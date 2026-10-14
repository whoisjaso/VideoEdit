import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {CUES, SHOT, cue, keys, wordT} from './data';
import {C, EASE, FONT, FPS, SIDE, SPRING, W, H} from './theme';
import {MBlur, clamp, lerp, prog, sp, win} from './lib';

const F5 = 5 / FPS;

// ================================================================ illustrated scene (Ken Burns: slow push + drift)

const Art: React.FC<{src: string; t: number; t0: number; t1: number; from?: number; to?: number; ox?: number; oy?: number; dx?: number; crop?: number}> = ({
  src, t, t0, t1, from = 1.02, to = 1.1, ox = 50, oy = 45, dx = 0, crop = 1,
}) => {
  const u = prog(t, t0, t1, EASE.sine);
  const s = lerp(from, to, u);
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
      <Img src={staticFile(`scenes/${src}.jpg`)} style={{position: 'absolute', left: 0, top: 0, width: W, height: H * crop,
        objectFit: 'cover', objectPosition: `${ox}% ${oy}%`, transform: `scale(${s}) translateX(${dx * u}px)`, transformOrigin: `${ox}% ${oy}%`}} />
      {/* lower shade so captions always read */}
      <AbsoluteFill style={{background: 'linear-gradient(rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.62) 82%, rgba(0,0,0,0.75) 100%)'}} />
    </AbsoluteFill>
  );
};

// reference-style pink section pill under the HUD
const Pill: React.FC<{text: string; t: number; t0: number; t1: number; color: string; ink?: string}> = ({text, t, t0, t1, color, ink = '#fff'}) => {
  const a = win(t, t0, t1, 0.15, 0.12);
  if (a <= 0) return null;
  return (
    <div style={{position: 'absolute', left: 60, top: 222, opacity: a, transform: `translateX(${(1 - a) * -20}px)`, padding: '8px 16px', borderRadius: 8,
      background: color, fontFamily: FONT.mono, fontWeight: 700, fontSize: 22, letterSpacing: 3, color: ink, boxShadow: `0 0 24px ${color}66`}}>{text}</div>
  );
};

/** a label the other person puts on you: pink pill + mono sub-line + a ring on the thing (reference "BAIT MONEY") */
const Label: React.FC<{text: string; sub?: string; x: number; y: number; t: number; t0: number; t1: number; ring?: [number, number, number]; color: string}> = ({
  text, sub, x, y, t, t0, t1, ring, color,
}) => {
  if (t < t0 - 0.02 || t > t1) return null;
  const p = sp(t, t0, SPRING.pop);
  const out = 1 - prog(t, t1 - 0.15, t1, EASE.in);
  const r = ring ? prog(t, t0, t0 + 0.35, EASE.out) : 0;
  return (
    <>
      {ring && (
        <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, opacity: out}}>
          <circle cx={ring[0]} cy={ring[1]} r={ring[2]} fill="none" stroke={color} strokeWidth={6} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - r}
            transform={`rotate(-90 ${ring[0]} ${ring[1]})`} />
        </svg>
      )}
      <div style={{position: 'absolute', left: x, top: y, opacity: clamp(p * 2) * out, transform: `scale(${0.7 + 0.3 * p})`, transformOrigin: '0 50%'}}>
        <div style={{display: 'inline-block', background: color, padding: '10px 18px 8px', borderRadius: 8, fontFamily: FONT.sans, fontWeight: 900,
          fontSize: 40, color: color === '#fff' ? '#111' : '#fff', letterSpacing: '-0.01em', boxShadow: `0 8px 24px rgba(0,0,0,0.35), 0 0 30px ${color === '#fff' ? 'rgba(0,0,0,0)' : color + '55'}`}}>{text}</div>
        {sub && <div style={{marginTop: 6, display: 'inline-block', background: 'rgba(0,0,0,0.6)', padding: '4px 10px', borderRadius: 6, fontFamily: FONT.mono,
          fontSize: 18, letterSpacing: 2, color: '#fff'}}>{sub}</div>}
      </div>
    </>
  );
};

// ================================================================ cards

type Tone = 'him' | 'you' | 'fix' | 'neutral';
const TONE: Record<Tone, {deep: string; mid: string; accent: string}> = {
  him: {deep: SIDE.himDeep, mid: SIDE.himMid, accent: SIDE.him},
  you: {deep: SIDE.youDeep, mid: SIDE.youMid, accent: SIDE.you},
  fix: {deep: '#03140F', mid: '#073326', accent: SIDE.fix},
  neutral: {deep: '#0C0C10', mid: '#1C1C24', accent: '#fff'},
};
/** explainer card, tinted by whose side it is on: deep gradient, a breathing accent glow, mono header with a colour tick */
const Card: React.FC<{header: string; tone: Tone; t: number; t0: number; foot?: string; children: React.ReactNode}> = ({header, tone, t, t0, foot, children}) => {
  return (
    // clean black stage: the only colour on a card is the word that means it (no headers, no footnotes)
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 90% 60% at 50% 42%, #17171C 0%, #08080A 75%)'}}>
      {children}
    </AbsoluteFill>
  );
};
/** red (fear) -> white (disarmed), u = 1 is full red */
const mixRed = (u: number) => `rgb(255, ${Math.round(255 - 196 * u)}, ${Math.round(255 - 177 * u)})`;
const glowText = (c: string): React.CSSProperties => ({color: c, textShadow: `0 0 34px ${c}66`});
/** gradient type for the two-sides words (amber you -> blue him) */
/** the light bar on a word: red/blue glow alternating, the stop that isn't over */
const siren = (t: number): React.CSSProperties => {
  const k = Math.sin(t * Math.PI * 2 * 1.4) > 0;
  return {color: '#fff', textShadow: `0 0 36px ${k ? SIDE.stakes : SIDE.him}, 0 0 80px ${k ? SIDE.stakesGlow : SIDE.himGlow}`};
};
const twoTone: React.CSSProperties = {background: `linear-gradient(90deg, ${SIDE.you} 0%, #FF7A8A 50%, ${SIDE.him} 100%)`, WebkitBackgroundClip: 'text',
  backgroundClip: 'text', color: 'transparent'};

/** a block of card type that arrives (rise + blur) and leaves over the 5 frames before the next */
const In: React.FC<{t: number; t0: number; t1?: number; y: number; children: React.ReactNode; style?: React.CSSProperties}> = ({t, t0, t1 = 1e9, y, children, style}) => {
  const a = win(t, t0, t1, 0.22, F5);
  if (a <= 0) return null;
  const p = prog(t, t0, t0 + 0.35, EASE.out);
  return <div style={{position: 'absolute', left: 70, right: 70, top: y, textAlign: 'center', opacity: a, transform: `translateY(${(1 - p) * 26}px)`,
    filter: `blur(${(1 - p) * 8}px)`, ...style}}>{children}</div>;
};

const big = (size: number, color: string = '#fff'): React.CSSProperties => ({fontFamily: FONT.sans, fontWeight: 900, fontSize: size, lineHeight: 1.04,
  letterSpacing: '-0.03em', color});

const Stamp: React.FC<{t: number; t0: number; text: string; y: number; rot?: number; color: string}> = ({t, t0, text, y, rot = -5, color}) => {
  if (t < t0) return null;
  const u = t - t0;
  const s = 1 + 0.5 * Math.max(0, 1 - u / 0.1) ** 2;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center'}}>
      <div style={{transform: `rotate(${rot}deg) scale(${s})`, opacity: clamp(u / 0.05), border: `5px solid ${color}`, borderRadius: 10,
        padding: '6px 22px', fontFamily: FONT.sans, fontWeight: 900, fontSize: 46, letterSpacing: 2, color, boxShadow: `0 0 30px ${color === '#fff' ? 'rgba(0,0,0,0)' : color + '55'}`}}>{text}</div>
    </div>
  );
};

/** rolling count-up with blurred digits while they spin (reference) */
const Count: React.FC<{t: number; t0: number; dur: number; to: number; size: number; color?: string; prefix?: string}> = ({t, t0, dur, to, size, color = '#fff', prefix = ''}) => {
  const u = prog(t, t0, t0 + dur, EASE.out);
  const v = Math.round(to * u);
  const spinning = u < 1;
  return <span style={{...big(size, color), filter: spinning ? 'blur(1.2px)' : undefined}}>{prefix}{v.toLocaleString('en-US')}</span>;
};

// ================================================================ scenes

export const Hook: React.FC<{t: number}> = ({t}) => <Art src="hook" t={t} t0={0} t1={SHOT.hook.end} from={1.1} to={1.0} oy={40} />;

export const Title: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.title;
  const words = ['TWO', 'SCARED', 'PEOPLE'];
  return (
    <AbsoluteFill>
      <Art src="hispov" t={t} t0={s.start} t1={s.end} from={1.15} to={1.22} oy={40} />
      <AbsoluteFill style={{background: 'rgba(12,8,10,0.55)'}} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 700, textAlign: 'center'}}>
        {words.map((w, i) => {
          const p = sp(t, s.start + 0.08 + i * 0.12, SPRING.pop);
          const sh = w === 'SCARED' ? Math.sin(t * 61) * 3 + Math.sin(t * 37) * 2 : 0;   // the word trembles
          return <div key={w} style={{...big(170, '#fff'), ...(w === 'SCARED' ? glowText(SIDE.stakes) : {}), lineHeight: 0.95, opacity: clamp(p * 1.5),
            transform: `translate(${sh}px, ${(1 - p) * 40}px) scale(${0.9 + 0.1 * p})`, filter: `blur(${(1 - clamp(p)) * 10}px)`}}>{w}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

export const P1: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill>
    <Art src="cruiser" t={t} t0={SHOT.p1.start} t1={SHOT.p1.end} from={1.04} to={1.12} oy={35} />
  </AbsoluteFill>
);

export const HisPov: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.hispov;
  const [a, b, c, d] = [cue('tagH1'), cue('tagH2'), cue('tagH3'), cue('tagH4')];
  return (
    <AbsoluteFill>
      <Art src="hispov" t={t} t0={s.start} t1={s.end} from={1.0} to={1.12} oy={42} />
      <Label color="#fff" text="PAPER TAGS?" x={560} y={850} t={t} t0={a} t1={s.end} ring={[645, 690, 90]} />
      <Label color="#fff" text="LOUD MUSIC" x={70} y={470} t={t} t0={b} t1={s.end} />
      <Label color="#fff" text="TANK TOP" x={600} y={330} t={t} t0={c} t1={s.end} ring={[535, 560, 70]} />
      <Label color={SIDE.stakes} text="DANGER?" x={90} y={1000} t={t} t0={d} t1={s.end} />
    </AbsoluteFill>
  );
};

/** where the reading ball lands and becomes the grid (Reading.tsx morph "seed" uses the same point) */
export const GRID = {x: 540, y: 640, cols: 24, rows: 20, cw: 34, ch: 22};

export const Danger: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.danger;
  const B = cue('dangerB'), Cc = cue('dangerC'), dot = cue('dot');
  const {cols, rows, cw, ch} = GRID;
  const gw = cols * cw, gh = rows * ch;
  const land = B + 0.4;                                    // ball arrives -> grid ripples out from it
  const R = prog(t, land, dot, EASE.out) * 1.05;
  const hero = Math.floor(rows / 2) * cols + Math.floor(cols / 2);
  const isolate = prog(t, dot, dot + 0.35, EASE.out);       // "one": everything else dims, one cell goes red
  const pulse = 0.5 + 0.5 * Math.sin((t - dot) * Math.PI * 3);
  return (
    <Card header="PROBLEM 1 · HIS SIDE" tone="him" t={t} t0={s.start} foot="Woods (2019), Michigan Law Review 117(4) · 10 yrs, 200+ Florida agencies">
      <In t={t} t0={s.start + 0.1} t1={B - F5} y={620}>
        <div style={big(54, 'rgba(255,255,255,0.7)')}>His training says</div>
        <div style={{...big(118), marginTop: 18}}>any stop could<br /><span style={glowText(SIDE.stakes)}>turn deadly.</span></div>
      </In>
      {t >= B && t < Cc && (
        <div style={{position: 'absolute', left: GRID.x - gw / 2, top: GRID.y - gh / 2, opacity: 1 - prog(t, Cc - F5, Cc)}}>
          <svg width={gw} height={gh} style={{overflow: 'visible'}}>
            {Array.from({length: cols * rows}, (_, i) => {
              const cx = (i % cols) * cw + cw / 2, cy = Math.floor(i / cols) * ch + ch / 2;
              const d = Math.hypot((cx - gw / 2) / (gw / 2), (cy - gh / 2) / (gh / 2)) / Math.SQRT2;
              const on = clamp((R - d) / 0.06);
              const me = i === hero;
              const col = me && isolate > 0 ? SIDE.stakes : '#fff';
              const op = me ? 1 : on * (0.85 - 0.7 * isolate);
              const sc = me ? 1 + isolate * (0.6 + 0.25 * pulse) : 0.4 + 0.6 * on;
              return <rect key={i} x={cx - 13 * sc} y={cy - 7 * sc} width={26 * sc} height={14 * sc} rx={3} fill={col} opacity={me ? Math.max(on, isolate) : op}
                style={me && isolate > 0 ? {filter: `drop-shadow(0 0 ${10 + 8 * pulse}px ${SIDE.stakes})`} : undefined} />;
            })}
          </svg>
        </div>
      )}
      <In t={t} t0={land + 0.1} t1={Cc - F5} y={GRID.y + gh / 2 + 50}>
        <div style={big(76)}>1 in <Count t={t} t0={land} dur={dot - land} to={6500000} size={76} /></div>
        <div style={{...big(40, 'rgba(255,255,255,0.6)'), fontWeight: 700, marginTop: 16, letterSpacing: '-0.01em'}}>stops where an officer was <span style={glowText(SIDE.stakes)}>killed</span></div>
      </In>
      <In t={t} t0={Cc} t1={s.end + 0.1} y={700}><div style={big(120)}>But <span style={glowText(SIDE.stakes)}>fear</span> doesn't<br />read data.</div></In>
    </Card>
  );
};

export const P2: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.p2;
  const [a, b, c] = [cue('tagY1'), cue('tagY2'), cue('tagY3')];
  return (
    <AbsoluteFill>
      <Art src="mirror" t={t} t0={s.start} t1={s.end} from={1.0} to={1.1} ox={60} oy={40} />
      <Label color="#fff" text="POWER TRIP?" x={420} y={760} t={t} t0={a} t1={s.end} />
      <Label color="#fff" text="QUOTA?" x={560} y={380} t={t} t0={b} t1={s.end} />
      <Label color={SIDE.him} text="THE BADGE" x={430} y={980} t={t} t0={c} t1={s.end} ring={[630, 480, 60]} />
    </AbsoluteFill>
  );
};

export const Bias: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.bias;
  const B = cue('biasB');
  const st = cue('stamp_bias');
  return (
    <Card header="PROBLEM 2 · YOUR SIDE" tone="you" t={t} t0={s.start} foot="Correll, Park, Judd & Wittenbrink (2002), JPSP 83(6)">
      <In t={t} t0={s.start + 0.1} y={520}>
        <div style={big(48, 'rgba(255,255,255,0.7)')}>In a famous study,</div>
        <div style={{...big(96), marginTop: 18}}>split-second <span style={glowText(SIDE.stakes)}>threat</span> calls followed</div>
        <div style={{...big(104), marginTop: 6}}>cultural stereotypes.</div>
      </In>
      <In t={t} t0={B} y={1060}>
        <div style={{width: 6, height: 70 * prog(t, B, B + 0.3, EASE.out), background: 'rgba(255,255,255,0.5)', margin: '0 auto 22px', borderRadius: 3}} />
        <div style={big(64)}>Even in people with</div>
        <div style={big(64)}>no personal prejudice.</div>
      </In>
      <Stamp t={t} t0={st} text="STILL" y={1330} color={SIDE.stakes} />
    </Card>
  );
};

export const Slice: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill>
    <Art src="face" t={t} t0={SHOT.slice.start} t1={SHOT.slice.end} from={1.0} to={1.14} oy={38} />
    <AbsoluteFill style={{background: `rgba(255,255,255,${0.5 * Math.max(0, 1 - Math.abs(t - cue('tenth')) / 0.06)})`}} />
  </AbsoluteFill>
);

export const Rule: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.rule;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 90% 60% at 50% 42%, #17171C 0%, #08080A 75%)'}}>
      <In t={t} t0={s.start + 0.05} y={760}>
        <div style={big(56, 'rgba(255,255,255,0.55)')}>Rule one.</div>
        <div style={{...big(104, '#fff'), marginTop: 22}}>Disarm <span style={{color: mixRed(1 - prog(t, s.start + 0.55, s.start + 1.25, EASE.inOut)),
          textShadow: `0 0 ${34 * (1 - prog(t, s.start + 0.55, s.start + 1.25))}px ${SIDE.stakesGlow}`}}>the fear</span><br />before you speak.</div>
      </In>
    </AbsoluteFill>
  );
};

export const Disarm: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.disarm;
  const items = ['HAZARDS ON', 'DOME LIGHT ON', 'WINDOW DOWN', 'HANDS ON THE WHEEL'];
  const ts = [cue('toggle1'), cue('toggle2'), cue('toggle3'), cue('toggle4')];
  const ok = cue('letsee');
  return (
    <AbsoluteFill>
      <Art src="disarm" t={t} t0={s.start} t1={s.end} from={1.28} to={1.36} oy={22} crop={1} />
      <div style={{position: 'absolute', left: 60, top: 300}}>
        {items.map((it, i) => {
          if (t < ts[i] - 0.02) return null;
          const p = sp(t, ts[i], SPRING.pop);
          return (
            <div key={it} style={{display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16, opacity: clamp(p * 2), transform: `translateX(${(1 - p) * -30}px)`}}>
              <div style={{width: 44, height: 44, borderRadius: 22, background: '#fff', boxShadow: '0 4px 14px rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <svg width={26} height={26}><path d="M 5 14 L 11 20 L 22 7" fill="none" stroke="#03140F" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round"
                  pathLength={1} strokeDasharray={1} strokeDashoffset={1 - prog(t, ts[i] + 0.05, ts[i] + 0.3)} /></svg>
              </div>
              <div style={{background: 'rgba(0,0,0,0.62)', padding: '8px 16px', borderRadius: 8, fontFamily: FONT.sans, fontWeight: 900, fontSize: 38, color: '#fff'}}>{it}</div>
            </div>
          );
        })}
      </div>
      {t >= ok && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1190, display: 'flex', justifyContent: 'center', opacity: clamp(sp(t, ok, SPRING.pop) * 2),
          transform: `scale(${0.8 + 0.2 * sp(t, ok, SPRING.pop)})`}}>
          <div style={{background: '#fff', color: C.ink, padding: '14px 30px', borderRadius: 14, fontFamily: FONT.sans, fontWeight: 900, fontSize: 52,
            boxShadow: '0 12px 30px rgba(0,0,0,0.4)'}}>LET HIM SEE YOU.</div>
        </div>
      )}
    </AbsoluteFill>
  );
};

export const Approach: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.approach;
  const steps = CUES.steps;
  const k = steps.filter((x) => t >= x).length;
  const last = steps[Math.max(0, k - 1)];
  const dip = k > 0 && t - last < 0.35 ? Math.sin(((t - last) / 0.35) * Math.PI) * 6 : 0;
  const flash = cue('flashlight');
  const drop = cue('drop');
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', inset: 0, transform: `translateY(${dip}px)`}}>
        <Art src="approach" t={t} t0={s.start} t1={s.end} from={1.0} to={1.16} ox={60} oy={40} />
      </div>
      <AbsoluteFill style={{mixBlendMode: 'screen', background: `radial-gradient(ellipse 40% 30% at 42% 48%, rgba(255,240,200,${0.5 * prog(t, flash, flash + 0.08)}), rgba(255,240,200,0) 70%)`}} />
      <Label color={SIDE.stakes} text="DANGER?" x={90} y={440} t={t} t0={s.start + 0.1} t1={drop + 0.4} />
    </AbsoluteFill>
  );
};

export const Ask: React.FC<{t: number}> = ({t}) => <Art src="window" t={t} t0={SHOT.ask.start} t1={SHOT.ask.end} from={1.0} to={1.08} oy={35} />;

export const Admit: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.admit;
  const B = cue('admitB'), Cc = cue('admitC');
  return (
    <Card header="THE QUESTION" tone="neutral" t={t} t0={s.start} foot="Jack Rice Defense · Cardon Stuart Law · honesty, not legal advice">
      <In t={t} t0={s.start + 0.1} y={400}>
        <div style={{...big(68), color: SIDE.him}}>“Do you know why<br />I stopped you?”</div>
        <div style={{fontSize: 56, margin: '18px 0', color: 'rgba(255,255,255,0.6)'}}>↓</div>
        <div style={big(56)}>Invites an <span style={glowText(SIDE.stakes)}>admission.</span></div>
      </In>
      {[{t0: B, k: "DON'T KNOW?", v: '“No, officer — could you tell me?”', y: 1000}, {t0: Cc, k: 'DO KNOW?', v: "Don't lie. Short & honest.", y: 1250}].map((r) => (
        <In key={r.k} t={t} t0={r.t0} y={r.y}>
          <div style={big(38, 'rgba(255,255,255,0.5)')}>{r.k}</div>
          <div style={{...big(54), marginTop: 10}}>{r.v}</div>
        </In>
      ))}
    </Card>
  );
};

export const Reg: React.FC<{t: number}> = ({t}) => <Art src="window" t={t} t0={SHOT.reg.start - 2.4} t1={SHOT.reg.end} from={1.08} to={1.2} oy={33} />;

export const Clip: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.clip;
  const pulse = 0.5 + 0.5 * Math.sin(t * Math.PI * 2 * 1.6);
  return (
    <AbsoluteFill>
      <Art src="clip" t={t} t0={s.start} t1={s.end} from={1.0} to={1.14} ox={60} oy={30} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse 70% 60% at 50% 45%, rgba(255,59,78,0) 50%, rgba(255,59,78,${0.16 + 0.14 * pulse}) 100%)`}} />
    </AbsoluteFill>
  );
};

/** a poll answer chip: dark glass, a light that keeps orbiting its border, a breathing halo. The two chips orbit out of phase,
 *  so the eye ping-pongs between them, the way the viewer's mind should. */
export const ChoiceChip: React.FC<{label: string; t: number; t0: number; color: string; phase: number; size?: number}> = ({label, t, t0, color, phase, size = 54}) => {
  if (t < t0) return null;
  const p = sp(t, t0, SPRING.pop);
  const ang = ((t - t0) * 160 + phase * 180) % 360;
  const breathe = 0.5 + 0.5 * Math.sin((t - t0) * Math.PI * 1.2 + phase * Math.PI);
  return (
    <div style={{position: 'relative', borderRadius: 22, padding: 4, transform: `scale(${0.6 + 0.4 * p})`, opacity: clamp(p * 2),
      background: `conic-gradient(from ${ang}deg, ${color} 0deg, ${color}00 90deg, ${color}00 250deg, #fff 320deg, ${color} 360deg)`,
      boxShadow: `0 0 ${24 + 26 * breathe}px ${color}${Math.round(0x40 + 0x50 * breathe).toString(16)}, 0 14px 34px rgba(0,0,0,0.5)`}}>
      <div style={{borderRadius: 18, padding: '18px 38px', background: 'rgba(10,10,14,0.88)', fontFamily: FONT.sans, fontWeight: 900, fontSize: size,
        color: '#fff', letterSpacing: '-0.01em', textShadow: `0 0 ${16 * breathe}px ${color}`}}>{label}</div>
    </div>
  );
};

export const Choice: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.choice;
  const ex = cue('explain'), ap = cue('apologize');
  return (
    <AbsoluteFill>
      <Art src="face" t={t} t0={s.start} t1={s.end} from={1.14} to={1.26} oy={36} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1480, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 22}}>
        <ChoiceChip label="EXPLAIN" t={t} t0={ex} color="#ffffff" phase={0} />
        {t >= ap && <div style={{...big(34, 'rgba(255,255,255,0.7)'), opacity: prog(t, ap, ap + 0.2)}}>or</div>}
        <ChoiceChip label="APOLOGIZE" t={t} t0={ap} color="#ffffff" phase={1} />
      </div>
    </AbsoluteFill>
  );
};

export const Black: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.black;
  const A = cue('blackA'), B = cue('blackB');
  return (
    <AbsoluteFill style={{background: '#0A0A0D'}}>
      <In t={t} t0={A} t1={B - F5} y={820}><div style={big(100, '#fff')}>One drops<br />his guard.</div></In>
      <In t={t} t0={B} t1={s.end + 0.1} y={820}><div style={big(100, '#fff')}>The other<br /><span style={glowText(SIDE.stakes)}>raises it.</span></div></In>
    </AbsoluteFill>
  );
};

export const End: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.end;
  const b1 = cue('end_btn1'), b2 = cue('end_btn2'), p2 = cue('part2');
  if (t >= p2 - 0.02) {
    return (
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 90% 60% at 50% 45%, #1A1530 0%, #08080C 72%)'}}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 1240, display: 'flex', justifyContent: 'center', gap: 22}}>
          <ChoiceChip label="EXPLAIN" t={t} t0={p2 + 0.3} color="#ffffff" phase={0} size={44} />
          <ChoiceChip label="APOLOGIZE" t={t} t0={p2 + 0.45} color="#ffffff" phase={1} size={44} />
        </div>
        <In t={t} t0={p2} y={700}>
          <div style={{...big(140, '#fff'), lineHeight: 0.95}}>PART 2<br /><span style={siren(t)}>TOMORROW</span></div>
          <div style={{...big(40, 'rgba(255,255,255,0.85)'), marginTop: 30, letterSpacing: '-0.01em'}}>Comment EXPLAIN or APOLOGIZE.<br />The majority writes Part 2.</div>
        </In>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <Art src="hook" t={t} t0={s.start} t1={s.end} from={1.25} to={1.32} ox={35} oy={30} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1495, display: 'flex', justifyContent: 'center', gap: 26}}>
        <ChoiceChip label="EXPLAIN" t={t} t0={b1} color="#ffffff" phase={0} />
        <ChoiceChip label="APOLOGIZE" t={t} t0={b2} color="#ffffff" phase={1} />
      </div>
    </AbsoluteFill>
  );
};

export const SCENES: Record<string, React.FC<{t: number}>> = {
  hook: Hook, title: Title, p1: P1, hispov: HisPov, danger: Danger, p2: P2, bias: Bias, slice: Slice, rule: Rule, disarm: Disarm,
  approach: Approach, ask: Ask, admit: Admit, reg: Reg, clip: Clip, choice: Choice, black: Black, end: End,
};

// ================================================================ HUD (reference: three dark mini panels)

export const Hud: React.FC<{t: number}> = ({t}) => {
  const on = CUES.hud_shots.some((id) => t >= SHOT[id].start && t < SHOT[id].end);
  if (!on) return null;
  const secs = t < CUES.clock[0][0] ? 60 : Math.max(0, Math.round(keys(CUES.clock, t)));
  const you = keys(CUES.fear.you, t), his = keys(CUES.fear.his, t);
  // each panel wears its owner's colour; heat = the value glows and the bar fills
  const box = (label: string, value: string, col: string, heat: number, w: number) => (
    <div style={{width: w, height: 92, borderRadius: 12, background: C.hud, padding: '12px 16px', boxSizing: 'border-box', position: 'relative', overflow: 'hidden',
      border: `1.5px solid ${col}${heat > 0.7 ? '99' : '33'}`}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
        <div style={{width: 8, height: 8, borderRadius: 4, background: col, boxShadow: `0 0 8px ${col}`}} />
        <div style={{fontFamily: FONT.mono, fontSize: 16, letterSpacing: 2, color: 'rgba(255,255,255,0.6)'}}>{label}</div>
      </div>
      <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 36, color: heat > 0.7 ? col : '#fff', marginTop: 4, letterSpacing: '-0.01em',
        textShadow: heat > 0.7 ? `0 0 18px ${col}` : undefined}}>{value}</div>
      <div style={{position: 'absolute', left: 0, bottom: 0, height: 4, width: `${heat * 100}%`, background: col, boxShadow: `0 0 10px ${col}`}} />
    </div>
  );
  return (
    <div style={{position: 'absolute', left: 60, top: 100, display: 'flex', gap: 12}}>
      {box('CLOCK', `0:${String(secs).padStart(2, '0')}`, secs <= 5 ? SIDE.stakes : '#fff', secs <= 5 ? 1 : secs / 60, 220)}
      {box('YOUR FEAR', `${you.toFixed(1)}/10`, SIDE.stakes, you / 10, 250)}
      {box('HIS FEAR', `${his.toFixed(1)}/10`, SIDE.stakes, his / 10, 250)}
    </div>
  );
};
