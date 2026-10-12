/**
 * EPISODE #4 "Perceived as nice" — beat sheet. Built on the 8.3 recipe (episode #3 structure).
 *   A = every word a graphic or sound hits, via at(section, WORD, n)   (never hard-coded frames)
 *   HERO = 4 hero words behind his head  |  HIDE = caption windows a graphic already says  |  TOPS = caption height
 *   Sound = one line per event, real iOS sounds 1:1  |  graphics from ../lib/Mg in spoken order  |  FollowCard last
 */
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import "@fontsource/nunito-sans/600.css";
import "@fontsource/nunito-sans/900.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import { Captions, PAGES } from "../lib/Captions";
import { FollowCard } from "../lib/Graphics";
import { HeroWord, R, Y } from "../lib/Ios";
import { Banner, BannerStack, BrokeHater, CommentRain, HeightTag, LetGo, Meter, NewCity, NiceSplit, Notes, PostUpload, SameWeek, SettingToggle, Tiles } from "../lib/Mg";
import { at, CUT, EDL, sec } from "./timeline";
import { Video } from "../lib/Video";

export const OUTRO = 120;
const FLIP = CUT + 62;

const A = {
  perceived0: at("cold", "PERCEIVED"), actually0: at("cold", "ACTUALLY"),
  see: at("potential", "SEE", 1), potential: at("potential", "POTENTIAL"), influential: at("potential", "INFLUENTIAL"),
  opinions: at("opinions", "OPINIONS"), nobody: at("opinions", "NOBODY"), rewire: at("opinions", "REWIRE"),
  talks: at("broke", "TALKS"), broke1: at("broke", "BROKE", 1), think: at("broke", "THINK"), talk: at("broke", "TALK"), broke3: at("broke", "BROKE", 3),
  six1: at("sixfive", "SIX-FIVE", 1), laugh1: at("sixfive", "LAUGH"), six2: at("sixfive", "SIX-FIVE", 2),
  female: at("female", "FEMALE"), your: at("female", "YOUR"), imaLaugh: at("female", "I'MA"), because: at("female", "BECAUSE"), know: at("female", "KNOW"), belief1: at("female", "BELIEF"),
  niggas: at("yapping", "NIGGAS", 1), got: at("yapping", "GOT"), money: at("yapping", "MONEY"), fuckY: at("yapping", "FUCK"), brokeY: at("yapping", "BROKE"),
  influential2: at("believe", "INFLUENTIAL"), speak: at("believe", "SPEAK"), funny: at("believe", "FUNNY"), but: at("believe", "BUT"), belief2: at("believe", "BELIEF"), so: at("believe", "SO"),
  script1: at("script", "SCRIPT", 1), script2: at("script", "SCRIPT", 2), nigga: at("script", "NIGGA"), state: at("script", "STATE"), city: at("script", "CITY"), script3: at("script", "SCRIPT", 3), you3: at("script", "YOU", 5),
  stop: at("appearance", "STOP"),
  khamani: at("nice", "KHAMANI"), aNice: at("nice", "PRIORITIZE"), perceived: at("nice", "PERCEIVED"), actually: at("nice", "ACTUALLY"), andN: at("nice", "AND", 2),
  sister: at("nice", "SISTER"), mom: at("nice", "MOM"), dad: at("nice", "DAD"), brother: at("nice", "BROTHER"), no: at("nice", "NO", 2), butN: at("nice", "BUT", 1),
  somebody: at("nice", "SOMEBODY"), hey: at("nice", "HEY"), you: at("nice", "YOU", 3), yes: at("nice", "YES"), not: at("nice", "NOT"),
  whatever: at("ego", "WHATEVER"), want: at("ego", "WANT", 3), doE: at("ego", "DO", 2), beliefs: at("ego", "BELIEFS"), andE: at("ego", "AND", 2), ego: at("ego", "EGO"), let: at("ego", "LET"), youre: at("ego", "YOU'RE", 2),
  post: at("post", "POST"), fuckP: at("post", "FUCK"), broke5: at("post", "BROKE", 1), broke6: at("post", "BROKE", 2),
};
const [, cold1] = sec("cold"), [opin0] = sec("opinions"), [broke0] = sec("broke"), [six0] = sec("sixfive"), [fem0] = sec("female"), [yap0] = sec("yapping");
const [bel0] = sec("believe"), [scr0] = sec("script"), [app0] = sec("appearance"), [nice0] = sec("nice"), [ego0] = sec("ego"), [post0] = sec("post");

const HERO = [
  { text: "BROKE", at: A.broke3 - 1, until: A.broke3 + 42, color: R, size: 230, top: 615 },
  { text: "BELIEF", at: A.belief2 - 1, until: A.so - 2, color: Y, size: 215, top: 690 },
  { text: "SCRIPT", at: A.script3 - 1, until: A.you3 + 4, color: Y, size: 210, top: 675 },
  { text: "EGO", at: A.ego - 1, until: A.let - 2, color: R, size: 300, top: 620 },
];
// captions hide while a graphic already carries those words (never show the same words twice)
const HIDE: [number, number][] = [
  [A.perceived0 - 1, cold1], [A.influential - 1, opin0], [A.influential2 - 1, A.but], [A.perceived - 1, A.andN], [A.no - 1, A.butN], [A.hey - 1, A.you], [A.let - 1, A.youre], [CUT, CUT + OUTRO],
  ...HERO.map((h) => [h.at - 1, h.until] as [number, number]),
];
const TOPS: [number, number, number][] = [[0, CUT, 1440]];

const Sfx: React.FC<{ f: number; name: string; v?: number }> = ({ f, name, v = 0.6 }) => (
  <Sequence from={Math.max(0, Math.round(f))} durationInFrames={150} layout="none"><Audio src={staticFile(name)} volume={v} /></Sequence>
);
const S = {
  tritone: "sfx/ios/ios_tritone.wav", received: "sfx/ios/ios_received.wav", tink: "sfx/ios/ios_tink.wav", paid: "sfx/ios/ios_success.wav", key: "sfx/ios/ios_key.wav", note: "sfx/ios/ios_note.wav",
  whoosh: "sfx/whoosh.wav", swoosh: "sfx/swoosh.wav", pop: "sfx/pop.wav", click: "sfx/click.wav", typing: "sfx/typing.wav", riser: "sfx/pack3/riser.wav", hit: "sfx/ui/reverb_hit.wav",
  cine: "sfx/pack4/cinestrike.wav", crack: "sfx/pack4/basscrack.wav", neg: "sfx/ui/negative_glitch_1.wav", data: "sfx/ui/data_loading.wav", shine: "sfx/pack3/shine.wav", tape: "sfx/tapestop.wav",
  bass: "sfx/deep_bass.wav", shutter: "sfx/camera_shutter.wav", bell: "sfx/ding.wav", success: "sfx/ui/success_ui.wav", counter: "sfx/pack3/counter.wav",
};
const Sound: React.FC = () => {
  const starts = PAGES.filter((p, i) => i === 0 || p.words[0].k !== PAGES[i - 1].words[0].k).map((p) => p.from);
  const cuts = EDL.slice(1).filter((e, i) => EDL[i].tag !== e.tag).map((e) => e.f0); // shutter only on section changes
  return (
    <>
      <Audio src={staticFile("ep/cut.mp4")} />
      {/* cold open: hit on frame 3 (motion in the first 15 frames), then the split lands */}
      <Sfx f={2} name={S.cine} v={0.4} />
      <Sfx f={2} name={S.whoosh} v={0.3} />
      <Sfx f={A.perceived0 - 2} name={S.cine} v={0.5} />
      <Sfx f={A.actually0 - 1} name={S.pop} v={0.5} />
      <Sfx f={A.actually0 + 1} name={S.success} v={0.4} />
      {/* potential meter */}
      <Sfx f={A.potential} name={S.counter} v={0.45} />
      <Sfx f={A.influential - 1} name={S.paid} v={0.5} />
      {/* opinions rain → freeze → toggle off */}
      {[0, 7, 14, 22].map((d) => <Sfx key={`o${d}`} f={A.opinions + d} name={S.received} v={0.35} />)}
      <Sfx f={A.nobody} name={S.tape} v={0.45} />
      <Sfx f={A.rewire + 8} name={S.tink} v={0.9} />
      {/* hater comment → broke balance */}
      <Sfx f={A.talks - 2} name={S.tritone} v={0.5} />
      <Sfx f={A.broke1} name={S.neg} v={0.35} />
      <Sfx f={A.talk - 2} name={S.received} v={0.45} />
      <Sfx f={A.broke3 - 1} name={S.crack} v={0.5} />
      {/* 6'5" */}
      <Sfx f={A.six1 - 2} name={S.whoosh} v={0.35} />
      <Sfx f={A.six1 + 8} name={S.shine} v={0.5} />
      {/* her message → I know who I am */}
      <Sfx f={A.your - 2} name={S.received} v={0.6} />
      <Sfx f={A.know - 2} name={S.note} v={0.5} />
      <Sfx f={A.belief1} name={S.typing} v={0.35} />
      {/* yapping comment → money */}
      <Sfx f={A.niggas - 2} name={S.tritone} v={0.5} />
      <Sfx f={A.money - 2} name={S.paid} v={0.6} />
      <Sfx f={A.brokeY} name={S.neg} v={0.3} />
      {/* you are… tiles */}
      {[A.influential2, A.speak, A.funny].map((f) => [<Sfx key={`p${f}`} f={f - 1} name={S.pop} v={0.45} />, <Sfx key={`c${f}`} f={f + 1} name={S.click} v={0.35} />])}
      <Sfx f={A.belief2 - 1} name={S.cine} v={0.5} />
      {/* script: same week → new city → SCRIPT */}
      <Sfx f={A.script2 - 4} name={S.whoosh} v={0.35} />
      <Sfx f={A.state - 14} name={S.swoosh} v={0.45} />
      <Sfx f={A.city} name={S.success} v={0.45} />
      <Sfx f={A.script3 - 1} name={S.crack} v={0.45} />
      {/* Khamani → split callback → family "no" → stranger → yes */}
      <Sfx f={A.khamani - 2} name={S.tritone} v={0.5} />
      <Sfx f={A.perceived - 2} name={S.cine} v={0.45} />
      <Sfx f={A.actually - 1} name={S.pop} v={0.5} />
      {[A.sister, A.mom, A.dad, A.brother].map((f) => <Sfx key={`fam${f}`} f={f - 2} name={S.tritone} v={0.4} />)}
      <Sfx f={A.hey - 2} name={S.received} v={0.6} />
      <Sfx f={A.yes - 2} name={S.paid} v={0.5} />
      {/* doing it for them → EGO → let it go */}
      {[A.whatever, A.want, A.doE].map((f) => <Sfx key={`n${f}`} f={f} name={S.typing} v={0.35} />)}
      <Sfx f={A.beliefs} name={S.neg} v={0.35} />
      <Sfx f={A.ego - 1} name={S.crack} v={0.55} />
      <Sfx f={A.ego - 1} name={S.bass} v={0.5} />
      <Sfx f={A.let} name={S.shine} v={0.5} />
      {/* just post */}
      <Sfx f={A.post - 6} name={S.data} v={0.3} />
      <Sfx f={A.post + 24} name={S.success} v={0.5} />
      <Sfx f={A.broke6 - 1} name={S.cine} v={0.5} />
      {/* outro */}
      <Sfx f={CUT + 18} name={S.pop} v={0.45} />
      <Sfx f={FLIP} name={S.bell} v={0.55} />
      {cuts.map((f) => <Sfx key={`sh${f}`} f={f - 1} name={S.shutter} v={0.18} />)}
      {starts.map((f) => <Sfx key={`ty${f}`} f={f} name={S.typing} v={0.08} />)}
    </>
  );
};

const IG = { logo: "instagram", color: "#fff", logoBg: "#D62976" };
const MSG = { logo: "imessage", color: "#34DA50", logoBg: "#34DA50", app: "MESSAGES" };

export const Episode: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Video punches={[3, A.rewire, A.broke3, A.laugh1, A.money, A.belief2, A.city, A.stop, A.ego, A.broke6]}
      behind={HERO.map((h) => <HeroWord key={h.at} {...h} />)} fgRanges={HERO.map((h) => [h.at - 2, h.until] as [number, number])} />
    {/* 0 — cold open: perceived nice vs actually nice */}
    <NiceSplit from={A.perceived0 - 4} perceived={A.perceived0} actually={A.actually0} to={cold1} />
    {/* 1 — potential */}
    <Meter from={A.see - 4} fill={A.potential} sub={A.influential} to={opin0} label="Your potential" subLabel="Influential" />
    {/* 2 — opinions of others → nobody cares → rewire */}
    <CommentRain from={A.opinions - 2} freeze={A.nobody} to={A.rewire - 4} comments={["who does he think he is 😂", "bro thinks he’s somebody", "that’s corny", "nobody asked", "he’s capping 🧢", "cringe"]} />
    <SettingToggle at={A.rewire - 6} flip={A.rewire + 8} until={broke0} label="Care what others think" />
    {/* 3 — the people talking shit are broke */}
    <BrokeHater comment={A.talks - 2} broke={A.broke1} to={A.think - 2} text="bro thinks he’s him 😂" />
    <Banner at={A.talk - 2} until={A.broke3 - 2} {...IG} app="INSTAGRAM" title="3 new comments" body="about your last post" />
    {/* 4 — I'm six-five */}
    <HeightTag at={A.six1 - 2} until={fem0} text={"6’5”"} />
    {/* 5 — a female says it → I know who I am */}
    <Banner at={A.your - 2} until={A.imaLaugh + 14} {...MSG} title="Her 👩🏾" body="your dick small 😂" />
    <Notes from={A.because - 2} to={yap0} title="Me" lines={[{ text: "I know who I am", at: A.know }, { text: "Strong belief about myself", at: A.belief1 }]} />
    {/* 6 — "he just be yapping" → I got money */}
    <Banner at={A.niggas - 2} until={A.got - 2} {...IG} app="INSTAGRAM" title="hater_2026 commented" body="he just be yapping 🙄" />
    <Banner at={A.money - 2} until={A.fuckY + 10} logo="applepay" color="#000" app="WALLET" title="Apple Pay" body="Payment received ✓" />
    {/* 7 — you are influential / can speak / funny */}
    <Tiles from={A.influential2 - 4} to={A.but} title="A LOT OF Y’ALL ARE…" tiles={[{ emoji: "🌟", label: "Influential", at: A.influential2 }, { emoji: "🗣️", label: "Know how to speak", at: A.speak }, { emoji: "😂", label: "Funny as fuck", at: A.funny }]} />
    {/* 8 — the script: same week → new city */}
    <SameWeek from={A.script2 - 4} to={A.nigga} />
    <NewCity at={A.state - 14} city={A.city} until={A.script3 - 4} />
    {/* 9 — Khamani's line: the split comes back (callback to the cold open) */}
    <Banner at={A.khamani - 2} until={A.aNice} {...IG} app="INSTAGRAM" title="Khamani" body="posted a new video" />
    <NiceSplit from={A.perceived - 4} perceived={A.perceived} actually={A.actually} to={A.andN} />
    {/* 10 — "no" to family, "yes" to strangers */}
    <BannerStack until={A.butN} items={[
      { at: A.sister - 2, ...MSG, title: "Sister", body: "Can you help me move?" },
      { at: A.mom - 2, ...MSG, title: "Mom", body: "Come over this weekend?" },
      { at: A.dad - 2, ...MSG, title: "Dad", body: "Help me with the yard?" },
      { at: A.brother - 2, ...MSG, title: "You → Brother", body: "No, I don’t wanna do that." },
    ]} />
    <Banner at={A.hey - 2} until={A.yes - 2} {...MSG} title="Someone you just met" body="Hey, can you do this for me?" />
    <Banner at={A.yes - 2} until={A.not} {...MSG} title="You" body="Yes, of course! 👍" />
    {/* 11 — doing whatever they want → compromises beliefs */}
    <Notes from={A.whatever - 4} to={A.andE} title="Doing it for them" lines={[{ text: "Pick them up at 6 AM", at: A.whatever }, { text: "Lend them $300", at: A.want }, { text: "Cancel my own plans", at: A.doE }]} />
    {/* 12 — let it go */}
    <LetGo at={A.let} until={A.youre + 30} />
    {/* 13 — just post */}
    <PostUpload at={A.post - 6} until={A.broke5 - 2} />
    <Captions hide={HIDE} tops={TOPS} />
    <FollowCard flipAt={FLIP} />
    <Sound />
  </AbsoluteFill>
);
