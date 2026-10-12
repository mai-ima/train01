---
name: strict-audit
description: 画像・形状の厳格監査を点数付きで実施する(グループ完了時・最終)。strict-auditor サブエージェントに委任する。
---
# 厳格監査の手順
1. 対象の画像を複数視点(3以上)・コンタクトシートで用意(imgcheck.py で黒/単色/白飛びを先に除外)。
2. Agent で `strict-auditor` を起動。渡すのは画像パス・対象名・docs/audit_rubric.md のみ。**前回点数は伏せる**。
3. 返却の点数表(リアルさ/差別化/内装/…)を会話に出し、net/status.json と session_state.md に正直に記録。
4. 総合95未満または軸90未満は不合格 → 修正→再レンダ→再監査。自分で合格にしない。
