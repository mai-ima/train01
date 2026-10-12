# 移行方法・プロンプトの調査記録(2026-10-12 / S-MG1)

ユーザー指示(19:24・19:25): 「作成前に複数ソースから最も効果的なのを調べる」「Webサイトの中までしっかり読む」。
以下は **本文を実際に読んだ** ソースと、そこから決めた設計判断です(伝聞・要約だけの検索結果は根拠にしていません)。

## 読んだソース(本文を取得して確認)
| # | ソース | 種別 | 読んだ範囲 | 要点 |
|---|---|---|---|---|
| 1 | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | 公式 | 全文 | 文脈ウィンドウが最重要資源。検証手段(テスト/スクショ/コマンド)を与える。探索→計画→実装→コミット。プロンプトは対象ファイル・制約・既存パターン・症状を具体的に。CLAUDE.md は短く(各行「消すとミスが増えるか」)。`/clear`・サブエージェントで文脈を節約。2回修正して直らなければ `/clear` して改善プロンプトで再開。無人運転は `/goal`・Stop hook・検証サブエージェント。 |
| 2 | [Effective harnesses for long-running agents](https://anthropic.com/engineering/effective-harnesses-for-long-running-agents)(Anthropic Engineering) | 公式ブログ | 全文 | 長時間タスクは「初期化エージェント(初回のみ: 機能一覧JSON・init.sh・進捗ファイル・初回コミット)」+「コーディングエージェント(毎回: pwd→進捗ファイル+git log→機能一覧から最優先1件→init.sh+基本E2E→1機能だけ実装→検証後に passes を更新→コミット+進捗更新)」。機能一覧は Markdown でなく **JSON**(モデルが書き換えにくい)。「テストの削除・編集は許されない」と強い文言。早すぎる完了宣言・一括実装・未検証の合格を防ぐ。 |
| 3 | [How Claude remembers your project(memory)](https://code.claude.com/docs/en/memory) | 公式 | 全文(50KB) | CLAUDE.md は「文脈であって強制設定ではない」。**200行以内**が目標。具体的に検証可能な文で書く。`@path` import は4段まで(ただしlaunch時に読み込まれるため文脈コストは減らない)。`.claude/rules/*.md` の `paths:` で範囲限定。ルート CLAUDE.md は `/compact` 後もディスクから再注入される。会話だけの指示は失われる→CLAUDE.md へ。auto memory は `MEMORY.md` 先頭200行/25KB。サブエージェントは親の auto memory を見ない。`/doctor` で肥大化を点検。 |
| 4 | [Manage sessions](https://code.claude.com/docs/en/sessions) | 公式 | 全文 | トランスクリプトは `~/.claude/projects/<project>/<id>.jsonl`。`claude --resume <path/to/.jsonl>` で絶対パス指定の再開が可能。`--continue`/`--resume <名前>`/`/branch`/`--fork-session`。再開では会話・モデル・権限モード・goal は復元、`--mcp-config` 等のフラグは再指定。形式は内部仕様で版により変わる→スクリプトで直接解析しない(`/export` を使う)。 |
| 5 | [Skills](https://code.claude.com/docs/en/skills) | 公式 | 約93% | `.claude/skills/<name>/SKILL.md`(frontmatter: name, description, disable-model-invocation, context: fork, allowed-tools…)。SKILL.md は500行以内、詳細は別ファイル。本文は使うときだけ読み込まれる(CLAUDE.md より安い)。副作用のある手順は `disable-model-invocation: true`。`$ARGUMENTS`。 |
| 6 | [Hooks](https://code.claude.com/docs/en/hooks) | 公式 | 約91% | イベント: SessionStart(matcher: startup/resume/clear/compact)・PreCompact/PostCompact・Stop・PostToolUse 等。SessionStart の stdout/`additionalContext` は文脈に注入される。Stop は exit 2 / `decision:"block"` で停止を阻止できる。方針強制は hook(助言ではなく決定的)。 |
| 7 | [Subagents](https://code.claude.com/docs/en/sub-agents) | 公式 | 約92% | `.claude/agents/*.md`(name, description, tools, model, memory…)。サブエージェントは**新しい隔離文脈**で動き、親の会話・auto memory を見ない(CLAUDE.md は読む)。`memory: project` で `.claude/agent-memory/<name>/` に永続メモ。同時20・入れ子3段。 |
| 8 | [/goal](https://code.claude.com/docs/en/goal) | 公式 | 全文 | 完了条件を設定すると、毎ターン後に別モデルが判定し、満たすまで続ける。条件は「測定可能な終了状態+証明方法+触ってはいけないこと+ターン/時間上限」。評価者はコマンド実行不可で会話に出た証拠だけを見る→Claude が検証出力を会話に出すこと。`claude -p "/goal …"` で非対話も可。 |
| 9 | [What survives compaction(dev.to rulestack)](https://dev.to/rulestack/what-survives-compaction-in-claude-code-and-how-to-keep-your-rules-alive-564p) | 個人記事 | 全文 | 不変条件はルートCLAUDE.md。SessionStart(matcher=compact)で「索引(1行1不変条件+詳細ファイルへの指し先+現タスク2〜3行、約20行以内)」を再注入。丸ごと再注入は逆効果。`/compact` を意図的に試験する。 |
| 10 | [Claude Code Memory(dsebastien)](https://www.dsebastien.net/claude-code-memory/) | 個人記事 | 全文 | CLAUDE.md は60〜200行。肥大・陳腐化に注意。探索はサブエージェントへ。文脈40%超で性能低下・60%超で圧縮/整理。永続ルールはCLAUDE.md。 |
| 11 | [Teleport(claudelog)](https://claudelog.com/faqs/what-is-teleport-in-claude-code/) | 個人記事 | 全文 | Web(claude.ai/code)→ローカルCLI へ `claude --teleport [id]`(同じGitリポジトリ・ブランチ・会話を引き継ぐ)。逆は `claude --remote "task"`。 |
| 12 | [Claude Code's /goal(Daily Dose of DS)](https://blog.dailydoseofds.com/p/claude-codes-goal-command) | 個人記事 | 全文 | 良い/悪い goal 条件の実例。複合目標は分割。ターン上限を条件に入れる。auto mode併用でないと承認待ちで止まる。 |

取得できなかった/未精読: sessions の続き・skills/hooks/sub-agents ページ末尾約7〜10%(各ページ100,000文字で切れた分)、headless ページ(リダイレクトで未取得)。`docs/en/headless`・`context-window` の公式ページは取得失敗(URL出所制限)→ 内容は上記 #1・#6・#9 の記述から補った。この点は未検証として扱う。

## 調査から決めた設計(= 移行パッケージの方針)
1. **文脈ではなくファイルに状態を置く**(#2,#3): 状態の正は `migration/` + `net/session_state.md` + `tasks.json`。新しいセッションは毎回これを読んで始める。
2. **CLAUDE.md は「常に守る規則」だけ**(#1,#3,#10): 既存の CLAUDE.md は(ユーザー指示「既存情報は消さない」により)**そのまま保持**。長い履歴は `migration/USER_INSTRUCTIONS_LOG.md` に完全コピーし、要点だけを `migration/USER_INSTRUCTIONS.md` に分類整理。CLAUDE.md の追記は日時付き1行まで。
3. **SessionStart(compact)フックで索引を再注入**(#6,#9): `.claude/hooks/reinject.md`(約20行)を圧縮後・再開時に注入。
4. **機能一覧=タスク台帳をJSONに**(#2): `migration/tasks.json`(id/status/subject)。完了の判定は「検証出力を見てから」。1回に1タスク(または1群)。
5. **検証手段を明記**(#1): レンダ→`imgcheck.py`→コンタクトシート→サブエージェント監査(点数)。`/goal` の条件テンプレを `MIGRATION_PROMPT.md` に用意(ターン上限つき)。
6. **独立監査は新文脈のサブエージェント**(#1,#7): `.claude/agents/strict-auditor.md`。前回点数を渡さず、audit_rubric.md の点数基準で採点させる。
7. **「止まらない」要求の実装**(#1,#8): ターンを必ず次のツール呼び出しで終える規則(CLAUDE.md追記済)+ `/goal`(測定可能な条件)+ 必要なら Stop hook。無人は `claude -p "/goal …" --permission-mode auto`(#8)。
8. **会話ログは参照用に同梱**(#4): `migration/transcripts/*.jsonl.gz`。旧セッションの再開(`claude --resume <path>`)ではなく、HANDOFF/CONTEXT を一次情報にする(形式が版で変わるため)。
9. **セットアップを1コマンドに**(#2 init.sh): `migration/setup_workspace.sh`(リポジトリ形式→作業形式へ展開、パス置換、bpy確認)。
10. **移行プロンプトは「読む順」「ルール」「最初の1手」「検証」「終了条件」を具体的に**(#1,#2): `MIGRATION_PROMPT.md`。

## 注意(正直な限界)
- Claude Code の実環境(ローカル/クラウド)でこのパッケージを**まだ動かしていない**。`setup_workspace.sh` はこの環境(`/home/claude/station`)で構文確認・ドライランのみ。移行先での初回実行時に差分が出たら HANDOFF.md の「既知の落とし穴」に追記すること。
- 「最も効果的」は一般的な公式推奨に基づく設計であり、この案件での優劣を実験比較したものではない。
