#!/bin/bash
# Render every scene in order (waits for its word timings), then a chat-size preview of each into preview/.
WD=$1; shift; F=$(cd "$(dirname "$0")" && pwd)
for SI in "$@"; do D=$WD/s$(printf %02d $SI)
  until [ -f $D/words.json ]; do sleep 5; done
  [ -f $D/scene.mp4 ] || bash $F/run_scene.sh $SI $WD $WD/../pd $WD/eng > $D/run.log 2>&1 || { echo "SCENE $SI FAILED"; tail -5 $D/run.log; continue; }
  L=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $D/scene.mp4); BR=$(python3 -c "print(int(min(6000, 28.5*8000/$L - 140)))")
  O=/home/user/ApoheniaQuest/preview/alexander-scene-$(printf %02d $SI).mp4
  ffmpeg -v error -y -i $D/scene.mp4 -vf scale=1600:900 -c:v libx264 -b:v ${BR}k -pass 1 -passlogfile $D/p2 -an -f null /dev/null &&
  ffmpeg -v error -y -i $D/scene.mp4 -vf scale=1600:900 -c:v libx264 -b:v ${BR}k -pass 2 -passlogfile $D/p2 -c:a aac -b:a 128k $O && echo "SCENE READY $SI $O"
done
echo "CHAPTER RENDER LOOP DONE"
