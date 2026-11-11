#!/bin/bash
# Master the mix: -14 LUFS integrated, true peak at or under -4 dBTP AFTER the AAC encode (AAC adds about 1 dB of overshoot,
# so the WAV is limited to about -5.3 dBTP).
set -e; cd "$(dirname "$0")/../audio"
python3 ../src/mix.py
ffmpeg -y -loglevel error -i mix_premaster.wav -af "acompressor=threshold=-26dB:ratio=4:attack=4:release=110:makeup=1" -c:a pcm_f32le _c.wav
I=$(ffmpeg -hide_banner -nostats -i _c.wav -af ebur128 -f null - 2>&1 | grep "I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(round(-12.9 - ($I), 2))")
ffmpeg -y -loglevel error -i _c.wav -af "volume=${G}dB,alimiter=limit=-7.5dB:level=false:attack=2:release=50,volume=1.3dB,aresample=48000" -c:a pcm_s24le master_mix.wav
rm -f _c.wav
ffmpeg -hide_banner -nostats -i master_mix.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:|LRA:" | tail -3
