cd /home/claude/station
for s in $(python3 -c "
import sys; sys.argv=['x']
import kit
print(' '.join(k for k in kit.ST if k not in ('M01','M06')))" 2>/dev/null); do
  python3 main.py --zone $s --parts none --no-render --out zsa_$s > out/zsa_$s.log 2>&1
  if grep -q "stock failed\|Traceback" out/zsa_$s.log; then echo "FAIL $s" >> out/zsa_res.txt; else echo "ok $s $(grep -c . out/zsa_$s.log)" >> out/zsa_res.txt; fi
done
echo done > out/zsa_done.txt
