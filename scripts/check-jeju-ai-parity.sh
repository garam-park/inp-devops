#!/usr/bin/env bash
# jeju-ai 프로토타입(Jeju-subsidence-AI)과 제품 저장소(jeju-ai-saas-be)의 파리티를 확인한다.
#
# 2026-10-19 에 프로토타입이 jeju-ai-saas-be · jeju-ai-saas-fe 로 나뉘고 그 뒤로 프로토타입은
# 동결되어 있다. 그래서 다음 둘이 어긋날 수 있다.
#
#   1. 레이어 자료 — 프로토타입 app/public/data 와 제품 data/ 는 같은 내용이어야 한다.
#   2. 파이썬 도구 — 프로토타입 tools/*.py 와 제품 pipeline/*.py 는 같은 프로그램이어야 한다.
#      경로·환경변수 차이(아래 '남는 차이')만 남아야 한다.
#
# 원본(제품 저장소)이 바뀌면 프로토타입도 따라야 한다. 이 검사가 그 사실을 알려 준다.
#
# 돌리기: mise run check:parity
#
# 기대 차이(allowed diff)는 scripts/jeju-ai-parity/expected/ 에 있다. 원본을 고쳐(expected 를
# 갱신하지 않고) 넘기면 이 검사가 실패한다 — 그게 알람이다.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# 기본값은 이 저장소의 서브모듈 경로다. worktree 등 다른 곳을 볼 때는 환경변수로 넘긴다.
#   JEJU_AI_PROTO_DIR  JEJU_AI_BE_DIR  JEJU_AI_PARITY_EXPECTED
PROTO="${JEJU_AI_PROTO_DIR:-$ROOT/projects/jeju-ai/apps/jeju-subsidence-ai}"
BE="${JEJU_AI_BE_DIR:-$ROOT/projects/jeju-ai/apps/jeju-ai-saas-be}"
EXPECTED="${JEJU_AI_PARITY_EXPECTED:-$ROOT/scripts/jeju-ai-parity/expected}"

# 제품 저장소와 공유하는 파이썬 파일 — 파일 이름이 두 저장소에서 같다
SHARED_FILES="gislib.py build_data.py run_index.py geocode_excavation.py"

fail=0

# ── 0. 필요한 자료가 있는가 ──────────────────────────────────────────────
for d in "$PROTO/tools" "$PROTO/app/public/data" "$BE/pipeline" "$BE/data"; do
  if [ ! -d "$d" ]; then
    echo "!! 필요한 폴더가 없다: $d"
    echo "   서브모듈을 받아라 — git submodule update --init <경로>"
    exit 2
  fi
done

# ── 1. 레이어 자료 파리티 ───────────────────────────────────────────────
# catalog.json 은 프로토타입 전용이다(제품은 목록을 스토리지에서 훑어 만든다).
data_diff="$(diff -rq --exclude=catalog.json "$PROTO/app/public/data" "$BE/data" 2>&1)"
if [ -z "$data_diff" ]; then
  echo "✓ 레이어 자료 — 프로토타입과 제품이 같다"
else
  echo "✗ 레이어 자료가 다르다"
  echo "$data_diff" | sed 's/^/   /'
  fail=1
fi

# ── 2. 파이썬 도구 파리티 ───────────────────────────────────────────────
for f in $SHARED_FILES; do
  if [ ! -f "$PROTO/tools/$f" ] || [ ! -f "$BE/pipeline/$f" ]; then
    echo "!! 한쪽에만 있는 파일이다: $f"
    fail=1
    continue
  fi
  if [ ! -f "$EXPECTED/$f.diff" ]; then
    echo "!! 기대 파일이 없다: $EXPECTED/$f.diff"
    fail=1
    continue
  fi
  actual="$(diff -u --label "a/tools/$f" --label "b/pipeline/$f" "$PROTO/tools/$f" "$BE/pipeline/$f")"
  expected="$(cat "$EXPECTED/$f.diff")"
  if [ "$actual" = "$expected" ]; then
    echo "✓ $f — 남는 차이가 기대와 같다"
  else
    echo "✗ $f — 원본이 바뀌었거나 프로토타입이 따라오지 않았다"
    echo "   기대와 다른 부분:"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/   /' | head -40
    fail=1
  fi
done

# ── 3. 기준이 된 파일 목록이 맞는가 ─────────────────────────────────────
# 새 파이썬 파일이 두 저장소에 따로 생기면 여기가 그걸 알아채야 한다.
proto_files="$(ls "$PROTO/tools" | grep '\.py$' | sort | tr '\n' ' ')"
echo "· 프로토타입 tools/ 의 파이썬 파일: $proto_files"
echo "· 공유 파일 목록(여기 있음): $SHARED_FILES"
echo "· 나머지 파일은 프로토타입 전용이거나 FE(jeju-ai-saas-fe/tools)의 것이라 여기서는 다루지 않는다"

if [ "$fail" -eq 0 ]; then
  echo "파리티 점검 통과"
else
  echo "파리티 어긋남 — 원본(jeju-ai-saas-be)을 고쳤다면 프로토타입에도 옮기고 expected 를 갱신하라"
fi
exit "$fail"
