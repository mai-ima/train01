---
name: resume-work
description: 新しいセッション開始時・圧縮後・/clear 後に、train01 の作業状態を回復して再開する手順。
---
# 作業再開手順
1. `bash scripts/recovery_snapshot.sh`(無ければ `tail -60 net/session_state.md` と `git status`)。
2. CLAUDE.md を全文、migration/HANDOFF.md → CONTEXT.md → USER_INSTRUCTIONS.md を読む。
3. `migration/tasks.json` の in_progress/pending(群順)を確認。
4. 日本語で「現在地・守るルール上位10・最初のタスク」を3〜10行で報告。
5. 最初のタスクに着手(止まらない)。詳細は docs/RECOVERY.md。
