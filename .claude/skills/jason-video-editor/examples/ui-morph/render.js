// usage: node render.js stills out/ t1 t2 ...   |   node render.js full out/ [workers]
const { chromium } = require("playwright-core");
const path = require("path"), fs = require("fs");
const [, , mode, out, ...rest] = process.argv;
fs.mkdirSync(out, { recursive: true });
const FPS = 60, SUB = 4, LEN = 14, SHUTTER = 0.5; // 180° shutter: 4 subframes across half a frame
(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--font-render-hinting=none"] });
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await page.goto("file://" + path.resolve(__dirname, "morph.html"));
    await page.evaluate(() => document.fonts.ready);
    return page;
  };
  if (mode === "stills") {
    const page = await open();
    for (const t of rest.map(Number)) { await page.evaluate((t) => seek(t), t); await page.screenshot({ path: path.join(out, `t${t.toFixed(2)}.png`) }); }
  } else {
    const N = Math.round(LEN * FPS) * SUB, workers = Number(rest[0] || 4);
    const pages = await Promise.all(Array.from({ length: workers }, open));
    let next = 0;
    await Promise.all(pages.map(async (page) => {
      while (true) {
        const i = next++; if (i >= N) break;
        const k = Math.floor(i / SUB), j = i % SUB;
        const t = k / FPS + (j / SUB) * (SHUTTER / FPS);
        if (process.env.T0 && (t < +process.env.T0 || t > +process.env.T1)) continue;
        await page.evaluate((t) => seek(t), t);
        await page.screenshot({ path: path.join(out, `s${String(i).padStart(5, "0")}.png`) });
        if (i % 400 === 0) console.log("sub", i, "/", N);
      }
    }));
  }
  await browser.close();
})();
