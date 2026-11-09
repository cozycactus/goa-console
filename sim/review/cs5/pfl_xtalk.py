"""CS5 (docs/studies/console_survey.md §5): what reaches the PFL sum from the ribbon, and what each of the three proposed measures
changes. One wing of the motherloom: master header -> group 1, group 2, strips 1-12, 14 segments of 41 mm; conductors
25-31 (AUX2, GCANCEL, PFL, pin 28, PFL DET, -V, -V) with 28 AWG R / L per segment, 2.5 pF to the next conductor
(as tools/sim_console.py) and 0.4 pF to the one after (an estimate, ~10 pF/m; sim_console has none).
- PFL (27): the master's OPA1656 summer (22K // 100p, + input on GCANCEL) at the header; strip 1 pressed, its 22K from
  PFL_S (0 V here: the crosstalk is what the sum carries besides the programme); the released strips leave their key's
  pin 1 open, 1 pF (estimated PVA2 pole-to-pole capacitance) from it to that strip's +VL.
- AUX2 (25): a virtual-earth bus summed on group 2 (22K // 100p); strip 1 drives its 22K at 0 dBu.
- GCANCEL (26): 10R to each strip's ground (the strips' grounds are 0 V here).
- PFL DET (29): the master's 10K // 1 uF to GNDD; each released key 100K + 4K7 + LED (~100K) to GNDD; strip 1's key
  100K to its +VL (a 5 V step at the press for the click test).
- -V (30, 31): -17 V at the master through 0.1 ohm; each strip draws through its R2 10R / C3 220 uF; the signal-
  correlated part of its supply current (op-amp output stages) is an AC source of 10 mA per strip (a hard worst case).
- +VL per strip: 10R from +V with 47 uF; the AC on it is an input to the key test (a).
Configurations: pin 28 open (as built), pin 28 on GNDA at the master (b), PFL DET held at a virtual earth at the
master (c, modelled as 0 ohm to ground for AC). Reported in dB against the programme (0 dBu at PFL_SUM).
usage: python3 sim/review/cs5/pfl_xtalk.py"""
import os, re, math, subprocess, tempfile

SEGS, SEG_R, SEG_L, C1, C2 = 14, 0.213 * 0.041, 0.6e-6 * 0.041, 2.5e-12, 0.4e-12
PINS = range(25, 32)
OPAMP = """.subckt OPA inp inn out
* single pole, 53 MHz GBW, 120 dB DC
E1 x 0 inp inn 1e6
R1 x y 1k
C1 y 0 {1 / (2 * math.pi * 1e3 * 53e6 / 1e6)}
E2 out 0 y 0 1
.ends"""

def deck(cfg, src):
    """src: which aggressor carries the AC source ('aux', 'rail', 'vl', 'det'); cfg: 'built', 'g28', 'vedet'."""
    L = ['* pfl crosstalk', OPAMP.replace('{1 / (2 * math.pi * 1e3 * 53e6 / 1e6)}', f'{1 / (2 * math.pi * 1e3 * 53):.4e}')]
    n = lambda p, k: f'c{p}_{k}'
    for k in range(SEGS):                                   # segment k joins position k (k = 0: master header) to k + 1
        for p in PINS:
            L += [f'R{p}_{k} {n(p, k)} {n(p, k)}m {SEG_R}', f'L{p}_{k} {n(p, k)}m {n(p, k + 1)} {SEG_L}']
        for p in PINS:
            if p + 1 in PINS: L.append(f'CA{p}_{k} {n(p, k + 1)} {n(p + 1, k + 1)} {C1}')
            if p + 2 in PINS: L.append(f'CB{p}_{k} {n(p, k + 1)} {n(p + 2, k + 1)} {C2}')
    # master (position 0): PFL summer, PFL DET network, -V entry, GCANCEL reference, pin 28
    L += ['XPFL 0 c27_0 pflsum OPA', 'RPF pflsum c27_0 22k', 'CPF pflsum c27_0 100p']
    L += ['RD c29_0 0 10k', 'CD c29_0 0 1u'] if cfg != 'vedet' else ['RD c29_0 0 1m']
    L += ['VNEG vneg 0 DC -17', 'RNEG vneg c30_0 0.1', 'RNEG2 vneg c31_0 0.1', 'RGC c26_0 0 1m']
    if cfg == 'g28': L.append('R28 c28_0 0 1m')
    # group 2 (position 2): AUX2 summer
    L += ['XAUX 0 c25_2 auxsum OPA', 'RAX auxsum c25_2 22k', 'CAX auxsum c25_2 100p']
    for k in range(1, SEGS + 1):
        strip = k >= 3
        L.append(f'RGCs{k} c26_{k} 0 10')
        if not strip: continue
        first = k == 3
        # PFL: strip 1 pressed (22K from PFL_S at 0 V); the rest open, 1 pF to +VL
        if first: L.append(f'RPS{k} c27_{k} 0 22k')
        else: L.append(f'CK{k} c27_{k} vl{k} 1p')
        # +VL: 10R from +V (AC ground here) and 47 uF; the AC test drives every strip's +VL through a current source
        L += [f'RVL{k} vl{k} 0 10', f'CVL{k} vl{k} 0 47u']
        if src == 'vl': L.append(f'IVL{k} 0 vl{k} DC 0 AC 1m')
        # PFL DET: pressed 100K to +VL (strip 1), released ~100K to GNDD
        L.append(f'RDT{k} c29_{k} {"pon" if first else "0"} 100k')
        if first: L.append('VSTEP pon 0 DC 0 PULSE(0 5 1u 1u 1u 1 2)' if src == 'det' else f'RPON pon vl{k} 1m')
        # AUX2: strip 1 drives its 22K at 0 dBu (AC 1 = 1 V; reported against 0.7746)
        L.append(f'RAUX{k} c25_{k} {"aux" if first else "0"} 22k')
        # -V: R2 10R and C3 220 uF per strip; the AC part of its supply current
        L += [f'R2s{k} c30_{k} vn{k} 5', f'R2t{k} c31_{k} vn{k} 5', f'C3s{k} vn{k} 0 220u']
        if src == 'rail': L.append(f'IRAIL{k} vn{k} 0 DC 0 AC 10m')
    if src == 'aux': L.append('VAUX aux 0 DC 0 AC 1')
    else: L.append('RAUXS aux 0 1m')
    L += [f'RLEAK{p} c{p}_{SEGS} 0 1e9' for p in PINS]
    return '\n'.join(L)

def ac(cfg, src, f):
    d = deck(cfg, src) + f"""
.control
ac lin 1 {f} {f}
let x = mag(v(pflsum))
print x
.endc
.end"""
    return float(run(d).get('x', 'nan'))

def step(cfg):
    d = deck(cfg, 'det') + """
.control
tran 1u 20m 0 1u
let x = abs(v(pflsum))
meas tran pk max x
.endc
.end"""
    return float(run(d).get('pk', 'nan'))

def run(d):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as fh: fh.write(d)
    out = subprocess.run(['ngspice', '-b', fh.name], capture_output=True, text=True).stdout
    os.unlink(fh.name)
    return {k.lower(): v for k, v in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', out, re.M)}

db = lambda v, ref=1.0: 20 * math.log10(max(v, 1e-30) / ref)
CFG = (('built', 'as built (pin 28 open)'), ('g28', '(b) pin 28 on GNDA at the master'), ('vedet', '(c) PFL DET at a virtual earth'))

if __name__ == '__main__':
    print('1. AUX2 (pin 25, a virtual-earth bus) at 0 dBu from strip 1 -> PFL sum, dB against the programme')
    for cfg, name in CFG:
        print(f'   {name:34s}: ' + ', '.join(f'{f / 1e3:4.0f} kHz {db(ac(cfg, "aux", f)):7.1f} dB' for f in (1e3, 20e3)), flush=True)
    print('\n2. -V (pins 30 / 31): 10 mA AC of supply current per strip (12 strips) -> PFL sum, dBu')
    for cfg, name in CFG:
        print(f'   {name:34s}: ' + ', '.join(f'{f / 1e3:4.0f} kHz {db(ac(cfg, "rail", f), 0.7746):7.1f} dBu' for f in (1e3, 20e3)), flush=True)
    print('\n3. (a) the keys: 1 mA AC into every strip\'s +VL (its 10R / 47 uF: ~3.4 mV at 1 kHz), 1 pF from each released')
    print('   key\'s pin 1 to its +VL, onto the PFL bus -> PFL sum, dBu')
    for cfg, name in CFG[:1]:
        print(f'   {name:34s}: ' + ', '.join(f'{f / 1e3:4.0f} kHz {db(ac(cfg, "vl", f), 0.7746):7.1f} dBu' for f in (1e3, 20e3)), flush=True)
    print('\n4. the press: strip 1\'s PFL_ON steps 0 -> 5 V in 1 us (the key closing onto +VL); peak at the')
    print('   PFL sum, dBu')
    for cfg, name in CFG:
        print(f'   {name:34s}: {db(step(cfg), 0.7746 * math.sqrt(2)):7.1f} dBu (peak, as a sine)', flush=True)
