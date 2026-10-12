import React from "react";
import { AbsoluteFill, Audio, Composition, registerRoot, staticFile, continueRender, delayRender } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import "@fontsource/inter/800.css";
import "@fontsource/archivo-black/400.css";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/700.css";
import { Anchor, Beam, Bloom, C, Cam, Crowd, Dash, Filters, Headline, Hud, Mono, Panel, PaperDetail, Push, Slash, SlamV2, World } from "../lib/Blueprint2";
import { Finale, Form } from "../lib/Blueprint";
import { Hit } from "../lib/sfx";
import caps from "./ep4caps.json";

type Cp = { t: string; f0: number; k: number };
const CAPS = caps as Cp[];
const W = (k: number) => CAPS.filter((c) => c.k === k).map((c, i) => { const low = c.t.toLowerCase(); return { t: i === 0 || low === "i" ? low.charAt(0).toUpperCase() + low.slice(1) : low, at: c.f0 }; });
const at = (word: string, n = 1) => CAPS.filter((c) => c.t.replace(/[^A-Z']/g, "") === word)[n - 1].f0;
const END = 548;

const Scenes: React.FC = () => {
  const A = { perceived: at("PERCEIVED"), actually: at("ACTUALLY"), its: at("IT'S"), niggas: at("NIGGAS"), potential: at("POTENTIAL"), not: at("NOT"), successful: at("SUCCESSFUL"), see2: at("SEE", 2), you3: at("YOU", 3), can: at("CAN"), influential: at("INFLUENTIAL") };
  const s1 = [0, A.its + 4], s2 = [A.its - 4, A.not + 4], s3 = [A.not - 4, A.you3], s4 = [END - 18, END];
  return (
    <AbsoluteFill style={{ background: C.navy2 }}>
      <Filters />
      {/* S1 perceived vs actually */}
      <Push from={s1[0]} to={s1[1]} inLen={1}>
        <Cam from={s1[0]} to={s1[1]} depth={0.35}><World pools={[{ x: 540, y: 1000, r: 520, color: "#3d4fb0" }, { x: 820, y: 935, r: 420, at: A.actually }]} /></Cam>
        <Bloom>
          <Cam from={s1[0]} to={s1[1]} depth={1}>
            <Headline words={W(0)} keep={["ACTUALLY"]} until={s1[1]} />
            <Dash x1={60} y1={1180} x2={1020} y2={1180} at={14} />
            <Dash x1={540} y1={700} x2={540} y2={1700} at={18} />
            <Beam x1={540} y1={1420} x2={270} y2={1010} at={22} comet={A.perceived - 18} curve={140} />
            <Beam x1={540} y1={1420} x2={810} y2={1010} at={22} comet={A.actually - 18} curve={-140} hot />
            <Panel x={340} y={1420} w={400} h={170} at={8} label="YOU" sub="the person" id="node 00" fs={48} />
            <Panel x={60} y={840} w={420} h={170} at={A.perceived - 8} label="PERCEIVED" sub="what they see" id="node 01" dead={A.actually + 12} />
            <Panel x={600} y={840} w={420} h={170} at={A.actually - 6} label="ACTUALLY" sub="who you are" id="node 02" hot={A.actually + 2} />
            <Slash x={60} y={840} w={420} h={170} at={A.actually + 4} />
            <Anchor x={540} y={1420} at={12} label="origin" />
            <Anchor x={270} y={1010} at={A.perceived - 6} />
            <Anchor x={810} y={1010} at={A.actually - 4} hot />
            <Mono x={60} y={1030} s={16} o={0.5} at={A.perceived}>perception · external · unstable</Mono>
            <Mono x={1020} y={1030} s={16} o={0.7} c={C.warm} at={A.actually} align="right">character · internal · real</Mono>
          </Cam>
        </Bloom>
        <Hud fig="fig. 1 — perception vs. reality" scene="SC.01" refId="REF 04-0001 · PERCEPTION_MODEL v2" readouts={["nodes: 3", "edges: 2", `struck: ${1}`]} />
      </Push>
      {/* S2 potential */}
      <Push from={s2[0]} to={s2[1]}>
        <Cam from={s2[0]} to={s2[1]} depth={0.35}><World pools={[{ x: 540, y: 1150, r: 560, color: "#3d4fb0" }, { x: 540, y: 1640, r: 480, at: A.potential }]} /></Cam>
        <Bloom>
          <Cam from={s2[0]} to={s2[1]} depth={1}>
            <Headline words={W(1)} keep={["POTENTIAL"]} size={66} y={170} until={s2[1]} />
            <Crowd at={A.niggas - 14} lit={A.potential - 8} />
            <Beam x1={540} y1={1500} x2={540} y2={1560} at={A.potential - 12} hot />
            <Panel x={220} y={1560} w={640} h={180} at={A.potential - 6} label="POTENTIAL" sub="detected · every one of you" id="scan 108/108" hot={A.potential + 2} fs={54} />
            <Anchor x={100} y={760} at={A.niggas} label="r0 c0" />
            <Anchor x={980} y={1400} at={A.niggas + 6} label="r8 c11" />
            <Mono x={100} y={720} s={16} o={0.5} at={A.niggas}>{"sample: y'all · n = 108"}</Mono>
          </Cam>
        </Bloom>
        <Hud fig="fig. 2 — y'all" scene="SC.02" refId="REF 04-0002 · CROWD_SCAN" readouts={["threshold: 0.00", "lit: 108", "missed: 0"]} />
      </Push>
      {/* S3 paper */}
      <Push from={s3[0]} to={s3[1]}>
        <Cam from={s3[0]} to={s3[1]} depth={0.3}><World paper /></Cam>
        <Cam from={s3[0]} to={s3[1]} depth={0.8}>
          <Mono x={70} y={430} s={20} o={0.7} c="#2a2a30">DEPT. OF WHAT I SEE · REF 04-0003</Mono>
          <Form title="FORM 4-A" sub="WHAT I SEE IN YOU · REVISED EDITION" at={A.not - 2} y={500} steps={[{ t: "successful", at: A.successful }]} strikeAt={A.successful + 14} stamp={{ t: "NOT ONLY", at: A.see2 }} />
          <PaperDetail at={A.not} fields={[{ k: "SUBJECT", v: "y'all", at: A.not + 2 }, { k: "ASSESSED BY", v: "Jason", at: A.not + 10 }, { k: "VERDICT", v: "not only successful", at: A.see2 + 4 }]}
            checks={[{ t: "SUCCESSFUL", at: A.successful + 2 }, { t: "ONLY THAT", at: A.see2, x: true }]} sign={{ t: "SIGNED · THE SPEAKER", at: A.see2 + 8 }} />
          <Mono x={70} y={1720} s={17} o={0.45} c="#2a2a30">* "only" struck by order of the speaker · do not detach</Mono>
          <Mono x={1010} y={1846} s={15} o={0.4} c="#2a2a30" align="right">page 1 / 1</Mono>
        </Cam>
      </Push>
      <SlamV2 words={[{ t: "YOU", at: A.you3 }, { t: "CAN BE", at: A.can }, { t: "INFLUENTIAL.", at: A.influential }]} until={s4[0]} />
      <Push from={s4[0]} to={s4[1]} outLen={1}>
        <World pools={[{ x: 540, y: 820, r: 560 }]} />
        <Bloom k={1.3}><Finale a="YOU CAN BE" b="INFLUENTIAL." at={s4[0]} until={s4[1]} /></Bloom>
        <Hud fig="fig. 4 — verdict" scene="SC.04" refId="REF 04-0004" />
      </Push>
    </AbsoluteFill>
  );
};

const Sample2: React.FC = () => {
  const A = { perceived: at("PERCEIVED"), actually: at("ACTUALLY"), its: at("IT'S"), niggas: at("NIGGAS"), potential: at("POTENTIAL"), not: at("NOT"), successful: at("SUCCESSFUL"), see2: at("SEE", 2), you3: at("YOU", 3), can: at("CAN"), influential: at("INFLUENTIAL") };
  return (
    <AbsoluteFill>
      <CameraMotionBlur samples={5} shutterAngle={170}><Scenes /></CameraMotionBlur>
      <Audio src={staticFile("ep4cut.mp4")} endAt={END} />
      <Hit at={2} id="pack5.deep_whoosh" />
      <Hit at={A.perceived} id="pack5.sparkle" v={0.35} />
      <Hit at={A.actually} id="pack5.sparkle" v={0.35} />
      <Hit at={A.actually + 4} id="pack6.blade" />
      <Hit at={A.actually + 14} id="ui.reverb_hit" v={0.3} />
      <Hit at={A.its} id="pack5.deep_whoosh" v={0.4} />
      <Hit at={A.niggas - 14} id="ui.data_loading" v={0.25} />
      <Hit at={A.potential} id="pack3.shine" />
      <Hit at={A.not} id="pack6.shutter" />
      <Hit at={A.successful} id="pack5.typing_2" />
      <Hit at={A.successful + 14} id="pack6.blade" v={0.3} />
      <Hit at={A.see2} id="pack6.impact_2" v={0.4} />
      <Hit at={A.you3} id="pack6.impact_1" v={0.4} />
      <Hit at={A.can} id="pack6.impact_1" v={0.4} />
      <Hit at={A.influential} id="pack4.cinestrike" v={0.5} />
    </AbsoluteFill>
  );
};

const h = typeof document !== "undefined" ? delayRender("fonts") : null;
if (h !== null) Promise.all(["800 40px Inter", "400 40px 'Archivo Black'", "400 40px 'JetBrains Mono'", "700 40px 'JetBrains Mono'"].map((x) => document.fonts.load(x))).then(() => continueRender(h));
const Root: React.FC = () => <Composition id="BpSample2" component={Sample2} durationInFrames={END} fps={30} width={1080} height={1920} />;
registerRoot(Root);
