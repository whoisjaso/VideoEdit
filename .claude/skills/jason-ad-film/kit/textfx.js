/* textfx.js — per-unit kinetic text for pure seek(t) engines.
   Recreates the "Kenyset" After Effects text-animator pack (42 presets, decoded from the .ffx files; values in kenyset-presets.json).
   Each preset = a from-state (x/y offset, scale x/y, rotation, opacity, blur, tracking) that every unit (char / word / line) travels out of,
   staggered across the text (AE Range Selector, shape Ramp Up, smoothness 100, ease high/low), plus an optional per-unit elastic spring
   (the pack's expression: amount = 1.5·cos(2π·2.5·τ)·e^(−7τ), 0.08 s delay per unit) on the transform channels.
   usage:  const T = TextFX.make(el, "Build the self no one claps for.", preset, {size: 96});  then each frame: T.seek(t - t0)   */
(function (G) {
  const bez = (x1, y1, x2, y2) => { // cubic-bezier timing function (y may exceed 0..1)
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = (t) => ((ax * t + bx) * t + cx) * t, Y = (t) => ((ay * t + by) * t + cy) * t, dX = (t) => (3 * ax * t + 2 * bx) * t + cx;
    return (x) => { if (x <= 0) return 0; if (x >= 1) return 1; let t = x; for (let i = 0; i < 8; i++) { const d = dX(t); if (Math.abs(d) < 1e-6) break; t -= (X(t) - x) / d; } return Y(Math.min(1, Math.max(0, t))); };
  };
  const EASE = { "50,100": bez(0.4, 0, 0.1, 1), "-100,100": bez(0.08, 0.75, 0.1, 1), "-50,100": bez(0.2, 0.5, 0.1, 1), "0,50": bez(0.33, 0, 0.3, 1), "0,0": (x) => x };
  const STAGGER = { char: 0.035, word: 0.09, line: 0.2 }, DUR = { char: 0.55, word: 0.6, line: 0.75 };
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const spring = (tau) => tau < 0 ? 1 : clamp(1.5 * Math.cos(2 * Math.PI * 2.5 * tau) * Math.exp(-7 * tau), -1, 1);
  function split(el, text, unit) { // nested spans: lines > words > chars; returns arrays per unit kind
    el.innerHTML = ""; const out = { char: [], word: [], line: [] };
    text.split("\n").forEach((ln, li) => {
      const L = document.createElement("span"); L.style.display = "inline-block"; L.style.whiteSpace = "nowrap"; out.line.push(L); el.appendChild(L);
      if (li) el.insertBefore(document.createElement("br"), L);
      ln.split(" ").forEach((w, wi) => {
        if (wi) L.appendChild(document.createTextNode(" "));
        const W = document.createElement("span"); W.style.display = "inline-block"; out.word.push(W); L.appendChild(W);
        [...w].forEach((c) => { const C = document.createElement("span"); C.style.display = "inline-block"; C.textContent = c; out.char.push(C); W.appendChild(C); });
      });
    });
    return out;
  }
  function make(el, text, p, o = {}) {
    const size = o.size || 96, k = size / 100, U = split(el, text, p.unit), units = U[p.unit], ease = EASE[`${p.easeHi},${p.easeLo}`] || EASE["50,100"];
    const st = (o.stagger || STAGGER[p.unit]), dur = o.dur || DUR[p.unit];
    const bunits = p.bounce ? U[p.bounce] : null, bIndex = new Map();
    if (bunits) units.forEach((u) => { const b = bunits.find((x) => x === u || x.contains(u) || u.contains(x)); bIndex.set(u, b ? bunits.indexOf(b) : 0); });
    function seek(t) {
      units.forEach((u, i) => {
        let w, wt;
        if (p.shape === "square") { w = t < i * (o.typeRate || 0.045) ? 1 : 0; wt = w; }
        else { const q = clamp((t - i * st) / dur); w = 1 - ease(q); wt = bunits ? (t - i * st < 0 ? 1 : spring(t - i * st)) : w; }
        const sx = 1 + (p.sx / 100 - 1) * wt, sy = 1 + (p.sy / 100 - 1) * wt;
        u.style.transform = `translate(${p.x * k * wt}px, ${p.y * k * wt}px) rotate(${p.rot * wt}deg) scale(${sx}, ${sy})`;
        u.style.opacity = (1 + (p.op / 100 - 1) * w).toFixed(3);
        u.style.filter = p.blur ? `blur(${(p.blur * k * 0.5 * w).toFixed(2)}px)` : "";
        if (p.track) u.style.marginRight = `${(p.track / 1000) * w}em`;
      });
    }
    seek(0); return { seek, length: (units.length - 1) * (p.shape === "square" ? (o.typeRate || 0.045) : st) + dur + (bunits ? 0.6 : 0) };
  }
  G.TextFX = { make, spring, bez };
})(typeof window !== "undefined" ? window : globalThis);
