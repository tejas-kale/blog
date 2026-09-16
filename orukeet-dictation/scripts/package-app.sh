#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
swift build -c release --product orukeet-dictation
BIN="$(swift build -c release --show-bin-path)/orukeet-dictation"
APP="$ROOT/dist/OrukeetDictation.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/OrukeetDictation"
cp "$ROOT/server/orukeet_server.py" "$APP/Contents/Resources/orukeet_server.py"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key>
  <string>com.tejaskale.orukeet-dictation</string>
  <key>CFBundleName</key>
  <string>OrukeetDictation</string>
  <key>CFBundleExecutable</key>
  <string>OrukeetDictation</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSUIElement</key>
  <true/>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSMicrophoneUsageDescription</key>
  <string>Orukeet dictation records while you hold the hotkey, then types the transcript into the focused app.</string>
</dict>
</plist>
PLIST
echo "Built $APP"
echo "Grant Microphone and Accessibility to OrukeetDictation, then launch it after install-orukeet.sh."
