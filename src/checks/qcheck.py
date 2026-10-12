import sys, numpy as np
from PIL import Image
for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert("RGB")).astype(float)/255
    l = a.mean(2)
    print(f"{f}: mean={l.mean():.3f} white(>.98)={(l>.98).mean()*100:.2f}% black(<.02)={(l<.02).mean()*100:.2f}% "
          f"p5={np.percentile(l,5):.3f} p95={np.percentile(l,95):.3f}")
