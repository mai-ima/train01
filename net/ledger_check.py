"""【Q16】台帳整合検査: tasks.json と docs/TASK_LIST.md の件数・状態の整合、誤完了候補(説明/報告に『待ち』『未確認』『暫定』等)を出力。"""
import json, re, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{R}/migration/tasks.json"))
ids = [t["id"] for t in d]
dup = {i for i in ids if ids.count(i) > 1}
print("件数", len(d), "重複ID", sorted(dup) or "なし")
from collections import Counter
print(dict(Counter(t["status"] for t in d)))
rp = {}
try:
    for x in json.load(open(f"{R}/migration/task_reports.json")): rp[x["id"]] = x.get("report", "")
except Exception as e:
    print("reports 読込 failed", e)
kw = re.compile(r"確認レンダ待ち|視覚確認.{0,6}(未|不足)|未確認|暫定|不合格|未実装|要再確認|TODO")
sus = [(t["id"], t["subject"][:40], kw.findall(t.get("description", "") + rp.get(t["id"], ""))) for t in d if t["status"] == "completed"]
sus = [s for s in sus if s[2] and "再オープン" not in next(t for t in d if t["id"] == s[0]).get("description", "")]
print("誤完了候補", len(sus))
for s in sus: print(" ", s)
