package com.betterdeepseek.app

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log

/**
 * Receives Termux RUN_COMMAND results via a PendingIntent.getService() callback.
 *
 * Every real working example of Termux's result-callback (StackOverflow samples,
 * termux-tasker's own GitHub issue threads) uses PendingIntent.getService()
 * targeting a dedicated Service, not PendingIntent.getBroadcast(). Multiple
 * attempts using a BroadcastReceiver here consistently failed to receive a
 * result bundle, so this matches the empirically-confirmed working pattern.
 *
 * Routes the result back into the currently-active WebViewBridge instance via
 * a static holder, since this Service and MainActivity run in the same
 * process (this targets our own app's component, not a cross-app IPC call),
 * so in-memory static state is safely shared.
 */
class TermuxResultReceiverService : Service() {

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            val requestId = intent?.getStringExtra(EXTRA_BDS_REQUEST_ID)
            val resultBundle = intent?.getBundleExtra("result")

            if (requestId.isNullOrEmpty()) {
                Log.w(TAG, "onStartCommand: missing requestId extra")
                return START_NOT_STICKY
            }

            val bridge = WebViewBridge.activeInstance
            if (bridge == null) {
                Log.w(TAG, "onStartCommand: no active WebViewBridge to deliver result to")
                return START_NOT_STICKY
            }

            if (resultBundle == null) {
                bridge.deliverTermuxResult(
                    requestId, ok = false, stdout = "", stderr = "", exitCode = null,
                    error = "Termux sent a result callback but no result bundle was found " +
                        "at the \"result\" key."
                )
                return START_NOT_STICKY
            }

            val stdout = resultBundle.getString("stdout") ?: ""
            val stderr = resultBundle.getString("stderr") ?: ""
            val exitCode = resultBundle.getInt("exitCode", -1)
            val err = resultBundle.getInt("err", 0)
            val errmsg = resultBundle.getString("errmsg")

            if (err != 0 || !errmsg.isNullOrBlank()) {
                bridge.deliverTermuxResult(
                    requestId, ok = false, stdout = stdout, stderr = stderr, exitCode = null,
                    error = errmsg?.takeIf { it.isNotBlank() } ?: "Termux internal error code $err"
                )
            } else {
                bridge.deliverTermuxResult(
                    requestId, ok = true, stdout = stdout, stderr = stderr,
                    exitCode = exitCode, error = null
                )
            }
        } catch (t: Throwable) {
            Log.e(TAG, "onStartCommand failed", t)
        } finally {
            stopSelf(startId)
        }
        return START_NOT_STICKY
    }

    companion object {
        private const val TAG = "BdsTermuxResultService"
        const val EXTRA_BDS_REQUEST_ID = "bds_request_id"
    }
}
