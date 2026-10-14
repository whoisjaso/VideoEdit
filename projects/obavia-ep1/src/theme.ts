import {Easing} from 'remotion';

export const W = 1080;
export const H = 1920;
export const FPS = 30;

// Colour = who. Blue is HIM (authority, order, cold vigilance: the light bar). Amber is YOU (warm, human, the heartbeat).
// Red is the stakes (danger, the clock). Mint is the way out (calm, safe, go). Nothing is coloured that doesn't mean one of these.
export const SIDE = {
  him: '#3D8BFF', himDeep: '#06122B', himMid: '#0C2552', himGlow: 'rgba(61,139,255,0.55)',
  you: '#FFA62B', youDeep: '#1C0E04', youMid: '#3A1C06', youGlow: 'rgba(255,166,43,0.55)',
  stakes: '#FF3B4E', stakesGlow: 'rgba(255,59,78,0.55)',
  fix: '#2EE6A6', fixGlow: 'rgba(46,230,166,0.5)',
};
export const C = {
  cream: '#EEEAE0',
  ink: '#121212',
  ink2: '#4A4741',
  grey: '#8D8A84',
  rule: '#D8D3C7',
  pink: '#E8458B',
  pinkSoft: 'rgba(232,69,139,0.14)',
  dark: '#1B1613',
  hud: 'rgba(16,16,18,0.78)',
  white: '#FFFFFF',
  unspoken: 'rgba(255,255,255,0.42)',
  amber: '#FFB21E',
  // kept for the shared Shapes kit
  red: '#FF3B4E', blue: '#3D8BFF', line: '#D8D3C7', stage: '#EEEAE0',
};

export const FONT = {
  sans: 'Inter, sans-serif',
  mono: '"JetBrains Mono", monospace',
};

export const EASE = {
  out: Easing.bezier(0.16, 1, 0.3, 1),
  in: Easing.bezier(0.7, 0, 0.84, 0),
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  back: Easing.bezier(0.34, 1.56, 0.64, 1),
  sine: Easing.inOut(Easing.sin),
};

export const SPRING = {
  pop: {damping: 14, stiffness: 190, mass: 0.7},
  ios: {damping: 30, stiffness: 210, mass: 1},
  slam: {damping: 18, stiffness: 280, mass: 0.8},
  smooth: {damping: 200, stiffness: 100, mass: 1},
};

export const ZONE = {hud: [64, 200], captions: [1330, 1450], margin: 60};
