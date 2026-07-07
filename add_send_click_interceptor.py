from pathlib import Path

TARGET = Path("src/content/scanner.js")
src = TARGET.read_text(encoding="utf-8")
original = src

# 1. Import findSendButton
old_import = '''import { tryExecuteRawInput } from "./commands/executor.js"'''
new_import = '''import { tryExecuteRawInput } from "./commands/executor.js"
import { findSendButton } from "./auto.js"'''
if old_import not in src:
    raise SystemExit("import anchor not found")
src = src.replace(old_import, new_import, 1)

# 2. Add module-level flag
old_vars = '''let autocompleteInstance = null
let commandsHelpInstance = null
let cmdSetupTimer = 0
let currentEditor = null
let currentKeydownHandler = null'''
new_vars = '''let autocompleteInstance = null
let commandsHelpInstance = null
let cmdSetupTimer = 0
let currentEditor = null
let currentKeydownHandler = null
let commandSendClickListenerInstalled = false'''
if old_vars not in src:
    raise SystemExit("vars anchor not found")
src = src.replace(old_vars, new_vars, 1)

# 3. Extract shared text-reading helper + add click interceptor installer,
#    right before retrySetupCommandListener.
old_fn_start = '''function retrySetupCommandListener() {'''
new_fn_start = '''function getEditorText(editor) {
  const t = (editor.tagName || "").toLowerCase()
  return t === "textarea" || t === "input" ? editor.value : (editor.textContent || "")
}

function isSlashCommandText(text) {
  if (!text.startsWith("/")) return false
  const hasSpaceAfterCmd = /^\\/[a-z0-9_]+\\s/.test(text)
  return hasSpaceAfterCmd || /^\\/[a-z0-9_]+$/.test(text)
}

/**
 * Mobile keyboards' on-screen Send button often does not dispatch a real
 * "keydown Enter" event, so the Enter-key interceptor below never fires when
 * the user taps Send instead of pressing return. This delegated, capturing
 * click listener catches that case by checking (at click time) whether the
 * click landed on the current composer send button, independent of any
 * specific editor/button DOM node surviving re-renders. Installed once,
 * ever — not tied to setupCommandListener's per-editor lifecycle.
 */
function installCommandSendClickInterceptor() {
  if (commandSendClickListenerInstalled) return
  commandSendClickListenerInstalled = true
  document.addEventListener("click", (e) => {
    const sendBtn = findSendButton()
    if (!sendBtn) return
    if (!(e.target === sendBtn || sendBtn.contains(e.target))) return
    const editor = findComposerEditor()
    if (!editor) return
    const text = getEditorText(editor)
    if (!isSlashCommandText(text)) return

    e.preventDefault()
    e.stopPropagation()
    if (e.stopImmediatePropagation) e.stopImmediatePropagation()

    const ok = tryExecuteRawInput(text)
    devLog("Cmd", "Send-button click execute cmd result=", ok)
    if (ok) {
      const tag = (editor.tagName || "").toLowerCase()
      if (tag === "textarea" || tag === "input") editor.value = ""
      else editor.textContent = ""
      editor.dispatchEvent(new Event("input", { bubbles: true }))
    }
  }, true)
}

function retrySetupCommandListener() {'''
if old_fn_start not in src:
    raise SystemExit("retrySetupCommandListener anchor not found")
src = src.replace(old_fn_start, new_fn_start, 1)

# 4. Reuse getEditorText in the existing keydown handler
old_text_extract = '''      const text = (() => { const t = (editor.tagName || "").toLowerCase(); return t === "textarea" || t === "input" ? editor.value : (editor.textContent || "") })()'''
new_text_extract = '''      const text = getEditorText(editor)'''
if old_text_extract not in src:
    raise SystemExit("text-extract anchor not found")
src = src.replace(old_text_extract, new_text_extract, 1)

old_pattern_check = '''      if (text.startsWith("/")) {
        const hasSpaceAfterCmd = /^\\/[a-z0-9_]+\\s/.test(text)
        if (hasSpaceAfterCmd || /^\\/[a-z0-9_]+$/.test(text)) {'''
new_pattern_check = '''      if (isSlashCommandText(text)) {
        {'''
if old_pattern_check not in src:
    raise SystemExit("pattern-check anchor not found")
src = src.replace(old_pattern_check, new_pattern_check, 1)

# 5. Call the installer once from setupCommandListener
old_call_site = '''function setupCommandListener(editor) {
  devLog("Cmd", "setupCommandListener called, editor=", !!editor, "autoInst=", !!autocompleteInstance, "tag=", editor?.tagName, "id=", editor?.id)'''
new_call_site = '''function setupCommandListener(editor) {
  devLog("Cmd", "setupCommandListener called, editor=", !!editor, "autoInst=", !!autocompleteInstance, "tag=", editor?.tagName, "id=", editor?.id)
  installCommandSendClickInterceptor()'''
if old_call_site not in src:
    raise SystemExit("call-site anchor not found")
src = src.replace(old_call_site, new_call_site, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Added send-button click interceptor for slash commands")
