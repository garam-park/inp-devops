# md2docx-styled

`../*.md` 를 `docx` 로 변환한 결과(서식 적용본)다. 기존 `../md2docx/` 는 pandoc 기본 서식이며 그대로 둔다.

## 서식

- 표 헤더 `#D6E0EB` 배경·굵은 `#131416` 글씨, 격자선 `#CDD1D5`.
- 제목 `#063A74`(제목 2 는 밑줄), 코드 배경 `#F4F5F6`·왼쪽 선 `#8A949E`.
- 맑은 고딕 10pt, A4, 여백 2cm.
- 정부 디자인 시스템(KRDS) 팔레트 기준이며 표 열 폭은 내용 길이에 맞춘다.

## 다시 만들기

`../*.md` 를 고친 뒤:

```sh
_변환도구/build.sh "../JSA-PF-ST-003_PR 템플릿·Definition of Done.md" "JSA-PF-ST-003_PR 템플릿·Definition of Done.docx"
```

mermaid 블록이 있는 문서(DS-002, DS-003, OP-001)는 세 번째 인자로 그림 폴더를 넘긴다(예: `_변환도구/img/JSA-PF-DS-003_아키텍처 문서`, 안에 `1.png`, `2.png` ... 순서대로). 그림은 기존 `md2docx/` 변환본에서 뽑아 둔 것이라, 다이어그램을 바꿨다면 새로 렌더링해서 교체해야 한다.

## 도구 구성

- `reference-A.docx`: 스타일 템플릿(`make_reference.py` 로 pandoc 기본 템플릿에서 생성).
- `tablewidths.lua`: 표 열 폭 계산 필터.
- `mermaid.lua`: mermaid 블록을 렌더링된 PNG 로 교체.
