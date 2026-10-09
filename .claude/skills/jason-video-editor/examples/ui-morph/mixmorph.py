import subprocess, numpy as np, json, sys
SFX='/tmp/claude-0/-home-user-ApoheniaQuest/a7864f3b-0e94-5f00-94a5-59ce23b410f7/scratchpad/v5/public/sfx/'
SR=48000
def load(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def peak(x):
    m=np.abs(x).mean(1); win=int(SR*0.005); env=np.convolve(m,np.ones(win)/win,'same'); return int(np.argmax(env))
B=lambda n:n*0.5
EV=[ # time, file, gain(dB)
 (B(1),'click.wav',-6),(B(2),'ui/open_ui.wav',-14),(B(3),'ui/success_ui.wav',-8),(B(4),'pop.wav',-12),
 (B(5),'ios/ios_tritone.wav',-8),(B(6),'ui/open_ui.wav',-14),(B(7),'click.wav',-10),(B(7)+0.3,'swoosh.wav',-10),
 (B(8),'pop.wav',-12),(B(9),'ios/ios_success.wav',-9),(B(10),'ios/ios_tink.wav',-6),(B(11),'ui/open_ui.wav',-14),
 (B(12),'click.wav',-10),(B(13),'ios/ios_key.wav',-14),(B(14),'ui/switch.wav',-6),(B(15),'swoosh.wav',-14),
 (B(16),'ios/ios_key.wav',-18),(B(17),'click.wav',-8),(B(18),'click.wav',-8),(B(19),'ui/open_ui.wav',-12),
 (B(20),'swoosh.wav',-14),(B(21),'ios/ios_tink.wav',-10),(B(22),'ios/ios_tink.wav',-8),(B(23),'ui/open_ui.wav',-12),
 *[(B(24)+i*0.032,'ios/ios_key.wav',-20) for i in range(13)],
 (B(25),'pop.wav',-12),(B(26),'ios/ios_received.wav',-8),(B(27),'swoosh.wav',-14),
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
