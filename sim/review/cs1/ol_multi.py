"""The strip's overload LED from five points, both polarities (CS1, cs1_proposal.md; strip v5.0, signed off 2026-10-27),
against the v4.9 detector it replaced. Part values are read from channel_strip.net.

v4.9 (sim/review/gaps/ol.py): PRESRC -> R39 1K -> D1 -> PK (C12 100n // R14 470K) -> U4A against
VREF = +VL / 2; U4A discharges OL_HOLD through R126 1K; U4B lights the red while OL_HOLD is below VREF. Positive peaks
of PRESRC only, from ~9.1 V peak (+18.4 dBu, 4.6 dB below the op-amps' +-15.5 V swing).

v5.0 ("mirror"): each tap (RECV U1A, GOUT U1B, EQOUT, PRESRC, FPOST U2A) -> 1K -> the middle of a BAV99:
- top diode into PK, as D1 today: positive peaks of any tap charge PK (C12 // R14 unchanged);
- bottom diode from NN: negative peaks of any tap pull NN down. NN mirrors PK: C_N 100n // R_N 470K to GNDA, so the
  attack (1K x 100n) and the decay (47 ms) match;
- U18A (LM393B on +VL / GNDD) compares NC, the R_A 4.99M / R_B 10M divider from +VL to NN (1/3), with VREF: NC < VREF
  when NN < -VL / 2 (mirroring PK > +VL / 2) and discharges OL_HOLD through its own 1K, wired-OR with U4A.
Every threshold is a ratio of +VL alone, so the rails' power-up / power-down order can't light it.
"first" is the first try (NN biased to ~-5.6 V from -VL), kept because it fails the power-down test.
Hold, LED drive and the green signal detector are unchanged.

Taps are ideal sources (op-amp outputs). Models and switch comparators as in ol.py. A tap's series impedance can be
set to estimate the error the detector's diode current makes at the tap.
usage: python3 sim/review/cs1/ol_multi.py [--quick]   (--quick: the pulse thresholds, both polarities, ~1 min)"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'gaps'))
import ol
from ol import v, run, vrms, VL

TAPS = ['recv', 'gout', 'eqout', 'presrc', 'fpost']
MIRROR = dict(RT=v('R128'), RA=v('R132'), RB=v('R133'), RN=v('R134'), NREF='0', CN=v('C103'), RDIS=v('R135'), IB=0.0)
FIRST = dict(RT=1e3, RA=499e3, RB=1e6, RN=750e3, NREF='vln', CN=100e-9, RDIS=1e3, IB=0.0)
VSW = 15.5                                            # op-amp swing limit (sim/review/gaps/headroom.py)

def rest(p, vl=VL, vln=VL):
    """NN and NC at rest."""
    a, b = 1 / (p['RA'] + p['RB']), 1 / p['RN']
    nn = (vl * a - (vln if p['NREF'] == 'vln' else 0) * b) / (a + b)
    k = p['RA'] / (p['RA'] + p['RB'])
    return nn, vl * (1 - k) + nn * k

def deck(src, tstop, mode='new', zout=0.0, extra='', p=MIRROR):
    """src: dict tap -> SPICE source body ('SIN(...)' or 'V = expr'); missing taps sit at 0 V. mode 'old' = v4.9."""
    lines = []
    for t in TAPS:
        body = src.get(t, 'DC 0'); el = 'B' if body.startswith('V =') else 'V'
        if zout: lines += [f'{el}_{t} {t}_s 0 {body}', f'RZ_{t} {t}_s {t} {zout}']
        else: lines += [f'{el}_{t} {t} 0 {body}']
    if mode == 'old':
        det = f"R39 presrc pka {v('R39')}\nVI_presrc pka pka2 0\nD1 pka2 pk D1N4148"
    else:
        det = []
        for t in TAPS:
            det += [f'RT_{t} {t} x_{t} {p["RT"]}', f'VI_{t} x_{t} xm_{t} 0',
                    f'DP_{t} xm_{t} pk D1N4148', f'DN_{t} nn xm_{t} D1N4148']
        det += [f'VVLN vln 0 DC -{VL}', f'RA vl nc {p["RA"]}', f'RB nc nn {p["RB"]}', f'RN nn {p["NREF"]} {p["RN"]}',
                f'CN nn 0 {p["CN"]}', 'S18A ndis 0 vref nc SW393', f'RDIS ndis ndisi {p["RDIS"]}', 'VI18 hold ndisi 0']
        if p['IB']: det += [f'IB18 nc 0 DC {-p["IB"]}']             # LM393 input bias flows out of the pin (PNP inputs)
        det = '\n'.join(det)
    d = ol.deck('\n'.join(lines), tstop, extra)
    i = d.index('R39 presrc pka'); j = d.index('C12 pk 0')
    d = d[:i] + det + '\n' + d[j:]
    if mode == 'new':
        d = d.replace('.ic v(hold)', f'.ic v(nn)={rest(p)[0]:.4f} v(hold)')
    return d

def red(src, tstop=0.3, mode='new', **k):
    r = run(deck(src, tstop, mode, **k))
    return r.get('redon') is not None, r

sine = lambda lvl, f=1000: f'SIN(0 {vrms(lvl) * math.sqrt(2)} {f})'
def pulse(vpk, duty=0.1, f=1000):
    """AC-coupled pulse wave: the narrow part (duty) reaches vpk (its sign is the polarity), the rest -vpk*d/(1-d)."""
    base = -vpk * duty / (1 - duty); T = 1 / f
    return f'PULSE({base} {vpk} 0 1u 1u {duty * T} {T})'
def clipped(lvl, f=1000, gain=1.0):
    a = vrms(lvl) * math.sqrt(2)
    return f'V = {gain} * max(-{VSW}, min({VSW}, {a} * sin(6.283185307e3 * time * {f / 1000})))'

def bsearch(fn, lo, hi, n=14):
    for _ in range(n):
        mid = (lo + hi) / 2
        if fn(mid): hi = mid
        else: lo = mid
    return hi

def rails(p, mode, t_p, t_n, up):
    """Peak red LED current (mA) while +VL is above 2.5 V, silence on every tap. Power-down: each rail falls linearly
    from VL to 0 between 0.1 s and t_p (+) / t_n (-). Power-up: each rail rises from 0 between 0.01 s and t_p / t_n."""
    d = deck({}, 0.6, mode, p=p)
    if up:
        d = d.replace(f'VVL vl 0 DC {VL}', f'VVL vl 0 PWL(0 0 0.01 0 {t_p} {VL})')
        d = d.replace(f'VVLN vln 0 DC -{VL}', f'VVLN vln 0 PWL(0 0 0.01 0 {t_n} -{VL})')
        d = d.replace('.ic ', '* ')                                  # everything starts discharged
        t0, t1 = 0.01 + (t_p - 0.01) * 2.5 / VL, 0.6
    else:
        d = d.replace(f'VVL vl 0 DC {VL}', f'VVL vl 0 PWL(0 {VL} 0.1 {VL} {t_p} 0)')
        d = d.replace(f'VVLN vln 0 DC -{VL}', f'VVLN vln 0 PWL(0 -{VL} 0.1 -{VL} {t_n} 0)')
        t0, t1 = 0.1, 0.1 + (t_p - 0.1) * (VL - 2.5) / VL
    r = run(d.replace('.endc', f'meas tran rx max i(VLEDR) from={t0} to={t1}\n.endc'))
    return r.get('rx', 0) * 1e3

def half_cycle(p, sgn, mode='new'):
    """Smallest single half-cycle (1 kHz) of one polarity on PRESRC that lights the red, peak V."""
    def lit_at(a):
        b = {'presrc': f'V = {sgn * a} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < 1.5m)'}
        return run(deck(b, 0.3, mode, p=p)).get('redon') is not None
    return bsearch(lit_at, 5, 40, 12)

if __name__ == '__main__' and '--quick' in sys.argv:
    pos = bsearch(lambda a: red({'presrc': pulse(a)})[0], 1, 30, 10)
    neg = bsearch(lambda a: red({'presrc': pulse(-a)})[0], 1, 30, 10)
    print(f'pulse thresholds: +{pos:.2f} V / -{neg:.2f} V')
elif __name__ == '__main__':
    p = MIRROR; nn, nc = rest(p); k = p['RA'] / (p['RA'] + p['RB'])
    print(f'v5.0: RT 1K per tap; NN rest {nn:.2f} V, NC rest {nc:.2f} V against VREF {VL / 2:.2f} V; '
          f'NN trips at {VL * (1 - 1 / (2 * k)):.2f} V, PK at +{VL / 2:.2f} V', flush=True)

    print('\n1. sine threshold on each tap alone (dBu; the op-amps clip at +23.0 dBu):', flush=True)
    print(f'   v4.9, PRESRC, 1 kHz: {bsearch(lambda L: red({"presrc": sine(L)}, mode="old")[0], 10, 24):5.1f}')
    for t in TAPS:
        print(f'   v5.0, {t:6s} 1 kHz: {bsearch(lambda L: red({t: sine(L)})[0], 10, 24):5.1f}', flush=True)
    for f in (50, 10000):
        print(f'   v5.0, presrc {f:5d} Hz: {bsearch(lambda L: red({"presrc": sine(L, f)})[0], 10, 24):5.1f}')

    print('\n2. polarity: 10 % pulse wave on PRESRC, the narrow peak (V) that lights the red:', flush=True)
    for sgn, name in ((1, 'positive'), (-1, 'negative')):
        old = bsearch(lambda a: red({'presrc': pulse(sgn * a)}, mode='old')[0], 1, 30)
        new = bsearch(lambda a: red({'presrc': pulse(sgn * a)})[0], 1, 30)
        fmt = lambda x: f'{x:5.2f}' if x < 29.9 else 'never (> 30)'
        print(f'   {name}: v4.9 {fmt(old)}, v5.0 {fmt(new)}')
    print(f'   one half-cycle at 1 kHz: v4.9 + {half_cycle(p, 1, "old"):5.2f} V; '
          f'v5.0 + {half_cycle(p, 1):5.2f} V / - {half_cycle(p, -1):5.2f} V')

    print('\n3. clipping the as-built detector misses (1 kHz):', flush=True)
    cases = [
        ('gain stage clips, EQ cuts 10 dB after it (in +15 dBu, gain +9 dB)',
         {'recv': sine(15), 'gout': clipped(24), 'eqout': clipped(24, gain=0.316), 'presrc': clipped(24, gain=0.316),
          'fpost': clipped(24, gain=0.316)}),
        ('post-amp clips: PRE +14 dBu, fader at the top (FPOST +24 dBu)',
         {'recv': sine(14), 'gout': sine(14), 'eqout': sine(14), 'presrc': sine(14), 'fpost': clipped(24)}),
        ('negative-going 10 % pulse, -14 V narrow peak, everywhere', {t: pulse(-14) for t in TAPS}),
        ('input clips at the receiver (+26 dBu), gain -15 dB',
         {'recv': clipped(26), 'gout': clipped(26, gain=0.178), 'eqout': clipped(26, gain=0.178),
          'presrc': clipped(26, gain=0.178), 'fpost': clipped(26, gain=0.178)}),
    ]
    for name, src in cases:
        o = red({'presrc': src['presrc']}, mode='old')[0]; n = red(src)[0]
        print(f'   {name}: v4.9 {"RED" if o else "off"}, v5.0 {"RED" if n else "off"}')

    print('\n4. no false red (v5.0):', flush=True)
    for name, src in [('+16 dBu sine on all five taps', {t: sine(16) for t in TAPS}),
                      ('+16 dBu at 10 kHz on all five', {t: sine(16, 10000) for t in TAPS}),
                      ('10 % pulses, +-8 V narrow peaks, mixed polarity', {'recv': pulse(8), 'gout': pulse(-8),
                       'eqout': pulse(8), 'presrc': pulse(-8), 'fpost': pulse(8)}),
                      ('silence', {})]:
        n, r = red(src)
        print(f'   {name}: red {"ON (false)" if n else "off"}')

    print('\n5. a 1 kHz burst on PRESRC, n cycles: red lit for (v5.0 / v4.9)', flush=True)
    for lvl in (20.0, 22.0):
        out = []
        for n in (1, 2, 5):
            a = vrms(lvl) * math.sqrt(2); t1 = 1e-3 + n * 1e-3
            b = {'presrc': f'V = {a} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < {t1})'}
            res = []
            for mode in ('new', 'old'):
                r = run(deck(b, 1.0, mode)); on, off = r.get('redon'), r.get('redoff')
                res.append(f'{(off - on) * 1e3:.0f}' if on and off else ('lit' if on else '--'))
            out.append(f'{n}: {res[0]} / {res[1]} ms')
        print(f'   {lvl:4.0f} dBu: ' + '; '.join(out))

    print('\n6. detector current from a tap, 1 kHz sine on PRESRC alone, and the error it makes through 20 mOhm (a', flush=True)
    print('   generous OPA1612 closed-loop output impedance at 20 kHz):')
    for lvl in (0.0, 10.0, 16.0, 18.0):
        r = run(deck({'presrc': sine(lvl)}, 0.1, zout=0.02).replace(
            '.endc', 'meas tran ipos max i(VI_presrc) from=50m\nmeas tran ineg min i(VI_presrc) from=50m\n.endc'))
        ip, ineg = r.get('ipos', 0), r.get('ineg', 0); err = max(abs(ip), abs(ineg)) * 0.02
        print(f'   {lvl:4.0f} dBu: +{ip * 1e6:6.1f} / {ineg * 1e6:6.1f} uA, error {err * 1e6:4.2f} uV peak '
              f'({20 * math.log10(err / (vrms(lvl) * math.sqrt(2)) + 1e-30):6.1f} dB re the signal)')

    print('\n7. rails switching (silence): peak red LED current while +VL > 2.5 V, mA', flush=True)
    seq = [('power-down, rails fall together (60 ms)', 0.1 + VL / 280, 0.1 + VL / 280, False),
           ('power-down, +V first (280 / 240 V/s: 2.8 / 2.4 A into ~10 mF)', 0.1 + VL / 280, 0.1 + VL / 240, False),
           ('power-down, -V first', 0.1 + VL / 240, 0.1 + VL / 280, False),
           ('power-up together (180 ms soft start)', 0.19, 0.19, True),
           ('power-up, +V 30 ms ahead', 0.19, 0.22, True), ('power-up, -V 30 ms ahead', 0.22, 0.19, True)]
    for name, tp, tn, up in seq:
        print(f'   {name:62s} v4.9 {rails(p, "old", tp, tn, up):4.2f}, first try {rails(FIRST, "new", tp, tn, up):4.2f}, '
              f'v5.0 {rails(p, "new", tp, tn, up):4.2f}', flush=True)

    print('\n8. tolerances (v5.0):', flush=True)
    th0 = bsearch(lambda a: red({'presrc': pulse(-a)})[0], 1, 30)
    th_ib = bsearch(lambda a: red({'presrc': pulse(-a)}, p=dict(p, IB=25e-9))[0], 1, 30)
    print(f'   negative trip with the LM393B input bias at its 25 nA maximum: {th_ib:.2f} V (vs {th0:.2f} V, '
          f'{20 * math.log10(th_ib / th0):+.2f} dB)')
    for ra, rb, tag in ((p['RA'] * 1.01, p['RB'] * 0.99, 'R_A +1 %, R_B -1 %'), (p['RA'] * 0.99, p['RB'] * 1.01, 'R_A -1 %, R_B +1 %')):
        kk = ra / (ra + rb); trip = VL * (1 - 1 / (2 * kk))
        print(f'   {tag}: NN trips at {trip:.2f} V ({20 * math.log10(trip / (VL * (1 - 1 / (2 * k)))):+.2f} dB)')
