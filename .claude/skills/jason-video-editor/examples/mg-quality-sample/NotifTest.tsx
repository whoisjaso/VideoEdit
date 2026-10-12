import React from "react";
import { AbsoluteFill, Composition, registerRoot, continueRender, delayRender } from "remotion";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import { Wallpaper } from "../lib/Glass";
import { Notification, NotificationStack } from "../lib/IosNotify";

const T: React.FC = () => (
  <AbsoluteFill>
    <Wallpaper />
    <Notification app="instagram" title="Instagram" body="hater_2026 commented: bro thinks he's him 😂" at={0} until={999} y={60} />
    <Notification app="messages" title="Her" body="your dick small 😂" at={0} until={999} y={330} avatar={{ initials: "H", hue: 330 }} />
    <NotificationStack until={999} y={600} items={[
      { app: "chase", title: "Chase", body: "Your available balance is $4.12", at: 0 },
      { app: "cashapp", title: "Cash App", body: "You received $500.00", at: 0 },
      { app: "applepay", title: "Wallet", body: "Apple Pay · Payment received", at: 0 },
    ]} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 960, bottom: 0, background: "#E9EAF0" }}>
      <Notification app="tiktok" title="TikTok" body="Your video is getting more views than usual" at={0} until={999} y={40} light />
      <Notification app="reminders" title="Reminders" body="Become successful" at={0} until={999} y={300} light />
      <Notification app="calendar" title="Calendar" subtitle="Change your script" body="Today · all day" at={0} until={999} y={560} light time="9:41 AM" />
    </div>
  </AbsoluteFill>
);
const h = typeof document !== "undefined" ? delayRender("fonts") : null;
if (h !== null) Promise.all(["400 40px Inter", "600 40px Inter"].map((x) => document.fonts.load(x))).then(() => continueRender(h));
registerRoot(() => <Composition id="NotifTest" component={T} durationInFrames={30} fps={30} width={1080} height={1920} />);
