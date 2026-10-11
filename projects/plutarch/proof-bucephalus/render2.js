// render2.js — plan-driven renderer.  node render2.js PLAN.json OUTDIR [workers]
// PLAN: [{"o":"name.png","t":seconds}, ...]  (sharp pass = one sample per frame; blur pass = many samples per frame)
const { chromium } = require("playwright-core");
const path = require("path"), fs = require("fs");
const [, , planFile, out, W = "6"] = process.argv;
const plan = JSON.parse(fs.readFileSync(planFile, "utf8")).filter((p) => !fs.existsSync(path.join(out, p.o)));
fs.mkdirSync(out, { recursive: true });
(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--font-render-hinting=none"] });
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: +(process.env.VW||1080), height: +(process.env.VH||1920) }, deviceScaleFactor: 1 });
    await page.goto("file://" + path.resolve(__dirname, process.env.HTML || "ad2.html"));
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => 0))));
    await page.evaluate(() => window.ready && window.ready());
    return page;
  };
  const pages = await Promise.all(Array.from({ length: +W }, open));
  let next = 0, done = 0;
  await Promise.all(pages.map(async (page) => {
    while (true) {
      const i = next++; if (i >= plan.length) break;
      await page.evaluate((t) => seek(t), plan[i].t);
      await page.screenshot({ path: path.join(out, plan[i].o), type: "png" });
      if (++done % 300 === 0) console.log(done, "/", plan.length);
    }
  }));
  if (process.env.CUES) fs.writeFileSync(process.env.CUES, JSON.stringify(await pages[0].evaluate(() => window.CUE_LIST && window.CUE_LIST())));
  await browser.close();
})();
