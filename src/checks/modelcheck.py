"""【K8】モデル同士の干渉(めり込み)検査: シーン内の可視メッシュ同士で、三角形が交差する組を列挙する。
対象外(意図的な接触): 地面・草・植生・線路(バラスト/レール/枕木)・道路・水面・同一建物の部品同士(名前の先頭2要素が同じ)。
方式: ワールド座標のAABBでスイープ&プルーン → 候補ペアだけ BVHTree.overlap で三角形交差数を数える。
使い方: 環境変数 MODELCHECK=<出力json> を付けて main.py を実行(--no-render 可)。結果は標準出力にも要約。"""
import re, json, numpy as np
import bpy
from mathutils.bvhtree import BVHTree

SKIP = re.compile(r"ground|hills|knoll|grass|blade|zgrass|zsusuki|susuki|sky|sea|water|ballast|trk|track|rail|sleeper|stones|pebble|road|ribbon|apron|paddy|lev|mist|cloud|sun|world|camera|lamp|cat_|catenary|wire|k2_(plat|isl|hill|sand)|snow|veg|tree|leaf|trunk|card", re.I)

def _group(name):
    t = re.split(r"[_.]", name)
    if re.search(r"\d", t[0]) and not t[0].startswith("stk"):   # k2s15_wall / k2sf3_roof など『接頭辞+番号』は同一建物の部品(先頭トークンで束ねる)
        return t[0]
    return "_".join(t[:2]) if len(t) > 1 else t[0]

def run(out_json, min_tris=4, max_report=40):
    bpy.context.view_layer.update()
    objs = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or o.hide_viewport or o.hide_render or SKIP.search(o.name):
            continue
        me = o.data
        if len(me.polygons) == 0:
            continue
        n = len(me.vertices)
        co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3).astype(np.float64)
        M = np.array(o.matrix_world, dtype=np.float64)
        w = co @ M[:3, :3].T + M[:3, 3]
        mn, mx = w.min(0), w.max(0)
        objs.append((o.name, o, mn, mx))
    objs.sort(key=lambda t: t[2][0])
    cand = []
    for i in range(len(objs)):
        a = objs[i]
        for j in range(i + 1, len(objs)):
            b = objs[j]
            if b[2][0] > a[3][0]:
                break
            if _group(a[0]) == _group(b[0]):
                continue
            ov = np.minimum(a[3], b[3]) - np.maximum(a[2], b[2])
            if (ov > 0.03).all():
                cand.append((i, j, float(ov.min())))
    trees = {}
    def tree(k):
        if k not in trees:
            o = objs[k][1]
            dg = bpy.context.evaluated_depsgraph_get()
            # ワールド座標の三角形で木を作る(FromObject はオブジェクト空間のため、SubZone の親を持つ部品同士で誤検出した)
            oe = o.evaluated_get(dg)
            me = oe.to_mesh()
            me.calc_loop_triangles()
            n = len(me.vertices)
            co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co)
            M = np.array(oe.matrix_world, dtype=np.float64)
            wv = co.reshape(-1, 3).astype(np.float64) @ M[:3, :3].T + M[:3, 3]
            tri = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', tri)
            trees[k] = BVHTree.FromPolygons([tuple(v) for v in wv], [tuple(t) for t in tri.reshape(-1, 3)])
            oe.to_mesh_clear()
        return trees[k]
    res = []
    for i, j, mo in cand:
        try:
            pairs = tree(i).overlap(tree(j))
        except Exception as e:
            print("modelcheck failed", objs[i][0], objs[j][0], e); continue
        if len(pairs) >= min_tris:
            c = (np.maximum(objs[i][2], objs[j][2]) + np.minimum(objs[i][3], objs[j][3])) / 2
            res.append(dict(a=objs[i][0], b=objs[j][0], tris=len(pairs), min_overlap_m=round(mo, 2), at=[round(float(x), 1) for x in c]))
    res.sort(key=lambda r: -r["tris"])
    json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1)
    print(f"MODELCHECK 対象{len(objs)}オブジェクト 候補{len(cand)}組 → 干渉{len(res)}組 ({out_json})")
    for r in res[:max_report]:
        print("  干渉", r["a"], "×", r["b"], f"三角形{r['tris']} 重なり最小{r['min_overlap_m']}m 位置{r['at']}")
    return res


def probe(spec):
    """PROBE='オブジェクト名,x,y,z,r' : その球内にあるメッシュ頂点(ワールド座標)を表示する(干渉の原因部品の特定用)。"""
    name, x, y, z, r = spec.split(",")
    x, y, z, r = float(x), float(y), float(z), float(r)
    o = bpy.data.objects[name]
    M = np.array(o.matrix_world, dtype=np.float64)
    n = len(o.data.vertices)
    co = np.empty(n * 3, np.float32); o.data.vertices.foreach_get('co', co)
    w = co.reshape(-1, 3).astype(np.float64) @ M[:3, :3].T + M[:3, 3]
    m = np.linalg.norm(w - np.array([x, y, z]), axis=1) < r
    print("PROBE", name, "頂点", int(m.sum()), "bbox", w[m].min(0).round(2).tolist() if m.any() else None, w[m].max(0).round(2).tolist() if m.any() else None)


def probe_box(name, y0, y1, z1):
    """PROBE_BOX='名前,y0,y1,zmax' : y0<=y<=y1 かつ z<=zmax の頂点のbbox(橋脚など線路上にある部品の特定用)。"""
    o = bpy.data.objects[name]
    M = np.array(o.matrix_world, dtype=np.float64)
    n = len(o.data.vertices)
    co = np.empty(n * 3, np.float32); o.data.vertices.foreach_get('co', co)
    w = co.reshape(-1, 3).astype(np.float64) @ M[:3, :3].T + M[:3, 3]
    m = (w[:, 1] >= y0) & (w[:, 1] <= y1) & (w[:, 2] <= z1)
    print("PROBE_BOX", name, int(m.sum()), "頂点", w[m].min(0).round(2).tolist() if m.any() else None, w[m].max(0).round(2).tolist() if m.any() else None)


def probe_pair(na, nb, k=3):
    """PROBE_PAIR='A,B' : 2つのオブジェクトの交差三角形(ワールド座標)を k 組表示。"""
    def wt(o):
        dg = bpy.context.evaluated_depsgraph_get(); oe = o.evaluated_get(dg); me = oe.to_mesh(); me.calc_loop_triangles()
        n = len(me.vertices); co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co)
        M = np.array(oe.matrix_world, dtype=np.float64); wv = co.reshape(-1, 3).astype(np.float64) @ M[:3, :3].T + M[:3, 3]
        tri = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', tri); tri = tri.reshape(-1, 3)
        return wv, tri
    va, ta = wt(bpy.data.objects[na]); vb, tb = wt(bpy.data.objects[nb])
    A = BVHTree.FromPolygons([tuple(v) for v in va], [tuple(t) for t in ta]); B = BVHTree.FromPolygons([tuple(v) for v in vb], [tuple(t) for t in tb])
    pr = A.overlap(B)
    print("PROBE_PAIR", na, nb, len(pr))
    for i, j in pr[:k]:
        print("  A", va[ta[i]].round(2).tolist(), " B", vb[tb[j]].round(2).tolist())


def probe_group(prefixes):
    """PROBE_GROUP='k2f16,k2f17' : 接頭辞ごとにワールドbbox(建物1棟分の実寸)を表示。"""
    for pf in prefixes.split(","):
        mn = np.full(3, 1e9); mx = np.full(3, -1e9)
        for o in bpy.data.objects:
            if o.type == 'MESH' and (o.name.startswith(pf + "_") or o.name == pf):
                M = np.array(o.matrix_world, dtype=np.float64)
                co = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get('co', co)
                w = co.reshape(-1, 3).astype(np.float64) @ M[:3, :3].T + M[:3, 3]
                mn = np.minimum(mn, w.min(0)); mx = np.maximum(mx, w.max(0))
        print("PROBE_GROUP", pf, mn.round(1).tolist(), mx.round(1).tolist(), "size", (mx - mn).round(1).tolist())
