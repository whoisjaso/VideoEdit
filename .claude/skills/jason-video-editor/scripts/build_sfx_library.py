"""Builds the SFX library: measures every assets/sfx/**/*.wav and joins it with the hand-written job catalog below.
Usage: python3 scripts/build_sfx_library.py
Writes assets/sfx/library.json (read by template/src/lib/sfx.ts) and references/sfx-library.md (the human table).

Why `hit`: many sounds peak late (CineStrike 0.53s, shutter click 0.54s, Digital Text 1.34s). The reference reels land the
sound's PEAK on the frame of the motion (measured: audio-minus-visual median 3-45 ms). So every sound stores the time of
its peak, and <Hit> starts it `hit` seconds early. Placing the FILE START on the frame (what ep #3/#4 did) lands it late."""
import glob, json, os, subprocess
import numpy as np

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(SK, "assets", "sfx")

# id -> (job, default volume, when to use, origin).  origin: real = recorded pack / Apple system sound;
# lifted = cut from a reference reel (reference-grade); synth = generated stand-in (replace when Jason sends originals)
CAT = {
    # HOOK / OPEN: the first 0.5-2s, under the hook line
    "pack6/hook_1": ("hook", 0.5, "Under the first frame of a hook: rising build that peaks on the hook word", "lifted"),
    "pack6/hook_2": ("hook", 0.45, "Alternative hook build (longer); its peak lands on the hook word", "lifted"),
    # IMPACT: a hero word / statement lands
    "pack6/impact_1": ("impact", 0.5, "Hero word lands, statement that must land (bass-heavy hit)", "lifted"),
    "pack6/impact_2": ("impact", 0.5, "Second impact flavour; use on the closer / payoff so it differs from the hook impact", "lifted"),
    "pack4/cinestrike": ("impact", 0.5, "Giant hero word behind the head, trailer-style", "real"),
    "pack4/basscrack": ("impact", 0.5, "Hard truth / red hero word (BROKE, EGO)", "real"),
    "deep_bass": ("impact", 0.5, "Thesis line / bass impact under a font combo", "real"),
    "synth_hit": ("impact", 0.35, "Reveal hit (very loud file: keep at ~0.35)", "real"),
    "metallic_hit": ("impact", 0.4, "Metallic reveal (Metallic Riser job)", "real"),
    "ui/reverb_hit": ("impact", 0.45, "Card / scene lands, softer than a hero impact", "real"),
    # WHOOSH / MOVE: anything that moves fast, every zoom-in
    "whoosh": ("whoosh", 0.35, "Every zoom-in punch; element flying in", "real"),
    "swoosh": ("whoosh", 0.45, "Lighter move: card slides, swipe", "real"),
    "pack3/woosh": ("whoosh", 0.4, "Montage move / pan", "real"),
    "pack3/cinematic_woosh": ("whoosh", 0.4, "Big cinematic pass, scene change", "real"),
    "pack5/deep_whoosh": ("whoosh", 0.45, "Heavy whoosh into a takeover graphic / dark scene flip", "lifted"),
    "pack6/blade": ("whoosh", 0.4, "Sharp slice: wipe transition, text cut in", "lifted"),
    # SHUTTER / CUT: section changes (never on same-thought jump cuts)
    "camera_shutter": ("shutter", 0.18, "Section change cut (keep quiet: ~0.18)", "lifted"),
    "pack6/shutter": ("shutter", 0.3, "Section change / photo-style freeze", "lifted"),
    "pack6/camera_action": ("shutter", 0.35, "Fast montage cuts (<=8f), one per cut", "lifted"),
    "pack3/camera_click": ("shutter", 0.35, "Photo snap / screenshot moment ('Screenshot this')", "real"),
    # CLICK / POP: anything appears (pop-up, tile, check)
    "pop": ("click", 0.45, "Pop-up appears (pair with a click 2f later)", "synth"),
    "click": ("click", 0.35, "Pair with pop; cursor click", "synth"),
    "pack5/button_1": ("click", 0.5, "UI button press / card appears", "lifted"),
    "pack5/button_2": ("click", 0.5, "Second button flavour (alternate so repeats don't sound identical)", "lifted"),
    "pack5/button_3": ("click", 0.45, "Button with tail: list item lands", "lifted"),
    "pack5/combo": ("click", 0.45, "Click + whoosh in one: element pops AND moves", "lifted"),
    "pack6/ui_sfx": ("click", 0.45, "UI element appears (premium UI click)", "lifted"),
    "pack6/click_sfx": ("click", 0.45, "Click with tail: tile / panel locks in", "lifted"),
    "ui/switch": ("click", 0.5, "Toggle / switch flips (non-iOS context)", "real"),
    "ui/open_ui": ("click", 0.45, "App / panel opens", "real"),
    "snap": ("click", 0.4, "Finger snap: instant change", "real"),
    # TYPING / TEXT: words appear, captions, typed prompts
    "typing": ("typing", 0.08, "New caption line (very quiet: 0.08)", "synth"),
    "pack5/typing_2": ("typing", 0.3, "Short key tap: one word / chunk pops (kinetic type per word)", "lifted"),
    "ui/macbook_keyboard": ("typing", 0.35, "Typed prompt / search bar typing", "real"),
    "pack3/digital_text": ("typing", 0.35, "Digital text build (peaks late: use <Hit>)", "real"),
    # iOS (REAL Apple system sounds, 1:1 - locked rule)
    "ios/ios_tritone": ("ios", 0.5, "iMessage/notification banner drops in", "real"),
    "ios/ios_received": ("ios", 0.6, "Message received inside an open chat", "real"),
    "ios/ios_tink": ("ios", 0.9, "iOS toggle / checkbox tick / Reminders tick", "real"),
    "ios/ios_key": ("ios", 0.8, "iOS keyboard tap", "real"),
    "ios/ios_note": ("ios", 0.5, "Notes / note-style alert", "real"),
    "ios/ios_success": ("ios", 0.55, "Apple Pay / payment success / money in", "real"),
    "ios/ios_rings": ("ios", 0.55, "Activity rings close / goal hit", "real"),
    "ios/ios_lock": ("ios", 0.5, "Phone lock: end of a scene, 'done'", "real"),
    "ui/notification": ("ios", 0.4, "Generic app notification (non-Apple app)", "real"),
    # WIN / MONEY / SUCCESS
    "kaching": ("win", 0.45, "Money number lands (green)", "synth"),
    "ui/success_ui": ("win", 0.45, "Task done / check mark / result appears", "real"),
    "ding": ("win", 0.55, "Follow button flips to Following (bell)", "synth"),
    "pack3/counter": ("win", 0.45, "Numbers rolling up", "real"),
    # SPARKLE / REVEAL
    "pack5/sparkle": ("reveal", 0.45, "Reveal / 'the secret is…' / gold word glows", "lifted"),
    "pack3/shine": ("reveal", 0.5, "Shine on a gold/hero element, light-up (peaks late: use <Hit>)", "real"),
    # TENSION / BUILD
    "pack6/tension": ("build", 0.4, "Drone under a build-up; ends at the payoff (peaks at 3.7s: start it 3.7s early)", "lifted"),
    "riser": ("build", 0.3, "Short riser ending exactly on the payoff word", "synth"),
    "pack3/riser": ("build", 0.3, "Long riser (5s): end on the payoff", "real"),
    # NEGATIVE / PROBLEM
    "ui/negative_glitch_1": ("negative", 0.3, "Problem / wrong / red word", "real"),
    "ui/negative_glitch_2": ("negative", 0.3, "Problem variant", "real"),
    "ui/negative_glitch_3": ("negative", 0.3, "Problem variant (longer)", "real"),
    "pack4/distortion_glitch": ("negative", 0.25, "Harsh failure / crash (VERY loud file)", "real"),
    # TECH / GLITCH / DATA
    "ui/data_loading": ("tech", 0.3, "AI thinking / loading / processing", "real"),
    "ui/glitch_transition": ("tech", 0.35, "Glitch transition between scenes", "real"),
    "ui/gears": ("tech", 0.35, "Systems / building / automation", "real"),
    "ui/zap": ("tech", 0.4, "Electric / instant / power", "real"),
    "pack4/cyber_shift": ("tech", 0.4, "Tech scene shift", "real"),
    "pack3/nextel": ("tech", 0.35, "Retro phone chirp / walkie", "real"),
    "pack3/night_vision": ("tech", 0.35, "Scan / surveillance / night-vision look", "real"),
    "pack3/8bit_talking": ("tech", 0.3, "Retro game / 8-bit joke beat", "real"),
    # TEXTURE / TRANSITION
    "pack4/ripple_textures": ("texture", 0.4, "Card transition, ripple", "real"),
    "pack4/ripple_textures_2": ("texture", 0.4, "Card transition, darker ripple", "real"),
    "pack4/alienated_warps": ("texture", 0.35, "Warp into a surreal/abstract beat", "real"),
    "pack3/old_flash": ("texture", 0.4, "Old camera flash / memory", "real"),
    "pack3/bicycle_chain": ("texture", 0.4, "Mechanical ratchet / gear turning", "real"),
    "pack3/ui_01": ("texture", 0.35, "UI texture 1", "real"), "pack3/ui_02": ("texture", 0.35, "Soft UI shimmer", "real"),
    "pack3/ui_03": ("texture", 0.35, "UI texture 3", "real"), "pack3/ui_04": ("texture", 0.35, "UI texture 4", "real"),
    "pack3/ui_05": ("texture", 0.35, "UI texture 5", "real"), "pack3/ui_06": ("texture", 0.35, "UI texture 6", "real"),
    "pack3/ui_07": ("texture", 0.35, "UI texture 7", "real"),
}
JOB_ORDER = ["hook", "impact", "whoosh", "shutter", "click", "typing", "ios", "win", "reveal", "build", "negative", "tech", "texture"]
# what lands on the target frame: the PEAK (impacts, moves, builds) or the ONSET (UI/iOS/typing: the sound starts as the element appears)
ALIGN = {"hook": "peak", "impact": "peak", "whoosh": "peak", "shutter": "onset", "click": "onset", "typing": "onset", "ios": "onset",
         "win": "onset", "reveal": "peak", "build": "peak", "negative": "onset", "tech": "onset", "texture": "peak"}
JOB_RULE = {
    "hook": "First 0.5-2s only. One per video.",
    "impact": "Statements that must land, hero words. Ration: max ~1 per 8-10s or they stop hitting.",
    "whoosh": "Every zoom-in and every fast move. Peak on the frame the motion is fastest.",
    "shutter": "Section changes and fast montages only. Never on same-thought jump cuts (ep #2 rule).",
    "click": "Anything appears. Same pairing every time (conditioned reward). Alternate button_1/2 so repeats stay fresh.",
    "typing": "Kinetic type: one quiet tap per word/chunk; captions: one very quiet tap per new line.",
    "ios": "LOCKED: real Apple sounds 1:1 for every iOS UI graphic.",
    "win": "Money, success, done, follow flip.",
    "reveal": "Reveals, secrets, gold words lighting up.",
    "build": "Under a build-up; the END/peak lands on the payoff word.",
    "negative": "Problems, red words, failure.",
    "tech": "AI, data, systems, glitch.",
    "texture": "Card/scene transitions and atmosphere.",
}

def measure(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "22050", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    k = 220  # 10ms
    env = np.array([np.abs(x[i:i + k]).max() for i in range(0, len(x), k)]) if len(x) else np.zeros(1)
    n = min(len(x), 44100); S = np.abs(np.fft.rfft(x[:n] * np.hanning(n))); fr = np.fft.rfftfreq(n, 1 / 22050)
    pk = float(env.max()) if len(env) else 0.0
    onset = float(np.argmax(env > 0.3 * pk)) * 0.01 if pk > 0 else 0.0
    return {"dur": round(len(x) / 22050, 3), "hit": round(float(np.argmax(env)) * 0.01, 3), "onset": round(onset, 3),
            "rms_db": round(float(10 * np.log10(np.mean(x ** 2) + 1e-12)), 1), "centroid_hz": int((S * fr).sum() / (S.sum() + 1e-9)),
            "peaks": [round(float(v), 3) for v in np.interp(np.linspace(0, len(env) - 1, 48), np.arange(len(env)), env)]}

lib, missing = [], []
for f in sorted(glob.glob(os.path.join(SFX, "**", "*.wav"), recursive=True)):
    rel = os.path.relpath(f, SFX)[:-4]
    if rel not in CAT: missing.append(rel); continue
    job, vol, use, origin = CAT[rel]
    m = measure(f); al = ALIGN[job]
    lib.append({"id": rel.replace("/", "."), "file": f"sfx/{rel}.wav", "job": job, "vol": vol, "use": use, "origin": origin, "align": al,
                "lead": m["hit"] if al == "peak" else m["onset"], **m})
lib.sort(key=lambda s: (JOB_ORDER.index(s["job"]), s["id"]))
json.dump({"jobs": JOB_RULE, "sounds": lib}, open(os.path.join(SFX, "library.json"), "w"), indent=1)

md = ["# SFX Library", "", "Generated by `scripts/build_sfx_library.py` from `assets/sfx/**` (do not hand-edit; edit the CAT table in the script).",
      "Use in Remotion: `<Hit at={frame} id=\"pack6.impact_1\" />` from `template/src/lib/sfx.tsx`. It starts the file `lead` seconds early so the right moment lands ON `frame`:", "the **peak** for impacts/whooshes/reveals/builds, the **onset** for iOS/UI/clicks/typing (the sound starts as the element appears).", "",
      "**origin:** real = recorded pack or Apple system sound · lifted = cut from a reference reel (clean pack: comment \"SFX\" on that reel) · synth = generated stand-in, replace first.", ""]
for job in JOB_ORDER:
    md += [f"## {job.upper()}: {JOB_RULE[job]}", "", "| id | use for | lands on frame | lead | len | vol | origin |", "|---|---|---|---|---|---|---|"]
    md += [f"| `{s['id']}` | {s['use']} | {s['align']} | {s['lead']:.2f}s | {s['dur']:.2f}s | {s['vol']} | {s['origin']} |" for s in lib if s["job"] == job]
    md.append("")
open(os.path.join(SK, "references", "sfx-library.md"), "w").write("\n".join(md))
print(f"{len(lib)} sounds catalogued -> assets/sfx/library.json + references/sfx-library.md")
if missing: print("NOT IN CATALOG (add to CAT):", missing)
