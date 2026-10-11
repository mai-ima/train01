cd /home/claude/station
python3 main.py --world M09,M10 --parts none --cam WS4 --w 960 --samples 16 --out w_s4c > out/w_s4c.log 2>&1
python3 main.py --world M11,M12 --parts none --cam WS3 --w 960 --samples 16 --out w_s3c > out/w_s3c.log 2>&1
python3 main.py --world M05,M06 --parts none --cam WK --w 960 --samples 16 --out w_lcc > out/w_lcc.log 2>&1
echo done > out/we_done.txt
