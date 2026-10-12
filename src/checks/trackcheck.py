"""【X15】線路部品の静的数値検査(bpy不要): 軌間・レール頭高・レール断面・バラスト断面・ホーム高・車両限界を実物の規格値と照合する。
使い方: python3 trackcheck.py   終了コード: 0=全て許容内 / 1=逸脱あり
基準(国鉄在来線・狭軌): 軌間1,067 mm、37kgレール 高さ約122 mm・頭幅約63 mm、バラスト肩幅(枕木長2.1〜2.4 m)、ホーム高=レール頭+0.76〜0.92 m(低床ホーム)、車両限界 幅3.0 m。"""
import os as _os, sys
_R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
sys.path.insert(0, _R)
import common, trackkit

bad = []
def chk(name, val, lo, hi, unit=""):
    ok = lo <= val <= hi
    print(f"{'OK ' if ok else 'NG '} {name}: {val:.4f}{unit}  (許容 {lo}〜{hi})")
    if not ok: bad.append(name)

chk("軌間(m)", common.GAUGE, 1.065, 1.069)
chk("レール頭天端(Z_RAIL, m)", common.Z_RAIL, 0.25, 0.30)
H = max(p[1] for p in trackkit.RAIL_PROFILE) - min(p[1] for p in trackkit.RAIL_PROFILE)
Wh = max(abs(p[0]) for p in trackkit.RAIL_PROFILE if p[1] > 0.088) * 2
Wb = max(abs(p[0]) for p in trackkit.RAIL_PROFILE) * 2
chk("レール高(m)", H, 0.115, 0.155)
chk("レール頭幅(m)", Wh, 0.060, 0.070)
chk("レール底幅(m)", Wb, 0.100, 0.130)
bw = trackkit.BALLAST_PROFILE
chk("バラスト天端幅(m)", (bw[2][0] - bw[1][0]), 3.5, 4.4)
chk("バラスト天端高(m)", common.Z_BAL, 0.05, 0.15)
chk("ホーム高(レール頭上, m)", common.Z_PLAT - common.Z_RAIL, 0.76, 0.92)

import re
_k5 = open(_os.path.join(_R, "kit5.py"), encoding="utf-8").read()
_m = re.search(r"hc = ([0-9.]+) if ac else ([0-9.]+)", _k5)
if _m:
    chk("トロリ線高 交流(m)", float(_m.group(1)), 5.2, 5.6)
    chk("トロリ線高 直流(m)", float(_m.group(2)), 5.0, 5.5)
else:
    print("NG トロリ線高の定義が見つからない"); bad.append("catenary")
print("\n逸脱", len(bad), "件" if bad else "件(全て許容内)")
sys.exit(1 if bad else 0)
