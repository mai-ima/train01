#!/bin/bash
# E5再撮(カメラfallback修正後の特殊駅)(W6採用: 同時3本×RENDER_THREADS=1(重い駅は1プロセス最大約4.4GB。4本だと16GBを超えOOM killされる))。M01/M06 は特殊(本体データ+専用カメラ)なので除外。
# 使い方: bash e5_all.sh <駅ID...>   出力 out/e5r/<ID>_<n>.png, 完了印 out/e5r/done_<ID>
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p out/e5r
printf '%s\n' "$@" | xargs -P 3 -I{} bash -c 'RENDER_THREADS=1 MULTICAM="@A;@E;@ZA;@L;@F;@P" python3 main.py --zone {} --parts none --cam A --w 960 --samples 20 --draft --out e5r/{} > out/e5r/{}.log 2>&1; touch out/e5r/done_{}'
echo all_done >> out/e5r/done_all.txt
