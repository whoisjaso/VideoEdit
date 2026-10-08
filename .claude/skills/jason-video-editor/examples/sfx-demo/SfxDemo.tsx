import React from "react";
import { AbsoluteFill, Audio, Composition, Sequence, interpolate, registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig, continueRender, delayRender } from "remotion";
import "@fontsource/inter/500.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import "@fontsource/nunito-sans/900.css";
import lib from "../lib/sfx-library.json";

/** SFX library audition reel (reference style: r10/r11 playhead timelines). Each sound plays once, its waveform crossing the playhead. */
type S = { id: string; file: string; job: string; vol: number; dur: number; use: string; origin: string; peaks: number[] };
const SOUNDS = (lib as { sounds: S[] }).sounds;
const JOBS = (lib as { jobs: Record<string, string> }).jobs;
const FPS = 30, INTRO = 54, PX = 420; // 420 px per second of audio
const slot = (s: S) => Math.round((Math.min(s.dur, 2.6) + 0.35) * FPS);
const STARTS = SOUNDS.reduce<number[]>((a, s, i) => [...a, i ? a[i - 1] + slot(SOUNDS[i - 1]) : INTRO], []);
export const TOTAL = STARTS[STARTS.length - 1] + slot(SOUNDS[SOUNDS.length - 1]) + 45;
const JC: Record<string, string> = { hook: "#FFD24A", impact: "#FF3B3B", whoosh: "#7FD1FF", shutter: "#E5E5EA", click: "#2BE37A", typing: "#C7C7CC", ios: "#34C759",
  win: "#2BE37A", reveal: "#FFD24A", build: "#FF9F0A", negative: "#FF3B3B", tech: "#5E5CE6", texture: "#BF5AF2" };

const Demo: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  let i = STARTS.findIndex((st, k) => f >= st && f < st + slot(SOUNDS[k]));
  if (i < 0) i = f < INTRO ? -1 : SOUNDS.length - 1;
  const s = i >= 0 ? SOUNDS[i] : null;
  const c = s ? JC[s.job] : "#FFD24A";
  const t = s ? (f - STARTS[i]) / fps : 0;
  const pl = spring({ frame: s ? f - STARTS[i] : f, fps, config: { damping: 18, stiffness: 180 } });
  const jobStart = s && (i === 0 || SOUNDS[i - 1].job !== s.job);
  const intro = spring({ frame: f, fps, config: { damping: 20, stiffness: 120 } });
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, #1c1c22 0%, #08080a 70%)`, fontFamily: "Inter", color: "#fff" }}>
      {/* title sandwich: small / BIG glow / small (r01, r10) */}
      <div style={{ position: "absolute", top: 150, left: 0, right: 0, textAlign: "center", opacity: intro, filter: `blur(${(1 - intro) * 10}px)` }}>
        <div style={{ fontSize: 44, fontWeight: 500, fontStyle: "italic", color: "rgba(255,255,255,.75)" }}>Jason's</div>
        <div style={{ fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 150, color: c, lineHeight: 1, textShadow: `0 0 60px ${c}88`, letterSpacing: "-0.02em" }}>SFX Library</div>
        <div style={{ fontSize: 40, fontWeight: 500, fontStyle: "italic", color: "rgba(255,255,255,.75)" }}>{SOUNDS.length} sounds · sorted by job</div>
      </div>
      {s && (
        <>
          <div style={{ position: "absolute", top: 520, left: 0, right: 0, textAlign: "center" }}>
            <div style={{ fontSize: 34, fontWeight: 800, letterSpacing: "0.3em", color: c, transform: `scale(${jobStart ? 0.8 + 0.2 * pl : 1})` }}>{s.job.toUpperCase()}</div>
            <div style={{ fontSize: 28, color: "rgba(255,255,255,.55)", marginTop: 8, padding: "0 90px" }}>{JOBS[s.job]}</div>
          </div>
          {/* track + waveform crossing the center playhead */}
          <div style={{ position: "absolute", top: 820, left: 0, right: 0, height: 260 }}>
            <div style={{ position: "absolute", top: 129, left: 0, right: 0, height: 2, background: "#ffffff22" }} />
            {[i - 1, i, i + 1].filter((k) => k >= 0 && k < SOUNDS.length).map((k) => {
              const sk = SOUNDS[k], w = Math.max(160, Math.min(sk.dur, 2.6) * PX);
              const x = 540 + (STARTS[k] - f) / fps * PX;
              return (
                <div key={k} style={{ position: "absolute", left: x, top: 40, width: w, height: 180, borderRadius: 26, background: k === i ? `${JC[sk.job]}22` : "#ffffff0d",
                  border: `2px solid ${k === i ? JC[sk.job] : "#ffffff22"}`, display: "flex", alignItems: "center", gap: 3, padding: "0 14px", boxShadow: k === i ? `0 0 40px ${JC[sk.job]}44` : "none" }}>
                  {sk.peaks.map((p, j) => <div key={j} style={{ flex: 1, height: `${8 + p * 82}%`, borderRadius: 3, background: k === i ? JC[sk.job] : "#ffffff55" }} />)}
                </div>
              );
            })}
            <div style={{ position: "absolute", left: 538, top: 0, width: 4, height: 260, background: "#fff", boxShadow: "0 0 18px #fff" }} />
            <div style={{ position: "absolute", left: 522, top: -14, width: 0, height: 0, borderLeft: "18px solid transparent", borderRight: "18px solid transparent", borderTop: "26px solid #fff" }} />
          </div>
          <div style={{ position: "absolute", top: 1160, left: 0, right: 0, textAlign: "center", transform: `translateY(${(1 - pl) * 20}px)`, opacity: pl }}>
            <div style={{ display: "inline-block", fontFamily: "monospace", fontSize: 46, fontWeight: 700, padding: "14px 34px", borderRadius: 22, background: "#ffffff12", border: "1px solid #ffffff2a" }}>{s.id}</div>
            <div style={{ fontSize: 38, fontWeight: 700, marginTop: 30, padding: "0 80px", lineHeight: 1.25 }}>{s.use}</div>
            <div style={{ fontSize: 28, marginTop: 22, color: s.origin === "synth" ? "#FF9F0A" : "rgba(255,255,255,.5)" }}>
              {s.origin === "synth" ? "stand-in · replace with the original" : s.origin === "lifted" ? "from a reference reel" : "real recording"} · vol {s.vol}
            </div>
          </div>
          <div style={{ position: "absolute", bottom: 120, left: 0, right: 0, textAlign: "center", fontSize: 30, color: "rgba(255,255,255,.45)", fontVariantNumeric: "tabular-nums" }}>{i + 1} / {SOUNDS.length}</div>
          <div style={{ position: "absolute", bottom: 90, left: 120, right: 120, height: 6, borderRadius: 3, background: "#ffffff14" }}>
            <div style={{ width: `${((i + Math.min(1, t / (slot(s) / fps))) / SOUNDS.length) * 100}%`, height: "100%", borderRadius: 3, background: c }} />
          </div>
        </>
      )}
      {SOUNDS.map((sk, k) => (
        <Sequence key={sk.id} from={STARTS[k]} durationInFrames={slot(sk)} layout="none">
          <Audio src={staticFile(sk.file)} volume={Math.min(1, sk.vol * 1.6)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const h = typeof document !== "undefined" ? delayRender("fonts") : null;
if (h !== null) Promise.all(["500 40px Inter", "700 40px Inter", "800 40px Inter", "900 40px 'Nunito Sans'"].map((x) => document.fonts.load(x))).then(() => continueRender(h));
const Root: React.FC = () => <Composition id="SfxDemo" component={Demo} durationInFrames={TOTAL} fps={FPS} width={1080} height={1920} />;
registerRoot(Root);
