import timelineJson from './data/timeline.json';
import cuesJson from './data/cues.json';

export type Word = {clip: string; shot: string; speaker: string; i: number; w: string; s: number; e: number};
export type Clip = {id: string; shot: string; speaker: string; text: string; file: string; start: number; dur: number; rms?: number[]};
export type Shot = {id: string; start: number; end: number};
export type Ev = {name: string; t: number; f: number; sfx: string | null; gain: number; lead: number};
export type Cap = {shot: string; speaker: string; s: number; e: number; out: number; words: {w: string; s: number; e: number}[]; accent: number[]};

export const TL = timelineJson as unknown as {
  fps: number; duration: number; frames: number; shots: Shot[]; clips: Clip[]; words: Word[];
};
export const CUES = cuesJson as unknown as {
  events: Ev[]; steps: number[]; pens: [number, number][]; hazard: {hz: number; spans: [number, number][]};
  clock: [number, number][]; fear: {you: [number, number][]; his: [number, number][]}; hud_shots: string[]; captions: Cap[];
};

export const SHOT: Record<string, Shot> = Object.fromEntries(TL.shots.map((s) => [s.id, s]));

/** time of a named cue (seconds) */
export const cue = (name: string): number => {
  const e = CUES.events.find((x) => x.name === name);
  if (!e) throw new Error('missing cue ' + name);
  return e.t;
};
export const cues = (prefix: string): number[] => CUES.events.filter((x) => x.name.startsWith(prefix)).map((x) => x.t);

/** word start time in a shot (first word starting with `w`, occurrence k) */
export const wordT = (shot: string, w: string, k = 1): number => {
  let n = 0;
  for (const x of TL.words) {
    if (x.shot === shot && x.w.toLowerCase().replace(/[^a-z0-9.]/g, '').startsWith(w.toLowerCase())) {
      n++;
      if (n === k) return x.s;
    }
  }
  throw new Error('missing word ' + shot + ':' + w);
};

export const officerClips = TL.clips.filter((c) => c.speaker === 'O');

/** officer mouth openness from that clip's per-frame RMS (lip flaps only during his audio) */
export const officerMouth = (t: number): number | null => {
  for (const c of officerClips) {
    if (t >= c.start && t < c.start + c.dur) {
      const i = Math.floor((t - c.start) * 30);
      const r = c.rms?.[i] ?? 0;
      return Math.min(1, Math.pow(r, 0.7) * 1.25);
    }
  }
  return null;
};

/** piecewise-linear keyframes [[t, v], ...] with eased segments */
export const keys = (k: [number, number][], t: number): number => {
  if (t <= k[0][0]) return k[0][1];
  for (let i = 0; i < k.length - 1; i++) {
    const [a, va] = k[i];
    const [b, vb] = k[i + 1];
    if (t <= b) {
      const u = b === a ? 1 : (t - a) / (b - a);
      const e = 0.5 - 0.5 * Math.cos(Math.PI * u);
      return va + (vb - va) * e;
    }
  }
  return k[k.length - 1][1];
};
