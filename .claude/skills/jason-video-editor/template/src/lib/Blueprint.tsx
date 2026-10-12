import React from "react";
import { AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * r05 motion-graphics kit (references/mg-quality-bar.md): one navy-blueprint world, bloom, one hot accent, micro-labels,
 * spoken-word sweep, comets along lines, line-draw everything, full-screen word slams.
 * Every prop that says `at` is a frame from at(section, WORD) so things land on his words.
 */
export const BP = { bg0: "#1d2554", bg1: "#0f1430", grid: "rgba(160,180,255,0.09)", grid5: "rgba(160,180,255,0.18)", line: "rgba(190,205,255,0.55)",
  hot: "#FF5A2A", warm: "#FFB347", text: "#F4F6FF", dim: "rgba(220,228,255,0.28)", mono: "'JetBrains Mono', monospace", head: "Inter" };
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const glow = (c: string, r = 18) => `0 0 ${r}px ${c}, 0 0 ${r * 2.2}px ${c}66`;

/** the world: radial navy, blueprint grid (every 5th line stronger), slow dolly, vignette, grain. `floor` tilts the grid into 3D. */
export const Stage: React.FC<{ from: number; to: number; floor?: boolean; dolly?: number; light?: boolean; children?: React.ReactNode }> = ({ from, to, floor, dolly = 0.06, light, children }) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const t = (f - from) / Math.max(1, to - from);
  const s = 1 + dolly * t;
  const bg = light ? "radial-gradient(ellipse at 50% 35%, #f3f2ee 0%, #dcdad3 100%)" : `radial-gradient(ellipse at 50% 38%, ${BP.bg0} 0%, ${BP.bg1} 75%)`;
  const gl = light ? "rgba(40,40,60,0.06)" : BP.grid, g5 = light ? "rgba(40,40,60,0.12)" : BP.grid5;
  const grid = `linear-gradient(${g5} 1px, transparent 1px), linear-gradient(90deg, ${g5} 1px, transparent 1px), linear-gradient(${gl} 1px, transparent 1px), linear-gradient(90deg, ${gl} 1px, transparent 1px)`;
  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      <AbsoluteFill style={floor
        ? { top: "38%", height: "120%", backgroundImage: grid, backgroundSize: "300px 300px, 300px 300px, 60px 60px, 60px 60px", transform: `perspective(700px) rotateX(64deg) translateY(${-t * 120}px)`, transformOrigin: "50% 0%", opacity: 0.9 }
        : { backgroundImage: grid, backgroundSize: "270px 270px, 270px 270px, 54px 54px, 54px 54px", transform: `scale(${s})` }} />
      <AbsoluteFill style={{ transform: `scale(${s})` }}>{children}</AbsoluteFill>
      <AbsoluteFill style={{ background: light ? "radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.18) 100%)" : "radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(0,0,0,0.55) 100%)", pointerEvents: "none" }} />
      <AbsoluteFill style={{ opacity: light ? 0.05 : 0.07, pointerEvents: "none", backgroundImage: `radial-gradient(rgba(255,255,255,${0.5 + random(`g${f % 6}`) * 0.5}) 1px, transparent 1px)`, backgroundSize: `${3 + (f % 3)}px ${3 + (f % 2)}px` }} />
    </AbsoluteFill>
  );
};

/** tiny technical label (the "expensive" detail) */
export const Micro: React.FC<{ x: number; y: number; children: React.ReactNode; o?: number; color?: string; size?: number }> = ({ x, y, children, o = 0.5, color = BP.text, size = 17 }) => (
  <div style={{ position: "absolute", left: x, top: y, fontFamily: BP.mono, fontSize: size, color, opacity: o, letterSpacing: "0.04em", whiteSpace: "nowrap" }}>{children}</div>
);

/** kinetic headline: words not yet spoken = ghost outline; the spoken word flashes HOT then settles white; `keep` words stay hot */
export const KLine: React.FC<{ words: { t: string; at: number }[]; keep?: string[]; x?: number; y?: number; size?: number; until?: number; maxW?: number }> = ({ words, keep = [], x = 70, y = 160, size = 64, until = 1e9, maxW = 940 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < words[0].at - 8 || f >= until) return null;
  const out = interpolate(f, [until - 6, until], [1, 0], cl);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: maxW, display: "flex", flexWrap: "wrap", columnGap: size * 0.26, rowGap: size * 0.05, fontFamily: BP.head, fontWeight: 800, fontSize: size, lineHeight: 1.08, letterSpacing: "-0.02em", opacity: out }}>
      {words.map((w, i) => {
        const p = spring({ frame: f - w.at, fps, config: { damping: 20, stiffness: 200 } });
        const said = f >= w.at;
        const isKeep = keep.includes(w.t.replace(/[^A-Za-z0-9']/g, "").toUpperCase());
        const flash = interpolate(f - w.at, [0, 3, 12], [1, 1, 0], cl);
        const col = !said ? "transparent" : isKeep ? BP.hot : flash > 0.01 ? BP.hot : BP.text;
        return (
          <span key={i} style={{ color: col, WebkitTextStroke: said ? "0px" : `1.5px ${BP.dim}`, textShadow: said ? glow(isKeep || flash > 0.3 ? `${BP.hot}aa` : "rgba(255,255,255,0.35)", 14) : "none",
            filter: said ? `blur(${(1 - p) * 8}px)` : "none", transform: `translateY(${said ? (1 - p) * 14 : 0}px)`, display: "inline-block" }}>{w.t}</span>
        );
      })}
    </div>
  );
};

/** labelled technical box that draws itself on (border line-draw), optional hot state */
export const Node: React.FC<{ x: number; y: number; w?: number; h?: number; label: string; sub?: string; at: number; hot?: number; dead?: number; fs?: number }> = ({ x, y, w = 380, h = 150, label, sub, at, hot, dead, fs = 38 }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const q = interpolate(f - at, [0, 12], [0, 1], cl);
  const isHot = hot !== undefined && f >= hot, isDead = dead !== undefined && f >= dead;
  const per = 2 * (w + h);
  const c = isDead ? "rgba(255,90,42,0.35)" : isHot ? BP.hot : BP.line;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: isDead ? 0.45 : 1 }}>
      <svg width={w} height={h} style={{ position: "absolute", inset: 0, overflow: "visible", filter: isHot ? `drop-shadow(0 0 10px ${BP.hot})` : "none" }}>
        <rect x={1} y={1} width={w - 2} height={h - 2} fill={isHot ? "rgba(255,90,42,0.10)" : "rgba(20,26,60,0.7)"} stroke={c} strokeWidth={3} strokeDasharray={per} strokeDashoffset={per * (1 - q)} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: interpolate(f - at, [6, 14], [0, 1], cl) }}>
        <div style={{ fontFamily: BP.mono, fontWeight: 700, fontSize: fs, letterSpacing: "0.1em", color: isHot ? BP.hot : BP.text, textShadow: isHot ? glow(`${BP.hot}88`, 10) : "none", textDecoration: isDead ? "line-through" : "none" }}>{label}</div>
        {sub && <div style={{ fontFamily: BP.mono, fontSize: Math.round(fs * 0.5), color: BP.text, opacity: 0.5, marginTop: 8 }}>{sub}</div>}
      </div>
    </div>
  );
};

/** a line that draws from A to B, then a glowing comet travels it (light is the connector) */
export const Wire: React.FC<{ x1: number; y1: number; x2: number; y2: number; at: number; comet?: number; curve?: number; hot?: boolean }> = ({ x1, y1, x2, y2, at, comet, curve = 0, hot }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - curve;
  const d = `M${x1},${y1} Q${mx},${my} ${x2},${y2}`;
  const len = Math.hypot(x2 - x1, y2 - y1) * (1 + Math.abs(curve) / 600);
  const q = interpolate(f - at, [0, 14], [0, 1], cl);
  const cq = comet !== undefined ? interpolate(f - comet, [0, 16], [0, 1], { ...cl }) : -1;
  const bez = (t: number) => [(1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2];
  const [cx, cy] = bez(Math.max(0, cq));
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <path d={d} stroke={hot ? BP.hot : BP.line} strokeWidth={3} fill="none" style={{ filter: hot ? `drop-shadow(0 0 6px ${BP.hot})` : "none" }} strokeDasharray={len} strokeDashoffset={len * (1 - q)} />
      {cq >= 0 && cq < 1 && <>
        <circle cx={cx} cy={cy} r={34} fill={BP.hot} opacity={0.3} style={{ filter: "blur(14px)" }} />
        <circle cx={cx} cy={cy} r={9} fill="#fff" style={{ filter: `drop-shadow(0 0 8px ${BP.hot}) drop-shadow(0 0 18px ${BP.warm})` }} />
      </>}
    </svg>
  );
};

/** two hot strike lines draw corner to corner over a box, with sparks at the tips */
export const Strike: React.FC<{ x: number; y: number; w: number; h: number; at: number }> = ({ x, y, w, h, at }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const a = interpolate(f - at, [0, 7], [0, 1], cl), b = interpolate(f - at, [4, 11], [0, 1], cl);
  const L = Math.hypot(w, h);
  const spark = (px: number, py: number, k: string) => Array.from({ length: 7 }).map((_, i) => {
    const ang = random(`${k}${i}`) * Math.PI * 2, dist = interpolate(f - at, [0, 14], [0, 26 + random(`${k}d${i}`) * 30], cl);
    return <circle key={k + i} cx={px + Math.cos(ang) * dist} cy={py + Math.sin(ang) * dist} r={2} fill={BP.warm} opacity={interpolate(f - at, [0, 16], [1, 0], cl)} />;
  });
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, overflow: "visible", filter: `drop-shadow(0 0 6px ${BP.hot})` }}>
      <line x1={x} y1={y} x2={x + w} y2={y + h} stroke={BP.hot} strokeWidth={4} strokeDasharray={L} strokeDashoffset={L * (1 - a)} strokeLinecap="round" />
      <line x1={x + w} y1={y} x2={x} y2={y + h} stroke={BP.hot} strokeWidth={4} strokeDasharray={L} strokeDashoffset={L * (1 - b)} strokeLinecap="round" />
      {a > 0 && a < 1 && spark(x + w * a, y + h * a, "a")}
      {b > 0 && b < 1 && spark(x + w * (1 - b), y + h * b, "b")}
    </svg>
  );
};

/** terminal prompt: mono typewriter + block cursor; `marks` words get a hot underline sweep when typed */
export const Prompt: React.FC<{ x?: number; y?: number; w?: number; text: string; at: number; cps?: number; marks?: string[]; until?: number }> = ({ x = 70, y = 700, w = 940, text, at, cps = 26, marks = [], until = 1e9 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at - 6 || f >= until) return null;
  const n = Math.max(0, Math.floor(((f - at) / fps) * cps));
  const shown = text.slice(0, n);
  const box = interpolate(f - at, [-6, 6], [0, 1], cl);
  const tokens = shown.split(/(\s+)/);
  let pos = 0;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, border: `2px solid ${BP.line}`, background: "rgba(12,16,40,0.75)", padding: "26px 30px", opacity: box, transform: `scaleY(${0.6 + 0.4 * box})`, transformOrigin: "50% 0%" }}>
      <Micro x={0} y={-30} o={0.5}>PROMPT · TO CLAUDE</Micro>
      <div style={{ fontFamily: BP.mono, fontSize: 38, lineHeight: 1.45, color: BP.text }}>
        <span style={{ color: BP.hot }}>› </span>
        {tokens.map((tk, i) => {
          const start = pos; pos += tk.length;
          const isMark = marks.some((m) => tk.toLowerCase().includes(m.toLowerCase()));
          const done = start + tk.length <= n;
          return <span key={i} style={{ color: isMark ? BP.hot : BP.text, borderBottom: isMark && done ? `3px solid ${BP.hot}` : "none", textShadow: isMark ? glow(`${BP.hot}66`, 8) : "none" }}>{tk}</span>;
        })}
        <span style={{ display: "inline-block", width: 20, height: 40, marginLeft: 4, verticalAlign: "middle", background: BP.hot, opacity: Math.floor(f / 8) % 2 ? 1 : 0.2 }} />
      </div>
    </div>
  );
};

/** wireframe cube that line-draws and rotates */
export const WireCube: React.FC<{ cx: number; cy: number; size?: number; at: number; hot?: boolean }> = ({ cx, cy, size = 160, at, hot }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const t = (f - at) / 30, q = interpolate(f - at, [0, 18], [0, 1], cl);
  const r = (p: number[]) => { const [x, y, z] = p; const a = t * 0.8, b = 0.5 + t * 0.4;
    const x1 = x * Math.cos(a) - z * Math.sin(a), z1 = x * Math.sin(a) + z * Math.cos(a); const y1 = y * Math.cos(b) - z1 * Math.sin(b);
    return [cx + x1 * size / 2, cy + y1 * size / 2]; };
  const V = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]].map(r);
  const E = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, filter: hot ? `drop-shadow(0 0 8px ${BP.hot})` : "none" }}>
      {E.map(([a, b], i) => { const L = Math.hypot(V[b][0] - V[a][0], V[b][1] - V[a][1]); const qi = interpolate(q * E.length - i, [0, 1], [0, 1], cl);
        return <line key={i} x1={V[a][0]} y1={V[a][1]} x2={V[b][0]} y2={V[b][1]} stroke={hot ? BP.hot : BP.line} strokeWidth={2} strokeDasharray={L} strokeDashoffset={L * (1 - qi)} />; })}
    </svg>
  );
};

/** full-screen orange slam, one word per beat, hard cuts */
export const Slam: React.FC<{ words: { t: string; at: number }[]; until: number }> = ({ words, until }) => {
  const f = useCurrentFrame();
  if (f < words[0].at || f >= until) return null;
  const cur = [...words].reverse().find((w) => f >= w.at)!;
  const k = f - cur.at;
  return (
    <AbsoluteFill style={{ background: "#FF6B35", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: "'Archivo Black', Inter", fontWeight: 900, fontSize: cur.t.length > 8 ? 150 : 230, color: "#141428", letterSpacing: "-0.03em", transform: `scale(${interpolate(k, [0, 2, 6], [1.18, 1.02, 1], cl)})` }}>{cur.t}</div>
      <Micro x={900} y={1840} o={0.55} color="#141428">{(f / 30).toFixed(2)}</Micro>
    </AbsoluteFill>
  );
};

/** giant two-line finale with heavy bloom: line 1 white, line 2 hot */
export const Finale: React.FC<{ a: string; b: string; at: number; until: number; y?: number }> = ({ a, b, at, until, y = 700 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at || f >= until) return null;
  const p = spring({ frame: f - at, fps, config: { damping: 14, stiffness: 160 } }), p2 = spring({ frame: f - at - 6, fps, config: { damping: 14, stiffness: 160 } });
  const line = (t: string, c: string, pp: number) => (
    <div style={{ fontFamily: "'Archivo Black', Inter", fontSize: Math.min(190, Math.floor(1220 / Math.max(a.length, b.length))), whiteSpace: "nowrap", lineHeight: 0.95, color: c, letterSpacing: "-0.03em", textShadow: glow(`${c}99`, 30), opacity: pp, transform: `scale(${1.25 - 0.25 * pp})`, filter: `blur(${(1 - pp) * 12}px)` }}>{t}</div>
  );
  return <div style={{ position: "absolute", top: y, left: 0, right: 0, textAlign: "center" }}>{line(a, BP.text, p)}{line(b, BP.hot, p2)}</div>;
};

/** light paper form scene element: header bar + mono process boxes + hand-drawn hot strike + stamp */
export const Form: React.FC<{ title: string; sub: string; at: number; steps: { t: string; at: number }[]; strikeAt?: number; stamp?: { t: string; at: number }; y?: number }> = ({ title, sub, at, steps, strikeAt, stamp, y = 520 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at) return null;
  const hb = interpolate(f - at, [0, 10], [0, 1], cl);
  const sq = strikeAt !== undefined ? interpolate(f - strikeAt, [0, 10], [0, 1], cl) : 0;
  const sp = stamp ? spring({ frame: f - stamp.at, fps, config: { damping: 10, stiffness: 220 } }) : 0;
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: y }}>
      <div style={{ background: "#2a2a30", color: "#f4f2ec", padding: "22px 30px", display: "flex", alignItems: "center", gap: 26, transform: `scaleX(${hb})`, transformOrigin: "0 50%" }}>
        <span style={{ fontFamily: "'Archivo Black', Inter", fontSize: 56 }}>{title}</span>
        <span style={{ fontFamily: BP.mono, fontSize: 16, letterSpacing: "0.12em", opacity: 0.8 }}>{sub}</span>
      </div>
      <div style={{ position: "relative", display: "flex", flexWrap: "wrap", gap: 18, alignItems: "center", marginTop: 60 }}>
        {steps.map((s, i) => f >= s.at && (
          <React.Fragment key={i}>
            {i > 0 && <span style={{ fontFamily: BP.mono, color: BP.hot, fontSize: 52 }}>→</span>}
            <div style={{ border: "3px solid #9a9890", padding: "26px 36px", fontFamily: BP.mono, fontSize: 52, color: "#55534c", background: "#f6f5f0" }}>{s.t}</div>
          </React.Fragment>
        ))}
        {sq > 0 && <svg width={960} height={120} style={{ position: "absolute", left: -10, top: -10, overflow: "visible" }}>
          <path d="M-10,70 C220,58 480,82 980,64" stroke={BP.hot} strokeWidth={12} fill="none" strokeLinecap="round" strokeDasharray={1000} strokeDashoffset={1000 * (1 - sq)} />
        </svg>}
      </div>
      {stamp && f >= stamp.at && <div style={{ marginTop: 70, marginLeft: 260, display: "inline-block", border: `5px solid ${BP.hot}`, color: BP.hot, fontFamily: "'Archivo Black', Inter", fontSize: 110, padding: "14px 40px", whiteSpace: "nowrap",
        transform: `rotate(-6deg) scale(${interpolate(sp, [0, 1], [2.2, 1])})`, opacity: Math.min(1, sp * 1.5) }}>{stamp.t}</div>}
    </div>
  );
};
