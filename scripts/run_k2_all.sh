#!/bin/bash
# K2: 全駅の統合検査(--interf: ドア開口・干渉・浮き・停車車両の衝突)をレンダなしで順番に実行し、結果の行を /tmp/k2_all.txt に溜める。
cd /home/claude/station
source /home/user/train01/scripts/render_guard.sh
: > /tmp/k2_all.txt
for z in $(cat /tmp/k2_ids.txt); do
  [ "$z" = "M06" ] && { echo "$z SKIP(穂波野は本体データ)" >> /tmp/k2_all.txt; continue; }
  timeout 900 python3 main.py --zone $z --interf --no-render --out k2_$z > /tmp/k2_$z.log 2>&1
  rc=$?
  { echo "== $z rc=$rc"; grep -E "^DOORS|^INTERF|^FLOAT|^STOCKHIT|Traceback|Error" /tmp/k2_$z.log | cut -c1-200; } >> /tmp/k2_all.txt
done
echo done > /tmp/k2_all.done
