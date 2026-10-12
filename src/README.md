# src/ — Python ソース(機能別)
リポジトリでは機能別フォルダに置き、**作業時は `migration/setup_workspace.sh` がフラットな作業ディレクトリへ展開**します(各モジュールは `import kit` のようにフラットな名前で読み込むため)。
`scripts/sync_safe.sh` は作業側の変更をこの構成へ書き戻します(同名ファイルは元の場所へ、新規は `misc/`)。

| フォルダ | 内容 | 主なファイル |
|---|---|---|
| `core/` | 入口・共通・小物・植生・経年・生活感 | `main.py`(入口)`common.py` `lib.py` `props.py` `specs.py` `weather.py` `life.py` `veg.py` `sig.py` |
| `honamino/` | 穂波野(基準駅)・町・室内・本社区画・車両基地 | `core.py` `station.py` `houses.py` `rooms.py` `hq.py` `depot*.py` |
| `stations/` | 駅キット(全42駅)・線路網・構造物・駅内部・停車車両 | `kit.py`〜`kit8.py` `kit_town.py` `trackkit.py` `zone_stock.py` |
| `vehicles/` | 車両(電車・気動車・機関車・客車・貨車)と室内 | `vehtypes.py`(形式別・中核)`trainkit.py` `train*.py` `steam*.py` `diesel2.py` `cabkit.py` `spec_table.py` |
| `textures/` | テクスチャ・ポスター・看板・ロゴ・ヘッドマークの生成 | `make_textures*.py` `make_posters*.py` |
| `checks/` | 自動検査・撮影後の確認 | `interf.py` `doorcheck.py` `floatcheck.py` `stockcheck.py` `imgcheck.py` `sheet.py` ほか |
| `export/` | three.js 書き出し・ビューア生成 | `webexport.py` `mkviewer.py` |
