import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""kit2: per-station bespoke design. Curved alignments, multi-volume station buildings, canopies, terrain, road networks, road-aligned towns.
Every object is built in a local frame and parented via (Sub)Zone empties."""
import json, math, random, os, zlib
from common import *
import lib, props, rooms, houses, core, trackkit, veg, sig
from props import G, face_plane
import kit
from kit import Zone, ST, NET, boards, mats, hip_roof, footbridge, snowshed
import kit_town as KT
from mathutils import noise as mn, Vector


class SubZone:
    def __init__(self, origin=(0, 0, 0), yaw=0.0):
        self.origin, self.yaw = origin, yaw

    def __enter__(self):
        self.before = set(bpy.data.objects.keys())
        import rooms
        rooms.SZ_STACK.append((tuple(self.origin), float(self.yaw)))
        return self

    def __exit__(self, *a):
        import rooms
        rooms.SZ_STACK.pop()
        e = bpy.data.objects.new("sub", None)
        e.location, e.rotation_euler = self.origin, (0, 0, self.yaw)
        lib.link(e, "Zones")
        for n in set(bpy.data.objects.keys()) - self.before:
            o = bpy.data.objects[n]
            if o.parent is None and o is not e:
                o.parent = e


def mats2():
    mats()
    if "pl_green" not in M:
        for k, c in (("pl_green", (0.33, 0.45, 0.36)), ("pl_cream", (0.78, 0.72, 0.52)), ("pl_blue", (0.36, 0.50, 0.62)),
                     ("pl_pink", (0.72, 0.52, 0.48)), ("pl_ochre", (0.70, 0.52, 0.22)), ("pl_grey", (0.55, 0.56, 0.54))):
            M[k] = lib.mat_plaster("kit_" + k, c, dirt=0.7)
        M["water"] = lib.mat_water("kit_water")
        M["sand"] = lib.mat_plain("kit_sand", (0.60, 0.53, 0.37), rough=0.97)
        M["tin_blue"] = lib.mat_paint("kit_tinblue", (0.20, 0.30, 0.42), rough=0.5, rust=0.5)
        M["tin_green"] = lib.mat_paint("kit_tingreen", (0.18, 0.34, 0.24), rough=0.5, rust=0.5)
        M["snow"] = lib.mat_plain("kit_snow", (0.86, 0.90, 0.96), rough=0.9, spec=0.25)


# ----------------------------------------------------------------- alignment
LH = 160
REACH = {}   # sid -> (後ろ側の線路長, 前側の線路長); kit4 が隣駅間隔から設定


CURVE_OVERRIDE = {}   # sid -> R (弧で曲げて両端の向きを隣駅に合わせる駅)


def track_offsets(plat, ntr):
    """プラットホーム形式ごとの線路の横オフセット(中心線からの距離)。ホーム縁から線路中心まで >=1.7m を保つ。
    island: ホームは線0-1の間。dual: A面ホームは線0の北、B面ホームは線1の南(ntr>=3 のとき線2はB面の反対側に置き島式化)。"""
    if plat == "island":
        return [0, -8.4] + [-8.4 - 4.6 * k for k in range(1, ntr - 1)]
    if plat == "island2":
        return [0, -8.4, -13.0, -21.4] + [-21.4 - 4.6 * k for k in range(1, ntr - 3)]
    if plat == "dual" and ntr >= 3:
        return [0, -4.6] + [-10.7 - 4.6 * (k - 2) for k in range(2, ntr)]
    return [-4.6 * k for k in range(ntr)]


def centerline(kind="straight", R=0.0, amp=0.0, flat=True):
    xs = np.arange(-LH, LH + 0.01, 1.0)
    if kind == "arc" and R:
        ys = np.sign(R) * (abs(R) - np.sqrt(abs(R) ** 2 - xs ** 2))
    elif kind == "S":
        ys = amp * np.sin(xs / LH * math.pi * 1.0)
    else:
        ys = np.zeros_like(xs)
    # 駅の両端は直線に戻して(位置・向きとも)、駅間線路と滑らかにつなぐ
    if flat:
        t = np.clip((np.abs(xs) - 45.0) / 60.0, 0, 1)
        ys = ys * (1 - t * t * (3 - 2 * t))
    return np.stack([xs, ys], -1)


def offs(P, d):
    t, n = trackkit.frames(P)
    return P + n * d


def frame_at(P, x):
    i = int(np.clip(round(x + LH), 1, len(P) - 2))
    t, n = trackkit.frames(P)
    return P[i], math.atan2(t[i, 1], t[i, 0]), n[i]


def strip(P, d0, d1, xa, xb, z0, z1, mat, name, col="Station", bevel=0.0):
    ia, ib = int(xa + LH), int(xb + LH)
    A = P[ia:ib + 1]
    t, n = trackkit.frames(P)
    N = n[ia:ib + 1]
    side0 = A + N * d0
    side1 = A + N * d1
    poly = [tuple(p) for p in side0] + [tuple(p) for p in side1[::-1]]
    a = lib.Acc(name, mat, col, bevel=bevel)
    a.extrude_z(poly, z0, z1)
    a.build()


def platform_strip(P, d0, d1, xa, xb, name):
    s = 1.0 if d1 > d0 else -1.0
    strip(P, d0, d1, xa, xb, -0.25, Z_PLAT - 0.05, M["concrete"], name + "_body")
    strip(P, d0 + 0.5 * s, d1 - 0.05 * s, xa + 0.05, xb - 0.05, Z_PLAT - 0.06, Z_PLAT, M["plat_top"], name + "_top")
    strip(P, d0, d0 + 0.5 * s, xa, xb, Z_PLAT - 0.06, Z_PLAT + 0.03, M["concrete"], name + "_edge")
    strip(P, d0 + 0.6 * s, d0 + 0.68 * s, xa, xb, Z_PLAT, Z_PLAT + 0.008, M["white_line"], name + "_line")
    # 穂波野(core.build_platform)に倣う: 縁の石の笠木 と ホーム両端のスロープ(階段状に低くなる)
    if "stone" in M:
        strip(P, d0, d0 + 0.16 * s, xa, xb, Z_PLAT + 0.02, Z_PLAT + 0.07, M["stone"], name + "_cope")
    for i in range(5):
        top = Z_PLAT * (1.0 - (i + 1) / 5.5)
        strip(P, d0 + 0.5 * s, d1 - 0.05 * s, xb + 0.9 * i, xb + 0.9 * (i + 1), -0.25, top, M["concrete"], f"{name}_rampB{i}")
        strip(P, d0 + 0.5 * s, d1 - 0.05 * s, xa - 0.9 * (i + 1), xa - 0.9 * i, -0.25, top, M["concrete"], f"{name}_rampA{i}")


# ----------------------------------------------------------------- station building volumes
def gable_y(gr, gw, x0, x1, y0, y1, zw, rise, ov=0.7, gov=0.5, thick=0.14):
    xm = (x0 + x1) / 2
    prof = [(x0 - ov, zw - 0.18), (xm, zw + rise), (x1 + ov, zw - 0.18), (x1 + ov, zw - 0.18 - thick), (xm, zw + rise - thick - 0.04), (x0 - ov, zw - 0.18 - thick)]
    gr.extrude_y(prof, y0 - gov, y1 + gov)
    gw.extrude_y([(x0, zw), (xm, zw + rise - 0.12), (x1, zw)], y0, y1)
    gr.box(xm - 0.12, xm + 0.12, y0 - gov, y1 + gov, zw + rise - 0.06, zw + rise + 0.08)


def shed_roof(gr, x0, x1, y0, y1, zw, rise, ov=0.6, thick=0.12, high='N'):
    za, zb = (zw, zw + rise) if high == 'N' else (zw + rise, zw)
    gr.extrude_x([(y0 - ov, za - 0.15), (y1 + ov, zb - 0.15), (y1 + ov, zb - 0.15 - thick), (y0 - ov, za - 0.15 - thick)], x0 - ov, x1 + ov)


def make_ops(v, rng, zf, door_side='S'):
    """Openings per side for a volume. v keys: x0,x1,y0,y1,nfl,skip(set)."""
    ops = {"S": [], "N": [], "W": [], "E": []}
    nfl = v["nfl"]
    for side, (a0, a1) in (("S", (v["x0"], v["x1"])), ("N", (v["x0"], v["x1"])), ("W", (v["y0"], v["y1"])), ("E", (v["y0"], v["y1"]))):
        if side in v.get("skip", ()):
            continue
        L = a1 - a0
        step = rng.choice([2.2, 2.6, 3.0]) if side in "SN" else 3.2
        n = max(1, int((L - 1.2) // step))
        for f in range(nfl):
            z0 = zf + f * 3.0 + 1.0
            for i in range(n):
                c = a0 + (i + 0.5) * L / n
                w = rng.choice([1.0, 1.2, 1.4]) if side in "SN" else 1.0
                if f == 0 and ((side == door_side and i == n // 2) or (side == v.get("door2") and i == n // 2)):
                    ops[side].append((c - 0.7, c + 0.7, zf, zf + 2.05, 'door' if side == 'N' else 'open'))
                else:
                    ops[side].append((c - w / 2, c + w / 2, z0, z0 + 1.1 + rng.choice([0, 0.2, 0.4]), 'glass'))
    return ops


def volume(g, v, rng, st, interior=False):
    zf = Z_PLAT + 0.30 if v.get("ground", True) else v.get("zf", Z_PLAT + 0.3)
    nfl = v["nfl"]
    zh = zf + 2.9 + (nfl - 1) * 3.0
    x0, x1, y0, y1 = v["x0"], v["x1"], v["y0"], v["y1"]
    wall = v.get("wall", "wall")
    g.a("stone", bevel=0.015).box(x0 - 0.08, x1 + 0.08, y0 - 0.08, y1 + 0.08, (-0.25 if v.get("ground", True) else zf - 0.7), zf - 0.02)   # 橋上通路は床版のみ(旧: 地面まで中実の石ブロックで線路を塞いでいた)
    ops = make_ops(v, rng, zf, v.get("door", 'S'))
    rooms.shell(g, x0, x1, y0, y1, zf - 0.02, zh, t=0.14, ops=ops, wall=wall)
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        g.a("wood_dark", bevel=0.004).box(cx - 0.09, cx + 0.09, cy - 0.09, cy + 0.09, zf - 0.02, zh + 0.1)
    for f in range(1, nfl):                       # storey slab + belt
        zz = zf + f * 3.0
        g.a("floor").box(x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, zz - 0.2, zz)
        g.a("wood_dark").box(x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, zz - 0.12, zz + 0.1)
    roof = v.get("roof", "gable")
    ridge = v.get("ridge", "x")
    rise = v.get("rise", 1.9)
    gr, gw = g.a(v.get("roofmat", "roof")), g.a(wall)
    if roof == "gable":
        (props.gable_roof(gr, gw, x0, x1, y0, y1, zh, rise, ov=0.8, gov=0.5) if ridge == 'x' else gable_y(gr, gw, x0, x1, y0, y1, zh, rise, ov=0.8, gov=0.5))
    elif roof in ("hip", "pyr"):
        hip_roof(gr, x0, x1, y0, y1, zh, rise + (0.8 if roof == "pyr" else 0), ov=0.85)
    elif roof == "shed":
        shed_roof(gr, x0, x1, y0, y1, zh, v.get("rise", 1.0), high=v.get("high", 'N'))
    elif roof == "saw":
        n = max(2, int((x1 - x0) // 3.5))
        for i in range(n):
            xa, xb = x0 + i * (x1 - x0) / n, x0 + (i + 1) * (x1 - x0) / n
            gr.extrude_x([(y0 - 0.3, zh), (y1 + 0.3, zh + 1.6), (y1 + 0.3, zh + 0.02), (y0 - 0.3, zh - 0.1)], xa, xb)
            g.a("glass").box(xa, xa + 0.05, y0, y1, zh, zh + 1.5)
    else:   # flat parapet
        g.a("concrete", bevel=0.01).box(x0 - 0.25, x1 + 0.25, y0 - 0.25, y1 + 0.25, zh, zh + 0.25)
        g.a("concrete").box(x0 - 0.25, x1 + 0.25, y0 - 0.25, y0 - 0.12, zh + 0.25, zh + 0.8)
        g.a("concrete").box(x0 - 0.25, x1 + 0.25, y1 + 0.12, y1 + 0.25, zh + 0.25, zh + 0.8)
    if interior:
        rooms.floor_boards(g, x0 + 0.14, x1 - 0.14, y0 + 0.14, y1 - 0.14, zf)
        rooms.ceiling(g, x0 + 0.14, x1 - 0.14, y0 + 0.14, y1 - 0.14, zf + 2.85)
        xo = x0 + (x1 - x0) * 0.62
        rooms.partition(g, 'y', xo, y0 + 0.14, y1 - 0.14, zf, zf + 2.85, doors=[((y0 + y1) / 2 - 0.5, (y0 + y1) / 2 + 0.5)], kind="wood_dark")
        nb = max(2, int((xo - x0 - 1.5) // 2.4))
        for k in range(nb):
            props.bench(g, x0 + 1.6 + k * 2.4, y1 - 0.6, 1.8, face='N', z=zf - 0.3)
        rooms.pot_stove(g, x0 + (xo - x0) * 0.4, (y0 + y1) / 2, zf)
        rooms.desk(g, xo + 1.2, y0 + 1.0, zf, face='S')
        rooms.desk(g, xo + 2.4, y1 - 1.2, zf, face='N', papers=True)
        rooms.shelf(g, xo + 0.5, min(x1 - 0.5, xo + 3.0), y1 - 0.45, zf, face='S', goods="jars", seed=3)
        for k_, nm_ in enumerate(("poster0", "poster1", "notice", "poster2")):
            ip = f"kit/{st['id']}_{nm_}.png"
            if os.path.exists(f"{_R}/tex/{ip}"):
                face_plane(f"k2in_{st['id']}_{k_}", ip, 'S', x0 + 1.5 + k_ * 1.4, y1 - 0.16, zf + 1.1, 0.75, h=1.0, off=0.0)
        try:
            import kit8
            _opn = [o for o in ops.get(v.get("door", "S"), []) if o[4] in ("open", "door")]
            _c = (_opn[0][0] + _opn[0][1]) / 2 if _opn else (x0 + xo) / 2
            if (xo - x0) >= 6.0 and (y1 - y0) >= 5.0 and v.get("door", "S") == "S":
                kit8.concourse(g, x0 + 0.14, x1 - 0.14, y0 + 0.14, y1 - 0.14, zf, xo, _c, st, rng)
        except Exception as _e:
            print("concourse failed", st.get("id"), _e)
        rooms.lamp_point(x0 + (xo - x0) * 0.5, (y0 + y1) / 2, zf + 2.5, 90)
        rooms.lamp_point(xo + 2.0, (y0 + y1) / 2, zf + 2.5, 90)
    return zh


def plan_volumes(plan, w, d, nfl, roof, wall, rng):
    """Return list of volumes in the building frame (x along track, y = away from track, front wall at y=0)."""
    main = dict(x0=0, x1=w, y0=0, y1=d, nfl=nfl, roof=roof, wall=wall, door='S', ridge='x')
    vs = [main]
    if plan == "L":
        wd = rng.uniform(6, 9)
        main["skip"] = ()
        vs.append(dict(x0=w - rng.uniform(4.5, 6), x1=w, y0=d, y1=d + wd, nfl=nfl, roof=roof, wall=wall, ridge='y', skip=("S",), door='N'))
    elif plan == "T":
        pw = rng.uniform(4.5, 6.5)
        c = w * rng.uniform(0.35, 0.6)
        vs.append(dict(x0=c - pw / 2, x1=c + pw / 2, y0=d, y1=d + rng.uniform(3.5, 5), nfl=nfl, roof="gable", wall=wall, ridge='y', skip=("S",), door='N', rise=1.8))
    elif plan == "U":
        wd = rng.uniform(5, 8)
        for xa in (0, w - 4.8):
            vs.append(dict(x0=xa, x1=xa + 4.8, y0=d, y1=d + wd, nfl=nfl, roof=roof, wall=wall, ridge='y', skip=("S",), door='N'))
    elif plan == "TW":
        tw = 4.0
        vs.append(dict(x0=-tw, x1=0, y0=-0.5, y1=tw - 0.5, nfl=3 + (nfl > 1), roof="pyr", wall=wall, skip=("E",), door='S', rise=2.6))
    elif plan == "A":
        aw = rng.uniform(5, 8)
        vs.append(dict(x0=w, x1=w + aw, y0=0.8, y1=d - 0.8, nfl=1, roof="shed", wall=rng.choice(["tin", "wall", "wood"]), skip=("W",), door='S', rise=0.9, roofmat=rng.choice(["tin", "roof"])))
    elif plan == "AA":     # annex on both ends
        for xa, xb in ((-5.5, 0), (w, w + 5.5)):
            vs.append(dict(x0=xa, x1=xb, y0=1.0, y1=d - 1.0, nfl=1, roof="shed", wall=rng.choice(["tin", "wall"]), skip=("E" if xa < 0 else "W",), door='S', rise=0.8, roofmat="tin"))
    return vs


def canopy(kind, xa, xb, ztop=3.7, depth=2.6, gm=None):
    """Platform canopy in the building frame (y<0 is the platform side)."""
    if kind == "none":
        return
    g = G("k2_canopy", "Station")
    posts = np.arange(xa, xb + 0.1, 4.0)
    for x in posts:
        g.a("wood_dark" if kind != "steel" else "iron_black", bevel=0.01).box(x - 0.09, x + 0.09, -depth - 0.09, -depth + 0.09, Z_PLAT, Z_PLAT + ztop)
        g.a("wood_dark" if kind != "steel" else "iron_black").sbox((x, -depth, Z_PLAT + ztop - 0.5), (x, -0.1, Z_PLAT + ztop + 0.2), 0.1, 0.16, up=(1, 0, 0))
    if kind in ("shed", "wood", "steel"):
        g.a("tin" if kind != "steel" else "roof").extrude_x([(-depth - 0.5, Z_PLAT + ztop - 0.1), (0.1, Z_PLAT + ztop + 0.45), (0.1, Z_PLAT + ztop + 0.38), (-depth - 0.5, Z_PLAT + ztop - 0.17)], xa - 0.5, xb + 0.5)
    elif kind == "curve":
        prof = []
        for a_ in np.linspace(0, math.pi / 2, 9):
            prof.append((-depth - 0.5 + (depth + 0.6) * (1 - math.cos(a_)), Z_PLAT + ztop - 0.1 + 0.55 * math.sin(a_)))
        prof2 = [(y, z - 0.07) for (y, z) in prof[::-1]]
        g.a("iron_black").extrude_x(prof + prof2, xa - 0.5, xb + 0.5)
    elif kind == "saw":
        n = int((xb - xa) // 4)
        for i in range(n):
            x0_, x1_ = xa + i * (xb - xa) / n, xa + (i + 1) * (xb - xa) / n
            g.a("tin").extrude_x([(-depth - 0.5, Z_PLAT + ztop), (0.1, Z_PLAT + ztop + 0.9), (0.1, Z_PLAT + ztop + 0.04), (-depth - 0.5, Z_PLAT + ztop - 0.07)], x0_, x1_)
            g.a("glass").box(x0_, x0_ + 0.04, -depth - 0.5, 0.1, Z_PLAT + ztop + 0.05, Z_PLAT + ztop + 0.9) if False else None
    g.build()


# ----------------------------------------------------------------- terrain / roads / town
def hill(cx, cy, rx, ry, h, name, seed=0):
    """丘: 2段のノイズで尾根と谷筋をつけ、草地(高い所は岩肌ぎみ)。戻り値=(Z格子, 地表高さ関数f(x,y))。"""
    nx, ny = 56, 56
    us, vs = np.linspace(-1, 1, nx), np.linspace(-1, 1, ny)
    U, V = np.meshgrid(us, vs)
    rho = np.sqrt(U * U + V * V)

    def zf(u, v, r):
        base = h * max(0.0, 1 - r ** 2) ** 1.25
        n1 = 0.75 + 0.5 * mn.noise(Vector((seed + u * 2.2, v * 2.2, 1.0)))
        n2 = 1.0 + 0.22 * mn.noise(Vector((seed + u * 7.0, v * 7.0, 3.0)))          # 尾根・谷筋
        n3 = 1.0 + 0.06 * mn.noise(Vector((seed + u * 21.0, v * 21.0, 5.0)))         # 細かな凹凸
        return base * n1 * n2 * n3

    Z = np.array([[zf(U[j, i], V[j, i], rho[j, i]) for i in range(nx)] for j in range(ny)])
    core.grid_mesh(name, cx + U[0] * rx, cy + V[:, 0] * ry, Z, M["grass_ground"], "Terrain", smooth=True)

    def f(x, y):
        u, v = (x - cx) / rx, (y - cy) / ry
        if abs(u) >= 1 or abs(v) >= 1:
            return 0.0
        fi, fj = (u + 1) / 2 * (nx - 1), (v + 1) / 2 * (ny - 1)
        i0, j0 = int(fi), int(fj)
        i1, j1 = min(i0 + 1, nx - 1), min(j0 + 1, ny - 1)
        a, b = fi - i0, fj - j0
        return float(Z[j0, i0] * (1 - a) * (1 - b) + Z[j0, i1] * a * (1 - b) + Z[j1, i0] * (1 - a) * b + Z[j1, i1] * a * b)
    return Z, f


BLDS, TREES = {}, {}        # K8: 駅ID→[(x,y,yaw,w,d)] / [(x,y,r)]  (建物と樹木、互いの重なりを避けるため)


def _bld_hit(sid, x, y, r):
    """点(x,y)に半径rの樹冠を置くと既存建物(OBB)に食い込むか。"""
    for (bx_, by_, yaw_, w_, d_) in BLDS.get(sid, []):
        c, s_ = math.cos(-yaw_), math.sin(-yaw_)
        lx = c * (x - bx_) - s_ * (y - by_)
        ly = s_ * (x - bx_) + c * (y - by_)
        m = r * 0.7
        if -m <= lx <= w_ + m and -m <= ly <= d_ + m:
            return True
    return False


def _tree_hit_bld(sid, o, yaw, w, d):
    """これから置く建物(原点o,向きyaw,幅w,奥行d)が既存樹木の樹冠に食い込むか。"""
    c, s_ = math.cos(-yaw), math.sin(-yaw)
    for (tx, ty, r) in TREES.get(sid, []):
        lx = c * (tx - o[0]) - s_ * (ty - o[1])
        ly = s_ * (tx - o[0]) + c * (ty - o[1])
        m = r * 0.7
        if -m <= lx <= w + m and -m <= ly <= d + m:
            return True
    return False


def scatter_trees(rng, cx, cy, rx, ry, n, kinds=("sugi", "zelkova"), hmax=0.0, zfun=None):
    for i in range(n):
        a, r = rng.uniform(0, 6.283), math.sqrt(rng.random())
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        k = rng.choice(kinds)
        if CUR_SID[0] and near_track(x, y, 7.0):
            continue
        _r = {"sugi": 2.4, "persimmon": 2.8}.get(k, 5.6)
        _sid = CUR_SID[0]
        if _bld_hit(_sid, x, y, _r) or any((x - tx) ** 2 + (y - ty) ** 2 < ((_r + tr) * 0.7) ** 2 for tx, ty, tr in TREES.get(_sid, [])):
            continue                                                  # K8: 建物・既存樹木に重なる位置には植えない
        TREES.setdefault(_sid, []).append((x, y, _r))
        before = set(bpy.data.objects.keys()) if zfun else None
        if k == "sugi":
            veg.sugi(x, y, h=rng.uniform(10, 17), r=rng.uniform(1.5, 2.2), seed=rng.randint(0, 9999))
        elif k == "persimmon":
            veg.persimmon(x, y, seed=rng.randint(0, 9999))
        else:
            veg.CARD_SCALE = float(os.environ.get('TREE_CARDS', '0.5'))   # Q14: 0.22だと葉が疎で塊状に見える → 0.5(.blend軽量化は VEG_LIGHT で行う)
            veg.zelkova(x, y, h=rng.uniform(8, 12), rad=rng.uniform(3.8, 5.4), seed=rng.randint(0, 9999))
            veg.CARD_SCALE = 1.0
        if zfun:
            dz = zfun(x, y)
            if dz > 0.05:
                for nm in set(bpy.data.objects.keys()) - before:
                    bpy.data.objects[nm].location.z += dz - 0.2


def pond(cx, cy, rx, ry, name):
    a = lib.Acc(name, M["water"], "Ground", closed=True)
    poly = [(cx + rx * math.cos(t) * (1 + 0.08 * math.sin(3 * t)), cy + ry * math.sin(t) * (1 + 0.1 * math.cos(2 * t))) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    a.extrude_z(poly, -0.3, 0.018)
    a.build()


def paddies(x0, x1, y0, y1, name, rng):
    a = lib.Acc(name, M["paddy"], "Ground")
    lev = lib.Acc(name + "_lev", M["soil"], "Ground")
    nx, ny = max(1, int((x1 - x0) // 28)), max(1, int((y1 - y0) // 20))
    for i in range(nx):
        for j in range(ny):
            xa, xb = x0 + i * (x1 - x0) / nx, x0 + (i + 1) * (x1 - x0) / nx
            ya, yb = y0 + j * (y1 - y0) / ny, y0 + (j + 1) * (y1 - y0) / ny
            a.box(xa + 0.3, xb - 0.3, ya + 0.3, yb - 0.3, -0.05, 0.03)
            lev.box(xa - 0.3, xa + 0.3, ya, yb, -0.05, 0.28)
            lev.box(xa, xb, ya - 0.3, ya + 0.3, -0.05, 0.28)
    a.build()
    lev.build()


def road_pts(style, ry):
    xs = np.arange(-150, 151, 3.0)
    if style == "curve":
        ys = ry + 9 * np.sin(xs / 55.0)
    elif style == "diag":
        ys = ry + xs * 0.12
    elif style == "bend":
        ys = ry + 14 * np.tanh(xs / 40.0)
    else:
        ys = ry + 0 * xs
    return np.stack([xs, ys], -1)


def road_geom(pts, w=4.6, name="k2_road"):
    core.ribbon(name, [tuple(p) for p in pts[::2]], w, M["road"])


def warehouse(w, d, rng, name, sign=None):
    g = G(name, "Buildings")
    wall = g.a(rng.choice(["tin", "tin_blue", "tin_green"]), bevel=0.01)
    wall.box(0, w, 0, d, 0.0, 4.4)
    g.a("dark_glass").box(w * 0.2, w * 0.5, -0.02, 0.0, 0.0, 3.4)
    g.a("wood_dark").box(w * 0.2 - 0.1, w * 0.5 + 0.1, -0.06, -0.02, 3.4, 3.55)
    for xx in np.linspace(0.6, w - 0.6, int(w // 3)):
        g.a("glass").box(xx - 0.4, xx + 0.4, -0.01, 0.0, 3.2, 3.9)
    g.a("tin").extrude_x([(-0.4, 4.3), (d / 2, 5.8), (d + 0.4, 4.3), (d + 0.4, 4.2), (d / 2, 5.7), (-0.4, 4.2)], -0.2, w + 0.2)
    g.build()
    if sign:
        face_plane(name + "_s", sign, 'S', w * 0.5, -0.05, 3.6, 3.0, h=0.85, off=0.0)


def danchi(w, d, rng, name, floors=5):
    """団地(RC中層住棟): 長いスラブ、バルコニー帯、階段室、フラット屋根。"""
    g = G(name, "Buildings")
    hf = 2.7
    H = floors * hf
    wall = g.a(rng.choice(["concrete", "pl_cream", "pl_grey"]), bevel=0.01)
    wall.box(0, w, 0, d, 0.0, H)
    gl = g.a("glass")
    bal = g.a("concrete")
    nb = max(3, int(w // 3.2))
    for f in range(floors):
        z0 = f * hf
        for i in range(nb):
            xx = (i + 0.5) * w / nb
            gl.box(xx - 0.9, xx + 0.9, -0.03, 0.0, z0 + 1.0, z0 + 2.2)
            bal.box(xx - 1.2, xx + 1.2, -0.7, 0.0, z0 + 0.0, z0 + 0.12)
            bal.box(xx - 1.2, xx + 1.2, -0.7, -0.62, z0 + 0.0, z0 + 1.0)
    for xs in (w * 0.33, w * 0.66):      # 階段室
        g.a("concrete").box(xs - 1.6, xs + 1.6, d, d + 1.2, 0.0, H + 1.0)
        g.a("dark_glass").box(xs - 0.6, xs + 0.6, d + 1.2, d + 1.23, 1.0, H - 0.5)
    g.a("concrete").box(-0.15, w + 0.15, -0.15, d + 0.15, H, H + 0.35)
    g.build()


def prefab_house(w, d, rng, name):
    """新興住宅地の2階建て(プレハブ風): 箱形、片流れ屋根、色パネル、ガレージ。"""
    g = G(name, "Buildings")
    H = 6.0
    g.a(rng.choice(["pl_cream", "pl_grey", "pl_blue", "pl_green", "pl_ochre"]), bevel=0.01).box(0, w, 0, d, 0.0, H)
    gl = g.a("glass")
    for f in range(2):
        for xx in np.linspace(1.4, w - 1.4, max(2, int(w // 3))):
            gl.box(xx - 0.7, xx + 0.7, -0.03, 0.0, 0.9 + f * 2.9, 2.2 + f * 2.9)
    g.a("wood_dark").box(w * 0.55, w * 0.9, -0.03, 0.0, 0.0, 2.2)      # 玄関/ガレージ
    g.a(rng.choice(["tin_blue", "tin_green", "tin", "kawara"])).extrude_x([(-0.5, H), (d + 0.5, H + 1.4), (d + 0.5, H + 1.25), (-0.5, H - 0.15)], -0.3, w + 0.3)
    g.build()


def put_building(kind, x, y, yaw, w, d, rng, st, k, sid, dens):
    BLDS.setdefault(sid, []).append((x, y, yaw, w, d))
    sign_names = [n for n in ("sign_shokudo", "sign_shoten", "sign_ryokan", "sign_riyo", "sign_kusuri", "sign_sakaya") if KT.img(sid, n)]
    sign = KT.img(sid, rng.choice(sign_names)) if sign_names else None
    with SubZone((x, y, 0), yaw):
        if kind == "farm":
            houses.farmhouse2(1.75, 1.75, w=(w - 3.5) / 1.25 * rng.uniform(0.85, 1.25), d=(d - 3.5) / 1.3 * rng.uniform(0.85, 1.3), name=f"k2f{k}", variant=rng.randint(0, 1), seed=k,
                              roofmat=rng.choice(ROOFS.get(sid, ["kawara", "tin", "tin_blue", "tin_green"])))
        elif kind == "shop":
            houses.shop2(0, 0, w=max(w, 7.5), d=max(d, 6.0), name=f"k2s{k}")
        elif kind == "kura":
            houses.kura2(0, 0, name=f"k2k{k}")
        elif kind == "inn":
            houses.inn2(0, 0, w=13.5, d=8.0, name=f"k2i{k}")
        elif kind == "ware":
            warehouse(w, d, rng, f"k2w{k}", sign)
        elif kind == "danchi":
            danchi(w, d, rng, f"k2d{k}", floors=rng.choice([4, 5, 5, 6]))
        elif kind == "pre":
            prefab_house(w, d, rng, f"k2p{k}")
        else:
            wall = rng.choice(["wall", "plasterw", "pl_cream", "pl_green", "pl_blue", "pl_ochre", "brick", "pl_pink", "wood"] if dens < 0.7 else ["plasterw", "pl_grey", "brick", "concrete", "pl_cream", "pl_blue"])
            fl = 2 if (dens > 0.55 and rng.random() < 0.7) else 1
            if dens > 0.85 and rng.random() < 0.4:
                fl = 3
            KT.shopfront(sid, 0, 0, w, d, fl, wall, sign, face='S', name=f"k2sf{k}", roof="gable" if dens < 0.65 or rng.random() < 0.4 else "flat",
                         poster=KT.img(sid, f"poster{rng.randint(0, 3)}"), rng=rng)


import zlib
ROOFS = {}
for _i, _s in enumerate(["M05","M07","M09","M10","M11","M12","M13","L01","M15","M17","M18","Y02","Y03","Y04","S02","S03","S04","M04","M08"]):
    _r = random.Random(zlib.crc32(_s.encode()))
    ROOFS[_s] = _r.sample(["kawara", "tin", "tin_blue", "tin_green", "kawara", "tin"], 3)
STYLES = {"rural": [("farm", 6), ("kura", 1), ("shop", 1)], "suburb": [("sf", 5), ("farm", 3), ("shop", 1)], "urban": [("sf", 9), ("shop", 1)],
          "port": [("ware", 3), ("sf", 3), ("farm", 2), ("shop", 1)], "onsen": [("inn", 2), ("sf", 4), ("farm", 2)], "forest": [("farm", 5), ("kura", 1)],
          "alpine": [("farm", 3), ("inn", 1), ("sf", 2)], "freight": [("ware", 6), ("sf", 1)],
          "newtown": [("danchi", 4), ("pre", 5), ("shop", 1)], "campus": [("pre", 4), ("danchi", 2), ("shop", 1)], "airport": [("ware", 5), ("pre", 2)]}


_EXC = {}
EXC_R = {"viaduct": 11.0, "arch": 14.0, "truss": 14.0, "river": 24.0, "cut": 14.0, "embank": 10.0, "tunnel": 20.0, "shed": 10.0, "over": 12.0, "trestle": 12.0}


def struct_excl(sid):
    """構造物(高架・橋・川・切通し等)の占有帯を、ゾーンのローカル座標の点列+半径で返す。geo.json を使う(無ければ空)。"""
    if sid in _EXC:
        return _EXC[sid]
    out = []
    try:
        import json, os
        gp = f"{_R}/net/geo.json"
        g = json.load(open(gp))
        st = g["stations"].get(sid)
        if st:
            yaw = math.radians(st["yaw"])
            c, s_ = math.cos(-yaw), math.sin(-yaw)
            for l in g["links"]:
                for it in l["items"]:
                    r = EXC_R.get(it["kind"])
                    if not r:
                        continue
                    for x, y in it["pts"]:
                        dx, dy = x - st["x"], y - st["y"]
                        lx, ly = c * dx - s_ * dy, s_ * dx + c * dy
                        if abs(lx) < 260 and abs(ly) < 260:
                            out.append((lx, ly, r))
    except Exception as e:
        print("struct_excl fail", e)
    _EXC[sid] = out
    return out


_TRKPTS = {}
CUR_SID = [None]


def near_track(x, y, clear=6.0, sid=None):
    P = track_pts(sid or CUR_SID[0])
    if len(P) == 0:
        return False
    return bool((np.hypot(P[:, 0] - x, P[:, 1] - y) < clear).any())


def nudge(x, y, clear=9.0, sid=None):
    """点(x,y)が線路から clear 未満なら、最寄り線路点から遠ざかる向きにずらして返す。"""
    sid = sid or CUR_SID[0]
    P = track_pts(sid)
    if len(P) == 0:
        return x, y
    sgn = 1.0 if y >= 0 else -1.0
    for _ in range(60):
        d = np.hypot(P[:, 0] - x, P[:, 1] - y)
        i = int(d.argmin())
        if d[i] >= clear:
            break
        dy = y - P[i, 1]
        y += (1.0 if dy >= 0 else -1.0) * 2.0 if abs(dy) > 0.5 else sgn * 2.0
    return x, y


def track_pts(sid):
    """ゾーンの全線路の中心線サンプル点(局所座標)。干渉回避用。"""
    if sid not in _TRKPTS:
        try:
            import interf_pts
            _TRKPTS[sid] = interf_pts.pts(sid)
        except Exception as e:
            print("track_pts fail", sid, e)
            _TRKPTS[sid] = np.zeros((0, 2))
    return _TRKPTS[sid]


def hits_track(sid, ox, oy, yaw, w, d, clear=5.5):
    P = track_pts(sid)
    if len(P) == 0:
        return False
    c, s_ = math.cos(yaw), math.sin(yaw)
    xs = np.linspace(-1.0, w + 1.0, 6)
    ys = np.linspace(-d - 1.0, d + 1.0, 5)
    gx, gy = np.meshgrid(xs, ys)
    wx = ox + c * gx.ravel() - s_ * gy.ravel()
    wy = oy + s_ * gx.ravel() + c * gy.ravel()
    dd = np.hypot(wx[:, None] - P[None, :, 0], wy[:, None] - P[None, :, 1])
    return bool((dd.min(1) < clear).any())


def town_along(pts, sid, st, rng, style, dens, xskip, sides=("L", "R"), off=2.6, xr=(-135, 135), rows=1):
    kinds = [k for k, wgt in STYLES[style] for _ in range(wgt)]
    t, n = trackkit.frames(pts)
    kcount = 0
    for side in sides:
        for row in range(rows):
            x = xr[0] + rng.uniform(0, 6)
            while x < xr[1]:
                kind = rng.choice(kinds)
                if kind == "sf":
                    w, d = rng.choice([5.0, 6.0, 7.0, 8.0, 9.5]), rng.uniform(7, 10)
                elif kind == "ware":
                    w, d = rng.uniform(12, 24), rng.uniform(10, 16)
                elif kind == "inn":
                    w, d = 13.5, 8.0
                elif kind == "danchi":
                    w, d = rng.uniform(26, 40), rng.uniform(9.5, 11.5)
                elif kind == "pre":
                    w, d = rng.choice([7.0, 8.0, 9.0]), rng.uniform(7.5, 9.5)
                else:
                    w, d = rng.uniform(8, 11), 7.0
                if kind == "farm":
                    w, d = w * 1.25 + 3.5, d * 1.3 + 3.5      # K8: 実測(PROBE_GROUP)で母屋は計画より x+3.2/y+3.5m 大きい(庇・縁側・納屋)。さらに 母屋は put_building で w×0.85〜1.25・d×0.85〜1.3 に変わる → 配置の占有幅は上限で見積もる
                i = int(np.clip((x + w / 2 - pts[0, 0]) / (pts[1, 0] - pts[0, 0]), 1, len(pts) - 2))   # K8: x は左端。建物中心 = x+w/2 で並べる(従来は中心=x で次との間隔が足りず隣棟が重なった)
                if any(a - w < x < b for a, b in xskip) or rng.random() > min(1.0, 0.35 + dens):
                    x += w + rng.uniform(2, 8) if dens < 0.5 else w + rng.uniform(1.3, 2.4)
                    continue
                u = float(np.clip((x + w / 2 - pts[0, 0]) / (pts[1, 0] - pts[0, 0]), 1, len(pts) - 2))   # K8: 添字を切り捨てず線形補間(点間隔が粗いと最大1間隔ずれて隣棟が重なった)
                i0 = int(u); fr = u - i0
                p = pts[i0] * (1 - fr) + pts[i0 + 1] * fr
                tt = t[i0] * (1 - fr) + t[i0 + 1] * fr; tt = tt / (np.linalg.norm(tt) + 1e-9)
                nn = np.array([-tt[1], tt[0]])
                ang = math.atan2(tt[1], tt[0])
                dd = off + 1.0 + row * (d + 6.5) + rng.uniform(0, 2.5 if dens < 0.6 else 0.8)
                if side == "L":
                    o = p + nn * dd - tt * (w / 2)
                    yaw = ang
                else:
                    o = p - nn * (dd + d * 0) + tt * (w / 2)
                    yaw = ang + math.pi
                if side == "R":
                    pass
                if any((o[0] - ex) ** 2 + (o[1] - ey) ** 2 < (er + max(w, d) * 0.6) ** 2 for ex, ey, er in struct_excl(sid)):
                    x += w + 1.0
                    continue
                if hits_track(sid, float(o[0]), float(o[1]), yaw, w, d):
                    x += w + 1.0
                    continue
                if _tree_hit_bld(sid, (float(o[0]), float(o[1])), yaw, w, d):
                    x += w + 1.0
                    continue
                if os.environ.get('KDEBUG'):
                    print('TOWN', side, kcount, kind, 'x=%.1f w=%.1f d=%.1f o=(%.1f,%.1f) yaw=%.0f' % (x, w, d, o[0], o[1], math.degrees(yaw)))
                put_building(kind, float(o[0]), float(o[1]), yaw, w, d, rng, st, kcount, sid, dens)
                kcount += 1
                x += w + (rng.uniform(1.0, 5.0) if dens < 0.6 else rng.uniform(1.3, 2.4))


# ----------------------------------------------------------------- per-station designs
ELEC_STN = {"M02", "M03", "M04", "M05", "SH04", "SH05", "SH06", "SH07", "SH08"}
D = lambda **k: k
DESIGN = {
 "M02": D(yaw=8, curve=("S", 12), plan="I", w=15, d=8, nfl=2, roof="flat", wall="pl_grey", plat="island", ntr=3, canopy="steel", cross="fb_steel", terrain=["pond"], road="straight", town="urban", dens=0.85, lm=[("water", -40, 26)], bx=-4),
 "M03": D(yaw=-6, curve=("arc", 900), plan="OVER", w=18, d=9, nfl=2, roof="flat", wall="concrete", plat="dual", ntr=4, canopy="none", cross="over", terrain=[], road="plaza", town="urban", dens=0.9, lm=[("clock", 10, 30)], bx=-8),
 "M04": D(yaw=-12, curve=("arc", 900), plan="AA", w=11, d=7.5, nfl=1, roof="hip", wall="pl_cream", plat="dual", ntr=3, canopy="wood", cross="fb_wood", terrain=["paddies"], road="curve", town="suburb", dens=0.55, lm=[("water", 30, 30)], bx=-6),
 "M05": D(yaw=20, curve=("arc", -700), plan="L", w=12, d=7, nfl=2, roof="hip", wall="brick", plat="dual", ntr=4, canopy="curve", cross="fb_steel", terrain=["pond", "orchard"], road="bend", town="suburb", dens=0.5, lm=[("sigtower", 16, 10)], bx=-8),
 "M07": D(yaw=-25, curve=("arc", 700), plan="A", w=8, d=6, nfl=1, roof="gable", wall="wall", plat="island", ntr=3, canopy="none", cross="fb_wood", terrain=["orchard"], road="bend", town="rural", dens=0.3, lm=[('farm_silo', 36, 30), ('deck', -34, 18)], bx=-5),
 "M08": D(yaw=35, curve=("S", 14), plan="T", w=16, d=8, nfl=2, roof="gable", wall="pl_ochre", plat="island", ntr=4, canopy="saw", cross="fb_wood", terrain=["hill_n"], road="straight", town="rural", dens=0.5, lm=[("water", 22, -18), ("chimney", -34, 34)], bx=-9),
 "M09": D(yaw=-40, curve=("arc", 500), plan="L", w=8, d=5, nfl=1, roof="hip", wall="wood", plat="side", ntr=2, canopy="shed", cross="level", terrain=["forest"], road="diag", town="forest", dens=0.14, lm=[("deck", 24, 13), ("water", -24, 16)], bx=-4),
 "M10": D(yaw=60, curve=("S", 10), plan="U", w=15, d=8, nfl=2, roof="hip", wall="wall", plat="island", ntr=4, canopy="curve", cross="underpass", terrain=["hill_s", "pond"], road="curve", town="onsen", dens=0.6, lm=[("onsen", 28, 44), ("footbath", -24, 22)], bx=-9),
 "M11": D(yaw=50, curve=("arc", 450), plan="A", w=9, d=6, nfl=1, roof="hip", wall="stone", plat="side", ntr=3, canopy="shed", cross="level", terrain=["hill_n"], road="diag", town="alpine", dens=0.22, lm=[("water", 22, -14), ("snowhut", -30, 14)], bx=-6),
 "M12": D(yaw=-70, curve=("arc", -500), plan="I", w=10, d=6, nfl=1, roof="shed", wall="concrete", plat="island", ntr=3, canopy="snow", cross="fb_steel", terrain=["snow", "hill_n", "hill_s"], road="bend", town="alpine", dens=0.15, lm=[("deck", 26, 14), ("snowhut", -26, 8)], bx=-5),
 "M13": D(yaw=80, curve=("arc", 600), plan="I", w=11, d=6, nfl=1, roof="shed", wall="wood", plat="side", ntr=2, canopy="snowfull", cross="level", terrain=["snow", "hill_n"], road="diag", town="alpine", dens=0.25, lm=[("snowhut", 30, 10)], bx=-5),
 "L01": D(yaw=95, curve=("arc", -400), plan="I", w=4, d=3, nfl=1, roof="shed", wall="tin_blue", plat="side_short", ntr=1, canopy="none", cross="steps", terrain=["snow", "hill_n"], road="straight", town="alpine", dens=0.08, lm=[('skilift', 20, 26)], bx=-2),
 "M14": D(yaw=-110, curve=("S", 8), plan="L", w=17, d=8, nfl=2, roof="flat", wall="brick", plat="island", ntr=5, canopy="steel", cross="fb_steel", terrain=["sea"], road="straight", town="port", dens=0.55, lm=[("crane", 34, 36), ("chimney", -32, 40)], bx=-8),
 "M15": D(yaw=130, curve=("arc", 400), plan="I", w=5, d=3.5, nfl=1, roof="gable", wall="pl_blue", plat="side_short", ntr=1, canopy="none", cross="steps", terrain=["sea"], road="bend", town="rural", dens=0.1, lm=[("deck", 20, 12)], bx=-3),
 "M16": D(yaw=-150, curve=("arc", -800), plan="TW", w=15, d=9, nfl=2, roof="hip", wall="pl_cream", plat="island", ntr=4, canopy="shed", cross="overshops", terrain=["sea"], road="plaza", town="port", dens=0.65, lm=[("clock", 8, 30), ("crane", 44, 36)], bx=-7),
 "M17": D(yaw=170, curve=("S", 9), plan="A", w=8, d=5.5, nfl=1, roof="gable", wall="pl_green", plat="side", ntr=2, canopy="shed", cross="level", terrain=["pond", "forest"], road="curve", town="rural", dens=0.25, lm=[("sigtower", 16, 8)], bx=-5),
 "M18": D(yaw=-175, curve=("arc", 350), plan="I", w=6, d=4, nfl=1, roof="shed", wall="brick", plat="side", ntr=1, canopy="none", cross="steps", terrain=["sea"], road="bend", town="rural", dens=0.12, lm=[("lighthouse", 30, 24)], bx=-3),
 "Y02": D(yaw=15, curve=("arc", 300), plan="I", w=5, d=4, nfl=1, roof="gable", wall="wood", plat="side_short", ntr=1, canopy="none", cross="steps", terrain=["hill_n", "pond"], road="diag", town="forest", dens=0.1, lm=[("deck", 22, 12)], bx=-3),
 "Y03": D(yaw=75, curve=("arc", -300), plan="I", w=5, d=3.5, nfl=1, roof="shed", wall="pl_grey", plat="side_short", ntr=1, canopy="none", cross="stairs", terrain=["hill_s"], road="bend", town="forest", dens=0.1, lm=[("bridge", 0, 0)], bx=-3),
 "Y04": D(yaw=-60, curve=("arc", 350), plan="L", w=7, d=4.5, nfl=1, roof="hip", wall="wall", plat="side_short", ntr=1, canopy="none", cross="steps", terrain=["hill_n", "pond"], road="curve", town="onsen", dens=0.2, lm=[("onsen", 24, 22), ("footbath", -14, 14)], bx=-4),
 "S02": D(yaw=-20, curve=("arc", 450), plan="I", w=6, d=4.5, nfl=1, roof="gable", wall="pl_ochre", plat="side_short", ntr=1, canopy="none", cross="level", terrain=["orchard"], road="straight", town="rural", dens=0.2, lm=[('torii', 26, 22)], bx=-3),
 "S03": D(yaw=110, curve=("S", 8), plan="I", w=7, d=5, nfl=1, roof="gable", wall="wood", plat="side_short", ntr=1, canopy="shed", cross="level", terrain=["forest"], road="diag", town="forest", dens=0.14, lm=[('logstack', 24, -22)], bx=-4),
 "S04": D(yaw=180, curve=("arc", -350), plan="L", w=9, d=5.5, nfl=1, roof="gable", wall="pl_green", plat="side", ntr=2, canopy="wood", cross="level", terrain=["hill_n", "forest"], road="bend", town="alpine", dens=0.28, lm=[('firetower', 30, 28), ('water', -24, 18)], bx=-5),
 "SH02": D(yaw=0, curve=("arc", -1100), plan="OVER", w=17, d=9, nfl=2, roof="flat", wall="pl_cream", plat="dual", ntr=3, canopy="none", cross="over", terrain=["paddies"], road="plaza", town="newtown", dens=0.85, lm=[("water", 44, -28)], bx=-8),
 "SH03": D(yaw=0, curve=("arc", 900), plan="I", w=9, d=6, nfl=1, roof="flat", wall="pl_grey", plat="island", ntr=3, canopy="curve", cross="stairs", terrain=["pond"], road="curve", town="newtown", dens=0.6, lm=[("deck", 30, 26)], bx=-5),
 "SH04": D(yaw=0, curve=("straight", 0), plan="TW", w=22, d=10, nfl=3, roof="flat", wall="concrete", plat="dual", ntr=4, canopy="steel", cross="overshops", terrain=[], road="plaza", town="urban", dens=0.92, lm=[("clock", 14, 36), ("apt", -34, 58)], bx=-10),
 "SH05": D(yaw=0, curve=("S", 10), plan="U", w=14, d=8, nfl=2, roof="shed", wall="pl_green", plat="island", ntr=3, canopy="curve", cross="fb_steel", terrain=["hill_n"], road="straight", town="campus", dens=0.5, lm=[("gate", -30, 24), ("field", -78, 34)], bx=-7),
 "SH06": D(yaw=0, curve=("arc", 1500), plan="AA", w=12, d=7, nfl=1, roof="saw", wall="tin", plat="island", ntr=5, canopy="shed", cross="fb_steel", terrain=[], road="straight", town="freight", dens=0.65, lm=[("crane", 36, 30), ("chimney", -30, 36)], bx=-6),
 "SH07": D(yaw=0, curve=("arc", -800), plan="I", w=7, d=5, nfl=1, roof="flat", wall="pl_grey", plat="dual", ntr=3, canopy="none", cross="fb_steel", terrain=["paddies"], road="diag", town="airport", dens=0.35, lm=[("windsock", 30, 28), ("silo", 40, 52)], bx=-4),
 "SH08": D(yaw=0, curve=("straight", 0), plan="L", w=24, d=11, nfl=2, roof="flat", wall="pl_cream", plat="island2", ntr=4, canopy="steel", cross="fb_steel", terrain=["paddies"], road="plaza", town="airport", dens=0.4, lm=[("atc", 52, 44), ("radar", -48, 40), ("windsock", 20, -26)], bx=-10, endbuf=True),
 "F01": D(yaw=0, curve=("straight", 0), plan="AA", w=30, d=12, nfl=1, roof="saw", wall="tin", plat="none", ntr=8, canopy="none", cross="level", terrain=[], road="straight", town="freight", dens=0.7, lm=[("chimney", -40, 40), ("crane", 40, 36)], bx=-15),
}


def stairs(g, x, y_hi, y_lo, z_hi, width=1.8, key="concrete"):
    n = max(4, int(abs(y_hi - y_lo) / 0.28))
    for k in range(n):
        ya = y_hi + (y_lo - y_hi) * k / n
        yb = y_hi + (y_lo - y_hi) * (k + 1) / n
        g.a(key, bevel=0.01).box(x - width / 2, x + width / 2, min(ya, yb), max(ya, yb), Z_PLAT, z_hi - (z_hi - Z_PLAT) * (k + 1) / n)


def furniture_c(P, bx, r0, r1, yb, st, tx, frame):
    """ホーム小物(街灯・駅名標)を曲線に追従して置く(kit.furniture の曲線版)。"""
    for x in np.arange(r0 + 4, r1 - 3, 11):
        with frame(bx + float(x)):
            g = G(f"kit_furn_{st['id']}", "Props")
            props.lamp_post(g, 0.0, yb - 0.4, side=-1)
            g.build()
    for xc in (r0 + (r1 - r0) * 0.25, r0 + (r1 - r0) * 0.75):
        with frame(bx + float(xc)):
            g = G(f"kit_furn_{st['id']}", "Props")
            g.a("pole_new").box(-1.3, -1.2, yb - 1.0, yb - 0.9, Z_PLAT, Z_PLAT + 2.2)
            g.a("pole_new").box(1.2, 1.3, yb - 1.0, yb - 0.9, Z_PLAT, Z_PLAT + 2.2)
            face_plane(f"kit_nm_s_{st['id']}_{xc:.0f}", tx[0], 'S', 0.0, yb - 1.0 - 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
            face_plane(f"kit_nm_n_{st['id']}_{xc:.0f}", tx[0], 'N', 0.0, yb - 1.0 + 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
            g.build()


def build_design(sid):
    mats2()
    st = ST[sid]
    d = DESIGN[sid]
    rng = random.Random(sum(map(ord, sid)) * 31)
    names = {s["id"]: s["name"] for s in NET["stations"]}
    o = NET["order"].get(st["lines"][0], [])
    i = o.index(sid) if sid in o else -1
    prev = names[o[i - 1]] if i > 0 else None
    nxt = names[o[i + 1]] if 0 <= i < len(o) - 1 else None
    tx = boards(st, prev, nxt)
    import make_posters
    kc, kv = d["curve"]
    P = centerline(kc, R=kv if kc == "arc" else 0, amp=kv if kc == "S" else 0) if sid not in CURVE_OVERRIDE else centerline("arc", R=CURVE_OVERRIDE[sid], flat=False)
    kit.ground(600, 600)
    if "snow" in d["terrain"]:                    # 雪景色: 地面に薄い積雪(線路・ホームはその上に出る)
        _sn = lib.Acc("kit_snowcover", M["snow"], "Ground")
        _sn.box(-400, 400, -400, 400, -0.012, 0.02)
        _sn.build()
    ntr, plat, dens = d["ntr"], d["plat"], d["dens"]
    w, dep, bx = d["w"], d["d"], d["bx"]
    # ---- tracks
    offsets = track_offsets(plat, ntr)
    for k, off in enumerate(offsets):
        Pk = offs(P, off)
        if k >= 2:
            sl = Pk[LH - 90 + rng.randint(-30, 20): LH + 110 + rng.randint(-20, 30)]
            trackkit.build_track(f"k2_trk{k}", sl, wooden=True, ballast=True, fittings=True, cam=(None if os.environ.get("PEBBLES", "1") == "0" else (float(bx + w / 2.0), float(Pk[min(LH, len(Pk) - 1)][1]))), pebble_radius=70.0)
            e = sl[-1]
            trackkit.buffer_stop(float(e[0]), float(e[1]), math.degrees(math.atan2(*(sl[-1] - sl[-3])[::-1])))
        else:
            rb, rf = REACH.get(sid, (LH, LH))
            trackkit.build_track(f"k2_trk{k}", Pk[LH - rb: LH + rf + 1], wooden=True, ballast=True, fittings=True, cam=(None if os.environ.get("PEBBLES", "1") == "0" else (float(bx + w / 2.0), float(Pk[min(LH, len(Pk) - 1)][1]))), pebble_radius=70.0)
            if d.get("endbuf"):       # 終端駅だが頭端式ではない: ホームの先まで通過形で線路が延び、先端に車止め
                sl2 = Pk[LH - rb: LH + rf + 1]
                trackkit.buffer_stop(float(sl2[-1][0]), float(sl2[-1][1]), math.degrees(math.atan2(*(sl2[-1] - sl2[-3])[::-1])))
    # ---- 架線(電化駅のみ)
    if sid in ELEC_STN:
        import kit5
        ac = sid.startswith("SH")
        rb, rf = REACH.get(sid, (LH, LH))
        for k, off in enumerate(offsets):
            Pk = offs(P, off)[LH - rb: LH + rf + 1]
            Q, _ = trackkit.resample(np.asarray(Pk, float), 1.0)
            try:
                kit5.catenary(Q, 12.0, len(Q) - 14.0, name=f"k2_cat{k}", side=(1 if k == 0 else (-1 if k == len(offsets) - 1 else -0.72)), ac=ac)
            except Exception as e_:
                print("station catenary fail", sid, k, e_)
    # ---- platforms
    L_ = max(w + 34, 46) if plat not in ("side_short",) else w + 14
    xa, xb = bx - (14 if plat != "side_short" else 3), bx - (14 if plat != "side_short" else 3) + L_
    if plat in ("side", "side_short", "dual", "island", "island2"):
        platform_strip(P, 1.7, 4.4, xa, xb, "k2_platA")
    if plat == "dual":
        platform_strip(P, -4.6 - 1.7, -4.6 - 4.4, xa, xb, "k2_platB")
    if plat in ("island", "island2"):
        platform_strip(P, -1.7, -6.7, xa + 6, xb - 6, "k2_isl")
    if plat == "island2":
        platform_strip(P, -14.7, -19.7, xa + 6, xb - 6, "k2_isl2")
    # ---- building frame
    pbx, yaw_b, nb = frame_at(P, bx)
    org = pbx + nb * 4.4
    with SubZone((float(org[0]), float(org[1]), 0), yaw_b):
        g = G(f"k2_bld_{sid}", "Station")
        plan = d["plan"]
        if plan == "OVER":
            vols = plan_volumes("I", w, dep, 1, "flat", d["wall"], rng)
            vols[0]["door2"] = "N"                                    # 橋上駅舎は駅前(N側)にも出入口を設ける(旧: 駅前に扉が無かった)
            for v in vols:
                volume(g, v, rng, st, interior=True)
            xc = w / 2
            zf_ = Z_PLAT + 0.30                                       # 駅前の庇と柱
            g.a("concrete", bevel=0.02).box(xc - 3.2, xc + 3.2, dep, dep + 2.6, zf_ + 2.75, zf_ + 2.95)
            for xx in (xc - 3.0, xc + 3.0):
                g.a("concrete", bevel=0.01).box(xx - 0.12, xx + 0.12, dep + 2.3, dep + 2.5, zf_, zf_ + 2.75)
            g.a("stone").box(xc - 3.2, xc + 3.2, dep, dep + 2.8, zf_ - 0.25, zf_ - 0.02)               # 車寄せの床
            gb = G("k2_over", "Station")
            _of = track_offsets(d["plat"], d["ntr"])
            _ye = -4.4 + min(_of) - 3.2
            _pb = (-4.6 - (1.7 + 4.4) / 2) - 4.4         # B面ホーム(線1の南 1.7〜4.4)の中央。建物枠は世界y+4.4 なので -4.4(K8: 旧式は線1の車体内=-5.35 に橋脚が立っていた)
            volume(gb, dict(x0=xc - 4.0, x1=xc + 4.0, y0=_ye - 0.4, y1=-0.4, nfl=1, roof="flat", wall="pl_grey", ground=False, zf=5.7, skip=(), door="S"), rng, st)   # 橋上通路: 長辺(E/W)にも窓を開ける(旧: skip=E,W で無窓の壁だった)
            for yy in (-1.4, _pb, _ye + 0.6):                          # 橋脚: A面ホーム上(-1.4)・B面ホーム中央(_pb)・線路の外側
                for xx in (xc - 3.6, xc + 3.6):
                    gb.a("concrete", bevel=0.02).box(xx - 0.3, xx + 0.3, yy - 0.3, yy + 0.3, 0.0, 5.6)
            stairs(gb, xc - 2.5, -2.5, -0.4, 5.6, key="concrete")
            gb.build()
            ymid = -9.0
        else:
            vols = plan_volumes(plan, w, dep, d["nfl"], d["roof"], d["wall"], rng)
            for k_, v in enumerate(vols):
                volume(g, v, rng, st, interior=(k_ == 0))
        g.build()
        # facade sign + clock-ish details
        zhm = Z_PLAT + 0.3 + 2.9 + (d["nfl"] - 1) * 3.0
        face_plane(f"k2_fac_{sid}", tx[1], 'S', w * 0.5, -0.17, zhm - 0.7 if d["roof"] in ("gable", "hip") else zhm - 0.9, min(2.6, w * 0.45), off=0.0)
    # ---- 上屋・防雪・ホーム小物・跨線橋: 軌道の曲線に追従させるため、小区間ごとに自分の座標系(frame_at)に置く
    def _frame(xp):
        p_, yw_, nb_ = frame_at(P, xp)
        o_ = p_ + nb_ * 4.4
        return SubZone((float(o_[0]), float(o_[1]), 0), yw_)

    def _segs(a_, b_, step):
        n_ = max(1, int(math.ceil((b_ - a_) / step)))
        L_ = (b_ - a_) / n_
        return [(a_ + (i_ + 0.5) * L_, L_) for i_ in range(n_)]

    cn = d["canopy"]
    if cn in ("snowfull", "snow"):
        for xc_, L_ in _segs(xa - bx, xb - bx, 6.0):
            with _frame(bx + xc_):
                gs = G("k2_snow", "Station")
                snowshed(gs, -L_ / 2, L_ / 2 - 0.2, -2.6, -0.2, h=3.7)
                gs.build()
    elif cn != "none":
        ca_, cb_ = max(xa - bx, -2), min(xb - bx - 4, w + 14)
        for xc_, L_ in _segs(ca_, cb_, 8.0):
            with _frame(bx + xc_):
                canopy(cn, -L_ / 2 + 0.5, L_ / 2 - 0.5, depth=2.4)
    if plat != "none":
        for (yb_f, r0, r1) in [(0.0, xa - bx + 2, xb - bx - 2)] + ([(-7.6, xa - bx + 8, xb - bx - 8)] if plat in ("island", "island2") else []) + ([(-20.6, xa - bx + 8, xb - bx - 8)] if plat == "island2" else []) + ([(-12.4, xa - bx + 8, xb - bx - 8)] if plat == "dual" else []):
            furniture_c(P, bx, r0, r1, yb_f, st, tx, _frame)
        # ---- 人物(H1): ホーム上の待ち客・駅員を駅ごとに配置(人数は町の密度に比例)
        import life as _life
        _rp = random.Random(zlib.crc32(sid.encode()) % 9999)
        _kinds = ["man", "man2", "woman", "student", "farmer", "worker"] if dens < 0.5 else ["man", "man2", "woman", "student", "man2", "woman"]
        _ys = [-1.35] + ([-8.6] if plat in ("island", "island2") else []) + ([-12.05] if plat == "dual" else [])
        _x0, _x1 = (xa - bx) + 6, (xb - bx) - 6
        for _yc in _ys:
            _n = 2 + int(dens * 5) + (1 if _rp.random() < 0.5 else 0)
            for _i in range(_n):
                _xp = _rp.uniform(_x0, _x1)
                with _frame(bx + _xp):
                    _f = _life.Fig(f"k2ppl_{sid}_{_yc}_{_i}")
                    _life.person(_f, 0.0, _yc + _rp.uniform(-0.35, 0.35), _rp.uniform(0, 6.28), _rp.choice(_kinds), z=Z_PLAT,
                                 scale=_rp.choice([1.0, 1.0, 0.92, 0.82]), pose=_rp.choice(["stand", "stand", "walk"]))
                    _f.build()
            with _frame(bx + (_x0 + _x1) / 2 - 8):
                _f = _life.Fig(f"k2mst_{sid}_{_yc}")
                _life.person(_f, 0.0, _yc, 1.57, "master", z=Z_PLAT)
                _f.build()
        for k_ in range(3):
            xk_ = (xa - bx) + ((xb - bx) - (xa - bx)) * (0.35 + 0.18 * k_)
            with _frame(bx + xk_):
                KT.decorate_platform(sid, 0.0, 0.0, 0.0, rng, ks=(k_,))
    cr = d["cross"]
    if cr in ("fb_steel", "fb_wood", "overshops", "underpass") and plat in ("dual", "island", "island2"):
        with _frame(bx + w + 7):
            gx = G("k2_cross", "Station")
            yb_ = -12.0 if plat == "dual" else (-21.6 if plat == "island2" else -8.6)
            if cr != "underpass":
                footbridge(gx, 0.0, -0.9, yb_, covered=(cr != "fb_steel"), kind="wood" if cr == "fb_wood" else "steel", z=5.2,
                           piers=([-0.9, -8.6, -21.6] if plat == "island2" else None), mid=([-8.6] if plat == "island2" else None))
            else:
                for yy in (-1.2, yb_):
                    gx.a("concrete", bevel=0.03).box(-1.5, 1.5, yy - 1.2, yy + 1.2, Z_PLAT, Z_PLAT + 2.6)
                    gx.a("roof").extrude_x([(yy - 1.5, Z_PLAT + 2.5), (yy, Z_PLAT + 3.4), (yy + 1.5, Z_PLAT + 2.5)], -1.9, 1.9)
            gx.build()
    # ---- poles along the track (south side)
    gp = G("k2_poles", "Props")
    for x in np.arange(-150, 150, 42):
        p_, a_, n_ = frame_at(P, x + rng.uniform(-3, 3))
        q = p_ - n_ * (-min(offsets) + 3.2)
        props.pole(gp, float(q[0]), float(q[1]), h=8.0, arms=((7.4, 0.9, 3),), axis='y' if abs(math.sin(a_)) < 0.5 else 'x', old=True)
    gp.build()
    # ---- terrain
    ryb = 14.5 + (6 if dens > 0.6 else 0)
    for tkind in d["terrain"]:
        if tkind == "hill_n":
            hcx, hh = rng.uniform(-40, 40), rng.uniform(18, 46)
            _, hf = hill(hcx, ryb + 80, 110, 55, hh, "k2_hill_n", seed=rng.randint(0, 99))
            scatter_trees(rng, hcx, ryb + 76, 100, 48, 70, zfun=hf)
        elif tkind == "hill_s":
            hcx2 = rng.uniform(-40, 40)
            _, hf2 = hill(hcx2, -80, 110, 50, rng.uniform(14, 36), "k2_hill_s", seed=rng.randint(0, 99))
            scatter_trees(rng, hcx2, -76, 100, 44, 56, zfun=hf2)
        elif tkind == "pond":
            px_, py_, prx, pry = rng.uniform(-60, 60), rng.choice([-32, ryb + 26]), rng.uniform(9, 16), rng.uniform(6, 10)
            px_, py_ = nudge(px_, py_, pry + 9.0)
            pond(px_, py_, prx, pry, "k2_pond")
        elif tkind == "paddies":
            paddies(-130, 130, -70, -26, "k2_pad_s", rng)
            paddies(-130, 130, ryb + 26, ryb + 70, "k2_pad_n", rng)
        elif tkind == "orchard":
            for gx_ in np.arange(-110, 110, 9):
                for gy_ in (-36, -45, -54, ryb + 30, ryb + 39):
                    if near_track(float(gx_), float(gy_), 7.0):
                        continue
                    _px, _py = float(gx_ + rng.uniform(-1, 1)), float(gy_ + rng.uniform(-1, 1))
                    if _bld_hit(sid, _px, _py, 2.8):
                        continue                                      # K8: 母屋・店に食い込む柿は植えない
                    TREES.setdefault(sid, []).append((_px, _py, 2.8))  # 以降に置く建物が柿を避けるよう登録
                    veg.persimmon(_px, _py, seed=rng.randint(0, 9999))
        elif tkind == "forest":
            scatter_trees(rng, 0, -48, 150, 24, 60, kinds=("sugi",))
            scatter_trees(rng, 0, ryb + 40, 150, 28, 60, kinds=("sugi", "zelkova"))
        elif tkind == "sea":
            _xs = np.arange(-600.0, 601.0, 12.0)
            _ph = (zlib.crc32(sid.encode()) % 628) / 100.0
            _sh = -52.0 + 5.5 * np.sin(_xs / 58.0 + _ph) + 3.0 * np.sin(_xs / 21.0 + 2 * _ph)       # 汀線(駅ごとに位相が違う曲線)
            wsea = lib.Acc("k2_sea", M["water"], "Ground")
            wsea.extrude_z([(-600.0, -600.0), (600.0, -600.0)] + [(float(x_), float(y_)) for x_, y_ in zip(_xs[::-1], _sh[::-1])], -0.4, 0.03)
            wsea.build()
            sand = lib.Acc("k2_sand", M.get("sand", M["plat_top"]), "Ground")
            _wd = 11.0 + 4.0 * np.sin(_xs / 37.0 + _ph)                                              # 砂浜の幅も場所で変える
            sand.extrude_z([(float(x_), float(y_)) for x_, y_ in zip(_xs, _sh)] + [(float(x_), float(y_ + w_)) for x_, y_, w_ in zip(_xs[::-1], _sh[::-1], _wd[::-1])], -0.3, 0.015)
            sand.build()
    # ---- roads + forecourt + town
    rp = road_pts(d["road"], ryb)
    road_geom(rp, 4.6)
    core.apron("k2_fc", bx + w / 2 * 1.0, (4.4 + dep + ryb) / 2 + 1.0, 9 if d["road"] != "plaza" else 22, (ryb - 4.4 - dep) / 2 + 2.0, M["road"])
    style = d["town"]
    skip = [(bx - 8, bx + w + 10)]
    dd2 = min(1.0, dens * 1.5 + 0.22)
    town_along(rp, sid, st, rng, style, dd2, skip, sides=("L", "R") if ryb > 18 else ("L",), rows=3 if dens > 0.8 else (2 if dens > 0.2 else 1))
    KT.billboard(sid, bx + w + 30, ryb + 3.2, KT.img(sid, "bb0"), 'S', name=f"bb_{sid}0")
    KT.billboard(sid, bx - 45, ryb - 3.2, KT.img(sid, "bb1"), 'N', name=f"bb_{sid}1")
    for (k_, x, y) in d.get("lm", []):
        try:
            if k_ != "bridge":
                x, y = nudge(x, y, 10.0)
                for _rad in (0, 5, 9, 13, 18, 24):                      # K8: 象徴物が既存の建物・樹木に重ならない最寄りの空きへずらす
                    _hit = True
                    for _a in range(8):
                        _cx, _cy = x + _rad * math.cos(_a * math.pi / 4), y + _rad * math.sin(_a * math.pi / 4)
                        if not _bld_hit(sid, _cx, _cy, 9.0 / 0.7) and not any((_cx - tx) ** 2 + (_cy - ty) ** 2 < (9.0 + tr) ** 2 * 0.5 for tx, ty, tr in TREES.get(sid, [])) and not near_track(_cx, _cy, 7.0):
                            x, y, _hit = _cx, _cy, False
                            break
                    if not _hit:
                        break
            sig.KINDS[k_](x, y, name=f"lm_{sid}_{k_}_{int(x)}") if k_ != "bridge" else sig.KINDS[k_](x, y, name=f"lm_{sid}_br")
        except Exception as e:
            print("lm fail", k_, e)


def _stock(sid):
    try:
        import zone_stock
        zone_stock.place_stock(sid)
    except Exception as e:
        import traceback; traceback.print_exc()
        print("stock failed", sid, e)


def build_zone(sid, origin=(0, 0, 0), yaw=None):
    import kit3
    CUR_SID[0] = sid
    if sid in kit3.BUILD:
        with Zone(sid, origin, 0.0 if yaw is None else yaw):
            kit3.BUILD[sid]()
            _stock(sid)
        return
    if sid in DESIGN:
        with Zone(sid, origin, math.radians(DESIGN[sid]["yaw"]) if yaw is None else yaw):
            build_design(sid)
            _stock(sid)
    else:
        with Zone(sid, origin, 0.0):
            kit.build_generic(sid)
            _stock(sid)
