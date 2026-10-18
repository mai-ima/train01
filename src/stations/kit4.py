import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
"""kit4: 線路網。各駅ゾーンの入口/出口(座標・向き)を合わせ、駅間線路をエルミート曲線で連結する(自社・他社すべて)。
局所座標: +x = 路線の進行方向(order順)。終端駅は列車が入ってくる向きが +x。"""
import math, json
import numpy as np
from common import *
import lib, trackkit, props
from props import G
import kit, kit2, kit3, kit5, kit7
from kit2 import centerline, offs, LH, DESIGN

NET = kit.NET
SB = {s["id"]: s for s in NET["stations"]}
ORDER = NET["order"]
TERMINALS_START = {"M01"}           # order の先頭にあるが、列車が入る向きが逆の終端
OWN = {"HR", "TR", "BM"}     # 直通なし: 自駅の他社用線路(構内)から分岐
TECH = {"HM": "rail", "SH": "rail", "YB": "rail", "KE": "rail", "SR": "rail", "KM": "rail", "HR": "rail", "TR": "tram", "BM": "mono"}


def world(sid):
    w = SB[sid]["world"]
    return np.array([float(w[0]), float(w[1])])


def yaw_of(sid):
    st = SB[sid]
    ln = st["lines"][0]
    o = ORDER[ln]
    i = o.index(sid)
    if sid in TERMINALS_START:
        v = world(sid) - world(o[i + 1])
        return math.atan2(v[1], v[0])
    if i == len(o) - 1:
        v = world(sid) - world(o[i - 1])
        return math.atan2(v[1], v[0])
    if i == 0:
        v = world(o[1]) - world(sid)
        return math.atan2(v[1], v[0])
    a, b, c = world(o[i - 1]), world(sid), world(o[i + 1])
    bi = math.atan2(*(b - a)[::-1])
    return bi + bend(sid) / 2


SMALL = {"SH02": 80, "SH03": 80, "SH04": 90, "SH05": 80, "SH06": 90, "SH07": 80, "SH08": 80, "L01": 55, "M15": 80, "M18": 85, "M09": 100, "Y02": 80, "Y03": 80, "Y04": 80, "S02": 80, "S03": 80, "S04": 80, "B02": 90, "TR02": 90, "R02": 90,
         "M07": 120, "M05": 130, "T02": 110, "T03": 110, "T04": 110, "K02": 110, "K03": 110, "M13": 90, "M17": 100, "F01": 110, "M02": 110, "M03": 110}


def compute_reach(lmax=160.0, margin=30.0):
    """各駅の(後ろ, 前)の線路長。本線の隣駅との間隔と相手の規模から決める。国都中央は後ろ300m。"""
    R = {}
    for s, st in SB.items():
        o = ORDER[st["lines"][0]]
        i = o.index(s)
        out = []
        for j in (i - 1, i + 1):
            if j < 0 or j >= len(o):
                out.append(lmax if s != "M01" else 300.0)
                continue
            n = o[j]
            d = float(np.linalg.norm(world(s) - world(n)))
            rn = 300.0 if n == "M01" else SMALL.get(n, min(lmax, (d - margin) / 2))
            rs = SMALL.get(s, lmax)
            out.append(max(45.0, min(rs, d - margin - rn if n == "M01" or s in SMALL or n in SMALL else (d - margin) / 2, lmax)))
        if s == "M01":
            out = [300.0, 300.0]
        R[s] = tuple(out)
    return R


def bend(sid):
    st = SB[sid]
    o = ORDER[st["lines"][0]]
    i = o.index(sid)
    if i == 0 or i == len(o) - 1:
        return 0.0
    a, b, c = world(o[i - 1]), world(sid), world(o[i + 1])
    bi, bo = math.atan2(*(b - a)[::-1]), math.atan2(*(c - b)[::-1])
    return (bo - bi + math.pi) % (2 * math.pi) - math.pi


REACH_V = compute_reach()
for _s, (_rb, _rf) in REACH_V.items():
    kit2.REACH[_s] = (int(_rb), int(_rf))
    kit.REACH[_s] = (_rb, _rf)
    if _s in DESIGN and abs(bend(_s)) > math.radians(12):
        _d = bend(_s)
        _T = min(_rb, _rf)
        _Rc = _T / math.tan(abs(_d) / 2)
        kit2.CURVE_OVERRIDE[_s] = math.copysign(_Rc, _d)
        _x = int(_Rc * math.sin(abs(_d) / 2))
        kit2.REACH[_s] = (_x, _x)


def local_tracks(sid):
    """-> list of dicts per track k: back=(x,y,ang) front=(x,y,ang) (local frame). 外向き接線。"""
    st = SB[sid]
    out = []
    if sid == "M01":
        ys, groups, fan = kit3.m01_layout()
        for i in range(len(ys)):
            out.append(dict(back=(-300.0, fan[i], math.pi), front=None, grp=[g[0] for g in groups if g[1] <= i < g[2]][0]))
        return out
    if sid in kit3.LAYOUT:
        return kit3.LAYOUT[sid]()
    if sid in DESIGN:
        d = DESIGN[sid]
        kc, kv = d["curve"]
        P = centerline(kc, R=kv if kc == "arc" else 0, amp=kv if kc == "S" else 0) if sid not in kit2.CURVE_OVERRIDE else centerline("arc", R=kit2.CURVE_OVERRIDE[sid], flat=False)
        ntr, plat = d["ntr"], d["plat"]
        offsets = kit2.track_offsets(plat, ntr)
        rb, rf = kit2.REACH.get(sid, (LH, LH))
        for off in offsets:
            Pk = offs(P, off)[LH - rb: LH + rf + 1]
            tf, _ = trackkit.frames(Pk)
            a_back = math.atan2(-tf[0, 1], -tf[0, 0])
            a_fwd = math.atan2(tf[-1, 1], tf[-1, 0])
            out.append(dict(back=(float(Pk[0, 0]), float(Pk[0, 1]), a_back), front=(float(Pk[-1, 0]), float(Pk[-1, 1]), a_fwd)))
        return out
    if sid == "M06":
        return [dict(back=(-140.0, 0.0, math.pi), front=(140.0, 0.0, 0.0)) for _ in range(2)]
    lay = st["layout"]
    if lay.startswith("terminal_stub") and st["tracks"] > 1:    # kit.terminal(): ys=-i*5.2, x -100..36
        n = min(st["tracks"], 12)
        return [dict(back=(-100.0, -i * 5.2, math.pi), front=None) for i in range(n)]
    ys = [0.0, -8.4] if (lay.startswith("island") or lay.startswith("elevated_island") or lay.startswith("underground_island")) else [0.0, -4.6]
    SPEC = {"K02": [0.0, -4.6, -9.2, -13.8], "K03": [0.0, -8.4, -13.0], "TR02": [0.0, 4.8]}
    if sid in SPEC:
        ys = SPEC[sid]
        rr = kit.REACH.get(sid, (120.0, 120.0))
        return [dict(back=(-min(120.0, rr[0]), y, math.pi), front=(min(120.0, rr[1]), y, 0.0)) for y in ys]
    ys = ys[:max(1, min(2, st["tracks"]))] if not lay.startswith("underground_island") else ys
    rr = kit.REACH.get(sid, (120.0, 120.0))
    return [dict(back=(-min(120.0, rr[0]), y, math.pi), front=(min(120.0, rr[1]), y, 0.0)) for y in ys]


def origin(sid):
    """曲線駅は、弧の両端が入出線の直線上に乗るよう頂点Vから内側へずらす。"""
    if sid in kit2.CURVE_OVERRIDE:
        R = kit2.CURVE_OVERRIDE[sid]
        d = bend(sid)
        yaw = yaw_of(sid)
        sh = abs(R) * (1 / math.cos(d / 2) - 1)
        sgn = 1 if d > 0 else -1
        return world(sid) + np.array([-math.sin(yaw), math.cos(yaw)]) * sgn * sh
    return world(sid)


def to_world(sid, p):
    yaw = yaw_of(sid)
    c, s = math.cos(yaw), math.sin(yaw)
    x, y = p[0], p[1]
    return np.array([c * x - s * y, s * x + c * y]) + origin(sid), yaw + p[2]


def end_world(sid, k, which):
    t = local_tracks(sid)
    k = min(k, len(t) - 1)
    e = t[k][which]
    if e is None:
        return None
    return to_world(sid, e)


def hermite(p0, a0, p1, a1, n=None, k=None):
    if k is None:
        best = None
        for kk in (0.45, 0.6, 0.8, 1.0, 1.3, 1.7, 2.2, 3.0):
            P = hermite(p0, a0, p1, a1, n, kk)
            r = min_radius(P)
            if best is None or r > best[0]:
                best = (r, P)
        return best[1]
    d = np.linalg.norm(p1 - p0)
    m0 = np.array([math.cos(a0), math.sin(a0)]) * d * k
    m1 = -np.array([math.cos(a1), math.sin(a1)]) * d * k       # a1 は B の外向き接線 → 進入方向は逆
    n = n or max(8, int(d / 4))
    t = np.linspace(0, 1, n)[:, None]
    h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
    return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1


def min_radius(P):
    P, _ = trackkit.resample(P, 5.0)
    t = np.gradient(P, axis=0)
    ang = np.unwrap(np.arctan2(t[:, 1], t[:, 0]))
    dth = np.abs(np.diff(ang))
    return 5.0 / max(dth.max(), 1e-6)


def pick_ends(a, b, ka, kb):
    """A,B の端のうち互いに近い組を選ぶ。"""
    best = None
    for wa in ("back", "front"):
        ea = end_world(a, ka, wa)
        if ea is None:
            continue
        for wb in ("back", "front"):
            eb = end_world(b, kb, wb)
            if eb is None:
                continue
            va = eb[0] - ea[0]
            dn = np.linalg.norm(va) + 1e-6
            ca = (math.cos(ea[1]) * va[0] + math.sin(ea[1]) * va[1]) / dn
            cb = (math.cos(eb[1]) * -va[0] + math.sin(eb[1]) * -va[1]) / dn
            dist = dn * (2.0 - 0.5 * (ca + cb)) + (0 if (ca > -0.25 and cb > -0.25) else 1e5)
            if best is None or dist < best[0]:
                best = (dist, ea, eb)
    return best


def link_list():
    """[(line, a, b, ka, kb)] — 本線は複線区間で2本、分岐・他社は外側の線路を使う。"""
    sect = {(s[0], s[1]): s[2] for s in NET["sect"]}
    L = []
    for ln, o in ORDER.items():
        for i in range(len(o) - 1):
            a, b = o[i], o[i + 1]
            kind = sect.get((a, b), "")
            nka, nkb = len(local_tracks(a)), len(local_tracks(b))
            primary = SB[a]["lines"][0] == ln and SB[b]["lines"][0] == ln
            if ln == "HM" or primary:
                L.append((ln, a, b, 0, 0))
                if kind.startswith("複線") and min(nka, nkb) > 1:
                    L.append((ln, a, b, 1, 1))
            else:
                ka = nka - 1 if SB[a]["lines"][0] != ln else 0
                kb = nkb - 1 if SB[b]["lines"][0] != ln else 0
                if a == "M01":
                    ka = {"KE": 14, "KM": 18}.get(ln, 0)
                if b == "M01":
                    kb = {"KE": 14, "KM": 18}.get(ln, 0)
                L.append((ln, a, b, ka, kb))
    return L


ENDONLY = set()


def own_polylines(sid, nlast=3):
    """駅内の外側線路(他社用)のワールド座標折れ線。分岐の起点候補。"""
    out = {}
    yaw = yaw_of(sid)
    c, s = math.cos(yaw), math.sin(yaw)
    nt = len(local_tracks(sid))
    for k in range(max(0, nt - nlast), nt):
        t = local_tracks(sid)[k]
        b, fr = t["back"], t["front"]
        if t.get("poly"):
            Pk = np.array(t["poly"], float)
            Pk = np.stack([np.interp(np.linspace(0, 1, 40), [0, 1], Pk[:, 0]), np.interp(np.linspace(0, 1, 40), [0, 1], Pk[:, 1])], 1)
        elif sid in DESIGN:
            d = DESIGN[sid]
            kc, kv = d["curve"]
            P = centerline(kc, R=kv if kc == "arc" else 0, amp=kv if kc == "S" else 0) if sid not in kit2.CURVE_OVERRIDE else centerline("arc", R=kit2.CURVE_OVERRIDE[sid], flat=False)
            ntr, plat = d["ntr"], d["plat"]
            offsets = kit2.track_offsets(plat, ntr)
            rb, rf = kit2.REACH.get(sid, (LH, LH))
            Pk = offs(P, offsets[k])[LH - rb: LH + rf + 1]
        else:
            x0 = b[0]
            x1 = fr[0] if fr is not None else 36.0
            xs = np.linspace(x0, x1, 40)
            Pk = np.stack([xs, np.full_like(xs, b[1])], 1)
        W = np.stack([c * Pk[:, 0] - s * Pk[:, 1], s * Pk[:, 0] + c * Pk[:, 1]], 1) + origin(sid)
        out[("own", sid, k)] = W
        if t.get("endonly"):
            ENDONLY.add(("own", sid, k))
    return out


def own_end_candidates(o, ln):
    """分岐線の自駅側端点(外向き接線つき)。複数の線路・両端を候補にする。"""
    out = []
    n = len(local_tracks(o))
    ks = [0] if SB[o]["lines"][0] == ln else list(range(max(0, n - 4), n))
    if o == "M01":
        ks = list(range(14, 20))
    for k in ks:
        for wh in ("back", "front"):
            e = end_world(o, k, wh)
            if e is not None:
                out.append((k, e))
    return out


def best_junction(j, o, ln, mainP):
    """junction 駅 j の本線上に分岐点を探す。-> (R, P, k)。"""
    best = None
    for (key, Q) in mainP.items():
        if key[0] != "own" and j not in key[:2]:
            continue
        Qr, s = trackkit.resample(Q, 1.0)
        t, _ = trackkit.frames(Qr)
        rng_i = range(len(Qr) - 9, len(Qr) - 3, 2) if key in ENDONLY else range(25, len(Qr) - 25, 7)
        for i in rng_i:
            for sgn in (1, -1):
                a0 = math.atan2(t[i, 1] * sgn, t[i, 0] * sgn)
                for k, e in own_end_candidates(o, ln):
                    P = hermite(Qr[i], a0, e[0], e[1])
                    r = min_radius(P)
                    L = float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1)))
                    sc = min(r, 400) - 0.02 * L
                    if best is None or sc > best[0]:
                        best = (sc, r, P, k)
    return best


def build_links(only=None, verbose=True):
    rep = []
    poles = G("net_poles", "Props")
    mainP = {}
    todo = []
    for (ln, a, b, ka, kb) in link_list():
        if only and ln not in only:
            continue
        ja = SB[a]["lines"][0] != ln and a != "M01"
        jb = SB[b]["lines"][0] != ln and b != "M01"
        if (ja or jb) and ln in OWN:
            todo.append((ln, a, b, ka, kb, ja, jb))
            continue
        if ja or jb:
            todo.append((ln, a, b, ka, kb, ja, jb))
            continue
        pk = pick_ends(a, b, ka, kb)
        if a == "M01" or b == "M01":                      # 国都中央の他社線: 出入口の線路を最良に選ぶ
            best = None
            for kk in range(14, 20):
                p2 = pick_ends(a, b, kk if a == "M01" else ka, kk if b == "M01" else kb)
                if p2 is None:
                    continue
                P2 = hermite(p2[1][0], p2[1][1], p2[2][0], p2[2][1])
                r2 = min_radius(P2)
                if best is None or r2 > best[0]:
                    best = (r2, p2, kk)
            if best:
                pk = best[1]
                ka, kb = (best[2], kb) if a == "M01" else (ka, best[2])
        _, ea, eb = pk
        P = hermite(ea[0], ea[1], eb[0], eb[1])
        emit(ln, a, b, ka, kb, P, rep, poles, mainP)
    for (ln, a, b, ka, kb, ja, jb) in todo:
        j, o = (a, b) if ja else (b, a)
        bj = best_junction(j, o, ln, own_polylines(j) if ln in OWN else mainP)
        if bj is None:
            rep.append((ln, a, b, "分岐点なし"))
            continue
        _, r, P, k = bj
        if ja:      # 向きは a→b にそろえる(線路としては向き無関係)
            pass
        emit(ln, a, b, ka, k, P, rep, poles, mainP, junction=j)
    poles.build()
    if verbose:
        for r in rep:
            print("link", r)
    return rep


EDGES = []
SZ = {"K03": 7.5}
DEPTH = UG_DEPTH            # 地下駅・地下区間のレール面の深さ(m)
MONO_Z0, MONO_Z1 = 8.2, 9.0   # 大湊のモノレール桁高 → 湾岸公園          # 駅の線路の高さ(高架駅)


def struct_plan(ln, a, b, L):
    """区間ごとの構造物計画。profile=[(s0,s1,h,ramp)] は線路の高低、items=[(関数名, kwargs)]。fractions は区間長 L に対する割合。"""
    prof, items = [], []
    key = (a, b)
    fr = lambda x: x * L
    if key == ("M03", "M04"):
        items += [("truss", dict(s0=fr(0.5) - 71, s1=fr(0.5) + 71, width=11.0)), ("river", dict(s=fr(0.5), width=60.0))]
    elif key == ("M05", "M06"):
        items += [("lc", dict(s=fr(x))) for x in (0.3, 0.55, 0.8)]
    elif key == ("M06", "M07"):
        prof += [(fr(0.08), fr(0.4), 2.0, 40.0)]       # 分岐(穂波空港線)が s≈164 にあるので、築堤はその手前で降りきる
        items += [("embank", dict(s0=fr(0.08), s1=fr(0.4), h=2.0))]
    elif key == ("M07", "M08"):
        items += [("over", dict(s=fr(0.5)))]
    elif key == ("M08", "M09"):
        items += [("cut", dict(s0=fr(0.2), s1=fr(0.8), trees=18, seed=1))]
    elif key == ("M09", "M10"):
        s0, s1 = fr(0.5) - 48, fr(0.5) + 48
        prof += [(s0 - 112, s1 + 112, 7.0, 110.0)]
        items += [("arch", dict(s0=s0, s1=s1, rise=4.0)), ("river", dict(s=fr(0.5), width=30.0, wiggle=30.0))]
    elif key == ("M11", "M12"):
        items += [("tunnel", dict(s0=fr(0.2), s1=fr(0.9))), ("shed", dict(s0=fr(0.05), s1=fr(0.2)))]
    elif key == ("M12", "M13"):
        items += [("shed", dict(s0=fr(0.1), s1=fr(0.95)))]
    elif key == ("L01", "M14"):
        s0, s1 = fr(0.1), fr(0.5)
        prof += [(s0 - 42, s1 + 42, 5.0, 40.0)]
        items += [("truss", dict(s0=s0, s1=s1, width=5.0)), ("river", dict(s=(s0 + s1) / 2, width=24.0, wiggle=15.0)), ("tunnel", dict(s0=fr(0.62), s1=fr(0.95)))]
    elif key == ("M14", "M15"):
        prof += [(fr(0.05), fr(0.95), 2.5, 50.0)]
        items += [("embank", dict(s0=fr(0.05), s1=fr(0.95), h=2.5)), ("sea", dict(s0=fr(0.1), s1=fr(0.9)))]
    elif key == ("M15", "M16"):
        items += [("tunnel", dict(s0=fr(0.35), s1=fr(0.6))), ("sea", dict(s0=fr(0.05), s1=fr(0.3))), ("sea", dict(s0=fr(0.65), s1=fr(0.95)))]
    elif key == ("M17", "M18"):
        items += [("cut", dict(s0=fr(0.15), s1=fr(0.85), trees=10, seed=4))]
    elif key == ("M18", "M19"):
        prof += [(fr(0.05), fr(0.93), 2.5, 60.0)]
        items += [("embank", dict(s0=fr(0.05), s1=fr(0.93), h=2.5)), ("sea", dict(s0=fr(0.1), s1=fr(0.9)))]
    elif key == ("Y02", "Y03"):
        items += [("truss", dict(s0=fr(0.5) - 18, s1=fr(0.5) + 18, width=4.2)), ("river", dict(s=fr(0.5), width=14.0, wiggle=12.0))]
    elif key == ("S02", "S03"):
        items += [("cut", dict(s0=fr(0.25), s1=fr(0.75), trees=8, seed=7))]
    elif key == ("S03", "S04"):
        s0, s1 = fr(0.5) - 15, fr(0.5) + 15
        prof += [(s0 - 5, s1 + 5, 3.0, 25.0)]
        items += [("trestle", dict(s0=s0, s1=s1)), ("river", dict(s=fr(0.5), width=10.0, wiggle=10.0))]
    elif key == ("SH02", "SH03"):
        prof += [(fr(0.1), fr(0.9), 2.0, 40.0)]
        items += [("over", dict(s=fr(0.15))), ("embank", dict(s0=fr(0.1), s1=fr(0.9), h=2.0))]
    elif key == ("SH03", "SH04"):
        s0, s1 = fr(0.2), fr(0.8)
        prof += [(s0 - 20, s1 + 20, 6.0, 30.0)]
        items += [("viaduct", dict(s0=s0, s1=s1)), ("river", dict(s=fr(0.5), width=22.0, wiggle=14.0))]
    elif key == ("SH04", "SH05"):
        prof += [(fr(0.1), fr(0.9), 2.0, 40.0)]
        items += [("embank", dict(s0=fr(0.1), s1=fr(0.9), h=2.0)), ("over", dict(s=fr(0.5)))]
    elif key == ("SH05", "SH06"):
        items += [("cut", dict(s0=fr(0.2), s1=fr(0.8), trees=8, seed=11)), ("over", dict(s=fr(0.5)))]
    elif key == ("SH06", "SH07"):
        prof += [(fr(0.1), fr(0.9), 1.8, 40.0)]
        items += [("embank", dict(s0=fr(0.1), s1=fr(0.9), h=1.8))]
    elif key == ("M01", "T02"):
        prof = kit7.ramp_fn([(0, 0), (90, 0), (90 + 7.2 / 0.027, -DEPTH), (L + 1, -DEPTH)], ease=16)
        items += [("subway", dict(s0=60.0, s1=L))]
    elif key == ("T02", "T03"):
        prof = kit7.ramp_fn([(0, -DEPTH), (L, -DEPTH)], ease=4)
        items += [("subway", dict(s0=0.0, s1=L))]
    elif key == ("T03", "T04"):
        prof = kit7.ramp_fn([(0, -DEPTH), (8, -DEPTH), (L - 6, 0.0), (L + 1, 0.0)], ease=10)
        items += [("subway", dict(s0=0.0, s1=L))]
    elif key == ("M01", "K02"):
        prof = kit7.ramp_fn([(0, 0), (90, 0), (90 + 7.2 / 0.027, -DEPTH), (L + 1, -DEPTH)], ease=16)
        items += [("subway", dict(s0=60.0, s1=L))]
    elif key == ("K02", "K03"):
        zk = SZ["K03"]
        prof = kit7.ramp_fn([(0, -DEPTH), (14, -DEPTH), (L - 14, zk), (L + 1, zk)], ease=14)
        items += [("subway", dict(s0=0.0, s1=fr(0.5))), ("viaduct", dict(s0=fr(0.5), s1=L, width=7.6))]
    elif key == ("K03", "M03"):
        zk = SZ["K03"]
        prof = kit7.ramp_fn([(-1, zk), (0.10 * L, zk), (0.29 * L, 0.0), (L + 1, 0.0)], ease=12)
        items += [("viaduct", dict(s0=0.0, s1=0.27 * L, width=7.6))]
    elif key == ("M19", "TR02"):
        items += [("street", dict(s0=0.0, s1=L))]
    elif key == ("M19", "B02"):
        prof = kit7.ramp_fn([(0, MONO_Z0), (L, MONO_Z1)], ease=20)
        items += [("mono", dict(s0=0.0, s1=L))]
    if a in SZ and key != ("K03", "M03"):
        pass
    return prof, items


def run_items(P, items, zfun, nm, shift_vec=None):
    for (kind, kw) in items:
        n = f"{nm}_{kind}_{int(kw.get('s0', kw.get('s', 0)))}"
        if kind == "truss":
            kit5.truss_bridge(P, name=n, zfun=zfun, **kw)
        elif kind == "arch":
            kit5.arch_bridge(P, name=n, zfun=zfun, **kw)
        elif kind == "river":
            kit5.river(P, name=n, **kw)
        elif kind == "tunnel":
            kit5.tunnel(P, name=n, zfun=zfun, **kw)
        elif kind == "shed":
            kit5.snowshed(P, name=n, zfun=zfun, **kw)
        elif kind == "cut":
            kit5.cutting(P, name=n, **kw)
        elif kind == "embank":
            kit5.embankment(P, name=n, **kw)
        elif kind == "over":
            kit5.overbridge(P, name=n, **kw)
        elif kind == "lc":
            kit5.level_crossing(P, name=n, **kw)
        elif kind == "viaduct":
            kit5.viaduct(P, name=n, zfun=zfun, **kw)
        elif kind == "trestle":
            kit5.trestle(P, name=n, zfun=zfun, **kw)
        elif kind == "sea":
            kit5.seawall(P, name=n, **kw)
        elif kind == "subway":
            kit7.subway(P, name=n, zfun=zfun, **kw)
        elif kind == "street":
            kit7.street(P, name=n, zfun=zfun, **kw)
        elif kind == "mono":
            kit7.mono_link(P, name=n, zfun=zfun, **kw)


def _power(line, a, b):
    od = NET.get("order", {}).get(line, [])
    for el in NET.get("elec", []):
        if el["line"] != line or a not in od or b not in od or el["a"] not in od or el["b"] not in od:
            continue
        lo, hi = sorted((od.index(el["a"]), od.index(el["b"])))
        if lo <= od.index(a) <= hi and lo <= od.index(b) <= hi:
            return el["sys"]
    return None


def emit(ln, a, b, ka, kb, P, rep, poles, mainP, junction=None):
    EDGES.append(dict(id=f"{ln}_{a}_{b}_{ka}_{kb}", line=ln, kind="link", a=a, b=b, ka=ka, kb=kb, junction=junction, pts=P))
    r = min_radius(P)
    nm = f"net_{ln}_{a}_{b}_{ka}_{kb}"
    tech = TECH[ln]
    Pr, s_ = trackkit.resample(np.asarray(P, float), 1.0)
    L_ = float(s_[-1])
    prof, items = struct_plan(ln, a, b, L_) if ((not junction and ka == 0) or ln in ("KM", "KE", "TR", "BM")) else ([], [])
    zf = (prof if callable(prof) else kit5.make_zfun(prof)) if (callable(prof) or prof) else None
    if SZ.get(b) and not junction and ka == 0 and (a, b) != ("K02", "K03"):
        pass
    if junction and tech == "rail" and len(Pr) > 80:
        # 分岐線の始端は本線と重なる: 重なる区間(横ずれ<2.4m)はバラストを省き、離れてから通常に敷く
        t0 = Pr[6] - Pr[0]
        t0 = t0 / np.linalg.norm(t0)
        n0 = np.array([-t0[1], t0[0]])
        lat = np.abs((Pr - Pr[0]) @ n0)
        i0 = int(np.argmax(lat >= 2.4)) if (lat >= 2.4).any() else 30
        i0 = max(12, min(i0, len(Pr) - 20))
        trackkit.build_track(nm + "_a", Pr[:i0 + 1], wooden=True, ballast=False, fittings=True, cam=None, zfun=zf)
        trackkit.build_track(nm, Pr[i0:], wooden=True, ballast=True, fittings=True, cam=None, zfun=zf)
    elif tech == "mono":
        pass       # 桁は kit7.mono_link(struct_plan の "mono")が作る
    elif tech == "tram":
        trackkit.build_track(nm, P, wooden=False, ballast=False, fittings=False, cam=None, zfun=zf)
    else:
        trackkit.build_track(nm, P, wooden=True, ballast=(tech == "rail"), fittings=(tech == "rail"), cam=None, zfun=zf)
    if items:
        kit5.mats5()
        run_items(Pr, items, zf, nm)
    if junction and TECH[ln] == "rail":
        try:
            kit5.turnout(Pr, name=nm + "_pt")
        except Exception as e_:
            print("turnout fail", nm, e_)
    pw = _power(ln, a, b)
    if pw and tech == "rail" and not any(k_ == "subway" for k_, _ in items):
        try:
            kit5.catenary(Pr, 20.0, L_ - 20.0, name=nm + "_cat", zfun=zf, side=(1 if ka == 0 else -1), ac=("交流" in pw))
        except Exception as e_:
            print("catenary fail", nm, e_)
    if ln == "HM":
        mainP[(a, b, ka)] = P
    rep.append((ln, a, b, ka, kb, round(float(np.linalg.norm(P[-1] - P[0])), 1), round(r), "分岐@" + junction if junction else ""))
    if ka == 0 and tech == "rail":
        Q, s = trackkit.resample(P, 1.0)
        t, n = trackkit.frames(Q)
        for si in np.arange(30.0, s[-1] - 30.0, 55.0):
            i = int(si)
            if zf is not None and (float(zf(si)) < -0.3 or float(zf(si)) > 1.5):
                continue
            q = Q[i] + n[i] * 3.6
            props.pole(poles, float(q[0]), float(q[1]), h=8.0, arms=((7.4, 0.9, 3),), axis='y', old=True)


def export_graph(path=f"{_R}/net/track_graph.json"):
    """運転準備: 軌道グラフ(後から列車を走らせるためのデータ)。座標はワールド(m)、折れ線は2m間隔、s=弧長。"""
    sect = {(s[0], s[1]): s for s in NET["sect"]}
    edges, stops = [], []

    def dens(P):
        Q, s = trackkit.resample(np.asarray(P), 2.0)
        return Q, s

    order = NET.get("order", {})

    def power(line, a, b):
        od = order.get(line, [])
        for el in NET.get("elec", []):
            if el["line"] != line or a not in od or b not in od or el["a"] not in od or el["b"] not in od:
                continue
            lo, hi = sorted((od.index(el["a"]), od.index(el["b"])))
            if lo <= od.index(a) <= hi and lo <= od.index(b) <= hi:
                return el["sys"]
        return None

    for e in EDGES:
        Q, s = dens(e["pts"])
        sc = sect.get((e["a"], e["b"])) or sect.get((e["b"], e["a"]))
        pw = power(e["line"], e["a"], e["b"])
        edges.append(dict(id=e["id"], line=e["line"], kind=e["kind"], from_station=e["a"], to_station=e["b"], length=round(float(s[-1]), 1),
                          speed_kmh=(sc[4] if sc else None), block=(sc[3] if sc else None), junction=e["junction"],
                          electrified=bool(pw), power=pw,
                          pts=[[round(float(x), 2), round(float(y), 2)] for x, y in Q]))
    for sid in SB:
        for key, W in own_polylines(sid, nlast=64).items():
            Q, s = dens(W)
            _ln = SB[sid]["lines"][0]
            if sid == "M19":   # 大湊: 4-7=市電(TR) 8-9=モノレール(BM) は別技術の網
                _ln = "TR" if 4 <= key[2] <= 7 else ("BM" if key[2] >= 8 else _ln)
            edges.append(dict(id=f"ST_{sid}_{key[2]}", line=_ln, kind="station", station=sid, track=key[2], length=round(float(s[-1]), 1),
                              pts=[[round(float(x), 2), round(float(y), 2)] for x, y in Q]))
            m = Q[len(Q) // 2]
            stops.append(dict(station=sid, track=key[2], edge=f"ST_{sid}_{key[2]}", s=round(float(s[-1] / 2), 1), pos=[round(float(m[0]), 2), round(float(m[1]), 2)]))
    # 接続ノード: 端点が20m以内の辺同士を同一ノードとして結ぶ
    ends = []
    for e in edges:
        ends.append((e["id"], "start", e["pts"][0]))
        ends.append((e["id"], "end", e["pts"][-1]))
    EL = {e["id"]: e for e in edges}
    nodes = []
    used = [False] * len(ends)
    for i, (eid, wh, p) in enumerate(ends):
        if used[i]:
            continue
        grp = [(eid, wh)]
        used[i] = True
        for j in range(i + 1, len(ends)):
            _ej = EL[ends[j][0]]
            _same = _ej["kind"] == "station" and any(EL[m[0]]["kind"] == "station" and EL[m[0]]["station"] == _ej["station"] and EL[m[0]]["line"] == _ej["line"] for m in grp)
            if TECH.get(EL[eid]["line"], "rail") != TECH.get(_ej["line"], "rail"):
                continue
            _th = 48.0 if _same else 25.0
            if not used[j] and (ends[j][2][0] - p[0]) ** 2 + (ends[j][2][1] - p[1]) ** 2 < _th ** 2:
                grp.append((ends[j][0], ends[j][1]))
                used[j] = True
        nodes.append(dict(id=f"N{len(nodes)}", pos=p, edges=grp, switch=len(grp) > 2))
    # 分岐接続: 端点が他の辺と25m超離れている分岐線は、最寄りの辺上の点(弧長s)へのjoinとして記録する
    joins = []
    for e in edges:
        if e["kind"] == "station" or not e.get("junction"):
            continue
        for wh, p in (("start", e["pts"][0]), ("end", e["pts"][-1])):
            best = None
            for o in edges:
                if o["id"] == e["id"]:
                    continue
                for k, q in enumerate(o["pts"]):
                    d = math.hypot(q[0] - p[0], q[1] - p[1])
                    if best is None or d < best[0]:
                        best = (d, o["id"], k)
            if best and best[0] < 150.0 and 0 < best[2] < len(next(o for o in edges if o["id"] == best[1])["pts"]) - 1:
                joins.append(dict(edge=e["id"], end=wh, to_edge=best[1], to_s=round(best[2] * 2.0, 1), gap_m=round(best[0], 1)))
    out = dict(units="m", frame="world", gauge_m=1.067, edges=edges, nodes=nodes, stops=stops, joins=joins,
               note="運転準備データ。走行システムは未実装。車両は台車Emptyをこの折れ線の弧長位置に置くだけで追従できる。")
    json.dump(out, open(path, "w"), ensure_ascii=False)
    return len(edges), len(nodes), len(stops)


def world_landscape(cam):
    """世界用の遠景: 世界の外周に山並み、外側に遠景の地面。"""
    import veg
    from mathutils import noise as mn, Vector
    hill = lib.mat_hill("hill_far_w", cam, far_dist=5000.0)
    C = np.array([540.0, 930.0])
    nth, nr = 360, 18
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    rr = np.concatenate([np.linspace(3300, 4200, 6), np.linspace(4400, 9000, nr - 6)])
    Vv = np.zeros((nr, nth, 3))
    for i, r in enumerate(rr):
        for j, t in enumerate(th):
            n1 = mn.noise(Vector((math.cos(t) * 1.7, math.sin(t) * 1.7, 0.3)))
            n2 = mn.noise(Vector((math.cos(t) * 5.0, math.sin(t) * 5.0, 2.0)))
            n3 = mn.noise(Vector((math.cos(t) * 14.0 + r * 0.001, math.sin(t) * 14.0, 5.0)))
            Hpk = 160 + 220 * (0.5 + 0.5 * math.sin(t - 0.4)) + 140 * n1 + 70 * n2 + 20 * n3
            fr = np.clip((r - 3300) / 1500.0, 0, 1)
            fo = np.clip((9000 - r) / 2500.0, 0, 1)
            h = max(0.0, Hpk) * (fr * fr * (3 - 2 * fr)) * fo
            Vv[i, j] = (C[0] + math.cos(t) * r, C[1] + math.sin(t) * r, -0.25 + h)
    idx = np.arange(nr * nth).reshape(nr, nth)
    a, b = idx[:-1, :], idx[:-1, np.r_[1:nth, 0]]
    c, d = idx[1:, np.r_[1:nth, 0]], idx[1:, :]
    Tt = np.concatenate([np.stack([a, d, b], -1).reshape(-1, 3), np.stack([b, d, c], -1).reshape(-1, 3)])
    veg.np_mesh("hills_w", Vv.reshape(-1, 3), Tt, hill, "Terrain", smooth=True)
    # 外周の地面(世界地面の外側を埋める)
    seg = 96
    rs = [3300.0, 5000.0, 9000.0, 20000.0]
    V, T = [], []
    for r in rs:
        for s in range(seg):
            ang = 2 * math.pi * s / seg
            V.append((C[0] + math.cos(ang) * r, C[1] + math.sin(ang) * r, -0.25))
    for k in range(len(rs) - 1):
        for s in range(seg):
            a0, a1 = k * seg + s, k * seg + (s + 1) % seg
            b0, b1 = (k + 1) * seg + s, (k + 1) * seg + (s + 1) % seg
            T += [(a0, b0, a1), (a1, b0, b1)]
    veg.np_mesh("far_ground_w", np.array(V), np.array(T), hill, "Terrain")
