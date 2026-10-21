#!/bin/sh
# usage: build.sh <input.md> <output.docx> [imgdir]   (A안: 연한 청회색 헤더 + 남색 제목)
D="$(cd "$(dirname "$0")" && pwd)"
pandoc -f gfm-gfm_auto_identifiers -t docx --syntax-highlighting=none \
  --reference-doc="$D/reference-A.docx" --lua-filter="$D/tablewidths.lua" --lua-filter="$D/mermaid.lua" \
  ${3:+-M imgdir="$3"} "$1" -o "$2"
