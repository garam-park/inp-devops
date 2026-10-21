#!/bin/sh
# usage: build.sh <input.md> <output.docx> [imgdir]   (A안: 연한 청회색 헤더 + 남색 제목)
# pandoc 으로 변환한 뒤 bake_tables.py 로 표·코드 서식을 직접 넣는다(Drive 미리보기 등 스타일을 무시하는 뷰어 대응).
D="$(cd "$(dirname "$0")" && pwd)"
pandoc -f gfm-gfm_auto_identifiers -t docx --syntax-highlighting=none \
  --reference-doc="$D/reference-A.docx" --lua-filter="$D/tablewidths.lua" --lua-filter="$D/mermaid.lua" \
  ${3:+-M imgdir="$3"} "$1" -o - | python3 "$D/bake_tables.py" - "$2"
