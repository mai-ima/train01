P=core,station,depot,props,train,veg
python3 main.py --cam H --w 1920 --samples 32 --parts $P --out f_H --save-blend --pack > out/f_H.log 2>&1
for c in B P AV D G A; do python3 main.py --cam $c --w 1920 --samples 32 --parts $P --out f_$c > out/f_$c.log 2>&1; done
echo done > out/f_done
