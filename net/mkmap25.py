import json
net=json.load(open("network.json"))
g=json.load(open("track_graph.json"))
# 概念図用の座標(世界座標とは独立): 穂波空港線は縦に広げて見やすくする
SX={"SH02":(622,590),"SH03":(622,626),"SH04":(622,662),"SH05":(622,698),"SH06":(622,734),"SH07":(622,770),"SH08":(622,806)}
for s in net["stations"]:
    if s["id"] in SX: s["xy"]=list(SX[s["id"]])
net["lines"]["SH"]["name"]="穂波空港線(穂波新都線)"  # lname: 愛称と正式名を併記
net["geo"]=json.load(open("geo.json"))
net["checks"]=json.load(open("checks.json"))
net["saudit"]={
 "arch":["不合格(改善中)","アーチの開口・橋脚・拱上壁は側面から読める形に作り直した(2026-10-11)。石積みの目地・色むら・川岸の取付が不足でリアルさ未達"],
 "tunnel":["不合格(改善中)","丘を大型化し草地・杉を載せて地形として自然になった。坑口の造作(扁額・翼壁・アーチ口)が簡素で未達"],
 "shed":["不合格(改善中)","門型フレーム・控え壁・谷側柱列・坑口の翼壁と垂れ壁で屋根の傾きが読める形に作り直した(2026-10-11)。コンクリの経年・雪の付着・排水の描き込みが不足で未達"],
 "truss":["不合格(改善中)","橋門構・上下横構・石積み橋台と支承を追加(2026-10-11)。リベット・塗装の経年・川岸取付が不足で厳格基準では未達"],
 "viaduct":["不合格(改善中)","RC橋脚・桁・高欄の形は成立し向きも正常(2026-10-11撮影)。起点側で町の建物が高架下に重なる干渉あり・桁の質感と排水・照明柱が不足"],
 "lc":["修正済・目視で向きOK","道路が線路に直交し、遮断機・警報機が道路の両脇に立つよう修正。質感・踏切警標などの描き込みは不足で厳格基準は未判定"],
 "river":["未監査",""],"embank":["未監査",""],"cut":["未監査",""],"over":["未監査","向き検査(C6)待ち"],"trestle":["未監査",""],"sea":["未監査",""]}
net["pg"]=json.load(open("plan_geo.json"))
net["plan"]=json.load(open("station_plan.json"))
net["struct"]=json.load(open("structures.json"))
net["sspec"]=json.load(open("station_spec.json"))
net["fspec"]=json.load(open("facility_spec.json"))
from tour import TOUR
import copy, base64, io, os
from PIL import Image
_T = copy.deepcopy(TOUR)
def _img(path, w, fmt="JPEG"):
    im = Image.open(path).convert("RGB"); im.thumbnail((w, w * 2))
    b = io.BytesIO(); im.save(b, fmt, quality=82) if fmt == "JPEG" else im.save(b, fmt)
    return "data:image/%s;base64," % fmt.lower() + base64.b64encode(b.getvalue()).decode()
_T["imgs"] = []
for p, cap, w in _T.get("img_src", []):
    fp = os.path.join(os.path.dirname(__file__), "..", p)
    if os.path.exists(fp):
        _T["imgs"].append([_img(fp, w), cap])
net["tour"]=_T
from v25_news import NEWS
import copy as _cp
_N = _cp.deepcopy(NEWS); _N["imgs"] = []
for p, cap, w in _N.pop("img_src"):
    fp = os.path.join(os.path.dirname(__file__), "..", p)
    if os.path.exists(fp):
        _N["imgs"].append([_img(fp, w), cap])
net["news"] = _N
net["meta"]={"edges":len(g["edges"]),"nodes":len(g["nodes"]),"stops":len(g["stops"])}
html=open("map_tmpl_v25.html").read().replace("__NET__",json.dumps(net,ensure_ascii=False))
open("routemap.html","w").write(html)
open("routemap_v25.html","w").write(html)
print(len(html))
