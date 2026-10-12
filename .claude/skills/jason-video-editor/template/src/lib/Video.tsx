import React from "react";
import { AbsoluteFill, Freeze, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { clamp } from "../fx";
import { theme } from "../theme";
import { CUT, EDL } from "../ep/timeline";

/**
 * The footage layer of the 8.3 build. Muted: the voice plays once, from <Audio src="ep/cut.mp4"> in the Sound map.
 *  - slow keyframed push across every clip (reel 7)
 *  - section change = zoom transition (1.14 -> 1, blur 10 -> 0, 6f); same-thought jump cut = alternate framing, no effect (ep #2 rule)
 *  - punches: zoom punch on the lines that must land
 *  - freeze: [from, to] holds one frame, desaturated (ep #3 "still" beat)
 *  - behind + fgRanges: hero word between footage and the person cutout (fg.webm) = text behind him
 *  - moody grade (§18): saturate .78, contrast 1.06, brightness .9
 */
export const TRANSITION = 6;
export const Video: React.FC<{ punches: number[]; behind?: React.ReactNode; fgRanges?: [number, number][]; freeze?: [number, number]; look?: string }> = ({ punches, behind, fgRanges = [], freeze, look }) => {
  const frame = useCurrentFrame();
  const idx = Math.max(0, EDL.findIndex((p) => frame >= p.f0 && frame < p.f1));
  const piece = EDL[idx];
  let z = 1.02;
  let blur = 0;
  if (piece) {
    z += interpolate(frame, [piece.f0, piece.f1], [0, 0.035], { ...clamp, easing: theme.ease.inOut });
    const t = frame - piece.f0;
    const section = idx > 0 && EDL[idx - 1].tag !== piece.tag;
    if (!section && piece.speed === 1) z += (idx % 2) * 0.045;
    if (section && t < TRANSITION) {
      z += interpolate(t, [0, TRANSITION], [0.14, 0], { ...clamp, easing: theme.ease.out });
      blur = interpolate(t, [0, TRANSITION], [10, 0], { ...clamp, easing: theme.ease.out });
    }
    if (piece.speed < 1) z += interpolate(frame, [piece.f0, piece.f1], [0.08, 0.3], { ...clamp, easing: theme.ease.inOut });
  }
  for (const p of punches) {
    const t = frame - p;
    if (t >= 0 && t < 45) z += interpolate(t, [0, 5, 45], [0, 0.14, 0.1], { ...clamp, easing: theme.ease.out });
  }
  const outro = frame >= CUT;
  const frozen = !!freeze && frame >= freeze[0] && frame < freeze[1];
  const ob = interpolate(frame, [CUT, CUT + 14], [0, 22], { ...clamp, easing: theme.ease.out });
  const grade = frozen ? "saturate(0) contrast(1.1) brightness(0.8)" : look ?? "saturate(0.78) contrast(1.06) brightness(0.9)";
  const style: React.CSSProperties = {
    width: "100%", height: "100%", objectFit: "cover", transformOrigin: "50% 32%",
    transform: `scale(${outro ? 1.2 : z})`,
    filter: outro ? `blur(${ob}px) brightness(0.45)` : `${grade}${blur ? ` blur(${blur}px)` : ""}`,
  };
  const hold = outro ? CUT - 1 : frozen ? freeze![0] : null;
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      {hold !== null ? (
        <Freeze frame={hold}><OffthreadVideo src={staticFile("ep/cut.mp4")} muted style={style} /></Freeze>
      ) : (
        <OffthreadVideo src={staticFile("ep/cut.mp4")} muted style={style} />
      )}
      {behind}
      {!outro && fgRanges.map(([a, b]) => (
        <Sequence key={a} from={a} durationInFrames={b - a} layout="none">
          <AbsoluteFill><OffthreadVideo src={staticFile("ep/fg.webm")} transparent muted trimBefore={a} style={style} /></AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
