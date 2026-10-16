#!/bin/bash
# K8: 全ゾーンのモデル間干渉検査(--no-render)。使い方: bash k8_all.sh <駅ID...>  並列3(メモリ影響小)。結果 out/mc_<ID>.json と out/mc_all.txt
cd "$(dirname "$(readlink -f "$0")")"
: > out/mc_all.txt
printf '%s\n' "$@" | xargs -P 3 -I{} bash -c 'MODELCHECK=out/mc_{}.json timeout 900 python3 main.py --zone {} --parts none --cam A --no-render 2>&1 | grep -E "MODELCHECK|Traceback|Error" | sed "s/^/{} /" >> out/mc_all.txt'
echo done >> out/mc_all.txt
