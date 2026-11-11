#!/bin/bash
# Mux picture + master audio, cut the two follow-up clips, write lossless audio deliverables.
# usage: src/finish.sh <work dir with picture_h.mp4 / picture_v.mp4>
set -e; WORK=$1; cd "$(dirname "$0")/.."; OUT=../../renders; N=your-brain-is-racist
read TS0 TS1 SW0 SW1 <<<$(python3 -c "
import sys; sys.path.insert(0,'src'); from timing import TL; t=TL()
print(round(t.T('ts1')-1.0,3), round(t.E('ts22')+0.9,3), round(t.T('sw1')-0.3,3), round(t.E('sw13')+0.9,3))")
for A in h v; do
  [ -f "$WORK/picture_$A.mp4" ] || continue
  R=$([ $A = h ] && echo 16x9 || echo 9x16); M="$OUT/$N-$R-v2.mp4"
  ffmpeg -y -loglevel error -i "$WORK/picture_$A.mp4" -i audio/master_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 \
    -movflags +faststart -metadata title="Your brain is racist. So is mine." -metadata artist="olaceo" "$M"
  for C in "traffic-stop $TS0 $TS1" "code-switching $SW0 $SW1"; do
    set -- $C; D=$(python3 -c "print(round($3-$2,3))"); FO=$(python3 -c "print(round($3-$2-0.3,3))")
    ffmpeg -y -loglevel error -ss $2 -t $D -i "$M" -vf "fade=in:st=0:d=0.25,fade=out:st=$FO:d=0.3" -af "afade=in:st=0:d=0.2,afade=out:st=$FO:d=0.3" \
      -c:v libx264 -preset medium -crf 19 -r 60 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart "$OUT/$N-cut-$1-$R.mp4"
  done
done
ffmpeg -y -loglevel error -i audio/narration.wav -c:a flac -sample_fmt s16 audio/narration.flac
ffmpeg -y -loglevel error -i audio/master_mix.wav -c:a flac -sample_fmt s32 -bits_per_raw_sample 24 audio/master_mix.flac
ls -la $OUT
