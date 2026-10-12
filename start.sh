#!/usr/bin/env bash
# One command to run Kairos on your machine:   ./start.sh
# Makes a virtualenv, installs Kairos with Whisper captions, checks ffmpeg, starts the app and opens it.
set -e
cd "$(dirname "$0")"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is missing. Install it first:"
  echo "  macOS:   brew install ffmpeg"
  echo "  Ubuntu:  sudo apt install ffmpeg"
  echo "  Windows: winget install ffmpeg"
  exit 1
fi
PY=$(command -v python3 || command -v python)
[ -n "$PY" ] || { echo "Python 3.10+ is missing: https://python.org/downloads"; exit 1; }

if [ ! -d .venv ]; then
  echo "Setting up (one time, a few minutes)…"
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate
pip install -q -e ".[all]" 2>&1 | grep -v "already satisfied" || true

PORT=${PORT:-8787}
URL="http://localhost:$PORT"
echo "Kairos is starting at $URL"
( sleep 2; command -v open >/dev/null && open "$URL" || command -v xdg-open >/dev/null && xdg-open "$URL" || true ) &
exec python -m kairos serve --port "$PORT"
