"""The old unpainted wooden station building (Honamino), inspired by real rural wooden stations:
tiled gable roof with a monitor roof (koshi-yane), gabled entrance porch with a row of clerestory
windows, ticket window, wicket gate (ratchi), pot-belly stove, detached small canopy / toilet annex.
Original combination, fictional name.
"""
from common import *

WT = 0.12                 # wall thickness
Z0 = Z_PLAT               # wall base (top of stone plinth)
Z_BEAM = 3.70             # eave beam / wall top
RIDGE_Y = (Y_WALL + Y_BACK) / 2
PITCH = 0.5
OVER = 1.2                # eave overhang
GAB = 0.7                 # gable overhang
RIDGE_Z = Z_BEAM + 0.25 + (RIDGE_Y - Y_WALL) * PITCH
EAVE_FY = Y_WALL - OVER
EAVE_BY = Y_BACK + OVER
EAVE_Z = RIDGE_Z - (RIDGE_Y - EAVE_FY) * PITCH
XC = (SX0 + SX1) / 2

ROOF_V, ROOF_T = [], []


# ------------------------------------------------------------------ roof surface generator (real tile relief)
def roof_surface(R0, rdir, sdir, run, drop, u0, u1, tile_w=0.26, tile_l=0.19, ax=0.028, al=0.032, nx=9):
    """Wave/lap tiled slope. R0 = ridge point, rdir = unit ridge direction (xy), sdir = unit horizontal slope
    direction (xy), run = horizontal length, drop = vertical drop. u along ridge, v down the slope."""
    r3 = np.array([rdir[0], rdir[1], 0.0])
    L = math.hypot(run, drop)
    s3 = np.array([sdir[0] * run, sdir[1] * run, -drop]) / L
    n = np.cross(r3, s3)
    flip = n[2] < 0
    if flip:
        n = -n
    n = n / np.linalg.norm(n)
    us = np.arange(u0, u1, tile_w / nx)
    us = np.append(us, u1)
    vs, fh = [], []
    r = 0
    while True:
        done = False
        for f in (0, 0.25, 0.5, 0.75, 0.96):
            v = (r + f) * tile_l
            if v >= L:
                done = True
                break
            vs.append(v)
            fh.append(f)
        if done:
            break
        r += 1
    vs.append(L)
    fh.append(min(1.0, (L / tile_l) % 1.0))
    vs, fh = np.array(vs), np.array(fh)
    h = ax * 0.5 * (1 - np.cos(2 * np.pi * (us - u0) / tile_w))[None, :] + al * fh[:, None]
    P = (np.array(R0)[None, None, :] + r3[None, None, :] * us[None, :, None] +
         s3[None, None, :] * vs[:, None, None] + n[None, None, :] * h[:, :, None])
    nv, nu = P.shape[:2]
    idx = np.arange(nv * nu).reshape(nv, nu)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    if flip:
        T = np.concatenate([np.stack([a, c, b], -1).reshape(-1, 3), np.stack([a, d, c], -1).reshape(-1, 3)])
    else:
        T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
    off = sum(len(v) for v in ROOF_V)
    ROOF_V.append(P.reshape(-1, 3))
    ROOF_T.append(T + off)
    return n, s3, L


# ------------------------------------------------------------------ framed openings
def hole_wall(acc, axis, c0, c1, p0, p1, zb, zt, holes):
    """Wall along `axis` ('x' or 'y') spanning c0..c1 with thickness p0..p1 on the other axis, with rectangular holes
    [(h0,h1,z0,z1), ...] (sorted)."""
    def seg(a, b, z0, z1):
        if b - a < 1e-4 or z1 - z0 < 1e-4:
            return
        if axis == 'x':
            acc.box(a, b, p0, p1, z0, z1)
        else:
            acc.box(p0, p1, a, b, z0, z1)
    # 掃引: x の区切りごとに、その区間を覆う穴(複数階で縦に重なる穴を含む)を縦方向に避けて壁を張る
    xs = sorted({c0, c1} | {min(max(h, c0), c1) for hh in holes for h in hh[:2]})
    for xa, xb in zip(xs[:-1], xs[1:]):
        if xb - xa < 1e-4:
            continue
        xm = (xa + xb) / 2
        cover = sorted((z0, z1) for (h0, h1, z0, z1) in holes if h0 <= xm <= h1)
        z = zb
        for (z0, z1) in cover:
            if z0 > z:
                seg(xa, xb, z, min(z0, zt))
            z = max(z, z1)
        if z < zt:
            seg(xa, xb, z, zt)


def sash_window(fr, gl, ypos, out, x0, x1, z0, z1, nh=2, nv=3, opened=0.0):
    """Wooden two-leaf sliding window in a wall along X. ypos = outer face y, out = +1/-1 outward."""
    w, h = x1 - x0, z1 - z0
    yc = ypos - out * (WT / 2)
    d0, d1 = yc - 0.05, yc + 0.05
    t = 0.05
    fr.box(x0 - 0.04, x1 + 0.04, d0 + out * 0.0 - 0.0, d1 + out * 0.0, z1, z1 + 0.06)       # head
    fr.box(x0 - 0.04, x1 + 0.04, d0 - out * 0.0 - 0.0, d1 + 0.0, z0 - 0.06, z0)             # sill
    # protruding sill board outside
    ys0, ys1 = (ypos, ypos + out * 0.14)
    fr.box(x0 - 0.06, x1 + 0.06, min(ys0, ys1), max(ys0, ys1), z0 - 0.09, z0 - 0.04)
    fr.box(x0 - 0.04, x0, d0, d1, z0, z1)
    fr.box(x1, x1 + 0.04, d0, d1, z0, z1)
    leaf_w = w / 2 + 0.03
    for k in range(2):
        lx0 = x0 + (0 if k == 0 else w - leaf_w) + (opened if k == 1 else 0.0)
        lx1 = lx0 + leaf_w
        dy = yc + (-out if k == 0 else out) * 0.02
        a, b = dy - 0.018, dy + 0.018
        fr.box(lx0, lx0 + t, a, b, z0, z1)
        fr.box(lx1 - t, lx1, a, b, z0, z1)
        fr.box(lx0, lx1, a, b, z0, z0 + t)
        fr.box(lx0, lx1, a, b, z1 - t, z1)
        for i in range(1, nh):
            xx = lx0 + t + (leaf_w - 2 * t) * i / nh
            fr.box(xx - 0.008, xx + 0.008, dy - 0.01, dy + 0.01, z0 + t, z1 - t)
        for j in range(1, nv):
            zz = z0 + t + (h - 2 * t) * j / nv
            fr.box(lx0 + t, lx1 - t, dy - 0.01, dy + 0.01, zz - 0.008, zz + 0.008)
        gl.box(lx0 + t, lx1 - t, dy - 0.003, dy + 0.003, z0 + t, z1 - t)


def sash_window_y(fr, gl, xpos, out, y0, y1, z0, z1, nh=2, nv=3):
    """Same window, wall along Y (gable walls); xpos = outer face x."""
    w, h = y1 - y0, z1 - z0
    xc = xpos - out * (WT / 2)
    t = 0.05
    fr.box(xc - 0.05, xc + 0.05, y0 - 0.04, y1 + 0.04, z1, z1 + 0.06)
    fr.box(xc - 0.05, xc + 0.05, y0 - 0.04, y1 + 0.04, z0 - 0.06, z0)
    xs0, xs1 = (xpos, xpos + out * 0.14)
    fr.box(min(xs0, xs1), max(xs0, xs1), y0 - 0.06, y1 + 0.06, z0 - 0.09, z0 - 0.04)
    fr.box(xc - 0.05, xc + 0.05, y0 - 0.04, y0, z0, z1)
    fr.box(xc - 0.05, xc + 0.05, y1, y1 + 0.04, z0, z1)
    leaf_w = w / 2 + 0.03
    for k in range(2):
        ly0 = y0 + (0 if k == 0 else w - leaf_w)
        ly1 = ly0 + leaf_w
        dx = xc + (-out if k == 0 else out) * 0.02
        a, b = dx - 0.018, dx + 0.018
        fr.box(a, b, ly0, ly0 + t, z0, z1)
        fr.box(a, b, ly1 - t, ly1, z0, z1)
        fr.box(a, b, ly0, ly1, z0, z0 + t)
        fr.box(a, b, ly0, ly1, z1 - t, z1)
        for i in range(1, nh):
            yy = ly0 + t + (leaf_w - 2 * t) * i / nh
            fr.box(dx - 0.01, dx + 0.01, yy - 0.008, yy + 0.008, z0 + t, z1 - t)
        for j in range(1, nv):
            zz = z0 + t + (h - 2 * t) * j / nv
            fr.box(dx - 0.01, dx + 0.01, ly0 + t, ly1 - t, zz - 0.008, zz + 0.008)
        gl.box(dx - 0.003, dx + 0.003, ly0 + t, ly1 - t, z0 + t, z1 - t)


def sash_door(fr, gl, ypos, out, x0, x1, z0, z1, open_leaf=0.0):
    """Old wooden sliding glass door (lower solid panel, glazed upper part with muntins)."""
    w, h = x1 - x0, z1 - z0
    yc = ypos - out * (WT / 2)
    t = 0.07
    fr.box(x0 - 0.05, x1 + 0.05, yc - 0.06, yc + 0.06, z1, z1 + 0.10)
    fr.box(x0 - 0.05, x0, yc - 0.06, yc + 0.06, z0, z1)
    fr.box(x1, x1 + 0.05, yc - 0.06, yc + 0.06, z0, z1)
    fr.box(x0, x1, yc - 0.06, yc + 0.06, z0 - 0.0, z0 + 0.03)  # threshold
    leaf_w = w / 2 + 0.04
    for k in range(2):
        lx0 = x0 + (0 if k == 0 else w - leaf_w) + (open_leaf if k == 1 else 0.0)
        lx1 = lx0 + leaf_w
        dy = yc + (-out if k == 0 else out) * 0.025
        a, b = dy - 0.02, dy + 0.02
        fr.box(lx0, lx0 + t, a, b, z0, z1)
        fr.box(lx1 - t, lx1, a, b, z0, z1)
        fr.box(lx0, lx1, a, b, z1 - t, z1)
        fr.box(lx0, lx1, a, b, z0, z0 + 0.62)                       # solid lower panel
        fr.box(lx0, lx1, a, b, z0 + 0.62, z0 + 0.62 + t * 0.8)
        gz0, gz1 = z0 + 0.62 + t * 0.8, z1 - t
        nh, nv = 3, 4
        for i in range(1, nh):
            xx = lx0 + t + (leaf_w - 2 * t) * i / nh
            fr.box(xx - 0.01, xx + 0.01, dy - 0.012, dy + 0.012, gz0, gz1)
        for j in range(1, nv):
            zz = gz0 + (gz1 - gz0) * j / nv
            fr.box(lx0 + t, lx1 - t, dy - 0.012, dy + 0.012, zz - 0.01, zz + 0.01)
        gl.box(lx0 + t, lx1 - t, dy - 0.003, dy + 0.003, gz0, gz1)
        # pull handle
        hx = lx1 - t - 0.04 if k == 0 else lx0 + t + 0.04
        fr.box(hx - 0.015, hx + 0.015, dy - out * 0.045, dy + out * 0.0, z0 + 0.95, z0 + 1.25)


def image_on(name, img, face, pos, size, z, extra=0.012, kw=None, alpha=False):
    """Hang a sign on a wall. face: 'F' (front, -y), 'B' (back, +y), 'W' (west, -x), 'E' (east, +x).
    pos = x (for F/B) or y (for W/E) centre, z = centre height, size = (w, h)."""
    w, h = size
    if face == 'F':
        y = Y_WALL - extra
        c = [(pos - w / 2, y, z - h / 2), (pos + w / 2, y, z - h / 2), (pos + w / 2, y, z + h / 2), (pos - w / 2, y, z + h / 2)]
    elif face == 'B':
        y = Y_BACK + extra
        c = [(pos + w / 2, y, z - h / 2), (pos - w / 2, y, z - h / 2), (pos - w / 2, y, z + h / 2), (pos + w / 2, y, z + h / 2)]
    elif face == 'W':
        x = SX0 - extra
        c = [(x, pos + w / 2, z - h / 2), (x, pos - w / 2, z - h / 2), (x, pos - w / 2, z + h / 2), (x, pos + w / 2, z + h / 2)]
    else:
        x = SX1 + extra
        c = [(x, pos - w / 2, z - h / 2), (x, pos + w / 2, z - h / 2), (x, pos + w / 2, z + h / 2), (x, pos - w / 2, z + h / 2)]
    return image_plane(name, c, img, kw or {"rough": 0.35, "spec": 0.6}, col="Signs", alpha=alpha)


# ------------------------------------------------------------------ the building
def build_station():
    S = lambda n, m, **k: Acc(n, m, "Station", **k)
    walls = S("walls", M["wall"], bevel=0.006)
    frame = S("frames", M["wood"], bevel=0.004)
    dark = S("dark_wood", M["wood_dark"], bevel=0.004)
    glass = S("glass", M["glass"], closed=False)
    plinth = S("plinth", M["stone"], bevel=0.015)
    floor = S("floor", M["floor"])
    iron = S("iron", M["iron_black"], bevel=0.003, smooth=False)
    tile_cap = S("ridge_caps", M["roof"], smooth=True)
    redp = S("post_box", M["post_red"], smooth=True)
    conc = S("steps", M["concrete"], bevel=0.015)

    f_y0, f_y1 = Y_WALL, Y_WALL + WT
    b_y0, b_y1 = Y_BACK - WT, Y_BACK
    zf = Z_FLOOR

    # ---- stone plinth + steps
    plinth.box(SX0 - 0.08, SX1 + 0.08, Y_WALL - 0.02, Y_BACK + 0.08, -0.25, Z0)
    plinth.box(-8.7, -5.3, Y_BACK + 0.08, Y_BACK + 1.9, -0.25, 0.22 * 1)         # porch landing foundation
    for k in range(4):                                                            # porch steps
        top = zf - 0.225 * (k + 1) + 0.0
        conc.box(-8.6 + k * 0.0, -5.4, Y_BACK + 0.1 + 1.8 + k * 0.30 - 0.6, Y_BACK + 0.1 + 1.8 + (k + 1) * 0.30 - 0.6 + 0.0, -0.1, max(0.05, top))
    conc.box(-8.4, -6.4, Y_WALL - 0.45, Y_WALL, Z0 - 0.2, Z0 + 0.15)              # step from platform to gate

    # ---- openings (front / platform side)
    gate = (-8.4, -6.4)
    holes_f = [(-11.4, -10.2, zf + 1.0, zf + 2.0), (-9.85, -8.85, zf + 0.85, zf + 1.65),
               (gate[0], gate[1], zf, zf + 2.05), (-5.3, -3.9, zf + 1.0, zf + 2.0), (-3.5, -2.4, zf + 1.0, zf + 2.0)]
    hole_wall(walls, 'x', SX0, SX1, f_y0, f_y1, Z0, Z_BEAM, holes_f)
    # ---- back / forecourt side
    holes_b = [(-11.2, -9.9, zf + 1.0, zf + 2.0), (-8.0, -6.0, zf, zf + 2.05), (-4.2, -2.9, zf + 1.0, zf + 2.0)]
    hole_wall(walls, 'x', SX0, SX1, b_y0, b_y1, Z0, Z_BEAM, holes_b)
    # ---- gable end walls
    hole_wall(walls, 'y', Y_WALL, Y_BACK, SX0, SX0 + WT, Z0, Z_BEAM, [])
    hole_wall(walls, 'y', Y_WALL, Y_BACK, SX1 - WT, SX1, Z0, Z_BEAM, [(5.4, 6.6, zf + 1.0, zf + 2.0)])
    # gable triangles
    for (xa, xb) in ((SX0, SX0 + WT), (SX1 - WT, SX1)):
        walls.extrude_x([(Y_WALL, Z_BEAM), (Y_BACK, Z_BEAM), (RIDGE_Y, RIDGE_Z - 0.10)], xa, xb)

    # ---- windows / doors
    sash_window(frame, glass, Y_WALL, -1, -11.4, -10.2, zf + 1.0, zf + 2.0)
    sash_window(frame, glass, Y_WALL, -1, -5.3, -3.9, zf + 1.0, zf + 2.0)
    sash_window(frame, glass, Y_WALL, -1, -3.5, -2.4, zf + 1.0, zf + 2.0, opened=0.12)
    sash_window(frame, glass, Y_WALL, -1, -9.85, -8.85, zf + 0.85, zf + 1.65, nv=2, opened=0.28)   # ticket window
    frame.box(-10.05, -8.65, Y_WALL - 0.22, Y_WALL, zf + 0.78, zf + 0.84)                          # counter ledge
    sash_window(frame, glass, Y_BACK, 1, -11.2, -9.9, zf + 1.0, zf + 2.0)
    sash_window(frame, glass, Y_BACK, 1, -4.2, -2.9, zf + 1.0, zf + 2.0)
    sash_window_y(frame, glass, SX1, 1, 5.4, 6.6, zf + 1.0, zf + 2.0)
    # gate (kaisatsu-guchi): open passage + door leaf slid aside
    for (xx, w_) in ((gate[0] - 0.05, 0.05), (gate[1], 0.05)):
        frame.box(xx, xx + w_, f_y0 - 0.04, f_y1 + 0.04, zf, zf + 2.05)
    frame.box(gate[0] - 0.05, gate[1] + 0.05, f_y0 - 0.04, f_y1 + 0.04, zf + 2.05, zf + 2.17)
    leaf_x0 = gate[1] - 0.95
    frame.box(leaf_x0, leaf_x0 + 0.06, f_y0 - 0.1, f_y0 - 0.06, zf, zf + 2.0)
    frame.box(leaf_x0 + 0.89, leaf_x0 + 0.95, f_y0 - 0.1, f_y0 - 0.06, zf, zf + 2.0)
    frame.box(leaf_x0, leaf_x0 + 0.95, f_y0 - 0.1, f_y0 - 0.06, zf, zf + 0.6)
    frame.box(leaf_x0, leaf_x0 + 0.95, f_y0 - 0.1, f_y0 - 0.06, zf + 1.94, zf + 2.0)
    glass.box(leaf_x0 + 0.06, leaf_x0 + 0.89, f_y0 - 0.085, f_y0 - 0.075, zf + 0.6, zf + 1.94)
    sash_door(frame, glass, Y_BACK + 1.8, 1, -8.0 + 0.0, -6.0, zf, zf + 2.05, open_leaf=-0.0)  # porch door (moved to porch front)

    # ---- corner posts, beams, belts (exposed raw timber)
    for (cx, cy) in ((SX0, Y_WALL), (SX1, Y_WALL), (SX0, Y_BACK), (SX1, Y_BACK)):
        dark.box(cx - 0.09, cx + 0.09, cy - 0.09, cy + 0.09, Z0, Z_BEAM + 0.2)
    dark.box(SX0 - 0.12, SX1 + 0.12, Y_WALL - 0.10, Y_WALL + 0.10, Z_BEAM, Z_BEAM + 0.25)       # front eave beam
    dark.box(SX0 - 0.12, SX1 + 0.12, Y_BACK - 0.10, Y_BACK + 0.10, Z_BEAM, Z_BEAM + 0.25)       # back eave beam
    dark.box(SX0, SX1, Y_WALL - 0.03, Y_WALL + 0.10, zf + 2.17, zf + 2.27)                      # lintel belt (front)
    dark.box(SX0, SX1, Y_BACK - 0.10, Y_BACK + 0.03, zf + 2.17, zf + 2.27)
    dark.box(SX0, SX1, Y_WALL - 0.05, Y_WALL, Z0 + 0.0, Z0 + 0.10)                              # base board
    dark.box(SX0, SX1, Y_BACK, Y_BACK + 0.05, Z0 + 0.0, Z0 + 0.10)

    # ---- roof (tile geometry) -------------------------------------------------------------
    xa, xb = SX0 - GAB, SX1 + GAB
    run = RIDGE_Y - EAVE_FY
    drop = run * PITCH
    roof_surface((xa, RIDGE_Y, RIDGE_Z + 0.03), (1, 0), (0, -1), run, drop, 0, xb - xa)
    roof_surface((xa, RIDGE_Y, RIDGE_Z + 0.03), (1, 0), (0, 1), run, drop, 0, xb - xa)
    # underside deck + rafters + verge boards
    for sgn, ey, wy in ((-1, EAVE_FY, Y_WALL), (1, EAVE_BY, Y_BACK)):
        za = EAVE_Z - 0.10
        zb = RIDGE_Z - 0.10
        dark.quad_pts((xa, ey, za), (xb, ey, za), (xb, RIDGE_Y, zb), (xa, RIDGE_Y, zb)) if sgn < 0 else \
            dark.quad_pts((xb, ey, za), (xa, ey, za), (xa, RIDGE_Y, zb), (xb, RIDGE_Y, zb))
        n_r = int((xb - xa) / 0.45)
        for i in range(n_r + 1):
            x = xa + 0.05 + (xb - xa - 0.1) * i / n_r
            z_wall = RIDGE_Z - (abs(wy - RIDGE_Y)) * PITCH - 0.14
            frame.sbox((x, ey, EAVE_Z - 0.16), (x, wy, z_wall), 0.05, 0.085, up=(1, 0, 0))
        frame.box(xa, xb, ey - 0.04 if sgn < 0 else ey, ey if sgn < 0 else ey + 0.04, EAVE_Z - 0.24, EAVE_Z + 0.02)  # eave board
        for xe in (xa, xb):
            frame.sbox((xe, ey, EAVE_Z - 0.02), (xe, RIDGE_Y, RIDGE_Z), 0.20, 0.06, up=(1, 0, 0))               # verge board
    # ridge cap & end blocks
    tile_cap.cyl((xa - 0.05, RIDGE_Y, RIDGE_Z + 0.10), (xb + 0.05, RIDGE_Y, RIDGE_Z + 0.10), 0.14, seg=14)
    for xe in (xa - 0.05, xb + 0.05):
        tile_cap.box(xe - 0.14, xe + 0.14, RIDGE_Y - 0.17, RIDGE_Y + 0.17, RIDGE_Z + 0.02, RIDGE_Z + 0.42)

    # ---- monitor roof (koshi-yane) ---------------------------------------------------------
    mx0, mx1 = -9.4, -4.6
    my0, my1 = RIDGE_Y - 0.62, RIDGE_Y + 0.62
    mz0, mz1 = RIDGE_Z - 0.30, RIDGE_Z + 0.62
    walls.box(mx0, mx1, my0, my1, mz0, mz1 - 0.0)
    for yy, out in ((my0, -1), (my1, 1)):
        n = 6
        for i in range(n):
            gx0 = mx0 + 0.16 + (mx1 - mx0 - 0.32) * i / n
            gx1 = gx0 + (mx1 - mx0 - 0.32) / n - 0.08
            gz0, gz1 = RIDGE_Z + 0.12, mz1 - 0.1
            frame.box(gx0 - 0.04, gx1 + 0.04, yy - 0.05 - (0.02 if out > 0 else 0.0), yy + 0.05 + (0.02 if out < 0 else 0.0), gz0 - 0.04, gz1 + 0.04)
            glass.box(gx0, gx1, yy - 0.01 * out - 0.003 + out * 0.045, yy - 0.01 * out + 0.003 + out * 0.045, gz0, gz1)
            frame.box((gx0 + gx1) / 2 - 0.008, (gx0 + gx1) / 2 + 0.008, yy + out * 0.045 - 0.012, yy + out * 0.045 + 0.012, gz0, gz1)
    mrun = (my1 - my0) / 2 + 0.38
    mdrop = mrun * PITCH
    mz_ridge = mz1 + 0.07 + (my1 - my0) / 2 * PITCH
    roof_surface((mx0 - 0.5, (my0 + my1) / 2, mz_ridge), (1, 0), (0, -1), mrun, mdrop, 0, mx1 - mx0 + 1.0)
    roof_surface((mx0 - 0.5, (my0 + my1) / 2, mz_ridge), (1, 0), (0, 1), mrun, mdrop, 0, mx1 - mx0 + 1.0)
    for sgn, ey in ((-1, (my0 + my1) / 2 - mrun), (1, (my0 + my1) / 2 + mrun)):
        dark.quad_pts((mx0 - 0.5, ey, mz_ridge - mdrop - 0.05), (mx1 + 0.5, ey, mz_ridge - mdrop - 0.05),
                      (mx1 + 0.5, (my0 + my1) / 2, mz_ridge - 0.08), (mx0 - 0.5, (my0 + my1) / 2, mz_ridge - 0.08)) if sgn < 0 else \
            dark.quad_pts((mx1 + 0.5, ey, mz_ridge - mdrop - 0.05), (mx0 - 0.5, ey, mz_ridge - mdrop - 0.05),
                          (mx0 - 0.5, (my0 + my1) / 2, mz_ridge - 0.08), (mx1 + 0.5, (my0 + my1) / 2, mz_ridge - 0.08))
    tile_cap.cyl((mx0 - 0.55, (my0 + my1) / 2, mz_ridge + 0.07), (mx1 + 0.55, (my0 + my1) / 2, mz_ridge + 0.07), 0.10, seg=12)
    for (xa_, xb_) in ((mx0, mx0 + 0.12), (mx1 - 0.12, mx1)):
        walls.extrude_x([(my0, mz1), (my1, mz1), ((my0 + my1) / 2, mz_ridge - 0.10)], xa_, xb_)

    # ---- entrance porch (genkan) with its own gable and a row of small clerestory windows ------
    px0, px1 = -8.55, -5.45
    py0, py1 = Y_BACK, Y_BACK + 1.8
    pz_top = 3.30
    pxc = (px0 + px1) / 2
    walls.box(px0, px0 + WT, py0, py1, Z0, pz_top)          # side walls
    walls.box(px1 - WT, px1, py0, py1, Z0, pz_top)
    # porch front wall with door opening
    hole_wall(walls, 'x', px0, px1, py1 - WT, py1, Z0, pz_top, [(-8.0, -6.0, zf, zf + 2.05)])
    walls.extrude_y([(px0, pz_top), (px1, pz_top), (pxc, pz_top + 1.0 - 0.10)], py1 - WT, py1)   # porch gable triangle
    # clerestory windows in the porch gable (row of 4)
    for i in range(4):
        gx0 = px0 + 0.35 + (px1 - px0 - 0.7) * i / 4
        gx1 = gx0 + (px1 - px0 - 0.7) / 4 - 0.1
        frame.box(gx0 - 0.04, gx1 + 0.04, py1 - 0.02, py1 + 0.07, pz_top + 0.14, pz_top + 0.50)
        glass.box(gx0, gx1, py1 + 0.03, py1 + 0.036, pz_top + 0.18, pz_top + 0.46)
    # porch roof
    prun = (px1 - px0) / 2 + 0.35
    pdrop = prun * PITCH
    pz_ridge = pz_top + 0.2 + (px1 - px0) / 2 * PITCH
    y_in, y_out = py0 - 0.2, py1 + 0.55
    roof_surface((pxc, y_in, pz_ridge + 0.03), (0, 1), (-1, 0), prun, pdrop, 0, y_out - y_in)
    roof_surface((pxc, y_in, pz_ridge + 0.03), (0, 1), (1, 0), prun, pdrop, 0, y_out - y_in)
    for ex, xs in ((pxc - prun, -1), (pxc + prun, 1)):
        za, zb_ = pz_ridge - pdrop - 0.10, pz_ridge - 0.10
        if xs < 0:
            dark.quad_pts((ex, y_in, za), (ex, y_out, za), (pxc, y_out, zb_), (pxc, y_in, zb_))
        else:
            dark.quad_pts((ex, y_out, za), (ex, y_in, za), (pxc, y_in, zb_), (pxc, y_out, zb_))
    frame.sbox((pxc - prun, y_out, pz_ridge - pdrop - 0.02), (pxc, y_out, pz_ridge), 0.20, 0.06, up=(0, 1, 0))
    frame.sbox((pxc + prun, y_out, pz_ridge - pdrop - 0.02), (pxc, y_out, pz_ridge), 0.20, 0.06, up=(0, 1, 0))
    tile_cap.cyl((pxc, y_in, pz_ridge + 0.10), (pxc, y_out + 0.05, pz_ridge + 0.10), 0.11, seg=12)
    # porch posts
    dark.box(px0 - 0.07, px0 + 0.07, py1 - 0.07, py1 + 0.07, Z0, pz_top + 0.2)
    dark.box(px1 - 0.07, px1 + 0.07, py1 - 0.07, py1 + 0.07, Z0, pz_top + 0.2)
    # porch floor (raised plank deck)
    floor.box(px0 + WT, px1 - WT, py0, py1 - WT, zf - 0.06, zf)
    # name board over the porch door (hand-painted, weathered)
    image_plane("facade_name", [(-8.0, py1 + 0.02, zf + 2.28), (-6.0, py1 + 0.02, zf + 2.28),
                                (-6.0, py1 + 0.02, zf + 2.28 + 0.54), (-8.0, py1 + 0.02, zf + 2.28 + 0.54)],
                "facade_board_old.png", {"rough": 0.7, "spec": 0.15}, col="Signs")
    # (porch sits in front of the main back door -> main back opening sits behind porch door)

    # ---- front canopy posts + struts (platform side) ---------------------------------------
    for x in (-11.6, -8.9, -5.6, -2.4):
        z_top_ = EAVE_Z - 0.20
        dark.cyl((x, Y_WALL - OVER + 0.18, Z_PLAT - 0.1), (x, Y_WALL - OVER + 0.18, z_top_), 0.075, 0.07, seg=10)
        frame.sbox((x, Y_WALL - OVER + 0.18, z_top_ - 0.55), (x, Y_WALL - 0.1, z_top_ + 0.05), 0.07, 0.07, up=(1, 0, 0))
    dark.box(SX0 - 0.1, SX1 + 0.1, Y_WALL - OVER + 0.10, Y_WALL - OVER + 0.26, EAVE_Z - 0.28, EAVE_Z - 0.10)

    # ---- interior ---------------------------------------------------------------------------
    floor.box(SX0 + WT, SX1 - WT, Y_WALL + WT, Y_BACK - WT, zf - 0.08, zf)
    # ceiling boards
    dark.box(SX0 + WT, SX1 - WT, Y_WALL + WT, Y_BACK - WT, Z_BEAM - 0.12, Z_BEAM - 0.06)
    # waiting benches (back wall)
    for (a, b) in ((-11.7, -9.1), (-4.95, -2.3)):
        frame.box(a, b, Y_BACK - WT - 0.46, Y_BACK - WT, zf + 0.42, zf + 0.46)
        frame.box(a, b, Y_BACK - WT - 0.04, Y_BACK - WT, zf + 0.46, zf + 0.95)
        for xl in (a + 0.1, (a + b) / 2, b - 0.1):
            frame.box(xl - 0.04, xl + 0.04, Y_BACK - WT - 0.42, Y_BACK - WT - 0.35, zf, zf + 0.42)
    # station-master's room behind the ticket window (partitions + desk)
    frame.box(SX0 + WT, -8.6, 6.30, 6.38, zf, Z_BEAM - 0.12)
    frame.box(-8.68, -8.6, Y_WALL + WT, 6.38, zf, Z_BEAM - 0.12)
    frame.box(-10.2, -8.9, Y_WALL + WT + 0.35, Y_WALL + WT + 0.85, zf + 0.72, zf + 0.76)   # desk top
    for (dx, dy) in ((-10.15, 5.35), (-8.95, 5.35), (-10.15, 4.95), (-8.95, 4.95)):
        frame.box(dx - 0.025, dx + 0.025, dy - 0.025, dy + 0.025, zf, zf + 0.72)
    frame.box(-9.8, -9.4, Y_WALL + WT + 1.05, Y_WALL + WT + 1.45, zf + 0.42, zf + 0.46)    # chair seat
    frame.box(-9.8, -9.4, Y_WALL + WT + 1.43, Y_WALL + WT + 1.47, zf + 0.46, zf + 0.9)
    iron.box(-9.85, -9.6, Y_WALL + WT + 0.45, Y_WALL + WT + 0.7, zf + 0.76, zf + 0.84)    # black telephone
    # wicket gate (ratchi): wooden rails with a pivoting bar
    for xr in (gate[0] + 0.15, gate[1] - 0.15):
        for yy in (Y_WALL + WT + 0.15, Y_WALL + WT + 1.25):
            frame.box(xr - 0.05, xr + 0.05, yy - 0.05, yy + 0.05, zf, zf + 1.05)
        frame.box(xr - 0.025, xr + 0.025, Y_WALL + WT + 0.15, Y_WALL + WT + 1.25, zf + 0.95, zf + 1.02)
        frame.box(xr - 0.025, xr + 0.025, Y_WALL + WT + 0.15, Y_WALL + WT + 1.25, zf + 0.55, zf + 0.60)
    frame.sbox((gate[0] + 0.2, Y_WALL + WT + 0.7, zf + 0.9), (gate[0] + 0.85, Y_WALL + WT + 0.35, zf + 0.9), 0.04, 0.06, up=(0, 0, 1))
    # pot-belly stove (darumasutoobu) + flue through the roof
    sx, sy = -4.3, 7.0
    iron.cyl((sx, sy, zf + 0.12), (sx, sy, zf + 0.78), 0.27, 0.27, seg=18)
    iron.cyl((sx, sy, zf + 0.78), (sx, sy, zf + 0.92), 0.22, 0.09, seg=18)
    iron.sphere((sx, sy, zf + 0.45), (0.30, 0.30, 0.30), seg=18, rings=10)
    for dx, dy in ((0.2, 0.2), (-0.2, 0.2), (0.2, -0.2), (-0.2, -0.2)):
        iron.box(sx + dx - 0.025, sx + dx + 0.025, sy + dy - 0.025, sy + dy + 0.025, zf, zf + 0.14)
    iron.box(sx - 0.45, sx + 0.45, sy - 0.45, sy + 0.45, zf, zf + 0.012)
    roof_z_at = RIDGE_Z - abs(sy - RIDGE_Y) * PITCH
    iron.cyl((sx, sy, zf + 0.9), (sx, sy, zf + 1.6), 0.065, seg=12)
    iron.cyl((sx, sy, zf + 1.6), (sx + 0.0, sy + 0.0, roof_z_at + 1.15), 0.062, seg=12)
    iron.cyl((sx, sy, roof_z_at + 1.15), (sx, sy, roof_z_at + 1.22), 0.11, 0.0, seg=12)
    # fire bucket + sand box
    redp.cyl((-3.0, 8.0, zf), (-3.0, 8.0, zf + 0.30), 0.15, 0.17, seg=14)

    # ---- west / east wall detail: ventilation window in the gable
    for xg in (SX0 - 0.03, SX1 + 0.0):
        frame.box(min(xg, xg + 0.03), max(xg, xg + 0.03), RIDGE_Y - 0.28, RIDGE_Y + 0.28, Z_BEAM + 0.35, Z_BEAM + 0.62)

    # ---- red cylindrical post box (maru-poSto) by the porch
    redp.cyl((-9.4, 10.2, 0.0), (-9.4, 10.2, 1.08), 0.27, 0.27, seg=24)
    redp.sphere((-9.4, 10.2, 1.08), (0.27, 0.27, 0.18), seg=24, rings=8)
    iron.box(-9.42, -9.37, 9.92, 9.935, 0.78, 0.84)
    redp.box(-9.50, -9.30, 10.0, 10.42, 0.0, 0.1)

    # ---- M6: 駅舎室内の照明(待合・出札/駅長室・改札通路)と吊りランプ。監査: 窓内が黒潰れ・室内が暗い
    import rooms as _rooms
    for (lx, ly, w_) in ((-10.4, 5.4, 60), (-7.2, 7.0, 90), (-3.6, 6.4, 90), (-7.4, 5.2, 60)):
        _rooms.lamp_point(lx, ly, zf + 2.35, w_)
        iron.cyl((lx, ly, zf + 2.35), (lx, ly, Z_BEAM - 0.12), 0.012, seg=8)            # 吊り棒
        iron.cyl((lx, ly, zf + 2.30), (lx, ly, zf + 2.46), 0.0, 0.16, seg=14)             # 笠(電球の傘)
    for a in (walls, frame, dark, glass, plinth, floor, iron, tile_cap, redp, conc):
        a.build()

    # roof surfaces -> one object
    if ROOF_V:
        V = np.concatenate(ROOF_V)
        T = np.concatenate(ROOF_T)
        np_mesh("roof_tiles", V, T, M["roof"], "Station", smooth=True)

    # ---- signs (enamel / paper / board) ---------------------------------------------------------------
    image_on("timetable", "timetable_old.png", 'F', -5.88, (0.54, 0.72), zf + 1.65, kw={"rough": 0.4, "spec": 0.5})
    image_on("fare", "fare_board.png", 'F', -9.35, (1.0, 0.73), 3.05, kw={"rough": 0.5, "spec": 0.3})
    image_on("clock", "clock.png", 'F', -7.4, (0.52, 0.52), 3.28, extra=0.03,
             kw={"rough": 0.2, "spec": 0.8}, alpha=True)
    image_on("ad_onsen", "ad_onsen.png", 'W', 5.4, (0.50, 0.71), 2.35, kw={"rough": 0.22, "spec": 0.7})
    image_on("ad_nokyo", "ad_nokyo.png", 'W', 6.6, (0.95, 0.40), 3.0, kw={"rough": 0.22, "spec": 0.7})
    image_on("ad_fire", "ad_fire.png", 'W', 7.2, (0.26, 0.56), 2.0, kw={"rough": 0.22, "spec": 0.7})
    image_on("poster1", "poster_inaho.png", 'B', -3.55, (0.45, 0.64), zf + 1.2, kw={"rough": 0.6, "spec": 0.2})
    image_on("poster2", "poster_hike.png", 'B', -11.8 + 0.0, (0.0001, 0.0001), 1.0, kw={"rough": 0.6})   # placeholder (tiny)
    image_on("ad_safety", "ad_safety.png", 'E', 4.6, (0.75, 0.27), 3.0, kw={"rough": 0.22, "spec": 0.7})
    image_on("logo_sign", "logo_new.png", 'F', -4.45, (0.80, 0.80), 3.12, extra=0.02, kw={"rough": 0.35, "spec": 0.5}, alpha=True)
    # first-generation emblem, framed and kept in the waiting room (back wall, between window and porch door)
    zc = zf + 1.62
    yb = Y_BACK - WT - 0.02
    image_plane("emblem_first_frame", [(-9.32, yb, zc - 0.40), (-8.58, yb, zc - 0.40), (-8.58, yb, zc + 0.40), (-9.32, yb, zc + 0.40)],
                "emblem_first.png", {"rough": 0.5, "spec": 0.3}, col="Signs")
    build_annex()


def build_annex():
    """Detached little toilet annex east of the station (real stations often have one) - tin roof."""
    x0, x1, y0, y1 = 0.4, 3.0, 5.4, 7.6
    z1 = 2.55
    w = Acc("annex_walls", M["wall"], "Station", bevel=0.006)
    w.box(x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, -0.1, 0.2)
    hole_wall(w, 'x', x0, x1, y0, y0 + 0.1, 0.2, z1, [(1.1, 2.0, 0.2, 2.0)])
    hole_wall(w, 'x', x0, x1, y1 - 0.1, y1, 0.2, z1, [])
    hole_wall(w, 'y', y0, y1, x0, x0 + 0.1, 0.2, z1, [(6.2, 6.9, 1.6, 2.1)])
    hole_wall(w, 'y', y0, y1, x1 - 0.1, x1, 0.2, z1, [])
    w.build()
    d = Acc("annex_door", M["wood_dark"], "Station", bevel=0.004)
    d.box(1.15, 1.2, y0 - 0.85, y0 + 0.04, 0.2, 1.95)       # door leaf swung open outwards
    d.box(x0 - 0.02, x1 + 0.02, y0 - 0.1, y1 + 0.1, z1, z1 + 0.12)
    for xx in (x0, x1):
        d.box(xx - 0.06, xx + 0.06, y0 - 0.06, y0 + 0.06, 0.2, z1 + 0.1)
        d.box(xx - 0.06, xx + 0.06, y1 - 0.06, y1 + 0.06, 0.2, z1 + 0.1)
    d.build()
    # corrugated tin roof (single pitch) built from a sine profile
    add_tin_roof((x0 - 0.35, x1 + 0.35), (y0 - 0.4, y1 + 0.45), z1 + 0.25, z1 + 0.62, name="annex_roof")


def add_tin_roof(xr, yr, z_low, z_high, name="tin_roof", period=0.076 * 1.0, amp=0.012):
    """Corrugated-iron lean-to roof sloping along Y (low at y0, high at y1). Real ridged geometry."""
    x0, x1 = xr
    y0, y1 = yr
    nx = int((x1 - x0) / (period / 6)) + 1
    xs = np.linspace(x0, x1, nx)
    ys = np.array([y0, y1])
    L = math.hypot(y1 - y0, z_high - z_low)
    ny = 2
    yy, zz = ys, np.array([z_low, z_high])
    nrm = np.array([0.0, -(z_high - z_low), (y1 - y0)]) / L
    if nrm[2] < 0:
        nrm = -nrm
    h = amp * np.sin(2 * np.pi * xs / period)
    P = np.zeros((ny, nx, 3))
    for j in range(ny):
        P[j, :, 0] = xs
        P[j, :, 1] = yy[j] + nrm[1] * h
        P[j, :, 2] = zz[j] + nrm[2] * h
    idx = np.arange(ny * nx).reshape(ny, nx)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
    return np_mesh(name, P.reshape(-1, 3), T, M["tin"], "Station", smooth=True)
