/**
 * Search Reader
 * Fetches DuckDuckGo Lite search results via background script,
 * parses the HTML, and returns formatted markdown results.
 * Supports optional deepFetch to auto-read content from top N results.
 */

import { fetchAndConvertWebPage } from "./web-reader.js";

const SEARCH_URL = "https://lite.duckduckgo.com/lite/?q=";
const MAX_DEEP_FETCH = 5;

/**
 * Extract the actual destination URL from a DDG click-track redirect link.
 * DDG wraps real URLs in: //duckduckgo.com/l/?uddg=<encoded_url>&rut=...
 */
function extractUrlFromDdgLink(href) {
  if (!href) return "";
  try {
    const url = new URL(href.startsWith("//") ? "https:" + href : href);
    const uddg = url.searchParams.get("uddg");
    return uddg ? decodeURIComponent(uddg) : href;
  } catch {
    return href;
  }
}

/**
 * Parse DDG Lite HTML and extract search results.
 * Current DDG Lite structure (tables, no table.result class):
 *   <table border="0">
 *     <tr>              ← link row
 *       <td valign="top">1.&nbsp;</td>
 *       <td><a class="result-link" href="//...?uddg=...">Title</a></td>
 *     </tr>
 *     <tr>              ← snippet row (may be absent)
 *       <td>&nbsp;&nbsp;&nbsp;</td>
 *       <td class="result-snippet">snippet</td>
 *     </tr>
 *     <tr>              ← URL row
 *       <td>&nbsp;&nbsp;&nbsp;</td>
 *       <td><span class="link-text">example.com/page</span></td>
 *     </tr>
 *     <tr><td>&nbsp;</td><td>&nbsp;</td></tr>  ← spacer
 *   </table>
 */
function parseSearchResults(html) {
  const doc = new DOMParser().parseFromString(html, "text/html");
  const links = doc.querySelectorAll("a.result-link");
  const results = [];

  for (const link of links) {
    const linkRow = link.closest("tr");
    if (!linkRow) continue;

    const title = link.textContent.trim();
    const rawHref = link.getAttribute("href") || "";
    const url = extractUrlFromDdgLink(rawHref);

    let snippet = "";
    let nextRow = linkRow.nextElementSibling;

    // The next row may be the snippet row, the URL row, or absent
    if (nextRow) {
      const snippetEl = nextRow.querySelector(".result-snippet");
      if (snippetEl) {
        snippet = snippetEl.textContent.trim();
        nextRow = nextRow.nextElementSibling;
      }
    }

    results.push({ title, url, snippet });
  }

  return results;
}

/**
 * Format search results as a markdown document.
 */
function formatSearchResults(query, results) {
  const lines = [];
  lines.push(`# Search Results: ${query}`);
  lines.push("");
  lines.push(`> ${results.length} results found via DuckDuckGo`);
  lines.push("");
  lines.push("---");
  lines.push("");

  results.forEach((result, index) => {
    const rank = index + 1;
    lines.push(`## ${rank}. ${result.title}`);
    lines.push("");
    lines.push(`> ${result.snippet}`);
    lines.push("");
    lines.push(`**URL:** ${result.url}`);
    lines.push("");
    lines.push("---");
    lines.push("");
  });

  return lines.join("\n");
}

/**
 * Format deep-fetched page content as an appendix.
 */
function formatDeepFetchContent(title, url, markdown) {
  const lines = [];
  lines.push("");
  lines.push("=".repeat(64));
  lines.push(`## Page Content: ${title}`);
  lines.push(`**Source:** ${url}`);
  lines.push("=".repeat(64));
  lines.push("");
  lines.push(markdown);
  lines.push("");
  lines.push("---");
  lines.push("");
  return lines.join("\n");
}

/**
 * Search the web via DuckDuckGo Lite.
 *
 * @param {string} query - Search query
 * @param {number} [deepFetch=0] - Number of top results to also fetch full content for
 * @param {(status: string) => void} [onStatus] - Optional status callback
 * @returns {Promise<File>} A markdown file with search results
 */
export { parseSearchResults, formatSearchResults, formatDeepFetchContent, extractUrlFromDdgLink };

export async function searchWeb(query, deepFetch = 0, onStatus = () => {}) {
  const trimmedQuery = String(query || "").trim();
  if (!trimmedQuery) {
    throw new Error("Search query is empty.");
  }

  const safeDeepFetch = Math.max(0, Math.min(MAX_DEEP_FETCH, Number(deepFetch) || 0));

  onStatus("Searching DuckDuckGo...");

  let html;
  try {
    const response = await chrome.runtime.sendMessage({
      type: "bds-fetch-url",
      url: SEARCH_URL + encodeURIComponent(trimmedQuery),
    });

    if (!response || !response.ok) {
      throw new Error(response?.error || "Search request failed.");
    }
    html = response.html;
  } catch (err) {
    throw new Error(`Search failed: ${err.message}`);
  }

  onStatus("Parsing search results...");
  const results = parseSearchResults(html);

  if (results.length === 0) {
    throw new Error("No search results found for query: " + trimmedQuery);
  }

  let output = formatSearchResults(trimmedQuery, results);

  if (safeDeepFetch > 0) {
    onStatus(`Fetching content from top ${safeDeepFetch} results...`);
    const urlsToFetch = results.slice(0, safeDeepFetch);

    for (let i = 0; i < urlsToFetch.length; i++) {
      const result = urlsToFetch[i];
      try {
        onStatus(`Reading page ${i + 1}/${safeDeepFetch}: ${result.title}`);
        const file = await fetchAndConvertWebPage(result.url, () => {});
        const markdown = await file.text();
        output += formatDeepFetchContent(result.title, result.url, markdown);
      } catch (err) {
        output += formatDeepFetchContent(
          result.title,
          result.url,
          `*(Failed to fetch page content: ${err.message})*`
        );
      }
    }
  }

  onStatus("Creating file...");
  const blob = new Blob([output], { type: "text/markdown" });
  const safeFilename = trimmedQuery
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "-")
    .slice(0, 50) + "-search.md";

  return new File([blob], safeFilename, { type: "text/markdown" });
}
