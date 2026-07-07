from pathlib import Path

TARGET = Path("android/app/src/main/java/com/betterdeepseek/app/WebViewBridge.kt")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''        val granted = context.checkSelfPermission(
            "com.termux.permission.RUN_COMMAND"
        ) == PackageManager.PERMISSION_GRANTED
        if (!granted) {
            response.put("ok", false)
            response.put(
                "error",
                "RUN_COMMAND permission is not granted. Install Termux first, " +
                    "then reinstall Better DeepSeek. Also ensure " +
                    "`allow-external-apps=true` is set in " +
                    "`~/.termux/termux.properties` inside Termux (then restart Termux)."
            )
            return
        }

        val handler = onRunTermux'''

new = '''        // RUN_COMMAND is a dangerous-level permission requiring a runtime
        // request/dialog, not an install-time auto-grant -- MainActivity's
        // onRunTermux handler owns the check + request flow, since only an
        // Activity can show a permission dialog. This bridge method just
        // hands off to it.
        val handler = onRunTermux'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Removed permission check from WebViewBridge (moved to MainActivity)")
