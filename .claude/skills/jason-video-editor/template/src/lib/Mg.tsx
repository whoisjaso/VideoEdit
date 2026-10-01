import React from "react";
import { AbsoluteFill, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { clamp } from "../fx";
import { theme } from "../theme";
import { G, R, Y, glass } from "./Ios";

/**
 * Episode #3 motion graphics (Jason: "motion graphics instead of B-roll images").
 * Language benchmarked against v9 (dark UI takeovers, staggered cards, green counters),
 * v19 (clean blur-in kinetic type) and v21 (one accent colour, designed beat per sentence).
 * iOS rules: no-bounce springs, blur-in, frosted glass, real brand logos (simple-icons).
 */
const IOS = { damping: 26, stiffness: 170, mass: 0.9 };
const POP = { damping: 12, stiffness: 190, mass: 0.7 };
const ease = { ...clamp, easing: theme.ease.out };
const fontUI = "Inter";

export const useWin = (from: number, to: number, cfg = IOS) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - from, fps, config: cfg });
  const out = interpolate(f, [to - 7, to], [1, 0], { ...clamp, easing: theme.ease.in });
  return { f, fps, t: f - from, p, out, on: f >= from - 1 && f < to };
};
const blurIn = (p: number, out = 1, dy = 30): React.CSSProperties => ({
  opacity: Math.min(1, p * 1.3) * out, filter: `blur(${(1 - p) * 12 + (1 - out) * 10}px)`, transform: `translateY(${(1 - p) * dy}px) scale(${0.96 + 0.04 * p})`,
});
const Logo: React.FC<{ name: string; color: string; size?: number; bg?: string; radius?: number }> = ({ name, color, size = 84, bg = "#fff", radius = 22 }) => (
  <div style={{ width: size, height: size, borderRadius: radius, background: bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
    <div style={{ width: size * 0.6, height: size * 0.6, background: color, WebkitMaskImage: `url(${staticFile(`logos/${name}.svg`)})`, WebkitMaskSize: "contain", WebkitMaskRepeat: "no-repeat", WebkitMaskPosition: "center" }} />
  </div>
);

/** v9 takeover backdrop: charcoal, faint giant watermark, drifting particles, fades in */
export const Takeover: React.FC<{ from: number; to: number; mark?: React.ReactNode; tint?: string; children: React.ReactNode }> = ({ from, to, mark, tint = "#0C0C10", children }) => {
  const { f, on } = useWin(from, to);
  if (!on) return null;
  const fade = Math.min(interpolate(f, [from, from + 7], [0, 1], ease), interpolate(f, [to - 7, to], [1, 0], clamp));
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, #1d1d24 0%, ${tint} 65%)`, opacity: fade, overflow: "hidden" }}>
      {mark && <div style={{ position: "absolute", right: -220, bottom: -160, opacity: 0.06, transform: `rotate(${(f - from) * 0.08}deg)` }}>{mark}</div>}
      {Array.from({ length: 26 }).map((_, i) => (
        <div key={i} style={{ position: "absolute", left: `${random(`x${i}`) * 100}%`, top: `${((random(`y${i}`) * 100 - (f - from) * (0.08 + random(`s${i}`) * 0.1)) % 100 + 100) % 100}%`,
          width: 3 + random(`r${i}`) * 4, height: 3 + random(`r${i}`) * 4, borderRadius: 9, background: "rgba(255,255,255,0.18)" }} />
      ))}
      <AbsoluteFill style={{ transform: `scale(${1.04 - 0.04 * fade})` }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/** iOS Notes (dark): title + lines that type on at their spoken frame, blinking cursor */
export const Notes: React.FC<{ from: number; to: number; title: string; lines: { text: string; at: number }[]; top?: number; empty?: boolean }> = ({ from, to, title, lines, top = 130, empty }) => {
  const { f, p, out, on } = useWin(from, to);
  if (!on) return null;
  const typed = lines.map((l) => l.text.slice(0, Math.max(0, Math.floor((f - l.at) * 1.6))));
  const cur = Math.floor(f / 15) % 2 === 0;
  return (
    <div style={{ position: "absolute", top, left: 60, right: 60, ...glass, background: "rgba(28,28,30,0.9)", padding: "30px 38px 40px", ...blurIn(p, out, -40) }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", color: "#FFD60A", fontSize: 32, fontWeight: 600, marginBottom: 18 }}>
        <span>‹ Notes</span><span style={{ fontSize: 30 }}>Done</span>
      </div>
      <div style={{ fontSize: 50, fontWeight: 700, color: "#fff", lineHeight: 1.15 }}>{title}</div>
      <div style={{ fontSize: 26, color: "rgba(255,255,255,.45)", margin: "8px 0 18px" }}>Today · 2:14 AM</div>
      {typed.map((t, i) => (t || i === 0) && (
        <div key={i} style={{ fontSize: 44, color: "#fff", lineHeight: 1.35, display: "flex", gap: 14 }}>
          <span style={{ color: "#FFD60A" }}>{t ? "•" : ""}</span><span>{t}{i === typed.filter(Boolean).length - 1 && cur ? <span style={{ color: "#FFD60A" }}>|</span> : null}</span>
        </div>
      ))}
      {empty && cur && <span style={{ fontSize: 48, color: "#FFD60A" }}>|</span>}
    </div>
  );
};

/** iMessage / app notification banner with a real logo */
export const Banner: React.FC<{ at: number; until: number; logo: string; color: string; app: string; title: string; body: string; top?: number; logoBg?: string }> = ({ at, until, logo, color, app, title, body, top = 90, logoBg }) => {
  const { p, out, on } = useWin(at, until);
  if (!on) return null;
  return (
    <div style={{ position: "absolute", top, left: 50, right: 50, ...glass, borderRadius: 44, padding: "24px 28px", display: "flex", gap: 22, alignItems: "center", ...blurIn(p, out, -110) }}>
      <Logo name={logo} color={logoBg ? "#fff" : color} bg={logoBg ?? "#fff"} />
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 27, color: "rgba(255,255,255,.6)", fontWeight: 600, letterSpacing: "0.02em" }}><span>{app}</span><span>now</span></div>
        <div style={{ fontSize: 36, fontWeight: 700, marginTop: 2 }}>{title}</div>
        <div style={{ fontSize: 33, color: "rgba(255,255,255,.85)" }}>{body}</div>
      </div>
    </div>
  );
};

/** stacked banners (newest in front, older collapse behind) */
export const BannerStack: React.FC<{ items: { at: number; logo: string; color: string; logoBg?: string; app: string; title: string; body: string }[]; until: number; top?: number }> = ({ items, until, top = 90 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {items.map((it, i) => {
        const depth = items.slice(i + 1).reduce((d, n) => d + spring({ frame: f - n.at, fps, config: IOS }), 0);
        if (depth > 2.9) return null;
        return (
          <div key={it.at} style={{ position: "absolute", inset: 0, transform: `translateY(${-depth * 18}px) scale(${1 - depth * 0.05})`, transformOrigin: "50% 0%", opacity: 1 - depth * 0.3 }}>
            <Banner {...it} until={until} top={top} />
          </div>
        );
      })}
    </>
  );
};

/** Reminders list that ticks as each grade is spoken + a rolling "grade" numeral */
export const Grades: React.FC<{ from: number; to: number; items: { label: string; n: number; at: number }[] }> = ({ from, to, items }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const done = items.filter((i) => f >= i.at);
  const n = done.length ? done[done.length - 1].n : 0;
  return (
    <Takeover from={from} to={to}>
      <div style={{ position: "absolute", top: 170, left: 0, right: 0, textAlign: "center", fontFamily: "Nunito Sans", fontWeight: 900, color: Y, fontSize: 300, lineHeight: 1, letterSpacing: "-0.04em" }}>
        {n ? `${n}${n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th"}` : ""}
      </div>
      <div style={{ position: "absolute", top: 490, left: 0, right: 0, textAlign: "center", fontFamily: fontUI, fontWeight: 600, color: "rgba(255,255,255,.6)", fontSize: 40, letterSpacing: "0.3em" }}>GRADE</div>
      <div style={{ position: "absolute", top: 620, left: 90, right: 90, ...glass, padding: "18px 34px" }}>
        <div style={{ fontSize: 30, color: "#0A84FF", fontWeight: 700, padding: "10px 0 6px" }}>School · told what to do</div>
        {items.map((it) => {
          const p = spring({ frame: f - it.at, fps, config: POP });
          const on = f >= it.at;
          return (
            <div key={it.label} style={{ display: "flex", alignItems: "center", gap: 24, padding: "16px 0", borderBottom: "1px solid rgba(255,255,255,.08)" }}>
              <div style={{ width: 46, height: 46, borderRadius: 23, border: `3px solid ${on ? "#0A84FF" : "rgba(255,255,255,.35)"}`, background: on ? "#0A84FF" : "transparent", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${on ? 0.7 + 0.3 * p : 1})` }}>
                {on && <span style={{ color: "#fff", fontSize: 30, fontWeight: 900 }}>✓</span>}
              </div>
              <span style={{ fontSize: 44, color: on ? "rgba(255,255,255,.45)" : "#fff", textDecoration: on ? "line-through" : "none" }}>{it.label}</span>
            </div>
          );
        })}
      </div>
    </Takeover>
  );
};

/** graduation cap drops in with gold confetti */
export const Graduate: React.FC<{ at: number; until: number }> = ({ at, until }) => {
  const { f, fps, t, out, on } = useWin(at, until);
  if (!on) return null;
  const drop = spring({ frame: t, fps, config: { damping: 10, stiffness: 150, mass: 0.8 } });
  return (
    <AbsoluteFill style={{ opacity: out, pointerEvents: "none" }}>
      {Array.from({ length: 40 }).map((_, i) => {
        const a = random(`a${i}`) * Math.PI * 2, v = 8 + random(`v${i}`) * 16, tt = Math.max(0, t);
        return <div key={i} style={{ position: "absolute", left: 540 + Math.cos(a) * v * tt, top: 330 + Math.sin(a) * v * tt + tt * tt * 0.5, width: 14, height: 8,
          background: i % 3 ? Y : "#fff", transform: `rotate(${tt * 20 + i * 30}deg)`, opacity: interpolate(tt, [0, 40], [1, 0], clamp) }} />;
      })}
      <div style={{ position: "absolute", top: interpolate(drop, [0, 1], [-300, 170]), left: 0, right: 0, textAlign: "center", fontSize: 230, transform: `rotate(${interpolate(drop, [0, 1], [-25, -8])}deg)` }}>🎓</div>
    </AbsoluteFill>
  );
};

/** the goldfish: small bowl → released into the ocean */
export const Goldfish: React.FC<{ from: number; release: number; ocean: number; to: number }> = ({ from, release, ocean, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const r = spring({ frame: f - release, fps, config: { damping: 30, stiffness: 60, mass: 1 } });
  const bowl = interpolate(r, [0, 1], [260, 2400]);
  const w = spring({ frame: f - ocean, fps, config: IOS });
  const swim = Math.sin(f / 7) * 18;
  return (
    <Takeover from={from} to={to} tint="#02101c">
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 42%, rgba(20,90,150,${0.9 * r}) 0%, rgba(4,30,60,${r}) 45%, rgba(2,10,20,${r}) 100%)` }} />
      {/* bowl */}
      <div style={{ position: "absolute", left: 540 - bowl / 2, top: 800 - bowl / 2, width: bowl, height: bowl, borderRadius: "50%",
        border: `${Math.max(0, 6 - r * 6)}px solid rgba(255,255,255,${0.55 * (1 - r)})`, background: `radial-gradient(circle at 40% 35%, rgba(120,190,255,${0.35 * (1 - r)}), rgba(40,110,190,${0.25 * (1 - r)}))`,
        boxShadow: `inset 0 -20px 60px rgba(255,255,255,${0.15 * (1 - r)})` }} />
      <div style={{ position: "absolute", left: 540 - 80 + swim + r * 160, top: 720 + Math.cos(f / 9) * 10 - r * 120, fontSize: 150 - r * 70, transform: `scaleX(-1) rotate(${swim / 3}deg)` }}>🐠</div>
      {/* ocean: tiny fish, lots of space */}
      {r > 0.3 && Array.from({ length: 14 }).map((_, i) => (
        <div key={i} style={{ position: "absolute", left: `${(random(`fx${i}`) * 120 - 10 + (f - release) * (0.05 + random(`fv${i}`) * 0.1)) % 110}%`, top: `${15 + random(`fy${i}`) * 75}%`,
          fontSize: 34 + random(`fs${i}`) * 30, opacity: 0.35 * r }}>{i % 3 ? "🐟" : "🐡"}</div>
      ))}
      <div style={{ position: "absolute", top: 1250, left: 0, right: 0, textAlign: "center", fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 210, color: Y, letterSpacing: "-0.03em", ...blurIn(w) }}>OCEAN</div>
    </Takeover>
  );
};

/** so many ways → the same destination: paths draw from YOU to one glowing point */
export const Paths: React.FC<{ from: number; to: number; words: { text: string; at: number }[]; dest: number }> = ({ from, to, words, dest }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const N = 16, sx = 540, sy = 1500, dx = 540, dy = 380;
  const g = spring({ frame: f - dest, fps, config: POP });
  return (
    <Takeover from={from} to={to}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: N }).map((_, i) => {
          const c1x = 540 + (random(`c1${i}`) - 0.5) * 1500, c1y = 1150 - random(`c1y${i}`) * 300, c2x = 540 + (random(`c2${i}`) - 0.5) * 1400, c2y = 700 + random(`c2y${i}`) * 200;
          const d = `M${sx},${sy} C${c1x},${c1y} ${c2x},${c2y} ${dx},${dy}`;
          const st = from + 8 + i * ((dest - from - 30) / N);
          const q = interpolate(f, [st, st + 26], [0, 1], ease);
          return <path key={i} d={d} stroke={f >= dest ? Y : "rgba(255,255,255,0.55)"} strokeOpacity={f >= dest ? 0.5 + 0.5 * g : 1} strokeWidth={4} fill="none" strokeDasharray={2200} strokeDashoffset={2200 * (1 - q)} strokeLinecap="round" />;
        })}
      </svg>
      <div style={{ position: "absolute", left: sx - 70, top: sy - 30, width: 140, textAlign: "center", fontFamily: fontUI, fontWeight: 800, fontSize: 40, color: "#fff", background: "#fff1", borderRadius: 30, padding: "8px 0", border: "2px solid #fff6" }}>YOU</div>
      <div style={{ position: "absolute", left: dx - 70, top: dy - 70, width: 140, height: 140, borderRadius: 70, background: Y, boxShadow: `0 0 ${40 + 80 * g}px ${Y}`, transform: `scale(${0.6 + 0.4 * g})`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 70 }}>★</div>
      {words.map((w, i) => {
        const p = spring({ frame: f - w.at, fps, config: IOS });
        if (f < w.at - 1) return null;
        return <div key={w.text} style={{ position: "absolute", top: 820 + i * 120, left: i % 2 ? 560 : 120, fontFamily: fontUI, fontWeight: 700, fontSize: 52, color: "#fff", ...blurIn(p) }}>{w.text}</div>;
      })}
      <div style={{ position: "absolute", top: 180, left: 0, right: 0, textAlign: "center", fontFamily: fontUI, fontWeight: 700, letterSpacing: "0.25em", fontSize: 34, color: Y, opacity: g }}>SAME DESTINATION</div>
    </Takeover>
  );
};

/** green rolling counter (v9 / §18 numbers roll) */
export const Counter: React.FC<{ from: number; to: number; steps: { at: number; dur: number; value: number }[]; suffix?: string; top?: number }> = ({ from, to, steps, suffix, top = 150 }) => {
  const { f, p, out, on } = useWin(from, to);
  if (!on) return null;
  let v = 0;
  for (const s of steps) if (f >= s.at) v = interpolate(f, [s.at, s.at + s.dur], [v, s.value], ease);
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, textAlign: "center", ...blurIn(p, out) }}>
      <div style={{ display: "inline-block", ...glass, padding: "26px 46px", borderRadius: 40 }}>
        <div style={{ fontSize: 30, color: "rgba(255,255,255,.6)", fontWeight: 600, letterSpacing: "0.1em" }}>MONTHLY GOAL</div>
        <div style={{ fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 150, color: G, lineHeight: 1.05, textShadow: `0 0 40px ${G}66`, fontVariantNumeric: "tabular-nums" }}>
          ${Math.round(v).toLocaleString("en-US")}<span style={{ fontSize: 56, color: "rgba(255,255,255,.7)" }}>{suffix}</span>
        </div>
      </div>
    </div>
  );
};

/** "you can sell…" tiles pop in one by one, then multiply until it's overwhelming */
export const SellTiles: React.FC<{ from: number; to: number; tiles: { emoji: string; label: string; sub?: string; at: number }[]; flood: number }> = ({ from, to, tiles, flood }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const EXTRA = ["📦", "👟", "💻", "🏠", "📱", "🎧", "🧴", "🍔", "💍", "🎮", "📈", "🛠️", "🎨", "📚", "🚚", "🪙", "🧢", "📸", "🕶️", "🏋️"];
  return (
    <Takeover from={from} to={to} mark={<Logo name="applepay" color="#fff" bg="transparent" size={900} />}>
      <div style={{ position: "absolute", top: 180, left: 0, right: 0, textAlign: "center", fontFamily: fontUI, fontWeight: 700, fontSize: 40, color: "rgba(255,255,255,.55)", letterSpacing: "0.2em" }}>YOU CAN SELL…</div>
      <div style={{ position: "absolute", top: 300, left: 60, right: 60, display: "flex", flexWrap: "wrap", gap: 30, justifyContent: "center" }}>
        {tiles.map((t) => {
          const p = spring({ frame: f - t.at, fps, config: POP });
          if (f < t.at - 1) return null;
          return (
            <div key={t.label} style={{ width: 280, height: 300, borderRadius: 48, background: "#fff", boxShadow: "0 24px 50px rgba(0,0,0,.45)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              transform: `scale(${p}) rotate(${(1 - p) * -12}deg)`, fontFamily: fontUI }}>
              <div style={{ fontSize: 130 }}>{t.emoji}</div>
              <div style={{ fontSize: 34, fontWeight: 800, color: "#111", marginTop: 6 }}>{t.label}</div>
              {t.sub && <div style={{ fontSize: 26, fontWeight: 700, color: "#0A7A3C" }}>{t.sub}</div>}
            </div>
          );
        })}
      </div>
      {f >= flood && EXTRA.map((e, i) => {
        const st = flood + i * 1.5, p = spring({ frame: f - st, fps, config: POP });
        if (f < st) return null;
        return <div key={i} style={{ position: "absolute", left: 40 + random(`tx${i}`) * 880, top: 260 + random(`ty${i}`) * 1250, width: 150, height: 160, borderRadius: 34, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 80, boxShadow: "0 16px 30px rgba(0,0,0,.45)", transform: `scale(${p}) rotate(${(random(`tr${i}`) - 0.5) * 30}deg)` }}>{e}</div>;
      })}
    </Takeover>
  );
};

/** overwhelmed: notifications rain down, then everything freezes grey ("not doing anything") */
export const Overwhelm: React.FC<{ from: number; freeze: number; to: number }> = ({ from, freeze, to }) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const tt = Math.min(f, freeze) - from;
  const APPS: [string, string][] = [["📈", "Start a business"], ["🎓", "Go back to school"], ["🚗", "Sell cars"], ["💻", "Learn to code"], ["🎥", "Start a YouTube"], ["🏠", "Real estate"], ["📦", "Dropshipping"], ["🤖", "Learn AI"], ["💪", "Get a trainer cert"], ["🎵", "Make music"]];
  const grey = interpolate(f, [freeze, freeze + 10], [0, 1], ease);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", backdropFilter: grey ? `grayscale(${grey}) brightness(${1 - 0.35 * grey})` : undefined }}>
      {Array.from({ length: 22 }).map((_, i) => {
        const st = i * 2.2, y = -200 + Math.max(0, tt - st) * (38 + random(`v${i}`) * 20);
        if (tt < st || y > 2000) return null;
        const [e, s] = APPS[i % APPS.length];
        return (
          <div key={i} style={{ position: "absolute", top: y, left: 40 + random(`l${i}`) * 420, width: 600, ...glass, borderRadius: 34, padding: "18px 24px", display: "flex", gap: 16, alignItems: "center",
            transform: `rotate(${(random(`r${i}`) - 0.5) * 16}deg)`, filter: `grayscale(${grey})` }}>
            <span style={{ fontSize: 50 }}>{e}</span><span style={{ fontSize: 36, fontWeight: 700 }}>{s}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** bank card (Chase) → Safari tabs piling up → progress stuck at 0% */
export const MoneyResearch: React.FC<{ money: number; research: number; never: number; doAt: number; to: number }> = ({ money, research, never, doAt, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < money - 1 || f >= to) return null;
  const pm = spring({ frame: f - money, fps, config: IOS });
  const out = interpolate(f, [to - 7, to], [1, 0], clamp);
  const TABS = ["how to make money online", "best side hustles 2026", "is dropshipping dead?", "how to start a business", "what should I do with my life", "passive income ideas", "how to find your purpose"];
  const nt = Math.max(0, Math.min(TABS.length, Math.floor((f - research + 14) / 5)));
  const pn = spring({ frame: f - never, fps, config: IOS });
  const shake = f >= doAt && f < doAt + 10 ? Math.sin((f - doAt) * 3) * 12 : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: out }}>
      <div style={{ position: "absolute", top: 110, left: 70, right: 70, height: 300, borderRadius: 36, background: "linear-gradient(135deg,#117ACA,#0b3f7a)", boxShadow: "0 24px 60px rgba(0,0,0,.5)", padding: 34, fontFamily: fontUI, color: "#fff", ...blurIn(pm, 1, -40) }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Logo name="chase" color="#117ACA" size={70} radius={16} /><span style={{ fontSize: 30, opacity: 0.8 }}>Savings ···· 4821</span>
        </div>
        <div style={{ fontSize: 30, opacity: 0.75, marginTop: 34 }}>Available balance</div>
        <div style={{ fontSize: 96, fontWeight: 800, fontVariantNumeric: "tabular-nums" }}>${Math.round(interpolate(f, [money, money + 24], [0, 18420], ease)).toLocaleString("en-US")}.00</div>
      </div>
      {f >= research - 14 && TABS.slice(0, nt).map((t, i) => (
        <div key={t} style={{ position: "absolute", top: 470 + i * 26, left: 70 + i * 8, right: 70 - i * 8, height: 110, borderRadius: 24, background: "rgba(40,40,46,0.95)", border: "1px solid #ffffff22",
          display: "flex", alignItems: "center", gap: 18, padding: "0 26px", fontFamily: fontUI, color: "#fff", fontSize: 32, boxShadow: "0 10px 26px rgba(0,0,0,.4)" }}>
          <Logo name="safari" color="#006CFF" size={56} radius={14} /><span>{t}</span>
        </div>
      ))}
      {f >= research && (
        <div style={{ position: "absolute", top: 400, right: 80, fontFamily: fontUI, fontWeight: 800, fontSize: 40, color: "#fff", background: R, borderRadius: 30, padding: "6px 22px" }}>{Math.min(47, Math.floor((f - research) * 1.6) + 7)} tabs</div>
      )}
      {f >= never - 1 && (
        <div style={{ position: "absolute", top: 760, left: 90, right: 90, ...glass, padding: "28px 34px", transform: `translateX(${shake}px)`, ...blurIn(pn) }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 32, fontWeight: 700 }}><span>Actually started</span><span style={{ color: R }}>0%</span></div>
          <div style={{ height: 22, borderRadius: 11, background: "#ffffff22", marginTop: 18 }}><div style={{ width: "1.5%", height: "100%", borderRadius: 11, background: R }} /></div>
        </div>
      )}
    </div>
  );
};

/** thinking (endless loading) → doing (bar fills) */
export const ThinkDo: React.FC<{ think: number; doAt: number; to: number }> = ({ think, doAt, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < think - 1 || f >= to) return null;
  const p = spring({ frame: f - think, fps, config: IOS });
  const d = spring({ frame: f - doAt, fps, config: IOS });
  const out = interpolate(f, [to - 7, to], [1, 0], clamp);
  const fill = interpolate(f, [doAt, doAt + 30], [0, 100], ease);
  const thinking = f < doAt;
  return (
    <div style={{ position: "absolute", top: 120, left: 80, right: 80, opacity: out }}>
      <div style={{ ...glass, padding: "30px 36px", ...blurIn(p, 1, -40) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
          {thinking ? (
            <svg width="64" height="64" viewBox="0 0 64 64" style={{ transform: `rotate(${f * 12}deg)` }}>
              {Array.from({ length: 8 }).map((_, i) => <rect key={i} x="29" y="4" width="6" height="16" rx="3" fill="#fff" opacity={0.2 + (i / 8) * 0.8} transform={`rotate(${i * 45} 32 32)`} />)}
            </svg>
          ) : <div style={{ width: 64, height: 64, borderRadius: 32, background: G, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, fontWeight: 900, transform: `scale(${d})` }}>✓</div>}
          <div style={{ fontSize: 44, fontWeight: 700 }}>{thinking ? "Thinking about my purpose…" : "Doing"}</div>
        </div>
        <div style={{ height: 22, borderRadius: 11, background: "#ffffff22", marginTop: 24, overflow: "hidden" }}>
          {thinking
            ? <div style={{ width: "30%", height: "100%", borderRadius: 11, background: "#ffffff55", transform: `translateX(${((f * 9) % 400) - 100}%)` }} />
            : <div style={{ width: `${fill}%`, height: "100%", borderRadius: 11, background: G, boxShadow: `0 0 20px ${G}` }} />}
        </div>
        <div style={{ fontSize: 30, color: thinking ? "rgba(255,255,255,.55)" : G, marginTop: 12, fontWeight: 600 }}>{thinking ? "still loading · 3 years" : `${Math.round(fill)}% · purpose found`}</div>
      </div>
    </div>
  );
};

/** Chess.com: daily-streak notification + board + streak grid lighting up */
export const Chess: React.FC<{ from: number; chess: number; streak: number; purpose: number; to: number }> = ({ from, chess, streak, purpose, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pc = spring({ frame: f - chess, fps, config: IOS });
  const pp = spring({ frame: f - purpose, fps, config: POP });
  const days = Math.max(0, Math.min(35, Math.floor((f - streak) * 1.4)));
  return (
    <Takeover from={from} to={to} tint="#15130f" mark={<Logo name="chessdotcom" color="#81B64C" bg="transparent" size={900} />}>
      <div style={{ position: "absolute", top: 120, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 20, ...blurIn(pc) }}>
        <Logo name="chessdotcom" color="#fff" bg="#81B64C" size={96} radius={24} />
        <span style={{ fontFamily: fontUI, fontWeight: 800, fontSize: 64, color: "#fff" }}>Chess.com</span>
      </div>
      <div style={{ position: "absolute", top: 290, left: 190, width: 700, height: 700, display: "grid", gridTemplateColumns: "repeat(8,1fr)", borderRadius: 18, overflow: "hidden",
        boxShadow: "0 30px 70px rgba(0,0,0,.6)", transform: `perspective(1400px) rotateX(${interpolate(pc, [0, 1], [35, 12])}deg) scale(${0.9 + 0.1 * pc})`, opacity: pc * interpolate(f, [purpose - 2, purpose + 8], [1, 0.25], clamp) }}>
        {Array.from({ length: 64 }).map((_, i) => (
          <div key={i} style={{ background: (Math.floor(i / 8) + i) % 2 ? "#769656" : "#EEEED2", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 70, color: i < 16 ? "#222" : "#fff",
            textShadow: i >= 48 ? "0 2px 4px #0008" : "none" }}>
            {i === 4 ? (f >= purpose ? "" : "♚") : i < 8 ? "♜♞♝♛♚♝♞♜"[i] : i < 16 ? "♟" : i >= 56 ? "♜♞♝♛♚♝♞♜"[i - 56] : i >= 48 ? "♟" : ""}
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", top: 1060, left: 150, right: 150, display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 14 }}>
        {Array.from({ length: 35 }).map((_, i) => <div key={i} style={{ height: 70, borderRadius: 14, background: i < days ? "#81B64C" : "#ffffff14", boxShadow: i < days ? "0 0 14px #81B64C88" : "none" }} />)}
      </div>
      <div style={{ position: "absolute", top: 1440, left: 0, right: 0, textAlign: "center", fontFamily: fontUI, fontWeight: 800, fontSize: 52, color: "#fff" }}>🔥 {days}-day streak</div>
      {f >= purpose - 1 && (
        <div style={{ position: "absolute", top: 400, left: 0, right: 0, textAlign: "center", transform: `scale(${pp})` }}>
          <div style={{ fontSize: 220, color: Y, textShadow: `0 0 60px ${Y}` }}>♚</div>
          <div style={{ fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 110, color: Y, letterSpacing: "-0.02em" }}>PURPOSE</div>
        </div>
      )}
    </Takeover>
  );
};

/** same life on repeat: a week in Calendar with the identical block copied every day */
export const SameWeek: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const { f, p, out, on } = useWin(from, to);
  if (!on) return null;
  const D = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
  return (
    <div style={{ position: "absolute", top: 110, left: 60, right: 60, ...glass, padding: 28, ...blurIn(p, out, -40) }}>
      <div style={{ fontSize: 30, fontWeight: 700, color: "#FF453A", marginBottom: 14 }}>Calendar · every week</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 10 }}>
        {D.map((d, i) => {
          const st = from + 6 + i * 6, q = interpolate(f, [st, st + 8], [0, 1], ease);
          return (
            <div key={d} style={{ textAlign: "center" }}>
              <div style={{ fontSize: 24, color: "rgba(255,255,255,.55)", fontWeight: 700 }}>{d}</div>
              {["Wake up", "Scroll", "Same job", "Scroll", "Sleep"].map((b, j) => (
                <div key={b + j} style={{ marginTop: 8, height: 70, borderRadius: 12, background: j === 1 || j === 3 ? "#FF453A55" : "#ffffff22", opacity: q, transform: `translateY(${(1 - q) * 20}px)`,
                  fontSize: 17, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center" }}>{b}</div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** the loop: paradigm · script · cycle spin on a ring (red) */
export const Loop: React.FC<{ from: number; to: number; words: { text: string; at: number }[] }> = ({ from, to, words }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Takeover from={from} to={to} tint="#140a0a">
      <div style={{ position: "absolute", left: 140, top: 560, width: 800, height: 800, transform: `rotate(${(f - from) * 2.2}deg)` }}>
        <svg width="800" height="800" viewBox="0 0 800 800">
          <circle cx="400" cy="400" r="330" stroke="#ffffff22" strokeWidth="26" fill="none" />
          <circle cx="400" cy="400" r="330" stroke={R} strokeWidth="26" fill="none" strokeDasharray="1500 574" strokeLinecap="round" />
          <polygon points="400,40 440,70 400,100" fill={R} transform="rotate(8 400 400)" />
        </svg>
      </div>
      {words.map((w, i) => {
        const p = spring({ frame: f - w.at, fps, config: POP });
        if (f < w.at - 1) return null;
        return <div key={w.text} style={{ position: "absolute", top: 780 + i * 130, left: 0, right: 0, textAlign: "center", fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 110, color: i === words.length - 1 ? R : "#fff", transform: `scale(${p})`, letterSpacing: "-0.02em" }}>{w.text}</div>;
      })}
      <div style={{ position: "absolute", top: 200, left: 0, right: 0, textAlign: "center", fontFamily: fontUI, fontWeight: 700, fontSize: 40, letterSpacing: "0.25em", color: "rgba(255,255,255,.55)" }}>THE SAME…</div>
    </Takeover>
  );
};

/** take a walk: Activity ring closes as the timer runs to 5:00 */
export const Walk: React.FC<{ at: number; five: number; to: number }> = ({ at, five, to }) => {
  const { f, p, out, on } = useWin(at, to);
  if (!on) return null;
  const q = interpolate(f, [at + 6, five + 10], [0, 1], ease);
  const secs = Math.round(q * 300);
  const r = 95;
  return (
    <div style={{ position: "absolute", top: 110, left: 70, right: 70, ...glass, padding: 34, display: "flex", alignItems: "center", gap: 36, ...blurIn(p, out, -40) }}>
      <svg width="240" height="240" viewBox="0 0 220 220">
        <circle cx="110" cy="110" r={r} stroke="#92E82A33" strokeWidth="26" fill="none" />
        <circle cx="110" cy="110" r={r} stroke="#92E82A" strokeWidth="26" fill="none" strokeLinecap="round" strokeDasharray={2 * Math.PI * r} strokeDashoffset={2 * Math.PI * r * (1 - q)} transform="rotate(-90 110 110)" />
        <text x="110" y="128" textAnchor="middle" fontSize="56" fill="#fff">🚶</text>
      </svg>
      <div style={{ fontFamily: fontUI }}>
        <div style={{ fontSize: 30, color: "rgba(255,255,255,.6)", fontWeight: 600, letterSpacing: "0.05em" }}>OUTDOOR WALK</div>
        <div style={{ fontSize: 110, fontWeight: 800, color: "#92E82A", fontVariantNumeric: "tabular-nums", lineHeight: 1 }}>{Math.floor(secs / 60)}:{String(secs % 60).padStart(2, "0")}</div>
        <div style={{ fontSize: 32, color: "rgba(255,255,255,.75)" }}>every single day</div>
      </div>
    </div>
  );
};

/** the doors: one lights up and opens */
export const Doors: React.FC<{ from: number; open: number; life: number; to: number }> = ({ from, open, life, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const o = spring({ frame: f - open, fps, config: { damping: 20, stiffness: 60, mass: 1 } });
  const l = interpolate(f, [life, life + 20], [0, 1], ease);
  return (
    <Takeover from={from} to={to}>
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 55%, rgba(255,210,74,${0.55 * l}) 0%, rgba(255,210,74,0) ${30 + 60 * l}%)` }} />
      <div style={{ position: "absolute", top: 640, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 46, perspective: 1200 }}>
        {[0, 1, 2].map((i) => {
          const gold = i === 1;
          return (
            <div key={i} style={{ width: 240, height: 480, position: "relative", background: gold ? `rgba(255,210,74,${0.2 + 0.8 * o})` : "#15151b", boxShadow: gold ? `0 0 ${120 * o}px ${Y}` : "none", borderRadius: "14px 14px 0 0", border: "4px solid #333" }}>
              <div style={{ position: "absolute", inset: 0, background: gold ? "#2a2418" : "#22222a", borderRadius: "10px 10px 0 0", transformOrigin: "0% 50%", transform: `rotateY(${gold ? -o * 100 : 0}deg)`, border: "2px solid #444" }}>
                <div style={{ position: "absolute", right: 24, top: 240, width: 18, height: 18, borderRadius: 9, background: Y }} />
              </div>
            </div>
          );
        })}
      </div>
    </Takeover>
  );
};

/** kinetic "DOING" ×3 */
export const DoingStack: React.FC<{ ats: number[]; to: number }> = ({ ats, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < ats[0] - 1 || f >= to) return null;
  const out = interpolate(f, [to - 6, to], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", top: 90, left: 0, right: 0, textAlign: "center", opacity: out }}>
      {ats.map((a, i) => {
        const p = spring({ frame: f - a, fps, config: POP });
        if (f < a - 1) return null;
        return <div key={a} style={{ fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 150 - i * 10, lineHeight: 0.95, color: G, opacity: 1 - i * 0.18, transform: `scale(${p})`, textShadow: `0 0 40px ${G}55`, letterSpacing: "-0.03em" }}>DOING</div>;
      })}
    </div>
  );
};

/** plans ✓ actions ✓ → EXECUTE */
export const Execute: React.FC<{ plans: number; actions: number; god: number; exec: number; to: number }> = ({ plans, actions, god, exec, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < plans - 1 || f >= to) return null;
  const pe = spring({ frame: f - exec, fps, config: { damping: 9, stiffness: 260, mass: 0.8 } });
  const row = (label: string, at: number) => {
    const p = spring({ frame: f - at, fps, config: POP });
    return f >= at - 1 ? (
      <div style={{ display: "flex", alignItems: "center", gap: 22, padding: "14px 0", ...blurIn(p) }}>
        <div style={{ width: 52, height: 52, borderRadius: 26, background: G, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34, fontWeight: 900 }}>✓</div>
        <span style={{ fontSize: 50, fontWeight: 700 }}>{label}</span>
      </div>
    ) : null;
  };
  return (
    <div style={{ position: "absolute", top: 110, left: 90, right: 90 }}>
      <div style={{ ...glass, padding: "20px 36px" }}>{row("Plans", plans)}{row("Actions", actions)}{row("Committed to God", god)}</div>
      {f >= exec - 1 && <div style={{ marginTop: 26, textAlign: "center", fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 170, color: Y, transform: `scale(${interpolate(pe, [0, 1], [2, 1])})`, textShadow: `0 0 60px ${Y}88`, letterSpacing: "-0.03em" }}>EXECUTE</div>}
    </div>
  );
};

/** CTA: comment PURPOSE → DM notification with the AI guide + course link */
export const CtaPurpose: React.FC<{ from: number; dm: number; to: number }> = ({ from, dm, to }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from || f >= to) return null;
  const p = spring({ frame: f - from, fps, config: IOS });
  const typed = "PURPOSE".slice(0, Math.max(0, Math.floor((f - from - 10) / 3)));
  const sent = f >= from + 36;
  const ps = spring({ frame: f - (from + 36), fps, config: POP });
  return (
    <>
      <div style={{ position: "absolute", top: 300, left: 60, right: 60, ...glass, padding: "30px 34px", ...blurIn(p) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 22 }}>
          <Logo name="instagram" color="#fff" bg="linear-gradient(45deg,#FEDA75,#FA7E1E,#D62976,#962FBF,#4F5BD5)" size={64} radius={18} />
          <span style={{ fontSize: 34, fontWeight: 700 }}>Comments</span>
        </div>
        {sent ? (
          <div style={{ display: "flex", gap: 18, alignItems: "center", transform: `scale(${ps})`, transformOrigin: "0 50%" }}>
            <div style={{ width: 64, height: 64, borderRadius: 32, background: "#444", fontSize: 34, display: "flex", alignItems: "center", justifyContent: "center" }}>🙋🏾</div>
            <div><div style={{ fontSize: 26, color: "rgba(255,255,255,.6)" }}>you · now</div><div style={{ fontSize: 60, fontWeight: 900, color: Y, letterSpacing: "0.04em" }}>PURPOSE</div></div>
          </div>
        ) : (
          <div style={{ background: "#ffffff14", borderRadius: 40, padding: "18px 26px", fontSize: 44, fontWeight: 700 }}>{typed}<span style={{ color: Y }}>{Math.floor(f / 12) % 2 ? "|" : ""}</span></div>
        )}
      </div>
      <Banner at={dm} until={to} logo="imessage" color="#34DA50" logoBg="#34DA50" app="MESSAGES" title="Jason" body="Here’s your free AI guide + the course link 🔗" top={80} />
      <div style={{ position: "absolute", top: 700, left: 0, right: 0, textAlign: "center", fontFamily: "Nunito Sans", fontWeight: 900, color: "#fff", ...blurIn(p) }}>
        <div style={{ fontSize: 64 }}>Comment</div>
        <div style={{ fontSize: 170, color: Y, lineHeight: 1, letterSpacing: "-0.02em", textShadow: `0 0 50px ${Y}66` }}>PURPOSE</div>
        <div style={{ fontSize: 44, fontWeight: 600, color: "rgba(255,255,255,.85)", marginTop: 14 }}>I’ll send you my AI guide + course</div>
      </div>
    </>
  );
};

/* ───────────── Episode #4 ("Perceived as nice") additions ───────────── */

/** PERCEIVED nice (mask, red) vs ACTUALLY nice (heart, green): two cards; the "actually" card lands on its word */
export const NiceSplit: React.FC<{ from: number; perceived: number; actually: number; to: number; top?: number }> = ({ from, perceived, actually, to, top = 120 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from - 1 || f >= to) return null;
  const out = interpolate(f, [to - 7, to], [1, 0], clamp);
  const card = (at: number, emoji: string, label: string, color: string, dim: boolean) => {
    const p = spring({ frame: f - at, fps, config: POP });
    if (f < at - 1) return <div style={{ width: 430 }} />;
    return (
      <div style={{ width: 430, height: 430, ...glass, borderRadius: 48, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", border: `3px solid ${color}88`,
        boxShadow: `0 24px 60px rgba(0,0,0,.5), 0 0 ${dim ? 0 : 50}px ${color}55`, transform: `scale(${p}) rotate(${(1 - p) * (color === G ? 10 : -10)}deg)`, opacity: dim ? 0.5 : 1 }}>
        <div style={{ fontSize: 170 }}>{emoji}</div>
        <div style={{ fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: "rgba(255,255,255,.65)", marginTop: 6 }}>{label}</div>
        <div style={{ fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 92, color, letterSpacing: "-0.02em", lineHeight: 1 }}>NICE</div>
      </div>
    );
  };
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 40, opacity: out }}>
      {card(perceived, "🎭", "PERCEIVED", R, f >= actually + 8)}
      {card(actually, "💛", "ACTUALLY", G, false)}
    </div>
  );
};

/** potential meter: a bar fills to 100%, then a sub-label ("Influential") pops */
export const Meter: React.FC<{ from: number; fill: number; sub: number; to: number; label: string; subLabel: string; top?: number }> = ({ from, fill, sub, to, label, subLabel, top = 130 }) => {
  const { f, fps, p, out, on } = useWin(from, to);
  if (!on) return null;
  const q = interpolate(f, [fill, fill + 26], [0.08, 1], ease);
  const ps = spring({ frame: f - sub, fps, config: POP });
  return (
    <div style={{ position: "absolute", top, left: 80, right: 80, ...glass, padding: "30px 36px", ...blurIn(p, out, -40) }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 34, fontWeight: 700 }}><span>{label}</span><span style={{ color: G, fontVariantNumeric: "tabular-nums" }}>{Math.round(q * 100)}%</span></div>
      <div style={{ height: 26, borderRadius: 13, background: "#ffffff22", marginTop: 18, overflow: "hidden" }}>
        <div style={{ width: `${q * 100}%`, height: "100%", borderRadius: 13, background: `linear-gradient(90deg, ${G}, #9BFFC6)`, boxShadow: `0 0 24px ${G}` }} />
      </div>
      {f >= sub - 1 && <div style={{ marginTop: 22, display: "inline-flex", gap: 14, alignItems: "center", background: `${G}22`, border: `2px solid ${G}88`, borderRadius: 40, padding: "10px 26px",
        fontSize: 40, fontWeight: 800, color: G, transform: `scale(${ps})`, transformOrigin: "0 50%" }}>✓ {subLabel}</div>}
    </div>
  );
};

/** comments pour in (other people's opinions) → at `freeze` they grey out and a "0 actually care" pill lands */
export const CommentRain: React.FC<{ from: number; freeze: number; to: number; comments: string[] }> = ({ from, freeze, to, comments }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from || f >= to) return null;
  const tt = Math.min(f, freeze) - from;
  const grey = interpolate(f, [freeze, freeze + 10], [0, 1], ease);
  const pz = spring({ frame: f - freeze, fps, config: POP });
  const out = interpolate(f, [to - 7, to], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: out }}>
      {Array.from({ length: 18 }).map((_, i) => {
        const st = i * 2.6, y = -160 + Math.max(0, tt - st) * (26 + random(`cv${i}`) * 14);
        if (tt < st || y > 640) return null;
        const fadeOut = interpolate(y, [380, 640], [1, 0], clamp); // dissolve before the face (never cover the face)
        return (
          <div key={i} style={{ position: "absolute", top: y, left: 30 + random(`cl${i}`) * 360, width: 660, ...glass, borderRadius: 30, padding: "16px 22px", display: "flex", gap: 16, alignItems: "center", opacity: fadeOut,
            transform: `rotate(${(random(`cr${i}`) - 0.5) * 10}deg)`, filter: `grayscale(${grey}) brightness(${1 - 0.4 * grey})` }}>
            <div style={{ width: 54, height: 54, borderRadius: 27, background: `hsl(${random(`ch${i}`) * 360},40%,45%)`, flexShrink: 0 }} />
            <div><div style={{ fontSize: 22, color: "rgba(255,255,255,.55)", fontWeight: 600 }}>user{Math.floor(random(`cn${i}`) * 9000 + 1000)}</div>
              <div style={{ fontSize: 32, fontWeight: 700 }}>{comments[i % comments.length]}</div></div>
          </div>
        );
      })}
      {f >= freeze && (
        <div style={{ position: "absolute", top: 300, left: 0, right: 0, textAlign: "center", transform: `scale(${pz})` }}>
          <span style={{ ...glass, display: "inline-block", padding: "22px 44px", borderRadius: 60, fontSize: 52, fontWeight: 800, color: "#fff", border: `2px solid ${Y}` }}>
            <span style={{ color: Y }}>0</span> people actually care
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};

/** iOS Settings row: a toggle flips OFF on its word */
export const SettingToggle: React.FC<{ at: number; flip: number; until: number; label: string; top?: number }> = ({ at, flip, until, label, top = 140 }) => {
  const { f, fps, p, out, on } = useWin(at, until);
  if (!on) return null;
  const q = spring({ frame: f - flip, fps, config: IOS });
  const offAmt = f >= flip ? q : 0;
  return (
    <div style={{ position: "absolute", top, left: 70, right: 70, ...glass, padding: "18px 30px", ...blurIn(p, out, -40) }}>
      <div style={{ fontSize: 26, color: "rgba(255,255,255,.5)", fontWeight: 700, letterSpacing: "0.06em", margin: "6px 0 12px" }}>SETTINGS · MINDSET</div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 0" }}>
        <span style={{ fontSize: 42, fontWeight: 600 }}>{label}</span>
        <div style={{ width: 120, height: 72, borderRadius: 36, background: interpolate(offAmt, [0, 1], [0, 1]) > 0.5 ? "#3a3a3c" : "#34C759", position: "relative", flexShrink: 0 }}>
          <div style={{ position: "absolute", top: 5, left: interpolate(offAmt, [0, 1], [53, 5]), width: 62, height: 62, borderRadius: 31, background: "#fff", boxShadow: "0 3px 8px rgba(0,0,0,.35)" }} />
        </div>
      </div>
      <div style={{ fontSize: 30, color: f >= flip ? G : "rgba(255,255,255,.45)", fontWeight: 600, paddingBottom: 8 }}>{f >= flip ? "Rewired ✓" : "On"}</div>
    </div>
  );
};

/** a hater's comment, then the bank balance under their name drops to almost nothing (red) */
export const BrokeHater: React.FC<{ comment: number; broke: number; to: number; text: string; balance?: number }> = ({ comment, broke, to, text, balance = 4.12 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < comment - 1 || f >= to) return null;
  const out = interpolate(f, [to - 7, to], [1, 0], clamp);
  const pc = spring({ frame: f - comment, fps, config: IOS });
  const pb = spring({ frame: f - broke, fps, config: IOS });
  const v = interpolate(f, [broke, broke + 22], [2480, balance], ease);
  return (
    <div style={{ position: "absolute", top: 100, left: 70, right: 70, opacity: out }}>
      <div style={{ ...glass, borderRadius: 34, padding: "20px 26px", display: "flex", gap: 18, alignItems: "center", ...blurIn(pc, 1, -40) }}>
        <Logo name="instagram" color="#fff" bg="linear-gradient(45deg,#FEDA75,#FA7E1E,#D62976,#962FBF,#4F5BD5)" size={64} radius={18} />
        <div><div style={{ fontSize: 24, color: "rgba(255,255,255,.55)", fontWeight: 600 }}>hater_2026 · commented</div><div style={{ fontSize: 38, fontWeight: 700 }}>{text}</div></div>
      </div>
      {f >= broke - 1 && (
        <div style={{ marginTop: 22, height: 250, borderRadius: 36, background: "linear-gradient(135deg,#117ACA,#0b3f7a)", boxShadow: "0 24px 60px rgba(0,0,0,.5)", padding: 30, fontFamily: fontUI, color: "#fff", ...blurIn(pb) }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Logo name="chase" color="#117ACA" size={60} radius={14} /><span style={{ fontSize: 28, opacity: 0.8 }}>hater_2026 · Checking</span>
          </div>
          <div style={{ fontSize: 28, opacity: 0.75, marginTop: 20 }}>Available balance</div>
          <div style={{ fontSize: 90, fontWeight: 800, fontVariantNumeric: "tabular-nums", color: f >= broke + 22 ? "#FF6B6B" : "#fff" }}>${v.toFixed(2)}</div>
        </div>
      )}
    </div>
  );
};

/** height tag: a ruler draws up and the number lands (6'5") */
export const HeightTag: React.FC<{ at: number; until: number; text: string }> = ({ at, until, text }) => {
  const { f, fps, t, out, on } = useWin(at, until);
  if (!on) return null;
  const q = interpolate(t, [0, 18], [0, 1], ease);
  const pn = spring({ frame: t - 10, fps, config: POP });
  return (
    <div style={{ position: "absolute", top: 120, right: 70, height: 640, display: "flex", gap: 22, alignItems: "flex-start", opacity: out }}>
      <div style={{ ...glass, borderRadius: 34, padding: "22px 30px", marginTop: 20, transform: `scale(${pn})`, transformOrigin: "100% 0%" }}>
        <div style={{ fontSize: 26, color: "rgba(255,255,255,.6)", fontWeight: 700, letterSpacing: "0.1em" }}>HEIGHT</div>
        <div style={{ fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 130, color: Y, lineHeight: 1, textShadow: `0 0 40px ${Y}66` }}>{text}</div>
      </div>
      <div style={{ width: 60, height: 620 * q, borderRadius: 10, background: "rgba(255,255,255,.12)", border: "2px solid rgba(255,255,255,.4)", position: "relative", overflow: "hidden", marginTop: 620 * (1 - q) }}>
        {Array.from({ length: 26 }).map((_, i) => <div key={i} style={{ position: "absolute", left: 0, top: i * 24, width: i % 4 ? 22 : 40, height: 3, background: "#fff" }} />)}
      </div>
    </div>
  );
};

/** generic glass tiles that pop in one by one under a small heading */
export const Tiles: React.FC<{ from: number; to: number; title: string; tiles: { emoji: string; label: string; at: number }[]; top?: number }> = ({ from, to, title, tiles, top = 120 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from - 1 || f >= to) return null;
  const out = interpolate(f, [to - 7, to], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, opacity: out }}>
      <div style={{ textAlign: "center", fontFamily: fontUI, fontWeight: 700, fontSize: 34, color: "rgba(255,255,255,.6)", letterSpacing: "0.2em", marginBottom: 24 }}>{title}</div>
      <div style={{ display: "flex", justifyContent: "center", gap: 26 }}>
        {tiles.map((t) => {
          const p = spring({ frame: f - t.at, fps, config: POP });
          if (f < t.at - 1) return <div key={t.label} style={{ width: 290 }} />;
          return (
            <div key={t.label} style={{ width: 290, height: 300, borderRadius: 44, background: "#fff", boxShadow: "0 24px 50px rgba(0,0,0,.45)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              transform: `scale(${p}) rotate(${(1 - p) * -12}deg)`, fontFamily: fontUI, padding: 14, textAlign: "center" }}>
              <div style={{ fontSize: 120 }}>{t.emoji}</div>
              <div style={{ fontSize: 32, fontWeight: 800, color: "#111", marginTop: 6, lineHeight: 1.1 }}>{t.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Maps: a route draws from HOME to a NEW CITY pin */
export const NewCity: React.FC<{ at: number; city: number; until: number }> = ({ at, city, until }) => {
  const { f, fps, p, out, on } = useWin(at, until);
  if (!on) return null;
  const q = interpolate(f, [at + 4, city + 14], [0, 1], ease);
  const pc = spring({ frame: f - city, fps, config: POP });
  const path = "M150,330 C330,120 560,420 830,140";
  return (
    <div style={{ position: "absolute", top: 110, left: 60, right: 60, height: 480, borderRadius: 40, overflow: "hidden", boxShadow: "0 24px 60px rgba(0,0,0,.5)", border: "1px solid #ffffff22", ...blurIn(p, out, -40),
      background: "linear-gradient(160deg,#1f2a22,#18202a)" }}>
      <svg width="960" height="480" style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: 9 }).map((_, i) => <line key={`h${i}`} x1="0" y1={i * 60} x2="960" y2={i * 60 + 30} stroke="#ffffff10" strokeWidth="10" />)}
        {Array.from({ length: 9 }).map((_, i) => <line key={`v${i}`} x1={i * 120} y1="0" x2={i * 120 - 40} y2="480" stroke="#ffffff0c" strokeWidth="8" />)}
        <path d={path} stroke="#0A84FF" strokeWidth="14" fill="none" strokeLinecap="round" strokeDasharray="1100" strokeDashoffset={1100 * (1 - q)} />
        <circle cx="150" cy="330" r="22" fill="#fff" /><circle cx="150" cy="330" r="12" fill="#0A84FF" />
      </svg>
      <div style={{ position: "absolute", left: 100, top: 370, fontFamily: fontUI, fontSize: 30, fontWeight: 700, color: "rgba(255,255,255,.75)" }}>Same old routine</div>
      {f >= city - 1 && (
        <div style={{ position: "absolute", left: 830 - 60, top: 140 - 130, width: 120, textAlign: "center", transform: `scale(${pc})`, transformOrigin: "50% 100%" }}>
          <div style={{ fontSize: 100 }}>📍</div>
        </div>
      )}
      {f >= city - 1 && <div style={{ position: "absolute", right: 40, top: 190, fontFamily: fontUI, fontSize: 40, fontWeight: 800, color: G, transform: `scale(${pc})` }}>New city</div>}
    </div>
  );
};

/** "Posting…" upload bar → "Shared ✓" */
export const PostUpload: React.FC<{ at: number; until: number }> = ({ at, until }) => {
  const { f, fps, p, out, on } = useWin(at, until);
  if (!on) return null;
  const q = interpolate(f, [at + 4, at + 30], [0, 1], ease);
  const done = q >= 1;
  const pd = spring({ frame: f - (at + 30), fps, config: POP });
  return (
    <div style={{ position: "absolute", top: 120, left: 80, right: 80, ...glass, padding: "28px 34px", ...blurIn(p, out, -40) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <Logo name="instagram" color="#fff" bg="linear-gradient(45deg,#FEDA75,#FA7E1E,#D62976,#962FBF,#4F5BD5)" size={70} radius={20} />
        <span style={{ fontSize: 44, fontWeight: 700 }}>{done ? "Shared" : "Posting…"}</span>
        {done && <span style={{ marginLeft: "auto", width: 64, height: 64, borderRadius: 32, background: G, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, fontWeight: 900, transform: `scale(${pd})` }}>✓</span>}
      </div>
      <div style={{ height: 20, borderRadius: 10, background: "#ffffff22", marginTop: 22, overflow: "hidden" }}>
        <div style={{ width: `${q * 100}%`, height: "100%", borderRadius: 10, background: done ? G : "#fff" }} />
      </div>
    </div>
  );
};

/** "LET IT GO": the words drift up and dissolve */
export const LetGo: React.FC<{ at: number; until: number; text?: string; top?: number }> = ({ at, until, text = "LET IT GO", top = 260 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at - 1 || f >= until) return null;
  const p = spring({ frame: f - at, fps, config: IOS });
  const rise = interpolate(f, [Math.max(at + 26, until - 22), until], [0, 1], ease);
  return (
    <div style={{ position: "absolute", top: top - rise * 160, left: 0, right: 0, textAlign: "center", fontFamily: "Nunito Sans", fontWeight: 900, fontSize: 150, color: "#fff", letterSpacing: `${-0.02 + rise * 0.25}em`,
      opacity: Math.min(1, p * 1.3) * (1 - rise), filter: `blur(${(1 - p) * 14 + rise * 16}px)`, textShadow: `0 0 50px rgba(255,255,255,.4)` }}>{text}</div>
  );
};
