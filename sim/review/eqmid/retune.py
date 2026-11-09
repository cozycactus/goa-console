"""KHN mid retune (docs/proposals/eqmid_proposal.md): the mid bands' frequency ranges against the Delta's measured ones (200 Delta Tech
Manual p.17 / DLX user guide p.15, the Audio Precision plots: HI ~600 Hz - 10 kHz, LO ~165 Hz - 2.55 kHz; the ED2911A
labels read 600-10k and 150-2.4k). Resistor values only: per band R0 (pin 1 to ground), RTOP (top to wiper) and RB
(wiper to the integrator); the A10K dual and the integrator caps stay.
Each gang is a divider from the driving op-amp: upper section (1 - a) P // RTOP, lower a P + R0; Thevenin k, Rth at the
wiper; integrator time constant (Rth + RB) C / k, so f0 = k / (2 pi (Rth + RB) sqrt(C1 C2)) with both gangs alike.
a(theta): the Alpha A taper as two slopes (15 % at mid-rotation), as everywhere in the project.
usage: python3 sim/review/eqmid/retune.py"""
import math
P = 10e3
A15 = lambda t: 0.30 * t if t <= 0.5 else 0.15 + 1.70 * (t - 0.5)
E96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54,
       1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43,
       2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83,
       3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04,
       6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
e96 = lambda v: min((m * 10 ** d for d in range(0, 7) for m in E96), key=lambda x: abs(math.log(x / v)))
BANDS = {'HI-MID': dict(c=(2.2e-9, 4.7e-9), now=(430, 13e3, 4.7e3), target=(600, 10.0e3)),
         'LO-MID': dict(c=(10e-9, 22e-9), now=(430, 13e3, 4.7e3), target=(165, 2.55e3))}

def f0(theta, c, r0, rtop, rb):
    a = A15(theta); lo = a * P + r0; up = (1 - a) * P
    up = up * rtop / (up + rtop) if up > 0 else 0.0
    k = lo / (lo + up); rth = lo * up / (lo + up)
    return k / (2 * math.pi * (rth + rb) * math.sqrt(c[0] * c[1]))

def fit(c, fmin, fmax, rtop):
    rb = 1 / (2 * math.pi * fmax * math.sqrt(c[0] * c[1]))
    lo_, hi_ = 10.0, 5e3                                   # R0 by bisection for fmin (f0 at theta 0 rises with R0)
    for _ in range(80):
        m = math.sqrt(lo_ * hi_)
        if f0(0, c, m, rtop, rb) < fmin: lo_ = m
        else: hi_ = m
    return lo_, rb

def law(c, r):
    fmin, fmax = f0(0, c, *r), f0(1, c, *r)
    dev = max(abs(math.log2(f0(t / 20, c, *r) / (fmin * (fmax / fmin) ** (t / 20)))) for t in range(21))
    return fmin, fmax, dev

if __name__ == '__main__':
    for name, b in BANDS.items():
        c = b['c']; print(f'== {name}: C1 / C2 {c[0] * 1e9:g} / {c[1] * 1e9:g} nF, target {b["target"][0]:.0f} Hz - {b["target"][1] / 1e3:.2f} kHz')
        fmin, fmax, dev = law(c, b['now']); print(f'   as built  R0 / RTOP / RB = 430R / 13K / 4K7: {fmin:6.0f} Hz - {fmax / 1e3:5.2f} kHz, '
                                                   f'worst {dev:.2f} oct from a log sweep')
        for rtop in (10e3, 12e3, 13e3, 15e3, 18e3):
            r0, rb = fit(c, *b['target'], rtop)
            for tag, r in (('exact', (r0, rtop, rb)), ('E96  ', (e96(r0), rtop, e96(rb)))):
                fmin, fmax, dev = law(c, r)
                print(f'   RTOP {rtop / 1e3:4.1f}K {tag} R0 {r[0]:7.1f}  RB {r[2]:7.1f}: {fmin:6.0f} Hz - {fmax / 1e3:5.2f} kHz, '
                      f'worst {dev:.2f} oct; f0 at theta 0.25 / 0.5 / 0.75: ' + ' / '.join(f'{f0(t, c, *r):.0f}' for t in (0.25, 0.5, 0.75)))
