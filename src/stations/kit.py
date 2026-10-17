import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Parametric station-zone kit. Each station is built in LOCAL coordinates (main line along +x, track y=0, platform to +y,
town on both sides) and all new objects are parented to an Empty placed in the world."""
import json, math, random, os
from common import *
import lib, props, rooms, houses, core, trackkit
from props import G, face_plane
import make_textures2 as mt

NET = json.load(open(f"{_R}/net/network.json"))
ST = {s["id"]: s for s in NET["stations"]}
TEX = f"{_R}/tex"


class Zone:
    def __init__(self, sid, origin=(0, 0, 0), yaw=0.0):
        self.sid, self.origin, self.yaw = sid, origin, yaw

    def __enter__(self):
        self.before = set(bpy.data.objects.keys())
        return self

    def __exit__(self, *a):
        e = bpy.data.objects.new("zone_" + self.sid, None)
        e.location, e.rotation_euler = self.origin, (0, 0, self.yaw)
        lib.link(e, "Zones")
        for n in set(bpy.data.objects.keys()) - self.before:
            o = bpy.data.objects[n]
            if o.parent is None and o is not e:
                o.parent = e


# ------------------------------------------------------------------ per-station signboards (original artwork)
def boards(st, prev, nxt):
    sid = st["id"]
    f = f"{TEX}/kit_{sid}_ekimei.png"
    if not os.path.exists(f):
        W, H = 2400, 800
        im = mt.Image.new("RGB", (W, H), (238, 237, 230))
        d = mt.ImageDraw.Draw(im)
        d.rectangle([0, 0, W - 1, H - 1], outline=(18, 18, 18), width=22)
        d.rectangle([40, 40, W - 41, H - 41], outline=(18, 18, 18), width=5)
        n = st["name"]
        mt.text(d, (W // 2, 140), st.get("kana", n), mt.SANS("Bold", 112), (18, 18, 18))
        mt.text(d, (W // 2, 400), " ".join(n), mt.SERIF("Black", int(min(270, 1500 / max(1, len(n))))), (14, 14, 14))
        d.line([90, 600, W - 90, 600], fill=(18, 18, 18), width=6)
        if prev:
            mt.text(d, (330, 690), "◀ " + prev, mt.SANS("Bold", 78), (18, 18, 18))
        if nxt:
            mt.text(d, (W - 330, 690), nxt + " ▶", mt.SANS("Bold", 78), (18, 18, 18))
        mt.text(d, (W // 2, 690), sid, mt.SANS("Medium", 54), (40, 40, 40))
        mt.age(im, rust=0.9, yellow=0.12, seed=hash(sid) % 50).save(f)
    g = f"{TEX}/kit_{sid}_facade.png"
    if not os.path.exists(g):
        W, H = 1800, 480
        im = mt.Image.new("RGB", (W, H), (30, 24, 20))
        d = mt.ImageDraw.Draw(im)
        mt.text(d, (W // 2, H // 2 + 6), st["name"] + "駅", mt.SERIF("Black", int(min(300, 1500 / (len(st["name"]) + 1)))), (232, 226, 210))
        im.save(g)
    return f"kit_{sid}_ekimei.png", f"kit_{sid}_facade.png"


# ------------------------------------------------------------------ pieces
NOGROUND = [False]


def ground(L=600, W=600):
    if NOGROUND[0]:
        return
    a = lib.Acc("kit_ground", M["grass_ground"], "Ground")
    a.box(-L, L, -W, W, -0.30, -0.01)
    a.build()


def ballast_bed(x0, x1, ys):
    pass


REACH = {}
REACH_CUR = [None]


def tracks(x0, x1, ys, wooden=True):
    if REACH_CUR[0]:
        x0, x1 = max(x0, -REACH_CUR[0][0]), min(x1, REACH_CUR[0][1])
    for i, y in enumerate(ys):
        P = np.array([[x0, y], [x1, y]], float)
        trackkit.build_track(f"kit_trk{i}", P, wooden=wooden, ballast=True, fittings=True, cam=None)


PLAT_REC = []      # H1: kit6 等のホーム(x0,x1,y0,y1,name)の記録。人物配置に使う


def platform(x0, x1, y0, y1, name="kit_plat"):
    PLAT_REC.append((x0, x1, y0, y1, name))
    g = G(name, "Station")
    g.a("concrete", bevel=0.01).box(x0, x1, y0, y1, -0.2, Z_PLAT - 0.04)
    g.a("plat_top", bevel=0.0).box(x0 + 0.04, x1 - 0.04, y0 + 0.5, y1 - 0.04, Z_PLAT - 0.04, Z_PLAT)
    g.a("concrete", bevel=0.01).box(x0, x1, y0, y0 + 0.5, Z_PLAT - 0.04, Z_PLAT + 0.02)
    g.a("white").box(x0, x1, y0 + 0.55, y0 + 0.62, Z_PLAT, Z_PLAT + 0.006) if "white" in M else None
    g.build()


def station_building(x0, x1, y0, y1, st, tx, interior=True, rng=None, wall="wall", roof="gabled"):
    """Raw-wood station building; platform side = y0 (south), forecourt side = y1. Hollow with interior."""
    g = G(f"kit_bld_{st['id']}", "Station")
    zb = Z_PLAT
    zf = zb + 0.30
    zh = zf + 2.9
    g.a("stone", bevel=0.015).box(x0 - 0.08, x1 + 0.08, y0 - 0.02, y1 + 0.08, -0.25, zf - 0.02)
    L = x1 - x0
    ops = {
        "S": [(x0 + 0.9, x0 + 2.1, zf + 1.0, zf + 2.0, 'glass'), (x0 + L * 0.42, x0 + L * 0.42 + 2.0, zf, zf + 2.05, 'open'),
              (x0 + L * 0.42 + 2.8, x0 + L * 0.42 + 4.0, zf + 1.0, zf + 2.0, 'glass'), (x1 - 2.6, x1 - 1.4, zf + 1.0, zf + 2.0, 'glass')],
        "N": [(x0 + 1.0, x0 + 2.2, zf + 1.0, zf + 2.0, 'glass'), (x0 + L * 0.45, x0 + L * 0.45 + 1.9, zf, zf + 2.05, 'door'),
              (x1 - 2.6, x1 - 1.4, zf + 1.0, zf + 2.0, 'glass')],
        "E": [((y0 + y1) / 2 - 0.6, (y0 + y1) / 2 + 0.6, zf + 1.0, zf + 2.0, 'glass')],
        "W": [],
    }
    rooms.shell(g, x0, x1, y0, y1, zf - 0.02, zh, t=0.12, ops=ops, wall=wall)
    # raw timber frame accents
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        g.a("wood_dark", bevel=0.004).box(cx - 0.09, cx + 0.09, cy - 0.09, cy + 0.09, zf - 0.02, zh + 0.2)
    if roof == "gabled":
        props.gable_roof(g.a("roof"), g.a("wall"), x0, x1, y0, y1, zh, 1.9, ov=0.85, gov=0.55)
    elif roof == "hip":
        hip_roof(g.a("roof"), x0, x1, y0, y1, zh, 2.1, ov=0.9)
    else:   # flat slab with parapet
        g.a("concrete", bevel=0.01).box(x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, zh, zh + 0.25)
        g.a("concrete", bevel=0.01).box(x0 - 0.2, x1 + 0.2, y0 - 0.2, y0 - 0.1, zh + 0.25, zh + 0.7)
    if interior:
        rooms.floor_boards(g, x0 + 0.12, x1 - 0.12, y0 + 0.12, y1 - 0.12, zf)
        rooms.ceiling(g, x0 + 0.12, x1 - 0.12, y0 + 0.12, y1 - 0.12, zh - 0.05)
        # waiting room (west half) + office (east end)
        xo = x1 - 4.2
        rooms.partition(g, 'y', xo, y0 + 0.12, y1 - 0.12, zf, zh - 0.05, doors=[((y0 + y1) / 2 - 0.5, (y0 + y1) / 2 + 0.5)], kind="wood_dark")
        for k in range(3):
            props.bench(g, x0 + 2.2 + k * 2.4, y1 - 0.55, 1.8, face='N', z=zf - 0.3)
        rooms.pot_stove(g, x0 + L * 0.3, (y0 + y1) / 2, zf)
        rooms.desk(g, xo + 1.4, y0 + 1.0, zf, face='S')
        rooms.desk(g, xo + 2.8, y1 - 1.2, zf, face='N', papers=True)
        rooms.shelf(g, xo + 0.5, xo + 3.2, y1 - 0.45, zf, face='S', goods="jars", seed=3)
        for k_, nm_ in enumerate(("poster0", "poster1", "notice", "poster2")):
            ip = f"kit/{st['id']}_{nm_}.png"
            if os.path.exists(f"{_R}/tex/{ip}"):
                face_plane(f"kit_in_{st['id']}_{k_}", ip, 'S', x0 + 2.0 + k_ * 1.5, y1 - 0.14, zf + 1.1, 0.75, h=1.0, off=0.0)
        rooms.lamp_point(x0 + L * 0.3, (y0 + y1) / 2, zh - 0.5, 40)
        rooms.lamp_point(xo + 2.0, (y0 + y1) / 2, zh - 0.5, 40)
    g.build()
    # signs
    face_plane(f"kit_fac_{st['id']}", tx[1], 'S', x0 + L * 0.42 + 1.0, y0 - 0.14, zh - 0.62, 2.6, off=0.0)
    face_plane(f"kit_facN_{st['id']}", tx[1], 'N', x0 + L * 0.45 + 0.95, y1 + 0.14, zh - 0.62, 2.6, off=0.0)


def furniture(x0, x1, yb, st, tx, rng):
    g = G(f"kit_furn_{st['id']}", "Props")
    for x in np.arange(x0 + 4, x1 - 3, 11):
        props.lamp_post(g, float(x), yb - 0.4, side=-1)
    for xc in (x0 + (x1 - x0) * 0.25, x0 + (x1 - x0) * 0.75):
        for yy, fc, off in ((yb - 1.0, 'S', -0.06), (yb - 1.0, 'N', 0.06)):
            pass
        g.a("pole_new").box(xc - 1.3, xc - 1.2, yb - 1.0, yb - 0.9, Z_PLAT, Z_PLAT + 2.2)
        g.a("pole_new").box(xc + 1.2, xc + 1.3, yb - 1.0, yb - 0.9, Z_PLAT, Z_PLAT + 2.2)
        face_plane(f"kit_nm_s_{st['id']}_{xc:.0f}", tx[0], 'S', xc, yb - 1.0 - 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
        face_plane(f"kit_nm_n_{st['id']}_{xc:.0f}", tx[0], 'N', xc, yb - 1.0 + 0.06, Z_PLAT + 1.22, 2.9, h=0.96)
    g.build()


def poles(x0, x1, y, step=40.0):
    g = G("kit_poles", "Props")
    xs = np.arange(x0, x1 + 1, step)
    anch = []
    for x in xs:
        anch.append(props.pole(g, float(x), y, h=8.0, arms=((7.4, 0.9, 3),), axis='y', old=True))
    g.build()


def town(rng, xr=(-60, 60), road_y=15.0, n=6, skip=(), south=False):
    placed = 0
    x = xr[0]
    k = 0
    while x < xr[1] and placed < n:
        kind = rng.choice(["farm", "farm", "shop", "kura"])
        w = rng.uniform(8, 11)
        if not any(a < x + w and x < b for a, b in skip):
            y = road_y + 3.5 + rng.uniform(0, 3) if not south else road_y - 3.5 - rng.uniform(7, 9)
            if kind == "farm":
                houses.farmhouse2(x, y, w=w, d=7.0, name=f"kit_h{k}", variant=rng.randint(0, 1), seed=k)
            elif kind == "shop":
                houses.shop2(x, y, w=8.0, d=6.0, name=f"kit_s{k}")
            else:
                houses.kura2(x, y, name=f"kit_k{k}")
            placed += 1
        x += w + rng.uniform(5, 14)
        k += 1


def trees(rng, n=14, L=100):
    import veg
    for i in range(n):
        x, y = rng.uniform(-L, L), rng.choice([rng.uniform(-60, -25), rng.uniform(26, 60)])
        (veg.zelkova if i % 3 else veg.sugi)(x, y, seed=100 + i) if True else None


def road(y=14.5, L=120):
    core.ribbon("kit_road", [(-L, y), (-L / 2, y + 0.4), (0, y), (L, y)], 4.4, M["road"])
    core.apron("kit_fc", -6, y - 2.5, 14, 4.2, M["road"])



def mats():
    if "brick" not in M:
        M["brick"] = lib.mat_pbr("kit_brick", "Concrete044D", scale=2.0, hsv=(0.5, 0.9, 0.8), tint=(0.62, 0.28, 0.2), tint_amt=0.85,
                                 rough=0.85, bump=1.0, dirt=0.4, spec=0.1)
        M["plasterw"] = lib.mat_pbr("kit_plasterw", "Concrete036", scale=1.6, hsv=(0.5, 0.5, 1.15), tint=(0.95, 0.9, 0.78), tint_amt=0.8, dirt=0.5, bump=0.3, spec=0.1)


def hip_roof(g, x0, x1, y0, y1, zw, rise, ov=0.9, thick=0.14):
    a = g
    xa, xb, ya, yb = x0 - ov, x1 + ov, y0 - ov, y1 + ov
    r = min((xb - xa), (yb - ya)) / 2
    xr0, xr1 = xa + (yb - ya) / 2 * 0.9, xb - (yb - ya) / 2 * 0.9
    ym = (ya + yb) / 2
    z0, z1 = zw - 0.18, zw + rise
    for (p0, p1, p2, p3) in (((xa, ya, z0), (xb, ya, z0), (xr1, ym, z1), (xr0, ym, z1)),
                             ((xb, yb, z0), (xa, yb, z0), (xr0, ym, z1), (xr1, ym, z1)),
                             ((xa, yb, z0), (xa, ya, z0), (xr0, ym, z1), (xr0, ym, z1)),
                             ((xb, ya, z0), (xb, yb, z0), (xr1, ym, z1), (xr1, ym, z1))):
        a.quad_pts(p0, p1, p2, p3)
        a.quad_pts(p3, p2, p1, p0)


def footbridge(g, x, ya, yb, covered=False, z=5.2, kind="steel", lo_turn=True, piers=None, mid=None):
    """跨線橋。桁は軌道を跨ぎ、橋脚は両端のホーム上(と長い場合のみ中間の線間)に立てる。
    lo側(島式/B面ホーム)の階段は、ホーム幅に収まるよう線路と平行(+x方向)に降りる。hi側(A面ホーム)は駅前側(+y)へ降りる。"""
    key = "iron_black" if kind == "steel" else "wood_dark"
    d = g.a(key, bevel=0.01)
    lo, hi = min(ya, yb), max(ya, yb)
    d.box(x - 1.0, x + 1.0, lo - 0.9, hi, z - 0.2, z)                   # デッキ(lo端はホーム中心を越えて 0.9m)
    for xx in (x - 1.0, x + 1.0):
        d.box(xx - 0.04, xx + 0.04, lo - 0.9, hi, z, z + 1.1)           # 欄干
    # 桁の下: 縦桁(側桁) と 橋脚(両端のホーム上のみ。長スパンのみ中間に1本)
    for xx in (x - 0.95, x + 0.95):
        d.box(xx - 0.06, xx + 0.06, lo - 0.9, hi, z - 0.65, z - 0.2)
    piers = piers if piers else [lo, hi] + ([(lo + hi) / 2] if (hi - lo) > 16.0 else [])
    for yy in piers:
        for xx in (x - 0.95, x + 0.95):
            d.box(xx - 0.12, xx + 0.12, yy - 0.12, yy + 0.12, 0.0, z - 0.65)
        d.box(x - 1.1, x + 1.1, yy - 0.1, yy + 0.1, z - 0.8, z - 0.55)  # 橋脚の梁
    if covered:
        g.a("tin").box(x - 1.3, x + 1.3, lo - 1.2, hi + 0.3, z + 2.2, z + 2.3)
        for yy in np.arange(lo - 0.9, hi + 0.1, 4.0):
            for xx in (x - 1.2, x + 1.2):
                g.a("wood_dark").box(xx - 0.06, xx + 0.06, yy - 0.06, yy + 0.06, z, z + 2.2)
    n = 18
    rise = z / n
    # hi側: +y(駅前)へ降りる
    for k in range(n):
        y0 = hi + k * 0.3
        d.box(x - 0.9, x + 0.9, y0, y0 + 0.3, z - (k + 1) * rise - 0.0, z - k * rise - 0.12)
        d.box(x - 0.9, x + 0.9, y0, y0 + 0.03, z - (k + 1) * rise, z - k * rise - 0.12)       # 蹴込み板
    for xx in (x - 0.93, x + 0.93):                                                          # 側桁(段の下を斜めに受ける)
        d.sbox((xx, hi, z - 0.35), (xx, hi + n * 0.3, 0.0), 0.05, 0.28)
    for xx in (x - 1.0, x + 1.0):
        d.sbox((xx, hi, z + 1.0), (xx, hi + n * 0.3, 1.0), 0.05, 0.05)
    for ym in (mid or []):                                             # 中間の島式ホームへの階段(-x 方向)
        for k_ in range(n):
            x0_ = x - 1.0 - (k_ + 1) * 0.3
            d.box(x0_, x0_ + 0.3, ym - 0.9, ym + 0.9, z - (k_ + 1) * rise, z - k_ * rise - 0.12)
            d.box(x0_ + 0.27, x0_ + 0.3, ym - 0.9, ym + 0.9, z - (k_ + 1) * rise, z - k_ * rise - 0.12)
        for yy in (ym - 0.93, ym + 0.93):
            d.sbox((x - 1.0, yy, z - 0.35), (x - 1.0 - n * 0.3, yy, 0.0), 0.28, 0.05)
        for yy in (ym - 0.9, ym + 0.9):
            d.sbox((x - 1.0, yy, z + 1.0), (x - 1.0 - n * 0.3, yy, 1.0), 0.05, 0.05)
    # lo側: ホーム上を +x へ降りる(lo_turn)か、従来どおり -y へ降りる
    if lo_turn:
        for k in range(n):
            x0_ = x + 1.0 + k * 0.3
            d.box(x0_, x0_ + 0.3, lo - 0.9, lo + 0.9, z - (k + 1) * rise, z - k * rise - 0.12)
            d.box(x0_, x0_ + 0.03, lo - 0.9, lo + 0.9, z - (k + 1) * rise, z - k * rise - 0.12)
        for yy in (lo - 0.93, lo + 0.93):
            d.sbox((x + 1.0, yy, z - 0.35), (x + 1.0 + n * 0.3, yy, 0.0), 0.28, 0.05)
        for yy in (lo - 0.9, lo + 0.9):
            d.sbox((x + 1.0, yy, z + 1.0), (x + 1.0 + n * 0.3, yy, 1.0), 0.05, 0.05)
    else:
        for k in range(n):
            y0 = lo - k * 0.3
            d.box(x - 0.9, x + 0.9, y0 - 0.3, y0, z - (k + 1) * rise, z - k * rise - 0.12)


def snowshed(g, x0, x1, y0, y1, h=3.6):
    for x in np.arange(x0, x1 + 0.1, 3.0):
        g.a("wood_dark", bevel=0.01).box(x - 0.12, x + 0.12, y1 - 0.12, y1 + 0.12, Z_PLAT, Z_PLAT + h)
        g.a("wood_dark", bevel=0.01).box(x - 0.1, x + 0.1, y0 - 0.1, y0 + 0.1, Z_PLAT, Z_PLAT + h - 0.8)
        g.a("wood_dark").sbox((x, y0, Z_PLAT + h - 0.8), (x, y1, Z_PLAT + h), 0.14, 0.2, up=(1, 0, 0))
    g.a("tin").extrude_x([(y0 - 0.4, Z_PLAT + h - 0.85), (y1 + 0.3, Z_PLAT + h + 0.05), (y1 + 0.3, Z_PLAT + h - 0.05), (y0 - 0.4, Z_PLAT + h - 0.95)], x0 - 0.3, x1 + 0.3)


def terminal(N, L0=-100, X1=36, hall=(0, 34)):
    """Stub-end terminal: N tracks with platforms between, steel-and-glass train shed, buffer stops, concourse at the head."""
    ys = [-i * 5.2 for i in range(N)]
    for i, y in enumerate(ys):
        P = np.array([[L0, y], [X1, y]], float)
        trackkit.build_track(f"kit_trk{i}", P, wooden=True, ballast=True, fittings=True, cam=None)
        trackkit.buffer_stop(X1 + 0.5, y, 0)
    for i in range(0, N - 1, 2):
        platform(hall[0] - 40, X1 - 1, ys[i] - 1.7 - 0.0, ys[i] - 1.7 + 0.0 + (ys[i] - ys[i + 1]) - 3.4 + 3.4 if False else ys[i] - 1.7 + 0.0, name=f"kit_plat{i}") if False else None
    for i in range(0, N - 1):
        y_hi, y_lo = ys[i] - 1.7, ys[i + 1] + 1.7
        if y_hi - y_lo > 0.5:
            platform(hall[0] - 40, X1 - 1, y_lo, y_hi, name=f"kit_plat{i}")
    g = G("kit_hall", "Station")
    top = Z_PLAT + 8.5
    ylo, yhi = ys[-1] - 3.5, ys[0] + 3.5
    for x in np.arange(hall[0], hall[1] + 0.1, 6.0):
        for y in (ylo, yhi):
            g.a("iron_black", bevel=0.01).box(x - 0.2, x + 0.2, y - 0.2, y + 0.2, 0.0, top)
        g.a("iron_black").sbox((x, ylo, top), (x, (ylo + yhi) / 2, top + 2.8), 0.16, 0.3, up=(1, 0, 0))
        g.a("iron_black").sbox((x, yhi, top), (x, (ylo + yhi) / 2, top + 2.8), 0.16, 0.3, up=(1, 0, 0))
    g.a("glass").extrude_x([(ylo - 0.5, top + 0.1), ((ylo + yhi) / 2, top + 2.9), ((ylo + yhi) / 2, top + 2.86), (ylo - 0.5, top + 0.06)], hall[0], hall[1])
    g.a("glass").extrude_x([(yhi + 0.5, top + 0.1), ((ylo + yhi) / 2, top + 2.9), ((ylo + yhi) / 2, top + 2.86), (yhi + 0.5, top + 0.06)], hall[0], hall[1])
    g.build()
    return ys, (ylo, yhi)


# ------------------------------------------------------------------ generic builder (layout x building x cross from the network data)
def build_generic(sid, seed=0):
    REACH_CUR[0] = REACH.get(sid)
    mats()
    st = ST[sid]
    names = {s["id"]: s["name"] for s in NET["stations"]}
    o = NET["order"].get(st["lines"][0], [])
    i = o.index(sid) if sid in o else -1
    prev = names[o[i - 1]] if i > 0 else None
    nxt = names[o[i + 1]] if 0 <= i < len(o) - 1 else None
    rng = random.Random(seed or (sum(map(ord, sid)) * 31))
    tx = boards(st, prev, nxt)
    lay, bld, cross, ntr = st["layout"], st["building"], st["cross"], st["tracks"]
    ground()
    wall, roof, w = "wall", "gabled", 10.0
    if "brick" in bld:
        wall = "brick"
    if "concrete" in bld or "art_deco" in bld or "tile" in bld or "marble" in bld:
        wall, roof = "plasterw", "flat"
    if "log" in bld:
        wall, w = "wood", 8.0
    if "hip" in bld:
        roof = "hip"
    if "small" in bld or "halt" in bld or "hut" in bld:
        w = 7.0
    if "long" in bld or "inn" in bld:
        w = 13.0
    if "two_story" in bld or "tower" in bld:
        w += 2
    if lay.startswith("terminal_stub") and ntr > 1:
        ys, (ylo, yhi) = terminal(min(ntr, 12))
        station_building(36, 52, ylo, yhi, st, tx, wall=wall if wall != "wall" else "plasterw", roof="flat")
        face_plane(f"kit_sgn_{sid}", tx[1], 'W', 36 - 0.12, (ylo + yhi) / 2, 8.0, 7.0, off=0.0)
        poles(-110, 0, yhi + 3)
        road(y=yhi + 22)
        town(rng, (-60, 70), road_y=yhi + 22, n=8)
        return
    if lay.startswith("island") or lay.startswith("elevated_island"):
        ys = [0.0, -8.4][:2]
        tracks(-120, 120, ys)
        platform(-22, 22, -6.7, -1.7, name="kit_island")
        station_building(-6, -6 + w, 6.0, 10.0, st, tx, wall=wall, roof=roof)
        footbridge(G("kit_fb", "Station"), -10, 10.0, -6.7) if False else None
        gfb = G("kit_fb", "Station")
        footbridge(gfb, -10 + 0.0, 5.0, -6.7, covered=("covered" in cross or "wood" in cross), kind="wood" if "wood" in cross else "steel")
        gfb.build()
        furniture(-22, 22, -2.0, st, tx, rng)
        by, ry = 10.0, 15.0
    elif lay.startswith("side_dual") or "overpass" in lay:
        ys = [0.0, -4.6]
        tracks(-120, 120, ys + ([-9.2] if ntr > 2 else []))
        platform(-20, 22, 1.7, 4.4, name="kit_platA")
        platform(-20, 22, -9.0, -6.3, name="kit_platB") if ntr <= 2 else None
        station_building(-8, -8 + w, 4.4, 8.4, st, tx, wall=wall, roof=roof)
        gfb = G("kit_fb", "Station")
        footbridge(gfb, 8, 4.4, -9.0, covered=("covered" in cross or "wood" in cross), kind="wood" if "wood" in cross else "steel")
        gfb.build()
        furniture(-20, 22, 4.4, st, tx, rng)
        by, ry = 8.4, 14.5
    elif "snowshed" in bld:
        tracks(-120, 120, [0.0, -4.6] if ntr > 1 else [0.0])
        platform(-24, 24, 1.7, 4.4)
        station_building(-6, -6 + 7, 4.4, 8.4, st, tx, wall="wood", roof="gabled")
        gg = G("kit_snow", "Station")
        snowshed(gg, -24, 24, 1.8, 4.4)
        gg.build()
        furniture(-24, 24, 4.4, st, tx, rng)
        by, ry = 8.4, 14.5
    else:   # side platform(s)
        tracks(-120, 120, [0.0, -4.6][:max(1, min(2, ntr))])
        platform(-18, 22, 1.7, 4.4)
        station_building(-12 if w > 9 else -8, (-12 if w > 9 else -8) + w, 4.4, 8.4, st, tx, wall=wall, roof=roof)
        furniture(-18, 22, 4.4, st, tx, rng)
        by, ry = 8.4, 14.5
    import kit_town as KT
    th = __import__("make_posters").THEME.get(sid, "farm")
    dens = {"city": 0.9, "suburb": 0.7, "harbor": 0.6, "origin": 0.6, "onsen": 0.55, "freight": 0.4, "farm": 0.35}.get(th, 0.25)
    if dens > 0.6:
        ry += 6
    poles(-110, 110, -2.0 if lay.startswith("side") else 2.0)
    road(y=ry)
    KT.decorate_platform(sid, -18, 22, -3.0 if (lay.startswith("island") or lay.startswith("elevated_island")) else 4.4, rng)
    if dens < 0.4:
        town(rng, (-70, 70), road_y=ry, n=6 + (ntr > 2) * 3, skip=[(-14, 6)])
        KT.dense_row(sid, st, rng, ry + 3.0, (-40, -16), 'S', dens, ["shop"], f"kt{sid}n")
        KT.dense_row(sid, st, rng, ry + 3.0, (8, 40), 'S', dens, ["shop"], f"kt{sid}m")
    else:
        KT.dense_row(sid, st, rng, ry + 3.0, (-80, 80), 'S', dens, ["shop"], f"kt{sid}a")
        KT.dense_row(sid, st, rng, ry + 3.0 + 11.0, (-80, 80), 'S', dens * 0.8, ["shop"], f"kt{sid}b")
        KT.dense_row(sid, st, rng, ry - 2.4 - 6.5, (-80, -16), 'N', dens, ["shop"], f"kt{sid}c")
        KT.dense_row(sid, st, rng, ry - 2.4 - 6.5, (8, 80), 'N', dens, ["shop"], f"kt{sid}d")
        KT.fence(-80, 80, ry + 3.0 + 22.0, name="kt_back")
    KT.billboard(sid, 30, ry + 2.4, KT.img(sid, "bb0"), 'S', name=f"bb_{sid}0")
    KT.billboard(sid, -50, ry - 2.6, KT.img(sid, "bb1"), 'N', name=f"bb_{sid}1")
    trees(rng, n=10)
    import sig
    sig.place(sid)


BUILDERS = {}


def build_zone(sid, origin=(0, 0, 0), yaw=0.0):
    with Zone(sid, origin, yaw):
        build_generic(sid)
