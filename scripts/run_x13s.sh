#!/bin/bash
cd /home/claude/station
export PYTHONHASHSEED=0
cp /home/user/train01/net/stock_cfg.json /tmp/stock_cfg.bakd
CAMS="41,-10,2.4,30,-4.6,2.6,36;41,-4.6,2.3,30,-4.6,2.6,40;-41,-10,2.4,-30,-4.6,2.6,36;15,-14,7,0,-2,2.5,30;38,-9,0.9,25,-4.6,1.0,32;0,-12,2.2,0,-2,2.4,28;10,-4.6,7.5,2,-4.6,3.4,34;36,-6.4,0.6,27,-4.6,0.6,40"
echo "{\"M03\":{\"enabled\":true,\"consists\":[{\"track\":0,\"kind\":\"emu\",\"opt\":{\"kind\":\"ke\"},\"n\":3},{\"track\":1,\"kind\":\"emu\",\"opt\":{\"kind\":\"jnr_ac\"},\"n\":3}]}}" > net/stock_cfg.json
MULTICAM="$CAMS" python3 main.py --zone M03 --cam E --people off --out x13s/emuC_off --w 1200 --samples 24 > /tmp/x13s_emuC_off.log 2>&1
cp /tmp/stock_cfg.bakd net/stock_cfg.json
