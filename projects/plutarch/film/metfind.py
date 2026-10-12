"""Find public-domain Met images per scene and build labelled contact sheets for picking.
usage: metfind.py OUTDIR  (queries below) -> OUTDIR/sNN.jpg sheets + OUTDIR/cands.json"""
import json, subprocess, sys, os, urllib.parse
from PIL import Image, ImageDraw
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
out = sys.argv[1]; os.makedirs(out + "/img", exist_ok=True)
get = lambda u: subprocess.run(["curl", "-s", "-m", "40", "-A", UA, u], capture_output=True).stdout
Q = {
 0: ["Napoleon Bonaparte", "Napoleon young", "Plutarch Lives frontispiece", "candlelight reading"],
 1: ["Plutarch", "philosopher bust", "scroll writing antique", "oil lamp"],
 2: ["Olympias", "Philip of Macedon", "temple of Diana Ephesus", "Jupiter thunderbolt", "lion engraving"],
 3: ["Alexander the Great youth", "Persian ambassadors", "Darius king Persia", "ancient world map"],
 5: ["Aristotle", "Aristotle Alexander", "Achilles", "Homer", "Iliad"],
 6: ["death of Philip Macedon", "Alexander the Great", "Thebes", "assassination"],
 7: ["Diogenes", "Diogenes Alexander", "Diogenes lantern", "Corinth"],
 8: ["Granicus", "battle of Granicus", "Clitus", "cavalry battle"],
 9: ["Alexander physician", "Alexander Philip physician", "medicine cup", "fever sick bed"],
 10: ["family of Darius", "tent of Darius", "Darius", "queens of Persia"],
 11: ["Jupiter Ammon", "oracle", "Egyptian temple desert", "siege of Tyre"],
 12: ["battle of Arbela", "Gaugamela", "Darius death", "army camp night"],
 13: ["entry Alexander Babylon", "triumph of Alexander", "Babylon", "Callisthenes"],
 14: ["Clitus death", "Alexander Clitus", "banquet", "feast drinking"],
 15: ["Porus", "Alexander Porus", "elephants battle", "desert soldiers"],
 16: ["death of Alexander", "Alexander deathbed", "Babylon ruins"],
 17: ["Alexander the Great portrait", "candle", "Alexander head coin"],
}
cands = {}
for sc, qs in Q.items():
    seen = set(); items = []
    for q in qs:
        r = json.loads(get("https://collectionapi.metmuseum.org/public/collection/v1.1/search?hasImages=true&limit=30&q=" + urllib.parse.quote(q)) or b"{}")
        n = 0
        for oid in (r.get("objectIDs") or [])[:30]:
            if oid in seen or n >= 6: continue
            seen.add(oid)
            d = json.loads(get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}") or b"{}")
            if not d.get("isPublicDomain") or not d.get("primaryImageSmall"): continue
            fn = f"{out}/img/{oid}.jpg"
            if not os.path.exists(fn): subprocess.run(["curl", "-s", "-m", "60", "-A", UA, "-o", fn, d["primaryImageSmall"]])
            try: Image.open(fn).verify()
            except Exception: continue
            items.append({"id": oid, "q": q, "title": d["title"][:60], "artist": (d.get("artistDisplayName") or "")[:30], "date": d.get("objectDate", "")})
            n += 1
    cands[sc] = items
    # sheet
    W, H, C = 300, 260, 6; rows = (len(items) + C - 1) // C
    sh = Image.new("RGB", (W * C, max(1, rows) * H), "white"); dr = ImageDraw.Draw(sh)
    for i, it in enumerate(items):
        im = Image.open(f"{out}/img/{it['id']}.jpg").convert("RGB"); im.thumbnail((W - 8, H - 44))
        x, y = (i % C) * W, (i // C) * H; sh.paste(im, (x + 4, y + 4))
        dr.text((x + 4, y + H - 38), f"{it['id']} {it['title'][:40]}", fill="black"); dr.text((x + 4, y + H - 24), f"{it['artist'][:28]} {it['date'][:14]}", fill="gray")
    sh.save(f"{out}/s{sc:02d}.jpg", quality=80); print(sc, len(items), flush=True)
json.dump(cands, open(out + "/cands.json", "w"), indent=1)
