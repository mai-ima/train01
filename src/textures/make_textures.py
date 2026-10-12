import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Generate sign / poster textures for the fictional rural station (Honamino).
Everything here is original artwork; no real logos or brands.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

OUT = f"{_R}/tex"
os.makedirs(OUT, exist_ok=True)
FD = "/usr/share/fonts/opentype/noto/"


def find_jp(weight):
    path = FD + f"NotoSansCJK-{weight}.ttc"
    for idx in range(6):
        try:
            f = ImageFont.truetype(path, 40, index=idx)
        except Exception:
            break
        if "JP" in " ".join(f.getname()):
            return path, idx
    return path, 0


def font(weight, size):
    p, i = find_jp(weight)
    return ImageFont.truetype(p, size, index=i)


def center_text(d, xy, text, f, fill, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


# ---------------------------------------------------------------- station name plate (ekimei-hyo)
def ekimei():
    W, H = 2400, 800
    im = Image.new("RGB", (W, H), (244, 244, 240))
    d = ImageDraw.Draw(im)
    # outer frame + colour band
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 40, 40), width=14)
    d.rectangle([14, 14, W - 15, 150], fill=(32, 120, 78))
    center_text(d, (W // 2, 82), "ほなみの", font("Bold", 96), (255, 255, 255))
    # big kanji
    center_text(d, (W // 2, 345), "穂波野", font("Black", 250), (20, 20, 20))
    center_text(d, (W // 2, 545), "Honamino", font("Medium", 84), (30, 30, 30))
    # neighbours
    d.line([40, 610, W - 40, 610], fill=(32, 120, 78), width=6)
    f_small = font("Medium", 60)
    f_tiny = font("Regular", 36)
    center_text(d, (330, 672), "◀  みずほ", f_small, (20, 20, 20))
    center_text(d, (330, 728), "Mizuho", f_tiny, (60, 60, 60))
    center_text(d, (W - 330, 672), "かやま  ▶", f_small, (20, 20, 20))
    center_text(d, (W - 330, 728), "Kayama", f_tiny, (60, 60, 60))
    center_text(d, (W // 2, 690), "No.07", font("Bold", 54), (32, 120, 78))
    im.save(f"{OUT}/ekimei.png")


# ---------------------------------------------------------------- building facade board
def facade_board():
    W, H = 1600, 420
    im = Image.new("RGB", (W, H), (236, 232, 220))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(70, 52, 38), width=18)
    center_text(d, (W // 2, H // 2 + 6), "穂波野駅", font("Black", 250), (22, 22, 22))
    im.save(f"{OUT}/facade_board.png")


# ---------------------------------------------------------------- timetable
def timetable():
    random.seed(7)
    W, H = 1100, 1500
    im = Image.new("RGB", (W, H), (250, 250, 246))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30), width=8)
    d.rectangle([8, 8, W - 9, 150], fill=(32, 120, 78))
    center_text(d, (W // 2, 80), "時刻表  穂波野", font("Bold", 84), (255, 255, 255))
    f_h = font("Bold", 48)
    f_m = font("Regular", 40)
    d.text((40, 175), "かやま方面", font=f_h, fill=(20, 20, 20))
    d.text((W // 2 + 30, 175), "みずほ方面", font=f_h, fill=(20, 20, 20))
    y0 = 250
    row = 62
    hours = list(range(5, 24))
    for k, h in enumerate(hours):
        y = y0 + k * row
        if k % 2 == 0:
            d.rectangle([12, y - 4, W - 13, y + row - 8], fill=(238, 240, 234))
        d.text((60, y), f"{h:2d}", font=f_h, fill=(20, 20, 20))
        d.text((W // 2 + 40, y), f"{h:2d}", font=f_h, fill=(20, 20, 20))
        for col in range(2):
            n = random.choice([0, 1, 1, 2]) if 6 <= h <= 21 else random.choice([0, 1])
            mins = sorted(random.sample(range(0, 60, 3), n))
            txt = " ".join(f"{m:02d}" for m in mins)
            x = 160 + col * (W // 2)
            d.text((x, y + 4), txt, font=f_m, fill=(40, 40, 40))
    d.line([W // 2 - 4, 170, W // 2 - 4, H - 40], fill=(30, 30, 30), width=5)
    center_text(d, (W // 2, H - 28), "※ワンマン運転・全列車各駅に停車", font("Regular", 30), (60, 60, 60))
    im.save(f"{OUT}/timetable.png")


# ---------------------------------------------------------------- posters
def poster(name, bg, title, sub, accent, size=(700, 990)):
    W, H = size
    im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(255, 255, 255), width=10)
    d.rectangle([0, 0, W, 230], fill=accent)
    center_text(d, (W // 2, 118), title, font("Black", 92), (255, 255, 255))
    # abstract illustration: sun, hills, paddy stripes
    d.ellipse([W // 2 - 130, 330, W // 2 + 130, 590], fill=(255, 214, 120))
    for i, c in enumerate([(70, 140, 90), (96, 170, 110), (130, 196, 120)]):
        d.polygon([(0, 690 + i * 70), (W * 0.35, 560 + i * 70), (W * 0.7, 700 + i * 70),
                   (W, 600 + i * 70), (W, H), (0, H)], fill=c)
    center_text(d, (W // 2, 780), sub, font("Bold", 54), (255, 255, 255))
    center_text(d, (W // 2, 880), "お問い合わせは町役場まで", font("Medium", 36), (255, 255, 255))
    im.save(f"{OUT}/{name}.png")


def safety_poster():
    W, H = 700, 990
    im = Image.new("RGB", (W, H), (255, 224, 70))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30), width=12)
    center_text(d, (W // 2, 150), "ご注意", font("Black", 130), (200, 30, 30))
    center_text(d, (W // 2, 330), "踏切では", font("Black", 100), (25, 25, 25))
    center_text(d, (W // 2, 450), "一旦停止", font("Black", 130), (25, 25, 25))
    center_text(d, (W // 2, 620), "左右の確認", font("Bold", 90), (25, 25, 25))
    d.polygon([(W // 2, 700), (W // 2 - 130, 930), (W // 2 + 130, 930)], outline=(200, 30, 30), width=14)
    center_text(d, (W // 2, 850), "！", font("Black", 130), (200, 30, 30))
    im.save(f"{OUT}/safety.png")


# ---------------------------------------------------------------- vending machine front (generic drinks)
def vending():
    W, H = 900, 1800
    im = Image.new("RGB", (W, H), (200, 40, 36))
    d = ImageDraw.Draw(im)
    # window area
    d.rectangle([60, 120, W - 60, 1130], fill=(236, 236, 232))
    random.seed(3)
    palette = [(60, 140, 220), (240, 240, 240), (235, 160, 40), (60, 170, 90), (150, 60, 50),
               (230, 80, 120), (40, 40, 40), (230, 200, 60), (120, 90, 190), (255, 120, 40)]
    cols, rows = 6, 3
    cw = (W - 120) // cols
    rh = (1130 - 120) // rows
    for r in range(rows):
        for c in range(cols):
            x = 60 + c * cw
            y = 120 + r * rh
            col = random.choice(palette)
            bw = cw - 40
            if (r + c) % 3 == 0:  # bottle
                d.rounded_rectangle([x + 20 + bw * 0.22, y + 30, x + 20 + bw * 0.78, y + rh - 110], radius=18, fill=col)
                d.rectangle([x + 20 + bw * 0.4, y + 8, x + 20 + bw * 0.6, y + 40], fill=col)
            else:  # can
                d.rounded_rectangle([x + 20 + bw * 0.18, y + 90, x + 20 + bw * 0.82, y + rh - 110], radius=10, fill=col)
            d.rectangle([x + 20, y + rh - 90, x + cw - 20, y + rh - 40], fill=(255, 255, 255))
            d.text((x + cw // 2, y + rh - 65), f"{random.choice([110, 130, 150, 160])}", font=font("Bold", 34),
                   fill=(180, 30, 30), anchor="mm")
            d.line([x, y + rh - 4, x + cw, y + rh - 4], fill=(180, 180, 176), width=4)
    center_text(d, (W // 2, 62), "つめた〜い  あったか〜い", font("Black", 50), (255, 255, 255))
    # coin slot / buttons area
    d.rectangle([60, 1170, W - 60, 1740], fill=(176, 30, 28))
    d.rectangle([110, 1210, 420, 1310], fill=(30, 30, 30))
    d.text((265, 1260), "130", font=font("Bold", 70), fill=(255, 80, 60), anchor="mm")
    d.rectangle([470, 1210, 790, 1500], fill=(120, 20, 18))
    for i in range(3):
        d.ellipse([500 + i * 100, 1250, 570 + i * 100, 1320], fill=(240, 240, 240))
    d.rectangle([150, 1560, W - 150, 1710], fill=(20, 20, 20))
    im.save(f"{OUT}/vending.png")


# ---------------------------------------------------------------- stop sign (止まれ) with alpha
def tomare():
    S = 600
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(20, 80), (S - 20, 80), (S // 2, S - 40)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    inner = [(70, 106), (S - 70, 106), (S // 2, S - 112)]
    # red triangle with white border
    d.polygon([(40, 92), (S - 40, 92), (S // 2, S - 76)], fill=(200, 24, 28, 255))
    d.polygon([(110, 150), (S - 110, 150), (S // 2, S - 190)], outline=None)
    center_text(d, (S // 2, 230), "止まれ", font("Black", 100), (255, 255, 255, 255))
    im.save(f"{OUT}/tomare.png")


# ---------------------------------------------------------------- crossing sign (fumikiri ari) - yellow diamond
def crossing_sign():
    S = 600
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(S // 2, 10), (S - 10, S // 2), (S // 2, S - 10), (10, S // 2)], fill=(20, 20, 20, 255))
    d.polygon([(S // 2, 40), (S - 40, S // 2), (S // 2, S - 40), (40, S // 2)], fill=(250, 210, 40, 255))
    # simple train symbol
    d.rounded_rectangle([190, 220, 410, 370], radius=18, fill=(20, 20, 20, 255))
    d.rectangle([215, 245, 270, 300], fill=(250, 210, 40, 255))
    d.rectangle([330, 245, 385, 300], fill=(250, 210, 40, 255))
    d.ellipse([220, 350, 260, 390], fill=(20, 20, 20, 255))
    d.ellipse([340, 350, 380, 390], fill=(20, 20, 20, 255))
    im.save(f"{OUT}/crossing_sign.png")


# ---------------------------------------------------------------- plain wooden notice board (kenji-ban)
def notice():
    W, H = 900, 700
    im = Image.new("RGB", (W, H), (226, 220, 200))
    d = ImageDraw.Draw(im)
    random.seed(11)
    # pinned paper sheets
    sheets = [(40, 40, 300, 330, (250, 250, 248)), (330, 60, 590, 360, (255, 244, 200)),
              (620, 40, 860, 300, (225, 240, 250)), (60, 370, 340, 660, (250, 230, 230)),
              (380, 400, 640, 660, (250, 250, 248)), (680, 340, 860, 640, (236, 246, 232))]
    for x0, y0, x1, y1, c in sheets:
        d.rectangle([x0, y0, x1, y1], fill=c, outline=(150, 150, 150))
        for k in range(int((y1 - y0 - 80) / 26)):
            w = random.randint(int((x1 - x0) * 0.4), int((x1 - x0) * 0.85))
            d.rectangle([x0 + 18, y0 + 60 + k * 26, x0 + 18 + w, y0 + 70 + k * 26], fill=(110, 110, 110))
        d.rectangle([x0 + 18, y0 + 16, x1 - 18, y0 + 44], fill=(60, 60, 60))
        d.ellipse([(x0 + x1) // 2 - 6, y0 - 4, (x0 + x1) // 2 + 6, y0 + 8], fill=(200, 40, 40))
    im.save(f"{OUT}/notice.png")


if __name__ == "__main__":
    ekimei()
    facade_board()
    timetable()
    poster("poster_festival", (232, 120, 60), "秋まつり", "10月第3日曜", (170, 40, 40))
    poster("poster_tour", (56, 120, 170), "ほたる観賞", "6月上旬 川沿い", (30, 80, 120))
    safety_poster()
    vending()
    tomare()
    crossing_sign()
    notice()
    print(sorted(os.listdir(OUT)))
