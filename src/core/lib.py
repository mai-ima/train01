import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Helpers: mesh accumulation + procedural materials for the Honamino station scene."""
import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Vector

TEX = f"{_R}/tex"

# ============================================================== collections / linking
_cols = {}


def collection(name):
    if name not in _cols:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        _cols[name] = c
    return _cols[name]


def link(obj, col="Station"):
    collection(col).objects.link(obj)
    return obj


# ============================================================== mesh accumulation
class Acc:
    """Collects boxes / cylinders / arbitrary quads into one mesh object."""

    def __init__(self, name, mat, col="Station", bevel=0.0, smooth=False, closed=True):
        self.name, self.mat, self.col = name, mat, col
        self.bevel, self.smooth, self.closed = bevel, smooth, closed
        self.V, self.F = [], []

    # -- primitives
    def v(self, p):
        self.V.append((float(p[0]), float(p[1]), float(p[2])))
        return len(self.V) - 1

    def quad(self, a, b, c, d):
        self.F.append((a, b, c, d))

    def tri(self, a, b, c):
        self.F.append((a, b, c))

    def quad_pts(self, p0, p1, p2, p3):
        self.quad(self.v(p0), self.v(p1), self.v(p2), self.v(p3))

    def box(self, x0, x1, y0, y1, z0, z1):
        i = len(self.V)
        self.V += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.F += [(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4),
                   (i + 1, i + 2, i + 6, i + 5), (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)]

    def boxc(self, cx, cy, cz, sx, sy, sz, rz=0.0):
        """Box by centre + size, rotated about Z."""
        c, s = math.cos(rz), math.sin(rz)
        i = len(self.V)
        for dz in (-0.5, 0.5):
            for dx, dy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
                px, py = dx * sx, dy * sy
                self.V.append((cx + px * c - py * s, cy + px * s + py * c, cz + dz * sz))
        self.F += [(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4),
                   (i + 1, i + 2, i + 6, i + 5), (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)]

    def cyl(self, p0, p1, r0, r1=None, seg=12, caps=True):
        """Cylinder / cone frustum between two points."""
        r1 = r0 if r1 is None else r1
        a, b = Vector(p0), Vector(p1)
        ax = (b - a)
        if ax.length < 1e-9:
            return
        ax.normalize()
        ref = Vector((0, 0, 1)) if abs(ax.z) < 0.99 else Vector((1, 0, 0))
        u = ax.cross(ref).normalized()
        w = ax.cross(u).normalized()
        i = len(self.V)
        for k in range(seg):
            t = 2 * math.pi * k / seg
            d = u * math.cos(t) + w * math.sin(t)
            self.V.append(tuple(a + d * r0))
            self.V.append(tuple(b + d * r1))
        for k in range(seg):
            k2 = (k + 1) % seg
            self.F.append((i + 2 * k, i + 2 * k2, i + 2 * k2 + 1, i + 2 * k + 1))
        if caps:
            self.F.append(tuple(i + 2 * k for k in reversed(range(seg))))
            self.F.append(tuple(i + 2 * k + 1 for k in range(seg)))

    def extrude_x(self, profile, x0, x1):
        """Extrude closed (y,z) polygon along X."""
        i = len(self.V)
        n = len(profile)
        for (y, z) in profile:
            self.V.append((x0, y, z))
        for (y, z) in profile:
            self.V.append((x1, y, z))
        for k in range(n):
            k2 = (k + 1) % n
            self.F.append((i + k, i + k2, i + n + k2, i + n + k))
        self.F.append(tuple(i + k for k in reversed(range(n))))
        self.F.append(tuple(i + n + k for k in range(n)))

    def loft_x(self, sections, cap=True):
        """Loft closed (y,z) profiles (same vertex count) at successive x: sections=[(x, [(y,z)...]), ...]."""
        i0 = len(self.V)
        n = len(sections[0][1])
        for (x, prof) in sections:
            for (y, z) in prof:
                self.V.append((x, y, z))
        for t in range(len(sections) - 1):
            a, b = i0 + t * n, i0 + (t + 1) * n
            for k in range(n):
                k2 = (k + 1) % n
                self.F.append((a + k, a + k2, b + k2, b + k))
        if cap:
            self.F.append(tuple(i0 + k for k in reversed(range(n))))
            last = i0 + (len(sections) - 1) * n
            self.F.append(tuple(last + k for k in range(n)))

    def tube(self, p0, p1, prof, seg=12, side=None):
        """軸 p0→p1 に沿う楕円断面のロフト。prof=[(t, rx, ry), ...]: t=0..1 の位置と半幅(side方向)/半奥行。端はキャップ。人体の胴・四肢の滑らかな造形用。"""
        a = Vector(p1) - Vector(p0)
        if a.length < 1e-9:
            return
        ax = a.normalized()
        sd = Vector(side) if side is not None else (Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0)))
        sd = (sd - ax * sd.dot(ax)).normalized()
        fw = ax.cross(sd).normalized()
        i0 = len(self.V)
        for (t, rx, ry) in prof:
            c = Vector(p0) + a * t
            for k in range(seg):
                th = 2 * math.pi * k / seg
                self.V.append(tuple(c + sd * (rx * math.cos(th)) + fw * (ry * math.sin(th))))
        for t in range(len(prof) - 1):
            ra, rb = i0 + t * seg, i0 + (t + 1) * seg
            for k in range(seg):
                k2 = (k + 1) % seg
                self.F.append((ra + k, ra + k2, rb + k2, rb + k))
        self.F.append(tuple(i0 + k for k in reversed(range(seg))))
        last = i0 + (len(prof) - 1) * seg
        self.F.append(tuple(last + k for k in range(seg)))

    def extrude_y(self, profile, y0, y1):
        """Extrude closed (x,z) polygon along Y."""
        i = len(self.V)
        n = len(profile)
        for (x, z) in profile:
            self.V.append((x, y0, z))
        for (x, z) in profile:
            self.V.append((x, y1, z))
        for k in range(n):
            k2 = (k + 1) % n
            self.F.append((i + k, i + n + k, i + n + k2, i + k2))
        self.F.append(tuple(i + k for k in range(n)))
        self.F.append(tuple(i + n + k for k in reversed(range(n))))

    def sbox(self, p0, p1, w, h, up=(0, 0, 1)):
        """Oriented box running from p0 to p1 with cross-section w (side) x h (up)."""
        a = Vector(p1) - Vector(p0)
        if a.length < 1e-9:
            return
        a.normalize()
        upv = Vector(up)
        if abs(a.dot(upv)) > 0.98:
            upv = Vector((1, 0, 0))
        s = a.cross(upv).normalized()
        u = s.cross(a).normalized()
        i = len(self.V)
        for p in (Vector(p0), Vector(p1)):
            for sx, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                self.V.append(tuple(p + s * (sx * w / 2) + u * (uy * h / 2)))
        self.F += [(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4),
                   (i + 1, i + 2, i + 6, i + 5), (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)]

    def extrude_z(self, poly_xy, z0, z1):
        """Extrude closed (x,y) polygon along Z."""
        i = len(self.V)
        n = len(poly_xy)
        for (x, y) in poly_xy:
            self.V.append((x, y, z0))
        for (x, y) in poly_xy:
            self.V.append((x, y, z1))
        for k in range(n):
            k2 = (k + 1) % n
            self.F.append((i + k, i + k2, i + n + k2, i + n + k))
        self.F.append(tuple(i + k for k in reversed(range(n))))
        self.F.append(tuple(i + n + k for k in range(n)))

    def sphere(self, c, radii, seg=16, rings=10):
        i = len(self.V)
        for r in range(rings + 1):
            th = math.pi * r / rings
            for k in range(seg):
                ph = 2 * math.pi * k / seg
                self.V.append((c[0] + radii[0] * math.sin(th) * math.cos(ph),
                               c[1] + radii[1] * math.sin(th) * math.sin(ph),
                               c[2] + radii[2] * math.cos(th)))
        for r in range(rings):
            for k in range(seg):
                k2 = (k + 1) % seg
                self.F.append((i + r * seg + k, i + r * seg + k2, i + (r + 1) * seg + k2, i + (r + 1) * seg + k))

    def torus(self, c, axis, R, r, segR=28, segr=8):
        """Torus around `c`, ring plane perpendicular to `axis` ('x','y','z')."""
        i = len(self.V)
        for a in range(segR):
            ta = 2 * math.pi * a / segR
            for b in range(segr):
                tb = 2 * math.pi * b / segr
                rad = R + r * math.cos(tb)
                p1, p2, p3 = rad * math.cos(ta), rad * math.sin(ta), r * math.sin(tb)
                if axis == 'y':
                    p = (c[0] + p1, c[1] + p3, c[2] + p2)
                elif axis == 'x':
                    p = (c[0] + p3, c[1] + p1, c[2] + p2)
                else:
                    p = (c[0] + p1, c[1] + p2, c[2] + p3)
                self.V.append(p)
        for a in range(segR):
            a2 = (a + 1) % segR
            for b in range(segr):
                b2 = (b + 1) % segr
                self.F.append((i + a * segr + b, i + a2 * segr + b, i + a2 * segr + b2, i + a * segr + b2))

    # -- finish
    def build(self):
        if not self.V:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.V, [], self.F)
        me.update()
        if self.closed:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()
        if self.smooth:
            me.shade_smooth()
        if self.mat is not None:
            me.materials.append(self.mat)
        ob = bpy.data.objects.new(self.name, me)
        link(ob, self.col)
        if self.bevel > 0:
            m = ob.modifiers.new("bevel", 'BEVEL')
            m.width = self.bevel
            m.segments = 2
            m.limit_method = 'ANGLE'
            m.angle_limit = math.radians(35)
        return ob


def np_mesh(name, V, T, mat, col="Station", colors=None, smooth=False):
    """Triangle mesh from numpy arrays (fast path for scatter geometry)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(V.astype(np.float32).tolist(), [], T.astype(np.int32).tolist())
    me.update()
    if colors is not None:
        ca = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT')
        ca.data.foreach_set("color", colors.astype(np.float32).ravel())
    if smooth:
        me.shade_smooth()
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    return ob


def image_plane(name, corners, image, mat_kwargs=None, col="Station", mirror=False, alpha=False):
    """Textured quad. corners = [bottom-left, bottom-right, top-right, top-left] (viewed from front)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(c) for c in corners], [], [(0, 1, 2, 3)])
    me.update()
    uv = me.uv_layers.new(name="UV")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    if mirror:
        uvs = [(1, 0), (0, 0), (0, 1), (1, 1)]
    for li, loop in enumerate(me.polygons[0].loop_indices):
        uv.data[loop].uv = uvs[li]
    m = mat_image(name + "_m", os.path.join(TEX, image), alpha=alpha, **(mat_kwargs or {}))
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    link(ob, col)
    return ob


# ============================================================== node-material builder
class Mat:
    def __init__(self, name):
        self.m = bpy.data.materials.new(name)
        try:
            self.m.use_nodes = True
        except Exception:
            pass
        self.nt = self.m.node_tree
        self.nt.nodes.clear()
        self.out = self.nt.nodes.new('ShaderNodeOutputMaterial')
        self._coord = None

    # ---- plumbing
    def node(self, idname, **attrs):
        n = self.nt.nodes.new(idname)
        for k, v in attrs.items():
            setattr(n, k, v)
        return n

    def set(self, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            self.nt.links.new(v, sock)
        elif sock.type == 'RGBA' and not isinstance(v, (int, float)) and len(v) == 3:
            sock.default_value = (v[0], v[1], v[2], 1.0)
        elif sock.type == 'RGBA' and isinstance(v, (int, float)):
            sock.default_value = (v, v, v, 1.0)
        else:
            sock.default_value = v

    def setall(self, n, d):
        for k, v in d.items():
            self.set(n.inputs[k], v)
        return n

    @property
    def obj(self):
        if self._coord is None:
            self._coord = self.node('ShaderNodeTexCoord').outputs['Object']
        return self._coord

    # ---- texture / utility nodes (each returns the main output socket)
    def mapping(self, vec=None, scale=(1, 1, 1), loc=(0, 0, 0), rot=(0, 0, 0)):
        n = self.node('ShaderNodeMapping')
        self.setall(n, {'Vector': vec or self.obj, 'Scale': scale, 'Location': loc, 'Rotation': rot})
        return n.outputs['Vector']

    def noise(self, vec=None, scale=5.0, detail=2.0, rough=0.5, dist=0.0):
        n = self.node('ShaderNodeTexNoise', noise_dimensions='3D')
        self.setall(n, {'Vector': vec or self.obj, 'Scale': scale, 'Detail': detail,
                        'Roughness': rough, 'Distortion': dist})
        return n.outputs['Fac']

    def voro(self, vec=None, scale=5.0, feature='F1', rand=1.0, out='Distance'):
        n = self.node('ShaderNodeTexVoronoi', voronoi_dimensions='3D', feature=feature)
        self.setall(n, {'Vector': vec or self.obj, 'Scale': scale, 'Randomness': rand})
        return n.outputs[out]

    def white(self, vec):
        n = self.node('ShaderNodeTexWhiteNoise', noise_dimensions='3D')
        self.set(n.inputs['Vector'], vec)
        return n.outputs['Value']

    def ramp(self, fac, stops, interp='LINEAR'):
        n = self.node('ShaderNodeValToRGB')
        n.color_ramp.interpolation = interp
        els = n.color_ramp.elements
        while len(els) < len(stops):
            els.new(0.5)
        for e, (p, c) in zip(els, stops):
            e.position = p
            e.color = (c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0)
        self.set(n.inputs['Fac'], fac)
        return n.outputs['Color']

    def mix(self, fac, a, b, blend='MIX'):
        n = self.node('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        self.set(n.inputs[0], fac)
        self.set(n.inputs[6], a)
        self.set(n.inputs[7], b)
        return n.outputs[2]

    def math(self, op, a, b=None, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.set(n.inputs[0], a)
        if b is not None:
            self.set(n.inputs[1], b)
        return n.outputs[0]

    def vmath(self, op, a, b=None):
        n = self.node('ShaderNodeVectorMath', operation=op)
        self.set(n.inputs[0], a)
        if b is not None:
            self.set(n.inputs[1], b)
        return n.outputs[0] if op not in ('LENGTH', 'DISTANCE', 'DOT_PRODUCT') else n.outputs['Value']

    def sep(self, vec):
        n = self.node('ShaderNodeSeparateXYZ')
        self.set(n.inputs['Vector'], vec)
        return n.outputs['X'], n.outputs['Y'], n.outputs['Z']

    def combine(self, x, y, z):
        n = self.node('ShaderNodeCombineXYZ')
        self.setall(n, {'X': x, 'Y': y, 'Z': z})
        return n.outputs['Vector']

    def maprange(self, v, a0, a1, b0, b1, clamp=True):
        n = self.node('ShaderNodeMapRange', clamp=clamp)
        self.setall(n, {'Value': v, 'From Min': a0, 'From Max': a1, 'To Min': b0, 'To Max': b1})
        return n.outputs['Result']

    def bump(self, height, strength=1.0, dist=0.02, normal=None, invert=False):
        n = self.node('ShaderNodeBump', invert=invert)
        d = {'Height': height, 'Strength': strength, 'Distance': dist}
        if normal is not None:
            d['Normal'] = normal
        self.setall(n, d)
        return n.outputs['Normal']

    def cell_rand(self, vec, size):
        """Random value constant inside every cell of the given size (x,y,z)."""
        v = self.vmath('DIVIDE', vec, size)
        v = self.vmath('FLOOR', v)
        return self.white(v)

    def attr_color(self, name="Col"):
        n = self.node('ShaderNodeAttribute', attribute_name=name)
        return n.outputs['Color']

    def obj_random(self):
        return self.node('ShaderNodeObjectInfo').outputs['Random']

    # ---- terminal shaders
    def principled(self, **inp):
        n = self.node('ShaderNodeBsdfPrincipled')
        self.setall(n, inp)
        self.nt.links.new(n.outputs['BSDF'], self.out.inputs['Surface'])
        return n

    def finish(self, shader_out):
        self.nt.links.new(shader_out, self.out.inputs['Surface'])
        return self.m


# ============================================================== palette of procedural materials
def mat_plain(name, color, rough=0.6, metal=0.0, spec=0.5):
    m = Mat(name)
    m.principled(**{'Base Color': color, 'Roughness': rough, 'Metallic': metal, 'Specular IOR Level': spec})
    return m.m


def mat_water(name, deep=(0.03, 0.10, 0.13), shallow=(0.10, 0.22, 0.24)):
    """海・池の水面: 大きなうねり+細かな波紋の法線(Bump)+深さ方向の色むら+強い映り込み(低ラフネス)。単色の板に見えないようにする(T4)。"""
    m = Mat(name)
    big = m.noise(scale=0.05, detail=3, rough=0.5)
    rip = m.noise(scale=0.9, detail=5, rough=0.55)
    h = m.mix(1.0, (0.5, 0.5, 0.5), rip, 'ADD') if hasattr(m, 'mix') else rip
    nrm = m.bump(rip, strength=0.35, dist=0.25)
    col = m.ramp(big, [(0.30, deep), (0.75, shallow)])
    m.principled(**{'Base Color': col, 'Roughness': 0.05, 'Specular IOR Level': 0.9, 'Normal': nrm})
    return m.m


def mat_concrete(name, base=(0.50, 0.49, 0.46), stain=0.5, seam=None, grain=1.0, seam_rot=(0, 0, 0), offset=0.0):
    """Weathered concrete. seam=(w, h) draws joints every w x h metres in the (rotated) XY plane."""
    m = Mat(name)
    big = m.noise(scale=0.35, detail=3, rough=0.6)
    mid = m.noise(scale=2.2, detail=6, rough=0.65)
    fine = m.noise(scale=90 * grain, detail=2, rough=0.7)
    tone = m.ramp(big, [(0.2, (0.78, 0.78, 0.78)), (0.8, (1.12, 1.12, 1.12))])
    col = m.mix(1.0, base, tone, 'MULTIPLY')
    stains = m.ramp(mid, [(0.42, (1, 1, 1)), (0.72, (0.62, 0.60, 0.56))])
    col = m.mix(stain, col, m.mix(1.0, col, stains, 'MULTIPLY'))
    height = fine
    if seam:
        sw, sh = (seam, seam) if isinstance(seam, (int, float)) else seam
        b = m.node('ShaderNodeTexBrick', offset=offset, squash=1.0)
        m.setall(b, {'Vector': m.mapping(rot=seam_rot), 'Color1': (1, 1, 1, 1), 'Color2': (1, 1, 1, 1),
                     'Mortar': (0, 0, 0, 1), 'Scale': 1.0, 'Mortar Size': 0.012, 'Mortar Smooth': 0.3,
                     'Brick Width': sw, 'Row Height': sh})
        mask = b.outputs['Color']  # 1 on the slab, 0 in the joint
        joint = m.ramp(mask, [(0.0, (0.40, 0.40, 0.40)), (1.0, (1, 1, 1))])
        col = m.mix(1.0, col, joint, 'MULTIPLY')
        height = m.math('ADD', m.math('MULTIPLY', fine, 0.35), m.math('MULTIPLY', mask, 0.65))
    nrm = m.bump(height, 0.45, 0.01)
    m.principled(**{'Base Color': col, 'Roughness': 0.88, 'Specular IOR Level': 0.3, 'Normal': nrm})
    return m.m


def mat_ballast(name):
    m = Mat(name)
    cell = m.voro(scale=26, rand=1.0, out='Color')
    sc = m.node('ShaderNodeSeparateColor')
    m.set(sc.inputs['Color'], cell)
    stone = m.ramp(sc.outputs['Red'], [(0.0, (0.20, 0.19, 0.18)), (0.5, (0.36, 0.35, 0.33)), (1.0, (0.55, 0.53, 0.50))])
    dirt = m.ramp(m.noise(scale=1.2, detail=4), [(0.35, (1, 1, 1)), (0.7, (0.55, 0.50, 0.42))])
    col = m.mix(1.0, stone, dirt, 'MULTIPLY')
    dist = m.voro(scale=26, feature='SMOOTH_F1', rand=1.0)
    nrm = m.bump(m.math('SUBTRACT', 1.0, dist), 1.2, 0.05)
    m.principled(**{'Base Color': col, 'Roughness': 0.92, 'Specular IOR Level': 0.3, 'Normal': nrm})
    return m.m


def mat_gravel(name, base=(0.46, 0.43, 0.37)):
    m = Mat(name)
    cell = m.node('ShaderNodeSeparateColor')
    m.set(cell.inputs['Color'], m.voro(scale=60, out='Color'))
    stone = m.ramp(cell.outputs['Red'], [(0.0, (0.55, 0.52, 0.46)), (1.0, (1.15, 1.10, 1.0))])
    col = m.mix(1.0, base, stone, 'MULTIPLY')
    patch = m.ramp(m.noise(scale=0.8, detail=4), [(0.35, (1, 1, 1)), (0.7, (0.6, 0.55, 0.45))])
    col = m.mix(1.0, col, patch, 'MULTIPLY')
    nrm = m.bump(m.math('SUBTRACT', 1.0, m.voro(scale=60, feature='SMOOTH_F1')), 0.9, 0.03)
    m.principled(**{'Base Color': col, 'Roughness': 0.95, 'Specular IOR Level': 0.2, 'Normal': nrm})
    return m.m


def mat_asphalt(name, base=(0.085, 0.085, 0.09), worn=0.5, crack_scale=0.55, crack_amt=0.8):
    m = Mat(name)
    grain = m.voro(scale=140, feature='F1')
    patches = m.ramp(m.noise(scale=0.5, detail=5), [(0.3, (0.8, 0.8, 0.8)), (0.7, (1.5, 1.5, 1.5))])
    col = m.mix(1.0, base, patches, 'MULTIPLY')
    sand = m.ramp(m.noise(scale=45, detail=2), [(0.45, (1, 1, 1)), (0.8, (2.2, 2.2, 2.1))])
    col = m.mix(worn, col, m.mix(1.0, col, sand, 'MULTIPLY'))
    crack = m.voro(scale=crack_scale, feature='DISTANCE_TO_EDGE')
    crack_m = m.ramp(crack, [(0.0, (0.2, 0.2, 0.2)), (0.025, (1, 1, 1))])
    col = m.mix(crack_amt, col, m.mix(1.0, col, crack_m, 'MULTIPLY'))
    h = m.math('ADD', m.math('MULTIPLY', grain, 0.6), m.math('MULTIPLY', m.maprange(crack, 0, 0.03, 0, 1), 0.7))
    nrm = m.bump(h, 0.7, 0.02)
    m.principled(**{'Base Color': col, 'Roughness': 0.85, 'Specular IOR Level': 0.35, 'Normal': nrm})
    return m.m


def mat_planks(name, color=(0.16, 0.085, 0.045), plank=0.12, weather=0.5):
    """Horizontal lap boards (shitami-ita)."""
    m = Mat(name)
    x, y, z = m.sep(m.obj)
    zz = m.math('DIVIDE', z, plank)
    fr = m.math('FRACT', zz)
    pid = m.math('FLOOR', zz)
    rnd = m.white(m.combine(pid, 0.0, 3.7))
    grain_vec = m.mapping(scale=(0.6, 30, 30))
    g1 = m.noise(grain_vec, scale=3.0, detail=4, rough=0.6)
    gtone = m.ramp(g1, [(0.3, (0.75, 0.75, 0.75)), (0.7, (1.2, 1.2, 1.2))])
    ptone = m.ramp(rnd, [(0.0, (0.8, 0.8, 0.8)), (1.0, (1.25, 1.25, 1.25))])
    col = m.mix(1.0, color, gtone, 'MULTIPLY')
    col = m.mix(1.0, col, ptone, 'MULTIPLY')
    gap = m.ramp(fr, [(0.0, (0.25, 0.25, 0.25)), (0.08, (1, 1, 1)), (1.0, (1, 1, 1))])
    col = m.mix(1.0, col, gap, 'MULTIPLY')
    wear = m.ramp(m.noise(scale=1.6, detail=5), [(0.4, (1, 1, 1)), (0.7, (1.9, 1.75, 1.6))])
    col = m.mix(weather, col, m.mix(1.0, col, wear, 'MULTIPLY'))
    h = m.math('ADD', m.math('MULTIPLY', m.math('SUBTRACT', 1.0, fr), 0.8), m.math('MULTIPLY', g1, 0.25))
    nrm = m.bump(h, 0.8, 0.03)
    m.principled(**{'Base Color': col, 'Roughness': 0.72, 'Specular IOR Level': 0.35, 'Normal': nrm})
    return m.m


def mat_wood(name, color=(0.20, 0.11, 0.06), rough=0.65, along='Z', weather=0.5, scale=1.0):
    """Generic stained wood with grain along an axis (posts, benches, beams)."""
    m = Mat(name)
    sc = {'X': (1.2, 30, 30), 'Y': (30, 1.2, 30), 'Z': (30, 30, 1.2)}[along]
    g = m.noise(m.mapping(scale=tuple(s * scale for s in sc)), scale=4.0, detail=5, rough=0.6)
    tone = m.ramp(g, [(0.3, (0.7, 0.7, 0.7)), (0.7, (1.25, 1.25, 1.25))])
    col = m.mix(1.0, color, tone, 'MULTIPLY')
    wear = m.ramp(m.noise(scale=1.3, detail=5), [(0.4, (1, 1, 1)), (0.75, (1.8, 1.65, 1.5))])
    col = m.mix(weather, col, m.mix(1.0, col, wear, 'MULTIPLY'))
    nrm = m.bump(g, 0.35, 0.01)
    m.principled(**{'Base Color': col, 'Roughness': rough, 'Specular IOR Level': 0.4, 'Normal': nrm})
    return m.m


def mat_plaster(name, color=(0.80, 0.77, 0.66), dirt=0.6):
    m = Mat(name)
    x, y, z = m.sep(m.obj)
    n1 = m.noise(scale=1.5, detail=5)
    stain = m.ramp(n1, [(0.35, (1, 1, 1)), (0.72, (0.72, 0.68, 0.60))])
    base_dirt = m.ramp(m.maprange(z, 0.8, 1.9, 1.0, 0.0), [(0.0, (1, 1, 1)), (1.0, (0.6, 0.55, 0.47))])
    streak = m.ramp(m.noise(m.mapping(scale=(8, 8, 0.8)), scale=3, detail=4), [(0.4, (1, 1, 1)), (0.75, (0.75, 0.72, 0.66))])
    col = m.mix(1.0, color, stain, 'MULTIPLY')
    col = m.mix(dirt, col, m.mix(1.0, m.mix(1.0, col, base_dirt, 'MULTIPLY'), streak, 'MULTIPLY'))
    fine = m.noise(scale=70, detail=3)
    nrm = m.bump(m.math('ADD', fine, m.math('MULTIPLY', n1, 0.4)), 0.35, 0.01)
    m.principled(**{'Base Color': col, 'Roughness': 0.93, 'Specular IOR Level': 0.2, 'Normal': nrm})
    return m.m


def mat_kawara(name, base=(0.075, 0.085, 0.10), tile_w=0.26, tile_l=0.19):
    m = Mat(name)
    rnd = m.cell_rand(m.obj, (tile_w, tile_l * 0.92, 1.0))
    tone = m.ramp(rnd, [(0.0, (0.75, 0.78, 0.85)), (1.0, (1.35, 1.35, 1.40))])
    mottle = m.ramp(m.noise(scale=18, detail=4), [(0.3, (0.8, 0.8, 0.85)), (0.7, (1.25, 1.25, 1.2))])
    moss = m.ramp(m.noise(scale=1.8, detail=5), [(0.55, (1, 1, 1)), (0.78, (1.3, 1.6, 1.0))])
    col = m.mix(1.0, base, tone, 'MULTIPLY')
    col = m.mix(1.0, col, mottle, 'MULTIPLY')
    col = m.mix(1.0, col, moss, 'MULTIPLY')
    m.principled(**{'Base Color': col, 'Roughness': 0.38, 'Specular IOR Level': 0.7,
                    'Coat Weight': 0.15, 'Coat Roughness': 0.3})
    return m.m


def mat_paint(name, color, rough=0.45, rust=0.35, metal=0.0, rust_scale=3.0):
    """Painted steel with rust blooms."""
    m = Mat(name)
    n = m.noise(scale=rust_scale, detail=6, rough=0.65)
    n2 = m.noise(scale=25, detail=3)
    rmask = m.ramp(n, [(0.5, (0, 0, 0)), (0.72, (1, 1, 1))])
    rmask = m.math('MULTIPLY', rmask, m.ramp(n2, [(0.3, (0.3, 0.3, 0.3)), (0.7, (1, 1, 1))]))
    rust_col = m.ramp(n2, [(0.0, (0.28, 0.11, 0.05)), (1.0, (0.45, 0.20, 0.08))])
    col = m.mix(m.math('MULTIPLY', rmask, rust), color, rust_col)
    chalk = m.ramp(m.noise(scale=1.2, detail=4), [(0.4, (1, 1, 1)), (0.8, (1.18, 1.18, 1.18))])
    col = m.mix(1.0, col, chalk, 'MULTIPLY')
    nrm = m.bump(m.math('MULTIPLY', rmask, n2), 0.4, 0.01)
    m.principled(**{'Base Color': col, 'Roughness': m.math('ADD', rough, m.math('MULTIPLY', rmask, 0.4)),
                    'Metallic': metal, 'Specular IOR Level': 0.45, 'Normal': nrm})
    return m.m


def mat_rail(name, z_lo=0.250, z_hi=0.268):
    m = Mat(name)
    x, y, z = m.sep(m.obj)
    n = m.noise(scale=6, detail=4)
    rust = m.ramp(n, [(0.0, (0.10, 0.052, 0.036)), (1.0, (0.21, 0.115, 0.065))])
    head = m.maprange(z, z_lo, z_hi, 0.0, 1.0)  # polished running surface
    steel = (0.30, 0.30, 0.31)
    col = m.mix(head, rust, steel)
    rough = m.maprange(z, z_lo, z_hi, 0.55, 0.25)
    nrm = m.bump(m.noise(m.mapping(scale=(0.3, 40, 40)), scale=20, detail=3), 0.2, 0.005)
    m.principled(**{'Base Color': col, 'Metallic': 0.6, 'Roughness': rough, 'Normal': nrm})
    return m.m


def mat_glass(name, tint=(0.82, 0.92, 0.95)):
    """Window glass that still lets direct light through (shadow-ray transparent)."""
    m = Mat(name)
    gl = m.node('ShaderNodeBsdfGlass')
    m.setall(gl, {'Color': tint, 'Roughness': 0.02, 'IOR': 1.45})
    tr = m.node('ShaderNodeBsdfTransparent')
    m.set(tr.inputs['Color'], tint)
    lp = m.node('ShaderNodeLightPath')
    mx = m.node('ShaderNodeMixShader')
    m.set(mx.inputs[0], lp.outputs['Is Shadow Ray'])
    m.set(mx.inputs[1], gl.outputs['BSDF'])
    m.set(mx.inputs[2], tr.outputs['BSDF'])
    m.finish(mx.outputs['Shader'])
    return m.m


def mat_image(name, path, rough=0.45, alpha=False, emit=0.0, spec=0.4):
    m = Mat(name)
    img = bpy.data.images.load(path, check_existing=True)
    t = m.node('ShaderNodeTexImage', image=img, interpolation='Cubic', extension='CLIP' if alpha else 'EXTEND')
    m.set(t.inputs['Vector'], m.node('ShaderNodeTexCoord').outputs['UV'])
    col = t.outputs['Color']
    dirt = m.ramp(m.noise(scale=3, detail=5), [(0.35, (1, 1, 1)), (0.8, (0.78, 0.76, 0.72))])
    col = m.mix(0.6, col, m.mix(1.0, col, dirt, 'MULTIPLY'))
    d = {'Base Color': col, 'Roughness': rough, 'Specular IOR Level': spec}
    if emit > 0:
        d['Emission Color'] = col
        d['Emission Strength'] = emit
    if alpha:
        d['Alpha'] = t.outputs['Alpha']
    m.principled(**d)
    return m.m


def mat_grass_ground(name):
    m = Mat(name)
    n = m.noise(scale=0.6, detail=5)
    n2 = m.noise(scale=8, detail=4)
    col = m.ramp(n, [(0.25, (0.17, 0.25, 0.07)), (0.55, (0.25, 0.33, 0.09)), (0.8, (0.34, 0.33, 0.12))])
    soil = m.ramp(n2, [(0.4, (1, 1, 1)), (0.8, (1.7, 1.45, 1.1))])
    col = m.mix(1.0, col, soil, 'MULTIPLY')
    nrm = m.bump(m.noise(scale=60, detail=3), 0.5, 0.02)
    m.principled(**{'Base Color': col, 'Roughness': 0.95, 'Specular IOR Level': 0.1, 'Normal': nrm})
    return m.m


def mat_paddy(name, green=(0.22, 0.38, 0.08), yellow=(0.46, 0.50, 0.14), vary=True):
    """Rice field seen from a distance: rows of clumps over wet soil."""
    m = Mat(name)
    x, y, z = m.sep(m.obj)
    row = m.math('FRACT', m.math('DIVIDE', y, 0.30))
    rowm = m.ramp(row, [(0.0, (0.2, 0.2, 0.2)), (0.35, (1, 1, 1)), (0.65, (1, 1, 1)), (1.0, (0.2, 0.2, 0.2))])
    clump = m.voro(m.mapping(scale=(3.3, 3.3, 3.3)), scale=1.0, rand=0.6)
    clump_c = m.ramp(clump, [(0.0, (1.15, 1.15, 1.15)), (0.55, (0.8, 0.8, 0.8))])
    n = m.noise(scale=0.07, detail=3)
    if vary:
        mixf = m.math('ADD', m.math('MULTIPLY', n, 0.8), m.math('MULTIPLY', m.obj_random(), 0.5), clamp=True)
    else:
        mixf = n
    col = m.mix(mixf, green, yellow)
    col = m.mix(1.0, col, rowm, 'MULTIPLY')
    col = m.mix(1.0, col, clump_c, 'MULTIPLY')
    soil = (0.10, 0.075, 0.05)
    col = m.mix(m.math('SUBTRACT', 1.0, m.math('MULTIPLY', rowm, 1.0)), col, soil)
    nrm = m.bump(m.math('ADD', rowm, m.math('SUBTRACT', 1.0, clump)), 0.6, 0.05)
    m.principled(**{'Base Color': col, 'Roughness': 0.65, 'Specular IOR Level': 0.35, 'Normal': nrm})
    return m.m


def mat_vertex_color(name, rough=0.55, trans=0.2, spec=0.3):
    """Material driven by the 'Col' colour attribute (grass blades, foliage)."""
    m = Mat(name)
    col = m.attr_color("Col")
    mott = m.ramp(m.voro(scale=40, feature='F1'), [(0.0, (1.15, 1.15, 1.1)), (1.0, (0.85, 0.85, 0.85))])
    col2 = m.mix(0.5, col, m.mix(1.0, col, mott, 'MULTIPLY'))
    p = m.node('ShaderNodeBsdfPrincipled')
    m.setall(p, {'Base Color': col2, 'Roughness': rough, 'Specular IOR Level': spec})
    tl = m.node('ShaderNodeBsdfTranslucent')
    m.set(tl.inputs['Color'], col2)
    mx = m.node('ShaderNodeMixShader')
    m.set(mx.inputs[0], trans)
    m.set(mx.inputs[1], p.outputs['BSDF'])
    m.set(mx.inputs[2], tl.outputs['BSDF'])
    m.finish(mx.outputs['Shader'])
    return m.m


def mat_bark(name, color=(0.10, 0.075, 0.055)):
    m = Mat(name)
    g = m.noise(m.mapping(scale=(6, 6, 0.6)), scale=4, detail=7, rough=0.7)
    col = m.mix(1.0, color, m.ramp(g, [(0.3, (0.6, 0.6, 0.6)), (0.7, (1.4, 1.4, 1.4))]), 'MULTIPLY')
    nrm = m.bump(g, 1.2, 0.05)
    m.principled(**{'Base Color': col, 'Roughness': 0.9, 'Specular IOR Level': 0.2, 'Normal': nrm})
    return m.m


def mat_hill(name, cam_pos, haze=(0.62, 0.72, 0.82), near=(0.07, 0.15, 0.07), far_dist=600.0):
    m = Mat(name)
    g = m.node('ShaderNodeNewGeometry')
    dist = m.vmath('DISTANCE', g.outputs['Position'], tuple(cam_pos))
    fog = m.maprange(dist, 120.0, far_dist, 0.0, 0.88)
    mott = m.ramp(m.noise(scale=0.08, detail=6, rough=0.7), [(0.3, (0.7, 0.8, 0.7)), (0.7, (1.4, 1.35, 1.1))])
    forest = m.ramp(m.noise(scale=0.35, detail=5), [(0.3, (0.05, 0.11, 0.05)), (0.7, (0.12, 0.22, 0.08))])
    col = m.mix(1.0, forest, mott, 'MULTIPLY')
    col = m.mix(fog, col, haze)
    m.principled(**{'Base Color': col, 'Roughness': 1.0, 'Specular IOR Level': 0.0})
    return m.m


def mat_emissive(name, color, strength=2.0):
    m = Mat(name)
    p = m.principled(**{'Base Color': color, 'Roughness': 0.5})
    m.setall(p, {'Emission Color': color, 'Emission Strength': strength})
    return m.m


def mat_stripes(name, c1=(0.8, 0.05, 0.04), c2=(0.92, 0.92, 0.9), period=0.5, axis='X'):
    m = Mat(name)
    x, y, z = m.sep(m.obj)
    a = {'X': x, 'Y': y, 'Z': z}[axis]
    f = m.math('FRACT', m.math('DIVIDE', a, period))
    mk = m.math('GREATER_THAN', f, 0.5)
    col = m.mix(mk, c1, c2)
    m.principled(**{'Base Color': col, 'Roughness': 0.4, 'Specular IOR Level': 0.5})
    return m.m


def mat_tactile(name, color=(0.78, 0.60, 0.04)):
    """Yellow guide blocks with a dome grid."""
    m = Mat(name)
    d = m.voro(scale=1.0 / 0.055, rand=0.0, feature='F1')
    dome = m.math('SUBTRACT', 1.0, m.math('MULTIPLY', d, 3.2, clamp=True), clamp=True)
    wear = m.ramp(m.noise(scale=3, detail=5), [(0.4, (1, 1, 1)), (0.8, (0.62, 0.58, 0.45))])
    col = m.mix(1.0, color, wear, 'MULTIPLY')
    nrm = m.bump(dome, 1.0, 0.02)
    m.principled(**{'Base Color': col, 'Roughness': 0.7, 'Specular IOR Level': 0.3, 'Normal': nrm})
    return m.m


# ============================================================== real-photo PBR materials (ambientCG, CC0)
PBR = f"{_R}/pbr"


def pbr_layer(m, tid, scale=1.0, rot=(0, 0, 0), vec=None):
    """Box-projected photo texture set in object space. Returns dict(col, rough, height, ao) sockets (None if missing)."""
    base = f"{PBR}/{tid}/{tid}_1K-JPG_"
    mv = m.mapping(vec=vec, scale=(1.0 / scale,) * 3, rot=rot)
    out = {}
    for key, suffix, cs in (("col", "Color", "sRGB"), ("rough", "Roughness", "Non-Color"),
                            ("height", "Displacement", "Non-Color"), ("ao", "AmbientOcclusion", "Non-Color")):
        p = base + suffix + ".jpg"
        if not os.path.exists(p):
            out[key] = None
            continue
        img = bpy.data.images.load(p, check_existing=True)
        img.colorspace_settings.name = cs
        n = m.node('ShaderNodeTexImage', image=img, projection='BOX', interpolation='Cubic')
        n.projection_blend = 0.3
        m.set(n.inputs['Vector'], mv)
        out[key] = n.outputs['Color']
    return out


def mat_pbr(name, tid, scale=1.0, tint=None, tint_amt=0.0, hsv=None, rough=None, rough_add=0.0, bump=0.5,
            bump_dist=0.02, ao_amt=0.6, macro=0.18, metal=0.0, rot=(0, 0, 0), spec=0.4, dirt=0.0):
    """Photo-based material. `macro` breaks up tiling with large-scale value noise; `dirt` adds grime streaks."""
    m = Mat(name)
    L = pbr_layer(m, tid, scale, rot)
    col = L["col"]
    if hsv is not None:
        h = m.node('ShaderNodeHueSaturation')
        m.setall(h, {'Hue': hsv[0], 'Saturation': hsv[1], 'Value': hsv[2], 'Fac': 1.0, 'Color': col})
        col = h.outputs['Color']
    if tint is not None and tint_amt > 0:
        col = m.mix(tint_amt, col, m.mix(1.0, col, tint, 'MULTIPLY'))
    if L["ao"] is not None and ao_amt > 0:
        col = m.mix(ao_amt, col, m.mix(1.0, col, L["ao"], 'MULTIPLY'))
    if macro > 0:
        nz = m.noise(scale=0.22, detail=4, rough=0.6)
        mac = m.ramp(nz, [(0.25, (1 - macro,) * 3), (0.75, (1 + macro * 0.8,) * 3)])
        col = m.mix(1.0, col, mac, 'MULTIPLY')
        nz2 = m.noise(scale=0.03, detail=3, rough=0.55)
        k = min(0.5, macro * 1.6)
        mac2 = m.ramp(nz2, [(0.3, (1 - k * 0.6, 1 - k * 0.2, 1 - k * 0.9)), (0.7, (1 + k * 0.5, 1 + k * 0.3, 1 - k * 0.2))])
        col = m.mix(1.0, col, mac2, 'MULTIPLY')
    if dirt > 0:
        x, y, z = m.sep(m.obj)
        streak = m.ramp(m.noise(m.mapping(scale=(5, 5, 0.5)), scale=2.2, detail=5),
                        [(0.35, (1, 1, 1)), (0.8, (0.62, 0.60, 0.55))])
        base = m.ramp(m.maprange(z, 0.0, 1.6, 1.0, 0.0), [(0.0, (1, 1, 1)), (1.0, (0.7, 0.67, 0.60))])
        col = m.mix(dirt, col, m.mix(1.0, m.mix(1.0, col, streak, 'MULTIPLY'), base, 'MULTIPLY'))
    r = L["rough"]
    if rough is not None:
        r = rough
    elif r is not None and rough_add:
        r = m.math('ADD', r, rough_add, clamp=True)
    elif r is None:
        r = 0.75
    d = {'Base Color': col, 'Roughness': r, 'Metallic': metal, 'Specular IOR Level': spec}
    if L["height"] is not None and bump > 0:
        d['Normal'] = m.bump(L["height"], bump, bump_dist)
    m.principled(**d)
    return m.m


def mat_pbr_blend(name, tid_a, tid_b, scale_a=1.0, scale_b=1.0, mask=None, tint_a=None, tint_b=None, bump=0.6,
                  macro=0.15, extra_dark=None):
    """Blend two photo textures by a mask socket-builder `mask(m)` (e.g. vertex colour / noise)."""
    m = Mat(name)
    A = pbr_layer(m, tid_a, scale_a)
    B = pbr_layer(m, tid_b, scale_b)
    ca, cb = A["col"], B["col"]
    if tint_a is not None:
        ca = m.mix(1.0, ca, tint_a, 'MULTIPLY')
    if tint_b is not None:
        cb = m.mix(1.0, cb, tint_b, 'MULTIPLY')
    f = mask(m)
    col = m.mix(f, ca, cb)
    if extra_dark is not None:
        col = m.mix(1.0, col, extra_dark(m), 'MULTIPLY')
    if macro > 0:
        nz = m.noise(scale=0.25, detail=4, rough=0.6)
        col = m.mix(1.0, col, m.ramp(nz, [(0.25, (1 - macro,) * 3), (0.75, (1 + macro * 0.8,) * 3)]), 'MULTIPLY')
    ra = A["rough"] if A["rough"] is not None else 0.8
    rb = B["rough"] if B["rough"] is not None else 0.8
    rr = m.mix(f, ra, rb) if (A["rough"] is not None and B["rough"] is not None) else 0.85
    ha, hb = A["height"], B["height"]
    h = m.mix(f, ha, hb)
    nrm = m.bump(h, bump, 0.03)
    m.principled(**{'Base Color': col, 'Roughness': rr, 'Specular IOR Level': 0.25, 'Normal': nrm})
    return m.m


def wrap_tree(nt):
    """Use Mat's node helpers on an arbitrary node tree (e.g. the world)."""
    o = Mat.__new__(Mat)
    o.m, o.nt, o.out, o._coord = None, nt, None, None
    return o
