/* adfilm kit — reusable pieces for code-built ads (pure functions of the frame number f at 60 fps).
 * Motion vocabulary adapted from the MIT-licensed `cinetic` skill by Leon Lin (tokens, hitPulse, seams), rebuilt for our seek(t) engine.
 * Rules baked in: ~3 easing characters, zero overshoot (critically damped), one settle constant for type, everything on a whole-frame grid.
 */
const FPS = 60;
const K = {};

// ── grid ──
K.grid = (bpm = 120) => { const BEAT = Math.round((60 / bpm) * FPS); return { BEAT, BAR: BEAT * 4, b: (bar, beat = 0, sub = 0) => Math.round(((bar - 1) * 4 + beat) * BEAT + (sub * BEAT) / 4) }; };

// ── math ──
K.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
K.lerp = (a, b, t) => a + (b - a) * t;
K.lmix = (a, b, t) => Math.exp(Math.log(a) + (Math.log(b) - Math.log(a)) * t); // scale/zoom always in log space
K.prog = (f, start, dur) => K.clamp((f - start) / dur);

// ── cubic-bezier easing (Newton-Raphson, like CSS) ──
K.bez = (x1, y1, x2, y2) => {
  const ax = 3 * x1 - 3 * x2 + 1, bx = 3 * x2 - 6 * x1, cx = 3 * x1;
  const ay = 3 * y1 - 3 * y2 + 1, by = 3 * y2 - 6 * y1, cy = 3 * y1;
  const sx = (t) => ((ax * t + bx) * t + cx) * t, sy = (t) => ((ay * t + by) * t + cy) * t, dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
  return (x) => {
    if (x <= 0) return 0; if (x >= 1) return 1;
    let t = x; for (let i = 0; i < 8; i++) { const e = sx(t) - x; if (Math.abs(e) < 1e-6) break; const d = dx(t); if (Math.abs(d) < 1e-6) break; t -= e / d; }
    t = K.clamp(t); let lo = 0, hi = 1; for (let i = 0; i < 20 && Math.abs(sx(t) - x) > 1e-6; i++) { if (sx(t) < x) lo = t; else hi = t; t = (lo + hi) / 2; }
    return sy(t);
  };
};
K.E = {
  out: K.bez(0.16, 1, 0.3, 1),        // arrivals, reveals, words
  outSoft: K.bez(0.22, 1, 0.36, 1),
  in: K.bez(0.7, 0, 0.84, 0),         // implosions, snap-outs
  exit: K.bez(0.55, 0.055, 0.675, 0.19), // accelerate into a cut
  inOut: K.bez(0.87, 0, 0.13, 1),     // whips, morphs, lockup slides
  smooth: K.bez(0.65, 0, 0.35, 1),    // fades, drifts
  cam: K.bez(0.48, 0.1, 0, 0.9),      // camera
  dolly: K.bez(0.35, 0, 0.65, 1),     // slow push through a hold
  contact: K.bez(0.55, 0, 0.9, 0.55), // accelerating into an impact
  // OVERSHOOT (Jason r22: "ease in/out & overshoot, always"): pop-ups, buttons, icons, badges, morph landings
  back: K.bez(0.34, 1.56, 0.64, 1),        // ~10% overshoot, one settle, no wobble
  backSoft: K.bez(0.25, 1.32, 0.5, 1),     // ~5%: big objects, cards, hero type
  backIn: K.bez(0.36, 0, 0.66, -0.56),     // anticipation exit: a small pull-back, then gone
};
K.ease = (f, start, dur, e = K.E.out) => e(K.prog(f, start, dur));

// ── one envelope for every punch / tick: quarter-sine attack, exponential decay ──
K.hit = (df, atk = 2, tau = 5) => (df < 0 || df > 32 + atk ? 0 : df < atk ? Math.sin(((df / atk) * Math.PI) / 2) : Math.exp(-(df - atk) / tau));

// ── critically damped spring (zero overshoot), step response 0→1 ──
K.crit = (df, w = 0.16) => (df <= 0 ? 0 : 1 - Math.exp(-w * df) * (1 + w * df));

// ── text measurement (kerned glyph positions: x_i = measure(prefix incl. i) − measure(glyph i)) ──
const _ctx = document.createElement("canvas").getContext("2d");
K.font = (size, wt, fam) => `${wt} ${size}px ${fam}`;
K.measure = (s, font, track = 0, size = 0) => { _ctx.font = font; return _ctx.measureText(s).width + track * size * s.length; };
K.glyphX = (s, font, track, size) => { const xs = []; for (let i = 0; i < s.length; i++) { const w = K.measure(s.slice(0, i + 1), font) - K.measure(s[i], font); xs.push(w + track * size * i); } return xs; };

/** masked baseline rise: each word rises out of its own clip box. words: [{t:frame, w:"word", accent?}] on ONE line, centred */
K.maskLine = (el, words, f, { y, size, wt = 700, fam = "SS4", track = -0.045, color = "#141413", accent = "#D97757", out = 1e9, stagger = 6 } = {}) => {
  if (!words.length || f < words[0].t - 1 || f > out + 24) { el.style.display = "none"; return; }
  el.style.display = "";
  let h = "";
  words.forEach((wd, i) => {
    const pin = K.ease(f, wd.t - 1, 12, K.E.out);
    const pout = K.ease(f, out + (i * stagger) / 2, 10, K.E.in);
    const ty = (1 - pin) * 112 - pout * 112;
    const op = K.clamp(K.prog(f, wd.t - 1, 3)) * (1 - K.prog(f, out + (i * stagger) / 2 + 7, 3));
    const txt = wd.w.replace(/([.?,])$/, `<span style="color:${wd.punct || accent}">$1</span>`);
    h += `<span style="display:inline-block;overflow:hidden;padding:0 0.04em 0.16em;margin:0 ${i < words.length - 1 ? 0.12 : 0}em -0.16em 0;vertical-align:top"><span style="display:inline-block;transform:translateY(${ty}%);opacity:${op}">${txt}</span></span>`;
  });
  el.innerHTML = h;
  Object.assign(el.style, { top: y + "px", fontSize: size + "px", fontWeight: wt, fontFamily: fam, letterSpacing: track + "em", color, fontVariationSettings: '"opsz" 60' });
};

/** shared-letter morph: glyphs present in both strings slide to their new kerned x; the rest fade out / fly in */
K.morphLine = (el, from, to, f, f0, { y, size, wt = 700, fam = "SS4", track = -0.045, color = "#141413", accent = "#D97757", dur = 22, spread = 14, cx = 540 } = {}) => {
  const font = K.font(size, wt, fam);
  const xa = K.glyphX(from, font, track, size), xb = K.glyphX(to, font, track, size);
  const wa = K.measure(from, font, track, size), wb = K.measure(to, font, track, size);
  const offA = cx - wa / 2, offB = cx - wb / 2;
  const used = new Array(from.length).fill(false), pair = [];
  for (let j = 0; j < to.length; j++) { if (to[j] === " ") { pair.push(-1); continue; } let best = -1, bd = 1e9; for (let i = 0; i < from.length; i++) if (!used[i] && from[i] === to[j]) { const d = Math.abs(i / from.length - j / to.length); if (d < bd) { bd = d; best = i; } } if (best >= 0) used[best] = true; pair.push(best); }
  const p = (k) => K.ease(f, f0 + k, dur, K.E.out);
  let h = "";
  const glyph = (ch, x, extra) => `<span style="position:absolute;left:${x}px;top:0;${extra}">${ch === "." ? `<span style="color:${accent}">.</span>` : ch}</span>`;
  // leaving glyphs
  for (let i = 0; i < from.length; i++) if (!used[i] && from[i] !== " ") { const q = K.ease(f, f0, 6, K.E.smooth); if (q < 1) h += glyph(from[i], offA + xa[i], `opacity:${1 - q}`); }
  // staying + arriving glyphs
  for (let j = 0; j < to.length; j++) {
    if (to[j] === " ") continue;
    const k = (j / Math.max(1, to.length - 1)) * spread;
    if (pair[j] >= 0) { const q = p(k * 0.5); h += glyph(to[j], K.lerp(offA + xa[pair[j]], offB + xb[j], q), ""); }
    else { const q = p(k); h += glyph(to[j], offB + xb[j], `transform:translateY(${(1 - q) * 0.42}em);opacity:${K.clamp(q * 2.5)};filter:blur(${(1 - K.clamp(q * 1.6)) * 6}px)`); }   // new glyphs rise in place, clean
  }
  el.innerHTML = `<div style="position:relative;height:${size * 1.2}px">${h}</div>`;
  Object.assign(el.style, { display: "", top: y + "px", fontSize: size + "px", fontWeight: wt, fontFamily: fam, letterSpacing: track + "em", color, fontVariationSettings: '"opsz" 60' });
};

/** place an image so its anchor (fx,fy as fractions) lands on stage point (x,y) at width w (px), rotation rot */
K.anchor = (img, x, y, w, fx, fy, rot = 0, k = 1) => {
  const ar = img.naturalHeight / img.naturalWidth || 1, W = w * k, H = W * ar;
  Object.assign(img.style, { width: W + "px", height: H + "px", transformOrigin: `${fx * 100}% ${fy * 100}%`, transform: `translate(${x - fx * W}px, ${y - fy * H}px) rotate(${rot}deg)` });
};

// ── SVG helpers ──
const NS = "http://www.w3.org/2000/svg";
K.svg = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
/** a path that draws on over [t0, t0+dur] and lifts off from its start over [out, out+lift] */
K.drawOn = (p, f, t0, dur, out = 1e9, lift = 10, e = K.E.out) => {
  const on = f >= t0 - 1 && f < out + lift + 1; p.style.display = on ? "" : "none"; if (!on) return;
  const d = e(K.prog(f, t0, dur)), r = K.E.in(K.prog(f, out, lift));
  p.style.strokeDasharray = `${Math.max(0.0001, d - r)} 3`; p.style.strokeDashoffset = -r;
};
