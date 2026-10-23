from pfl import *
# Large-signal: (1) on-path THD at +20 dBu (10.96 V pk) 1 kHz and 10 kHz, off source silent;
#               (2) off-isolation: +20 dBu 1 kHz on the OFF source, on source silent -> fundamental and THD at CRS_L
A = float(os.environ.get('AMP', '10.96'))
def four(out):
    # parse ngspice 'fourier' output: harmonic table
    m = re.search(r'Fourier analysis for v\(crs_l\):.*?THD:\s*([-+0-9.eE]+)\s*%.*?\n(.*?)\n\s*\n', out, re.S)
    thd = float(m.group(1)) if m else None
    rows = re.findall(r'^\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)', out, re.M)
    mags = {int(r[0]): float(r[2]) for r in rows}
    return thd, mags
for variant in sys.argv[1].split(','):
  for model in sys.argv[2].split(','):
    for f in (1e3, 10e3):
        per = 1 / f
        body = f'tran {per/400} {0.3 + 4*per} {0.3} {per/400}\nfourier {f} v(CRS_L)\n'
        out = run(f't3_on_{variant}_{model}_{int(f)}_{A}', make(variant, model, body, am=A, fm=f, pfl0=0))
        thd, mags = four(out)
        g = 20 * math.log10(mags[1] / A) if mags else float('nan')
        h = ' '.join(f'H{k} {20*math.log10(mags[k]/mags[1]):6.1f}' for k in (2, 3) if k in mags and mags[k] > 0)
        print(f'{variant:6s} {model:7s} ON  {20*math.log10(A/math.sqrt(2)/0.7746):+.1f} dBu {f/1e3:4.0f} kHz: gain {g:7.3f} dB  THD {thd:.2e} %  ({20*math.log10(max(thd,1e-12)/100):6.1f} dB)  {h}')
    f = 1e3; per = 1e-3
    body = f'tran {per/400} {0.3 + 4*per} {0.3} {per/400}\nfourier {f} v(CRS_L)\n'
    out = run(f't3_off_{variant}_{model}_{A}', make(variant, model, body, ap=A, fp=f, pfl0=0))
    thd, mags = four(out)
    m = re.search(r'Harmonic.*?\n.*?\n\s*0\s+0\s+([-+0-9.eE]+)', out, re.S)
    if m: print(f'   DC at CRS_L during the off-side drive: {float(m.group(1)):.4f} V')
    print(f'{variant:6s} {model:7s} OFF {20*math.log10(A/math.sqrt(2)/0.7746):+.1f} dBu on PFL_SIG (MON on, silent): leak fund {20*math.log10(mags[1]/A):7.1f} dB, '
          f'H2 {20*math.log10(max(mags.get(2,0),1e-15)/A):7.1f} dB, H3 {20*math.log10(max(mags.get(3,0),1e-15)/A):7.1f} dB (re source)')
