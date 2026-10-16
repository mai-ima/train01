import json,re,collections,sys
r=json.load(open(sys.argv[1]))
c=collections.defaultdict(list)
for x in r:
    f=lambda n: re.sub(r'\.\d+$','',re.sub(r'\d+','N',n))
    a,b=sorted((f(x['a']),f(x['b'])))
    c[(a.split('_')[0],b.split('_')[0])].append(x)
for k,v in sorted(c.items(), key=lambda kv:-len(kv[1]))[:10]:
    m=max(v,key=lambda i:i['tris'])
    print(len(v),k,'maxtri',m['tris'],'ov',m['min_overlap_m'],m['a'],m['b'],m['at'])
