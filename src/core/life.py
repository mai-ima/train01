"""Signs of life: people, animals, fallen leaves, puddles (all original low-poly figures)."""
from common import *
import lib
import props
from props import XF, G

_PM = {}


def pc(key, color, rough=0.85):
    if key not in _PM:
        _PM[key] = lib.mat_plain("lf_" + key, color, rough=rough)
    return _PM[key]


class Fig:
    """Accumulators per colour for one figure group."""
    def __init__(self, name):
        self.name, self.d = name, {}

    def a(self, key, color, bevel=0.0, smooth=False):
        if (key, bevel) not in self.d:
            self.d[(key, bevel)] = Acc(f"{self.name}_{key}", pc(key, color), "People", bevel=bevel, smooth=smooth)
        return self.d[(key, bevel)]

    def build(self):
        for a in self.d.values():
            a.build()


SKIN = (0.55, 0.38, 0.28)
OUTFITS = {
    "master": dict(top=(0.04, 0.05, 0.10), bot=(0.04, 0.05, 0.10), hat="cap", hatc=(0.04, 0.05, 0.10), band=(0.75, 0.70, 0.5), gloves=True),
    "man": dict(top=(0.22, 0.20, 0.16), bot=(0.12, 0.12, 0.13), hat="cap", hatc=(0.30, 0.27, 0.20)),
    "man2": dict(top=(0.14, 0.17, 0.20), bot=(0.20, 0.18, 0.14), hat="none", hatc=(0, 0, 0)),
    "woman": dict(top=(0.22, 0.24, 0.40), bot=(0.07, 0.07, 0.10), hat="scarf", hatc=(0.55, 0.50, 0.40)),
    "farmer": dict(top=(0.34, 0.30, 0.20), bot=(0.18, 0.17, 0.15), hat="straw", hatc=(0.62, 0.52, 0.30)),
    "worker": dict(top=(0.08, 0.14, 0.30), bot=(0.08, 0.14, 0.30), hat="cap", hatc=(0.08, 0.14, 0.30)),
    "student": dict(top=(0.03, 0.03, 0.05), bot=(0.03, 0.03, 0.05), hat="cap", hatc=(0.03, 0.03, 0.05)),
}


def person(f, x, y, yaw, kind="man", z=0.0, scale=1.0, pose="stand", skirt=False):
    o = OUTFITS[kind]
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a * scale, b * scale, z + c * scale))
    top, bot = f.a("top_" + kind, o["top"], 0.02, True), f.a("bot_" + kind, o["bot"], 0.02, True)
    skin = f.a("skin", SKIN, 0.0, True)
    shoe = f.a("shoe", (0.03, 0.025, 0.02))
    wl = 0.12 if pose == "walk" else 0.0
    sc = scale
    for s_ in (-1, 1):
        k = s_ * wl
        # legs: tapered, with knee joints, shoes with toe cap
        bot.cyl(P(k, s_ * 0.085, 0.92), P(k * 0.4, s_ * 0.085, 0.48), 0.082 * sc, 0.062 * sc, seg=10)
        bot.sphere(P(k * 0.4, s_ * 0.085, 0.47), (0.062 * sc,) * 3, seg=8, rings=5)
        bot.cyl(P(k * 0.4, s_ * 0.085, 0.47), P(-k * 0.2, s_ * 0.085, 0.09), 0.058 * sc, 0.042 * sc, seg=10)
        shoe.sbox(P(-k * 0.2 - 0.03, s_ * 0.085, 0.05), P(-k * 0.2 + 0.12, s_ * 0.085, 0.05), 0.095 * sc, 0.075 * sc)
        shoe.sphere(P(-k * 0.2 + 0.13, s_ * 0.085, 0.045), (0.05 * sc, 0.048 * sc, 0.038 * sc), seg=8, rings=5)
    if skirt:
        bot.cyl(P(0, 0, 0.50), P(0, 0, 0.98), 0.24 * sc, 0.17 * sc, seg=12)
    # pelvis + chest + shoulders as rounded forms
    bot.sphere(P(0, 0, 0.95), (0.115 * sc, 0.165 * sc, 0.13 * sc), seg=12, rings=8)
    top.sphere(P(0.005, 0, 1.22), (0.115 * sc, 0.185 * sc, 0.27 * sc), seg=14, rings=10)
    top.cyl(P(0.0, 0, 0.98), P(0.005, 0, 1.2), 0.16 * sc, 0.19 * sc, seg=12)
    for s_ in (-1, 1):
        k = -s_ * wl * 1.2
        top.sphere(P(0, s_ * 0.205, 1.38), (0.065 * sc,) * 3, seg=8, rings=6)
        top.cyl(P(0, s_ * 0.205, 1.38), P(k * 0.5, s_ * 0.225, 1.14), 0.052 * sc, 0.043 * sc, seg=8)
        top.sphere(P(k * 0.5, s_ * 0.225, 1.13), (0.043 * sc,) * 3, seg=6, rings=4)
        top.cyl(P(k * 0.5, s_ * 0.225, 1.13), P(k, s_ * 0.235, 0.94), 0.042 * sc, 0.034 * sc, seg=8)
        skin.sphere(P(k, s_ * 0.235, 0.90), (0.040 * sc, 0.024 * sc, 0.055 * sc), seg=8, rings=5)
        skin.sbox(P(k + 0.012, s_ * 0.235, 0.88), P(k + 0.018, s_ * 0.235, 0.80), 0.030 * sc, 0.020 * sc)
        skin.sphere(P(k + 0.03, s_ * 0.215, 0.89), (0.012 * sc, 0.010 * sc, 0.026 * sc), seg=5, rings=4)
    # neck + collar (trapezius slope)
    skin.cyl(P(0.01, 0, 1.40), P(0.015, 0, 1.53), 0.050 * sc, 0.044 * sc, seg=10)
    top.cyl(P(0.0, 0, 1.36), P(0.005, 0, 1.43), 0.085 * sc, 0.060 * sc, seg=10)
    f.a("collar", (0.80, 0.78, 0.72)).cyl(P(0.0, 0, 1.425), P(0.008, 0, 1.455), 0.062 * sc, 0.058 * sc, seg=10)
    # head: cranium + cheek/jaw taper + chin + ears + brow + nose bridge
    skin.sphere(P(0.015, 0, 1.635), (0.094 * sc, 0.082 * sc, 0.105 * sc), seg=14, rings=10)
    skin.sphere(P(0.045, 0, 1.575), (0.072 * sc, 0.066 * sc, 0.062 * sc), seg=12, rings=8)
    skin.sphere(P(0.075, 0, 1.535), (0.034 * sc, 0.040 * sc, 0.032 * sc), seg=8, rings=6)
    skin.sphere(P(0.112, 0, 1.585), (0.020 * sc, 0.015 * sc, 0.026 * sc), seg=6, rings=4)
    skin.sbox(P(0.095, 0, 1.600), P(0.122, 0, 1.578), 0.014 * sc, 0.014 * sc)
    for s_ in (-1, 1):
        skin.sphere(P(0.0, s_ * 0.088, 1.600), (0.014 * sc, 0.008 * sc, 0.028 * sc), seg=6, rings=4)
    eye = f.a("eye", (0.02, 0.015, 0.012))
    brow = f.a("brow", (0.03, 0.025, 0.02))
    for s_ in (-1, 1):
        eye.sphere(P(0.100, s_ * 0.036, 1.622), (0.009 * sc, 0.011 * sc, 0.007 * sc), seg=5, rings=4)
        brow.sbox(P(0.103, s_ * 0.022, 1.646), P(0.100, s_ * 0.058, 1.649), 0.006 * sc, 0.006 * sc)
    f.a("lip", (0.34, 0.16, 0.13)).sbox(P(0.103, -0.016, 1.555), P(0.103, 0.016, 1.555), 0.006 * sc, 0.006 * sc)
    hair = f.a("hair", (0.02, 0.02, 0.02), 0.0, True)
    if o["hat"] not in ("scarf",):
        hair.sphere(P(-0.02, 0, 1.655), (0.090 * sc, 0.086 * sc, 0.088 * sc), seg=12, rings=7)
        hair.sphere(P(-0.045, 0, 1.600), (0.060 * sc, 0.074 * sc, 0.060 * sc), seg=10, rings=6)
    h = o["hat"]
    hc = f.a("hat_" + kind, o["hatc"], 0.01, True)
    if h == "cap":
        hc.cyl(P(0.02, 0, 1.69), P(0.02, 0, 1.76), 0.10 * scale, 0.095 * scale, seg=14)
        hc.cyl(P(0.02, 0, 1.68), P(0.02, 0, 1.695), 0.108 * scale, seg=14)
        f.a("visor", (0.02, 0.02, 0.02)).box(*sorted((P(0.08, 0, 1.68)[0], P(0.19, 0, 1.68)[0])), -0.001, 0.001, 0, 0) if False else None
        hc.sbox(P(0.09, 0, 1.685), P(0.19, 0, 1.675), 0.14 * scale, 0.012 * scale)
        if "band" in o:
            f.a("band", o["band"]).cyl(P(0.02, 0, 1.69), P(0.02, 0, 1.705), 0.101 * scale, seg=14)
    elif h == "straw":
        hc.cyl(P(0.02, 0, 1.68), P(0.02, 0, 1.80), 0.30 * scale, 0.02 * scale, seg=16)
    elif h == "scarf":
        hc.sphere(P(0.0, 0, 1.63), (0.11 * scale, 0.10 * scale, 0.12 * scale), seg=10, rings=7)
    else:
        f.a("hair", (0.02, 0.02, 0.02), 0.0, True).sphere(P(-0.01, 0, 1.64), (0.098 * scale, 0.09 * scale, 0.09 * scale), seg=10, rings=6)
    if o.get("gloves"):
        pass


def cat(f, x, y, yaw, z=0.0, color=(0.25, 0.17, 0.10)):
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, z + c))
    c = f.a("cat", color, 0.02, True)
    c.sphere(P(0, 0, 0.14), (0.18, 0.10, 0.13), seg=10, rings=6)
    c.sphere(P(0.17, 0, 0.26), (0.07, 0.065, 0.065), seg=8, rings=5)
    for s in (-1, 1):
        c.cyl(P(0.17, s * 0.04, 0.31), P(0.17, s * 0.045, 0.37), 0.025, 0.002, seg=4)
    c.cyl(P(-0.16, 0, 0.1), P(-0.3, 0.1, 0.05), 0.03, 0.02, seg=6)
    c.cyl(P(-0.2, 0, 0.1), P(-0.2, 0.0, 0.02), 0.04, seg=6) if False else None


def dog(f, x, y, yaw, z=0.0):
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, z + c))
    c = f.a("dog", (0.45, 0.32, 0.18), 0.02, True)
    c.sphere(P(0, 0, 0.38), (0.3, 0.13, 0.15), seg=10, rings=6)
    c.sphere(P(0.32, 0, 0.5), (0.1, 0.08, 0.09), seg=8, rings=5)
    c.cyl(P(0.4, 0, 0.47), P(0.5, 0, 0.45), 0.04, 0.03, seg=6)
    for sx in (-0.2, 0.2):
        for s in (-1, 1):
            c.cyl(P(sx, s * 0.08, 0.32), P(sx, s * 0.08, 0.0), 0.035, 0.025, seg=6)
    c.cyl(P(-0.28, 0, 0.42), P(-0.45, 0, 0.55), 0.03, 0.015, seg=5)


def crow(f, x, y, z, yaw):
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, z + c))
    c = f.a("crow", (0.015, 0.015, 0.02), 0.01, True)
    c.sphere(P(0, 0, 0.12), (0.14, 0.07, 0.07), seg=8, rings=5)
    c.sphere(P(0.12, 0, 0.19), (0.05, 0.04, 0.045), seg=6, rings=4)
    c.cyl(P(0.15, 0, 0.19), P(0.24, 0, 0.17), 0.016, 0.004, seg=5)
    c.cyl(P(-0.1, 0, 0.1), P(-0.28, 0, 0.06), 0.03, 0.01, seg=5)
    c.cyl(P(0.0, 0.02, 0.06), P(0.0, 0.02, 0.0), 0.006, seg=4)
    c.cyl(P(0.0, -0.02, 0.06), P(0.0, -0.02, 0.0), 0.006, seg=4)


def sparrow(f, x, y, z, yaw):
    T = XF(x, y, yaw)
    P = lambda a, b, c: T((a, b, z + c))
    c = f.a("sparrow", (0.30, 0.22, 0.14), 0.02, True)
    c.sphere(P(0, 0, 0.05), (0.05, 0.03, 0.035), seg=6, rings=4)
    c.sphere(P(0.045, 0, 0.08), (0.025, 0.02, 0.022), seg=6, rings=4)


def build_people():
    f = Fig("people")
    # platform (station): stationmaster by the train, waiting passengers
    P0 = Z_PLAT
    person(f, 6.5, 2.95, -math.pi / 2, "master", z=P0)
    person(f, 12.0, 3.4, math.pi, "man", z=P0)
    person(f, 12.8, 3.1, math.pi * 0.8, "woman", z=P0, skirt=False)
    person(f, 16.5, 2.9, -1.2, "man2", z=P0)
    person(f, 14.5, 3.5, math.pi, "student", z=P0, scale=0.82)
    person(f, 19.0, 3.2, 3.0, "farmer", z=P0, pose="walk")
    # island platform
    iy = (ISLAND[2] + ISLAND[3]) / 2
    person(f, 7.5, iy + 0.4, 0.4, "woman", z=P0)
    person(f, 9.0, iy - 0.4, 3.3, "man", z=P0)
    person(f, 18.0, iy, 0.0, "man2", z=P0, pose="walk")
    # forecourt / road
    person(f, -22.0, 14.9, 0.1, "farmer", pose="walk")
    person(f, -9.5, 11.8, 0.7, "woman")
    person(f, -9.0, 11.2, 0.1, "student", scale=0.65)
    person(f, -12.5, 8.4, -0.4, "man")                    # near the porch
    person(f, 1.2, 13.3, 3.0, "man2")                     # by the three-wheeler
    person(f, -13.0, 16.4, 2.7, "woman", pose="walk")      # at the shop front
    # crossing hut
    person(f, 38.9, 3.2, 3.6, "master")
    # depot workers
    person(f, -14.0, -60.5, 0.0, "worker")                # beside the turntable
    person(f, 24.5, -77.5, 1.2, "worker")
    person(f, -45.0, -33.5, 0.8, "worker")                # in the depot office
    person(f, -42.5, -31.6, 3.7, "worker") if False else None
    person(f, -52.0, -53.0, 0.3, "worker")                # inspection shed
    person(f, 44.0, -66.0, 2.0, "worker")                 # material yard
    # inside the goods shed / shop / inn
    person(f, 8.2, 7.9, 1.2, "man2", z=0.95)
    person(f, -12.0, 21.2, 0.3, "woman", z=0.25)
    person(f, -28.0, 20.6, 0.0, "woman", z=0.78, skirt=False)
    f.build()
    a = Fig("animals")
    cat(a, -3.6, 9.6, 0.4, z=0.0)
    cat(a, -14.5, 16.8, 2.0, z=0.0, color=(0.55, 0.50, 0.42))
    cat(a, 4.0, 3.2, 1.0, z=P0, color=(0.1, 0.1, 0.1))
    dog(a, -20.0, 17.2, 0.2)
    dog(a, 42.5, 8.0, 3.0)
    for (x, y, z, yw) in ((10.0, 8.05, 5.45, 0.2), (14.5, 8.05, 5.45, 2.9), (-27.3, 11.3, 8.55, 1.0), (-52.2, 11.3, 8.55, 4.0),
                         (-61.0, 24.8, 5.45, 0.3), (-30.0, 21.6, 8.15, 2.0)):
        crow(a, x, y, z, yw)
    rng = random.Random(4)
    for k in range(14):
        sparrow(a, rng.uniform(-8, 22), rng.uniform(9.5, 15.5), 0.02, rng.uniform(0, 6.28))
    for k in range(6):
        sparrow(a, rng.uniform(-14, -2), 2.4 + rng.uniform(0, 1.6), Z_PLAT + 0.0, rng.uniform(0, 6.28))
    a.build()


def build_leaves(cam):
    cx, cy = cam[0], cam[1]
    rng = np.random.default_rng(12)
    centres = [(-27.5, 17.9, 7), (36.0, 22.5, 8), (-17.5, 6.8, 5), (29.0, 6.0, 5), (-64.5, 20.5, 4), (-55.8, 16.4, 4), (43.0, 21.0, 4),
               (-42.0, 24.0, 4), (-72.0, 21.0, 8), (-9.0, 12.5, 14), (-60.0, 14.5, 18), (20.0, 14.5, 8)]
    V, T, C = [], [], []
    o = 0
    for (x, y, r) in centres:
        n = int(r * r * 28)
        for _ in range(n):
            a = rng.uniform(0, 6.28)
            rr = r * math.sqrt(rng.uniform(0, 1))
            px, py = x + math.cos(a) * rr * 1.4, y + math.sin(a) * rr * 0.8
            if math.hypot(px - cx, py - cy) > 130:
                continue
            if -19 < px < 27.5 and 0.5 < py < 11.5:          # platform/station area handled separately
                continue
            s = rng.uniform(0.05, 0.10)
            ang = rng.uniform(0, 6.28)
            ca, sa = math.cos(ang), math.sin(ang)
            pts = [(-s, 0), (s, 0), (0, s * 0.8 * rng.choice([-1, 1]) + (s * 0.3))]
            z = 0.03 + rng.uniform(0, 0.02)
            for (u, v) in pts:
                V.append((px + u * ca - v * sa, py + u * sa + v * ca, z))
            col = [(0.55, 0.20, 0.03), (0.60, 0.40, 0.05), (0.35, 0.18, 0.05), (0.70, 0.52, 0.08), (0.45, 0.10, 0.03)][rng.integers(0, 5)]
            col = np.array(col) * rng.uniform(0.7, 1.2)
            C += [list(col) + [1.0]] * 3
            T.append((o, o + 1, o + 2))
            o += 3
    if V:
        np_mesh("fallen_leaves", np.array(V), np.array(T), M["leaf"], "Vegetation", colors=np.array(C))


def build_puddles():
    spots = [(-40, 14.2, 1.8, 0.7), (-62, 14.9, 1.4, 0.55), (-85, 14.4, 2.0, 0.8), (-6, 15.5, 1.5, 0.6), (-20, 10.0, 1.0, 0.5),
             (6, 11.4, 1.3, 0.6), (38.0, 28, 0.9, 1.7), (38.2, 60, 0.9, 2.0), (37.8, -60, 1.0, 2.2), (-30, 13.5, 1.2, 0.5),
             (16, 13.0, 1.2, 0.6), (46, -70, 2.0, 1.2), (-8, 8.0, 0.8, 0.4)]
    mat = lib.mat_plain("lf_puddle", (0.14, 0.12, 0.09), rough=0.03)
    rng = np.random.default_rng(5)
    for k, (x, y, rx, ry) in enumerate(spots):
        n = 28
        V = [(x, y, 0.022)]
        for i in range(n):
            a = 2 * math.pi * i / n
            w = 1.0 + 0.18 * math.sin(3 * a + k) + 0.1 * math.sin(5 * a + 2 * k)
            V.append((x + math.cos(a) * rx * w, y + math.sin(a) * ry * w, 0.022))
        T = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
        np_mesh(f"puddle_{k}", np.array(V), np.array(T), mat, "Roads")


def build_life(cam):
    build_people()
    build_leaves(cam)
    build_puddles()
