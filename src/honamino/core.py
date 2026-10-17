"""Terrain, paddies, track, platform, dirt roads, level crossing."""
from common import *
from mathutils import noise as mn


def ss(a, b, t):
    t = np.clip((t - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def grid_mesh(name, xs, ys, Z, mat, col="Terrain", colors=None, smooth=True):
    nx, ny = len(xs), len(ys)
    X, Y = np.meshgrid(xs, ys)
    V = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    idx = np.arange(nx * ny).reshape(ny, nx)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
    return np_mesh(name, V, T, mat, col, colors=colors, smooth=smooth)


# ------------------------------------------------------------------ ground
def build_ground():
    xs = np.unique(np.concatenate([np.arange(-600, -100, 25), np.arange(-100, 100.1, 4.0), np.arange(100, 601, 25)]))
    ys = np.unique(np.concatenate([np.arange(-600, -100, 25), np.arange(-100, 130.1, 4.0), np.arange(130, 601, 25)]))
    Z = np.zeros((len(ys), len(xs)))
    for j, y in enumerate(ys):
        south = ss(-125.0, -126.5, y)
        north = ss(24.0, 25.4, y)
        Z[j, :] = -0.2 * np.maximum(south, north)
    grid_mesh("ground", xs, ys, Z, M["grass_ground"])


# ------------------------------------------------------------------ paddies, levees
HQ_ON = False
HQ_ZONE = (43.0, 125.0, 25.0, 58.0)
PLOTS_X = [(-110, -84), (-84, -61), (-61, -40), (-40, -19), (-19, 5), (5, 34), (43, 68), (68, 95), (95, 125)]
PLOTS_YS = [(-127.3, -145), (-145, -165), (-165, -190)]
PLOTS_YN = [(25.8, 41), (41, 58), (58, 78), (78, 104)]
HARVESTED = []   # (x0,x1,y0,y1) of plots with stubble (hasa racks go here)
NEWDEPOT_ON = False            # D4/D5: 新・総合車両基地の敷地(x>=35 の南側)では水田を作らない
NEWDEPOT_X0 = 35.0


def build_paddies():
    rng = random.Random(8)
    lev = Acc("levees", M["soil"], "Terrain", closed=True)
    for rows in (PLOTS_YS, PLOTS_YN):
        for (x0, x1) in PLOTS_X:
            for (ya, yb) in rows:
                y0, y1 = min(ya, yb), max(ya, yb)
                harvested = rng.random() < 0.38
                if NEWDEPOT_ON and rows is PLOTS_YS and x1 > NEWDEPOT_X0:
                    continue
                if HQ_ON and x0 >= HQ_ZONE[0] - 0.5 and x1 <= HQ_ZONE[1] + 5 and y0 < HQ_ZONE[3] - 0.5:
                    continue
                mat = M["stubble"] if harvested else M["paddy"]
                a = Acc(f"plot_{x0}_{y0}", mat, "Terrain")
                a.box(x0 + 0.28, x1 - 0.28, y0 + 0.28, y1 - 0.28, -0.30, -0.185)
                a.build()
                if harvested:
                    HARVESTED.append((x0 + 0.28, x1 - 0.28, y0 + 0.28, y1 - 0.28))
    for rows in (PLOTS_YS, PLOTS_YN):
        ylo, yhi = min(min(r) for r in rows), max(max(r) for r in rows)
        _south = NEWDEPOT_ON and rows is PLOTS_YS
        for (x0, x1) in PLOTS_X:
            if _south and x1 > NEWDEPOT_X0:
                continue
            ylo2 = HQ_ZONE[3] if (HQ_ON and x0 >= HQ_ZONE[0] - 0.5 and ylo < HQ_ZONE[3]) else ylo
            lev.box(x0 - 0.27, x0 + 0.27, ylo2, yhi, -0.30, 0.04)
        ylo2 = HQ_ZONE[3] if (HQ_ON and ylo < HQ_ZONE[3]) else ylo
        if not _south:
            lev.box(PLOTS_X[-1][1] - 0.27, PLOTS_X[-1][1] + 0.27, ylo2, yhi, -0.30, 0.04)
        for (ya, yb) in rows:
            for yy in (ya, yb):
                xe = PLOTS_X[-1][1]
                if HQ_ON and yy < HQ_ZONE[3] - 0.5 and yy > HQ_ZONE[2] - 3:
                    xe = HQ_ZONE[0]
                if _south:
                    xe = NEWDEPOT_X0
                lev.box(PLOTS_X[0][0], xe, yy - 0.27, yy + 0.27, -0.30, 0.04)
    lev.build()


# ------------------------------------------------------------------ yard tracks (1-4) with turnout curves
import trackkit
from trackkit import smooth_x, seg_line, seg_arc, join

YARD_PATHS = {}


def build_tracks(cam):
    """Main line (T1), loop (T2), passing/siding (T3) and freight siding (T4) with S-curve connections."""
    P1 = smooth_x([(-140, T1), (140, T1)], -140, 140)
    P2 = smooth_x([(-140, T1), (-112, T1), (-80, T2), (88, T2), (122, T1), (140, T1)], -140, 140)
    P3 = smooth_x([(-72, T2), (-42, T3), (60, T3), (88, T2)], -72, 88)
    P4 = smooth_x([(-38, T3), (-6, T4), (54, T4)], -38, 54)
    P5 = smooth_x([(-2, T4), (24, T5), (68, T5)], -2, 68)         # D10: T4 から分岐する第5線
    P6 = smooth_x([(24, T5), (46, T6), (78, T6)], 24, 78)         # 第5線から分岐する第6線
    YARD_PATHS.update({"T1": P1, "T2": P2, "T3": P3, "T4": P4, "T5": P5, "T6": P6})
    for nm, P in YARD_PATHS.items():
        trackkit.build_track(nm, P, cam=cam, pebble_radius=44.0)
    trackkit.buffer_stop(54.5, T4, 0)
    if not NEWDEPOT_ON:
        trackkit.buffer_stop(68.5, T5, 0)
    if not NEWDEPOT_ON:
        trackkit.buffer_stop(78.5, T6, 0)
    return YARD_PATHS


# ------------------------------------------------------------------ platform
def build_platform():
    z_top = Z_PLAT
    ye, yw = Y_EDGE, Y_WALL
    body = Acc("platform_body", M["stone"], "Platform", bevel=0.01)
    body.box(PX0, PX1, ye, yw, -0.25, z_top - 0.05)
    body.build()
    # gravel/ash surface, inset slightly so the stone rim shows
    top = Acc("platform_surface", M["plat_top"], "Platform")
    top.box(PX0 + 0.04, PX1 - 0.04, ye + 0.62, yw - 0.04, z_top - 0.07, z_top - 0.035)
    top.build()
    # concrete coping along the edge
    cope = Acc("platform_coping", M["concrete"], "Platform", bevel=0.012)
    cope.box(PX0, PX1, ye - 0.02, ye + 0.62, z_top - 0.12, z_top)
    cope.build()
    line = Acc("platform_whiteline", M["white_line"], "Platform", closed=False)
    line.box(PX0 + 0.1, PX1 - 0.1, ye + 0.40, ye + 0.50, z_top, z_top + 0.004)
    line.build()
    # end ramps (gravel)
    for sgn, xe in ((1, PX1), (-1, PX0)):
        r = Acc("ramp", M["plat_top"], "Platform", closed=True)
        prof = [(xe, -0.25), (xe, z_top - 0.035), (xe + sgn * 5.5, 0.0), (xe + sgn * 5.5, -0.25)]
        r.extrude_y(prof, ye, yw)
        r.build()
    # old wooden fence along the back (north) edge, except in front of the building
    fence_ranges = [(PX0 + 0.1, SX0 - 0.6), (SX1 + 0.6, PX1 - 0.1)]
    f = Acc("platform_fence", M["wood"], "Platform", bevel=0.006)
    rng = random.Random(6)
    for (a, b) in fence_ranges:
        n = int((b - a) / 2.0) + 1
        for i in range(n + 1):
            x = a + (b - a) * i / n
            lean = rng.uniform(-0.03, 0.03)
            f.sbox((x, yw - 0.12, z_top - 0.1), (x + lean, yw - 0.12, z_top + 1.1), 0.12, 0.12)
        for zr in (z_top + 0.5, z_top + 0.95):
            f.sbox((a, yw - 0.12, zr), (b, yw - 0.12, zr + rng.uniform(-0.02, 0.02)), 0.05, 0.1, up=(0, 1, 0))
    f.build()


def build_island():
    """Island platform between T2 and T3 (reached by the board crossing), low gravel platform with stone rim."""
    x0, x1, y0, y1 = ISLAND
    z_top = Z_PLAT
    body = Acc("island_body", M["stone"], "Platform", bevel=0.01)
    body.box(x0, x1, y0, y1, -0.25, z_top - 0.05)
    body.build()
    top = Acc("island_surface", M["plat_top"], "Platform")
    top.box(x0 + 0.04, x1 - 0.04, y0 + 0.62, y1 - 0.62, z_top - 0.07, z_top - 0.035)
    top.build()
    cope = Acc("island_coping", M["concrete"], "Platform", bevel=0.012)
    cope.box(x0, x1, y0 - 0.02, y0 + 0.62, z_top - 0.12, z_top)
    cope.box(x0, x1, y1 - 0.62, y1 + 0.02, z_top - 0.12, z_top)
    cope.build()
    line = Acc("island_lines", M["white_line"], "Platform", closed=False)
    line.box(x0 + 0.1, x1 - 0.1, y0 + 0.40, y0 + 0.50, z_top, z_top + 0.004)
    line.box(x0 + 0.1, x1 - 0.1, y1 - 0.50, y1 - 0.40, z_top, z_top + 0.004)
    line.build()
    for sgn, xe in ((1, x1), (-1, x0)):
        r = Acc("island_ramp", M["plat_top"], "Platform", closed=True)
        r.extrude_y([(xe, -0.25), (xe, z_top - 0.035), (xe + sgn * 5.0, 0.0), (xe + sgn * 5.0, -0.25)], y0, y1)
        r.build()


def build_yard_crossing():
    """Board crossing for passengers (kounai-fumikiri) from the station platform to the island."""
    xc0, xc1 = -1.45, -0.45
    pl = Acc("yard_crossing_boards", M["wood_dark"], "Track", bevel=0.01)
    for T in (T1, T2):
        pl.box(xc0, xc1, T - 1.0, T + 1.0, Z_SLEEP + 0.004, Z_RAIL - 0.022)
    pl.box(xc0, xc1, T2 + 1.0, T1 - 1.0, Z_SLEEP - 0.01, Z_SLEEP + 0.03)      # path between the tracks
    pl.build()
    # ramps from the platforms down to rail level
    for y_top, y_low, sg in ((Y_EDGE, T1 + 1.0, 1), (ISLAND[3], T2 - 1.0, -1)):
        r = Acc("crossing_ramp", M["wood_dark"], "Track", closed=True)
        r.extrude_x([(y_top, Z_PLAT - 0.02), (y_top + 0.0, Z_PLAT - 0.06), (y_low, Z_RAIL - 0.05), (y_low, Z_RAIL - 0.022)], xc0, xc1)
        r.build()
    # warning plates on posts
    for (x, y, rot) in ((-1.95, T1 + 1.6, 0), (0.05, T2 - 1.5, 180)):
        p = Acc("fumikiri_post", M["wood_dark"], "Props", bevel=0.005)
        p.box(x - 0.05, x + 0.05, y - 0.05, y + 0.05, 0.0, 1.5)
        p.build()


# ------------------------------------------------------------------ roads (dirt)
def densify(pts, step=1.0):
    pts = np.asarray(pts, float)
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.linalg.norm(b - a) / step))
        for k in range(1, n + 1):
            out.append(a + (b - a) * k / n)
    return np.array(out)


def ribbon(name, pts, width, mat, z0=0.016, nacross=15, z_func=None, rut=True, skirt=0.0, col="Roads"):
    P = densify(pts, 1.0)
    N = len(P)
    tang = np.gradient(P, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9
    left = np.stack([-tang[:, 1], tang[:, 0]], -1)
    ts = np.linspace(-1, 1, nacross)
    rng = np.random.default_rng(abs(hash(name)) % (2 ** 32))
    jit = rng.normal(0, 0.06, (N,))
    V = np.zeros((N, nacross, 3), np.float32)
    C = np.zeros((N, nacross, 4), np.float32)
    s_acc = np.cumsum(np.r_[0, np.linalg.norm(np.diff(P, axis=0), axis=1)])
    for j, t in enumerate(ts):
        off = t * width / 2
        edge = np.abs(t) > 0.85
        wob = np.array([mn.noise(Vector((s * 0.12, j * 0.5, 3.1))) for s in s_acc]) * (0.35 if abs(t) == 1 else 0.12)
        xy = P + left * (off + wob * edge * 1.0 + jit * (0.5 if edge else 0.0))[:, None]
        z = np.full(N, z0) + (-0.035 * t * t)
        if z_func is not None:
            z = np.array([z_func(x, y) for x, y in xy]) + (-0.035 * t * t)
        if rut:
            d = (np.abs(t) - 0.33)
            z -= 0.045 * np.exp(-(d / 0.075) ** 2)
            C[:, j, 0] = np.exp(-(d / 0.11) ** 2) * (0.75 + 0.25 * np.array([mn.noise(Vector((s * 0.2, 0, j))) for s in s_acc]))
            C[:, j, 1] = np.exp(-(t / 0.19) ** 2) * (0.6 + 0.4 * np.array([mn.noise(Vector((s * 0.15, 5, 0))) for s in s_acc]))
        # edges blend into the meadow
        C[:, j, 1] = np.maximum(C[:, j, 1], ss(0.78, 1.0, abs(t)) * 0.9)
        C[:, j, 3] = 1.0
        V[:, j, 0], V[:, j, 1], V[:, j, 2] = xy[:, 0], xy[:, 1], z
    idx = np.arange(N * nacross).reshape(N, nacross)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    T = np.concatenate([np.stack([a, c, b], -1).reshape(-1, 3), np.stack([a, d, c], -1).reshape(-1, 3)])
    V = V.reshape(-1, 3)
    C = C.reshape(-1, 4)
    if skirt > 0:
        sv = [V]
        sc = [C]
        base = len(V)
        for j in (0, nacross - 1):
            col_idx = idx[:, j]
            low = V[col_idx].copy()
            low[:, 2] = -skirt
            sv.append(low)
            sc.append(C[col_idx])
        V = np.concatenate(sv)
        C = np.concatenate(sc)
        for k, j in enumerate((0, nacross - 1)):
            top = idx[:, j]
            lo = base + k * N + np.arange(N)
            q = np.stack([top[:-1], top[1:], lo[1:], lo[:-1]], -1)
            T = np.concatenate([T, q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
    return np_mesh(name, V, T, mat, col, colors=C, smooth=True)


def apron(name, cx, cy, rx, ry, mat, n=8.0, noise_amp=0.07, z0=0.014, col="Roads"):
    """Irregular rounded-rectangle patch of dirt (station forecourt)."""
    rings, seg = 7, 72
    rng = np.random.default_rng(5)
    V, C = [(cx, cy, z0)], [(0.0, 0.0, 0, 1)]
    for k in range(1, rings + 1):
        r = k / rings
        for i in range(seg):
            th = 2 * math.pi * i / seg
            ct, st = math.cos(th), math.sin(th)
            ex = np.sign(ct) * abs(ct) ** (2.0 / n)
            ey = np.sign(st) * abs(st) ** (2.0 / n)
            w = 1.0 + noise_amp * mn.noise(Vector((math.cos(th) * 2.0, math.sin(th) * 2.0, 1.3))) * 2.0
            x = cx + rx * ex * r * (w if k == rings else 1.0)
            y = cy + ry * ey * r * (w if k == rings else 1.0)
            gm = float(ss(0.62, 1.0, r)) * (0.65 + 0.35 * mn.noise(Vector((x * 0.25, y * 0.25, 7.0))))
            rt = max(0.0, mn.noise(Vector((x * 0.9, y * 0.12, 2.0)))) * 0.7
            V.append((x, y, z0 + 0.02 * (1 - r) - 0.01 * rt))
            C.append((rt, gm, 0, 1))
    T = []
    for i in range(seg):
        T.append((0, 1 + i, 1 + (i + 1) % seg))
    for k in range(1, rings):
        for i in range(seg):
            a = 1 + (k - 1) * seg + i
            b = 1 + (k - 1) * seg + (i + 1) % seg
            c = 1 + k * seg + i
            d = 1 + k * seg + (i + 1) % seg
            T.append((a, c, b))
            T.append((b, c, d))
    return np_mesh(name, np.array(V), np.array(T), mat, col, colors=np.array(C), smooth=True)


def xing_z(x, y):
    """Crossing road height: flat over all yard tracks, ramping down to the meadow on both sides."""
    t = float(ss(2.6, 6.5, y)) if y > -8 else float(ss(-20.0, -24.5, y))
    return 0.20 * (1.0 - t) + 0.016 * t


def build_roads():
    # forecourt road (east-west) meets the crossing road at X_C
    ribbon("road_forecourt", [(-110, ROAD_Y), (-40, ROAD_Y + 0.6), (-10, ROAD_Y), (X_C, ROAD_Y)], 4.6, M["road"])
    # crossing road (north-south)
    ribbon("road_crossing", [(X_C, -124), (X_C, -50), (X_C, -24), (X_C, -8), (X_C, 7), (X_C, 40), (X_C, 100)], 4.4, M["road"],
           z_func=xing_z, skirt=0.45)
    apron("forecourt", -9.0, 12.5, 18.0, 4.9, M["road"])
    apron("warehouse_yard", 17.0, 9.0, 9.0, 4.0, M["road"], noise_amp=0.1)
    # path from the platform ramps
    ribbon("path_east", [(PX1 + 5.0, 3.0), (PX1 + 12, 6.5), (30.5, 11.0), (30.5, ROAD_Y)], 1.6, M["road"], rut=False)


def build_crossing_deck():
    """Plank deck between / beside the rails at the unguarded road crossing (all four tracks)."""
    d = Acc("crossing_planks", M["wood_dark"], "Track", bevel=0.01)
    for T in TRACK_YS:
        x = X_C - 2.0
        while x < X_C + 2.0:
            d.box(x, x + 0.19, T - 1.75, T + 1.75, Z_SLEEP + 0.004, Z_RAIL - 0.028)
            x += 0.2
    d.build()
