# 코딩 컨벤션

| 항목 | 내용 |
| --- | --- |
| 문서번호 | JSA-PF-ST-001 |
| 시스템 | 지반침하 스마트 관리 시스템(통합플랫폼) |
| 분류 | 표준·환경 |
| 버전 | V0.1 |
| 작성일 | 2026-10-16 |
| 작성자 / 승인자 | 김재헌 / 박가람 |

## 제·개정 이력

| 버전 | 날짜 | 변경 내용 | 작성자 | 승인자 |
| --- | --- | --- | --- | --- |
| 0.1 | 2026-10-16 | 최초 작성 | 김재헌 | 박가람 |

## 1. 원칙

- **표기(case)로 종류를 구분한다.** 이름만 보고 변수(`snake_case`)·함수(`camelCase`)·타입(`PascalCase`)·상수(`UPPER_SNAKE_CASE`)를 알 수 있어야 한다.
- **모든 언어에 같은 규칙을 적용한다.** 언어 생태계의 관례와 다른 부분이 있어도 종류 구분의 일관성을 우선한다. 외부 라이브러리·프레임워크가 강제하는 이름(오버라이드 메서드, 프레임워크 훅 등)만 예외이며 해당 API의 표기를 따른다.
- **약어는 일반 단어처럼 취급한다.** `HttpServer`, `user_id`, `parseUrl()` 처럼 쓴다(`HTTPServer`, `parseURL()` 은 쓰지 않는다).
- **기능(도메인)별로 묶고 그 안에 계층을 둔다.** 의존은 `controller → service → repository` 한 방향만 허용하고, 다른 도메인은 service 를 거쳐서만 접근한다. 이보다 복잡한 구조(헥사고날 등)는 필요가 증명되기 전에는 쓰지 않는다.
- **규칙마다 이유를 함께 기록한다.** 지키기 어렵거나 불필요해진 규칙은 수정·삭제한다.
- 규칙 원본은 저장소의 `docs/rules/` 에 있고, 이 문서에 옮긴 규칙의 상태는 모두 "확정"(2026-07-11)이다.

## 2. 언어별 규칙

| 언어 | 포맷터·린터 | 설정 파일 | 비고 |
| --- | --- | --- | --- |
| Java | 테스트 커버리지 JaCoCo | `apps/*/api/**/build.gradle.kts`, `packages/api-core/build.gradle.kts` | Java 25(Temurin) · Spring Boot 4.1 · Gradle 9.7(Kotlin DSL). API 는 `api-core` 를 컴포지트 빌드로 공유 |
| TypeScript | 컴파일러 엄격 옵션(`strict`, `noUnusedLocals`, `noUnusedParameters`) | `apps/customer/web/tsconfig.json`, `apps/admin/web/tsconfig.json`, `packages/web-core/tsconfig.json` | Node 24 · Vite · React 18. 빌드 `tsc -b && vite build`, 테스트 Vitest |
| Markdown | markdownlint-cli2 0.23.3 | 저장소 루트 `.markdownlint-cli2.jsonc` | CI `docs` 잡이 린트와 문서 링크 검사(`scripts/check-doc-links.py`)를 실행 |
| Python | - | - | 보조 스크립트용. 모듈 이름은 `snake_case` |

이름·계층 규칙은 6절 코드 리뷰 체크리스트로 확인한다. 로그 비밀 비노출(5절), 응답 envelope·`X-Api-Version` 헤더·비멤버 404 같은 동작 규칙은 테스트로 확인한다.

## 3. 이름 규칙

| 대상 | 규칙 | 예 |
| --- | --- | --- |
| 클래스·인터페이스·타입 | `PascalCase`. `I` 같은 접두사를 붙이지 않는다 | `User`, `OrderItem`, `PaymentService` |
| 메서드·함수 | `camelCase` + 표준 동사. `get` 은 반드시 존재하는 것(없으면 예외), `find` 는 없을 수 있는 것(없으면 null), `fetch` 는 원격·IO, `list` 는 컬렉션, 그 밖에 `create`·`update`·`delete` | `getUser()`, `findUser()`, `listOrders()` |
| 변수·매개변수 | `snake_case`(컬렉션은 복수형). boolean 은 `is_`·`has_`·`can_` 접두사, 단위가 있는 값은 단위 접미사 필수 | `user_name`, `active_users`, `timeout_ms` |
| 상수·환경변수 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `DATABASE_URL` |
| 파일·디렉터리 | `kebab-case`(Python 모듈은 `snake_case`). 테스트 파일은 생태계 기본 패턴 | `user-service.ts`, `user_service.py`, `user-service.test.ts` |
| DB 테이블·컬럼 | `snake_case`. 테이블은 복수형, 컬럼은 단수형. 시각 `_at`, 날짜 `_on`, 외래키 `_id`. 인덱스·제약은 `접두사_테이블_컬럼`(`pk_`·`fk_`·`uq_`·`ix_`·`ck_`) | `users`, `created_at`, `ix_users_email` |
| API JSON·쿼리 필드 | `snake_case`. enum 값은 저장값 그대로 `UPPER_SNAKE_CASE` | `user_id`, `?status=IN_PROGRESS` |
| URL 경로 | `kebab-case`, 리소스 이름은 복수형 | `/order-items`, `/users/{id}` |
| 내부용 멤버 | 모든 언어에서 `_` 접두사 | `_cache`, `_buildQuery()` |

## 4. 주석·문서화

- 결정의 근거는 코드 주석이 아니라 ADR(`docs/01.개발/ADRs/`)에, API 계약은 `docs/01.개발/APIs/` 에, 테스트 절차는 `docs/TESTING.md` 에 남긴다. 설계서는 "무엇이 어떻게 되어 있는가", ADR 은 "왜 그렇게 정했는가"로 역할을 나눈다.
- 커밋 본문에는 "무엇"이 아니라 "왜"를 적는다(JSA-PF-ST-002).
- 문서는 한국어로 작성한다. 비밀값·개인정보를 문서에 넣지 않는다(JSA-PF-ST-002 5절의 비밀값 커밋 금지와 같은 방침이다).

## 5. 오류 처리·로깅

- **실패는 예외로 전파한다.** "없음이 정상"인 경우만 null 을 반환한다(`find` 류).
- 도메인 예외는 공통 부모(`AppError` 등) 아래에 두고, 응답에 필요한 정보(HTTP 상태, 응답 코드, 개발자용 message)를 스스로 가진다.
- **예외는 진입 경계의 공통 핸들러에서만 잡는다.** 중간 계층은 복구할 수 있을 때(재시도·대체값·보상)만 catch 하고, 빈 catch 나 로그만 찍고 계속 진행하는 catch(삼키기)는 쓰지 않는다.
- API 응답은 성공·실패 모두 `code` + `message` + `result` envelope 이며, `code` 앞 3자리는 HTTP 상태와 같다(예: `404001`). 비멤버에게는 403 이 아니라 404 를 준다(존재 은닉).
- 로그는 필드 기반 JSON 한 줄로 남기고(운영 프로필 `prod`), 모든 로그에 `request_id` 를 포함한다. 메시지에 값을 문자열로 섞지 않고 필드로 분리한다.
- **비밀번호·토큰·개인정보는 로그에 남기지 않는다.** 감사·인증 로그 컨텍스트에 비밀번호·토큰·인증키로 보이는 필드가 생기면 실패하는 회귀 테스트가 있다(`AuditLogPrivacyTest`, `AuthLogPrivacyTest`). `SourceResponsePrivacyTest` 는 로그가 아니라 소스 응답 DTO 에 외부 인증키 값 필드가 없는지(설정 여부 `has_auth_secret` 만 허용)를 지키는 테스트다.
- 로그 레벨: `ERROR` 는 사람의 조치가 필요한 예상 밖 실패만, `WARN` 은 비정상이지만 동작에 지장 없는 경우(4xx 는 원칙적으로 WARN 이하), `INFO` 는 주요 이벤트, `DEBUG` 는 개발·진단용(운영 기본 INFO).

## 6. 코드 리뷰 체크리스트

머지 전 셀프 리뷰에서 diff 를 처음부터 끝까지 읽으며 아래를 확인한다. 항목 끝에 근거를 적었다.

- [ ] 이름이 표기 규칙을 따른다(변수 `snake_case`, 함수 `camelCase`, 타입 `PascalCase`, 상수 `UPPER_SNAKE_CASE`, 단위 접미사). — `naming.md`
- [ ] `controller → service → repository` 방향만 쓰고, 다른 도메인은 service 로만 접근한다. `shared/` 에 도메인 지식이 들어가지 않았다. — `project-structure.md`
- [ ] 실패를 예외로 전파하고 삼키는 catch 가 없다. `get` 은 없으면 예외, `find` 는 없으면 null 이다. — `error-logging.md`
- [ ] 인가 판정이 service 계층의 명시적 가드에 있고, 비멤버는 404 로 응답한다. — ADR-2026-08-18.01
- [ ] 응답이 `code`·`message`·`result` envelope 이고 `X-Api-Version` 헤더를 지킨다. 새 오류 코드는 코드표에 반영했다. — `rest-api.md`
- [ ] 로그에 비밀·토큰·개인정보가 없고 `request_id` 가 포함되며 레벨 기준을 지켰다. — `error-logging.md`
- [ ] 테스트가 given-when-then 구조와 한국어 문장 이름을 따르고, mock 은 외부 경계에만 썼다. 버그 수정에는 재현 테스트를 남겼다. — `test.md`
- [ ] 관련 문서(API 문서·ADR·설계서·`docs/TESTING.md`)를 갱신했다. — JSA-PF-ST-003 2절(Definition of Done)
- [ ] 이해하지 못한 줄(특히 AI 가 생성한 코드)은 머지하지 않는다. — `pull-request.md`

## 7. 근거 자료

- `docs/rules/coding/naming.md`, `project-structure.md`, `rest-api.md`, `error-logging.md`, `test.md` (gis-sass 저장소)
- `docs/rules/workflow/pull-request.md` (gis-sass 저장소)
