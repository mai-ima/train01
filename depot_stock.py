"""Rolling stock for the depot: steam / diesel locos in stalls, stabled cars, inspection shed, and the assembly hall with
experimental and under-construction vehicles (skeleton body on a jig, scaffolding, tarp-covered prototype, bogie racks)."""
from trainkit import *
import train as T
import steam2 as S
import diesel2 as DZ
from depot import TX, TY, PR, RIN, ROUT, STALLS, TABLE_DIR, pol


def xext(v):
    xs = [p[0] for a in v.accs.values() for p in a.V]
    return min(xs), max(xs)


# ====================================================================== loft helper (streamlined noses)
def loft_x(acc, secs):
    """secs: [(x, [(y, z), ...]), ...] with identical point counts -> closed tube with end caps."""
    i0 = len(acc.V)
    n = len(secs[0][1])
    for x, pr in secs:
        for (y, z) in pr:
            acc.V.append((x, y, z))
    for k in range(len(secs) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            acc.F.append((i0 + k * n + j, i0 + k * n + j2, i0 + (k + 1) * n + j2, i0 + (k + 1) * n + j))
    acc.F.append(tuple(i0 + j for j in reversed(range(n))))
    acc.F.append(tuple(i0 + (len(secs) - 1) * n + j for j in range(n)))


def nosed_body(acc, L, W, z0, ze, zp, nose=3.2, sy=0.50, sz=0.30, drop=0.18, ends=(-1, 1), steps=7):
    base = upper_profile(W, z0, ze, zp, n=6)
    zc = (z0 + zp) / 2
    secs = []
    for e in (-1, 1):
        pass
    xs = []
    # tail nose at -x
    def tipsec(u):
        s_y = 1 - (1 - sy) * u * u
        s_z = 1 - (1 - sz) * u * u
        return [(y * s_y, zc + (z - zc) * s_z - drop * u * u) for (y, z) in base]
    pts = []
    if -1 in ends:
        for k in range(steps + 1):
            u = 1 - k / steps
            pts.append((-L / 2 + (nose * (1 - u)), tipsec(u)))
        pts[0] = (-L / 2, pts[0][1])
    else:
        pts.append((-L / 2, base))
    mid_start = len(pts)
    if 1 in ends:
        for k in range(1, steps + 1):
            u = k / steps
            pts.append((L / 2 - nose + nose * u, tipsec(u)))
    else:
        pts.append((L / 2, base))
    loft_x(acc, pts)
    return tipsec(1.0)


# ====================================================================== experimental cars
def make_exp_car(name="exp1", L=17.0, tarp=False):
    """Original experimental battery railcar: streamlined silver body, blue stripe, roof battery pods."""
    v = Veh(name)
    W, z0, ze, zp = 2.70, 1.00, 3.05, 3.55
    nosed_body(v.A("silver", 0.0, True), L, W, z0, ze, zp)
    h = W / 2
    # window band (thin glass proud of the straight section) and stripe
    for s in (-1, 1):
        v.A("glass").box(-L / 2 + 3.4, L / 2 - 3.4, *sorted((s * (h + 0.003), s * (h + 0.012))), 1.95, 2.65)
        v.A("blue", 0.004).box(-L / 2 + 3.2, L / 2 - 3.2, *sorted((s * (h + 0.002), s * (h + 0.009))), 1.55, 1.78)
        for x in np.arange(-L / 2 + 3.4, L / 2 - 3.3, 1.3):
            v.A("silver").box(x - 0.04, x + 0.04, *sorted((s * (h + 0.003), s * (h + 0.014))), 1.95, 2.65)
        v.A("silver", 0.004).box(-0.55, 0.55, *sorted((s * (h + 0.002), s * (h + 0.012))), 1.0, 2.9) if False else None
    for e in (-1, 1):
        base = upper_profile(W, z0, ze, zp, n=6)
        zc = (z0 + zp) / 2
        # flat windscreen on the tip cap
        xt = e * L / 2
        v.A("glass").box(*sorted((xt, xt + e * 0.012)), -0.62, 0.62, 2.25, 2.72)
        v.A("blue", 0.004).box(*sorted((xt, xt + e * 0.008)), -0.66, 0.66, 1.72, 1.92)
        v.A("lampglass").cyl((xt + e * 0.01, -0.5, 1.95), (xt + e * 0.04, -0.5, 1.95), 0.085, 0.085, seg=12)
        v.A("lampglass").cyl((xt + e * 0.01, 0.5, 1.95), (xt + e * 0.04, 0.5, 1.95), 0.085, 0.085, seg=12)
        coupler(v, e, xt, z=0.88)
        v.end_plane("plate_ex.png", e, 0.0, 0.5, 1.5, 1.5 + 0.19, xt + e * 0.015)
    # roof battery pods + cooling
    for x in np.arange(-5.0, 5.1, 2.5):
        v.A("white", 0.02).box(x - 0.9, x + 0.9, -0.7, 0.7, zp - 0.05, zp + 0.28)
        v.A("dark").box(x - 0.8, x + 0.8, -0.62, 0.62, zp + 0.275, zp + 0.285)
    v.A("black").cyl((0.0, -0.6, zp + 0.28), (0.0, 0.6, zp + 0.28), 0.03, 0.03, seg=6)
    # under-floor battery boxes
    for x in np.arange(-5.5, 5.6, 2.2):
        v.A("under", 0.015).box(x - 0.9, x + 0.9, -1.0, 1.0, 0.55, 1.0)
        v.A("yellow", 0.01).box(x - 0.82, x + 0.82, -1.01, -0.99, 0.62, 0.78)
    for x in (-L / 2 + 3.6, L / 2 - 3.6):
        bogie2(v, x, wb=1.9)
    for s in (-1, 1):
        v.side_plane("logo_new.png", s, -4.0, 0.5, 1.12, 1.62, s * (h + 0.012))
        v.side_plane("plate_ex.png", s, 2.5, 0.5, 1.2, 1.39, s * (h + 0.012))
    if tarp:
        # sheeting tied over the front half: stepped section, rope bands, a few sagging folds
        sec = []
        for k in range(10):
            x = -1.0 + k * 0.95
            sag = 0.05 * math.sin(k * 1.7)
            sec.append((x, [(-1.52, 1.05), (1.52, 1.05), (1.50, 2.9 + sag), (1.1, 3.55), (0.4, 3.78 + sag), (-0.4, 3.78 - sag), (-1.1, 3.55), (-1.50, 2.9 - sag)]))
        loft_x(v.A("tarp", 0.0, True), sec)
        for x in np.arange(0.0, 8.0, 1.6):
            v.A("tarp2").extrude_x([(-1.53, 1.0), (-1.51, 2.9), (-1.11, 3.57), (-0.41, 3.80), (0.41, 3.80), (1.11, 3.57), (1.51, 2.9), (1.53, 1.0),
                                    (1.56, 1.0), (1.54, 2.9), (1.12, 3.60), (0.42, 3.83), (-0.42, 3.83), (-1.12, 3.60), (-1.54, 2.9), (-1.56, 1.0)], x - 0.03, x + 0.03)
    return v


def make_skeleton_car(name="skel", L=20.0, skinned=0.45):
    """Under-construction steel frame of a railcar (posts, ribs, partial skin) standing on a jig."""
    v = Veh(name)
    W, h = 2.80, 1.40
    zf, zt, zr = 1.05, 2.95, 3.52
    v.A("primer", 0.01).box(-L / 2, L / 2, -1.2, 1.2, 0.85, zf)                         # underframe plate
    for s in (-1, 1):
        v.A("steel", 0.006).box(-L / 2, L / 2, *sorted((s * h, s * (h - 0.08))), zf, zf + 0.12)  # sole bar
        v.A("steel", 0.006).box(-L / 2, L / 2, *sorted((s * h, s * (h - 0.06))), zt - 0.06, zt)  # waist rail
        for z in (1.85, 2.75):
            v.A("steel", 0.004).box(-L / 2, L / 2, *sorted((s * h, s * (h - 0.04))), z, z + 0.05)
    arc = upper_profile(W, zt, zt + 0.0001, zr, n=8)[3:3 + 8]
    ribs = np.arange(-L / 2, L / 2 + 0.01, 1.0)
    for x in ribs:
        for s in (-1, 1):
            v.A("steel", 0.003).box(x - 0.035, x + 0.035, *sorted((s * h, s * (h - 0.07))), zf + 0.12, zt)
        pts = [(h, zt)] + [p for p in upper_profile(W, zt, zt + 0.0001, zr, n=8)[3:3 + 7]] + [(0.0, zr)]
        pts = [(-p[0], p[1]) for p in reversed(pts)] + pts[1:]
        for (a, b) in zip(pts[:-1], pts[1:]):
            v.A("steel", 0.002).sbox((x, a[0], a[1]), (x, b[0], b[1]), 0.06, 0.05, up=(1, 0, 0))
        v.A("steel").box(x - 0.03, x + 0.03, -1.3, 1.3, zf + 0.12, zf + 0.15)          # floor cross-bar
    for y in (-0.7, 0.0, 0.7):
        v.A("steel", 0.003).sbox((-L / 2, y, zr - 0.05 if y == 0 else zr - 0.35), (L / 2, y, zr - 0.05 if y == 0 else zr - 0.35), 0.07, 0.05)
    for e in (-1, 1):
        for yy in (-1.38, -0.5, 0.5, 1.38):
            v.A("steel", 0.003).box(*sorted((e * L / 2, e * (L / 2 - 0.07))), yy - 0.04, yy + 0.04, zf + 0.12, zt)
    # partially skinned: red-oxide primed panels on the first part of both sides and over the roof
    xs0, xs1 = -L / 2, -L / 2 + L * skinned
    for s in (-1, 1):
        v.A("primer", 0.004).box(xs0, xs1, *sorted((s * (h + 0.012), s * (h - 0.02))), zf + 0.12, 1.85)
        v.A("primer", 0.004).box(xs0, xs1 - 4.0, *sorted((s * (h + 0.012), s * (h - 0.02))), 2.75, zt)
    v.A("primer", 0.006).extrude_x(upper_profile(W, zt - 0.02, zt, zr, n=7, inset=0.03), xs0, xs0 + 5.5)
    for x in (-L / 2 + 3.5, L / 2 - 3.5):
        bogie2(v, x, wb=2.1)
    return v


def jig_stands(x, y, yaw_axis='y', n=5, span=18.0, z=0.0):
    """Wooden/steel trestles under a body being assembled (world placed, no rotation)."""
    v = Veh("jig")
    for k in range(n):
        t = -span / 2 + span * k / (n - 1)
        for s in (-1, 1):
            v.A("iron", 0.01).box(t - 0.15, t + 0.15, s * 1.0 - 0.15, s * 1.0 + 0.15, -0.27, 0.35)
            v.A("wood_dark", 0.01).box(t - 0.3, t + 0.3, s * 1.0 - 0.2, s * 1.0 + 0.2, 0.35, 0.5)
    return v


def scaffold(x0, x1, y, z_top=3.6, depth=1.2, sgn=1, name="scaffold"):
    """Tube-and-board scaffold along one side of a car (local x along the car, y = side)."""
    v = Veh(name)
    st = v.A("steel")
    pl = v.A("wood", 0.004)
    bays = max(2, int((x1 - x0) / 1.9))
    xs = np.linspace(x0, x1, bays + 1)
    levels = [0.9, 1.9, 2.9, 3.9] if z_top > 3.5 else [0.9, 1.9, 2.9]
    for x in xs:
        for yy in (y, y + sgn * depth):
            st.cyl((x, yy, -0.2), (x, yy, levels[-1] + 1.0), 0.024, 0.024, seg=6)
        for z in levels:
            st.cyl((x, y, z), (x, y + sgn * depth, z), 0.02, 0.02, seg=5)
    for z in levels:
        for yy in (y, y + sgn * depth):
            st.cyl((x0, yy, z), (x1, yy, z), 0.02, 0.02, seg=5)
        pl.box(x0, x1, *sorted((y + sgn * 0.05, y + sgn * (depth - 0.05))), z + 0.02, z + 0.07)
    for z in levels[1:]:
        for yy in (y + sgn * depth,):
            st.cyl((x0, yy, z + 0.55), (x1, yy, z + 0.55), 0.015, 0.015, seg=5)
    for i in range(bays):
        a = xs[i]
        b = xs[i + 1]
        st.cyl((a, y + sgn * depth, 0.0), (b, y + sgn * depth, levels[1]), 0.015, 0.015, seg=5)
        st.cyl((b, y + sgn * depth, levels[1]), (a, y + sgn * depth, levels[2] if len(levels) > 2 else levels[1]), 0.015, 0.015, seg=5)
    for z in (levels[0],):
        st.cyl((x0, y + sgn * (depth + 0.0), 1.0), (x0, y + sgn * (depth + 0.0), 3.0), 0.0, 0.0, seg=3) if False else None
    return v


def bogie_rack(name, n=3, seed=0):
    """Overhauled bogies waiting on timber cribbing."""
    rr = random.Random(seed)
    v = Veh(name)
    for k in range(n):
        x = k * 4.2
        v.A("wood_dark", 0.01).box(x - 1.9, x + 1.9, -0.9, -0.6, -0.03, 0.12)
        v.A("wood_dark", 0.01).box(x - 1.9, x + 1.9, 0.6, 0.9, -0.03, 0.12)
        bogie2(v, x, wb=2.1)
    v.A("wood_dark", 0.01).box(-2.2, (n - 1) * 4.2 + 2.2, -1.3, -1.1, -0.05, 0.0) if False else None
    return v


def build_stalls():
    """Locos in the roundhouse stalls and on the turntable."""
    plan = {1: ("C", True), 3: ("D", False), 5: ("DD", None), 6: ("D", False), 0: ("C", False), 8: ("T", False)}
    for k, (kind, smoke) in plan.items():
        a = STALLS[k]
        if kind == "DD":
            v = DZ.make_de10(f"de10_stall{k}", body="verm")
        else:
            kk = {"D": "D51", "C": "C57", "T": "C57"}[kind]
            v = S.make_steam2(f"stall{k}", kk, ang=[30, 70, 110, 150, 200, 250][k % 6], smoke=bool(smoke), num_plate="plate_d.png" if kk == "D51" else "plate_c.png")
        x0, x1 = xext(v)
        length = x1 - x0
        r_front = min(17.5, ROUT - 0.5 - length)
        r_front = max(r_front, 14.6)
        r_org = r_front + x1
        px, py = pol(r_org, a)
        v.place(px, py, math.radians(a + 180.0))
        print(f"stall {k} {kind} length {length:.1f} front r={r_front:.1f}")
    # small tank engine on the turntable, smoking
    v = S.make_steam2("table_T", "C57", ang=95, smoke=True, num_plate="plate_c.png")
    x0, x1 = xext(v)
    v.place(TX - math.cos(math.radians(TABLE_DIR)) * (x0 + x1) / 2, TY - math.sin(math.radians(TABLE_DIR)) * (x0 + x1) / 2,
            math.radians(TABLE_DIR), z=0.262)


def build_sheds_and_sidings():
    # inspection shed W1/W2 (y=-51, -55.5 : x -26..-62)
    T.make_kiha("kiha_shed", seed=7).place(-47.0, -51.0, 0.0)
    DZ.make_dd51("dd_shed", body="blue", top="gtop", band="cream2").place(-45.0, -55.5, math.pi)
    # stabling E1 (y=-49.5)
    T.make_coach("coach_E1", "mark_coach2.png", 1, seed=31).place(16.5, -49.5, 0.0)
    T.make_yo("yo_E1").place(0.3 + 3.4, -49.5, 0.0) if False else None
    T.make_wam("wam_E1", seed=41).place(2.6, -49.5, 0.0)
    T.make_tora("tora_E1", "coal", seed=42).place(-7.0 + 7.0, -49.5, 0.0) if False else None
    # lead track: a lone brake van waiting
    T.make_yo("yo_lead").place(-14.0, -62.0, math.pi / 2)


def build_hall_stock():
    # track x=25.5 : skeleton car on jig; x=30 : tarp-covered experimental car; outside: finished experimental car
    sk = make_skeleton_car("skeleton")
    sk.place(25.5, -86.0, math.pi / 2)
    scaffold(-10.0, 10.0, -1.55, name="scaffold_a").place(25.5, -86.0, math.pi / 2)
    scaffold(-8.0, 7.0, 1.55, sgn=1, name="scaffold_b", z_top=3.0).place(25.5, -86.0, math.pi / 2)
    tp = make_exp_car("exp_tarp", tarp=True)
    tp.place(30.0, -87.0, -math.pi / 2)
    # finished experimental battery railcar at the hall apron
    make_exp_car("exp_done").place(30.0, -66.0, -math.pi / 2) if False else None


def build_yard_items():
    bogie_rack("racks_a", 3, 1).place(42.0, -78.0, math.pi / 2, z=0.0)
    bogie_rack("racks_b", 2, 2).place(47.0, -84.0, 0.0, z=0.0)
    jig_stands(0, 0).place(25.5, -86.0, math.pi / 2, z=0.0)


def build_depot_stock():
    build_stalls()
    build_sheds_and_sidings()
    build_hall_stock()
    build_yard_items()
    try:
        import depot_in
        depot_in.build_depot_interiors()
    except ImportError:
        pass
    try:
        import props
        props.build_depot_props()
    except (ImportError, AttributeError):
        pass
