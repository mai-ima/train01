#!/bin/bash
cd /home/claude/station
export PYTHONHASHSEED=0
git -C /home/user/train01 show HEAD:net/stock_cfg.json > /tmp/stock_cfg.bakw; echo '{"M03":{"enabled":true,"consists":[{"track":0,"kind":"emu","opt":{"kind":"jnr_dc"},"n":3},{"track":1,"kind":"emu","opt":{"kind":"jnr_sub"},"n":3}]}}' > net/stock_cfg.json
MULTICAM="0,-12,2.2,0,-2,2.4,28;38,-9,0.9,25,-4.6,1.0,32" python3 main.py --zone M03 --cam E --people off --out x13/sd1 --w 1200 --samples 24 > /tmp/wip.log 2>&1
cp /tmp/stock_cfg.bakw net/stock_cfg.json
