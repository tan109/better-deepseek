from pathlib import Path

TARGET = Path("termux-server/bds_server.py")
src = TARGET.read_text(encoding="utf-8")
original = src

old_import = '''import http.server
import json
import os
import secrets
import subprocess
import sys'''
new_import = '''import http.server
import json
import os
import secrets
import shlex
import subprocess
import sys'''
if old_import not in src:
    raise SystemExit("import anchor not found")
src = src.replace(old_import, new_import, 1)

old_exec = '''        argv = [command] + [str(a) for a in args]

        try:
            result = subprocess.run(
                argv,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )'''

new_exec = '''        # Run through an actual shell (bash) rather than exec'ing the
        # command directly, so shell builtins (echo, cd, etc.), pipes,
        # redirects, and PATH resolution all behave the way a normal
        # terminal command would.
        full_command = shlex.join([command] + [str(a) for a in args])

        try:
            result = subprocess.run(
                ["bash", "-c", full_command],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )'''

if old_exec not in src:
    raise SystemExit("exec anchor not found")
src = src.replace(old_exec, new_exec, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Server now runs commands through bash -c instead of direct exec")
