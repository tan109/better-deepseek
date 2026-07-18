from pathlib import Path

TARGET = Path("src/content/scanner.js")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''  const handler = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      if (!document.contains(editor)) { devLog("Cmd", "Enter ignored — editor detached"); return }
      const dropdown = document.querySelector(".bds-cmd-dropdown")
      if (dropdown) { devLog("Cmd", "Enter ignored — dropdown open"); return }
      const text = getEditorText(editor)
      devLog("Cmd", "Enter pressed, text=", text.substring(0, 80).replace(/\\n/g, "\\\\n"))
      if (isSlashCommandText(text)) {
        {'''

new = '''  const handler = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      if (!document.contains(editor)) { devLog("Cmd", "Enter ignored — editor detached"); return }
      const text = getEditorText(editor)
      devLog("Cmd", "Enter pressed, text=", text.substring(0, 80).replace(/\\n/g, "\\\\n"))
      // Only defer to the autocomplete dropdown (for arrow-key navigation of
      // suggestions) when the typed text is NOT already a complete,
      // well-formed slash command -- Autocomplete.svelte has no keydown
      // handling of its own, so bailing here unconditionally previously
      // swallowed Enter presses with nothing else picking them up whenever
      // a short exact-match command (e.g. "/compress") kept the dropdown
      // open, silently letting the raw text fall through to DeepSeek.
      const dropdown = document.querySelector(".bds-cmd-dropdown")
      if (dropdown && !isSlashCommandText(text)) { devLog("Cmd", "Enter ignored — dropdown open"); return }
      if (isSlashCommandText(text)) {
        {'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Fixed dropdown-open guard to not swallow Enter for already-complete commands")
