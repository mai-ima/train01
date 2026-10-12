cd /home/claude/station
for s in "$@"; do
  python3 main.py --zone $s --parts none --cam ZA --w 900 --samples 10 --out zs_$s > out/zs_$s.log 2>&1
done
echo done > out/zs_done.txt
