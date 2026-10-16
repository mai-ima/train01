import os as _os; _R = _os.environ.get("STATION_ROOT") or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # Q8: 絶対パスを使わない
"""状態表(checks.json / status.json)を実態に合わせて更新(2026-10-11)。路線図v2.4の『最新内容』用。"""
import json, glob, os, re
os.chdir(_R + '/net')
ck = json.load(open('checks.json')); st = json.load(open('status.json'))
imgs = {}
for f in glob.glob('../tex/kit/*.png'):
    m = re.match(r'.*/([A-Z0-9]+)_', f)
    if m: imgs[m.group(1)] = imgs.get(m.group(1), 0) + 1
NOTE = {
 "M05": "2026-10-11 再設計: 煉瓦2階の郊外駅・曲線上屋・鉄骨跨線橋・池と果樹・郊外商店街。両側ホーム+島式(4線・折返し対応)。M04との差別化済み。",
 "M07": "2026-10-11 3線化: 島式+分岐側の引上線。停車車両を再配置。",
 "SH03": "2026-10-11 3線化: 島式+待避線。", "SH07": "2026-10-11 3線化: 両側+待避線。",
 "SH08": "2026-10-11 島式2面4線(終着・折返し14本/h)に拡張。跨線橋に中間階段。",
 "M03": "2026-10-11 4線化。橋上の跨線部を線路限界の外へ移し干渉解消。", "SH02": "2026-10-11 3線化。橋上跨線部の干渉解消。",
 "SH04": "2026-10-11 4線化(両側+待避島)。", "SH05": "2026-10-11 島式3線(折返し線追加)。",
 "M09": "2026-10-11 2線化(行違い線)。", "M10": "2026-10-11 4線化(温泉街分岐)。", "M12": "2026-10-11 3線(頂上の行違い線)。",
 "K02": "2026-10-11 4線化(両側ホーム+中央通過2線)。路盤の床・構内照明・土被りの丘・窓つき高層ビルを追加。",
 "K03": "2026-10-11 3線化(島式1面2線+折返し線)。", "TR02": "2026-10-11 上下2線(島式の安全地帯を挟む)。",
 "T02": "2026-10-11 土被りの丘と窓つき商店街ビルを追加。路線図の線位置を修正。", "T03": "2026-10-11 土被りの丘と窓つき庁舎を追加。線位置を修正。",
}
for s in ck:
    ck[s]['render'] = os.path.exists(f'../out/contact/{s}.png')
    ck[s]['trains'] = '未' if s in ('M01',) else 'あり'
    if s in imgs: ck[s]['images'] = imgs[s]
for s, n in NOTE.items():
    if s in st['status']:
        base = st['status'][s].get('note', '')
        st['status'][s]['note'] = (n + ' / ' + base) if n[:10] not in base else base
json.dump(ck, open('checks.json', 'w'), ensure_ascii=False, indent=1)
json.dump(st, open('status.json', 'w'), ensure_ascii=False, indent=1)
print('ok', len(ck), sum(1 for v in ck.values() if v['render']))
