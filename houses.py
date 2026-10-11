"""Furnished buildings of the town (hollow, with interiors): farmhouse, inn, shop, kura, goods shed, crossing hut, hokora."""
from common import *
import lib
import props
from props import G, face_plane, gable_roof, FOOT
import rooms as R
from rooms import A, shell, partition, floor_tatami, floor_boards, floor_dirt, ceiling, lamp_point


def farmhouse2(x, y, w=10.0, d=7.0, name="house", variant=0, seed=0, roofmat="kawara"):
    g = G(name, "Buildings")
    FOOT.append((x - 1, x + w + 3.6, y - 3.5, y + d + 1))
    rng = random.Random(seed + int(x * 7))
    zb = 0.45
    hf = 2.9
    zt = zb + hf
    x0, x1, y0, y1 = x, x + w, y, y + d
    t = 0.12
    Fz = 0.78
    Dz = 0.50
    # foundation stones (ring only) + engawa
    stone = A(g, "stone", 0.02)
    for (a, b, c, e) in ((x0 - 0.1, x1 + 0.1, y0 - 0.1, y0 + 0.2), (x0 - 0.1, x1 + 0.1, y1 - 0.2, y1 + 0.1),
                         (x0 - 0.1, x0 + 0.2, y0, y1), (x1 - 0.2, x1 + 0.1, y0, y1)):
        stone.box(a, b, c, e, -0.3, zb)
    ud = w - 3.6                            # raised-floor width; doma beyond
    yr = y0 + d * 0.58                      # front/back room divider
    xz = x0 + (4.0 if variant == 0 else 3.6)     # zashiki | tsugi divider
    ops = {
        "S": [(x0 + 0.35, xz - 0.35, Fz + 0.02, 2.55, 'slide'),
              (xz + 0.35, min(xz + 2.6, x0 + ud - 0.4), Fz + 0.25, 2.3, 'glass'),
              (x1 - 3.0, x1 - 1.3, Dz + 0.02, 2.55, 'door')],
        "N": [(x0 + 1.0, x0 + 2.5, Fz + 0.5, 2.3, 'glass'), (x0 + ud + 0.5, x0 + ud + 1.7, Fz + 0.6, 2.3, 'glass')],
        "W": [(y0 + d * 0.62, y0 + d * 0.62 + 1.2, Fz + 0.5, 2.3, 'glass')],
        "E": [(y1 - 2.2, y1 - 1.2, Fz + 0.6, 2.2, 'glass')],
    }
    shell(g, x0, x1, y0, y1, zb, zt, t, ops)
    # exterior detail: engawa, gutter, roof
    eg = A(g, "floor", 0.01)
    eg.box(x0 + 0.3, x0 + ud, y0 - 0.95, y0 - 0.0, Fz - 0.1, Fz - 0.04)
    for xx in np.linspace(x0 + 0.5, x0 + ud - 0.2, 5):
        A(g, "wood", 0.01).box(xx - 0.05, xx + 0.05, y0 - 0.9, y0 - 0.8, 0.0, Fz - 0.1)
    kw, wl = g.a(roofmat), g.a("wall")
    gable_roof(kw, wl, x0, x1, y0, y1, zt, 2.0 + 0.25 * (d - 7), ov=0.9, gov=0.6)
    g.a("iron_black").sbox((x0, y0 - 0.85, zt - 0.18), (x1, y0 - 0.85, zt - 0.18), 0.1, 0.1)
    # ---- interior
    floor_tatami(g, x0 + t, xz - 0.03, y0 + t, yr - 0.03, Fz, 'x')            # zashiki 8 mats
    floor_tatami(g, xz + 0.03, x0 + ud - 0.03, y0 + t, yr - 0.03, Fz, 'x')   # tsugi-no-ma
    floor_tatami(g, x0 + t, xz - 0.03, yr + 0.03, y1 - t, Fz, 'x')           # nando (bedroom)
    floor_boards(g, xz + 0.03, x0 + ud - 0.03, yr + 0.03, y1 - t, Fz)       # kitchen-side itanoma
    floor_dirt(g, x0 + ud + 0.03, x1 - t, y0 + t, y1 - t, Dz)
    # raised step edge (kamachi beam)
    A(g, "wood_dark", 0.01).box(x0 + ud - 0.08, x0 + ud + 0.02, y0 + t, y1 - t, Dz, Fz + 0.02)
    zc = Fz + 2.0
    ceiling(g, x0 + t, x0 + ud, y0 + t, y1 - t, zc, 'y')
    for yy in np.linspace(y0 + 0.6, y1 - 0.6, 4):
        A(g, "wood_dark", 0.02).box(x0 + ud, x1 - t, yy - 0.12, yy + 0.12, zt - 0.5, zt - 0.2)       # doma beams (open to rafters)
    partition(g, 'x', yr, x0 + t, x0 + ud, Fz, zc, doors=[(x0 + 1.2, x0 + 2.2), (xz + 0.2, xz + 1.2)], kind="fusuma")
    partition(g, 'y', xz, y0 + t, yr, Fz, zc, doors=[(y0 + 0.9, y0 + 2.4)], kind="paper")
    # plaster lining on the bare walls so the room is not just raw boards
    # zashiki
    R.chabudai(g, x0 + 2.0, y0 + 1.7, Fz)
    R.butsudan(g, x0 + 0.62, yr - 0.4, Fz, face='S') if False else None
    R.kamidana(g, x0 + 2.2, yr - 0.1, zc - 0.5, face='S')
    R.butsudan(g, x0 + 0.6, y0 + 1.5, Fz, face='E') if False else R.butsudan(g, x0 + 1.5, yr - 0.34, Fz, face='S')
    # tsugi
    R.tansu(g, xz + 1.0, yr - 0.3, Fz, face='S')
    R.low_table(g, xz + 1.8, y0 + 1.5, Fz)
    R.zabuton(g, xz + 1.8, y0 + 0.8, Fz)
    # nando: futon + tansu
    R.futon(g, x0 + 1.5, y0 + d * 0.8, Fz, 'x')
    R.tansu(g, x0 + 3.4, y1 - 0.3, Fz, face='S')
    # itanoma: shelves + kitchen table
    R.shelf(g, xz + 0.3, xz + 2.3, y1 - t, Fz, h=1.7, rows=3, face='S', goods="boxes", seed=seed)
    R.low_table(g, xz + 1.5, yr + 0.9, Fz, 1.2, 0.7)
    # doma
    R.kamado(g, x1 - 1.6, y1 - 0.7, Dz, face='S')
    R.sink_stone(g, x1 - 3.0, y1 - 0.5, Dz)
    R.water_jar(g, x1 - 0.55, y1 - 0.6, Dz)
    R.water_jar(g, x1 - 0.5, y0 + 0.7, Dz)
    R.shelf(g, x0 + ud + 0.2, x0 + ud + 1.5, y1 - t, Dz, h=1.9, rows=4, face='S', goods="jars", seed=seed + 1)
    A(g, "wood", 0.01).box(x1 - 3.1, x1 - 1.9, y0 + 2.0, y0 + 2.7, Dz + 0.7, Dz + 0.75)       # prep table
    for a in (-1, 1):
        for b in (-1, 1):
            A(g, "wood").box(x1 - 2.5 + a * 0.5 - 0.03, x1 - 2.5 + a * 0.5 + 0.03, y0 + 2.35 + b * 0.3 - 0.03, y0 + 2.35 + b * 0.3 + 0.03, Dz, Dz + 0.7)
    props.G.a(g, "sack").box(0, 0, 0, 0, 0, 0) if False else None
    R.sack_pile(g, x1 - 1.4, y0 + 3.2, Dz, nx=2, ny=1, nz=3, seed=seed)
    # farm tools hung on the wall
    for k in range(3):
        A(g, "iron_rust").sbox((x1 - 0.2, y0 + 1.5 + k * 0.5, Dz + 2.0), (x1 - 0.2, y0 + 1.5 + k * 0.5, Dz + 0.9), 0.04, 0.02)
    lamp_point((x0 + xz) / 2, (y0 + yr) / 2, zc - 0.25, 22)
    lamp_point((xz + x0 + ud) / 2, (y0 + yr) / 2, zc - 0.25, 18)
    lamp_point((x0 + xz) / 2, (yr + y1) / 2, zc - 0.25, 14)
    lamp_point(x1 - 1.8, (y0 + y1) / 2, zt - 0.7, 40)
    # annex: bath shed / wood store on the east end, open to the front
    ax0, ax1 = x1, x1 + 2.6
    shell(g, ax0, ax1, y0 + 1.0, y0 + 4.6, zb, zb + 2.5, 0.1, {"S": [(ax0 + 0.2, ax1 - 0.2, zb + 0.05, zb + 2.2, 'open')]})
    A(g, "tin").extrude_x([(y0 + 0.4, zb + 2.75), (y0 + 5.2, zb + 2.35), (y0 + 5.2, zb + 2.3), (y0 + 0.4, zb + 2.70)], ax0 - 0.1, ax1 + 0.4)
    A(g, "concrete", 0.01).box(ax0 + 1.8, ax0 + 2.2, y0 + 3.6, y0 + 4.0, zb + 2.4, zb + 5.0)
    A(g, "dirt_floor").box(ax0 + 0.1, ax1 - 0.1, y0 + 1.1, y0 + 4.5, 0.0, zb)
    A(g, "iron_black", 0.02).cyl((ax0 + 1.3, y0 + 3.2, zb), (ax0 + 1.3, y0 + 3.2, zb + 0.85), 0.5, seg=16)     # goemon-buro
    A(g, "wood", 0.01).cyl((ax0 + 1.3, y0 + 3.2, zb + 0.85), (ax0 + 1.3, y0 + 3.2, zb + 0.88), 0.46, seg=16)
    for i in range(6):
        for k in range(4):
            A(g, "wood").cyl((ax0 + 0.3 + i * 0.1, y0 + 1.3, zb + 0.06 + k * 0.1), (ax0 + 0.3 + i * 0.1, y0 + 2.3, zb + 0.06 + k * 0.1), 0.05, seg=6) if False else None
    for k in range(4):
        for i in range(8):
            A(g, "wood").cyl((ax0 + 0.2 + i * 0.1, y0 + 1.2, zb + 0.08 + k * 0.1), (ax0 + 0.2 + i * 0.1, y0 + 2.2, zb + 0.08 + k * 0.1), 0.045, seg=6)
    lamp_point(ax0 + 1.3, y0 + 2.8, zb + 2.0, 12)
    # clothes pole
    A(g, "wood").cyl((x0 + 2.0, y0 - 2.5, 0.0), (x0 + 2.0, y0 - 2.5, 2.4), 0.04, seg=6)
    A(g, "wood").cyl((x0 + 4.0, y0 - 2.5, 0.0), (x0 + 4.0, y0 - 2.5, 2.4), 0.04, seg=6)
    A(g, "wood").cyl((x0 + 2.0, y0 - 2.5, 2.3), (x0 + 4.0, y0 - 2.5, 2.3), 0.025, seg=6)
    g.build()
    cl = [lib.mat_plain(f"pb_cloth{i}", c, rough=0.9) for i, c in enumerate(
        [(0.75, 0.74, 0.70), (0.2, 0.28, 0.45), (0.65, 0.60, 0.45), (0.5, 0.15, 0.12)])]
    for k in range(4):
        cc = Acc(f"{name}_cloth{k}", cl[k], "Buildings")
        cc.box(x0 + 2.1 + k * 0.45, x0 + 2.45 + k * 0.45, y0 - 2.52, y0 - 2.48, 1.45 + rng.uniform(0, 0.2), 2.25)
        cc.build()


def kura2(x, y, w=4.4, d=5.6, name="kura"):
    g = G(name, "Buildings")
    FOOT.append((x - 1, x + w + 1, y - 1.5, y + d + 1))
    t = 0.35
    zt = 3.6
    ops = {"S": [(x + w / 2 - 0.9, x + w / 2 + 0.9, 0.35, 2.45, 'door')], "N": [(x + 1.7, x + 2.7, 2.0, 2.7, 'open')]}
    shell(g, x, x + w, y, y + d, 0.0, zt, t, ops, wall="plaster2")
    A(g, "wood_dark", 0.01).box(x - 0.03, x + w + 0.03, y - 0.03, y + d + 0.03, 0.0, 1.0)
    A(g, "stone", 0.02).box(x - 0.1, x + w + 0.1, y - 0.1, y + d + 0.1, -0.3, 0.2)
    kw, wl = g.a("kawara"), g.a("plaster2")
    gable_roof(kw, wl, x, x + w, y, y + d, zt, 1.9, ov=0.7, gov=0.4)
    dk = A(g, "iron_black", 0.01)
    for k in range(5):
        dk.sbox((x + w / 2 - 0.85, y - 0.03, 0.7 + k * 0.32), (x + w / 2 + 0.85, y - 0.03, 0.7 + k * 0.32), 0.03, 0.03)
    A(g, "plaster").box(x + w / 2 - 1.15, x + w / 2 + 1.15, y - 0.2, y - 0.05, 2.5, 2.65)
    # interior: plank floor, upper deck, shelves, chests, ladder
    floor_boards(g, x + t, x + w - t, y + t, y + d - t, 0.15)
    z2 = 2.1
    A(g, "floor", 0.01).box(x + t, x + w - t, y + t + 1.6, y + d - t, z2 - 0.08, z2)
    for xx in np.linspace(x + t + 0.3, x + w - t - 0.3, 5):
        A(g, "wood_dark", 0.01).box(xx - 0.07, xx + 0.07, y + t, y + d - t, z2 - 0.28, z2 - 0.08)
    R.shelf(g, x + t, x + w - t, y + d - t, 0.15, h=1.9, rows=4, face='S', goods="boxes", seed=4, key="wood_dark")
    R.shelf(g, x + t + 0.1, x + 1.9, y + d - t, z2, h=1.4, rows=3, face='S', goods="jars", seed=5)
    for i in range(3):
        A(g, "wood_dark", 0.015).box(x + 0.5 + i * 1.2, x + 1.5 + i * 1.2, y + 1.0, y + 1.6, 0.15, 0.7)     # nagamochi chests
        A(g, "iron_black").box(x + 0.9 + i * 1.2, x + 1.1 + i * 1.2, y + 0.98, y + 1.0, 0.35, 0.5)
    A(g, "tin").cyl((x + 3.7, y + 1.4, 0.15), (x + 3.7, y + 1.4, 1.0), 0.3, seg=12)
    for s in (-1, 1):
        A(g, "wood").sbox((x + 1.0 + s * 0.25, y + 1.8, 0.15), (x + 1.0 + s * 0.25, y + 2.0, z2 + 0.8), 0.05, 0.04)
    for k in range(7):
        A(g, "wood").sbox((x + 0.75, y + 1.8 + k * 0.03, 0.4 + k * 0.33), (x + 1.25, y + 1.8 + k * 0.03, 0.4 + k * 0.33), 0.03, 0.03)
    lamp_point(x + w / 2, y + 2.5, 1.6, 25)
    lamp_point(x + w / 2, y + 4.0, 3.0, 12)
    g.build()


def shop2(x, y, w=8.0, d=6.0, name="shop"):
    g = G(name, "Buildings")
    FOOT.append((x - 1, x + w + 1, y - 2.5, y + d + 1))
    zb, zt = 0.25, 3.3
    t = 0.12
    ops = {"S": [(x + 0.6, x + 5.2, 0.5, 2.4, 'glass'), (x + 5.5, x + 7.4, 0.5, 2.5, 'open')],
           "N": [(x + 1.0, x + 2.2, 1.2, 2.2, 'glass'), (x + 5.0, x + 6.0, 0.8, 2.2, 'door')],
           "W": [(y + 2.0, y + 3.2, 1.2, 2.2, 'glass')], "E": [(y + 1.5, y + 2.5, 1.2, 2.2, 'glass')]}
    shell(g, x, x + w, y, y + d, zb, zt, t, ops)
    A(g, "stone", 0.02).box(x - 0.1, x + w + 0.1, y - 0.1, y + d + 0.1, -0.3, zb)
    kw, wl = g.a("kawara"), g.a("wall")
    gable_roof(kw, wl, x, x + w, y, y + d, zt, 1.7, ov=0.8, gov=0.5)
    A(g, "tin").extrude_x([(y - 1.6, 2.55), (y - 0.1, 2.95), (y - 0.1, 3.0), (y - 1.6, 2.6)], x - 0.1, x + w + 0.1)
    for xx in (x + 0.1, x + w - 0.1):
        A(g, "wood", 0.01).box(xx - 0.07, xx + 0.07, y - 1.55, y - 1.41, 0.0, 2.6)
    # exterior goods
    cr = A(g, "crate", 0.01)
    for i in range(3):
        cr.box(x + 0.9 + i * 0.7, x + 1.5 + i * 0.7, y - 0.8, y - 0.35, 0.0, 0.32)
        for j in range(5):
            A(g, "bottle").cyl((x + 0.98 + i * 0.7 + (j % 3) * 0.17, y - 0.7 + (j // 3) * 0.2, 0.32), (x + 0.98 + i * 0.7 + (j % 3) * 0.17, y - 0.7 + (j // 3) * 0.2, 0.52), 0.035, seg=8)
    # interior: dirt floor, plank step for the shop-keeper's room, shelves, counter
    floor_dirt(g, x + t, x + w - t, y + t, y + d - t, zb)
    zf = 0.7
    floor_boards(g, x + t, x + w - t, y + d - 2.2, y + d - t, zf)
    floor_tatami(g, x + 2.5, x + w - t, y + d - 2.15, y + d - t, zf, 'x') if False else None
    R.shelf(g, x + 0.3, x + w - 0.3, y + d - 2.2 - 0.0, zf, h=1.9, rows=4, face='S', goods="mixed", seed=7) if False else None
    R.shelf(g, x + 0.3, x + 3.8, y + t, zb, h=2.0, rows=5, face='N', goods="mixed", seed=8, key="wood_dark")
    R.shelf(g, x + 4.3, x + 7.6, y + d - t - 0.35, zb, h=2.0, rows=5, face='N', goods="mixed", seed=9, key="wood_dark") if False else None
    R.shelf(g, x + 0.3, x + w - 0.3, y + d - t, zb, h=2.1, rows=5, face='S', goods="mixed", seed=10, key="wood_dark")
    R.counter(g, x + 1.2, x + 4.6, y + 2.3, zb, d=0.7)
    A(g, "iron_black", 0.01).box(x + 3.6, x + 4.1, y + 2.2, y + 2.6, zb + 0.95, zb + 1.2)           # cash register / abacus
    A(g, "wood_dark").box(x + 4.15, x + 4.45, y + 2.2, y + 2.55, zb + 0.95, zb + 1.0)
    # center island: barrels + sacks (rice, beans)
    R.barrel(g, x + 5.6, y + 1.5, zb)
    R.barrel(g, x + 6.3, y + 1.8, zb)
    R.sack_pile(g, x + 5.3, y + 3.0, zb, nx=3, ny=1, nz=2, seed=3)
    # glass-door cooler / ice box
    A(g, "enamel", 0.02).box(x + 0.4, x + 1.4, y + 4.0, y + 4.7, zb, zb + 1.1)
    A(g, "glass").box(x + 0.45, x + 1.35, y + 4.0 - 0.02, y + 4.0, zb + 0.5, zb + 1.05)
    # tatami corner (shop-keeper's rest) with low table
    floor_tatami(g, x + 2.0, x + 5.2, y + d - 2.0, y + d - t - 0.001, zf, 'x') if False else None
    R.chabudai(g, x + 6.0, y + d - 1.1, zf)
    lamp_point(x + 2.5, y + 2.0, 2.7, 45)
    lamp_point(x + 6.0, y + d - 1.0, 2.7, 25)
    g.build()
    face_plane(name + "_adA", "ad_onsen.png", 'S', x + 6.0, y - 0.02, 2.55, 0.5) if False else None
    face_plane(name + "_adB", "ad_nokyo.png", 'S', x + 2.8, y - 0.02, 2.55, 0.0001) if False else None
    face_plane(name + "_ad1", "ad_fire.png", 'S', x + 7.65, y - 0.02, 1.4, 0.28)
    face_plane(name + "_sign", "shop_sign.png", 'S', x + w / 2, y - 1.63, 2.6, 3.4)
    face_plane(name + "_price", "price_board.png", 'E', x + t + 0.01, y + 4.5, 1.2, 0.8)
    face_plane(name + "_ad2", "ad_safety.png", 'S', x + 4.0, y - 0.02, 2.55, 0.5) if False else None
    face_plane(name + "_vend", "vending.png", 'S', x + 5.9, y - 0.95, 0.0, 0.62) if False else None


def inn2(x, y, w=13.5, d=8.0, name="inn"):
    g = G(name, "Buildings")
    FOOT.append((x - 1, x + w + 1, y - 3.5, y + d + 1))
    zb = 0.45
    zt = 6.0
    t = 0.14
    F1, F2 = 0.78, 3.55
    xs = [x + 0.5 + 2.8 * i for i in range(4)]
    ops = {"S": [(x + 0.4, x + 3.6, F1 + 0.02, 2.55, 'slide'),
                 (x + 4.2, x + 6.4, F1 + 0.3, 2.4, 'glass'),
                 (x + 6.8, x + 9.6, 0.5, 2.6, 'open')] +
                [(x + 0.6 + 2.2 * i, x + 2.4 + 2.2 * i, F2 + 0.25, 5.15, 'slide') for i in range(5)],
           "N": [(x + 1.0, x + 2.3, F1 + 0.6, 2.4, 'glass'), (x + 4.5, x + 5.8, F1 + 0.6, 2.4, 'glass'), (x + 9.0, x + 10.2, F1 + 0.6, 2.4, 'glass')] +
                [(x + 1.0 + 3.2 * i, x + 2.3 + 3.2 * i, F2 + 0.6, 5.15, 'glass') for i in range(4)],
           "W": [(y + 3.0, y + 4.2, F1 + 0.6, 2.4, 'glass'), (y + 3.0, y + 4.2, F2 + 0.6, 5.15, 'glass')],
           "E": [(y + 3.0, y + 4.2, F1 + 0.6, 2.4, 'glass'), (y + 3.0, y + 4.2, F2 + 0.6, 5.15, 'glass')]}
    shell(g, x, x + w, y, y + d, zb, zt, t, ops)
    A(g, "wood_dark", 0.01).box(x - 0.1, x + w + 0.1, y - 0.1, y + d + 0.1, F2 - 0.4, F2 - 0.05)    # 2F band beam on the outside
    for (a, b, c, e) in ((x - 0.1, x + w + 0.1, y - 0.1, y + 0.2), (x - 0.1, x + w + 0.1, y + d - 0.2, y + d + 0.1),
                         (x - 0.1, x + 0.2, y, y + d), (x + w - 0.2, x + w + 0.1, y, y + d)):
        A(g, "stone", 0.02).box(a, b, c, e, -0.3, zb)
    kw, wl = g.a("kawara"), g.a("wall")
    gable_roof(kw, wl, x, x + w, y, y + d, zt, 2.3, ov=1.0, gov=0.7)
    # balcony on the south side, 2F
    A(g, "floor", 0.01).box(x + 0.2, x + w - 0.2, y - 1.0, y, F2 - 0.1, F2 - 0.03)
    for xx in np.linspace(x + 0.3, x + w - 0.3, 14):
        A(g, "wood_dark").box(xx - 0.03, xx + 0.03, y - 0.98, y - 0.92, F2 - 0.03, F2 + 0.95)
    A(g, "wood_dark", 0.01).box(x + 0.2, x + w - 0.2, y - 1.0, y - 0.9, F2 + 0.9, F2 + 0.97)
    for xx in (x + 0.3, x + w / 2, x + w - 0.3):
        A(g, "wood", 0.01).box(xx - 0.08, xx + 0.08, y - 0.98, y - 0.82, 0.0, F2 - 0.1)
    # ---------------- ground floor
    floor_dirt(g, x + 4.0, x + 9.8, y + t, y + 4.2, 0.5)                 # genkan earth-floor entrance
    floor_boards(g, x + t, x + 4.0, y + t, y + d - t, F1)               # reception / dining boards
    floor_tatami(g, x + 9.8, x + w - t, y + t, y + d - t, F1, 'x')      # tatami room east
    floor_boards(g, x + 4.0, x + 9.8, y + 4.2, y + d - t, F1)           # corridor + stair hall
    A(g, "wood_dark", 0.01).box(x + 3.9, x + 4.0, y + t, y + 4.2, 0.5, F1 + 0.03)
    # 天井は階段の吹き抜け(x+8.2..9.3, y+4.4..階段終端)を避けて張る
    _sx0, _sx1, _sy0, _sy1 = x + 8.2, x + 9.3, y + 4.4, y + 4.4 + 14 * 0.21 + 0.1
    ceiling(g, x + t, _sx0, y + t, y + d - t, F2 - 0.3, 'y')
    ceiling(g, _sx1, x + w - t, y + t, y + d - t, F2 - 0.3, 'y')
    ceiling(g, _sx0, _sx1, y + t, _sy0, F2 - 0.3, 'y')
    ceiling(g, _sx0, _sx1, _sy1, y + d - t, F2 - 0.3, 'y')
    # reception desk + key rack
    R.counter(g, x + 0.5, x + 3.4, y + 3.0, F1, d=0.6)
    for k in range(10):
        A(g, "gold").cyl((x + 0.7 + k * 0.28, y + d - t - 0.04, F1 + 1.7), (x + 0.7 + k * 0.28, y + d - t - 0.04, F1 + 1.8), 0.02, seg=6)
    R.shelf(g, x + 0.4, x + 3.5, y + d - t, F1, h=1.9, rows=4, face='S', goods="mixed", seed=11, key="wood_dark")
    R.low_table(g, x + 1.5, y + 1.3, F1, 1.2, 0.7) if False else None
    for k in range(2):
        R.low_table(g, x + 1.2 + k * 1.6, y + 1.2, F1)
        R.zabuton(g, x + 1.2 + k * 1.6, y + 1.9, F1)
        R.zabuton(g, x + 1.2 + k * 1.6, y + 0.6, F1)
    R.pot_stove(g, x + 3.2, y + 0.9, F1, pipe_to=F2 - 0.3)
    # shoe boxes in the genkan
    A(g, "wood_dark", 0.01).box(x + 4.1, x + 5.7, y + t, y + 0.5, 0.5, 1.4)
    for k in range(4):
        A(g, "leather", 0.03).box(x + 4.3 + k * 0.35, x + 4.55 + k * 0.35, y + 0.7, y + 0.95, 0.5, 0.58)
    # stair (straight, along y) in the stair hall: x 8.3..9.3, rising toward +y
    ns = 14
    sh = (F2 - F1) / ns
    for k in range(ns):
        A(g, "wood", 0.006).box(x + 8.2, x + 9.3, y + 4.4 + k * 0.21, y + 4.4 + (k + 1) * 0.21, F1, F1 + (k + 1) * sh)
    # 2F deck: opening above the stair
    A(g, "floor", 0.006).box(x + t, x + w - t, y + t, y + d - t, F2 - 0.06, F2) if False else None
    deck = A(g, "floor", 0.006)
    deck.box(x + t, x + w - t, y + t, y + 4.4, F2 - 0.08, F2)
    deck.box(x + t, x + 8.2, y + 4.4, y + d - t, F2 - 0.08, F2)
    deck.box(x + 9.3, x + w - t, y + 4.4, y + d - t, F2 - 0.08, F2)
    deck.box(x + 8.2, x + 9.3, y + 4.4 + ns * 0.21, y + d - t, F2 - 0.08, F2)
    # east tatami room: low table + zabuton + butsudan
    R.chabudai(g, x + 11.4, y + 4.0, F1)
    R.tansu(g, x + 12.9, y + 6.2, F1, face='W') if False else R.tansu(g, x + 11.5, y + d - 0.4, F1, face='S')
    partition(g, 'y', x + 9.8, y + t, y + d - t, F1, F2 - 0.3, doors=[(y + 3.4, y + 4.8)], kind="fusuma")
    # ---------------- second floor
    zc2 = zt - 1.0
    corr_y = y + 1.6         # corridor along the south side (y+t .. corr_y)
    floor_boards(g, x + t, x + w - t, y + t, corr_y, F2) if False else None
    A(g, "floor", 0.004).box(x + t, x + w - t, y + t, corr_y, F2, F2 + 0.02)
    xr = [x + t, x + 3.5, x + 6.9, x + 10.2, x + w - t]
    for i in range(4):
        floor_tatami(g, xr[i] + (0.06 if i else 0), xr[i + 1] - 0.03, corr_y + 0.03, y + d - t, F2 + 0.02, 'x')
        if i:
            partition(g, 'y', xr[i], corr_y, y + d - t, F2 + 0.02, zc2, doors=[(corr_y + 0.2, corr_y + 1.2)], kind="fusuma")
        # room contents
        cx = (xr[i] + xr[i + 1]) / 2
        R.low_table(g, cx, y + 4.6, F2 + 0.02)
        R.zabuton(g, cx - 0.6, y + 4.6, F2 + 0.02)
        R.zabuton(g, cx + 0.6, y + 4.6, F2 + 0.02)
        if i % 2 == 0:
            R.futon(g, cx - 0.2, y + 6.4, F2 + 0.02, 'x', c="futon" if i == 0 else "futon2")
        R.toko_alcove(g, xr[i + 1] - 1.4, xr[i + 1] - 0.1, y + d - t - 0.8, y + d - t, F2 + 0.02, F2 + 2.3) if False else None
        lamp_point(cx, y + 5.0, zc2 - 0.2, 20)
    partition(g, 'x', corr_y, x + t, x + w - t, F2 + 0.02, zc2,
              doors=[(xr[i] + 0.4, xr[i] + 1.4) for i in range(4)], kind="paper")
    A(g, "ceiling").box(x + t, x + w - t, y + t, y + d - t, zc2, zc2 + 0.04)
    lamp_point(x + 2.0, y + 2.2, F1 + 2.0, 45)
    lamp_point(x + 7.0, y + 6.0, F1 + 1.9, 30)
    lamp_point(x + 11.6, y + 4.0, F1 + 1.9, 25)
    lamp_point(x + 6.0, y + 1.0, F2 + 1.5, 25)
    # sign
    g.build()
    face_plane(name + "_ekimae", "ekimae.png", 'S', x + w * 0.5, y - 1.08, F2 + 1.1, 3.4)
    face_plane(name + "_tariff", "inn_tariff.png", 'S', x + 11.2, y - 0.02, 0.9, 0.9)
    face_plane(name + "_menu", "menu_shokudo.png", 'N', x + 1.3, y + t + 0.01, F1 + 0.7, 0.8)
    gs = G(name + "_sign", "Buildings")
    for s in (-1, 1):
        gs.a("wood_dark").box(x + w * 0.5 + s * 1.7 - 0.05, x + w * 0.5 + s * 1.7 + 0.05, y - 1.1, y - 1.04, F2 + 1.0, F2 + 2.3)
    gs.build()


def goods_shed2(x0=6.0, x1=20.0, y0=5.9, y1=10.2):
    """Goods shed with interior: scale, rice bales, parcel racks, small office corner with stove."""
    g = G("goods_shed", "Buildings")
    props.FOOT.append((x0 - 1, x1 + 1, y0 - 1.0, y1 + 3.0))
    zb = 0.45
    zt = zb + 3.5
    t = 0.14
    ops = {"N": [(xc - 1.6, xc + 1.6, 0.95 + 0.05, 3.35, 'open') for xc in (9.0, 13.0, 17.0)],
           "S": [(xc - 1.0, xc + 1.0, 0.5, 2.7, 'open') for xc in (10.0, 16.0)] + [(12.0, 14.0, 1.8, 2.8, 'glass'), (7.0, 8.4, 1.8, 2.8, 'glass')],
           "W": [(y0 + 1.2, y0 + 2.4, 1.6, 2.7, 'glass')], "E": [(y0 + 1.0, y0 + 2.4, 0.6, 2.7, 'open')]}
    shell(g, x0, x1, y0, y1, zb, zt, t, ops)
    A(g, "stone", 0.02).box(x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, -0.3, zb)
    tin = A(g, "tin")
    ym = (y0 + y1) / 2
    ov = 1.3
    tin.extrude_x([(y0 - ov, zb + 3.55), (ym, zb + 4.9), (y1 + ov, zb + 3.55), (y1 + ov, zb + 3.49), (ym, zb + 4.84), (y0 - ov, zb + 3.49)], x0 - 0.5, x1 + 0.5)
    A(g, "wall").extrude_x([(y0, zb + 3.5), (ym, zb + 4.8), (y1, zb + 3.5)], x0, x1)
    # exterior dock (kept from the old version)
    dock = A(g, "floor", 0.01)
    dock.box(x0 + 0.5, x1 - 0.5, y1, y1 + 1.5, 0.0, 0.95)
    A(g, "stone", 0.02).box(x0 + 0.5, x1 - 0.5, y1 + 1.5, y1 + 1.62, -0.1, 0.95)
    for xx in np.linspace(x0 + 0.6, x1 - 0.6, 6):
        A(g, "wood", 0.01).box(xx - 0.09, xx + 0.09, y1 + 1.35, y1 + 1.53, 0.95, 3.6)
    tin.extrude_x([(y1 + 1.8, 3.55), (y1 + 0.2, 4.2), (y1 + 0.2, 4.14), (y1 + 1.8, 3.49)], x0 + 0.2, x1 - 0.2)
    dw = A(g, "wood_dark", 0.01)
    for xc in (9.0, 13.0, 17.0):
        dw.box(xc - 1.6, xc - 0.1, y1, y1 + 0.07, 1.0, 3.35)          # door leaves parked beside the openings (open)
        dw.box(xc + 0.1, xc + 1.6, y1 + 0.07, y1 + 0.14, 1.0, 3.35) if False else None
        dw.box(xc - 1.7, xc + 1.7, y1 + 0.03, y1 + 0.17, 3.35, 3.5)
    # ---- interior
    A(g, "concrete").box(x0 + t, x1 - t, y0 + t, y1 - t, 0.0, 0.95) if False else None
    floor_boards(g, x0 + t, x1 - t, y0 + t, y1 - t, 0.95)
    A(g, "wood_dark", 0.01).box(x0 + t, x1 - t, y0 + t - 0.0, y1 - t, 0.0, 0.88)
    # rice bale stacks along the walls
    R.sack_pile(g, x0 + 0.5, y1 - 1.5, 0.95, nx=6, ny=2, nz=4, seed=1)
    R.sack_pile(g, x0 + 7.0, y1 - 1.4, 0.95, nx=5, ny=2, nz=3, seed=2)
    R.sack_pile(g, x0 + 10.2, y1 - 1.4, 0.95, nx=4, ny=2, nz=4, seed=9)
    R.sack_pile(g, x0 + 0.5, y0 + 0.5, 0.95, nx=3, ny=1, nz=3, seed=5)
    # platform scale (large beam scale)
    A(g, "iron_black", 0.02).box(x0 + 4.0, x0 + 5.4, y0 + 1.5, y0 + 2.5, 0.95, 1.08)
    A(g, "iron_black", 0.02).box(x0 + 5.5, x0 + 5.8, y0 + 1.9, y0 + 2.1, 0.95, 1.7)
    A(g, "tin").box(x0 + 5.35, x0 + 6.0, y0 + 1.85, y0 + 2.15, 1.7, 1.75)
    # parcel racks & crates
    R.shelf(g, x0 + 8.0, x0 + 11.5, y0 + t, 0.95, h=2.0, rows=4, face='N', goods="boxes", seed=21, key="wood_dark")
    for i in range(4):
        A(g, "crate", 0.015).box(x0 + 11.8 + i * 0.5, x0 + 12.25 + i * 0.5, y0 + 0.4, y0 + 0.9, 0.95, 1.4)
    # small office corner (west end): desk, stove, bench
    R.desk(g, x0 + 1.4, y0 + 1.8, 0.95, face='N')
    R.pot_stove(g, x0 + 3.0, y0 + 0.9, 0.95, pipe_to=zt + 0.8)
    A(g, "wood", 0.01).box(x0 + 0.3, x0 + 2.0, y0 + 0.25, y0 + 0.65, 1.3, 1.35)
    face_plane("shed_timetable_in", "timetable_old.png", 'N', x0 + 1.3, y0 + t + 0.01, 1.3, 0.6)
    lamp_point(x0 + 3.0, (y0 + y1) / 2, zt - 0.6, 60)
    lamp_point(x0 + 10.0, (y0 + y1) / 2, zt - 0.6, 60)
    g.build()
    face_plane("shed_sign", "goods_sign.png", 'N', 13.0, y1 + 0.2, 3.55, 5.0)
    face_plane("shed_notice", "notice.png", 'S', 8.2, y0 - 0.02, 1.5, 0.9)
    face_plane("shed_ad1", "ad_fire.png", 'S', 18.5, y0 - 0.02, 1.2, 0.5)
    face_plane("shed_ad2", "ad_nokyo.png", 'S', 19.0, y0 - 0.02, 2.2, 1.3)
    face_plane("shed_poster", "poster_savings.png", 'S', 11.6, y0 - 0.02, 1.4, 0.5)
    face_plane("shed_sabo", "sabo.png", 'S', 14.8, y0 - 0.02, 3.0, 1.5)


def hut2(hx0, hy0, name="xing_hut"):
    """Crossing keeper's hut: desk, stove, signal levers, bell, telephone, tea kettle."""
    g = G(name, "Props")
    zb = 0.2
    zt = 2.5
    ops = {"S": [(hx0 + 0.3, hx0 + 1.5, 1.1, 2.1, 'glass'), (hx0 + 1.7, hx0 + 2.5, zb + 0.02, 2.1, 'door')],
           "W": [(hy0 + 0.8, hy0 + 1.8, 1.1, 2.1, 'glass')], "E": [(hy0 + 0.8, hy0 + 1.8, 1.1, 2.1, 'glass')]}
    shell(g, hx0, hx0 + 2.8, hy0, hy0 + 2.6, zb, zt, 0.1, ops)
    A(g, "stone").box(hx0 - 0.08, hx0 + 2.88, hy0 - 0.08, hy0 + 2.68, -0.2, zb)
    A(g, "tin").extrude_x([(hy0 - 0.4, 2.55), (hy0 + 1.3, 3.2), (hy0 + 3.0, 2.55), (hy0 + 3.0, 2.49), (hy0 + 1.3, 3.14), (hy0 - 0.4, 2.49)], hx0 - 0.3, hx0 + 3.1)
    A(g, "wall").extrude_x([(hy0, 2.5), (hy0 + 1.3, 3.15), (hy0 + 2.6, 2.5)], hx0, hx0 + 2.8)
    floor_boards(g, hx0 + 0.1, hx0 + 2.7, hy0 + 0.1, hy0 + 2.5, zb + 0.02)
    ceiling(g, hx0 + 0.1, hx0 + 2.7, hy0 + 0.1, hy0 + 2.5, zt - 0.1, 'y', step=0.8)
    R.desk(g, hx0 + 1.4, hy0 + 1.9, zb + 0.02, w=1.1, d=0.6, face='S')
    # signal lever frame + bell + phone + stove
    for k in range(3):
        A(g, "tr_red" if k < 2 else "tr_cream").cyl((hx0 + 0.3 + k * 0.12, hy0 + 2.3, zb + 0.02), (hx0 + 0.3 + k * 0.12, hy0 + 2.3, zb + 1.2), 0.02, seg=6)
    A(g, "iron_black").box(hx0 + 0.2, hx0 + 0.7, hy0 + 2.2, hy0 + 2.5, zb + 0.02, zb + 0.35)
    A(g, "gold").cyl((hx0 + 2.5, hy0 + 2.0, 1.9), (hx0 + 2.5, hy0 + 2.0, 2.05), 0.09, 0.05, seg=10)
    A(g, "lacquer", 0.01).box(hx0 + 2.45, hx0 + 2.7, hy0 + 1.2, hy0 + 1.5, 1.5, 1.8)
    R.pot_stove(g, hx0 + 2.3, hy0 + 0.5, zb + 0.02, pipe_to=3.0)
    A(g, "tin").cyl((hx0 + 2.3, hy0 + 0.5, zb + 0.82), (hx0 + 2.3, hy0 + 0.5, zb + 0.98), 0.1, 0.08, seg=10)
    lamp_point(hx0 + 1.4, hy0 + 1.3, 2.1, 12)
    g.build()


def hokora2(x, y):
    """Shrine hall: raised floor, altar with mirror, offering, shimenawa, lantern (open front)."""
    g = G("hokora", "Buildings")
    zb = 0.5
    ops = {"S": [(x - 0.9, x + 0.9, zb + 0.05, 2.1, 'open')]}
    shell(g, x - 1.2, x + 1.2, y + 0.5, y + 2.7, zb, 2.5, 0.1, ops)
    A(g, "stone", 0.02).box(x - 1.5, x + 1.5, y + 0.2, y + 3.0, -0.2, zb)
    ym = y + 1.6
    A(g, "kawara").extrude_x([(y - 0.4, 2.35), (ym, 3.55), (y + 3.4, 2.35), (y + 3.4, 2.2), (ym, 3.4), (y - 0.4, 2.2)], x - 1.7, x + 1.7)
    A(g, "wall").extrude_x([(y + 0.5, 2.5), (ym, 3.3), (y + 2.7, 2.5)], x - 1.2, x + 1.2)
    floor_boards(g, x - 1.1, x + 1.1, y + 0.6, y + 2.6, zb + 0.1)
    A(g, "wood_dark", 0.01).box(x - 0.6, x + 0.6, y + 2.0, y + 2.5, zb + 0.1, zb + 0.7)          # altar
    A(g, "chrome").cyl((x, y + 2.45, zb + 1.1), (x, y + 2.47, zb + 1.1), 0.18, seg=18)          # mirror
    A(g, "white_paint").box(x - 0.5, x - 0.3, y + 2.2, y + 2.3, zb + 0.7, zb + 0.78)
    A(g, "straw").box(0, 0, 0, 0, 0, 0) if False else None
    A(g, "wood").cyl((x - 0.9, y + 0.65, 2.1), (x + 0.9, y + 0.65, 2.1), 0.05, seg=6)           # shimenawa
    A(g, "wood_dark", 0.01).box(x - 0.5, x + 0.5, y - 0.2, y + 0.3, 0.0, 0.9)                   # offering box
    lamp_point(x, y + 1.6, 2.0, 6)
    g.build()
