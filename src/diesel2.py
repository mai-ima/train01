"""Realistic-leaning diesel locomotives: a DD51-type (B-2-B, centre cab, two equal hoods, radiators at the hood ends) and a
DE10-type (1B-B1, semi-centre cab, long hood + short hood).  Generic geometry; no real markings.
Local frame: +x = front (long hood / 1-end), z = 0 at rail-head top."""
from trainkit import *


def hood(v, body, top, x0, x1, w, z0, zt, shoulder=0.42, chamfer=0.17):
    zs = zt - shoulder
    v.A(body, 0.012).extrude_x([(-w / 2, z0), (w / 2, z0), (w / 2, zs), (-w / 2, zs)], x0, x1)
    v.A(top, 0.014).extrude_x([(-w / 2 - 0.012, zs), (w / 2 + 0.012, zs), (w / 2 - chamfer, zt), (-w / 2 + chamfer, zt)], x0, x1)


def louvers(v, x0, x1, y, side, z0, z1, n=10, slat="gtop"):
    v.A("dark").box(x0, x1, *sorted((side * (y - 0.01), side * (y + 0.018))), z0, z1)
    for i in range(n):
        z = z0 + (z1 - z0) * (i + 0.5) / n
        v.A(slat, 0.002).box(x0 + 0.03, x1 - 0.03, *sorted((side * (y + 0.005), side * (y + 0.05))), z - 0.014, z + 0.01)
    t = 0.025
    for (a, b, c_, d) in ((x0, x1, z0 - t, z0), (x0, x1, z1, z1 + t), (x0 - t, x0, z0 - t, z1 + t), (x1, x1 + t, z0 - t, z1 + t)):
        v.A("gtop", 0.002).box(a, b, *sorted((side * (y - 0.01), side * (y + 0.04))), c_, d)


def door_panel(v, x0, x1, y, side, z0, z1, handle="left"):
    t = 0.012
    for (a, b, c_, d) in ((x0, x1, z0, z0 + t), (x0, x1, z1 - t, z1), (x0, x0 + t, z0, z1), (x1 - t, x1, z0, z1)):
        v.A("under").box(a, b, *sorted((side * y, side * (y + 0.012))), c_, d)
    hx = x0 + 0.1 if handle == "left" else x1 - 0.1
    v.A("steel", 0.003).box(hx - 0.025, hx + 0.025, *sorted((side * (y + 0.005), side * (y + 0.05))), (z0 + z1) / 2 - 0.08, (z0 + z1) / 2 + 0.08)


def lamp(v, x, y, z, e, r=0.12):
    """Sealed-beam headlight with rim, facing +x (e=1) or -x (e=-1)."""
    v.A("dark").cyl((x, y, z), (x + e * 0.03, y, z), r + 0.02, r + 0.02, seg=20)
    v.A("lampglass").cyl((x + e * 0.03, y, z), (x + e * 0.05, y, z), r, r * 0.92, seg=20)
    v.A("steel").torus((x + e * 0.03, y, z), 'x', r + 0.025, 0.012, segR=20, segr=4)


def end_gear(v, e, x_beam, W, plate, z_deck):
    """End beam, couplers, hoses, steps, ladders, lamps, plates at the loco end e."""
    v.A("iron", 0.015).box(*sorted((e * (x_beam - 0.22), e * (x_beam + 0.12))), -1.40, 1.40, 0.95, z_deck - 0.02)
    v.A("verm", 0.01).box(*sorted((e * (x_beam + 0.0), e * (x_beam + 0.14))), -1.40, 1.40, 1.18, z_deck + 0.04) if False else None
    coupler(v, e, e * (x_beam + 0.12), z=0.88)
    for s in (-1, 1):
        v.A("rubber").cyl((e * (x_beam + 0.1), s * 0.55, 1.1), (e * (x_beam + 0.22), s * 0.55, 0.85), 0.03, 0.03, seg=6)
        v.A("rubber").cyl((e * (x_beam + 0.1), s * 0.70, 1.1), (e * (x_beam + 0.22), s * 0.70, 0.85), 0.03, 0.03, seg=6)
        v.A("steel", 0.003).box(*sorted((e * (x_beam + 0.12), e * (x_beam + 0.2))), s * 1.1 - 0.05, s * 1.1 + 0.05, 1.05, 1.15)    # jumper box
        # steps down from the deck at the corners + grab rails
        for k in range(2):
            v.A("iron", 0.004).box(*sorted((e * (x_beam - 0.5), e * (x_beam - 0.1))), *sorted((s * 1.33, s * 1.55)), 0.62 + 0.30 * k, 0.65 + 0.30 * k)
        grab_rail(v, (e * (x_beam - 0.12), s * 1.38, 0.6), (e * (x_beam - 0.12), s * 1.38, z_deck + 0.7), 0.02, "steel")
        v.A("lampglass").cyl((e * (x_beam + 0.0), s * 1.18, 1.35), (e * (x_beam + 0.04), s * 1.18, 1.35), 0.05, 0.05, seg=10)   # tail lamps


# ====================================================================== DD51-type
def make_dd51(name="dd51", body="verm", top="gtop", band="cream2", plate="plate_dd.png"):
    v = Veh(name)
    zd = 1.32
    Wc, Wh = 2.95, 2.70
    xc = 1.70
    xh = 6.78
    # frame, tanks, deck
    v.A("under", 0.012).box(-6.95, 6.95, -1.38, 1.38, 1.05, zd)
    v.A("under", 0.012).box(-2.5, 2.5, -0.95, 0.95, 0.52, 1.05)                           # fuel tank
    v.A("steel").cyl((-1.8, -1.05, 0.7), (1.8, -1.05, 0.7), 0.20, 0.20, seg=14)             # air reservoirs
    v.A("steel").cyl((-1.8, 1.05, 0.7), (1.8, 1.05, 0.7), 0.20, 0.20, seg=14)
    v.A("gtop", 0.008).box(-6.95, 6.95, -1.45, 1.45, zd - 0.05, zd)
    # hoods (identical, mirrored)
    for e in (-1, 1):
        xa, xb = sorted((e * xc, e * xh))
        hood(v, body, top, xa, xb, Wh, zd, 3.32)
        # front face details
        xf = e * xh
        v.A(body, 0.01).box(*sorted((xf, xf + e * 0.04)), -Wh / 2 + 0.05, Wh / 2 - 0.05, zd + 0.1, 3.0)
        for s in (-1, 1):
            lamp(v, xf + e * 0.04, s * 0.72, 3.02, e, 0.12)
            v.A("lampglass").cyl((xf + e * 0.04, s * 1.0, 1.75), (xf + e * 0.06, s * 1.0, 1.75), 0.06, 0.06, seg=10)
        v.end_plane(plate, e, 0.0, 0.62, 2.55, 2.55 + 0.62 * 160 / 420, xf + e * 0.045)
        v.A("white" if band == "white" else band, 0.004).box(*sorted((xf, xf + e * 0.045)), -Wh / 2 + 0.04, Wh / 2 - 0.04, 1.55, 1.78)   # front band
        # side details: radiator + fan at the outer end, engine doors in the middle
        for s in (-1, 1):
            louvers(v, *sorted((e * (xh - 2.25), e * (xh - 0.35))), Wh / 2, s, 1.55, 3.0, n=12)
            for (a, b) in ((2.05, 3.05), (3.2, 4.2)):
                door_panel(v, *sorted((e * a, e * b)), Wh / 2, s, 1.65, 2.95, "left" if e * s > 0 else "right")
            v.A(band, 0.003).box(*sorted((e * xc, e * xh)), *sorted((s * (Wh / 2 + 0.006), s * (Wh / 2 + 0.014))), 1.46, 1.54)        # cream line
            for xx in np.arange(e * (xc + 0.4), e * (xh - 0.3), e * 1.3):
                v.A("steel").cyl((xx, s * (Wh / 2 + 0.01), 2.35), (xx, s * (Wh / 2 + 0.07), 2.35), 0.012, 0.012, seg=5)
            grab_rail(v, (e * (xc + 0.15), s * (Wh / 2 + 0.07), 2.35), (e * (xh - 0.4), s * (Wh / 2 + 0.07), 2.35), 0.016, "steel")
        # roof fan above the radiator, exhaust stacks near the cab
        fx = e * (xh - 1.3)
        v.A("gtop", 0.01).cyl((fx, 0, 3.30), (fx, 0, 3.38), 0.66, 0.62, seg=28)
        v.A("dark").cyl((fx, 0, 3.375), (fx, 0, 3.395), 0.54, 0.54, seg=28)
        for k in range(5):
            v.A("steel").box(fx - 0.5, fx + 0.5, -0.012 + (k - 2) * 0.2, 0.012 + (k - 2) * 0.2, 3.39, 3.41)
        v.A("steel").torus((fx, 0, 3.39), 'z', 0.5, 0.012, segR=24, segr=4)
        for yy in (-0.5, 0.5):
            v.A("black").cyl((e * (xc + 0.9), yy, 3.3), (e * (xc + 0.9), yy, 3.75), 0.11, 0.09, seg=10)
        end_gear(v, e, 6.95, Wh, plate, zd)
    # cab
    hc = Wc / 2
    t_ = 0.08
    for s in (-1, 1):
        wall_open(v, body, 'y', -xc, xc, s * (hc - t_), s * hc, zd, 3.10,
                  [(-1.55, -0.78, 2.15, 2.95), (-0.62, 0.30, 2.15, 2.95), (0.62, 1.55, 2.15, 2.95)], 0.008)
        v.A(top, 0.006).box(-xc, xc, *sorted((s * (hc - t_), s * (hc + 0.012))), 2.95, 3.10)
        for (a, b, door) in ((-1.55, -0.78, 0), (-0.62, 0.30, 1), (0.62, 1.55, 0)):
            v.A("glass").box(a + 0.02, b - 0.02, *sorted((s * (hc - 0.05), s * (hc - 0.045))), 2.17, 2.93)
            v.A("steel", 0.002).box(a - 0.03, b + 0.03, *sorted((s * (hc - t_), s * (hc + 0.014))), 2.95, 2.99)
            v.A("steel", 0.002).box(a - 0.03, b + 0.03, *sorted((s * (hc - t_), s * (hc + 0.014))), 2.12, 2.16)
        door_panel(v, -0.70, 0.40, hc, s, zd + 0.05, 3.0, "right")
        grab_rail(v, (-0.72, s * (hc + 0.06), 1.4), (-0.72, s * (hc + 0.06), 2.9), 0.02, "steel")
        grab_rail(v, (0.42, s * (hc + 0.06), 1.4), (0.42, s * (hc + 0.06), 2.9), 0.02, "steel")
        for k in range(3):
            v.A("iron", 0.004).box(-0.7, 0.4, *sorted((s * (hc - 0.02), s * (hc + 0.25))), 0.6 + 0.24 * k, 0.63 + 0.24 * k)
            v.A("iron", 0.004).box(-0.7, 0.4, *sorted((s * (hc - 0.02), s * (hc + 0.25))), 0.6 + 0.24 * k, 0.63 + 0.24 * k) if False else None
        v.A(band, 0.003).box(-xc, xc, *sorted((s * (hc + 0.004), s * (hc + 0.012))), 1.46, 1.54)
        v.side_plane(plate, s, 1.2, 0.5, 1.7, 1.7 + 0.5 * 160 / 420, s * (hc + 0.014)) if False else None
        v.side_plane("logo_new.png", s, 3.6, 0.9, 1.9, 2.8, s * (Wh / 2 + 0.014))
        v.side_plane("logo_new.png", s, -3.6, 0.9, 1.9, 2.8, s * (Wh / 2 + 0.014))
        v.side_plane(plate, s, -1.15, 0.5, 1.58, 1.58 + 0.5 * 160 / 420, s * (hc + 0.014))
    for e in (-1, 1):
        wall_open(v, body, 'x', -hc, hc, *sorted((e * xc, e * (xc - t_))), zd, 3.10,
                  [(1.1, 1.40, 2.25, 3.05), (-1.40, -1.10, 2.25, 3.05)], 0.008)
        for yy in (-1.25, 1.25):
            v.A("glass").box(*sorted((e * (xc - 0.045), e * (xc - 0.05))), yy - 0.15, yy + 0.15, 2.27, 3.03)
    v.A("floorw").box(-xc, xc, -hc + 0.08, hc - 0.08, zd, zd + 0.02)
    v.A(top, 0.016).extrude_x(upper_profile(Wc + 0.28, 3.06, 3.12, 3.96, n=8), -xc - 0.2, xc + 0.2)       # roof with eaves
    for xx in (-0.7, 0.7):
        v.A(top, 0.01).cyl((xx, 0, 3.92), (xx, 0, 4.06), 0.33, 0.30, seg=20)                              # two ceiling-fan bumps
    v.A("steel").box(-0.5, 0.5, -0.5, 0.5, 4.05, 4.07) if False else None
    # cab interior
    v.A("gtop").box(-1.62, -1.2, -1.2, 1.2, zd + 0.02, zd + 1.05)
    v.A("black").box(-1.62, -1.2, -1.2, 1.2, zd + 1.05, zd + 1.12)
    import cabkit
    cabkit.stand(v, -1.2, +1, zd, hw=1.0, y_seat=-0.62)
    v.A("gtop").box(1.2, 1.62, -1.2, 1.2, zd + 0.02, zd + 1.05)
    v.A("black").box(1.2, 1.62, -1.2, 1.2, zd + 1.05, zd + 1.12)
    cabkit.stand(v, 1.2, -1, zd, hw=1.0, y_seat=0.62, driver=False)
    v.A("lamp_in").box(-0.4, 0.4, -0.3, 0.3, 3.05, 3.07)
    # bogies: two powered two-axle trucks + centre idler truck (B-2-B)
    for x in (-4.9, 4.9):
        bogie2(v, x, wb=2.4, r=0.5)
    bogie2(v, 0.0, wb=1.8, r=0.43)
    for x in (-4.9, 4.9):
        for s in (-1, 1):
            v.A("steel").box(x - 0.9, x + 0.9, *sorted((s * 0.99, s * 1.01)), 0.3, 0.38)                  # sand pipe / brake detail
    return v


# ====================================================================== DE10-type
def make_de10(name="de10", body="verm", top="gtop", band="white", plate="plate_dd.png"):
    v = Veh(name)
    zd = 1.26
    Wc, Wl = 2.80, 2.50
    xa, xb = -2.05, 0.95            # cab limits
    xl, xs = 6.55, -5.75            # long / short hood ends
    v.A("under", 0.012).box(-6.8, 6.8, -1.30, 1.30, 0.98, zd)
    v.A("under", 0.012).box(-2.3, 2.3, -0.9, 0.9, 0.50, 0.98)
    v.A("gtop", 0.008).box(-6.8, 6.8, -1.40, 1.40, zd - 0.05, zd)
    hood(v, body, top, xb, xl, Wl, zd, 3.30)                            # long hood
    hood(v, body, top, xs, xa, Wl - 0.1, zd, 2.92, shoulder=0.35)       # short hood
    hc = Wc / 2
    t_ = 0.08
    # long-hood details
    for s in (-1, 1):
        louvers(v, xl - 2.2, xl - 0.3, Wl / 2, s, 1.5, 3.0, n=11)
        for (a, b) in ((xb + 0.35, xb + 1.6), (xb + 1.75, xb + 3.0)):
            door_panel(v, a, b, Wl / 2, s, 1.6, 2.9, "left" if s > 0 else "right")
        v.A(band, 0.003).box(xs, xl, *sorted((s * (Wl / 2 + 0.006), s * (Wl / 2 + 0.014))), 1.46, 1.58)
        louvers(v, xs + 0.4, xs + 2.1, (Wl - 0.1) / 2, s, 1.5, 2.55, n=8)
        grab_rail(v, (xb + 0.2, s * (Wl / 2 + 0.07), 2.35), (xl - 0.4, s * (Wl / 2 + 0.07), 2.35), 0.016, "steel")
        for xx in np.arange(xb + 0.5, xl - 0.3, 1.4):
            v.A("steel").cyl((xx, s * (Wl / 2 + 0.01), 2.35), (xx, s * (Wl / 2 + 0.07), 2.35), 0.012, 0.012, seg=5)
    v.A("gtop", 0.01).cyl((xl - 1.3, 0, 3.28), (xl - 1.3, 0, 3.36), 0.64, 0.6, seg=28)                     # radiator fan
    v.A("dark").cyl((xl - 1.3, 0, 3.355), (xl - 1.3, 0, 3.375), 0.52, 0.52, seg=28)
    v.A("steel").torus((xl - 1.3, 0, 3.37), 'z', 0.48, 0.012, segR=24, segr=4)
    v.A("black").cyl((xb + 0.7, 0, 3.28), (xb + 0.7, 0, 3.85), 0.12, 0.10, seg=10)                         # engine exhaust
    v.A("black").cyl((xs + 0.9, 0.0, 2.9), (xs + 0.9, 0.0, 3.35), 0.10, 0.08, seg=10)                      # SG exhaust
    # cab: walls, windows, roof
    for s in (-1, 1):
        wall_open(v, body, 'y', xa, xb, s * (hc - t_), s * hc, zd, 3.10, [(xa + 0.15, xa + 0.95, 2.15, 3.0), (xb - 1.05, xb - 0.2, 2.15, 3.0)], 0.008)
        v.A(top, 0.006).box(xa, xb, *sorted((s * (hc - t_), s * (hc + 0.012))), 3.0, 3.10)
        for (a, b) in ((xa + 0.15, xa + 0.95), (xb - 1.05, xb - 0.2)):
            v.A("glass").box(a + 0.02, b - 0.02, *sorted((s * (hc - 0.05), s * (hc - 0.045))), 2.17, 2.98)
            v.A("steel", 0.002).box(a - 0.03, b + 0.03, *sorted((s * (hc - t_), s * (hc + 0.014))), 3.0, 3.04)
            v.A("steel", 0.002).box(a - 0.03, b + 0.03, *sorted((s * (hc - t_), s * (hc + 0.014))), 2.12, 2.16)
        door_panel(v, xa + 1.1, xa + 1.95, hc, s, zd + 0.05, 3.05, "right")
        v.A("glass").box(xa + 1.2, xa + 1.85, *sorted((s * (hc + 0.002), s * (hc + 0.012))), 2.25, 2.95)
        grab_rail(v, (xa + 1.05, s * (hc + 0.06), 1.4), (xa + 1.05, s * (hc + 0.06), 2.9), 0.02, "steel")
        grab_rail(v, (xa + 2.0, s * (hc + 0.06), 1.4), (xa + 2.0, s * (hc + 0.06), 2.9), 0.02, "steel")
        for k in range(3):
            v.A("iron", 0.004).box(xa + 1.1, xa + 1.95, *sorted((s * (hc - 0.02), s * (hc + 0.25))), 0.6 + 0.24 * k, 0.63 + 0.24 * k)
        v.A(band, 0.003).box(xa, xb, *sorted((s * (hc + 0.004), s * (hc + 0.012))), 1.46, 1.58)
        v.side_plane(plate, s, xa + 0.55, 0.5, 1.64, 1.64 + 0.5 * 160 / 420, s * (hc + 0.014))
        v.side_plane("logo_new.png", s, xl - 3.9, 0.9, 1.9, 2.8, s * (Wl / 2 + 0.014))
    for (xe, e) in ((xa, -1), (xb, 1)):
        wall_open(v, body, 'x', -hc, hc, *sorted((xe, xe - e * t_)), zd, 3.10, [(1.05, 1.35, 2.25, 3.05), (-1.35, -1.05, 2.25, 3.05)], 0.008)
        for yy in (-1.2, 1.2):
            v.A("glass").box(*sorted((xe - e * 0.045, xe - e * 0.05)), yy - 0.15, yy + 0.15, 2.27, 3.03)
    v.A("floorw").box(xa, xb, -hc + 0.08, hc - 0.08, zd, zd + 0.02)
    v.A(top, 0.016).extrude_x(upper_profile(Wc + 0.24, 3.06, 3.12, 3.88, n=8), xa - 0.15, xb + 0.15)
    v.A(top, 0.01).cyl((xa + 1.5, 0, 3.84), (xa + 1.5, 0, 3.98), 0.30, 0.27, seg=20)
    v.A("gtop", 0.01).box(xa + 0.2, xa + 0.5, -0.9, 0.9, 3.84, 3.98)                                     # roof vent
    v.A("gtop").box(xa + 0.1, xa + 0.5, -1.15, 1.15, zd + 0.02, zd + 1.0)
    import cabkit
    v.A("black").box(xa + 0.1, xa + 0.5, -1.15, 1.15, zd + 1.0, zd + 1.06)
    cabkit.stand(v, xa + 0.5, +1, zd, hw=1.05, y_seat=-0.55, z_con=1.0)
    v.A("moq2").box(xb - 0.7, xb - 0.2, 0.1, 0.6, zd + 0.02, zd + 0.5)
    v.A("moq2", 0.03).box(xb - 0.3, xb - 0.2, 0.1, 0.6, zd + 0.5, zd + 1.0)
    v.A("lamp_in").box(xa + 0.8, xb - 0.8, -0.3, 0.3, 3.05, 3.07)
    # ends
    for (xe, e, wh, zt, nm) in ((xl, 1, Wl, 3.30, "L"), (xs, -1, Wl - 0.1, 2.92, "S")):
        xf = xe
        v.A(body, 0.01).box(*sorted((xf, xf + e * 0.04)), -wh / 2 + 0.05, wh / 2 - 0.05, zd + 0.1, zt - 0.3)
        for s in (-1, 1):
            lamp(v, xf + e * 0.04, s * 0.66, zt - 0.38, e, 0.115)
        v.end_plane(plate, e, 0.0, 0.6, zt - 1.05, zt - 1.05 + 0.6 * 160 / 420, xf + e * 0.045)
        v.A(band, 0.004).box(*sorted((xf, xf + e * 0.045)), -wh / 2 + 0.04, wh / 2 - 0.04, 1.5, 1.72)
        end_gear(v, e, 6.8, wh, plate, zd)
    # bogies: two three-axle trucks (idler + two powered axles)
    for x in (-4.0, 4.0):
        bogie3(v, x, wb=1.8)
    return v
