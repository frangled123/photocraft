#!/usr/bin/env bash
# Compile Apple's appearance-aware icon before signing the app bundle.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP="${1:?Usage: compile-icon.sh /path/to/Iride.app}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
xcrun actool --compile "$TMP" --platform macosx --minimum-deployment-target 11.0 \
  --app-icon Iride --output-partial-info-plist "$TMP/icon-info.plist" \
  --output-format human-readable-text "$ROOT/assets/app-icon/Iride.icon"
# The system reads Assets.car for native appearances; ICNS remains a legacy fallback.
cp "$TMP/Assets.car" "$APP/Contents/Resources/Assets.car"
# Keep all legacy ICNS sizes through 1024 px; actool emits only the smaller fallbacks.
cp "$ROOT/assets/app-icon/photocraft.icns" "$APP/Contents/Resources/Iride.icns"
plutil -replace CFBundleIconName -string Iride "$APP/Contents/Info.plist"
plutil -replace CFBundleIconFile -string Iride "$APP/Contents/Info.plist"

# Carry the original code licences and the fork artwork notice with the native bundle.
cp "$ROOT/LICENSE-MIT" "$ROOT/LICENSE-APACHE" "$APP/Contents/Resources/"
cp "$ROOT/assets/app-icon/LICENSE.txt" "$APP/Contents/Resources/LICENSE-ribbon.txt"
