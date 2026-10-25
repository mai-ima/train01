"""K3: 浮き検査。建物/駅施設の「グループ(名前の接頭辞)」の最下点から真下へレイを飛ばし、
自分以外の面(地面・ホーム・路盤)までの隙間が GAP を超えるものを列挙(高架など意図的な高さは名前で除外)。"""
import re, numpy as np, bpy
from mathutils import Vector
GAP = 0.2
SKIP = re.compile(r"^(bb_|kit_ground|far_|hills|knoll|stk_|veh|room_|sky|sun|cam)|(_ovnm|_via|_beam|_sig|_cat|trk|track|catenary|bridge|_over|fb_|canopy|_snow|k6_K03|k6_B02|m19_head|_quay|_pier|_poles|k2_cross|_hall|_nm|_ship|ferry|_tt|_stop|^lm$)", re.I)   # Q25: _ovnm=橋上通路の壁付け駅名板(下に面が無いのが正常。M03 の偽陽性)
def prefix(n):
    return re.split(r"[_.]", n, 1)[0] if not n.startswith("k2_") and not n.startswith("k6_") and not n.startswith("m19_") else "_".join(re.split(r"[_.]", n)[:3])
def run(sid):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    groups = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or SKIP.search(ob.name) or not ob.users_collection: continue
        if ob.users_collection[0].name not in ("Buildings", "Station", "Props"): continue
        nv = len(ob.data.vertices)
        if nv == 0: continue
        a = np.empty(nv * 3, np.float32); ob.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
        M = np.array(ob.matrix_world); w = a @ M[:3, :3].T + M[:3, 3]
        groups.setdefault(prefix(ob.name), []).append((ob.name, w))
    res = {}
    for g, lst in groups.items():
        W = np.vstack([w for _, w in lst])
        if W[:, 2].max() - W[:, 2].min() < 1.2: continue      # 薄物・小物は対象外
        zmin = float(W[:, 2].min())
        low = W[W[:, 2] < zmin + 0.05]
        pts = low[:: max(1, len(low) // 6)][:6]
        gaps = []
        names = {n for n, _ in lst}
        for p in pts:
            o = Vector((float(p[0]), float(p[1]), zmin + 0.02))
            for _ in range(4):
                ok, loc, nrm, idx, hob, mat = sc.ray_cast(dg, o, Vector((0, 0, -1)), distance=60.0)
                if not ok: gaps.append(99.0); break
                if hob.name in names:
                    o = Vector((loc.x, loc.y, loc.z - 0.01)); continue
                gaps.append(float(zmin - loc.z)); break
        if gaps and min(gaps) > GAP:
            res[g] = dict(zmin=round(zmin, 2), gap=round(min(gaps), 2), n=len(lst))
    return res
