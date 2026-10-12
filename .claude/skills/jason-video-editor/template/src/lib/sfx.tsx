import React from "react";
import { Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import lib from "./sfx-library.json";

/**
 * The SFX library (assets/sfx/library.json, built by scripts/build_sfx_library.py; new_episode.sh copies it here).
 * <Hit at={frame} id="pack6.impact_1" /> lands the sound ON `frame`: its PEAK for impacts/whooshes/reveals/builds,
 * its ONSET for iOS/UI/clicks/typing. Reference reels hit within ~3-45ms of the motion; starting the file on the frame
 * (ep #3/#4) made late-peaking sounds like CineStrike land ~16 frames late.
 */
export type SfxEntry = { id: string; file: string; job: string; vol: number; lead: number; dur: number; use: string; origin: string };
export const SFX: Record<string, SfxEntry> = Object.fromEntries((lib as { sounds: SfxEntry[] }).sounds.map((s) => [s.id, s]));

export const Hit: React.FC<{ at: number; id: string; v?: number }> = ({ at, id, v }) => {
  const { fps } = useVideoConfig();
  const s = SFX[id];
  if (!s) throw new Error(`unknown sfx id: ${id} (see references/sfx-library.md)`);
  const from = Math.round(at - s.lead * fps);
  const trim = Math.max(0, -from); // sound would start before frame 0: skip its head instead
  return (
    <Sequence from={Math.max(0, from)} durationInFrames={Math.ceil(s.dur * fps) + 2} layout="none">
      <Audio src={staticFile(s.file)} volume={v ?? s.vol} trimBefore={trim} />
    </Sequence>
  );
};
