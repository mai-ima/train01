"""out/<prefix>_<n>.png を N枚ずつコンタクトシートにする。 usage: sheet.py prefix per_sheet cols [labels...]"""
import sys, glob, re
from PIL import Image, ImageDraw
prefix, per, cols = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
files = sorted(glob.glob(f"/home/claude/station/out/{prefix}_[0-9]*.png"), key=lambda p: int(re.findall(r"_(\d+)\.png", p)[-1]))
labels = sys.argv[4:]
tw, th = 640, 360
for si in range(0, len(files), per):
    chunk = files[si:si + per]
    rows = (len(chunk) + cols - 1) // cols
    W = Image.new("RGB", (cols * tw, rows * th), (20, 20, 24))
    for i, f in enumerate(chunk):
        im = Image.open(f).convert("RGB").resize((tw, th))
        d = ImageDraw.Draw(im)
        idx = si + i
        d.rectangle([0, 0, 150, 18], fill=(0, 0, 0))
        d.text((4, 3), (labels[idx] if idx < len(labels) else str(idx)), fill=(255, 255, 255))
        W.paste(im, ((i % cols) * tw, (i // cols) * th))
    out = f"/home/claude/station/out/{prefix}_sheet{si // per}.png"
    W.save(out); print(out)
