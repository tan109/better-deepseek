from pathlib import Path

TARGET = Path("src/content/auto.js")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''function findSendButton() {'''
new = '''export function findSendButton() {'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Exported findSendButton from auto.js")
