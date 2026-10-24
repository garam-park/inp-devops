# 작업 현황

- 기준: 2026-10-22 08:35 KST(dev 반영 · 결정 대기 표시는 09:45 에 고침)
- 출처: [작업목록 xlsx](../../projects/jeju-ai/tasks/지반침하스마트관리시스템_작업목록-V0.1.xlsx)(기준일 10-20)의 108건을 저장소 코드 · git 이력 · GitHub 이슈/PR · 작업 기록과 맞춰 본 실제 상태다. 작업목록의 상태 칸이 아니라 실제를 적었다.
- jeju-ai 고도화의 인계 · 결정 대기: [tasks/jeju-ai-고도화/index.md](tasks/jeju-ai-고도화/index.md), [결정.md](tasks/jeju-ai-고도화/결정.md). 다음 세션은 여기서 시작한다.
- 다른 작업
  - CSAP 인증준비: [tasks/CSAP-인증준비/index.md](tasks/CSAP-인증준비/index.md)
  - 현장방문대비: [tasks/현장방문대비/](tasks/현장방문대비/)
  - goyang-uam 구조변경(porthole 구조로 전체 이동, 계획 단계): [tasks/goyang-uam-구조변경/index.md](tasks/goyang-uam-구조변경/index.md)
  - 이 문서는 그 셋의 현황을 다루지 않는다.

## 1. 한눈에 — 지반침하 스마트관리 시스템 (jeju-ai-saas)

화면(FE) · 서버(BE)의 기본 기능과 dev0 개발 클러스터는 다 만들어져 있다. develop 에 올리면 사람 손 없이 `jeju-ai.dev.innopam.net` 에 배포된다. 품질 검사(커밋 · push · 야간)도 갖춰졌다.

지금은 검토를 기다리는 PR 7개를 병합하는 단계다. 다음 큰 덩어리인 로그인 → DB → 지도 성능(벡터 타일)은 모두 **결정을 기다린다**. 시계열 기능은 자료를 기다린다.

| 영역 | 작업 | 끝남 | 진행 중 | 막힘 | 시작 전 | 확인 불가 |
| --- | --: | --: | --: | --: | --: | --: |
| FE (화면) | 46 | 32 | 3 | 1 | 9 | 1 |
| BE (서버 · 자료) | 26 | 16 | 3 | 2 | 5 | 0 |
| DevOps (dev0) | 36 | 28 | 1 | 3 | 4 | 0 |
| **합계** | **108** | **76** | **7** | **6** | **18** | **1** |

- 진행 중: 브랜치 · PR 이 있거나 일부만 됨. 막힘: 결정 · 자료 · 앞 작업을 기다림. 확인 불가: 했다는 근거가 없음.
- 작업목록의 8–10월 날짜는 보고용 가상 일정이다([기록 10-20/05](../../docs/history/2026/10/20/05.jeju-ai-task-list-xlsx.md)). 실제로는 프로토타입(9월)을 10-19 에 FE · BE 저장소로 나눴고, 품질 검사는 10-20 에 붙였다.

## 2. 지금 움직이는 것

### 열린 PR — 모두 CI 통과, 리뷰 · 병합 대기

| PR | 내용 | 작업목록 | 병합하면 |
| --- | --- | --- | --- |
| [FE #16](https://github.com/innopam/jeju-ai-saas-fe/pull/16) | 벡터 타일 렌더링 평가 메모 | FE-040 | 결정 근거로 남음 |
| [FE #13](https://github.com/innopam/jeju-ai-saas-fe/pull/13) | 형상 증빙(정적분석 · SBOM · 라이선스 리포트) | 없음(CSAP) | BE 는 10-22 에 병합됨 |
| [FE #14](https://github.com/innopam/jeju-ai-saas-fe/pull/14) | Dependabot: vite 8.2.2 → 8.3.5 | 없음 | 개발 의존성 갱신 |
| [BE #7](https://github.com/innopam/jeju-ai-saas-be/pull/7) | 린트 엄격도 상향(BE #4) | BE-017 후속 | BE #4 닫힘 |
| [BE #8](https://github.com/innopam/jeju-ai-saas-be/pull/8) | 파일 중계 CPU 줄이기(야간 k6, BE #3) | BE-018 후속 | 러너 p95 여유 확보 |
| [BE #9](https://github.com/innopam/jeju-ai-saas-be/pull/9) | 벡터 타일 전환 조사 메모 | BE-024 | 결정 근거로 남음 |

- **10-24 에 4개 PR 이 병합됐다** (아래 '10-24 에 한 일'). FE #15(화면 상태 처리 리팩터 · FE #6)를 포함한다.
- BE develop 에 오늘 PR #6(형상 증빙 + certifi 보안 수정)이 들어갔다(`f015e76`). CI 를 통과해 dev 에 반영됐다(api 이미지 `f015e76`, 08:34 Image Updater).
- 오늘 dev0 스토리지 메모리 상한을 512Mi → 1536Mi 로 올렸다. 동시 접속에서 OOM 이 나는 것을 로컬에서 재현했기 때문이다. dev 에 반영됐다([dev0 기록 10-22/01](../../ops/dev0/docs/history/2026/10/22/01.jeju-ai-saas-storage-memory.md)).

### PR 없이 일부만 된 작업

| 작업 | 된 것 | 안 된 것 |
| --- | --- | --- |
| FE-014 그리기 성능 | 화면 안 셀만 그림, 타일 지연 로딩 | '25만 셀 끊김 없음' 미달. 끌 때마다 1.6–1.7초 멈춤이 두 번 온다(FE-040 측정). '끊김' 기준도 정하지 않았다 |
| BE-011 샌드박스 시험 | 출력 검증, 격리 플래그 단위 시험 | 실제 컨테이너에서의 탈출 시험(네트워크 · 쓰기 · uid) 근거 없음 |
| BE-012 빌드 재현성 | README 절차 | 원본 GIS 경로가 개인 PC 절대경로(`gislib.py`)라 다른 PC 에서 재생성 불가 |
| DEVOPS-033 인증서 · 접근 | nginx 경유 VM 콘솔 확인 | Proxmox 인증서 SAN(W47) · LimitRange max(W59) |

## 3. 막힌 것 — 무엇을 기다리나

### 사용자 결정

| 결정 | 막힌 작업 | 근거 · 추천이 있는 곳 |
| --- | --- | --- |
| 지도 렌더러 · 전달 방식(벡터 타일 여부) | FE-014, FE-042, BE-025, DEVOPS-035 | FE #16 · BE #9 메모, 설계 05 §4-3 |
| 인증 방식(자체 계정 / OIDC) · 역할 출처 | BE-020, FE-041 | 설계 04 §8, 05 §4-4(발주처 SSO 확인) |
| DB: dev0 PV · 마이그레이션 도구 · 성명 저장 · 완전삭제 · 버킷명(CSAP 결정 3 · 7 · 9 와 겹침) | BE-021 → BE-022 · BE-023, FE-037 · FE-043 · FE-045, DEVOPS-034 | 설계 04 §5, [결정.md](tasks/jeju-ai-고도화/결정.md) D5 |
| 레이어 편집 저장 API(누가 · 어디에 저장) | FE-034(예정일 10-21 지남), FE-035 | BE 시트에 해당 작업 행이 없다 |
| 색 대비: 디자인 토큰 색 | FE-039 일부(FE #5), 야간 Lighthouse 매일 실패(FE #8) | FE #5 선택지 A · B |
| 품질 게이트 설정 4건 확정 | BE-019(지금 코드가 추천안 그대로라 확정만 하면 닫힘) | BE #2 |
| 복합 필터 조건 해석('시설물 이격거리'가 무엇인지) | FE-046 | 화면정의서 SCR-001 |
| 원본 GIS 자료를 공유 위치로 옮길지 | BE-012 | 설계 02 §5.1 · 04 §1 |
| 백업 대상 · 스토리지 예약 방식 | DEVOPS-031(W49 · W50) | dev0 main.md |
| 그 밖의 이슈 | FE #9(COOP) · FE #10(계약 검사) · FE #12(braces, 패치 없음) · BE #5(액션 SHA 고정) · W58(Hubble) | 각 이슈 |

### 자료 · 사람 · 외부

- 시계열 InSAR 자료 입수 대기: BE-026, FE-044.
- 발주처 확인 대기: SSO 방식, 감사 · 내보내기 보존 기간, 동시 사용자 수 · 피크.
- 운영 DB 는 NCP 공공 Cloud DB 로 정해졌다(CSAP ADR D4). PostGIS 는 지원 목록에 있다. 실제 확인은 Cloud DB 를 만드는 gov-ncloud 작업에서 한다.
- 사용자 손 필요
  - DEVOPS-031: NAS NFS 경로를 만들어 알려 줘야 한다.
  - DEVOPS-032: 장애 시험 2차의 전원 차단 · 노드 중단.
  - DEVOPS-029: 앞 작업 W65(official-website prd 전환)가 먼저다.
- 외부 도구: FE #7(ESLint 10 은 플러그인 지원을 기다린다).

## 4. 결정 없이 바로 할 수 있는 것

- 열린 PR 7개: CI 는 통과했다. 리뷰 · 병합 방식과 순서는 결정 대기다([결정.md](tasks/jeju-ai-고도화/결정.md) D2). BE #7 과 #8 은 서로 충돌한다.
- **BE #3 닫기 조건은 이미 채워졌다.** develop 야간 k6 가 10-21(288.9–292.6 ms)과 10-22(295.7–298.7 ms)에 두 번 연속 300 ms 아래였다. 다만 여유가 1–11 ms 라, 언제 되돌릴지는 결정 대기다(D1, 추천은 BE #8 병합 뒤).
- DEVOPS-030 모니터링 · 알림: 보류 이유('알림 받을 워크로드 없음')는 지금 맞지 않는다. 다만 설치는 클러스터 변경(메모리 약 1.2–1.5GB, Longhorn PV 10GB)이라 **착수 전 사용자 승인**이 필요하다. Hubble UI(W58)는 따로 결정한다.
- FE-021 화면 안 도움말 · 산정 모델 설명: 작업목록은 완료지만 실제로 없다.
- FE-027 Edge · Safari 확인: 근거가 없다.
- BE-011 실제 컨테이너 탈출 시험.
- 작업목록 정정(아래 5절).
- **10-24 에 끝난 것** (결정 없이 한 일 — 기록 10-24/03 · 04)
  - FE #15 병합 — 화면 상태 처리 리팩터(FE #6) + 회귀 수정 + strict 린트. `set-state-in-effect` 예외 0곳.
  - FE `App.tsx` 계산 규칙을 `src/hooks/` 5개로 분리 + 상태 27개를 5묶음으로 정리 (FE #18, 787줄 → 623줄).
  - FE 권한 정책을 '레이어 → 역할' 표로 (FE #19). 서버가 집행할 기준이 생겼다.
  - prototype 파이프라인을 jeju-ai-saas-be 원본과 같은 프로그램으로 맞춤 (Jeju-subsidence-AI #4). gislib.py 는 바이트 동일.
  - ws: prototype ↔ 제품 저장소 파리티 점검(`mise run check:parity`) + 인증 통합 지점 문서.

## 5. 작업목록과 실제가 다른 곳

| 작업 | 작업목록 | 실제 |
| --- | --- | --- |
| FE-032 E2E · 접근성 · 시각 회귀 | 진행 | 끝남(10-20 develop, FE #4 닫힘) |
| FE-036 CI · 야간 검사, FE-038 보안 헤더 | 예정 | 끝남(FE #1–#3 닫힘, dev 배포) |
| BE-018 품질 3단계 | 진행 | 끝남(10-20 develop) |
| BE-019 품질 마무리 | 예정 | BE #2 결정만 남음 |
| FE-039 · FE-040 · BE-024 | 예정(11월) | 이미 PR 이 있다(FE #15 · #16, BE #9) |
| FE-034 레이어 편집 설계 | 진행(10-21 종료) | 시작 전(설계 · 합의 흔적 없음) |
| FE-014 그리기 성능 | 완료 | 기준 미달(2절) |
| FE-021 도움말 | 완료 | 화면에 없음 |
| FE-027 브라우저 호환 | 완료 | 근거 없음(Playwright 는 Chromium 만) |
| BE-011 · BE-012 | 완료 | 일부만(2절) |
| FE-012 CSI 라벨 상한 | 700개 | 코드는 2,200개 |
| BE-005 굴착 지오코딩 | 동 단위 1,099건 · 19개 동 | 지번 지오코딩 1,322곳 · 2,169건 · 69개 동 · 리 |
| BE-003 · BE-007 · BE-009 산출물 경로 | 옛 경로 | `insar-velocity/10m/` 등으로 바뀜. CSI 로직 `main.py` 는 BE git 밖(스토리지 · 프로토타입에만) |
| DEVOPS-029 official-website 빌드 | 예정(10-21–22) | 기간이 지났는데 손대지 않음. GitHub 에 `release` 브랜치가 없다 |
| DEVOPS-034 PostgreSQL | Longhorn PV | dev0 결정(10/09/38 · W16)은 local-path |

작업목록에 없는 일

- PR: FE #13 · #14, BE #6(병합) · #7 · #8
- 이슈: FE #8–#12 · #17, BE #5
- dev0: 스토리지 메모리 상한 변경, 러너 용량. ARC 러너가 최대 2대라 push 가 몰리면 배포가 밀린다.

## 6. 앞으로의 흐름 (작업목록 일정 순)

1. **지금–10월 말**: PR 병합(D2), BE #3 · BE-019 닫기(D1 · D8), 모니터링(DEVOPS-030, 승인 뒤), 장애 시험 2차(DEVOPS-032, 사용자 손).
2. **10/27–11/11 로그인**: BE-020 → FE-041. 인증 방식 결정이 먼저다.
3. **11/04–11/20 DB 전환**: BE-021 설계 → BE-022 · BE-023 → FE-037 · FE-043 · FE-045. DEVOPS-034 와 함께 한다. dev0 PV · 도구 · CSAP 스키마 결정이 먼저다.
4. **11/05–12/02 지도 성능 · 벡터 타일**: FE-042 · BE-025 · DEVOPS-035. 렌더러 · 전달 방식 결정이 먼저다. 메모는 '화면 렌더러(캔버스)부터'를 추천한다.
5. **11/16–11/18 stage 환경**: DEVOPS-036. dev 쿼터가 거의 차서 stage 쿼터도 함께 본다.
6. **자료 입수 뒤 시계열**: BE-026 → FE-044.

## 7. 오늘까지의 기록

- [10-21/09](../../docs/history/2026/10/21/09.jeju-ai-saas-decision-free-tasks.md): 결정 없이 할 수 있는 6건
- [10-22/03](../../docs/history/2026/10/22/03.cleanup-old-worktrees.md): worktree 정리 · 커밋
- [10-22/04](../../docs/history/2026/10/22/04.jeju-ai-saas-pending-decisions.md): 결정 처리 · PR
- [10-22/05](../../docs/history/2026/10/22/05.work-index-status.md): 이 현황 문서
- [10-22/07](../../docs/history/2026/10/22/07.jeju-ai-handoff.md): 인계 문서 · 결정 대기 정리, ws push · dev0 스토리지 · FE #17
- [10-24/03](../../docs/history/2026/10/24/03.jeju-ai-prototype-parity.md): prototype 파이프라인 동기화 + 파리티 점검
- [10-24/04](../../docs/history/2026/10/24/04.jeju-ai-screen-structure.md): 화면 구조 정리(App.tsx 훅 분리 · 권한 정책표)

## 부록. 작업별 실제 상태 (108건)

근거는 대조할 때 확인한 파일 · 커밋 · 이슈다. 상태가 '끝남'이고 작업목록과 같은 행은 근거를 생략했다.

<details>
<summary>FE (화면) — 46건</summary>

| ID | 작업 | 작업목록 | 실제 | 근거 · 막힌 이유 |
| --- | --- | --- | --- | --- |
| FE-001 | FE 프로젝트 골격 | 완료 | 끝남 |  |
| FE-002 | 디자인 토큰·아이콘·글꼴 | 완료 | 끝남 |  |
| FE-003 | 헤더·GNB | 완료 | 끝남 |  |
| FE-004 | 지도 뷰어 기반(MapPane) | 완료 | 끝남 |  |
| FE-005 | 조회 조건(지역·기간·등급) | 완료 | 끝남 |  |
| FE-006 | 해안선·지질·재해위험지구 GeoJSON 레이어 | 완료 | 끝남 |  |
| FE-007 | 격자 셀 렌더링(GridCellsLayer) | 완료 | 끝남 |  |
| FE-008 | 조회 결과(도넛·순위 목록) | 완료 | 끝남 |  |
| FE-009 | InSAR 지반 변위 레이어 | 완료 | 끝남 |  |
| FE-010 | 구역 상세·판단 근거 | 완료 | 끝남 |  |
| FE-011 | 지하시설물 레이어(관로·굴착) | 완료 | 끝남 |  |
| FE-012 | 위험격자(CSI) 레이어·등급 라벨 | 완료 | 끝남 |  |
| FE-013 | 침하 사고이력 레이어·사고 관리 화면 | 완료 | 끝남 |  |
| FE-014 | 그리기 성능 정리 | 완료 | 진행 중 | 화면 안 셀 라벨만 그리기와 타일 지연 로딩은 있음. FE-040 메모(PR #16, docs/research/vector-tile-rendering.md 요약·§3-2): 1600×1000 배율 15에서 끌 때마다 1.6–1.7초 멈춤이 두 번 생겨 '25만 셀 끊김 없음'을 채우지 못하고, '끊김' 기준도 정해지지 않음 **막힘:** '끊김' 기준 결정, FE-040 렌더러 방향 결정 |
| FE-015 | 레이어 패널·범례 | 완료 | 끝남 |  |
| FE-016 | 위험 징후 알림 | 완료 | 끝남 |  |
| FE-017 | 공간정보 내보내기·리포트 | 완료 | 끝남 |  |
| FE-018 | 기간 설정(RunBar)·기간별 점수 전환 | 완료 | 끝남 |  |
| FE-019 | 워크스페이스·레이어 설정(manifest) 로딩 | 완료 | 끝남 |  |
| FE-020 | 권한·작업 기록 화면 | 완료 | 끝남 |  |
| FE-021 | 도움말·산정 모델 설명 | 완료 | 시작 전 | Header.tsx에 도움말 메뉴가 없음(주석 :18, 프로토타입 1cccc44부터 뺐음). app.css:2251 '도움말 팝오버' 절은 비어 있음. 산정 근거는 화면 밖 문서(프로토타입 docs/CSI_산정근거.html·pdf)에만 있음. 화면 안 가중치·등급 기준 설명은 코드 검색 0건 |
| FE-022 | 표시 형식 해석기(layerStyle) | 완료 | 끝남 |  |
| FE-023 | 분석 실행 기록·기간 설정 동작 | 완료 | 끝남 |  |
| FE-024 | 단위 테스트 정비(vitest) | 완료 | 끝남 |  |
| FE-025 | 구조 전환 검증 | 완료 | 끝남 |  |
| FE-026 | FE 저장소 분리·strict TypeScript 전환 | 완료 | 끝남 |  |
| FE-027 | 브라우저 호환·반응형 점검 | 완료 | 확인 불가 | 오른쪽 패널 드로어(App.tsx:165), app.css의 @media는 1곳. playwright.config.ts는 chromium 프로젝트만 있음. Edge·Safari 확인 기록 없음 |
| FE-028 | 품질 검사 1단계: 도구 고정·훅·비밀값 차단 | 완료 | 끝남 |  |
| FE-029 | 품질 검사 2단계: 린트·접근성 규칙 | 완료 | 끝남 |  |
| FE-030 | FE 이미지·API 프록시 | 완료 | 끝남 |  |
| FE-031 | 예시 레이어(동 중심점) 추가 | 완료 | 끝남 |  |
| FE-032 | E2E·접근성·웹표준·시각 회귀 | 진행 | 끝남 | 52e71af(Playwright 전환), e8e9beb(axe), e9973e1(html-validate), 9c2a852 + e2e/__snapshots__ PNG 8장, e2e/fixture-server.ts. develop 병합 e9ca15d(10-20). amd64 러너에서 기준 PNG 통과(77d99c0, ci 39388043299). FE #4 닫힘 |
| FE-033 | 컴포넌트 분리·훅 정리 | 완료 | 끝남 |  |
| FE-034 | 레이어 순서·표시 편집 UI 설계 | 진행 | 시작 전 | 설계 메모, BE 저장 API 합의, 관련 이슈 모두 없음(ws docs/design/jeju-subsidence-ai, FE·BE README·docs, 이슈 목록 검색). 10-21/09에서 '결정 필요'로 분류. 작업목록의 종료 예정일 10-21이 지남 **막힘:** BE와 워크스페이스 저장 API 요건 합의(결정) |
| FE-035 | 레이어 순서·표시 편집 UI 구현 | 예정 | 시작 전 | 관련 코드·브랜치·PR 없음. BE 시트에 워크스페이스 저장 API 작업 행이 없음 **막힘:** FE-034 설계, BE 워크스페이스 저장 API |
| FE-036 | FE CI 게이트·야간 검사 | 예정 | 끝남 | .github/workflows/ci.yml(모든 push → checks·e2e, develop만 build-push), nightly.yml(Lighthouse·k6·ZAP·trivy, 04:00 KST). develop 7e3d70a(10-20), FE #1·#2 닫힘. 야간 39505134831·39683693889는 Lighthouse 단계만 실패(FE #8) |
| FE-037 | 메타데이터 DB 전환에 맞춘 FE 변경 | 예정 | 시작 전 | FE는 아직 /api/catalog 파일 catalog를 읽음(lib/workspace.ts). 관련 브랜치·이슈 없음 **막힘:** BE-021·BE-022 메타데이터 DB 설계·전환 |
| FE-038 | nginx 보안 응답 헤더 | 예정 | 끝남 | nginx.headers.conf(CSP·nosniff·Referrer·XFO·Permissions·HSTS), e2e/headers.spec.ts. 커밋 5dfe5dc·1b175b8·8428a5a, FE #3 닫힘. dev 응답 헤더 6개 확인(10-20/09). dev 브라우저에서 CSP 아래 배경지도·내보내기는 확인 안 함. 후속 FE #9(COOP) |
| FE-039 | 색 대비 토큰 결정 반영·리팩터 | 예정 | 진행 중 | #6: PR #15 열림(checks·e2e 성공, set-state-in-effect 예외가 develop 4곳에서 브랜치 0곳으로, strict 린트 병합 32285fb 포함). #5 열림(tokens.css #7e7e7e·#a1a1a1 그대로). #7 열림: jsx-a11y 6.10.2 peer ^9, react 7.37.5 peer ^9.7(10-22 npm 확인) **막힘:** #5 디자인 토큰 색 결정, #7 플러그인의 ESLint 10 지원, PR #15 리뷰·병합 |
| FE-040 | 벡터 타일(MBTiles/PMTiles) 렌더링 전환 평가 | 예정 | 진행 중 | PR #16 열림(checks 성공): docs/research/vector-tile-rendering.md + 평가 페이지(71151a1). 추천은 모두 '결정 필요'. BE 짝 메모는 BE PR #9(BE-024) **막힘:** 렌더러·전달 방식(05 §4-3) 결정, 운영 PC WebGL 확인, PR #16 병합 |
| FE-041 | 로그인 화면·세션 처리 | 예정 | 시작 전 | 로그인 화면·세션 코드 없음. 역할은 고정값(PR #15 본문 'role 이 service 로 고정') **막힘:** BE-020 인증 API, SSO 방식 결정(05 §4-4) |
| FE-042 | 벡터 타일 렌더링 적용 | 예정 | 시작 전 | 앱 코드·의존성 변경 없음(PR #16은 메모만) **막힘:** FE-040 결정, BE-025 타일 파이프라인·제공 |
| FE-043 | 권한 화면을 DB API 로 전환 | 예정 | 시작 전 | lib/perms.ts가 아직 localStorage 사용(perms.test.ts) **막힘:** BE-021·BE-022 DB API |
| FE-044 | 시공간 타임슬라이더 | 예정 | 막힘 | 작업목록 비고 '시계열 자료 입수 뒤', BE-026 '자료 입수 뒤'. AlertPanel.tsx:35 시계열 자료 없음 **막힘:** 시계열 InSAR 자료 입수(BE-026) |
| FE-045 | 작업 기록 서버 저장 전환 | 예정 | 시작 전 | lib/audit.ts가 아직 localStorage 저장(:70, :102) **막힘:** BE-023 감사 저장 API |
| FE-046 | 복합 조건 필터(인자값 조합 검색) | 예정 | 시작 전 | 관련 코드·이슈 없음. 10-21/09에서 '복합 필터 조건 해석' 결정 필요로 분류 **막힘:** 조건 해석 결정 |

</details>

<details>
<summary>BE (서버 · 자료) — 26건</summary>

| ID | 작업 | 작업목록 | 실제 | 근거 · 막힌 이유 |
| --- | --- | --- | --- | --- |
| BE-001 | 원본 자료 조사·좌표계 정리 | 완료 | 끝남 |  |
| BE-002 | 원본 자료 품질 점검·결측 처리 | 완료 | 끝남 |  |
| BE-003 | 10 m 표준 격자·100 m 집계 셀 생성 | 완료 | 끝남 |  |
| BE-004 | 인벤토리 격자 바인딩 | 완료 | 끝남 |  |
| BE-005 | 굴착 허가 지오코딩 | 완료 | 끝남 |  |
| BE-006 | 행정경계 최근접 배정·지역 목록 | 완료 | 끝남 |  |
| BE-007 | 복합 위험지수(CSI) 산정 로직 | 완료 | 끝남 |  |
| BE-008 | 기간별 점수 사전 계산 | 완료 | 끝남 |  |
| BE-009 | 워크스페이스·레이어 자료 구조 | 완료 | 끝남 |  |
| BE-010 | 지수 레이어 계약·격리 실행 | 완료 | 끝남 |  |
| BE-011 | 샌드박스 탈출 시험·출력 검증 | 완료 | 진행 중 | 출력 검증은 있다. pipeline/tests/test_run_index.py 가 JSON 만·크기 상한·링크 금지·out/ 통째 교체·격리 플래그를 단위 테스트한다(CI pipeline 잡). 그러나 docker 를 모의로 바꿔 끼워(subprocess.run) 플래그만 본다. 실제 컨테이너에서 네트워크·DNS·쓰기 차단과 uid 를 확인하는 탈출 시험은 코드·CI·기록 어디에도 없다. 수동으로 했는지는 확인 불가. |
| BE-012 | 데이터 빌드 재현성 | 완료 | 진행 중 | README '파이프라인과 지수 레이어' 절차가 있고, build_data.py 는 data/orgs/jeju/layers/** 로 쓴다. 하지만 data/ 는 .gitignore 대상이다(스토리지가 원본). 그래서 '산출 자료를 저장소에 포함'과 반대다. 원본 경로가 개인 PC 절대경로다(gislib.py SRC=/Users/gyuyoung/Downloads/…, INSAR_DIR=/Volumes/GeoAI2/…). 다른 PC·CI 에서는 다시 만들 수 없다(설계 01 §7-2). 지금 자료의 generatedAt 이 2026-09-17 이라 BE 에서 다시 돌린 흔적이 없다(추정). **막힘:** 원본 GIS 자료를 공유 위치(스토리지 raw/ 등)로 옮길지 결정과 이관(설계 02 §5.1·04 §1) |
| BE-013 | BE 저장소 분리·API 골격 | 완료 | 끝남 |  |
| BE-014 | 객체 저장소(SeaweedFS S3)·동기화 CLI | 완료 | 끝남 |  |
| BE-015 | catalog·workspace·layer files API | 완료 | 끝남 |  |
| BE-016 | API 이미지·dev 배포 연동 | 완료 | 끝남 |  |
| BE-017 | 품질 검사 1–2단계: 도구·훅·린트 | 완료 | 끝남 |  |
| BE-018 | 품질 검사 3단계: 통합 테스트·CI 게이트·야간 검사 | 진행 | 끝남 | 산출물이 모두 develop 에 있다: docker-compose.test.yml, api/test/integration 16개, api/scripts/fixtures.ts 시드, ci.yml(checks·integration·pipeline → build-push, semgrep), nightly.yml(k6·ZAP·trivy), @fastify/helmet(9823c1d). develop 머지 21cb656·589ac14(10-20). 러너 ci 39388069706 성공. 야간 검사 39496555443·39675051984 성공(ZAP High 0, trivy HIGH·CRITICAL 0). BE #1 은 10-20 에 닫혔다. 남은 BE #2 결정은 BE-019 범위다. |
| BE-019 | 품질 게이트 마무리 | 예정 | 막힘 | 3개 중 2개는 끝났다. BE #1 은 10-20 에 닫혔다: 러너 ci 39374635323·39375973207, nightly 39374659883·39375982717, 기록 20/09. 깨끗한 클론 재현은 로컬 에이전트가 했다. BE #2 는 댓글 없이 열려 있다. 지금 코드는 이미 추천안 4개 상태다: .prettierrc singleQuote, run_index.py docker 인자 줄 분리, mise ci 에 test:integration 포함, 커버리지 70. 그래서 결정만 하면 코드 변경 없이 닫을 수 있다. **막힘:** BE #2 설정 결정 4건(사용자 결정) |
| BE-020 | 로그인·인증 API | 예정 | 시작 전 | api 에 인증 코드가 없다(README '권한은 아직 막지 않는다'). 설계 초안만 있다: ws docs/design/jeju-subsidence-ai/04 §8(1차 자체 계정·Argon2id·세션 쿠키·CSRF, 2차 OIDC)과 05 §4-4 열린 결정. 기록 21/09 에서 '결정 필요'로 분류됐다. **막힘:** 결정: 인증 방식(자체 계정/OIDC)과 역할 출처(05 §4-4), 발주처 SSO 확인. FE-041 과 함께 |
| BE-021 | 메타데이터 DB 설계 | 예정 | 시작 전 | BE 저장소에 DB 코드·문서가 없다. ws 설계 04 §5 'DB 스키마 초안'(users·roles·sessions·dataset_versions·audit_events 등)은 있다. 그러나 조직·워크스페이스·레이어 표가 없고, 마이그레이션 도구도 'Drizzle 또는 Kysely'(02)로 정해지지 않았다. 기록 21/09 에서 결정 필요로 분류됐다. **막힘:** 결정: 운영 DB 의 PostGIS 가능 여부(발주처·DBA, 05 §5)와 마이그레이션 도구 |
| BE-022 | 조직·워크스페이스·레이어 DB 전환 | 예정 | 시작 전 | 코드가 없다. catalog 는 아직 스토리지 파일을 훑어 만든다(api/src/catalog.ts). **막힘:** 앞 작업 BE-021(DB 설계)·BE-020(권한 검사용 사용자·역할), FE 관리 화면 전환과 함께 |
| BE-023 | 작업 기록(감사) 저장 API | 예정 | 시작 전 | 코드가 없다. 설계 04 §5 audit_events·§8 감사, 보존 기간은 05 §4-9(기본 3년 제안, 발주처 확인)에 있다. **막힘:** 앞 작업 BE-020·BE-021, 보존 기간 결정(05 §4-9) |
| BE-024 | 벡터 타일 전환 조사 | 예정 | 진행 중 | 브랜치 docs/vector-tile-research 93000a5(10-22), PR #9 OPEN, 러너 ci 39691539998 성공. docs/research/vector-tiles.md 616줄과 재현 스크립트 12개가 작업 범위를 모두 다룬다: tippecanoe MBTiles·PMTiles 용량·시간(10m 110–118초·1.75GB, PMTiles 129MB), 제공 방식(스토리지 range·martin·API JSON) 지연·동시 접속, 캐시·갱신(버전 키). 추천(P1b 등)은 모두 '결정 필요'로 남겼다. 짝 작업 FE-040 은 FE PR #16. 기록 21/09 §5. 작업목록 예정일(11-20–11-24)보다 한 달 앞섰다. **막힘:** PR #9 검토·병합. 전달 방식(05 §4-3)과 제공 경로는 사용자 결정 |
| BE-025 | 벡터 타일 파이프라인·제공 | 예정 | 시작 전 | 코드가 없다(manifest source 에 tiles 종류 없음). BE-024 메모 §5 는 P1b(martin 이 PMTiles 사본을 읽음, DEVOPS-035)를 추천한다. §7 의 FE-040 질문 14개가 범위를 정한다. **막힘:** 결정 05 §4-3(PostGIS bbox·MVT·파일 유지), 제공 경로·버전 키. BE-024(PR #9)·FE-040(FE PR #16) 검토 뒤 |
| BE-026 | 시계열 InSAR 적재 | 예정 | 막힘 | build_data.py 1537줄에 '가속도는 시계열이 없어 미산출입니다'라고 적혀 있다. 지금 InSAR 는 7년 스택 평균 변위속도다(build.json insar.source jeju7yr_grid10m_polygon.gpkg). 시계열 자료를 입수한 기록이 없다. **막힘:** 시계열 InSAR 변위 자료 미입수(외부) |

</details>

<details>
<summary>DevOps (dev0) — 36건</summary>

| ID | 작업 | 작업목록 | 실제 | 근거 · 막힌 이유 |
| --- | --- | --- | --- | --- |
| DEVOPS-001 | Proxmox 노드 정리 | 완료 | 끝남 |  |
| DEVOPS-002 | 클러스터 구축 준비 | 완료 | 끝남 |  |
| DEVOPS-003 | dev0 클러스터 부트스트랩 | 완료 | 끝남 |  |
| DEVOPS-004 | local-path 스토리지 | 완료 | 끝남 |  |
| DEVOPS-005 | Tailscale 경유 API 접속·CA 교체 | 완료 | 끝남 |  |
| DEVOPS-006 | C4 구조도·구축 보고서·백업 절차 | 완료 | 끝남 |  |
| DEVOPS-007 | Proxmox 3노드 클러스터·VIP | 완료 | 끝남 |  |
| DEVOPS-008 | 두 번째 망·corosync 2링크 | 완료 | 끝남 |  |
| DEVOPS-009 | 컨트롤 플레인 3대·워커 3대로 확장 | 완료 | 끝남 |  |
| DEVOPS-010 | 장애 시험 1차 | 완료 | 끝남 |  |
| DEVOPS-011 | 관리 환경 Mac 이전 | 완료 | 끝남 |  |
| DEVOPS-012 | Tailscale 서브넷 라우터 3대·ACL | 완료 | 끝남 |  |
| DEVOPS-013 | Proxmox 웹 TLS·백업 매체·PV 보호 방향 | 완료 | 끝남 |  |
| DEVOPS-014 | Longhorn 설치·시험 | 완료 | 끝남 |  |
| DEVOPS-015 | 할 일 체계 정비 | 완료 | 끝남 |  |
| DEVOPS-016 | 설정 보강 | 완료 | 끝남 |  |
| DEVOPS-017 | metrics-server·Hubble | 완료 | 끝남 |  |
| DEVOPS-018 | 저장소 품질 검사 | 완료 | 끝남 |  |
| DEVOPS-019 | 백업 체계 | 완료 | 끝남 |  |
| DEVOPS-020 | 운영 문서·단일 출처 | 완료 | 끝남 |  |
| DEVOPS-021 | 클러스터 재구축(새 비밀값) | 완료 | 끝남 |  |
| DEVOPS-022 | 전원 차단 시험 | 완료 | 끝남 |  |
| DEVOPS-023 | prd 네임스페이스·Cilium Ingress | 완료 | 끝남 |  |
| DEVOPS-024 | 프로토타입 dev 배포·앱 비밀값 규칙 | 완료 | 끝남 |  |
| DEVOPS-025 | GitHub Actions 러너(ARC) | 완료 | 끝남 |  |
| DEVOPS-026 | jeju-ai-saas dev 매니페스트·Argo CD 설치 | 완료 | 끝남 |  |
| DEVOPS-027 | develop 자동 배포 컷오버 | 완료 | 끝남 |  |
| DEVOPS-028 | Argo CD 계정·백업 갱신 | 완료 | 끝남 |  |
| DEVOPS-029 | official-website build-push 워크플로 | 예정 | 막힘 | W66 은 todo '대기(W65 끝난 뒤)'. official-website 의 .github/workflows 에는 deploy.yml(SSH 배포)만 있음. 시트 기간(10-21–10-22)이 지났는데 손대지 않음. release 브랜치는 GitHub 에 없음(gh api 404, 기본 브랜치 main) **막힘:** 앞 작업 W65(official-website prd 전환: NPM 뒷단 교체·누락 env 키, 사용자 손)를 기다림. 대상 브랜치(release→main) 다시 정해야 함 |
| DEVOPS-030 | 모니터링·알림 | 예정 | 시작 전 | k8s/ 에 kube-prometheus-stack 없음(grep). W48 은 todo '보류'(보류 이유는 알림 받을 워크로드가 없다는 것이었는데, 지금은 jeju-ai-saas·official-website 가 떠 있음). W58 은 결정 필요 **막힘:** Hubble UI 확인 부분만 사용자 결정(W58: 쓸지 안 쓸지). 설치 자체는 결정 필요 없음 |
| DEVOPS-031 | Longhorn 백업 대상·스토리지 예약 | 예정 | 막힘 | k8s/longhorn/values.yaml 에 backupTarget·storageReservedPercentage 없음. W49·W50 모두 '결정 필요'. W49 의 전제 'PVC 0개'는 낡았음: jeju-ai-saas-storage PVC 5Gi(longhorn)가 있음. 다만 자료는 사본이라 다시 올리면 됨(storage.yaml 주석) **막힘:** W49: NAS 의 NFS 공유 경로를 사용자가 만들어 알려 줘야 함. W50: 예약 비율·용량 제한·데이터 디스크 분리 가운데 방식 결정 |
| DEVOPS-032 | 장애 시험 2차 | 예정 | 시작 전 | W42 todo(결정 필요 없음). 전원 차단은 10/13 에 했지만 main.md W42 에는 아직 남아 있음. 10/13/01 에 기록 없이 만든 w42-test 네임스페이스(Longhorn 5Gi)가 보였음. W42 를 일부 시도했을 수 있음(추정) **막힘:** 전원 차단과 노드 중단은 사용자가 직접 해야 함(결정 대기는 아님) |
| DEVOPS-033 | 인증서·접근 경로 정리 | 예정 | 진행 중 | 일부만 됨: nginx 를 거친 VM 콘솔(WebSocket)은 10-10 W41 에서 확인(main.md W43 비고). 나머지는 손대지 않음: tofu/versions.tf:20 이 아직 insecure = true(W47), LimitRange max 는 dev.yaml 에 그대로(W59). 지금 진행 중인 작업은 없음 **막힘:** W59: LimitRange max 유지·삭제·변경 결정(사용자). W47: pve-2·3 에서 사용자가 명령 실행. W43: nginx 중단은 사용자 손 |
| DEVOPS-034 | PostgreSQL 운영 구성 | 예정 | 시작 전 | dev0 에 CloudNativePG·Postgres 없음. BE 저장소 develop 에도 DB 코드 없음(git grep). W16 은 todo '보류'. 설계 문서 docs/design/jeju-subsidence-ai/02.target-architecture.md 는 PostgreSQL + PostGIS **막힘:** 앞 작업 BE-021(메타데이터 DB 설계, BE 시트 예정). PV 종류(시트는 Longhorn, 10/09/38·W16 은 local-path)부터 맞춰야 함 |
| DEVOPS-035 | 타일 제공 구성 | 예정 | 막힘 | dev0 에 martin·PMTiles 구성 없음. BE PR #9(OPEN, docs/research/vector-tiles.md)는 P1b(martin 이 버전 붙은 PMTiles 복사본을 읽음)를 추천하지만 '결정 필요'로 남김. FE PR #16(OPEN) 평가 메모. ws 10/22/04 남은 결정에 '벡터 타일 방향' **막힘:** 벡터 타일 방향 결정(사용자). BE PR #9·FE PR #16 검토 |
| DEVOPS-036 | stage 환경·승격 절차 | 예정 | 시작 전 | apps/jeju-ai-saas/overlays/stage 없음. apps·k8s/argocd 어디에도 stage 참조 없음. stage 네임스페이스와 쿼터(1.5 CPU·2560Mi, k8s/namespaces/stage.yaml)만 있음. jeju-ai-saas limits.memory 합이 1920Mi 라 쿼터 여유가 적음(추정) |

</details>
