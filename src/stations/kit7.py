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
        g.a("ug_conc").sbox((a[0], a[1], z0 - 0.45), (b[0], b[1], z1 - 0.45), 2 * half + 2 * wt, 0.7)
        cov = covered[i] and covered[i + 1]
        for sg in (-1, 1):
            p0 = a + nrm[i] * sg * (half + wt / 2)
            p1 = b + nrm[i + 1] * sg * (half + wt / 2)
            top = (ROOF_BOT + 0.02) if cov else 0.12
            bot = zm - 0.75
            zc = (top + bot) / 2
            hh = top - bot
            g.a("ug_conc").sbox((p0[0], p0[1], zc), (p1[0], p1[1], zc), wt, hh)
            if not cov:
                # 掘割の笠コンクリートと地上側の転落防止柵
                g.a("k5_stone").sbox((p0[0], p0[1], 0.16), (p1[0], p1[1], 0.16), wt + 0.25, 0.12)
                q0 = a + nrm[i] * sg * (half + wt + 0.5)
                q1 = b + nrm[i + 1] * sg * (half + wt + 0.5)
                g.a("k5_steel").sbox((q0[0], q0[1], 0.95), (q1[0], q1[1], 0.95), 0.05, 0.05)
                if i % 3 == 0:
                    g.a("k5_steel").sbox((q0[0], q0[1], 0.1), (q0[0], q0[1], 1.0), 0.07, 0.07)
                if i % 3 == 0:     # 控え壁(内側の付柱)と水抜き穴・梯子
                    zc_ = (0.12 + (zm - 0.75)) / 2
                    pi0 = a + nrm[i] * sg * (half - 0.30)
                    pi1 = a + nrm[i] * sg * (half + 0.02)
                    g.a("ug_conc2", bevel=0.02).sbox((pi0[0], pi0[1], zc_), (pi1[0], pi1[1], zc_), 0.55, 0.12 - (zm - 0.75))
                    wh = a + nrm[i] * sg * (half - 0.02) + (b - a) * 0.5
                    g.a("iron_black").sbox((wh[0], wh[1], zm - 0.35), (wh[0] - nrm[i][0] * sg * 0.08, wh[1] - nrm[i][1] * sg * 0.08, zm - 0.35), 0.1, 0.1)
            else:
                # 壁面の仕上げ: 腰のタイル帯と避難用の側歩道
                if sg == 1:
                    w0 = a + nrm[i] * (half - 0.45)
                    w1 = b + nrm[i + 1] * (half - 0.45)
                    g.a("ug_conc").sbox((w0[0], w0[1], zm - 0.1), (w1[0], w1[1], zm - 0.1), 0.9, 0.24)
                u0 = a + nrm[i] * sg * (half - 0.04)
                u1 = b + nrm[i + 1] * sg * (half - 0.04)
                g.a("k5_stone").sbox((u0[0], u0[1], zm + 1.0), (u1[0], u1[1], zm + 1.0), 0.04, 1.8)
        if cov:
            r0 = a
            r1 = b
            g.a("ug_conc").sbox((r0[0], r0[1], (ROOF_TOP + ROOF_BOT) / 2), (r1[0], r1[1], (ROOF_TOP + ROOF_BOT) / 2), 2 * half + 2 * wt, ROOF_TOP - ROOF_BOT)
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
            od_ = np.array([math.cos(ang[i]), math.sin(ang[i])]) * (-1.0 if covered[i] else 1.0)
            fc = c + od_ * 0.55
            g.a("ug_conc2", bevel=0.03).sbox((fc[0], fc[1], ROOF_TOP + 0.05), (fc[0] + od_[0] * 0.6, fc[1] + od_[1] * 0.6, ROOF_TOP + 0.05), w + 0.9, 0.26)   # 軒蛇腹
            pl = c + od_ * 0.62
            g.a("k5_stone", bevel=0.02).sbox((pl[0], pl[1], ROOF_BOT + 0.35), (pl[0] + od_[0] * 0.08, pl[1] + od_[1] * 0.08, ROOF_BOT + 0.35), 1.8, 0.4)   # 扁額
            g.a("iron_black").sbox((pl[0] + od_[0] * 0.07, pl[1] + od_[1] * 0.07, ROOF_BOT + 0.35), (pl[0] + od_[0] * 0.1, pl[1] + od_[1] * 0.1, ROOF_BOT + 0.35), 1.5, 0.28)
    _surface_works(P, ss, pos, ang, nrm, zs, covered, below, half, wt, g, name)
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


def _vent_tower(g, c, ang, st, sg):
    """換気塔。st['type'] で 4 種: pilaster(煉瓦+付柱+アーチ開口) / mushroom(円筒+笠) / slab(RC+庇+格子) / grate(地表格子ピット)。"""
    ca, sa = math.cos(ang), math.sin(ang)

    def at(u, v):
        return (c[0] + ca * u - sa * v, c[1] + sa * u + ca * v)
    hx, hy, hz = st['hx'], st['hy'], st['hz']
    ty = st.get('type', 'pilaster')
    dk = "iron_black"
    if ty == "pilaster":
        # 壁体+四隅の付柱+胴蛇腹+アーチ形の開口(凹んだ黒い羽板)+寄棟屋根
        for q in range(4):
            a_, b_ = [at(-hx, -hy), at(hx, -hy), at(hx, hy), at(-hx, hy)][q], [at(-hx, -hy), at(hx, -hy), at(hx, hy), at(-hx, hy)][(q + 1) % 4]
            g.a(st["mat"], bevel=0.02).sbox((a_[0], a_[1], hz / 2), (b_[0], b_[1], hz / 2), 0.32, hz)
        for ux, vy in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)):
            p0 = at(ux, vy)
            g.a("ug_conc2", bevel=0.03).box(p0[0] - 0.3, p0[0] + 0.3, p0[1] - 0.3, p0[1] + 0.3, 0.0, hz + 0.1)
        for zz in (hz * 0.34, hz * 0.68):
            for v_ in (-hy - 0.2, hy + 0.2):
                a_, b_ = at(-hx - 0.12, v_), at(hx + 0.12, v_)
                g.a("ug_conc2").sbox((a_[0], a_[1], zz), (b_[0], b_[1], zz), 0.2, 0.16)
        nb = max(2, int(2 * hx / 0.9))
        for v_ in (-hy - 0.18, hy + 0.18):
            for k in range(nb):
                u = -hx + (k + 0.5) * 2 * hx / nb
                for zz, hh in ((hz * 0.5, hz * 0.22),):
                    a_, b_ = at(u - 0.22, v_), at(u + 0.22, v_)
                    g.a(dk).sbox((a_[0], a_[1], zz), (b_[0], b_[1], zz), 0.07, hh)
                    for lv in range(4):
                        a_, b_ = at(u - 0.2, v_ + 0.04 * (1 if v_ > 0 else -1)), at(u + 0.2, v_ + 0.04 * (1 if v_ > 0 else -1))
                        g.a("ug_conc2").sbox((a_[0], a_[1], zz - hh / 2 + lv * hh / 3.6 + 0.1), (b_[0], b_[1], zz - hh / 2 + lv * hh / 3.6 + 0.1), 0.03, 0.04)
        rh = 1.2
        for k_ in range(5):     # 段状の寄棟屋根(隙間なく積む)
            f_ = 1.0 - k_ * 0.17
            g.a("tin").boxc(c[0], c[1], hz + 0.11 + k_ * 0.22, (2 * hx + 0.8) * f_, (2 * hy + 0.8) * f_, 0.24, rz=ang)
    elif ty == "mushroom":
        r = max(hy * 1.15, 0.9)
        g.a("ug_conc2").cyl((c[0], c[1], 0.0), (c[0], c[1], 0.45), r + 0.35, r + 0.25, seg=20)
        g.a("ug_conc", smooth=False).cyl((c[0], c[1], 0.45), (c[0], c[1], hz), r, r * 0.95, seg=20)
        for k in range(12):
            th = ang + k * math.pi / 6
            q = (c[0] + math.cos(th) * (r + 0.02), c[1] + math.sin(th) * (r + 0.02))
            for lv in range(5):
                zz = hz * 0.55 + lv * 0.2
                g.a(dk).boxc(q[0], q[1], zz, 0.05, 0.62, 0.07, rz=th)
        g.a("ug_conc2").cyl((c[0], c[1], hz), (c[0], c[1], hz + 0.25), r + 0.55, r + 0.45, seg=20)
        g.a("tin").cyl((c[0], c[1], hz + 0.25), (c[0], c[1], hz + 0.25 + 0.9), r + 0.5, 0.12, seg=20)
        g.a(dk).cyl((c[0], c[1], hz + 1.15), (c[0], c[1], hz + 1.55), 0.06, seg=8)
    elif ty == "slab":
        # RC の薄い塔: 全高の縦ルーバー帯+張り出す庇+頂部の小さな採光窓
        g.a("ug_conc", bevel=0.02).boxc(c[0], c[1], hz / 2, 2 * hx, 2 * hy, hz, rz=ang)
        g.a("ug_conc2").boxc(c[0], c[1], 0.3, 2 * hx + 0.5, 2 * hy + 0.5, 0.6, rz=ang)
        for v_ in (-hy - 0.03, hy + 0.03):
            for k in range(int(2 * hx / 0.18)):
                u = -hx + 0.25 + k * 0.18
                if abs(u) > hx - 0.1:
                    continue
                a_, b_ = at(u, v_), at(u, v_)
                g.a(dk).boxc(a_[0], a_[1], hz * 0.62, 0.06, 0.05, hz * 0.55, rz=ang)
        g.a("ug_conc2").boxc(c[0], c[1], hz + 0.14, 2 * hx + 1.4, 2 * hy + 1.4, 0.28, rz=ang)
        g.a("ug_conc").boxc(c[0], c[1], hz + 0.28 + 0.35, 2 * hx * 0.5, 2 * hy * 0.6, 0.7, rz=ang)
        for k in range(3):
            g.a(dk).boxc(c[0], c[1], hz + 0.28 + 0.2 + k * 0.17, 2 * hx * 0.5 + 0.02, 2 * hy * 0.6 + 0.02, 0.04, rz=ang)
        a_ = at(hx + 0.04, 0)
        g.a(dk).boxc(a_[0], a_[1], 0.9, 0.05, 0.9, 1.8, rz=ang)
    else:   # grate: 歩道面に格子蓋のピット+低い立上り+鋳鉄の格子
        L_, W_ = hx * 1.6, hy * 1.4
        g.a("ug_conc2").boxc(c[0], c[1], 0.12, 2 * L_ + 0.5, 2 * W_ + 0.5, 0.24, rz=ang)
        g.a(dk).boxc(c[0], c[1], 0.14, 2 * L_, 2 * W_, 0.05, rz=ang)
        for k in range(int(2 * L_ / 0.14)):
            u = -L_ + 0.07 + k * 0.14
            a_ = at(u, 0)
            g.a("iron_black").boxc(a_[0], a_[1], 0.26, 0.05, 2 * W_ - 0.04, 0.035, rz=ang)
        for v_ in (-W_ * 0.5, W_ * 0.5):
            a_, b_ = at(-L_, v_), at(L_, v_)
            g.a("iron_black").sbox((a_[0], a_[1], 0.25), (b_[0], b_[1], 0.25), 0.06, 0.05)
        # 小さな排気筒(格子の脇)
        a_ = at(L_ + 0.9, 0)
        g.a("ug_conc").cyl((a_[0], a_[1], 0.0), (a_[0], a_[1], 2.6), 0.32, seg=12)
        g.a("tin").cyl((a_[0], a_[1], 2.6), (a_[0], a_[1], 2.95), 0.5, 0.1, seg=12)


def tram_bed(pts, name, gauge=1.067, z0=0.2465):
    """併用軌道の敷石帯(サイコロ石の舗装)と溝付きレールの溝(軌間の内側/外側の黒い線)。pts=軌道中心線(N,2)。"""
    mats5()
    P = np.asarray(pts, float)
    if len(P) < 2:
        return
    d = np.gradient(P, axis=0)
    ln = np.hypot(d[:, 0], d[:, 1]) + 1e-9
    nr = np.stack([-d[:, 1] / ln, d[:, 0] / ln], 1)
    core.ribbon(name + "_sett", [tuple(p) for p in P], gauge + 1.3, M["ug_paving"], z0=z0, rut=False, col="Roads")
    for sg in (-1, 1):
        for k, off in enumerate((gauge / 2 - 0.05, gauge / 2 + 0.07)):
            core.ribbon(f"{name}_gv{sg}{k}", [tuple(p + n * sg * off) for p, n in zip(P, nr)], 0.04, M["iron_black"], z0=z0 + 0.0008, rut=False, col="Roads")


def _surface_works(P, ss, pos, ang, nrm, zs, covered, below, half, wt, g, name):
    """開削上部の復旧舗装(継ぎ目・マンホール)、換気塔、坑口の翼壁と門柱、埋戻し土(断面で見える)。"""
    n = len(ss)
    import zlib, random as _rnd
    rv = _rnd.Random(zlib.crc32(name.encode()))
    st_tw = dict(hx=rv.choice([1.4, 1.7, 2.0, 2.3]), hy=rv.choice([1.0, 1.2, 1.5]), hz=rv.choice([3.8, 4.4, 5.2, 6.0]),
                 mat=rv.choice(["ug_brick", "ug_brick", "ug_stone", "ug_tile"]), roof=rv.choice(["flat", "hip", "gable"]),
                 louv=rv.choice([4, 6, 8]), step=rv.choice([36, 45, 60]), type=(__import__('os').environ.get('SUBWAY_TYPE') or rv.choice(['pilaster', 'mushroom', 'slab', 'grate'])))
    st_pt = dict(flare=rv.choice([2.2, 3.2, 4.2]), wl=rv.choice([7.0, 9.0, 11.0]), pw=rv.choice([0.8, 1.0, 1.3]), cap=rv.choice([True, False]))
    cidx = np.where(covered)[0]
    soil = "soil" if "soil" in M else "k5_earth"
    gs = G(name + "_soil", "Props")
    if len(cidx):
        runs = np.split(cidx, np.where(np.diff(cidx) > 1)[0] + 1)
        for k, r in enumerate(runs):
            if len(r) < 3:
                continue
            idx = np.arange(r[0], r[-1] + 1)
            core.ribbon(f"{name}_rest{k}", [tuple(pos[i]) for i in idx], 2 * half + 2 * wt + 3.2, M["ug_asph"], z0=0.03, rut=False, col="Roads")
            for i in idx[::6]:        # 継ぎ目(開削の復旧ライン)
                a = pos[i] + nrm[i] * (half + wt + 1.5)
                b = pos[i] - nrm[i] * (half + wt + 1.5)
                g.a("iron_black").sbox((a[0], a[1], 0.045), (b[0], b[1], 0.045), 0.05, 0.01)
            for i in idx[::15]:       # マンホール
                c = pos[i] + nrm[i] * 1.2
                g.a("iron_black").cyl((c[0], c[1], 0.03), (c[0], c[1], 0.055), 0.32, seg=14)
            # 埋戻し土(土被りの断面表現)
            for sg in (-1, 1):
                for i in idx[:-1:2]:
                    zm = zs[i]
                    p0 = pos[i] + nrm[i] * sg * (half + wt + 2.2)
                    p1 = pos[min(i + 2, n - 1)] + nrm[min(i + 2, n - 1)] * sg * (half + wt + 2.2)
                    gs.a(soil).sbox((p0[0], p0[1], (zm - 0.75 - 0.08) / 2), (p1[0], p1[1], (zm - 0.75 - 0.08) / 2), 3.4, -0.08 - (zm - 0.75))
            # 換気塔(約90m毎・片側ずつ): 駅ごとに型が違う(煉瓦付柱/きのこ型円筒/RC庇付/地表格子ピット)
            for j, i in enumerate(idx[12:-12:st_tw['step']]):
                sg = 1 if j % 2 == 0 else -1
                c = pos[i] + nrm[i] * sg * (half + wt + 5.5)
                _vent_tower(g, c, ang[i], st_tw, sg)
    print('SUBWAY_DBG', name, 'portals', [round(float(ss[i])) for i in range(1, n - 1) if covered[i] != covered[i - 1] and zs[i] < 0.5], 'covered', [round(float(ss[r[0]])) for r in ([np.arange(0)] if not len(cidx) else np.split(cidx, np.where(np.diff(cidx) > 1)[0] + 1))] if len(cidx) else [], 'n', n, flush=True)
    # 坑口: 門柱と翼壁
    for i in range(1, n - 1):
        if covered[i] != covered[i - 1] and zs[i] < 0.5:
            c = pos[i]
            d = np.array([math.cos(ang[i]), math.sin(ang[i])])
            od = -d if covered[i] else d      # 開いている側
            for sg in (-1, 1):
                o = nrm[i] * sg
                q = c + o * (half + wt + 0.3)
                g.a("ug_stone", bevel=0.03).sbox((q[0], q[1], zs[i] - 0.75), (q[0], q[1], 1.9), st_pt['pw'], 1.3)
                e0 = c + o * (half + wt + 0.3) + od * 0.5
                e1 = c + od * st_pt['wl'] + o * (half + wt + 0.3 + st_pt['flare'])
                for k_ in range(3):     # 階段状の擁壁(だんだん低くなる)+笠石+控え壁
                    f0, f1 = k_ / 3.0, (k_ + 1) / 3.0
                    q0 = e0 + (e1 - e0) * f0
                    q1 = e0 + (e1 - e0) * f1
                    top = 2.3 - 0.75 * k_
                    zc = (top - 1.2) / 2
                    g.a("ug_stone", bevel=0.02).sbox((q0[0], q0[1], zc), (q1[0], q1[1], zc), 0.5, top + 1.2)
                    g.a("ug_conc2", bevel=0.02).sbox((q0[0], q0[1], top + 0.06), (q1[0], q1[1], top + 0.06), 0.72, 0.12)
            w = 2 * half + 2 * wt
    gs.build()


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
    M["asphalt"] = M["ug_asph"]
    M["paving"] = M["ug_paving"]
    ss = np.arange(s0, s1 + 0.5, 3.0)
    pos, ang = frames_at(P, ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    pts = [tuple(p) for p in pos]
    zr = 0.243
    core.ribbon(name + "_asph", pts, road_w, M["asphalt"] if "asphalt" in M else M["road"], z0=zr, rut=False, col="Roads")
    tram_bed(pos, name + "_bed")
    for sg in (-1, 1):
        wp = [tuple(p + n * sg * (road_w / 2 + 1.5)) for p, n in zip(pos, nrm)]
        core.ribbon(f"{name}_walk{sg}", wp, 3.0, M["paving"], z0=0.33, rut=False, col="Roads")
    g = G(name + "_fit", "Props")
    for i in range(len(ss) - 1):
        a, b = pos[i], pos[i + 1]
        for sg in (-1, 1):
            c0 = a + nrm[i] * sg * (road_w / 2 + 0.06)
            c1 = b + nrm[i + 1] * sg * (road_w / 2 + 0.06)
            g.a("k5_conc").sbox((c0[0], c0[1], 0.18), (c1[0], c1[1], 0.18), 0.18, 0.36)
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


def shaft_cut(x0, x1, y0, y1, name="shaft", z0=-2.5, z1=2.0):
    """軸平行の箱形の切り欠き型(階段室・換気口など)。ゾーン局所座標。"""
    V = np.array([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], float)
    T = np.array([(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)])
    ob = np_mesh(name, V, T, None, "Cutters")
    _bm_clean(ob)
    ob["is_cutter"] = 1
    ob.hide_render = True
    return ob
