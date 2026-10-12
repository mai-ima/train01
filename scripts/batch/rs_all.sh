cd "$(dirname "$(readlink -f "$0")")"
mkdir -p out/contact; rm -f out/contact/done.txt
ids=$(python3 -c "
import sys; sys.argv=['x']
import kit
print(' '.join(k for k in kit.ST))" 2>/dev/null)
n=0
for s in $ids; do
  ( timeout 900 python3 main.py --zone $s --parts none --cam ZA --w 640 --samples 6 --out contact/$s > out/contact/$s.log 2>&1 ) &
  n=$((n+1)); if [ $((n%4)) -eq 0 ]; then wait; fi
done
wait
echo done > out/contact/done.txt
