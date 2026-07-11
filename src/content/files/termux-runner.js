/**
 * Termux Command Runner (HTTP server variant)
 *
 * Sends a shell command to a small HTTP server running inside Termux
 * (127.0.0.1 only) instead of using the Android RUN_COMMAND intent, which
 * proved unreliable across multiple attempts (see git history / commit
 * messages around 2026-07-08 for the full RUN_COMMAND debugging trail).
 *
 * SECURITY: Android does not sandbox 127.0.0.1 per-app -- any app on the
 * device can reach the same loopback port. A shared secret token
 * (appState.settings.termuxServerToken, set via /termux-config) is
 * required and sent as an Authorization header; the native bridge should
 * refuse to proceed without one configured.
 *
 * SECURITY: This module is ONLY called from the /termux slash command in
 * commands/executor.js. There is no <BDS:AUTO:...> tag and no AI-output
 * path that can reach this code. The AI cannot trigger shell execution.
 *
 * Browser-extension build: chrome.runtime.sendMessage routes to
 * src/background/index.js, which returns
 *   { ok: false, error: "Termux integration is Android-only." }
 */

import appState from "../state.js";

export async function runTermuxCommand(command, args, workdir) {
  if (!command || typeof command !== "string") {
    return { ok: false, error: "No command provided." };
  }

  const token = String(appState.settings.termuxServerToken || "").trim();
  if (!token) {
    return {
      ok: false,
      error:
        "No Termux server token configured. Run /termux-config <token> first " +
        "(the token must match TERMUX_BDS_TOKEN in the server script running inside Termux).",
    };
  }

  const port = Number(appState.settings.termuxServerPort) || 8817;

  let result;
  try {
    result = await chrome.runtime.sendMessage({
      type: "bds-run-termux-command",
      command,
      args: Array.isArray(args) ? args : [],
      workdir: workdir || null,
      token,
      port,
    });
  } catch (err) {
    return {
      ok: false,
      error: `Bridge error: ${err && err.message ? err.message : String(err)}`,
    };
  }

  if (!result) {
    return { ok: false, error: "Empty bridge response." };
  }
  return result;
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
