"""Poster / signboard generator v2: every station gets its own palette, its own style mix (woodblock / enamel / watercolour / retro halftone / photo postcard / handwritten notice / newspaper / nobori),
its own motif set and copy. Original artwork only."""
import json, math, random, sys, os, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import make_textures2 as mt

NET = json.load(open("/home/claude/station/net/network.json"))
ST = {s["id"]: s for s in NET["stations"]}
IDX = {s["id"]: i for i, s in enumerate(NET["stations"])}
OUT = "/home/claude/station/tex/kit"
SANS, SERIF = mt.SANS, mt.SERIF
STYLES = ["woodblock", "enamel", "watercolor", "retro", "photo", "newspaper", "hand", "nobori"]
MOT = {"mountain": ["山", "峠", "高嶺", "高原", "岳"], "sea": ["港", "海", "浦", "汐", "湊", "灯台", "岬", "磯", "埠頭"], "onsen": ["湯", "温泉", "足湯"],
       "snow": ["雪", "スキー"], "farm": ["田", "畑", "栗", "野", "原", "みず", "稲"], "forest": ["杉", "森", "林"], "city": ["国都", "中央", "丸の内", "本町", "市役所", "新田橋"],
       "river": ["川", "橋", "滝", "渓"], "rail": ["穂波野", "貨物", "かやま", "山辺"]}


def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def pal(sid):
    i = IDX[sid]
    rng = random.Random(i * 53 + 5)
    # 昭和の印刷インキ風: 朱・藍・黄土・深緑・栗・鼠 から駅ごとに組み合わせを変える
    ink = [(0.02, 0.62, 0.62), (0.60, 0.55, 0.42), (0.11, 0.55, 0.72), (0.36, 0.45, 0.42), (0.05, 0.50, 0.45), (0.95, 0.42, 0.55), (0.52, 0.40, 0.52), (0.14, 0.60, 0.60)]
    p = rng.sample(ink, 3)
    j = rng.uniform(-0.02, 0.02)
    return dict(a=hsv(p[0][0] + j, p[0][1], p[0][2] * 0.85), b=hsv(p[1][0] + j, p[1][1] * 0.9, min(0.85, p[1][2] + 0.15)), c=hsv(p[2][0], p[2][1] * 0.45, 0.93),
                d=hsv(p[1][0], p[1][1] * 0.8, 0.30), paper=hsv(0.11 + 0.03 * ((i % 5) - 2) / 2, 0.08 + 0.03 * (i % 3), 0.92), ink=hsv(p[0][0], 0.35, 0.15))


def motifs(sid):
    st = ST[sid]
    txt = st["name"] + " ".join(st.get("town", []) + st.get("features", []))
    out = [k for k, ws in MOT.items() if any(w in txt for w in ws)]
    rng = random.Random(IDX[sid] * 7 + 3)
    base = ["mountain", "farm", "river", "city", "sea", "forest", "snow", "onsen"]
    while len(out) < 3:
        k = rng.choice(base)
        if k not in out:
            out.append(k)
    return out[:4]


def styles_for(sid):
    rng = random.Random(IDX[sid] * 131 + 17)
    s = STYLES[:]
    rng.shuffle(s)
    return s


def paper_tex(W, H, base, seed=0, fiber=0.05):
    rng = np.random.default_rng(seed)
    n = mt.noise_layer((W, H), 3, seed) * 0.5 + mt.noise_layer((W, H), 40, seed + 1) * 0.5
    a = np.ones((H, W, 3), np.float32) * np.array(base, np.float32) / 255.0
    a *= (1 - fiber + fiber * 2 * n[..., None])
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ------------------------------------------------------------ motif drawing
def m_mountain(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pts = [(x0, y1)]
    k = rng.randint(3, 5)
    for i in range(k + 1):
        pts.append((x0 + w * i / k, y1 - h * (0.35 + 0.55 * rng.random()) * (1 if 0 < i < k else 0.3)))
    pts.append((x1, y1))
    d.polygon(pts, fill=P["d"], outline=line)
    d.polygon([(x0, y1), (x0 + w * .3, y1 - h * .25), (x0 + w * .6, y1 - h * .12), (x1, y1)], fill=P["a"], outline=line)


def m_sun(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    r = min(x1 - x0, y1 - y0) * 0.16
    cx, cy = x0 + (x1 - x0) * rng.uniform(0.2, 0.8), y0 + (y1 - y0) * 0.22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P["b"], outline=line)


def m_sea(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y1 - h * .35, x1, y1], fill=P["a"])
    for k in range(7):
        yy = y1 - h * .33 + k * h * 0.045
        for xx in np.arange(x0, x1, 38):
            d.arc([xx, yy - 7, xx + 38, yy + 7], 200, 340, fill=P["c"], width=3)
    bx = x0 + w * rng.uniform(0.25, 0.6)
    by = y1 - h * .33
    d.polygon([(bx, by), (bx + w * .22, by), (bx + w * .17, by + h * .07), (bx + w * .04, by + h * .07)], fill=P["paper"], outline=line)
    d.polygon([(bx + w * .11, by), (bx + w * .11, by - h * .22), (bx + w * .2, by - .01 * h)], fill=P["c"], outline=line)


def m_tree(d, box, P, rng, line=None, n=7):
    x0, y0, x1, y1 = box
    for i in range(n):
        cx = x0 + (x1 - x0) * rng.random()
        hh = (y1 - y0) * rng.uniform(0.25, 0.55)
        ww = hh * 0.28
        by = y1 - rng.uniform(0, (y1 - y0) * 0.1)
        for j in range(3):
            d.polygon([(cx - ww * (1 - j * .15), by - hh * j * .28), (cx, by - hh * (j * .28 + .45)), (cx + ww * (1 - j * .15), by - hh * j * .28)], fill=P["d"] if i % 2 else P["a"], outline=line)


def m_house(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for i in range(rng.randint(2, 4)):
        bx = x0 + w * (0.1 + 0.8 * rng.random())
        bw, bh = w * 0.18, h * 0.16
        by = y1 - rng.uniform(0, h * 0.18)
        d.rectangle([bx, by - bh, bx + bw, by], fill=P["paper"], outline=line)
        d.polygon([(bx - bw * .12, by - bh), (bx + bw / 2, by - bh * 1.7), (bx + bw * 1.12, by - bh)], fill=P["ink"] if i % 2 else P["d"], outline=line)


def m_city(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for k in range(10):
        bw = w * 0.075
        bx = x0 + w * (0.04 + 0.095 * k)
        bh = h * (0.18 + 0.5 * rng.random())
        c = P["d"] if k % 2 else P["a"]
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=c, outline=line)
        for r_ in range(int(bh / 20)):
            d.rectangle([bx + 4, y1 - bh + 8 + r_ * 20, bx + bw - 4, y1 - bh + 15 + r_ * 20], fill=P["b"])


def m_snow(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    for i in range(18):
        cx, cy = x0 + (x1 - x0) * rng.random(), y0 + (y1 - y0) * rng.random() * 0.8
        r = rng.uniform(4, 12)
        for a in range(0, 180, 60):
            dx, dy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            d.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=P["paper"], width=2)


def m_onsen(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for k in range(4):
        cx = x0 + w * (0.25 + 0.17 * k)
        d.arc([cx - 18, y1 - h * .55, cx + 18, y1 - h * .32], 200, 340, fill=P["paper"], width=6)
        d.arc([cx - 12, y1 - h * .72, cx + 12, y1 - h * .5], 20, 160, fill=P["paper"], width=5)
    d.rectangle([x0 + w * .3, y1 - h * .28, x0 + w * .7, y1 - h * .06], fill=P["ink"], outline=line)
    d.polygon([(x0 + w * .26, y1 - h * .28), (x0 + w * .5, y1 - h * .42), (x0 + w * .74, y1 - h * .28)], fill=P["d"], outline=line)


def m_farm(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    h = y1 - y0
    for k in range(7):
        yy = y1 - h * (0.04 + 0.05 * k)
        d.rectangle([x0, yy - h * 0.035, x1, yy], fill=P["b"] if k % 2 else P["c"])


def m_river(d, box, P, rng, line=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pts = [(x0 + w * (0.4 + 0.15 * math.sin(i * 0.7)), y0 + h * i / 12) for i in range(13)]
    d.line(pts, fill=P["c"], width=int(w * 0.09), joint="curve")
    d.line([(x0, y1 - h * .25), (x1, y1 - h * .3)], fill=P["ink"], width=6)
    d.line([(x0, y1 - h * .32), (x1, y1 - h * .36)], fill=P["ink"], width=3)


MOTIF_FN = {"mountain": m_mountain, "sea": m_sea, "forest": m_tree, "farm": m_farm, "city": m_city, "snow": m_snow, "onsen": m_onsen, "river": m_river, "rail": m_house}


def scene(sid, size, P, rng, line=None):
    W, H = size
    im = Image.new("RGB", size, P["c"])
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        c = tuple(int(P["c"][i] * (1 - t * 0.35) + P["paper"][i] * t * 0.35) for i in range(3))
        d.line([0, y, W, y], fill=c)
    box = (0, 0, W, H)
    m_sun(d, box, P, rng, line)
    ms = motifs(sid)
    order = ["mountain", "sea", "city", "river", "farm", "onsen", "snow", "forest", "rail"]
    for k in sorted(ms, key=lambda x: order.index(x) if x in order else 9):
        MOTIF_FN[k](d, box, P, rng, line)
    m_house(d, box, P, rng, line) if "farm" in ms or "forest" in ms else None
    return im


# ------------------------------------------------------------ copy
SPOTS = {"onsen": ["湯けむり祭", "湯治割引", "足湯めぐり", "秘湯の宿"], "sea": ["朝市", "魚まつり", "遊覧船", "港まつり", "潮干狩り"], "snow": ["雪まつり", "スキー場開き", "かまくら", "樹氷ツアー"],
         "farm": ["新米まつり", "収穫祭", "栗拾い", "農協まつり"], "forest": ["森の木工市", "きのこ狩り", "林道ウォーク"], "mountain": ["峠の茶屋", "紅葉ハイク", "山開き", "星空観察"],
         "city": ["大売出し", "市民音楽祭", "名店街フェア", "ビヤホール開き"], "river": ["鮎まつり", "川開き", "花火大会"], "rail": ["鉄道まつり", "機関車まつり", "記念乗車券"]}


def copy(sid, k):
    rng = random.Random(IDX[sid] * 977 + k * 31)
    ms = motifs(sid)
    kind = ms[k % len(ms)]
    return rng.choice(SPOTS.get(kind, SPOTS["farm"]))


def tfit(d, s, kind, wt, maxw, size):
    while size > 14:
        f = (SANS if kind == "s" else SERIF)(wt, size)
        if d.textlength(s, font=f) <= maxw:
            return f
        size -= 2
    return (SANS if kind == "s" else SERIF)(wt, 14)


def stamp(d, xy, ch, P, r=46):
    x, y = xy
    d.rounded_rectangle([x - r, y - r, x + r, y + r], radius=8, outline=(180, 30, 30), width=5)
    d.text((x, y), ch, font=SERIF("Black", int(r * 1.3)), fill=(180, 30, 30), anchor="mm")


def halftone(im, strength=0.35, cell=7, seed=0):
    g = np.asarray(im.convert("L")).astype(np.float32) / 255
    H, W = g.shape
    yy, xx = np.mgrid[0:H, 0:W]
    ang = 0.6
    u = (xx * math.cos(ang) + yy * math.sin(ang)) / cell
    v = (-xx * math.sin(ang) + yy * math.cos(ang)) / cell
    pat = (np.cos(u * 2 * math.pi) * np.cos(v * 2 * math.pi) * 0.5 + 0.5)
    mask = (g * 0.9 + 0.05) > pat
    a = np.asarray(im).astype(np.float32)
    dark = a * 0.78
    out = np.where(mask[..., None], a, dark * (1 - strength) + a * strength)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------ styles
def st_woodblock(sid, k, P, rng, W=760, H=1080):
    st = ST[sid]
    im = paper_tex(W, H, P["paper"], seed=k)
    d = ImageDraw.Draw(im)
    art = scene(sid, (W - 120, int(H * 0.56)), P, rng, line=P["ink"])
    a = np.asarray(art).astype(np.float32)
    levels = 5
    a = (np.round(a / 255 * (levels - 1)) / (levels - 1) * 255)
    art = Image.fromarray(a.astype(np.uint8))
    im.paste(art, (60, 210))
    d.rectangle([60, 210, W - 61, 210 + art.height], outline=P["ink"], width=6)
    title = copy(sid, k)
    for i, ch in enumerate(title[:6]):
        d.text((W - 100, 270 + i * 96), ch, font=SERIF("Black", 90), fill=P["ink"], anchor="mm")
    d.rectangle([60, 40, W - 61, 170], fill=P["a"])
    d.text((W // 2, 105), st["name"] + " 名所案内", font=tfit(d, st["name"] + " 名所案内", "r", "Black", W - 160, 78), fill=P["paper"], anchor="mm")
    d.text((W // 2, 930), "国鉄 " + st["name"] + "駅下車", font=SERIF("Bold", 50), fill=P["ink"], anchor="mm")
    stamp(d, (W - 110, 990), st["name"][0], P)
    return mt.age(im, rust=0.1, chips=False, yellow=0.12, seed=k + IDX[sid])


def st_enamel(sid, k, P, rng, W=1100, H=520):
    st = ST[sid]
    im = Image.new("RGB", (W, H), P["paper"])
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, W - 9, H - 9], radius=40, outline=P["a"], width=26)
    d.rounded_rectangle([46, 46, W - 47, H - 47], radius=26, outline=P["a"], width=5)
    art = scene(sid, (360, H - 140), P, rng, line=None)
    mask = Image.new("L", art.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, art.width - 1, art.height - 1], radius=18, fill=255)
    im.paste(art, (80, 70), mask)
    title = copy(sid, k + 2)
    d.text((795, 190), title, font=tfit(d, title, "s", "Black", 470, 120), fill=P["a"], anchor="mm")
    d.text((795, 330), st["name"] + "駅 から", font=SANS("Bold", 56), fill=P["ink"], anchor="mm")
    d.text((795, 420), ["徒歩5分", "すぐ", "300m →", "バス10分"][k % 4], font=SANS("Black", 60), fill=(190, 40, 30), anchor="mm")
    for cx, cy in ((34, 34), (W - 34, 34), (34, H - 34), (W - 34, H - 34)):
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(150, 150, 150), outline=(70, 70, 70), width=2)
    return mt.age(im, rust=0.9, yellow=0.1, seed=k + IDX[sid] * 3)


def st_watercolor(sid, k, P, rng, W=760, H=1000):
    st = ST[sid]
    base = paper_tex(W, H, P["paper"], seed=k + 5, fiber=0.07)
    wash = Image.new("RGB", (W, H), P["paper"])
    d = ImageDraw.Draw(wash, "RGBA")
    art = scene(sid, (W - 80, int(H * 0.62)), P, rng, line=None)
    art = art.filter(ImageFilter.GaussianBlur(5))
    for _ in range(14):
        cx, cy, r = rng.randint(0, W), rng.randint(0, int(H * .7)), rng.randint(80, 220)
        c = rng.choice([P["a"], P["b"], P["c"]])
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c + (40,))
    wash = wash.filter(ImageFilter.GaussianBlur(30))
    wash.paste(art, (40, 110), Image.new("L", art.size, 215))
    im = ImageChops.multiply(base, wash)
    d = ImageDraw.Draw(im)
    title = copy(sid, k + 1)
    d.text((W // 2, 60), title, font=tfit(d, title, "r", "Bold", W - 100, 74), fill=P["ink"], anchor="mm")
    d.text((W // 2, H - 150), st["name"] + "の風景", font=SERIF("Medium", 54), fill=P["ink"], anchor="mm")
    d.text((W // 2, H - 80), f"{rng.randint(1, 12)}月の展覧会  駅前ギャラリー", font=SANS("Medium", 32), fill=P["a"], anchor="mm")
    return mt.age(im, rust=0.0, chips=False, yellow=0.08, seed=k + IDX[sid])


def st_retro(sid, k, P, rng, W=760, H=1080):
    st = ST[sid]
    im = Image.new("RGB", (W, H), P["b"])
    d = ImageDraw.Draw(im)
    art = scene(sid, (W, int(H * 0.62)), P, rng, line=P["ink"])
    art = halftone(art, 0.3, 8, seed=k)
    im.paste(art, (0, 130))
    title = copy(sid, k)
    f = tfit(d, title, "r", "Black", W - 120, 130)
    for dx, dy in ((6, 6), (4, 4), (2, 2)):
        d.text((W // 2 + dx, 60 + dy), title, font=f, fill=P["ink"], anchor="mm")
    d.text((W // 2, 60), title, font=f, fill=P["paper"], anchor="mm")
    d.rectangle([0, 130 + art.height, W, H], fill=P["ink"])
    d.text((W // 2, H - 150), "ようこそ " + st["name"] + " へ", font=SERIF("Black", 64), fill=P["paper"], anchor="mm")
    d.text((W // 2, H - 70), "国鉄 " + st["name"] + "駅 ・ 時刻表は駅で", font=SANS("Medium", 34), fill=P["c"], anchor="mm")
    return mt.age(im, rust=0.15, chips=False, yellow=0.1, seed=k + IDX[sid])


def st_photo(sid, k, P, rng, W=900, H=700):
    st = ST[sid]
    src = f"/home/claude/station/out/z_{sid}.png"
    if os.path.exists(src):
        ph = Image.open(src).convert("RGB")
        ph = ph.resize((W - 120, int((W - 120) * ph.height / ph.width)))
    else:
        ph = scene(sid, (W - 120, H - 240), P, rng, line=None)
        ph = halftone(ph, 0.25, 6)
    im = Image.new("RGB", (W, H), (244, 240, 230))
    im.paste(ph.crop((0, 0, W - 120, min(ph.height, H - 220))), (60, 50))
    d = ImageDraw.Draw(im)
    d.text((W // 2, H - 130), st["name"] + "駅前" + ["風景", "の朝", "あたり", "の夕暮れ"][k % 4], font=SERIF("Bold", 56), fill=(40, 34, 30), anchor="mm")
    d.text((W - 80, H - 55), "昭和" + str(rng.randint(30, 49)) + "年撮影", font=SANS("Medium", 26), fill=(110, 100, 90), anchor="rm")
    return mt.age(im, rust=0.0, chips=False, yellow=0.25, seed=k + IDX[sid])


def st_newspaper(sid, k, P, rng, W=800, H=1000):
    st = ST[sid]
    im = paper_tex(W, H, (232, 226, 208), seed=k + 11, fiber=0.08)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 70), st["name"] + "新報", font=SERIF("Black", 76), fill=(30, 28, 26), anchor="mm")
    d.line([30, 125, W - 30, 125], fill=(30, 28, 26), width=5)
    head = copy(sid, k) + " " + rng.choice(["今週末に開催", "盛況のうちに閉幕", "まもなく開幕", "見どころ紹介"])
    d.text((40, 190), head, font=tfit(d, head, "r", "Black", W - 80, 58), fill=(20, 18, 16), anchor="lm")
    art = scene(sid, (W - 80, 280), P, rng, line=None).convert("L").convert("RGB")
    im.paste(halftone(art, 0.2, 6), (40, 240))
    for c in range(3):
        x0 = 40 + c * (W - 80) // 3
        for r_ in range(16):
            ln = "".join(rng.choice("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわ") for _ in range(11))
            d.text((x0, 560 + r_ * 26), ln, font=SERIF("Medium", 17), fill=(50, 46, 42), anchor="lm")
    return mt.age(im, rust=0.0, chips=False, yellow=0.3, seed=k + IDX[sid])


def st_hand(sid, k, P, rng, W=700, H=900):
    st = ST[sid]
    im = paper_tex(W, H, (246, 242, 228), seed=k + 21, fiber=0.05)
    d = ImageDraw.Draw(im)
    title = rng.choice(["臨時列車のおしらせ", "運休のおしらせ", "迷子のおしらせ", st["name"] + "駅からのお願い", "尋ね人"])
    tl = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
    ImageDraw.Draw(tl).text((W // 2, 65), title, font=tfit(d, title, "r", "Black", W - 80, 70), fill=(190, 30, 30, 255), anchor="mm")
    tl = tl.rotate(rng.uniform(-3, 3), resample=Image.BICUBIC)
    im.paste(tl, (0, 40), tl)
    lines = rng.sample(["下記のとおり運転します", "お間違えのないように", "ご不便をおかけします", "詳しくは駅員まで", "雨天のため一部運休", "持ち物にご注意", f"{rng.randint(1, 12)}月{rng.randint(1, 28)}日 午前{rng.randint(6, 11)}時"], 5)
    for i, l in enumerate(lines):
        layer = Image.new("RGBA", (W, 90), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((70 + rng.randint(-8, 8), 45), l, font=SERIF("Bold", rng.randint(36, 46)), fill=(30, 28, 26, 255), anchor="lm")
        layer = layer.rotate(rng.uniform(-2, 2), resample=Image.BICUBIC)
        im.paste(layer, (0, 220 + i * 105), layer)
    d.ellipse([W // 2 - 14, 14, W // 2 + 14, 42], fill=(190, 40, 40), outline=(90, 20, 20), width=2)
    d.text((W - 60, H - 50), st["name"] + "駅長", font=SERIF("Bold", 36), fill=(30, 28, 26), anchor="rm")
    return mt.age(im, rust=0.0, chips=False, yellow=0.22, seed=k + IDX[sid])


def st_nobori(sid, k, P, rng, W=300, H=1100):
    st = ST[sid]
    im = Image.new("RGB", (W, H), P["b"] if k % 2 else P["a"])
    d = ImageDraw.Draw(im)
    fg = P["paper"] if k % 2 == 0 else P["ink"]
    d.rectangle([10, 10, W - 11, H - 11], outline=fg, width=8)
    title = copy(sid, k + 3)
    for i, ch in enumerate(title[:7]):
        d.text((W // 2, 130 + i * 112), ch, font=SERIF("Black", 104), fill=fg, anchor="mm")
    d.text((W // 2, H - 150), "開催中", font=SANS("Black", 52), fill=(210, 50, 40) if k % 2 else P["c"], anchor="mm")
    d.text((W // 2, H - 80), st["name"] + "駅前", font=SANS("Bold", 40), fill=fg, anchor="mm")
    return mt.age(im, rust=0.0, chips=False, yellow=0.1, seed=k + IDX[sid])


FN = {"woodblock": st_woodblock, "enamel": st_enamel, "watercolor": st_watercolor, "retro": st_retro, "photo": st_photo, "newspaper": st_newspaper, "hand": st_hand, "nobori": st_nobori}


def shop_sign(sid, kind, P, rng):
    st = ST[sid]
    pre = st["name"] if len(st["name"]) <= 3 else st["name"][:2]
    nm = {"shokudo": rng.choice([pre + "食堂", "めし処 " + pre, pre + "軒"]), "ryokan": rng.choice([pre + "館", "旅館 " + pre + "荘", pre + "の宿"]),
          "shoten": rng.choice([pre + "商店", "よろず " + pre + "屋", pre + "雑貨店"]), "riyo": rng.choice(["理容 " + pre, pre + "理髪店"]),
          "kusuri": rng.choice([pre + "薬局", "薬 " + pre + "堂"]), "sakaya": rng.choice(["酒 " + pre + "屋", pre + "酒店"])}[kind]
    form = rng.choice(["wide", "wide", "vertical", "noren", "enamel"])
    ink = P["ink"]
    if form == "vertical":
        W, H = 320, 1000
        im = paper_tex(W, H, P["paper"], seed=3)
        d = ImageDraw.Draw(im)
        d.rectangle([8, 8, W - 9, H - 9], outline=ink, width=8)
        for i, ch in enumerate(nm[:7]):
            d.text((W // 2, 120 + i * 130), ch, font=SERIF("Black", 120), fill=ink, anchor="mm")
        im = mt.age(im, rust=0.4, yellow=0.15, seed=rng.randint(0, 90))
    elif form == "noren":
        W, H = 1200, 520
        im = Image.new("RGB", (W, H), (236, 230, 214))
        d = ImageDraw.Draw(im)
        for i in range(3):
            x0 = 20 + i * 395
            d.rectangle([x0, 30, x0 + 370, H - 20], fill=P["a"])
            d.line([x0 + 185, 30, x0 + 185, 110], fill=P["ink"], width=3)
        ch = nm.replace(" ", "")[:6]
        for i, c in enumerate(ch[:3]):
            d.text((205 + i * 395, 270), c, font=SERIF("Black", 220), fill=P["paper"], anchor="mm")
        d.rectangle([0, 0, W, 34], fill=(70, 50, 36))
        im = mt.age(im, rust=0.0, chips=False, yellow=0.1, seed=rng.randint(0, 90))
    elif form == "enamel":
        W, H = 1200, 420
        im = Image.new("RGB", (W, H), P["a"] if rng.random() < 0.5 else (240, 236, 226))
        d = ImageDraw.Draw(im)
        fg = P["paper"] if sum(im.getpixel((5, 5))) < 420 else P["ink"]
        d.rounded_rectangle([14, 14, W - 15, H - 15], radius=36, outline=fg, width=10)
        d.text((W // 2, H // 2), nm, font=tfit(d, nm, "s", "Black", W - 140, 220), fill=fg, anchor="mm")
        im = mt.age(im, rust=0.8, yellow=0.08, seed=rng.randint(0, 90))
    else:
        W, H = 1500, 420
        bg = rng.choice([(30, 30, 34), (236, 230, 210), P["a"], (52, 36, 24)])
        im = paper_tex(W, H, bg, seed=7, fiber=0.04)
        d = ImageDraw.Draw(im)
        fg = (240, 232, 205) if sum(bg) < 330 else P["ink"]
        d.rectangle([12, 12, W - 13, H - 13], outline=fg, width=7)
        d.text((W // 2, H // 2), nm, font=tfit(d, nm, "r", "Black", W - 160, 260), fill=fg, anchor="mm")
        im = mt.age(im, rust=0.5, yellow=0.1, seed=rng.randint(0, 90))
    return im, nm


def make(sid):
    st = ST[sid]
    P = pal(sid)
    rng = random.Random(IDX[sid] * 4099 + 5)
    sty = styles_for(sid)
    names = []
    for k in range(4):
        fn = FN[sty[k] if sty[k] != "nobori" else sty[4]]
        fn(sid, k, P, rng).save(f"{OUT}/{sid}_poster{k}.png")
        names.append(f"{sid}_poster{k}.png")
    FN["hand"](sid, 9, P, rng).save(f"{OUT}/{sid}_notice.png")
    for k in range(2):
        FN["nobori"](sid, k, P, rng).save(f"{OUT}/{sid}_nobori{k}.png")
    for k in range(3):
        s_ = FN[rng.choice(["enamel", "woodblock", "retro"])]
        im = s_(sid, k + 5, P, rng)
        im.save(f"{OUT}/{sid}_bb{k}.png")
    th = motifs(sid)[0]
    kinds = ["shokudo", "shoten", "kusuri", "sakaya"] + (["ryokan"] if "onsen" in motifs(sid) or "sea" in motifs(sid) else ["riyo"])
    first = None
    for kd in kinds:
        im, nm = shop_sign(sid, kd, P, rng)
        im.save(f"{OUT}/{sid}_sign_{kd}.png")
        if kd == "shokudo":
            first = nm
    import make_posters as v1
    v1.THEME.setdefault(sid, "farm")
    v1.timetable(st, sid, rng).save(f"{OUT}/{sid}_timetable.png")
    v1.areamap(st, sid, rng).save(f"{OUT}/{sid}_map.png")
    v1.menu(st, sid, first or st["name"] + "食堂", rng).save(f"{OUT}/{sid}_menu.png")
    return True


if __name__ == "__main__":
    ids = sys.argv[1:] or list(ST)
    for s in ids:
        make(s)
    print("v2 made for", len(ids))
