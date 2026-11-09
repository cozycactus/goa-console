"""CS6 (docs/studies/console_survey.md §5): fusible supply resistors on every ribbon module (strip and group R1-R4: 10R from the
bus to +VA / -VA / +VL / -VL). The part: Vishay Draloric M25SI (M251206BB1009JP500), thin-film fusible, 1206, 0.25 W
at 70 C, 216 K/W film rise (its datasheet: 54 K at 0.25 W), fuses at >= 3 W; its "Fusing Performance" band (time to
fuse at constant power, read off the datasheet's plot) below. Max. voltage across it after fusing: ~22 V at 10 ohm.
1. Normal duty: each resistor's power and film temperature in a 40 C tub (docs/studies/thermal_study.md: ~16 K over the room).
2. Faults behind a resistor: a hard short and a resistive one; fusing time from the band; the wing PTC's state
   (+V MF-RX250/72: 2.5 A hold, 5.0 A trip; -V MF-RX185/72: 1.85 / 3.7 A; below the trip current a PTC need not trip).
3. Surges (ngspice): the console powering up through the PSU's soft start; the PSU lead plugged into a running PSU;
   one module plugged into a live wing.
usage: python3 sim/review/cs6/fusible.py"""
import math, os, re, subprocess, tempfile

R, VBUS, PRATED, KPW, TAMB, TFMAX = 10.0, 16.9, 0.25, 216.0, 40.0, 125.0
FAST = [(3, 1.5), (4, 0.12), (5, 0.012), (6, 0.0025), (6.5, 0.001)]               # band, lower edge: P (W), t (s)
SLOW = [(3, 100), (4, 11), (5, 3.5), (6, 1.4), (7, 0.45), (8, 0.17), (9, 0.07)]    # upper edge (every part fused)

def band(P, pts):
    """log-interpolated time to fuse at constant power P; None below 3 W (not specified), the end value beyond."""
    if P < pts[0][0]: return None
    if P >= pts[-1][0]: return pts[-1][1]
    for (p0, t0), (p1, t1) in zip(pts, pts[1:]):
        if p0 <= P <= p1: return 10 ** (math.log10(t0) + (P - p0) / (p1 - p0) * (math.log10(t1) - math.log10(t0)))

# typical / maximum currents per resistor (A): strip from master spec §27 (104 / 87 mA per strip, of which ~15 mA of
# LEDs and comparators on +VL) and docs/reviews/strip_parts_review.md T10 (R1 at the OPA1612's maximum: 0.125 W); group from §27
# (61 mA + return 1 followers 16 mA + RET1 30 mA; x 1.25 at maximum IQ), its logic rails up to 3 LEDs
DUTY = [('strip R1 +VA', 0.089, 0.112), ('strip R2 -VA', 0.087, 0.108), ('strip R3 +VL', 0.015, 0.022),
        ('strip R4 -VL', 0.001, 0.002), ('group R1 +VA', 0.107, 0.135), ('group R2 -VA', 0.107, 0.135),
        ('group R3 +VL', 0.010, 0.015), ('group R4 -VL', 0.001, 0.002)]
# source resistance seen by a fault at the far end of a wing: PTC (max initial) + 14 ribbon segments (0.213 ohm/m,
# 41 mm, 3 conductors on +V / 2 on -V) + two contacts per conductor (20 mOhm)
RSRC = {'+V': 0.13 + 14 * 0.213 * 0.041 / 3 + 2 * 0.02 / 3, '-V': 0.19 + 14 * 0.213 * 0.041 / 2 + 2 * 0.02 / 2}
WING = {'+V': (1.48, 2.07, 2.5, 5.0, 'MF-RX250/72'), '-V': (1.05, 1.30, 1.85, 3.7, 'MF-RX185/72')}

def ng(deck):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(deck)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True)
    os.unlink(f.name)
    return out.stdout + out.stderr

def pulse(fn):
    """peak current, energy in the 10R, time above 6.5 W, from wrdata columns (time, i)"""
    t, i = [], []
    for line in open(fn):
        v = line.split()
        if len(v) >= 2: t.append(float(v[0])); i.append(abs(float(v[1])))
    e = tabove = 0.0
    for k in range(1, len(t)):
        dt, p = t[k] - t[k - 1], R * (i[k] ** 2 + i[k - 1] ** 2) / 2
        e += p * dt; tabove += dt if p > 6.5 else 0.0
    return max(i), e, tabove


def module(name, vbus, c_va=220e-6, c_vl=47e-6, esr=0.15):
    """a strip / group: 10R + C on the audio rail (VA) and the logic rail (VL), currents through VM probes"""
    return [f'VM{name}a {vbus} {name}a1 0', f'RA{name} {name}a1 {name}a2 10', f'CA{name} {name}a2 {name}a3 {c_va}',
            f'RE{name}a {name}a3 0 {esr}',
            f'VM{name}l {vbus} {name}l1 0', f'RL{name} {name}l1 {name}l2 10', f'CL{name} {name}l2 {name}l3 {c_vl}',
            f'RE{name}l {name}l3 0 {esr * 2}']

def console(src_lines, hot=None):
    """+V side of the console: the source drives the master's J1, each wing through its PTC and the ribbon (14
    segments; module k hangs at segment k), the master's own branches at J1. hot: one module (wing L, last) that
    connects at t = 1 ms with the rest charged (initial conditions)."""
    L = ['* cs6 surges'] + src_lines
    L += ['RCAB src j1 0.04', 'LCAB j1 j1b 1.5u']        # 2 m supply cable
    # master branches: +VA 1R / 470u, +VP 2R2 / 1000u, +VM and +VL 10R / 47u
    for k, (r, c) in enumerate(((1.0, 470e-6), (2.2, 1000e-6), (10, 47e-6), (10, 47e-6))):
        L += [f'RMS{k} j1b ms{k} {r}', f'CMS{k} ms{k} 0 {c}']
    for w in 'LR':
        L += [f'RPTC{w} j1b w{w}0 0.13']
        for k in range(14):
            L += [f'RRB{w}{k} w{w}{k} w{w}{k}m {0.213 * 0.041 / 3:.5f}', f'LRB{w}{k} w{w}{k}m w{w}{k + 1} {0.6e-6 * 0.041 / 3:.3e}']
            name = f'{w}{k}'
            if hot and name == hot:
                L += [f'SHOT w{w}{k + 1} h{w}{k} ctl 0 SWH', '.model SWH SW(VT=0.5 VH=0.01 RON=0.06 ROFF=1e9)',
                      'VCTL ctl 0 PWL(0 0 1m 0 1.001m 1)', f'RBL h{w}{k} 0 1Meg']      # unplugged: discharged
                L += [l.replace(f'w{w}{k + 1}', f'h{w}{k}') for l in module(name, f'w{w}{k + 1}')]
            else: L += module(name, f'w{w}{k + 1}')
    return L

def surge(kind):
    if kind == 'soft':      # the PSU's soft start: 10 -> 90 % in 5 -> 165 ms (sim/psu.cir), tau ~73 ms, LDO limit 6 A
        src = ['BSRC src 0 V = 16.9*(1-exp(-time/73m))']
        L = console(src); tstop, probe = '400m', 'R13a'
    elif kind == 'lead':    # PSU running, lead plugged: its 220 uF output cap at 16.9 V, then the LDO in current limit
        src = ['CPSU psrc 0 220u IC=16.9', 'BLDO 0 psrc I = min(6, max(0, (16.9 - v(psrc)) * 100))', 'SPL psrc src ctl2 0 SWL',
               '.model SWL SW(VT=0.5 VH=0.01 RON=0.01 ROFF=1e9)', 'VCTL2 ctl2 0 PWL(0 0 1m 0 1.001m 1)']
        L = console(src); tstop, probe = '150m', 'R13a'
    else:                   # module 14 of the left wing plugged into the running console
        L = console(['VSRC src 0 16.9'], hot='L13'); tstop, probe = '40m', 'L13a'
    probes = [probe] + (['L13l'] if kind == 'hot' else [])
    fns = [os.path.join(tempfile.gettempdir(), f'cs6_{kind}_{p}.txt') for p in probes]
    wr = '\n'.join(f'wrdata {fn} i(VM{p})' for fn, p in zip(fns, probes))
    d = '\n'.join(L) + f"""
.options method=gear reltol=1e-4
.control
set wr_singlescale
tran 2u {tstop} 0 2u {'uic' if kind == 'lead' else ''}
{wr}
.endc
.end"""
    log = ng(d)
    res = []
    for fn, p in zip(fns, probes):
        try: res.append((p, *pulse(fn))); os.unlink(fn)
        except OSError: print(log[-1500:]); raise
    return res

if __name__ == '__main__':
    print(f'1. normal duty (M25SI 1206: {PRATED} W at 70 C, {KPW:.0f} K/W; film at {TAMB:.0f} C ambient, limit {TFMAX:.0f} C)')
    for name, it, im in DUTY:
        pt, pm = it * it * R, im * im * R
        print(f'   {name:13s}: {it * 1e3:5.1f} / {im * 1e3:5.1f} mA typ / max -> {pt * 1e3:5.1f} / {pm * 1e3:5.1f} mW '
              f'({pt / PRATED * 100:3.0f} / {pm / PRATED * 100:3.0f} % of rating), film {TAMB + pt * KPW:5.1f} / {TAMB + pm * KPW:5.1f} C')
    print('\n2. faults behind a resistor at the far end of a wing (the worst source resistance), fault resistance RF')
    for rail in ('+V', '-V'):
        wt, wc, hold, trip, ptc = WING[rail]
        print(f'   {rail} ({ptc}: hold {hold} A, trip {trip} A; wing load {wt} A typical, {wc} A in the accepted corner)')
        for rf in (0.0, 1.0, 5.0, 10.0, 20.0, 30.0, 47.0):
            i = VBUS / (R + RSRC[rail] + rf); p = i * i * R
            f, s = band(p, FAST), band(p, SLOW)
            fuse = (f'fuses in {f * 1e3:6.1f} ms - {s:7.2f} s' + (' (beyond the band: faster)' if p > 9 else '')) if f else \
                   f'below 3 W: no fusing specified, film ~{TAMB + p * KPW:4.0f} C'
            print(f'     RF {rf:4.1f} ohm: {i:5.3f} A, {p:5.2f} W: {fuse}; wing {wt + i:4.2f} / {wc + i:4.2f} A '
                  f'({"under trip" if wc + i < trip else "over trip"})')
    vpost = VBUS + 0.45
    print(f'\n   after fusing: at most the rail ({VBUS} V) plus a CS10 diode\'s drop for a +VA-to--VA short: {vpost:4.1f} V '
          f'across the open part (M25SI at 10 ohm: ~22 V)')
    print('\n3. surges through a module\'s 10R (ngspice): peak current, energy, time spent above 6.5 W (where the fastest')
    print('   parts of the band fuse in ~1 ms)')
    for kind, what in (('soft', 'power-up through the PSU soft start (all modules)'),
                       ('lead', 'PSU lead plugged into a running PSU (all modules)'),
                       ('hot', 'one module plugged into a live wing')):
        for p, ipk, e, tab in surge(kind):
            lab = 'VL 10R + 47u' if p.endswith('l') else 'VA 10R + 220u'
            print(f'   {what:52s} {lab:14s}: {ipk:5.2f} A peak, {e * 1e3:7.2f} mJ, {tab * 1e3:5.2f} ms above 6.5 W', flush=True)
