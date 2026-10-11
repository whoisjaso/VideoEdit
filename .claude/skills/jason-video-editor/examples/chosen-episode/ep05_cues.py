"""Ep05 v3 sound map (r20 sound spec): every cue on a spoken word, levelled by role, layered, the whole library in play.
python3 ep05_cues.py work2/ > cues_v3.json"""
import json, re, sys
W = sys.argv[1]
caps = json.load(open(W + "/captions.json")); edl = json.load(open(W + "/edl.json"))
key = lambda s: re.sub(r"[^A-Z0-9']", "", s.upper())
def at(tag, word, n=1):
    h = [c for c in caps if c["tag"] == tag and key(c["t"]) == key(word)]
    return h[n - 1]["f0"]
def sec(tag):
    p = [e for e in edl if e["tag"] == tag]; return p[0]["f0"], p[-1]["f1"]
CUT = edl[-1]["f1"]
C = []
def cue(f, id, role, **k): C.append(dict(f=int(f), id=id, role=role, **k))
# ── layered helpers (r20: lows + mids + highs; bass stacks start early) ──
def whoosh3(f, mid="pack4.ripple_textures"):
    cue(f, "whoosh", "whoosh", speed=0.6, db=-1)          # low: same whoosh slowed (tape pitch down)
    cue(f, mid, "texture")                                # mid: a texture
    cue(f, "whoosh", "whoosh", speed=1.25, db=-6)          # high: same whoosh sped up
def bass3(f, top="pack4.basscrack"):
    cue(f, top, "impact", pre=2)
    cue(f, "deep_bass", "sub", pre=3, db=-4)
    cue(f, "pack6.impact_1", "sub", pre=3, db=-9)
ticks = ["camera_shutter", "pack6.shutter"]

# 0 ─ hook card (open loop): something on frame 0, words land, "chosen" gets the full stack
cue(0, "pack6.impact_1", "impact", db=-2)
cue(0, "pack3.ui_02", "texture", db=2)                    # shimmer bed under the card
for i, (t, w) in enumerate([("cold", "HOW"), ("cold", "NIGGA"), ("cold2", "HE")]):
    cue(at(t, w), "pack5.typing_2", "typing")
cue(at("cold", "BEAT"), "pack4.cinestrike", "impact")
cue(at("cold", "BELIEVES"), "pack3.shine", "accent")
bass3(at("cold2", "CHOSEN"))
cue(at("cold2", "CHOSEN"), "pack5.sparkle", "accent", tail=True)
# 1 ─ checklist (iOS Notes): open, a tink per item, alternate tink/button so repeats don't sound identical
cue(at("hook", "IF") - 2, "ios.ios_note", "ui")
for i, (t, w) in enumerate([("hook", "DICK"), ("hook", "SIX"), ("hook", "AMAZING,"), ("hook", "HANDSOME,")]):
    cue(at(t, w) + 5, "ios.ios_tink", "ui", db=(-1 if i % 2 else 0))
cue(at("hook", "DICK"), "whoosh", "whoosh", db=-4)        # the punch-in on "dick"
# 2 ─ translate cards: received + digital typing (tech) + one glitch between languages
for f in [at("lang", "YO"), at("lang", "NI")]:
    cue(f - 3, "ios.ios_received", "notif")
    cue(f, "pack3.digital_text", "typing", db=4)
cue(at("lang", "NI") - 4, "ui.glitch_transition", "texture", db=-3)
# 3 ─ checklist returns, language lands
cue(sec("speak")[0], "pack5.button_3", "ui", db=-3)
for t, w in [("speak", "REAL"), ("speak", "SPEAK")]: cue(at(t, w) + 5, "ios.ios_tink", "ui")
cue(at("speak", "LANGUAGE."), "ui.reverb_hit", "impact", db=-4)
# 4 ─ gifted + engraving cutaways: old-flash texture on every bridge, tink on landings, success on the payoff
cue(at("gifted", "GIFTED."), "pack3.shine", "accent")
cue(at("gifted", "GIFTED."), "pack6.impact_2", "sub", db=-8)
INS = [(853, [874]), (972, [989]), (1170, [1185, 1250, 1327]), (2327, [2341, 2419, 2447, 2494])]
for i, (f, land) in enumerate(INS):
    cue(f, "pack3.old_flash", "texture", db=1)
    cue(f, "swoosh", "whoosh", speed=0.6, db=-3)
    for j, l in enumerate(land): cue(l, "ios.ios_tink", "accent", db=(0 if j < len(land) - 1 else 3))
cue(1327, "pack5.sparkle", "accent", tail=True)            # "high." — the summit
cue(at("gifted", "SHOUT") - 2, "pack5.combo", "ui", db=-3)  # sent iMessage
# 5 ─ the viewer turn
bass3(at("belief", "YOU", 1), top="pack6.impact_2")
cue(at("belief", "CANNOT"), "ui.negative_glitch_2", "ui", db=-2)
cue(at("belief", "CANNOT"), "pack4.basscrack", "impact", db=-3)
# 6 ─ confidence meter + can't tell me shit (slow-mo)
cue(at("confidence", "CONFIDENCE"), "pack3.counter", "ui")
cue(at("confidence", "HIGH."), "ui.success_ui", "ui")
cue(at("cantell", "CAN'T"), "pack4.cinestrike", "impact")
for e in [e for e in edl if e["speed"] < 1]:
    cue(e["f0"], "pack5.deep_whoosh", "slowmo", speed=0.6)   # curse slow-mo: deep, slowed whoosh
# 7 ─ the room: 1,000, the insults as messages, then SILENCE for his look (a hold is a sound)
bass3(at("room", "THOUSAND"))
for i, (t, w) in enumerate([("room", "JASON,"), ("room", "BLACK"), ("room", "FUCKING")]):
    cue(at(t, w) - 3, "ios.ios_tritone", "notif", db=i * 1.0)  # each insult a touch louder
# (no cues from LOOK to the ego line: the smile breathes)
cue(at("ego", "HIGH"), "pack4.cinestrike", "impact")
bass3(at("ego", "EGO."), top="pack6.impact_2")
# 8 ─ arrogant
cue(at("arrogant", "SORRY,") - 2, "pack5.button_1", "ui")
cue(at("arrogant", "NOT", 1), "ui.switch", "ui", db=2)
cue(at("arrogant", "ARROGANT"), "ui.reverb_hit", "impact")
cue(at("arrogant", "BETTER", 1), "pack5.button_2", "ui")
cue(at("arrogant", "LITERALLY"), "pack3.bicycle_chain", "texture", db=2)  # bars ratchet down
cue(at("arrogant", "AM."), "pack4.basscrack", "impact")
cue(at("superior", "SUPERIOR"), "pack3.shine", "accent", tail=True)
cue(at("superior", "CHOSEN"), "ios.ios_tink", "accent")
# 9 ─ payoff: 0.6 s of nothing before the line (silence = the drop), the hook card callback, riser into the engraving
cue(at("payoff", "BEAT"), "pack4.cinestrike", "impact")
cue(2327, "pack3.riser", "riser")                           # ends exactly on the cutaway
cue(2325, "pack6.tension", "riser", db=-6)
cue(2518, "ios.ios_success", "accent", db=4, tail=True)     # HaMashiach rings out (reverb end)
cue(2518, "pack6.impact_2", "sub", db=-6)
# 10 ─ closers + outro
cue(at("payoff2", "MAKE", 1) - 2, "pack6.ui_sfx", "ui")
cue(at("payoff2", "OR") - 1, "click", "ui", db=2)
cue(at("payoff2", "HAVE") - 2, "pack6.ui_sfx", "ui")
bass3(at("payoff2", "BITCH."))
cue(CUT + 20, "pop", "ui", db=-4)
cue(CUT + 52, "ding", "ui", tail=True)
# section cuts: alternate two shutters at tick level; the last cut before the payoff gets the bigger camera click
cuts = [e["f0"] for i, e in enumerate(edl[1:]) if edl[i]["tag"] != e["tag"] and e["speed"] == 1 and edl[i]["speed"] == 1]
for i, f in enumerate(cuts):
    big = f == max(c for c in cuts if c <= 2330)
    cue(f - 1, "pack3.camera_click" if big else ticks[i % 2], "tick", db=(4 if big else 0))
json.dump(sorted(C, key=lambda c: c["f"]), sys.stdout, indent=0)
