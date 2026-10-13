#!/usr/bin/env bash
# skills-sync.sh — Jason's account skills (claude.ai) are the MASTER copy. This repo is the editable source + history.
# Run after ANY skill change: it compares each repo skill with the copy synced down from Jason's account,
# and zips every skill that differs into the outbox, so Jason can re-upload it (claude.ai → Settings → Capabilities → Skills → replace).
set -u
OUT="${1:-/tmp/skills-outbox}"; mkdir -p "$OUT"
SYNC=$(ls -d /root/.claude/skills/synced/*/ 2>/dev/null | head -1)
cd "$(dirname "$0")/.claude/skills" || exit 1
for s in jason-video-editor jason-motion-graphics jason-ad-film; do
  if [ -n "$SYNC" ] && [ -d "$SYNC$s" ] && diff -rq -x node_modules "$s" "$SYNC$s" >/dev/null 2>&1; then
    echo "up to date in account: $s"
  else
    # claude.ai allows at most 200 files per skill zip: bulky folders ship as ONE packed.tgz (SKILL.md says how to unpack)
    ST=$(mktemp -d); cp -r "$s" "$ST/"; rm -rf "$ST/$s"/node_modules "$ST/$s"/*/node_modules
    PK=""; for d in assets examples references/ref-sheets kit/node_modules; do [ -d "$ST/$s/$d" ] && PK="$PK $d"; done
    if [ "$(find "$ST/$s" -type f | wc -l)" -gt 190 ] && [ -n "$PK" ]; then (cd "$ST/$s" && tar czf packed.tgz $PK && rm -rf $PK); fi
    N=$(find "$ST/$s" -type f | wc -l); [ "$N" -gt 200 ] && echo "WARNING: $s still has $N files (limit 200)"
    rm -f "$OUT/$s.zip"; (cd "$ST" && zip -qr "$OUT/$s.zip" "$s" -x "*.DS_Store"); rm -rf "$ST"
    echo "NEEDS RE-UPLOAD: $s  ->  $OUT/$s.zip"
  fi
done
