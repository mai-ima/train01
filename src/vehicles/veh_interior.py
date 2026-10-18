"""車内の目線撮影(F3d2/F5e): 1両だけ原点に置き、客室の中にカメラを置いて撮る。
使い方: python3 veh_interior.py <形式> <人物on|off> <出力名> [cam指定 "x,y,z,tx,ty,tz,lens;..."]   → out/int/<出力名>_<n>.png"""
import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
import sys, math
import bpy
sys.path.insert(0, _R)
import common, vehtypes
from mathutils import Vector

kind, ppl, name = sys.argv[1], sys.argv[2], sys.argv[3]
cams = sys.argv[4] if len(sys.argv) > 4 else "-3,0.0,2.55,4,0.0,2.3,26;3,-0.6,2.5,-4,0.9,2.2,30;0,0.0,2.6,6.5,0.0,2.4,24"
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
common.make_materials()
v = vehtypes.make(kind, "vint", seed=3, ends=("cab", "cab"), people=(ppl == "on")) if "people" in vehtypes.make.__code__.co_varnames else vehtypes.make(kind, "vint", seed=3, ends=("cab", "cab"))
v.place(0, 0, 0, z=0.274)
# 屋根と屋根上機器を隠さずに、天井の外側だけ薄い外光(窓から入る昼光)を与える
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.55, 0.65, 0.8, 1.0); bg.inputs[1].default_value = 1.2
sun = bpy.data.lights.new("Sun", 'SUN'); sun.energy = 4.0
so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(35))
g = bpy.data.meshes.new("G"); go = bpy.data.objects.new("G", g); sc.collection.objects.link(go)
import bmesh
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60.0); bm.to_mesh(g); bm.free()
go.location.z = 0.0
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 675
try:
    sc.cycles.device = 'CPU'
except Exception:
    pass
for i, c in enumerate(cams.split(";")):
    x, y, z, tx, ty, tz, lens = [float(t) for t in c.split(",")]
    cd = bpy.data.cameras.new(f"C{i}"); cd.lens = lens
    co = bpy.data.objects.new(f"C{i}", cd); sc.collection.objects.link(co); co.location = (x, y, z)
    d = Vector((tx - x, ty - y, tz - z)); co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    out = _os.path.join(_R, "out", "int", f"{name}_{i}.png"); _os.makedirs(_os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    print("saved", out)
