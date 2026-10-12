#!/bin/bash
# 作業ディレクトリ(/home/claude/station)→ GitHub用リポジトリ(/home/claude/train01)へ整理して同期する
S=/home/claude/station; R=/home/claude/train01
cd $R
git rm -r -q --cached . >/dev/null 2>&1
find . -mindepth 1 -maxdepth 1 ! -name .git ! -name CLAUDE.md -exec rm -rf {} +
mkdir -p src scripts docs data assets/textures assets/pbr_textures assets/candidates renders/{contact,eye,deliver,pano,zones,work} viewer
cp $S/*.py src/
cp $S/*.sh scripts/; mv scripts/sync_repo.sh scripts/sync_repo.sh 2>/dev/null
cp $S/audit_rubric.md $S/RECOVERY.md docs/
cp $S/README.md $R/README.md
cp $S/network.json $S/nodes.json $S/sky_nodes.json data/ 2>/dev/null
cp -r $S/net ./net; rm -rf net/__pycache__
python3 - <<'P'
import os,shutil,fnmatch
S='/home/claude/station'; R='/home/claude/train01'
def cp(src,dst,exts=None,skip=('__pycache__','*.blend','*.blend1')):
    for root,ds,fs in os.walk(src):
        ds[:]=[d for d in ds if not any(fnmatch.fnmatch(d,p) for p in skip)]
        for f in fs:
            if any(fnmatch.fnmatch(f,p) for p in skip): continue
            if exts and not f.lower().endswith(exts): continue
            o=os.path.join(dst,os.path.relpath(os.path.join(root,f),src)); os.makedirs(os.path.dirname(o),exist_ok=True); shutil.copy(os.path.join(root,f),o)
cp(S+'/tex',R+'/assets/textures')
cp(S+'/pbr',R+'/assets/pbr_textures',exts=('.jpg','.png'))
cp(S+'/cand',R+'/assets/candidates')
cp(S+'/dl',R+'/assets/candidates/dl')
cp(S+'/assets',R+'/assets/misc',skip=('__pycache__','*.blend'))
cp(S+'/viewer',R+'/viewer')
P
# 撮影画像: deliver は PNG のまま、他は JPEG(q90)
python3 - <<'P'
import os,glob
from PIL import Image
S='/home/claude/station/out'; R='/home/claude/train01/renders'
def conv(src,dst,png=False):
    if png:
        import shutil; shutil.copy(src,dst); return
    im=Image.open(src).convert('RGB'); im.save(dst.rsplit('.',1)[0]+'.jpg',quality=90,optimize=True)
for d in ['contact','eye','pano','zones']:
    for f in glob.glob(f'{S}/{d}/*.png')+glob.glob(f'{S}/{d}/*.jpg'):
        conv(f,f'{R}/{d}/'+os.path.basename(f))
for f in glob.glob(f'{S}/deliver/*'):
    if f.lower().endswith(('.png','.jpg')): conv(f,f'{R}/deliver/'+os.path.basename(f),png=True)
for f in glob.glob(f'{S}/*.png'):
    conv(f,f'{R}/work/'+os.path.basename(f))
P
cp -r $S/migration $R/migration; mkdir -p $R/.claude && cp -r $S/dotclaude/. $R/.claude/
find . -name '*emblem*' -not -path './.git/*' | head
cat > .gitignore <<'G'
*.blend
*.blend1
__pycache__/
G
