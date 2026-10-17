"""D4/D5: 穂波野 新・総合車両基地(引き揚げ線 + 留置線群 + 大型庫 + 管理棟/技術開発棟の外形)。
座標は穂波野ゾーン原点。引き揚げ線は第6線(78,T6)の東端から東へ出て南へ曲がり、幹線 x=123 を南下、留置線12本が東へ分岐する。"""
from common import *
import random
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


def _smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def build_lead_b(turnout):
    """S-D11: 入出庫線を複線化。第5線の東端から第2の引き揚げ線(N_leadB)を並行して出し、
    第6線側の引き揚げ線(N_lead)へは緩い渡り線(約1:8)でつなぐ。第5線⇄第6線の渡り線(T5→T6)も設ける。
    N_leadB ははしご線と並行する長い引上線で、先端に車止めを置く(2本の引き揚げ線で入出庫が同時に取れる)。"""
    dT = T5 - T6                                                    # 引き揚げ線の線間(5.5m)
    rb = LEAD_R + dT
    cb = _c
    arcB = seg_arc(cb, rb, 90, 90 - math.degrees(ALPHA))
    endB = LADDER0 + HDIR * (S0 + DS * 9 + 6.0) + np.array([math.sin(ALPHA), math.cos(ALPHA)]) * dT
    B = join(seg_line((50.0, T5), (78.0, T5)), arcB, seg_line(arcB[-1], endB))
    build_track("N_leadB", join(seg_line((68.0, T5), (78.0, T5)), arcB, seg_line(arcB[-1], endB)))   # 68までは第5線本体(core)と重ねない
    trackkit.buffer_stop(endB[0] + HDIR[0] * 1.0, endB[1] + HDIR[1] * 1.0, -math.degrees(ALPHA))
    # 渡り線 B→A: 第5線(引き揚げ線B)から第6線側の引き揚げ線Aへ、長さ約44mで寄る(1:8相当)
    Bd, _s = trackkit.resample(B, 1.0)
    L = 44.0
    i0 = int(np.argmax(Bd[:, 0] >= 58.0))
    Q = []
    for k in range(int(L) + 1):
        P = Bd[i0 + k]
        if P[0] <= 78.0 + 1e-6 and abs(P[1] - T5) < 0.2:
            A = np.array([P[0], T6])
        else:
            v = P - np.array(cb)
            A = np.array(cb) + v / np.linalg.norm(v) * LEAD_R
        Q.append(P + (A - P) * _smooth(k / L))
    X = np.array(Q)
    build_track("N_leadX", X)
    turnout(X, "N_toX", sig=True)


def build_tracks():
    from kit5 import turnout
    lead = join(seg_line((70.0, T6), (78.0, T6)), seg_arc(_c, LEAD_R, 90, 90 - math.degrees(ALPHA)),
                seg_line(LADDER0, ladder_pt(N_STAB - 1) + HDIR * 14.0))
    build_track("N_lead", lead)
    build_lead_b(turnout)
    for k in range(N_STAB):
        L = ladder_pt(k)
        cx, cy = L[0] + TURN_R * math.sin(ALPHA), L[1] + TURN_R * math.cos(ALPHA)
        arc = seg_arc((cx, cy), TURN_R, -90 - math.degrees(ALPHA), -90)
        xe = SHED["x1"] - 3.0 if k <= 5 else X_END           # 庫に入る6線は庫内の東端で行き止まり(貫通させない)
        P = join(arc, seg_line(arc[-1], (xe, arc[-1][1])))
        build_track(f"N_stab{k}", P)
        trackkit.buffer_stop(xe + 1.0, arc[-1][1], 0)
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
    nb = int(w // 10)                                              # D5b: 10m ごとの屋根スパンに分節(段差・母屋・軒先)
    rng_r = random.Random(31)
    for i in range(nb):
        x = s["x0"] - 0.5 + (w + 1.0) * (i + 0.5) / nb
        roof.boxc(x, cy, h + 0.9 + rng_r.uniform(-0.04, 0.04), (w + 1.0) / nb - 0.06, d + 1.6, 0.22)
    roof.build()
    rib = Acc("nd_shed_purlin", M["iron_black"], "Station", bevel=0.01)
    for i in range(nb + 1):                                        # 各スパン境に棟と直交する大梁(軒下から見える)
        x = s["x0"] - 0.5 + (w + 1.0) * i / nb
        rib.boxc(x, cy, h + 0.72, 0.22, d + 1.7, 0.3)
    for j in range(1, 5):                                          # 長手方向の母屋
        rib.boxc(cx, s["y0"] + d * j / 5, h + 0.78, w + 1.0, 0.16, 0.18)
    rib.build()
    mon = Acc("nd_shed_monitor", M["tin"], "Station")              # 棟の上に採光・排煙用のモニター屋根
    mon.boxc(cx, cy, h + 2.05, w * 0.82, d * 0.30, 0.18)
    mon.build()
    mg = Acc("nd_shed_monitor_glass", M["glass"], "Station")
    for y in (cy - d * 0.15 + 0.05, cy + d * 0.15 - 0.05):
        mg.boxc(cx, y, h + 1.5, w * 0.82, 0.08, 0.95)
    mg.build()
    stk = Acc("nd_shed_stacks", M["iron_black"], "Station", bevel=0.02)
    for i in range(1, nb, 3):                                      # 蒸機・ディーゼル用の排気塔
        x = s["x0"] - 0.5 + (w + 1.0) * i / nb
        for dy in (-d * 0.25, d * 0.25):
            stk.boxc(x, cy + dy, h + 1.9, 0.9, 0.9, 1.9)
            stk.boxc(x, cy + dy, h + 2.95, 1.5, 1.5, 0.15)
    stk.build()


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


def _grid_lights(g, v, zf, step=6.0, watt=150.0):
    import rooms
    x0, x1, y0, y1 = v["x0"], v["x1"], v["y0"], v["y1"]
    nx, ny = max(1, int((x1 - x0) // step)), max(1, int((y1 - y0) // step))
    for i in range(nx):
        for j in range(ny):
            rooms.lamp_point(x0 + (i + 0.5) * (x1 - x0) / nx, y0 + (j + 0.5) * (y1 - y0) / ny, zf + 2.55, watt, color=(0.95, 0.97, 1.0), size=0.4, name="nd_in_light")


def office_fit(g, v, rng, zf):
    """管理棟の1階: 受付カウンター・事務机の島・書庫・掲示板。"""
    import rooms
    x0, x1, y0, y1 = v["x0"], v["x1"], v["y0"], v["y1"]
    rooms.counter(g, x0 + 3.0, x0 + (x1 - x0) * 0.45, y0 + 2.6, zf, d=0.7, h=1.05)
    for r in range(2):
        for i in range(5):
            rooms.desk(g, x0 + 2.0 + i * 2.1, y0 + 5.5 + r * 2.4, zf, face='S' if r == 0 else 'N')
    for k in range(3):
        rooms.shelf(g, x0 + 1.0 + k * 3.4, x0 + 3.9 + k * 3.4, y1 - 0.45, zf, face='S', goods="jars", seed=k + 2)
    g.a("white_paint").box(x1 - 4.5, x1 - 0.4, y1 - 0.2, y1 - 0.14, zf + 1.0, zf + 2.2)   # 掲示板
    _grid_lights(g, v, zf)


def lab_fit(kind):
    def fit(g, v, rng, zf):
        import rooms
        x0, x1, y0, y1 = v["x0"], v["x1"], v["y0"], v["y1"]
        w, d = x1 - x0, y1 - y0
        if kind == "ticket":                         # 券売機の試作室: 試作機を並べた展示台と調整用作業台
            for i in range(6):
                x = x0 + 2.0 + i * (w - 4.0) / 5.0
                g.a("iron_black").box(x - 0.4, x + 0.4, y1 - 1.6, y1 - 0.9, zf, zf + 1.75)
                g.a("dark_glass").box(x - 0.3, x + 0.3, y1 - 1.62, y1 - 1.6, zf + 1.25, zf + 1.6)
                g.a("lamp_glow").box(x - 0.1, x + 0.1, y1 - 1.62, y1 - 1.6, zf + 0.95, zf + 1.0)
                g.a("chrome").box(x - 0.25, x + 0.25, y1 - 1.62, y1 - 1.6, zf + 0.7, zf + 0.78)
            for i in range(4):
                rooms.desk(g, x0 + 3.0 + i * 3.4, y0 + 4.0, zf, w=1.8, face='S')
        elif kind == "gate":                         # 改札機の試作室: 通路型の試作ゲートと通過試験レーン
            for i in range(5):
                x = x0 + 3.0 + i * 1.5
                for sg in (-0.45, 0.45):
                    g.a("iron_black").box(x + sg - 0.12, x + sg + 0.12, y0 + 5.0, y0 + 6.7, zf, zf + 1.0)
                    g.a("lamp_glow").box(x + sg - 0.05, x + sg + 0.05, y0 + 5.3, y0 + 5.5, zf + 1.0, zf + 1.04)
                    g.a("chrome").box(x + sg - 0.1, x + sg + 0.1, y0 + 5.0, y0 + 5.1, zf + 0.9, zf + 0.96)
            for i in range(3):
                rooms.desk(g, x0 + 2.0 + i * 3.0, y1 - 1.6, zf, face='N')
        elif kind == "display":                      # 運行・表示システムの開発室: 壁一面の表示盤と制御卓
            for i in range(5):
                x = x0 + 1.5 + i * (w - 3.0) / 5.0
                g.a("dark_glass").box(x, x + (w - 3.0) / 5.0 - 0.3, y1 - 0.32, y1 - 0.2, zf + 1.1, zf + 2.3)
                g.a("lamp_glow").box(x + 0.2, x + (w - 3.0) / 5.0 - 0.5, y1 - 0.2, y1 - 0.18, zf + 1.4, zf + 2.0)
            for i in range(4):
                rooms.desk(g, x0 + 2.5 + i * 3.6, y0 + 6.0, zf, w=1.6, face='N')
        _grid_lights(g, v, zf)
    return fit


def build_blocks():
    """管理棟群(3階建)と技術開発棟群。室内つき(1階の窓口/事務室+階段+上階の執務室。B6e の kit2.volume を流用)。はしご線の南側に置く。
    技術開発棟は用途別: 券売機の試作・改札機の試作・運行/表示システムの開発(ユーザー指示 2026-10-11 22:43)。"""
    import kit2
    from kit2 import SubZone
    kit2.mats2()
    rng = random.Random(77)
    # (名前, 前面中心x, 前面y, 幅, 奥行, 階数, 壁, 備品) — 前面(local y=0)が北(はしご線側)を向くよう yaw=π
    # D7b: 3棟を別設計に(屋根形状・階数・平面・外構を変える。以前は同一の箱を色と寸法だけ変えていた)
    specs = [("nd_adm1", 245.0, -100.0, 24.0, 14.0, 3, "pl_grey", office_fit, "gable", "wing"), ("nd_adm2", 285.0, -100.0, 20.0, 12.0, 3, "plasterw", office_fit, "hip", "porch"),
             ("nd_adm3", 322.0, -100.0, 22.0, 13.0, 2, "pl_cream", office_fit, "saw", "tank"),
             ("nd_rd1", 150.0, -108.0, 30.0, 18.0, 4, "pl_grey", lab_fit("ticket"), "flat", "porch"), ("nd_rd2", 195.0, -108.0, 28.0, 16.0, 3, "pl_blue", lab_fit("gate"), "hip", "wing"),
             ("nd_rd3", 150.0, -140.0, 36.0, 20.0, 2, "concrete", lab_fit("display"), "saw", "tank")]
    for nm, xc, yf, w, d, nfl, wall, fit, roof, extra in specs:
        with SubZone((xc + w / 2, yf, -1.3), math.pi):
            g = kit2.G(nm, "Buildings")
            v = dict(x0=0.0, x1=w, y0=0.0, y1=d, nfl=nfl, roof=roof, wall=wall, door="S", custom_fit=fit)
            kit2.volume(g, v, rng, {"id": "M06"}, interior=True)
            zf = Z_PLAT + 0.30
            zh = zf + 2.9 + (nfl - 1) * 3.0
            if extra == "porch":                                  # 正面の車寄せ(庇+2本の柱)
                g.a("concrete", bevel=0.01).box(w / 2 - 3.4, w / 2 + 3.4, -3.2, 0.1, zf + 2.7, zf + 2.95)
                for px in (w / 2 - 3.1, w / 2 + 3.1):
                    g.a("iron_black", bevel=0.01).box(px - 0.12, px + 0.12, -3.0, -2.76, zf, zf + 2.7)
            elif extra == "wing":                                  # 平屋の別棟(食堂・倉庫など)を側面に増築
                wv = dict(x0=w, x1=w + 9.0, y0=1.0, y1=min(d, 9.0), nfl=1, roof="shed", wall="plasterw", door="S")
                kit2.volume(g, wv, rng, {"id": "M06"}, interior=False)
            elif extra == "tank":                                  # 屋上の高架水槽と階段室の塔屋
                g.a("iron_black", bevel=0.02).cyl((w * 0.75, d * 0.5, zh + 0.2), (w * 0.75, d * 0.5, zh + 2.6), 1.2, 1.2, seg=14)
                g.a("pl_grey", bevel=0.02).box(w * 0.2, w * 0.2 + 3.2, d * 0.35, d * 0.35 + 3.0, zh, zh + 2.9)
            g.build()

def build_site():
    """敷地づくり: 管理棟前の舗装広場・構内道路・柵・植栽・街灯。箱だけが芝生に建つ状態を解消する。"""
    plaza = Acc("nd_plaza", M["concrete"], "Roads")
    plaza.boxc(283.0, -103.0, 0.035, 110.0, 24.0, 0.07)            # 管理棟前の広場
    plaza.boxc(172.0, -118.0, 0.035, 90.0, 52.0, 0.07)             # 技術開発棟前
    plaza.build()
    road = Acc("nd_road", M["road"], "Roads")
    road.boxc(228.0, -88.0, 0.045, 190.0, 7.0, 0.09)                # 構内道路(はしご線の南側)
    road.boxc(110.0, -150.0, 0.045, 8.0, 140.0, 0.09)               # 本社側へ南下する道
    road.build()
    fence = Acc("nd_fence", M["iron_black"], "Props")
    for x in np.arange(100.0, 480.0, 5.0):                          # 南側境界のフェンス(柱+上下2段の横桟)。旧車庫は敷地の内側に含める
        fence.boxc(x, -255.0, 0.9, 0.08, 0.08, 1.8)
    fence.boxc(290.0, -255.0, 1.6, 380.0, 0.03, 0.04)
    fence.boxc(290.0, -255.0, 0.7, 380.0, 0.03, 0.04)
    fence.build()
    lamps = Acc("nd_poles", M["iron_black"], "Props")
    glow = Acc("nd_pole_lamps", M["lamp_glow"], "Props")
    for x in np.arange(120.0, 330.0, 30.0):                         # 街灯は構内道路沿い(はしご線・引込線の上に立たない範囲)
        lamps.boxc(x, -91.5, 4.0, 0.14, 0.14, 8.0)
        lamps.boxc(x, -92.2, 8.0, 0.14, 1.5, 0.1)
        glow.boxc(x, -92.8, 7.9, 0.5, 0.25, 0.08)
    lamps.build()
    glow.build()
    import veg
    rng = random.Random(5)
    for k in range(26):                                             # 敷地の周りの並木
        x = 105.0 + k * 14.5 + rng.uniform(-2, 2)
        veg.zelkova(x, (-160.0 if x < 350.0 else -250.0) + rng.uniform(-2.5, 2.0), h=rng.uniform(8, 12), rad=rng.uniform(3.6, 5.0), seed=k)


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


def register_grass_exclusion():
    """新基地の敷地(留置線・庫・管理棟群・広場・構内道路・引込線)には近景の草を生やさない。屋内の床にまで草が出ていた(室内確認で発見)。"""
    import veg
    for r in ((96.0, 495.0, -102.0, -26.0), (125.0, 345.0, -168.0, -86.0), (340.0, 445.0, -160.0, -80.0)):
        if r not in veg.EXTRA_EXCL:
            veg.EXTRA_EXCL.append(r)


def build():
    import os
    register_grass_exclusion()
    skip = os.environ.get("ND_SKIP", "").split(",")          # 調査用: 部分ごとに構築を省く(通常は空)
    build_tracks()
    build_ground()
    if "shed" not in skip:
        build_shed()
        build_shed_fit()
    if "blocks" not in skip:
        build_blocks()
    if "site" not in skip:
        build_site()
    if "stock" not in skip:
        build_stock()
    print("newdepot built")
