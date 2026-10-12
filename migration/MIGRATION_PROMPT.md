# Claude Code 移行プロンプト(S-MG1)

使い方: リポジトリ(github.com/mai-ima/train01)を clone した Claude Code で、下の「A. 貼り付け用(標準)」をそのまま最初のメッセージに貼る。
短縮版は B、無人連続運転は C(`/goal`)。根拠は `research_handoff.md`。ユーザー向けの文章は**すべて日本語**。

---
## A. 貼り付け用(標準・日本語)
```
あなたは、別のセッション(claude.ai のクラウド環境)から作業を引き継ぐ Claude Code です。
プロジェクトは「昭和国鉄(JNR)風の架空路線網を Blender(bpy, ヘッドレス)で生成する」train01 です。前任セッションの文脈は引き継がれていません。
**状態の正はすべてリポジトリ内のファイルです**。会話の記憶は当てにせず、次の順に実際に読んでから作業を始めてください。

# 0. 準備(最初に1回)
1. `bash migration/setup_workspace.sh` を実行(リポジトリ形式→作業形式 /home/claude/station へ展開、パス置換、bpy確認)。失敗したらエラーを HANDOFF.md「既知の落とし穴」に追記して対処。
2. 以後の作業ディレクトリは展開先(既定 /home/claude/station)。GitHub 側は /home/claude/train01(= このリポジトリ)。

# 1. 読む順(全文を読むこと。要約で済ませない)
1. `CLAUDE.md`(運用ルール・ユーザー指示の全履歴。**絶対に削除・短縮しない**。追記のみ)
2. `migration/USER_INSTRUCTIONS.md`(指示の分類整理)→ 必要なら `USER_INSTRUCTIONS_LOG.md`(原文コピー)
3. `migration/HANDOFF.md`(概要・構造・現状・次の一手)と `migration/CONTEXT.md`(技術メモ・落とし穴・監査点数の履歴)
4. `migration/TASKS.md` / `tasks.json`(全タスク台帳。status の正はこの JSON)
5. `net/session_state.md`(作業ログ。末尾=最新)、`docs/audit_rubric.md`(監査の点数基準)、`docs/RECOVERY.md`
6. `migration/KEY_FILES.md`、`migration/COMMANDS.md`(実行コマンド)
読み終えたら、日本語で「理解した現在地・守るルール上位10・最初に着手するタスク」を3〜10行で報告してから着手。

# 2. 守るルール(要点。全文は CLAUDE.md)
- ユーザーに見える文章・タスク名・コミット文は日本語。コミットは日本語本文+末尾に Co-Authored-By と Claude-Session 行。
- 既存の情報・ファイルを消さない(追記/移動のみ)。「GitHubに入れない」類の旧指示は無効(CLAUDE.md の最新優先)。
- 勝手に中断・停止しない。ターンは必ず次の作業(ツール呼び出し)で終える。待機中も可能な作業を続ける。`bash scripts/continue_check.sh` を終了前に実行。
- 一度に1タスク(または1群)。レンダは1度に1本(2コア)。待機は Monitor か上限付き `timeout … until` ループ(sleep連打禁止)。
- 合格は「実写と見分けがつかない超高品質」+「他駅/他形式と明確に差別化」。監査は点数化(総合95以上かつ全軸90以上、未確認=0)。監査は新文脈のサブエージェント(strict-auditor)に、前回点数を伏せて依頼。自分で自分に合格を出さない。
- 視覚確認は異なる3視点以上(MULTICAM)。1枚で合格にしない。
- 正直に報告(未検証・未達は明記)。現状、車両の内装/外観の監査はすべて不合格(最高52点)。
- 機関車は実物写真を参照できず公開諸元ベース(納品時に必ず伝える)。実在の社名・標章は使わない。ヘッドマークは作るが車両に未装着(指示があるまで)。
- ユーザー指示を受けたら、即 CLAUDE.md 末尾(日時つき)・session_state.md・tasks.json に反映し、タスクを再最適化。
- タスク名は net/taxonomy.md の「群記号+番号」。最優先と**ユーザーが書いた時だけ** `S-` を付ける。

# 3. 最初の1手
- `tasks.json` の in_progress を確認し、なければ pending の先頭群(TASKS.md の「実行順」)。現在の実質位置は HANDOFF.md「現在地と次の一手」(車両の外観差別化 F3c → 内装 F3d2 → 再監査 X13)。
- 1タスクごと: 実装 → レンダ → imgcheck.py → コンタクトシート → 多視点で目視 → 完了なら tasks.json 更新+session_state.md 追記 → コミット/push(`bash scripts/sync_repo.sh` 等、COMMANDS.md)。

# 4. 完了条件
`tasks.json` の全タスクが completed、最終監査(X9 最終超超超高レベル監査)が基準を満たすまで続ける。途中で「おおむね良い」は不合格。
```

---
## B. 短縮版(再開・圧縮後用)
```
作業を引き継ぐ。まず CLAUDE.md を全文、次に migration/HANDOFF.md → CONTEXT.md → tasks.json → net/session_state.md(末尾)を読み、
現在地とルール上位10を日本語で3〜10行報告してから、in_progress のタスクを続行。止まらない・日本語・既存情報を消さない・1タスクずつ・自己合格禁止(strict-auditor で採点)。
```

---
## C. 無人連続運転(/goal)
対話セッションで次を実行(条件は測定可能+証明方法+上限):
```
/goal migration/tasks.json の status が pending/in_progress のタスクが0件で、かつ最新の strict-auditor 最終監査(総合95点以上・全軸90点以上)の出力が会話に提示されている。1ターンごとに tasks.json を更新しその差分を示すこと。CLAUDE.md の削除・短縮と実在標章の使用は禁止。20ターン経過しても未達なら、現在の進捗と未達項目を日本語で報告して一旦区切る。
```
補足: 評価者は会話に出た証拠だけを見る → 検証出力(タスク件数、監査の点数表)を毎回会話に出すこと。非対話は `claude -p "/goal …" --permission-mode auto`。長い連続運転は 20〜30 ターンごとに区切り、`/clear` 後に B を貼って再開。

---
## D. 旧セッションのログを参照したいとき
`migration/transcripts/*.jsonl.gz` を展開(`gunzip -k`)。ただし形式は版で変わるため一次情報にしない(HANDOFF/CONTEXT が一次)。
