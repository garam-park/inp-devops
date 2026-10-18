# 지반침하 스마트관리 시스템 — 프로토타입을 제품으로: FE/BE 분리 설계안

- 기준일: 2026-10-17
- 대상: [`projects/Jeju-subsidence-AI`](../../../projects/Jeju-subsidence-AI/) (서브모듈, 커밋 `129d660`)
- 읽는 사람: 이 제품을 FE/BE 로 나눠 구현할 개발자
- 상태: 초안. **코드는 바꾸지 않았다.** 결정이 필요한 항목은 [05 §4](05.migration-plan.md#4-열린-결정)에 모았다.

## 합의한 전제

이 문서를 쓰기 전에 정한 것이다. 바뀌면 문서도 바뀐다.

| 항목 | 결정 |
|---|---|
| 오브젝트 스토리지로 옮길 "파일 쓰기" | **전부** — 배치 산출 데이터, 사용자가 올리는 사고이력 엑셀, 내보내기 결과(GeoJSON·CSV·XLSX·PDF, 그리고 지금 잠겨 있는 SHP·GeoTIFF) |
| BE 스택 | **Node.js + TypeScript** |
| 문서 위치 | 이 폴더 (`ws` 저장소 `docs/design/jeju-subsidence-ai/`) |
| 가정 | 스토리지는 S3 호환 API(개발은 MinIO, 운영은 미정). 배포는 `ops/dev0`. 사용자 상태(조회 이력·감사·권한·사고 기록)는 DB. SSO·권한 집행·감사 저장은 BE 책임으로 두되 상세 설계는 하지 않는다. Python GIS 파이프라인은 유지 vs TS 포팅 두 안을 비교한다 |

## 한 장 요약

**지금.** 백엔드가 없는 정적 SPA 다. Python 배치가 개발자 PC 에서 312MB 의 레이어 파일을 만들어 git 에 넣고, React 앱이 그대로 받아 그린다.
권한·감사·사고 기록·조회 이력은 브라우저 localStorage 에만 있다. 채점 공식은 Python 과 JS 에 두 벌 있다.

**문제.** (1) 코드와 자료의 버전이 어긋나 있다 — 저장소의 데이터에는 코드가 더 이상 만들지 않는 필드가 있고, README 와 `model.json` 의 격자 수가 다르다.
(2) 권한이 집행되지 않고 감사 증적이 없다 — 관로 같은 "중요 시설물 정보"도 URL 만 알면 받을 수 있다. (3) 자료 갱신이 특정 PC 와 외부 지오코딩에 묶여 있다.
(4) 사용자 상태가 공유되지 않아 사람마다 다른 알림을 본다. (5) 비밀키가 번들에 들어가고 빌드가 외부 CDN 에 기댄다. 자세한 근거는 [01 §7](01.current-state.md#7-제품화-관점에서-본-문제).

**목표.** 실행 단위 3개 + 저장소 2개.

| 단위 | 기술 | 책임 |
|---|---|---|
| web | React 19 + TS, nginx | 화면. 자료는 전부 api 에서 |
| api | Node.js 24 + TS, Fastify | 유일한 진입점. 인증·권한·감사, 조회, 내보내기 생성, 업로드, 번들 파일 중계, 작업 등록, 번들 → DB 가져오기 |
| pipeline | Python 3.12 (지금 `tools/`) | 원본 → 데이터셋 번들. 작업 표 폴링. SHP·GeoTIFF 변환 |
| PostgreSQL + PostGIS | | 사용자·권한·감사·사고 기록·데이터셋 버전·작업·내보내기·기간별 점수. (2단계) 격자·관로 |
| 오브젝트 스토리지 | S3 호환 | `raw/` 원본, `datasets/{버전}/` 불변 번들, `exports/` 결과, `incidents/uploads/` 엑셀 원본 |

**핵심 설계 결정 다섯.**

1. **데이터셋 버전 번들** — 파이프라인 한 번 실행 = 불변 번들 하나(`manifest.json` + `model.json` + 레이어). 화면은 항상 같은 버전의 모델과 자료를 본다. 드리프트가 구조적으로 사라진다. ([04 §2](04.data-and-storage.md#2-데이터셋-번들-규약))
2. **모든 파일은 api 를 거친다** — 번들 파일 중계가 레이어 권한을 검사하고(`pipes`·`excavation` 은 민감), 불변이라 1년 캐시. 브라우저는 스토리지를 모른다. ([04 §1](04.data-and-storage.md#1-오브젝트-스토리지))
3. **기간별 CSI 는 사전 계산** — 후보 × 기간 조합 28개를 파이프라인이 미리 계산해 번들에 넣는다. `scoring.js` 와 JS 쪽 등급 경계 복제가 사라지고 보고서가 재현된다. ([04 §4](04.data-and-storage.md#4-기간별-채점--사전-계산을-추천))
4. **Python 파이프라인 유지, DB 작업 표로 연결** — api 와 pipeline 은 서로 부르지 않는다. `jobs` 표와 스토리지 번들이 유일한 접점. 관리자가 화면에서 원본 올리기 → 빌드 → 검토 → 활성화. ([04 §3](04.data-and-storage.md#3-동적-파이프라인--작업-표와-워커))
5. **내보내기는 서버가 만들고 보관한다** — 같은 조회 쿼리로 생성, `exports/` 에 저장, 감사 기록과 연결. SHP·GeoTIFF 잠금 해제. ([04 §7](04.data-and-storage.md#7-내보내기))

**모듈.** `apps/web`, `apps/api`, `apps/pipeline`, `packages/contracts`(API 스키마·번들 규약), `packages/domain`(등급·레이어·역할·사고 필드).
모델 상수는 `model.yaml` → 번들 `model.json` 한 곳. 지금 파일 하나하나가 어디로 가는지는 [03 §7](03.modules.md#7-현재-파일--목표-위치).

**전환.** 6단계. 매 단계 끝에 동작하는 제품이 있고, 자료(1단계) → 사용자 상태(2) → 내보내기(3) → 동적 파이프라인·사전 계산(4) → 공간 질의(5) → 제품화 마무리(6) 순서다. ([05 §2](05.migration-plan.md#2-단계))

## 문서 구성

| 문서 | 내용 | 읽는 데 |
|---|---|---|
| [01. 현황 분석](01.current-state.md) | 지금 구조, 데이터 흐름, 파일 쓰는 지점 11곳 전수, 코드에 표시된 서버 접합점, 지켜야 할 것, 문제 8가지 | 15분 |
| [02. 목표 아키텍처](02.target-architecture.md) | C4 — System Context, Container, Component(api·web·pipeline), Deployment(dev0·운영), 주요 흐름 4개(시퀀스), 기술 선택표 | 20분 |
| [03. 모듈 분해](03.modules.md) | 저장소 레이아웃, 의존 방향 규칙, 공유 패키지, web·api·pipeline 내부 구조, 상태 재배치표, **현재 파일 → 목표 위치 매핑**, 상수 단일 출처 | 15분 |
| [04. 데이터·스토리지·API](04.data-and-storage.md) | 버킷·키·수명, 번들 manifest, 작업 표·워커, 기간별 채점 두 안, DB 스키마, 공간 질의, 내보내기, 사고·권한·감사·인증, API 초안 30개, 캐시, 보안 체크리스트 | 25분 |
| [05. 전환 단계](05.migration-plan.md) | 원칙, 0–6단계(목표·작업·완료 조건·되돌리기), 리스크 9개, 열린 결정 9개, 측정해야 할 수치 | 10분 |

## 그림

문서 안의 Mermaid 가 원본이고(GitHub·VS Code 에서 바로 보인다), 보고서·발표에 붙이기 위해 PNG 로도 두었다.

| 파일 | 어디 그림인가 |
|---|---|
| `images/01-current-state.png` | 01 §1 지금 구조 |
| `images/02-1-system-context.png` | 02 §1 System Context |
| `images/02-2-container.png` | 02 §2 Container |
| `images/02-3-1-api-components.png` | 02 §3.1 api Component |
| `images/02-3-2-web-components.png` | 02 §3.2 web Component |
| `images/02-3-3-pipeline-components.png` | 02 §3.3 pipeline Component |
| `images/02-4-deployment-dev0.png` | 02 §4.1 Deployment (dev0) |
| `images/02-5-1-flow-dataset-refresh.png` | 02 §5.1 자료 갱신 흐름 |
| `images/02-5-2-flow-query.png` | 02 §5.2 조회 흐름 |
| `images/02-5-3-flow-export.png` | 02 §5.3 내보내기 흐름 |
| `images/02-5-4-flow-incident-import.png` | 02 §5.4 사고 엑셀 올리기 |
| `images/03-dependencies.png` | 03 §2 의존 방향 |

### 그림 다시 만들기

Mermaid 블록을 고친 뒤 아래처럼 다시 그린다. Chrome 이 설치된 Mac 기준이다(`puppeteer.json` 에 Chrome 경로).

```bash
cat > /tmp/puppeteer.json <<'EOF'
{"executablePath":"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","args":["--no-sandbox"]}
EOF
# 블록 하나를 diagram.mmd 로 저장한 뒤
PUPPETEER_SKIP_DOWNLOAD=1 npx -y -p @mermaid-js/mermaid-cli@11.4.2 mmdc \
  -p /tmp/puppeteer.json -i diagram.mmd -o images/<이름>.png -w 1400 -s 2 -b white
```

표기법은 dev0 의 [k8s-c4.md](../../../ops/dev0/docs/architecture/k8s-c4.md) 와 같다. Mermaid 전용 C4 문법(`C4Context` 등)은 선 라벨이 겹쳐 쓰지 않는다.

## 함께 볼 것

- 자매 제품 [gis-sass `AGENTS.md`](../../../projects/gis-sass/AGENTS.md) — `apps/*` + `packages/*` 배치, chart 구조, web-core 의 인증·API 클라이언트 패턴을 이 설계가 따른다. 단 gis-sass 의 BE 는 Java/Spring 이라 `api-core` 는 공유하지 않는다.
- dev0 [k8s-c4.md](../../../ops/dev0/docs/architecture/k8s-c4.md) — 배포 대상 클러스터의 구조(Cilium Ingress, Longhorn, 네임스페이스 쿼터).
- ws [AGENTS.md](../../../AGENTS.md) — 제품 배포 설정은 클러스터 저장소(`ops/dev0/apps/<제품>/`)에, 차트·이미지는 게시된 버전으로.
