from pathlib import Path

TARGET = Path("src/lib/constants.js")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''  "- If the user asks you to run a shell command, check a file, or do something only possible via a real terminal, and no [BDS:TERMUX_RESULT] for that request is already present in this conversation, tell them to run it themselves via /termux <command> rather than fabricating output.",
  "",
  "When using <BDS:AUTO:SEARCH>query</BDS:AUTO:SEARCH>:",'''

new = '''  "- If the user asks you to run a shell command, check a file, or do something only possible via a real terminal, and no [BDS:TERMUX_RESULT] for that request is already present in this conversation, tell them to run it themselves via /termux <command> rather than fabricating output.",
  "- CRITICAL: never write the literal text /github, /termux, or /termux-config as your own output expecting it to execute -- these only work when the human physically types them into the composer and presses Enter/Send. If your response contains that text, nothing happens; it just sits there as inert words. To fetch a repo/file yourself, use the real <BDS:AUTO:REQUEST_GITHUB_FETCH> tag as documented above. To suggest the user run one of these commands, phrase it as plain instruction, e.g. 'you can run /termux ls to check that' -- do not present it as something you are about to do.",
  "",
  "When using <BDS:AUTO:SEARCH>query</BDS:AUTO:SEARCH>:",'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Clarified that the model must never literally emit slash-command text expecting it to execute")
