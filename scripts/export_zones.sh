#!/bin/bash
# ゾーン別 .blend 書き出し(テクスチャ非パック・相対パス化は納品時に tex/ と合わせる)。使い方: ./export_zones.sh M05 SH05 ...
cd /home/claude/station
mkdir -p out/zones
for s in "$@"; do
  python3 main.py --zone $s --parts none --cam ZA --w 320 --samples 1 --save-blend --out zones/Z_$s > out/zones/Z_$s.log 2>&1
  ls -la out/zones/Z_$s.blend >> out/zones/sizes.txt
done
echo done > out/zones/done.txt
