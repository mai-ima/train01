"""線路干渉の自動検出: 線路中心線の限界(横±LAT m, 高さ ZMIN〜ZMAX)に頂点が入る非軌道メッシュを列挙。"""
import json, math, re
import numpy as np
import bpy

OK_PAT = re.compile(r"trk|track|ballast|rail|sleeper|tie|cat[_0-9]|_cat|catenary|buffer|bufstop|_pt|turnout|switch|stk_|veh|kiha|emu|loco|wam|tora|coach|bogie|ground|terrain|sky|sun|cam|^Plane|k6_.*_via|rails|fittings|signal|sig_|pole|mast|crossing|kikyo|sleep|roadbed|embank|ditch|bed|cut|tunnel|portal|shed|k2_snow|B02_beam", re.I)
LAT = 1.6
ZMIN, ZMAX = 0.55, 4.0


def tracks_xy(sid, xr=(-160, 160), step=1.5):
    import zone_stock, kit4, kit2
    n = len(kit4.local_tracks(sid)) if sid not in kit2.DESIGN else kit2.DESIGN[sid]["ntr"]
    out = []
    try:
        lt = kit4.local_tracks(sid)
    except Exception:
        lt = []
    for k in range(n):
        pts = []
        x0, x1 = xr
        if k < len(lt) and sid not in kit2.DESIGN:
            b, f = lt[k].get("back"), lt[k].get("front")
            if b: x0 = max(x0, min(b[0], 36.0 if f is None else f[0]))
            x1 = min(x1, f[0] if f else lt[k].get("xend", 36.0))
        for x in np.arange(x0, x1, step):
            tp = zone_stock._tpoint(sid, k, float(x))
            if tp: pts.append((tp[0], tp[1]))
        if pts:
            out.append(np.array(pts))
    return out


def run(sid, path=None):
    bpy.context.view_layer.update()
    tr = tracks_xy(sid)
    if not tr:
        return {}
    allp = np.vstack(tr)
    lo, hi = allp.min(0) - 3, allp.max(0) + 3
    import zone_stock as _zs
    zr = 9.0 if sid == "B02" else _zs.SPECIAL_Z.get(sid, 0.0)   # 軌条面の高さ(高架/地下/モノレールは地面と別)
    res = {}
    PLAT = re.compile(r"plat|isl_|_pl[0-9]|k6_.*plat", re.I)
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        isplat = bool(PLAT.search(ob.name))
        if not isplat and OK_PAT.search(ob.name):
            continue
        cols = [c.name for c in ob.users_collection]
        if any(c in ("Trains", "Track") for c in cols):
            continue
        me = ob.data
        nv = len(me.vertices)
        if nv == 0:
            continue
        a = np.empty(nv * 3, np.float32)
        me.vertices.foreach_get("co", a)
        a = a.reshape(-1, 3)
        M = np.array(ob.matrix_world)
        w = a @ M[:3, :3].T + M[:3, 3]
        zmin = 0.3 if isplat else ZMIN
        lat = 1.55 if isplat else LAT
        m = (w[:, 2] > zmin + zr) & (w[:, 2] < ZMAX + zr) & (w[:, 0] > lo[0]) & (w[:, 0] < hi[0]) & (w[:, 1] > lo[1]) & (w[:, 1] < hi[1])
        if not m.any():
            continue
        w = w[m]
        hit = np.zeros(len(w), bool)
        for P in tr:
            d = np.min(np.hypot(w[:, None, 0] - P[None, :, 0], w[:, None, 1] - P[None, :, 1]), axis=1) if len(w) * len(P) < 4e7 else None
            if d is None:
                continue
            hit |= d < lat
        if hit.any():
            key = re.sub(r"[_.]?\d+$", "", ob.name)
            r = res.setdefault(key, {"n": 0, "verts": 0, "ex": ob.name, "z": float(w[hit][:, 2].max())})
            r["n"] += 1
            r["verts"] += int(hit.sum())
    if path:
        json.dump(res, open(path, "w"), ensure_ascii=False, indent=1)
    return res
