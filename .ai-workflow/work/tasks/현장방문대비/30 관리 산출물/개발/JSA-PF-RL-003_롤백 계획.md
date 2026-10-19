# 롤백 계획

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-RL-003 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 | 박가람 |
| 승인자 | - |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 박가람 | - |

이 문서는 통합플랫폼(`gis-sass`) Helm 배포를 되돌리는 계획이다. 배포 절차는 JSA-PF-RL-002 를 따른다.

## 1. 롤백 판단 기준

첫 항목은 `deploy/README.md` §3.4 의 기준이고, 나머지는 배포 후 검증(`deploy/README.md` §6)의 기대 결과를 롤백 판단에 적용한 것이다.

- 마이그레이션 Job 이 `Failed` 이다(`backoffLimit: 0`, 제한 시간 600초). 이 경우 새 api 파드는 `Init` 에서 멈추고 **이전 파드가 계속 서비스한다.** 즉시 롤백이 필요하지 않을 수 있으며, 원인을 `kubectl logs job/<Job 이름>` 으로 확인해 고친 이미지로 다시 배포하거나 롤백한다.
- `helm upgrade --wait --timeout 10m` 이 시간 초과로 실패한다(새 파드가 Ready 에 이르지 못함).
- 헬스 확인이 실패한다 — 관리 포트(8081) `/actuator/health` 가 `UP` 이 아니거나 readiness 가 계속 false 다.
- 배포 후 검증이 실패한다 — 로그인 왕복(HTTP 200) 실패, smoke 기준 PASS 수 미달(인증 38, 지도 42), 제품 간 토큰 교차 요청이 401 이 아님.
- 핵심 기능 장애 — 로그인·워크스페이스 접근·지도 소스·타일 프록시가 동작하지 않는다.

## 2. 사전 준비

- 이전 버전 위치: GHCR `ghcr.io/innopam/gis-<customer|admin>-<api|web|migrate>` 의 이전 배포 커밋 SHA 태그 또는 OCI digest(build-push 잡 요약에 이미지마다 기록), 그리고 Helm 리비전 이력(`helm history gis`). 배포할 때 이전 digest 와 리비전 번호를 기록해 둔다.
- 데이터베이스 백업 위치·시점: 운영은 NCP Cloud DB 자동 백업을 기본 방침으로 한다.
- 롤백 결정자: -

## 3. 롤백 절차

| 순서 | 작업 | 명령·방법 | 담당 | 예상 시간 |
| --- | --- | --- | --- | --- |
| 1 | 상황 판단 — 롤백할지, 수정 이미지로 다시 배포할지 결정 | `kubectl get pods,jobs`, `kubectl logs job/<Job 이름>` | 롤백 결정자 | — |
| 2 | 되돌릴 리비전 확인 | `helm history gis` | 개발팀 | — |
| 3 | 롤백 실행 | `helm rollback gis <리비전> --wait --timeout 10m` | 개발팀 | 한도 10분(`--timeout`) |
| 4 | 마이그레이션 Job 확인 | 롤백도 새 리비전이라 이전 이미지로 Job 이 한 번 더 돈다. Laravel 은 되돌리지 않으므로 `Nothing to migrate` 로 끝난다 | 개발팀 | 한도 600초(`migrate.activeDeadlineSeconds`) |
| 5 | 롤백 후 검증 | 아래 5절 | 개발팀 | — |
| 6 | 스키마 되돌림 판단(필요할 때만) | `migrate:rollback` 은 chart 가 자동으로 하지 않는다. 사람이 데이터 영향을 판단해 따로 실행한다 | 롤백 결정자 | — |

- 롤백한 이전 이미지의 `wait-for-migration` 은 "적용된 마이그레이션 수 ≥ 이미지의 마이그레이션 수"로 판정하므로, 스키마가 앞선 상태 그대로여도 `wait-for-migration` 은 통과한다(앱 컨테이너가 그 스키마에서 뜨는지는 별개다).
- 새 스키마 위에서 옛 코드가 도는 구간이 생기므로, 마이그레이션은 이전 코드와 호환되게(컬럼 추가 → 코드 배포 → 옛 컬럼 제거 순) 작성하는 것이 `deploy/README.md` §3.4 의 방침이다.

## 4. 데이터 복구

- **스키마**: 롤백은 스키마를 되돌리지 않는다. 마이그레이션은 이전 코드와 호환되게 쓰는 것이 `deploy/README.md` §3.4 의 방침이며(`migrate-roundtrip` 이 빈 DB 에서 마이그레이션 왕복을 확인한다), 이전 코드와 호환되지 않는 스키마 변경 이전으로 되돌려야 할 때처럼 꼭 필요할 때만 `migrate:rollback` 을 사람이 실행한다. 마이그레이션 `down()` 은 PostGIS 확장을 지우지 않는다(`DROP EXTENSION` 미수행).
- **데이터**: 운영은 관리형 DB 의 자동 백업에서 복원한다.
- **JWT 서명키 교체가 원인인 경우**: chart 는 활성 서명키 `AUTH_JWT_SIGNING_KEY`(admin 은 `ADMIN_AUTH_JWT_SIGNING_KEY`)를 주입한다. 활성 키를 교체하면 기존 access 토큰이 모두 무효가 된다(`deploy/README.md` §5.3 이 유출 대응 '긴급 회전'으로 설명하는 동작과 같다).

## 5. 롤백 후 검증

| 항목 | 확인 방법 | 기대 결과 |
| --- | --- | --- |
| 이미지 버전 | 실행 중 이미지는 `kubectl get deploy -o wide` 의 IMAGES 열로 본다(마이그레이션 Job 은 `kubectl get jobs -o wide`). 배포 때 기록해 둔 이전 digest 와 대조한다 | 두 값이 같다(되돌린 리비전의 digest) |
| 리비전 이력 | `helm history gis` — REVISION·UPDATED(갱신 시각)·STATUS·CHART·APP VERSION·DESCRIPTION 열이 나오고 이미지는 나오지 않는다 | 가장 최근 리비전이 STATUS `deployed`, DESCRIPTION 이 롤백 대상 리비전을 가리킨다 |
| 파드·Job 상태 | `kubectl get pods,jobs` | 앱 파드 모두 Ready, 롤백 리비전의 Job `Complete` |
| 헬스 | 관리 포트 8081 `/actuator/health` | HTTP 200, `status` 가 `UP`(본문 예: `{"groups":["liveness","readiness"],"status":"UP"}`) |
| 로그인·핵심 기능 | 로그인 왕복, `scripts/smoke-auth.sh`, `smoke-map.sh` | HTTP 200, 기준 PASS 수(인증 38, 지도 42) |
| 데이터 정합 | 롤백 전후 워크스페이스·소스·레이어 조회 | 이전과 동일(스키마를 되돌렸다면 해당 변경분 확인) |

로그인 왕복과 smoke 는 검증용 계정이 있는 환경에서 수행한다.

## 6. 커뮤니케이션

운영 체계(책임자·사고 대응·연락 체계)는 CSAP 인증 신청 과업(WBS ID 34)에서 정한다.

## 7. 근거 자료

- `deploy/README.md` §3.4(업그레이드와 롤백)·§5.3(JWT 키 회전)·§7(무중단 배포 검증) (gis-sass 저장소)
- 설계서 장 3 §3.1.4(마이그레이션과 부트스트랩)·§3.1.5(백업)
- `scripts/ci/migrate-roundtrip.sh`(마이그레이션 왕복 검증)
