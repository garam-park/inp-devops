# goyang-uam 을 porthole 구조로 바꾸는 계획

- 기준: 2026-10-22. `projects/goyang-uam` 은 `develop`(`0b3c78c8`, 0단계 뒤), `projects/porthole` 은 `develop`(`325b9c9`).
- 요청: `projects/goyang-uam`(innopam/ws-goyang-uam)을 `projects/porthole`(innopam/ws-jeju-porthole)과 같은 "프로젝트 작업 공간" 구조로 **전체 이동**한다. 실행 전에 이 계획을 먼저 세운다.
- 상태: **1 · 2 · 3단계 끝(10-22, [기록 11](../../../../docs/history/2026/10/22/11.goyang-uam-porthole-layout-step1-3.md)). PR #165 머지됨(`08639a25`), ws 고정 커밋 갱신, 기록 [13](../../../../docs/history/2026/10/22/13.goyang-uam-porthole-layout-merged.md). 이 계획은 끝. 남은 것은 goyang-uam 안의 후속 작업.** #128 안내는 사용자가 직접 한다. D14 반영([기록 12](../../../../docs/history/2026/10/22/12.goyang-uam-gitleaks-tracked-files.md)), D15 는 goyang-uam 작업 T002 로. 결정 15개 모두 끝.
- 함께 읽을 것
  - porthole 의 규칙: [AGENTS.md](../../../../projects/porthole/AGENTS.md), [folder-structure.md](../../../../projects/porthole/.ai-workspace/docs/folder-structure.md), [tasks.md](../../../../projects/porthole/.ai-workspace/docs/tasks.md), [adr.md](../../../../projects/porthole/.ai-workspace/docs/adr.md)
  - goyang-uam 의 지금 규칙: [AGENTS.md](../../../../projects/goyang-uam/AGENTS.md), [README.md](../../../../projects/goyang-uam/README.md)
  - ws 기록: [10-22/08 goyang-uam 서브모듈 등록](../../../../docs/history/2026/10/22/08.goyang-uam-submodule.md), [10-22/06 porthole 서브모듈](../../../../docs/history/2026/10/22/06.porthole-submodule.md)

## 1. 한눈에

porthole 은 "문서 중심 프로젝트 작업 공간"이다. `docs/`(sources → wiki → deliverable, history, ADRs), `.ai-workspace/`(규칙 · 작업 메모 · worktree), `apps/`(코드 서브모듈) 세 덩어리와 커밋 검사(mise · lefthook · gitleaks · markdownlint-cli2)로 이루어진다.

goyang-uam 은 같은 성격의 작업 공간이지만 코드 · 개발 환경이 함께 있고(서브모듈 3개, `tools/`, `deploy/`, `local-backend.sh`), 문서가 이미 많다(git 추적 944 개 중 `docs/` 673 개, LFS 392 개, ADR 45 개). 그래서 **porthole 의 폴더 역할과 규칙을 가져오되, 개발 문서는 wiki 분류를 늘려서 담고(D2 결정), 개발 환경(`deploy/`, `tools/`)은 goyang-uam 의 확장으로 인정**하는 것이 이 계획의 뼈대다. 개발 환경을 루트에 두는 것은 D3 에서 정했다.

작업은 네 단계로 나눈다. (0) 사전 정리 → (1) 폴더 이동과 경로 수정(`git mv`, 한 PR) → (2) 규칙 문서 · AGENTS.md · README 다시 쓰기 → (3) 커밋 검사 도입. 산출물을 `drafts/` · `results/` 로 다시 분류하고 wiki 를 뽑는 일은 (4) 후속 작업으로 뺀다. 파일마다 사람 판단이 필요해서 이번 이동과 섞으면 PR 이 너무 커진다.

## 2. 지금 모습과 목표 모습

### 지금 (goyang-uam, git 추적 기준)

```text
ws-goyang-uam/
├── AGENTS.md  README.md  PRODUCT_BRIEF.md  local-backend.sh  package.json  (+ 잡파일 3: temp.md, 계획초안.md, simulation2 비행 설계….md)
├── .claude/        claude.md(AGENTS.md 와 중복), commands/, rules/ 7개, skills/ 4개, settings.json, worktrees/(무시, stale 17개)
├── .github/        agents/svn-doc-helper.agent.md
├── .ai-workflow/   docs/(lxprod 배포 체크리스트, todos), work/(index.md, .archived/ 5개), .workspace/(무시, 안에 별도 git 저장소 "배포")
├── repos/          gygo-svc3d-front-uamms · gygo-svc3d-back-uamms · gygo-database (서브모듈), gygo-svc3d-front-devhost (일반 파일 8개)
├── tools/          devhost-lite, dummy-simulator, mjpeg-dummy-server, .achive/dummy-batchers, gygo-svc3d-front-microsample (.gitmodules 없는 gitlink)
├── deploy/         local/ (docker-compose, initdb, mock-engine, portal-db), secrets/(무시), lxprod/(무시)
├── tasks/          plan/, 웹접근성/r1–r7, 웹표준/, 증적이미지/  (114개)
└── docs/           (673개)
    ├── decisions/ 45 ADR + README.md(index) + template.md
    ├── develop/   API-guide 39, manual-tests 30, secure-coding 8, analysis 5, database, deployment, design, sample-data, 가이드 md 5
    ├── deliverables/ GDP 72 (hwpx · docx · xlsx · pdf · md, histories/), UAM 26 (xlsx, md, histories/, 10월2일_월간)
    ├── UAM-통합테스트-결과/ round-1 246 (이미지 LFS), round-2
    ├── 시큐어-코딩/ 3차 · 4차 · 5차 점검 결과, 가이드/(무시)
    ├── 대화-자료/  이메일 45, KakaoTalk_Chat_* 3개
    ├── inbox/     auth/ 12, pdf 2, geojson 1
    ├── partners/  client/ pdf 5, consortiums/inbox/VPN 클라이언트 계정.txt
    ├── references/ secure-coding pdf 7, design-guide 2, UAM-구현자료 1
    ├── reports/   20260406, 20260528 (회의 피드백 · 구현 현황, html, wip/)
    ├── research/  simulation2 조사 19
    ├── simulation2/ 기능 명세 9
    ├── tasks/20261001/ simulation2 데이터 설계 + geojson · json 샘플
    ├── 주간보고/ 3,  .agents/디자인가이드/ 2,  READMEs/git-lfs-guide.md,  GETTING_STARTED.md,  session/(무시)
    ├── svn.md     (SVN 색인)
    └── svn/       (무시, svn checkout 27 GB)
```

### 목표 (porthole 구조 + goyang 확장, D2 · D3 결정 기준)

```text
ws-goyang-uam/
├── AGENTS.md                      porthole 식 요약 규칙 (코드 · 배포 절은 goyang 확장)
├── README.md                      사람용 Q&A 색인 (유지, 경로만 고침)        ← porthole 에 없음, D9
├── mise.toml  lefthook.yml  .gitleaks.toml  .markdownlint-cli2.jsonc  .gitignore  .gitattributes
├── local-backend.sh  package.json  deploy/  tools/                        ← goyang 확장 (D3)
├── apps/                          ← repos/ 에서 이름 변경
│   ├── gygo-svc3d-front-uamms/  gygo-svc3d-back-uamms/  gygo-database/   (서브모듈)
│   └── gygo-svc3d-front-devhost/  (일반 파일, 임시 메인앱)
├── docs/
│   ├── sources/                   바깥에서 들어온 원자료 (고치지 않는다)
│   │   ├── chats/emails/  chats/kakao-talks/        ← docs/대화-자료
│   │   ├── outsides/                               ← docs/inbox, docs/partners, docs/references, 산출물 양식 원본
│   │   ├── svn/  (무시, svn checkout)  svn.md(색인)  ← docs/svn, docs/svn.md
│   │   └── index.md
│   ├── wiki/                      porthole 5분류 + goyang 분류 5개 (D2)
│   │   ├── people/ schedule/ glossary/              (처음엔 빈 상태)
│   │   ├── scope/     PRODUCT_BRIEF, 요구사항 분석(analysis), 엔터티정의 확장
│   │   ├── systems/   getting-started, git-lfs, deployment(lxprod 체크리스트 포함), database, service-flow, design-guide 요약
│   │   ├── api/       ← docs/develop/API-guide (39)
│   │   ├── guides/    ← spring-implementation-guide, ui-component-guide, design/design-tokens, secure-coding (8)
│   │   ├── specs/     ← docs/simulation2 (9), 비행 설계 md, sample-data, docs/tasks/20261001
│   │   ├── research/  ← docs/research (19)
│   │   └── tests/     ← docs/develop/manual-tests (30), docs/UAM-통합테스트-결과 (249)
│   ├── deliverable/               정식 산출물
│   │   ├── drafts/
│   │   └── results/md/ · results/for-human/        ← docs/deliverables, 주간보고, reports, 시큐어-코딩 점검 결과 (1차는 폴더째, 분류는 후속 D7)
│   ├── history/YYYY/MM/DD/NN.slug.md                (새로 시작)
│   └── ADRs/  0001–0045 + index.md + template.md    ← docs/decisions
└── .ai-workspace/                 ← .ai-workflow
    ├── docs/   folder-structure.md tasks.md history.md adr.md wiki.md deliverable.md + goyang 규칙(api-guide, subapp, secure-coding, notion-task, design-guide, lxprod-deploy)
    ├── work/   index.md  tasks/T001-…/  .archived-tasks/(지난 simulation2 작업 5개, tasks/ 의 웹접근성 · 웹표준 · plan)
    └── .worktrees/                (git 에 넣지 않음)  ← .claude/worktrees
```

## 3. 매핑표

"방식" 열: `mv` = `git mv`(이력 유지), `new` = 새로 만듦, `rewrite` = 내용 다시 씀, `keep` = 그대로, `del` = 삭제. "결정" 열은 4절 번호.

### 3.1 코드 · 개발 환경

| 지금 | 목표 | 방식 | 비고 | 결정 |
| --- | --- | --- | --- | --- |
| `repos/gygo-svc3d-front-uamms` (서브모듈, `.git` 디렉터리) | `apps/gygo-svc3d-front-uamms` | mv | `git mv` 가 `.gitmodules` 의 `path` 와 `.git/config` 를 같이 고친다 | — |
| `repos/gygo-svc3d-back-uamms` (서브모듈, `.git` 디렉터리) | `apps/gygo-svc3d-back-uamms` | mv | 같음 | — |
| `repos/gygo-database` (서브모듈, `.git` 파일 absorbed) | `apps/gygo-database` | mv | `git mv` 가 `.git` 파일의 `gitdir:` 와 `core.worktree` 를 고친다. 끝나고 `git -C apps/gygo-database status` 로 확인 | — |
| `repos/gygo-svc3d-front-devhost` (일반 파일 8개, 외부 팀 메인앱 임시본) | `apps/gygo-svc3d-front-devhost` | mv | 서브모듈이 아니다. `node_modules` · `dist` · `devhost.log` 는 무시 중 | — |
| `tools/devhost-lite`, `tools/dummy-simulator`, `tools/mjpeg-dummy-server` | `tools/` 그대로 | keep | porthole 에 없는 "dev 전용 도구". AGENTS.md 에 goyang 확장으로 적는다 | D3 |
| `tools/.achive/dummy-batchers` (41개, 이름이 오타) | 삭제(`git rm -r`) | del | dependabot PR 5개가 이 경로를 가리킨다. README 에 "회수 조건: 데이터 소스 확정 시 정리" | D4 |
| `tools/gygo-svc3d-front-microsample` (`.gitmodules` 매핑 없는 gitlink, 원격은 컨소시엄 GitLab) | GitHub `innopam/gygo-svc3d-front-microsample`(private, 새로 만듦)에 push 하고 그 URL 로 `.gitmodules` 에 등록 | new + rewrite | 지금은 `git submodule update --init` 으로 받을 수 없는 반쪽 상태. 로컬 `develop` 이 GitLab `origin/develop` 보다 4 커밋 앞서 있고 push 된 적이 없다(`98d6b93`). `main` 도 같이 올린다. GitLab 은 `gitlab` 원격으로 남겨 둔다. 10-22/08 기록의 `absorbgitdirs` 전제 조건이기도 하다 | D5 |
| `deploy/local/`, `deploy/secrets/`(무시), `deploy/lxprod/`(무시) | `deploy/` 그대로 | keep | `docker-compose.yml` 의 `../../repos/gygo-database/…` 2줄을 `apps/` 로 고친다 | D3 |
| `local-backend.sh` | 그대로 | rewrite | `repos/` 경로 7곳을 `apps/` 로 | — |
| `package.json` (`dev`, `dev:host`, `dev:sub` 스크립트), `package-lock.json`, `pnpm-lock.yaml` | 그대로 | rewrite | 스크립트의 `repos/` 3곳. lock 파일이 둘(npm · pnpm)인 것은 범위 밖 | — |
| `.gitmodules` | 경로 `apps/…` | rewrite | `git mv` 가 고친다. `branch` 키가 없는데 ws 처럼 넣을지는 범위 밖 | — |

### 3.2 문서 `docs/`

| 지금 | 목표 | 방식 | 비고 | 결정 |
| --- | --- | --- | --- | --- |
| `docs/decisions/0001–0045*.md` | `docs/ADRs/` 같은 이름 | mv | 본문은 고치지 않는다(지금 규칙도 porthole 규칙도 "채택한 ADR 은 안 고친다"). 경로 링크만 고친다 | D6 |
| `docs/decisions/README.md` (인덱스) | `docs/ADRs/index.md` | mv + rewrite | porthole 은 `index.md`. 표 형식은 지금 것 유지(번호 · 제목 · Status · Date). 21 파일 56 곳이 `docs/decisions` 를 언급 | D6 |
| `docs/decisions/template.md` | `docs/ADRs/template.md` | mv | MADR 유지. 안의 경로 링크만 고친다 | D6 |
| `docs/develop/API-guide/` (39) | `docs/wiki/api/` | mv | 38 파일 93 곳이 `docs/develop` 을 언급. 폴더 안 구조는 그대로 | D2 |
| `docs/develop/spring-implementation-guide.md`, `ui-component-guide.md`, `design/design-tokens.md`, `secure-coding/` (8) | `docs/wiki/guides/` | mv | 구현 · UI 규칙 | D2 |
| `docs/develop/analysis/` (5), `UAM_엔터티정의_확장.md` | `docs/wiki/scope/` | mv | 요구사항 · 범위 | D2 |
| `docs/develop/database/`, `deployment/`, `service-flow.md`, `parallel-work-environment.md` | `docs/wiki/systems/` | mv | 환경 · 시스템 | D2 |
| `docs/develop/manual-tests/` (30) | `docs/wiki/tests/manual/` | mv | — | D2 |
| `docs/develop/sample-data/` | `docs/wiki/specs/sample-data/` | mv | — | D2 |
| `docs/simulation2/` (기능 명세 9) | `docs/wiki/specs/simulation2/` | mv | 15 파일 29 곳 링크 | D2 |
| `docs/research/` (19) | `docs/wiki/research/` | mv | 6 파일 8 곳 | D2 |
| `docs/tasks/20261001/` (데이터 설계 md + geojson · json) | `docs/wiki/specs/sample-data/simulation2-20261001/` | mv | 14 파일 27 곳. `.gitattributes` 의 `docs/tasks/**/*.geojson` 규칙 경로도 고친다 | D2 |
| `docs/UAM-통합테스트-결과/` (249, 이미지 LFS) | `docs/wiki/tests/integration/` | mv | 수행 기록 · 증적. `tests/manual/` 과 나란히 둔다. PR #140 이 이 폴더를 만든 브랜치인데 이미 develop 에 들어가 있는지 사전 확인 | D2 |
| `docs/GETTING_STARTED.md`, `docs/READMEs/git-lfs-guide.md` | `docs/wiki/systems/getting-started.md`, `docs/wiki/systems/git-lfs-guide.md` | mv | README 링크 2곳 | D2 |
| `docs/대화-자료/이메일/` (45) | `docs/sources/chats/emails/` | mv | 3 파일 4 곳 | — |
| `docs/대화-자료/KakaoTalk_Chat_*/` (3 폴더) | `docs/sources/chats/kakao-talks/` | mv | — | — |
| `docs/inbox/auth/` (12 md), pdf 2, geojson 1 | `docs/sources/outsides/auth/`, `outsides/` | mv | README 가 "인증 체계 문서" 로 링크. 6 파일 14 곳 | — |
| `docs/partners/client/*.pdf` (RFP · 제안서) | `docs/sources/outsides/client/` | mv | — | — |
| `docs/partners/consortiums/inbox/VPN 클라이언트 계정.txt` | `docs/sources/outsides/consortium/` | mv | 이름이 비밀값처럼 보이지만 내용에 비밀번호 줄은 없다(`grep -c` 0). 옮기기 전에 한 번 더 눈으로 본다 | — |
| `docs/references/secure-coding/*.pdf` (7), `design-guide/*.pdf`, `UAM-구현자료/*.pptx` | `docs/sources/outsides/references/` | mv | `design-guide/SUMMARY.md` 는 우리가 쓴 요약 → `docs/wiki/systems/design-guide.md` | — |
| `docs/시큐어-코딩/가이드/` (무시, PDF 5) | `docs/sources/outsides/references/secure-coding/` 와 합침 | — | 무시 중이라 git 에는 없다. `.claude/skills/secure-coding-*` 이 "1차 출처" 로 이 경로를 가리킨다(29 곳) | D7 |
| `docs/시큐어-코딩/3차 · 4차 · 5차` (점검 결과 · 소명) | `docs/deliverable/results/md/secure-coding/` | mv | 감리에 낸 산출물 성격 | D7 |
| `docs/deliverables/GDP/`, `docs/deliverables/UAM/` (98, 대부분 LFS 바이너리) | 1차: `docs/deliverable/GDP/`, `docs/deliverable/UAM/` (폴더째) → 2차(후속): `drafts/` · `results/md/` · `results/for-human/`, 양식 원본(`_원본.hwpx`, 소다시스템 참고본, 개발 가이드 pdf)은 `sources/outsides/` | mv | 어느 파일이 초안 · 완성본 · 양식 · 참고본인지 파일마다 사람이 정해야 한다. `histories/` 31개(날짜별 옛 버전)는 porthole 에 자리가 없다 | D7 |
| `docs/reports/20260406`, `20260528` (회의 피드백 · 구현 현황, html, `wip/`, lua) | `docs/deliverable/results/md/reports/<날짜>/`, html 은 `for-human/`, `wip/` 는 `drafts/` | mv | 3 파일 4 곳 | D7 |
| `docs/주간보고/` (3) | `docs/deliverable/results/md/weekly/` | mv | — | D7 |
| `docs/.agents/디자인가이드/` (버튼-사용, 텍스트-서식) | `.ai-workspace/docs/design-guide/` | mv | 에이전트용 규칙이라 `.ai-workspace/docs/` | — |
| `docs/session/` (`.gitignore` 만) | 삭제. 세션 메모는 `.ai-workspace/work/tasks/<작업>/sessions/` | del | 무시된 md 3개가 디스크에 있다. 지울지 작업 폴더로 옮길지 실행 때 묻는다 | — |
| `docs/svn/` (무시, 27 GB svn checkout) | `docs/sources/svn/` | mv(디스크) | git 밖이라 `mv` 한 번. 같은 볼륨이라 즉시 끝난다. `.gitignore` 항목, `svn.md`, `svn-doc-helper.agent.md`, 12 파일 49 곳 | D8 |
| `docs/svn.md` (SVN 색인) | `docs/sources/svn.md` | mv | — | D8 |
| (없음) | `docs/history/` | new | porthole `history.md` 규칙. 과거 작업은 소급하지 않는다 | — |
| (없음) | `docs/wiki/index.md`, 분류별 `.gitkeep` | new | 분류 표에 goyang 분류 5개(api · guides · specs · research · tests)를 더한다. `PRODUCT_BRIEF.md` → `wiki/scope/product-brief.md`, `design-guide/SUMMARY.md` → `wiki/systems/`. 옮긴 문서 90여 개에 porthole 형식(`갱신:` 줄, `## 출처`)을 붙이는 일은 후속 | D2 |
| (없음) | `docs/sources/index.md`, `docs/sources/outsides/index.md` | new | 원자료 목록 | — |

### 3.3 AI 작업 문서 `.ai-workflow/` → `.ai-workspace/`

| 지금 | 목표 | 방식 | 비고 | 결정 |
| --- | --- | --- | --- | --- |
| `.ai-workflow/` | `.ai-workspace/` | mv | 이름 자체가 porthole 과 다르다. 4 파일 12 곳 | — |
| `.ai-workflow/docs/README.md`, `lxprod-deploy-checklist.md` (LX 운영 배포 문서) | `docs/wiki/systems/deployment/lxprod-deploy-checklist.md` | mv | 규칙이 아니라 프로젝트 문서다 | D2 |
| `.ai-workflow/docs/todos/index.md` | `.ai-workspace/work/` 의 작업으로 흡수 | rewrite | 내용 보고 T0xx 로 쪼갠다 | — |
| `.ai-workflow/work/index.md` (현황판) | `.ai-workspace/work/index.md` | rewrite | porthole 표(ID · 제목 · 상태 · 갱신일). "작업 문서는 develop 에 바로 커밋, 산출물만 PR" 운영 규칙은 goyang 규칙으로 AGENTS.md 에 남긴다 | D10 |
| `.ai-workflow/work/.archived/` (md 4 + `20261014-simulation2/`) | `.ai-workspace/work/.archived-tasks/` + `index.md` | mv | 번호가 없다. `T001–T005` 를 소급해 붙일지, 이름만 두고 index 에만 적을지 | D10 |
| `.ai-workflow/work/tasks/.archived/` (빈 폴더), `tasks/.gitkeep` | 삭제 | del | 중복 | — |
| `.ai-workflow/.workspace/` (무시; `배포/` 는 **별도 git 저장소**, `작업1/`) | `.ai-workspace/.workspace/` (디스크만) | mv(디스크) | git 밖. `배포/` 저장소의 원격이 어디인지 실행 때 확인 | — |
| `tasks/plan/` (3), `tasks/웹접근성/r1–r7`, `tasks/웹표준/`, `tasks/증적이미지/` (114개) | `.ai-workspace/work/.archived-tasks/` | mv | 끝난 작업의 기록 · 증적. 44 파일 100 곳이 `tasks/` 를 언급하지만 대부분 Notion "작업" 의미라 실제 경로 링크만 고친다 | D10 |
| 루트 `temp.md` (코드값 변경 후속 TODO) | `.ai-workspace/work/tasks/T0xx-aircraft-status-code-followup/index.md` | mv + rewrite | 살아 있는 할 일 | — |
| 루트 `계획초안.md` (simulation2 요구 메모, 10-06) | `.ai-workspace/work/.archived-tasks/20261014-simulation2/` 옆 | mv | 끝난 작업의 입력 메모 | — |
| 루트 `simulation2 비행 설계 (경유점 따라 비행, 여러 기체).md` (10-19) | `docs/wiki/specs/simulation2/flight-design-waypoints.md` 또는 작업 폴더 | mv | 내용이 명세인지 작업 메모인지 실행 때 읽고 정한다 | — |
| `.claude/worktrees/` (무시, stale 17개 등록) | `.ai-workspace/.worktrees/` + `.gitignore` | new | `git worktree prune` 으로 stale 등록을 지운다(10-22/08 의 "남은 일") | — |

### 3.4 도구 설정 `.claude/`, `.github/`, `.vscode/`

| 지금 | 목표 | 방식 | 비고 | 결정 |
| --- | --- | --- | --- | --- |
| `.claude/claude.md` | 삭제 | del | AGENTS.md 와 같은 내용, 링크 4개는 이미 깨져 있다 | D11 |
| `.claude/rules/rule_adr.md`, `rule_api-guide.md`, `rule_subapp.md`, `rule_notion-task-interpretation.md` | `.ai-workspace/docs/adr.md`(MADR 규칙 유지, history 연결만 추가), `api-guide.md`, `subapp.md`, `notion-task.md` | mv + rewrite | porthole 식: 긴 규칙은 `.ai-workspace/docs/`, AGENTS.md 에서 링크. 36 파일 125 곳이 `.claude/` 경로 언급 | D11 |
| `.claude/rules/rule_secure-coding*.md` (3) | `.ai-workspace/docs/secure-coding/` | mv | 스킬이 참조 | D11 |
| `.claude/skills/secure-coding-*/SKILL.md` (4) | `.claude/skills/` 그대로 | keep + rewrite | Claude Code 전용 경로라 옮기지 않는다. 안의 경로(`docs/시큐어-코딩/…`, `.claude/rules/…`)만 고친다 | D11 |
| `.claude/commands/verified-tag.md`, `.claude/settings.json` | 그대로 | keep + rewrite | `repos/` 6곳 | — |
| `.github/agents/svn-doc-helper.agent.md` | 그대로 | rewrite | `docs/svn` 경로 | D8 |
| `.github/skills/adr-authoring/` (빈 폴더, 추적 안 됨) | 삭제 | del(디스크) | — | — |
| `.vscode/settings.json`, `.omm`, `opencode.json`, `.codegraph`(심볼릭 링크, 무시) | 그대로 | keep | — | — |
| `.env.tsk.example` (추적), `.env.tsk` (무시) | 삭제 | del | 읽는 곳이 없다 | D12 |

### 3.5 루트 문서와 설정 파일

| 지금 | 목표 | 방식 | 비고 | 결정 |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | porthole 식으로 다시 씀: 구조 · 규칙 문서 표 · 핵심 규칙 · 커밋 검사 · worktree · 규칙 추가 + goyang 절(개발 환경, DB 스키마, API 가이드, 시큐어코딩 스킬, SVN 도우미) | rewrite | "Imported Claude Cowork project instructions" 빈 절은 지운다 | D9 |
| `README.md` (사람용 Q&A 색인) | 유지, 경로 수정 | rewrite | porthole 엔 없지만 사람에게 유용하다. 이미 깨진 링크 2개(`rule_task-management.md`, `mcp-notion.md`)는 지우거나 대체 | D9 |
| `PRODUCT_BRIEF.md` | `docs/wiki/scope/product-brief.md` | mv | 출처 줄 추가 | — |
| `.gitignore` | porthole 항목(`.env*`, 키 파일, 동기화 파일) + goyang 항목(`docs/sources/svn/`, `deploy/secrets/`, `.port-offset`, `.local-pids`, …) 합침 | rewrite | `docs/svn/` → `docs/sources/svn/`, `.worktrees/` → `.ai-workspace/.worktrees/` 처럼 경로 갱신 | — |
| `.gitattributes` (LFS: `docs/**`) | 유지, `docs/tasks/**` 규칙 경로만 갱신 | rewrite | 옮겨도 `docs/` 아래라 LFS 포인터는 그대로. porthole 은 LFS 를 안 쓰지만 goyang 은 필요 | — |
| `.markdownlint.yml` (MD013 · MD051 · MD060 · MD040 끔, MD024 siblings) | `.markdownlint-cli2.jsonc` (porthole 규칙 집합) | rewrite | porthole 은 MD040 · MD051 을 **켠다**. 기존 673개 문서가 통과하지 못할 가능성이 크다 → 3단계에서 전체 검사 후 `ignores` 에 옛 문서 폴더를 넣을지, 고칠지 정한다 | D13 |
| (없음) | `mise.toml`, `lefthook.yml`, `.gitleaks.toml` | new | porthole 것을 복사하고 `title` 과 `ignores`(`apps/**`, `tools/**`, `.ai-workspace/.worktrees/**`)를 바꾼다. `mise run lint` 의 gitleaks 는 **커밋 이력 전체**를 보므로 옛 커밋에 비밀값이 있으면 걸린다 | D13 |

## 4. 결정 목록

하나씩 묻는다. 추천은 굵게. 정해진 것은 번호 옆에 ✅ 와 고른 선택지, 날짜를 적는다.

| 번호 | 결정 | 선택지 | 추천과 이유 |
| --- | --- | --- | --- |
| D1 ✅ A (10-22) | 작업 브랜치의 기준 | (A) PR #161(`chore/split-gygo-database`)을 먼저 develop 에 머지하고 develop 에서 `chore/porthole-layout` 분기 (B) `chore/split-gygo-database` 위에 바로 분기 | **A**. 이동 PR 은 거의 모든 파일을 건드려서 다른 PR 과 섞이면 리뷰가 안 된다. #161 은 한 커밋이라 먼저 머지하는 비용이 작다 |
| D2 ✅ B (10-22) | 개발 문서의 자리 | (A) `docs/develop/` 을 goyang 확장 폴더로 유지 (B) wiki 분류를 늘려서 담음 | **B 로 결정**(사용자). porthole `wiki.md` 가 "분류는 필요에 따라 추가할 수 있다" 고 했으니 5분류에 `api` · `guides` · `specs` · `research` · `tests` 를 더하고, 환경 문서는 `systems`, 요구사항 분석은 `scope` 로. 분류 이름과 배정은 실행 때 표로 다시 확인한다. 분류 안에 하위 폴더(`api/`, `tests/integration/round-1/` 등)를 두는 것은 porthole 규칙(`wiki/<분류>/<슬러그>.md`)의 확장이라 `wiki.md` 에 적는다 |
| D3 ✅ A (10-22) | `deploy/`, `tools/`, `local-backend.sh` 위치 | (A) 루트에 그대로, AGENTS.md 에 확장으로 명시 (B) `apps/` 아래로 | **A**. `apps/` 는 "코드 저장소(서브모듈)" 자리다. 섞으면 porthole 의 뜻이 흐려진다. D2 처럼 porthole 의 자리에 넣는다면 후보는 `apps/tools/` · `apps/deploy/` 인데, `apps/` 의 뜻을 "코드와 그 실행 환경" 으로 넓혀야 한다 |
| D4 ✅ B (10-22) | `tools/.achive/dummy-batchers` | (A) `tools/.archive/` 로 오타 수정 (B) 삭제(이력에 남는다) (C) 그대로 | **B**. README 가 "회수 조건: 데이터 소스 확정 시 정리" 라 했고, dependabot PR 5개가 이 폴더 때문에 열려 있다. 삭제하면 그 PR 들도 닫힌다 |
| D5 ✅ A′ (10-22) | `tools/gygo-svc3d-front-microsample` gitlink | (A) `.gitmodules` 에 등록(컨소시엄 GitLab URL) (B) gitlink 제거, 폴더는 `.gitignore` | **사용자 결정: `.gitmodules` 에 등록하되 origin 은 `github.com/innopam` 만.** GitHub 에 `innopam/gygo-svc3d-front-microsample` 을 private 로 만들고(이름은 폴더 이름을 따름. GitLab 이름은 `gygo-svc3d-front-my-loc`) `develop` · `main` 을 push 한 뒤, 서브모듈 `origin` 을 GitHub 로 바꾸고 `.gitmodules` 에 `path = tools/gygo-svc3d-front-microsample`, `url = git@github.com:innopam/gygo-svc3d-front-microsample.git`, `branch = develop` 으로 등록한다. 0단계에서 한다 |
| D6 ✅ C (10-22) | ADR 형식 | (A) 기존 45개는 그대로, `README.md` → `index.md`, 새 ADR 은 porthole 템플릿 (B) 기존도 porthole 템플릿으로 변환 (C) MADR 유지 | **C 로 결정**(사용자). 폴더만 `docs/ADRs/` 로 옮기고 형식은 지금 MADR(`template.md`)을 계속 쓴다. 인덱스는 `README.md` → `index.md` 로 이름만 맞춘다. `.ai-workspace/docs/adr.md` 는 porthole 것이 아니라 지금 `rule_adr.md` 내용(트리거 · 상태 전이 · 절차)을 옮겨 쓰고, history 와의 관계("방향을 정한 결정은 history 에도 번호를 적는다")만 porthole 에서 가져온다 |
| D7 ✅ A (10-22) | 산출물 분류 시점 | (A) 1차는 `docs/deliverable/GDP · UAM · reports · weekly · secure-coding` 으로 폴더째 옮기고, `drafts/` · `results/` 분류는 후속 작업 (B) 이번에 파일마다 분류까지 | **A**. 98+32+29+3 개를 파일마다 사람이 봐야 한다. 이번 PR 과 섞으면 검토가 불가능하다 |
| D8 ✅ A (10-22) | `docs/svn/` 위치 | (A) `docs/sources/svn/` 으로 (B) `docs/svn/` 유지 | **A**. 컨소시엄 원자료라 sources 가 맞다. 디스크 `mv` 한 번이고 참조 수정은 12 파일 |
| D9 ✅ A (10-22) | `README.md` 유지 | (A) 사람용 Q&A 색인으로 유지, AGENTS.md 는 porthole 식 (B) README 삭제, AGENTS.md 하나로 | **A**. 신규 개발자 온보딩 문서다. porthole 은 작아서 없을 뿐이다 |
| D10 ✅ A (10-22) | 작업 메모 번호와 운영 규칙 | (A) 끝난 작업(`.archived/` 5 + `tasks/` 웹접근성 · 웹표준 · plan)은 번호 없이 이름만 두고 `.archived-tasks/index.md` 에 적음, 새 작업부터 `T001` (B) 소급해 번호 부여 | **A**. 소급 번호는 의미가 없고 링크만 늘어난다. "작업 문서는 develop 에 바로 커밋" 규칙은 porthole 에 없으니 AGENTS.md 에 goyang 규칙으로 남길지 함께 정한다 |
| D11 ✅ A (10-22) | `.claude/rules/` 처리 | (A) 규칙 본문을 `.ai-workspace/docs/` 로 옮기고 AGENTS.md 에서 링크, `.claude/claude.md` 삭제, 스킬은 `.claude/skills/` 유지 (B) `.claude/` 전부 그대로 | **A**. porthole 원칙은 "규칙은 도구와 무관한 자리에". `.claude/rules/` 는 Claude Code 만 자동으로 읽는다. 스킬은 Claude Code 전용 기능이라 남긴다 |
| D12 ✅ C (10-22) | `.env.tsk.example` | (A) `env.tsk.example` 로 이름 변경 (B) `.gitleaks.toml` 에 예외 (C) 삭제 | **C 로 결정**. 조사 결과 읽는 곳이 없다. 설치된 스킬(`~/.claude/skills` 의 `ntn-*` · `inp-*`)과 저장소 안 어디에도 `.env.tsk` · `NOTION_DATABASE_ID` 를 읽는 코드가 없고 `.gitignore` 만 언급한다. `git rm .env.tsk.example`, `.gitignore` 의 `.env.tsk` 줄 삭제(porthole 의 `.env.*` 가 대신 막는다). 디스크의 `.env.tsk` 는 실행 때 지울지 묻는다 |
| D13 ✅ A (10-22) | 커밋 검사 도입 범위 | (A) 3단계에서 porthole 설정을 그대로 넣고 전체 검사 → 걸리는 옛 문서 폴더는 `ignores` 로 빼고 후속에서 고침 (B) 이번엔 gitleaks pre-commit 만 (C) 도입 안 함 | **A**. porthole 과 같게 가는 것이 요청의 취지다. 단 `mise run lint` 의 이력 전체 gitleaks 결과는 먼저 보고 나서 정한다 |
| D14 ✅ B (10-22, 커밋 `fff728d0`) | gitleaks 이력 검사 120건(20 커밋) 처리 | (A) `.gitleaksignore` 에 120건 지문을 적어 `mise run lint` 를 통과시킴 (B) `lint:secrets` 를 이력 대신 작업 트리(`gitleaks dir`, 추적 파일)만 보게 바꿈 (C) 이력을 다시 씀(filter-repo) | **B**. 이력은 이미 push 돼 여러 clone 에 있어 다시 쓸 수 없고, 지문 120개를 적어도 뜻이 없다. 앞으로는 pre-commit 이 막는다. 단 이력의 `.opencode/opencode.json`(커밋 `1ebfc2f5`, 2026-06-01, sky221b9)에 Notion API 토큰이 있다 → **토큰을 폐기(재발급)해야 한다**, 선택지와 무관 |
| D15 ✅ A (10-22, goyang-uam 작업 T002) | 추적 파일의 비밀값 후보 28건(원자료 `sources/outsides/auth/*`, 카카오톡 csv, 이메일, `12.합사_계정정보.md`, 시큐어코딩 예시, `.env.example`) | (A) 후속 작업에서 파일마다 보고 실제 비밀값은 `[REDACTED:<종류>]` 로 가리고 예시 · 가짜는 `gitleaks:allow` (B) 지금 PR 에서 처리 (C) 그대로 | **A**. porthole 규칙("원자료의 비밀값은 넣기 전에 가린다")이고 사람이 봐야 한다. 이 PR 과 섞지 않는다. `12.합사_계정정보.md` 는 이름부터 계정 정보라 먼저 본다 |

## 5. 단계별 순서

각 단계 끝에 커밋 하나. 1단계는 PR 하나로 보낸다. 모든 명령은 goyang-uam 루트(`/Users/garam/ops/inp/ws/projects/goyang-uam`)에서.

### 0단계. 사전 정리 — 끝(10-22). PR #161 머지 `10838cb1`, PR #164 머지 `0b3c78c8`

1. ✅ PR #161 머지(D1-A). `git checkout develop && git pull`.
2. ⏳ 열린 PR 확인. #140 은 커밋이 이미 develop 에 있다(닫으면 됨). #128(skynotlimit), #80 은 안내 초안 [notice-open-prs.md](notice-open-prs.md) 를 **사용자가 보낸다.** dependabot PR 5개는 `.achive` 삭제로 dependabot 이 스스로 닫는다.
3. ✅ `git worktree prune` (stale 17개). `.github/skills/adr-authoring/` 빈 폴더 삭제.
4. ✅ (PR #164) D5: `gh repo create innopam/gygo-svc3d-front-microsample --private`, 서브모듈 안에서 `git remote rename origin gitlab && git remote add origin git@github.com:innopam/gygo-svc3d-front-microsample.git && git push -u origin develop main`, 루트에서 `.gitmodules` 항목 추가 후 `git submodule sync` 와 `git submodule status tools/gygo-svc3d-front-microsample` 로 `98d6b93` 확인. D4: `git rm -r tools/.achive`, README 의 dummy-batchers 줄 정리.
5. ✅ 기준 수치: `git ls-files` 944, `git lfs ls-files` 392, 서브모듈 4개(`c77ce61` · `b300f82` · `ebd748d` · `98d6b93`), svn Revision 4115.
6. ✅ 링크 점검 [check-links.py](check-links.py). 이동 전 결과 [links-before.txt](links-before.txt): 이미 깨진 링크 86개(md 324개). 이동 후 `python3 -I check-links.py projects/goyang-uam > links-after.txt; diff links-before.txt links-after.txt` 로 "새로 깨진 것" 만 고친다. 이미 깨진 86개는 4단계 후속.

### 1단계. 폴더 이동과 경로 수정 — 끝(10-22). 브랜치 `chore/porthole-layout`, 커밋 `2d5a51a7` · `85d55a12` · `addb7974`

커밋을 세 개로 나눈다. 각 커밋 뒤에 `local-backend.sh status` 와 링크 점검이 통과해야 한다.

1. **코드 · 개발 환경** — `git mv repos apps`. 바로 `git submodule status` 로 세 서브모듈 SHA 가 그대로인지, `git -C apps/gygo-database status` 가 되는지 본다. `deploy/local/docker-compose.yml`, `local-backend.sh`, `package.json`, `.claude/commands/verified-tag.md`, `.claude/skills/*` 의 `repos/` 를 `apps/` 로. `docker compose -f deploy/local/docker-compose.yml config` 로 볼륨 경로 확인.
2. **문서** — 3.2 표대로 `git mv`. 새 폴더(`docs/sources/…`, `docs/wiki/…` 10 분류, `docs/deliverable/…`, `docs/history/`)와 porthole 식 `.gitkeep`(폴더 설명 md) · `index.md` 를 만든다. `docs/svn` 은 `mv`(디스크) + `.gitignore` 갱신. `.gitattributes` 의 `docs/tasks/**` 규칙 갱신. `git lfs ls-files | wc -l` 이 392 인지 확인.
3. **AI 작업 문서와 도구 설정** — `git mv .ai-workflow .ai-workspace`, `tasks/` → `.archived-tasks/`, `.claude/rules/*` → `.ai-workspace/docs/`, 루트 잡파일 3개 이동, `.claude/claude.md` 삭제, `.ai-workspace/.worktrees/.gitignore` 추가, `.ai-workspace/work/tasks/.gitignore` · `.archived-tasks/.gitignore`(바이너리 문서 제외) 추가.
4. **경로 일괄 치환** — 6절 표의 옛 경로 → 새 경로를 `git ls-files '*.md' '*.sh' '*.json' '*.yml' '*.py' '*.cjs'` 대상으로 `sed`(또는 Python) 치환. `tasks/` 와 `.claude/` 처럼 일반 단어와 겹치는 것은 상대 링크 `](…)` 와 코드 스팬 안의 경로만 바꾸고 나머지는 눈으로 본다. ADR 본문의 경로도 링크 보정으로 보고 바꾼다(D6). 서브모듈 안은 건드리지 않는다(gygo-database 의 README 가 `ws-goyang-uam` 의 `deploy/local/` 과 `local-backend.sh` 를 언급하는데 둘 다 자리가 안 바뀐다).
5. 링크 점검 스크립트를 다시 돌려 "새로 깨진 것" 0 을 확인. PR 생성. 본문에 매핑표 요약과 "다른 브랜치는 머지 후 rebase 필요" 를 적는다.

### 2단계. 규칙 문서와 AGENTS.md · README — 끝(10-22). 커밋 `71624828`, 같은 PR

1. porthole 의 `.ai-workspace/docs/{folder-structure,tasks,history,adr,wiki,deliverable}.md` 를 가져와 goyang 에 맞게 고친다(저장소 이름, `apps/` 아래 세 저장소, wiki 분류 10개와 하위 폴더 허용, `deploy/` · `tools/` 확장, ADR 번호가 0045 부터 이어진다는 것, LFS).
2. `AGENTS.md` 를 porthole 식으로 다시 쓴다. goyang 절: 개발 · 스테이지 환경, DB 스키마(gygo-database), API 가이드 규칙, 서브앱 UI 규칙, 디자인 토큰, 시큐어코딩 스킬, Notion 작업 해석, SVN 도우미, java 버전.
3. `README.md` 경로 수정, 깨진 링크 2개 정리, "프로젝트 구조" 트리를 새 구조로.
4. `.ai-workspace/work/index.md` 를 porthole 표로, `.archived-tasks/index.md` 에 끝난 작업 목록(D10).
5. `docs/history/2026/MM/DD/01.porthole-layout.md` 에 이 이동을 기록하고, `docs/ADRs/0046-porthole-layout.md` 로 "porthole 구조를 따른다, wiki 분류를 늘리고 deploy · tools 는 확장" 결정을 남긴다(MADR, `Status: Accepted`).

### 3단계. 커밋 검사 — 끝(10-22). 커밋 `1e9bb4d5`, 같은 PR(#165). gitleaks 이력 결과는 D14

1. porthole 의 `mise.toml`, `lefthook.yml`, `.gitleaks.toml`, `.markdownlint-cli2.jsonc` 복사. `ignores` 에 `apps/**`, `tools/**`, `.ai-workspace/.worktrees/**`. `.markdownlint.yml` 삭제.
2. `mise trust && mise install && mise exec -- lefthook install`.
3. `mise run lint` 결과를 본다. markdownlint 가 많이 걸리면 옛 문서 폴더(`docs/deliverable/**`, `docs/wiki/tests/**` 등)를 `ignores` 에 넣고 후속 작업으로 뺀다. gitleaks 가 이력에서 걸리면 `.gitleaksignore` 지문으로 넘길지, 이력을 그대로 둘지 사람에게 묻는다(D13).

### 4단계. 후속 작업 (이 계획 밖, 새 작업으로)

- 산출물 파일별 `drafts/` · `results/md/` · `results/for-human/` 분류와 양식 원본의 `sources/outsides/` 이동(D7).
- `docs/wiki/` 채우기: 참여자 · 연락처(people), 일정(schedule), 용어(glossary) 는 빈 상태로 시작한다. 원자료는 이미 `sources/` 에 있다. 옮겨 온 개발 문서 90여 개에 `갱신:` 줄과 `## 출처` 를 붙인다.
- `.ai-workspace/docs/todos/` 와 `temp.md` 를 `T001…` 작업으로.
- 3단계에서 `ignores` 로 뺀 옛 문서의 markdownlint 수정.
- ws 쪽: `.gitmodules` 의 `projects/goyang-uam` 고정 커밋을 머지 후 develop 끝으로 갱신, ws `docs/history` 기록.

## 6. 깨지는 참조 (이동 전 집계)

대상: git 추적 중인 md · sh · json · yml · py · cjs. 서브모듈 안은 제외.

| 옛 경로 | 새 경로 | 파일 수 | 언급 횟수 | 메모 |
| --- | --- | --- | --- | --- |
| `repos/` | `apps/` | 129 | 2,530 | 대부분 ADR · API 가이드 본문의 `repos/gygo-svc3d-…` 언급. 단순 치환 가능 |
| `docs/develop` | `docs/wiki/{api,guides,scope,systems,tests,specs}` | 38 | 93 | 하위 폴더별로 목적지가 달라 치환 표를 폴더 단위로 만든다 |
| `docs/decisions` | `docs/ADRs` | 21 | 56 | `README.md` → `index.md` 도 함께 |
| `docs/svn` | `docs/sources/svn` | 12 | 49 | `svn.md`, `.github/agents/svn-doc-helper.agent.md`, README 의 svn 명령 |
| `docs/시큐어-코딩` | `docs/deliverable/…/secure-coding`, `docs/sources/outsides/references/secure-coding` | 6 | 29 | `.claude/skills/secure-coding-*` 가 출처로 가리킨다 |
| `docs/simulation2` | `docs/wiki/specs/simulation2` | 15 | 29 | — |
| `docs/tasks` | `docs/wiki/specs/sample-data/simulation2-20261001` | 14 | 27 | `.gitattributes` 포함 |
| `docs/inbox` | `docs/sources/outsides/…` | 6 | 14 | README "인증 체계 문서" |
| `docs/deliverables` | `docs/deliverable/…` | 10 | 12 | — |
| `.ai-workflow` | `.ai-workspace` | 4 | 12 | — |
| `docs/research` | `docs/wiki/research` | 6 | 8 | — |
| `docs/대화-자료`, `docs/reports`, `docs/references`, `docs/UAM-통합테스트-결과`, `docs/GETTING_STARTED`, `docs/partners`, `docs/주간보고`, `docs/READMEs` | 3.2 표 | 각 1–3 | 각 1–4 | — |
| `deploy/` | (그대로) | 42 | 162 | D3-A 면 안 바뀐다. `docker-compose.yml` 의 `../../repos` 2줄만 |
| `tools/` | (그대로) | 17 | 36 | D3-A 면 안 바뀐다 |
| `local-backend.sh` | (그대로) | 14 | 37 | 안의 `repos/` 7곳만 |
| `.claude/` | `.ai-workspace/docs/…` (rules), `.claude/skills` 는 그대로 | 36 | 125 | `rules/` 링크만 바뀐다. `skills/` 언급은 그대로 |
| `tasks/` | `.ai-workspace/work/.archived-tasks/…` | 44 | 100 | 대부분 Notion "작업(task)" 의미. 상대 링크만 고친다 |

이미 깨져 있는 링크(이동과 무관, 2단계에서 정리): README 의 `.claude/rules/rule_task-management.md`, `docs/develop/mcp-notion.md`; `.claude/claude.md` 의 `rules/rule_adr.md`, `rules/rule_api-guide.md`.

## 7. 검증

이동 후 다음이 모두 맞아야 한다.

- `git status` 깨끗, `git ls-files | wc -l` 이 이동 전 944 에서 새로 만든 `.gitkeep` · `index.md` · 규칙 문서 수만큼만 늘어남, `git lfs ls-files | wc -l` 392.
- `git submodule status`: 세 서브모듈이 `apps/` 경로로, microsample 은 `tools/` 그대로, SHA 는 이동 전과 같음(`c77ce61`, `b300f82`, `ebd748d`, `98d6b93`). `git submodule update --init --recursive` 가 새 clone 에서 되는지는 임시 폴더에 clone 해서 본다.
- `./local-backend.sh status`, `docker compose -f deploy/local/docker-compose.yml config` 가 `apps/gygo-database/database/…` 볼륨을 가리킴. 가능하면 `./local-backend.sh infra` 로 DB 초기화까지.
- `npm run dev:sub` 가 `apps/gygo-svc3d-front-uamms` 에서 뜸(VPN 필요하면 경로만 확인).
- 링크 점검 스크립트: 새로 깨진 상대 링크 0.
- `svn info docs/sources/svn` 이 같은 Revision.
- 3단계 뒤: `mise run lint` 통과(또는 `ignores` 로 뺀 목록이 기록에 있음), `git commit` 시 lefthook 이 돈다.
- ws 쪽: `git -C /Users/garam/ops/inp/ws submodule status projects/goyang-uam` 이 새 커밋.

## 8. 되돌리기

- PR 머지 전: 브랜치를 버린다. `git checkout develop && git branch -D chore/porthole-layout`. 디스크만 옮긴 것(`docs/svn`, `.ai-workflow/.workspace`, `.claude/worktrees`)은 `mv` 로 되돌린다. 서브모듈 `.git` 은 `git mv` 가 되돌릴 때도 함께 고친다.
- PR 머지 후: `git revert -m 1 <머지 커밋>`. 이동 커밋이 크지만 revert 는 가능하다. 다른 사람이 새 경로 위에 커밋을 쌓기 전에 해야 한다.
- 0단계(PR #161 · #164)는 [기록 10](../../../../docs/history/2026/10/22/10.goyang-uam-porthole-layout-step0.md) 의 되돌리는 방법.

## 9. 위험과 주의

- **다른 사람의 브랜치.** 이동 PR 이 머지되면 열린 브랜치 전부가 충돌한다(#128 skynotlimit, #80, 그리고 로컬에만 있는 `claude/*` 20여 개). 머지 시점을 정하고 미리 알린다. 로컬 `claude/*` 브랜치는 대부분 끝난 작업이라 지워도 되는지 실행 때 묻는다.
- **서브모듈 `git mv`.** `.git` 디렉터리인 서브모듈(front · back)과 absorbed 된 것(gygo-database)이 섞여 있다. `git mv` 는 둘 다 지원하지만, 옮긴 직후 세 폴더 각각에서 `git status` 가 되는지 반드시 본다. 안 되면 `.git` 파일의 `gitdir:` 와 `.git/modules/…/config` 의 `core.worktree` 를 손으로 맞춘다.
- **LFS.** `git mv` 는 포인터 파일을 옮기므로 안전하다. 단 `.gitattributes` 규칙이 `docs/**` 라 `docs/` 밖으로 나가는 파일이 있으면 LFS 에서 빠진다. 이 계획에서는 `docs/` 밖으로 나가는 바이너리가 없다(`tasks/웹접근성/*/evidence/*.png` 는 원래 LFS 가 아니다).
- **27 GB `docs/svn`.** git 밖이라 `mv` 는 즉시 끝나지만, 실수로 `git add` 하면 안 된다. `.gitignore` 를 **먼저** 고치고 옮긴다.
- **`.ai-workflow/.workspace/배포` 는 별도 git 저장소.** 원격과 상태를 확인하고 옮긴다. 안의 커밋이 push 안 됐으면 먼저 push.
- **gitleaks 이력 검사.** `mise run lint` 가 과거 커밋까지 본다. 결과를 보고 나서 정한다(D13). pre-commit 은 스테이징 파일만 본다.
- **markdownlint 규칙 강화.** porthole 은 MD040(코드 블록 언어), MD051(앵커) 을 켠다. 옛 문서가 대량으로 걸릴 수 있다.
- **Notion · 스킬 경로.** `.claude/skills/secure-coding-*` 과 `.github/agents/svn-doc-helper` 가 문서 경로를 하드코딩한다. 치환 후 스킬을 한 번 호출해 본다.

## 10. 범위 밖

- 서브모듈 세 개 안의 내용(코드, 서브모듈 자체의 AGENTS.md · README). gygo-database 가 `ws-goyang-uam` 의 `deploy/local/` 을 언급하는 것은 경로가 안 바뀌니 그대로.
- ws 루트 `.gitmodules` 의 `projects/goyang-uam` 경로 · URL.
- `package-lock.json` 과 `pnpm-lock.yaml` 둘 중 하나로 정리.
- 산출물 파일별 분류, wiki 작성, 옛 문서 markdownlint 수정(4단계로).
