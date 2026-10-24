import json, sys
from concurrent.futures import ProcessPoolExecutor
from stabg import run
from fixes import FIX
V = {'base': {}, 'R13moved': dict(mst={'S_PRE': 121}),
     'ser47': dict(repin={('C13', '1'): 'SUB_RBO'}, x=[('RSER', 'SUB_RBUF', 'SUB_RBO', 47)]),
     'ser100': dict(repin={('C13', '1'): 'SUB_RBO'}, x=[('RSER', 'SUB_RBUF', 'SUB_RBO', 100)]),
     'R13moved_ser47': dict(mst={'S_PRE': 121}, repin={('C13', '1'): 'SUB_RBO'}, x=[('RSER', 'SUB_RBUF', 'SUB_RBO', 47)])}
C = {}
for fx in ('none', 'f10'):
    for vn, v in V.items():
        for pan in (0.0, 0.5, 1.0):
            for extra in (0, 22e-12, 47e-12):
                cfg = dict(pos={'RV1': 1.0, 'RV2': pan, 'RV3': 0.5, 'RV4': 0.5}, board=0.08, extra=FIX[fx] + v.get('x', []),
                           mst=v.get('mst', {}), repin=v.get('repin', {}))
                if extra: cfg['loads'] = {'S_PRE': extra}
                C[f'{fx}_{vn}_pan{pan}_cl{extra*1e12:.0f}'] = cfg
def job(it):
    nm, cfg = it; return nm, run('u2b_' + nm.replace('.', 'p'), cfg, stages=['U2B'])
if __name__ == '__main__':
  with ProcessPoolExecutor(5) as ex: R = dict(ex.map(job, C.items()))
  json.dump(R, open('res_u2b.json', 'w'), indent=0)
  for fx in ('none', 'f10'):
    for vn in V:
        for cl in (0, 22, 47):
            rows = [(R[k]['U2B']['pm'], R[k]['U2B']['clpk'], k) for k in R if k.startswith(f'{fx}_{vn}_pan') and k.endswith(f'_cl{cl}')]
            print(f'{fx:5s} {vn:16s} +{cl:2d}pF on S_PRE  PM min {min(rows)[0]:5.1f}  CLpk max {max(r[1] for r in rows):5.2f} dB')
