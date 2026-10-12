# Bucephalus proof: George (IMMERSE) + Fable at sleep pace. Writes vo.wav + lines.json (start/end per line).
import soundfile as sf, numpy as np, json
from kokoro import KPipeline
SR=24000; pipe=KPipeline(lang_code="b")
L=[ # (voice, text, pause_after_s)
 ("bm_george","You are twelve years old.",1.0),
 ("bm_george","The air smells of dust, and sweat, and leather.",1.0),
 ("bm_george","In front of you, a black horse is screaming and rearing, higher than the men around him.",0.8),
 ("bm_george","They call him Bucephalus.",1.0),
 ("bm_george","Your father's best riders have tried him, one after another. And every one has been thrown, or has backed away.",1.4),
 ("bm_george","Your father is tired of it. He tells them to take the horse away.",0.8),
 ("bm_george","And the men nod, because that's what you do, when the king has decided.",1.6),
 ("bm_george","But you've been watching. Not the horse's hooves. His eyes.",1.0),
 ("bm_george","Every time he lunges, he's jumping away from something on the ground.",0.9),
 ("bm_george","His own shadow. Black, and moving at his feet.",1.6),
 ("bm_george","The men are laughing at you for speaking up. Your father is watching, to see if you'll embarrass him.",0.9),
 ("bm_george","Your heart is pounding.",3.0),
 ("bm_george","What do you do?",3.2),
 ("bm_george","You walk forward, slowly.",0.9),
 ("bm_george","You take the reins, and turn his head toward the sun, so the shadow falls behind him, where he can't see it.",1.0),
 ("bm_george","You speak low. You put your hand on his neck, and feel him trembling under your palm.",1.0),
 ("bm_george","Then, in one motion, you're on his back.",0.8),
 ("bm_george","And you let him run.",2.6),
 ("bm_george","When you ride back, your father has tears in his eyes.",0.9),
 ("bm_george","My son, he says. Find a kingdom big enough for you. Macedonia is too small.",2.6),
 ("bm_fable","Feel what just happened inside you. Not the applause. Something quieter.",1.1),
 ("bm_fable","A part of you watched you see what the grown men missed. And it wrote it down.",1.0),
 ("bm_fable","I see what others miss. I move when others give up.",1.4),
 ("bm_fable","That's the Observer. It doesn't believe what you say about yourself. It believes what it sees you do.",1.2),
 ("bm_fable","You've had moments like this. Fixing what the adults gave up on. Finishing the rep, when everyone else racked the weight.",1.0),
 ("bm_fable","Nobody throws a party. But a belief is born.",1.8),
 ("bm_fable","What's the last thing you did, that gave your Observer real evidence?",3.0),
]
out=[]; t=1.5; meta=[]; out.append(np.zeros(int(SR*1.5),np.float32))
for i,(v,tx,p) in enumerate(L):
    a=np.concatenate([x for _,_,x in pipe(tx, voice=v, speed=0.82)]).astype(np.float32)
    meta.append(dict(i=i,voice=v,text=tx,start=round(t,3),end=round(t+len(a)/SR,3)))
    out.append(a); t+=len(a)/SR
    gap=p+(1.0 if i+1<len(L) and L[i+1][0]!=v else 0)
    out.append(np.zeros(int(SR*gap),np.float32)); t+=gap
sf.write("vo.wav",np.concatenate(out),SR); json.dump(meta,open("lines.json","w"),indent=1); print("total",round(t,1),"s")
