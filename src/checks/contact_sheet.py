"""全駅コンタクトシート: out/<dir> の *_<n>.png(人物あり)から n 番目の視点を一覧にする(Z1/X11 の目視確認用)。
使い方: python3 contact_sheet.py out/e3b 2 out/sheet_ZA.jpg [列数=6] [サムネ幅=320]   (n=0:A目線 1:E斜め 2:ZA俯瞰)"""
import sys, glob, os
from PIL import Image, ImageDraw
d, n, outp = sys.argv[1], sys.argv[2], sys.argv[3]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
W = int(sys.argv[5]) if len(sys.argv) > 5 else 320
H = W * 9 // 16
fs = [f for f in sorted(glob.glob(f"{d}/*_{n}.png")) if "_np_" not in os.path.basename(f)]
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows), (20, 20, 20))
dr = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    sheet.paste(Image.open(f).convert("RGB").resize((W, H)), ((i % cols) * W, (i // cols) * H))
    dr.rectangle([(i % cols) * W, (i // cols) * H, (i % cols) * W + 64, (i // cols) * H + 16], fill=(0, 0, 0))
    dr.text(((i % cols) * W + 3, (i // cols) * H + 2), os.path.basename(f).split("_")[0], fill=(255, 255, 255))
sheet.save(outp, quality=88)
print(len(fs), "枚 →", outp)
