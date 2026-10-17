"""Furnished building interiors: hollow shells with real openings + clear glass, rooms, furniture, interior lights.
All axis-aligned (x/y).  Used by props.py (houses, inn, shop, kura, shed, huts) and depot fit-outs."""
from common import *
import lib
import props
from props import G, pm, face_plane
from station import hole_wall

_RM = {}


def rm(key):
    """Interior-only materials."""
    if key in _RM:
        return _RM[key]
    d = {
        "tatami": lambda: lib.mat_plain("rm_tatami", (0.36, 0.34, 0.16), rough=0.95),
        "tatami_edge": lambda: lib.mat_plain("rm_tatami_e", (0.03, 0.03, 0.025), rough=0.8),
        "paper": lambda: lib.mat_plain("rm_paper", (0.78, 0.74, 0.62), rough=0.95),
        "fusuma": lambda: lib.mat_plain("rm_fusuma", (0.50, 0.44, 0.30), rough=0.9),
        "plaster_in": lambda: lib.mat_plaster("rm_plaster_in", (0.52, 0.42, 0.28), dirt=0.9),
        "ceiling": lambda: lib.mat_plain("rm_ceiling", (0.30, 0.21, 0.12), rough=0.9),
        "futon": lambda: lib.mat_plain("rm_futon", (0.16, 0.22, 0.34), rough=0.95),
        "futon2": lambda: lib.mat_plain("rm_futon2", (0.40, 0.18, 0.15), rough=0.95),
        "linen": lambda: lib.mat_plain("rm_linen", (0.70, 0.68, 0.60), rough=0.95),
        "zabuton": lambda: lib.mat_plain("rm_zabuton", (0.30, 0.10, 0.09), rough=0.9),
        "lacquer": lambda: lib.mat_plain("rm_lacquer", (0.03, 0.012, 0.01), rough=0.25, spec=0.8),
        "gold": lambda: lib.mat_plain("rm_gold", (0.7, 0.5, 0.12), rough=0.3, metal=0.9),
        "dirt_floor": lambda: lib.mat_plain("rm_doma", (0.20, 0.14, 0.09), rough=1.0),
        "soot": lambda: lib.mat_plain("rm_soot", (0.02, 0.018, 0.016), rough=0.9),
        "enamel": lambda: lib.mat_plain("rm_enamel", (0.72, 0.72, 0.68), rough=0.3),
        "label": lambda: lib.mat_plain("rm_label", (0.65, 0.55, 0.30), rough=0.8),
        "cabinet_g": lambda: lib.mat_paint("rm_cab_g", (0.20, 0.30, 0.24), rough=0.5, rust=0.3),
        "desk": lambda: lib.mat_wood("rm_desk", (0.20, 0.12, 0.06), rough=0.55, along='X', weather=0.3),
        "book": lambda: lib.mat_plain("rm_book", (0.22, 0.12, 0.10), rough=0.8),
        "tin_sh": lambda: lib.mat_plain("rm_tin_sh", (0.4, 0.4, 0.4), rough=0.5, metal=0.8),
    }
    _RM[key] = d[key]()
    return _RM[key]


RMKEYS = {"tatami", "tatami_edge", "paper", "fusuma", "plaster_in", "ceiling", "futon", "futon2", "linen", "zabuton", "lacquer",
          "gold", "dirt_floor", "soot", "enamel", "label", "cabinet_g", "desk", "book", "tin_sh"}


def A(g, key, bevel=0.0):
    """Accumulator by key: scene materials (M), interior registry, then props registry."""
    if key in M:
        return g.a(key, bevel=bevel)
    if key in RMKEYS:
        return g.a("rm_" + key, rm(key), bevel=bevel)
    return g.a(key, bevel=bevel)


def lamp_point(x, y, z, watt=40.0, color=(1.0, 0.82, 0.58), size=0.25, name="room_light"):
    li = bpy.data.lights.new(name, 'POINT')
    li.energy = watt * 3.0
    li.color = color
    li.shadow_soft_size = size
    ob = bpy.data.objects.new(name, li)
    ob.location = (x, y, z)
    ob.visible_camera = False        # 根本対策: 点光源は半径ぶんの白い円盤としてカメラに映る(窓越しに白丸が見えた)。光は出すが映らないようにする
    link(ob, "Lighting")


def pb(g, key, axis, a0, a1, p0, p1, z0, z1, bevel=0.0):
    acc = A(g, key, bevel)
    if axis == 'x':
        acc.box(a0, a1, p0, p1, z0, z1)
    else:
        acc.box(p0, p1, a0, a1, z0, z1)


DOORS = []          # 開口の登録(K2検査用): dict(stack, axis, p0, p1, a0, a1, z0, z1, kind, out)
SZ_STACK = []       # SubZone の入れ子 [(origin, yaw), ...]


def fill_opening(g, axis, p0, p1, a0, a1, z0, z1, kind, out):
    """Frame + glazing for one opening. Wall spans p0..p1 on the perpendicular axis; out = +1/-1 direction of outside."""
    if kind in ("door", "open") or (kind == "slide" and z0 < 0.9):
        DOORS.append(dict(stack=list(SZ_STACK), axis=axis, p0=p0, p1=p1, a0=a0, a1=a1, z0=z0, z1=z1, kind=kind, out=out))
    pc = (p0 + p1) / 2
    fr = lambda *a, **k: pb(g, "wood_dark", axis, *a, **k)
    fr(a0 - 0.04, a1 + 0.04, p0 - 0.01, p1 + 0.01, z1, z1 + 0.07)              # lintel
    fr(a0 - 0.04, a1 + 0.04, p0 - 0.02, p1 + 0.04, z0 - 0.06, z0)              # sill
    fr(a0 - 0.04, a0, p0, p1, z0, z1)
    fr(a1, a1 + 0.04, p0, p1, z0, z1)
    if kind == 'open':
        return
    w = a1 - a0
    if kind in ('glass', 'slide'):
        nl = 2 if w > 0.9 else 1
        lw = w / nl + 0.04
        for k in range(nl):
            la = a0 + k * (w - lw) / max(1, nl - 1) if nl > 1 else a0
            pp = pc + (0.02 if k % 2 else -0.02)
            fr(la, la + lw, pp - 0.015, pp + 0.015, z0, z0 + 0.05)
            fr(la, la + lw, pp - 0.015, pp + 0.015, z1 - 0.05, z1)
            fr(la, la + 0.05, pp - 0.015, pp + 0.015, z0, z1)
            fr(la + lw - 0.05, la + lw, pp - 0.015, pp + 0.015, z0, z1)
            nh = max(2, int(lw / 0.32))
            for i in range(1, nh):
                xx = la + lw * i / nh
                fr(xx - 0.008, xx + 0.008, pp - 0.008, pp + 0.008, z0 + 0.05, z1 - 0.05)
            nv = max(2, int((z1 - z0) / 0.34))
            for j in range(1, nv):
                zz = z0 + (z1 - z0) * j / nv
                fr(la + 0.05, la + lw - 0.05, pp - 0.008, pp + 0.008, zz - 0.008, zz + 0.008)
            pb(g, "glass", axis, la + 0.05, la + lw - 0.05, pp - 0.003, pp + 0.003, z0 + 0.05, z1 - 0.05)
        if kind == 'slide':   # shoji on the inside, one leaf open
            ps = pc - out * 0.07
            sa = a0 + w * 0.5
            pb(g, "paper", axis, sa, a1, ps - 0.01, ps + 0.01, z0, z1)
            for i in range(1, 4):
                xx = sa + (a1 - sa) * i / 4
                fr(xx - 0.01, xx + 0.01, ps - 0.012, ps + 0.012, z0, z1)
            for j in range(1, 6):
                zz = z0 + (z1 - z0) * j / 6
                fr(sa, a1, ps - 0.012, ps + 0.012, zz - 0.01, zz + 0.01)
    elif kind == 'door':      # wooden sliding door, half open
        pp = pc + out * 0.03
        pb(g, "wood_dark", axis, a0 + w * 0.45, a1, pp - 0.03, pp + 0.03, z0, z1, bevel=0.004)
        for i in range(5):
            pb(g, "iron_black", axis, a0 + w * 0.45 + i * w * 0.11, a0 + w * 0.45 + i * w * 0.11 + 0.012, pp - 0.035, pp + 0.035, z0, z1)
    elif kind == 'shutter':   # tin rolling shutter half raised
        pb(g, "tin", axis, a0, a1, pc - 0.02, pc + 0.02, z0, z0 + (z1 - z0) * 0.35)


def shell(g, x0, x1, y0, y1, zb, zh, t=0.12, ops=None, wall="wall"):
    """Four walls with holes. ops = {'S':[(a0,a1,z0,z1,kind)], 'N':[..], 'W':[..], 'E':[..]} (a in world x for S/N, world y for W/E)."""
    ops = ops or {}
    wl = g.a(wall, bevel=0.008)
    for side, axis, c0, c1, p0, p1, out in (("S", 'x', x0, x1, y0, y0 + t, -1), ("N", 'x', x0, x1, y1 - t, y1, 1),
                                           ("W", 'y', y0 + t, y1 - t, x0, x0 + t, -1), ("E", 'y', y0 + t, y1 - t, x1 - t, x1, 1)):
        lst = sorted(ops.get(side, []))
        hole_wall(wl, axis, c0, c1, p0, p1, zb, zh, [(a, b, za, zb2) for (a, b, za, zb2, k) in lst])
        for (a, b, za, zb2, k) in lst:
            fill_opening(g, axis, p0, p1, a, b, za, zb2, k, out)


def partition(g, axis, pos, a0, a1, z0, z1, doors=(), kind="fusuma", t=0.06):
    """Interior wall along `axis` at perpendicular position pos; doors = [(d0,d1)] openings."""
    cur = a0
    for (d0, d1) in sorted(doors):
        pb(g, kind, axis, cur, d0, pos - t / 2, pos + t / 2, z0, z1)
        pb(g, "wood_dark", axis, d0, d1, pos - t / 2, pos + t / 2, z1 - 0.18, z1)
        cur = d1
    pb(g, kind, axis, cur, a1, pos - t / 2, pos + t / 2, z0, z1)
    # frame posts at each end / door side
    for q in [a0, a1] + [d for ds in doors for d in ds]:
        pb(g, "wood_dark", axis, q - 0.05, q + 0.05, pos - 0.06, pos + 0.06, z0, z1)
    pb(g, "wood_dark", axis, a0, a1, pos - 0.06, pos + 0.06, z1 - 0.1, z1)     # nageshi beam


# ------------------------------------------------------------------ floors / ceilings
def floor_tatami(g, x0, x1, y0, y1, z, along='x'):
    """Tatami mats 0.9x1.8 filling the rectangle (approx)."""
    tw, tl = 0.91, 1.82
    t = A(g, "tatami", 0.004)
    e = A(g, "tatami_edge")
    if along == 'x':
        nx, ny = max(1, round((x1 - x0) / tl)), max(1, round((y1 - y0) / tw))
        sx, sy = (x1 - x0) / nx, (y1 - y0) / ny
        for i in range(nx):
            for j in range(ny):
                xa, ya = x0 + i * sx, y0 + j * sy
                t.box(xa + 0.004, xa + sx - 0.004, ya + 0.004, ya + sy - 0.004, z - 0.05, z)
                e.box(xa + 0.004, xa + sx - 0.004, ya + 0.004, ya + 0.03, z - 0.049, z + 0.002)
                e.box(xa + 0.004, xa + sx - 0.004, ya + sy - 0.03, ya + sy - 0.004, z - 0.049, z + 0.002)
    else:
        ny, nx = max(1, round((y1 - y0) / tl)), max(1, round((x1 - x0) / tw))
        sx, sy = (x1 - x0) / nx, (y1 - y0) / ny
        for i in range(nx):
            for j in range(ny):
                xa, ya = x0 + i * sx, y0 + j * sy
                t.box(xa + 0.004, xa + sx - 0.004, ya + 0.004, ya + sy - 0.004, z - 0.05, z)
                e.box(xa + 0.004, xa + 0.03, ya + 0.004, ya + sy - 0.004, z - 0.049, z + 0.002)
                e.box(xa + sx - 0.03, xa + sx - 0.004, ya + 0.004, ya + sy - 0.004, z - 0.049, z + 0.002)


def floor_boards(g, x0, x1, y0, y1, z):
    A(g, "floor", 0.004).box(x0, x1, y0, y1, z - 0.06, z)


def floor_dirt(g, x0, x1, y0, y1, z):
    A(g, "dirt_floor").box(x0, x1, y0, y1, z - 0.2, z)


def ceiling(g, x0, x1, y0, y1, z, beams_axis='y', step=0.9):
    A(g, "ceiling").box(x0, x1, y0, y1, z, z + 0.04)
    b = A(g, "wood_dark", 0.01)
    if beams_axis == 'y':
        for xx in np.arange(x0 + 0.3, x1, step):
            b.box(xx - 0.06, xx + 0.06, y0, y1, z - 0.2, z)
    else:
        for yy in np.arange(y0 + 0.3, y1, step):
            b.box(x0, x1, yy - 0.06, yy + 0.06, z - 0.2, z)


def liner(g, x0, x1, y0, y1, zlo, zhi, key="plaster_in", t=0.02, sides="SNWE"):
    """Interior wall lining (plaster / paper) pressed against the inside faces; keeps window holes open by leaving them to caller."""
    pass


# ------------------------------------------------------------------ furniture
def zabuton(g, x, y, z, yaw=0):
    A(g, "zabuton", 0.03).box(x - 0.28, x + 0.28, y - 0.28, y + 0.28, z, z + 0.07)


def chabudai(g, x, y, z):
    A(g, "wood", 0.01).cyl((x, y, z + 0.33), (x, y, z + 0.37), 0.45, seg=18)
    for k in range(4):
        a = k * math.pi / 2 + 0.7
        A(g, "wood").cyl((x + math.cos(a) * 0.3, y + math.sin(a) * 0.3, z), (x + math.cos(a) * 0.3, y + math.sin(a) * 0.3, z + 0.33), 0.025, seg=6)
    # tea set
    A(g, "enamel").cyl((x, y, z + 0.37), (x, y, z + 0.5), 0.07, seg=10)
    for k in range(3):
        a = k * 2.1
        A(g, "milk").cyl((x + math.cos(a) * 0.25, y + math.sin(a) * 0.25, z + 0.37), (x + math.cos(a) * 0.25, y + math.sin(a) * 0.25, z + 0.42), 0.04, seg=8)
        zabuton(g, x + math.cos(a) * 0.75, y + math.sin(a) * 0.75, z)


def low_table(g, x, y, z, sx=1.0, sy=0.6):
    A(g, "lacquer", 0.01).box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z + 0.3, z + 0.35)
    for a in (-1, 1):
        for b in (-1, 1):
            A(g, "lacquer").box(x + a * (sx / 2 - 0.05) - 0.02, x + a * (sx / 2 - 0.05) + 0.02, y + b * (sy / 2 - 0.05) - 0.02, y + b * (sy / 2 - 0.05) + 0.02, z, z + 0.3)


def futon(g, x, y, z, along='x', c="futon"):
    if along == 'x':
        A(g, c, 0.04).box(x - 0.95, x + 0.95, y - 0.45, y + 0.45, z, z + 0.14)
        A(g, "linen", 0.04).box(x - 0.95, x - 0.6, y - 0.2, y + 0.2, z + 0.14, z + 0.22)
        A(g, "futon2" if c == "futon" else "futon", 0.04).box(x - 0.5, x + 0.9, y - 0.47, y + 0.47, z + 0.14, z + 0.2)
    else:
        A(g, c, 0.04).box(x - 0.45, x + 0.45, y - 0.95, y + 0.95, z, z + 0.14)
        A(g, "linen", 0.04).box(x - 0.2, x + 0.2, y - 0.95, y - 0.6, z + 0.14, z + 0.22)
        A(g, "futon2" if c == "futon" else "futon", 0.04).box(x - 0.47, x + 0.47, y - 0.5, y + 0.9, z + 0.14, z + 0.2)


def tansu(g, x, y, z, w=0.9, d=0.45, h=1.2, face='N'):
    """Chest of drawers; front faces `face` (N=+y)."""
    A(g, "wood_dark", 0.01).box(x - w / 2, x + w / 2, y - d / 2, y + d / 2, z, z + h)
    s = 1 if face == 'N' else -1
    yf = y + s * d / 2
    for r in range(4):
        zz = z + 0.08 + r * (h - 0.12) / 4
        A(g, "wood", 0.006).box(x - w / 2 + 0.03, x + w / 2 - 0.03, yf, yf + s * 0.02, zz, zz + (h - 0.12) / 4 - 0.03)
        A(g, "iron_black").box(x - 0.05, x + 0.05, yf + s * 0.02, yf + s * 0.035, zz + 0.1, zz + 0.12)


def shelf(g, x0, x1, y, z, h=1.8, d=0.35, rows=4, face='N', goods="jars", seed=0, key="wood"):
    """Open shelving unit against a wall (along x), depth d toward `face` side."""
    rng = random.Random(seed)
    s = 1 if face == 'N' else -1
    ya, yb = (y, y + s * d) if s > 0 else (y + s * d, y)
    A(g, key, 0.006).box(x0, x0 + 0.04, ya, yb, z, z + h)
    A(g, key, 0.006).box(x1 - 0.04, x1, ya, yb, z, z + h)
    for r in range(rows + 1):
        zz = z + 0.08 + r * (h - 0.1) / rows
        A(g, key, 0.006).box(x0, x1, ya, yb, zz, zz + 0.03)
    A(g, "wood_dark").box(x0, x1, y - 0.0 if s < 0 else y, y + 0.015 if s > 0 else y + 0.0, z, z + h)
    ym = (ya + yb) / 2
    for r in range(rows):
        zz = z + 0.11 + r * (h - 0.1) / rows
        hh = (h - 0.1) / rows - 0.08
        x = x0 + 0.08
        while x < x1 - 0.12:
            kind = goods
            if goods == "mixed":
                kind = rng.choice(["jars", "boxes", "bottles", "cans"])
            if kind == "jars":
                rr = rng.uniform(0.06, 0.1)
                A(g, "bottle" if rng.random() < 0.3 else "tr_cream").cyl((x + rr, ym, zz), (x + rr, ym, zz + min(hh, rng.uniform(0.15, 0.3))), rr, seg=8)
                x += 2 * rr + 0.03
            elif kind == "boxes":
                w = rng.uniform(0.1, 0.22)
                A(g, "label" if rng.random() < 0.5 else "crate", 0.004).box(x, x + w, ym - 0.12, ym + 0.12, zz, zz + min(hh, rng.uniform(0.12, 0.3)))
                x += w + 0.02
            elif kind == "bottles":
                A(g, "bottle").cyl((x + 0.04, ym, zz), (x + 0.04, ym, zz + min(hh, 0.28)), 0.035, seg=8)
                x += 0.1
            elif kind == "books":
                w = rng.uniform(0.025, 0.05)
                A(g, "book").box(x, x + w, ym - 0.12, ym + 0.12, zz, zz + rng.uniform(0.22, min(hh, 0.32)))
                x += w + 0.003
            else:
                A(g, "milk").cyl((x + 0.07, ym, zz), (x + 0.07, ym, zz + min(hh, 0.2)), 0.07, seg=10)
                x += 0.16


def counter(g, x0, x1, y, z, d=0.6, h=0.95, key="wood_dark"):
    A(g, key, 0.01).box(x0, x1, y - d / 2, y + d / 2, z, z + h - 0.05)
    A(g, "desk", 0.01).box(x0 - 0.04, x1 + 0.04, y - d / 2 - 0.05, y + d / 2 + 0.05, z + h - 0.05, z + h)


def desk(g, x, y, z, w=1.3, d=0.7, face='S', papers=True):
    A(g, "desk", 0.01).box(x - w / 2, x + w / 2, y - d / 2, y + d / 2, z + 0.7, z + 0.75)
    for a in (-1, 1):
        for b in (-1, 1):
            A(g, "wood_dark").box(x + a * (w / 2 - 0.05) - 0.03, x + a * (w / 2 - 0.05) + 0.03, y + b * (d / 2 - 0.05) - 0.03, y + b * (d / 2 - 0.05) + 0.03, z, z + 0.7)
    A(g, "wood_dark").box(x + w / 2 - 0.45, x + w / 2 - 0.03, y - d / 2 + 0.03, y + d / 2 - 0.03, z + 0.3, z + 0.7)   # drawer block
    s = -1 if face == 'S' else 1
    if papers:
        A(g, "linen").box(x - 0.3, x + 0.1, y - 0.15, y + 0.15, z + 0.75, z + 0.765)
        A(g, "book").box(x - 0.5, x - 0.35, y - 0.1, y + 0.1, z + 0.75, z + 0.82)
        A(g, "iron_black").cyl((x - 0.1, y + 0.2, z + 0.75), (x - 0.1, y + 0.2, z + 0.8), 0.04, seg=8)
    # chair on the opposite side of the facing
    cy = y + s * 0.65
    A(g, "wood", 0.01).box(x - 0.2, x + 0.2, cy - 0.2, cy + 0.2, z + 0.43, z + 0.47)
    for a in (-1, 1):
        for b in (-1, 1):
            A(g, "wood").box(x + a * 0.17 - 0.015, x + a * 0.17 + 0.015, cy + b * 0.17 - 0.015, cy + b * 0.17 + 0.015, z, z + 0.43)
    A(g, "wood", 0.01).box(x - 0.2, x + 0.2, cy + s * 0.18, cy + s * 0.21, z + 0.47, z + 0.85)


def pot_stove(g, x, y, z, pipe_to=None):
    A(g, "iron_black", 0.02).cyl((x, y, z + 0.05), (x, y, z + 0.8), 0.28, seg=14)
    A(g, "iron_black").cyl((x, y, z), (x, y, z + 0.05), 0.35, seg=14)
    A(g, "iron_black").cyl((x, y, z + 0.8), (x, y, pipe_to or (z + 2.4)), 0.06, seg=8)
    A(g, "iron_rust").box(x - 0.1, x + 0.1, y + 0.25, y + 0.3, z + 0.3, z + 0.5)


def kamado(g, x, y, z, face='S'):
    s = -1 if face == 'S' else 1
    A(g, "plaster2", 0.02).box(x - 0.7, x + 0.7, y - 0.4, y + 0.4, z, z + 0.7)
    for k in (-1, 1):
        A(g, "iron_black").cyl((x + k * 0.3, y, z + 0.7), (x + k * 0.3, y, z + 0.78), 0.2, seg=14)
        A(g, "tin").cyl((x + k * 0.3, y, z + 0.78), (x + k * 0.3, y, z + 1.0), 0.17, 0.14, seg=14)
    A(g, "soot").box(x - 0.2, x + 0.2, y + s * 0.4, y + s * 0.41, z + 0.1, z + 0.4)
    A(g, "plaster2").box(x - 0.2, x + 0.2, y - 0.15, y + 0.15, z + 0.7, z + 2.2) if False else None


def sink_stone(g, x, y, z, w=1.2, d=0.6):
    A(g, "stone", 0.02).box(x - w / 2, x + w / 2, y - d / 2, y + d / 2, z + 0.5, z + 0.8)
    A(g, "wood_dark").box(x - w / 2 + 0.05, x + w / 2 - 0.05, y - d / 2 + 0.05, y + d / 2 - 0.05, z, z + 0.5)
    A(g, "chrome").cyl((x - w / 4, y + d / 2 - 0.1, z + 0.8), (x - w / 4, y + d / 2 - 0.1, z + 1.0), 0.015, seg=6)


def water_jar(g, x, y, z):
    A(g, "tr_grey").cyl((x, y, z), (x, y, z + 0.8), 0.32, 0.26, seg=14)
    A(g, "wood", 0.01).cyl((x, y, z + 0.8), (x, y, z + 0.83), 0.26, seg=14)


def kamidana(g, x, y, z, face='S'):
    s = -1 if face == 'S' else 1
    A(g, "wood", 0.01).box(x - 0.6, x + 0.6, y, y + s * 0.2, z, z + 0.04)
    A(g, "wood_dark", 0.01).box(x - 0.18, x + 0.18, y + s * 0.02, y + s * 0.16, z + 0.04, z + 0.28)
    A(g, "kawara").extrude_x([(y, z + 0.28), (y + s * 0.09, z + 0.36), (y + s * 0.18, z + 0.28)] if s > 0 else [(y + s * 0.18, z + 0.28), (y + s * 0.09, z + 0.36), (y, z + 0.28)], x - 0.22, x + 0.22)
    A(g, "paper").box(x + 0.3, x + 0.4, y + s * 0.02, y + s * 0.03, z - 0.2, z + 0.02)


def butsudan(g, x, y, z, face='S'):
    s = -1 if face == 'S' else 1
    A(g, "lacquer", 0.01).box(x - 0.4, x + 0.4, y - 0.25, y + 0.25, z, z + 0.9)
    yf = y + s * 0.25
    A(g, "gold").box(x - 0.3, x + 0.3, yf, yf + s * 0.01, z + 0.35, z + 0.8)
    A(g, "wood_dark").box(x - 0.34, x + 0.34, yf, yf + s * 0.02, z + 0.3, z + 0.35)
    A(g, "gold").cyl((x + 0.12, yf + s * 0.1, z + 0.35), (x + 0.12, yf + s * 0.1, z + 0.5), 0.02, seg=6)
    A(g, "gold").cyl((x - 0.12, yf + s * 0.1, z + 0.35), (x - 0.12, yf + s * 0.1, z + 0.5), 0.02, seg=6)


def toko_alcove(g, x0, x1, y0, y1, z, zc, back='N'):
    """Tokonoma raised alcove: floor board, post, hanging scroll, vase."""
    A(g, "lacquer", 0.01).box(x0, x1, y0, y1, z, z + 0.12)
    xc = (x0 + x1) / 2
    yb = y1 - 0.03 if back == 'N' else y0 + 0.03
    A(g, "plaster_in").box(x0, x1, y1 - 0.04, y1, z + 0.12, zc) if back == 'N' else None
    A(g, "wood").box(x1 - 0.1, x1, y0, y0 + 0.1, z, zc)
    A(g, "paper").box(xc - 0.25, xc + 0.25, yb - 0.01, yb, z + 0.55, z + 1.55)
    A(g, "wood_dark").box(xc - 0.28, xc + 0.28, yb - 0.015, yb, z + 1.55, z + 1.6)
    A(g, "wood_dark").box(xc - 0.28, xc + 0.28, yb - 0.015, yb, z + 0.5, z + 0.55)
    A(g, "tr_grey").cyl((xc + 0.35, yb - 0.25, z + 0.12), (xc + 0.35, yb - 0.25, z + 0.38), 0.07, 0.05, seg=10)


def sack_pile(g, x, y, z, nx=3, ny=2, nz=3, yaw=0.0, seed=0):
    rng = random.Random(seed)
    sk = A(g, "bag", 0.05)
    for k in range(nz):
        for i in range(nx):
            for j in range(ny):
                if k == nz - 1 and rng.random() < 0.3:
                    continue
                sk.boxc(x + i * 0.42 + (0.2 if k % 2 else 0) + rng.uniform(-0.02, 0.02), y + j * 0.68 + rng.uniform(-0.03, 0.03),
                        z + 0.13 + k * 0.27, 0.40, 0.64, 0.27, rz=rng.uniform(-0.05, 0.05))


def barrel(g, x, y, z, r=0.28, h=0.8):
    A(g, "wood", 0.01).cyl((x, y, z), (x, y, z + h), r, seg=14)
    for zz in (z + 0.15, z + h - 0.15):
        A(g, "iron_black").cyl((x, y, zz - 0.015), (x, y, zz + 0.015), r + 0.01, seg=14)


def room_light_c(x0, x1, y0, y1, z, watt=40.0):
    lamp_point((x0 + x1) / 2, (y0 + y1) / 2, z, watt)


def stair_run(g, axis, a_from, a_to, c, z_from, z_to, width=2.4, rise=0.18, key="concrete", rail="iron_black", rails=True):
    """直線階段(段板+蹴込み+手すり)。axis='y': 進行方向 y 、中心 x=c。axis='x': 進行方向 x 、中心 y=c。
    a_from(z_from, 下端)→a_to(z_to, 上端)。段は厚み0.25の板で、下に空間を残す(穴あけは呼び出し側が行う)。"""
    n = max(2, int(math.ceil((z_to - z_from) / rise)))
    dz = (z_to - z_from) / n
    da = (a_to - a_from) / n
    acc = A(g, key, 0.006)
    for k in range(n):
        s0, s1 = a_from + k * da, a_from + (k + 1) * da
        zt = z_from + (k + 1) * dz
        lo, hi = min(s0, s1), max(s0, s1)
        if axis == 'y':
            acc.box(c - width / 2, c + width / 2, lo, hi, zt - 0.25, zt)
        else:
            acc.box(lo, hi, c - width / 2, c + width / 2, zt - 0.25, zt)
    # 側桁(斜め)
    r = A(g, rail)
    for s in (-1, 1):
        cc = c + s * (width / 2 + 0.03)
        p0 = (cc, a_from, z_from + 0.9) if axis == 'y' else (a_from, cc, z_from + 0.9)
        p1 = (cc, a_to, z_to + 0.9) if axis == 'y' else (a_to, cc, z_to + 0.9)
        if rails:
            r.sbox(p0, p1, 0.05, 0.05)
            for k in range(0, n + 1, 4):
                s_ = a_from + k * da
                zz = z_from + k * dz
                pa = (cc, s_, zz) if axis == 'y' else (s_, cc, zz)
                pb_ = (cc, s_, zz + 0.9) if axis == 'y' else (s_, cc, zz + 0.9)
                r.sbox(pa, pb_, 0.04, 0.04)
    return n
