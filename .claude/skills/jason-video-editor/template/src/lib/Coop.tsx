/**
 * COOP KIT — the "preset look" decoded from Jason Cooperson's Claude-edited YouTube video (sGt1ACELN4k, 2026-10-08).
 * Every value here is a dialed-in preset value, not a per-episode choice (his rule: "have Claude save the values,
 * so it follows the recipe instead of inventing it every time").
 *   - motion graphics animate at 12 fps on the 30 fps timeline (held frames: 3,2,3,2) -> "cinematic" stepped motion
 *   - a glow layer on every graphic + grain on everything
 *   - captions: lowercase bold sans, 2-4 words, ONE accent word in italic serif (Instrument Serif)
 *   - graphics = full-screen hard cutaways on a near-black stage with a blue/violet light band, real UI, real icons
 *   - colour still means something (our locked rule): gold = key idea, green = win, red = problem
 */
import React from "react";
import { AbsoluteFill, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";
import "@fontsource-variable/inter/opsz.css";
import "@fontsource/instrument-serif/400-italic.css";
import { CAPS, Cap } from "../ep/timeline";

export const FPS = 30;
export const STEP = FPS / 12;
export const SANS = "'Inter Variable', Inter, sans-serif";
export const SERIF = "'Instrument Serif', serif";
export const C = { bg: "#060609", ink: "#F4F4F6", dim: "rgba(244,244,246,.46)", gold: "#FFC94A", green: "#34C759", red: "#FF453A", blue: "#3D63FF", violet: "#8B46FF", card: "rgba(28,28,34,.86)" };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** current frame snapped to the 12 fps grid (use for every graphic, never for captions) */
export const useStep = () => {
  const f = useCurrentFrame();
  return Math.floor(f / STEP) * STEP;
};
/** stepped spring: 0 -> 1 starting at `at` (frame inside the current Sequence) */
export const useIn = (at = 0, damping = 18, stiffness = 170) => {
  const f = useStep();
  return spring({ frame: f - at, fps: FPS, config: { damping, stiffness, mass: 0.8 } });
};

/** grain on everything: animated SVG noise, new seed every 12 fps step */
export const Grain: React.FC<{ o?: number }> = ({ o = 0.075 }) => {
  const seed = Math.floor(useCurrentFrame() / STEP) % 9;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "overlay", opacity: o }}>
      <svg width="100%" height="100%"><filter id={`g${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={seed} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter><rect width="100%" height="100%" filter={`url(#g${seed})`} /></svg>
    </AbsoluteFill>
  );
};

/** glow layer: children + a blurred, screen-blended copy (light spills into the air). Keep sounds outside. */
export const Glow: React.FC<{ children: React.ReactNode; k?: number; r?: number }> = ({ children, k = 0.7, r = 22 }) => (
  <AbsoluteFill>
    <AbsoluteFill>{children}</AbsoluteFill>
    <AbsoluteFill style={{ filter: `blur(${r}px) saturate(1.4)`, opacity: k, mixBlendMode: "screen" }}>{children}</AbsoluteFill>
  </AbsoluteFill>
);

/** the stage every cutaway sits on: near-black, blue->violet light band low in frame, slow breathing, vignette */
export const Stage: React.FC = () => {
  const f = useStep();
  const b = 0.85 + 0.15 * Math.sin(f / 22);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill style={{ background: `radial-gradient(70% 22% at 50% 100%, rgba(61,99,255,${0.55 * b}) 0%, rgba(139,70,255,${0.28 * b}) 45%, transparent 80%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(48% 26% at 50% 46%, rgba(61,99,255,${0.13 * b}) 0%, rgba(139,70,255,${0.06 * b}) 50%, transparent 80%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(55% 18% at 30% 0%, rgba(139,70,255,${0.16 * b}) 0%, transparent 70%)` }} />
      <AbsoluteFill style={{ background: "radial-gradient(120% 80% at 50% 45%, transparent 55%, rgba(0,0,0,.75) 100%)" }} />
    </AbsoluteFill>
  );
};

/** a full-screen hard cutaway: stage + glowing content + grain, content settles in on the 12 fps grid */
export const Cutaway: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({ from, to, children }) => (
  <Sequence from={from} durationInFrames={to - from}>
    <CutIn>{children}</CutIn>
  </Sequence>
);
const CutIn: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const p = useIn(0, 20, 190);
  const f = useStep();
  const { durationInFrames: d } = useVideoConfig();
  const push = interpolate(f, [0, d], [0, 0.045], cl); // slow push on the 12 fps grid: the graphic is never still
  return (
    <AbsoluteFill>
      <Stage />
      <AbsoluteFill style={{ transform: `scale(${1.24 + 0.06 * (1 - p) + push})`, filter: `blur(${(1 - p) * 8}px)` }}>
        <Glow>{children}</Glow>
      </AbsoluteFill>
      <Grain o={0.09} />
    </AbsoluteFill>
  );
};

/** lowercase label + one italic-serif accent word, the core type pairing */
export const Pair: React.FC<{ pre?: string; accent: string; post?: string; size?: number; color?: string }> = ({ pre, accent, post, size = 84, color = C.ink }) => (
  <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: size, letterSpacing: "-0.035em", color: C.ink, lineHeight: 1.05, textAlign: "center" }}>
    {pre && <span>{pre} </span>}
    <span style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, fontSize: size * 1.28, letterSpacing: "-0.01em", color }}>{accent}</span>
    {post && <span> {post}</span>}
  </div>
);

// ───────────────────────── captions ─────────────────────────
type Chunk = { words: Cap[]; from: number; to: number };
const clean = (t: string) => t.toLowerCase().replace(/[.,!?]+$/, "");
export const chunkCaps = (caps: Cap[], max = 3): Chunk[] => {
  const out: Chunk[] = [];
  let cur: Cap[] = [];
  const push = () => { if (cur.length) out.push({ words: cur, from: cur[0].f0 - 1, to: 0 }); cur = []; };
  caps.forEach((c, i) => {
    const prev = caps[i - 1];
    if (cur.length && (cur.length >= max || /[.,!?]$/.test(prev.t) || c.f0 - prev.f1 > 8 || c.k !== prev.k)) push();
    cur.push(c);
  });
  push();
  out.forEach((ch, i) => { const last = ch.words[ch.words.length - 1]; ch.to = Math.min(out[i + 1]?.from ?? last.f1 + 12, last.f1 + 18); });
  return out;
};
/**
 * Coop captions: lowercase, 2-3 words, words appear as spoken; the accent word (from `accents`) is italic serif,
 * 1.28x, coloured by meaning. Hidden while a cutaway is on screen (the graphic carries the words).
 */
export const CoopCaptions: React.FC<{ accents: Record<string, string>; hide: [number, number][]; top?: number }> = ({ accents, hide, top = 1330 }) => {
  const f = useCurrentFrame();
  if (hide.some(([a, b]) => f >= a && f < b)) return null;
  const ch = chunkCaps(CAPS).find((c) => f >= c.from && f < c.to);
  if (!ch) return null;
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div style={{ position: "absolute", top, width: 940, display: "flex", flexWrap: "wrap", justifyContent: "center", alignItems: "baseline", columnGap: 22 }}>
        {ch.words.map((w) => {
          const t = f - w.f0 + 1;
          if (t < 0) return null;
          const p = interpolate(t, [0, 4], [0, 1], cl);
          const key = clean(w.t);
          const acc = accents[key];
          return (
            <span key={w.f0} style={{
              fontFamily: acc ? SERIF : SANS, fontStyle: acc ? "italic" : "normal", fontWeight: acc ? 400 : 700,
              fontSize: acc ? 112 : 86, letterSpacing: acc ? "-0.01em" : "-0.035em", color: acc || C.ink, lineHeight: 1.1,
              opacity: p, transform: `translateY(${(1 - p) * 14}px) scale(${0.94 + 0.06 * p})`, filter: `blur(${(1 - p) * 6}px)`,
              textShadow: acc ? `0 0 3px rgba(0,0,0,.9), 0 2px 10px rgba(0,0,0,.85), 0 0 34px rgba(0,0,0,.6), 0 0 26px ${acc}66` : "0 4px 18px rgba(0,0,0,.6), 0 0 2px rgba(0,0,0,.4)",
            }}>{key}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ───────────────────────── graphics (all frames are local to the Cutaway) ─────────────────────────
const tiny: React.CSSProperties = { fontFamily: SANS, fontWeight: 600, fontSize: 30, letterSpacing: "0.12em", color: C.dim, textTransform: "uppercase" };

/** iOS segmented control: thumb sits on `a`, slides to `b` at `flip`; `a` gets struck through. */
export const Segmented: React.FC<{ label: string; a: string; b: string; flip: number }> = ({ label, a, b, flip }) => {
  const enter = useIn(0);
  const s = useIn(flip, 16, 160);
  const strike = interpolate(useStep(), [flip + 4, flip + 12], [0, 1], cl);
  const W = 740, half = W / 2 - 12;
  const thumbColor = s > 0.5 ? C.green : C.red;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", gap: 70, flexDirection: "column", opacity: enter, transform: `translateY(${(1 - enter) * 40}px)` }}>
      <div style={tiny}>{label}</div>
      <div style={{ position: "relative", width: W, height: 150, borderRadius: 75, background: "rgba(118,118,128,.24)", boxShadow: "inset 0 1px 0 rgba(255,255,255,.08)" }}>
        <div style={{ position: "absolute", top: 12, left: 12 + s * half, width: half, height: 126, borderRadius: 63, background: "linear-gradient(180deg,#3a3a42,#26262c)", boxShadow: `0 10px 30px rgba(0,0,0,.5), 0 0 40px ${thumbColor}55, inset 0 1px 0 rgba(255,255,255,.14)` }} />
        {[a, b].map((t, i) => {
          const on = i === 0 ? 1 - s : s;
          return (
            <div key={t} style={{ position: "absolute", top: 0, left: 12 + i * half, width: half, height: 150, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ position: "relative", fontFamily: on > 0.5 ? SERIF : SANS, fontStyle: on > 0.5 ? "italic" : "normal", fontWeight: on > 0.5 ? 400 : 650, fontSize: on > 0.5 ? 76 : 54, color: i === 1 ? (s > 0.5 ? C.green : C.dim) : s > 0.5 ? C.dim : C.ink, letterSpacing: "-0.02em" }}>
                {t}
                {i === 0 && <span style={{ position: "absolute", left: -6, right: -6, top: "54%", height: 6, borderRadius: 3, background: C.red, transformOrigin: "0 50%", transform: `scaleX(${strike})`, boxShadow: `0 0 18px ${C.red}` }} />}
              </span>
            </div>
          );
        })}
      </div>
      <Pair pre="being" accent="nice" size={78} color={s > 0.5 ? C.green : C.ink} />
    </AbsoluteFill>
  );
};

/** pixel-grid meter (his green-pixel graphic): cells light column by column up to `pct` from `fill` */
export const PixelMeter: React.FC<{ label: string; pct: number; fill: number }> = ({ label, pct, fill }) => {
  const f = useStep();
  const enter = useIn(0);
  const cols = 12, rows = 7, cell = 50, gap = 10;
  const lit = interpolate(f, [fill, fill + 30], [0, pct / 100], { ...cl, easing: (t) => 1 - Math.pow(1 - t, 3) }) * cols;
  const n = Math.round(interpolate(f, [fill, fill + 30], [0, pct], { ...cl, easing: (t) => 1 - Math.pow(1 - t, 3) }));
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 56, opacity: enter }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 28 }}>
        <Pair accent={label} size={80} color={C.gold} />
      </div>
      <div style={{ padding: 34, borderRadius: 48, background: C.card, boxShadow: "0 30px 80px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.07)" }}>
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, ${cell}px)`, gap }}>
          {Array.from({ length: cols * rows }).map((_, i) => {
            const c = i % cols, r = Math.floor(i / cols);
            const on = c < Math.floor(lit) || (c === Math.floor(lit) && (rows - r) / rows < lit % 1);
            const wave = 0.75 + 0.25 * Math.sin(f / 5 + c * 0.6 + r);
            return <div key={i} style={{ width: cell, height: cell, borderRadius: 12, background: on ? C.green : "rgba(255,255,255,.06)", opacity: on ? wave : 1, boxShadow: on ? `0 0 16px ${C.green}aa` : "none" }} />;
          })}
        </div>
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 150, color: C.ink, letterSpacing: "-0.05em", fontVariantNumeric: "tabular-nums" }}>{n}<span style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, color: C.green, fontSize: 130 }}>%</span></div>
    </AbsoluteFill>
  );
};

/** equation tiles (his "$20 ÷ ▢▢▢▢ = 4 edits"): a tile, an arrow that draws, the payoff tile glows gold */
export const Equation: React.FC<{ pre: string; a: string; b: string; at: number; bt: number }> = ({ pre, a, b, at, bt }) => {
  const f = useStep();
  const pa = useIn(at), pb = useIn(bt, 14, 150);
  const arrow = interpolate(f, [bt - 8, bt], [0, 1], cl);
  const tile = (t: string, p: number, col: string, big: boolean): React.ReactNode => (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * 50}px) scale(${0.9 + 0.1 * p})`, padding: big ? "34px 64px" : "28px 54px", borderRadius: 40, background: big ? `linear-gradient(180deg, ${col}, #E09B12)` : "rgba(52,199,89,.16)", boxShadow: big ? `0 0 70px ${col}aa, 0 20px 50px rgba(0,0,0,.5)` : "inset 0 0 0 3px rgba(52,199,89,.55)", color: big ? "#1a1204" : C.green, fontFamily: big ? SERIF : SANS, fontStyle: big ? "italic" : "normal", fontWeight: big ? 400 : 750, fontSize: big ? 120 : 76, letterSpacing: big ? "-0.01em" : "-0.03em" }}>{t}</div>
  );
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 40 }}>
      <div style={{ ...tiny, opacity: pa }}>{pre}</div>
      {tile(a, pa, C.green, false)}
      <svg width="80" height="150" style={{ overflow: "visible" }}>
        <path d="M40 0 L40 130 M14 104 L40 132 L66 104" fill="none" stroke={C.ink} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - arrow} />
      </svg>
      {tile(b, pb, C.gold, true)}
    </AbsoluteFill>
  );
};

/** real-looking dark comment cards (his YouTube "Comments" card), stacking on given frames */
export const Comments: React.FC<{ app: string; items: { user: string; text: string; at: number; hue: number }[]; fade?: number }> = ({ app, items, fade }) => {
  const f = useStep();
  const out = fade ? interpolate(f, [fade, fade + 5], [1, 0.25], cl) : 1;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 830, padding: "40px 44px", borderRadius: 52, background: C.card, boxShadow: "0 40px 100px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.07)", opacity: out, filter: fade && f > fade ? "saturate(.3)" : "none" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 26 }}>
          <div style={{ width: 54, height: 38, borderRadius: 10, background: C.red, display: "flex", alignItems: "center", justifyContent: "center" }}><div style={{ width: 0, height: 0, borderLeft: "16px solid #fff", borderTop: "10px solid transparent", borderBottom: "10px solid transparent", marginLeft: 4 }} /></div>
          <span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 42, color: C.ink }}>{app}</span>
          <span style={{ fontFamily: SANS, fontWeight: 500, fontSize: 32, color: C.dim, marginLeft: "auto" }}>{items.filter((i) => f >= i.at).length}</span>
        </div>
        {items.map((it) => {
          const p = spring({ frame: f - it.at, fps: FPS, config: { damping: 18, stiffness: 190 } });
          if (f < it.at) return null;
          return (
            <div key={it.at} style={{ display: "flex", gap: 22, padding: "22px 0", borderTop: "1px solid rgba(255,255,255,.07)", opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
              <div style={{ width: 72, height: 72, borderRadius: 36, flexShrink: 0, background: `linear-gradient(135deg, hsl(${it.hue},70%,60%), hsl(${it.hue + 40},70%,40%))` }} />
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <span style={{ fontFamily: SANS, fontWeight: 600, fontSize: 30, color: C.dim }}>@{it.user} · 2m ago</span>
                <span style={{ fontFamily: SANS, fontWeight: 550, fontSize: 44, color: C.ink, letterSpacing: "-0.02em" }}>{it.text}</span>
                <span style={{ fontFamily: SANS, fontWeight: 600, fontSize: 28, color: C.dim }}>👍 {12 + (it.hue % 40)}   👎   Reply</span>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** the red X (his "Don't Do This" frame): two strokes draw on, glow, then the line under it */
export const BigX: React.FC<{ at: number; pre?: string; accent: string; post?: string }> = ({ at, pre, accent, post }) => {
  const f = useStep();
  const s1 = interpolate(f, [at, at + 5], [0, 1], cl), s2 = interpolate(f, [at + 3, at + 8], [0, 1], cl);
  const t = useIn(at + 6);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 60 }}>
      <AbsoluteFill style={{ background: `radial-gradient(45% 30% at 50% 42%, rgba(255,69,58,${0.35 * s1}) 0%, transparent 70%)` }} />
      <svg width="420" height="420" viewBox="0 0 100 100" style={{ overflow: "visible" }}>
        <path d="M18 18 L82 82" stroke={C.red} strokeWidth="11" strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - s1} />
        <path d="M82 18 L18 82" stroke={C.red} strokeWidth="11" strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - s2} />
      </svg>
      <div style={{ opacity: t, transform: `translateY(${(1 - t) * 30}px)` }}><Pair pre={pre} accent={accent} post={post} size={82} color={C.red} /></div>
    </AbsoluteFill>
  );
};

/** iOS settings toggle that flips off at `flip`, with the line his words give it */
export const Toggle: React.FC<{ label: string; flip: number; pre?: string; accent: string; post?: string }> = ({ label, flip, pre, accent, post }) => {
  const enter = useIn(0);
  const s = useIn(flip, 15, 210);
  const t = useIn(flip + 6);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 80 }}>
      <div style={{ width: 760, padding: "40px 40px", borderRadius: 48, background: C.card, display: "flex", alignItems: "center", gap: 28, opacity: enter, transform: `translateY(${(1 - enter) * 40}px)`, boxShadow: "0 30px 80px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.07)" }}>
        <div style={{ width: 78, height: 78, borderRadius: 20, background: "linear-gradient(180deg,#8E8E93,#636366)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 44 }}>⚙️</div>
        <span style={{ fontFamily: SANS, fontWeight: 600, fontSize: 40, color: C.ink, letterSpacing: "-0.02em", flex: 1, whiteSpace: "nowrap" }}>{label}</span>
        <div style={{ width: 150, height: 90, borderRadius: 45, background: s > 0.5 ? "rgba(120,120,128,.36)" : C.green, position: "relative", boxShadow: s > 0.5 ? "none" : `0 0 30px ${C.green}88` }}>
          <div style={{ position: "absolute", top: 6, left: 66 - s * 60, width: 78, height: 78, borderRadius: 39, background: "#fff", boxShadow: "0 4px 12px rgba(0,0,0,.35)" }} />
        </div>
      </div>
      <div style={{ opacity: t, transform: `translateY(${(1 - t) * 30}px)` }}><Pair pre={pre} accent={accent} post={post} size={80} color={C.gold} /></div>
    </AbsoluteFill>
  );
};
