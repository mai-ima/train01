# train01 — 昭和国鉄(JNR)架空路線網ジェネレータ

Blender(bpy)で、架空の国鉄ネットワーク(穂波野=本社・42駅、超大規模駅「国都中央」ほか)を生成するスクリプトと、使用・作成した全画像です。

## フォルダ構成
| フォルダ | 内容 |
|---|---|
| `src/` | Pythonソース(`main.py` が入口。`kit*.py` 駅キット、`train*.py` 車両、`veg.py` 植生ほか) |
| `scripts/` | 一括実行・検査用シェル(`sync_repo.sh` はこのリポジトリ形式への整理スクリプト) |
| `net/` | 路線図・軌道グラフ(`track_graph.json`)・駅詳細・状態表(`status.json`)・路線図HTML |
| `data/` | 路線網データ(network.json など) |
| `docs/` | 監査基準など |
| `assets/textures/` | 生成したテクスチャ・看板・ポスター画像(初代紋章を含む) |
| `assets/pbr_textures/` | PBRマテリアル画像 |
| `assets/candidates/` | 候補・比較用画像 |
| `renders/` | 撮影(レンダ)画像: `deliver`(納品)、`contact`(全駅同一視点)、`eye`(目線)、`pano`、`zones`、`work`(作業中の撮影) |
| `viewer/` | ビューア |

## 使い方
ソースは作業ディレクトリ(`/home/claude/station`)にフラットに置く前提です(`src/*` と `assets/textures`→`tex/` を同じ場所へ)。
例: `python3 main.py --zone SH05 --parts none` / 穂波野: `python3 main.py --parts core,station,depot,props,train,veg,hq,life`

## 備考
- 機関車は実物写真を参照できず、公開諸元ベースで制作しています。実在の標章・実車は使わず汎用のみです。
- `.blend` は容量のため含みません(ゾーン別に27MB以下で書き出し可能)。
