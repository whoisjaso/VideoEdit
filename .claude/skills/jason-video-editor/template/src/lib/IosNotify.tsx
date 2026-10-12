import React from "react";
import "@fontsource-variable/inter/opsz.css";
import { interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * iPhone notifications, built to iOS 17/18 metrics (Jason 2026-10-08: "iPhone notifications exactly how it looks, real assets").
 * Scale: 1080px frame = 393pt iPhone width → 1pt = 2.748px. Banner = full width − 16pt margins, radius 23pt, padding 14pt,
 * icon 38pt superellipse, title 15pt semibold, body 15pt regular, time 13pt secondary, line 20pt.
 * Font: Apple's SF Pro license (developer.apple.com/fonts) allows UI mock-ups by a registered Apple Developer only and forbids "artwork… or any
 * other work product" and transfer, so it can't be rendered here. Stand-in: Inter 4 VARIABLE with the optical-size axis (like SF's Text/Display
 * split): small text gets the Text design, big text the Display design automatically (font-optical-sizing: auto). Import "@fontsource-variable/inter/opsz.css".
 * Brand icons: real simple-icons glyphs on official brand colors (assets/logos). Apple system app icons are drawn originals in Apple's colors.
 * Sounds: pair with the real iOS sounds in the SFX library (ios.ios_tritone for a banner, ios.ios_received in-thread).
 */
const PT = 1080 / 393;
const px = (pt: number) => Math.round(pt * PT);
export const NOTIF_FONT = "'Inter Variable', Inter";

/** iOS superellipse (continuous corners) as a CSS clip-path polygon */
const SQUIRCLE = (() => {
  const n = 5, pts: string[] = [];
  for (let i = 0; i < 72; i++) {
    const t = (i / 72) * Math.PI * 2, c = Math.cos(t), s = Math.sin(t);
    const x = Math.sign(c) * Math.pow(Math.abs(c), 2 / n), y = Math.sign(s) * Math.pow(Math.abs(s), 2 / n);
    pts.push(`${(50 + x * 50).toFixed(2)}% ${(50 + y * 50).toFixed(2)}%`);
  }
  return `polygon(${pts.join(",")})`;
})();

type IconSpec = { bg: string; glyph?: string; fg?: string; draw?: (s: number) => React.ReactNode };
const glyph = (name: string, fg: string, s: number, k = 0.6) => (
  <div style={{ width: s * k, height: s * k, background: fg, WebkitMaskImage: `url(${staticFile(`logos/${name}.svg`)})`, WebkitMaskSize: "contain", WebkitMaskRepeat: "no-repeat", WebkitMaskPosition: "center" }} />
);
/** app id → icon. Brand apps use real logos on brand colors; Apple apps are drawn in Apple's colors. */
export const APPS: Record<string, IconSpec & { name: string }> = {
  messages: { name: "Messages", bg: "linear-gradient(180deg,#5DF777 0%,#0ABD28 100%)", glyph: "imessage", fg: "#fff" },
  phone: { name: "Phone", bg: "linear-gradient(180deg,#5DF777 0%,#0ABD28 100%)", draw: (s) => <svg width={s * 0.56} height={s * 0.56} viewBox="0 0 24 24"><path fill="#fff" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" /></svg> },
  mail: { name: "Mail", bg: "linear-gradient(180deg,#1FB6FF 0%,#0A63F6 100%)", draw: (s) => <svg width={s * 0.62} height={s * 0.62} viewBox="0 0 24 24"><rect x="2.5" y="5" width="19" height="14" rx="2.2" fill="#fff" /><path d="M3.5 6.5l8.5 6.4 8.5-6.4" stroke="#1C8DFB" strokeWidth="1.6" fill="none" strokeLinejoin="round" /></svg> },
  calendar: { name: "Calendar", bg: "#fff", draw: (s) => <div style={{ textAlign: "center", fontFamily: NOTIF_FONT, lineHeight: 1 }}><div style={{ color: "#FF3B30", fontSize: s * 0.16, fontWeight: 600 }}>TUE</div><div style={{ color: "#111", fontSize: s * 0.5, fontWeight: 400, marginTop: s * 0.02 }}>8</div></div> },
  reminders: { name: "Reminders", bg: "#fff", draw: (s) => <svg width={s * 0.7} height={s * 0.7} viewBox="0 0 24 24">{[["#0A84FF", 6], ["#FF3B30", 12], ["#FF9F0A", 18]].map(([c, y]) => <g key={String(y)}><circle cx="5" cy={y as number} r="2.2" fill={c as string} /><rect x="9" y={(y as number) - 0.6} width="12" height="1.2" rx="0.6" fill="#D1D1D6" /></g>)}</svg> },
  wallet: { name: "Wallet", bg: "#0B0B0D", draw: (s) => <svg width={s * 0.66} height={s * 0.66} viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="15" rx="3" fill="#2B2B30" />{["#2FB85A", "#F5B400", "#FF6A3D", "#1E88E5"].map((c, i) => <rect key={c} x="3" y={6 + i * 2.2} width="18" height="2.2" fill={c} />)}<rect x="3" y="13" width="18" height="6" rx="2" fill="#E9E9EE" /></svg> },
  notes: { name: "Notes", bg: "linear-gradient(180deg,#FFD53D 0 28%,#FFFFFF 28% 100%)", draw: (s) => <svg width={s} height={s} viewBox="0 0 24 24">{[12, 15.5, 19].map((y) => <rect key={y} x="3" y={y} width="18" height="0.7" fill="#D9D9DE" />)}</svg> },
  photos: { name: "Photos", bg: "#fff", draw: (s) => <svg width={s * 0.74} height={s * 0.74} viewBox="-12 -12 24 24">{["#FFB300", "#FF6D00", "#FF3D7F", "#B34BFF", "#2F7BFF", "#00C2FF", "#2FD158", "#C7E000"].map((c, i) => <ellipse key={c} cx="0" cy="-5.2" rx="3.4" ry="5.4" fill={c} opacity="0.85" transform={`rotate(${i * 45})`} />)}</svg> },
  instagram: { name: "Instagram", bg: "radial-gradient(circle at 30% 107%, #FDF497 0%, #FDF497 5%, #FD5949 45%, #D6249F 60%, #285AEB 90%)", glyph: "instagram", fg: "#fff" },
  tiktok: { name: "TikTok", bg: "#010101", glyph: "tiktok", fg: "#fff" },
  whatsapp: { name: "WhatsApp", bg: "linear-gradient(180deg,#5FFC7B 0%,#28D146 100%)", glyph: "whatsapp", fg: "#fff" },
  gmail: { name: "Gmail", bg: "#fff", glyph: "gmail", fg: "#EA4335" },
  snapchat: { name: "Snapchat", bg: "#FFFC00", glyph: "snapchat", fg: "#fff" },
  youtube: { name: "YouTube", bg: "#fff", glyph: "youtube", fg: "#FF0000" },
  x: { name: "X", bg: "#000", glyph: "x", fg: "#fff" },
  cashapp: { name: "Cash App", bg: "#00D64F", glyph: "cashapp", fg: "#fff" },
  venmo: { name: "Venmo", bg: "#008CFF", glyph: "venmo", fg: "#fff" },
  paypal: { name: "PayPal", bg: "#fff", glyph: "paypal", fg: "#003087" },
  zelle: { name: "Zelle", bg: "#6D1ED4", glyph: "zelle", fg: "#fff" },
  chase: { name: "Chase", bg: "#117ACA", glyph: "chase", fg: "#fff" },
  applepay: { name: "Wallet", bg: "#000", glyph: "applepay", fg: "#fff" },
  facebook: { name: "Facebook", bg: "#0866FF", glyph: "facebook", fg: "#fff" },
  messenger: { name: "Messenger", bg: "linear-gradient(45deg,#0099FF,#A033FF 60%,#FF5280)", glyph: "messenger", fg: "#fff" },
  telegram: { name: "Telegram", bg: "linear-gradient(180deg,#2AABEE,#229ED9)", glyph: "telegram", fg: "#fff" },
  spotify: { name: "Spotify", bg: "#000", glyph: "spotify", fg: "#1DB954" },
  uber: { name: "Uber", bg: "#000", glyph: "uber", fg: "#fff" },
  netflix: { name: "Netflix", bg: "#000", glyph: "netflix", fg: "#E50914" },
  maps: { name: "Google Maps", bg: "#fff", glyph: "googlemaps", fg: "#34A853" },
  discord: { name: "Discord", bg: "#5865F2", glyph: "discord", fg: "#fff" },
  threads: { name: "Threads", bg: "#000", glyph: "threads", fg: "#fff" },
  chess: { name: "Chess.com", bg: "#81B64C", glyph: "chessdotcom", fg: "#fff" },
};

export const AppIcon: React.FC<{ app: string; size: number }> = ({ app, size }) => {
  const a = APPS[app];
  if (!a) throw new Error(`unknown app icon: ${app}`);
  return (
    <div style={{ width: size, height: size, clipPath: SQUIRCLE, background: a.bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, overflow: "hidden",
      boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.06)" }}>
      {a.draw ? a.draw(size) : glyph(a.glyph!, a.fg!, size, app === "messages" ? 0.64 : 0.58)}
    </div>
  );
};

/** contact avatar (iOS communication notification): gradient circle + initials, small app icon badge bottom-right */
const Avatar: React.FC<{ initials: string; hue: number; app: string; size: number }> = ({ initials, hue, app, size }) => (
  <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
    <div style={{ width: size, height: size, borderRadius: "50%", background: `linear-gradient(180deg, hsl(${hue},14%,70%), hsl(${hue},12%,52%))`, display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: NOTIF_FONT, fontWeight: 600, fontSize: size * 0.4, color: "#fff", letterSpacing: "-0.01em" }}>{initials}</div>
    <div style={{ position: "absolute", right: -size * 0.06, bottom: -size * 0.06, padding: size * 0.03, borderRadius: size * 0.14, background: "rgba(40,40,44,0.9)" }}><AppIcon app={app} size={size * 0.4} /></div>
  </div>
);

export type NotifProps = { app: string; title: string; body: string; at: number; until: number; time?: string; avatar?: { initials: string; hue?: number }; light?: boolean; y?: number; subtitle?: string };

/** one iPhone banner: drops from the top on the iOS spring, holds, slides back up */
export const Notification: React.FC<NotifProps> = ({ app, title, body, at, until, time = "now", avatar, light, y = px(12), subtitle }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at - 1 || f >= until) return null;
  const i = spring({ frame: f - at, fps, config: { damping: 24, stiffness: 240, mass: 0.9 } }); // iOS drop: tiny settle
  const o = spring({ frame: f - (until - 12), fps, config: { damping: 30, stiffness: 260 } });
  const W = 1080 - px(8) * 2, R = px(23), pad = px(14), icon = px(38);
  const fg = light ? "#000" : "#fff", sec = light ? "rgba(60,60,67,0.6)" : "rgba(235,235,245,0.6)";
  const mat: React.CSSProperties = light
    ? { background: "rgba(246,246,248,0.78)", backdropFilter: "blur(30px) saturate(1.8)", WebkitBackdropFilter: "blur(30px) saturate(1.8)" }
    : { background: "rgba(36,36,40,0.62)", backdropFilter: "blur(30px) saturate(1.8)", WebkitBackdropFilter: "blur(30px) saturate(1.8)" };
  return (
    <div style={{ position: "absolute", left: px(8), top: y, width: W, borderRadius: R, ...mat, padding: `${px(12)}px ${pad}px`, display: "flex", gap: px(10), alignItems: "center",
      boxShadow: "0 12px 40px rgba(0,0,0,0.28)", transform: `translateY(${(1 - i) * -px(110) - o * px(120)}px) scale(${0.96 + 0.04 * i})`, opacity: Math.min(1, i * 1.6) * (1 - o) }}>
      {avatar ? <Avatar initials={avatar.initials} hue={avatar.hue ?? 220} app={app} size={icon} /> : <AppIcon app={app} size={icon} />}
      <div style={{ flex: 1, minWidth: 0, fontFamily: NOTIF_FONT, fontOpticalSizing: "auto", letterSpacing: "-0.012em" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: px(8) }}>
          <span style={{ fontSize: px(15), fontWeight: 600, color: fg, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{title}</span>
          <span style={{ fontSize: px(13), color: sec, flexShrink: 0 }}>{time}</span>
        </div>
        {subtitle && <div style={{ fontSize: px(15), fontWeight: 600, color: fg, lineHeight: `${px(20)}px` }}>{subtitle}</div>}
        <div style={{ fontSize: px(15), fontWeight: 400, color: fg, lineHeight: `${px(20)}px`, display: "-webkit-box", WebkitLineClamp: 4, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{body}</div>
      </div>
    </div>
  );
};

/** lock-screen grouped stack (iOS): the newest card is in front; older cards are blank material plates that peek ~8pt below it,
 *  each narrower (inset 8pt more per level) and dimmer. Content never shows through. Each card arrives on its frame (pushes the rest back). */
export const NotificationStack: React.FC<{ items: Omit<NotifProps, "until" | "y">[]; until: number; y?: number; light?: boolean }> = ({ items, until, y = px(60), light }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shown = items.filter((it) => f >= it.at - 1);
  if (!shown.length || f >= until) return null;
  const front = shown[shown.length - 1];
  const behind = Math.min(2, shown.length - 1);
  const grow = spring({ frame: f - front.at, fps, config: { damping: 28, stiffness: 220 } });
  const plate = light ? "rgba(236,236,240,0.82)" : "rgba(52,52,58,0.62)";
  const H = px(64); // single-line banner height: 12 + 20 + 20 + 12 pt
  return (
    <>
      {Array.from({ length: behind }).map((_, k) => {
        const lvl = k + 1, d = lvl - 1 + grow; // animate plates sliding back as a new card arrives
        const inset = px(8) * (1 + d);
        return <div key={lvl} style={{ position: "absolute", left: px(8) + inset, right: px(8) + inset, top: y + H - px(14) + px(8) * d, height: px(22), borderRadius: `0 0 ${px(18)}px ${px(18)}px`,
          background: plate, backdropFilter: "blur(30px) saturate(1.8)", WebkitBackdropFilter: "blur(30px) saturate(1.8)", opacity: 0.9 - 0.25 * d, boxShadow: "0 8px 20px rgba(0,0,0,0.18)", zIndex: 10 - lvl }} />;
      })}
      <div style={{ position: "absolute", inset: 0, zIndex: 20 }}><Notification {...front} until={until} y={y} light={light} /></div>
    </>
  );
};
