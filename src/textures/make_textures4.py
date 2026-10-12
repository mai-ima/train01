import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Railway-company mark (fictional abbreviation 'JPR' = 日本鉄道公社), headmark and first-generation emblem plaque.
All artwork original; the company, abbreviation and marks are fictional."""
import sys
sys.argv = sys.argv[:1]
from make_textures2 import *
from PIL import Image, ImageDraw, ImageFilter

OUTD = f"{_R}/tex"
BLUE = (16, 54, 112, 255)
WHITE = (240, 238, 228, 255)
RED = (196, 40, 32, 255)


def logo_new():
    """Mark for the national-railway era: sheared heavy 'JNR' on a blue capsule with a red/white rail motif.
    Only the mark is new - the organisation name is unchanged. Everything sits well inside the border (no edge contact)."""
    S = 1200
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 60, 320, S - 60, 880
    d.rounded_rectangle([x0, y0, x1, y1], radius=160, fill=BLUE)
    d.rounded_rectangle([x0 + 26, y0 + 26, x1 - 26, y1 - 26], radius=134, outline=WHITE, width=14)
    # wordmark, sheared; measured so it keeps >=90px clear of the inner border
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.text((S // 2, 540), "JNR", font=font("Sans", "Black", 300), fill=WHITE, anchor="mm")
    sh = 0.20
    lay = lay.transform(lay.size, Image.AFFINE, (1, sh, -sh * 540, 0, 1, 0), resample=Image.BICUBIC)
    bb = lay.getbbox()
    assert bb[0] > x0 + 26 + 90 and bb[2] < x1 - 26 - 90, bb
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    # twin rails + sleepers, centred, inside the border with a wide margin
    ry0, ry1 = 690, 790
    for sgn in (-1, 1):
        d.polygon([(S // 2 + sgn * 36, ry0), (S // 2 + sgn * 50, ry0), (S // 2 + sgn * 250, ry1), (S // 2 + sgn * 214, ry1)], fill=WHITE)
    for k in range(4):
        t = (k + 0.5) / 4
        yy = ry0 + 6 + t * (ry1 - ry0 - 16)
        half = 52 + t * 200
        d.rectangle([S // 2 - half, yy, S // 2 + half, yy + 8], fill=RED)
    im = im.resize((600, 600), Image.LANCZOS)
    im.save(f"{OUTD}/logo_new.png")


def headmark():
    """Circular enamel headmark carrying the first-generation emblem (rice ears over rails)."""
    S = 800
    base = Image.open(f"{OUTD}/emblem.png").convert("RGBA").resize((430, 430), Image.LANCZOS)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([6, 6, S - 6, S - 6], fill=(30, 30, 30, 255))
    d.ellipse([26, 26, S - 26, S - 26], fill=(214, 168, 54, 255))          # brass rim
    d.ellipse([70, 70, S - 70, S - 70], fill=(236, 230, 208, 255))
    d.ellipse([86, 86, S - 86, S - 86], outline=(30, 90, 60, 255), width=10)
    im.alpha_composite(base, ((S - 430) // 2, 150))
    d = ImageDraw.Draw(im)
    d.text((S // 2, 618), "ほなみの", font=font("Sans", "Black", 50), fill=(30, 90, 60, 255), anchor="mm")
    a = np.array(im).astype(float)
    n = noise_layer((S, S), 9, 4) * 0.5 + noise_layer((S, S), 30, 5) * 0.5
    a[..., :3] *= (0.78 + 0.28 * n)[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").resize((512, 512), Image.LANCZOS).save(f"{OUTD}/headmark.png")


def emblem_first():
    """Framed, aged display of the first-generation emblem for the station waiting room."""
    W, H = 640, 800
    im = Image.new("RGB", (W, H), (70, 46, 28))
    d = ImageDraw.Draw(im)
    d.rectangle([22, 22, W - 22, H - 22], outline=(30, 20, 12), width=6)
    d.rectangle([54, 54, W - 54, H - 54], fill=(224, 214, 186))
    em = Image.open(f"{OUTD}/emblem.png").convert("RGBA").resize((400, 400), Image.LANCZOS)
    im.paste(em, ((W - 400) // 2, 120), em)
    d.text((W // 2, 590), "初 代 局 章", font=font("Serif", "Bold", 64), fill=(40, 40, 36), anchor="mm")
    d.text((W // 2, 660), "穂波野鉄道管理局  制定", font=font("Serif", "Medium", 34), fill=(60, 56, 48), anchor="mm")
    d.rectangle([W // 2 - 190, 706, W // 2 + 190, 746], fill=(150, 112, 40))
    d.text((W // 2, 726), "— 保存 —", font=font("Sans", "Bold", 28), fill=(40, 28, 10), anchor="mm")
    im = age(im, rust=0.1, yellow=0.25, seed=12, fade=0.1)
    im.save(f"{OUTD}/emblem_first.png")


if __name__ == "__main__":
    logo_new(); headmark(); emblem_first()
    print("ok")
