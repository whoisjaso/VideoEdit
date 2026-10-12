# tools
| file | job | run with |
|---|---|---|
| metengr.py | search the Met (v1.1) and keep only engraving-like public-domain images (low colour, light paper) | python3 |
| metpick.py | download chosen Met objects by id at full res (`id:name[:cut]`) | python3 |
| engrave.py | the one treatment: grayscale, paper → white, ink → #141413; `cut` assets get a rembg alpha cutout | rembg venv python |
| bpm.py / grid.py | tempo and the exact beat/downbeat grid of a track (numpy) | python3 |
| render2.js | plan-driven Playwright renderer (`HTML=ad.html node render2.js plan.json outdir 6`); `CUES=cues.json` dumps `window.CUE_LIST()` | node (playwright-core 1.56.1, Chromium at /opt/pw-browsers) |
| blurplan.py | optical-flow speed per sharp frame → 1–32 samples per frame (240° shutter, ~3 px apart) | venv python with opencv |
| blend.py | float average of samples per frame + TPDF dither, quantised once | venv python |
| qa.py | forensics (pops, stalls, holds > 48 f, still opening, device absent, accent %) + 12 fps contact sheets | python3 |
| mix2.py | SFX by measured peak on picture cue frames; music suck before the drop, stop on the bar line; −14 LUFS | python3 |

**rembg venv** (keeps numpy 2 away from DeepFilterNet):
```
python3 -m venv venv-rembg
venv-rembg/bin/pip install "rembg[cpu]" pillow opencv-python-headless
```
