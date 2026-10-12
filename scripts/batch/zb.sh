cd /home/claude/station
for s in "$@"; do
  python3 main.py --zone $s --parts none --cam ZA --w 800 --samples 12 --out zb_$s > out/zb_$s.log 2>&1
done
echo done > out/zb_done.txt
