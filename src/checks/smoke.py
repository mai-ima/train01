import bpy, lib
bpy.ops.wm.read_factory_settings(use_empty=True)
fs = [lib.mat_concrete("c", seam=2.0), lib.mat_ballast("b"), lib.mat_gravel("g"), lib.mat_asphalt("a"),
      lib.mat_planks("p"), lib.mat_wood("w"), lib.mat_plaster("pl"), lib.mat_kawara("k"), lib.mat_paint("pt",(0.7,0.7,0.7)),
      lib.mat_rail("r"), lib.mat_glass("gl"), lib.mat_image("i", "tex/ekimei.png"), lib.mat_grass_ground("gr"),
      lib.mat_paddy("pd"), lib.mat_vertex_color("vc"), lib.mat_bark("bk"), lib.mat_hill("h",(0,0,2)),
      lib.mat_emissive("e",(1,1,1)), lib.mat_stripes("s"), lib.mat_tactile("t")]
print("ok", len(fs))
