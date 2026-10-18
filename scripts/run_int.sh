#!/bin/bash
# 車内の目線撮影(F3d2/F5e 用): M03 の停車編成の内部から。人物 on/off。使い方: bash run_int.sh <名前> <車種> <人物on|off>
cd /home/claude/station
export PYTHONHASHSEED=0
git -C /home/user/train01 show HEAD:net/stock_cfg.json > /tmp/stock_cfg.bakint
echo "{\"M03\":{\"enabled\":true,\"consists\":[{\"track\":0,\"kind\":\"emu\",\"opt\":{\"kind\":\"$2\"},\"n\":3},{\"track\":1,\"kind\":\"emu\",\"opt\":{\"kind\":\"jnr_sub\"},\"n\":3}]}}" > net/stock_cfg.json
MULTICAM="33,-4.6,1.55,24,-4.6,1.5,60;28,-5.6,1.4,28,-3.6,1.2,70;30,-4.6,2.25,22,-4.6,1.3,55" python3 main.py --zone M03 --cam E --people $3 --out int/$1_$3 --w 1200 --samples 24 > /tmp/int_$1_$3.log 2>&1
cp /tmp/stock_cfg.bakint net/stock_cfg.json
