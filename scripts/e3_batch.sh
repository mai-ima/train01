#!/bin/bash
# E3: 全駅を「1回の構築で 3カメラ(A目線/E斜め/ZA俯瞰) × 人物 表示/非表示」で撮る。2並列。完了で out/e3b/done.txt
# 出力: out/e3b/<SID>_<n>.png(人物あり) / out/e3b/<SID>_np_<n>.png(人物なし)  n=0:A 1:E 2:ZA
cd /home/claude/station
mkdir -p out/e3b
ids=$(python3 -c "
import kit
print(' '.join(k for k in kit.ST))" 2>/dev/null)
W=${E3_W:-960}; SPL=${E3_SPL:-24}
worker() {
  for s in "$@"; do
    [ -f out/e3b/${s}_np_2.png ] && continue
    PEOPLE_BOTH=1 MULTICAM="@A;@E;@ZA" python3 main.py --zone $s --parts none --cam A --w $W --samples $SPL --out e3b/$s > out/e3b/$s.log 2>&1
    python3 healthscan.py out/e3b/$s.log >> out/e3b/HEALTH.txt 2>&1 || echo "NG $s (ログに failed/Traceback)" >> out/e3b/HEALTH_NG.txt
  done
}
set -- $ids
A=(); B=(); i=0
for s in "$@"; do if [ $((i%2)) -eq 0 ]; then A+=($s); else B+=($s); fi; i=$((i+1)); done
worker "${A[@]}" &
worker "${B[@]}" &
wait
python3 healthscan.py "out/e3b/*.log" > out/e3b/HEALTH_SUMMARY.txt 2>&1
echo done > out/e3b/done.txt
