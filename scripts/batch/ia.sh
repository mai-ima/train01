cd "$(dirname "$(readlink -f "$0")")"
for s in $(python3 -c "
import sys; sys.argv=['x']
import kit
print(' '.join(k for k in kit.ST if k not in ('M01','M06')))" 2>/dev/null); do
  python3 main.py --zone $s --parts none --no-render --interf --out ia_$s > out/ia_$s.log 2>&1
done
echo done > out/ia_done.txt
