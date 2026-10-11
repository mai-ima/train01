"""Shop/inn/shrine/depot/goods signs and menus (all fictional names)."""
import sys
sys.argv = sys.argv[:1]
from make_textures2 import *
from PIL import Image, ImageDraw
OUTD = "/home/claude/station/tex"


def board(W, H, base=(206, 184, 140), edge=(60, 40, 22)):
    im = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(3)
    for y in range(0, H, 6):
        v = rng.integers(-10, 10)
        d.line([0, y, W, y], fill=tuple(int(np.clip(c + v, 0, 255)) for c in base), width=3)
    d.rectangle([0, 0, W - 1, H - 1], outline=edge, width=max(6, W // 120))
    return im, d


def shop_sign():
    W, H = 1800, 560
    im, d = board(W, H, (22, 44, 36), (200, 190, 150))
    d.text((W // 2, 215), "よろず　穂波屋", font=font("Serif", "Black", 230), fill=(240, 232, 200), anchor="mm")
    d.text((W // 2, 430), "たばこ　雑貨　食料品　酒類", font=font("Sans", "Medium", 100), fill=(220, 210, 170), anchor="mm")
    age(im, rust=0.1, yellow=0.1, seed=21).save(f"{OUTD}/shop_sign.png")


def menu_shokudo():
    W, H = 900, 1300
    im, d = board(W, H, (232, 222, 190), (70, 40, 20))
    d.text((W // 2, 120), "お品書き", font=font("Serif", "Black", 120), fill=(120, 20, 16), anchor="mm")
    d.line([80, 200, W - 80, 200], fill=(120, 20, 16), width=6)
    items = [("中華そば", 90), ("ワンタンめん", 110), ("親子丼", 120), ("カレーライス", 100), ("かけうどん", 70), ("おでん（一皿）", 40), ("焼き魚定食", 150), ("ラムネ", 20), ("お茶", 10)]
    for k, (n, p) in enumerate(items):
        y = 285 + k * 110
        d.text((100, y), n, font=font("Serif", "Bold", 64), fill=(30, 26, 20), anchor="lm")
        d.text((W - 100, y), f"{p}円", font=font("Serif", "Bold", 64), fill=(30, 26, 20), anchor="rm")
        d.line([100, y + 48, W - 100, y + 48], fill=(150, 120, 90), width=2)
    d.text((W // 2, H - 80), "※ 本日 米飯は 国産米です", font=font("Sans", "Medium", 40), fill=(80, 60, 40), anchor="mm")
    age(im, rust=0.0, yellow=0.3, seed=22).save(f"{OUTD}/menu_shokudo.png")


def inn_tariff():
    W, H = 800, 1000
    im, d = board(W, H, (40, 28, 20), (170, 140, 80))
    d.text((W // 2, 110), "旅館 みどり屋", font=font("Serif", "Black", 100), fill=(236, 220, 170), anchor="mm")
    d.text((W // 2, 210), "御宿泊料金表", font=font("Serif", "Bold", 64), fill=(220, 200, 150), anchor="mm")
    rows = [("一泊二食付", "1,200円"), ("一泊朝食付", "800円"), ("素泊まり", "500円"), ("御休憩", "150円"), ("団体割引あり", "")]
    for k, (a, b) in enumerate(rows):
        y = 340 + k * 120
        d.text((70, y), a, font=font("Serif", "Bold", 58), fill=(236, 226, 190), anchor="lm")
        d.text((W - 70, y), b, font=font("Serif", "Bold", 58), fill=(236, 226, 190), anchor="rm")
        d.line([70, y + 52, W - 70, y + 52], fill=(150, 130, 90), width=2)
    d.text((W // 2, H - 90), "電話　穂波野 三番", font=font("Sans", "Medium", 48), fill=(210, 190, 140), anchor="mm")
    age(im, rust=0.0, yellow=0.1, seed=23).save(f"{OUTD}/inn_tariff.png")


def shrine_plaque():
    W, H = 640, 800
    im, d = board(W, H, (30, 26, 22), (190, 150, 60))
    d.text((W // 2, 250), "穂波野", font=font("Serif", "Black", 190), fill=(230, 210, 120), anchor="mm")
    d.text((W // 2, 520), "神社", font=font("Serif", "Black", 220), fill=(230, 210, 120), anchor="mm")
    age(im, rust=0.0, yellow=0.1, seed=24).save(f"{OUTD}/shrine_plaque.png")


def depot_sign():
    W, H = 1800, 520
    im, d = board(W, H, (236, 236, 228), (30, 30, 30))
    d.text((W // 2, 200), "穂波野機関区", font=font("Sans", "Black", 260), fill=(18, 18, 18), anchor="mm")
    d.text((W // 2, 420), "HONAMINO  LOCOMOTIVE  DEPOT", font=font("Sans", "Bold", 70), fill=(60, 60, 60), anchor="mm")
    age(im, rust=0.4, yellow=0.1, seed=25).save(f"{OUTD}/depot_sign.png")


def keep_out():
    W, H = 700, 900
    im = Image.new("RGB", (W, H), (230, 230, 224))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 230], fill=(190, 36, 30))
    d.text((W // 2, 120), "立入禁止", font=font("Sans", "Black", 160), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 420), "構内", font=font("Sans", "Black", 190), fill=(20, 20, 20), anchor="mm")
    d.text((W // 2, 640), "関係者以外\nはいる\nべからず", font=font("Sans", "Bold", 90), fill=(30, 30, 30), anchor="mm", align="center")
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30), width=14)
    age(im, rust=0.5, yellow=0.1, seed=26).save(f"{OUTD}/keep_out.png")


def fire_sign():
    W, H = 600, 600
    im = Image.new("RGB", (W, H), (240, 238, 230))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 170], fill=(190, 36, 30))
    d.text((W // 2, 90), "火気厳禁", font=font("Sans", "Black", 120), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 360), "油 · 薪 · 石炭\n取扱注意", font=font("Sans", "Bold", 80), fill=(30, 30, 30), anchor="mm", align="center")
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30), width=12)
    age(im, rust=0.5, yellow=0.1, seed=27).save(f"{OUTD}/fire_sign.png")


def goods_sign():
    W, H = 1800, 420
    im, d = board(W, H, (30, 28, 24), (200, 180, 120))
    d.text((W // 2, 150), "穂波野駅　貨物取扱所", font=font("Serif", "Black", 190), fill=(236, 226, 190), anchor="mm")
    d.text((W // 2, 330), "小荷物・米穀・肥料 受付", font=font("Sans", "Medium", 80), fill=(210, 195, 150), anchor="mm")
    age(im, rust=0.1, yellow=0.1, seed=28).save(f"{OUTD}/goods_sign.png")


def price_board():
    W, H = 700, 900
    im, d = board(W, H, (236, 232, 214), (60, 50, 30))
    d.text((W // 2, 90), "本日の品", font=font("Serif", "Black", 100), fill=(30, 40, 90), anchor="mm")
    items = [("米（一升）", "160円"), ("味噌（百匁）", "35円"), ("醤油（一升）", "230円"), ("砂糖（一斤）", "110円"), ("豆腐（一丁）", "15円"), ("石鹸", "30円"), ("煙草", "70円"), ("ラムネ", "20円")]
    for k, (a, b) in enumerate(items):
        y = 200 + k * 85
        d.text((60, y), a, font=font("Serif", "Bold", 50), fill=(20, 20, 20), anchor="lm")
        d.text((W - 60, y), b, font=font("Serif", "Bold", 50), fill=(20, 20, 20), anchor="rm")
        d.line([60, y + 36, W - 60, y + 36], fill=(150, 140, 110), width=2)
    age(im, rust=0.0, yellow=0.3, seed=29).save(f"{OUTD}/price_board.png")


def toilet_signs():
    W, H = 900, 300
    im, d = board(W, H, (236, 236, 228), (30, 30, 30))
    d.text((W // 2, H // 2), "便　所", font=font("Sans", "Black", 190), fill=(20, 20, 20), anchor="mm")
    age(im, rust=0.2, yellow=0.2, seed=30).save(f"{OUTD}/benjo.png")


if __name__ == "__main__":
    shop_sign(); menu_shokudo(); inn_tariff(); shrine_plaque(); depot_sign(); keep_out(); fire_sign(); goods_sign(); price_board(); toilet_signs()
    print("ok")
