cd "$(dirname "$(readlink -f "$0")")"
python3 main.py --world M09,M10 --parts none --cam WS1 --w 960 --samples 16 --out w_s1 > out/w_s1.log 2>&1
python3 main.py --world M03,M04 --parts none --cam WS2 --w 960 --samples 16 --out w_s2 > out/w_s2.log 2>&1
python3 main.py --world M11,M12 --parts none --cam WS3 --w 960 --samples 16 --out w_s3 > out/w_s3.log 2>&1
