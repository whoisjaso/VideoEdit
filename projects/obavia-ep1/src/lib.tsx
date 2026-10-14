import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, random} from 'remotion';
import {C, EASE, FONT, FPS, SPRING, W, ZONE} from './theme';
export {C};

export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;

/** eased 0..1 over [t0, t1] seconds */
export const prog = (t: number, t0: number, t1: number, ease = EASE.out) =>
  interpolate(t, [t0, t1], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/** spring 0..1 starting at time t0 (seconds) */
export const sp = (t: number, t0: number, cfg = SPRING.pop) =>
  t < t0 ? 0 : spring({frame: (t - t0) * FPS, fps: FPS, config: cfg});

/** visible window with fade-in / fade-out (fade-out ends exactly at t1) */
export const win = (t: number, t0: number, t1: number, fin = 0.25, fout = 0.17) =>
  t < t0 || t > t1 ? 0 : Math.min(prog(t, t0, t0 + fin), 1 - prog(t, t1 - fout, t1, EASE.in));

export const useT = () => useCurrentFrame() / FPS;

// ---------------------------------------------------------------- directional motion blur (SVG filter)

let blurId = 0;
/** Wraps children in a directional Gaussian blur (dx, dy in px). Zero blur renders plain. */
export const MBlur: React.FC<{dx?: number; dy?: number; style?: React.CSSProperties; children: React.ReactNode}> = ({
  dx = 0, dy = 0, style, children,
}) => {
  const id = React.useMemo(() => `mb${blurId++}`, []);
  const on = Math.abs(dx) > 0.3 || Math.abs(dy) > 0.3;
  return (
    <>
      {on && (
        <svg width={0} height={0} style={{position: 'absolute'}}>
          <filter id={id} x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation={`${Math.abs(dx).toFixed(2)} ${Math.abs(dy).toFixed(2)}`} />
          </filter>
        </svg>
      )}
      <div style={{...style, filter: on ? `url(#${id})` : undefined}}>{children}</div>
    </>
  );
};

// ---------------------------------------------------------------- texture layers

export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.06}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'overlay', opacity}}>
      <svg width="100%" height="100%">
        <filter id="grainf">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={f % 97} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grainf)" />
      </svg>
    </AbsoluteFill>
  );
};

export const Vignette: React.FC<{strength?: number; color?: string}> = ({strength = 0.65, color = '0,0,0'}) => (
  <AbsoluteFill
    style={{pointerEvents: 'none', background: `radial-gradient(ellipse 75% 62% at 50% 46%, rgba(${color},0) 55%, rgba(${color},${strength}) 100%)`}}
  />
);

export const Scanlines: React.FC = () => (
  <AbsoluteFill
    style={{pointerEvents: 'none', opacity: 0.05,
      backgroundImage: 'repeating-linear-gradient(0deg, #000 0px, #000 1px, transparent 1px, transparent 4px)'}}
  />
);

// ---------------------------------------------------------------- text measurement (canvas, fonts are loaded first)

import fontW from './data/font-widths.json';
const FW = fontW as Record<string, Record<string, number>>;
/** text width from the font's own advance widths (no DOM: deterministic in every render tab).
 *  family: 'Inter800' | 'Inter900' | 'SerifItalic' | 'Anton' | 'mono' */
export const measure = (text: string, size: number, family = 'Inter800', tracking = 0) => {
  if (family === 'mono') return text.length * 0.6 * size;
  const tbl = FW[family] ?? FW.Inter800;
  let w = 0;
  for (const ch of text) w += tbl[ch] ?? 0.55;
  return w * size + tracking * size * Math.max(0, text.length - 1);
};

/** spec auto-fit: size = min(max, width*lines/(chars*0.52), width/(longestWord*0.56)) */
export const fitSize = (text: string, max: number, width: number, lines: number) => {
  const chars = text.length;
  const longest = Math.max(...text.split(/\s+/).map((w) => w.length));
  return Math.min(max, (width * lines) / (chars * 0.52), width / (longest * 0.56));
};

