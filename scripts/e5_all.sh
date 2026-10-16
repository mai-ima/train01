#!/bin/bash
# E5/E6/E3 全駅撮影(W6採用: 同時3本×RENDER_THREADS=1(重い駅は1プロセス最大約4.4GB。4本だと16GBを超えOOM killされる))。M01/M06 は特殊(本体データ+専用カメラ)なので除外。
# 使い方: bash e5_all.sh <駅ID...>   出力 out/e5/<ID>_<n>.png, 完了印 out/e5/done_<ID>
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p out/e5
printf '%s\n' "$@" | xargs -P 3 -I{} bash -c 'RENDER_THREADS=1 MULTICAM="@A;@E;@ZA;@L;@F;@P" python3 main.py --zone {} --parts none --cam A --w 960 --samples 20 --draft --out e5/{} > out/e5/{}.log 2>&1; touch out/e5/done_{}'
echo all_done >> out/e5/done_all.txt
