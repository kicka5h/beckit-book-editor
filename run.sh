#!/bin/bash
set -e

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# Install/update dependencies
pip install -e . --quiet
pip install flet --quiet

# ── Optional PDF-generation dependencies ──────────────────────────────────────
# pandoc and pdflatex are required only for Generate PDF.  Install them via
# Homebrew if missing.  Skipped gracefully when Homebrew is not available.

_need_pandoc=0
_need_mactex=0

command -v pandoc &>/dev/null || _need_pandoc=1

# pdflatex may be in /Library/TeX/texbin even when not yet on PATH
if ! command -v pdflatex &>/dev/null && ! [ -x /Library/TeX/texbin/pdflatex ]; then
  _need_mactex=1
fi

if [ "$_need_pandoc" -eq 1 ] || [ "$_need_mactex" -eq 1 ]; then
  if ! command -v brew &>/dev/null; then
    echo "WARNING: Homebrew not found — skipping automatic dependency install."
    echo "  For PDF export, install pandoc and MacTeX manually, then re-run run.sh:"
    echo "    https://brew.sh"
  else
    if [ "$_need_pandoc" -eq 1 ]; then
      echo "Installing pandoc (required for PDF export)..."
      brew install pandoc
    fi
    if [ "$_need_mactex" -eq 1 ]; then
      echo "Installing mactex-no-gui (required for PDF export, ~300 MB one-time download)..."
      brew install --cask mactex-no-gui
      # Add TeX binaries to PATH for the remainder of this session
      export PATH="/Library/TeX/texbin:$PATH"
    fi
  fi
fi

# Patch the Flet viewer's Info.plist so the macOS menu bar shows "Beckit"
# instead of "Flet". The viewer is cached in ~/.flet/bin/ and may be
# re-downloaded when the flet version changes, so we patch on every launch.
FLET_BIN_DIR="$HOME/.flet/bin"
if [ -d "$FLET_BIN_DIR" ]; then
  for flet_app in "$FLET_BIN_DIR"/*/Flet.app/Contents/Info.plist; do
    if [ -f "$flet_app" ]; then
      /usr/libexec/PlistBuddy -c "Set :CFBundleName Beckit" "$flet_app" 2>/dev/null || true
      /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName Beckit" "$flet_app" 2>/dev/null \
        || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string Beckit" "$flet_app" 2>/dev/null || true
    fi
  done
fi

# Run the app
python3 -m book_editor
