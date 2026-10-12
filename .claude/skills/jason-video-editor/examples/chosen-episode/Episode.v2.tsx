/**
 * EPISODE #5 "Chosen" v2 — rebuilt against references/scorecard.md (v1 scored 5.6: retention 4, psychology 5, visual language 5).
 *  - DUAL TYPE ONLY: Inter (sans, 700–900) + Instrument Serif italic (the accent word, gold). One accent colour: gold.
 *  - a designed beat on every sentence; nothing bare-face longer than ~4 s (the smile reaction is the one deliberate hold)
 *  - psychology: the hook card is an open loop ("how can you beat… chosen") that the payoff closes with the SAME card (callback);
 *    "if YOU want to be better than me" is staged at the viewer
 *  - engraving cutaways are dark prints in the same world as the car, bridged in with a 5-frame blur dissolve (no white flash)
 */
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import "@fontsource-variable/inter/opsz.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import "@fontsource/instrument-serif/400-italic.css";
import { CoopCaptions } from "../lib/Coop";
import { FollowCard } from "../lib/Graphics";
import { glass } from "../lib/Ios";
import { NotificationStack } from "../lib/IosNotify";
import { at, CUT, EDL, sec } from "./timeline";
import { Video } from "../lib/Video";

export const OUTRO = 96;
const FLIP = CUT + 52;
const SANS = "'Inter Variable', Inter, sans-serif";
const SERIF = "'Instrument Serif', serif";
const GOLD = "#FFC94A", RED = "#FF453A", INK = "#F4F4F6", DIM = "rgba(244,244,246,.55)";
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outE = (x: number) => 1 - Math.pow(1 - x, 3);
const NOB = { damping: 30, stiffness: 190, mass: 1 }; // critically damped: no wobble

const A = {
  how: at("cold", "HOW"), beat: at("cold", "BEAT"), nigga0: at("cold", "NIGGA"), believes0: at("cold", "BELIEVES"), he0: at("cold2", "HE"), chosen0: at("cold2", "CHOSEN"), god0: at("cold2", "GOD"),
  iff: at("hook", "IF"), dick: at("hook", "DICK"), six: at("hook", "SIX"), amazing: at("hook", "AMAZING,"), handsome: at("hook", "HANDSOME,"),
  yo: at("lang", "YO"), ni: at("lang", "NI"), real: at("speak", "REAL"), speak: at("speak", "SPEAK"), language: at("speak", "LANGUAGE."),
  gifted: at("gifted", "GIFTED."), intel: at("gifted", "INTELLECTUALLY"), shout: at("gifted", "SHOUT"),
  you1: at("belief", "YOU", 1), better: at("belief", "BETTER", 1), cannot: at("belief", "CANNOT"), because: at("belief", "BECAUSE"),
  confidence: at("confidence", "CONFIDENCE"), high2: at("confidence", "HIGH."), cant: at("cantell", "CAN'T"), shit: at("cantell", "SHIT."),
  thousand: at("room", "THOUSAND"), room: at("room", "ROOM,"), jason: at("room", "JASON,"), black: at("room", "BLACK"), fucking: at("room", "FUCKING"), look: at("room", "LOOK"),
  high3: at("ego", "HIGH"), ego: at("ego", "EGO."),
  sorry: at("arrogant", "SORRY,"), not: at("arrogant", "NOT", 1), yeah: at("arrogant", "YEAH,"), arrogant: at("arrogant", "ARROGANT"), know: at("arrogant", "KNOW"), better2: at("arrogant", "BETTER", 1),
  notBecause: at("arrogant", "BECAUSE"), literally: at("arrogant", "LITERALLY"), even: at("arrogant", "EVEN"), am: at("arrogant", "AM."),
  view: at("superior", "VIEW"), superior: at("superior", "SUPERIOR"), chosen1: at("superior", "CHOSEN"), god1: at("superior", "GOD."),
  how2: at("payoff", "HOW"), beat2: at("payoff", "BEAT"), believes2: at("payoff", "BELIEVES"),
  make: at("payoff2", "MAKE", 1), sense: at("payoff2", "SENSE."), or: at("payoff2", "OR"), have: at("payoff2", "HAVE"), bitch: at("payoff2", "BITCH."),
};
const [, cold1] = sec("cold2"), [lang0, lang1] = sec("lang"), [speak0, speak1] = sec("speak"), [belief0] = sec("belief"), [conf0] = sec("confidence"), [, cant1] = sec("cantell");
const [room0] = sec("room"), [ego0, ego1] = sec("ego"), [arr0, arr1] = sec("arrogant"), [sup0, sup1] = sec("superior"), [pay0] = sec("payoff");

// engraving inserts (dark prints): [file, from, to, landings], each starts 2 frames before its sentence
const INS = [
  { src: "ep/ins_persp.mp4", from: 853, to: 920, land: [874] },
  { src: "ep/ins_indef.mp4", from: 972, to: 1034, land: [989] },
  { src: "ep/ins_high.mp4", from: 1170, to: 1340, land: [1185, 1250, 1327] },
  { src: "ep/ins_chosen.mp4", from: 2327, to: 2543, land: [2341, 2419, 2447, 2494], success: 2518 },
];

// ─────────────── shared pieces (two fonts only) ───────────────
const useWin = (from: number, to: number) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - from, fps, config: NOB });
  const out = interpolate(f, [to - 7, to], [1, 0], { ...cl, easing: (x) => x * x });
  return { f, fps, p, out, on: f >= from - 1 && f < to };
};
const enter = (p: number, out = 1, dy = 30): React.CSSProperties => ({
  opacity: Math.min(1, p * 1.3) * out, filter: `blur(${(1 - p) * 12 + (1 - out) * 10}px)`, transform: `translateY(${(1 - p) * dy}px) scale(${0.96 + 0.04 * p})`,
});
/** one word rising: sans (Inter 800) or the accent (Instrument Serif italic, gold) */
const Word: React.FC<{ t: string; at: number; serif?: boolean; size: number; color?: string }> = ({ t, at: a, serif, size, color }) => {
  const f = useCurrentFrame();
  if (f < a - 1) return null;
  const p = outE(Math.min(1, (f - a + 1) / 9));
  return (
    <span style={{ display: "inline-block", fontFamily: serif ? SERIF : SANS, fontStyle: serif ? "italic" : "normal", fontWeight: serif ? 400 : 800,
      fontSize: serif ? size * 1.25 : size, letterSpacing: serif ? "-0.01em" : "-0.045em", color: color ?? (serif ? GOLD : INK), lineHeight: 1.02,
      opacity: p, transform: `translateY(${(1 - p) * 0.35}em)`, filter: `blur(${(1 - p) * 8}px)`, textShadow: serif ? `0 0 40px ${GOLD}55` : "0 6px 30px rgba(0,0,0,.6)", margin: "0 0.12em" }}>{t}</span>
  );
};

/** HOOK CARD — full-screen kinetic type over the dimmed footage. Used twice: cold open (open loop) and payoff (callback). */
const HookCard: React.FC<{ from: number; to: number; words: { t: string; at: number; serif?: boolean; size?: number; br?: boolean; color?: string }[] }> = ({ from, to, words }) => {
  const f = useCurrentFrame();
  if (f < from - 1 || f >= to) return null;
  const dim = interpolate(f, [from, from + 6, to - 8, to], [0, 0.62, 0.62, 0], cl);
  const out = interpolate(f, [to - 8, to], [1, 0], cl);
  const lines: (typeof words)[] = [[]];
  words.forEach((w) => { if (w.br && lines[lines.length - 1].length) lines.push([]); lines[lines.length - 1].push(w); });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: `rgba(6,6,9,${dim})` }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, filter: `blur(${(1 - out) * 10}px)` }}>
        <div style={{ width: 960, textAlign: "center", marginTop: -160 }}>
          {lines.map((ln, i) => <div key={i} style={{ marginBottom: 6 }}>{ln.map((w) => <Word key={w.at + w.t} t={w.t} at={w.at} serif={w.serif} size={(w.size ?? 96) * 1.3} color={w.color} />)}</div>)}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** iOS Notes checklist — "if you want to be like me": his requirements tick off one by one (one card, two visits) */
const Checklist: React.FC<{ from: number; to: number; items: { t: string; at: number; serif?: boolean }[] }> = ({ from, to, items }) => {
  const { f, fps, p, out, on } = useWin(from, to);
  if (!on) return null;
  return (
    <div style={{ position: "absolute", top: 120, left: 64, right: 64, ...glass, background: "rgba(24,24,28,.82)", borderRadius: 44, padding: "30px 40px 26px", ...enter(p, out, -40) }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: SANS, fontSize: 28, fontWeight: 600, color: GOLD }}><span>‹ Notes</span><span>Done</span></div>
      <div style={{ fontFamily: SANS, fontSize: 72, fontWeight: 800, letterSpacing: "-0.035em", color: INK, margin: "10px 0 14px" }}>if you want to be <span style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, color: GOLD, fontSize: 92 }}>like me</span></div>
      {items.filter((it) => f >= it.at - 2).map((it) => {
        const q = spring({ frame: f - it.at, fps, config: NOB });
        const c = spring({ frame: f - it.at - 6, fps, config: { damping: 18, stiffness: 260 } });
        return (
          <div key={it.t} style={{ display: "flex", alignItems: "center", gap: 22, padding: "10px 0", opacity: Math.min(1, q * 1.4), transform: `translateX(${(1 - q) * -30}px)` }}>
            <div style={{ width: 68, height: 68, borderRadius: 34, border: `3px solid ${c > 0.5 ? GOLD : "rgba(255,255,255,.35)"}`, background: c > 0.5 ? GOLD : "transparent", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ fontFamily: SANS, fontWeight: 900, fontSize: 42, color: "#151006", transform: `scale(${c})` }}>✓</span>
            </div>
            <span style={{ fontFamily: it.serif ? SERIF : SANS, fontStyle: it.serif ? "italic" : "normal", fontWeight: it.serif ? 400 : 700, fontSize: it.serif ? 84 : 64, letterSpacing: it.serif ? "0" : "-0.025em", color: it.serif ? GOLD : INK }}>{it.t}</span>
          </div>
        );
      })}
    </div>
  );
};

/** iOS Translate — one card at a time: the original types in, the English resolves under it */
const Translate: React.FC<{ from: number; to: number; cards: { at: number; until: number; lang: string; text: string; en: string; cjk?: boolean }[] }> = ({ from, to, cards }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from - 1 || f >= to) return null;
  const c = cards.find((k) => f >= k.at - 2 && f < k.until);
  if (!c) return null;
  const p = spring({ frame: f - c.at, fps, config: NOB });
  const out = interpolate(f, [c.until - 7, c.until], [1, 0], cl);
  const n = Math.floor(Math.max(0, f - c.at) * (c.cjk ? 0.7 : 1.4));
  const q = spring({ frame: f - c.at - 26, fps, config: NOB });
  return (
    <div style={{ position: "absolute", top: 120, left: 64, right: 64, ...glass, background: "rgba(24,24,28,.84)", borderRadius: 44, padding: "30px 40px", ...enter(p, out, -40) }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: SANS, fontSize: 32, fontWeight: 700, letterSpacing: "0.08em", color: DIM }}><span>{c.lang.toUpperCase()}</span><span style={{ color: GOLD }}>⇄ ENGLISH</span></div>
      <div style={{ fontFamily: c.cjk ? "'WenQuanYi Zen Hei', Inter" : SANS, fontSize: 74, fontWeight: 800, letterSpacing: "-0.025em", color: INK, lineHeight: 1.15, marginTop: 12, minHeight: 170 }}>
        {c.text.slice(0, n)}<span style={{ color: GOLD, opacity: Math.floor(f / 8) % 2 && n < c.text.length ? 1 : 0 }}>|</span>
      </div>
      <div style={{ height: 2, background: "rgba(255,255,255,.14)", margin: "18px 0", transform: `scaleX(${q})`, transformOrigin: "0 50%" }} />
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 84, color: GOLD, lineHeight: 1.05, opacity: q, filter: `blur(${(1 - q) * 8}px)`, transform: `translateY(${(1 - q) * 14}px)` }}>{c.en}</div>
    </div>
  );
};

/** HERO word behind his head: sans (white/red) or the serif accent (gold), between footage and his cutout */
const Hero: React.FC<{ text: string; at: number; until: number; serif?: boolean; color?: string; size?: number; top?: number }> = ({ text, at: a, until, serif, color, size = 300, top = 120 }) => {
  const { f, p, out, on } = useWin(a, until);
  if (!on) return null;
  const col = color ?? (serif ? GOLD : INK);
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div style={{ marginTop: top, fontFamily: serif ? SERIF : SANS, fontStyle: serif ? "italic" : "normal", fontWeight: serif ? 400 : 900, fontSize: serif ? size * 1.2 : size,
        letterSpacing: serif ? "-0.01em" : "-0.055em", lineHeight: 0.9, color: col, whiteSpace: "nowrap", opacity: p * out,
        filter: `blur(${(1 - p) * 18 + (1 - out) * 10}px)`, transform: `scale(${1.1 - 0.1 * p + 0.03 * Math.min(1, (f - a) / 60)})`, textShadow: `0 0 60px ${col}55` }}>{text}</div>
    </AbsoluteFill>
  );
};

/** "shout out to my nigga Tate": his line as a sent iMessage */
const Sent: React.FC<{ at: number; until: number; text: string }> = ({ at: a, until, text }) => {
  const { p, out, on } = useWin(a, until);
  if (!on) return null;
  return (
    <div style={{ position: "absolute", top: 210, right: 64, maxWidth: 760, ...enter(p, out, 40) }}>
      <div style={{ background: "#0A84FF", color: "#fff", fontFamily: SANS, fontSize: 64, fontWeight: 600, letterSpacing: "-0.02em", padding: "26px 40px", borderRadius: 44, borderBottomRightRadius: 12, boxShadow: "0 20px 50px rgba(0,0,0,.45)" }}>{text}</div>
      <div style={{ textAlign: "right", fontFamily: SANS, fontSize: 24, fontWeight: 600, color: DIM, marginTop: 10 }}>Delivered</div>
    </div>
  );
};

/** confidence meter: fills to 100%, then his words land as the serif accent */
const Meter: React.FC<{ from: number; fill: number; sub: number; to: number }> = ({ from, fill, sub, to }) => {
  const { f, fps, p, out, on } = useWin(from, to);
  if (!on) return null;
  const q = interpolate(f, [fill, fill + 30], [0.12, 1], { ...cl, easing: outE });
  const s = spring({ frame: f - sub, fps, config: NOB });
  return (
    <div style={{ position: "absolute", top: 130, left: 64, right: 64, ...glass, background: "rgba(24,24,28,.84)", borderRadius: 44, padding: "30px 40px", ...enter(p, out, -40) }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", fontFamily: SANS }}>
        <span style={{ fontSize: 54, fontWeight: 800, letterSpacing: "-0.035em", color: INK }}>confidence on who I am</span>
        <span style={{ fontSize: 84, fontWeight: 900, color: GOLD, fontVariantNumeric: "tabular-nums" }}>{Math.round(q * 100)}%</span>
      </div>
      <div style={{ height: 30, borderRadius: 15, background: "rgba(255,255,255,.12)", marginTop: 18, overflow: "hidden" }}>
        <div style={{ width: `${q * 100}%`, height: "100%", borderRadius: 11, background: GOLD, boxShadow: `0 0 26px ${GOLD}` }} />
      </div>
      <div style={{ marginTop: 16, fontFamily: SERIF, fontStyle: "italic", fontSize: 100, color: GOLD, opacity: s, filter: `blur(${(1 - s) * 8}px)`, transform: `translateY(${(1 - s) * 12}px)` }}>so fucking high</div>
    </div>
  );
};

/** "sorry, I'm not sorry": an iOS toggle labelled with his word flips OFF on "not" */
const SorryToggle: React.FC<{ at: number; flip: number; until: number }> = ({ at: a, flip, until }) => {
  const { f, fps, p, out, on } = useWin(a, until);
  if (!on) return null;
  const q = f >= flip ? spring({ frame: f - flip, fps, config: NOB }) : 0;
  return (
    <div style={{ position: "absolute", top: 150, left: 64, right: 64, ...glass, background: "rgba(24,24,28,.84)", borderRadius: 44, padding: "30px 40px", display: "flex", alignItems: "center", justifyContent: "space-between", ...enter(p, out, -40) }}>
      <span style={{ fontFamily: q > 0.5 ? SERIF : SANS, fontStyle: q > 0.5 ? "italic" : "normal", fontWeight: q > 0.5 ? 400 : 800, fontSize: q > 0.5 ? 130 : 96, letterSpacing: "-0.02em", color: q > 0.5 ? GOLD : INK }}>{q > 0.5 ? "not sorry" : "sorry"}</span>
      <div style={{ width: 210, height: 126, borderRadius: 63, background: q > 0.5 ? "#3A3A3C" : "#34C759", position: "relative" }}>
        <div style={{ position: "absolute", top: 6, left: interpolate(q, [0, 1], [92, 8]), width: 110, height: 110, borderRadius: 55, background: "#fff", boxShadow: "0 4px 10px rgba(0,0,0,.35)" }} />
      </div>
    </div>
  );
};

/** "I know I'm better than you … not because I'm literally better … even though I am": two bars, me vs you */
const Bars: React.FC<{ from: number; up: number; level: number; snap: number; to: number }> = ({ from, up, level, snap, to }) => {
  const { f, fps, p, out, on } = useWin(from, to);
  if (!on) return null;
  const s1 = spring({ frame: f - up, fps, config: NOB }), s2 = spring({ frame: f - level, fps, config: NOB }), s3 = spring({ frame: f - snap, fps, config: { damping: 22, stiffness: 240 } });
  const me = 0.42 + 0.48 * s1 - 0.48 * s2 + 0.58 * s3, you = 0.42;
  const bar = (h: number, label: string, gold: boolean) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, width: 200 }}>
      <div style={{ height: 330, width: 200, display: "flex", alignItems: "flex-end" }}>
        <div style={{ width: "100%", height: `${Math.min(1, h) * 100}%`, borderRadius: 26, background: gold ? GOLD : "rgba(255,255,255,.28)", boxShadow: gold ? `0 0 40px ${GOLD}88` : "none" }} />
      </div>
      <span style={{ fontFamily: gold ? SERIF : SANS, fontStyle: gold ? "italic" : "normal", fontWeight: gold ? 400 : 800, fontSize: gold ? 96 : 66, color: gold ? GOLD : INK }}>{label}</span>
    </div>
  );
  return (
    <div style={{ position: "absolute", top: 70, left: 64, right: 64, ...glass, background: "rgba(24,24,28,.8)", borderRadius: 44, padding: "26px 40px 18px", display: "flex", justifyContent: "center", gap: 120, ...enter(p, out, -40) }}>
      {bar(me, "me", true)}{bar(you, "you", false)}
    </div>
  );
};

/** closing lines, centred big, his words */
const Closer: React.FC<{ at: number; until: number; pre: string; accent: string }> = ({ at: a, until, pre, accent }) => {
  const { p, out, on } = useWin(a, until);
  if (!on) return null;
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div style={{ marginTop: 170, textAlign: "center", ...enter(p, out, 30) }}>
        <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 110, letterSpacing: "-0.045em", color: INK, textShadow: "0 6px 30px rgba(0,0,0,.7)" }}>{pre} </span>
        <span style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 168, color: GOLD, textShadow: `0 0 40px ${GOLD}55, 0 6px 30px rgba(0,0,0,.7)` }}>{accent}</span>
      </div>
    </AbsoluteFill>
  );
};

/** engraving insert with a 5-frame blur-dissolve bridge in and a 4-frame one out (no white flash) */
const Insert: React.FC<{ src: string; from: number; to: number }> = ({ src, from, to }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [from, from + 5, to - 4, to], [0, 1, 1, 0], cl);
  const b = interpolate(f, [from, from + 5, to - 4, to], [14, 0, 0, 10], cl);
  return (
    <Sequence from={from} durationInFrames={to - from} layout="none">
      <AbsoluteFill style={{ opacity: o, filter: `blur(${b}px)` }}><OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%" }} /></AbsoluteFill>
    </Sequence>
  );
};

// hero words (behind the head; head covers < 30%): sans for the hard ones, serif gold for the identity words
const HERO = [
  { text: "gifted", at: A.gifted - 1, until: 851, serif: true, size: 250 },
  { text: "YOU", at: A.you1 - 1, until: A.cannot - 3, size: 380 },
  { text: "CANNOT", at: A.cannot - 1, until: A.because - 3, color: RED, size: 230 },
  { text: "CAN'T", at: A.cant - 1, until: cant1, color: RED, size: 300 },
  { text: "1,000", at: A.thousand - 1, until: A.jason - 4, color: RED, size: 290 },
  { text: "ego", at: A.high3 - 1, until: ego1 + 4, serif: true, size: 300 },
  { text: "ARROGANT", at: A.arrogant - 1, until: A.know - 2, size: 172 },
  { text: "superior", at: A.superior - 1, until: sup1, serif: true, size: 220 },
];
// caption accents (≈8%): italic serif gold, the Coop/dual-font captions
const ACC: Record<string, string> = { beat: GOLD, chosen: GOLD, god: GOLD, believes: GOLD, gifted: GOLD, better: GOLD, belief: GOLD, high: GOLD, confidence: GOLD, language: GOLD, ego: GOLD, bitch: RED, shit: RED };
const HIDE: [number, number][] = [
  [0, cold1], [A.iff - 2, speak1], [A.intel - 2, A.shout - 2], [A.confidence - 3, A.high2 + 12], [A.jason - 3, A.look - 2],
  [A.sorry - 2, A.yeah - 2], [A.know - 2, arr1], [pay0, INS[3].from], [A.make - 2, CUT + OUTRO],
  ...INS.map((i) => [i.from, i.to] as [number, number]),
  ...HERO.map((h) => [h.at - 1, h.until] as [number, number]),
];

const Sfx: React.FC<{ f: number; name: string; v?: number }> = ({ f, name, v = 0.6 }) => (
  <Sequence from={Math.max(0, Math.round(f))} durationInFrames={150} layout="none"><Audio src={staticFile(name)} volume={v} /></Sequence>
);
const S = {
  tritone: "sfx/ios/ios_tritone.wav", received: "sfx/ios/ios_received.wav", tink: "sfx/ios/ios_tink.wav", paid: "sfx/ios/ios_success.wav", key: "sfx/ios/ios_key.wav", lock: "sfx/ios/ios_lock.wav", note: "sfx/ios/ios_note.wav",
  whoosh: "sfx/whoosh.wav", swoosh: "sfx/swoosh.wav", pop: "sfx/pop.wav", click: "sfx/click.wav", typing: "sfx/typing.wav", riser: "sfx/pack3/riser.wav", hit: "sfx/ui/reverb_hit.wav",
  cine: "sfx/pack4/cinestrike.wav", crack: "sfx/pack4/basscrack.wav", neg: "sfx/ui/negative_glitch_1.wav", shine: "sfx/pack3/shine.wav", tape: "sfx/tapestop.wav",
  bass: "sfx/deep_bass.wav", shutter: "sfx/camera_shutter.wav", bell: "sfx/ding.wav", success: "sfx/ui/success_ui.wav", kaching: "sfx/kaching.wav",
};
const Sound: React.FC = () => {
  const cuts = EDL.slice(1).filter((e, i) => EDL[i].tag !== e.tag && e.speed === 1 && EDL[i].speed === 1).map((e) => e.f0);
  const slow = EDL.filter((e) => e.speed < 1).map((e) => e.f0);
  return (
    <>
      <Audio src={staticFile("ep/cut.mp4")} />
      {/* hook card: impact on frame 0, the loop opens on "chosen" */}
      <Sfx f={0} name={S.bass} v={0.55} />
      <Sfx f={A.beat - 1} name={S.cine} v={0.5} />
      <Sfx f={A.believes0 - 2} name={S.whoosh} v={0.3} />
      <Sfx f={A.chosen0 - 1} name={S.crack} v={0.5} />
      <Sfx f={A.chosen0} name={S.shine} v={0.45} />
      {/* checklist */}
      <Sfx f={A.iff - 2} name={S.note} v={0.5} />
      {[A.dick, A.six, A.amazing, A.handsome, A.real, A.speak].map((f) => <Sfx key={`t${f}`} f={f + 5} name={S.tink} v={0.8} />)}
      <Sfx f={A.language - 1} name={S.hit} v={0.4} />
      {/* translate */}
      <Sfx f={A.yo - 3} name={S.received} v={0.55} />
      <Sfx f={A.ni - 3} name={S.received} v={0.55} />
      {[A.yo, A.ni].map((f) => <Sfx key={`ty${f}`} f={f} name={S.typing} v={0.22} />)}
      <Sfx f={A.gifted - 1} name={S.shine} v={0.45} />
      {/* engraving cutaways: whoosh on the bridge, a tink on every landing, success on the payoff */}
      {INS.map((i) => <Sfx key={`w${i.from}`} f={i.from - 3} name={S.swoosh} v={0.35} />)}
      {INS.flatMap((i) => i.land.map((f) => <Sfx key={`l${f}`} f={f - 1} name={S.tink} v={0.85} />))}
      {INS.filter((i) => i.success).map((i) => <Sfx key={`s${i.success}`} f={i.success! - 1} name={S.paid} v={0.6} />)}
      <Sfx f={A.shout - 2} name={S.swoosh} v={0.35} />
      <Sfx f={A.you1 - 2} name={S.bass} v={0.5} />
      <Sfx f={A.cannot - 1} name={S.crack} v={0.45} />
      <Sfx f={A.confidence - 2} name={S.key} v={0.7} />
      <Sfx f={A.high2 - 2} name={S.success} v={0.45} />
      <Sfx f={A.cant - 1} name={S.cine} v={0.5} />
      <Sfx f={A.thousand - 1} name={S.crack} v={0.45} />
      {[A.jason, A.black, A.fucking].map((f) => <Sfx key={`n${f}`} f={f - 3} name={S.tritone} v={0.5} />)}
      <Sfx f={A.high3 - 1} name={S.cine} v={0.5} />
      <Sfx f={A.ego - 1} name={S.bass} v={0.45} />
      <Sfx f={A.sorry - 2} name={S.pop} v={0.4} />
      <Sfx f={A.not} name={S.lock} v={0.6} />
      <Sfx f={A.arrogant - 1} name={S.hit} v={0.45} />
      <Sfx f={A.better2 - 1} name={S.pop} v={0.4} />
      <Sfx f={A.literally} name={S.tape} v={0.4} />
      <Sfx f={A.am - 1} name={S.crack} v={0.5} />
      <Sfx f={A.superior - 1} name={S.shine} v={0.5} />
      <Sfx f={A.chosen1 - 1} name={S.tink} v={0.7} />
      {/* payoff: the hook card returns (callback) */}
      <Sfx f={A.how2 - 2} name={S.riser} v={0.3} />
      <Sfx f={A.beat2 - 1} name={S.cine} v={0.5} />
      <Sfx f={A.make - 2} name={S.pop} v={0.4} />
      <Sfx f={A.or - 1} name={S.click} v={0.4} />
      {slow.map((f) => <Sfx key={`sl${f}`} f={f - 2} name={S.whoosh} v={0.4} />)}
      <Sfx f={A.bitch - 1} name={S.bass} v={0.45} />
      <Sfx f={CUT + 20} name={S.pop} v={0.45} />
      <Sfx f={FLIP} name={S.bell} v={0.55} />
      {cuts.map((f) => <Sfx key={`sh${f}`} f={f - 1} name={S.shutter} v={0.14} />)}
    </>
  );
};

const hookWords = (o: number) => [
  { t: "how can you", at: A.how + o, size: 84 },
  { t: "beat", at: A.beat + o, serif: true, size: 150, br: true },
  { t: "a nigga that", at: A.nigga0 + o, size: 74, br: true },
  { t: "literally", at: A.nigga0 + 13 + o, size: 74 },
  { t: "believes", at: A.believes0 + o, serif: true, size: 104, br: true },
];

export const Episode: React.FC = () => (
  <AbsoluteFill style={{ background: "#000", fontFamily: SANS }}>
    <Video punches={[2, A.beat, A.dick, A.language, A.you1, A.cant, A.ego, A.am, A.beat2, A.bitch]}
      behind={HERO.map((h) => <Hero key={h.at} {...h} />)} fgRanges={HERO.map((h) => [h.at - 2, h.until] as [number, number])} />
    {/* 0 — hook card: open loop */}
    <HookCard from={0} to={cold1} words={[...hookWords(0),
      { t: "he is", at: A.he0, size: 74, br: true }, { t: "chosen", at: A.chosen0, serif: true, size: 170, br: true }, { t: "by God himself.", at: A.god0 - 6, size: 74, br: true }]} />
    {/* 1 — if you want to be like me */}
    <Checklist from={A.iff - 2} to={lang0} items={[{ t: "fat ass dick", at: A.dick }, { t: "6'5\"", at: A.six, serif: true }, { t: "amazing", at: A.amazing }, { t: "handsome", at: A.handsome, serif: true }]} />
    <Translate from={lang0} to={lang1} cards={[
      { at: A.yo - 2, until: A.ni - 3, lang: "Spanish", text: "Yo hablo mucho español, pinche negrito, wey.", en: "I speak a lot of Spanish, damn negrito, bro." },
      { at: A.ni - 2, until: lang1, lang: "Chinese (Mandarin)", text: "你叫什么名字？我叫欧杰。", en: "What’s your name? My name is Ou Jie.", cjk: true },
    ]} />
    <Checklist from={speak0} to={speak1} items={[{ t: "fat ass dick", at: speak0 - 40 }, { t: "6'5\"", at: speak0 - 40, serif: true }, { t: "amazing · handsome", at: speak0 - 40 },
      { t: "real ass nigga", at: A.real }, { t: "any fucking language", at: A.speak, serif: true }]} />
    {/* 2 — gifted, the shout-out */}
    <Sent at={A.shout - 2} until={972} text="shout out to my nigga Tate 🫡" />
    {/* 3 — confidence, can't tell me shit */}
    <Meter from={A.confidence - 4} fill={A.confidence + 2} sub={A.high2 - 2} to={A.cant - 2} />
    {/* 4 — the room: insults land as messages; then his look (the one deliberate hold) */}
    <div style={{ position: "absolute", inset: 0, transform: "scale(1.6)", transformOrigin: "50% 0%" }}>
      <NotificationStack until={A.look - 2} items={[
        { app: "messages", title: "Unknown", body: "Jason, you’re a bitch", at: A.jason - 3 },
        { app: "messages", title: "Unknown", body: "you’re so black and ugly", at: A.black - 3 },
        { app: "messages", title: "Unknown", body: "and you’re a fucking nigga", at: A.fucking - 3 },
      ]} />
    </div>
    {/* 5 — arrogant */}
    <SorryToggle at={A.sorry - 2} flip={A.not} until={A.yeah - 2} />
    <Bars from={A.know - 2} up={A.better2} level={A.literally} snap={A.am} to={arr1} />
    {/* 6 — payoff: the hook card returns, then the engraving closes the loop */}
    <HookCard from={pay0} to={INS[3].from + 3} words={hookWords(pay0 - 0 + (A.how2 - pay0) - A.how)} />
    {INS.map((i) => <Insert key={i.src} {...i} />)}
    <Closer at={A.make - 2} until={A.or - 2} pre="make it make" accent="sense." />
    <Closer at={A.or - 2} until={A.have - 2} pre="or" accent="don’t." />
    <Closer at={A.have - 2} until={CUT} pre="have a," accent="bitch." />
    <CoopCaptions accents={ACC} hide={HIDE} top={1460} />
    <FollowCard flipAt={FLIP} />
    <Sound />
  </AbsoluteFill>
);
