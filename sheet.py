import sys,glob
from PIL import Image
sid=sys.argv[1]; fs=sorted(glob.glob(f"/home/claude/station/tex/kit/{sid}_*.png"))
W=1800; x=y=0; rowh=0; pos=[]
ims=[]
for f in fs:
    im=Image.open(f).convert("RGB"); s=300/im.height if im.height>im.width*0.6 else 420/im.width
    im=im.resize((int(im.width*s),int(im.height*s))); ims.append(im)
sheet=Image.new("RGB",(W,1500),(60,60,60))
for im in ims:
    if x+im.width>W: x=0;y+=rowh+8;rowh=0
    sheet.paste(im,(x,y)); x+=im.width+8; rowh=max(rowh,im.height)
sheet.crop((0,0,W,y+rowh)).save(sys.argv[2])
