# 개발환경 셋업 가이드

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-ST-005 |
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

이 문서는 통합플랫폼 저장소(`gis-sass`)와 제주 지반침하 SaaS 저장소(서버 `jeju-ai-saas-be`, 화면 `jeju-ai-saas-fe`)의 개발·테스트 환경을 만드는 절차다. 세 저장소는 서로 빌드 의존이 없어 각각 받아 띄운다. SaaS 화면은 자료를 모두 SaaS 서버 API 에서 받으므로 서버를 먼저 띄운다. 제주 지반침하 프로토타입(`Jeju-subsidence-AI`)은 참조 기준 자료이며 빌드와 무관하므로 별도 절(3.4)에서 실행 방법만 적는다.

## 1. 사전 준비

| 항목 | 버전 | 대상 | 설치 방법 |
| --- | --- | --- | --- |
| Git | 최신 | 공통 | OS 패키지 관리자 |
| mise | 최신 | 공통 | OS 패키지 관리자. 세 저장소 모두 루트 `mise.toml` 이 도구 버전을 고정한다. `gis-sass` 는 Node 만, SaaS 저장소 두 개는 린트·보안 검사 도구(lefthook, gitleaks, actionlint, hadolint 등)까지 mise 가 받는다 |
| Node.js | 24 (LTS) | 공통 | `mise install` — `gis-sass`·`jeju-ai-saas-fe` 는 `24`, `jeju-ai-saas-be` 는 `24.22.0` 으로 고정 |
| JDK | 25 (Temurin) | `gis-sass` | 호스트에 별도 설치(mise 는 Node 만 고정). 확인: `java -version` |
| Gradle | 9.7 | `gis-sass` | 설치 불필요 — 각 API 디렉터리의 `./gradlew` 사용 |
| Docker, Docker Compose | 최신 | 공통 | Docker Desktop · colima · podman 등. Docker Engine 29 이상은 5절 참고. `jeju-ai-saas-be` 는 스토리지·지수 레이어 실행기·통합 테스트에, `jeju-ai-saas-fe` 는 운영 이미지 빌드와 리눅스 E2E 에만 쓴다 |
| PostgreSQL + PostGIS | `postgis/postgis:16-3.4` | `gis-sass` | compose 가 컨테이너로 기동(호스트 설치 불필요) |
| SeaweedFS (S3 호환 스토리지) | `chrislusf/seaweedfs:3.97` | `jeju-ai-saas-be` | compose 가 컨테이너로 기동(호스트 설치 불필요) |
| curl, jq | — | `gis-sass`, `jeju-ai-saas-be` | smoke 스크립트(`scripts/smoke-*.sh`)와 API 동작 확인용. jq 는 smoke 스크립트만 쓴다 |
| Python | 3 | `gis-sass` | 문서 링크 검사(`scripts/check-doc-links.py`) 실행용 |
| Python | 3.12 | `jeju-ai-saas-be` | `mise install` — `mise.toml` 이 `3.12.15` 로 고정하고 `.venv` 를 만든다(파이프라인·지수 실행기). 파이프라인 의존성(`pipeline/requirements.txt`)은 `mise run pipeline:install` |
| lefthook | 2.2.2 | `jeju-ai-saas-be`, `jeju-ai-saas-fe` | `mise install` 로 받는다. 커밋 훅 설치는 처음 한 번 `mise exec -- lefthook install` |
| Chromium (Playwright) | `@playwright/test` 가 요구하는 버전 | `jeju-ai-saas-fe` | `npm ci` 뒤 `npx playwright install chromium` — E2E 용. 리눅스 공식 이미지로 돌리면(`mise run test:e2e:docker`) 호스트 설치 불필요 |
| Dagger CLI | v0.21.9 | `gis-sass` | 선택 — CI 와 같은 컨테이너에서 로컬 사전 검증할 때(`dagger/README.md`) |
| helm, kubectl, k3d | — | `gis-sass` | 선택 — 로컬 k3s 배포 검증용(JSA-PF-RL-002 참조) |

마이그레이션·시드는 PHP(Laravel) 컨테이너가 실행하므로 호스트에 PHP·Composer 를 설치할 필요가 없다.

## 2. 저장소 받기

```bash
git clone git@github.com:innopam/gis-sass.git
cd gis-sass
git switch develop
```

SaaS 저장소 두 개는 기본 브랜치가 `develop` 이라 clone 만 하면 된다. 서로 독립이라 둘 다 받거나 필요한 쪽만 받는다.

```bash
git clone git@github.com:innopam/jeju-ai-saas-be.git
git clone git@github.com:innopam/jeju-ai-saas-fe.git
```

## 3. 설치·실행

### 3.1 통합플랫폼(gis-sass)

```bash
# 도구 버전 고정 (Node 24)
mise install

# 의존성 설치 — npm 워크스페이스(customer web · admin web · web-core). 호스트에서 web 테스트와 마크다운 린트(npm run lint:md)를 돌릴 때 필요
npm ci

# 개발 스택 기동 — db → migrate(마이그레이션·시드) → api + web
docker compose up -d
docker compose logs -f api web
```

- 개발 스택은 `docker-compose.yml` 이 정의한다(db, migrate, migrate-admin, api, api-admin, web, web-admin). api 는 소스 저장 시 자동 재시작하고, web 은 HMR 로 즉시 반영된다.
- JWT 서명키는 지정하지 않으면 개발 전용 기본값이 쓰인다(운영 사용 금지). 바꾸려면 루트 `.env`(git 추적 안 함)에 `AUTH_JWT_SIGNING_KEY` 를 둔다.
- 포트의 기준표는 저장소 `AGENTS.md` 의 "포트"다. 개발 compose 기준 customer web 15173, admin web 15174, customer api 18080(관리 포트 8081), admin api 8082(관리 포트 8083), db 5432 다.
- 종료: `docker compose down`(볼륨 유지). DB 와 캐시까지 지우려면 `-v` 를 붙인다. DB 구성이 바뀐 뒤에는 기존 볼륨을 버려야 한다(초기화 스크립트는 컨테이너 첫 기동에서만 실행).
- 시드 계정은 마이그레이션 시더가 만든다(customer `admin`·`guest`·`lockout`, admin `sysop`). 비밀번호는 시더 소스를 따르며, 개발·운영 배포에서는 시드를 끄는 것이 기본이다(`migrate.seed=false`).

테스트 스택(개발 스택과 볼륨·네트워크·포트가 분리되어 동시에 띄울 수 있다):

```bash
# 테스트 compose 는 AUTH_JWT_SIGNING_KEY 가 없으면 up·down·run·ps 가 모두 실패한다. 셸에 export 해 둔다.
export AUTH_JWT_SIGNING_KEY=$(openssl rand -hex 32)
docker compose -f docker-compose.test.yml up --abort-on-container-exit
docker compose -f docker-compose.test.yml down -v
```

- 테스트 스택의 api 서비스는 `AUTH_JWT_SIGNING_KEY`(32바이트 이상)를 필수로 요구하고 기본값이 없다(개발 스택과 다르다). compose 가 파일을 읽을 때 검사하므로 `down -v`·`ps`·`run` 과 5절의 단계별 명령도 키가 없으면 `required variable AUTH_JWT_SIGNING_KEY is missing a value` 로 실패한다. 명령 앞에 `KEY=... docker compose ...` 로 붙인 값은 그 명령 하나에만 적용된다. 새 셸에서도 쓰려면 루트 `.env`(git 추적 안 함)에 한 번 둔다.

### 3.2 지반침하 SaaS 서버(jeju-ai-saas-be)

저장소는 두 부분이다. `api/`(Node.js 24 + TypeScript, Fastify)는 오브젝트 스토리지(S3 호환)에 둔 레이어 자료를 화면에 중계하고, `pipeline/`(Python 3.12)은 원본 GIS 를 레이어로 바꾸는 변환과 지수 레이어 실행을 맡는다. 로컬 스토리지는 compose 가 띄우는 SeaweedFS 다. 레이어 자료는 git 에 없고 스토리지가 원본이므로 처음 한 번 자료를 올려야 화면에 무언가 보인다. 아래 명령은 저장소 루트에서 실행한다.

```bash
# 도구 설치와 커밋 훅 (처음 한 번). mise.toml 이 Node 24.22.0 · Python 3.12.15 와 검사 도구를 고정하고 .venv 를 만든다
mise trust && mise install && mise exec -- lefthook install

# 로컬 설정 — 스토리지 자격 증명(로컬 전용 값)과 포트. docker compose 와 api 가 함께 읽는다
cp .env.example .env

# 스토리지 기동(S3 localhost:8333) 후 API 의존성 설치
docker compose up -d storage
npm --prefix api ci

# 처음 한 번: 레이어 자료 올리기 — 프로토타입 저장소의 app/public/data 를 올린다(폴더의 orgs/ 아래만 올라간다)
npm --prefix api run storage -- push <프로토타입 저장소>/app/public/data

# API 기동 (localhost:8787, 소스 저장 시 자동 재시작)
npm --prefix api run dev
```

- `docker compose up -d` 로 api 까지 컨테이너(`api/Dockerfile`)로 띄울 수도 있다. 이때 api 는 compose 네트워크의 `storage:8333` 을 본다.
- 프로토타입 자료 없이 띄우려면 합성 자료(조직 1·워크스페이스 1·레이어 4)를 만들어 올린다: `npm --prefix api run seed:fixtures -- <폴더>` 뒤 같은 폴더를 `npm --prefix api run storage -- push <폴더>`.
- 스토리지 자격 증명 `S3_ACCESS_KEY`·`S3_SECRET_KEY` 는 기본값이 없어 `.env` 가 없으면 api 가 시작하지 못한다. `.env` 는 git 추적 안 함. 브이월드 키(`VWORLD_KEY`)는 굴착 허가 지번 지오코딩에만 쓰고 비워 둬도 된다.
- 올린 자료를 둘러보는 화면: 파일러 `http://127.0.0.1:8888`(버킷 `jeju-ai-saas` 의 `orgs/`), 마스터 `http://127.0.0.1:9333`. 인증이 없어 이 컴퓨터에서만 열린다.
- 파이프라인(원본 GIS 를 다시 받아 값을 고칠 때만): `mise run pipeline:install` 로 의존성(`pipeline/requirements.txt`)을 `.venv` 에 넣은 뒤 `npm --prefix api run storage -- pull data` → `python3 pipeline/build_data.py`(원본 자료 경로는 `pipeline/gislib.py`) → `python3 pipeline/run_index.py jeju/csi`(지수 레이어 실행, Docker 필요) → `npm --prefix api run storage -- push data`(바뀐 파일만 올린다) 순서다. `.venv` 는 `mise exec --`·`mise run` 에서 활성화된다. 지수 실행기와 단위 테스트는 표준 라이브러리만 써서 의존성 설치 없이 돈다.
- 종료: `docker compose down`(볼륨 `storage` 유지, 올린 자료 보존). `-v` 를 붙이면 자료가 지워져 다시 올려야 한다.

### 3.3 지반침하 SaaS 화면(jeju-ai-saas-fe)

React 19 + TypeScript(strict) + Vite + Leaflet 화면이다. 자료는 모두 SaaS 서버 API 에서 받으므로 3.2 의 서버(8787)가 떠 있어야 화면이 뜬다. 개발 서버는 `/api` 요청을 서버로 넘겨 CORS 를 피한다. 아래 명령은 저장소 루트에서 실행한다.

```bash
# 도구 설치와 커밋 훅 (처음 한 번). mise.toml 이 Node 24 와 검사 도구를 고정한다
mise trust && mise install && mise exec -- lefthook install

# 로컬 설정 — 브이월드 키(VITE_VWORLD_KEY)와 서버 주소(API_PROXY_TARGET, 비우면 http://localhost:8787)
cp .env.example .env.local

# 의존성 설치, 개발 서버 기동 (http://localhost:5178, HMR)
npm ci
npm run dev

# E2E 브라우저 (처음 한 번, npm ci 뒤)
npx playwright install chromium
```

- 브이월드 키는 등록한 서비스 URL 에서만 동작하므로 개발용은 `http://localhost:5178` 로 발급한다(절차는 `.env.example`). 키가 비어 있으면 배경지도 없이(격자만) 뜨고 국외 공개 타일로 대체하지 않는다. `.env.local` 은 git 추적 안 함.
- 서버의 라우트 스키마가 바뀌면 `npm run gen:api` 로 `src/api/schema.d.ts` 를 다시 만든다(서버가 떠 있어야 하며 주소는 `API_SCHEMA_URL`, 기본 `http://localhost:8787/api/openapi.json`). 이 파일은 손으로 고치지 않는다.
- 운영 이미지(nginx)는 `docker build --build-arg VITE_VWORLD_KEY=… -t jeju-ai-saas-fe .` 로 만들고 `docker run -e API_UPSTREAM=http://<서버>:8787 -p 8080:8080 jeju-ai-saas-fe` 로 띄운다. 키는 빌드 때 번들에 들어간다.

### 3.4 참조 프로토타입(Jeju-subsidence-AI, 선택)

프로토타입은 별도 백엔드(API) 서버 없이 정적 데이터로 동작하는 React 지도 화면이다(개발 서버 기본 포트 5178). 화면용 데이터(`app/public/data`)가 저장소에 포함되어 있어 원본 GIS 자료 없이 바로 실행할 수 있다. 배경지도는 선택 사항이다. 브이월드 인증키(`app/.env.local` 의 `VITE_VWORLD_KEY`, 견본은 `app/.env.example`)를 넣은 경우에만 브라우저가 외부(`api.vworld.kr`)에서 타일을 받고, 키가 없으면 배경지도 없이 열린다. 아래 명령은 `Jeju-subsidence-AI` 저장소 루트에서 실행한다.

```bash
npm --prefix app install
npm --prefix app run dev
```

원본 GIS 자료를 다시 받아 값을 고칠 때만 데이터 변환 단계가 필요하다(원본 자료 경로는 `tools/gislib.py` 위쪽에 모아 두었으니 본인 환경에 맞게 고친 뒤 실행한다).

```bash
python3 -m venv .venv && ./.venv/bin/pip install pyshp pyproj shapely openpyxl
./.venv/bin/python tools/build_data.py
```

## 4. 동작 확인

### 4.1 통합플랫폼(gis-sass)

- 개발 스택 상태: `docker compose ps -a` 에서 db 가 healthy 이고 migrate·migrate-admin 이 `Exited (0)` 으로 끝난 뒤 api·api-admin·web·web-admin 이 실행 중(`Up`)이어야 한다. `-a` 가 없으면 종료된 migrate 컨테이너는 목록에 나오지 않는다.
- 화면: customer web `http://localhost:15173`, admin web `http://localhost:15174` 에서 로그인 화면이 열린다.
- API 상태: customer API 관리 포트에서 확인한다(서비스 포트에서는 `/actuator/**` 가 `404001` 이다).

  ```bash
  curl -fsS http://localhost:8081/actuator/health   # {"groups":["liveness","readiness"],"status":"UP"}  (status 가 UP 이면 정상)
  ```

- 인증 smoke(12 시나리오, 38 개 검사): `API_BASE=http://localhost:18080/api scripts/smoke-auth.sh` — 종료 코드 0 이면 모두 통과.
- 테스트(영역별 명령은 `docs/TESTING.md` 가 단일 출처):

  | 영역 | 명령 |
  | --- | --- |
  | 마크다운 린트 | `npm run lint:md` |
  | 문서 링크 | `python3 scripts/check-doc-links.py` |
  | 백엔드 단위(제품) | `cd apps/customer/api && ./gradlew :gis-api:test` |
  | 백엔드 통합(제품) | `cd apps/customer/api && ./gradlew :gis-api:integrationTest` (Docker 필요) |
  | 백엔드 단위(공유) | `cd packages/api-core && ./gradlew test` |
  | web 단위 | `npm test -w @inp-gis/customer-web` (admin 은 `-w @inp-gis/admin-web`) |

### 4.2 지반침하 SaaS 서버(jeju-ai-saas-be)

- 스토리지 상태: `docker compose ps` 에서 storage 가 healthy 여야 한다.
- API: `curl -fsS http://localhost:8787/api/catalog` 가 조직·워크스페이스·레이어 목록을 돌려주고, 올린 레이어가 목록에 보여야 한다(스토리지를 훑어 만들며 10초 캐시). 계약은 `curl -fsS http://localhost:8787/api/openapi.json`.
- 테스트(영역별 명령은 `mise.toml` 의 작업이 단일 출처. `mise run ci` 가 CI 와 같은 순서로 전부 돈다):

  | 영역 | 명령 |
  | --- | --- |
  | API 타입 검사 | `mise run typecheck` (= `npm --prefix api run typecheck`) |
  | API 단위(메모리 버킷, 스토리지 불필요, 커버리지 하한 70%) | `mise run test:api` (= `npm --prefix api test`) |
  | API 통합(실제 SeaweedFS, Docker 필요) | `mise run test:integration` — 전용 compose 프로젝트·버킷(`jeju-ai-saas-test`, `127.0.0.1:18333`)을 띄우고 지우므로 개발 스토리지는 건드리지 않는다 |
  | 지수 실행기 단위(Docker 불필요) | `mise run test:pipeline` (= `python3 -m unittest discover -s pipeline/tests`) |
  | OpenAPI 계약(라우트 스키마와 `openapi.json` 일치) | `mise run openapi:check` |
  | 린트 전체 | `mise run lint` |

### 4.3 지반침하 SaaS 화면(jeju-ai-saas-fe)

- 화면: `http://localhost:5178` 에서 지도가 열리고 레이어 패널에 서버에 올린 레이어가 보여야 한다. 브이월드 키가 없으면 배경지도 없이 격자만 보이는 것이 정상이다.
- 테스트(`mise run ci` 가 CI 와 같은 순서로 전부 돈다):

  | 영역 | 명령 |
  | --- | --- |
  | 타입 검사 | `npm run typecheck` |
  | 단위·컴포넌트(Vitest + jsdom) | `npm test` (커버리지 하한 70% 검사는 `npm run test:coverage`) |
  | E2E(Playwright, 서버 없이 합성 자료) | `npm run test:e2e` — 운영 번들을 빌드해 preview(`127.0.0.1:4173`)를 직접 띄운다. 시각 회귀는 리눅스에서만 비교하므로 전체는 `mise run test:e2e:docker` |
  | 린트 전체 | `mise run lint` |

## 5. 자주 겪는 문제

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| 컨테이너를 다시 띄웠는데 예전 DB 구성으로 동작한다 | DB 초기화 스크립트는 컨테이너 첫 기동에서만 실행된다 | `docker compose down -v` 후 다시 기동 |
| 통합 테스트 전부가 `DockerClientProviderStrategy` 초기화에서 실패(`client version 1.32 is too old`) | Docker Engine 29 이상은 API 1.40 미만을 거부하는데 docker-java 가 낮은 버전을 쓴다 | 홈 디렉터리 `~/.docker-java.properties` 에 `api.version=1.44` 한 줄을 넣는다 |
| Apple Silicon 에서 api 가 DB 에 처음 붙을 때 DNS 오류 | `linux/amd64` 이미지가 QEMU 로 느리게 떠서 생기는 race | 먼저 `export AUTH_JWT_SIGNING_KEY=$(openssl rand -hex 32)`(또는 루트 `.env` 에 키를 둔다) 한 뒤 단계별로 기동: `docker compose -f docker-compose.test.yml up -d db` → `run --rm migrate` → `up -d api` → `up smoke` |
| smoke 스크립트가 시작부터 실패 | 공유 `/tmp` 에 다른 사용자가 남긴 파일을 sticky bit 때문에 지우지 못한다 | `TMPDIR=$(mktemp -d) scripts/smoke-auth.sh` |
| api 코드를 고쳤는데 e2e 결과가 예전 그대로다 | compose 는 이미지가 있으면 다시 빌드하지 않는다 | `--build` 를 붙여 실행(`docker compose -f docker-compose.test.yml --profile e2e up --build …`) |
| 호스트의 8080 포트 충돌 | 다른 개발 서버가 8080 을 사용 | 개발 compose 의 customer api 는 호스트 18080 을 쓰도록 되어 있다. 호스트 직접 실행 시 포트는 `AGENTS.md` 표 참고 |
| 빌드 스크립트를 고쳤는데 api 가 반영되지 않는다 | `build.gradle.kts`·`libs.versions.toml` 변경은 자동 재시작 대상이 아니다 | `docker compose restart api` |
| SaaS 서버 api 가 시작하자마자 `환경변수 S3_ACCESS_KEY 가 없습니다` 로 멈춘다 | 루트 `.env` 가 없다. 스토리지 자격 증명은 기본값이 없다 | `cp .env.example .env` 뒤 다시 기동 |
| SaaS 서버에 레이어를 올렸는데 카탈로그·화면에 없다 | `storage push` 는 폴더의 `orgs/` 아래만 올리고, 카탈로그는 10초 캐시다 | 폴더 구조가 `orgs/{org}/layers/{layer}/manifest.json` 인지 확인하고 10초 뒤 다시 조회 |
| SaaS 서버 통합 테스트가 "개발·운영 버킷으로 돌리지 않는다" 오류로 멈춘다 | 환경에 `S3_BUCKET=jeju-ai-saas` 가 들어 있다(테스트는 끝나면 버킷의 `orgs/` 를 지우므로 막는다) | `mise run test:integration` 으로 돌린다(전용 버킷 `jeju-ai-saas-test`) |
| SaaS 화면이 비어 있고 `/api` 요청이 실패한다 | 서버(8787)가 떠 있지 않거나 `.env.local` 의 `API_PROXY_TARGET` 이 다른 주소다 | 3.2 의 서버를 먼저 띄우고 `curl localhost:8787/api/catalog` 로 확인 |
| SaaS 화면 또는 프로토타입이 `localhost:5179` 로 뜬다 | 둘 다 개발 서버 기본 포트가 5178 이라 먼저 뜬 쪽이 차지한다. 5179 는 브이월드 키의 등록 URL 과 달라 배경지도가 빠진다 | 둘 중 하나만 띄운다 |
| SaaS 화면 E2E 가 `Executable doesn't exist` 로 실패한다 | Playwright 브라우저를 받지 않았다 | `npx playwright install chromium` |
| SaaS 화면 E2E 의 시각 회귀(`visual.spec`)가 macOS 에서 건너뛴다 | 기준 이미지는 리눅스에서만 만들고 비교한다 | `mise run test:e2e:docker`(공식 Playwright 리눅스 이미지). 기준 갱신은 `mise run test:e2e:docker -- --update-snapshots` |

## 6. 근거 자료

- `AGENTS.md` §2(기술 스택·포트), `docs/TESTING.md`, `docker-compose.yml`, `docker-compose.test.yml`, `mise.toml`, `package.json`, `scripts/README.md` (gis-sass 저장소)
- `README.md`(실행·파이프라인), `AGENTS.md`(검증), `docker-compose.yml`, `docker-compose.test.yml`, `.env.example`, `mise.toml`, `lefthook.yml`, `api/package.json`, `api/src/storage.ts`, `pipeline/pyproject.toml` (jeju-ai-saas-be 저장소)
- `README.md`(실행·테스트·배포), `AGENTS.md`(검증), `.env.example`, `mise.toml`, `lefthook.yml`, `package.json`, `vite.config.ts`, `playwright.config.ts`, `vitest.config.ts`, `Dockerfile` (jeju-ai-saas-fe 저장소)
- `README.md`(실행 절), `app/src/data/constants.js`(배경지도), `app/.env.example` (Jeju-subsidence-AI 저장소)
