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
ZELKOVA_RATIO = float(__import__("os").environ.get("LINK_ZELKOVA", "0.5"))     # 沿線の広葉樹のうち、枝つきの樹形(veg.zelkova)にする割合
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
        p = np.array(c) + d * br * nr.uniform(0.68, 1.04)      # 内側〜表面に重ねる(外へ突き出すと黒い三角の破片に見える)
        t1 = np.cross(d, [0, 0, 1.0])
        if np.linalg.norm(t1) < 1e-3:
            t1 = np.array([1.0, 0, 0])
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(d, t1)
        a0 = nr.uniform(0, 6.28)
        u = t1 * math.cos(a0) + t2 * math.sin(a0)
        v = -t1 * math.sin(a0) + t2 * math.cos(a0)
        sz = nr.uniform(0.16, 0.32)       # C17/Q14: 近景で大きな平らな三角片の寄せ集めに見えた(gt4)→小さくして数を増やす
        V += [p - u * sz * 0.5, p + u * sz * 0.5, p + v * sz + d * 0.04]
        sh = nr.uniform(0.0, 1.0) * (0.4 + 0.6 * (d[2] * 0.5 + 0.5))
        col = np.array(bc) * (0.95 + 1.6 * sh) * nr.uniform(0.85, 1.35)
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
                except Exception as _e:
                    print("scenery station_origin failed", sid, _e)      # 駅の除外範囲が効かなくなる(healthscan の対象)
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
        except Exception as _e:
            print("scenery struct_plan failed", ln, a, b, _e)            # 構造物の除外が効かず、橋・踏切の上に樹木・畑が載る(healthscan の対象)
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
        fv, fts, fk = [], [], []   # 田畑(1区画ごとの頂点・三角形・刈田か)
        lv = []                  # 畦
        tv, tt, tc = [], [], []  # 樹木
        pv = []                  # 柵
        gp_, gh_, gs_ = [], [], []   # 沿線の地面草(位置・高さ・ススキか)

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
                        fallow = (not harvest) and rng.random() < 0.3              # C17: 耕起した褐色の畑も混ぜる(一様な緑を崩す)
                        col = (0.40, 0.33, 0.11) if harvest else ((0.24, 0.16, 0.08) if fallow else (0.10, 0.30, 0.06))
                        vv = []
                        nd = max(2, int(depth / 0.9) + 1)       # 畝(うね): 奥行き方向に0.9m刻みで高さと色を交互に
                        for j in range(i, i_end + 1, 2):
                            for kd in range(nd):
                                d = depth * kd / (nd - 1)
                                x, y = Pr[j, 0] + nrm[j, 0] * side * (off0 + d), Pr[j, 1] + nrm[j, 1] * side * (off0 + d)
                                vv.append((x, y, 0.02 + (0.07 if kd % 2 else 0.0)))
                        m = (i_end - i) // 2 + 1
                        arr = np.array(vv)
                        loc_t = []
                        for k in range(m - 1):
                            for kd in range(nd - 1):
                                a0, a1 = k * nd + kd, k * nd + kd + 1
                                b0, b1 = (k + 1) * nd + kd, (k + 1) * nd + kd + 1
                                loc_t += [(a0, a1, b0), (b0, a1, b1)]
                        fv.append(arr)
                        fts.append(loc_t)
                        fk.append(harvest)
                        fcol = np.array(col) * tone
                        stripe = np.array([(1.0 if kd % 2 else 0.58) for _ in range(m) for kd in range(nd)])[:, None]
                        fc = np.tile(np.append(fcol, 1.0), (len(arr), 1)) * np.concatenate([stripe * np.array([[1, 1, 1]]), np.ones((len(arr), 1))], 1) * nr_.uniform(0.9, 1.1, (len(arr), 1))
                        total["fields"] += 1
                        if verbose:
                            print("  field", ln, a, b, "harvest" if harvest else "green", [round(float(v)) for v in arr[len(arr) // 2][:2]])
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
                        nl = 1 if conif else (rng.choice((2, 3)) if bam else rng.choice((4, 5, 6, 7)))   # 広葉樹は枝先ごとの葉房を複数(球1個の塊状を避け、隙間のある不規則な樹冠に)
                        if (not conif) and (not bam) and rng.random() < ZELKOVA_RATIO:
                            try:        # 駅ゾーンと同じ枝つきの樹形(幹+主枝+葉房9個)。球塊の簡易樹より写実的
                                import veg
                                veg.zelkova(x, y, h=rng.uniform(7.0, 11.0), rad=rng.uniform(3.4, 5.0), seed=rng.randrange(10 ** 7))
                                nl = 0
                            except Exception as e:
                                print("scenery zelkova failed (fallback to blob)", e)
                        for li in range(nl):
                            if conif or bam or li == 0:
                                ox, oy = (0.0, 0.0) if li == 0 else (rng.uniform(-0.5, 0.5) * rad, rng.uniform(-0.5, 0.5) * rad)
                                rl = rad * (0.62 if conif else (0.9 if li == 0 else rng.uniform(0.5, 0.7)))
                                c = (x + ox, y + oy, z + hc + (0 if li == 0 else rng.uniform(-0.2, 0.7) * rad))
                            else:
                                ang_l = rng.uniform(0, 6.283)
                                dist_l = rng.uniform(0.45, 1.0) * rad
                                rl = rad * rng.uniform(0.42, 0.62)
                                c = (x + math.cos(ang_l) * dist_l, y + math.sin(ang_l) * dist_l, z + hc + rng.uniform(-0.35, 0.75) * rad)
                            Vb, seg, rings = _blob(c, rl, rng, k=0.5)
                            if conif:
                                Vb[:, 2] = c[2] + (Vb[:, 2] - c[2]) * 2.0
                            base = sum(len(v) for v in tv)
                            tv.append(Vb)
                            tt += _tris(base, seg, rings)
                            # C17/Q14: 沿線樹の葉色が草(0.1〜0.3)より遥かに暗く、遠目に青黒い塊に見えた(shed/桟橋/海の目視)。草地と並べて自然な暗い緑に引き上げる
                            if conif:
                                bc = np.array([0.030, 0.070, 0.040])
                            elif bam:
                                bc = np.array([0.110, 0.190, 0.050])
                            else:
                                bc = np.array([0.100, 0.170, 0.045]) * rng.uniform(0.8, 1.3)
                            sh = np.clip((Vb[:, 2] - z) / (hc * 2.0 + 1e-3), 0, 1)[:, None]
                            tc.append(np.concatenate([bc[None, :] * (0.55 + 0.9 * sh) * nr_.uniform(0.7, 1.35, (len(Vb), 1)), np.ones((len(Vb), 1))], 1))
                            cv, ct_, cc_ = _cards(c, rl, nr_, bc * 1.5, max(120, int(1100 * rl * rl)), conif)
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
            # C17: 沿線の地面草(草地が低周波のにじんだ塗りに見えた=近景の草ジオメトリが駅間に無かった)。線路際ほど密、離れるほど疎
            if GROUND_TUFTS:
                for j in range(22, n - 22, 2):
                    for _ in range(int(rng.uniform(14.0, 28.0))):
                        off = side * (3.6 + 26.0 * rng.random() ** 1.7)
                        q = ok(j, off, 4.0)
                        if q is None:
                            continue
                        gp_.append((q[0] + rng.uniform(-0.9, 0.9), q[1] + rng.uniform(-0.9, 0.9), 0.0))
                        gh_.append(0.16 + 0.42 * rng.random() ** 1.5)
                        gs_.append(rng.random() < 0.06)
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
        if "scn_paddy" not in M:      # 沿線用の青田: 周囲の草より少し明るい程度の稲の緑(共通の paddy は黄が強く、白っぽく飛んで見える)
            M["scn_paddy"] = lib.mat_paddy("scn_paddy", green=(0.085, 0.125, 0.022), yellow=(0.17, 0.165, 0.035))   # C17: 周囲の草より明るい淡いミント色の板に見えた → 反射率を約半分に
        for hv, mname in ((False, "scn_paddy"), (True, "stubble")):           # 青田=稲の列の材質、刈田=刈り株の材質(区画ごとに種別で分けて1メッシュずつ)
            sel = [i_ for i_ in range(len(fv)) if fk[i_] == hv]
            if not sel:
                continue
            import veg
            Vs, Ts, off_ = [], [], 0
            for i_ in sel:
                Vs.append(fv[i_]); Ts += [(a_ + off_, b_ + off_, c_ + off_) for (a_, b_, c_) in fts[i_]]; off_ += len(fv[i_])
            veg.np_mesh(f"scn_fields_{mname}_{ln}_{a}_{b}", np.concatenate(Vs), np.array(Ts), M[mname], "Terrain", smooth=False)
        _FC.clear()
        if tv:
            import veg
            veg.np_mesh(f"scn_trees_{ln}_{a}_{b}", np.concatenate(tv), np.array(tt), M["leaf"], "Trees", colors=np.concatenate(tc), smooth=True)
        if gp_:
            import veg as _vg
            _gp, _gh, _gs = np.array(gp_), np.array(gh_), np.array(gs_)
            for _nm, _m, _kw in (("tuft", ~_gs, dict(k=6, spread=0.15, wmean=0.024, cb=(0.06, 0.11, 0.022), ct=(0.25, 0.30, 0.08))),
                                 ("susuki", _gs, dict(k=7, spread=0.2, wmean=0.017, cb=(0.10, 0.12, 0.04), ct=(0.55, 0.50, 0.30), lean=0.45, jit=0.4))):
                if _m.any():
                    _Vv, _Tt, _Cc = _vg.tufts(_gp[_m][:, :2], _gp[_m][:, 2], _gh[_m] * (1.5 if _nm == "susuki" else 1.0), seed=sum(map(ord, f"{a}{b}")) % 977 + 5, **_kw)
                    _vg.emit(f"scn_gtuft_{_nm}_{ln}_{a}_{b}", _Vv, _Tt, _Cc, M["blade"])
            total["gtufts"] = total.get("gtufts", 0) + len(gp_)
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


GROUND_TUFTS = __import__('os').environ.get('LINK_TUFTS', '1') != '0'      # C17: 沿線の地面草(LINK_TUFTS=0 で無効)
_FC = []
_REJ = __import__('collections').Counter()


def _cell_pts(g, x, y):
    cx, cy = int(x // GRID), int(y // GRID)
    for ix in range(cx - 1, cx + 2):
        for iy in range(cy - 1, cy + 2):
            for p in g.get((ix, iy), ()):
                yield p
