from pfl import *
# AC: on-path gain and off-path crosstalk at CRS_L, 20 Hz-20 kHz (small signal around the operating point)
freqs = [20, 100, 1e3, 10e3, 20e3]
for variant in sys.argv[1].split(','):
  for model in sys.argv[2].split(','):
    for pfl0 in (0, 1):
      res = {}
      for which in ('mon', 'pfl'):
        body = 'ac dec 20 10 30k\n' + '\n'.join(f'meas ac g{i} find vdb(CRS_L) at={f}' for i, f in enumerate(freqs))
        kw = dict(acm=1) if which == 'mon' else dict(acp=1)
        out = run(f"t2_{variant}_{model}_{pfl0}_{which}", make(variant, model, body, pfl0=pfl0, **kw))
        res[which] = [grab(out, f'g{i}') for i in range(len(freqs))]
      on, off = ('pfl', 'mon') if pfl0 else ('mon', 'pfl')
      st = 'PFL active' if pfl0 else 'PFL idle'
      print(f'{variant:6s} {model:7s} {st:10s} on-path ({on}) dB: ' + ' '.join(f'{x:7.3f}' for x in res[on]) +
            f' | off-path ({off}) dB: ' + ' '.join(f'{x:7.1f}' for x in res[off]))
print('freqs', freqs)
