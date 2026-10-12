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
SPECIAL_Z = {"K03": 7.5, "T02": -7.2, "T03": -7.2, "K02": -7.2}          # 軌道面の高さ
LEN = {"emu": 20.0, "tram": 12.6, "mono": 14.0}


def _kind(s):
    if "モノレール" in s: return ("mono", {})
    if "市電" in s: return ("tram", {})
    if "地下鉄" in s: return ("emu", dict(kind="km"))
    if "国都電鉄" in s: return ("emu", dict(kind="ke"))
    if "山麓鉄道" in s: return ("kiha", dict(kind="kiha_sr"))
    if "臨港線" in s: return ("kiha", dict(kind="kiha_hr"))
    if "ハイブリッド" in s: return ("kiha", dict(kind="kiha_hyb"))
    if "交流" in s and "電車" in s: return ("emu", dict(kind="jnr_ac"))
    if "臨時急行" in s: return ("kiha", dict(kind="kiha_exp"))
    if "特急" in s: return ("kiha", dict(kind="kiha_ltd"))     # 非電化区間の特急は気動車(電車の特急形は電化区間の国都中央のみ)
    if "近郊" in s: return ("emu", dict(kind="jnr_sub"))
    if "気動車" in s: return ("kiha", dict(kind="kiha_std"))
    if "電車" in s: return ("emu", dict(kind="jnr_dc"))
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


def _len(kn, opt):
    """編成の1両の全長(m)。"""
    if kn in ("emu", "kiha"):
        import vehtypes
        return float(vehtypes.TYPES[opt.get("kind", "jnr_dc" if kn == "emu" else "kiha_std")]["L"])
    return float(LEN.get(kn, 20.0))


def _nose2(kn, opt):
    """連結面の追加間隔(先頭の鼻は編成の外側へ伸びるだけなので 0)。"""
    return 0.0


def _consist(kindname, opt, n, seed):
    import train, train2, diesel2
    out = []
    if kindname == "emu":
        for i in range(n):
            import vehtypes
            ends = ("cab" if i == 0 else "gang", "cab" if i == n - 1 else "gang")
            out.append(vehtypes.make(opt.get("kind", "jnr_dc"), f"stk_{seed}_{i}", seed=seed + i, ends=ends, pant=(i == (1 if n >= 3 else 0)) or (n == 1)))
    elif kindname == "kiha":
        import vehtypes
        for i in range(n):
            ends = ("cab" if i == 0 else "gang", "cab" if i == n - 1 else "gang")
            out.append(vehtypes.make(opt.get("kind", "kiha_std"), f"stk_{seed}_{i}", seed=seed + i, ends=ends, pant=(i == (1 if n >= 3 else 0)) or (n == 1)))
    elif kindname == "tram":
        import vehtypes; out.append(vehtypes.make("tram_o", f"stk_{seed}_0", seed=seed, ends=("cab", "cab")))
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
        L = _len(kn, opt)
        pitch = L + 0.55 + _nose2(kn, opt)
        x0 = float(it.get("x", 0.0)) - pitch * (len(cars) - 1) / 2
        for i, v in enumerate(cars):
            tp = _tpoint(sid, k, x0 + i * pitch)
            if tp is None:
                continue
            v.place(tp[0], tp[1], tp[2] + (math.pi if it.get("flip") else 0.0), z=(zrail + 0.274) if kn != "mono" else zrail)
            placed += 1
    return placed


def _place_m19_special(kinds):
    import math as _m, kit3, train2
    L = kit3.m19_layout()
    n = 0
    for kn, opt in kinds:
        if kn == "tram":
            x, (y0, y1) = L["tr"][0][0] - 1.2, (L["tr"][0][1], L["tr"][1][1])
            import vehtypes; v = vehtypes.make("tram_o", "stk_M19_tram", seed=11, ends=("cab", "cab"))
            v.place(x, (y0 + y1) / 2.0 + 2.0, _m.pi / 2, z=0.274)
            n += 1
        elif kn == "mono":
            x, (y0, y1) = L["bm"][0][0], (L["bm"][0][1], L["bm"][1][1])
            cars = [train2.make_mono(f"stk_M19_mono{i}", seed=21 + i) for i in range(2)]
            for i, v in enumerate(cars):
                v.place(x, (y0 + y1) / 2.0 + (i - 0.5) * 14.55, _m.pi / 2, z=8.2)
                n += 1
    return n


SLEEPER_ST = {"M01": 0, "M06": 1, "M19": 0}      # 寝台特急「ほなみ」(NT1): 始発M01・機関車付替M06・終着M19


def _place_sleeper(sid, ntr, used, cx, stub):
    """寝台特急「ほなみ」: DD(公開諸元ベース)+電源車+B+食堂+A+B(最後尾)。空いている最後の線に置く。"""
    import diesel2, vehtypes
    free = [k for k in range(ntr) if k not in used]
    if not free:
        return 0
    k = free[-1]
    cars = [("sl_gen", ("gang", "gang")), ("sl_b", ("gang", "gang")), ("sl_din", ("gang", "gang")),
            ("sl_a", ("gang", "gang")), ("sl_b", ("gang", "tail"))]
    pitch = 21.0 + 0.55
    loco_l = 14.2
    tot = loco_l + 0.6 + pitch * len(cars)
    x0 = cx - tot / 2
    zr = SPECIAL_Z.get(sid, 0.0) + (9.0 if sid == "B02" else 0.0)
    n = 0
    tp = _tpoint(sid, k, x0 + loco_l / 2)
    if tp is None:
        return 0
    seed = _h(sid, 77) % 9000
    diesel2.make_dd51(f"stk_{sid}_nt1_loco", hm_holder=True).place(tp[0], tp[1], tp[2], z=zr + 0.274)
    n += 1
    for i, (t, ends) in enumerate(cars):
        tp = _tpoint(sid, k, x0 + loco_l + 0.6 + pitch * (i + 0.5))
        if tp is None:
            continue
        vehtypes.make(t, f"stk_{sid}_nt1_{i}", seed=seed + i, ends=ends).place(tp[0], tp[1], tp[2], z=zr + 0.274)
        n += 1
    return n


LUX_ST = {"M01": 2}      # 周遊列車「結」(TC1〜TC4)の停車(1日目の始発M01)


def _place_lux(sid, ntr, used, cx, stub):
    """周遊列車「結」10両(ハイブリッド自走): 展望-スイート×3-ラウンジ-食堂-特別スイート-スイート×2-展望。"""
    import vehtypes
    free = [k for k in range(ntr) if k not in used]
    if len(free) < 2:
        return 0
    k = free[-LUX_ST[sid]]
    cars = ["lx_obs", "lx_ste", "lx_ste", "lx_ste", "lx_lng", "lx_din", "lx_grn", "lx_ste", "lx_ste", "lx_obs"]
    pitch = 21.0 + 0.55
    tot = pitch * len(cars)
    x0 = cx - tot / 2
    zr = SPECIAL_Z.get(sid, 0.0)
    seed = _h(sid, 99) % 9000
    n = 0
    for i, t in enumerate(cars):
        tp = _tpoint(sid, k, x0 + pitch * (i + 0.5))
        if tp is None:
            continue
        ends = ("cab" if i == 0 else "gang", "cab" if i == len(cars) - 1 else "gang")
        vehtypes.make(t, f"stk_{sid}_yui_{i}", seed=seed + i, ends=ends, pant=(i in (1, 2, 7, 8))).place(tp[0], tp[1], tp[2], z=zr + 0.274)
        n += 1
    return n


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
    placed = 0
    if sid == "M19":     # 大湊: 市電(TR)・モノレール(BM)は別技術の線路(local_tracks の 8,9)。折れ線の座標へ直接置く
        placed += _place_m19_special(kinds)
        kinds = [k for k in kinds if k[0] not in ("tram", "mono")]
        if not kinds:
            return placed
    cx, stub = _free_x(sid)
    ntr = len(kit4.local_tracks(sid)) if sid not in kit2.DESIGN else kit2.DESIGN[sid]["ntr"]
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
        L = _len(kn, opt)
        pitch = L + 0.55 + _nose2(kn, opt)
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
    if sid in SLEEPER_ST:
        placed += _place_sleeper(sid, ntr, {k for k, _ in jobs}, cx, stub)
    if sid in LUX_ST:
        placed += _place_lux(sid, ntr, {k for k, _ in jobs}, cx, stub)
    return placed

