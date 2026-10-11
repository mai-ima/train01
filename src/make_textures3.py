"""Vehicle marking textures (white/cream stencil on transparent) + number plates."""
import sys
sys.argv = sys.argv[:1]
from make_textures2 import *
from PIL import Image, ImageDraw
import random

def stencil(name, size, lines, col=(236, 230, 210, 235), seed=1):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for (xy, s, kind, wt, sz, anchor) in lines:
        text(d, xy, s, font(kind, wt, sz), col, anchor)
    # worn paint: knock out blotches
    a = np.array(im).astype(float)
    n = noise_layer(size, 6, seed) * 0.6 + noise_layer(size, 22, seed + 3) * 0.4
    a[..., 3] *= np.clip((n - 0.25) * 2.6, 0.35, 1.0)
    Image.fromarray(a.astype(np.uint8), "RGBA").save(f"tex/{name}.png")

stencil("mark_wam", (512, 256), [((256, 70), "ワム", "Sans", "Bold", 90, "mm"), ((256, 160), "23087", "Sans", "Bold", 64, "mm"),
        ((256, 224), "荷重 15t  自重 9.4t", "Sans", "Medium", 30, "mm")], seed=2)
stencil("mark_tora", (512, 200), [((256, 60), "ト ラ", "Sans", "Bold", 80, "mm"), ((256, 140), "20417", "Sans", "Bold", 60, "mm"),
        ((256, 185), "荷重 17t", "Sans", "Medium", 28, "mm")], seed=4)
stencil("mark_yo", (400, 160), [((200, 50), "ヨ", "Sans", "Bold", 70, "mm"), ((200, 120), "3512", "Sans", "Bold", 54, "mm")], seed=6)
stencil("mark_coach", (700, 120), [((350, 60), "オハ 35  2214", "Sans", "Bold", 74, "mm")], col=(232, 214, 150, 235), seed=8)
stencil("mark_coach2", (700, 120), [((350, 60), "スハフ 32  2188", "Sans", "Bold", 74, "mm")], col=(232, 214, 150, 235), seed=9)
stencil("mark_depot", (500, 120), [((250, 60), "穂波野機関区", "Sans", "Bold", 62, "mm")], col=(236, 230, 210, 235), seed=10)

def plate(name, size, bg, fg, s, sz, seed):
    im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, size[0] - 5, size[1] - 5], outline=fg, width=4)
    text(d, (size[0] // 2, size[1] // 2), s, font("Sans", "Bold", sz), fg)
    im = age(im, rust=0.2, seed=seed)
    im.save(f"tex/{name}.png")

plate("plate_dd", (420, 160), (120, 22, 18), (240, 232, 205), "DD 9 4", 92, 3)
plate("plate_c", (420, 160), (14, 12, 12), (235, 215, 150), "C 5 7 1 3 8", 76, 5)
plate("plate_d", (420, 160), (14, 12, 12), (235, 215, 150), "D 5 1 4 6 2", 76, 6)
plate("plate_ex", (420, 160), (20, 50, 90), (240, 240, 230), "EX 1", 92, 7)
print("ok")
