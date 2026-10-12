import sys
sys.argv = ["main.py", "--cam", "SS", "--parts", "tst", "--no-render"]
exec(open("main.py").read())
import bpy
for ob in bpy.data.objects:
    if ob.type == 'MESH' and ob.name.startswith("sD_"):
        xs = [v.co.x for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]; zs = [v.co.z for v in ob.data.vertices]
        print(ob.name, len(ob.data.vertices), "x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
