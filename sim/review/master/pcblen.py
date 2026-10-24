"""Per net: pad positions on a placed board, minimum-spanning-tree length (Manhattan) as a routed-length estimate.
usage: KPY pcblen.py board.kicad_pcb out.json"""
import sys, json, pcbnew, itertools
b = pcbnew.LoadBoard(sys.argv[1])
nets = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname().lstrip('/')
        if not n: continue
        pos = p.GetPosition()
        nets.setdefault(n, []).append((fp.GetReference(), p.GetNumber(), pos.x / 1e6, pos.y / 1e6))
def mst(pts):
    if len(pts) < 2: return 0.0
    import math
    inn = [pts[0]]; out = pts[1:]; tot = 0
    d = {i: abs(out[i][0]-pts[0][0]) + abs(out[i][1]-pts[0][1]) for i in range(len(out))}
    while d:
        i = min(d, key=d.get); tot += d.pop(i); q = out[i]
        for j in d: d[j] = min(d[j], abs(out[j][0]-q[0]) + abs(out[j][1]-q[1]))
    return tot
res = {n: dict(mst=round(mst([(x, y) for _, _, x, y in v]), 1), pads=[f'{r}.{p}' for r, p, _, _ in v],
               xy=[(round(x,1), round(y,1)) for _, _, x, y in v]) for n, v in nets.items()}
json.dump(res, open(sys.argv[2], 'w'), indent=0)
print(len(res), 'nets')
