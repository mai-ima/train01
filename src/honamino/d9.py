"""D9a: 穂波野の旅客ホーム増設。第3線(T3)と第4線(T4)の間に島式ホーム(第2島)、第5線(T5)と第6線(T6)の間に短い島式ホーム(第3島)。
島間は構内踏切(板張り)で結ぶ。仕上げは core.build_island と同じ(石積みの側面+砂利舗装+コンクリート縁石+白線+端のスロープ)。"""
from common import *
from lib import Acc

ISLAND2 = (-4.0, 48.0, T4 + 1.7, T3 - 1.7)       # x0, x1, y0(南縁), y1(北縁)
ISLAND3 = (46.0, 66.0, T6 + 1.7, T5 - 1.7)


def _island(name, rect):
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


def build_platforms():
    _island("d9_isl2", ISLAND2)
    _island("d9_isl3", ISLAND3)
    # 第1島(T2/T3)→第2島: T3 を横切る。第2島→第3島: T4・T5 を横切る
    _crossing(0.5, ISLAND2[3], T3 + 1.7, [T3])
    _crossing(47.0, ISLAND2[2], ISLAND3[3], [T4, T5])
    _footbridge(20.0)
    print("[D9b] 跨線橋を追加: x=20")
    print("[D9a] 島式ホーム2面を追加:", ISLAND2, ISLAND3)
