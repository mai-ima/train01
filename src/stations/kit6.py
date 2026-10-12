"""kit6: 国都電鉄/地下鉄/市電/モノレール/臨港鉄道の駅(専用ビルダー)。
ローカル座標: 線路は +x 方向、ホームは y=0 側、駅前は +y 側。線路の端点は kit4.local_tracks の既定配置に合わせる。"""
import math, random
import numpy as np
from common import *
import lib, props, rooms, core, trackkit, sig
from props import G, face_plane
from rooms import lamp_point
import kit, kit2
from kit import ST, platform
import kit_town as KT
import bpy
import kit7
import kit8

ZP = Z_PLAT


def _boards(sid):
    """駅名標など画像(kit_<駅>_ekimei.png 等)を作る。未生成の駅でも読み込めるようにする。"""
    st = ST[sid]
    names = {x["id"]: x["name"] for x in kit.NET["stations"]}
    o = kit.NET["order"].get(st["lines"][0], [])
    i = o.index(sid) if sid in o else -1
    prev = names[o[i - 1]] if i > 0 else None
    nxt = names[o[i + 1]] if 0 <= i < len(o) - 1 else None
    return kit.boards(st, prev, nxt)


def _reach(sid):
    rb, rf = kit.REACH.get(sid, (120.0, 120.0))
    return min(120.0, rb), min(120.0, rf)


def _tracks(sid, ys, z=0.0, ballast=True, bufend=False, x0=None, x1=None):
    rb, rf = _reach(sid)
    x0 = -rb if x0 is None else x0
    x1 = rf if x1 is None else x1
    for i, y in enumerate(ys):
        P = np.array([[x0, y], [x1, y]], float)
        zf = None if z == 0.0 else (lambda s, zz=z: np.full(np.shape(s), zz))
        trackkit.build_track(f"k6_{sid}_trk{i}", P, wooden=True, ballast=ballast, fittings=(i == 0), cam=None, zfun=zf)
        if bufend:
            trackkit.buffer_stop(float(x1), float(y), 0.0)


def _town(sid, rng, style, ryb, dens, rows=2, sides=("L",), skip=((-20, 20),)):
    rp = kit2.road_pts("straight", ryb)
    kit2.road_geom(rp, 5.2, name=f"k6_{sid}_road")
    kit2.town_along(rp, sid, ST[sid], rng, style, dens, list(skip), sides=sides, rows=rows)


def _ekimei(sid, x, y, z, w=5.0, face='S', name=None):
    p = f"kit_{sid}_ekimei.png"
    face_plane(name or f"k6_{sid}_ekimei", p, face, x, y, z, w, h=w / 3.0)


def _benches(g, xs, y, z):
    for x in xs:
        g.a("wood_dark").box(x - 1.0, x + 1.0, y - 0.22, y + 0.22, z + 0.42, z + 0.47)
        g.a("iron_black").box(x - 0.9, x - 0.84, y - 0.2, y + 0.2, z, z + 0.42)
        g.a("iron_black").box(x + 0.84, x + 0.9, y - 0.2, y + 0.2, z, z + 0.42)


def _vault(g, x0, x1, y0, y1, zb, rise, wall_key, rib_key="concrete", ribs=7.0):
    """かまぼこ形の天井(リブ付き)。"""
    n = 16
    arc = lambda off: [(y0 + (y1 - y0) * t / n, zb + off + rise * math.sin(math.pi * t / n)) for t in range(n + 1)]
    outer, inner = arc(0.0), arc(-0.45)
    g.a(wall_key).extrude_x(outer + inner[::-1], x0, x1)
    for xr in np.arange(x0 + 2.0, x1, ribs):
        g.a(rib_key, bevel=0.01).extrude_x(outer + [(y1, zb - 0.1 + 0.0), (y0, zb - 0.1)][::-1] if False else outer + inner[::-1], xr - 0.25, xr + 0.25)


# ----------------------------------------------------------------- 地下鉄・地下駅 (T02/T03/K02): 地上は街区の下に覆われた駅

def _slab(g, x0, x1, y0, y1, za, zb, holes):
    """長方形スラブから軸平行の穴(x0,x1,y0,y1)を抜いて作る。"""
    xs = sorted(set([x0, x1] + [h[0][0] for h in holes] + [h[0][1] for h in holes]))
    for xa_, xb_ in zip(xs[:-1], xs[1:]):
        xm = (xa_ + xb_) / 2
        hs = sorted([(h[1], h[2]) for h in holes if h[0][0] < xm < h[0][1]])
        y = y0
        for (ha, hb) in hs:
            if ha > y:
                g.a("concrete", bevel=0.02).box(xa_, xb_, y, ha, za, zb)
            y = max(y, hb)
        if y < y1:
            g.a("concrete", bevel=0.02).box(xa_, xb_, y, y1, za, zb)


def _solid_stair(g, sg, yc, width=2.4):
    """ホーム端から地上へ上がる直線階段(蹴上げは詰まった中実)。ホーム面 ZP → 地表 UG_DEPTH(ホール局所座標)。"""
    D = UG_DEPTH
    n = int(math.ceil((D - ZP) / 0.18))
    dz = (D - ZP) / n
    x_from = sg * (39.4 - n * 0.28)        # 最上段が地表(穴の縁 x=39.4)にちょうど届く
    for k in range(n):
        xa_ = x_from + sg * k * 0.28
        xb_ = x_from + sg * (k + 1) * 0.28
        zt_ = ZP + (k + 1) * dz
        g.a("concrete", bevel=0.004).box(min(xa_, xb_), max(xa_, xb_), yc - width / 2, yc + width / 2, ZP - 0.05, zt_)
    xe = x_from + sg * n * 0.28
    for s in (-1, 1):
        g.a("concrete", bevel=0.01).sbox((x_from, yc + s * (width / 2 + 0.1), ZP + 0.45), (xe, yc + s * (width / 2 + 0.1), D + 0.45), 0.2, 0.9)   # 腰壁
        g.a("iron_black").sbox((x_from, yc + s * (width / 2 + 0.1), ZP + 1.2), (xe, yc + s * (width / 2 + 0.1), D + 1.2), 0.05, 0.05)   # 手すり
    return xe


def _tunnel_ext(g, sid, xa, xb, ylo, yhi, zt):
    """ホールの外側(±52m〜ゾーン端)の箱形トンネル。"""
    rb, rf = _reach(sid)
    for (x0, x1) in ((xb, rf), (-rb, xa)):
        if x1 - x0 < 1.0:
            continue
        for yw in (ylo - 0.4, yhi):
            g.a("concrete", bevel=0.01).box(x0, x1, yw, yw + 0.4, -0.5, zt)
        g.a("concrete", bevel=0.02).box(x0, x1, ylo - 0.4, yhi + 0.4, zt, zt + 0.5)
        g.a("concrete", bevel=0.0).box(x0, x1, ylo, yhi, -0.55, 0.0)


def _ug_surface(sid, stairs, ylo, yhi, xa, xb):
    """地上: 地下への出入口の上屋、舗装の広場、地面の切り欠き(階段室)。ゾーン局所座標(地表 z=0)。"""
    g = G(f"k6_{sid}_ug_surf", "Buildings")
    holes = []
    for k, (yc, sg) in enumerate(stairs):
        hx = (33.5, 39.4) if sg > 0 else (-39.4, -33.5)
        kit7.shaft_cut(hx[0] - 0.05, hx[1] + 0.05, yc - 1.5, yc + 1.5, name=f"k6_{sid}_shaft{k}")
        holes.append((hx, yc - 1.5, yc + 1.5))
        kit8.ticket_hall(sid, 32.6 * sg, sg, yc)
    g.build()
    # 広場の舗装(階段室の穴を残す)
    gp = G(f"k6_{sid}_plaza", "Roads")
    _slab_mat(gp, xa - 6, xb + 6, ylo - 5, yhi + 3, -0.08, 0.0, holes)
    gp.build()


def _slab_mat(g, x0, x1, y0, y1, za, zb, holes):
    xs = sorted(set([x0, x1] + [h[0][0] for h in holes] + [h[0][1] for h in holes]))
    for xa_, xb_ in zip(xs[:-1], xs[1:]):
        xm = (xa_ + xb_) / 2
        hs = sorted([(h[1], h[2]) for h in holes if h[0][0] < xm < h[0][1]])
        y = y0
        for (ha, hb) in hs:
            if ha > y:
                g.a("paving" if "paving" in M else "concrete").box(xa_, xb_, y, ha, za, zb)
            y = max(y, hb)
        if y < y1:
            g.a("paving" if "paving" in M else "concrete").box(xa_, xb_, y, y1, za, zb)


def underground_hall(sid, rng, island=True, theme="tile", wall="plasterw", stripe="pl_blue", over="arcade", ys=None):
    kit7.mats5()
    kit.ground(L=600, W=600)
    _b0 = set(bpy.data.objects.keys())
    D = UG_DEPTH
    if ys is None:
        ys = [0.0, -8.4] if island else [0.0, -4.6]
    _tracks(sid, ys, ballast=False)
    g = G(f"k6_{sid}_hall", "Station")
    xa, xb = -52.0, 52.0
    ylo, yhi = (ys[-1] - 4.0), 4.0
    zt = 6.4
    # 側壁(タイル)と天井、両端は線路の坑口
    for yw, sgn in ((ylo - 0.4, 1), (yhi, 1)):
        g.a("ug_tile").box(xa, xb, yw, yw + 0.4, 0.0, 2.4)                      # 腰高のタイル壁
        g.a("ug_plaster").box(xa, xb, yw, yw + 0.4, 2.4, zt)                     # 上部は躯体
        g.a(stripe if stripe in M else "concrete").box(xa, xb, yw + (0.4 if yw == ylo - 0.4 else -0.02), yw + (0.42 if yw == ylo - 0.4 else 0.0) + 0.02, 1.0, 1.5)
    # 階段の位置(ホームの両端から地上へ)。屋根スラブは階段の通る穴を残して作る
    if island:
        stairs = [(-4.2, +1), (-4.2, -1)]
    else:
        stairs = [(2.65, +1), (2.65, -1), (ys[-1] - 2.65, +1), (ys[-1] - 2.65, -1)]
    holes = [((33.5, 39.4) if sg > 0 else (-39.4, -33.5), yc - 1.5, yc + 1.5) for (yc, sg) in stairs]
    _slab(g, xa, xb, ylo - 0.4, yhi + 0.4, zt, zt + 0.5, holes)
    for xe in (xa, xb):                          # 坑口の袖壁(線路の通る穴を残す)
        for (y0_, y1_) in ((ylo - 0.4, ylo + 1.0), (yhi - 1.0, yhi + 0.4)):
            g.a("concrete", bevel=0.01).box(xe - 0.3, xe + 0.3, y0_, y1_, 0.0, zt)
        mid = (ys[0] + ys[-1]) / 2
        g.a("concrete", bevel=0.01).box(xe - 0.3, xe + 0.3, ylo + 1.0, yhi - 1.0, zt - 1.0, zt)
    g.a("ug_conc", bevel=0.0).box(xa, xb, ylo, yhi, -0.4, 0.03)       # 路盤の床(地面の草が見えないように)
    # ホーム
    if island:
        platform(xa + 2, xb - 2, -6.7, -1.7, name=f"k6_{sid}_plat")
        pcs = [-4.2]
    else:
        platform(xa + 2, xb - 2, 1.7, 4.0, name=f"k6_{sid}_platA") if False else None
        platform(xa + 2, xb - 2, 1.7, 3.6, name=f"k6_{sid}_platA")
        platform(xa + 2, xb - 2, ys[-1] - 3.6, ys[-1] - 1.7, name=f"k6_{sid}_platB")
        pcs = [2.7, ys[-1] - 2.7]
    for (yc, sg) in stairs:
        _solid_stair(g, sg, yc)
    _tunnel_ext(g, sid, xa, xb, ylo, yhi, zt)
    # 柱・照明・ベンチ・案内
    gp = G(f"k6_{sid}_fit", "Props")
    for yc in pcs:
        for x in np.arange(xa + 6, xb - 4, 6.5):
            gp.a("ug_conc", bevel=0.03).box(x - 0.35, x + 0.35, yc - 0.35, yc + 0.35, 0.0, zt)
            gp.a("ug_tile").box(x - 0.37, x + 0.37, yc - 0.37, yc + 0.37, 0.0, 1.9)
            gp.a("lamp_glow").box(x - 0.6, x + 0.6, yc - 0.06, yc + 0.06, zt - 0.5, zt - 0.35)
        _benches(gp, np.arange(xa + 9, xb - 8, 13.0), yc + (1.2 if island else 0.0), ZP)
    # 蛍光灯の列
    for yl in (ys[0] - 2.2, ys[-1] + 2.2) if island else (ys[0] + 2.0, ys[-1] - 2.0):
        for x in np.arange(xa + 3, xb - 2, 2.2):
            gp.a("lamp_glow").box(x - 0.45, x + 0.45, yl - 0.05, yl + 0.05, zt - 0.08, zt - 0.02)
    gp.build()
    g.build()
    for x in np.arange(xa + 8, xb - 6, 6.0):                 # 構内照明(ホーム上と線路上)
        for yc in sorted(set([ (ys[0]+ys[-1])/2 ] + pcs)):
            lamp_point(float(x), float(yc), zt - 0.7, watt=150.0)
    for x in (-34, 0, 34):
        lamp_point(x, (ylo + yhi) / 2, zt - 0.7, watt=120.0)
    for x in (-24, 24):
        _ekimei(sid, x, yhi - 0.4 + 0.0, 3.0, w=4.2, face='S', name=f"k6_{sid}_nm{x}")
    # ---- ここまで(ホール・線路・ホーム・照明・駅名標)を地下 D m へ下げる
    for nm in set(bpy.data.objects.keys()) - _b0:
        bpy.data.objects[nm].location.z -= D
    # 地上: 出入口(階段室の上屋)・広場・切り欠き
    _ug_surface(sid, stairs, ylo, yhi, xa, xb)
    # 地上: 換気塔・上の街区
    gs = G(f"k6_{sid}_surf", "Buildings")
    cx = 0.0
    if over == "arcade":                          # 商店街アーケードを抱える2階建て街区
        gs.a("brick", bevel=0.02).box(xa - 4, xb + 4, yhi + 0.6, yhi + 15.0, 0.0, 8.0) if False else None
        for sx in (-1, 1):
            gs.a("plasterw", bevel=0.02).box(sx * 22 - 8, sx * 22 + 8, yhi + 2.0, yhi + 12.0, 0.0, zt + 6.5)
            Hb = zt + 6.5
            for zz in (5.2, 8.6, 12.0):                              # 3階分の窓(木枠+ガラス)
                for xx in np.arange(sx * 22 - 6.8, sx * 22 + 7.0, 2.6):
                    gs.a("wood_dark").box(xx - 0.75, xx + 0.75, yhi + 1.93, yhi + 2.0, zz, zz + 1.6)
                    gs.a("glass").box(xx - 0.65, xx + 0.65, yhi + 1.91, yhi + 1.95, zz + 0.1, zz + 1.5)
            gs.a("concrete", bevel=0.02).box(sx * 22 - 8.3, sx * 22 + 8.3, yhi + 1.7, yhi + 12.3, Hb, Hb + 0.5)    # パラペット笠木
            gs.a(["post_red", "pl_green"][(sx + 1) // 2] if ["post_red", "pl_green"][(sx + 1) // 2] in M else "tin").box(sx * 22 - 8.2, sx * 22 + 8.2, yhi + 1.0, yhi + 2.4, 3.4, 3.6)   # 1階の庇
        gs.a("tin").box(-60, 60, yhi + 1.0, yhi + 9.0, 4.5, 4.7)
    elif over == "civic":
        gs.a("stone", bevel=0.02).box(-30, 30, yhi + 3.0, yhi + 18.0, 0.0, zt + 12.0)
        for i in range(8):
            gs.a("stone", bevel=0.02).box(-26 + i * 7.4 - 0.5, -26 + i * 7.4 + 0.5, yhi + 1.8, yhi + 2.8, 0.0, zt + 11.0)
        for zz in (3.0, 8.2, 13.4):                                  # 柱間の縦長窓(3段)
            for i in range(7):
                xx = -22.6 + i * 7.4
                gs.a("dark_glass").box(xx - 1.3, xx + 1.3, yhi + 2.96, yhi + 3.02, zz, zz + 3.6)
                gs.a("stone", bevel=0.01).box(xx - 1.5, xx + 1.5, yhi + 2.9, yhi + 3.0, zz + 3.6, zz + 3.9)
        gs.a("stone", bevel=0.02).box(-8, 8, yhi + 1.4, yhi + 3.2, 0.0, 4.2)                                      # 正面玄関の車寄せ
        gs.a("dark_glass").box(-3.0, 3.0, yhi + 1.38, yhi + 1.42, 0.0, 3.4)
        gs.a("stone", bevel=0.02).box(-31, 31, yhi + 1.5, yhi + 19.0, zt + 12.0, zt + 12.8)
        gs.a("copper" if "copper" in M else "tin").extrude_x([(yhi + 3.0, zt + 12.8), (yhi + 10.5, zt + 17.0), (yhi + 18.0, zt + 12.8)], -22, 22)
    else:                                         # office
        for k, (sx, h) in enumerate(((-30, 28), (6, 38), (38, 22))):
            gs.a("concrete", bevel=0.02).box(sx - 12, sx + 12, yhi + 3.0, yhi + 17.0, 0.0, zt + h)
            Ht = zt + h
            x0_, x1_, y0_, y1_ = sx - 12, sx + 12, yhi + 3.0, yhi + 17.0
            for z0_ in np.arange(3.2, Ht - 2.4, 3.6):            # 各階の連続窓(ガラス帯)と層間の腰壁
                gs.a("dark_glass" if (k + int(z0_ / 3.6)) % 5 else "glass").box(x0_ + 0.5, x1_ - 0.5, y0_ - 0.04, y0_ + 0.01, z0_, z0_ + 1.9)
                gs.a("dark_glass").box(x0_ - 0.04, x0_ + 0.01, y0_ + 0.5, y1_ - 0.5, z0_, z0_ + 1.9)
                gs.a("dark_glass").box(x1_ - 0.01, x1_ + 0.04, y0_ + 0.5, y1_ - 0.5, z0_, z0_ + 1.9)
            for xx_ in np.arange(x0_ + 0.5, x1_ - 0.4, 3.0):      # 縦の方立
                gs.a("concrete").box(xx_ - 0.12, xx_ + 0.12, y0_ - 0.2, y0_, 0.0, Ht)
            gs.a("concrete", bevel=0.02).box(x0_ - 0.3, x1_ + 0.3, y0_ - 0.3, y1_ + 0.3, Ht, Ht + 0.6)          # 屋上の笠木
            gs.a("iron_black").box(sx - 4, sx + 3, y0_ + 4, y0_ + 9, Ht + 0.6, Ht + 3.4)                               # 屋上機械室
            gs.a("iron_black").cyl((sx + 8, y1_ - 3, Ht + 0.6), (sx + 8, y1_ - 3, Ht + 7.0), 0.08, seg=6)       # アンテナ
    # 駅ビルの店舗列(ひさしの色を変える)
    for i, x in enumerate(np.arange(xa + 3, xb - 2, 6.0)):
        col = ["pl_blue", "post_red", "pl_green", "pl_cream", "pl_ochre"][i % 5]
        gs.a("wood_dark", bevel=0.01).box(x, x + 5.4, yhi + 0.4, yhi + 1.6, 0.0, 3.2)
        gs.a(col if col in M else "tin").box(x - 0.1, x + 5.5, yhi + 1.0, yhi + 2.6, 3.2, 3.4)
        gs.a("glass").box(x + 0.4, x + 5.0, yhi + 1.58, yhi + 1.62, 0.5, 2.6)
    gs.build()
    _town(sid, rng, "urban" if over != "civic" else "suburb", yhi + 36.0, 0.75)
    kit.ground  # keep import usage
    return ys


def t02():
    rng = random.Random(402)
    underground_hall("T02", rng, island=True, wall="plasterw", stripe="pl_blue", over="arcade")


def t03():
    rng = random.Random(403)
    underground_hall("T03", rng, island=True, wall="stone", stripe="post_red", over="civic")


def k02():
    rng = random.Random(502)
    underground_hall("K02", rng, island=False, wall="concrete", stripe="pl_green", over="office", ys=[0.0, -4.6, -9.2, -13.8])   # 両側ホーム+中央2線の通過線(4線)


# ----------------------------------------------------------------- T04 国都西: 地上に出る終点 (切通し+ポータル)
def t04():
    sid = "T04"
    rng = random.Random(404)
    kit.ground(L=600, W=600)
    ys = [0.0, -4.6]
    _tracks(sid, ys, ballast=True, bufend=True, x1=60.0)
    platform(-45, 55, 1.7, 3.8, name="k6_T04_platA")
    platform(-45, 55, -4.6 - 3.8, -4.6 - 1.7, name="k6_T04_platB")
    g = G("k6_T04_cut", "Station")
    # 切通しの擁壁(コンクリ)+ポータル
    g.a("concrete", bevel=0.02).box(-120, -20, 6.0, 6.6, -0.3, 4.2)
    g.a("concrete", bevel=0.02).box(-120, -20, -12.2, -11.6, -0.3, 4.2)
    for x in np.arange(-118, -20, 12.0):
        g.a("concrete", bevel=0.02).box(x - 0.4, x + 0.4, 6.6, 7.4, -0.3, 4.2)
        g.a("concrete", bevel=0.02).box(x - 0.4, x + 0.4, -12.8, -12.2, -0.3, 4.2)
    # 駅舎: RCの低層(改札・売店・自転車置場)+大庇
    g.a("concrete", bevel=0.02).box(-15, 25, 10.0, 22.0, 0.0, 4.4)
    g.a("glass").box(-14.8, 24.8, 9.98, 10.02, 0.4, 3.4)
    g.a("concrete", bevel=0.02).box(-17, 27, 6.0, 22.5, 4.4, 4.8)
    for x in (-14, -4, 6, 16, 26):
        g.a("iron_black").cyl((x, 6.4, 0), (x, 6.4, 4.4), 0.14, seg=8)
    # ホーム上屋
    for (yc, ya, yb) in ((2.8, 1.7, 4.0), (-7.4, -8.6, -6.3)):
        for x in np.arange(-40, 50, 8.0):
            g.a("iron_black").cyl((x, yc, ZP), (x, yc, ZP + 3.6), 0.08, seg=8)
        g.a("tin").box(-42, 52, ya - 0.5, yb + 0.5, ZP + 3.6, ZP + 3.72)
    g.build()
    # 連絡橋(ホーム間)
    gb = G("k6_T04_fb", "Station")
    gb.a("iron_black").box(30, 31.6, -8.6, 4.0, 5.0, 5.15)
    for yy in (-8.6, 4.0):
        gb.a("iron_black").box(30, 31.6, yy - 0.15, yy + 0.15, ZP, 5.0)
    gb.build()
    _ekimei(sid, 5.0, 9.9, 3.2, w=6.0, name="k6_T04_nm")
    sig.KINDS["sigtower"](-60, 14, name="k6_T04_sig")
    _town(sid, rng, "urban", 32.0, 0.6)


# ----------------------------------------------------------------- K03 港町: 高架駅 (線路高さ 7.5m)
def k03():
    sid = "K03"
    rng = random.Random(503)
    kit.ground(L=600, W=600)
    Z = 7.5
    ys = [0.0, -8.4, -13.0]      # 島式1面2線+折返し線1本
    YB = ys[-1] - 2.8
    _tracks(sid, ys, z=Z, ballast=True)
    g = G("k6_K03_via", "Station")
    xa, xb = -70.0, 70.0
    # RC高架: 柱列+桁
    for x in np.arange(xa, xb + 1, 10.0):
        for yy in (YB + 0.8, 2.0):
            g.a("concrete", bevel=0.03).box(x - 0.6, x + 0.6, yy - 0.6, yy + 0.6, -0.2, Z - 0.9)
        g.a("concrete", bevel=0.02).box(x - 0.45, x + 0.45, YB + 0.2, 2.6, Z - 1.2, Z - 0.6)
    for (xa_, xb_) in ((xa, -15.2), (-9.7, xb)):
        g.a("concrete", bevel=0.02).box(xa_, xb_, YB, 2.8, Z - 0.9, Z - 0.35)
    for (ya_, yb_) in ((YB, -6.0), (-2.4, 2.8)):
        g.a("concrete", bevel=0.02).box(-15.2, -9.7, ya_, yb_, Z - 0.9, Z - 0.35)
    g.a("concrete", bevel=0.02).box(xa, xb, 2.2, 2.9, Z - 0.35, Z + 1.1)           # 手すり壁
    g.a("concrete", bevel=0.02).box(xa, xb, YB - 0.1, YB + 0.6, Z - 0.35, Z + 1.1)
    # 島式ホーム(高架上)
    for (xa_, xb_) in ((-55, -15.2), (-9.7, 55)):
        g.a("concrete", bevel=0.01).box(xa_, xb_, -6.7, -1.7, Z - 0.35, Z + 0.5)
        g.a("plat_top").box(max(xa_, -54.9), min(xb_, 54.9), -6.6, -1.8, Z + 0.5, Z + 0.54)
    for (ya_, yb_) in ((-6.7, -6.0), (-2.4, -1.7)):
        g.a("concrete", bevel=0.01).box(-15.2, -9.7, ya_, yb_, Z - 0.35, Z + 0.5)
    # 上屋(鉄骨・波板)
    for x in np.arange(-50, 51, 8.0):
        g.a("iron_black").cyl((x, -2.4, Z + 0.5), (x, -2.4, Z + 4.3), 0.1, seg=8)
        g.a("iron_black").cyl((x, -6.0, Z + 0.5), (x, -6.0, Z + 4.3), 0.1, seg=8)
        g.a("iron_black").box(x - 0.07, x + 0.07, -6.4, -2.0, Z + 4.3, Z + 4.45)
    g.a("tin").box(-52, 52, -6.6, -1.8, Z + 4.45, Z + 4.55)
    # 駅舎(高架下の1階・コンコース): 中空の躯体(開口・窓・床)。ホームへ上がる直線階段は室内を x 方向に走り、
    # ホーム床と桁スラブの穴(x -15.2〜-9.7, y -6.0〜-2.4)から上に出る。
    import rooms as _R
    zc = Z - 0.9                                                    # 桁下端=コンコース天井
    ops = {"N": [(xx - 1.6, xx + 1.6, 0.5, 3.8, 'glass') for xx in (-21, -14, 14, 21)] + [(-2.0, 2.0, 0.0, 2.6, 'open')],
           "S": [(xx - 1.4, xx + 1.4, 0.8, 3.4, 'glass') for xx in (-18, 18)],
           "W": [(-6.0, -3.6, 0.0, 2.5, 'open')], "E": [(-6.0, -3.6, 0.0, 2.5, 'open')]}
    kit7.mats5()
    _R.shell(g, -24, 24, -9.8, 1.4, 0.0, zc, t=0.3, ops=ops, wall="ug_plaster")
    g.a("ug_floor").box(-23.7, 23.7, -9.5, 1.1, -0.02, 0.02)
    # 階段(室内): -22 → -9.7 で z 0.02 → Z+0.5
    _R.stair_run(g, 'x', -22.0, -9.7, -4.2, 0.02, Z + 0.5, width=1.6, rise=0.18)
    # 内部の改札・案内・照明
    g.a("iron_black").box(-8.0, -7.9, -9.0, -5.0, 0.02, 1.1)
    # 改札(階段下): 2通路・鉄パイプの支柱・木の笠・外柵、券売機、出札窓口、売店
    for yy in (-5.0, -4.2, -3.4):
        g.a("iron_black").cyl((-21.5, yy, 0.02), (-21.5, yy, 1.0), 0.045, seg=10)
        g.a("wood_dark", bevel=0.01).box(-21.8, -21.2, yy - 0.07, yy + 0.07, 1.0, 1.12)
    for (ya, yb) in ((-9.5, -5.05), (-3.35, 1.1)):
        g.a("iron_black").box(-21.55, -21.45, ya, yb, 0.9, 0.96)
        g.a("iron_black").box(-21.55, -21.45, ya, yb, 0.45, 0.5)
        for yy in np.arange(ya + 0.2, yb, 0.7):
            g.a("iron_black").box(-21.54, -21.46, yy - 0.02, yy + 0.02, 0.02, 0.96)
    for k, xx in enumerate((-20.0, -18.9, -17.8)):          # 券売機
        vk = ("pl_blue", "post_red", "pl_green")[k]
        g.a(vk if vk in M else "iron_black", bevel=0.02).box(xx - 0.45, xx + 0.45, -9.5, -9.0, 0.02, 1.8)
        g.a("iron_black").box(xx - 0.3, xx + 0.3, -9.0, -8.98, 1.1, 1.65)
        g.a("iron_black").box(xx - 0.2, xx + 0.2, -9.0, -8.95, 0.62, 0.78)
    g.a("wood_dark", bevel=0.01).box(-14.0, -10.0, 0.0, 0.7, 0.02, 1.0)                 # 出札窓口のカウンター
    g.a("iron_black").box(-14.0, -10.0, 0.0, 0.05, 1.0, 2.2)
    g.a("wood_dark").box(1.0, 5.0, -9.4, -8.6, 0.02, 1.05)                          # 売店
    g.a("pl_cream" if "pl_cream" in M else "plasterw").box(0.8, 5.2, -9.5, -8.4, 2.15, 2.3)
    for x in (-20, -12, -4, 4, 12, 20):
        for yy in (-7.0, -2.0):
            lamp_point(x, yy, zc - 0.5, watt=260.0)
            g.a("lamp_glow").box(x - 0.6, x + 0.6, yy - 0.1, yy + 0.1, zc - 0.12, zc - 0.04)
    g.a("concrete", bevel=0.02).box(-26, 26, 1.0, 5.0, 4.6, 5.0)
    g.build()
    # 高架下の店舗(柱間のスパンごとに間口・シャッター・庇・看板を変える)
    gsh = G("k6_K03_shops", "Buildings")
    tones = ["pl_blue", "post_red", "pl_green", "pl_cream", "wood_dark"]
    rs = random.Random(31)
    for xs_ in list(np.arange(-70, -30, 10.0)) + list(np.arange(30, 70, 10.0)):
        k = rs.randrange(5)
        dep = rs.choice([4.5, 5.5, 6.5])
        gsh.a("concrete", bevel=0.02).box(xs_ + 0.6, xs_ + 0.8, 2.0 - dep, 2.0, 0.0, zc)            # 間仕切り
        gsh.a("concrete", bevel=0.02).box(xs_ + 0.6, xs_ + 10.6 - 0.6, 2.0 - dep - 0.2, 2.0 - dep, 0.0, zc)      # 奥壁
        tn = tones[k] if tones[k] in M else "iron_black"
        gsh.a(tn, bevel=0.02).box(xs_ + 0.9, xs_ + 9.5, 2.1, 2.4, 3.55, 4.3)                           # 看板(間口)
        gsh.a("tin").box(xs_ + 0.8, xs_ + 9.6, 2.1, 3.5, 3.4, 3.5)                                    # 庇
        if k % 2 == 0:
            gsh.a("iron_black").box(xs_ + 1.0, xs_ + 9.4, 2.15, 2.3, 0.2, 3.2)                        # シャッター
            for zz in np.arange(0.4, 3.2, 0.18):
                gsh.a("k5_steel" if "k5_steel" in M else "iron_black").box(xs_ + 1.0, xs_ + 9.4, 2.3, 2.33, zz, zz + 0.04)
        else:
            gsh.a("glass").box(xs_ + 1.0, xs_ + 9.4, 2.15, 2.2, 0.9, 3.2)                              # ショーウインドウ
            gsh.a("wood_dark").box(xs_ + 1.5, xs_ + 8.5, 2.0 - dep + 0.6, 2.0 - dep + 1.0, 0.0, 1.8)    # 棚
            gsh.a("wood_dark").box(xs_ + 2.0, xs_ + 8.0, 1.0, 1.6, 0.0, 0.95)                          # カウンター
        lamp_point(xs_ + 5.0, 3.2, 3.2, watt=220.0)                                                   # 店先の明かり
        gsh.a("lamp_glow").box(xs_ + 1.5, xs_ + 8.5, 2.9, 3.0, 3.36, 3.4)
    gsh.build()
    gp = G("k6_K03_fit", "Props")
    for yc in (-4.2,):
        _benches(gp, np.arange(-40, 41, 12.0), yc, Z + 0.54)
        for x in np.arange(-44, 45, 8.0):
            gp.a("lamp_glow").box(x - 0.4, x + 0.4, yc - 0.05, yc + 0.05, Z + 4.28, Z + 4.34)
    gp.build()
    _ekimei(sid, 0.0, -9.85, 3.0, w=6.4, face='S', name="k6_K03_nm")
    face_plane("k6_K03_nm2", f"kit_{sid}_ekimei.png", 'S', 0.0, -6.7, Z + 1.6, 3.6, h=1.2) if False else None
    for x in (-30, 0, 30):
        lamp_point(x, -4.2, Z + 3.6, watt=60.0)
    gsig = G("k6_K03_sig", "Props")
    gsig.build()
    _town(sid, rng, "urban", 22.0, 0.85, rows=3, sides=("L", "R"))


# ----------------------------------------------------------------- TR02 大湊市場前: 路面電車の停留場+市場
def tr02():
    sid = "TR02"
    rng = random.Random(602)
    kit.ground(L=600, W=600)
    rb, rf = _reach(sid)
    # 道路に埋め込まれた軌道(舗装・バラストなし)と電車線柱
    kit7.mats5()
    M["asphalt"] = M["ug_asph"]
    M["paving"] = M["ug_paving"]
    core.ribbon("k6_TR02_street", [(x, 2.4) for x in np.arange(-rb - 10, rf + 11, 6.0)], 15.0, M["asphalt"], z0=0.243, rut=False, col="Roads")
    for sgn in (-1, 1):   # 歩道と縁石
        core.ribbon(f"k6_TR02_walk{sgn}", [(x, 2.4 + sgn * 9.5) for x in np.arange(-rb - 10, rf + 11, 6.0)], 3.0, M["ug_paving"], z0=0.33, rut=False, col="Roads")
    _tracks(sid, [0.0, 4.8], ballast=False, x0=-rb, x1=rf)     # 上下2線(島式の安全地帯を挟む)
    for _y in (0.0, 4.8):
        kit7.tram_bed([(x, _y) for x in np.arange(-rb, rf + 1, 4.0)], f'k6_TR02_bed{int(_y)}')
    g = G("k6_TR02_stop", "Station")
    g.a("concrete", bevel=0.02).box(-8, 12, 1.6, 3.2, -0.05, 0.28)          # 安全地帯(島)
    g.a("plat_top").box(-7.9, 11.9, 1.7, 3.1, 0.28, 0.31)
    for x in (-5, 9):
        g.a("iron_black").cyl((x, 2.4, 0.3), (x, 2.4, 3.0), 0.06, seg=8)
    g.a("glass").box(-5, 9, 2.0, 2.05, 0.9, 2.7)
    g.a("tin").box(-5.6, 9.6, 1.7, 3.1, 3.0, 3.1)
    g.build()
    # 市場: 大屋根の公設市場(柱+波板屋根)と屋台
    gm = G("k6_TR02_market", "Buildings")
    for ix in range(7):
        for iy in range(3):
            x, y = -26 + ix * 9.0, 20 + iy * 9.0
            gm.a("iron_black").cyl((x, y, 0), (x, y, 4.2), 0.12, seg=8)
    gm.a("tin").box(-28, 36, 18.0, 46.0, 4.2, 4.35)
    gm.a("tin").extrude_x([(18.0, 4.35), (32.0, 6.0), (46.0, 4.35)], -28, 36)
    for ix in range(12):
        x = -24 + ix * 5.0
        gm.a("wood_dark").box(x - 1.4, x + 1.4, 22.0, 23.2, 0.0, 0.9)
        gm.a(["pl_blue", "post_red", "pl_green", "pl_cream"][ix % 4] if ["pl_blue", "post_red", "pl_green", "pl_cream"][ix % 4] in M else "tin").box(x - 1.6, x + 1.6, 21.6, 23.4, 2.3, 2.45)
        for k in range(4):
            gm.a("sack" if "sack" in M else "straw").box(x - 1.2 + k * 0.7, x - 0.7 + k * 0.7, 22.1, 22.9, 0.9, 1.25)
    gm.build()
    face_plane("k6_TR02_nm", f"kit_{sid}_ekimei.png", 'S', 2.0, 2.4, 1.0, 2.0, h=0.8)
    face_plane("k6_TR02_nm_b", f"kit_{sid}_ekimei.png", 'N', 2.0, 2.52, 1.0, 2.0, h=0.8)   # 両面の駅名標(裏から見て鏡文字にならない)
    gpst = G("k6_TR02_signposts", "Props")
    for xx in (1.1, 2.9):
        gpst.a("iron_black").cyl((xx, 2.46, 0.3), (xx, 2.46, 1.85), 0.045, seg=8)
    gpst.a("iron_black").box(1.0, 3.0, 2.40, 2.52, 1.78, 1.84)
    gpst.build()
    face_plane("k6_TR02_mk", f"kit_{sid}_facade.png", 'S', 4.0, 18.05, 4.3, 12.0, h=2.0)
    # 架線(電車線)柱
    gp = G("k6_TR02_poles", "Props")
    for x in np.arange(-rb + 8, rf, 28.0):
        gp.a("iron_black").cyl((x, -3.6, 0), (x, -3.6, 6.8), 0.1, seg=8)
        gp.a("iron_black").sbox((x, -3.6, 6.4), (x, 0.0, 6.0), 0.05, 0.05)
    gp.a("iron_black").sbox((-rb, 0.0, 5.8), (rf, 0.0, 5.8), 0.02, 0.02)
    gp.build()
    # 横断歩道(ゼブラ)と歩行者用信号
    gz = G("k6_TR02_xwalk", "Props")
    wk = "white" if "white" in M else "plasterw"
    for xc in (-16.0, 40.0):
        for k in range(17):
            yy = -4.6 + k * 0.92
            gz.a(wk).box(xc - 1.6, xc + 1.6, yy, yy + 0.46, 0.2435, 0.2475)
        for sgn in (-1, 1):
            px, py = xc + 2.4, (-6.2 if sgn < 0 else 11.4)
            gz.a("iron_black").cyl((px, py, 0.33), (px, py, 3.2), 0.06, seg=8)
            gz.a("iron_black").box(px - 0.18, px + 0.18, py - 0.12, py + 0.12, 2.5, 3.1)
            for kk, mk in enumerate(("post_red" if "post_red" in M else "iron_black", "lamp_glow", "pl_green" if "pl_green" in M else "iron_black")):
                gz.a(mk).cyl((px, py - 0.13 * (1 if sgn > 0 else -1), 2.95 - kk * 0.2), (px, py - 0.15 * (1 if sgn > 0 else -1), 2.95 - kk * 0.2), 0.07, seg=10)
    gz.build()
    _town(sid, rng, "urban", 52.0, 0.9, rows=2, sides=("L",), skip=((-30, 38),))
    _town(sid, rng, "urban", -26.0, 0.95, rows=1, sides=("L",), skip=())
    _town_s(sid, rng)


def _town_s(sid, rng):
    kit2.town_along(kit2.road_pts("straight", -28.0), sid, ST[sid], rng, "urban", 0.8, [(-20, 20)], sides=("R",), rows=2)


# ----------------------------------------------------------------- B02 湾岸公園: 高架モノレール終着駅 (軌道高 9m)
def b02():
    sid = "B02"
    kit7.mats5()
    rng = random.Random(702)
    kit.ground(L=600, W=600)
    Z = 9.0
    rb, rf = _reach(sid)
    ys = [0.0, -4.6]
    g = G("k6_B02_beam", "Station")
    for y in ys:
        # PC軌道桁(幅0.85×高1.5)
        g.a("concrete").extrude_x([(y - 0.45, Z), (y + 0.45, Z), (y + 0.45, Z - 1.25), (y + 0.30, Z - 1.5), (y - 0.30, Z - 1.5), (y - 0.45, Z - 1.25)], -rb, rf)   # 面取りのPC桁
        sgw = 1 if y >= -0.1 else -1                                                    # 外側の避難用点検歩廊(格子床+手摺)
        yw0, yw1 = y + sgw * 0.50, y + sgw * 1.05
        g.a("k5_steel").box(-rb, rf, min(yw0, yw1), max(yw0, yw1), Z - 0.95, Z - 0.90)
        for x in np.arange(-rb + 1.5, rf, 3.0):
            g.a("iron_black").box(x - 0.03, x + 0.03, y + sgw * 0.45 - 0.02, y + sgw * 1.04 + 0.02, Z - 1.1, Z - 0.95)
            g.a("iron_black").box(x - 0.025, x + 0.025, y + sgw * 1.03 - 0.025, y + sgw * 1.03 + 0.025, Z - 0.90, Z + 0.25)
        g.a("iron_black").box(-rb, rf, y + sgw * 1.03 - 0.02, y + sgw * 1.03 + 0.02, Z + 0.22, Z + 0.26)
        g.a("iron_black").box(-rb, rf, y + sgw * 1.03 - 0.015, y + sgw * 1.03 + 0.015, Z - 0.30, Z - 0.27)
    for x in np.arange(-rb + 10, rf, 24.0):
        # T字橋脚: 脚柱+張り出した横梁(2本の桁を受ける)+支承
        g.a("concrete", bevel=0.05).cyl((x, -2.3, -0.2), (x, -2.3, Z - 2.1), 1.05, 0.8, seg=8)
        g.a("concrete").extrude_x([(-5.5, Z - 1.5), (-5.0, Z - 2.1), (0.4, Z - 2.1), (0.9, Z - 1.5), (0.9, Z - 1.35), (-5.5, Z - 1.35)], x - 0.7, x + 0.7)   # 張り出し梁(下面に勾配)
        for y in ys:
            g.a("k5_steel").box(x - 0.25, x + 0.25, y - 0.25, y + 0.25, Z - 1.58, Z - 1.5)
        g.a("concrete").box(x - 1.4, x + 1.4, -2.3 - 1.6, -2.3 + 1.6, -0.45, -0.1)           # 基礎フーチング
    for y in ys:       # 走行面の鋼板・案内/安定輪の走行面・給電レール
        g.a("iron_black").box(-rb, rf, y - 0.31, y + 0.31, Z, Z + 0.03)
        for sg in (-1, 1):
            g.a("k5_steel").box(-rb, rf, y + sg * 0.43 - 0.025, y + sg * 0.43 + 0.025, Z - 0.5, Z - 0.2)
        g.a("iron_black").box(-rb, rf, y + 0.46, y + 0.5, Z - 1.1, Z - 1.04)
    for x in np.arange(-rb, rf, 6.0):      # 桁の継目(伸縮装置)
        for y in ys:
            g.a("iron_black").box(x - 0.03, x + 0.03, y - 0.43, y + 0.43, Z - 1.5, Z + 0.001)
    # 駅(軌道の間に島式ホーム+コンコース)
    for (xa_, xb_) in ((-34, 14.0), (19.5, 34)):
        g.a("concrete", bevel=0.02).box(xa_, xb_, -3.9, -0.7, Z - 1.2, Z + 0.25)
        g.a("stone").box(max(xa_, -33.9), min(xb_, 33.9), -3.8, -0.8, Z + 0.25, Z + 0.28)
    for (ya_, yb_) in ((-3.9, -3.1), (-1.5, -0.7)):            # 階段の穴の両脇
        g.a("concrete", bevel=0.02).box(14.0, 19.5, ya_, yb_, Z - 1.2, Z + 0.25)
        g.a("stone").box(14.0, 19.5, ya_ + 0.1, yb_ - 0.1, Z + 0.25, Z + 0.28)
    for x in np.arange(-30, 31, 7.5):
        if 13.0 < x < 29.0:
            continue                                            # 階段の通り道
        g.a("concrete", bevel=0.02).box(x - 0.5, x + 0.5, -2.8, -1.8, 0.0, Z - 1.2)
    # 屋根(曲面シェル風の片流れ)と柱
    for x in np.arange(-32, 33, 8.0):
        g.a("iron_black").cyl((x, -2.3, Z + 0.28), (x, -2.3, Z + 3.8), 0.1, seg=8)
    g.a("white_paint").extrude_x([(-5.6, Z + 3.5), (-2.3, Z + 4.4), (1.0, Z + 3.5), (1.0, Z + 3.3), (-2.3, Z + 4.2), (-5.6, Z + 3.3)], -36, 36)
    for x in np.arange(-34, 35, 8.0):      # 屋根の梁(鉄骨リブ)と雨樋
        g.a("iron_black").extrude_x([(-5.5, Z + 3.3), (-2.3, Z + 4.2), (0.9, Z + 3.3), (0.9, Z + 3.1), (-2.3, Z + 3.95), (-5.5, Z + 3.1)], x - 0.07, x + 0.07)
    g.a("iron_black").box(-36, 36, -5.7, -5.5, Z + 3.1, Z + 3.4)
    g.a("iron_black").box(-36, 36, 0.9, 1.1, Z + 3.1, Z + 3.4)
    for x in np.arange(-30, 31, 6.0):      # ホームのベンチ・水銀灯・黄線
        if 13.0 < x < 20.0:
            continue
        g.a("wood_dark").box(x - 0.9, x + 0.9, -2.55, -2.05, Z + 0.28 + 0.4, Z + 0.28 + 0.45)
        g.a("iron_black").box(x - 0.85, x - 0.8, -2.5, -2.1, Z + 0.28, Z + 0.28 + 0.4)
        g.a("iron_black").box(x + 0.8, x + 0.85, -2.5, -2.1, Z + 0.28, Z + 0.28 + 0.4)
    g.a("stone").box(-33.9, 33.9, -0.95, -0.85, Z + 0.28, Z + 0.285) if False else None
    for yy in (-0.95, -3.65):
        g.a("white_paint").box(-33.9, 33.9, yy, yy + 0.1, Z + 0.281, Z + 0.285)
    # 下の駅舎(1階: ガラス張りのコンコース)
    g.a("glass").box(-22, 22, 4.0, 4.05, 0.2, 4.4)
    g.a("concrete", bevel=0.02).box(-24, 24, -0.5, 14.0, 4.4, 4.8)
    for (xa_, xb_, ya_, yb_) in ((-24, 24, -0.5, -0.2), (-24, 24, 13.7, 14.0), (-24, -23.7, -0.5, 14.0), (23.7, 24, -0.5, 14.0)):
        g.a("concrete", bevel=0.01).box(xa_, xb_, ya_, yb_, 4.8, 5.3)                  # 屋上パラペット
    for k in range(3):                                                             # 屋上の機器(空調室外機・煙突)
        g.a("k5_steel").box(-12 + k * 12, -9 + k * 12, 6.0, 8.0, 4.8, 6.0)
    g.a("iron_black").cyl((16, 11, 4.8), (16, 11, 7.5), 0.25, seg=10)
    g.a("concrete", bevel=0.02).box(-24, -22, 4.0, 14.0, 0.0, 4.4)
    g.a("concrete", bevel=0.02).box(22, 24, 4.0, 14.0, 0.0, 4.4)
    g.a("concrete", bevel=0.01).box(-22, 22, 13.8, 14.0, 0.0, 4.4)
    # 昇降階段: 島式ホームの真下を x 方向に走り、ホーム床の穴(x14〜19.5, y-3.1〜-1.5)から上に出る(軌道桁 y=0 とは交差しない)
    import rooms as _R
    _R.stair_run(g, 'x', 28.0, 14.0, -2.3, 0.0, Z + 0.25, width=1.5, rise=0.18)
    g.build()
    # 車止め(終端)と駅名
    gp = G("k6_B02_stop", "Props")
    gp.a("iron_black").box(rf - 6.0, rf - 5.6, -5.1, 0.5, Z, Z + 0.9)
    gp.build()
    face_plane("k6_B02_nm", f"kit_{sid}_ekimei.png", 'S', 0.0, 3.95, 3.2, 6.0, h=2.0)
    lamp_point(0.0, 8.0, 3.8, watt=90.0)
    # 公園: 並木・池・遊歩道・ベンチ
    import veg
    for i in range(10):
        veg.CARD_SCALE = 0.35
        veg.zelkova(-60 + i * 14.0, 26.0 + (i % 3) * 7.0, h=9.5, rad=3.9, seed=700 + i)
        veg.CARD_SCALE = 1.0
    kit2.pond(40, 36, 20, 11, "k6_B02_pond")
    core.ribbon("k6_B02_walk", [(x, 22.0) for x in np.arange(-70, 71, 6.0)], 3.0, M["pebble"] if "pebble" in M else M["road"])
    _town(sid, rng, "urban", 56.0, 0.5, rows=1, sides=("L",), skip=((-40, 40),))


# ----------------------------------------------------------------- R02 汐見埠頭: 臨港線の終点 (桟橋・貨客船)
def r02():
    sid = "R02"
    rng = random.Random(802)
    kit.ground(L=600, W=600)
    rb, rf = _reach(sid)
    ys = [0.0, -4.6]
    _tracks(sid, ys, ballast=True, bufend=True, x1=70.0)
    g = G("k6_R02_quay", "Station")
    # 岸壁と桟橋(木+コンクリ)
    g.a("concrete", bevel=0.02).box(-20, 90, -26.0, -10.5, -0.6, 0.45)
    g.a("wood_dark", bevel=0.01).box(40, 110, -34.0, -26.0, -0.1, 0.4)
    for x in np.arange(40, 110, 4.0):
        for yy in (-33.5, -26.4):
            g.a("wood_dark").cyl((x, yy, -2.5), (x, yy, 0.0), 0.2, seg=8)
    # 待合桟橋上屋(トタン+木)
    g.a("wood_dark", bevel=0.01).box(46, 74, -33.0, -27.0, 0.4, 3.6)
    g.a("tin").extrude_x([(-33.6, 3.5), (-30.0, 5.0), (-26.4, 3.5)], 45.5, 74.5)
    g.a("glass").box(48, 72, -27.0, -26.96, 1.2, 2.8)
    # ホーム(2線をはさむ島式風) と貨物上屋
    platform(-30, 60, -3.2, -1.1 + 0.0, name="k6_R02_plat") if False else None
    platform(-30, 60, -9.4, -6.3, name="k6_R02_plat")
    g.a("tin", bevel=0.01).box(15, 52, 6.0, 20.0, 0.0, 5.2)
    g.a("tin").extrude_x([(5.6, 5.0), (13.0, 7.0), (20.4, 5.0)], 14.5, 52.5)
    g.a("dark_glass").box(18, 28, 5.97, 6.03, 0.0, 4.0)
    g.a("dark_glass").box(34, 44, 5.97, 6.03, 0.0, 4.0)
    # 倉庫 煉瓦
    g.a("brick", bevel=0.02).box(-40, -8, 12.0, 26.0, 0.0, 6.0)
    g.a("roof").extrude_x([(11.4, 6.0), (19.0, 8.6), (26.6, 6.0)], -40.4, -7.6)
    # 駅舎: 木造平屋(待合・切符)
    g.a("wood", bevel=0.02).box(-6, 8, -17.0, -11.0, 0.0, 3.2) if False else None
    g.build()
    # 船(貨客船の舷側・白と黒)
    gs = G("k6_R02_ship", "Props")
    gs.a("iron_black", bevel=0.05).box(52, 108, -62.0, -36.0, -2.0, 4.0)
    gs.a("white_paint", bevel=0.05).box(58, 100, -60.0, -38.0, 4.0, 7.5)
    gs.a("white_paint", bevel=0.05).box(66, 90, -56.0, -42.0, 7.5, 10.2)
    gs.a("post_red").cyl((78, -49, 10.2), (78, -49, 14.0), 1.5, 1.2, seg=18)
    gs.a("iron_black").cyl((78, -49, 14.0), (78, -49, 14.5), 1.55, seg=18)
    gs.build()
    sig.KINDS["crane"](100.0, -20.0, name="k6_R02_crane")
    sig.KINDS["water"](-34, 32, name="k6_R02_water")
    sig.KINDS["lighthouse"](118, -30, name="k6_R02_lh")
    # 海(桟橋まわり)
    gw = G("k6_R02_sea", "Ground")
    gw.a("water").box(-30, 160, -160, -26.0, -0.55, 0.03)   # 旧: 上面-0.06が地面(-0.01)の下で海が見えなかった
    gw.build()
    _ekimei(sid, 30.0, 5.9, 3.6, w=6.0, name="k6_R02_nm")
    face_plane("k6_R02_pier_nm", f"kit_{sid}_facade.png", 'S', 60.0, -33.05, 2.2, 6.0, h=1.4)
    _town(sid, rng, "port", 34.0, 0.55, rows=1, sides=("L",), skip=((-45, 55),))


def _wrap(f, sid):
    def w():
        kit2.mats2()
        _boards(sid)
        f()
    return w


BUILD6 = {k: _wrap(v, k) for k, v in {"T02": t02, "T03": t03, "K02": k02, "T04": t04, "K03": k03, "TR02": tr02, "B02": b02, "R02": r02}.items()}
