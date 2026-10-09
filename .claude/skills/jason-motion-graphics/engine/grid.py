import sys, subprocess, numpy as np, json
p=sys.argv[1]; sr=22050; hop=64
raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout
y=np.frombuffer(raw,np.float32)
n=1024; w=np.hanning(n); fr=np.lib.stride_tricks.sliding_window_view(y,n)[::hop]*w
S=np.log1p(np.abs(np.fft.rfft(fr,axis=1))); freqs=np.fft.rfftfreq(n,1/sr)
d=np.maximum(0,np.diff(S,axis=0)); fps=sr/hop
env=d.sum(1); kick=d[:,freqs<160].sum(1)
def best(period):
    # phase search on full track
    t=np.arange(len(env))/fps; scores=[]
    phases=np.linspace(0,period,200,endpoint=False)
    for ph in phases:
        idx=np.round((np.arange(ph, t[-1], period))*fps).astype(int); idx=idx[idx<len(env)]
        scores.append(env[idx].sum())
    return phases[int(np.argmax(scores))], max(scores)
# refine period around 120
cands=np.linspace(0.495,0.505,41); res=[(best(P)[1],P) for P in cands]; P=max(res)[1]; ph,_=best(P)
beats=np.arange(ph, len(y)/sr, P)
# downbeat: which of 4 offsets has most kick energy
kb=[kick[np.minimum((beats[o::4]*fps).astype(int),len(kick)-1)].sum() for o in range(4)]
o=int(np.argmax(kb)); downs=beats[o::4]
print(json.dumps({"period":P,"bpm":60/P,"phase":ph,"downbeat_offset":o,"kick_by_offset":[round(float(k),1) for k in kb],"downbeats":[round(float(x),3) for x in downs[:30]]}))
