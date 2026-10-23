"""Aux / PFL summing amp + re-inverter output noise, 20 Hz - 20 kHz unweighted, for candidate op-amps.

Circuit (master_lib.summer + reinv, as generated in master.net / group.net):
  N sources x Ri (22K + Rs, Rs = source/wiper resistance) -> bus (Cbus) -> ferrite -> inverting input
  Rf 22K || Cf 100p, + input on GCANCEL (~0.36 ohm: 10R per strip/group in parallel, negligible)
  re-inverter: 4 x 2K2 difference amp, out = GCANCEL_BUF - SUM; GCANCEL_BUF = OPA1612 follower.
Op-amp noise: log-log interpolation through datasheet table/figure points (flat beyond the last point,
first-segment slope extrapolated below the first point).  T = 300 K.
"""
import math
import numpy as np

k, T = 1.380649e-23, 300.0
FOURKT = 4 * k * T

# (en points [(f, nV/rtHz)], in points [(f, pA/rtHz)], source)
PARTS = {
 'OPA1612': ([(10, 2.0), (100, 1.5), (1e3, 1.1)], [(10, 3.0), (1e3, 1.7)],
             'SBOS450C Table 6.5 (en 2/1.5/1.1 @10/100/1k, in 3/1.7 @10/1k), Fig 1'),
 'OPA1656': ([(10, 37), (100, 11.8), (1e3, 4.3), (1e4, 2.9)], [(1e3, 0.006)],
             'SBOS901C Table 6.6 (11.8/4.3/2.9 @100/1k/10k, in 6 fA), 10 Hz from Fig 6-1'),
 'NE5534A': ([(30, 5.5), (1e3, 3.5)], [(30, 1.5), (1e3, 0.4)],
             'SLOS070D 7.6 (NE5534A: Vn 5.5/3.5 @30/1k, In 1.5/0.4 @30/1k)'),
 'LM4562':  ([(10, 6.4), (1e3, 2.7)], [(10, 3.1), (1e3, 1.6)],
             'SNAS326K Electrical Characteristics (6.4/2.7 nV, 3.1/1.6 pA @10/1k)'),
 'OPA1642': ([(10, 8), (100, 5.8), (1e3, 5.1)], [(1e3, 0.0008)],
             'SBOS484D 6.5 (8/5.8/5.1 @10/100/1k, 0.8 fA)'),
 'OPA2156': ([(100, 12.0), (1e3, 4.0), (1e4, 3.0)], [(1e3, 0.019)],
             'SBOS900B 6.5 (12/4/3 @100/1k/10k, 19 fA)'),
 'OPA1678': ([(10, 36), (100, 11.5), (1e3, 4.5), (1e4, 4.2)], [(1e3, 0.003)],
             'SBOS855E 6.5 (4.5 @1k, 3 fA) + Fig 6-1 (36/11.5 @10/100, 4.2 floor)'),
 'OPA1602': ([(100, 2.5), (1e3, 2.5)], [(100, 2.2), (1e3, 1.8)],
             'SBOS474B (2.5 nV @100/1k, 2.2/1.8 pA @100/1k)'),
 'OPA2210': ([(10, 3.0), (100, 2.25), (1e3, 2.2)], [(10, 0.55), (100, 0.42), (1e3, 0.40)],
             'SBOS924H 6.5 (2.25 @100, 2.2 @1k, 0.4 pA @1k) + Fig 6-3/6-4 for 10 Hz'),
}

def interp(points, f):
    fs = np.array([p[0] for p in points], float); vs = np.array([p[1] for p in points], float)
    if len(fs) == 1:
        return np.full_like(f, vs[0])
    lf, lv = np.log10(fs), np.log10(vs)
    x = np.log10(f)
    y = np.interp(x, lf, lv)                      # flat outside the range...
    lo = x < lf[0]                                # ...except: extend the first slope downwards
    slope = (lv[1] - lv[0]) / (lf[1] - lf[0])
    y[lo] = lv[0] + slope * (x[lo] - lf[0])
    return 10 ** y

CAL = {}          # en scale factors, set below so a part's integrated 20 Hz-20 kHz noise matches its datasheet figure
def en(part, f): return interp(PARTS[part][0], f) * 1e-9 * CAL.get(part, 1.0)
def inn(part, f): return interp(PARTS[part][1], f) * 1e-12

F = np.logspace(math.log10(20), math.log10(20e3), 4000)
def integ(psd): return math.sqrt(np.trapezoid(psd, F))
def dbu(v): return 20 * math.log10(v / 0.7746)

def chain(part, N, Ri=22e3, Rs=0.0, Rf=22e3, Cf=100e-12, Cbus=1e-9, Rr=2.2e3, ri_part=None, gref_part='OPA1612',
          parts_out=False):
    """PSD at the re-inverter output (V^2/Hz) and the breakdown."""
    ri_part = ri_part or part
    w = 2 * np.pi * F
    Zf = Rf / (1 + 1j * w * Rf * Cf)
    Rin = Ri + Rs
    Zg = 1 / (N / Rin + 1j * w * Cbus) if N else 1 / (1j * w * Cbus)
    NG = 1 + Zf / Zg
    c = {}
    c['sum en'] = en(part, F) ** 2 * abs(NG) ** 2
    c['sum in x Rf'] = inn(part, F) ** 2 * abs(Zf) ** 2
    c['Rf thermal'] = FOURKT * Rf * abs(1 / (1 + 1j * w * Rf * Cf)) ** 2
    c['input R thermal'] = N * FOURKT * Rin * abs(Zf / Rin) ** 2
    c['reinv en (x2)'] = 4 * en(ri_part, F) ** 2
    c['reinv in'] = 2 * (inn(ri_part, F) * Rr) ** 2
    c['reinv 4x2K2'] = 4 * FOURKT * Rr * np.ones_like(F)
    c['GCANCEL_BUF'] = en(gref_part, F) ** 2
    tot = sum(c.values())
    if parts_out:
        return tot, c
    return tot

def check_integrals():
    print('Datasheet cross-check, input voltage noise integrated 20 Hz-20 kHz:')
    ref = {'OPA1656': '0.53 uVrms (SBOS901C 6.6)', 'LM4562': '0.34 uVrms (SNAS326K)',
           'OPA1612': '1.2 uVpp ~ 0.18 uVrms', 'OPA1642': '4.3 uVpp ~ 0.65 uVrms',
           'OPA1678': '5.4 uVpp ~ 0.82 uVrms', 'OPA1602': '2.5 uVpp ~ 0.38 uVrms'}
    for p in PARTS:
        v = integ(en(p, F) ** 2)
        print(f'  {p:8s} {v*1e6:5.3f} uVrms  ({v/math.sqrt(19980)*1e9:4.2f} nV/rtHz rms-avg)   datasheet: {ref.get(p, "-")}')

def table(Ns, title, **kw):
    print(f'\n{title}')
    hdr = 'N    ' + ''.join(f'{p:>9s}' for p in PARTS) + '   resistors-only'
    print(hdr)
    for N in Ns:
        row = f'{N:<4d} '
        for p in PARTS:
            row += f'{dbu(integ(chain(p, N, **kw))):9.1f}'
        # ideal op-amps, ideal GCANCEL buffer
        _, c = chain('OPA1656', N, parts_out=True, **kw)
        r = c['Rf thermal'] + c['input R thermal'] + c['reinv 4x2K2']
        row += f'{dbu(integ(r)):12.1f}'
        print(row)

def breakdown(part, N, **kw):
    tot, c = chain(part, N, parts_out=True, **kw)
    s = ', '.join(f'{n} {integ(v)*1e6:.2f}' for n, v in c.items())
    print(f'  {part} N={N}: total {integ(tot)*1e6:.2f} uV = {dbu(integ(tot)):.1f} dBu  [{s}] (uVrms)')

if __name__ == '__main__':
    import sys
    check_integrals()
    if '--raw' not in sys.argv:
        v = integ(en('OPA1656', F) ** 2)
        CAL['OPA1656'] = 0.53e-6 / v           # SBOS901C 6.6: 0.53 uVrms, 20 Hz-20 kHz
        print(f'OPA1656 en scaled x{CAL["OPA1656"]:.3f} to the datasheet 0.53 uVrms (20 Hz-20 kHz); '
              f'rms-average {0.53e-6/math.sqrt(19980)*1e9:.2f} nV/rtHz (spec 13 assumed 3.3)')
    table([1, 2, 4, 12, 24, 32], 'AUX / PFL, 22K, Rs = 0 (dBu at the re-inverter output, 20 Hz-20 kHz unweighted)')
    table([24, 32], 'AUX, aux pots at a typical setting: wiper source resistance 1.3K (A10K near -15 dB)', Rs=1.3e3)
    table([24], 'AUX, worst wiper source resistance 2.5K', Rs=2.5e3)
    print('\nBreakdown (uVrms in 20 Hz-20 kHz at the re-inverter output):')
    for N in (1, 2, 24):
        for p in ('OPA1612', 'OPA1656', 'NE5534A'):
            breakdown(p, N)
    print('\nMixed: OPA1656 sum + OPA1612 re-inverter (not possible in one dual, for reference):')
    for N in (1, 24):
        print(f'  N={N}: {dbu(integ(chain("OPA1656", N, ri_part="OPA1612"))):.1f} dBu')
    # crossover N where OPA1656 == OPA1612
    for N in range(1, 40):
        a = dbu(integ(chain('OPA1612', N))); b = dbu(integ(chain('OPA1656', N)))
        if a < b:
            print(f'\nOPA1612 becomes quieter than OPA1656 from N = {N} ({a:.1f} vs {b:.1f} dBu)')
            break
