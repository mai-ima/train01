#!/bin/bash
# Stop フック: 未完了タスクがある限り、ターンの終了をブロックして作業継続を促す(ユーザー指示: 完成まで止まらない)。
# 解除: ユーザーが「止めてよい」と言った時は  touch "$CLAUDE_PROJECT_DIR/.claude/ALLOW_STOP"
D="${CLAUDE_PROJECT_DIR:-$(pwd)}"
[ -f "$D/.claude/ALLOW_STOP" ] && exit 0
N=$(python3 - "$D/migration/tasks.json" <<'P'
import json,sys
try: print(sum(1 for t in json.load(open(sys.argv[1])) if t.get("status")!="completed"))
except Exception: print(0)
P
)
if [ "${N:-0}" -gt 0 ]; then
  echo "未完了タスクが ${N} 件あります。終了せず、次のツール呼び出し(実装・レンダ・検査・監査)で作業を続けてください。待機中は別作業を並行して進めること。" >&2
  exit 2
fi
exit 0
