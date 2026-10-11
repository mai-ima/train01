for c in AV P D B G; do python3 main.py --cam $c --w 960 --samples 24 --parts core,station,depot,props,train,veg --out au_$c > out/au_$c.log 2>&1; done
echo done > out/au_done
