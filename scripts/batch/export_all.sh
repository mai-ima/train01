#!/bin/bash
cd /home/claude/station
mkdir -p out/zones; rm -f out/zones/done.txt out/zones/sizes.txt
ids=$(python3 -c "
import kit
print(' '.join(k for k in kit.ST))" 2>/dev/null)
export VEG_LIGHT=0.35
n=0
for s in $ids; do
  ( python3 main.py --zone $s --parts none --cam ZA --w 320 --samples 1 --save-blend --out zones/Z_$s > out/zones/Z_$s.log 2>&1; ls -la out/zones/Z_$s.blend >> out/zones/sizes.txt ) &
  n=$((n+1)); if [ $((n%3)) -eq 0 ]; then wait; fi
done
wait
echo done > out/zones/done.txt
