"""kit7: 駅間の特殊構造。
  subway   : 地下鉄(開削トンネル=箱形、坑口手前は掘割)。地面には切り欠き(cutter)を作り、apply_cuts() で地面をくり抜く。
  street   : 路面電車の軌道(舗装・縁石・歩道・街灯・電車線柱)。
  mono_link: モノレール高架桁(橋脚つき・走行面・給電レール)。
  ramp_fn  : 勾配を折れ点で与える高さ関数(なめらか)。
座標は kit5 と同じ(世界座標の中心線 P と弧長 s)。"""
import math
import numpy as np
import bpy
import bmesh
from common import *
import lib, core, trackkit, kit5
from props import G
from veg import np_mesh
from kit5 import frames_at, mats5

CLEAR = 5.0          # レール面から天井下端まで
ROOF_TOP = -0.30     # 覆工の上面(地面の下端に揃える)
ROOF_BOT = -1.00


def ramp_fn(knots, ease=14.0, ds=1.0):
    """knots=[(s,z),...] を直線補間し、幅 ease(m) で平滑化した高さ関数を返す。"""
    S = np.array([k[0] for k in knots], float)
    Z = np.array([k[1] for k in knots], float)
    smax = S[-1] + 40.0
    g = np.arange(-40.0, smax + ds, ds)
    z = np.interp(g, S, Z)
    k = max(1, int(ease / ds))
    ker = np.ones(2 * k + 1) / (2 * k + 1)
    zp = np.pad(z, k, mode="edge")
    zs = np.convolve(zp, ker, mode="valid")
    return lambda s: np.interp(np.asarray(s, float), g, zs)


def _bm_clean(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def _cutter(name, pos, nrm, half, z0=-2.5, z1=2.0):
    """pos(N,2) に沿う帯を z0..z1 に押し出した閉じた立体(地面をくり抜くための型)。"""
    n = len(pos)
    if n < 2:
        return None
    Lp = pos + nrm * half
    Rp = pos - nrm * half
    V = []
    for i in range(n):
        V += [(Lp[i, 0], Lp[i, 1], z1), (Rp[i, 0], Rp[i, 1], z1), (Lp[i, 0], Lp[i, 1], z0), (Rp[i, 0], Rp[i, 1], z0)]
    V = np.array(V)
    T = []
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        T += [(a, a + 1, b + 1), (a, b + 1, b)]                 # top
        T += [(a + 2, b + 3, a + 3), (a + 2, b + 2, b + 3)]     # bottom
        T += [(a, b, b + 2), (a, b + 2, a + 2)]                 # left
        T += [(a + 1, a + 3, b + 3), (a + 1, b + 3, b + 1)]     # right
    T += [(0, 2, 3), (0, 3, 1)]
    e = 4 * (n - 1)
    T += [(e, e + 1, e + 3), (e, e + 3, e + 2)]
    ob = np_mesh(name, V, np.array(T), None, "Cutters")
    _bm_clean(ob)
    ob["is_cutter"] = 1
    ob.hide_render = True
    return ob


def subway(P, s0, s1, name="subway", zfun=None, half=3.15, lights=True):
    """開削式の地下鉄。レール面が地表から CLEAR+被り以上深い所は覆工(箱形)、浅い所は掘割(擁壁)。"""
    mats5()
    ss = np.arange(s0, s1 + 0.5, 2.0)
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else np.asarray(zfun(ss), float)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    g = G(name, "Props")
    gl = G(name + "_lt", "Props")
    covered = zs + CLEAR <= ROOF_BOT + 0.001
    below = zs < 0.25
    wt = 0.55
    for i in range(len(ss) - 1):
        a, b = pos[i], pos[i + 1]
        z0, z1 = zs[i], zs[i + 1]
        zm = (z0 + z1) / 2
        if not (below[i] or below[i + 1]):
            continue
        # 底版(インバート)
        g.a("k5_conc").sbox((a[0], a[1], z0 - 0.45), (b[0], b[1], z1 - 0.45), 2 * half + 2 * wt, 0.7)
        cov = covered[i] and covered[i + 1]
        for sg in (-1, 1):
            p0 = a + nrm[i] * sg * (half + wt / 2)
            p1 = b + nrm[i + 1] * sg * (half + wt / 2)
            top = (ROOF_BOT + 0.02) if cov else 0.12
            bot = zm - 0.75
            zc = (top + bot) / 2
            hh = top - bot
            g.a("k5_conc").sbox((p0[0], p0[1], zc), (p1[0], p1[1], zc), wt, hh)
            if not cov:
                # 掘割の笠コンクリートと地上側の転落防止柵
                g.a("k5_stone").sbox((p0[0], p0[1], 0.16), (p1[0], p1[1], 0.16), wt + 0.25, 0.12)
                q0 = a + nrm[i] * sg * (half + wt + 0.5)
                q1 = b + nrm[i + 1] * sg * (half + wt + 0.5)
                g.a("k5_steel").sbox((q0[0], q0[1], 0.95), (q1[0], q1[1], 0.95), 0.05, 0.05)
                if i % 3 == 0:
                    g.a("k5_steel").sbox((q0[0], q0[1], 0.1), (q0[0], q0[1], 1.0), 0.07, 0.07)
            else:
                # 壁面の仕上げ: 腰のタイル帯と避難用の側歩道
                if sg == 1:
                    w0 = a + nrm[i] * (half - 0.45)
                    w1 = b + nrm[i + 1] * (half - 0.45)
                    g.a("k5_conc").sbox((w0[0], w0[1], zm - 0.1), (w1[0], w1[1], zm - 0.1), 0.9, 0.24)
                u0 = a + nrm[i] * sg * (half - 0.04)
                u1 = b + nrm[i + 1] * sg * (half - 0.04)
                g.a("k5_stone").sbox((u0[0], u0[1], zm + 1.0), (u1[0], u1[1], zm + 1.0), 0.04, 1.8)
        if cov:
            r0 = a
            r1 = b
            g.a("k5_conc").sbox((r0[0], r0[1], (ROOF_TOP + ROOF_BOT) / 2), (r1[0], r1[1], (ROOF_TOP + ROOF_BOT) / 2), 2 * half + 2 * wt, ROOF_TOP - ROOF_BOT)
            # ケーブルラックと剛体架線(天井吊り)
            for sg in (-1, 1):
                c0 = a + nrm[i] * sg * (half - 0.25)
                c1 = b + nrm[i + 1] * sg * (half - 0.25)
                g.a("k5_steel").sbox((c0[0], c0[1], zm + 3.3), (c1[0], c1[1], zm + 3.3), 0.3, 0.05)
            g.a("iron_black").sbox((a[0], a[1], z0 + CLEAR - 0.25), (b[0], b[1], z1 + CLEAR - 0.25), 0.07, 0.1)
            if i % 4 == 0:
                g.a("k5_steel").sbox((a[0], a[1], z0 + CLEAR - 0.25), (a[0], a[1], z0 + CLEAR + 0.0), 0.05, 0.05)
            if lights and i % 5 == 0:
                for sg in (-1, 1):
                    l0 = a + nrm[i] * sg * (half - 0.2)
                    gl.a("lamp_glow").box(l0[0] - 0.3, l0[0] + 0.3, l0[1] - 0.06, l0[1] + 0.06, zm + 3.05, zm + 3.15) if False else \
                        gl.a("lamp_glow").sbox((l0[0], l0[1], zm + 3.1), (l0[0] + math.cos(ang[i]) * 0.9, l0[1] + math.sin(ang[i]) * 0.9, zm + 3.1), 0.12, 0.08)
    # 坑口(掘割→覆工の切り替わり)に門型の梁
    for i in range(1, len(ss) - 1):
        if covered[i] != covered[i - 1] and zs[i] < 0.5:
            c = pos[i]
            w = 2 * half + 2 * wt
            g.a("k5_stone", bevel=0.03).sbox((c[0], c[1], ROOF_BOT - 0.15), (c[0] + math.cos(ang[i]) * 0.9, c[1] + math.sin(ang[i]) * 0.9, ROOF_BOT - 0.15), w + 0.6, 0.9)
    g.build()
    gl.build()
    # 地面の切り欠き(掘割部分: 地表から見える範囲)
    idx = np.where(below & ~covered)[0]
    if len(idx):
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        for k, r in enumerate(runs):
            r = np.arange(max(0, r[0] - 1), min(len(ss), r[-1] + 2))
            if len(r) >= 2:
                _cutter(f"{name}_cut{k}", pos[r], nrm[r], half + wt + 0.15)
    return int(covered.sum())


def apply_cuts():
    """Cutters を使って Ground の地面(kit_ground* / world_ground*)をくり抜き、型を削除する。"""
    cuts = [o for o in bpy.data.objects if o.get("is_cutter")]
    if not cuts:
        return 0
    grounds = [o for o in bpy.data.objects if o.type == 'MESH' and (o.name.startswith("kit_ground") or o.name.startswith("world_ground"))]
    tmp = bpy.data.collections.new("CutTmp")
    bpy.context.scene.collection.children.link(tmp)
    for c in cuts:
        for cc in list(c.users_collection):
            cc.objects.unlink(c)
        tmp.objects.link(c)
        c.hide_viewport = False
    bpy.context.view_layer.update()
    for gr in grounds:
        m = gr.modifiers.new("cut", 'BOOLEAN')
        m.operation = 'DIFFERENCE'
        m.operand_type = 'COLLECTION'
        m.collection = tmp
        m.solver = 'EXACT'
        dg = bpy.context.evaluated_depsgraph_get()
        ge = gr.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ge)
        gr.modifiers.remove(m)
        gr.data = me
    for c in cuts:
        bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.collections.remove(tmp)
    return len(cuts)


# ----------------------------------------------------------------------------- 路面電車
def street(P, s0, s1, name="street", road_w=8.8, zfun=None):
    """併用軌道: 舗装道路・縁石・歩道・街灯・電車線柱(トロリ線)。レールは舗装面と面一。"""
    mats5()
    ss = np.arange(s0, s1 + 0.5, 3.0)
    pos, ang = frames_at(P, ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    pts = [tuple(p) for p in pos]
    zr = 0.115
    core.ribbon(name + "_asph", pts, road_w, M["asphalt"] if "asphalt" in M else M["road"], z0=zr, rut=False, col="Roads")
    for sg in (-1, 1):
        wp = [tuple(p + n * sg * (road_w / 2 + 1.5)) for p, n in zip(pos, nrm)]
        core.ribbon(f"{name}_walk{sg}", wp, 3.0, M["paving"] if "paving" in M else M["road"], z0=0.2, rut=False, col="Roads")
    g = G(name + "_fit", "Props")
    for i in range(len(ss) - 1):
        a, b = pos[i], pos[i + 1]
        for sg in (-1, 1):
            c0 = a + nrm[i] * sg * (road_w / 2 + 0.06)
            c1 = b + nrm[i + 1] * sg * (road_w / 2 + 0.06)
            g.a("k5_conc").sbox((c0[0], c0[1], 0.1), (c1[0], c1[1], 0.1), 0.18, 0.22)
        if i % 2 == 0:       # 車線境界の破線
            for sg in (-1, 1):
                d0 = a + nrm[i] * sg * 2.9
                d1 = a + (b - a) * 0.5 + nrm[i] * sg * 2.9
                g.a("white" if "white" in M else "plasterw").sbox((d0[0], d0[1], zr + 0.002), (d1[0], d1[1], zr + 0.002), 0.1, 0.006)
    # 電車線柱(千鳥・腕金でトロリ線を吊る)と街灯
    sp = np.arange(s0 + 12.0, s1 - 8.0, 30.0)
    pp, pa = frames_at(P, sp)
    pn = np.stack([-np.sin(pa), np.cos(pa)], 1)
    for k in range(len(sp)):
        sg = 1 if k % 2 == 0 else -1
        q = pp[k] + pn[k] * sg * (road_w / 2 + 0.7)
        c = pp[k] + pn[k] * 0.0
        g.a("k5_steel", bevel=0.01).sbox((q[0], q[1], 0.0), (q[0], q[1], 7.0), 0.2, 0.2)
        g.a("k5_steel").sbox((q[0], q[1], 6.5), (c[0], c[1], 6.0), 0.08, 0.1)
        g.a("k5_steel").sbox((q[0], q[1], 5.2), (c[0], c[1], 5.85), 0.05, 0.06)
        g.a("porcelain").cyl((c[0], c[1], 5.85), (c[0], c[1], 6.1), 0.05, seg=8)
        if k % 2 == 1:   # 街灯(反対側)
            r = pp[k] + pn[k] * (-sg) * (road_w / 2 + 0.7)
            g.a("iron_black").sbox((r[0], r[1], 0.0), (r[0], r[1], 6.2), 0.14, 0.14)
            g.a("iron_black").sbox((r[0], r[1], 6.1), (r[0] + pn[k][0] * sg * 1.1, r[1] + pn[k][1] * sg * 1.1, 6.2), 0.07, 0.07)
            lp = r + pn[k] * sg * 1.1
            g.a("lamp_glow").box(lp[0] - 0.2, lp[0] + 0.2, lp[1] - 0.12, lp[1] + 0.12, 6.05, 6.12)
    sub, sa = frames_at(P, np.arange(s0 + 12.0, s1 - 8.0, 4.0))
    for i in range(len(sub) - 1):
        z0 = 5.85 + 0.15 * math.sin(i * 0.5)
        g.a("iron_black").sbox((sub[i][0], sub[i][1], z0), (sub[i + 1][0], sub[i + 1][1], 5.85 + 0.15 * math.sin((i + 1) * 0.5)), 0.025, 0.025)
    g.build()


# ----------------------------------------------------------------------------- モノレール
def mono_link(P, s0, s1, name="mono", zfun=None, span=22.0):
    """跨座式モノレールの高架桁。PC桁(幅0.85・高1.5)+橋脚+走行面・ガイドレール・給電レール。"""
    mats5()
    g = G(name, "Props")
    ss = np.arange(s0, s1 + 0.5, 2.0)
    pos, ang = frames_at(P, ss)
    zs = np.asarray(zfun(ss), float) if zfun is not None else np.full(len(ss), 8.2)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    for i in range(len(ss) - 1):
        a, b = pos[i], pos[i + 1]
        z0, z1 = zs[i], zs[i + 1]
        g.a("concrete", bevel=0.02).sbox((a[0], a[1], z0 - 0.75), (b[0], b[1], z1 - 0.75), 0.85, 1.5)
        g.a("iron_black").sbox((a[0], a[1], z0 + 0.02), (b[0], b[1], z1 + 0.02), 0.62, 0.04)           # 走行面の鋼板
        for sg in (-1, 1):
            c0, c1 = a + nrm[i] * sg * 0.45, b + nrm[i + 1] * sg * 0.45
            g.a("k5_steel").sbox((c0[0], c0[1], z0 - 0.3), (c1[0], c1[1], z1 - 0.3), 0.05, 0.28)          # 案内・安定輪の走行面
        pw = a + nrm[i] * 0.47
        g.a("iron_black").sbox((pw[0], pw[1], z0 - 0.65), ((b + nrm[i + 1] * 0.47)[0], (b + nrm[i + 1] * 0.47)[1], z1 - 0.65), 0.04, 0.06)     # 給電レール
    sp = np.arange(s0 + 6.0, s1 - 2.0, span)
    pp, pa = frames_at(P, sp)
    pz = np.asarray(zfun(sp), float) if zfun is not None else np.full(len(sp), 8.2)
    for k in range(len(sp)):
        c = pp[k]
        h = pz[k] - 1.5
        g.a("concrete", bevel=0.05).boxc(c[0], c[1], h / 2 - 0.2, 1.5, 1.5, h + 0.4, rz=float(pa[k]))
        g.a("concrete", bevel=0.05).boxc(c[0], c[1], h + 0.15, 3.0, 1.1, 0.5, rz=float(pa[k]))        # 橋脚の頭(支承台)
        g.a("k5_steel").boxc(c[0], c[1], h + 0.47, 0.5, 0.5, 0.12, rz=float(pa[k]))                       # 支承
        g.a("concrete").boxc(c[0], c[1], -0.1, 2.4, 2.4, 0.3, rz=float(pa[k]))                            # 基礎フーチング
    g.build()
