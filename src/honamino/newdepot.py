"""D4/D5: 穂波野 新・総合車両基地(引き揚げ線 + 留置線群 + 大型庫 + 管理棟/技術開発棟の外形)。
座標は穂波野ゾーン原点。引き揚げ線は第6線(78,T6)の東端から東へ出て南へ曲がり、幹線 x=123 を南下、留置線12本が東へ分岐する。"""
from common import *
import trackkit
from trackkit import seg_line, seg_arc, join, build_track
from lib import Acc

# --- 配線(実際の車両基地に倣う): 引き揚げ線は第6線端から緩い曲線(R=200)で出て、斜めのはしご線(約12°)に入り、
#     はしご線から各留置線が分岐(分岐器の転向曲線 R=150、約1:5相当)して間隔4.5mの平行線になる。台形の敷地(手前の線ほど長い)。
ALPHA = math.radians(12.0)
LEAD_R = 200.0
TURN_R = 150.0
N_STAB = 12
DY = 4.5
X_END = 480.0
S0 = 12.0                       # はしご始点から最初の分岐器までの距離(m)
DS = DY / math.sin(ALPHA)       # はしご線上の分岐器の間隔
_c = (78.0, T6 - LEAD_R)
LADDER0 = np.array([_c[0] + LEAD_R * math.sin(ALPHA), _c[1] + LEAD_R * math.cos(ALPHA)])
HDIR = np.array([math.cos(ALPHA), -math.sin(ALPHA)])      # はしご線の進行方向(東南東)


def ladder_pt(k):
    return LADDER0 + HDIR * (S0 + DS * k)


def stab_y(k):
    L = ladder_pt(k)
    return L[1] - TURN_R * (1 - math.cos(ALPHA))


def stab_x0(k):
    """留置線の平行部分の始端x(転向曲線の終点)。"""
    return ladder_pt(k)[0] + TURN_R * math.sin(ALPHA)


YA, YB = stab_y(0), stab_y(N_STAB - 1)
SHED = dict(x0=300.0, x1=420.0, y0=stab_y(5) - 2.8, y1=YA + 2.8, h=9.5)


def build_tracks():
    from kit5 import turnout
    lead = join(seg_line((70.0, T6), (78.0, T6)), seg_arc(_c, LEAD_R, 90, 90 - math.degrees(ALPHA)),
                seg_line(LADDER0, ladder_pt(N_STAB - 1) + HDIR * 14.0))
    build_track("N_lead", lead)
    for k in range(N_STAB):
        L = ladder_pt(k)
        cx, cy = L[0] + TURN_R * math.sin(ALPHA), L[1] + TURN_R * math.cos(ALPHA)
        arc = seg_arc((cx, cy), TURN_R, -90 - math.degrees(ALPHA), -90)
        P = join(arc, seg_line(arc[-1], (X_END, arc[-1][1])))
        build_track(f"N_stab{k}", P)
        trackkit.buffer_stop(X_END + 1.0, arc[-1][1], 0)
        turnout(P, f"N_to{k}", sig=(k == 0))


# --- 旧車庫(扇形庫・転車台)は新基地の「ごく小さな一部」として、はしご線の終端から続く支線の先へ移設する(D6)
OLD_TX, OLD_TY, OLD_PR = -14.0, -80.0, 11.5
OLD_DY = -120.0
_E = ladder_pt(N_STAB - 1) + HDIR * 14.0
_R2 = 60.0
_th = -ALPHA
_C2 = _E + _R2 * np.array([math.cos(_th - math.pi / 2), math.sin(_th - math.pi / 2)])
OLD_DX = float(_C2[0] + _R2 - OLD_TX)


def build_old_depot_lead():
    end_y = OLD_TY + OLD_PR + OLD_DY
    P = join(seg_arc(_C2, _R2, math.degrees(_th) + 90.0, 0.0), seg_line((_C2[0] + _R2, _C2[1]), (_C2[0] + _R2, end_y)))
    build_track("N_oldlead", P)


def move_new_objects(names, dx, dy):
    """旧車庫の構築で増えたオブジェクトを平行移動する(親のないものだけ。子は親に従う)。"""
    n = 0
    for nm in names:
        ob = bpy.data.objects.get(nm)
        if ob is not None and ob.parent is None:
            ob.location.x += dx
            ob.location.y += dy
            n += 1
    return n


def build_ground():
    a = Acc("nd_yard_cinder", M["dirt"], "Roads")
    x0, x1 = 96.0, X_END + 10.0
    cy = (YA + YB) / 2 - 3.0
    a.boxc((x0 + x1) / 2, cy, 0.03, x1 - x0, abs(YA - YB) + 40.0, 0.06)
    a.build()


def build_shed():
    s = SHED
    w, d, h = s["x1"] - s["x0"], s["y1"] - s["y0"], s["h"]
    cx, cy = (s["x0"] + s["x1"]) / 2, (s["y0"] + s["y1"]) / 2
    col = Acc("nd_shed_frame", M["iron_black"], "Station", bevel=0.01)
    n = int(w // 10)
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


def build_shed_fit():
    """庫内の設備: 検修ピット縁・作業用側歩廊・天井の吊り照明・天井クレーン走行桁。"""
    s = SHED
    h = s["h"]
    x0, x1 = s["x0"] + 6.0, s["x1"] - 4.0
    pit = Acc("nd_shed_pit", M["concrete"], "Station")
    walk = Acc("nd_shed_walk", M["plat_top"], "Station")
    lamp = Acc("nd_shed_lamps", M["lamp_glow"], "Station")
    rod = Acc("nd_shed_rods", M["iron_black"], "Station")
    for k in range(6):
        y = stab_y(k)
        for sg in (-0.95, 0.95):                      # ピットの縁石(レールの内側)
            pit.boxc((x0 + x1) / 2, y + sg, 0.06, x1 - x0 - 8.0, 0.18, 0.16)
        if k % 2 == 0:                                  # 2線おきに高い作業歩廊(線の北側)
            walk.boxc((x0 + x1) / 2, y + 2.25, 0.35, x1 - x0, 0.95, 0.7)
        for x in np.arange(x0 + 4.0, x1, 12.0):
            lamp.boxc(x, y, h - 1.3, 0.9, 0.3, 0.12)
            rod.boxc(x, y, h - 0.65, 0.04, 0.04, 1.3)
    for a in (pit, walk, lamp, rod):
        a.build()
    import rooms as _rooms                                  # 発光面だけでは室内が真っ暗になるので実光源(蛍光灯色)も置く
    for k in (1, 3, 5):
        y = (stab_y(k - 1) + stab_y(k)) / 2
        for x in np.arange(x0 + 4.0, x1, 12.0):
            _rooms.lamp_point(x, y, h - 1.6, 260.0, color=(0.92, 0.97, 1.0), size=0.5, name="nd_shed_light")
    gd = Acc("nd_shed_crane", M["iron_rust"], "Station")
    for y in (SHED["y0"] + 0.9, SHED["y1"] - 0.9):
        gd.boxc((x0 + x1) / 2, y, h - 1.8, x1 - x0, 0.3, 0.45)
    gd.build()


def build_blocks():
    """管理棟群(3階建)と技術開発棟群(外形。室内は D7/D8)。はしご線の南側に置く。"""
    adm = Acc("nd_admin", M["concrete"], "Station", bevel=0.02)
    for x, y in [(230.0, -115.0), (256.0, -115.0), (282.0, -115.0)]:
        adm.boxc(x, y, 5.5, 22, 16, 11)
    adm.build()
    rd = Acc("nd_rd", M["wall"], "Station", bevel=0.02)
    for x, y, w, d, h in [(140.0, -120.0, 34, 22, 14), (140.0, -150.0, 34, 22, 14), (190.0, -150.0, 30, 30, 10)]:
        rd.boxc(x, y, h / 2, w, d, h)
    rd.build()
    gl = Acc("nd_blocks_glass", M["dark_glass"], "Station")
    for x, y in [(230.0, -115.0), (256.0, -115.0), (282.0, -115.0)]:
        for z in (2.6, 5.9, 9.0):
            gl.boxc(x, y + 8.02, z, 18, 0.06, 1.4)
    gl.build()


def build_stock():
    """留置車両: 庫内(第0〜5線)と庫外(第6〜11線)に客車編成。外形のみ(室内は車両側の室内つきモデル)。"""
    import train as T
    n = 0
    plan = {0: 3, 1: 3, 2: 2, 3: 3, 4: 3, 5: 2, 6: 4, 7: 5, 8: 3, 9: 4, 10: 2, 11: 3}
    for k, cnt in plan.items():
        x0 = max(stab_x0(k) + 14.0, SHED["x0"] + 12.0) if k <= 5 else stab_x0(k) + 14.0
        for j in range(cnt):
            T.make_coach(f"nd_coach_{k}_{j}", variant=(k + j) % 4, seed=300 + n).place(x0 + 10.0 + j * 20.6, stab_y(k), math.pi if (k + j) % 2 else 0.0)
            n += 1


def build():
    build_tracks()
    build_ground()
    build_shed()
    build_shed_fit()
    build_blocks()
    build_stock()
    print("newdepot built")
