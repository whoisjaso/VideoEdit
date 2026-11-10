"""The film. Scenes are keyed to narration word times; picture, captions and sound cues
all come from the same clock (timing.py).

  python3 src/film.py still  --aspect h --t 12.5 --out stills/x.png
  python3 src/film.py render --aspect h --out /path/seg.mp4 [--start F --end F]
  python3 src/film.py cues          -> cues.json (for mix.py) + captions/*.srt
"""
import sys, os, math, json, argparse, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, skia
from gfx import *
import plates as P
from timing import TL, FPS, ROOT, caption_chunks, write_srt

class Film:
    def __init__(self, aspect="h"):
        self.vert = aspect == "v"
        self.W, self.H = (1080, 1920) if self.vert else (1920, 1080)
        self.tl = TL(); self.scenes = []; self.mute = set(); self.cues = {}
        self.grain = Grain(self.W, self.H)
        self.ps = skia.Surface(self.W // 2, self.H // 2); self.main = skia.Surface(self.W, self.H)
        self.caps = caption_chunks(self.tl)
        self._vp = {}
        self.build()

    def S(self, h, v): return v if self.vert else h
    def add(self, name, t0, t1, plate=None, over=None, fin=0.24, fout=0.0):
        self.scenes.append(dict(name=name, t0=t0, t1=t1, plate=plate, over=over, fin=fin, fout=fout))

    # ---------------------------------------------------------------- type helpers
    def phrase(self, c, t, line, x, y, size, a=0, b=None, weight=500, color=WHITE, align="center", max_w=None,
               t_out=None, txt=None, alpha=1.0, dim_at=None, dim_to=0.5, shadow=False, top=False):
        tl = self.tl; ws = tl.by[line]["words"][a:b]
        words = txt if txt is not None else [w["w"] for w in ws]
        st = word_states(t, [w["s"] for w in ws], color, t_out=t_out)
        k = alpha * (lerp(1, dim_to, io_sine(ramp(t, dim_at, dim_at + 0.4))) if dim_at is not None else 1.0)
        st = [(s[0] * k, s[1], s[2]) for s in st]
        mw = max_w or self.W * 0.84
        if shadow:
            draw_words(c, words, [(s[0] * 0.7, (0, 0, 0), s[2]) for s in st], x, y + 2, size, weight, mw, align=align, top=top)
        return draw_words(c, words, st, x, y, size, weight, mw, align=align, top=top)

    def typed(self, c, t, text, t0, x, y, size, weight=600, color=WHITE, align="left", dur=0.5, alpha=1.0):
        n = int(math.ceil(len(text) * ramp(t, t0, t0 + dur)))
        if n <= 0: return
        if align == "center": x = x - text_w(text, font(size, weight), -0.012) / 2
        draw_text(c, text[:n], x, y, size, weight, color, alpha, align="left")

    def drift(self, c, t, t0, t1, amt=0.035):
        s = 1 + amt * ramp(t, t0, t1); c.translate(self.W / 2, self.H / 2); c.scale(s, s); c.translate(-self.W / 2, -self.H / 2)

    def hook(self, c, t, ta, tb, dim_t, out_t):
        W, H, S = self.W, self.H, self.S; size = S(124, 84)
        dim = lerp(1, 0.42, io_sine(ramp(t, dim_t, dim_t + 0.6))) * vanish(t, out_t, 0.5)
        c.save(); self.drift(c, t, ta, out_t)
        for txt, t0, y in (("Your brain is racist.", ta, H / 2 - size * 0.2), ("So is mine.", tb, H / 2 + size * 1.08)):
            p = appear(t, t0, 0.9)
            draw_text(c, txt, W / 2, y + (1 - p) * size * 0.12, size * (1.04 - 0.04 * p), 600, WHITE, p * dim, blur=(1 - p) * size * 0.1)
        c.restore()

    # ---------------------------------------------------------------- the schedule
    def build(self):
        tl, W, H, S = self.tl, self.W, self.H, self.S
        T, E, Wn = tl.T, tl.E, tl.Wn; cx, cy = W / 2, H / 2
        X = 0.24                                    # crossfade between plates
        mute = self.mute

        # 1 ---- hook: type only, grain, silence
        mute |= {"hook1", "hook2"}
        self.add("hook", 0, T("job1") - X + X, over=lambda c, t: self.hook(c, t, 0.6, 2.4, T("hook3"), T("job1") - 0.1), fin=0)

        # 2 ---- one job: the eye
        t0, t1 = T("job1") - X, T("pat1")
        def eye_plate(c, t):
            P.eye(c, W, H, t, pupil=lerp(0.41, 0.25, io_cubic(ramp(t, T("job2"), T("job2") + 1.3))), push=ramp(t, t0, t1))
        def eye_over(c, t):
            lx = W * S(0.06, 0.08); ly = H * S(0.38, 0.11); sz = S(54, 50); out = T("job6") - 0.1
            for i, (ln, word, txt) in enumerate((("job3", "fair", "fair"), ("job4", "moral", "moral"), ("job5", "a", "a good person"))):
                s0 = Wn(ln, word); a = appear(t, s0, 0.45) * vanish(t, out, 0.3)
                a2 = a * lerp(1, 0.45, ramp(t, s0 + 0.5, s0 + 0.9)); y = ly + i * sz * 1.5
                tw = draw_text(c, txt, lx, y, sz, 500, WHITE, a2, align="left")
                k = out_quint(ramp(t, s0 + 0.35, s0 + 0.75))
                if k > 0 and a > 0: c.drawLine(lx - 6, y - sz * 0.3, lx - 6 + (text_w(txt, font(sz, 500), -0.012) + 12) * k, y - sz * 0.3, paint(WHITE, 0.8 * a, stroke=2.5))
            self.phrase(c, t, "job6", S(lx, cx), S(H * 0.47, H * 0.15), S(88, 80), a=2, b=5, weight=600, align=S("left", "center"),
                        txt=["keep", "you", "alive."], t_out=t1 - 0.1, max_w=W * S(0.24, 0.9), shadow=True)
        self.add("eye", t0, t1 + X, eye_plate, eye_over)

        # 3 ---- pattern-match: the stack of screens
        t0, t1 = T("pat1") - X, T("cul1")
        def scr_plate(c, t):
            P.screens(c, W, H, t, grow=io_sine(ramp(t, t0, T("pat5"))), dolly=io_sine(ramp(t, t0, t1 + 1)),
                      lum=lerp(1, 0.45, window(t, T("pat4") - 0.2, E("pat4") + 0.7, 0.4, 0.4)))
        def scr_over(c, t):
            out = E("pat4") + 0.7; sz = S(88, 72)
            self.phrase(c, t, "pat4", cx, cy - sz * 0.6, sz, a=0, b=4, t_out=out)
            self.phrase(c, t, "pat4", cx, cy + sz * 0.7, sz, a=4, b=6, weight=600, t_out=out)
        mute |= {"pat4"}
        self.add("screens", t0, t1 + X, scr_plate, scr_over)

        # 4 ---- cultivation: the child and the TV
        t0, t1 = T("cul1") - X, T("chA1") - 0.4
        def cul_over(c, t):
            s0 = Wn("cul4", "cultivation"); a = appear(t, s0, 0.6) * vanish(t, T("cul6") - 0.1, 0.4)
            x = S(W * 0.045, cx); y = H * S(0.40, 0.145); al = S("left", "center")
            draw_text(c, "cultivation", x, y, S(88, 104), 600, WHITE, a, align=al, blur=(1 - appear(t, s0, 0.6)) * 8)
            draw_text(c, "Gerbner & Gross, 1976", x, y + S(52, 58), 26, 500, WHITE, 0.5 * appear(t, s0 + 0.5, 0.5) * vanish(t, T("cul6") - 0.1, 0.4), align=al, mono=True, track=0)
        self.add("couch", t0, t1, lambda c, t: P.room(c, W, H, t, viewer=0.13), cul_over)

        # 5-7 ---- three characters: hard cuts, the label types in
        cards = (("tank", "the Black guy", ("chA1", "chA2", "chA3")), ("hat", "the Mexican", ("chB1", "chB2", "chB3")),
                 ("suit", "the white guy", ("chC1", "chC2", "chC3", "chC4")))
        bounds = [T("chA1") - 0.4, T("chB1") - 0.4, T("chC1") - 0.4, T("iat1") - 0.35]
        self.cues["cuts"] = bounds[:3]
        for i, (kind, label, ids) in enumerate(cards):
            a0, a1 = bounds[i], bounds[i + 1]; mute |= set(ids)
            def over(c, t, a0=a0, label=label, ids=ids):
                lx = S(W * 0.56, cx); ly = H * S(0.42, 0.13); al = S("left", "center")
                self.typed(c, t, label, a0 + 0.04, lx, ly, S(104, 84), 600, align=al, dur=0.32)
                for j, lid in enumerate(ids):
                    txt = tl.by[lid]["text"].rstrip(".").lower()
                    a = appear(t, T(lid), 0.4) * (lerp(1, 0.5, ramp(t, E(lid) + 0.1, E(lid) + 0.5)) if j < len(ids) - 1 else 1)
                    draw_text(c, txt, lx, ly + S(96, 78) + j * S(72, 60), S(54, 46), 500, WHITE, a * 0.9, align=al)
            self.add("card_" + kind, a0, a1, lambda c, t, kind=kind, a0=a0, a1=a1: P.figure_wall(c, W, H, t, kind, push=ramp(t, a0, a1)), over, fin=0)

        # 8 ---- the IAT: clean, clinical
        t0, t1 = bounds[3], T("st1") - 0.1
        mute |= {"iat2", "iat3", "iat7"}
        def iat_over(c, t):
            tb = T("iat4"); sz = S(88, 76)
            if t < tb + 0.2:
                out = tb - 0.1
                self.phrase(c, t, "iat2", cx, cy - sz * 0.5, sz, a=4, b=6, t_out=out, dim_at=T("iat3"), dim_to=0.45)
                self.phrase(c, t, "iat3", cx, cy + sz * 0.85, sz, weight=600, t_out=out)
            draw_text(c, "Say that's not you.", cx, cy + 10, S(64, 58), 500, WHITE, 0.8 * appear(t, T("iat1"), 0.5) * vanish(t, T("iat2") - 0.1, 0.4))
            if t < tb - 0.1: return
            g = appear(t, tb, 0.7) * vanish(t, t1, 0.4); dimk = lerp(1, 0.28, io_sine(ramp(t, T("iat6"), T("iat6") + 0.6)))
            x0, x1 = W * S(0.14, 0.07), W * S(0.86, 0.93); bx0 = x0 + S(300, 230)
            draw_text(c, "implicit association test", x0, H * S(0.2, 0.25), S(52, 46), 600, WHITE, 0.9 * g * dimk, align="left")
            draw_text(c, "Greenwald, McGhee & Schwartz, 1998", x0, H * S(0.2, 0.25) + 44, 24, 500, WHITE, 0.5 * g * dimk, align="left", mono=True, track=0)
            thl = Wn("iat5", "faster"); hl = out_quint(ramp(t, thl, thl + 0.7))
            ends = []
            for i, (lab, rt, frac, y) in enumerate((("pairs that match the script", 0.40, 0.34, H * S(0.42, 0.40)), ("pairs that don't", 0.78, 0.66, H * S(0.64, 0.55)))):
                draw_text(c, lab, x0, y - 56, 34, 500, WHITE, 0.7 * g * dimk, align="left")
                per = 1.55; lt = t - tb - 0.5 - i * 0.22; n = math.floor(lt / per); phs = lt - n * per if lt >= 0 else -1
                jit = 0.035 * noise1(n * 7.3 + i * 3.1, 5); fr = frac + jit; ends.append(frac)
                c.drawLine(bx0, y, x1, y, paint(WHITE, 0.16 * g * dimk, stroke=5))
                if phs >= 0:
                    a = clamp(phs / 0.1) * vanish(phs, per - 0.05, 0.25) * g * dimk
                    k = out_quint(clamp(phs / 0.28))
                    c.drawOval(skia.Rect.MakeXYWH(x0 + (1 - k) * -30, y - 40, 60, 80), paint((150, 150, 150), a))           # a face: neutral grey oval
                    rrect(c, x0 + 84 + (1 - k) * 40, y - 18, 110 + 30 * noise1(n * 3.7, 9 + i), 36, 18, paint((205, 205, 205), a))   # a word: blank chip
                    fill = clamp(phs / rt) * fr
                    c.drawLine(bx0, y, bx0 + (x1 - bx0) * fill, y, paint(WHITE, 0.92 * a, stroke=9))
                    if phs > rt: c.drawCircle(bx0 + (x1 - bx0) * fr, y, 11, paint(WHITE, a))
                draw_text(c, "faster" if i == 0 else "slower", bx0 + (x1 - bx0) * frac, y + 58, 34, 600, WHITE if i == 0 else AMBER, hl * g * dimk * 0.9)
            ya, yb = H * S(0.42, 0.40), H * S(0.64, 0.55); xa, xb = bx0 + (x1 - bx0) * ends[0], bx0 + (x1 - bx0) * ends[1]
            if hl > 0:                                      # the difference, in amber
                c.drawLine(xa, ya + 10, xa, yb - 10, paint(WHITE, 0.3 * hl * g * dimk, stroke=1.5))
                c.drawLine(xa, yb, xa + (xb - xa) * hl, yb, paint(AMBER, 0.35 * hl * g * dimk, stroke=24, blur=10))
                c.drawLine(xa, yb, xa + (xb - xa) * hl, yb, paint(AMBER, hl * g * dimk, stroke=10))
            self.phrase(c, t, "iat7", cx, H * S(0.84, 0.70), S(68, 60), a=1, weight=600, t_out=t1, max_w=W * 0.86)
        self.add("iat", t0, t1, None, iat_over, fin=0, fout=0)

        # 9-13 ---- the street, pass one, and the amber card
        s0 = T("st2") - X; t1 = T("sx1") - 0.1; VW = 2.0
        self.walk0 = s0
        def fig1(t): return min(24.0, 20.0 - 1.55 * (t - T("st4")))
        camx = lambda t: -5.4 * io_cubic(ramp(t, T("st9") + 0.15, T("st10") + 2.4))
        def st1_plate(c, t):
            pr = tuple(window(t, Wn("st3", w), T("st4") + 0.4, 0.5, 0.6) for w in ("phone", "watch", "keys"))
            card = window(t, T("st11") - 0.4, E("st11") + 0.85, 0.5, 0.4)
            P.street(c, W, H, t, walk=(t - s0) * VW, cam_x=camx(t), fig_z=fig1(t) if t > T("st4") - 1.5 else None, fig_kind="tank",
                     props=pr, lum=1 - 0.88 * card)
        def st1_over(c, t):
            a = window(t, T("st11") - 0.3, E("st11") + 0.85, 0.5, 0.4)
            if a <= 0: return
            draw_text(c, "the script", cx, cy - S(170, 250), 34, 600, WHITE, 0.65 * a, track=0.12)
            c.saveLayerAlpha(None, int(a * 255))
            self.phrase(c, t, "st11", cx, cy + 10, S(76, 66), weight=600, color=AMBER, max_w=W * S(0.62, 0.84))
            c.restore()
        mute |= {"st11"}
        self.add("street1", s0, t1, st1_plate, st1_over)
        self.cues["street"] = [(s0, t1 + 0.2)]; self.cues["walk"] = dict(t0=s0, v=VW, cam=[T("st9") + 0.15, T("st10") + 2.4])
        self.cues["breath"] = T("st4") + 0.9

        # pass two: same street, a suit; you do not cross
        b0, b1 = T("sx1") - X, T("ch6") - 0.1
        tp = E("sx6") + 0.5
        def fig2(t): return 1.5 + (tp - t) * 2.0
        def st2_plate(c, t):
            z = fig2(t)
            P.street(c, W, H, t, walk=(t - s0) * VW, fig_z=z if (z < 30 and t > T("sx3") - 1.0) else None, fig_kind="suit",
                     fig_x=lerp(0.9, 0.25, clamp((z - 1.0) / 6.0)))
        def st2_over(c, t):
            out = T("ch5") + 0.3; sz = S(72, 64)
            xl, xr = W * 0.07, W * 0.93; yl, yr = H * S(0.30, 0.17), H * S(0.30, 0.27)
            draw_text(c, "dangerous?", xl, yl, sz, 600, WHITE, appear(t, Wn("ch1", "dangerous"), 0.5) * vanish(t, out), align="left")
            self.phrase(c, t, "ch1", xl, yl + sz * 0.85, 40, a=5, b=9, align="left", t_out=out, alpha=0.75, txt=["you", "have", "no", "idea."])
            draw_text(c, "safe?", xr, yr, sz, 600, WHITE, appear(t, Wn("ch2", "safe"), 0.5) * vanish(t, out), align="right")
            self.phrase(c, t, "ch2", xr, yr + sz * 0.85, 40, a=5, b=9, align="right", t_out=out, alpha=0.75, txt=["you", "have", "no", "idea."])
        self.add("street2", b0, b1, st2_plate, st2_over)
        self.cues["street"].append((b0, b1 + 0.2)); self.cues["pass2"] = tp - 0.5

        # ---- not hate. prediction.
        c0, c1 = T("ch6") - X, T("two1") - 0.1
        mute |= {"ch7", "ch8"}
        def pred_over(c, t):
            c.save(); self.drift(c, t, T("ch7"), c1)
            a = appear(t, T("ch7"), 0.5) * lerp(1, 0.4, io_sine(ramp(t, T("ch8") - 0.1, T("ch8") + 0.4))) * vanish(t, c1)
            draw_text(c, "Not hate.", cx, cy - S(70, 60), S(92, 80), 500, WHITE, a)
            p = appear(t, T("ch8"), 0.7)
            draw_text(c, "Prediction.", cx, cy + S(110, 90), S(170, 128), 600, WHITE, p * vanish(t, c1), blur=(1 - p) * 14)
            c.restore()
        self.add("prediction", c0, c1, None, pred_over, fout=0)

        # ---- two heads, then the card: a traffic stop
        d0, d1 = T("two1") - 0.1, T("ts1") - X
        def two_over(c, t):
            r = S(118, 108); out = E("two3") + 0.3
            pts = ((cx - W * 0.15, cy), (cx + W * 0.15, cy)) if not self.vert else ((cx, cy - H * 0.11), (cx, cy + H * 0.11))
            for i, ((x, y), s0_) in enumerate(zip(pts, (Wn("two2", "one"), Wn("two3", "both")))):
                a = appear(t, s0_, 0.6) * vanish(t, out, 0.3)
                if a <= 0: continue
                c.drawCircle(x, y, r * (0.9 + 0.1 * a), paint(WHITE, 0.85 * a, stroke=3))
                for j, wd in enumerate((0.9, 0.6, 0.75)):
                    k = out_quint(ramp(t, s0_ + 0.25 + j * 0.22, s0_ + 0.7 + j * 0.22))
                    c.drawLine(x - r * 0.5, y - r * 0.3 + j * r * 0.3, x - r * 0.5 + r * wd * k, y - r * 0.3 + j * r * 0.3, paint(WHITE, 0.7 * a, stroke=5))
            a = window(t, E("two3") + 0.45, T("ts1") - 0.08, 0.45, 0.3)
            c.save(); self.drift(c, t, E("two3"), T("ts1"))
            draw_text(c, "a traffic stop", cx, cy + S(30, 26), S(96, 84), 600, WHITE, a, blur=(1 - appear(t, E("two3") + 0.45, 0.45)) * 8)
            c.restore()
        self.add("two", d0, d1 + X, None, two_over, fin=0)

        # 14-18 ---- the traffic stop: two points of view, no faces
        e0, e1 = T("ts1") - X, T("news1")
        def sm(t, a, b, lo): return lerp(1, lo, io_sine(ramp(t, a, a + 0.6)) * (1 - io_sine(ramp(t, b - 0.5, b))))
        def stop_plate(c, t):
            la = min(sm(t, T("ts8"), T("ts14") - 0.2, 0.3), sm(t, T("ts18"), T("ts20") - 0.1, 0.5))
            lb = min(sm(t, T("ts3"), T("ts8") - 0.2, 0.3), sm(t, T("ts16"), T("ts18") - 0.1, 0.5))
            P.stop_split(c, W, H, t, la, lb, tense_a=io_sine(ramp(t, T("ts7"), T("ts7") + 2)), tense_b=io_sine(ramp(t, T("ts13"), T("ts13") + 2.5)),
                         pull=io_sine(ramp(t, T("ts20"), E("ts22") + 0.4)))
        A1, B1 = ("ts4", "ts5", "ts6"), ("ts9", "ts10", "ts11", "ts12")
        mute |= set(A1) | set(B1) | {"ts17", "ts19"}
        def stop_over(c, t):
            am = io_sine(ramp(t, T("ts20"), T("ts20") + 0.8)); colr = mix(WHITE, AMBER, am)
            wdt = 2 + 5 * am; a = (0.3 + 0.7 * am) * appear(t, e0, 0.5)
            p0, p1 = ((cx, 0), (cx, H)) if not self.vert else ((0, cy), (W, cy))
            if am > 0: c.drawLine(*p0, *p1, paint(AMBER, 0.5 * am, stroke=30, blur=18, blend=skia.BlendMode.kPlus))
            c.drawLine(*p0, *p1, paint(colr, a, stroke=wdt, cap=False))
            sz = S(56, 48); step = sz * 1.3
            ax, ay = W * S(0.045, 0.07), H * S(0.15, 0.085); bx, by = W * S(0.545, 0.07), H * S(0.40, 0.665)
            for ids, x, y, out in ((A1, ax, ay, T("ts8") - 0.25), (B1, bx, by, T("ts14") - 0.25), (("ts17",), ax, ay, E("ts22") + 0.3), (("ts19",), bx, by, E("ts22") + 0.3)):
                yy = y
                for j, lid in enumerate(ids):
                    nxt = T(ids[j + 1]) if j + 1 < len(ids) else None
                    yy += step * self.phrase(c, t, lid, x, yy, sz, top=True, weight=600 if nxt is None else 500, align="left", t_out=out, dim_at=nxt, dim_to=0.5,
                                max_w=W * S(0.43, 0.88), shadow=True)
        self.add("stop", e0, e1 + X, stop_plate, stop_over)
        self.cues["stop"] = (e0, e1); self.cues["belt"] = T("ts8") + 0.9; self.cues["tone"] = (T("ts20"), E("ts22") + 0.45)

        # 19 ---- two scripts, one set of screens
        f0, f1 = T("news1") - X, T("od1") - 0.1
        self.add("news", f0, f1, lambda c, t: P.screens(c, W, H, t, grow=1.0, dolly=0.35 + 0.25 * ramp(t, f0, f1)), None, fout=0.5)

        # ---- the other direction
        g0, g1 = T("od1") - 0.1, T("od5")
        def od_over(c, t):
            q = lerp(1, 0.6, io_sine(ramp(t, T("od2"), T("od2") + 0.5))) * vanish(t, g1, 0.4)
            r = S(104, 96); y = cy - S(60, 80)
            c.drawCircle(cx, y, r, paint(WHITE, 0.85 * q * appear(t, T("od1"), 0.6), stroke=3))
            k = io_cubic(ramp(t, Wn("od1", "other") - 0.1, T("od2") + 0.3))
            if k > 0:
                p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - r * 1.5, y - r * 1.5, cx + r * 1.5, y + r * 1.5), -40, 290 * k)
                c.drawPath(p, paint(WHITE, 0.55 * q, stroke=3))
                ang = math.radians(-40 + 290 * k); ex, ey = cx + math.cos(ang) * r * 1.5, y + math.sin(ang) * r * 1.5
                c.save(); c.translate(ex, ey); c.rotate(math.degrees(ang) + 90)
                c.drawPath(path_from([(-9, -13), (14, 0), (-9, 13)]), paint(WHITE, 0.75 * q)); c.restore()
            self.phrase(c, t, "od4", cx, y + r * 1.5 + S(100, 110), S(80, 70), a=0, b=3, weight=600, txt=["it's", "watching", "you."], t_out=g1, alpha=q)
        self.add("otherdir", g0, g1, None, od_over, fin=0)

        # 20-22 ---- the boy and the screen
        h0, h1 = T("od5") - X, T("od20")
        labs = ("od7", "od8", "od9", "od10"); mute |= set(labs) | {"od17", "od18", "od19"}
        def boy_plate(c, t):
            P.room(c, W, H, t, viewer=lerp(0.15, 0.24, io_sine(ramp(t, T("od11"), E("od15")))), tv="sil", tv_scale=1.12,
                   outline=ramp(t, T("od18") - 0.1, E("od18") + 0.5), seed=2)
        def boy_over(c, t):
            lx = S(W * 0.755, cx); ly = H * S(0.27, 0.115); al = S("left", "center"); out = T("od11") - 0.15
            for j, lid in enumerate(labs):
                a = appear(t, T(lid), 0.4) * vanish(t, out) * (lerp(1, 0.5, ramp(t, E(lid) + 0.1, E(lid) + 0.5)) if j < 3 else 1)
                draw_text(c, tl.by[lid]["text"].rstrip(".").lower(), lx, ly + j * S(68, 56), S(50, 44), 600 if j == 3 else 500, WHITE, a * 0.92, align=al)
            self.phrase(c, t, "od17", lx, ly + S(60, 40), S(50, 48), align=al, t_out=T("od18") - 0.2, max_w=W * S(0.22, 0.8), txt=["see?", "told", "you.", "that's", "us."])
            o2 = h1 - 0.1
            self.phrase(c, t, "od18", S(W * 0.035, cx), H * S(0.40, 0.115), S(56, 56), weight=600, align=al, t_out=o2, max_w=W * S(0.28, 0.9))
            self.phrase(c, t, "od19", S(W * 0.755, cx), H * S(0.40, 0.165), S(56, 56), weight=600, align=al, t_out=o2, max_w=W * S(0.23, 0.9))
        self.add("boy", h0, h1 + X, boy_plate, boy_over)

        i0, i1 = T("od20") - X + X, T("sw1") - 0.1
        def three_plate(c, t):
            P.three_rooms(c, W, H, t, lit=(1, io_sine(ramp(t, Wn("od20", "mexican") - 0.15, Wn("od20", "mexican") + 0.7)),
                                           io_sine(ramp(t, Wn("od21", "white") - 0.15, Wn("od21", "white") + 0.7))))
        self.add("three", i0, i1, three_plate, None, fout=0.4)

        # 23 ---- the switch: a voice changing shape
        j0, j1 = T("sw1") - 0.1, T("sw5")
        def wave_over(c, t):
            g = appear(t, j0, 0.6) * vanish(t, j1, 0.4)
            m = 0.45 * io_sine(ramp(t, T("sw3"), E("sw3"))) + 0.55 * io_sine(ramp(t, T("sw4"), E("sw4")))
            wake = appear(t, T("sw2") - 0.1, 0.9)
            n = S(110, 70); wd = W * lerp(S(0.72, 0.86), S(0.46, 0.6), m); yc = cy - S(40, 60) - m * H * 0.025
            bw = wd / n * 0.5
            for i in range(n):
                u = i / (n - 1); x = cx - wd / 2 + wd * u
                edge = math.sin(math.pi * u) ** 0.6
                ah = H * 0.15 * (0.2 + 0.8 * abs(noise1(u * 7 + t * 1.7, 1))) * (0.35 + 0.65 * abs(noise1(t * 2.3 + u * 1.3, 2)))
                asw = H * 0.062 * (0.6 + 0.4 * abs(noise1(u * 19 + t * 3.4, 3))) * (0.75 + 0.25 * abs(noise1(t * 3.1, 4)))
                hgt = max(3.0, lerp(ah, asw, m) * wake * edge)
                c.drawLine(x, yc - hgt, x, yc + hgt, paint(WHITE, 0.9 * g, stroke=max(2.5, bw)))
            marks = [(T("sw2"), "home"), (Wn("sw3", "interview"), "the interview"), (Wn("sw3", "sales"), "the sales call"), (Wn("sw3", "meeting"), "the meeting")]
            for k, (s0_, lab) in enumerate(marks):
                e_ = marks[k + 1][0] if k + 1 < len(marks) else j1 + 1
                draw_text(c, lab, cx, yc + H * 0.15 + S(90, 100), S(52, 50), 500, WHITE, 0.75 * g * appear(t, s0_, 0.35) * vanish(t, e_, 0.2), track=0.02)
        self.add("wave", j0, j1, None, wave_over, fin=0)

        # 24 ---- code-switching: the glass room
        k0, k1 = T("sw5") - X, T("wf1") - 0.1
        cs = (("sw5", "code-switching"), ("sw6", "corporate voice"), ("sw7", "being professional")); mute |= {"sw5", "sw6", "sw7"}
        def glass_plate(c, t):
            P.glass_room(c, W, H, t, refl=0.35 + 0.65 * io_sine(ramp(t, T("sw13") - 0.4, E("sw13") + 0.8)), ghost=io_sine(ramp(t, Wn("sw12", "two") - 0.1, Wn("sw12", "two") + 1.4)))
        def glass_over(c, t):
            out = T("sw8") - 0.15; x = W * S(0.095, 0.08); y = H * S(0.31, 0.12); sz = S(62, 50)
            for j, (lid, lab) in enumerate(cs):
                a = appear(t, T(lid), 0.45) * vanish(t, out) * (lerp(1, 0.55, ramp(t, E(lid) + 0.1, E(lid) + 0.5)) if j < 2 else 1)
                draw_text(c, lab, x, y + j * sz * 1.35 + 3, sz, 600, (0, 0, 0), 0.6 * a, align="left", blur=6)
                draw_text(c, lab, x, y + j * sz * 1.35, sz, 600, WHITE, a, align="left")
        self.add("glass", k0, k1, glass_plate, glass_over, fout=0.5)

        # 25 ---- whose fault
        l0, l1 = T("wf1") - 0.1, T("ob1") - 0.2
        mute |= {"wf2", "wf3"}
        def fault_over(c, t):
            c.save(); self.drift(c, t, l0, l1)
            self.phrase(c, t, "wf2", cx, cy + 20, S(88, 76), t_out=T("wf3") - 0.2)
            self.phrase(c, t, "wf3", cx, cy + 20, S(100, 80), weight=600, t_out=l1, dim_at=E("wf3") + 0.5, dim_to=0.3, max_w=W * 0.9)
            c.restore()
        self.add("fault", l0, l1, None, fault_over, fin=0)

        # 26 ---- the observer: amber is the only light; the bed is gone
        m0, m1 = T("ob1") - 0.2, T("hs0") - 0.1
        mute |= {"ob5"}
        def obs_plate(c, t):
            P.eye(c, W, H, t, pupil=lerp(0.2, 0.43, io_sine(ramp(t, T("ob2"), E("ob6")))), push=0.4 + 0.6 * ramp(t, m0, m1), amber=1.0,
                  lum=io_sine(ramp(t, m0 + 0.2, T("ob2") + 1.2)) * (1 - 0.35 * window(t, Wn("ob5", "the") - 0.3, T("ob6") - 0.1, 0.4, 0.4)))
        def obs_over(c, t):
            self.phrase(c, t, "ob5", cx, H * S(0.5, 0.5) + S(40, 30), S(132, 100), a=2, weight=600, color=AMBER, t_out=T("ob6") - 0.12, shadow=True)
        self.add("observer", m0, m1, obs_plate, obs_over, fin=0.0, fout=0.6)
        self.cues["observer"] = (m0, m1)

        # 27 ---- the half-second (a model)
        n0, n1 = T("hs0") - 0.1, T("ns1") - 0.1
        def hs_over(c, t):
            g = vanish(t, n1, 0.4); x0, x1 = W * S(0.16, 0.08), W * S(0.84, 0.92); y = H * S(0.54, 0.5)
            wid = io_sine(ramp(t, T("hs3"), E("hs3")))
            px = lambda v: x0 + (x1 - x0) * v
            p1, p2 = px(0.25 - 0.03 * wid), px(0.75 + 0.05 * wid)
            k = out_quint(ramp(t, n0 + 0.1, n0 + 1.0))
            draw_text(c, "a model, not a measurement", x0, y - S(250, 300), 28, 500, WHITE, 0.55 * g * appear(t, T("hs0"), 0.5), align="left", mono=True, track=0)
            c.drawLine(x0, y, x0 + (x1 - x0) * k, y, paint(WHITE, 0.2 * g, stroke=3))
            for v, lab in ((0.0, "you see it"), (1.0, "1 s")):
                c.drawLine(px(v), y - 12, px(v), y + 12, paint(WHITE, 0.4 * g * k, stroke=2))
                draw_text(c, lab, px(v), y + 62, 26, 500, WHITE, 0.5 * g * k, mono=True, track=0, align="left" if v == 0 else "right")
            ts, tq = Wn("hs1", "script"), Wn("hs1", "quarter")
            kk = io_cubic(ramp(t, T("hs1"), tq + 0.1))
            c.drawLine(x0, y, lerp(x0, p1, kk), y, paint(WHITE, 0.95 * g, stroke=6))
            a = appear(t, ts, 0.4) * g
            c.drawLine(p1, y - 26, p1, y + 26, paint(WHITE, a, stroke=3)); draw_text(c, "the script", p1, y - 60, S(54, 42), 600, WHITE, a)
            draw_text(c, "0.25 s", p1, y + 62, 26, 500, WHITE, 0.7 * appear(t, tq, 0.4) * g, mono=True, track=0)
            tc, th, to = Wn("hs2", "catches"), Wn("hs2", "halfsecond"), Wn("hs2", "observer")
            ka = io_cubic(ramp(t, tc, th + 0.25))
            if ka > 0:
                xe = lerp(p1, p2, ka)
                c.drawLine(p1, y, xe, y, paint(AMBER, (0.3 + 0.35 * wid) * g, stroke=22 + 16 * wid, blur=12 + 8 * wid, blend=skia.BlendMode.kPlus))
                c.drawLine(p1, y, xe, y, paint(AMBER, g, stroke=7))
            a = appear(t, to, 0.4) * g
            draw_text(c, "the observer", (p1 + p2) / 2 + S(40, 80), y - 60, S(54, 42), 600, AMBER, a)
            draw_text(c, "the half-second after", (p1 + p2) / 2 + S(40, 40), y + 62, 26, 500, AMBER, 0.8 * appear(t, th, 0.4) * g, mono=True, track=0)
        self.add("halfsecond", n0, n1, None, hs_over, fin=0)

        # 28 ---- the new script: screens go dark, one warm light grows
        o0 = T("ns1") - X; tc0 = E("ns4") + 1.0; o1 = tc0 - 0.15
        marks = [Wn("ns2", "feet"), Wn("ns2", "voice"), Wn("ns2", "shoulders"), Wn("ns3", "one")]
        def new_plate(c, t):
            P.screens(c, W, H, t, grow=1.0, dolly=0.45 + 0.35 * ramp(t, o0, o1), dark=io_sine(ramp(t, T("ns1"), E("ns4"))) * 0.96,
                      warm=io_sine(ramp(t, T("ns2") - 0.5, E("ns4") + 0.6)))
        def new_over(c, t):
            x = cx - W * S(0.09, 0.2); y = cy + H * S(0.2, 0.17); g = vanish(t, o1, 0.5)
            for j, (s0_, wd) in enumerate(zip(marks, (0.6, 0.85, 0.7, 1.0))):
                k = out_quint(ramp(t, s0_, s0_ + 0.7))
                if k <= 0: continue
                last = j == 3; x1 = x + W * S(0.18, 0.4) * wd * k; yy = y + j * 26
                if last: c.drawLine(x, yy, x1, yy, paint(AMBER, 0.5 * g, stroke=18, blur=10, blend=skia.BlendMode.kPlus))
                c.drawLine(x, yy, x1, yy, paint(AMBER, (1.0 if last else 0.6) * g, stroke=6))
        self.add("newscript", o0, o1, new_plate, new_over, fout=0.7)
        self.cues["newscript"] = (o0, o1)

        # 29 ---- close: the hook restated, then olaceo
        zt = E("cl1") + 0.9
        def close_over(c, t):
            self.hook(c, t, tc0, tc0 + 1.4, T("cl1"), E("cl1") + 0.55)
            if t >= zt and t < tl.end - 0.5:
                p = appear(t, zt, 0.7)
                draw_text(c, "olaceo", cx, cy + 14 + (1 - p) * 6, 46 * (1 + 0.02 * ramp(t, zt, tl.end)), 600, WHITE, p, track=0.02, blur=(1 - p) * 5)
        self.add("close", tc0 - 0.1, tl.end, None, close_over, fin=0)
        self.cues.update(sub=0.6, settle=zt, bed=[(T("job1") - 0.3, T("ob1") - 0.3), (T("hs0"), o1 + 0.3)],
                         hiss=[(T("pat1") - X, T("cul1") + 0.3, 1.0), (f0, f1 + 0.3, 0.6), (o0, o1, 0.55)], end=tl.end)

    def video_plate(self, name):
        """A generated plate in plates/<scene>_<h|v>.* replaces the procedural one for that scene."""
        if name not in self._vp:
            import videoplate
            path = videoplate.find(ROOT, name, "v" if self.vert else "h")
            self._vp[name] = videoplate.VideoPlate(path, self.W, self.H) if path else None
        return self._vp[name]

    # ---------------------------------------------------------------- captions
    def captions(self, c, t):
        W, H = self.W, self.H; size = 44 if self.vert else 36
        for ch in self.caps:
            if ch["s"] <= t < ch["out"]:
                if ch["line"] in self.mute: return
                f = font(size, 600, display=False); words = [w["w"] for w in ch["words"]]
                sp = f.measureText(" "); ws = [text_w(w, f, 0) for w in words]; tw = sum(ws) + sp * (len(ws) - 1)
                a = clamp((t - ch["s"]) / 0.05 + 0.4) * clamp((ch["out"] - t) / 0.08)
                yc = H * 0.735 if self.vert else H - 118; px_, py_ = 22, 14
                rrect(c, W / 2 - tw / 2 - px_, yc - size * 0.72 - py_, tw + 2 * px_, size * 1.02 + 2 * py_, 10, paint((0, 0, 0), 0.6 * a))
                x = W / 2 - tw / 2
                for w, wd, wt in zip(words, ws, ch["words"]):
                    k = 0.55 + 0.45 * clamp((t - wt["s"]) / 0.07 + 0.01) if t >= wt["s"] else 0.55      # spoken words brighten on their frame
                    draw_text(c, w, x, yc, size, 600, WHITE, a * k, align="left", track=0, display=False); x += wd + sp
                return

    # ---------------------------------------------------------------- one frame
    def frame(self, n, grain=True):
        t = n / FPS; W, H = self.W, self.H; c = self.main.getCanvas()
        c.clear(col(BLACK))
        for s in self.scenes:
            if not (s["t0"] <= t < s["t1"]): continue
            a = (io_sine(ramp(t, s["t0"], s["t0"] + s["fin"])) if s["fin"] > 0 else 1.0) * ((1 - io_sine(ramp(t, s["t1"] - s["fout"], s["t1"]))) if s["fout"] > 0 else 1.0)
            if a <= 0.002: continue
            if s["plate"]:
                pc = self.ps.getCanvas(); pc.save(); pc.clear(col((0, 0, 0))); pc.scale(0.5, 0.5)
                vp = self.video_plate(s["name"])
                if vp: vp.draw(pc, W, H, t - s["t0"], s["t1"] - s["t0"], amber=1.0 if s["name"] == "observer" else 0.0)
                else: s["plate"](pc, t)
                pc.restore()
                p = skia.Paint(); p.setAlphaf(a)
                c.drawImageRect(self.ps.makeImageSnapshot(), skia.Rect.MakeWH(W // 2, H // 2), skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.CubicResampler.Mitchell()), p)
            if s["over"]:
                if a < 0.998: c.saveLayerAlpha(None, int(a * 255))
                else: c.save()
                s["over"](c, t); c.restore()
        self.captions(c, t)
        if grain: self.grain.draw(c, n)
        return self.main

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--aspect", default="h"); ap.add_argument("--t", type=float, default=0)
    ap.add_argument("--out"); ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=-1); ap.add_argument("--crf", default="18")
    A = ap.parse_args(); F = Film(A.aspect)
    if A.cmd == "still":
        F.frame(int(round(A.t * FPS))).makeImageSnapshot().save(A.out, skia.kPNG); return
    if A.cmd == "cues":
        json.dump(F.cues, open(f"{ROOT}/cues.json", "w"), indent=1)
        json.dump([dict(name=s["name"], t0=round(s["t0"], 3), t1=round(s["t1"], 3)) for s in F.scenes], open(f"{ROOT}/scenes.json", "w"), indent=1)
        os.makedirs(f"{ROOT}/captions", exist_ok=True); write_srt(F.tl, f"{ROOT}/captions/your-brain-is-racist.en.srt")
        print("frames", F.tl.frames(), "duration", round(F.tl.end, 2)); return
    end = F.tl.frames() if A.end < 0 else A.end
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{F.W}x{F.H}", "-r", "60", "-i", "-",
        "-vf", "format=yuv420p,noise=c0s=7:c0f=t+u", "-c:v", "libx264", "-preset", "medium", "-crf", A.crf, "-g", "120", "-bf", "2",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "60", "-video_track_timescale", "15360", A.out], stdin=subprocess.PIPE)
    for n in range(A.start, end):
        ff.stdin.write(F.frame(n, grain=False).makeImageSnapshot().tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__": main()
