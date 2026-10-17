"""Vegetation + far landscape: grass tufts, susuki, rice, hasa racks, trees, bamboo, hills and far ground."""
from common import *
import lib
import core
from mathutils import noise as mn

RNG = np.random.default_rng(42)


def blades(P, h, w, ang, bend, cb, ct):
    """P (N,3) bases; h,w,ang,bend (N,) ; cb/ct (N,3) base/tip colours. 5 verts, 3 tris per blade."""
    N = len(P)
    d = np.stack([np.cos(ang), np.sin(ang), np.zeros(N)], 1)           # outward lean dir
    s = np.stack([-np.sin(ang), np.cos(ang), np.zeros(N)], 1)          # blade width dir
    z = np.array([0, 0, 1.0])
    bL, bR = P - s * (w / 2)[:, None], P + s * (w / 2)[:, None]
    mid = P + z * (h * 0.55)[:, None] + d * (bend * 0.25)[:, None]
    mL, mR = mid - s * (w * 0.32)[:, None], mid + s * (w * 0.32)[:, None]
    tip = P + z * (h * 0.93)[:, None] + d * bend[:, None]
    V = np.stack([bL, bR, mL, mR, tip], 1).reshape(-1, 3)
    cm = cb * 0.45 + ct * 0.55
    C = np.stack([cb, cb, cm, cm, ct], 1).reshape(-1, 3)
    C = np.concatenate([C, np.ones((len(C), 1))], 1)
    i = np.arange(N) * 5
    T = np.concatenate([np.stack([i, i + 1, i + 3], 1), np.stack([i, i + 3, i + 2], 1), np.stack([i + 2, i + 3, i + 4], 1)])
    return V, T, C


def tufts(xy, z, hmean, k=7, spread=0.12, wmean=0.035, cb=(0.07, 0.12, 0.025), ct=(0.27, 0.31, 0.08), jit=0.35, lean=0.35, seed=0):
    rng = np.random.default_rng(seed)
    n = len(xy)
    P = np.repeat(xy, k, axis=0)
    zz = np.repeat(np.broadcast_to(z, (n,)), k)
    r = rng.uniform(0, spread, len(P))
    a = rng.uniform(0, 2 * np.pi, len(P))
    P3 = np.stack([P[:, 0] + np.cos(a) * r, P[:, 1] + np.sin(a) * r, zz], 1)
    hh = np.repeat(np.broadcast_to(hmean, (n,)), k) * rng.uniform(0.6, 1.25, len(P))
    ang = np.arctan2(P3[:, 1] - np.repeat(xy[:, 1], k), P3[:, 0] - np.repeat(xy[:, 0], k)) + rng.normal(0, 0.8, len(P))
    bend = hh * lean * rng.uniform(0.3, 1.2, len(P))
    base = np.array(cb) * rng.uniform(0.7, 1.3, (len(P), 1))
    tip = np.array(ct) * rng.uniform(0.7, 1.35, (len(P), 3)) * (1 + jit * rng.uniform(-1, 1, (len(P), 1)))
    return blades(P3, hh, np.full(len(P), wmean) * rng.uniform(0.8, 1.3, len(P)), ang, bend, base, tip)


def join(parts):
    Vs, Ts, Cs, off = [], [], [], 0
    for V, T, C in parts:
        Vs.append(V)
        Ts.append(T + off)
        Cs.append(C)
        off += len(V)
    return np.concatenate(Vs), np.concatenate(Ts), np.concatenate(Cs)


def emit(name, V, T, C, mat, col="Vegetation"):
    if len(V) == 0:
        return None
    return np_mesh(name, V, T, mat, col, colors=C, smooth=False)


# ------------------------------------------------------------------ exclusion zones
TREE_EXCL = []       # [(x0, x1, y0, y1)] 樹木を植えない矩形(幹の中心が入る樹は作らない。D9c 西棟など新築の建物が登録)
EXTRA_EXCL = []      # [(x0, x1, y0, y1)] 草を生やさない追加の矩形(newdepot が登録)

def inside_rect(P, x0, x1, y0, y1):
    return (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > y0) & (P[:, 1] < y1)


def free_mask(P):
    x, y = P[:, 0], P[:, 1]
    bad = inside_rect(P, -300, 300, -20.2, 3.6)                       # rail corridor (ballast, tracks)
    bad |= inside_rect(P, -19, 27.5, 1.0, 11.5)                       # platform + station + porch area
    bad |= inside_rect(P, -12, 33, -9.3, -2.9)
    bad |= ((x + 9.0) / 18.5) ** 2 + ((y - 12.5) / 5.4) ** 2 < 1      # forecourt apron
    bad |= ((x - 17.0) / 9.5) ** 2 + ((y - 9.0) / 4.5) ** 2 < 1       # yard by the goods shed
    bad |= inside_rect(P, 5, 21.5, 5, 13.5)
    bad |= (np.abs(y - ROAD_Y) < 2.5) & (x < X_C + 2.5)               # forecourt road
    bad |= np.abs(x - X_C) < 2.6                                      # crossing road
    bad |= (np.abs(x - 30.5) < 1.2) & (y > 2) & (y < 15)
    bad |= inside_rect(P, 29, 42, -2, 14) & (np.abs(x - 30.5) < 3) & (y < 7.5) & (y > 2)
    bad |= inside_rect(P, 39.5, 43.5, 2.5, 6.5)
    bad |= inside_rect(P, -38, 76, -112, -58)                         # depot yard (own surfaces)
    try:
        import props
        for (a, b, c, d) in props.FOOT:
            bad |= inside_rect(P, a, b, c, d)
    except Exception:
        pass
    try:
        import newdepot as _nd
        _nd.register_grass_exclusion()                                # 構築順に依存せず登録する(冪等)
    except ImportError:
        pass
    for (a, b, c, d) in EXTRA_EXCL:                                   # 新総合車両基地など、他モジュールが登録した除外矩形(D4/D5)
        bad |= inside_rect(P, a, b, c, d)
    bad |= (y < -125) | (y > 24.8)
    return ~bad


def build_grass(cam):
    cx, cy = cam[0], cam[1]
    parts_g, parts_s = [], []
    # --- general meadow (north strip, south strip beside the yard, road verges)
    N = 500000
    P = np.stack([RNG.uniform(-170, 170, N), RNG.uniform(-125, 24.8, N)], 1)
    dist = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
    keep = RNG.uniform(0, 1, N) < np.clip(1.15 - dist / 160.0, 0.06, 1.0)
    P = P[keep & free_mask(np.pad(P, ((0, 0), (0, 1))))]
    # density modulation by large-scale noise: patches of tall / short / bare
    nz = np.array([mn.noise(Vector((p[0] * 0.05, p[1] * 0.05, 1.7))) for p in P[::1]]) if len(P) < 60000 else \
        np.array([mn.noise(Vector((p[0] * 0.05, p[1] * 0.05, 1.7))) for p in P[::1]])
    sel = RNG.uniform(-0.4, 0.8, len(P)) < nz + 0.35
    P = P[sel]
    h = 0.20 + 0.28 * RNG.uniform(0, 1, len(P)) * (0.6 + 0.8 * np.abs(nz[sel]))
    parts_g.append(tufts(P, 0.0, h, k=6, spread=0.14, seed=1))
    # taller dry stems (susuki) on verges
    M2 = 14000
    Q = np.stack([RNG.uniform(-150, 150, M2), RNG.uniform(3, 24.5, M2)], 1)
    Q = Q[free_mask(np.pad(Q, ((0, 0), (0, 1))))]
    nzq = np.array([mn.noise(Vector((p[0] * 0.03, p[1] * 0.03, 9.0))) for p in Q])
    Q = Q[nzq > 0.12]
    dq = np.hypot(Q[:, 0] - cx, Q[:, 1] - cy)
    Q = Q[dq < 140]
    parts_s.append(tufts(Q, 0.0, RNG.uniform(1.0, 1.6, len(Q)), k=9, spread=0.2, wmean=0.03, cb=(0.10, 0.12, 0.04),
                         ct=(0.55, 0.50, 0.30), lean=0.45, seed=3, jit=0.4))
    # --- weeds in the ballast edges / along rails (sparse)
    W = np.stack([RNG.uniform(-140, 140, 40000), RNG.choice([-20.4, -19.8, 3.4, 4.0, -9.7, -1.4], 40000) + RNG.uniform(-0.5, 0.5, 40000)], 1)
    dW = np.hypot(W[:, 0] - cx, W[:, 1] - cy)
    W = W[(dW < 90) & (RNG.uniform(0, 1, len(W)) < 0.07)]
    W = W[~inside_rect(W, -19, 27.5, 1.0, 11.5) & ~(np.abs(W[:, 0] - X_C) < 2.8)]
    parts_g.append(tufts(W, 0.05, RNG.uniform(0.25, 0.5, len(W)), k=5, spread=0.1, seed=7, cb=(0.07, 0.12, 0.03), ct=(0.28, 0.32, 0.10)))
    V, T, C = join(parts_g)
    emit("grass_tufts", V, T, C, M["blade"])
    V, T, C = join(parts_s)
    emit("susuki", V, T, C, M["blade"])
    # --- levees: grass + susuki + higanbana
    xl, yl = [], []
    for rows in (core.PLOTS_YS, core.PLOTS_YN):
        ylo, yhi = min(min(r) for r in rows), max(max(r) for r in rows)
        xsl = [a for (a, b) in core.PLOTS_X] + [core.PLOTS_X[-1][1]]
        for xv in xsl:
            for yv in np.arange(ylo, yhi, 0.45):
                for sx in (-0.2, 0.2):
                    xl.append(xv + sx + RNG.normal(0, 0.1))
                    yl.append(yv + RNG.normal(0, 0.1))
        ys_all = sorted({v for (a, b) in rows for v in (a, b)})
        for yv in ys_all:
            for xv in np.arange(core.PLOTS_X[0][0], core.PLOTS_X[-1][1], 0.45):
                for sy in (-0.2, 0.2):
                    xl.append(xv + RNG.normal(0, 0.1))
                    yl.append(yv + sy + RNG.normal(0, 0.1))
    L = np.stack([xl, yl], 1)
    L = L[~(np.abs(L[:, 0] - X_C) < 2.4)]
    dL = np.hypot(L[:, 0] - cx, L[:, 1] - cy)
    L = L[(dL < 150) & (RNG.uniform(0, 1, len(L)) < np.clip(1.2 - dL / 150.0, 0.12, 1))]
    nzl = np.array([mn.noise(Vector((p[0] * 0.06, p[1] * 0.06, 3.0))) for p in L])
    parts = [tufts(L, 0.03, RNG.uniform(0.25, 0.45, len(L)), k=6, spread=0.12, seed=11)]
    S = L[nzl > 0.25]
    parts_sus = [tufts(S, 0.03, RNG.uniform(0.9, 1.5, len(S)), k=8, spread=0.18, wmean=0.03, cb=(0.10, 0.12, 0.04),
                       ct=(0.60, 0.52, 0.30), lean=0.5, seed=13)]
    V, T, C = join(parts)
    emit("levee_grass", V, T, C, M["blade"])
    V, T, C = join(parts_sus)
    emit("levee_susuki", V, T, C, M["blade"])
    # higanbana (red spider lily): thin stem + 6 curling red petals
    Hh = L[(nzl < -0.15) & (RNG.uniform(0, 1, len(L)) < 0.22)]
    if len(Hh):
        stems = tufts(Hh, 0.03, np.full(len(Hh), 0.45), k=1, spread=0.03, wmean=0.012, cb=(0.10, 0.18, 0.05), ct=(0.12, 0.22, 0.06), lean=0.05, seed=17)
        pet = []
        for j in range(6):
            Pp = np.stack([Hh[:, 0], Hh[:, 1], np.full(len(Hh), 0.03 + 0.43)], 1)
            ang = j * np.pi / 3 + RNG.uniform(0, 0.3, len(Hh))
            pet.append(blades(Pp, np.full(len(Hh), 0.2), np.full(len(Hh), 0.018), ang, np.full(len(Hh), 0.22),
                              np.tile((0.55, 0.02, 0.02), (len(Hh), 1)), np.tile((0.85, 0.04, 0.04), (len(Hh), 1))))
        V, T, C = join([stems] + pet)
        emit("higanbana", V, T, C, M["blade"])


# ------------------------------------------------------------------ rice + hasa racks
def build_rice(cam):
    cx, cy = cam[0], cam[1]
    harv = set((round(a, 2), round(b, 2), round(c, 2), round(d, 2)) for (a, b, c, d) in core.HARVESTED)
    parts = []
    for rows in (core.PLOTS_YS, core.PLOTS_YN):
        for (x0, x1) in core.PLOTS_X:
            for (ya, yb) in rows:
                y0, y1 = min(ya, yb), max(ya, yb)
                key = (round(x0 + 0.28, 2), round(x1 - 0.28, 2), round(y0 + 0.28, 2), round(y1 - 0.28, 2))
                if key in harv:
                    continue
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                d = math.hypot(mx - cx, my - cy)
                if d > 170:
                    continue
                area = (x1 - x0 - 0.8) * (y1 - y0 - 0.8)
                dens = 2.4 if d < 70 else 1.2 if d < 120 else 0.5
                n = int(area * dens)
                P = np.stack([RNG.uniform(x0 + 0.5, x1 - 0.5, n), RNG.uniform(y0 + 0.5, y1 - 0.5, n)], 1)
                gold = RNG.uniform(0, 1)       # per-plot ripeness
                cb = (0.10 + 0.12 * gold, 0.17 + 0.05 * gold, 0.03)
                ct = (0.20 + 0.42 * gold, 0.34 + 0.12 * gold, 0.06 + 0.04 * gold)
                parts.append(tufts(P, -0.19, np.full(n, 0.62 + 0.1 * RNG.uniform()), k=5, spread=0.12, wmean=0.03, cb=cb, ct=ct, lean=0.9, seed=int(abs(mx * 3 + my))))
    if parts:
        V, T, C = join(parts)
        emit("rice_clumps", V, T, C, M["blade"])


def build_hasa(cam):
    cx, cy = cam[0], cam[1]
    g = Acc("hasa_poles", lib.mat_wood("hasa_wood", (0.22, 0.14, 0.08), rough=0.8, along='Z', weather=0.7), "Vegetation", bevel=0.005)
    bundles = []
    for (x0, x1, y0, y1) in core.HARVESTED:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if math.hypot(mx - cx, my - cy) > 160:
            continue
        L = min(18.0, (x1 - x0) - 3)
        xs = mx - L / 2
        xe = mx + L / 2
        for yy in (my - 0.8, my + 0.8):
            for xx in np.linspace(xs, xe, int(L // 2.5) + 1):
                g.cyl((xx, yy, -0.2), (xx, yy, 1.85), 0.03, seg=6)
        # three horizontal bars on each side (hung with rice sheaves)
        for zz in (0.75, 1.20, 1.65):
            for yy in (my - 0.8, my + 0.8):
                g.cyl((xs, yy, zz), (xe, yy, zz), 0.018, seg=5)
                bundles.append((xs, xe, yy, zz))
        for xx in np.linspace(xs, xe, int(L // 2.5) + 1):
            g.cyl((xx, my - 0.8, 1.2), (xx, my + 0.8, 1.2), 0.016, seg=4) if False else None
    g.build()
    # sheaves as simple tapered quads hanging down
    Vl, Tl, Cl = [], [], []
    off = 0
    for (xs, xe, yy, zz) in bundles:
        n = int((xe - xs) / 0.16)
        for i in range(n):
            xc = xs + (i + 0.5) * (xe - xs) / n
            for side in (-1, 1):
                ycen = yy + side * 0.04
                w0, w1, hh = 0.11, 0.17, 0.52 * RNG.uniform(0.85, 1.1)
                top, bot = zz + 0.02, zz + 0.02 - hh
                V4 = [(xc - w0 / 2, ycen, top), (xc + w0 / 2, ycen, top), (xc + w1 / 2, ycen + side * 0.04, bot), (xc - w1 / 2, ycen + side * 0.04, bot)]
                Vl += V4
                col = (0.45 + RNG.uniform(-0.05, 0.05), 0.33, 0.07, 1.0)
                cdark = (0.30, 0.20, 0.04, 1.0)
                Cl += [col, col, cdark, cdark]
                Tl += [(off, off + 1, off + 2), (off, off + 2, off + 3), (off, off + 2, off + 1), (off, off + 3, off + 2)]
                off += 4
    if Vl:
        emit("hasa_sheaves", np.array(Vl), np.array(Tl), np.array(Cl), M["straw"])


# ------------------------------------------------------------------ trees
def blob(c, rad, rng, seg=16, rings=10, k=0.18):
    V, C = [], []
    for r in range(rings + 1):
        th = math.pi * r / rings
        for s in range(seg):
            ph = 2 * math.pi * s / seg
            d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
            n = mn.noise(d * 1.8 + Vector((c[0] * 0.3, c[1] * 0.3, c[2] * 0.3)))
            rr = rad * (1 + k * n)
            V.append((c[0] + d.x * rr * 1.0, c[1] + d.y * rr * 1.0, c[2] + d.z * rr * 0.8))
    return np.array(V), seg, rings


CARD_SCALE = 1.0
import os as _os
LIGHT = float(_os.environ.get('VEG_LIGHT', '1'))   # .blend軽量化(葉カード数の倍率)


def tree_canopy(name, centre, rad, col_a, col_b, rng, nblobs=6, cards=True, spread=0.55, flat=0.8):
    Vs, Ts, Cs, off = [], [], [], 0
    pts = []
    nr = np.random.default_rng(int(rng.random() * 1e6))
    for b in range(nblobs):
        a = rng.uniform(0, 2 * math.pi)
        rr = rad * rng.uniform(0.25, spread) if b else 0.0
        c = (centre[0] + math.cos(a) * rr, centre[1] + math.sin(a) * rr, centre[2] + rng.uniform(-0.2, 0.4) * rad * flat)
        br = (rad * rng.uniform(0.38, 0.6) if b else rad * 0.6)
        V, seg, rings = blob(c, br * 0.86, rng)
        n = len(V)
        for r in range(rings):
            for s in range(seg):
                a0, a1 = r * seg + s, r * seg + (s + 1) % seg
                b0, b1 = (r + 1) * seg + s, (r + 1) * seg + (s + 1) % seg
                Ts += [(off + a0, off + b0, off + a1), (off + a1, off + b0, off + b1)]
        t = rng.uniform(0, 1)
        shade = np.clip((V[:, 2] - centre[2]) / (rad * 1.2) * 0.5 + 0.5, 0, 1)[:, None]
        ca = np.array(col_a) * (1 - t * 0.3)
        cb = np.array(col_b)
        Cc = (ca[None, :] * (1 - shade) + cb[None, :] * shade) * 0.55
        Cc = Cc * nr.uniform(0.85, 1.15, (n, 1))
        Cs.append(np.concatenate([Cc, np.ones((n, 1))], 1))
        Vs.append(V)
        pts.append((c, br))
        off += n
    # leaf cards on the surface
    if cards:
        CV, CT, CC = [], [], []
        o2 = 0
        for (c, br) in pts:
            m = max(int(40 * LIGHT), int(480 * br * br * CARD_SCALE * LIGHT))
            for _ in range(m):
                d = nr.normal(size=3) * np.array([1, 1, 0.75])
                d /= np.linalg.norm(d) + 1e-9
                p = np.array(c) + d * br * nr.uniform(0.80, 1.18)
                t1 = np.cross(d, [0, 0, 1.0])
                if np.linalg.norm(t1) < 1e-3:
                    t1 = np.array([1.0, 0, 0])
                t1 /= np.linalg.norm(t1)
                t2 = np.cross(d, t1)
                a0 = nr.uniform(0, 6.28)
                u = t1 * math.cos(a0) + t2 * math.sin(a0)
                v = -t1 * math.sin(a0) + t2 * math.cos(a0)
                sz = nr.uniform(0.14, 0.30)
                q = [p - u * sz * 0.5, p + u * sz * 0.5, p + v * sz + d * 0.04]
                CV += q
                sh = nr.uniform(0.0, 1.0) * (0.4 + 0.6 * (d[2] * 0.5 + 0.5))
                cc = (np.array(col_a) * (1 - sh) + np.array(col_b) * sh) * nr.uniform(0.75, 1.3)
                CC += [list(cc) + [1.0]] * 3
                CT += [(o2, o2 + 1, o2 + 2), (o2, o2 + 2, o2 + 1)]
                o2 += 3
        V = np.concatenate(Vs + [np.array(CV)])
        T = np.concatenate([np.array(Ts), np.array(CT) + off])
        C = np.concatenate(Cs + [np.array(CC)])
    else:
        V, T, C = np.concatenate(Vs), np.array(Ts), np.concatenate(Cs)
    emit(name, V, T, C, M["leaf"], "Trees")


def trunk(name, x, y, h, r0, r1, branches=(), mat=None):
    g = Acc(name, mat or M["bark"], "Trees", smooth=False)
    g.cyl((x, y, -0.1), (x, y, h), r0, r1, seg=9)
    for (z0, dx, dy, z1, rr) in branches:
        g.cyl((x, y, z0), (x + dx, y + dy, z1), rr, rr * 0.5, seg=6)
    g.build()


def zelkova(x, y, h=11.0, rad=5.2, seed=0, col_a=(0.07, 0.15, 0.03), col_b=(0.22, 0.30, 0.06)):
    for (ex0, ex1, ey0, ey1) in TREE_EXCL:          # 新築の建物と樹冠が重なる樹は植えない(樹冠半径ぶん広げて判定)
        if ex0 - rad * 0.8 < x < ex1 + rad * 0.8 and ey0 - rad * 0.8 < y < ey1 + rad * 0.8:
            return
    rng = random.Random(seed)
    br = []
    for k in range(5):
        a = rng.uniform(0, 6.28)
        br.append((h * 0.5 + k * 0.5, math.cos(a) * rad * 0.5, math.sin(a) * rad * 0.5, h * 0.8 + k * 0.3, 0.17))
    trunk(f"zelkova_{seed}_trunk", x, y, h * 0.65, 0.42, 0.25, br)
    tree_canopy(f"zelkova_{seed}", (x, y, h * 0.85), rad, col_a, col_b, rng, nblobs=9, spread=1.0)


def persimmon(x, y, seed=0, h=5.2, rad=2.6):
    rng = random.Random(seed)
    br = []
    for k in range(6):
        a = rng.uniform(0, 6.28)
        br.append((h * 0.45 + k * 0.1, math.cos(a) * rad * 0.5, math.sin(a) * rad * 0.5, h * 0.8 + k * 0.25, 0.1))
    trunk(f"kaki_{seed}_trunk", x, y, h * 0.6, 0.2, 0.12, br)
    tree_canopy(f"kaki_{seed}", (x, y, h * 0.85), rad, (0.20, 0.26, 0.04), (0.55, 0.50, 0.08), rng, nblobs=6, spread=0.95)
    # orange fruit
    fr = Acc(f"kaki_{seed}_fruit", lib.mat_plain("kaki_fruit", (0.80, 0.22, 0.02), rough=0.35, spec=0.6), "Trees")
    for _ in range(70):
        a = rng.uniform(0, 6.28)
        rr = rad * math.sqrt(rng.uniform(0.1, 1.0)) * 0.9
        fr.sphere((x + math.cos(a) * rr, y + math.sin(a) * rr, h * 0.85 + rng.uniform(-0.9, 0.7)), (0.065, 0.065, 0.055), seg=7, rings=4)
    fr.build()


def sakura(x, y, seed=0, h=6.0, rad=3.2):
    rng = random.Random(seed)
    br = []
    for k in range(5):
        a = rng.uniform(0, 6.28)
        br.append((h * 0.35 + k * 0.3, math.cos(a) * rad * 0.6, math.sin(a) * rad * 0.6, h * 0.8 + k * 0.2, 0.13))
    trunk(f"sakura_{seed}_trunk", x, y, h * 0.55, 0.30, 0.18, br)
    tree_canopy(f"sakura_{seed}", (x, y, h * 0.85), rad, (0.20, 0.17, 0.03), (0.60, 0.30, 0.05), rng, nblobs=8, spread=1.0)


def sugi(x, y, h=14.0, r=2.0, seed=0):
    rng = np.random.default_rng(seed)
    g = Acc(f"sugi_{seed}_trunk", M["bark"], "Trees")
    g.cyl((x, y, -0.1), (x, y, h * 0.9), 0.28, 0.07, seg=8)
    g.build()
    Vs, Ts, Cs, off = [], [], [], 0
    tiers = 15
    for t in range(tiers):
        f = t / (tiers - 1)
        z0 = h * (0.16 + 0.8 * f)
        rad = r * (1.0 - 0.82 * f) * rng.uniform(0.85, 1.15)
        seg = 18
        ap = (x, y, z0 + 1.5 - 0.9 * f)
        V = [ap]
        for s in range(seg):
            a = 2 * math.pi * s / seg + rng.uniform(-0.1, 0.1)
            rr = rad * rng.uniform(0.55, 1.2)
            V.append((x + math.cos(a) * rr, y + math.sin(a) * rr, z0 - 0.4 + rng.uniform(-0.35, 0.3)))
        V.append((x, y, z0 - 0.6))
        n = len(V)
        for s in range(seg):
            a, b = 1 + s, 1 + (s + 1) % seg
            Ts += [(off, off + a, off + b), (off + n - 1, off + b, off + a)]
        V = np.array(V)
        cl = np.array([0.012, 0.035, 0.016]) * (1 + 0.5 * f)
        Cc = np.tile(cl, (n, 1)) * rng.uniform(0.8, 1.2, (n, 1))
        Cc[0] = cl * 1.4
        Vs.append(V)
        Cs.append(np.concatenate([Cc, np.ones((n, 1))], 1))
        off += n
    o = emit(f"sugi_{seed}", np.concatenate(Vs), np.array(Ts), np.concatenate(Cs), M["leaf"], "Trees")
    if o is not None:
        o.data.shade_smooth()


def bamboo_grove(x0, x1, y0, y1, n=120, seed=1):
    rng = random.Random(seed)
    g = Acc("bamboo_culms", lib.mat_plain("bamboo", (0.20, 0.30, 0.08), rough=0.45, spec=0.4), "Trees")
    nodes = Acc("bamboo_nodes", lib.mat_plain("bamboo_n", (0.32, 0.36, 0.12), rough=0.5), "Trees")
    CV, CT, CC = [], [], []
    o = 0
    for i in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        h = rng.uniform(8, 12)
        lx, ly = rng.gauss(0, 0.012), rng.gauss(0, 0.012)
        prev = (x, y, 0.0)
        for k in range(1, 7):
            t = k / 6
            p = (x + lx * h * t * t * 4, y + ly * h * t * t * 4, h * t)
            g.cyl(prev, p, 0.04 * (1 - 0.4 * t), 0.04 * (1 - 0.4 * (t)), seg=5, caps=False)
            nodes.cyl((p[0], p[1], p[2] - 0.02), (p[0], p[1], p[2] + 0.02), 0.047 * (1 - 0.4 * t), seg=5, caps=False)
            prev = p
            if t > 0.5:
                for _ in range(3):
                    a = rng.uniform(0, 6.28)
                    c = np.array(p)
                    for l in range(6):
                        a2 = a + rng.uniform(-0.6, 0.6)
                        d = np.array([math.cos(a2), math.sin(a2), -0.3])
                        q0, q1 = c, c + d * rng.uniform(0.7, 1.1)
                        w = np.cross(d, [0, 0, 1.0])
                        w = w / (np.linalg.norm(w) + 1e-9) * 0.06
                        CV += [q0 - w, q0 + w, q1]
                        col = [0.10 + rng.uniform(0, 0.05), 0.24 + rng.uniform(0, 0.08), 0.04, 1.0]
                        CC += [col] * 3
                        CT += [(o, o + 1, o + 2), (o, o + 2, o + 1)]
                        o += 3
    g.build()
    nodes.build()
    emit("bamboo_leaves", np.array(CV), np.array(CT), np.array(CC), M["leaf"], "Trees")


def build_trees():
    zelkova(-27.5, 17.9, 11, 5.0, seed=1)
    zelkova(36.0, 22.5, 12, 5.6, seed=2)
    zelkova(-110.0, 26.0, 13, 6.0, seed=3, col_a=(0.15, 0.17, 0.03), col_b=(0.40, 0.33, 0.05))
    sakura(-17.5, 6.8, seed=1)
    sakura(29.0, 6.0, seed=2, h=5.6)
    persimmon(-64.5, 20.5, seed=1)
    persimmon(-55.8, 16.4, seed=2, h=4.8, rad=2.4)
    persimmon(43.0, 21.0, seed=3)
    persimmon(-42.0, 24.0, seed=4)
    for i, (sx, sy) in enumerate(((-77, 24.5), (-67, 24.5), (-78, 18.0), (-66, 24.8), (-74, 25.0), (-69, 19.5), (-76, 22.0))):
        if (sx, sy) in ((-69, 19.5),):
            continue
        sugi(sx, sy, h=15 + (i % 3) * 2, r=2.1, seed=i)
    for i, (sx, sy) in enumerate(((-104, 24.8), (-97, 25.0), (-106, 21.0), (50, 25), (56, 25.2), (60, 22.5))):
        sugi(sx, sy, h=13 + (i % 2) * 3, r=1.9, seed=20 + i)
    bamboo_grove(-118, -108, 17.5, 25.5, n=140)
    bamboo_grove(63, 72, 17.5, 25.2, n=90, seed=5)


# ------------------------------------------------------------------ landscape
def build_landscape(cam):
    hill = lib.mat_hill("hill_far", cam, far_dist=1300.0)
    # far ground ring to hide the world edge
    seg = 96
    rs = [590.0, 900.0, 1700.0, 3500.0, 7000.0]
    V, T = [], []
    for r in rs:
        for s in range(seg):
            a = 2 * math.pi * s / seg
            V.append((math.cos(a) * r, math.sin(a) * r, -0.25))
    for k in range(len(rs) - 1):
        for s in range(seg):
            a0, a1 = k * seg + s, k * seg + (s + 1) % seg
            b0, b1 = (k + 1) * seg + s, (k + 1) * seg + (s + 1) % seg
            T += [(a0, b0, a1), (a1, b0, b1)]
    np_mesh("far_ground", np.array(V), np.array(T), hill, "Terrain")
    # hill ring: polar grid with noise heights; leaves a notch to the south-east (open valley)
    nth, nr = 360, 24
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    rr = np.concatenate([np.linspace(620, 900, 6), np.linspace(960, 2400, nr - 6)])
    Vv = np.zeros((nr, nth, 3))
    for i, r in enumerate(rr):
        for j, t in enumerate(th):
            n1 = mn.noise(Vector((math.cos(t) * 1.7, math.sin(t) * 1.7, 0.3)))
            n2 = mn.noise(Vector((math.cos(t) * 5.0, math.sin(t) * 5.0, 2.0)))
            n3 = mn.noise(Vector((math.cos(t) * 14.0 + r * 0.004, math.sin(t) * 14.0, 5.0)))
            sector = 0.5 + 0.5 * math.sin(t - 0.4)                           # taller to the north-west
            Hpk = (45 + 70 * sector + 50 * n1 + 25 * n2 + 8 * n3)
            fr = np.clip((r - 650) / 500.0, 0, 1)
            fo = np.clip((2300 - r) / 900.0, 0, 1)
            h = max(0.0, Hpk) * (fr * fr * (3 - 2 * fr)) * fo
            Vv[i, j] = (math.cos(t) * r, math.sin(t) * r, -0.25 + h)
    idx = np.arange(nr * nth).reshape(nr, nth)
    a, b = idx[:-1, :], idx[:-1, np.r_[1:nth, 0]]
    c, d = idx[1:, np.r_[1:nth, 0]], idx[1:, :]
    Tt = np.concatenate([np.stack([a, d, b], -1).reshape(-1, 3), np.stack([b, d, c], -1).reshape(-1, 3)])
    np_mesh("hills", Vv.reshape(-1, 3), Tt, hill, "Terrain", smooth=True)
    # near satoyama knolls (forest) at 300-520 m, north / west
    near = lib.mat_hill("hill_near", cam, far_dist=900.0)
    for k, (cx, cy, rx, ry, hh) in enumerate(((-250, 330, 180, 120, 55), (-60, 420, 220, 110, 70), (230, 380, 160, 100, 45),
                                                (-420, 120, 110, 200, 60), (430, 200, 120, 140, 50), (-380, -260, 170, 120, 52))):
        nx, ny = 64, 64
        us = np.linspace(-1, 1, nx)
        vs = np.linspace(-1, 1, ny)
        U, Vg = np.meshgrid(us, vs)
        rho = np.sqrt(U * U + Vg * Vg)
        Z = np.array([[hh * max(0.0, 1 - rho[j, i] ** 2) ** 1.3 * (0.8 + 0.4 * mn.noise(Vector((cx * 0.01 + U[j, i] * 2, cy * 0.01 + Vg[j, i] * 2, 1.0)))) for i in range(nx)] for j in range(ny)])
        X = cx + U * rx
        Y = cy + Vg * ry
        Vk = np.stack([X, Y, Z - 0.25], -1).reshape(-1, 3)
        ii = np.arange(nx * ny).reshape(ny, nx)
        aa, bb, cc, dd = ii[:-1, :-1], ii[:-1, 1:], ii[1:, 1:], ii[1:, :-1]
        Tk = np.concatenate([np.stack([aa, bb, cc], -1).reshape(-1, 3), np.stack([aa, cc, dd], -1).reshape(-1, 3)])
        np_mesh(f"knoll_{k}", Vk, Tk, near, "Terrain", smooth=True)


def build_veg(cam_loc):
    build_landscape(cam_loc)
    build_grass(cam_loc)
    build_rice(cam_loc)
    build_hasa(cam_loc)
    build_trees()


def _scene_bvh(x0, x1, y0, y1):
    """可視メッシュ全部(三角形化・ワールド座標)から1つの BVH を作る。範囲 x0..x1,y0..y1 と重なるオブジェクトだけ。
    戻り値: (BVHTree, 三角形→オブジェクト番号の配列, オブジェクト名リスト)。失敗時は None(呼び出し側で従来方式にフォールバック)。"""
    import bpy
    from mathutils.bvhtree import BVHTree
    try:
        bpy.context.view_layer.update()
        V, T, own, names, off = [], [], [], [], 0
        for o in bpy.context.scene.objects:
            if o.type != 'MESH' or o.hide_viewport or o.hide_render:
                continue
            me = o.data
            if not len(me.polygons):
                continue
            n = len(me.vertices)
            co = np.empty(n * 3, np.float32)
            me.vertices.foreach_get('co', co)
            co = co.reshape(-1, 3).astype(np.float64)
            M = np.array(o.matrix_world, dtype=np.float64)
            co = co @ M[:3, :3].T + M[:3, 3]
            if co[:, 0].max() < x0 or co[:, 0].min() > x1 or co[:, 1].max() < y0 or co[:, 1].min() > y1:
                continue
            me.calc_loop_triangles()
            nt = len(me.loop_triangles)
            if not nt:
                continue
            tr = np.empty(nt * 3, np.int32)
            me.loop_triangles.foreach_get('vertices', tr)
            V.append(co); T.append(tr.reshape(-1, 3) + off); own.append(np.full(nt, len(names), np.int32)); names.append(o.name)
            off += n
        Va, Ta, Oa = np.vstack(V), np.vstack(T), np.concatenate(own)
        tree = BVHTree.FromPolygons([tuple(p) for p in Va.tolist()], [tuple(t) for t in Ta.tolist()], all_triangles=True)
        return tree, Oa, names
    except Exception as e:
        print('scene_bvh failed -> slow path', e)
        return None


# ------------------------------------------------------------------ zone grass (全駅ゾーン共通)
GROUND_RE = None


def zone_grass(cam, x0=-110, x1=110, y0=-70, y1=95, step=0.5, light=None):
    """下向きレイで『地面にそのまま当たる点』だけに草むら/ススキ/線路際の雑草を置く(建物・線路・道路・ホーム・木には置かない)。"""
    import re
    import bpy
    global GROUND_RE
    if GROUND_RE is None:
        GROUND_RE = re.compile(r"^(kit_ground|k2_ground|hills|knoll|far_ground|k2_hill)", re.I)
    light = LIGHT if light is None else light
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    gx = np.arange(x0, x1, step)
    gy = np.arange(y0, y1, step)
    rng = np.random.default_rng(11)
    pts, edge = [], []
    from mathutils import Vector as _V
    D = _V((0, 0, -1))
    free = np.zeros((len(gx), len(gy)), dtype=bool)
    zz = np.zeros((len(gx), len(gy)))
    _bvh = _scene_bvh(x0 - 2, x1 + 2, y0 - 2, y1 + 2) if os.environ.get('ZGRASS_SLOW') != '1' else None
    for i, x in enumerate(gx):
        for j, y in enumerate(gy):
            xx, yy = x + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3)
            if _bvh is not None:                      # 高速経路: 事前に作った BVH を引く(従来は scene.ray_cast を14万回 → 約175秒)
                tree, own, names = _bvh
                loc, n, fidx, _d = tree.ray_cast(_V((xx, yy, 80.0)), D, 200.0)
                if loc is not None and n[2] > 0.8 and GROUND_RE.match(names[own[fidx]]):
                    free[i, j] = True
                    zz[i, j] = loc.z
                    pts.append((xx, yy, loc.z))
                continue
            ok, loc, n, idx, ob, mat = sc.ray_cast(dg, _V((xx, yy, 80.0)), D, distance=200.0)
            if ok and GROUND_RE.match(ob.name) and n[2] > 0.8:
                free[i, j] = True
                zz[i, j] = loc.z
                pts.append((xx, yy, loc.z))
    P3 = np.array(pts)
    if len(P3) == 0:
        return 0
    # 構造物のそばほど草が高い(縁取り): 近傍に非空きセルがあるか
    pad = np.pad(~free, 2, constant_values=False)
    near = np.zeros_like(free)
    for di in range(-2, 3):
        for dj in range(-2, 3):
            near |= pad[2 + di:2 + di + free.shape[0], 2 + dj:2 + dj + free.shape[1]]
    ii = np.clip(((P3[:, 0] - x0) / step).astype(int), 0, len(gx) - 1)
    jj = np.clip(((P3[:, 1] - y0) / step).astype(int), 0, len(gy) - 1)
    isedge = near[ii, jj]
    cx, cy = cam[0], cam[1]
    dist = np.hypot(P3[:, 0] - cx, P3[:, 1] - cy)
    nz = np.array([mn.noise(Vector((p[0] * 0.05, p[1] * 0.05, 1.7))) for p in P3])
    pk = np.clip(1.1 - dist / 170.0, 0.15, 1.0) * np.where(isedge, 1.0, 0.75) * (0.55 + 0.6 * np.clip(nz + 0.4, 0, 1))
    sel = rng.uniform(0, 1, len(P3)) < pk * light
    Q = P3[sel]
    ne = isedge[sel]
    nzq = nz[sel]
    # 近景の密度補強(B10): カメラから15m以内は1点ごとに追加の草むらを微小ずらしで置く(疎で平板に見える問題の対策)
    near_m = np.hypot(Q[:, 0] - cx, Q[:, 1] - cy) < 15.0
    if near_m.any() and os.environ.get('NEAR_GRASS', '1') == '1':
        Qn = Q[near_m].copy()
        Qn[:, :2] += rng.uniform(-0.25, 0.25, (len(Qn), 2))
        Q = np.vstack([Q, Qn]); ne = np.concatenate([ne, ne[near_m]]); nzq = np.concatenate([nzq, nzq[near_m]])
    h = 0.14 + 0.30 * rng.uniform(0, 1, len(Q)) * (0.6 + 0.8 * np.abs(nzq)) + np.where(ne, 0.12, 0.0)
    cols = [dict(cb=(0.07, 0.12, 0.025), ct=(0.27, 0.31, 0.08)), dict(cb=(0.09, 0.13, 0.03), ct=(0.38, 0.36, 0.12))]
    _zt = globals().get('ZONE_TINT')
    if _zt:                                              # 駅ごとの草色味(kit2._apply_tint)。ベースは建物配置の後でも色は房の頂点色に乗る
        _tm = np.array([_zt[0], _zt[1], _zt[2]]) * _zt[3]
        cols = [dict(cb=tuple(np.array(c['cb']) * _tm), ct=tuple(np.array(c['ct']) * _tm)) for c in cols]
    for gi, kd in enumerate(cols):
        m = (np.arange(len(Q)) % 2) == gi
        if m.sum():
            Vv, Tt, Cc = tufts(Q[m][:, :2], Q[m][:, 2], h[m], k=5, spread=0.16, seed=21 + gi, **kd)
            emit(f"zgrass{gi}", Vv, Tt, Cc, M["blade"])
    # Q13: 近景の野花(白詰草・タンポポ調の黄/白の穂先)。均一な緑一色で平板に見える問題への対策
    if os.environ.get('WILDFLOWERS', '1') == '1':
        dq = np.hypot(Q[:, 0] - cx, Q[:, 1] - cy)
        fm = (dq < 24.0) & (rng.uniform(0, 1, len(Q)) < 0.16) & (~ne)
        for fi, (fb, ft) in enumerate([((0.10, 0.18, 0.04), (0.95, 0.88, 0.25)), ((0.10, 0.18, 0.04), (0.93, 0.93, 0.88)), ((0.10, 0.17, 0.05), (0.80, 0.55, 0.75))]):
            sel_f = fm & ((np.arange(len(Q)) % 3) == fi)
            if sel_f.any():
                Vv, Tt, Cc = tufts(Q[sel_f][:, :2], Q[sel_f][:, 2], rng.uniform(0.16, 0.26, int(sel_f.sum())), k=3, spread=0.07, wmean=0.016, cb=fb, ct=ft, lean=0.15, seed=51 + fi)
                emit(f"zflower{fi}", Vv, Tt, Cc, M["blade"])
    # 縁取りのススキ・背の高い草
    E_ = Q[ne & (nzq > 0.0)]
    if len(E_):
        Vv, Tt, Cc = tufts(E_[:, :2], E_[:, 2], rng.uniform(0.7, 1.3, len(E_)), k=7, spread=0.2, wmean=0.03, cb=(0.10, 0.12, 0.04),
                           ct=(0.55, 0.50, 0.30), lean=0.45, seed=33, jit=0.4)
        emit("zsusuki", Vv, Tt, Cc, M["blade"])
    return len(Q)
