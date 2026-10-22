#!/usr/bin/env python3
"""폴더 이동 전에 md 의 상대 링크를 이동 후 경로로 고쳐 쓴다.

사용: python3 rewrite-links.py <저장소 루트> <moves.json> [--dry-run]

moves.json: [{"old": "docs/decisions", "new": "docs/ADRs", "move": true}, ...]
  old/new 는 저장소 루트 기준 경로(파일 또는 폴더). 긴 old 부터 맞춘다. move 는 이 스크립트에서 쓰지 않는다.

동작: git 추적 중인 md 마다 (1) 그 파일이 이동 후 어디로 가는지, (2) 각 링크가 지금 가리키는 파일이 이동 후 어디로
가는지를 구해, 새 위치 기준 상대 링크로 다시 쓴다. http(s)·mailto·#앵커만·코드 블록·코드 스팬·저장소 밖은 건너뛴다.
docs/sources/ 아래(원자료)는 고치지 않는다. 이동 전에 돌려야 한다(파일 위치로 옛 경로를 안다).
"""
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote, unquote

root = os.path.abspath(sys.argv[1])
moves = json.load(open(sys.argv[2], encoding="utf-8"))
dry = "--dry-run" in sys.argv
pairs = sorted(((m["old"].rstrip("/"), m["new"].rstrip("/")) for m in moves), key=lambda p: -len(p[0]))
SKIP_PREFIXES = ("docs/sources/", "docs/대화-자료/", "docs/inbox/", "docs/partners/", "docs/references/")


def map_path(p):
    for old, new in pairs:
        if p == old or p.startswith(old + "/"):
            return new + p[len(old):]
    return p


link_re = re.compile(r"(\]\(\s*<?)([^)\s>]+)(>?(?:\s+\"[^\"]*\")?\s*\))")
fence_re = re.compile(r"^\s*(```|~~~)")
code_span_re = re.compile(r"`[^`]*`")

files = [f for f in subprocess.run(["git", "-C", root, "ls-files", "-z", "--", "*.md"],
                                   capture_output=True, check=True).stdout.decode().split("\0") if f]
changed_files = 0
changed_links = 0
for rel in files:
    if rel.startswith(SKIP_PREFIXES):
        continue
    path = os.path.join(root, rel)
    try:
        text = open(path, encoding="utf-8", newline="").read()
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    new_rel = map_path(rel)
    old_dir = os.path.dirname(rel)
    new_dir = os.path.dirname(new_rel)
    counter = {"n": 0}

    def fix(m):
        global changed_links
        target = m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            return m.group(0)
        tpath, sep, anchor = target.partition("#")
        if not tpath:
            return m.group(0)
        encoded = "%" in tpath
        tdec = unquote(tpath)
        old_abs = os.path.normpath(os.path.join(old_dir, tdec))
        if old_abs.startswith(".."):
            return m.group(0)
        new_abs = map_path(old_abs)
        new_link = os.path.relpath(new_abs, new_dir) if new_dir else new_abs
        if tdec.startswith("./") and not new_link.startswith("."):
            new_link = "./" + new_link
        if new_link == tdec:
            return m.group(0)
        counter["n"] += 1
        changed_links += 1
        out = quote(new_link, safe="/") if encoded else new_link
        return m.group(1) + out + sep + anchor + m.group(3)

    lines = text.split("\n")
    in_fence = False
    for i, line in enumerate(lines):
        if fence_re.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        parts = code_span_re.split(line)
        spans = code_span_re.findall(line)
        parts = [link_re.sub(fix, p) for p in parts]
        rebuilt = parts[0]
        for s, p in zip(spans, parts[1:]):
            rebuilt += s + p
        lines[i] = rebuilt
    if counter["n"]:
        changed_files += 1
        if not dry:
            open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
print(f"files: {changed_files}, links rewritten: {changed_links}{' (dry-run)' if dry else ''}", file=sys.stderr)
