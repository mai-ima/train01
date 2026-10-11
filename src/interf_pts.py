import numpy as np, zone_stock
def pts(sid, xr=(-170, 170), step=1.5):
    import kit4, kit2
    n = len(kit4.local_tracks(sid)) if sid not in kit2.DESIGN else kit2.DESIGN[sid]["ntr"]
    out = []
    for k in range(n):
        for x in np.arange(xr[0], xr[1], step):
            tp = zone_stock._tpoint(sid, k, float(x))
            if tp: out.append((tp[0], tp[1]))
    return np.array(out) if out else np.zeros((0, 2))
