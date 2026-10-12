#!/bin/bash
# X15 部品単位の監査用撮影(線路・レール・枕木・バラスト・継目・電柱・架線・ホーム縁・階段など)。M04 川原ゾーン(線路 y=0/-4.1/-10.7)で近接5〜6視点。
# 使い方: bash parts_audit.sh   → out/parts/M04_<n>.png(人物なし/あり両方は PEOPLE_BOTH=1)
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p out/parts
# x,y,z,tx,ty,tz,lens ; で区切る
CAMS="3,-1.8,0.9,0,-4.1,0.3,35;8,-4.1,0.5,0,-4.1,0.3,40;-6,-7.0,1.2,0,-4.1,0.3,45;2,-4.1,0.45,-8,-4.1,0.3,50;0,-9.5,1.0,0,-4.1,0.9,35;12,-6.0,2.0,0,-4.1,1.0,30"
PEOPLE_BOTH=0 MULTICAM="$CAMS" python3 main.py --zone M04 --parts none --cam A --w 1280 --samples 48 --draft --out parts/M04
