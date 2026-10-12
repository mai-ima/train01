#!/bin/bash
# E3a 後処理2: e3b2(穂波野+撮り直し)の完了を待って、健全性集計とコンタクトシート(A/E/ZA)を作り、X15 の部品撮影(parts_audit.sh)を起動する。
cd "$(dirname "$(readlink -f "$0")")"
until [ -f out/e3b2/done.txt ]; do sleep 30; done
python3 healthscan.py "out/e3b2/*.log" > out/e3b2/HEALTH_SUMMARY.txt 2>&1
for n in 0 1 2; do python3 contact_sheet.py out/e3b $n out/sheet_e3b_$n.jpg 6 320; done
for n in 0 1 2; do python3 contact_sheet.py out/e3b2 $n out/sheet_e3b2_$n.jpg 4 400; done
echo done > out/e3b2/post2_done.txt
bash parts_audit.sh > out/parts_audit.log 2>&1
echo done > out/parts_done.txt
