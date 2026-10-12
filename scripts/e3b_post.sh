#!/bin/bash
# E3a 後処理: バッチ完了を待って、(1) 穂波野 M06 は「以前作成した本体データ」(--zone なし)を専用カメラで撮影、(2) 旧ロジックで撮った駅(out/e3b_redo.txt)を A/E/ZA/L で再撮、(3) 全駅を象徴物カメラ @L で撮影。2並列。
cd "$(dirname "$(readlink -f "$0")")"
until [ -f out/e3b/done.txt ]; do sleep 30; done
mkdir -p out/e3b2
( PEOPLE_BOTH=1 MULTICAM="@H;@C;@B;@D;@G;@Z1;@ZT" python3 main.py --parts core,station,depot,props,train,veg,hq,life --cam A --w 960 --samples 24 --draft --out e3b2/M06 > out/e3b2/M06.log 2>&1 ) &
( for s in $(grep -v '^M06$' out/e3b_redo.txt); do
    PEOPLE_BOTH=1 MULTICAM="@A;@E;@ZA;@L" python3 main.py --zone $s --parts none --cam A --w 960 --samples 24 --draft --out e3b2/$s > out/e3b2/$s.log 2>&1
    python3 healthscan.py out/e3b2/$s.log >> out/e3b2/HEALTH.txt 2>&1 || echo "NG $s" >> out/e3b2/HEALTH_NG.txt
  done ) &
wait
# 象徴物カメラ @L を redo 以外の全駅で撮る(2並列)
ids=$(python3 -c "
import kit
print(' '.join(k for k in kit.ST))" 2>/dev/null)
rest=""
for s in $ids; do grep -qx "$s" out/e3b_redo.txt || [ "$s" = "M06" ] || rest="$rest $s"; done
A=(); B=(); i=0
for s in $rest; do if [ $((i%2)) -eq 0 ]; then A+=($s); else B+=($s); fi; i=$((i+1)); done
lw() { for s in "$@"; do PEOPLE_BOTH=1 MULTICAM="@L" python3 main.py --zone $s --parts none --cam A --w 960 --samples 24 --draft --out e3b2/${s}L > out/e3b2/${s}L.log 2>&1; done; }
lw "${A[@]}" &
lw "${B[@]}" &
wait
echo done > out/e3b2/done.txt
