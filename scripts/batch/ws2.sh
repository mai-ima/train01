cd "$(dirname "$(readlink -f "$0")")"
while pgrep -x -f "bash ./ws.sh" >/dev/null; do sleep 5; done
python3 main.py --world M09,M10 --parts none --cam WS4 --w 960 --samples 16 --out w_s4 > out/w_s4.log 2>&1
python3 main.py --world M05,M06 --parts none --cam WK --w 960 --samples 16 --out w_lc > out/w_lc.log 2>&1
