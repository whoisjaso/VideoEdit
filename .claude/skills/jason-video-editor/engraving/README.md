# Engraving cutaways for talking heads

The ENGRAVING CUTAWAYS rule in `../SKILL.md`, as a reusable engine. Built for episode #5, "Chosen".

## Files
- `ins.html`: pure `seek(t)` page.
  - One orange device travels between key points and lands on each plate's key point. A compass ring draws on at each landing.
  - Keys can ride a plate (`shot`, `fx`, `fy`), so the dot stays glued to the plate while it dollies.
  - A shot can `match` its anchor to another plate's point at the cut frame, which gives a match cut on the device.
  - His words rise one line at a time (`K.maskLine`, bold serif), with an optional small definition line.
  - A white band at the bottom keeps the words readable over dense engraving.
- `scenes.ep05.js`: the episode #5 scenes. Copy and edit it per episode as `scenes.js`.
  - Times are 60 fps frames, local to each insert: `f = (episode frame - insert start) * 2`.
  - Take every time from his words in `captions.json`.
- `full.sh`: render.
  - 30 fps, with 5 subframes per frame across a 180° shutter;
  - `../../jason-ad-film/tools/blend.py` for the float blend;
  - BT.709 encode.
  - `SCENES="a b" ./full.sh` re-renders only the named scenes.
- `ep05-assets.json`: the Met CC0 plates used in episode #5.

## Steps
1. **Copy the files.** Put `ins.html`, `full.sh` and `scenes.js` in a work dir, along with:
   - `../../jason-ad-film/kit/kit.js`;
   - `serif.woff2` (from `../../jason-ad-film/examples/claude-ad-v2/`);
   - `render2.js` (from `../../jason-ad-film/tools/`);
   - a `node_modules` folder containing `playwright-core`.
2. **Get the plates.** Search with `../../jason-ad-film/tools/metengr.py OUT "query" ...`. If that is slow, use a fast title search, then:
   - `metpick.py . id:name ...`
   - `engrave.py .` → `img/NAME.png`
3. **Pick anchors on a gridded sheet.** Choose an eye, a heart, a fingertip, a hat. Check the plate covers the frame down to about 1150 px.
4. **Check stills, then render.** Render stills (a plan of `{o, t}`), then `./full.sh`. Copy the `ins_*.mp4` files to `proj/public/ep/`.
5. **Place them in `Episode.tsx`.** Play each as an `INS` entry with `<Sequence><OffthreadVideo/></Sequence>`. Add the windows to `HIDE`. Put an iOS tink on every landing and a success sound on the payoff.
