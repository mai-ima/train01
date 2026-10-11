cd /home/claude/station
for c in "$@"; do python3 main.py --cam $c --w 960 --samples 16 --parts core,station,depot,props,train,veg --out a_$c 2>&1 | grep -E "Error:|Traceback|rendered|line [0-9]+" ; done
echo ALLDONE
