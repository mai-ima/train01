cd /home/claude/station
while [ ! -f out/wc_done.txt ]; do sleep 8; done
python3 main.py --world M09,M10 --parts none --cam WS4 --w 960 --samples 16 --out w_s4c > out/w_s4c.log 2>&1
python3 main.py --world M09,M10 --parts none --cam WS1 --w 960 --samples 16 --out w_s1c > out/w_s1c.log 2>&1
echo done > out/wd_done.txt
