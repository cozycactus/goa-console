"""usage: python3 sweep.py <set> <fixset> [board pF/mm] [tran]  -> res_<set>_<fixset>_<board>.json + table
sets: pots, bus, ins, ret, sw, loads"""
import os, sys, json, time, itertools
from concurrent.futures import ProcessPoolExecutor
from stabg import run
from groupdeck import ROLE, UNITS
from fixes import FIX, apply

SET, FX = sys.argv[1], sys.argv[2]
BOARD = float(sys.argv[3]) if len(sys.argv) > 3 else 0
TRAN = len(sys.argv) > 4 and sys.argv[4] == 'tran'
ALLSW = {f'SW{i}': True for i in range(1, 12)}

def P(p, pan): return {'RV1': p, 'RV3': p, 'RV4': p, 'RV5': p, 'RV2': pan}
C = {}
if SET == 'pots':
    for p, pan in ((0, 0), (0.3, 0.25), (0.5, 0.5), (0.6, 0.5), (0.706, 0.5), (0.85, 0.75), (1.0, 1.0), (1.0, 0.5), (0.706, 0)):
        C[f'pot{p}_pan{pan}'] = dict(pos=P(p, pan))
        C[f'pot{p}_pan{pan}_swon'] = dict(pos=P(p, pan), sw=ALLSW)
elif SET == 'bus':
    for ns, cb, fb, rl in itertools.product((0, 1, 24, 28), (0, 100e-12, 470e-12, 2.2e-9, 10e-9), ('model', 'short', (0.3e-6, 280, 1e-12), (1.5e-6, 280, 1e-12)), (0, 0.3e-6)):
        if rl and fb != 'model': continue
        nm = f'n{ns}_c{cb*1e12:.0f}p_fb{fb if isinstance(fb, str) else fb[0]*1e6}_rl{rl*1e6}'
        C[nm] = dict(nsub=ns, cbus_sub=cb, naux=max(ns, 1) if ns < 24 else 24, cbus_aux=cb, fb=fb, rib_l=rl)
    C['jp_open'] = dict(jp=set())
    C['jp_open_fbshort'] = dict(jp=set(), fb='short')
    C['gc_local'] = dict(gc='local')
elif SET == 'ins':
    for p in (0.0, 0.706, 1.0):
        C[f'unplugged_f{p}'] = dict(pos=P(p, 0.5))
        for rs, cret, csend in itertools.product((50, 600, 2.2e3, 10e3, None), (0, 470e-12, 2.2e-9), (100e-12, 2.2e-9, 10e-9)):
            if p != 1.0 and (cret, csend) not in ((0, 100e-12), (2.2e-9, 10e-9)): continue
            C[f'plug_rs{rs}_cr{cret*1e12:.0f}p_cs{csend*1e12:.0f}p_f{p}'] = dict(pos=P(p, 0.5), ins=dict(rs=rs, cret=cret, csend=csend))
elif SET == 'ret':
    for p in (0.0, 0.706, 1.0):
        C[f'open_l{p}'] = dict(pos=P(p, 0.5))
        for rs, cc in itertools.product((10, 600, 2.2e3), (100e-12, 2.2e-9)):
            C[f'rs{rs}_cc{cc*1e12:.0f}p_l{p}'] = dict(pos=P(p, 0.5), ret=dict(rs=rs, cc=cc), sw=ALLSW)
elif SET == 'loads':           # extra output C on the long output nets (on top of the board MST estimate)
    for cl in (22e-12, 47e-12):
        for p, pan in ((0, 0), (0.3, 0.5), (0.706, 0.5), (1.0, 1.0), (1.0, 0.0), (0.6, 0.5)):   # 0.3: worst with extra C
            C[f'cl{cl*1e12:.0f}p_pot{p}_pan{pan}'] = dict(pos=P(p, pan), loads={n: cl for n in (
                'GC_BUF', 'S_SUM', 'A_SUM', 'S_MIX', 'S_PRE', 'S_POST', 'S_PBL', 'S_PBR', 'A_OUT', 'A_MIX', 'RT_L', 'RT_R', 'RT_BL', 'RT_BR',
                'RT2_L', 'RT2_R', 'RT2_BL', 'RT2_BR')})
STAGES = {'bus': ['U1A', 'U1B', 'U6A', 'U2A', 'U6B'], 'ins': ['U2A', 'U2B', 'U3A'], 'ret': ['U8A', 'U8B', 'U9A', 'U9B', 'U10A', 'U10B', 'U11A', 'U11B',
                                                                                    'U12A', 'U12B', 'U13A', 'U13B', 'U14A', 'U14B', 'U15A', 'U15B']}.get(SET)
if os.environ.get('STAGES'): STAGES = os.environ['STAGES'].split(',')       # e.g. only the OPA1656 followers
for k in C:
    if BOARD: C[k]['board'] = BOARD
    apply(C[k], FX)

def job(item):
    nm, cfg = item
    tag = f'{SET}_{FX}_{BOARD}_{nm}'.replace('.', 'p').replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
    return nm, run(tag, cfg, stages=STAGES, tran=TRAN)

if __name__ == '__main__':
    t = time.time(); R = {}
    with ProcessPoolExecutor(int(__import__("os").environ.get("NJ", "4"))) as ex:
        for nm, r in ex.map(job, C.items()): R[nm] = r
    out = f'res_{SET}_{FX}_{BOARD}{"_t" if TRAN else ""}.json'
    json.dump(R, open(out, 'w'), indent=0)
    print(f'{len(C)} configs, {time.time() - t:.0f} s -> {out}')
    for u in UNITS:
        rows = [(r[u].get('pm', 999), r[u].get('clpk', 0), nm, r[u]) for nm, r in R.items() if u in r and 'pm' in r[u]]
        if not rows: print(u, 'no data'); continue
        lo = min(rows, key=lambda x: x[0]); pk = max(rows, key=lambda x: x[1])
        os_ = max((r[u].get('os', -1), nm) for nm, r in R.items())
        print(f"{u} {ROLE[u]:22s} PM min {lo[0]:6.1f} @ {lo[2]:34s} fc {lo[3].get('fc')} | CLpk max {pk[1]:5.2f} dB @ {pk[2]:30s}"
              + (f" | OS max {os_[0]}% @ {os_[1]}" if TRAN else ''))
