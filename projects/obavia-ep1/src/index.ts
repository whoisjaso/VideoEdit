import {registerRoot, staticFile} from 'remotion';
import {Root} from './Root';

// fonts via @font-face; Remotion waits for document.fonts.ready before every frame.
// Text layout never touches the DOM (lib.measure uses the font's advance widths), so no delayRender is needed.
const css = `
@font-face {font-family: 'Inter'; src: url('${staticFile('fonts/Inter500.woff2')}') format('woff2'); font-weight: 500; font-display: block;}
@font-face {font-family: 'Inter'; src: url('${staticFile('fonts/Inter800.woff2')}') format('woff2'); font-weight: 800; font-display: block;}
@font-face {font-family: 'Inter'; src: url('${staticFile('fonts/Inter900.woff2')}') format('woff2'); font-weight: 900; font-display: block;}
@font-face {font-family: 'Instrument Serif'; src: url('${staticFile('fonts/SerifItalic.woff2')}') format('woff2'); font-weight: 400; font-style: italic; font-display: block;}
@font-face {font-family: 'Anton'; src: url('${staticFile('fonts/Anton.woff2')}') format('woff2'); font-weight: 400; font-display: block;}
@font-face {font-family: 'JetBrains Mono'; src: url('${staticFile('fonts/JBMono.woff2')}') format('woff2'); font-weight: 500; font-display: block;}
@font-face {font-family: 'JetBrains Mono'; src: url('${staticFile('fonts/JBMono700.woff2')}') format('woff2'); font-weight: 700; font-display: block;}`;
if (typeof document !== 'undefined' && !document.getElementById('ep1-fonts')) {
  const el = document.createElement('style');
  el.id = 'ep1-fonts';
  el.textContent = css;
  document.head.appendChild(el);
}

registerRoot(Root);
