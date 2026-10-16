import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
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
ap.add_argument("--world", default="", help="markers | all | id,id,... : 全駅を世界座標に配置+駅間線路")
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

# ------------------------------------------------------------------ build geometry
if args.zone in ("M06", "M01"):      # E7: 穂波野・国都中央は専用の本体データがある。--zone の汎用ゾーン版で撮ると別物(新しい駅舎)になる
    print(f"WARNING: --zone {args.zone} は汎用ゾーン版です。以前作成した本体データで撮るには --zone を付けず "
          f"--parts core,station,depot,props,train,veg,hq,life (M06) を使ってください(scripts/e3b_post.sh 参照)。")
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
            if _o.type == "MESH" and _re.match(r"(hills|knoll|far_ground|kit_ground|k2_hill|k2_sand)", _o.name):
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
    sel = args.world
    for sid in kit4.SB:
        ox, oy = kit4.origin(sid)
        yw = kit4.yaw_of(sid)
        if sel == "markers":
            g = G(f"mk_{sid}", "Props")
            g.a("iron_black").box(-30, 30, -6, 6, 0.0, 60)
            g.build()
            e = bpy.data.objects.new("mkz", None)
            for n in [n for n in bpy.data.objects.keys() if n.startswith(f"mk_{sid}")]:
                bpy.data.objects[n].parent = e
            e.location, e.rotation_euler = (ox, oy, 0), (0, 0, yw)
            lib.link(e, "Zones")
        elif sel == "all" or sid in sel.split(","):
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
for look in ("Medium High Contrast", "AgX - Medium High Contrast", "High Contrast"):
    try:
        scene.view_settings.look = look
        break
    except Exception:
        continue
scene.view_settings.exposure = args.exposure
print(f"[{time.time() - t0:5.1f}s] scene ready; objects={len(bpy.data.objects)}")
if os.environ.get("MODELCHECK"):      # K8: モデル同士の干渉検査(出力 json)
    import modelcheck
    modelcheck.run(os.environ["MODELCHECK"])
if os.environ.get("DBG_NEAR"):      # デバッグ: "x,y,z,r" の球内に入るオブジェクト名とマテリアルを列挙(視界を塞ぐ黒い面などの特定用)
    _p = [float(t) for t in os.environ["DBG_NEAR"].split(",")]
    bpy.context.view_layer.update()
    for _o in bpy.data.objects:
        if _o.type != 'MESH':
            continue
        _c = [(_o.matrix_world @ Vector(b)) for b in _o.bound_box]
        _mn = [min(v[i] for v in _c) for i in range(3)]; _mx = [max(v[i] for v in _c) for i in range(3)]
        if all(_mn[i] - _p[3] <= _p[i] <= _mx[i] + _p[3] for i in range(3)):
            print("[near]", _o.name, [m.name for m in _o.data.materials][:2], [round(v, 1) for v in _mn], [round(v, 1) for v in _mx])

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
                    _v = [*CAMS["B"][0], *CAMS["B"][1], CAMS["B"][2]]
            elif _c.strip()[1:] == "L":                       # @L: 駅の象徴物(landmark)を主題にしたカメラ(駅ごとに構図が変わる)
                import kit2 as _k2
                _lm = _k2.DESIGN.get(getattr(args, "zone", ""), {}).get("lm") or []
                if _lm:
                    _lx, _ly = float(_lm[0][1]), float(_lm[0][2])
                    _v = [_lx - 28.0, _ly - 40.0, 3.0, _lx, _ly, 9.0, 24]
                else:
                    _v = [*CAMS["B"][0], *CAMS["B"][1], CAMS["B"][2]]
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
