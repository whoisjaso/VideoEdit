import React from 'react';
import {spring} from 'remotion';
import {CUES, Cap, SHOT} from './data';
import {C, EASE, FONT, FPS, W, ZONE} from './theme';
import {clamp, measure, prog, useT} from './lib';
import {COL, Shape} from './Shapes';

// captions ride the illustrated scenes; cards and title cards carry their own type (reference behaviour)
export const CARD_SHOTS = new Set(['title', 'danger', 'bias', 'rule', 'admit', 'black']);
export const shotAt = (t: number) => Object.values(SHOT).find((s) => t >= s.start && t < s.end)?.id ?? 'end';
const capsOn = (c: Cap) => !CARD_SHOTS.has(c.shot) && !(c.shot === 'end' && c.s >= endCardT());
const endCardT = () => CUES.events.find((e) => e.name === 'part2')!.t;

const SIZE = 64;
const GAP = SIZE * 0.26;
type Laid = {size: number; pos: {x: number; y: number; w: number}[]};

const layout = (cap: Cap): Laid => {
  let size = SIZE;
  const maxW = W - 2 * ZONE.margin - 80;
  const widths = () => cap.words.map((w) => measure(w.w, size, 'Inter800', -0.01));
  let ws = widths();
  while (ws.reduce((a, b) => a + b, 0) + GAP * (ws.length - 1) > maxW && size > 40) {
    size -= 4;
    ws = widths();
  }
  const gap = size * 0.26;
  const total = ws.reduce((a, b) => a + b, 0) + gap * (ws.length - 1);
  let x = (W - total) / 2;
  const y = ZONE.captions[0];
  const pos = ws.map((w) => {
    const p = {x, y, w};
    x += w + gap;
    return p;
  });
  return {size, pos};
};
const cache = new Map<Cap, Laid>();
const laid = (c: Cap) => {
  if (!cache.has(c)) cache.set(c, layout(c));
  return cache.get(c)!;
};
const CAPS = () => CUES.captions.filter(capsOn);

// ---------------------------------------------------------------- the reading ball

type P = {t: number; x: number; y: number};
let LAND: P[] | null = null;
const landings = () => {
  if (LAND) return LAND;
  LAND = [];
  for (const c of CAPS()) {
    const L = laid(c);
    c.words.forEach((w, i) => LAND!.push({t: w.s, x: L.pos[i].x + L.pos[i].w / 2, y: L.pos[i].y - 10}));
  }
  return LAND;
};

const readAt = (t: number) => {
  const P = landings();
  if (t <= P[0].t) return {x: P[0].x, y: P[0].y, sq: 0};
  for (let i = 0; i < P.length - 1; i++) {
    const a = P[i], b = P[i + 1];
    if (t < b.t) {
      const hop = Math.min(0.26, Math.max(0.1, (b.t - a.t) * 0.8));
      const t0 = b.t - hop;
      const since = t - a.t;
      const sq = since < 0.1 ? Math.sin((since / 0.1) * Math.PI) : 0;
      if (t < t0) return {x: a.x, y: a.y, sq};
      const u = (t - t0) / hop;
      const e = u * u * (3 - 2 * u);
      const arc = (26 + Math.hypot(b.x - a.x, b.y - a.y) * 0.12) * 4 * u * (1 - u);
      return {x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e - arc, sq: 0};
    }
  }
  const z = P[P.length - 1];
  return {x: z.x, y: z.y, sq: 0};
};

const FLY = 0.4;
const BACK = 0.42;
type Morph = {shape: string; t0: number; t1: number; color: string; x: number; y: number; size: number};
const MORPHS = () => (CUES as unknown as {morphs: Morph[]}).morphs;
const arcTo = (a: {x: number; y: number}, b: {x: number; y: number}, u: number, lift: number) => {
  const e = EASE.inOut(clamp(u));
  const h = (lift + Math.hypot(b.x - a.x, b.y - a.y) * 0.2) * 4 * e * (1 - e);
  return {x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e - h};
};

export const ballAt = (t: number) => {
  for (const m of MORPHS()) {
    if (t >= m.t0 && t < m.t1 + BACK) {
      const home = readAt(m.t0);
      if (t < m.t0 + FLY) return {...arcTo(home, m, (t - m.t0) / FLY, 140), sq: 0, m, phase: 'fly' as const, k: 0};
      if (t < m.t1) return {x: m.x, y: m.y, sq: 0, m, phase: 'hold' as const,
        k: spring({frame: (t - m.t0 - FLY) * FPS, fps: FPS, config: {damping: 14, stiffness: 190, mass: 0.7}})};
      const u = (t - m.t1) / BACK;
      return {...arcTo(m, readAt(t), u, 110), sq: 0, m, phase: 'back' as const, k: 1 - clamp(u / 0.35)};
    }
  }
  return {...readAt(t), m: null as Morph | null, phase: 'read' as const, k: 0};
};

export const Ball: React.FC = () => {
  const t = useT();
  const cur = CAPS().find((c) => t >= c.s - 0.1 && t < c.out);
  const b = ballAt(t);
  const vis = b.m ? 1 : cur ? clamp((t - (cur.s - 0.12)) / 0.12) * (1 - prog(t, cur.out - 0.15, cur.out, EASE.in)) : 0;
  if (vis <= 0.01) return null;
  const R = 9;
  const showBall = b.phase !== 'hold' || b.k < 0.05;
  const m = b.m;
  const u = m ? t - (m.t0 + FLY) : 0;
  const draw = m ? (b.phase === 'hold' ? clamp(u / 0.4) : b.k) : 0;
  const isDot = m?.shape === 'dot';
  return (
    <svg width={W} height={1920} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
      {showBall && Array.from({length: 22}, (_, k) => {
        const q = ballAt(t - (k + 1) * 0.005);
        return <circle key={k} cx={q.x} cy={q.y - R - 4} r={R * (1 - k / 26)} fill="#fff" opacity={vis * 0.12 * (1 - k / 22)} />;
      })}
      {showBall && !(isDot && b.phase === 'hold') && (
        <ellipse cx={b.x} cy={b.y - R * (1 - b.sq * 0.25) - 4} rx={R * (1 + b.sq * 0.3)} ry={R * (1 - b.sq * 0.25)} fill="#fff" opacity={vis}
          style={{filter: 'drop-shadow(0 0 6px rgba(255,255,255,0.6)) drop-shadow(0 2px 3px rgba(0,0,0,0.5))'}} />
      )}
      {m && isDot && b.phase !== 'fly' && (
        <circle cx={m.x} cy={m.y} r={13} fill={C.pink} opacity={b.phase === 'back' ? b.k : 1} style={{filter: 'drop-shadow(0 0 10px rgba(232,69,139,0.9))'}} />
      )}
      {m && !isDot && (b.phase === 'hold' || b.phase === 'back') && b.k > 0.01 && (
        <g transform={`translate(${m.x} ${m.y}) scale(${(m.size / 200) * (0.35 + 0.65 * b.k)})`}>
          <circle r={120} fill={COL[m.color] ?? '#fff'} opacity={0.12 * b.k} style={{filter: 'blur(30px)'}} />
          <Shape shape={m.shape} color={COL[m.color] ?? '#fff'} d={draw} u={u} night />
        </g>
      )}
    </svg>
  );
};

// ---------------------------------------------------------------- captions (reference: whole chunk up, unspoken grey -> spoken white)

export const Captions: React.FC = () => {
  const t = useT();
  const cur = CAPS().find((c) => t >= c.s - 0.1 && t < c.out);
  if (!cur) return null;
  const L = laid(cur);
  const inP = prog(t, cur.s - 0.1, cur.s + 0.06, EASE.out);
  const exit = prog(t, cur.out - 0.15, cur.out, EASE.in);
  const officer = cur.speaker === 'O';
  return (
    <div style={{position: 'absolute', inset: 0, pointerEvents: 'none', opacity: inP * (1 - exit),
      transform: `translateY(${(1 - inP) * 14 - exit * 10}px)`}}>
      {officer && (
        <div style={{position: 'absolute', left: 0, right: 0, top: L.pos[0].y - 64, textAlign: 'center', fontFamily: FONT.mono, fontWeight: 700,
          fontSize: 24, letterSpacing: 4, color: C.pink}}>OFFICER</div>
      )}
      {cur.words.map((w, i) => {
        const said = clamp((t - w.s + 0.02) / 0.12);
        return (
          <div key={i} style={{position: 'absolute', left: L.pos[i].x, top: L.pos[i].y, whiteSpace: 'nowrap', fontFamily: FONT.sans, fontWeight: 800,
            fontSize: L.size, letterSpacing: '-0.01em', lineHeight: 1,
            color: said >= 1 ? '#fff' : `rgba(255,255,255,${0.42 + 0.58 * said})`,
            textShadow: '0 2px 14px rgba(0,0,0,0.75), 0 1px 2px rgba(0,0,0,0.8)'}}>{w.w}</div>
        );
      })}
    </div>
  );
};
