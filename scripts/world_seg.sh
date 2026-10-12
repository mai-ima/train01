#!/bin/bash
# C14/X16: 隣り合う駅(M04-M05)を世界合成で繋ぎ、駅間の線路・沿線を複数視点で撮る(全駅バッチ完了後に実行)
cd "$(dirname "$(readlink -f "$0")")"
until [ -f out/e3b2/done.txt ]; do sleep 30; done
mkdir -p out/seg
MULTICAM="-765,-160,70,-765,0,0,28;-905,-7,3.0,-700,0,2.0,30;-1080,-12,3.5,-930,0,1.5,32;-560,-10,3.0,-700,0,1.5,32;-765,-14,2.0,-600,0,1.5,50" python3 main.py --world M04,M05 --parts none --cam A --w 1280 --samples 24 --draft --out seg/M04_M05 > out/seg/M04_M05.log 2>&1
echo done > out/seg/done.txt
