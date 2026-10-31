import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""C17/Q14: 針葉樹(杉)の枝カード用テクスチャ。主軸の小枝から左右に細い側枝が出て、各側枝に短い針葉が密に付く「スプレー」を
アルファ付きで描く(三角ポリゴンに頂点色だけ塗った葉が板状に見える問題の根本対策)。根元が下(v=0)、先端が上(v=1)。原作オリジナルの手続き生成。"""
import math, random
import numpy as np
from PIL import Image, ImageDraw


def spray(seed, W=256, H=512, SS=3):
    rnd = random.Random(seed)
    w, h = W * SS, H * SS
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w * 0.5
    x0, y0 = cx, h * 0.97          # 根元
    x1, y1 = cx + rnd.uniform(-0.03, 0.03) * w, h * 0.03    # 先端

    def needle(px, py, ang, ln, shade):
        ex, ey = px + math.cos(ang) * ln, py + math.sin(ang) * ln
        g = int(255 * shade)
        col = (int(g * rnd.uniform(0.52, 0.72)), int(g * rnd.uniform(0.82, 1.0)), int(g * rnd.uniform(0.28, 0.5)), 255)
        d.line([(px, py), (ex, ey)], fill=col, width=max(1, int(rnd.uniform(1.1, 1.9) * SS)))

    # 主軸
    n_axis = 60
    for i in range(n_axis + 1):
        t = i / n_axis
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        # 主軸の針葉(前向き)
        for _ in range(3):
            ang = -math.pi / 2 + rnd.uniform(-0.7, 0.7)
            needle(px, py, ang, rnd.uniform(0.045, 0.075) * w, rnd.uniform(0.55, 1.0))
    d.line([(x0, y0), (x1, y1)], fill=(52, 38, 22, 255), width=int(2.4 * SS))
    # 側枝(左右・先端ほど短く、斜め上へ)
    n_side = 22
    for i in range(n_side):
        t = 0.04 + 0.94 * i / (n_side - 1)
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for sd in (-1, 1):
            if rnd.random() < 0.08:
                continue
            L = (0.46 - 0.30 * t) * w * rnd.uniform(0.85, 1.15)
            a0 = -math.pi / 2 + sd * rnd.uniform(0.85, 1.15) * (1.2 - 0.35 * t)       # 根元側は水平に近く、先端側は上向き
            nseg = 14
            qx, qy = px, py
            for k in range(1, nseg + 1):
                f = k / nseg
                a = a0 + sd * 0.25 * f * f - 0.0
                step = L / nseg
                qx2, qy2 = qx + math.cos(a) * step, qy + math.sin(a) * step + 0.35 * step * f * f
                d.line([(qx, qy), (qx2, qy2)], fill=(58, 42, 24, 255), width=max(1, int(1.1 * SS)))
                for _ in range(3):
                    s2 = rnd.choice((-1, 1))
                    ang = math.atan2(qy2 - qy, qx2 - qx) + s2 * rnd.uniform(0.6, 1.25)
                    needle(qx2, qy2, ang, rnd.uniform(0.035, 0.07) * w * (1.0 - 0.35 * f), rnd.uniform(0.5, 1.0) * (0.75 + 0.25 * f))
                qx, qy = qx2, qy2
    im = im.resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype(float)
    # 縁の毛羽を整える: アルファを少し締める
    a[..., 3] = np.clip((a[..., 3] - 40) * 1.25, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def leafspray(seed, W=256, H=256, SS=3):
    """広葉樹の葉房: 短い小枝から卵形の葉が重なって付く(アルファ付き)。葉ごとに色味と向きが違う。"""
    rnd = random.Random(seed)
    w, h = W * SS, H * SS
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = w * 0.5, h * 0.5
    def leaf(px, py, ang, ln, wd, shade):
        pts = []
        for k in range(17):
            t = k / 16.0
            ww = wd * math.sin(math.pi * t) ** 0.8 * (1.0 - 0.35 * t)
            pts.append((t * ln, ww))
        poly = [(px + math.cos(ang) * a - math.sin(ang) * b, py + math.sin(ang) * a + math.cos(ang) * b) for a, b in pts]
        poly += [(px + math.cos(ang) * a + math.sin(ang) * b, py + math.sin(ang) * a - math.cos(ang) * b) for a, b in reversed(pts)]
        g = int(255 * shade)
        d.polygon(poly, fill=(int(g * rnd.uniform(0.45, 0.7)), int(g * rnd.uniform(0.85, 1.0)), int(g * rnd.uniform(0.25, 0.45)), 255))
        d.line([(px, py), (px + math.cos(ang) * ln * 0.92, py + math.sin(ang) * ln * 0.92)], fill=(int(g * 0.9), int(g * 1.0), int(g * 0.5), 255), width=max(1, SS))
    for k in range(34):
        ang = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(0.0, 0.30) * w
        px, py = cx + math.cos(ang) * r0 * 0.55, cy + math.sin(ang) * r0 * 0.55
        ln = rnd.uniform(0.17, 0.27) * w
        leaf(px, py, ang + rnd.uniform(-0.5, 0.5), ln, ln * rnd.uniform(0.26, 0.38), rnd.uniform(0.5, 1.0))
    im = im.resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype(float)
    a[..., 3] = np.clip((a[..., 3] - 30) * 1.3, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


if __name__ == "__main__":
    out = _os.path.join(_R, "tex")
    _os.makedirs(out, exist_ok=True)
    atlas = Image.new("RGBA", (256 * 4, 512), (0, 0, 0, 0))     # 4種の枝を横に並べたアトラス(UVで選ぶ)
    for k in range(4):
        atlas.paste(spray(101 + k * 17), (256 * k, 0))
    atlas.save(_os.path.join(out, "conifer_spray.png"))
    la = Image.new("RGBA", (256 * 4, 256), (0, 0, 0, 0))
    for k in range(4):
        la.paste(leafspray(201 + k * 13), (256 * k, 0))
    la.save(_os.path.join(out, "broadleaf_spray.png"))
    print("saved", _os.path.join(out, "conifer_spray.png"))
