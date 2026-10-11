"""Driver's stand + seated driver for diesel cabs (generic, original design).  Uses trainkit.Veh materials."""
import math
import numpy as np


def stand(v, xb, d, zd, hw=0.95, y_seat=-0.65, driver=True, z_con=1.12):
    """xb: x of the console's inner (driver-side) edge; d=+1 when the driver sits at larger x than the console.
    Builds a sloped instrument panel with gauges, controller + brake handles, seat, optional seated driver."""
    X = lambda u: xb + d * u
    zc = zd + z_con
    # sloped panel (extrude along y)
    prof = [(X(-0.40), zc), (X(0.06), zc), (X(0.06), zc + 0.10), (X(-0.40), zc + 0.32)]
    v.A("gtop", 0.006).extrude_y(prof, -hw, hw)
    # gauges: two rows
    rng = np.random.default_rng(int(abs(xb) * 100) + 3)
    for row, (u, zz) in enumerate(((-0.12, zc + 0.20), (-0.27, zc + 0.27))):
        for k in range(6):
            y = -0.8 + k * 0.32 + (0.16 if row else 0.0)
            if abs(y) > hw - 0.12:
                continue
            p = (X(u), y, zz)
            q = (X(u) + d * 0.026, y, zz + 0.012)
            v.A("black").cyl(p, q, 0.058, seg=14)
            v.A("white").cyl((q[0] + d * 0.001, q[1], q[2]), (q[0] + d * 0.006, q[1], q[2] + 0.002), 0.048, seg=14)
            # needle
            a = rng.uniform(-1.0, 1.0)
            v.A("black").sbox((q[0] + d * 0.008, y, q[2]), (q[0] + d * 0.008, y + math.sin(a) * 0.04, q[2] + math.cos(a) * 0.04), 0.004, 0.004)
    # warning lamps + switches strip
    for k in range(8):
        y = -0.7 + k * 0.1
        v.A("lamp_glow" if k % 3 == 0 else ("red" if k % 3 == 1 else "yellow")).sphere((X(-0.05), y, zc + 0.12), (0.014, 0.014, 0.014), seg=6, rings=3)
    for k in range(5):
        v.A("steel").cyl((X(-0.05), 0.15 + k * 0.1, zc + 0.115), (X(-0.01), 0.15 + k * 0.1, zc + 0.14), 0.007, seg=5)
    # master controller (left hand) and brake valve (right hand)
    for (y, key, h) in ((-0.40, "black", 0.28), (-0.78, "steel", 0.22)):
        v.A(key).cyl((X(-0.12), y, zc + 0.06), (X(-0.12), y, zc + 0.06 + h), 0.05, 0.035, seg=10)
        v.A(key).sbox((X(-0.12), y, zc + 0.06 + h), (X(0.10), y, zc + 0.06 + h + 0.03), 0.026, 0.026)
        v.A("red" if key == "steel" else "black").sphere((X(0.10), y, zc + 0.09 + h), (0.035, 0.035, 0.035), seg=8, rings=5)
    v.A("black").box(min(X(-0.3), X(-0.05)), max(X(-0.3), X(-0.05)), 0.40, 0.65, zc + 0.04, zc + 0.12)       # reverser box
    # window frame sun-visor
    v.A("black").box(min(X(-0.42), X(-0.02)), max(X(-0.42), X(-0.02)), -hw, hw, zd + 2.95, zd + 2.99) if False else None
    # seat (swivel base + cushion + back + armrests)
    sx = X(1.15)
    v.A("black").cyl((sx, y_seat, zd + 0.02), (sx, y_seat, zd + 0.40), 0.06, seg=10)
    v.A("black").cyl((sx, y_seat, zd + 0.02), (sx, y_seat, zd + 0.05), 0.24, seg=12)
    v.A("moq2", 0.03).box(sx - 0.24, sx + 0.24, y_seat - 0.24, y_seat + 0.24, zd + 0.40, zd + 0.48)
    bx0, bx1 = sorted((X(1.15 + 0.22), X(1.15 + 0.30)))
    v.A("moq2", 0.03).box(bx0, bx1, y_seat - 0.23, y_seat + 0.23, zd + 0.48, zd + 0.95)
    for s in (-1, 1):
        v.A("black").sbox((sx - d * 0.2, y_seat + s * 0.25, zd + 0.62), (sx + d * 0.2, y_seat + s * 0.25, zd + 0.62), 0.04, 0.03)
    # floor pedals (dead-man pedal) + mat
    v.A("black").box(min(X(0.1), X(0.45)), max(X(0.1), X(0.45)), y_seat - 0.2, y_seat + 0.2, zd + 0.02, zd + 0.04)
    v.A("steel").box(min(X(0.15), X(0.30)), max(X(0.15), X(0.30)), y_seat - 0.07, y_seat + 0.07, zd + 0.04, zd + 0.13)
    if not driver:
        return
    face = -d                                  # driver faces the console
    Fx = lambda u: X(u)                        # u measured from the console edge toward the driver
    ys = y_seat
    # thighs / calves / shoes
    for s in (-1, 1):
        yy = ys + s * 0.11
        v.A("cl2", 0.02, True).sbox((Fx(1.15), yy, zd + 0.55), (Fx(0.70), yy, zd + 0.55), 0.14, 0.14)
        v.A("cl2", 0.02, True).sbox((Fx(0.70), yy, zd + 0.55), (Fx(0.62), yy, zd + 0.06), 0.11, 0.11)
        v.A("black", 0.02, True).box(min(Fx(0.52), Fx(0.72)), max(Fx(0.52), Fx(0.72)), yy - 0.06, yy + 0.06, zd + 0.02, zd + 0.09)
    # torso (jacket) leaning slightly forward + belt
    v.A("cl1", 0.04, True).sbox((Fx(1.14), ys, zd + 0.60), (Fx(1.06), ys, zd + 1.10), 0.38, 0.22)
    v.A("black").sbox((Fx(1.14), ys, zd + 0.62), (Fx(1.12), ys, zd + 0.64), 0.40, 0.03)
    # arms to the controller (left) and brake valve (right)
    for (s, tgt_y, tgt_h) in ((-1, -0.40, 0.34), (1, -0.78, 0.28)):
        sh = (Fx(1.08), ys + s * 0.22, zd + 1.03)
        el = (Fx(0.80), ys + s * 0.26, zd + 0.88)
        ha = (X(0.08), tgt_y, zc + 0.06 + tgt_h + 0.02)
        v.A("cl1", 0.02, True).sbox(sh, el, 0.075, 0.075)
        v.A("cl1", 0.02, True).sbox(el, ha, 0.065, 0.065)
        v.A("white", 0.0, True).sphere(ha, (0.04, 0.04, 0.04), seg=8, rings=5)
    # head + cap + visor
    hx = Fx(1.04)
    v.A("skin", 0.0, True).sphere((hx, ys, zd + 1.28), (0.095, 0.085, 0.11), seg=10, rings=7)
    v.A("skin", 0.0, True).cyl((hx, ys, zd + 1.14), (hx, ys, zd + 1.20), 0.04, seg=8)
    v.A("cl1", 0.0, True).cyl((hx, ys, zd + 1.34), (hx, ys, zd + 1.43), 0.10, 0.095, seg=14)
    v.A("cl1", 0.0, True).cyl((hx, ys, zd + 1.33), (hx, ys, zd + 1.345), 0.108, seg=14)
    v.A("black").box(min(hx + face * 0.06, hx + face * 0.17), max(hx + face * 0.06, hx + face * 0.17), ys - 0.075, ys + 0.075, zd + 1.33, zd + 1.345)
    v.A("white", 0.0, True).box(hx - 0.02, hx + 0.02, ys - 0.012, ys + 0.012, zd + 1.435, zd + 1.445) if False else None
