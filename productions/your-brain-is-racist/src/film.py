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
import gfx
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
        gfx.BOUNDS[0], gfx.BOUNDS[1] = self.W * 0.035, self.W * 0.965
        self.build()

    def S(self, h, v): return v if self.vert else h
    MOVE = 0.95        # seconds a camera move between two plates lasts
    def add(self, name, t0, t1, plate=None, over=None, fin=0.24, fout=0.0, fg=None):
        """Plates never cut. Each one arrives by the camera pushing out of the last and leaves by pushing into the next,
        so every plate is extended on both sides to overlap its neighbours for the length of the move."""
        if plate: t0, t1 = max(0.0, t0 - 0.36), t1 + 0.36
        self.scenes.append(dict(name=name, t0=t0, t1=t1, plate=plate, over=over, fin=fin, fout=fout, fg=fg))

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

    def window_text(self, c, text, x, y, size, weight, a, fill, align="center", blur=0.0):
        """Text as a window: the letters are cut out, and a picture plays inside them."""
        if a <= 0.003: return
        c.saveLayerAlpha(None, int(clamp(a) * 255))
        draw_text(c, text, x, y, size, weight, WHITE, 1.0, align=align, blur=blur)
        p = skia.Paint(); p.setBlendMode(skia.BlendMode.kSrcIn); c.saveLayer(None, p)
        fill(c); c.restore(); c.restore()

    def plate_fill(self, c, fn, dy=0.0, zoom=1.0, lift=0.22, gain=0.9):
        """Render a plate and lay it across the frame, brightened, for use inside letters."""
        W, H = self.W, self.H; pc = self.ps.getCanvas(); pc.save(); pc.clear(col((0, 0, 0))); pc.scale(0.5, 0.5); fn(pc); pc.restore()
        im = self.ps.makeImageSnapshot(); src = skia.Rect.MakeWH(W // 2, H // 2); so = skia.SamplingOptions(skia.FilterMode.kLinear)
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((0, 0, 0))))
        c.save(); c.translate(W / 2, H / 2 + dy); c.scale(zoom, zoom); c.translate(-W / 2, -H / 2)
        c.drawImageRect(im, src, skia.Rect.MakeWH(W, H), so)
        pp = skia.Paint(); pp.setBlendMode(skia.BlendMode.kPlus); pp.setAlphaf(gain); c.drawImageRect(im, src, skia.Rect.MakeWH(W, H), so, pp); c.restore()
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((255, 255, 255), lift)))

    def typed(self, c, t, text, t0, x, y, size, weight=600, color=WHITE, align="left", dur=0.5, alpha=1.0, shadow=0.0):
        n = int(math.ceil(len(text) * ramp(t, t0, t0 + dur)))
        if n <= 0: return
        full = text.upper(); sz = size * gfx.CAPS_SCALE; avail = self.W * 0.93 if align == "center" else gfx.BOUNDS[1] - x
        tw = text_w(full, font(sz, weight), gfx.CAPS_TRACK)
        if tw > avail: sz *= avail / tw; tw = avail
        if align == "center": x = x - tw / 2
        if shadow > 0: draw_text(c, full[:n], x, y + sz * 0.03, sz, weight, (0, 0, 0), alpha * shadow, align="left", track=gfx.CAPS_TRACK, caps=False, blur=sz * 0.09)
        draw_text(c, full[:n], x, y, sz, weight, color, alpha, align="left", track=gfx.CAPS_TRACK, caps=False)

    def drift(self, c, t, t0, t1, amt=0.035):
        s = 1 + amt * ramp(t, t0, t1); c.translate(self.W / 2, self.H / 2); c.scale(s, s); c.translate(-self.W / 2, -self.H / 2)

    def jason(self, c, t, t_in, t_out, x, feet, h):
        """Jason on screen: the narrator. He breathes and shifts his weight; he is not a sticker."""
        a = appear(t, t_in, 0.8) * vanish(t, t_out, 0.5)
        if a <= 0.003: return
        im = P.AVATAR; w = h * im.width() / im.height(); p = out_quint(ramp(t, t_in, t_in + 0.9))
        br = 1 + 0.006 * math.sin(t * 1.5); rot = 0.7 * math.sin(t * 0.55) + 0.25 * math.sin(t * 1.3)
        c.drawOval(skia.Rect.MakeLTRB(x - w * 0.42, feet - h * 0.012, x + w * 0.42, feet + h * 0.02), paint((0, 0, 0), 0.6 * a, blur=10))
        c.save(); c.translate(x, feet + (1 - p) * h * 0.05); c.rotate(rot); c.scale(1.0, br)
        pp = skia.Paint(); pp.setAlphaf(a)
        c.drawImageRect(im, skia.Rect.MakeWH(im.width(), im.height()), skia.Rect.MakeXYWH(-w / 2, -h, w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), pp)
        c.restore()

    def tagger(self, c, t, geo, a, tags, verdict):
        """What your brain does to a stranger in a quarter of a second: lock on, itemise, decide.
        geo = (feet x, feet y, height). tags = [(time, text)], verdict = (time, text)."""
        if a <= 0.003: return
        fx, fy, fh = geo; S = self.S
        x0, x1, y0, y1 = fx - 0.3 * fh, fx + 0.3 * fh, fy - 1.06 * fh, fy + 0.03 * fh; L = max(10.0, 0.12 * fh)
        lock = out_quint(ramp(t, tags[0][0] - 0.9, tags[0][0] - 0.3)); k = lerp(1.6, 1.0, lock); mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        x0, x1, y0, y1 = mx + (x0 - mx) * k, mx + (x1 - mx) * k, my + (y0 - my) * k, my + (y1 - my) * k
        fl = 0.8 + 0.2 * math.sin(t * 23)
        for (bx, by, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            c.drawPath(path_from([(bx + sx * L, by), (bx, by), (bx, by + sy * L)], False), paint(WHITE, 0.9 * a * fl * lock, stroke=2.6))
        right = x1 + 18 + self.W * 0.2 < self.W * 0.97; tx = x1 + 18 if right else x0 - 18; al = "left" if right else "right"; sz = S(30, 30)
        for i, (t0, txt) in enumerate(tags):
            p = appear(t, t0, 0.3)
            draw_text(c, txt, tx, y0 + sz + i * sz * 1.5 + (1 - p) * 8, sz, 600, WHITE, a * p * 0.92, align=al, track=0.06)
        vt, vtxt = verdict; p = appear(t, vt, 0.25)
        if p > 0:
            f = font(sz * 1.15 * gfx.CAPS_SCALE, 700); tw = text_w(vtxt.upper(), f, 0.08) + 28; vy = y0 + sz + len(tags) * sz * 1.5 + 10
            bx = tx if right else tx - tw; blink = 0.75 + 0.25 * math.sin((t - vt) * 6.5)
            rrect(c, bx, vy - sz * 0.2, tw, sz * 1.5, 6, paint(WHITE, a * p * blink))
            draw_text(c, vtxt, bx + tw / 2, vy + sz * 0.86, sz * 1.15, 700, (8, 8, 9), a * p, track=0.08)

    def hook(self, c, t, ta, tb, dim_t, out_t):
        W, H, S = self.W, self.H, self.S; size = S(124, 84)
        dim = lerp(1, 0.42, io_sine(ramp(t, dim_t, dim_t + 0.6))) * vanish(t, out_t, 0.5)
        c.save(); self.drift(c, t, ta, out_t)
        ty = H / 2 if not self.vert else H * 0.36; tx = W * 0.43 if not self.vert else W / 2
        for txt, t0, y in (("Your brain is racist.", ta, ty - size * 0.2), ("So is mine.", tb, ty + size * 1.08)):
            p = appear(t, t0, 0.9)
            draw_text(c, txt, tx, y + (1 - p) * size * 0.12, size * (1.04 - 0.04 * p), 600, WHITE, p * dim, blur=(1 - p) * size * 0.1)
        c.restore()
        if not self.vert: self.jason(c, t, tb + 0.15, out_t, W * 0.875, H * 0.95, H * 0.74)       # "So is mine": he means himself
        else: self.jason(c, t, tb + 0.15, out_t, W * 0.5, H * 0.93, H * 0.4)

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
                if k > 0 and a > 0: c.drawLine(lx - 6, y - sz * 0.3, lx - 6 + (text_w(txt.upper(), font(sz * gfx.CAPS_SCALE, 500), gfx.CAPS_TRACK) + 12) * k, y - sz * 0.3, paint(WHITE, 0.8 * a, stroke=2.5))
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
            x, y, al = cx, H * S(0.815, 0.155), "center"         # the word is a window onto the wall of screens
            self.window_text(c, "cultivation", x, y, S(210, 150), 700, a, align=al, blur=(1 - appear(t, s0, 0.6)) * 8,
                             fill=lambda cc: self.plate_fill(cc, lambda pc: P.screens(pc, W, H, t, grow=1.0, dolly=0.2), dy=y - H * 0.5 - S(60, 40), zoom=1.9, lift=0.2, gain=1.0))
            draw_text(c, "Gerbner & Gross, 1976", S(W * 0.955, cx), y - S(175, -62), 26, 500, WHITE, 0.55 * appear(t, s0 + 0.5, 0.5) * vanish(t, T("cul6") - 0.1, 0.4), align=S("right", "center"), mono=True, track=0)
        self.add("couch", t0, t1, lambda c, t: P.room(c, W, H, t, viewer=0.13), cul_over)

        # 5-7 ---- three characters: hard cuts, the label types in
        cards = (("tank", "the Black guy", ("chA1", "chA2", "chA3")), ("hat", "the Mexican", ("chB1", "chB2", "chB3")),
                 ("suit", "the white guy", ("chC1", "chC2", "chC3", "chC4")))
        bounds = [T("chA1") - 0.4, T("chB1") - 0.4, T("chC1") - 0.4, T("iat1") - 0.35]
        self.cues["cuts"] = bounds[:3]
        for i, (kind, label, ids) in enumerate(cards):
            a0, a1 = bounds[i], bounds[i + 1]; mute |= set(ids)
            def over(c, t, a0=a0, label=label, ids=ids):
                # text behind the subject: the title fills the wall and he stands in front of it
                self.typed(c, t, label, a0 + 0.04, cx, H * S(0.5, 0.5), S(330, 230), 700, align="center", dur=0.4, shadow=0.75)
                lx = S(W * 0.7, cx); ly = H * S(0.66, 0.115); al = S("left", "center")
                for j, lid in enumerate(ids):
                    txt = tl.by[lid]["text"].rstrip(".").lower()
                    a = appear(t, T(lid), 0.4) * (lerp(1, 0.5, ramp(t, E(lid) + 0.1, E(lid) + 0.5)) if j < len(ids) - 1 else 1)
                    draw_text(c, txt, lx, ly + j * S(64, 56), S(48, 44), 500, WHITE, a * 0.92, align=al, fit=W * S(0.27, 0.9))
            self.add("card_" + kind, a0, a1, lambda c, t, kind=kind, a0=a0, a1=a1: P.figure_wall(c, W, H, t, kind, push=ramp(t, a0, a1), tin=t - a0 + 0.36), over, fin=0,
                     fg=lambda c, t, kind=kind, a0=a0, a1=a1: P.card_fig(c, W, H, t, kind, t - a0 + 0.36, push=ramp(t, a0, a1), rim=False))

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
        self._camx = camx
        def st1_plate(c, t):
            pr = tuple(window(t, Wn("st3", w), T("st4") + 0.4, 0.5, 0.6) for w in ("phone", "watch", "keys"))
            card = window(t, T("st11") - 0.4, E("st11") + 0.85, 0.5, 0.4)
            P.street(c, W, H, t, walk=(t - s0) * VW, cam_x=camx(t), fig_z=fig1(t) if t > T("st4") - 1.5 else None, fig_kind="tank",
                     props=pr, lum=1 - 0.88 * card, menace=io_sine(ramp(t, T("st5"), T("st9"))), react=io_sine(ramp(t, T("st9") + 0.5, T("st10") + 1.0)))
        def st1_over(c, t):
            z = fig1(t)
            if t > T("st4") - 0.6 and 0.9 < z < 24:
                ha = appear(t, T("st4") + 0.2, 0.5) * vanish(t, T("st11") - 0.6, 0.4) * clamp((z - 0.9) * 2)
                self.tagger(c, t, P.street_geo(W, H, (t - s0) * VW, camx(t), z, 0.25), ha,
                            [(T("st5"), "tank top"), (T("st6"), "pants low"), (T("st7"), "black")], (T("st8") + 0.2, "threat"))
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
            z = fig2(t)
            if t > T("sx3") - 0.9 and 1.3 < z < 24:
                ha = appear(t, T("sx3") - 0.6, 0.5) * clamp((z - 1.3) * 1.5)
                self.tagger(c, t, P.street_geo(W, H, (t - s0) * VW, 0.0, z, lerp(0.9, 0.25, clamp((z - 1.0) / 6.0))), ha,
                            [(T("sx3"), "suit"), (T("sx4"), "clean shaven"), (T("sx5"), "white")], (T("sx6"), "safe"))
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
            wy = cy + S(140, 100)                                   # the word is a window onto the street it came from
            self.window_text(c, "Prediction.", cx, wy, S(250, 150), 700, p * vanish(t, c1), blur=(1 - p) * 14,
                             fill=lambda cc: self.plate_fill(cc, lambda pc: P.street(pc, W, H, t, walk=(t - self.walk0) * 2.0, fig_z=5.2, fig_kind="tank", fig_x=0.0), dy=wy - H * S(0.5, 0.47) - S(70, 44), zoom=1.5, lift=0.42, gain=1.0))
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
            def lights(cc):                                         # the words are a window onto the light bar
                r_, b_ = P.flash(t); cc.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((30, 30, 34))))
                glow(cc, W * 0.25, cy, W * 0.6, P.RED, 0.25 + 0.75 * r_, blend=skia.BlendMode.kPlus); glow(cc, W * 0.75, cy, W * 0.6, P.BLUE, 0.25 + 0.75 * b_, blend=skia.BlendMode.kPlus)
                cc.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((255, 255, 255), 0.2)))
            self.window_text(c, "a traffic stop", cx, cy + S(40, 30), S(170, 120), 700, a, lights, blur=(1 - appear(t, E("two3") + 0.45, 0.45)) * 8)
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
        acts = [("rapper", T("od7")), ("athlete", T("od8")), ("dealer", T("od9")), ("cell", T("od10"))]
        def boy_plate(c, t):
            act, at, prev = None, 0.0, None
            for i, (nm, s0_) in enumerate(acts):
                if t >= s0_ - 0.15: act, at, prev = nm, t - s0_ + 0.15, (acts[i - 1][0] if i else None)
            if t > T("od11") + 0.4: prev, act, at = "cell", "rapper", t - T("od11") - 0.4      # it loops back to the first thing it showed him
            P.room(c, W, H, t, viewer=lerp(0.15, 0.2, io_sine(ramp(t, T("od11"), E("od15")))), tv="sil", tv_scale=1.12, seed=2,
                   act=act, act_t=at, prev=prev, act_k=ramp(at, 0.0, 0.35),
                   grow=ramp(t, T("od14"), T("od15") + 0.6), mimic=ramp(t, T("od15") + 0.2, T("od17")), echo=ramp(t, T("od18") - 0.1, E("od18") + 0.5), strings=io_sine(ramp(t, T("od14"), T("od15") + 0.8)))
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
            for v, lab in ((0.0, "you see it"), (1.0, "1 sec")):
                c.drawLine(px(v), y - 12, px(v), y + 12, paint(WHITE, 0.4 * g * k, stroke=2))
                draw_text(c, lab, px(v), y + 62, 26, 500, WHITE, 0.5 * g * k, mono=True, track=0, align="left" if v == 0 else "right")
            ts, tq = Wn("hs1", "script"), Wn("hs1", "quarter")
            kk = io_cubic(ramp(t, T("hs1"), tq + 0.1))
            c.drawLine(x0, y, lerp(x0, p1, kk), y, paint(WHITE, 0.95 * g, stroke=6))
            a = appear(t, ts, 0.4) * g
            c.drawLine(p1, y - 26, p1, y + 26, paint(WHITE, a, stroke=3)); draw_text(c, "the script", p1, y - 60, S(54, 42), 600, WHITE, a)
            draw_text(c, "0.25 sec", p1, y + 62, 26, 500, WHITE, 0.7 * appear(t, tq, 0.4) * g, mono=True, track=0)
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
        import stick as K
        yg = H * S(0.845, 0.655); fhh = min(W, H) * 0.21
        def xy(t): return lerp(-0.1 * W, 1.1 * W, ramp(t, T("ns1") + 0.2, E("ns4") + 0.5))
        def xo(t): return lerp(1.1 * W, -0.1 * W, ramp(t, T("ns1") + 1.4, E("ns4") + 0.1))
        tm = min((abs(xy(o0 + i * 0.05) - xo(o0 + i * 0.05)), o0 + i * 0.05) for i in range(int((o1 - o0) / 0.05)))[1]      # the moment they pass
        self.cues["pass3"] = tm
        def new_over(c, t):
            """The street, a third time, on the one line. Nobody crosses. They pass, they nod, and his steps leave the new script behind him."""
            g = appear(t, T("ns1"), 0.8) * vanish(t, o1, 0.5)
            if g <= 0.003: return
            nod = window(t, tm - 0.45, tm + 0.75, 0.3, 0.45); x, x2 = xy(t), xo(t)
            for q in range(int(max(0.0, x + 0.1 * W) / (0.37 * fhh)) + 1):                  # footprints: one amber mark for every step taken
                fxm = -0.1 * W + q * 0.37 * fhh
                if fxm < x - 0.12 * fhh:
                    age = clamp((x - fxm) / (0.5 * fhh)); c.drawLine(fxm - 0.05 * fhh, yg + 12, fxm + 0.05 * fhh, yg + 12, paint(AMBER, 0.85 * g * age, stroke=4))
            po = K.walk_ik((1.1 * W - x2) / fhh, -1, energy=0.75, nod=nod)
            K.draw(c, po, x2, yg, fhh, a=g, outfit="tank", t=t, dim=0.95, toon=True, face=K.face_blend("cool", "smile", nod * 1.4), edge=K.EDGE)
            py_ = K.walk_ik((x + 0.1 * W) / fhh, 1, energy=0.9, nod=nod)
            lead = K.walk_ik((x + 0.1 * W) / fhh + 0.06, 1, energy=0.9, nod=nod)             # the observer walks half a step ahead of him
            K.draw(c, lead, x + 0.07 * fhh, yg, fhh, AMBER, 0.9 * g, weight=0.03, glow=True)
            K.draw(c, py_, x, yg, fhh, a=g, t=t + 1.0, toon=True, face=K.face_blend("wary", "smile", nod * 1.4), edge=K.EDGE)
        self.add("newscript", o0, o1, new_plate, new_over, fout=0.7)
        self.cues["newscript"] = (o0, o1)

        # 29 ---- close: the hook restated, then olaceo
        zt = E("cl1") + 0.9
        def close_over(c, t):
            self.hook(c, t, tc0, tc0 + 1.4, T("cl1"), E("cl1") + 0.55)
            if t >= zt - 0.2 and t < tl.end - 0.5:                 # the exit: the OLACEO wordmark. The line arrives as the E's middle bar.
                p = appear(t, zt, 0.9); lock = io_cubic(ramp(t, zt + 0.35, zt + 0.95))
                c.save(); self.drift(c, t, zt, tl.end, 0.02)
                gfx.draw_logo(c, cx, cy, S(66, 58), p, mid=False)
                gfx.draw_logo(c, cx, cy, S(66, 58), lock, mid=True)
                c.restore()
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
                    draw_text(c, w, x, yc, size, 600, WHITE, a * k, align="left", track=0, display=False, caps=False); x += wd + sp
                return

    # ---------------------------------------------------------------- one frame
    # ---------------------------------------------------------------- the continuum
    def focus(self, name):
        """Where the camera pushes through each plate: always something dark or bright enough to swallow the frame."""
        S = self.S
        return {"eye": (0.5, 0.5), "observer": (0.5, 0.5), "screens": (0.5, 0.5), "news": (0.5, 0.5), "newscript": (0.5, 0.5),
                "couch": (S(0.52, 0.5), 0.36), "boy": (S(0.52, 0.5), 0.36), "three": (0.5, S(0.4, 0.405)),
                "card_tank": (S(0.3, 0.5), S(0.55, 0.6)), "card_hat": (S(0.3, 0.5), S(0.55, 0.6)), "card_suit": (S(0.3, 0.5), S(0.55, 0.6)),
                "street1": (0.5, 0.45), "street2": (0.5, 0.45), "stop": (0.5, 0.5), "glass": (S(0.555, 0.5), S(0.55, 0.5))}.get(name, (0.5, 0.5))

    def dust(self, c, t):
        """One slow field of dust drifts through the whole film, so black is never empty and nothing resets."""
        import random
        W, H = self.W, self.H; rng = random.Random(99)
        for i in range(46):
            sp = rng.uniform(0.004, 0.014); x = (rng.random() - t * sp) % 1.0; y = (rng.random() + t * sp * 0.35 + 0.02 * math.sin(t * 0.3 + i)) % 1.0
            r = rng.uniform(1.2, 3.4); a = rng.uniform(0.05, 0.13) * (0.6 + 0.4 * math.sin(t * rng.uniform(0.2, 0.7) + i))
            c.drawCircle(x * W, y * H, r, paint((226, 226, 232), a, blur=r * 0.7))

    def line_pts(self, name, t):
        """The line's shape in each scene, as N points. It is the same line all the way through."""
        W, H, S, tl = self.W, self.H, self.S, self.tl; cx, cy = W / 2, H / 2; N = 160; T, E = tl.T, tl.E
        def seg(x0, y0, x1, y1): return [(x0 + (x1 - x0) * i / (N - 1), y0 + (y1 - y0) * i / (N - 1)) for i in range(N)]
        def circ(x, y, r): return [(x + r * math.cos(-math.pi / 2 + math.tau * i / (N - 1)), y + r * math.sin(-math.pi / 2 + math.tau * i / (N - 1))) for i in range(N)]
        def rect(x, y, w, h):
            per = 2 * (w + h); out = []
            for i in range(N):
                d = per * i / (N - 1)
                if d < w: out.append((x + d, y))
                elif d < w + h: out.append((x + w, y + d - w))
                elif d < 2 * w + h: out.append((x + w - (d - w - h), y + h))
                else: out.append((x, y + h - (d - 2 * w - h)))
            return out
        def under(y, w, x=None): x = cx if x is None else x; return seg(x - w / 2, y, x + w / 2, y)
        if name in ("hook", "close"):
            hxc = W * 0.43 if not self.vert else cx
            w = S(620, 520) * (out_quint(ramp(t, 0.25, 1.4)) if name == "hook" else 1.0); y = (cy if not self.vert else H * 0.36) + S(124, 84) * 1.72
            if name == "close":                                    # down into the wordmark: the line becomes the middle bar of the E
                zt = E("cl1") + 0.9; k = io_cubic(ramp(t, zt - 0.45, zt + 0.75)); _, m, _ = gfx.logo_geo(cx, cy, S(66, 58))
                a_ = under(y, max(w, 2), hxc); b_ = seg(m[0][0], m[0][1], m[1][0], m[1][1])
                return [(lerp(p[0], q[0], k), lerp(p[1], q[1], k)) for p, q in zip(a_, b_)]
            return under(y, max(w, 2), hxc)
        if name in ("eye", "observer"): return circ(cx, cy, 0.43 * min(W, H) * (1.02 + 0.07 * (ramp(t, T("job1"), T("pat1")) if name == "eye" else 0.6)))
        if name in ("screens", "news"): w = W * S(0.3, 0.52); return rect(cx - w / 2, cy - w * 0.3, w, w * 0.6)
        if name in ("couch", "boy"):
            tw = W * S(0.36, 0.66) * (1.12 if name == "boy" else 1.0); th = tw * 0.6; tx = W * S(0.52, 0.5); ty = H * 0.36
            return rect(tx - tw / 2, ty - th / 2, tw, th)
        if name.startswith("card_"): return seg(W * 0.682, H * 0.615, W * 0.682, H * 0.875) if not self.vert else seg(W * 0.3, H * 0.085, W * 0.7, H * 0.085)
        if name == "iat": return seg(W * S(0.14, 0.07), H * S(0.2, 0.25) + 72, W * S(0.86, 0.93), H * S(0.2, 0.25) + 72)
        if name in ("street1", "street2"):                       # the curb you walk along
            cam = self._camx(t) if name == "street1" else 0.0
            k = W * S(0.40, 0.62); yh = H * S(0.45, 0.44); gh = H - yh
            pts = [(cx + (-1.0 - cam) * k / z, yh + gh / z) for z in [0.55 * (60 / 0.55) ** (i / (N - 1)) for i in range(N)]]
            if name == "street1":                                  # while the amber card is up, the line sits under it
                kc = io_cubic(ramp(t, T("st11") - 0.5, T("st11") + 0.2)) * (1 - io_cubic(ramp(t, E("st11") + 0.5, E("st11") + 1.0)))
                if kc > 0: u = under(cy + S(150, 190), S(760, 600)); pts = [(lerp(a[0], b[0], kc), lerp(a[1], b[1], kc)) for a, b in zip(pts, u)]
            return pts
        if name == "prediction": return under(cy + S(140, 100) + S(88, 62), S(760, 600))
        if name in ("two", "stop"):
            g = 1.0 if name == "stop" else 0.6
            pts = seg(cx, cy - H * 0.5 * g, cx, cy + H * 0.5 * g) if not self.vert else seg(cx - W * 0.5 * g, cy, cx + W * 0.5 * g, cy)
            if name == "two":                                      # under the title card, then up into the divider
                kc = io_cubic(ramp(t, E("two3") + 0.15, E("two3") + 0.8))
                if kc > 0: u = under(cy + S(40, 30) + S(58, 46), S(600, 500)); pts = [(lerp(a[0], b[0], kc), lerp(a[1], b[1], kc)) for a, b in zip(pts, u)]
            return pts
        if name == "otherdir": return circ(cx, cy - S(60, 80), S(104, 96))
        if name == "three": return seg(W * 0.08, H * 0.74, W * 0.92, H * 0.74) if not self.vert else seg(W * 0.9, H * 0.1, W * 0.9, H * 0.72)
        if name == "wave":
            yc = cy - S(40, 60); wd = W * S(0.8, 0.9); return seg(cx - wd / 2, yc, cx + wd / 2, yc)
        if name == "glass": return seg(W * 0.06, H * S(0.82, 0.68), W * 0.94, H * S(0.82, 0.68))
        if name == "fault": return under(cy + S(86, 120), S(820, 640))
        if name == "halfsecond": return seg(W * S(0.16, 0.08), H * S(0.54, 0.5), W * S(0.84, 0.92), H * S(0.54, 0.5))
        if name == "newscript": return seg(W * 0.04, H * S(0.845, 0.655), W * 0.96, H * S(0.845, 0.655))      # the line is the ground now
        return under(cy, 300)

    def the_line(self, c, t):
        """One line, first frame to last. White while the script runs you; amber once the observer is watching."""
        pts, colr, a = self.line_state(t); self.draw_line(c, pts, colr, a)

    def draw_line(self, c, pts, colr, a):
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        c.drawPath(p, paint(colr, 0.28 * a, stroke=12, blur=7, blend=skia.BlendMode.kPlus))
        c.drawPath(p, paint(colr, 0.95 * a, stroke=3.2))

    def line_state(self, t):
        """Where the line is and what colour it is at time t."""
        order = [s for s in self.scenes]; M = 1.2
        idx = 0
        for i, s in enumerate(order):
            if t >= (s["t0"] + (0.36 if s["plate"] else 0.0)): idx = i
        cur = order[idx]; pts = self.line_pts(cur["name"], t)
        if idx + 1 < len(order):                                   # leaning into the next shape before the move
            nb = order[idx + 1]["t0"] + (0.36 if order[idx + 1]["plate"] else 0.0)
            k = io_cubic(ramp(t, nb - M / 2, nb + M / 2) * 0.5 * 2) if t > nb - M / 2 else 0.0
            k = 0.5 * io_cubic(ramp(t, nb - M / 2, nb)) if t > nb - M / 2 else 0.0
            if k > 0: q = self.line_pts(order[idx + 1]["name"], t); pts = [(lerp(a[0], b[0], k), lerp(a[1], b[1], k)) for a, b in zip(pts, q)]
        if idx > 0:                                                # finishing the move out of the last shape
            pb = cur["t0"] + (0.36 if cur["plate"] else 0.0)
            k = 0.5 + 0.5 * io_cubic(ramp(t, pb, pb + M / 2))
            if k < 1: q = self.line_pts(order[idx - 1]["name"], t); pts = [(lerp(b[0], a[0], k), lerp(b[1], a[1], k)) for a, b in zip(pts, q)]
        tl = self.tl; amb = io_sine(ramp(t, tl.T("ob1") - 0.2, tl.T("ob2") + 1.0))
        amb = max(amb, io_sine(ramp(t, tl.T("ts20"), tl.T("ts20") + 0.8)) * (1 - io_sine(ramp(t, tl.E("ts22") + 0.3, tl.E("ts22") + 1.2))))
        zt = tl.E("cl1") + 0.9; home = io_cubic(ramp(t, zt - 0.2, zt + 0.8))          # at the exit it settles into the mark: white, and the mark's own weight
        amb *= 1 - home
        colr = mix(WHITE, AMBER, amb); a = appear(t, 0.2, 0.6) * (1 - ramp(t, tl.end - 0.5, tl.end - 0.45)) * (1 - 0.999 * io_cubic(ramp(t, zt + 0.7, zt + 1.0)))
        return pts, colr, a

    # ---------------------------------------------------------------- one frame
    def frame(self, n, grain=True, line=True, caps=True):
        t = n / FPS; W, H = self.W, self.H; c = self.main.getCanvas(); D = self.MOVE
        c.clear(col(BLACK))
        for s in self.scenes:
            if not (s["t0"] <= t < s["t1"]): continue
            if s["plate"]:
                # arrive by pulling out of a point, leave by pushing into one: the cut is a camera move
                first = s["t0"] <= 0.001
                kin = 1.0 if first else io_cubic(ramp(t, s["t0"], s["t0"] + D)); kout = in_cubic(ramp(t, s["t1"] - D, s["t1"])) if s["t1"] < self.tl.end - 0.01 else 0.0
                a = clamp(kin * 1.6) * (1 - clamp(kout * 1.5 - 0.5) if kout > 0 else 1.0)
                if a <= 0.002: continue
                sc = lerp(0.34, 1.0, out_quint(ramp(t, s["t0"], s["t0"] + D)) if not first else 1.0) * lerp(1.0, 3.4, kout)
                fx, fy = self.focus(s["name"]); fx *= W; fy *= H
                pc = self.ps.getCanvas(); pc.save(); pc.clear(col((0, 0, 0))); pc.scale(0.5, 0.5)
                vp = self.video_plate(s["name"])
                if vp: vp.draw(pc, W, H, t - s["t0"], s["t1"] - s["t0"], amber=1.0 if s["name"] == "observer" else 0.0)
                else: s["plate"](pc, t)
                pc.restore()
                p = skia.Paint(); p.setAlphaf(a)
                c.save(); c.translate(fx, fy); c.scale(sc, sc); c.translate(-fx, -fy)
                if sc < 0.999:                                         # while it is still small, hold it in a soft iris so no edge shows
                    mm = skia.Matrix(); mm.setScale(W / 2, H / 2); mm.postTranslate(W / 2, H / 2)      # an ellipse that dies before any edge
                    sh = skia.GradientShader.MakeRadial((0, 0), 1.0, [col((255, 255, 255), a), col((255, 255, 255), a), col((255, 255, 255), 0)], [0, 0.45, 0.96], skia.TileMode.kClamp, 0, mm)
                    c.saveLayer(None, None)
                    c.drawImageRect(self.ps.makeImageSnapshot(), skia.Rect.MakeWH(W // 2, H // 2), skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
                    mp = skia.Paint(Shader=sh); mp.setBlendMode(skia.BlendMode.kDstIn); c.drawRect(skia.Rect.MakeLTRB(-W, -H, 2 * W, 2 * H), mp); c.restore()
                else:
                    c.drawImageRect(self.ps.makeImageSnapshot(), skia.Rect.MakeWH(W // 2, H // 2), skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.CubicResampler.Mitchell()), p)
                c.restore()
                ao = clamp(kin * 2.2 - 1.2) * (1 - clamp(kout * 3.0))    # type steps aside for the move
                fgx = (fx, fy, sc, a)
            else:
                ao = (io_sine(ramp(t, s["t0"], s["t0"] + s["fin"])) if s["fin"] > 0 else 1.0) * ((1 - io_sine(ramp(t, s["t1"] - s["fout"], s["t1"]))) if s["fout"] > 0 else 1.0)
            if s["over"] and ao > 0.002:
                if ao < 0.998: c.saveLayerAlpha(None, int(ao * 255))
                else: c.save()
                s["over"](c, t); c.restore()
            if s.get("fg") and s["plate"]:                             # the subject again, sharp, in front of the type
                fx, fy, sc, a = fgx
                c.save(); c.translate(fx, fy); c.scale(sc, sc); c.translate(-fx, -fy)
                if a < 0.998: c.saveLayerAlpha(None, int(a * 255))
                else: c.save()
                s["fg"](c, t); c.restore(); c.restore()
        self.dust(c, t)
        if line: self.the_line(c, t)
        if caps: self.captions(c, t)
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
    if A.cmd == "tail":
        # The exit, for any moment in the film: the picture lets go, and the line travels home to become the E in OLACEO.
        n0 = int(round(A.t * FPS)); W, H = F.W, F.H; cx, cy = W / 2, H / 2
        base = F.frame(n0, grain=False, line=False, caps=False).makeImageSnapshot()        # a snapshot keeps its own pixels
        pts0, col0, _ = F.line_state(A.t); hh = F.S(66, 58); _, m, _ = gfx.logo_geo(cx, cy, hh); N_ = len(pts0)
        tgt = [(m[0][0] + (m[1][0] - m[0][0]) * i / (N_ - 1), m[0][1]) for i in range(N_)]
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", "60", "-i", "-",
            "-vf", "format=yuv420p,noise=c0s=7:c0f=t+u", "-c:v", "libx264", "-preset", "medium", "-crf", A.crf, "-g", "120", "-bf", "2",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "60", "-video_track_timescale", "15360", A.out], stdin=subprocess.PIPE)
        for k in range(int(3.5 * FPS)):
            tt = k / FPS; c = F.main.getCanvas(); c.clear(col(BLACK))
            pa = skia.Paint(); pa.setAlphaf(1 - io_sine(ramp(tt, 0.0, 0.75))); c.drawImage(base, 0, 0, skia.SamplingOptions(), pa)
            F.dust(c, A.t + tt)
            kk = io_cubic(ramp(tt, 0.15, 1.3)); pts = [(lerp(a_[0], b_[0], kk), lerp(a_[1], b_[1], kk)) for a_, b_ in zip(pts0, tgt)]
            F.draw_line(c, pts, mix(col0, WHITE, io_cubic(ramp(tt, 0.45, 1.3))), 1 - 0.999 * io_cubic(ramp(tt, 1.3, 1.6)))
            pl = appear(tt, 0.8, 0.9); lock = io_cubic(ramp(tt, 1.1, 1.7))
            c.save(); F.drift(c, tt, 0.8, 3.5, 0.02); gfx.draw_logo(c, cx, cy, hh, pl, mid=False); gfx.draw_logo(c, cx, cy, hh, lock, mid=True); c.restore()
            ff.stdin.write(F.main.makeImageSnapshot().tobytes())
        ff.stdin.close(); ff.wait(); return
    end = F.tl.frames() if A.end < 0 else A.end
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{F.W}x{F.H}", "-r", "60", "-i", "-",
        "-vf", "format=yuv420p,noise=c0s=7:c0f=t+u", "-c:v", "libx264", "-preset", "medium", "-crf", A.crf, "-g", "120", "-bf", "2",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "60", "-video_track_timescale", "15360", A.out], stdin=subprocess.PIPE)
    for n in range(A.start, end):
        ff.stdin.write(F.frame(n, grain=False).makeImageSnapshot().tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__": main()
