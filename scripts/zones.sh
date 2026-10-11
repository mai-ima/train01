#!/bin/bash
# usage: zones.sh "M02 M03 ..." cam w samples
cd /home/claude/station
for s in $1; do
  python3 main.py --zone $s --parts none --cam ${2:-Z2} --w ${3:-640} --samples ${4:-12} --out z_$s > out/z_$s.log 2>&1
  echo "$s $(grep -c Traceback out/z_$s.log)" >> out/zones_done.txt
done
