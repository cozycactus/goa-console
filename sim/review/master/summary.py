"""Per unit: worst phase margin / largest closed-loop peak over every res/<fix>_<cfg>.json. usage: summary.py FIX"""
import json, glob, sys, os
from masterdeck import UNITS
fix = sys.argv[1]
worst = {}
for fn in sorted(glob.glob(f'res/{fix}_*.json')):
    cfg = os.path.basename(fn)[len(fix) + 1:-5]
    for u, r in json.load(open(fn)).items():
        if 'pm' not in r: continue
        w = worst.setdefault(u, dict(pm=999, clpk=-99, n=0))
        w['n'] += 1
        if r['pm'] < w['pm']: w.update(pm=r['pm'], pmcfg=cfg, fc=r.get('fc'))
        if r.get('clpk', -99) > w['clpk']: w.update(clpk=r['clpk'], clcfg=cfg, fcl=r.get('fclpk'))
        if r.get('gm') is not None and r['gm'] < w.get('gm', 999): w.update(gm=r['gm'], gmcfg=cfg)
for u in UNITS:
    if u in worst:
        w = worst[u]
        print(f"{u:5s} PM {w['pm']:6.1f} ({w['pmcfg']}, fc {w['fc']} MHz)  peak {w['clpk']:+5.2f} dB ({w['clcfg']}, {w['fcl']} MHz)"
              f"  gm {w.get('gm', '-')}  [{w['n']} cfgs]")
