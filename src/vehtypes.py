"""形式別の電車ビルダー(F3): 実車の設計(車体断面・窓割・前面・屋根上機器・台車・内装)を参考にした汎用形。
実在の社名・標章・番号は使わない。各形式は TYPES の仕様で寸法・窓割・前面形状・屋根機器・台車・床下・内装・塗色が
すべて異なり、同一テンプレートの色違いにならないようにする。リグ規約(台車/輪軸/連結器の部品化)は trainkit に従う。

形式: jnr_dc 通勤形(平妻・4扉・ロングシート) / jnr_sub 近郊形(湘南顔・3扉・ボックス+ロング) /
      jnr_exp 急行形(2扉デッキ・大窓・ボックス) / jnr_ltd 特急形(ボンネット・リクライニング) /
      jnr_ac 交流形(波板側面・碍子・3扉) / ke 私鉄(丸い3枚窓の流線形・転換クロス) / km 地下鉄(ステンレス・4扉・貫通扉)
"""
import math
import random
import lib
from trainkit import *
import trainkit as TK
import train2


# --------------------------------------------------------------------------- materials
def mats():
    train2.extra_mats()
    if "t_green" in TK._VM:
        return
    P = TK.vpaint
    TK._VM.update({
        "t_green": P("t_green", (0.035, 0.15, 0.085), rough=0.4, rust=0.15),
        "t_orange": P("t_orange", (0.72, 0.31, 0.035), rough=0.4, rust=0.15),
        "t_verm": P("t_verm", (0.58, 0.085, 0.03), rough=0.38, rust=0.15),
        "t_cream": P("t_cream", (0.80, 0.70, 0.50), rough=0.42, rust=0.12),
        "t_ltdred": P("t_ltdred", (0.50, 0.04, 0.035), rough=0.36, rust=0.12),
        "t_ivory": P("t_ivory", (0.78, 0.76, 0.66), rough=0.42, rust=0.10),
        "t_navy": P("t_navy", (0.025, 0.06, 0.16), rough=0.42, rust=0.12),
        "t_maroon": P("t_maroon", (0.26, 0.03, 0.03), rough=0.34, rust=0.10),
        "t_gold": P("t_gold", (0.62, 0.46, 0.12), rough=0.34, rust=0.05, metal=0.5),
        "t_steel": P("t_steel", (0.60, 0.62, 0.63), rough=0.26, rust=0.04, metal=0.8, seams=False),
        "t_sred": P("t_sred", (0.58, 0.035, 0.04), rough=0.36, rust=0.08),
        "t_warn": P("t_warn", (0.72, 0.56, 0.05), rough=0.45, rust=0.15),
        "t_sky": P("t_sky", (0.11, 0.33, 0.56), rough=0.38, rust=0.14),
        "t_grey": P("t_grey", (0.20, 0.21, 0.22), rough=0.5, rust=0.25),
        "t_moq_g": lib.mat_plain("t_moq_g", (0.10, 0.22, 0.12), rough=0.9, spec=0.1),
        "t_moq_b": lib.mat_plain("t_moq_b", (0.12, 0.16, 0.34), rough=0.9, spec=0.1),
        "t_moq_r": lib.mat_plain("t_moq_r", (0.36, 0.07, 0.07), rough=0.9, spec=0.1),
        "t_moq_o": lib.mat_plain("t_moq_o", (0.52, 0.27, 0.07), rough=0.9, spec=0.1),
        "t_moq_k": lib.mat_plain("t_moq_k", (0.05, 0.05, 0.06), rough=0.9, spec=0.1),
        "t_moq_y": lib.mat_plain("t_moq_y", (0.70, 0.55, 0.14), rough=0.9, spec=0.1),
        "t_bronze": P("t_bronze", (0.15, 0.085, 0.045), rough=0.30, rust=0.05, metal=0.55),
        "t_champ": P("t_champ", (0.72, 0.60, 0.36), rough=0.28, rust=0.03, metal=0.75, seams=False),
        "t_carp": lib.mat_plain("t_carp", (0.20, 0.07, 0.07), rough=0.95, spec=0.05),
        "t_leat": lib.mat_plain("t_leat", (0.30, 0.16, 0.08), rough=0.55, spec=0.25),
        "t_cream2": lib.mat_plain("t_cream2", (0.80, 0.74, 0.60), rough=0.8, spec=0.05),
        "t_curt": lib.mat_plain("t_curt", (0.07, 0.13, 0.28), rough=0.92, spec=0.05),
        "t_blank": lib.mat_plain("t_blank", (0.55, 0.60, 0.70), rough=0.9, spec=0.05),
        "t_white": lib.mat_plain("t_white", (0.82, 0.82, 0.78), rough=0.85, spec=0.05),
        "t_panel": lib.mat_plain("t_panel", (0.52, 0.45, 0.30), rough=0.7, spec=0.1),
        "t_wood": lib.mat_plain("t_wood", (0.30, 0.17, 0.08), rough=0.55, spec=0.2),
        "t_cab": lib.mat_plain("t_cab", (0.18, 0.28, 0.20), rough=0.7, spec=0.1),
        "t_pole": lib.mat_plain("t_pole", (0.72, 0.30, 0.04), rough=0.4, metal=0.5),
        "t_lino": lib.mat_plain("t_lino", (0.12, 0.10, 0.08), rough=0.7, spec=0.1),
        "t_lino2": lib.mat_plain("t_lino2", (0.33, 0.22, 0.12), rough=0.7, spec=0.1),
        "t_ins": lib.mat_plain("t_ins", (0.55, 0.28, 0.12), rough=0.15, spec=0.8),
    })


# --------------------------------------------------------------------------- spec table
# z = (zfl 床, zs 窓下端, zw1 窓上端, zt 軒, zr 屋根頂)  cab = 乗務員室長 (片側)
TYPES = {
    "jnr_dc": dict(
        fs="sabo", ss="sabo",
        ds="two", ps="weld", wc=(0.05, 0.05), liner="t_white", lamp="tube",
        title="通勤形(平妻・4扉)", L=20.0, W=2.80, z=(1.10, 1.80, 2.62, 3.00, 3.52), cab=1.55, zb0=0.92,
        lo="t_sky", up="t_sky", door="t_grey", mask="t_warn", stripe=[],
        pattern="w1 D w3 D w3 D w3 D w1", door_w=1.30, win="single", pillar=0.13,
        front="flat", screens=2, lamps="belt", roofshape="round",
        roof=["pant", "garland", "tvent"], pant_x=-5.5, bogie=("dt", 2.1, 0.43), under="boxes",
        seat="t_moq_g", interior="long", standing=True, stripe_rain=True),
    "jnr_sub": dict(
        fs="sabo", ss="roll",
        ds="louver", ps="louver", wc=(0.0, 0.0), liner="t_panel", lamp="tube",
        title="近郊形(湘南顔・3扉)", L=20.0, W=2.90, z=(1.10, 1.78, 2.66, 3.05, 3.50), cab=1.85, zb0=0.90,
        lo="t_green", up="t_orange", door="t_green", mask="t_green", stripe=[("t_cream", 1.62, 1.70)],
        pattern="w2 D w3 D w3 D w2", door_w=1.30, win="sash2", pillar=0.15,
        front="vee", screens=2, lamps="roofc", roofshape="round", rake=0.20,
        roof=["pant", "pant2", "torpedo"], pant_x=-6.8, bogie=("dt", 2.1, 0.43), under="skirt",
        seat="t_moq_b", interior="mix", standing=True),
    "jnr_exp": dict(
        fs="holder", ss="sabo",
        ds="deck", ps="rivets", wc=(0.12, 0.0), liner="t_panel", lamp="tube",
        title="急行形(2扉デッキ・大窓)", L=20.0, W=2.90, z=(1.15, 1.85, 2.60, 3.02, 3.60), cab=1.95, zb0=0.92,
        lo="t_verm", up="t_cream", door="t_verm", mask="t_verm", stripe=[("t_verm", 2.64, 2.76)],
        pattern="D s w8 D", door_w=0.95, win="wide", pillar=0.09,
        front="vee", screens=2, lamps="roofc", roofshape="round", rake=0.30, headboard=True,
        roof=["pant", "bigvent", "duct"], pant_x=5.6, bogie=("air", 2.2, 0.43), under="boxes",
        seat="t_moq_r", interior="box", standing=False),
    "jnr_ltd": dict(
        fs="holder", ss="roll",
        ds="plug", ps="flute", wc=(0.16, 0.16), liner="t_cream", lamp="strip",
        title="特急形(ボンネット・リクライニング)", L=20.5, W=2.95, z=(1.22, 1.90, 2.70, 3.10, 3.66), cab=2.0, zb0=0.90,
        lo="t_cream", up="t_cream", door="t_cream", mask="t_cream", stripe=[("t_ltdred", 1.10, 1.30), ("t_ltdred", 2.78, 2.98)],
        pattern="D s w9 D", door_w=0.90, win="wide", pillar=0.08,
        front="bonnet", screens=3, lamps="bonnet", roofshape="round", nose=2.1,
        roof=["pant", "acpod", "aerial"], pant_x=5.8, bogie=("air", 2.3, 0.43), under="skirtfull",
        seat="t_moq_y", interior="recline", standing=False),
    "jnr_ac": dict(
        fs="roll", ss="roll",
        ds="slide1", ps="corrug", wc=(0.0, 0.0), liner="t_white", lamp="globe",
        title="交流形(波板・碍子)", L=20.0, W=2.80, z=(1.10, 1.80, 2.60, 3.00, 3.46), cab=1.60, zb0=0.92,
        lo="t_ivory", up="t_ivory", door="t_navy", mask="t_navy", stripe=[("t_navy", 1.05, 1.32), ("t_navy", 2.70, 2.84)],
        pattern="w2 D w4 D w4 D w2", door_w=1.25, win="single", pillar=0.11,
        front="flat", screens=3, lamps="high", roofshape="flat", corrug=True,
        roof=["pant", "insul", "hvcable", "tvent"], pant_x=-5.0, bogie=("dt", 2.2, 0.43), under="xfmr",
        seat="t_moq_o", interior="mix", standing=True),
    "ke": dict(
        fs="sabo", ss="roll",
        ds="fold", ps="plank", wc=(0.22, 0.04), liner="t_wood", lamp="globe",
        title="私鉄形(丸い3枚窓・転換クロス)", L=18.0, W=2.70, z=(1.05, 1.74, 2.55, 2.92, 3.42), cab=1.5, zb0=0.90,
        lo="t_maroon", up="t_maroon", door="t_maroon", mask="t_maroon", stripe=[("t_ivory", 1.62, 1.72), ("t_gold", 1.76, 1.79)],
        pattern="w1 D w3 D w3 D w1", door_w=1.20, win="arch", pillar=0.10,
        front="round", screens=3, lamps="round", roofshape="round", nose=0.95,
        roof=["pant_sa", "pods", "signbox"], pant_x=-4.5, bogie=("pedestal", 2.0, 0.40), under="skirt",
        seat="t_moq_b", interior="cross", standing=False),
    "km": dict(
        fs="roll", ss="roll",
        ds="two2", ps="ribs", wc=(0.07, 0.07), liner="t_white", lamp="strip",
        title="地下鉄(ステンレス・4扉・貫通扉)", L=18.0, W=2.80, z=(1.00, 1.66, 2.42, 2.80, 3.30), cab=1.35, zb0=0.88,
        lo="t_steel", up="t_steel", door="t_steel", mask="t_sred", stripe=[("t_sred", 1.45, 1.60), ("t_sred", 2.52, 2.62)],
        pattern="w1 D w2 D w2 D w2 D w1", door_w=1.30, win="subway", pillar=0.12,
        front="subfront", screens=2, lamps="sub", roofshape="flat",
        roof=["ac_box", "ac_box2", "aerial"], pant_x=0.0, bogie=("dt", 2.1, 0.43), under="skirtfull",
        seat="t_moq_r", interior="subway", standing=True),
}

TYPES.update({
    "kiha_std": dict(
        title="国鉄一般形気動車(2扉・ラジエーター)", L=20.0, W=2.80, z=(1.12, 1.80, 2.58, 2.98, 3.50), cab=1.75, zb0=0.92, diesel=True,
        fs="sabo", ss="sabo", ds="hing", ps="lap", wc=(0.04, 0.04), liner="t_cab", lamp="globe",
        lo="t_verm", up="t_cream", door="t_verm", mask="t_verm", stripe=[],
        pattern="w2 D w8 D w2", door_w=1.05, win="pair", pillar=0.11,
        front="vee", screens=2, lamps="roofc", roofshape="round", rake=0.12,
        roof=["radiator", "exhaust", "garland"], pant_x=0.0, bogie=("dt", 2.1, 0.43), under="engine",
        seat="t_moq_g", interior="box", standing=False),
    "kiha_exp": dict(
        title="国鉄急行形気動車(2扉デッキ・大窓)", L=21.0, W=2.90, z=(1.18, 1.86, 2.62, 3.04, 3.58), cab=2.0, zb0=0.92, diesel=True,
        fs="holder", ss="sabo", ds="deck", ps="beads", wc=(0.10, 0.02), liner="t_panel", lamp="tube",
        lo="t_cream", up="t_cream", door="t_cream", mask="t_cream", stripe=[("t_ltdred", 1.62, 1.80), ("t_ltdred", 2.64, 2.78)],
        pattern="D s w9 D", door_w=0.95, win="wide", pillar=0.08,
        front="flat", screens=2, lamps="belt", roofshape="round", rake=0.28,
        roof=["radiator", "exhaust", "bigvent"], pant_x=0.0, bogie=("air", 2.3, 0.43), under="engine",
        seat="t_moq_r", interior="box", standing=False),
    "kiha_hyb": dict(
        title="国鉄ハイブリッド汎用気動車(3扉・パンタ付)", L=20.0, W=2.95, z=(1.06, 1.72, 2.50, 2.88, 3.36), cab=1.45, zb0=0.88, diesel=True,
        fs="roll", ss="roll", ds="modern", ps="smooth", wc=(0.12, 0.12), liner="t_white", lamp="strip",
        lo="t_steel", up="t_steel", door="t_orange", mask="black", stripe=[("t_orange", 1.30, 1.52), ("t_green", 2.56, 2.66)],
        pattern="w1 D w3 D w3 D w1", door_w=1.30, win="ribbon", pillar=0.07,
        front="flat", screens=2, lamps="led", roofshape="flat", rake=0.34,
        roof=["pant", "hybrid", "aerial"], pant_x=-5.2, bogie=("dt", 2.1, 0.43), under="skirtfull",
        seat="t_moq_b", interior="mix", standing=True),
    "kiha_ltd": dict(
        title="国鉄特急ハイブリッド気動車(展望前面)", L=21.0, W=2.95, z=(1.20, 1.92, 2.66, 3.06, 3.60), cab=2.1, zb0=0.9, diesel=True,
        fs="roll", ss="roll", ds="modern", ps="smooth", wc=(0.18, 0.18), liner="t_cream", lamp="strip",
        lo="t_ivory", up="t_ivory", door="t_ivory", mask="t_ltdred", stripe=[("t_ltdred", 1.20, 1.46), ("t_navy", 2.70, 2.80)],
        pattern="D s w9 D", door_w=0.95, win="ribbon", pillar=0.06,
        front="round", screens=3, lamps="round", roofshape="round", nose=1.25,
        roof=["pant", "hybrid", "acpod"], pant_x=6.0, bogie=("air", 2.3, 0.43), under="skirtfull",
        seat="t_moq_o", interior="recline", standing=False),
    "kiha_sr": dict(
        title="山麓鉄道キハ200(丸形・片引き1扉)", L=16.0, W=2.65, z=(1.00, 1.66, 2.42, 2.78, 3.28), cab=1.5, zb0=0.88, diesel=True,
        fs="sabo", ss="sabo", ds="bus", ps="plank", wc=(0.14, 0.14), liner="t_wood", lamp="globe",
        lo="t_maroon", up="t_ivory", door="t_maroon", mask="t_maroon", stripe=[("t_gold", 1.64, 1.70)],
        pattern="w2 D w4 w1", door_w=1.05, win="bus", pillar=0.10,
        front="round", screens=3, lamps="round", roofshape="round", nose=0.55,
        roof=["radiator", "exhaust", "pods"], pant_x=0.0, bogie=("pedestal", 1.9, 0.40), under="engine",
        seat="t_wood", interior="long", standing=False),
    "kiha_hr": dict(
        title="臨港線小型気動車(バス型・中央扉)", L=12.5, W=2.50, z=(0.95, 1.55, 2.30, 2.66, 3.08), cab=1.3, zb0=0.82, diesel=True,
        fs="sabo", ss="sabo", ds="bus", ps="weld", wc=(0.10, 0.10), liner="t_panel", lamp="globe",
        lo="t_navy", up="t_warn", door="t_navy", mask="t_navy", stripe=[("t_navy", 2.30, 2.42)],
        pattern="w2 D w2", door_w=1.0, win="bus", pillar=0.10,
        front="flat", screens=1, lamps="belt", roofshape="round", rake=0.10,
        roof=["radiator", "exhaust"], pant_x=0.0, bogie=("dt", 1.8, 0.36), under="engine",
        seat="t_moq_y", interior="long", standing=False),
})


def _bays(S, tot, key="pattern"):
    """pattern 'w1 D w3 ...' → bays [(kind,width)]. W 幅は残り寸法を窓数で均等割り。"""
    toks = S.get(key, S["pattern"]).split()
    nD = sum(1 for t in toks if t == "D")
    nS = sum(1 for t in toks if t == "s")
    nW = sum(int(t[1:]) for t in toks if t[0] == "w")
    sw = 0.95
    ww = (tot - nD * S["door_w"] - nS * sw) / max(1, nW)
    out = []
    for t in toks:
        if t == "D":
            out.append(("D", S["door_w"]))
        elif t == "s":
            out.append(("s", sw))
        else:
            out += [("W", ww)] * int(t[1:])
    return out


def _sec(w, zb, zt, rc):
    """角丸の断面(8点)。"""
    rc = min(rc, (zt - zb) * 0.45, w * 0.9)
    return [(-w, zb), (w, zb), (w, zt - rc), (w - rc * 0.3, zt - rc * 0.3), (w - rc, zt),
            (-(w - rc), zt), (-(w - rc * 0.3), zt - rc * 0.3), (-w, zt - rc)]


def _pane(v, x0, y0, z0, x1, y1, z1, key="glass", t=0.018):
    """平面ガラス(底辺中心(x0,y0,z0) → 上辺中心(x1,y1,z1)、幅は別指定)は使わず、4点を直接張る薄板。"""
    pass


def _pane4(acc, p00, p10, p11, p01, t=0.016, n=(1, 0, 0)):
    """4点の薄い板(法線 n 方向へ厚み t)。"""
    i = len(acc.V)
    pts = [p00, p10, p11, p01]
    for p in pts:
        acc.V.append((p[0], p[1], p[2]))
    for p in pts:
        acc.V.append((p[0] + n[0] * t, p[1] + n[1] * t, p[2] + n[2] * t))
    acc.F += [(i, i + 1, i + 2, i + 3), (i + 7, i + 6, i + 5, i + 4), (i, i + 4, i + 5, i + 1),
              (i + 1, i + 5, i + 6, i + 2), (i + 2, i + 6, i + 7, i + 3), (i + 3, i + 7, i + 4, i)]


# --------------------------------------------------------------------------- body + windows
def _body(v, S):
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    zb0 = S["zb0"]
    lo, up = S["lo"], S["up"]
    for s in (-1, 1):                       # 腰板(側板だけ: 室内を見通せるよう中空)
        v.A(lo, 0.012).box(-L / 2, L / 2, *sorted((s * (h - 0.07), s * h)), zb0, zs)
    v.A("t_grey", 0.01).box(-L / 2, L / 2, -h + 0.07, h - 0.07, zfl - 0.12, zfl)         # 床板
    v.A(up, 0.01).extrude_x([(-h, zw1), (h, zw1), (h, zt), (-h, zt)], -L / 2, L / 2)   # 窓上の帯+天井
    rs = S["roofshape"]
    if rs == "flat":
        prof = upper_profile(W, zt - 0.05, zt + 0.02, zr, n=5, inset=0.10)
    else:
        prof = upper_profile(W, zt - 0.05, zt + 0.06, zr, n=7, inset=0.03)
    v.A("roof", 0.015).extrude_x(prof, -L / 2 + 0.02, L / 2 - 0.02)
    # 窓下の帯(ステンレス/波板の縦リブ)
    if S.get("corrug"):
        k = "t_steel" if S["lo"] == "t_steel" else S["lo"]
        n = int(L / 0.30)
        for s in (-1, 1):
            a = v.A(k, 0.003)
            for i in range(n):
                x = -L / 2 + 0.15 + i * 0.30
                a.box(x - 0.025, x + 0.025, *sorted((s * h, s * (h + 0.006))), zb0 + 0.05, zs - 0.04)
    for (key, z0, z1) in S["stripe"]:                                   # 帯
        for s in (-1, 1):
            v.A(key, 0.004).box(-L / 2 + 0.01, L / 2 - 0.01, *sorted((s * (h + 0.001), s * (h + 0.009))), z0, z1)
    # 雨どい
    for s in (-1, 1):
        v.A("t_grey", 0.003).box(-L / 2, L / 2, *sorted((s * (h - 0.005), s * (h + 0.04))), zt - 0.02, zt + 0.02)


def _fillet(v, key, xc, zc, r, sx, sz, ya, yb):
    """窓の隅の丸み(三角板)。(xc,zc)=窓の角、sx,sz=窓が広がる向き。"""
    if r < 0.01:
        return
    prof = [(xc, zc), (xc + sx * r, zc), (xc + sx * r * 0.55, zc + sz * r * 0.2), (xc + sx * r * 0.2, zc + sz * r * 0.55), (xc, zc + sz * r)]
    v.A(key, 0.002).extrude_y(prof, ya, yb)


def _door(v, S, xa, xb, s, style):
    h = S["W"] / 2
    zfl, zs, zw1, zt, zr = S["z"]
    ya, yb = sorted((s * (h - 0.078), s * (h + 0.014)))
    yo0, yo1 = sorted((s * (h + 0.014), s * (h + 0.022)))
    key = S["door"]
    zlo, zhi = zfl + 0.02, zw1 + 0.07
    xm = (xa + xb) / 2
    gl = v.A("glass")
    fk = v.A("t_grey", 0.002)
    w = xb - xa
    # 戸袋/枠(全形式共通の「溝」だけは持たない: 形式ごとに違う縁取り)
    if style == "two":            # 通勤形: 2枚引戸+各枚に角窓、黒いゴム縁
        v.A(key, 0.004).box(xa, xm - 0.012, ya, yb, zlo, zhi)
        v.A(key, 0.004).box(xm + 0.012, xb, ya, yb, zlo, zhi)
        v.A("black").box(xm - 0.012, xm + 0.012, ya, yb, zlo, zhi)
        for (a, b) in ((xa + 0.13, xm - 0.10), (xm + 0.10, xb - 0.13)):
            gl.box(a, b, yo0, yo1, zs + 0.18, zw1 - 0.10)
            fk.box(a - 0.025, b + 0.025, yo0, yo1, zs + 0.15, zs + 0.18)
            fk.box(a - 0.025, b + 0.025, yo0, yo1, zw1 - 0.10, zw1 - 0.075)
        v.A("t_grey").box(xa - 0.04, xa, ya, yb, zlo, zhi + 0.02); v.A("t_grey").box(xb, xb + 0.04, ya, yb, zlo, zhi + 0.02)
    elif style == "hing":         # 気動車一般形: 片引戸1枚(上半分が窓)+下半に補強リブ+手すり
        v.A(key, 0.004).box(xa + 0.04, xb - 0.04, ya, yb, zlo, zhi)
        gl.box(xa + 0.14, xb - 0.14, yo0, yo1, zs - 0.05, zw1 - 0.08)
        fk.box(xa + 0.12, xb - 0.12, yo0, yo1, zs - 0.08, zs - 0.05)
        for k in range(3):
            v.A("t_grey").box(xa + 0.10, xb - 0.10, yo0, yo1, zfl + 0.20 + k * 0.17, zfl + 0.23 + k * 0.17)
        v.A("t_steel").cyl((xb - 0.07, s * (h + 0.06), zfl + 0.1), (xb - 0.07, s * (h + 0.06), zw1), 0.015, 0.015, seg=6)
    elif style == "bus":          # バス型: 黒枠の大きなガラスの2枚折戸
        v.A("black", 0.004).box(xa, xb, ya, yb, zlo, zhi)
        for (a, b) in ((xa + 0.06, xm - 0.03), (xm + 0.03, xb - 0.06)):
            gl.box(a, b, yo0, yo1, zlo + 0.14, zhi - 0.10)
            _fillet(v, "black", a, zhi - 0.10, 0.10, 1, -1, yo0, yo1); _fillet(v, "black", b, zhi - 0.10, 0.10, -1, -1, yo0, yo1)
        v.A("t_steel").cyl((xm, s * (h + 0.05), zfl), (xm, s * (h + 0.05), zw1), 0.014, 0.014, seg=6)
    elif style == "modern":       # 近代形: 面一の引戸(全面スモークガラス+白縁)
        v.A(key, 0.003).box(xa, xb, ya, yb, zlo, zhi)
        for (a, b) in ((xa + 0.06, xm - 0.03), (xm + 0.03, xb - 0.06)):
            gl.box(a, b, yo0, yo1, zlo + 0.30, zhi - 0.12)
            v.A("t_white").box(a - 0.02, a, yo0, yo1, zlo + 0.28, zhi - 0.10); v.A("t_white").box(b, b + 0.02, yo0, yo1, zlo + 0.28, zhi - 0.10)
        v.A("t_sred").box(xm - 0.05, xm + 0.05, *sorted((s * (h + 0.014), s * (h + 0.03))), zhi + 0.0, zhi + 0.06)
        v.A("lamp_glow").box(xm - 0.035, xm + 0.035, *sorted((s * (h + 0.03), s * (h + 0.034))), zhi + 0.01, zhi + 0.05)
    elif style == "lux":          # 周遊列車: 面一の木目調の片開き戸+金縁+縦長の窓+真鍮の把手
        v.A(key, 0.004).box(xa + 0.03, xb - 0.03, ya, yb, zlo, zhi)
        v.A("t_champ", 0.002).box(xa + 0.02, xa + 0.05, ya, yo1, zlo, zhi); v.A("t_champ", 0.002).box(xb - 0.05, xb - 0.02, ya, yo1, zlo, zhi)
        v.A("t_champ", 0.002).box(xa + 0.02, xb - 0.02, ya, yo1, zhi - 0.03, zhi)
        gl.box(xa + 0.20, xb - 0.20, yo0, yo1, zs - 0.10, zw1 + 0.02)
        v.A("t_champ", 0.002).box(xa + 0.17, xb - 0.17, yo0, yo1, zs - 0.13, zs - 0.10)
        v.A("t_champ").box(xb - 0.16, xb - 0.12, yo0, yo1 + s * 0.012, zfl + 1.00, zfl + 1.28)
    elif style == "two2":         # 地下鉄: 全高の細長い窓+上部の戸閉表示灯+アルミ縁
        v.A(key, 0.004).box(xa, xm - 0.01, ya, yb, zlo, zhi)
        v.A(key, 0.004).box(xm + 0.01, xb, ya, yb, zlo, zhi)
        v.A("black").box(xm - 0.01, xm + 0.01, ya, yb, zlo, zhi)
        for (a, b) in ((xa + 0.38, xm - 0.08), (xm + 0.08, xb - 0.38)):
            gl.box(a, b, yo0, yo1, zfl + 0.55, zw1 + 0.02)
            for k in (a - 0.02, b + 0.02):
                v.A("t_steel").box(k - 0.012, k + 0.012, yo0, yo1, zfl + 0.52, zw1 + 0.05)
        v.A("t_sred").box(xm - 0.07, xm + 0.07, *sorted((s * (h + 0.012), s * (h + 0.05))), zhi + 0.02, zhi + 0.09)
        v.A("lamp_glow").box(xm - 0.05, xm + 0.05, *sorted((s * (h + 0.05), s * (h + 0.056))), zhi + 0.035, zhi + 0.075)
    elif style == "louver":       # 近郊形: 小さな2連窓+下部ルーバー
        v.A(key, 0.004).box(xa, xm - 0.012, ya, yb, zlo, zhi)
        v.A(key, 0.004).box(xm + 0.012, xb, ya, yb, zlo, zhi)
        v.A("black").box(xm - 0.012, xm + 0.012, ya, yb, zlo, zhi)
        for (a, b) in ((xa + 0.10, xm - 0.08), (xm + 0.08, xb - 0.10)):
            for zz in (zw1 - 0.50, zw1 - 0.20):
                gl.box(a, b, yo0, yo1, zz - 0.12, zz + 0.07) if False else None
            gl.box(a, b, yo0, yo1, zw1 - 0.62, zw1 - 0.10)
            fk.box(a - 0.02, b + 0.02, yo0, yo1, zw1 - 0.38, zw1 - 0.35)
            for k in range(5):
                v.A("black").box(a + 0.02, b - 0.02, yo0, yo1, zfl + 0.30 + k * 0.075, zfl + 0.325 + k * 0.075)
    elif style == "deck":         # 急行形: 幅の狭い片開き扉+縦長窓+ステップ板+握り棒
        v.A(key, 0.004).box(xa + 0.03, xb - 0.03, ya, yb, zlo, zhi)
        gl.box(xa + 0.22, xb - 0.22, yo0, yo1, zs - 0.15, zw1 - 0.06)
        fk.box(xa + 0.20, xb - 0.20, yo0, yo1, zs - 0.18, zs - 0.15)
        v.A("t_steel").cyl((xa + 0.06, s * (h + 0.07), zfl), (xa + 0.06, s * (h + 0.07), zw1 + 0.02), 0.014, 0.014, seg=6)
        v.A("t_steel").cyl((xb - 0.06, s * (h + 0.07), zfl), (xb - 0.06, s * (h + 0.07), zw1 + 0.02), 0.014, 0.014, seg=6)
        v.A("iron").box(xa + 0.02, xb - 0.02, *sorted((s * (h - 0.01), s * (h + 0.07))), zfl - 0.06, zfl - 0.02)
    elif style == "plug":         # 特急形: 窓なし格間つきプラグドア+丸い小窓+金色の把手
        v.A(key, 0.004).box(xa + 0.02, xb - 0.02, ya, yb, zlo, zhi)
        for (z0, z1) in ((zfl + 0.08, zfl + 0.55), (zfl + 0.62, zs + 0.40)):
            v.A(key, 0.006).box(xa + 0.10, xb - 0.10, *sorted((s * (h + 0.014), s * (h + 0.026))), z0, z1)
        v.A("glass").cyl((xm, s * (h + 0.014), zw1 - 0.22), (xm, s * (h + 0.028), zw1 - 0.22), 0.14, 0.14, seg=14)
        v.A("t_gold").torus((xm, s * (h + 0.03), zw1 - 0.22), "y", 0.15, 0.014, segR=16, segr=4)
        v.A("t_gold").box(xb - 0.16, xb - 0.12, *sorted((s * (h + 0.014), s * (h + 0.05))), zs - 0.2, zs + 0.15)
    elif style == "slide1":       # 交流形: 幅広の一枚戸+横長の高窓2つ+下部の蹴板
        v.A(key, 0.004).box(xa, xb, ya, yb, zlo, zhi)
        for (a, b) in ((xa + 0.10, xm - 0.04), (xm + 0.04, xb - 0.10)):
            gl.box(a, b, yo0, yo1, zw1 - 0.48, zw1 - 0.08)
        v.A("t_grey").box(xa, xb, yo0, yo1, zlo, zlo + 0.18)
        v.A("t_grey").box(xm - 0.015, xm + 0.015, yo0, yo1, zlo + 0.18, zhi)
        v.A("t_steel").box(xb - 0.12, xb - 0.07, *sorted((s * (h + 0.02), s * (h + 0.06))), zs - 0.1, zs + 0.3)
    elif style == "fold":         # 私鉄形: 折戸(中央ちょうつがい)+アーチ窓+真鍮の手すり
        v.A(key, 0.004).box(xa, xm - 0.006, ya, yb, zlo, zhi)
        v.A(key, 0.004).box(xm + 0.006, xb, ya, yb, zlo, zhi)
        for (a, b, sg) in ((xa + 0.10, xm - 0.07, -1), (xm + 0.07, xb - 0.10, 1)):
            gl.box(a, b, yo0, yo1, zs - 0.05, zw1 - 0.10)
            _fillet(v, key, a, zw1 - 0.10, 0.16, 1, -1, yo0, yo1); _fillet(v, key, b, zw1 - 0.10, 0.16, -1, -1, yo0, yo1)
            v.A("t_gold").box(a - 0.015, b + 0.015, yo0, yo1, zs - 0.08, zs - 0.05)
        v.A("t_gold").cyl((xm, s * (h + 0.07), zfl), (xm, s * (h + 0.07), zw1 + 0.02), 0.016, 0.016, seg=8)
        v.A("black").box(xm - 0.006, xm + 0.006, ya, yb, zlo, zhi)


def _panels(v, S, tot, bays):
    """窓下の側面パネル意匠(形式ごとに別設計)。"""
    h = S["W"] / 2
    zfl, zs, zw1, zt, zr = S["z"]
    L = S["L"]
    ps = S["ps"]
    x = -tot / 2
    z0, z1 = S["zb0"] + 0.08, zs - 0.06
    for kind, w in bays:
        xa, xb = x, x + w
        x = xb
        if kind != "W" and kind != "s":
            continue
        for s in (-1, 1):
            yy = s * h
            if ps == "weld":                  # 平板+水平の溶接ビード+点検ふた
                v.A("t_grey", 0.002).box(xa + 0.03, xb - 0.03, *sorted((yy, yy + s * 0.004)), (z0 + z1) / 2 - 0.006, (z0 + z1) / 2 + 0.006)
                if (kind == "W") and int((xa + 20) * 10) % 3 == 0:
                    v.A("t_grey", 0.003).box(xa + 0.2, xb - 0.2, *sorted((yy, yy + s * 0.012)), z0 + 0.04, z0 + 0.26)
            elif ps == "louver":              # 通風ルーバーの縦スリット群
                for k in range(6):
                    xx = xa + w * (0.22 + k * 0.11)
                    v.A("black").box(xx - 0.012, xx + 0.012, *sorted((yy, yy + s * 0.006)), z0 + 0.10, z0 + 0.46)
                v.A("t_grey", 0.002).box(xa + w * 0.18, xa + w * 0.84, *sorted((yy, yy + s * 0.005)), z0 + 0.46, z0 + 0.49)
            elif ps == "rivets":              # 2列のリベット線+水平補強帯
                for zz in (z0 + 0.05, z1 - 0.06):
                    k = int(w / 0.09)
                    for j in range(k):
                        v.A("t_grey").cyl((xa + 0.05 + j * 0.09, yy, zz), (xa + 0.05 + j * 0.09, yy + s * 0.010, zz), 0.012, 0.012, seg=5)
                v.A("t_grey", 0.002).box(xa, xb, *sorted((yy, yy + s * 0.005)), (z0 + z1) / 2 - 0.02, (z0 + z1) / 2 + 0.02)
            elif ps == "flute":               # 縦のフルーティング(浅い溝)
                k = int(w / 0.14)
                for j in range(k):
                    xx = xa + 0.07 + j * 0.14
                    v.A("t_grey").box(xx - 0.01, xx + 0.01, *sorted((yy, yy + s * 0.007)), z0, z1)
            elif ps == "beads":               # 水平のビード2条
                for zz in (z0 + 0.30, z0 + 0.62):
                    v.A("t_grey", 0.002).box(xa, xb, *sorted((yy, yy + s * 0.012)), zz, zz + 0.035)
            elif ps == "lap":                 # 下見板張りのように重ねた水平継ぎ+縦の継ぎ目
                for k in range(1, 4):
                    v.A("black").box(xa, xb, *sorted((yy, yy + s * 0.004)), z0 + k * 0.17, z0 + k * 0.17 + 0.012)
                v.A("black").box(xa + w * 0.5 - 0.006, xa + w * 0.5 + 0.006, *sorted((yy, yy + s * 0.004)), z0, z1)
            elif ps == "smooth":              # 平滑+細い縦の継ぎ目だけ
                v.A("t_grey").box(xa - 0.004, xa + 0.004, *sorted((yy, yy + s * 0.003)), z0, z1)
            elif ps == "plank":               # 水平の羽目板(細い溝)
                n = int((z1 - z0) / 0.13)
                for j in range(1, n):
                    v.A("black").box(xa, xb, *sorted((yy, yy + s * 0.004)), z0 + j * 0.13 - 0.004, z0 + j * 0.13 + 0.004)
            elif ps == "ribs":                # ステンレスの太い縦リブ+接合ボルト
                k = int(w / 0.22)
                for j in range(k):
                    xx = xa + 0.11 + j * 0.22
                    v.A("t_steel").box(xx - 0.02, xx + 0.02, *sorted((yy, yy + s * 0.010)), z0, z1)


def _windows(v, S, tot, seed):
    h = S["W"] / 2
    zfl, zs, zw1, zt, zr = S["z"]
    bays = _bays(S, tot)
    bays2 = _bays(S, tot, "pattern2") if "pattern2" in S else bays
    rnd = random.Random(seed + 7)
    pillar = S["pillar"]
    win = S["win"]
    upk = S["up"]
    cp = 0.5 if S["interior"] == "recline" else 0.22
    gl = v.A("glass")
    for s_ in (-1, 1):
        gl.box(-tot / 2, tot / 2, *sorted((s_ * (h - 0.070), s_ * (h - 0.064))), zs, zw1)
    doors = []
    x = -tot / 2
    r_top, r_bot = S["wc"]
    for s in (-1, 1):
      x = -tot / 2
      win = S["win"] if (s == 1 or "win2" not in S) else S["win2"]
      for kind, w in (bays if s == 1 else bays2):
        xa, xb = x, x + w
        if True:
            ya, yb = sorted((s * (h - 0.078), s * h))
            yf0, yf1 = sorted((s * (h - 0.082), s * (h + 0.008)))
            if kind == "W":
                v.A(upk, 0.004).box(xa, xa + pillar / 2, ya, yb, zs, zw1)
                v.A(upk, 0.004).box(xb - pillar / 2, xb, ya, yb, zs, zw1)
                x0, x1 = xa + pillar / 2, xb - pillar / 2
                xm = (xa + xb) / 2
                fk = v.A(upk, 0.002)
                if win == "single":       # 通勤形: 1枚の上昇窓+中桟1本
                    zm = zs + (zw1 - zs) * 0.52
                    fk.box(x0, x1, yf0, yf1, zm - 0.018, zm + 0.018)
                    fk.box(x0, x1, yf0, yf1, zs - 0.02, zs + 0.02); fk.box(x0, x1, yf0, yf1, zw1 - 0.02, zw1 + 0.02)
                elif win == "sash2":      # 近郊形: 縦桟で左右2枚+上段固定/下段上昇(下段は半分上がった状態)
                    fk.box(xm - 0.02, xm + 0.02, yf0, yf1, zs, zw1)
                    fk.box(x0, x1, yf0, yf1, zw1 - 0.43, zw1 - 0.40)
                    fk.box(x0, x1, yf0, yf1, zs + 0.30, zs + 0.34)
                    v.A("black").box(x0 + 0.02, xm - 0.03, *sorted((s * (h - 0.088), s * (h - 0.01))), zs + 0.02, zs + 0.28)   # 開いた窓の隙間
                elif win == "wide":       # 急行形: 幅広の一枚大窓+巻上げ式日除け
                    fk.box(x0, x1, yf0, yf1, zs - 0.02, zs + 0.02); fk.box(x0, x1, yf0, yf1, zw1 - 0.02, zw1 + 0.02)
                    sh_ = rnd.uniform(0.05, 0.38) if rnd.random() < cp * 1.6 else 0.0
                    if sh_ > 0:
                        v.A("curtain").box(x0 + 0.02, x1 - 0.02, *sorted((s * (h - 0.115), s * (h - 0.095))), zw1 - sh_, zw1 - 0.02)
                elif win == "pair":       # 2枚引き違い+中桟+黒ゴム
                    fk.box(xm - 0.02, xm + 0.02, yf0, yf1, zs, zw1)
                    v.A("black").box(x0, x1, yf0, yf1, zs - 0.01, zs + 0.03)
                    v.A("black").box(x0, x1, yf0, yf1, zw1 - 0.03, zw1 + 0.01)
                elif win == "bus":        # バス窓: 黒い太枠+丸い隅
                    v.A("black").box(x0, x1, yf0, yf1, zs - 0.02, zs + 0.05)
                    v.A("black").box(x0, x1, yf0, yf1, zw1 - 0.05, zw1 + 0.02)
                    v.A("black").box(xm - 0.03, xm + 0.03, yf0, yf1, zs, zw1)
                elif win == "ribbon":     # 連続窓: 無桟+細い柱だけ
                    pass
                elif win == "arch":       # 私鉄形: 上部がアーチの窓+金色の下枠+欄間
                    fk.box(x0, x1, yf0, yf1, zw1 - 0.24, zw1 - 0.21)
                    v.A("t_gold").box(x0, x1, yf0, yf1, zs - 0.03, zs + 0.01)
                    fk.box(xm - 0.018, xm + 0.018, yf0, yf1, zs, zw1 - 0.24)
                elif win == "grand":      # 周遊列車: 大きな一枚窓+金の欄間と縦桟(二段窓)
                    gk = v.A("t_champ", 0.002)
                    gk.box(x0, x1, yf0, yf1, zw1 - 0.40, zw1 - 0.37)
                    gk.box(x0, x1, yf0, yf1, zs - 0.02, zs + 0.03)
                    gk.box(xm - 0.015, xm + 0.015, yf0, yf1, zw1 - 0.37, zw1)
                    v.A("t_bronze").box(x0, x1, yf0, yf1, zs - 0.06, zs - 0.02)
                elif win == "square":     # 廊下側: 壁に小さな正方形の窓を上下2段に開ける(実在クルーズトレインの意匠を参考)
                    cx_ = xm
                    hw_ = 0.21
                    zc_ = (zs + zw1) / 2 + 0.04
                    cs_ = (zc_ - 0.30, zc_ + 0.30)
                    wk = v.A(upk, 0.003)
                    wk.box(x0, cx_ - hw_, ya, yb, zs, zw1); wk.box(cx_ + hw_, x1, ya, yb, zs, zw1)
                    wk.box(cx_ - hw_, cx_ + hw_, ya, yb, zs, cs_[0] - hw_)
                    wk.box(cx_ - hw_, cx_ + hw_, ya, yb, cs_[0] + hw_, cs_[1] - hw_)
                    wk.box(cx_ - hw_, cx_ + hw_, ya, yb, cs_[1] + hw_, zw1)
                    fk2 = v.A("t_champ", 0.002)
                    for zc2 in cs_:
                        fk2.box(cx_ - hw_ - 0.02, cx_ + hw_ + 0.02, yf0, yf1, zc2 - hw_ - 0.022, zc2 - hw_)
                        fk2.box(cx_ - hw_ - 0.02, cx_ + hw_ + 0.02, yf0, yf1, zc2 + hw_, zc2 + hw_ + 0.022)
                        fk2.box(cx_ - hw_ - 0.022, cx_ - hw_, yf0, yf1, zc2 - hw_, zc2 + hw_)
                        fk2.box(cx_ + hw_, cx_ + hw_ + 0.022, yf0, yf1, zc2 - hw_, zc2 + hw_)
                elif win == "subway":     # 地下鉄: 上段が固定の2枚窓+ステンレス桟+下段のみ小さな換気窓
                    fk = v.A("t_steel", 0.002)
                    fk.box(xm - 0.02, xm + 0.02, yf0, yf1, zs, zw1)
                    fk.box(x0, x1, yf0, yf1, zs + 0.38, zs + 0.41)
                    v.A("black").box(x0 + 0.03, xm - 0.04, *sorted((s * (h - 0.088), s * (h - 0.01))), zs + 0.01, zs + 0.35) if False else None
                if win in ("single", "wide", "sash2", "arch", "subway", "pair", "bus", "ribbon", "grand"):
                    # 窓隅の丸み(形式ごとに半径が違う)
                    yy0, yy1 = sorted((s * (h - 0.082), s * (h + 0.006)))
                    _fillet(v, upk, x0, zw1, r_top, 1, -1, yy0, yy1); _fillet(v, upk, x1, zw1, r_top, -1, -1, yy0, yy1)
                    _fillet(v, upk, x0, zs, r_bot, 1, 1, yy0, yy1); _fillet(v, upk, x1, zs, r_bot, -1, 1, yy0, yy1)
                if rnd.random() < cp and win not in ("wide", "grand", "square"):
                    lo = zw1 - (zw1 - zs) * rnd.uniform(0.25, 0.7)
                    v.A("curtain").box(x0 + 0.01, x1 - 0.01, *sorted((s * (h - 0.115), s * (h - 0.095))), lo, zw1)
            elif kind == "D":
                if s == 1:
                    doors.append((xa + xb) / 2)
                _door(v, S, xa, xb, s, S["ds"])
            elif kind == "s" and S.get("louver"):
                v.A(upk, 0.003).box(xa, xb, ya, yb, zs, zw1)
                for k in range(9):
                    zz = zs + 0.28 + k * (zw1 - zs - 0.55) / 8
                    v.A("black").box(xa + 0.10, xb - 0.10, *sorted((s * (h + 0.012), s * (h - 0.01))), zz, zz + 0.07)
                    v.A(upk).box(xa + 0.10, xb - 0.10, *sorted((s * (h + 0.02), s * (h + 0.006))), zz + 0.07, zz + 0.095)
            elif kind == "s":
                v.A(upk, 0.003).box(xa, xb, ya, yb, zs, zw1)
                gl.box(xa + 0.2, xb - 0.2, *sorted((s * h, s * (h + 0.012))), zw1 - 0.45, zw1 - 0.1)
        x = xb
    _panels(v, S, tot, bays)
    return doors, bays


# --------------------------------------------------------------------------- cab + front
def _cab(v, S, e, tot, nose):
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    up = S["up"]
    xe = L / 2
    cl = S["cab"]
    xa, xb = sorted((e * tot / 2, e * xe))
    mask = S["mask"]
    fr = S["front"]
    # 乗務員室の側壁(窓+乗務員扉)
    for s in (-1, 1):
        wall_open(v, up, "y", xa, xb, s * (h - 0.08), s * h, zs, zw1,
                  [(*sorted((e * (tot / 2 + 0.2), e * (tot / 2 + 0.2 + min(0.85, cl - 0.55)))), zs + 0.12, zw1 - 0.08)])
        v.A("glass").box(*sorted((e * (tot / 2 + 0.2), e * (tot / 2 + 0.2 + min(0.85, cl - 0.55)))), *sorted((s * (h - 0.01), s * (h + 0.004))), zs + 0.12, zw1 - 0.08)
        v.A(S["door"], 0.004).box(*sorted((e * (tot / 2 + 0.2 + min(0.85, cl - 0.55)) + e * 0.08, e * (xe - 0.12))), *sorted((s * (h - 0.078), s * (h + 0.012))), zs - 0.55, zw1 + 0.04)
        grab_rail(v, (e * (xe - 0.16), s * (h + 0.05), zfl + 0.10), (e * (xe - 0.16), s * (h + 0.05), zw1))
    # 仕切り壁(ガラス戸つき)
    wall_open(v, up, "x", -h, h, e * tot / 2 - 0.05 * e, e * tot / 2, zs, zw1, [(-0.40, 0.40, zs, zw1 - 0.28)])
    wall_open(v, S["lo"], "x", -h, h, e * tot / 2 - 0.05 * e, e * tot / 2, zfl, zs, [])
    v.A("glass").box(*sorted((e * tot / 2 - 0.01 * e, e * tot / 2 - 0.03 * e)), -0.40, 0.40, zs, zw1 - 0.28)
    v.A("t_cab").box(*sorted((e * tot / 2, e * (xe - 0.0))), -h + 0.08, h - 0.08, zfl, zfl + 0.02)
    # 運転台: 機器台+制御器+計器+運転士席
    dx = e * (xe - 0.55)
    yd = -0.52 if fr != "subfront" else -0.62
    v.A("t_cab", 0.01).box(*sorted((dx - e * 0.22, dx + e * 0.22)), -h + 0.1, h - 0.1, zfl, zfl + 0.88)
    v.A("t_grey", 0.01).box(*sorted((dx - e * 0.25, dx + e * 0.12)), -h + 0.12, h - 0.12, zfl + 0.88, zfl + 0.94)
    v.A("black").box(*sorted((dx - e * 0.18, dx + e * 0.02)), yd - 0.32, yd + 0.32, zfl + 0.94, zfl + 1.02)     # 計器盤
    v.A("lampglass").box(*sorted((dx - e * 0.08, dx - e * 0.12)), yd - 0.20, yd + 0.20, zfl + 1.0, zfl + 1.04)   # 速度計
    v.A("steel").cyl((dx - e * 0.28, yd - 0.45, zfl + 0.94), (dx - e * 0.28, yd - 0.45, zfl + 1.08), 0.013, 0.013, seg=6)
    v.A("black").cyl((dx - e * 0.28, yd - 0.45, zfl + 1.08), (dx - e * 0.34, yd - 0.45, zfl + 1.10), 0.032, 0.032, seg=8)   # マスコン
    v.A("steel").cyl((dx - e * 0.28, yd + 0.45, zfl + 0.94), (dx - e * 0.28, yd + 0.45, zfl + 1.02), 0.012, 0.012, seg=6)  # ブレーキ弁
    v.A("t_moq_k", 0.02).box(*sorted((dx - e * 1.15, dx - e * 0.82)), yd - 0.22, yd + 0.22, zfl, zfl + 0.45)     # 運転士席
    v.A("t_moq_k", 0.02).box(*sorted((dx - e * 1.15, dx - e * 1.2)), yd - 0.22, yd + 0.22, zfl + 0.45, zfl + 0.95)
    if e == 1:
        v.A("t_grey", 0.01, True).box(dx - 0.95, dx - 0.7, yd - 0.18, yd + 0.18, zfl + 0.45, zfl + 0.85)      # 運転士の背
        v.A("skin", 0.0, True).sphere((dx - 0.83, yd, zfl + 1.00), (0.085, 0.075, 0.1), seg=8, rings=5)
        v.A("hair", 0.0, True).sphere((dx - 0.85, yd, zfl + 1.04), (0.088, 0.08, 0.09), seg=8, rings=5)
    # 助士側の座席(補助席)
    v.A("t_moq_k", 0.02).box(*sorted((dx - e * 1.0, dx - e * 0.75)), 0.35, 0.65, zfl, zfl + 0.38)
    # ---- 前面
    _front(v, S, e, nose)
    # 連結器
    ce = xe + (nose if fr in ("bonnet", "round") else 0.12)
    coupler(v, e, e * (ce + 0.05))
    v.A("iron", 0.01).box(*sorted((e * xe, e * (ce + 0.0))), -1.2, 1.2, 0.84, 1.00)         # 排障板/バッファ梁
    for s in (-1, 1):
        v.A("black").cyl((e * (ce - 0.04), s * 0.78, 0.95), (e * (ce + 0.14), s * 0.78, 0.95), 0.075, 0.075, seg=10)
        v.A("steel").cyl((e * (ce + 0.14), s * 0.78, 0.95), (e * (ce + 0.17), s * 0.78, 0.95), 0.10, 0.10, seg=10)  # バッファ


def _front0(v, S, e, nose):
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    up, mask, fr = S["up"], S["mask"], S["front"]
    xe = L / 2
    X = lambda a: e * a
    zws, zwt = zs + 0.02, zw1 + 0.06
    if S.get("pano"):
        zws, zwt = zs - 0.30, zt - 0.02
    gl = v.A("glass")
    pil = v.A(up, 0.004)
    rake = S.get("rake", 0.0)

    def screen(xs, yc, wd, zb, zt_, rk, tkey="glass"):
        """風防1枚(幅wd, 下端x=xs, 上端はrk後退)。"""
        a0 = (X(xs), yc - wd / 2, zb); a1 = (X(xs), yc + wd / 2, zb)
        b1 = (X(xs - rk), yc + wd / 2, zt_); b0 = (X(xs - rk), yc - wd / 2, zt_)
        _pane4(v.A(tkey), a0, a1, b1, b0, t=0.02 * e, n=(1, 0, 0))

    if fr in ("flat", "subfront"):
        # 平妻: 前面板(マスク色)+窓
        v.A(mask, 0.006).box(*sorted((X(xe - 0.12), X(xe))), -h, h, 0.92, zws)
        v.A(mask, 0.006).box(*sorted((X(xe - 0.12), X(xe))), -h, h, zwt, zt)
        n = S["screens"]
        if fr == "subfront":
            # 左: 運転窓(大)/ 右: 貫通扉(幅0.78)の非対称
            yd0, yd1 = -h + 0.12, 0.30
            v.A("t_steel", 0.005).box(*sorted((X(xe - 0.12), X(xe + 0.015))), 0.30, 0.34, zws, zwt)
            screen(xe + 0.016, (yd0 + yd1) / 2, yd1 - yd0, zws + 0.05, zwt - 0.08, 0.0)
            v.A("t_steel", 0.005).box(*sorted((X(xe - 0.12), X(xe + 0.02))), 0.34, h - 0.10, zws, zwt)         # 貫通扉
            gl.box(*sorted((X(xe + 0.02), X(xe + 0.032))), 0.46, h - 0.22, zws + 0.35, zwt - 0.10)
            v.A("t_grey").box(*sorted((X(xe + 0.02), X(xe + 0.03))), h - 0.20, h - 0.17, zws + 0.55, zws + 0.80)  # ハンドル
            v.A("t_sred", 0.004).box(*sorted((X(xe - 0.12), X(xe + 0.02))), -h, h, zws - 0.28, zws - 0.12)   # 前面の帯
        else:
            rk = S.get("rake", 0.0)
            if n == 1:
                screen(xe + 0.015, 0.0, 2 * h - 0.34, zws + 0.06, zwt - 0.10, rk)
            elif n == 2:
                for yc in (-0.64, 0.64):
                    screen(xe + 0.015, yc, 0.98, zws + 0.06, zwt - 0.10, rk)
                pil.box(*sorted((X(xe - 0.08), X(xe + 0.04))), -0.10, 0.10, zws, zwt)
            else:
                for yc in (-0.88, 0.0, 0.88):
                    screen(xe + 0.015, yc, 0.72 if yc == 0 else 0.66, zws + 0.06, zwt - 0.10, rk)
                for yp in (-0.51, 0.51):
                    pil.box(*sorted((X(xe - 0.08), X(xe + 0.04))), yp - 0.05, yp + 0.05, zws, zwt)
            pil.box(*sorted((X(xe - 0.08), X(xe + 0.04))), -h, -h + 0.13, zws, zwt)
            pil.box(*sorted((X(xe - 0.08), X(xe + 0.04))), h - 0.13, h, zws, zwt)
            # 前面の補強帯(形式色)
            v.A(mask, 0.004).box(*sorted((X(xe - 0.02), X(xe + 0.02))), -h, h, zwt - 0.01, zwt + 0.12)
            # 貫通路(中央ではなく縁の細い扉枠)
            v.A("t_grey").box(*sorted((X(xe), X(xe + 0.012))), -0.36, 0.36, 1.12, 1.62)
        # 行先表示
        if fr == "flat" and S["fs"] == "roll":
            v.A("black").box(*sorted((X(xe), X(xe + 0.03))), -0.5, 0.5, zt - 0.34, zt - 0.10)
            v.end_plane(f"dest_{S['id']}_{(sum(map(ord, S['id'])) + int(e)) % 3}.png", e, 0.0, 0.84, zt - 0.30, zt - 0.14, X(xe + 0.032))
        elif fr == "subfront" and S["fs"] == "roll":
            v.A("black").box(*sorted((X(xe), X(xe + 0.03))), -0.34, 0.34, zt - 0.30, zt - 0.10)
            v.end_plane(f"dest_{S['id']}_{(sum(map(ord, S['id'])) + int(e)) % 3}.png", e, 0.0, 0.56, zt - 0.26, zt - 0.14, X(xe + 0.032))
        # 灯具
        lp = S["lamps"]
        if lp == "belt":      # 通勤形: 前面下部に前照灯+尾灯の角形ケース
            for s in (-1, 1):
                v.A("black", 0.01).box(*sorted((X(xe), X(xe + 0.07))), s * 0.95 - 0.16, s * 0.95 + 0.16, 1.28, 1.62)
                v.A("lampglass").box(*sorted((X(xe + 0.07), X(xe + 0.085))), s * 0.95 - 0.12, s * 0.95 + 0.12, 1.34, 1.56)
                v.A("t_sred").cyl((X(xe + 0.0), s * 0.62, 1.20), (X(xe + 0.05), s * 0.62, 1.20), 0.06, 0.06, seg=10)
        elif lp == "led":     # 近代形: 角形LEDの前照灯・尾灯を黒マスクの隅に
            for s in (-1, 1):
                v.A("lampglass").box(*sorted((X(xe + 0.012), X(xe + 0.04))), s * 0.98 - 0.14, s * 0.98 + 0.14, 1.20, 1.30)
                v.A("t_sred").box(*sorted((X(xe + 0.012), X(xe + 0.04))), s * 0.98 - 0.14, s * 0.98 + 0.14, 1.34, 1.40)
                v.A("lampglass").box(*sorted((X(xe + 0.012), X(xe + 0.04))), s * 0.55 - 0.05, s * 0.55 + 0.05, zt - 0.20, zt - 0.14)
        elif lp == "high":    # 交流形: 屋根肩に2灯の丸形前照灯+側面寄りの尾灯
            for s in (-1, 1):
                v.A("black").cyl((X(xe), s * 0.90, zt - 0.20), (X(xe + 0.12), s * 0.90, zt - 0.20), 0.14, 0.13, seg=14)
                v.A("lampglass").cyl((X(xe + 0.12), s * 0.90, zt - 0.20), (X(xe + 0.14), s * 0.90, zt - 0.20), 0.105, 0.105, seg=14)
                v.A("t_sred").cyl((X(xe), s * 1.18, 1.30), (X(xe + 0.05), s * 1.18, 1.30), 0.06, 0.06, seg=10)
        else:                 # subway
            for s in (-1, 1):
                v.A("black").box(*sorted((X(xe), X(xe + 0.05))), s * 1.10 - 0.09, s * 1.10 + 0.09, zws - 0.06, zws + 0.12)
                v.A("lampglass").box(*sorted((X(xe + 0.05), X(xe + 0.062))), s * 1.10 - 0.06, s * 1.10 + 0.06, zws - 0.03, zws + 0.09)
                v.A("t_sred").box(*sorted((X(xe), X(xe + 0.04))), s * 0.90 - 0.04, s * 0.90 + 0.04, zws - 0.2, zws - 0.1)
            v.A("lamp_glow").box(*sorted((X(xe + 0.03), X(xe + 0.04))), -0.5, -0.2, zt - 0.26, zt - 0.14)
        if fr == "flat" and S["z"][4] > 3.4:
            v.A("t_grey").box(*sorted((X(xe - 0.15), X(xe + 0.14))), -0.9, 0.9, zt + 0.0, zt + 0.07)   # 庇
        for s in (-1, 1):
            v.A("steel").cyl((X(xe + 0.03), s * 0.55, zwt - 0.1), (X(xe + 0.03), s * 0.05, zws + 0.3), 0.011, 0.011, seg=5)   # ワイパー
        return
    if fr == "vee":
        ap = S.get("ap", 0.55 if S["z"][4] > 3.55 else 0.45)
        yy = h - 0.12
        # マスク(下部): 平面V字のくさび
        poly = [(X(xe - 0.05), -h), (X(xe + ap * 0.82), -0.10), (X(xe + ap), 0.0), (X(xe + ap * 0.82), 0.10), (X(xe - 0.05), h)]
        if e < 0:
            poly = poly[::-1]
        v.A(mask, 0.01).extrude_z(poly, 0.92, zws + 0.02)
        # 風防: V字に配置した2枚(各 yy 幅)
        for s in (-1, 1):
            a0 = (X(xe + ap), s * 0.06, zws + 0.04); a1 = (X(xe + 0.02), s * yy, zws + 0.04)
            b1 = (X(xe + 0.02 - rake), s * yy, zwt - 0.06); b0 = (X(xe + ap - rake), s * 0.06, zwt - 0.06)
            _pane4(gl, a0, a1, b1, b0, t=0.02 * e, n=(1, 0, 0))
        # 中央ピラー+外側ピラー
        v.A(up, 0.004).box(*sorted((X(xe + ap - 0.04 - rake * 0.5), X(xe + ap + 0.04))), -0.07, 0.07, zws, zwt)
        for s in (-1, 1):
            v.A(up, 0.004).box(*sorted((X(xe - 0.05), X(xe + 0.06))), s * (h - 0.10), s * h, zws, zwt)
        # 窓上の前面屋根(ひさし)+ヘッドマーク/行先
        v.A(mask if S["mask"] != S["lo"] else up, 0.006).extrude_z(
            [(X(xe - 0.02), -h), (X(xe + ap * 0.7 - rake), -0.1), (X(xe + ap * 0.82 - rake), 0.0), (X(xe + ap * 0.7 - rake), 0.1), (X(xe - 0.02), h)][::(1 if e > 0 else -1)],
            zwt - 0.06, zt + 0.02)
        v.A("black").box(*sorted((X(xe + ap * 0.6 - rake), X(xe + ap * 0.6 - rake + 0.03)))   , -0.34, 0.34, zt - 0.30, zt - 0.10) if False else None
        v.A("lamp_glow").cyl((X(xe + ap * 0.82 - rake), 0.0, zt + 0.05), (X(xe + ap * 0.82 - rake + 0.04 * e), 0.0, zt + 0.05), 0.10, 0.10, seg=12)
        v.A("black").cyl((X(xe + ap * 0.82 - rake - 0.02 * e), 0.0, zt + 0.05), (X(xe + ap * 0.82 - rake + 0.02 * e), 0.0, zt + 0.05), 0.15, 0.15, seg=14)
        v.A("lampglass").cyl((X(xe + ap * 0.82 - rake + 0.02 * e), 0.0, zt + 0.05), (X(xe + ap * 0.82 - rake + 0.05 * e), 0.0, zt + 0.05), 0.115, 0.115, seg=14)
        for s in (-1, 1):                                   # 尾灯(マスク下部)
            v.A("t_sred").cyl((X(xe + ap * 0.45), s * 0.62, 1.34), (X(xe + ap * 0.45 + 0.05), s * 0.62, 1.34), 0.065, 0.065, seg=10)
            v.A("lampglass").cyl((X(xe + ap * 0.45), s * 0.95, 1.55), (X(xe + ap * 0.45 + 0.05), s * 0.95, 1.55), 0.07, 0.07, seg=10)
        v.A("t_steel").cyl((X(xe + ap * 0.6), -0.4, zwt - 0.1), (X(xe + ap * 0.6), -0.05, zws + 0.3), 0.011, 0.011, seg=5)
        if S.get("pano"):                                   # 縦に並ぶ小型LEDの前照灯(両端の柱)
            for s in (-1, 1):
                for k in range(3):
                    zz = zws + 0.35 + k * 0.42
                    v.A("black").box(*sorted((X(xe + 0.05), X(xe + 0.09))), s * (h - 0.07) - 0.045, s * (h - 0.07) + 0.045, zz - 0.07, zz + 0.07)
                    v.A("lamp_glow").box(*sorted((X(xe + 0.09), X(xe + 0.10))), s * (h - 0.07) - 0.035, s * (h - 0.07) + 0.035, zz - 0.05, zz + 0.05)
        return
    if fr == "bonnet":
        nl = nose
        # 長い角丸のボンネット(先端に向かって細く低く)
        secs = []
        for i in range(9):
            t = i / 8.0
            w = (h - 0.05) * (1 - 0.17 * t ** 1.4) * (1 - 0.30 * (t ** 6))
            ztop = 2.02 - 0.20 * t ** 1.2 - 0.18 * t ** 5
            zb = 0.98 + 0.10 * t ** 2
            secs.append((X(xe - 0.02 + nl * t), _sec(w, zb, ztop, 0.28 + 0.2 * t)))
        v.A(mask, 0.01, True).loft_x(secs)
        # 運転席窓: ボンネット後方の高い位置に3枚(パノラミック)
        for yc, wd in ((-0.92, 0.55), (0.0, 0.85), (0.92, 0.55)):
            sk = 0.16 if abs(yc) > 0.1 else 0.0
            a0 = (X(xe + 0.02), yc - wd / 2, 2.10); a1 = (X(xe + 0.02), yc + wd / 2, 2.10)
            b1 = (X(xe - 0.10), yc + wd / 2, zwt + 0.04); b0 = (X(xe - 0.10), yc - wd / 2, zwt + 0.04)
            _pane4(gl, a0, a1, b1, b0, t=0.02 * e, n=(1, 0, 0))
        for yp in (-0.5, 0.5):
            v.A(up, 0.004).box(*sorted((X(xe - 0.10), X(xe + 0.04))), yp - 0.04, yp + 0.04, 2.08, zwt + 0.05)
        v.A("t_ltdred", 0.01).box(*sorted((X(xe - 0.05), X(xe + 0.05))), -h, h, 1.85, 2.08)       # 窓下の赤帯
        # ボンネット先端の前照灯(2灯)+ヘッドマーク+エアホーンカバー
        for s in (-1, 1):
            v.A("black").cyl((X(xe + nl * 0.90), s * 0.62, 1.78), (X(xe + nl * 0.95), s * 0.62, 1.78), 0.18, 0.16, seg=16)
            v.A("lampglass").cyl((X(xe + nl * 0.95), s * 0.62, 1.78), (X(xe + nl * 0.955 + 0.02 * e), s * 0.62, 1.78), 0.135, 0.13, seg=16)
            v.A("t_ltdred").cyl((X(xe + nl * 0.93), s * 0.88, 1.36), (X(xe + nl * 0.94), s * 0.88, 1.36), 0.06, 0.06, seg=10)
        v.A("t_white").box(*sorted((X(xe + nl * 0.60), X(xe + nl * 0.60 + 0.03 * e))), -0.38, 0.38, 1.40, 1.76) if False else None
        pass  # ヘッドマーク掛けは _signs で
        v.A("t_ltdred", 0.01).box(*sorted((X(xe + nl * 0.99), X(xe + nl * 1.0)))  , -0.45, 0.45, 1.30, 1.42) if False else None
        # ボンネット側面のルーバー
        for s in (-1, 1):
            for k in range(6):
                xx = xe + 0.25 + k * 0.17
                v.A("black").box(*sorted((X(xx), X(xx + 0.06))), *sorted((s * (h - 0.05) * 0.98, s * (h - 0.05) * 1.0 + s * 0.012)), 1.45, 1.80) if False else None
        # 屋根前部の庇
        v.A(up, 0.006).box(*sorted((X(xe - 0.1), X(xe + 0.18))), -h + 0.2, h - 0.2, zwt + 0.04, zwt + 0.10)
        return
    if fr == "round":
        nl = nose
        # 下部: 丸い断面のマスク(先端へ細る)
        secs = []
        for i in range(9):
            t = i / 8.0
            w = (h - 0.02) * math.sqrt(max(0.02, 1 - t ** 2.2))
            ztop = zws + 0.02 - 0.08 * t
            secs.append((X(xe - 0.02 + nl * t), _sec(w, 0.94 + 0.12 * t, ztop, 0.18)))
        v.A(mask, 0.01, True).loft_x(secs)
        # 3枚窓: 中央は正面、左右は折れて回り込む
        xc = xe + nl * 0.84
        yc0 = 0.46
        gl2 = gl
        _pane4(gl2, (X(xc), -yc0, zws + 0.04), (X(xc), yc0, zws + 0.04), (X(xc - 0.10), yc0, zwt - 0.08), (X(xc - 0.10), -yc0, zwt - 0.08), t=0.02 * e, n=(1, 0, 0))
        for s in (-1, 1):
            xs_, ys_ = xe + nl * 0.15, h - 0.10
            _pane4(gl2, (X(xc), s * yc0, zws + 0.04), (X(xs_), s * ys_, zws + 0.04), (X(xs_ - 0.10), s * ys_, zwt - 0.08), (X(xc - 0.10), s * yc0, zwt - 0.08),
                   t=0.02 * e, n=(1, 0, 0))
            v.A(up, 0.004).box(*sorted((X(xc - 0.12), X(xc + 0.02))), s * yc0 - 0.04, s * yc0 + 0.04, zws, zwt)
        # 屋根の前方への張り出し(丸い帽子)
        secs = []
        for i in range(7):
            t = i / 6.0
            w = (h - 0.06) * math.sqrt(max(0.05, 1 - t ** 2.0))
            zb = zwt - 0.06
            ztp = zt + 0.04 + (zr - zt) * (1 - t ** 1.5) * 0.9 - 0.05 * t
            secs.append((X(xe - 0.02 + nl * 0.92 * t), _sec(w, zb, max(ztp, zb + 0.12), 0.24)))
        v.A(S["up"], 0.01, True).loft_x(secs)
        # 前照灯: 前面上部に1灯+窓下に2灯の丸目
        v.A("black").cyl((X(xc - 0.05), 0, zt + 0.12), (X(xc + 0.03), 0, zt + 0.12), 0.15, 0.14, seg=16)
        v.A("lampglass").cyl((X(xc + 0.03), 0, zt + 0.12), (X(xc + 0.05 * 1), 0, zt + 0.12), 0.115, 0.115, seg=16)
        for s in (-1, 1):
            v.A("black").cyl((X(xe + nl * 0.55), s * 0.72, 1.40), (X(xe + nl * 0.55 + 0.05), s * 0.72, 1.40), 0.11, 0.11, seg=14)
            v.A("lampglass").cyl((X(xe + nl * 0.55 + 0.05), s * 0.72, 1.40), (X(xe + nl * 0.55 + 0.065), s * 0.72, 1.40), 0.08, 0.08, seg=14)
            v.A("t_sred").cyl((X(xe + nl * 0.30), s * 1.12, 1.30), (X(xe + nl * 0.30 + 0.05), s * 1.12, 1.30), 0.06, 0.06, seg=10)
        v.A("t_gold").box(*sorted((X(xe + nl * 0.82), X(xe + nl * 0.82 + 0.02 * e))), -0.5, 0.5, 1.12, 1.17)    # 金色の飾り帯
        v.A("t_ivory").box(*sorted((X(xe + nl * 0.30), X(xe + nl * 0.30 + 0.01 * e)))   , -0.35, 0.35, 1.0, 1.04) if False else None
        return


def _gang(v, S, e, tot):
    """連結面(中間車の車端): 側壁+貫通路+幌。運転台はなし。"""
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    up = S["up"]
    xe = L / 2
    xa, xb = sorted((e * tot / 2, e * xe))
    for s in (-1, 1):
        wall_open(v, up, "y", xa, xb, s * (h - 0.08), s * h, zs, zw1,
                  [(*sorted((e * (tot / 2 + 0.35), e * (xe - 0.35))), zs + 0.45, zw1 - 0.2)])
        v.A("glass").box(*sorted((e * (tot / 2 + 0.35), e * (xe - 0.35))), *sorted((s * (h - 0.01), s * (h + 0.004))), zs + 0.45, zw1 - 0.2)
    v.A("t_grey").box(*sorted((e * tot / 2, e * xe)), -h + 0.08, h - 0.08, zfl, zfl + 0.02)
    # 妻面: 貫通路の開口(幅0.9×高さ1.9)を残した壁
    wall_open(v, S["lo"], "x", -h, h, e * xe - 0.10 * e, e * xe, zfl, zw1 + 0.05, [(-0.45, 0.45, zfl + 0.02, zfl + 1.95)])
    v.A("t_steel").box(*sorted((e * (xe - 0.05), e * (xe + 0.04))), -0.50, -0.45, zfl, zfl + 2.0)
    v.A("t_steel").box(*sorted((e * (xe - 0.05), e * (xe + 0.04))), 0.45, 0.50, zfl, zfl + 2.0)
    v.A("t_steel").box(*sorted((e * (xe - 0.05), e * (xe + 0.04))), -0.50, 0.50, zfl + 1.95, zfl + 2.0)
    # 貫通扉(ガラス窓つき・片側に引いた状態)
    v.A(S["door"], 0.004).box(*sorted((e * (xe - 0.07), e * (xe - 0.045))), -0.45, -0.02, zfl + 0.02, zfl + 1.95)
    v.A("glass").box(*sorted((e * (xe - 0.07), e * (xe - 0.055))), -0.38, -0.10, zfl + 1.0, zfl + 1.7)
    # 幌(ゴム)と渡り板
    for (y0, y1, z0, z1) in ((-0.60, -0.50, zfl - 0.05, zfl + 2.05), (0.50, 0.60, zfl - 0.05, zfl + 2.05)):
        v.A("black", 0.01).box(*sorted((e * xe, e * (xe + 0.27))), y0, y1, z0, z1)
    v.A("black", 0.01).box(*sorted((e * xe, e * (xe + 0.27))), -0.60, 0.60, zfl + 2.0, zfl + 2.07)
    v.A("t_steel").box(*sorted((e * (xe - 0.05), e * (xe + 0.30))), -0.45, 0.45, zfl - 0.04, zfl - 0.01)       # 渡り板
    coupler(v, e, e * (xe + 0.12))
    for s in (-1, 1):
        grab_rail(v, (e * (xe - 0.16), s * (h + 0.05), zfl + 0.10), (e * (xe - 0.16), s * (h + 0.05), zw1))


def _front(v, S, e, nose):
    _front0(v, S, e, nose)
    _signs(v, S, e, nose)


def _signs(v, S, e, nose):
    """前面の行先表示: roll=字幕式(方向幕) / sabo=行先板(サボ・吊り下げ式) / holder=ヘッドマーク掛け(板は未装着)。"""
    L, W = S["L"], S["W"]
    zfl, zs, zw1, zt, zr = S["z"]
    xe = L / 2
    fr, fs, tid = S["front"], S["fs"], S["id"]
    X = lambda a: e * a
    idx = (sum(map(ord, tid)) + int(e)) % 3
    if fr in ("flat", "subfront"):
        xp = xe + 0.03
        zc = 1.46
    elif fr == "vee":
        xp = xe + (0.55 if zr > 3.55 else 0.45) * 0.88 + 0.03
        zc = 1.46
    elif fr == "round":
        xp = xe + nose + 0.03
        zc = 1.34
    else:
        xp = xe + nose * 0.97
        zc = 1.62
    if fs == "sabo":
        v.A("t_steel").box(*sorted((X(xp - 0.03), X(xp + 0.004))), -0.30, 0.30, zc - 0.12, zc + 0.12)     # サボ受け(金具)
        v.end_plane(f"sabo_{tid}.png", e, 0.0, 0.52, zc - 0.10, zc + 0.10, X(xp + 0.006))
    elif fs == "holder" and fr == "vee":
        xa_ = xe + S.get("ap", 0.55) * 0.82 - S.get("rake", 0.0)
        v.A("t_steel").cyl((X(xa_ + 0.05), 0, zt + 0.40), (X(xa_ + 0.075), 0, zt + 0.40), 0.20, 0.20, seg=20)      # 掛け金具のリング
        v.A("t_bronze" if S["id"].startswith("lx_") else "t_white").cyl((X(xa_ + 0.075), 0, zt + 0.40), (X(xa_ + 0.082), 0, zt + 0.40), 0.17, 0.17, seg=20)     # 無地の板(未装着)
        v.A("t_steel").box(*sorted((X(xa_), X(xa_ + 0.06))), -0.04, 0.04, zt, zt + 0.26)
    elif fs == "holder" and fr == "bonnet":
        xa_ = xe + nose * 0.60
        zt_ = 1.92
        v.A("t_steel").cyl((X(xa_ - 0.01), 0, zt_), (X(xa_ + 0.03 * 1), 0, zt_), 0.25, 0.25, seg=20)
        v.A("t_white").cyl((X(xa_ + 0.03), 0, zt_), (X(xa_ + 0.037), 0, zt_), 0.21, 0.21, seg=20)


# --------------------------------------------------------------------------- roof, underframe
def _pant_diamond(v, x, zr, key="steel", wide=1.0):
    train2.pantograph(v, x, zr, key)


def _pant_sa(v, x, zr):
    """シングルアーム形パンタ(私鉄風)。"""
    v.A("t_ins").box(x - 0.3, x - 0.1, -0.4, 0.4, zr - 0.02, zr + 0.14)
    for s in (-1, 1):
        v.A("iron").cyl((x - 0.2, s * 0.35, zr + 0.14), (x - 0.2, s * 0.35, zr + 0.28), 0.06, 0.07, seg=8)
    v.A("steel").sbox((x - 0.2, 0, zr + 0.26), (x + 0.45, 0, zr + 0.78), 0.07, 0.07)
    v.A("steel").sbox((x + 0.45, 0, zr + 0.78), (x - 0.05, 0, zr + 1.15), 0.06, 0.06)
    v.A("black").box(x - 0.12, x - 0.02, -0.95, 0.95, zr + 1.13, zr + 1.18)
    v.A("steel").sbox((x - 0.2, 0.32, zr + 0.28), (x + 0.2, 0.0, zr + 0.34), 0.03, 0.03)


def _roof(v, S):
    L, W = S["L"], S["W"]
    zfl, zs, zw1, zt, zr = S["z"]
    px = S["pant_x"]
    rn = S["roof"]
    for it in rn:
        if it == "pant":
            _pant_diamond(v, px, zr)
        elif it == "pant2":
            _pant_diamond(v, -px, zr)
            v.A("black").box(px + 0.1, -px - 0.1, -0.015, 0.015, zr + 0.06, zr + 0.09) if False else None
        elif it == "pant_sa":
            _pant_sa(v, px, zr)
        elif it == "garland":       # ガーランド形ベンチレータ(長手1列)
            for x in (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5):
                v.A("roof", 0.008).cyl((x - 0.32, 0, zr - 0.01), (x + 0.32, 0, zr - 0.01), 0.14, 0.14, seg=10)
                v.A("t_grey").box(x - 0.34, x + 0.34, -0.015, 0.015, zr + 0.10, zr + 0.13)
        elif it == "tvent":
            for s in (-1, 1):
                for x in (-3.0, 3.0):
                    v.A("roof", 0.008).cyl((x - 0.2, s * 0.6, zr - 0.2), (x + 0.2, s * 0.6, zr - 0.2), 0.10, 0.10, seg=8)
        elif it == "radiator":      # 気動車: ラジエーター(屋根上・両端)+通風口
            for x in (-7.2, 7.2) if S["L"] > 15 else (-4.0, 4.0):
                v.A("roof", 0.015).box(x - 0.8, x + 0.8, -0.62, 0.62, zr - 0.08, zr + 0.16)
                v.A("dark").box(x - 0.7, x + 0.7, -0.57, 0.57, zr + 0.15, zr + 0.17)
                for k in range(7):
                    v.A("black").box(x - 0.76, x + 0.76, -0.60 + k * 0.2 - 0.01, -0.60 + k * 0.2 + 0.01, zr + 0.02, zr + 0.15)
        elif it == "exhaust":
            v.A("steel").cyl((-1.2, 0.0, zr - 0.04), (-1.2, 0.0, zr + 0.55), 0.09, 0.075, seg=10)
            v.A("black").cyl((-1.2, 0.0, zr + 0.55), (-1.2, 0.0, zr + 0.60), 0.10, 0.10, seg=10)
        elif it == "hybrid":        # ハイブリッド: 屋根上の蓄電池箱+冷房
            for x in (-1.5, 2.5):
                v.A("t_steel", 0.015).box(x - 1.0, x + 1.0, -0.6, 0.6, zr - 0.10, zr + 0.2)
                v.A("t_grey").box(x - 0.9, x + 0.9, -0.5, 0.5, zr + 0.2, zr + 0.23)
            v.A("t_orange").box(-2.6, -0.4, -0.6, 0.6, zr + 0.0, zr + 0.04) if False else None
        elif it == "torpedo":       # 魚雷形ベンチレータ
            for x in (-4.0, -1.6, 1.6, 4.0):
                v.A("roof", 0.01, True).sphere((x, 0, zr + 0.0), (0.38, 0.14, 0.12), seg=12, rings=6)
        elif it == "bigvent":       # 急行形の箱形ベンチレータ(大)
            for x in (-6.0, -2.0, 2.0):
                v.A("roof", 0.012).box(x - 0.55, x + 0.55, -0.32, 0.32, zr - 0.06, zr + 0.17)
                v.A("t_grey").box(x - 0.50, x + 0.50, -0.29, 0.29, zr + 0.17, zr + 0.19)
        elif it == "kvent":         # 食堂車: 厨房の排気煙突+大型換気
            v.A("steel").cyl((-6.2, 0.4, zr - 0.04), (-6.2, 0.4, zr + 0.42), 0.12, 0.10, seg=10)
            v.A("black").cyl((-6.2, 0.4, zr + 0.42), (-6.2, 0.4, zr + 0.48), 0.14, 0.14, seg=10)
            v.A("roof", 0.012).box(-7.6, -4.8, -0.5, 0.0, zr - 0.06, zr + 0.14)
            for x in (-3.0, 0.5, 4.0):
                v.A("roof", 0.01, True).sphere((x, 0, zr), (0.34, 0.14, 0.10), seg=12, rings=6)
        elif it == "gensetvent":    # 電源車: 大型ルーバー+機関室ベンチ+消音器
            v.A("roof", 0.015).box(-6.8, -1.0, -0.8, 0.8, zr - 0.08, zr + 0.20)
            for k in range(11):
                v.A("black").box(-6.6 + k * 0.5, -6.5 + k * 0.5, -0.75, 0.75, zr + 0.19, zr + 0.23)
            v.A("t_grey", 0.01).box(1.4, 3.6, -0.55, 0.55, zr - 0.06, zr + 0.28)
            v.A("steel").cyl((5.0, 0.0, zr - 0.04), (5.0, 0.0, zr + 0.70), 0.15, 0.12, seg=10)
            v.A("black").cyl((5.0, 0.0, zr + 0.70), (5.0, 0.0, zr + 0.76), 0.16, 0.16, seg=10)
        elif it == "duct":
            v.A("roof", 0.01).box(-8.2, 8.2, -0.05, 0.05, zr + 0.0, zr + 0.06)
        elif it == "acpod":         # 冷房用の箱(特急形)
            for x in (-5.5, -1.0, 3.5):
                v.A("t_cream", 0.02).box(x - 0.9, x + 0.9, -0.62, 0.62, zr - 0.10, zr + 0.28)
                v.A("t_grey").box(x - 0.8, x + 0.8, -0.52, 0.52, zr + 0.28, zr + 0.30)
                v.A("black").box(x - 0.85, x + 0.85, -0.60, -0.58, zr, zr + 0.2)
        elif it == "aerial":
            v.A("steel").cyl((-6.5, 0.5, zr), (-6.5, 0.5, zr + 0.32), 0.012, 0.01, seg=5)
            v.A("steel").cyl((-6.5, 0.5, zr + 0.32), (-5.9, 0.5, zr + 0.34), 0.008, 0.008, seg=5)
        elif it == "insul":         # 交流形: 屋根上の碍子と避雷器
            for i, x in enumerate((px + 1.6, px + 2.2, px + 2.8)):
                v.A("t_ins").cyl((x, 0.0, zr), (x, 0.0, zr + 0.36), 0.075, 0.09, seg=10)
                for k in range(4):
                    v.A("t_ins").cyl((x, 0.0, zr + 0.06 + k * 0.08), (x, 0.0, zr + 0.09 + k * 0.08), 0.115, 0.115, seg=10)
            v.A("iron", 0.01).box(px + 3.5, px + 5.4, -0.45, 0.45, zr - 0.04, zr + 0.45)   # 遮断器箱
        elif it == "hvcable":
            for s in (0,):
                v.A("black").cyl((px + 2.8, 0, zr + 0.36), (px + 3.5, 0, zr + 0.40), 0.018, 0.018, seg=5)
                v.A("black").cyl((px, 0, zr + 0.2), (px + 1.6, 0, zr + 0.34), 0.018, 0.018, seg=5)
        elif it == "pods":          # 私鉄形: キノコ形ベンチレータ
            for x in (-6.0, -3.2, -0.4, 2.4, 5.2):
                v.A("t_steel", 0.01, True).sphere((x, 0, zr - 0.03), (0.22, 0.22, 0.10), seg=12, rings=5)
                v.A("roof").cyl((x, 0, zr - 0.10), (x, 0, zr - 0.02), 0.07, 0.07, seg=8)
        elif it == "signbox":
            v.A("t_white", 0.01).box(-0.45, 0.45, -0.30, 0.30, zr, zr + 0.06) if False else None
        elif it == "ac_box":        # 地下鉄: 屋根上の冷房装置
            for x in (-5.4, -1.2):
                v.A("t_steel", 0.015).box(x - 1.2, x + 1.2, -0.55, 0.55, zr - 0.10, zr + 0.22)
                v.A("t_grey").box(x - 1.1, x + 1.1, -0.45, 0.45, zr + 0.22, zr + 0.25)
                for k in range(4):
                    v.A("black").box(x - 0.9 + k * 0.5, x - 0.8 + k * 0.5, -0.5, 0.5, zr + 0.05, zr + 0.2)
        elif it == "ac_box2":
            v.A("t_steel", 0.015).box(3.2, 4.6, -0.45, 0.45, zr - 0.10, zr + 0.16)
            for s in (-1, 1):
                v.A("t_grey").cyl((6.2, s * 0.4, zr - 0.05), (6.8, s * 0.4, zr - 0.05), 0.08, 0.08, seg=8)


def _under(v, S):
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    u = S["under"]
    zb = zfl - 0.12
    v.A("under", 0.01).box(-L / 2 + 0.4, L / 2 - 0.4, -h + 0.25, h - 0.25, zb - 0.06, zb)             # 床下梁
    if u == "boxes":
        for (x0, x1, y0, y1, zz) in ((-4.2, -1.2, -0.95, 0.30, 0.48), (1.0, 3.6, -0.40, 0.95, 0.46), (4.8, 6.2, -0.9, 0.9, 0.55)):
            v.A("iron", 0.01).box(x0, x1, y0, y1, zz, zb)
        v.A("steel").cyl((-7.0, 0.55, 0.62), (-5.0, 0.55, 0.62), 0.16, 0.16, seg=10)
        v.A("steel").cyl((-7.0, -0.55, 0.62), (-5.0, -0.55, 0.62), 0.16, 0.16, seg=10)
    elif u == "skirt":
        for s in (-1, 1):
            v.A(S["lo"], 0.01).box(-L / 2 + 1.2, L / 2 - 1.2, *sorted((s * (h - 0.25), s * (h - 0.22))), 0.50, zb)
            for i in range(5):
                x = -6.0 + i * 3.0
                v.A("under", 0.005).box(x - 0.01, x + 0.01, *sorted((s * (h - 0.28), s * (h - 0.21))), 0.50, zb)
        v.A("iron", 0.01).box(-1.0, 1.4, -0.5, 0.5, 0.40, zb)
    elif u == "skirtfull":
        for s in (-1, 1):
            v.A(S["lo"], 0.01).box(-L / 2 + 0.9, L / 2 - 0.9, *sorted((s * (h - 0.12), s * (h - 0.09))), 0.46, zb + 0.04)
        v.A("iron", 0.01).box(-2.0, 2.0, -0.5, 0.5, 0.42, zb)
    elif u == "engine":
        v.A("under", 0.01).box(-3.4, 0.9, -0.85, 0.85, 0.34, zb)                       # 燃料タンク
        v.A("iron", 0.01).box(1.8, 3.6, -0.9, 0.2, 0.40, zb)                         # 蓄電池箱
        v.A("iron", 0.01).box(-5.6, -4.2, -0.2, 0.9, 0.42, zb)
        v.A("black").cyl((-L * 0.34, 0, 0.90), (L * 0.34, 0, 0.90), 0.04, 0.04, seg=6)       # 推進軸
        for yy in (-0.5, 0.5):
            v.A("steel").cyl((4.3, yy, 0.50), (5.9, yy, 0.50), 0.14, 0.14, seg=10)
        v.A("steel").cyl((0.0, 0.0, 0.46), (1.8, 0.0, 0.46), 0.17, 0.17, seg=12)      # 排気管のマフラー
    elif u == "sleeper":       # 寝台車: 水タンク・蓄電池箱・ブレーキシリンダー
        v.A("iron", 0.01).box(-4.4, -1.6, -0.95, 0.95, 0.42, zb)
        v.A("under", 0.01).box(0.6, 3.4, -0.9, 0.6, 0.44, zb)
        v.A("iron", 0.01).box(4.6, 6.4, -0.8, 0.8, 0.48, zb)
        v.A("steel").cyl((-0.8, 0.5, 0.60), (0.4, 0.5, 0.60), 0.13, 0.13, seg=10)
    elif u == "gen":           # 電源車: 燃料タンク+発電機+消音器
        v.A("under", 0.01).box(-7.4, -2.4, -0.95, 0.95, 0.30, zb)
        v.A("iron", 0.01).box(-1.6, 2.0, -0.9, 0.9, 0.44, zb)
        v.A("steel").cyl((2.6, 0.0, 0.52), (5.6, 0.0, 0.52), 0.19, 0.19, seg=12)
        v.A("iron", 0.01).box(6.0, 7.6, -0.8, 0.8, 0.46, zb)
    elif u == "xfmr":
        v.A("iron", 0.012).box(-3.2, 0.8, -0.9, 0.9, 0.40, zb)             # 主変圧器
        for k in range(6):
            v.A("t_grey").box(-3.1 + k * 0.62, -2.85 + k * 0.62, -0.97, -0.9, 0.46, zb - 0.04)             # 放熱フィン
            v.A("t_grey").box(-3.1 + k * 0.62, -2.85 + k * 0.62, 0.9, 0.97, 0.46, zb - 0.04)
        v.A("iron", 0.01).box(2.2, 4.8, -0.6, 0.9, 0.46, zb)
        v.A("steel").cyl((5.5, 0.0, 0.56), (7.2, 0.0, 0.56), 0.16, 0.16, seg=10)
    kind, wb, r = S["bogie"]
    for x in (-L * 0.34, L * 0.34):
        if kind == "dt":
            bogie2(v, x, wb=wb, r=r)
        elif kind == "pedestal":
            bogie2(v, x, wb=wb, r=r, sideframe_h=0.38, key="black")
        elif kind == "air":
            with v.part("bogie", (x, 0.0, 0.0), axis="z"):
                TK._bogie2(v, x, wb, r, 0.24, "iron")
                for s in (-1, 1):                                    # 大きな空気ばね(ゴム製ベローズ)
                    v.A("rubber", 0.01).cyl((x, s * 0.58, r + 0.14), (x, s * 0.58, r + 0.46), 0.17, 0.15, seg=14)
                    v.A("steel").cyl((x, s * 0.58, r + 0.46), (x, s * 0.58, r + 0.54), 0.19, 0.19, seg=14)
            v.meta["bogies"].append(dict(x=round(float(x), 3), wheelbase=wb, wheel_r=r, axles=2))

TYPES.update({
    "sl_b": dict(
        title="国鉄寝台客車 B寝台(開放式・2段)", L=21.0, W=2.90, z=(1.20, 1.90, 2.66, 3.06, 3.66), cab=1.10, zb0=0.95,
        fs="holder", ss="sabo", ds="deck", ps="beads", wc=(0.05, 0.05), liner="t_cream", lamp="tube",
        lo="t_navy", up="t_navy", door="t_navy", mask="t_navy", stripe=[("t_ivory", 2.74, 2.86), ("t_ivory", 1.86, 1.94)],
        pattern="D w15 D", pattern2="D w11 D", door_w=0.85, win="wide", pillar=0.09,
        front="flat", screens=0, lamps="belt", roofshape="round", rake=0.0,
        roof=["torpedo", "duct"], pant_x=0.0, bogie=("dt", 2.4, 0.43), under="sleeper",
        seat="t_moq_b", interior="bunk", standing=False),
    "sl_a": dict(
        title="国鉄寝台客車 A寝台(個室・廊下側窓)", L=21.0, W=2.90, z=(1.20, 1.90, 2.66, 3.06, 3.66), cab=1.10, zb0=0.95,
        fs="holder", ss="sabo", ds="deck", ps="lap", wc=(0.02, 0.02), liner="t_wood", lamp="globe",
        lo="t_navy", up="t_navy", door="t_navy", mask="t_navy", stripe=[("t_gold", 2.74, 2.80), ("t_ivory", 1.86, 1.92), ("t_ivory", 2.66, 2.70)],
        pattern="D w16 D", pattern2="D w8 D", door_w=0.85, win="sash2", pillar=0.11,
        front="flat", screens=0, lamps="belt", roofshape="round", rake=0.0,
        roof=["bigvent", "duct"], pant_x=0.0, bogie=("air", 2.5, 0.43), under="sleeper",
        seat="t_moq_r", interior="compart", standing=False),
    "sl_din": dict(
        title="国鉄食堂車(厨房・大窓・煙突)", L=21.0, W=2.90, z=(1.20, 1.90, 2.62, 3.06, 3.68), cab=1.10, zb0=0.95,
        fs="holder", ss="sabo", ds="deck", ps="smooth", wc=(0.12, 0.12), liner="t_cream", lamp="strip",
        lo="t_navy", up="t_navy", door="t_navy", mask="t_navy", stripe=[("t_ltdred", 2.70, 2.82), ("t_ivory", 1.86, 1.94)],
        pattern="D s w7 D", pattern2="D s w7 D", door_w=0.85, win="arch", pillar=0.16,
        front="flat", screens=0, lamps="belt", roofshape="round", rake=0.0,
        roof=["acpod", "kvent"], pant_x=0.0, bogie=("air", 2.5, 0.43), under="sleeper",
        seat="t_moq_r", interior="dining", standing=False),
    "sl_gen": dict(
        title="国鉄電源荷物車(発電機・ルーバー)", L=21.0, W=2.90, z=(1.20, 1.90, 2.66, 3.06, 3.66), cab=1.10, zb0=0.95, diesel=True,
        fs="holder", ss="sabo", ds="deck", ps="weld", wc=(0.02, 0.02), liner="t_grey", lamp="globe",
        lo="t_navy", up="t_navy", door="t_navy", mask="t_navy", stripe=[("t_ivory", 1.86, 1.94)],
        pattern="D s s s s s s s s s s s s s s s s s s D", door_w=0.85, win="pair", pillar=0.12, louver=True,
        front="flat", screens=0, lamps="belt", roofshape="round", rake=0.0,
        roof=["gensetvent", "exhaust"], pant_x=0.0, bogie=("dt", 2.4, 0.43), under="gen",
        seat="t_moq_k", interior="genset", standing=False),
})

TYPES.update({
    "tram_o": dict(
        title="大湊市電 600形(両運転台・2扉・丸屋根)", L=12.6, W=2.45, z=(0.62, 0.80, 2.12, 2.34, 2.84), cab=1.30, zb0=0.60,
        fs="sabo", ss="sabo", ds="bus", ps="beads", wc=(0.20, 0.20), liner="t_wood", lamp="globe",
        lo="t_green", up="t_cream", door="t_green", mask="t_green", stripe=[("t_gold", 0.68, 0.74), ("t_gold", 2.15, 2.19)],
        pattern="w3 D w3 D w3", door_w=1.10, win="single", pillar=0.09,
        front="round", screens=3, lamps="round", roofshape="round", nose=0.22,
        roof=["pant_sa", "pods"], pant_x=-3.4, bogie=("dt", 1.6, 0.33), under="boxes",
        seat="t_wood", interior="long", standing=False),
})

_LUX = dict(
    fs="holder", ss="none", ds="lux", ps="smooth", wc=(0.14, 0.14), lamp="globe", liner="t_wood",
    lo="t_bronze", up="t_champ", door="t_bronze", mask="t_bronze", pillar=0.10,
    front="vee", screens=2, lamps="led", roofshape="round", rake=0.30, pant_x=2.0,
    bogie=("air", 2.5, 0.43), under="skirtfull", seat="t_leat", standing=False, diesel=True,
)
TYPES.update({
    "lx_obs": dict(_LUX, title="周遊列車「結」展望スイート(パノラマ前面・発電機)", L=21.0, W=2.95, z=(1.20, 1.45, 2.78, 3.12, 3.74), cab=2.4, zb0=0.9,
        stripe=[("t_champ", 1.08, 1.16), ("t_champ", 2.84, 2.90)], pano=True, ap=0.95, rake=0.55, mask="black",
        pattern="D w7 D", pattern2="D w5 D", win="grand", door_w=0.95, roof=["hybrid", "acpod"], interior="lux_obs", under="gen"),
    "lx_ste": dict(_LUX, title="周遊列車「結」スイート(1両3室・廊下側は小窓)", L=21.0, W=2.95, z=(1.20, 1.45, 2.78, 3.12, 3.74), cab=1.1, zb0=0.9,
        stripe=[("t_champ", 1.08, 1.16), ("t_champ", 2.84, 2.90)],
        pattern="D w16 D", pattern2="D w9 D", win="square", win2="grand", door_w=0.95, roof=["hybrid", "aerial"], interior="lux_ste"),
    "lx_lng": dict(_LUX, title="周遊列車「結」ラウンジ「結の間」(床まで大窓・唯一の乗降口)", L=21.0, W=2.95, z=(1.20, 1.38, 2.80, 3.12, 3.74), cab=1.1, zb0=0.9,
        stripe=[("t_champ", 1.04, 1.12), ("t_champ", 2.86, 2.92)], lamp="strip",
        pattern="w4 D w4", pattern2="w4 D w4", win="grand", door_w=1.10, roof=["acpod", "aerial"], interior="lux_lng"),
    "lx_din": dict(_LUX, title="周遊列車「結」ダイニング「穂波膳」(大窓・ライブキッチン)", L=21.0, W=2.95, z=(1.20, 1.38, 2.80, 3.12, 3.74), cab=1.1, zb0=0.9,
        stripe=[("t_champ", 1.04, 1.12), ("t_ltdred", 2.86, 2.92)],
        pattern="D w8 D", pattern2="D w8 D", win="grand", door_w=0.95, roof=["acpod", "kvent"], interior="lux_din"),
    "lx_grn": dict(_LUX, title="周遊列車「結」特別スイート(メゾネット・檜風呂)", L=21.0, W=2.95, z=(1.20, 1.45, 2.80, 3.12, 3.74), cab=1.1, zb0=0.9,
        stripe=[("t_champ", 1.08, 1.30), ("t_champ", 2.84, 2.90)],
        pattern="D w10 D", pattern2="D w4 D", win="square", win2="grand", door_w=0.95, roof=["hybrid", "acpod"], interior="lux_grn"),
})


# --------------------------------------------------------------------------- interior
def _rider(v, x, y, zfl, ang=0.0, seated=True, kind=None, rnd=None):
    rnd = rnd or random
    c = kind or rnd.choice(["cl1", "cl2", "cl3", "cl4"])
    if seated:
        v.A(c, 0.02, True).box(x - 0.12, x + 0.12, y - 0.17, y + 0.17, zfl + 0.45, zfl + 0.95)      # 胴
        v.A(c, 0.02, True).box(x + 0.10, x + 0.50 * (1 if ang == 0 else -1) * 0.8, y - 0.16, y - 0.04, zfl + 0.50, zfl + 0.64)
        v.A("skin", 0.0, True).sphere((x + 0.02, y, zfl + 1.08), (0.082, 0.072, 0.10), seg=8, rings=6)
        v.A("hair", 0.0, True).sphere((x - 0.012, y, zfl + 1.11), (0.088, 0.078, 0.088), seg=8, rings=5)
    else:
        v.A(c, 0.02, True).box(x - 0.13, x + 0.13, y - 0.19, y + 0.19, zfl + 0.85, zfl + 1.45)
        v.A(c, 0.02, True).box(x - 0.09, x + 0.09, y - 0.15, y - 0.02, zfl + 0.0, zfl + 0.85)
        v.A(c, 0.02, True).box(x - 0.09, x + 0.09, y + 0.02, y + 0.15, zfl + 0.0, zfl + 0.85)
        v.A("skin", 0.0, True).sphere((x, y, zfl + 1.58), (0.085, 0.075, 0.105), seg=8, rings=6)
        v.A("hair", 0.0, True).sphere((x - 0.012, y, zfl + 1.61), (0.09, 0.08, 0.09), seg=8, rings=5)


def _door_zones(bays, tot, dw):
    x = -tot / 2
    zones = []
    for kind, w in bays:
        if kind in ("D", "s"):
            zones.append((x - 0.1, x + w + 0.1))
        x += w
    return zones


def _segments(tot, zones):
    """ドア区間を除いた座席区間 [(a,b)]。"""
    segs = []
    cur = -tot / 2 + 0.05
    for a, b in sorted(zones):
        if a - cur > 0.5:
            segs.append((cur, a))
        cur = max(cur, b)
    if tot / 2 - 0.05 - cur > 0.5:
        segs.append((cur, tot / 2 - 0.05))
    return segs


def _interior(v, S, tot, bays, seed):
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    rnd = random.Random(seed)
    st = S["interior"]
    seat = S["seat"]
    zones = _door_zones(bays, tot, S["door_w"])
    segs = _segments(tot, zones)
    cl = ["cl1", "cl2", "cl3", "cl4"]
    ax = tot / 2 - 0.05
    floor = "t_lino2" if st in ("cross", "recline", "box") else "t_lino"
    v.A(floor).box(-ax, ax, -h + 0.08, h - 0.08, zfl, zfl + 0.02)
    if st == "recline":
        v.A("t_moq_r").box(-ax + 0.1, ax - 0.1, -0.22, 0.22, zfl + 0.02, zfl + 0.025)    # 通路のカーペット
    # 内張り(窓下)・天井・照明(形式ごとに違う)
    lk = S.get("liner", "t_white")
    for s_ in (-1, 1):
        v.A(lk).box(-ax, ax, *sorted((s_ * (h - 0.082), s_ * (h - 0.092))), zfl + 0.02, zs)
    v.A(lk if st != "recline" else "t_cream").box(-ax, ax, -h + 0.08, h - 0.08, zw1 - 0.03, zw1 - 0.02)
    lamp = v.A("lamp_in")
    ls = S.get("lamp", "tube")
    if ls == "tube":           # 長手2列の蛍光灯(カバー付き)
        for s_ in (-1, 1):
            lamp.box(-ax, ax, *sorted((s_ * 0.50, s_ * 0.68)), zw1 - 0.02, zw1)
            for i in range(int(2 * ax / 1.2) + 1):
                v.A("t_white").box(-ax + i * 1.2 - 0.02, -ax + i * 1.2 + 0.02, *sorted((s_ * 0.48, s_ * 0.70)), zw1 - 0.035, zw1 - 0.015)
    elif ls == "strip":        # 中央の連続した間接照明帯
        lamp.box(-ax, ax, -0.20, 0.20, zw1 - 0.02, zw1)
        for s_ in (-1, 1):
            v.A("t_white").box(-ax, ax, *sorted((s_ * 0.20, s_ * 0.24)), zw1 - 0.045, zw1 - 0.02)
    else:                      # 丸いグローブ灯(白熱球風)を一定間隔で
        for i in range(int(2 * ax / 1.6)):
            x = -ax + 0.8 + i * 1.6
            for s_ in (-1, 1):
                v.A("lamp_in").sphere((x, s_ * 0.55, zw1 - 0.10), (0.085, 0.085, 0.085), seg=10, rings=6)
                v.A("steel").cyl((x, s_ * 0.55, zw1 - 0.02), (x, s_ * 0.55, zw1 - 0.06), 0.012, 0.012, seg=5)
    if st in ("bunk", "compart", "dining", "genset"):
        _sleep_inside(v, S, tot, bays, segs, zones, rnd)
        return
    if st.startswith("lux_"):
        _lux_inside(v, S, tot, bays, segs, zones, rnd)
        return
    if st in ("long", "mix", "cross"):
        n = int((2 * ax) / 2.4)
        for i in range(n):                   # 扇風機(扇風機は私鉄/近郊/通勤に)
            x = -ax + 1.2 + i * 2.4
            v.A("steel").cyl((x, 0, zw1 - 0.03), (x, 0, zw1 - 0.12), 0.02, 0.02, seg=6)
            v.A("t_grey").cyl((x - 0.002, 0, zw1 - 0.14), (x + 0.002, 0, zw1 - 0.14), 0.19, 0.19, seg=12)
            v.A("steel").cyl((x - 0.05, 0, zw1 - 0.14), (x + 0.05, 0, zw1 - 0.14), 0.02, 0.02, seg=6)
    # ---------------- 座席
    if st in ("long", "subway") or st == "mix":
        for ai, (a, b) in enumerate(segs):
            lng = (st in ("long", "subway")) or (st == "mix" and ai % 2 == 1) or (st == "mix" and len(segs) == 1)
            for s in (-1, 1):
                if lng:       # ロングシート
                    v.A(seat, 0.015).box(a, b, *sorted((s * (h - 0.09), s * (h - 0.58))), zfl + 0.02, zfl + 0.42)
                    v.A(seat, 0.015).box(a, b, *sorted((s * (h - 0.09), s * (h - 0.16))), zfl + 0.42, zfl + 0.88)
                    v.A("t_steel" if st == "subway" else "t_grey").box(a, a + 0.03, *sorted((s * (h - 0.09), s * (h - 0.58))), zfl + 0.02, zfl + 0.98)   # 袖仕切
                    v.A("t_steel" if st == "subway" else "t_grey").box(b - 0.03, b, *sorted((s * (h - 0.09), s * (h - 0.58))), zfl + 0.02, zfl + 0.98)
                    # 乗客
                    k = int((b - a) / 0.5)
                    for j in range(k):
                        if rnd.random() < (0.55 if S.get("standing") else 0.35):
                            _rider(v, a + 0.25 + j * 0.5, s * (h - 0.36), zfl, 0.0 if s > 0 else 3.14, True, rnd=rnd)
                else:         # ボックス席(向かい合わせ)
                    m = int((b - a) / 1.55)
                    m = max(1, m)
                    pitch = (b - a) / m
                    for j in range(m):
                        xc = a + pitch * (j + 0.5)
                        for sg in (-1, 1):
                            xx = xc + sg * 0.50
                            v.A(seat, 0.015).box(xx - 0.24, xx + 0.24, *sorted((s * (h - 0.09), s * (h - 0.56))), zfl + 0.02, zfl + 0.42)
                            v.A(seat, 0.015).box(xx + sg * 0.22 - 0.045, xx + sg * 0.22 + 0.045, *sorted((s * (h - 0.09), s * (h - 0.56))), zfl + 0.42, zfl + 0.98)
                        v.A("t_wood").box(xc - 0.22, xc + 0.22, *sorted((s * (h - 0.09), s * (h - 0.30))), zfl + 0.70, zfl + 0.725)  # 窓台
                        if rnd.random() < 0.45:
                            _rider(v, xc + 0.50, s * (h - 0.32), zfl, 0.0, True, rnd=rnd)
                        if rnd.random() < 0.3:
                            _rider(v, xc - 0.50, s * (h - 0.32), zfl, 3.14, True, rnd=rnd)
    elif st in ("box", "cross", "recline"):
        whole = [(-ax + 0.1, ax - 0.1)] if st != "box" else segs
        for (a, b) in (segs if st != "box" else segs):
            if st == "box":
                m = max(1, int((b - a) / 1.52))
                pitch = (b - a) / m
                for j in range(m):
                    xc = a + pitch * (j + 0.5)
                    for s in (-1, 1):
                        for sg in (-1, 1):                             # 向かい合う2席(窓側+通路側)
                            xx = xc + sg * 0.50
                            for yy in (h - 0.38, 0.62):
                                v.A(seat, 0.02).box(xx - 0.22, xx + 0.22, *sorted((s * (yy - 0.20), s * (yy + 0.20))), zfl + 0.02, zfl + 0.42)
                            v.A(seat, 0.02).box(xx + sg * 0.20 - 0.04, xx + sg * 0.20 + 0.04, *sorted((s * 0.40, s * (h - 0.10))), zfl + 0.42, zfl + 1.05)
                        v.A("t_wood").box(xc - 0.20, xc + 0.20, *sorted((s * (h - 0.09), s * (h - 0.34))), zfl + 0.70, zfl + 0.73)
                        v.A("steel").box(xc - 0.01, xc + 0.01, *sorted((s * (h - 0.30), s * (h - 0.31))), zfl + 0.02, zfl + 0.70)
                        if rnd.random() < 0.5:
                            _rider(v, xc + 0.5, s * (h - 0.38), zfl, 0.0, True, rnd=rnd)
                        if rnd.random() < 0.35:
                            _rider(v, xc - 0.5, s * 0.62, zfl, 3.14, True, rnd=rnd)
            else:
                pitch = 1.0 if st == "recline" else 0.95
                m = int((b - a) / pitch)
                for j in range(m):
                    x = a + (j + 0.5) * (b - a) / m
                    for s in (-1, 1):
                        for yy in (0.44, 1.02) if st == "recline" else (0.40, 0.98):
                            cy = s * yy
                            v.A(seat, 0.025).box(x - 0.22, x + 0.22, cy - 0.26, cy + 0.26, zfl + 0.02, zfl + 0.40)
                            sbk = v.A(seat, 0.03)
                            if st == "recline":
                                sbk.sbox((x - 0.20, cy, zfl + 0.40), (x - 0.34, cy, zfl + 1.10), 0.52, 0.10)       # 傾いた背もたれ
                                v.A("t_white", 0.01).box(x - 0.40, x - 0.32, cy - 0.15, cy + 0.15, zfl + 0.86, zfl + 1.10)   # ヘッドレストカバー
                                v.A("t_grey").box(x + 0.0, x + 0.2, cy - 0.23, cy - 0.21, zfl + 0.45, zfl + 0.70) if False else None
                            else:
                                sbk.box(x - 0.30, x - 0.22, cy - 0.26, cy + 0.26, zfl + 0.40, zfl + 0.98)
                            if rnd.random() < 0.28:
                                _rider(v, x - 0.02, cy, zfl, 0.0, True, rnd=rnd)
                    # 肘掛け
                    for s in (-1, 1):
                        v.A("t_grey").box(x - 0.2, x + 0.2, s * 0.70 - 0.02, s * 0.70 + 0.02, zfl + 0.40, zfl + 0.58) if False else None
        if st in ("recline",):
            for s in (-1, 1):                                            # 荷棚(蓋つきのカバー)
                v.A("t_cream", 0.01).box(-ax, ax, *sorted((s * (h - 0.09), s * (h - 0.46))), zw1 - 0.34, zw1 - 0.30)
                v.A("t_gold").box(-ax, ax, *sorted((s * (h - 0.46), s * (h - 0.47))), zw1 - 0.34, zw1 - 0.20)
                v.A("t_cream", 0.01).box(-ax, ax, *sorted((s * (h - 0.09), s * (h - 0.10))), zw1 - 0.34, zw1 - 0.18)
    # ---------------- 荷棚・吊り革・手すり・車内広告
    if st not in ("recline",):
        for s in (-1, 1):
            if st == "subway":
                v.A("t_steel").box(-ax, ax, *sorted((s * (h - 0.09), s * (h - 0.22))), zw1 - 0.30, zw1 - 0.28)     # 網棚(ステンレス)
                for i in range(int(2 * ax / 0.12)):
                    pass
            else:
                v.A("steel").box(-ax, ax, *sorted((s * (h - 0.09), s * (h - 0.42))), zw1 - 0.30, zw1 - 0.285)         # 網棚
                for i in range(int(2 * ax / 0.8) + 1):
                    xx = -ax + i * 0.8
                    v.A("steel").box(xx - 0.008, xx + 0.008, *sorted((s * (h - 0.09), s * (h - 0.42))), zw1 - 0.30, zw1 - 0.22)
    if st in ("long", "mix", "subway") or S.get("standing"):
        for s in (-1, 1):
            v.A("t_steel" if st == "subway" else "steel").cyl((-ax, s * 0.52, zw1 - 0.12), (ax, s * 0.52, zw1 - 0.12), 0.013, 0.013, seg=6)   # つり革レール
        pitch = 0.58 if st in ("long", "subway") else 0.8
        n = int(2 * ax / pitch)
        for i in range(n):
            x = -ax + 0.3 + i * pitch
            for s in (-1, 1):
                if any(a < x < b for a, b in zones):
                    continue
                v.A("black").cyl((x, s * 0.52, zw1 - 0.12), (x, s * 0.52, zw1 - 0.34), 0.004, 0.004, seg=4)
                v.A("t_white" if st != "subway" else "t_sred").torus((x, s * 0.52, zw1 - 0.40), "x", 0.045, 0.007, segR=10, segr=4)
        for a, b in zones:                                              # ドア脇の縦手すり
            for s in (-1, 1):
                for xx in (a + 0.1, b - 0.1):
                    v.A("t_pole").cyl((xx, s * (h - 0.62), zfl), (xx, s * (h - 0.62), zw1 - 0.02), 0.019, 0.019, seg=8)
        if st == "subway":
            for (a, b) in zones:                                        # 路線図/ドア上の表示器
                for s in (-1, 1):
                    v.A("black").box(a + 0.3, b - 0.3, *sorted((s * (h - 0.09), s * (h - 0.11))), zw1 - 0.20, zw1 - 0.06)
                    v.A("lamp_glow").box(a + 0.34, b - 0.34, *sorted((s * (h - 0.11), s * (h - 0.112))), zw1 - 0.17, zw1 - 0.09)
    if st in ("long", "mix"):
        for i in range(int(2 * ax / 1.5)):                              # 中吊り広告
            x = -ax + 0.9 + i * 1.5
            if not any(a < x < b for a, b in zones):
                v.A("t_panel").box(x - 0.30, x + 0.30, -0.003, 0.003, zw1 - 0.54, zw1 - 0.40) if False else None
    # 立ち客
    if S.get("standing"):
        for s in (-1, 1):
            x = -ax + 0.7 + rnd.random() * 0.4
            while x < ax - 0.5:
                if not any(a < x < b for a, b in zones) and rnd.random() < 0.38:
                    _rider(v, x, s * 0.52 + rnd.uniform(-0.08, 0.08), zfl, 0.0, False, rnd=rnd)
                x += rnd.uniform(1.3, 2.4)
    # 車端の幌まわり: 妻面の貫通扉
    for e in (-1, 1):
        pass

def _sleep_inside(v, S, tot, bays, segs, zones, rnd):
    """寝台車・食堂車・電源車の室内。通路は +y 側、寝台/個室は -y 側。"""
    h = S["W"] / 2
    zfl, zs, zw1, zt, zr = S["z"]
    st = S["interior"]
    ax = tot / 2 - 0.05
    ya, yb = -h + 0.12, 0.50              # 寝台側の奥行 (≒1.8m)
    if st == "bunk":
        for (a, b) in segs:
            m = max(1, int((b - a) / 0.78))
            p = (b - a) / m
            for j in range(m):
                xc = a + p * (j + 0.5)
                v.A("t_blank", 0.02).box(xc - 0.34, xc + 0.34, ya + 0.02, yb, zfl + 0.40, zfl + 0.58)       # 下段マットレス
                v.A("t_curt", 0.03).box(xc - 0.33, xc + 0.33, ya + 0.04, yb - 0.02, zfl + 0.50, zfl + 0.62)    # 毛布
                v.A("t_white", 0.03).box(xc - 0.26, xc + 0.26, ya + 0.04, ya + 0.32, zfl + 0.62, zfl + 0.70)   # 枕
                v.A("t_blank", 0.02).box(xc - 0.34, xc + 0.34, ya + 0.02, yb, zfl + 1.38, zfl + 1.54)      # 上段
                v.A("t_curt", 0.03).box(xc - 0.33, xc + 0.33, ya + 0.04, yb - 0.02, zfl + 1.48, zfl + 1.58)
                v.A("t_white", 0.03).box(xc - 0.26, xc + 0.26, ya + 0.04, ya + 0.32, zfl + 1.58, zfl + 1.66)
                if j % 2 == 1:                                                                             # 区画の仕切り
                    v.A("t_wood").box(xc - p / 2 - 0.015, xc - p / 2 + 0.015, ya + 0.02, yb, zfl + 0.02, zfl + 1.75)
                if rnd.random() < 0.6:                                                                      # 通路側のカーテン(半分閉)
                    k = rnd.choice((0.0, 0.5))
                    v.A("t_curt", 0.01).box(xc - 0.33 + k * 0.5, xc + 0.33, yb, yb + 0.02, zfl + 0.30, zfl + 1.80)
            for s_ in (a, b):
                v.A("t_wood").box(s_ - 0.015, s_ + 0.015, ya + 0.02, yb, zfl + 0.02, zfl + 1.75)
        for (a, b) in segs:                                                                                 # 通路側の窓下: 補助席と小テーブル
            for xx in range(int((b - a) / 1.56)):
                x = a + 0.78 + xx * 1.56
                v.A("t_moq_b", 0.02).box(x - 0.2, x + 0.2, h - 0.38, h - 0.10, zfl + 0.40, zfl + 0.46)
                v.A("t_wood").box(x - 0.2, x + 0.2, h - 0.28, h - 0.09, zfl + 0.70, zfl + 0.73)
    elif st == "compart":
        for (a, b) in segs:
            m = max(1, int((b - a) / 2.05))
            p = (b - a) / m
            for j in range(m + 1):
                xw = a + p * j
                v.A("t_cream").box(xw - 0.02, xw + 0.02, ya, yb, zfl + 0.02, zw1 - 0.03)                    # 個室の仕切壁
            for j in range(m):
                xc = a + p * (j + 0.5)
                v.A("t_wood", 0.01).box(xc - 0.40, xc + 0.40, yb - 0.04, yb, zfl + 0.02, zw1 - 0.25)         # 引き戸
                v.A("glass").box(xc - 0.22, xc + 0.22, yb - 0.04, yb - 0.02, zfl + 1.30, zfl + 1.80)
                v.A("t_gold").box(xc + 0.28, xc + 0.34, yb, yb + 0.03, zfl + 0.95, zfl + 1.05)
                v.A("t_moq_r", 0.03).box(xc - 0.55, xc + 0.55, ya + 0.02, ya + 0.60, zfl + 0.40, zfl + 0.82)  # 長手の下段寝台(座席状態)
                v.A("t_moq_r", 0.03).box(xc - 0.55, xc + 0.55, ya + 0.02, ya + 0.14, zfl + 0.82, zfl + 1.45)
                v.A("t_blank", 0.02).box(xc - 0.55, xc + 0.55, ya + 0.02, yb - 0.10, zfl + 1.62, zfl + 1.72)  # 折畳みの上段
                v.A("t_wood").box(xc - 0.25, xc + 0.25, ya + 0.02, ya + 0.40, zfl + 0.72, zfl + 0.75)         # 窓台テーブル
                v.A("t_gold").cyl((xc, ya + 0.20, zfl + 0.75), (xc, ya + 0.20, zfl + 0.98), 0.03, 0.045, seg=8)  # スタンド
        v.A("t_moq_r").box(-ax, ax, h - 0.80, h - 0.12, zfl + 0.02, zfl + 0.03)                                # 廊下の絨毯
        for s_ in (h - 0.14,):
            v.A("t_gold").cyl((-ax, s_, zfl + 0.98), (ax, s_, zfl + 0.98), 0.014, 0.014, seg=6)               # 窓際の手すり
    elif st == "dining":
        kx = -tot / 2 + 4.4                                                                                 # 厨房: x<kx
        v.A("t_steel").box(-ax, kx - 0.1, -0.30, 0.30, zfl + 0.02, zfl + 0.90)                              # 調理台
        v.A("black").box(-ax + 0.4, -ax + 1.4, -0.28, 0.28, zfl + 0.90, zfl + 0.94)
        for k in range(3):
            v.A("t_steel").box(-ax + 0.2, -ax + 0.5, h - 0.65 - k * 0.0, h - 0.12, zfl + 0.02 + k * 0.7, zfl + 0.68 + k * 0.7)
        v.A("t_cream").box(kx - 0.05, kx, -h + 0.08, h - 0.08, zfl + 0.02, zw1 - 0.03)                     # 配膳口のある仕切壁
        v.A("t_cream").box(kx - 0.05, kx, -h + 0.08, -0.45, zfl + 0.02, zw1 - 0.03)
        for x in [kx + 0.9 + i * 1.62 for i in range(int((tot / 2 - kx - 1.4) / 1.62) + 1)]:
            for s_ in (-1, 1):
                yy = s_ * (h - 0.72)
                v.A("t_white", 0.01).box(x - 0.42, x + 0.42, yy - 0.34, yy + 0.34, zfl + 0.72, zfl + 0.745)    # テーブルクロス
                v.A("t_gold").cyl((x, yy, zfl + 0.745), (x, yy, zfl + 0.80), 0.03, 0.012, seg=8)
                v.A("lamp_glow").sphere((x, yy, zfl + 0.85), (0.045, 0.045, 0.06), seg=10, rings=6)           # 卓上ランプ
                v.A("steel").cyl((x, yy, zfl + 0.02), (x, yy, zfl + 0.72), 0.03, 0.03, seg=6)
                for sg in (-1, 1):
                    v.A("t_moq_r", 0.025).box(x + sg * 0.62 - 0.19, x + sg * 0.62 + 0.19, yy - 0.2, yy + 0.2, zfl + 0.02, zfl + 0.44)
                    v.A("t_moq_r", 0.025).box(x + sg * 0.80 - 0.03, x + sg * 0.80 + 0.03, yy - 0.2, yy + 0.2, zfl + 0.44, zfl + 1.0)
                    if rnd.random() < 0.45:
                        _rider(v, x + sg * 0.62, yy, zfl, 0.0 if sg < 0 else 3.14, True, rnd=rnd)
        v.A("t_moq_r").box(kx, ax, -0.32, 0.32, zfl + 0.02, zfl + 0.03)                                    # 通路の絨毯
    else:   # genset
        v.A("iron", 0.02).box(-ax + 1.0, -ax + 4.4, -0.85, 0.85, zfl + 0.05, zfl + 1.45)                   # ディーゼル機関
        for k in range(6):
            v.A("steel").cyl((-ax + 1.4 + k * 0.5, 0, zfl + 1.45), (-ax + 1.4 + k * 0.5, 0, zfl + 1.75), 0.10, 0.10, seg=8)
        v.A("iron", 0.02).box(-ax + 4.4, -ax + 6.2, -0.7, 0.7, zfl + 0.05, zfl + 1.15)                     # 発電機
        v.A("t_warn").box(-ax + 6.8, -ax + 7.6, h - 0.5, h - 0.12, zfl + 0.02, zfl + 1.7)                  # 配電盤
        v.A("t_grey").box(-ax + 8.4, ax - 0.6, -0.6, 0.9, zfl + 0.02, zfl + 0.9)                            # 荷物室の荷
        v.A("t_wood").box(-ax + 8.6, ax - 0.9, -0.5, 0.7, zfl + 0.9, zfl + 1.6)

def _armchair(v, x, y, zfl, face, key="t_leat", w=0.62):
    """肘掛け椅子。face=+1: +x 向き(背もたれは -x 側), -1: -x 向き, +2: +y向き, -2: -y向き。"""
    if abs(face) == 1:
        v.A(key, 0.03).box(x - 0.30, x + 0.30, y - w / 2, y + w / 2, zfl + 0.02, zfl + 0.42)
        bx = x - face * 0.27
        v.A(key, 0.04).box(bx - 0.05, bx + 0.05, y - w / 2, y + w / 2, zfl + 0.42, zfl + 0.98)
        for sy in (-1, 1):
            v.A("t_wood").box(x - 0.28, x + 0.28, y + sy * (w / 2 - 0.02) - 0.025, y + sy * (w / 2 - 0.02) + 0.025, zfl + 0.42, zfl + 0.60)
    else:
        sg = 1 if face > 0 else -1
        v.A(key, 0.03).box(x - w / 2, x + w / 2, y - 0.30, y + 0.30, zfl + 0.02, zfl + 0.42)
        by = y - sg * 0.27
        v.A(key, 0.04).box(x - w / 2, x + w / 2, by - 0.05, by + 0.05, zfl + 0.42, zfl + 0.98)
        for sx in (-1, 1):
            v.A("t_wood").box(x + sx * (w / 2 - 0.02) - 0.025, x + sx * (w / 2 - 0.02) + 0.025, y - 0.28, y + 0.28, zfl + 0.42, zfl + 0.60)


def _lux_inside(v, S, tot, bays, segs, zones, rnd):
    """周遊列車の室内。廊下は +y 側(小窓)、客室は -y 側(大窓)。"""
    h = S["W"] / 2
    zfl, zs, zw1, zt, zr = S["z"]
    st = S["interior"]
    ax = tot / 2 - 0.05
    v.A("t_carp").box(-ax, ax, -h + 0.08, h - 0.08, zfl + 0.02, zfl + 0.035)           # 全面の絨毯
    v.A("t_wood", 0.01).box(-ax, ax, h - 0.092, h - 0.082, zfl + 0.035, zfl + 0.17)    # 幅木
    # 天井の間接照明(温白色)と廻り縁
    for s_ in (-1, 1):
        v.A("t_champ").box(-ax, ax, *sorted((s_ * 0.62, s_ * 0.66)), zw1 - 0.04, zw1 - 0.02)
    lamp = v.A("lamp_in")
    ends = S.get("_ends", ("cab", "cab"))
    if st in ("lux_ste", "lux_grn"):
        yc = h - 0.84                                         # 廊下の壁面(y)
        wy = 0.46                                            # 客室と廊下の間仕切り位置
        for (a, b) in segs:
            n = 3 if st == "lux_ste" else 2
            p = (b - a) / n
            for j in range(n + 1):
                xw = a + p * j
                v.A("t_wood").box(xw - 0.03, xw + 0.03, -h + 0.09, wy, zfl + 0.035, zw1 - 0.03)   # 客室の仕切壁
                v.A("t_champ").box(xw - 0.035, xw + 0.035, wy - 0.02, wy + 0.01, zfl + 0.035, zw1 - 0.03)
            for j in range(n):
                x0, x1 = a + p * j + 0.03, a + p * (j + 1) - 0.03
                xc = (x0 + x1) / 2
                # 廊下側の壁と扉(扉は壁の端に)
                v.A("t_wood").box(x0, xc - 0.5, wy, wy + 0.04, zfl + 0.035, zw1 - 0.03)
                v.A("t_wood").box(xc + 0.5, x1, wy, wy + 0.04, zfl + 0.035, zw1 - 0.03)
                v.A("t_wood").box(xc - 0.5, xc + 0.5, wy, wy + 0.04, zw1 - 0.60, zw1 - 0.03)
                v.A("t_champ").box(xc + 0.40, xc + 0.44, wy + 0.04, wy + 0.06, zfl + 1.0, zfl + 1.25)
                # 窓側のソファ(窓向き)+ローテーブル+肘掛け椅子
                v.A("t_leat", 0.04).box(xc - 1.15, xc + 0.35, -h + 0.14, -h + 0.66, zfl + 0.035, zfl + 0.44)
                v.A("t_leat", 0.04).box(xc - 1.15, xc + 0.35, -h + 0.60, -h + 0.70, zfl + 0.44, zfl + 0.96)
                v.A("t_wood").box(xc - 0.40, xc + 0.10, -h + 0.78, -h + 1.10, zfl + 0.035, zfl + 0.42)      # 低い机
                v.A("t_champ").box(xc - 0.40, xc + 0.10, -h + 0.78, -h + 1.10, zfl + 0.42, zfl + 0.44)
                _armchair(v, xc + 0.85, -h + 0.55, zfl, -2, "t_leat")
                # ベッド(日中はたたまれ、頭板だけ見える)+クローゼット
                v.A("t_wood").box(xc - 1.3, xc - 0.95, wy - 0.10, wy - 0.04, zfl + 0.60, zfl + 1.50)
                v.A("t_cream2", 0.03).box(xc - 1.3, xc - 0.45, 0.05, wy - 0.12, zfl + 0.45, zfl + 0.62)
                v.A("t_wood").box(x0 + 0.05, x0 + 0.40, wy - 0.42, wy - 0.02, zfl + 0.035, zfl + 1.90)       # 衣装棚
                # シャワー・洗面ユニット(扉つき小部屋の壁)
                v.A("t_cream").box(x1 - 0.95, x1 - 0.05, wy - 0.12, wy - 0.07, zfl + 0.035, zw1 - 0.1)
                v.A("lamp_glow").sphere((xc + 0.3, -0.35, zw1 - 0.12), (0.08, 0.08, 0.06), seg=10, rings=5)
                v.A("lamp_glow").sphere((xc - 0.6, -h + 0.9, zw1 - 0.12), (0.08, 0.08, 0.06), seg=10, rings=5)
                if st == "lux_grn":
                    v.A("t_wood").box(x1 - 1.6, x1 - 0.2, -h + 0.12, -h + 0.85, zfl + 0.035, zfl + 0.62)       # 檜の浴槽
                    v.A("glass").box(x1 - 1.58, x1 - 0.22, -h + 0.16, -h + 0.81, zfl + 0.50, zfl + 0.52)
                    v.A("t_cream2", 0.01).box(xc - 1.5, xc - 0.2, 0.0, wy - 0.15, zfl + 0.035, zfl + 0.08)      # 畳の間
        v.A("t_champ").cyl((-ax, h - 0.20, zfl + 0.98), (ax, h - 0.20, zfl + 0.98), 0.016, 0.016, seg=6)      # 廊下の手すり
        for k in range(int(2 * ax / 1.6)):
            xx = -ax + 0.8 + k * 1.6
            v.A("lamp_glow").sphere((xx, h - 0.45, zw1 - 0.08), (0.07, 0.07, 0.05), seg=8, rings=4)
    elif st == "lux_lng":
        xs = [-ax + 3.2 + i * 2.6 for i in range(int((2 * ax - 7.0) / 2.6) + 1)]
        for x in xs:
            if any(a < x < b for a, b in zones):
                continue
            for s_ in (-1, 1):
                yy = s_ * (h - 0.80)
                v.A("t_wood").cyl((x, yy, zfl + 0.035), (x, yy, zfl + 0.40), 0.20, 0.20, seg=14)
                v.A("t_champ").cyl((x, yy, zfl + 0.40), (x, yy, zfl + 0.42), 0.26, 0.26, seg=14)
                for sx in (-1, 1):
                    _armchair(v, x + sx * 0.80, yy, zfl, -sx, "t_leat")
                if rnd.random() < 0.5:
                    _rider(v, x + 0.80, yy, zfl, 3.14, True, rnd=rnd)
        # バーカウンター(車端)
        bx = ax - 1.0
        v.A("t_wood").box(bx - 0.5, bx + 0.5, -1.0, 0.2, zfl + 0.035, zfl + 1.05)
        v.A("t_champ").box(bx - 0.55, bx + 0.55, -1.05, 0.25, zfl + 1.05, zfl + 1.08)
        for k in range(4):
            v.A("t_leat", 0.02).cyl((bx - 0.9, -0.75 + k * 0.35, zfl + 0.035), (bx - 0.9, -0.75 + k * 0.35, zfl + 0.70), 0.15, 0.13, seg=10)
        v.A("t_champ").box(bx + 0.45, bx + 0.50, -1.0, 0.2, zfl + 1.2, zfl + 1.9)                        # 酒棚
        for k in range(7):
            v.A("lamp_glow").cyl((bx + 0.44, -0.9 + k * 0.17, zfl + 1.3), (bx + 0.44, -0.9 + k * 0.17, zfl + 1.7), 0.04, 0.04, seg=6)
        # 暖炉風の飾り棚
        v.A("t_wood").box(-ax + 0.1, -ax + 0.8, -0.8, 0.8, zfl + 0.035, zfl + 1.2)
        v.A("black").box(-ax + 0.78, -ax + 0.8, -0.35, 0.35, zfl + 0.2, zfl + 0.8)
        v.A("lamp_glow").box(-ax + 0.77, -ax + 0.79, -0.30, 0.30, zfl + 0.22, zfl + 0.45)
    elif st == "lux_din":
        kx = -ax + 3.6                                        # 厨房: x<kx(通路から見えるライブキッチン)
        v.A("t_steel").box(-ax, kx - 0.2, -0.45, 0.45, zfl + 0.035, zfl + 0.92)
        v.A("black").box(-ax + 0.3, kx - 0.4, -0.40, 0.40, zfl + 0.92, zfl + 0.95)
        v.A("lamp_glow").box(-ax + 0.3, kx - 0.4, -0.38, 0.38, zfl + 1.7, zfl + 1.74)
        v.A("t_champ").box(kx - 0.2, kx - 0.14, -h + 0.1, h - 0.1, zfl + 0.9, zfl + 0.96)
        for k in range(5):
            v.A("t_wood", 0.02).box(kx - 0.2, kx - 0.15, -h + 0.1, -0.5, zfl + 0.035 + k * 0.0, zfl + 2.0) if k == 0 else None
        for x in [kx + 0.9 + i * 1.75 for i in range(int((ax - kx - 1.2) / 1.75) + 1)]:
            for s_ in (-1, 1):
                yy = s_ * (h - 0.66)
                v.A("t_wood").box(x - 0.45, x + 0.45, yy - 0.50, yy + 0.50, zfl + 0.035, zfl + 0.20) if False else None
                v.A("t_cream2", 0.01).box(x - 0.40, x + 0.40, yy - 0.34, yy + 0.34, zfl + 0.76, zfl + 0.785)      # テーブルクロス
                v.A("t_champ").cyl((x, yy, zfl + 0.035), (x, yy, zfl + 0.76), 0.03, 0.03, seg=6)
                v.A("lamp_glow").sphere((x, yy, zfl + 0.86), (0.04, 0.04, 0.055), seg=10, rings=6)
                v.A("t_champ").cyl((x, yy, zfl + 0.785), (x, yy, zfl + 0.80), 0.06, 0.06, seg=10)
                for sg in (-1, 1):
                    _armchair(v, x + sg * 0.62, yy, zfl, -sg, "t_leat", w=0.54)
                    if rnd.random() < 0.4:
                        _rider(v, x + sg * 0.62, yy, zfl, 0.0 if sg < 0 else 3.14, True, rnd=rnd)
    else:   # lux_obs: 前面に向いた回転椅子+後部バー
        fe = 1 if ends[1] == "cab" else -1                     # 運転台のある側
        for i in range(3):
            x = fe * (ax - 1.0 - i * 1.5)
            for sy in (-1, 1):
                _armchair(v, x, sy * 0.95, zfl, fe, "t_leat", w=0.70)
                if rnd.random() < 0.5:
                    _rider(v, x, sy * 0.95, zfl, 0.0 if fe > 0 else 3.14, True, rnd=rnd)
            v.A("t_wood").cyl((x + fe * 0.70, 0, zfl + 0.035), (x + fe * 0.70, 0, zfl + 0.42), 0.20, 0.20, seg=12) if i == 0 else None
        bx = -fe * (ax - 1.2)
        v.A("t_wood").box(bx - 0.5, bx + 0.5, -0.9, 0.9, zfl + 0.035, zfl + 1.0)
        v.A("t_champ").box(bx - 0.55, bx + 0.55, -0.95, 0.95, zfl + 1.0, zfl + 1.03)
        for k in range(5):
            v.A("t_leat", 0.02).cyl((bx + fe * 0.9, -0.8 + k * 0.4, zfl + 0.035), (bx + fe * 0.9, -0.8 + k * 0.4, zfl + 0.70), 0.15, 0.13, seg=10)
        v.A("t_champ").box(bx - fe * 0.45, bx - fe * 0.50, -0.9, 0.9, zfl + 1.2, zfl + 1.9)



def _tail(v, S, e, tot):
    """最後尾の車端: 貫通路は閉じ、尾灯と空の後部標識(テールマーク)掛けを付ける。"""
    _gang(v, S, e, tot)
    L, W = S["L"], S["W"]
    zfl, zs, zw1, zt, zr = S["z"]
    xe = L / 2
    X = lambda a: e * a
    for s in (-1, 1):
        v.A("t_steel").box(*sorted((X(xe + 0.02), X(xe + 0.10))), s * 1.02 - 0.14, s * 1.02 + 0.14, zfl + 0.62, zfl + 0.92)   # 尾灯の枠
        v.A("lamp_glow").box(*sorted((X(xe + 0.10), X(xe + 0.12))), s * 1.02 - 0.10, s * 1.02 + 0.10, zfl + 0.67, zfl + 0.87)
    v.A("t_steel").box(*sorted((X(xe + 0.02), X(xe + 0.07))), -0.30, 0.30, zfl + 2.05, zfl + 2.12)      # テールマーク掛け(空)
    v.A("t_steel").torus((X(xe + 0.10), 0.0, zfl + 2.62), "x", 0.30, 0.025, segR=28, segr=6)
    v.A("t_steel").box(*sorted((X(xe + 0.04), X(xe + 0.10))), -0.015, 0.015, zfl + 2.12, zfl + 2.34)


# --------------------------------------------------------------------------- main entry
def make(tid, name="emu", seed=11, num_img=None, ends=("cab", "cab"), pant=True):
    mats()
    S = dict(TYPES[tid], id=tid)
    if not pant:
        S["roof"] = [r for r in S["roof"] if not r.startswith("pant")]
    num_img = num_img if num_img not in (None, "kiha_number.png") else f"num_{tid}.png"
    v = Veh(name)
    L, W = S["L"], S["W"]
    h = W / 2
    zfl, zs, zw1, zt, zr = S["z"]
    cl = S["cab"]
    tot = L - 2 * cl
    nose = S.get("nose", 0.12) if S["front"] in ("bonnet", "round") else 0.12
    S["_ends"] = ends
    _body(v, S)
    doors, bays = _windows(v, S, tot, seed)
    _interior(v, S, tot, bays, seed)
    for e, kd in ((-1, ends[0]), (1, ends[1])):
        if kd == "cab":
            _cab(v, S, e, tot, nose)
        elif kd == "tail":
            _tail(v, S, e, tot)
        else:
            _gang(v, S, e, tot)
    for dx in doors:
        for s in (-1, 1):
            steps_down(v, dx, s, h, zfl - 0.1, n=2)
    _under(v, S)
    _roof(v, S)
    lg = {"jnr_dc": ("logo_new.png", 0.50), "jnr_sub": ("logo_new.png", 0.62), "jnr_exp": ("logo_new.png", 0.70),
          "jnr_ltd": ("logo_new.png", 0.52), "jnr_ac": ("logo_new.png", 0.56), "ke": ("logo_ke.png", 0.60), "km": ("logo_km.png", 0.46), "kiha_std": ("logo_new.png", 0.55), "kiha_exp": ("logo_new.png", 0.66),
          "kiha_hyb": ("logo_new.png", 0.60), "kiha_ltd": ("logo_new.png", 0.58), "kiha_sr": ("logo_sr.png", 0.46), "kiha_hr": ("logo_hr.png", 0.40),
          "tram_o": ("logo_hr.png", 0.40), "lx_obs": ("logo_yui.png", 0.62), "lx_ste": ("logo_yui.png", 0.62), "lx_lng": ("logo_yui.png", 0.62), "lx_din": ("logo_yui.png", 0.62), "lx_grn": ("logo_yui.png", 0.62), "sl_b": ("logo_new.png", 0.56), "sl_a": ("logo_new.png", 0.56), "sl_din": ("logo_new.png", 0.60), "sl_gen": ("logo_new.png", 0.50)}[tid]
    ds = sorted(doors)
    xm = (ds[0] + ds[1]) / 2 if len(ds) > 1 else ds[0] + 2.2
    di = ds[1] if len(ds) > 1 else ds[0]
    for s in (-1, 1):
        v.side_plane(num_img, s, L * 0.37, 0.72, zs - 0.38, zs - 0.16, s * (h + 0.013))
        zc = zs - 0.52 if tid not in ("ke", "jnr_exp") else zs - 0.60
        v.side_plane(lg[0], s, xm, lg[1], zc - lg[1] / 2, zc + lg[1] / 2, s * (h + 0.014))
        if S["ss"] == "none":
            pass
        elif S["ss"] == "roll":
            v.side_plane(f"dest_{tid}_0.png", s, di + (0.0 if len(ds) > 2 else 0.3), 0.92, zw1 + 0.10, zw1 + 0.28, s * (h + 0.013))
        else:
            v.A("t_steel").box(di + 0.55, di + 0.9, *sorted((s * (h + 0.0), s * (h + 0.012))), zs - 0.02, zs + 0.2) if False else None
            v.side_plane(f"sabo_{tid}.png", s, ds[0] + 0.0 if False else di + 0.82, 0.42, zs + 0.06, zs + 0.24, s * (h + 0.016))
    v.meta["type"] = tid
    v.meta["title"] = S["title"]
    v.meta["length"] = L
    return v
