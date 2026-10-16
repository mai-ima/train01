# scripts/ — シェルスクリプト
作業ディレクトリ(`/home/claude/station`)で動かす前提です。`setup_workspace.sh` がフラットに展開します。

## 運用(ここに置く: フック・規則から参照される)
| ファイル | 用途 |
|---|---|
| `continue_check.sh` | ターン終了前の確認(未コミット・実行中ジョブ・次の一手) |
| `recovery_snapshot.sh` | 圧縮/再開直後の状態回復(CLAUDE.md末尾・状態・git・ジョブ) |
| `sync_safe.sh` | 作業側 → repo の**一方向・非破壊**同期(通常はこれを使う) |
| `sync_repo.sh` | **破壊的**(repo を全削除して再コピー)。`FORCE_DESTRUCTIVE_SYNC=1` が無いと中止。使わない |
| `e3_batch.sh` | 全駅を1回の構築で 3カメラ × 人物 表示/非表示 で撮る(E3) |

## batch/ — 一括レンダ・検査・書き出し
`ia.sh`(全駅検査)`rs_all.sh`(コンタクトシート)`eye_all.sh`(目線)`export_all.sh` `export_zones.sh`(ゾーン別 .blend)`pano.sh` `final.sh` `audit.sh` ほか。`ws*.sh` `we.sh` `wf.sh` `wc.sh` `wd.sh` は世界合成の撮影、`za.sh` `zb.sh` `zc.sh` `zs*.sh` `zones.sh` はゾーン撮影の試行用。

## 2026-10-16 追加
- `k8_all.sh <駅ID...>`: 全ゾーンのモデル間干渉検査(--no-render, 3並列)。結果 out/mc_<ID>.json。集計は `src/checks/mc_agg.py`(意味のある干渉=重なり0.3m以上・三角形20以上、樹冠同士は除外)、駅別内訳は `mc_sum.py <json>`。
- 干渉の原因特定: `PROBE='名前,x,y,z,r'`(球内の頂点)/ `PROBE_BOX='名前,y0,y1,zmax'` / `PROBE_PAIR='A,B'`(交差三角形の実座標)/ `PROBE_GROUP='接頭辞,…'`(建物1棟の実bbox)を MODELCHECK と併用。
- `k8_vis.sh`: 指定駅を最大4本×1スレッドで撮る視覚確認。`e5_all.sh`: 全駅6視点撮影(同時3本×1スレッド。重い駅は1本4.4GBなので4本はOOM)。
- `bench_conc.sh / bench_n4.sh / bench_n4c.sh`: レンダ同時本数の計測(W6、結果は docs/TASK_RULES.md §7)。
