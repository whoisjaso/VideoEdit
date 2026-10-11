#!/bin/bash
# Full scene pipeline after voice + words exist:  run_scene.sh SCENE WORKDIR PD_DIR ENG_DIR
#   build scene.js -> world sound -> text SFX + mix -> render (3 lanes, 600-frame chunks) -> scene.mp4 (+ preview copy per scene)
set -e
SI=$1; WD=$2; PD=$3; ENG=$4; F=$(cd "$(dirname "$0")" && pwd); D=$WD/s$(printf %02d $SI)
SK=/home/user/ApoheniaQuest/.claude/skills/jason-video-editor
python3 $F/build_scene.py $SI $WD
python3 $F/world_scene.py $SI $WD $PD
LEN=$(grep -o 'const LEN=[0-9.]*' $D/scene.js | cut -d= -f2)
(cd $D && python3 $SK/scripts/mix_talk.py vo.wav cues.json $SK/assets/sfx/library.json $SK/assets/sfx vo_sfx.wav --len_s $(python3 -c "print($LEN+1)") > /dev/null &&
 ffmpeg -v error -y -i vo_sfx_raw.wav -i music.wav -i amb.wav -filter_complex "[0]aformat=channel_layouts=stereo[v];[v][1][2]amix=inputs=3:normalize=0:duration=longest,atrim=0:$LEN,loudnorm=I=-18:TP=-2:LRA=11" -ar 48000 audio.wav)
for f in film.html kit.js inter.woff2 is-italic.woff2 render2.js node_modules; do ln -sfn $ENG/$f $D/$f; done
ln -sfn $WD/plates $D/plates
N=$(python3 -c "print(int($LEN*30))"); C=$(( (N + 2) / 3 ))
cd $D; rm -f seg_*.mp4
lane() { A=$1; B=$2; for ((s=A; s<B; s+=600)); do e=$((s+600<B ? s+600 : B)); rm -rf smp_$A
  python3 -c "import json; json.dump([{'o':f'{f:05d}.png','t':f/30} for f in range($s,$e)],open('plan_$A.json','w'))"
  VW=1920 VH=1080 HTML=film.html node render2.js plan_$A.json smp_$A 2 > /dev/null
  ffmpeg -v error -y -framerate 30 -start_number $s -i smp_$A/%05d.png -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 seg_$(printf %05d $s).mp4
  rm -rf smp_$A; echo "s$SI chunk $s-$e"; done; }
lane 0 $C & lane $C $((2*C)) & lane $((2*C)) $N & wait
ls seg_*.mp4 | sort | sed "s/.*/file '&'/" > segs.txt
ffmpeg -v error -y -f concat -safe 0 -i segs.txt -c copy picture.mp4
ffmpeg -v error -y -i picture.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest scene.mp4 && rm -f seg_*.mp4
echo "SCENE $SI DONE $D/scene.mp4"
