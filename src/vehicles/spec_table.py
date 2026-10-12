"""vehtypes.py の TYPES(dict(...)リテラル)から net/vehicle_spec.md を生成する(bpy不要)。"""
import ast
src = open("/home/claude/station/vehtypes.py").read()
tree = ast.parse(src)
rows = {}
for n in ast.walk(tree):
    if isinstance(n, ast.Dict):
        for k, v in zip(n.keys, n.values):
            if isinstance(k, ast.Constant) and isinstance(k.value, str) and isinstance(v, ast.Call) and getattr(v.func, "id", "") == "dict":
                try:
                    rows[k.value] = {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords if kw.arg}
                except Exception:
                    pass
cols = [("title", "名称"), ("L", "全長m"), ("W", "幅m"), ("front", "前面"), ("win", "窓"), ("pattern", "窓扉割(右)"), ("pattern2", "窓扉割(左)"), ("ds", "扉"), ("ps", "外板"),
        ("lo", "下塗色"), ("up", "上塗色"), ("roofshape", "屋根"), ("roof", "屋根上機器"), ("bogie", "台車"), ("under", "床下"), ("interior", "室内"), ("seat", "座席"), ("lamp", "室内灯"), ("fs", "前面表示"), ("ss", "側面表示")]
out = ["# 車両仕様表(自動生成: spec_table.py ← vehtypes.TYPES)", "", "実在車両のデザイン(窓割・前面・台車・屋根機器・塗色)を参考にしつつ、社名・標章は使わない。機関車は公開諸元ベース。", "",
       "| 形式 | " + " | ".join(c[1] for c in cols) + " |", "|" + "---|" * (len(cols) + 1)]
for t, d in rows.items():
    if "title" not in d:
        continue
    out.append(f"| {t} | " + " | ".join(str(d.get(c[0], "")).replace("|", "/") for c in cols) + " |")
# 差別化チェック: 組(窓扉割,扉,外板,前面)が同一の形式を警告
seen = {}
for t, d in rows.items():
    k = (d.get("pattern"), d.get("ds"), d.get("ps"), d.get("front"))
    seen.setdefault(k, []).append(t)
dup = [v for v in seen.values() if len(v) > 1]
out += ["", "## 差別化チェック(窓扉割・扉・外板・前面が全て同じ形式の組)", "なし" if not dup else "\n".join("- " + ", ".join(v) for v in dup)]
open("/home/claude/station/net/vehicle_spec.md", "w").write("\n".join(out) + "\n")
print(len(rows), "types; dup:", dup)
