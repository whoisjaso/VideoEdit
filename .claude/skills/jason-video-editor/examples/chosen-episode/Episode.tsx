/**
 * EPISODE #5 "Chosen" — beat sheet. Structure kept from the 8.3 template; beats replaced.
 * Cold open = the payoff line. Engraving cutaways (ENGRAVING CUTAWAYS rule) on the definitions, the big idea and the payoff,
 * rendered as motion-blurred 30 fps inserts from ../../ins (pure seek(t) HTML engine) and cut in on his sentence boundaries.
 */
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import "@fontsource/nunito-sans/600.css";
import "@fontsource/nunito-sans/900.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import { Captions } from "../lib/Captions";
import { FollowCard, PopRow } from "../lib/Graphics";
import { HeroWord, R, Y, glass } from "../lib/Ios";
import { HeightTag, Meter } from "../lib/Mg";
import { NotificationStack } from "../lib/IosNotify";
import { at, CUT, EDL, sec } from "./timeline";
import { Video } from "../lib/Video";

export const OUTRO = 150;
const FLIP = CUT + 100;
const A = {
  beat: at("cold", "BEAT"), chosen0: at("cold2", "CHOSEN"),
  dick: at("hook", "DICK"), six: at("hook", "SIX"), amazing: at("hook", "AMAZING,"), handsome: at("hook", "HANDSOME,"),
  yo: at("lang", "YO"), ni: at("lang", "NI"), language: at("speak", "LANGUAGE."),
  gifted: at("gifted", "GIFTED."), shout1: at("gifted", "SHOUT", 1), shout2: at("gifted", "SHOUT", 2),
  better: at("belief", "BETTER", 1), cannot: at("belief", "CANNOT"), because: at("belief", "BECAUSE"),
  confidence: at("confidence", "CONFIDENCE"), high2: at("confidence", "HIGH."), shit1: at("confidence", "SHIT.", 1), shit2: at("confidence", "SHIT.", 2),
  thousand: at("room", "THOUSAND"), jason: at("room", "JASON,"), black: at("room", "BLACK"), fucking: at("room", "FUCKING"), look: at("room", "LOOK"),
  high3: at("ego", "HIGH"), ego: at("ego", "EGO."),
  sorry: at("arrogant", "SORRY,"), arrogant: at("arrogant", "ARROGANT"), am: at("arrogant", "AM."), superior: at("arrogant", "SUPERIOR"), chosen1: at("arrogant", "CHOSEN"),
  beat2: at("payoff", "BEAT"), believes: at("payoff", "BELIEVES"), make: at("payoff2", "MAKE", 1), bitch: at("payoff2", "BITCH."),
};
const [, cold1] = sec("cold2"), [lang0, lang1] = sec("lang"), [speak0] = sec("speak"), [, conf1] = sec("confidence"), [room0, room1] = sec("room"), [, arr1] = sec("arrogant");

// engraving inserts: [file, from, to, landings (episode frames)]
const INS: { src: string; from: number; to: number; land: number[]; success?: number }[] = [
  { src: "ep/ins_persp.mp4", from: 928, to: 995, land: [949] },
  { src: "ep/ins_indef.mp4", from: 1046, to: 1110, land: [1064] },
  { src: "ep/ins_high.mp4", from: 1282, to: 1452, land: [1297, 1362, 1439] },
  { src: "ep/ins_chosen.mp4", from: 2573, to: 2789, land: [2587, 2665, 2693, 2740], success: 2764 },
];

const HERO = [
  { text: "CHOSEN", at: A.chosen0 - 1, until: cold1 - 2, color: Y, size: 230, top: 140 },
  { text: "GIFTED", at: A.gifted - 1, until: 926, color: Y, size: 250, top: 140 },
  { text: "CANNOT", at: A.cannot - 1, until: A.because - 3, color: R, size: 240, top: 140 },
  { text: "1,000", at: A.thousand - 1, until: A.jason - 4, color: R, size: 280, top: 140 },
  { text: "EGO", at: A.ego - 2, until: A.ego + 26, color: Y, size: 320, top: 140 },
  { text: "ARROGANT", at: A.arrogant - 1, until: A.arrogant + 34, color: Y, size: 170, top: 140 },
];
const HIDE: [number, number][] = [
  [A.six - 1, lang0], [lang0, lang1], [A.confidence - 2, A.high2 + 12], [A.jason - 2, A.look - 2], [A.superior - 1, A.chosen1 - 1], [CUT, CUT + OUTRO],
  ...INS.map((i) => [i.from, i.to] as [number, number]),
  ...HERO.map((h) => [h.at - 1, h.until] as [number, number]),
];

/** iOS Translate-style card: original line, then the English underneath */
const Translate: React.FC<{ from: number; to: number; cards: { at: number; lang: string; text: string; en: string; cjk?: boolean }[] }> = ({ from, to, cards }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from - 1 || f >= to) return null;
  const out = interpolate(f, [to - 8, to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shown = cards.filter((c) => f >= c.at - 1);
  return (
    <div style={{ position: "absolute", top: 110, left: 60, right: 60, display: "flex", flexDirection: "column", gap: 22, opacity: out }}>
      {shown.map((c, i) => {
        const p = spring({ frame: f - c.at, fps, config: { damping: 30, stiffness: 210 } });
        const q = spring({ frame: f - c.at - 16, fps, config: { damping: 30, stiffness: 210 } });
        const old = i < shown.length - 1;
        return (
          <div key={c.at} style={{ ...glass, borderRadius: 40, padding: "26px 34px", opacity: p * (old ? 0.55 : 1), filter: `blur(${(1 - p) * 14}px)`, transform: `scale(${0.96 + 0.04 * p}) translateY(${(1 - p) * -30}px)` }}>
            <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "0.08em", color: "rgba(255,255,255,.55)" }}>{c.lang.toUpperCase()}</div>
            <div style={{ fontSize: 50, fontWeight: 800, color: "#fff", lineHeight: 1.2, marginTop: 6, fontFamily: c.cjk ? "'WenQuanYi Zen Hei', Inter" : "Inter" }}>{c.text}</div>
            <div style={{ height: 2, background: "rgba(255,255,255,.15)", margin: "18px 0 14px", transform: `scaleX(${q})`, transformOrigin: "0 50%" }} />
            <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "0.08em", color: "#0A84FF", opacity: q }}>ENGLISH</div>
            <div style={{ fontSize: 44, fontWeight: 600, color: "#0A84FF", lineHeight: 1.2, marginTop: 6, opacity: q, filter: `blur(${(1 - q) * 6}px)` }}>{c.en}</div>
          </div>
        );
      })}
    </div>
  );
};

const Sfx: React.FC<{ f: number; name: string; v?: number }> = ({ f, name, v = 0.6 }) => (
  <Sequence from={Math.max(0, Math.round(f))} durationInFrames={150} layout="none"><Audio src={staticFile(name)} volume={v} /></Sequence>
);
const S = {
  tritone: "sfx/ios/ios_tritone.wav", received: "sfx/ios/ios_received.wav", tink: "sfx/ios/ios_tink.wav", paid: "sfx/ios/ios_success.wav", key: "sfx/ios/ios_key.wav",
  whoosh: "sfx/whoosh.wav", swoosh: "sfx/swoosh.wav", pop: "sfx/pop.wav", click: "sfx/click.wav", typing: "sfx/typing.wav", riser: "sfx/pack3/riser.wav", hit: "sfx/ui/reverb_hit.wav",
  cine: "sfx/pack4/cinestrike.wav", crack: "sfx/pack4/basscrack.wav", neg: "sfx/ui/negative_glitch_1.wav", shine: "sfx/pack3/shine.wav",
  bass: "sfx/deep_bass.wav", shutter: "sfx/camera_shutter.wav", bell: "sfx/ding.wav", success: "sfx/ui/success_ui.wav",
};
const Sound: React.FC = () => {
  const cuts = EDL.slice(1).filter((e, i) => EDL[i].tag !== e.tag && e.speed === 1 && EDL[i].speed === 1).map((e) => e.f0);
  const slow = EDL.filter((e) => e.speed < 1).map((e) => e.f0);
  return (
    <>
      <Audio src={staticFile("ep/cut.mp4")} />
      {/* cold open: hit on frame 1, CHOSEN lands */}
      <Sfx f={0} name={S.bass} v={0.5} />
      <Sfx f={A.beat - 1} name={S.whoosh} v={0.3} />
      <Sfx f={A.chosen0 - 1} name={S.cine} v={0.5} />
      {/* hook: height tag + checks */}
      <Sfx f={A.six} name={S.pop} v={0.45} />
      <Sfx f={A.amazing} name={S.tink} v={0.8} />
      <Sfx f={A.handsome} name={S.tink} v={0.8} />
      {/* languages: a received message per card */}
      <Sfx f={A.yo - 1} name={S.received} v={0.55} />
      <Sfx f={A.ni - 1} name={S.received} v={0.55} />
      <Sfx f={A.language - 1} name={S.hit} v={0.4} />
      <Sfx f={A.gifted - 1} name={S.shine} v={0.45} />
      {/* engraving cutaways: iOS only, a tink on every landing, success on the payoff */}
      {INS.flatMap((i) => i.land.map((f) => <Sfx key={`l${f}`} f={f - 1} name={S.tink} v={0.85} />))}
      {INS.filter((i) => i.success).map((i) => <Sfx key={`s${i.success}`} f={i.success! - 1} name={S.paid} v={0.6} />)}
      <Sfx f={A.cannot - 1} name={S.neg} v={0.3} />
      <Sfx f={A.confidence} name={S.key} v={0.7} />
      <Sfx f={A.high2 - 2} name={S.success} v={0.4} />
      <Sfx f={A.shit2 - 2} name={S.whoosh} v={0.4} />
      <Sfx f={A.thousand - 1} name={S.crack} v={0.45} />
      {[A.jason, A.black, A.fucking].map((f) => <Sfx key={`n${f}`} f={f - 3} name={S.tritone} v={0.5} />)}
      <Sfx f={A.ego - 2} name={S.cine} v={0.5} />
      <Sfx f={A.arrogant - 1} name={S.hit} v={0.4} />
      <Sfx f={A.superior - 1} name={S.shine} v={0.45} />
      <Sfx f={A.believes - 40} name={S.riser} v={0.3} />
      <Sfx f={A.beat2 - 1} name={S.whoosh} v={0.3} />
      {slow.map((f) => <Sfx key={`sl${f}`} f={f - 2} name={S.whoosh} v={0.4} />)}
      <Sfx f={CUT + 40} name={S.pop} v={0.45} />
      <Sfx f={FLIP} name={S.bell} v={0.55} />
      {cuts.map((f) => <Sfx key={`sh${f}`} f={f - 1} name={S.shutter} v={0.16} />)}
    </>
  );
};

export const Episode: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Video punches={[2, A.beat, A.dick, A.language, A.shit1, A.ego, A.am, A.beat2]}
      behind={HERO.map((h) => <HeroWord key={h.at} {...h} />)} fgRanges={HERO.map((h) => [h.at - 2, h.until] as [number, number])} />
    <HeightTag at={A.six - 2} until={lang0} text={"6'5\""} />
    <PopRow items={[{ label: "AMAZING", at: A.amazing }, { label: "HANDSOME", at: A.handsome }]} until={lang0} column top={1180} />
    <Translate from={lang0} to={speak0 + 4} cards={[
      { at: A.yo - 2, lang: "Spanish", text: "Yo hablo mucho español, pinche negrito, wey.", en: "I speak a lot of Spanish, damn negrito, bro." },
      { at: A.ni - 2, lang: "Chinese (Mandarin)", text: "你叫什么名字？我叫欧杰。", en: "What’s your name? My name is Ou Jie.", cjk: true },
    ]} />
    <Meter from={A.confidence - 4} fill={A.confidence + 4} sub={A.high2 - 2} to={A.high2 + 14} label="Confidence on who I am" subLabel="so fucking high" />
    <div style={{ position: "absolute", inset: 0, transform: "scale(1.55)", transformOrigin: "50% 0%" }}><NotificationStack until={A.look - 2} items={[
      { app: "messages", title: "Unknown", body: "Jason, you’re a bitch", at: A.jason - 3 },
      { app: "messages", title: "Unknown", body: "you’re so black and ugly", at: A.black - 3 },
      { app: "messages", title: "Unknown", body: "and you’re a fucking nigga", at: A.fucking - 3 },
    ]} /></div>
    <PopRowSuperior at={A.superior - 1} until={A.chosen1 - 1} />
    {INS.map((i) => (
      <Sequence key={i.src} from={i.from} durationInFrames={i.to - i.from} layout="none">
        <AbsoluteFill><OffthreadVideo src={staticFile(i.src)} muted style={{ width: "100%", height: "100%" }} /></AbsoluteFill>
      </Sequence>
    ))}
    <Captions hide={HIDE} />
    <FollowCard flipAt={FLIP} />
    <Sound />
  </AbsoluteFill>
);

/** "superior": one gold word card */
const PopRowSuperior: React.FC<{ at: number; until: number }> = ({ at, until }) => (
  <PopRow items={[{ label: "SUPERIOR", at }]} until={until} check={false} top={1180} />
);
