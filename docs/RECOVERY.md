# コンテキスト圧縮後の記憶回復手順(ユーザー最優先指定 2026-10-11)

圧縮(要約)直後は、作業を再開する前に必ず以下を上から順に実行する。

0. **まず `bash /home/claude/station/recovery_snapshot.sh` を1回実行**(CLAUDE.md末尾・状態・直近ユーザー指示・git・実行中ジョブを一括表示。圧縮要約には直後に届いた割り込み指示が載らないことがあるため必ず確認)。
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

## 圧縮前チェック(圧縮が近い/大きな切替の前)
- session_state.md に「現在地・次の一手・中断作業の再開めど・未コミット・実行中の背景ジョブ(監視ID)」を書く。
- 途中の割り込み指示(例: 最優先の路線図v2.4.5)は、元作業の再開手順とセットで記録する。
- 背景モニタ(Monitor/チェーン)が走っているなら名前と目的を session_state.md に書く(要約に残らないため)。
- 圧縮直後に受け取ったユーザー指示は、回復手順の完了後すぐ TaskList に反映する。

## 注意(会話ログの限界)
- 会話ログ(.jsonl)には圧縮後の割り込み指示が user 行として残らないことがある。ユーザー指示は受領直後に必ず CLAUDE.md の末尾へ日時つきで追記する(これが唯一確実な記録)。
- 「以前の方式」(TaskList確認→会話ログ確認→主要ファイル確認→未了/恒久指示の再確認)と「強化版」(recovery_snapshot.sh→RECOVERY.md手順0〜8→圧縮前チェック)は両方を毎回実施する。
