"""Q25: 駅間リンクの線路勾配の検査。kit4.struct_plan の prof(線路の高低)から最大勾配を求め、基準超を報告する。
基準: 国鉄在来線の本線は最大 25‰(2.5%)程度、山岳でも 35〜40‰。ここでは 35‰(3.5%)を超えるものを「急」として報告する。
使い方: python3 src/checks/gradecheck.py [作業ディレクトリ(既定: /home/claude/station)] [上限‰(既定35)]   終了コード: 0=超過なし / 1=超過あり
地下・高架・モノレールなど callable の prof(ramp_fn)も評価する。bpy が必要(kit4 の import のため)。"""
import json, os, sys
import numpy as np
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/station"
LIM = float(sys.argv[2]) if len(sys.argv) > 2 else 35.0
sys.argv = sys.argv[:1]
sys.path.insert(0, ROOT)
import bpy  # noqa: F401
import kit4, kit5
g = json.load(open(os.path.join(ROOT, "net", "track_graph.json")))
rows = []
for e in g["edges"]:
    if e.get("kind") != "link" or not e["id"].endswith("_0_0") and e.get("junction"):
        continue
    a, b = e["from_station"], e["to_station"]        # track_graph のキー名は from_station / to_station
    p = np.array(e["pts"], float)
    if len(p) < 2:
        continue
    L = float(np.hypot(*np.diff(p, axis=0).T).sum())
    try:
        prof, items = kit4.struct_plan(e["line"], a, b, L)
    except Exception as ex:
        print("gradecheck struct_plan failed", e["id"], ex)
        continue
    if not prof:
        continue
    zf = prof if callable(prof) else kit5.make_zfun(prof)
    s = np.arange(0.0, L, 1.0)
    z = np.asarray(zf(s), float)
    gr = np.abs(np.diff(z)) * 1000.0           # 1m刻みなので ‰
    rows.append((float(gr.max()), e["id"], round(L), round(float(z.max() - z.min()), 1)))
rows.sort(reverse=True)
bad = [r for r in rows if r[0] > LIM]
for gmax, i, L, dz in rows[:12]:
    print(f"{'NG' if gmax > LIM else 'OK'} {i:24s} 区間長{L:5d}m 高低差{dz:5.1f}m 最大勾配{gmax:5.1f}‰")
print(f"勾配検査: {len(rows)}区間中 {LIM:.0f}‰超 {len(bad)}件")
sys.exit(1 if bad else 0)
