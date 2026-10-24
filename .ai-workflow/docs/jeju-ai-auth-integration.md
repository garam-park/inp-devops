# jeju-ai 인증 · 서버 저장 통합 지점

- 대상: `projects/jeju-ai/apps/jeju-ai-saas-fe`(화면) · `projects/jeju-ai/apps/jeju-ai-saas-be`(서버)
- 상태: **아직 붙지 않았다.** 화면의 권한 · 기록은 전부 브라우저(localStorage)다.
- 이 문서의 목적: 붙일 때 손댈 곳을 한 곳에 모으는 것이다. **결정을 해도 코드는 여기만 보면 된다.**

## 지금의 상태

| 저장소 | 파일 | 브라우저에 있는 것 | 문제 |
| --- | --- | --- | --- |
| FE | `src/lib/perms.ts` | 역할별 권한 설정 (`subsidence.perms.v2`) | 브라우저 저장소를 고치면 권한이 바뀐다 |
| FE | `src/lib/incidents.ts` | 담당자가 쓴 사고 기록 (`subsidence.incidents.v1`) | 이 기기에서만 보인다 — 부서 간 공유 불가 |
| FE | `src/lib/runHistory.ts` | 직전 조회 이력 (`subsidence.runs.v1`) | 사람마다 '직전 조회 대비' 결과가 다르다 |
| FE | `src/lib/audit.ts` | 감사 기록 (`subsidence.audit.v1`, 최근 2000건) | 사용자가 지울 수 있다 — CSAP 증적으로 인정받지 못한다 |
| FE | `src/App.tsx` | 접속자 (`USER` 상수 — 홍길동/사회재난과/service) | 고정값이다. 실서비스의 접속자가 아니다 |
| BE | `api/src/app.ts` | (없음) | 권한을 전혀 검사하지 않는다 — 라우트 주석에 그대로 적혀 있다 |

`src/lib/perms.ts` · `incidents.ts` · `audit.ts` · `runHistory.ts` 는 각 파일 맨 앞에
"이건 '설정'이지 '집행'이 아니다 · 서버가 해야 한다" 라고 이미 적어 두었다. 서버를 붙일 때
**이 주석들도 같이 갱신한다** — 그대로 두면 문서와 코드가 어긋난다.

## 붙일 때 손댈 곳

### 화면 (jeju-ai-saas-fe)

1. **접속자** — `src/App.tsx` 의 `USER` 상수. SSO 응답으로 채운다.
   - `src/lib/audit.ts` 의 `setAuditActor()` 가 받는 모양(이름 · 부서 · 역할)이 그 계약이다.
   - `setAuditActor(USER)` 호출은 `src/App.tsx` 맨 위(모듈 최상위)에서 한 번 한다 — 지금도 그렇다.
2. **감사 기록** — `src/lib/audit.ts` 의 `setAuditSink()` 에 서버 전송 함수를 등록한다.
   - **호출 지점과 기록 형식은 이미 고정돼 있다** — 서버를 붙여도 기록하는 일은 늘지 않는다.
   - `AuditAction`(`export` · `incident.create` …)이 그대로 서버 계약이 된다.
3. **권한 설정** — `src/lib/perms.ts` 의 `loadPerms` · `savePerms` · `resetPerms`.
   - 정책(어떤 역할이 어떤 레이어 · 어떤 형식을 보는가)은 `src/data/constants.ts` 의
     `LAYER_ACCESS` · `EXPORT_ACCESS` **표**에 있다. `DEFAULT_PERMS` 는 그 표에서 만들어지는
     파생값이다.
   - 서버는 **같은 표**를 집행해야 한다. 표가 진짜 기준이다.
4. **사고 기록** — `src/lib/incidents.ts` 의 `loadIncidents` · `saveIncidents`. 서버 저장소로 교체.
   - 엑셀 가져오기 · 내려받기(`rowToIncident` · `incidentToRow`)도 그대로 쓸 수 있다.
5. **조회 이력** — `src/lib/runHistory.ts` 의 `commitRun` · `newIdsAgainst` · `clearHistory`.
   - 서버 상태화로 교체하면 '직전 조회 대비' 가 전 사람에게 같아진다.
   - 문구를 '직전 자료 대비' 로 바꿀지는 별도 결정이다(결정.md D19).

### 서버 (jeju-ai-saas-be)

6. **권한 검사 지점** — `api/src/app.ts` 의 `GET /api/orgs/:org/layers/:layer/files/*`.
   - 라우트 주석이 말하는 대로 "권한: 아직 막지 않는다" — **이 라우트가 검사 지점**이다.
   - `:org` · `:layer` · `:ws` 는 이미 `SLUG` 패턴으로 좁혀져 있고, 파일 경로는 `safeFilePath` 가
     올라가거나 숨은 파일을 막는다. 인증을 붙여도 이 부분은 손댈 것이 적다.
7. **목록 필터링** — `GET /api/catalog` 는 지금 모든 조직 · 레이어를 다 준다. 역할별로 거른다.
8. **감사 로그 자리** — `api/src/storage.ts` · `api/src/sync.ts` 는 자격 증명으로 버킷에 바로 붙는다.
   - '누가 무엇을 봤는가' 는 애플리케이션 로그로 남겨야 한다(S3 접근 로그가 아니다).

## 붙일 때 정해야 하는 것

| 결정 | 내용 | 상태 |
| --- | --- | --- |
| 인증 방식 | 사내 SSO · 자체 로그인 · 앞단 보안 게이트웨이 | 미정 |
| 서버 저장소 | 사고 기록 · 권한 · 조회 이력 · 감사 기록을 무엇에 저장하는가 | 미정 |
| 집행 위치 | BE 라우트에서 검사하는가, 앞단 게이트웨이가 하는가 | 미정 |
| gis-sass 재사용 | `repos/gis-sass/packages/api-core`(JWT · 권한 · 감사 로그) · `packages/web-core`(api-client · auth-store)를 가져오는가 | 미정 |

`gis-sass` 는 이미 인증 · 조직/워크스페이스 멤버십 · 감사 로그를 구현해 두었다. 새로 만드는
선택지만큼 나쁘지는 않지만, **같은 팀이 이미 만든 것을 쓰는 쪽이 싸다.** gis-sass 는 이
도메인을 쓰지 않으므로(api-core 가 아니라 `apps/customer/api` 에 있다) 세 번째 제품으로
편입하는 쪽이 precedent 다.

## 이 문서를 만든 계기

프로토타입 ↔ 제품 저장소의 파리티 점검(`.ai-workflow/work/index.md` 의 jeju-ai 고도화 작업)을
하면서 "브라우저에 있는 것"을 한 번에 세어 Putting 하기 위해 정리했다. 코드를 고칠 때
옮겨 갈 목록이다.
