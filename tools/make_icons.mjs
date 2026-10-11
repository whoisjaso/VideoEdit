// Renders the Kairos icon set from one SVG master. Dev tool, not a runtime dependency.
//   node tools/make_icons.mjs            (needs playwright, which the repo's UI tests already use)
// Writes web/icons/: mark.svg, mark-light.svg, wordmark.svg, icon-{16..1024}.png,
// icon-maskable-512.png, apple-touch-icon.png, favicon.ico (via Python/Pillow if present).
import { mkdirSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import { createRequire } from "node:module";

// Local install first; fall back to a global one (e.g. /opt/node22/lib/node_modules on the CI image).
const req = createRequire(import.meta.url);
const pwPath = ["playwright", `${execSync("npm root -g").toString().trim()}/playwright`].find((p) => { try { req.resolve(p); return true; } catch { return false; } });
if (!pwPath) throw new Error("playwright not found: npm i -D playwright, or npm i -g playwright");
const pw = await import(req.resolve(pwPath));
const chromium = pw.chromium ?? pw.default.chromium;

const OUT = new URL("../web/icons/", import.meta.url).pathname;
mkdirSync(OUT, { recursive: true });

// The moment mark: a ring (the hour of footage) with one slice lifted out (the clip you keep).
// Ring r=150 on a 512 canvas; the slice spans -20°..40° and is pushed 30px outward along 10°.
const ring = (stroke) => `<circle cx="256" cy="256" r="150" fill="none" stroke="${stroke}" stroke-width="44" stroke-dasharray="785.4 157.1" stroke-dashoffset="-104.72"/>`;
const slice = `<path d="M396.95 204.70A150 150 0 0 1 370.91 352.42" fill="none" stroke="#ffc21a" stroke-width="44" transform="translate(29.54 5.21)"/>`;
const app = (bg, fg, pad = 0) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="116" fill="${bg}"/>
  <g transform="translate(256 256) scale(${1 - pad}) translate(-256 -256)">${ring(fg)}${slice}</g>
</svg>`;
const mark = (fg) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">${ring(fg)}${slice}</svg>`;
const wordmark = (fg) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 320">
  <g transform="translate(40 40) scale(.47)">${ring(fg)}${slice}</g>
  <text x="330" y="222" font-family="Outfit, 'SF Pro Display', system-ui, sans-serif" font-weight="800" font-size="196" letter-spacing="-6" fill="${fg}">Kairos</text>
</svg>`;

writeFileSync(OUT + "mark.svg", mark("#14131a"));
writeFileSync(OUT + "mark-light.svg", mark("#f4f2ec"));
writeFileSync(OUT + "wordmark.svg", wordmark("#14131a"));
writeFileSync(OUT + "wordmark-light.svg", wordmark("#f4f2ec"));
writeFileSync(OUT + "app.svg", app("#14131a", "#f4f2ec"));

const b = await chromium.launch();
const page = await b.newPage();
const png = async (svg, size, file) => {
  await page.setViewportSize({ width: size, height: size });
  await page.setContent(`<html><body style="margin:0;background:transparent">${svg.replace("<svg ", `<svg width="${size}" height="${size}" `)}</body></html>`);
  await page.screenshot({ path: OUT + file, omitBackground: true });
};
for (const s of [16, 32, 48, 64, 128, 192, 256, 512, 1024]) await png(app("#14131a", "#f4f2ec"), s, `icon-${s}.png`);
await png(app("#14131a", "#f4f2ec", 0.2), 512, "icon-maskable-512.png");   // Android safe zone: keep the mark inside 80%
await png(app("#14131a", "#f4f2ec"), 180, "apple-touch-icon.png");
await png(mark("#14131a"), 512, "mark-512.png");
await png(mark("#f4f2ec"), 512, "mark-light-512.png");
await b.close();

try {   // favicon.ico from the small PNGs
  execSync(`python3 -c "from PIL import Image; Image.open('${OUT}icon-64.png').save('${OUT}favicon.ico', sizes=[(16,16),(32,32),(48,48),(64,64)])"`);
} catch { console.log("favicon.ico skipped (Pillow not installed)"); }
console.log("icons written to", OUT);
