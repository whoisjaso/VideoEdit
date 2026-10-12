import React from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { noise2D } from "@remotion/noise";

/**
 * r05 kit v2: built after Jason scored v1 6.8 ("the glows, smooth animations, the backgrounds, the infinitesimal details").
 * Four layers every beat must have (references/mg-quality-bar.md §8):
 *   1 BLOOM: <Bloom> re-renders the foreground blurred + screen-blended, so light spills into the air
 *   2 SMOOTHNESS: <Cam> parallax depth + noise drift + push; wrap scenes in @remotion/motion-blur CameraMotionBlur; <Push> transitions w/ RGB split
 *   3 DEPTH BACKGROUND: <World>: far blurred grid + sharp near grid w/ intersection dots, light pools, dust, grain, scanlines, leak, vignette
 *   4 HUD MICRO-DETAIL: <Hud>: corner brackets, edge rulers, live timecode, readouts; <Anchor> crosshair + coordinates; <Dash> construction lines
 * Sounds must stay OUTSIDE <Bloom> (it renders children 3x).
 */
export const C = { navy0: "#24306a", navy1: "#121838", navy2: "#0a0d22", hot: "#FF5A2A", warm: "#FFB15C", ice: "#CFDBFF", text: "#F6F8FF",
  line: "rgba(200,214,255,0.62)", faint: "rgba(200,214,255,0.22)", mono: "'JetBrains Mono', monospace", head: "Inter" };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const ease = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3));
const smooth = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t));

/* ---------------- 1. BLOOM ---------------- */
export const Bloom: React.FC<{ children: React.ReactNode; k?: number }> = ({ children, k = 1 }) => (
  <AbsoluteFill>
    <AbsoluteFill>{children}</AbsoluteFill>
    <AbsoluteFill style={{ filter: "blur(14px) brightness(1.5) saturate(1.3)", mixBlendMode: "screen", opacity: 0.6 * k, pointerEvents: "none" }}>{children}</AbsoluteFill>
    <AbsoluteFill style={{ filter: "blur(55px) brightness(2.2) saturate(1.4)", mixBlendMode: "screen", opacity: 0.42 * k, pointerEvents: "none" }}>{children}</AbsoluteFill>
  </AbsoluteFill>
);

/* ---------------- 2. CAMERA / PARALLAX / TRANSITIONS ---------------- */
/** depth layer: depth 0 = far (moves least), 1 = near. Noise drift + push-in + tiny roll, all eased. */
export const Cam: React.FC<{ from: number; to: number; depth?: number; push?: number; children: React.ReactNode }> = ({ from, to, depth = 1, push = 0.07, children }) => {
  const f = useCurrentFrame();
  const t = smooth((f - from) / Math.max(1, to - from));
  const dx = noise2D("cx", f / 140, 0) * 26 * depth, dy = noise2D("cy", 0, f / 160) * 22 * depth;
  const rot = noise2D("cr", f / 220, 3) * 0.6 * depth;
  return <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px) scale(${1 + push * t * (0.4 + 0.6 * depth)}) rotate(${rot}deg)` }}>{children}</AbsoluteFill>;
};

/** push-through transition: outgoing zooms+blurs out, incoming zooms in from 0.86, RGB split + bloom flash on the cut */
export const Push: React.FC<{ from: number; to: number; inLen?: number; outLen?: number; children: React.ReactNode }> = ({ from, to, inLen = 9, outLen = 8, children }) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const i = ease((f - from) / inLen), o = ease((f - (to - outLen)) / outLen);
  const s = (0.86 + 0.14 * i) * (1 + 0.32 * o);
  const blur = (1 - i) * 14 + o * 18;
  const split = Math.max(1 - i, o) * 14;
  return (
    <AbsoluteFill style={{ transform: `scale(${s})`, filter: `blur(${blur}px)`, opacity: Math.min(1, i * 1.4) * (1 - o * 0.9) }}>
      {split > 0.5 ? (
        <>
          <AbsoluteFill style={{ transform: `translateX(${-split}px)`, mixBlendMode: "screen", filter: "url(#onlyR)" }}>{children}</AbsoluteFill>
          <AbsoluteFill style={{ mixBlendMode: "screen", filter: "url(#onlyG)" }}>{children}</AbsoluteFill>
          <AbsoluteFill style={{ transform: `translateX(${split}px)`, mixBlendMode: "screen", filter: "url(#onlyB)" }}>{children}</AbsoluteFill>
        </>
      ) : children}
    </AbsoluteFill>
  );
};
/** put once at the root: SVG filters used by <Push> RGB split */
export const Filters: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="onlyR"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="onlyG"><feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="onlyB"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" /></filter>
  </svg>
);

/* ---------------- 3. DEPTH BACKGROUND ---------------- */
/** pools: light pools {x,y,r,color,at} that fade in on their frame and breathe */
export const World: React.FC<{ pools?: { x: number; y: number; r: number; color?: string; at?: number }[]; floor?: boolean; paper?: boolean }> = ({ pools = [], floor, paper }) => {
  const f = useCurrentFrame();
  if (paper) {
    return (
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 45% 30%, #fbfaf6 0%, #e9e6dd 60%, #d6d2c6 100%)" }}>
        <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(40,40,60,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(40,40,60,0.07) 1px, transparent 1px)", backgroundSize: "36px 36px" }} />
        <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(60,50,30,0.25) 1px, transparent 1.4px)", backgroundSize: "7px 7px", opacity: 0.18 }} />
        <Grain o={0.07} />
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(60,50,30,0.22) 100%)" }} />
      </AbsoluteFill>
    );
  }
  const gx = noise2D("gx", f / 300, 1) * 18, gy = noise2D("gy", 2, f / 300) * 14 - f * 0.15;
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at ${50 + noise2D("lx", f / 400, 0) * 8}% 36%, ${C.navy0} 0%, ${C.navy1} 48%, ${C.navy2} 100%)`, overflow: "hidden" }}>
      {/* far grid: big cells, defocused, slow */}
      <AbsoluteFill style={{ backgroundImage: `linear-gradient(rgba(170,190,255,0.10) 2px, transparent 2px), linear-gradient(90deg, rgba(170,190,255,0.10) 2px, transparent 2px)`, backgroundSize: "180px 180px",
        backgroundPosition: `${gx * 0.4}px ${gy * 0.4}px`, filter: "blur(3px)", opacity: 0.8, transform: "scale(1.15)" }} />
      {/* near grid: sharp minor + major lines + intersection dots */}
      <AbsoluteFill style={floor ? { top: "40%", height: "130%", transform: `perspective(650px) rotateX(66deg)`, transformOrigin: "50% 0%" } : {}}>
        <AbsoluteFill style={{ backgroundImage: `linear-gradient(rgba(180,198,255,0.075) 1px, transparent 1px), linear-gradient(90deg, rgba(180,198,255,0.075) 1px, transparent 1px),
          linear-gradient(rgba(190,206,255,0.17) 1px, transparent 1px), linear-gradient(90deg, rgba(190,206,255,0.17) 1px, transparent 1px),
          radial-gradient(rgba(220,230,255,0.55) 1.6px, transparent 2px)`,
          backgroundSize: "45px 45px, 45px 45px, 225px 225px, 225px 225px, 225px 225px", backgroundPosition: `${gx}px ${gy}px, ${gx}px ${gy}px, ${gx}px ${gy}px, ${gx}px ${gy}px, ${gx - 112}px ${gy - 112}px` }} />
      </AbsoluteFill>
      {/* light pools behind the action */}
      {pools.map((p, i) => {
        const on = p.at === undefined ? 1 : interpolate(f - p.at, [0, 18], [0, 1], cl);
        const br = 1 + noise2D(`p${i}`, f / 50, 0) * 0.08;
        return <div key={i} style={{ position: "absolute", left: p.x - p.r * br, top: p.y - p.r * br, width: p.r * 2 * br, height: p.r * 2 * br, borderRadius: "50%",
          background: `radial-gradient(circle, ${p.color ?? C.hot}55 0%, ${p.color ?? C.hot}18 40%, transparent 70%)`, opacity: on, mixBlendMode: "screen" }} />;
      })}
      {/* top light leak */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% -10%, rgba(140,160,255,0.22) 0%, transparent 45%)", mixBlendMode: "screen" }} />
      <Dust />
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 4px)" }} />
      <Grain o={0.09} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 46%, transparent 40%, rgba(2,3,12,0.7) 100%)" }} />
    </AbsoluteFill>
  );
};
const Dust: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 70 }).map((_, i) => {
        const z = random(`dz${i}`), x = (random(`dx${i}`) * 1180 + noise2D(`dn${i}`, f / 200, i) * 60 + f * (0.1 + z * 0.3)) % 1180 - 50;
        const y = (random(`dy${i}`) * 2000 - f * (0.15 + z * 0.5) + 4000) % 2000 - 40;
        const r = 1 + z * 3.2, tw = 0.35 + 0.65 * Math.abs(noise2D(`dt${i}`, f / 30, 0));
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: r, height: r, borderRadius: "50%", background: z > 0.85 ? C.warm : C.ice, opacity: (0.15 + z * 0.45) * tw, filter: `blur(${(1 - z) * 2.5}px)` }} />;
      })}
    </AbsoluteFill>
  );
};
export const Grain: React.FC<{ o?: number }> = ({ o = 0.08 }) => {
  const f = useCurrentFrame();
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: o, mixBlendMode: "overlay", pointerEvents: "none" }}>
      <filter id={`gr${f}`}><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={f % 97} /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter={`url(#gr${f})`} />
    </svg>
  );
};

/* ---------------- 4. HUD MICRO-DETAIL ---------------- */
export const Mono: React.FC<{ x: number; y: number; s?: number; o?: number; c?: string; children: React.ReactNode; at?: number; align?: "left" | "right" }> = ({ x, y, s = 17, o = 0.5, c = C.ice, children, at = -999, align = "left" }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const q = interpolate(f - at, [0, 8], [0, 1], cl);
  return <div style={{ position: "absolute", left: align === "left" ? x : undefined, right: align === "right" ? 1080 - x : undefined, top: y, fontFamily: C.mono, fontSize: s, color: c, opacity: o * q, letterSpacing: "0.05em", whiteSpace: "nowrap" }}>{children}</div>;
};
/** whole-frame HUD: corner brackets, edge rulers with ticks + numbers, live timecode, scene readouts */
export const Hud: React.FC<{ fig: string; scene: string; refId: string; readouts?: string[] }> = ({ fig, scene, refId, readouts = [] }) => {
  const f = useCurrentFrame();
  const br = (x: number, y: number, sx: number, sy: number) => <path d={`M${x},${y + sy * 34} L${x},${y} L${x + sx * 34},${y}`} stroke={C.line} strokeWidth={2} fill="none" />;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {br(28, 28, 1, 1)}{br(1052, 28, -1, 1)}{br(28, 1892, 1, -1)}{br(1052, 1892, -1, -1)}
        {/* left ruler */}
        {Array.from({ length: 49 }).map((_, i) => <line key={`l${i}`} x1={0} x2={i % 5 ? 10 : 22} y1={90 + i * 36} y2={90 + i * 36} stroke={C.faint} strokeWidth={1.5} />)}
        {/* bottom ruler */}
        {Array.from({ length: 28 }).map((_, i) => <line key={`b${i}`} y1={1920} y2={i % 5 ? 1910 : 1898} x1={70 + i * 36} x2={70 + i * 36} stroke={C.faint} strokeWidth={1.5} />)}
        {/* top progress hairline */}
        <line x1={70} x2={1010} y1={84} y2={84} stroke={C.faint} strokeWidth={1} />
        <line x1={70} x2={70 + (Math.round(f) % 300) / 300 * 940} y1={84} y2={84} stroke={C.hot} strokeWidth={2} />
      </svg>
      {[0, 5, 10, 15, 20, 25, 30, 35, 40, 45].map((i) => <Mono key={i} x={28} y={84 + i * 36} s={12} o={0.32}>{String(i * 36).padStart(4, "0")}</Mono>)}
      <Mono x={70} y={48} s={17} o={0.62}>{fig}</Mono>
      <Mono x={1010} y={48} s={17} o={0.62} align="right">t = {(f / 30).toFixed(3)} s</Mono>
      <Mono x={70} y={1846} s={15} o={0.38}>{refId}</Mono>
      <Mono x={1010} y={1846} s={15} o={0.38} align="right">{scene} · {String(Math.round(f)).padStart(5, "0")}f</Mono>
      {readouts.map((r, i) => <Mono key={i} x={1010} y={1700 + i * 24} s={14} o={0.34} align="right">{r}</Mono>)}
    </AbsoluteFill>
  );
};
/** crosshair + live coordinates on an anchor point */
export const Anchor: React.FC<{ x: number; y: number; at: number; label?: string; hot?: boolean }> = ({ x, y, at, label, hot }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const q = ease((f - at) / 10), c = hot ? C.hot : C.line;
  return (
    <>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: q }}>
        <circle cx={x} cy={y} r={14 * q} stroke={c} strokeWidth={1.5} fill="none" />
        <line x1={x - 24} x2={x - 6} y1={y} y2={y} stroke={c} strokeWidth={1.5} /><line x1={x + 6} x2={x + 24} y1={y} y2={y} stroke={c} strokeWidth={1.5} />
        <line y1={y - 24} y2={y - 6} x1={x} x2={x} stroke={c} strokeWidth={1.5} /><line y1={y + 6} y2={y + 24} x1={x} x2={x} stroke={c} strokeWidth={1.5} />
        <circle cx={x} cy={y} r={2.5} fill={hot ? C.hot : C.text} />
      </svg>
      <Mono x={x + 22} y={y + 14} s={13} o={0.55 * q} c={hot ? C.hot : C.ice}>({Math.round(x)}, {Math.round(y)}){label ? ` · ${label}` : ""}</Mono>
    </>
  );
};
/** dashed construction line that draws on */
export const Dash: React.FC<{ x1: number; y1: number; x2: number; y2: number; at: number }> = ({ x1, y1, x2, y2, at }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const q = ease((f - at) / 16);
  return <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}><line x1={x1} y1={y1} x2={x1 + (x2 - x1) * q} y2={y1 + (y2 - y1) * q} stroke={C.faint} strokeWidth={1.5} strokeDasharray="6 8" /></svg>;
};

/* ---------------- CONTENT PIECES (v2) ---------------- */
/** headline, per-CHARACTER reveal: ghost outline → blur-in white; the spoken word flashes hot; keep-words stay hot */
export const Headline: React.FC<{ words: { t: string; at: number }[]; keep?: string[]; x?: number; y?: number; size?: number; until?: number; w?: number }> = ({ words, keep = [], x = 70, y = 170, size = 78, until = 1e9, w = 940 }) => {
  const f = useCurrentFrame();
  if (f < words[0].at - 10 || f >= until) return null;
  const out = ease((f - (until - 7)) / 7);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, display: "flex", flexWrap: "wrap", columnGap: size * 0.25, rowGap: size * 0.02, fontFamily: C.head, fontWeight: 800, fontSize: size, lineHeight: 1.06, letterSpacing: "-0.025em",
      opacity: 1 - out, filter: out > 0 ? `blur(${out * 10}px)` : undefined, transform: `translateY(${-out * 20}px)` }}>
      {words.map((wd, i) => {
        const isKeep = keep.includes(wd.t.replace(/[^A-Za-z0-9']/g, "").toUpperCase());
        const flash = interpolate(f - wd.at, [0, 2, 14], [1, 1, 0], cl);
        return (
          <span key={i} style={{ display: "inline-flex" }}>
            {wd.t.split("").map((ch, j) => {
              const ca = wd.at + j * 0.9, p = ease((f - ca) / 7), said = f >= ca;
              const col = isKeep ? C.hot : `rgb(${246 + (255 - 246) * flash}, ${248 - (248 - 90) * flash}, ${255 - (255 - 42) * flash})`;
              return <span key={j} style={{ color: said ? col : "transparent", WebkitTextStroke: said ? undefined : "1.2px rgba(200,214,255,0.22)", display: "inline-block",
                filter: said && p < 1 ? `blur(${(1 - p) * 9}px)` : undefined, transform: `translateY(${said ? (1 - p) * 16 : 0}px)`, opacity: said ? 0.25 + 0.75 * p : 1 }}>{ch}</span>;
            })}
          </span>
        );
      })}
    </div>
  );
};

/** technical node: line-drawn frame, inner fill sweeps in, corner ticks, header strip + label + sub + tiny id */
export const Panel: React.FC<{ x: number; y: number; w: number; h: number; at: number; label: string; sub?: string; id?: string; hot?: number; dead?: number; fs?: number }> = ({ x, y, w, h, at, label, sub, id, hot, dead, fs = 40 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at) return null;
  const q = ease((f - at) / 14), isHot = hot !== undefined && f >= hot, isDead = dead !== undefined && f >= dead;
  const hp = hot !== undefined ? spring({ frame: f - hot, fps, config: { damping: 18, stiffness: 160 } }) : 0;
  const per = 2 * (w + h), c = isDead ? "rgba(255,90,42,0.45)" : isHot ? C.hot : C.line;
  const tick = (tx: number, ty: number, sx: number, sy: number) => <path d={`M${tx + sx * 16},${ty} L${tx},${ty} L${tx},${ty + sy * 16}`} stroke={isHot ? C.warm : C.ice} strokeWidth={3} fill="none" />;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: isDead ? 0.5 : 1, transform: `scale(${1 + hp * 0.04 - (isDead ? 0.03 : 0)})` }}>
      <svg width={w} height={h} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <rect x={0} y={0} width={w} height={h} fill={isHot ? "rgba(255,90,42,0.13)" : "rgba(16,22,58,0.82)"} opacity={interpolate(f - at, [4, 16], [0, 1], cl)} />
        <rect x={0} y={0} width={w * interpolate(f - at, [6, 22], [0, 1], cl)} height={30} fill={isHot ? "rgba(255,90,42,0.28)" : "rgba(200,214,255,0.08)"} />
        <rect x={1} y={1} width={w - 2} height={h - 2} fill="none" stroke={c} strokeWidth={2.5} strokeDasharray={per} strokeDashoffset={per * (1 - q)} />
        {q > 0.9 && <>{tick(-6, -6, 1, 1)}{tick(w + 6, -6, -1, 1)}{tick(-6, h + 6, 1, -1)}{tick(w + 6, h + 6, -1, -1)}</>}
      </svg>
      <Mono x={12} y={6} s={14} o={0.6} c={isHot ? C.warm : C.ice} at={at + 8}>{id ?? "node"}</Mono>
      <Mono x={w - 12} y={6} s={14} o={0.45} c={isHot ? C.warm : C.ice} at={at + 10} align="right">{isDead ? "status: struck" : isHot ? "status: live" : "status: idle"}</Mono>
      <div style={{ position: "absolute", left: 0, right: 0, top: 30, bottom: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: interpolate(f - at, [8, 18], [0, 1], cl) }}>
        <div style={{ fontFamily: C.mono, fontWeight: 700, fontSize: fs, letterSpacing: "0.1em", color: isHot ? C.hot : C.text, textDecoration: isDead ? "line-through" : "none", textDecorationColor: C.hot }}>{label}</div>
        {sub && <div style={{ fontFamily: C.mono, fontSize: Math.round(fs * 0.46), color: C.ice, opacity: 0.55, marginTop: 8 }}>{sub}</div>}
      </div>
    </div>
  );
};

/** wire with line-draw, flowing dash particles along it, and a comet with an anamorphic flare */
export const Beam: React.FC<{ x1: number; y1: number; x2: number; y2: number; at: number; comet?: number; curve?: number; hot?: boolean }> = ({ x1, y1, x2, y2, at, comet, curve = 0, hot }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const mx = (x1 + x2) / 2 + curve * 0.3, my = (y1 + y2) / 2 - curve;
  const d = `M${x1},${y1} Q${mx},${my} ${x2},${y2}`;
  const len = Math.hypot(x2 - x1, y2 - y1) * (1 + Math.abs(curve) / 500);
  const q = ease((f - at) / 16);
  const bez = (t: number) => [(1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2];
  const cq = comet !== undefined ? smooth((f - comet) / 18) : -1;
  const [cx, cy] = bez(Math.max(0, Math.min(1, cq)));
  const arrive = comet !== undefined ? interpolate(f - comet - 18, [0, 4, 20], [0, 1, 0], cl) : 0;
  const [ex, ey] = bez(1);
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <path d={d} stroke={hot ? C.hot : C.line} strokeWidth={2.5} fill="none" strokeDasharray={len} strokeDashoffset={len * (1 - q)} />
      {q >= 1 && <path d={d} stroke={hot ? C.warm : C.ice} strokeWidth={2} fill="none" strokeDasharray="2 22" strokeDashoffset={-f * 2.2} opacity={0.55} />}
      {cq > 0 && cq < 1 && <g>
        {[0.06, 0.12, 0.18, 0.24].map((k, i) => { const [tx, ty] = bez(Math.max(0, cq - k)); return <circle key={i} cx={tx} cy={ty} r={7 - i * 1.5} fill={C.warm} opacity={0.5 - i * 0.11} />; })}
        <ellipse cx={cx} cy={cy} rx={70} ry={3} fill="#fff" opacity={0.75} />
        <ellipse cx={cx} cy={cy} rx={3} ry={34} fill="#fff" opacity={0.4} />
        <circle cx={cx} cy={cy} r={30} fill={C.hot} opacity={0.35} />
        <circle cx={cx} cy={cy} r={8} fill="#fff" />
      </g>}
      {arrive > 0 && <g opacity={arrive}><circle cx={ex} cy={ey} r={10 + 40 * (1 - arrive)} stroke={C.warm} strokeWidth={3} fill="none" /><ellipse cx={ex} cy={ey} rx={110} ry={3} fill="#fff" /></g>}
    </svg>
  );
};

/** corner-to-corner strike with sparks and a light-flash at the crossing */
export const Slash: React.FC<{ x: number; y: number; w: number; h: number; at: number }> = ({ x, y, w, h, at }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const a = ease((f - at) / 6), b = ease((f - at - 4) / 6), L = Math.hypot(w, h);
  const sparks = (px: number, py: number, k: string, t0: number) => Array.from({ length: 14 }).map((_, i) => {
    const ang = random(`${k}${i}`) * Math.PI * 2, sp = 2 + random(`${k}v${i}`) * 7, t = Math.max(0, f - at - t0);
    return <circle key={k + i} cx={px + Math.cos(ang) * sp * t} cy={py + Math.sin(ang) * sp * t + 0.25 * t * t} r={1.5 + random(`${k}r${i}`) * 2} fill={i % 3 ? C.warm : "#fff"} opacity={interpolate(t, [0, 18], [1, 0], cl)} />;
  });
  const flash = interpolate(f - at - 10, [0, 3, 16], [0, 1, 0], cl);
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <line x1={x} y1={y} x2={x + w} y2={y + h} stroke={C.hot} strokeWidth={6} strokeDasharray={L} strokeDashoffset={L * (1 - a)} strokeLinecap="round" />
      <line x1={x + w} y1={y} x2={x} y2={y + h} stroke={C.hot} strokeWidth={6} strokeDasharray={L} strokeDashoffset={L * (1 - b)} strokeLinecap="round" />
      <line x1={x} y1={y} x2={x + w * a} y2={y + h * a} stroke="#fff" strokeWidth={2} opacity={0.8} />
      {a < 1 && sparks(x + w * a, y + h * a, "a", 0)}
      {b > 0 && b < 1 && sparks(x + w * (1 - b), y + h * b, "b", 4)}
      {flash > 0 && <g opacity={flash}><circle cx={x + w / 2} cy={y + h / 2} r={60} fill={C.hot} opacity={0.4} /><ellipse cx={x + w / 2} cy={y + h / 2} rx={260} ry={4} fill="#fff" /></g>}
    </svg>
  );
};

/** full-screen orange slam (v2: subtle grid + grain on the orange, punch-in, light sweep) */
export const SlamV2: React.FC<{ words: { t: string; at: number }[]; until: number }> = ({ words, until }) => {
  const f = useCurrentFrame();
  if (f < words[0].at || f >= until) return null;
  const cur = [...words].reverse().find((w) => f >= w.at)!;
  const k = f - cur.at;
  const sweep = interpolate(k, [0, 10], [-30, 130], cl);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #FF7A45 0%, #FF5A2A 60%, #E8481C 100%)", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(20,20,40,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(20,20,40,0.06) 1px, transparent 1px)", backgroundSize: "45px 45px" }} />
      <div style={{ fontFamily: "'Archivo Black', Inter", fontSize: cur.t.length > 8 ? 150 : 240, color: "#16162c", letterSpacing: "-0.035em", transform: `scale(${interpolate(k, [0, 3, 10], [1.22, 1.03, 1], cl)})`,
        filter: k < 2 ? "blur(6px)" : undefined, textShadow: "0 18px 50px rgba(120,20,0,0.35)" }}>{cur.t}</div>
      <AbsoluteFill style={{ background: `linear-gradient(105deg, transparent ${sweep - 12}%, rgba(255,255,255,0.28) ${sweep}%, transparent ${sweep + 12}%)` }} />
      <Grain o={0.12} />
      <Mono x={1010} y={1840} s={16} o={0.6} c="#16162c" align="right">{(f / 30).toFixed(2)}</Mono>
      <Mono x={70} y={1840} s={16} o={0.6} c="#16162c">SLAM · {words.indexOf(cur) + 1}/{words.length}</Mono>
    </AbsoluteFill>
  );
};

/** dot crowd that assembles from scatter, then lights up hot in a ripple from a point */
export const Crowd: React.FC<{ at: number; lit: number; cols?: number; rows?: number; x0?: number; y0?: number; gap?: number }> = ({ at, lit, cols = 12, rows = 9, x0 = 100, y0 = 760, gap = 80 }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const ox = x0 + (cols - 1) * gap / 2, oy = y0 + rows * gap + 60;
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
      {Array.from({ length: cols * rows }).map((_, i) => {
        const tx = x0 + (i % cols) * gap, ty = y0 + Math.floor(i / cols) * gap;
        const sx = random(`sx${i}`) * 1080, sy = random(`sy${i}`) * 1920;
        const p = ease((f - at - random(`st${i}`) * 24) / 22);
        const x = sx + (tx - sx) * p, y = sy + (ty - sy) * p;
        const dist = Math.hypot(tx - ox, ty - oy);
        const h = ease((f - lit - dist / 40) / 8);
        const r = 6 + 6 * h;
        return <g key={i}>
          {h > 0 && <circle cx={x} cy={y} r={r * 2.4} fill={C.hot} opacity={0.18 * h} />}
          <circle cx={x} cy={y} r={r} fill={h > 0.5 ? C.hot : C.ice} opacity={p * (0.55 + 0.45 * h)} />
        </g>;
      })}
    </svg>
  );
};

/** paper-form detail layer: punch holes, red margin rule, typed form fields, checkboxes, signature line (fills the page like r05's FORM 2-B) */
export const PaperDetail: React.FC<{ at: number; fields: { k: string; v: string; at: number }[]; checks?: { t: string; at: number; x?: boolean }[]; sign?: { t: string; at: number } }> = ({ at, fields, checks = [], sign }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const ink = "#2a2a30";
  return (
    <AbsoluteFill>
      {[420, 960, 1500].map((y) => <div key={y} style={{ position: "absolute", left: 26, top: y, width: 26, height: 26, borderRadius: 13, background: "#cfcbbf", boxShadow: "inset 0 2px 4px rgba(0,0,0,0.25)" }} />)}
      <div style={{ position: "absolute", left: 64, top: 0, bottom: 0, width: 2, background: "rgba(220,60,40,0.35)" }} />
      {fields.map((fl, i) => {
        const n = Math.max(0, Math.floor((f - fl.at) * 1.4));
        return (
          <div key={i} style={{ position: "absolute", left: 90, right: 70, top: 1010 + i * 92, display: "flex", alignItems: "flex-end", gap: 18, opacity: interpolate(f - fl.at, [-6, 0], [0, 1], cl) }}>
            <span style={{ fontFamily: C.mono, fontSize: 18, letterSpacing: "0.14em", color: ink, opacity: 0.55, width: 220 }}>{fl.k}</span>
            <span style={{ flex: 1, borderBottom: "2px solid rgba(42,42,48,0.35)", fontFamily: C.mono, fontSize: 36, color: "#1d3a8a", paddingBottom: 4 }}>{fl.v.slice(0, n)}</span>
          </div>
        );
      })}
      {checks.map((c, i) => f >= c.at - 8 && (
        <div key={i} style={{ position: "absolute", left: 90 + i * 300, top: 1390, display: "flex", alignItems: "center", gap: 12, fontFamily: C.mono, fontSize: 22, letterSpacing: "0.12em", color: ink }}>
          <span style={{ width: 30, height: 30, border: `2px solid ${ink}`, display: "inline-flex", alignItems: "center", justifyContent: "center", color: C.hot, fontSize: 30, fontWeight: 700 }}>{f >= c.at ? (c.x ? "✕" : "✓") : ""}</span>{c.t}
        </div>
      ))}
      {sign && f >= sign.at && (
        <div style={{ position: "absolute", left: 90, top: 1540, width: 520 }}>
          <svg width={520} height={90}><path d="M10,60 C60,10 90,80 140,40 S220,20 250,55 S330,70 360,30 S440,50 500,40" stroke="#1d3a8a" strokeWidth={4} fill="none" strokeDasharray={900} strokeDashoffset={900 * (1 - ease((f - sign.at) / 20))} strokeLinecap="round" /></svg>
          <div style={{ borderTop: "2px solid rgba(42,42,48,0.4)", fontFamily: C.mono, fontSize: 16, letterSpacing: "0.14em", color: ink, opacity: 0.55, paddingTop: 6 }}>{sign.t}</div>
        </div>
      )}
    </AbsoluteFill>
  );
};
