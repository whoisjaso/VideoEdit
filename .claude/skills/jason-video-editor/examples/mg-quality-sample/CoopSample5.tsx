/**
 * MG v5 — episode #4's first 27 s rebuilt in the Coop preset look (decoded from Jason Cooperson, sGt1ACELN4k).
 * Face ↔ full-screen hard cutaways, alternating; graphics at 12 fps with glow + grain; lowercase captions with one
 * italic-serif accent word; warm "autumn" camera grade on footage only (never on graphics); every cue timed to his words.
 */
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { Video } from "../lib/Video";
import { BigX, C, Comments, CoopCaptions, Cutaway, Equation, Grain, PixelMeter, Segmented, Toggle } from "../lib/Coop";
import { at } from "./timeline";

const A = {
  perceived: at("cold", "PERCEIVED"), actually: at("cold", "ACTUALLY"), shame: at("potential", "SHAME"),
  potential: at("potential", "POTENTIAL"), successful: at("potential", "SUCCESSFUL"), influential: at("potential", "INFLUENTIAL"),
  but: at("opinions", "BUT"), scared: at("opinions", "SCARED"), opinions: at("opinions", "OPINIONS"), nobody: at("opinions", "NOBODY"),
  you: at("opinions", "YOU", 2), rewire: at("opinions", "REWIRE"), every: at("broke", "EVERY"),
};
export const V5_LEN = A.every;

// cutaway windows [from, to) — face in between every one of them
const CUTS = {
  nice: [A.perceived - 4, A.actually + 34],
  meter: [A.potential - 3, A.potential + 45],
  eq: [A.influential - 12, A.but],
  comments: [A.opinions - 5, A.nobody - 4],
  x: [A.nobody - 4, A.you - 4],
  toggle: [A.rewire - 6, A.every],
} as const;
const HIDE = Object.values(CUTS).map(([a, b]) => [a, b] as [number, number]);
const ACCENTS: Record<string, string> = { shame: C.red, potential: C.gold, successful: C.green, influential: C.gold, scared: C.red, opinions: C.red, rewire: C.gold, mindset: C.gold };

const Sfx: React.FC<{ f: number; name: string; v?: number }> = ({ f, name, v = 0.5 }) => (
  <Sequence from={Math.max(0, Math.round(f))} durationInFrames={120} layout="none"><Audio src={staticFile(`sfx/${name}`)} volume={v} /></Sequence>
);
const Sound: React.FC = () => (
  <>
    <Audio src={staticFile("ep/cut.mp4")} />
    {/* every hard cut into a graphic gets a whoosh 1-2 frames early; every cut back to the face a soft swoosh */}
    {Object.values(CUTS).map(([a]) => <Sfx key={`w${a}`} f={a - 2} name="whoosh.wav" v={0.28} />)}
    {[CUTS.nice[1], CUTS.meter[1], CUTS.eq[1], CUTS.x[1]].map((b) => <Sfx key={`s${b}`} f={b - 1} name="swoosh.wav" v={0.16} />)}
    {/* nice: thumb slides to "actually", the strike draws */}
    <Sfx f={A.actually - 1} name="ios/ios_tink.wav" v={0.8} />
    <Sfx f={A.actually + 4} name="ui/success_ui.wav" v={0.35} />
    {/* potential: pixels fill with a counter, land with a shine */}
    <Sfx f={A.potential + 2} name="pack3/counter.wav" v={0.4} />
    <Sfx f={A.potential + 32} name="pack3/shine.wav" v={0.45} />
    {/* influential: arrow draws, gold tile lands */}
    <Sfx f={A.influential - 8} name="swoosh.wav" v={0.3} />
    <Sfx f={A.influential - 1} name="ios/ios_success.wav" v={0.5} />
    {/* opinions: each comment arrives */}
    {[0, 8, 16, 24].map((d) => <Sfx key={`c${d}`} f={A.opinions + d - 1} name="ios/ios_received.wav" v={0.32} />)}
    {/* nobody: the X */}
    <Sfx f={A.nobody - 1} name="pack4/basscrack.wav" v={0.5} />
    <Sfx f={A.nobody} name="ui/negative_glitch_1.wav" v={0.25} />
    {/* rewire: toggle off */}
    <Sfx f={A.rewire - 1} name="ios/ios_tink.wav" v={0.9} />
    <Sfx f={A.rewire + 6} name="pack3/shine.wav" v={0.35} />
  </>
);

const L = (k: keyof typeof CUTS, f: number) => f - CUTS[k][0]; // global frame -> frame inside that cutaway

export const V5: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Video punches={[3, A.shame, A.scared]} look="saturate(1.2) contrast(1.06) sepia(0.12) brightness(1.01)" />
    {/* autumn warmth on the footage only: warm soft-light wash + a gentle cool lift in the shadows */}
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(255,170,90,.10), rgba(255,120,60,.06))", mixBlendMode: "soft-light" }} />
    <Grain o={0.06} />
    <CoopCaptions accents={ACCENTS} hide={HIDE} />

    <Cutaway from={CUTS.nice[0]} to={CUTS.nice[1]}><Segmented label="what you prioritize" a="perceived" b="actually" flip={L("nice", A.actually)} /></Cutaway>
    <Cutaway from={CUTS.meter[0]} to={CUTS.meter[1]}><PixelMeter label="potential" pct={92} fill={L("meter", A.potential)} /></Cutaway>
    <Cutaway from={CUTS.eq[0]} to={CUTS.eq[1]}><Equation pre="not only" a="successful" b="influential" at={0} bt={L("eq", A.influential)} /></Cutaway>
    <Cutaway from={CUTS.comments[0]} to={CUTS.comments[1]}>
      <Comments app="Comments" items={[
        { user: "realtalk_99", text: "who does he think he is 😂", at: L("comments", A.opinions), hue: 10 },
        { user: "kev.o", text: "bro thinks he’s somebody", at: L("comments", A.opinions + 8), hue: 200 },
        { user: "nae2x", text: "that’s corny", at: L("comments", A.opinions + 16), hue: 290 },
        { user: "j_marcus", text: "nobody asked", at: L("comments", A.opinions + 24), hue: 120 },
      ]} />
    </Cutaway>
    <Cutaway from={CUTS.x[0]} to={CUTS.x[1]}><BigX at={L("x", A.nobody)} pre="nobody gives a" accent="fuck" /></Cutaway>
    <Cutaway from={CUTS.toggle[0]} to={CUTS.toggle[1]}><Toggle label="Care what others think" flip={L("toggle", A.rewire)} pre="rewire your" accent="mindset" /></Cutaway>
    <Sound />
  </AbsoluteFill>
);
