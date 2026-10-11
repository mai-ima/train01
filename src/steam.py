"""Generic steam locomotives (inspired by common Japanese 2-8-2 / 4-6-2 / 2-6-4T types — original geometry, no markings).
Local frame: +x = chimney end (front), z = 0 at rail-head top."""
from trainkit import *

_EXTRA = {}


def smat(key):
    if not _EXTRA:
        _EXTRA["steam"] = lib.mat_plain("steam_white", (0.92, 0.92, 0.92), rough=0.95, spec=0.05)
        _EXTRA["glow"] = lib.mat_emissive("firebox_glow", (1.0, 0.45, 0.12), 6.0)
    return _EXTRA[key]


def driver(v, x, r, y_g=0.5335, ang=40.0, spokes=12):
    a = v.A("wheel")
    ir = r - 0.10
    for s in (-1, 1):
        y = s * y_g
        a.cyl((x, y - 0.075, r), (x, y + 0.075, r), r, r, seg=36)                       # tyre
        a.cyl((x, y - s * 0.085, r), (x, y - s * 0.055, r), r + 0.03, r + 0.03, seg=36)   # flange
        a.cyl((x, y - 0.03, r), (x, y + 0.03, r), ir, ir, seg=36) if False else None
        sp = v.A("iron", 0.0)
        for k in range(spokes):
            t = 2 * math.pi * k / spokes
            c, sn = math.cos(t), math.sin(t)
            sp.cyl((x + 0.17 * c, y + s * 0.01, r + 0.17 * sn), (x + (ir) * c, y + s * 0.01, r + (ir) * sn), 0.028, 0.022, seg=6)
        sp.cyl((x, y + s * 0.01 - 0.03, r), (x, y + s * 0.01 + 0.03, r), 0.19, 0.19, seg=16)
        sp.cyl((x, y + s * 0.07, r), (x, y + s * 0.13, r), 0.115, 0.115, seg=14)        # hub boss (outer)
        # counterweight (a thick sector opposite the crank pin)
        ca = math.radians(ang + 180)
        for dr, w in ((0.30, 0.34), (0.42, 0.30), (0.52, 0.22)):
            for da in (-0.28, 0.0, 0.28):
                sp.sbox((x + 0.2 * math.cos(ca + da), y + s * 0.025, r + 0.2 * math.sin(ca + da)),
                        (x + (dr + 0.14) * math.cos(ca + da), y + s * 0.025, r + (dr + 0.14) * math.sin(ca + da)), 0.12, 0.05)
    a.cyl((x, -y_g - 0.1, r), (x, y_g + 0.1, r), 0.075, 0.075, seg=10)


def truck_wheel(v, x, r=0.43):
    wheelset(v, x, r)
    axle_box(v, x, 0.88, r)


def make_steam(name="steam", kind="D", ang=40.0, smoke=False, num_plate="plate_d.png", crew=True):
    v = Veh(name)
    if kind == "D":
        lead, drv, trail, rd = [4.3], [2.85, 1.35, -0.15, -1.65], [-3.3], 0.70
        x_sf, x_fb, rb, zb = 4.75, -2.9, 0.95, 2.75
        cab0, cab1, cyl_x, stack_x, dome_x, sand_x = -5.0, -2.9, 3.55, 4.15, 1.5, 0.3
        tender = True
    elif kind == "C":
        lead, drv, trail, rd = [4.55, 3.35], [2.35, 0.35, -1.65], [-3.7], 0.85
        x_sf, x_fb, rb, zb = 5.55, -3.0, 0.90, 2.72
        cab0, cab1, cyl_x, stack_x, dome_x, sand_x = -5.2, -3.0, 3.55, 5.0, 1.8, 0.5
        tender = True
    else:   # "T": small tank engine
        lead, drv, trail, rd = [3.3], [1.8, 0.4, -1.0], [-2.7, -3.8], 0.55
        x_sf, x_fb, rb, zb = 3.6, -1.7, 0.72, 2.25
        cab0, cab1, cyl_x, stack_x, dome_x, sand_x = -3.5, -1.7, 2.5, 3.1, 1.0, -0.1
        tender = False
    W = 2.9 if kind != "T" else 2.7
    h = W / 2
    pin_r = 0.30 if kind != "T" else 0.24
    # -------- wheels
    for x in drv:
        driver(v, x, rd, ang=ang)
    for x in lead + trail:
        truck_wheel(v, x, 0.43 if kind != "T" else 0.40)
    x_lo = min(drv + lead + trail) - 0.5
    x_hi = x_sf + 0.3
    # -------- frames + axleboxes
    fr = v.A("black", 0.01)
    for s in (-1, 1):
        fr.box(x_lo, x_hi, *sorted((s * 0.70, s * 0.78)), 0.80, 1.28)
        for x in drv:
            v.A("iron", 0.008).box(x - 0.22, x + 0.22, *sorted((s * 0.70, s * 0.88)), rd - 0.12, rd + 0.14)
            v.A("steel").cyl((x, s * 0.76, rd + 0.14), (x, s * 0.76, rd + 0.52), 0.07, 0.07, seg=8)
        for x in lead + trail:
            v.A("iron", 0.008).box(x - 0.14, x + 0.14, *sorted((s * 0.70, s * 0.86)), 0.3, 0.55)
        v.A("iron", 0.008).box(x_lo + 0.3, x_hi - 0.2, *sorted((s * 0.70, s * 0.74)), 0.95, 1.28)
    fr.box(x_lo, x_hi, -0.70, 0.70, 1.05, 1.28)
    fr.box(x_fb - 0.2, x_fb + 2.5, -1.15, 1.15, 0.78, 1.55) if False else None
    # -------- boiler
    b = v.A("black", 0.0, True)
    b.cyl((x_fb + 0.8, 0, zb), (x_sf - 0.15, 0, zb), rb, rb, seg=28, caps=False)
    v.A("black", 0.01).box(x_fb, x_fb + 2.3, -1.15, 1.15, 1.35, zb + 0.3)                                # firebox wrapper
    v.A("black", 0.01, True).cyl((x_fb, 0, zb + 0.28), (x_fb + 2.3, 0, zb + 0.28), rb + 0.15, rb + 0.15, seg=28)
    v.A("black", 0.0, True).cyl((x_sf - 0.5, 0, zb), (x_sf, 0, zb), rb + 0.03, rb + 0.03, seg=28)         # smokebox
    v.A("iron", 0.0, True).cyl((x_sf, 0, zb), (x_sf + 0.07, 0, zb), rb - 0.05, rb - 0.05, seg=28)        # smokebox door
    v.A("steel").cyl((x_sf + 0.07, 0, zb), (x_sf + 0.12, 0, zb), 0.16, 0.06, seg=12)                      # door handle
    for k in range(4):
        a_ = k * math.pi / 2 + 0.4
        v.A("steel").sbox((x_sf + 0.07, 0.8 * math.cos(a_) * 0.6, zb + 0.8 * math.sin(a_) * 0.6),
                          (x_sf + 0.07, 0.8 * math.cos(a_), zb + 0.8 * math.sin(a_)), 0.04, 0.03)
    for xb in np.arange(x_fb + 2.6, x_sf - 0.5, 0.95):
        v.A("steel").torus((xb, 0, zb), 'x', rb + 0.015, 0.025, segR=30, segr=4)                           # boiler bands
    # chimney, domes
    v.A("black", 0.0, True).cyl((stack_x, 0, zb + rb - 0.1), (stack_x, 0, zb + rb + 0.55), 0.28, 0.20, seg=14)
    v.A("black", 0.0, True).cyl((stack_x, 0, zb + rb + 0.5), (stack_x, 0, zb + rb + 0.82), 0.20, 0.30, seg=14)
    v.A("dark").cyl((stack_x, 0, zb + rb + 0.82), (stack_x, 0, zb + rb + 0.83), 0.24, 0.24, seg=14)
    v.A("black", 0.0, True).cyl((dome_x, 0, zb + rb - 0.15), (dome_x, 0, zb + rb + 0.42), 0.47, 0.47, seg=18)
    v.A("black", 0.0, True).sphere((dome_x, 0, zb + rb + 0.42), (0.47, 0.47, 0.2), seg=18, rings=6)
    v.A("black", 0.0, True).cyl((sand_x, 0, zb + rb - 0.15), (sand_x, 0, zb + rb + 0.30), 0.32, 0.32, seg=16)
    v.A("black", 0.0, True).sphere((sand_x, 0, zb + rb + 0.30), (0.32, 0.32, 0.14), seg=16, rings=5)
    v.A("brass").cyl((dome_x - 0.7, 0, zb + rb - 0.1), (dome_x - 0.7, 0, zb + rb + 0.28), 0.05, 0.05, seg=8)  # whistle
    v.A("brass").cyl((dome_x - 0.7, 0, zb + rb + 0.28), (dome_x - 0.7, 0, zb + rb + 0.34), 0.07, 0.03, seg=8)
    v.A("brass").sphere((x_fb + 0.9, 0, zb + rb + 0.15), (0.08, 0.08, 0.16), seg=8, rings=5)                   # safety valve
    if kind != "T":
        v.A("steel", 0.0, True).cyl((stack_x - 1.0, 0, zb + rb - 0.05), (stack_x - 1.0, 0, zb + rb + 0.28), 0.30, 0.30, seg=16)  # feed-water heater
    # headlamp
    v.A("black", 0.01).box(x_sf - 0.35, x_sf - 0.05, -0.2, 0.2, zb + rb - 0.02, zb + rb + 0.06)
    v.A("black", 0.0, True).cyl((x_sf - 0.3, 0, zb + rb + 0.26), (x_sf - 0.02, 0, zb + rb + 0.26), 0.22, 0.22, seg=16)
    v.A("lampglass").cyl((x_sf - 0.02, 0, zb + rb + 0.26), (x_sf, 0, zb + rb + 0.26), 0.17, 0.17, seg=16)
    # number plate + front beam + pilot + coupler + buffers
    v.end_plane(num_plate, 1, 0.0, 0.58, zb - 0.42, zb - 0.42 + 0.58 * 160 / 420, x_sf + 0.075)
    xb = x_sf + 0.15
    v.A("red", 0.012).box(xb, xb + 0.22, -1.38, 1.38, 0.82, 1.20)
    for s in (-1, 1):
        v.A("steel").cyl((xb + 0.22, s * 0.85, 1.02), (xb + 0.52, s * 0.85, 1.02), 0.11, 0.11, seg=12)
        v.A("steel").cyl((xb + 0.52, s * 0.85, 1.02), (xb + 0.54, s * 0.85, 1.02), 0.17, 0.17, seg=12)
    coupler(v, 1, xb + 0.22, z=0.88)
    for yy in (-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9):                       # pilot bars
        v.A("iron").sbox((xb + 0.02, yy, 0.88), (xb + 0.65, yy * 0.55, 0.36), 0.045, 0.06)
    v.A("iron").box(xb + 0.58, xb + 0.66, -0.55, 0.55, 0.32, 0.38)
    # -------- running boards, handrails, pipes
    for s in (-1, 1):
        v.A("iron", 0.006).box(x_fb + 0.3, x_sf - 0.3, *sorted((s * 1.0, s * 1.6)), 1.90, 1.95)
        v.A("black").box(x_fb + 0.3, x_sf - 0.3, *sorted((s * 1.6, s * 1.62)), 1.72, 1.95)
        n = int((x_sf - 0.5 - x_fb) / 1.3)
        for i in range(n + 1):
            xx = x_fb + 0.6 + (x_sf - 0.8 - x_fb - 0.3) * i / n
            grab_rail(v, (xx, s * 1.03, 1.95), (xx, s * 1.03, 2.85) if kind != "T" else (xx, s * 0.82, 2.6), 0.02, "steel")
        grab_rail(v, (x_fb + 0.6, s * 1.03, 2.85 if kind != "T" else 2.6), (x_sf - 0.3, s * 0.80, zb + 0.2), 0.022, "steel")
        for (px, py, pz) in ((x_sf - 0.3, s * 0.80, zb + 0.2), (x_fb + 0.6, s * 1.03, 2.85 if kind != "T" else 2.6)):
            pass
        v.A("steel").cyl((x_fb + 1.6, s * 0.5, zb + 0.65), (x_sf - 0.8, s * 0.5, zb + 0.72), 0.045, 0.045, seg=8)   # steam pipe
        v.A("steel").cyl((x_fb + 1.6, s * 0.0, zb + 0.97), (x_sf - 0.8, 0, zb + 0.97), 0.0, 0.0, seg=3) if False else None
    # air pump + tanks
    for s in (-1, 1):
        v.A("iron", 0.0, True).cyl((x_sf - 1.3, s * 1.3, 1.95), (x_sf - 1.3, s * 1.3, 2.75), 0.17, 0.17, seg=10)
        v.A("steel", 0.0, True).cyl((x_fb + 0.6, s * 1.35, 2.2), (x_fb + 2.0, s * 1.35, 2.2), 0.19, 0.19, seg=12)
    # -------- cylinders, rods, valve gear
    pin_x = drv[len(drv) // 2 if kind == "D" else 1] if kind != "T" else drv[1]
    ar = math.radians(ang)
    px, pz = pin_x + pin_r * math.cos(ar), rd + pin_r * math.sin(ar)
    zc = 1.02 if kind != "T" else 0.88
    Lmr = 2.9 if kind != "T" else 2.2
    xc = px + math.sqrt(Lmr ** 2 - (zc - pz) ** 2)
    for s in (-1, 1):
        y = s * 0.98
        v.A("iron", 0.012, True).cyl((cyl_x - 0.55, y, zc), (cyl_x + 0.55, y, zc), 0.27, 0.27, seg=16)
        v.A("steel", 0.0, True).cyl((cyl_x + 0.55, y, zc), (cyl_x + 0.62, y, zc), 0.20, 0.20, seg=14)
        v.A("iron", 0.01).box(cyl_x - 0.55, cyl_x + 0.55, *sorted((s * 0.98 - 0.15, s * 0.98 + 0.15)), zc + 0.22, zc + 0.46)   # steam chest
        v.A("steel").cyl((cyl_x - 0.55, y, zc), (xc, y, zc), 0.04, 0.04, seg=8)                                      # piston rod
        v.A("steel").box(xc - 0.12, xc + 0.04, *sorted((y - 0.06, y + 0.06)), zc - 0.07, zc + 0.07)                  # crosshead
        for dz in (-0.1, 0.1):
            v.A("steel").box(cyl_x - 0.55, xc + 0.25, *sorted((y - 0.03, y + 0.03)), zc + dz - 0.015, zc + dz + 0.015)  # slide bars
        yr = s * (y_rod := 0.5335 + 0.17)
        yr2 = s * (0.5335 + 0.215)
        v.A("steel", 0.003).sbox((xc, yr2, zc), (px, yr2, pz), 0.11, 0.045)                                          # main rod
        for x in drv:
            c = (x + pin_r * math.cos(ar), pin_r * math.sin(ar) + rd)
            v.A("steel").cyl((c[0], yr - s * 0.04, c[1]), (c[0], yr2 + s * 0.02, c[1]), 0.06, 0.06, seg=10)
        for i in range(len(drv) - 1):
            a0 = (drv[i] + pin_r * math.cos(ar), yr, rd + pin_r * math.sin(ar))
            a1 = (drv[i + 1] + pin_r * math.cos(ar), yr, rd + pin_r * math.sin(ar))
            v.A("steel", 0.003).sbox(a0, a1, 0.10, 0.04)
        # Walschaerts-style valve gear (simplified)
        ax = drv[len(drv) // 2 if kind == "D" else 1]
        ec = (ax + 0.18 * math.cos(ar + 1.57), s * 0.6, rd + 0.18 * math.sin(ar + 1.57))
        v.A("steel").sbox((ax, s * 0.62, rd), ec, 0.03, 0.03)
        v.A("steel").sbox((ec[0], s * 0.64, ec[2]), (ax + 0.9, s * 0.64, 1.62), 0.03, 0.04)
        v.A("steel").sbox((ax + 0.9, s * 0.64, 1.62), (cyl_x - 0.1, s * 0.64, 1.62), 0.04, 0.04)
        v.A("steel").sbox((ax + 0.5, s * 0.64, 1.55), (ax + 0.6, s * 0.64, 1.15), 0.03, 0.03)
        v.A("steel").sbox((ax + 1.0, s * 0.64, 1.62), (xc + 0.04, s * 0.64, zc + 0.1), 0.03, 0.03)
    # -------- cab
    for s in (-1, 1):
        wall_open(v, "black", 'y', cab0, cab1, s * (h - 0.06), s * h, 1.55, 3.55,
                  [(cab1 - 0.75, cab1 - 0.15, 2.3, 3.05), (cab0 + 0.45, cab0 + 1.05, 2.3, 3.05)], 0.01)
        v.A("black", 0.01).box(cab0, cab1, *sorted((s * (h - 0.06), s * (h + 0.0))), 1.40, 1.55)
    wall_open(v, "black", 'x', -h, h, cab1 - 0.05, cab1, 1.55, 3.55, [(-1.0, -0.2, 2.5, 3.0)], 0.01) if False else v.A("black", 0.01).box(cab1 - 0.05, cab1, -h, h, 1.55, 3.55)
    v.A("floorw").box(cab0, cab1, -h + 0.06, h - 0.06, 1.55, 1.58)
    v.A("black", 0.012).extrude_x(upper_profile(W + 0.2, 3.5, 3.58, 3.95 if kind != "T" else 3.85), cab0 - 0.25, cab1 + 0.2)
    gl = v.A("glass")
    for s in (-1, 1):
        for (a, bb) in ((cab1 - 0.75, cab1 - 0.15), (cab0 + 0.45, cab0 + 1.05)):
            gl.box(a, bb, *sorted((s * (h - 0.03), s * (h - 0.025))), 2.3, 3.05)
        v.A("iron").box(cab0, cab0 + 0.06, *sorted((s * (h - 0.1), s * h)), 1.55, 3.55)
    v.A("black").box(cab1 - 0.9, cab1 - 0.05, -0.5, 0.5, 1.58, 2.15)                       # backhead
    v.A("glow").box(cab1 - 0.93, cab1 - 0.9, -0.22, 0.22, 1.65, 1.95) if False else None
    v.A("dark").box(cab1 - 0.94, cab1 - 0.9, -0.22, 0.22, 1.66, 1.95)
    v.A("brass").cyl((cab1 - 0.1, -0.35, 2.4), (cab1 - 0.04, -0.35, 2.4), 0.08, 0.08, seg=12)
    v.A("brass").cyl((cab1 - 0.1, 0.35, 2.4), (cab1 - 0.04, 0.35, 2.4), 0.08, 0.08, seg=12)
    v.A("moq2").box(cab0 + 0.4, cab0 + 0.9, 0.6, 1.2, 1.58, 1.95)                            # driver's seat
    v.A("moq2").box(cab0 + 0.4, cab0 + 0.9, -1.2, -0.6, 1.58, 1.95)
    if crew:
        v.A("cl1", 0.03, True).box(cab0 + 0.45, cab0 + 0.85, -1.15, -0.65, 1.95, 2.45)
        v.A("skin", 0.0, True).sphere((cab0 + 0.65, -0.9, 2.62), (0.1, 0.09, 0.11), seg=8, rings=6)
        v.A("cl1", 0.0, True).sphere((cab0 + 0.65, -0.9, 2.72), (0.12, 0.11, 0.05), seg=8, rings=4)   # cap
    v.A("lamp_in").cyl((cab1 - 0.5, 0, 3.52), (cab1 - 0.5, 0, 3.55), 0.1, 0.1, seg=8)
    # cab side decals
    for s in (-1, 1):
        v.side_plane(num_plate, s, (cab0 + cab1) / 2 + 0.15, 0.55, 1.66, 1.66 + 0.55 * 160 / 420, s * (h + 0.012))
    # -------- tender or tank/bunker
    if tender:
        t0, t1 = cab0 - 0.15, cab0 - (6.0 if kind == "D" else 6.3)
        tw = 1.40
        v.A("black", 0.012).box(t1, t0, -tw, tw, 1.18, 2.35)
        v.A("black", 0.012).box(t1, t0 - 2.6, -tw + 0.05, tw - 0.05, 2.35, 2.6)
        v.A("black", 0.012).box(t0 - 2.6, t0, -tw, tw, 2.35, 2.45)
        v.A("black", 0.012).box(t1, t0, -tw, tw, 2.35, 2.62) if False else None
        for i in range(30):
            rr = random.Random(i)
            v.A("coal", 0.0, True).sphere((t0 - 0.3 - rr.uniform(0, 2.3), rr.uniform(-1.0, 1.0), rr.uniform(2.55, 2.85)),
                                          (rr.uniform(0.35, 0.65), rr.uniform(0.3, 0.6), rr.uniform(0.2, 0.38)), seg=8, rings=5)
        v.A("coal").box(t0 - 2.7, t0 - 0.1, -1.25, 1.25, 2.4, 2.6)
        v.A("iron", 0.01).box(t1 + 0.1, t0 - 2.8, -0.55, 0.55, 2.62, 2.74)                   # water hatch
        v.A("black", 0.0, True).cyl((t1 + 0.7, 0, 2.74), (t1 + 0.7, 0, 2.82), 0.42, 0.42, seg=14)
        for s in (-1, 1):
            v.A("iron", 0.006).box(t1, t0, *sorted((s * tw, s * (tw + 0.04))), 1.18, 1.22)
            v.A("iron", 0.006).box(t1, t0, *sorted((s * tw, s * (tw + 0.04))), 2.30, 2.36)
            grab_rail(v, (t1 + 0.4, s * (tw + 0.06), 1.2), (t1 + 0.4, s * (tw + 0.06), 2.5), 0.018, "iron")
            grab_rail(v, (t0 - 0.4, s * (tw + 0.06), 1.2), (t0 - 0.4, s * (tw + 0.06), 2.5), 0.018, "iron")
            v.side_plane("logo_new.png", s, (t0 + t1) / 2, 0.8, 1.5, 2.3, s * (tw + 0.012))
            v.side_plane("mark_depot.png", s, (t0 + t1) / 2 + 1.6, 1.4, 1.30, 1.30 + 1.4 * 120 / 500, s * (tw + 0.012)) if False else None
        v.A("iron", 0.01).box(t1, t0, -0.9, 0.9, 0.95, 1.18)
        v.A("black", 0.01).box(t0, cab0 + 0.05, -0.15, 0.15, 1.05, 1.18)                       # drawbar
        for dx in (0.0, -0.1):
            pass
        bx = (t0 + t1) / 2
        for xx in (bx - 1.5, bx + 1.5):
            bogie2(v, xx, wb=1.9)
        coupler(v, -1, t1)
        v.A("iron", 0.01).box(t1 - 0.12, t1, -1.2, 1.2, 0.85, 1.12)
    else:
        for s in (-1, 1):
            v.A("black", 0.012).box(x_fb + 0.1, x_sf - 0.9, *sorted((s * 0.8, s * 1.35)), 1.55, 2.5)          # side tanks
            v.A("iron", 0.006).box(x_fb + 0.1, x_sf - 0.9, *sorted((s * 0.78, s * 1.37)), 2.5, 2.55)
        v.A("black", 0.012).box(cab0 - 1.25, cab0, -1.25, 1.25, 1.55, 2.6)                                  # bunker
        v.A("coal").box(cab0 - 1.15, cab0 - 0.05, -1.15, 1.15, 2.6, 2.75)
        coupler(v, -1, cab0 - 1.25, z=0.88)
        v.A("iron", 0.01).box(cab0 - 1.37, cab0 - 1.25, -1.2, 1.2, 0.85, 1.12)
        for s in (-1, 1):
            v.side_plane("logo_new.png", s, cab0 - 0.65, 0.7, 1.65, 2.4, s * (1.25 + 0.012))
    if smoke:
        rr = random.Random(5)
        for i in range(14):
            t = i / 13.0
            v.A("steam", 0.0, True).sphere((stack_x - 0.4 * t - rr.uniform(-0.1, 0.1), rr.uniform(-0.2, 0.2) * (1 + t) + 0.3 * t,
                                            zb + rb + 0.95 + 1.1 * t + rr.uniform(-0.1, 0.1)),
                                           (0.2 + 0.55 * t, 0.2 + 0.55 * t, 0.17 + 0.5 * t), seg=10, rings=6)
        for s in (-1, 1):
            for i in range(3):
                v.A("steam", 0.0, True).sphere((cyl_x + 0.3 + 0.2 * i, s * (1.2 + 0.25 * i), 0.45 + 0.1 * i), (0.22 + 0.1 * i,) * 3, seg=8, rings=5)
    return v
