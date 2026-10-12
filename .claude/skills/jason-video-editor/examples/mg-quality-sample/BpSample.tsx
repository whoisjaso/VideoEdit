import React from "react";
import { AbsoluteFill, Audio, Composition, interpolate, random, registerRoot, staticFile, useCurrentFrame, continueRender, delayRender } from "remotion";
import "@fontsource/inter/800.css";
import "@fontsource/archivo-black/400.css";
import "@fontsource/jetbrains-mono/700.css";
import { BP, Finale, Form, KLine, Micro, Node, Slam, Stage, Strike, Wire } from "../lib/Blueprint";
import { Hit } from "../lib/sfx";
import caps from "./ep4caps.json";

/** r05-quality sample over ep #4's opening (cold open + first lines). Every element lands on a spoken word. */
type C = { t: string; f0: number; k: number };
const CAPS = caps as C[];
// sentence case (r05): first word capitalised, "I" stays, everything else lower
const W = (k: number) => CAPS.filter((c) => c.k === k).map((c, i) => { const low = c.t.toLowerCase(); const t = i === 0 || low === "i" ? low.charAt(0).toUpperCase() + low.slice(1) : low.replace(/^i'/, "I'"); return { t, at: c.f0 }; });
const at = (word: string, n = 1) => CAPS.filter((c) => c.t.replace(/[^A-Z']/g, "") === word)[n - 1].f0;
const END = 548;

const Dots: React.FC<{ from: number; lit: number; to: number }> = ({ from, lit, to }) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
      {Array.from({ length: 12 * 9 }).map((_, i) => {
        const cx = 100 + (i % 12) * 80, cy = 760 + Math.floor(i / 12) * 80;
        const appear = from + 4 + random(`a${i}`) * 40, on = f >= appear;
        const hot = f >= lit + random(`h${i}`) * 18;
        return on ? <circle key={i} cx={cx} cy={cy} r={hot ? 13 : 8} fill={hot ? BP.hot : "rgba(200,212,255,0.55)"} style={hot ? { filter: `drop-shadow(0 0 8px ${BP.hot})` } : undefined} /> : null;
      })}
    </svg>
  );
};

const Sample: React.FC = () => {
  const A = { perceived: at("PERCEIVED"), actually: at("ACTUALLY"), nice2: at("NICE", 2), its: at("IT'S"), niggas: at("NIGGAS"), females: at("FEMALES"), potential: at("POTENTIAL"),
    not: at("NOT"), successful: at("SUCCESSFUL"), see2: at("SEE", 2), you3: at("YOU", 3), can: at("CAN"), influential: at("INFLUENTIAL") };
  return (
    <AbsoluteFill style={{ background: BP.bg1 }}>
      <Audio src={staticFile("ep4cut.mp4")} endAt={END} />
      {/* S1 cold open: perceived vs actually */}
      <Stage from={0} to={A.its}>
        <KLine words={W(0)} keep={["ACTUALLY"]} until={A.its} size={76} y={200} />
        <Micro x={70} y={120}>fig. 1 — perception vs. reality</Micro>
        <Micro x={850} y={120}>t = {(0).toFixed(3)}</Micro>
        <Node x={340} y={1420} w={400} h={160} label="YOU" sub="the person" at={10} fs={46} />
        <Wire x1={540} y1={1420} x2={260} y2={1010} at={20} comet={A.perceived - 14} curve={120} />
        <Wire x1={540} y1={1420} x2={820} y2={1010} at={20} comet={A.actually - 14} curve={120} hot />
        <Node x={60} y={860} w={420} h={150} label="PERCEIVED" sub="what they see" at={A.perceived - 8} dead={A.actually + 10} />
        <Node x={600} y={860} w={420} h={150} label="ACTUALLY" sub="who you are" at={A.actually - 4} hot={A.actually + 2} />
        <Strike x={60} y={860} w={420} h={150} at={A.actually + 4} />
        <Micro x={60} y={1030} o={0.45} size={20}>status: performance</Micro>
        <Micro x={600} y={1030} o={0.7} color={BP.hot} size={20}>status: real</Micro>
        <Micro x={340} y={1600} o={0.4} size={20}>node 00 · origin</Micro>
        <Micro x={70} y={1780} o={0.35} size={18}>REF 04-COLD · PERCEPTION_MODEL v1</Micro>
      </Stage>
      {/* S2 potential: a crowd of y'all lights up */}
      <Stage from={A.its} to={A.not} dolly={0.08}>
        <KLine words={W(1)} keep={["POTENTIAL"]} size={64} y={190} until={A.not} />
        <Micro x={70} y={120}>fig. 2 — y'all</Micro>
        <Micro x={760} y={120}>{`sample: ${12 * 9} people`}</Micro>
        <Dots from={A.niggas - 10} lit={A.potential - 4} to={A.not} />
        <Node x={240} y={1560} w={600} h={170} label="POTENTIAL" sub="detected: every one of you" at={A.potential - 6} hot={A.potential + 2} fs={52} />
        <Wire x1={540} y1={1460} x2={540} y2={1560} at={A.potential - 10} comet={A.potential - 10} hot />
      </Stage>
      {/* S3 light paper scene: not only successful */}
      <Stage from={A.not} to={A.you3} light dolly={0.05}>
        <Micro x={70} y={430} color="#2a2a30" size={20}>DEPT. OF WHAT I SEE · REF 04-0001</Micro>
        <Micro x={70} y={1700} color="#2a2a30" size={18} o={0.4}>* "only" is struck by order of the speaker. Do not detach.</Micro>
        <Form title="FORM 4-A" sub="WHAT I SEE IN YOU · REVISED EDITION" at={A.not - 2} y={500}
          steps={[{ t: "successful", at: A.successful }]} strikeAt={A.successful + 14} stamp={{ t: "NOT ONLY", at: A.see2 }} />
      </Stage>
      {/* S4 slam */}
      <Slam words={[{ t: "YOU", at: A.you3 }, { t: "CAN BE", at: A.can }, { t: "INFLUENTIAL.", at: A.influential }]} until={END - 18} />
      <Stage from={END - 18} to={END}><Finale a="YOU CAN BE" b="INFLUENTIAL." at={END - 18} until={END} /></Stage>
      {/* sound: lands on the frame via <Hit> */}
      <Hit at={2} id="pack5.deep_whoosh" />
      <Hit at={A.perceived - 14} id="pack5.sparkle" v={0.35} />
      <Hit at={A.actually - 14} id="pack5.sparkle" v={0.35} />
      <Hit at={A.actually + 4} id="pack6.blade" />
      <Hit at={A.actually + 2} id="pack6.click_sfx" v={0.35} />
      <Hit at={A.its} id="pack6.camera_action" />
      <Hit at={A.niggas - 10} id="ui.data_loading" v={0.25} />
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
if (h !== null) Promise.all(["800 40px Inter", "400 40px 'Archivo Black'", "700 40px 'JetBrains Mono'"].map((x) => document.fonts.load(x))).then(() => continueRender(h));
const Root: React.FC = () => <Composition id="BpSample" component={Sample} durationInFrames={END} fps={30} width={1080} height={1920} />;
registerRoot(Root);
