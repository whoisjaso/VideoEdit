"""Auto-edit: turn a chosen moment into a full Timeline, following the style's rules.

This is the 8.3 recipe from the skill, as code:
  cut dead air (keep the pauses) -> cold open -> hook title + bass -> raw word-timed captions with
  rationed keyword colors -> punch zooms with whooshes -> curse slow-mo -> money pop-ups -> riser into
  the payoff -> follow CTA with the bell. Every SFX cue records the rule that placed it.
"""
from __future__ import annotations

import re

from . import media, sfx as sfxlib
from .moments import CURSES
from .timeline import Caption, Graphic, Keyframe, Segment, Shake, SfxCue, Timeline, Word

FILLER = {"the", "a", "an", "and", "to", "of", "it", "is", "that", "you", "i", "in", "on", "so", "like",
          "uh", "um", "just", "for", "with", "be", "this", "my", "we", "they", "but", "was", "are", "at"}
MONEY = re.compile(r"^\$|^\d+k$|dollar|bucks|grand|thousand|million|billion|profit|revenue|paid|cash|money|rich|^won$|^win")
NUMS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALE = {"hundred": 100, "thousand": 1_000, "grand": 1_000, "k": 1_000, "million": 1_000_000, "billion": 1_000_000_000}


def money_phrase(ws: list[str]) -> str | None:
    """'seven thousand dollars' -> '$7,000'; '50k' -> '$50,000'. None if the words aren't an amount."""
    total, cur, seen, dollars = 0, 0, False, False
    for raw in ws:
        w = norm(raw).lstrip("$")
        if raw.startswith("$"):
            dollars = True
        m = re.match(r"^(\d+(?:\.\d+)?)(k|m)?$", w)
        if m:
            cur += float(m.group(1)) * {"k": 1_000, "m": 1_000_000}.get(m.group(2) or "", 1)
            seen = True
        elif w in NUMS:
            cur += NUMS[w]
            seen = True
        elif w in SCALE and seen:
            if SCALE[w] == 100:
                cur *= 100
            else:
                total += (cur or 1) * SCALE[w]
                cur = 0
            dollars = dollars or w == "grand"
        elif w in ("dollars", "dollar", "bucks"):
            dollars = True
        elif w == "a" and not seen:
            cur, seen = 1, True
        elif w == "and":
            continue
        else:
            break
    val = total + cur
    if not seen or val < 10:
        return None
    return ("$" if dollars else "") + f"{int(val):,}"
PROBLEM = re.compile(r"broke|problem|fail|lose|lost|wrong|fear|scared|debt|pain|hate|stuck|never|lie|against")
SLURS = {"nigga", "niggas"}   # raw in captions, never slowed down (Jason's rule)
norm = lambda s: re.sub(r"[^a-z0-9$']", "", s.lower())


def _keep_spans(words: list[dict], a: float, b: float, gap_max: float, gap_keep: float) -> list[tuple[float, float]]:
    """His pauses stay; only dead air longer than gap_max shrinks to gap_keep."""
    ws = [w for w in words if w["start"] >= a - 0.05 and w["end"] <= b + 0.05]
    if not ws:
        return [(a, b)]
    out, t = [], max(a, ws[0]["start"] - 0.12)
    for x, y in zip(ws, ws[1:]):
        if y["start"] - x["end"] > gap_max:
            h = gap_keep / 2
            out.append((t, x["end"] + h))
            t = y["start"] - h
    out.append((t, min(b, ws[-1]["end"] + 0.25)))
    return out


def _speech_keep(spans: list[tuple[float, float]], a: float, b: float, gap_max: float, gap_keep: float):
    inside = [(max(a, x), min(b, y)) for x, y in spans if y > a and x < b]
    if not inside:
        return [(a, b)]
    out, t = [], inside[0][0]
    for (x0, x1), (y0, _) in zip(inside, inside[1:]):
        if y0 - x1 > gap_max:
            out.append((t, x1 + gap_keep / 2))
            t = y0 - gap_keep / 2
    out.append((t, inside[-1][1]))
    return out


def _color_for(word: str, keywords: set[str]) -> str:
    n = norm(word)
    if MONEY.search(n) and not re.fullmatch(r"\d+", n):    # "$7,000", "50k", "dollars" (not "6 5" feet)
        return "green"
    if PROBLEM.search(n) and n in keywords:
        return "red"
    if n in keywords:
        return "gold"
    return "white"


def build(src: str, info: dict, words: list[dict], speech: list[tuple[float, float]], moment: dict,
          style: dict, name: str = "jason") -> Timeline:
    cut, zcfg = style["cut"], style["zoom"]
    a, b = float(moment["start"]), float(moment["end"])
    tl = Timeline(title=moment.get("title", ""), hook=moment.get("hook", ""), why=moment.get("why", ""),
                  score=float(moment.get("score", 0)), style=name, grade=style.get("grade", "moody"),
                  grade_intensity=float(style.get("grade_intensity", 1.0)), moment=dict(moment))

    wide = info["width"] / max(info["height"], 1) > 9 / 16 + 0.02
    crop_x = media.face_center_x(src, a, b) if wide else 0.5

    # 1. Cold open: the payoff line first (open loop), then the clip in his order.
    co = moment.get("cold_open")
    if cut.get("cold_open") and co:
        c0, c1 = co[0], min(co[1], co[0] + cut.get("cold_open_max", 3.0))
        tl.segments.append(Segment(src_in=c0, src_out=c1, crop_x=crop_x, tag="cold_open"))

    # 2. Body: keep his pauses, shorten only dead air.
    spans = (_keep_spans(words, a, b, cut["gap_max"], cut["gap_keep"]) if words
             else _speech_keep(speech, a, b, cut["gap_max"], cut["gap_keep"]))
    for x, y in spans:
        if y - x > 0.1:
            tl.segments.append(Segment(src_in=x, src_out=y, crop_x=crop_x, tag="body"))

    in_clip = [w for w in words if a - 0.05 <= w["start"] and w["end"] <= b + 0.05]

    # 3. Curse slow-mo: punchline curses only (followed by a pause), never a slur, capped.
    sm = style.get("slowmo", {})
    if sm.get("enabled") and in_clip:
        punch = [w for i, w in enumerate(in_clip) if norm(w["word"]) in CURSES - SLURS
                 and (i + 1 == len(in_clip) or in_clip[i + 1]["start"] - w["end"] > 0.3)][: sm.get("max", 2)]
        for w in punch:
            for k, s in enumerate(tl.segments):
                if s.tag == "body" and s.src_in < w["start"] and w["end"] + 0.12 < s.src_out:
                    left = s.model_copy(update={"src_out": w["start"]}, deep=True)
                    mid = s.model_copy(update={"src_in": w["start"], "src_out": w["end"] + 0.12, "speed": 0.5,
                                               "pitch_drop": True, "tag": "slowmo"}, deep=True)
                    right = s.model_copy(update={"src_in": w["end"] + 0.12}, deep=True)
                    tl.segments[k:k + 1] = [left, mid, right]
                    break

    keywords = {norm(k) for kw in moment.get("keywords", []) for k in kw.split()} - FILLER
    want = max(3, int(len(in_clip) * style["caption"]["keyword_ratio"] / 2))
    if in_clip and len(keywords) < want and moment.get("engine") != "claude":
        # Offline: top up with idea words. Charged words first, then the long words he leans on.
        from .moments import HOOK_WORDS, STOP
        freq: dict[str, int] = {}
        for w in in_clip:
            freq[norm(w["word"])] = freq.get(norm(w["word"]), 0) + 1
        pool = {n for n in freq if len(n) > 3 and n not in STOP and n not in FILLER and not n.startswith("nigg")}
        ranked = sorted(pool, key=lambda x: (-(x in HOOK_WORDS or bool(PROBLEM.search(x))), -freq[x] * len(x)))
        keywords |= set(ranked[: want - len(keywords)])

    # 4. Captions: every segment's words on the output clock, pages of <= max_words, keyword on its own page.
    budget = max(2, int(len(in_clip) * style["caption"]["keyword_ratio"]) + 1)
    used_kw: set[str] = set()
    out_t = 0.0
    for s in tl.segments:
        seg_words = [w for w in words if s.src_in - 0.02 <= w["start"] < s.src_out]
        page: list[Word] = []
        for w in seg_words:
            t0 = out_t + (max(w["start"], s.src_in) - s.src_in) / s.speed
            t1 = out_t + (min(w["end"], s.src_out) - s.src_in) / s.speed
            color = _color_for(w["word"], keywords)
            n = norm(w["word"])
            if color in ("gold", "red") and (n in used_kw or budget <= 0):
                color = "white"
            if color != "white":
                used_kw.add(n)
                budget -= 1 if color != "green" else 0
            word = Word(t0=round(t0, 3), t1=round(max(t1, t0 + 0.08), 3), w=w["word"], color=color)
            gap = page and t0 - page[-1].t1 > 0.3
            if page and (len(page) >= style["caption"]["max_words"] or gap or color != "white"
                         or page[-1].color != "white"):
                tl.captions.append(Caption(start=page[0].t0, end=page[-1].t1, words=page))
                page = []
            page.append(word)
        if page:
            tl.captions.append(Caption(start=page[0].t0, end=page[-1].t1, words=page))
        out_t += s.out_dur
    for c, nxt in zip(tl.captions, tl.captions[1:]):          # hold each page until the next (no flicker)
        if nxt.start - c.end < 0.6:
            c.end = nxt.start
    total = tl.duration
    S = style["sfx"]

    def cue(t: float, event: str, why: str, gain: float | None = None):
        keys = S.get(event)
        for key in ([keys] if isinstance(keys, str) else keys or []):
            if sfxlib.resolve(key):
                tl.sfx.append(SfxCue(t=round(max(0.0, t), 3), name=key, gain=gain or style.get("sfx_gain", 0.8), why=why))

    # 5. Hook title (font combo): the thesis in big type, bass impact on the first frame.
    body0 = next((sum(x.out_dur for x in tl.segments[:i]) for i, s in enumerate(tl.segments) if s.tag != "cold_open"), 0.0)
    if body0 > 0:
        cue(body0, "cut", "section change: cold open -> clip (camera shutter, playbook §3c)", 0.35)
    title_text = tl.title or (tl.hook.split(".")[0] if tl.hook else "")
    if title_text:
        t_end = body0 + max(style["title"]["hold_min"], 2.2)
        tl.graphics.append(Graphic(kind="title", start=body0, end=t_end, text=title_text.upper(), color="gold", position="top"))
        cue(body0, "hook", "hook / thesis line gets the bass impact (playbook §3c)")
        for c in tl.captions:                                 # never the same words twice
            if c.start < t_end and c.end > body0 and set(norm(w.w) for w in c.words) & set(norm(x) for x in title_text.split()):
                c.hidden = True

    # 6. Punch zooms: on the hook, then on keyword pages every ~N seconds; every zoom gets a whoosh.
    punches = [body0 + 0.05] if total > 3 else []
    for c in tl.captions:
        if any(w.color != "white" for w in c.words) and (not punches or c.start - punches[-1] >= zcfg["every"]):
            punches.append(c.start)
    acc = 0.0
    for s in tl.segments:
        d = s.out_dur
        base = lambda t, d=d: 1.0 + zcfg["drift"] * (t / d if d else 0)
        kfs = [Keyframe(t=0, value=1.0)]
        if s.tag == "slowmo":
            kfs = [Keyframe(t=0, value=1.0), Keyframe(t=d, value=1.12)]
            cue(acc, "slowmo", "curse punchline: 0.5x slow-mo + push-in + whoosh (Jason's rule)")
        else:
            for p in punches:
                lt = p - acc
                if 0 <= lt < d - 0.3:
                    hold_end = min(lt + 1.1, d - 0.05)
                    kfs += [Keyframe(t=lt, value=base(lt)), Keyframe(t=min(lt + 0.16, hold_end), value=base(lt) * zcfg["scale"], ease="overshoot"),
                            Keyframe(t=hold_end, value=base(lt) * zcfg["scale"], ease="hold")]
                    if hold_end + 0.25 < d:
                        kfs.append(Keyframe(t=hold_end + 0.25, value=base(hold_end + 0.25)))
                    cue(p - 0.06, "zoom", "every zoom-in gets a whoosh (playbook §3b)")
            kfs.append(Keyframe(t=d, value=base(d)))
        kfs.sort(key=lambda k: k.t)
        clean = [kfs[0]]
        for k in kfs[1:]:
            if k.t > clean[-1].t + 1e-3:
                clean.append(k)
        s.zoom = clean
        acc += d

    # 7. Money pop-ups (green, spoken words only) + the register sound.
    money_pages = []
    for i, c in enumerate(tl.captions):
        if c.hidden or not any(w.color == "green" for w in c.words):
            continue
        run = [w.w for x in tl.captions[i:i + 3] for w in x.words]
        amount = money_phrase(run[next(k for k, w in enumerate(run) if norm(w) in NUMS or re.match(r"^\$?\d", norm(w)) or k == len(run) - 1):])
        if amount and (not money_pages or c.start - money_pages[-1][0].start > 4):
            money_pages.append((c, amount))
        if len(money_pages) >= 2:
            break
    for c, amount in money_pages:
        tl.graphics.append(Graphic(kind="popup", start=c.start, end=c.start + 1.8, text=amount, color="green", position="center"))
        for x in tl.captions:   # hide the pages that say the amount (never the same words twice)
            if c.start <= x.start < c.start + 1.8 and (set(norm(w.w) for w in x.words) & (set(NUMS) | set(SCALE) | {"dollars", "dollar", "bucks"})):
                x.hidden = True
        cue(c.start, "popup", "pop-up appears: pop + click (playbook §3c, x4)")
        cue(c.start + 0.05, "money", "money / numbers (playbook §3)")

    # 8. Riser into the payoff: the last keyword page in the back half; sting on the word.
    if total > 18:
        late = [c for c in tl.captions if any(w.color in ("gold", "red") for w in c.words) and c.start > total * 0.5 and c.start < total - 3]
        if late:
            t = late[-1].start
            cue(t - 2.0, "riser", "riser ends exactly on the payoff (playbook §3c)", 0.55)
            cue(t, "reveal", "reveal sting on the payoff word (playbook §3c)")

    if style.get("caption_sfx"):
        for c in tl.captions[::2]:
            cue(c.start, "caption", "soft typing under a new caption line (reel 9)", 0.16)

    # 9. Follow CTA over the last beat; the bell rings when Follow flips to Following.
    if style.get("cta", {}).get("enabled") and total > 8:
        start = max(0.0, total - 2.2)
        tl.graphics.append(Graphic(kind="cta", start=start, end=total, text=style["cta"]["text"], position="bottom"))
        cue(start + 1.0, "cta", "bell ding on the Follow -> Following flip (playbook §3c)")

    # Impact shake (wiggle) on the bass hit and reveal stings: the hit is felt, not just heard.
    if style.get("shake", True):
        for c in tl.sfx:
            if c.name in (S.get("hook"), S.get("reveal")):
                acc = 0.0
                for s in tl.segments:
                    if acc <= c.t < acc + s.out_dur - 0.2:
                        s.shake.append(Shake(t=c.t - acc, dur=0.32, amp=12))
                        break
                    acc += s.out_dur

    # Skill rule: never guess a caption. Surface every word the recognizer wasn't sure of, on the output clock.
    for w in in_clip:
        if w.get("conf", 1) < 0.5 and len(norm(w["word"])) > 2 and norm(w["word"]) not in FILLER:
            t = tl.src_to_out(w["start"])
            if t is not None:
                ctx = [x["word"] for x in in_clip if abs(x["start"] - w["start"]) < 1.6]
                tl.check_words.append({"t": round(t, 2), "word": w["word"], "context": " ".join(ctx)})

    tl.sfx.sort(key=lambda c: c.t)
    return tl
