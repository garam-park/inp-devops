# 체인지로그

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-IM-002 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 기능 구현 현황 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 | 박가람 |
| 승인자 | - |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 박가람 | - |

대상은 통합플랫폼 저장소(`gis-sass`)다. 형식은 Keep a Changelog 를 따르고 최신 버전이 맨 위에 온다. 기준은 `develop` 브랜치 2026-10-16 시점이다. 항목 끝의 `#N` 은 PR 번호이고, PR 없이 반영된 항목은 `#N` 대신 커밋 해시를 적는다.

## [Unreleased]

### Added

- 보호 브랜치 머지 형태 가드 — squash·rebase 병합을 사후 검출하는 `lint-git` 워크플로와 `scripts/check-merge-shape.sh` (#44)
- CI 배포물 검증 잡 — 마이그레이션 왕복(`migrate-roundtrip`), 이미지 빌드(`image-build`), 차트 검증(`chart`: helm lint·template·kubeconform). 이미지 푸시는 자동 실행(develop push·`v*` 태그)에서 모든 테스트·검증 잡이 통과한 뒤에만 이뤄진다 (#67)
- Helm 차트 파드 보안 컨텍스트 기본 적용 — 렌더 결과를 PSA `restricted` 필드 기준으로 정적 검사해 워크로드 9종(기본 비활성 3종 포함) 위반 0건 (#55)
- Playwright e2e 시나리오 — 두 탭이 동시에 access 토큰을 잃어도 옛 refresh 쿠키를 재사용하지 않는지 확인 (커밋 87732ac)
- CI Actions 실행 진단 스크립트 (#64)

### Changed

- CI 러너를 조직 self-hosted runner 로 전환 (#57)
- web 공통화 — 로그인·404 페이지와 테스트 설정을 `web-core` 로 이동 (#50)
- 개발·로컬 실행 기본 포트 조정 — admin API 8080·8081 → 8082·8083, admin web(vite) 5173 → 5174 로 바꿔 `AGENTS.md` 포트 표에 맞추고 customer 와 동시에 띄울 수 있게 했다. vite 포트(`VITE_PORT`)와 API 서버 포트(`SERVER_PORT`)는 환경변수로 바꿀 수 있다. 배포 chart 는 #55 에서 컨테이너 포트를 8080·8081 로 고정한다 (#36)
- 개발 의존성 상향 — vite 6·coverage 4(#76), tailwindcss 4·daisyUI 5 와 전이 의존성 override(#78). `npm audit` 개발 의존성 취약점 21건(critical 3·high 9) → 5건(critical 0), 런타임 의존성은 전후 0건

### Fixed

- 인증 경로 보강 — refresh 회전·로그인 실패 카운트의 동시성(원자화), `X-Forwarded-For` 위조로 인한 rate limit 우회 차단, rate limit 맵 만료 청소와 크기 상한 (#56)
- 타일 프록시 — 응답 하드닝(Content-Type 허용 목록 등, #52), 벡터 타일 경로의 `octet-stream` 응답 허용 회귀 수정(#70), 소스 인증 비밀의 오리진 밖 전송 차단(#66)
- 지도 화면 — 로딩 중 변경 누락과 레이어 순서 미반영 수정(#68), 레이어 낙관적 갱신 경합 수정(#51), WMTS 주소 변경 뒤 이전 조회 결과 숨김
- customer API 동시성·예외 매핑 — 마지막 OWNER 검사에 조직 행 잠금 추가, 이름 유니크 위반을 409 로 변환, 프레임워크 4xx 예외의 응답 매핑 (#53)
- web 인증 흐름 — 탭 사이 refresh 를 Web Locks 로 단일화(#69), 세션 만료·로그아웃 실패 시 정리, 로그인 리다이렉트의 해시 보존(#50)
- ETL 수신 메타데이터 — 버전 전환·동시 등록·version 조회 결함 (#46), 산출물 유형 길이 상한 검증 (#49)
- Helm 차트 — 마이그레이션 Job 의 시드 실행·업그레이드 결함 수정 (#55)
- API 이미지 빌드에 `VERSION` 파일 복사 누락 (#58)

### Security

- 위 인증·타일 프록시 수정과 Helm 차트 수정은 보안 갭 분석(설계서 9장 §9.2)의 판정 항목을 보완한 것이다. 보완한 항목은 인증 방어의 우회 내성, 외부 콘텐츠의 오리진 격리(응답 쪽), 배포 기본 보안 설정, 비밀 관리의 사용 경로 유출이다.
- npm 개발 의존성의 알려진 취약점 21건 중 16건(critical 3건 전부)을 해소했다. 런타임 의존성은 전후 0건이다(위 Changed 참조).

## [0.1.0] - 2026-09-17

첫 릴리스. `main` 브랜치를 새로 만들고 `vX.Y.Z` 태그를 처음 발행했으며, 버전의 기준을 저장소 루트 `VERSION` 파일로 두었다(#37). 원본은 저장소의 `RELEASE-NOTES.md` 다.

### Added

- 지도 소스 7종 모델 — `XYZ`·`TMS`·`WMTS`·`TILEJSON`·`WMS`·`ARCGIS_MAPSERVER`·`GEOJSON` 과 종류별 `options` 검증기 (#25)
- 타일 프록시 4종 — TMS·TileJSON(#28), WMTS 와 Capabilities 조회(#27), ArcGIS MapServer(#26). 브라우저가 외부 타일을 직접 부르지 않고 서버가 대신 받으며, 4종 모두 같은 프록시 경로로 요청 직전 SSRF 검사(사설·루프백·링크로컬 대역 거부)와 리다이렉트 금지를 적용하고, 인증키는 서버에 보관해 상대 요청에만 붙이고 응답에는 싣지 않는다
- web 등록 폼의 소스 종류별 분기와 지도 렌더링 (#29)
- 마이그레이션 이미지에 vendor 포함과 마이그레이션 Job 의 외부 접속(egress) 차단 (#34)

### Changed

- 레이어 `wms_layer_name` 을 `options`(jsonb)로 이관 — **깨지는 변경**(`!`). 기존 WMS 레이어의 컬럼 기반 파라미터가 jsonb 로 옮겨졌다 (#23)

### Fixed

- Helm 차트 결함 3건 — Secret 템플릿 신설, customer·admin JWT Secret 분리, 비활성 단위로 가는 Ingress 규칙을 해당 단위가 켜졌을 때만 렌더(가드) (#12)
- NetworkPolicy DNS egress 가 모든 파드의 egress 를 53 으로 제한하던 결함 — 대상 파드를 chart 파드로 좁혀 수정, k3d 에서 마이그레이션 Job `Complete` 재현 검증 (#24)

v0.1.0 이전의 개발 이력(인증·권한·지도 등)은 릴리스 전이라 항목화하지 않았고, Git 이력과 작업 문서(`planning/archive`)에 남아 있다. 지도 소스 3종→7종 확장의 기능 변경은 위 [0.1.0] 항목에 있다.

## 참고 — 제주 지반침하 프로토타입 저장소 이력

프로토타입(`Jeju-subsidence-AI`)은 통합플랫폼 변경 관리 대상이 아니라 **참조 기준 자료**다. 현재 단계는 프로토타입 분석 및 통합플랫폼과의 결합 방식 검토다. 프로토타입 저장소의 커밋은 4개다.

| 날짜 | 커밋 | 내용 |
| --- | --- | --- |
| 2026-09-17 | 1cccc44 | 지반침하 스마트관리 시스템 최초 커밋 |
| 2026-10-14 | 638aa02 | 제주 전용으로 정리, 근거 없는 지표 삭제 |
| 2026-10-14 | 5e4063f | 산출 데이터를 저장소에 포함 |
| 2026-10-14 | 129d660 | 아이콘 SVG 에서 Figma 내보내기 찌꺼기 제거 |

## 근거 자료

- `RELEASE-NOTES.md`, `VERSION`, Git 이력(`v0.1.0..develop`), 병합 PR 목록(GitHub) (gis-sass 저장소)
- `planning/milestones/`(코드 품질·보안 개선 작업), `docs/TESTING.md`
- Git 이력 (Jeju-subsidence-AI 저장소)
