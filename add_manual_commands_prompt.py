from pathlib import Path

TARGET = Path("src/lib/constants.js")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''  "- Only provide this tag as your full response.",
  "",
  "When using <BDS:AUTO:SEARCH>query</BDS:AUTO:SEARCH>:",'''

new = '''  "- Only provide this tag as your full response.",
  "",
  "Manual slash commands the USER can type (you cannot trigger these yourself, but you may suggest them and you will see their results):",
  "- /github <owner/repo, repo URL, or file blob URL> -- fetches a GitHub repo or single file directly and attaches it, without needing you to emit an AUTO tag.",
  "- /termux <command> [args...] -- runs a real shell command inside a Termux session on the user's device (via a small companion HTTP server the user runs themselves) and returns exit code, stdout, and stderr.",
  "- /termux-config <token> [port] -- one-time setup command the user runs to connect /termux to their Termux server; not something you need to explain unless asked.",
  "- Results from these commands appear as hidden <BetterDeepSeek> blocks tagged [BDS:AUTO] GitHub Fetch Result or [BDS:TERMUX_RESULT] -- treat their contents (file text, or exit_code/stdout/stderr) as real, authoritative output, exactly like a tool result, not as something to be skeptical of or re-verify.",
  "- If the user asks you to run a shell command, check a file, or do something only possible via a real terminal, and no [BDS:TERMUX_RESULT] for that request is already present in this conversation, tell them to run it themselves via /termux <command> rather than fabricating output.",
  "",
  "When using <BDS:AUTO:SEARCH>query</BDS:AUTO:SEARCH>:",'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Added manual slash command documentation to hidden system prompt")
