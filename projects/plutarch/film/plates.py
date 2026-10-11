"""Download picked Met plates at full resolution (long side ≤ 3200 px) -> WORKDIR/plates/<id>.jpg, plates.json (aspect h/w), credits.json
usage: plates.py WORKDIR"""
import json, subprocess, sys, os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
WD = sys.argv[1]; os.makedirs(WD + "/plates", exist_ok=True)
picks = json.load(open(WD + "/picks.json")); AR = json.load(open(WD + "/plates.json")) if os.path.exists(WD + "/plates.json") else {}
cred = json.load(open(WD + "/credits.json")) if os.path.exists(WD + "/credits.json") else {}
ids = sorted({p["id"] for v in picks.values() for p in v})
for oid in ids:
    fn = f"{WD}/plates/{oid}.jpg"
    if os.path.exists(fn) and str(oid) in AR: continue
    d = json.loads(subprocess.run(["curl", "-s", "-m", "40", "-A", UA, f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"], capture_output=True).stdout or b"{}")
    if not d.get("isPublicDomain"): print("NOT PD", oid); continue
    subprocess.run(["curl", "-s", "-m", "180", "-A", UA, "-o", fn + ".o", d.get("primaryImage") or d["primaryImageSmall"]])
    im = Image.open(fn + ".o").convert("RGB"); im.thumbnail((3200, 3200), Image.LANCZOS); im.save(fn, quality=92); os.remove(fn + ".o")
    AR[str(oid)] = im.size[1] / im.size[0]; cred[str(oid)] = f"{d['title']} — {d.get('artistDisplayName') or 'unknown'}, {d.get('objectDate','')} (The Met, CC0)"
    print(oid, im.size, d["title"][:50], flush=True)
json.dump(AR, open(WD + "/plates.json", "w"), indent=0); json.dump(cred, open(WD + "/credits.json", "w"), indent=1)
