"""構造物撮影用の MULTICAM 文字列を作る。使い方: python3 struct_cams.py <mid_x> <mid_y> <dir_x> <dir_y> [W]
mid/dir は kit4.run_items が出力する STRUCT 行(世界座標の中央と進行方向)から取る。6視点: 側面低/斜め俯瞰/進行方向の目線/反対側/空撮/近接。
地形内に入ったカメラは main.py が持ち上げる(ログに「地形の下に埋まっていたため」)。それでも真っ黒な視点は imgcheck で無効にする。"""
import sys, math
mx, my, dx, dy = [float(v) for v in sys.argv[1:5]]
d = math.hypot(dx, dy); tx, ty = dx / d, dy / d
nx, ny = -ty, tx
def P(a, b, z): return (mx + tx * a + nx * b, my + ty * a + ny * b, z)
views = [(P(-10, 28, 6.0), P(0, 0, 3.0), 35), (P(35, 40, 14.0), P(0, 0, 2.0), 30), (P(-38, 6, 2.6), P(10, 0, 3.0), 32),
         (P(14, -20, 3.0), P(0, 0, 3.0), 38), (P(-30, 45, 30.0), P(0, 0, 2.0), 28), (P(4, 14, 1.8), P(0, 0, 4.0), 40)]
print(";".join("%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%d" % (*a, *b, l) for a, b, l in views))
