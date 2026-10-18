#!/bin/bash
cd /home/claude/station
export PYTHONHASHSEED=0
cp net/stock_cfg.json /tmp/stock_cfg.bakd
CAMS="41,-10,2.4,30,-4.6,2.6,36;41,-4.6,2.3,30,-4.6,2.6,40;-41,-10,2.4,-30,-4.6,2.6,36;15,-14,7,0,-2,2.5,30;38,-9,0.9,25,-4.6,1.0,32;0,-12,2.2,0,-2,2.4,28;10,-4.6,7.5,2,-4.6,3.4,34;36,-6.4,0.6,27,-4.6,0.6,40"
run(){ # name kindA kindB ppl
  echo "{\"M03\":{\"enabled\":true,\"consists\":[{\"track\":0,\"kind\":\"$2\",\"opt\":{\"kind\":\"$3\"},\"n\":3},{\"track\":1,\"kind\":\"$4\",\"opt\":{\"kind\":\"$5\"},\"n\":3}]}}" > net/stock_cfg.json
  MULTICAM="$CAMS" python3 main.py --zone M03 --cam E --people $6 --out x13g/$1_$6 --w 1200 --samples 24 > /tmp/x13g_$1_$6.log 2>&1
}
for p in on off; do
 run emuA emu jnr_dc emu jnr_sub $p
 run emuB emu jnr_exp emu jnr_ltd $p
 run kiha kiha kiha_ltd kiha kiha_exp $p
 run emuC emu ke emu jnr_ac $p
done
cp /tmp/stock_cfg.bakd net/stock_cfg.json
