# 移行パッケージ(S-MG1) — claude.ai セッション → Claude Code

**目的**: このセッションの文脈・記憶・タスク・計画をすべてファイル化し、Claude Code で続きを進める。既存ファイル/情報は消していない(追記・複製のみ)。

## 5ステップ
1. `git clone https://github.com/mai-ima/train01 && cd train01`(Claude Code をここで起動。`.claude/` の設定・スキル・サブエージェントが自動で有効)
2. `bash migration/setup_workspace.sh`(作業形式 /home/claude/station へ展開+パス置換+依存確認)
3. `MIGRATION_PROMPT.md` の **A** を最初のメッセージに貼る(無人連続運転は **C** の `/goal`)
4. Claude が `CLAUDE.md → USER_INSTRUCTIONS.md → HANDOFF.md → CONTEXT.md → tasks.json → net/session_state.md` を読み、現在地を日本語で報告 → 作業再開
5. 以後、節目ごとに tasks.json / session_state.md を更新し、`scripts/sync_repo.sh` 等でコミット+push 【補足(2026-10-16): sync_repo.sh は使用禁止(repo を全削除して再コピーする)。コミットは通常の git add/commit/push、作業側→repoの一方向コピーは scripts/sync_safe.sh。Claude-Session は現セッションのID(system指示)を使う】

## ファイル一覧
| ファイル | 内容 |
|---|---|
| MIGRATION_PROMPT.md | 移行プロンプト(標準A・短縮B・/goal C) |
| HANDOFF.md | 概要・構造・現状(正直)・次の一手・落とし穴 |
| CONTEXT.md | 技術メモ・失敗と対処・監査点数の履歴 |
| USER_INSTRUCTIONS.md / _LOG.md | 指示の分類整理 / CLAUDE.md の原文コピー |
| TASKS.md / tasks.json | 全184タスク台帳(完了95・進行10・未着手79) |
| KEY_FILES.md / COMMANDS.md | 主要ファイル / コマンド集 |
| research_handoff.md | 調査したソースと設計判断・限界 |
| setup_workspace.sh | 展開スクリプト(冪等) |
| transcripts/*.jsonl.gz | 旧セッションの生ログ(参照用) |
| ../.claude/ | settings.json(SessionStart フック)、hooks/reinject.md、skills(resume-work, strict-audit, record-instruction)、agents/strict-auditor.md |

## 会話ログ(jsonl)
`transcripts/session_*.jsonl.gz` に旧セッションの生ログを同梱(ユーザーが 2026-10-12 19:40 に許可)。`gunzip -k` で展開。形式は版依存のため一次情報は HANDOFF/CONTEXT。検索例: `grep -n '"role":"user"' x.jsonl | tail -40`。

## 限界(正直に)
Claude Code 実環境では未実行。setup_workspace.sh はドライラン(展開・パス置換・bpy確認)のみ検証済み。ログ(jsonl)の形式は版依存。
