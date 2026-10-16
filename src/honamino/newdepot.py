"""D4/D5: 穂波野 新・総合車両基地(引き揚げ線 + 留置線群 + 大型庫 + 管理棟/技術開発棟の外形)。
座標は穂波野ゾーン原点。引き揚げ線は第6線(78,T6)の東端から東へ出て南へ曲がり、幹線 x=123 を南下、留置線12本が東へ分岐する。"""
from common import *
import trackkit
from trackkit import seg_line, seg_arc, join, build_track
from lib import Acc

LEAD_R = 45.0
SPINE_X = LEAD_R + 78.0
N_STAB = 12
Y0 = -140.0
DY = 6.0
BR = 14.0
X_END = 285.0
SHED = dict(x0=190.0, x1=290.0, y0=-171.0, y1=-134.0, h=9.5)


def stab_y(k):
    return Y0 - DY * k


def build_tracks():
    cy = T6 - LEAD_R
    y_last = stab_y(N_STAB - 1) + BR
    lead = join(seg_line((70.0, T6), (78.0, T6)), seg_arc((78.0, cy), LEAD_R, 90, 0),
                seg_line((SPINE_X, cy), (SPINE_X, y_last)))
    build_track("N_lead", lead)
    for k in range(N_STAB):
        y = stab_y(k)
        P = join(seg_arc((SPINE_X + BR, y + BR), BR, 180, 270), seg_line((SPINE_X + BR, y), (X_END, y)))
        build_track(f"N_stab{k}", P)
        trackkit.buffer_stop(X_END + 1.0, y, 0)


def build_ground():
    a = Acc("nd_yard_cinder", M["dirt"], "Roads")
    cx, cy = (SPINE_X + X_END) / 2 + 4, (stab_y(0) + stab_y(N_STAB - 1)) / 2
    a.boxc(cx, cy, 0.0, X_END - SPINE_X + 24, DY * N_STAB + 30, 0.04)
    a.build()
    b = Acc("nd_lead_cinder", M["dirt"], "Roads")
    b.boxc(SPINE_X, (T6 - LEAD_R + stab_y(N_STAB - 1)) / 2, 0.0, 14, abs(T6 - LEAD_R - stab_y(N_STAB - 1)), 0.04)
    b.build()


def build_shed():
    s = SHED
    w, d, h = s["x1"] - s["x0"], s["y1"] - s["y0"], s["h"]
    cx, cy = (s["x0"] + s["x1"]) / 2, (s["y0"] + s["y1"]) / 2
    col = Acc("nd_shed_frame", M["iron_black"], "Station", bevel=0.01)
    n = int(w // 10) + 1
    for i in range(n + 1):
        x = s["x0"] + w * i / n
        for y in (s["y0"], s["y1"]):
            col.boxc(x, y, h / 2, 0.45, 0.45, h)
        col.boxc(x, cy, h + 0.4, 0.3, d + 0.4, 0.5)
    col.build()
    wall = Acc("nd_shed_wall", M["tin"], "Station")
    wall.boxc(s["x1"], cy, h / 2, 0.25, d, h)
    for y in (s["y0"], s["y1"]):
        wall.boxc(cx, y, h * 0.37, w, 0.2, h * 0.74)
    wall.build()
    gl = Acc("nd_shed_clerestory", M["glass"], "Station")
    for y in (s["y0"], s["y1"]):
        gl.boxc(cx, y, h * 0.87, w, 0.1, h * 0.26)
    gl.build()
    roof = Acc("nd_shed_roof", M["tin"], "Station")
    roof.boxc(cx, cy, h + 0.9, w + 1.0, d + 1.6, 0.22)
    roof.build()


def build_blocks():
    """管理棟群(3階建)と技術開発棟群(外形。室内は D7/D8)。"""
    adm = Acc("nd_admin", M["concrete"], "Station", bevel=0.02)
    for x, y in [(160.0, -110.0), (160.0, -140.0), (160.0, -170.0)]:
        adm.boxc(x, y, 5.5, 22, 16, 11)
    adm.build()
    rd = Acc("nd_rd", M["wall"], "Station", bevel=0.02)
    for x, y, w, d, h in [(96.0, -215.0, 34, 22, 14), (96.0, -245.0, 34, 22, 14), (136.0, -240.0, 30, 30, 10)]:
        rd.boxc(x, y, h / 2, w, d, h)
    rd.build()
    gl = Acc("nd_blocks_glass", M["dark_glass"], "Station")
    for x, y in [(160.0, -110.0), (160.0, -140.0), (160.0, -170.0)]:
        for z in (2.6, 5.9, 9.0):
            gl.boxc(x, y + 8.02, z, 18, 0.06, 1.4)
    gl.build()


def build():
    build_tracks()
    build_ground()
    build_shed()
    build_blocks()
    print("newdepot built")
