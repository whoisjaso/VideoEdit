import React from "react";
import { AbsoluteFill, Audio, Composition, random, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig, continueRender, delayRender } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import "@fontsource/inter/900.css";
import { Bloom, Cam } from "../lib/Blueprint2";
import { Card, Chip, Chrome, G, IOS, Island, Moment, Ring, Row, Swipe, Title, Wallpaper } from "../lib/Glass";
import { Hit } from "../lib/sfx";
import caps from "./ep4caps.json";

/** iOS-language sample at r05 quality (v3). Soft, borderless, springs; every element on a spoken word. */
type Cp = { t: string; f0: number; k: number };
const CAPS = caps as Cp[];
const W = (k: number) => CAPS.filter((c) => c.k === k).map((c, i) => { const low = c.t.toLowerCase(); return { t: i === 0 || low === "i" ? low.charAt(0).toUpperCase() + low.slice(1) : low, at: c.f0 }; });
const at = (word: string, n = 1) => CAPS.filter((c) => c.t.replace(/[^A-Z']/g, "") === word)[n - 1].f0;
const END = 548;

const Soft: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({ from, to, children }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from || f >= to) return null;
  const i = spring({ frame: f - from, fps, config: IOS }), o = spring({ frame: f - (to - 12), fps, config: IOS });
  return <AbsoluteFill style={{ opacity: Math.min(1, i * 1.3) * (1 - o), transform: `scale(${(0.93 + 0.07 * i) * (1 + 0.06 * o)})`, filter: `blur(${(1 - i) * 14 + o * 14}px)` }}>{children}</AbsoluteFill>;
};

const Avatars: React.FC<{ at: number; lit: number }> = ({ at: a0, lit }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hues = [215, 260, 20, 330, 190, 40, 280, 150];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 22, marginTop: 18 }}>
      {Array.from({ length: 30 }).map((_, i) => {
        const p = spring({ frame: f - a0 - i * 1.2, fps, config: IOS });
        const h = spring({ frame: f - lit - (Math.abs((i % 6) - 2.5) + Math.floor(i / 6)) * 2, fps, config: IOS });
        const hue = hues[Math.floor(random(`h${i}`) * hues.length)];
        return (
          <div key={i} style={{ width: 112, height: 112, borderRadius: 56, background: `linear-gradient(160deg, hsl(${hue},70%,68%), hsl(${hue + 25},65%,48%))`, opacity: p, transform: `scale(${0.85 + 0.15 * p})`,
            boxShadow: `0 0 0 ${6 * h}px ${G.accent}, 0 0 ${50 * h}px rgba(255,106,61,0.6), inset 0 1px 0 rgba(255,255,255,0.35)`, display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "Inter", fontWeight: 800, fontSize: 40, color: "rgba(255,255,255,0.9)" }}>{"ABCDEFGHJKLMNPRSTVWYZQXUOIBDE"[i]}</div>
        );
      })}
    </div>
  );
};

const Scenes: React.FC = () => {
  const A = { perceived: at("PERCEIVED"), actually: at("ACTUALLY"), its: at("IT'S"), niggas: at("NIGGAS"), females: at("FEMALES"), potential: at("POTENTIAL"), not: at("NOT"), successful: at("SUCCESSFUL"), see2: at("SEE", 2), you3: at("YOU", 3), can: at("CAN"), influential: at("INFLUENTIAL") };
  const s1 = [0, A.its + 6], s2 = [A.its - 6, A.not + 6], s3 = [A.not - 6, A.you3 + 2], s4 = [END - 20, END];
  return (
    <AbsoluteFill style={{ background: "#0B0D1E" }}>
      <Soft from={s1[0]} to={s1[1]}>
        <Cam from={s1[0]} to={s1[1]} depth={0.35}><Wallpaper pools={[{ x: 540, y: 1250, r: 420, at: A.actually }]} /></Cam>
        <Bloom k={0.55}>
          <Cam from={s1[0]} to={s1[1]} depth={1}>
            <Title words={W(0)} keep={["ACTUALLY"]} until={s1[1]} />
            <div style={{ position: "absolute", left: 70, top: 820, width: 940 }}>
              <Swipe at={A.actually + 6} w={940} h={190}>
                <Card x={0} y={0} w={940} at={A.perceived - 6} header="What they see">
                  <Row icon="🎭" tint="linear-gradient(160deg,#8E8E93,#5A5A60)" title="Perceived as nice" sub="Performance · for approval" at={A.perceived - 2} />
                </Card>
              </Swipe>
            </div>
            <Card x={70} y={1190} w={940} at={A.actually - 6} header="Who you are" hot={A.actually + 4} foot="Updated just now">
              <Row icon="💛" tint={`linear-gradient(160deg, ${G.accent2}, ${G.accent})`} title="Actually nice" sub="Character · no audience needed" at={A.actually - 2}
                trail={<div style={{ width: 56, height: 56, borderRadius: 28, background: G.green, color: "#fff", fontSize: 34, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>✓</div>} />
            </Card>
          </Cam>
        </Bloom>
        <Chrome page={0} pages={4} />
      </Soft>
      <Soft from={s2[0]} to={s2[1]}>
        <Cam from={s2[0]} to={s2[1]} depth={0.35}><Wallpaper pools={[{ x: 540, y: 1150, r: 480, at: A.potential }]} /></Cam>
        <Bloom k={0.55}>
          <Cam from={s2[0]} to={s2[1]} depth={1}>
            <Title words={W(1)} keep={["POTENTIAL"]} size={64} y={200} until={s2[1]} />
            <Island at={A.niggas - 22} open={A.niggas} until={s2[1]} x={70} y={720} w={940} h={760}
              pill={<span style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 30, color: "#fff" }}><span style={{ color: G.accent }}>●</span> Looking at y'all</span>}>
              <div style={{ fontFamily: "Inter", fontSize: 22, fontWeight: 600, letterSpacing: "0.06em", color: G.sub }}>Y'ALL · 30 PEOPLE</div>
              <Avatars at={A.niggas + 6} lit={A.potential - 6} />
            </Island>
            <Chip t="Potential · every one of you" at={A.potential} x={170} y={1640} big />
          </Cam>
        </Bloom>
        <Chrome page={1} pages={4} />
      </Soft>
      <Soft from={s3[0]} to={s3[1]}>
        <Cam from={s3[0]} to={s3[1]} depth={0.35}><Wallpaper light /></Cam>
        <Cam from={s3[0]} to={s3[1]} depth={0.9}>
          <div style={{ position: "absolute", left: 70, top: 300, fontFamily: "Inter", fontWeight: 800, fontSize: 72, color: "#16161E", letterSpacing: "-0.03em" }}>What I see in you</div>
          <div style={{ position: "absolute", left: 72, top: 395, fontFamily: "Inter", fontWeight: 500, fontSize: 28, color: "rgba(20,20,30,0.45)" }}>Reminders · y'all</div>
          <div style={{ position: "absolute", left: 70, top: 500, width: 940, borderRadius: 44, background: "rgba(255,255,255,0.75)", backdropFilter: "blur(30px)", boxShadow: "0 30px 80px rgba(20,20,40,0.15), 0 6px 18px rgba(20,20,40,0.08)", padding: "18px 36px" }}>
            {[{ t: "Become successful", a: A.successful, done: true }, { t: "Only that?", a: A.see2 - 6, done: false }].map((r, i) => {
              const f = useCurrentFrame();
              if (f < r.a - 4) return null;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 26, padding: "26px 0", borderBottom: i === 0 ? "1px solid rgba(20,20,30,0.08)" : undefined }}>
                  <div style={{ width: 54, height: 54, borderRadius: 27, border: `3px solid ${r.done ? G.accent : "rgba(20,20,30,0.25)"}`, background: r.done && f >= r.a + 4 ? G.accent : "transparent", color: "#fff", fontSize: 30, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>{r.done && f >= r.a + 4 ? "✓" : ""}</div>
                  <span style={{ fontFamily: "Inter", fontWeight: 600, fontSize: 44, color: "#16161E", opacity: !r.done && f >= A.see2 ? 0.35 : 1 }}>{r.t}</span>
                </div>
              );
            })}
          </div>
          <Chip t="Not only." at={A.see2} x={590} y={820} tint={G.accent} big />
          <div style={{ position: "absolute", left: 96, top: 1000, fontFamily: "Inter", fontSize: 24, color: "rgba(20,20,30,0.4)" }}>2 items · 1 completed</div>
          <Ring cx={540} cy={1400} r={170} at={A.successful + 4} to={0.5} color={G.accent} />
          <div style={{ position: "absolute", top: 1360, left: 0, right: 0, textAlign: "center", fontFamily: "Inter", fontWeight: 800, fontSize: 64, color: "#16161E" }}>1 of 2</div>
          <div style={{ position: "absolute", top: 1610, left: 0, right: 0, textAlign: "center", fontFamily: "Inter", fontWeight: 600, fontSize: 26, color: "rgba(20,20,30,0.42)" }}>Updated just now</div>
        </Cam>
        <Chrome page={2} pages={4} dark />
      </Soft>
      <Moment words={[{ t: "You", at: A.you3 }, { t: "can be", at: A.can }, { t: "influential.", at: A.influential }]} until={s4[0] + 4} />
      <Soft from={s4[0]} to={s4[1] + 12}>
        <Wallpaper pools={[{ x: 540, y: 900, r: 520 }]} />
        <Bloom k={0.8}>
          <div style={{ position: "absolute", top: 760, left: 0, right: 0, textAlign: "center", fontFamily: "Inter", fontWeight: 900, letterSpacing: "-0.045em", lineHeight: 1 }}>
            <div style={{ fontSize: 120, color: G.ink }}>You can be</div>
            <div style={{ fontSize: 132, backgroundImage: `linear-gradient(100deg, ${G.accent}, ${G.accent2})`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>influential.</div>
          </div>
        </Bloom>
        <Chrome page={3} pages={4} />
      </Soft>
    </AbsoluteFill>
  );
};

const IosSample: React.FC = () => {
  const A = { perceived: at("PERCEIVED"), actually: at("ACTUALLY"), its: at("IT'S"), niggas: at("NIGGAS"), potential: at("POTENTIAL"), not: at("NOT"), successful: at("SUCCESSFUL"), see2: at("SEE", 2), you3: at("YOU", 3), can: at("CAN"), influential: at("INFLUENTIAL") };
  return (
    <AbsoluteFill>
      <CameraMotionBlur samples={5} shutterAngle={170}><Scenes /></CameraMotionBlur>
      <Audio src={staticFile("ep4cut.mp4")} endAt={END} />
      <Hit at={A.perceived - 6} id="ios.ios_tritone" v={0.4} />
      <Hit at={A.actually - 6} id="ios.ios_received" v={0.45} />
      <Hit at={A.actually + 6} id="pack5.deep_whoosh" v={0.35} />
      <Hit at={A.actually + 6} id="ios.ios_tink" v={0.6} />
      <Hit at={A.its - 6} id="pack5.deep_whoosh" v={0.3} />
      <Hit at={A.niggas} id="ui.open_ui" v={0.4} />
      <Hit at={A.potential} id="ios.ios_success" v={0.5} />
      <Hit at={A.not - 6} id="pack5.deep_whoosh" v={0.3} />
      <Hit at={A.successful + 4} id="ios.ios_tink" v={0.7} />
      <Hit at={A.see2} id="pack5.button_1" v={0.5} />
      <Hit at={A.you3} id="pack6.impact_1" v={0.35} />
      <Hit at={A.can} id="pack5.button_2" v={0.4} />
      <Hit at={A.influential} id="pack3.shine" v={0.5} />
    </AbsoluteFill>
  );
};

const h = typeof document !== "undefined" ? delayRender("fonts") : null;
if (h !== null) Promise.all(["500 40px Inter", "600 40px Inter", "700 40px Inter", "800 40px Inter", "900 40px Inter"].map((x) => document.fonts.load(x))).then(() => continueRender(h));
const Root: React.FC = () => <Composition id="IosSample" component={IosSample} durationInFrames={END} fps={30} width={1080} height={1920} />;
registerRoot(Root);
