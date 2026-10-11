"""K2: 開口(ドア)が塞がれていないかをレイキャストで検査。rooms.DOORS を使用。"""
import math
import bpy
from mathutils import Vector
import rooms

WALLS = ("_wall", "_wood", "_brick", "_concrete", "_stone", "_tin", "_plaster2", "_plasterw", "_kawara")
SKIP = ("glass", "sky", "sun", "ground", "terrain", "grass", "hill", "far_")


def _w(stack, p):
    x, y, z = p
    for (o, yaw) in reversed(stack):
        c, s = math.cos(yaw), math.sin(yaw)
        x, y = c * x - s * y + o[0], s * x + c * y + o[1]
        z += o[2]
    return Vector((x, y, z))


def _wd(stack, d):
    x, y = d
    for (o, yaw) in reversed(stack):
        c, s = math.cos(yaw), math.sin(yaw)
        x, y = c * x - s * y, s * x + c * y
    return Vector((x, y, 0))


def cast(origin, dirn, length):
    dg = bpy.context.evaluated_depsgraph_get()
    p, left, hits = origin, length, []
    for _ in range(6):
        ok, loc, n, idx, ob, mat = bpy.context.scene.ray_cast(dg, p, dirn, distance=left)
        if not ok:
            break
        d = (loc - p).length
        nm = ob.name.lower().split(".")[0]
        if not any(k in nm for k in SKIP) and (nm.endswith(WALLS) or "_pl_" in nm):
            hits.append((length - left + d, ob.name))
            break
        p = loc + dirn * 0.02
        left -= d + 0.02
    return hits


def run():
    bpy.context.view_layer.update()
    bad = []
    for d in rooms.DOORS:
        if d['z1'] - d['z0'] < 1.8:
            continue
        pc = (d["p0"] + d["p1"]) / 2
        w = d["a1"] - d["a0"]
        out = d["out"]
        clear_any = False
        dbg = []
        info = None
        for fr in (0.3, 0.5, 0.7):
            a = d["a0"] + w * fr
            ok_h = True
            for zz in (d["z0"] + 1.0, d["z0"] + 1.7):
                if zz >= d["z1"] - 0.1:
                    continue
                if d["axis"] == 'x':
                    o_loc, dl = (a, pc + out * 0.8, zz), (0, -out)
                else:
                    o_loc, dl = (pc + out * 0.8, a, zz), (-out, 0)
                h = cast(_w(d["stack"], o_loc), _wd(d["stack"], dl).normalized(), 2.4)
                if h and h[0][0] <= 1.2:
                    ok_h = False
                    info = info if (info and info[0] > h[0][0]) else (h[0] if not info else info)
                    dbg.append((fr, zz, h[0]))
            if ok_h:
                clear_any = True
                break
        if not clear_any:
            c0 = _w(d["stack"], ((d["a0"] + d["a1"]) / 2, pc, d["z0"]) if d["axis"] == 'x' else (pc, (d["a0"] + d["a1"]) / 2, d["z0"]))
            bad.append(dict(kind=d["kind"], at=[round(c0.x, 1), round(c0.y, 1)], hit=info[1] if info else None, dbg=[(a, round(b, 2), (round(c[0], 2), c[1])) for a, b, c in dbg], dist=round(info[0], 2) if info else None))
    return bad, len(rooms.DOORS)
