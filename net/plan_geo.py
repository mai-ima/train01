import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # Q8: 絶対パスを使わない
"""駅の実配線(ホーム・線路のy位置[m]、駅舎側が+y)を形状コードから書き出す → net/plan_geo.json(路線図の配線略図が使う)。"""
import sys, json, re
sys.path.insert(0, _R)
import kit2, kit3
from kit2 import DESIGN, track_offsets
out = {}
for sid, d in DESIGN.items():
    plat, ntr = d["plat"], d["ntr"]
    ys = [o for o in track_offsets(plat, ntr)]
    pl = []
    if plat in ("side", "side_short", "dual", "island", "island2"): pl.append([1.7, 4.4])
    if plat == "dual": pl.append([-9.0, -6.3])
    if plat in ("island", "island2"): pl.append([-6.7, -1.7])
    if plat == "island2": pl.append([-19.7, -14.7])
    L = max(d["w"] + 34, 46) if plat != "side_short" else d["w"] + 14
    out[sid] = dict(ys=ys, pl=pl, L=L, stub=0, und=0, cross=d.get("cross", ""))
def put(sid, ys, pl, **k):
    out[sid] = dict(ys=ys, pl=pl, L=k.pop("L", 100), stub=k.pop("stub", 0), und=k.pop("und", 0), cross=k.pop("cross", ""))
put("K02", [0, -4.6, -9.2, -13.8], [[1.7, 3.6], [-17.4, -15.5]], L=100, und=1)
put("K03", [0, -8.4, -13.0], [[-6.7, -1.7]], L=110, und=1)
put("T02", [0, -8.4], [[-6.7, -1.7]], L=100, und=1)
put("T03", [0, -8.4], [[-6.7, -1.7]], L=100, und=1)
put("T04", [0, -4.6], [[1.7, 3.8], [-8.4, -6.3]], L=100, stub=1)
put("TR02", [0, 4.8], [[1.7, 3.1]], L=20, und=0)
put("R02", [0, -4.6], [[1.7, 3.8]], L=60, stub=1)
put("B02", [0, -4.6], [[-3.1, -1.5]], L=40, und=1)
m1 = kit3.m01_layout()[0]
put("M01", m1, [[a + 1.7, b - 1.7] for a, b in zip(m1[0::2], m1[1::2])], L=110, stub=1)
m19 = kit3.m19_layout()["ys"]
put("M19", m19, [[b + 1.7, a - 1.7] for a, b in zip(m19[0::2], m19[1::2])][:4], L=100, stub=1)
json.dump(out, open(_R + "/net/plan_geo.json", "w"), ensure_ascii=False)
print(len(out), sorted(out))
