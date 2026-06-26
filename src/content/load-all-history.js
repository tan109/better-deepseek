/**
 * Load All History — intercepts DeepSeek's `/api/v0/chat/history_messages`
 * API call (via the injected script's fetch/XHR patch) to obtain every message
 * in the session along with accurate `accumulated_token_usage`.
 *
 * Default: off (opt-in via settings.loadAllHistoryOnSession).
 * When enabled, runs automatically on session open AND on-demand before
 * export / select-all / price recalculation.
 */

import state from "./state.js";

const HISTORY_MSGS_TIMEOUT = 10000;

let pendingPromise = null;

export function isLoadInProgress() {
  return pendingPromise !== null;
}

/**
 * Get the current session ID from the URL.
 * @returns {string|null}
 */
function getSessionId() {
  const match = String(location.href || "").match(/\/chat\/s\/([^/?#]+)/);
  return match ? match[1] : null;
}

/**
 * Wait for the `bds:history-msgs-loaded` event.
 * @param {string} sessionId
 * @returns {Promise<boolean>} true if data was loaded
 */
function waitForHistoryData(sessionId) {
  return new Promise((resolve) => {
    const handler = (event) => {
      let detail = event.detail;
      if (typeof detail === "string") {
        try { detail = JSON.parse(detail); } catch { return; }
      }
      if (detail?.sessionId === sessionId) {
        window.removeEventListener("bds:history-msgs-loaded", handler);
        resolve(true);
      }
    };
    window.addEventListener("bds:history-msgs-loaded", handler);
    setTimeout(() => {
      window.removeEventListener("bds:history-msgs-loaded", handler);
      resolve(false);
    }, HISTORY_MSGS_TIMEOUT);
  });
}

/**
 * Load all messages for the current session via the history_messages API.
 *
 * Returns an array of API message objects (or null if unavailable):
 *   { message_id, role, fragments, accumulated_token_usage, ... }
 *
 * Callers can pass these to `collectMessagesFromApi()` in exporter.js.
 */
export async function loadAllHistory() {
  if (pendingPromise) {
    return pendingPromise;
  }

  const sessionId = getSessionId();
  if (!sessionId) {
    return null;
  }

  if (state.chatMessagesBySession.has(sessionId)) {
    const messages = state.chatMessagesBySession.get(sessionId);
    return messages.length > 0 ? messages : null;
  }

  pendingPromise = (async () => {
    window.dispatchEvent(new CustomEvent("bds:request-history-msgs", {
      detail: JSON.stringify({ sessionId })
    }));

    const loaded = await waitForHistoryData(sessionId);

    if (loaded && state.chatMessagesBySession.has(sessionId)) {
      const messages = state.chatMessagesBySession.get(sessionId);
      return messages.length > 0 ? messages : null;
    }

    return null;
  })();

  try {
    return await pendingPromise;
  } finally {
    pendingPromise = null;
  }
}
