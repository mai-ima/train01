"""kit8: 駅の内部構造(出入口の駅舎・出札・改札・券売機・売店・事務室)。
ticket_hall: 地下駅の地上出入口(階段の真上)に建つ駅舎。ゾーン局所座標(地表 z=0)。
  u 軸: 階段室側(u=0)→街側(u=13.6)。階段口は u=0.9〜6.8(階段は u の小さい側=ホームへ下る)。
  街から入る → 券売機/出札窓口 → 改札(3通路+改札掛のボックス) → 階段口 → ホームへ。"""
import math
import numpy as np
from common import *
import lib
import rooms as R
from rooms import A, lamp_point, counter, desk
from props import G, face_plane
import kit_town as KT


def _mat():
    import kit5
    kit5.mats5()
    if "k8_floor" not in M:
        M["k8_floor"] = M["ug_floor"]


def _img(sid, key, fallback=None):
    try:
        p = KT.img(sid, key)
        return p or fallback
    except Exception:
        return fallback


def ticket_hall(sid, x_in, sg, yc, name=None, tone="ug_plaster"):
    _mat()
    nm = name or f"k6_{sid}_eh{'p' if sg > 0 else 'm'}"
    X = lambda u: x_in + sg * u
    U = 13.6
    y0, y1 = yc - 4.5, yc + 2.8
    zh = 3.5
    x0, x1 = min(X(0), X(U)), max(X(0), X(U))
    g = G(nm, "Buildings")
    gi = G(nm + "_in", "Props")

    def bx(acc, ua, ub, ya, yb, za, zb):
        acc.box(min(X(ua), X(ub)), max(X(ua), X(ub)), ya, yb, za, zb)

    st = "E" if sg > 0 else "W"            # 街側の壁
    uw = lambda a, b: (min(X(a), X(b)), max(X(a), X(b)))
    wins_n = [uw(u - 0.45, u + 0.45) for u in (9.4, 10.8, 12.2)]               # 出札窓口(北壁・事務室側)
    ops = {st: [(yc - 1.5, yc + 1.5, 0.0, 2.7, 'open')] + [(yc - 4.0, yc - 2.0, 0.9, 2.7, 'glass')],
           "N": [(a, b, 1.05, 2.15, 'glass') for (a, b) in wins_n],
           "S": [(uw(u - 1.0, u + 1.0)[0], uw(u - 1.0, u + 1.0)[1], 0.9, 2.6, 'glass') for u in (2.4, 5.2)] + [(uw(11.4, 13.0)[0], uw(11.4, 13.0)[1], 0.9, 2.6, 'glass')]}
    R.shell(g, x0, x1, y0, y1, 0.0, zh, t=0.3, ops=ops, wall=tone)
    # 床(階段口を残す)
    hole_u = (0.9, 6.8)
    hy = (yc - 1.5, yc + 1.5)
    fl = A(g, "k8_floor")
    bx(fl, 0.0, hole_u[0], y0, y1, -0.05, 0.02)
    bx(fl, hole_u[1], U, y0, y1, -0.05, 0.02)
    bx(fl, hole_u[0], hole_u[1], y0, hy[0], -0.05, 0.02)
    bx(fl, hole_u[0], hole_u[1], hy[1], y1, -0.05, 0.02)
    # 階段口の縁: コンクリートの立ち上がり(穴の側面の内張り)と手すり
    cb = A(g, "concrete", 0.01)
    for yy_ in (hy[0], hy[1] - 0.2):
        bx(cb, hole_u[0], hole_u[1], yy_, yy_ + 0.2, -3.0, 0.02)
    bx(cb, hole_u[0] - 0.2, hole_u[0], hy[0], hy[1], -3.0, 0.02)
    bx(cb, hole_u[1], hole_u[1] + 0.2, hy[0], hy[0] + 0.0001, -3.0, 0.02)
    # 屋根・パラペット・庇
    A(g, "concrete", 0.02).box(x0 - 0.35, x1 + 0.35, y0 - 0.35, y1 + 0.35, zh, zh + 0.32)
    A(g, "concrete", 0.02).box(min(X(U), X(U + 2.2)) - 0.0, max(X(U), X(U + 2.2)), yc - 2.6, yc + 2.6, 2.95, 3.12)          # 入口の庇
    for ys_ in (yc - 2.5, yc + 2.5):
        bx(A(g, "iron_black"), U + 1.9, U + 2.1, ys_ - 0.04, ys_ + 0.04, 0.0, 2.95)
    # ---- 室内の仕上げ: 腰壁のタイルと天井の照明
    inner = A(gi, "pl_cream" if "pl_cream" in M else "plasterw")
    bx(inner, 0.32, U - 0.32, y0 + 0.3, y0 + 0.33, 0.0, 1.3)
    bx(inner, 0.32, U - 0.32, y1 - 0.33, y1 - 0.3, 0.0, 1.3)
    for u in (3.0, 7.0, 11.0):
        bx(A(gi, "lamp_glow"), u - 0.7, u + 0.7, yc - 0.5, yc + 0.5, zh - 0.06, zh - 0.0)
        lamp_point(X(u), yc, zh - 0.5, watt=70.0)
    # ---- 改札: 3通路(幅0.9)・鉄パイプの支柱・木の笠・鋏・鎖/レール、改札掛のボックス
    ug0, ug1 = 8.3, 8.9
    posts = [yc - 1.35, yc - 0.45, yc + 0.45, yc + 1.35]
    for yy in posts:
        gi.a("iron_black").cyl((X(0.5 * (ug0 + ug1)), yy, 0.0), (X(0.5 * (ug0 + ug1)), yy, 1.0), 0.045, seg=10)
        bx(A(gi, "wood_dark", 0.01), ug0, ug1, yy - 0.07, yy + 0.07, 1.0, 1.12)                       # 笠木(改札鋏を置く台)
        gi.a("iron_black").cyl((X(0.5 * (ug0 + ug1)), yy, 1.12), (X(0.5 * (ug0 + ug1)), yy, 1.2), 0.012, seg=6)   # 鋏の軸
    for (ya, yb) in ((y0 + 0.3, yc - 1.4), (yc + 1.4, yc + 1.5)):                                      # 改札外柵(両側の壁まで)
        bx(A(gi, "iron_black"), ug0, ug0 + 0.06, ya, yb, 0.9, 0.96)
        bx(A(gi, "iron_black"), ug0, ug0 + 0.06, ya, yb, 0.45, 0.5)
        for yy in np.arange(ya + 0.2, yb, 0.7):
            bx(A(gi, "iron_black"), ug0, ug0 + 0.06, yy - 0.02, yy + 0.02, 0.0, 0.96)
    # 改札掛の箱(ガラス張り)
    bx(A(gi, "wood_dark", 0.01), 8.0, 9.8, yc + 1.55, yc + 2.55, 0.0, 1.0)
    bx(A(gi, "glass"), 8.0, 9.8, yc + 1.55, yc + 1.58, 1.0, 2.1)
    bx(A(gi, "glass"), 8.0, 9.8, yc + 2.52, yc + 2.55, 1.0, 2.1)
    bx(A(gi, "glass"), 8.0, 8.03, yc + 1.55, yc + 2.55, 1.0, 2.1)
    bx(A(gi, "wood_dark"), 8.0, 9.8, yc + 1.55, yc + 2.55, 2.1, 2.16)
    desk(gi, X(9.0), yc + 2.05, 0.0, w=0.8, d=0.55, face='S', papers=True)
    for yy, nmx in ((yc - 0.9, "出"), (yc, "入"), (yc + 0.9, "出")):                                   # 通路の案内灯
        bx(A(gi, "lamp_glow"), ug0 - 0.3, ug0 + 0.1, yy - 0.15, yy + 0.15, 2.25, 2.3)
        bx(A(gi, "iron_black"), ug0 - 0.3, ug0 + 0.1, yy - 0.16, yy + 0.16, 2.3, 2.42)
    # ---- 出札窓口と事務室(北側)
    ledge = A(gi, "desk", 0.01)
    for (a, b) in wins_n:
        ledge.box(a - 0.1, b + 0.1, y1 - 0.62, y1 - 0.3, 1.0, 1.05)
        A(gi, "iron_black").box(a - 0.03, b + 0.03, y1 - 0.34, y1 - 0.30, 1.05, 2.18)
        A(gi, "glass").box(a, b, y1 - 0.58, y1 - 0.55, 1.05, 2.15)
    fb = _img(sid, "fare", None) or "fare_board.png"
    cxm = X(10.8)
    face_plane(nm + "_fare", fb, 'S', cxm, y1 - 0.31, 2.3, 4.0, h=1.0)
    face_plane(nm + "_clock", "clock.png", 'S', X(6.2), y1 - 0.31, 2.4, 0.7, h=0.7)
    # 事務室(切符・金庫・電話・机)
    oy0, oy1 = y1, y1 + 3.2
    og = G(nm + "_off", "Buildings")
    oops = {"S": [(a, b, 1.05, 2.15, 'glass') for (a, b) in wins_n], st: [(oy0 + 1.6, oy0 + 2.6, 0.0, 2.3, 'open')]}
    R.shell(og, min(X(8.8), X(U)), max(X(8.8), X(U)), oy0, oy1, 0.0, zh, t=0.3, ops=oops, wall=tone)
    A(og, "concrete", 0.02).box(min(X(8.8), X(U)) - 0.35, max(X(8.8), X(U)) + 0.35, oy0 - 0.0, oy1 + 0.35, zh, zh + 0.32)
    og.build()
    og2 = G(nm + "_offin", "Props")
    A(og2, "k8_floor").box(min(X(8.8), X(U)), max(X(8.8), X(U)), oy0, oy1, -0.05, 0.02)
    desk(og2, X(10.2), oy0 + 1.0, 0.0, w=1.3, d=0.7, face='N')
    desk(og2, X(12.4), oy0 + 1.0, 0.0, w=1.3, d=0.7, face='N')
    R.shelf(og2, min(X(9.2), X(11.8)), max(X(9.2), X(11.8)), oy1 - 0.55, 0.0, h=1.9, d=0.35, rows=4, face='S', goods="jars", seed=7)
    A(og2, "iron_black", 0.02).box(X(12.8) - 0.3, X(12.8) + 0.3, oy1 - 0.65, oy1 - 0.3, 0.0, 0.8)           # 金庫
    A(og2, "iron_black").box(X(12.8) - 0.28, X(12.8) + 0.28, oy1 - 0.31, oy1 - 0.3, 0.2, 0.7)
    lamp_point(X(11.0), oy0 + 1.6, zh - 0.5, watt=50.0)
    og2.build()
    # ---- 券売機(南壁際)・運賃表・案内・ベンチ・売店
    v = ["pl_blue", "post_red", "pl_green"]
    for k, u in enumerate((9.2, 10.4, 11.6)):
        vk = v[k % 3] if v[k % 3] in M else "iron_black"
        bx(A(gi, vk, 0.02), u - 0.45, u + 0.45, y0 + 0.32, y0 + 0.8, 0.0, 1.8)
        fy = y0 + 0.8
        bx(A(gi, "white" if "white" in M else "concrete"), u - 0.38, u + 0.38, fy, fy + 0.012, 1.1, 1.65)          # 運賃表示板
        for r in range(3):
            for c in range(4):
                bx(A(gi, "iron_black"), u - 0.3 + c * 0.18, u - 0.3 + c * 0.18 + 0.12, fy, fy + 0.02, 1.15 + r * 0.14, 1.25 + r * 0.14)   # 押しボタン
        bx(A(gi, "iron_black"), u - 0.08, u + 0.08, fy, fy + 0.03, 0.95, 1.0)                                    # 硬貨投入口
        bx(A(gi, "iron_black"), u - 0.2, u + 0.2, fy, fy + 0.05, 0.62, 0.78)                                     # 切符取出口
    ad = _img(sid, "poster", None) or "poster_map.png"
    face_plane(nm + "_ad1", ad, 'N', X(3.3), y0 + 0.34, 1.2, 1.4, h=1.0)
    face_plane(nm + "_ad2", "poster_safety.png", 'N', X(5.4), y0 + 0.34, 1.2, 1.1, h=0.8)
    for ub in (2.0, 4.6):
        bx(A(gi, "wood_dark", 0.01), ub, ub + 1.8, yc - 3.6, yc - 3.2, 0.42, 0.47)
        bx(A(gi, "iron_black"), ub + 0.1, ub + 0.16, yc - 3.58, yc - 3.22, 0.0, 0.42)
        bx(A(gi, "iron_black"), ub + 1.64, ub + 1.7, yc - 3.58, yc - 3.22, 0.0, 0.42)
    # 売店(街側の入口わき)
    counter(gi, min(X(11.8), X(13.2)), max(X(11.8), X(13.2)), yc - 2.4, 0.0, d=0.6, h=1.0)
    R.shelf(gi, min(X(11.8), X(13.2)), max(X(11.8), X(13.2)), yc - 2.9, 0.0, h=1.8, d=0.35, rows=4, face='N', goods="jars", seed=3)
    # 出口表示(街側の壁の内側)
    bx(A(gi, "lamp_glow"), U - 0.45, U - 0.33, yc - 0.6, yc + 0.6, 2.75, 2.95)
    # 外の看板: 駅名(街側の上)
    nmimg = f"kit_{sid}_ekimei.png"
    xo = X(U) + sg * 0.34
    face_plane(nm + "_name", nmimg, st, xo, yc, 3.0, 4.2, h=1.1, off=0.0)
    g.build()
    gi.build()
    return nm


def concourse(g, x0, x1, y0, y1, zf, xo, c, st, rng):
    """【B6】地上駅舎の待合室(x0〜xo)に改札・券売機・出札窓口・運賃表・時計を足す。
    S壁=ホーム側の出入口(中心 x=c)。改札柵を S壁の 1.8m 内側に平行に置き、出入口の正面だけ 1.0m 開ける(改札口)。"""
    sid = st["id"]
    _mat()
    gi = G(f"k8c_{sid}", "Props")
    yg = y0 + 1.9                               # 改札柵の y
    xa, xb = x0 + 0.20, xo - 0.20
    k = A(gi, "iron_black")
    seg = [(xa, c - 0.55), (c + 0.55, xb)]
    for (a, b) in seg:
        if b - a < 0.4:
            continue
        for yy in (0.95, 0.50):                                              # 上下の横桟
            gi.a("iron_black").box(a, b, yg - 0.02, yg + 0.02, zf + yy - 0.02, zf + yy + 0.02)
        n = max(2, int((b - a) / 0.7))
        for i in range(n + 1):
            xx = a + i * (b - a) / n
            gi.a("iron_black").cyl((xx, yg, zf), (xx, yg, zf + 0.96), 0.022, 0.022, seg=8)
    for xx in (c - 0.55, c + 0.55):                                          # 改札口の太い支柱+鋏の台
        gi.a("iron_black").cyl((xx, yg, zf), (xx, yg, zf + 1.05), 0.045, 0.045, seg=10)
        gi.a("wood_dark", 0.01).box(xx - 0.09, xx + 0.09, yg - 0.09, yg + 0.09, zf + 1.05, zf + 1.13)
        gi.a("iron_black").cyl((xx, yg, zf + 1.13), (xx, yg, zf + 1.22), 0.012, 0.012, seg=6)
    # 改札掛の机と案内灯
    desk(gi, min(xb - 0.7, c + 1.3), y0 + 1.0, zf, w=0.9, d=0.55, face='N', papers=True)
    gi.a("lamp_glow").box(c - 0.4, c + 0.4, y0 + 0.5, y0 + 0.62, zf + 2.3, zf + 2.38)
    # 出札窓口: 事務室との仕切り(x=xo)の待合室側に、木枠+ガラス+鉄格子+台を付ける
    yw = (y0 + y1) / 2 + 1.7
    A(gi, "wood_dark", 0.01).box(xo - 0.16, xo - 0.06, yw - 0.75, yw + 0.75, zf + 0.95, zf + 2.05)        # 窓枠
    A(gi, "glass").box(xo - 0.09, xo - 0.075, yw - 0.65, yw + 0.65, zf + 1.05, zf + 1.95)
    for yy in np.arange(yw - 0.6, yw + 0.61, 0.15):
        A(gi, "iron_black").box(xo - 0.10, xo - 0.085, yy - 0.01, yy + 0.01, zf + 1.05, zf + 1.95)
    A(gi, "desk", 0.01).box(xo - 0.45, xo - 0.05, yw - 0.85, yw + 0.85, zf + 0.95, zf + 1.0)                # 台(ここで切符を買う)
    A(gi, "wood_dark", 0.01).box(xo - 0.42, xo - 0.08, yw - 0.8, yw + 0.8, zf, zf + 0.95)
    fb = _img(sid, "fare", None) or "fare_board.png"
    face_plane(f"k8c_{sid}_fare", fb, 'W', xo - 0.17, yw, zf + 2.1, 1.3, h=0.85)
    face_plane(f"k8c_{sid}_clock", "clock.png", 'W', xo - 0.17, yw + 1.2, zf + 2.2, 0.55, h=0.55)
    # 券売機(N壁際の東端)
    v_ = ["pl_blue", "post_red", "pl_green"]
    for kk, xx in enumerate((xo - 1.0, xo - 2.0)):
        vk = v_[(kk + rng.randrange(3)) % 3]
        vk = vk if vk in M else "iron_black"
        A(gi, vk, 0.02).box(xx - 0.4, xx + 0.4, y1 - 0.62, y1 - 0.16, zf, zf + 1.7)
        fy = y1 - 0.62
        A(gi, "white" if "white" in M else "concrete").box(xx - 0.34, xx + 0.34, fy - 0.012, fy, zf + 1.05, zf + 1.55)
        for r in range(3):
            for cc in range(4):
                A(gi, "iron_black").box(xx - 0.27 + cc * 0.17, xx - 0.27 + cc * 0.17 + 0.11, fy - 0.02, fy, zf + 1.10 + r * 0.13, zf + 1.20 + r * 0.13)
        A(gi, "iron_black").box(xx - 0.08, xx + 0.08, fy - 0.03, fy, zf + 0.92, zf + 0.97)
        A(gi, "iron_black").box(xx - 0.18, xx + 0.18, fy - 0.05, fy, zf + 0.60, zf + 0.74)
    gi.build()
