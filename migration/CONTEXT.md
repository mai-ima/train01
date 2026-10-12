# 技術メモ・文脈(記憶のファイル化) — 2026-10-12

## 車両フレームワーク(vehtypes.py)
- `TYPES[kind]` に仕様。`z=(floor, sill, window top, eave, roof peak)`。前面 flat/vee/bonnet/round/subfront/gate。
- 室内: `_interior`(通勤/急行)、`_sleep_inside`(寝台)、`_lux_inside`(周遊)。人物 `_rider`(+`_rider_body`)は `v.pax()` で kind="pax" のパートにする(→ `--people off` で消える)。
- 窓上帯は**中空**(側板+天井板 zt-0.06)。中実だと天井が窓上端になり、内部灯が中実ジオメトリ内に入って真っ黒になる。`zwin = zw1; zw1 = zt - 0.06`。
- 末尾の高さ補正ループ(`_zfix`: +0.12/+0.22/+0.20)と `_FLOOR`(形式別床高)。
- 材質: t_lino/t_lino2(PBR床)、t_fl_gr/st/bl、t_mahog(Planks023A)、`TK.moquette`(綾織+斑)、`TK.carpet_lux`(金菱格子)、vpaint の屋根煤(`soot` maprange z 3.05–3.55)。
- `_front_extras(v,S,e,nose)` を `_cab` の後に呼ぶ(連結器/ホース/ステップ/渡り板)。

## レンダ・検査パイプライン
`MULTICAM="x,y,z,tx,ty,tz,lens;..." python3 main.py --parts vtest --w 960 --samples 28 --out NAME` → `out/NAME_n.png`
vtest: 車はx=0, y=30·i(TYPES順)。寝台編成 y=-12 付近、周遊編成 y=-40, x=-250+j·21.55+10.5。
→ `imgcheck.py out/NAME_*.png` → `sheet.py prefix per cols labels…`(ラベルは位置順で、取り違えは見た目だけの問題)→ Read で目視 → Agent(strict-auditor)。

## 路線図パイプライン
network.py → patch_tour.py → mkmap.py → Playwright検査 → Artifact公開(Ae51R2sD6GyV81wgfMWG5A)。patch_v245.py 再実行禁止。

## 過去の失敗と対処
| 事象 | 原因 | 対処 |
|---|---|---|
| 室内が黒 | 中実スラブ内にライト | 窓上帯を中空化 |
| 前景コマンドが exit 143 | 10分超の待機 | Monitor/別コマンド、sync は nohup |
| カメラが壁に遮られる | カメラが車外 | 車内に置く |
| WebFetch PROVENANCE_REQUIRED | URLが検索結果に無い | 先に WebSearch |
| 監査員の「パンタ」指摘 | ラベル未対応のため未検証 | 対応しない(不確実) |
| 路線図 hidden が効かない | SVG | setAttribute('hidden') |

## 監査点数の履歴(正直な数字)
- 車内: 第1〜2回 平均34、第3回(19:30)最高 cross 52 / lx_lng 51 / sl_a・sl_b・box・lx_ste 48 / 最低 sl_din・lx_grn 30。指摘TOP: 人物(球頭+円柱)、座席が直方体、モケット繰り返し、照明/露出、床壁の経年。
- 外観: 第1回(22:05)13形式 43〜47点、環境=40点(vtestの砂地・短い線路)。似たペアは HANDOFF §4。
- Z-A(地下/路面/モノレール/K03): 2回目 0/6 合格。

## 判断メモ
- 軌道グラフ/リグ(運転準備 #94)は完了: net/track_graph.json, rig_convention.md, vehicle_rig.json。走行システム自体は作らない。
- ゾーン .blend は樹木葉カード数を減らして軽量化。パック時はテクスチャ共有か縮小で27MB以下。
- 他社線8駅は kit6、本社区画は hq.py(--parts hq)、駅名画像は kit6._boards。
- 実線路図は北が上(y反転)。
