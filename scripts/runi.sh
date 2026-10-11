cd /home/claude/station
for c in "$@"; do python3 main.py --cam $c --w 960 --samples 28 --parts core,depot,props --out i_$c 2>&1 | grep -E "Traceback|Error:|rendered|File" ; done
echo ALLDONE
