# Git 브랜치 커밋 규칙

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-ST-002 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 표준·환경 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 | 박가람 |
| 승인자 | - |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 박가람 | - |

## 1. 브랜치 전략

Git Flow 를 쓴다(규칙 상태: 확정, 2026-07-26).

| 브랜치 | 역할 | 분기 → 병합 대상 |
| --- | --- | --- |
| main | 배포된 안정 버전만. 릴리스 태그(`vX.Y.Z`)는 main 에서만 붙인다 | `release/*`·`hotfix/*` → main (`--no-ff`) |
| develop | 다음 릴리스 개발 통합. 기본 브랜치 | 작업 브랜치 → develop (PR) |
| `feat/*` | 기능 개발 | develop → develop |
| `fix/*` | develop 의 버그 수정 | develop → develop |
| `refactor/*` · `perf/*` · `test/*` · `docs/*` · `style/*` · `chore/*` | 동작 변화 없는 구조 개선 · 성능 개선 · 테스트 · 문서 · 포맷팅 · 빌드·의존성·설정 | develop → develop |
| `release/*` | 릴리스 준비(버전 반영, QA). 수정은 release 브랜치에서 | develop → main + develop |
| `hotfix/*` | 배포본 긴급 수정 | main → main + develop |

릴리스 기준은 `vX.Y.Z` 태그다. 운영 배포는 main 의 `vX.Y.Z` 태그, 개발 클러스터 배포는 develop 병합이 기준이다(ADR-2026-08-11.03).

작업 브랜치는 최신 기준 브랜치 위로 rebase 해 이력을 선형으로 유지한다. 다른 사람과 함께 쓰는 브랜치는 rebase 하지 않고 기준 브랜치의 변경을 merge 로 가져온다.

## 2. 브랜치 이름

`타입/설명` (설명은 kebab-case). 타입은 커밋 타입과 같은 어휘를 쓰고, `release/*`·`hotfix/*` 는 배포 흐름을 나타내는 관리 브랜치다.

```text
feat/order-cancel
fix/token-expiry
docs/install-guide
release/1.2.0
hotfix/payment-timeout
```

작업 브랜치는 설명 앞에 작업 일자를 붙이는 관례가 있다(예: `docs/20261016/weekly-report-10w2`).

## 3. 커밋 메시지 형식

Conventional Commits 를 따른다. **타입은 영어, 제목·본문은 한국어**로 쓴다.

```text
타입(범위): 제목

본문(왜 바꿨는지)
```

| 타입 | 의미 |
| --- | --- |
| feat | 기능 추가·변경 |
| fix | 버그 수정 |
| refactor | 동작 변화 없는 구조 개선 |
| perf | 성능 개선 |
| test | 테스트 추가·수정 |
| docs | 문서만 변경 |
| style | 포맷팅 등 코드 의미에 영향 없는 변경 |
| chore | 빌드·의존성·설정 등 그 외 잡무 |

- 범위(스코프)는 선택이며 변경 영역을 좁힐 때만 쓴다(`fix(auth): …`).
- 제목은 50자 이내, 마침표 없이, "~추가·~수정·~제거" 같은 명사형으로 끝낸다.
- 본문에는 "왜"(이유·배경·트레이드오프)를 적는다. 자명한 변경이면 생략한다.
- 깨지는 변경(breaking change)은 타입 뒤에 `!` 를 붙이고 본문에 `BREAKING CHANGE:` 로 내용을 적는다(예: `feat(map)!: 레이어 wms_layer_name 이관`).
- GitHub 가 PR 병합 때 만드는 `Merge pull request #…` 커밋은 이 형식의 예외이며 기본 메시지를 유지한다.
- 커밋 하나에는 하나의 논리적 변경만 담고, 기계적 변경(이름 변경·포맷팅·파일 이동)은 동작 변경과 분리한다. `WIP`·`fixup!` 커밋은 병합 전에 정리한다.

## 4. Pull Request 규칙

- 제목·본문 양식: 제목은 커밋 메시지와 같은 Conventional Commits 형식이다. 본문은 JSA-PF-ST-003 1절을 따른다.
- 모든 머지는 PR 을 거치는 것이 규칙이다(혼자 작업해도 마찬가지). 한 PR 은 한 가지 목적만 갖고, 리팩토링과 기능 변경을 섞지 않는다. 크기는 "한 번의 셀프 리뷰 세션에서 전부 이해하고 검증할 수 있는 단위"를 기준으로 한다.
- 리뷰어 수: 규칙 문서는 **셀프 리뷰**(diff 를 처음부터 끝까지 다시 읽기)를 머지 조건으로 정한다.
- 머지 조건(CI 통과 등): 규칙 문서는 ① CI 통과 ② 셀프 리뷰를 조건으로 정한다. CI(`.github/workflows/test.yml` — 테스트, 마크다운 린트·문서 링크 검사, 의존성 점검, 이미지 빌드, 차트·마이그레이션 검증)는 PR 과 `develop`·`main` push(및 `v*` 태그)마다 자동 실행된다.
- 머지 방식: 보호 브랜치(`main`·`develop`)로는 fast-forward 없이 **merge commit(`--no-ff`)** 만 쓴다. 작업 단위의 경계가 이력에 남고, 문제가 생기면 merge 커밋 하나를 revert 해 작업 단위로 되돌릴 수 있기 때문이다.

## 5. 금지 사항

- `main`·`develop`·`release/*`·`hotfix/*` 에 직접 push 하지 않는다(PR 경유).
- 보호 브랜치(`main`·`develop`·`release/*`·`hotfix/*`)의 이력을 재작성하지 않는다. force push 는 본인만 쓰는 작업 브랜치에서 `--force-with-lease` 로만 허용하고 `--force` 는 쓰지 않는다.
- 다른 사람과 공유하는 브랜치는 rebase 하지 않는다.
- squash merge 와 rebase merge 를 쓰지 않는다. 새로 들어오는 병합에 대해 두 겹으로 강제한다.
  1. 저장소 설정에서 `Allow merge commits` 만 켜고 squash·rebase 병합은 끈다.
  2. `develop`·`main` push 마다 `lint-git` 워크플로가 `scripts/check-merge-shape.sh` 로 그 push 로 새로 들어온 first-parent 범위에서 GitHub 가 만든(committer `noreply@github.com`) 부모 1개 커밋을 찾아 실패시킨다(사후 검출).
- `main`·`develop` 에 반영된 변경은 reset 으로 지우지 않고 revert 한다. 병합된 PR 전체를 취소할 때는 merge 커밋을 revert 한다.
- 평문 비밀값(운영 키·비밀번호·토큰)은 저장소에 커밋하지 않는다. chart 는 평문 Secret 을 두지 않고(`deploy/README.md` 5절), 개발·운영은 암호문(SealedSecret)만 커밋하기로 했으며(ADR-2026-09-26.01), `.env`·`.env.test` 는 `.gitignore` 대상이다. 개발·테스트 전용 기본값(`docker-compose.yml`, `application.yml`, `.env.test.example`, 시드 계정)은 '운영 사용 금지'로 표시해 커밋되어 있다.

## 6. 버전·릴리스

- 버전은 SemVer(`MAJOR.MINOR.PATCH`)이며 커밋 타입과 연결된다(`!` → MAJOR, `feat` → MINOR, `fix` → PATCH).
- 릴리스 절차: `develop` 에서 `release/x.y.z` 분기 → 버전 반영·점검 → `main` 으로 `--no-ff` 병합 후 `vx.y.z` 태그 → `develop` 에도 병합. hotfix 도 같은 방식이다.
- 첫 릴리스 `v0.1.0` 은 2026-09-17 에 발행했다(태그와 GitHub Release). 버전의 기준은 저장소 루트 `VERSION` 파일이며 API 빌드(`apps/customer/api`·`apps/admin/api` 의 `build.gradle.kts`)가 이 값을 읽는다. Helm chart 의 `Chart.yaml` `version`·`appVersion` 은 릴리스 때 같은 값으로 맞추고(`deploy/charts/gis/README.md`), 이미지의 `vX.Y.Z` 태그는 푸시한 Git 태그에서 만들어진다(`build-push.yml`).

## 7. 근거 자료

- `docs/rules/git/branch.md`, `commit-message.md`, `commit.md` (gis-sass 저장소, 2026-07-26 확정)
- `docs/rules/workflow/pull-request.md`, `release.md` (gis-sass 저장소)
- `.github/workflows/lint-git.yml`, `scripts/check-merge-shape.sh` (gis-sass 저장소)
