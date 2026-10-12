# engrave.py DIR : raw/*.jpg -> img/NAME.png  (grayscale, paper -> pure white, ink -> near-black ink #141413;
#   "cut" assets get a rembg alpha cutout first). Run with the rembg venv python.
import json, sys, os, numpy as np
from PIL import Image, ImageFilter
D=sys.argv[1]; os.makedirs(D+'/img',exist_ok=True)
meta=json.load(open(D+'/meta.json'))
sess=None
INK=np.array([20,20,19],float)
for m in meta:
    im=Image.open(f"{D}/raw/{m['name']}.jpg").convert('RGB')
    alpha=None
    if m['cut']:
        if sess is None:
            from rembg import new_session, remove
            sess=new_session('isnet-general-use')
        from rembg import remove
        rgba=remove(im,session=sess)
        alpha=np.asarray(rgba.split()[-1]).astype(float)/255
    g=np.asarray(im.convert('L')).astype(float)
    region=g[alpha>0.5] if alpha is not None else g
    lo,hi=np.percentile(region,1.5),np.percentile(region,96 if alpha is None else 99.5)
    v=np.clip((g-lo)/max(1,hi-lo),0,1)**1.08          # 0 = ink, 1 = paper
    rgb=(INK[None,None,:]*(1-v[...,None])+255*v[...,None])
    if alpha is None:
        out=Image.fromarray(rgb.astype(np.uint8),'RGB')
    else:
        a=(np.clip(alpha,0,1)*255).astype(np.uint8)
        out=Image.fromarray(np.dstack([rgb.astype(np.uint8),a]),'RGBA')
        bb=out.getbbox(); out=out.crop(bb)
    out.save(f"{D}/img/{m['name']}.png",optimize=True)
    m['size']=out.size
    print(m['name'],out.size,'cut' if alpha is not None else 'print',flush=True)
json.dump(meta,open(D+'/meta.json','w'),indent=1)
