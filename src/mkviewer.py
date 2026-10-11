import json, os, shutil
from PIL import Image
nodes=json.load(open("nodes.json"))
os.makedirs("viewer/pano",exist_ok=True)
have=[]
for n in nodes:
    p=f"out/pano/{n['id']}.png"; q=f"viewer/pano/{n['id']}.jpg"
    if os.path.exists(p) and os.path.exists(f"out/pano/{n['id']}.png"):
        if not os.path.exists(q) or os.path.getmtime(p)>os.path.getmtime(q):
            Image.open(p).convert("RGB").save(q,quality=90,optimize=True,subsampling=0)
        have.append(n)
ids={n['id'] for n in have}
L=[("r6","n07"),("n07","p2"),("p3","pe"),("pe","r9"),("n12","sp"),("sp","d4"),("c2","c3"),("c3","d1"),("d1","d2"),("d2","d3"),("d3","d4"),("d1","d4"),("n14","c2"),("r9","c2"),("n13","n12"),("r8","pe"),("p1","n07")]
L=[l for l in L if l[0] in ids and l[1] in ids]
t=open("viewer/index.html").read() if not os.path.exists("viewer/tmpl.html") else open("viewer/tmpl.html").read()
if not os.path.exists("viewer/tmpl.html"): open("viewer/tmpl.html","w").write(t)
out=t.replace("__NODES__",json.dumps(have,ensure_ascii=False)).replace("__LINKS__",json.dumps(L))
# start node
open("viewer/index_built.html","w").write(out)
print(len(have),"nodes", sum(os.path.getsize(f"viewer/pano/{n['id']}.jpg") for n in have)/1e6,"MB")
