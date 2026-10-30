"""kit5: 線路構造物(橋・トンネル・スノーシェッド・切通し・築堤・こ線橋・踏切・河川)。
入力は世界座標の中心線(N,2)と区間[s0,s1](m)。線路自体は kit4 が敷設し、ここでは周囲の構造物だけを作る(高低差は zfun で共有)。"""
import math, random
import numpy as np
from common import *
import lib, core, trackkit, props, kit2
from props import G
from veg import np_mesh


def frames_at(P, s):
    Q, ss = trackkit.resample(np.asarray(P, float), 1.0)
    pos, ang = trackkit.at_s(Q, np.asarray(s, float))
    return pos, ang


def smooth01(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def make_zfun(profile):
    """profile: [(s0, s1, h, ramp)] 区間[s0,s1]で高さ h(m)、両端 ramp(m) で擦り付け。"""
    def f(s):
        s = np.asarray(s, float)
        z = np.zeros_like(s)
        for (a, b, h, ramp) in profile:
            r0, r1 = ramp if isinstance(ramp, tuple) else (ramp, ramp)
            up = smooth01((s - a) / max(r0, 1e-3))
            dn = smooth01((b - s) / max(r1, 1e-3))
            z = np.maximum(z, h * np.minimum(up, dn)) if h >= 0 else np.minimum(z, h * np.minimum(up, dn))
        return z
    return f


def mats5():
    kit2.mats2()
    if "k5_stone" not in M:
        M["k5_stone"] = lib.mat_plaster("k5_stone", (0.30, 0.285, 0.26), dirt=1.0)
        M["k5_earth"] = lib.mat_plain("k5_earth", (0.12, 0.17, 0.07), rough=1.0)
        M["k5_gravel"] = lib.mat_plain("k5_gravel", (0.30, 0.27, 0.22), rough=1.0)
        M["k5_foam"] = lib.mat_plain("k5_foam", (0.62, 0.66, 0.68), rough=0.95)
        M["k5_conc"] = lib.mat_plaster("k5_conc", (0.52, 0.52, 0.50), dirt=0.8)
        M["k5_steel"] = lib.mat_paint("k5_steel", (0.035, 0.045, 0.05), rough=0.6, rust=0.6)
        M["k5_timber"] = lib.mat_plain("k5_timber", (0.18, 0.13, 0.08), rough=0.9)
    if "ug_conc" not in M:     # 実写PBR(ambientCG CC0): 構造物・地下・舗装用
        M["ug_conc"] = lib.mat_pbr("ug_conc", "Concrete031", scale=2.6, tint=(0.95, 0.93, 0.88), tint_amt=0.3, bump=0.5, macro=0.2, dirt=0.0, spec=0.2)
        M["ug_conc2"] = lib.mat_pbr("ug_conc2", "Concrete048", scale=2.8, bump=0.6, macro=0.2, dirt=0.0, spec=0.2)
        M["k5_conc"] = lib.mat_pbr("k5_conc", "Concrete031", scale=2.2, hsv=(0.5, 0.6, 1.5), tint=(0.95, 0.94, 0.90), tint_amt=0.4, bump=0.7, macro=0.4, dirt=0.5, spec=0.12)   # C17: 無地の漆喰(mat_plaster)だった桁・橋脚を実写PBR+汚れ・斑に
        M["k5_shedwall"] = lib.mat_pbr("k5_shedwall", "Concrete048", scale=1.6, hsv=(0.5, 0.8, 0.8), tint=(0.9, 0.88, 0.82), tint_amt=0.35, bump=0.8, macro=0.4, dirt=0.7, spec=0.1)   # C17: 雪覆い側壁の長大な無地面に汚れ・斑を載せる
        M["ug_asph"] = lib.mat_pbr("ug_asph", "Asphalt032", scale=2.2, hsv=(0.5, 1.0, 0.62), bump=0.7, macro=0.25, spec=0.25)
        M["k5_rock"] = lib.mat_pbr("k5_rock", "Ground110", scale=1.6, tint=(0.62, 0.60, 0.56), tint_amt=0.55, bump=1.0, macro=0.25, spec=0.15)
        M["k5_soil"] = lib.mat_pbr("k5_soil", "Ground110", scale=2.4, tint=(0.34, 0.22, 0.12), tint_amt=0.85, bump=1.2, macro=0.45, spec=0.05)
        M["ug_stone"] = lib.mat_pbr("ug_stone", "Bricks102", scale=1.8, bump=0.9, macro=0.15, spec=0.2)
        def _hill_mask(m):                                       # 頂点カラー(高さ帯)+ノイズで草↔土を滑らかに混ぜる(面ごとの割当だとタイル状にギザギザしていた)
            sx, sy, sz = m.sep(m.attr_color("Col"))
            nz = m.noise(scale=0.07, detail=5, rough=0.6)
            f = m.math('ADD', sx, m.math('MULTIPLY', m.math('SUBTRACT', nz, 0.5), 0.9))
            return m.ramp(f, [(0.42, (0, 0, 0)), (0.58, (1, 1, 1))])
        M["k5_hillsoil"] = lib.mat_pbr_blend("k5_hillsoil", "Grass004", "Ground110", scale_a=1.6, scale_b=2.4, mask=_hill_mask,
                                             tint_a=(0.98, 0.88, 0.48), tint_b=(0.34, 0.22, 0.12), bump=0.8, macro=0.3,
                                             hsv_a=(0.49, 0.62, 0.78), spec=0.0)
        M["k5_pitch"] = lib.mat_pbr("k5_pitch", "Bricks102", scale=3.2, tint=(0.5, 0.46, 0.4), tint_amt=0.7, bump=0.9, macro=0.3, dirt=0.5, spec=0.12)      # 法面の石張り: 擁壁用より小粒で暗く、泥汚れ
        M["ug_brick"] = lib.mat_pbr("ug_brick", "Bricks097", scale=1.4, bump=0.8, macro=0.2, spec=0.25)
        M["ug_tile"] = lib.mat_pbr("ug_tile", "Tiles107", scale=2.4, bump=0.3, macro=0.1, spec=0.5)
        M["ug_floor"] = lib.mat_pbr("ug_floor", "Tiles139", scale=2.4, bump=0.3, macro=0.12, spec=0.4)
        M["ug_paving"] = lib.mat_pbr("ug_paving", "PavingStones070", scale=1.6, bump=0.9, macro=0.12, spec=0.2)
        M["ug_plaster"] = lib.mat_pbr("ug_plaster", "Concrete046", scale=3.0, bump=0.4, macro=0.2, dirt=0.0, spec=0.15)


def river(P, s, width=40.0, length=700.0, name="river", wiggle=22.0, seed=0, flow_dir=None):
    """track の位置 s を横切る川(蛇行する水面の帯)。"""
    mats5()
    pos, ang = frames_at(P, [s])
    c, a = pos[0], float(ang[0]) + math.pi / 2
    d = np.array([math.cos(a), math.sin(a)])
    nrm = np.array([-d[1], d[0]])
    ts = np.linspace(-length / 2, length / 2, 90)
    rng = random.Random(seed)
    ph = rng.uniform(0, 6.28)
    lat = wiggle * np.sin(ts / 120.0 + ph) * smooth01((np.abs(ts) - 30) / 80.0)       # 橋の下は直線
    pts = [tuple(c + d * t + nrm * l) for t, l in zip(ts, lat)]
    core.ribbon(name, pts, width, M["water"], z0=0.05, rut=False, col="Ground")
    # 護岸の縁
    # 岸: 外側に土の帯(湿った泥)、水際に砂利の帯。水面が地面に直線で刺さって見える問題の対策
    core.ribbon(name + "_bank", [tuple(np.array(p) + 0) for p in pts], width + 9.0, M["dirt"], z0=0.034, rut=False, col="Ground")
    core.ribbon(name + "_shore", [tuple(np.array(p) + 0) for p in pts], width + 3.4, M["ballast"], z0=0.042, rut=False, col="Ground")


def truss_bridge(P, s0, s1, name="truss", h=7.5, width=7.0, zfun=None):
    """鉄製ワーレントラス(下路式)。"""
    mats5()
    g = G(name, "Props")
    L = s1 - s0
    nb = max(2, int(L / 14.0))
    ss = np.linspace(s0, s1, nb + 1)
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else zfun(ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    steel = g.a("k5_steel", bevel=0.01)
    zdeck = -0.55
    for k in range(nb + 1):
        zk = zs[k]
        for sgn in (-1, 1):
            p = pos[k] + nrm[k] * sgn * width / 2
            steel.box(p[0] - 0.22, p[0] + 0.22, p[1] - 0.22, p[1] + 0.22, zk + zdeck - 0.9, zk + zdeck + h)
        a, b = pos[k] + nrm[k] * width / 2, pos[k] - nrm[k] * width / 2
        g.a("k5_steel").sbox((a[0], a[1], zk + zdeck), (b[0], b[1], zk + zdeck), 0.3, 0.55)       # 床桁
        tg = np.array([math.cos(ang[k]), math.sin(ang[k])])
        for sgn in (-1, 1):                                                                       # 格点の隅板(ガセット)とリベット列
            pg = pos[k] + nrm[k] * sgn * (width / 2 + 0.2)
            for zz, hh in ((zk + zdeck, 1.35), (zk + zdeck + h, 1.15)):      # Q25/C17: 隅板とリベットが小さく読めなかった(監査)。板を大きく、リベットを密に
                q0, q1 = pg - tg * 1.05, pg + tg * 1.05
                g.a("k5_steel").sbox((q0[0], q0[1], zz), (q1[0], q1[1], zz), 0.06, hh)
                for rv in (-0.8, -0.5, -0.2, 0.1, 0.4, 0.7):
                    for dz in (-0.42, 0.0, 0.42):
                        rp = pg + tg * rv + nrm[k] * sgn * 0.04
                        g.a("k5_steel").sbox((rp[0], rp[1], zz + dz), (rp[0], rp[1], zz + dz + 0.06), 0.1, 0.1)
        g.a("k5_steel").sbox((a[0], a[1], zk + zdeck + h), (b[0], b[1], zk + zdeck + h), 0.25, 0.35)   # 上横構
    for k in range(nb):
        for sgn in (-1, 1):
            p0 = pos[k] + nrm[k] * sgn * width / 2
            p1 = pos[k + 1] + nrm[k + 1] * sgn * width / 2
            z0, z1 = zs[k], zs[k + 1]
            # Q25: 弦材が平らな角材だった。ウェブ+上下フランジ(I形断面)にして、鋼橋の部材らしい断面にする
            for zc, dep in ((zdeck, 0.6), (zdeck + h, 0.5)):                                                      # 下弦 / 上弦
                g.a("k5_steel").sbox((p0[0], p0[1], z0 + zc), (p1[0], p1[1], z1 + zc), 0.07, dep)                  # ウェブ
                for fz in (-dep / 2, dep / 2):
                    g.a("k5_steel").sbox((p0[0], p0[1], z0 + zc + fz), (p1[0], p1[1], z1 + zc + fz), 0.38, 0.07)   # フランジ
            for dn in (-0.09, 0.09):                                                                                # 斜材は二枚板(溝形)+間のレーシング板
                pa0 = p0 + nrm[k] * dn; pa1 = p1 + nrm[k + 1] * dn
                if k % 2 == 0:
                    g.a("k5_steel").sbox((pa0[0], pa0[1], z0 + zdeck), (pa1[0], pa1[1], z1 + zdeck + h), 0.04, 0.3)        # 斜材 /
                else:
                    g.a("k5_steel").sbox((pa0[0], pa0[1], z0 + zdeck + h), (pa1[0], pa1[1], z1 + zdeck), 0.04, 0.3)        # 斜材 \
            for fr in (0.25, 0.5, 0.75):
                pm = p0 + (p1 - p0) * fr
                zm = (z0 + zdeck + (z1 - z0 + h) * fr) if k % 2 == 0 else (z0 + zdeck + h + (z1 - z0 - h) * fr)
                g.a("k5_steel").box(pm[0] - 0.12, pm[0] + 0.12, pm[1] - 0.12, pm[1] + 0.12, zm - 0.03, zm + 0.03)       # レーシング板(目安)
    # 上横構(X字)と端部の橋門構(ポータル)、下横構
    for k in range(nb):
        a0, a1 = pos[k] + nrm[k] * width / 2, pos[k + 1] - nrm[k + 1] * width / 2
        b0, b1 = pos[k] - nrm[k] * width / 2, pos[k + 1] + nrm[k + 1] * width / 2
        zt0, zt1 = zs[k] + zdeck + h - 0.2, zs[k + 1] + zdeck + h - 0.2
        if 0 < k < nb - 1:
            g.a("k5_steel").sbox((a0[0], a0[1], zt0), (a1[0], a1[1], zt1), 0.16, 0.16)
            g.a("k5_steel").sbox((b0[0], b0[1], zt0), (b1[0], b1[1], zt1), 0.16, 0.16)
        zl0, zl1 = zs[k] + zdeck - 0.2, zs[k + 1] + zdeck - 0.2
        g.a("k5_steel").sbox((a0[0], a0[1], zl0), (a1[0], a1[1], zl1), 0.14, 0.14)
        g.a("k5_steel").sbox((b0[0], b0[1], zl0), (b1[0], b1[1], zl1), 0.14, 0.14)
    for k, kk in ((0, 1), (nb, nb - 1)):
        a, b = pos[k] + nrm[k] * width / 2, pos[k] - nrm[k] * width / 2
        zb = zs[k] + zdeck
        for f in (0.62, 0.9):                                          # 橋門構: 梁+隅板
            g.a("k5_steel").sbox((a[0], a[1], zb + h * f), (b[0], b[1], zb + h * f), 0.3, 0.3)
        g.a("k5_steel").sbox((a[0], a[1], zb + h * 0.62), (b[0], b[1], zb + h), 0.18, 0.2)
        g.a("k5_steel").sbox((b[0], b[1], zb + h * 0.62), (a[0], a[1], zb + h), 0.18, 0.2)
        # 橋台(石積み)と支承
        for sgn in (-1, 1):
            p = pos[k] + nrm[k] * sgn * (width / 2)
            g.a("ug_stone", bevel=0.05).box(p[0] - 1.4, p[0] + 1.4, p[1] - 1.4, p[1] + 1.4, -2.5, zb - 0.4)
            g.a("iron_black").box(p[0] - 0.5, p[0] + 0.5, p[1] - 0.5, p[1] + 0.5, zb - 0.5, zb - 0.3)
    # 縦桁・床板
    for sgn in (-0.9, 0.9):
        for k in range(nb):
            p0 = pos[k] + nrm[k] * sgn
            p1 = pos[k + 1] + nrm[k + 1] * sgn
            g.a("k5_steel").sbox((p0[0], p0[1], zs[k] + zdeck + 0.05), (p1[0], p1[1], zs[k + 1] + zdeck + 0.05), 0.35, 0.5)
    # 橋脚(川の中)
    for k in range(1, nb, 2):
        for sgn in (-1, 1):
            p = pos[k] + nrm[k] * sgn * (width / 2 - 0.3)
            g.a("ug_stone", bevel=0.05).box(p[0] - 1.0, p[0] + 1.0, p[1] - 1.0, p[1] + 1.0, -2.5, zs[k] + zdeck - 0.5)
    g.build()


def arch_bridge(P, s0, s1, name="arch", rise=4.0, width=8.0, zfun=None, deck=None):
    """石造アーチ橋: 橋脚+楕円アーチの輪+拱上壁(側壁)+床版+高欄。アーチの下は開口(川が通る)。"""
    mats5()
    g = G(name, "Props")
    L = s1 - s0
    na = max(1, int(round(L / 22.0)))
    span = L / na
    ss = np.linspace(s0, s1, int(L / 2.0) + 2)
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else zfun(ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    zt = zs - 0.35                              # 床版上面
    zdb = zt - 0.9                              # 床版下面
    # 床版+高欄
    for i in range(len(ss) - 1):
        a0, a1 = pos[i], pos[i + 1]
        g.a("k5_conc").sbox((a0[0], a0[1], zt[i] - 0.45), (a1[0], a1[1], zt[i + 1] - 0.45), width - 0.5, 0.9)      # Q25/C17: 床版の側面が白い帯として見えていた(監査)。コンクリートは内側に引き、外面は石積みで覆う
        for sg in (-1, 1):
            p0, p1 = a0 + nrm[i] * sg * (width / 2 - 0.2), a1 + nrm[i + 1] * sg * (width / 2 - 0.2)
            g.a("ug_stone").sbox((p0[0], p0[1], zt[i] - 0.45), (p1[0], p1[1], zt[i + 1] - 0.45), 0.45, 0.9)           # 床版の外面の石積み
            g.a("ug_stone").sbox((p0[0], p0[1], zt[i] + 0.45), (p1[0], p1[1], zt[i + 1] + 0.45), 0.4, 0.9)
            g.a("ug_stone").sbox((p0[0], p0[1], zt[i] + 0.95), (p1[0], p1[1], zt[i + 1] + 0.95), 0.55, 0.14)
            g.a("ug_stone").sbox((p0[0], p0[1], zt[i] - 0.05), (p1[0], p1[1], zt[i + 1] - 0.05), 0.62, 0.16)   # 帯石(コーニス)
            if i % 4 == 0:                                                                                       # 親柱状の束石
                g.a("ug_stone", bevel=0.03).box(p0[0] - 0.3, p0[0] + 0.3, p0[1] - 0.3, p0[1] + 0.3, zt[i] + 0.45, zt[i] + 1.18)
    # アーチ
    for k in range(na):
        sa, sb = s0 + k * span, s0 + (k + 1) * span
        sub = np.linspace(sa + 0.7, sb - 0.7, 121)
        pp, aa = frames_at(P, sub)
        zsub = np.asarray(zfun(sub), float) if zfun is not None else np.zeros(len(sub))
        zz = float(np.mean(zsub))
        zcrown = zz - 0.35 - 0.9 - 0.8 - 0.8      # アーチ内面の頂点
        zspring = zcrown - rise
        u = np.linspace(-1, 1, 121)
        arc = zspring + rise * np.sqrt(np.clip(1 - u ** 2, 0, 1))
        nn = np.stack([-np.sin(aa), np.cos(aa)], 1)
        for i in range(120):
            # アーチ輪(石)
            g.a("ug_stone").sbox((pp[i][0], pp[i][1], arc[i] + 0.4), (pp[i + 1][0], pp[i + 1][1], arc[i + 1] + 0.4), width - 0.1, 0.85)
            # 拱上壁: アーチ輪の上〜床版下面を、両側の外面で埋める
            ztop_w = float((zsub[i] + zsub[i + 1]) / 2 - 0.35 - 0.9)
            for sg in (-1, 1):
                q0 = pp[i] + nn[i] * sg * (width / 2 - 0.3)
                q1 = pp[i + 1] + nn[i + 1] * sg * (width / 2 - 0.3)
                zlo = max(arc[i], arc[i + 1]) + 0.82
                if ztop_w - zlo > 0.05:
                    g.a("ug_stone").sbox((q0[0], q0[1], (zlo + ztop_w) / 2), (q1[0], q1[1], (zlo + ztop_w) / 2), 0.6, ztop_w - zlo)
            # 中詰め(内側の見えない部分は薄く)
        # Q25/C17: 迫石・要石が無く石積みが一様だった(監査)。頂部の要石と、起拱部(橋脚上)の迫り元石を両側の外面へ張り出す
        tgp = np.stack([np.cos(aa), np.sin(aa)], 1)
        for sg in (-1, 1):
            for iu, hh_, ll_ in ((60, 1.15, 1.0), (4, 0.9, 1.1), (116, 0.9, 1.1)):
                qc = pp[iu] + nn[iu] * sg * (width / 2 + 0.06)
                zc_ = arc[iu] + 0.4 + (0.0 if iu == 60 else 0.25)
                g.a("ug_stone", bevel=0.03).sbox((qc[0] - tgp[iu][0] * ll_ / 2, qc[1] - tgp[iu][1] * ll_ / 2, zc_), (qc[0] + tgp[iu][0] * ll_ / 2, qc[1] + tgp[iu][1] * ll_ / 2, zc_), 0.34, hh_)
        # 橋脚(スパン境界)・橋台
        for s_e, abut in ((sa, k == 0), (sb, k == na - 1)):
            pe, ae = frames_at(P, [s_e])
            tn = np.array([math.cos(ae[0]), math.sin(ae[0])])
            nr = np.array([-tn[1], tn[0]])
            zr = float(zfun([s_e])[0]) if zfun is not None else 0.0
            ztop_p = zr - 0.35 - 0.9
            wpier = 1.8 if abut else 1.6
            c0 = pe[0] + (tn * (0.9 if s_e == sa else -0.9)) * (1 if abut else 0)
            g.a("ug_stone", bevel=0.05).sbox((c0[0], c0[1], -1.6), (c0[0], c0[1], ztop_p), wpier * (1.0 if abut else 1.0), width + 0.2) if False else None
            c = pe[0]
            g.a("ug_stone", bevel=0.05).sbox((c[0] - nr[0] * 0, c[1] - nr[1] * 0, -1.6), (c[0], c[1], ztop_p), wpier + (0.6 if abut else 0.0), width + 0.2) if False else None
            # sbox は点間の線分に沿って押し出されるため、橋脚は線分(c-nr*w/2 → c+nr*w/2)の鉛直壁として作る
            a_, b_ = c - nr * (width / 2 + 0.1), c + nr * (width / 2 + 0.1)
            g.a("ug_stone", bevel=0.04).sbox((a_[0], a_[1], (ztop_p - 1.6) / 2), (b_[0], b_[1], (ztop_p - 1.6) / 2), wpier + (0.8 if abut else 0.0), ztop_p + 1.6)
    g.build()


def _boulders(name, pts, seed=1, r0=0.5, r1=1.5):
    """丘の斜面・法尻に置く岩(ゆがめた多面体)。pts は岩の中心の位置 [(x,y,z),...]。1個=緯度5×経度8の頂点、半径と高さをランダムに崩す。"""
    rng = np.random.default_rng(seed)
    V, T = [], []
    nl, nm = 5, 8
    for (x, y, z) in pts:
        r = rng.uniform(r0, r1)
        sx, sy, sz = r * rng.uniform(0.8, 1.3), r * rng.uniform(0.8, 1.3), r * rng.uniform(0.5, 0.85)
        base = len(V)
        V.append((x, y, z - sz * 0.35))
        for a in range(1, nl):
            th = math.pi * a / nl
            for b in range(nm):
                ph = 2 * math.pi * b / nm
                k = rng.uniform(0.78, 1.18)
                V.append((x + sx * k * math.sin(th) * math.cos(ph), y + sy * k * math.sin(th) * math.sin(ph), z - sz * 0.35 + sz * k * math.cos(th)))
        V.append((x, y, z + sz * 0.95))
        top = len(V) - 1
        for b in range(nm):
            b2 = (b + 1) % nm
            T.append((base, base + 1 + b2, base + 1 + b))
            for a in range(nl - 2):
                p0, p1, p2, p3 = base + 1 + a * nm + b, base + 1 + a * nm + b2, base + 1 + (a + 1) * nm + b2, base + 1 + (a + 1) * nm + b
                T += [(p0, p1, p2), (p0, p2, p3)]
            T.append((top, base + 1 + (nl - 2) * nm + b, base + 1 + (nl - 2) * nm + b2))
    if V:
        np_mesh(name, np.array(V), np.array(T), M["k5_rock"], "Ground", smooth=False)


def _plate_png(text):
    """坑口の扁額(石板に刻んだ文字)の画像。tex/ に文字列ごとのファイル名で保存し、あればそれを使う。"""
    import hashlib
    from PIL import Image, ImageDraw, ImageFont
    fn = "tunplate_" + hashlib.md5(text.encode()).hexdigest()[:10] + ".png"
    path = f"{lib.TEX}/{fn}"
    if not os.path.exists(path):
        W, H = 1040, 224
        im = Image.new("RGB", (W, H), (196, 192, 180))
        d = ImageDraw.Draw(im)
        size = 150
        f = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size, index=0)
        while d.textlength(text, font=f) > W - 90 and size > 40:       # 長い名前は枠に収まるまで縮める(L01 は8字以上で右端が切れていた)
            size -= 6
            f = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", size, index=0)
        tw = d.textlength(text, font=f)
        yy = (H - size) // 2 - 4
        d.text(((W - tw) / 2 + 3, yy + 3), text, font=f, fill=(228, 224, 212))      # 彫りの明部
        d.text(((W - tw) / 2, yy), text, font=f, fill=(46, 42, 38))                 # 刻字
        d.rectangle([6, 6, W - 7, H - 7], outline=(88, 84, 76), width=5)
        im.save(path)
    return fn


def tunnel(P, s0, s1, name="tunnel", zfun=None, mound=15.0, half=46.0, inner_w=2.5, inner_h=5.2, plate=None, style=None):
    """覆土トンネル: 外側は盛土の丘、内側はコンクリート覆工(中を歩ける)。坑口に石積みの門。"""
    mats5()
    ss = np.arange(s0, s1 + 0.5, 2.0)
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else zfun(ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    # 外側断面(左地面→頂→右地面)
    uo = np.linspace(-1, 1, (int(2 * half / 2.6) // 2) * 2 + 1)      # 列間隔≈2.6m(坑口の開口判定は列間隔が inner_w 程度に収まることが前提。奇数で中央列を確保)
    hump = lambda u: mound * (1 - abs(u) ** 1.7) ** 1.6
    prof_o = [(half * u, -0.05 + hump(u)) for u in uo]
    # 内側断面(アーチ)
    ui = np.linspace(-1, 1, 13)
    prof_i = [(inner_w * u * 1.0 + 0.0, 0.0 + inner_h * (1 - u ** 2) ** 0.5 if abs(u) < 1 else 0.0) for u in ui]
    prof_i = [(-inner_w, -0.2)] + [(-inner_w * math.cos(t), 2.6 + (inner_h - 2.6) * math.sin(t)) for t in np.linspace(0, math.pi / 2, 7)[1:]] \
        + [(inner_w * math.cos(t), 2.6 + (inner_h - 2.6) * math.sin(t)) for t in np.linspace(math.pi / 2, 0, 7)[:-1]] + [(inner_w, 2.6), (inner_w, -0.2)]
    prof_i = [(-inner_w, -0.2), (-inner_w, 2.6)] + [(-inner_w * math.cos(t), 2.6 + (inner_h - 2.6) * math.sin(t)) for t in np.linspace(0.0, math.pi, 13)[1:-1] if False] \
        + [(inner_w * math.cos(t), 2.6 + (inner_h - 2.6) * math.sin(t)) for t in np.linspace(math.pi, 0, 13)] + [(inner_w, -0.2)]
    prof_i = [(-inner_w, -0.2)] + [(inner_w * math.cos(t), 2.6 + (inner_h - 2.6) * math.sin(t)) for t in np.linspace(math.pi, 0, 13)] + [(inner_w, -0.2)]

    def sweep(prof, mat, nm, flip):
        N, K = len(ss), len(prof)
        V = np.zeros((N, K, 3))
        for k, (off, z) in enumerate(prof):
            V[:, k, 0] = pos[:, 0] + nrm[:, 0] * off
            V[:, k, 1] = pos[:, 1] + nrm[:, 1] * off
            V[:, k, 2] = zs + z
        if not flip:     # 丘: 坑口側は切り立った面(高さ9m)、中央へ向かって盛り上がり、うねりを加える
            L = max(1.0, ss[-1] - ss[0])
            ends = np.minimum((ss - ss[0]) / (0.35 * L), (ss[-1] - ss) / (0.35 * L)).clip(0, 1)
            ends_s = ends * ends * (3 - 2 * ends)
            fe = 0.62 + 0.38 * ends_s
            for k, (off, z) in enumerate(prof):
                edge = 1.0 - abs(off) / half
                # Q25: 端面が幅±46m・高さ9mの垂直な草の壁になっていた。坑口の翼壁の外側(横6m〜)は端へ向かって低く落とし、斜めの法面にする
                lat = float(np.clip((abs(off) - 6.0) / 20.0, 0, 1))
                lat = lat * lat * (3 - 2 * lat)
                fe = (0.62 + 0.38 * ends_s) * (1.0 - lat * (1.0 - ends_s))
                wob = 3.4 * np.sin(0.037 * ss + 2.1 * off / half + 0.8) * np.clip(edge * 2, 0, 1) + 1.5 * np.sin(0.093 * ss + 5.0 * off / half) * np.clip(edge * 2, 0, 1) + 0.7 * np.sin(0.21 * ss + 9.0 * off / half) * np.clip(edge * 3, 0, 1)
                V[:, k, 2] = zs - 0.05 + np.where(z > 0.01, z * fe + wob * (1.0 - lat * (1.0 - ends_s)), 0.0)
        idx = np.arange(N * K).reshape(N, K)
        a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
        T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
        if flip:
            T = T[:, ::-1]
        if flip:
            np_mesh(nm, V.reshape(-1, 3), T, mat, "Ground", smooth=True)
        else:
            # C17: 丘が単色の草だった → 斜面の中腹〜法尻に土肌の帯。高さ帯を頂点カラーに焼き、シェーダで草↔土を滑らかに混ぜる
            hgt = V[:, :, 2].reshape(N, K)
            zr = (hgt - zs[:, None]) / max(1.0, float(hgt.max() - zs.min()))
            kk_ = np.arange(K)[None, :]
            band = np.sin(0.11 * ss[:, None] + 3.0 * kk_ / K) + 0.7 * np.sin(0.29 * ss[:, None] - 2.0 * kk_)
            soil_v = np.clip((0.28 + 0.12 * band - zr) / 0.10, 0.0, 1.0)
            soil_v = np.maximum(soil_v, (zr < 0.05).astype(float))
            cols = np.zeros((N * K, 4), dtype=np.float32)
            cols[:, 0] = soil_v.reshape(-1)
            cols[:, 3] = 1.0
            np_mesh(nm, V.reshape(-1, 3), T, M["k5_hillsoil"], "Ground", smooth=True, colors=cols)
        return V
    Vh = sweep(prof_o, M.get("grass_ground", M["k5_earth"]), name + "_hill", False)
    # 丘の木(杉・雑木)
    try:
        import veg
        from kit2 import SubZone
        rng_t = random.Random(int(s0) + 7)
        N_, K_ = Vh.shape[0], Vh.shape[1]
        for _ in range(int(min(60, (s1 - s0) / 7))):
            i = rng_t.randrange(int(N_ * 0.1), int(N_ * 0.9))
            k = rng_t.randrange(4, K_ - 4)
            p3 = Vh[i, k]
            with SubZone((float(p3[0]), float(p3[1]), float(p3[2]) - 0.3), rng_t.uniform(0, 6.28)):
                veg.sugi(0.0, 0.0, rng_t.uniform(9, 17), seed=rng_t.randrange(10 ** 6))
    except Exception as e:
        print("hill trees failed (skipped)", e)
    # Q25/C17: 丘が単色の草の半球だった(独立監査)。坑口まわりと法尻に岩を散らして土砂・露岩の変化を出す
    try:
        rng_b = random.Random(int(s0) + 11)
        N_, K_ = Vh.shape[0], Vh.shape[1]
        bp = []
        for _ in range(int(26 + min(60, (s1 - s0) / 3))):
            i = rng_b.choice(list(range(0, min(6, N_))) + list(range(max(0, N_ - 6), N_)) + [rng_b.randrange(N_)])
            k = rng_b.randrange(2, K_ - 2)
            if abs(prof_o[k][0]) < inner_w + 4.5 and (i < 6 or i > N_ - 7):
                continue            # 坑口の真上は空けておく
            p3 = Vh[i, k]
            bp.append((float(p3[0]), float(p3[1]), float(p3[2])))
        _boulders(name + "_rocks", bp, seed=int(s0) + 5, r0=0.8, r1=2.6)
    except Exception as e:
        print("hill rocks failed (skipped)", e)
    # 坑口の切り立った面(土の斜面): 丘の断面の下を埋め、トンネル口の部分だけ開ける
    for (i, flipc) in ((0, True), (len(ss) - 1, False)):
        verts, tris = [], []
        K = Vh.shape[1]
        for k in range(K - 1):
            a_, b_ = Vh[i, k], Vh[i, k + 1]
            za0, zb0 = -0.3, -0.3     # Q25: 端面の下端が線路高さ(zs-0.2)で、丘の中空の内部(暗い)が下の隙間から黒い線として見えていた。地面まで下ろす
            oa, ob = abs(prof_o[k][0]), abs(prof_o[k + 1][0])
            if max(oa, ob) <= inner_w + 0.5:        # 開口は坑の幅(列間隔≈2.8m)に収まる列だけ。min で判定すると隣の列まで開いて、門の外側に黒い隙間が出る
                za0 = zb0 = zs[i] + 6.9      # Q25: 開口の上端が門の笠石の上端(7.05)より高い 7.3 で、笠石の背後に黒い隙間(中空の丘の内部)が見えていた。笠石の中に収める
                if max(a_[2], b_[2]) <= za0 + 0.05:
                    continue
            base = len(verts)
            verts += [(a_[0], a_[1], za0), (b_[0], b_[1], zb0), (b_[0], b_[1], max(b_[2], zb0 + 0.01)), (a_[0], a_[1], max(a_[2], za0 + 0.01))]
            tris += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
        if verts:
            T = np.array(tris)
            if flipc:
                T = T[:, ::-1]
            np_mesh(f"{name}_face{i}", np.array(verts), T, M.get("grass_ground", M["k5_earth"]), "Ground", smooth=False)   # 丘の端面は土の斜面(石積みは坑口の門だけ)
    sweep(prof_i, M["k5_conc"], name + "_lining", True)
    # 坑内灯: 両側の側壁の高さ3.0mに10m間隔で発光する灯具(監査指摘「内部が真っ黒で照明が無い」)
    if "tun_lamp" not in M:
        M["tun_lamp"] = lib.mat_emissive("tun_lamp", (1.0, 0.82, 0.50), strength=450.0)
    gl = G(name + "_lamps", "Props")
    for i in range(3, len(ss) - 3, 5):
        for sg in (-1, 1):
            q = pos[i] + nrm[i] * sg * (inner_w - 0.22)
            gl.a("tun_lamp").box(q[0] - 0.14, q[0] + 0.14, q[1] - 0.14, q[1] + 0.14, zs[i] + 2.9, zs[i] + 3.12)
            gl.a("iron_black").box(q[0] - 0.17, q[0] + 0.17, q[1] - 0.17, q[1] + 0.17, zs[i] + 3.12, zs[i] + 3.2)      # 灯具の笠
    gl.build()
    # 坑口: 石積みの門(外周と内周の間を埋める)
    # C17: 3つの坑口が同じ煉瓦門だった(独立監査)。名前のCRCで 0=煉瓦の段状翼壁 / 1=切石積みの低い直線翼壁 / 2=コンクリートの無装飾の袖壁 に決める
    import zlib
    pstyle = zlib.crc32(name.encode()) % 3 if style is None else style
    pm = ("ug_brick", "ug_stone", "ug_conc2")[pstyle]
    wing = (((0.45, 3.0, 5.5), (0.45, 6.0, 4.0), (0.45, 9.0, 2.5)),
            ((0.45, 4.5, 3.6), (0.45, 9.0, 3.6)),
            ((0.45, 3.0, 6.4), (0.45, 6.0, 6.4), (0.45, 9.0, 6.4), (0.45, 12.0, 6.4)))[pstyle]
    g = G(name + "_portal", "Props")
    for (i, sgn) in ((0, -1), (len(ss) - 1, 1)):
        p, n_, z0 = pos[i], nrm[i], zs[i]
        tdir = np.array([math.cos(ang[i]), math.sin(ang[i])])
        # 門柱+まぐさ
        for sg in (-1, 1):
            q = p + n_ * sg * (inner_w + 1.0) - tdir * 0.0
            g.a(pm, bevel=0.03).box(q[0] - 0.9, q[0] + 0.9, q[1] - 0.9, q[1] + 0.9, z0 - 0.2, z0 + 5.8)
        qa = p + n_ * (inner_w + 1.0)
        qb = p - n_ * (inner_w + 1.0)
        g.a(pm, bevel=0.03).sbox((qa[0], qa[1], z0 + 6.0), (qb[0], qb[1], z0 + 6.0), 1.4, 1.2)
        g.a(pm).sbox((qa[0], qa[1], z0 + 6.8), (qb[0], qb[1], z0 + 6.8), 1.0, 0.5)
        # 扁額: 坑口の上に石の銘板(白い石板を門の外面へ少し出す。監査指摘「銘板が無い」)
        pn = p + tdir * sgn * 0.78
        g.a("ug_stone").sbox((pn[0] + n_[0] * 1.5, pn[1] + n_[1] * 1.5, z0 + 6.05), (pn[0] - n_[0] * 1.5, pn[1] - n_[1] * 1.5, z0 + 6.05), 0.14, 0.7)
        # 翼壁: 門柱から外へ開く石積みの擁壁(段状に低くなる)。坑口前の土を押さえる
        outv = tdir * sgn
        for sg in (-1, 1):
            base_pt = p + n_ * sg * (inner_w + 1.9)
            # Q25: 翼壁を outv(坑口の外)へ6.6m張り出すと、丘の端面(垂直)から離れた野原に壁だけが立っていた。端面に沿って横へ段状に下げる(端面の外へ0.45m)
            for j, (du, dv, hh) in enumerate(wing):
                a_ = base_pt + n_ * sg * (wing[j - 1][1] if j else 0.0) + outv * du
                b_ = base_pt + n_ * sg * dv + outv * du
                g.a(pm, bevel=0.02).sbox((a_[0], a_[1], z0 + hh / 2 - 0.2), (b_[0], b_[1], z0 + hh / 2 - 0.2), 0.7, hh)
                g.a(pm).sbox((a_[0], a_[1], z0 + hh - 0.1), (b_[0], b_[1], z0 + hh - 0.1), 0.9, 0.14)   # 笠石
                if pstyle == 2:      # C17: 無装飾のコンクリート袖壁が白一色だった → 3mごとの打継ぎ目地と、壁脚の雨はねの汚れ帯
                    wl = float(np.hypot(*(b_ - a_)))
                    for t_ in np.arange(1.5, wl, 3.0):
                        q_ = a_ + (b_ - a_) * (t_ / wl) + outv * (du + 0.36)
                        g.a("iron_black").sbox((q_[0], q_[1], z0 + hh / 2 - 0.2), (q_[0] + outv[0] * 0.02, q_[1] + outv[1] * 0.02, z0 + hh / 2 - 0.2), 0.05, hh)
                    qa_, qb_ = a_ + outv * (du + 0.36), b_ + outv * (du + 0.36)
                    g.a("ug_asph").sbox((qa_[0], qa_[1], z0 + 0.35), (qb_[0], qb_[1], z0 + 0.35), 0.03, 0.9)
    g.build()
    if plate:      # 扁額の文字(石板の外面に画像を貼る。画像の右方向は坑口を外から見た時の右)
        try:
            fn = _plate_png(plate)
            for (i, sgn) in ((0, -1), (len(ss) - 1, 1)):
                p, n_, z0 = pos[i], nrm[i], zs[i]
                tdir = np.array([math.cos(ang[i]), math.sin(ang[i])])
                outv = tdir * sgn
                right = np.array([-outv[1], outv[0]])
                c = p + outv * 0.78 + outv * 0.085
                zc = z0 + 6.05
                hw, hh = 1.3, 0.28
                cr = [np.append(c - right * hw, zc - hh), np.append(c + right * hw, zc - hh), np.append(c + right * hw, zc + hh), np.append(c - right * hw, zc + hh)]
                lib.image_plane(f"{name}_plate{i}", cr, fn, col="Props")
        except Exception as e:
            print("tunnel plate failed (skipped)", e)


def snowshed(P, s0, s1, name="snowshed", zfun=None, half=4.2, h=6.0, steel=False):
    """スノーシェッド(PC桁式): 山側=控え壁つき擁壁、谷側=柱列(開放)、屋根は山側が高い片流れ。
    6m間隔の門型フレーム、谷側に雪庇受けの張り出し、両端に坑口の垂れ壁と翼壁。"""
    mats5()
    g = G(name, "Props")
    step = 3.0
    ss = np.arange(s0, s1 + 0.5, step)
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else zfun(ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    tan = np.stack([np.cos(ang), np.sin(ang)], 1)
    hm, hv = h + 1.3, h - 0.2           # 山側/谷側の屋根高さ
    for i in range(len(ss) - 1):
        z0, z1 = zs[i], zs[i + 1]
        p0, p1 = pos[i] + nrm[i] * half, pos[i + 1] + nrm[i + 1] * half
        g.a("k5_shedwall").sbox((p0[0], p0[1], z0 + hm / 2), (p1[0], p1[1], z1 + hm / 2), 0.45, hm)      # 山側壁(写真ベースの打放し。Q25/C17: 屋根も壁も無地の白板だった)
        g.a("k5_conc").sbox((p0[0], p0[1], z0 + 0.45), (p1[0], p1[1], z1 + 0.45), 0.85, 0.9)        # 壁の根固め
        # 屋根スラブ(横断勾配: 山側高く谷側低く)。 1区間ごとに傾斜させて並べる
        c = (pos[i] + pos[i + 1]) / 2
        za = (z0 + z1) / 2
        a = c + nrm[i] * (half + 0.2)
        b = c - nrm[i] * (half + 1.4)
        g.a("k5_conc").sbox((a[0], a[1], za + hm + 0.15), (b[0], b[1], za + hv + 0.1), step + 0.05, 0.4)
        # 屋根の目地(伸縮目地の立ち上がり)と雪止めフェンス(鋼管の支柱+2段の横桟)
        ja, jb = c - tan[i] * step / 2 + nrm[i] * (half + 0.2), c - tan[i] * step / 2 - nrm[i] * (half + 1.4)
        g.a("ug_conc2").sbox((ja[0], ja[1], za + hm + 0.4), (jb[0], jb[1], za + hv + 0.35), 0.18, 0.12)
        fe_ = c - nrm[i] * (half + 1.2)
        for tt in (-1.2, 0.0, 1.2):
            fp = fe_ + tan[i] * tt
            g.a("k5_steel").cyl((fp[0], fp[1], za + hv + 0.3), (fp[0], fp[1], za + hv + 1.25), 0.04, seg=6)
        for hh in (0.65, 1.1):
            f0, f1 = fe_ - tan[i] * step / 2, fe_ + tan[i] * step / 2
            g.a("k5_steel").sbox((f0[0], f0[1], za + hv + hh), (f1[0], f1[1], za + hv + hh), 0.05, 0.05)
        # 谷側の雪止め(縁の立ち上がり)
        e = c - nrm[i] * (half + 1.4)
        g.a("k5_conc").sbox((e[0] - tan[i][0] * step / 2, e[1] - tan[i][1] * step / 2, za + hv + 0.45), (e[0] + tan[i][0] * step / 2, e[1] + tan[i][1] * step / 2, za + hv + 0.45), 0.4, 0.4)
        if i % 2 == 0:
            # 門型フレーム: 谷側柱+梁(梁は屋根の下面に見える)
            q = pos[i] - nrm[i] * half
            g.a("k5_conc").sbox((q[0], q[1], z0 - 0.05), (q[0], q[1], z0 + hv - 0.1), 0.55, 0.55)
            g.a("k5_conc").sbox((q[0], q[1], z0 + 0.0), (q[0], q[1], z0 + 0.25), 0.9, 0.9)         # 柱脚
            r0 = pos[i] + nrm[i] * half
            g.a("k5_conc").sbox((r0[0], r0[1], z0 + hm - 0.35), (q[0], q[1], z0 + hv - 0.35), 0.45, 0.5)   # 梁
        if i % 4 == 0:
            # 山側の控え壁(外側へ張り出す)
            r2 = pos[i] + nrm[i] * (half + 0.9)
            g.a("k5_conc").sbox((r2[0], r2[1], z0), (r2[0], r2[1], z0 + hm * 0.62), 0.55, 1.0)
    # 両端の坑口: 垂れ壁・翼壁
    for k, sg in ((0, 1), (len(ss) - 1, -1)):
        o = pos[k] - tan[k] * sg * 0.4
        zk = zs[k]
        for off in (-half, half):
            w = o + nrm[k] * off
            g.a("k5_conc").sbox((w[0], w[1], zk + 1.0), (w[0] - tan[k][0] * sg * 3.0, w[1] - tan[k][1] * sg * 3.0, zk + 0.3), 0.5, 2.0)
        a = o + nrm[k] * half
        b = o - nrm[k] * half
        g.a("k5_conc").sbox((a[0], a[1], zk + hm - 0.3), (b[0], b[1], zk + hv - 0.3), 0.5, 1.1)
    g.build()


def catenary(P, s0, s1, name="cat", zfun=None, side=1, ac=False, span=50.0, posts=True):
    """電車線(架線)柱とトロリ線・ちょう架線・吊架線。
    直流1500V: 鋼管柱+片持ちの腕金(トロリ線高5.2m)。交流20kV: 細い鋼管柱+がい子2連の片持ち、トロリ線5.4m(最新方式=軽量コンパウンド)。"""
    mats5()
    g = G(name, "Props")
    ss = np.arange(s0, s1 + 0.01, span)
    if len(ss) < 2:
        return
    sub = np.arange(s0, s1 + 0.01, 5.0)
    pos, ang = frames_at(P, sub)
    zs = np.zeros(len(sub)) if zfun is None else zfun(sub)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    hc = 5.4 if ac else 5.2
    # 柱
    pp, pa = frames_at(P, ss)
    pz = np.zeros(len(ss)) if zfun is None else zfun(ss)
    pn = np.stack([-np.sin(pa), np.cos(pa)], 1)
    for k in (range(len(ss)) if posts else ()):        # posts=False: 多線区間(ガントリー支持)では柱と腕金を作らず線だけ張る
        q = pp[k] + pn[k] * side * 3.2
        z = pz[k]
        w = 0.22 if ac else 0.32
        g.a("k5_steel", bevel=0.01).sbox((q[0], q[1], z), (q[0], q[1], z + 7.6), w, w)
        g.a("k5_steel").sbox((q[0], q[1], z - 0.05), (q[0], q[1], z + 0.45), w + 0.25, w + 0.25)      # 基礎
        c = pp[k]
        g.a("k5_steel").sbox((q[0], q[1], z + 6.9), (c[0], c[1], z + hc + 1.3), 0.12, 0.14)             # 腕金(上)
        g.a("k5_steel").sbox((q[0], q[1], z + 5.9), (c[0], c[1], z + hc + 0.15), 0.08, 0.1)             # 斜材
        if ac:
            for f in (0.35, 0.7):
                i0 = q + (c - q) * f
                g.a("porcelain").cyl((i0[0], i0[1], z + 6.5 + f * 0.1), (i0[0], i0[1], z + 6.9 + f * 0.2), 0.05, seg=8)
        else:
            g.a("porcelain").cyl((c[0], c[1], z + hc + 0.9), (c[0], c[1], z + hc + 1.25), 0.06, seg=8)
    # 線: トロリ線は千鳥(ジグザグ)、ちょう架線は径間でたるむ
    for k in range(len(sub) - 1):
        stagger0 = 0.22 * (1 if int(sub[k] // span + k * 0) % 2 == 0 else -1)
        a0 = pos[k] + nrm[k] * 0.22 * math.sin(sub[k] * 0.063)
        a1 = pos[k + 1] + nrm[k + 1] * 0.22 * math.sin(sub[k + 1] * 0.063)
        z0, z1 = zs[k] + hc, zs[k + 1] + hc
        g.a("iron_black").sbox((a0[0], a0[1], z0), (a1[0], a1[1], z1), 0.03, 0.03)
        ph = (sub[k] - s0) % span
        sag = 0.45 * (1 - ((ph + 2.5 - span / 2) / (span / 2)) ** 2)
        m0 = pos[k]; m1 = pos[k + 1]
        zm0 = zs[k] + hc + 1.2 - 0.0
        g.a("iron_black").sbox((m0[0], m0[1], zm0 - sag * 0.0), (m1[0], m1[1], zs[k + 1] + hc + 1.2), 0.025, 0.025)
        if k % 2 == 0:
            g.a("iron_black").sbox((a0[0], a0[1], z0), (a0[0], a0[1], zs[k] + hc + 1.2), 0.012, 0.012)  # 吊架線(ドロッパ)
    g.build()


def turnout(P, name="turnout", sig=True):
    """分岐器の表現: 先端レール(トングレール)・クロッシング(ノーズ)・転てつ機(標識つき)・場内信号機(色灯式)。
    P=分岐線の折れ線(始点が本線上)。"""
    mats5()
    Q, s = trackkit.resample(np.asarray(P, float), 1.0)
    if len(Q) < 60:
        return
    t = Q[8] - Q[0]
    t /= np.linalg.norm(t)
    n = np.array([-t[1], t[0]])
    side = 1.0 if float(np.dot(n, Q[45] - Q[0])) >= 0 else -1.0
    g = G(name, "Props")
    p0 = Q[0]
    ng = n * side
    # トングレール(先端レールの尖った部分)
    a = p0 + ng * 0.533
    b = p0 + t * 5.5 + ng * 0.62
    g.a("k5_steel").sbox((a[0], a[1], 0.12), (b[0], b[1], 0.12), 0.07, 0.15)
    a2 = p0 - ng * 0.533
    g.a("k5_steel").sbox((a2[0], a2[1], 0.12), (a2[0] + t[0] * 5.5, a2[1] + t[1] * 5.5, 0.12), 0.07, 0.15)
    for sx in (0.8, 2.6, 4.4):                                            # 床板(スイッチプレート)+連絡棒
        c = p0 + t * sx
        g.a("iron_black").sbox((c[0] - n[0] * 0.9, c[1] - n[1] * 0.9, 0.08), (c[0] + n[0] * 0.9, c[1] + n[1] * 0.9, 0.08), 0.12, 0.05)
    # クロッシング(ノーズ)
    lat = np.array([float(np.dot(ng, q - p0 - t * float(np.dot(t, q - p0)))) for q in Q[:120]])
    i = int(np.argmax(lat >= 1.067)) if (lat >= 1.067).any() else 40
    c = Q[i]
    g.a("k5_steel", bevel=0.01).sbox((c[0] - t[0] * 1.0, c[1] - t[1] * 1.0, 0.13), (c[0] + t[0] * 1.0, c[1] + t[1] * 1.0, 0.13), 0.32, 0.16)
    # 転てつ機: 分岐側の枕木端に置く標識つき転換器
    m = p0 + t * 2.4 + ng * 1.9
    g.a("iron_black").box(m[0] - 0.22, m[0] + 0.22, m[1] - 0.22, m[1] + 0.22, 0.0, 0.55)
    g.a("iron_black").sbox((m[0], m[1], 0.55), (m[0] - ng[0] * 0.5, m[1] - ng[1] * 0.5, 0.95), 0.03, 0.03)
    g.a("post_red").cyl((m[0] - ng[0] * 0.5, m[1] - ng[1] * 0.5, 0.95), (m[0] - ng[0] * 0.5 + 0.0, m[1] - ng[1] * 0.5 + 0.0, 1.0), 0.26, seg=16)
    g.a("white_paint").cyl((m[0], m[1], 0.56), (m[0], m[1], 0.58), 0.12, seg=12)
    if sig:
        # 場内信号機(三現示): 進行方向手前の分岐側に立つ
        q = p0 - t * 45.0 + ng * 3.3
        g.a("white_paint").sbox((q[0], q[1], 0.0), (q[0], q[1], 5.6), 0.16, 0.16)
        g.a("iron_black").sbox((q[0], q[1], 5.45), (q[0] - t[0] * 0.2, q[1] - t[1] * 0.2, 5.5), 0.5, 0.5)
        for j, mat in enumerate(("lamp_glow", "post_red", "iron_black")):
            lc = q - t * 0.5
            g.a(mat).sphere((lc[0], lc[1], 6.15 - j * 0.38), (0.11, 0.11, 0.11), seg=10, rings=5)
        g.a("iron_black").sbox((q[0] - t[0] * 0.18, q[1] - t[1] * 0.18, 5.85), (q[0] - t[0] * 0.18, q[1] - t[1] * 0.18, 6.45), 0.42, 0.95)
    g.build()


def cutting(P, s0, s1, name="cutting", half=4.0, h=5.0, trees=0, seed=0):
    """切通し: 線路の両側に土手(盛り上がり)。"""
    mats5()
    ss = np.arange(s0, s1 + 0.5, 2.0)
    pos, ang = frames_at(P, ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    for sgn, nm in ((-1, "a"), (1, "b")):
        # Q25/C17: 法面が1枚のつるつるの壁だった(監査)。高さの半分に小段(平場)を設けた2段の法面にして、天端から外へなだらかに落とす
        prof = [(sgn * half, -0.05), (sgn * (half + 0.4), h * 0.42), (sgn * (half + 2.0), h * 0.48), (sgn * (half + 3.8), h * 0.5), (sgn * (half + 4.4), h * 0.55),
                (sgn * (half + 6.4), h), (sgn * (half + 9.5), h * 0.92), (sgn * (half + 15.0), -0.05)]
        N, K = len(ss), len(prof)
        V = np.zeros((N, K, 3))
        edge = smooth01((ss - s0) / 40.0) * smooth01((s1 - ss) / 40.0)
        for k, (off, z) in enumerate(prof):
            V[:, k, 0] = pos[:, 0] + nrm[:, 0] * off
            V[:, k, 1] = pos[:, 1] + nrm[:, 1] * off
            V[:, k, 2] = z * edge if z > 0 else z
        idx = np.arange(N * K).reshape(N, K)
        a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
        T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
        if sgn > 0:
            T = T[:, ::-1]
        # C17: 上段の法面は築堤と同じ頂点カラー(草↔土)。侵食溝(上段ほど濃い)と裸地の斑を焼く
        rgc = np.random.default_rng(seed * 17 + int(abs(s0)) % 991 + (5 if sgn > 0 else 1))
        gul = (rgc.random(N) > 0.93).astype(float) * rgc.uniform(0.4, 0.95, N)
        gul = np.convolve(gul, np.array([0.3, 1.0, 0.3]), mode="same").clip(0, 1)
        patch = np.clip((np.sin(0.08 * ss + 0.7 * sgn) * np.sin(0.041 * ss + 1.9) - 0.2) * 3.0, 0, 1)
        soil = np.zeros((N, K))
        soil[:, 4] = np.maximum(0.5 * patch, 0.7 * gul)
        soil[:, 5] = np.maximum(0.35 * patch, 0.95 * gul)
        soil[:, 6] = np.maximum(0.3 * patch[::-1], 0.85 * gul)
        soil[:, 7] = 0.5
        cols_c = np.zeros((N * K, 4), dtype=np.float32)
        cols_c[:, 0] = soil.reshape(-1)
        cols_c[:, 3] = 1.0
        ob_c = np_mesh(f"{name}_{nm}", V.reshape(-1, 3), T, M["k5_hillsoil"], "Ground", smooth=True, colors=cols_c)
        # 切土の法面を材質で分ける(C17監査: 草一色の斜面だった)。線路際の急な面=石張り、小段=土、上段=草
        ob_c.data.materials.append(M["k5_pitch"])
        ob_c.data.materials.append(M["k5_soil"])
        jj = np.tile(np.arange(K - 1), N - 1)
        sel = np.zeros(len(jj), dtype=int)
        sel[jj == 0] = 1
        sel[(jj >= 1) & (jj <= 3)] = 2
        mi_c = np.concatenate([sel, sel])
        if len(ob_c.data.polygons) == len(mi_c):
            ob_c.data.polygons.foreach_set("material_index", mi_c.tolist())
        else:
            print("cutting: 面数が想定と違うため材質分けを付けません(failed)", len(ob_c.data.polygons), len(mi_c))
        # C17: 法面(小段〜上段)に疎な岩の群れ。草一色の壁を崩す
        rg = np.random.default_rng(seed * 31 + (7 if sgn > 0 else 3) + int(abs(s0)) % 997)
        rp = []
        for i in np.where(rg.random(N) > 0.82)[0]:
            if edge[i] < 0.6:
                continue
            for _ in range(int(rg.integers(2, 5))):
                k0 = int(rg.integers(3, 7))
                u = rg.uniform(0.0, 1.0)
                j = min(max(i + int(rg.integers(-2, 3)), 0), N - 1)
                q = V[j, k0] * (1 - u) + V[j, k0 + 1] * u
                rp.append((q[0], q[1], q[2] + 0.05))
        if rp:
            _boulders(f"{name}_{nm}_rocks", rp, seed=seed + (11 if sgn > 0 else 5), r0=0.45, r1=1.4)
    if trees:
        import veg
        rng = random.Random(seed)
        for _ in range(trees):
            i = rng.randrange(len(ss))
            sgn = rng.choice((-1, 1))
            off = sgn * (half + rng.uniform(4, 16))
            p = pos[i] + nrm[i] * off
            try:
                veg.sugi(float(p[0]), float(p[1]), rng.uniform(9, 16))
            except Exception as _e:
                print("sugi failed", _e)


def embankment(P, s0, s1, h=3.0, name="embank", half=4.0, ramp=40.0, zfun=None, holes=()):
    """築堤の法面(線路の高さ zfun と合わせて使う)。
    zfun を渡すと、線路の高さ関数にそのまま追従する盛土になる(橋の取付部など)。holes=[(a,b)] の区間(橋の下)は盛土を地面の高さに落とす。"""
    mats5()
    ss = np.arange(s0, s1 + 0.5, 2.0)
    pos, ang = frames_at(P, ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    if zfun is not None:
        zt = np.asarray(zfun(ss), float).copy()
        for (ha, hb) in holes:
            zt[(ss > ha) & (ss < hb)] = 0.0
    else:
        zt = h * smooth01((ss - s0) / ramp) * smooth01((s1 - ss) / ramp)
    # 法面: 法尻→法面中腹(やや急)→法肩(バラスト肩のすぐ下)。旧: 法肩がバラスト面より0.3m下で、バラストの側面が垂直な灰色の壁に見えていた
    toe = half + h * 1.6 + 1
    prof = [(-toe, 0.0), (-(half + 2.3), 0.78), (-half - 0.6, 0.985), (half + 0.6, 0.985), (half + 2.3, 0.78), (toe, 0.0)]
    N, K = len(ss), 6
    V = np.zeros((N, K, 3))
    for k, (off, f) in enumerate(prof):
        V[:, k, 0] = pos[:, 0] + nrm[:, 0] * (off if f == 0 else off)
        V[:, k, 1] = pos[:, 1] + nrm[:, 1] * (off if f == 0 else off)
        V[:, k, 2] = -0.05 + (zt - 0.08) * f
    idx = np.arange(N * K).reshape(N, K)
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    T = np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])
    # C17: 築堤の法面が単色の草だった(監査・築堤42視点の目視)。法尻の土の帯と、法面の侵食溝・裸地の斑を頂点カラーに焼き、草↔土を滑らかに混ぜる
    rg = np.random.default_rng(int(abs(s0)) % 99991 + 7)
    gul = (rg.random(N) > 0.95).astype(float) * rg.uniform(0.4, 0.9, N)      # 溝はまばらに・濃さも不揃いに
    gul = np.convolve(gul, np.array([0.3, 1.0, 0.3]), mode="same").clip(0, 1)                    # 溝は2〜3列にまたがる
    patch = np.clip((np.sin(0.09 * ss + 1.1) * np.sin(0.037 * ss + 2.3) - 0.25) * 3.0, 0, 1)      # 裸地の斑
    soil = np.zeros((N, K))
    soil[:, 0] = soil[:, K - 1] = 0.5 * (0.6 + 0.4 * patch)                                         # 法尻(濃淡あり)
    soil[:, 1] = np.maximum(0.45 * patch, 0.9 * gul)
    soil[:, K - 2] = np.maximum(0.45 * patch[::-1], 0.9 * gul)
    soil[:, 2] = soil[:, K - 3] = 0.8 * gul
    cols = np.zeros((N * K, 4), dtype=np.float32)
    cols[:, 0] = soil.reshape(-1)
    cols[:, 3] = 1.0
    np_mesh(name, V.reshape(-1, 3), T, M["k5_hillsoil"], "Ground", smooth=True, colors=cols)
    # C17: 法面の石(法尻〜中腹に疎な群れ)。盛土が低い所(zt<0.8)には置かない
    rp = []
    for i in np.where(rg.random(N) > 0.965)[0]:
        if zt[i] < 0.8 or i < 3 or i > N - 4:
            continue
        sd = 1 if rg.random() < 0.5 else -1
        k = 0 if sd < 0 else K - 1
        k2 = 1 if sd < 0 else K - 2
        for _ in range(int(rg.integers(2, 5))):
            u = rg.uniform(0.0, 0.7)
            j = min(max(i + int(rg.integers(-2, 3)), 0), N - 1)
            q = V[j, k] * (1 - u) + V[j, k2] * u
            rp.append((q[0], q[1], q[2] + 0.05))
    if rp:
        _boulders(name + "_rocks", rp, seed=int(abs(s0)) % 9973 + 3, r0=0.25, r1=0.7)


import os as _os_dbg
DOUBLE_SIDED_DBG = _os_dbg.environ.get('BANK_DOUBLE') == '1'     # 検証用: 盛土を両面にして、裏面から見たときの黒面かを切り分ける


def overbridge(P, s, name="overbridge", span=15.0, road_w=6.0, zh=6.2):
    """こ線橋: 道路が線路を直角にまたぐ(コンクリート橋台+鉄桁、両側に坂道)。"""
    mats5()
    pos, ang = frames_at(P, [s])
    c, a = pos[0], float(ang[0])
    t = np.array([math.cos(a), math.sin(a)])
    n = np.array([-t[1], t[0]])
    g = G(name, "Props")
    # 橋本体(道路は n 方向)
    for sg in (-1, 1):
        p = c + n * sg * (span / 2 + 1.0)
        g.a("k5_conc", bevel=0.05).box(p[0] - road_w / 2, p[0] + road_w / 2, p[1] - road_w / 2, p[1] + road_w / 2, -0.2, zh - 0.6) if False else None
    # 軸が斜めでも作れるよう sbox で組む。桁・床版は橋台の間(±(span/2+0.9))だけ。盛土部分には伸ばさない(盛土面より上に突き出していた)
    L2 = span / 2 + 0.9
    a0, a1 = c - n * L2, c + n * L2
    g.a("k5_conc").sbox((a0[0], a0[1], zh - 0.12), (a1[0], a1[1], zh - 0.12), road_w + 0.9, 0.24)          # RC床版
    g.a("ug_asph").sbox((a0[0], a0[1], zh + 0.02), (a1[0], a1[1], zh + 0.02), road_w, 0.1)   # 舗装(アスファルト)
    gx = road_w / 2 - 0.15
    for sg in (-1, 1):                                                                                      # 鋼板桁(腹板+上下フランジ)×2
        q0, q1 = a0 + t * sg * gx, a1 + t * sg * gx
        g.a("k5_steel").sbox((q0[0], q0[1], zh - 0.95), (q1[0], q1[1], zh - 0.95), 0.1, 1.15)
        g.a("k5_steel").sbox((q0[0], q0[1], zh - 0.36), (q1[0], q1[1], zh - 0.36), 0.52, 0.09)
        g.a("k5_steel").sbox((q0[0], q0[1], zh - 1.5), (q1[0], q1[1], zh - 1.5), 0.52, 0.1)
        for k in range(1, int(2 * L2 / 1.8)):                                                             # 垂直補剛材
            qq = a0 + (a1 - a0) * (k * 1.8 / (2 * L2)) + t * sg * (gx + (0.07 if sg > 0 else -0.07))
            g.a("k5_steel").box(qq[0] - 0.04, qq[0] + 0.04, qq[1] - 0.04, qq[1] + 0.04, zh - 1.45, zh - 0.4)
    for k in range(1, int(2 * L2 / 3.0)):                                                                  # 横桁(対傾構)
        qa = a0 + (a1 - a0) * (k * 3.0 / (2 * L2))
        e0, e1 = qa - t * gx, qa + t * gx
        g.a("k5_steel").sbox((e0[0], e0[1], zh - 1.4), (e1[0], e1[1], zh - 1.4), 0.1, 0.14)
        g.a("k5_steel").sbox((e0[0], e0[1], zh - 1.4), (e1[0], e1[1], zh - 0.45), 0.06, 0.06)
    for sg in (-1, 1):                                                                                      # 縁石+パイプ高欄(上桟・中桟・支柱)
        p0 = a0 + t * sg * (road_w / 2 + 0.3)
        p1 = a1 + t * sg * (road_w / 2 + 0.3)
        g.a("k5_conc").sbox((p0[0], p0[1], zh + 0.12), (p1[0], p1[1], zh + 0.12), 0.34, 0.3)
        for hh, ww in ((1.05, 0.07), (0.62, 0.05)):
            g.a("k5_steel").sbox((p0[0], p0[1], zh + hh + 0.12), (p1[0], p1[1], zh + hh + 0.12), ww, ww)
        for q in np.linspace(0, 1, int(2 * L2 / 1.4) + 1):
            pq = p0 + (p1 - p0) * q
            g.a("k5_steel").box(pq[0] - 0.05, pq[0] + 0.05, pq[1] - 0.05, pq[1] + 0.05, zh + 0.25, zh + 1.15)
    for sg in (-1, 1):                                                                                      # 橋台(石積みの胸壁。盛土が両側を抱くので翼壁は別に立てない)
        p = c + n * sg * (span / 2 + 0.8)
        g.a("ug_conc2", bevel=0.05).sbox((p[0], p[1], -0.2), (p[0], p[1], zh - 0.9), road_w + 1.0, 1.6)
    g.build()
    # 取付道路(盛土の坂): 断面は台形(法面勾配 1:1.8)の滑らかなメッシュ。縦壁の箱を段々に積まない
    for sg in (-1, 1):
        p0 = c + n * sg * (span / 2 + 0.8)
        p1 = c + n * sg * (span / 2 + 6.0 + 28.0)
        us = np.linspace(0, 1, 18)
        VB, VR = [], []
        for u in us:
            q = p0 + (p1 - p0) * u
            h = zh * (1 - u)
            hh_ = max(h, 0.0)
            hb_, bw_ = hh_ * 0.5, min(1.2, 0.5 * hh_)                 # Q25/C17: 法面が1枚の斜面だった(監査)。高さの半分に小段(幅最大1.2m)を設けて2段にする
            sh_ = road_w / 2 + 0.5
            for off, z in ((-(sh_ + 1.8 * (hh_ - hb_) + bw_ + 1.8 * hb_), -0.05), (-(sh_ + 1.8 * (hh_ - hb_) + bw_), hb_), (-(sh_ + 1.8 * (hh_ - hb_)), hb_), (-sh_, h - 0.12),
                           (sh_, h - 0.12), (sh_ + 1.8 * (hh_ - hb_), hb_), (sh_ + 1.8 * (hh_ - hb_) + bw_, hb_), (sh_ + 1.8 * (hh_ - hb_) + bw_ + 1.8 * hb_, -0.05)):
                VB.append((q[0] + t[0] * off, q[1] + t[1] * off, max(z, -0.05)))
            for off in (-road_w / 2, road_w / 2):
                VR.append((q[0] + t[0] * off, q[1] + t[1] * off, h + 0.02))
        def strip(V, k):
            T = []
            Va = np.asarray(V, float)
            for i in range(len(us) - 1):
                for j in range(k - 1):
                    a_, b_, c_, d_ = i * k + j, (i + 1) * k + j, (i + 1) * k + j + 1, i * k + j + 1
                    for tri in ((a_, b_, c_), (a_, c_, d_)):
                        nz = np.cross(Va[tri[1]] - Va[tri[0]], Va[tri[2]] - Va[tri[0]])[2]
                        T.append(tri if nz >= 0 else (tri[0], tri[2], tri[1]))     # 法線を上向きにそろえる(左右で巻き方向が逆になり、片側が黒くなっていた)
            T = np.array(T)
            return np.concatenate([T, T[:, ::-1]]) if DOUBLE_SIDED_DBG else T
        # 橋台側の端(u=0)に蓋をして盛土を閉じる。蓋が無いと、開いた断面から盛土の内側に視線が入り、斜面を裏側から見て真っ黒になる(裏面はシェーディング法線が反転する)
        # 蓋は盛土の材質(草)ではなく擁壁のコンクリート面にする。草の材質だと、橋の脇から見える盛土の端面が地面から浮いた逆三角の草の板に見えていた(C17監査の最優先指摘)
        Va = np.asarray(VB, float)
        ob_b = np_mesh(f"{name}_bank{sg}", Va, strip(VB, 8), M.get("grass_ground", M["k5_earth"]), "Ground", smooth=False)
        # 法面の下半分(地面〜小段)は石張りにして、草一色の斜面の単調さをなくす(C17監査)。断面の区間0と6が下段の法面
        ob_b.data.materials.append(M["k5_pitch"])
        nseg = len(us) - 1
        mi_ = np.zeros(nseg * 7 * 2, dtype=int)
        for i_ in range(nseg):
            for j_ in (0, 6):
                mi_[(i_ * 7 + j_) * 2:(i_ * 7 + j_) * 2 + 2] = 1
        if len(ob_b.data.polygons) == len(mi_):
            ob_b.data.polygons.foreach_set("material_index", mi_.tolist())
        else:
            print("overbridge bank: 面数が想定と違うため石張りを付けません(failed)", len(ob_b.data.polygons), len(mi_))
        face_dir = -sg * n                                  # 蓋の外向き=橋の中心側
        cv = Va[:8].copy()
        cap = []
        for j in range(1, 7):
            nn = np.cross(cv[j] - cv[0], cv[j + 1] - cv[0])
            cap.append([0, j, j + 1] if (nn[0] * face_dir[0] + nn[1] * face_dir[1]) >= 0 else [0, j + 1, j])
        np_mesh(f"{name}_bankwall{sg}", cv, np.array(cap), M["ug_conc2"], "Ground", smooth=False)
        # 擁壁の面に型枠の打継ぎ目(1.5mごとの水平線)と、足元の泥はね帯を付ける。無地の1枚板だった(C17監査)
        pc = c + n * sg * (span / 2 + 0.8)
        offs = np.array([(v[0] - pc[0]) * t[0] + (v[1] - pc[1]) * t[1] for v in cv])
        zs_ = cv[:, 2]
        oi = np.argsort(offs)
        xs_ = np.linspace(offs.min(), offs.max(), 200)
        hs_ = np.interp(xs_, offs[oi], zs_[oi])
        gj = G(f"{name}_bwjoint{sg}", "Props")
        for zj in np.arange(1.5, zh, 1.5):
            ok_ = xs_[hs_ > zj + 0.05]
            if len(ok_) < 2:
                continue
            q0 = pc + t * ok_[0] + face_dir * 0.03
            q1 = pc + t * ok_[-1] + face_dir * 0.03
            gj.a("iron_black").sbox((q0[0], q0[1], zj), (q1[0], q1[1], zj), 0.04, 0.05)
        q0 = pc + t * offs.min() + face_dir * 0.03
        q1 = pc + t * offs.max() + face_dir * 0.03
        gj.a("ug_asph").sbox((q0[0], q0[1], 0.3), (q1[0], q1[1], 0.3), 0.03, 0.6)
        gj.build()
        np_mesh(f"{name}_road{sg}", np.array(VR), strip(VR, 2), M["ug_asph"], "Ground", smooth=False)


def level_crossing(P, s, name="lc", road_w=4.6):
    """踏切: 道路を線路に直角に横断(板張り+遮断機+警報機)。"""
    mats5()
    pos, ang = frames_at(P, [s])
    c, a = pos[0], float(ang[0])
    t = np.array([math.cos(a), math.sin(a)])
    n = np.array([-t[1], t[0]])
    pts = [tuple(c + n * u) for u in (-120, -40, 0, 40, 120)]
    asph = M["ug_asph"]          # 写真ベースのアスファルト(旧: M["asphalt"] は未定義で、砂色の土の道になっていた)
    # C17: 道路が幅の狭い灰色の帯で路肩も区画線も無く、20か所すべて同一の意匠だった(踏切20視点の目視)。名前から決まる変化(幅・遮断機の有無・路肩)と路肩・中央線を足す
    var = sum(ord(ch) for ch in name) % 6
    road_w = road_w * (0.8, 1.0, 1.15, 0.9, 1.3, 1.0)[var]
    has_gate = var % 3 != 0                                  # 第3種(遮断機なし・警報機のみ)を混ぜる
    core.ribbon(name + "_shoulder", pts, road_w + 2.6, M["k5_gravel"], z0=0.008, rut=False)          # 砂利の路肩
    core.ribbon(name + "_road", pts, road_w, asph, z0=0.016, rut=False)
    g = G(name, "Props")
    if road_w >= 4.4:
        for sn in (-1, 1):                                    # 中央線(踏切の手前だけ・破線)
            for k in range(10):
                d0 = 11.0 + k * 3.0
                a0, a1 = c + n * sn * d0, c + n * sn * (d0 + 1.6)
                g.a("white_paint").sbox((a0[0], a0[1], 0.03), (a1[0], a1[1], 0.03), 0.12, 0.02)
    g.a("k5_timber").sbox((c[0] - n[0] * 2.4, c[1] - n[1] * 2.4, 0.12), (c[0] + n[0] * 2.4, c[1] + n[1] * 2.4, 0.12), road_w, 0.14)
    # 踏切の舗装(道路は n 方向、幅は t 方向): 板張りの外側にコンクリート踏板、道路の縁に縁石、路面に停止線
    for sn in (-1, 1):
        e0, e1 = c + n * sn * 2.4, c + n * sn * 3.9
        g.a("k5_conc").sbox((e0[0], e0[1], 0.06), (e1[0], e1[1], 0.06), road_w, 0.12)         # 端部の踏板
        for st in (-1, 1):
            k0 = c + t * st * (road_w / 2 + 0.12) + n * sn * 2.4
            k1 = c + t * st * (road_w / 2 + 0.12) + n * sn * 9.0
            g.a("k5_stone").sbox((k0[0], k0[1], 0.12), (k1[0], k1[1], 0.12), 0.22, 0.24)       # 縁石
        sa, sb = c + n * sn * 6.0 - t * (road_w / 2 - 0.25), c + n * sn * 6.0 + t * (road_w / 2 - 0.25)
        g.a("white_paint").sbox((sa[0], sa[1], 0.03), (sb[0], sb[1], 0.03), 0.3, 0.02)         # 停止線
    for sg in (-1, 1):
        for tt in (-1, 1):
            p = c + t * sg * (road_w / 2 + 0.9) + n * tt * 3.3
            g.a("iron_black").cyl((p[0], p[1], 0.0), (p[0], p[1], 3.3), 0.055, seg=8)
            face = -n * tt                                    # 標識面は道路の接近側(線路から離れる向き)ではなく道路側へ向ける
            # 踏切警標(X字の十字板): 白地の板2枚を交差させる
            for k in (-1, 1):
                u0 = p + t * 0.55 * k + face * 0.0
                u1 = p - t * 0.55 * k
                g.a("white_paint").sbox((u0[0], u0[1], 2.95 + 0.30 * k), (u1[0], u1[1], 2.95 - 0.30 * k), 0.11, 0.025)
            # 警報灯2灯(赤)を横木に並べる
            bar0, bar1 = p - t * 0.45 + face * 0.08, p + t * 0.45 + face * 0.08
            g.a("iron_black").sbox((bar0[0], bar0[1], 2.45), (bar1[0], bar1[1], 2.45), 0.05, 0.05)
            for k in (-1, 1):
                q = p + t * 0.4 * k + face * 0.12
                g.a("post_red").cyl((q[0], q[1], 2.36), (q[0] + face[0] * 0.06, q[1] + face[1] * 0.06, 2.36), 0.15, seg=14)
            # 遮断機の機械箱と、紅白縞の遮断竿(下りた状態で道路を横切る)
            g.a("iron_black").box(p[0] - 0.18, p[0] + 0.18, p[1] - 0.18, p[1] + 0.18, 0.0, 0.9)
            tip = p - t * sg * (road_w / 2 + 0.25)
            for j in range(8 if has_gate else 0):
                f0, f1 = j / 8.0, (j + 1) / 8.0
                m0 = (p[0] + (tip[0] - p[0]) * f0, p[1] + (tip[1] - p[1]) * f0)
                m1 = (p[0] + (tip[0] - p[0]) * f1, p[1] + (tip[1] - p[1]) * f1)
                g.a("post_red" if j % 2 else "white_paint").sbox((m0[0], m0[1], 1.0), (m1[0], m1[1], 1.0), 0.07, 0.10)
    g.build()


def trestle(P, s0, s1, name="trestle", width=3.4, zfun=None):
    """木橋(トレッスル)。"""
    mats5()
    g = G(name, "Props")
    ss = np.arange(s0, s1 + 0.5, 3.0)
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else zfun(ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    for i in range(len(ss)):
        for sg in (-1, 1):
            p = pos[i] + nrm[i] * sg * width / 2
            g.a("k5_timber", bevel=0.01).box(p[0] - 0.22, p[0] + 0.22, p[1] - 0.22, p[1] + 0.22, -2.0, zs[i] - 0.3)
        a, b = pos[i] + nrm[i] * width / 2, pos[i] - nrm[i] * width / 2
        g.a("k5_timber").sbox((a[0], a[1], zs[i] - 0.4), (b[0], b[1], zs[i] - 0.4), 0.3, 0.3)
        if i % 2 == 0:
            g.a("k5_timber").sbox((a[0], a[1], zs[i] - 1.8), (b[0], b[1], zs[i] - 0.5), 0.1, 0.12)
        for sg in (-1, 1):      # Q25: 手すりに支柱が無く細い線だけが浮いて見えていた
            q = pos[i] + nrm[i] * sg * (width / 2 + 0.25)
            g.a("k5_timber").box(q[0] - 0.06, q[0] + 0.06, q[1] - 0.06, q[1] + 0.06, zs[i] - 0.3, zs[i] + 0.78)
    for i in range(len(ss) - 1):
        for sg in (-1, 0, 1):
            p0 = pos[i] + nrm[i] * sg * 1.0
            p1 = pos[i + 1] + nrm[i + 1] * sg * 1.0
            g.a("k5_timber").sbox((p0[0], p0[1], zs[i] - 0.3), (p1[0], p1[1], zs[i + 1] - 0.3), 0.3, 0.3)
        for sg in (-1, 1):
            p0 = pos[i] + nrm[i] * sg * (width / 2 + 0.25)
            p1 = pos[i + 1] + nrm[i + 1] * sg * (width / 2 + 0.25)
            g.a("k5_timber").sbox((p0[0], p0[1], zs[i] + 0.7), (p1[0], p1[1], zs[i + 1] + 0.7), 0.08, 0.1)
    g.build()


def viaduct(P, s0, s1, name="viaduct", width=8.4, zfun=None, span=12.0):
    """RC高架橋(ラーメン高架): 橋脚+梁+床版+防音壁。新線用。"""
    mats5()
    g = G(name, "Props")
    ss = np.arange(s0, s1 + 0.5, span)
    if ss[-1] < s1 - 0.5:
        ss = np.r_[ss, s1]
    pos, ang = frames_at(P, ss)
    zs = np.zeros(len(ss)) if zfun is None else zfun(ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    tng = np.stack([np.cos(ang), np.sin(ang)], 1)
    for i in range(len(ss)):
        top = zs[i] - 0.9
        if top > 1.0:
            for sg in (-1, 1):
                p = pos[i] + nrm[i] * sg * width * 0.27
                g.a("k5_conc", bevel=0.05).boxc(p[0], p[1], top / 2 - 0.3, 1.1, 1.1, top + 0.6, rz=float(ang[i]))
            a, b = pos[i] + nrm[i] * width * 0.5, pos[i] - nrm[i] * width * 0.5
            g.a("k5_conc", bevel=0.04).sbox((a[0], a[1], top + 0.1), (b[0], b[1], top + 0.1), 1.2, 0.7)
    for i in range(len(ss) - 1):
        a0, a1 = pos[i], pos[i + 1]
        g.a("k5_conc").sbox((a0[0], a0[1], zs[i] - 0.55), (a1[0], a1[1], zs[i + 1] - 0.55), width, 0.5)
        for sg in (-1, 1):
            p0, p1 = a0 + nrm[i] * sg * width / 2, a1 + nrm[i + 1] * sg * width / 2
            g.a("k5_conc").sbox((p0[0], p0[1], zs[i] + 0.1), (p1[0], p1[1], zs[i + 1] + 0.1), 0.3, 1.1)
            g.a("k5_steel").sbox((p0[0], p0[1], zs[i] + 1.15), (p1[0], p1[1], zs[i + 1] + 1.15), 0.08, 0.5)
    # C17: 桁の両端が草地から板のように立ち上がっていた(高架桁橋7視点の目視)。橋台の背面壁と段状の翼壁を付ける
    for e, outward in ((0, -1.0), (len(ss) - 1, 1.0)):
        o = tng[e] * outward
        hb = max(zs[e], 0.0) + 0.5
        b0, b1 = pos[e] - nrm[e] * (width / 2 + 0.5), pos[e] + nrm[e] * (width / 2 + 0.5)
        g.a("k5_conc").sbox((b0[0], b0[1], hb / 2 - 0.3), (b1[0], b1[1], hb / 2 - 0.3), 0.7, hb + 0.6)      # 橋台背面壁
        for sg in (-1, 1):
            for k in range(4):                                                                              # 翼壁(沖へ段状に低くなる)
                q0 = pos[e] + nrm[e] * sg * (width / 2 + 0.4) + o * (1.5 * k)
                q1 = q0 + o * 1.5
                hk = max(hb * (1.0 - 0.22 * k), 0.4)
                g.a("k5_conc").sbox((q0[0], q0[1], hk / 2 - 0.3), (q1[0], q1[1], hk / 2 - 0.3), 0.35, hk + 0.6)
    g.build()


def _tetrapod(g, x, y, z, rz, sc=1.0, leg=0.95, r0=0.42, r1=0.26):
    """テトラポッド: 中心から正四面体の4方向へ円錐台の脚。rz は鉛直軸まわりの回転。"""
    c, sn = math.cos(rz), math.sin(rz)
    for (dx, dy, dz) in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)):
        d = np.array([dx, dy, dz], float) / math.sqrt(3.0)
        d = np.array([d[0] * c - d[1] * sn, d[0] * sn + d[1] * c, d[2]])
        p1 = np.array([x, y, z]) + d * leg * sc
        g.a("k5_conc", bevel=0.0).cyl((x, y, z), tuple(p1), r0 * sc, r1 * sc, seg=8, caps=True)


def seawall(P, s0, s1, side=1, name="seawall", h=2.0):
    """防波堤・護岸: 線路の海側にコンクリート壁と消波ブロック。"""
    mats5()
    g = G(name, "Props")
    ss = np.arange(s0, s1 + 0.5, 3.0)
    pos, ang = frames_at(P, ss)
    nrm = np.stack([-np.sin(ang), np.cos(ang)], 1)
    rng = random.Random(3)
    for i in range(len(ss) - 1):
        p0, p1 = pos[i] + nrm[i] * side * 7.0, pos[i + 1] + nrm[i + 1] * side * 7.0
        g.a("k5_conc").sbox((p0[0], p0[1], h / 2 - 0.2), (p1[0], p1[1], h / 2 - 0.2), 1.0, h + 0.4)
        w0, w1 = pos[i] + nrm[i] * side * 7.55, pos[i + 1] + nrm[i + 1] * side * 7.55
        g.a("k5_conc").sbox((w0[0], w0[1], h + 0.05), (w1[0], w1[1], h + 0.05), 0.3, 0.7)           # Q25/C17: 波返し(海側へ張り出す立ち上がり)。護岸が白い箱だった(監査)
        for j in range(4):
            # 乱積み: 沖側ほど低く、位置を散らして2〜3層(下層は広く、上層は壁寄り)。捨石を足元に敷く
            off = 9.0 + 1.7 * j + rng.uniform(-0.5, 0.5)
            q = pos[i] + nrm[i] * side * off + (pos[i + 1] - pos[i]) * rng.uniform(-0.3, 0.3)
            zq = 0.62 + (0.55 if j == 0 and rng.random() < 0.6 else 0.0)       # 壁寄りは一段積む
            _tetrapod(g, q[0], q[1], zq, rng.uniform(0, 6.28), rng.uniform(0.85, 1.2))      # Q25: 消波ブロックが立方体だった。テトラポッド(4脚)にする
        for _ in range(3):
            q = pos[i] + nrm[i] * side * rng.uniform(7.9, 14.5) + (pos[i + 1] - pos[i]) * rng.uniform(-0.4, 0.4)
            g.a("k5_stone", bevel=0.05).boxc(q[0], q[1], 0.12, rng.uniform(0.5, 1.1), rng.uniform(0.5, 1.1), rng.uniform(0.3, 0.6), rz=rng.uniform(0, 3.0))   # 捨石
    g.build()
    # 海面
    # C17: 幅70mの帯だと沖側の直線の縁が草地に露出し「青い長方形」に見えた(海28視点の目視)ため、水平線まで届く幅500mの帯にする。
    # 試行の記録: ①70m帯+大水面を重ねる/別高さで重ねる→透過水面が二重になり真っ黒 ②扇状メッシュ→区間外に黒い穴 ③70m帯と大水面を隣接→曲線で楔形の隙間。
    # 500m帯は曲線の内側で自己交差して遠景に細い暗い筋が出るが、他案より破綻が少ない(未達: 筋の除去)。
    # 護岸の足元に泡の帯(不透明・水面より少し上。透過する水面と重ねない)。監査で「汀線・泡が無い」(水面系で最低点)
    fpts = [tuple(p + n * side * 8.6) for p, n in zip(pos[::3], nrm[::3])]
    core.ribbon(name + "_foam", fpts, 1.6, M["k5_foam"], z0=0.045, rut=False, col="Ground")
    sea_w = 500.0
    ss_sea = np.arange(s0 - 120.0, s1 + 120.5, 9.0)
    pos_s, ang_s = frames_at(P, ss_sea)
    nrm_s = np.stack([-np.sin(ang_s), np.cos(ang_s)], 1)
    pts = [tuple(p + n * side * (5.0 + sea_w / 2)) for p, n in zip(pos_s, nrm_s)]
    core.ribbon(name + "_sea", pts, sea_w, M["water"], z0=0.03, rut=False, col="Ground")


def gantry(x, y0, y1, z, hc=5.2, name="gantry", w=0.34):
    """多線区間の門形ビーム(ヘッドスパン代わりの鋼製ガントリー): y0〜y1 を跨ぎ、両端に鋼管柱。トロリ線高 hc の上に梁を渡す。"""
    mats5()
    g = G(name, "Props")
    top = z + hc + 2.0
    for yy in (y0, y1):
        g.a("k5_steel", bevel=0.01).sbox((x, yy, z), (x, yy, top + 0.3), w, w)
        g.a("k5_steel").sbox((x, yy, z - 0.05), (x, yy, z + 0.45), w + 0.3, w + 0.3)          # 基礎
    g.a("k5_steel").sbox((x, y0, top), (x, y1, top), 0.22, 0.30)                              # 上弦梁
    g.a("k5_steel").sbox((x, y0, top - 0.9), (x, y1, top - 0.9), 0.12, 0.12)                  # 下弦
    n = max(2, int((y1 - y0) / 3.0))
    for k in range(n + 1):                                                                    # ラチス斜材
        ya = y0 + (y1 - y0) * k / n
        g.a("k5_steel").sbox((x, ya, top - 0.9), (x, ya, top), 0.06, 0.06)
    g.build()
