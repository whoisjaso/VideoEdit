import soundfile as sf, numpy as np, sys
from kokoro import KPipeline
TEXT = ("Before he ever ruled the world, a boy in Macedonia believed something about himself. "
        "He believed he was born for something larger than his father's kingdom. "
        "And because he believed it, he began to act like it. Long before anyone was watching.")
for v, lang in [("af_heart","a"),("bm_george","b"),("am_michael","a"),("bm_fable","b")]:
    pipe = KPipeline(lang_code=lang)
    audio = np.concatenate([a for _,_,a in pipe(TEXT, voice=v, speed=0.9)])
    sf.write(f"{v}.wav", audio, 24000); print(v, round(len(audio)/24000,1), "s", flush=True)
