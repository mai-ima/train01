"""ゾーン内の停車車両: 駅ごとの stock(会社別)に応じ、線路上に編成を置く。リグ規約に従う(Veh.place)。
kit2.build_zone から Zone 内で呼ぶ(車両は自動的にゾーン空empty配下になる)。"""
import math
import random
import zlib


def _h(*a):
    return zlib.crc32(repr(a).encode())
import numpy as np
import kit
import kit4
import kit2
import trackkit

PITCH = 20.6
SPECIAL_Z = {"K03": 7.5}          # 軌道面の高さ
LEN = {"emu": 20.0, "tram": 12.6, "mono": 14.0}


def _kind(s):
    if "モノレール" in s: return ("mono", {})
    if "市電" in s: return ("tram", {})
    if "地下鉄" in s: return ("emu", dict(kind="km"))
    if "国都電鉄" in s: return ("emu", dict(kind="ke"))
    if "交流" in s and "電車" in s: return ("emu", dict(kind="jnr_ac"))
    if "電車" in s: return ("emu", dict(kind="jnr_dc"))
    if "山麓鉄道" in s: return ("kiha", dict(lo="maroon", up="ivory"))
    if "臨港線" in s: return ("kiha", dict(lo="hr_yellow", up="hr_navy"))
    if "ハイブリッド" in s: return ("kiha", dict(lo="jorange", up="cream"))
    if "気動車" in s: return ("kiha", dict(lo="red", up="cream"))
    if "貨物" in s or "コンテナ" in s: return ("freight", {})
    return None


def _tpoint(sid, k, x):
    """k番線の局所座標 x における (x, y, yaw)。曲線駅は中心線から求める。"""
    if sid in kit2.DESIGN and sid not in kit3_layout():
        d = kit2.DESIGN[sid]
        kc, kv = d["curve"]
        P = kit2.centerline(kc, R=kv if kc == "arc" else 0, amp=kv if kc == "S" else 0) if sid not in kit2.CURVE_OVERRIDE else kit2.centerline("arc", R=kit2.CURVE_OVERRIDE[sid], flat=False)
        ntr, plat = d["ntr"], d["plat"]
        offsets = kit2.track_offsets(plat, ntr)
        if k >= len(offsets):
            return None
        Pk = kit2.offs(P, offsets[k])
        tf, _ = trackkit.frames(Pk)
        i = int(np.argmin(np.abs(Pk[:, 0] - x)))
        return float(Pk[i, 0]), float(Pk[i, 1]), math.atan2(tf[i, 1], tf[i, 0])
    lt = kit4.local_tracks(sid)
    if k >= len(lt):
        return None
    return x, lt[k]["back"][1], 0.0


def kit3_layout():
    import kit3
    return kit3.LAYOUT


def _free_x(sid):
    """編成を置く x の中心と、頭端(車止め)があるか。"""
    lay = kit.ST[sid]["layout"]
    if sid == "T04": return 52.0 - 8, True
    if sid == "R02": return 70.0 - 8, True
    if lay.startswith("terminal_stub"): return 33.0 - 6, True
    return 0.0, False


def _consist(kindname, opt, n, seed):
    import train, train2, diesel2
    out = []
    if kindname == "emu":
        for i in range(n):
            out.append(train2.make_emu(f"stk_{seed}_{i}", seed=seed + i, **opt))
    elif kindname == "kiha":
        for i in range(n):
            out.append(train.make_kiha(f"stk_{seed}_{i}", seed=seed + i, **opt))
    elif kindname == "tram":
        out.append(train2.make_tram(f"stk_{seed}_0", seed=seed))
    elif kindname == "mono":
        for i in range(2):
            out.append(train2.make_mono(f"stk_{seed}_{i}", seed=seed + i))
    return out


def place_stock(sid):
    if sid in ("M01", "M06"):
        return 0
    import bpy
    before = set(bpy.data.objects.keys())
    n = _place_stock(sid)
    col = bpy.data.collections.get(f"Stock_{sid}") or bpy.data.collections.new(f"Stock_{sid}")
    if col.name not in [c.name for c in bpy.context.scene.collection.children_recursive]:
        parent = bpy.data.collections.get("Trains") or bpy.context.scene.collection
        try:
            parent.children.link(col)
        except RuntimeError:
            pass
    for nm in set(bpy.data.objects.keys()) - before:
        ob = bpy.data.objects[nm]
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)
        ob["stock_sid"] = sid
    col["stock_sid"] = sid
    return n


def set_stock(show):
    """show: True/False(全駅) または駅IDの集合。Stock_<SID> コレクションの表示/レンダを切替。"""
    import bpy
    for c in bpy.data.collections:
        if c.name.startswith("Stock_"):
            sid = c.name[6:]
            on = show if isinstance(show, bool) else (sid in show)
            c.hide_viewport = not on
            c.hide_render = not on


def _cfg(sid):
    """net/stock_cfg.json: {"SID": {"enabled": bool, "consists": [{"track":k,"kind":"emu|kiha|tram|mono|freight","opt":{..},"n":3,"x":0.0,"flip":false}]}}"""
    import json, os
    p = "/home/claude/station/net/stock_cfg.json"
    try:
        return json.load(open(p)).get(sid, {}) if os.path.exists(p) else {}
    except Exception as e:
        print("stock_cfg error", e)
        return {}


def _place_stock(sid):
    cfg = _cfg(sid)
    if cfg.get("enabled") is False:
        return 0
    if cfg.get("consists"):
        return _place_cfg(sid, cfg["consists"])
    return _place_auto(sid)


def _place_cfg(sid, items):
    import train, train2
    train2.extra_mats()
    zrail = 9.0 if sid == "B02" else SPECIAL_Z.get(sid, 0.0)
    placed = 0
    for it in items:
        kn, opt, k = it.get("kind", "kiha"), it.get("opt", {}), int(it.get("track", 0))
        n = int(it.get("n", 2))
        cars = _consist(kn, opt, n, seed=_h(sid, k, it.get("x", 0)) % 9000)
        L = LEN.get(kn, 20.0)
        pitch = L + 0.55
        x0 = float(it.get("x", 0.0)) - pitch * (len(cars) - 1) / 2
        for i, v in enumerate(cars):
            tp = _tpoint(sid, k, x0 + i * pitch)
            if tp is None:
                continue
            v.place(tp[0], tp[1], tp[2] + (math.pi if it.get("flip") else 0.0), z=(zrail + 0.274) if kn != "mono" else zrail)
            placed += 1
    return placed


def _place_auto(sid):
    st = kit.ST[sid]
    kinds = [_kind(s) for s in st["stock"]]
    kinds = [k for k in kinds if k]
    if not kinds:
        return 0
    import train, train2
    train2.extra_mats()
    rng = random.Random(_h(sid) % 9999)
    zrail = SPECIAL_Z.get(sid, 0.0)
    if sid == "B02": zrail = 9.0
    cx, stub = _free_x(sid)
    ntr = len(kit4.local_tracks(sid)) if sid not in kit2.DESIGN else kit2.DESIGN[sid]["ntr"]
    placed = 0
    pax = [k for k in kinds if k[0] != "freight"]
    frt = [k for k in kinds if k[0] == "freight"]
    jobs = []                                  # (track, (kind,opt))
    for i, kd in enumerate(pax):
        jobs.append((i, kd))
    if len(pax) == 1 and ntr >= 3:
        jobs.append((2, pax[0]))
    if frt:
        for j in range(max(1, min(2, ntr - len(jobs)))):
            jobs.append((len(jobs), frt[0]))
    for k, (kn, opt) in jobs:
        if k >= ntr:
            continue
        if kn == "freight":
            import diesel2
            x = cx - 25.0
            tp = _tpoint(sid, k, x)
            if tp is None: continue
            yaw0 = math.pi if rng.random() < 0.5 else 0.0
            diesel2.make_de10(f"stk_{sid}_{k}_loco").place(tp[0], tp[1], tp[2] + yaw0, z=zrail + 0.274)
            for w in range(4):
                x = cx - 25.0 + 11.0 + w * 9.9
                tp = _tpoint(sid, k, x)
                v = train.make_wam(f"stk_{sid}_{k}_w{w}", seed=w + k, load="sacks") if w % 2 == 0 else train.make_tora(f"stk_{sid}_{k}_t{w}", "coal" if (w + k) % 2 else "rice", seed=w)
                v.place(tp[0], tp[1], tp[2] + (math.pi if w % 2 else 0.0), z=zrail + 0.274)
                placed += 1
            continue
        n = 2 if ntr <= 2 or sid.startswith(("S", "Y")) else 3
        cars = _consist(kn, opt, n, seed=_h(sid, k) % 9000)
        L = LEN.get(kn, 20.0)
        pitch = L + 0.55
        tot = pitch * len(cars)
        x0 = cx - tot / 2 + pitch / 2 + (rng.uniform(-6, 6) if not stub else 0.0)
        flip = (rng.random() < 0.5) and not stub
        zr = zrail
        for i, v in enumerate(cars):
            tp = _tpoint(sid, k, x0 + i * pitch)
            if tp is None: continue
            zz = (zr + 0.274) if kn not in ("mono",) else zr
            v.place(tp[0], tp[1], tp[2] + (math.pi if flip else 0.0), z=zz)
            placed += 1
    return placed
