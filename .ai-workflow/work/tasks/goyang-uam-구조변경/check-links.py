#!/usr/bin/env python3
"""git 추적 중인 Markdown 의 상대 링크가 실제 파일을 가리키는지 본다.

사용: python3 check-links.py <저장소 루트> > links.txt
출력: "<md 파일>: <링크 대상>" 한 줄씩, 없는 대상만. 정렬돼 있어 이동 전후 diff 가 된다.
http(s)·mailto·#앵커만 있는 링크·코드 블록 안은 건너뛴다. 서브모듈 안은 git ls-files 에 안 나와 자동으로 빠진다.
"""
import os
import re
import subprocess
import sys
from urllib.parse import unquote

root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
files = subprocess.run(
    ["git", "-C", root, "ls-files", "-z", "--", "*.md"],
    capture_output=True, check=True,
).stdout.decode().split("\0")
link_re = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
fence_re = re.compile(r"^\s*(```|~~~)")

missing = []
for rel in files:
    if not rel:
        continue
    path = os.path.join(root, rel)
    try:
        text = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    in_fence = False
    for line in text.splitlines():
        if fence_re.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        for target in link_re.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            dest = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(dest):
                missing.append(f"{rel}: {target}")

for m in sorted(set(missing)):
    print(m)
print(f"# missing: {len(set(missing))} (files scanned: {len([f for f in files if f])})", file=sys.stderr)
