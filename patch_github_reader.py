import sys
from pathlib import Path

TARGET = Path("src/content/files/github-reader.js")
src = TARGET.read_text(encoding="utf-8")
original = src

# 1. Recognize /blob/branch/path URLs in parseGitHubUrl
old_parse = '''    if (parts[2] === "tree") {
      branch = parts.slice(3).join("/");
    }

    return { owner, repo, branch };'''

new_parse = '''    if (parts[2] === "tree") {
      branch = parts.slice(3).join("/");
    }

    let filePath = null;
    if (parts[2] === "blob" && parts.length > 4) {
      branch = parts[3];
      filePath = parts.slice(4).join("/");
    }

    return { owner, repo, branch, filePath };'''

if old_parse not in src:
    sys.exit("parseGitHubUrl anchor not found")
src = src.replace(old_parse, new_parse, 1)

# 2. Insert fetchGitHubFile() before fetchGitHubRepo()
anchor = 'export async function fetchGitHubRepo(repoUrl, onStatus = () => { }, options = {}) {'

new_fn = '''export async function fetchGitHubFile(owner, repo, branch, filePath, onStatus = () => { }, options = {}) {
  const token = String(
    typeof options.token === "string" ? options.token : ""
  ).trim();

  onStatus(`Fetching ${filePath}...`);

  let content = null;

  if (!token) {
    const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${filePath}`;
    try {
      const res = await fetch(rawUrl);
      if (res.ok) {
        content = await res.text();
      } else if (res.status === 404) {
        throw new Error(`File not found: ${filePath} (on branch ${branch}). Check the path and branch.`);
      }
    } catch (error) {
      if (error instanceof Error && error.message.startsWith("File not found")) {
        throw error;
      }
    }
  }

  if (content === null) {
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
  }

  onStatus("Creating file...");

  const fileName = filePath.split("/").pop() || `${repo}_file.txt`;
  const output =
    `Repository: ${owner}/${repo}/${branch}\\n` +
    `File: ${filePath}\\n` +
    `${"=".repeat(48)}\\n\\n` +
    content;

  const blob = new Blob([output], { type: "text/plain" });
  const file = new File([blob], fileName, { type: "text/plain" });
  Object.defineProperty(file, "bdsGitHub", {
    value: { owner, repo, branch, filePath, singleFile: true },
    configurable: true,
  });
  return file;
}

'''

if anchor not in src:
    sys.exit("fetchGitHubRepo anchor not found")
src = src.replace(anchor, new_fn + anchor, 1)

# 3. Short-circuit to fetchGitHubFile() when a filePath was parsed
old_body = '''  const { owner, repo, branch } = parsed;
  const token = String(
    typeof options.token === "string" ? options.token : ""
  ).trim();'''

new_body = '''  const { owner, repo, branch, filePath } = parsed;
  const token = String(
    typeof options.token === "string" ? options.token : ""
  ).trim();

  if (filePath) {
    return fetchGitHubFile(owner, repo, branch, filePath, onStatus, options);
  }'''

if old_body not in src:
    sys.exit("fetchGitHubRepo body anchor not found")
src = src.replace(old_body, new_body, 1)

if src == original:
    sys.exit("no changes made")

Path("src/content/files/github-reader.js.bak").write_text(original, encoding="utf-8")
TARGET.write_text(src, encoding="utf-8")
print("Patched src/content/files/github-reader.js (backup at .bak)")
