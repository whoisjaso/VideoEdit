#!/usr/bin/env bash
# Create a render-ready Remotion project with the 8.3 build (template/ + every asset in the right public/ path).
# Usage: bash scripts/new_episode.sh /path/to/project
#   then: cp OUTDIR/{cut.mp4,fg.webm} project/public/ep/ ; cp OUTDIR/{captions.json,edl.json} project/src/ep/
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)"; P="$1"; [ -n "$P" ] || { echo "usage: new_episode.sh PROJECT_DIR"; exit 1; }
mkdir -p "$P" && cp -r "$SK/template/." "$P/"
mkdir -p "$P/public/ep" "$P/public/sfx" "$P/public/logos"
python3 -c "import numpy" 2>/dev/null || pip install -q numpy
(cd "$P" && python3 "$SK/scripts/synth_sfx.py" >/dev/null)   # synth fallbacks first (tapestop, boom, ...)
cp -r "$SK/assets/sfx/." "$P/public/sfx/"                                 # then the real sounds win: root, ios/, ui/, pack3-6/
cp "$SK/assets/sfx/library.json" "$P/src/lib/sfx-library.json"          # <Hit> reads ids, leads and volumes from here
cp "$SK/assets/logos/"*.svg "$P/public/logos/"
cp "$SK/assets/avatar.png" "$P/public/ep/avatar.png"
(cd "$P" && npm i --silent --no-audit --no-fund)
echo "project ready: $P"
