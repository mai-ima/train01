"""Q25: 材質辞書 M の「参照されているが定義されていないキー」を検出する(静かなフォールバックの再発防止)。
背景: `M["asphalt"] if "asphalt" in M else M["road"]` や `g.a("white") ... if "white" in M else None` は、キーが未定義だと
エラーにならず別材質に置換される/描画が省かれる。実際に asphalt・white・brass・copper・yellow_grass が未定義だった。
使い方: python3 src/checks/matkeys_check.py [作業ディレクトリ(既定: /home/claude/station)]   終了コード: 0=問題なし / 1=未定義あり
実行時に make_materials() と kit2.mats2() / kit5.mats5() を呼んで実在キーを取得するため bpy が必要。"""
import glob, os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/station"
sys.argv = sys.argv[:1]
sys.path.insert(0, ROOT)
import bpy  # noqa: F401
import common
common.make_materials()
for mod, fn in (("kit2", "mats2"), ("kit5", "mats5")):
    try:
        getattr(__import__(mod), fn)()
    except Exception as e:
        print(f"{mod}.{fn} failed", e)
M = common.M
used = {}
for f in glob.glob(os.path.join(ROOT, "*.py")):
    t = open(f, errors="ignore").read()
    for m in re.finditer(r'(?:M\[\s*["\']([\w\-]+)["\']\s*\]|M\.get\(\s*["\']([\w\-]+)["\']|["\']([\w\-]+)["\']\s+(?:not\s+)?in\s+M\b)', t):
        k = m.group(1) or m.group(2) or m.group(3)
        used.setdefault(k, set()).add(os.path.basename(f))
# 駅ごとのビルダー(kit3/kit6/kit7/kit8)は使う直前に `M["asphalt"] = M["ug_asph"]` のように別名を定義する。
# そのため「静的な代入が1つも無く、かつ実行時にも無い」キーだけを未定義として報告する。
static = set()
for f in glob.glob(os.path.join(ROOT, "*.py")):
    t = open(f, errors="ignore").read()
    static |= set(re.findall(r'M\[\s*["\']([\w\-]+)["\']\s*\]\s*=', t))
ALLOW = {"cream"}      # train.py(現行は trainkit.py が車両材質 vmat を持つため未使用の旧車両生成)の参照。M には存在しなくてよい
missing = sorted(k for k in used if k not in M and k not in static and k not in ALLOW)
for k in missing:
    print("未定義の材質キー:", k, sorted(used[k]))
print(f"材質キー 参照{len(used)}種 / 未定義{len(missing)}種")
sys.exit(1 if missing else 0)
