---
name: record-instruction
description: ユーザーから新しい指示を受けたら、取りこぼさないよう各ファイルへ即記録しタスクを再最適化する。
---
# 指示の記録
1. CLAUDE.md 末尾に `- (YYYY-MM-DD HH:MM) ユーザー指示: …` を**追記**(削除・短縮禁止)。
2. migration/USER_INSTRUCTIONS.md の該当カテゴリに1行追加。net/session_state.md に追記。
3. migration/tasks.json にタスク追加/更新し、群記号+番号(net/taxonomy.md)で命名。「最優先」と書かれた時だけ `S-`。
4. 優先順を再最適化し、日本語で一言報告。
