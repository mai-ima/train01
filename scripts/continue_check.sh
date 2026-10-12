#!/bin/bash
# ターン終了前チェック: 未完了があれば終了せず続行するための確認
cd /home/claude/station
echo "=== 未コミット(train01) ==="; git -C /home/user/train01 status --short | head -5
echo "=== 実行中ジョブ ==="; pgrep -af "main.py|blender" | head -3
echo "=== 次の一手(session_state末尾) ==="; tail -4 net/session_state.md
echo "→ 未完了タスクがある限り終了せず、TaskListのin_progress/pendingを実行すること(CLAUDE.md 停止再発防止ルール)"
