# usage: metpick.py OUTDIR id:name[:cut] ...   -> OUTDIR/raw/NAME.jpg (full-res original, resized to 2000 px), meta.json
import json, subprocess, sys, os
from PIL import Image
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
out=sys.argv[1]; os.makedirs(out+'/raw',exist_ok=True); meta=[]
for spec in sys.argv[2:]:
    oid,name,*rest=spec.split(':')
    d=json.loads(subprocess.run(['curl','-s','-m','40','-A',UA,f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"],capture_output=True).stdout or b'{}')
    if not d.get('isPublicDomain'): print('SKIP not PD',oid); continue
    fn=f"{out}/raw/{name}.jpg"
    subprocess.run(['curl','-s','-m','120','-A',UA,'-o',fn+'.o',d['primaryImage'] or d['primaryImageSmall']])
    im=Image.open(fn+'.o').convert('RGB'); im.thumbnail((2000,2000)); im.save(fn,quality=94); os.remove(fn+'.o')
    meta.append({'id':int(oid),'name':name,'title':d['title'],'artist':d.get('artistDisplayName'),'date':d.get('objectDate'),'cut':bool(rest)})
    print(oid,name,im.size,d['title'][:50],flush=True)
json.dump(meta,open(out+'/meta.json','w'),indent=1)
