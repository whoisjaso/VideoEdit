#!/bin/bash
# chunked 60 fps render with adaptive motion blur: sharp -> blurplan -> samples -> blend -> h264 segment
cd "$(dirname "$0")"; FPS=60; N=$(python3 -c "import soundfile as sf;i=sf.info('vo.wav');print(int(i.frames/i.samplerate*60))"); C=600
mkdir -p segs
for ((s=0; s<N; s+=C)); do e=$((s+C<N ? s+C : N)); n=$((e-s)); seg=segs/seg_$(printf %05d $s).mp4; [ -f $seg ] && continue
  rm -rf sharp samp blended; python3 -c "import json;json.dump([{'o':f'f{i:04d}.jpg','t':($s+i)/60} for i in range($n)],open('plan_sharp.json','w'))"
  for try in 1 2 3; do VW=1920 VH=1080 HTML=$PWD/film_built.html node render2.js plan_sharp.json sharp 4 >/dev/null 2>&1 && [ $(ls sharp | wc -l) -ge $n ] && break; echo "retry sharp $s"; done
  python3 blurplan.py sharp $n plan_blur.json speeds.json >/dev/null && python3 -c "
import json; P=json.load(open('plan_blur.json'))
for p in P: p['t']=round(p['t']+$s/60,6)
json.dump(P,open('plan_blur.json','w')); print('samples',len(P))"
  for try in 1 2 3; do VW=1920 VH=1080 HTML=$PWD/film_built.html node render2.js plan_blur.json samp 4 >/dev/null 2>&1 && break; echo "retry samp $s"; done
  python3 blend.py samp plan_blur.json blended >/dev/null
  ffmpeg -v error -y -framerate 60 -i blended/f%04d.png -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -r 60 $seg && echo "SEG $s-$e done"
  rm -rf sharp samp blended
done
ls segs/seg_*.mp4 | sort | sed "s/.*/file '&'/" > segs.txt && ffmpeg -v error -y -f concat -safe 0 -i segs.txt -c copy picture.mp4 && echo PICTURE DONE
