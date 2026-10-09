import sys, subprocess, numpy as np
def load(p, sr=22050):
    raw = subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw, np.float32), sr
def flux(y, sr, hop=128, n=2048):
    w = np.hanning(n); frames = np.lib.stride_tricks.sliding_window_view(y, n)[::hop]*w
    S = np.log1p(np.abs(np.fft.rfft(frames, axis=1)))
    f = np.maximum(0, np.diff(S, axis=0)).sum(1); f = f - np.convolve(f, np.ones(16)/16, 'same')
    return np.maximum(f, 0), sr/hop
def tempo(env, fps):
    env = env - env.mean(); ac = np.correlate(env, env, 'full')[len(env)-1:]
    lags = np.arange(len(ac)); bpm = 60*fps/np.maximum(lags,1)
    m = (bpm > 70) & (bpm < 180)
    # weight toward 120
    score = ac[m] * np.exp(-0.5*(np.log2(bpm[m]/120)/0.6)**2)
    i = np.argmax(score); L = lags[m][i]
    a,b_,c_ = ac[L-1],ac[L],ac[L+1]; d = 0.5*(a-c_)/(a-2*b_+c_)  # parabolic peak
    return 60*fps/(L+d), ac[L]/ac[0]
for p in sys.argv[1:]:
    y, sr = load(p)
    if len(y) < sr*10: continue
    y = y[: sr*60]
    env, fps = flux(y, sr); b, c = tempo(env, fps)
    print(f"{p.split('/')[-1]:10s} {b:6.1f} bpm  conf {c:.2f}  dur {len(load(p)[0])/sr:5.0f}s")
