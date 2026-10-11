"""P6: 会社別ロゴ・社紋、ヘッドマーク(作成のみ・未装着)、方向幕(行先表示)、中吊り広告、車内路線図、番号板。
すべて原作オリジナル(実在の社名・標章は使わない)。tex/ に保存。"""
import sys
sys.argv = sys.argv[:1]
import math
from make_textures2 import *
from PIL import Image, ImageDraw

OUTD = "/home/claude/station/tex"

# 会社: id → (名称, 主色, 副色)
CO = {
    "jnr": ("国鉄", (0, 70, 140), (240, 236, 220)),
    "ke": ("国都電鉄", (110, 14, 20), (226, 190, 96)),
    "km": ("国都地下鉄", (190, 20, 30), (230, 232, 235)),
    "tr": ("大湊市電", (20, 100, 60), (238, 224, 170)),
    "bm": ("湾岸モノレール", (16, 70, 150), (230, 236, 240)),
    "hr": ("臨港線", (20, 30, 70), (222, 170, 40)),
    "sr": ("山麓鉄道", (150, 60, 20), (236, 226, 196)),
}
S = 4          # スーパーサンプリング


def canvas(w, h, bg=(0, 0, 0, 0)):
    im = Image.new("RGBA", (w * S, h * S), bg)
    return im, ImageDraw.Draw(im)


def fin(im, w, h, path):
    im.resize((w, h), Image.LANCZOS).save(path)


def logo(cid):
    name, c1, c2 = CO[cid]
    W = 512
    im, d = canvas(W, W)
    s = lambda v: int(v * S)
    cx = cy = s(W / 2)
    if cid == "jnr":      # 双翼を思わせる車輪+横線(原作オリジナル)
        d.ellipse([s(40), s(40), s(472), s(472)], fill=c1)
        d.ellipse([s(70), s(70), s(442), s(442)], outline=c2, width=s(10))
        for k in range(8):
            a = k * math.pi / 4
            d.line([cx, cy, cx + s(150) * math.cos(a), cy + s(150) * math.sin(a)], fill=c2, width=s(10))
        d.ellipse([cx - s(40), cy - s(40), cx + s(40), cy + s(40)], fill=c2)
        d.rectangle([s(150), s(232), s(362), s(280)], fill=c1)
        d.text((cx, cy + s(2)), "国", font=SANS("Black", s(58)), fill=c2, anchor="mm")
    elif cid == "ke":     # 円に流れる波と頭文字
        d.ellipse([s(30), s(30), s(482), s(482)], fill=c1)
        d.ellipse([s(54), s(54), s(458), s(458)], outline=c2, width=s(12))
        for k in range(3):
            pts = [(s(120 + x), s(300 + k * 34 + 22 * math.sin(x / 38 + k))) for x in range(0, 272, 6)]
            d.line(pts, fill=c2, width=s(10))
        d.text((cx, s(205)), "都", font=SERIF("Black", s(190)), fill=c2, anchor="mm")
    elif cid == "km":     # 丸い坑口(アーチ)と二本のレール
        d.ellipse([s(24), s(24), s(488), s(488)], fill=c1)
        d.pieslice([s(120), s(110), s(392), s(382)], 180, 360, fill=c2)
        d.rectangle([s(120), s(246), s(392), s(400)], fill=c2)
        d.pieslice([s(160), s(150), s(352), s(342)], 180, 360, fill=c1)
        d.rectangle([s(160), s(246), s(352), s(400)], fill=c1)
        for xx in (214, 298):
            d.polygon([(s(xx - 6), s(252)), (s(xx + 6), s(252)), (s(xx + 30 * (1 if xx > 256 else -1) + 6), s(400)), (s(xx + 30 * (1 if xx > 256 else -1) - 6), s(400))], fill=c2)
        d.text((cx, s(440)), "地", font=SANS("Black", s(60)), fill=c2, anchor="mm")
    elif cid == "tr":     # 車輪+集電棒(トロリーポール)と架線
        d.rounded_rectangle([s(40), s(40), s(472), s(472)], radius=s(90), fill=c1)
        d.ellipse([s(146), s(236), s(366), s(456)], outline=c2, width=s(22))
        d.ellipse([s(236), s(326), s(276), s(366)], fill=c2)
        for k in range(6):
            a_ = k * math.pi / 3
            d.line([s(256), s(346), s(256) + s(100) * math.cos(a_), s(346) + s(100) * math.sin(a_)], fill=c2, width=s(8))
        d.line([s(256), s(236), s(340), s(110)], fill=c2, width=s(14))
        d.line([s(70), s(96), s(442), s(96)], fill=c2, width=s(10))
        d.ellipse([s(330), s(100), s(352), s(122)], fill=c2)
    elif cid == "bm":     # 一本の桁と波
        d.rounded_rectangle([s(30), s(110), s(482), s(402)], radius=s(120), fill=c1)
        d.rectangle([s(90), s(196), s(422), s(232)], fill=c2)
        for k in range(2):
            pts = [(s(90 + x), s(290 + k * 44 + 14 * math.sin(x / 26))) for x in range(0, 332, 6)]
            d.line(pts, fill=c2, width=s(12))
    elif cid == "hr":     # 錨+レール
        d.ellipse([s(34), s(34), s(478), s(478)], fill=c1)
        d.line([cx, s(130), cx, s(400)], fill=c2, width=s(26))
        d.arc([s(120), s(270), s(392), s(450)], 10, 170, fill=c2, width=s(26))
        d.ellipse([cx - s(30), s(96), cx + s(30), s(156)], outline=c2, width=s(20))
        d.line([s(190), s(192), s(322), s(192)], fill=c2, width=s(22))
    else:                 # sr 山と線路
        d.rounded_rectangle([s(36), s(36), s(476), s(476)], radius=s(60), fill=c1)
        d.polygon([(s(60), s(380)), (s(190), s(150)), (s(260), s(270)), (s(330), s(190)), (s(452), s(380))], fill=c2)
        d.polygon([(s(190), s(150)), (s(160), s(205)), (s(215), s(200))], fill=(250, 250, 250))
        for xx in (150, 362):
            d.line([(s(xx), s(380)), (s(256), s(300))], fill=c1, width=s(12))
    fin(im, W, W, f"{OUTD}/logo_{cid}.png")


# ---- ヘッドマーク(愛称入り・内照式の琺瑯/アクリル板風) 実在の作法: 円形(蒸機時代〜)/楕円/角形(電車・気動車の電照式)、
#      列車名を大きく+種別の帯+図案(列車名にちなむ景物)。すべて原作オリジナルの愛称と図案。
HM = [  # (id, 題字, 種別, 場面, 形, 配色)
    ("honami_ltd", "穂波", "特急", "honami", "circle", dict(sky=((250, 226, 150), (244, 170, 80)), ink=(20, 70, 40), rim=(176, 150, 70), band=(150, 24, 20))),
    ("yunosato", "ゆのさと", "急行", "yu", "circle", dict(sky=((250, 240, 214), (236, 196, 150)), ink=(120, 40, 18), rim=(150, 80, 40), band=(150, 24, 20))),
    ("minato", "みなと", "急行", "minato", "oval", dict(sky=((190, 224, 244), (250, 246, 232)), ink=(14, 44, 100), rim=(150, 150, 160), band=(14, 44, 100))),
    ("honami_night", "ほなみ", "寝台特急", "night", "circle", dict(sky=((10, 20, 60), (40, 60, 120)), ink=(240, 226, 150), rim=(170, 160, 120), band=(150, 24, 20))),
    ("airport_honami", "エアポート穂波", "特急", "airport", "rect", dict(sky=((16, 80, 150), (120, 190, 232)), ink=(250, 250, 250), rim=(190, 190, 196), band=(220, 130, 20))),
    ("airliner", "空港ライナー", "快速", "airliner", "oval", dict(sky=((30, 100, 170), (240, 170, 90)), ink=(250, 250, 250), rim=(180, 180, 190), band=(20, 60, 110))),
    ("mizuho_liner", "みずほ", "ホームライナー", "mizuho", "rect", dict(sky=((250, 240, 190), (230, 200, 110)), ink=(40, 80, 30), rim=(150, 150, 130), band=(40, 80, 30))),
    ("ski", "ゆきみ", "スキー臨", "ski", "circle", dict(sky=((160, 200, 240), (246, 250, 255)), ink=(20, 60, 120), rim=(180, 190, 200), band=(20, 60, 120))),
    ("umi", "いそべ", "海水浴臨", "umi", "circle", dict(sky=((120, 200, 240), (252, 240, 200)), ink=(10, 80, 130), rim=(176, 170, 140), band=(220, 100, 30))),
]


def _grad(w, h, c0, c1):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(c0)[None, None, :] * (1 - a) + np.array(c1)[None, None, :] * a)
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def _polyfill(im, pts, fill):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    if isinstance(fill, Image.Image):
        im.paste(fill, (0, 0), m)
    else:
        im.paste(Image.new("RGBA", im.size, tuple(fill) + (255,)), (0, 0), m)


def _scene(im, kind, box, P):
    """box=(x0,y0,x1,y1) の景物を描く(スーパーサンプル済み座標)。"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d = ImageDraw.Draw(im)
    sky = _grad(im.size[0], im.size[1], *P["sky"])
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rectangle(box, fill=255)
    im.paste(sky, (0, 0), m)
    ink = P["ink"]
    X = lambda u: x0 + u * w
    Y = lambda v: y0 + v * h

    def poly(pts, col):
        _polyfill(im, [(X(u), Y(v)) for u, v in pts], col)
    if kind == "honami":          # 朝日と稲穂の波打つ田
        d.ellipse([X(0.30), Y(0.30), X(0.70), Y(0.78)], fill=(250, 120, 40))
        for k in range(14):
            a = -math.pi + k * math.pi / 13
            d.line([X(0.5), Y(0.62), X(0.5) + w * 0.62 * math.cos(a), Y(0.62) + h * 0.62 * math.sin(a)], fill=(250, 190, 90), width=max(2, int(w * 0.012)))
        for r_, c_ in ((0.0, (60, 120, 50)), (0.14, (36, 92, 40)), (0.28, (20, 66, 34))):
            pts = [(u / 40.0, 0.72 + r_ * 0.8 + 0.035 * math.sin(u / 5.5 + r_ * 20)) for u in range(0, 41)] + [(1, 1.0), (0, 1.0)]
            poly(pts, c_)
        for k in range(5):
            bx = 0.14 + k * 0.18
            d.line([X(bx), Y(0.95), X(bx + 0.04), Y(0.62)], fill=(236, 200, 80), width=max(2, int(w * 0.012)))
            for j in range(6):
                d.ellipse([X(bx + 0.04 - 0.025 + j * 0.003), Y(0.62 + j * 0.03) - w * 0.012, X(bx + 0.04 + 0.025 + j * 0.003), Y(0.62 + j * 0.03) + w * 0.012], fill=(240, 210, 90))
    elif kind == "yu":            # 湯けむりと湯の山
        poly([(0, 0.82), (0.0, 0.55), (0.22, 0.36), (0.38, 0.52), (0.58, 0.28), (0.82, 0.55), (1, 0.45), (1, 0.82)], (110, 150, 120))
        poly([(0, 1), (0, 0.76), (1, 0.76), (1, 1)], (200, 120, 60))
        d.rounded_rectangle([X(0.26), Y(0.64), X(0.74), Y(0.92)], radius=int(h * 0.1), fill=(126, 70, 30))
        d.ellipse([X(0.30), Y(0.60), X(0.70), Y(0.70)], fill=(120, 190, 220))
        for k, dx in enumerate((-0.16, 0.0, 0.16)):
            pts = [(X(0.5 + dx) + w * 0.035 * math.sin(yy / (h * 0.11) + k * 1.4), Y(0.58) - yy) for yy in range(0, int(h * 0.44), 3)]
            d.line(pts, fill=(250, 250, 248), width=max(3, int(w * 0.05)), joint="curve")
    elif kind == "minato":        # 灯台と帆船と波
        poly([(0, 0.66), (0, 1), (1, 1), (1, 0.66)], (24, 80, 140))
        for k in range(5):
            pts = [(u / 30.0, 0.74 + k * 0.05 + 0.014 * math.sin(u * 0.9 + k)) for u in range(31)]
            d.line([(X(a_), Y(b_)) for a_, b_ in pts], fill=(200, 230, 250), width=max(2, int(h * 0.012)))
        poly([(0.08, 0.68), (0.18, 0.68), (0.16, 0.22), (0.10, 0.22)], (250, 250, 248))
        poly([(0.10, 0.22), (0.16, 0.22), (0.13, 0.12)], (190, 30, 30))
        d.rectangle([X(0.095), Y(0.18), X(0.165), Y(0.23)], fill=(250, 230, 120))
        poly([(0.34, 0.70), (0.92, 0.70), (0.84, 0.82), (0.42, 0.82)], (28, 30, 40))
        d.line([X(0.62), Y(0.70), X(0.62), Y(0.14)], fill=(70, 50, 30), width=max(2, int(w * 0.012)))
        poly([(0.64, 0.16), (0.88, 0.66), (0.64, 0.66)], (250, 248, 240))
        poly([(0.60, 0.26), (0.40, 0.66), (0.60, 0.66)], (240, 236, 224))
    elif kind == "night":         # 月と星と山影
        d.ellipse([X(0.55), Y(0.14), X(0.80), Y(0.14) + w * 0.25], fill=(250, 240, 190))
        d.ellipse([X(0.60), Y(0.10), X(0.84), Y(0.10) + w * 0.24], fill=P["sky"][0])
        rng = np.random.default_rng(4)
        for _ in range(40):
            sx, sy = x0 + rng.random() * w, y0 + rng.random() * h * 0.6
            r_ = max(2, int(w * 0.006 * (1 + rng.random() * 1.5)))
            d.ellipse([sx - r_, sy - r_, sx + r_, sy + r_], fill=(250, 246, 220))
        poly([(0, 1), (0, 0.72), (0.18, 0.55), (0.34, 0.68), (0.52, 0.48), (0.72, 0.66), (0.88, 0.58), (1, 0.7), (1, 1)], (14, 24, 40))
        poly([(0, 1), (0, 0.88), (1, 0.84), (1, 1)], (6, 12, 22))
        for k in range(6):
            d.rectangle([X(0.10 + k * 0.14), Y(0.90), X(0.10 + k * 0.14 + 0.06), Y(0.94)], fill=(250, 220, 120))
    elif kind == "airport":       # 旅客機と滑走路
        poly([(0, 1), (0, 0.78), (1, 0.78), (1, 1)], (60, 64, 72))
        for k in range(8):
            d.rectangle([X(0.04 + k * 0.125), Y(0.88), X(0.04 + k * 0.125 + 0.07), Y(0.90)], fill=(250, 250, 240))
        poly([(0.10, 0.50), (0.78, 0.42), (0.94, 0.46), (0.78, 0.52)], (250, 250, 250))
        poly([(0.40, 0.46), (0.28, 0.14), (0.40, 0.14), (0.60, 0.44)], (230, 236, 244))
        poly([(0.42, 0.52), (0.30, 0.80), (0.42, 0.80), (0.60, 0.52)], (216, 224, 234))
        poly([(0.12, 0.49), (0.08, 0.30), (0.17, 0.32), (0.24, 0.48)], (220, 130, 20))
        for k in range(6):
            d.ellipse([X(0.50 + k * 0.05), Y(0.435), X(0.50 + k * 0.05 + 0.025), Y(0.465)], fill=(40, 70, 110))
    elif kind == "airliner":      # 夕空へ上がる機影と軌跡
        d.ellipse([X(0.60), Y(0.44), X(0.96), Y(0.44) + w * 0.36], fill=(252, 214, 120))
        poly([(0, 1), (0, 0.86), (1, 0.82), (1, 1)], (20, 40, 80))
        pl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        cx, cy = X(0.52), Y(0.46)
        sc_ = w * 0.9
        body = [(-0.32, 0.00), (0.26, -0.035), (0.38, 0.0), (0.26, 0.035)]
        pd.polygon([(cx + sc_ * a_, cy + sc_ * b_) for a_, b_ in body], fill=(250, 250, 250))
        pd.polygon([(cx + sc_ * a_, cy + sc_ * b_) for a_, b_ in ((0.04, -0.02), (-0.12, -0.36), (-0.04, -0.36), (0.14, -0.02))], fill=(232, 238, 246))
        pd.polygon([(cx + sc_ * a_, cy + sc_ * b_) for a_, b_ in ((0.04, 0.02), (-0.12, 0.34), (-0.04, 0.34), (0.14, 0.02))], fill=(214, 222, 234))
        pd.polygon([(cx + sc_ * a_, cy + sc_ * b_) for a_, b_ in ((-0.30, -0.01), (-0.36, -0.14), (-0.27, -0.14), (-0.20, -0.01))], fill=(220, 130, 20))
        pl = pl.rotate(16, resample=Image.BICUBIC, center=(cx, cy))
        im.alpha_composite(pl)
        for k in range(3):
            d.line([X(0.0), Y(0.80 - k * 0.04), X(0.26), Y(0.64 - k * 0.04)], fill=(250, 250, 250), width=max(2, int(h * 0.014)))
    elif kind == "mizuho":        # 実った稲穂(通勤客の朝)
        for k in range(3):
            ox = k * 0.07
            pts = [(X(0.20 + ox + 0.5 * u), Y(0.95 - 0.78 * u + 0.10 * math.sin(u * 3.0))) for u in np.linspace(0, 1, 40)]
            d.line(pts, fill=(160, 120, 40), width=max(3, int(w * 0.014)))
            for j in range(11):
                u = 0.35 + j * 0.06
                px, py = X(0.20 + ox + 0.5 * u), Y(0.95 - 0.78 * u + 0.10 * math.sin(u * 3.0))
                for sg in (-1, 1):
                    d.ellipse([px + sg * w * 0.015 - w * 0.03, py - h * 0.03, px + sg * w * 0.015 + w * 0.03, py + h * 0.03], fill=(236, 190, 70))
        d.rectangle([X(0.0), Y(0.92), X(1.0), Y(0.94)], fill=(60, 90, 40))
    elif kind == "ski":           # 雪山とシュプール
        poly([(0, 1), (0, 0.5), (0.30, 0.18), (0.50, 0.42), (0.70, 0.12), (1, 0.52), (1, 1)], (230, 240, 250))
        poly([(0.30, 0.18), (0.22, 0.36), (0.36, 0.30)], (150, 180, 210))
        poly([(0.70, 0.12), (0.60, 0.36), (0.78, 0.28)], (150, 180, 210))
        poly([(0, 1), (0, 0.72), (1, 0.66), (1, 1)], (250, 252, 255))
        for k in (0, 1):
            pts = [(X(0.30 + k * 0.03 + 0.14 * math.sin(u * 5)), Y(0.62 + 0.36 * u)) for u in np.linspace(0, 1, 40)]
            d.line(pts, fill=(130, 170, 210), width=max(2, int(w * 0.008)))
    elif kind == "umi":           # 海と入道雲と浜
        d.ellipse([X(0.62), Y(0.10), X(0.88), Y(0.10) + w * 0.26], fill=(252, 220, 90))
        for (cx_, cy_, r_) in ((0.28, 0.34, 0.14), (0.40, 0.30, 0.17), (0.18, 0.40, 0.11), (0.50, 0.38, 0.12)):
            d.ellipse([X(cx_ - r_), Y(cy_ - r_), X(cx_ + r_), Y(cy_ + r_)], fill=(252, 252, 250))
        poly([(0, 1), (0, 0.52), (1, 0.52), (1, 1)], (30, 130, 190))
        for k in range(4):
            pts = [(u / 30.0, 0.58 + k * 0.08 + 0.016 * math.sin(u * 1.1 + k)) for u in range(31)]
            d.line([(X(a_), Y(b_)) for a_, b_ in pts], fill=(220, 244, 252), width=max(2, int(h * 0.012)))
        poly([(0, 1), (0, 0.88), (1, 0.84), (1, 1)], (240, 220, 160))


def headmark_train(h):
    """愛称入りヘッドマーク(内照式の琺瑯板風・未装着)。"""
    tid, title, kind, scene, shape, P = h
    W, H = {"circle": (720, 720), "oval": (900, 640), "rect": (960, 560)}[shape]
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    s = lambda v: int(v * S)
    rim = P["rim"]
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    if shape == "rect":
        md.rounded_rectangle([0, 0, W * S - 1, H * S - 1], radius=s(70), fill=255)
    else:
        md.ellipse([0, 0, W * S - 1, H * S - 1], fill=255)
    base = Image.new("RGBA", im.size, tuple(rim) + (255,))
    rg = _grad(im.size[0], im.size[1], tuple(min(255, c + 60) for c in rim), tuple(max(0, c - 70) for c in rim))
    im.paste(rg, (0, 0), mask)
    inset = s(22)
    inner = Image.new("RGBA", im.size, (0, 0, 0, 0))
    imask = Image.new("L", im.size, 0)
    idr = ImageDraw.Draw(imask)
    if shape == "rect":
        idr.rounded_rectangle([inset, inset, W * S - inset, H * S - inset], radius=s(52), fill=255)
    else:
        idr.ellipse([inset, inset, W * S - inset, H * S - inset], fill=255)
    # 絵の領域
    if shape == "circle":
        box = (s(W * 0.05), s(H * 0.06), s(W * 0.95), s(H * 0.66))
    elif shape == "oval":
        box = (s(W * 0.10), s(H * 0.16), s(W * 0.46), s(H * 0.84))
    else:
        box = (s(W * 0.05), s(H * 0.08), s(W * 0.40), s(H * 0.92))
    # 地(空色)全体を内側に敷く
    fullbox = (0, 0, W * S, H * S)
    bg = Image.new("RGBA", im.size, (0, 0, 0, 0))
    skyg = _grad(im.size[0], im.size[1], *P["sky"])
    bg.paste(skyg, (0, 0), imask)
    im = Image.alpha_composite(im, bg)
    # 景物(アルファ合成。円形は箱の下端を下へ引き伸ばして縁まで絵を延ばす)
    sc = Image.new("RGBA", im.size, (0, 0, 0, 0))
    _scene(sc, scene, box, P)
    if shape == "circle":
        sa = np.asarray(sc).copy()
        yb = box[3] - 1
        sa[yb:, box[0]:box[2]] = sa[yb, box[0]:box[2]][None, :, :]
        sc = Image.fromarray(sa, "RGBA")
    scm = Image.new("L", im.size, 0)
    sd = ImageDraw.Draw(scm)
    if shape == "circle":
        sd.ellipse([inset, inset, W * S - inset, H * S - inset], fill=255)
        sd.rectangle([0, 0, box[0] - 1, H * S], fill=0)
        sd.rectangle([box[2], 0, W * S, H * S], fill=0)
    else:
        sd.rounded_rectangle(box, radius=s(34), fill=255)
    if shape == "oval":
        scm = Image.fromarray((np.minimum(np.asarray(scm), np.asarray(imask))).astype(np.uint8), "L")
    sa2 = np.asarray(sc).copy()
    sa2[..., 3] = (sa2[..., 3].astype(np.float32) * (np.asarray(scm).astype(np.float32) / 255.0)).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(sa2, "RGBA"))
    d = ImageDraw.Draw(im)
    ink = P["ink"]
    # 題字と種別帯
    if shape == "circle":
        d.rounded_rectangle([s(W * 0.10), s(H * 0.675), s(W * 0.90), s(H * 0.885)], radius=s(34), fill=(250, 246, 232), outline=P["band"], width=s(6))
        ft = SERIF("Black", s(140 if len(title) <= 3 else 100))
        ink_t = ink if sum(ink) < 500 else P["band"]
        d.text((s(W / 2), s(H * 0.78)), title, font=ft, fill=ink_t, anchor="mm")
        d.rounded_rectangle([s(W * 0.30), s(H * 0.585), s(W * 0.70), s(H * 0.665)], radius=s(18), fill=P["band"])
        d.text((s(W / 2), s(H * 0.625)), kind, font=SANS("Black", s(44 if len(kind) <= 4 else 36)), fill=(250, 250, 244), anchor="mm")
    else:
        tx = W * (0.70 if shape == "oval" else 0.69)
        n = len(title)
        fsz = int(min(130, (W * (0.46 if shape == "oval" else 0.52)) / max(1, n)))
        d.text((s(tx), s(H * 0.42)), title, font=SERIF("Black", s(fsz)), fill=ink, anchor="mm", stroke_width=s(3), stroke_fill=(30, 30, 30) if ink[0] > 200 else (255, 255, 255))
        bw = W * (0.40 if shape == "oval" else 0.46)
        d.rounded_rectangle([s(tx - bw / 2), s(H * 0.66), s(tx + bw / 2), s(H * 0.80)], radius=s(26), fill=P["band"])
        d.text((s(tx), s(H * 0.733)), kind, font=SANS("Black", s(64 if len(kind) <= 4 else 50)), fill=(250, 250, 244), anchor="mm")
    # 縁のリベット
    if shape == "circle":
        for k in range(24):
            a = k * 2 * math.pi / 24
            cx, cy = s(W / 2) + (s(W / 2) - s(11)) * math.cos(a), s(H / 2) + (s(H / 2) - s(11)) * math.sin(a)
            d.ellipse([cx - s(4), cy - s(4), cx + s(4), cy + s(4)], fill=tuple(max(0, c - 60) for c in rim))
    # 内照式のつや(上からの光沢+縁の陰影)
    arr = np.asarray(im).astype(np.float32)
    hh, ww = arr.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww]
    nx, ny = (xx - ww / 2) / (ww / 2), (yy - hh / 2) / (hh / 2)
    rr = np.sqrt(nx ** 2 + ny ** 2)
    light = 1.06 - 0.20 * np.clip(rr, 0, 1.2) ** 2 + 0.07 * (-ny)
    arr[..., :3] = np.clip(arr[..., :3] * light[..., None], 0, 255)
    rng = np.random.default_rng(sum(map(ord, tid)))
    gr = rng.normal(0, 3.0, (hh // 4, ww // 4)).astype(np.float32)
    gr = np.kron(gr, np.ones((4, 4), np.float32))[:hh, :ww]
    arr[..., :3] = np.clip(arr[..., :3] + gr[..., None], 0, 255)
    im2 = Image.fromarray(arr.astype(np.uint8), "RGBA")
    out = im2.resize((W, H), Image.LANCZOS)
    a = out.split()[3]
    a = Image.composite(a, Image.new("L", out.size, 0), a)
    out.putalpha(mask.resize((W, H), Image.LANCZOS))
    out.save(f"{OUTD}/hm_{tid}.png")


# ---- 非営業の掲出板(回送・試運転): 実際の運用で使う無地の白/黒の標識板
def plate_kaiso():
    im = Image.new("RGB", (560, 200), (18, 18, 20))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, 553, 193], radius=22, outline=(240, 240, 232), width=8)
    d.text((280, 100), "回　送", font=font("Sans", "Black", 110), fill=(246, 246, 238), anchor="mm")
    age(im, rust=0.1, seed=9).save(f"{OUTD}/sabo_kaiso.png")
    im = Image.new("RGB", (560, 200), (170, 24, 22))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, 553, 193], radius=22, outline=(246, 238, 220), width=8)
    d.text((280, 100), "試運転", font=font("Sans", "Black", 100), fill=(250, 244, 230), anchor="mm")
    age(im, rust=0.1, seed=10).save(f"{OUTD}/sabo_shiunten.png")


DEST = {
    "jnr_dc": ["各駅停車　国都中央", "普通　穂波野", "普通　川原", "回送", "試運転"],
    "jnr_sub": ["近郊　新田橋", "普通　みずほ", "快速　国都中央", "普通　穂波野"],
    "jnr_exp": ["急行　北浦", "急行　大湊", "臨時急行　湯の里", "急行　国都中央"],
    "jnr_ltd": ["特急　大湊", "特急　国都中央", "特急　北浦", "臨時特急　穂波空港"],
    "jnr_ac": ["空港アクセス　穂波空港", "快速　新都中央", "普通　穂波新都", "空港　穂波空港"],
    "ke": ["特急　国都中央", "急行　新田橋", "普通　川原", "普通　国都中央"],
    "km": ["国都中央", "港町", "地下鉄　各駅停車", "回送"],
}
FRONT_STYLE = {   # 方向幕の書体・配色(形式ごとに違える)
    "jnr_dc": ("Sans", "Black", (14, 14, 16), (244, 244, 236)),
    "jnr_sub": ("Serif", "Black", (18, 30, 22), (244, 236, 200)),
    "jnr_exp": ("Sans", "Bold", (120, 14, 12), (250, 244, 232)),
    "jnr_ltd": ("Serif", "Bold", (12, 12, 18), (240, 214, 120)),
    "jnr_ac": ("Sans", "Medium", (8, 40, 86), (246, 246, 244)),
    "ke": ("Serif", "Black", (70, 8, 10), (236, 214, 150)),
    "km": ("Sans", "Black", (6, 6, 8), (250, 250, 250)),
}


def dest_rolls(tid):
    k, wgt, bg, fg = FRONT_STYLE[tid]
    items = DEST[tid]
    W, H = 1024, 192
    im = Image.new("RGB", (W, H * len(items)), bg)
    d = ImageDraw.Draw(im)
    for i, t in enumerate(items):
        y = i * H
        d.rectangle([0, y, W - 1, y + H - 1], outline=fg, width=6)
        d.text((W // 2, y + H // 2), t, font=font(k, wgt, 108), fill=fg, anchor="mm")
        d.line([24, y + H - 18, W - 24, y + H - 18], fill=fg, width=3)
    im = age(im, rust=0.0, yellow=0.1, seed=sum(map(ord, tid)) % 99)
    im.save(f"{OUTD}/dest_{tid}.png")
    for i in range(len(items)):
        im.crop((0, i * H, W, (i + 1) * H)).save(f"{OUTD}/dest_{tid}_{i}.png")


SABO = {"jnr_dc": ("各駅停車　国都中央", (250, 250, 244), (20, 20, 20)), "jnr_sub": ("近郊　新田橋", (250, 250, 244), (14, 60, 30)),
        "jnr_exp": ("急行　北浦", (250, 244, 232), (150, 20, 16)), "jnr_ltd": ("特急", (250, 250, 244), (150, 20, 16)),
        "jnr_ac": ("空港　穂波空港", (250, 250, 244), (10, 50, 100)), "ke": ("急行　新田橋", (240, 226, 170), (100, 12, 16)),
        "km": ("各駅停車", (250, 250, 244), (20, 20, 20))}


def sabo(tid):
    """行先板(サボ): 琺瑯引きの角丸板に行先を書き込んだもの。"""
    t, bg, fg = SABO[tid]
    W, H = 520, 200
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, W - 7, H - 7], radius=22, outline=fg, width=8)
    f = font("Sans", "Black", 62 if len(t) <= 6 else 50)
    d.text((W // 2, H // 2 - 4), t, font=f, fill=fg, anchor="mm")
    for xx in (28, W - 28):
        for yy in (28, H - 28):
            d.ellipse([xx - 5, yy - 5, xx + 5, yy + 5], fill=fg)
    age(im, rust=0.2, yellow=0.1, seed=sum(map(ord, tid)) % 77).save(f"{OUTD}/sabo_{tid}.png")


def num_plate(tid, label):
    W, H = 360, 100
    bg = {"jnr_dc": (24, 24, 26), "jnr_sub": (20, 40, 28), "jnr_exp": (90, 14, 12), "jnr_ltd": (18, 18, 24),
          "jnr_ac": (14, 40, 84), "ke": (70, 10, 12), "km": (30, 30, 34)}[tid]
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([3, 3, W - 4, H - 4], radius=10, outline=(230, 222, 196), width=3)
    d.text((W // 2, H // 2 + 2), label, font=font("Sans", "Bold", 62), fill=(236, 230, 206), anchor="mm")
    age(im, rust=0.1, seed=5).save(f"{OUTD}/num_{tid}.png")


def car_ad(i):
    """中吊り広告(原作オリジナル)。"""
    W, H = 600, 420
    pal = [((246, 226, 120), (160, 20, 20)), ((200, 230, 244), (10, 60, 120)), ((240, 214, 214), (110, 14, 30)),
           ((222, 240, 210), (20, 90, 40)), ((250, 244, 224), (60, 40, 20)), ((30, 30, 50), (240, 210, 90))]
    bg, fg = pal[i % len(pal)]
    t = [("穂波の湯", "旅の疲れに　湯の里温泉"), ("みずほ米", "新米入荷　国都米穀"), ("国都百貨店", "夏の大売出し　屋上遊園"),
         ("安全運転", "駆け込み乗車は おやめください"), ("港まつり", "大湊港　花火大会"), ("活動写真", "国都座　封切")][i % 6]
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, W - 11, H - 11], outline=fg, width=5)
    d.text((W // 2, 140), t[0], font=font("Serif", "Black", 96), fill=fg, anchor="mm")
    d.line([60, 215, W - 60, 215], fill=fg, width=4)
    d.text((W // 2, 290), t[1], font=font("Sans", "Bold", 40), fill=fg, anchor="mm")
    for k in range(6):
        d.ellipse([60 + k * 90, 345, 100 + k * 90, 385], fill=fg)
    age(im, rust=0.0, yellow=0.25, seed=40 + i).save(f"{OUTD}/car_ad_{i}.png")


def line_map(tid, stops, title, col):
    W, H = 900, 200
    im = Image.new("RGB", (W, H), (246, 244, 236))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 46], fill=col)
    d.text((24, 24), title, font=font("Sans", "Bold", 30), fill=(250, 250, 250), anchor="lm")
    n = len(stops)
    for i, nm in enumerate(stops):
        x = 60 + i * (W - 120) / (n - 1)
        if i:
            d.line([60 + (i - 1) * (W - 120) / (n - 1), 118, x, 118], fill=col, width=10)
        d.ellipse([x - 14, 104, x + 14, 132], fill=(250, 250, 250), outline=col, width=6)
        d.text((x, 160), nm, font=font("Sans", "Medium", 26), fill=(30, 30, 30), anchor="mm")
    age(im, rust=0.0, yellow=0.2, seed=60).save(f"{OUTD}/linemap_{tid}.png")


if __name__ == "__main__":
    for c in CO:
        logo(c)
    for h in HM:
        headmark_train(h)
    plate_kaiso()
    for t in DEST:
        dest_rolls(t)
    for t, lb in (("jnr_dc", "クハ 103-24"), ("jnr_sub", "モハ 113-8"), ("jnr_exp", "モハ 165-12"), ("jnr_ltd", "クハ 181-3"),
                  ("jnr_ac", "クモハ 401-5"), ("ke", "デハ 3012"), ("km", "1056")):
        num_plate(t, lb)
    for t_ in SABO:
        sabo(t_)
    for i in range(6):
        car_ad(i)
    line_map("km", ["国都中央", "新橋", "港町", "大手", "終点"], "国都地下鉄", (190, 20, 30))
    line_map("ke", ["国都中央", "新田橋", "川原", "みずほ"], "国都電鉄", (110, 14, 20))
    line_map("jnr", ["国都中央", "川原", "みずほ", "穂波野", "北浦"], "国鉄 幹線", (0, 70, 140))
    print("done")
