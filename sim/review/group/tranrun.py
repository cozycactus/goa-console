import json
from concurrent.futures import ProcessPoolExecutor
from stabg import run
from fixes import apply
from groupdeck import ROLE
C = {}
for fx in ('none', 'rec'):
    for nm, p, pan in (('w0706', 0.706, 0.5), ('wtop_panL', 1.0, 1.0), ('w03', 0.3, 0.25), ('wtop_panR', 1.0, 0.0)):
        C[f'{fx}_{nm}'] = apply(dict(pos={'RV1': p, 'RV3': p, 'RV4': p, 'RV2': pan}, board=0.08), fx)
def job(it):
    nm, cfg = it; return nm, run('tr_' + nm, cfg, tran=True)
if __name__ == '__main__':
    with ProcessPoolExecutor(4) as ex: R = dict(ex.map(job, C.items()))
    json.dump(R, open('res_tran.json', 'w'), indent=0)
    for fx in ('none', 'rec'):
        print(fx)
        for u in ROLE:
            rows = [(R[k][u].get('os', -1), R[k][u].get('late_pp', -1), R[k][u].get('pm'), k) for k in R if k.startswith(fx)]
            w = max(rows)
            print(f'  {u} {ROLE[u]:22s} overshoot max {w[0]}% (late p-p {w[1]}%, PM {w[2]}) @ {w[3]}')
