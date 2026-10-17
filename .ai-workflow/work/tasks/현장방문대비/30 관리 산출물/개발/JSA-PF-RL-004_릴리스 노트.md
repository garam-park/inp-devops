# 릴리스 노트

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-RL-004 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 배포·시범적용 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 / 승인자 | 개발팀 / <mark>확인 필요</mark> |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 개발팀 | <mark>확인 필요</mark> |

통합플랫폼의 현재까지 유일한 릴리스(`v0.1.0`)의 노트다. 사용자에게 달라지는 점을 중심으로 적었고, 원본은 저장소의 `RELEASE-NOTES.md` 와 GitHub Release 페이지다. 이후 변경은 JSA-PF-IM-002(체인지로그)의 `[Unreleased]` 에 있다.

## [0.1.0] - 2026-09-17

### 새 기능

- **지도 소스 7종 지원** — `XYZ`·`TMS`·`WMTS`·`TILEJSON`·`WMS`·`ARCGIS_MAPSERVER`·`GEOJSON`. 워크스페이스 안에서 소스(연결)와 레이어(화면에 얹히는 것)를 나눠 관리하며, 종류별 입력값은 서버가 검증한다.
- **타일 프록시 4종** — TMS·TileJSON·WMTS·ArcGIS MapServer. 브라우저가 외부 타일 서버를 직접 부르지 않고 서버가 대신 받아 오므로, 네 종류 모두 같은 경로를 지나며 요청 직전에 사설·루프백·링크로컬 주소(SSRF)로 향하는 요청을 거부하고 리다이렉트를 따라가지 않는다. 인증키는 서버가 암호화해 보관하고 요청에만 실어 보내며 브라우저에는 노출하지 않는다. 차단 범위의 남은 한계는 '알려진 이슈'를 본다.
- **WMTS Capabilities 조회** — WMTS 소스 등록을 돕는 조회 기능(등록값은 직접 입력이 기준).
- **지도 소스 등록 화면** — 소스 종류에 따라 입력 폼이 바뀌고, 등록한 레이어가 지도에 렌더링된다.

### 개선

- **배포 보안 강화** — 마이그레이션 이미지가 빌드 시점에 의존성을 포함하므로 마이그레이션 Job 은 실행 중 외부(인터넷)에서 패키지를 내려받지 않는다(DB·DNS 접속만 한다). NetworkPolicy 를 켜는 환경 values(local·dev·prod)에서는 Job 에 외부 443 을 여는 허용 규칙이 기본으로 꺼져 있어(`networkPolicy.migrationPackageDownload.enabled: false`) 외부 443 이 막힌다. chart 기본값(`values.yaml`)은 NetworkPolicy 자체가 꺼져 있어 이 차단이 없고, 차단 동작은 로컬 k3s 에서만 실측했다(2026-09-16).

### 수정

- Helm 차트 결함 3건 — Secret 을 chart 가 만들도록 보완, customer·admin 의 JWT 서명키 Secret 분리, 비활성 단위(타일 프록시·ETL 수신)로 향하던 Ingress 규칙을 해당 단위(`tileProxy.enabled`·`ingestApi.enabled`)를 켰을 때만 만들도록 변경.
- NetworkPolicy 의 DNS 허용 규칙이 모든 파드의 외부 통신을 53 으로 제한하던 결함 수정.

### 호환성에 영향을 주는 변경

- **레이어의 `wms_layer_name` 이 `options`(jsonb) 안으로 이동했다.** 기존 WMS 레이어의 값은 마이그레이션이 옮기며, 이전 필드는 남아 있지 않다. 레이어 API 를 직접 호출하는 클라이언트는 `options.wms_layer_name` 을 사용해야 한다.

### 알려진 이슈

저장소 기록 기준(2026-10-16)이다.

- 사내 개발 클러스터(`dev0`)는 구축되어 있으나 통합플랫폼은 아직 배포하지 않았다. `values-dev.yaml` 이 이 클러스터에 맞춰지지 않았고(Ingress 클래스는 `nginx` 인데 클러스터는 Cilium 내장 Ingress 인 `cilium`) 이미지·Secret·DB 호스트·NetworkPolicy 대상이 비어 있어 렌더가 실패하며, 사내 개발 DB 위치와 GHCR 이미지 pull 자격 주입 방법도 정해지지 않았다. 운영 후보(NCP 공공기관용)는 Ingress 방식·관리형 DB 대역 등 환경 정보가 정해지지 않아(공공 콘솔 실측 5건이 승인 조건) `values-prod.yaml` 도 같은 방식으로 렌더가 실패하므로 배포할 수 없다. 로컬 k3s(k3d)에는 v0.1.0 시점 chart 로 첫 설치를 배포·검증했다.
- 배포 실행 자동화(클러스터에 `helm upgrade` 를 실행할 배포용 러너와 배포 워크플로, T089)가 없다. CI·이미지 빌드에 쓰는 조직 self-hosted runner 는 이미지 게시까지만 하고 배포는 하지 않는다. 배포는 `helm upgrade --install` 을 사람이 실행한다.
- 세세부1·2 산출물 수신(ETL)은 메타데이터 등록 골격까지만 구현되어 있다. 실데이터 적재 어댑터는 세세부1·2 측 확인 5건(파일 형식·좌표계, 1회 용량·갱신 주기, 전달 방식, 격자 체계, 인증·인가 경계)에 대한 회신이 아직 없어 만들지 않았다. 질의 발송 기록은 저장소에 없다 <mark>확인 필요</mark>.
- 타일 프록시와 ETL 수신은 별도 이미지 없이 customer API 안에서 동작한다(chart 의 분리 단위는 기본 비활성).
- 타일 프록시의 요청 조립·자원 방어 보강이 남아 있다(T100, 미착수). 주소 차단은 사설·루프백·링크로컬·멀티캐스트 대역이며 `100.64.0.0/10`·`198.18.0.0/15` 와 IPv4 를 품은 IPv6 대역(NAT64·6to4 등)은 막지 않는다(코드 점검 결과, 실제 요청으로 확인하지는 않았다). 요청 직전에 주소를 해석해 검사하지만 검사한 주소로 연결을 고정하지는 않아 DNS 재바인딩 방어가 없다. 설계서 9장 §9.2 #11 은 이 영역을 '미흡'으로 판정했다.
- chart 는 외부 소스 인증키의 암호화 키(`MAP_SECRET_KEY`)와 인증 쿠키의 `Secure` 속성(`AUTH_COOKIE_SECURE`)을 주입하지 않는다. 앞의 것은 비워 두면 앱의 개발용 고정 기본값이 쓰일 수 있고, 뒤의 것은 기본값이 `false` 라 TLS 를 종단하는 환경에서도 쿠키에 `Secure` 가 붙지 않을 수 있다(저장소 점검 결과, 클러스터 실측 아님). 쿠키 쪽은 설계서 9장 #14 가 같은 점을 지적한다.
- 보안 갭 분석(설계서 9장)의 "미흡·부분" 항목 중 일부는 CSAP 기준이 확정된 뒤에 처리가 정해진다. 로그 보존 기간은 M011 의 T077~T080 이 소관으로 정해져 있고, 서비스 간 TLS 는 아직 어떤 Task 범위에도 없어 M011 판정 뒤 보완 여부부터 정한다. v0.1.0 이후 수정된 항목은 JSA-PF-IM-002 를 참조한다.
- **릴리스 노트 정정** — 원본(`RELEASE-NOTES.md`·GitHub Release)에는 `main`·`develop` 의 branch protection 을 `PR 필수 · squash OFF · rebase OFF · merge commit ON · 1 approval` 으로 잠근다고 적혀 있으나, 조직 플랜(GitHub Free)과 private 저장소 조건 때문에 branch protection·ruleset 을 쓸 수 없어(API 403) 적용되지 않았다. 이 사실은 릴리스 PR(#37) 본문에 2026-09-17 에 이미 적혀 있었으나 원본에는 반영되지 않았고, 2026-09-26 T096 에서 다시 확인해 `docs/rules/git/branch.md` 에 기록했다. 현재는 저장소 병합 옵션(merge commit 만 허용)과 `lint-git` 사후 검출로 squash·rebase 병합만 대신 막는다(T096). PR 경유는 규칙(`docs/rules/workflow/pull-request.md`)으로만 두어 시스템이 강제하지 않고, 승인자 수는 규정이 없다(셀프 리뷰).
- **v0.1.0 태그의 chart 는 아래 '업그레이드 안내'의 동작과 다르다** — 마이그레이션 Job 이름이 고정이고 인자 없이 실행되어 이미지 기본값인 `migrate --seed` 가 돈다(`migrate.seed` 값이 없어 끌 수 없다). 그래서 이미지 태그(또는 digest)를 바꿔 다시 `helm upgrade` 하면 Job 의 `spec.template` 을 바꿀 수 없어 `field is immutable` 로 실패하고(코드와 Kubernetes 규칙에서 도출한 것으로 재현하지는 않았다), 이 Job 이 실행될 때마다(설치, 또는 Job 을 지우고 다시 배포할 때) 개발용 계정·조직·지도 데모 데이터가 들어가며 바꾼 비밀번호가 되돌아간다. 스키마가 앞선 상태에서 롤백하면 `wait-for-migration` 이 '=' 로 비교해 롤백한 파드가 `Init` 에서 멈춘다. 수정은 v0.1.0 이후 `develop` 에만 반영되어 있고(T105, #55) `main`·릴리스에는 아직 없다.

### 업그레이드 안내

이 절의 마이그레이션 Job·시드 안내는 v0.1.0 태그가 아니라 2026-10-16 `develop`(gis-sass 4e37ab6)의 chart 와 `deploy/README.md` §3.4 를 따른 것이다. 마이그레이션 Job 이름에 리비전을 붙이고(`-r<리비전>`) 명령을 `migrate --force` 로 고정하며 시드를 기본으로 끈 변경은 v0.1.0 이후 T105(#55, 2026-09-27 KST 병합)에서 들어갔고 아직 릴리스되지 않았다(JSA-PF-IM-002 `[Unreleased]`). 렌더 검사(helm lint·template·kubeconform)와 마이그레이션 이미지 단독 실행까지만 했고 클러스터에서 `helm upgrade` 를 실행한 기록은 저장소에 없다(실측은 T089 로 이관). v0.1.0 태그와 다른 점은 '알려진 이슈'에 적었다.

- 업그레이드는 설치와 같은 `helm upgrade --install gis charts/gis -f <환경 values> …` 이며, 이미지 태그(또는 digest)와 시크릿 4종을 함께 준다. 절차는 JSA-PF-RL-002(배포 런북)를 따른다.
- (develop 기준) 업그레이드마다 마이그레이션 Job 이 리비전이 붙은 새 이름으로 만들어진다. 새 api 파드는 새 마이그레이션이 있으면 `wait-for-migration` 이 적용을 확인할 때까지 대기한다(v0.1.0 도 같다). 그동안 이전 파드가 트래픽을 받으므로 마이그레이션은 이전 코드와 호환되게(컬럼 추가 → 코드 배포 → 옛 컬럼 제거) 작성한다. 새 마이그레이션이 없는 배포에서는 두 버전 모두 Job 이 끝나기 전에도 통과한다. 롤백(DB 의 적용 수가 이미지의 마이그레이션 수보다 많은 경우)은 develop 이 '적용 수 ≥ 기대 수'로 판정해 통과하지만, v0.1.0 은 '=' 로 비교하므로 통과하지 못한다(알려진 이슈 참조).
- `wms_layer_name` 이관은 마이그레이션이 자동 수행한다. develop chart 에서는 시드(`migrate.seed`)가 기본으로 꺼져 있으며 개발·운영 배포에서 켜지 않는다(알려진 계정이 만들어지고 바뀐 비밀번호가 되돌아간다). v0.1.0 chart 에는 이 값이 없고 시드가 항상 실행된다(알려진 이슈 참조).
- 롤백은 JSA-PF-RL-003 을 따른다. `helm rollback` 은 스키마를 되돌리지 않으므로 스키마까지 되돌려야 하면 `migrate:rollback` 을 사람이 판단해 실행한다.

## 근거 자료

- `RELEASE-NOTES.md`, `VERSION`, `deploy/README.md` §3.4·§8, `docs/01.개발/APIs/customer/ingest/README.md` (gis-sass 저장소)
- `docs/rules/git/branch.md`(branch protection 사용 불가 기록)
