# jeju-ai 고도화 — 인계 (2026-10-22 중단 시점)

- 기준: 2026-10-22 09:45 KST. 이 세션은 여기서 끝난다. 다음 세션은 이 문서부터 읽는다.
- 범위: `projects/jeju-ai/apps` 의 FE(innopam/jeju-ai-saas-fe) · BE(innopam/jeju-ai-saas-be)와 그 dev 배포(ops/dev0)
- 시작 요청(10-21): "작업목록 xlsx 에서 할 수 있는 작업을 골라 결정 없이 할 수 있는 것부터 시작"
- 함께 읽을 것
  - 전체 현황: [../../index.md](../../index.md). 작업목록 108건의 실제 상태가 있다.
  - 결정 대기 상세: [결정.md](결정.md)
  - 겹치는 다른 작업: [CSAP 인증준비 index](../CSAP-인증준비/index.md)의 '결정 (사람)' 1 · 2 · 3 · 6 · 7 · 8 · 9 가 jeju-ai 결정과 겹친다(결정.md 에 표시).

## 1. 다음 세션이 처음 할 일

1. 이 문서와 [결정.md](결정.md)를 읽는다.
2. 상태를 다시 보고 2절 표와 비교한다(ws 루트에서).

   ```sh
   cd /Users/garam/ops/inp/ws
   for r in fe be; do gh pr list -R innopam/jeju-ai-saas-$r \
     --json number,headRefName,headRefOid,mergeStateStatus,statusCheckRollup \
     --jq '.[]|[.number,.headRefName,.headRefOid[0:7],.mergeStateStatus,([.statusCheckRollup[].conclusion]|unique|join("/"))]|@tsv'; done
   for r in fe be; do git -C projects/jeju-ai/apps/jeju-ai-saas-$r fetch -q origin; \
     git -C projects/jeju-ai/apps/jeju-ai-saas-$r branch -vv; \
     git -C projects/jeju-ai/apps/jeju-ai-saas-$r rev-parse --short origin/develop; done
   kubectl --kubeconfig ops/dev0/talos/_out/kubeconfig -n dev get deploy \
     -o 'custom-columns=NAME:.metadata.name,IMAGE:.spec.template.spec.containers[0].image'
   git status --short; git diff --cached --name-only
   ```

   - PR 체크는 `SUCCESS` 와 `SKIPPED` 만 있으면 정상이다. ci.yml 은 push 실행과 겹치는 pull_request 실행을 일부러 건너뛴다.
   - 이미지 태그는 40자다. 앞 7자로 비교한다.
   - develop 이 바뀌면 Image Updater 가 dev 이미지를 바꾸는 것이 정상이다.
   - 2절과 다른 값이 그 밖에 있으면 그 사이에 사람이나 다른 세션이 움직인 것이다.
3. 결정을 하나씩 받는다.
   - 사용자 규칙대로 하나에 질문 하나다. 옵션 · 추천 · 장단점을 붙여 `AskUserQuestion` 으로 묻고, 결정 목록은 끝날 때까지 체크 표시와 함께 보여 준다.
   - 순서: **D3 첫 질문부터** 다시 묻는다(벡터 타일 방향). 직전 대화에서는 이것을 '5번 결정'이라고 불렀다. 이어서 D2 → D1 → 나머지 표 순서로 묻는다.
   - 사용자가 다른 순서를 원하면 따른다.
4. 결정 없이 할 수 있는 일은 4절에 있다.

## 2. 지금 상태

### 저장소 · 브랜치 (모두 push 됨)

본 체크아웃은 저장소마다 하나다. FE 는 `refactor/set-state-in-effect`, BE 는 `chore/lint-strict` 가 체크아웃돼 있다.

| 저장소 | 브랜치 · HEAD | 열린 PR | 비고 |
| --- | --- | --- | --- |
| FE | `refactor/set-state-in-effect` · `32285fb` | [#15](https://github.com/innopam/jeju-ai-saas-fe/pull/15) | FE #6 리팩터 + 회귀 수정 + strict 린트 병합. 커밋 9개(병합 1) · 파일 45개 |
| FE | `docs/vector-tile-rendering` · `71151a1` | [#16](https://github.com/innopam/jeju-ai-saas-fe/pull/16) | FE-040 평가 메모 |
| FE | `chore/scm-evidence` · `675dfdd` | [#13](https://github.com/innopam/jeju-ai-saas-fe/pull/13) | 형상 증빙(다른 세션 작업) |
| FE | `dependabot/npm_and_yarn/vite-8.3.5` · `4b9af05`(원격만) | [#14](https://github.com/innopam/jeju-ai-saas-fe/pull/14) | vite 8.2.2 → 8.3.5 |
| FE | `chore/lint-strict` · `e574d5c`(로컬만) | 없음 | #15 에 병합됨 |
| BE | `chore/lint-strict` · `ddf5b57` | [#7](https://github.com/innopam/jeju-ai-saas-be/pull/7) | BE #4. develop(certifi) 병합 포함 |
| BE | `perf/k6-p95` · `99f0b41` | [#8](https://github.com/innopam/jeju-ai-saas-be/pull/8) | BE #3. **#7 과 3–5개 파일에서 충돌한다**(결정.md D2) |
| BE | `docs/vector-tile-research` · `93000a5` | [#9](https://github.com/innopam/jeju-ai-saas-be/pull/9) | BE-024 조사 메모 |

- develop
  - FE: `7e3d70a`(10-20).
  - BE: `f015e76`(10-22, PR #6 형상 증빙 + certifi 2026.10.19 병합).
  - BE **로컬** develop 은 `932af51` 로 origin 보다 3커밋 뒤다. 새 브랜치는 `origin/develop` 에서 `--no-track` 으로 딴다.
- 7개 PR 모두 CI 성공(SUCCESS · SKIPPED), 병합 가능 상태(CLEAN). 09:25 검토 때 확인했다.
- 커밋하지 않은 변경: FE · BE 본 체크아웃 모두 없다.
- worktree
  - FE · BE · dev0 와 `.ai-workflow/.worktrees` 에는 없다(10-22 에 정리).
  - ws 의 `.claude/worktrees/*` 3개는 다른 Claude 세션 것이다. 건드리지 않는다.
- 새 worktree 는 `.ai-workflow/.worktrees/<저장소>/<브랜치에서 / 를 - 로>` 에 만든다(ws AGENTS.md 'worktree').

### dev 배포 (`jeju-ai.dev.innopam.net`, dev0 dev 네임스페이스)

- 이미지(09:24 확인)
  - api: `f015e76`. BE develop 이 dev0 `57997f8`(08:34 Image Updater 자동 커밋)로 반영됐다.
  - fe: `7e3d70a`. FE #15 가 병합돼야 바뀐다.
- 스토리지(SeaweedFS 3.97) 메모리 상한
  - 10-22 에 512Mi → 1536Mi 로 올렸다(dev0 `a3ce7e9`).
  - Argo CD Synced · Healthy, 쿼터 limits.memory 1920Mi / 2560Mi.
  - 기록: [dev0 10-22/01](../../../../ops/dev0/docs/history/2026/10/22/01.jeju-ai-saas-storage-memory.md).
- 자동 배포 경로: develop push → ci.yml build-push(GHCR) → Argo CD Image Updater(dev0 main 에 태그 커밋) → dev.
  - dev0 main 은 Image Updater 커밋으로 계속 앞서간다. ws 의 dev0 고정 커밋을 올릴 때는 `git -C ops/dev0 pull --ff-only` 뒤 최신으로 한다.
- 러너는 ARC 최대 2대(`ops/dev0/k8s/arc/runner-values.yaml`)다. 10-22 아침 push 가 몰리자 BE develop build-push 가 08:11 부터 밀렸다.

### ws 저장소

- 브랜치: `docs/md2docx-styled`(origin 에 있음).
- 이 작업의 마지막 ws 커밋은 이 인계 문서를 넣은 커밋이다. `git log -1 --oneline -- .ai-workflow/work/tasks/jeju-ai-고도화` 로 찾는다. 거기에 `ops/dev0` 고정 커밋 `ebe68a0` → `57997f8` 이 같이 들어갔다.
- **섞이면 안 되는 다른 세션 변경이 작업 트리에 있다**(09:45 기준).
  - porthole 서브모듈 추가: `.gitmodules` 와 `projects/porthole` 이 **stage 돼 있다**. 기록은 `docs/history/2026/10/22/06.porthole-submodule.md`(미추적)다.
  - `ops/inbox/`: 등록 안 된 별도 저장소다.
- 그래서 ws 커밋은 반드시 `git commit -m … -- <이 작업의 경로…>` 처럼 경로를 지정해 만든다. 커밋 전에 `git diff --cached --name-only` 로 stage 목록을 확인한다. porthole 의 stage 는 풀지 않는다.

## 3. 오늘까지 한 일

| 날짜 | 한 일 | 기록 |
| --- | --- | --- |
| 10-21 | 결정 없이 할 수 있는 6건을 워크플로로 수행 · 검토 · 반영 | [21/09](../../../../docs/history/2026/10/21/09.jeju-ai-saas-decision-free-tasks.md) |
| 10-22 | FE #6 · BE #4 검토 반영분 커밋(다른 세션) | [22/01](../../../../docs/history/2026/10/22/01.jeju-ai-saas-commit-fe6-be4.md) |
| 10-22 | AGENTS.md 에 worktree 위치 · 규칙 추가 방법 | [22/02](../../../../docs/history/2026/10/22/02.agents-worktree-and-rule-docs.md) |
| 10-22 | 옛 `.worktrees` 4개 커밋 · 정리, FE 린트를 FE #6 에 병합 | [22/03](../../../../docs/history/2026/10/22/03.cleanup-old-worktrees.md) |
| 10-22 | BE PR #6 병합, 브랜치 5개 push · PR, ws 커밋 | [22/04](../../../../docs/history/2026/10/22/04.jeju-ai-saas-pending-decisions.md) |
| 10-22 | `.ai-workflow/work/index.md` 현황 정리 | [22/05](../../../../docs/history/2026/10/22/05.work-index-status.md) |
| 10-22 | ws push, dev0 스토리지 1.5Gi, FE 이슈 #17, 이 인계 문서 | [22/07](../../../../docs/history/2026/10/22/07.jeju-ai-handoff.md) |

### 결과물 위치

PR 이 병합되기 전에는 해당 브랜치에만 있다. 읽을 때는 `git -C <저장소> show origin/<브랜치>:<경로>` 를 쓴다.

| 무엇 | 위치 |
| --- | --- |
| BE #3 k6 측정 메모 · 짝 측정 스크립트 | BE `perf/k6-p95`: `docs/research/k6-p95.md`(§9 러너에서 잴 것), `docs/research/k6-pair.sh` |
| BE-024 벡터 타일 조사 | BE `docs/vector-tile-research`: `docs/research/vector-tiles.md`(§5 제공 경로, §7 FE 질문 14개) + `vector-tiles/` 스크립트 12개 |
| FE-040 렌더링 평가 | FE `docs/vector-tile-rendering`: `docs/research/vector-tile-rendering.md`(§7 BE 질문 답, §8 선택지) + 평가 페이지(`page/modes/jsoncanvas.js` 가 캔버스 렌더러 시제품) · `bench.mjs` |
| 설계(분리 전 계획, 열린 결정 9개) | ws `docs/design/jeju-subsidence-ai/`(05 §4 · §5). 대응 표는 결정.md |
| 작업목록 · 요구사항 · 화면정의서 | `projects/jeju-ai/tasks/`(작업목록), `projects/jeju-ai/tasks/전달/`(받은 원본) |
| 운영(gov-ncloud) 사실 | `ops/gov-ncloud/docs/gov-zone-facts.md`(PostGIS 지원 목록 등) |

- 세션 임시 폴더의 파일은 이 세션이 끝나면 사라진다.
  - 사라지는 것: 대조 결과 JSON, 워크플로 결과, 생성한 타일, SDK 를 거치지 않는 GET 시제품.
  - 필요한 내용은 위 문서 · PR 본문 · 기록에 옮겼다. SDK 우회 시제품 코드는 옮기지 않았다(결정.md D14).
  - 타일은 BE-024 스크립트(`build_tiles.sh`)와 BE 본 체크아웃 `data/`(git 밖 사본)로 다시 만든다.
- 로컬 docker 이미지 `ghcr.io/maplibre/martin:1.16.1`, `protomaps/go-pmtiles:v1.31.2` 가 남아 있다. 타일 재측정용이고 필요 없으면 지운다.

## 4. 결정 없이 할 수 있는 일

모두 사용자 결정은 필요 없다. 다만 커밋 · push · PR · 병합 · 이슈 작성은 사용자 요청이 있어야 하고, 클러스터를 바꾸는 일은 승인을 받는다(5절).

1. **FE-021 화면 안 도움말 · 산정 모델 설명**: 작업목록은 '완료'지만 화면에 없다.
   - 근거: FE `src/components/Header.tsx` 19행 주석(도움말을 뺀 이유), `src/styles/app.css` 2251행 '도움말 팝오버' 절이 비어 있다.
   - 산정 근거 원문은 BE `docs/CSI_산정근거.html · pdf` 다.
   - 화면 문구를 새로 넣는 일이라 범위만 사용자에게 확인하고 시작하는 편이 안전하다.
2. **FE-027 브라우저 확인**: Edge · Safari 근거가 없다. Playwright 는 Chromium 만 돈다.
3. **BE-011 실제 컨테이너 탈출 시험**: 지금 시험은 docker 를 모의로 바꿔 플래그만 본다. 실제 컨테이너에서 네트워크 · DNS · 쓰기 차단과 uid 를 확인한다.
4. **FE `.dockerignore`**: 루트 `node_modules` 만 가린다. PR #16 이 병합되면 `docs/research/vector-tile-rendering/node_modules`(평가 때 약 54MB)가 docker build 문맥에 들어갈 수 있다. `**/node_modules` 로 넓히는 작은 수정이다.
5. **FE #17 준비**: PR #15 병합 뒤 별도 브랜치에서 `noUncheckedIndexedAccess` 를 켠다(오류 126건). BE 쪽 건수는 아직 재지 않았으니 같이 잰다.
6. **CSAP '코드 · 설정 개선 후보' 중 FE · BE 항목을 이슈로 옮긴다.** CSAP 세션과 겹치지 않게 먼저 확인한다.
   - BE `api/src/storage.ts` 기본값(`localhost:8333` · `us-east-1`): 값이 없으면 기동을 멈추게 한다.
   - FE Dockerfile 에 `apk upgrade` 가 없다.
   - api 와 web 의 X-Frame-Options · HSTS 값이 다르다.
   - Fastify 500 응답의 내부 메시지.
   - `/api/openapi.json` 공개 여부.
   - 나머지 셋(XFO · HSTS, 500 메시지, openapi 공개)은 CSAP 문서에서 옮긴 것이고 직접 확인하지 않았다.
7. **브랜치 정리**(원격 삭제는 사용자 승인). 두 저장소 모두 `deleteBranchOnMerge=false` 라 병합해도 브랜치가 남는다.
   - 이미 병합돼 지금 지울 수 있는 것: FE `chore/quality-gates` · `chore/quality-gates-2`, BE `chore/quality-gates` · `chore/quality-gates-2` · `chore/scm-evidence`(로컬 · 원격).
   - PR 병합 뒤: 각 PR 브랜치와 FE `chore/lint-strict`(로컬만).
8. **ws 고정 커밋 갱신**: 서브모듈(FE · BE develop, dev0 main)이 바뀌면 서브모듈을 먼저 push 하고 ws 에 고정 커밋을 올린다.
9. **`../../index.md` 갱신**: PR 병합 · 결정이 생기면 1–4절을 고친다.

승인이 필요해 4절에서 뺀 것

- **DEVOPS-030 모니터링 · 알림**(kube-prometheus-stack, dev0 W48 '보류').
  - 보류 이유('알림 받을 워크로드 없음')는 이제 맞지 않으니 착수를 제안할 만하다.
  - 다만 클러스터 변경이다(메모리 약 1.2–1.5GB, Longhorn PV 10GB). 보류 해제와 설치를 먼저 묻는다.
  - Hubble UI(W58)는 따로 정한다.
- **BE PR #8 러너 측정**: `gh workflow run nightly.yml --ref perf/k6-p95` 은 워크플로 실행이라 승인이 필요하다(결정.md D1-D).

## 5. 지켜야 할 것

- 커밋 · push · PR 생성 · 병합 · 이슈 작성 · 워크플로 실행은 사용자가 요청할 때만 한다. 커밋 메시지에 AI 트레일러를 넣지 않는다.
  - PR · 이슈 본문은 기존 것들처럼 맨 끝에 `🤖 Generated with Claude Code` 링크 줄을 두었다.
- 커밋 메시지 관례
  - FE 는 영어 conventional commits(`refactor(app): …`).
  - BE · dev0 · ws 는 한국어 제목.
  - 병합은 merge commit, BE 는 '… 머지: …' 제목.
- 작업 기록
  - ws `docs/history` 는 두 저장소 이상이 함께 바뀐 일과 ws 자체 변경을 기록한다. 번호는 그날 폴더의 마지막 번호 + 1 이다. 다른 세션이 같은 날 먼저 쓸 수 있으니 쓰기 직전에 다시 본다(10-22 에 06 이 겹쳐 07 로 옮김).
  - 지난 기록은 고치지 않는다. 커밋된 기록에 덧붙일 것은 새 기록에 쓴다.
  - dev0 는 자기 `docs/history` 에 기록한다. FE · BE 에는 기록 규칙이 없다. 대신 PR 본문과 `docs/research` 가 그 역할을 한다.
- 각 저장소 `AGENTS.md` 를 먼저 읽는다. 특히 다음을 지킨다.
  - FE: 시각 회귀 기준 이미지를 함부로 갱신하지 않는다. nginx · CSP 를 바꾸면 `test:e2e:image`.
  - BE: `openapi.json` 은 라우트와 함께. files 라우트는 JSON · GeoJSON 만.
- 포트(로컬 동시 작업 시)
  - FE E2E 4173
  - BE 기본 8333 · 8787, 통합 테스트 18333, 야간 28333 · 28787
  - FE 야간 38080 · 8787
  - 조사용은 19000–19999 를 썼다.
- 클러스터 · dev 환경
  - dev 환경(`*.dev.innopam.net`)에 부하를 걸거나 클러스터를 바꾸는 일은 승인을 받고 한다.
  - 읽기 전용 확인은 `ops/dev0/talos/_out/kubeconfig` 로 한다(기본 kubectl 컨텍스트는 다른 로컬 클러스터 `k3d-gis-local` 이다).
- zsh 에서 셸 변수 이름 `path` 는 PATH 와 묶여 있어 쓰면 안 된다(10-22 에 한 번 겪음).
- BE 원본 GIS 자료 경로는 다른 사람 PC 와 외장 디스크다(`pipeline/gislib.py`: `SRC=/Users/gyuyoung/Downloads/…`, `INSAR_DIR=/Volumes/GeoAI2/…`). 둘 다 이 컴퓨터에 없다(10-22 확인).
  - 그래서 이 컴퓨터에서는 `build_data.py` 로 처음부터 다시 만들 수 없다.
  - 작업용 사본 `data/`(빌드 결과)만 있다. 결정.md D16 을 본다.
