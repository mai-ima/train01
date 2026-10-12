import json
g=json.load(open('/home/claude/station/net/track_graph.json'))
par={}
def f(x):
    par.setdefault(x,x)
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
def u(a,b): par[f(a)]=f(b)
for n in g['nodes']:
    for e,_ in n['edges']: u(n['id'],'E:'+e)
for j in g['joins']: u('E:'+j['edge'],'E:'+j['to_edge'])
comps={}
for e in g['edges']: comps.setdefault(f('E:'+e['id']),[]).append(e)
print('components',len(comps))
for es in comps.values(): print(len(es),sorted({e['line'] for e in es}))
