// Kenyset text pack (r29) for Remotion: 41 kinetic text reveals decoded from @kenyset's After Effects presets.
// Same math as jason-ad-film/kit/textfx.js (pure function of the frame). Pick presets by ROLE (see KENYSET_ROLES) and rotate so the whole pack gets used.
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import PRESETS from "./kenyset-presets.json";

export type KPreset = { n: number; unit: "char" | "word" | "line"; bounce: "char" | "word" | "line" | null; x: number; y: number; sx: number; sy: number;
  rot: number; op: number; blur: number; track: number; easeHi: number; easeLo: number; shape: "ramp" | "square" };
export const KENYSET = PRESETS as KPreset[];
export const kp = (n: number) => KENYSET.find((p) => p.n === n) as KPreset;

// which presets fit which moment (Jason: "we need all this and need to utilize it too")
export const KENYSET_ROLES: Record<string, number[]> = {
  hook: [1, 2, 3, 35, 36, 37, 13, 14],          // stretch-flip pops, blur-zoom from 150%, fall-in: the first 2 s
  reveal: [11, 12, 17, 20, 21, 18, 19],          // drop/spin and spin-up: twists, "here's the thing", surprises
  money: [22, 23, 24, 28, 29],                   // scale pops: numbers, prices, wins
  list: [38, 39, 40, 41, 42],                    // typewriters / tracking: steps, lists, quotes, on-screen "typing"
  move: [4, 5, 6, 7, 8, 9, 10],                  // slides: section changes, before -> after, comparisons
  calm: [25, 26, 27, 30, 31, 32, 33, 34],        // soft rise + blur: reflective lines, sleep films, CTAs
};
// rotate within a role: the k-th time a role fires in a video, use the next preset in its list
export const pickKenyset = (role: keyof typeof KENYSET_ROLES, k: number) => kp(KENYSET_ROLES[role][k % KENYSET_ROLES[role].length]);

const bez = (x1: number, y1: number, x2: number, y2: number) => {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const X = (t: number) => ((ax * t + bx) * t + cx) * t, Y = (t: number) => ((ay * t + by) * t + cy) * t, dX = (t: number) => (3 * ax * t + 2 * bx) * t + cx;
  return (x: number) => { if (x <= 0) return 0; if (x >= 1) return 1; let t = x; for (let i = 0; i < 8; i++) { const d = dX(t); if (Math.abs(d) < 1e-6) break; t -= (X(t) - x) / d; } return Y(Math.min(1, Math.max(0, t))); };
};
const EASE: Record<string, (x: number) => number> = { "50,100": bez(0.4, 0, 0.1, 1), "-100,100": bez(0.08, 0.75, 0.1, 1), "-50,100": bez(0.2, 0.5, 0.1, 1), "0,50": bez(0.33, 0, 0.3, 1), "0,0": (x) => x };
const STAGGER = { char: 0.035, word: 0.09, line: 0.2 }, DUR = { char: 0.55, word: 0.6, line: 0.75 };
const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const spring = (tau: number) => (tau < 0 ? 1 : clamp(1.5 * Math.cos(2 * Math.PI * 2.5 * tau) * Math.exp(-7 * tau), -1, 1));

export const KenysetText: React.FC<{ text: string; preset: KPreset; at: number; size?: number; color?: string; style?: React.CSSProperties; accent?: Record<string, string> }> =
  ({ text, preset: p, at, size = 96, color = "#F4F1EA", style, accent = {} }) => {
  const f = useCurrentFrame(), { fps } = useVideoConfig(), t = (f - at) / fps, k = size / 100;
  const ease = EASE[`${p.easeHi},${p.easeLo}`] || EASE["50,100"];
  // unit indices for every char (char / word / line) so any unit type can drive it
  const lines = text.split("\n"); let ci = 0, wi = 0;
  const st = STAGGER[p.unit], dur = DUR[p.unit];
  const weights = (idx: number, bidx: number | null) => {
    if (p.shape === "square") { const w = t < idx * 0.045 ? 1 : 0; return [w, w]; }
    const w = 1 - ease(clamp((t - idx * st) / dur));
    const wt = p.bounce != null && bidx != null ? (t - idx * st < 0 ? 1 : spring(t - idx * st)) : w;
    return [w, wt];
  };
  const tf = (w: number, wt: number): React.CSSProperties => ({ display: "inline-block",
    transform: `translate(${p.x * k * wt}px, ${p.y * k * wt}px) rotate(${p.rot * wt}deg) scale(${1 + (p.sx / 100 - 1) * wt}, ${1 + (p.sy / 100 - 1) * wt})`,
    opacity: 1 + (p.op / 100 - 1) * w, filter: p.blur ? `blur(${p.blur * k * 0.5 * w}px)` : undefined, marginRight: p.track ? `${(p.track / 1000) * w}em` : undefined });
  return (
    <div style={{ fontSize: size, color, lineHeight: 1.12, textAlign: "center", whiteSpace: "nowrap", ...style }}>
      {lines.map((ln, li) => {
        const [lw, lwt] = p.unit === "line" ? weights(li, li) : [0, 0];
        return (
          <div key={li} style={p.unit === "line" ? tf(lw, lwt) : { display: "block" }}>
            {ln.split(" ").map((word, wj) => {
              const myW = wi++; const [ww, wwt] = p.unit === "word" ? weights(myW, myW) : [0, 0];
              const col = accent[word.toLowerCase().replace(/[^a-z0-9']/g, "")];
              return (
                <span key={wj} style={{ ...(p.unit === "word" ? tf(ww, wwt) : { display: "inline-block" }), marginRight: "0.26em", color: col || undefined }}>
                  {[...word].map((c, cj) => { const myC = ci++; const [cw, cwt] = p.unit === "char" ? weights(myC, myC) : [0, 0];
                    return <span key={cj} style={p.unit === "char" ? tf(cw, cwt) : { display: "inline-block" }}>{c}</span>; })}
                </span>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};
