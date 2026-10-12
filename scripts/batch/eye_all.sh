cd "$(dirname "$(readlink -f "$0")")"
rm -f out/eye/done.txt
ids=$(python3 -c "
import kit
print(' '.join(k for k in kit.ST))" 2>/dev/null)
n=0
for s in $ids; do
  ( timeout 900 python3 main.py --zone $s --parts none --cam A --w 800 --samples 10 --out eye/$s > out/eye/$s.log 2>&1 ) &
  n=$((n+1)); if [ $((n%4)) -eq 0 ]; then wait; fi
done
wait; echo done > out/eye/done.txt
