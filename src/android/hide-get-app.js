/**
 * Hides the "Get App" promotional button injected by chat.deepseek.com on mobile viewports.
 * Installed by src/platform/globals-android.js when the Android content bundle starts.
 *
 * Detection is text-based ("Get App" span) and only requires a button-like ancestor
 * so it survives DeepSeek's dynamic tag/class churn.
 * The MutationObserver stays alive for the lifetime of the page so SPA navigations that
 * re-insert the button are caught automatically.
 */
export function hideGetAppButton() {
  if (window.__bdsGetAppObserver) return;

  function getHideTarget(label) {
    const control = label.closest?.("button, .ds-button, [role='button']");
    if (!control) return null;
    return control.matches?.(".ds-button") ? control : (control.parentElement || control);
  }

  function hideButton() {
    const spans = document.querySelectorAll("span");
    for (const span of spans) {
      if (span.textContent.trim() !== "Get App") continue;
      const target = getHideTarget(span);
      if (target) {
        target.style.display = "none";
        console.log("[BDS] Hidden Get App container");
      }
    }
  }

  hideButton();

  const observer = new MutationObserver(hideButton);
  observer.observe(document.body, { subtree: true, childList: true });
  window.__bdsGetAppObserver = observer;
}
