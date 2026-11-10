#!/bin/bash
# Render one aspect (h = 1920x1080, v = 1080x1920) in 4 parallel chunks, then join. No re-encode on the join.
# usage: src/render.sh h|v <work dir> [crf]
set -e
A=$1; WORK=$2; CRF=${3:-19}; cd "$(dirname "$0")/.."
N=$(python3 -c "import sys; sys.path.insert(0,'src'); from timing import TL; print(TL().frames())")
J=4; mkdir -p "$WORK"; : > "$WORK/list_$A.txt"
for i in $(seq 0 $((J-1))); do
  S=$(( (N*i/J)/120*120 )); E=$(( i==J-1 ? N : (N*(i+1)/J)/120*120 ))
  python3 src/film.py render --aspect $A --start $S --end $E --crf $CRF --out "$WORK/${A}_$i.mp4" 2>/dev/null &
  echo "file '${A}_$i.mp4'" >> "$WORK/list_$A.txt"
done
wait
ffmpeg -y -loglevel error -f concat -safe 0 -i "$WORK/list_$A.txt" -c copy "$WORK/picture_$A.mp4"
echo "done $A $(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate -of csv=p=0 "$WORK/picture_$A.mp4") expected $N"
