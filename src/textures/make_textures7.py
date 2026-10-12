"""P7: 周遊列車「結」の画像(エンブレム・献立・乗車券・旅程ポスター)。原作オリジナル。tex/ に保存。"""
import sys
sys.path.insert(0, "/home/claude/station/net")
import math
import make_textures6 as m
from make_textures6 import canvas, fin, SERIF, SANS, S, OUTD
from PIL import Image, ImageDraw
import network, services

GOLD = (238, 208, 132)
BRZ = (30, 18, 10)
BRZ2 = (92, 58, 28)
CREAM = (250, 244, 226)


def emblem():
    W = 512
    im, d = canvas(W, W)
    s = lambda v: int(v * S)
    d.ellipse([s(20), s(20), s(492), s(492)], fill=BRZ, outline=GOLD, width=s(10))
    d.ellipse([s(46), s(46), s(466), s(466)], outline=GOLD, width=s(3))
    lw = s(13)
    for (cx_, cy_, rx, ry, ang) in ((226, 214, 100, 58, 0.5), (286, 214, 100, 58, -0.5)):
        pts = []
        for t in range(0, 361, 4):
            a = math.radians(t)
            x = rx * math.cos(a); y = ry * math.sin(a)
            pts.append((s(cx_ + x * math.cos(ang) - y * math.sin(ang)), s(cy_ + x * math.sin(ang) + y * math.cos(ang))))
        d.line(pts + [pts[0]], fill=GOLD, width=lw, joint="curve")
    d.ellipse([s(240), s(200), s(272), s(232)], fill=GOLD)
    for sg in (-1, 1):
        d.line([s(256), s(236), s(256 + sg * 40), s(330)], fill=GOLD, width=s(10))
        d.line([s(256), s(236), s(256 + sg * 16), s(344)], fill=GOLD, width=s(7))
    d.text((s(256), s(414)), "結", font=SERIF("Black", s(96)), fill=GOLD, anchor="mm")
    fin(im, W, W, f"{OUTD}/logo_yui.png")


def menu():
    W, H = 640, 960
    im = Image.new("RGB", (W * S, H * S), CREAM)
    d = ImageDraw.Draw(im)
    s = lambda v: int(v * S)
    d.rectangle([s(18), s(18), s(W - 18), s(H - 18)], outline=BRZ2, width=s(5))
    d.rectangle([s(30), s(30), s(W - 30), s(H - 30)], outline=GOLD, width=s(2))
    d.text((s(W / 2), s(92)), "穂波膳", font=SERIF("Black", s(76)), fill=BRZ, anchor="mm")
    d.text((s(W / 2), s(150)), "周遊列車「結」 一日目 夕食", font=SANS("Bold", s(26)), fill=BRZ2, anchor="mm")
    d.line([s(120), s(182), s(W - 120), s(182)], fill=GOLD, width=s(3))
    rows = [("先付", "穂波米の小鉢 川原の湧水豆腐"), ("椀", "北浦の鰈と山辺の根菜 澄まし仕立て"), ("造り", "磯辺の朝獲れ三種 灯台前の藻塩"),
            ("焼", "湯の里の岩魚 みずほの味噌漬け焼"), ("強肴", "高嶺の鴨と雪見の長葱 柚子胡椒"), ("食事", "穂波野の新米 かやま漬 留椀"),
            ("甘味", "杉ノ原の栗 くずきり 汐見の黒蜜")]
    y = 236
    for k, (a, b) in enumerate(rows):
        d.text((s(70), s(y)), a, font=SERIF("Black", s(30)), fill=(150, 24, 20), anchor="lm")
        d.text((s(170), s(y)), b, font=SERIF("Regular", s(27)), fill=BRZ, anchor="lm")
        y += 82
    d.line([s(120), s(y - 24), s(W - 120), s(y - 24)], fill=GOLD, width=s(3))
    d.text((s(W / 2), s(y + 26)), "ご用意する飲み物 国都の地酒・山麓のワイン・各種茶", font=SANS("Regular", s(21)), fill=BRZ2, anchor="mm")
    d.text((s(W / 2), s(H - 70)), "国鉄 周遊列車「結」 食堂車", font=SANS("Bold", s(22)), fill=BRZ2, anchor="mm")
    m.age(im.resize((W, H), Image.LANCZOS), rust=0.0, yellow=0.12, seed=3).save(f"{OUTD}/yui_menu.png")


def ticket():
    W, H = 900, 380
    im = Image.new("RGB", (W * S, H * S), (240, 230, 205))
    d = ImageDraw.Draw(im)
    s = lambda v: int(v * S)
    d.rectangle([0, 0, s(W), s(78)], fill=BRZ)
    d.text((s(30), s(40)), "周遊乗車券・特別車両券  周遊列車「結」", font=SANS("Black", s(34)), fill=GOLD, anchor="lm")
    d.text((s(W - 30), s(40)), "国鉄", font=SANS("Black", s(34)), fill=GOLD, anchor="rm")
    d.text((s(60), s(150)), "国都中央", font=SERIF("Black", s(64)), fill=BRZ, anchor="lm")
    d.text((s(W / 2), s(150)), "→ 周遊 →", font=SANS("Bold", s(34)), fill=BRZ2, anchor="mm")
    d.text((s(W - 60), s(150)), "大湊", font=SERIF("Black", s(64)), fill=BRZ, anchor="rm")
    d.text((s(60), s(236)), "3泊4日  穂波野・穂波空港・奥湯  泊", font=SANS("Bold", s(32)), fill=BRZ, anchor="lm")
    d.text((s(60), s(290)), "スイート 2名1室  展望スイート・ラウンジ・食堂 利用可", font=SANS("Regular", s(26)), fill=BRZ2, anchor="lm")
    d.text((s(60), s(336)), "不定期運行 事前予約制 定員少数 払戻不可", font=SANS("Regular", s(22)), fill=(120, 40, 30), anchor="lm")
    d.ellipse([s(W - 170), s(220), s(W - 40), s(350)], outline=(150, 24, 20), width=s(5))
    d.text((s(W - 105), s(285)), "結", font=SERIF("Black", s(76)), fill=(150, 24, 20), anchor="mm")
    for k in range(18):
        d.ellipse([s(10), s(90 + k * 16), s(18), s(98 + k * 16)], fill=(250, 250, 250)) if False else None
    m.age(im.resize((W, H), Image.LANCZOS), rust=0.0, yellow=0.14, seed=4).save(f"{OUTD}/yui_ticket.png")


def poster():
    W, H = 900, 1280
    im = Image.new("RGB", (W * S, H * S), BRZ)
    d = ImageDraw.Draw(im)
    s = lambda v: int(v * S)
    d.rectangle([s(24), s(24), s(W - 24), s(H - 24)], outline=GOLD, width=s(4))
    d.text((s(W / 2), s(120)), "結", font=SERIF("Black", s(190)), fill=GOLD, anchor="mm")
    d.text((s(W / 2), s(236)), "周遊列車「結」  三泊四日の旅", font=SANS("Bold", s(38)), fill=CREAM, anchor="mm")
    d.text((s(W / 2), s(290)), "国都中央から穂波野・穂波空港・奥湯を巡り大湊へ", font=SANS("Regular", s(26)), fill=GOLD, anchor="mm")
    st = {x[0]: x for x in network.S}
    xs = [x[5][0] for x in network.S]; ys = [x[5][1] for x in network.S]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    bx0, bx1, by0, by1 = 90, W - 90, 350, 1000
    def P(sid):
        x, y = st[sid][5]
        return (s(bx0 + (x - x0) / (x1 - x0) * (bx1 - bx0)), s(by0 + (y - y0) / (y1 - y0) * (by1 - by0)))
    for x in network.S:                       # 全駅のうすい点
        px, py = P(x[0]); d.ellipse([px - s(3), py - s(3), px + s(3), py + s(3)], fill=(110, 80, 50))
    cols = [(236, 150, 60), (120, 200, 220), (150, 220, 120), (240, 120, 150)]
    for i, t in enumerate(("TC1", "TC2", "TC3", "TC4")):
        sv = [q for q in services.SVC if q[0] == t][0]
        pts = [P(x) for x in sv[9]]
        d.line(pts, fill=cols[i], width=s(9), joint="curve")
        for k, sid in enumerate(sv[4]):
            px, py = P(sid); d.ellipse([px - s(9), py - s(9), px + s(9), py + s(9)], fill=CREAM, outline=cols[i], width=s(4))
            dy = -26 if (k + i) % 2 == 0 else 28
            d.text((px, py + s(dy)), st[sid][1], font=SANS("Bold", s(22)), fill=CREAM, anchor="mm", stroke_width=s(3), stroke_fill=BRZ)
    y = 1040
    for i, (a, b) in enumerate((("一日目", "国都中央 → 穂波野  本社と記念館 車内泊"), ("二日目", "かやま → 穂波空港線 → 穂波空港  交流電化区間 車内泊"),
                                ("三日目", "山辺 → 湯の里 → 滝口・奥湯  温泉宿に泊"), ("四日目", "北浦・汐見 → 大湊  市電とモノレールの街へ"))):
        d.rectangle([s(70), s(y - 16), s(96), s(y + 10)], fill=cols[i])
        d.text((s(112), s(y - 3)), a, font=SANS("Black", s(26)), fill=GOLD, anchor="lm")
        d.text((s(222), s(y - 3)), b, font=SANS("Regular", s(23)), fill=CREAM, anchor="lm")
        y += 48
    m.age(im.resize((W, H), Image.LANCZOS), rust=0.0, yellow=0.08, seed=6).save(f"{OUTD}/yui_poster.png")


if __name__ == "__main__":
    emblem(); menu(); ticket(); poster()
    print("done yui")
