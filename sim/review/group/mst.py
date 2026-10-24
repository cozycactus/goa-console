import json, math, sys
d = json.load(open(sys.argv[1]))
def mst(pts):
    n = len(pts); 
    if n < 2: return 0, []
    used = [False]*n; dist = [1e18]*n; par=[-1]*n; dist[0]=0; tot=0; edges=[]
    for _ in range(n):
        k = min((i for i in range(n) if not used[i]), key=lambda i: dist[i]); used[k]=True; tot += dist[k]
        if par[k]>=0: edges.append((par[k],k,dist[k]))
        for i in range(n):
            if not used[i]:
                dd = abs(pts[i][2]-pts[k][2]) + abs(pts[i][3]-pts[k][3])   # Manhattan
                if dd < dist[i]: dist[i]=dd; par[i]=k
    return tot, edges
nets = sys.argv[2:] or sorted(d)
for n in nets:
    key = n if n in d else '/'+n
    if key not in d: print(n, 'missing'); continue
    pts = d[key]; L, e = mst(pts)
    span = ' '.join(f"{p[0]}.{p[1]}({p[2]:.0f},{p[3]:.0f})" for p in pts)
    print(f"{n:14s} {L:7.1f} mm  {span}")
