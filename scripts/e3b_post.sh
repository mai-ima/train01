#!/bin/bash
# E3a 後処理: バッチ完了を待って、(1) 穂波野 M06 は「以前作成した本体データ」(--zone を使わない)で撮影、(2) 旧ロジックで撮った駅(out/e3b_redo.txt)を再撮。2並列。
cd "$(dirname "$(readlink -f "$0")")"
until [ -f out/e3b/done.txt ]; do sleep 30; done
mkdir -p out/e3b2
( PEOPLE_BOTH=1 MULTICAM="@H;@C;@B;@D;@G;@Z1;@ZT" python3 main.py --parts core,station,depot,props,train,veg,hq,life --cam A --w 960 --samples 24 --draft --out e3b2/M06 > out/e3b2/M06.log 2>&1 ) &
( for s in $(grep -v '^M06$' out/e3b_redo.txt); do
    PEOPLE_BOTH=1 MULTICAM="@A;@E;@ZA" python3 main.py --zone $s --parts none --cam A --w 960 --samples 24 --draft --out e3b2/$s > out/e3b2/$s.log 2>&1
    python3 healthscan.py out/e3b2/$s.log >> out/e3b2/HEALTH.txt 2>&1 || echo "NG $s" >> out/e3b2/HEALTH_NG.txt
  done ) &
wait
echo done > out/e3b2/done.txt
