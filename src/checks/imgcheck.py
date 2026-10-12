"""撮影画像の自動チェック: 黒つぶれ(平均輝度が低い)/単色(分散が小さい)/白飛びを検出して再撮影候補を出す。usage: imgcheck.py out/prefix_*.png"""
import sys, glob
from PIL import Image, ImageStat
bad = 0
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        im = Image.open(f).convert("L").resize((200, 112))
        st = ImageStat.Stat(im)
        mean, sd = st.mean[0], st.stddev[0]
        hist = im.histogram()
        white = sum(hist[250:]) / sum(hist) * 100
        flags = []
        if mean < 25: flags.append("黒つぶれ")
        if sd < 14: flags.append("単色(遮蔽/壁埋没)")
        if white > 12: flags.append(f"白飛び{white:.0f}%")
        if flags:
            bad += 1; print("NG", f, f"mean={mean:.0f} sd={sd:.0f}", ",".join(flags))
print("不良", bad)
