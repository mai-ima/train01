"""K5: 停車車両と構造物の干渉。車両メッシュの占有格子(0.4m)に、構造物(建物・ホーム上屋・柱・小物)の頂点が入っていれば報告。"""
import re, numpy as np, bpy
CELL = 0.4
OKS = re.compile(r"trk|track|ballast|rail|sleeper|fit$|ground|terrain|sky|^cam|cat[_0-9]|catenary|buffer|stk_|veh|plat|_isl|k6_.*(plat|via)|signal|sig_|room_|floor", re.I)
def _verts(ob):
    nv = len(ob.data.vertices)
    if not nv: return None
    a = np.empty(nv * 3, np.float32); ob.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(ob.matrix_world); return a @ M[:3, :3].T + M[:3, 3]
def run(sid):
    bpy.context.view_layer.update()
    occ = {}
    for ob in bpy.data.objects:
        if ob.type == "MESH" and any(c.name.startswith("Stock_") for c in ob.users_collection):
            w = _verts(ob)
            if w is None: continue
            # 面の内部も埋めるため頂点を格子化+隣接へ膨張
            for p in np.unique(np.floor(w / CELL).astype(int), axis=0):
                occ[tuple(p)] = ob.name
    if not occ: return {}
    res = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or OKS.search(ob.name) or any(c.name.startswith("Stock_") or c.name in ("Trains", "Track", "Ground", "Terrain", "Lighting", "Cameras", "Zones") for c in ob.users_collection): continue
        w = _verts(ob)
        if w is None: continue
        w = w[(w[:, 2] > 0.4)]
        if not len(w): continue
        ks = np.floor(w / CELL).astype(int)
        hit = sum(1 for k in map(tuple, ks) if k in occ)
        if hit >= 3:
            res[ob.name] = dict(hits=hit)
    return res
