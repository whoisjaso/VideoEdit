import subprocess, numpy as np, json, sys
import os
# the shared SFX library lives in the editor skill; override with SFX_DIR=...
SFX=os.environ.get('SFX_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../jason-video-editor/assets/sfx/'))
SR=48000
def load(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def peak(x):
    m=np.abs(x).mean(1); win=int(SR*0.005); env=np.convolve(m,np.ones(win)/win,'same'); return int(np.argmax(env))
B=lambda n:n*0.5
EV=[ # time, file, gain(dB). v2 (Jason: "sfx could be better"): one sound per KIND of moment, no repeats of the same swell,
     # taps = real buttons, panels opening = iOS lock/card sound, transitions quieter and lighter, typing = one key per letter, hovers silent
 (B(1),'pack5/button_1.wav',-8),            # press Post
 (B(2),'ios/ios_key.wav',-16),              # becomes loader (light)
 (B(3),'ui/success_ui.wav',-10),            # Posted ✓
 (B(4),'pop.wav',-15),                      # island
 (B(5),'ios/ios_tritone.wav',-11),          # notification
 (B(6),'ios/ios_lock.wav',-14),             # card opens
 (B(7),'click.wav',-12),                    # grab
 (B(7)+0.3,'pack5/deep_whoosh.wav',-14),    # swipe away
 (B(8),'pop.wav',-16),                      # Apple Pay pill
 (B(9),'ios/ios_success.wav',-10),          # payment received
 (B(10),'ios/ios_tink.wav',-8),             # gold check
 (B(11),'ios/ios_lock.wav',-17),            # settings row
 (B(12),'click.wav',-12),                   # grab knob
 (B(13),'ios/ios_key.wav',-18),             # stretch
 (B(14),'ui/switch.wav',-7),                # flips off ON the beat
 (B(15),'pack3/woosh.wav',-20),             # knob becomes the tab indicator
 (B(17),'pack5/button_2.wav',-9),           # tap Followers
 (B(18),'pack5/button_2.wav',-10),          # tap Money
 (B(19),'pack5/deep_whoosh.wav',-19),       # chart opens
 (B(20),'pack5/sparkle.wav',-22),           # line draws
 (B(21),'ios/ios_tink.wav',-12),            # tooltip
 (B(22),'ios/ios_tink.wav',-10),            # peak
 (B(23),'ios/ios_lock.wav',-16),            # ⌘K
 *[(B(24)+i*0.032,'pack5/typing_2.wav' if i%2==0 else 'ios/ios_key.wav',-19) for i in range(13)],
 (B(25),'pop.wav',-14),                     # filter to one
 (B(26),'ios/ios_received.wav',-9),         # toast
 (B(27),'pack3/woosh.wav',-18),             # back to Post
]
LEN=14.0; N=int(LEN*SR)
fx=np.zeros((N,2),np.float32); cache={}
for t,f,g in EV:
    if f not in cache: x=load(SFX+f); cache[f]=(x,peak(x))
    x,pk=cache[f]; start=int(t*SR)-pk; amp=10**(g/20)
    a=max(0,start); b=min(N,start+len(x)); 
    if b>a: fx[a:b]+=x[a-start:b-start]*amp
    # sounds that ring past the loop point wrap to the start, so the loop is seamless
    if start+len(x)>N: rest=x[N-start:]*amp; fx[:len(rest)]+=rest[:N]
print('placed',len(EV),'sounds; peaks(ms):',{k:round(v[1]/SR*1000,1) for k,v in cache.items()})
music=load(sys.argv[1])[int(8.468*SR):int(8.468*SR)+N]
fade=int(0.012*SR); music[:fade]*=np.linspace(0,1,fade)[:,None]; music[-fade:]*=np.linspace(1,0,fade)[:,None]
for name,mix in [('fx_only',fx),('with_music',fx+music*10**(-7/20))]:
    mix.astype(np.float32).tofile(f'{name}.f32')
    subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i',f'{name}.f32','-af','loudnorm=I=-14:TP=-1:LRA=11','-ar','48000',f'{name}.wav'],check=True)
print('ok')
