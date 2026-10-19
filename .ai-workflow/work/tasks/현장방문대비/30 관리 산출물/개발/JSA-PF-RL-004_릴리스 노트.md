# 릴리스 노트

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-RL-004 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 | 박가람 |
| 승인자 | - |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 박가람 | - |

통합플랫폼 릴리스 `v0.1.0` 의 노트다. 사용자에게 달라지는 점을 중심으로 적었고, 원본은 저장소의 `RELEASE-NOTES.md` 와 GitHub Release 페이지다. 이후 변경은 JSA-PF-IM-002(체인지로그)의 `[Unreleased]` 에 있다.

## [0.1.0] - 2026-09-17

### 새 기능

- **지도 소스 7종 지원** — `XYZ`·`TMS`·`WMTS`·`TILEJSON`·`WMS`·`ARCGIS_MAPSERVER`·`GEOJSON`. 워크스페이스 안에서 소스(연결)와 레이어(화면에 얹히는 것)를 나눠 관리하며, 종류별 입력값은 서버가 검증한다.
- **타일 프록시 4종** — TMS·TileJSON·WMTS·ArcGIS MapServer. 브라우저가 외부 타일 서버를 직접 부르지 않고 서버가 대신 받아 오므로, 네 종류 모두 같은 경로를 지나며 요청 직전에 사설·루프백·링크로컬 주소(SSRF)로 향하는 요청을 거부하고 리다이렉트를 따라가지 않는다. 인증키는 서버가 암호화해 보관하고 요청에만 실어 보내며 브라우저에는 노출하지 않는다.
- **WMTS Capabilities 조회** — WMTS 소스 등록을 돕는 조회 기능(등록값은 직접 입력이 기준).
- **지도 소스 등록 화면** — 소스 종류에 따라 입력 폼이 바뀌고, 등록한 레이어가 지도에 렌더링된다.

### 개선

- **배포 보안 강화** — 마이그레이션 이미지가 빌드 시점에 의존성을 포함하므로 마이그레이션 Job 은 실행 중 외부(인터넷)에서 패키지를 내려받지 않는다(DB·DNS 접속만 한다). NetworkPolicy 를 켜는 환경 values(local·dev·prod)에서는 Job 에 외부 443 을 여는 허용 규칙이 기본으로 꺼져 있어(`networkPolicy.migrationPackageDownload.enabled: false`) 외부 443 이 막힌다.

### 수정

- Helm 차트 결함 3건 — Secret 을 chart 가 만들도록 보완, customer·admin 의 JWT 서명키 Secret 분리, 비활성 단위(타일 프록시·ETL 수신)로 향하던 Ingress 규칙을 해당 단위(`tileProxy.enabled`·`ingestApi.enabled`)를 켰을 때만 만들도록 변경.
- NetworkPolicy 의 DNS 허용 규칙이 모든 파드의 외부 통신을 53 으로 제한하던 결함 수정.

### 호환성에 영향을 주는 변경

- **레이어의 `wms_layer_name` 이 `options`(jsonb) 안으로 이동했다.** 기존 WMS 레이어의 값은 마이그레이션이 옮기며, 이전 필드는 남아 있지 않다. 레이어 API 를 직접 호출하는 클라이언트는 `options.wms_layer_name` 을 사용해야 한다.

### 알려진 이슈

- 세세부1·2 산출물 수신(ETL)은 메타데이터 등록을 제공한다. 실데이터 적재 어댑터는 세세부1·2 측과 5개 항목(파일 형식·좌표계, 1회 용량·갱신 주기, 전달 방식, 격자 체계, 인증·인가 경계)이 정해진 뒤 만든다.
- 타일 프록시와 ETL 수신은 별도 이미지 없이 customer API 안에서 동작한다(chart 의 분리 단위는 기본 비활성).
- 배포는 `helm upgrade --install` 을 사람이 실행한다(JSA-PF-RL-002).

### 업그레이드 안내

- 업그레이드는 설치와 같은 `helm upgrade --install gis charts/gis -f <환경 values> …` 이며, 이미지 태그(또는 digest)와 시크릿 4종을 함께 준다. 절차는 JSA-PF-RL-002(배포 런북)를 따른다.
- 새 api 파드는 새 마이그레이션이 있으면 `wait-for-migration` 이 적용을 확인할 때까지 대기한다. 그동안 이전 파드가 트래픽을 받으므로 마이그레이션은 이전 코드와 호환되게(컬럼 추가 → 코드 배포 → 옛 컬럼 제거) 작성한다.
- `wms_layer_name` 이관은 마이그레이션이 자동 수행한다.
- 롤백은 JSA-PF-RL-003 을 따른다. `helm rollback` 은 스키마를 되돌리지 않으므로 스키마까지 되돌려야 하면 `migrate:rollback` 을 사람이 판단해 실행한다.

## 근거 자료

- `RELEASE-NOTES.md`, `VERSION`, `deploy/README.md` §3.4, `docs/01.개발/APIs/customer/ingest/README.md` (gis-sass 저장소)
