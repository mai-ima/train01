cd "$(dirname "$(readlink -f "$0")")"
for s in "$@"; do
  python3 main.py --zone $s --parts none --cam ZA --w 800 --samples 10 --out zc_$s > out/zc_$s.log 2>&1
done
echo done > out/zc_done.txt
