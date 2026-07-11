from pathlib import Path

TARGET = Path("termux-server/bds_server.py")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''        try:
            result = subprocess.run(
                ["bash", "-c", full_command],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )'''

new = '''        # Use the fixed, known Termux bash path instead of relying on
        # PATH lookup -- avoids ambiguity across however this server
        # process happened to be started (tmux, different shell contexts,
        # etc. can carry different PATH values).
        bash_path = "/data/data/com.termux/files/usr/bin/bash"
        if not os.path.exists(bash_path):
            bash_path = "bash"  # fall back to PATH lookup as a last resort

        try:
            result = subprocess.run(
                [bash_path, "-c", full_command],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Server now uses the fixed Termux bash path instead of PATH lookup")
