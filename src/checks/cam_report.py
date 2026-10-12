"""【Q11】撮影ログの『[cam] 障害物回避 … (視界スコア a→b)』『改善なし(視界スコア s)』を集計し、スコアの低い視点を再撮リストにする。
使い方: python3 cam_report.py "out/e3b*/*.log" [しきい値=0.5]   → 標準出力に一覧、out/cam_redo.txt に駅ID(重複なし)を書く"""
import glob, re, sys, os
pat = sys.argv[1] if len(sys.argv) > 1 else "out/e3b*/*.log"
th = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
rows = []
for f in sorted(glob.glob(pat)):
    sid = os.path.basename(f).split(".")[0]
    for ln in open(f, encoding="utf-8", errors="ignore"):
        m = re.search(r"\[cam\] 障害物回避: (.*?)\(視界スコア ([0-9.]+)→([0-9.]+)\)", ln)
        if m: rows.append((sid, float(m.group(3)), "回避 " + m.group(1).strip() + f" ({m.group(2)}→{m.group(3)})")); continue
        m = re.search(r"\[cam\] 障害物回避: 改善なし\(視界スコア ([0-9.]+)\)", ln)
        if m: rows.append((sid, float(m.group(1)), "改善なし"))
low = [r for r in rows if r[1] < th]
for sid, sc, note in sorted(low, key=lambda r: r[1]): print(f"{sid:6s} スコア{sc:.2f} {note}")
print(f"集計 {len(rows)} 視点 / {th} 未満 {len(low)} 視点")
open("out/cam_redo.txt", "w").write("\n".join(sorted({r[0].rstrip('L') for r in low})) + "\n")
