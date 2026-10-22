# 열린 PR 작성자에게 보낼 안내 (초안)

- 대상: ws-goyang-uam 에 열린 사람 PR 의 작성자. #128(skynotlimit), #80(garam-park 본인), #140(garam-park 본인)
- 보내는 시점: 폴더 이동 PR 을 올리기 전
- 상태: 초안. 사용자가 문구를 고쳐 보낸다. 아직 보내지 않았다.

## 상황 (사용자 참고)

| PR | 작성자 | 마지막 갱신 | 상태 | 제안 |
| --- | --- | --- | --- | --- |
| #140 docs: UAM 통합테스트 시나리오 31건 수행 결과 기록 | garam-park | — | 두 커밋(`d2a1c07c`, `9ef94bf8`)이 이미 `develop` 에 들어가 있다 | 닫는다(머지할 것이 없다) |
| #128 Feature/운항스케쥴관리시딩추가 | skynotlimit | 2026-08-28 | `deploy/local/db/schema/*.sql`(지금은 gygo-database 로 분리됨), `docs/decisions/0024 · 0025`(번호가 이미 다른 ADR 에 쓰임), 서브모듈 포인터 2개 | 작성자에게 묻는다. 내용이 이미 반영됐으면 닫고, 아니면 gygo-database 저장소 쪽 PR 로 다시 만든다 |
| #80 docs: 노선·회랑 연결 선택값화에 따른 API 가이드 동기화 (TSK-3662) | garam-park | 2026-06-23 | `docs/develop/API-guide/air-routes.md · corridor.md`, 서브모듈 포인터 1개 | 본인 판단. 이동 뒤에는 경로가 `docs/wiki/api/` 로 바뀌어 rebase 가 필요하다 |

dependabot PR 5개(#152 #138 #136 #130 #125)는 `tools/.achive` 삭제(PR #164 머지)로 대상 경로가 없어졌다. dependabot 이 다음 실행 때 스스로 닫는다. 바로 닫으려면 `gh pr close <번호>`.

## 문구 (skynotlimit 님, PR #128 코멘트)

> 안녕하세요. ws-goyang-uam 저장소의 폴더 구조를 바꾸는 작업을 준비하고 있습니다. `repos/` → `apps/`, `docs/decisions/` → `docs/ADRs/`, `docs/develop/` → `docs/wiki/` 등 거의 모든 경로가 바뀌어서, 머지되면 지금 열려 있는 브랜치는 전부 충돌합니다.
>
> 이 PR(#128)은 8월 이후 갱신이 없고, 건드리는 `deploy/local/db/` 는 10월에 `gygo-database` 저장소로 분리됐습니다(ADR-0045). ADR 번호 0024 · 0025 도 지금은 다른 결정에 쓰이고 있습니다.
>
> 아직 필요한 내용이 있으면 알려 주세요. 구조 변경 전에 먼저 머지하거나, `gygo-database` 쪽 PR 로 옮기겠습니다. 응답이 없으면 구조 변경 뒤에 닫겠습니다.
