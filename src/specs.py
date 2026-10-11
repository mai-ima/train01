"""Q1: 参照スペック表(日本の狭軌・昭和期の標準的な寸法の範囲)と、シーン実測との照合。"""
import re, numpy as np, bpy
SPEC = {   # 名称: (下限, 上限, 説明)
 "gauge": (1.00, 1.12, "軌間(狭軌1.067m)"),
 "track_pitch": (3.8, 5.0, "線間隔(m)"),
 "platform_h": (0.45, 1.15, "ホーム高(m)・昭和期は低床〜1.1m"),
 "car_w": (2.6, 3.0, "車体幅(m)"),
 "car_h": (3.3, 4.3, "車体高(パンタ除く,m)・屋根上機器込み"),
 "car_l": (11.0, 21.5, "車体長(m)・路面/モノ/小型〜20m級"),
}
def measure(sid):
    bpy.context.view_layer.update()
    out = {}
    cars = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not re.match(r"stk_\d+_\d+", ob.name): continue
        if not any(c.name.startswith("Stock_") for c in ob.users_collection): continue
        if re.search(r"bogie|coupler|pant|wheel|step|hose|wiper|antenna|iron", ob.name, re.I): continue
        m = re.match(r"(stk_\d+_\d+)", ob.name)
        nv = len(ob.data.vertices)
        if not nv: continue
        a = np.empty(nv * 3, np.float32); ob.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
        M = np.array(ob.matrix_world); w = a @ M[:3, :3].T + M[:3, 3]
        cars.setdefault(m.group(1), []).append(w)
    dims = []
    for k, l in cars.items():
        W = np.vstack(l)
        # 主軸方向で長さ・幅を求める(PCA)
        xy = W[:, :2] - W[:, :2].mean(0)
        u, s, vt = np.linalg.svd(xy, full_matrices=False)
        p = xy @ vt.T
        L = float(p[:, 0].max() - p[:, 0].min()); Wd = float(p[:, 1].max() - p[:, 1].min()); H = float(W[:, 2].max() - W[:, 2].min())
        dims.append((k, round(L, 2), round(Wd, 2), round(H, 2)))
    return dims
def judge(dims):
    bad = []
    for k, L, Wd, H in dims:
        if not (SPEC["car_l"][0] <= L <= SPEC["car_l"][1]): bad.append((k, "長さ", L))
        if not (SPEC["car_w"][0] <= Wd <= SPEC["car_w"][1] + 0.4): bad.append((k, "幅", Wd))
        if not (2.9 <= H <= 5.0): bad.append((k, "高さ", H))
    return bad
