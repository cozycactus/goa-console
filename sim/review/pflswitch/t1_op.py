from pfl import *
nodes = ['PFL_ON', 'MON_ON', 'PFL_ON_RAW', 'MON_ON_RAW', 'CRS_L', 'CRS_R', 'ML_S', 'ML_G', 'PL_S', 'PL_G', 'MR_S', 'MR_G', 'PR_S', 'PR_G']
for variant in sys.argv[1].split(','):
  for model in sys.argv[2].split(','):
    for pfl0 in (0, 1):
        body = 'op\n' + '\n'.join(f'print v({n})' for n in nodes) + '\nprint @JML[id] @JPL[id] @JMR[id] @JPR[id]\n'
        out = run(f't1_{variant}_{model}_{pfl0}', deck(variant, model, body, pfl0=pfl0))
        v = {n: grab(out, f'v({n.lower()})') for n in nodes}
        ids = {k: grab(out, f'@j{k}[id]') for k in ('ml', 'pl', 'mr', 'pr')}
        st = 'PFL active' if pfl0 else 'PFL idle (MON on)'
        print(f'--- {variant} {model} {st}')
        print('   ctrl: PFL_ON %.2f  MON_ON %.2f  (raw %.2f / %.2f)' % (v['PFL_ON'], v['MON_ON'], v['PFL_ON_RAW'], v['MON_ON_RAW']))
        print('   CRS_L %.3f  CRS_R %.3f' % (v['CRS_L'], v['CRS_R']))
        for k in ('ML', 'PL', 'MR', 'PR'):
            s_, g_ = v[k + '_S'], v[k + '_G']; d_ = v['CRS_' + k[1]]
            print(f'   {k}: S {s_:8.3f}  G {g_:8.3f}  D {d_:8.3f}  Vgs {g_-s_:7.3f}  Vg-min(S,D) {g_-min(s_,d_):7.3f}  Id {ids[k.lower()]*1e6:9.2f} uA')
