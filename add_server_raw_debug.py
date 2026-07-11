from pathlib import Path

TARGET = Path("termux-server/bds_server.py")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"ok": False, "error": f"Invalid JSON body: {e}"})
            return'''

new = '''        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length > 0 else b"{}"
        print(f"[bds-server][DEBUG] raw_body={raw_body!r}", file=sys.stderr)
        print(f"[bds-server][DEBUG] headers={dict(self.headers)}", file=sys.stderr)

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"ok": False, "error": f"Invalid JSON body: {e}"})
            return

        print(f"[bds-server][DEBUG] parsed data={data!r}", file=sys.stderr)'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Added raw request debug logging to server")
