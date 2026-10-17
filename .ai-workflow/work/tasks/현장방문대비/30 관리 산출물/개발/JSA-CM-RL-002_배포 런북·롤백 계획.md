# 배포 런북·롤백 계획

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-CM-RL-002 |
| 시스템 | 공통(시스템 구분 없음) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 / 승인자 | 개발팀 / <mark>확인 필요</mark> |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 개발팀 | <mark>확인 필요</mark> |

이 문서는 지반침하 스마트 관리 시스템(통합플랫폼)의 배포 런북과 롤백 계획을 한 문서로 요약한 공통 문서다. 통합플랫폼 배포·롤백의 세부 절차와 근거는 JSA-PF-RL-002(배포 런북)와 JSA-PF-RL-003(롤백 계획)이 단일 출처이며, 두 문서와 어긋나면 두 문서를 따른다. 사내 개발 클러스터(`dev0`) 자체의 복구는 두 문서의 범위 밖이라 5절 마지막 항목에서 JSA-PF-OP-001(운영 런북)과 `ops/dev0` 운영 문서를 가리킨다. 배포 실행 자동화는 아직 구성되지 않았고 모든 절차는 사람이 실행한다.

## 1. 배포 개요

- 대상 버전: `develop`(기준 커밋 4e37ab6) 기준이다. 현재 릴리스 `v0.1.0`(2026-09-17)은 마이그레이션 Job 개선(T105, 2026-09-27 KST 병합) 이전 chart 라 이 절차의 대상이 아니며, T105 를 포함한 릴리스 태그는 아직 없다(JSA-PF-RL-002 §1). 이미지는 커밋 SHA 태그로 식별하고 환경 값에는 OCI digest 를 고정한다(`latest` 미사용).
- 대상 환경: 로컬 k3s(리허설, T105 이전 chart 의 첫 설치만 배포·검증 — 현재 chart 의 설치·업그레이드·롤백은 실행 기록 없음) → 사내 k8s 개발(`ops/dev0` 클러스터, 대상 정보 대기로 현재 배포 불가) → NCP 공공기관용 NKS 운영(대상 정보 대기, T077). 같은 이미지(digest)를 환경 사이에서 승격하는 것이 설계 원칙이나, 이를 보장하는 절차는 아직 없다(JSA-PF-RL-002 §1) <mark>확인 필요</mark>.
- 배포 일시·담당: 로컬 k3s 실배포 기록만 있다(2026-09-10, 2026-09-16, 둘 다 첫 설치·T105 이전). 사내 개발·운영 배포 이력은 없다. 담당은 개발팀(담당자명 <mark>확인 필요</mark>).

## 2. 사전 점검

- [ ] 변경 사항 검토 완료 — 대상 커밋의 CI(`test` 워크플로) 전 잡 통과, 이미지 6종 GHCR 게시, 릴리스 승인 체크리스트(JSA-PF-TS-011)
- [ ] 백업 완료 — 운영은 NCP Cloud DB 자동 백업이 기본 방침(구성·주기 미확정), 사내 개발 DB 백업 구성은 <mark>확인 필요</mark>
- [ ] 롤백 방법 확인 — 이전 리비전(`helm history gis`)과 이전 이미지 digest 를 기록해 두었다
- [ ] 외부 소스 인증키 암호화 키(`MAP_SECRET_KEY`)의 주입 방법을 정했다 — chart 가 주입하지 않아 비워 두면 앱의 개발용 고정 기본값이 쓰일 수 있다 <mark>확인 필요</mark>

## 3. 배포 절차

| 순서 | 작업 | 명령·방법 | 담당 | 예상 시간 |
| --- | --- | --- | --- | --- |
| 1 | 대상 환경 values·시크릿 준비 | values 의 이미지·DB 호스트·NetworkPolicy 대상을 채우고, 시크릿 4종은 로컬에서는 `--set-string secret.*`, 개발·운영에서는 외부에서 만든 Secret(SealedSecrets 채택, ADR-2026-09-26.01, 도입 T093 진행 중·미검증)의 이름을 values 로 4개 모두 지정(`database.<제품>.existingSecret`, `auth.<제품>.jwtSecretName`, `<제품>` 은 customer·admin)해 주입. `values-dev.yaml`·`values-prod.yaml` 에는 이 키가 아직 없다 | 개발팀 | — |
| 2 | 차트 검증 | `helm lint`, `helm template`(`scripts/ci/check-chart.sh`) | 개발팀 | — |
| 3 | 설치·업그레이드 | `helm upgrade --install gis charts/gis -f charts/gis/values-<환경>.yaml --set <이미지 digest 6종> --wait --timeout 10m`. 로컬만 `--set-string <시크릿 4종>`(`secret.customerDbPassword` 등)을 더 붙인다. 개발·운영은 `--set-string secret.*` 를 쓰지 않는다 — 1단계에서 values 로 지정한 외부 Secret 이름을 chart 가 참조하고 Secret 을 만들지 않으며, SealedSecret 매니페스트는 `helm upgrade` 전에 apply 한다(JSA-PF-RL-002 3단계) | 개발팀 | 실측 없음. 한도 10분 |
| 4 | 마이그레이션·기동 확인 | `kubectl get jobs,pods,ingress` — 마이그레이션 Job 2개 `Complete`, 앱 파드 Ready | 개발팀 | 실측 각 5초(로컬 k3d, 참고값). 한도 600초 |
| 5 | 헬스·smoke | 관리 포트 8081 `/actuator/health`. smoke(`scripts/smoke-auth.sh`·`smoke-org-workspace.sh`·`smoke-map.sh`)는 시더가 만드는 개발용 계정에 고정돼 있어 시드를 켠 로컬 k3s 에서만 쓸 수 있고, 시드를 끈 사내 개발·운영의 대체 검증은 <mark>확인 필요</mark> | 개발팀 | — |

## 4. 배포 후 검증

| 항목 | 확인 방법 | 기대 결과 |
| --- | --- | --- |
| 기동 상태 | `kubectl get pods,jobs,ingress` | 앱 파드 Ready, Job `Complete` |
| 헬스 | `/actuator/health`(관리 포트) | HTTP 200, `status` 가 `UP`(본문 예: `{"groups":["liveness","readiness"],"status":"UP"}`) |
| 로그인·핵심 기능 | (시드를 켠 로컬 k3s) 로그인 왕복, smoke 3종. 시드를 끈 환경은 로그인할 계정이 없어 수행할 수 없다 <mark>확인 필요</mark> | HTTP 200, 기준 PASS 수(인증 38·지도 42, compose 스택에서 실측한 수치이고 클러스터 실행 기록은 없다) |
| 제품 간 격리 | (시드를 켠 로컬 k3s) 토큰 교차 요청 | 양방향 401 |

## 5. 롤백

- 롤백 판단 기준: 마이그레이션 Job 실패(이전 파드는 계속 서비스), `--wait` 시간 초과, 헬스 `UP` 아님, 로그인 왕복·smoke 실패(시드를 켠 환경), 핵심 기능 장애. 저장소에 기준으로 명시된 것은 첫 항목뿐이고 나머지는 개발팀 제안이다(JSA-PF-RL-003 §1). 오류율·지연 수치 임계치는 정해져 있지 않다(<mark>확인 필요</mark>).
- 롤백 절차: `helm history gis` 로 리비전 확인 → `helm rollback gis <리비전> --wait --timeout 10m` → 롤백 후 검증(헬스·smoke). 롤백도 새 리비전이므로 이전 이미지로 마이그레이션 Job 이 한 번 더 돈다. 롤백을 클러스터에서 실행한 기록은 없다(JSA-PF-RL-003 머리말).
- 데이터 복구 방법: `helm rollback` 은 스키마를 되돌리지 않는다. 마이그레이션을 이전 코드와 호환되게 작성하는 것은 `deploy/README.md` 의 방침일 뿐 CI 가 강제하지 않으며, 호환되지 않는 마이그레이션이 이미 포함돼 있다(JSA-PF-RL-003 §4). 꼭 필요하면 `migrate:rollback` 을 사람이 판단해 실행한다. 데이터 복원은 운영 관리형 DB 자동 백업을 쓰며 복원 절차·리허설은 미정이다.
- 사내 개발 클러스터 자체(노드·etcd) 복구는 이 문서와 상세판(JSA-PF-RL-002·RL-003)의 범위 밖이다. JSA-PF-OP-001 4절·5절과 클러스터 운영 문서(재구축·비밀 파일 백업과 복원)를 따른다. 비밀 파일 3종과 etcd 스냅샷을 암호화 묶음으로 만드는 스크립트가 있으나 자동 주기는 없고 사람이 실행한다. 클러스터 전체 재구축은 2026-10-10 에 1회 해 봤고, 깨진 노드·호스트 교체와 etcd 스냅샷 복원은 실행해 본 적이 없다(미검증).

## 6. 연락 체계

| 역할 | 이름 | 연락처 |
| --- | --- | --- |
| 배포 담당 | <mark>확인 필요</mark> | <mark>확인 필요</mark> |
| 롤백 결정자 | <mark>확인 필요</mark> | <mark>확인 필요</mark> |
| 인프라(사내 클러스터) 담당 | <mark>확인 필요</mark> | <mark>확인 필요</mark> |

운영 체계는 CSAP 인증 신청 과업(WBS ID 34)에서 확정한다.

## 7. 근거 자료

- JSA-PF-RL-002, JSA-PF-RL-003 (이 문서의 상세판), JSA-PF-OP-001 4절·5절(사내 클러스터 복구)
- `deploy/README.md` (gis-sass 저장소), `docs/operations/secrets-backup.md`·`cluster-rebuild.md` (ops/dev0 저장소)
