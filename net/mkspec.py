"""駅の設備仕様(設定値)と車両基地・貨物施設の詳細仕様を、既存データから規則で導出して出力する(すべて架空の設定値)。
出力: station_spec.json / facility_spec.json   (python3 mkspec.py)"""
import json, os, re, zlib, random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
N = json.load(open("network.json")); S = {s["id"]: s for s in N["stations"]}
PG = json.load(open("plan_geo.json")); PL = json.load(open("station_plan.json")); CK = json.load(open("checks.json"))
STATUS = json.load(open("status.json"))["status"]
ELEC = N.get("elec", [])
SECT = {}
for a, b, tr, blk, v, st, note in N["sect"]:
    SECT[(a, b)] = (tr, blk, v); SECT[(b, a)] = (tr, blk, v)
CO = {s: N["lines"][N["stations"][0]["lines"][0]]["co"] for s in S}
LINE_CO = {k: v["co"] for k, v in N["lines"].items()}
UG = {"T02", "T03", "K02"}; ELV = {"K03", "B02", "SH02", "M03", "SH04"}; STREET = {"TR02"}; MONO = {"B02"}
INTERIOR_DONE = {"T02": "地下駅(改札階+ホーム階。出札窓口・改札・券売機・事務室を制作済)", "T03": "地下駅(改札階+ホーム階を制作済)", "K02": "地下駅(改札階+ホーム階を制作済)",
                 "K03": "高架駅(コンコースに改札・券売機・出札窓口・売店、高架下店舗を制作済)", "M06": "原型(駅舎・待合・事務室・改札を制作済)"}


def rnd(k): return random.Random(zlib.crc32(k.encode()))


def station_spec(sid):
    s = S[sid]; pg = PG.get(sid, {}); pl = PL.get(sid, {}); r = rnd(sid)
    feats = " ".join(s.get("features", [])) + " " + s.get("note", "")
    tracks = s.get("tracks", 1); pls = list(pg.get("pl", []))
    if not pls and sid != "F01": pls = [[1.7, 4.4]] * max(1, (tracks + 1) // 2)
    pg = dict(pg, pl=pls); npl = len(pls)
    stop = pl.get("stop", 0.0); pas = pl.get("pax", 0) or 0
    co = LINE_CO.get(s["lines"][0], "JNR")
    typ = s.get("type", "")
    # --- ホーム
    heavy = stop >= 6 or sid in ("M01", "M19", "SH08", "M06")
    kind = ("頭端式" if sid in ("M01", "M19", "SH08", "R02", "T04", "B02") and pg.get("stub", 1) else "島式/相対式") if npl else "なし(貨物)"
    if sid in UG | ELV | STREET | MONO: height = {"TR02": 300, "B02": 1100}.get(sid, 1100)
    elif typ in ("temp_halt", "lighthouse_halt", "cape_halt", "coast_halt", "branch_small") or tracks == 1: height = 760 if sid not in ("L01",) else 300
    else: height = 1100 if stop >= 3 else 920
    cars = (15 if sid == "M01" else 10 if sid in ("M19", "SH08", "M06") else 8 if heavy else 6 if stop >= 3 else 4 if tracks > 1 else 2)
    if sid in STREET: cars = 2
    if sid in MONO: cars = 4
    if sid in UG: cars = 6
    plen = cars * (20 if sid not in STREET else 13)
    plat = dict(count=npl, form=kind, length_m=plen, cars=cars, height_mm=height, widths_m=[round(y1 - y0, 1) for y0, y1 in pg.get("pl", [])],
                roof="あり(鉄骨・波板)" if (heavy or tracks >= 3) else "待合のみ" if tracks > 1 else "なし/簡易", surface="アスファルト舗装" if height >= 920 else "砂利/木製")
    # --- 出札・改札
    if sid == "M01": staff, win, gates, mach = "有人(大規模・各社独立改札)", 24, 18, 20
    elif heavy: staff, win, gates, mach = "有人(出札・改札・手荷物)", 4 + tracks, 3 + tracks // 2, 4
    elif stop >= 2.5 or tracks >= 3: staff, win, gates, mach = "有人(出札・改札)", 2, 2, 2
    elif tracks >= 2: staff, win, gates, mach = "簡易委託(出札のみ)", 1, 1, 1
    else: staff, win, gates, mach = "無人(車内精算)", 0, 0, 0
    if sid == "L01": staff = "臨時の出札所(冬季のみ)"; win = 1
    tick = dict(staff=staff, windows=win, gates=gates, machines=mach, note="券売機は昭和後期の機械式。自動改札は新線(穂波空港線)のみ" if sid.startswith("SH") else "改札は鋏による手検札" if gates else "")
    # --- 信号・保安
    a_b = [v for (a, b), v in SECT.items() if sid in (a, b)]
    block = a_b[0][1] if a_b else "自動閉塞"
    inter = ("電気連動(CTC)" if sid.startswith("SH") or sid in ("M01", "M19") else "電気連動" if tracks >= 3 else "機械連動" if tracks == 2 else "連動なし(ポイントなし/手動)")
    sig = dict(block=block, interlocking=inter, signals="色灯式信号機" if tracks >= 2 else "腕木式信号機/手信号", ats="ATS-S(設定)" if heavy else "なし")
    # --- 付帯
    am = []
    if tracks >= 2 or heavy: am += ["待合室"]
    if mach or win: am += ["公衆電話", "水飲み場"]
    if "売店" in feats or heavy or typ in ("urban_island", "urban_overpass"): am += ["売店(キオスク)"]
    if heavy or tracks >= 3: am += ["男女別トイレ", "手荷物扱所"]
    elif tracks >= 2: am += ["トイレ"]
    if "旅館" in feats or "温泉" in feats: am += ["観光案内所", "足湯"]
    if "駐輪" in feats or "自転車" in feats or typ in ("suburb_island", "rural_wood"): am += ["駐輪場"]
    if sid in UG: am += ["券売機コーナー", "案内所", "地下街接続(一部)"]
    approach = []
    if "ロータリー" in feats or heavy: approach += ["バス乗場", "タクシー乗場"]
    if sid in UG | STREET: approach += ["路面電車/バス連絡(地上出入口)"]
    if not approach: approach = ["駅前広場(小)" if tracks >= 2 else "駅前の小路"]
    # --- 電化
    el = [e for e in ELEC if sid in (e["a"], e["b"])]
    elec = el[0]["sys"] if el else ("直流600V(路面電車)" if sid in STREET else "直流750V(第三軌条/架線)" if sid in UG else "非電化")
    # --- 3D制作状況
    st = STATUS.get(sid, {})
    ck = CK.get(sid, {})
    d3 = dict(shape=ck.get("shape", ""), interior=INTERIOR_DONE.get(sid, "駅舎の内部あり(家具・待合・事務室。改札内部は未作り込み=B6で順次)" if ck.get("interior") == "あり" else "未"),
              images=ck.get("images", 0), stock=ck.get("trains", ""), audit=st.get("audit", ck.get("audit", "")), state=st.get("state", ""))
    fac = [f["id"] for f in N["fac"] if f["at"] == sid]
    return dict(platform=plat, ticket=tick, signal=sig, amenities=am, approach=approach, electric=elec, threed=d3, facilities=fac,
                structure=("地下" if sid in UG else "高架" if sid in ELV or sid in MONO else "路面" if sid in STREET else "地上"))


KIND_CAR = {"coach_depot": 18, "emu_depot": 10, "dmu_depot": 3, "loco_depot": 3, "works_depot": 6, "emu_stabling": 10, "freight_yard": 0, "container_terminal": 0, "marshalling": 0,
            "stabling": 8, "turnback": 4, "siding": 0, "maint_base": 0, "track_maint": 0, "engine_siding": 0, "tram_depot": 1, "mono_depot": 4}
STAFF = {"coach_depot": 120, "emu_depot": 90, "dmu_depot": 30, "loco_depot": 80, "works_depot": 260, "emu_stabling": 12, "freight_yard": 60, "container_terminal": 45, "marshalling": 150,
         "stabling": 6, "turnback": 2, "siding": 4, "maint_base": 25, "track_maint": 30, "engine_siding": 8, "tram_depot": 20, "mono_depot": 25}
BUILD = {"coach_depot": ["検修庫", "洗浄線", "客車仕立線", "事務所棟", "乗務員区所"], "emu_depot": ["検修庫(ピット線)", "洗浄線", "留置線群", "事務所棟", "乗務員区所"],
         "dmu_depot": ["検修庫", "給油線(軽油)", "洗浄線", "事務所"], "loco_depot": ["扇形庫", "転車台", "給水・給炭設備", "機関庫事務所", "乗務員宿泊所"],
         "works_depot": ["扇形庫", "転車台", "検修庫", "組立工場", "給水塔", "石炭台", "事務所棟", "乗務員区所"], "emu_stabling": ["留置線", "休憩所"],
         "freight_yard": ["荷役線", "貨物上屋", "貨物事務所", "計量台", "貨物ホーム"], "container_terminal": ["コンテナ荷役線", "ストラドルキャリア置場", "ガントリークレーン", "事務所"],
         "marshalling": ["仕分線群", "入換機溜", "ハンプ/信号所", "操車場事務所", "検査場"], "stabling": ["留置線"], "turnback": ["引上線"], "siding": ["専用線", "荷主設備"],
         "maint_base": ["保線詰所", "除雪車庫", "資材置場"], "track_maint": ["保線区事務所", "機械庫", "資材置場"], "engine_siding": ["機待線", "機回し線"],
         "tram_depot": ["路面電車庫", "検修場", "事務所"], "mono_depot": ["モノレール車庫", "検修庫", "洗浄設備", "事務所"]}


def fac_spec(f):
    k = f["kind"]; t = f.get("tracks", 1)
    if k in ("freight_yard", "container_terminal", "marshalling", "siding", "track_maint", "maint_base", "engine_siding"): cap = f"貨車 約{t * 18}両" if k in ("freight_yard", "marshalling", "siding", "container_terminal") else "作業用車両 数両"
    else: cap = f"{t * KIND_CAR.get(k, 6)}両"
    st = f.get("state", "")
    built = ("穂波野" in f["name"] and "車両基地" in f["name"])
    ladder = dict(tracks=t, kind=k, turntable=("転車台" in " ".join(f.get("equip", [])) or "扇形庫" in " ".join(f.get("equip", []))), shed=any("検修庫" in e or "車庫" in e or "扇形庫" in e for e in f.get("equip", [])))
    return dict(id=f["id"], capacity=cap, staff=STAFF.get(k, 10), buildings=BUILD.get(k, []), ladder=ladder, built3d=built,
                three_d=("制作済(穂波野原型・位置固定)" if built else "計画のみ(3D未制作。共通ビルダーで順次=I8)"),
                hours="24時間(検修は昼夜)" if k in ("emu_depot", "coach_depot", "works_depot", "loco_depot", "dmu_depot") else "昼間作業" if k in ("freight_yard", "container_terminal", "marshalling") else "夜間留置",
                power=("電化(架線)" if k in ("emu_depot", "emu_stabling", "tram_depot") else "非電化(ディーゼル/蒸機)" if k in ("dmu_depot", "loco_depot", "works_depot") else "-"))


if __name__ == "__main__":
    ss = {sid: station_spec(sid) for sid in S}
    json.dump(ss, open("station_spec.json", "w"), ensure_ascii=False, indent=1)
    fs = {f["id"]: fac_spec(f) for f in N["fac"]}
    json.dump(fs, open("facility_spec.json", "w"), ensure_ascii=False, indent=1)
    print(len(ss), len(fs)); print(json.dumps(ss["M06"], ensure_ascii=False)[:900])
