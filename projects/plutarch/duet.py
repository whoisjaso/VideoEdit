# Duet demo: George narrates the history; Fable is the inner voice (the belief lens + modern example). Sleep pace = slower speed + real pauses.
import soundfile as sf, numpy as np
from kokoro import KPipeline
SR=24000; pipe=KPipeline(lang_code="b")
LINES=[
 ("bm_george","When Alexander was a boy, a horse was brought before his father. A wild horse. No rider could hold him."),
 ("bm_george","The men around the king gave up. But Alexander noticed something they had missed. The horse was afraid of its own shadow."),
 ("bm_george","So he turned the horse toward the sun, and calmly, he rode him."),
 ("bm_fable","Notice what happened in that moment. The boy didn't just tame a horse. He learned something about himself. I see what others miss."),
 ("bm_fable","It's the same thing that happens when a kid fixes the family wifi that the adults gave up on. Nobody announces it. But a belief is born, quietly. I am the one who figures it out."),
 ("bm_fable","And from that day, he acts like it."),
]
out=[]
for i,(v,t) in enumerate(LINES):
    a=np.concatenate([x for _,_,x in pipe(t, voice=v, speed=0.82)])
    out.append(a)
    nxt = LINES[i+1][0] if i+1<len(LINES) else None
    out.append(np.zeros(int(SR*(2.2 if nxt and nxt!=v else 1.1)),np.float32))   # longer breath when the voice changes
sf.write("duet_demo.wav", np.concatenate(out), SR); print(round(sum(len(x) for x in out)/SR,1),"s")
