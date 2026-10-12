#!/bin/bash
# Chapter = Prologue (s18) + scenes 0..17 -> WORKDIR/chapter1.mp4 (stream copy; every scene shares codec settings)
WD=$1; cd $WD; rm -f chapter_list.txt
for s in 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do f=$WD/s$(printf %02d $s)/scene.mp4; [ -f $f ] || { echo "MISSING $f"; exit 1; }; echo "file '$f'" >> chapter_list.txt; done
ffmpeg -v error -y -f concat -safe 0 -i chapter_list.txt -c copy -movflags +faststart chapter1.mp4
T=0; for s in 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do T=$(python3 -c "print($T+$(ffprobe -v error -show_entries format=duration -of csv=p=0 $WD/s$(printf %02d $s)/scene.mp4))"); done
echo "chapter $(ffprobe -v error -show_entries format=duration -of csv=p=0 chapter1.mp4) s (sum of scenes $T s)"
