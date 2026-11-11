#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
APP="$HOME/Applications/Granola to Obsidian.app"
WORKFLOW="$HOME/Library/Services/Granola to Obsidian.workflow"
PB=/usr/libexec/PlistBuddy

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installer uses macOS Services and requires macOS." >&2
  exit 1
fi

for tool in python3 curl osacompile; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool" >&2
    exit 1
  fi
done

mkdir -p "$BIN"
install -m 755 "$ROOT/bin/granola-import" "$BIN/granola-import"

# A Service inherits the privacy permissions of whichever app is frontmost when
# it fires, so a script started straight from Automator loses vault access as
# soon as that app has none. A bundle gets its own identity instead, and a shell
# script as CFBundleExecutable does not: macOS attributes it to the interpreter.
# So the bundle is a compiled AppleScript applet that only calls the CLI. It is a
# regular app on purpose: a background-only one cannot show the macOS prompt that
# grants access to Documents the first time it runs.
LAUNCHER="$(mktemp -t granola-import).applescript"
cat > "$LAUNCHER" <<APPLESCRIPT
on run
	try
		do shell script quoted form of "$BIN/granola-import"
	end try
end run
APPLESCRIPT

rm -rf "$APP"
mkdir -p "$(dirname "$APP")"
osacompile -o "$APP" "$LAUNCHER"
rm -f "$LAUNCHER"

plist_set() {
  "$PB" -c "Set :$1 $3" "$APP/Contents/Info.plist" 2>/dev/null ||
    "$PB" -c "Add :$1 $2 $3" "$APP/Contents/Info.plist"
}

plist_set CFBundleIdentifier string com.github.zakhvatov.granola-to-obsidian
plist_set CFBundleName string "Granola to Obsidian"
plist_set CFBundleDisplayName string "Granola to Obsidian"
plutil -lint "$APP/Contents/Info.plist" >/dev/null

codesign --force --sign - "$APP" >/dev/null 2>&1 ||
  echo "warning: could not sign $APP, macOS may ask for access again" >&2

mkdir -p "$WORKFLOW/Contents/Resources"
cp "$ROOT/service/Info.plist" "$WORKFLOW/Contents/Info.plist"

python3 - "$ROOT/service/document.wflow" "$WORKFLOW/Contents/document.wflow" "$APP" <<'PY'
import plistlib
import sys

src, dst, app = sys.argv[1], sys.argv[2], sys.argv[3]
with open(src, "rb") as fh:
    wf = plistlib.load(fh)
wf["actions"][0]["action"]["ActionParameters"]["COMMAND_STRING"] = f'/usr/bin/open "{app}"\n'
with open(dst, "wb") as fh:
    plistlib.dump(wf, fh, fmt=plistlib.FMT_XML)
PY

cp "$WORKFLOW/Contents/document.wflow" "$WORKFLOW/Contents/Resources/document.wflow"
plutil -lint "$WORKFLOW/Contents/Info.plist" "$WORKFLOW/Contents/document.wflow" >/dev/null

cat <<EOF
Installed:
  $BIN/granola-import
  $APP
  $WORKFLOW

Next steps (one time):
  1. System Settings -> Privacy & Security -> Full Disk Access -> "+"
     -> add "$APP". Needed while the vault lives in Documents, Desktop,
     Downloads or iCloud Drive.
  2. System Settings -> Keyboard -> Keyboard Shortcuts... -> Services
     -> "Granola to Obsidian" -> add a shortcut (for example
     Control+Option+Command+G).

Then in Granola: Share -> Copy link, press the shortcut, and the note
appears in your Obsidian vault.
EOF
