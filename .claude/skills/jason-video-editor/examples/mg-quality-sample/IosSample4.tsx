import React from "react";
import { AbsoluteFill, Audio, Composition, random, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig, continueRender, delayRender } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import "@fontsource-variable/inter/opsz.css";
import { Bloom } from "../lib/Blueprint2";
import { Chip, G, IOS, Island, Moment, Ring, Row, Stage3D, Swipe, Title, Wallpaper, Whip, Z, glassStyle, useIn } from "../lib/Glass";
import { Hit } from "../lib/sfx";
import caps from "./ep4caps.json";

/** v4: after v3 scored 6.9. 3D camera on every scene, whip transitions + heavy motion blur, big centered focal object from frame 1, an event every ~0.5s. */
type Cp = { t: string; f0: number; k: number };
const CAPS = caps as Cp[];
const W = (k: number) => CAPS.filter((c) => c.k === k).map((c, i) => { const low = c.t.toLowerCase(); return { t: i === 0 || low === "i" ? low.charAt(0).toUpperCase() + low.slice(1) : low, at: c.f0 }; });
const at = (word: string, n = 1) => CAPS.filter((c) => c.t.replace(/[^A-Z']/g, "") === word)[n - 1].f0;
const END = 548;
const A = { perceived: at("PERCEIVED"), actually: at("ACTUALLY"), its: at("IT'S"), niggas: at("NIGGAS"), females: at("FEMALES"), potential: at("POTENTIAL"), not: at("NOT"), successful: at("SUCCESSFUL"), see2: at("SEE", 2), you3: at("YOU", 3), can: at("CAN"), influential: at("INFLUENTIAL") };

/** big "You" avatar with breathing ring pulses (the focal object from frame 1) */
const YouOrb: React.FC<{ at: number; y: number; hotAt: number }> = ({ at: a, y, hotAt }) => {
  const { f, fps, on, style } = useIn(a);
  if (!on) return null;
  const hot = spring({ frame: f - hotAt, fps, config: IOS });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: y, display: "flex", flexDirection: "column", alignItems: "center", ...style }}>
      <div style={{ position: "relative", width: 260, height: 260 }}>
        {[0, 1, 2].map((k) => { const t = ((f - a + k * 20) % 60) / 60; return <div key={k} style={{ position: "absolute", inset: -t * 120, borderRadius: "50%", border: `3px solid ${hot > 0.5 ? G.accent : "rgba(235,240,255,0.5)"}`, opacity: (1 - t) * 0.6 }} />; })}
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", background: `linear-gradient(160deg, ${hot > 0.5 ? G.accent2 : "#8EA2FF"}, ${hot > 0.5 ? G.accent : "#4B5BD6"})`, boxShadow: `0 30px 80px rgba(0,0,10,0.5), 0 0 ${80 * hot}px rgba(255,106,61,0.6), inset 0 2px 0 rgba(255,255,255,0.35)`,
          display: "flex", alignItems: "center", justifyContent: "center", fontFamily: G.font, fontWeight: 800, fontSize: 92, color: "#fff", letterSpacing: "-0.03em" }}>You</div>
      </div>
    </div>
  );
};
const BigCard: React.FC<{ y: number; at: number; hot?: number; children: React.ReactNode; header: string }> = ({ y, at: a, hot, children, header }) => {
  const { f, on, style } = useIn(a);
  if (!on) return null;
  const isHot = hot !== undefined && f >= hot;
  return (
    <div style={{ position: "absolute", left: 50, width: 980, top: y, ...style }}>
      <div style={{ fontFamily: G.font, fontSize: 26, fontWeight: 600, letterSpacing: "0.06em", color: G.sub, margin: "0 0 14px 30px" }}>{header}</div>
      <div style={{ ...glassStyle(isHot, 52), padding: "34px 40px" }}>{children}</div>
    </div>
  );
};
const Avatars: React.FC<{ at: number; lit: number }> = ({ at: a0, lit }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hues = [215, 260, 20, 330, 190, 40, 280, 150];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 20, marginTop: 22 }}>
      {Array.from({ length: 30 }).map((_, i) => {
        const p = spring({ frame: f - a0 - i * 0.9, fps, config: IOS });
        const h = spring({ frame: f - lit - (Math.abs((i % 6) - 2.5) + Math.floor(i / 6)) * 2, fps, config: IOS });
        const hue = hues[Math.floor(random(`h${i}`) * hues.length)];
        return <div key={i} style={{ width: 124, height: 124, borderRadius: 62, background: `linear-gradient(160deg, hsl(${hue},70%,68%), hsl(${hue + 25},65%,48%))`, opacity: p, transform: `scale(${0.6 + 0.4 * p}) translateZ(0)`,
          boxShadow: `0 0 0 ${6 * h}px ${G.accent}, 0 0 ${60 * h}px rgba(255,106,61,0.65), inset 0 1px 0 rgba(255,255,255,0.35)`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: G.font, fontWeight: 800, fontSize: 44, color: "rgba(255,255,255,0.92)" }}>{"ABCDEFGHJKLMNPRSTVWYZQXUOIBDE"[i]}</div>;
      })}
    </div>
  );
};

const Scenes: React.FC = () => {
  const s1 = [0, A.its + 5], s2 = [A.its - 5, A.not + 5], s3 = [A.not - 5, A.you3 + 2], s4 = [END - 22, END];
  return (
    <AbsoluteFill style={{ background: "#0B0D1E" }}>
      <Whip from={s1[0]} to={s1[1]}>
        <Wallpaper pools={[{ x: 540, y: 1100, r: 380, at: 6, color: "rgba(110,130,255,0.5)" }, { x: 540, y: 1430, r: 440, at: A.actually }]} />
        <Stage3D keys={[{ f: 0, rx: 24, ry: -20, z: -520, y: 90 }, { f: 50, rx: 8, ry: -8, z: -160 }, { f: A.actually, rx: 2, ry: 4, z: -40 }, { f: s1[1], rx: -4, ry: 10, z: 60 }]}>
          <Bloom k={0.6}>
            <Z depth={180}><Title words={W(0)} keep={["ACTUALLY"]} until={s1[1]} size={88} y={150} /></Z>
            <Z depth={0}>
              <div style={{ position: "absolute", left: 50, top: 650, width: 980 }}>
                <Swipe at={A.actually + 6} w={980} h={210}>
                  <BigCard y={0} at={A.perceived - 6} header="WHAT THEY SEE">
                    <Row icon="🎭" tint="linear-gradient(160deg,#8E8E93,#5A5A60)" title="Perceived as nice" sub="performance · for approval" at={A.perceived - 2} />
                  </BigCard>
                </Swipe>
              </div>
              <YouOrb at={4} y={990} hotAt={A.actually + 4} />
              <BigCard y={1360} at={A.actually - 6} header="WHO YOU ARE" hot={A.actually + 4}>
                <Row icon="💛" tint={`linear-gradient(160deg, ${G.accent2}, ${G.accent})`} title="Actually nice" sub="character · no audience needed" at={A.actually - 2}
                  trail={<div style={{ width: 64, height: 64, borderRadius: 32, background: G.green, color: "#fff", fontSize: 38, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>✓</div>} />
              </BigCard>
            </Z>
            <Z depth={90}><Chip t="perception check" at={22} x={340} y={560} tint="rgba(255,255,255,0.16)" /></Z>
          </Bloom>
        </Stage3D>
      </Whip>
      <Whip from={s2[0]} to={s2[1]}>
        <Wallpaper pools={[{ x: 540, y: 1150, r: 520, at: A.potential }]} />
        <Stage3D keys={[{ f: s2[0], rx: 14, ry: 22, z: -420 }, { f: A.niggas, rx: 6, ry: 4, z: -140 }, { f: A.potential, rx: 0, ry: -2, z: 40 }, { f: s2[1], rx: -3, ry: -10, z: 120 }]}>
          <Bloom k={0.6}>
            <Z depth={160}><Title words={W(1)} keep={["POTENTIAL"]} size={72} y={170} until={s2[1]} /></Z>
            <Z depth={0}>
              <Island at={s2[0] + 4} open={A.niggas - 4} until={s2[1]} x={40} y={640} w={1000} h={820}
                pill={<span style={{ fontFamily: G.font, fontWeight: 700, fontSize: 32, color: "#fff" }}><span style={{ color: G.accent }}>●</span> Looking at y'all</span>}>
                <div style={{ fontFamily: G.font, fontSize: 24, fontWeight: 600, letterSpacing: "0.06em", color: G.sub }}>Y'ALL · 30 PEOPLE</div>
                <Avatars at={A.niggas} lit={A.potential - 6} />
              </Island>
            </Z>
            <Z depth={140}><Chip t="Potential · every one of you" at={A.potential} x={150} y={1560} big /></Z>
          </Bloom>
        </Stage3D>
      </Whip>
      <Whip from={s3[0]} to={s3[1]}>
        <Wallpaper light />
        <Stage3D keys={[{ f: s3[0], rx: 20, ry: -12, z: -380 }, { f: A.successful, rx: 6, ry: -2, z: -80 }, { f: A.see2, rx: 0, ry: 3, z: 20, rz: -1.5 }, { f: s3[1], rx: -3, ry: 8, z: 100 }]}>
          <Z depth={140}>
            <div style={{ position: "absolute", left: 60, top: 260, fontFamily: G.font, fontWeight: 800, fontSize: 96, color: "#16161E", letterSpacing: "-0.035em" }}>What I see in you</div>
            <div style={{ position: "absolute", left: 64, top: 384, fontFamily: G.font, fontWeight: 500, fontSize: 32, color: "rgba(20,20,30,0.45)" }}>Reminders · y'all</div>
          </Z>
          <Z depth={0}>
            <ListCard />
            <Ring cx={540} cy={1380} r={200} at={A.successful + 4} to={0.5} color={G.accent} />
            <div style={{ position: "absolute", top: 1330, left: 0, right: 0, textAlign: "center", fontFamily: G.font, fontWeight: 800, fontSize: 80, color: "#16161E" }}>1 of 2</div>
          </Z>
          <Z depth={160}><Chip t="Not only." at={A.see2} x={560} y={860} big /></Z>
        </Stage3D>
      </Whip>
      <Moment words={[{ t: "You", at: A.you3 }, { t: "can be", at: A.can }, { t: "influential.", at: A.influential }]} until={s4[0] + 4} />
      <Whip from={s4[0]} to={s4[1] + 20}>
        <Wallpaper pools={[{ x: 540, y: 900, r: 520 }]} />
        <Stage3D keys={[{ f: s4[0], z: -300, rx: 10 }, { f: s4[1], z: 80, rx: 0 }]}>
          <Bloom k={0.85}>
            <div style={{ position: "absolute", top: 720, left: 0, right: 0, textAlign: "center", fontFamily: G.font, fontWeight: 900, letterSpacing: "-0.045em", lineHeight: 1 }}>
              <div style={{ fontSize: 130, color: G.ink }}>You can be</div>
              <div style={{ fontSize: 146, backgroundImage: `linear-gradient(100deg, ${G.accent}, ${G.accent2})`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>influential.</div>
            </div>
          </Bloom>
        </Stage3D>
      </Whip>
    </AbsoluteFill>
  );
};
const ListCard: React.FC = () => {
  const f = useCurrentFrame();
  const rows = [{ t: "Become successful", a: A.successful, done: true }, { t: "Only that?", a: A.see2 - 8, done: false }];
  return (
    <div style={{ position: "absolute", left: 50, top: 520, width: 980, borderRadius: 52, background: "rgba(255,255,255,0.82)", boxShadow: "0 40px 100px rgba(20,20,40,0.18), 0 8px 22px rgba(20,20,40,0.08)", padding: "20px 42px" }}>
      {rows.map((r, i) => f >= r.a - 4 && (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 30, padding: "32px 0", borderBottom: i === 0 ? "1px solid rgba(20,20,30,0.08)" : undefined }}>
          <div style={{ width: 66, height: 66, borderRadius: 33, border: `4px solid ${r.done ? G.accent : "rgba(20,20,30,0.25)"}`, background: r.done && f >= r.a + 4 ? G.accent : "transparent", color: "#fff", fontSize: 38, fontWeight: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>{r.done && f >= r.a + 4 ? "✓" : ""}</div>
          <span style={{ fontFamily: G.font, fontWeight: 650, fontSize: 56, color: "#16161E", opacity: !r.done && f >= A.see2 ? 0.35 : 1 }}>{r.t}</span>
        </div>
      ))}
    </div>
  );
};

const Sample4: React.FC = () => (
  <AbsoluteFill>
    <CameraMotionBlur samples={8} shutterAngle={200}><Scenes /></CameraMotionBlur>
    <Audio src={staticFile("ep4cut.mp4")} endAt={END} />
    <Hit at={4} id="ui.open_ui" v={0.35} />
    <Hit at={A.perceived - 6} id="ios.ios_tritone" v={0.4} />
    <Hit at={A.actually - 6} id="ios.ios_received" v={0.45} />
    <Hit at={A.actually + 6} id="pack6.blade" v={0.3} />
    <Hit at={A.actually + 6} id="ios.ios_tink" v={0.6} />
    <Hit at={A.its} id="pack5.deep_whoosh" v={0.45} />
    <Hit at={A.niggas - 4} id="ui.open_ui" v={0.4} />
    <Hit at={A.potential} id="ios.ios_success" v={0.5} />
    <Hit at={A.not} id="pack5.deep_whoosh" v={0.45} />
    <Hit at={A.successful + 4} id="ios.ios_tink" v={0.7} />
    <Hit at={A.see2} id="pack5.button_1" v={0.5} />
    <Hit at={A.you3} id="pack6.impact_1" v={0.35} />
    <Hit at={A.can} id="pack5.button_2" v={0.4} />
    <Hit at={A.influential} id="pack3.shine" v={0.5} />
    <Hit at={END - 22} id="pack5.deep_whoosh" v={0.35} />
  </AbsoluteFill>
);

const h = typeof document !== "undefined" ? delayRender("fonts") : null;
if (h !== null) Promise.all(["500 40px 'Inter Variable'", "800 40px 'Inter Variable'", "900 120px 'Inter Variable'"].map((x) => document.fonts.load(x))).then(() => continueRender(h));
registerRoot(() => <Composition id="IosSample4" component={Sample4} durationInFrames={END} fps={30} width={1080} height={1920} />);
