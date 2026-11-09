"""HI-MID / LO-MID frequency tuning: the Delta's Wien band-pass with a 100K C-law dual (not stocked)
against a KHN state-variable band-pass tuned by a stocked Alpha A100K dual (strip spec §6.2).
usage: python3 sim/mid_tuning.py [pot ohms, default 100e3]      (needs ngspice)
HISTORICAL (the 2026-10-22 tuning study, 430R / 13K / 4K7 per band, 670 Hz-10.5 kHz / 148 Hz-2.32 kHz): since strip v5.5
(EQM1, docs/proposals/eqmid_proposal.md) the built ranges are 598 Hz-9.93 kHz and 165 Hz-2.54 kHz; the current values, the panel FREQ
numerals and the sim_netlist peak checks come from sim/review/eqmid/retune.py and measure.py, not from here.

Both versions drive the same band stage: U6A-style inverting unity amp (22K/22K) with the band-pass of
the 10K gain-pot wiper on its + input, as in sim/strip_v4.cir. The KHN reproduces the Wien band-pass
(peak gain 0.407, Q 0.2747, in phase); every internal node stays at or below the input level.
Pot laws: Alpha catalogue tapers are two straight slopes, 15 % at mid-rotation (A); C is its mirror.
KHN per band: summer (R1 = R2 = R3 = 10K, BP to + input via R4/R5), two integrators C1 / C2 fed through
the pot dividers: pot top = driving op-amp output, RTOP wiper-to-top, pin 1 -> R0 -> AGND, wiper -> RB."""
import math, re, subprocess, sys, tempfile, os

A15 = lambda t: 0.30 * t if t <= 0.5 else 0.15 + 1.70 * (t - 0.5)
C15 = lambda t: 1 - A15(1 - t)
BANDS = {   # Delta Wien: series C, shunt C;  KHN integrator caps C1, C2 for a 100K pot (x10 for 10K)
    'HI-MID': dict(cs=3.3e-9, cp=1.5e-9, c1=220e-12, c2=470e-12, fmin=670, fmax=10.5e3),
    'LO-MID': dict(cs=15e-9, cp=6.8e-9, c1=1.0e-9, c2=2.2e-9, fmin=148, fmax=2.32e3)}
R4, R5 = 2.2e3, 10e3                    # BP to the summer's + input: 0.82, sets peak gain 0.407
RSUM = 10e3                             # summer R1 = R2 = R3 (input, LP, feedback)
POT = 100e3                             # A-law dual; divider R0 / RTOP / RB scale with it
def net(pot):                           # (R0, RTOP, RB, cap scale): fitted for a 0.28-octave log law
    k = pot / 100e3
    return 4.3e3 * k, 130e3 * k, 47e3 * k, 1 / k

OPA = """.subckt OPA inp inn out
* OPA1612: GBW 40 MHz, A0 120 dB, 1.1 nV/rtHz and 1.7 pA/rtHz as resistor noise (73R series, 5.7M shunts)
RENX inp ip 73
RINP ip 0 5.7meg
RINN inn 0 5.7meg
G1 0 n1 ip inn 1
R1 n1 0 1e6 noisy=0
C1 n1 0 3.98n
E1 out 0 n1 0 1
.ends"""

def stage(kind, b, theta, gain, extra=''):
    """One band: source -> 10K gain pot (wiper w) -> band-pass -> + input of U (o4 = stage output)."""
    p = 10e3
    L = ['* band ' + kind, OPA, 'VIN in 0 DC 0 AC 0.7746',
         f'RGA in w {p * gain + 0.01}', f'RGB w o4 {p * (1 - gain) + 0.01}',
         'RI in m 22k', 'RF o4 m 22k', 'XU bp m o4 OPA']
    if kind == 'delta':
        rh = 100e3 * (1 - C15(theta)) + 0.01                 # each gang: wiper-to-pin-3 rheostat
        L += [f'CS w s1 {b["cs"]}', f'RS s1 s2 6.8k', f'RA s2 bp {rh}',
              f'CP bp 0 {b["cp"]}', f'RBB bp s3 {rh}', 'RP s3 0 6.8k']
    else:
        R0, RTOP, RB, cs = net(POT)
        a = A15(theta); top, bot = POT * (1 - a) + 0.01, POT * a + 0.01
        L += [f'R1 w sm {RSUM}', f'R2 lpn sm {RSUM}', f'R3 hp sm {RSUM}', f'R4 bpo sp {R4}', f'R5 sp 0 {R5}',
              'XS sp sm hp OPA',
              # integrator 1: HP -> pot divider -> RB -> C1 ; output = BP
              f'RT1 hp d1 {top}', f'RL1 d1 p1 {bot}', f'R01 p1 0 {R0}', f'RX1 hp d1 {RTOP}', f'RB1 d1 i1 {RB}',
              f'CI1 bpo i1 {b["c1"] * cs}', 'XI1 0 i1 bpo OPA',
              # integrator 2: BP -> pot divider -> RB -> C2 ; output = -LP (inverting)
              f'RT2 bpo d2 {top}', f'RL2 d2 p2 {bot}', f'R02 p2 0 {R0}', f'RX2 bpo d2 {RTOP}', f'RB2 d2 i2 {RB}',
              f'CI2 lpn i2 {b["c2"] * cs}', 'XI2 0 i2 lpn OPA',    # two inversions: lpn = +LP, straight to R2
              'VBP bpo bp 0']
    L += [extra, '.end']
    return '\n'.join(l for l in L if l)

def run(deck, ctrl):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f:
        f.write(deck.replace('.end', '.control\nset noaskquit\n' + ctrl + '\n.endc\n.end')); fn = f.name
    out = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True).stdout
    os.unlink(fn)
    res = {}
    for line in out.splitlines():
        m = re.match(r'^(\w+)\s*=\s*([-+0-9.eE]+)(?:\s+at=\s*([-+0-9.eE]+))?', line.strip())
        if m:
            res[m.group(1).lower()] = float(m.group(2))
            if m.group(3): res[m.group(1).lower() + '_at'] = float(m.group(3))
    return res

def band(kind, b, theta, gain):
    r = run(stage(kind, b, theta, gain), 'ac dec 200 10 100k\nlet g = db(mag(v(o4))/0.7746)\n'
            'meas ac pk max g\nmeas ac pkmin min g\nlet gn = g - pk + 3\n'
            'meas ac flo when gn=0 rise=1\nmeas ac fhi when gn=0 fall=1\n'
            'meas ac g20 find g at=20\nmeas ac g20k find g at=20k')
    return r

if __name__ == '__main__':
    POT = float(sys.argv[1]) if len(sys.argv) > 1 else POT
    print(f'KHN pot: A{POT/1e3:.0f}K dual, R0/RTOP/RB = ' + ' / '.join(f'{x/1e3:.3g}K' for x in net(POT)[:3]))
    for name, b in BANDS.items():
        print(f'== {name} (Delta range {b["fmin"]:.0f} Hz - {b["fmax"]/1e3:.2f} kHz)')
        print(' theta | Delta (C15): f0 Hz  boost  cut   Q    | KHN (A15): f0 Hz  boost  cut   Q    | ideal log f0')
        for th in (0, 0.25, 0.5, 0.75, 1.0):
            row = []
            for kind in ('delta', 'khn'):
                bo, cu = band(kind, b, th, 1.0), band(kind, b, th, 0.0)
                f0 = bo.get('pk_at', 0); q = f0 / (bo.get('fhi', 1) - bo.get('flo', 0)) if bo.get('fhi') else 0
                row.append((f0, bo.get('pk', 0), cu.get('pkmin', 0), q))
            ideal = b['fmin'] * (b['fmax'] / b['fmin']) ** th
            print(' %4.2f  | %8.0f  %+5.1f  %+5.1f  %4.2f | %8.0f  %+5.1f  %+5.1f  %4.2f | %8.0f' %
                  (th, *row[0], *row[1], ideal))
        for kind in ('delta', 'khn'):
            fl = band(kind, b, 0.5, 0.5)
            print(f'  {kind}: flat (gain at centre) deviation {max(abs(fl.get("pk", 0)), abs(fl.get("pkmin", 0))):.2f} dB')
        # noise at the stage output, gain at centre, frequency at mid rotation, 20 Hz - 20 kHz
        for kind in ('delta', 'khn'):
            r = run(stage(kind, b, 0.5, 0.5), 'noise v(o4) VIN dec 20 20 20k\nlet n = 20*log10(onoise_total/0.7746)\nprint n')
            print(f'  {kind}: output noise {r.get("n", 0):.1f} dBu (20 Hz - 20 kHz, flat, theta 0.5)')
        # headroom: largest KHN internal node vs input over frequency, full boost and full cut, theta 0 / 1
        worst = 0
        for th in (0, 1):
            for g in (0, 1):
                r = run(stage('khn', b, th, g), 'ac dec 50 10 100k\n' + '\n'.join(
                    f'let x{n} = db(mag(v({n}))/0.7746)\nmeas ac m{n} max x{n}' for n in ('hp', 'bpo', 'lpn', 'o4', 'w')))
                worst = max([worst] + [r.get(f'm{n}', 0) for n in ('hp', 'bpo', 'lpn')])
        print(f'  khn: largest internal node (HP/BP/LP) {worst:+.1f} dB re input (stage output itself reaches +14.6)')
