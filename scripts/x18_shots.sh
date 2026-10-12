#!/bin/bash
# X18: 直近の修正の複数視点確認(M03: 駅舎正面/ホーム目線/線路脇/町並み(新ホーム縁・砂利)、R02: 船・クレーン・海面)。parts_audit.sh 完了後に実行(同時2本まで)。
cd "$(dirname "$(readlink -f "$0")")"
until [ -f out/parts_done.txt ]; do sleep 30; done
mkdir -p out/x18
PEOPLE_BOTH=1 MULTICAM="@F;@P;@R;@T;@ZA" python3 main.py --zone M03 --parts none --cam A --w 960 --samples 24 --draft --out x18/M03 > out/x18/M03.log 2>&1 &
MULTICAM="20,-15,5,95,-40,5,28;130,-15,8,90,-40,6,30;60,-80,12,90,-30,5,32;85,-8,4,100,-30,10,32" python3 main.py --zone R02 --parts none --cam A --w 960 --samples 24 --draft --out x18/R02 > out/x18/R02.log 2>&1 &
wait
echo done > out/x18/done.txt
