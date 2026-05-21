/**
 * Content script entry point.
 *
 * Orchestrates initialization of all subsystems:
 * - Wait for document.body
 * - Load state from chrome.storage
 * - Inject the MAIN-world hook script
 * - Set up bridge events
 * - Mount Svelte UI
 * - Bind storage change listener
 * - Start URL watcher
 * - Observe chat DOM
 * - Schedule initial scan
 * - Push config to injected script
 */

import "bds-platform-globals";
import "../styles/content.css";

import state from "./state.js";
import { loadStateFromStorage, bindStorageChangeListener } from "./storage.js";
import { injectHookScript, setupBridgeEvents, pushConfigToPage } from "./bridge.js";
import { mountUi } from "./ui/mount.js";
import { observeChatDom, scheduleScan, startUrlWatcher } from "./scanner.js";
import { initSidebarMenuInjector } from "./ui/SidebarMenuInjector.js";
import { initSidebarSearch } from "./ui/SidebarSearch.js";
import { checkPendingExport } from "./tools/pending-export.js";
import { initPricing } from "../lib/pricing.js";
import { startStatusMonitor } from "./status-monitor.js";
import { startThemeWatcher } from "./theme.js";
import { i18n } from "../lib/i18n.svelte.js";
import { remoteConfig, REMOTE_CONFIG_EVENT, detectModelType } from "../lib/remote-config.svelte.js";

const CONTENT_BOOTSTRAP_KEY = "__bdsContentBootstrapped";

if (!window[CONTENT_BOOTSTRAP_KEY]) {
  window[CONTENT_BOOTSTRAP_KEY] = true;
  init().catch((error) => {
    console.error("[BetterDeepSeek] Init error:", error);
  });
}

async function init() {
  await waitForBody();
  await loadStateFromStorage();

  // Initialize localization locale
  i18n.init(state.settings.syncLocale ? null : state.settings.locale);

  // Silently check for language updates on startup
  if (typeof chrome !== "undefined" && chrome.runtime?.sendMessage) {
    chrome.runtime.sendMessage({ type: "BDS_UPDATE_LANGUAGES" });
  }

  injectHookScript();
  setupBridgeEvents();
  mountUi();
  bindStorageChangeListener();
  startUrlWatcher();
  observeChatDom();
  initSidebarMenuInjector();
  initSidebarSearch();
  scheduleScan();
  checkPendingExport();
  pushConfigToPage();
  startStatusMonitor();
  startThemeWatcher();

  // Keep state.remoteConfig in sync when the RemoteConfigManager updates
  window.addEventListener(REMOTE_CONFIG_EVENT, () => {
    state.remoteConfig = remoteConfig.raw;
  });

  // Debug API — listen for requests from MAIN-world injected script
  window.addEventListener("bds:debug-api-request", (e) => {
    let detail = e.detail;
    if (typeof detail === "string") { try { detail = JSON.parse(detail); } catch { return; } }
    const { id, method, args } = detail || {};
    let result;
    try {
      switch (method) {
        case "getRaw":   result = remoteConfig.raw; break;
        case "getFlag":  result = remoteConfig.getFlag(args?.[0]); break;
        case "getConfig": result = remoteConfig.getConfig(args?.[0]); break;
        case "applyRemote":   remoteConfig.applyRemote(args?.[0]); result = remoteConfig.raw; break;
        case "replaceRemote": remoteConfig.replaceRemote(args?.[0]); result = remoteConfig.raw; break;
        case "resetToBuiltin": remoteConfig.resetToBuiltin(); result = remoteConfig.raw; break;
        case "detectModel": result = detectModelType(); break;
        case "toggleDebugPanel":
          window.dispatchEvent(new CustomEvent("bds:toggle-debug-panel"));
          result = true;
          break;
      }
    } catch (err) { result = { __error: err.message }; }
    window.dispatchEvent(new CustomEvent("bds:debug-api-response", {
      detail: JSON.stringify({ id, result }),
    }));
  });

  // Dynamically fetch pricing and update embedded fallback
  initPricing().then((pricing) => {
    if (pricing && pricing.models) {
      state.embeddedPricing = pricing;
      scheduleScan();
    }
  }).catch(() => {});
}

async function waitForBody() {
  if (document.body) {
    return;
  }

  await new Promise((resolve) => {
    const observer = new MutationObserver(() => {
      if (document.body) {
        observer.disconnect();
        resolve();
      }
    });
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  });
}
