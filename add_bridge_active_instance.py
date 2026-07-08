from pathlib import Path

TARGET = Path("android/app/src/main/java/com/betterdeepseek/app/WebViewBridge.kt")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''class WebViewBridge(
        private val context: Context,
        httpClient: OkHttpClient? = null,
        private val githubApiBaseUrl: String = DEFAULT_GITHUB_API_BASE_URL,
) {

    private val prefs: SharedPreferences ='''

new = '''class WebViewBridge(
        private val context: Context,
        httpClient: OkHttpClient? = null,
        private val githubApiBaseUrl: String = DEFAULT_GITHUB_API_BASE_URL,
) {

    init {
        activeInstance = this
    }

    private val prefs: SharedPreferences ='''

if old not in src:
    raise SystemExit("class-header anchor not found")
src = src.replace(old, new, 1)

old_companion = '''    companion object {
        private const val TAG = "BdsWebViewBridge"'''
new_companion = '''    companion object {
        /**
         * Static reference to the most recently constructed WebViewBridge,
         * so same-process components with no direct reference to it (like
         * TermuxResultReceiverService, reached via a PendingIntent callback)
         * can still deliver results back into the WebView.
         */
        @Volatile var activeInstance: WebViewBridge? = null

        private const val TAG = "BdsWebViewBridge"'''
if old_companion not in src:
    raise SystemExit("companion anchor not found")
src = src.replace(old_companion, new_companion, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Added WebViewBridge.activeInstance static holder")
