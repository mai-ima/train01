"""視点生成: python3 vp.py EDGE_ID s side dist height  [...] → MULTICAM 文字列 (線路上の点 s[m] を、進行方向に対し side(+左/-右) dist[m] 横、height[m] 高から見る)"""
import json, sys, math
g = json.load(open('/home/claude/station/net/track_graph.json'))
E = {e['id']: e for e in g['edges']}
def one(eid, s, side, dist, h, lens=32, zt=0.0, back=0.0):
    e = E[eid]; P = e['pts']; i = min(len(P) - 2, max(0, int(s / 2.0)))
    x, y = P[i]; x2, y2 = P[i + 1]; a = math.atan2(y2 - y, x2 - x)
    nx, ny = -math.sin(a), math.cos(a)
    cx, cy = x + nx * side * dist - math.cos(a) * back, y + ny * side * dist - math.sin(a) * back
    return f"{cx:.1f},{cy:.1f},{h},{x:.1f},{y:.1f},{zt},{lens}"
if __name__ == '__main__':
    a = sys.argv[1:]
    out = []
    for k in range(0, len(a), 6):
        out.append(one(a[k], float(a[k+1]), float(a[k+2]), float(a[k+3]), float(a[k+4]), zt=float(a[k+5])))
    print(';'.join(out))
