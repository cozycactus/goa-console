from pfl import *
import numpy as np
# Power-up: +-VL ramp 0 -> 16.9 V (linear, 150 ms; PSU soft start 165 ms to 90 %). No PFL pressed: the PFL comparator
# sinks once the supply exceeds ~2 V total, the MON comparator stays off (output pulled up). Tone (2 kHz, 0 dBu) on one
# path at a time -> per-path gain vs time from the sliding 1-cycle RMS. Also CRS DC (1-cycle mean) at the end.
F = 2e3; A = 1.0954; TEND = 0.4
def mod(text):
    text = text.replace(f'VLP VLP 0 {VL}', f'VLP VLP 0 PWL(0 0 0.15 {VL})').replace(f'VLN VLN 0 -{VL}', f'VLN VLN 0 PWL(0 0 0.15 -{VL})')
    text = text.replace(f'VLO vlo 0 -{VL - 0.12}', 'EVLO vlo 0 VLN 0 0.993')
    text = re.sub(r'VCP cp 0 PWL\([^)]*\)', 'BCP cp 0 V = V(VLP) > 1 ? 1 : 0', text)
    text = re.sub(r'VCM cm 0 PWL\([^)]*\)', 'VCM cm 0 0', text)
    return text
for variant in sys.argv[1].split(','):
    model = sys.argv[2]
    res = {}
    for which in ('mon', 'pfl'):
        name = f't6_{variant}_{model}_{which}'; fn = os.path.join(DECKS, name + '.dat')
        body = f'tran 5u {TEND} 0 10u uic\nwrdata {fn} v(CRS_L) v(PFL_ON) v(MON_ON)\n'
        kw = dict(am=A, fm=F) if which == 'mon' else dict(ap=A, fp=F)
        out = run(name, mod(make(variant, model, body, pfl0=0, **kw)), timeout=3000)
        d = np.loadtxt(fn, skiprows=1); t = d[:, 0]
        if t[-1] < TEND * 0.999: print(name, 'stopped at', t[-1]); continue
        dt = 1e-5; n = int(round(1 / F / dt)); tt0 = np.arange(0, TEND, dt)
        v = np.interp(tt0, t, d[:, 1]); k = np.ones(n) / n
        mean = np.convolve(v, k, 'valid'); vc = v[n // 2: n // 2 + len(mean)]; ac = vc - mean
        rms = np.sqrt(np.convolve(ac * ac, k, 'valid')); tt = tt0[n: n + len(rms)]
        g = 20 * np.log10(np.maximum(rms, 1e-9) / (A / math.sqrt(2)))
        res[which] = (tt, g, np.interp(tt, t, d[:, 2]), np.interp(tt, t, d[:, 3]), mean[n // 2: n // 2 + len(rms)])
    if len(res) < 2: continue
    tt, gm, pon, mon, dcm = res['mon']; gp = res['pfl'][1]
    both = (gm > -6) & (gp > -6)
    t_both_end = tt[both][-1] * 1e3 if both.any() else 0
    pfl_off40 = tt[np.argmax((gp < -40) & (tt > 0.001))] * 1e3 if (gp < -40).any() else float('nan')
    print(f'{variant:6s} {model}: both paths > -6 dB until {t_both_end:6.1f} ms (rails at {VL*min(t_both_end/150,1):.1f} V); '
          f'PFL path < -40 dB from {pfl_off40:6.1f} ms; at 400 ms PFL path {gp[-50:].mean():6.1f} dB, MON {gm[-50:].mean():6.2f} dB; '
          f'PFL_ON {pon[-1]:6.2f} V, MON_ON {mon[-1]:6.2f} V; CRS DC {dcm[-1]*1e3:8.1f} mV (peak |DC| {np.max(np.abs(dcm))*1e3:7.1f} mV)')
