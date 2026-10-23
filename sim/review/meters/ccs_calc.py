"""Skeptic re-derivation of the meter string current source (gen_master.py: 75R from +VM, 2 x 1N4148 + 27K reference,
PNP, collector into 10 LEDs to -VM). Analytic, with datasheet-typical junction voltages instead of SPICE model values:
1N4148 ~0.61 V at 1.2 mA (+-30 mV), MMBT3906 VBE ~0.70 V at 6 mA (+-30 mV), large-die PNP (BCP53-16) ~0.63 V at 5 mA,
-2 mV/K for every junction. Diodes at ambient, PNP at Tj = Ta + Rth*P. Dark state: collector at -VM + 0.2 V."""
import math
VT = 0.0257; VM = 16.45
def solve(Re, vbe25, vd25, rth, ta=40.0, i0=6e-3):
    tj = ta; I = 5e-3
    for _ in range(200):
        vd = vd25 - 2e-3*(ta-25)
        vbe = vbe25 - 2e-3*(tj-25) + VT*math.log(max(I,1e-6)/i0)
        In = (2*vd - vbe)/Re
        I = 0.5*I + 0.5*In
        P = I*(2*VM - I*Re - 0.2)
        tn = ta + rth*P
        if tn > 300: return float('inf'), I, P
        tj = 0.5*tj + 0.5*tn
    return tj, I, P
print('isothermal 25 C string current, min / typ / max (Vd +-30 mV each, Vbe -+30 mV):')
for name, vbe, i0 in (('MMBT3906', 0.70, 6e-3), ('BCP53-16', 0.63, 5e-3)):
    for Re in (75, 91, 100, 120):
        lo = (2*(0.61-0.03) - (vbe+0.03))/Re; ty = (2*0.61 - vbe)/Re; hi = (2*(0.61+0.03) - (vbe-0.03))/Re
        print(f'  {name:9s} Re {Re:3d}: {lo*1e3:4.1f} / {ty*1e3:4.1f} / {hi*1e3:4.1f} mA')
print('dark-state self-heating at Ta 40 C (typ and high-current corner):')
for name, vbe, i0, rth, Re in (('MMBT3906 SOT-23 min pad', 0.70, 6e-3, 556, 75),
                               ('MMBT3906 SOT-23 ~2 cm2 Cu', 0.70, 6e-3, 300, 75),
                               ('MMBT3906 SOT-23 min pad', 0.70, 6e-3, 556, 100),
                               ('2N3906 TO-92', 0.70, 6e-3, 200, 75),
                               ('2N3906 TO-92', 0.70, 6e-3, 200, 100),
                               ('BCP53-16 SOT-223 std pad', 0.63, 5e-3, 160, 100),
                               ('BCP53-16 SOT-223 std pad', 0.63, 5e-3, 160, 120),
                               ('BCP53-16 SOT-223 1 cm2', 0.63, 5e-3, 95, 120)):
    t1, i1, p1 = solve(Re, vbe, 0.61, rth, i0=i0)
    t2, i2, p2 = solve(Re, vbe-0.03, 0.64, rth, i0=i0)
    print(f'  {name:28s} Re {Re:3d} Rth {rth:3d}: typ Tj {t1:6.1f} C, {i1*1e3:4.1f} mA, {p1*1e3:4.0f} mW | high corner Tj {t2:6.1f} C, {i2*1e3:4.1f} mA, {p2*1e3:4.0f} mW')
print('LED headroom, string fully lit, rails -2 %:')
vm = 17*0.98 - 0.5
for vf in (2.0, 2.4, 3.3, 4.1):
    for Re, I in ((75, 6e-3), (120, 5e-3)):
        vce = 2*vm - I*Re - 10*vf
        print(f'  Vf {vf} V x10, Re {Re}: Vce = {vce:5.1f} V')
print('+VM load (gen_master: TL072 x4, LM2901 x10, 4 strings, 2 ladders, 4 references):')
for cmp_i, label in ((1.0e-3, 'LM2901 ~1 mA/pkg'), (0.7e-3, 'LM2901B ~0.7 mA/pkg')):
    for Is in (6e-3, 5e-3):
        I = 4*2.8e-3 + 10*cmp_i + 4*Is + 2*16.9/23009 + 4*(2*16.9-1.2)/27e3
        print(f'  {label}, strings {Is*1e3:.0f} mA: {I*1e3:4.1f} mA -> +VM {16.95 - 10*I:5.2f} V; T11 = {0.6494*(16.95-10*I)/17:5.4f} V ({20*math.log10((16.95-10*I)/17):+.2f} dB vs 0.649 V)')
