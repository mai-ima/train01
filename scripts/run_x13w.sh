#!/bin/bash
cd /home/claude/station
export PYTHONHASHSEED=0
cp /home/user/train01/net/stock_cfg.json /tmp/stock_cfg.bakd
CAMS="41,-10,2.4,30,-4.6,2.6,36;-41,-10,2.4,-30,-4.6,2.6,36;-41,-4.6,2.0,-30,-4.6,2.4,40"
echo '{"M03":{"enabled":true,"consists":[{"track":0,"kind":"emu","opt":{"kind":"jnr_ac"},"n":3},{"track":1,"kind":"emu","opt":{"kind":"jnr_ac"},"n":3}]}}' > net/stock_cfg.json
MULTICAM="$CAMS" python3 main.py --zone M03 --cam E --people off --out x13w/kiha_off --w 1200 --samples 24 > /tmp/x13w.log 2>&1
cp /tmp/stock_cfg.bakd net/stock_cfg.json
echo done > /tmp/x13w.done
