"""C14: 駅間(リンク)の沿線景観。柵・田畑(畦つき)・防風林・疎林・竹やぶを、線路ごとに乱数固定で並べる。
世界合成(--world)で kit4.build_links の最後に呼ばれる。環境変数 LINK_SCENERY=0 で無効。

設計:
  * 対象は地上の鉄道リンク(HM/SH/SR/HR/KE/YB の主線 ka==0)。地下・路面・モノレールは対象外。
  * 構造物区間(橋・トンネル・高架・築堤・海・踏切・こ線橋)の前後、リンク両端(駅圏)、他の線路の近傍は避ける。
  * 近傍の駅の町タイプ(rural/forest/alpine/urban/port...)でスタイル(田畑の割合・樹林の密度・樹種色)を決める。
  * 1リンク×1種類で1メッシュにまとめる(軽量化)。"""
import math
import random
import numpy as np
from mathutils import noise as mn, Vector
from common import M
import trackkit
import lib
from props import G

STYLE = {            # 町タイプ -> (田畑の割合, 樹木の密度, 針葉の割合, 竹・低木の割合)
    "rural": (0.70, 0.35, 0.15, 0.10), "suburb": (0.35, 0.30, 0.10, 0.10), "urban": (0.10, 0.18, 0.05, 0.05),
    "newtown": (0.20, 0.22, 0.08, 0.05), "campus": (0.25, 0.30, 0.10, 0.05), "forest": (0.05, 0.85, 0.55, 0.05),
    "alpine": (0.02, 0.60, 0.80, 0.0), "onsen": (0.10, 0.60, 0.40, 0.10), "port": (0.0, 0.10, 0.0, 0.0),
    "freight": (0.05, 0.12, 0.05, 0.0), "airport": (0.30, 0.10, 0.0, 0.0),
}
SKIP_KINDS_S = ("truss", "arch", "river", "tunnel", "cut", "viaduct", "trestle", "sea", "subway", "street", "mono")     # 築堤(embank)・雪覆い(shed)は線路際だけを占めるので除外しない
GRID = 12.0


def _grid(points):
    g = {}
    for p in points:
        g.setdefault((int(p[0] // GRID), int(p[1] // GRID)), []).append(p)
    return g


def _near(g, x, y, r):
    cx, cy = int(x // GRID), int(y // GRID)
    n = int(r // GRID) + 1
    r2 = r * r
    for ix in range(cx - n, cx + n + 1):
        for iy in range(cy - n, cy + n + 1):
            for p in g.get((ix, iy), ()):
                if (p[0] - x) ** 2 + (p[1] - y) ** 2 < r2:
                    return True
    return False


def _blob(c, rad, rng, seg=9, rings=6, k=0.45, flat=0.85):
    V = []
    for r in range(rings + 1):
        th = math.pi * r / rings
        for s in range(seg):
            ph = 2 * math.pi * s / seg
            d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
            n = mn.noise(d * 1.8 + Vector((c[0] * 0.3, c[1] * 0.3, c[2] * 0.3)))
            rr = rad * (1 + k * n)
            V.append((c[0] + d.x * rr, c[1] + d.y * rr, c[2] + d.z * rr * flat))
    return np.array(V), seg, rings


def _tris(off, seg, rings):
    T = []
    for r in range(rings):
        for s in range(seg):
            a0, a1 = r * seg + s, r * seg + (s + 1) % seg
            b0, b1 = (r + 1) * seg + s, (r + 1) * seg + (s + 1) % seg
            T += [(off + a0, off + b0, off + a1), (off + a1, off + b0, off + b1)]
    return T


def _cards(c, br, nr, bc, n, conif=False):
    """葉カード(小三角)を樹冠の表面に散らして、塊状のシルエットを崩す。"""
    V, T, C = [], [], []
    for i in range(n):
        d = nr.normal(size=3) * np.array([1, 1, 1.6 if conif else 0.75])
        d /= np.linalg.norm(d) + 1e-9
        p = np.array(c) + d * br * nr.uniform(0.82, 1.2)
        t1 = np.cross(d, [0, 0, 1.0])
        if np.linalg.norm(t1) < 1e-3:
            t1 = np.array([1.0, 0, 0])
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(d, t1)
        a0 = nr.uniform(0, 6.28)
        u = t1 * math.cos(a0) + t2 * math.sin(a0)
        v = -t1 * math.sin(a0) + t2 * math.cos(a0)
        sz = nr.uniform(0.16, 0.34)
        V += [p - u * sz * 0.5, p + u * sz * 0.5, p + v * sz + d * 0.04]
        sh = nr.uniform(0.0, 1.0) * (0.4 + 0.6 * (d[2] * 0.5 + 0.5))
        col = np.array(bc) * (0.7 + 1.1 * sh) * nr.uniform(0.8, 1.3)
        C += [list(col) + [1.0]] * 3
        T += [(3 * i, 3 * i + 1, 3 * i + 2), (3 * i, 3 * i + 2, 3 * i + 1)]
    return np.array(V), T, np.array(C)


def _skip_ranges(items, L):
    out = []
    for kind, kw in items:
        if kind in ("lc", "over"):
            s = kw.get("s", 0.0)
            out.append((s - 30.0, s + 30.0))
        elif kind in SKIP_KINDS_S:
            out.append((kw.get("s0", kw.get("s", 0.0)) - 45.0, kw.get("s1", kw.get("s", 0.0)) + 45.0))
    return out


def link_scenery(edges, struct_plan, station_origin, town_of, verbose=True):
    """edges: kit4.EDGES(リンク)。struct_plan(ln,a,b,L)->(prof,items)。station_origin(sid)->(x,y)。town_of(sid)->町タイプ。"""
    rail = [e for e in edges if e.get("kind") == "link" and e["line"] in ("HM", "SH", "SR", "HR", "KE", "YB")]
    allpts = []
    for e in edges:
        if e.get("kind") != "link":
            continue
        Pe, _ = trackkit.resample(np.asarray(e["pts"], float), 4.0)
        allpts += [tuple(p) for p in Pe]
    stn = []
    for e in edges:
        for sid in (e.get("a"), e.get("b")):
            if sid:
                try:
                    stn.append(tuple(station_origin(sid)))
                except Exception:
                    pass
    gall, gstn = _grid(allpts), _grid(stn)
    total = dict(trees=0, fields=0, fence=0)
    done_corr = set()
    for e in rail:
        ln, a, b = e["line"], e["a"], e["b"]
        if (e.get("ka", 0) != 0) and ln != "KE":
            continue
        key = (ln, a, b)
        if key in done_corr:
            continue
        done_corr.add(key)
        P = np.asarray(e["pts"], float)
        Pr, s_ = trackkit.resample(P, 2.0)
        L = float(s_[-1])
        if L < 230:
            continue
        try:
            _, items = struct_plan(ln, a, b, L)
        except Exception:
            items = []
        skips = _skip_ranges(items, L)
        if verbose:
            _cov = sum(max(0.0, min(hi, L) - max(lo, 0.0)) for lo, hi in skips)
            print('  scn', ln, a, b, 'L', round(L), 'skip', round(_cov), [k for k, _ in items])
        ta, tb = STYLE.get(town_of(a), STYLE["rural"]), STYLE.get(town_of(b), STYLE["rural"])
        rng = random.Random(sum(map(ord, f"{ln}{a}{b}")) * 7 + 11)
        nr_ = np.random.default_rng(sum(map(ord, f"{a}{b}")))
        tang = np.gradient(Pr, axis=0)
        tang /= (np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9)
        nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
        n = len(Pr)
        fv, ft = [], []          # 田畑
        lv = []                  # 畦
        tv, tt, tc = [], [], []  # 樹木
        pv = []                  # 柵

        def ok(i, off, clear):
            x, y = Pr[i, 0] + nrm[i, 0] * off, Pr[i, 1] + nrm[i, 1] * off
            if i < 22 or i > n - 22:
                _REJ["端"] += 1
                return None
            s = s_[i]
            if any(lo < s < hi for lo, hi in skips):
                _REJ["構造物"] += 1
                return None
            if _near(gstn, x, y, 60.0):
                _REJ["駅圏"] += 1
                return None
            if clear > 0 and _near(gall, x, y, clear):        # 他の線路(複線の相方を含む)が近い
                _REJ["他線"] += 1
                return None
            return (x, y)

        for side in (-1, 1):
            i = 22
            while i < n - 22:
                frac = i / n
                st = tuple(ta[k] * (1 - frac) + tb[k] * frac for k in range(4))
                kind = rng.random()
                seglen = int(rng.uniform(22, 55))          # 2m刻み → 44〜110m
                depth = rng.uniform(20.0, 55.0)
                i_end = min(i + seglen, n - 23)
                off0 = rng.uniform(11.0, 17.0)
                if kind < st[0] * 1.15:                  # 田畑(畦つき)
                    mid = (i + i_end) // 2
                    q = [ok(j, side * (off0 + d), 3.0) for j, d in ((i, 0.0), (i_end, 0.0), (i, depth), (i_end, depth), (mid, depth * 0.5))]
                    if all(v is not None for v in q):
                        harvest = rng.random() < 0.38
                        tone = rng.uniform(0.85, 1.15)
                        col = (0.30, 0.27, 0.10) if harvest else (0.13, 0.30, 0.07)
                        vv = []
                        nd = max(2, int(depth / 0.9) + 1)       # 畝(うね): 奥行き方向に0.9m刻みで高さと色を交互に
                        for j in range(i, i_end + 1, 2):
                            for kd in range(nd):
                                d = depth * kd / (nd - 1)
                                x, y = Pr[j, 0] + nrm[j, 0] * side * (off0 + d), Pr[j, 1] + nrm[j, 1] * side * (off0 + d)
                                vv.append((x, y, 0.02 + (0.07 if kd % 2 else 0.0)))
                        m = (i_end - i) // 2 + 1
                        base = sum(len(v) for v in fv)
                        arr = np.array(vv)
                        for k in range(m - 1):
                            for kd in range(nd - 1):
                                a0, a1 = base + k * nd + kd, base + k * nd + kd + 1
                                b0, b1 = base + (k + 1) * nd + kd, base + (k + 1) * nd + kd + 1
                                ft += [(a0, a1, b0), (b0, a1, b1)]
                        fv.append(arr)
                        fcol = np.array(col) * tone
                        stripe = np.array([(1.0 if kd % 2 else 0.72) for _ in range(m) for kd in range(nd)])[:, None]
                        fc = np.tile(np.append(fcol, 1.0), (len(arr), 1)) * np.concatenate([stripe * np.array([[1, 1, 1]]), np.ones((len(arr), 1))], 1) * nr_.uniform(0.9, 1.1, (len(arr), 1))
                        total["fields"] += 1
                        _FC.append(fc)
                        # 畦(道側の細い土手)
                        for j in range(i, i_end, 3):
                            x0, y0 = Pr[j, 0] + nrm[j, 0] * side * (off0 - 0.4), Pr[j, 1] + nrm[j, 1] * side * (off0 - 0.4)
                            x1, y1 = Pr[min(j + 3, i_end), 0] + nrm[min(j + 3, i_end), 0] * side * (off0 - 0.4), Pr[min(j + 3, i_end), 1] + nrm[min(j + 3, i_end), 1] * side * (off0 - 0.4)
                            lv.append(((x0, y0), (x1, y1)))
                i = i_end + int(rng.uniform(3, 18))
            # 樹木: 防風林の列と疎林(町タイプの密度)
            j = 22
            while j < n - 22:
                frac = j / n
                st = tuple(ta[k] * (1 - frac) + tb[k] * frac for k in range(4))
                clump = mn.noise(Vector((Pr[j, 0] * 0.006, Pr[j, 1] * 0.006, 1.0 + side)))
                dens = st[1] * (0.55 + 0.9 * (0.5 + 0.5 * clump))
                if rng.random() < dens * 0.9:
                    off = side * rng.uniform(9.0, 62.0) if rng.random() < 0.75 else side * rng.uniform(9.0, 16.0)
                    q = ok(j, off, 5.0)
                    if q is not None:
                        x, y = q
                        conif = rng.random() < st[2]
                        bam = (not conif) and rng.random() < st[3]
                        z = 0.0
                        rad = rng.uniform(2.2, 4.2) * (0.7 if conif else 1.0) * (0.75 if bam else 1.0)
                        hc = rng.uniform(3.2, 5.0) if not conif else rng.uniform(4.0, 7.0)
                        nl = 1 if conif else rng.choice((2, 2, 3))
                        for li in range(nl):
                            ox, oy = (0.0, 0.0) if li == 0 else (rng.uniform(-0.5, 0.5) * rad, rng.uniform(-0.5, 0.5) * rad)
                            rl = rad * (0.62 if conif else (0.9 if li == 0 else rng.uniform(0.5, 0.7)))
                            c = (x + ox, y + oy, z + hc + (0 if li == 0 else rng.uniform(-0.2, 0.7) * rad))
                            Vb, seg, rings = _blob(c, rl, rng, k=0.5)
                            if conif:
                                Vb[:, 2] = c[2] + (Vb[:, 2] - c[2]) * 2.0
                            base = sum(len(v) for v in tv)
                            tv.append(Vb)
                            tt += _tris(base, seg, rings)
                            if conif:
                                bc = np.array([0.014, 0.034, 0.020])
                            elif bam:
                                bc = np.array([0.060, 0.120, 0.030])
                            else:
                                bc = np.array([0.040, 0.085, 0.028]) * rng.uniform(0.8, 1.3)
                            sh = np.clip((Vb[:, 2] - z) / (hc * 2.0 + 1e-3), 0, 1)[:, None]
                            tc.append(np.concatenate([bc[None, :] * (0.55 + 0.9 * sh) * nr_.uniform(0.7, 1.35, (len(Vb), 1)), np.ones((len(Vb), 1))], 1))
                            cv, ct_, cc_ = _cards(c, rl, nr_, bc * 1.5, max(40, int(260 * rl * rl)), conif)
                            base2 = sum(len(v) for v in tv)
                            tv.append(cv)
                            tt += [(base2 + a, base2 + b, base2 + c2) for (a, b, c2) in ct_]
                            tc.append(cc_)
                        # 幹(細い角柱)
                        trunk = []
                        for dx, dy in ((-0.13, -0.13), (0.13, -0.13), (0.13, 0.13), (-0.13, 0.13)):
                            trunk.append((x + dx, y + dy, 0.0)); trunk.append((x + dx * 0.7, y + dy * 0.7, hc * 0.9))
                        base = sum(len(v) for v in tv)
                        tv.append(np.array(trunk))
                        for k in range(4):
                            a0, a1 = 2 * k, 2 * ((k + 1) % 4)
                            tt += [(base + a0, base + a1, base + a0 + 1), (base + a1, base + a1 + 1, base + a0 + 1)]
                        tc.append(np.tile(np.array([0.030, 0.020, 0.014, 1.0]), (8, 1)))
                        total["trees"] += 1
                j += max(1, int(rng.uniform(2, 9)))
            # 柵(線路際、区間でとぎれる)
            j = 22
            while j < n - 22:
                seglen = int(rng.uniform(20, 90))
                if rng.random() < 0.55:
                    for jj in range(j, min(j + seglen, n - 23), 3):
                        q = ok(jj, side * 6.4, 0)
                        q2 = ok(min(jj + 3, n - 23), side * 6.4, 0)
                        if q is None or q2 is None:
                            continue
                        pv.append((q, q2))
                j += seglen + int(rng.uniform(4, 30))
        if fv:
            V = np.concatenate(fv)
            import veg
            veg.np_mesh(f"scn_fields_{ln}_{a}_{b}", V, np.array(ft), M["leaf"], "Terrain", colors=np.concatenate(_FC), smooth=False)
        _FC.clear()
        if tv:
            import veg
            veg.np_mesh(f"scn_trees_{ln}_{a}_{b}", np.concatenate(tv), np.array(tt), M["leaf"], "Trees", colors=np.concatenate(tc), smooth=True)
        if pv or lv:
            g = G(f"scn_fence_{ln}_{a}_{b}", "Props")
            for (p0, p1) in pv:
                g.a("wood_dark").sbox((p0[0], p0[1], 0.0), (p0[0], p0[1], 1.15), 0.09, 0.09)
                g.a("iron_black").sbox((p0[0], p0[1], 0.55), (p1[0], p1[1], 0.55), 0.015, 0.015)
                g.a("iron_black").sbox((p0[0], p0[1], 0.95), (p1[0], p1[1], 0.95), 0.015, 0.015)
                total["fence"] += 1
            for (p0, p1) in lv:
                g.a("soil").sbox((p0[0], p0[1], 0.06), (p1[0], p1[1], 0.06), 0.55, 0.14)
            g.build()
    if verbose:
        print("link_scenery", total, dict(_REJ))
    return total


_FC = []
_REJ = __import__('collections').Counter()


def _cell_pts(g, x, y):
    cx, cy = int(x // GRID), int(y // GRID)
    for ix in range(cx - 1, cx + 2):
        for iy in range(cy - 1, cy + 2):
            for p in g.get((ix, iy), ()):
                yield p
