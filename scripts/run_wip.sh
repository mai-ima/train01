#!/bin/bash
cd /home/claude/station
export PYTHONHASHSEED=0
git -C /home/user/train01 show HEAD:net/stock_cfg.json > /tmp/stock_cfg.bakw; echo '{"M03":{"enabled":true,"consists":[{"track":0,"kind":"emu","opt":{"kind":"jnr_ltd"},"n":3},{"track":1,"kind":"emu","opt":{"kind":"jnr_exp"},"n":3}]}}' > net/stock_cfg.json
MULTICAM="26,-9,4.5,30,-4.6,3.8,40;36,-6.4,0.6,27,-4.6,0.6,40" python3 main.py --zone M03 --cam E --people off --out x13/rf2 --w 1200 --samples 24 > /tmp/wip.log 2>&1
cp /tmp/stock_cfg.bakw net/stock_cfg.json
