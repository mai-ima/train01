"""Original (fictional) posters, signboards, menus, timetables and maps for every station of the network."""
import json, math, random, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import make_textures2 as mt

NET = json.load(open("/home/claude/station/net/network.json"))
ST = {s["id"]: s for s in NET["stations"]}
OUT = "/home/claude/station/tex/kit"
SANS, SERIF, text = mt.SANS, mt.SERIF, mt.text

THEME = {"M01": "city", "M02": "suburb", "M03": "city", "M04": "suburb", "M05": "farm", "M06": "origin", "M07": "farm", "M08": "forest",
         "M09": "forest", "M10": "onsen", "M11": "mountain", "M12": "mountain", "M13": "snow", "L01": "snow", "M14": "harbor", "M15": "cliff",
         "M16": "harbor", "M17": "cliff", "M18": "lighthouse", "M19": "harbor", "F01": "freight", "Y02": "onsen", "Y03": "onsen", "Y04": "onsen",
         "K02": "city", "K03": "harbor", "T02": "city", "T03": "city", "T04": "suburb", "S02": "farm", "S03": "forest", "S04": "highland",
         "R02": "harbor", "TR02": "harbor", "B02": "harbor"}
PAL = {"city": [(34, 52, 94), (232, 190, 80)], "suburb": [(60, 120, 150), (240, 220, 160)], "farm": [(110, 150, 70), (240, 214, 120)],
       "origin": [(120, 28, 24), (238, 214, 150)], "forest": [(30, 90, 60), (226, 220, 170)], "onsen": [(150, 60, 70), (250, 230, 200)],
       "mountain": [(70, 90, 120), (240, 236, 224)], "snow": [(60, 110, 160), (250, 252, 255)], "harbor": [(18, 80, 120), (250, 220, 120)],
       "cliff": [(30, 100, 130), (255, 236, 200)], "lighthouse": [(20, 60, 110), (255, 255, 235)], "freight": [(70, 70, 76), (240, 200, 70)],
       "highland": [(80, 140, 100), (255, 245, 210)]}
SPOT = {"city": ["百貨店の大売出し", "市民音楽祭", "名店街フェア", "ビヤホール開き"], "suburb": ["桜まつり", "団地の夏祭り", "ふれあい運動会", "園芸市"],
        "farm": ["新米まつり", "稲刈り体験", "秋の収穫祭", "農協まつり"], "origin": ["国鉄発祥記念祭", "鉄道記念館 開館", "機関車まつり", "創業の地 巡り"],
        "forest": ["森の木工市", "きのこ狩り", "山菜まつり", "林道ウォーク"], "onsen": ["湯けむり祭", "秘湯めぐり", "湯治割引", "足湯の里"],
        "mountain": ["峠の茶屋", "紅葉ハイク", "高原列車", "山開き"], "snow": ["スキー場開き", "雪まつり", "かまくら村", "樹氷ツアー"],
        "harbor": ["朝市", "魚まつり", "遊覧船", "港まつり"], "cliff": ["海水浴場開き", "夕日の岬", "潮干狩り", "海の家"],
        "lighthouse": ["灯台一般公開", "岬めぐり", "星空観察会", "漁火見物"], "freight": ["安全週間", "荷役作業 注意", "貨物取扱案内", "運送のご案内"],
        "highland": ["高原牧場 乳しぼり", "星空キャンプ", "ソフトクリーム", "ペンション村"]}


def fnt(kind, w, s):
    return (SANS if kind == "s" else SERIF)(w, s)


def art(d, theme, box, rng):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    a, b = PAL[theme]
    d.rectangle(box, fill=tuple(int(c * 0.55 + 255 * 0.25) for c in a))
    d.ellipse([x0 + w * 0.62, y0 + h * 0.1, x0 + w * 0.86, y0 + h * 0.1 + w * 0.24], fill=b)
    def ridge(k, col, amp):
        pts = [(x0, y1)]
        for i in range(0, 21):
            pts.append((x0 + w * i / 20, y1 - h * (0.25 + k * 0.12) - amp * h * (0.5 + 0.5 * math.sin(i * 0.7 + k * 2 + rng.random() * 0.3))))
        pts.append((x1, y1))
        d.polygon(pts, fill=col)
    ridge(2, tuple(int(c * 0.75) for c in a), 0.16)
    ridge(1, tuple(int(c * 0.55) for c in a), 0.12)
    if theme in ("harbor", "cliff", "lighthouse"):
        d.rectangle([x0, y1 - h * 0.3, x1, y1], fill=(20, 70, 110))
        for k in range(8):
            yy = y1 - h * 0.28 + k * h * 0.035
            d.line([x0 + w * 0.05, yy, x1 - w * 0.05, yy], fill=(150, 190, 215), width=2)
        d.polygon([(x0 + w * .15, y1 - h * .3), (x0 + w * .45, y1 - h * .3), (x0 + w * .4, y1 - h * .22), (x0 + w * .2, y1 - h * .22)], fill=(225, 225, 215))
        d.line([x0 + w * .3, y1 - h * .3, x0 + w * .3, y1 - h * .46], fill=(80, 60, 40), width=3)
        d.polygon([(x0 + w * .3, y1 - h * .46), (x0 + w * .3, y1 - h * .32), (x0 + w * .42, y1 - h * .33)], fill=(245, 245, 235))
        if theme == "lighthouse":
            d.rectangle([x0 + w * .66, y1 - h * .62, x0 + w * .74, y1 - h * .3], fill=(245, 245, 240))
            d.rectangle([x0 + w * .66, y1 - h * .5, x0 + w * .74, y1 - h * .44], fill=(190, 40, 30))
    elif theme in ("onsen",):
        for k in range(5):
            cx = x0 + w * (0.2 + 0.15 * k)
            d.arc([cx - 18, y1 - h * .55, cx + 18, y1 - h * .35], 200, 340, fill=(250, 250, 250), width=5)
        d.rectangle([x0 + w * .3, y1 - h * .3, x0 + w * .7, y1 - h * .1], fill=(120, 80, 50))
        d.polygon([(x0 + w * .26, y1 - h * .3), (x0 + w * .5, y1 - h * .42), (x0 + w * .74, y1 - h * .3)], fill=(60, 50, 50))
    elif theme in ("snow", "mountain", "highland"):
        d.polygon([(x0 + w * .55, y1 - h * .2), (x0 + w * .75, y1 - h * .72), (x0 + w * .95, y1 - h * .2)], fill=(238, 238, 240))
    elif theme in ("farm", "suburb"):
        for k in range(6):
            d.line([x0, y1 - h * (0.05 + 0.04 * k), x1, y1 - h * (0.05 + 0.04 * k)], fill=(70 + 15 * k, 120 + 12 * k, 40), width=int(h * 0.04))
    elif theme in ("city", "freight"):
        for k in range(9):
            bw = w * 0.07
            bx = x0 + w * (0.06 + 0.1 * k)
            bh = h * (0.2 + 0.4 * rng.random())
            d.rectangle([bx, y1 - bh, bx + bw, y1], fill=(60 + rng.randint(0, 40),) * 3)
            for r_ in range(int(bh / 18)):
                d.rectangle([bx + 4, y1 - bh + 8 + r_ * 18, bx + bw - 4, y1 - bh + 14 + r_ * 18], fill=(240, 220, 120))
    elif theme == "origin":
        d.rectangle([x0 + w * .15, y1 - h * .22, x0 + w * .85, y1 - h * .14], fill=(40, 35, 30))
        d.rectangle([x0 + w * .2, y1 - h * .4, x0 + w * .52, y1 - h * .22], fill=(30, 28, 28))
        d.rectangle([x0 + w * .46, y1 - h * .5, x0 + w * .5, y1 - h * .4], fill=(30, 28, 28))
        d.ellipse([x0 + w * .22, y1 - h * .2, x0 + w * .3, y1 - h * .12], fill=(60, 55, 50))
        d.ellipse([x0 + w * .4, y1 - h * .2, x0 + w * .48, y1 - h * .12], fill=(60, 55, 50))
    elif theme == "forest":
        for k in range(14):
            cx = x0 + w * rng.random()
            d.polygon([(cx - 22, y1), (cx, y1 - h * (0.25 + 0.25 * rng.random())), (cx + 22, y1)], fill=(20, 80 + rng.randint(0, 30), 45))


def fit(d, s_, kind, w_, maxw, size):
    while size > 14:
        f = fnt(kind, w_, size)
        if d.textlength(s_, font=f) <= maxw:
            return f
        size -= 2
    return fnt(kind, w_, 14)


def poster(st, sid, k, rng):
    th = THEME[sid]
    a, b = PAL[th]
    rot = [(0, 1, 2), (2, 0, 1), (1, 2, 0), (0, 2, 1)][k % 4]
    a = tuple(a[i_] for i_ in rot) if k % 4 else a
    W, H = 760, 1080
    title = SPOT[th][k % 4]
    paper = tuple(int(c * 0.15 + 238 * 0.85) for c in b)
    im = Image.new("RGB", (W, H), paper if k % 2 == 0 else tuple(int(c * 0.5 + 120) for c in a))
    d = ImageDraw.Draw(im)
    dark = (30, 24, 24)
    if k % 4 == 0:        # banner on top, art, caption below
        d.rectangle([0, 0, W, 170], fill=a)
        text(d, (W // 2, 70), title, fit(d, title, "r", "Black", 700, 86), tuple(min(255, c + 160) for c in b))
        text(d, (W // 2, 138), st["name"] + "駅から " + ["徒歩5分", "バス10分", "徒歩12分", "すぐそこ"][rng.randint(0, 3)], fnt("s", "Bold", 40), (255, 255, 255))
        art(d, th, (30, 190, W - 30, 700), rng)
        text(d, (W // 2, 770), "安全第一 " + st["name"] if th == "freight" else "おいでよ " + st["name"], fnt("r", "Bold", 54), a)
        text(d, (W // 2, 860), f"{rng.randint(3, 11)}月{rng.randint(1, 28)}日(日) 午前{rng.randint(9, 11)}時から", fnt("s", "Bold", 44), dark)
        text(d, (W // 2, 930), "指差し呼称 ヨシ!" if th == "freight" else "雨天決行 入場無料", fnt("s", "Medium", 36), (70, 50, 40))
        d.rectangle([60, 985, W - 60, 1045], outline=a, width=4)
        text(d, (W // 2, 1015), "主催 " + st["name"] + "観光協会", fnt("s", "Medium", 32), a)
    elif k % 4 == 1:      # full-bleed art, big circle title, lanterns
        art(d, th, (0, 0, W, 760), rng)
        for q in range(7):
            cx = 60 + q * 107
            d.line([cx, 0, cx, 60 + (q % 2) * 30], fill=dark, width=3)
            d.ellipse([cx - 28, 60 + (q % 2) * 30, cx + 28, 140 + (q % 2) * 30], fill=(215, 50, 40), outline=(255, 230, 150), width=3)
        d.ellipse([W // 2 - 330, 560, W // 2 + 330, 1130], fill=b, outline=a, width=10)
        text(d, (W // 2, 690), title, fit(d, title, "r", "Black", 520, 104), a)
        text(d, (W // 2, 810), st["name"] + "駅前広場", fnt("s", "Bold", 48), dark)
        text(d, (W // 2, 880), f"{rng.randint(3, 11)}月{rng.randint(1, 28)}日 {rng.randint(9, 18)}:00〜", fnt("s", "Medium", 40), dark)
        text(d, (W // 2, 950), "屋台・抽選会・ステージ", fnt("s", "Medium", 34), (80, 40, 40))
    elif k % 4 == 2:      # vertical (tategaki) title on the right
        d.rectangle([0, 0, W, 90], fill=a)
        text(d, (W // 2, 45), st["name"] + "駅 お知らせ", fnt("s", "Bold", 44), b)
        art(d, th, (30, 120, 470, 840), rng)
        for q, ch in enumerate(title):
            text(d, (600, 190 + q * (min(120, 620 // max(1, len(title))))), ch, fnt("r", "Black", 100), a)
        d.line([510, 120, 510, 840], fill=a, width=4)
        text(d, (W // 2, 920), f"{rng.randint(3, 11)}月{rng.randint(1, 28)}日 開催", fnt("r", "Bold", 54), dark)
        text(d, (W // 2, 1000), "お問い合わせは駅前案内所へ", fnt("s", "Medium", 34), (70, 50, 40))
    else:                 # framed "travel" style with ribbon
        d.rectangle([24, 24, W - 25, H - 25], outline=a, width=14)
        art(d, th, (60, 230, W - 60, 760), rng)
        d.polygon([(0, 150), (W, 150), (W - 50, 205), (W, 260), (0, 260), (50, 205)], fill=a)
        text(d, (W // 2, 205), title, fit(d, title, "r", "Black", 560, 96), b)
        text(d, (W // 2, 120), "国鉄 " + st["name"] + "駅 から", fnt("s", "Bold", 44), a)
        text(d, (W // 2, 830), rng.choice(["荷物は 国鉄 チッキ・小荷物", "コンテナ輸送で迅速に", "貨物の取扱い 受付中"] if th == "freight" else ["日帰り割引きっぷ発売中", "周遊券で一日たっぷり", "団体割引あり"]), fnt("r", "Bold", 50), dark)
        text(d, (W // 2, 910), ("貨物 " if th == "freight" else "運賃 ") + str(rng.randint(2, 9) * 10 + 20) + "円〜", fnt("s", "Black", 60), (170, 40, 30))
        text(d, (W // 2, 1000), st["name"] + "駅 出札口まで", fnt("s", "Medium", 34), a)
    return mt.age(im, rust=0.2, chips=False, yellow=0.1, seed=k + hash(sid) % 90)


def sign_shop(st, sid, kind, rng):
    th = THEME[sid]
    a, b = PAL[th]
    pre = st["name"] if len(st["name"]) <= 3 else st["name"][:2]
    names = {"shokudo": [pre + "食堂", "めし処 " + pre], "ryokan": [pre + "館", "旅館 " + pre + "荘"], "shoten": [pre + "商店", "よろず " + pre + "屋"],
             "riyo": ["理容 " + pre, pre + "理髪店"], "kusuri": [pre + "薬局", "薬 " + pre + "堂"], "sakaya": ["酒 " + pre + "屋", pre + "酒店"]}[kind]
    nm = rng.choice(names)
    W, H = 1500, 420
    bgc = {"shokudo": (30, 30, 34), "ryokan": (58, 38, 24), "shoten": (230, 226, 210), "riyo": (240, 240, 235), "kusuri": (220, 238, 226), "sakaya": (28, 42, 30)}[kind]
    fg = (240, 232, 205) if sum(bgc) < 300 else (30, 30, 34)
    im = Image.new("RGB", (W, H), bgc)
    d = ImageDraw.Draw(im)
    d.rectangle([12, 12, W - 13, H - 13], outline=fg, width=8)
    text(d, (W // 2, H // 2), nm, fnt("r", "Black", int(min(250, 1300 / len(nm)))), fg)
    if kind == "riyo":
        for i in range(0, 90, 18):
            d.line([60, 50 + i, 160, 120 + i], fill=(200, 40, 40), width=8)
    return mt.age(im, rust=0.5, yellow=0.1, seed=rng.randint(0, 80)), nm


def menu(st, sid, shopname, rng):
    th = THEME[sid]
    dish = {"harbor": [("海鮮丼", 450), ("焼き魚定食", 380), ("あら汁", 120), ("いか刺", 280)], "onsen": [("山菜そば", 220), ("温泉卵", 60), ("川魚塩焼", 320), ("ところてん", 120)],
            "farm": [("きつねうどん", 150), ("かつ丼", 300), ("おでん", 180), ("新米おにぎり", 80)], "mountain": [("山賊焼", 350), ("とろろ飯", 280), ("栗ぜんざい", 150), ("お茶", 40)],
            "snow": [("味噌ラーメン", 250), ("豚汁定食", 280), ("甘酒", 80), ("カレーライス", 230)], "city": [("ナポリタン", 300), ("オムライス", 350), ("プリン", 180), ("コーヒー", 150)]}.get(th, [("ラーメン", 200), ("カレー", 220), ("そば", 150), ("ごはん", 60)])
    W, H = 720, 960
    im = Image.new("RGB", (W, H), (236, 224, 196))
    d = ImageDraw.Draw(im)
    d.rectangle([20, 20, W - 21, H - 21], outline=(110, 40, 30), width=6)
    text(d, (W // 2, 100), shopname, fnt("r", "Black", 70 if len(shopname) < 7 else 56), (110, 40, 30))
    text(d, (W // 2, 175), "お品書き", fnt("r", "Bold", 44), (60, 40, 30))
    for i, (n, p) in enumerate(dish + [("ビール", 260), ("お冷や", 0)][:2]):
        y = 260 + i * 110
        text(d, (80, y), n, fnt("r", "Bold", 52), (30, 24, 20), anchor="lm")
        text(d, (W - 80, y), "お代 無料" if p == 0 else f"{p}円", fnt("s", "Medium", 46), (30, 24, 20), anchor="rm")
        d.line([60, y + 48, W - 60, y + 48], fill=(150, 120, 90), width=2)
    return mt.age(im, rust=0.1, chips=False, yellow=0.2, seed=rng.randint(0, 80))


def timetable(st, sid, rng):
    W, H = 900, 1000
    im = Image.new("RGB", (W, H), (238, 236, 226))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 130], fill=(30, 100, 70))
    text(d, (W // 2, 65), st["name"] + "駅 時刻表", fnt("s", "Black", 64), (255, 255, 255))
    for col, lab in enumerate(["上り(国都中央方面)", "下り(終点方面)"]):
        x0 = 30 + col * 440
        text(d, (x0 + 200, 175), lab, fnt("s", "Bold", 34), (30, 30, 30))
        d.line([x0, 205, x0 + 410, 205], fill=(30, 30, 30), width=3)
        for hr in range(5, 23):
            y = 225 + (hr - 5) * 42
            text(d, (x0 + 20, y), f"{hr:02d}", fnt("s", "Black", 30), (30, 30, 30), anchor="lm")
            mins = sorted(rng.sample(range(0, 60, 3), rng.choice([1, 1, 2, 2, 3] if st["km"] < 20 else [0, 1, 1, 2])))
            text(d, (x0 + 80, y), "  ".join(f"{m:02d}" for m in mins), fnt("s", "Medium", 30), (30, 30, 30), anchor="lm")
    text(d, (W // 2, 975), "国鉄 ※臨時列車はお知らせします", fnt("s", "Medium", 26), (70, 70, 70))
    return mt.age(im, rust=0.1, chips=False, yellow=0.12, seed=rng.randint(0, 80))


def areamap(st, sid, rng):
    W, H = 900, 640
    im = Image.new("RGB", (W, H), (240, 232, 205))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, W - 15, H - 15], outline=(60, 50, 40), width=6)
    text(d, (W // 2, 56), st["name"] + "駅周辺案内図", fnt("s", "Black", 48), (40, 30, 24))
    d.line([40, 340, W - 40, 340], fill=(60, 60, 60), width=14)
    d.line([40, 340, W - 40, 340], fill=(240, 240, 240), width=2)
    d.line([430, 340, 430, 560], fill=(150, 120, 80), width=18)
    d.rectangle([380, 262, 480, 322], fill=(150, 40, 30))
    text(d, (430, 292), "駅", fnt("s", "Black", 40), (255, 255, 255))
    import re as _re
    spots = [_re.split(r"[(（+]", x)[0][:9] for x in list(dict.fromkeys(st.get("town", []) + st.get("features", [])))][:8]
    cells = [(125 + c * 215, y) for y in (125, 200) for c in range(4)]
    cells = [p for p in cells if not (330 < p[0] < 530 and p[1] > 190)][:5] + [(125 + c * 215, y) for y in (440, 520) for c in range(4) if not (330 < 125 + c * 215 < 540)]
    for (x, y), s_ in zip(cells, spots):
        f = fit(d, s_, "s", "Bold", 170, 28)
        d.rectangle([x - 90, y - 28, x + 90, y + 28], fill=(250, 250, 245), outline=(90, 70, 50), width=3)
        text(d, (x, y), s_, f, (30, 30, 30))
    text(d, (W // 2, 598), "★ 現在地 " + st["name"] + "駅", fnt("s", "Medium", 28), (150, 40, 30))
    return mt.age(im, rust=0.1, chips=False, yellow=0.18, seed=rng.randint(0, 80))


def billboard(st, sid, k, rng):
    th = THEME[sid]
    a, b = PAL[th]
    items = [("ひまわり薬品", "元気の素 ひまわり胃腸薬"), ("あけぼの醤油", "味は あけぼの"), ("みどり茶園", "お茶は みどり"), ("つばめ石鹸", "つばめ 清潔のしるし"), ("ほし乳業", "牛乳は ほし")][k % 5]
    W, H = 1500, 560
    im = Image.new("RGB", (W, H), a)
    d = ImageDraw.Draw(im)
    d.rectangle([20, 20, W - 21, H - 21], outline=b, width=10)
    text(d, (W // 2, 170), items[0], fnt("r", "Black", 170), b)
    text(d, (W // 2, 360), items[1], fnt("r", "Bold", 90), (255, 255, 255))
    text(d, (W // 2, 480), st["name"] + "駅前 取扱店 ← 100m", fnt("s", "Medium", 50), tuple(min(255, c + 80) for c in b))
    return mt.age(im, rust=0.6, yellow=0.15, seed=rng.randint(0, 80))


def notice(st, sid, rng):
    W, H = 640, 900
    im = Image.new("RGB", (W, H), (244, 240, 228))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 130], fill=(160, 30, 24))
    text(d, (W // 2, 65), rng.choice(["おしらせ", "ご注意", "旅客のみなさまへ", "安全第一"]), fnt("r", "Black", 78), (255, 255, 255))
    lines = rng.sample(["線路への立入りは危険です", "踏切では一旦停止", "忘れ物にご注意ください", "ホームでは走らないで", "列車の窓から顔や手を出さないで", "ごみは持ち帰りましょう", "手荷物は網棚に", "お年寄りに席をおゆずりください"], 4)
    for i, l in enumerate(lines):
        text(d, (W // 2, 230 + i * 130), l, fnt("r", "Bold", 40 if len(l) < 14 else 33), (30, 30, 30))
        d.line([60, 285 + i * 130, W - 60, 285 + i * 130], fill=(160, 140, 120), width=2)
    text(d, (W // 2, 850), st["name"] + "駅長", fnt("s", "Medium", 36), (60, 60, 60))
    return mt.age(im, rust=0.3, yellow=0.2, seed=rng.randint(0, 80))


def make(sid):
    st = ST[sid]
    rng = random.Random(hash(sid) % 100000 + 7)
    out = []
    for k in range(4):
        poster(st, sid, k, rng).save(f"{OUT}/{sid}_poster{k}.png")
        out.append(f"{sid}_poster{k}.png")
    for kind in (["shokudo", "shoten", "ryokan"] if THEME[sid] in ("onsen", "harbor", "origin", "city") else ["shokudo", "shoten", "riyo"]) + ["kusuri", "sakaya"]:
        im, nm = sign_shop(st, sid, kind, rng)
        im.save(f"{OUT}/{sid}_sign_{kind}.png")
        out.append(f"{sid}_sign_{kind}.png")
        if kind == "shokudo":
            menu(st, sid, nm, rng).save(f"{OUT}/{sid}_menu.png")
            out.append(f"{sid}_menu.png")
    timetable(st, sid, rng).save(f"{OUT}/{sid}_timetable.png")
    areamap(st, sid, rng).save(f"{OUT}/{sid}_map.png")
    notice(st, sid, rng).save(f"{OUT}/{sid}_notice.png")
    for k in range(3):
        billboard(st, sid, k + hash(sid) % 5, rng).save(f"{OUT}/{sid}_bb{k}.png")
        out.append(f"{sid}_bb{k}.png")
    return out + [f"{sid}_timetable.png", f"{sid}_map.png", f"{sid}_notice.png"]


if __name__ == "__main__":
    ids = sys.argv[1:] or list(ST)
    tot = 0
    for sid in ids:
        tot += len(make(sid))
    print("made", tot, "images for", len(ids), "stations")
