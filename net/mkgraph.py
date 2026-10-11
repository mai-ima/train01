"""実線路図データ(geo.json)と工程チェック(checks.json)を作る。bpy は使うがレンダはしない。"""
import sys, json, math, os, glob
sys.path.insert(0, "/home/claude/station")
import numpy as np
import trackkit, props, kit5
import kit4
trackkit.build_track = lambda *a, **k: None
props.pole = lambda *a, **k: None
kit5.mats5 = lambda: None
kit4.G = lambda *a, **k: type("x", (), {"build": lambda s: None})()
CAP = {}
def cap_items(P, items, zfun, nm):
    CAP[nm] = (np.asarray(P, float), items)
kit4.run_items = cap_items
rep = kit4.build_links(verbose=False)
def dec(P, step=18.0):
    Q, s = trackkit.resample(np.asarray(P, float), step)
    return [[round(float(x), 1), round(float(y), 1)] for x, y in Q]
links = []
for e in kit4.EDGES:
    nm = f"net_{e['line']}_{e['a']}_{e['b']}_{e['ka']}_{e['kb']}"
    P = np.asarray(e["pts"], float)
    Q, s = trackkit.resample(P, 1.0)
    its = []
    cp = CAP.get(nm)
    if cp:
        for kind, kw in cp[1]:
            a = kw.get("s0", kw.get("s", 0)); b = kw.get("s1", a)
            a = max(0, min(a, s[-1])); b = max(a, min(b, s[-1]))
            ss = np.linspace(a, b, max(2, int((b - a) / 10) + 1))
            pos, _ = trackkit.at_s(Q, ss)
            its.append(dict(kind=kind, s0=round(float(a)), s1=round(float(b)), pts=[[round(float(x), 1), round(float(y), 1)] for x, y in pos]))
    links.append(dict(id=e["id"], line=e["line"], a=e["a"], b=e["b"], k=e["ka"], junction=e["junction"], len=round(float(s[-1])), rmin=round(float(kit4.min_radius(P))), pts=dec(P), items=its))
sts = {}
for sid in kit4.SB:
    o = kit4.origin(sid)
    rb, rf = kit4.kit2.REACH.get(sid, (160, 160))
    sts[sid] = dict(x=round(float(o[0]), 1), y=round(float(o[1]), 1), yaw=round(math.degrees(kit4.yaw_of(sid)), 1), reach=[rb, rf],
                    bend=round(math.degrees(kit4.bend(sid)), 1), tracks=len(kit4.local_tracks(sid)), curve_R=round(abs(kit4.kit2.CURVE_OVERRIDE.get(sid, 0))))
json.dump(dict(links=links, stations=sts), open("/home/claude/station/net/geo.json", "w"), ensure_ascii=False)
# ---- 工程チェック
import kit2, kit3
st = json.load(open("/home/claude/station/net/status.json"))["status"]
chk = {}
for sid, s in kit4.SB.items():
    shape = "専用設計" if sid in kit3.BUILD else ("型別設計" if sid in kit2.DESIGN else ("原型(穂波野)" if sid == "M06" else "汎用"))
    imgs = len(glob.glob(f"/home/claude/station/tex/kit/{sid}_*.png")) if sid != "M06" else 0
    rd = os.path.exists(f"/home/claude/station/out/z_{sid}.png") or sid == "M06"
    chk[sid] = dict(shape=shape, images=imgs, render=bool(rd), track=True,
                    interior=("あり" if shape in ("専用設計", "型別設計", "原型(穂波野)", "汎用") else "-"),
                    trains=("あり" if sid == "M06" else "未"), audit=st.get(sid, {}).get("audit", "未監査"))
json.dump(chk, open("/home/claude/station/net/checks.json", "w"), ensure_ascii=False)
print(len(links), "links;", sum(len(l["items"]) for l in links), "struct items;", len(chk), "stations")
