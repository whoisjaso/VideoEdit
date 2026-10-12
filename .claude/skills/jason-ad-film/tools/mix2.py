# mix2.py music.mp3 cues.json : effects placed by measured peak on frames computed from the picture code
import subprocess, numpy as np, json, sys
SFX = '/home/user/ApoheniaQuest/.claude/skills/jason-video-editor/assets/sfx/'
SR = 48000; LEN = 15.0; N = int(LEN * SR); F = lambda f: f / 60
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def peak(x):
    m = np.abs(x).mean(1); w = int(SR * 0.004); return int(np.argmax(np.convolve(m, np.ones(w) / w, 'same')))
C = json.load(open(sys.argv[2]))
EV = []
for f in C['ticks']: EV.append((F(f) + 0.008, 'ios/ios_tink.wav', -19))           # one ray = one soft tick, all equal
for w in C['whoosh']: EV.append((F(w['apex']), 'pack3/woosh.wav', -15))            # peak on the velocity peak
EV += [(F(C['drop']) + 0.02, 'deep_bass.wav', -5), (F(C['drop']) + 0.02, 'pack4/cinestrike.wav', -13)]
EV += [(F(741), 'pack5/deep_whoosh.wav', -20)]                                       # the hero turn
EV += [(F(C['name']) + 0.05, 'ding.wav', -13), (F(C['name']) + 0.05, 'deep_bass.wav', -20)]  # the name: one soft resolved hit
fx = np.zeros((N, 2), np.float32); cache = {}
for t, f, g in EV:
    if f not in cache: x = load(SFX + f); cache[f] = (x, peak(x))
    x, pk = cache[f]; st = int(t * SR) - pk; a, b = max(0, st), min(N, st + len(x))
    if b > a: fx[a:b] += x[a - st:b - st] * 10 ** (g / 20)
mus = load(sys.argv[1])[int(9.67 * SR):int(9.67 * SR) + N]
env = np.ones(N)
s0, s1 = int(F(C['silence'][0]) * SR), int(F(C['silence'][1]) * SR)          # the suck before the drop
env[s0 - int(.03 * SR):s0] = np.linspace(1, 0.05, int(.03 * SR)); env[s0:s1] = 0.05
st = int(F(C['stop']) * SR); env[st:st + int(.05 * SR)] = np.linspace(1, 0, int(.05 * SR)); env[st + int(.05 * SR):] = 0   # music stops on the bar line
env[:int(.015 * SR)] = np.linspace(0, 1, int(.015 * SR))
mus *= env[:, None]
for name, mix in [('v2_fx', fx), ('v2_music', fx + mus * 10 ** (-5 / 20))]:
    mix.astype(np.float32).tofile(name + '.f32')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', name + '.f32', '-af', 'highpass=f=25,loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '48000', name + '.wav'], check=True)
print('events', len(EV))
