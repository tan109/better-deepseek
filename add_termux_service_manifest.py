from pathlib import Path

TARGET = Path("android/app/src/main/AndroidManifest.xml")
src = TARGET.read_text(encoding="utf-8")
original = src

old = '''        <!-- FileProvider for legacy (<=API 28) ACTION_VIEW handoff after a
             blob download writes into the app's external Downloads folder. -->
        <provider'''

new = '''        <!-- Receives Termux RUN_COMMAND results via PendingIntent.getService().
             Not exported -- only Termux itself (via the PendingIntent we hand
             it, which carries our app's identity) can trigger this. -->
        <service
            android:name=".TermuxResultReceiverService"
            android:exported="false" />

        <!-- FileProvider for legacy (<=API 28) ACTION_VIEW handoff after a
             blob download writes into the app's external Downloads folder. -->
        <provider'''

if old not in src:
    raise SystemExit("anchor not found")
src = src.replace(old, new, 1)

if src == original:
    raise SystemExit("no changes made")

TARGET.write_text(src, encoding="utf-8")
print("Registered TermuxResultReceiverService in AndroidManifest.xml")
