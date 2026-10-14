"""Motion graphics for Lead With Questions (spec §12): V1-V8, both cuts, 16:9 and 9:16.

    python projects/lead-with-questions/lwq_visual.py night 16x9 --frames 30 300 900     # sample PNGs
    python projects/lead-with-questions/lwq_visual.py night 16x9 --render out.mp4        # silent video

Parameters live in the CONFIG dicts below. Everything is procedural except the five M4 scene photos.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("LWQ_WORK", "/tmp/lwq"))
FPS = 30
INTER = Path("/usr/share/fonts/opentype/inter")
FONTS = HERE / "fonts"

# palette (§12.2)
VOID = np.array([3, 4, 9], np.float32)
MIDNIGHT = np.array([10, 16, 32], np.float32)
INDIGO = np.array([22, 26, 56], np.float32)
EMBER = np.array([156, 107, 60], np.float32)
MOON = (140, 147, 163)
NAVY = np.array([20, 33, 61], np.float32)
RUST = np.array([200, 85, 61], np.float32)
GOLD = np.array([242, 181, 68], np.float32)
CREAM = np.array([250, 243, 227], np.float32)
STEEL = np.array([58, 74, 92], np.float32)
INK = (17, 18, 20)

CONFIG = dict(
    circle_diam=0.34,          # V1: share of frame height (16:9) / width*0.62 (9:16)
    particles=200,             # V2
    fractal_orbit_s=240.0,     # V3: one full parameter orbit
    bands=10,                  # V4
    lantern_sigma=0.19,        # V5: glow radius as a share of frame height
    grain_night=0.010, grain_morning=0.015,   # V8
    night_cap_early=64, night_cap=38,         # §12.2 luminance limits (sRGB levels)
)


def ease(x):
    x = np.clip(x, 0, 1)
    return 0.5 - 0.5 * np.cos(np.pi * x)


def ramp(t, a, b):
    return float(ease((t - a) / max(1e-6, b - a)))


def win(t, a, b, fin, fout):
    """1 inside [a, b] with cosine fades."""
    if t < a or t > b:
        return 0.0
    return min(ramp(t, a, a + fin), 1 - ramp(t, b - fout, b))


# ================================================================ plan

M3_CARDS = [("Here's who you are", "WHO YOU ARE TODAY"), ("I lead with", "I LEAD WITH QUESTIONS."),
            ("Talking isn't", "ASKING IS LEADING."), ("Nobody's coming", "I STEER IT. WITH A QUESTION."),
            ("I don't chase", "I DON'T CHASE. I ASK."), ("Overthinking", "TURN IT DOWN. ASK."),
            ("I don't need the perfect", "THE NEXT QUESTION."), ("Thinking poor", "THINKING RICH ASKS WHAT THEY NEED."),
            ("I let silence", "SILENCE DOES THE CLOSING."), ("My numbers", "SAY THE PRICE ONCE."),
            ("I give before", "I GIVE BEFORE I ASK."), ("One conversation", "ONE LANE. ONE NEXT STEP."),
            ("I don't do guilt", "NO GUILT. NO FAKE DEADLINES."), ('A "no"', "A NO IS INFORMATION."),
            ("I'd be fine", "NOTHING TO HIDE."), ("Jason... you lead", "YOU LEAD WITH QUESTIONS."),
            ("Jason... you've done", "YOU'VE DONE THE REPS."), ("Jason... go hold", "GO HOLD THE LIGHT.")]
M4_SCENES = {"M4.1": ("lot.jpg", "WHAT'S GOT YOU LOOKING?"), "M4.2": ("owner.jpg", "WHAT HAPPENS AT 9 P.M.?"),
             "M4.3": ("investor.jpg", "WHAT MAKES THIS A CLEAR YES?"), "M4.4": ("boardroom.jpg", "WHY NOW?"),
             "M4.5": ("interview.jpg", "WHAT'S A CLEAR WIN IN 90 DAYS?")}
M5_CARDS = [("When I feel the urge", "URGE TO EXPLAIN? I ASK."),
            ("When they hit me", "THREE QUESTIONS? ONE BACK."),
            ("When they say it's too much", "TOO MUCH? COMPARED TO WHAT?"),
            ("When it goes quiet", "QUIET? COUNT TO FIVE.")]
NIGHT_LABELS = {"N6.1": "LOT", "N6.2": "OWNER", "N6.3": "INVESTOR", "N6.4": "BOARDROOM", "N6.5": "INTERVIEW"}
SAFETY = ("Don't listen while driving or doing anything that needs your attention. "
          "Not medical advice. Headphones for the binaural tones. No flashing visuals.")


def make_plan(cut):
    tl = json.loads((WORK / cut / "timeline.json").read_text())
    ev = tl["events"]
    says = [e for e in ev if e["kind"] == "say"]
    S = {s["sid"]: s["start"] for s in tl["sections"]}
    U = {u["sid"]: u for u in tl["units"]}
    plan = dict(cut=cut, total=tl["total"], S=S, tones=[e["t"] for e in ev if e["kind"] == "tone"])
    sec1 = "N1" if cut == "night" else "M1"
    plan["breaths"] = [(e["phase"], e["t"], e["end"]) for e in ev if e["kind"] == "breath" and e["unit"] == sec1]
    if cut == "night":
        free = next(e for e in ev if e["kind"] == "pause" and e["unit"] == "N1" and e["scripted"] == 20)
        t = free["t"] + 0.5
        while t + 10 <= free["t"] + free["dur"] + 0.5:
            plan["breaths"] += [("in", t, t + 4), ("out", t + 4, t + 10)]
            t += 10
        words = ["Ten.", "Nine.", "Eight.", "Seven.", "Six.", "Five.", "Four.", "Three.", "Two.", "And one."]
        plan["counts"] = [next(e["t"] for e in says if e["unit"] == "N3" and e["text"].startswith(w)) for w in words]
        plan["asks"] = [e["t"] for e in says if e["unit"] == "N7" and e["text"].strip(" .*") == "Ask"]
        plan["labels"] = [(U[k]["first_voice"] - 0.5, v) for k, v in NIGHT_LABELS.items()]
    else:
        plan["steady"] = next(e["t"] for e in says if e["unit"] == "M2" and "steady" in e["text"])
        plan["sharp"] = next(e["t"] for e in says if e["unit"] == "M2" and "sharp" in e["text"])
        cards = []
        m3 = [e for e in says if e["unit"] == "M3" and e["role"] != "B"]
        last_end = -1
        for e in m3:
            for pre, card in M3_CARDS:
                if e["text"].startswith(pre):
                    words = len(card.split())
                    dur = max(2.5 + 0.3 * words, e["dur"] + 0.6)
                    if e["t"] >= last_end:
                        cards.append((e["t"], e["t"] + dur, card))
                        last_end = e["t"] + dur
        q = next(e for e in says if e["unit"] == "M5" and e["text"].startswith("What's the first"))
        qp = next(x for x in ev if x["kind"] == "pause" and x["unit"] == "M5" and x["t"] > q["t"])
        cards.append((q["t"], qp["t"] + qp["dur"], "YOUR FIRST QUESTION?"))
        for pre, card in M5_CARDS:
            e = next(x for x in says if x["unit"] == "M5" and x["text"].startswith(pre))
            cards.append((e["t"], e["t"] + max(2.5 + 0.3 * len(card.split()), e["dur"] + 1.5), card))
        plan["cards"] = cards
        plan["scenes"] = [(U[k]["start"], U[k]["end"], img, qtext) for k, (img, qtext) in M4_SCENES.items()]
        nums = []
        for w, d in zip(["One.", "Two.", "Three.", "Four.", "Five."], "12345"):
            nums.append((next(e["t"] for e in says if e["unit"] == "M6" and e["text"].startswith(w)), d))
        plan["numbers"] = nums
        plan["five"] = nums[-1][0]
        last = next(e for e in says if e["unit"] == "M7" and e["text"].startswith("Now go lead"))
        plan["askfirst"] = last["t"] + last["dur"] + 0.6
    return plan


# ================================================================ renderer

class R:
    def __init__(self, plan, aspect):
        self.p = plan
        self.night = plan["cut"] == "night"
        self.W, self.H = (1920, 1080) if aspect == "16x9" else (1080, 1920)
        self.vert = aspect == "9x16"
        self.w, self.h = self.W // 2, self.H // 2
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.xx, self.yy = xx, yy
        self.cx = self.w / 2
        self.cy = self.h * (0.45 if self.vert else 0.5)
        rng = np.random.default_rng(3)
        n = CONFIG["particles"]
        self.px = rng.uniform(0, self.w, n)
        self.py = rng.uniform(0, self.h, n)
        self.pv = rng.uniform(1, 3, n) * (self.H / 1080)            # 2-6 px/s at full res
        self.pa = rng.uniform(0.10, 0.30, n)
        self.pb = rng.random(n) < 0.5
        self.pph = rng.uniform(0, 6.28, (n, 2))
        self.pw = rng.uniform(0.03, 0.08, n)
        rng2 = np.random.default_rng(9)
        self.grain = [rng2.standard_normal((self.H, self.W)).astype(np.float32)]   # static dither: kills banding, keeps bitrate sane
        self.R0 = (CONFIG["circle_diam"] / 2) * (self.h if not self.vert else self.w * 0.62)
        self.fonts = {}
        self.text_cache = {}
        self.imgs = {}

    # ---------------- helpers
    def font(self, path, size):
        k = (str(path), size)
        if k not in self.fonts:
            self.fonts[k] = ImageFont.truetype(str(path), size)
        return self.fonts[k]

    def text_layer(self, key, lines, font, color, align="center", track=0.0, x=None, y=None):
        """RGBA layer (full res) with the text drawn once; cached."""
        if key in self.text_cache:
            return self.text_cache[key]
        img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        lh = int(font.size * 1.18)
        total_h = lh * len(lines)
        y0 = (self.H - total_h) / 2 if y is None else y - total_h / 2
        for i, ln in enumerate(lines):
            widths = [d.textlength(ch, font=font) for ch in ln]
            sp = font.size * track
            tw = sum(widths) + sp * max(0, len(ln) - 1)
            if align == "center":
                x0 = (self.W - tw) / 2
            else:
                x0 = x
            cx = x0
            for ch, wd in zip(ln, widths):
                d.text((cx, y0 + i * lh), ch, font=font, fill=color + (255,))
                cx += wd + sp
        self.text_cache[key] = np.asarray(img).astype(np.float32)
        return self.text_cache[key]

    def wrap(self, text, font, maxw):
        d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) * 1.06 <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines

    @staticmethod
    def comp(img, layer, alpha, dy=0):
        if alpha <= 0.002:
            return
        a = layer[..., 3:4] / 255.0 * alpha
        if dy:
            dy = int(dy)
            a = np.roll(a, -dy, axis=0)
            rgb = np.roll(layer[..., :3], -dy, axis=0)
        else:
            rgb = layer[..., :3]
        img *= (1 - a)
        img += rgb * a

    def particles(self, t, amount, colors):
        if amount <= 0.002:
            return 0.0
        y = (self.py - self.pv * t / 2) % (self.h + 20) - 10
        x = self.px + 6 * np.sin(self.pw * t + self.pph[:, 0]) + 3 * np.sin(0.37 * self.pw * t + self.pph[:, 1])
        layers = []
        for blur, sig in ((False, 0.8), (True, 2.2)):
            m = self.pb == blur
            acc = np.zeros((self.h, self.w), np.float32)
            xi = np.clip(x[m].astype(int), 0, self.w - 1)
            yi = np.clip(y[m].astype(int), 0, self.h - 1)
            np.add.at(acc, (yi, xi), self.pa[m])
            acc = gaussian_filter(acc, sig) * (2 * np.pi * sig * sig) * 0.9
            layers.append(acc)
        a = np.clip(layers[0] + layers[1], 0, 1) * amount
        return a[..., None] * colors

    def glow(self, x, y, sigma, amp, color):
        g = np.exp(-(((self.xx - x) ** 2 + (self.yy - y) ** 2) / (2 * sigma * sigma)))
        return (g * amp)[..., None] * color

    def ring(self, scale, alpha, color, fill=0.0, cx=None, cy=None, R=None):
        cx = self.cx if cx is None else cx
        cy = self.cy if cy is None else cy
        R = (self.R0 if R is None else R) * scale
        r = np.sqrt((self.xx - cx) ** 2 + (self.yy - cy) ** 2)
        ring = np.exp(-((r - R) / 1.2) ** 2) + 0.35 * np.exp(-((r - R) / 10.0) ** 2)
        if fill > 0:
            ring = ring * (1 - fill) + fill * (1 / (1 + np.exp((r - R) / 1.5))) + fill * 0.5 * np.exp(-((r - R) / 18.0) ** 2)
        return (ring * alpha)[..., None] * color

    def breath_scale(self, t, inhale_from=0.85):
        for phase, a, b in self.p["breaths"]:
            if a <= t <= b:
                u = ease((t - a) / (b - a))
                return inhale_from + (1 - inhale_from) * u if phase == "in" else 1 - (1 - inhale_from) * u, True
        return 0.985 + 0.015 * np.cos(2 * np.pi * t / 12.0), False

    def julia(self, t, t0):
        lw, lh = (240, 135) if not self.vert else (135, 240)
        th = 2 * np.pi * (t - t0) / CONFIG["fractal_orbit_s"]
        c = 0.7885 * np.exp(1j * th)
        zoom = 1.6 * (1 - 0.003 * (t - t0) / 1.0) if t - t0 < 200 else 1.6 * 0.4
        ys, xs = np.mgrid[-1:1:lh * 1j, -1:1:lw * 1j]
        ar = lw / lh
        z = (xs * ar + 1j * ys) * zoom
        it = np.zeros(z.shape, np.float32)
        alive = np.ones(z.shape, bool)
        for i in range(36):
            z[alive] = z[alive] ** 2 + c
            esc = alive & (np.abs(z) > 4)
            it[esc] = i + 1 - np.log2(np.log(np.abs(z[esc]) + 1e-9) + 1e-9)
            alive &= ~esc
        it[alive] = 36
        v = np.clip(it / 36, 0, 1) ** 0.7
        v = gaussian_filter(v, 1.2)
        img = Image.fromarray((v * 255).astype(np.uint8)).resize((self.w, self.h), Image.BILINEAR)
        return np.asarray(img).astype(np.float32) / 255

    def finish(self, half, t, grain, cap=None):
        if cap is not None:                      # hue-preserving luminance ceiling
            m = half.max(axis=2, keepdims=True)
            half = half * np.minimum(1.0, cap / np.maximum(m, 1e-3))
        img = np.asarray(Image.fromarray(np.clip(half, 0, 255).astype(np.uint8)).resize((self.W, self.H), Image.BILINEAR))
        img = img.astype(np.float32)
        return img

    # ---------------- night
    def night_frame(self, t):
        p, S = self.p, self.p["S"]
        if t >= 1500:
            return np.zeros((self.H, self.W, 3), np.uint8)
        f = np.zeros((self.h, self.w, 3), np.float32)
        grad = (self.yy / self.h)[..., None]
        bg = VOID * (0.6 + 0.4 * grad) + (MIDNIGHT - VOID) * 0.35 * (1 - grad)
        dim = 1.0 - ramp(t, S["N9"], 1500)
        f += bg * dim
        # V2 particles
        amt = ramp(t, 16, 45) * (1 - 0.4 * ramp(t, S["N2"], S["N3"])) * (1 - ramp(t, S["N9"], 1500))
        if t >= 16:
            f += self.particles(t, amt, EMBER * 0.9)
        # V1 circle
        ca = ramp(t, S["N1"] - 2, S["N1"] + 2) * (1 - 0.5 * ramp(t, S["N2"], S["N2"] + 60)) * (1 - ramp(t, S["N3"], S["N3"] + 8))
        if ca > 0:
            sc, _ = self.breath_scale(t)
            f += self.ring(sc, 0.9 * ca, np.array([190, 160, 120], np.float32) * 0.42)
        # V3 fractal
        fa = (0.20 * ramp(t, S["N3"], S["N3"] + 20) + 0.05 * ramp(t, S["N4"], S["N4"] + 10)) * (1 - ramp(t, S["N5"], S["N6"]))
        if fa > 0.003:
            v = self.julia(t, S["N3"])
            col = MIDNIGHT[None, None] * (1 - v[..., None]) + INDIGO[None, None] * v[..., None]
            f = f * (1 - fa) + col * fa + f * fa * 0.0
        # V4 bands
        if S["N3"] <= t < S["N4"] + 6:
            nb = CONFIG["bands"]
            bands = np.zeros((self.h, self.w), np.float32)
            xe = np.clip(np.minimum(self.xx[0] / (0.2 * self.w), (self.w - self.xx[0]) / (0.2 * self.w)), 0, 1)
            xe = ease(xe)
            for i in range(nb):
                y = self.h * (0.56 + 0.38 * i / (nb - 1))
                ct = p["counts"][i]
                a = (1 - ramp(t, ct, ct + 1.5)) * ramp(t, S["N3"], S["N3"] + 4) * (1 - ramp(t, S["N4"], S["N4"] + 6))
                if a > 0:
                    bands += a * np.exp(-((self.yy[:, 0] - y) / (self.h * 0.011)) ** 2)[:, None] * xe[None, :]
            f += bands[..., None] * EMBER * 0.22
        # V5 lantern
        la = ramp(t, S["N4"] - 2, S["N4"] + 8) * (1 - ramp(t, S["N9"], 1495))
        if la > 0:
            x0, x1 = self.w / 3, 2 * self.w / 3
            if t < S["N5"]:
                x = x0 + (x1 - x0) * ease((t - S["N4"]) / (S["N5"] - S["N4"]))
            else:
                x = x1 + (self.w / 2 - x1) * ramp(t, S["N5"], S["N5"] + 12)
            amp = 1.0
            sig = CONFIG["lantern_sigma"] * self.h
            if t >= S["N6"]:
                k = ramp(t, S["N6"], S["N6"] + 8)
                sig *= 1 - 0.35 * k
                amp *= 1 - 0.45 * k
                for tt in p["tones"]:
                    if tt <= t < tt + 4:
                        x += 0.02 * self.w * np.sin(np.pi * (t - tt) / 4)
            if t >= S["N7"]:
                amp *= 1 + 0.45 * ramp(t, S["N7"], S["N7"] + 6)
                for a in p["asks"]:
                    if a <= t < a + 4:
                        amp *= 1 + 0.03 * (1 - ramp(t, a + 1, a + 4)) * ramp(t, a, a + 1) / 0.03 * 0.03 / 0.03 * 0.03 / 0.03
            if t >= S["N8"]:
                amp *= 1 - 0.65 * ramp(t, S["N8"], S["N9"])
            amp *= la
            f += self.glow(x, self.cy, sig, 0.17 * amp, EMBER) + self.glow(x, self.cy, sig * 0.25, 0.05 * amp, EMBER * 1.1)
        cap = CONFIG["night_cap_early"] if t < S["N3"] else CONFIG["night_cap"]
        img = self.finish(f, t, True, cap)
        # text
        fs = 56 if self.vert else 40
        fnt = self.font(INTER / "Inter-Light.otf", fs)
        if t < 8.6:
            lay = self.text_layer("safety", self.wrap(SAFETY.upper(), fnt, self.W * (0.62 if self.vert else 0.7)),
                                  fnt, MOON, track=0.06)
            self.comp(img, lay, 0.6 * win(t, 0.0, 8.0, 0.6, 0.8))
        if 8 <= t < 16.5:
            big = self.font(INTER / "Inter-Light.otf", int(fs * 1.5))
            lay = self.text_layer("title", ["LEAD WITH", "QUESTIONS"] if self.vert else ["LEAD WITH QUESTIONS"], big, MOON, track=0.06, y=self.H * 0.47)
            lay2 = self.text_layer("title2", ["NIGHT INSTALL"], fnt, MOON, track=0.06, y=self.H * 0.47 + fs * (3.2 if self.vert else 2.2))
            a = 0.6 * win(t, 8.0, 16.0, 0.6, 0.8)
            self.comp(img, lay, a, dy=20 * (t - 8) / 8)
            self.comp(img, lay2, a * 0.8, dy=20 * (t - 8) / 8)
        for t0, lab in p["labels"]:
            if t0 <= t < t0 + 4.2:
                lay = self.text_layer("lab" + lab, [lab], fnt, MOON, track=0.06)
                self.comp(img, lay, 0.10 * win(t, t0, t0 + 4.0, 0.6, 0.8))
        img += (self.grain[0] * (CONFIG["grain_night"] * 255))[..., None]
        return np.clip(img, 0, 255).astype(np.uint8)

    # ---------------- morning
    def dawn(self, t):
        p, S = self.p, self.p["S"]
        five = p["five"]
        pts = [(0, 0.0), (S["M2"], 0.10), (p["steady"] + 0.5, 0.10), (p["steady"] + 2.5, 0.17),
               (p["sharp"] + 0.5, 0.17), (p["sharp"] + 2.5, 0.24), (S["M3"], 0.28), (S["M4"], 0.50),
               (S["M5"], 0.64), (S["M6"], 0.72), (five - 0.2, 0.86), (five + 1.5, 1.0), (700, 1.0)]
        ts, vs = zip(*pts)
        u = float(np.interp(t, ts, vs))
        if S["M6"] <= t < five + 1.5:
            u = float(np.interp(t, ts, vs))
        return u

    def grad_colors(self, u):
        keys = [(0.0, NAVY * 0.45, NAVY * 0.9), (0.3, NAVY * 0.8, RUST * 0.75), (0.65, STEEL * 1.3, GOLD * 0.9),
                (0.86, STEEL * 2.2, GOLD), (1.0, CREAM, CREAM * 0.55 + GOLD * 0.45)]
        for (ua, ta, ba), (ub, tb, bb) in zip(keys, keys[1:]):
            if u <= ub:
                k = (u - ua) / (ub - ua)
                return ta + (tb - ta) * k, ba + (bb - ba) * k
        return keys[-1][1], keys[-1][2]

    def scene_img(self, name):
        if name not in self.imgs:
            im = Image.open(HERE / "assets" / name).convert("RGB")
            W2, H2 = int(self.W * 1.03), int(self.H * 1.03)
            s = max(W2 / im.width, H2 / im.height)
            im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
            l, tp = (im.width - W2) // 2, (im.height - H2) // 2
            im = im.crop((l, tp, l + W2, tp + H2))
            a = np.asarray(im).astype(np.float32) * np.array([1.06, 0.98, 0.86], np.float32)
            self.imgs[name] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return self.imgs[name]

    def morning_frame(self, t):
        p, S = self.p, self.p["S"]
        u = self.dawn(t)
        top, bot = self.grad_colors(u)
        g = (self.yy / self.h)[..., None]
        f = top * (1 - g) + bot * g
        five = p["five"]
        # sun position / circle
        sx = self.w * (0.5 if self.vert else 0.68)
        if t < S["M2"]:
            ca = ramp(t, S["M1"] - 2, S["M1"] + 2)
            sc, _ = self.breath_scale(t)
            if ca > 0:
                f += self.ring(sc, ca * 0.9, CREAM * 0.55)
        else:
            k = ramp(t, S["M2"], S["M2"] + 5)
            y_low, y_high = self.h * 0.85, self.h * 0.40
            sy = y_low + (y_high - y_low) * ease((t - S["M2"] - 5) / (five - S["M2"] - 5))
            cx = self.cx + (sx - self.cx) * k
            cy = self.cy + (sy - self.cy) * k
            R = self.R0 + (self.h * 0.06 - self.R0) * k
            col = (GOLD * (1 - u) + CREAM * u) * (0.55 + 0.45 * u)
            f += self.glow(cx, cy, R * 3.5, 0.25 + 0.25 * u, GOLD * 0.8)
            f += self.ring(1.0, 0.9, col, fill=k, cx=cx, cy=cy, R=R)
        # particles in M0-M2 (cool -> warm)
        amt = (1 - ramp(t, S["M3"] - 4, S["M3"])) * ramp(t, 3, 8)
        if amt > 0:
            col = np.array([150, 170, 200], np.float32) * (1 - u * 3) + CREAM * min(1, u * 3)
            f += self.particles(t, amt * 1.4, np.clip(col, 0, 255))
        img = self.finish(f, t, True)
        # V7 scene images
        for a, b, name, q in p["scenes"]:
            al = win(t, a, b, 1.0, 1.0)
            if al > 0:
                im = self.scene_img(name)
                z = 1.0 + 0.02 * (t - a) / (b - a)
                cw, ch = im.width / z, im.height / z
                l, tp = (im.width - cw) / 2, (im.height - ch) / 2
                fr = np.asarray(im.resize((self.W, self.H), Image.BILINEAR, box=(l, tp, l + cw, tp + ch))).astype(np.float32)
                yy = np.linspace(0, 1, self.H)[:, None, None]
                shade = 1 - 0.55 * (yy if self.vert else np.linspace(0, 1, self.H)[:, None, None] * 0.6 +
                                    (1 - np.linspace(0, 1, self.W))[None, :, None] * 0.4)
                fr = fr * shade
                img[:] = img * (1 - 0.65 * al) + fr * 0.65 * al
                fq = self.font(FONTS / "ArchivoBlack-Regular.ttf", 120 if self.vert else 92)
                lines = self.wrap(q, fq, self.W * (0.8 if self.vert else 0.5))
                if self.vert:
                    lay = self.text_layer("q" + q, lines, fq, tuple(CREAM.astype(int)), y=self.H * 0.6)
                else:
                    lay = self.text_layer("q" + q, lines, fq, tuple(CREAM.astype(int)), align="left",
                                          x=self.W * 0.1, y=self.H * 0.68)
                self.comp(img, lay, win(t, a + 0.5, b - 0.3, 0.3, 0.4), dy=20 * (t - a) / (b - a))
        # cards
        dark = u < 0.78
        fc = self.font(FONTS / "ArchivoBlack-Regular.ttf", 120 if self.vert else 96)
        for a, b, text in p["cards"]:
            if a <= t < b:
                lines = self.wrap(text, fc, self.W * (0.82 if self.vert else 0.5))
                col = tuple(CREAM.astype(int)) if dark else INK
                if self.vert:
                    lay = self.text_layer(("c", text, col), lines, fc, col, y=self.H * 0.5)
                else:
                    lay = self.text_layer(("c", text, col), lines, fc, col, align="left", x=self.W * 0.1, y=self.H * 0.5)
                self.comp(img, lay, win(t, a, b, 0.3, 0.4), dy=20 * (t - a) / (b - a))
        fs = self.font(INTER / "Inter-SemiBold.otf", 56 if self.vert else 44)
        if t < 6.5:
            fsm = self.font(INTER / "Inter-SemiBold.otf", 34 if self.vert else 26)
            lay = self.text_layer("safety", self.wrap(SAFETY, fsm, self.W * 0.6), fsm, tuple(CREAM.astype(int)),
                                  y=self.H * (0.62 if self.vert else 0.85))
            self.comp(img, lay, 0.75 * win(t, 0, 6.0, 0.3, 0.4))
        if 6 <= t < 30:
            ft = self.font(FONTS / "ArchivoBlack-Regular.ttf", 110 if self.vert else 96)
            lines = ["LEAD WITH", "QUESTIONS"] if self.vert else ["LEAD WITH QUESTIONS"]
            lay = self.text_layer("title", lines, ft, tuple(CREAM.astype(int)), y=self.H * 0.42)
            lay2 = self.text_layer("title2", ["MORNING RUN"], fs, tuple(CREAM.astype(int)),
                                   y=self.H * 0.42 + (160 if self.vert else 100))
            a = win(t, 6, 30, 0.3, 0.4)
            self.comp(img, lay, a, dy=20 * (t - 6) / 24)
            self.comp(img, lay2, a * 0.85, dy=20 * (t - 6) / 24)
        for i, (a, d) in enumerate(p["numbers"]):
            b = p["numbers"][i + 1][0] if i + 1 < len(p["numbers"]) else a + 4
            if a <= t < b + 0.1:
                fn = self.font(INTER / "Inter-SemiBold.otf", 84 if self.vert else 72)
                col = tuple(CREAM.astype(int)) if u < 0.8 else INK
                lay = self.text_layer(("n", d, col), [d], fn, col, y=self.H * (0.66 if self.vert else 0.8))
                self.comp(img, lay, win(t, a, b, 0.3, 0.4))
        af = p["askfirst"]
        if af <= t < af + 4.2:
            fa = self.font(FONTS / "ArchivoBlack-Regular.ttf", 140 if self.vert else 120)
            lay = self.text_layer("askfirst", ["ASK FIRST."], fa, INK)
            self.comp(img, lay, win(t, af, af + 4, 0.3, 0.4))
        if t >= af + 4:
            fe = self.font(FONTS / "ArchivoBlack-Regular.ttf", 92 if self.vert else 84)
            lines = ["STOP", "THINKING", "POOR"] if self.vert else ["STOP THINKING POOR"]
            lay = self.text_layer("end", lines, fe, INK, track=0.12, y=self.H * 0.46)
            fl = self.font(INTER / "Inter-SemiBold.otf", 40 if self.vert else 32)
            lay2 = self.text_layer("end2", ["LEAD WITH QUESTIONS  ·  MORNING RUN"], fl, tuple(STEEL.astype(int)),
                                   track=0.06, y=self.H * (0.62 if self.vert else 0.58))
            a = win(t, af + 4, p["total"] - 2.0, 0.3, 0.01)
            self.comp(img, lay, a)
            self.comp(img, lay2, a)
        img *= 1 - ramp(t, p["total"] - 2.0, p["total"] - 0.05)
        img += (self.grain[0] * (CONFIG["grain_morning"] * 255))[..., None]
        return np.clip(img, 0, 255).astype(np.uint8)

    def frame(self, t):
        return self.night_frame(t) if self.night else self.morning_frame(t)


# ================================================================ render

def _chunk(args):
    plan, aspect, a, b, path = args
    if os.path.exists(path):                       # resumable: finished chunks are kept
        return path
    final, path = path, path + ".part.mp4"
    r = R(plan, aspect)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{r.W}x{r.H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-threads", "2", "-rc-lookahead", "20", "-maxrate", "16M", "-bufsize", "32M",
           "-pix_fmt", "yuv420p", "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
           "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(a, b):
        pr.stdin.write(r.frame(i / FPS).tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise RuntimeError(f"encoder failed for {final}")
    os.replace(path, final)
    return final


def render(cut, aspect, out, workers=4, t0=0.0, t1=None):
    plan = make_plan(cut)
    total = plan["total"] if t1 is None else t1
    n0, n1 = int(t0 * FPS), int(total * FPS)
    tmp = WORK / cut / f"chunks-{aspect}"
    tmp.mkdir(parents=True, exist_ok=True)
    nchunks = workers * 6
    edges = np.linspace(n0, n1, nchunks + 1).astype(int)
    jobs = [(plan, aspect, edges[i], edges[i + 1], str(tmp / f"c{i:03d}.mp4")) for i in range(nchunks)]
    with ProcessPoolExecutor(workers) as ex:
        paths = list(ex.map(_chunk, jobs))
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in paths))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", out],
                   check=True)
    return out


if __name__ == "__main__":
    cut, aspect = sys.argv[1], sys.argv[2]
    if "--frames" in sys.argv:
        plan = make_plan(cut)
        r = R(plan, aspect)
        ts = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1:]]
        for t in ts:
            Image.fromarray(r.frame(t)).save(WORK / f"frame-{cut}-{aspect}-{t:07.1f}.png")
            print("frame", t)
    elif "--render" in sys.argv:
        out = sys.argv[sys.argv.index("--render") + 1]
        rng = [float(x) for x in sys.argv[sys.argv.index("--render") + 2:]]
        render(cut, aspect, out, t0=rng[0] if rng else 0.0, t1=rng[1] if len(rng) > 1 else None)
