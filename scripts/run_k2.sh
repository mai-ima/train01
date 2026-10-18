#!/bin/bash
# K2/K9: 全駅の扉・階段開口(DOORS)・干渉(INTERF)・浮き(FLOAT)を --interf --no-render で検査し out/k2_doors.txt に集約
cd /home/claude/station
export PYTHONHASHSEED=0 RENDER_THREADS=1
: > out/k2_doors.txt
one(){ z=$1; PYTHONHASHSEED=0 timeout 1200 python3 main.py --zone $z --interf --no-render > /tmp/k2_$z.log 2>&1; grep -h "^DOORS\|^INTERF\|^STOCKHIT\|^FLOAT" /tmp/k2_$z.log | cut -c1-400 >> out/k2_doors.txt; }
export -f one
grep -v "^M06$" /tmp/k2_ids.txt | xargs -P 3 -I{} bash -c 'one {}'
echo done >> out/k2_doors.txt
