import subprocess, numpy as np, os, sys
SFX='/home/user/ApoheniaQuest/.claude/skills/jason-video-editor/assets/sfx/'
SR=48000; LEN=15.0; N=int(LEN*SR)
def load(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def peak(x):
    m=np.abs(x).mean(1); w=int(SR*0.005); return int(np.argmax(np.convolve(m,np.ones(w)/w,'same')))
EV=[ # time the PEAK lands, file, gain dB
 (0.16,'pack5/sparkle.wav',-17),            # spark draws
 (0.52,'pack5/deep_whoosh.wav',-11),        # spark opens into the marble head
 (0.96,'pack5/button_2.wav',-17),           # image settles into a card
 (2.02,'pack3/woosh.wav',-17),              # card becomes a circle
 (3.0,'pop.wav',-10),(3.03,'ios/ios_tink.wav',-12),   # the thought (spark) pops
 (3.94,'pack3/cinematic_woosh.wav',-8),     # dive into the spark
 (4.0,'deep_bass.wav',-5),(4.0,'pack4/cinestrike.wav',-11),  # the drop
 (4.05,'pop.wav',-15),(4.14,'pop.wav',-16),(4.23,'pop.wav',-16),
 (4.5,'click.wav',-12),(5.0,'click.wav',-12),(5.5,'click.wav',-12),
 (5.0,'pack3/woosh.wav',-22),(5.5,'pack3/woosh.wav',-22),
 (6.03,'pack5/deep_whoosh.wav',-11),        # the wave takes the frame
 (6.5,'pack3/woosh.wav',-15),               # shrinks into the carousel
 (7.0,'pack3/cinematic_woosh.wav',-16),     # carousel turns
 (7.25,'click.wav',-13),(7.8,'click.wav',-13),
 (8.04,'pack3/cinematic_woosh.wav',-11),    # Van Gogh fills the frame
 *[(8.0+0.25*i,'camera_shutter.wav',-15) for i in range(1,8)],   # match cuts
 (9.02,'pop.wav',-15),                      # second frame slides in
 (10.02,'pack3/woosh.wav',-15),             # the red-chalk study
 (10.5,'ios/ios_tink.wav',-9),              # "yours?"
 (12.05,'pack5/sparkle.wav',-14),           # ring of works
 (13.48,'riser.wav',-14),                   # rays gather
 (13.5,'ui/reverb_hit.wav',-6),(13.62,'pack3/shine.wav',-12),   # the spark
 (14.08,'pop.wav',-17),                     # wordmark
]
fx=np.zeros((N,2),np.float32); cache={}
for t,f,g in EV:
    if f not in cache: x=load(SFX+f); cache[f]=(x,peak(x))
    x,pk=cache[f]; st=int(t*SR)-pk; a=max(0,st); b=min(N,st+len(x))
    if b>a: fx[a:b]+=x[a-st:b-st]*10**(g/20)
mus=load(sys.argv[1])[int(11.67*SR):int(11.67*SR)+N]
env=np.ones(N); f0,f1=int(14.1*SR),N; env[f0:f1]=np.linspace(1,0,f1-f0)**1.6   # the music bows out under the logo
env[:int(0.02*SR)]=np.linspace(0,1,int(0.02*SR))
mus*=env[:,None]
for name,mix in [('ad_fx',fx),('ad_music',fx+mus*10**(-6/20))]:
    mix.astype(np.float32).tofile(name+'.f32')
    subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i',name+'.f32','-af','loudnorm=I=-14:TP=-1:LRA=11','-ar','48000',name+'.wav'],check=True)
print('placed',len(EV))
