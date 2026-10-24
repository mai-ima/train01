import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
import sys as _sys
if _os.environ.get("PYTHONHASHSEED") != "0":      # Q24: 文字列 hash() が乱数の種に使われているため、実行ごとに結果が変わらないよう固定して再実行する
    _os.environ["PYTHONHASHSEED"] = "0"
    _os.execv(_sys.executable, [_sys.executable] + _sys.argv)
"""Build + render the Honamino station (national-railway era). Usage:
python3 main.py --cam A --w 960 --samples 24 --parts core,station --out test
"""
import argparse
import math
import os
import sys
import time

sys.path.insert(0, f"{_R}")
import bpy
from mathutils import Vector

import common
from common import *

ap = argparse.ArgumentParser()
ap.add_argument("--cam", default="A")
ap.add_argument("--w", type=int, default=960)
ap.add_argument("--samples", type=int, default=24)
ap.add_argument("--parts", default="core,station,props,train,veg,hq")
ap.add_argument("--out", default="test")
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--exposure", type=float, default=0.0)
ap.add_argument("--sky", type=float, default=0.14)
ap.add_argument("--sun", type=float, default=4.6)
ap.add_argument("--cloud", type=float, default=0.0)
ap.add_argument("--noclouds", action="store_true")
ap.add_argument("--air", type=float, default=1.5)
ap.add_argument("--aer", type=float, default=0.2)
ap.add_argument("--save-blend", action="store_true")
ap.add_argument("--tex-max", type=int, default=0)
ap.add_argument("--pack", action="store_true")
ap.add_argument("--pano", default="", help="json nodes file -> equirect panoramas")
ap.add_argument("--webexport", default="")
ap.add_argument("--stats", action="store_true")
ap.add_argument("--people", default="on", help="人物の表示: on | off | cars(車内の乗客のみ) | station(駅の人物のみ)")
ap.add_argument("--stock", default="on", help="停車車両の表示: on | off | 駅ID,駅ID(その駅のみ表示)")
ap.add_argument("--interf", action="store_true", help="線路干渉検査(--zone)")
ap.add_argument("--zone", default="", help="station id -> kit zone only")
ap.add_argument("--world", default="", help="markers | bare | all | id,id,... : 全駅を世界座標に配置+駅間線路(bare=駅も目印も置かない)")
ap.add_argument("--rig-export", default="", help="車両リグ構造+メタデータをJSON出力")
ap.add_argument("--pano-start", type=int, default=0)
ap.add_argument("--dof", type=float, default=0.0, help="f-stop; 0=off")
ap.add_argument("--draft", action="store_true", help="ドラフト画質(確認用): サンプル12・光路を浅く・ガラス/透過のバウンス削減。構築後のレンダが数倍速い")
ap.add_argument("--hq", action="store_true", help="高画質プロファイル(1600px以上・128サンプル・アルベド/法線つきデノイズ・細かい適応閾値)")
args = ap.parse_args()
if args.hq:
    args.w = max(args.w, 1600); args.samples = max(args.samples, 128)

t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
M = common.make_materials()
parts = set(args.parts.split(","))
if (args.zone or args.world) and not os.environ.get('ZONE_PARTS'):     # --zone/--world はゾーンビルダーが全部作る(--world で既定 parts のままだと原点の基本パーツが重なり真っ黒になった)。parts(core/station/props/train…)を重ねると全体が二重生成され、同位置の重なりで影が黒く潰れる
    if parts - {'none', ''}:
        print('NOTE: --zone/--world 指定のため --parts を無視します(二重生成防止):', sorted(parts))
    parts = set(p for p in parts if p in ('vtest',))

# ------------------------------------------------------------------ cameras / sun presets
CAMS = {
    # name: (location, target, lens, sun azimuth (deg from N, clockwise), sun elevation)
    "A": ((-4.0, -25.0, 2.4), (-6.0, 2.0, 2.7), 26, 205, 40),
    "B": ((-1.0, 24.5, 1.7), (-6.5, 7.0, 2.1), 24, 250, 30),
    "C": ((-30.0, -2.6, 1.55), (6.0, 1.5, 2.0), 30, 200, 40),
    "H": ((-52.0, -27.0, 4.2), (4.0, -6.0, 1.9), 26, 215, 38),
    "E": ((62.0, -33.0, 5.5), (6.0, -6.0, 1.9), 28, 150, 38),
    "L1": ((-24.0, -10.0, 2.0), (-33.0, -4.6, 2.3), 32, 215, 38),
    "K": ((30.0, 2.9, 1.6), (12.0, 0.0, 2.2), 30, 215, 38),
    "F": ((22.0, -9.2, 1.8), (2.0, -11.0, 2.2), 30, 215, 38),
    "S": ((-47.0, -7.5, 1.7), (-38.0, 0.0, 2.3), 32, 215, 38),
    "K2": ((9.0, 2.6, 1.55), (12.5, 0.0, 2.25), 24, 215, 38),
    "L2": ((-30.0, -8.6, 1.9), (-33.0, -4.6, 2.5), 28, 215, 38),
    "K3": ((9.0, 2.5, 2.3), (13.0, 0.0, 2.45), 30, 215, 38),
    "D": ((72.0, -28.0, 26.0), (-12.0, -72.0, 3.0), 26, 215, 40),
    "D2": ((46.0, -58.0, 9.0), (28.0, -88.0, 3.0), 28, 215, 40),
    "D3": ((-14.0, -56.0, 7.0), (-20.0, -86.0, 3.0), 30, 215, 40),
    "SF": ((-16.0, -5.5, 2.0), (-29.0, 0.0, 2.5), 34, 215, 40),
    "SS": ((-34.0, -9.0, 1.7), (-34.0, 0.0, 2.3), 38, 215, 40),
    "SW": ((-22.0, -12.5, 2.0), (-33.0, 0.0, 2.3), 30, 215, 40),
    "G": ((4.0, 17.2, 1.7), (-14.0, 10.5, 1.3), 28, 215, 40),
    "Z1": ((14.0, 22.0, 2.0), (-6.0, 8.0, 2.4), 26, 215, 40),
    "Z2": ((20.0, 2.6, 1.7), (-8.0, 3.0, 2.2), 28, 215, 40),
    "ZA": ((75.0, -55.0, 45.0), (-5.0, 8.0, 0.0), 30, 215, 40),
    "WA": ((540.0, 931.0, 3500.0), (540.0, 930.0, 0.0), 14, 215, 40),
    "WL": ((-380.0, -120.0, 55.0), (-300.0, 0.0, 0.0), 26, 215, 40),
    "WS1": ((1975.0, 100.0, 16.0), (1885.0, 190.0, 5.0), 30, 215, 40),
    "WS2": ((-1330.0, -85.0, 14.0), (-1275.0, 0.0, 4.0), 30, 215, 40),
    "WS3": ((2700.0, 790.0, 20.0), (2760.0, 880.0, 3.0), 30, 215, 40),
    "WS4": ((1903.0, 150.0, 2.6), (1885.0, 190.0, 5.0), 32, 215, 40),
    "WS5": ((3002.0, 1310.0, 7.0), (2970.0, 1360.0, 3.0), 30, 215, 40),
    "WS6": ((2970.0, 1244.0, 2.6), (2970.0, 1320.0, 3.0), 32, 215, 40),
    "WS7": ((2950.0, 1228.0, 10.0), (2970.0, 1262.0, 2.0), 30, 215, 40),
    "WS8": ((748.0, -640.0, 9.0), (712.0, -668.0, 5.0), 30, 215, 40),
    "WS9": ((822.0, -930.0, 8.0), (797.0, -958.0, 5.0), 32, 215, 40),
    "WS10": ((-790.0, 12.0, 3.5), (-720.0, -3.0, 4.5), 40, 215, 40),
    "WM1": ((-260.0, -170.0, 80.0), (0.0, 0.0, 0.0), 28, 215, 40),
    "WT1": ((296.0, 7.0, 3.4), (316.0, -1.0, 0.2), 50, 215, 40),
    "ZT": ((10.0, -45.0, 90.0), (10.0, 38.0, 0.0), 32, 215, 40),
    "MN": ((60.0, -10.0, 85.0), (60.0, 40.0, 0.0), 34, 215, 40),
    "HQ1": ((62.0, 27.0, 4.0), (76.0, 44.0, 6.0), 28, 215, 40),
    "HQ2": ((100.0, 14.0, 6.0), (115.0, 40.0, 3.0), 34, 215, 40),
    "I1": ((-3.1, 8.0, 2.75), (-10.5, 5.2, 2.2), 20, 215, 40),        # M6: 駅舎室内(待合・ベンチ・ストーブ)
    "I2": ((-11.2, 5.0, 2.75), (-4.0, 7.6, 2.2), 20, 215, 40),        # 駅舎室内(出札窓口側から)
    "I3": ((-7.5, 4.9, 2.5), (-7.5, 8.3, 2.3), 18, 215, 40),          # 駅舎室内(駅前の出入口方向)
    "N1": ((-15.0, 12.5, 2.0), (-7.0, 8.4, 2.9), 30, 215, 40),        # 駅舎の壁・庇・軒の近接(駅前側)
    "N2": ((-15.0, 0.6, 1.9), (-7.0, 4.4, 3.2), 30, 215, 40),         # 駅舎のホーム側・庇の近接
    "D4": ((120.0, 20.0, 150.0), (300.0, -75.0, 0.0), 24, 215, 40),     # D4: 新総合車両基地の全景
    "D6": ((330.0, -110.0, 70.0), (430.0, -205.0, 0.0), 26, 215, 40),     # D6: 移設した旧車庫と新基地の接続
    "D10": ((98.0, -58.0, 20.0), (34.0, -22.0, 1.0), 30, 215, 40),     # D10: 第5・第6線(T5/T6)を南東の上空から
    "D11": ((20.0, -34.0, 3.0), (52.0, -24.0, 1.0), 28, 215, 40),     # 第5・第6線の端(車止め・留置貨車)を低い目線で
    "BG": ((10.0, -2.9, 0.38), (11.5, -0.2, 0.7), 24, 215, 40),        # 車両の台車・床下(線路脇の低い目線)
    "V2A": ((-12.0, -14.0, 7.0), (18.0, 6.0, 1.8), 40, 215, 40),
    "V2B": ((40.0, -14.0, 7.0), (22.0, 8.0, 1.8), 40, 215, 40),
    "WK": ((-330.0, -70.0, 22.0), (-250.0, 0.0, 1.0), 28, 215, 40),
    "ZN1": ((150.0, -190.0, 90.0), (0.0, -20.0, 5.0), 28, 215, 40),
    "ZN4": ((120.0, 120.0, 60.0), (150.0, -10.0, 0.0), 24, 215, 40),
    "ZN2": ((40.0, -105.0, 3.2), (-5.0, -25.0, 5.0), 24, 215, 40),
    "ZN3": ((-90.0, -75.0, 12.0), (-30.0, -25.0, 4.0), 26, 215, 40),
    "WB": ((-2300.0, 300.0, 700.0), (-2200.0, 300.0, 0.0), 30, 215, 40),
    "ZM": ((250.0, -260.0, 170.0), (10.0, 0.0, 6.0), 30, 215, 40),
    "ZM2": ((-170.0, -150.0, 38.0), (10.0, 0.0, 10.0), 26, 215, 40),
    "ZM4": ((31.0, -26.0, 3.0), (6.0, -2.0, 4.6), 20, 215, 40),
    "ZM5": ((-4.0, -40.0, 4.2), (-70.0, -5.0, 6.0), 24, 215, 40),
    "ZM3": ((100.0, -30.0, 4.0), (10.0, 4.0, 12.0), 22, 215, 40),
    "Z3": ((22.0, -2.0, 1.7), (-6.0, 6.0, 2.4), 28, 215, 40),
    "Z4": ((-30.0, 30.0, 1.8), (6.0, 8.0, 3.0), 26, 215, 40),
    "ZS": ((26.0, 11.5, 1.7), (-4.0, 20.0, 2.6), 28, 215, 40),
    "ZB": ((-60.0, 45.0, 30.0), (5.0, 5.0, 0.0), 30, 215, 40),
    "P": ((25.0, 3.0, 2.0), (-8.0, 2.2, 2.0), 26, 215, 40),
    "AV": ((95.0, -40.0, 75.0), (-5.0, -45.0, 0.0), 30, 215, 40),
    "AV2": ((75.0, -40.0, 38.0), (35.0, -62.0, 0.0), 30, 215, 40),
    "SH": ((-58.0, 9.0, 2.0), (-72.0, 21.0, 2.3), 28, 215, 40),
    "IN": ((-26.0, 9.5, 2.0), (-28.0, 20.0, 3.0), 26, 215, 40),
    "XH": ((33.0, -26.0, 2.4), (40.0, 0.0, 1.8), 30, 215, 40),
    "IS": ((-1.0, -8.0, 1.8), (9.0, -6.2, 2.0), 28, 215, 40),
    "HI": ((-60.0, 6.0, 2.1), (-56.5, 21.5, 1.6), 30, 215, 40),
    "II": ((-28.0, 11.0, 2.0), (-27.0, 20.0, 1.7), 34, 215, 40),
    "IH": ((-61.3, 18.5, 1.8), (-53.0, 22.5, 1.3), 24, 215, 40),
    "IIN": ((-30.6, 18.3, 1.8), (-24.0, 22.5, 1.4), 24, 215, 40),
    "II2": ((-30.5, 19.5, 4.7), (-19.0, 19.5, 4.3), 22, 215, 40),
    "ISH": ((-15.6, 19.0, 1.7), (-10.0, 22.5, 1.4), 24, 215, 40),
    "IKU": ((-47.4, 19.0, 1.7), (-46.0, 23.5, 1.6), 24, 215, 40),
    "ISD": ((6.6, 6.5, 2.0), (14.0, 9.0, 1.5), 24, 215, 40),
    "DH": ((22.2, -76.0, 2.6), (30.0, -96.0, 2.2), 22, 215, 40),
    "DO": ((-46.5, -35.0, 1.8), (-40.0, -31.0, 1.5), 22, 215, 40),
    "DR": ((-14.0, -70.0, 2.2), (-14.0, -100.0, 1.8), 26, 215, 40),
    "DI": ((-14.0, -55.0, 1.8), (-14.0, -62.0, 2.0), 30, 215, 40),
    "DDC": ((-32.5, -9.8, 2.9), (-32.5, -4.6, 2.6), 36, 215, 40),
    "DDI": ((-33.8, -4.0, 2.6), (-30.5, -4.9, 2.3), 24, 215, 40),
    "WI": ((3.6, -8.4, 1.8), (5.35, -11.0, 1.7), 30, 215, 40),
    "ANX": ((1.6, 3.4, 1.7), (1.6, 6.8, 1.0), 26, 215, 40),
    "SI": ((-7.0, 5.0, 1.7), (-7.0, 8.4, 1.9), 24, 215, 40),
    "T": ((-8.6, 1.0, 1.7), (-8.0, 4.4, 2.3), 28, 200, 40),
}
import os as _os
if _os.environ.get("DBCAM"):
    _v = [float(t) for t in _os.environ["DBCAM"].split(",")]
    CAMS["DB"] = ((_v[0], _v[1], _v[2]), (_v[3], _v[4], _v[5]), _v[6] if len(_v) > 6 else 30, 215, 40)
    args.cam = "DB"
_CLR_BVH = []
def _cam_clear(v):
    """カメラ(v[0..2])→注視点(v[3..5])の視線と±12°の視線が手前で障害物に当たるなら、視線に直交する水平方向へずらした位置を返す。"""
    import math as _m
    import veg
    from mathutils import Vector as _V
    if not _CLR_BVH:
        _CLR_BVH.append(veg._scene_bvh(-400, 400, -400, 400))
    B = _CLR_BVH[0]
    if not B:
        return v[0], v[1], v[2]
    tree = B[0]
    tgt = _V((v[3], v[4], v[5]))
    base = _V((v[0], v[1], v[2]))
    def score(p):
        """視界の抜け具合(0〜1)。5本の視線の最短ヒット距離/注視点距離の最小値。壁際/内部は0。"""
        _n = 0
        for _dv in (_V((1, 0, 0)), _V((-1, 0, 0)), _V((0, 1, 0)), _V((0, -1, 0))):
            if tree.ray_cast(p, _dv, 2.0)[0] is not None:
                _n += 1
        if _n >= 3:
            return 0.0
        d = tgt - p
        L = d.length
        a0 = _m.atan2(d.y, d.x)
        sc = 1.0
        for da in (0.0, -0.25, 0.25, -0.5, 0.5):
            dv = _V((_m.cos(a0 + da), _m.sin(a0 + da), d.z / max(d.xy.length, 1e-6) * 1.0)).normalized()
            hit = tree.ray_cast(p, dv, L * 0.85)
            if hit[0] is not None:
                sc = min(sc, hit[3] / (L * 0.55))
        for _el in (0.0, -0.12, -0.3):                  # Q11: 手前6m以内の物体(列車の屋根・壁・針葉樹)が画面を占める構図は減点(M02 @A で屋根、S03/S04 @E/@L で針葉樹が画面を占めた)
            for _da in (0.0, -0.2, 0.2, -0.4, 0.4):     # E5所見: 中央1本だけでは画面端の木を拾えない → 水平方向も5本
                _dv2 = _V((_m.cos(a0 + _da), _m.sin(a0 + _da), _el)).normalized()
                _h2 = tree.ray_cast(p, _dv2, 6.0)
                if _h2[0] is not None:
                    sc = min(sc, 0.55 + 0.4 * (_h2[3] / 6.0))
        return min(sc, 1.0)
    base_sc = score(base)
    if base_sc >= 1.0:
        return v[0], v[1], v[2]
    d = tgt - base
    n = _V((-d.y, d.x, 0)).normalized()
    fwd = _V((d.x, d.y, 0)).normalized()
    best = (base_sc, base, "")
    for b in (0.0, -6.0, -12.0, 5.0):                    # 視線方向の前後・高さも試す(密集した駅で横ずらしだけでは見つからないため)
        for dz in (0.0, 2.5):
            for k in (3, -3, 6, -6, 10, -10, 15, -15, 22, -22):
                p = base + n * k + fwd * b + _V((0, 0, dz))
                sc = score(p) - 0.002 * (abs(k) + abs(b) + 3 * dz)      # 元の位置から遠いほど少し減点
                if sc > best[0]:
                    best = (sc, p, f"横{k:+d} m 前後{b:+.0f} m 高さ+{dz:.1f} m")
                if sc >= 0.98:
                    break
    if best[2]:
        print(f"[cam] 障害物回避: {best[2]} (視界スコア {base_sc:.2f}→{best[0]:.2f})")
        return best[1].x, best[1].y, best[1].z
    print(f"[cam] 障害物回避: 改善なし(視界スコア {base_sc:.2f})")
    return v[0], v[1], v[2]


cam_loc, cam_tgt, cam_lens, sun_az, sun_el = CAMS[args.cam]
if os.environ.get('SUN_AZ'):      # 検証用: 太陽の方位(度)を上書き
    sun_az = float(os.environ['SUN_AZ'])

# ------------------------------------------------------------------ build geometry
if args.zone == "M01":      # E7: 国都中央は kit3.m01(専用ビルダー)。穂波野(M06)は M6 で本体データ(kit3.m06)へ移行済み
    print("NOTE: --zone M01 は専用ビルダー(kit3.m01)で組みます。")
if args.zone:
    import kit4  # CURVE_OVERRIDE 等を先に確定(ワールド合成と同じ形状で組む)
    import kit2 as kit
    kit.build_zone(args.zone, yaw=0.0)
    import kit7 as _k7; print('CUTS', _k7.apply_cuts())
    import kit7 as _k7
    print('CUTS', _k7.apply_cuts())
    import veg
    veg.build_landscape(cam_loc)
    if args.zone not in ('M12', 'M13', 'L01') and os.environ.get('ZGRASS', '1') == '1':
        print('ZGRASS', veg.zone_grass(cam_loc))
    if args.zone in ("M12", "M13", "L01"):          # 雪の駅: 丘・遠景・地面を雪面に
        import re as _re, kit2 as _k2
        _k2.mats2()
        for _o in bpy.data.objects:
            if _o.type == "MESH" and _re.match(r"(hills|knoll|far_ground|kit_ground|k2_hill|k2_sand)", _o.name) and not _o.name.endswith("_forest"):   # T6: 里山の樹林(knoll_*_forest)まで雪面材にすると白い玉の山になる
                _o.data.materials.clear(); _o.data.materials.append(M["snow"])
            elif _o.type == "MESH" and _re.match(r"k2_(platA|platB|isl\d?)_top", _o.name):
                _o.data.materials.clear(); _o.data.materials.append(M["snow"])        # ホーム面に積雪
        _snow = (0.88, 0.92, 0.97)                                                   # 樹冠・草を雪化粧(約6割白)
        for _o in bpy.data.objects:
            if _o.type == "MESH" and any(c.name in ("Trees", "Vegetation") for c in _o.users_collection):
                _ca = _o.data.color_attributes.get("Col")
                if _ca is None: continue
                _n = len(_ca.data); _a = np.zeros(_n * 4, dtype=np.float32); _ca.data.foreach_get("color", _a)
                _a = _a.reshape(-1, 4)
                _top = np.random.default_rng(abs(hash(_o.name)) % 99999).uniform(0.45, 0.8, (_n, 1)).astype(np.float32)
                _a[:, :3] = _a[:, :3] * (1 - _top) + np.array(_snow, dtype=np.float32) * _top
                _ca.data.foreach_set("color", _a.ravel())
    if os.environ.get('WEATHER','1')=='1':
        import weather as _w
        print('WEATHER', _w.apply(float(os.environ.get('WEATHER_K','0.5'))))
    import zone_stock as _zs
    _zs.set_stock(True if args.stock == "on" else (False if args.stock == "off" else set(args.stock.split(","))))
    if args.interf:
        import interf
        _r = interf.run(args.zone, f"{_R}/out/interf_{args.zone}.json")
        import doorcheck, json as _j
        _bad, _nd = doorcheck.run()
        _j.dump(_bad, open(f"{_R}/out/doors_{args.zone}.json", "w"), ensure_ascii=False)
        print("DOORS", args.zone, _nd, "blocked", len(_bad), _bad[:5])
        print("INTERF", args.zone, {k: (v["n"], v["verts"]) for k, v in _r.items()})
        import floatcheck
        _f = floatcheck.run(args.zone)
        _j.dump(_f, open(f"{_R}/out/float_{args.zone}.json", "w"), ensure_ascii=False)
        import stockcheck
        _s5 = stockcheck.run(args.zone)
        _j.dump(_s5, open(f"{_R}/out/stockhit_{args.zone}.json", "w"), ensure_ascii=False)
        print("STOCKHIT", args.zone, len(_s5), list(_s5.items())[:6])
        print("FLOAT", args.zone, len(_f), list(_f.items())[:6])
if args.world:
    import kit2 as kit
    import kit4, trackkit, lib
    from props import G
    kit.mats2()
    import kit as _k
    _k.NOGROUND[0] = True
    ga = lib.Acc("world_ground", M["grass_ground"], "Ground")
    ga.box(-3400, 4600, -2600, 3400, -0.30, -0.01)
    ga.build()
    kit4.build_links()
    if os.environ.get('LINK_SCENERY', '1') != '0':        # C14: 駅間の沿線景観(柵・田畑・樹林)
        import scenery, kit2 as _k2s
        scenery.link_scenery(kit4.EDGES, kit4.struct_plan, kit4.origin, lambda sid: _k2s.DESIGN.get(sid, {}).get('town', 'urban'))
    sel = args.world
    for sid in kit4.SB:
        ox, oy = kit4.origin(sid)
        yw = kit4.yaw_of(sid)
        if sel == "bare":
            continue                      # 駅も目印も置かない(駅間の線路・構造物・沿線だけを監査用に撮る)
        if sel == "markers":
            g = G(f"mk_{sid}", "Props")
            g.a("iron_black").box(-30, 30, -6, 6, 0.0, 60)
            g.build()
            for _mo in bpy.data.objects:          # 駅位置の目印(60m の黒い直方体)は成果物ではない。影を落とさない・映り込まない(長い影が盛土や橋に黒い楔形を作っていた)
                if _mo.name.startswith(f"mk_{sid}"):
                    _mo.visible_shadow = False
            e = bpy.data.objects.new("mkz", None)
            for n in [n for n in bpy.data.objects.keys() if n.startswith(f"mk_{sid}")]:
                bpy.data.objects[n].parent = e
            e.location, e.rotation_euler = (ox, oy, 0), (0, 0, yw)
            lib.link(e, "Zones")
        elif sel == "all" or sid in sel.split(","):
            kit.TINT_ON[0] = False
            kit.build_zone(sid, origin=(float(ox), float(oy), 0.0), yaw=yw)
    import kit7 as _k7w
    print('CUTS', _k7w.apply_cuts())
    import kit7 as _k7w; print('CUTS', _k7w.apply_cuts())
    kit4.export_graph()
    kit4.world_landscape(cam_loc)
    import zone_stock as _zs2
    _zs2.set_stock(True if args.stock == "on" else (False if args.stock == "off" else set(args.stock.split(","))))
if "hq" in parts:
    import core as _c
    _c.HQ_ON = True
if "core" in parts:
    import core
    core.build_ground()
    core.build_paddies()
    core.build_tracks(cam_loc)
    core.build_platform()
    core.build_island()
    core.build_yard_crossing()
    core.build_roads()
    core.build_crossing_deck()
if "station" in parts:
    import station
    station.build_station()
if "hq" in parts:
    import hq
    hq.build_hq()
if "depot" in parts:
    import depot
    depot.build_depot(cam_loc)
    import depot_stock
    depot_stock.build_depot_stock()
if "props" in parts:
    import props
    props.build_props()
if "train" in parts:
    import train
    train.build_train()
    train.build_vehicles()
if "v2test" in parts:
    import train2, train as _tr, math as _m
    train2.extra_mats()
    train2.make_emu("e1","jnr_dc").place(0,0,0)
    train2.make_emu("e2","jnr_ac",seed=3).place(24,0,0)
    train2.make_emu("e3","ke",seed=4).place(0,6,0)
    train2.make_emu("e4","km",seed=5).place(24,6,0)
    train2.make_tram("t1").place(0,12,0)
    train2.make_mono("m1").place(24,12,0)
    _tr.make_kiha("hr1",lo="hr_yellow",up="hr_navy").place(48,0,0)
if "vtest" in parts:
    import vehtypes
    for _i, _t in enumerate(vehtypes.TYPES):
        vehtypes.make(_t, "vt_" + _t, seed=3 + _i, ends=(("gang", "tail") if _t.startswith("sl_") else (("cab", "gang") if _t == "lx_obs" else (("gang", "gang") if _t.startswith("lx_") else ("cab", "cab"))))).place(0, 30.0 * _i, 0)
    for _j, _t in enumerate(("sl_b", "sl_a", "sl_din", "sl_gen", "sl_b")):
        vehtypes.make(_t, f"sl_{_j}", seed=40 + _j, ends=("gang", "tail" if _j == 4 else "gang")).place(-70 + _j * 21.6, -12, 0)
    _lx = ["lx_obs", "lx_ste", "lx_ste", "lx_ste", "lx_lng", "lx_din", "lx_grn", "lx_ste", "lx_ste", "lx_obs"]
    for _j, _t in enumerate(_lx):
        vehtypes.make(_t, f"lx_{_j}", seed=60 + _j, ends=("cab" if _j == 0 else "gang", "cab" if _j == 9 else "gang"), pant=(_j in (1, 2, 7, 8))).place(-250 + _j * 21.55 + 10.5, -40, 0)
    for _k, _t in enumerate(("jnr_sub", "ke", "kiha_std")):
        _L = vehtypes.TYPES[_t]["L"] + 0.55
        for _j in range(3):
            vehtypes.make(_t, f"vc_{_t}_{_j}", seed=20 + _j, ends=("cab" if _j == 0 else "gang", "cab" if _j == 2 else "gang")).place(40 + _j * _L, 8.0 * _k, 0)
    if os.environ.get("VGROUND", "1") == "1":
        import lib as _lib
        _gm = _lib.mat_grass_ground("vt_ground"); _bm = _lib.mat_ballast("vt_ballast"); _rm = _lib.mat_rail("vt_rail", -0.02, 0.0)
        _g = _lib.Acc("vt_ground", _gm, "Station"); _b = _lib.Acc("vt_ballast", _bm, "Station"); _r = _lib.Acc("vt_rails", _rm, "Station"); _t = _lib.Acc("vt_ties", _lib.mat_plain("vt_tie", (0.12, 0.09, 0.07), rough=0.9), "Station")
        _g.box(-420, 260, -90, 1500, -0.62, -0.30)
        _rows = [(30.0 * _i, -140, 140) for _i in range(len(vehtypes.TYPES))] + [(-12, -80, 52), (-40, -260, -26)] + [(8.0 * _k, 36, 120) for _k in range(3)]
        for _y, _x0, _x1 in _rows:
            _b.box(_x0, _x1, _y - 1.9, _y + 1.9, -0.30, -0.12)
            for _s in (-1, 1):
                _r.box(_x0, _x1, _y + _s * 0.5335 - 0.035, _y + _s * 0.5335 + 0.035, -0.14, 0.0)
            _x = _x0
            while _x < _x1:
                _t.box(_x, _x + 0.24, _y - 1.35, _y + 1.35, -0.14, -0.02); _x += 0.62
        for _a in (_g, _b, _r, _t):
            _a.build()
if "tst" in parts:
    import tst
    tst.build()
if "veg" in parts:
    import veg
    veg.build_veg(cam_loc)
if "life" in parts or "veg" in parts:
    import life
    life.build_life(cam_loc)
print(f"[{time.time() - t0:5.1f}s] geometry built")
if args.webexport:
    import webexport
    webexport.run(set(args.webexport.split(",")))
    sys.exit(0)
if args.rig_export:
    import train as _tr
    print('rig vehicles:', _tr.export_rig(args.rig_export))
if args.stats:
    import collections
    st = collections.defaultdict(lambda: [0, 0])
    mats = collections.Counter()
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        c = o.users_collection[0].name if o.users_collection else "-"
        st[c][0] += 1
        st[c][1] += sum(len(p.vertices) - 2 for p in o.data.polygons)
        for sl in o.material_slots:
            if sl.material: mats[sl.material.name] += 1
    for c, (n, t) in sorted(st.items(), key=lambda x: -x[1][1]):
        print("STAT", c, n, "objs", t, "tris")
    print("STAT total tris", sum(v[1] for v in st.values()), "materials", len(mats))
    sys.exit(0)

# ------------------------------------------------------------------ sun + world
d = Vector((math.sin(math.radians(sun_az)) * math.cos(math.radians(sun_el)),
            math.cos(math.radians(sun_az)) * math.cos(math.radians(sun_el)),
            math.sin(math.radians(sun_el))))
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = args.sun
sun.angle = math.radians(0.55)
sun.color = (1.0, 0.92, 0.80)
sob = bpy.data.objects.new("Sun", sun)
sob.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
link(sob, "Lighting")

world = bpy.data.worlds.new("World")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
nt = world.node_tree
nt.nodes.clear()
W = lib.wrap_tree(nt)
sky = nt.nodes.new('ShaderNodeTexSky')
sky.sky_type = 'MULTIPLE_SCATTERING'
sky.sun_disc = False
sky.sun_elevation = math.radians(sun_el)
sky.sun_rotation = math.radians((180 - sun_az) % 360)
sky.air_density = args.air
sky.aerosol_density = args.aer
sky.ozone_density = 1.6
gen = nt.nodes.new('ShaderNodeTexCoord').outputs['Generated']
dx, dy, dz = W.sep(gen)
den = W.math('ADD', dz, 0.14)
px, py = W.math('DIVIDE', dx, den), W.math('DIVIDE', dy, den)
pv = W.combine(px, py, 0.0)
cover = W.ramp(W.noise(W.mapping(vec=pv, scale=(1, 1, 1), loc=(7.0, 3.0, 0)), scale=0.9, detail=3, rough=0.5, dist=0.25),
               [(0.50 + args.cloud, (0, 0, 0)), (0.70 + args.cloud, (1, 1, 1))])
cells = W.ramp(W.noise(W.mapping(vec=pv, scale=(1.0, 1.6, 1.0), loc=(2.0, 5.0, 0)), scale=5.0, detail=2, rough=0.5, dist=0.35),
               [(0.46, (0, 0, 0)), (0.60, (1, 1, 1))])
alpha = W.math('MULTIPLY', cover, cells)
alpha = W.math('MULTIPLY', alpha, W.maprange(dz, 0.03, 0.30, 0.0, 1.0))
cloud_col = W.mix(W.noise(W.mapping(vec=pv, scale=(1, 1, 1)), scale=19.0, detail=3), (1.6, 1.58, 1.52), (0.95, 0.96, 1.05))
sky_col = sky.outputs['Color'] if args.noclouds else W.mix(alpha, sky.outputs['Color'], cloud_col)
bg = nt.nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = args.sky
nt.links.new(sky_col, bg.inputs['Color'])
wout = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(bg.outputs['Background'], wout.inputs['Surface'])
if 'vtest' in parts and not os.environ.get('HDRI') and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hdri', 'autumn_field_1k.hdr')) and os.environ.get('VT_NOHDRI') != '1':
    os.environ['HDRI'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hdri', 'autumn_field_1k.hdr'); args.sun = min(args.sun, 2.0)   # 車両試験は実写HDRIの環境で撮る
if os.environ.get('HDRI'):      # HDRI=パス [HDRI_ROT=度 HDRI_STR=強さ]: 実写の屋外環境で照明・反射(車両試験用)
    _et = nt.nodes.new('ShaderNodeTexEnvironment')
    _et.image = bpy.data.images.load(os.environ['HDRI'])
    _mp = nt.nodes.new('ShaderNodeMapping'); _mp.inputs['Rotation'].default_value[2] = math.radians(float(os.environ.get('HDRI_ROT', '0')))
    _tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(_tc.outputs['Generated'], _mp.inputs['Vector']); nt.links.new(_mp.outputs['Vector'], _et.inputs['Vector'])
    nt.links.new(_et.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = float(os.environ.get('HDRI_STR', '1.0'))

# ------------------------------------------------------------------ camera
cam = bpy.data.cameras.new("Cam" + args.cam)
cam.lens = cam_lens
cam.sensor_width = 36
cam.clip_start = 0.05
cam.clip_end = 4000
if args.dof > 0:
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(cam_tgt) - Vector(cam_loc)).length
    cam.dof.aperture_fstop = args.dof
cob = bpy.data.objects.new("Cam" + args.cam, cam)
cob.location = cam_loc
cob.rotation_euler = (Vector(cam_tgt) - Vector(cam_loc)).to_track_quat('-Z', 'Y').to_euler()
link(cob, "Cameras")
scene.camera = cob

# ------------------------------------------------------------------ render settings
r = scene.render
r.engine = 'CYCLES'
bpy.context.view_layer.update()
if os.environ.get('SECTION'):      # SECTION="y,-10,-1" : 平面 y=-10 の「-1側」を切り取って断面を見る(ゾーン局所座標・ゾーン単独ビルド用)
    import bmesh
    _ax, _val, _sg = os.environ['SECTION'].split(',')
    _val, _sg = float(_val), float(_sg)
    _no = (0, 1, 0) if _ax == 'y' else ((1, 0, 0) if _ax == 'x' else (0, 0, 1))
    for _o in list(bpy.data.objects):
        if _o.type != 'MESH' or not len(_o.data.polygons):
            continue
        _bm = bmesh.new(); _bm.from_mesh(_o.data); _mw = _o.matrix_world.copy(); _bm.transform(_mw)
        _geom = list(_bm.verts) + list(_bm.edges) + list(_bm.faces)
        bmesh.ops.bisect_plane(_bm, geom=_geom, plane_co=tuple(_val * n for n in _no), plane_no=_no, clear_outer=(_sg > 0), clear_inner=(_sg < 0))
        _bm.transform(_mw.inverted()); _bm.to_mesh(_o.data); _bm.free()
    print('SECTION left polys', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'))
for _hp in [x for x in os.environ.get('HIDE_OBJ', '').split(',') if x]:   # D5c: 名前の前方一致でオブジェクトを隠す(屋根を外した庫内撮影)
    for _o in bpy.data.objects:
        if _o.name.startswith(_hp):
            _o.hide_render = True
for _hc in [x for x in os.environ.get('HIDE_COLS', '').split(',') if x]:
    for _o in (bpy.data.collections[_hc].all_objects if _hc in bpy.data.collections else []):
        _o.hide_render = True
# ---- 人物の表示/非表示(--people): 車内乗客(rig_kind=pax の子)と駅の人物(People コレクション)
_pm = args.people
_hide_cars = _pm in ("off", "station")
_hide_stn = _pm in ("off", "cars")
for _o in bpy.data.objects:
    if _hide_cars and (_o.get("rig_kind") == "pax" or (_o.parent is not None and _o.parent.get("rig_kind") == "pax")):
        _o.hide_render = True; _o.hide_viewport = True
if _hide_stn and "People" in bpy.data.collections:
    bpy.data.collections["People"].hide_render = True
    bpy.data.collections["People"].hide_viewport = True
r.resolution_x = args.w
r.resolution_y = int(args.w * 9 / 16)
r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'
r.image_settings.color_depth = '8'
cy = scene.cycles
cy.device = 'CPU'
if os.environ.get("RENDER_THREADS"):       # W6: 並列実行時に1プロセスあたりのスレッド数を固定(未指定=全コア)
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = int(os.environ["RENDER_THREADS"])
cy.samples = args.samples
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.03
cy.use_denoising = True
if os.environ.get('NODENOISE'):      # 検証用: デノイズ無し
    cy.use_denoising = False
if os.environ.get('NOADAPT'):
    cy.use_adaptive_sampling = False
try:
    cy.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
cy.max_bounces = 6
cy.diffuse_bounces = 3
cy.glossy_bounces = 3
cy.transmission_bounces = 6
cy.transparent_max_bounces = 8
cy.sample_clamp_indirect = 8.0
cy.sample_clamp_direct = 0.0
if args.hq:
    cy.adaptive_threshold = 0.008
    cy.sample_clamp_indirect = 10.0
    try:
        cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'; cy.denoising_prefilter = 'ACCURATE'
    except Exception as _e:
        print('denoise opts failed', _e)
    r.filter_size = 1.2
cy.caustics_reflective = False
cy.caustics_refractive = False
if args.draft:                       # 確認用の速い設定(最終納品は --hq)。Blender公式: バウンスを減らすとノイズも時間も減る
    cy.samples = min(cy.samples, 12)
    cy.adaptive_threshold = 0.06
    cy.max_bounces = 4; cy.diffuse_bounces = 2; cy.glossy_bounces = 2
    cy.transmission_bounces = 3; cy.transparent_max_bounces = 4
    cy.sample_clamp_indirect = 4.0     # 公式の例(間接のみクランプ 4)
if os.environ.get('MULTICAM'):
    r.use_persistent_data = True       # 同一シーンを複数カメラで撮る時、BVH等を再利用して2枚目以降を速くする(Blender公式 Performance > Persistent Data)
scene.view_settings.view_transform = 'AgX'
for look in ((os.environ["LOOK"],) if os.environ.get("LOOK") else ()) + ("Medium High Contrast", "AgX - Medium High Contrast", "High Contrast"):
    try:
        scene.view_settings.look = look
        break
    except Exception:
        continue
scene.view_settings.exposure = args.exposure
if os.environ.get("DBG_BOX"):
    _dg = bpy.context.evaluated_depsgraph_get()
    _seen = {}
    for _x in range(330, 420, 4):
        for _y in range(-115, -60, 4):
            _ok, _loc, _nm, _ix, _ob, _mx = bpy.context.scene.ray_cast(_dg, Vector((_x, _y, 60.0)), Vector((0, 0, -1)))
            if _ok and _loc.z > 2.0 and _ob is not None:
                _seen.setdefault(_ob.name, (_x, _y, round(_loc.z, 1)))
    for _k, _v in _seen.items():
        print("[DBG_RAY]", _k, _v)
if os.environ.get("DBG_BOX"):
    for _o in bpy.data.objects:
        if _o.type != 'MESH':
            continue
        _bb = [(_o.matrix_world @ Vector(_p)) for _p in _o.bound_box]
        _x0, _x1 = min(p.x for p in _bb), max(p.x for p in _bb)
        _y0, _y1 = min(p.y for p in _bb), max(p.y for p in _bb)
        for _px, _py in ((372, -100), (380, -97), (365, -97)):
            if _x0 <= _px <= _x1 and _y0 <= _py <= _y1 and (_x1 - _x0) < 120:
                print("[DBG_HIT]", _px, _py, _o.name, [round(v) for v in (_x0, _x1, _y0, _y1)], _o.parent.name if _o.parent else None)
if os.environ.get("DBG_BOX"):
    for _o in bpy.data.objects:
        _c = _o.matrix_world.translation
        if 330 < _c.x < 390 and -115 < _c.y < -85 and _o.type != 'MESH':
            print("[DBG_NONMESH]", _o.name, _o.type, [round(v) for v in _c], getattr(_o, "instance_type", None))
        if _o.type == 'MESH' and 340 < _c.x < 380 and -112 < _c.y < -88:
            print("[DBG_ORIGIN]", _o.name, [round(v, 1) for v in _c], [round(v) for v in _o.dimensions], _o.parent.name if _o.parent else None)
if os.environ.get("DBG_BOX3"):
    for _o in bpy.data.objects:
        if _o.type != 'MESH':
            continue
        _bb = [(_o.matrix_world @ Vector(_p)) for _p in _o.bound_box]
        _x0, _x1 = min(p.x for p in _bb), max(p.x for p in _bb)
        _y0, _y1 = min(p.y for p in _bb), max(p.y for p in _bb)
        _z1 = max(p.z for p in _bb)
        if _x0 < 375 and _x1 > 340 and _y0 < -88 and _y1 > -112 and _z1 > 1.0 and (_x1 - _x0) < 80 and not _o.name.startswith(("N_", "nd_")):
            print("[DBG3]", _o.name, [round(v) for v in (_x0, _x1, _y0, _y1, _z1)], _o.parent.name if _o.parent else None)
if os.environ.get("DBG_BOX4"):
    _dg = bpy.context.evaluated_depsgraph_get()
    _seen = {}
    for _x in range(330, 395, 3):
        for _y in range(-118, -82, 3):
            _ok, _loc, _nm, _ix, _ob, _mx = bpy.context.scene.ray_cast(_dg, Vector((_x, _y, 80.0)), Vector((0, 0, -1)))
            if _ok and _ob is not None:
                _seen.setdefault(_ob.name, []).append((_x, _y, round(_loc.z, 1)))
    for _k, _v in _seen.items():
        print("[DBG4]", _k, len(_v), _v[0])
if os.environ.get("DBG_GRID"):
    import lib as _lb
    _ga = _lb.Acc("dbg_grid", M["post_red"], "Props")
    for _gx in range(320, 401, 10):
        for _gy in range(-130, -69, 10):
            _ga.boxc(_gx, _gy, 6.0 + (_gx - 320) / 10.0 * 1.5, 0.5, 0.5, 12.0 + (_gx - 320) / 10.0 * 3.0)
    _ga.build()
if os.environ.get("DBG_ALL"):
    for _o in bpy.data.objects:
        try:
            _bb = [(_o.matrix_world @ Vector(_p)) for _p in _o.bound_box]
        except Exception:
            continue
        _x0, _x1 = min(p.x for p in _bb), max(p.x for p in _bb)
        _y0, _y1 = min(p.y for p in _bb), max(p.y for p in _bb)
        if _x0 < 380 and _x1 > 352 and _y0 < -91 and _y1 > -101 and (_x1 - _x0) < 200:
            print("[DBGALL]", _o.name, _o.type, [round(v) for v in (_x0, _x1, _y0, _y1)], "hv", _o.hide_viewport, "hr", _o.hide_render, "hide", _o.hide_get() if _o.name in bpy.context.view_layer.objects else None)
if os.environ.get("DBG_HALL"):
    import bmesh as _bm
    _o = bpy.data.objects.get("hall_wall")
    print("[DBGHALL] loc", tuple(round(v, 1) for v in _o.location), "parent", _o.parent.name if _o.parent else None, "verts", len(_o.data.vertices))
    _b = _bm.new(); _b.from_mesh(_o.data)
    _seen = set()
    for _v in _b.verts:
        if _v.index in _seen:
            continue
        _stack, _isl = [_v], []
        while _stack:
            _u = _stack.pop()
            if _u.index in _seen:
                continue
            _seen.add(_u.index); _isl.append(_u)
            for _e in _u.link_edges:
                _stack.append(_e.other_vert(_u))
        _w = [(_o.matrix_world @ _u.co) for _u in _isl]
        print("[DBGHALL] 島", len(_isl), [round(min(p.x for p in _w)), round(max(p.x for p in _w)), round(min(p.y for p in _w)), round(max(p.y for p in _w)), round(max(p.z for p in _w), 1)])
    _b.free()
if os.environ.get("DBG_BOX2"):
    for _o in bpy.data.objects:
        if _o.type != 'MESH' or _o.name.startswith(("N_",)):
            continue
        _bb = [(_o.matrix_world @ Vector(_p)) for _p in _o.bound_box]
        _cx = sum(p.x for p in _bb) / 8
        _cy = sum(p.y for p in _bb) / 8
        if 250 < _cx < 480 and -140 < _cy < -30 and max(_o.dimensions) > 3:
            print("[DBG_BOX]", _o.name, round(_cx), round(_cy), _o.parent.name if _o.parent else None, [round(d, 1) for d in _o.dimensions])
if os.environ.get("DBG_MAT"):      # デバッグ: マテリアル欠け(スロット無し/空/ピンク)の集計
    _nm = {}
    for _o in bpy.data.objects:
        if _o.type != "MESH" or _o.hide_render:
            continue
        _ms = [s.material for s in _o.material_slots]
        if not _ms or any(m is None for m in _ms):
            _k = _o.name.split(".")[0].rstrip("0123456789_")[:24]
            _nm[_k] = _nm.get(_k, 0) + 1
    _bad = [(i.name, i.filepath) for i in bpy.data.images if i.source == 'FILE' and (i.size[0] == 0 or not os.path.exists(bpy.path.abspath(i.filepath)))]
    print("[DBG_MAT] 画像欠け:", len(_bad), _bad[:30], "全画像", len(bpy.data.images))
    print("[DBG_MAT] マテリアル欠け:", sum(_nm.values()), sorted(_nm.items(), key=lambda t: -t[1])[:40])
if os.environ.get("DBG_BBOX"):      # デバッグ: 名前が前方一致する mesh の外接箱を出力(カメラ位置の決定用)。例 DBG_BBOX="stn_,hall,m06"
    _pf = [x for x in os.environ["DBG_BBOX"].split(",") if x]
    for _o in bpy.data.objects:
        if _o.type == "MESH" and any(_o.name.startswith(p) for p in _pf):
            _bb = [(_o.matrix_world @ Vector(_p)) for _p in _o.bound_box]
            print("[BBOX]", _o.name, [round(min(p[i] for p in _bb), 1) for i in range(3)], [round(max(p[i] for p in _bb), 1) for i in range(3)])
print(f"[{time.time() - t0:5.1f}s] scene ready; objects={len(bpy.data.objects)}")
if os.environ.get("STOCKDUMP"):      # Z-A10: 停車車両(stk_*)の外接箱と、同じ x 範囲にあるレール(trk/rail)の y 範囲を出力して、線路外置きを検出する
    import re as _re2
    for _o in bpy.data.objects:
        if _o.type == 'MESH' and _re2.match(r"stk_", _o.name) or (_o.type == 'EMPTY' and _o.name.startswith("stk_")):
            _p = _o.matrix_world.translation
            print(f"[stk] {_o.name} x={_p.x:.1f} y={_p.y:.1f} z={_p.z:.2f}")
    _rl = [(_o.name, _o) for _o in bpy.data.objects if _o.type == 'MESH' and _re2.search(r"rail|trk", _o.name, _re2.I)]
    print(f"[stk] rail objects={len(_rl)}")
if os.environ.get("MODELCHECK"):      # K8: モデル同士の干渉検査(出力 json)
    import modelcheck
    modelcheck.run(os.environ["MODELCHECK"])
    if os.environ.get("PROBE"): modelcheck.probe(os.environ["PROBE"])
    if os.environ.get("PROBE_GROUP"): modelcheck.probe_group(os.environ["PROBE_GROUP"])
    if os.environ.get("PROBE_PAIR"):
        _b = os.environ["PROBE_PAIR"].split(","); modelcheck.probe_pair(_b[0], _b[1])
    if os.environ.get("PROBE_BOX"):
        _a = os.environ["PROBE_BOX"].split(","); modelcheck.probe_box(_a[0], float(_a[1]), float(_a[2]), float(_a[3]))
if os.environ.get("DBG_RAYS"):      # デバッグ: "ox,oy,oz,tx,ty,tz;..." の線分の最初の命中オブジェクト・面法線・マテリアルを表示
    bpy.context.view_layer.update()
    _dg = bpy.context.evaluated_depsgraph_get()
    for _r in os.environ["DBG_RAYS"].split(";"):
        _v = [float(t) for t in _r.split(",")]
        _o0 = Vector(_v[:3]); _dd = (Vector(_v[3:6]) - _o0).normalized()
        _hit, _loc, _nrm, _idx, _ob, _mx = bpy.context.scene.ray_cast(_dg, _o0, _dd)
        if _hit and os.environ.get("DBG_SUNRAY"):      # 命中点から太陽方向へ再度飛ばし、日陰の原因物を特定
            _sd = Vector((math.sin(math.radians(sun_az)) * math.cos(math.radians(sun_el)), math.cos(math.radians(sun_az)) * math.cos(math.radians(sun_el)), math.sin(math.radians(sun_el))))
            _h2, _l2, _n2, _i2, _b2, _m2 = bpy.context.scene.ray_cast(_dg, _loc + _nrm * 0.05, _sd)
            print("[sunray] 日陰物:", (_b2.name, [round(c, 1) for c in _l2]) if _h2 else "なし(直射あり)", "法線·太陽 =", round(_nrm.dot(_sd), 2))
        print("[ray]", _r, "->", (_ob.name, [m.name if m else None for m in _ob.data.materials][:2], [round(c, 1) for c in _loc], [round(c, 2) for c in _nrm]) if _hit else None)
if os.environ.get("DBG_BASE"):      # デバッグ: "材質名,..." の Base Color を切り分け(DBG_BASE_MODE=tex: 最初の画像の色を直結 / flat: 灰0.3 / ao: AO入力を外す)
    _mode = os.environ.get("DBG_BASE_MODE", "tex")
    for _mn in os.environ["DBG_BASE"].split(","):
        _m = bpy.data.materials.get(_mn)
        if not _m or not _m.use_nodes:
            continue
        _nt = _m.node_tree
        _b = next(x for x in _nt.nodes if x.type == "BSDF_PRINCIPLED")
        for _l in list(_b.inputs["Base Color"].links):
            _nt.links.remove(_l)
        if _mode == "swap":
            _sm = bpy.data.materials.new("dbg_swap"); _sm.use_nodes = True
            _sm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
            for _o in bpy.data.objects:
                if _o.type == "MESH":
                    for _i, _sl in enumerate(_o.material_slots):
                        if _sl.material == _m:
                            _o.material_slots[_i].material = _sm
            print("[base]", _mn, "単純材質に置換")
            continue
        if _mode == "nobump":
            for _l in list(_b.inputs["Normal"].links):
                _nt.links.remove(_l)
            print("[base]", _mn, "法線入力を切断")
            continue
        if _mode == "tex":
            _t = next(x for x in _nt.nodes if x.type == "TEX_IMAGE")
            _nt.links.new(_t.outputs["Color"], _b.inputs["Base Color"])
        else:
            _b.inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
        print("[base]", _mn, _mode)
if os.environ.get("DBG_TREE"):      # デバッグ: 指定マテリアル名(カンマ区切り)のノード構成と入力値を表示
    for _mn in os.environ["DBG_TREE"].split(","):
        _m = bpy.data.materials.get(_mn)
        if not _m or not _m.use_nodes:
            print("[tree]", _mn, "なし"); continue
        for _n in _m.node_tree.nodes:
            _ins = []
            for _i in _n.inputs:
                if hasattr(_i, "default_value") and not _i.links and _i.name in ("Base Color", "Color", "Roughness", "Metallic", "Alpha", "Fac", "Factor", "Strength", "Emission Strength"):
                    _v = _i.default_value
                    _ins.append((_i.name, [round(c, 2) for c in _v] if hasattr(_v, "__len__") else round(_v, 2)))
            if _n.type == "TEX_IMAGE":
                _im = _n.image
                try:
                    _px = list(_im.pixels[:4000]) if _im and _im.size[0] else []
                    print("[treeimg]", _mn, _n.name, _im.name if _im else None, tuple(_im.size) if _im else None, _im.colorspace_settings.name if _im else None, "平均", round(sum(_px) / max(1, len(_px)), 3), "packed" if _im and _im.packed_file else "file", _im.filepath if _im else "")
                except Exception as _e:
                    print("[treeimg] failed", _mn, _e)
            print("[tree]", _mn, _n.name, _n.type, _ins, [(l.from_node.name, l.to_socket.name) for i in _n.inputs for l in i.links][:6])
if os.environ.get("DBG_DUP"):      # デバッグ: 名前が「X」と「X.001」で形・範囲が同じ(=二重生成)のオブジェクトを集計
    bpy.context.view_layer.update()
    import re as _r3
    _dup = {}
    for _o in bpy.data.objects:
        _m3 = _r3.match(r"(.+)\.(\d{3})$", _o.name)
        if _o.type != "MESH" or not _m3 or _m3.group(1) not in bpy.data.objects:
            continue
        _p = bpy.data.objects[_m3.group(1)]
        if _p.type == "MESH" and len(_p.data.vertices) == len(_o.data.vertices) and all(abs(x - y) < 0.01 for x, y in zip(_p.dimensions, _o.dimensions)) and (_p.matrix_world.translation - _o.matrix_world.translation).length < 0.01:
            _k = _m3.group(1)[:20]; _dup[_k] = _dup.get(_k, 0) + 1
    print("[dup] 二重オブジェクト:", sum(_dup.values()), sorted(_dup.items(), key=lambda t: -t[1])[:40])
import re as _r5
_dupn = 0
for _o in bpy.data.objects:
    _m4 = _r5.match(r"(.+)\.(\d{3})$", _o.name)
    if _m4 and _o.type == "MESH" and _m4.group(1) in bpy.data.objects:
        _p4 = bpy.data.objects[_m4.group(1)]
        if _p4.type == "MESH" and len(_p4.data.vertices) == len(_o.data.vertices) and (_p4.matrix_world.translation - _o.matrix_world.translation).length < 0.01:
            _dupn += 1
if _dupn > 200:
    print("[dup] failed: 二重生成の疑い(同位置・同頂点数の X/X.001 が %d 組)。--zone では --parts が無視される設計か確認" % _dupn)
if os.environ.get("HIDE_GROUND"):      # 断面確認用: 地面・丘・遠景を非表示にして埋没を見る
    import re as _rg
    for _o in bpy.data.objects:
        if _o.type == "MESH" and _rg.match(r"(ground|kit_ground|far_ground|hills|levees|knoll|k2_hill|nd_yard_cinder)", _o.name):
            _o.hide_render = True; _o.hide_viewport = True
if os.environ.get("DBG_COPLANAR"):   # Q19: 同一平面で重なる上向き面(差<0.004m)を面単位で検出(黒帯・黒欠けの原因)。薄い板(厚さ<0.3m)どうしだけを対象にする
    import mathutils
    from mathutils.bvhtree import BVHTree
    _sl = []
    for _o in bpy.data.objects:
        if _o.type != "MESH" or _o.hide_render or not _o.data.vertices:
            continue
        _bb = [_o.matrix_world @ mathutils.Vector(c) for c in _o.bound_box]
        _z0, _z1 = min(v.z for v in _bb), max(v.z for v in _bb)
        if _z1 - _z0 < 0.3:
            _sl.append((_o, min(v.x for v in _bb), max(v.x for v in _bb), min(v.y for v in _bb), max(v.y for v in _bb), _z1))
    _bvh = {}
    def _tree(o):
        if o.name not in _bvh:
            _bvh[o.name] = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
        return _bvh[o.name]
    _n = 0
    for _i in range(len(_sl)):
        for _j in range(_i + 1, len(_sl)):
            a, b = _sl[_i], _sl[_j]
            if abs(a[5] - b[5]) > 0.004 or min(a[2], b[2]) - max(a[1], b[1]) < 0.3 or min(a[4], b[4]) - max(a[3], b[3]) < 0.3:
                continue
            _bt, _hit = _tree(b[0]), 0
            _ms = a[0].data
            _faces = [p for p in _ms.polygons if (a[0].matrix_world.to_3x3() @ p.normal).z > 0.9]
            for p in _faces[:: max(1, len(_faces) // 40)]:
                c = a[0].matrix_world @ p.center
                loc, nrm, idx, dist = _bt.find_nearest(c, 0.004)
                if loc is not None and nrm.z > 0.9 and abs(loc.z - c.z) < 0.004 and abs(loc.x - c.x) < 0.02 and abs(loc.y - c.y) < 0.02:
                    _hit += 1
            if _hit:
                _n += 1
                if _n <= 60: print("[coplanar]", a[0].name, b[0].name, "z=%.3f" % a[5], "faces", _hit)
    print("[coplanar] total", _n)
if os.environ.get("DBG_RECT"):      # デバッグ: "x0,x1,y0,y1" の平面範囲に重なる(地上0.5m超の)オブジェクトを列挙(新設構造の干渉確認用)
    bpy.context.view_layer.update()
    _r = [float(t) for t in os.environ["DBG_RECT"].split(",")]
    for _o in bpy.data.objects:
        if _o.type != "MESH" or _o.name.startswith(("d9", "ground", "kit_ground", "far_", "hills")):
            continue
        _c = [(_o.matrix_world @ Vector(b)) for b in _o.bound_box]
        _mn = [min(v[i] for v in _c) for i in range(3)]; _mx = [max(v[i] for v in _c) for i in range(3)]
        if _mx[0] > _r[0] and _mn[0] < _r[1] and _mx[1] > _r[2] and _mn[1] < _r[3] and _mx[2] > 0.5 and (_mx[0] - _mn[0]) < 200:
            print("[rect]", _o.name, [round(v, 1) for v in _mn], [round(v, 1) for v in _mx])
if os.environ.get("DBG_NORM"):      # デバッグ: カスタム法線の有無を集計し、DBG_NORM=clear なら全メッシュの法線を作り直す
    _cn = {}
    for _o in bpy.data.objects:
        if _o.type == "MESH":
            _m = _o.data
            if getattr(_m, "has_custom_normals", False):
                _k = _o.name.split(".")[0].rstrip("0123456789_")[:20]
                _cn[_k] = _cn.get(_k, 0) + 1
                if os.environ["DBG_NORM"] == "clear":
                    bpy.context.view_layer.objects.active = _o
                    try:
                        bpy.ops.mesh.customdata_custom_splitnormals_clear()
                    except Exception as _e:
                        _m.free_normals_split() if hasattr(_m, "free_normals_split") else print("[norm] failed", _e)
    print("[norm] カスタム法線つき:", sum(_cn.values()), sorted(_cn.items(), key=lambda t: -t[1])[:25])
if os.environ.get("DBG_HIDE"):      # デバッグ: 指定オブジェクト名(部分一致)をレンダから隠して、どの物体が黒面の原因かを切り分ける
    _n = 0
    for _o in bpy.data.objects:
        if _o.type == "MESH" and any(k in _o.name for k in os.environ["DBG_HIDE"].split(",")):
            _o.hide_render = True; _n += 1
    print("[hide]", _n, "objects")
if os.environ.get("DBG_NOSHADOW"):      # デバッグ: 指定オブジェクト名(部分一致)が影を落とさないようにして、影が原因かを切り分ける
    _n = 0
    for _o in bpy.data.objects:
        if _o.type == "MESH" and any(k in _o.name for k in os.environ["DBG_NOSHADOW"].split(",")):
            _o.visible_shadow = False; _n += 1
    print("[noshadow]", _n, "objects")
if os.environ.get("DBG_MESH"):      # デバッグ: 指定メッシュ(部分一致)の面法線(上向き/下向き)・頂点範囲・面数をダンプ
    for _o in bpy.data.objects:
        if _o.type == "MESH" and any(k in _o.name for k in os.environ["DBG_MESH"].split(",")):
            _m = _o.data
            _up = sum(1 for _p in _m.polygons if _p.normal.z > 0.01); _dn = sum(1 for _p in _m.polygons if _p.normal.z < -0.01); _sd = len(_m.polygons) - _up - _dn
            _vz = [v.co.z for v in _m.vertices]
            print("[mesh]", _o.name, "faces", len(_m.polygons), "up", _up, "down", _dn, "side", _sd, "zrange", round(min(_vz), 2), round(max(_vz), 2), "smooth", any(_p.use_smooth for _p in _m.polygons))
            for _p in _m.polygons[:40]:
                print("   poly", _p.index, "n", [round(c, 2) for c in _p.normal], "c", [round(c, 1) for c in _p.center])
if os.environ.get("DBG_OBJ"):      # デバッグ: 指定オブジェクト名(部分一致)の可視性・ライトリンク・コレクション・モディファイア・UV/頂点色を表示
    for _o in bpy.data.objects:
        if _o.type == "MESH" and any(k in _o.name for k in os.environ["DBG_OBJ"].split(",")):
            _ll = _o.light_linking
            print("[obj]", _o.name, "col", [c.name for c in _o.users_collection], "vis cam/diff/spec/shadow", _o.visible_camera, _o.visible_diffuse, _o.visible_glossy, _o.visible_shadow,
                  "holdout", _o.is_holdout, "shcatch", _o.is_shadow_catcher, "recv", _ll.receiver_collection.name if _ll.receiver_collection else None, "blk", _ll.blocker_collection.name if _ll.blocker_collection else None,
                  "mods", [m.type for m in _o.modifiers], "uv", [u.name for u in _o.data.uv_layers], "attrs", [a.name for a in _o.data.attributes][:6], "scale", [round(v, 2) for v in _o.scale], "display", _o.display_type, "verts", len(_o.data.vertices), "dim", [round(v, 3) for v in _o.dimensions], "loc", [round(v, 3) for v in _o.matrix_world.translation], "parent", _o.parent.name if _o.parent else None, "mats", [m.name if m else None for m in _o.data.materials], "mesh", _o.data.name, "users", _o.data.users)
    for _l in bpy.data.objects:
        if _l.type == "LIGHT" and _l.data.type == "SUN":
            _ll = _l.light_linking
            print("[sun-dir]", [round(c, 3) for c in (_l.matrix_world.to_quaternion() @ Vector((0, 0, -1)))], "(光の進行方向)", "az/el設定", round(sun_az, 1), round(sun_el, 1)); print("[sun]", _l.name, "recv", _ll.receiver_collection.name if _ll.receiver_collection else None, "blk", _ll.blocker_collection.name if _ll.blocker_collection else None, "shadow", _l.data.use_shadow, "energy", _l.data.energy)
def _mcol(m):
    try:
        n = m.node_tree.nodes.get("Principled BSDF") or next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
        i = n.inputs["Base Color"]
        return ("link:" + i.links[0].from_node.name) if i.links else [round(v, 2) for v in i.default_value[:3]]
    except Exception:
        return "?"
if os.environ.get("DBG_NEAR"):      # デバッグ: "x,y,z,r" の球内に入るオブジェクト名とマテリアルを列挙(視界を塞ぐ黒い面などの特定用)
    _p = [float(t) for t in os.environ["DBG_NEAR"].split(",")]
    bpy.context.view_layer.update()
    for _o in bpy.data.objects:
        if _o.type != 'MESH':
            continue
        _c = [(_o.matrix_world @ Vector(b)) for b in _o.bound_box]
        _mn = [min(v[i] for v in _c) for i in range(3)]; _mx = [max(v[i] for v in _c) for i in range(3)]
        if all(_mn[i] - _p[3] <= _p[i] <= _mx[i] + _p[3] for i in range(3)):
            print("[near]", _o.name, [(m.name, _mcol(m)) for m in _o.data.materials][:2], [round(v, 1) for v in _mn], [round(v, 1) for v in _mx])

if args.tex_max:
    for im in bpy.data.images:
        try:
            if im.source == 'FILE' and max(im.size) > args.tex_max:
                k = args.tex_max / max(im.size)
                im.scale(max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k)))
        except Exception as e:
            print("scale fail", im.name, e)
if args.pack:
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print("pack failed", e)
if args.save_blend and os.environ.get('KEEP_COLS'):
    keep = set(os.environ['KEEP_COLS'].split(','))
    def _cols(c):
        yield c
        for ch in c.children: yield from _cols(ch)
    names = set()
    for c in bpy.data.collections:
        if c.name in keep:
            for cc in _cols(c): names.add(cc.name)
    kobjs = set()
    for n in names: kobjs |= set(bpy.data.collections[n].objects)
    for o in list(bpy.data.objects):
        if o not in kobjs and o.type not in ('CAMERA','LIGHT'):
            bpy.data.objects.remove(o, do_unlink=True)
    vs = os.environ.get('VEGSLICE')  # name:i/n -> keep only slice i of n (by x) of that object; other Vegetation objs: VEGONLY names
    vo = os.environ.get('VEGONLY')
    if vo:
        for o in list(bpy.data.objects):
            if o.name.split('.')[0] in ('grass_tufts','susuki','levee_grass','levee_susuki','higanbana','rice_clumps','hasa_poles','hasa_sheaves','fallen_leaves') and o.name.split('.')[0] not in vo.split(','):
                bpy.data.objects.remove(o, do_unlink=True)
    if vs:
        import bmesh
        nm, fr = vs.split(':'); i, n = map(int, fr.split('/'))
        for o in bpy.data.objects:
            if o.name.split('.')[0] == nm and o.type == 'MESH':
                bm = bmesh.new(); bm.from_mesh(o.data)
                xs = sorted(f.calc_center_median().x for f in bm.faces)
                lo = xs[len(xs)*i//n]; hi = xs[min(len(xs)-1, len(xs)*(i+1)//n)] if i < n-1 else 1e9
                bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (lo <= f.calc_center_median().x < hi)], context='FACES')
                bm.to_mesh(o.data); bm.free()
    print("KEEP", sorted(keep), len(bpy.data.objects))
if os.environ.get('LIST_COLS'):
    for c in bpy.data.collections:
        if c.name=="Vegetation":
            for o in c.objects: print("VOBJ", o.name, len(o.data.polygons))
        print("COL", c.name, len(c.objects), sum(len(o.data.polygons) for o in c.objects if o.type=='MESH'))
if args.save_blend:
    bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/{args.out}.blend", compress=True)
if args.pano:
    import json
    nodes = json.load(open(args.pano))
    cam.type = 'PANO'
    cam.panorama_type = 'EQUIRECTANGULAR'
    cam.dof.use_dof = False
    r.resolution_x = args.w
    r.resolution_y = args.w // 2
    os.makedirs(f"{OUT}/pano", exist_ok=True)
    for i, nd in enumerate(nodes):
        if i < args.pano_start:
            continue
        cob.location = (nd["x"], nd["y"], nd["z"])
        cob.rotation_euler = (math.pi / 2, 0, 0)      # forward = +Y (north), centre of image
        r.filepath = f"{OUT}/pano/{nd['id']}.png"
        bpy.ops.render.render(write_still=True)
        print("PANO done", nd["id"], f"{time.time() - t0:.0f}s", flush=True)
    sys.exit(0)
# E8: 駅別の個別カメラ(fallback で不成立だった視点)。TR02 の F は天蓋下が真っ黒になるため、通りの反対側から商店街の正面を撮る
CAM_OVERRIDE = {("TR02", "F"): [0.0, -45.0, 3.0, 0.0, -7.0, 3.0, 28]}


def _fallback_cam(k):
    """E6/M19所見: kit3/kit6 の特殊駅は kit2.DESIGN に無く、@F/@P/@T/@R/@L が全て同一の既定カメラになっていた。
    シーン内の「ホーム」メッシュ(名前に plat を含む)の外接箱から、駅ごとに異なる位置のカメラを作る。見つからなければ None。"""
    import re as _re
    xs, ys, zs = [], [], []
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and _re.search(r"plat", o.name, _re.I) and not o.hide_render:
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                xs.append(w.x); ys.append(w.y); zs.append(w.z)
    if len(xs) < 8:
        return None
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    print(f"[cam] fallback ホーム外接箱 x={x0:.1f}..{x1:.1f} y={y0:.1f}..{y1:.1f} z={min(zs):.1f}..{max(zs):.1f}")
    zp = max(1.1, max(zs) if max(zs) < 14.0 else 1.1)      # 高架駅(K03 等)はホーム面の高さに合わせる
    if k == "F":
        return [cx, y1 + 38.0, 3.0, cx, cy, zp + 2.4, 28]
    if k == "P":
        return [x0 - 18.0, cy, zp + 1.65, x1, cy, zp + 1.8, 28]
    if k == "T":
        return [cx + 55.0, y1 + 24.0, 2.2, cx - 40.0, y1 + 26.0, 3.0, 32]
    if k == "R":
        return [x1 + 18.0, y0 - 3.0, zp, x0 - 10.0, cy, zp + 0.5, 32]
    return [x0 - 30.0, cy - 14.0, 2.4, cx, cy + 12.0, zp + 5.0, 24]      # L


if not args.no_render and os.environ.get('MULTICAM'):
    _both = os.environ.get('PEOPLE_BOTH') == '1'      # 1回の構築で 人物表示/非表示 の両方を撮る(出力: <out>_<n>.png=表示, <out>_np_<n>.png=非表示)
    _pp = [o for o in bpy.data.objects if o.get("rig_kind") == "pax" or (o.parent is not None and o.parent.get("rig_kind") == "pax")]
    def _people(show):
        for _o in _pp:
            _o.hide_render = not show
        if "People" in bpy.data.collections:
            bpy.data.collections["People"].hide_render = not show
    for _i, _c in enumerate([x for x in os.environ['MULTICAM'].split(';') if x.strip()]):
        if _c.strip().startswith('@'):                  # @A のようにプリセットカメラ名で指定できる
            if _c.strip()[1:] in ("F", "P", "T", "R"):       # 駅ごとの追加カメラ: F=駅舎正面(駅前広場から) P=ホーム上の目線 T=駅前の町並み R=線路脇の低い目線
                import kit2 as _k2
                _d = _k2.DESIGN.get(getattr(args, "zone", ""))
                if _d:
                    _bx, _w, _dp = float(_d["bx"]), float(_d["w"]), float(_d["d"])
                    _cx = _bx + _w / 2.0
                    _k = _c.strip()[1:]
                    if _k == "F":
                        _v = [_cx, _dp + 30.0, 3.0, _cx, _dp * 0.5 + 2.0, 3.5, 28]
                    elif _k == "P":
                        _v = [_bx - 25.0, -4.0, 2.75, _bx + 40.0, -4.0, 2.9, 28]
                    elif _k == "T":
                        _v = [_cx + 60.0, _dp + 20.0, 2.2, _cx - 40.0, _dp + 22.0, 3.0, 32]   # 道路沿い(駅前通りの端)から通りを見通す
                    else:
                        _v = [_bx + _w + 18.0, 3.0, 1.1, _bx - 10.0, -4.0, 1.6, 32]
                else:
                    _v = CAM_OVERRIDE.get((getattr(args, "zone", ""), _c.strip()[1:])) or _fallback_cam(_c.strip()[1:]) or [*CAMS["B"][0], *CAMS["B"][1], CAMS["B"][2]]
            elif _c.strip()[1:] == "L":                       # @L: 駅の象徴物(landmark)を主題にしたカメラ(駅ごとに構図が変わる)
                import kit2 as _k2
                _lm = _k2.DESIGN.get(getattr(args, "zone", ""), {}).get("lm") or []
                if _lm:
                    _lx, _ly = float(_lm[0][1]), float(_lm[0][2])
                    _v = [_lx - 28.0, _ly - 40.0, 3.0, _lx, _ly, 9.0, 24]
                else:
                    _v = _fallback_cam("L") or [*CAMS["B"][0], *CAMS["B"][1], CAMS["B"][2]]
            else:
                _cc = CAMS[_c.strip()[1:]]
                _v = [*_cc[0], *_cc[1], _cc[2]]
            _big = {"M01": 2.6, "M06": 1.8}.get(getattr(args, "zone", ""), 1.0)   # 大規模駅は俯瞰/斜めを遠ざける
            if _big != 1.0 and _c.strip()[1:] in ("ZA", "E"):
                _v[0] *= _big; _v[1] *= _big; _v[2] *= _big
            if _c.strip()[1:] == "ZA" and getattr(args, "zone", ""):      # 俯瞰の方位を駅ごとに変え、全駅が同じ構図に見えないようにする(±50°)
                import zlib as _zl
                _ang = math.radians(((_zl.crc32(args.zone.encode()) % 11) - 5) * 10.0)
                _dx, _dy = _v[0] - _v[3], _v[1] - _v[4]
                _v[0] = _v[3] + _dx * math.cos(_ang) - _dy * math.sin(_ang)
                _v[1] = _v[4] + _dx * math.sin(_ang) + _dy * math.cos(_ang)
        else:
            _v = [float(t) for t in _c.split(',')]
        if _c.strip().startswith('@') and _c.strip()[1:] in ("A", "E", "L", "F", "P", "T", "R"):      # 構造物に視界を塞がれるカメラは横にずらす(E3 所見: M03 の A が壁で遮られた)
            _v[0], _v[1], _v[2] = _cam_clear(_v)
        cob.location = (_v[0], _v[1], _v[2])
        cob.rotation_euler = (Vector((_v[3], _v[4], _v[5])) - Vector(cob.location)).to_track_quat('-Z', 'Y').to_euler()
        cam.lens = _v[6] if len(_v) > 6 else 30
        if os.environ.get("DBG_SEG") and _i == 0:      # デバッグ: 線分(カメラ→対象)と外接箱が交差する全メッシュを列挙(非表示・レンダ時に追加された物体の検出)
            bpy.context.view_layer.update()
            _sg = [float(t) for t in os.environ["DBG_SEG"].split(",")]
            _a, _b = Vector(_sg[:3]), Vector(_sg[3:6]); _dv = _b - _a
            for _o in bpy.data.objects:
                if _o.type != "MESH":
                    continue
                _bb = [(_o.matrix_world @ Vector(_q)) for _q in _o.bound_box]
                _lo = [min(q[k] for q in _bb) for k in range(3)]; _hi = [max(q[k] for q in _bb) for k in range(3)]
                _t0, _t1 = 0.0, 1.0
                for _k in range(3):
                    if abs(_dv[_k]) < 1e-9:
                        if _a[_k] < _lo[_k] or _a[_k] > _hi[_k]:
                            _t0, _t1 = 1.0, 0.0
                        continue
                    _u0, _u1 = (_lo[_k] - _a[_k]) / _dv[_k], (_hi[_k] - _a[_k]) / _dv[_k]
                    _t0, _t1 = max(_t0, min(_u0, _u1)), min(_t1, max(_u0, _u1))
                if _t0 <= _t1 and (_hi[0] - _lo[0]) < 400:
                    print("[seg]", _o.name, "hide_render", _o.hide_render, "hide_vp", _o.hide_viewport, "cam", _o.visible_camera, "shadow", _o.visible_shadow, "col", [c.name for c in _o.users_collection], "mats", [m.name if m else None for m in _o.data.materials][:2], "bbox", [round(v, 1) for v in _lo], [round(v, 1) for v in _hi])
        if _both:
            _people(True)
        r.filepath = f"{OUT}/{args.out}_{_i}.png"
        bpy.ops.render.render(write_still=True)
        print(f"[{time.time() - t0:5.1f}s] multicam {_i} -> {r.filepath}", flush=True)
        if _both:
            _people(False)
            r.filepath = f"{OUT}/{args.out}_np_{_i}.png"
            bpy.ops.render.render(write_still=True)
            print(f"[{time.time() - t0:5.1f}s] multicam {_i} (人物なし) -> {r.filepath}", flush=True)
    sys.exit(0)
if not args.no_render:
    r.filepath = f"{OUT}/{args.out}.png"
    bpy.ops.render.render(write_still=True)
    print(f"[{time.time() - t0:5.1f}s] rendered -> {r.filepath}")
