"""穂波野 北東区画: 国鉄本社ビル・鉄道記念館・初代機関庫(保存)・発祥記念広場。M06(穂波野)のローカル座標。"""
import math
from common import *
import lib, props, rooms, trackkit
from props import G, face_plane
from rooms import shell, floor_boards, ceiling, partition, desk, counter, lamp_point

HQ_ZONE = (43.0, 125.0, 25.0, 58.0)     # 水田を空ける範囲 (x0,x1,y0,y1)
HQ = dict(x0=52.0, x1=96.0, y0=40.0, y1=54.0)
MU = dict(x0=101.0, x1=123.0, y0=41.0, y1=53.0)
SHED = dict(x0=108.0, x1=121.0, y0=26.5, y1=37.5)


def _plaza():
    g = G("hq_plaza", "Roads")
    g.a("dirt").box(HQ_ZONE[0], HQ_ZONE[1], HQ_ZONE[2], HQ_ZONE[3], -0.01, 0.025)
    g.a("concrete", bevel=0.01).box(60, 88, 31.0, 40.0, 0.0, 0.05)          # 本社前の石畳
    g.a("concrete", bevel=0.01).box(100, 124, 38.0, 41.0, 0.0, 0.05)        # 記念館前
    g.a("white_line").box(73.8, 74.2, 31.0, 40.0, 0.05, 0.06)               # 正面軸
    g.build()


def _floors(g, b, nfl=3, fh=4.0):
    for k in range(nfl + 1):
        z = 0.3 + k * fh
        g.a("concrete", bevel=0.01).box(b["x0"] + 0.1, b["x1"] - 0.1, b["y0"] + 0.1, b["y1"] - 0.1, z - 0.22, z) if 0 < k <= nfl else None
    floor_boards(g, b["x0"] + 0.1, b["x1"] - 0.1, b["y0"] + 0.1, b["y1"] - 0.1, 0.3)


def _hq():
    b = HQ
    g = G("hq_main", "Buildings")
    fh, nfl = 4.0, 3
    cx = (b["x0"] + b["x1"]) / 2
    for k in range(nfl):
        zb = 0.3 + k * fh
        ops = {"S": [], "N": [], "W": [], "E": []}
        for i in range(10):                              # 南面(正面)の窓: 10連
            xa = b["x0"] + 2.0 + i * 4.2
            if k == 0 and abs(xa + 0.9 - cx) < 3.2:
                continue
            ops["S"].append((xa, xa + 1.8, zb + 0.9, zb + 3.2, "glass"))
        for i in range(10):
            xa = b["x0"] + 2.0 + i * 4.2
            ops["N"].append((xa, xa + 1.8, zb + 0.9, zb + 3.2, "glass"))
        for yy in (43.0, 49.0):
            ops["W"].append((yy, yy + 1.6, zb + 0.9, zb + 3.2, "glass"))
            ops["E"].append((yy, yy + 1.6, zb + 0.9, zb + 3.2, "glass"))
        if k == 0:
            ops["S"].append((cx - 2.0, cx + 2.0, zb, zb + 3.1, "open"))     # 玄関(開口)
        shell(g, b["x0"], b["x1"], b["y0"], b["y1"], zb, zb + fh, t=0.35, ops=ops, wall="brick" if k == 0 else "pl_cream" if "pl_cream" in M else "concrete")
        g.a("concrete", bevel=0.01).box(b["x0"] - 0.15, b["x1"] + 0.15, b["y0"] - 0.15, b["y1"] + 0.15, zb + fh - 0.25, zb + fh)   # 腰帯
        if k > 0:
            g.a("concrete", bevel=0.01).box(b["x0"] + 0.35, b["x1"] - 0.35, b["y0"] + 0.35, b["y1"] - 0.35, zb - 0.22, zb)
        # 室内: 廊下(北側)+事務室(南側)に机。2階以上は大会議室(中央)
        yc = 47.0
        partition(g, 'x', yc, b["x0"] + 0.35, b["x1"] - 0.35, zb, zb + fh - 0.25, doors=[(cx - 1.5, cx + 1.5), (b["x0"] + 8, b["x0"] + 9.2), (b["x1"] - 9.2, b["x1"] - 8)], kind="plaster_in")
        for i in range(8):
            for j in range(2):
                desk(g, b["x0"] + 3.0 + i * 5.0, 42.2 + j * 2.4, zb, face='N' if j else 'S')
        for i in range(0, 10, 3):
            lamp_point(b["x0"] + 4 + i * 4, 44.0, zb + fh - 0.5, watt=25.0)
    zt = 0.3 + nfl * fh
    g.a("concrete", bevel=0.02).box(b["x0"] - 0.3, b["x1"] + 0.3, b["y0"] - 0.3, b["y1"] + 0.3, zt, zt + 0.45)       # 屋根スラブ
    g.a("concrete", bevel=0.02).box(b["x0"] - 0.3, b["x1"] + 0.3, b["y0"] - 0.3, b["y0"] + 0.05, zt + 0.45, zt + 1.1)     # パラペット
    g.a("concrete", bevel=0.02).box(b["x0"] - 0.3, b["x1"] + 0.3, b["y1"] + 0.25, b["y1"] + 0.3, zt + 0.45, zt + 1.1)
    # 玄関ポーチ: 角柱6本+大庇
    for i in range(6):
        xx = cx - 4.6 + i * 1.84
        g.a("concrete", bevel=0.02).box(xx - 0.3, xx + 0.3, b["y0"] - 4.0, b["y0"] - 3.4, 0.0, 5.6)
    g.a("concrete", bevel=0.02).box(cx - 5.4, cx + 5.4, b["y0"] - 4.3, b["y0"] + 0.1, 5.6, 6.2)
    g.a("concrete", bevel=0.01).box(cx - 5.6, cx + 5.6, b["y0"] - 4.6, b["y0"] + 0.1, 0.0, 0.3)      # 車寄せの段
    # 中央塔(時計)と旗竿
    g.a("brick", bevel=0.02).box(cx - 3.0, cx + 3.0, b["y0"] + 1.0, b["y0"] + 6.0, zt + 0.45, zt + 5.5)
    g.a("roof").extrude_x([(b["y0"] + 0.6, zt + 5.5), (b["y0"] + 3.5, zt + 7.5), (b["y0"] + 6.4, zt + 5.5)], cx - 3.3, cx + 3.3)
    g.a("iron_black").cyl((b["x1"] - 4, b["y0"] - 2.0, 0.0), (b["x1"] - 4, b["y0"] - 2.0, 11.0), 0.07, seg=8)
    g.a("post_red").box(b["x1"] - 4 + 0.03, b["x1"] - 4 + 0.03 + 0.02, b["y0"] - 2.0 - 0.9, b["y0"] - 2.0, 9.4, 10.8) if False else None
    g.build()
    face_plane("hq_sign_plane", "hq_sign.png", 'S', cx, b["y0"] - 0.2, 7.6, 9.0, h=2.3, off=0.0)
    face_plane("hq_emblem", "emblem_first.png", 'S', cx, b["y0"] + 1.0 - 0.02, 0.3 + 3 * fh + 2.0, 2.2, h=2.2)
    # 時計
    face_plane("hq_clock", "clock.png", 'S', cx, b["y0"] + 1.0 - 0.02, 0.3 + 3 * fh + 2.7, 2.6, h=2.6)


def _museum():
    b = MU
    g = G("hq_museum", "Buildings")
    zb, h = 0.3, 6.2
    ops = {"S": [(b["x0"] + 3, b["x0"] + 6, zb + 0.4, zb + 3.2, "glass"), (b["x1"] - 6, b["x1"] - 3, zb + 0.4, zb + 3.2, "glass"),
                 ((b["x0"] + b["x1"]) / 2 - 1.3, (b["x0"] + b["x1"]) / 2 + 1.3, zb, zb + 2.8, "open")],
           "N": [(b["x0"] + 4, b["x0"] + 8, zb + 1.5, zb + 4.5, "glass"), (b["x1"] - 8, b["x1"] - 4, zb + 1.5, zb + 4.5, "glass")],
           "W": [(45.0, 48.0, zb + 1.5, zb + 4.5, "glass")], "E": [(45.0, 48.0, zb + 1.5, zb + 4.5, "glass")]}
    shell(g, b["x0"], b["x1"], b["y0"], b["y1"], zb, zb + h, t=0.3, ops=ops, wall="brick")
    g.a("concrete", bevel=0.02).box(b["x0"] - 0.3, b["x1"] + 0.3, b["y0"] - 0.3, b["y1"] + 0.3, zb + h, zb + h + 0.3)
    g.a("roof").extrude_x([(b["y0"] - 0.6, zb + h + 0.3), ((b["y0"] + b["y1"]) / 2, zb + h + 2.6), (b["y1"] + 0.6, zb + h + 0.3)], b["x0"] - 0.4, b["x1"] + 0.4)
    floor_boards(g, b["x0"] + 0.3, b["x1"] - 0.3, b["y0"] + 0.3, b["y1"] - 0.3, zb)
    ceiling(g, b["x0"] + 0.3, b["x1"] - 0.3, b["y0"] + 0.3, b["y1"] - 0.3, zb + h - 0.3, beams_axis='x', step=2.5)
    # 展示: ガラスケース(模型)・歴代ヘッドマーク・年表パネル
    for i in range(4):
        xx = b["x0"] + 3.5 + i * 4.6
        g.a("wood_dark", bevel=0.01).box(xx - 1.0, xx + 1.0, 44.0, 45.4, zb, zb + 0.9)
        g.a("glass").box(xx - 1.0, xx + 1.0, 44.0, 45.4, zb + 0.9, zb + 1.4)
        g.a("iron_black", bevel=0.01).box(xx - 0.6, xx + 0.6, 44.4, 45.0, zb + 0.9, zb + 1.0)
        g.a("post_red", bevel=0.01).box(xx - 0.5, xx + 0.5, 44.5, 44.9, zb + 1.0, zb + 1.3)
    for i in range(4):
        xx = b["x0"] + 3.5 + i * 4.6
        face_plane(f"mu_panel{i}", ["headmark.png", "emblem_first.png", "fare_board.png", "ad_safety.png"][i], 'S', xx, b["y1"] - 0.32, zb + 1.3, 1.8, h=1.3)
    for xx, yy in ((b["x0"] + 2.5, 50.0), (b["x1"] - 2.5, 50.0)):
        lamp_point(xx, yy, zb + h - 0.7, watt=30.0)
    counter(g, b["x0"] + 8.5, b["x0"] + 12.5, 42.4, zb)
    g.build()
    cxm = (b["x0"] + b["x1"]) / 2
    face_plane("mu_sign", "museum_sign.png", 'S', cxm, b["y0"] - 0.34, zb + h - 1.3, 5.0, h=1.5)


def _shed():
    b = SHED
    g = G("hq_firstshed", "Buildings")
    zb, h = 0.0, 5.0
    cx = (b["x0"] + b["x1"]) / 2
    # 煉瓦の1線庫(切妻、前面にアーチ扉。扉は開放)
    ops = {"S": [(cx - 2.0, cx + 2.0, zb, zb + 4.0, "open")], "N": [(cx - 0.8, cx + 0.8, zb + 3.0, zb + 4.2, "glass")],
           "W": [(29.5, 31.0, zb + 2.6, zb + 4.0, "glass"), (33.0, 34.5, zb + 2.6, zb + 4.0, "glass")],
           "E": [(29.5, 31.0, zb + 2.6, zb + 4.0, "glass"), (33.0, 34.5, zb + 2.6, zb + 4.0, "glass")]}
    shell(g, b["x0"], b["x1"], b["y0"], b["y1"], zb, zb + h, t=0.4, ops=ops, wall="brick")
    g.a("roof").extrude_x([(b["y0"] - 0.5, zb + h), ((b["y0"] + b["y1"]) / 2, zb + h + 3.4), (b["y1"] + 0.5, zb + h)], b["x0"] - 0.4, b["x1"] + 0.4)
    # 妻壁(前面)の三角部
    g.a("brick", bevel=0.01).extrude_x([(b["y0"], zb + h), ((b["y0"] + b["y1"]) / 2, zb + h + 3.2), (b["y1"], zb + h)], b["x0"] + 0.0, b["x0"] + 0.4) if False else None
    for i in range(6):                                              # 壁柱(控え)
        yy = b["y0"] + 0.7 + i * 1.9
        g.a("stone", bevel=0.02).box(b["x0"] - 0.15, b["x0"] + 0.1, yy - 0.2, yy + 0.2, 0.0, h)
        g.a("stone", bevel=0.02).box(b["x1"] - 0.1, b["x1"] + 0.15, yy - 0.2, yy + 0.2, 0.0, h)
    g.a("stone", bevel=0.02).box(cx - 2.4, cx - 1.9, b["y0"] - 0.1, b["y0"] + 0.4, 0.0, 4.1)       # 扉口の石枠
    g.a("stone", bevel=0.02).box(cx + 1.9, cx + 2.4, b["y0"] - 0.1, b["y0"] + 0.4, 0.0, 4.1)
    g.a("stone", bevel=0.02).box(cx - 2.4, cx + 2.4, b["y0"] - 0.1, b["y0"] + 0.4, 4.0, 4.4)
    floor_boards(g, b["x0"] + 0.4, b["x1"] - 0.4, b["y0"] + 0.4, b["y1"] - 0.4, 0.05) if False else None
    g.build()
    face_plane("shed_plate_p", "shed_plate.png", 'S', cx - 4.3, b["y0"] - 0.12, 1.6, 2.0, h=0.82)
    # 保存線: 庫内から南へ短い側線(車止め付き)。標準軌ではなく狭軌の既存規格
    P = np.array([[cx, b["y0"] - 12.0], [cx, b["y1"] - 0.6]], float)
    Q, _ = trackkit.resample(P, 1.0)
    trackkit.build_track("hq_shedtrack", Q, wooden=True, ballast=True, fittings=True, cam=None)
    trackkit.buffer_stop(float(Q[-1][0]), float(Q[-1][1]), 90.0)
    try:
        import steam2 as S
        v = S.make_steam2("hq_C57", "C57", ang=90, smoke=False, num_plate="plate_c.png")
        xs = [p[0] for p in v.pts] if hasattr(v, "pts") else None
        v.place(cx, b["y0"] + 4.2, math.radians(90), z=0.262)
    except Exception as e:
        print("hq loco fail", e)
    lamp_point(cx, (b["y0"] + b["y1"]) / 2, zb + 4.4, watt=45.0)


def _memorial():
    g = G("hq_memorial", "Props")
    x, y = 74.0, 33.0
    g.a("stone", bevel=0.03).box(x - 2.4, x + 2.4, y - 1.6, y + 1.6, 0.0, 0.5)
    g.a("stone", bevel=0.03).box(x - 1.2, x + 1.2, y - 0.5, y + 0.5, 0.5, 4.2)
    g.a("stone", bevel=0.03).box(x - 1.3, x + 1.3, y - 0.6, y + 0.6, 4.2, 4.5)
    g.build()
    face_plane("hq_plaque_p", "hq_plaque.png", 'S', x, y - 0.52, 1.4, 1.9, h=0.8)
    g = G("hq_mile0", "Props")
    x2, y2 = 66.0, 32.0
    g.a("white_paint", bevel=0.02).box(x2 - 0.25, x2 + 0.25, y2 - 0.25, y2 + 0.25, 0.0, 1.4)
    g.build()
    face_plane("mile0_p", "mile0_plate.png", 'S', x2, y2 - 0.27, 0.5, 0.45, h=0.8)
    # 並木
    import veg
    for xx, yy in ((58, 28.5), (90, 28.5), (103, 23.0)):
        veg.CARD_SCALE = 0.4
        veg.zelkova(xx, yy, h=9.0, rad=3.6, seed=int(xx))
        veg.CARD_SCALE = 1.0
    props.FOOT.append((HQ["x0"] - 4, HQ["x1"] + 4, HQ["y0"] - 12, HQ["y1"] + 3))
    props.FOOT.append((MU["x0"] - 2, MU["x1"] + 2, 26, MU["y1"] + 3))
    props.FOOT.append((SHED["x0"] - 3, SHED["x1"] + 3, 12, 38))
    props.FOOT.append((60, 90, 29, 41))


def build_hq():
    import kit2
    kit2.mats2()
    _plaza()
    _hq()
    _museum()
    _shed()
    _memorial()
