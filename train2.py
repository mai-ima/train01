"""会社別の旅客車両(汎用・実在標章なし): 国鉄電車(直流/交流)、国都電鉄、国都地下鉄、大湊市電、湾岸モノレール、臨港鉄道気動車。
すべてリグ規約(台車/輪軸/連結器の部品化)に従い、室内(座席・吊り革・つり手・乗客)つき。"""
import math
import numpy as np
import lib
from trainkit import *
import trainkit as TK
from train import fill_walls, make_kiha


def extra_mats():
    vmat("red")
    P = vpaint
    TK._VM.update({
        "sky": P("v_sky", (0.12, 0.34, 0.55), rough=0.38, rust=0.12),
        "jorange": P("v_jorange", (0.64, 0.30, 0.04), rough=0.4, rust=0.15),
        "maroon": P("v_maroon", (0.28, 0.035, 0.03), rough=0.38, rust=0.12),
        "ivory": P("v_ivory", (0.80, 0.77, 0.66), rough=0.4, rust=0.1),
        "sub_silver": P("v_subsil", (0.55, 0.57, 0.58), rough=0.30, rust=0.08, metal=0.7),
        "sub_red": P("v_subred", (0.55, 0.04, 0.04), rough=0.35, rust=0.1),
        "tram_green": P("v_tramg", (0.10, 0.30, 0.18), rough=0.4, rust=0.15),
        "tram_cream": P("v_tramc", (0.78, 0.72, 0.52), rough=0.4, rust=0.12),
        "mono_white": P("v_monow", (0.78, 0.80, 0.80), rough=0.3, rust=0.05),
        "mono_blue": P("v_monob", (0.05, 0.20, 0.48), rough=0.3, rust=0.05),
        "hr_yellow": P("v_hry", (0.66, 0.50, 0.06), rough=0.42, rust=0.2),
        "hr_navy": P("v_hrn", (0.04, 0.07, 0.16), rough=0.42, rust=0.2),
    })


def pantograph(v, x, zr, key="steel"):
    """下枠交差形に近い簡素なパンタグラフ(畳んだ姿)。"""
    for s in (-1, 1):
        v.A("iron").box(x - 0.9, x + 0.9, s * 0.45 - 0.05, s * 0.45 + 0.05, zr - 0.04, zr + 0.12)
        v.A(key).sbox((x - 0.5, s * 0.45, zr + 0.12), (x + 0.4, s * 0.45, zr + 0.62), 0.05, 0.05)
        v.A(key).sbox((x + 0.4, s * 0.45, zr + 0.62), (x - 0.1, s * 0.45, zr + 1.0), 0.05, 0.05)
    v.A(key).box(x - 0.15, x + 0.05, -0.95, 0.95, zr + 0.95, zr + 1.02)
    v.A("black").box(x - 0.05, x + 0.0, -1.05, 1.05, zr + 1.0, zr + 1.04)
    for s in (-1, 1):
        v.A("porcelain" if False else "lampglass").cyl((x - 0.9, s * 0.45, zr), (x - 0.9, s * 0.45, zr + 0.14), 0.07, 0.07, seg=8)


def _ends(v, L, tot, W, h, zs, zw1, zt, zr, up, lo, num_img, headmark="headmark.png", cab=True):
    for e in (-1, 1):
        xa, xb = sorted((e * tot / 2, e * L / 2))
        for s in (-1, 1):
            wall_open(v, up, 'y', xa, xb, s * (h - 0.08), s * h, zs, zw1,
                      [(*sorted((e * (tot / 2 + 0.12), e * (tot / 2 + 0.90))), zs + 0.1, zw1 - 0.1)])
        wall_open(v, up, 'x', -h, h, e * L / 2 - 0.1 * e, e * L / 2, zs, zw1,
                  [(-1.08, -0.16, zs + 0.12, zw1 - 0.08), (0.16, 1.08, zs + 0.12, zw1 - 0.08)])
        wall_open(v, up, 'x', -h, h, e * tot / 2 - 0.05 * e, e * tot / 2, zs, zw1, [(-0.35, 0.35, zs, zw1 - 0.25)])
        v.A("floorw").box(xa, xb, -h + 0.08, h - 0.08, zs, zs + 0.02)
        dx = e * (L / 2 - 0.45)
        v.A("grey", 0.01).box(dx - 0.2, dx + 0.2, -1.1, 1.1, zs, zs + 0.34)
        v.A("black").box(dx - 0.22 * e - 0.1, dx - 0.22 * e + 0.1, -0.5, -0.1, zs + 0.34, zs + 0.40)
        gl = v.A("glass")
        for s in (-1, 1):
            gl.box(*sorted((e * (tot / 2 + 0.12), e * (tot / 2 + 0.90))), *sorted((s * h, s * (h + 0.012))), zs + 0.1, zw1 - 0.1)
        for yc in (-0.62, 0.62):
            gl.box(*sorted((e * L / 2, e * (L / 2 + 0.012))), yc - 0.46, yc + 0.46, zs + 0.12, zw1 - 0.08)
        v.A(up, 0.005).box(*sorted((e * L / 2, e * (L / 2 + 0.02))), -0.07, 0.07, zs + 0.05, zw1)
        v.A("lampglass").cyl((e * (L / 2 + 0.04), 0, zt + 0.17), (e * (L / 2 + 0.07), 0, zt + 0.17), 0.1, 0.1, seg=12)
        for yc in (-1.0, 1.0):
            v.A("lampglass").cyl((e * (L / 2), yc, zs - 0.35), (e * (L / 2 + 0.06), yc, zs - 0.35), 0.065, 0.065, seg=10)
            v.A("black").cyl((e * (L / 2 + 0.01), yc, zs - 0.35), (e * (L / 2 + 0.04), yc, zs - 0.35), 0.09, 0.09, seg=10)
        v.A("iron", 0.01).box(*sorted((e * L / 2, e * (L / 2 + 0.16))), -1.2, 1.2, 0.86, 1.02)
        coupler(v, e, e * (L / 2 + 0.12))
        v.end_plane(num_img, e, 0.0, 0.62, zs - 0.3, zs - 0.08, e * (L / 2 + 0.014))
        v.end_plane(headmark, e, 0.0, 0.34, zw1 - 0.05, zw1 + 0.22, e * (L / 2 + 0.016)) if False else None


def make_emu(name="emu", kind="jnr_dc", seed=11, num_img="kiha_number.png"):
    """kind: jnr_dc / jnr_ac / ke / km(地下鉄) ."""
    extra_mats()
    v = Veh(name)
    prm = dict(
        jnr_dc=dict(L=20.0, up="sky", lo="sky", band="cream", pant=True, nd=4),
        jnr_ac=dict(L=20.0, up="ivory", lo="ivory", band="jorange", pant=True, nd=3),
        ke=dict(L=19.0, up="maroon", lo="maroon", band="ivory", pant=True, nd=3),
        km=dict(L=18.0, up="sub_silver", lo="sub_silver", band="sub_red", pant=False, nd=3),
    )[kind]
    L, up, lo, band = prm["L"], prm["up"], prm["lo"], prm["band"]
    W, h = (2.80, 1.40) if kind != "km" else (2.60, 1.30)
    zf, zs, zw1, zt, zr = (1.05, 1.15, 2.75, 2.95, 3.55) if kind != "km" else (1.0, 1.10, 2.55, 2.75, 3.30)
    v.A(lo, 0.014).extrude_x([(-h, zf), (h, zf), (h, zw1), (-h, zw1)], -L / 2, L / 2)
    v.A(band, 0.01).extrude_x([(-h - 0.004, zs + 0.52), (h + 0.004, zs + 0.52), (h + 0.004, zs + 0.64), (-h - 0.004, zs + 0.64)], -L / 2 + 0.01, L / 2 - 0.01)
    v.A(up, 0.01).extrude_x([(-h, zw1), (h, zw1), (h, zt), (-h, zt)], -L / 2, L / 2)
    v.A("roof", 0.015).extrude_x(upper_profile(W, zt - 0.05, zt + 0.03, zr, inset=0.04), -L / 2 + 0.02, L / 2 - 0.02)
    nd = prm["nd"]
    bays = [('D', 1.3)] + [('W', 1.0)] * 2 + [('D', 1.3)] + [('W', 1.0)] * 2 + [('D', 1.3)] + [('W', 1.0)] * 2 + [('D', 1.3)]
    if nd == 3:
        bays = [('D', 1.3)] + [('W', 1.0)] * 3 + [('D', 1.3)] + [('W', 1.0)] * 3 + [('D', 1.3)] + [('W', 1.0)] * 3 + [('D', 1.3)]
        bays = bays[:-4]
    tot, doors = window_bays(v, bays, W, zs, zw1, up, door_key=band if kind != "km" else "sub_red", seed=seed, curtain_p=0.3, door_drop=0.0)
    interior(v, -tot / 2 + 0.1, tot / 2 - 0.1, W, zs, zw1, zt, pitch=1.02, seed=seed, person_p=0.35)
    _ends(v, L, tot, W, h, zs, zw1, zt, zr, up, lo, num_img)
    for dx in doors:
        for s in (-1, 1):
            steps_down(v, dx, s, h, zf)
    v.A("under", 0.01).box(-L / 2 + 0.3, L / 2 - 0.3, -1.1, 1.1, 0.62, zf)
    v.A("iron", 0.01).box(-3.0, 0.8, -0.8, 0.8, 0.40, 0.62)             # 主制御器箱
    v.A("iron", 0.01).box(2.2, 4.4, -0.85, 0.5, 0.42, 0.62)
    v.A("steel").cyl((-5.0, 0.2, 0.5), (-3.6, 0.2, 0.5), 0.15, 0.15, seg=10)   # 空気タンク
    for x in (-L * 0.34, L * 0.34):
        bogie2(v, x, wb=2.2 if kind != "km" else 2.0)
    # 屋根上機器
    if prm["pant"]:
        pantograph(v, -L * 0.28 if kind != "jnr_ac" else -L * 0.25, zr)
        if kind == "jnr_ac":
            v.A("iron").box(L * 0.1 - 1.5, L * 0.1 + 1.5, -0.55, 0.55, zr - 0.05, zr + 0.55)   # 交流用主変圧器箱(屋根上遮断器)
            v.A("lampglass").cyl((L * 0.1 - 1.8, 0, zr + 0.55), (L * 0.1 - 1.8, 0, zr + 0.9), 0.09, 0.09, seg=8)
    roof_vents(v, [L * 0.08, L * 0.18, L * 0.3] if kind == "km" else [-2.0, 1.0, 4.0, 6.5], zr - 0.04)
    if kind == "km":      # 地下鉄: 屋根上クーラー・床下の集電靴
        v.A("under").box(-0.6, 0.6, -1.25, -1.18, 0.35, 0.55)
    for s in (-1, 1):
        v.side_plane("mark_depot.png", s, 5.0 if kind != "km" else 4.0, 1.9, zs + 0.0, zs + 0.25, s * (h + 0.012)) if False else None
        v.side_plane(num_img, s, L * 0.38, 0.72, zf + 0.02, zf + 0.22, s * (h + 0.012))
        v.side_plane("logo_new.png", s, 0.0, 0.5, zs + 0.7, zs + 1.1, s * (h + 0.012)) if False else None
    return v


def make_tram(name="tram", seed=21, num_img="kiha_number.png"):
    extra_mats()
    v = Veh(name)
    L, W, h = 12.6, 2.45, 1.225
    zf, zs, zw1, zt, zr = 0.62, 0.78, 2.15, 2.30, 2.82
    v.A("tram_green", 0.012).extrude_x([(-h, zf), (h, zf), (h, zw1), (-h, zw1)], -L / 2, L / 2)
    v.A("tram_cream", 0.01).extrude_x([(-h - 0.004, zs + 0.5), (h + 0.004, zs + 0.5), (h + 0.004, zw1 - 0.0), (-h - 0.004, zw1 - 0.0)], -L / 2 + 0.01, L / 2 - 0.01)
    v.A("tram_cream", 0.01).extrude_x([(-h, zw1), (h, zw1), (h, zt), (-h, zt)], -L / 2, L / 2)
    v.A("roof", 0.015).extrude_x(upper_profile(W, zt - 0.05, zt + 0.03, zr, inset=0.05), -L / 2 + 0.02, L / 2 - 0.02)
    bays = [('D', 1.1)] + [('W', 0.9)] * 4 + [('D', 1.1)]
    tot, doors = window_bays(v, bays, W, zs, zw1 - 0.2, "tram_cream", door_key="tram_green", seed=seed, curtain_p=0.2, door_drop=0.0)
    interior(v, -tot / 2 + 0.1, tot / 2 - 0.1, W, zs, zw1 - 0.2, zt, pitch=0.9, seed=seed, person_p=0.4)
    for e in (-1, 1):
        fill_walls(v, "tram_cream", *sorted((e * tot / 2, e * L / 2)), W, zs, zw1)
        gl = v.A("glass")
        for yc in (-0.55, 0.55):
            gl.box(*sorted((e * L / 2, e * (L / 2 + 0.012))), yc - 0.45, yc + 0.45, zs + 0.2, zw1 - 0.15)
        v.A("lampglass").cyl((e * (L / 2 + 0.03), 0, zs + 0.1), (e * (L / 2 + 0.06), 0, zs + 0.1), 0.1, 0.1, seg=12)
        coupler(v, e, e * (L / 2 + 0.1), z=0.7)
        v.A("iron", 0.01).box(*sorted((e * L / 2, e * (L / 2 + 0.12))), -1.1, 1.1, 0.5, 0.6)
    v.A("under", 0.01).box(-L / 2 + 0.3, L / 2 - 0.3, -1.1, 1.1, 0.4, zf)
    for x in (-4.2, 4.2):
        bogie2(v, x, wb=1.6, r=0.33)
    # 集電装置(ビューゲル/小型パンタ)
    v.A("iron").box(-3.5, -2.9, -0.35, 0.35, zr - 0.04, zr + 0.12)
    v.A("steel").sbox((-3.2, -0.3, zr + 0.12), (-2.2, 0.0, zr + 0.78), 0.04, 0.04)
    v.A("steel").sbox((-3.2, 0.3, zr + 0.12), (-2.2, 0.0, zr + 0.78), 0.04, 0.04)
    v.A("black").box(-2.3, -2.1, -0.7, 0.7, zr + 0.76, zr + 0.82)
    for s in (-1, 1):
        v.side_plane(num_img, s, 0.0, 0.7, zf + 0.05, zf + 0.25, s * (h + 0.012))
    return v


def make_mono(name="mono", seed=31, num_img="kiha_number.png"):
    """跨座式モノレール(軌道桁を跨ぐ)。軌道桁の上面を基準(z=0)に、車体は桁の上に座る。"""
    extra_mats()
    v = Veh(name)
    L, W, h = 14.0, 2.9, 1.45
    zf, zs, zw1, zt, zr = 0.55, 0.80, 2.15, 2.35, 3.05
    v.A("mono_white", 0.014).extrude_x([(-h, zf), (h, zf), (h, zw1), (-h, zw1)], -L / 2, L / 2)
    v.A("mono_blue", 0.01).extrude_x([(-h - 0.004, zs + 0.2), (h + 0.004, zs + 0.2), (h + 0.004, zs + 0.5), (-h - 0.004, zs + 0.5)], -L / 2 + 0.01, L / 2 - 0.01)
    v.A("mono_white", 0.01).extrude_x([(-h, zw1), (h, zw1), (h, zt), (-h, zt)], -L / 2, L / 2)
    v.A("roof", 0.015).extrude_x(upper_profile(W, zt - 0.05, zt + 0.03, zr, inset=0.06), -L / 2 + 0.02, L / 2 - 0.02)
    bays = [('D', 1.3)] + [('W', 1.05)] * 3 + [('D', 1.3)] + [('W', 1.05)] * 3 + [('D', 1.3)]
    bays = bays[:6]
    tot, doors = window_bays(v, bays, W, zs, zw1, "mono_white", door_key="mono_blue", seed=seed, curtain_p=0.15, door_drop=0.0)
    interior(v, -tot / 2 + 0.1, tot / 2 - 0.1, W, zs, zw1, zt, pitch=1.05, seed=seed, person_p=0.3)
    for e in (-1, 1):
        fill_walls(v, "mono_white", *sorted((e * tot / 2, e * L / 2)), W, zs, zw1)
        gl = v.A("glass")
        for yc in (-0.7, 0.7):
            gl.box(*sorted((e * L / 2, e * (L / 2 + 0.012))), yc - 0.6, yc + 0.6, zs + 0.15, zw1 - 0.1)
        v.A("lampglass").cyl((e * (L / 2 + 0.03), -1.0, zs + 0.0), (e * (L / 2 + 0.06), -1.0, zs + 0.0), 0.09, 0.09, seg=12)
        v.A("lampglass").cyl((e * (L / 2 + 0.03), 1.0, zs + 0.0), (e * (L / 2 + 0.06), 1.0, zs + 0.0), 0.09, 0.09, seg=12)
    # 桁を跨ぐ台車(走行輪+案内輪)。部品として別オブジェクト化
    for x in (-4.6, 4.6):
        with v.part("bogie", (x, 0.0, 0.0), axis="z"):
            v.A("iron", 0.01).box(x - 1.4, x + 1.4, -0.55, 0.55, 0.0, 0.5)
            for s in (-1, 1):
                v.A("iron", 0.01).box(x - 1.3, x + 1.3, s * 0.52 - 0.12, s * 0.52 + 0.12, -1.5, 0.5)      # 桁の側面を抱く枠
            for dx in (-0.8, 0.8):
                with v.part("ws", (x + dx, 0.0, 0.0), axis="y", r=0.55):
                    v.A("rubber").cyl((x + dx, -0.4, 0.0), (x + dx, 0.4, 0.0), 0.55, 0.55, seg=20) if False else None
                    v.A("rubber").cyl((x + dx, -0.38, 0.0), (x + dx, 0.38, 0.0), 0.55, 0.55, seg=20)
        v.meta["bogies"].append(dict(x=x, wheelbase=1.6, wheel_r=0.55, axles=2))
        v.meta["wheelsets"] += [x - 0.8, x + 0.8]
    for e in (-1, 1):
        v.meta["couplers"].append(dict(end=e, x=e * (L / 2 + 0.05), z=0.9))
        v.A("iron", 0.01).box(*sorted((e * L / 2, e * (L / 2 + 0.12))), -0.6, 0.6, 0.55, 0.7)
    for s in (-1, 1):
        v.side_plane(num_img, s, 0.0, 0.7, zf + 0.05, zf + 0.25, s * (h + 0.012))
    return v
