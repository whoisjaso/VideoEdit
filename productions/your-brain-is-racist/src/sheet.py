import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skia, numpy as np
from PIL import Image
from film import Film, FPS
asp = sys.argv[1]; times = [float(x) for x in sys.argv[3:]]; F = Film(asp)
tw, th = (480, 270) if asp == "h" else (216, 384); cols = 5 if asp == "h" else 10
rows = (len(times) + cols - 1) // cols; sh = Image.new("RGB", (cols * tw, rows * th))
for i, t in enumerate(times):
    a = F.frame(int(t * FPS)).makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    sh.paste(Image.fromarray(a[..., :3]).resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
sh.save(sys.argv[2], quality=90)
