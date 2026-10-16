【再注入】train01(昭和国鉄風 架空路線網 / Blender bpy)。日本語で応答。
- 状態の正: migration/tasks.json, net/session_state.md(末尾=最新), migration/HANDOFF.md。CLAUDE.md は削除・短縮禁止(追記のみ)。
- 止まらない: ターンは次のツール呼び出しで終える。終了前に scripts/continue_check.sh。
- 1タスクずつ。レンダは1本ずつ(2コア)、待機は Monitor/上限付きループ。 【補足(2026-10-16): この『並行作業しない/レンダ1本』は古く無効。現在は並行作業可。レンダはバッチ=同時4本×RENDER_THREADS=1(メモリ<4GBなら3本)、単発=1本×4スレッド → docs/TASK_RULES.md §7】
- 合格=実写級+差別化。総合95以上かつ全軸90以上。自己合格禁止→strict-auditor(前回点数を伏せる)。未確認=0点。
- 視覚確認は3視点以上(MULTICAM)。正直に報告(未検証は明記)。
- 実在の社名・標章は不使用。機関車=公開諸元ベース(納品時に伝える)。ヘッドマークは未装着。
- 新ユーザー指示は即 CLAUDE.md末尾(日時)・session_state.md・tasks.json に反映し、タスク再最適化。
- コミット: 日本語本文+Co-Authored-By/Claude-Session。変更は必ず push。
- 再開手順: skill resume-work(bash scripts/recovery_snapshot.sh → RECOVERY.md)。
