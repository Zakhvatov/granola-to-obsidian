#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
WORKFLOW="$HOME/Library/Services/Granola to Obsidian.workflow"

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installer uses macOS Services and requires macOS." >&2
  exit 1
fi

for tool in python3 curl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool" >&2
    exit 1
  fi
done

mkdir -p "$BIN"
install -m 755 "$ROOT/bin/granola-import" "$BIN/granola-import"

mkdir -p "$WORKFLOW/Contents/Resources"
cp "$ROOT/service/Info.plist" "$WORKFLOW/Contents/Info.plist"

python3 - "$ROOT/service/document.wflow" "$WORKFLOW/Contents/document.wflow" "$BIN/granola-import" <<'PY'
import plistlib
import sys

src, dst, script = sys.argv[1], sys.argv[2], sys.argv[3]
with open(src, "rb") as fh:
    wf = plistlib.load(fh)
wf["actions"][0]["action"]["ActionParameters"]["COMMAND_STRING"] = script + "\n"
with open(dst, "wb") as fh:
    plistlib.dump(wf, fh, fmt=plistlib.FMT_XML)
PY

cp "$WORKFLOW/Contents/document.wflow" "$WORKFLOW/Contents/Resources/document.wflow"
plutil -lint "$WORKFLOW/Contents/Info.plist" "$WORKFLOW/Contents/document.wflow" >/dev/null

cat <<EOF
Installed:
  $BIN/granola-import
  $WORKFLOW

Next step (one time):
  System Settings -> Keyboard -> Keyboard Shortcuts... -> Services
  -> "Granola to Obsidian" -> add a shortcut (for example Control+Option+Command+G)

Then in Granola: Share -> Copy link, press the shortcut, and the note
appears in your Obsidian vault.
EOF
