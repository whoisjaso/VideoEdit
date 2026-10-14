import React from 'react';
import {C, SIDE} from './theme';
import {clamp} from './lib';

export const COL: Record<string, string> = {red: C.red, blue: C.blue, amber: C.amber, ink: C.ink, white: '#fff', both: C.ink, pink: C.pink, him: SIDE.him, you: SIDE.you, stakes: SIDE.stakes, fix: SIDE.fix};

/** Icon the reading ball morphs into. Drawn in a 200x200 box centred on 0,0.
 *  d = draw-on progress 0..1 (stroke reveal), u = seconds since the morph landed (idle motion). */
export const Shape: React.FC<{shape: string; color: string; d: number; u: number; night?: boolean}> = ({shape, color, d, u, night}) => {
  const ink = night ? '#fff' : C.ink;
  const sw = 13;
  const stroke = {fill: 'none', stroke: ink, strokeWidth: sw, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const,
    pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - d};
  const fillA = clamp((d - 0.55) * 2.5);
  switch (shape) {
    case 'eye': {
      const look = Math.sin(u * 2.2) * 22;
      const bl = (u % 2.4) < 0.18 ? Math.sin(((u % 2.4) / 0.18) * Math.PI) : 0;
      return (
        <g transform={`scale(1 ${1 - bl * 0.9})`}>
          <path d="M -95 0 Q 0 -78 95 0 Q 0 78 -95 0 Z" {...stroke} />
          <circle cx={look} cy={0} r={38} fill={color} opacity={fillA} />
          <circle cx={look} cy={0} r={15} fill={ink} opacity={fillA} />
          <circle cx={look - 12} cy={-12} r={7} fill="#fff" opacity={fillA} />
        </g>
      );
    }
    case 'badge': {
      const pts = Array.from({length: 12}, (_, i) => {
        const r = i % 2 === 0 ? 92 : 58;
        const a = (i / 12) * Math.PI * 2 - Math.PI / 2;
        return `${(Math.cos(a) * r).toFixed(1)} ${(Math.sin(a) * r).toFixed(1)}`;
      });
      return (
        <g transform={`rotate(${Math.sin(u * 1.5) * 4})`}>
          <path d={`M ${pts.join(' L ')} Z`} fill={color} fillOpacity={fillA} {...stroke} />
          <circle cx={0} cy={0} r={30} fill="#fff" opacity={fillA} stroke={ink} strokeWidth={9} />
        </g>
      );
    }
    case 'scales': {
      const tilt = Math.sin(u * 1.8) * 14;
      return (
        <g>
          <path d="M 0 -80 L 0 80 M -50 80 L 50 80" {...stroke} />
          <g transform={`rotate(${tilt} 0 -60)`}>
            <path d="M -90 -60 L 90 -60" {...stroke} />
            {[-90, 90].map((x) => (
              <g key={x} transform={`rotate(${-tilt} ${x} -60)`}>
                <path d={`M ${x} -60 L ${x - 34} 0 M ${x} -60 L ${x + 34} 0 M ${x - 40} 0 Q ${x} 40 ${x + 40} 0 Z`} {...stroke}
                  fill={x < 0 ? color : 'none'} fillOpacity={x < 0 ? fillA : 0} />
              </g>
            ))}
          </g>
        </g>
      );
    }
    case 'stopwatch': {
      const sweep = 36 * clamp((u - 0.35) / 0.1);   // a tenth of a second = 36 degrees
      const a = (sweep * Math.PI) / 180;
      return (
        <g>
          <circle cx={0} cy={10} r={82} {...stroke} />
          <path d="M -18 -88 L 18 -88 M 0 -88 L 0 -72 M 62 -52 L 74 -64" {...stroke} />
          <path d={`M 0 10 L 0 -60 A 70 70 0 0 1 ${70 * Math.sin(a)} ${10 - 70 * Math.cos(a)} Z`} fill={C.blue} opacity={0.85 * fillA} />
          <path d={`M 0 10 L ${66 * Math.sin(a)} ${10 - 66 * Math.cos(a)}`} {...stroke} strokeDashoffset={0} opacity={fillA} />
          <circle cx={0} cy={10} r={10} fill={ink} opacity={fillA} />
        </g>
      );
    }
    case 'question':
      return (
        <g transform={`translate(0 ${Math.sin(u * 2) * 6}) rotate(${Math.sin(u * 1.3) * 3})`}>
          <path d="M -48 -42 Q -48 -96 0 -96 Q 52 -96 52 -48 Q 52 -14 8 4 Q 0 8 0 34" {...stroke} stroke={color} strokeWidth={26} />
          <circle cx={0} cy={78} r={17} fill={color} opacity={fillA} />
        </g>
      );
    case 'hazard': {
      const blink = Math.sin(u * Math.PI * 3) > 0 ? 1 : 0.25;
      return (
        <g>
          <path d="M 0 -84 L 90 72 L -90 72 Z" {...stroke} fill={color} fillOpacity={fillA * blink} />
          <path d="M 0 -30 L 44 46 L -44 46 Z" {...stroke} />
        </g>
      );
    }
    case 'bulb':
      return (
        <g>
          <path d="M -36 40 Q -70 0 -50 -40 Q -30 -80 0 -80 Q 30 -80 50 -40 Q 70 0 36 40 L 36 64 L -36 64 Z" {...stroke} fill={color} fillOpacity={fillA} />
          <path d="M -24 84 L 24 84" {...stroke} />
        </g>
      );
    case 'window': {
      const down = clamp(u / 0.8);
      return (
        <g>
          <path d="M -80 80 L -80 -20 Q -66 -76 -10 -84 L 84 -84 L 84 80 Z" {...stroke} />
          <rect x={-66} y={-70 + 120 * down} width={136} height={Math.max(0, 136 - 120 * down)} fill={color} opacity={0.45 * fillA} />
          <path d="M 4 -30 L 4 40 M -22 16 L 4 42 L 30 16" {...stroke} strokeDashoffset={0} opacity={fillA} />
        </g>
      );
    }
    case 'wheel':
      return (
        <g>
          <circle cx={0} cy={6} r={78} {...stroke} />
          <circle cx={0} cy={6} r={16} fill={ink} opacity={fillA} />
          <path d="M 0 6 L 0 84 M 0 6 L -72 30 M 0 6 L 72 30" {...stroke} />
          <ellipse cx={-56} cy={-50} rx={26} ry={32} fill={color} opacity={fillA} transform="rotate(-40 -56 -50)" />
          <ellipse cx={56} cy={-50} rx={26} ry={32} fill={color} opacity={fillA} transform="rotate(40 56 -50)" />
        </g>
      );
    case 'stamp': {
      const slam = 1 + 0.6 * Math.max(0, 1 - u / 0.12);
      return (
        <g transform={`scale(${slam}) rotate(-9)`}>
          <rect x={-112} y={-46} width={224} height={92} rx={14} fill="none" stroke={C.red} strokeWidth={11} opacity={clamp(d * 2)} />
          <text x={0} y={22} textAnchor="middle" fontFamily="Inter" fontWeight={900} fontSize={62} fill={C.red} opacity={clamp(d * 2)} letterSpacing={4}>EXPIRED</text>
        </g>
      );
    }
    case 'timer': {
      const left = clamp(1 - u / 1.7);
      const a = left * Math.PI * 2;
      return (
        <g>
          <circle cx={0} cy={0} r={84} fill="none" stroke={night ? 'rgba(255,255,255,0.15)' : C.line} strokeWidth={16} />
          <path d={`M 0 -84 A 84 84 0 ${a > Math.PI ? 1 : 0} 1 ${84 * Math.sin(a)} ${-84 * Math.cos(a)}`} fill="none" stroke={C.red} strokeWidth={16} strokeLinecap="round" opacity={clamp(d * 2)} />
          <text x={0} y={40} textAnchor="middle" fontFamily="Inter" fontWeight={900} fontSize={120} fill={C.red} opacity={fillA}>5</text>
        </g>
      );
    }
    case 'shield': {
      const lower = u < 1.55 ? clamp(u / 0.6) : 1 - clamp((u - 1.55) / 0.4);
      return (
        <g transform={`translate(0 ${lower * 60}) rotate(${lower * 12})`} opacity={1 - lower * 0.35}>
          <path d="M 0 -88 L 76 -60 Q 76 40 0 90 Q -76 40 -76 -60 Z" {...stroke} fill={color} fillOpacity={fillA * 0.25} />
          <path d="M 0 -50 L 0 50" {...stroke} />
        </g>
      );
    }
    default:
      return <circle r={30} fill={color} />;
  }
};
