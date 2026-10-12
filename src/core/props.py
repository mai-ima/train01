"""Street furniture, vehicles on the road, houses, poles, signs - everything around the station (fictional Honamino)."""
from common import *
import lib
from PIL import Image

TEXD = lib.TEX if hasattr(lib, "TEX") else "/home/claude/station/tex"
_MATS = {}
FOOT = []   # building footprints (x0,x1,y0,y1) for vegetation exclusion


def pm(key):
    """Props materials (lazy)."""
    if key in _MATS:
        return _MATS[key]
    c = {
        "bike_black": lambda: lib.mat_paint("pb_bike", (0.025, 0.027, 0.03), rough=0.35, rust=0.25, metal=0.3),
        "bike_green": lambda: lib.mat_paint("pb_bikeg", (0.05, 0.11, 0.07), rough=0.35, rust=0.3, metal=0.2),
        "cart_blue": lambda: lib.mat_paint("pb_cartb", (0.10, 0.20, 0.30), rough=0.5, rust=0.45),
        "tr_green": lambda: lib.mat_paint("pb_trg", (0.13, 0.25, 0.19), rough=0.45, rust=0.4),
        "tr_cream": lambda: lib.mat_paint("pb_trc", (0.72, 0.66, 0.50), rough=0.5, rust=0.35),
        "tr_red": lambda: lib.mat_paint("pb_trr", (0.42, 0.07, 0.05), rough=0.45, rust=0.4),
        "tr_grey": lambda: lib.mat_paint("pb_trgy", (0.36, 0.38, 0.38), rough=0.5, rust=0.4),
        "plaster": lambda: lib.mat_plaster("pb_plaster", (0.80, 0.77, 0.66), dirt=0.8),
        "plaster2": lambda: lib.mat_plaster("pb_plaster2", (0.66, 0.60, 0.48), dirt=0.9),
        "kawara": lambda: lib.mat_kawara("pb_kawara"),
        "pole": lambda: lib.mat_wood("pb_pole", (0.085, 0.058, 0.04), rough=0.8, along='Z', weather=0.8),
        "pole_new": lambda: lib.mat_wood("pb_pole2", (0.20, 0.15, 0.10), rough=0.8, along='Z', weather=0.7),
        "wire": lambda: lib.mat_plain("pb_wire", (0.02, 0.02, 0.022), rough=0.5, metal=0.3),
        "stone_lantern": lambda: lib.mat_plain("pb_stone", (0.38, 0.37, 0.33), rough=0.9),
        "shoji": lambda: lib.mat_plain("pb_shoji", (0.80, 0.78, 0.68), rough=0.9),
        "noren": lambda: lib.mat_plain("pb_noren", (0.10, 0.14, 0.26), rough=0.9),
        "crate": lambda: lib.mat_wood("pb_crate", (0.30, 0.20, 0.11), rough=0.8, along='X', weather=0.7),
        "bottle": lambda: lib.mat_plain("pb_bottle", (0.10, 0.28, 0.12), rough=0.2),
        "primer": lambda: lib.mat_paint("pb_primer", (0.30, 0.12, 0.08), rough=0.7, rust=0.5),
        "bag": lambda: lib.mat_plain("pb_bag", (0.50, 0.40, 0.24), rough=0.95),
        "milk": lambda: lib.mat_plain("pb_milk", (0.55, 0.57, 0.58), rough=0.4, metal=0.8),
    }[key]
    _MATS[key] = c()
    return _MATS[key]


def tex_size(img):
    try:
        return Image.open(f"{TEXD}/{img}").size
    except Exception:
        return (1, 1)


class G:
    """Group of accumulators keyed by material, built together."""
    def __init__(self, name, col="Props"):
        self.name, self.col, self.d = name, col, {}

    def a(self, key, mat=None, bevel=0.0, smooth=False):
        k = (key, bevel, smooth)
        if k not in self.d:
            if mat is None:
                mat = M[key] if key in M else pm(key)
            self.d[k] = Acc(f"{self.name}_{key}", mat, self.col, bevel=bevel, smooth=smooth)
        return self.d[k]

    def build(self):
        for acc in self.d.values():
            acc.build()


def face_plane(name, img, face, cx, cy, z0, w, h=None, off=0.0, col="Props", kw=None, alpha=False):
    """Image plane at (cx,cy) facing direction face in {'N','S','E','W'} (N=+y)."""
    if h is None:
        iw, ih = tex_size(img)
        h = w * ih / iw
    z1 = z0 + h
    hw = w / 2
    if face == 'N':
        c = [(cx + hw, cy + off, z0), (cx - hw, cy + off, z0), (cx - hw, cy + off, z1), (cx + hw, cy + off, z1)]
    elif face == 'S':
        c = [(cx - hw, cy - off, z0), (cx + hw, cy - off, z0), (cx + hw, cy - off, z1), (cx - hw, cy - off, z1)]
    elif face == 'E':
        c = [(cx + off, cy - hw, z0), (cx + off, cy + hw, z0), (cx + off, cy + hw, z1), (cx + off, cy - hw, z1)]
    else:
        c = [(cx - off, cy + hw, z0), (cx - off, cy - hw, z0), (cx - off, cy - hw, z1), (cx - off, cy + hw, z1)]
    return lib.image_plane(name, c, img, kw or {"rough": 0.55, "spec": 0.2}, col=col, alpha=alpha)


def XF(x, y, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return lambda p: (x + p[0] * c - p[1] * s, y + p[0] * s + p[1] * c, p[2])


# =================================================================== bicycles
def bike(g, x, y, yaw, kind=0, z0=0.016):
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, c + z0))
    frame = g.a("bike_black" if kind != 1 else "bike_green", bevel=0.0)
    chrome = g.a("chrome")
    rub = g.a("rubber")
    ax = (-math.sin(yaw), math.cos(yaw), 0.0)
    R = 0.34
    for xc in (-0.55, 0.55):
        rub.torus(P(xc, 0, R), ax, R, 0.022, segR=24, segr=6)
        chrome.torus(P(xc, 0, R), ax, R - 0.03, 0.006, segR=24, segr=4)
        chrome.cyl(P(xc, -0.05, R), P(xc, 0.05, R), 0.025, seg=8)
        for k in range(6):
            a = math.pi * k / 6
            chrome.cyl(P(xc + math.cos(a) * (R - 0.03), 0, R + math.sin(a) * (R - 0.03)),
                       P(xc - math.cos(a) * (R - 0.03), 0, R - math.sin(a) * (R - 0.03)), 0.003, seg=3, caps=False)
    fr = frame
    bb, seat, head = P(-0.05, 0, 0.30), P(-0.20, 0, 0.93), P(0.42, 0, 0.88)
    rh, fh = P(-0.55, 0, R), P(0.55, 0, R)
    for a, b in ((bb, seat), (seat, head), (bb, head), (rh, seat), (rh, bb), (head, fh)):
        fr.cyl(a, b, 0.016, seg=6)
    fr.cyl(P(0.40, 0, 0.98), P(0.44, 0, 0.82), 0.019, seg=6)
    fr.cyl(P(0.42, -0.30, 1.0), P(0.42, 0.30, 1.0), 0.012, seg=6)        # handlebar
    chrome.cyl(P(0.42, 0.30, 1.0), P(0.42, 0.36, 1.0), 0.016, seg=6)
    chrome.cyl(P(0.42, -0.30, 1.0), P(0.42, -0.36, 1.0), 0.016, seg=6)
    sad = g.a("leather")
    sad.sbox(P(-0.30, 0, 0.97), P(-0.06, 0, 0.97), 0.16, 0.05)
    fr.cyl(seat, P(-0.20, 0, 0.99), 0.012, seg=6)
    # pedals / crank / chain guard
    chrome.cyl(P(-0.05, -0.09, 0.30), P(-0.05, 0.09, 0.30), 0.012, seg=6)
    chrome.cyl(P(-0.05, 0.0, 0.30), P(0.0, 0.0, 0.18), 0.012, seg=6)
    fr.cyl(P(-0.05, 0.05, 0.30), P(-0.55, 0.05, R + 0.03), 0.02, seg=4, caps=False)
    # carrier + front basket (kind 0/2) + lamp
    if kind in (0, 2):
        fr.sbox(P(-0.78, 0, 0.62), P(-0.30, 0, 0.62), 0.22, 0.015)
        fr.cyl(P(-0.30, 0, 0.62), P(-0.55, 0.0, R), 0.006, seg=4)
        if kind == 2:
            g.a("bag", bevel=0.02).boxc(*T((-0.55, 0.0, 0.62 + z0 + 0.14))[:2], T((0, 0, 0.62 + z0 + 0.14))[2], 0.55, 0.3, 0.22, rz=yaw)
        else:
            bk = g.a("chrome")
            bk.sbox(P(0.56, -0.18, 0.88), P(0.56, 0.18, 0.88), 0.01, 0.02)
            bk.sbox(P(0.56, -0.18, 0.88), P(0.56, -0.18, 0.88 + 0.22), 0.012, 0.012)
    g.a("chrome").sphere(P(0.60, 0, 1.0), (0.04, 0.04, 0.045), seg=8, rings=5)
    # kickstand lean: prop under rear
    fr.cyl(P(-0.50, 0, 0.30), P(-0.40, 0.18, 0.0), 0.007, seg=4)


# =================================================================== road vehicles
def wheel_v(g, T, cx, cy, r, w, z0, side):
    ax = (-math.sin(T[2]), math.cos(T[2]), 0.0) if False else None


def road_wheel(g, P, yaw, xc, yc, r, w=0.2, tread=True):
    rub, st = g.a("rubber"), g.a("tr_grey")
    p0, p1 = P(xc, yc - w / 2, r), P(xc, yc + w / 2, r)
    rub.cyl(p0, p1, r, seg=22)
    st.cyl(P(xc, yc - w / 2 - 0.004, r), P(xc, yc + w / 2 + 0.004, r), r * 0.58, seg=14)
    g.a("chrome").cyl(P(xc, yc - w / 2 - 0.02, r), P(xc, yc + w / 2 + 0.02, r), r * 0.13, seg=8)
    for k in range(6):
        a = 2 * math.pi * k / 6
        g.a("iron_black").sbox(P(xc, yc - w / 2 - 0.01, r), P(xc + math.cos(a) * r * 0.55, yc - w / 2 - 0.01, r + math.sin(a) * r * 0.55), 0.018, 0.012)


def bonnet_truck(x, y, yaw, load="rice", name="truck", body="tr_green", z0=0.016):
    """Generic 1950s-60s Japanese 2-tonne bonnet truck (original design)."""
    g = G(name, "Vehicles")
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, c + z0))
    ax = (-math.sin(yaw), math.cos(yaw), 0.0)
    b = g.a(body, bevel=0.03)
    bl = g.a("tr_cream", bevel=0.02)
    dk = g.a("iron_black", bevel=0.01)
    wd = g.a("wood_dark", bevel=0.01)
    # chassis
    for s in (-1, 1):
        dk.sbox(P(-3.4, s * 0.45, 0.62), P(2.0, s * 0.45, 0.62), 0.10, 0.20)
    dk.sbox(P(2.0, -0.62, 0.52), P(2.0, 0.62, 0.52), 0.18, 0.14)           # front bumper (rust-painted)
    dk.sbox(P(-3.45, -0.8, 0.65), P(-3.45, 0.8, 0.65), 0.10, 0.18)
    # axles + wheels
    for xc in (1.55, -1.55):
        dk.cyl(P(xc, -0.78, 0.38), P(xc, 0.78, 0.38), 0.05, seg=8)
        for s in (-1, 1):
            road_wheel(g, P, yaw, xc, s * 0.82, 0.38, 0.22)
    # real fenders as sloped boxes
    for s in (-1, 1):
        b.sbox(P(0.95, s * 0.92, 0.86), P(2.05, s * 0.92, 0.80), 0.34, 0.05)
        b.sbox(P(2.05, s * 0.92, 0.80), P(2.12, s * 0.92, 0.62), 0.34, 0.05)
        b.sbox(P(1.0, s * 1.08, 0.80), P(2.0, s * 1.08, 0.74), 0.06, 0.20)
    # bonnet
    b.boxc(*T((1.35, 0, 1.20 + z0)), 1.5, 1.18, 0.62, rz=yaw)
    b.boxc(*T((1.35, 0, 1.55 + z0)), 1.3, 0.96, 0.10, rz=yaw)
    # grille + lamps
    gx = 2.12
    g.a("chrome").boxc(*T((gx, 0, 1.16 + z0)), 0.04, 0.78, 0.50, rz=yaw)
    for k in range(-5, 6):
        dk.sbox(P(gx + 0.03, k * 0.062, 0.93), P(gx + 0.03, k * 0.062, 1.40), 0.018, 0.016)
    for s in (-1, 1):
        g.a("chrome").sphere(P(1.95, s * 0.72, 1.40), (0.14, 0.14, 0.14), seg=12, rings=7)
        g.a("lamp_glow").sphere(P(2.03, s * 0.72, 1.40), (0.06, 0.1, 0.1), seg=10, rings=6)
    # cab
    bl.boxc(*T((0.15, 0, 1.78 + z0)), 1.30, 1.74, 1.10, rz=yaw)
    bl.boxc(*T((0.0, 0, 1.18 + z0 + 0.0)), 1.10, 1.74, 0.45, rz=yaw)
    b.boxc(*T((0.15, 0, 2.38 + z0)), 1.50, 1.90, 0.07, rz=yaw)             # roof
    # cab glazing (windscreen forwards, sides, rear)
    gl = g.a("dark_glass")
    gl.sbox(P(0.82, -0.62, 1.95), P(0.82, 0.62, 1.95), 0.04, 0.55)       # windscreen at front of cab (x~0.8)
    for s in (-1, 1):
        gl.sbox(P(0.45, s * 0.89, 1.95), P(-0.25, s * 0.89, 1.95), 0.03, 0.55)
        wd_k = g.a("wood_dark")
        wd_k.sbox(P(0.0, s * 0.91, 1.60), P(0.0, s * 0.91, 2.24), 0.03, 0.02)
    gl.sbox(P(-0.5, -0.5, 1.95), P(-0.5, 0.5, 1.95), 0.04, 0.45)
    # steering wheel visible
    dk.torus(P(0.5, 0.35, 1.55), (math.cos(yaw) * 0.6, math.sin(yaw) * 0.6, 0.8), 0.17, 0.015, segR=16, segr=5) if False else None
    # load bed
    wd.box(*[0] * 6) if False else None
    bed = g.a("crate", bevel=0.008)
    bed.boxc(*T((-1.95, 0, 0.82 + z0)), 2.8, 2.04, 0.10, rz=yaw)
    # side boards: rotate offsets
    for s in (-1, 1):
        sx0, sx1 = P(-3.35, s * 1.0, 0.92), P(-0.55, s * 1.0, 0.92)
        bed.sbox(sx0, sx1, 0.05, 0.38)
    bed.sbox(P(-3.38, -1.0, 0.92), P(-3.38, 1.0, 0.92), 0.05, 0.38)
    bed.sbox(P(-0.55, -1.0, 0.92), P(-0.55, 1.0, 0.92), 0.05, 0.60)
    for k in range(8):
        xx = -3.3 + k * 0.4
        for s in (-1, 1):
            dk.sbox(P(xx, s * 1.03, 0.75), P(xx, s * 1.03, 1.12), 0.04, 0.03)
    # load
    sk = g.a("bag", bevel=0.05)
    rng = random.Random(int(abs(x) * 7 + abs(y) * 3))
    if load == "rice":
        for layer in range(3):
            for i in range(4):
                for j in range(3):
                    px = -3.0 + i * 0.7 + (0.35 if layer % 2 else 0.0) + rng.uniform(-0.03, 0.03)
                    py = -0.62 + j * 0.62 + rng.uniform(-0.03, 0.03) + (0.12 if layer == 1 else 0)
                    if layer == 2 and (i + j) % 3 == 0:
                        continue
                    sk.boxc(*T((px, py, 1.14 + layer * 0.27 + z0)), 0.64, 0.38, 0.27, rz=yaw + rng.uniform(-0.05, 0.05))
        # rope
        g.a("rope", lib.mat_plain("pb_rope", (0.35, 0.28, 0.16), rough=0.9)).sbox(P(-3.2, -1.05, 1.50), P(-0.7, -1.05, 1.50), 0.015, 0.015) if False else None
    elif load == "logs":
        for k in range(3):
            for j in range(5):
                px = -0.9 - k * 0.0
                g.a("pole_new" if False else "wood").cyl(P(-3.2, -0.8 + j * 0.4, 1.12 + (k * 0.15)), P(-0.75, -0.8 + j * 0.4, 1.12 + (k * 0.15)), 0.09, seg=8)
    # mirrors, wipers, tail light, plate, horn
    g.a("chrome").sbox(P(0.7, 0.98, 1.8), P(0.95, 1.2, 1.9), 0.02, 0.1)
    g.a("tr_red").boxc(*T((-3.43, 0.72, 0.98 + z0)), 0.04, 0.12, 0.08, rz=yaw)
    g.a("tr_red").boxc(*T((-3.43, -0.72, 0.98 + z0)), 0.04, 0.12, 0.08, rz=yaw)
    g.build()
    # number plate (decal)
    face = 'E'
    return g


def three_wheeler(x, y, yaw, name="oto3", body="tr_red", z0=0.016):
    g = G(name, "Vehicles")
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, c + z0))
    b = g.a(body, bevel=0.025)
    dk = g.a("iron_black", bevel=0.01)
    # front wheel (single) + fork + handlebar
    road_wheel(g, P, yaw, 1.35, 0.0, 0.31, 0.16)
    dk.cyl(P(1.35, -0.10, 0.31), P(1.15, -0.10, 1.05), 0.022, seg=6)
    dk.cyl(P(1.35, 0.10, 0.31), P(1.15, 0.10, 1.05), 0.022, seg=6)
    dk.cyl(P(1.15, -0.45, 1.12), P(1.15, 0.45, 1.12), 0.016, seg=6)
    b.sbox(P(1.50, 0, 0.62), P(1.0, 0, 0.58), 0.34, 0.05)                      # front mudguard
    g.a("chrome").sphere(P(1.18, 0, 1.0), (0.14, 0.14, 0.14), seg=12, rings=7)
    g.a("lamp_glow").sphere(P(1.28, 0, 1.0), (0.05, 0.09, 0.09), seg=8, rings=5)
    # body: engine hood + seat cab
    b.boxc(*T((0.55, 0, 0.78 + z0)), 0.9, 0.62, 0.42, rz=yaw)
    g.a(body, bevel=0.03).boxc(*T((-0.35, 0, 1.02 + z0)), 0.95, 1.30, 0.50, rz=yaw)
    g.a("leather", bevel=0.03).boxc(*T((-0.25, 0, 1.38 + z0)), 0.55, 1.1, 0.14, rz=yaw)
    for s in (-1, 1):
        dk.sbox(P(-0.05, s * 0.62, 1.4), P(-0.05, s * 0.62, 2.1), 0.04, 0.04)
        dk.sbox(P(-1.0, s * 0.62, 1.4), P(-1.0, s * 0.62, 2.1), 0.04, 0.04)
    g.a("tr_cream", bevel=0.02).boxc(*T((-0.55, 0, 2.14 + z0)), 1.3, 1.45, 0.05, rz=yaw)               # canvas-ish roof (metal)
    g.a("dark_glass").sbox(P(-0.02, -0.5, 1.78), P(-0.02, 0.5, 1.78), 0.025, 0.46)
    # rear axle, wheels, bed
    dk.cyl(P(-1.05, -0.7, 0.32), P(-1.05, 0.7, 0.32), 0.05, seg=8)
    for s in (-1, 1):
        road_wheel(g, P, yaw, -1.05, s * 0.72, 0.32, 0.17)
        b.sbox(P(-0.45, s * 0.85, 0.74), P(-1.65, s * 0.85, 0.74), 0.20, 0.04)
    bed = g.a("crate", bevel=0.008)
    bed.boxc(*T((-2.15, 0, 0.62 + z0)), 1.6, 1.5, 0.07, rz=yaw)
    for s in (-1, 1):
        bed.sbox(P(-2.95, s * 0.75, 0.66), P(-1.35, s * 0.75, 0.66), 0.04, 0.34)
    bed.sbox(P(-2.95, -0.75, 0.66), P(-2.95, 0.75, 0.66), 0.04, 0.34)
    # load: milk cans + crates
    for i in range(3):
        for j in range(2):
            g.a("milk").cyl(P(-1.7 - i * 0.45, -0.3 + j * 0.6, 0.66), P(-1.7 - i * 0.45, -0.3 + j * 0.6, 1.2), 0.17, seg=12)
            g.a("milk").cyl(P(-1.7 - i * 0.45, -0.3 + j * 0.6, 1.2), P(-1.7 - i * 0.45, -0.3 + j * 0.6, 1.28), 0.10, seg=10)
    g.build()


def handcart(x, y, yaw, name="rear_cart", sacks=True, z0=0.016):
    g = G(name, "Vehicles")
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, c + z0))
    wd = g.a("wood_dark", bevel=0.008)
    wd.boxc(*T((0, 0, 0.62 + z0)), 1.9, 1.0, 0.06, rz=yaw)
    for s in (-1, 1):
        wd.sbox(P(-0.95, s * 0.5, 0.68), P(0.95, s * 0.5, 0.68), 0.04, 0.26)
        g.a("iron_black").sbox(P(-1.0, s * 0.42, 0.56), P(2.2, s * 0.30, 0.78), 0.035, 0.035)    # shafts
        road_wheel(g, P, yaw, 0.1, s * 0.66, 0.50, 0.04)
    wd.sbox(P(-0.95, -0.5, 0.68), P(-0.95, 0.5, 0.68), 0.04, 0.26)
    wd.sbox(P(2.2, -0.30, 0.80), P(2.2, 0.30, 0.80), 0.04, 0.04)
    g.a("iron_black").cyl(P(0.1, -0.7, 0.5), P(0.1, 0.7, 0.5), 0.03, seg=8)
    if sacks:
        sk = g.a("bag", bevel=0.05)
        for i in range(2):
            for j in range(2):
                sk.boxc(*T((-0.45 + i * 0.7, -0.25 + j * 0.5, 0.82 + z0)), 0.62, 0.40, 0.26, rz=yaw + 0.05 * (i - j))
        sk.boxc(*T((-0.1, 0.0, 1.07 + z0)), 0.6, 0.4, 0.26, rz=yaw + 0.1)
    g.build()


# =================================================================== poles + wires
def wire(g, p0, p1, sag=0.45, n=9, r=0.006):
    w = g.a("wire")
    prev = None
    for i in range(n + 1):
        t = i / n
        p = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t,
             p0[2] + (p1[2] - p0[2]) * t - sag * 4 * t * (1 - t))
        if prev is not None:
            w.cyl(prev, p, r, seg=4, caps=False)
        prev = p


def pole(g, x, y, h=8.2, arms=((7.5, 0.9, 3),), axis='y', old=False, transformer=False):
    """Wooden pole; arms: (z, half_length, n_insulators). axis = direction of crossarm. returns list of wire anchors [(x,y,z)]"""
    bk = g.a("pole" if old else "pole_new")
    bk.cyl((x, y, 0.0), (x, y, h), 0.17, 0.10, seg=10)
    anchors = []
    for (z, hl, ni) in arms:
        d = (0, 1) if axis == 'y' else (1, 0)
        bk.sbox((x - d[0] * hl, y - d[1] * hl, z), (x + d[0] * hl, y + d[1] * hl, z), 0.08, 0.10)
        # braces
        for s in (-1, 1):
            bk.sbox((x, y, z - 0.75), (x + d[0] * s * 0.7, y + d[1] * s * 0.7, z - 0.05), 0.04, 0.05)
        for k in range(ni):
            off = (k - (ni - 1) / 2) * (2 * hl / max(ni, 1)) * (1.0 if ni > 1 else 0.0)
            ix, iy = x + d[0] * off, y + d[1] * off
            g.a("porcelain").cyl((ix, iy, z + 0.05), (ix, iy, z + 0.16), 0.035, seg=8)
            g.a("porcelain").cyl((ix, iy, z + 0.16), (ix, iy, z + 0.22), 0.022, seg=8)
            anchors.append((ix, iy, z + 0.22))
    if transformer:
        g.a("tr_grey", bevel=0.02).cyl((x + 0.3, y, h - 2.4), (x + 0.3, y, h - 1.35), 0.26, seg=12)
        g.a("iron_black").sbox((x + 0.1, y, h - 1.6), (x + 0.3, y, h - 1.6), 0.05, 0.4)
    # step bolts
    for k in range(8):
        g.a("iron_black").cyl((x - 0.2, y, 2.0 + k * 0.6), (x - 0.12, y, 2.0 + k * 0.6), 0.01, seg=4)
    return anchors


def build_lines():
    g = G("poles", "Props")
    # distribution line along the south side of the forecourt road, then north along the crossing road
    xs = [-112, -82, -52, -27, -4, 24.5, 34]
    y = ROAD_Y - 3.2
    prevA = None
    for i, x in enumerate(xs):
        A = pole(g, x, y, 9.0, arms=((8.3, 1.0, 3),), axis='y', transformer=(i == 3))
        if prevA:
            for a, b in zip(prevA, A):
                wire(g, a, b, sag=0.7, n=10)
        prevA = A
    xx = X_C + 3.6
    A = pole(g, xx, y, 9.0, arms=((8.3, 1.0, 3),), axis='x')
    for a, b in zip(prevA, A):
        wire(g, a, b, sag=0.5, n=6)
    prevA = A
    for yy in (44, 76, 108):
        A = pole(g, xx, yy, 9.0, arms=((8.3, 1.0, 3),), axis='x')
        for a, b in zip(prevA, A):
            wire(g, a, b, sag=0.8, n=10)
        prevA = A
    # telegraph line: south of the yard
    ytel = -22.5
    txs = [-118, -80, -42, -4, 34, 72, 110]
    prevA = None
    for x in txs:
        A = pole(g, x, ytel, 7.4, arms=((6.9, 0.8, 4), (6.1, 0.8, 4)), axis='y', old=True)
        if prevA:
            for a, b in zip(prevA, A):
                wire(g, a, b, sag=0.55, n=10, r=0.005)
        prevA = A
    # pole beside the station building: service drop
    pass
    g.build()


# =================================================================== buildings
def gable_roof(g_roof, g_wall, x0, x1, y0, y1, zw, rise, ov=0.7, gov=0.5, thick=0.14, ridge_x=True):
    ym = (y0 + y1) / 2
    prof = [(y0 - ov, zw - 0.18), (ym, zw + rise), (y1 + ov, zw - 0.18),
            (y1 + ov, zw - 0.18 - thick), (ym, zw + rise - thick - 0.04), (y0 - ov, zw - 0.18 - thick)]
    g_roof.extrude_x(prof, x0 - gov, x1 + gov)
    g_wall.extrude_x([(y0, zw), (ym, zw + rise - 0.12), (y1, zw)], x0, x1)
    # ridge cap
    g_roof.box(x0 - gov, x1 + gov, ym - 0.12, ym + 0.12, zw + rise - 0.06, zw + rise + 0.08)


def window_grid(g, x0, x1, y, z0, z1, ncols, face=-1, depth=0.05, glass="dark_glass", mull=0.03):
    """Row of sliding windows on a wall facing +/-y (face=-1: -y side)."""
    gl, fr = g.a(glass), g.a("wood_dark", bevel=0.004)
    gl.box(x0, x1, y - depth * 0.3, y + depth * 0.3, z0, z1)
    w = (x1 - x0) / ncols
    for i in range(ncols + 1):
        fr.box(x0 + i * w - mull / 2, x0 + i * w + mull / 2, y + face * depth, y + face * 0.0 - 0.0, z0 - 0.02, z1 + 0.02) if face < 0 else \
            fr.box(x0 + i * w - mull / 2, x0 + i * w + mull / 2, y, y + depth, z0 - 0.02, z1 + 0.02)
    nh = max(2, int((z1 - z0) / 0.32))
    for j in range(nh + 1):
        zz = z0 + j * (z1 - z0) / nh
        if face < 0:
            fr.box(x0, x1, y - depth, y, zz - 0.012, zz + 0.012)
        else:
            fr.box(x0, x1, y, y + depth, zz - 0.012, zz + 0.012)


def farmhouse(x, y, w=10.0, d=7.0, floors=1, front='S', name="house", variant=0):
    """Wooden farmhouse. x,y = SW corner. Ridge along x. front 'S' faces -y (toward road if house is north of it)."""
    g = G(name, "Buildings")
    wall = g.a("wall", bevel=0.01)
    stone = g.a("stone", bevel=0.02)
    wd = g.a("wood_dark", bevel=0.006)
    zb = 0.45
    hf = 2.9 if floors == 1 else 5.6
    x0, x1, y0, y1 = x, x + w, y, y + d
    FOOT.append((x0 - 1, x1 + 3.6, y0 - 3.5, y1 + 1))
    stone.box(x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, -0.3, zb)
    wall.box(x0, x1, y0, y1, zb, zb + hf)
    if floors == 2:
        wd.box(x0 - 0.08, x1 + 0.08, y0 - 0.08, y1 + 0.08, zb + 2.75, zb + 2.95)
    kw = g.a("kawara")
    wl = g.a("wall")
    gable_roof(kw, wl, x0, x1, y0, y1, zb + hf, 2.0 + 0.25 * (d - 7), ov=0.9, gov=0.6)
    # front (south) engawa and windows
    fy = y0 if front == 'S' else y1
    sg = -1 if front == 'S' else 1
    eg = g.a("floor", bevel=0.01)
    eg.box(x0 + 0.5, x1 - 0.5, fy + sg * 1.0 if sg < 0 else fy, fy if sg < 0 else fy + 1.0, zb - 0.02, zb + 0.07)
    for fl in range(floors):
        zz = zb + 0.1 + fl * 2.8
        nwin = 4 if w > 8 else 3
        wx0 = x0 + 1.0
        wx1 = x0 + 1.0 + (w - 2.0) * (0.64 if variant == 0 else 0.5)
        window_grid(g, wx0, wx1, fy, zz + 0.25, zz + 1.95, nwin, face=sg)
        # shoji paper strips behind part of the glass handled by lighter material
        g.a("shoji").box(wx0 + (wx1 - wx0) * 0.5, wx1, fy - sg * 0.06 + (-0.0 if sg < 0 else 0.0) - 0.0, fy + (0.0), zz + 0.25, zz + 1.95) if False else None
        # door
        dx = wx1 + 0.5
        wd.box(dx, dx + 1.1, fy + (sg * 0.04 if sg < 0 else 0), fy + (0 if sg < 0 else 0.04), zz, zz + 2.0)
        wd.box(dx - 0.05, dx + 1.15, fy + (sg * 0.06 if sg < 0 else 0), fy + (0 if sg < 0 else 0.06), zz + 2.0, zz + 2.08)
    # narrow tin lean-to / kitchen annex on the east end with chimney
    tin = g.a("tin")
    ax0, ax1 = x1, x1 + 2.6
    wall.box(ax0, ax1, y0 + 1.0, y0 + 4.6, zb, zb + 2.5)
    tin.extrude_x([(y0 + 0.4, zb + 2.75), (y0 + 5.2, zb + 2.35), (y0 + 5.2, zb + 2.3), (y0 + 0.4, zb + 2.70)], ax0 - 0.1, ax1 + 0.4)
    g.a("brick" if False else "concrete", bevel=0.01).box(ax0 + 1.8, ax0 + 2.2, y0 + 3.6, y0 + 4.0, zb + 2.4, zb + 5.0)
    # rain gutter + downpipe
    g.a("iron_black").sbox((x0, fy + sg * 0.85, zb + hf - 0.18), (x1, fy + sg * 0.85, zb + hf - 0.18), 0.1, 0.1)
    # clothes pole
    g.a("wood").cyl((x0 + 2.0, fy + sg * 2.5, 0.0), (x0 + 2.0, fy + sg * 2.5, 2.4), 0.04, seg=6)
    g.a("wood").cyl((x0 + 4.0, fy + sg * 2.5, 0.0), (x0 + 4.0, fy + sg * 2.5, 2.4), 0.04, seg=6)
    g.a("wood").cyl((x0 + 2.0, fy + sg * 2.5, 2.3), (x0 + 4.0, fy + sg * 2.5, 2.3), 0.025, seg=6)
    rng = random.Random(int(x * 11 + y))
    cl = [lib.mat_plain(f"pb_cloth{i}", c, rough=0.9) for i, c in enumerate(
        [(0.75, 0.74, 0.70), (0.2, 0.28, 0.45), (0.65, 0.60, 0.45), (0.5, 0.15, 0.12)])]
    for k in range(4):
        cc = Acc(f"{name}_cloth{k}", cl[k], "Buildings")
        cc.box(x0 + 2.1 + k * 0.45, x0 + 2.45 + k * 0.45, fy + sg * 2.5 - 0.02, fy + sg * 2.5 + 0.02, 1.45 + rng.uniform(0, 0.2), 2.25)
        cc.build()
    g.build()


def kura(x, y, w=4.4, d=5.6, name="kura"):
    g = G(name, "Buildings")
    FOOT.append((x - 1, x + w + 1, y - 1.5, y + d + 1))
    pl = g.a("plaster2")
    pl.box(x, x + w, y, y + d, 0.0, 3.4)
    g.a("wood_dark", bevel=0.01).box(x - 0.03, x + w + 0.03, y - 0.03, y + d + 0.03, 0.0, 1.0)         # namako-style lower cladding
    g.a("stone", bevel=0.02).box(x - 0.1, x + w + 0.1, y - 0.1, y + d + 0.1, -0.3, 0.2)
    kw, wl = g.a("kawara"), g.a("plaster2")
    gable_roof(kw, wl, x, x + w, y, y + d, 3.4, 1.9, ov=0.7, gov=0.4)
    # secondary eave
    kw.box(x - 0.2, x + w + 0.2, y - 0.2, y + d + 0.2, 1.7, 1.9) if False else None
    # front doors (heavy, black) facing -y
    dk = g.a("iron_black", bevel=0.01)
    dk.box(x + w / 2 - 0.9, x + w / 2 + 0.9, y - 0.12, y, 0.4, 2.4)
    g.a("plaster").box(x + w / 2 - 1.15, x + w / 2 + 1.15, y - 0.2, y - 0.05, 2.4, 2.55)
    for k in range(5):
        dk.sbox((x + w / 2 - 0.85, y - 0.15, 0.7 + k * 0.32), (x + w / 2 + 0.85, y - 0.15, 0.7 + k * 0.32), 0.03, 0.03)
    # small window
    dk.box(x + 0.7, x + 1.4, y - 0.1, y, 2.0, 2.6)
    g.a("plaster").box(x + 0.6, x + 1.5, y - 0.12, y - 0.03, 1.9, 2.0)
    g.build()


def inn(x, y, w=13.0, d=8.0, name="inn"):
    """Two-storey wooden inn facing -y (toward the road? no - facing the station side -y)."""
    farmhouse(x, y, w, d, floors=2, front='S', name=name, variant=1)
    g = G(name + "_sign", "Buildings")
    # hanging sign board with image + lantern
    face_plane(name + "_ekimae", "ekimae.png", 'S', x + w * 0.5, y - 0.22, 3.7, 3.4, off=0.0)
    g.a("wood_dark").box(x + w * 0.5 - 1.8, x + w * 0.5 + 1.8, y - 0.2, y - 0.1, 3.55, 3.7)
    g.build()


def shop(x, y, w=8.0, d=6.0, name="shop"):
    """Roadside general store (よろず屋): tin awning, shutters, vending machine, ad plates."""
    g = G(name, "Buildings")
    FOOT.append((x - 1, x + w + 1, y - 2.5, y + d + 1))
    g.a("stone", bevel=0.02).box(x - 0.1, x + w + 0.1, y - 0.1, y + d + 0.1, -0.3, 0.25)
    g.a("wall", bevel=0.01).box(x, x + w, y, y + d, 0.25, 3.3)
    kw, wl = g.a("kawara"), g.a("wall")
    gable_roof(kw, wl, x, x + w, y, y + d, 3.3, 1.7, ov=0.8, gov=0.5)
    # open front: sliding glass door + shutters
    g.a("dark_glass").box(x + 0.7, x + 5.0, y - 0.02, y + 0.03, 0.5, 2.3)
    fr = g.a("wood_dark", bevel=0.005)
    for i in range(7):
        fr.box(x + 0.7 + i * 0.7, x + 0.74 + i * 0.7, y - 0.05, y, 0.45, 2.35)
    fr.box(x + 0.7, x + 5.0, y - 0.05, y, 1.3, 1.34)
    # tin awning on posts
    g.a("tin").extrude_x([(y - 1.6, 2.55), (y - 0.1, 2.95), (y - 0.1, 3.0), (y - 1.6, 2.6)], x - 0.1, x + w + 0.1)
    for xx in (x + 0.1, x + w - 0.1):
        g.a("wood", bevel=0.01).box(xx - 0.07, xx + 0.07, y - 1.55, y - 1.41, 0.0, 2.6)
    # goods: crates with bottles, sacks, stove
    cr = g.a("crate", bevel=0.01)
    for i in range(3):
        cr.box(x + 0.9 + i * 0.7, x + 1.5 + i * 0.7, y - 0.8, y - 0.35, 0.0, 0.32)
    for i in range(3):
        for j in range(5):
            g.a("bottle").cyl((x + 0.98 + i * 0.7 + (j % 3) * 0.17, y - 0.7 + (j // 3) * 0.2, 0.32),
                              (x + 0.98 + i * 0.7 + (j % 3) * 0.17, y - 0.7 + (j // 3) * 0.2, 0.52), 0.035, seg=8)
    # bench
    g.a("wood", bevel=0.01).box(x + 5.6, x + 7.2, y - 0.7, y - 0.3, 0.38, 0.45)
    for xx in (x + 5.7, x + 7.1):
        g.a("wood", bevel=0.01).box(xx - 0.04, xx + 0.04, y - 0.65, y - 0.35, 0.0, 0.38)
    g.build()
    # enamel plates on the front wall (various)
    face_plane(name + "_adA", "ad_onsen.png", 'S', x + 6.0, y - 0.02, 1.15, 0.55)
    face_plane(name + "_adB", "ad_nokyo.png", 'S', x + 2.8, y - 0.02, 2.4, 1.4)
    face_plane(name + "_adC", "ad_fire.png", 'S', x + 7.3, y - 0.02, 1.2, 0.30)
    face_plane(name + "_vend", "vending.png", 'S', x + 5.4, y - 0.95, 0.0, 0.62, off=0.0)
    face_plane(name + "_safe", "ad_safety.png", 'S', x + 4.0, y - 0.02, 2.45, 1.0)


# =================================================================== goods shed (warehouse) + dock
def goods_shed(x0=6.0, x1=20.0, y0=5.9, y1=10.2):
    g = G("goods_shed", "Buildings")
    wall = g.a("wall", bevel=0.01)
    zb = 0.45
    g.a("stone", bevel=0.02).box(x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, -0.3, zb)
    wall.box(x0, x1, y0, y1, zb, zb + 3.5)
    tin = g.a("tin")
    ym = (y0 + y1) / 2
    ov = 1.3
    tin.extrude_x([(y0 - ov, zb + 3.55), (ym, zb + 4.9), (y1 + ov, zb + 3.55), (y1 + ov, zb + 3.49), (ym, zb + 4.84), (y0 - ov, zb + 3.49)], x0 - 0.5, x1 + 0.5)
    g.a("wall").extrude_x([(y0, zb + 3.5), (ym, zb + 4.8), (y1, zb + 3.5)], x0, x1)
    # lean-to canopy (north / road side) for loading
    tin.extrude_x([(y1 + ov, zb + 3.55), (y1 + 3.0, zb + 2.75), (y1 + 3.0, zb + 2.69), (y1 + ov, zb + 3.49)], x0 - 0.5, x1 + 0.5) if False else None
    # loading docks
    dock = g.a("floor", bevel=0.01)
    dock.box(x0 + 0.5, x1 - 0.5, y1, y1 + 1.5, 0.0, 0.95)
    g.a("stone", bevel=0.02).box(x0 + 0.5, x1 - 0.5, y1 + 1.5, y1 + 1.62, -0.1, 0.95)
    # canopy posts over dock
    for xx in np.linspace(x0 + 0.6, x1 - 0.6, 6):
        g.a("wood", bevel=0.01).box(xx - 0.09, xx + 0.09, y1 + 1.35, y1 + 1.53, 0.95, 3.6)
    tin.extrude_x([(y1 + 1.8, 3.55), (y1 + 0.2, 4.2), (y1 + 0.2, 4.14), (y1 + 1.8, 3.49)], x0 + 0.2, x1 - 0.2)
    # sliding doors (north side) : 3 big leaves
    dw = g.a("wood_dark", bevel=0.01)
    for i, xc in enumerate((9.0, 13.0, 17.0)):
        wall.box(xc - 1.5, xc + 1.5, y1 - 0.03, y1 + 0.02, 1.0, 3.4) if False else None
        dw.box(xc - 1.6, xc + 0.05, y1, y1 + 0.07, 1.0, 3.35)
        dw.box(xc - 0.05, xc + 1.6, y1 + 0.07, y1 + 0.14, 1.0, 3.35)
        dw.box(xc - 1.7, xc + 1.7, y1 + 0.03, y1 + 0.17, 3.35, 3.5)
        for k in range(4):
            g.a("iron_black").box(xc - 1.6, xc + 1.6, y1 + 0.17, y1 + 0.19, 1.3 + k * 0.5, 1.34 + k * 0.5) if False else None
    # south side (platform side) door + windows
    for xc in (10.0, 16.0):
        dw.box(xc - 1.0, xc + 1.0, y0 - 0.06, y0, 0.45, 2.7)
    window_grid(g, 12.0, 14.0, y0, 1.8, 2.8, 3, face=-1)
    g.a("dark_glass").box(7.0, 8.4, y0 - 0.02, y0 + 0.02, 1.8, 2.8)
    # rice bags stacked on dock + on the floor
    sk = g.a("bag", bevel=0.05)
    rng = random.Random(3)
    for (bx, by, nx, nz) in ((8.0, y1 + 0.6, 5, 4), (14.2, y1 + 0.55, 3, 3), (18.0, y1 + 0.6, 2, 2)):
        for k in range(nx):
            for l in range(nz):
                for j in range(2):
                    sk.boxc(bx + k * 0.42 + (0.2 if l % 2 else 0) + rng.uniform(-0.02, 0.02), by + j * 0.7 + rng.uniform(-0.03, 0.03),
                            0.95 + 0.14 + l * 0.27, 0.40, 0.64, 0.27, rz=rng.uniform(-0.04, 0.04))
    # tarp-covered pile
    g.a("tarp", None).box(10.6, 12.4, y1 + 0.3, y1 + 1.3, 0.95, 1.55) if False else None
    g.build()
    # posters & notices on the south wall (platform side) + enamel plates
    face_plane("shed_notice", "notice.png", 'S', 8.2, y0 - 0.02, 1.5, 0.9)
    face_plane("shed_ad1", "ad_fire.png", 'S', 18.5, y0 - 0.02, 1.2, 0.5)
    face_plane("shed_ad2", "ad_nokyo.png", 'S', 19.0, y0 - 0.02, 2.2, 1.3)
    face_plane("shed_poster", "poster_savings.png", 'S', 11.6, y0 - 0.02, 1.4, 0.5)
    face_plane("shed_sabo", "sabo.png", 'S', 14.8, y0 - 0.02, 3.0, 1.5)
    # north wall: small rate board
    face_plane("shed_fare", "fare_board.png", 'N', 5.2 + 0, y1 + 0.02, 1.3, 1.0) if False else None


# =================================================================== crossing, signal, signs, shrine
def crossing_furniture():
    g = G("xing", "Props")
    for (xx, yy, face) in ((X_C - 3.3, 2.5, 'N'), (X_C + 3.3, 2.5, 'N'), (X_C - 3.3, -18.5, 'S'), (X_C + 3.3, -18.5, 'S')):
        g.a("white_paint", bevel=0.01).box(xx - 0.06, xx + 0.06, yy - 0.06, yy + 0.06, 0.0, 2.5)
        # crossbuck X
        for sg in (-1, 1):
            g.a("crossbuck", bevel=0.01).sbox((xx - 0.8, yy + (0.08 if face == 'N' else -0.08), 2.2 - sg * 0.5 * 0.9),
                                              (xx + 0.8, yy + (0.08 if face == 'N' else -0.08), 2.2 + sg * 0.5 * 0.9), 0.14, 0.03)
        face_plane(f"xsign_{xx}_{yy}", "crossing_sign.png", face, xx, yy + (0.1 if face == 'N' else -0.1), 1.35, 0.6, h=0.6)
    hx0, hy0 = 40.4, 3.4
    import houses
    houses.hut2(hx0, hy0)
    # gate-bell post + flasher
    g.a("iron_black").box(hx0 + 3.3, hx0 + 3.42, hy0 + 0.5, hy0 + 0.62, 0.0, 3.2)
    g.a("tr_red").cyl((hx0 + 3.36, hy0 + 0.5, 3.0), (hx0 + 3.36, hy0 + 0.35, 3.0), 0.16, seg=14)
    g.build()
    face_plane("hut_sign", "fumikiri_plate.png", 'S', hx0 + 1.4, hy0 - 0.08, 2.25, 0.8)
    face_plane("tomare_sign", "tomare.png", 'N', X_C + 3.3, 5.2, 1.3, 0.55, h=0.55) if False else None


def signals():
    g = G("signals", "Props")
    for (x, y, ang, flip) in ((28.5, -2.3, 40, 1), (-24.5, -2.3, 40, -1)):
        g.a("white_paint", bevel=0.01).box(x - 0.09, x + 0.09, y - 0.09, y + 0.09, 0.0, 6.2)
        g.a("iron_black").box(x - 0.14, x + 0.14, y - 0.14, y + 0.14, 5.9, 6.4)
        # ladder
        for s in (-1, 1):
            g.a("iron_black").sbox((x + flip * 0.2, y + s * 0.2, 0.2), (x + flip * 0.2, y + s * 0.2, 5.5), 0.025, 0.025)
        for k in range(10):
            g.a("iron_black").sbox((x + flip * 0.2, y - 0.2, 0.4 + k * 0.5), (x + flip * 0.2, y + 0.2, 0.4 + k * 0.5), 0.02, 0.02)
        # semaphore arm (clear: drops 40 deg), faces the oncoming train along x
        a = math.radians(ang)
        L = 1.5
        base = (x + flip * 0.15, y, 5.55)
        tip = (base[0], base[1] - L * math.cos(a), base[2] - L * math.sin(a))
        g.a("post_red", bevel=0.01).sbox(base, tip, 0.04, 0.26)
        g.a("white_paint").sbox((base[0], base[1] - L * math.cos(a) * 0.7, base[2] - L * math.sin(a) * 0.7),
                                (base[0], base[1] - L * math.cos(a) * 0.9, base[2] - L * math.sin(a) * 0.9), 0.045, 0.27)
        g.a("lamp_glow").sphere((x + flip * 0.28, y, 5.95), (0.12, 0.12, 0.14), seg=10, rings=6)
        g.a("iron_black").cyl((x + flip * 0.18, y, 5.45), (x + flip * 0.38, y, 5.45), 0.17, seg=12)
        # counterweight lever box + rod to ground (wire)
        g.a("iron_black").sbox((x - flip * 0.1, y + 0.12, 0.8), (x - flip * 0.1, y + 0.12, 5.4), 0.012, 0.012)
        g.a("iron_black").box(x + 0.25, x + 0.7, y + 0.1, y + 0.4, 0.0, 0.9)
    g.build()


def shrine():
    g = G("shrine", "Buildings")
    x, y = -72.0, 21.0          # north of the road, faces south
    FOOT.append((x - 4, x + 4, y - 4, y + 4))
    red = g.a("post_red", bevel=0.01)
    for s in (-1, 1):
        red.cyl((x + s * 1.6, y - 3.5, 0.0), (x + s * 1.6, y - 3.5, 3.5), 0.22, 0.2, seg=12)
        g.a("stone", bevel=0.03).box(x + s * 1.6 - 0.35, x + s * 1.6 + 0.35, y - 3.85, y - 3.15, -0.1, 0.35)
    red.sbox((x - 2.3, y - 3.5, 3.35), (x + 2.3, y - 3.5, 3.35), 0.18, 0.16)   # nuki
    red.sbox((x - 2.3, y - 3.5, 3.35), (x + 2.3, y - 3.5, 3.35), 0.18, 0.16)
    kas = g.a("iron_black", bevel=0.02)
    kas.sbox((x - 2.7, y - 3.5, 3.95), (x - 1.0, y - 3.5, 3.85), 0.28, 0.2)
    kas.sbox((x - 1.0, y - 3.5, 3.85), (x + 1.0, y - 3.5, 3.85), 0.28, 0.2)
    kas.sbox((x + 1.0, y - 3.5, 3.85), (x + 2.7, y - 3.5, 3.95), 0.28, 0.2)
    red.sbox((x - 2.0, y - 3.5, 3.65), (x + 2.0, y - 3.5, 3.65), 0.2, 0.22)
    red.sbox((x, y - 3.5, 3.55), (x, y - 3.5, 3.85), 0.2, 0.3)
    # approach path (gravel) + lanterns
    g.a("pebble" if "pebble" in M else "stone").box(x - 0.9, x + 0.9, y - 3.3, y - 0.2, 0.0, 0.03)
    for s in (-1, 1):
        for yy in (-2.4, -0.9):
            st = g.a("stone_lantern", bevel=0.02)
            xl = x + s * 1.7
            st.box(xl - 0.22, xl + 0.22, y + yy - 0.22, y + yy + 0.22, 0.0, 0.2)
            st.cyl((xl, y + yy, 0.2), (xl, y + yy, 1.0), 0.09, seg=8)
            st.box(xl - 0.26, xl + 0.26, y + yy - 0.26, y + yy + 0.26, 1.0, 1.08)
            st.box(xl - 0.18, xl + 0.18, y + yy - 0.18, y + yy + 0.18, 1.08, 1.4)
            st.cyl((xl, y + yy, 1.4), (xl, y + yy, 1.75), 0.34, 0.03, seg=4)
    import houses
    houses.hokora2(x, y)
    g.build()
    face_plane("torii_plaque", "shrine_plaque.png", 'S', x, y - 3.5 - 0.12, 3.42, 0.62, h=0.78)
    g = G("shrine2", "Buildings")
    g.build()


# =================================================================== platform furniture
def lamp_post(g, x, y, h=4.3, side=0):
    g.a("wood", bevel=0.01).box(x - 0.07, x + 0.07, y - 0.07, y + 0.07, Z_PLAT, Z_PLAT + h)
    g.a("wood", bevel=0.01).sbox((x, y, Z_PLAT + h - 0.4), (x, y + 0.5 * (1 if side >= 0 else -1), Z_PLAT + h - 0.1), 0.05, 0.05)
    yy = y + 0.5 * (1 if side >= 0 else -1)
    g.a("tin").cyl((x, yy, Z_PLAT + h - 0.05), (x, yy, Z_PLAT + h - 0.3), 0.04, 0.3, seg=14)
    g.a("lamp_glow").sphere((x, yy, Z_PLAT + h - 0.3), (0.1, 0.1, 0.07), seg=8, rings=4)


def bench(g, x, y, length=2.0, face='S', z=None):
    z = Z_PLAT if z is None else z
    w = g.a("wood", bevel=0.012)
    s = -1 if face == 'S' else 1
    w.box(x - length / 2, x + length / 2, y - 0.22, y + 0.22, z + 0.42, z + 0.46)
    w.box(x - length / 2, x + length / 2, y + s * -0.22 - 0.02 * 0, y + s * -0.22 + (0.03), z + 0.46, z + 0.95) if False else None
    yb = y - s * 0.22
    w.box(x - length / 2, x + length / 2, yb - 0.02, yb + 0.02, z + 0.62, z + 0.9)
    for xx in (x - length / 2 + 0.12, x + length / 2 - 0.12):
        g.a("iron_black").box(xx - 0.03, xx + 0.03, y - 0.2, y + 0.2, z, z + 0.42)
        g.a("iron_black").box(xx - 0.03, xx + 0.03, yb - 0.03, yb + 0.03, z + 0.42, z + 0.9)


def luggage_cart(g, x, y, z=None):
    z = Z_PLAT if z is None else z
    wd = g.a("wood_dark", bevel=0.008)
    wd.box(x - 0.9, x + 0.9, y - 0.4, y + 0.4, z + 0.28, z + 0.34)
    for s in (-1, 1):
        for xx in (x - 0.55, x + 0.55):
            g.a("iron_black").cyl((xx, y + s * 0.42, z + 0.16), (xx, y + s * 0.46, z + 0.16), 0.16, seg=14)
    g.a("iron_black").sbox((x + 0.95, y, z + 0.34), (x + 1.7, y, z + 0.85), 0.04, 0.04)
    sk = g.a("bag", bevel=0.05)
    sk.boxc(x - 0.4, y - 0.1, z + 0.48, 0.6, 0.4, 0.27, rz=0.2)
    sk.boxc(x + 0.1, y + 0.1, z + 0.48, 0.6, 0.4, 0.27, rz=-0.1)
    g.a("crate", bevel=0.01).box(x + 0.35, x + 0.8, y - 0.2, y + 0.25, z + 0.34, z + 0.7)
    g.a("tr_cream", bevel=0.03).box(x - 0.2, x + 0.3, y - 0.15, y + 0.2, z + 0.62, z + 0.92)   # bundled parcel


def milk_cans(g, x, y, z=None, n=4):
    z = Z_PLAT if z is None else z
    for i in range(n):
        xx, yy = x + (i % 2) * 0.32, y + (i // 2) * 0.32
        g.a("milk").cyl((xx, yy, z), (xx, yy, z + 0.62), 0.14, seg=12)
        g.a("milk").cyl((xx, yy, z + 0.62), (xx, yy, z + 0.74), 0.08, seg=10)
        g.a("milk").cyl((xx, yy, z + 0.74), (xx, yy, z + 0.78), 0.1, seg=10)


def platform_furniture():
    g = G("platform_furn", "Props")
    for x in (-16.5, -0.8, 9.5, 18.5, 24.0):
        lamp_post(g, x, 2.15, side=1)
    for x in (-14.0, 5.8, 13.0):
        bench(g, x, 2.6, 2.0, face='S')
    luggage_cart(g, 8.5, 3.6)
    milk_cans(g, -3.8, 2.4)
    # fire bucket stand
    g.a("wood").box(-1.4 + 3.2, -1.0 + 3.2, 3.7, 3.9, Z_PLAT, Z_PLAT + 0.5)
    g.a("tr_red").cyl((1.9, 3.8, Z_PLAT + 0.5), (1.9, 3.8, Z_PLAT + 0.75), 0.13, 0.15, seg=10)
    # bins
    g.a("tin").cyl((16.0, 3.9, Z_PLAT), (16.0, 3.9, Z_PLAT + 0.65), 0.22, seg=12)
    # ekimei boards on two posts (double-sided)
    for xc in (-15.0, 10.5, 22.5):
        for s in (-1, 1):
            g.a("wood_dark", bevel=0.01).box(xc + s * 1.35 - 0.06, xc + s * 1.35 + 0.06, 3.3 - 0.06, 3.3 + 0.06, Z_PLAT, Z_PLAT + 2.6)
        g.a("wood_dark", bevel=0.01).box(xc - 1.45, xc + 1.45, 3.3 - 0.05, 3.3 + 0.05, Z_PLAT + 1.2, Z_PLAT + 2.2)
    # island shelter
    isx0, isx1 = 3.5, 13.5
    iy = (ISLAND[2] + ISLAND[3]) / 2
    for xx in np.linspace(isx0, isx1, 5):
        for yy in (iy - 1.1, iy + 1.1):
            g.a("wood", bevel=0.01).box(xx - 0.09, xx + 0.09, yy - 0.09, yy + 0.09, Z_PLAT, Z_PLAT + 3.0)
    g.a("tin").extrude_x([(iy - 2.0, Z_PLAT + 3.0), (iy, Z_PLAT + 3.45), (iy + 2.0, Z_PLAT + 3.0), (iy + 2.0, Z_PLAT + 2.94), (iy, Z_PLAT + 3.39), (iy - 2.0, Z_PLAT + 2.94)], isx0 - 0.6, isx1 + 0.6)
    bench(g, 8.5, iy + 0.7, 3.0, face='S')
    bench(g, 11.5, iy - 0.7, 2.2, face='N')
    for x in (-8.0, 22.0, 29.0):
        lamp_post(g, x, iy, side=1)
    milk_cans(g, 5.0, iy - 0.7, n=2)
    g.build()
    for xc in (-15.0, 10.5, 22.5):
        face_plane(f"ekimei_s_{xc}", "ekimei_old.png", 'S', xc, 3.3 - 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
        face_plane(f"ekimei_n_{xc}", "ekimei_old.png", 'N', xc, 3.3 + 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
    face_plane("tt_island", "timetable_old.png", 'S', 6.0, iy + 1.13, Z_PLAT + 1.0, 0.8, kw=None)
    face_plane("poster_isl1", "poster_travel.png", 'N', 10.5, iy - 1.13, Z_PLAT + 1.0, 0.5)
    face_plane("poster_isl2", "poster_leaf.png", 'N', 7.0, iy - 1.13, Z_PLAT + 1.0, 0.55) if False else None
    # island name board
    gi = G("isl_board", "Props")
    for s in (-1, 1):
        gi.a("wood_dark", bevel=0.01).box(27 + s * 1.35 - 0.06, 27 + s * 1.35 + 0.06, iy - 0.06, iy + 0.06, Z_PLAT, Z_PLAT + 2.6)
    gi.a("wood_dark", bevel=0.01).box(27 - 1.45, 27 + 1.45, iy - 0.05, iy + 0.05, Z_PLAT + 1.2, Z_PLAT + 2.2)
    gi.build()
    face_plane("ekimei_isl_s", "ekimei_old.png", 'S', 27, iy - 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
    face_plane("ekimei_isl_n", "ekimei_old.png", 'N', 27, iy + 0.06, Z_PLAT + 1.22, 2.9, h=0.96)


def forecourt_furniture():
    g = G("forecourt", "Props")
    # notice board with posters, beside the porch
    nx, ny = -2.2, 10.5
    for s in (-1, 1):
        g.a("wood", bevel=0.01).box(nx + s * 0.95 - 0.06, nx + s * 0.95 + 0.06, ny - 0.06, ny + 0.06, 0.0, 2.1)
    g.a("wood_dark", bevel=0.01).box(nx - 1.1, nx + 1.1, ny - 0.04, ny + 0.04, 0.85, 1.95)
    g.a("tin").extrude_x([(ny - 0.2, 2.0), (ny, 2.2), (ny + 0.2, 2.0), (ny + 0.2, 1.96), (ny, 2.16), (ny - 0.2, 1.96)], nx - 1.2, nx + 1.2)
    # bike racks (wood rails) by the wall
    g.a("wood", bevel=0.01).box(-13.2, -9.2, 9.0, 9.08, 0.0, 0.5)
    # bollards / stones along the apron
    for x in np.arange(-24, 8, 4.0):
        if -9.5 < x < -4.5:
            continue
        g.a("stone", bevel=0.04).box(x - 0.18, x + 0.18, 17.0, 17.36, -0.05, 0.4 + 0.1 * math.sin(x))
    # wood fence along the platform end (no fence at platform ramps)
    g.build()
    face_plane("nb_p1", "poster_sumo.png", 'N', nx - 0.65, ny + 0.05, 1.05, 0.45)
    face_plane("nb_p2", "poster_festival.png", 'N', nx - 0.0, ny + 0.05, 1.0, 0.5)
    face_plane("nb_p3", "poster_safety.png", 'N', nx + 0.65, ny + 0.05, 1.1, 0.4)
    face_plane("nb_p4", "poster_movie.png", 'N', nx + 0.0, ny + 0.05, 1.55, 0.3)
    face_plane("fare_out", "fare_board.png", 'N', -11.0, 8.46, 1.4, 1.0) if False else None
    face_plane("tt_out", "timetable.png", 'N', -3.7, 8.5, 0.0, 0.0001, h=0.0001) if False else None


def build_props():
    random.seed(11)
    build_lines()
    crossing_furniture()
    signals()
    shrine()
    platform_furniture()
    forecourt_furniture()
    build_links()
    build_annex_in()
    station_lights()
    # vehicles at the forecourt
    bonnet_truck(-18.5, 12.2, math.pi + 0.06, load="rice", name="truck_forecourt", body="tr_green")
    three_wheeler(0.8, 12.0, 0.55, name="oto3_forecourt")
    handcart(3.8, 10.3, 0.2, name="rear_cart1")
    bonnet_truck(12.2, 12.4, 0.0, load="rice", name="truck_dock", body="tr_red")
    handcart(27.0, 8.0, -0.3, name="rear_cart2", sacks=False)
    # bicycles at the wall and by the platform ramp
    g = G("bikes", "Vehicles")
    for i, (bx, kind) in enumerate(((-12.6, 0), (-12.0, 1), (-11.4, 0), (-10.8, 2), (-10.2, 0))):
        bike(g, bx, 9.3 + 0.0, math.pi / 2 + 0.05 * (i % 3 - 1) + 0.35 * (i % 2), kind=kind)
    bike(g, -3.4, 8.9, 1.2, kind=1)
    bike(g, 28.0, 4.0, 0.0, kind=2)
    bike(g, 4.0, 3.0, math.pi / 2, kind=0, z0=Z_PLAT) if False else None
    g.build()
    # houses, kura, inn, shop along the forecourt road (north side) - all furnished inside
    import houses
    houses.goods_shed2()
    houses.farmhouse2(-62.0, 17.8, 11.0, 7.0, name="house_A", variant=0, seed=1)
    houses.kura2(-48.0, 18.4, name="kura_A")
    houses.farmhouse2(-44.0, 17.8, 10.0, 6.8, name="house_B", variant=1, seed=2)
    houses.inn2(-31.0, 17.6, 13.5, 8.0, name="inn")
    houses.shop2(-16.0, 18.4, 8.0, 5.5, name="shop")
    houses.farmhouse2(-100.0, 17.7, 12.0, 7.2, name="house_C", variant=0, seed=3)
    houses.farmhouse2(-86.0, 17.8, 9.0, 6.5, name="house_D", variant=1, seed=4)
    houses.farmhouse2(44.5, 17.8, 10.5, 7.0, name="house_E", variant=0, seed=5)
    houses.farmhouse2(46.0, -33.0, 9.5, 6.5, name="house_F", variant=1, seed=6)


def rail_stack(g, x, y, yaw, n=5, length=6.0):
    """Stack of spare rails resting on sleepers."""
    T = XF(x, y, yaw)
    for k in range(3):
        g.a("wood_dark", bevel=0.01).box(*[0] * 6) if False else None
        c = T((k * (length / 2.2) - length / 2.2, 0, 0.0))
        g.a("wood_dark", bevel=0.01).boxc(c[0], c[1], 0.1, 0.22, 1.5, 0.2, rz=yaw + math.pi / 2)
    for i in range(n):
        for j in range(n - i):
            off = (j - (n - i - 1) / 2) * 0.17
            z = 0.32 + i * 0.15
            g.a("iron_rust").sbox(T((-length / 2, off, z)), T((length / 2, off, z)), 0.07, 0.13)


def sleeper_pile(g, x, y, yaw, nx=8, nz=6):
    T = XF(x, y, yaw)
    rng = random.Random(int(abs(x * 3 + y)))
    for k in range(nz):
        for i in range(nx):
            c = T(((rng.uniform(-0.03, 0.03)), (i - nx / 2) * 0.2, 0.09 + k * 0.15))
            g.a("wood_dark", bevel=0.008).boxc(c[0], c[1], c[2], 2.1, 0.17, 0.14, rz=yaw + rng.uniform(-0.02, 0.02) + (math.pi / 2 if k % 2 else 0))


def drums(g, x, y, n=6):
    rng = random.Random(5)
    for i in range(n):
        xx, yy = x + (i % 3) * 0.62 + rng.uniform(-0.05, 0.05), y + (i // 3) * 0.62
        g.a("tr_red" if i % 2 else "tr_grey").cyl((xx, yy, 0.0), (xx, yy, 0.88), 0.29, seg=14)
        g.a("iron_black").cyl((xx, yy, 0.45), (xx, yy, 0.49), 0.30, seg=14)


def lowloader(x, y, yaw, name="lowloader"):
    """Trailer carrying a new car shell (a vehicle under construction heading to the depot)."""
    g = G(name, "Vehicles")
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, c + 0.016))
    dk = g.a("iron_black", bevel=0.01)
    wd = g.a("wood_dark", bevel=0.01)
    wd.boxc(*T((0, 0, 0.95 + 0.016)), 10.5, 2.3, 0.14, rz=yaw)
    for s in (-1, 1):
        dk.sbox(P(-5.2, s * 0.8, 0.85), P(5.2, s * 0.8, 0.85), 0.14, 0.2)
    for xc in (-3.6, -2.7):
        dk.cyl(P(xc, -1.0, 0.4), P(xc, 1.0, 0.4), 0.06, seg=8)
        for s in (-1, 1):
            road_wheel(g, P, yaw, xc, s * 1.05, 0.4, 0.22)
    dk.sbox(P(5.2, 0, 0.9), P(6.8, 0, 0.9), 0.12, 0.1)                        # drawbar
    dk.cyl(P(4.6, -0.9, 0.4), P(4.6, 0.9, 0.4), 0.06, seg=8) if False else None
    # car shell on cradle: bare primer body with window openings (no glass), steel frame inside
    pr = g.a("primer", bevel=0.03)
    L, W, z0, z1 = 9.4, 2.5, 1.18, 3.7
    for (ya, yb) in ((-W / 2, -W / 2 + 0.06), (W / 2 - 0.06, W / 2)):
        # side walls with window gaps
        zs, ze = 2.05, 2.95
        pr.boxc(*T((0, (ya + yb) / 2, (z0 + zs) / 2 + 0.016)), L, 0.06, zs - z0, rz=yaw)
        pr.boxc(*T((0, (ya + yb) / 2, (ze + z1 - 0.3) / 2 + 0.016)), L, 0.06, z1 - 0.3 - ze, rz=yaw)
        for k in range(10):
            pr.boxc(*T((-4.4 + k * 0.98, (ya + yb) / 2, (zs + ze) / 2 + 0.016)), 0.28, 0.06, ze - zs, rz=yaw)
    pr.boxc(*T((0, 0, z1 - 0.15 + 0.016)), L, W - 0.3, 0.06, rz=yaw)
    for k in range(7):
        g.a("iron_rust").sbox(P(-4.5 + k * 1.5, -W / 2 + 0.1, 3.2), P(-4.5 + k * 1.5, W / 2 - 0.1, 3.2), 0.05, 0.05)
    pr.boxc(*T((-L / 2, 0, (z0 + z1) / 2 + 0.016)), 0.06, W, z1 - z0 - 0.3, rz=yaw)
    # chain tie-downs
    for xx in (-3.0, 0.0, 3.0):
        for s in (-1, 1):
            dk.sbox(P(xx, s * 1.2, 1.0), P(xx, s * 0.9, 2.6), 0.02, 0.02)
    g.build()


def switch_stand(g, x, y, ang=0.0):
    g.a("iron_black").cyl((x, y, 0), (x, y, 1.1), 0.045, seg=8)
    g.a("iron_black").cyl((x - 0.3, y, 1.15), (x + 0.3, y, 1.15), 0.015, seg=6)
    g.a("tr_red").cyl((x, y, 1.1), (x, y + 0.03, 1.1), 0.22, seg=14)
    g.a("white_paint").cyl((x, y + 0.03, 1.1), (x, y + 0.04, 1.1), 0.12, seg=14)
    g.a("lamp_glow").sphere((x, y, 1.45), (0.07, 0.07, 0.09), seg=8, rings=5)
    g.a("iron_black").sbox((x, y, 0.5), (x + 0.9, y - 0.3, 0.05), 0.03, 0.03)


def build_links():
    """Connect the station yard and the depot: depot access road, staff footpath with a yard board crossing, turnout furniture."""
    import core
    from core import ribbon
    ribbon("road_depot", [(X_C, -50), (X_C - 1.5, -58), (34.5, -64.5), (27.5, -66.5)], 3.8, M["road"], z0=0.018)
    core.apron("depot_gate", 31.0, -65.5, 5.5, 3.2, M["road"], noise_amp=0.06, z0=0.016)
    # staff footpath: island west end -> board crossing -> south -> depot office
    ribbon("path_staff", [(-19.0, -6.3), (-21.0, -6.3), (-21.0, -20.0), (-21.5, -26.0), (-30.0, -28.8), (-37.0, -28.8)], 1.3, M["road"], rut=False, z0=0.018)
    d = Acc("staff_crossing", M["wood_dark"], "Track", bevel=0.01)
    xs = -21.0
    for t in (-0.0, 0.0):
        pass
    for k in range(7):
        d.box(xs - 0.7, xs + 0.7, -19.4 + k * 0.0, -19.4 + k * 0.0, 0, 0) if False else None
    d.box(xs - 0.65, xs + 0.65, -18.4, -2.6, Z_SLEEP + 0.006, Z_RAIL - 0.03)
    d.build()
    g = G("links", "Props")
    for yy in (-2.2, -19.0):
        for sx in (-1, 1):
            g.a("white_paint", bevel=0.01).box(xs + sx * 1.0 - 0.05, xs + sx * 1.0 + 0.05, yy - 0.05, yy + 0.05, 0.0, 1.4)
    for yy in (-2.2, -19.0):
        g.a("crossbuck", bevel=0.01).sbox((xs - 1.0, yy, 1.5), (xs + 1.0, yy, 1.1), 0.06, 0.12)
    # turnout furniture where the depot lead leaves T4
    switch_stand(g, 7.0, -18.3)
    switch_stand(g, -4.6, -14.6)
    # direction/guide post at the depot gate + gate posts
    for sx in (-1, 1):
        g.a("wood", bevel=0.01).box(31.0 + sx * 2.5 - 0.1, 31.0 + sx * 2.5 + 0.1, -67.7 - 0.1, -67.7 + 0.1, 0.0, 1.8)
    g.build()
    face_plane("depot_gate_sign", "mark_depot.png", 'N', 31.0, -67.6, 1.9, 1.4) if False else None
    face_plane("depot_gate_sign", "mark_depot.png", 'N', 31.0, -67.62, 1.3, 1.2)
    face_plane("depot_keepout", "keep_out.png", 'N', 28.9, -67.62, 1.1, 0.55)
    g.a("wood")
    gg = G("gate_board", "Props")
    gg.a("wood_dark", bevel=0.01).box(31.0 - 0.8, 31.0 + 0.8, -67.72, -67.62, 1.2, 1.55) if False else None
    gg.build()


def build_depot_props():
    gm = G("depot_mat", "Props")
    core_apron = None
    try:
        import core
        core.apron("depot_mat_yard", 47.0, -62.0, 8.5, 11.0, M["road"], noise_amp=0.08, z0=0.016)
    except Exception:
        pass
    rail_stack(gm, 44.0, -54.0, 0.05)
    rail_stack(gm, 44.0, -57.2, -0.03, n=4, length=7.0)
    sleeper_pile(gm, 50.5, -55.0, 0.0)
    sleeper_pile(gm, 50.5, -59.5, 0.1, nx=7, nz=5)
    drums(gm, 52.0, -67.0)
    drums(gm, 44.5, -69.5, n=4)
    # gravel/coal heaps
    gm.a("ballast").sphere((51.5, -72.0, 0.0), (2.4, 2.0, 1.3), seg=14, rings=8)
    gm.a("concrete", bevel=0.02).box(41.0, 42.4, -74.4, -73.0, 0.0, 0.5)
    gm.build()
    lowloader(46.0, -64.0, math.pi / 2 + 0.1, name="lowloader_carshell")
    bonnet_truck(47.2, -78.0, math.pi / 2, load="logs", name="truck_tractor", body="tr_cream")
    three_wheeler(53.0, -62.0, 2.5, name="oto3_depot", body="tr_green")
    bike_g = G("depot_bikes", "Vehicles")
    bike(bike_g, 34.0, -66.5, 0.4, kind=1)
    bike_g.build()


def build_annex_in():
    """Interior of the little toilet annex east of the station (x 0.4..3.0, y 5.4..7.6)."""
    import rooms as R
    from rooms import A, lamp_point
    g = G("annex_in", "Station")
    x0, x1, y0, y1 = 0.4, 3.0, 5.4, 7.6
    zf = 0.2
    A(g, "concrete").box(x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 0.1, zf + 0.01)
    # window glazing (west wall) + door leaf ajar
    A(g, "glass").box(x0 + 0.04, x0 + 0.06, 6.22, 6.88, 1.62, 2.08)
    A(g, "wood_dark").box(x0 + 0.02, x0 + 0.08, 6.2, 6.9, 1.6, 1.64)
    A(g, "wood_dark").box(x0 + 0.02, x0 + 0.08, 6.2, 6.9, 2.08, 2.12)
    # cubicle (east): partition + door + squat toilet + paper holder
    A(g, "wood_dark", 0.005).box(1.95, 2.0, y0 + 0.9, y1 - 0.1, zf, 1.9)
    A(g, "wood_dark", 0.005).box(2.0, x1 - 0.1, y0 + 0.9, y0 + 0.95, zf, 1.9) if False else None
    A(g, "wood", 0.005).box(2.0, x1 - 0.1, y1 - 1.35, y1 - 1.3, zf, 1.9) if False else None
    A(g, "porcelain", 0.015).box(2.3, 2.8, 6.4, 7.2, zf, zf + 0.12)
    A(g, "dark_glass").box(2.45, 2.65, 6.6, 7.0, zf + 0.12, zf + 0.125)
    A(g, "porcelain", 0.015).box(2.3, 2.8, 7.25, 7.5, zf + 0.12, zf + 0.5)           # hooded end
    A(g, "wood_dark").box(2.8, 2.9, 7.0, 7.15, 1.3, 1.45)                             # paper holder
    A(g, "wood_dark", 0.005).box(1.5, 1.95, y0 + 1.0, y0 + 1.06, zf, 1.5) if False else None
    # urinal trough (west) + sink
    A(g, "porcelain", 0.015).box(0.5, 0.75, 6.1, 7.2, zf + 0.35, zf + 0.9)
    A(g, "porcelain", 0.015).box(0.5, 0.9, 6.1, 7.2, zf, zf + 0.35)
    A(g, "tin", 0.01).box(1.2, 1.8, y1 - 0.45, y1 - 0.1, zf + 0.85, zf + 1.0)         # basin
    A(g, "chrome").cyl((1.5, y1 - 0.15, zf + 1.0), (1.5, y1 - 0.15, zf + 1.2), 0.015, seg=6)
    A(g, "wood_dark").box(1.2, 1.8, y1 - 0.45, y1 - 0.1, zf, zf + 0.85)
    A(g, "chrome").box(1.3, 1.7, y1 - 0.105, y1 - 0.1, 1.5, 2.0)                      # mirror
    A(g, "tin", 0.01).cyl((0.9, y0 + 0.5, zf), (0.9, y0 + 0.5, zf + 0.35), 0.15, seg=10)     # pail
    A(g, "lamp_glow").sphere((1.6, 6.5, 2.3), (0.06, 0.06, 0.08), seg=8, rings=5)
    lamp_point(1.6, 6.5, 2.3, 6)
    g.build()
    face_plane("annex_sign", "benjo.png", 'S', 1.55, y0 - 0.12, 2.05, 0.5, h=0.18)


def station_lights():
    """Interior lighting for the station building (waiting room, ticket office, baggage room, porch)."""
    from rooms import lamp_point
    for (x, y, w) in ((-10.4, 6.4, 45), (-7.0, 6.4, 45), (-3.8, 6.4, 45), (-10.0, 5.2, 30), (-4.5, 5.2, 30), (-7.0, 9.4, 14)):
        lamp_point(x, y, 3.0, w, name="station_light")
