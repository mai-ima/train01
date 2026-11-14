#!/bin/bash
# K2: 浮き判定(floatcheck)を変更した後の回帰確認。代表駅の FLOAT 行だけを /tmp/k2_float.txt に溜める。
cd /home/claude/station
source /home/user/train01/scripts/render_guard.sh
: > /tmp/k2_float.txt
for z in K03 B02 M19 SH04 M01 T02 Y03; do
  timeout 900 python3 main.py --zone $z --interf --no-render --out k2f_$z > /tmp/k2f_$z.log 2>&1
  { echo "== $z rc=$?"; grep -E "^FLOAT|Traceback" /tmp/k2f_$z.log | cut -c1-240; } >> /tmp/k2_float.txt
done
echo done > /tmp/k2_float.done
