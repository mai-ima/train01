cd /home/claude/station
while ! grep -q "^SH08 " out/zones_done.txt; do sleep 10; done
for s in SH02 SH03 SH04 SH05 SH06 SH07 SH08; do
  python3 main.py --zone $s --parts none --cam ZA --w 800 --samples 12 --out za_$s > out/za_$s.log 2>&1
done
echo done > out/za_done.txt
