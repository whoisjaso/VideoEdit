import re, json, numpy as np, soundfile as sf
from kokoro import KPipeline
L = [l.split('. ',1)[1] for l in open('/home/user/ApoheniaQuest/projects/royalty-roofing/script.md').read().split('\n') if re.match(r'^\d+\. ', l)]
L = [re.sub(r'\s*\[[^\]]*\]', '', l).strip() for l in L]
P = KPipeline(lang_code='a'); SR = 24000
GAP = {1: 0.35, 4: 0.55, 5: 0.6, 9: 0.6, 10: 0.7, 11: 0.5, 13: 0.7, 14: 0.6, 15: 0.8}
out = [np.zeros(int(SR*0.6), np.float32)]; t = 0.6; meta = []
for i, l in enumerate(L, 1):
    a = np.concatenate([x for _, _, x in P(l, voice='af_heart', speed=0.95)]).astype(np.float32)
    meta.append(dict(i=i, text=l, start=round(t,3), end=round(t+len(a)/SR,3))); out.append(a); t += len(a)/SR
    g = GAP.get(i, 0.4); out.append(np.zeros(int(SR*g), np.float32)); t += g
out.append(np.zeros(int(SR*1.4), np.float32)); t += 1.4
sf.write('vo_raw.wav', np.concatenate(out), SR); json.dump(meta, open('lines.json','w'), indent=1)
print(round(t,2), 's'); [print(m['i'], m['start'], m['text'][:60]) for m in meta]
