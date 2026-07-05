import sys
from pathlib import Path

TARGET = Path("src/background/index.js")
src = TARGET.read_text(encoding="utf-8")
original = src

listener_anchor = 'if (message.type === "bds-fetch-github-commits") {'
new_listener_block = '''if (message.type === "bds-fetch-github-file") {
    fetchGithubFile(
      message.owner,
      message.repo,
      message.path,
      message.branch,
      message.token,
    )
      .then((text) => {
        sendResponse({ ok: true, text });
      })
      .catch((error) => {
        sendResponse({
          ok: false,
          error: String(error && error.message ? error.message : error),
          status:
            error && Number.isFinite(error.status) ? Number(error.status) : null,
          authRejected: Boolean(error && error.authRejected),
          rateLimited: Boolean(error && error.rateLimited),
        });
      });
    return true;
  }

  '''

if listener_anchor not in src:
    sys.exit("listener anchor not found")
src = src.replace(listener_anchor, new_listener_block + listener_anchor, 1)

fn_anchor = "export async function fetchGithubCommits(owner, repo, branch, count, token) {"
new_fn = '''export async function fetchGithubFile(owner, repo, path, branch, token) {
  const safeOwner = String(owner || "").trim();
  const safeRepo = String(repo || "").trim();
  const safePath = String(path || "").trim();
  const safeBranch = String(branch || "").trim() || "main";
  const trimmedToken = String(token || "").trim();

  if (!safeOwner || !safeRepo || !safePath) {
    throw new Error("Missing owner, repo, or file path.");
  }

  const url = new URL(
    `https://api.github.com/repos/${safeOwner}/${safeRepo}/contents/${safePath}`,
  );
  url.searchParams.set("ref", safeBranch);

  const headers = buildGithubApiHeaders(trimmedToken);
  headers.Accept = "application/vnd.github.raw";

  const resp = await fetch(url.toString(), { headers });

  if (!resp.ok) {
    const bodyText = await resp.text();

    if (isGithubRateLimitResponse(resp, bodyText)) {
      throw createGithubFetchError(
        `GitHub API rate limit exceeded fetching ${safePath}`,
        { status: resp.status, rateLimited: true },
      );
    }

    if (resp.status === 401 || resp.status === 403) {
      throw createGithubFetchError(
        `GitHub rejected the supplied token for ${safePath}`,
        { status: resp.status, authRejected: true },
      );
    }

    throw createGithubFetchError(
      `GitHub returned ${resp.status} for ${safePath}`,
      { status: resp.status },
    );
  }

  return await resp.text();
}

'''

if fn_anchor not in src:
    sys.exit("fn anchor not found")
src = src.replace(fn_anchor, new_fn + fn_anchor, 1)

if src == original:
    sys.exit("no changes made")

Path("src/background/index.js.bak").write_text(original, encoding="utf-8")
TARGET.write_text(src, encoding="utf-8")
print("Patched src/background/index.js (backup at .bak)")
