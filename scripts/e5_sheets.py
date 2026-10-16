"""E5撮影物のコンタクトシート: (1) 視点別(全駅を並べて個性の違いを見る) (2) 駅別(6視点)。出力 out/e5/sheets/*.jpg(JPEG q88)"""
import os, glob, re
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.abspath(__file__))
D = f"{R}/out/e5"; O = f"{D}/sheets"; os.makedirs(O, exist_ok=True)
sids = sorted({re.match(r"([A-Z0-9]+)_\d\.png", os.path.basename(p)).group(1) for p in glob.glob(f"{D}/*_[0-9].png")})
VN = ["A俯瞰", "E斜め", "ZA個性", "L象徴", "F正面", "Pホーム"]
def tile(p, w, h, lab):
    im = Image.open(p).convert("RGB").resize((w, h)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 120, 16], fill=(0, 0, 0)); d.text((4, 2), lab, fill=(255, 255, 255)); return im
for v in range(6):
    fs = [(s, f"{D}/{s}_{v}.png") for s in sids if os.path.exists(f"{D}/{s}_{v}.png")]
    if not fs: continue
    cols = 5; rows = (len(fs) + cols - 1) // cols; tw, th = 480, 270
    W = Image.new("RGB", (cols * tw, rows * th), (20, 20, 24))
    for i, (s, p) in enumerate(fs): W.paste(tile(p, tw, th, f"{s} {VN[v]}"), ((i % cols) * tw, (i // cols) * th))
    W.save(f"{O}/view{v}_{VN[v]}.jpg", quality=88)
for s in sids:
    fs = [(v, f"{D}/{s}_{v}.png") for v in range(6) if os.path.exists(f"{D}/{s}_{v}.png")]
    tw, th = 640, 360; W = Image.new("RGB", (3 * tw, 2 * th), (20, 20, 24))
    for i, (v, p) in enumerate(fs): W.paste(tile(p, tw, th, f"{s} {VN[v]}"), ((i % 3) * tw, (i // 3) * th))
    W.save(f"{O}/station_{s}.jpg", quality=88)
print(len(sids), "駅のシートを", O, "に出力")
