import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {CUES, SHOT, cue, keys, wordT} from './data';
import {C, EASE, FONT, FPS, SPRING, W, H} from './theme';
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
const Pill: React.FC<{text: string; t: number; t0: number; t1: number}> = ({text, t, t0, t1}) => {
  const a = win(t, t0, t1, 0.15, 0.12);
  if (a <= 0) return null;
  return (
    <div style={{position: 'absolute', left: 60, top: 222, opacity: a, transform: `translateX(${(1 - a) * -20}px)`, padding: '8px 16px', borderRadius: 8,
      background: C.pink, fontFamily: FONT.mono, fontWeight: 700, fontSize: 22, letterSpacing: 3, color: '#fff'}}>{text}</div>
  );
};

/** a label the other person puts on you: pink pill + mono sub-line + a ring on the thing (reference "BAIT MONEY") */
const Label: React.FC<{text: string; sub?: string; x: number; y: number; t: number; t0: number; t1: number; ring?: [number, number, number]; red?: boolean}> = ({
  text, sub, x, y, t, t0, t1, ring,
}) => {
  if (t < t0 - 0.02 || t > t1) return null;
  const p = sp(t, t0, SPRING.pop);
  const out = 1 - prog(t, t1 - 0.15, t1, EASE.in);
  const r = ring ? prog(t, t0, t0 + 0.35, EASE.out) : 0;
  return (
    <>
      {ring && (
        <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, opacity: out}}>
          <circle cx={ring[0]} cy={ring[1]} r={ring[2]} fill="none" stroke={C.pink} strokeWidth={6} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - r}
            transform={`rotate(-90 ${ring[0]} ${ring[1]})`} />
        </svg>
      )}
      <div style={{position: 'absolute', left: x, top: y, opacity: clamp(p * 2) * out, transform: `scale(${0.7 + 0.3 * p})`, transformOrigin: '0 50%'}}>
        <div style={{display: 'inline-block', background: C.pink, padding: '10px 18px 8px', borderRadius: 8, fontFamily: FONT.sans, fontWeight: 900,
          fontSize: 40, color: '#fff', letterSpacing: '-0.01em', boxShadow: '0 8px 24px rgba(0,0,0,0.35)'}}>{text}</div>
        {sub && <div style={{marginTop: 6, display: 'inline-block', background: 'rgba(0,0,0,0.6)', padding: '4px 10px', borderRadius: 6, fontFamily: FONT.mono,
          fontSize: 18, letterSpacing: 2, color: '#fff'}}>{sub}</div>}
      </div>
    </>
  );
};

// ================================================================ cards

const Cream: React.FC<{header: string; t: number; t0: number; foot?: string; children: React.ReactNode}> = ({header, t, t0, foot, children}) => (
  <AbsoluteFill style={{background: C.cream}}>
    <div style={{position: 'absolute', left: 0, right: 0, top: 300, textAlign: 'center', fontFamily: FONT.mono, fontSize: 24, letterSpacing: 6, color: C.grey,
      opacity: prog(t, t0, t0 + 0.25)}}>{header}</div>
    {children}
    {foot && <div style={{position: 'absolute', left: 60, right: 60, top: 1640, textAlign: 'center', fontFamily: FONT.mono, fontSize: 19, letterSpacing: 1,
      color: C.grey, opacity: prog(t, t0 + 0.6, t0 + 1.0)}}>{foot}</div>}
  </AbsoluteFill>
);

/** a block of card type that arrives (rise + blur) and leaves over the 5 frames before the next */
const In: React.FC<{t: number; t0: number; t1?: number; y: number; children: React.ReactNode; style?: React.CSSProperties}> = ({t, t0, t1 = 1e9, y, children, style}) => {
  const a = win(t, t0, t1, 0.22, F5);
  if (a <= 0) return null;
  const p = prog(t, t0, t0 + 0.35, EASE.out);
  return <div style={{position: 'absolute', left: 70, right: 70, top: y, textAlign: 'center', opacity: a, transform: `translateY(${(1 - p) * 26}px)`,
    filter: `blur(${(1 - p) * 8}px)`, ...style}}>{children}</div>;
};

const big = (size: number, color: string = C.ink): React.CSSProperties => ({fontFamily: FONT.sans, fontWeight: 900, fontSize: size, lineHeight: 1.04,
  letterSpacing: '-0.03em', color});

const Stamp: React.FC<{t: number; t0: number; text: string; y: number; rot?: number}> = ({t, t0, text, y, rot = -5}) => {
  if (t < t0) return null;
  const u = t - t0;
  const s = 1 + 0.5 * Math.max(0, 1 - u / 0.1) ** 2;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center'}}>
      <div style={{transform: `rotate(${rot}deg) scale(${s})`, opacity: clamp(u / 0.05), border: `5px solid ${C.pink}`, borderRadius: 10,
        padding: '6px 22px', fontFamily: FONT.sans, fontWeight: 900, fontSize: 46, letterSpacing: 2, color: C.pink}}>{text}</div>
    </div>
  );
};

/** rolling count-up with blurred digits while they spin (reference) */
const Count: React.FC<{t: number; t0: number; dur: number; to: number; size: number; color?: string; prefix?: string}> = ({t, t0, dur, to, size, color = C.ink, prefix = ''}) => {
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
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', fontFamily: FONT.mono, fontSize: 24, letterSpacing: 6,
        color: 'rgba(255,255,255,0.8)', opacity: prog(t, s.start, s.start + 0.3)}}>PART 1 · THE TRAFFIC STOP</div>
      <div style={{position: 'absolute', left: 60, right: 60, top: 700, textAlign: 'center'}}>
        {words.map((w, i) => {
          const p = sp(t, s.start + 0.08 + i * 0.12, SPRING.pop);
          return <div key={w} style={{...big(170, w === 'SCARED' ? C.pink : '#fff'), lineHeight: 0.95, opacity: clamp(p * 1.5),
            transform: `translateY(${(1 - p) * 40}px) scale(${0.9 + 0.1 * p})`, filter: `blur(${(1 - clamp(p)) * 10}px)`}}>{w}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

export const P1: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill>
    <Art src="cruiser" t={t} t0={SHOT.p1.start} t1={SHOT.p1.end} from={1.04} to={1.12} oy={35} />
    <Pill text="PROBLEM 1" t={t} t0={SHOT.p1.start} t1={SHOT.hispov.end} />
  </AbsoluteFill>
);

export const HisPov: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.hispov;
  const [a, b, c, d] = [cue('tagH1'), cue('tagH2'), cue('tagH3'), cue('tagH4')];
  return (
    <AbsoluteFill>
      <Art src="hispov" t={t} t0={s.start} t1={s.end} from={1.0} to={1.12} oy={42} />
      <Pill text="PROBLEM 1" t={t} t0={s.start - 0.1} t1={s.end} />
      <Label text="PAPER TAGS?" sub="TEMP PLATE" x={560} y={850} t={t} t0={a} t1={s.end} ring={[645, 690, 90]} />
      <Label text="LOUD MUSIC" sub="BASS · 2 BLOCKS AWAY" x={90} y={460} t={t} t0={b} t1={s.end} />
      <Label text="TANK TOP" sub="DRIVER · ONE" x={580} y={470} t={t} t0={c} t1={s.end} ring={[535, 560, 70]} />
      <Label text="DANGER?" x={90} y={1000} t={t} t0={d} t1={s.end} />
    </AbsoluteFill>
  );
};

export const Danger: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.danger;
  const B = cue('dangerB'), Cc = cue('dangerC'), dot = cue('dot');
  const cols = 24, rows = 20;
  const fill = prog(t, B + 0.2, dot + 0.3, EASE.inOut);
  return (
    <Cream header="PROBLEM 1 · HIS SIDE" t={t} t0={s.start} foot="Woods (2019), Michigan Law Review 117(4) · 10 yrs, 200+ Florida agencies">
      <In t={t} t0={s.start + 0.1} t1={B - F5} y={620}>
        <div style={big(54, C.ink2)}>His training says</div>
        <div style={{...big(118), marginTop: 18}}>any stop could<br /><span style={{color: C.pink}}>turn deadly.</span></div>
      </In>
      <In t={t} t0={B} t1={Cc - F5} y={420}>
        <svg width={cols * 34} height={rows * 22} style={{display: 'block', margin: '0 auto'}}>
          {Array.from({length: cols * rows}, (_, i) => {
            const on = i / (cols * rows) < fill;
            return <rect key={i} x={(i % cols) * 34 + 4} y={Math.floor(i / cols) * 22 + 4} width={26} height={14} rx={3}
              fill={on ? '#8FA889' : 'rgba(0,0,0,0.06)'} stroke={on ? '#5E7759' : 'none'} strokeWidth={1.5} />;
          })}
        </svg>
        <div style={{...big(76), marginTop: 46}}>1 in <Count t={t} t0={B + 0.2} dur={dot - B + 0.2} to={6500000} size={76} color={C.pink} /></div>
        <div style={{fontFamily: FONT.mono, fontSize: 24, color: C.ink2, marginTop: 14}}>routine stops where an officer was killed</div>
      </In>
      <In t={t} t0={Cc} t1={s.end + 0.1} y={700}><div style={big(120)}>But fear doesn't<br /><span style={{color: C.pink}}>read data.</span></div></In>
    </Cream>
  );
};

export const P2: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.p2;
  const [a, b, c] = [cue('tagY1'), cue('tagY2'), cue('tagY3')];
  return (
    <AbsoluteFill>
      <Art src="mirror" t={t} t0={s.start} t1={s.end} from={1.0} to={1.1} ox={60} oy={40} />
      <Pill text="PROBLEM 2" t={t} t0={s.start} t1={s.end} />
      <Label text="POWER TRIP?" sub="HANDS ON HIPS" x={420} y={760} t={t} t0={a} t1={s.end} />
      <Label text="QUOTA?" sub="END OF THE MONTH" x={560} y={380} t={t} t0={b} t1={s.end} />
      <Label text="THE BADGE" x={430} y={980} t={t} t0={c} t1={s.end} ring={[630, 480, 60]} />
    </AbsoluteFill>
  );
};

export const Bias: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.bias;
  const B = cue('biasB');
  const st = cue('stamp_bias');
  return (
    <Cream header="PROBLEM 2 · YOUR SIDE" t={t} t0={s.start} foot="Correll, Park, Judd & Wittenbrink (2002), JPSP 83(6)">
      <In t={t} t0={s.start + 0.1} y={520}>
        <div style={big(48, C.ink2)}>In a famous study,</div>
        <div style={{...big(96), marginTop: 18}}>split-second threat calls followed</div>
        <div style={{...big(104, C.pink), marginTop: 6}}>cultural stereotypes.</div>
      </In>
      <In t={t} t0={B} y={1060}>
        <div style={{width: 6, height: 70, background: C.ink, margin: '0 auto 22px', borderRadius: 3}} />
        <div style={big(64)}>Even in people with</div>
        <div style={big(64)}>no personal prejudice.</div>
      </In>
      <Stamp t={t} t0={st} text="STILL" y={1330} />
    </Cream>
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
    <AbsoluteFill style={{background: C.dark}}>
      <In t={t} t0={s.start + 0.05} y={760}>
        <div style={{fontFamily: FONT.mono, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: C.pink}}>RULE 1</div>
        <div style={{...big(96, '#fff'), marginTop: 26}}>Disarm the fear<br />before you speak.</div>
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
      <Pill text="RULE 1" t={t} t0={s.start} t1={s.end} />
      <div style={{position: 'absolute', left: 60, top: 300}}>
        {items.map((it, i) => {
          if (t < ts[i] - 0.02) return null;
          const p = sp(t, ts[i], SPRING.pop);
          return (
            <div key={it} style={{display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16, opacity: clamp(p * 2), transform: `translateX(${(1 - p) * -30}px)`}}>
              <div style={{width: 44, height: 44, borderRadius: 22, background: C.pink, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <svg width={26} height={26}><path d="M 5 14 L 11 20 L 22 7" fill="none" stroke="#fff" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round"
                  pathLength={1} strokeDasharray={1} strokeDashoffset={1 - prog(t, ts[i] + 0.05, ts[i] + 0.3)} /></svg>
              </div>
              <div style={{background: 'rgba(0,0,0,0.62)', padding: '8px 16px', borderRadius: 8, fontFamily: FONT.sans, fontWeight: 900, fontSize: 38, color: '#fff'}}>{it}</div>
            </div>
          );
        })}
      </div>
      {t >= ok && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1060, display: 'flex', justifyContent: 'center', opacity: clamp(sp(t, ok, SPRING.pop) * 2),
          transform: `scale(${0.8 + 0.2 * sp(t, ok, SPRING.pop)})`}}>
          <div style={{background: '#fff', color: C.ink, padding: '14px 30px', borderRadius: 14, fontFamily: FONT.sans, fontWeight: 900, fontSize: 52,
            boxShadow: '0 12px 30px rgba(0,0,0,0.4)'}}>LET HIM <span style={{color: C.pink}}>SEE YOU.</span></div>
        </div>
      )}
      <div style={{position: 'absolute', left: 0, right: 0, top: 1500, textAlign: 'center', fontFamily: FONT.mono, fontSize: 18, color: 'rgba(255,255,255,0.6)',
        opacity: prog(t, cue('handbook'), cue('handbook') + 0.3)}}>Texas DPS Driver Handbook · AAMVA</div>
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
      <Label text="DANGER?" x={90} y={440} t={t} t0={s.start + 0.1} t1={drop + 0.4} />
    </AbsoluteFill>
  );
};

export const Ask: React.FC<{t: number}> = ({t}) => <Art src="window" t={t} t0={SHOT.ask.start} t1={SHOT.ask.end} from={1.0} to={1.08} oy={35} />;

export const Admit: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.admit;
  const B = cue('admitB'), Cc = cue('admitC');
  return (
    <Cream header="THE QUESTION" t={t} t0={s.start} foot="Jack Rice Defense · Cardon Stuart Law · honesty, not legal advice">
      <In t={t} t0={s.start + 0.1} y={400}>
        <div style={big(68)}>“Do you know why<br />I stopped you?”</div>
        <div style={{fontSize: 56, margin: '18px 0', color: C.ink}}>↓</div>
        <div style={big(56)}>Invites an <span style={{color: C.pink}}>admission.</span></div>
      </In>
      {[{t0: B, k: "DON'T KNOW?", v: '“No, officer — could you tell me?”', y: 1000}, {t0: Cc, k: 'DO KNOW?', v: "Don't lie. Short & honest.", y: 1250}].map((r) => (
        <In key={r.k} t={t} t0={r.t0} y={r.y}>
          <div style={{fontFamily: FONT.mono, fontWeight: 700, fontSize: 26, letterSpacing: 4, color: C.pink}}>{r.k}</div>
          <div style={{...big(54), marginTop: 10}}>{r.v}</div>
        </In>
      ))}
    </Cream>
  );
};

export const Reg: React.FC<{t: number}> = ({t}) => <Art src="window" t={t} t0={SHOT.reg.start - 2.4} t1={SHOT.reg.end} from={1.08} to={1.2} oy={33} />;

export const Clip: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.clip;
  const pulse = 0.5 + 0.5 * Math.sin(t * Math.PI * 2 * 1.6);
  return (
    <AbsoluteFill>
      <Art src="clip" t={t} t0={s.start} t1={s.end} from={1.0} to={1.14} ox={60} oy={30} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse 70% 60% at 50% 45%, rgba(232,69,139,0) 50%, rgba(232,69,139,${0.18 + 0.16 * pulse}) 100%)`}} />
    </AbsoluteFill>
  );
};

export const Choice: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.choice;
  const ex = cue('explain'), ap = cue('apologize');
  const btn = (label: string, t0: number, pink: boolean) => {
    if (t < t0) return null;
    const p = sp(t, t0, SPRING.pop);
    return <div style={{padding: '18px 40px', borderRadius: 16, background: pink ? C.pink : C.cream, color: pink ? '#fff' : C.ink, fontFamily: FONT.sans, fontWeight: 900,
      fontSize: 54, transform: `scale(${0.6 + 0.4 * p})`, opacity: clamp(p * 2), boxShadow: '0 12px 30px rgba(0,0,0,0.45)'}}>{label}</div>;
  };
  return (
    <AbsoluteFill>
      <Art src="face" t={t} t0={s.start} t1={s.end} from={1.14} to={1.26} oy={36} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1480, display: 'flex', justifyContent: 'center', gap: 26}}>
        {btn('EXPLAIN', ex, false)}{btn('APOLOGIZE', ap, true)}
      </div>
    </AbsoluteFill>
  );
};

export const Black: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.black;
  const A = cue('blackA'), B = cue('blackB');
  return (
    <AbsoluteFill style={{background: C.dark}}>
      <In t={t} t0={A} t1={B - F5} y={820}><div style={big(100, '#fff')}>One drops<br />his guard.</div></In>
      <In t={t} t0={B} t1={s.end + 0.1} y={820}><div style={big(100, '#fff')}>The other<br /><span style={{color: C.pink}}>raises it.</span></div></In>
    </AbsoluteFill>
  );
};

export const End: React.FC<{t: number}> = ({t}) => {
  const s = SHOT.end;
  const b1 = cue('end_btn1'), b2 = cue('end_btn2'), p2 = cue('part2');
  const btn = (label: string, t0: number, pink: boolean) => {
    if (t < t0) return null;
    const p = sp(t, t0, SPRING.pop);
    return <div style={{padding: '18px 40px', borderRadius: 16, background: pink ? C.pink : C.cream, color: pink ? '#fff' : C.ink, fontFamily: FONT.sans, fontWeight: 900,
      fontSize: 54, transform: `scale(${0.6 + 0.4 * p})`, opacity: clamp(p * 2)}}>{label}</div>;
  };
  if (t >= p2 - 0.02) {
    return (
      <AbsoluteFill style={{background: C.dark}}>
        <In t={t} t0={p2} y={760}>
          <div style={{fontFamily: FONT.mono, fontSize: 22, letterSpacing: 5, color: 'rgba(255,255,255,0.6)'}}>TWO SCARED PEOPLE</div>
          <div style={{...big(140, '#fff'), marginTop: 16, lineHeight: 0.95}}>PART 2<br /><span style={{color: C.pink}}>TOMORROW</span></div>
          <div style={{...big(40, 'rgba(255,255,255,0.85)'), marginTop: 30, letterSpacing: '-0.01em'}}>Comment EXPLAIN or APOLOGIZE.<br />The majority writes Part 2.</div>
        </In>
        <div style={{position: 'absolute', left: 0, right: 0, top: 1640, textAlign: 'center', fontFamily: FONT.mono, fontSize: 20, color: 'rgba(255,255,255,0.45)'}}>
          @obavia — the psychology behind every conversation · not legal advice</div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <Art src="hook" t={t} t0={s.start} t1={s.end} from={1.25} to={1.32} ox={35} oy={30} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1060, textAlign: 'center', fontFamily: FONT.mono, fontSize: 24, letterSpacing: 5, color: '#fff',
        opacity: prog(t, s.start + 0.1, s.start + 0.4)}}>COMMENT ONE WORD</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1120, display: 'flex', justifyContent: 'center', gap: 26}}>
        {btn('EXPLAIN', b1, false)}{btn('APOLOGIZE', b2, true)}
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
  const box = (label: string, value: string, hot: boolean, w: number) => (
    <div style={{width: w, height: 92, borderRadius: 12, background: C.hud, padding: '12px 16px', boxSizing: 'border-box'}}>
      <div style={{fontFamily: FONT.mono, fontSize: 16, letterSpacing: 2, color: 'rgba(255,255,255,0.55)'}}>{label}</div>
      <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 36, color: hot ? C.pink : '#fff', marginTop: 4, letterSpacing: '-0.01em'}}>{value}</div>
    </div>
  );
  return (
    <div style={{position: 'absolute', left: 60, top: 100, display: 'flex', gap: 12}}>
      {box('CLOCK', `0:${String(secs).padStart(2, '0')}`, secs <= 5, 220)}
      {box('YOUR FEAR', `${you.toFixed(1)}/10`, you >= 7, 250)}
      {box('HIS FEAR', `${his.toFixed(1)}/10`, his >= 7, 250)}
    </div>
  );
};
