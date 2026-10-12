#!/usr/bin/env bash
# One-time environment setup for the jason-video-editor skill (works in the sandboxed cloud container:
# only npm/PyPI/GitHub are reachable — every model here comes from those).
set -e
pip install -q imageio-ffmpeg "mediapipe==0.10.14" opencv-python-headless numpy >/dev/null 2>&1 || true
pip install -q --no-deps vosk >/dev/null 2>&1 || true
pip install -q tqdm requests cffi >/dev/null 2>&1 || true   # vosk runtime deps that --no-deps skips
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"); ln -sf "$FF" /usr/local/bin/ffmpeg
mkdir -p /tmp/stub && touch /tmp/stub/srt.py                      # vosk imports 'srt' (not needed) — stub it
# Offline English speech model (Vosk small, word timestamps) — shipped inside the npm package transcribe2texts
if [ ! -d "$HOME/.vosk-model" ]; then
  (cd /tmp && f=$(npm pack transcribe2texts 2>/dev/null | tail -1) && tar xzf "$f" && mv package/vosk-model-small-en-us-0.15 "$HOME/.vosk-model")
fi
echo "ready: ffmpeg=$(which ffmpeg) vosk_model=$HOME/.vosk-model mediapipe=$(python3 -c 'import mediapipe;print(mediapipe.__version__)')"
