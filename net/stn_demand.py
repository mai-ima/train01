"""駅ごとの列車需要(1時間あたり・片方向)から、必要な線数・ホーム形式を算出し、現状と比較する(B4)。"""
import re, sys, json
sys.path.insert(0, "/home/claude/station/net")
from services import SVC, FREIGHT_ONLY, NONREV


def per_hour(txt):
    m = re.search(r"(\d+)分間隔", txt)
    if m:
        v = 60 / int(m.group(1))
        return v * (0.5 if "朝夕" in txt else 1)
    if "1時間1本" in txt: return 1.0
    if "1時間2本" in txt: return 2.0
    m = re.search(r"(\d+)往復", txt)
    if m:
        return int(m.group(1)) / (6 if "夜間" in txt else 16)
    return 0.3


def demand():
    D = {}
    for t in SVC:
        if t[2] in NONREV:
            continue
        h = per_hour(t[5])
        for s in t[9]:
            d = D.setdefault(s, dict(stop=0.0, pas=0.0, term=0.0, frt_stop=0.0, frt_term=0.0, svc=[]))
            stops = s in t[4]
            first, last = t[4][0] == s, t[4][-1] == s
            if t[2] == "貨物":
                if stops: d["frt_stop"] += h
                if first or last: d["frt_term"] += h
            else:
                if stops: d["stop"] += h
                else: d["pas"] += h
                if first or last: d["term"] += h
            d["svc"].append((t[0], "停" if stops else "通", round(h, 2), "始発/終着" if (first or last) else ""))
    return D


def need(d, sid=None, kind=None):   # kind: "city"=地下鉄/路面/モノレール(折返し12本/hごとに1線)
    """必要な旅客線数の目安。
    ・通過があり停車と混在→待避1線 ・始発/終着は折返し本数に応じ追加(地下鉄/路面/モノレールは折返し12本/hごと、他は5本/hごと)
    ・低頻度(停+通≦2.5本/h、折返しなし)の単線区間駅は1線で足りる(交換は隣駅で行う) ・貨物の停車/折返しは貨物線1"""
    frt = 1 if (d["frt_stop"] + d["frt_term"]) > 0 else 0
    if d["stop"] + d["pas"] <= 2.5 and d["term"] <= 1.0 and not frt:
        return 1, 0
    pax = 2
    if d["pas"] >= 2 and d["stop"] >= 3: pax += 1
    per = 12 if kind == "city" else 5
    pax += min(2, int(d["term"] // per))
    return pax, frt


def plan():
    D = demand()
    net = json.load(open("/home/claude/station/net/network.json"))
    out = {}
    for s in net["stations"]:
        i = s["id"]
        if i not in D: continue
        d = D[i]; p, f = need(d, i, "city" if set(s["lines"]) & {"KM", "TR", "BM"} else None)
        out[i] = dict(now=s["tracks"], need=p + f, pax=p, frt=f, stop=round(d["stop"], 1), pas=round(d["pas"], 1), term=round(d["term"], 1),
                      note=("増設要" if p + f > s["tracks"] else ("余裕あり" if p + f < s["tracks"] else "適正")))
    json.dump(out, open("/home/claude/station/net/station_plan.json", "w"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    net = {x["id"]: x for x in json.load(open("/home/claude/station/net/network.json"))["stations"]}
    for i, p in plan().items():
        print(i, net[i]["name"], p)
