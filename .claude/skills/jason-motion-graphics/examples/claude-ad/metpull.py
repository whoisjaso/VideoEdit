import json, subprocess, sys, os, urllib.parse
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
def get(u):
    r=subprocess.run(['curl','-s','-m','40','-A',UA,u],capture_output=True); return r.stdout
Q=["Vermeer","Hokusai wave","Van Gogh","Monet","Rembrandt","Degas dancers","Sargent Madame X","marble head","Bruegel","Seurat","Cezanne","Klimt","bust","Egyptian statue","Greek kouros","Velazquez","David Socrates","Homer","Botticelli","Raphael"]
seen=set(); meta=[]
for q in Q:
    r=json.loads(get("https://collectionapi.metmuseum.org/public/collection/v1.1/search?isHighlight=true&hasImages=true&limit=6&q="+urllib.parse.quote(q)) or b'{}')
    for oid in (r.get('objectIDs') or [])[:4]:
        if oid in seen: continue
        seen.add(oid)
        d=json.loads(get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}") or b'{}')
        if not d.get('isPublicDomain') or not d.get('primaryImage'): continue
        fn=f"{out}/met_{oid}.jpg"
        subprocess.run(['curl','-s','-m','90','-A',UA,'-o',fn+'.orig',d['primaryImage']])
        subprocess.run(['convert',fn+'.orig','-resize','1800x1800>','-quality','92',fn]); os.remove(fn+'.orig')
        meta.append({'id':oid,'title':d['title'],'artist':d.get('artistDisplayName'),'date':d.get('objectDate'),'q':q,'file':os.path.basename(fn)})
        print(oid,'|',d['title'][:50],'|',d.get('artistDisplayName'),flush=True)
json.dump(meta,open(f"{out}/meta.json",'w'),indent=1)
