cd "$(dirname "$(readlink -f "$0")")"
while [ ! -f out/zb_done.txt ]; do sleep 8; done
python3 main.py --world M09,M10 --parts none --cam WS4 --w 960 --samples 16 --out w_s4b > out/w_s4b.log 2>&1
python3 main.py --world M11,M12 --parts none --cam WS3 --w 960 --samples 16 --out w_s3b > out/w_s3b.log 2>&1
python3 main.py --world M05,M06 --parts none --cam WK --w 960 --samples 16 --out w_lcb > out/w_lcb.log 2>&1
echo done > out/wc_done.txt
