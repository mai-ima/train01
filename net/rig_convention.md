# 運転準備データ規約(走行システムは未実装)

## ファイル
- `net/track_graph.json` 軌道グラフ。座標はワールド(m)、折れ線は2m間隔、s=弧長。
  - edges: id / line / kind / from_station / to_station / length / speed_kmh / block / junction / electrified / power / pts
  - 駅構内線は `ST_<駅ID>_<番線>`(kind="station")
  - nodes: 端点が25m以内の辺を同一ノード化。`switch=true` は3辺以上が集まる分岐点
  - stops: 各駅・各線の停止位置(辺IDと弧長s)
  - 電化: 直流1500V(HM M01–M05)、交流20kV 50Hz(SH SH04–SH08)。非電化区間は `electrified=false`
- `net/vehicle_rig.json` 全14両のリグ情報(Blender上の階層と回転軸、台車位置・軸距・輪径・連結器位置)。

## リグ階層
車両ルートEmpty > `bogieN`(Z軸=旋回)> `wsN`(Y軸=車輪回転、半径はcustom prop)  
車両ルートEmpty > `couplerN`(Z軸)。Emptyの原点が回転中心。

## 走らせ方(将来)
1. 各台車の x を車両ルートからのオフセットとして、辺の弧長 s に対応する位置へ置く。
2. 台車の向きは折れ線の接線、車体は前後台車の位置を結ぶ線で決める。
3. 車輪回転 = 走行距離 / 輪径。
4. 分岐は nodes の switch で選ぶ。速度上限は speed_kmh、閉そくは block。

## 分岐接続(joins)
端点が他の辺の途中に取り付く分岐線(穂波空港線・川原線・他社線など)は、`joins` に
`{edge, end, to_edge, to_s, gap_m}` として記録(分岐元の辺と弧長位置)。nodes の端点一致だけでは繋がらない箇所をここで補う。
