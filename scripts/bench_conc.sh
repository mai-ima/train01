#!/bin/bash
# W6: レンダ同時本数の計測。N本を同時に走らせ、全体の所要時間とスループット(駅/時)を out/bench/result.txt に記録する。
# 条件は E3a の1駅撮影と同じ(--draft, 960px, 24spl, 3視点×人物あり/なし)。使い方: bash bench_conc.sh   (約20〜30分)
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p out/bench; : > out/bench/result.txt
stations=(M04 M05 M08 M09 M10 M11 M14 M16)
run1() { PEOPLE_BOTH=1 MULTICAM="@A;@E;@ZA" RENDER_THREADS=$2 python3 main.py --zone $1 --parts none --cam A --w 960 --samples 24 --draft --out bench/$1_$3 > out/bench/$1_$3.log 2>&1; }
idx=0
for cfg in "1 4" "2 2" "3 1" "4 1"; do
  set -- $cfg; N=$1; TH=$2
  t0=$(date +%s)
  for ((k=0;k<N;k++)); do run1 ${stations[$((idx+k))]} $TH N${N} & done
  wait
  t1=$(date +%s)
  dt=$((t1-t0)); idx=$((idx+N))
  python3 -c "print('N=%d threads=%d 所要=%ds スループット=%.1f 駅/時' % ($N,$TH,$dt, $N*3600.0/$dt))" | tee -a out/bench/result.txt
done
echo done >> out/bench/result.txt
