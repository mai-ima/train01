import json
"""Rolling-stock kit: vehicle container, materials and reusable parts (wheelsets, bogies, couplers ...).
Local frame of every vehicle: x along the car, y across, z = 0 at rail-head top.  Placed via an Empty."""
from common import *

_VM = {}


def vpaint(name, color, rough=0.5, rust=0.25, grime=0.8, seams=True, metal=0.0, panel=(1.15, 0.80)):
    """Weathered rolling-stock paint: panel seams (bump), rain streaks, lower-body grime, sun fade, rust blooms."""
    m = lib.Mat(name)
    x, y, z = m.sep(m.obj)
    n_r = m.noise(scale=3.0, detail=6, rough=0.65)
    n_f = m.noise(scale=26, detail=3)
    rmask = m.ramp(n_r, [(0.52, (0, 0, 0)), (0.74, (1, 1, 1))])
    rmask = m.math('MULTIPLY', rmask, m.ramp(n_f, [(0.3, (0.2, 0.2, 0.2)), (0.7, (1, 1, 1))]))
    rmask = m.math('MULTIPLY', rmask, rust)
    rust_col = m.ramp(n_f, [(0.0, (0.26, 0.10, 0.045)), (1.0, (0.42, 0.18, 0.07))])
    col = m.mix(rmask, color, rust_col)
    streak = m.noise(vec=m.mapping(scale=(6.0, 6.0, 0.28), loc=(3, 1, 0)), scale=1.0, detail=5, rough=0.62)
    st = m.ramp(streak, [(0.45, (0, 0, 0)), (0.75, (1, 1, 1))])
    low = m.maprange(z, 0.45, 2.4, 1.0, 0.0)
    low = m.math('MULTIPLY', low, m.ramp(m.noise(scale=2.2, detail=5), [(0.25, (0.5, 0.5, 0.5)), (0.7, (1.2, 1.2, 1.2))]))
    gm = m.math('ADD', m.math('MULTIPLY', low, 0.95), m.math('MULTIPLY', st, 0.38), clamp=True)
    gm = m.math('MULTIPLY', gm, grime)
    dirt = m.mix(m.noise(scale=7, detail=2), (0.055, 0.042, 0.034), (0.11, 0.085, 0.06))
    col = m.mix(gm, col, dirt)
    fade = m.maprange(z, 2.6, 3.8, 0.0, 0.10)
    col = m.mix(fade, col, m.mix(0.5, color, (0.55, 0.52, 0.47), 'ADD'))
    soot = m.math('MULTIPLY', m.maprange(z, 3.05, 3.55, 0.0, 0.5), m.ramp(m.noise(scale=4.0, detail=4), [(0.3, (0.3, 0.3, 0.3)), (0.7, (1.0, 1.0, 1.0))]))   # 屋根の煤
    sk = m.noise(vec=m.mapping(scale=(0.22, 9.0, 1.0), loc=(5, 2, 0)), scale=1.0, detail=4, rough=0.6)       # 走行風で車体長手方向に伸びる煤の筋
    soot = m.math('MULTIPLY', soot, m.ramp(sk, [(0.38, (0.25, 0.25, 0.25)), (0.62, (1.6, 1.6, 1.6))]), clamp=True)
    col = m.mix(soot, col, (0.035, 0.032, 0.03))
    h = m.math('ADD', m.math('MULTIPLY', rmask, n_f), m.math('MULTIPLY', n_f, 0.12))
    if seams:
        br = m.node('ShaderNodeTexBrick')
        m.setall(br, {'Vector': m.combine(m.math('ADD', x, y), z, 0.0), 'Scale': 1.0, 'Mortar Size': 0.006, 'Mortar Smooth': 0.3,
                      'Brick Width': panel[0], 'Row Height': panel[1], 'Bias': 0.0})
        h = m.math('ADD', h, m.math('MULTIPLY', br.outputs['Fac'], 0.6))
    nrm = m.bump(h, 0.5, 0.012)
    rr = m.math('ADD', rough, m.math('ADD', m.math('MULTIPLY', rmask, 0.4), m.math('MULTIPLY', gm, 0.25)), clamp=True)
    m.principled(**{'Base Color': col, 'Roughness': rr, 'Metallic': metal, 'Specular IOR Level': 0.45, 'Normal': nrm})
    return m.m


def moquette(name, color, scale=70.0, contrast=0.55):
    """座席のモケット(織物): 細かい格子+繊維ノイズ+擦れ。色は color を基準に明暗2色。"""
    m = lib.Mat(name)
    x, y, z = m.sep(m.obj)
    ck = m.node('ShaderNodeTexChecker')
    m.setall(ck, {'Vector': m.combine(m.math('ADD', x, y), z, 0.0), 'Scale': scale})
    fib = m.noise(scale=380.0, detail=3, rough=0.7)
    wear = m.ramp(m.noise(scale=5.0, detail=4), [(0.45, (1.0, 1.0, 1.0)), (0.80, (0.72, 0.70, 0.66))])
    dark = tuple(c * (1.0 - contrast * 0.5) for c in color)
    light = tuple(min(1.0, c * (1.0 + contrast * 0.35)) for c in color)
    ck2 = m.node('ShaderNodeTexChecker')
    m.setall(ck2, {'Vector': m.combine(m.math('SUBTRACT', x, z), m.math('ADD', y, z), 0.0), 'Scale': scale * 2.7})     # 斜め綾(細かい二重織り)
    ckm = m.math('MULTIPLY', m.math('ADD', ck.outputs['Fac'], ck2.outputs['Fac']), 0.5)
    blot = m.ramp(m.noise(scale=3.0, detail=5), [(0.35, (0.80, 0.80, 0.80)), (0.7, (1.0, 1.0, 1.0))])     # 座面ごとの色むら・へたり
    col = m.mix(ckm, dark, light)
    col = m.mix(1.0, col, blot, 'MULTIPLY')
    col = m.mix(fib, col, tuple(c * 0.8 for c in color))
    col = m.mix(m.math('MULTIPLY', wear, 0.0), col, col) if False else col
    h = m.math('ADD', m.math('MULTIPLY', ckm, 0.4), m.math('MULTIPLY', fib, 0.6))
    m.principled(**{'Base Color': col, 'Roughness': 0.96, 'Metallic': 0.0, 'Specular IOR Level': 0.12, 'Normal': m.bump(h, 0.4, 0.004)})
    return m.m


def carpet_lux(name):
    """周遊列車の絨毯: 深紅の地に金の菱格子(ブリック状の目地を金糸に見立てる)+毛足ノイズ。"""
    m = lib.Mat(name)
    x, y, z = m.sep(m.obj)
    br = m.node('ShaderNodeTexBrick')
    m.setall(br, {'Vector': m.combine(m.math('ADD', x, y), m.math('SUBTRACT', x, y), 0.0), 'Scale': 4.2, 'Mortar Size': 0.022, 'Mortar Smooth': 0.2,
                  'Brick Width': 0.5, 'Row Height': 0.5, 'Bias': 0.0})
    fib = m.noise(scale=420.0, detail=3, rough=0.7)
    base = m.mix(fib, (0.30, 0.035, 0.05), (0.22, 0.025, 0.04))
    col = m.mix(br.outputs['Fac'], base, (0.42, 0.31, 0.12))
    m.principled(**{'Base Color': col, 'Roughness': 0.98, 'Metallic': 0.0, 'Specular IOR Level': 0.1, 'Normal': m.bump(fib, 0.6, 0.003)})
    return m.m


def mat_veh_window(name, tint=(0.80, 0.90, 0.88)):
    """Clear glass: transparent with Fresnel reflection and a little dust, so the saloon shows through."""
    m = lib.Mat(name)
    tr = m.node('ShaderNodeBsdfTransparent')
    m.set(tr.inputs['Color'], tint)
    gl = m.node('ShaderNodeBsdfGlossy')
    m.setall(gl, {'Color': (0.9, 0.95, 1.0), 'Roughness': 0.04})
    fr = m.node('ShaderNodeFresnel')
    m.set(fr.inputs['IOR'], 1.5)
    dust = m.ramp(m.noise(scale=6, detail=4), [(0.30, (0.05, 0.05, 0.05)), (0.75, (0.16, 0.16, 0.16))])      # 埃のむらと弱い基底反射(窓が真っ黒/単色の板に見えない)
    fac = m.math('ADD', fr.outputs['Fac'], dust)
    mx = m.node('ShaderNodeMixShader')
    m.set(mx.inputs[0], fac)
    m.set(mx.inputs[1], tr.outputs['BSDF'])
    m.set(mx.inputs[2], gl.outputs['BSDF'])
    return m.finish(mx.outputs['Shader'])


def vmat(key):
    """Vehicle materials (lazy)."""
    if not _VM:
        P = vpaint
        _VM.update({
            "red": vpaint("v_red", (0.50, 0.065, 0.028), rough=0.36, rust=0.2), "cream": vpaint("v_cream", (0.76, 0.64, 0.42), rough=0.38, rust=0.15),
            "roof": vpaint("v_roof", (0.20, 0.205, 0.21), rough=0.62, rust=0.35, grime=0.9, seams=False), "under": vpaint("v_under", (0.16, 0.145, 0.125), rough=0.7, rust=0.45, grime=0.8, seams=False, metal=0.2),
            "wplank": lib.mat_pbr("wagon_plank", "Planks023A", scale=1.3, hsv=(0.5, 0.95, 0.62), tint=(0.42, 0.16, 0.09), tint_amt=0.75, bump=0.8, dirt=0.5, macro=0.3, spec=0.15),
            "glass": mat_veh_window("veh_window"),
            "moq": lib.mat_plain("veh_moq", (0.07, 0.15, 0.09), rough=0.9, spec=0.1),
            "moq2": lib.mat_plain("veh_moq2", (0.20, 0.08, 0.05), rough=0.9, spec=0.1),
            "skin": lib.mat_plain("veh_skin", (0.55, 0.38, 0.28), rough=0.7),
            "hair": lib.mat_plain("veh_hair", (0.02, 0.018, 0.018), rough=0.8),
            "cl1": lib.mat_plain("veh_cl1", (0.10, 0.12, 0.16), rough=0.9),
            "cl2": lib.mat_plain("veh_cl2", (0.30, 0.25, 0.18), rough=0.9),
            "cl3": lib.mat_plain("veh_cl3", (0.38, 0.12, 0.10), rough=0.9),
            "cl4": lib.mat_plain("veh_cl4", (0.22, 0.26, 0.20), rough=0.9),
            "floorw": M["floor"], "lamp_in": lib.mat_emissive("veh_lamp_in", (1.0, 0.88, 0.66), 5.0),
            "coach": P("coach_brown", (0.115, 0.060, 0.040), rough=0.50, rust=0.30),
            "wagon": P("wagon_brown", (0.14, 0.062, 0.040), rough=0.62, rust=0.65),
            "wagon2": P("wagon_brown2", (0.10, 0.048, 0.032), rough=0.65, rust=0.7),
            "black": P("veh_black", (0.06, 0.058, 0.056), rough=0.55, rust=0.10, grime=0.5),
            "blue": P("loco_blue", (0.022, 0.058, 0.115), rough=0.45, rust=0.25),
            "white": P("loco_white", (0.72, 0.70, 0.62), rough=0.5, rust=0.25),
            "grey": P("loco_grey", (0.22, 0.23, 0.235), rough=0.55, rust=0.35),
            "green": P("loco_green", (0.06, 0.16, 0.09), rough=0.5, rust=0.3),
            "orange": P("loco_orange", (0.62, 0.26, 0.05), rough=0.45, rust=0.3),
            "silver": P("exp_silver", (0.62, 0.64, 0.65), rough=0.28, rust=0.1, metal=0.75),
            "wheel": lib.mat_plain("veh_wheel", (0.11, 0.075, 0.055), rough=0.5, metal=0.75),
            "brass": lib.mat_plain("veh_brass", (0.62, 0.44, 0.15), rough=0.32, metal=0.85),
            "tarp": lib.mat_plain("veh_tarp", (0.11, 0.17, 0.12), rough=0.95),
            "tarp2": lib.mat_plain("veh_tarp2", (0.30, 0.27, 0.20), rough=0.95),
            "coal": lib.mat_plain("veh_coal", (0.018, 0.018, 0.019), rough=0.75, spec=0.3),
            "curtain": lib.mat_plain("veh_curtain", (0.42, 0.47, 0.30), rough=0.9),
            "lampglass": lib.mat_plain("veh_lamp", (0.85, 0.85, 0.75), rough=0.08, spec=0.9),
            "steel": lib.mat_plain("veh_steel", (0.30, 0.30, 0.30), rough=0.4, metal=0.8),
            "rustsc": M["iron_rust"], "wood": M["wood"], "wood_dark": M["wood_dark"], "iron": lib.mat_plain("veh_iron", (0.15, 0.13, 0.115), rough=0.55, metal=0.5),
            "sack": M["sack"], "tin": M["tin"], "concrete": M["concrete"], "rubber": M["rubber"],
            "lamp_glow": M["lamp_glow"], "rail": M["rail"], "dark": lib.mat_plain("veh_dark", (0.01, 0.01, 0.012), rough=0.8),
            "primer": lib.mat_paint("veh_primer", (0.36, 0.17, 0.10), rough=0.8, rust=0.6, rust_scale=2.0),
            "steam": lib.mat_plain("veh_steam", (0.62, 0.62, 0.63), rough=0.98, spec=0.02),
            "verm": vpaint("v_verm", (0.50, 0.10, 0.035), rough=0.40, rust=0.2, grime=0.8),
            "gtop": vpaint("v_gtop", (0.19, 0.20, 0.21), rough=0.55, rust=0.25, grime=0.5, seams=False),
            "cream2": vpaint("v_cream2", (0.76, 0.68, 0.48), rough=0.45, rust=0.1, grime=0.6, seams=False),
            "yellow": lib.mat_paint("veh_yellow", (0.62, 0.48, 0.07), rough=0.5, rust=0.3),
        })
    if key not in _VM and key in M:
        return M[key]
    return _VM[key]


class _LampWrap:
    """灯具レンズ(円筒)の周囲に金属のケース(つば)を自動で足す。平らな円板に見えるのを防ぐ。"""

    def __init__(self, veh, acc):
        self._v, self._a = veh, acc

    def cyl(self, p0, p1, r0, r1=None, seg=12, caps=True):
        from mathutils import Vector
        a, b = Vector(p0), Vector(p1)
        ax = b - a
        if ax.length > 1e-6 and r0 < 0.2:
            u = ax.normalized()
            h = self._v.A("steel")
            h.cyl(tuple(a - u * 0.035), tuple(a + u * 0.004), r0 * 1.32, r0 * 1.22, seg=max(seg, 12))
        return self._a.cyl(p0, p1, r0, r1, seg=seg, caps=caps)

    def __getattr__(self, n):
        return getattr(self._a, n)


class Veh:
    """車両ビルダー。リグ規約(運転準備): 台車・輪軸・連結器は part() で別オブジェクト化され、
    部品の原点が回転中心になる(台車=鉛直軸z、輪軸=車軸y、連結器=z)。place() が空オブジェクト階層
    <name> > <name>.bogie0 > <name>.bogie0.ws0 ... を作る。メタデータは meta に溜め、export_meta() で出力。"""

    def __init__(self, name):
        self.name, self.accs, self.planes = name, {}, []
        self.cur = None                 # 現在の部品(パス文字列)
        self.parts = {}                 # path -> dict(origin, parent, axis, kind, r)
        self.meta = {"bogies": [], "wheelsets": [], "couplers": []}
        self._n = {}
        self.lights = []                # 車内灯(area): (x,y,z,長さ,幅,W,色)

    def part(self, kind, origin, axis="z", r=None):
        import contextlib

        @contextlib.contextmanager
        def cm():
            idx = self._n.get((self.cur, kind), 0)
            self._n[(self.cur, kind)] = idx + 1
            path = f"{self.cur}.{kind}{idx}" if self.cur else f"{kind}{idx}"
            self.parts[path] = dict(origin=tuple(origin), parent=self.cur, axis=axis, kind=kind, r=r)
            prev, self.cur = self.cur, path
            try:
                yield path
            finally:
                self.cur = prev
        return cm()

    def pax(self):
        """乗客専用のパート(kind='pax')。同じ親の下で1つを再利用し、人物のON/OFFを切替可能にする。"""
        import contextlib

        @contextlib.contextmanager
        def cm():
            path = f"{self.cur}.pax" if self.cur else "pax"
            if path not in self.parts:
                self.parts[path] = dict(origin=(0.0, 0.0, 0.0), parent=self.cur, axis="z", kind="pax", r=None)
            prev, self.cur = self.cur, path
            try:
                yield path
            finally:
                self.cur = prev
        return cm()

    def A(self, key, bevel=0.0, smooth=False):
        k = (self.cur, key, bevel, smooth)
        if k not in self.accs:
            nm = f"{self.name}_{self.cur.replace('.', '_')}_{key}" if self.cur else f"{self.name}_{key}"
            self.accs[k] = Acc(nm, vmat(key), "Trains", bevel=bevel, smooth=smooth)
        if key == "lampglass":
            return _LampWrap(self, self.accs[k])
        return self.accs[k]

    def plane(self, img, corners, kw=None):
        self.planes.append((img, corners, kw))

    def side_plane(self, img, side, xc, w, z0, z1, y):
        """Readable decal on the +y (side=1) or -y (side=-1) flank, centred on x=xc."""
        a, b = xc + w / 2, xc - w / 2
        if side > 0:
            c = [(a, y, z0), (b, y, z0), (b, y, z1), (a, y, z1)]
        else:
            c = [(b, y, z0), (a, y, z0), (a, y, z1), (b, y, z1)]
        self.plane(img, c)

    def end_plane(self, img, end, yc, w, z0, z1, x):
        """Decal on the +x (end=1) or -x (end=-1) face."""
        a, b = yc - w / 2, yc + w / 2
        if end > 0:
            c = [(x, a, z0), (x, b, z0), (x, b, z1), (x, a, z1)]
        else:
            c = [(x, b, z0), (x, a, z0), (x, a, z1), (x, b, z1)]
        self.plane(img, c)

    def place(self, x, y, yaw=0.0, z=None, parent=None):
        z = Z_RAIL if z is None else z
        e = bpy.data.objects.new(self.name, None)
        link(e, "Trains")
        e.location = (x, y, z)
        e.rotation_euler = (0, 0, yaw)
        e["rig_root"] = True
        e["rig_meta"] = json.dumps(self.meta)
        if parent is not None:
            e.parent = parent
        empties = {None: (e, (0.0, 0.0, 0.0))}
        for path in sorted(self.parts, key=lambda p: p.count(".")):
            pi = self.parts[path]
            pe, po = empties[pi["parent"]]
            em = bpy.data.objects.new(f"{self.name}.{path}", None)
            link(em, "Trains")
            em.parent = pe
            em.location = tuple(o - q for o, q in zip(pi["origin"], po))
            em["rig_kind"], em["rig_axis"] = pi["kind"], pi["axis"]
            if pi["r"] is not None:
                em["rig_radius"] = pi["r"]
            empties[path] = (em, pi["origin"])
        for (cur, key, bev, sm), acc in self.accs.items():
            ob = acc.build()
            if ob is None:
                continue
            pe, po = empties[cur]
            ob.parent = pe
            ob.location = tuple(-q for q in po)
        for li_i, (lx, ly, lz, ll, lw, watt, col) in enumerate(self.lights):
            ld = bpy.data.lights.new(f"{self.name}_in{li_i}", 'AREA')
            ld.shape = 'RECTANGLE'; ld.size, ld.size_y = ll, lw
            ld.energy = watt; ld.color = col
            lo = bpy.data.objects.new(f"{self.name}_in{li_i}", ld)
            link(lo, "Trains")
            lo.parent = e; lo.location = (lx, ly, lz)
            lo.rotation_euler = (0, 0, 0)
            try:
                lo.visible_camera = False          # 面光源そのものはカメラに映さない(窓越しに白い板として見えるのを防ぐ)
            except Exception:
                pass
        for i, (img, corners, kw) in enumerate(self.planes):
            ob = lib.image_plane(f"{self.name}_decal{i}", corners, img, kw or {"rough": 0.5, "spec": 0.25}, col="Trains", alpha=True)
            ob.parent = e
        return e


# ------------------------------------------------------------------ geometry helpers
def upper_profile(W, z0, ze, zp, n=7, inset=0.0):
    """(y,z) polygon: straight sides from z0 to ze then an elliptical roof up to zp."""
    h = W / 2 - inset
    pts = [(-h, z0), (h, z0), (h, ze)]
    for i in range(1, n):
        a = math.pi / 2 * i / n
        pts.append((h * math.cos(a), ze + (zp - ze) * math.sin(a)))
    pts.append((0.0, zp))
    for i in range(n - 1, 0, -1):
        a = math.pi / 2 * i / n
        pts.append((-h * math.cos(a), ze + (zp - ze) * math.sin(a)))
    pts.append((-h, ze))
    return pts


def wheelset(v, x, r=0.43, y_g=0.5335, spokes=False):
    with v.part("ws", (x, 0.0, r), axis="y", r=r):
        _wheelset(v, x, r, y_g, spokes)
    v.meta["wheelsets"].append(round(float(x), 3))


def _wheelset(v, x, r=0.43, y_g=0.5335, spokes=False):
    a = v.A("wheel", 0.0, True)
    for s in (-1, 1):
        y = s * y_g
        a.cyl((x, y - 0.065, r), (x, y + 0.065, r), r, r, seg=40)                           # 踏面
        a.cyl((x, y - s * 0.078, r), (x, y - s * 0.052, r), r + 0.03, r + 0.03, seg=40)    # フランジ
        a.cyl((x, y + s * 0.06, r), (x, y + s * 0.10, r), 0.15, 0.15, seg=16)              # ハブ
        a.cyl((x, y - s * 0.07, r), (x, y - s * 0.068, r), r - 0.05, r - 0.05, seg=40)     # 円板の凹み
        for k in range(8):                                                                  # 円板のリブ(8本)
            th = 2 * math.pi * k / 8
            a.sbox((x + 0.17 * math.cos(th), y + s * 0.072, r + 0.17 * math.sin(th)), (x + (r - 0.07) * math.cos(th), y + s * 0.072, r + (r - 0.07) * math.sin(th)), 0.02, 0.012)
        v.A("steel").cyl((x, s * (y_g + 0.20), r), (x, s * (y_g + 0.25), r), 0.075, 0.07, seg=14)   # 軸端のキャップ
    a.cyl((x, -y_g - 0.07, r), (x, y_g + 0.07, r), 0.058, 0.058, seg=10)


def axle_box(v, x, y_off=0.88, r=0.43):
    a = v.A("iron", 0.006)
    for s in (-1, 1):
        a.box(x - 0.17, x + 0.17, s * y_off - 0.09, s * y_off + 0.09, r - 0.12, r + 0.14)


def bogie2(v, x, wb=2.1, r=0.43, sideframe_h=0.28, key="iron"):
    """Two-axle truck centred at x(リグ: 鉛直軸の台車部品)。"""
    with v.part("bogie", (x, 0.0, 0.0), axis="z"):
        _bogie2(v, x, wb, r, sideframe_h, key)
    v.meta["bogies"].append(dict(x=round(float(x), 3), wheelbase=wb, wheel_r=r, axles=2))


def _bogie2(v, x, wb=2.1, r=0.43, sideframe_h=0.28, key="iron"):
    for dx in (-wb / 2, wb / 2):
        wheelset(v, x + dx, r)
    a = v.A(key, 0.008)
    for s in (-1, 1):
        y = s * 0.80
        a.box(x - wb / 2 - 0.35, x + wb / 2 + 0.35, y - 0.05, y + 0.05, r + 0.04, r + 0.04 + sideframe_h)
        for dx in (-wb / 2, wb / 2):
            a.box(x + dx - 0.15, x + dx + 0.15, y - 0.07, y + 0.07, r - 0.11, r + 0.12)
            sp = v.A("steel")
            sp.cyl((x + dx, y, r + 0.12), (x + dx, y, r + 0.30), 0.075, 0.075, seg=8)
    for s_ in (-1, 1):                                                     # 側梁の上弦・下弦と軸箱(形鋼組みの台車枠)
        y = s_ * 0.80
        a.box(x - wb / 2 - 0.30, x + wb / 2 + 0.30, y - 0.06, y + 0.06, r + 0.30, r + 0.38)
        a.box(x - wb / 2 - 0.30, x + wb / 2 + 0.30, y - 0.06, y + 0.06, r - 0.02, r + 0.05)
        for dx in (-wb / 2, wb / 2):
            v.A("steel").cyl((x + dx, y + s_ * 0.05, r), (x + dx, y + s_ * 0.17, r), 0.115, 0.115, seg=20)     # 軸箱蓋
            v.A("steel").cyl((x + dx, y + s_ * 0.17, r), (x + dx, y + s_ * 0.19, r), 0.06, 0.06, seg=16)
            for k in range(6):                                                                         # 大きな軸ばね
                v.A("steel").torus((x + dx, y, r + 0.12 + k * 0.034), 'z', 0.095, 0.014, segR=16, segr=5)
    a.box(x - 0.18, x + 0.18, -0.85, 0.85, r + 0.12, r + 0.28)           # bolster
    a.cyl((x, 0, r + 0.28), (x, 0, r + 0.38), 0.14, 0.14, seg=10)         # centre pivot
    st, bk, bl = v.A("steel"), v.A("black"), v.A("iron", 0.006)
    for s_ in (-1, 1):
        y = s_ * 0.80
        for dx in (-wb / 2, wb / 2):
            for k in range(5):                                            # coil springs
                st.torus((x + dx, y + s_ * 0.0, r + 0.14 + k * 0.034), 'z', 0.06, 0.011, segR=10, segr=4)
            st.cyl((x + dx - 0.02, y + s_ * 0.09, r + 0.14), (x + dx + 0.10, y + s_ * 0.13, r + 0.38), 0.012, 0.012, seg=5)   # damper
        # brake gear: shoe hangers and beams
        for dx in (-wb / 2, wb / 2):
            for sg in (-1, 1):
                bl.box(x + dx + sg * 0.40 - 0.05, x + dx + sg * 0.40 + 0.05, s_ * 0.52 - 0.07, s_ * 0.52 + 0.07, r - 0.25, r + 0.05)
        bk.box(x - wb / 2 - 0.1, x + wb / 2 + 0.1, y - 0.03, y + 0.03, r - 0.20, r - 0.14)
    for dx in (-0.36, 0.36):
        bl.box(x + dx - 0.04, x + dx + 0.04, -0.8, 0.8, r - 0.18, r - 0.08)    # cross beams
    bk.cyl((x - 0.1, 0.35, r + 0.05), (x + 0.45, 0.35, r + 0.05), 0.07, 0.07, seg=10)  # brake cylinder
    for dx in (-wb / 2, wb / 2):                                               # axle gear cases / motors
        bk.cyl((x + dx, -0.15, r), (x + dx, 0.15, r), 0.17, 0.17, seg=12)
    mo = v.A("iron", 0.006)
    for dx in (-wb / 2 + 0.05, wb / 2 - 0.05):                                 # 吊掛式主電動機(車軸に抱く胴+端ブラケット+ギアケース)
        mo.cyl((x + dx + 0.30, -0.52, r + 0.02), (x + dx + 0.30, 0.52, r + 0.02), 0.20, 0.20, seg=16)
        for yy in (-0.52, 0.52):
            bk.cyl((x + dx + 0.30, yy, r + 0.02), (x + dx + 0.30, yy + (0.025 if yy > 0 else -0.025), r + 0.02), 0.13, 0.13, seg=12)
        mo.box(x + dx + 0.04, x + dx + 0.30, 0.38, 0.52, r - 0.10, r + 0.12)   # ギアケース肩
        mo.box(x + dx + 0.04, x + dx + 0.30, -0.52, -0.38, r - 0.10, r + 0.12)
    for s_ in (-1, 1):                                                          # 軸箱守・枕ばね受け・スタビライザ棒
        for dx in (-wb / 2, wb / 2):
            st.box(x + dx - 0.06, x + dx + 0.06, s_ * 0.80 - 0.08, s_ * 0.80 + 0.08, r + 0.30, r + 0.36)
        st.cyl((x - 0.30, s_ * 0.92, r + 0.20), (x + 0.30, s_ * 0.92, r + 0.20), 0.018, 0.018, seg=6)
    for yy in (-0.28, 0.28):                                                    # ブレーキホース・配線
        bk.cyl((x - 0.5, yy, r + 0.20), (x + 0.5, yy, r + 0.22), 0.012, 0.012, seg=5)


def bogie3(v, x, wb=1.8, r=0.43, key="iron"):
    """Three-axle truck centred at x (loco)(リグ: 鉛直軸の台車部品)。"""
    with v.part("bogie", (x, 0.0, 0.0), axis="z"):
        _bogie3(v, x, wb, r, key)
    v.meta["bogies"].append(dict(x=round(float(x), 3), wheelbase=wb, wheel_r=r, axles=3))


def _bogie3(v, x, wb=1.8, r=0.43, key="iron"):
    for dx in (-wb, 0.0, wb):
        wheelset(v, x + dx, r)
    a = v.A(key, 0.008)
    for s in (-1, 1):
        y = s * 0.80
        a.box(x - wb - 0.45, x + wb + 0.45, y - 0.06, y + 0.06, r + 0.02, r + 0.40)
        for dx in (-wb, 0.0, wb):
            a.box(x + dx - 0.17, x + dx + 0.17, y - 0.08, y + 0.08, r - 0.12, r + 0.14)
    a.box(x - wb - 0.35, x - wb + 0.1, -0.8, 0.8, r + 0.12, r + 0.30)
    a.box(x + wb - 0.1, x + wb + 0.35, -0.8, 0.8, r + 0.12, r + 0.30)
    a.box(x - 0.25, x + 0.25, -0.85, 0.85, r + 0.12, r + 0.40)
    for dx in (-wb, 0.0, wb):   # traction motors
        v.A("black").cyl((x + dx - 0.05, 0, r + 0.05), (x + dx + 0.05, 0, r + 0.05), 0.33, 0.33, seg=12)


def coupler(v, end, x, z=0.88, hose=True):
    """Knuckle coupler at +x (end=1) or -x (end=-1), x = body end(リグ: 連結器部品・原点=車体端)。"""
    with v.part("coupler", (x, 0.0, z), axis="z"):
        _coupler(v, end, x, z, hose)
    v.meta["couplers"].append(dict(end=end, x=round(float(x), 3), z=z))


def _coupler(v, end, x, z=0.88, hose=True):
    a = v.A("iron", 0.012)
    a.box(*(sorted((x, x + end * 0.48)) + [-0.13, 0.13, z - 0.11, z + 0.11]))
    a.box(*(sorted((x + end * 0.40, x + end * 0.68)) + [-0.22, 0.10, z - 0.10, z + 0.10]))   # knuckle
    a.cyl((x - end * 0.05, 0, z), (x + end * 0.30, 0, z), 0.05, 0.05, seg=6)
    if hose:
        for s in (-1, 1):
            h = v.A("rubber")
            h.cyl((x + end * 0.06, s * 0.40, z + 0.02), (x + end * 0.14, s * 0.40, z - 0.30), 0.028, 0.028, seg=6)
            h.cyl((x + end * 0.14, s * 0.40, z - 0.30), (x + end * 0.28, s * 0.40, z - 0.34), 0.028, 0.028, seg=6)


def grab_rail(v, p0, p1, r=0.017, key="steel"):
    v.A(key).cyl(p0, p1, r, r, seg=6)


def steps_down(v, x, side, y_body, z_floor, n=2, w=0.5, key="iron"):
    """Boarding steps hanging below a door."""
    a = v.A(key, 0.004)
    for i in range(n):
        z = max(z_floor - 0.30 - i * 0.30, 0.10)       # 踏段はレール頭より下へ出さない
        a.box(x - w / 2, x + w / 2, side * (y_body + 0.02), side * (y_body + 0.10 + 0.01 * i), z, z + 0.035)      # 踏段の張り出しは約0.12〜0.15m(車両限界内。旧: 0.30〜0.42mで限界を超えていた=vehcheck が検出)
    for s in (-1, 1):
        a.box(x + s * w / 2 - 0.02, x + s * w / 2 + 0.02, side * (y_body + 0.02), side * (y_body + 0.05), max(z_floor - 0.30 - (n - 1) * 0.3, 0.10), z_floor)


def roof_vents(v, xs, z_roof, n_side=0, key="roof"):
    a = v.A(key, 0.008)
    for x in xs:
        a.cyl((x - 0.28, 0, z_roof + 0.06), (x + 0.28, 0, z_roof + 0.06), 0.17, 0.17, seg=12)
        a.box(x - 0.22, x + 0.22, -0.22, 0.22, z_roof - 0.02, z_roof + 0.08)


def window_bays(v, bays, W, zw0, zw1, wall_key, glass_key="glass", curtain_p=0.35, seed=0, door_key=None,
                x_center=0.0, frame_key=None, pillar=0.12, door_win=True, door_drop=0.55):
    """Window band: recessed dark glass core + pillars + doors + curtains; both flanks."""
    rnd = random.Random(seed)
    total = sum(w for _, w in bays)
    x = x_center - total / 2
    h = W / 2
    wall = v.A(wall_key, 0.004)
    gl = v.A(glass_key)
    cur = v.A("curtain")
    fk = v.A(frame_key or wall_key, 0.003)
    doors = []
    dk = v.A(door_key or wall_key, 0.004)
    # glass core spans the whole band, wall pillars cover what is not window
    for s_ in (-1, 1):
        gl.box(x, x + total, *sorted((s_ * (h - 0.070), s_ * (h - 0.064))), zw0, zw1)
    for kind, w in bays:
        xa, xb = x, x + w
        for s in (-1, 1):
            if kind == 'W':
                wall.box(xa, xa + pillar / 2, *sorted((s * (h - 0.078), s * h)), zw0, zw1)
                wall.box(xb - pillar / 2, xb, *sorted((s * (h - 0.078), s * h)), zw0, zw1)
                zm = zw0 + (zw1 - zw0) * 0.52
                fk.box(xa + pillar / 2, xb - pillar / 2, *sorted((s * (h - 0.082), s * (h - 0.02))), zm - 0.018, zm + 0.018)
                fk.box(xa + pillar / 2, xb - pillar / 2, *sorted((s * (h - 0.082), s * (h - 0.012))), zw0 - 0.04, zw0 + 0.01)
                fk.box(xa + pillar / 2, xb - pillar / 2, *sorted((s * (h - 0.082), s * (h - 0.012))), zw1 - 0.01, zw1 + 0.04)
                if rnd.random() < curtain_p:
                    lo = zw1 - (zw1 - zw0) * rnd.uniform(0.25, 0.7)
                    cur.box(xa + pillar / 2, xb - pillar / 2, *sorted((s * (h - 0.115), s * (h - 0.095))), lo, zw1)
            elif kind == 'D':
                if s == 1:
                    doors.append((xa + xb) / 2)
                dk.box(xa, xb, *sorted((s * (h - 0.078), s * (h + 0.014))), zw0 - door_drop, zw1 + 0.06)
                if door_win:
                    gl.box(xa + 0.14, xb - 0.14, *sorted((s * (h + 0.012), s * (h + 0.022))), zw0 + 0.22, zw1 - 0.06)
                grab_rail(v, (xa + 0.07, s * (h + 0.06), zw0 - door_drop + 0.1), (xa + 0.07, s * (h + 0.06), zw1), 0.016)
                grab_rail(v, (xb - 0.07, s * (h + 0.06), zw0 - door_drop + 0.1), (xb - 0.07, s * (h + 0.06), zw1), 0.016)
            elif kind == 's':   # solid wall bay with a small high window
                wall.box(xa, xb, *sorted((s * (h - 0.078), s * h)), zw0, zw1)
                gl.box(xa + 0.1, xb - 0.1, *sorted((s * (h + 0.0), s * (h + 0.012))), zw0 + 0.25, zw1 - 0.2)
        x = xb
    return total, doors


def interior(v, x0, x1, W, zs, zw1, zt, pitch=1.0, seed=0, person_p=0.3, cross=True, rack=True):
    """Passenger saloon seen through the windows: floor, seat backs, passengers, luggage racks, straps, lamps."""
    rnd = random.Random(seed)
    h = W / 2
    v.A("floorw").box(x0, x1, -h + 0.07, h - 0.07, zs, zs + 0.02)
    v.A("cream").box(x0, x1, -h + 0.07, h - 0.07, zw1 + 0.02, zw1 + 0.06) if False else None
    n = int((x1 - x0) / pitch)
    cl = ["cl1", "cl2", "cl3", "cl4"]
    for i in range(n):
        x = x0 + pitch * (i + 0.5)
        for s in (-1, 1):
            if cross:
                v.A("moq", 0.01).box(x - 0.05, x + 0.05, *sorted((s * 0.25, s * 1.0)), zs, zs + 0.28)
                if rnd.random() < person_p:
                    yy = s * rnd.uniform(0.5, 0.85)
                    c = rnd.choice(cl)
                    v.A(c, 0.02, True).box(x + 0.10, x + 0.42, yy - 0.19, yy + 0.19, zs, zs + 0.17)
                    v.A("skin", 0.0, True).sphere((x + 0.26, yy, zs + 0.34), (0.095, 0.085, 0.11), seg=8, rings=6)
                    v.A("hair", 0.0, True).sphere((x + 0.23, yy, zs + 0.37), (0.10, 0.09, 0.10), seg=8, rings=5)
            else:
                v.A("moq", 0.01).box(x - 0.2, x + 0.2, *sorted((s * (h - 0.35), s * (h - 0.12))), zs, zs + 0.24)
        if rack:
            pass
    if rack:
        for s in (-1, 1):
            v.A("steel").box(x0, x1, *sorted((s * (h - 0.12), s * (h - 0.42))), zw1 - 0.28, zw1 - 0.26)
            for i in range(0, n + 1):
                xx = x0 + pitch * i
                v.A("steel").box(xx - 0.01, xx + 0.01, *sorted((s * (h - 0.12), s * (h - 0.42))), zw1 - 0.28, zw1 - 0.20)
            v.A("steel").box(x0, x1, s * (h - 0.42) - 0.01, s * (h - 0.42) + 0.01, zw1 - 0.28, zw1 - 0.10)
    for i in range(1, n, 1):
        x = x0 + pitch * i
        if i % 2:
            v.A("steel").cyl((x, 0.0, zt + 0.08), (x, 0.0, zw1 - 0.35), 0.006, 0.006, seg=4)
            v.A("steel").torus((x, 0.0, zw1 - 0.4), 'x', 0.05, 0.007, segR=10, segr=4)
    for sgn in (-1, 1):
        v.A("lamp_in").box(x0, x1, *sorted((sgn * 0.45, sgn * 0.75)), zw1 - 0.015, zw1)
    v.A("cream").box(x0, x1, -h + 0.07, h - 0.07, zw1 - 0.012, zw1 - 0.005) if False else None


def wall_open(v, key, ax, a0, a1, f0, f1, z0, z1, openings, bevel=0.004):
    """Wall with rectangular holes. ax='y': extends along x (a0..a1), thickness in y (f0..f1);
    ax='x': extends along y, thickness in x. openings: [(pa, pb, za, zb)] with disjoint (pa,pb)."""
    acc = v.A(key, bevel)
    f0, f1 = sorted((f0, f1))

    def B(p0, p1, za, zb):
        if p1 - p0 < 1e-4 or zb - za < 1e-4:
            return
        if ax == 'y':
            acc.box(p0, p1, f0, f1, za, zb)
        else:
            acc.box(f0, f1, p0, p1, za, zb)
    cur = a0
    for (pa, pb, za, zb) in sorted(openings):
        B(cur, pa, z0, z1)
        B(pa, pb, z0, za)
        B(pa, pb, zb, z1)
        cur = pb
    B(cur, a1, z0, z1)
