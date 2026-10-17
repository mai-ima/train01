"""Generic railway track builder: sweeps ballast, sleepers, rails and fittings along any polyline."""
from common import *

RAIL_PROFILE = [(-0.0525, 0), (0.0525, 0), (0.0525, 0.010), (0.007, 0.025), (0.007, 0.082), (0.0315, 0.088),
                (0.0315, 0.122), (-0.0315, 0.122), (-0.0315, 0.088), (-0.007, 0.082), (-0.007, 0.025),
                (-0.0525, 0.010)]
Z_RAILBASE = Z_RAIL - 0.122
BALLAST_PROFILE = [(-3.1, -0.25), (-1.95, Z_BAL), (1.95, Z_BAL), (3.1, -0.25)]
TRACKS = {}          # name -> dense (N,2) centre line (for placing vehicles / buffer stops)


# ------------------------------------------------------------------ polyline building blocks
def seg_line(p0, p1, step=1.0):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    n = max(2, int(np.linalg.norm(p1 - p0) / step) + 1)
    return np.linspace(p0, p1, n)


def seg_arc(c, r, a0, a1, step=0.8):
    """Arc about centre c, radius r, from angle a0 to a1 (degrees, CCW positive)."""
    n = max(3, int(abs(math.radians(a1 - a0)) * r / step) + 1)
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)], -1)


def join(*parts):
    out = [parts[0]]
    for p in parts[1:]:
        out.append(p[1:] if np.linalg.norm(p[0] - out[-1][-1]) < 0.05 else p)
    return np.concatenate(out)


def smooth_x(knots, x0, x1, step=1.0):
    """y(x) with smoothstep transitions between consecutive knots [(x, y), ...]."""
    xs = np.arange(x0, x1 + 1e-6, step)
    ys = np.zeros_like(xs)
    kx = [k[0] for k in knots]
    ky = [k[1] for k in knots]
    for i, x in enumerate(xs):
        if x <= kx[0]:
            ys[i] = ky[0]
        elif x >= kx[-1]:
            ys[i] = ky[-1]
        else:
            j = np.searchsorted(kx, x) - 1
            t = (x - kx[j]) / (kx[j + 1] - kx[j])
            t = t * t * (3 - 2 * t)
            ys[i] = ky[j] + (ky[j + 1] - ky[j]) * t
    return np.stack([xs, ys], -1)


def resample(P, step=1.0):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    s = np.arange(0, d[-1], step)
    s = np.append(s, d[-1])
    return np.stack([np.interp(s, d, P[:, 0]), np.interp(s, d, P[:, 1])], -1), s


def frames(P):
    t = np.gradient(P, axis=0)
    t /= (np.linalg.norm(t, axis=1, keepdims=True) + 1e-9)
    n = np.stack([-t[:, 1], t[:, 0]], -1)
    return t, n


def at_s(P, s_query):
    """Point + heading at arc-length positions."""
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    x = np.interp(s_query, d, P[:, 0])
    y = np.interp(s_query, d, P[:, 1])
    t, _ = frames(P)
    tx = np.interp(s_query, d, t[:, 0])
    ty = np.interp(s_query, d, t[:, 1])
    return np.stack([x, y], -1), np.arctan2(ty, tx)


# ------------------------------------------------------------------ sweep builder
_MATS = {}


def _sweep_open(name, P, profile, mat, col="Track", flip=False, dz=None):
    t, n = frames(P)
    N, K = len(P), len(profile)
    V = np.zeros((N, K, 3))
    for k, (off, z) in enumerate(profile):
        V[:, k, 0] = P[:, 0] + n[:, 0] * off
        V[:, k, 1] = P[:, 1] + n[:, 1] * off
        V[:, k, 2] = z + (0 if dz is None else dz)
    idx = np.arange(N * K).reshape(N, K)
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
    if flip:
        T = T[:, ::-1]
    return np_mesh(name, V.reshape(-1, 3), T, mat, col, smooth=False)


def _sweep_closed(name, P, profile, offset, z0, mat, col="Track", dz=None):
    t, n = frames(P)
    N, K = len(P), len(profile)
    V = np.zeros((N, K, 3))
    for k, (yp, zp) in enumerate(profile):
        V[:, k, 0] = P[:, 0] + n[:, 0] * (offset + yp)
        V[:, k, 1] = P[:, 1] + n[:, 1] * (offset + yp)
        V[:, k, 2] = z0 + zp + (0 if dz is None else dz)
    idx = np.arange(N * K).reshape(N, K)
    tris = []
    for k in range(K):
        k2 = (k + 1) % K
        a, b, c, d = idx[:-1, k], idx[1:, k], idx[1:, k2], idx[:-1, k2]
        tris += [np.stack([a, b, c], -1), np.stack([a, c, d], -1)]
    cap0 = [(idx[0, 0], idx[0, i], idx[0, i + 1]) for i in range(1, K - 1)]
    cap1 = [(idx[-1, 0], idx[-1, i + 1], idx[-1, i]) for i in range(1, K - 1)]
    T = np.concatenate(tris + [np.array(cap0), np.array(cap1)])
    ob = np_mesh(name, V.reshape(-1, 3), T, mat, col, smooth=False)
    import bmesh as _bm
    bm = _bm.new()
    bm.from_mesh(ob.data)
    _bm.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def build_track(name, P, wooden=True, ballast=True, fittings=True, cam=None, pebble_radius=38.0, sleeper_step=0.60, zfun=None):
    """P: (N,2) centre line. Builds everything and registers it in TRACKS."""
    P, s = resample(P, 1.0)
    TRACKS[name] = P
    DZ = None if zfun is None else np.asarray(zfun(s), float)      # 高低差(m): 高架・地下・築堤用
    if ballast:
        # 根本対策(Q19): 分岐・渡り線でバラストが重なる所の上面が同一平面だと影レイが自己交差して真っ黒になる。
        # 線ごとに上面を 2mm ずつずらして同一平面を作らない(見た目には影響しない)。
        _bz = 0.002 * (len(TRACKS) % 6)
        _dzb = np.full(len(P), _bz) if DZ is None else np.asarray(DZ, float) + _bz
        _sweep_open(name + "_ballast", P, BALLAST_PROFILE, M["ballast"], dz=_dzb)
    # sleepers + fittings
    rng = random.Random(abs(hash(name)) % 100000)
    sl = Acc(name + "_sleepers", M["sleeper"], "Track", bevel=0.012)
    fit = Acc(name + "_fit", M["iron_rust"], "Track", closed=True)
    total = s[-1]
    ss_ = np.arange(0.3, total, sleeper_step)
    pos, ang = at_s(P, ss_)
    dzs = np.zeros(len(ss_)) if zfun is None else np.asarray(zfun(ss_), float)
    for (px, py), a, dzz in zip(pos, ang, dzs):
        jx, jy, rz, dz = rng.uniform(-0.025, 0.025), rng.uniform(-0.04, 0.04), rng.uniform(-0.022, 0.022), rng.uniform(-0.02, 0.0)
        # sleeper long axis is across the track: rotate box (x = along track, y = across)
        sl.boxc(px + jx * math.cos(a) - jy * math.sin(a), py + jx * math.sin(a) + jy * math.cos(a),
                (Z_SLEEP - 0.075) + dz + dzz, 0.15, 2.1, 0.15, a + rz)
        if fittings:
            for side in (-1, 1):
                ox = -math.sin(a) * side * RAIL_Y
                oy = math.cos(a) * side * RAIL_Y
                fit.boxc(px + ox, py + oy, Z_SLEEP + 0.006 + dzz, 0.09, 0.17, 0.011, a)
                for sy in (-1, 1):
                    qx = ox + (-math.sin(a)) * sy * 0.066
                    qy = oy + math.cos(a) * sy * 0.066
                    fit.boxc(px + qx, py + qy, Z_RAILBASE + 0.02 + dzz, 0.024, 0.024, 0.045, a)
    sl.build()
    fit.build()
    for side, nm in ((-1, "L"), (1, "R")):
        _sweep_closed(f"{name}_rail{nm}", P, RAIL_PROFILE, side * RAIL_Y, Z_RAILBASE, M["rail"], dz=DZ)
    # rail joints every 25 m
    jp = Acc(name + "_joints", M["iron_rust"], "Track", closed=True)
    sj = np.arange(12.0, total, 25.0)
    pos, ang = at_s(P, sj)
    dzj = np.zeros(len(sj)) if zfun is None else np.asarray(zfun(sj), float)
    for (px, py), a, dzz in zip(pos, ang, dzj):
        for side in (-1, 1):
            for fs in (-1, 1):
                off = side * RAIL_Y + fs * 0.0145
                jp.boxc(px - math.sin(a) * off, py + math.cos(a) * off, Z_RAILBASE + 0.061 + dzz, 0.60, 0.014, 0.062, a)
    jp.build()
    if cam is not None:
        scatter_pebbles(name, P, s, cam, pebble_radius)
    return P


def scatter_pebbles(name, P, s, cam, radius, density=75.0):
    rng = np.random.default_rng(abs(hash(name)) % (2 ** 31))
    d = np.linalg.norm(P - np.array(cam[:2])[None, :], axis=1)
    sel = np.where(d < radius)[0]
    if len(sel) < 2:
        return
    s0, s1 = s[sel[0]], s[sel[-1]]
    n = int((s1 - s0) * 4.0 * density)
    sq = rng.uniform(s0, s1, n)
    lat = rng.uniform(-2.35, 2.35, n)
    pos, ang = at_s(P, sq)
    x = pos[:, 0] - np.sin(ang) * lat
    y = pos[:, 1] + np.cos(ang) * lat
    z = Z_BAL + rng.uniform(-0.005, 0.012, n) - np.maximum(0.0, np.abs(lat) - 1.75) * 0.5
    # keep stones off sleeper tops and out of the rail seat
    along = (sq - 0.3) % 0.60
    keep = ~((np.abs(lat) < 1.05) & ((along < 0.075) | (along > 0.525)))
    keep &= ~(np.abs(np.abs(lat) - RAIL_Y) < 0.06)
    x, y, z, ang = x[keep], y[keep], z[keep], ang[keep]
    n = len(x)
    size = rng.uniform(0.020, 0.044, n)
    tmpl = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 0.8], [0, 0, -0.5]], dtype=np.float32)
    faces = np.array([[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]])
    jit = 1.0 + rng.uniform(-0.3, 0.3, (n, 6, 3)).astype(np.float32)
    squash = rng.uniform(0.6, 1.2, (n, 1, 3)).astype(np.float32)
    local = tmpl[None] * jit * squash * size[:, None, None]
    a2 = rng.uniform(0, 2 * np.pi, n)
    c, sn = np.cos(a2), np.sin(a2)
    R = np.zeros((n, 3, 3), np.float32)
    R[:, 0, 0], R[:, 0, 1], R[:, 1, 0], R[:, 1, 1], R[:, 2, 2] = c, -sn, sn, c, 1
    local = np.einsum('nij,nvj->nvi', R, local)
    V = (local + np.stack([x, y, z + size * 0.12], -1)[:, None, :]).reshape(-1, 3)
    T = (faces[None] + (np.arange(n) * 6)[:, None, None]).reshape(-1, 3)
    g = rng.uniform(0.07, 0.24, n)
    warm = rng.uniform(0.0, 0.035, n)
    cols = np.stack([g + warm, g + warm * 0.6, g, np.ones(n)], -1)
    cols = np.repeat(cols[:, None, :], 6, axis=1).reshape(-1, 4)
    np_mesh(name + "_stones", V, T, M["pebble"], "Track", colors=cols, smooth=False)


def buffer_stop(x, y, heading_deg):
    """Old timber-and-earth buffer stop at the end of a siding. heading = direction the track runs toward the stop."""
    a = math.radians(heading_deg)
    b = Acc("buffer_stop", M["wood_dark"], "Track", bevel=0.01)
    for off in (-0.55, 0.55):
        px = x - math.sin(a) * off
        py = y + math.cos(a) * off
        b.boxc(px, py, 0.55, 0.22, 0.22, 1.0, a)
    b.boxc(x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, 0.95, 0.25, 1.6, 0.18, a)
    b.build()
    e = Acc("buffer_earth", M["soil"], "Track")
    e.boxc(x + math.cos(a) * 1.2, y + math.sin(a) * 1.2, 0.2, 2.0, 2.6, 0.5, a)
    e.build()
