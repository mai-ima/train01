# 主要ファイル早見表

> **【補足(2026-10-16)】** 本書は移行時点(2026-10-12)の内容を含み、一部は古い(並行作業しない/レンダ1本/sync_repo.sh/旧Session ID/旧パス)。**最新の運用は docs/TASK_RULES.md・docs/INSTRUCTIONS_CHECK.md・migration/HANDOFF.md §11〜12・net/session_state.md(冒頭の自己チェック)** を優先する。古い記述には行末に【補足】を付けてある(元の記述は削除していない)。

| 区分 | ファイル | 役割 |
|---|---|---|
| 規則 | CLAUDE.md, migration/USER_INSTRUCTIONS*.md, docs/audit_rubric.md, docs/RECOVERY.md | 守る規則・指示履歴・採点基準 |
| 状態 | migration/tasks.json, TASKS.md, HANDOFF.md, CONTEXT.md, net/session_state.md | 台帳・現在地 |
| 入口 | main.py | CLI(--zone/--world/--parts/--people/…) |
| 駅 | kit.py kit2.py kit3.py kit6.py kit8.py rooms.py props.py houses.py kit_town.py hq.py | 駅・町・室内 |
| 線路 | kit4.py kit5.py trackkit.py kit7.py | 軌道グラフ・架線・分岐・地下 |
| 車両 | vehtypes.py trainkit.py train.py train2.py steam.py diesel2.py cabkit.py zone_stock.py depot*.py | 形式・室内・編成・車庫 |
| データ | net/network.py details.py services.py facilities.py structs.py track_graph.json status.json | 路線網の正 |
| 画像 | make_textures*.py make_posters*.py hq_tex.py assets/textures | テクスチャ生成 |
| 検査 | imgcheck.py sheet.py interf.py doorcheck.py floatcheck.py stockcheck.py net/orient_graph.py qcheck.py | 自動検査 |
| 路線図 | net/mkmap.py net/routemap_v245.html net/map_tmpl_v245.html | 路線図生成 |
| 運用 | scripts/sync_repo.sh continue_check.sh recovery_snapshot.sh | 同期・終了前確認・回復 | 【補足(2026-10-16): sync_repo.sh は使用禁止(repo を全削除して再コピーする)。コミットは通常の git add/commit/push、作業側→repoの一方向コピーは scripts/sync_safe.sh。Claude-Session は現セッションのID(system指示)を使う】
