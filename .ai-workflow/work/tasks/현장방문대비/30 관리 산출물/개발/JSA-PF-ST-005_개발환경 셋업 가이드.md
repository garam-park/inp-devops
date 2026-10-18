# 개발환경 셋업 가이드

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-ST-005 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 표준·환경 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 / 승인자 | 개발팀 / <mark>확인 필요</mark> |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 개발팀 | <mark>확인 필요</mark> |

이 문서는 통합플랫폼 저장소(`gis-sass`)의 개발·테스트 환경을 만드는 절차다. 제주 지반침하 프로토타입(`Jeju-subsidence-AI`)은 참조 기준 자료이며 통합플랫폼 빌드와 무관하므로 별도 절(3.2)에서 실행 방법만 적는다.

## 1. 사전 준비

| 항목 | 버전 | 설치 방법 |
| --- | --- | --- |
| Git | 최신 | OS 패키지 관리자 |
| Node.js | 24 (LTS) | `mise install` — 저장소 루트 `mise.toml` 이 24 로 고정 |
| JDK | 25 (Temurin) | 호스트에 별도 설치(mise 는 Node 만 고정). 확인: `java -version` |
| Gradle | 9.7 | 설치 불필요 — 각 API 디렉터리의 `./gradlew` 사용 |
| Docker, Docker Compose | 최신 | Docker Desktop · colima · podman 등. Docker Engine 29 이상은 5절 참고 |
| PostgreSQL + PostGIS | `postgis/postgis:16-3.4` | compose 가 컨테이너로 기동(호스트 설치 불필요) |
| curl, jq | — | smoke 스크립트(`scripts/smoke-*.sh`) 실행용 |
| Python | 3 | 문서 링크 검사(`scripts/check-doc-links.py`) 실행용 |
| Dagger CLI | v0.21.9 | 선택 — CI 와 같은 컨테이너에서 로컬 사전 검증할 때(`dagger/README.md`) |
| helm, kubectl, k3d | — | 선택 — 로컬 k3s 배포 검증용(JSA-PF-RL-002 참조) |

마이그레이션·시드는 PHP(Laravel) 컨테이너가 실행하므로 호스트에 PHP·Composer 를 설치할 필요가 없다.

## 2. 저장소 받기

```bash
git clone git@github.com:innopam/gis-sass.git
cd gis-sass
git switch develop
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

### 3.2 참조 프로토타입(Jeju-subsidence-AI, 선택)

프로토타입은 별도 백엔드(API) 서버 없이 정적 데이터로 동작하는 React 지도 화면이다(개발 서버 기본 포트 5178). 화면용 데이터(`app/public/data`)가 저장소에 포함되어 있어 원본 GIS 자료 없이 바로 실행할 수 있다. 배경지도는 선택 사항이다. 브이월드 인증키(`app/.env.local` 의 `VITE_VWORLD_KEY`, 견본은 `app/.env.example`)를 넣은 경우에만 브라우저가 외부(`api.vworld.kr`)에서 타일을 받고, 키가 없으면 배경지도 없이 열린다. 아래 명령은 `Jeju-subsidence-AI` 저장소 루트에서 실행한다.

```bash
npm --prefix app install
npm --prefix app run dev
```

원본 GIS 자료를 다시 받아 값을 고칠 때만 데이터 변환 단계가 필요하다(원본 자료는 저장소에 없고 경로는 `tools/gislib.py` 위쪽에 모아 두었다. 이 경로는 개발자 개인 PC 의 절대 경로이므로 본인 환경에 맞게 고친 뒤 실행한다).

```bash
python3 -m venv .venv && ./.venv/bin/pip install pyshp pyproj shapely openpyxl
./.venv/bin/python tools/build_data.py
```

## 4. 동작 확인

- 개발 스택 상태: `docker compose ps -a` 에서 db 가 healthy 이고 migrate·migrate-admin 이 `Exited (0)` 으로 끝난 뒤 api·api-admin·web·web-admin 이 실행 중(`Up`)이어야 한다. `-a` 가 없으면 종료된 migrate 컨테이너는 목록에 나오지 않는다.
- 화면: customer web `http://localhost:15173`, admin web `http://localhost:15174` 에서 로그인 화면이 열린다.
- API 상태: customer API 관리 포트에서 확인한다(서비스 포트에서는 `/actuator/**` 가 `404001` 이다).

  ```bash
  curl -fsS http://localhost:8081/actuator/health   # {"groups":["liveness","readiness"],"status":"UP"}  (status 가 UP 이면 정상)
  ```

- 인증 smoke(12 시나리오, 현재 기준 38 PASS): `API_BASE=http://localhost:18080/api scripts/smoke-auth.sh` — 종료 코드 0 이면 모두 통과.
- 테스트(영역별 명령은 `docs/TESTING.md` 가 단일 출처):

  | 영역 | 명령 |
  | --- | --- |
  | 마크다운 린트 | `npm run lint:md` |
  | 문서 링크 | `python3 scripts/check-doc-links.py` |
  | 백엔드 단위(제품) | `cd apps/customer/api && ./gradlew :gis-api:test` |
  | 백엔드 통합(제품) | `cd apps/customer/api && ./gradlew :gis-api:integrationTest` (Docker 필요) |
  | 백엔드 단위(공유) | `cd packages/api-core && ./gradlew test` |
  | web 단위 | `npm test -w @inp-gis/customer-web` (admin 은 `-w @inp-gis/admin-web`) |

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

## 6. 근거 자료

- `AGENTS.md` §2(기술 스택·포트), `docs/TESTING.md`, `docker-compose.yml`, `docker-compose.test.yml`, `mise.toml`, `package.json`, `scripts/README.md` (gis-sass 저장소)
- `README.md`(실행 절), `app/src/data/constants.js`(배경지도), `app/.env.example` (Jeju-subsidence-AI 저장소)
