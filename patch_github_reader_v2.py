import sys
from pathlib import Path

TARGET = Path("src/content/files/github-reader.js")
src = TARGET.read_text(encoding="utf-8")
original = src

old_block = '''  if (content === null) {
    // Private repo (token present) or the direct fetch above failed --
    // route through the background service worker, same as the ZIP path.
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${filePath}?ref=${branch}`;
    const result = await chrome.runtime.sendMessage({
      type: "bds-fetch-github-file",
      url: apiUrl,
      token: token || undefined,
    });

    if (!result || !result.ok) {
      throw buildGitHubFetchError(
        result,
        `Could not fetch ${filePath} from ${owner}/${repo}. Check the URL, branch, and (for private repos) your token.`
      );
    }

    // GitHub's contents API returns base64-encoded content.
    if (result.base64) {
      content = decodeURIComponentSafe(atob(result.base64.replace(/\\n/g, "")));
    } else if (typeof result.text === "string") {
      content = result.text;
    } else {
      throw new Error(`Unexpected response fetching ${filePath}.`);
    }
  }'''

new_block = '''  if (content === null) {
    // Private repo (token present) or the direct fetch above failed --
    // route through the background service worker, same as the ZIP path.
    const result = await chrome.runtime.sendMessage({
      type: "bds-fetch-github-file",
      owner,
      repo,
      path: filePath,
      branch,
      token: token || undefined,
    });

    if (!result || !result.ok || typeof result.text !== "string") {
      throw buildGitHubFetchError(
        result,
        `Could not fetch ${filePath} from ${owner}/${repo}. Check the URL, branch, and (for private repos) your token.`
      );
    }

    content = result.text;
  }'''

if old_block not in src:
    sys.exit("old block not found -- may already be patched, or content differs")
src = src.replace(old_block, new_block, 1)

if src == original:
    sys.exit("no changes made")

Path("src/content/files/github-reader.js.bak2").write_text(original, encoding="utf-8")
TARGET.write_text(src, encoding="utf-8")
print("Patched src/content/files/github-reader.js (backup at .bak2)")
