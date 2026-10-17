# 배포 런북

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-RL-002 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 / 승인자 | 개발팀 / <mark>확인 필요</mark> |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 개발팀 | <mark>확인 필요</mark> |

이 문서는 통합플랫폼(`gis-sass`)을 Kubernetes 에 배포하는 절차다. 배포 단위는 Helm chart(`deploy/charts/gis`) 하나이고, 환경별 차이는 values 파일(`values-local.yaml`·`values-dev.yaml`·`values-prod.yaml`)로 흡수한다. **배포 실행 자동화(배포용 러너·배포 워크플로)는 아직 구성되지 않았으며, 아래 절차는 사람이 실행한다.** 현재 단계는 제주 지반침하 프로토타입 분석 및 통합플랫폼과의 결합 방식 검토 중이고, 결합 방식은 미결정이다. 따라서 이 런북은 현재 통합플랫폼 기준이다.

## 1. 배포 개요

- 대상 버전: 릴리스 태그가 아니라 `develop` 의 chart·이미지 기준이다(기준 커밋 4e37ab6, `v0.1.0` 이후 235 커밋). 현재 유일한 릴리스 `v0.1.0`(2026-09-17)은 이 절차의 대상이 아니다. 마이그레이션 Job 개선(T105, 2026-09-27 KST `develop` 병합)이 `v0.1.0` 뒤에 들어와서, `v0.1.0` chart 는 Job 이름이 고정이고 인자가 없어 이미지 기본값 `migrate --seed` 가 Job 이 만들어질 때마다(설치, 또는 Job 을 지우고 다시 배포할 때) 돌며(끌 `migrate.seed` 키 없음), 마이그레이션 이미지의 태그(또는 digest)를 바꾼 두 번째 `helm upgrade` 는 Job 불변 필드로 실패할 것으로 보이고, 스키마가 앞선 상태에서 롤백하면 `wait-for-migration` 이 '=' 로 비교해 api 파드가 `Init` 에서 멈출 것으로 보인다(불변 필드 실패와 `Init` 정지는 코드와 Kubernetes 규칙에서 도출한 것이며 클러스터에서 재현하지는 않았다). T105 를 포함한 릴리스 태그는 아직 없다. `develop` 의 `VERSION`·`Chart.yaml` 도 0.1.0 그대로라 버전 값으로는 구별되지 않으므로 커밋 SHA 로 식별한다. 기준 커밋 4e37ab6 의 CI 실행(2026-10-16)은 `docs` 잡이 실패해 build-push 가 건너뛰어졌으므로 이 커밋의 이미지는 게시되지 않았다. 실제 배포 대상은 §2 점검을 통과한 커밋을 따로 정하고 chart 와 이미지는 같은 커밋의 것을 쓴다.
- 이미지 식별: 커밋 SHA(40자) 태그로 식별한다. `vX.Y.Z` 는 `v*` 태그 푸시 때 build-push 가 태그가 가리키는 커밋(릴리스 규칙상 `main` 병합 커밋)을 새로 빌드하면서 SHA 태그와 함께 붙이는 별칭이며, `develop` 에서 올린 이미지에 덧붙는 태그가 아니다. `latest` 태그는 만들지 않는다. 환경 값에는 이미지의 OCI digest 를 고정하는 것이 기본이며 digest 가 태그보다 우선한다. 이미지는 6종(customer·admin 각각 api·web·migrate)이고 GHCR(`ghcr.io/innopam`)에 올라간다. `v0.1.0` 태그의 build-push(run 35182539015)는 잡 6개가 모두 시작되지 못해 실패했다. 이 태그의 이미지가 GHCR 에 있는지는 확인하지 못했다 <mark>확인 필요</mark>.
- 대상 환경: 3계층 사다리. 같은 이미지(digest)를 환경 사이에서 승격하는 것이 설계 원칙이다(ADR-2026-08-11.03). 현재는 이를 보장하는 절차가 없다 — 릴리스 이미지는 태그 커밋을 새로 빌드하므로 `develop` 이미지와 SHA·digest 가 다르고, 재태깅·digest 전달 절차와 배포 워크플로가 없으며(T089 todo), CI 가 만든 이미지가 배포된 환경도 없다(로컬 k3s 는 로컬에서 빌드해 import 한 이미지로 리허설했다). 운영에 어느 digest 를 쓸지는 정해야 한다 <mark>확인 필요</mark>.

  | 환경 | 용도·트리거 | 현재 상태 |
  | --- | --- | --- |
  | 로컬 k3s(k3d `gis-local`) | 매니페스트 리허설 | 첫 설치(install)만 배포·검증 — 2026-09-10 실배포, 2026-09-16 NetworkPolicy 수정 후 재설치·재검증(둘 다 T105 이전 chart 이고 이미지는 로컬에서 빌드해 import 한 것, 검증 뒤 네임스페이스·릴리스는 삭제). 현재 chart(T105 이후)의 클러스터 설치·이미지 태그를 바꾼 업그레이드·롤백·PSA `restricted` 는 실행 기록이 없다(lint·template·kubeconform 과 컨테이너 단위 시험만 했고 클러스터 실측은 T089 로 이관) <mark>확인 필요</mark> |
  | 사내 k8s 개발(`ops/dev0` 클러스터) | `develop` 승격 대상, 통합 검증·스테이징 겸용 | **배포 불가** — `values-dev.yaml` 의 이미지, Secret, DB 호스트, NetworkPolicy 대상이 비어 있다(대상 정보 대기). 또한 `values-dev.yaml` 의 `ingress.className` 은 `nginx`(NetworkPolicy 출발지 예시도 ingress-nginx 기준)인데 `ops/dev0` 의 IngressClass 는 `cilium`(2026-10-16)이라 맞춰야 한다. 통합플랫폼 배포 설정이 클러스터 저장소 `apps/` 에도 아직 없다 |
  | NCP 공공기관용 NKS(운영) | `vX.Y.Z` 태그 + 수동 승인 | **배포 불가** — Ingress 방식·DB 대역 등 대상 정보 대기(T077). 운영 타깃은 2026-10-14 NCP 공공기관용으로 결정(실측 5건이 승인 조건) |

- 배포 일시·담당: 로컬 k3s 실배포 기록만 있다(2026-09-10 앱 파드 6개 Ready·마이그레이션 Job 2개 Complete·로그인 왕복 200, 2026-09-16 NetworkPolicy 수정 후 재검증). 둘 다 첫 설치이고 T105 병합(2026-09-27 KST) 이전 chart 다. 사내 개발·운영 배포 이력은 없다. 담당은 개발팀(담당자명 <mark>확인 필요</mark>).

## 2. 사전 점검

- [ ] 릴리스 승인 체크리스트 완료 (JSA-PF-TS-011)
- [ ] 백업 완료 — 운영은 NCP Cloud DB 자동 백업을 기본 방침으로 하며 구성·주기는 미확정(T077·T076). 사내 개발 DB 는 위치 미정이고 CronJob 백업은 설계 방향일 뿐 chart 에 없다 <mark>확인 필요</mark>
- [ ] 롤백 계획 확인 (JSA-PF-RL-003)
- [ ] 대상 커밋의 CI(`test` 워크플로)가 모두 통과했고, `build-push` 로 이미지 6종이 GHCR 에 올라갔다(digest 는 build-push 잡 요약에 이미지마다 출력된다)
- [ ] 이미지 태그(또는 digest) 6종과 시크릿 4종(customer·admin DB 비밀번호, customer·admin JWT 서명키)을 준비했다. 평문 비밀값은 저장소에 두지 않는다
- [ ] 외부 소스 인증키 암호화 키(`MAP_SECRET_KEY`, base64 32바이트)의 주입 방법을 정했다 — chart 가 주입하지 않아 비워 두면 앱의 개발용 고정 기본값이 쓰일 수 있다(저장소 점검 결과, 클러스터 실측 아님) <mark>확인 필요</mark>
- [ ] 대상 환경 values 가 채워져 있다(`database.*.host`, `networkPolicy.ingressControllerFrom`·`databaseTo`, 이미지) — 이미지(tag·digest 둘 다 빔)와 NetworkPolicy 대상(dev·prod 는 `networkPolicy.enabled: true`)이 비면 렌더가 실패한다. `database.*.host` 는 렌더 가드가 없어 비어 있어도 `helm template`·`helm lint` 가 통과하고(`DB_HOST` 가 빈 값이 된다) DB 접속 단계에서 실패하는 것으로 추정된다(저장소 점검 결과, 클러스터 실측 아님). 렌더 통과로 갈음하지 말고 host 값을 직접 확인한다
- [ ] DB 가 TLS 를 받는지 확인했다(`sslMode` 기본 `require` 라 TLS 를 받지 않는 DB 에는 연결에 실패해 API 파드가 Ready 가 되지 않는다. chart 는 `sslMode` 한 값에서 `DB_REQUIRE_TLS` 도 함께 파생하므로 `sslMode` 를 `prefer`·`allow`·`disable` 로 낮추면 부팅 검증도 꺼져 기동 거부 없이 그 값으로 붙는다. `prefer`·`allow` 는 암호화를 보장하지 않아 DB 설정에 따라 조용히 평문이 될 수 있고, 낮춘 값을 막는 chart 가드·CI 검사는 없다)
- [ ] `helm lint`·`helm template` 이 통과한다(`scripts/ci/check-chart.sh` 가 5개 조합으로 helm lint·template·kubeconform 을 검증한다). 이 스크립트의 dev·prod 조합은 NetworkPolicy 를 끄고 DB host 에 자리값을 넣어 돌리므로, CI 통과가 실제 대상 values 의 host·NetworkPolicy 대상이 채워졌다는 뜻은 아니다
- [ ] 시드(`migrate.seed`)가 꺼져 있다(로컬만 `true`). 꺼져 있으면 로그인할 계정이 없어서 4절의 로그인 왕복·smoke 3종은 사내 개발·운영에서 현재 절차로는 할 수 없다(시드를 끈 DB 에서 첫 관리자 계정을 만드는 절차가 없다, T105 남은 일) <mark>확인 필요</mark>
- [ ] 클러스터가 GHCR 이미지를 pull 할 수 있다(패키지 공개 여부 또는 pull Secret) <mark>확인 필요</mark>

## 3. 배포 절차

예상 시간 칸에는 실측 기록이 있으면 측정 조건과 함께 실측값을 적고, 실측이 없으면 설정된 제한 시간을 '한도'로 적는다. 둘 다 없으면 "—"로 둔다. 실측은 로컬 k3d 의 마이그레이션 Job 소요뿐이며 사내·운영 배포 실측은 없다.

| 순서 | 작업 | 명령·방법 | 담당 | 예상 시간 |
| --- | --- | --- | --- | --- |
| 1 | 대상 클러스터 컨텍스트 확인, 이미지 pull 자격 확인 | `kubectl config current-context`. GHCR 패키지가 비공개이면 클러스터에 pull Secret(imagePullSecrets)이 있어야 하는데 chart 에는 해당 값이 없고, 로컬 k3s 는 직접 빌드해 import 한 이미지로 검증해 GHCR pull 은 거치지 않았다. 패키지 공개 여부와 pull 자격 주입 방법은 <mark>확인 필요</mark> | 개발팀 | — |
| 2 | 차트 검증 | `helm lint charts/gis -f charts/gis/values-<환경>.yaml`, `helm template gis charts/gis -f …` | 개발팀 | — |
| 3 | 설치·업그레이드 (설치와 업그레이드 명령이 같다) | 로컬: `helm upgrade --install gis charts/gis -f charts/gis/values-local.yaml --set customerApi.image.digest=sha256:… (6종) --set-string secret.customerDbPassword=… (4종) --wait --timeout 10m`. 개발·운영: 같은 명령에서 `--set-string secret.*` 를 빼고, 외부에서 만든 Secret 의 이름을 values 로 지정한다(`database.<제품>.existingSecret`, `auth.<제품>.jwtSecretName`). SealedSecret 매니페스트는 `helm upgrade` 전에 apply 한다. 이 경로는 ADR-2026-09-26.01(승인 2026-10-14)로 정해졌으나 도입(T093)이 끝나지 않아 controller 설치·봉인·배포를 해 본 적이 없다(미검증) | 개발팀 | 실측 없음. 한도 10분(`--timeout`, 4단계 Job 대기 포함) |
| 4 | 마이그레이션 Job 확인 | `kubectl get jobs -l app.kubernetes.io/component=migration` — 새 리비전 Job 이 `Complete`. 실패 시 `kubectl logs job/<Job 이름>` | 개발팀 | 실측 각 5초(로컬 k3d, 빈 DB 첫 설치, T087 기록 — 참고값). 한도 600초(`migrate.activeDeadlineSeconds`). 3단계 `--wait` 안에서 진행 |
| 5 | 기동 확인 | `kubectl get pods,jobs,ingress` — 새 마이그레이션이 있는 배포에서는 api 파드가 `wait-for-migration` 을 통과할 때까지(적용 건수가 이미지의 마이그레이션 수 이상이 될 때까지) `Init` 에 머물다 `Running` 으로 넘어간다 | 개발팀 | 실측 없음. 3단계 `--wait` 한도(10분) 안에서 진행. 파드 단위 한도: api `wait-for-migration` 5분(`migrateWait`, 5초×60회), api startupProbe 300초(10초×30회), web startupProbe 50초(5초×10회) |
| 6 | 상태 확인(관리 포트) | `kubectl port-forward deploy/gis-gis-customer-api 8081:8081` 후 `curl -fsS http://localhost:8081/actuator/health` (admin 은 `gis-gis-admin-api`) | 개발팀 | — |
| 7 | smoke 3종(시드를 켠 로컬 k3s 한정) | `API_BASE=<대상>/api scripts/smoke-auth.sh`, `smoke-org-workspace.sh`, `smoke-map.sh` — 세 스크립트는 시더가 만드는 개발용 계정과 데이터(기본 조직·워크스페이스·배경지도)에 고정돼 있어 `migrate.seed=true` 인 로컬 k3s 에서만 통과한다. 시드를 끈 사내 개발·운영의 대체 검증은 <mark>확인 필요</mark> | 개발팀 | — |

운영 시 알아 둘 점(첫 두 항목은 chart 설계상 동작이고 이미지 태그를 바꾼 업그레이드와 롤백을 클러스터에서 실행한 기록은 없다 — T089. 세 번째·네 번째는 로컬 k3d 실측 기록에 근거한다). 첫 두 항목은 `develop` 의 chart 기준이다. `v0.1.0` 에 없는 동작은 Job 이름의 리비전 접미사, `migrate --force` 고정과 `migrate.seed` 기본 꺼짐(`values-local.yaml` 만 `true`. `v0.1.0` 은 인자 없이 실행해 이미지 기본값 `migrate --seed` 가 항상 돈다), `wait-for-migration` 의 '적용 수 ≥ 기대 수' 판정(롤백한 파드가 통과)이다. 새 마이그레이션이 있을 때 api 파드가 `Init` 에서 대기하는 것, `maxUnavailable: 0`, `backoffLimit: 0` 은 `v0.1.0` 에도 있다(위에서 든 차이와 그 영향은 1절. chart 의 그 밖의 차이 — 마이그레이션 Job 의 제한 시간·TTL·자원, 파드 보안 컨텍스트(PSA `restricted`), api 의 포트·`trustedProxies` 환경변수 주입 — 는 gis-sass 저장소의 `git diff v0.1.0 4e37ab6 -- deploy/` 로 본다):

- 업그레이드 때 마이그레이션 Job 이름에 리비전이 붙어(`<릴리스>-gis-migrate-<제품>-r<리비전>`) 매번 새로 만들어진다. 새 api 파드는 `wait-for-migration` 이 이미지의 마이그레이션 수 이상이 적용될 때까지 대기하고 Job 상태는 보지 않으므로, 새 마이그레이션이 있는 배포에서는 그 마이그레이션이 모두 적용될 때까지 기다리고(새 마이그레이션이 없는 배포나 롤백에서는 Job 이 끝나기 전에도 통과한다), 그동안 이전 파드가 트래픽을 받는다(`maxUnavailable: 0`). 그래서 마이그레이션은 이전 코드와 호환되게(컬럼 추가 → 코드 배포 → 옛 컬럼 제거 순) 쓴다.
- 마이그레이션 Job 은 기본값(`migrate.seed: false`)에서 `migrate --force` 만 실행해 시드가 돌지 않는다. 개발·운영 values 는 이 값을 바꾸지 않으며 켜지도 않는다(알려진 비밀번호의 개발용 계정이 만들어지기 때문이다). `values-local.yaml` 만 `migrate.seed: true` 라 로컬 k3s 의 Job 은 `migrate --force --seed` 로 돌고, 로그인 왕복과 smoke 가 쓰는 개발용 계정이 이때 만들어진다. 실패(`backoffLimit: 0`)하면 새 api 파드는 `Init` 에서 멈추고 `--wait` 가 시간 초과로 실패하지만 이전 파드는 계속 서비스한다. 고친 이미지로 다시 업그레이드하거나 롤백한다(JSA-PF-RL-003).
- 로컬 k3s 는 `values-local.yaml` 이 NetworkPolicy 를 켠다. DB 를 다른 네임스페이스·라벨로 띄웠다면 `database.*.host` 와 `networkPolicy.databaseTo` 를 함께 바꾼다. 맞지 않으면 마이그레이션 Job 이 실패하고 api 파드가 `Init:0/1` 에서 멈춘다.
- 로컬 k3s 의 첫 배포 기준 앱 파드는 6개(customer-api 2 · admin-api 2 · customer-web 1 · admin-web 1)다.

## 4. 배포 후 검증

로그인 왕복·smoke 3종·제품 간 격리(토큰 교차) 검증은 시더가 만드는 개발용 계정과 데이터(기본 조직·배경지도 레이어)를 전제로 하므로 `migrate.seed=true` 인 로컬 k3s 에서만 수행한다. 시드를 끄는 사내 개발·운영에는 로그인할 계정을 만드는 절차가 저장소에 없어(T105 남은 일) 지금은 이 검증을 수행할 수 없다. 계정 발급 절차와 대체 검증은 <mark>확인 필요</mark>. 계정 없이 확인되는 항목은 파드·Job 상태, 관리 포트 헬스, 관리 포트 비노출, NetworkPolicy 다.

| 항목 | 확인 방법 | 기대 결과 |
| --- | --- | --- |
| 파드·Job 상태 | `kubectl get pods,jobs,ingress` | 앱 파드가 모두 Ready, 마이그레이션 Job 2개 `Complete` |
| 헬스 | 관리 포트 8081 `/actuator/health` (customer·admin 각각) | HTTP 200, 본문의 `status` 가 `UP`. 실측 본문 예: `{"groups":["liveness","readiness"],"status":"UP"}`(2026-09-10 로컬 k3s, customer·admin 동일). 필드 순서·추가 필드는 달라질 수 있으므로 문자열 전체 일치가 아니라 `"status":"UP"` 포함 여부로 판정한다 |
| 관리 포트 비노출 | `curl -s -o /dev/null -w '%{http_code}' http://<ingress-host>/api/actuator/health` | 404. 참고로 `/actuator/health` 는 SPA 폴백이 200 으로 `index.html` 을 주므로 상태 코드가 아니라 **본문**으로 판정한다 |
| 로그인 왕복 | (시드를 켠 로컬 k3s) Ingress 경유 시드 계정 로그인 → `/api/auth/me`. 사내 개발·운영은 계정 발급 절차가 없어 현재 절차로는 할 수 없다 <mark>확인 필요</mark> | HTTP 200 |
| 인증 smoke | (시드를 켠 로컬 k3s) `scripts/smoke-auth.sh` | 38 PASS·0 FAIL — compose 스택에서 실측한 기준 수치다(2026-08-18 연속 2회 동일, 2026-09-27 develop b1b07e0 에서 1회 재확인). 클러스터를 대상으로 돌린 기록은 찾지 못했다 |
| 조직·워크스페이스·지도 smoke | (시드를 켠 로컬 k3s) `scripts/smoke-org-workspace.sh`, `scripts/smoke-map.sh` | smoke-map 42 PASS(compose 스택에서 실측한 기준 수치, 클러스터 실행 기록 없음). 3번 시나리오는 외부 타일 서버(OpenStreetMap)를 호출하므로 외부 네트워크가 필요하고, 소스 등록을 확인하는 시나리오는 호스트 이름을 IP 로 해석하므로 DNS 도 필요하다 |
| 제품 간 격리 | (시드를 켠 로컬 k3s) customer 토큰으로 admin API 호출, 반대 방향도 호출 | 양방향 401 |
| NetworkPolicy | admin-api 파드에서 customer-api 8080 호출 | 차단(허용 규칙 없음) |
| 무중단(선택) | 롤링 업데이트 중 반복 요청 | 실패 0건(로컬 k3s, `kubectl rollout restart` 중 2026-08-26 기록: 40/40. 이후 chart 변경 뒤 요청 실패를 센 재수행 기록은 없다) |

## 5. 연락 체계

| 역할 | 이름 | 연락처 |
| --- | --- | --- |
| 배포 담당 | <mark>확인 필요</mark> | <mark>확인 필요</mark> |
| 롤백 결정자 | <mark>확인 필요</mark> | <mark>확인 필요</mark> |
| 인프라(사내 클러스터) 담당 | <mark>확인 필요</mark> | <mark>확인 필요</mark> |

운영 체계(책임자·직무 분리·연락 체계)는 CSAP 인증 신청 과업(M011, WBS ID 34 서비스 보안 운영체계 구성)에서 확정한다. 개인 연락처는 이 문서에 적지 않는다.

## 6. 근거 자료

- `deploy/README.md` §3~§8, `deploy/charts/gis/`, `scripts/ci/check-chart.sh` (gis-sass 저장소)
- 설계서 장 3 배포 토폴로지 §3.1.1·§3.1.4·§3.1.5, `docs/TESTING.md`
- `docs/01.개발/ADRs/deployment/`(3환경 사다리, 배포 실행 구조, CSAP 범위·운영 타깃)
- `ops/dev0/apps/`(통합플랫폼 배포 설정 없음 확인, 2026-10-16)
