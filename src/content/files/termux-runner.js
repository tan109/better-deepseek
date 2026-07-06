/**
 * Termux Command Runner
 *
 * Sends a shell command to the native bridge (which invokes Termux:API's
 * RunCommandService via the RUN_COMMAND intent), then awaits the result
 * delivered as a CustomEvent -- since the intent is asynchronous, the bridge
 * returns { ok: true, pending: true, requestId } synchronously and the
 * actual { ok, stdout, stderr, exitCode } arrives later via a
 * `__bds_native_termux_result_<requestId>` CustomEvent dispatched by
 * WebViewBridge.deliverTermuxResult().
 *
 * SECURITY: This module is ONLY called from the /termux slash command in
 * commands/executor.js. There is no <BDS:AUTO:...> tag and no AI-output
 * path that can reach this code. The AI cannot trigger shell execution.
 *
 * Browser-extension build: chrome.runtime.sendMessage routes to
 * src/background/index.js, which returns
 *   { ok: false, error: "Termux integration is Android-only." }
 */

const TIMEOUT_MS = 60_000;

export async function runTermuxCommand(command, args, workdir) {
  if (!command || typeof command !== "string") {
    return { ok: false, error: "No command provided." };
  }

  let init;
  try {
    init = await chrome.runtime.sendMessage({
      type: "bds-run-termux-command",
      command,
      args: Array.isArray(args) ? args : [],
      workdir: workdir || null,
    });
  } catch (err) {
    return {
      ok: false,
      error: `Bridge error: ${err && err.message ? err.message : String(err)}`,
    };
  }

  if (!init) {
    return { ok: false, error: "Empty bridge response." };
  }
  if (!init.ok) {
    return init;
  }
  if (!init.pending || !init.requestId) {
    return init;
  }

  const requestId = String(init.requestId);
  const eventName = `__bds_native_termux_result_${requestId}`;

  return new Promise((resolve) => {
    let settled = false;

    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      window.removeEventListener(eventName, handler);
      resolve({
        ok: false,
        error:
          `Termux command did not return within ${TIMEOUT_MS / 1000}s. ` +
          "If this is unexpected, ensure `allow-external-apps=true` is set " +
          "in `~/.termux/termux.properties` inside Termux (then restart Termux).",
      });
    }, TIMEOUT_MS);

    function handler(e) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      window.removeEventListener(eventName, handler);
      const detail = e && e.detail;
      if (detail && typeof detail === "object") {
        resolve(detail);
      } else {
        resolve({ ok: false, error: "Empty result from Termux bridge." });
      }
    }

    window.addEventListener(eventName, handler);
  });
}

export function formatTermuxResult(command, args, result) {
  const argsStr = (args || []).join(" ");
  const fullCommand = argsStr ? `${command} ${argsStr}` : command;

  if (!result || !result.ok) {
    const err = (result && result.error) || "Unknown error";
    return (
      `<BetterDeepSeek>\n` +
      `[BDS:TERMUX_RESULT] /termux ${fullCommand}\n` +
      `status: FAILED\n` +
      `error: ${err}\n` +
      (result && result.stderr ? `\n--- stderr ---\n${result.stderr}\n` : "") +
      `</BetterDeepSeek>`
    );
  }

  const exitCode = result.exitCode != null ? result.exitCode : "?";
  const stdout = result.stdout || "";
  const stderr = result.stderr || "";

  return (
    `<BetterDeepSeek>\n` +
    `[BDS:TERMUX_RESULT] /termux ${fullCommand}\n` +
    `exit_code: ${exitCode}\n` +
    `--- stdout ---\n${stdout || "(empty)"}\n` +
    `--- stderr ---\n${stderr || "(empty)"}\n` +
    `</BetterDeepSeek>`
  );
}
