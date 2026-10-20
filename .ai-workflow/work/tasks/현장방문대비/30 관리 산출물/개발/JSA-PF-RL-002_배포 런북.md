# 배포 런북

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-RL-002 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 | 박가람 |
| 승인자 | 박가람 |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 박가람 | 박가람 |

이 문서는 통합플랫폼(`gis-sass`)을 Kubernetes 에 배포하는 절차다. 배포 단위는 Helm chart(`deploy/charts/gis`) 하나이고, 환경별 차이는 values 파일(`values-local.yaml`·`values-dev.yaml`·`values-prod.yaml`)로 흡수한다. 아래 절차는 사람이 실행한다.

## 1. 배포 개요

- 대상 버전: `develop` 의 chart·이미지 기준이다. 배포 대상은 2절 점검을 통과한 커밋으로 정하고, chart 와 이미지는 같은 커밋의 것을 쓰며 커밋 SHA 로 식별한다.
- 이미지 식별: 커밋 SHA(40자) 태그로 식별한다. `vX.Y.Z` 는 `v*` 태그 푸시 때 build-push 가 태그가 가리키는 커밋(릴리스 규칙상 `main` 병합 커밋)을 빌드하면서 SHA 태그와 함께 붙이는 별칭이다. `latest` 태그는 만들지 않는다. 환경 값에는 이미지의 OCI digest 를 고정하는 것이 기본이며 digest 가 태그보다 우선한다. 이미지는 6종(customer·admin 각각 api·web·migrate)이고 GHCR(`ghcr.io/innopam`)에 올라간다.
- 대상 환경: 3계층 사다리. 같은 이미지(digest)를 환경 사이에서 승격하는 것이 설계 원칙이다(ADR-2026-08-11.03).

  | 환경 | 용도·트리거 |
  | --- | --- |
  | 로컬 k3s(k3d `gis-local`) | 매니페스트 리허설 |
  | 사내 k8s 개발(`ops/dev0` 클러스터) | `develop` 승격 대상, 통합 검증·스테이징 겸용 |
  | NCP 공공기관용 NKS(운영) | `vX.Y.Z` 태그 + 수동 승인 |

- 배포 일시·담당: 로컬 k3s 배포 2026-09-10(앱 파드 6개 Ready·마이그레이션 Job 2개 Complete·로그인 왕복 200), 2026-09-16 NetworkPolicy 수정 후 재검증. 담당은 박가람.

## 2. 사전 점검

- [ ] 릴리스 승인 체크리스트 완료 (JSA-PF-TS-011)
- [ ] 백업 완료 — 운영은 NCP Cloud DB 자동 백업을 기본 방침으로 한다
- [ ] 롤백 계획 확인 (JSA-PF-RL-003)
- [ ] 대상 커밋의 CI(`test` 워크플로)가 모두 통과했고, `build-push` 로 이미지 6종이 GHCR 에 올라갔다(digest 는 build-push 잡 요약에 이미지마다 출력된다)
- [ ] 이미지 태그(또는 digest) 6종과 시크릿 4종(customer·admin DB 비밀번호, customer·admin JWT 서명키)을 준비했다. 평문 비밀값은 저장소에 두지 않는다
- [ ] 외부 소스 인증키 암호화 키(`MAP_SECRET_KEY`, base64 32바이트)의 주입 방법을 정했다
- [ ] 대상 환경 values 가 채워져 있다(`database.*.host`, `networkPolicy.ingressControllerFrom`·`databaseTo`, 이미지) — 이미지(tag·digest 둘 다 빔)와 NetworkPolicy 대상(dev·prod 는 `networkPolicy.enabled: true`)이 비면 렌더가 실패한다. `database.*.host` 는 렌더 통과와 별개로 값을 직접 확인한다
- [ ] DB 가 TLS 를 받는지 확인했다(`sslMode` 기본 `require` 라 TLS 를 받지 않는 DB 에는 연결에 실패해 API 파드가 Ready 가 되지 않는다)
- [ ] `helm lint`·`helm template` 이 통과한다(`scripts/ci/check-chart.sh` 가 5개 조합으로 helm lint·template·kubeconform 을 검증한다)
- [ ] 시드(`migrate.seed`)가 꺼져 있다(로컬만 `true`)
- [ ] 클러스터가 GHCR 이미지를 pull 할 수 있다(패키지 공개 여부 또는 pull Secret)

## 3. 배포 절차

예상 시간 칸에는 실측값이 있으면 측정 조건과 함께 적고, 없으면 설정된 제한 시간을 '한도'로 적는다. 둘 다 없으면 "—"로 둔다.

| 순서 | 작업 | 명령·방법 | 담당 | 예상 시간 |
| --- | --- | --- | --- | --- |
| 1 | 대상 클러스터 컨텍스트 확인, 이미지 pull 자격 확인 | `kubectl config current-context`. GHCR 패키지가 비공개이면 클러스터에 pull Secret(imagePullSecrets)이 있어야 한다 | 개발팀 | — |
| 2 | 차트 검증 | `helm lint charts/gis -f charts/gis/values-<환경>.yaml`, `helm template gis charts/gis -f …` | 개발팀 | — |
| 3 | 설치·업그레이드 (설치와 업그레이드 명령이 같다) | 로컬: `helm upgrade --install gis charts/gis -f charts/gis/values-local.yaml --set customerApi.image.digest=sha256:… (6종) --set-string secret.customerDbPassword=… (4종) --wait --timeout 10m`. 개발·운영: 같은 명령에서 `--set-string secret.*` 를 빼고, 외부에서 만든 Secret 의 이름을 values 로 지정한다(`database.<제품>.existingSecret`, `auth.<제품>.jwtSecretName`). SealedSecret 매니페스트는 `helm upgrade` 전에 apply 한다(ADR-2026-09-26.01) | 개발팀 | 한도 10분(`--timeout`, 4단계 Job 대기 포함) |
| 4 | 마이그레이션 Job 확인 | `kubectl get jobs -l app.kubernetes.io/component=migration` — 새 리비전 Job 이 `Complete`. 실패 시 `kubectl logs job/<Job 이름>` | 개발팀 | 실측 각 5초(로컬 k3d, 빈 DB 첫 설치). 한도 600초(`migrate.activeDeadlineSeconds`). 3단계 `--wait` 안에서 진행 |
| 5 | 기동 확인 | `kubectl get pods,jobs,ingress` — 새 마이그레이션이 있는 배포에서는 api 파드가 `wait-for-migration` 을 통과할 때까지(적용 건수가 이미지의 마이그레이션 수 이상이 될 때까지) `Init` 에 머물다 `Running` 으로 넘어간다 | 개발팀 | 3단계 `--wait` 한도(10분) 안에서 진행. 파드 단위 한도: api `wait-for-migration` 5분(`migrateWait`, 5초×60회), api startupProbe 300초(10초×30회), web startupProbe 50초(5초×10회) |
| 6 | 상태 확인(관리 포트) | `kubectl port-forward deploy/gis-gis-customer-api 8081:8081` 후 `curl -fsS http://localhost:8081/actuator/health` (admin 은 `gis-gis-admin-api`) | 개발팀 | — |
| 7 | smoke 3종 | `API_BASE=<대상>/api scripts/smoke-auth.sh`, `smoke-org-workspace.sh`, `smoke-map.sh` | 개발팀 | — |

운영 시 알아 둘 점:

- 업그레이드 때 마이그레이션 Job 이름에 리비전이 붙어(`<릴리스>-gis-migrate-<제품>-r<리비전>`) 매번 새로 만들어진다. 새 api 파드는 `wait-for-migration` 이 이미지의 마이그레이션 수 이상이 적용될 때까지 대기하고 Job 상태는 보지 않으므로, 새 마이그레이션이 있는 배포에서는 그 마이그레이션이 모두 적용될 때까지 기다리고(새 마이그레이션이 없는 배포나 롤백에서는 Job 이 끝나기 전에도 통과한다), 그동안 이전 파드가 트래픽을 받는다(`maxUnavailable: 0`). 그래서 마이그레이션은 이전 코드와 호환되게(컬럼 추가 → 코드 배포 → 옛 컬럼 제거 순) 쓴다.
- 마이그레이션 Job 은 기본값(`migrate.seed: false`)에서 `migrate --force` 만 실행해 시드가 돌지 않는다. 개발·운영 values 는 이 값을 켜지 않는다(알려진 비밀번호의 개발용 계정이 만들어지기 때문이다). `values-local.yaml` 만 `migrate.seed: true` 라 로컬 k3s 의 Job 은 `migrate --force --seed` 로 돈다. 실패(`backoffLimit: 0`)하면 새 api 파드는 `Init` 에서 멈추고 `--wait` 가 시간 초과로 실패하지만 이전 파드는 계속 서비스한다. 고친 이미지로 다시 업그레이드하거나 롤백한다(JSA-PF-RL-003).
- 로컬 k3s 는 `values-local.yaml` 이 NetworkPolicy 를 켠다. DB 를 다른 네임스페이스·라벨로 띄웠다면 `database.*.host` 와 `networkPolicy.databaseTo` 를 함께 바꾼다. 맞지 않으면 마이그레이션 Job 이 실패하고 api 파드가 `Init:0/1` 에서 멈춘다.
- 로컬 k3s 의 첫 배포 기준 앱 파드는 6개(customer-api 2 · admin-api 2 · customer-web 1 · admin-web 1)다.

## 4. 배포 후 검증

| 항목 | 확인 방법 | 기대 결과 |
| --- | --- | --- |
| 파드·Job 상태 | `kubectl get pods,jobs,ingress` | 앱 파드가 모두 Ready, 마이그레이션 Job 2개 `Complete` |
| 헬스 | 관리 포트 8081 `/actuator/health` (customer·admin 각각) | HTTP 200, 본문의 `status` 가 `UP`. 본문 예: `{"groups":["liveness","readiness"],"status":"UP"}`. 필드 순서·추가 필드는 달라질 수 있으므로 문자열 전체 일치가 아니라 `"status":"UP"` 포함 여부로 판정한다 |
| 관리 포트 비노출 | `curl -s -o /dev/null -w '%{http_code}' http://<ingress-host>/api/actuator/health` | 404. 참고로 `/actuator/health` 는 SPA 폴백이 200 으로 `index.html` 을 주므로 상태 코드가 아니라 **본문**으로 판정한다 |
| 로그인 왕복 | Ingress 경유 로그인 → `/api/auth/me` | HTTP 200 |
| 인증 smoke | `scripts/smoke-auth.sh` | 38 PASS·0 FAIL |
| 조직·워크스페이스·지도 smoke | `scripts/smoke-org-workspace.sh`, `scripts/smoke-map.sh` | smoke-map 42 PASS. 3번 시나리오는 외부 타일 서버(OpenStreetMap)를 호출하므로 외부 네트워크가 필요하고, 소스 등록을 확인하는 시나리오는 호스트 이름을 IP 로 해석하므로 DNS 도 필요하다 |
| 제품 간 격리 | customer 토큰으로 admin API 호출, 반대 방향도 호출 | 양방향 401 |
| NetworkPolicy | admin-api 파드에서 customer-api 8080 호출 | 차단(허용 규칙 없음) |
| 무중단(선택) | 롤링 업데이트 중 반복 요청 | 실패 0건 |

로그인 왕복과 smoke 는 검증용 계정이 있는 환경에서 수행한다.

## 5. 연락 체계

| 역할 | 이름 | 연락처 |
| --- | --- | --- |
| 배포 담당 | 박가람 | - |
| 롤백 결정자 | - | - |
| 인프라(사내 클러스터) 담당 | 박가람 | - |

운영 체계(책임자·직무 분리·연락 체계)는 CSAP 인증 신청 과업(WBS ID 34 서비스 보안 운영체계 구성)에서 확정한다. 개인 연락처는 이 문서에 적지 않는다.

## 6. 근거 자료

- `deploy/README.md` §3–§8, `deploy/charts/gis/`, `scripts/ci/check-chart.sh` (gis-sass 저장소)
- 설계서 장 3 배포 토폴로지 §3.1.1·§3.1.4·§3.1.5, `docs/TESTING.md`
- `docs/01.개발/ADRs/deployment/`(3환경 사다리, 배포 실행 구조, CSAP 범위·운영 타깃)
