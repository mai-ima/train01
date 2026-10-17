import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
"""【C1/D4】線路配置のリアルさ検査: 各辺の最小曲線半径(3点外接円)を求め、設計速度に対する実用下限(R >= V^2/(127*(カント+不足カント)) の簡易式)を下回るものを列挙する。"""
import json, math
g = json.load(open(_R + "/net/track_graph.json"))


def resample(p, step=12.0):
    """不等間隔の点列(端の短い区間など)で偽の急曲線が出ないよう、弧長で等間隔に取り直す。"""
    out, acc, nxt = [p[0]], 0.0, step
    for a, b in zip(p, p[1:]):
        d = math.dist(a, b)
        while acc + d >= nxt and d > 0:
            t = (nxt - acc) / d
            out.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
            nxt += step
        acc += d
    return out


def min_radius(p):
    best = 1e9
    p = resample(p)
    for i in range(1, len(p) - 1):
        a, b, c = p[i - 1], p[i], p[i + 1]
        ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
        ar = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        if ar > 1e-6:
            best = min(best, ab * bc * ca / (2 * ar))
    return best


def need(v):                       # 狭軌の標準: カント105+不足カント60 mm 相当
    return v * v / (127 * 0.165 / 1.067 * 1.067) if v else 0


bad = []
for e in g["edges"]:
    r = min_radius(e["pts"])
    v = e.get("speed_kmh") or 0
    nr = max(100.0, v * v / 20.0 / 1.0) if v else 100.0          # 90km/h→405m, 60→180m, 45→101m
    if r < nr:
        bad.append((e["id"], round(r), v, round(nr)))
print("辺", len(g["edges"]), "/ 半径不足", len(bad))
for b in bad[:40]:
    print(b)
json.dump(dict(bad=bad), open(_R + "/net/radius_check.json", "w"), ensure_ascii=False)
