cd "$(dirname "$(readlink -f "$0")")"
python3 main.py --world M12,M13 --parts none --cam WS6 --w 960 --samples 16 --out w_s6 > out/w_s6.log 2>&1
echo done > out/wf_done.txt
