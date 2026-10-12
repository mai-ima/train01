import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""kit3: bespoke builders for special stations (megaterminal 国都中央 first).  Local frame: tracks along +x ending at buffer stops x=0,
headhouse at x>0, forecourt further +x.  Wrapped by kit.Zone from kit2.build_zone."""
import math, random
from common import *
import lib, props, rooms, core, trackkit, sig
from props import G, face_plane
from rooms import A, shell, lamp_point, counter
import kit
from kit import ST, platform, mats
import kit_town as KT

ZP = Z_PLAT
TEX = kit.TEX if hasattr(kit, "TEX") else f"{_R}/tex"
import os


def asphalt():
    import kit5
    kit5.mats5()
    M["asphalt"] = M["ug_asph"]
    M["paving"] = M["ug_paving"]
    return M["asphalt"], M["paving"]


def ss(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ M01 国都中央
def m01_layout():
    ys = []
    y = -74.0
    groups = []
    for gname, nisl in (("JNR", 7), ("KE", 3)):
        g0 = len(ys)
        for k in range(nisl):
            ys += [y, y + 8.2]
            y += 8.2 + 4.4
        groups.append((gname, g0, len(ys)))
        y += 5.0
    fan = []
    for i, yy in enumerate(ys):
        yc = np.mean(ys) * 0.6 if i % 2 == 0 else np.mean(ys) * 0.6 + 4.4
        fan.append(yc + (i - len(ys) / 2) * 0.45)
    return ys, groups, fan


def m01():
    import kit2
    kit2.mats2()
    asphalt()
    st = ST["M01"]
    rng = random.Random(101)
    kit.ground(L=900, W=900)
    # ---- track layout: JNR 7 islands (14 tracks) + KE 3 islands (6 tracks); KM is underground
    ys, plats, groups = [], [], []
    y = -74.0
    for gname, nisl in (("JNR", 7), ("KE", 3)):
        g0 = len(ys)
        for k in range(nisl):
            ys += [y, y + 8.2]
            plats.append((y + 1.7, y + 6.5, gname))
            y += 8.2 + 4.4
        groups.append((gname, g0, len(ys), ys[g0] - 3.0, ys[-1] + 3.0))
        y += 5.0
    fan_x0, x_start = -300.0, -230.0
    for i, yy in enumerate(ys):
        xs = np.linspace(fan_x0, 0.0, 70)
        yc = np.mean(ys) * 0.6 if i % 2 == 0 else np.mean(ys) * 0.6 + 4.4
        yk = yy + (yc + (i - len(ys) / 2) * 0.45 - yy) * (1 - ss((xs - (-215)) / 80.0))
        P = np.stack([xs, yk], 1)
        trackkit.build_track(f"m01_trk{i}", P, wooden=True, ballast=True, fittings=(i % 3 == 0), cam=None)
        trackkit.buffer_stop(0.5, yy, 0)
    for (a, b, gname) in plats:
        platform(-205, -2, a, b, name=f"m01_plat_{int(a)}")
    # platform furniture: benches, lamps, number boards, kiosks
    gp = G("m01_platfurn", "Props")
    for ia, (a, b, gname) in enumerate(plats):
        ym = (a + b) / 2
        for x in np.arange(-190, -8, 14.0):
            gp.a("iron_black").box(x - 0.05, x + 0.05, ym - 0.05, ym + 0.05, ZP, ZP + 3.4)
            gp.a("wood_dark").box(x - 1.2, x + 1.2, ym - 0.35 - 0.9, ym - 0.05 - 0.9, ZP + 0.4, ZP + 0.45)
            gp.a("wood_dark").box(x - 1.2, x + 1.2, ym + 0.05 + 0.9, ym + 0.35 + 0.9, ZP + 0.4, ZP + 0.45)
        for x in (-30, -80, -140):
            gp.a("wood_dark").box(x - 1.6, x + 1.6, ym - 1.0, ym + 1.0, ZP, ZP + 2.3)
            gp.a("glass").box(x - 1.45, x + 1.45, ym - 1.02, ym - 0.98, ZP + 0.9, ZP + 2.0)
            gp.a("tin").box(x - 1.9, x + 1.9, ym - 1.3, ym + 1.3, ZP + 2.3, ZP + 2.45)
    gp.build()
    # ---- JNR grand train shed: 3 barrel vaults, steel ribs on columns, glass
    gs = G("m01_shed", "Station")
    (_, ja, jb, ylo, yhi) = groups[0]
    span = (yhi - ylo) / 3.0
    for v in range(3):
        y0, y1 = ylo + v * span, ylo + (v + 1) * span
        rise = 10.0
        top = ZP + 9.0
        def arc(yy0, yy1, off, n=18):
            return [(yy0 + (yy1 - yy0) * t / n, top + off + rise * math.sin(math.pi * t / n)) for t in range(n + 1)]
        outer, inner = arc(y0, y1, 0.0), arc(y0, y1, -0.35)
        for xr in np.arange(-136, 1, 8.5):
            prof = outer + inner[::-1]
            gs.a("iron_black").extrude_x(prof, xr - 0.14, xr + 0.14)
            gs.a("iron_black").sbox((xr, y0 + 0.5, top - 0.2), (xr, y1 - 0.5, top - 0.2), 0.12, 0.25)
        gs.a("glass").extrude_x(arc(y0, y1, 0.05, 18) + arc(y0, y1, 0.0, 18)[::-1], -136.0, 0.0)
        for ly in np.linspace(y0 + 2, y1 - 2, 9):
            t = (ly - y0) / (y1 - y0)
            gs.a("iron_black").box(-136, 0, ly - 0.05, ly + 0.05, top + rise * math.sin(math.pi * t) - 0.3, top + rise * math.sin(math.pi * t))
    for yy in np.linspace(ylo, yhi, 4):
        for xr in np.arange(-136, 1, 17.0):
            gs.a("iron_black", bevel=0.02).box(xr - 0.3, xr + 0.3, yy - 0.3, yy + 0.3, 0.0, ZP + 9.2)
    # gable end screen at far end (x=-136): glass + mullions
    for v in range(3):
        y0, y1 = ylo + v * span, ylo + (v + 1) * span
        for t in range(0, 18):
            ya, yb = y0 + span * t / 18, y0 + span * (t + 1) / 18
            h = rise * math.sin(math.pi * (t + 0.5) / 18)
            gs.a("glass").box(-136.05, -135.95, ya, yb, ZP + 9.2, ZP + 9.2 + h)
            gs.a("iron_black").box(-136.1, -135.9, ya - 0.04, ya + 0.04, ZP + 9.2, ZP + 9.2 + h)
    gs.build()
    # ---- KE terminal canopies (lower, gabled steel with tin)
    gk = G("m01_ke_can", "Station")
    (_, ka, kb, klo, khi) = groups[1]
    for (a, b, gname) in plats:
        if gname != "KE":
            continue
        ym = (a + b) / 2
        for x in np.arange(-160, -5, 9.0):
            gk.a("iron_black").box(x - 0.12, x + 0.12, ym - 0.12, ym + 0.12, 0.0, ZP + 4.2)
        gk.a("tin").extrude_x([(ym - 6.2, ZP + 3.9), (ym, ZP + 4.7), (ym + 6.2, ZP + 3.9), (ym + 6.2, ZP + 3.84), (ym, ZP + 4.64), (ym - 6.2, ZP + 3.84)], -160, -4)
    gk.build()
    # ---- headhouse: wings (solid brick, windows) + hollow central concourse
    yH0, yH1 = ys[0] - 14.0, ys[-1] + 14.0
    gh = G("m01_head", "Buildings")
    xb0, xb1 = 3.0, 36.0
    brick, band = gh.a("brick", bevel=0.01), gh.a("plasterw", bevel=0.01)
    glass, dark = gh.a("glass"), gh.a("iron_black")
    yc = (yH0 + yH1) / 2
    cw = 46.0   # central pavilion half-width... total 2*cw/2
    cy0, cy1 = yc - cw / 2, yc + cw / 2
    zc0 = ZP
    nfl, fh = 4, 5.2

    def wall_block(ya, yb, nfloors, gx0=xb0, gx1=xb1, rooftype="mansard"):
        top = zc0 + nfloors * fh
        brick.box(gx0, gx1, ya, yb, -0.3, top)
        for k in range(nfloors + 1):
            band.box(gx0 - 0.15, gx1 + 0.15, ya - 0.1, yb + 0.1, zc0 + k * fh - 0.2, zc0 + k * fh + 0.2)
        # window grid on +x face and the two long faces
        for k in range(nfloors):
            z0 = zc0 + k * fh + 1.1
            for yy in np.arange(ya + 2.0, yb - 2.0, 3.6):
                glass.box(gx1 - 0.02, gx1 + 0.06, yy, yy + 1.9, z0, z0 + 2.9)
                dark.box(gx1 - 0.04, gx1 + 0.08, yy - 0.1, yy, z0 - 0.1, z0 + 3.0)
                dark.box(gx1 - 0.04, gx1 + 0.08, yy + 1.9, yy + 2.0, z0 - 0.1, z0 + 3.0)
                dark.box(gx1 - 0.04, gx1 + 0.08, yy - 0.1, yy + 2.0, z0 + 2.9, z0 + 3.05)
                band.box(gx1 - 0.04, gx1 + 0.12, yy - 0.2, yy + 2.1, z0 - 0.2, z0 - 0.05)
            for xx in np.arange(gx0 + 3.0, gx1 - 2.0, 4.0):
                for yy in (ya, yb):
                    s = -1 if yy == ya else 1
                    glass.box(xx, xx + 1.8, yy + (0.06 * s if s > 0 else -0.06), yy + (0.0 if s > 0 else 0.0) + 0.0, z0, z0 + 2.9) if False else None
        # roof
        if rooftype == "mansard":
            gh.a("roof").extrude_x([(ya - 0.6, top), (ya + 2.5, top + 3.6), (yb - 2.5, top + 3.6), (yb + 0.6, top), (yb - 0.2, top), (yb - 2.9, top + 3.3), (ya + 2.9, top + 3.3), (ya + 0.2, top)], gx0 - 0.4, gx1 + 0.4)
            for yy in np.arange(ya + 4, yb - 3, 8.0):
                dark.box(gx1 - 1.0, gx1 - 0.2, yy, yy + 1.4, top + 0.6, top + 2.6)
        elif rooftype == "flat":
            band.box(gx0 - 0.3, gx1 + 0.3, ya - 0.3, yb + 0.3, top, top + 0.7)
        return top

    wl = cy0 - 6.0
    wall_block(yH0, cy0, 3)
    wall_block(cy1, yH1, 3)
    # end pavilions, taller, flat with band
    wall_block(yH0 - 14, yH0, 5, rooftype="flat")
    wall_block(yH1, yH1 + 14, 5, rooftype="flat")
    # upper floors above the central concourse (floors 2..4 solid), concourse below hollow
    ctop = zc0 + nfl * fh + 4
    gh.a("brick").box(xb0, xb1, cy0, cy1, zc0 + 12.0, ctop)
    for k in range(2, nfl + 1):
        band.box(xb0 - 0.2, xb1 + 0.2, cy0 - 0.15, cy1 + 0.15, zc0 + k * fh + 1.6, zc0 + k * fh + 2.0)
    for yy in np.arange(cy0 + 3, cy1 - 3, 4.2):
        for z0 in (zc0 + 13.0, zc0 + 17.0):
            glass.box(xb1 - 0.02, xb1 + 0.06, yy, yy + 2.2, z0, z0 + 2.8)
            dark.box(xb1 - 0.04, xb1 + 0.1, yy - 0.12, yy + 2.32, z0 - 0.12, z0 + 2.92)
    gh.a("roof").extrude_x([(cy0 - 0.8, ctop), (cy0 + 4, ctop + 6), (cy1 - 4, ctop + 6), (cy1 + 0.8, ctop), (cy1 - 0.2, ctop), (cy1 - 4.4, ctop + 5.5), (cy0 + 4.4, ctop + 5.5), (cy0 + 0.2, ctop)], xb0 - 0.6, xb1 + 0.6)
    # clock tower on the central pavilion
    tx, ty = xb1 - 6.0, yc
    gh.a("brick").box(tx - 4.0, tx + 4.0, ty - 4.0, ty + 4.0, ctop, ctop + 22)
    band.box(tx - 4.4, tx + 4.4, ty - 4.4, ty + 4.4, ctop + 22, ctop + 23)
    gh.a("roof").extrude_z([(tx - 4.6, ty - 4.6), (tx + 4.6, ty - 4.6), (tx + 4.6, ty + 4.6), (tx - 4.6, ty + 4.6)], ctop + 23, ctop + 24)
    gh.a("roof").cyl((tx, ty, ctop + 23), (tx, ty, ctop + 32), 4.2, 0.2, seg=4)
    gh.a("iron_black").cyl((tx, ty, ctop + 32), (tx, ty, ctop + 35), 0.1, seg=6)
    gh.build()
    for face, (dx, dy, f) in (("E", (4.05, 0, 'E')), ("W", (-4.05, 0, 'W')), ("S", (0, -4.05, 'S')), ("N", (0, 4.05, 'N'))):
        gc = G(f"m01_clk_{face}", "Props")
        gc.a("white" if "white" in M else "plasterw").cyl((tx + dx, ty + dy, ctop + 15), (tx + dx * 1.01, ty + dy * 1.01, ctop + 15.2), 2.6, seg=24)
        gc.a("iron_black").cyl((tx + dx * 1.01, ty + dy * 1.01, ctop + 15.2), (tx + dx * 1.02, ty + dy * 1.02, ctop + 15.3), 0.15, seg=8)
        gc.build()
    # ---- concourse (hollow, 12 m high) across the centre block
    g = G("m01_conc", "Station")
    zf = ZP + 0.05
    ops = {"E": [(cy0 + 4 + 8.0 * i, cy0 + 4 + 8.0 * i + 5.0, zf + 0.2, zf + 7.5, 'glass') for i in range(5)] +
                [(yc - 3.0, yc + 3.0, zf, zf + 4.2, 'open')],
           "W": [(cy0 + 2, yc - 2, zf, zf + 8.5, 'open'), (yc + 2, cy1 - 2, zf, zf + 8.5, 'open')],
           "S": [(xb0 + 6, xb0 + 10, zf, zf + 3.8, 'open')], "N": [(xb0 + 6, xb0 + 10, zf, zf + 3.8, 'open')]}
    shell(g, xb0, xb1, cy0, cy1, ZP, zc0 + 12.0, 0.5, ops, wall="brick")
    g.a("plat_top").box(xb0 + 0.5, xb1 - 0.5, cy0 + 0.5, cy1 - 0.5, ZP - 0.05, zf)
    g.a("plasterw").box(xb0 + 0.5, xb1 - 0.5, cy0 + 0.5, cy1 - 0.5, zc0 + 11.4, zc0 + 11.6)
    for xx in (xb0 + 11, xb0 + 22):
        for yy in np.arange(cy0 + 5, cy1 - 4, 8.0):
            g.a("plasterw", bevel=0.03).box(xx - 0.6, xx + 0.6, yy - 0.6, yy + 0.6, zf, zc0 + 11.4)
            g.a("iron_black").box(xx - 0.75, xx + 0.75, yy - 0.75, yy + 0.75, zf, zf + 0.5)
    # ticket windows (west wall of the east block = counters along x=xb1-1), info desk, kiosks, benches
    for j in range(8):
        yy = cy0 + 5 + j * 4.6
        g.a("wood_dark").box(xb1 - 3.2, xb1 - 1.2, yy, yy + 3.2, zf, zf + 1.1)
        g.a("glass").box(xb1 - 3.2, xb1 - 3.1, yy + 0.2, yy + 3.0, zf + 1.1, zf + 2.4)
        g.a("iron_black").box(xb1 - 3.25, xb1 - 3.05, yy + 0.1, yy + 3.1, zf + 2.4, zf + 2.6)
    g.a("wood_dark").cyl((xb0 + 16, yc, zf), (xb0 + 16, yc, zf + 1.1), 2.2, seg=20)
    g.a("brass" if "brass" in M else "iron_black").cyl((xb0 + 16, yc, zf + 1.1), (xb0 + 16, yc, zf + 3.5), 0.12, seg=8)
    for dy in (-12, 12):
        for k in range(6):
            g.a("wood_dark").box(xb0 + 5 + k * 1.6, xb0 + 5.9 + k * 1.6, yc + dy - 2.5, yc + dy + 2.5, zf, zf + 0.5)
    for j in range(5):
        yy = cy0 + 4 + j * 8.5
        g.a("wood_dark").box(xb0 + 4, xb0 + 6.2, yy, yy + 3, zf, zf + 2.2)
        g.a("tin").box(xb0 + 3.8, xb0 + 6.4, yy - 0.1, yy + 3.1, zf + 2.2, zf + 2.4)
    for yy in np.linspace(cy0 + 4, cy1 - 4, 5):
        for xx in (xb0 + 8, xb0 + 20):
            lamp_point(xx, float(yy), zc0 + 10.5, watt=260.0, size=0.5, name="m01_lamp")
    for yy in np.linspace(cy0 + 6, cy1 - 6, 4):
        g.a("iron_black").cyl((xb0 + 16, float(yy), zc0 + 11.4), (xb0 + 16, float(yy), zc0 + 9.5), 0.04, seg=6)
        g.a("glass").cyl((xb0 + 16, float(yy), zc0 + 9.5), (xb0 + 16, float(yy), zc0 + 8.6), 0.55, 0.25, seg=10)
    g.build()
    for nm, (ya, yb) in {"a": (cy0 + 5, cy0 + 17), "b": (cy1 - 17, cy1 - 5)}.items():
        face_plane(f"m01_board_{nm}", KT.img("M01", "timetable"), 'E', xb0 + 0.6, (ya + yb) / 2, zf + 7.5, 10.0, h=3.4, off=0.0) if False else None
    kt = KT.img("M01", "timetable")
    if kt:
        face_plane("m01_tt1", kt, 'W', xb1 - 0.55, cy0 + 12, zf + 3.0, 2.6, h=3.2, off=0.0)
    # signage on facade
    nm = ST["M01"]
    ek = f"{TEX}/kit_M01_ekimei.png"
    if os.path.exists(ek):
        face_plane("m01_ekimei", ek, 'E', xb1 + 0.3, yc, zc0 + 11.4, 14.0, h=14.0 / 3.0, off=0.0)
    # ---- other-company access: KM subway entrances (stairs into the ground) + KE ticket gate block
    ge = G("m01_km", "Station")
    for (yy, nmx) in ((yH0 - 30, "a"), (yH1 + 30, "b")):
        ge.a("concrete").box(40, 52, yy - 5, yy + 5, -0.2, 3.6)
        ge.a("dark_glass").box(51.9, 52.05, yy - 3.5, yy + 3.5, 0.0, 2.8)
        ge.a("plasterw").box(39.6, 52.4, yy - 5.4, yy + 5.4, 3.6, 4.0)
        ge.a("iron_black").box(52.0, 52.3, yy - 4.9, yy + 4.9, 3.3, 3.6)
    ge.build()
    # ---- forecourt plaza, fountain, bus terminal, roads, expressway, towers
    core.apron("m01_plaza", 74.0, yc, 38.0, 90.0, M["paving"])
    gp2 = G("m01_plaza_f", "Props")
    gp2.a("concrete").cyl((72, yc, 0.0), (72, yc, 0.9), 9.0, seg=40)
    gp2.a("dark_glass").cyl((72, yc, 0.7), (72, yc, 0.95), 8.4, seg=40)
    gp2.a("concrete").cyl((72, yc, 0.9), (72, yc, 3.6), 1.2, 0.7, seg=16)
    gp2.a("concrete").cyl((72, yc, 3.6), (72, yc, 4.1), 3.0, 0.4, seg=20)
    for k in range(10):
        a = 2 * math.pi * k / 10
        gp2.a("iron_black").cyl((72 + 6 * math.cos(a), yc + 6 * math.sin(a), 0.9), (72 + 6 * math.cos(a), yc + 6 * math.sin(a), 2.6), 0.07, seg=6)
    # bus shelters
    for j in range(8):
        yy = yc - 60 + j * 17
        gp2.a("iron_black").box(94, 94.2, yy, yy + 0.2, 0.0, 3.3)
        gp2.a("iron_black").box(98, 98.2, yy, yy + 0.2, 0.0, 3.3)
        gp2.a("tin").box(93.5, 99, yy - 0.2, yy + 7.4, 3.3, 3.45)
        gp2.a("wood_dark").box(95, 97, yy + 2.0, yy + 5.5, 0.0, 0.5)
        for xx in (94, 98):
            gp2.a("iron_black").box(xx, xx + 0.2, yy + 7.0, yy + 7.2, 0.0, 3.3)
    # streetlamps
    for yy in np.arange(yc - 110, yc + 111, 22.0):
        for xx in (50, 110):
            gp2.a("iron_black").cyl((xx, float(yy), 0.0), (xx, float(yy), 7.0), 0.08, seg=6)
            gp2.a("iron_black").sbox((xx, float(yy), 7.0), (xx - 1.6, float(yy), 7.1), 0.08, 0.08)
    gp2.build()
    for pts, w in (([(120, yc - 400), (120, yc), (120, yc + 400)], 14.0), ([(30, yc + 130), (150, yc + 130), (400, yc + 130)], 12.0), ([(30, yc - 130), (150, yc - 130), (400, yc - 130)], 12.0),
                   ([(-300, yc + 140), (-150, yc + 140), (30, yc + 130)], 9.0), ([(-300, yc - 120), (-150, yc - 120), (30, yc - 130)], 9.0),
                   ([(190, yc - 400), (190, yc), (190, yc + 400)], 12.0), ([(260, yc - 400), (260, yc), (260, yc + 400)], 10.0)):
        core.ribbon(f"m01_rd_{int(pts[0][0])}_{int(pts[0][1])}", pts, w, M["asphalt"], rut=False)
    # elevated expressway on piers
    ex = G("m01_exp", "Props")
    xe = 170.0
    for yy in np.arange(yc - 400, yc + 400, 22.0):
        ex.a("concrete", bevel=0.05).box(xe - 0.7, xe + 0.7, yy - 0.7, yy + 0.7, 0.0, 7.2)
        ex.a("concrete").box(xe - 5, xe + 5, yy - 0.9, yy + 0.9, 7.2, 8.0)
    ex.a("concrete").box(xe - 6, xe + 6, yc - 400, yc + 400, 8.0, 8.6)
    ex.a("road" if "road" in M else "concrete").box(xe - 5.5, xe + 5.5, yc - 400, yc + 400, 8.6, 8.66)
    for sgn in (-1, 1):
        ex.a("concrete").box(xe + sgn * 5.8 - 0.15, xe + sgn * 5.8 + 0.15, yc - 400, yc + 400, 8.6, 9.5)
    ex.build()
    # towers: department store, hotel, offices (variety of plan/height/finish)
    gt = G("m01_towers", "Buildings")
    plans = []
    r = random.Random(7)
    cols = ["plasterw", "brick", "concrete"]
    spots = [(135, yc - 95, 40, 30, 48, "brick"), (135, yc + 98, 42, 34, 66, "plasterw"), (205, yc - 60, 36, 40, 90, "concrete"), (205, yc + 70, 44, 36, 58, "plasterw"),
             (235, yc - 150, 30, 30, 120, "concrete"), (235, yc + 160, 34, 34, 100, "plasterw"), (140, yc - 190, 34, 44, 40, "brick"), (140, yc + 195, 40, 40, 52, "concrete"),
             (-20, yc + 105, 30, 36, 34, "plasterw"), (-20, yc - 100, 28, 36, 28, "brick")]
    for (x0, y0, w, d, h, wallk) in spots:
        gt.a(wallk, bevel=0.02).box(x0, x0 + w, y0 - d / 2, y0 + d / 2, -0.2, h)
        n = int(h // 3.6)
        for k in range(1, n):
            zz = k * 3.6
            gt.a("glass").box(x0 - 0.05, x0 + w + 0.05, y0 - d / 2 - 0.05, y0 + d / 2 + 0.05, zz + 0.7, zz + 2.7)
            gt.a("iron_black").box(x0 - 0.06, x0 + w + 0.06, y0 - d / 2 - 0.06, y0 + d / 2 + 0.06, zz + 0.65, zz + 0.75)
        # vertical piers hide the glass band's flat look
        for yy in np.linspace(y0 - d / 2, y0 + d / 2, int(d // 3) + 1):
            gt.a(wallk).box(x0 - 0.12, x0 + 0.1, yy - 0.25, yy + 0.25, 0.0, h)
            gt.a(wallk).box(x0 + w - 0.1, x0 + w + 0.12, yy - 0.25, yy + 0.25, 0.0, h)
        for xx in np.linspace(x0, x0 + w, int(w // 3) + 1):
            gt.a(wallk).box(xx - 0.25, xx + 0.25, y0 - d / 2 - 0.12, y0 - d / 2 + 0.1, 0.0, h)
            gt.a(wallk).box(xx - 0.25, xx + 0.25, y0 + d / 2 - 0.1, y0 + d / 2 + 0.12, 0.0, h)
        gt.a("concrete").box(x0 - 0.5, x0 + w + 0.5, y0 - d / 2 - 0.5, y0 + d / 2 + 0.5, h, h + 0.8)
        gt.a("iron_black").box(x0 + w * 0.3, x0 + w * 0.5, y0 - 2, y0 + 2, h + 0.8, h + 3.5)
    gt.build()
    for k, (x0, y0, w, d, h, wk) in enumerate(spots[:2]):
        pass
    # big billboard on the department store roof
    bb = KT.img("M01", "bb0")
    if bb:
        gtt = G("m01_bbpost", "Props")
        gtt.a("iron_black").box(150, 152, yc - 100, yc - 99, 48.8, 56)
        gtt.a("iron_black").box(150, 152, yc - 90, yc - 89, 48.8, 56)
        gtt.build()
        face_plane("m01_bbimg", bb, 'W', 149.9, yc - 94.5, 50.5, 9.0, h=4.6, off=0.0)
    # low shopfront row filling the gaps along the plaza edge
    rr = random.Random(5)
    for yy in np.arange(yc - 112, yc + 112, 9.0):
        if abs(yy - yc) < 8:
            continue
        w = rr.choice([5.0, 6.0, 7.0, 8.0])
        KT.shopfront("M01", 112.0, float(yy), 9.0, w, rr.choice([2, 3]), rr.choice(["plasterw", "brick", "concrete"]), None, face='W', name=f"m01_sf{int(yy)}",
                     roof="flat", poster=KT.img("M01", f"poster{rr.randint(0, 3)}"), rng=rr)
    print("m01 built, tracks", len(ys), "yc", yc)


BUILD = {"M01": m01}


# ------------------------------------------------------------------ M19 大湊 (大規模港湾ターミナル)
def m19_layout():
    ys = [0.0, -9.0, -13.4, -22.4, -26.8, -35.8, -40.2, -49.2]
    C, RO, RI = (-52.0, -25.0), 52.0, 40.0
    xe = []
    for y in ys:
        s = max(-0.98, min(0.98, (y - C[1]) / RI))
        xe.append(C[0] + RI * math.sqrt(1 - s * s) - 2.8)
    return dict(ys=ys, C=C, RO=RO, RI=RI, xe=xe,
                tr=[(70.0, 0.0), (70.0, 58.0)], bm=[(40.0, 0.0), (40.0, 58.0)])


def arc_strip(g, key, C, r0, r1, a0, a1, z0, z1, n=None, bevel=0.0):
    """円弧帯(角度は度)を鉛直に押し出す。"""
    n = n or max(2, int(abs(a1 - a0) / 4))
    pts_o = [(C[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    pts_i = [(C[0] + r0 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C[1] + r0 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n, -1, -1)]
    g.a(key, bevel=bevel).extrude_z(pts_o + pts_i, z0, z1)


def m19():
    import kit2
    kit2.mats2()
    asphalt()
    L = m19_layout()
    ys, C, RO, RI, xe = L["ys"], L["C"], L["RO"], L["RI"], L["xe"]
    rng = random.Random(19)
    st = ST["M19"]
    kit.ground(900, 900)
    # ---- JNR tracks (8) + buffer stops, island platforms, shed
    for i, y in enumerate(ys):
        P = np.stack([np.linspace(-170, xe[i], 70), np.full(70, y)], 1)
        trackkit.build_track(f"m19_trk{i}", P, wooden=True, ballast=True, fittings=(i % 2 == 0), cam=None)
        trackkit.buffer_stop(xe[i] + 0.4, y, 0)
    for k in range(0, 8, 2):
        platform(-150, -23.5, ys[k + 1] + 1.7, ys[k] - 1.7, name=f"m19_plat{k}")
    gp = G("m19_platfurn", "Props")
    for k in range(0, 8, 2):
        ym = (ys[k] + ys[k + 1]) / 2
        for x in np.arange(-140, -30, 13.0):
            gp.a("iron_black").box(x - 0.05, x + 0.05, ym - 0.05, ym + 0.05, ZP, ZP + 3.3)
            gp.a("wood_dark").box(x - 1.1, x + 1.1, ym - 0.2, ym + 0.2, ZP + 0.4, ZP + 0.45)
            gp.a("wood_dark").box(x - 1.1, x + 1.1, ym - 0.2, ym + 0.2, ZP + 0.0, ZP + 0.4)
    gp.build()
    gs = G("m19_shed", "Station")
    for (ya, yb) in ((ys[1] - 3.5, ys[0] + 3.5 - 0.0), (ys[3] - 3.5, ys[2] + 3.5), (ys[5] - 3.5, ys[4] + 3.5), (ys[7] - 3.5, ys[6] + 3.5)):
        pass
    for (ya, yb) in ((ys[3] - 3.0, ys[0] + 3.0), (ys[7] - 3.0, ys[4] + 3.0)):
        top = ZP + 6.8
        ym = (ya + yb) / 2
        for xr in np.arange(-110, -22, 7.0):
            prof = [(ya, top), (ym, top + 3.2), (yb, top), (yb, top - 0.28), (ym, top + 2.9), (ya, top - 0.28)]
            gs.a("iron_black").extrude_x(prof, xr - 0.12, xr + 0.12)
            gs.a("iron_black").sbox((xr, ya, top - 0.3), (xr, yb, top - 0.3), 0.1, 0.22)
            for yy in (ya + 1.0, yb - 1.0, ym):
                gs.a("iron_black", bevel=0.01).box(xr - 0.18, xr + 0.18, yy - 0.18, yy + 0.18, 0.0, top)
        gs.a("tin").extrude_x([(ya - 0.5, top - 0.15), (ym, top + 3.3), (yb + 0.5, top - 0.15), (yb + 0.5, top - 0.25), (ym, top + 3.2), (ya - 0.5, top - 0.25)], -110, -22)
        gs.a("glass").box(-110, -22, ym - 0.6, ym + 0.6, top + 3.25, top + 3.45)
    gs.build()
    # ---- curved concrete headhouse (hollow concourse on ground floor)
    gh = G("m19_head", "Buildings")
    nfl, fh = 4, 4.6
    A0, A1 = -47.0, 47.0
    zf = ZP + 0.05
    # ground floor: outer wall piers + inner colonnade, floor slab, ceiling
    arc_strip(gh, "plat_top", C, RI - 0.2, RO - 0.3, A0, A1, ZP - 0.05, zf, n=24)
    arc_strip(gh, "plasterw", C, RI - 0.2, RO, A0, A1, zf + 5.6, zf + 5.9, n=24)
    nwin = 18
    for k in range(nwin):
        a_s = A0 + (A1 - A0) * k / nwin
        a_e = A0 + (A1 - A0) * (k + 1) / nwin
        am = (a_s + a_e) / 2
        arc_strip(gh, "concrete", C, RO - 0.7, RO, a_s, a_s + (a_e - a_s) * 0.3, ZP, zf + 5.6, bevel=0.01)       # pier
        arc_strip(gh, "dark_glass" if k % 3 == 1 else "glass", C, RO - 0.45, RO - 0.4, a_s + (a_e - a_s) * 0.3, a_e, zf + 0.25, zf + 5.0)
        arc_strip(gh, "iron_black", C, RO - 0.5, RO - 0.35, a_s + (a_e - a_s) * 0.3, a_e, zf + 2.6, zf + 2.72)  # transom
        arc_strip(gh, "concrete", C, RO - 0.7, RO, a_s + (a_e - a_s) * 0.3, a_e, zf, zf + 0.25)                 # sill
        arc_strip(gh, "concrete", C, RO - 0.7, RO, a_s + (a_e - a_s) * 0.3, a_e, zf + 5.0, zf + 5.6)            # lintel
    # entrance arcade (central 3 bays open) -> cut by a recessed portal
    for fl in range(1, nfl):
        z0 = zf + 5.9 + (fl - 1) * fh
        arc_strip(gh, "plasterw", C, RI, RO, A0, A1, z0, z0 + fh, n=24)
        for k in range(nwin * 2):
            a_s = A0 + (A1 - A0) * k / (nwin * 2)
            a_e = A0 + (A1 - A0) * (k + 0.55) / (nwin * 2)
            arc_strip(gh, "glass", C, RO - 0.02, RO + 0.06, a_s, a_e, z0 + 1.0, z0 + 3.4)
            arc_strip(gh, "iron_black", C, RO - 0.03, RO + 0.08, a_s, a_s + 0.25, z0 + 0.9, z0 + 3.5)
        arc_strip(gh, "concrete", C, RO - 0.2, RO + 0.5, A0, A1, z0 + fh - 0.25, z0 + fh + 0.1, n=24)
    ztop = zf + 5.9 + (nfl - 1) * fh
    arc_strip(gh, "concrete", C, RI - 0.5, RO + 0.9, A0 - 1, A1 + 1, ztop, ztop + 0.8, n=26)
    # inner wall (track side) with big glazed openings toward the platforms
    arc_strip(gh, "plasterw", C, RI - 0.3, RI, A0, A1, zf, zf + 5.6, n=24)
    # concourse ceiling + columns + counters
    arc_strip(gh, "plasterw", C, RI, RO - 0.7, A0, A1, zf + 5.55, zf + 5.9, n=24)
    for rr in (RI + 4.0, RI + 8.0):
        for a in np.linspace(A0 + 2, A1 - 2, 11):
            cx, cy = C[0] + rr * math.cos(math.radians(a)), C[1] + rr * math.sin(math.radians(a))
            gh.a("plasterw", bevel=0.03).box(cx - 0.4, cx + 0.4, cy - 0.4, cy + 0.4, zf, zf + 5.55)
            gh.a("iron_black").box(cx - 0.5, cx + 0.5, cy - 0.5, cy + 0.5, zf, zf + 0.3)
    for a in np.linspace(A0 + 8, A1 - 8, 7):
        cx, cy = C[0] + (RI + 1.6) * math.cos(math.radians(a)), C[1] + (RI + 1.6) * math.sin(math.radians(a))
        gh.a("wood_dark").boxc(cx, cy, zf + 0.55, 1.2, 3.4, 1.1, rz=math.radians(a))
        gh.a("glass").boxc(cx - 0.9 * math.cos(math.radians(a)), cy - 0.9 * math.sin(math.radians(a)), zf + 1.75, 0.06, 3.0, 1.3, rz=math.radians(a))
    for a in (-25, 0, 25):
        cx, cy = C[0] + (RI + 9.5) * math.cos(math.radians(a)), C[1] + (RI + 9.5) * math.sin(math.radians(a))
        gh.a("wood_dark").cyl((cx, cy, zf), (cx, cy, zf + 1.1), 1.4, seg=16)
    # roof tower + big sign block on the central axis
    tx = C[0] + RO - 7.0
    gh.a("concrete").box(tx - 6.0, tx + 4.5, C[1] - 9, C[1] + 9, ztop + 0.8, ztop + 9.5)
    gh.a("plasterw").box(tx - 6.3, tx + 4.8, C[1] - 9.3, C[1] + 9.3, ztop + 9.5, ztop + 10.0)
    gh.a("glass").box(tx + 4.5, tx + 4.6, C[1] - 7, C[1] + 7, ztop + 3.0, ztop + 7.5)
    gh.a("iron_black").cyl((tx, C[1], ztop + 10.0), (tx, C[1], ztop + 17.0), 0.15, seg=8)
    gh.build()
    ek = f"{TEX}/kit_M19_ekimei.png"
    if os.path.exists(ek):
        face_plane("m19_ekimei", ek, 'E', tx + 4.65, C[1], ztop + 8.4, 12.0, h=4.0, off=0.0)
    for a in np.linspace(A0 + 4, A1 - 4, 9):
        lamp_point(C[0] + (RI + 6.0) * math.cos(math.radians(a)), C[1] + (RI + 6.0) * math.sin(math.radians(a)), zf + 5.0, watt=200.0, size=0.4, name="m19_lamp")
    kt = KT.img("M19", "timetable")
    if kt:
        for a in (-15.0, 15.0):
            face_plane(f"m19_tt{int(a)}", kt, 'W', C[0] + (RI + 0.32) * math.cos(math.radians(a)), C[1] + (RI + 0.32) * math.sin(math.radians(a)), zf + 2.2, 2.4, h=3.0, off=0.0)
    # ---- plaza + roads
    core.apron("m19_plaza", 46.0, -25.0, 46.0, 60.0, M["paving"])
    for pts, w in (([(110, -140), (110, -25), (110, 120)], 11.0), ([(-8, 70), (50, 70), (130, 70)], 9.0), ([(-8, -120), (50, -120), (130, -120)], 9.0),
                   ([(30, -140), (30, -25), (30, 140)], 7.0)):
        core.ribbon(f"m19_rd_{pts[0][0]}_{pts[0][1]}", pts, w, M["asphalt"], rut=False)
    # ---- TR tram stop (embedded rails + shelter), BM monorail station (elevated)
    tr, bm = L["tr"], L["bm"]
    # 市電の停留場: 舗装道路に埋め込んだ複線(舗装面はレール頭の少し下)。終端は y=0(車止め)、y=58 で市電線へ続く
    core.ribbon("m19_tram_street", [(tr[0][0] - 0.8, float(y)) for y in np.arange(-14.0, 70.0, 6.0)], 14.0, M["asphalt"], z0=0.243, rut=False, col="Roads")
    for sgn in (-1, 1):   # 歩道・縁石・横断歩道・信号
        core.ribbon(f"m19_tram_walk{sgn}", [(tr[0][0] - 0.8 + sgn * 9.4, float(y)) for y in np.arange(-14.0, 70.0, 6.0)], 3.2, M["ug_paving"], z0=0.33, rut=False, col="Roads")
    gx = G("m19_tram_xw", "Props")
    wk = "white" if "white" in M else "plasterw"
    for yc_ in (8.0, 46.0):
        for k in range(15):
            xx = tr[0][0] - 7.0 + k * 0.92
            gx.a(wk).box(xx, xx + 0.46, yc_ - 1.6, yc_ + 1.6, 0.2435, 0.2475)
        for sgn in (-1, 1):
            px = tr[0][0] - 0.8 + sgn * 7.6
            gx.a("iron_black").cyl((px, yc_ + 2.4, 0.33), (px, yc_ + 2.4, 3.2), 0.06, seg=8)
            gx.a("iron_black").box(px - 0.12, px + 0.12, yc_ + 2.28, yc_ + 2.52, 2.5, 3.1)
    gx.build()
    for off in (-1.2, 1.2):
        P = np.stack([np.full(60, tr[0][0] + off), np.linspace(0.0, 58.0, 60)], 1)
        trackkit.build_track(f"m19_tr_{off}", P, wooden=False, ballast=False, fittings=False, cam=None)
        import kit7 as _k7b
        _k7b.tram_bed([tuple(q) for q in P[::3]], f'm19_tr_bed{off}')
        trackkit.buffer_stop(tr[0][0] + off, 0.0, math.pi / 2) if False else None
    gt = G("m19_tram", "Station")
    gt.a("concrete").box(tr[0][0] + 2.0, tr[0][0] + 5.0, 14, 40, 0.0, 0.3)
    for yy in (14.5, 39.5):
        gt.a("iron_black").box(tr[0][0] + 2.2, tr[0][0] + 2.35, yy, yy + 0.15, 0.3, 3.4)
        gt.a("iron_black").box(tr[0][0] + 4.6, tr[0][0] + 4.75, yy, yy + 0.15, 0.3, 3.4)
    gt.a("tin").box(tr[0][0] + 1.8, tr[0][0] + 5.2, 14, 40, 3.4, 3.55)
    gt.a("wood_dark").box(tr[0][0] + 3.0, tr[0][0] + 3.6, 22, 30, 0.3, 0.75)
    gt.build()
    gb = G("m19_mono", "Station")
    y0b, y1b = 14.0, 48.0
    gb.a("concrete").box(bm[0][0] - 0.5, bm[0][0] + 0.5, bm[0][1], bm[1][1], 7.0, 8.2)
    gb.a("iron_black").box(bm[0][0] - 0.31, bm[0][0] + 0.31, bm[0][1], bm[1][1], 8.2, 8.23)          # 走行面
    for sgn in (-1, 1):
        gb.a("iron_black").box(bm[0][0] + sgn * 0.43 - 0.025, bm[0][0] + sgn * 0.43 + 0.025, bm[0][1], bm[1][1], 7.5, 7.8)   # 案内輪の走行面
    for yy in np.arange(bm[0][1] + 6, bm[1][1], 20.0):
        gb.a("concrete", bevel=0.05).box(bm[0][0] - 0.6, bm[0][0] + 0.6, yy - 0.6, yy + 0.6, 0.0, 7.0)
        gb.a("concrete").box(bm[0][0] - 2.4, bm[0][0] + 2.4, yy - 0.8, yy + 0.8, 6.6, 7.0)
    gb.a("concrete").box(bm[0][0] + 1.2, bm[0][0] + 5.6, y0b, y1b, 6.8, 7.2)
    gb.a("glass").box(bm[0][0] + 5.5, bm[0][0] + 5.6, y0b, y1b, 7.2, 8.2)
    gb.a("tin").box(bm[0][0] + 0.8, bm[0][0] + 6.4, y0b - 1, y1b + 1, 9.0, 9.2)
    for yy in np.arange(y0b + 1, y1b, 6.0):
        gb.a("iron_black").box(bm[0][0] + 1.4, bm[0][0] + 1.6, yy, yy + 0.2, 7.2, 9.0)
        gb.a("iron_black").box(bm[0][0] + 5.8, bm[0][0] + 6.0, yy, yy + 0.2, 7.2, 9.0)
    # stair tower
    gb.a("concrete").box(bm[0][0] + 7.0, bm[0][0] + 11.0, y0b + 2, y0b + 8, 0.0, 7.2)
    gb.build()
    # ---- harbour: sea, quay, ferry pier, cranes, warehouses, containers
    xq = 128.0
    gq = G("m19_quay", "Station")
    gq.a("water" if "water" in M else "dark_glass").box(xq, xq + 900, -420, 420, -3.0, 0.0)
    gq.a("concrete", bevel=0.03).box(xq - 4, xq + 0.5, -420, 420, -3.0, 0.35)
    gq.a("concrete").box(xq - 4, xq - 3.0, -420, 420, 0.35, 0.55)
    for yy in np.arange(-400, 401, 12.0):
        gq.a("iron_black").cyl((xq - 1.0, float(yy), 0.35), (xq - 1.0, float(yy), 0.75), 0.18, seg=8)
        gq.a("wood_dark").box(xq - 0.2, xq + 0.1, float(yy) - 0.35, float(yy) + 0.35, -1.8, 0.15)    # fenders
    gq.a("concrete").box(xq, xq + 150, -8, 8, -0.6, 0.35)             # ferry pier
    gq.a("wood_dark").box(xq, xq + 150, -8, -7.6, 0.35, 1.0)
    gq.a("wood_dark").box(xq, xq + 150, 7.6, 8, 0.35, 1.0)
    gq.build()
    # ferry
    gf = G("m19_ferry", "Props")
    fx0, fx1, fy = xq + 25, xq + 100, 16.0
    gf.a("iron_black").extrude_z([(fx0, fy - 6), (fx1 - 12, fy - 6), (fx1, fy), (fx1 - 12, fy + 6), (fx0, fy + 6)], -1.8, 1.5)
    gf.a("white_paint" if "white_paint" in M else "plasterw").extrude_z([(fx0 + 4, fy - 5), (fx1 - 20, fy - 5), (fx1 - 8, fy), (fx1 - 20, fy + 5), (fx0 + 4, fy + 5)], 1.5, 5.2)
    gf.a("dark_glass").extrude_z([(fx0 + 10, fy - 5.05), (fx1 - 30, fy - 5.05), (fx1 - 30, fy - 4.6), (fx0 + 10, fy - 4.6)], 2.4, 4.4)
    gf.a("dark_glass").extrude_z([(fx0 + 10, fy + 4.6), (fx1 - 30, fy + 4.6), (fx1 - 30, fy + 5.05), (fx0 + 10, fy + 5.05)], 2.4, 4.4)
    gf.a("white_paint" if "white_paint" in M else "plasterw").box(fx0 + 22, fx0 + 36, fy - 3.5, fy + 3.5, 5.2, 8.4)
    gf.a("post_red" if "post_red" in M else "iron_black").cyl((fx0 + 14, fy, 5.2), (fx0 + 14, fy, 11.0), 1.2, 0.9, seg=14)
    gf.build()
    for (cx, cy_) in ((xq - 12, -60.0), (xq - 12, 85.0)):
        try:
            sig.KINDS["crane"](cx, cy_, name=f"lm_m19_crane_{int(cy_)}", arm=1, swap=True)
        except Exception as e:
            print("crane fail", e)
    gw = G("m19_wh", "Buildings")
    for k, yy in enumerate(np.arange(-150, 151, 40.0)):
        if abs(yy) < 20:
            continue
        w, d = 32.0, 22.0
        x0 = 78.0 + (k % 2) * 6
        gw.a(rng.choice(["tin", "tin_blue", "tin_green"])).box(x0, x0 + d, yy, yy + w, 0.0, 5.0)
        gw.a("tin").extrude_y([(x0 - 0.5, 4.8), (x0 + d / 2, 7.0), (x0 + d + 0.5, 4.8), (x0 + d + 0.5, 4.7), (x0 + d / 2, 6.9), (x0 - 0.5, 4.7)], yy - 0.4, yy + w + 0.4)
        gw.a("dark_glass").box(x0 + d - 0.05, x0 + d + 0.05, yy + 4, yy + 12, 0.0, 3.8)
    gw.build()
    gc = G("m19_cont", "Props")
    cols = ["post_red", "iron_black", "tin_blue", "tin_green", "tin"]
    for ix in range(6):
        for iy in range(14):
            if rng.random() < 0.18:
                continue
            h = 2.6 * rng.choice([1, 1, 2, 3])
            cx, cy_ = 100.0 + ix * 3.0, -110.0 + iy * 2.6 - (60 if iy > 7 else 0) + (160 if iy > 7 else 0)
            gc.a(rng.choice([c for c in cols if c in M])).box(cx, cx + 2.5, cy_, cy_ + 6.1 if False else cy_ + 2.3, 0.0, h)
    gc.build()
    # ---- town along the shore road, port style
    import kit2
    rp = np.stack([np.linspace(-8, 125, 90), 70 + 0 * np.linspace(-8, 125, 90)], 1)
    kit2.town_along(rp, "M19", st, rng, "port", 0.8, [], sides=("L",), off=2.6, xr=(-8, 60), rows=2)
    rp2 = np.stack([np.linspace(-8, 125, 90), -120 + 0 * np.linspace(-8, 125, 90)], 1)
    kit2.town_along(rp2, "M19", st, rng, "urban", 0.8, [], sides=("R",), off=2.6, xr=(-8, 70), rows=2)
    KT.billboard("M19", 20, 62, KT.img("M19", "bb0"), 'S', name="bb_m19_0")
    print("m19 built")


BUILD["M19"] = m19

# 駅ごとの特別な線路配置(kit4 が参照): poly はローカル座標の折れ線、endonly=True は端点からのみ分岐
def layout_m19():
    L = m19_layout()
    out = []
    for i, y in enumerate(L["ys"]):
        out.append(dict(back=(-170.0, y, math.pi), front=None, xend=L["xe"][i]))
    out.append(dict(back=(L["tr"][1][0], L["tr"][1][1], math.pi / 2), front=None, poly=L["tr"], endonly=True))
    out.append(dict(back=(L["bm"][1][0], L["bm"][1][1], math.pi / 2), front=None, poly=L["bm"], endonly=True))
    return out


LAYOUT = {"M19": layout_m19}


try:
    import kit6
    BUILD.update(kit6.BUILD6)
except Exception as _e:      # kit6 が壊れていても他駅は作れるように
    print("kit6 load fail", _e)
