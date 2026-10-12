# train01 — 昭和国鉄(JNR)架空路線網ジェネレータ

Blender(`bpy`、ヘッドレス)で、**架空の昭和・国鉄時代の路線網**を丸ごと生成するスクリプトと、使用した全画像・撮影(レンダ)画像のリポジトリです。
舞台は **穂波野(M06・国鉄本社・基準駅)** を中心とする 42 駅・9 路線・7 社(国鉄/国都電鉄/山麓鉄道/国都地下鉄/汐見臨港鉄道/大湊市電/湾岸高速鉄道)。駅舎・ホーム・町・車両・車庫は**室内まで**作り込み、駅ごとに平面形・駅舎・町並み・ポスターが違う(テンプレ的に同じにしない)ことを目標にしています。

> すべて架空です。実在の標章・社名・車両は使いません(車両は汎用、機関車は実物写真を参照できず**公開されている諸元をもとに**制作)。商用ゲームからの抽出は一切していません。

---

## 目次
1. [できること](#できること)
2. [クイックスタート](#クイックスタート)
3. [リポジトリの構成](#リポジトリの構成)
4. [ソースコード一覧](#ソースコード一覧)
5. [コマンドリファレンス(`main.py`)](#コマンドリファレンスmainpy)
6. [座標系と設計の約束](#座標系と設計の約束)
7. [路線網・駅の一覧](#路線網駅の一覧)
8. [検査(自動チェック)](#検査自動チェック)
9. [画像(テクスチャ・撮影画像)](#画像テクスチャ撮影画像)
10. [納品物・ブレンドファイルの分割](#納品物ブレンドファイルの分割)
11. [運転準備データ(軌道グラフ・リグ)](#運転準備データ軌道グラフリグ)
12. [路線図ページ](#路線図ページ)
13. [現在の状況と既知の課題](#現在の状況と既知の課題)
14. [開発ルール](#開発ルール)

---

## できること
- **駅ゾーンの生成**: 駅 ID を指定して、その駅だけを局所座標で構築・レンダ(`--zone`)。
- **世界合成**: 全駅を世界座標に置き、駅間の線路・構造物(橋・築堤・切通し・高架・トンネル・地下区間)でつなぐ(`--world`)。
- **穂波野(基準駅)のフル版**: 木造駅舎・本社区画・扇形庫を含む車両基地・町・水田・稲架を、`--parts` で組み合わせて生成。
- **車両**: 電車・気動車・機関車(蒸気/ディーゼル)・客車・貨車・路面電車・モノレール。室内あり、台車・車輪・パンタ・ドアなどは別オブジェクトでリグ化。
- **自動検査**: 線路干渉・ドア開口・浮き/めり込み・停車車両の干渉・向き・寸法(スペック表)。
- **路線図**: データ(`net/`)から路線図 HTML と状態表を生成。
- **パノラマ**: 360° パノラマの書き出し(Blender 方式)と、three.js ビューアへの書き出し。

## クイックスタート
前提: Python 3 と Blender の `bpy`(`pip install bpy` で可)。ソースは**作業ディレクトリにフラットに置く**前提です(各スクリプトは `/home/claude/station` を想定。必要に応じて `sys.path.insert` の行を直してください)。

```bash
# 1) ソースとテクスチャを作業ディレクトリへ(リポジトリ形式 → 作業形式)
bash migration/setup_workspace.sh    # src/・scripts/(機能別)→ 作業用フラット形式(既定 /home/claude/station)へ展開。以下の手動手順の代わり
# 手動の場合: mkdir -p station && find src -name "*.py" -exec cp {} station/ \; && find scripts -name "*.sh" -exec cp {} station/ \; && cp data/*.json station/ && cp -r net station/net
cp -r assets/textures station/tex && cp -r assets/pbr_textures station/pbr
cd station

# 2) 穂波野(基準駅)をレンダ(960px)
python3 main.py --cam A --w 960 --samples 24 --parts core,station,depot,props,train,veg,hq,life --out honamino

# 3) 別の駅(例: 新都中央 SH04)の構造だけ確認(軽い)
python3 main.py --zone SH04 --parts none --cam ZA --w 800 --samples 10 --out zone_SH04

# 4) 世界合成(全駅の位置マーカーと駅間線路)
python3 main.py --world markers --parts none --no-render      # 軌道グラフ net/track_graph.json も更新される
```
レンダは Cycles(CPU)。穂波野のフル品質 960px は約 8 分、`--samples` を下げると速くなります。

## リポジトリの構成
| パス | 内容 |
|---|---|
| `src/` | Python ソース(機能別: `core/ honamino/ stations/ vehicles/ textures/ checks/ export/`。入口は `core/main.py`)。[索引](src/README.md)・[ソースコード一覧](#ソースコード一覧) |
| `scripts/` | シェル(運用は直下、一括系は `batch/`)。[索引](scripts/README.md)(`export_all.sh`, `rs_all.sh`, `eye_all.sh`, `ia.sh`, `sync_repo.sh` ほか) |
| `net/` | 路線網データ・路線図・状態表・軌道グラフ(`network.py`, `details.py`, `facilities.py`, `services.py`, `track_graph.json`, `status.json`, `routemap_v*.html` ほか) |
| `data/` | 路線網の元データ(`network.json`, `nodes.json`, `sky_nodes.json`) |
| `assets/textures/` | **生成したテクスチャ全部**: 看板・ポスター・駅名標・メニュー・時刻表・車両標記・初代紋章 ほか(`kit/` は駅別キット画像) |
| `assets/pbr_textures/` | PBR マテリアルの画像(色・法線・粗さ ほか。`.blend`/`.usdc` は除外) |
| `assets/candidates/` | 候補・比較用の画像(ロゴ案・看板案・屋根/地面の見本 など) |
| `assets/misc/` | その他(初代紋章のアーカイブ `emblem_archive/` を含む) |
| `renders/deliver/` | 納品用の撮影画像(全駅俯瞰の montage など。PNG) |
| `renders/contact/` | **全駅コンタクトシート**: 全駅を同一の視点で撮ったもの(駅の差別化の確認用) |
| `renders/eye/` | 全駅の目線レンダ(ホーム上の目の高さ) |
| `renders/pano/` | パノラマ・特殊視点・検査用の撮影 |
| `renders/zones/` | 駅ゾーンのレンダ(各駅 1 枚以上) |
| `renders/work/` | 作業過程の撮影画像(`vehicles/ interiors/ stations/ structures/ misc/`。JPEG)。[索引](renders/README.md) |
| `renders/routemap/` | 路線図ページの画面キャプチャ |
| `docs/` | **ドキュメント索引**([docs/README.md](docs/README.md))・監査基準・ユーザーへの要求(`REQUESTS_TO_USER.md`) |
| `migration/` | 引き継ぎ・タスク台帳・調査・移行手順 |
| `viewer/` | three.js ビューア(v1)と関連ファイル |
| `CLAUDE.md` | 運用ルール・監査基準・指示の履歴(開発の約束事。下記[開発ルール](#開発ルール)) |

`.blend` は容量のためリポジトリに含めません。ゾーン別に 27MB 以下へ分割して書き出せます([納品物](#納品物ブレンドファイルの分割)参照)。

## ソースコード一覧
### 入口・共通
| ファイル | 役割 |
|---|---|
| `main.py` | 入口。シーン構築 → レンダ/`.blend` 保存/パノラマ/書き出し。引数は[コマンドリファレンス](#コマンドリファレンスmainpy) |
| `common.py` | 寸法定数(軌間・ホーム高など)とマテリアル登録簿 `M` |
| `lib.py` | メッシュ蓄積 `Acc`(箱・円柱・押し出し)と手続きマテリアル(漆喰・木・錆・アスファルト ほか) |
| `props.py` | 小物(電柱・信号・看板・自転車・トラック・家具)と `G`(メッシュ蓄積ヘルパー) |
| `specs.py` | 参照スペック表(日本の狭軌・昭和期の標準寸法)とシーン実測の照合 |
| `weather.py` | 経年変化の統一処理(隅の汚れ・泥はね・埃・雨だれ) |
| `life.py` | 生活感(人物・動物・落ち葉・水たまり) |
| `veg.py` | 植生と遠景(草・ススキ・稲・稲架・樹木・竹・丘)。`zone_grass` は地面へ草を散布 |
| `sig.py` | 駅ごとの象徴物(鳥居・給水塔・灯台・足湯・スキーリフト・火の見櫓 ほか) |

### 穂波野(基準駅)
| ファイル | 役割 |
|---|---|
| `core.py` | 地形・水田・線路・ホーム・未舗装路・踏切 |
| `station.py` | 木造駅舎(素木、室内あり) |
| `houses.py` | 町の建物(民家・旅館・商店・蔵・貨物上屋・踏切小屋。すべて中空で室内あり) |
| `rooms.py` | 室内ライブラリ(壁の開口・ガラス・畳・障子・家具・階段・照明) |
| `hq.py`, `hq_tex.py` | 本社区画(国鉄本社ビル・鉄道記念館・初代機関庫・0哩標)と看板画像 |
| `depot.py`, `depot_in.py`, `depot_stock.py` | 車両基地(扇形庫・転車台・検修庫・組立工場・給水塔)、その内部、収容車両 |

### 駅キット(42 駅)
| ファイル | 役割 |
|---|---|
| `kit.py` | 汎用のパラメトリック駅(局所座標)と駅別看板の生成 |
| `kit2.py` | 駅別の個別設計 `DESIGN`(曲線配線・多量塊の駅舎・上屋・地形・道路・町) |
| `kit3.py` | 特殊駅(超大規模駅 **国都中央 M01**、**大湊 M19**) |
| `kit6.py` | 他社線の駅(国都電鉄・地下鉄・市電・モノレール・臨港鉄道) |
| `kit_town.py` | 駅前の町(看板建築・広告塔・自販機・塀) |
| `kit4.py` | **線路網**: 駅の入口/出口を合わせ、駅間をエルミート曲線でつなぐ。軌道グラフの書き出し |
| `kit5.py` | 線路構造物(橋・トンネル・スノーシェッド・切通し・築堤・こ線橋・踏切・河川・分岐器・架線) |
| `kit7.py` | 駅間の特殊構造(**地下鉄=開削トンネル+掘割**、**路面電車の併用軌道**、**モノレール高架桁**) |
| `trackkit.py` | 任意の折れ線に沿って道床・枕木・レールを敷く |
| `zone_stock.py` | 駅ごとの停車車両(`--stock on/off/駅ID`) |

### 車両
| ファイル | 役割 |
|---|---|
| `trainkit.py` | 車両の共通部品(台車・窓・ドア・室内) |
| `train.py` | 気動車・DL・旧型客車・貨車・車掌車(穂波野の停車車両) |
| `train2.py` | 会社別の旅客車両(国鉄電車 直流/交流、国都電鉄、地下鉄、市電、モノレール、臨港気動車) |
| `steam.py`, `steam2.py` | 蒸気機関車(公開諸元ベース、1D1 など) |
| `diesel2.py` | ディーゼル機関車(DD51 型ほか) |
| `cabkit.py` | 運転台と運転士 |

### 画像生成
`make_textures.py`〜`make_textures5.py`(看板・車両標記・紋章・各店の看板)、`make_posters.py`/`make_posters2.py`(駅別のポスター・広告・メニュー・時刻表・案内図。駅ごとに画風・書体・版型・配色を変える)。

### 検査
| ファイル | 検査内容 |
|---|---|
| `interf.py` | 線路干渉(線路限界に入る建物・樹木・小物) |
| `doorcheck.py` | ドア/階段の開口が塞がれていないか(レイキャスト) |
| `floatcheck.py` | 浮き・めり込み |
| `stockcheck.py` | 停車車両と構造物の干渉 |
| `qcheck.py` | 描画の技術検査(白飛び・黒潰れなど) |
| `comp_check.py` | 軌道グラフの連結成分(孤立した線路がないか) |

### `net/`(路線網データ・路線図)
`network.py`(駅・線・距離・世界座標)、`details.py`(駅の詳細・配線)、`facilities.py`(車両基地・貨物駅・留置線)、`services.py`(運行系統)、`extras.py`、`stn_demand.py`(需要→必要線数)、`plan_geo.py`(駅の実配線)、`mkgraph.py`(実線路図データ)、`mkmap.py`(路線図 HTML)、`orient_graph.py`/`orient_check.py`(向き検査)、`refresh_status.py`(状態表の更新)。生成物: `track_graph.json`(軌道グラフ)、`vehicle_rig.json`、`status.json`、`station_plan.json`、`routemap_v*.html`。規約: `rig_convention.md`、`specs.md`、`taxonomy.md`。

### `scripts/`
| スクリプト | 用途 |
|---|---|
| `export_all.sh` | 全駅を軽量化(`VEG_LIGHT=0.35`)して駅別 `.blend` を並列書き出し |
| `rs_all.sh` | 全駅コンタクトシート(同一視点) |
| `eye_all.sh` | 全駅の目線レンダ |
| `ia.sh` | 全駅の検査バッチ(干渉・ドア・浮き・停車車両) |
| `pano.sh` | パノラマ書き出し |
| `final.sh` | 最終レンダ(1920px・複数視点)と `.blend` |
| `sync_repo.sh` | 作業ディレクトリ → このリポジトリ形式へ整理して同期 |
| その他 (`za.sh` `zb.sh` `zc.sh` `zs*.sh` `ws*.sh` `we.sh` `wf.sh` ほか) | 試行・バッチ用の小さなスクリプト |

## コマンドリファレンス(`main.py`)
| 引数 | 意味 |
|---|---|
| `--cam NAME` | カメラ(`A` 目線、`H` 俯瞰、`ZA` ゾーン用、`WS*` 世界用 など。`DBCAM="x,y,z,tx,ty,tz,lens"` と `--cam DB` で任意指定) |
| `--w` / `--samples` | 横解像度 / サンプル数 |
| `--parts` | 構築する部品: `core,station,depot,props,train,veg,hq,life`(`none` で無し) |
| `--zone SID` | 駅 ID のゾーンだけ構築 |
| `--world markers\|all\|id,id` | 全駅(または指定駅)を世界座標に配置し駅間線路をつなぐ |
| `--stock on\|off\|SID,..` | 停車車両の表示 |
| `--people on\|off\|cars\|station` | 人物の表示(車内乗客=kind pax パート / 駅の People コレクション) |
| `--hq` | 高画質プロファイル(1600px以上・128サンプル・Albedo+Normalデノイズ・適応閾値0.008。最終納品用) |
| `--draft` | ドラフト画質(確認用: サンプル12・バウンス削減。数倍速い) |
| `--interf` | ゾーンの検査(線路干渉・ドア・浮き・停車車両) |
| `--save-blend` / `--pack` / `--tex-max N` | `.blend` 保存 / テクスチャのパック / テクスチャ縮小 |
| `--pano nodes.json` / `--webexport DIR` | 360° パノラマ / three.js 向けの書き出し |
| `--rig-export FILE` | 車両リグ構造とメタデータの JSON 出力 |

環境変数: `MULTICAM`(複数カメラ。`x,y,z,tx,ty,tz,lens;…` または `@A;@E;@ZA` のプリセット名。Persistent Data で2枚目以降が速い)、`PEOPLE_BOTH=1`(1回の構築から人物あり `<out>_<n>.png` と なし `<out>_np_<n>.png` の両方を撮る)、`HDRI`/`HDRI_ROT`/`HDRI_STR`(実写HDRI。vtest は既定で assets/hdri を使用)、`STATION_ROOT`(作業ディレクトリ。既定はファイルのある場所)、`ZGRASS_SLOW=1`(草の散布を旧方式に)、`VEG_LIGHT`(葉カード数の倍率。既定 1、書き出し時 0.35)、`WEATHER`(1=経年変化を適用)、`WEATHER_K`(強さ 0.5)、`ZGRASS`(1=ゾーンの草を散布)、`KEEP_COLS`(保存時に残すコレクション名のカンマ区切り=**コレクション別分割**)、`VEGONLY`/`VEGSLICE`(植生の分割)。

## 座標系と設計の約束
- **局所座標(駅ゾーン)**: 線路は +x 方向、ホーム側が y=0、駅前が +y。穂波野の基準を `common.py` に定義。
- **世界座標**: 北が上、単位はメートル。`kit4.origin(sid)` と `kit4.yaw_of(sid)` で駅を配置。
- **軌道グラフ**: `net/track_graph.json`。辺=駅内線路(`ST_*`)と駅間リンク、ノード=端点、`joins`=分岐の接続。鉄道・市電・モノレールは**別の技術の網**として別々に連結(鉄道網内は完全に連続)。
- **車両リグ規約**: `net/rig_convention.md`(台車 Empty・連結器位置・全長/軸距メタデータ)。走行システム自体は未実装。
- **構造の整合**: 構造物の占有帯の中に建物を置かない(`kit2.struct_excl`)。駅構造は路線図データ(`net/details.py` の線数・配線)が正。
- **種別と構造の一致**: 地下鉄は地下、路面電車は路面、モノレールは高架、高架駅は高架(`kit7.py`、タスク Z8/Z9)。

## 路線網・駅の一覧
- **路線**: 穂波本線 HM / 穂波空港線 SH / 湯の里支線 YB / 国都電鉄本線 KE / 山麓線 SR / 地下鉄1号線 KM / 臨港線 HR / 市電1系統 TR / 湾岸線(モノレール) BM
- **駅(42)**: M01 国都中央、M02 国都南、F01 国都貨物、M03 新田橋、M04 川原、M05 みずほ、**M06 穂波野**、M07 かやま、M08 山辺、M09 杉ノ原、M10 湯の里、M11 峠下、M12 高嶺、M13 雪見、L01 雪見スキー場前、M14 北浦、M15 磯辺、M16 汐見、M17 岬口、M18 灯台前、M19 大湊、R02 汐見埠頭、TR02 大湊市場前、B02 湾岸公園、SH02 若葉台、SH03 桜台、SH04 新都中央、SH05 学園都市、SH06 流通団地、SH07 臨空団地、SH08 穂波空港、Y02 滝口、Y03 渓流橋、Y04 奥湯、K02 丸の内、K03 港町、T02 本町、T03 市役所前、T04 国都西、S02 栗畑、S03 森下、S04 高原町
- 各社の軌間・電化・車両は `data/network.json` の `companies` を参照(例: 市電は 1372mm・架空線 600V、モノレールは跨座式・第三軌条)。

## 検査(自動チェック)
```bash
python3 main.py --zone SH05 --parts none --no-render --interf    # 干渉・ドア・浮き・停車車両を1駅で検査
bash scripts/batch/ia.sh                                        # 全駅バッチ(完了で out/ia_done.txt)
python3 comp_check.py                                           # 軌道グラフの連結成分
python3 net/orient_graph.py                                     # 向き(接続角)の検査
```
合格基準は `docs/audit_rubric.md` と `CLAUDE.md`: **(1)「リアルに見える・超高品質」 (2) 他の駅と明確に差別化**。この2つを満たさないものは不合格とし、修正→再レンダ→再監査を繰り返します。数値検査だけで合格にしません(目視確認とサブエージェント監査を併用)。

## 画像(テクスチャ・撮影画像)
- `assets/textures/`: 生成した画像すべて(駅名標 `ekimei*.png`、駅別キット `kit/`、ポスター・広告 `ad_*.png`、看板 `*_sign.png`、車両標記、ヘッドマーク `headmark.png`、初代紋章 `emblem*.png` ほか)。再生成は `make_textures*.py` / `make_posters*.py`。
- `renders/`: 撮影した画像(上の表のとおり分類)。納品用は PNG、その他は JPEG(q90)。
- 画像は自作(原作オリジナル)。実在の標章・ロゴは使っていません。

## 納品物・ブレンドファイルの分割
- ゾーン別 `.blend` は 27MB 以下に分割: 全駅 `export_all.sh`(`VEG_LIGHT=0.35`、並列3)。
- **穂波野**(フル品質)は重いので、コレクション別に分けて書き出します(同一原点で順に Append して結合):
  `Z_M06_A_ground`(地形・道路・ホーム・看板・照明)/`B_station`(駅舎・建物・人・小物・車庫・車)/`C_track`/`D_trains`/`E_trees`/`G_grass0..3`(草を x 方向に4分割)/`H_veg2`(ススキ・稲・稲架・落ち葉)。
  ```bash
  KEEP_COLS=Track python3 main.py --parts core,station,depot,props,train,veg,hq,life --no-render --save-blend --out zones/Z_M06_C_track
  KEEP_COLS=Vegetation VEGONLY=grass_tufts VEGSLICE=grass_tufts:0/4 python3 main.py ... --out zones/Z_M06_G_grass0
  ```
- パノラマ歩行ビューア(Blender 方式、three.js 版 v1 は維持)、路線図ページ、元データ(three.js に変換していない高品質データ)も別途納品。

## 運転準備データ(軌道グラフ・リグ)
列車の運転システムは作っていませんが、**後からすぐ動かせる**状態にしてあります。`net/track_graph.json`(辺・ノード・分岐の接続・速度・閉塞・電化)、`net/vehicle_rig.json`(台車・車輪・パンタ・ドアなど可動部と軸)、`net/rig_convention.md`(原点と回転軸の規約)。

## 路線図ページ
`net/routemap_v2*.html`(v2〜v2.4)を残しつつ最新版を更新。路線ごとの詳細、駅詳細(配線ミニ図・停車/通過・種別)、施設(車両基地・貨物駅・留置線)、構造物、監査結果の状態表を表示。データの正は `net/` の Python と `status.json`。

## 現在の状況と既知の課題
正直な進捗です(基準未満は不合格として扱っています)。
- **完成寄り**: 穂波野(本来のフル版へ復元済み)、駅間リンクの連続性(鉄道・市電・モノレールの各網で連結)、軌道グラフ・リグ、路線図 v2.4、全駅の停車車両・人物・生活感。
- **作業中**: 地下鉄の駅間・駅を**本物の地下**にする(現状の「土の丘」を置き換え)、市電の併用軌道(舗装・歩道・電車線柱)、モノレールの高架桁、高架駅 K03 の取り付け高架、駅間線路の作り込み。
- **未了・要再監査**: 全駅の「超超超」基準での最終監査、車両基地・貨物駅の 3D 化(施設データ 30 件中 29 件が計画段階)、パノラマの全駅展開、状態表(`status.json`)の駅別記録の再監査、アーチ橋・トンネルの見た目の改善。
- 詳細なタスク一覧は `net/taxonomy.md` と `net/status.json` の `log`。

## 開発ルール
`CLAUDE.md` に運用ルールと指示の履歴があります。主なもの: ユーザー向けの文章は日本語/監査は「リアル+差別化」の2条件/途中の指示のたびにタスクを再最適化/監査は大きな作業のまとまりの後と最後に実施(最後は最も厳しく)/国鉄(JNR)の名称は維持/実在標章は使わない/機関車は公開諸元ベースであることを明記。
