import React from 'react';
import {Composition} from 'remotion';
import {Ep1} from './Ep1';
import {TL} from './data';
import {FPS, W, H} from './theme';

export const Root: React.FC = () => (
  <Composition id="Ep1" component={Ep1} durationInFrames={TL.frames} fps={FPS} width={W} height={H} />
);
