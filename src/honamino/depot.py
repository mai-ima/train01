"""Locomotive depot south of the station yard: lead, turntable, roundhouse, straight shed, assembly hall, water tower ..."""
from trainkit import *
import trackkit
from trackkit import seg_arc, seg_line, join, RAIL_PROFILE, Z_RAILBASE
import core

TX, TY, PR = -14.0, -80.0, 11.5          # turntable centre, pit radius
RIN, ROUT = 15.0, 36.0                   # roundhouse inner / outer radius
SA = 15.0                                # stall pitch (deg)
STALLS = [270.0 + SA * (k - 4) for k in range(9)]
TABLE_DIR = STALLS[2]                    # table currently lined up with stall 2
DEPOT_PATHS = {}
LEVEL = Z_RAIL


def pol(r, a_deg, cx=TX, cy=TY):
    a = math.radians(a_deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def D(name, mat, bevel=0.0, closed=True, smooth=False):
    return Acc(name, mat, "Depot", bevel=bevel, closed=closed, smooth=smooth)


# ====================================================================== tracks
def build_depot_tracks(cam):
    T4y = T4
    lead = join(seg_arc((4.0, T4y - 18), 18, 90, 180), seg_line((-14.0, T4y - 18), (-14.0, TY + PR)))
    P = {"D_lead": lead}
    for nm, y0 in (("E1", -37.5), ("E2", -42.0), ("E3", -46.5)):
        a = seg_arc((-2.0, y0), 12, 180, 270)
        y = y0 - 12
        if nm == "E1":
            P[nm] = join(a, seg_line((-2.0, y), (30.0, y)))
        elif nm == "E2":
            P[nm] = join(a, seg_line((-2.0, y), (12.0, y)), seg_arc((12.0, -72.0), 18, 90, 0), seg_line((30.0, -72.0), (30.0, -97.0)))
        else:
            P[nm] = join(a, seg_line((-2.0, y), (12.0, y)), seg_arc((12.0, -72.0), 13.5, 90, 0), seg_line((25.5, -72.0), (25.5, -97.0)))
    for nm, y0 in (("W1", -39.0), ("W2", -43.5)):
        a = seg_arc((-26.0, y0), 12, 0, -90)
        P[nm] = join(a, seg_line((-26.0, y0 - 12), (-62.0, y0 - 12)))
    for k, ang in enumerate(STALLS):
        P[f"S{k}"] = np.array([pol(PR + 0.35, ang), pol(ROUT - 1.2, ang)])
    for nm, pth in P.items():
        if nm.startswith("S"):
            pth = trackkit.resample(pth, 1.0)[0]
        trackkit.build_track(nm, pth, cam=cam, pebble_radius=26.0)
        DEPOT_PATHS[nm] = pth
    trackkit.buffer_stop(30.6, -49.5, 0)
    trackkit.buffer_stop(-62.6, -51.0, 180)
    trackkit.buffer_stop(-62.6, -55.5, 180)
    return P


def build_depot_ground():
    core.apron("depot_yard", -14.0, -76.0, 50.0, 47.0, M["road"], noise_amp=0.05, z0=0.012)
    # darker cinder bed round the turntable and in front of the stalls
    a = D("cinder_bed", M["ballast"])
    for k in range(60):
        pass


# ====================================================================== turntable
def build_turntable(ang=None):
    ang = TABLE_DIR if ang is None else ang
    # pit wall (concrete curb) + dark pit floor + rim rail
    w = D("tt_wall", M["concrete"], 0.012)
    N = 56
    for i in range(N):
        a = 360.0 * i / N
        c = pol(PR + 0.32, a)
        chord = 2 * (PR + 0.32) * math.sin(math.pi / N) * 1.03
        w.boxc(c[0], c[1], -0.05, 0.62, chord, 0.62, math.radians(a))
    w.build()
    fl = D("tt_floor", vmat("dark"))
    fl.cyl((TX, TY, 0.02), (TX, TY, 0.04), PR, PR, seg=64)
    fl.build()
    rr = D("tt_rimrail", vmat("rail"))
    rr.torus((TX, TY, 0.07), 'z', PR - 0.45, 0.04, segR=72, segr=5)
    rr.torus((TX, TY, 0.07), 'z', PR - 0.85, 0.04, segR=72, segr=5)
    rr.build()
    # the bridge (local frame: x along the rails)
    v = Veh("turntable")
    hl = PR - 0.55
    dk = v.A("wood_dark", 0.006)
    dk.box(-hl, hl, -1.7, 1.7, 0.02, 0.12)
    for s in (-1, 1):
        g = v.A("iron", 0.008)
        g.box(-hl, hl, s * 1.55 - 0.05, s * 1.55 + 0.05, 0.0, 0.95)                    # girder web
        g.box(-hl, hl, s * 1.55 - 0.16, s * 1.55 + 0.16, 0.90, 0.98)                   # top flange
        g.box(-hl, hl, s * 1.55 - 0.16, s * 1.55 + 0.16, 0.02, 0.08)
        for x in np.arange(-hl + 0.6, hl, 0.9):
            g.box(x - 0.025, x + 0.025, s * 1.55 + s * 0.05, s * 1.55 + s * 0.12, 0.08, 0.90)       # stiffeners
        v.A("iron").cyl((-hl, s * 1.55 + s * 0.06, 0.5), (hl, s * 1.55 + s * 0.06, 0.5), 0.0, 0.0, seg=3) if False else None
        for e in (-1, 1):
            v.A("iron", 0.01).box(*sorted((e * hl, e * (hl + 0.7))), s * 1.55 - 0.3, s * 1.55 + 0.3, -0.25, 0.28)     # end carriage
            v.A("wheel").cyl((e * (hl + 0.35), s * 1.55 - 0.2, 0.0), (e * (hl + 0.35), s * 1.55 + 0.2, 0.0), 0.2, 0.2, seg=12)
        for x in np.arange(-hl + 0.3, hl, 2.2):                                           # rails of the bridge
            pass
    for sgn in (-1, 1):
        prof = [(y + sgn * RAIL_Y, z + 0.14 + 0.0) for (y, z) in RAIL_PROFILE]
        v.A("rail").extrude_x([(y + sgn * RAIL_Y, z + 0.14 - 0.0) for (y, z) in RAIL_PROFILE], -hl, hl)
    sl = v.A("wood", 0.01)
    for x in np.arange(-hl + 0.3, hl, 0.6):
        sl.box(x - 0.075, x + 0.075, -1.05, 1.05, 0.12, 0.26)
    # centre pivot cap + operator cabin
    v.A("steel").cyl((0, 0, 0.12), (0, 0, 0.3), 0.55, 0.45, seg=16)
    v.A("wall", 0.01).box(-hl + 1.2, -hl + 2.7, 1.55, 2.6, 0.95, 2.5)
    v.A("tin", 0.01).box(-hl + 1.1, -hl + 2.8, 1.45, 2.7, 2.5, 2.58)
    v.A("glass").box(-hl + 1.2, -hl + 2.7, 1.54, 1.545, 1.5, 2.2)
    v.A("glass").box(-hl + 1.2, -hl + 1.205, 1.55, 2.6, 1.5, 2.2)
    for s in (-1, 1):
        grab_rail(v, (-hl + 0.5, s * 1.65, 0.98), (-hl + 0.5, s * 1.65, 1.8), 0.02, "iron")
    # buffers / stop blocks at the ends
    for e in (-1, 1):
        v.A("black", 0.01).box(*sorted((e * (hl - 0.1), e * (hl + 0.15))), -0.2, 0.2, 0.15, 0.55)
    return v.place(TX, TY, math.radians(ang), z=0.0)


# ====================================================================== simple gable building
def gable(name, x0, x1, y0, y1, zw, zr, wall_mat="wall", roof_mat="tin", ov=0.5, openings_x=None, openings_y=None,
          t=0.22, ridge_axis='x', window_rows=True, interior=True):
    """Gable building, ridge along x. openings_x: list of (ya,yb,za,zb) holes in the x-end walls (both);
    openings_y: list of (xa,xb,za,zb) holes in the y walls."""
    v = Veh(name)
    ym = (y0 + y1) / 2
    openings_x = openings_x or []
    openings_y = openings_y or []
    wm = wall_mat
    for xe in (x0, x1):
        fx = (xe, xe + t) if xe == x0 else (xe - t, xe)
        wall_open(v, wm, 'x', y0, y1, fx[0], fx[1], 0.0, zw, openings_x, 0.0)
        v.A(wm, 0.0).extrude_y([(fx[0], zw), (fx[1], zw), (fx[1], zw)], y0, y1) if False else None
        # gable triangle
        g = v.A(wm)
        i = len(g.V)
        for (yy, zz) in ((y0, zw), (y1, zw), (ym, zr - 0.15)):
            g.v((fx[0], yy, zz))
        for (yy, zz) in ((y0, zw), (y1, zw), (ym, zr - 0.15)):
            g.v((fx[1], yy, zz))
        g.F.append((i, i + 1, i + 2))
        g.F.append((i + 5, i + 4, i + 3))
        g.F.append((i, i + 3, i + 4, i + 1))
        g.F.append((i + 1, i + 4, i + 5, i + 2))
        g.F.append((i + 2, i + 5, i + 3, i))
    for ys in (y0, y1):
        fy = (ys, ys + t) if ys == y0 else (ys - t, ys)
        wall_open(v, wm, 'y', x0, x1, fy[0], fy[1], 0.0, zw, openings_y, 0.0)
    prof = [(y0 - ov, zw - 0.05), (ym, zr), (y1 + ov, zw - 0.05), (y1 + ov, zw - 0.20), (ym, zr - 0.15), (y0 - ov, zw - 0.20)]
    v.A(roof_mat, 0.0).extrude_x(prof, x0 - ov, x1 + ov)
    v.A("wood_dark").box(x0 - ov, x1 + ov, ym - 0.12, ym + 0.12, zr - 0.04, zr + 0.10)
    if interior:
        v.A("concrete").box(x0 + t, x1 - t, y0 + t, y1 - t, 0.0, 0.05)
    return v


# ====================================================================== roundhouse
def build_roundhouse():
    wallm = D("rh_wall", M["wall"], 0.0)
    pier = D("rh_pier", M["concrete"], 0.01)
    door = D("rh_door", M["wood_dark"], 0.006)
    ironw = D("rh_iron", M["iron_black"], 0.004)
    roofA = D("rh_roofA", M["tin"], closed=False)
    roofB = D("rh_roofB", M["tin"], closed=False)
    glass = D("rh_glass", M["glass"], closed=False)
    trim = D("rh_trim", M["wood_dark"], 0.005)
    flo = D("rh_floor", M["concrete"], 0.0)
    hw = SA / 2
    zA0, zA1 = 5.7, 8.4                     # roof A: r RIN-0.2 -> 25
    rA0, rA1 = RIN - 0.2, 25.0
    zC1 = 9.5                               # clerestory top
    rB1, zB1 = ROUT + 0.4, 5.8
    for k, ang in enumerate(STALLS):
        a0, a1 = ang - hw, ang + hw
        # floor of the stall
        P = [pol(RIN - 3.0, a0), pol(RIN - 3.0, a1), pol(ROUT, a1), pol(ROUT, a0)]
        flo.quad_pts(*[(p[0], p[1], 0.05) for p in P][::-1])
        # piers at stall boundaries (radial walls)
        for a in (a0, a1):
            if (a == a1 and k < 8):
                continue
            cm = pol((RIN + ROUT) / 2, a)
            pier.boxc(cm[0], cm[1], 2.9, ROUT - RIN, 0.55, 5.8, math.radians(a))
            f = pol(RIN, a)
            pier.boxc(f[0], f[1], 2.9, 0.6, 0.9, 5.8, math.radians(a))
        # lintel above the doors
        cf = pol(RIN, ang)
        wallm.boxc(cf[0], cf[1], 5.15, 0.45, 2 * RIN * math.sin(math.radians(hw)) - 0.1, 1.1, math.radians(ang))
        trim.boxc(cf[0] - 0.2 * math.cos(math.radians(ang)), cf[1] - 0.2 * math.sin(math.radians(ang)), 4.65, 0.12,
                  2 * RIN * math.sin(math.radians(hw)) - 0.7, 0.14, math.radians(ang))
        # door leaves (hinged at the pier edges)
        op = [0.0, 100.0, 60.0, 100.0, 0.0, 100.0, 90.0, 0.0, 100.0][k]
        wdoor = (2 * RIN * math.sin(math.radians(hw)) - 0.75) / 2
        for sgn in (-1, 1):
            hinge = pol(RIN + 0.3, ang + sgn * (hw - 2.2))
            hinge = (hinge[0] + 0.0, hinge[1])
            # hinge position: edge of opening
            edge = pol(RIN + 0.25, ang + sgn * math.degrees(math.asin((wdoor) / RIN)))
            tang = np.array([-math.sin(math.radians(ang)), math.cos(math.radians(ang))]) * sgn   # towards the pier
            rad = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
            th = math.radians(op) * (1 if True else -1)
            # closed: leaf extends from the hinge toward the centre (-tang); open: swings outward (-rad)
            d = -tang * math.cos(th) - rad * math.sin(th)
            h0 = np.array(edge)
            h1 = h0 + d * wdoor
            door.sbox((h0[0], h0[1], 2.4), (h1[0], h1[1], 2.4), 0.09, 4.5)
            ironw.sbox((h0[0], h0[1], 1.2), (h1[0], h1[1], 1.2), 0.11, 0.12)
            ironw.sbox((h0[0], h0[1], 3.5), (h1[0], h1[1], 3.5), 0.11, 0.12)
            ironw.sbox((h0[0], h0[1], 0.45), (h1[0], h1[1], 0.45), 0.1, 0.1)
        # outer wall with a high window
        co = pol(ROUT, ang)
        chord = 2 * ROUT * math.sin(math.radians(hw)) - 0.1
        for (zc, hh) in ((1.0, 2.0), (5.0, 1.4)):
            wallm.boxc(co[0], co[1], zc, 0.3, chord, hh, math.radians(ang))
        jamb = (chord - 2.2) / 2
        for sgn in (-1, 1):
            c2 = pol(ROUT, ang + sgn * math.degrees((1.1 + jamb / 2) / ROUT))
            wallm.boxc(c2[0], c2[1], 3.0, 0.3, jamb, 2.0, math.radians(ang))
        glass.quad_pts(*[(p[0], p[1], z) for p, z in ((pol(ROUT - 0.1, ang + 1.1 / ROUT * 57.3), 2.0), (pol(ROUT - 0.1, ang - 1.1 / ROUT * 57.3), 2.0),
                                                       (pol(ROUT - 0.1, ang - 1.1 / ROUT * 57.3), 4.0), (pol(ROUT - 0.1, ang + 1.1 / ROUT * 57.3), 4.0))])
        for fr in (-0.55, 0.0, 0.55):
            cf2 = pol(ROUT, ang + math.degrees(fr / ROUT))
            trim.boxc(cf2[0], cf2[1], 3.0, 0.2, 0.05, 2.0, math.radians(ang))
        # roofs (per stall, in polar)
        def quad_rz(acc, r0, z0, r1, z1):
            acc.quad_pts((pol(r0, a0)[0], pol(r0, a0)[1], z0), (pol(r0, a1)[0], pol(r0, a1)[1], z0),
                         (pol(r1, a1)[0], pol(r1, a1)[1], z1), (pol(r1, a0)[0], pol(r1, a0)[1], z1))
        quad_rz(roofA, rA0, zA0, rA1, zA1)
        quad_rz(roofA, rA0, zA0 - 0.1, rA1, zA1 - 0.1)
        quad_rz(roofB, rA1 + 0.35, zC1 + 0.05, rB1, zB1)
        quad_rz(roofB, rA1 + 0.35, zC1 - 0.05, rB1, zB1 - 0.1)
        # clerestory glazing + frame
        gp = [(pol(rA1, a0), zA1), (pol(rA1, a1), zA1), (pol(rA1 + 0.3, a1), zC1), (pol(rA1 + 0.3, a0), zC1)]
        glass.quad_pts(*[(p[0], p[1], z) for p, z in gp])
        for fr in np.linspace(a0, a1, 5):
            p = pol(rA1 + 0.15, fr)
            trim.boxc(p[0], p[1], (zA1 + zC1) / 2, 0.12, 0.08, zC1 - zA1, math.radians(fr))
        # smoke hood on the roof
        pc = pol(19.0, ang)
        ironw.boxc(pc[0], pc[1], 7.3, 1.1, 1.1, 1.2, math.radians(ang))
        ironw.boxc(pc[0], pc[1], 8.0, 1.5, 1.5, 0.12, math.radians(ang))
    # end walls of the ring
    for a, sgn in ((STALLS[0] - hw, -1), (STALLS[-1] + hw, 1)):
        poly = [(RIN - 0.2, 0.0), (RIN - 0.2, zA0), (rA1, zA1), (rA1, zC1), (rA1 + 0.35, zC1), (rB1, zB1), (ROUT + 0.2, zB1 - 0.1), (ROUT + 0.2, 0.0)]
        pier.F.append(tuple(pier.v((pol(r, a)[0], pol(r, a)[1], z)) for (r, z) in poly))
        pier.F.append(tuple(reversed([pier.v((pol(r, a)[0], pol(r, a)[1], z)) for (r, z) in poly])))
    for acc in (wallm, pier, door, ironw, roofA, roofB, glass, trim, flo):
        acc.build()


# ====================================================================== other structures
def build_water_tower(x, y):
    v = Veh("water_tower")
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        px, py = 1.9 * math.cos(a), 1.9 * math.sin(a)
        v.A("iron", 0.01).sbox((px * 1.15, py * 1.15, 0.0), (px, py, 6.0), 0.3, 0.3)
        v.A("concrete", 0.01).box(px * 1.15 - 0.4, px * 1.15 + 0.4, py * 1.15 - 0.4, py * 1.15 + 0.4, -0.3, 0.3)
    for zz in (2.0, 4.0):
        for i in range(4):
            a0, a1 = math.radians(45 + 90 * i), math.radians(135 + 90 * i)
            p0 = (1.9 * math.cos(a0) * (1.15 - 0.15 * zz / 6.0), 1.9 * math.sin(a0) * (1.15 - 0.15 * zz / 6.0), zz)
            p1 = (1.9 * math.cos(a1) * (1.15 - 0.15 * zz / 6.0), 1.9 * math.sin(a1) * (1.15 - 0.15 * zz / 6.0), zz)
            v.A("iron").sbox(p0, p1, 0.1, 0.12)
            v.A("iron").sbox(p0, (p1[0], p1[1], zz + 2.0), 0.05, 0.05)
    v.A("wall", 0.02).cyl((0, 0, 6.0), (0, 0, 9.4), 2.5, 2.5, seg=32)
    for zz in np.arange(6.4, 9.4, 0.7):
        v.A("iron").torus((0, 0, zz), 'z', 2.52, 0.04, segR=40, segr=4)
    v.A("tin", 0.02).cyl((0, 0, 9.4), (0, 0, 10.7), 2.8, 0.25, seg=32)
    v.A("iron").cyl((0, 0, 10.6), (0, 0, 11.3), 0.06, 0.06, seg=6)
    v.A("iron").cyl((2.45, 0, 1.0), (2.45, 0, 6.2), 0.03, 0.03, seg=6)
    for zz in np.arange(1.0, 6.2, 0.4):
        v.A("iron").box(2.3, 2.5, -0.2, 0.2, zz, zz + 0.03)
    v.A("iron").cyl((0, 2.55, 6.2), (0, 6.0, 6.2), 0.14, 0.14, seg=8)                  # down pipe
    v.A("iron").cyl((0, 6.0, 6.2), (0, 6.0, 0.4), 0.14, 0.14, seg=8)
    return v.place(x, y, 0.0, z=0.0)


def water_crane(x, y, yaw):
    v = Veh("water_crane")
    v.A("iron").cyl((0, 0, 0), (0, 0, 4.2), 0.12, 0.10, seg=10)
    v.A("iron").cyl((0, 0, 4.0), (-2.5, 0, 4.6), 0.09, 0.09, seg=8)
    v.A("black").cyl((-2.5, 0, 4.6), (-2.6, 0, 3.9), 0.12, 0.12, seg=8)
    v.A("iron").box(-0.4, 0.4, -0.4, 0.4, -0.1, 0.1)
    v.A("iron").box(-0.15, 0.15, -0.5, 0.5, 1.4, 1.5)
    v.A("concrete").box(-0.5, 0.5, -0.5, 0.5, -0.3, 0.1)
    return v.place(x, y, yaw, z=0.0)


def build_coal_stage(x, y):
    v = Veh("coal_stage")
    v.A("wood_dark", 0.01).box(-3.5, 3.5, -2.6, 2.6, 2.4, 2.55)
    for ix in np.arange(-3.3, 3.4, 1.65):
        for iy in (-2.4, 2.4):
            v.A("wood", 0.01).box(ix - 0.15, ix + 0.15, iy - 0.15, iy + 0.15, 0.0, 2.45)
    for iy in (-2.45, 2.45):
        v.A("wood").box(-3.5, 3.5, iy - 0.06, iy + 0.06, 2.5, 3.0)
    rr = random.Random(3)
    for i in range(34):
        v.A("coal", 0.0, True).sphere((rr.uniform(-3, 3), rr.uniform(-2.0, 2.0), 2.7 + rr.uniform(0.0, 0.5)),
                                      (rr.uniform(0.5, 1.0), rr.uniform(0.4, 0.8), rr.uniform(0.3, 0.55)), seg=8, rings=5)
    v.A("wood_dark", 0.01).box(3.5, 8.0, -1.4, 1.4, 1.3, 2.4)
    v.A("wood_dark", 0.01).box(7.8, 8.4, -1.4, 1.4, 0.0, 2.4)
    v.A("coal").box(-3.5, 3.5, -2.5, 2.5, 2.55, 2.7)
    return v.place(x, y, 0.0, z=0.0)


def build_depot_buildings():
    # ---- straight inspection shed (W1/W2), opening east
    sh = gable("shed", -64.0, -34.0, -60.0, -46.5, 4.8, 7.4,
               openings_x=[(-53.2, -48.8, 0.0, 4.6), (-57.7, -53.3, 0.0, 4.6)],
               openings_y=[(-62 + 3.0 + 5.0 * i, -62 + 3.0 + 5.0 * i + 1.4, 2.2, 3.4) for i in range(6)])
    sh.place(0, 0, 0.0, z=0.0)
    # ---- assembly hall (A tracks, opening north)
    hall = gable("hall", 22.0, 34.5, -98.0, -74.5, 7.2, 10.5, ridge_axis='y')
    # build as ridge along y: gable() has ridge along x, so build rotated: use a Veh with swapped axes instead
    return sh


def build_hall():
    """Assembly hall: ridge along y (north-south), two open bays facing north."""
    v = Veh("hall")
    x0, x1, y0, y1 = 21.0, 35.0, -99.0, -74.5
    zw, zr, t, ov = 7.0, 10.2, 0.28, 0.6
    xm = (x0 + x1) / 2
    wall_open(v, "wall", 'x', y0, y1, x0, x0 + t, 0.0, zw, [(-96.0 + 5.2 * i, -96.0 + 5.2 * i + 1.6, 3.3, 4.7) for i in range(4)], 0.0)
    wall_open(v, "wall", 'x', y0, y1, x1 - t, x1, 0.0, zw, [(-96.0 + 5.2 * i, -96.0 + 5.2 * i + 1.6, 3.3, 4.7) for i in range(4)], 0.0)
    # north wall (big openings), south wall (solid)
    wall_open(v, "wall", 'y', x0, x1, y1 - t, y1, 0.0, zw, [(24.2, 28.0, 0.0, 6.0), (28.2, 32.5, 0.0, 6.0)], 0.0)
    wall_open(v, "wall", 'y', x0, x1, y0, y0 + t, 0.0, zw, [], 0.0)
    for (ye, sg) in ((y1, 1), (y0, -1)):
        g = v.A("wall")
        i = len(g.V)
        yy0, yy1 = (ye - t, ye) if sg > 0 else (ye, ye + t)
        for yy in (yy0, yy1):
            for (xx, zz) in ((x0, zw), (x1, zw), (xm, zr - 0.2)):
                g.v((xx, yy, zz))
        g.F += [(i, i + 1, i + 2), (i + 5, i + 4, i + 3), (i, i + 3, i + 4, i + 1), (i + 1, i + 4, i + 5, i + 2), (i + 2, i + 5, i + 3, i)]
    v.A("tin", 0.0).extrude_y([(x0 - ov, zw - 0.05), (xm, zr), (x1 + ov, zw - 0.05), (x1 + ov, zw - 0.22), (xm, zr - 0.17), (x0 - ov, zw - 0.22)], y0 - ov, y1 + ov)
    v.A("wood_dark").box(xm - 0.12, xm + 0.12, y0 - ov, y1 + ov, zr - 0.05, zr + 0.12)
    v.A("concrete").box(x0 + t, x1 - t, y0 + t, y1 - t, 0.0, 0.05)
    # gantry-crane rails + bridge
    for xx in (x0 + 1.0, x1 - 1.0):
        v.A("iron", 0.01).box(xx - 0.2, xx + 0.2, y0 + 0.5, y1 - 0.5, 5.4, 5.7)
        for yy in np.arange(y0 + 1.0, y1, 4.0):
            v.A("concrete").box(xx - 0.3, xx + 0.3, yy - 0.3, yy + 0.3, 0.0, 5.4)
    v.A("iron", 0.01).box(x0 + 0.8, x1 - 0.8, -86.0, -85.2, 5.7, 6.5)
    v.A("iron", 0.01).box(xm - 0.5, xm + 0.5, -86.2, -85.0, 4.6, 5.7)
    v.A("iron").cyl((xm, -85.6, 4.6), (xm, -85.6, 3.0), 0.03, 0.03, seg=5)
    v.A("black", 0.01).box(xm - 0.3, xm + 0.3, -85.9, -85.3, 2.5, 3.0)
    return v.place(0, 0, 0.0, z=0.0)


def build_office(x, y):
    v = gable("office", x, x + 9.0, y, y + 5.5, 2.9, 4.4,
              openings_y=[(x + 1.2 + 2.2 * i, x + 2.4 + 2.2 * i, 1.0, 2.2) for i in range(4)],
              openings_x=[(y + 2.2, y + 3.3, 0.0, 2.0)], interior=False)
    v.A("glass").box(x + 0.3, x + 8.7, y + 0.05, y + 0.07, 1.0, 2.2) if False else None
    v.A("black").box(x + 7.2, x + 7.6, y + 4.0, y + 4.4, 4.2, 5.7)          # chimney
    return v.place(0, 0, 0.0, z=0.0)


def build_depot(cam):
    build_depot_tracks(cam)
    build_depot_ground()
    build_turntable()
    build_roundhouse()
    build_depot_buildings()
    build_hall()
    build_office(-47.0, -35.5)
    build_water_tower(-23.0, -41.5)
    water_crane(-12.4, -62.0, math.pi)
    water_crane(-15.6, -62.0, 0.0)
    build_coal_stage(-21.5, -62.5)
