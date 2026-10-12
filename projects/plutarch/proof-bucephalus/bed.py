# Ambient bed for the Bucephalus proof: wind + warm drone + heartbeat + hooves; drops near-silent for "What do you do?"
import numpy as np, subprocess
SR=48000; L=184.0; n=int(L*SR); t=np.arange(n)/SR
rng=np.random.default_rng(3)
def lp(x,a): # one-pole lowpass
    y=np.empty_like(x); acc=0.0
    for i in range(0,len(x),4096):
        seg=x[i:i+4096]; out=np.empty_like(seg)
        for j,v in enumerate(seg): acc+=a*(v-acc); out[j]=acc
        y[i:i+4096]=out
    return y
# wind: filtered noise with slow gusts
w=rng.standard_normal(n).astype(np.float32)
w=np.convolve(w,np.ones(48)/48,mode='same')
w=w-np.convolve(w,np.ones(2400)/2400,mode='same')
gust=0.55+0.45*np.sin(2*np.pi*t/9.0)*np.sin(2*np.pi*t/23.0+1)
wind=w*gust*0.9
# drone: A1/E2/A2 with slow beating, soft
dr=(np.sin(2*np.pi*55*t)*0.5+np.sin(2*np.pi*82.41*t+0.3)*0.35+np.sin(2*np.pi*110.3*t)*0.22+np.sin(2*np.pi*164.8*t)*0.08)
dr*=0.6+0.4*np.sin(2*np.pi*t/14)
# mirror section (Fable, 130s+): drone warms (adds a fifth), wind recedes
mir=np.clip((t-129)/4,0,1)
dr=dr+mir*np.sin(2*np.pi*246.9*t)*0.05
# envelope: fade in, silence window, fade out
env=np.clip(t/3,0,1)*np.clip((L-t)/5,0,1)
sil=1-0.85*np.clip((t-79.2)/0.6,0,1)*np.clip((84.6-t)/1.0,0,1)
bed=(wind*(1-0.6*mir)*0.35+dr*0.25)*env*sil
# heartbeat 73.9–79.6
hb=np.zeros(n)
for k in range(7):
    for off,a in [(0,1.0),(0.22,0.7)]:
        s=73.9+k*0.92+off
        if s>79.5: continue
        i=int(s*SR); m=int(0.18*SR); tt=np.arange(m)/SR
        hb[i:i+m]+=a*np.sin(2*np.pi*48*tt)*np.exp(-tt*22)
bed+=hb*0.9
# hooves 110.4–115 (gallop: 3 beats + gap), receding
hv=np.zeros(n)
s=110.45
while s<115.2:
    for off in (0,0.11,0.22):
        i=int((s+off)*SR); m=int(0.09*SR); tt=np.arange(m)/SR
        if i+m<n: hv[i:i+m]+=np.sin(2*np.pi*95*tt)*np.exp(-tt*45)*(1+0.3*rng.standard_normal(m)*np.exp(-tt*80))
    s+=0.5
hv*=np.clip((115.4-t)/4,0,1)
bed+=hv*0.6
bed=bed/np.abs(bed).max()*0.5
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-ac","2","bed.wav"],input=bed.astype(np.float32).tobytes(),check=True)
print("bed ok")
