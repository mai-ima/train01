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
