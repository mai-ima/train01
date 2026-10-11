"""向き検査: ゾーンyawと、駅に接続する本線リンクの端点接線のずれ(度)を出す。"""
import json, math
g = json.load(open("geo.json"))
S = g["stations"]
bad = []
def ang(dx, dy): return math.degrees(math.atan2(dy, dx))
def diff(a, b): return abs((a - b + 180) % 360 - 180)
for L in g["links"]:
    if L["junction"] or L["k"] != 0: continue
    P = L["pts"]
    for sid, end in ((L["a"], 0), (L["b"], 1)):
        s = S[sid]
        if end == 0:
            dx, dy = P[1][0] - P[0][0], P[1][1] - P[0][1]   # 駅から外向き
        else:
            dx, dy = P[-2][0] - P[-1][0], P[-2][1] - P[-1][1]
        out = ang(dx, dy)
        yaw = s["yaw"]
        d = min(diff(out, yaw), diff(out, yaw + 180))   # 前方or後方どちらかと一致
        if d > 8: bad.append((L["line"], sid, round(d, 1), round(out), round(yaw)))
for b in bad: print("ずれ", b)
print("検査リンク端", sum(1 for L in g["links"] if not L["junction"] and L["k"] == 0) * 2, "不一致", len(bad))
