import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""Shared layout constants + material registry for the Honamino station scene (national-railway era)."""
import math
import os
import random
import sys

sys.path.insert(0, f"{_R}")

import bpy
import numpy as np
from mathutils import Vector

import lib
from lib import Acc, Mat, collection, image_plane, link, np_mesh

OUT = f"{_R}/out"
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ layout (metres, Z up, track along X)
GAUGE = 1.067
RAIL_Y = GAUGE / 2
Z_BAL = 0.10            # ballast surface
Z_SLEEP = 0.14          # sleeper top
Z_RAIL = 0.274          # rail head top
Z_PLAT = 1.10           # platform surface: rail head(0.274)+0.83 (JNR low platform; was 0.60 → stock cars looked floating)
Y_EDGE = 1.70           # platform edge (track side)
Y_WALL = 4.40           # building front wall / platform back
Y_BACK = 8.40           # building back wall
SX0, SX1 = -12.0, -2.0  # station building x-range
PX0, PX1 = -18.0, 26.0  # platform x-range
X_C = 38.0              # level crossing x
ROAD_Y = 14.5           # forecourt dirt road centre line
TRAIN_X0, TRAIN_X1 = 2.0, 22.0
# ---- yard: four running / siding tracks (track centre lines, y)
T1, T2, T3, T4 = 0.0, -4.6, -11.0, -16.5
T5, T6 = -22.0, -27.5       # D10: 穂波野を6線へ(T4 の南に留置/入換の側線を2本増設。T4 から分岐して東へ伸びる)
TRACK_YS = [T1, T2, T3, T4, T5, T6]
ISLAND = (-12.0, 32.0, T3 + 1.7, T2 - 1.7)   # x0, x1, y0 (south edge), y1 (north edge) of the island platform
YARD_SOUTH = -24.0
Z_FLOOR = Z_PLAT + 0.30  # interior floor (raised wooden floor)

M = {}


def rgb(r, g, b):
    return (r, g, b)


def make_materials():
    P = lib.mat_pbr
    # ---- raw (unpainted) weathered wood: silver-grey boards
    wall_id = os.environ.get("WALL", "WoodSiding011")
    wall_scale = float(os.environ.get("WALLSCALE", "2.2"))
    M["wall"] = P("wall_siding", wall_id, scale=wall_scale, hsv=(0.5, 0.8, 0.95), tint=(0.78, 0.70, 0.60),
                  tint_amt=0.5, rough=0.88, bump=1.0, bump_dist=0.03, dirt=0.45, macro=0.22, spec=0.1)
    M["wood"] = P("wood_plank", "Planks023A", scale=0.9, hsv=(0.5, 0.8, 0.85), tint=(0.78, 0.70, 0.62),
                  tint_amt=0.5, bump=0.6, dirt=0.3, macro=0.2, spec=0.2)
    M["wood_dark"] = P("wood_dark", "Planks023A", scale=0.7, hsv=(0.5, 0.9, 0.45), tint=(0.62, 0.50, 0.40),
                       tint_amt=0.6, bump=0.6, macro=0.2, spec=0.2)
    M["floor"] = P("floor", "Planks023A", scale=0.8, hsv=(0.5, 0.85, 0.62), tint=(0.7, 0.6, 0.5), tint_amt=0.5,
                   bump=0.5, dirt=0.5, macro=0.2, spec=0.25)
    M["roof"] = P("roof_tile", "RoofingTiles013B", scale=1.0, hsv=(0.55, 0.45, 2.6), tint=(0.62, 0.66, 0.72),
                  tint_amt=0.5, bump=0.5, macro=0.3, spec=0.45, ao_amt=0.4)
    M["concrete"] = P("concrete", "Concrete036", scale=1.4, hsv=(0.5, 0.7, 1.0), tint=(0.95, 0.88, 0.76), tint_amt=0.7, dirt=0.35, bump=0.4, spec=0.25)
    M["stone"] = P("stone", "Concrete044D", scale=1.3, hsv=(0.5, 0.65, 0.85), tint=(0.95, 0.88, 0.76), tint_amt=0.6, dirt=0.35, bump=0.9, spec=0.2)
    M["ballast"] = P("ballast", "Gravel041", scale=1.7, hsv=(0.5, 0.6, 0.42), tint=(0.78, 0.74, 0.68), tint_amt=0.6,
                     bump=1.2, bump_dist=0.04, macro=0.25, spec=0.05)
    M["plat_top"] = P("plat_top", "Gravel041", scale=1.1, hsv=(0.5, 0.9, 0.7), tint=(0.78, 0.68, 0.55),
                      tint_amt=0.6, bump=0.9, bump_dist=0.03, macro=0.3, spec=0.03)
    M["dirt"] = P("dirt", "Ground081", scale=1.8, hsv=(0.5, 0.85, 0.85), tint=(0.85, 0.75, 0.6), tint_amt=0.4,
                  bump=0.9, bump_dist=0.04, macro=0.25, spec=0.0)
    M["soil"] = P("soil", "Ground110", scale=1.6, hsv=(0.5, 0.9, 0.7), bump=0.8, macro=0.2, spec=0.0)
    M["grass_ground"] = P("grass_ground", "Grass004", scale=1.6, hsv=(0.49, 0.62, 0.78), tint=(0.98, 0.88, 0.48),
                          tint_amt=0.8, bump=0.8, macro=0.3, spec=0.0, patch=0.6)
    M["bark"] = P("bark", "Bark001", scale=0.9, hsv=(0.5, 0.65, 0.7), tint=(0.8, 0.72, 0.62), tint_amt=0.5,
                  bump=1.2, spec=0.15)
    M["tin"] = P("tin_roof", "CorrugatedSteel005", scale=1.2, hsv=(0.5, 0.9, 0.75), tint=(0.62, 0.34, 0.2),
                 tint_amt=0.7, bump=0.5, macro=0.35, dirt=0.4, spec=0.45)
    M["rust"] = P("rust_metal", "Metal041B", scale=0.9, bump=0.5, macro=0.3, spec=0.4)

    # road: dry dirt with dark wheel ruts and a grassy centre strip; driven by the 'Col' colour attribute
    M["road"] = mat_road()
    # ---- procedural / simple
    M["rail"] = lib.mat_rail("rail", z_lo=0.250, z_hi=0.268)
    M["sleeper"] = lib.mat_wood("sleeper", color=(0.075, 0.05, 0.035), along='Y', weather=0.7, rough=0.8)
    M["iron_black"] = lib.mat_paint("iron_black", (0.025, 0.025, 0.028), rough=0.62, rust=0.25, metal=0.15, rust_scale=1.8)   # 鉄骨: 空の青い映り込みと橙斑を抑える
    M["iron_rust"] = lib.mat_paint("iron_rust", (0.09, 0.07, 0.06), rough=0.78, rust=0.55, metal=0.08, rust_scale=1.6)   # 橙の斑と金属反射を抑え、暗い褐色の錆に
    M["white_paint"] = lib.mat_paint("white_paint", (0.72, 0.70, 0.64), rough=0.6, rust=0.25)
    M["post_red"] = lib.mat_paint("post_red", (0.50, 0.035, 0.025), rough=0.35, rust=0.35)
    M["porcelain"] = lib.mat_plain("porcelain", (0.85, 0.85, 0.82), rough=0.15, spec=0.7)
    M["rubber"] = lib.mat_plain("rubber", (0.02, 0.02, 0.02), rough=0.85)
    M["chrome"] = lib.mat_plain("chrome", (0.55, 0.55, 0.57), rough=0.25, metal=1.0)
    M["leather"] = lib.mat_plain("leather", (0.05, 0.03, 0.02), rough=0.55)
    M["glass"] = lib.mat_glass("glass")
    M["dark_glass"] = lib.mat_plain("dark_glass", (0.01, 0.015, 0.02), rough=0.08, spec=0.8)
    M["white_line"] = lib.mat_plain("white_line", (0.78, 0.76, 0.70), rough=0.9)
    M["crossbuck"] = lib.mat_stripes("crossbuck", c1=(0.04, 0.04, 0.04), c2=(0.80, 0.62, 0.08), period=0.28, axis='Z')
    M["stripes_gate"] = lib.mat_stripes("stripes", period=0.5, axis='Z')
    M["paddy"] = lib.mat_paddy("paddy", green=(0.30, 0.38, 0.08), yellow=(0.64, 0.52, 0.14))
    M["stubble"] = P("stubble", "Ground081", scale=1.4, hsv=(0.5, 0.8, 0.62), tint=(0.8, 0.62, 0.30), tint_amt=0.7,
                     bump=0.6, macro=0.3, spec=0.0)
    M["leaf"] = lib.mat_vertex_color("leaf", rough=0.55, trans=0.3)
    M["blade"] = lib.mat_vertex_color("blade", rough=0.6, trans=0.35, spec=0.2)
    M["straw"] = lib.mat_vertex_color("straw", rough=0.75, trans=0.15, spec=0.15)
    M["pebble"] = mat_pebble()
    M["sack"] = mat_sack()
    # train
    M["kiha_red"] = lib.mat_paint("kiha_red", (0.55, 0.075, 0.03), rough=0.38, rust=0.25, rust_scale=2.0)
    M["kiha_cream"] = lib.mat_paint("kiha_cream", (0.80, 0.68, 0.44), rough=0.40, rust=0.2, rust_scale=2.0)
    M["kiha_roof"] = lib.mat_paint("kiha_roof", (0.18, 0.19, 0.2), rough=0.6, rust=0.3)
    M["kiha_under"] = lib.mat_paint("kiha_under", (0.03, 0.03, 0.032), rough=0.6, rust=0.45, metal=0.3)
    M["kiha_glass"] = lib.mat_plain("kiha_glass", (0.015, 0.02, 0.025), rough=0.05, spec=0.9)
    M["truck"] = lib.mat_paint("truck", (0.11, 0.24, 0.20), rough=0.45, rust=0.65, rust_scale=2.5)
    M["truck_cream"] = lib.mat_paint("truck_cream", (0.62, 0.58, 0.45), rough=0.5, rust=0.55)
    M["lamp_glow"] = lib.mat_plain("lamp_glow", (0.9, 0.85, 0.7), rough=0.2)
    return M


def mat_road():
    """Dry dirt road: ruts darken (Col.R), centre strip turns grassy (Col.G), edges blend to meadow."""
    m = Mat("dirt_road")
    A = lib.pbr_layer(m, "Ground081", 1.6)
    B = lib.pbr_layer(m, "Ground110", 1.4)
    C = lib.pbr_layer(m, "Grass006", 1.2)
    at = m.node('ShaderNodeAttribute', attribute_name="Col")
    sep = m.node('ShaderNodeSeparateColor')
    m.set(sep.inputs['Color'], at.outputs['Color'])
    rut = sep.outputs['Red']
    grass = sep.outputs['Green']
    dry = m.mix(1.0, A["col"], (0.82, 0.72, 0.58), 'MULTIPLY')
    wet = m.mix(1.0, B["col"], (0.9, 0.8, 0.7), 'MULTIPLY')
    gr = m.mix(1.0, C["col"], (0.95, 0.88, 0.5), 'MULTIPLY')
    col = m.mix(rut, dry, wet)
    gmask = m.maprange(m.math('MULTIPLY', grass, m.ramp(m.noise(scale=1.6, detail=4), [(0.3, (0.4, 0.4, 0.4)), (0.7, (1.3, 1.3, 1.3))]), clamp=True), 0.3, 0.8, 0.0, 1.0)
    col = m.mix(gmask, col, gr)
    macro = m.ramp(m.noise(scale=0.25, detail=4), [(0.25, (0.82, 0.82, 0.82)), (0.75, (1.12, 1.12, 1.12))])
    col = m.mix(1.0, col, macro, 'MULTIPLY')
    h = m.mix(gmask, m.mix(rut, A["height"], B["height"]), C["height"])
    nrm = m.bump(h, 0.9, 0.04)
    m.principled(**{'Base Color': col, 'Roughness': 0.93, 'Specular IOR Level': 0.12, 'Normal': nrm})
    return m.m


def mat_pebble():
    m = Mat("pebble")
    col = m.attr_color("Col")
    m.principled(**{'Base Color': col, 'Roughness': 0.88, 'Specular IOR Level': 0.25})
    return m.m


def mat_sack():
    m = Mat("sack")
    img = bpy.data.images.load(os.path.join(lib.TEX, "ricebag.png"), check_existing=True)
    t = m.node('ShaderNodeTexImage', image=img, projection='BOX', interpolation='Cubic')
    t.projection_blend = 0.1
    m.set(t.inputs['Vector'], m.mapping(scale=(1 / 0.5, 1 / 0.5, 1 / 0.5), loc=(0.3, 0.3, 0.3)))
    weave = m.voro(scale=90, feature='F1')
    col = m.mix(0.4, t.outputs['Color'], m.mix(1.0, t.outputs['Color'], m.ramp(weave, [(0, (1.1,) * 3), (1, (0.8,) * 3)]), 'MULTIPLY'))
    m.principled(**{'Base Color': col, 'Roughness': 0.9, 'Specular IOR Level': 0.1,
                    'Normal': m.bump(m.voro(scale=90, feature='F1'), 0.4, 0.01)})
    return m.m


def smooth(ob):
    ob.data.shade_smooth()
    return ob


def sample_noise(x, y, scale=1.0, seed=0.0):
    from mathutils import noise as mn
    return mn.noise(Vector((x * scale + seed, y * scale - seed, seed)))

UG_DEPTH = 7.2          # 地下駅・地下区間のレール面の深さ(m)。駅ホール床=地表-UG_DEPTH、覆工の上面=地表の下0.3m
