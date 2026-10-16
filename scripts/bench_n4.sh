#!/bin/bash
# W6 追補: N=4×1スレッドを4駅で正しく計測(前回は駅リスト不足で実質2駅だった)
cd "$(dirname "$(readlink -f "$0")")"
t0=$(date +%s)
for s in M14 M16 M18 TR02; do
  NEAR_GRASS=0 TREE_CARDS=0.22 PEOPLE_BOTH=1 MULTICAM="@A;@E;@ZA" RENDER_THREADS=1 python3 main.py --zone $s --parts none --cam A --w 960 --samples 24 --draft --out bench/${s}_N4b > out/bench/${s}_N4b.log 2>&1 &
done
wait
t1=$(date +%s); dt=$((t1-t0))
python3 -c "print('N=4(補正) threads=1 所要=%ds スループット=%.1f 駅/時' % ($dt, 4*3600.0/$dt))" | tee -a out/bench/result.txt
echo done2 >> out/bench/result.txt
