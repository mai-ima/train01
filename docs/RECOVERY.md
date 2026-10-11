# コンテキスト圧縮後の記憶回復手順(ユーザー最優先指定 2026-10-11)

圧縮(要約)直後は、作業を再開する前に必ず以下を上から順に実行する。

1. **CLAUDE.md を全文読む**(`/home/claude/train01/CLAUDE.md`。station 側と同内容)。
2. **作業状態ファイル `net/session_state.md` を読む**(現在地・直前の作業・次の一手・保留中の判断。節目ごとに更新している)。
3. **TaskList を確認**(進行中=in_progress を最優先、次に S- 付き、続いて pending を群順に)。
4. **会話ログを確認**: `/root/.claude/projects/-home-claude*/*.jsonl` の末尾~数百行(ユーザー発言は `"role":"user"` を grep)。
   `grep -n '"role":"user"' <jsonl> | tail -40` で直近のユーザー指示を拾う。
5. **主要ファイルを確認**: net/network.py, kit.py, main.py, common.py, trackkit.py, rooms.py, props.py, houses.py, kit4〜kit8.py(必要部分)。
6. **未了事項・恒久指示の再確認**(国鉄/JNR名称維持, 機関車は公開諸元ベースと納品時に伝える, 室内まで, 日本語, 並行作業しない(ユーザー指定時), 複数角度で視覚確認, 監査はグループ完了時と最終, 「最優先」はユーザー明記のみ S- を付ける)。
7. `git -C /home/claude/train01 status` で未コミットを確認し、節目なら sync_repo.sh でコミット/push。
8. 回復できたら一言「回復完了: 現在は◯◯、次は△△」を日本語で SendUserMessage し、作業再開。

## 運用
- 節目(タスク完了・方針変更・ユーザー指示受領)のたびに `net/session_state.md` を更新する。
- ユーザーの新指示は受領直後に CLAUDE.md と TaskList に反映(取りこぼし防止)。
- 圧縮が近いと感じたら、先に session_state.md を最新化してから作業を続ける。
