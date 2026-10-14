import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'path';
const pairs = process.argv.slice(2).map((a) => a.split(':'));
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const composition = await selectComposition({serveUrl, id: 'Ep1', browserExecutable});
for (const [name, f] of pairs) {
  await renderStill({serveUrl, composition, frame: +f, output: `out/stills/${name}.png`, browserExecutable, scale: 0.5});
  console.log(name, f);
}
