"""K8集計: out/mc_*.json を横断し、『意味のある干渉(重なり>=0.3m かつ 三角形>=20)』を種類別に数える。"""
import json, glob, re, collections
cat = collections.defaultdict(list)
tot = {}
for f in sorted(glob.glob('out/mc_[A-Z]*.json')):
    sid = re.search(r'mc_(\w+)\.json', f).group(1)
    if sid in ('M03e','M03f','M03g','M03h','M03b','M03c','M03d','tmp'): continue
    try: r = json.load(open(f))
    except Exception: continue
    tot[sid] = len(r)
    for x in r:
        if x['min_overlap_m'] >= 0.3 and x['tris'] >= 20:
            g = lambda n: re.sub(r'\.\d+$', '', re.sub(r'\d+', 'N', n)).split('_')[0]
            k = tuple(sorted((g(x['a']), g(x['b']))))
            if all(t in ('zelkova','sugi','kaki') for t in k):
                continue                                   # 樹冠同士の接触は自然(欠陥として数えない)
            cat[k].append((sid, x))
print('駅別 総件数:', ' '.join(f'{k}:{v}' for k, v in tot.items()))
print('--- 種類別(重なり>=0.3m, 三角形>=20) ---')
for k, v in sorted(cat.items(), key=lambda kv: -len(kv[1]))[:20]:
    sids = collections.Counter(s for s, _ in v)
    m = max(v, key=lambda t: t[1]['tris'])
    print(len(v), k, '駅:', dict(sids.most_common(4)), '例', m[0], m[1]['a'], m[1]['b'], m[1]['at'])
