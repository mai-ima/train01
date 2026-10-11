"""Realistic-leaning steam locomotives, built from published proportions of the Japanese 1D1 (D51-type, standard, with smoke
deflectors) and 2C1 (C57-type) classes.  Generic geometry, no markings other than the fictional emblem/plates.
Local frame: +x = front (smokebox), y across, z = 0 at rail-head top.  Origin = main driving axle."""
from trainkit import *

CFG = {
    "D51": dict(rd=0.70, drv=[3.10, 1.60, 0.0, -1.55], main=2, lead=[5.30], lead_r=0.43, trail=[-3.95], trail_r=0.50,
                zb=2.50, rb=(0.88, 0.95, 1.00), x_sf=6.05, sb_len=1.95, stack=4.62, fwh=5.45, sand=2.35, dome=0.60,
                cab=(-2.55, -5.55), cyl_x=(4.00, 5.05), zc=1.02, pin_r=0.33, Lmr=3.30, rp_z=1.95, defl=True,
                tender=dict(L=7.2, W=2.80, h_tank=2.95, h_coal=3.35, wb=1.9), spokes=False, board_z=2.02),
    "C57": dict(rd=0.875, drv=[2.15, 0.0, -2.15], main=1, lead=[5.55, 3.75], lead_r=0.43, trail=[-4.45], trail_r=0.50,
                zb=2.78, rb=(0.88, 0.93, 0.97), x_sf=6.35, sb_len=1.75, stack=5.05, fwh=None, sand=2.65, dome=1.05,
                cab=(-3.05, -5.95), cyl_x=(4.15, 5.20), zc=1.12, pin_r=0.33, Lmr=3.45, rp_z=2.22, defl=True,
                tender=dict(L=6.9, W=2.75, h_tank=2.9, h_coal=3.3, wb=1.9), spokes=True, board_z=2.22),
}


def revolve_x(acc, prof, cy=0.0, cz=0.0, seg=32, cap_front=True, cap_back=True):
    """Surface of revolution about the x axis. prof = [(x, r), ...] ordered along +x."""
    i0 = len(acc.V)
    n = len(prof)
    for (x, r) in prof:
        for k in range(seg):
            t = 2 * math.pi * k / seg
            acc.V.append((x, cy + r * math.cos(t), cz + r * math.sin(t)))
    for j in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            acc.F.append((i0 + j * seg + k, i0 + j * seg + k2, i0 + (j + 1) * seg + k2, i0 + (j + 1) * seg + k))
    if cap_back:
        acc.F.append(tuple(i0 + k for k in reversed(range(seg))))
    if cap_front:
        acc.F.append(tuple(i0 + (n - 1) * seg + k for k in range(seg)))


def revolve_z(acc, cx, cy, prof, seg=20):
    """Surface of revolution about a vertical axis. prof = [(z, r), ...]."""
    i0 = len(acc.V)
    n = len(prof)
    for (z, r) in prof:
        for k in range(seg):
            t = 2 * math.pi * k / seg
            acc.V.append((cx + r * math.cos(t), cy + r * math.sin(t), z))
    for j in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            acc.F.append((i0 + j * seg + k, i0 + j * seg + k2, i0 + (j + 1) * seg + k2, i0 + (j + 1) * seg + k))
    acc.F.append(tuple(i0 + k for k in reversed(range(seg))))
    acc.F.append(tuple(i0 + (n - 1) * seg + k for k in range(seg)))


def annulus_y(acc, cx, cz, y0, y1, r_out, r_in, seg=48):
    """Ring (tyre) about a y-parallel axis through (cx, cz)."""
    i0 = len(acc.V)
    for yy in (y0, y1):
        for rr_ in (r_out, r_in):
            for k in range(seg):
                t = 2 * math.pi * k / seg
                acc.V.append((cx + rr_ * math.cos(t), yy, cz + rr_ * math.sin(t)))
    # index: layer l (0:y0 out, 1:y0 in, 2:y1 out, 3:y1 in)
    def idx(l, k):
        return i0 + l * seg + k % seg
    for k in range(seg):
        acc.F.append((idx(0, k), idx(0, k + 1), idx(2, k + 1), idx(2, k)))        # outer
        acc.F.append((idx(1, k), idx(3, k), idx(3, k + 1), idx(1, k + 1)))        # inner
        acc.F.append((idx(0, k), idx(1, k), idx(1, k + 1), idx(0, k + 1)))        # y0 face
        acc.F.append((idx(2, k), idx(2, k + 1), idx(3, k + 1), idx(3, k)))        # y1 face


def rod(v, p0, p1, w=0.09, h=0.04, key="steel"):
    v.A(key, 0.003).sbox(p0, p1, w, h, up=(0, 1, 0))


def pin(v, c, y0, y1, r, key="steel"):
    v.A(key).cyl((c[0], y0, c[1]), (c[0], y1, c[1]), r, r, seg=10)


# ------------------------------------------------------------------ wheels
def box_driver(v, x, r, ang, y_g=0.5335, spokes=False):
    """Driving wheel: tyre + flange + web (box-section 'hollow' centre with lightening holes, or spokes) + counterweight."""
    w = v.A("wheel")
    ws = v.A("iron", 0.0)
    for s in (-1, 1):
        y = s * y_g
        ri = r - 0.095
        annulus_y(w, x, r, y - 0.078, y + 0.078, r, ri + 0.012, 48)                         # tyre
        annulus_y(w, x, r, *sorted((y - s * 0.095, y - s * 0.062)), r + 0.032, r, 48)       # flange
        if not spokes:
            ws.cyl((x, y - 0.03, r), (x, y + 0.03, r), ri + 0.01, ri + 0.01, seg=48)               # web disc (recessed inside the tyre)
            ws.cyl((x, y + s * 0.03, r), (x, y + s * 0.06, r), ri - 0.03, ri - 0.03, seg=48) if False else None
            nh = 7
            for k in range(nh):
                t = 2 * math.pi * k / nh + 0.2
                hr = 0.5 * ri
                v.A("dark").cyl((x + hr * math.cos(t), y + s * 0.031, r + hr * math.sin(t)),
                                (x + hr * math.cos(t), y + s * 0.035, r + hr * math.sin(t)), 0.075 * (r / 0.7), 0.075 * (r / 0.7), seg=10)
            ws.torus((x, y + s * 0.034, r), 'y', ri - 0.02, 0.014, segR=40, segr=4)
        else:
            for k in range(14):
                t = 2 * math.pi * k / 14
                c, sn = math.cos(t), math.sin(t)
                ws.sbox((x + 0.20 * c, y, r + 0.20 * sn), (x + ri * c, y, r + ri * sn), 0.060, 0.07)
            ws.torus((x, y, r), 'y', ri - 0.01, 0.022, segR=44, segr=5)
        ws.cyl((x, y - 0.06, r), (x, y + 0.06, r), 0.20, 0.20, seg=20)                       # boss
        ws.cyl((x, y + s * 0.06, r), (x, y + s * 0.13, r), 0.13, 0.13, seg=16)               # axle cap
        # counterweight: crescent opposite the crank
        ca = math.radians(ang + 180)
        pts = []
        for da in np.linspace(-0.62, 0.62, 7):
            pts.append((x + ri * 0.97 * math.cos(ca + da), r + ri * 0.97 * math.sin(ca + da)))
        for da in np.linspace(0.45, -0.45, 5):
            pts.append((x + ri * 0.52 * math.cos(ca + da), r + ri * 0.52 * math.sin(ca + da)))
        i0 = len(ws.V)
        for (px, pz) in pts:
            ws.V.append((px, y + s * 0.02, pz))
        for (px, pz) in pts:
            ws.V.append((px, y + s * 0.075, pz))
        n = len(pts)
        for k in range(n):
            k2 = (k + 1) % n
            ws.F.append((i0 + k, i0 + k2, i0 + n + k2, i0 + n + k))
        ws.F.append(tuple(i0 + k for k in reversed(range(n))))
        ws.F.append(tuple(i0 + n + k for k in range(n)))
    w.cyl((x, -y_g - 0.1, r), (x, y_g + 0.1, r), 0.085, 0.085, seg=10)


def small_wheel(v, x, r, disc=True):
    wheelset(v, x, r)
    axle_box(v, x, 0.88, r)


# ------------------------------------------------------------------ the locomotive
def make_steam2(name="steam", kind="D51", ang=35.0, smoke=False, num_plate="plate_d.png", crew=True, deflectors=None):
    c = CFG[kind]
    v = Veh(name)
    rd, drv, zb = c["rd"], c["drv"], c["zb"]
    r_f, r_m, r_r = c["rb"]
    x_sf, sb_len = c["x_sf"], c["sb_len"]
    cab_f, cab_r = c["cab"]
    h = 1.45
    zc, pr, Lmr = c["zc"], c["pin_r"], c["Lmr"]
    main_x = drv[c["main"]]
    ar = math.radians(ang)
    defl = c["defl"] if deflectors is None else deflectors

    # ---- running gear: drivers, truck wheels
    for x in drv:
        box_driver(v, x, rd, ang, spokes=c["spokes"])
    for x in c["lead"]:
        small_wheel(v, x, c["lead_r"])
    for x in c["trail"]:
        small_wheel(v, x, c["trail_r"])

    # ---- frame (inside bar frames, as on the real engines), axleboxes, springs
    x_lo, x_hi = min(drv + c["trail"]) - 1.0, x_sf + 0.12
    for s in (-1, 1):
        v.A("black", 0.01).box(x_lo, x_hi, *sorted((s * 0.30, s * 0.38)), 0.86, 1.34)
        for x in drv:
            v.A("iron", 0.008).box(x - 0.20, x + 0.20, *sorted((s * 0.38, s * 0.45)), rd - 0.14, rd + 0.14)           # axlebox
            v.A("black", 0.004).box(x - 0.26, x + 0.26, *sorted((s * 0.38, s * 0.43)), rd + 0.14, 1.34)
        for (xa, xb) in zip(drv[:-1:2], drv[1::2]):
            for j in range(5):                                                                                          # leaf spring pack above the wheels
                v.A("steel", 0.003).box((xa + xb) / 2 - 0.95 + 0.07 * j, (xa + xb) / 2 + 0.95 - 0.07 * j,
                                         *sorted((s * 0.66 - 0.05, s * 0.66 + 0.05)), 1.50 + 0.026 * j, 1.52 + 0.026 * j)
            for xx in (xa, xb):
                v.A("steel").cyl((xx, s * 0.66, 1.44), (xx, s * 0.66, 1.50), 0.03, 0.03, seg=6)
                v.A("steel").sbox((xx, s * 0.43, 1.34), (xx, s * 0.66, 1.46), 0.035, 0.035, up=(1, 0, 0))
        for x in c["lead"] + c["trail"]:
            v.A("iron", 0.006).box(x - 0.16, x + 0.16, *sorted((s * 0.42, s * 0.50)), 0.32, 0.6)
    v.A("black", 0.01).box(x_lo, x_hi, -0.38, 0.38, 1.18, 1.34)
    for x in np.arange(drv[-1] - 0.2, drv[0] + 0.4, 0.8):
        v.A("black").box(x - 0.05, x + 0.05, -0.38, 0.38, 0.9, 1.18)                      # stretcher plates
    v.A("dark").box(x_lo, x_hi, -0.30, 0.30, 0.7, 1.18)                                    # shadowed space between the frames
    for x in c["lead"]:
        v.A("iron", 0.006).box(x - 0.45, x + 0.45, -0.75, 0.75, 0.62, 0.78)
    for x in c["trail"]:
        v.A("iron", 0.006).box(x - 0.5, x + 0.5, -0.8, 0.8, 0.70, 0.85)

    # ---- boiler: tapered courses, smokebox, wide firebox, as surfaces of revolution
    xr = cab_f + 0.15
    prof = [(x_sf - sb_len, r_f + 0.04), (x_sf - sb_len + 0.1, r_f + 0.07), (x_sf - 0.1, r_f + 0.07), (x_sf, r_f + 0.05)]
    sbx = v.A("black", 0.0, True)
    revolve_x(sbx, [(x_sf, r_f + 0.04), (x_sf - 0.06, r_f + 0.065), (x_sf - sb_len, r_f + 0.065), (x_sf - sb_len - 0.05, r_f + 0.02)], 0.0, zb, 40, cap_front=False, cap_back=False)
    barrel = v.A("black", 0.0, True)
    revolve_x(barrel, [(x_sf - sb_len - 0.05, r_f), (x_sf - sb_len - 0.9, r_f + 0.01), (0.9 - 0.0, r_m - 0.02), (0.9 - 1.9, r_m), (xr, r_r)], 0.0, zb, 40, cap_front=False, cap_back=False)
    # boiler bands / cladding seams
    for xb in list(np.arange(x_sf - sb_len - 0.6, xr + 0.6, -0.95)):
        rr_ = np.interp(xb, [xr, 0.0, x_sf - sb_len], [r_r, r_m, r_f])
        v.A("steel").torus((xb, 0, zb), 'x', rr_ + 0.012, 0.022, segR=44, segr=4)
    # wide firebox wrapper over the rear frame
    fb = v.A("black", 0.012, True)
    fb.extrude_x([(-1.22, 1.45), (1.22, 1.45), (1.22, zb + 0.35), (0.9, zb + 0.88), (-0.9, zb + 0.88), (-1.22, zb + 0.35)], cab_r + 0.55, cab_f + 0.05) if False else None
    v.A("black", 0.012).extrude_x([(-1.24, 1.62), (1.24, 1.62), (1.24, zb + 0.30), (r_r, zb + 0.98), (-r_r, zb + 0.98), (-1.24, zb + 0.30)], cab_r + 0.25, cab_f + 0.05)
    v.A("black", 0.012).box(cab_r + 0.25, cab_f + 0.05, -1.0, 1.0, 1.0, 1.62)           # ash pan
    v.A("iron", 0.0).box(cab_r + 0.35, cab_f - 0.1, -0.86, 0.86, 0.80, 1.0)

    # ---- smokebox front: door, ring, hinges, dart handle, number plate, lamp
    door = v.A("iron", 0.0, True)
    revolve_x(door, [(x_sf, r_f - 0.03), (x_sf + 0.04, r_f - 0.07), (x_sf + 0.14, r_f - 0.42), (x_sf + 0.17, 0.0)], 0.0, zb, 36, cap_front=False, cap_back=True)
    v.A("steel").torus((x_sf + 0.01, 0, zb), 'x', r_f - 0.015, 0.03, segR=40, segr=5)                 # door ring
    for k in range(10):
        t = 2 * math.pi * k / 10
        v.A("steel").cyl((x_sf + 0.01, (r_f - 0.015) * math.cos(t), zb + (r_f - 0.015) * math.sin(t)),
                         (x_sf + 0.05, (r_f - 0.015) * math.cos(t), zb + (r_f - 0.015) * math.sin(t)), 0.022, 0.022, seg=6)
    v.A("steel").cyl((x_sf + 0.17, 0, zb), (x_sf + 0.26, 0, zb), 0.055, 0.045, seg=10)               # dart head
    v.A("steel").sbox((x_sf + 0.24, -0.34, zb), (x_sf + 0.24, 0.34, zb), 0.045, 0.035, up=(0, 0, 1))  # handle bar
    v.A("steel").sbox((x_sf + 0.24, 0, zb - 0.34), (x_sf + 0.24, 0, zb + 0.34), 0.035, 0.045, up=(0, 1, 0))
    for sgn in (-1, 1):
        v.A("iron").box(x_sf + 0.01, x_sf + 0.12, *sorted((sgn * (r_f - 0.12), sgn * (r_f - 0.02))), zb - 0.04, zb + 0.04)   # hinge straps
    v.end_plane(num_plate, 1, 0.0, 0.52, zb - 0.63, zb - 0.63 + 0.52 * 160 / 420, x_sf + 0.172)
    v.A("black", 0.0, True)
    # headlamp on the smokebox top
    lamp = v.A("black", 0.008, True)
    lamp.box(x_sf - 0.55, x_sf - 0.22, -0.16, 0.16, zb + r_f + 0.04, zb + r_f + 0.10)
    revolve_x(lamp, [(x_sf - 0.52, 0.0), (x_sf - 0.52, 0.215), (x_sf - 0.02, 0.215), (x_sf - 0.02, 0.0)], 0.0, zb + r_f + 0.36, 24, True, True)
    v.A("lampglass").cyl((x_sf - 0.02, 0, zb + r_f + 0.36), (x_sf + 0.01, 0, zb + r_f + 0.36), 0.17, 0.17, seg=20)
    v.A("steel").torus((x_sf - 0.01, 0, zb + r_f + 0.36), 'x', 0.18, 0.012, segR=24, segr=4)
    v.A("steel").cyl((x_sf - 0.3, 0, zb + r_f + 0.58), (x_sf - 0.3, 0, zb + r_f + 0.66), 0.05, 0.05, seg=8)

    # ---- stack, feed-water heater, domes, fittings (all revolved so they read as smooth castings)
    zt_ = zb + np.interp(c["stack"], [xr, 0.0, x_sf - sb_len], [r_r, r_m, r_f])
    ch = v.A("black", 0.0, True)
    revolve_z(ch, c["stack"], 0.0, [(zt_ - 0.08, 0.30), (zt_ + 0.05, 0.255), (zt_ + 0.28, 0.185), (zt_ + 0.46, 0.20), (zt_ + 0.58, 0.285), (zt_ + 0.62, 0.285), (zt_ + 0.62, 0.20)], 24)
    v.A("dark").cyl((c["stack"], 0, zt_ + 0.617), (c["stack"], 0, zt_ + 0.622), 0.20, 0.20, seg=24)
    if c["fwh"] is not None:
        fw = v.A("steel", 0.0, True)
        fw.cyl((c["fwh"] - 0.0, -0.55, zb + r_f + 0.25), (c["fwh"], 0.55, zb + r_f + 0.25), 0.27, 0.27, seg=20)
        for sgn in (-1, 1):
            v.A("iron", 0.0, True).cyl((c["fwh"], sgn * 0.55, zb + r_f + 0.25), (c["fwh"], sgn * 0.62, zb + r_f + 0.25), 0.29, 0.29, seg=20)
        v.A("steel").box(c["fwh"] - 0.30, c["fwh"] + 0.30, -0.45, 0.45, zb + r_f - 0.03, zb + r_f + 0.04)
    for (xs, rr_s, hh, nm) in ((c["sand"], 0.36, 0.34, "sand"), (c["dome"], 0.48, 0.42, "steam")):
        z0 = zb + np.interp(xs, [xr, 0.0, x_sf - sb_len], [r_r, r_m, r_f]) - 0.12
        d = v.A("black", 0.0, True)
        revolve_z(d, xs, 0.0, [(z0, rr_s + 0.05), (z0 + 0.10, rr_s), (z0 + hh * 0.6, rr_s * 0.98), (z0 + hh * 0.9, rr_s * 0.82), (z0 + hh + 0.12, rr_s * 0.48),
                                (z0 + hh + 0.17, rr_s * 0.2), (z0 + hh + 0.18, 0.0)], 28)
        v.A("steel").torus((xs, 0, z0 + 0.12), 'z', rr_s + 0.005, 0.02, segR=28, segr=4)
    zd = zb + np.interp(c["dome"], [xr, 0.0, x_sf - sb_len], [r_r, r_m, r_f])
    v.A("brass").cyl((c["dome"] - 0.85, 0, zd - 0.1), (c["dome"] - 0.85, 0, zd + 0.22), 0.045, 0.045, seg=8)    # whistle
    v.A("brass", 0.0, True).sphere((c["dome"] - 0.85, 0, zd + 0.25), (0.06, 0.06, 0.07), seg=8, rings=5)
    for k, dx in enumerate((-1.45, -1.62)):
        v.A("brass", 0.0, True).cyl((c["dome"] + dx, 0, zd - 0.08), (c["dome"] + dx, 0, zd + 0.30), 0.075 if k == 0 else 0.06, 0.075 if k == 0 else 0.06, seg=10)
    v.A("steel").cyl((c["dome"] - 1.1, 0.0, zd - 0.05), (c["dome"] - 1.1, 0.0, zd + 0.15), 0.12, 0.10, seg=10)    # turret
    v.A("black", 0.0, True).cyl((cab_f + 0.8, 0.0, zb + r_r - 0.1), (cab_f + 0.8, 0.0, zb + r_r + 0.08), 0.20, 0.17, seg=14)   # air-reservoir-like turret

    # ---- running boards, handrails, boiler-side pipework, air pump, sand pipes
    bz = c["board_z"]
    for s in (-1, 1):
        v.A("iron", 0.005).box(cab_f + 0.2, x_sf - 0.25, *sorted((s * 0.86, s * 1.50)), bz, bz + 0.05)
        v.A("black", 0.004).box(cab_f + 0.2, x_sf - 0.25, *sorted((s * 1.50, s * 1.53)), bz - 0.15, bz + 0.05)    # valance
        v.A("steel").box(cab_f + 0.2, x_sf - 0.25, *sorted((s * 1.5, s * 1.51)), bz + 0.05, bz + 0.06) if False else None
        for x in np.arange(cab_f + 0.7, x_sf - 0.5, 1.1):                                   # brackets under the board
            v.A("black").box(x - 0.04, x + 0.04, *sorted((s * 0.9, s * 1.48)), bz - 0.18, bz)
        # boiler handrail on stanchions, curved down around smokebox front
        for x in np.arange(cab_f + 0.9, x_sf - sb_len + 0.4, 1.25):
            rr_ = np.interp(x, [xr, 0.0, x_sf - sb_len], [r_r, r_m, r_f])
            grab_rail(v, (x, s * (rr_ * 0.87), zb + rr_ * 0.49), (x, s * (rr_ * 0.87 + 0.20), zb + rr_ * 0.49 + 0.02), 0.014, "steel")
        rz = zb + 0.50
        grab_rail(v, (cab_f + 0.9, s * (r_r * 0.87 + 0.2), rz + 0.02), (x_sf - sb_len + 0.4, s * (r_f * 0.87 + 0.2), zb + r_f * 0.49 + 0.02), 0.017, "steel")
        grab_rail(v, (x_sf - sb_len + 0.4, s * (r_f * 0.87 + 0.2), zb + r_f * 0.49 + 0.02), (x_sf - 0.2, s * (r_f * 0.90), zb + r_f * 0.45), 0.017, "steel")
        grab_rail(v, (x_sf - 0.2, s * (r_f * 0.90), zb + r_f * 0.45), (x_sf + 0.02, s * 0.6, zb + 0.2), 0.017, "steel")
        grab_rail(v, (x_sf + 0.02, s * 0.6, zb + 0.2), (x_sf + 0.02, s * 0.6, zb - 0.45), 0.017, "steel")
        # steam pipe + exhaust to cylinders; sand pipes
        px0, pz0 = x_sf - sb_len + 0.4, zb - 0.38
        v.A("steel").cyl((px0, s * (r_f - 0.1), pz0), (c["cyl_x"][0] + 0.5, s * 0.98, zc + 0.46), 0.075, 0.075, seg=8)
        v.A("steel").cyl((c["sand"] - 0.05, s * 0.55, bz + 0.05), (drv[1] + 0.35, s * 0.82, rd + 0.50), 0.022, 0.022, seg=5)
        v.A("steel").cyl((c["sand"] - 0.05, s * 0.55, bz + 0.05), (drv[2] + 0.35 if len(drv) > 2 else drv[1] - 0.8, s * 0.82, rd + 0.50), 0.022, 0.022, seg=5) if False else None
        # air pump (left) / feed pump (right)
        ap = v.A("iron", 0.0, True)
        xp = x_sf - 1.55 if s == 1 else x_sf - 1.40
        ap.cyl((xp, s * 1.30, bz + 0.05), (xp, s * 1.30, bz + 0.78), 0.14, 0.14, seg=12)
        ap.cyl((xp, s * 1.30, bz + 0.78), (xp, s * 1.30, bz + 1.0), 0.09, 0.09, seg=10)
        v.A("steel").cyl((xp, s * 1.30, bz + 0.2), (xp, s * 1.30, bz + 0.52), 0.19, 0.19, seg=14)
        v.A("steel").cyl((xp + 0.0, s * 1.15, bz + 0.45), (xp + 0.9, s * 0.72, zb - 0.15), 0.03, 0.03, seg=6)
        # tool box / lubricator on the board
        v.A("black", 0.01).box(cab_f + 0.35, cab_f + 1.35, *sorted((s * 1.1, s * 1.45)), bz + 0.05, bz + 0.35)
        # steps up to the board at the front and rear
        for k in range(3):
            v.A("iron", 0.004).box(x_sf - 0.9 - k * 0.0, x_sf - 0.5, *sorted((s * 1.45, s * 1.62)), 0.55 + 0.45 * k, 0.58 + 0.45 * k)

    # ---- front end: buffer beam, pilot, couplers, hoses, ladder, lamps
    xb = x_sf + 0.17
    v.A("red", 0.012).box(xb, xb + 0.24, -1.42, 1.42, 0.80, 1.22)
    for s in (-1, 1):
        v.A("steel").cyl((xb + 0.24, s * 1.1, 1.0), (xb + 0.30, s * 1.1, 1.0), 0.105, 0.105, seg=16)       # dummy buffer
        v.A("steel", 0.0, True).cyl((xb + 0.24, s * 0.62, 0.78), (xb + 0.26, s * 0.62, 0.78), 0.03, 0.03, seg=6)
        v.A("lampglass").cyl((xb + 0.245, s * 1.25, 1.14), (xb + 0.275, s * 1.25, 1.14), 0.05, 0.05, seg=10)
        v.A("rubber").cyl((xb + 0.2, s * 0.45, 0.8), (xb + 0.34, s * 0.45, 0.45), 0.03, 0.03, seg=6)
    coupler(v, 1, xb + 0.24, z=0.88)
    for yy in np.linspace(-1.1, 1.1, 8):                                                       # pilot bars
        v.A("iron").sbox((xb + 0.02, yy, 0.82), (xb + 0.78, yy * 0.45, 0.32), 0.05, 0.07, up=(0, 1, 0))
    v.A("iron").box(xb + 0.70, xb + 0.80, -0.5, 0.5, 0.28, 0.36)
    for s in (-1, 1):
        for k in range(4):
            v.A("steel").cyl((xb + 0.12, s * 0.12, 1.22 + 0.17 * k - 0.0 * s), (xb + 0.12, s * 0.12 - 0, 1.22 + 0.17 * k + 0.01), 0.0, 0.0, seg=3) if False else None
    for k in range(5):                                                                          # smokebox front ladder (hand holds)
        v.A("steel").cyl((x_sf + 0.17, -0.22, 1.23 + 0.17 * k), (x_sf + 0.17, 0.22, 1.23 + 0.17 * k), 0.012, 0.012, seg=5)
    for s in (-1, 1):
        v.A("steel").cyl((x_sf + 0.17, s * 0.22, 1.23), (x_sf + 0.17, s * 0.22, 1.23 + 0.17 * 4), 0.012, 0.012, seg=5)

    # ---- cylinders, guides, rods, Walschaerts gear
    cx0, cx1 = c["cyl_x"]
    px, pz = main_x + pr * math.cos(ar), rd + pr * math.sin(ar)
    xc = px + math.sqrt(Lmr ** 2 - (zc - pz) ** 2)
    y_out = 0.5335 + 0.215
    y_pin = 0.5335 + 0.17
    for s in (-1, 1):
        y = s * 1.00
        cyl = v.A("iron", 0.012, True)
        cyl.cyl((cx0 + 0.04, y, zc), (cx1 - 0.04, y, zc), 0.285, 0.285, seg=24)
        v.A("steel", 0.0, True).cyl((cx1 - 0.04, y, zc), (cx1 + 0.02, y, zc), 0.255, 0.215, seg=24)       # front cover
        v.A("steel", 0.0, True).cyl((cx0 - 0.0, y, zc), (cx0 + 0.04, y, zc), 0.24, 0.285, seg=24)
        v.A("steel").cyl((cx1 + 0.02, y, zc), (cx1 + 0.05, y, zc), 0.07, 0.07, seg=10)
        v.A("iron", 0.012).box(cx0 + 0.1, cx1 - 0.1, *sorted((y - 0.2, y + 0.2)), zc - 0.35, zc - 0.20)       # lower saddle bracket
        sc = v.A("iron", 0.012, True)
        sc.cyl((cx0 + 0.15, y, zc + 0.42), (cx1 - 0.15, y, zc + 0.42), 0.17, 0.17, seg=18)                # steam chest (valve cylinder)
        v.A("steel").cyl((cx1 - 0.15, y, zc + 0.42), (cx1 - 0.08, y, zc + 0.42), 0.14, 0.12, seg=14)
        v.A("iron", 0.01).box(cx0 + 0.15, cx1 - 0.15, *sorted((y - 0.17, y + 0.17)), zc + 0.08, zc + 0.42)
        v.A("steel").cyl((cx0 - 0.0, y, zc), (xc, y, zc), 0.035, 0.035, seg=8)                              # piston rod / tail
        gb = v.A("steel", 0.003)
        for dz in (-0.075, 0.075):                                                                          # guide bars
            gb.box(xc - 0.45, cx0 - 0.0, *sorted((y - 0.045, y + 0.045)), zc + dz - 0.015, zc + dz + 0.015)
        v.A("iron", 0.004).box(xc - 0.28, xc - 0.22, *sorted((y - 0.06, y + 0.06)), zc - 0.12, zc + 0.12)    # guide yoke
        v.A("iron", 0.006).box(xc - 0.13, xc + 0.05, *sorted((y - 0.075, y + 0.075)), zc - 0.07, zc + 0.07)  # crosshead
        # main rod from crosshead pin (cylinder side) to main crank pin (outside plane)
        v.A("steel", 0.003).sbox((xc, s * y_out, zc), (px, s * y_out, pz), 0.12, 0.045, up=(0, 1, 0))
        v.A("steel").cyl((xc, y, zc), (xc, s * y_out, zc), 0.035, 0.035, seg=8)
        for x in drv:                                                                                       # crank pins + bosses
            cxp, czp = x + pr * math.cos(ar), rd + pr * math.sin(ar)
            v.A("steel").cyl((cxp, s * (0.5335 + 0.05), czp), (cxp, s * (0.5335 + 0.26), czp), 0.055, 0.055, seg=10)
            v.A("brass").cyl((cxp, s * (0.5335 + 0.24), czp), (cxp, s * (0.5335 + 0.27), czp), 0.07, 0.07, seg=10) if False else None
        for i in range(len(drv) - 1):                                                                       # coupling rods
            a0 = (drv[i] + pr * math.cos(ar), s * y_pin, rd + pr * math.sin(ar))
            a1 = (drv[i + 1] + pr * math.cos(ar), s * y_pin, rd + pr * math.sin(ar))
            v.A("steel", 0.003).sbox(a0, a1, 0.115, 0.04, up=(0, 1, 0))
            v.A("steel").cyl((a0[0], s * (y_pin - 0.03), a0[2]), (a0[0], s * (y_pin + 0.03), a0[2]), 0.075, 0.075, seg=10)
        a_last = (drv[-1] + pr * math.cos(ar), s * y_pin, rd + pr * math.sin(ar))
        v.A("steel").cyl((a_last[0], s * (y_pin - 0.03), a_last[2]), (a_last[0], s * (y_pin + 0.03), a_last[2]), 0.075, 0.075, seg=10)
        # --- Walschaerts valve gear
        rc = (main_x + 0.21 * math.cos(ar - math.pi / 2), rd + 0.21 * math.sin(ar - math.pi / 2))        # return crank
        yg = s * (y_out + 0.06)
        v.A("steel").sbox((px, s * (y_out + 0.0), pz), (rc[0], yg, rc[1]), 0.05, 0.03, up=(0, 1, 0))
        lk = (main_x + 1.30, 1.50)                                                                            # expansion-link centre
        v.A("steel", 0.003).sbox((rc[0], yg, rc[1]), (lk[0], yg, lk[1] - 0.25), 0.04, 0.035, up=(0, 1, 0))   # eccentric rod
        for t in np.linspace(-1, 1, 6):
            v.A("steel").box(lk[0] - 0.05 * t * 0.0 - 0.04, lk[0] + 0.04, *sorted((yg - 0.03, yg + 0.03)),
                             lk[1] + 0.26 * t * 0.9 - 0.04 + 0.0, lk[1] + 0.26 * t * 0.9 + 0.04)
        v.A("steel", 0.003).sbox((lk[0], yg, lk[1] - 0.27), (lk[0], yg, lk[1] + 0.27), 0.05, 0.03, up=(1, 0, 0))
        pv = (cx0 + 0.55, zc + 0.80)                                                                           # combination-lever pivot
        v.A("steel", 0.003).sbox((lk[0], yg, lk[1]), (pv[0] - 0.4, yg, pv[1] - 0.26), 0.03, 0.03, up=(0, 1, 0))   # radius rod
        v.A("steel", 0.003).sbox((pv[0] - 0.4, yg, pv[1] - 0.26), (cx0 + 0.55, yg, pv[1] - 0.10), 0.03, 0.03, up=(0, 1, 0))
        v.A("steel", 0.003).sbox((cx0 + 0.55, yg, zc + 0.12), (cx0 + 0.55, yg, zc + 0.72), 0.04, 0.025, up=(1, 0, 0))  # combination lever
        v.A("steel", 0.003).sbox((xc - 0.1, y_out * s, zc + 0.10), (cx0 + 0.55, yg, zc + 0.30), 0.03, 0.025, up=(0, 1, 0))     # union link
        v.A("steel", 0.003).sbox((cx0 + 0.55, yg, zc + 0.64), (cx0 + 0.14, s * 1.0, zc + 0.42), 0.03, 0.025, up=(0, 1, 0))     # valve rod
        v.A("steel").cyl((lk[0], yg - s * 0.02, lk[1] + 0.05), (lk[0], yg + s * 0.05, lk[1] + 0.05), 0.04, 0.04, seg=8)
        v.A("steel", 0.003).sbox((lk[0] + 0.0, yg, lk[1] + 0.34), (lk[0] - 0.85, yg, bz + 0.18), 0.02, 0.02, up=(0, 1, 0))  # reach rod
        v.A("steel").cyl((lk[0] - 0.85, yg, bz + 0.18), (lk[0] - 0.85, yg, bz + 0.45), 0.025, 0.025, seg=6) if False else None
        # drain cocks + lubricator pipes
        for dx in (-0.3, 0.3):
            v.A("brass").cyl((cx0 + 0.5 + dx, y, zc - 0.28), (cx0 + 0.5 + dx, y + s * 0.0, zc - 0.55), 0.022, 0.022, seg=6)

    # ---- cab
    W = 2.90
    hc = W / 2
    t_ = 0.08
    for s in (-1, 1):
        wall_open(v, "black", 'y', cab_r, cab_f, s * (hc - t_), s * hc, 1.62, 3.55,
                  [(cab_f - 1.00, cab_f - 0.30, 2.40, 3.10), (cab_r + 0.45, cab_r + 1.45, 2.40, 3.10)], 0.008)
        v.A("black", 0.008).box(cab_r, cab_f, *sorted((s * (hc - t_), s * hc)), 1.46, 1.62)
        for (a_, b_) in ((cab_f - 1.00, cab_f - 0.30), (cab_r + 0.45, cab_r + 1.45)):
            v.A("glass").box(a_ + 0.02, b_ - 0.02, *sorted((s * (hc - 0.05), s * (hc - 0.045))), 2.42, 3.08)
            v.A("steel", 0.002).box(a_ - 0.03, b_ + 0.03, *sorted((s * (hc - t_), s * (hc + 0.012))), 3.08, 3.12)
            v.A("steel", 0.002).box(a_ - 0.03, b_ + 0.03, *sorted((s * (hc - t_), s * (hc + 0.012))), 2.38, 2.42)
        v.A("iron", 0.004).box(cab_r, cab_r + 0.06, *sorted((s * (hc - 0.12), s * hc)), 1.62, 3.55)         # rear post
        v.A("steel").cyl((cab_f - 0.4, s * (hc + 0.02), 3.12), (cab_f - 0.4, s * (hc + 0.08), 3.12), 0.012, 0.012, seg=5)
    wall_open(v, "black", 'x', -hc, hc, cab_f - t_, cab_f, 1.62, 3.55, [], 0.008)
    v.A("floorw").box(cab_r, cab_f, -hc + 0.08, hc - 0.08, 1.62, 1.65)
    v.A("black", 0.014).extrude_x(upper_profile(W + 0.22, 3.50, 3.58, 4.00 if kind == "D51" else 3.96, n=8), cab_r - 0.55, cab_f + 0.25)
    v.A("black", 0.01, True).cyl((cab_r + 0.5, 0.0, 3.99), (cab_r + 1.5, 0.0, 3.99), 0.0, 0.0, seg=3) if False else None
    v.A("black", 0.01).box(cab_r - 0.55, cab_f + 0.25, -0.65, 0.65, 3.98, 4.02)                               # roof ventilator rib
    v.A("black", 0.01).box(cab_r - 0.55 + 0.4, cab_r + 1.0, -0.4, 0.4, 3.92, 4.10)                             # roof vent
    # interior: backhead, fire door glow, controls, seats, crew
    v.A("black").box(cab_f - 1.05, cab_f - 0.07, -0.55, 0.55, 1.65, 2.55)
    v.A("dark").box(cab_f - 1.075, cab_f - 1.05, -0.26, 0.26, 1.72, 2.12)
    v.A("glow" if False else "lamp_in").box(cab_f - 1.08, cab_f - 1.075, -0.18, 0.18, 1.78, 2.0)
    for sgn in (-1, 1):
        v.A("brass").cyl((cab_f - 1.08, sgn * 0.38, 2.45), (cab_f - 1.04, sgn * 0.38, 2.45), 0.085, 0.085, seg=14)      # gauges
        v.A("brass").cyl((cab_f - 1.1, sgn * 0.12, 2.35), (cab_f - 1.04, sgn * 0.12, 2.35), 0.035, 0.035, seg=8)
    v.A("steel").cyl((cab_f - 1.0, -0.0, 2.55), (cab_f - 1.0, 0.0, 2.75), 0.02, 0.02, seg=6)
    v.A("moq2").box(cab_r + 0.35, cab_r + 0.85, 0.55, 1.15, 1.65, 2.05)
    v.A("moq2").box(cab_r + 0.35, cab_r + 0.85, -1.15, -0.55, 1.65, 2.05)
    if crew:
        v.A("cl1", 0.03, True).box(cab_r + 0.40, cab_r + 0.82, -1.12, -0.62, 2.05, 2.55)
        v.A("skin", 0.0, True).sphere((cab_r + 0.61, -0.87, 2.72), (0.1, 0.09, 0.115), seg=8, rings=6)
        v.A("cl1", 0.0, True).sphere((cab_r + 0.61, -0.87, 2.82), (0.125, 0.115, 0.05), seg=8, rings=4)
        v.A("steel").sbox((cab_r + 0.40, -1.0, 2.40), (cab_f - 1.2, -0.62, 2.50), 0.05, 0.05)
    v.A("lamp_in").cyl((cab_f - 0.8, 0, 3.52), (cab_f - 0.8, 0, 3.55), 0.1, 0.1, seg=8)
    # cab steps + grab rails + number plates
    for s in (-1, 1):
        for k in range(3):
            v.A("iron", 0.004).box(cab_r + 0.55, cab_r + 1.15, *sorted((s * (hc - 0.02), s * (hc + 0.25))), 0.6 + 0.35 * k, 0.63 + 0.35 * k)
        grab_rail(v, (cab_r + 0.08, s * (hc + 0.05), 1.55), (cab_r + 0.08, s * (hc + 0.05), 3.2), 0.02, "steel")
        grab_rail(v, (cab_r + 1.2, s * (hc + 0.05), 1.55), (cab_r + 1.2, s * (hc + 0.05), 3.2), 0.02, "steel")
        v.side_plane(num_plate, s, cab_f - 0.35 - 0.1, 0.46, 1.78, 1.78 + 0.46 * 160 / 420, s * (hc + 0.012))
        v.side_plane("logo_new.png", s, (cab_r + cab_f) / 2 + 0.2, 0.0001 + 0.0, 0, 0.0001, 0) if False else None

    # ---- tender
    td = c["tender"]
    t0 = cab_r - 0.55
    t1 = t0 - td["L"]
    tw = td["W"] / 2
    ztop = td["h_tank"]
    v.A("iron", 0.008).box(t1, t0, -1.25, 1.25, 0.88, 1.22)                                               # tender frame
    v.A("black", 0.01).box(t1, t0, -tw, tw, 1.22, 2.30)                                                  # lower body
    for s in (-1, 1):
        v.A("black", 0.012).box(t1, t0 - 2.2, *sorted((s * (tw - 0.08), s * tw)), 2.30, ztop)           # tank side (rear)
        v.A("black", 0.012).box(t0 - 2.2, t0, *sorted((s * (tw - 0.08), s * tw)), 2.30, ztop - 0.12)   # forward upper sides (U-shape arms)
        v.A("iron", 0.004).box(t1, t0, *sorted((s * (tw + 0.012), s * (tw - 0.0))), 2.27, 2.33)          # waist bead
        v.A("iron", 0.004).box(t1, t0, *sorted((s * (tw + 0.012), s * (tw - 0.0))), 1.22, 1.27)
    v.A("black", 0.012).box(t1, t0 - 2.2, -tw + 0.08, tw - 0.08, 2.30, ztop - 0.02)                      # water deck
    v.A("black", 0.012).box(t1, t1 + 0.12, -tw, tw, ztop - 0.5, ztop + 0.12)                            # rear coal board
    v.A("black", 0.012).box(t0 - 0.12, t0, -tw, tw, 2.30, ztop + 0.25)                                  # front coal board
    # coal pile in the bunker
    rr = random.Random(7)
    prof = [(-1, -1)]
    v.A("coal", 0.0, True).extrude_x([(-tw + 0.12, 2.3), (tw - 0.12, 2.3), (tw - 0.35, td["h_coal"] - 0.1), (0.0, td["h_coal"] + 0.1), (-tw + 0.35, td["h_coal"] - 0.1)], t0 - 2.15, t0 - 0.15)
    for k in range(46):
        v.A("coal", 0.0, True).sphere((t0 - 0.25 - rr.uniform(0, 1.9), rr.uniform(-1.0, 1.0), rr.uniform(td["h_coal"] - 0.18, td["h_coal"] + 0.18)),
                                      (rr.uniform(0.18, 0.4), rr.uniform(0.15, 0.35), rr.uniform(0.1, 0.22)), seg=6, rings=4)
    # water filler hatch and manholes
    for xh in (t1 + 1.0, t1 + 3.2):
        v.A("iron", 0.0, True).cyl((xh, 0.0, ztop - 0.02), (xh, 0.0, ztop + 0.10), 0.38, 0.34, seg=18)
        v.A("steel").cyl((xh, 0.0, ztop + 0.10), (xh, 0.0, ztop + 0.12), 0.30, 0.30, seg=18)
    v.A("iron", 0.006).box(t1 + 0.6, t1 + 4.6, -0.04, 0.04, ztop - 0.02, ztop + 0.0)
    for s in (-1, 1):
        for xx in (t1 + 0.35, (t0 + t1) / 2, t0 - 0.4):
            grab_rail(v, (xx, s * (tw + 0.06), 1.3), (xx, s * (tw + 0.06), 2.3), 0.018, "iron")
        grab_rail(v, (t1 + 0.35, s * (tw + 0.06), 2.3), (t0 - 0.4, s * (tw + 0.06), 2.3), 0.016, "iron") if False else None
        v.A("black", 0.006).box(t1 + 0.25, t0 - 0.25, *sorted((s * (tw + 0.0), s * (tw + 0.04))), 1.35, 1.48)       # panel strip
        v.side_plane("logo_new.png", s, (t0 + t1) / 2 + 0.2, 0.8, 1.45, 2.25, s * (tw + 0.014))
        v.side_plane("mark_depot.png", s, (t0 + t1) / 2 - 1.8, 1.0, 1.52, 1.52 + 1.0 * 120 / 500, s * (tw + 0.014))
    # tender running gear: two 2-axle trucks, drawbar, buffers, couplers, hoses, hand brake wheel
    bx = (t0 + t1) / 2
    for xx in (bx - td["L"] * 0.26, bx + td["L"] * 0.26):
        bogie2(v, xx, wb=td["wb"], r=0.43)
    v.A("black", 0.01).box(t0, cab_r + 0.30, -0.14, 0.14, 1.02, 1.20)                                    # drawbar
    v.A("iron", 0.01).box(t1 - 0.14, t1, -1.25, 1.25, 0.82, 1.18)
    coupler(v, -1, t1 - 0.14, z=0.88)
    for s in (-1, 1):
        v.A("steel").cyl((t1 - 0.14, s * 0.9, 1.0), (t1 - 0.2, s * 0.9, 1.0), 0.09, 0.09, seg=12)
    v.A("steel").cyl((t1 + 0.4, 0.9, ztop + 0.12), (t1 + 0.4, 0.9, ztop + 0.7), 0.025, 0.025, seg=6)        # brake staff
    v.A("steel").torus((t1 + 0.4, 0.9, ztop + 0.7), 'z', 0.18, 0.016, segR=20, segr=4)
    for s in (-1, 1):                                                                                     # rear lamp brackets
        v.A("iron").box(t1 + 0.02, t1 + 0.18, *sorted((s * 0.85 - 0.12, s * 0.85 + 0.12)), ztop + 0.12, ztop + 0.16)
        v.A("lampglass").cyl((t1 - 0.02, s * 0.85, ztop + 0.38), (t1 + 0.04, s * 0.85, ztop + 0.38), 0.07, 0.07, seg=10)
    v.A("black").cyl((t0 - 0.3, 0.0, 1.5), (t0 - 0.3, 0.0, 1.5), 0.0, 0.0, seg=3) if False else None

    # ---- steam / smoke puffs
    if smoke:
        rr = random.Random(5)
        zs0 = zt_ + 0.62
        for i in range(16):
            t = i / 15.0
            v.A("steam", 0.0, True).sphere((c["stack"] - 0.5 * t - rr.uniform(-0.1, 0.1), rr.uniform(-0.2, 0.2) * (1 + t) + 0.3 * t,
                                            zs0 + 0.3 + 1.2 * t + rr.uniform(-0.1, 0.1)),
                                           (0.14 + 0.45 * t, 0.14 + 0.45 * t, 0.12 + 0.38 * t), seg=10, rings=6)

    # ---- smoke deflectors (Z-shaped plates beside the smokebox) + stays
    if defl:
        zd0 = zb + 0.25
        zd1 = zb + r_f + 0.46
        for s in (-1, 1):
            yd = s * 0.98
            pts = [(x_sf - 0.38, zd0 + 0.12), (x_sf - 0.38, zd0 + 0.9), (x_sf - 1.55, zd1), (c["sand"] + 0.45, zd1), (c["sand"] + 0.45, zd0 + 0.25), (x_sf - 1.0, zd0 - 0.02)]
            dfl = v.A("black", 0.004)
            dfl.extrude_y([(p[0], p[1]) for p in pts], *sorted((yd - 0.012, yd + 0.012)))
            for (xa, za) in ((x_sf - 0.85, zd0 + 0.2), (x_sf - 2.2, zd0 + 0.2), (x_sf - 1.2, zd0 + 0.2)):
                v.A("steel").sbox((xa, s * 0.70, za - 0.05), (xa, yd, za + 0.35), 0.03, 0.03, up=(1, 0, 0))
            v.A("steel").sbox((x_sf - 0.38, yd, zd0 + 0.9), (c["sand"] + 0.45, yd, zd1), 0.0, 0.0, up=(0, 1, 0)) if False else None
    return v
