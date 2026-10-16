import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # Q8: 絶対パスを使わない
"""【C6】向きの自動検査: 軌道グラフの接続ノードで、接続する2辺の接線のなす角(直通なら0°)を測り、閾値超を列挙する。"""
import json, math, sys
g = json.load(open(_R + "/net/track_graph.json"))
E = {e["id"]: e for e in g["edges"]}


def away(e, wh):
    """ノードから辺の内側へ向かう方向角。"""
    p = e["pts"]
    a, b = (p[0], p[min(4, len(p) - 1)]) if wh == "start" else (p[-1], p[max(-5, -len(p))])
    return math.atan2(b[1] - a[1], b[0] - a[0])


bad, n = [], 0
for nd in g["nodes"]:
    es = nd["edges"]
    if len(es) < 2:
        continue
    for i in range(len(es)):
        for j in range(i + 1, len(es)):
            (a, wa), (b, wb) = es[i], es[j]
            d = abs((away(E[a], wa) - away(E[b], wb) + math.pi) % (2 * math.pi) - math.pi)
            d = min(d, math.pi - d)       # 0°=平行/分岐, 180°=直通 → どちらも折れ角0
            n += 1
            if math.degrees(d) > 12:
                bad.append((a, wa, b, wb, round(math.degrees(d), 1)))
print("検査", n, "組 / 12°超", len(bad))
for b in bad:
    print(b)
json.dump(dict(checked=n, bad=bad), open(_R + "/net/orient_graph.json", "w"), ensure_ascii=False)
