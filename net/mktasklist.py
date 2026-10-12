"""docs/TASK_LIST.md を生成する(【S-T1】)。
入力: migration/tasks.json(状態の正) + migration/task_reports.json(完了順・報告) + migration/task_progress.json(進行中の報告)
使い方: python3 net/mktasklist.py   (リポジトリ直下から)。タスクを完了したら task_reports.json の末尾に {order,id,basis,report} を追記して再実行する。"""
import json, os, re, collections, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(R, p)))
tasks = {x['id']: x for x in J('migration/tasks.json')}
reports = J('migration/task_reports.json')
prog = J('migration/task_progress.json')
rep_ids = [r['id'] for r in reports]
for i, x in tasks.items():                      # 完了なのに報告が無いもの(新規完了)は末尾に『報告未記入』として追加
    if x['status'] == 'completed' and i not in rep_ids:
        reports.append({"order": len(reports) + 1, "id": i, "basis": "—", "report": "(報告未記入。task_reports.json に追記してください)"})
cnt = collections.Counter(x['status'] for x in tasks.values())
def grp(s):
    m = re.search(r'【(S-)?([A-Za-zぁ-んァ-ン一-龥]+)', s)
    return (m.group(2) if m else '-')
out = []
w = out.append
w("# タスク一覧(新)— 全タスク・未実行はそのまま・実行済みは実行順+報告")
w("")
w(f"生成: net/mktasklist.py({datetime.date.today()})。状態の正は `migration/tasks.json`。タスク名は `net/taxonomy.md` の「群記号+番号」、**S- はユーザーが『最優先』と明記したもの**。")
w(f"件数: 全 {len(tasks)} 件 = 完了 {cnt['completed']} / 進行中 {cnt['in_progress']} / 未実行 {cnt['pending']}")
w("")
w("> **完了順についての正直な注記**: 旧セッション(claude.ai)の個別の作業ログは圧縮で失われており、完了時刻を持つ記録は git 履歴と作業ログの一部だけです。各行の「根拠」に `git`(コミット)/`セッション要約`/`ID順(推定)`/`Claude Code`(本セッション)を示します。`ID順(推定)` は台帳IDの小さい順で、**厳密な完了順ではありません**。報告は台帳・コード・文書からの再構成で、旧セッションで実施した詳細な検証結果は確認できていません。")
w("")
w("## 目次")
w("1. [未実行(そのまま)](#1-未実行そのまま)  2. [進行中(報告つき)](#2-進行中報告つき)  3. [完了(実行順・報告つき)](#3-完了実行順報告つき)")
w("")
w("## 1. 未実行(そのまま)")
w("実行順の指針は `net/session_state.md` の「タスク実行順」(車両 F → 構造 Z-A → B6 → … → 最終監査 X9 → 修正ループ Z-G1 → 納品 G)。")
w("")
w("| ID | タスク |")
w("|---|---|")
for i in sorted(tasks):
    if tasks[i]['status'] == 'pending':
        s = tasks[i]['subject'].replace('|', '/')
        w(f"| #{i} | {s} |")
w("")
w("## 1b. 実行順(最適化 2026-10-12)")
w("方針: **先に『納品可能な状態』を完成**させ(リスク低減)、その後に群ごとに『実装→複数視点撮影(人物あり/なし)→healthscan→独立監査(2名・超超超厳格)→修正』を回して品質を上げる。")
w("")
w("1. **基盤・健全性**(完了/進行): 根本原因対策 S-Q7、撮影バッチの健全性スキャン W4、全駅の撮り直し E3a(進行中)。")
w("2. **納品の先行完成**: G1a(全42ゾーン.blend 27MB以下)→ G1b(全景/目線/俯瞰レンダ・パノラマ)→ 路線図(R9 済)→ G3 納品物整備。※品質は暫定(未合格)と明記して納める。")
w("3. **車両 F 群**: F5b〜e(実車準拠: 窓割/前面/台車/座席)→ F3c/F3d2 の修正 → F3e 車両監査 → F3f(ほなみ等)→ F4(結)→ P6/X11(画像)→ X13 再監査。")
w("4. **構造 Z-A 群**: Z-A3〜A8(素材・意匠)→ Z-A15 監査 → C7 構造物監査。")
w("5. **駅内部 B6 群**: B6b〜d(特殊駅・ホーム設備・階段/通路/事務室)→ K2/K6(検査)。")
w("6. **駅・町 B/E/T 群**: B3(テンプレ感)→ N3 → B7/T3 → E1/E2。")
w("7. **新車庫 D4〜D9・V3・R4・X7**。")
w("8. **群監査 X1〜X7 → 最終 X9(最終超超超高レベル監査)→ 修正ループ Z-G1 → 最終納品 G1/G3**。")
w("")
w("## 2. 進行中(報告つき)")
w("")
for i in sorted(tasks):
    if tasks[i]['status'] == 'in_progress':
        w(f"- **#{i} {tasks[i]['subject']}**")
        w(f"  - 報告: {prog.get(str(i), '(報告未記入。task_progress.json に追記してください)')}")
w("")
w("## 3. 完了(実行順・報告つき)")
w("")
w("| 順 | ID | タスク | 根拠 | 報告 |")
w("|---|---|---|---|---|")
for r in sorted(reports, key=lambda r: r['order']):
    i = r['id']
    if i not in tasks:
        continue
    s = tasks[i]['subject'].replace('|', '/')
    w(f"| {r['order']} | #{i} | {s} | {r['basis']} | {r['report'].replace('|', '/')} |")
w("")
open(os.path.join(R, 'docs/TASK_LIST.md'), 'w').write('\n'.join(out) + '\n')
print('docs/TASK_LIST.md', len(out), 'lines;', dict(cnt))
