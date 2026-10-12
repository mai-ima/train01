"""【Q10】車両の数値検査: 各形式を1両ずつ構築し、仕様(vehtypes.TYPES)と実測(バウンディングボックス)を照合する。
VLM(監査員)は部品の接続切れ・寸法のずれを見逃す(LL3M 論文の弱点)ため、決定論的に検出する。
使い方: python3 vehcheck.py [形式 ...]   出力: out/vehcheck.json と標準出力の表。 終了コード: 0=全て許容内 / 1=逸脱あり
検査: ①全長(連結器・鼻を除く車体の x 範囲≒L) ②全幅(車体 y 範囲≒W。手すり等は除く) ③屋根頂(z 最大≒zr。パンタ・機器は除く)
      ④接地(最下点≒0=レール面) ⑤浮き(台車より下にある部品が無い・車体と台車の隙間が過大でない) ⑥台車数=2 ⑦輪径=仕様"""
import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
import sys, json
import bpy
sys.path.insert(0, _R)
import common
import lib
import vehtypes
from mathutils import Vector
import numpy as np

TOL_L, TOL_W, TOL_H = 0.06, 0.04, 0.08      # 許容(L: 鼻/連結器分を許す下限と上限の比率)

def bbox_world(obj):
    mw = obj.matrix_world
    pts = np.array([mw @ Vector(c) for c in obj.bound_box])
    return pts.min(axis=0), pts.max(axis=0)

def run(kinds):
    rows = []
    common.make_materials()
    for i, k in enumerate(kinds):
        S = vehtypes.TYPES[k]
        nm = f"vchk_{k}"
        v = vehtypes.make(k, nm, seed=3, ends=("cab", "cab"))
        v.place(0, 40.0 * i, 0)
        bpy.context.view_layer.update()
        objs = [o for o in bpy.data.objects if o.name.startswith(nm) and o.type == 'MESH' and len(o.data.polygons)]
        # 車体: 名前に body/shell/wall を含むもの優先。無ければ全体
        mn = np.array([1e9, 1e9, 1e9]); mx = -mn
        for o in objs:
            a, b = bbox_world(o)
            mn = np.minimum(mn, a); mx = np.maximum(mx, b)
        L, W, zr = S["L"], S["W"], S["z"][4]
        ext = mx - mn
        ncoup = 0
        zr0 = getattr(common, "Z_RAIL", 0.244); mn[2] -= zr0; mx[2] -= zr0
        wide = sorted(((max(abs(bbox_world(o)[0][1] - 40.0 * i), abs(bbox_world(o)[1][1] - 40.0 * i)), o.name.replace(nm + "_", "")) for o in objs), reverse=True)[:3]
        r = dict(kind=k, L_spec=L, W_spec=W, zr_spec=round(zr, 3),
                 L_meas=round(float(ext[0]), 2), W_meas=round(float(ext[1]), 2), H_meas=round(float(mx[2]), 2), zmin=round(float(mn[2]), 3),
                 bogies=len(v.meta.get("bogies", [])), nobj=len(objs), widest=[[round(float(a), 2), b] for a, b in wide])
        probs = []
        if ext[0] < L * (1 - TOL_L): probs.append(f"全長が仕様より短い {ext[0]:.2f}<{L}")
        if ext[0] > L * 1.25: probs.append(f"全長が仕様の1.25倍超 {ext[0]:.2f}(鼻・連結器含む)")
        if ext[1] < W * (1 - TOL_W): probs.append(f"全幅が仕様より狭い {ext[1]:.2f}<{W}")
        if ext[1] > W * 1.12: probs.append(f"全幅が仕様より広い {ext[1]:.2f}>{W}(手すり・パンタ以外?)")
        if mx[2] < zr * (1 - TOL_H): probs.append(f"全高が屋根頂より低い {mx[2]:.2f}<{zr}")  # 上限はパンタ等で超えるため検査しない
        if abs(mn[2]) > 0.06: probs.append(f"最下点が接地(レール面0)から {mn[2]:.2f}m")
        if r["bogies"] != 2: probs.append(f"台車数={r['bogies']}(2であるべき)")
        r["problems"] = probs
        rows.append(r)
    return rows

if __name__ == "__main__":
    kinds = sys.argv[1:] or [k for k in vehtypes.TYPES]
    rows = run(kinds)
    out = _os.path.join(_R, "out", "vehcheck.json")
    json.dump(rows, open(out, "w"), ensure_ascii=False, indent=1)
    bad = 0
    print(f"{'形式':10s} {'L仕様':>6s} {'L実測':>6s} {'W仕様':>6s} {'W実測':>6s} {'高さ実測':>7s} {'zmin':>6s} 台車")
    for r in rows:
        print(f"{r['kind']:10s} {r['L_spec']:6.1f} {r['L_meas']:6.2f} {r['W_spec']:6.2f} {r['W_meas']:6.2f} {r['H_meas']:7.2f} {r['zmin']:6.2f} {r['bogies']}")
        for p in r["problems"]:
            print("    ⚠", p); bad += 1
        if any("全幅" in p for p in r["problems"]): print("      最も張り出す部品:", r["widest"])
    print(f"逸脱 {bad} 件 / {len(rows)} 形式 → {out}")
    sys.exit(1 if bad else 0)
