from pathlib import Path

f = Path(".github/workflows/release.yml")
content = f.read_text()

old = """on:
  push:
    branches:
      - main
    tags:
      - "v\""""

new = """on:
  push:
    tags:
      - "v\""""

if old in content:
    content = content.replace(old, new)
    f.write_text(content)
    print("Fixed: release.yml now only triggers on tags")
else:
    print("Pattern not found — checking current state:")
    print(content[:200])
