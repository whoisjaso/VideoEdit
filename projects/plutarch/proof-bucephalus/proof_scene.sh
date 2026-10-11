#!/bin/bash
# Bucephalus = chapter scene 4: render the proof engine (3 lanes) and mux into WORKDIR/s04/scene.mp4
cd "$(dirname "$0")"; WD=$1; mkdir -p $WD/s04; rm -f seg_*.mp4 picture.mp4
sed -i 's#HTML=proof.html#HTML=$PWD/proof.html#' lane.sh
bash par.sh > par.log 2>&1
ffmpeg -v error -y -i picture.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest $WD/s04/scene.mp4 && echo "SCENE 4 DONE"
