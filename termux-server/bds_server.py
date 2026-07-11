#!/usr/bin/env python3
"""
Better DeepSeek Termux server.

Runs inside Termux, listens on 127.0.0.1 only, and executes shell commands
sent by the Better DeepSeek app's /termux slash command.

SECURITY NOTE: Android does not sandbox 127.0.0.1 per-app -- any other app
on this device can reach this port too. A shared secret token is required
on every request (Authorization: Bearer <token>) to prevent that. The same
token must be set in the app via the /termux-config <token> command.

Usage:
    python3 bds_server.py

The token is read from the TERMUX_BDS_TOKEN environment variable if set,
otherwise a random token is generated on first run and saved to
~/.bds_server_token (printed on every startup so you can copy it into
/termux-config).

To keep this running in the background, use tmux or a similar tool, e.g.:
    tmux new -s bds-server
    python3 bds_server.py
    # detach with Ctrl+B then D; reattach later with: tmux attach -t bds-server
"""

import http.server
import json
import os
import secrets
import shlex
import subprocess
import sys

TOKEN_FILE = os.path.expanduser("~/.bds_server_token")
DEFAULT_PORT = 8817
COMMAND_TIMEOUT_SECONDS = 55  # stay under the app's 60s HTTP read timeout


def load_or_create_token():
    env_token = os.environ.get("TERMUX_BDS_TOKEN", "").strip()
    if env_token:
        return env_token

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            existing = f.read().strip()
            if existing:
                return existing

    new_token = secrets.token_urlsafe(24)
    with open(TOKEN_FILE, "w") as f:
        f.write(new_token)
    os.chmod(TOKEN_FILE, 0o600)
    return new_token


TOKEN = load_or_create_token()
PORT = int(os.environ.get("TERMUX_BDS_PORT", DEFAULT_PORT))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[bds-server] " + (fmt % args) + "\n")

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/run":
            self._send_json(404, {"ok": False, "error": "Unknown endpoint."})
            return

        auth = self.headers.get("Authorization", "")
        expected = f"Bearer {TOKEN}"
        if auth != expected:
            self._send_json(401, {"ok": False, "error": "Invalid or missing token."})
            return

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"ok": False, "error": f"Invalid JSON body: {e}"})
            return

        command = str(data.get("command", "")).strip()
        args = data.get("args") or []
        workdir = data.get("workdir") or None

        if not command:
            self._send_json(400, {"ok": False, "error": "No command provided."})
            return
        if not isinstance(args, list):
            self._send_json(400, {"ok": False, "error": "args must be a list of strings."})
            return

        # Run through an actual shell (bash) rather than exec'ing the
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
            )
            self._send_json(200, {
                "ok": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exitCode": result.returncode,
            })
        except FileNotFoundError:
            self._send_json(200, {
                "ok": False,
                "error": f"Command not found: {command}",
            })
        except subprocess.TimeoutExpired:
            self._send_json(200, {
                "ok": False,
                "error": f"Command timed out after {COMMAND_TIMEOUT_SECONDS}s.",
            })
        except Exception as e:
            self._send_json(200, {
                "ok": False,
                "error": f"Execution error: {e}",
            })


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[bds-server] Listening on http://127.0.0.1:{PORT}/run")
    print(f"[bds-server] Token (set this in the app via /termux-config <token>):")
    print(f"[bds-server]   {TOKEN}")
    print(f"[bds-server] Token also saved to: {TOKEN_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[bds-server] Shutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
