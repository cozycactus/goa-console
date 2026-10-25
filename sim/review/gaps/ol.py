"""Strip overload detector (U4A LM393, spec 8.1), the one strip circuit no earlier simulation covered (2026-10-25).
PRESRC (BUF1, U7B's follower output with JP7 at 1-2) -> R39 1K -> D1 -> PK (C12 1u // R14 470K) -> U4A - input;
VREF = +VL / 2 (R40 / R41 10K) at the + input; output sinks OL_K, lighting D2 from +VL through R15 4K7.
Part values are read from channel_strip.net, so the deck follows the schematic.
usage: python3 sim/review/gaps/ol.py
Models: 1N4148 (standard), red GaAsP LED fitted to ~1.9 V at 3 mA, LM393 as a sink switch (60 ohm, threshold at
VREF, ideal speed; the real part's 1.3 us response is far below the detector's 1 ms charge time). The source is
ideal: PRESRC is an op-amp output."""
import os, re, sys, math, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '..', '..', '..')
sys.path.insert(0, os.path.join(REPO, 'tools'))
from verify import sexp, field

net = sexp(open(os.path.join(REPO, 'channel_strip.net')).read())
VAL = {field(c, 'ref'): field(c, 'value') for c in next(x for x in net[1:] if isinstance(x, list) and x[0] == 'components')[1:]}
def v(ref):
    t = VAL[ref].split()[0]; m = re.fullmatch(r'(\d+)([RKkMpnuµ])(\d*)', t)
    return float(m.group(1) + ('.' + m.group(3) if m.group(3) else '')) * {'R': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6}[m.group(2)]
VL = 16.9                                              # +VL: +17 V less R3's drop

def deck(src, tstop, extra=''):
    return f"""* strip overload detector
.model D1N4148 D(IS=2.52n RS=0.568 N=1.752 CJO=4p M=0.4 TT=20n BV=100)
.model LEDR D(IS=1e-20 N=1.8 RS=5)
.model SW393 SW(VT=0 VH=0.001 RON=60 ROFF=1e9)
VVL vl 0 DC {VL}
{src}
R39 presrc pka {v('R39')}
D1 pka pk D1N4148
C12 pk 0 {v('C12')}
R14 pk 0 {v('R14')}
R40 vl vref {v('R40')}
R41 vref 0 {v('R41')}
S4 olk 0 pk vref SW393
R15 vl ola {v('R15')}
VLED ola ola2 0
D2 ola2 olk LEDR
{extra}
.control
set noaskquit
tran 20u {tstop} 0 20u
meas tran pkmax max v(pk)
meas tran ledon when v(olk)=1 fall=1
meas tran ledoff when v(olk)=1 rise=1
meas tran imax max i(VLED)
.endc
.end"""

def run(d):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    return {k.lower(): float(x) for k, x in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', out, re.M)}

dbu = lambda vrms: 20 * math.log10(vrms / 0.7746)
vrms = lambda d: 0.7746 * 10 ** (d / 20)

def lights(level, f, tstop=0.3):
    r = run(deck(f'VS presrc 0 SIN(0 {vrms(level) * math.sqrt(2)} {f})', tstop))
    return 'ledon' in r

def threshold(f):
    lo, hi = 10.0, 24.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if lights(mid, f): hi = mid
        else: lo = mid
    return hi

if __name__ == '__main__':
    print(f'values: R39 {VAL["R39"]}, C12 {VAL["C12"]}, R14 {VAL["R14"]}, VREF {VL / 2:.2f} V (R40 / R41 {VAL["R40"]} / {VAL["R41"]}), R15 {VAL["R15"]}')
    print('steady sine: OL lights from')
    for f in (50, 1000, 10000):
        print(f'  {f:6d} Hz: {threshold(f):5.1f} dBu')
    print('bursts at 1 kHz (n cycles), and how long the LED stays lit:')
    for lvl in (19.0, 20.0, 22.0):
        for n in (1, 2, 5, 20):
            a = vrms(lvl) * math.sqrt(2); t1 = 1e-3 + n * 1e-3          # n whole cycles of 1 kHz from 1 ms
            r = run(deck(f'BS presrc 0 V = {a} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < {t1})', 1.0))
            on = r.get('ledon'); off = r.get('ledoff')
            hold = f'{(off - on) * 1e3:6.0f} ms' if on and off else ('stays lit' if on else '   --')
            print(f'  {lvl:4.0f} dBu, {n:2d} cycle(s): PK {r["pkmax"]:5.2f} V, LED {"on" if on else "off"}, lit {hold}')
    r = run(deck(f'VS presrc 0 SIN(0 {vrms(22) * math.sqrt(2)} 1000)', 0.3))
    print(f'LED current while lit (+22 dBu, 1 kHz): {r["imax"] * 1e3:.2f} mA')
