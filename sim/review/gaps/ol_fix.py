"""Proposed overload detector (gaps_proposal.md K3), against the built one: C12 1u -> 100n (attack 0.1 ms) and a hold
stage on U4B, the package's spare comparator: U4A's output now discharges a hold cap (HOLD: Rh to +VL, Ch to GNDD)
instead of driving the LED; U4B lights the LED while HOLD is below VREF, a fixed ~150 ms after the last overload.
usage: python3 sim/review/gaps/ol_fix.py [rh ch]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ol
from ol import v, VL, run, vrms

RH = float(sys.argv[1]) if len(sys.argv) > 2 else 1e6
CH = float(sys.argv[2]) if len(sys.argv) > 2 else 220e-9
C12 = 100e-9

def deck(src, tstop):
    return f"""* proposed overload detector
.model D1N4148 D(IS=2.52n RS=0.568 N=1.752 CJO=4p M=0.4 TT=20n BV=100)
.model LEDR D(IS=1e-20 N=1.8 RS=5)
.model SW393 SW(VT=0 VH=0.001 RON=60 ROFF=1e9)
VVL vl 0 DC {VL}
{src}
R39 presrc pka {v('R39')}
D1 pka pk D1N4148
C12 pk 0 {C12}
R14 pk 0 {v('R14')}
R40 vl vref {v('R40')}
R41 vref 0 {v('R41')}
S4A hold 0 pk vref SW393
RH vl hold {RH}
CH hold 0 {CH} IC={VL}
S4B olk 0 vref hold SW393
R15 vl ola {v('R15')}
VLED ola ola2 0
D2 ola2 olk LEDR
.ic v(hold)={VL}
.control
set noaskquit
tran 20u {tstop} 0 20u
meas tran pkmax max v(pk)
meas tran ledon when v(olk)=1 fall=1
meas tran ledoff when v(olk)=1 rise=1
meas tran imax max i(VLED)
.endc
.end"""

ol.deck = deck
print(f'proposed: C12 {C12 * 1e9:.0f}n, hold {RH / 1e6:.1f}M / {CH * 1e9:.0f}n (tau {RH * CH * 1e3:.0f} ms)')
print('steady sine: OL lights from')
for f in (50, 1000, 10000):
    print(f'  {f:6d} Hz: {ol.threshold(f):5.1f} dBu')
print('bursts at 1 kHz (n cycles), and how long the LED stays lit:')
for lvl in (19.0, 20.0, 22.0):
    for n in (1, 2, 5, 20):
        a = vrms(lvl) * math.sqrt(2); t1 = 1e-3 + n * 1e-3
        r = run(deck(f'BS presrc 0 V = {a} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < {t1})', 1.0))
        on = r.get('ledon'); off = r.get('ledoff')
        hold = f'{(off - on) * 1e3:6.0f} ms' if on and off else ('stays lit' if on else '   --')
        print(f'  {lvl:4.0f} dBu, {n:2d} cycle(s): PK {r["pkmax"]:5.2f} V, LED {"on" if on else "off"}, lit {hold}')
