"""Showa / national-railway-era signboards for the fictional Honamino station.
All artwork is original: invented town, invented advertisers, no real logos or marks.
"""
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = "/home/claude/station/tex"
FD = "/usr/share/fonts/opentype/noto/"
random.seed(21)
np.random.seed(21)


def _idx(path):
    for i in range(6):
        try:
            if "JP" in " ".join(ImageFont.truetype(path, 30, index=i).getname()):
                return i
        except Exception:
            break
    return 0


def font(kind, weight, size):
    path = FD + f"Noto{kind}CJK-{weight}.ttc"
    return ImageFont.truetype(path, size, index=_idx(path))


SANS = lambda w, s: font("Sans", w, s)
SERIF = lambda w, s: font("Serif", w, s)


def text(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def noise_layer(size, scale, seed=0):
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, size[1] // scale), max(2, size[0] // scale))).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize(size, Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255.0


def age(im, rust=0.5, chips=True, yellow=0.0, seed=0, fade=0.0):
    """Weathering: grime blotches, rust-brown speckles at edges, enamel chips, fading, yellowing."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    big = noise_layer((w, h), 90, seed)
    mid = noise_layer((w, h), 18, seed + 1)
    grime = np.clip((big - 0.45) * 2.0, 0, 1) * 0.22 + np.clip((mid - 0.6) * 2.5, 0, 1) * 0.14
    a *= (1.0 - grime[..., None] * np.array([0.55, 0.62, 0.75])[None, None, :])
    # edge rust / chipped enamel
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    edge = np.clip(1.0 - edge / (0.06 * min(w, h)), 0, 1)
    sp = noise_layer((w, h), 5, seed + 2)
    rustmask = np.clip((sp - 0.55) * 4.0, 0, 1) * (edge * 1.4 + 0.12) * rust
    rcol = np.array([0.36, 0.17, 0.08])[None, None, :]
    a = a * (1 - rustmask[..., None]) + rcol * rustmask[..., None]
    if chips:
        chip = (noise_layer((w, h), 3, seed + 3) > 0.93) & (edge > 0.2)
        a[chip] = np.array([0.15, 0.1, 0.07])
    if yellow > 0:
        a = a * (1 - yellow) + a * np.array([1.0, 0.92, 0.72])[None, None, :] * yellow
    if fade > 0:
        a = a * (1 - fade) + a.mean(axis=2, keepdims=True) * fade
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- station name plate (enamel)
def ekimei():
    W, H = 2400, 800
    im = Image.new("RGB", (W, H), (238, 237, 230))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(18, 18, 18), width=22)
    d.rectangle([40, 40, W - 41, H - 41], outline=(18, 18, 18), width=5)
    text(d, (W // 2, 140), "ほなみの", SANS("Bold", 112), (18, 18, 18))
    text(d, (W // 2, 400), "穂 波 野", SERIF("Black", 270), (14, 14, 14))
    d.line([90, 600, W - 90, 600], fill=(18, 18, 18), width=6)
    text(d, (330, 690), "◀ みずほ", SANS("Bold", 78), (18, 18, 18))
    text(d, (W - 330, 690), "かやま ▶", SANS("Bold", 78), (18, 18, 18))
    text(d, (W // 2, 690), "Honamino", SANS("Medium", 54), (40, 40, 40))
    age(im, rust=0.9, yellow=0.12, seed=3).save(f"{OUT}/ekimei_old.png")


# ---------------------------------------------------------------- building name board (painted wood)
def facade_board():
    W, H = 1800, 480
    base = Image.new("RGB", (W, H), (30, 24, 20))
    d = ImageDraw.Draw(base)
    text(d, (W // 2, H // 2 + 6), "穂波野駅", SERIF("Black", 300), (232, 226, 210))
    a = np.asarray(base).astype(np.float32) / 255.0
    paint_wear = np.clip((noise_layer((W, H), 14, 5) - 0.55) * 3.0, 0, 1)
    wood = np.array([0.20, 0.15, 0.11])[None, None, :]
    mask = (a.mean(axis=2) > 0.5)
    a[mask] = a[mask] * (1 - paint_wear[mask][:, None] * 0.75) + wood[0, 0] * paint_wear[mask][:, None] * 0.75
    grain = noise_layer((W, H), 3, 8)[..., None] * 0.10
    a = np.clip(a * (0.92 + grain), 0, 1)
    age(Image.fromarray((a * 255).astype(np.uint8)), rust=0.0, chips=False, seed=7).save(f"{OUT}/facade_board_old.png")


# ---------------------------------------------------------------- fare table
def fare_board():
    W, H = 1100, 800
    im = Image.new("RGB", (W, H), (232, 224, 200))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 30, 22), width=14)
    text(d, (W // 2, 90), "運  賃  表", SERIF("Black", 84), (24, 20, 16))
    rows = [("みずほ", 40, 20), ("かやま", 60, 30), ("青 柳", 90, 50), ("中 津", 130, 70),
            ("城 下", 180, 90), ("大 津 口", 250, 130)]
    y0 = 170
    d.line([40, y0 - 14, W - 40, y0 - 14], fill=(24, 20, 16), width=5)
    text(d, (220, y0 + 25), "駅 名", SANS("Bold", 46), (24, 20, 16))
    text(d, (690, y0 + 25), "大人", SANS("Bold", 46), (24, 20, 16))
    text(d, (930, y0 + 25), "小児", SANS("Bold", 46), (24, 20, 16))
    for k, (n, a, c) in enumerate(rows):
        y = y0 + 80 + k * 86
        d.line([40, y - 10, W - 40, y - 10], fill=(70, 60, 50), width=2)
        text(d, (220, y + 32), n, SANS("Medium", 56), (24, 20, 16))
        text(d, (690, y + 32), f"{a}円", SANS("Medium", 56), (24, 20, 16))
        text(d, (930, y + 32), f"{c}円", SANS("Medium", 56), (24, 20, 16))
    age(im, rust=0.0, chips=False, yellow=0.4, seed=12).save(f"{OUT}/fare_board.png")


# ---------------------------------------------------------------- timetable (few trains a day)
def timetable():
    W, H = 900, 1200
    im = Image.new("RGB", (W, H), (238, 236, 226))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(20, 20, 20), width=12)
    text(d, (W // 2, 90), "列 車 時 刻 表", SERIF("Black", 70), (20, 20, 20))
    text(d, (W // 2, 160), "穂 波 野", SANS("Bold", 52), (20, 20, 20))
    up = ["6:12", "7:48", "9:30", "12:05", "14:20", "16:35", "18:02", "20:15"]
    dn = ["6:40", "8:25", "10:10", "12:50", "15:05", "17:20", "19:08", "21:30"]
    text(d, (W // 4, 240), "かやま 方面", SANS("Bold", 48), (20, 20, 20))
    text(d, (3 * W // 4, 240), "みずほ 方面", SANS("Bold", 48), (20, 20, 20))
    d.line([W // 2, 210, W // 2, H - 60], fill=(20, 20, 20), width=5)
    d.line([30, 280, W - 30, 280], fill=(20, 20, 20), width=4)
    for k, (a, b) in enumerate(zip(up, dn)):
        y = 345 + k * 100
        text(d, (W // 4, y), a, SANS("Medium", 62), (24, 24, 24))
        text(d, (3 * W // 4, y), b, SANS("Medium", 62), (24, 24, 24))
        d.line([30, y + 48, W - 30, y + 48], fill=(150, 150, 140), width=2)
    text(d, (W // 2, H - 32), "※ 運転日にご注意ください", SANS("Regular", 30), (60, 60, 60))
    age(im, rust=0.0, chips=False, yellow=0.3, seed=15).save(f"{OUT}/timetable_old.png")


# ---------------------------------------------------------------- enamel adverts (invented)
def ad(name, size, bg, fg, lines, accent=None, border=None):
    W, H = size
    im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    bc = border or fg
    d.rectangle([0, 0, W - 1, H - 1], outline=bc, width=16)
    d.rectangle([30, 30, W - 31, H - 31], outline=bc, width=4)
    n = len(lines)
    for k, (s, sz, kind) in enumerate(lines):
        y = int(H * (k + 1) / (n + 1))
        f = SERIF("Black", sz) if kind == "serif" else SANS("Black", sz)
        text(d, (W // 2, y), s, f, fg)
    if accent:
        d.ellipse([W - 190, 50, W - 50, 190], fill=accent)
    return im


def adverts():
    a = ad("onsen", (700, 1000), (178, 52, 36), (250, 240, 220),
           [("みずほ", 120, "serif"), ("温 泉", 190, "serif"), ("♨", 150, "sans"), ("湯の里まで 6粁", 70, "sans")])
    age(a, rust=1.0, yellow=0.1, seed=21).save(f"{OUT}/ad_onsen.png")
    b = ad("nokyo", (1000, 420), (28, 70, 140), (250, 248, 240),
           [("穂波野農協", 120, "sans"), ("米・肥料・農機具", 78, "sans")])
    age(b, rust=1.0, yellow=0.05, seed=22).save(f"{OUT}/ad_nokyo.png")
    c = ad("fire", (420, 900), (236, 236, 228), (200, 24, 28),
           [("火", 220, "serif"), ("の", 160, "serif"), ("用", 220, "serif"), ("心", 220, "serif")], border=(200, 24, 28))
    age(c, rust=1.0, yellow=0.1, seed=23).save(f"{OUT}/ad_fire.png")
    d_ = ad("safety", (900, 330), (244, 200, 40), (24, 24, 24),
            [("交 通 安 全", 150, "sans"), ("ゆずりあい　まごころ", 60, "sans")])
    age(d_, rust=1.0, yellow=0.05, seed=24).save(f"{OUT}/ad_safety.png")


# ---------------------------------------------------------------- "tomare-miyo-kike" crossing plate
def fumikiri():
    W, H = 800, 560
    im = Image.new("RGB", (W, H), (240, 238, 228))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(18, 18, 18), width=16)
    text(d, (W // 2, 150), "ふみきり", SANS("Black", 130), (18, 18, 18))
    text(d, (W // 2, 330), "とまれ", SANS("Black", 120), (190, 24, 28))
    text(d, (W // 2, 460), "みよ ・ きけ", SANS("Black", 84), (18, 18, 18))
    age(im, rust=1.0, yellow=0.1, seed=31).save(f"{OUT}/fumikiri_plate.png")


# ---------------------------------------------------------------- railcar destination plate / number
def sabo():
    W, H = 900, 300
    im = Image.new("RGB", (W, H), (236, 234, 224))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(20, 20, 20), width=12)
    text(d, (W // 2, 105), "穂波野 ─ かやま", SANS("Black", 100), (20, 20, 20))
    text(d, (W // 2, 225), "普 通", SANS("Bold", 76), (190, 24, 28))
    age(im, rust=0.6, yellow=0.2, seed=41).save(f"{OUT}/sabo.png")
    W, H = 600, 200
    im = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(im)
    text(d, (W // 2, H // 2), "キハ 5 2 5", SANS("Bold", 100), (236, 232, 220))
    age(im, rust=0.0, chips=False, seed=42).save(f"{OUT}/kiha_number.png")


# ---------------------------------------------------------------- wall clock face (round, alpha)
def clock():
    S = 800
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, S - 10, S - 10], fill=(34, 26, 20, 255))
    d.ellipse([60, 60, S - 60, S - 60], fill=(238, 232, 214, 255))
    import math
    for k in range(60):
        t = math.radians(k * 6)
        r0 = S / 2 - 90
        r1 = S / 2 - (130 if k % 5 == 0 else 110)
        c = S / 2
        d.line([c + r0 * math.sin(t), c - r0 * math.cos(t), c + r1 * math.sin(t), c - r1 * math.cos(t)],
               fill=(20, 20, 20, 255), width=8 if k % 5 == 0 else 3)
    for n in range(1, 13):
        t = math.radians(n * 30)
        rr = S / 2 - 190
        text(d, (S / 2 + rr * math.sin(t), S / 2 - rr * math.cos(t)), str(n), SERIF("Bold", 78), (20, 20, 20))
    # hands: 2:40
    c = S / 2
    th = math.radians(2 * 30 + 40 * 0.5)
    tm = math.radians(40 * 6)
    d.line([c, c, c + 190 * math.sin(th), c - 190 * math.cos(th)], fill=(15, 15, 15, 255), width=18)
    d.line([c, c, c + 280 * math.sin(tm), c - 280 * math.cos(tm)], fill=(15, 15, 15, 255), width=11)
    d.ellipse([c - 16, c - 16, c + 16, c + 16], fill=(15, 15, 15, 255))
    im.save(f"{OUT}/clock.png")


# ---------------------------------------------------------------- posters / notices
def old_poster(name, title, sub, bg, accent, size=(700, 990), seed=50):
    W, H = size
    im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 30, 24), width=10)
    d.rectangle([40, 40, W - 41, 260], fill=accent)
    text(d, (W // 2, 150), title, SERIF("Black", 104), (250, 244, 228))
    for i, c in enumerate([(120, 96, 52), (150, 120, 60), (184, 150, 76)]):
        d.polygon([(0, 640 + i * 60), (W * 0.3, 500 + i * 60), (W * 0.6, 650 + i * 60),
                   (W, 540 + i * 60), (W, H), (0, H)], fill=c)
    d.ellipse([W - 250, 320, W - 90, 480], fill=(224, 120, 40))
    text(d, (W // 2, 800), sub, SANS("Bold", 54), (250, 244, 228))
    text(d, (W // 2, 900), "穂波野 観光協会", SANS("Medium", 36), (250, 244, 228))
    age(im, rust=0.0, chips=False, yellow=0.45, seed=seed, fade=0.15).save(f"{OUT}/{name}.png")


def ricebag():
    W, H = 600, 900
    im = Image.new("RGB", (W, H), (214, 190, 140))
    d = ImageDraw.Draw(im)
    for k in range(0, H, 14):
        d.line([0, k, W, k], fill=(200, 175, 125), width=2)
    text(d, (W // 2, 270), "穂波野米", SERIF("Black", 130), (150, 20, 20))
    d.rectangle([120, 400, W - 120, 560], outline=(150, 20, 20), width=10)
    text(d, (W // 2, 480), "一 等", SERIF("Black", 100), (150, 20, 20))
    text(d, (W // 2, 700), "三十瓩", SANS("Bold", 80), (40, 30, 24))
    age(im, rust=0.0, chips=False, yellow=0.3, seed=60).save(f"{OUT}/ricebag.png")


def ekimae():
    W, H = 900, 300
    im = Image.new("RGB", (W, H), (226, 220, 200))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 30, 22), width=12)
    text(d, (W // 2, H // 2), "駅前 旅館 みどり屋", SERIF("Black", 96), (24, 20, 16))
    age(im, rust=0.0, chips=False, yellow=0.4, seed=70).save(f"{OUT}/ekimae.png")


def poster_generic(name, size, bg, band, title, sub, art, seed, title_size=96, text_col=(250, 244, 228)):
    W, H = size
    im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 30, 24), width=10)
    d.rectangle([34, 34, W - 35, 250], fill=band)
    text(d, (W // 2, 142), title, SERIF("Black", title_size), text_col)
    art(d, W, H)
    text(d, (W // 2, H - 150), sub, SANS("Bold", 50), text_col)
    text(d, (W // 2, H - 70), "お問い合わせは役場まで", SANS("Medium", 32), text_col)
    age(im, rust=0.0, chips=False, yellow=0.4, seed=seed, fade=0.12).save(f"{OUT}/{name}.png")


def art_child(d, W, H):
    d.ellipse([W // 2 - 70, 330, W // 2 + 70, 470], fill=(250, 222, 180))
    d.polygon([(W // 2 - 100, 480), (W // 2 + 100, 480), (W // 2 + 130, 720), (W // 2 - 130, 720)], fill=(230, 190, 40))
    d.rectangle([W // 2 - 150, 740, W // 2 + 150, 760], fill=(240, 240, 240))
    for k in range(6):
        d.rectangle([W // 2 - 150 + k * 52, 740, W // 2 - 120 + k * 52, 760], fill=(30, 30, 30))


def art_map(d, W, H):
    pts = [(80, 520), (210, 470), (330, 520), (470, 440), (600, 480), (720, 400)]
    d.line(pts, fill=(30, 30, 30), width=10)
    for k, p in enumerate(pts):
        d.ellipse([p[0] - 18, p[1] - 18, p[0] + 18, p[1] + 18], fill=(250, 244, 228), outline=(30, 30, 30), width=6)
    names = ["みずほ", "穂波野", "かやま", "青柳", "中津", "城下"]
    for p, n in zip(pts, names):
        text(d, (p[0], p[1] + 60), n, SANS("Bold", 36), (30, 30, 30))
    d.ellipse([W // 2 - 26, 300 - 0, W // 2 + 26, 352], fill=(190, 40, 30))


def art_mountain(d, W, H):
    d.polygon([(0, 700), (W * 0.3, 380), (W * 0.55, 620), (W * 0.8, 340), (W, 650), (W, H), (0, H)], fill=(70, 100, 120))
    d.polygon([(0, 760), (W * 0.4, 560), (W * 0.7, 720), (W, 600), (W, H), (0, H)], fill=(40, 70, 60))
    d.ellipse([90, 300, 200, 410], fill=(250, 200, 90))
    d.rounded_rectangle([W // 2 - 190, 800, W // 2 + 190, 880], radius=16, fill=(30, 30, 30))
    d.rectangle([W // 2 - 170, 815, W // 2 + 170, 845], fill=(230, 190, 120))


def art_film(d, W, H):
    d.rectangle([60, 320, W - 60, 760], fill=(20, 20, 24))
    for k in range(10):
        d.rectangle([76, 335 + k * 43, 110, 360 + k * 43], fill=(240, 236, 220))
        d.rectangle([W - 110, 335 + k * 43, W - 76, 360 + k * 43], fill=(240, 236, 220))
    d.ellipse([W // 2 - 130, 420, W // 2 + 130, 680], fill=(230, 80, 40))
    d.polygon([(W // 2 - 40, 480), (W // 2 - 40, 620), (W // 2 + 80, 550)], fill=(250, 244, 228))


def art_leaf(d, W, H):
    for k, c in enumerate([(200, 60, 30), (230, 150, 30), (150, 40, 24), (220, 110, 30)]):
        cx, cy = 160 + k * 150, 460 + (k % 2) * 120
        d.polygon([(cx, cy - 90), (cx + 60, cy), (cx + 24, cy + 30), (cx, cy + 100), (cx - 24, cy + 30), (cx - 60, cy)], fill=c)


def art_coin(d, W, H):
    for k in range(4):
        d.ellipse([140 + k * 90, 520 - k * 36, 300 + k * 90, 680 - k * 36], fill=(236, 190, 60), outline=(120, 80, 20), width=8)
    d.rectangle([W // 2 - 140, 330, W // 2 + 140, 460], outline=(250, 244, 228), width=8)


def art_sumo(d, W, H):
    d.ellipse([W // 2 - 220, 380, W // 2 + 220, 780], outline=(250, 244, 228), width=12)
    d.ellipse([W // 2 - 40, 440, W // 2 + 40, 520], fill=(240, 200, 150))
    d.rounded_rectangle([W // 2 - 90, 520, W // 2 + 90, 680], radius=40, fill=(40, 60, 120))


def emblem():
    """Original emblem of the fictional 'Honami Railway Bureau': rice ears over two rails. Not based on any real mark."""
    import math
    S = 600
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, S - 10, S - 10], fill=(236, 230, 208, 255), outline=(30, 90, 60, 255), width=22)
    d.ellipse([70, 70, S - 70, S - 70], outline=(30, 90, 60, 255), width=8)
    # two rails
    for dx in (-52, 52):
        d.polygon([(S // 2 + dx - 14, 350), (S // 2 + dx + 14, 350), (S // 2 + dx + 24, 520), (S // 2 + dx - 24, 520)], fill=(30, 90, 60, 255))
    for k in range(4):
        y = 385 + k * 34
        d.rectangle([S // 2 - 120, y, S // 2 + 120, y + 12], fill=(30, 90, 60, 255))
    # rice ears
    for sgn in (-1, 1):
        for k in range(5):
            ang = math.radians(sgn * (12 + k * 9))
            cx = S // 2 + sgn * (26 + k * 14)
            cy = 300 - k * 34
            for j in range(4):
                gx = cx + sgn * j * 11 * math.cos(ang)
                gy = cy - j * 15
                d.ellipse([gx - 12, gy - 20, gx + 12, gy + 20], fill=(206, 150, 30, 255), outline=(120, 80, 10, 255), width=3)
    d.line([S // 2, 360, S // 2, 170], fill=(120, 80, 10, 255), width=10)
    im.save(f"{OUT}/emblem.png")


def more_posters():
    s = (600, 860)
    poster_generic("poster_safety", s, (236, 200, 50), (30, 30, 30), "とびだすな", "車は急に止まれない", art_child, 81, 92, (250, 244, 228))
    poster_generic("poster_map", (900, 640), (232, 222, 196), (40, 70, 110), "沿線案内図", "ご旅行は汽車で", art_map, 82, 80)
    poster_generic("poster_travel", s, (60, 100, 130), (180, 60, 40), "旅は汽車で", "秋の山里へ", art_mountain, 83, 96)
    poster_generic("poster_movie", s, (40, 36, 50), (190, 40, 30), "映画の夕べ", "公民館 午後六時", art_film, 84, 92)
    poster_generic("poster_leaf", s, (140, 60, 36), (80, 30, 20), "紅葉まつり", "十一月三日", art_leaf, 85, 96)
    poster_generic("poster_savings", s, (230, 220, 190), (60, 100, 70), "こつこつ貯金", "郵便局・農協", art_coin, 86, 70, (30, 30, 30))
    poster_generic("poster_sumo", s, (44, 70, 110), (220, 200, 90), "相撲大会", "神社境内　日曜", art_sumo, 87, 96, (24, 24, 30))


if __name__ == "__main__":
    emblem()
    more_posters()
    os.makedirs(OUT, exist_ok=True)
    ekimei(); facade_board(); fare_board(); timetable(); adverts(); fumikiri(); sabo(); clock()
    old_poster("poster_inaho", "稲穂まつり", "十月 第三日曜", (150, 52, 40), (110, 30, 24), seed=51)
    old_poster("poster_hike", "紅葉ハイキング", "歩こう会 参加者募集", (60, 98, 70), (34, 66, 48), seed=52)
    ricebag(); ekimae()
    print(sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
