"""Q2: 経年変化の統一パス。全マテリアルの Base Color に共通の汚れ(隅のAO汚れ・地際の泥はね・上向き面の埃/雨だれ)を重ねる。
素材ごとの個別汚れ(lib)の上に、共通の一貫した層を足す。発光/ガラス/水/空/雪の素材は除外。"""
import bpy

SKIP = ("glow", "glass", "lamp", "water", "sky", "snow", "hill", "emit", "window", "light", "wire", "leaf", "grass", "far", "rice")


def apply(strength=0.5):
    n = 0
    for m in bpy.data.materials:
        if not m.use_nodes or m.get("weathered"):
            continue
        if any(k in m.name.lower() for k in SKIP):
            continue
        nt = m.node_tree
        bsdf = next((x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None:
            continue
        inp = bsdf.inputs["Base Color"]
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.6; ao.samples = 4
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sep.inputs[0])
        zm = nt.nodes.new("ShaderNodeMapRange"); zm.inputs["From Min"].default_value = 0.0; zm.inputs["From Max"].default_value = 0.9
        zm.inputs["To Min"].default_value = 1.0; zm.inputs["To Max"].default_value = 0.0; zm.clamp = True
        nt.links.new(sep.outputs["Z"], zm.inputs["Value"])                      # 地際ほど汚れる(泥はね)
        inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(ao.outputs["AO"], inv.inputs[1])                          # 隅ほど汚れる
        fac = nt.nodes.new("ShaderNodeMath"); fac.operation = 'ADD'
        nt.links.new(inv.outputs[0], fac.inputs[0]); nt.links.new(zm.outputs["Result"], fac.inputs[1])
        top = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], top.inputs[0])
        dust = nt.nodes.new("ShaderNodeMath"); dust.operation = 'MULTIPLY'; dust.inputs[1].default_value = 0.35
        nt.links.new(top.outputs["Z"], dust.inputs[0])                         # 上向き面の埃
        fac2 = nt.nodes.new("ShaderNodeMath"); fac2.operation = 'ADD'
        nt.links.new(fac.outputs[0], fac2.inputs[0]); nt.links.new(dust.outputs[0], fac2.inputs[1])
        sc = nt.nodes.new("ShaderNodeMath"); sc.operation = 'MULTIPLY'; sc.use_clamp = True; sc.inputs[1].default_value = strength
        nt.links.new(fac2.outputs[0], sc.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs["B"].default_value = (0.42, 0.38, 0.33, 1.0)
        nt.links.new(sc.outputs[0], mix.inputs["Factor"])
        if inp.is_linked:
            src = inp.links[0].from_socket
            nt.links.new(src, mix.inputs["A"])
        else:
            mix.inputs["A"].default_value = inp.default_value
        nt.links.new(mix.outputs["Result"], inp)
        m["weathered"] = 1
        n += 1
    return n
