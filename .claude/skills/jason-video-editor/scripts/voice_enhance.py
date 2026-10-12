"""Clean + loud voice track: DeepFilterNet3 denoise, then the 6-stage radio chain (r26), -14 LUFS.
Usage: python3 voice_enhance.py in.(mov|wav) out.wav [model_dir] [atten_lim_db=15]
Ep #4 lesson: unlimited denoise ERASED his quieter opening 5s (it judged soft speech as noise). The denoise is now capped
(atten_lim_db, default 15 dB) and a leveler (dynaudnorm) lifts quiet stretches before compression. Always run check_voice.py after.
Setup notes (this container):
- pip install torch deepfilternet torchaudio, then pip install "numpy>=2,<2.3".
- Shim torchaudio.backend.common (removed in new torchaudio): create backend/__init__.py and backend/common.py with `class AudioMetaData: pass`.
- Model: git clone --depth 1 --filter=blob:none --sparse https://github.com/Rikorose/DeepFilterNet; sparse-checkout models; unzip DeepFilterNet3.zip."""
import array, subprocess, sys, wave, warnings
warnings.filterwarnings("ignore")
import torch
from df.enhance import enhance, init_df
src, out = sys.argv[1], sys.argv[2]
model, st, _ = init_df(model_base_dir=sys.argv[3] if len(sys.argv) > 3 else None)
sr = st.sr()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", "/tmp/_ve_in.wav"], check=True)
w = wave.open("/tmp/_ve_in.wav"); a = array.array("h", w.readframes(w.getnframes()))
lim = float(sys.argv[4]) if len(sys.argv) > 4 else 15.0
y = enhance(model, st, torch.tensor(a, dtype=torch.float32).unsqueeze(0) / 32768.0, atten_lim_db=lim).squeeze(0).clamp(-1, 1)
o = wave.open("/tmp/_ve_clean.wav", "w"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
o.writeframes(array.array("h", (y * 32767).to(torch.int16).tolist()).tobytes()); o.close()
# THE RADIO CHAIN (r26, Jason 2026-10-12: "what we need to do EVERYTIME to our voice"), in this order:
# 1 high-pass 100 Hz (rumble) -> 2 downward expander (gentle 2:1, max -12 dB, so quiet words survive: ep #4 lesson)
# -> leveler -> 3 de-esser -> 4 EQ (-2 dB mud at 250, +4 dB clarity at 3.5 kHz, light air) -> 5 compressor -> loudness -> 6 limiter (ceiling)
CHAIN = ("highpass=f=100:poles=2,"
         "agate=threshold=0.008:ratio=2:range=0.25:attack=5:release=180:knee=4:detection=rms,"
         "dynaudnorm=f=250:g=15:p=0.9:m=12,"
         "deesser=i=0.45:m=0.5:f=0.5:s=o,"
         "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.0:g=4,equalizer=f=9000:t=h:w=2000:g=1,"
         "acompressor=threshold=-22dB:ratio=3.5:attack=8:release=120:makeup=4,"
         "loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:attack=3:release=50")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/_ve_clean.wav", "-af",
    CHAIN, "-ar", "48000", out], check=True)
print("wrote", out)
