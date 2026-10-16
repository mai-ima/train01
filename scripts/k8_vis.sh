#!/bin/bash
# K8 視覚確認: 指定駅を同時に最大4本×1スレッドで撮る(W6の採用値)。使い方: bash k8_vis.sh M07 S04 M05 M08
cd "$(dirname "$(readlink -f "$0")")"
for s in "$@"; do
  RENDER_THREADS=1 MULTICAM="@A;@E;@ZA;@F" python3 main.py --zone $s --parts none --cam A --w 960 --samples 20 --draft --out k8v_$s > out/k8v_$s.log 2>&1 &
done
wait
echo vis_done >> out/k8v_done.txt
