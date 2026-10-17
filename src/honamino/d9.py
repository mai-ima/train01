"""D9a: 穂波野の旅客ホーム増設。第3線(T3)と第4線(T4)の間に島式ホーム(第2島)、第5線(T5)と第6線(T6)の間に短い島式ホーム(第3島)。
島間は構内踏切(板張り)で結ぶ。仕上げは core.build_island と同じ(石積みの側面+砂利舗装+コンクリート縁石+白線+端のスロープ)。"""
from common import *
from lib import Acc

ISLAND2 = (-4.0, 48.0, T4 + 1.7, T3 - 1.7)       # x0, x1, y0(南縁), y1(北縁)
ISLAND3 = (46.0, 66.0, T6 + 1.7, T5 - 1.7)


def _island(name, rect, ramps=(1, -1)):
    x0, x1, y0, y1 = rect
    zt = Z_PLAT
    body = Acc(f"{name}_body", M["stone"], "Platform", bevel=0.01)
    body.box(x0, x1, y0, y1, -0.25, zt - 0.05)
    body.build()
    top = Acc(f"{name}_surface", M["plat_top"], "Platform")
    top.box(x0 + 0.04, x1 - 0.04, y0 + 0.62, y1 - 0.62, zt - 0.07, zt - 0.035)
    top.build()
    cope = Acc(f"{name}_coping", M["concrete"], "Platform", bevel=0.012)
    cope.box(x0, x1, y0 - 0.02, y0 + 0.62, zt - 0.12, zt)
    cope.box(x0, x1, y1 - 0.62, y1 + 0.02, zt - 0.12, zt)
    cope.build()
    line = Acc(f"{name}_lines", M["white_line"], "Platform", closed=False)
    line.box(x0 + 0.1, x1 - 0.1, y0 + 0.40, y0 + 0.50, zt, zt + 0.004)
    line.box(x0 + 0.1, x1 - 0.1, y1 - 0.50, y1 - 0.40, zt, zt + 0.004)
    line.build()
    for sgn, xe in ((1, x1), (-1, x0)):
        if sgn not in ramps:
            continue
        r = Acc(f"{name}_ramp", M["plat_top"], "Platform", closed=True)
        r.extrude_y([(xe, -0.25), (xe, zt - 0.035), (xe + sgn * 5.0, 0.0), (xe + sgn * 5.0, -0.25)], y0, y1)
        r.build()
    # 上屋の柱列と灯(昭和の木造ホーム上屋に倣う簡易版。本格的な上屋は D9c で駅舎と合わせて作る)
    pst = Acc(f"{name}_posts", M["wood_dark"], "Platform", bevel=0.006)
    lamp = Acc(f"{name}_lamps", M["lamp_glow"], "Platform")
    ym = (y0 + y1) / 2
    for x in np.arange(x0 + 4.0, x1 - 3.0, 8.0):
        pst.box(x - 0.07, x + 0.07, ym - 0.07, ym + 0.07, zt, zt + 3.3)
        pst.box(x - 0.9, x + 0.9, ym - 0.05, ym + 0.05, zt + 3.2, zt + 3.3)
        lamp.box(x - 0.12, x + 0.12, ym - 0.12, ym + 0.12, zt + 3.05, zt + 3.2)
    pst.build()
    lamp.build()


def _crossing(x, y_from, y_to, tracks):
    """構内踏切(板張り): x を中心に y_from→y_to を横切り、通過する各線路にレール間の板を敷く。"""
    pl = Acc("d9_crossing_boards", M["wood_dark"], "Track", bevel=0.01)
    xc0, xc1 = x - 0.5, x + 0.5
    for T in tracks:
        pl.box(xc0, xc1, T - 1.0, T + 1.0, Z_SLEEP + 0.004, Z_RAIL - 0.022)
    lo, hi = min(y_from, y_to), max(y_from, y_to)
    pl.box(xc0, xc1, lo, hi, Z_SLEEP - 0.01, Z_SLEEP + 0.03)
    pl.build()


class _G:
    """kit.footbridge が使う g.a(キー, bevel=) の最小アダプタ: キーごとに Acc を1つ作り、最後にまとめて build する。"""
    def __init__(self, name):
        self.name, self.accs = name, {}

    def a(self, key, bevel=0.0):
        if key not in self.accs:
            self.accs[key] = Acc(f"{self.name}_{key}", M[key], "Structures", bevel=bevel)
        return self.accs[key]

    def build(self):
        for v in self.accs.values():
            v.build()


def _footbridge(x=20.0):
    """D9b: 屋根つき跨線橋。駅前(北)から本屋側ホーム・第1島・第2島(T4北側)へ。第2島は橋の-x側の階段で、第1島は-x側の階段で降りる。"""
    from kit import footbridge
    g = _G("d9_fb")
    ym1 = (ISLAND[2] + ISLAND[3]) / 2               # 第1島(T2/T3)の中心
    ym2 = (ISLAND2[2] + ISLAND2[3]) / 2             # 第2島(T3/T4)の中心
    footbridge(g, x, Y_WALL, ym2, covered=True, kind="steel", z=5.2, lo_turn=True, mid=[ym1])
    g.build()


WING_DX = -33.0                                   # 作図は x=4..17.6、最後に西(本屋の西側の空き地)へ移す → x=-29..-15.4
WEST_EXT = (-34.0, -18.0, 1.7, Y_WALL)             # 本屋側ホームの西側延伸(既存の西端スロープは撤去して端に付け直す)
WING = (4.0, 17.6, Y_WALL, Y_WALL + 5.0)          # x0, x1, y0, y1: 駅舎東棟(木造2階建・切妻瓦屋根)


def _wing():
    """D9c: 駅舎東棟。1階=待合室・出札/駅長室・手荷物/売店・階段室、2階=事務室・宿直室(畳)。ホーム側に庇。室内灯つき。"""
    import rooms
    before = set(bpy.data.objects.keys())
    from rooms import shell, partition, floor_boards, floor_tatami, ceiling, counter, desk, shelf, pot_stove, stair_run, lamp_point
    from props import G
    from station import add_tin_roof
    x0, x1, y0, y1 = WING
    import veg
    veg.TREE_EXCL.append((x0 + WING_DX, x1 + WING_DX, y0, y1))
    zf = Z_PLAT + 0.12                      # 1階床
    H = 2.8
    z2 = zf + H                             # 2階床
    zt = z2 + 2.6                           # 軒(壁の上端)
    g = G("d9c_wing", col="Station")
    ops = {
        "S": [(5.0, 6.2, zf, zf + 2.05, "door"), (7.0, 8.0, zf + 0.9, zf + 2.0, "glass"),
              (9.0, 10.2, zf + 0.9, zf + 1.6, "glass"), (11.0, 12.0, zf + 0.9, zf + 2.0, "glass"),
              (13.2, 14.4, zf + 0.9, zf + 1.6, "glass"), (14.7, 15.7, zf + 0.9, zf + 1.7, "glass"),
              (5.2, 6.4, z2 + 0.9, z2 + 2.0, "glass"), (8.0, 9.2, z2 + 0.9, z2 + 2.0, "glass"),
              (10.8, 12.0, z2 + 0.9, z2 + 2.0, "glass"), (13.6, 14.8, z2 + 0.9, z2 + 2.0, "glass")],
        "N": [(6.0, 7.2, zf + 0.9, zf + 2.0, "glass"), (9.6, 10.6, zf + 0.9, zf + 2.0, "glass"),
              (13.0, 14.0, zf, zf + 2.05, "door"), (16.3, 17.2, zf + 0.9, zf + 2.0, "glass"),
              (5.6, 6.8, z2 + 0.9, z2 + 2.0, "glass"), (9.4, 10.6, z2 + 0.9, z2 + 2.0, "glass"),
              (13.0, 14.2, z2 + 0.9, z2 + 2.0, "glass")],
        "W": [(6.4, 7.4, zf + 0.9, zf + 2.0, "glass"), (6.4, 7.4, z2 + 0.9, z2 + 2.0, "glass")],
        "E": [(6.4, 7.4, z2 + 0.9, z2 + 2.0, "glass")],
    }
    # 石の基礎+壁+開口(ガラス・建具つき)
    g.a("stone", bevel=0.01).box(x0 - 0.1, x1 + 0.1, y0 - 0.05, y1 + 0.05, -0.25, zf - 0.02)
    shell(g, x0, x1, y0, y1, zf - 0.02, zt, t=0.14, ops=ops, wall="wall")
    # 1階・2階の床と天井(2階床=1階天井)
    floor_boards(g, x0 + 0.14, x1 - 0.14, y0 + 0.14, y1 - 0.14, zf)
    sx0, sx1, sy0, sy1 = 15.7, 16.9, 4.7, 8.1       # 階段の抜け
    for (a, b, c, d_) in ((x0 + 0.14, sx0, y0 + 0.14, y1 - 0.14), (sx1, x1 - 0.14, y0 + 0.14, y1 - 0.14),
                          (sx0, sx1, sy1, y1 - 0.14), (sx0, sx1, y0 + 0.14, sy0)):
        g.a("floor", bevel=0.004).box(a, b, c, d_, z2 - 0.22, z2)
        g.a("wood_dark", bevel=0.01).box(a, b, c, d_, z2 - 0.36, z2 - 0.22)           # 梁の見え
    ceiling(g, x0 + 0.14, x1 - 0.14, y0 + 0.14, y1 - 0.14, zt - 0.05, beams_axis='y', step=1.4)
    # 1階の間仕切り: 待合室|出札・駅長室|手荷物・売店|階段室
    for xp, doors in ((8.6, [(5.2, 6.2)]), (12.6, [(5.4, 6.4)]), (15.0, [(5.6, 6.6)])):
        partition(g, 'y', xp, y0 + 0.14, y1 - 0.14, zf, z2 - 0.22, doors=doors, kind="plaster_in")
    # 2階の間仕切り: 事務室|宿直室
    partition(g, 'y', 11.6, y0 + 0.14, y1 - 0.14, z2, zt, doors=[(6.2, 7.2)], kind="plaster_in")
    # 階段(南から北へ上る)
    stair_run(g, 'y', 4.9, 8.0, 16.3, zf, z2, width=1.1, rise=0.2, key="wood_dark")
    # ---- 待合室: 長椅子・ストーブ・時刻表
    for xb in (5.0, 6.4, 7.8):
        g.a("wood", bevel=0.01).box(xb - 0.55, xb + 0.55, y0 + 1.6, y0 + 2.0, zf + 0.44, zf + 0.5)
        g.a("wood", bevel=0.01).box(xb - 0.55, xb + 0.55, y0 + 1.95, y0 + 2.0, zf + 0.5, zf + 0.95)
        for xx in (xb - 0.5, xb + 0.5):
            g.a("wood_dark").box(xx - 0.03, xx + 0.03, y0 + 1.65, y0 + 1.95, zf, zf + 0.44)
    pot_stove(g, 6.4, y0 + 3.6, zf, pipe_to=zt - 0.1)
    # ---- 出札・駅長室: 出札カウンター(ホーム側の窓の内側)・机・金庫棚
    counter(g, 9.0, 10.4, y0 + 0.6, zf, d=0.5, h=1.0)
    desk(g, 10.6, y0 + 3.2, zf, w=1.5, d=0.8, face='N')
    shelf(g, 8.8, 12.4, y1 - 0.14, zf, h=1.9, d=0.35, rows=4, face='S', goods="jars", seed=3)
    # ---- 手荷物・売店: 窓口カウンターと棚
    counter(g, 13.2, 14.5, y0 + 0.6, zf, d=0.5, h=0.95)
    shelf(g, 13.0, 14.9, y1 - 0.14, zf, h=1.9, d=0.35, rows=4, face='S', goods="jars", seed=5)
    # ---- 2階: 事務室(机2・書棚)・宿直室(畳)
    desk(g, 6.2, y0 + 1.4, z2, w=1.5, d=0.8, face='N')
    desk(g, 8.2, y0 + 3.4, z2, w=1.5, d=0.8, face='S')
    shelf(g, 5.0, 8.4, y1 - 0.14, z2, h=1.9, d=0.35, rows=4, face='S', goods="jars", seed=7)
    floor_tatami(g, 11.74, 15.7, y0 + 0.14, y1 - 0.14, z2 + 0.0, along='x')
    # ---- 照明
    for (a, b, zz, w_) in ((4.0, 8.6, zf, 150), (8.6, 12.6, zf, 150), (12.6, 15.0, zf, 130), (15.0, 17.6, zf, 90),
                           (4.0, 11.6, z2, 150), (11.6, 17.6, z2, 150)):
        for yy in (y0 + 1.5, y1 - 1.5):                          # 各室に2灯(手前と奥)
            lamp_point((a + b) / 2, yy, zz + 2.3, w_ / 2)
    g.build()
    # ---- 屋根(切妻・瓦): 棟は x 方向。厚み0.1の2枚の斜面+妻の三角壁
    rz = zt + 1.9
    rg = G("d9c_roof", col="Station")
    prof_o = [(y0 - 0.7, zt - 0.12), ((y0 + y1) / 2, rz), ((y0 + y1) / 2, rz - 0.14), (y0 - 0.7, zt - 0.26)]
    prof_o2 = [(y1 + 0.7, zt - 0.12), ((y0 + y1) / 2, rz), ((y0 + y1) / 2, rz - 0.14), (y1 + 0.7, zt - 0.26)]
    rg.a("roof", bevel=0.01).extrude_x(prof_o, x0 - 0.6, x1 + 0.6)
    rg.a("roof", bevel=0.01).extrude_x(prof_o2, x0 - 0.6, x1 + 0.6)
    for xa, xb in ((x0, x0 + 0.14), (x1 - 0.14, x1)):
        rg.a("wall", bevel=0.006).extrude_x([(y0, zt), (y1, zt), ((y0 + y1) / 2, rz - 0.14)], xa, xb)
    rg.build()
    # ---- ホーム側の庇(トタン葺き・木柱)
    pc = G("d9c_canopy", col="Station")
    for xx in np.arange(x0 + 0.5, x1, 3.4):
        pc.a("wood_dark", bevel=0.01).box(xx - 0.08, xx + 0.08, 2.35, 2.5, Z_PLAT, zf + 2.75)
    pc.build()
    add_tin_roof((x0 - 0.3, x1 + 0.3), (2.2, y0 + 0.1), zf + 2.65, zf + 3.0, name="d9c_canopy_roof")
    for k in set(bpy.data.objects.keys()) - before:          # 西側ホーム延伸に合わせ、まとめて西へ移す(DOORS 登録は未更新=K2検査は後で)
        ob = bpy.data.objects[k]
        if ob.parent is None:
            ob.location.x += WING_DX
    print("[D9c] 駅舎(西棟):", (x0 + WING_DX, x1 + WING_DX, y0, y1))


def _west_extension():
    """本屋側ホームを西へ16m延伸(既存の西端スロープ ramp は延伸端へ付け直すため撤去)。"""
    for ob in list(bpy.data.objects):
        if ob.type == "MESH" and ob.name.split(".")[0] == "ramp":
            xs = [(ob.matrix_world @ Vector(b)).x for b in ob.bound_box]
            if max(xs) < -17.0:
                bpy.data.objects.remove(ob, do_unlink=True)
    _island("d9_west", WEST_EXT, ramps=(-1,))


FREIGHT = (10.0, 46.0, T6 - 6.0, T6 - 1.7)      # x0, x1, y0(南縁), y1(T6側の縁): 貨物ホーム(T6の南側)


def _freight():
    """D9d: 貨物ホーム(高さは旅客ホームと同じ)・開放式の貨物上屋(木柱+トタン)・荷役クレーン・米俵/木箱/荷車・南側のトラック荷受け道。"""
    import rooms
    from props import G
    from station import add_tin_roof
    x0, x1, y0, y1 = FREIGHT
    zt = Z_PLAT
    body = Acc("d9f_body", M["stone"], "Platform", bevel=0.01)
    body.box(x0, x1, y0, y1, -0.25, zt - 0.05)
    body.build()
    top = Acc("d9f_surface", M["concrete"], "Platform")
    top.box(x0 + 0.04, x1 - 0.04, y0 + 0.04, y1 - 0.62, zt - 0.07, zt - 0.035)
    top.build()
    cope = Acc("d9f_coping", M["concrete"], "Platform", bevel=0.012)
    cope.box(x0, x1, y1 - 0.62, y1 + 0.02, zt - 0.12, zt)
    cope.build()
    for sgn, xe in ((1, x1), (-1, x0)):                     # 端のスロープ(荷車・フォーク用)
        r = Acc("d9f_ramp", M["plat_top"], "Platform", closed=True)
        r.extrude_y([(xe, -0.25), (xe, zt - 0.035), (xe + sgn * 4.0, 0.0), (xe + sgn * 4.0, -0.25)], y0, y1)
        r.build()
    # 荷受け道(南側・未舗装)とトラック用の段差
    rd = Acc("d9f_road", M["dirt"], "Roads")
    rd.box(x0 - 6.0, x1 + 6.0, y0 - 5.0, y0 - 0.1, -0.02, 0.04)
    rd.build()
    # 上屋: 木柱+梁+トタン片流れ(ホーム中央寄り)
    g = G("d9f_shed", col="Station")
    sx0, sx1 = x0 + 4.0, x1 - 6.0
    ya, yb = y0 + 0.6, y1 - 1.2
    for xx in np.arange(sx0, sx1 + 0.1, 4.5):
        for yy in (ya, yb):
            g.a("wood_dark", bevel=0.01).box(xx - 0.1, xx + 0.1, yy - 0.1, yy + 0.1, zt, zt + 3.6)
        g.a("wood_dark", bevel=0.01).box(xx - 0.08, xx + 0.08, ya, yb, zt + 3.45, zt + 3.62)    # 梁
    g.a("wood_dark", bevel=0.01).box(sx0 - 0.1, sx1 + 0.1, ya - 0.05, ya + 0.05, zt + 3.5, zt + 3.62)
    g.a("wood_dark", bevel=0.01).box(sx0 - 0.1, sx1 + 0.1, yb - 0.05, yb + 0.05, zt + 3.7, zt + 3.82)
    g.build()
    add_tin_roof((sx0 - 0.5, sx1 + 0.5), (ya - 0.8, yb + 0.6), zt + 3.62, zt + 4.05, name="d9f_roof")
    # 荷: 米俵の山・木箱・荷車・はかり
    gc = G("d9f_cargo", col="Props")
    rooms.sack_pile(gc, sx0 + 3.0, (ya + yb) / 2, zt, nx=3, ny=2, nz=3, yaw=0.1, seed=11)
    rooms.sack_pile(gc, sx0 + 12.0, (ya + yb) / 2 + 0.3, zt, nx=4, ny=2, nz=2, yaw=-0.05, seed=12)
    for k, xx in enumerate((sx0 + 7.0, sx0 + 8.2, sx0 + 18.0, sx0 + 19.4)):
        gc.a("wood", bevel=0.01).box(xx - 0.4, xx + 0.4, (ya + yb) / 2 - 0.4, (ya + yb) / 2 + 0.4, zt, zt + 0.7 + 0.1 * (k % 2))
    gc.build()
    # 荷役クレーン(門型・ホーム端): 2本脚+ブーム
    cr = G("d9f_crane", col="Station")
    cx = x1 - 2.5
    for yy in (ya, yb):
        cr.a("iron_black", bevel=0.01).box(cx - 0.12, cx + 0.12, yy - 0.12, yy + 0.12, zt, zt + 4.2)
    cr.a("iron_black", bevel=0.01).box(cx - 0.1, cx + 0.1, ya - 2.6, yb + 1.2, zt + 4.0, zt + 4.3)
    cr.a("iron_black").cyl((cx, ya - 1.4, zt + 4.0), (cx, ya - 1.4, zt + 2.4), 0.03, seg=6)
    cr.a("iron_black", bevel=0.01).box(cx - 0.2, cx + 0.2, ya - 1.6, ya - 1.2, zt + 2.0, zt + 2.4)
    cr.build()
    print("[D9d] 貨物ホームと上屋・クレーンを追加:", FREIGHT)



def _people():
    """H3: 新設の島式ホーム・跨線橋・貨物ホーム・西棟まわり・新車庫に人物を配置する(People コレクション=--people で一括表示/非表示)。"""
    from life import Fig, person
    f = Fig("d9_people")
    z = Z_PLAT
    ym2 = (ISLAND2[2] + ISLAND2[3]) / 2
    ym3 = (ISLAND3[2] + ISLAND3[3]) / 2
    ym1 = (ISLAND[2] + ISLAND[3]) / 2
    person(f, 6.0, ym2 + 0.3, 0.2, "man", z=z)
    person(f, 8.0, ym2 - 0.3, 3.2, "woman", z=z)
    person(f, 25.0, ym2, 1.5, "student", z=z, scale=0.82)
    person(f, 33.0, ym2 + 0.4, 3.0, "farmer", z=z, pose="walk")
    person(f, 52.0, ym3, 0.0, "man2", z=z)
    person(f, 56.0, ym3 + 0.3, 3.1, "woman", z=z)
    person(f, 22.0, ym1 + 0.3, 2.0, "man", z=z)                      # 第1島の跨線橋階段そば
    person(f, 20.0, (Y_WALL + ym2) / 2, 1.57, "man2", z=5.2 + 0.03)   # 跨線橋の上(通路中央)
    person(f, 20.0, (Y_WALL + ym2) / 2 + 3.0, 4.7, "student", z=5.2 + 0.03, scale=0.85)
    person(f, 20.0, Y_WALL + 4.0, 0.0, "man", z=5.2 - 0.9)           # 駅前側の階段の途中(おおよその高さ)
    for i, x in enumerate((14.0, 22.0, 30.0, 38.0)):                  # 貨物ホーム: 荷役の作業員
        person(f, x, (FREIGHT[2] + FREIGHT[3]) / 2, 0.6 * i, "worker", z=Z_PLAT - 0.2, pose="walk" if i % 2 else "stand")
    # H1b: 群像を追加(島ごとに待客の列・談笑の2人組・単独の人を散らし、1視点あたりの人数を増やす)。固定シードで再現可能
    import random as _rnd
    rr = _rnd.Random(2024)
    kinds = ["man", "man2", "woman", "student", "farmer"]
    for ym, x0, x1, n in ((ym1, -2.0, 46.0, 9), (ym2, -2.0, 46.0, 10), (ym3, 48.0, 64.0, 6)):
        placed = []
        for _ in range(n * 3):
            if len(placed) >= n:
                break
            x = rr.uniform(x0, x1)
            if abs(x - 20.0) < 2.5 or any(abs(x - p) < 1.6 for p in placed):      # 跨線橋の階段前と近すぎる所は避ける
                continue
            placed.append(x)
            k = rr.choice(kinds)
            person(f, x, ym + rr.uniform(-0.7, 0.7), rr.uniform(0, 6.28), k, z=z, scale=0.82 if k == "student" else rr.uniform(0.94, 1.04), pose=rr.choice(["stand", "stand", "walk"]), skirt=(k == "woman" and rr.random() < 0.5))
            if rr.random() < 0.35:                                                    # 2人組(向かい合って立つ)
                person(f, x + 0.7, ym + rr.uniform(-0.5, 0.5), 3.14, rr.choice(kinds), z=z)
    f.build()

def build_platforms():
    _island("d9_isl2", ISLAND2)
    _island("d9_isl3", ISLAND3)
    # 第1島(T2/T3)→第2島: T3 を横切る。第2島→第3島: T4・T5 を横切る
    _crossing(0.5, ISLAND2[3], T3 + 1.7, [T3])
    _crossing(47.0, ISLAND2[2], ISLAND3[3], [T4, T5])
    _footbridge(20.0)
    _people()
    _west_extension()
    _wing()
    _freight()
    print("[D9b] 跨線橋を追加: x=20")
    print("[D9a] 島式ホーム2面を追加:", ISLAND2, ISLAND3)
