from pathlib import Path

TARGET = Path("android/app/src/main/java/com/betterdeepseek/app/WebViewBridge.kt")
src = TARGET.read_text(encoding="utf-8")
original = src

# 1. Add PackageManager import
old_imports = '''import android.content.ContentValues
import android.content.Context
import android.content.Intent'''
new_imports = '''import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager'''
if old_imports not in src:
    raise SystemExit("imports anchor not found")
src = src.replace(old_imports, new_imports, 1)

# 2. Add onRunTermux callback property after onPickFiles
old_prop = '''    @Volatile var onPickFiles: ((mode: String, requestId: String) -> Unit)? = null

    /**
     * Returns the last DeepSeek page theme'''
new_prop = '''    @Volatile var onPickFiles: ((mode: String, requestId: String) -> Unit)? = null

    /**
     * Set by MainActivity to launch a Termux RUN_COMMAND intent. Called from
     * [handleRunTermuxCommand] after pre-flight checks (Termux + Termux:API
     * installed, RUN_COMMAND permission granted) pass.
     */
    @Volatile var onRunTermux:
            ((requestId: String, command: String, args: List<String>, workdir: String?) -> Unit)? = null

    /**
     * Returns the last DeepSeek page theme'''
if old_prop not in src:
    raise SystemExit("onPickFiles anchor not found")
src = src.replace(old_prop, new_prop, 1)

# 3. Register dispatch case
old_dispatch = '''                "bds-fetch-github-file" -> handleFetchGithubFile(payload, response)'''
new_dispatch = '''                "bds-fetch-github-file" -> handleFetchGithubFile(payload, response)
                "bds-run-termux-command" -> handleRunTermuxCommand(payload, response)'''
if old_dispatch not in src:
    raise SystemExit("dispatch anchor not found")
src = src.replace(old_dispatch, new_dispatch, 1)

# 4. Insert handleRunTermuxCommand + deliverTermuxResult before handleFetchGithubCommits
anchor = '''    private fun handleFetchGithubCommits(payload: JSONObject, response: JSONObject) {'''
new_fn = '''    /**
     * Termux RUN_COMMAND dispatcher (manual /termux slash command only --
     * see termux-runner.js and commands/executor.js; there is no AI-tag
     * path that reaches this method).
     *
     * Pre-flight checks run synchronously and return an immediate
     * { ok: false, error } if they fail. If they pass, [onRunTermux] is
     * invoked and this returns { ok: true, pending: true, requestId }
     * synchronously; the real result arrives later via a CustomEvent
     * dispatched by [deliverTermuxResult].
     */
    private fun handleRunTermuxCommand(payload: JSONObject, response: JSONObject) {
        val command = payload.optString("command").trim()
        if (command.isEmpty()) {
            response.put("ok", false)
            response.put("error", "No command provided.")
            return
        }

        val args = mutableListOf<String>()
        val argsArr = payload.optJSONArray("args")
        if (argsArr != null) {
            for (i in 0 until argsArr.length()) {
                args.add(argsArr.optString(i))
            }
        }
        val workdir = payload.optString("workdir").takeIf { it.isNotEmpty() }

        val pm = context.packageManager
        if (!isPackageInstalled(pm, "com.termux")) {
            response.put("ok", false)
            response.put(
                "error",
                "Termux app is not installed. Install it from F-Droid or " +
                    "https://github.com/termux/termux-app/releases first."
            )
            return
        }
        if (!isPackageInstalled(pm, "com.termux.api")) {
            response.put("ok", false)
            response.put(
                "error",
                "Termux:API app is not installed. Install it from F-Droid or " +
                    "https://github.com/termux/termux-api/releases, then run " +
                    "`pkg install termux-api` inside Termux."
            )
            return
        }

        val granted = context.checkSelfPermission(
            "com.termux.permission.RUN_COMMAND"
        ) == PackageManager.PERMISSION_GRANTED
        if (!granted) {
            response.put("ok", false)
            response.put(
                "error",
                "RUN_COMMAND permission is not granted. Install Termux first, " +
                    "then reinstall Better DeepSeek. Also ensure " +
                    "`allow-external-apps=true` is set in " +
                    "`~/.termux/termux.properties` inside Termux (then restart Termux)."
            )
            return
        }

        val handler = onRunTermux
        if (handler == null) {
            response.put("ok", false)
            response.put("error", "Termux launcher is not initialized.")
            return
        }

        val requestId = generateTermuxRequestId()
        handler.invoke(requestId, command, args, workdir)

        response.put("ok", true)
        response.put("pending", true)
        response.put("requestId", requestId)
    }

    private fun isPackageInstalled(pm: PackageManager, packageName: String): Boolean =
        try {
            @Suppress("DEPRECATION")
            pm.getPackageInfo(packageName, 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }

    private fun generateTermuxRequestId(): String {
        val ts = java.lang.Long.toString(System.currentTimeMillis(), 36)
        val rnd = (1..8).map { ('a'..'z').random() }.joinToString("")
        return "tx_${ts}_$rnd"
    }

    /**
     * Called by MainActivity when the Termux:API result PendingIntent fires.
     * Dispatches a page CustomEvent named
     * `__bds_native_termux_result_<requestId>`, mirroring the pickFiles
     * async-delivery pattern.
     */
    internal fun deliverTermuxResult(
        requestId: String,
        ok: Boolean,
        stdout: String,
        stderr: String,
        exitCode: Int?,
        error: String?
    ) {
        val safeId = requestId.filter { it.isLetterOrDigit() || it == '_' || it == '-' }.take(64)
        if (safeId.isEmpty()) return

        val payload = JSONObject().apply {
            put("ok", ok)
            put("stdout", stdout)
            put("stderr", stderr)
            if (exitCode != null) put("exitCode", exitCode)
            if (error != null) put("error", error)
        }
        val payloadQuoted = JSONObject.quote(payload.toString())
        val script =
            "(function(){try{var d=JSON.parse($payloadQuoted);" +
                "window.dispatchEvent(new CustomEvent('__bds_native_termux_result_$safeId'," +
                "{detail:d}));}" +
                "catch(e){console.error('[BDS] termux result delivery failed',e)}})();"
        postScript(script)
    }

    private fun handleFetchGithubCommits(payload: JSONObject, response: JSONObject) {'''
if anchor not in src:
    raise SystemExit("handleFetchGithubCommits anchor not found")
src = src.replace(anchor, new_fn, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Patched WebViewBridge.kt for Termux integration")
