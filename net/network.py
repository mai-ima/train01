import json
# ---------------------------------------------------------------- companies / lines
COMP = {
 "JNR": {"name":"国鉄","color":"#2f9e6b"},
 "KE":  {"name":"国都電鉄","color":"#d9433f"},
 "SR":  {"name":"山麓鉄道","color":"#e8962a"},
 "KM":  {"name":"国都地下鉄","color":"#3b7bd9"},
 "HR":  {"name":"汐見臨港鉄道","color":"#8e5bd0"},
 "TR":  {"name":"大湊市電","color":"#c9a227"},
 "BM":  {"name":"湾岸高速鉄道","color":"#12a3b4"},
}
ELEC=[{"line":"HM","a":"M01","b":"M05","sys":"直流1500V"},{"line":"SH","a":"SH04","b":"SH08","sys":"交流20kV 50Hz(最新方式)"}]
from facilities import FAC, KIND as FACKIND

JP = {
 "layout": { "dual_island_turnback":"相対式+島式3線(電車折返し線)","island_junction_branch":"島式+分岐線3線(かやま分岐)","island_passing":"島式1面2線+通過線","dual_island_passing":"相対式+島式3線(通過・待避)","island2_through":"島式2面4線(引上線つき)","underground_side_passing":"地下・相対式2面4線(急行通過線)","elevated_island_turnback":"高架・島式+折返し線","tram_stop_double":"路面電停(2線)","island_newtown_cherry":"島式1面2線(桜台)","overpass_two_sides_newtown":"橋上駅・2面2線+通過線","side_dual_passing":"相対式2面3線(待避線)","island_campus":"島式1面2線(学園)","island_freight_logistics":"島式+貨物着発線","side_dual_opposed_airport":"相対式2面2線","island_airport_through":"島式1面2線・通過形(引上線つき)","elevated_island":"高架・島式","freight_yard_8":"貨物ヤード(荷役8線)","honamino_four_tracks":"4線・島式+片面(基準配線)","honamino_six_tracks":"6線・島式+片面+留置側線2線(D10: 第5・第6線を増設)","island2":"島式1面2線","island_plus_side_branch":"島式+分岐側ホーム","island_plus_side_port":"島式+臨港側ホーム","island_port_yard":"島式+貨物ヤード","island_summit":"島式(最高地点)","island_wye_branch":"島式・支線分岐","monorail_elevated":"モノレール高架","overpass_station_two_sides":"橋上駅・2面4線","side_dual_opposed":"相対式2面3線","side_single":"単式1面","side_single_bridge":"単式(鉄橋脇)","side_single_plus_passing":"単式+行違い島式","side_snowshed_full":"単式(全長雪よけ)","side_windbreak":"単式(風除け壁)","side_with_banking_siding":"単式+補機側線","surface_terminal":"地上終端","temp_halt_side":"臨時・仮設ホーム","temp_side_cliff":"臨時・断崖ホーム","terminal_pier":"桟橋終端","terminal_stub1":"頭端1線","terminal_stub10":"櫛形10面","terminal_stub20":"櫛形24線(超大規模)","tram_stop":"路面電停","underground_island":"地下・島式","underground_side":"地下・相対式"},
 "building": {"rc_overpass_newtown":"RC橋上駅舎(新線)","rc_cherry_station":"RC駅舎(桜台)","rc_complex_shopping":"RC商業ビル直結駅","campus_glass_hall":"ガラスホールの駅舎","prefab_steel_logistics":"鉄骨プレハブ駅舎","concrete_box_airport":"RC箱形駅舎","airport_terminal_link":"空港ターミナル直結駅","art_deco_concrete_grand_with_glass":"アールデコ風RC大駅舎+ガラス","brick_warehouse_style_station":"煉瓦倉庫風駅舎","concrete_box_small":"RC箱形の小駅舎","concrete_snow_shelter_station":"RC雪よけシェルタ駅舎","concrete_two_story_with_tower":"RC二層+塔屋","freight_shed_steel_and_brick":"貨物上屋(煉瓦+鉄骨)","highland_wood_terminal":"高原の木造終着駅舎","log_cabin_halt":"丸太小屋","log_station_forest":"丸太造の駅舎","marble_subway":"大理石張り地下駅","monorail_terminal":"モノレール高架駅舎","portal_station":"ポータル駅舎","redbrick_grand_hall+glass_concourse":"赤煉瓦大駅舎+ガラスコンコース","station_over_tracks_concrete":"RC橋上駅舎","steel_truss_bridge_halt":"鉄橋脇の鉄骨小屋","steel_viaduct_station":"鉄骨高架駅","stone_base_wood_upper":"石積み基礎+木造","tile_subway":"タイル張り地下駅","timber_halt_on_cliff":"断崖の木造待合","timber_platform_with_tin_shelter":"木製ホーム+トタン待合","timber_snowshed_long":"木造雪よけ(全長)","tram_shelter":"電停待合","underground_concourse_tiled":"タイル張り地下コンコース","wharf_shed_station":"桟橋の上屋駅","windbreak_brick_halt":"煉瓦風除けの小駅","wood_gable_shed_waiting":"木造切妻+別棟待合","wood_gable_small_raw":"素木・小切妻駅舎","wood_halt_in_orchard":"果樹園の木造待合","wood_hip_roof_two_story_annex":"木造寄棟・二層別棟","wood_inn_style_station_onsen":"旅館風の木造二層駅舎","wood_onsen_hut_terminal":"木造の小屋駅舎","wood_raw_long_gable_hq_annex":"素木・長大切妻+本社別棟","wood_two_gable_junction":"木造二連切妻(分岐駅)","wood_waterfall_view_halt":"滝見の木造待合","wood_with_signal_tower":"木造駅舎+信号扱所"},
 "cross": {"concourse_overhead":"頭上コンコース","concourse_underpass":"地下コンコース","covered_passage":"屋根付き通路","footbridge_steel":"鉄骨跨線橋","footbridge_steel_through":"鉄骨跨線橋(通り抜け)","footbridge_wood":"木造跨線橋","footbridge_wood_covered":"屋根付き木造跨線橋","footpath":"構内通路","footpath_crossing":"構内踏切","level_crossing_and_underpass":"踏切+地下道","level_crossing_board":"踏切板","level_crossing_gates":"遮断機付き踏切","none":"なし","none_crossing_boards":"なし(踏切板のみ)","overbridge_building":"橋上駅舎","overbridge_with_shops":"店舗つき跨線橋","pier_deck":"桟橋デッキ","stairs":"階段","stairs_elevator":"階段・エレベーター","stairs_in_shelter":"シェルタ内階段","stairs_to_slope":"斜面への階段","steps_down_to_beach":"浜への階段","stone_steps":"石段","street":"道路横断","underpass_only":"地下通路のみ","underpass_stone":"石造地下道"},
}
COMPX = {
 "JNR":{"hq":"穂波野(国鉄本社)","founded":"1887年(穂波野〜かやま2.7km、国鉄発祥)","gauge":"1067mm","power":"電化: 国都中央〜みずほ(架空線1500V)/他は非電化","fleet":["特急・急行型(電車・気動車)","近郊・通勤電車","キハ系気動車","DD/DE形ディーゼル機関車","D51・C57型蒸気機関車(保存・補機)","貨車(ワム・コキ・ホキ他)","試作車・開発中の列車(穂波野)"]},
 "KE":{"hq":"国都中央","founded":"1928年(新田橋接続時)","gauge":"1067mm","power":"架空線1500V","fleet":["3000系電車(独自)","直通用: 国鉄線内対応装備","地下鉄1000系と共通運用"]},
 "SR":{"hq":"山辺","founded":"1912年","gauge":"1067mm","power":"非電化","fleet":["キハ200形気動車(独自)","貨物用小型機関車"]},
 "KM":{"hq":"国都中央","founded":"1957年","gauge":"1067mm","power":"架空線1500V(国都電鉄と規格統一)","fleet":["1000系電車(独自)"]},
 "HR":{"hq":"汐見","founded":"1935年","gauge":"1067mm","power":"非電化","fleet":["小型気動車","DLの貨物列車","客車(2軸・ボギー)"]},
 "TR":{"hq":"大湊","founded":"1948年","gauge":"1372mm","power":"架空線600V","fleet":["単車","ボギー電車"]},
 "BM":{"hq":"大湊","founded":"1964年","gauge":"跨座式(軌道桁)","power":"第三軌条(側面集電)","fleet":["モノレール4両編成"]},
}
INFO = {
 "JNR":"本社:穂波野。発祥:1887年穂波野〜かやま。軌間1067mm。国鉄全線の中心。",
 "KE":"本社:国都中央。軌間1067mm・架空線1500V。新田橋で国鉄へ直通し、みずほまで乗入れ。港町で地下鉄と相互直通。",
 "SR":"本社:山辺。軌間1067mm・非電化。山辺から穂波野まで国鉄へ直通(気動車)。",
 "KM":"本社:国都中央。軌間1067mm・架空線1500V(国都電鉄と規格統一のため架空線式に変更)。港町〜国都中央で国都電鉄と相互直通。",
 "HR":"本社:汐見。軌間1067mm・非電化。汐見で国鉄と駅を接するが線路は接続せず直通・乗入れなし。",
 "TR":"本社:大湊。軌間1372mm(国鉄と異なる)。路面電車。大湊で国鉄駅前に電停を置くが接続・直通なし。",
 "BM":"本社:大湊。跨座式モノレール・高架。大湊で国鉄駅に隣接するが直通なし。",
}
LINES = {
 "HM": {"co":"JNR","name":"穂波本線","color":"#2f9e6b","kind":"幹線(電化は国都中央〜みずほ。穂波野が起点の本社駅)"},
 "SH": {"co":"JNR","name":"穂波空港線","official":"穂波新都線","color":"#9bc53d","kind":"新設支線(愛称: 穂波空港線／正式名: 穂波新都線・1973年開業・CTC)。部分電化: 新都中央〜穂波空港のみ交流20kV 50Hz(最新方式)、かやま〜新都中央は非電化"},
 "YB": {"co":"JNR","name":"湯の里支線","color":"#7bcf9c","kind":"支線(非電化)"},
 "KE": {"co":"KE","name":"国都電鉄本線","color":"#d9433f","kind":"私鉄(架線電化)"},
 "SR": {"co":"SR","name":"山麓線","color":"#e8962a","kind":"ローカル私鉄(非電化)"},
 "KM": {"co":"KM","name":"地下鉄1号線","color":"#3b7bd9","kind":"地下鉄(架空線式1500V・国都電鉄と規格統一)"},
 "HR": {"co":"HR","name":"臨港線","color":"#8e5bd0","kind":"港湾貨客線(非電化・国鉄と線路接続なし)"},
 "TR": {"name":"1系統","co":"TR","color":"#c9a227","kind":"路面電車(軌間1372mm・国鉄と接続なし)"},
 "BM": {"co":"BM","name":"湾岸線","color":"#12a3b4","kind":"跨座式モノレール(高架・国鉄と接続なし)"},
}
# ---------------------------------------------------------------- stations: id, name, kana, line(s), km along its main line, schematic xy, type, notes
S = [
 # JNR main line (km from 国都中央)
 ("M01","国都中央","こくとちゅうおう","HM,KE,KM",0.0,(90,500),"megaterminal","超大規模駅都市。国鉄・国都電鉄・地下鉄が乗り入れる首都側の終着駅(国鉄本社は穂波野へ)。"),
 ("M02","国都南","こくとみなみ","HM",3.2,(175,500),"urban_island","住宅地に近い島式ホームの駅。"),
 ("F01","国都貨物","こくとかもつ","HM",5.0,(218,500),"freight_yard","貨物専用駅。コンテナ・石炭・鮮魚の取扱い、荷役線と留置線。"),
 ("M03","新田橋","にったばし","HM,KE",6.8,(260,500),"urban_overpass","国都電鉄と接続。国都電鉄の直通列車が国鉄線へ乗り入れる。"),
 ("M04","川原","かわら","HM",10.5,(345,500),"suburb_island","みずほまで続く電化区間の途中駅。"),
 ("M05","みずほ","みずほ","HM",14.1,(430,500),"rural_wood","穂波野の隣駅。電化区間の終点(国都電鉄の直通電車が折り返す)。"),
 ("M06","穂波野","ほなみの","HM",16.9,(515,500),"honamino","国鉄本社所在駅。国鉄発祥の地(初の営業区間・初代機関庫・起点0哩標)。木造駅舎、4線、車両基地併設(基準駅)。"),
 ("M07","かやま","かやま","HM,SH",19.6,(600,500),"junction_wood","穂波野の隣駅。1973年から穂波空港線が分岐する。"),
 ("M08","山辺","やまべ","HM,SR",23.4,(685,500),"junction_wood","山麓鉄道と接続。山麓鉄道の気動車が国鉄線へ乗り入れる。"),
 ("M09","杉ノ原","すぎのはら","HM",27.0,(770,500),"rural_wood","杉林の中の無人駅。"),
 ("M10","湯の里","ゆのさと","HM,YB",31.2,(890,440),"junction_onsen","湯の里支線の分岐駅。温泉街。"),
 ("M11","峠下","とうげした","HM",35.5,(950,380),"mountain","峠の登り口、補機連結駅。"),
 ("M12","高嶺","たかね","HM",39.8,(1010,320),"summit","最高地点。トンネルの手前。"),
 ("M13","雪見","ゆきみ","HM",44.0,(1010,235),"mountain","雪よけの屋根つき駅。"),
 ("L01","雪見スキー場前","ゆきみすきーじょうまえ","HM",46.8,(1010,192),"temp_halt","冬季のみ営業の臨時乗降場(スキー臨)。"),
 ("M14","北浦","きたうら","HM",49.5,(1010,150),"port_through","北浦漁港の駅。貨物ヤードあり。旧終着駅で先へ延伸された。"),
 ("M15","磯辺","いそべ","HM",54.0,(930,100),"coast_halt","断崖の海沿いの小駅。"),
 ("M16","汐見","しおみ","HM,HR",58.8,(840,100),"medium_port","中規模駅。汐見臨港鉄道と接続(乗り入れなし)。"),
 ("M17","岬口","みさきぐち","HM",63.3,(750,100),"cape_halt","岬へ向かう分岐のない無人駅。"),
 ("M18","灯台前","とうだいまえ","HM",67.5,(660,100),"lighthouse_halt","灯台の見える風除けの駅。"),
 ("M19","大湊","おおみなと","HM,TR,BM",72.4,(500,100),"large_terminal","大規模終着駅。大湊市電・湾岸高速鉄道が隣接(乗り入れなし)。"),
 ("R02","汐見埠頭","しおみふとう","HR",2.4,(840,190),"harbor_end","臨港線の終点、貨客船の桟橋駅。"),
 ("TR02","大湊市場前","おおみなといちばまえ","TR",1.8,(430,190),"tram_stop","路面電車の終点。市場の前。"),
 ("B02","湾岸公園","わんがんこうえん","BM",2.6,(570,190),"monorail_end","モノレールの終点。"),

 # SH branch (新線・昭和48年開業。km は かやま 起点)
 ("SH02","若葉台","わかばだい","SH",1.9,(615,542),"newtown_overpass","穂波ニュータウンの玄関口。橋上駅舎と団地群。"),
 ("SH03","桜台","さくらだい","SH",3.8,(628,588),"newtown_cherry","桜並木の島式駅。川沿いの住宅団地。"),
 ("SH04","新都中央","しんとちゅうおう","SH",5.8,(640,635),"newtown_center","ニュータウンの中心駅。待避線つき・商業ビル直結。"),
 ("SH05","学園都市","がくえんとし","SH",7.7,(655,682),"campus","大学・高校が集まる学園都市。"),
 ("SH06","流通団地","りゅうつうだんち","SH",9.6,(670,728),"logistics","流通団地・工業団地。貨物の着発線とコンテナ基地。"),
 ("SH07","臨空団地","りんくうだんち","SH",11.2,(680,768),"airport_industrial","空港関連の団地と倉庫群。"),
 ("SH08","穂波空港","ほなみくうこう","SH",12.8,(692,808),"airport_terminal","空港ターミナル直結の終着駅。頭端式ではなく、島式ホームの先に引上線・電留線が延びる通過形。"),
 # YB branch
 ("Y02","滝口","たきぐち","YB",3.4,(960,440),"branch_small","滝見の小駅。"),
 ("Y03","渓流橋","けいりゅうばし","YB",6.1,(1040,440),"branch_small","鉄橋の脇の無人駅。"),
 ("Y04","奥湯","おくゆ","YB",9.0,(1120,440),"branch_end","秘湯の終着駅。"),
 # KE only
 ("K02","丸の内","まるのうち","KE",1.9,(170,360),"urban_underground","オフィス街。"),
 ("K03","港町","みなとまち","KE,KM",4.3,(250,360),"urban_elevated","国都地下鉄との直通接続点。"),
 # KM only
 ("T02","本町","ほんまち","KM",1.1,(150,590),"subway","商店街の地下駅。"),
 ("T03","市役所前","しやくしょまえ","KM",2.2,(215,590),"subway","官庁街の地下駅。"),
 ("T04","国都西","こくとにし","KM",3.5,(280,590),"subway","地上に出る終点側の駅。"),
 # SR only
 ("S02","栗畑","くりはた","SR",3.1,(775,610),"rural_wood","栗園の中の小駅。"),
 ("S03","森下","もりした","SR",6.0,(850,610),"rural_wood","森の中の駅。"),
 ("S04","高原町","こうげんまち","SR",9.2,(925,610),"highland_end","高原の終着駅。"),
]
# ---------------------------------------------------------------- line geometry (schematic), line-id -> ordered station ids
ORDER = {
 "HM": ["M01","M02","F01","M03","M04","M05","M06","M07","M08","M09","M10","M11","M12","M13","L01","M14","M15","M16","M17","M18","M19"],
 "YB": ["M10","Y02","Y03","Y04"],
 "SH": ["M07","SH02","SH03","SH04","SH05","SH06","SH07","SH08"],
 "KE": ["M01","K02","K03","M03"],
 "KM": ["M01","T02","T03","T04"],
 "SR": ["M08","S02","S03","S04"],
 "HR": ["M16","R02"],
 "TR": ["M19","TR02"],
 "BM": ["M19","B02"],
}
# through services: (name, run over, trains)
THROUGH = [
 {"name":"国都電鉄 → 国鉄 直通","from":"KE","onto":"HM","section":["M03","M04","M05"],"note":"新田橋から川原・みずほまで乗り入れ。電化区間は川原まで、みずほまで電車が入るため架線を延伸(みずほまで電化)。","stock":"国都電鉄 3000系(独自) / 国鉄 通勤型"},
 {"name":"山麓鉄道 → 国鉄 直通","from":"SR","onto":"HM","section":["M08","M07","M06"],"note":"山辺から穂波野まで気動車が乗り入れ。穂波野の車両基地で折り返し・留置。","stock":"山麓鉄道 キハ200形(独自)"},
 {"name":"国都地下鉄 ⇄ 国都電鉄 相互直通","from":"KM","onto":"KE","section":["K03","K02","M01"],"note":"港町〜国都中央で地下鉄と私鉄が相互乗り入れ。","stock":"国都地下鉄 1000系(独自) / 国都電鉄 3000系"},
]
from details import D,KEYS
def station_dict():
    out=[]
    for sid,name,kana,lines,km,xy,typ,note in S:
        e={"id":sid,"name":name,"kana":kana,"lines":lines.split(","),"km":km,"xy":xy,"type":typ,"note":note}
        e.update(dict(zip(KEYS,D[sid])))
        out.append(e)
    return out
for k,v in INFO.items(): COMP[k]["info"]=v
for k,v in COMPX.items(): COMP[k].update(v)
import os
from extras import ELEV,SECT,WORLD_SCALE
from services import SVC
_st=json.load(open("status.json")) if os.path.exists("status.json") else {"status":{},"log":[]}
_c=[x for x in station_dict() if x["id"]=="M06"][0]["xy"]
for _s in net_st if False else []: pass
net={"sect":SECT,"svc":SVC,"jp":JP,"status":_st["status"],"log":_st["log"],"fac":FAC,"elec":ELEC,"fackind":{k:{"name":v[0],"desc":v[1]} for k,v in FACKIND.items()},"companies":COMP,"lines":LINES,"stations":station_dict(),"order":ORDER,"through":THROUGH}
json.dump(net,open("network.json","w"),ensure_ascii=False,indent=1)
for _s in net["stations"]:
    _s["elev"]=ELEV[_s["id"]]
    _s["world"]=[round((_s["xy"][0]-_c[0])*WORLD_SCALE),round(-(_s["xy"][1]-_c[1])*WORLD_SCALE)]
json.dump(net,open("network.json","w"),ensure_ascii=False,indent=1)
print(len(net["stations"]),"stations")
