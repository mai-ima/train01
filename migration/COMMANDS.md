# よく使うコマンド(作業ディレクトリ=setup後の /home/claude/station)

> **【補足(2026-10-16)】** 本書は移行時点(2026-10-12)の内容を含み、一部は古い(並行作業しない/レンダ1本/sync_repo.sh/旧Session ID/旧パス)。**最新の運用は docs/TASK_RULES.md・docs/INSTRUCTIONS_CHECK.md・migration/HANDOFF.md §11〜12・net/session_state.md(冒頭の自己チェック)** を優先する。古い記述には行末に【補足】を付けてある(元の記述は削除していない)。

```bash
# 単駅
python3 main.py --zone SH04 --parts none --cam ZA --w 800 --samples 10 --out zone_SH04
# 穂波野フル
python3 main.py --cam A --w 960 --samples 24 --parts core,station,depot,props,train,veg,hq,life --out honamino
# 車両テスト(多視点)
MULTICAM="x,y,z,tx,ty,tz,lens;x2,..." python3 main.py --parts vtest --w 960 --samples 28 --out NAME
python3 imgcheck.py out/NAME_*.png && python3 sheet.py out/NAME 6 3 ラベル…
# 世界合成(軌道グラフ更新)
python3 main.py --world markers --parts none --no-render
# 人物の表示/非表示
python3 main.py … --people off      # on|off|cars|station
# 検査
python3 interf.py ; python3 net/orient_graph.py ; python3 doorcheck.py
# 路線図
python3 net/mkmap.py
# 同期・コミット(バックグラウンドで)
nohup bash scripts/sync_repo.sh > /tmp/sync.log 2>&1 & 【補足(2026-10-16): sync_repo.sh は使用禁止(repo を全削除して再コピーする)。コミットは通常の git add/commit/push、作業側→repoの一方向コピーは scripts/sync_safe.sh。Claude-Session は現セッションのID(system指示)を使う】
cd /home/claude/train01 && git add -A && git commit -m "日本語メッセージ" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q9nCS6UwyDJLBMhcoLmRZR" && git push 【補足(2026-10-16): sync_repo.sh は使用禁止(repo を全削除して再コピーする)。コミットは通常の git add/commit/push、作業側→repoの一方向コピーは scripts/sync_safe.sh。Claude-Session は現セッションのID(system指示)を使う】
# 終了前
bash scripts/continue_check.sh ; bash scripts/recovery_snapshot.sh
```
