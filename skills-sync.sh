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
    zip -qr -FS "$OUT/$s.zip" "$s" -x "*/node_modules/*" "*.DS_Store"
    echo "NEEDS RE-UPLOAD: $s  ->  $OUT/$s.zip"
  fi
done
