import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {TL} from './data';
import {FPS} from './theme';
import {Hud, SCENES} from './Scenes';
import {Ball, Captions} from './Reading';
import {Grain} from './lib';

/** reference grammar: hard cuts on the sentence, every scene slowly pushing; text lives in fixed zones */
export const Ep1: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const cur = TL.shots.find((s) => t >= s.start && t < s.end) ?? TL.shots[TL.shots.length - 1];
  const S = SCENES[cur.id];
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <S t={t} />
      <Hud t={t} />
      <Captions />
      <Ball />
      <Grain opacity={0.05} />
      <Audio src={staticFile('mix.wav')} />
    </AbsoluteFill>
  );
};
