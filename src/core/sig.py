"""Signature (landmark) objects that make each station recognisable. Local coordinates, built via props.G."""
from common import *
import math
import lib, props
from props import G


def clock_tower(x, y, h=14.0, w=3.2, wall="plasterw", name="sig_clock"):
    g = G(name, "Buildings")
    g.a(wall if wall in M else "concrete", bevel=0.02).box(x - w / 2, x + w / 2, y - w / 2, y + w / 2, 0.0, h)
    g.a("concrete", bevel=0.02).box(x - w / 2 - 0.3, x + w / 2 + 0.3, y - w / 2 - 0.3, y + w / 2 + 0.3, h, h + 0.4)
    g.a("roof").extrude_x([(y - w / 2 - 0.3, h + 0.4), (y, h + 2.6), (y + w / 2 + 0.3, h + 0.4)], x - w / 2 - 0.3, x + w / 2 + 0.3)
    for fx, fy, nx, ny in ((x, y - w / 2, 0, -1), (x, y + w / 2, 0, 1), (x - w / 2, y, -1, 0), (x + w / 2, y, 1, 0)):
        g.a("white_paint").cyl((fx, fy, h - 2.2), (fx + nx * 0.08, fy + ny * 0.08, h - 2.2), 1.0, seg=24)
        g.a("iron_black").cyl((fx + nx * 0.08, fy + ny * 0.08, h - 2.2), (fx + nx * 0.1, fy + ny * 0.1, h - 2.2 + 0.7), 0.04, seg=6)
        g.a("iron_black").cyl((fx + nx * 0.08, fy + ny * 0.08, h - 2.2), (fx + nx * 0.1 + 0.6 * (ny != 0), fy + ny * 0.1 + 0.6 * (nx != 0), h - 2.2), 0.04, seg=6)
    g.build()


def water_tower(x, y, h=9.0, name="sig_water"):
    g = G(name, "Props")
    for dx in (-1.2, 1.2):
        for dy in (-1.2, 1.2):
            g.a("iron_black").cyl((x + dx, y + dy, 0), (x + dx * 0.7, y + dy * 0.7, h), 0.12, seg=8)
    g.a("wood_dark", bevel=0.01).cyl((x, y, h), (x, y, h + 3.2), 2.1, seg=24)
    g.a("iron_rust").cyl((x, y, h + 3.2), (x, y, h + 4.1), 2.2, 0.15, seg=24)
    g.build()


def lighthouse(x, y, h=16.0, name="sig_lighthouse"):
    g = G(name, "Buildings")
    g.a("white_paint").cyl((x, y, 0), (x, y, h), 2.6, 1.6, seg=28)
    g.a("post_red").cyl((x, y, h * 0.45), (x, y, h * 0.62), 2.1, 1.95, seg=28)
    g.a("iron_black").cyl((x, y, h), (x, y, h + 0.3), 2.2, seg=28)
    g.a("glass").cyl((x, y, h + 0.3), (x, y, h + 2.2), 1.3, seg=20)
    g.a("lamp_glow").sphere((x, y, h + 1.2), (0.5, 0.5, 0.5), seg=8, rings=4)
    g.a("post_red").cyl((x, y, h + 2.2), (x, y, h + 3.4), 1.5, 0.05, seg=20)
    g.build()


def onsen_hut(x, y, name="sig_onsen"):
    g = G(name, "Buildings")
    g.a("wood", bevel=0.02).box(x - 3.0, x + 3.0, y - 2.2, y + 2.2, 0.0, 3.0)
    g.a("roof").extrude_x([(y - 2.8, 2.9), (y, 5.0), (y + 2.8, 2.9)], x - 3.4, x + 3.4)
    g.a("wood_dark").box(x - 0.6, x + 0.6, y - 0.8, y + 0.8, 5.0, 7.0)          # steam vent (yagura)
    g.a("roof").extrude_x([(y - 1.1, 7.0), (y, 8.0), (y + 1.1, 7.0)], x - 0.9, x + 0.9)
    g.build()


def foot_bath(x, y, name="sig_footbath"):
    g = G(name, "Props")
    g.a("stone").box(x - 2.0, x + 2.0, y - 0.7, y + 0.7, 0.0, 0.5)
    for dx in (-2.0, 2.0):
        g.a("wood_dark").box(x + dx - 0.07, x + dx + 0.07, y - 0.7, y - 0.55, 0.0, 2.4)
    g.a("roof").box(x - 2.4, x + 2.4, y - 1.3, y + 1.3, 2.4, 2.55)
    g.build()


def quay_crane(x, y, name="sig_crane", arm=1):
    """岸壁の門型ジブクレーン(ポータルフレーム+旋回する機械室+トラス状ジブ+フック・ケーブル+カウンターウェイト)。arm=+1/-1 でジブを出す向き(y方向)。"""
    g = G(name, "Props")
    ir, ib, yel = "iron_rust", "iron_black", "post_red"
    for dx in (-4.2, 4.2):                                  # 走行レールと脚(2つの門型)
        g.a(ib).box(x + dx - 0.15, x + dx + 0.15, y - 5.0, y + 5.0, 0.0, 0.2)
        for dy in (-3.8, 3.8):
            g.a(ir, bevel=0.01).box(x + dx - 0.25, x + dx + 0.25, y + dy - 0.25, y + dy + 0.25, 0.2, 9.5)
            g.a(ib).box(x + dx - 0.5, x + dx + 0.5, y + dy - 0.5, y + dy + 0.5, 0.0, 0.5)             # 台車
        g.a(ir, bevel=0.01).box(x + dx - 0.3, x + dx + 0.3, y - 4.1, y + 4.1, 9.2, 9.8)               # 上梁
        for k in (-1, 1):
            g.a(ir).sbox((x + dx, y + k * 3.8, 3.0), (x + dx, y, 9.4), 0.14, 0.14, up=(1, 0, 0))      # 斜材
    g.a(ir, bevel=0.01).box(x - 4.6, x + 4.6, y - 0.4, y + 0.4, 9.8, 10.3)                              # 脚間の渡し梁
    g.a(yel, bevel=0.02).box(x - 2.2, x + 2.2, y - 2.0, y + 2.0, 10.3, 14.0)                             # 機械室(旋回台の上)
    g.a("dark_glass").box(x - 2.0, x + 2.0, y + arm * 2.0, y + arm * 2.03, 11.6, 13.4)                  # 運転室の窓(ジブ側)
    g.a(ib).box(x - 2.4, x + 2.4, y - 2.2, y + 2.2, 14.0, 14.3)                                         # 屋根
    # トラス状ジブ(2本の弦材+斜材)を海側へ
    a0 = (x, y + arm * 1.5, 13.0); a1 = (x, y + arm * 24.0, 19.5)
    for dx in (-0.6, 0.6):
        g.a(ir).sbox((a0[0] + dx, a0[1], a0[2]), (a1[0] + dx, a1[1], a1[2]), 0.14, 0.14, up=(1, 0, 0))
        g.a(ir).sbox((a0[0] + dx, a0[1], a0[2] - 1.4), (a1[0] + dx, a1[1], a1[2] - 0.6), 0.12, 0.12, up=(1, 0, 0))
    for t in np.linspace(0.05, 0.95, 12):
        p0 = (x - 0.6, a0[1] + (a1[1] - a0[1]) * t, a0[2] + (a1[2] - a0[2]) * t)
        p1 = (x + 0.6, a0[1] + (a1[1] - a0[1]) * (t + 0.04), a0[2] - 1.4 + (a1[2] - 0.6 - (a0[2] - 1.4)) * (t + 0.04))
        g.a(ir).sbox(p0, p1, 0.07, 0.07, up=(1, 0, 0))
    g.a(ir).sbox((x, y - arm * 1.0, 14.3), (x, y + arm * 24.0, 19.6), 0.08, 0.08, up=(1, 0, 0))              # 吊り索
    g.a(ib).box(x - 2.0, x + 2.0, y - arm * 6.0 - 1.5, y - arm * 6.0 + 1.5, 10.3, 13.2)                 # カウンターウェイト
    g.a(ib).cyl((x, y + arm * 20.0, 18.4), (x, y + arm * 20.0, 6.5), 0.03, seg=6)                       # フックのケーブル
    g.a(yel).box(x - 0.35, x + 0.35, y + arm * 20.0 - 0.3, y + arm * 20.0 + 0.3, 5.4, 6.5)               # フック/スプレッダ
    g.build()


def pier(x0, y0, length=40.0, name="sig_pier"):
    g = G(name, "Props")
    g.a("wood_dark").box(x0 - 3, x0 + 3, y0, y0 + length, 0.5, 0.75)
    for k in np.arange(0.0, length, 4.0):
        for dx in (-2.8, 2.8):
            g.a("wood_dark").cyl((x0 + dx, y0 + k, -2.5), (x0 + dx, y0 + k, 0.5), 0.18, seg=8)
    g.build()


def truss_bridge(x, y, span=24.0, name="sig_bridge"):
    """Steel through-truss on the main line (track y); river bed below."""
    g = G(name, "Props")
    for yy in (y - 1.7, y + 1.7):
        g.a("iron_black").box(x - span / 2, x + span / 2, yy - 0.1, yy + 0.1, 0.0, 0.5)
        g.a("iron_black").box(x - span / 2, x + span / 2, yy - 0.1, yy + 0.1, 5.2, 5.5)
        n = int(span / 4)
        for k in range(n + 1):
            xx = x - span / 2 + k * span / n
            g.a("iron_black").box(xx - 0.1, xx + 0.1, yy - 0.1, yy + 0.1, 0.4, 5.3)
            if k < n:
                g.a("iron_black").sbox((xx, yy, 0.4 if k % 2 == 0 else 5.3), (xx + span / n, yy, 5.3 if k % 2 == 0 else 0.4), 0.12, 0.12, up=(0, 1, 0))
    for xx in (x - span / 2 - 1.2, x + span / 2 + 1.2):
        g.a("stone").box(xx - 1.2, xx + 1.2, y - 3.0, y + 3.0, -4.0, 0.5)
    g.build()
    w = lib.Acc("sig_river", lib.mat_plain("river", (0.07, 0.14, 0.15), rough=0.05, spec=0.9), "Ground")
    w.box(x - span / 2 - 0.2, x + span / 2 + 0.2, -60, 60, -3.2, -3.0)
    w.build()


def obs_deck(x, y, name="sig_deck"):
    g = G(name, "Props")
    g.a("wood").box(x - 3, x + 3, y - 2, y + 2, 2.4, 2.6)
    for dx in (-2.8, 2.8):
        for dy in (-1.8, 1.8):
            g.a("wood_dark").box(x + dx - 0.1, x + dx + 0.1, y + dy - 0.1, y + dy + 0.1, 0.0, 2.4)
    g.a("wood_dark").box(x - 3, x + 3, y - 2, y - 1.9, 2.6, 3.5)
    g.build()


def chimney(x, y, h=22.0, name="sig_chimney"):
    g = G(name, "Buildings")
    g.a("brick", bevel=0.02).cyl((x, y, 0), (x, y, h), 1.4, 0.8, seg=20)
    g.build()


def snow_hut(x, y, name="sig_snowhut"):
    g = G(name, "Buildings")
    g.a("wood", bevel=0.02).box(x - 2, x + 2, y - 1.5, y + 1.5, 0.0, 2.4)
    g.a("tin").extrude_x([(y - 2.0, 2.2), (y, 3.4), (y + 2.0, 2.2)], x - 2.3, x + 2.3)
    g.build()


def signal_tower(x, y, name="sig_sigtower"):
    g = G(name, "Buildings")
    g.a("wood", bevel=0.02).box(x - 1.5, x + 1.5, y - 1.5, y + 1.5, 0.0, 3.0)
    g.a("wood", bevel=0.02).box(x - 1.8, x + 1.8, y - 1.8, y + 1.8, 3.0, 5.2)
    g.a("glass").box(x - 1.7, x + 1.7, y - 1.75, y - 1.7, 3.5, 4.8)
    g.a("roof").extrude_x([(y - 2.2, 5.1), (y, 6.4), (y + 2.2, 5.1)], x - 2.2, x + 2.2)
    g.build()


def monument(x, y, name="sig_monument"):
    """起点記念碑 + 0哩標 (Honamino)."""
    g = G(name, "Props")
    g.a("stone", bevel=0.03).box(x - 1.6, x + 1.6, y - 1.6, y + 1.6, 0.0, 0.4)
    g.a("stone", bevel=0.03).box(x - 0.6, x + 0.6, y - 0.3, y + 0.3, 0.4, 3.2)
    g.build()


def atc_tower(x, y, h=26.0, name="sig_atc"):
    """空港管制塔: 細い塔身+張り出した管制室+アンテナ。"""
    g = G(name, "Buildings")
    g.a("concrete", bevel=0.03).cyl((x, y, 0), (x, y, h), 2.4, 1.7, seg=24)
    g.a("concrete", bevel=0.03).cyl((x, y, h), (x, y, h + 1.2), 3.6, 3.6, seg=24)
    g.a("glass").cyl((x, y, h + 1.2), (x, y, h + 3.6), 4.0, 3.4, seg=24)
    g.a("white_paint").cyl((x, y, h + 3.6), (x, y, h + 4.1), 4.4, 4.4, seg=24)
    g.a("post_red").cyl((x, y, h + 4.1), (x, y, h + 4.5), 4.5, 4.5, seg=24)
    g.a("iron_black").cyl((x, y, h + 4.5), (x, y, h + 8.5), 0.07, seg=6)
    g.a("iron_black").box(x - 0.9, x + 0.9, y - 0.05, y + 0.05, h + 7.0, h + 7.12)
    g.a("lamp_glow").sphere((x, y, h + 8.6), (0.18, 0.18, 0.18), seg=8, rings=4)
    g.build()


def radar_dome(x, y, name="sig_radar"):
    """空港監視レーダー: 低い塔+回転アンテナ(ドーム)。"""
    g = G(name, "Buildings")
    g.a("concrete", bevel=0.03).box(x - 2.2, x + 2.2, y - 2.2, y + 2.2, 0.0, 6.0)
    g.a("iron_black").cyl((x, y, 6.0), (x, y, 8.0), 0.2, seg=8)
    g.a("white_paint").box(x - 3.2, x + 3.2, y - 0.2, y + 0.2, 8.0, 10.6)
    g.a("post_red").box(x - 3.2, x + 3.2, y - 0.25, y + 0.25, 10.4, 10.8)
    g.build()


def windsock(x, y, name="sig_windsock"):
    """吹き流し(紅白)。"""
    g = G(name, "Props")
    g.a("iron_black").cyl((x, y, 0), (x, y, 7.0), 0.07, seg=8)
    for i in range(5):
        g.a("post_red" if i % 2 == 0 else "white_paint").cyl((x + i * 0.55, y, 7.0), (x + (i + 1) * 0.55, y, 7.0), 0.4 - i * 0.05, 0.35 - i * 0.05, seg=12)
    g.build()


def campus_gate(x, y, name="sig_gate"):
    """学園の正門: 門柱+校名板+時計つき講堂。"""
    g = G(name, "Buildings")
    for dx in (-3.2, 3.2):
        g.a("concrete", bevel=0.03).box(x + dx - 0.5, x + dx + 0.5, y - 0.5, y + 0.5, 0.0, 2.6)
        g.a("concrete", bevel=0.03).box(x + dx - 0.65, x + dx + 0.65, y - 0.65, y + 0.65, 2.6, 2.9)
    g.a("iron_black").box(x - 2.7, x + 2.7, y - 0.05, y + 0.05, 0.1, 0.18)
    g.a("white_paint").box(x - 2.4, x + 2.4, y - 0.3, y + 0.3, 3.1, 4.2)
    g.a("brick", bevel=0.03).box(x - 9, x + 9, y + 16, y + 26, 0.0, 9.0)
    g.a("roof").extrude_x([(y + 15.4, 9.0), (y + 21, 12.5), (y + 26.6, 9.0)], x - 9.6, x + 9.6)
    for i in range(5):
        g.a("glass").box(x - 7.5 + i * 3.7, x - 6.3 + i * 3.7, y + 15.95, y + 16.05, 2.0, 6.8)
    g.a("brick", bevel=0.03).box(x - 1.6, x + 1.6, y + 19.5, y + 22.5, 9.0, 17.0)
    g.a("white_paint").cyl((x, y + 19.45, 14.4), (x, y + 19.35, 14.4), 1.0, seg=24)
    g.a("roof").extrude_x([(y + 19.2, 17.0), (y + 21, 19.0), (y + 22.8, 17.0)], x - 1.8, x + 1.8)
    g.build()


def silo_group(x, y, name="sig_silo"):
    """流通団地の高層自動倉庫+サイロ。"""
    g = G(name, "Buildings")
    g.a("concrete", bevel=0.03).box(x - 12, x + 12, y - 8, y + 8, 0.0, 22.0)
    g.a("tin").box(x - 12.2, x + 12.2, y - 8.2, y + 8.2, 22.0, 22.5)
    for i in range(3):
        g.a("white_paint").cyl((x + 16 + i * 5.2, y, 0), (x + 16 + i * 5.2, y, 17.0), 2.5, seg=24)
        g.a("iron_black").cyl((x + 16 + i * 5.2, y, 17.0), (x + 16 + i * 5.2, y, 18.2), 2.5, 0.4, seg=24)
    g.build()


def farm_silo(x, y, name="sig_farmsilo"):
    """農村: 円筒の穀物サイロ3基(円錐屋根・梯子・帯)+切妻の納屋+干し草(M07 果樹園)。"""
    g = G(name, "Buildings")
    for i, (dx, r, h) in enumerate([(0.0, 2.6, 13.0), (5.9, 2.6, 11.0), (11.8, 2.2, 9.0)]):
        cx = x + dx
        g.a("concrete", bevel=0.02).cyl((cx, y, 0), (cx, y, h), r, seg=28)
        for k in range(1, 5):                                   # 横帯(型枠継ぎ目)
            g.a("iron_black").cyl((cx, y, h * k / 5.0), (cx, y, h * k / 5.0 + 0.12), r + 0.05, seg=28)
        g.a("tin").cyl((cx, y, h), (cx, y, h + 1.5), r + 0.15, 0.25, seg=28)       # 円錐屋根
        g.a("iron_black").box(cx + r - 0.02, cx + r + 0.12, y - 0.25, y + 0.25, 0.3, h - 0.5)   # 梯子
    bx, by = x - 4.0, y + 12.0
    g.a("wood_dark", bevel=0.03).box(bx - 9, bx + 9, by - 5, by + 5, 0.0, 5.5)
    g.a("tin").extrude_x([(by - 5.6, 5.4), (by, 8.8), (by + 5.6, 5.4), (by + 5.6, 5.2), (by, 8.55), (by - 5.6, 5.2)], bx - 9.6, bx + 9.6)
    g.a("iron_black").box(bx - 2.0, bx + 2.0, by - 5.02, by - 4.9, 0.0, 4.2)      # 大戸
    for i in range(5):
        g.a("yellow_grass" if "yellow_grass" in M else "wood_dark").cyl((bx + 12 + i * 2.2, by - 3, 0.0), (bx + 12 + i * 2.2, by - 3, 1.3), 0.9, seg=14)  # 干し草(丸ロール)
    g.build()


def apt_tower(x, y, name="sig_apt"):
    """ニュータウン: 14階建て高層住棟(バルコニー縞)。"""
    g = G(name, "Buildings")
    g.a("pl_cream" if "pl_cream" in M else "concrete", bevel=0.03).box(x - 14, x + 14, y - 5.5, y + 5.5, 0.0, 42.0)
    for z in range(2, 42, 3):
        g.a("concrete").box(x - 14.1, x + 14.1, y - 6.4, y - 5.5, z, z + 0.15)
        g.a("glass").box(x - 13, x + 13, y - 5.55, y - 5.5, z + 0.5, z + 2.3)
    g.a("concrete").box(x - 14.3, x + 14.3, y - 5.8, y + 5.8, 42.0, 42.6)
    g.a("post_red").box(x + 8, x + 12, y - 0.6, y + 0.6, 42.6, 45.5)
    g.build()


def sports_field(x, y, name="sig_field"):
    """学園の運動場: 赤褐色のトラック+芝のフィールド+ゴール+ネット。"""
    g = G(name, "Props")
    n = 40
    pts = [(x + 26 * math.cos(2 * math.pi * k / n), y + 15 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        g.a("brick").sbox((a[0], a[1], 0.03), (b[0], b[1], 0.03), 5.0, 0.04)
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        g.a("white_paint").sbox((a[0], a[1], 0.07), (b[0], b[1], 0.07), 0.08, 0.02)
    g.a("grass_ground" if "grass_ground" in M else "concrete").box(x - 20, x + 20, y - 8.5, y + 8.5, 0.0, 0.05)
    for sx in (-1, 1):
        for dy in (-1.8, 1.8):
            g.a("white_paint").cyl((x + sx * 20, y + dy, 0), (x + sx * 20, y + dy, 2.4), 0.06, seg=6)
        g.a("white_paint").sbox((x + sx * 20, y - 1.8, 2.4), (x + sx * 20, y + 1.8, 2.4), 0.06, 0.06)
    for k in range(10):                                   # バックネット
        yy = y - 18 + k * 0.01
    g.a("iron_black").box(x - 6, x + 6, y - 19.2, y - 19.1, 0.0, 4.5)
    for px in (-6, 0, 6):
        g.a("iron_black").cyl((x + px, y - 19.15, 0), (x + px, y - 19.15, 5.0), 0.05, seg=6)
    g.build()


def torii(x, y, name="sig_torii"):
    """鳥居(朱)と石灯籠・参道の敷石。"""
    g = G(name, "Buildings")
    for dx in (-1.9, 1.9):
        g.a("post_red", bevel=0.02).cyl((x + dx, y, 0), (x + dx, y, 4.6), 0.28, 0.24, seg=14)
        g.a("stone", bevel=0.02).box(x + dx - 0.4, x + dx + 0.4, y - 0.4, y + 0.4, 0.0, 0.3)
    g.a("post_red", bevel=0.02).box(x - 2.6, x + 2.6, y - 0.22, y + 0.22, 4.3, 4.75)       # 笠木
    g.a("post_red", bevel=0.02).box(x - 2.1, x + 2.1, y - 0.15, y + 0.15, 3.5, 3.8)        # 貫
    g.a("iron_black").box(x - 0.3, x + 0.3, y - 0.08, y + 0.08, 3.85, 4.3)                  # 額束
    for dx in (-3.4, 3.4):
        g.a("stone", bevel=0.02).box(x + dx - 0.25, x + dx + 0.25, y + 2.0 - 0.25, y + 2.0 + 0.25, 0.0, 1.5)
        g.a("stone", bevel=0.02).box(x + dx - 0.4, x + dx + 0.4, y + 2.0 - 0.4, y + 2.0 + 0.4, 1.5, 1.9)
    for i in range(9):
        g.a("stone").box(x - 0.6, x + 0.6, y + 1.0 + i * 1.1, y + 1.9 + i * 1.1, 0.0, 0.05)
    g.build()


def logstack(x, y, name="sig_log"):
    """製材所: 丸太の山と製材小屋・トロッコ線の木材ホッパー。"""
    g = G(name, "Props")
    for row in range(4):
        for i in range(10 - row * 2):
            g.a("bark").cyl((x - 5 + row + i * 1.0, y - 2.0, 0.45 + row * 0.8), (x - 5 + row + i * 1.0, y + 2.6, 0.45 + row * 0.8), 0.46, seg=10)
    g.a("wood", bevel=0.02).box(x + 8, x + 16, y - 3.0, y + 3.0, 0.0, 3.4)
    g.a("tin").extrude_x([(y - 3.6, 3.2), (y, 4.6), (y + 3.6, 3.2)], x + 7.6, x + 16.4)
    g.a("iron_black").cyl((x + 13, y - 3.0, 3.4), (x + 13, y - 3.0, 8.0), 0.2, seg=8)       # 煙突
    g.build()


def ski_lift(x, y, name="sig_skilift"):
    """スキー場: リフト乗り場と鉄塔・ワイヤ。"""
    g = G(name, "Props")
    g.a("wood_dark", bevel=0.02).box(x - 4, x + 4, y - 2.5, y + 2.5, 0.0, 0.4)
    g.a("tin_blue").extrude_x([(y - 3.0, 3.0), (y, 4.0), (y + 3.0, 3.0)], x - 4.3, x + 4.3)
    for dx in (-3.6, 3.6):
        g.a("iron_black").cyl((x + dx, y - 2.4, 0.4), (x + dx, y - 2.4, 3.1), 0.12, seg=8)
    for k in range(1, 5):
        xx, yy = x + 6 + k * 14, y + k * 6
        g.a("iron_black").cyl((xx, yy, 0.0), (xx, yy, 9.0 + k * 0.6), 0.22, 0.14, seg=8)
        g.a("iron_black").box(xx - 1.4, xx + 1.4, yy - 0.08, yy + 0.08, 9.0 + k * 0.6, 9.2 + k * 0.6)
    g.build()


def fire_tower(x, y, h=16.0, name="sig_firetower"):
    """山の火の見櫓(木造4脚+見張り台)。"""
    g = G(name, "Props")
    for dx in (-1.4, 1.4):
        for dy in (-1.4, 1.4):
            g.a("wood_dark", bevel=0.01).cyl((x + dx * 1.5, y + dy * 1.5, 0), (x + dx, y + dy, h), 0.14, 0.1, seg=8)
    for z in (4.0, 8.0, 12.0):
        s_ = 1.4 * (1.5 - z / (h * 2.0))
        g.a("wood_dark").box(x - s_, x + s_, y - s_, y + s_, z, z + 0.08)
    g.a("wood").box(x - 1.8, x + 1.8, y - 1.8, y + 1.8, h, h + 0.15)
    g.a("tin").extrude_x([(y - 2.3, h + 2.0), (y, h + 3.2), (y + 2.3, h + 2.0)], x - 2.3, x + 2.3)
    for dx in (-1.7, 1.7):
        for dy in (-1.7, 1.7):
            g.a("wood_dark").box(x + dx - 0.06, x + dx + 0.06, y + dy - 0.06, y + dy + 0.06, h, h + 2.0)
    g.build()


KINDS = {"clock": clock_tower, "water": water_tower, "lighthouse": lighthouse, "onsen": onsen_hut, "footbath": foot_bath,
         "crane": quay_crane, "pier": pier, "bridge": truss_bridge, "deck": obs_deck, "chimney": chimney, "snowhut": snow_hut,
         "sigtower": signal_tower, "monument": monument,
         "atc": atc_tower, "radar": radar_dome, "windsock": windsock, "gate": campus_gate, "silo": silo_group, "farm_silo": farm_silo, "apt": apt_tower, "field": sports_field, "torii": torii, "logstack": logstack, "skilift": ski_lift, "firetower": fire_tower}
# station id -> [(kind, x, y)]  (local coords: y>0 forecourt side, y<0 far side)
SIG = {
 "M01": [("clock", 40, 40), ("chimney", -30, 40)], "M02": [("water", -40, 22)], "M03": [("clock", 10, 24)],
 "M04": [("water", 30, 18), ("chimney", -40, 30)], "M05": [("sigtower", 14, 8), ("water", -34, 20)],
 "M06": [("monument", -14, 11), ("water", -45, 20), ("clock", 6, 18)],
 "M07": [("deck", 30, 12)], "M08": [("water", 20, -16), ("sigtower", 10, 10), ("chimney", -30, 28)],
 "M09": [], "M10": [("onsen", 30, 24), ("footbath", -22, 12), ("chimney", 50, 30)], "M11": [("water", 20, -12), ("snowhut", -30, 8)],
 "M12": [("deck", 25, 10), ("snowhut", -26, 8)], "M13": [("snowhut", 30, 8)],
 "M14": [("crane", 30, 24), ("chimney", -30, 30), ("water", -20, 22)], "M15": [("deck", 20, 8)],
 "M16": [("clock", 8, 26), ("crane", 40, 30)], "M17": [("sigtower", 14, 8)], "M18": [("lighthouse", 30, 24)],
 "M19": [("clock", 60, 20), ("crane", 70, 50), ("chimney", 80, 40)],
 "Y02": [("deck", 20, 10)], "Y03": [("bridge", 0, 0)], "Y04": [("onsen", 26, 20), ("footbath", -14, 10)],
}
def place(sid):
    for k, x, y in SIG.get(sid, []):
        if k == "pier":
            KINDS[k](x, y)
        else:
            KINDS[k](x, y, name=f"sig_{sid}_{k}_{int(x)}") if k not in ("bridge",) else KINDS[k](x, y, name=f"sig_{sid}_bridge")
