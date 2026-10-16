# X19 完了タスク監査 — サブエージェント用ブリーフ(後ほど実施)

目的: migration/tasks.json で status=completed のタスクが「本当に完了」か、粗探しで確かめる。自己合格は不可。

## 監査員への指示(strict-auditor / general-purpose に渡す)
- 対象: 完了タスク1件ずつ。description の完了条件と、実在する証拠(コード・出力ファイル・画像・ログ)を突き合わせる。
- 証拠が無い/未確認の項目は「未完了」扱い(0点)。「たぶん」は不可。
- 判定: 完了 / 部分完了 / 未完了 と、不足点の具体一覧(ファイルパス・行・画像名)。
- 前回判定は伏せる。画像が絡む場合は複数視点を見る。

## 報告後のこちら側の処理
- 部分完了/未完了は tasks.json を in_progress に戻し、TaskList・docs/TASK_LIST.md に反映、docs/TASK_ORDER.md を再最適化。
