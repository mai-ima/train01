import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Export the built Blender scene to a compact real-time format (chunked binary + manifest) for the three.js viewer."""
import gzip
import json
import math
import os
import re
import shutil

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = f"{_R}/web"
VCOL_NAMES = ("Col", "Color", "col", "color")


# ----------------------------------------------------------------------------- materials
def _principled(mat):
    if not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None


def _walk_inputs(sock, seen=None):
    """yield all nodes upstream of a socket"""
    seen = seen if seen is not None else set()
    for l in sock.links:
        n = l.from_node
        if n.name in seen:
            continue
        seen.add(n.name)
        yield n
        for i in n.inputs:
            yield from _walk_inputs(i, seen)


def analyse_material(mat):
    """static info: photo textures (box), uv image, vertex colour use, transparency flags"""
    info = {"vcol": False, "box": None, "uvimg": None, "alpha": 1.0, "glass": False, "emit": None}
    if not mat.use_nodes:
        return info
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type in ('VERTEX_COLOR', 'ATTRIBUTE'):
            nm = getattr(n, 'layer_name', None) or getattr(n, 'attribute_name', None)
            if nm in VCOL_NAMES or n.type == 'VERTEX_COLOR':
                info["vcol"] = True
        if n.type == 'BSDF_GLASS':
            info["glass"] = True
    P = _principled(mat)
    if P is None:
        return info
    if P.inputs['Transmission Weight'].default_value > 0.5 and not P.inputs['Transmission Weight'].links:
        info["glass"] = True
    # colour textures feeding Base Color
    up = list(_walk_inputs(P.inputs['Base Color']))
    imgs = [n for n in up if n.type == 'TEX_IMAGE' and n.image]
    for n in imgs:
        path = bpy.path.abspath(n.image.filepath)
        if n.projection == 'BOX' and "_Color" in os.path.basename(path) and info["box"] is None:
            tid = os.path.basename(path).split("_")[0]
            scale = 1.0
            for m in up:
                if m.type == 'MAPPING':
                    s = m.inputs['Scale'].default_value
                    if s[0] > 1e-6:
                        scale = 1.0 / s[0]
                        break
            info["box"] = {"tid": tid, "scale": scale, "file": os.path.basename(path)}
        elif n.projection == 'FLAT' and info["uvimg"] is None and "/tex/" in path.replace("\\", "/"):
            info["uvimg"] = {"file": os.path.basename(path), "clip": n.extension == 'CLIP'}
    if P.inputs['Alpha'].links or P.inputs['Alpha'].default_value < 0.99:
        info["alpha"] = 0.5 if not P.inputs['Alpha'].links else 1.0
        info["alpha_map"] = bool(P.inputs['Alpha'].links)
    if info["glass"]:
        info["alpha"] = 0.18
    es = P.inputs['Emission Strength'].default_value
    if es > 0.01 and (P.inputs['Emission Color'].links or sum(P.inputs['Emission Color'].default_value[:3]) > 0.01):
        info["emit"] = float(es)
    return info


def _grid_render(mats, mode):
    """Render all materials side by side with an emission shader that outputs the chosen Principled socket; return mean RGB (sRGB display values)."""
    sc = bpy.data.scenes.new("matgrid")
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 6
    sc.cycles.use_denoising = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    w = bpy.data.worlds.new("black")
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0, 0, 0, 1)
    sc.world = w
    n = len(mats)
    cols = 20
    rows = int(math.ceil(n / cols))
    cell = 10.0
    px = 24
    sc.render.resolution_x = cols * px
    sc.render.resolution_y = rows * px
    sc.render.pixel_aspect_x = 1
    cam = bpy.data.cameras.new("mg")
    cam.type = 'ORTHO'
    cam.ortho_scale = cols * cell
    co = bpy.data.objects.new("mg", cam)
    co.location = (cols * cell / 2 - cell / 2 + 20000, -(rows * cell / 2 - cell / 2) + 20000, 50)
    sc.collection.objects.link(co)
    sc.camera = co
    tmp = []
    objs = []
    for i, m in enumerate(mats):
        cm = m.copy()
        tmp.append(cm)
        nt = cm.node_tree if cm.use_nodes else None
        if nt is not None:
            out = next((x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL' and x.is_active_output), None) or \
                  next((x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL'), None)
            P = next((x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'), None)
            em = nt.nodes.new('ShaderNodeEmission')
            em.inputs['Strength'].default_value = 1.0
            val = None
            if P is not None:
                sk = {'col': 'Base Color', 'rough': 'Roughness', 'metal': 'Metallic'}[mode]
                s = P.inputs[sk]
                if s.links:
                    nt.links.new(s.links[0].from_socket, em.inputs['Color'])
                else:
                    v = s.default_value
                    if mode == 'col':
                        em.inputs['Color'].default_value = (v[0], v[1], v[2], 1)
                    else:
                        em.inputs['Color'].default_value = (v, v, v, 1)
            else:
                # no principled: use the first colour-ish input of whatever shader is connected
                src = None
                for x in nt.nodes:
                    if x.type in ('BSDF_GLASS', 'BSDF_DIFFUSE', 'EMISSION', 'BSDF_GLOSSY', 'BSDF_TRANSPARENT'):
                        src = x
                        break
                if mode == 'col' and src is not None and 'Color' in src.inputs:
                    if src.inputs['Color'].links:
                        nt.links.new(src.inputs['Color'].links[0].from_socket, em.inputs['Color'])
                    else:
                        em.inputs['Color'].default_value = src.inputs['Color'].default_value
                else:
                    v = 0.5 if mode == 'rough' else 0.0
                    em.inputs['Color'].default_value = (v, v, v, 1) if mode != 'col' else (0.5, 0.5, 0.5, 1)
            nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
        mesh = bpy.data.meshes.new("mg")
        r, c = divmod(i, cols)
        x0, y0 = c * cell + 20000, -r * cell + 20000
        h = 4.0
        mesh.from_pydata([(x0 - h, y0 - h, 0), (x0 + h, y0 - h, 0), (x0 + h, y0 + h, 0), (x0 - h, y0 + h, 0)], [], [(0, 1, 2, 3)])
        for nm in VCOL_NAMES:
            a = mesh.color_attributes.new(nm, 'FLOAT_COLOR', 'POINT')
            for d in a.data:
                d.color = (1, 1, 1, 1)
        mesh.materials.append(cm)
        ob = bpy.data.objects.new("mg", mesh)
        sc.collection.objects.link(ob)
        objs.append(ob)
    path = bpy.app.tempdir + "/matgrid.png"
    sc.render.filepath = path
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '8'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    img = bpy.data.images.load(path, check_existing=False)
    W, H = img.size
    arr = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[:, :, :3]
    res = []
    for i in range(n):
        r, c = divmod(i, cols)
        # image row 0 is the bottom in Blender; scene row r is at y = -r*cell -> from the top
        yy = rows - 1 - r
        a = arr[yy * px + 4:(yy + 1) * px - 4, c * px + 4:(c + 1) * px - 4].reshape(-1, 3)
        res.append(a.mean(0))
    bpy.data.images.remove(img)
    for ob in objs:
        bpy.data.objects.remove(ob)
    for cm in tmp:
        bpy.data.materials.remove(cm)
    bpy.data.scenes.remove(sc)
    return np.array(res)


def export_materials(used_names):
    mats = [bpy.data.materials[n] for n in sorted(used_names)]
    col = _grid_render(mats, 'col')
    rough = _grid_render(mats, 'rough')
    metal = _grid_render(mats, 'metal')
    table = {}
    texfiles = set()
    for i, m in enumerate(mats):
        a = analyse_material(m)
        P = _principled(m)
        d = {"c": [round(float(v), 4) for v in col[i]], "r": round(float(rough[i].mean()), 3),
             "m": round(float(metal[i].mean()), 3), "a": a["alpha"], "vc": a["vcol"], "g": a["glass"]}
        if a["box"]:
            d["box"] = {"tid": a["box"]["tid"], "s": round(a["box"]["scale"], 4)}
            texfiles.add(a["box"]["tid"])
        if a["uvimg"]:
            d["img"] = a["uvimg"]["file"]
            d["clip"] = a["uvimg"]["clip"]
            texfiles.add("img:" + a["uvimg"]["file"])
        if a.get("alpha_map"):
            d["am"] = True
        if a["emit"]:
            d["e"] = a["emit"]
            if P is not None and not P.inputs['Emission Color'].links:
                d["ec"] = [round(float(v), 3) for v in P.inputs['Emission Color'].default_value[:3]]
        table[m.name] = d
    return table, texfiles


# ----------------------------------------------------------------------------- geometry
CLASS_OF = {"Vegetation": "veg", "Track": "trk", "Trees": "tre"}
CELL = {"veg": 40.0, "trk": 64.0, "tre": 64.0, "std": 64.0}


def _mesh_arrays(ob):
    me = ob.data
    me.calc_loop_triangles()
    nv = len(me.vertices)
    co = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    M = np.array(ob.matrix_world, dtype=np.float32)
    co = co @ M[:3, :3].T + M[:3, 3]
    nt = len(me.loop_triangles)
    tv = np.empty(nt * 3, np.int32)
    me.loop_triangles.foreach_get('vertices', tv)
    tv = tv.reshape(-1, 3)
    tp = np.empty(nt, np.int32)
    me.loop_triangles.foreach_get('polygon_index', tp)
    tl = np.empty(nt * 3, np.int32)
    me.loop_triangles.foreach_get('loops', tl)
    tl = tl.reshape(-1, 3)
    npoly = len(me.polygons)
    mi = np.empty(npoly, np.int32)
    me.polygons.foreach_get('material_index', mi)
    sm = np.empty(npoly, np.bool_)
    me.polygons.foreach_get('use_smooth', sm)
    vcol = None
    for nm in VCOL_NAMES:
        a = me.color_attributes.get(nm)
        if a is not None:
            raw = np.empty(len(a.data) * 4, np.float32)
            a.data.foreach_get('color', raw)
            raw = raw.reshape(-1, 4)
            if a.domain == 'POINT':
                vcol = raw
            else:  # corner -> point average
                lv = np.empty(len(me.loops), np.int32)
                me.loops.foreach_get('vertex_index', lv)
                acc = np.zeros((nv, 4), np.float64)
                cnt = np.zeros(nv)
                np.add.at(acc, lv, raw)
                np.add.at(cnt, lv, 1)
                vcol = (acc / np.maximum(cnt, 1)[:, None]).astype(np.float32)
            break
    uv = None
    if me.uv_layers.active is not None:
        u = np.empty(len(me.loops) * 2, np.float32)
        me.uv_layers.active.data.foreach_get('uv', u)
        uv = u.reshape(-1, 2)
    nrm = None
    if sm.any():
        nrm = np.empty(nv * 3, np.float32)
        me.vertex_normals.foreach_get('vector', nrm)
        nrm = nrm.reshape(-1, 3) @ M[:3, :3].T
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-8)
    return co, tv, tp, tl, mi, sm, vcol, uv, nrm


def export_geometry(valid_mats):
    """Collect triangles per (class, cell, material, flat/smooth, uv?) and write chunk files."""
    groups = {}
    stats = {}
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.hide_render:
            continue
        coll = ob.users_collection[0].name if ob.users_collection else "-"
        cls = CLASS_OF.get(coll, "std")
        co, tv, tp, tl, mi, sm, vcol, uv, nrm = _mesh_arrays(ob)
        if len(tv) == 0:
            continue
        slots = [s.material.name if s.material else None for s in ob.material_slots]
        cen = (co[tv[:, 0]] + co[tv[:, 1]] + co[tv[:, 2]]) / 3.0
        cs = CELL[cls]
        cx = np.clip(np.floor(cen[:, 0] / cs), -300 / cs, 300 / cs).astype(np.int32)
        cy = np.clip(np.floor(cen[:, 1] / cs), -300 / cs, 300 / cs).astype(np.int32)
        tmi = mi[tp]
        tsm = sm[tp]
        key = (tmi.astype(np.int64) * 2 + tsm) * 1000003 + (cx + 500) * 1009 + (cy + 500)
        for k in np.unique(key):
            sel = np.nonzero(key == k)[0]
            m = slots[int(tmi[sel[0]])] if slots else None
            if m is None or m not in valid_mats:
                continue
            gk = (cls, int(cx[sel[0]]), int(cy[sel[0]]), m, bool(tsm[sel[0]]), uv is not None and valid_mats[m].get("img") is not None)
            g = groups.setdefault(gk, [])
            if gk[5]:
                # unindexed corner data (uv per loop)
                lp = tl[sel]
                g.append(("u", co[tv[sel]].reshape(-1, 3), uv[lp].reshape(-1, 2),
                          (vcol[tv[sel]].reshape(-1, 4) if vcol is not None else None)))
            else:
                v = tv[sel]
                g.append(("i", co, v, vcol, nrm if gk[4] else None))
            stats[cls] = stats.get(cls, 0) + len(sel)
    print("export tris per class", stats)
    # write chunk files
    chunks = {}
    for gk in groups:
        chunks.setdefault((gk[0], gk[1], gk[2]), []).append(gk)
    os.makedirs(OUT + "/geo", exist_ok=True)
    manifest = []
    for (cls, cx, cy), gks in chunks.items():
        blobs = []
        gdesc = []
        off = 0
        bb_min = np.array([1e9] * 3)
        bb_max = np.array([-1e9] * 3)
        for gk in gks:
            _, _, _, mname, smooth, isuv = gk
            parts = groups[gk]
            P_list, V_list, I_list, C_list, N_list, U_list = [], [], [], [], [], []
            base = 0
            for p in parts:
                if p[0] == "u":
                    pos = p[1]
                    n = len(pos)
                    P_list.append(pos)
                    U_list.append(p[2])
                    if p[3] is not None:
                        C_list.append(p[3])
                    I_list.append(np.arange(n, dtype=np.int64) + base)
                    base += n
                else:
                    co, v, vcol, nrm = p[1], p[2], p[3], p[4]
                    uniq, inv = np.unique(v.reshape(-1), return_inverse=True)
                    P_list.append(co[uniq])
                    if vcol is not None:
                        C_list.append(vcol[uniq])
                    if nrm is not None:
                        N_list.append(nrm[uniq])
                    I_list.append(inv.astype(np.int64) + base)
                    base += len(uniq)
            pos = np.concatenate(P_list)
            idx = np.concatenate(I_list)
            lo, hi = pos.min(0), pos.max(0)
            bb_min = np.minimum(bb_min, lo)
            bb_max = np.maximum(bb_max, hi)
            # split into <=65535-vertex sub-meshes is avoided: use uint32 indices when needed
            size = np.maximum(hi - lo, 1e-4)
            q = np.round((pos - lo) / size * 65535.0).astype(np.uint16)
            qpad = np.zeros((len(q), 4), np.uint16)
            qpad[:, :3] = q
            d = {"m": mname, "n": int(len(pos)), "lo": [float(x) for x in lo], "sz": [float(x) for x in size],
                 "sm": smooth}
            parts_b = [qpad.tobytes()]
            if C_list and len(C_list) == len(P_list):
                c = np.concatenate(C_list)
                c8 = np.clip(c * 255.0 + 0.5, 0, 255).astype(np.uint8)
                if c8.shape[1] == 3:
                    c8 = np.concatenate([c8, np.full((len(c8), 1), 255, np.uint8)], 1)
                parts_b.append(c8.tobytes())
                d["col"] = 1
            if N_list and len(N_list) == len(P_list):
                nn = np.concatenate(N_list)
                n8 = np.clip(np.round(nn * 127.0), -127, 127).astype(np.int8)
                n8p = np.zeros((len(n8), 4), np.int8)
                n8p[:, :3] = n8
                parts_b.append(n8p.tobytes())
                d["nrm"] = 1
            if U_list:
                parts_b.append(np.concatenate(U_list).astype(np.float32).tobytes())
                d["uv"] = 1
            if len(pos) < 65536:
                parts_b.append(idx.astype(np.uint16).tobytes())
                d["it"] = 16
            else:
                parts_b.append(idx.astype(np.uint32).tobytes())
                d["it"] = 32
            d["ni"] = int(len(idx))
            blob = b"".join(parts_b)
            pad = (-len(blob)) % 4
            blob += b"\0" * pad
            d["off"] = off
            d["len"] = len(blob)
            off += len(blob)
            blobs.append(blob)
            gdesc.append(d)
        fn = f"{cls}_{cx}_{cy}.bin.gz"
        with gzip.GzipFile(OUT + "/geo/" + fn, "wb", compresslevel=9, mtime=0) as f:
            f.write(b"".join(blobs))
        manifest.append({"f": fn, "cls": cls, "bb": [[float(x) for x in bb_min], [float(x) for x in bb_max]], "g": gdesc})
    return manifest


# ----------------------------------------------------------------------------- collision
def export_collision():
    x0, x1, y0, y1, cs = -140.0, 120.0, -128.0, 52.0, 0.25
    nx, ny = int((x1 - x0) / cs), int((y1 - y0) / cs)
    walk_colls = {"Terrain", "Roads", "Platform", "Station", "Track", "Buildings", "Depot", "Props"}
    ground_colls = {"Terrain", "Roads", "Platform", "Track"}
    solid_colls = {"Station", "Buildings", "Depot", "Vehicles", "Trains", "Props", "Trees", "Signs", "People"}

    def tris_of(colls):
        V, F = [], []
        base = 0
        for ob in bpy.data.objects:
            if ob.type != 'MESH' or not ob.users_collection or ob.users_collection[0].name not in colls:
                continue
            co, tv, *_ = _mesh_arrays(ob)
            if len(tv) == 0:
                continue
            V.append(co)
            F.append(tv + base)
            base += len(co)
        return np.concatenate(V), np.concatenate(F)

    Vg, Fg = tris_of(ground_colls)
    Vw, Fw = tris_of(walk_colls)
    print("collision tris ground", len(Fg), "walk", len(Fw))
    bg = BVHTree.FromPolygons([tuple(v) for v in Vg.tolist()], [tuple(f) for f in Fg.tolist()])
    bw = BVHTree.FromPolygons([tuple(v) for v in Vw.tolist()], [tuple(f) for f in Fw.tolist()])
    H = np.full((ny, nx), -32768, np.int16)
    down = Vector((0, 0, -1))
    for j in range(ny):
        y = y0 + (j + 0.5) * cs
        for i in range(nx):
            x = x0 + (i + 0.5) * cs
            hit = bg.ray_cast(Vector((x, y, 3.2)), down, 12.0)
            if hit[0] is None:
                continue
            h0 = hit[0].z
            best = h0
            # walk surfaces within step range above the ground
            o = Vector((x, y, h0 + 1.0))
            hw = bw.ray_cast(o, down, 1.3)
            if hw[0] is not None and hw[1].z > 0.8:
                best = max(best, hw[0].z)
            H[j, i] = int(round(best * 1000))
    # solids occupancy
    occ = np.zeros((ny, nx), np.uint8)
    Hm = np.where(H > -32768, H / 1000.0, 0.0)
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or not ob.users_collection or ob.users_collection[0].name not in solid_colls:
            continue
        co, tv, *_ = _mesh_arrays(ob)
        if len(tv) == 0:
            continue
        a, b, c = co[tv[:, 0]], co[tv[:, 1]], co[tv[:, 2]]
        mn = np.minimum(np.minimum(a, b), c)
        mx = np.maximum(np.maximum(a, b), c)
        i0 = np.clip(((mn[:, 0] - x0) / cs).astype(int), 0, nx - 1)
        i1 = np.clip(((mx[:, 0] - x0) / cs).astype(int), 0, nx - 1)
        j0 = np.clip(((mn[:, 1] - y0) / cs).astype(int), 0, ny - 1)
        j1 = np.clip(((mx[:, 1] - y0) / cs).astype(int), 0, ny - 1)
        ic = (i0 + i1) // 2
        jc = (j0 + j1) // 2
        gh = Hm[jc, ic]
        ok = (mx[:, 2] >= gh + 0.30) & (mn[:, 2] <= gh + 1.7) & ((i1 - i0) <= 80) & ((j1 - j0) <= 80)
        for t in np.nonzero(ok)[0]:
            occ[j0[t]:j1[t] + 1, i0[t]:i1[t] + 1] = 1
    os.makedirs(OUT, exist_ok=True)
    with gzip.GzipFile(OUT + "/collision.bin.gz", "wb", compresslevel=9, mtime=0) as f:
        f.write(H.tobytes())
        f.write(occ.tobytes())
    return {"x0": x0, "y0": y0, "nx": nx, "ny": ny, "cs": cs}


# ----------------------------------------------------------------------------- lights
def export_lights():
    out = []
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.data.type == 'POINT':
            c = ob.data.color
            out.append({"p": [round(v, 3) for v in ob.matrix_world.translation], "w": round(ob.data.energy, 1),
                        "c": [round(c[0], 3), round(c[1], 3), round(c[2], 3)]})
    return out


def run(steps):
    if os.path.exists(OUT) and "geo" in steps:
        shutil.rmtree(OUT + "/geo", ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    bpy.context.view_layer.update()
    used = set()
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and not ob.hide_render:
            for s in ob.material_slots:
                if s.material:
                    used.add(s.material.name)
    meta = {}
    if "mat" in steps:
        table, texfiles = export_materials(used)
        json.dump(table, open(OUT + "/materials.json", "w"))
        json.dump(sorted(texfiles), open(OUT + "/texfiles.json", "w"))
        print("materials", len(table), "textures", sorted(texfiles))
    table = json.load(open(OUT + "/materials.json"))
    if "geo" in steps:
        man = export_geometry(table)
        json.dump(man, open(OUT + "/manifest.json", "w"))
        print("chunks", len(man))
    if "col" in steps:
        meta["grid"] = export_collision()
    if "light" in steps:
        meta["lights"] = export_lights()
    if meta:
        old = json.load(open(OUT + "/meta.json")) if os.path.exists(OUT + "/meta.json") else {}
        old.update(meta)
        json.dump(old, open(OUT + "/meta.json", "w"))
