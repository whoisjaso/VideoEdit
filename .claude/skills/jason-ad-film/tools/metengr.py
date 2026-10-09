import json, subprocess, sys, os, urllib.parse, numpy as np
from PIL import Image
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
out=sys.argv[1]  # usage: metengr.py OUTDIR [query ...] (no queries = the ad-film default list)
os.makedirs(out,exist_ok=True)
get=lambda u: subprocess.run(['curl','-s','-m','40','-A',UA,u],capture_output=True).stdout
Q=sys.argv[2:] or ["Durer rhinoceros","Durer engraving","Muybridge horse","Muybridge","anatomy engraving","skeleton engraving","botanical engraving","flower engraving","insect engraving","shell engraving","geometry engraving","perspective engraving","alphabet letter","calligraphy","astronomy engraving","moon","celestial","machine engraving","hand study","plaster cast","bust photograph","snowflake","crystal","architecture engraving","ornament engraving","feather","bird engraving","fish engraving","telescope","compass","globe","ship engraving"]
seen=set(); meta=[]
for q in Q:
    r=json.loads(get("https://collectionapi.metmuseum.org/public/collection/v1.1/search?hasImages=true&limit=10&q="+urllib.parse.quote(q)) or b'{}')
    n=0
    for oid in (r.get('objectIDs') or []):
        if oid in seen or n>=5: continue
        seen.add(oid)
        d=json.loads(get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}") or b'{}')
        if not d.get('isPublicDomain') or not d.get('primaryImageSmall'): continue
        fn=f"{out}/e_{oid}.jpg"
        if not os.path.exists(fn): subprocess.run(['curl','-s','-m','60','-A',UA,'-o',fn,d['primaryImageSmall']])
        try:
            im=Image.open(fn).convert('RGB'); a=np.asarray(im.resize((120,120))).astype(float)
            sat=(a.max(2)-a.min(2)).mean(); bright=a.mean()
        except Exception:
            if os.path.exists(fn): os.remove(fn)
            continue
        # engraving test: low colour, light paper
        if sat>38 or bright<120: os.remove(fn); continue
        n+=1
        meta.append({'id':oid,'title':d['title'],'artist':d.get('artistDisplayName'),'q':q,'big':d.get('primaryImage'),'sat':round(sat,1),'bright':round(bright,1)})
        json.dump(meta,open(f"{out}/meta.json",'w'),indent=1)   # saved as it goes, so a crash keeps the finds
        print(oid,'|',q,'|',d['title'][:48],'|',round(sat),round(bright),flush=True)
json.dump(meta,open(f"{out}/meta.json",'w'),indent=1)
