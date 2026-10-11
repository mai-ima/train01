"""穂波野 本社区画の看板画像(オリジナル)。"""
from PIL import Image, ImageDraw
import make_textures as T
OUT = "/home/claude/station/tex"


def plate(name, lines, W=1600, H=420, bg=(28, 36, 33), fg=(226, 205, 140), sub=None, border=(150, 130, 80)):
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, W - 11, H - 11], outline=border, width=8)
    n = len(lines)
    for i, (t, sz) in enumerate(lines):
        y = H * (i + 1) / (n + 1)
        d.text((W / 2, y), t, font=T.font("Bold", sz), fill=fg, anchor="mm")
    im.save(f"{OUT}/{name}.png")


plate("hq_sign", [("日本国有鉄道 本社", 150), ("JAPANESE NATIONAL RAILWAYS  HEAD OFFICE", 44)])
plate("hq_plaque", [("国鉄発祥の地", 120), ("明治五年 初代機関庫跡", 52)], W=1000, H=420, bg=(70, 70, 66), fg=(236, 232, 220), border=(200, 196, 180))
plate("museum_sign", [("鉄道記念館", 170), ("RAILWAY MEMORIAL MUSEUM", 50)], W=1400, H=420, bg=(40, 22, 20), fg=(236, 220, 190), border=(170, 120, 90))
plate("shed_plate", [("初代機関庫", 150), ("保存 昭和三十八年", 52)], W=1000, H=420, bg=(20, 38, 28), fg=(232, 232, 220), border=(180, 190, 160))
plate("mile0_plate", [("零哩標", 160), ("ZERO MILE POST", 48)], W=720, H=420, bg=(238, 236, 226), fg=(30, 30, 30), border=(30, 30, 30))
print("ok")
