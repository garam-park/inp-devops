#!/usr/bin/env python3
"""moves.json 대로 git mv 한다. 이어서 경로 문자열(링크가 아닌 본문의 `docs/…` 언급, .gitignore, .gitattributes 등)을 치환한다.

사용: python3 apply-moves.py <저장소 루트> <moves.json>

- "move": true 인 항목만 옮긴다. 긴 old 부터(파일 → 폴더 순서가 되도록 json 순서를 그대로 쓴다).
- git 이 추적하는 것은 git mv. 폴더에 무시된 파일(node_modules, svn checkout 등)이 남으면 os.rename 으로 마저 옮긴다.
  통째로 무시된 폴더(docs/svn)는 git mv 가 실패하므로 os.rename 만 한다.
- 치환: git 추적 중인 텍스트 파일에서 old 가 경로 앞머리로 나온 곳(앞에 글자·`-`·`.`·`/` 가 없고 뒤에 글자·`-` 가 없는 곳)을
  new 로 바꾼다. "move": false 항목도 치환에는 쓴다. docs/sources/ 아래와 tasks/ 의 json 증적은 건드리지 않는다.
"""
import json
import os
import re
import subprocess
import sys

root = os.path.abspath(sys.argv[1])
moves = json.load(open(sys.argv[2], encoding="utf-8"))


def run(*args, check=True):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=check)


# 1. 이동
def is_tracked(rel):
    return run("ls-files", "--", rel).stdout.strip() != ""


def move_tree(old, new):
    """old 를 new 로 옮긴다. new 가 이미 있는 폴더면 자식마다 재귀한다(git mv 가 안으로 넣는 것을 막는다)."""
    old_abs, new_abs = os.path.join(root, old), os.path.join(root, new)
    if os.path.isdir(old_abs) and not os.path.islink(old_abs) and os.path.isdir(new_abs):
        for name in sorted(os.listdir(old_abs)):
            move_tree(os.path.join(old, name), os.path.join(new, name))
        if os.path.isdir(old_abs) and not os.listdir(old_abs):
            os.rmdir(old_abs)
        return
    os.makedirs(os.path.dirname(new_abs), exist_ok=True)
    if is_tracked(old):
        r = run("mv", "-k", old, new, check=False)
        if r.returncode != 0:
            print(f"git mv 실패: {old} → {new}\n{r.stderr}", file=sys.stderr)
            sys.exit(1)
        if os.path.lexists(old_abs):  # 폴더에 무시된 파일이 남은 경우
            move_tree(old, new)
    else:
        if os.path.lexists(new_abs):
            print(f"이미 있어 못 옮김: {new}", file=sys.stderr)
            return
        os.rename(old_abs, new_abs)


for m in moves:
    if not m.get("move"):
        continue
    old, new = m["old"].rstrip("/"), m["new"].rstrip("/")
    if not os.path.lexists(os.path.join(root, old)):
        print(f"skip (없음): {old}")
        continue
    tracked = is_tracked(old)
    move_tree(old, new)
    print(f"moved: {old} → {new}" + ("" if tracked else " (디스크만)"))

# 2. 빈 상위 폴더 정리 (.DS_Store 만 남은 경우 포함)
for m in moves:
    parent = os.path.dirname(os.path.join(root, m["old"].rstrip("/")))
    while parent != root and os.path.isdir(parent):
        rest = [n for n in os.listdir(parent) if n != ".DS_Store"]
        if rest:
            break
        for n in os.listdir(parent):
            os.remove(os.path.join(parent, n))
        os.rmdir(parent)
        print(f"rmdir: {os.path.relpath(parent, root)}")
        parent = os.path.dirname(parent)

# 3. 경로 문자열 치환
pairs = sorted(((m["old"].rstrip("/"), m["new"].rstrip("/")) for m in moves), key=lambda p: -len(p[0]))
exts = ("*.md", "*.sh", "*.json", "*.yml", "*.yaml", "*.py", "*.cjs", "*.js", "*.html", "*.toml",
        "*.txt", "*.ts", "*.tsx", ".gitignore", ".gitattributes")
files = [f for f in run("ls-files", "-z", "--", *exts).stdout.split("\0") if f]
skip = ("docs/sources/", "docs/대화-자료/", "docs/inbox/", "docs/partners/", "docs/references/", "tasks/")
n_files = 0
for rel in files:
    if rel.startswith(skip) and (not rel.startswith("tasks/") or rel.endswith(".json")):
        continue
    path = os.path.join(root, rel)
    try:
        text = open(path, encoding="utf-8", newline="").read()
    except UnicodeDecodeError:
        continue
    out = text
    for old, new in pairs:
        out = re.sub(r"(?<![\w\-./])" + re.escape(old) + r"(?![\w\-])", new.replace("\\", "\\\\"), out)
    if out != text:
        open(path, "w", encoding="utf-8", newline="").write(out)
        n_files += 1
print(f"치환한 파일: {n_files}")
