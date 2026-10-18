# 롤백 계획

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-RL-003 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 / 승인자 | 개발팀 / <mark>확인 필요</mark> |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 개발팀 | <mark>확인 필요</mark> |

이 문서는 통합플랫폼(`gis-sass`) Helm 배포를 되돌리는 계획이다. 배포 절차는 JSA-PF-RL-002 를 따른다. 롤백을 실제로 수행한 기록은 저장소에서 찾지 못했다(실배포는 로컬 k3s 만 있고, 무중단 배포 검증에서는 파드 삭제·롤링 업데이트·DB 일시 중단을 시험했다).

## 1. 롤백 판단 기준

저장소에 롤백 기준으로 명시된 것은 1번(마이그레이션 Job 실패, `deploy/README.md` §3.4)뿐이다. 2~5번은 배포 후 검증(`deploy/README.md` §6)의 기대 결과를 롤백 판단에 적용한 개발팀 제안이다 <mark>확인 필요</mark>. **오류율·지연 시간 같은 수치 임계치는 정해져 있지 않다**(운영 개시 전 정의 필요, <mark>확인 필요</mark>).

- 마이그레이션 Job 이 `Failed` 이다(`backoffLimit: 0`, 제한 시간 600초). 이 경우 새 api 파드는 `Init` 에서 멈추고 **이전 파드가 계속 서비스한다.** 즉시 롤백이 필요하지 않을 수 있으며, 원인을 `kubectl logs job/<Job 이름>` 으로 확인해 고친 이미지로 다시 배포하거나 롤백한다.
- `helm upgrade --wait --timeout 10m` 이 시간 초과로 실패한다(새 파드가 Ready 에 이르지 못함).
- 헬스 확인이 실패한다 — 관리 포트(8081) `/actuator/health` 가 `UP` 이 아니거나 readiness 가 계속 false 다.
- 배포 후 검증이 실패한다 — 시드를 켠 환경(로컬 k3s)에서만 판정한다: 로그인 왕복(HTTP 200) 실패, smoke 기준 PASS 수 미달(인증 38, 지도 42), 제품 간 토큰 교차 요청이 401 이 아님. 시드를 끈 사내 개발·운영은 로그인할 계정이 없어 이 판정을 쓸 수 없고(시드를 끈 DB 에서 첫 관리자 계정을 만드는 절차가 없다, T105 남은 일) 대체 기준은 정해지지 않았다 <mark>확인 필요</mark>.
- 핵심 기능 장애 — 로그인·워크스페이스 접근·지도 소스·타일 프록시가 동작하지 않는다.

## 2. 사전 준비

- 이전 버전 위치: GHCR `ghcr.io/innopam/gis-<customer|admin>-<api|web|migrate>` 의 이전 배포 커밋 SHA 태그 또는 OCI digest(build-push 잡 요약에 이미지마다 기록), 그리고 Helm 리비전 이력(`helm history gis`). 배포할 때 이전 digest 와 리비전 번호를 기록해 둔다.
- 데이터베이스 백업 위치·시점: 운영은 NCP Cloud DB 자동 백업을 기본 방침으로 한다(구성·주기 미확정, T077·T076). 사내 개발 DB 는 위치가 정해지지 않았고, `pg_dump` CronJob 은 설계 방향일 뿐 chart 에 없다. 따라서 **배포 직전 백업 시점과 위치는 <mark>확인 필요</mark>**다.
- 롤백 결정자: <mark>확인 필요</mark>(운영 담당 주체는 CSAP 보안 운영체계 구성에서 확정 예정).

## 3. 롤백 절차

| 순서 | 작업 | 명령·방법 | 담당 | 예상 시간 |
| --- | --- | --- | --- | --- |
| 1 | 상황 판단 — 롤백할지, 수정 이미지로 다시 배포할지 결정 | `kubectl get pods,jobs`, `kubectl logs job/<Job 이름>` | 롤백 결정자 | — |
| 2 | 되돌릴 리비전 확인 | `helm history gis` | 개발팀 | — |
| 3 | 롤백 실행 | `helm rollback gis <리비전> --wait --timeout 10m` | 개발팀 | 실측 없음. 한도 10분(`--timeout`) |
| 4 | 마이그레이션 Job 확인 | 롤백도 새 리비전이라 이전 이미지로 Job 이 한 번 더 돈다. Laravel 은 되돌리지 않으므로 `Nothing to migrate` 로 끝난다 | 개발팀 | 실측 없음. 한도 600초(`migrate.activeDeadlineSeconds`, T105 이후 chart 기준) |
| 5 | 롤백 후 검증 | 아래 5절 | 개발팀 | — |
| 6 | 스키마 되돌림 판단(필요할 때만) | `migrate:rollback` 은 chart 가 자동으로 하지 않는다. 사람이 데이터 영향을 판단해 따로 실행한다(승인 절차는 <mark>확인 필요</mark>) | 롤백 결정자 | — |

- 롤백한 이전 이미지의 `wait-for-migration` 은 "적용된 마이그레이션 수 ≥ 이미지의 마이그레이션 수"로 판정하므로, 스키마가 앞선 상태 그대로여도 `wait-for-migration` 은 통과한다(앱 컨테이너가 그 스키마에서 뜨는지는 별개다).
- 새 스키마 위에서 옛 코드가 도는 구간이 생기므로, 마이그레이션은 이전 코드와 호환되게(컬럼 추가 → 코드 배포 → 옛 컬럼 제거 순) 작성하는 것이 `deploy/README.md` §3.4 의 방침이다. 이 방침은 CI 가 강제하지 않는다(4절).

## 4. 데이터 복구

- **스키마**: 롤백은 스키마를 되돌리지 않는다. 마이그레이션을 이전 코드와 호환되게 쓰는 것은 `deploy/README.md` §3.4 에 적힌 방침일 뿐 CI·리뷰 규칙으로 강제되지 않는다(`migrate-roundtrip` 은 빈 DB 에서 마이그레이션 왕복만 확인한다). 실제로 `v0.1.0` 에 들어 있는 `2026_09_16_000205`(customer)는 `layers.wms_layer_name` 을 `options` 로 옮긴 같은 마이그레이션에서 그 컬럼을 삭제한다(커밋 `5cb9609`, 2026-09-16). 이 커밋 이전의 이미지는 그 컬럼을 매핑하고 `ddl-auto: validate` 로 기동하므로, 스키마를 그대로 둔 채 그 이미지로 롤백하면 customer-api 가 기동에 실패할 것으로 본다(코드 점검 결과이며, 이전 이미지가 이 스키마에서 스키마 검증으로 죽은 사례가 T087 기록에 있다) <mark>확인 필요</mark>. 그런 대상으로 되돌려야 할 때처럼 꼭 필요할 때만 `migrate:rollback` 을 사람이 실행한다. 마이그레이션 `down()` 은 PostGIS 확장을 지우지 않는다(`DROP EXTENSION` 미수행).
- **데이터**: 운영은 관리형 DB 의 자동 백업에서 복원한다. 복원 절차·리허설 주기·담당 주체는 아직 정해지지 않았다(T076 의 `deploy/README.md` 작성 범위, 담당 확정 전에는 운영 배포를 완료 판정하지 않는다).
- **JWT 서명키 교체가 원인인 경우**: 앱은 `kid` 기반 무중단 회전(신 키 배포 → access 토큰 TTL 대기 → 구 키 폐기, `deploy/README.md` §5.3)을 지원하지만, chart 는 `AUTH_JWT_SIGNING_KEY`(admin 은 `ADMIN_AUTH_JWT_SIGNING_KEY`) 한 값만 주입하고 `*_JWT_SIGNING_KEY_ID`·`*_JWT_PREVIOUS_SIGNING_KEYS` 를 넣을 경로가 없어(T088 todo) chart 로는 3단계 회전을 할 수 없다. 지금 가능한 것은 활성 키 교체뿐이며, 교체하면 기존 access 토큰이 모두 무효가 된다(README 가 유출 대응 '긴급 회전'으로 설명하는 동작과 같다). README 는 이를 전체 사용자 재로그인이라 적었으나 refresh 토큰 처리까지 포함해 실제로 다시 로그인해야 하는지는 <mark>확인 필요</mark>다. 키 값만 바꾼 배포가 api 파드를 재시작하는지도 <mark>확인 필요</mark>다(Deployment 템플릿에 checksum 어노테이션이 없다).

## 5. 롤백 후 검증

| 항목 | 확인 방법 | 기대 결과 |
| --- | --- | --- |
| 이미지 버전 | 실행 중 이미지는 `kubectl get deploy -o wide` 의 IMAGES 열로 본다(마이그레이션 Job 은 `kubectl get jobs -o wide`). 배포 때 기록해 둔 이전 digest 와 대조한다 | 두 값이 같다(되돌린 리비전의 digest) |
| 리비전 이력 | `helm history gis` — REVISION·UPDATED(갱신 시각)·STATUS·CHART·APP VERSION·DESCRIPTION 열이 나오고 이미지는 나오지 않는다(CHART·APP VERSION 은 릴리스 때만 사람이 올리는 값이라 이미지 태그·digest 만 바꾼 리비전끼리는 같다. 현재 `develop` 은 `gis-0.1.0`·`0.1.0`) | 가장 최근 리비전이 STATUS `deployed`, DESCRIPTION 이 롤백 대상 리비전을 가리킨다 |
| 파드·Job 상태 | `kubectl get pods,jobs` | 앱 파드 모두 Ready, 롤백 리비전의 Job `Complete` |
| 헬스 | 관리 포트 8081 `/actuator/health` | HTTP 200, `status` 가 `UP`(본문 예: `{"groups":["liveness","readiness"],"status":"UP"}`) |
| 로그인·핵심 기능 | (시드를 켠 로컬 k3s) 로그인 왕복, `scripts/smoke-auth.sh`, `smoke-map.sh`. 시드를 끈 사내 개발·운영의 대체 검증은 <mark>확인 필요</mark> | HTTP 200, 기준 PASS 수(compose 스택에서 실측한 수치이고 클러스터 실행 기록은 없다) |
| 데이터 정합 | 롤백 전후 워크스페이스·소스·레이어 조회 | 이전과 동일(스키마를 되돌렸다면 해당 변경분 확인) |

## 6. 커뮤니케이션

고객·내부에 알리는 시점과 방법은 정해져 있지 않다. 현재는 사내 개발 단계라 별도 통지 체계가 없으며, 운영 체계(책임자·사고 대응·연락 체계)는 CSAP 인증 신청 과업(WBS ID 34)에서 정한다 — <mark>확인 필요</mark>.

## 7. 근거 자료

- `deploy/README.md` §3.4(업그레이드와 롤백)·§5.3(JWT 키 회전)·§7(무중단 배포 검증)·§8(미결 항목) (gis-sass 저장소)
- 설계서 장 3 §3.1.4(마이그레이션과 부트스트랩)·§3.1.5(백업)
- `scripts/ci/migrate-roundtrip.sh`(마이그레이션 왕복 검증)
