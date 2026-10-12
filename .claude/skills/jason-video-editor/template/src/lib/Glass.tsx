import React from "react";
import "@fontsource-variable/inter/opsz.css";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { noise2D } from "@remotion/noise";

/**
 * iOS motion-graphics kit (Jason 2026-10-08: "iOS-like UX, soft borderless animations") at r05 quality.
 * Look: frosted borderless cards, continuous big radii, layered soft shadows, no outlines, accent gradient text.
 * Motion: critically-damped springs (no bounce), fade + scale .94→1 + blur 16→0, shared-element morphs, swipe-to-delete.
 * Quality layers still apply: wrap the foreground in <Bloom k≈0.6> (Blueprint2), parallax <Cam>, CameraMotionBlur.
 */
export const G = { ink: "#F5F7FF", sub: "rgba(235,240,255,0.62)", faint: "rgba(235,240,255,0.32)", accent: "#FF6A3D", accent2: "#FFB36B", red: "#FF453A", green: "#30D158",
  font: "'Inter Variable', Inter", glass: "rgba(255,255,255,0.10)", glassHot: "rgba(255,106,61,0.18)" };
export const IOS = { damping: 30, stiffness: 210, mass: 1 }; // no overshoot
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const sm = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t));

export const useIn = (at: number, until = 1e9, cfg = IOS) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - at, fps, config: cfg });
  const o = sm((f - (until - 10)) / 10);
  return { f, fps, p, o, on: f >= at - 1 && f < until, style: { opacity: Math.min(1, p * 1.25) * (1 - o), filter: `blur(${(1 - p) * 16 + o * 12}px)`, transform: `translateY(${(1 - p) * 40 - o * 20}px) scale(${0.94 + 0.06 * p - o * 0.03})` } as React.CSSProperties };
};

/** iOS-wallpaper world: slow mesh-gradient blobs (parallax), a faint dot grid, grain, vignette. `warm` adds accent blobs; `pools` light up on cue */
export const Wallpaper: React.FC<{ pools?: { x: number; y: number; r: number; at?: number; color?: string }[]; light?: boolean }> = ({ pools = [], light }) => {
  const f = useCurrentFrame();
  const blob = (k: string, x: number, y: number, r: number, c: string) => {
    const dx = noise2D(k, f / 260, 0) * 120, dy = noise2D(k + "y", 0, f / 300) * 140;
    return <div key={k} style={{ position: "absolute", left: x + dx - r, top: y + dy - r, width: r * 2, height: r * 2, borderRadius: "50%", background: c, filter: "blur(90px)" }} />;
  };
  if (light) {
    return (
      <AbsoluteFill style={{ background: "#ECEDF2", overflow: "hidden" }}>
        {blob("l1", 200, 300, 520, "rgba(255,190,150,0.55)")}{blob("l2", 900, 1300, 620, "rgba(170,190,255,0.55)")}{blob("l3", 500, 1800, 500, "rgba(255,255,255,0.9)")}
        <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(30,30,60,0.10) 1.2px, transparent 1.6px)", backgroundSize: "34px 34px" }} />
        <GrainS o={0.05} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ background: "#0B0D1E", overflow: "hidden" }}>
      {blob("b1", 160, 380, 620, "rgba(70,82,210,0.65)")}{blob("b2", 980, 900, 560, "rgba(120,60,200,0.42)")}{blob("b3", 420, 1650, 700, "rgba(40,60,160,0.55)")}{blob("b4", 900, 120, 380, "rgba(255,120,70,0.22)")}
      {pools.map((p, i) => {
        const on = p.at === undefined ? 1 : sm((f - p.at) / 20);
        return <div key={i} style={{ position: "absolute", left: p.x - p.r, top: p.y - p.r, width: p.r * 2, height: p.r * 2, borderRadius: "50%", background: p.color ?? "rgba(255,106,61,0.55)", filter: "blur(110px)", opacity: on }} />;
      })}
      <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(235,240,255,0.10) 1.2px, transparent 1.6px)", backgroundSize: "34px 34px", transform: `translateY(${-f * 0.12}px)` }} />
      <SoftDust />
      <GrainS o={0.07} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 50%, rgba(0,0,8,0.55) 100%)" }} />
    </AbsoluteFill>
  );
};
const SoftDust: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill>{Array.from({ length: 36 }).map((_, i) => {
    const z = random(`sz${i}`), x = (random(`sx${i}`) * 1100 + noise2D(`sn${i}`, f / 240, i) * 50) % 1100, y = (random(`sy${i}`) * 1960 - f * (0.2 + z * 0.5) + 4000) % 1960;
    return <div key={i} style={{ position: "absolute", left: x, top: y, width: 2 + z * 4, height: 2 + z * 4, borderRadius: "50%", background: "#fff", opacity: 0.08 + z * 0.22, filter: `blur(${(1 - z) * 3}px)` }} />;
  })}</AbsoluteFill>;
};
const GrainS: React.FC<{ o: number }> = ({ o }) => {
  const f = useCurrentFrame();
  const s = Math.round(f) % 89;
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: o, mixBlendMode: "overlay" }}>
      <filter id={`gs${s}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={s} /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter={`url(#gs${s})`} />
    </svg>
  );
};

/** frosted borderless card: blur material, soft inner highlight (no stroke), layered shadow, big radius */
export const glassStyle = (hot = false, r = 44): React.CSSProperties => ({
  background: hot ? G.glassHot : G.glass, backdropFilter: "blur(40px) saturate(1.8)", WebkitBackdropFilter: "blur(40px) saturate(1.8)", borderRadius: r,
  boxShadow: `inset 0 1px 0 rgba(255,255,255,0.14), 0 30px 80px rgba(0,0,10,0.45), 0 8px 22px rgba(0,0,10,0.25)${hot ? `, 0 0 90px rgba(255,106,61,0.35)` : ""}`,
});

/** section header (small caps grey) + card body, iOS grouped-list style */
export const Card: React.FC<{ x: number; y: number; w: number; h?: number; at: number; until?: number; header?: string; hot?: number; children: React.ReactNode; foot?: string }> = ({ x, y, w, h, at, until, header, hot, children, foot }) => {
  const { f, on, style } = useIn(at, until);
  if (!on) return null;
  const isHot = hot !== undefined && f >= hot;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, ...style }}>
      {header && <div style={{ fontFamily: G.font, fontSize: 22, fontWeight: 600, letterSpacing: "0.06em", color: G.sub, margin: "0 0 12px 26px", textTransform: "uppercase" }}>{header}</div>}
      <div style={{ ...glassStyle(isHot), height: h, padding: "30px 34px", transition: "none" }}>{children}</div>
      {foot && <div style={{ fontFamily: G.font, fontSize: 20, color: G.faint, margin: "12px 0 0 26px" }}>{foot}</div>}
    </div>
  );
};

/** list row: SF-symbol-style glyph in a rounded tile + title + subtitle + trailing accessory */
export const Row: React.FC<{ icon: string; tint: string; title: string; sub?: string; trail?: React.ReactNode; at: number; dim?: boolean }> = ({ icon, tint, title, sub, trail, at, dim }) => {
  const { on, style } = useIn(at);
  if (!on) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 24, padding: "14px 0", opacity: dim ? 0.45 : 1, ...style }}>
      <div style={{ width: 72, height: 72, borderRadius: 18, background: tint, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 38, boxShadow: "inset 0 1px 0 rgba(255,255,255,0.3)" }}>{icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: G.font, fontWeight: 700, fontSize: 40, color: G.ink, letterSpacing: "-0.01em" }}>{title}</div>
        {sub && <div style={{ fontFamily: G.font, fontSize: 24, color: G.sub, marginTop: 2 }}>{sub}</div>}
      </div>
      {trail}
    </div>
  );
};

/** swipe-to-delete: the card slides left revealing a red Delete pill, then collapses (iOS way to "strike" something) */
export const Swipe: React.FC<{ at: number; children: React.ReactNode; w: number; h: number }> = ({ at, children, w, h }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: f - at, fps, config: IOS });
  const gone = spring({ frame: f - at - 16, fps, config: IOS });
  return (
    <div style={{ position: "relative", width: w, height: h * (1 - gone * 0.0), opacity: 1 - gone * 0.65, transform: `scale(${1 - gone * 0.06})` }}>
      <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: 260 * s, borderRadius: 44, background: G.red, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden",
        boxShadow: `0 0 ${60 * s}px rgba(255,69,58,0.55)` }}>
        <span style={{ fontFamily: G.font, fontWeight: 700, fontSize: 34, color: "#fff", opacity: s }}>Delete</span>
      </div>
      <div style={{ transform: `translateX(${-260 * s}px)` }}>{children}</div>
    </div>
  );
};

/** iOS headline: sentence case, words fade up out of blur on their spoken frame; unspoken words faint; keep-words get the accent gradient */
export const Title: React.FC<{ words: { t: string; at: number }[]; keep?: string[]; x?: number; y?: number; size?: number; until?: number; w?: number }> = ({ words, keep = [], x = 70, y = 190, size = 76, until = 1e9, w = 940 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < words[0].at - 10 || f >= until) return null;
  const o = sm((f - (until - 10)) / 10);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, display: "flex", flexWrap: "wrap", columnGap: size * 0.24, fontFamily: G.font, fontWeight: 800, fontSize: size, lineHeight: 1.08, letterSpacing: "-0.03em",
      opacity: 1 - o, filter: o > 0 ? `blur(${o * 12}px)` : undefined }}>
      {words.map((wd, i) => {
        const p = spring({ frame: f - wd.at, fps, config: IOS });
        const said = f >= wd.at - 1;
        const isKeep = keep.includes(wd.t.replace(/[^A-Za-z0-9']/g, "").toUpperCase());
        const st: React.CSSProperties = isKeep && said
          ? { backgroundImage: `linear-gradient(100deg, ${G.accent} 10%, ${G.accent2} 90%)`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }
          : { color: said ? G.ink : "rgba(235,240,255,0.14)" };
        return <span key={i} style={{ display: "inline-block", ...st, opacity: said ? 0.3 + 0.7 * p : 1, filter: said && p < 0.99 ? `blur(${(1 - p) * 10}px)` : undefined, transform: `translateY(${said ? (1 - p) * 18 : 0}px)` }}>{wd.t}</span>;
      })}
    </div>
  );
};

/** Dynamic-Island pill that morphs into a full card (shared-element), content crossfades in */
export const Island: React.FC<{ at: number; open: number; until: number; x: number; y: number; w: number; h: number; pill: React.ReactNode; children: React.ReactNode }> = ({ at, open, until, x, y, w, h, pill, children }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at || f >= until) return null;
  const a = spring({ frame: f - at, fps, config: IOS }), m = spring({ frame: f - open, fps, config: { damping: 32, stiffness: 160, mass: 1 } });
  const o = sm((f - (until - 10)) / 10);
  const pw = 380, ph = 104, px = 540 - pw / 2, py = 70;
  const L = px + (x - px) * m, T = py + (y - py) * m, Wd = (pw + (w - pw) * m) * (0.6 + 0.4 * a), Ht = ph + (h - ph) * m, R = 52 - 8 * m;
  return (
    <div style={{ position: "absolute", left: L + (pw - Wd) * (1 - m) / 2, top: T, width: Wd, height: Ht, borderRadius: R, background: `rgba(${12 + 8 * m},${13 + 9 * m},${24 + 14 * m},${0.98 - 0.25 * m})`,
      backdropFilter: "blur(40px)", boxShadow: "0 30px 80px rgba(0,0,10,0.5), inset 0 1px 0 rgba(255,255,255,0.08)", overflow: "hidden", opacity: a * (1 - o), filter: o > 0 ? `blur(${o * 10}px)` : undefined }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", opacity: 1 - m * 1.6 }}>{pill}</div>
      <div style={{ position: "absolute", inset: 0, opacity: interpolate(m, [0.45, 1], [0, 1], cl), padding: 34 }}>{children}</div>
    </div>
  );
};

/** capsule tag */
export const Chip: React.FC<{ t: string; at: number; tint?: string; x: number; y: number; big?: boolean }> = ({ t, at, tint = G.accent, x, y, big }) => {
  const { on, style } = useIn(at);
  if (!on) return null;
  return <div style={{ position: "absolute", left: x, top: y, padding: big ? "18px 40px" : "10px 26px", borderRadius: 999, background: tint, color: "#fff", fontFamily: G.font, fontWeight: 800, fontSize: big ? 52 : 28,
    boxShadow: `0 14px 40px ${tint}66, inset 0 1px 0 rgba(255,255,255,0.35)`, ...style }}>{t}</div>;
};

/** activity-style progress ring */
export const Ring: React.FC<{ cx: number; cy: number; r: number; at: number; to: number; color?: string; label?: string }> = ({ cx, cy, r, at, to, color = G.accent, label }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at) return null;
  const p = spring({ frame: f - at, fps, config: { damping: 40, stiffness: 60 } }) * to;
  const C = 2 * Math.PI * r;
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <circle cx={cx} cy={cy} r={r} stroke={`${color}33`} strokeWidth={34} fill="none" />
      <circle cx={cx} cy={cy} r={r} stroke={color} strokeWidth={34} fill="none" strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - p)} transform={`rotate(-90 ${cx} ${cy})`} style={{ filter: `drop-shadow(0 0 18px ${color}88)` }} />
      {label && <text x={cx} y={cy + 18} textAnchor="middle" fill={G.ink} fontFamily="Inter" fontWeight={800} fontSize={54}>{label}</text>}
    </svg>
  );
};

/** iOS chrome micro-detail: page dots + home indicator + tiny caption */
export const Chrome: React.FC<{ page: number; pages: number; caption?: string; dark?: boolean }> = ({ page, pages, caption, dark }) => {
  const c = dark ? "rgba(20,20,30," : "rgba(240,244,255,";
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", bottom: 120, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 14 }}>
        {Array.from({ length: pages }).map((_, i) => <div key={i} style={{ width: i === page ? 34 : 12, height: 12, borderRadius: 6, background: `${c}${i === page ? 0.9 : 0.3})` }} />)}
      </div>
      <div style={{ position: "absolute", bottom: 40, left: 360, width: 360, height: 10, borderRadius: 5, background: `${c}0.55)` }} />
      {caption && <div style={{ position: "absolute", bottom: 160, left: 0, right: 0, textAlign: "center", fontFamily: "Inter", fontSize: 20, color: `${c}0.45)` }}>{caption}</div>}
    </AbsoluteFill>
  );
};

/** soft full-screen word moment (iOS version of the slam): accent gradient field, word scales/fades in, no hard flash */
export const Moment: React.FC<{ words: { t: string; at: number }[]; until: number }> = ({ words, until }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < words[0].at - 4 || f >= until) return null;
  const bg = spring({ frame: f - words[0].at + 4, fps, config: IOS });
  return (
    <AbsoluteFill style={{ opacity: bg }}>
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 42%, ${G.accent2} 0%, ${G.accent} 45%, #C9381A 100%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${30 + noise2D("m", f / 60, 0) * 20}% 20%, rgba(255,255,255,0.35), transparent 45%)` }} />
      {words.map((w, i) => {
        const p = spring({ frame: f - w.at, fps, config: IOS }), next = words[i + 1];
        const q = next ? spring({ frame: f - next.at, fps, config: IOS }) : 0;
        if (f < w.at - 1 || q > 0.99) return null;
        return <div key={i} style={{ position: "absolute", top: 0, bottom: 0, left: 0, right: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Inter", fontWeight: 900,
          fontSize: w.t.length > 8 ? 150 : 230, letterSpacing: "-0.045em", color: "#fff", opacity: p * (1 - q), filter: `blur(${(1 - p) * 18 + q * 18}px)`, transform: `scale(${0.9 + 0.1 * p + q * 0.12})`,
          textShadow: "0 20px 60px rgba(120,20,0,0.35)" }}>{w.t}</div>;
      })}
    </AbsoluteFill>
  );
};

/* ---------------- v4: 3D camera + whip transitions (after v3 scored 6.9: "nothing moves, too small, flat camera") ---------------- */
type CamKey = { f: number; rx?: number; ry?: number; rz?: number; x?: number; y?: number; z?: number };
const lerpKeys = (keys: CamKey[], f: number) => {
  const k = [...keys].sort((a, b) => a.f - b.f);
  if (f <= k[0].f) return k[0];
  for (let i = 0; i < k.length - 1; i++) {
    const a = k[i], b = k[i + 1];
    if (f <= b.f) {
      const t = (f - a.f) / Math.max(1, b.f - a.f), e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; // easeInOutCubic
      const m = (p: keyof CamKey) => ((a[p] as number) ?? 0) + ((((b[p] as number) ?? 0) - ((a[p] as number) ?? 0)) * e);
      return { f, rx: m("rx"), ry: m("ry"), rz: m("rz"), x: m("x"), y: m("y"), z: m("z") };
    }
  }
  return k[k.length - 1];
};
/** a real 3D stage: children are placed in 3D (use <Z depth> inside); the camera flies through keyframes (eased) */
export const Stage3D: React.FC<{ keys: CamKey[]; children: React.ReactNode; persp?: number }> = ({ keys, children, persp = 1700 }) => {
  const f = useCurrentFrame();
  const c = lerpKeys(keys, f);
  return (
    <AbsoluteFill style={{ perspective: persp, perspectiveOrigin: "50% 45%" }}>
      <AbsoluteFill style={{ transformStyle: "preserve-3d", transform: `translate3d(${c.x ?? 0}px, ${c.y ?? 0}px, ${c.z ?? 0}px) rotateX(${c.rx ?? 0}deg) rotateY(${c.ry ?? 0}deg) rotateZ(${c.rz ?? 0}deg)` }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
/** depth layer inside Stage3D: positive = toward the camera (moves more on camera moves = parallax for free) */
export const Z: React.FC<{ depth: number; children: React.ReactNode }> = ({ depth, children }) => (
  <AbsoluteFill style={{ transform: `translateZ(${depth}px)`, transformStyle: "preserve-3d" }}>{children}</AbsoluteFill>
);
/** whip: scene enters swinging in from the right (rotateY + x) and exits whipping left; pair with CameraMotionBlur samples≥7 for the smear */
export const Whip: React.FC<{ from: number; to: number; inLen?: number; outLen?: number; children: React.ReactNode }> = ({ from, to, inLen = 10, outLen = 9, children }) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const ei = (t: number) => 1 - Math.pow(1 - Math.max(0, Math.min(1, t)), 4), eo = (t: number) => Math.pow(Math.max(0, Math.min(1, t)), 3);
  const i = from === 0 ? 1 : ei((f - from) / inLen), o = eo((f - (to - outLen)) / outLen);
  const x = (1 - i) * 1300 - o * 1300, ry = (1 - i) * -38 + o * 38;
  return (
    <AbsoluteFill style={{ perspective: 1400 }}>
      <AbsoluteFill style={{ transform: `translateX(${x}px) rotateY(${ry}deg) scale(${1 - 0.08 * Math.max(1 - i, o)})`, opacity: Math.min(1, i * 2) * (1 - o * 0.6) }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
