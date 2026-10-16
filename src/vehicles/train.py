"""Stopped rolling stock at the station: railcar, diesel loco, old coaches, freight wagons, brake van."""
from trainkit import *


def fill_walls(v, key, x0, x1, W, z0, z1):
    """Solid wall block (full width) for cab ends / unused bay remnants."""
    if x1 - x0 > 0.01:
        v.A(key, 0.004).box(x0, x1, -W / 2, W / 2, z0, z1)


# ====================================================================== railcar (two-tone, cream over red)
def make_kiha(name="kiha", num_img="kiha_number.png", seed=1, lo="red", up="cream"):
    v = Veh(name)
    L, W, h = 20.0, 2.80, 1.40
    zf, zs, zw1, zt, zr = 1.05, 1.85, 2.75, 2.95, 3.52
    v.A(lo, 0.014).extrude_x([(-h, zf), (h, zf), (h, zs), (-h, zs)], -L / 2, L / 2)
    v.A(up, 0.01).extrude_x([(-h, zw1), (h, zw1), (h, zt), (-h, zt)], -L / 2, L / 2)
    v.A("roof", 0.015).extrude_x(upper_profile(W, zt - 0.05, zt + 0.03, zr, inset=0.04), -L / 2 + 0.02, L / 2 - 0.02)
    bays = [('D', 1.0)] + [('W', 1.02)] * 7 + [('D', 1.0)] + [('W', 1.02)] * 7 + [('D', 1.0)]
    tot, doors = window_bays(v, bays, W, zs, zw1, up, door_key=lo, seed=seed, curtain_p=0.4, door_drop=0.0)
    interior(v, -tot / 2 + 0.1, tot / 2 - 0.1, W, zs, zw1, zt, pitch=1.02, seed=seed)
    for e in (-1, 1):
        xa, xb = sorted((e * tot / 2, e * L / 2))
        for s in (-1, 1):
            wall_open(v, up, 'y', xa, xb, s * (h - 0.08), s * h, zs, zw1,
                      [(*sorted((e * (tot / 2 + 0.12), e * (tot / 2 + 0.90))), zs + 0.1, zw1 - 0.1)])
        wall_open(v, up, 'x', -h, h, e * L / 2 - 0.1 * e, e * L / 2, zs, zw1,
                  [(-1.08, -0.16, zs + 0.12, zw1 - 0.08), (0.16, 1.08, zs + 0.12, zw1 - 0.08)])
        wall_open(v, up, 'x', -h, h, e * tot / 2 - 0.05 * e, e * tot / 2, zs, zw1, [(-0.35, 0.35, zs, zw1 - 0.25)])   # cab partition
        v.A("floorw").box(xa, xb, -h + 0.08, h - 0.08, zs, zs + 0.02)
        dx = e * (L / 2 - 0.45)
        v.A("grey", 0.01).box(dx - 0.2, dx + 0.2, -1.2, 1.2, zs, zs + 0.34)                       # driver's desk
        v.A("black").box(dx - 0.22 * e - 0.1, dx - 0.22 * e + 0.1, -0.5, -0.1, zs + 0.34, zs + 0.40)
        v.A("steel").cyl((dx - e * 0.05, -0.75, zs + 0.34), (dx - e * 0.05, -0.75, zs + 0.52), 0.015, 0.015, seg=6)
        v.A("moq2").box(dx - e * 0.9 - 0.2, dx - e * 0.9 + 0.2, -0.95, -0.55, zs, zs + 0.26)
        if e == 1:
            v.A("cl1", 0.02, True).box(dx - e * 0.8 - 0.15, dx - e * 0.8 + 0.15, -0.9, -0.6, zs, zs + 0.18)
            v.A("skin", 0.0, True).sphere((dx - e * 0.8, -0.75, zs + 0.34), (0.09, 0.08, 0.1), seg=8, rings=6)
            v.A("cream", 0.01).box(dx - e * 0.8 - 0.15, dx - e * 0.8 + 0.15, -0.9, -0.6, zs + 0.18, zs + 0.28) if False else None
    gl = v.A("glass")
    for e in (-1, 1):                                    # cab-end driver side windows + windscreens
        for s in (-1, 1):
            gl.box(*sorted((e * (tot / 2 + 0.12), e * (tot / 2 + 0.90))), *sorted((s * (h + 0.0), s * (h + 0.012))), zs + 0.1, zw1 - 0.1)
        for yc in (-0.62, 0.62):
            gl.box(*sorted((e * L / 2, e * (L / 2 + 0.012))), yc - 0.46, yc + 0.46, zs + 0.12, zw1 - 0.08)
        v.A(up, 0.005).box(*sorted((e * L / 2, e * (L / 2 + 0.02))), -0.07, 0.07, zs + 0.05, zw1)   # centre pillar
        v.A("roof", 0.01).box(*sorted((e * (L / 2 - 0.1), e * (L / 2 + 0.05))), -0.5, 0.5, zt + 0.06, zt + 0.40)  # headlamp hood
        v.A("lampglass").cyl((e * (L / 2 + 0.04), 0, zt + 0.23), (e * (L / 2 + 0.07), 0, zt + 0.23), 0.12, 0.12, seg=12)
        for yc in (-1.0, 1.0):                           # marker lamps
            v.A("lampglass").cyl((e * (L / 2), yc, 1.55), (e * (L / 2 + 0.06), yc, 1.55), 0.065, 0.065, seg=10)
            v.A("black").cyl((e * (L / 2 + 0.01), yc, 1.55), (e * (L / 2 + 0.04), yc, 1.55), 0.09, 0.09, seg=10)
        v.A("steel").cyl((e * (L / 2 + 0.03), -0.9, zw1 - 0.02), (e * (L / 2 + 0.03), -0.2, zs + 0.45), 0.012, 0.012, seg=5)   # wipers
        v.A("steel").cyl((e * (L / 2 + 0.03), 0.9, zw1 - 0.02), (e * (L / 2 + 0.03), 0.2, zs + 0.45), 0.012, 0.012, seg=5)
        v.A("iron", 0.01).box(*sorted((e * L / 2, e * (L / 2 + 0.16))), -1.2, 1.2, 0.86, 1.02)     # end sill
        coupler(v, e, e * (L / 2 + 0.12))
        v.end_plane(num_img, e, 0.0, 0.62, 1.60, 1.82, e * (L / 2 + 0.014))
        v.end_plane("headmark.png", e, 0.0, 0.34, 1.20, 1.54, e * (L / 2 + 0.016))
        for s in (-1, 1):                                # step + grab rail at cab end
            grab_rail(v, (e * (L / 2 - 0.1), s * (h + 0.05), 1.15), (e * (L / 2 - 0.1), s * (h + 0.05), 2.65))
    for dx in doors:
        for s in (-1, 1):
            steps_down(v, dx, s, h, zf)
    # underframe + equipment
    v.A("under", 0.01).box(-L / 2 + 0.3, L / 2 - 0.3, -1.15, 1.15, 0.62, zf)
    v.A("under", 0.01).box(-3.4, 0.9, -0.85, 0.85, 0.34, 0.62)                       # fuel tank
    v.A("iron", 0.01).box(1.8, 3.6, -0.9, 0.2, 0.40, 0.62)                           # battery box
    v.A("iron", 0.01).box(-5.6, -4.2, -0.2, 0.9, 0.42, 0.62)
    for yy in (-0.5, 0.5):
        v.A("steel").cyl((4.3, yy, 0.50), (5.9, yy, 0.50), 0.14, 0.14, seg=10)       # air reservoirs
    v.A("black").cyl((-6.9, 0, 0.9), (6.9, 0, 0.9), 0.04, 0.04, seg=6)               # propeller shaft
    for x in (-6.9, 6.9):
        bogie2(v, x)
    roof_vents(v, [-6.4, -3.2, 0.0, 3.2, 6.4], zr - 0.04)
    for x in (-8.0, 8.0):                                                            # roof radiator boxes
        v.A("roof", 0.015).box(x - 0.9, x + 0.9, -0.65, 0.65, zr - 0.08, zr + 0.14)
        v.A("dark").box(x - 0.8, x + 0.8, -0.60, 0.60, zr + 0.13, zr + 0.15)
    v.A("steel").cyl((-5.0, 0.0, zr), (-5.0, 0.0, zr + 0.5), 0.07, 0.07, seg=8)
    # decals
    for s in (-1, 1):
        v.side_plane("mark_depot.png", s, 1.0, 1.9, 1.20, 1.45, s * (h + 0.012))
        v.side_plane("logo_new.png", s, -4.0, 0.52, 1.22, 1.74, s * (h + 0.012))
        v.side_plane(num_img, s, 7.4, 0.72, 1.55, 1.82, s * (h + 0.012))
    return v


# ====================================================================== old brown passenger coach
def make_coach(name="coach", mark="mark_coach.png", variant=0, seed=2):
    v = Veh(name)
    Lb, Ld, W, h = 17.8, 19.8, 2.80, 1.40
    zf, zs, zw1, zt, zr = 1.05, 1.72, 2.62, 2.80, 3.48
    v.A("coach", 0.012).extrude_x([(-h, zf), (h, zf), (h, zs), (-h, zs)], -Lb / 2, Lb / 2)
    v.A("coach", 0.01).extrude_x([(-h, zw1), (h, zw1), (h, zt), (-h, zt)], -Lb / 2, Lb / 2)
    v.A("roof", 0.015).extrude_x(upper_profile(W + 0.04, zt - 0.05, zt + 0.05, zr, inset=0.0), -Ld / 2, Ld / 2)
    bays = [('s', 0.55), ('D', 0.95)] + [('W', 1.38)] * 9 + [('D', 0.95), ('s', 0.55)]
    if variant == 1:
        bays = [('s', 0.7), ('s', 0.7), ('D', 0.95)] + [('W', 1.38)] * 7 + [('s', 1.1), ('D', 0.95), ('s', 0.55)]
    tot, doors = window_bays(v, bays, W, zs, zw1, "coach", door_key="coach", seed=seed, curtain_p=0.35, door_drop=0.0,
                             frame_key="coach", pillar=0.16)
    fill_walls(v, "coach", -Lb / 2, -tot / 2, W, zs, zw1)
    fill_walls(v, "coach", tot / 2, Lb / 2, W, zs, zw1)
    interior(v, -tot / 2 + 1.0, tot / 2 - 1.0, W, zs, zw1, zt, pitch=1.38, seed=seed, person_p=0.4)
    for e in (-1, 1):
        xe = e * Lb / 2
        v.A("black", 0.01).box(*sorted((xe, e * (Ld / 2))), -1.12, 1.12, 0.95, 1.05)         # end deck
        v.A("coach", 0.008).box(*sorted((xe, xe + e * 0.03)), -0.47, 0.47, 1.12, 2.55)         # end door
        v.A("glass").box(*sorted((xe, xe + e * 0.045)), -0.30, 0.30, 1.85, 2.45)
        for s in (-1, 1):                                                                     # deck railings
            for xx in (xe + e * 0.12, e * (Ld / 2 - 0.12)):
                grab_rail(v, (xx, s * 1.05, 1.05), (xx, s * 1.05, 2.0), 0.022, "iron")
            grab_rail(v, (xe + e * 0.12, s * 1.05, 1.95), (e * (Ld / 2 - 0.12), s * 1.05, 1.95), 0.02, "iron")
            grab_rail(v, (xe + e * 0.12, s * 1.05, 1.45), (e * (Ld / 2 - 0.12), s * 1.05, 1.45), 0.02, "iron")
            grab_rail(v, (e * (Ld / 2 - 0.12), s * 1.05, 2.0), (e * (Ld / 2 - 0.12), s * 1.05, 2.8), 0.025, "iron")
        grab_rail(v, (e * (Ld / 2 - 0.12), -1.05, 1.95), (e * (Ld / 2 - 0.12), 1.05, 1.95), 0.02, "iron")
        v.A("coach", 0.008).box(*sorted((e * (Ld / 2 - 0.16), e * (Ld / 2 - 0.10))), -0.65, 0.65, 1.1, 1.5)    # gate board
        coupler(v, e, e * (Ld / 2 + 0.05))
        v.A("iron", 0.01).box(*sorted((e * (Ld / 2), e * (Ld / 2 + 0.12))), -1.1, 1.1, 0.90, 1.03)
        v.A("lampglass").cyl((e * (Ld / 2 - 0.2), 0.0, 2.3), (e * (Ld / 2 - 0.12), 0.0, 2.3), 0.06, 0.06, seg=8)
        for s in (-1, 1):
            steps_down(v, e * (Ld / 2 - 0.6), s, 1.12, 1.05, n=2, w=0.55)
    # underfloor
    v.A("under", 0.01).box(-Lb / 2, Lb / 2, -1.2, 1.2, 0.84, zf)
    for yy in (-0.35, 0.35):
        v.A("iron").cyl((-7.0, yy, 0.80), (7.0, yy, 0.80), 0.016, 0.016, seg=5)          # truss rods
    for x in (-5.0, 5.0):
        v.A("iron").box(x - 0.05, x + 0.05, -0.2, 0.2, 0.60, 0.84)
    v.A("steel").cyl((-3.0, 0.0, 0.62), (-0.8, 0.0, 0.62), 0.20, 0.20, seg=10)           # air cylinder
    v.A("iron", 0.01).box(1.4, 3.4, -0.9, 0.3, 0.45, 0.84)                                # battery box
    v.A("iron", 0.01).box(-6.0, -4.0, -0.4, 0.9, 0.5, 0.84)                               # water tank
    for x in (-6.6, 6.6):
        bogie2(v, x, wb=2.45)
    roof_vents(v, [-6.4, -3.2, 0.0, 3.2, 6.4], zr - 0.04)
    v.A("black").cyl((-7.8, 0.75, zr - 0.1), (-7.8, 0.75, zr + 0.35), 0.07, 0.09, seg=8)  # stove chimney
    # decals
    for s in (-1, 1):
        v.side_plane(mark, s, 5.6, 2.2, 1.10, 1.38, s * (h + 0.012))
        v.side_plane("logo_new.png", s, -5.8, 0.5, 1.12, 1.62, s * (h + 0.012))
    return v


# ====================================================================== diesel locomotive (centre cab, two hoods)
def make_loco(name="loco", body="blue", stripe="white", plate="plate_dd.png"):
    v = Veh(name)
    L = 13.6
    ze = 1.28
    h = 1.45
    v.A("under", 0.012).box(-6.7, 6.7, -1.35, 1.35, 0.90, 1.22)
    v.A("under", 0.01).box(-1.9, 1.9, -0.9, 0.9, 0.50, 0.90)                              # fuel tank
    v.A("grey", 0.008).box(-6.8, 6.8, -1.45, 1.45, 1.20, ze)                              # deck
    hood_lo = [(-1.18, ze), (1.18, ze), (1.18, 2.55), (0.95, 2.85), (-0.95, 2.85), (-1.18, 2.55)]
    hood_hi = [(-1.18, ze), (1.18, ze), (1.18, 2.95), (0.95, 3.30), (-0.95, 3.30), (-1.18, 2.95)]
    v.A(body, 0.02).extrude_x(hood_lo, -6.2, -2.8)
    v.A(body, 0.02).extrude_x(hood_hi, 0.8, 6.3)
    for s in (-1, 1):
        wall_open(v, body, 'y', -2.8, 0.8, s * (h - 0.08), s * h, ze, 3.55, [(-2.55, -1.55, 2.30, 3.30), (-0.45, 0.55, 2.30, 3.30)], 0.01)
    wall_open(v, body, 'x', -h, h, -2.8, -2.72, ze, 3.55, [(-1.2, 1.2, 2.95, 3.45)], 0.01)
    wall_open(v, body, 'x', -h, h, 0.72, 0.8, ze, 3.55, [(-1.40, -1.18, 2.35, 3.35), (1.18, 1.40, 2.35, 3.35), (-1.18, 1.18, 3.32, 3.48)], 0.01)
    v.A("grey", 0.02).extrude_x(upper_profile(2.9, 3.50, 3.58, 3.98, inset=0.0), -2.9, 0.9)
    # stripe
    for s in (-1, 1):
        v.A(stripe, 0.004).box(-6.2, -2.8, *sorted((s * 1.18, s * 1.19)), 1.52, 1.70)
        v.A(stripe, 0.004).box(0.8, 6.3, *sorted((s * 1.18, s * 1.19)), 1.52, 1.70)
        v.A(stripe, 0.004).box(-2.8, 0.8, *sorted((s * h, s * (h + 0.012))), 1.52, 1.70)
    v.A(stripe, 0.004).box(-6.21, -6.2, -1.2, 1.2, 1.52, 1.70)
    v.A(stripe, 0.004).box(6.3, 6.31, -1.2, 1.2, 1.52, 1.70)
    # cab windows
    gl = v.A("glass")
    for s in (-1, 1):
        for (a, b) in ((-2.55, -1.55), (-0.45, 0.55)):
            gl.box(a, b, *sorted((s * h, s * (h + 0.012))), 2.30, 3.30)
        v.A(body, 0.005).box(-1.45, -0.55, *sorted((s * h, s * (h + 0.02))), 1.75, 3.35)    # door leaf
        gl.box(-1.30, -0.70, *sorted((s * (h + 0.02), s * (h + 0.03))), 2.35, 3.20)
        grab_rail(v, (-1.55, s * (h + 0.07), 1.45), (-1.55, s * (h + 0.07), 3.2), 0.018)
        grab_rail(v, (-0.45, s * (h + 0.07), 1.45), (-0.45, s * (h + 0.07), 3.2), 0.018)
        for y0, y1 in ((1.22, 1.40), (-1.40, -1.22)):
            if s == 1:
                gl.box(0.80, 0.82, y0, y1, 2.35, 3.35)
    v.A("floorw").box(-2.75, 0.75, -h + 0.08, h - 0.08, ze, ze + 0.02)
    v.A("grey").box(-2.6, -2.2, -1.1, 1.1, ze, ze + 1.15)
    v.A("black").box(-2.6, -2.3, -1.1, 1.1, ze + 1.15, ze + 1.20)
    v.A("moq2").box(-1.5, -1.1, 0.2, 0.7, ze, ze + 0.55)
    v.A("skin", 0.0, True).sphere((-1.3, 0.45, ze + 1.15), (0.1, 0.09, 0.11), seg=8, rings=6)
    v.A("cl1", 0.02, True).box(-1.45, -1.15, 0.28, 0.62, ze + 0.55, ze + 1.0)
    v.A("steel").cyl((-2.4, 0.0, ze + 1.2), (-2.4, 0.0, ze + 1.42), 0.03, 0.03, seg=6)
    v.A("lamp_in").cyl((-1.0, 0, 3.52), (-1.0, 0, 3.56), 0.12, 0.12, seg=10)
    # hood panels: louvres, doors, grilles
    def louver(x0, x1, z0, z1, s, yf):
        v.A("dark").box(x0, x1, *sorted((s * yf, s * (yf + 0.012))), z0, z1)
        nf = max(2, int((z1 - z0) / 0.075))
        for k in range(nf):
            zz = z0 + 0.03 + k * (z1 - z0 - 0.05) / nf
            v.A(body, 0.003).box(x0, x1, *sorted((s * (yf + 0.004), s * (yf + 0.055))), zz, zz + 0.028)
        for (xa, xb, za, zb) in ((x0 - 0.04, x0, z0 - 0.04, z1 + 0.04), (x1, x1 + 0.04, z0 - 0.04, z1 + 0.04),
                                 (x0 - 0.04, x1 + 0.04, z0 - 0.04, z0), (x0 - 0.04, x1 + 0.04, z1, z1 + 0.04)):
            v.A("grey", 0.003).box(xa, xb, *sorted((s * yf, s * (yf + 0.045))), za, zb)

    def hood_door(x0, x1, z0, z1, s, yf):
        for xx in (x0, x1):
            v.A("black").box(xx - 0.008, xx + 0.008, *sorted((s * yf, s * (yf + 0.014))), z0, z1)
        for zz in (z0, z1):
            v.A("black").box(x0, x1, *sorted((s * yf, s * (yf + 0.014))), zz - 0.008, zz + 0.008)
        v.A("steel").box(x1 - 0.14, x1 - 0.06, *sorted((s * (yf + 0.01), s * (yf + 0.05))), (z0 + z1) / 2 - 0.03, (z0 + z1) / 2 + 0.03)
        for zz in (z0 + 0.15, z1 - 0.15):
            v.A("iron").box(x0 + 0.01, x0 + 0.07, *sorted((s * (yf + 0.005), s * (yf + 0.04))), zz - 0.05, zz + 0.05)

    for s in (-1, 1):
        louver(1.25, 2.35, 1.95, 2.85, s, 1.18)
        hood_door(2.55, 3.65, 1.40, 2.95, s, 1.18) if False else None
        hood_door(2.55, 4.05, 1.80, 2.95, s, 1.18)
        louver(4.30, 6.0, 1.95, 2.85, s, 1.18)
        louver(-3.55, -2.95, 1.95, 2.45, s, 1.18)
        hood_door(-5.9, -4.0, 1.80, 2.50, s, 1.18)
        for xx in (1.0, 3.0, 5.4):                       # sand-box fillers / lift rings
            v.A("iron").torus((xx, s * 1.19, 1.62), 'y', 0.04, 0.008, segR=10, segr=4)
    v.A("black").cyl((5.2, 0, 3.28), (5.2, 0, 3.36), 0.78, 0.78, seg=24)
    v.A("dark").cyl((5.2, 0, 3.33), (5.2, 0, 3.37), 0.72, 0.72, seg=24)
    for i in range(10):
        a_ = i * math.pi / 5
        v.A("steel").cyl((5.2 + 0.72 * math.cos(a_), 0.72 * math.sin(a_), 3.375), (5.2 - 0.72 * math.cos(a_), -0.72 * math.sin(a_), 3.375), 0.010, 0.010, seg=4)
    for r_ in (0.2, 0.4, 0.6):
        v.A("steel").torus((5.2, 0, 3.375), 'z', r_, 0.008, segR=20, segr=4)
    v.A("black").cyl((5.2, 0, 3.34), (5.2, 0, 3.42), 0.09, 0.09, seg=8)
    v.A("black").cyl((2.0, 0.0, 3.25), (2.0, 0.0, 3.95), 0.13, 0.11, seg=10)
    v.A("dark").cyl((2.0, 0.0, 3.94), (2.0, 0.0, 3.96), 0.10, 0.10, seg=10)
    v.A("black").cyl((3.3, 0.0, 3.25), (3.3, 0.0, 3.62), 0.10, 0.10, seg=10)
    v.A("steel").cyl((0.1, 0.30, 3.98), (0.1, 0.30, 4.30), 0.035, 0.012, seg=8)            # air horns
    v.A("steel").cyl((0.1, -0.30, 3.98), (0.1, -0.30, 4.30), 0.035, 0.012, seg=8)
    v.A("grey", 0.01).box(-2.95, -2.78, -1.38, 1.38, 3.45, 3.55)                              # sun visor
    v.A("grey", 0.01).box(0.8, 0.98, -1.38, 1.38, 3.45, 3.55)
    for yc in (-0.6, 0.6):                                                                    # wipers
        v.A("steel").cyl((-2.835, yc, 2.98), (-2.835, yc - 0.3, 3.3), 0.008, 0.008, seg=4)
    # underframe equipment
    for s in (-1, 1):
        v.A("under", 0.01).box(-1.6, 1.0, *sorted((s * 1.15, s * 1.38)), 0.72, 1.20)         # battery boxes
        v.A("iron").box(-1.6 + 0.04, 1.0 - 0.04, *sorted((s * 1.38, s * 1.40)), 0.76, 1.16)
        v.A("steel").cyl((-1.7, s * 0.60, 0.70), (1.7, s * 0.60, 0.70), 0.17, 0.17, seg=12)  # air reservoirs
        v.A("steel").cyl((1.9, s * 0.45, 0.62), (4.0, s * 0.45, 0.62), 0.07, 0.07, seg=8) if False else None
        v.A("iron", 0.01).box(2.3, 3.0, *sorted((s * 0.9, s * 1.28)), 0.78, 1.18)            # sand boxes
        v.A("iron", 0.01).box(-3.0, -2.3, *sorted((s * 0.9, s * 1.28)), 0.78, 1.18)
    v.A("iron").cyl((-1.7, 0.0, 0.95), (1.9, 0.0, 0.95), 0.03, 0.03, seg=6)                   # brake pipe
    v.A("steel").cyl((0.0, 0.0, 0.50), (0.0, 0.0, 0.46), 0.1, 0.1, seg=8)
    v.A("black").cyl((0.0, -0.9, 0.49), (0.0, 0.9, 0.49), 0.045, 0.045, seg=8)               # fuel filler / gauge
    v.A("steel").cyl((0.6, 0.9, 0.55), (0.6, 0.98, 0.55), 0.06, 0.06, seg=8)
    # handrails along hoods
    for s in (-1, 1):
        for (a, b) in ((-6.0, -2.95), (0.95, 6.1)):
            n = int((b - a) / 1.2) + 1
            for i in range(n + 1):
                x = a + (b - a) * i / n
                grab_rail(v, (x, s * 1.40, ze), (x, s * 1.40, 2.0), 0.02, "iron")
            grab_rail(v, (a, s * 1.40, 2.0), (b, s * 1.40, 2.0), 0.02, "iron")
    # ends: beams, lamps, plates, couplers
    for e in (-1, 1):
        x0 = -6.2 if e < 0 else 6.3
        v.A("iron", 0.015).box(*sorted((e * 6.55, e * 6.85)), -1.4, 1.4, 0.92, 1.25)
        v.A("grey", 0.01).box(*sorted((e * 6.55, e * 6.9)), -1.45, 1.45, 1.22, 1.30)
        coupler(v, e, e * 6.85)
        for s in (-1, 1):
            v.A("lampglass").cyl((e * 6.88, s * 1.05, 1.12), (e * 6.93, s * 1.05, 1.12), 0.07, 0.07, seg=8)
            steps_down(v, e * 6.2, s, 1.18, ze, n=2, w=0.5)
    v.A("black", 0.01).box(-6.32, -6.2, -0.30, 0.30, 2.30, 2.62)                         # headlamp housing
    v.A("lampglass").cyl((-6.34, 0, 2.46), (-6.36, 0, 2.46), 0.14, 0.14, seg=14)
    v.A("black", 0.01).box(6.3, 6.4, -0.25, 0.25, 2.75, 3.05)
    v.A("lampglass").cyl((6.41, 0, 2.9), (6.43, 0, 2.9), 0.11, 0.11, seg=12)
    v.end_plane(plate, -1, 0.0, 0.52, 1.80, 2.01, -6.205)
    v.end_plane(plate, 1, 0.0, 0.52, 1.80, 2.01, 6.305)
    v.end_plane("headmark.png", 1, 0.0, 0.62, 2.12, 2.74, 6.31)
    v.end_plane("headmark.png", -1, 0.0, 0.50, 1.30, 1.80, -6.21)
    for s in (-1, 1):
        v.side_plane(plate, s, -1.0, 0.55, 1.78, 1.99, s * (h + 0.016))
        v.side_plane("logo_new.png", s, 3.35, 0.0 + 0.8, 1.08, 1.08 + 0.01, 0) if False else v.side_plane("logo_new.png", s, -4.55, 0.75, 1.80, 2.45, s * (1.18 + 0.011))
    gl_f = v.A("glass")
    gl_f.box(-2.83, -2.80, -1.2, 1.2, 2.95, 3.45)
    v.A("steel").cyl((-2.0, 0.0, 3.96), (-2.0, 0.0, 4.35), 0.012, 0.012, seg=4)
    for x in (-4.3, 4.3):
        bogie3(v, x)
    return v


# ====================================================================== freight
def freight_frame(v, L=8.8, W=2.6, r=0.43, wb=4.4):
    for x in (-wb / 2, wb / 2):
        wheelset(v, x, r)
        axle_box(v, x, 0.88, r)
    v.A("black", 0.01).box(-L / 2, L / 2, -1.2, 1.2, 0.76, 1.00)
    for s in (-1, 1):
        v.A("iron", 0.008).box(-L / 2 + 0.2, L / 2 - 0.2, s * 1.08 - 0.05, s * 1.08 + 0.05, 0.50, 1.00)
        for x in (-wb / 2, wb / 2):
            v.A("iron", 0.008).box(x - 0.1, x + 0.1, s * 0.95 - 0.04, s * 0.95 + 0.04, 0.55, 0.95)
            v.A("steel").box(x - 0.55, x + 0.55, s * 0.95 - 0.05, s * 0.95 + 0.05, 0.86, 0.90)       # leaf spring
        v.A("iron", 0.008).box(-L / 2 + 0.5, L / 2 - 0.5, s * 1.05 - 0.0, s * 1.05 + 0.12 * s, 0.98, 1.02)
    for e in (-1, 1):
        coupler(v, e, e * (L / 2 + 0.05), z=0.88)
        v.A("iron", 0.01).box(*sorted((e * (L / 2 - 0.1), e * (L / 2 + 0.08))), -1.15, 1.15, 0.80, 1.00)
        for s in (-1, 1):                                   # corner steps
            grab_rail(v, (e * (L / 2 - 0.35), s * 1.28, 0.55), (e * (L / 2 - 0.35), s * 1.28, 1.75), 0.018, "iron")
            v.A("iron", 0.004).box(e * (L / 2 - 0.35) - 0.12, e * (L / 2 - 0.35) + 0.12, s * 1.15, s * 1.3, 0.55, 0.58)


def make_wam(name="wam", mark="mark_wam.png", seed=3, open_door=0, load="sacks"):
    """Covered van. open_door=+1/-1 builds a hollow body with that side's sliding door opened, showing the load."""
    v = Veh(name)
    Lb, W = 7.9, 2.62
    freight_frame(v)
    if not open_door:
        v.A("wplank", 0.01).extrude_x(upper_profile(W, 1.0, 2.95, 3.42), -Lb / 2, Lb / 2)
    else:
        tw = 0.07
        for s in (-1, 1):
            ops = [(-0.95, 0.95, 1.12, 2.86)] if s == open_door else []
            wall_open(v, "wplank", 'y', -Lb / 2, Lb / 2, *sorted((s * W / 2, s * (W / 2 - tw))), 1.0, 2.95, ops, 0.004)
        for e in (-1, 1):
            v.A("wplank", 0.006).box(*sorted((e * Lb / 2, e * (Lb / 2 - tw))), -W / 2, W / 2, 1.0, 2.95)
        v.A("wplank", 0.01).extrude_x(upper_profile(W, 2.92, 2.95, 3.42), -Lb / 2, Lb / 2)
        v.A("floorw").box(-Lb / 2 + tw, Lb / 2 - tw, -W / 2 + tw, W / 2 - tw, 0.98, 1.04)
        # cross ribs inside + cargo
        for x in np.arange(-3.2, 3.3, 0.8):
            v.A("wagon2").box(x - 0.03, x + 0.03, -W / 2 + tw, W / 2 - tw, 2.88, 2.94)
        rnd0 = random.Random(seed + 9)
        if load == "sacks":
            for k in range(3):
                for i in range(5):
                    for j in range(2):
                        v.A("sack", 0.04).boxc(-3.0 + i * 0.58 + (0.28 if k % 2 else 0) + rnd0.uniform(-0.02, 0.02), -0.55 + j * 0.8 + rnd0.uniform(-0.04, 0.04) + 0.1 * open_door * 0, 1.2 + k * 0.30, 0.54, 0.74, 0.30)
            for k in range(2):
                for i in range(3):
                    v.A("sack", 0.04).boxc(2.0 + i * 0.5, 0.0 + 0.5 * (-open_door), 1.2 + k * 0.30, 0.46, 0.7, 0.30)
        else:
            for i in range(6):
                v.A("wood", 0.01).box(-3.2 + i * 0.5, -3.0 + i * 0.5, -0.9, 0.9, 1.04, 1.6)
        v.A("lamp_in").box(-0.2, 0.2, -0.2, 0.2, 2.88, 2.9)
        # the opened door leaf parked on the outside of the wall next to the opening
        y = open_door * (W / 2)
        v.A("wagon2", 0.006).box(0.95, 2.85, *sorted((y, y + open_door * 0.06)), 1.12, 2.86)
        for xx in (1.4, 1.9, 2.4):
            v.A("wagon", 0.003).box(xx - 0.01, xx + 0.01, *sorted((y + open_door * 0.06, y + open_door * 0.07)), 1.15, 2.83)
        v.A("iron", 0.005).box(-1.9, 1.9, *sorted((y + open_door * 0.01, y + open_door * 0.08)), 1.03, 1.08)
    rnd = random.Random(seed)
    for s in (-1, 1):
        y = s * (W / 2)
        for i in range(-5, 6):
            x = i * 0.66
            if abs(x) < 1.15:
                continue
            v.A("wagon2", 0.004).box(x - 0.04, x + 0.04, *sorted((y, y + s * 0.025)), 1.02, 2.93)
        for z in (1.05, 2.94):
            v.A("wagon2", 0.004).box(-Lb / 2, Lb / 2, *sorted((y, y + s * 0.03)), z - 0.04, z + 0.04)
        # door + rails
        if s != open_door:
            v.A("wagon2", 0.006).box(-0.95, 0.95, *sorted((y, y + s * 0.05)), 1.12, 2.86)
            for xx in (-0.47, 0.0, 0.47):
                v.A("wagon", 0.003).box(xx - 0.01, xx + 0.01, *sorted((y + s * 0.05, y + s * 0.06)), 1.15, 2.83)
            v.A("iron", 0.005).box(0.7, 0.9, *sorted((y + s * 0.05, y + s * 0.10)), 1.9, 2.0)         # door handle
        v.A("iron", 0.005).box(-1.9, 1.9, *sorted((y + s * 0.01, y + s * 0.08)), 2.97, 3.03)
        v.A("iron", 0.005).box(-1.9, 1.9, *sorted((y + s * 0.01, y + s * 0.08)), 1.03, 1.08)
        # small ventilation hatch
        v.A("black", 0.004).box(Lb / 2 - 0.75, Lb / 2 - 0.35, *sorted((y, y + s * 0.03)), 2.55, 2.75)
        v.side_plane(mark, s, -2.45, 1.15, 1.50, 1.50 + 1.15 / 2, y + s * 0.034)
        v.side_plane("logo_new.png", s, 2.55, 0.55, 1.62, 2.17, y + s * 0.034)
    roof_vents(v, [-2.4, 2.4], 3.38, key="wagon2")
    v.A("black", 0.004).box(-Lb / 2, Lb / 2, -0.05, 0.05, 3.40, 3.43)
    return v


def make_tora(name="tora", load="empty", seed=4):
    v = Veh(name)
    Lb, W = 7.9, 2.62
    freight_frame(v)
    zt = 1.98
    rnd = random.Random(seed)
    v.A("wood_dark", 0.004).box(-Lb / 2, Lb / 2, -W / 2, W / 2, 1.0, 1.07)
    for s in (-1, 1):
        y = s * (W / 2)
        v.A("wplank", 0.006).box(-Lb / 2, Lb / 2, *sorted((y - s * 0.06, y)), 1.07, zt)
        for i in range(-5, 6):
            v.A("wagon2", 0.004).box(i * 0.66 - 0.04, i * 0.66 + 0.04, *sorted((y, y + s * 0.03)), 1.05, zt + 0.02)
        v.A("iron", 0.004).box(-Lb / 2, Lb / 2, *sorted((y - s * 0.07, y + s * 0.04)), zt, zt + 0.05)
        for x in (-1.3, 1.3):
            v.A("iron", 0.004).box(x - 0.06, x + 0.06, *sorted((y + s * 0.0, y + s * 0.05)), 1.2, 1.9)
        v.A("wagon2", 0.003).box(-1.8, 1.8, *sorted((y, y + s * 0.045)), 1.12, 1.92)              # drop door
        v.side_plane("mark_tora.png", s, -2.6, 1.0, 1.2, 1.2 + 1.0 * 200 / 512, y + s * 0.034)
        v.side_plane("logo_new.png", s, 2.6, 0.5, 1.3, 1.8, y + s * 0.034)
    for e in (-1, 1):
        x = e * Lb / 2
        v.A("wplank", 0.006).box(*sorted((x, x - e * 0.07)), -W / 2, W / 2, 1.07, zt + 0.3)
        v.A("iron", 0.004).box(*sorted((x - e * 0.07, x + e * 0.03)), -W / 2, W / 2, zt + 0.3, zt + 0.35)
    if load == "rice":
        for k in range(3):
            for i in range(6):
                for j in range(3):
                    for y0 in (-1, 1):
                        x = -3.3 + i * 1.12 + rnd.uniform(-0.03, 0.03)
                        yy = y0 * (0.32 + j * 0.0) + rnd.uniform(-0.02, 0.02)
                        if k >= 2 and (i + j) % 2:
                            continue
                        if j > 0:
                            continue
                        v.A("sack", 0.06, True).boxc(x, yy - y0 * 0.0 + y0 * (0.34 if True else 0), 1.07 + 0.17 + k * 0.30, 0.95, 0.52, 0.3, rnd.uniform(-0.05, 0.05))
    elif load == "coal":
        for _ in range(26):
            v.A("coal", 0.0, True).sphere((rnd.uniform(-3.1, 3.1), rnd.uniform(-0.8, 0.8), rnd.uniform(1.75, 2.0)),
                                           (rnd.uniform(0.5, 0.9), rnd.uniform(0.45, 0.7), rnd.uniform(0.3, 0.45)), seg=8, rings=5)
        v.A("coal").box(-3.7, 3.7, -1.2, 1.2, 1.07, 1.7)
    elif load == "tarp":
        v.A("wood_dark", 0.02).box(-3.3, 3.3, -1.0, 1.0, 1.07, 1.9)
        v.A("tarp", 0.03, True).extrude_x([(-1.38, zt - 0.1), (1.38, zt - 0.1), (1.30, 2.45), (0.7, 2.85), (-0.7, 2.85), (-1.30, 2.45)], -3.5, 3.5)
        for x in np.arange(-3.0, 3.1, 1.0):
            v.A("tarp2").extrude_x([(-1.385, zt - 0.1), (-1.3, 2.45), (-0.7, 2.855), (0.7, 2.855), (1.3, 2.45), (1.385, zt - 0.1),
                                    (1.39, zt - 0.1), (1.31, 2.46), (0.7, 2.87), (-0.7, 2.87), (-1.31, 2.46), (-1.39, zt - 0.1)], x - 0.02, x + 0.02)
    return v


def make_yo(name="yo", seed=5):
    v = Veh(name)
    Lb, W = 6.4, 2.50
    freight_frame(v, L=6.8, W=W, wb=3.6)
    v.A("black", 0.01).box(-3.4, 3.4, -1.2, 1.2, 0.98, 1.06)
    v.A("wagon2", 0.012).extrude_x(upper_profile(W, 1.06, 2.75, 3.15, n=4), -1.7, 1.7)
    v.A("roof", 0.01).box(-1.8, 1.8, -1.05, 1.05, 3.12, 3.18)
    v.A("wagon2", 0.01).box(-0.9, 0.9, -0.85, 0.85, 3.15, 3.80)                                 # cupola
    v.A("roof", 0.01).box(-1.0, 1.0, -0.95, 0.95, 3.80, 3.88)
    gl = v.A("glass")
    for s in (-1, 1):
        gl.box(-0.75, 0.75, *sorted((s * 0.85, s * 0.862)), 3.35, 3.72)
        for xs in (-1.1, 0.45):
            gl.box(xs, xs + 0.65, *sorted((s * W / 2, s * (W / 2 + 0.012))), 1.9, 2.5)
    for e in (-1, 1):
        gl.box(*sorted((e * 0.9, e * 0.912)), -0.55, 0.55, 3.35, 3.72)
        gl.box(*sorted((e * 1.7, e * 1.712)), -0.45, 0.45, 1.95, 2.55)
        v.A("wagon2", 0.006).box(*sorted((e * 1.7, e * 1.72)), -0.55, 0.55, 1.1, 2.8)
        # end platform + railings
        v.A("wood_dark", 0.006).box(*sorted((e * 1.7, e * 3.2)), -1.2, 1.2, 1.0, 1.07)
        for s in (-1, 1):
            grab_rail(v, (e * 3.15, s * 1.15, 1.07), (e * 3.15, s * 1.15, 2.1), 0.022, "iron")
            grab_rail(v, (e * 1.75, s * 1.15, 1.07), (e * 1.75, s * 1.15, 2.1), 0.022, "iron")
            grab_rail(v, (e * 1.75, s * 1.15, 2.08), (e * 3.15, s * 1.15, 2.08), 0.02, "iron")
            grab_rail(v, (e * 1.75, s * 1.15, 1.55), (e * 3.15, s * 1.15, 1.55), 0.02, "iron")
        grab_rail(v, (e * 3.15, -1.15, 2.08), (e * 3.15, 1.15, 2.08), 0.02, "iron")
    v.A("black").cyl((0.9, 0.5, 3.1), (0.9, 0.5, 3.75), 0.07, 0.08, seg=8)
    for s in (-1, 1):
        v.side_plane("mark_yo.png", s, -0.2, 0.7, 1.28, 1.28 + 0.28, s * (W / 2 + 0.014))
        v.side_plane("logo_new.png", s, 0.9, 0.44, 1.2, 1.64, s * (W / 2 + 0.014))
    return v


# ====================================================================== placement at the station
def build_train():
    """Five vehicle types standing at the station tracks."""
    # T1: railcar at the platform
    make_kiha("kiha_A").place(12.0, T1, 0.0)
    # T2: loco (long hood west) + three old coaches along the island platform
    import diesel2
    diesel2.make_dd51("loco_dd", hm_holder=True).place(-33.0, T2, math.pi)
    import vehtypes
    xs = -26.6 + 1.0
    for i, (t_, ends) in enumerate((("sl_gen", ("gang", "gang")), ("sl_b", ("gang", "gang")), ("sl_din", ("gang", "gang")),
                                    ("sl_a", ("gang", "gang")), ("sl_b", ("gang", "tail")))):     # 寝台特急「ほなみ」(NT1)
        L = vehtypes.TYPES[t_]["L"]
        vehtypes.make(t_, f"sleeper{i}", seed=10 + i, ends=ends).place(xs + L / 2, T2, 0.0)
        xs += L + 0.55
    # T3: mixed freight
    x = -14.45
    for i, f in enumerate(("wam", "tora_rice", "wam", "wam", "tora_coal")):
        v = make_wam(f"wamT3_{i}", seed=i, open_door=({0: 1, 2: 1, 3: -1}.get(i, 0)), load=("sacks" if i != 3 else "logs")) if f == "wam" else make_tora(f"toraT3_{i}", f.split("_")[1], seed=i)
        v.place(x, T3, 0.0 if i % 2 == 0 else math.pi)
        x += 9.9
    # T4: siding stock + brake van at the buffer stops
    for i, (x, f) in enumerate(((6.0, "tora_rice"), (15.9, "wam"), (25.8, "tora_tarp"))):
        v = make_wam(f"wamT4_{i}", seed=20 + i) if f == "wam" else make_tora(f"toraT4_{i}", f.split("_")[1], seed=20 + i)
        v.place(x, T4, 0.0)
    make_yo("yoT4").place(47.5, T4, math.pi)
    # D10: 第5線(貨車の留置)と第6線(客車の留置)
    for i, (x, f) in enumerate(((31.0, "wam"), (40.9, "tora_coal"), (50.8, "wam"), (60.7, "tora_rice"))):
        v = make_wam(f"wamT5_{i}", seed=40 + i) if f == "wam" else make_tora(f"toraT5_{i}", f.split("_")[1], seed=40 + i)
        v.place(x, T5, 0.0)
    for w_ in range(2):
        make_coach(f"coachT6_{w_}", variant=w_, seed=60 + w_).place(54.0 + w_ * 20.6, T6, math.pi)


def build_vehicles():
    pass


def export_rig(path):
    """シーン内の全車両のリグ構造とメタデータをJSONに出す(運転システム用)。"""
    import json, bpy
    out = []
    for ob in bpy.data.objects:
        if not ob.get("rig_root"):
            continue
        parts = []
        stack = list(ob.children)
        while stack:
            c = stack.pop()
            if c.get("rig_kind"):
                parts.append(dict(name=c.name, kind=c["rig_kind"], axis=c["rig_axis"], parent=c.parent.name, local_origin=[round(v, 3) for v in c.location],
                                  radius=c.get("rig_radius")))
            stack.extend(c.children)
        meta = json.loads(ob["rig_meta"])
        out.append(dict(name=ob.name, location=[round(v, 3) for v in ob.location], yaw=round(ob.rotation_euler[2], 4), parts=sorted(parts, key=lambda p: p["name"]), **meta))
    json.dump(dict(convention="車両ルート空オブジェクト>台車(bogie,z軸)>輪軸(ws,y軸)・連結器(coupler,z軸)。原点=回転中心。レール上面=ローカルz0。", vehicles=out), open(path, "w"), ensure_ascii=False, indent=1)
    return len(out)


def make_plow(name="plow", seed=7):
    """除雪車(ラッセル式・汎用): 運転室つき車体+V字の雪かき翼(公開の一般的な形を参考にした汎用モデル。実在形式の寸法ではない)。
    +x 端が前(雪かき側)。主翼=平面V字の傾斜板2枚+中央の鼻、上部の雪切り板、下端のフランジ刃。"""
    rnd = random.Random(seed)
    v = Veh(name)
    L, W = 10.6, 2.70
    freight_frame(v, L=L, W=W, wb=5.8)
    red = "post_red"
    v.A("black", 0.01).box(-L / 2, L / 2, -1.2, 1.2, 0.98, 1.06)
    # 運転室(後半): 高い箱形+切妻風の屋根+窓
    v.A(red, 0.02).box(-4.9, 1.6, -W / 2, W / 2, 1.06, 3.55)
    v.A("roof", 0.015).box(-5.0, 1.7, -W / 2 - 0.08, W / 2 + 0.08, 3.55, 3.65)
    v.A("iron", 0.01).box(-1.9, -1.3, -0.45, 0.45, 3.65, 4.35)                     # 煙突/換気塔
    gl = v.A("glass")
    for s in (-1, 1):
        for xs in (-4.3, -3.2, -2.1, -0.9):
            v.A("wood_dark", 0.01).box(xs - 0.06, xs + 0.81, *sorted((s * W / 2, s * (W / 2 + 0.02))), 2.04, 3.06)       # 窓枠
            v.A("cream", 0.0).box(xs, xs + 0.75, *sorted((s * (W / 2 - 0.02), s * (W / 2 + 0.014))), 2.1, 3.0) if "cream" in M else None   # 室内側の明るい壁
            gl.box(xs, xs + 0.75, *sorted((s * (W / 2 + 0.014), s * (W / 2 + 0.03))), 2.1, 3.0)
    gl.box(1.6, 1.612, -1.0, 1.0, 2.3, 3.1)                                         # 前面窓(翼の後ろ)
    # 前部: 排土板(V字)。後端 x=1.6 から先端 x=5.6 へ
    for s in (-1, 1):
        v.A(red, 0.02).sbox((1.6, s * 1.35, 2.1), (5.5, s * 0.12, 1.75), 0.10, 2.15, up=(0, 0, 1))     # 主翼(縦板)
        v.A("iron", 0.01).sbox((1.6, s * 1.35, 3.18), (5.4, s * 0.12, 2.82), 0.12, 0.30, up=(0, 0, 1))  # 上縁補強帯
        v.A("steel").box(1.6, 5.5, *sorted((s * 1.33, s * 0.12)), 0.99, 1.03) if False else None
    v.A("steel", 0.01).sbox((1.6, -1.40, 1.00), (5.5, 0.0, 0.88), 0.06, 0.16, up=(0, 0, 1))     # フランジ刃(左)
    v.A("steel", 0.01).sbox((1.6, 1.40, 1.00), (5.5, 0.0, 0.88), 0.06, 0.16, up=(0, 0, 1))      # フランジ刃(右)
    v.A(red, 0.02).box(5.1, 5.7, -0.22, 0.22, 0.9, 2.55)                                        # 中央の鼻
    v.A("iron", 0.01).box(5.7, 5.8, -0.22, 0.22, 0.9, 2.55)
    for s in (-1, 1):                                                                           # 側面の手すり・梯子
        grab_rail(v, (-4.6, s * (W / 2 + 0.05), 1.1), (-4.6, s * (W / 2 + 0.05), 3.4), 0.02, "iron")
        v.A("iron", 0.004).box(-4.75, -4.45, *sorted((s * W / 2, s * (W / 2 + 0.2))), 1.1, 1.14)
    v.side_plane("logo_new.png", 1, -2.0, 0.5, 1.4, 1.9, W / 2 + 0.012) if hasattr(v, "side_plane") else None
    return v
