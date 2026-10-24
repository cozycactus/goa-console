import json
from concurrent.futures import ProcessPoolExecutor
from stabg import run
from fixes import apply
V = {'rec': ([], {}), 'rec+10p': ([('CRET', 'SUB_RET', '0', '10p')], {}),
     'rec+1K': ([('RPROT', 'SUB_RET', 'SUB_RETIN', 1000)], {('U2', '5'): 'SUB_RETIN'}),
     'rec+1K+100p': ([('RPROT', 'SUB_RET', 'SUB_RETIN', 1000), ('CPROT', 'SUB_RETIN', '0', '100p')], {('U2', '5'): 'SUB_RETIN'})}
C = {}
for vn, (x, rp) in V.items():
    for board in (0, 0.08):
        for ins in ('open', 50, 600, 2200, 10000, None):
            for p in (0.706, 1.0):
                cfg = apply(dict(pos={'RV1': p, 'RV2': 0.0, 'RV3': 0.5, 'RV4': 0.5}, board=board), 'rec')
                cfg['extra'] += x; cfg['repin'].update(rp)
                cfg['ins'] = 'open' if ins == 'open' else dict(rs=ins, cret=0, csend=470e-12)
                C[f'{vn}|b{board}|ins{ins}|f{p}'] = cfg
def job(it):
    nm, cfg = it
    return nm, run('pr_' + nm.replace('|', '_').replace('.', 'p').replace('+', 'p'), cfg, stages=['U2B'])
if __name__ == '__main__':
    with ProcessPoolExecutor(4) as ex: R = dict(ex.map(job, C.items()))
    json.dump(R, open('res_u2b_prot.json', 'w'), indent=0)
    for vn in V:
        for b in ('b0', 'b0.08'):
            rows = [(R[k]['U2B']['pm'], R[k]['U2B']['clpk'], k) for k in R if k.startswith(vn + '|' + b + '|')]
            print(f'{vn:12s} {b:6s} PM min {min(rows)[0]:5.1f} @ {min(rows)[2]}  CLpk max {max(r[1] for r in rows):.2f}')
