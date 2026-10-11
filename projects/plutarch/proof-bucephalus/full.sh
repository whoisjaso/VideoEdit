#!/bin/bash
# chunked render: 600 frames at a time -> encoded segment -> PNGs deleted (keeps disk small)
cd "$(dirname "$0")"
rm -rf smp
L=181.5; N=$(python3 -c "print(int($L*30))"); CH=600
rm -f segs.txt
for ((s=0; s<N; s+=CH)); do
  e=$((s+CH<N ? s+CH : N))
  python3 -c "
import json; json.dump([{'o':f'{f:05d}.png','t':f/30} for f in range($s,$e)],open('plan.json','w'))"
  VW=1920 VH=1080 HTML=proof.html node render2.js plan.json smp 4 > /dev/null
  ffmpeg -v error -y -framerate 30 -start_number $s -i smp/%05d.png -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 seg_$s.mp4
  rm -rf smp; echo "file 'seg_$s.mp4'" >> segs.txt; echo "chunk $s-$e done"
done
ffmpeg -v error -y -f concat -safe 0 -i segs.txt -c copy picture.mp4 && rm -f seg_*.mp4 && echo done
