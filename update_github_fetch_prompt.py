from pathlib import Path

TARGET = Path("src/lib/constants.js")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''  "When using <BDS:AUTO:REQUEST_GITHUB_FETCH>owner/repo</BDS:AUTO:REQUEST_GITHUB_FETCH>:",
  "- Instructs the Better DeepSeek extension to automatically fetch a GitHub repository's content.",
  "- Use this when the user mentions a GitHub repo or when you need to see the full code context of a public repository.",
  "- You can provide the full URL (https://github.com/owner/repo) or just 'owner/repo'.",
  "- The extension will download the repo ZIP, extract text files, concatenate them into a single report, upload it to the chat, and prompt you to continue.",
  "- Only provide this tag as your full response. Do not explain you are doing it.",'''

new = '''  "When using <BDS:AUTO:REQUEST_GITHUB_FETCH>owner/repo</BDS:AUTO:REQUEST_GITHUB_FETCH>:",
  "- Instructs the Better DeepSeek extension to automatically fetch a GitHub repository's content.",
  "- Use this when the user mentions a GitHub repo or when you need to see the full code context of a public repository.",
  "- You can provide the full URL (https://github.com/owner/repo) or just 'owner/repo'.",
  "- If the user wants a SINGLE specific file rather than the whole repo (e.g. they name a file, paste a direct link to one, or only need one file's contents), provide the file's GitHub 'blob' URL instead, e.g. https://github.com/owner/repo/blob/branch/path/to/file.ext -- this fetches only that file directly, without downloading the whole repository.",
  "- Prefer the single-file blob URL whenever the user's need is scoped to one known file; only fetch the whole repo when broader context across multiple files is actually needed.",
  "- The extension will download the repo ZIP (or just the one file, for blob URLs), extract text files, concatenate them into a single report, upload it to the chat, and prompt you to continue.",
  "- Only provide this tag as your full response. Do not explain you are doing it.",'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Updated GitHub fetch prompt to mention single-file blob URL support")
