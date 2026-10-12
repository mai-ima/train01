import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Dense town around a kit station: shopfront rows (signboard architecture), billboards, vending machines, fences, poster boards."""
import os, math, random
from common import *
import lib, props
from props import G, face_plane

KIT = f"{_R}/tex/kit"


def img(sid, name):
    p = f"kit/{sid}_{name}.png"
    return p if os.path.exists(f"{_R}/tex/{p}") else None


def shopfront(sid, x, y, w, d, floors, wall, sign, face='S', name="sf", roof="gable", poster=None, rng=None):
    """Two-sided-facade shop: front faces `face` ('S' -> -y). Ground floor glass + awning + signboard; upper floor windows."""
    g = G(f"{name}", "Buildings")
    rng = rng or random.Random(1)
    h1, h2 = 3.2, 2.9
    H = h1 + (h2 if floors > 1 else 0)
    wl = g.a(wall, bevel=0.01)
    wl.box(x, x + w, y, y + d, 0.0, H)
    fy = y if face == 'S' else y + d
    sgn = -1 if face == 'S' else 1
    # ground floor shop window + door
    dw = 1.0
    g.a("dark_glass").box(x + 0.4, x + w - dw - 0.9, fy + sgn * 0.02 - 0.01, fy + sgn * 0.02 + 0.01 + (0.0), 0.6, 2.4) if False else None
    gl = g.a("glass")
    gl.box(x + 0.4, x + w - dw - 0.9, fy + sgn * 0.03 - 0.005, fy + sgn * 0.03 + 0.005, 0.6, 2.4)
    fr = g.a("wood_dark", bevel=0.005)
    for xx in np.linspace(x + 0.4, x + w - dw - 0.9, 4):
        fr.box(xx - 0.03, xx + 0.03, fy + sgn * 0.06 - 0.03, fy + sgn * 0.06 + 0.03, 0.6, 2.4)
    fr.box(x + w - dw - 0.5, x + w - 0.5, fy + sgn * 0.06 - 0.04, fy + sgn * 0.06 + 0.04, 0.0, 2.2)
    g.a("dark_glass").box(x + w - dw - 0.4, x + w - 0.6, fy + sgn * 0.075 - 0.01, fy + sgn * 0.075 + 0.01, 0.2, 2.1)
    # awning
    ay0, ay1 = fy, fy + sgn * 1.3
    g.a("noren" if rng.random() < 0.5 else "tin").quad_pts((x + 0.1, ay0, 2.7), (x + w - 0.1, ay0, 2.7), (x + w - 0.1, ay1, 2.3), (x + 0.1, ay1, 2.3))
    # signboard
    if sign:
        face_plane(f"{name}_sign", sign, face, x + w / 2, fy + sgn * 0.08, 2.9 - 0.0, min(w - 0.4, 3.6), h=min(w - 0.4, 3.6) * 0.28, off=0.0)
    if floors > 1:
        for xx in np.linspace(x + 1.0, x + w - 1.0, max(2, int(w / 2.4))):
            g.a("glass").box(xx - 0.5, xx + 0.5, fy + sgn * 0.03 - 0.005, fy + sgn * 0.03 + 0.005, h1 + 0.8, h1 + 2.1)
            fr.box(xx - 0.55, xx + 0.55, fy + sgn * 0.06 - 0.03, fy + sgn * 0.06 + 0.03, h1 + 0.75, h1 + 0.85)
            fr.box(xx - 0.55, xx + 0.55, fy + sgn * 0.06 - 0.03, fy + sgn * 0.06 + 0.03, h1 + 2.1, h1 + 2.2)
    if roof == "gable":
        props.gable_roof(g.a("roof"), wl, x, x + w, y, y + d, H, 1.4 + 0.1 * d, ov=0.4, gov=0.25)
    else:
        g.a("concrete", bevel=0.01).box(x - 0.1, x + w + 0.1, y - 0.1, y + d + 0.1, H, H + 0.2)
        g.a("concrete").box(x - 0.1, x + w + 0.1, fy + sgn * 0.1 - 0.1, fy + sgn * 0.1 + 0.1, H + 0.2, H + 1.2)
        if sign and floors > 1:   # rooftop signboard
            face_plane(f"{name}_roof", sign, face, x + w / 2, fy + sgn * 0.25, H + 0.25, min(w, 4.2), h=min(w, 4.2) * 0.28, off=0.0)
    if poster:
        face_plane(f"{name}_post", poster, face, x + 0.9, fy + sgn * 0.09, 1.0, 0.75, h=1.06, off=0.0)
    g.build()
    props.FOOT.append((x - 1, x + w + 1, y - 2, y + d + 1))


def billboard(sid, x, y, imgname, face='S', name="bb"):
    g = G(name, "Props")
    for dx in (-1.4, 1.4):
        g.a("wood_dark", bevel=0.01).box(x + dx - 0.07, x + dx + 0.07, y - 0.07, y + 0.07, 0.0, 3.4)
    g.a("wood_dark").box(x - 1.6, x + 1.6, y - 0.05, y + 0.05, 1.1, 3.3)
    g.build()
    if imgname:
        face_plane(name, imgname, face, x, y + (0.07 if face == 'N' else -0.07), 1.18, 3.0, h=1.0 * 3.0 / 2.7, off=0.0)


def vending(x, y, face='S', name="vend", col="tr_red"):
    g = G(name, "Props")
    g.a(col).box(x - 0.4, x + 0.4, y - 0.3, y + 0.3, 0.0, 1.75)
    g.a("lamp_glow").box(x - 0.34, x + 0.34, y - 0.31 if face == 'S' else y + 0.3, y - 0.30 if face == 'S' else y + 0.31, 0.9, 1.6)
    g.build()


def fence(x0, x1, y, h=1.1, name="fence"):
    g = G(name, "Props")
    for xx in np.arange(x0, x1 + 0.1, 2.0):
        g.a("wood_dark").box(xx - 0.05, xx + 0.05, y - 0.05, y + 0.05, 0, h)
    g.a("wood").box(x0, x1, y - 0.02, y + 0.02, h - 0.35, h - 0.15)
    g.a("wood").box(x0, x1, y - 0.02, y + 0.02, h - 0.8, h - 0.6)
    g.build()


def dense_row(sid, st, rng, y, xr, face, density, kinds, name):
    """Pack shopfronts / houses along a row. density 0..1 -> gap size."""
    x = xr[0]
    k = 0
    imgs_sign = [n for n in ("sign_shokudo", "sign_shoten", "sign_ryokan", "sign_riyo", "sign_kusuri", "sign_sakaya") if img(sid, n)]
    posters = [f"poster{i}" for i in range(4)]
    while x < xr[1]:
        w = rng.choice([5.0, 6.0, 7.0, 8.0, 9.0]) if density > 0.5 else rng.choice([7.0, 8.5, 10.0])
        kind = rng.choice(kinds)
        d = rng.uniform(6.5, 9.0)
        sign = img(sid, rng.choice(imgs_sign)) if imgs_sign else None
        pst = img(sid, rng.choice(posters))
        wall = rng.choice(["wall", "wall", "plasterw", "wood", "brick"] if density < 0.7 else ["plasterw", "brick", "concrete", "wall"])
        floors = 2 if (density > 0.6 and rng.random() < 0.7) else 1
        shopfront(sid, x, y, w, d, floors, wall, sign, face=face, name=f"{name}{k}", roof="gable" if density < 0.7 or rng.random() < 0.5 else "flat", poster=pst, rng=rng)
        if rng.random() < 0.25:
            vending(x + rng.uniform(0.6, w - 0.6), y - 0.6 if face == 'S' else y + d + 0.6, face, name=f"{name}v{k}", col=rng.choice(["tr_red", "tr_green", "cart_blue"]))
        gap = rng.uniform(0.4, 1.8) if density > 0.6 else rng.uniform(1.5, 6.0)
        x += w + gap
        k += 1


def decorate_platform(sid, x0, x1, y_back, rng, ks=None):
    """Timetable / notice / map boards on posts along the platform back."""
    for k, nm in enumerate(("timetable", "map", "notice")):
        if ks is not None and k not in ks:
            continue
        im = img(sid, nm)
        if im:
            xc = x0 + (x1 - x0) * (0.35 + 0.18 * k)
            g = G(f"pb_{sid}_{k}", "Props")
            for dx in (-0.5, 0.5):
                g.a("wood_dark").box(xc + dx - 0.04, xc + dx + 0.04, y_back - 0.9, y_back - 0.8, Z_PLAT, Z_PLAT + 1.6)
            g.a("wood_dark").box(xc - 0.6, xc + 0.6, y_back - 0.9, y_back - 0.82, Z_PLAT + 0.5, Z_PLAT + 1.6)
            g.build()
            iw = 0.9 if nm != "map" else 1.0
            face_plane(f"pbi_{sid}_{k}", im, 'S', xc, y_back - 0.9 - 0.012, Z_PLAT + 0.55, iw, h=iw * (1.1 if nm != "map" else 0.7), off=0.0)
