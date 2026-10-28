"""Strip overload / signal LED (U4, U17, spec 8.1), as built since MET1 (feature_gaps.md, 2026-10-26).
Red (overload, K3): PRESRC (BUF1) -> R39 1K -> D1 -> PK (C12 100n // R14 470K) -> U4A - input against VREF = +VL / 2
(R40 / R41); U4A discharges OL_HOLD (R115 to +VL, C97 to GNDD); U4B pulls Q3's base (R116 / R117) while OL_HOLD is below
VREF, and Q3 feeds the red anode through R15.
Green (signal, MET1): PRESRC -> R118 47K -> SIG_IN (BAT54W clamp to GNDD) -> U17A - input against VTH = VREF / 76;
U17A discharges SIG_HOLD (R121 / C99); U17B pulls Q4's base (R122 / R123) while SIG_HOLD is below VREF, Q4 feeds the green
anode through R124. Q5 (base from U4B's output through R125) holds Q4's base at +VL while the red is lit.
Since 2026-10-27: P1, U4A / U17A discharge their holds through R126 / R127 1K (the output current peak is measured);
P2, C100 100n on VREF; E6, C101 / C102 10n base to emitter on Q3 / Q4 (the LED current's 10-90 % rise is measured).
Part values are read from channel_strip.net; the WIRING is this file's (one PRESRC tap through a 1N4148 as the
detector was before CS1), so this is a values check of the hold / drive / green stages, not a check of the schematic's
netlist. The five CS1 taps and the detector's wiring are checked from the netlist by sim/review/cs1/ol_multi.py
(project_review.md RV11.8).
usage: python3 sim/review/gaps/ol.py
Models: 1N4148, BAT54 and a generic 2N3906 (standard), GaAsP red ~1.9 V and GaP green ~2.0 V at 3 mA, LM393
halves as sink switches (60 ohm, ideal speed; the real 1.3 us is far below the 0.1 ms attack). The source is ideal:
PRESRC is an op-amp output. Time step 2 us: at 20 us the ideal switches showed a false 26 us blink where the hold node
crosses VREF (gone at 1 and 0.2 us)."""
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
    return f"""* strip overload / signal LED (as built)
.model D1N4148 D(IS=2.52n RS=0.568 N=1.752 CJO=4p M=0.4 TT=20n BV=100)
.model DBAT54 D(IS=0.1u RS=0.9 N=1.0 CJO=10p BV=30)
.model LEDR D(IS=1e-20 N=1.8 RS=5)
.model LEDG D(IS=4e-21 N=1.85 RS=8)
.model Q3906 PNP(IS=1.41f XTI=3 EG=1.11 VAF=18.7 BF=180.7 NE=1.5 ISE=0 IKF=80m XTB=1.5 BR=4.977 NC=2 ISC=0 IKR=0 RC=2.5 CJC=9.728p MJC=.5776 VJC=.75 FC=.5 CJE=8.063p MJE=.3677 VJE=.75 TR=33.42n TF=179.3p ITF=.4 VTF=4 XTF=6)
.model SW393 SW(VT=0 VH=0.001 RON=60 ROFF=1e9)
VVL vl 0 DC {VL}
{src}
R39 presrc pka {v('R39')}
D1 pka pk D1N4148
C12 pk 0 {v('C12')}
R14 pk 0 {v('R14')}
R40 vl vref {v('R40')}
R41 vref 0 {v('R41')}
C100 vref 0 {v('C100')}
S4A dis 0 pk vref SW393
R126 dis disi {v('R126')}
VI4 hold disi 0
R115 vl hold {v('R115')}
C97 hold 0 {v('C97')}
S4B olk 0 vref hold SW393
R116 olk olb {v('R116')}
R117 vl olb {v('R117')}
Q3 olc olb vl Q3906
C101 olb vl {v('C101')}
R15 olc ola {v('R15')}
VLEDR ola ola2 0
D2R ola2 0 LEDR
R118 presrc sigin {v('R118')}
D11 0 sigin DBAT54
R119 vref vth {v('R119')}
R120 vth 0 {v('R120')}
S17A sdis 0 sigin vth SW393
R127 sdis sdisi {v('R127')}
VI17 shold sdisi 0
R121 vl shold {v('R121')}
C99 shold 0 {v('C99')}
S17B sigk 0 vref shold SW393
R122 sigk sigb {v('R122')}
R123 vl sigb {v('R123')}
Q4 sigc sigb vl Q3906
C102 sigb vl {v('C102')}
R124 sigc siga {v('R124')}
R125 olk gateb {v('R125')}
Q5 sigb gateb vl Q3906
VLEDG siga siga2 0
D2G siga2 0 LEDG
.ic v(hold)={VL} v(shold)={VL} v(vref)={VL / 2}
{extra}
.control
set noaskquit
tran 2u {tstop} 0 2u
meas tran pkmax max v(pk)
meas tran redon when i(VLEDR)=1m rise=1
meas tran redoff when i(VLEDR)=1m fall=1
meas tran grnon when i(VLEDG)=1m rise=1
meas tran grnoff when i(VLEDG)=1m fall=1
meas tran rmax max i(VLEDR)
meas tran gmax max i(VLEDG)
meas tran gend find i(VLEDG) at={tstop}
meas tran rend find i(VLEDR) at={tstop}
meas tran vin_min min v(sigin)
meas tran i4max max i(VI4)
meas tran i17max max i(VI17)
meas tran r10 when i(VLEDR)=0.3m rise=1
meas tran r90 when i(VLEDR)=2.7m rise=1
.endc
.end"""

def run(d):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    return {k.lower(): float(x) for k, x in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', out, re.M)}

dbu = lambda vrms: 20 * math.log10(vrms / 0.7746)
vrms = lambda d: 0.7746 * 10 ** (d / 20)
sine = lambda level, f: f'VS presrc 0 SIN(0 {vrms(level) * math.sqrt(2)} {f})'

def lit(level, f, colour, tstop=0.3):
    return f'{colour}on' in run(deck(sine(level, f), tstop))

def threshold(f, colour, lo, hi):
    for _ in range(14):
        mid = (lo + hi) / 2
        if lit(mid, f, colour): hi = mid
        else: lo = mid
    return hi

if __name__ == '__main__':
    print(f'values: R39 {VAL["R39"]}, C12 {VAL["C12"]}, R14 {VAL["R14"]}, VREF {VL / 2:.2f} V (R40 / R41 {VAL["R40"]} / {VAL["R41"]}), '
          f'hold R115 {VAL["R115"]} / C97 {VAL["C97"]}, R15 {VAL["R15"]}; signal R118 {VAL["R118"]}, VTH {VL / 2 * v("R120") / (v("R119") + v("R120")) * 1e3:.0f} mV, '
          f'hold R121 {VAL["R121"]} / C99 {VAL["C99"]}, R124 {VAL["R124"]}')
    print('steady sine: red (overload) / green (signal) light from')
    for f in (50, 1000, 10000):
        print(f'  {f:6d} Hz: red {threshold(f, "red", 10.0, 24.0):5.1f} dBu, green {threshold(f, "grn", -40.0, 0.0):6.1f} dBu')
    print('bursts at 1 kHz (n cycles), and how long the red LED stays lit:')
    for lvl in (19.0, 20.0, 22.0):
        for n in (1, 2, 5, 20):
            a = vrms(lvl) * math.sqrt(2); t1 = 1e-3 + n * 1e-3          # n whole cycles of 1 kHz from 1 ms
            r = run(deck(f'BS presrc 0 V = {a} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < {t1})', 1.0))
            on = r.get('redon'); off = r.get('redoff')
            hold = f'{(off - on) * 1e3:6.0f} ms' if on and off else ('stays lit' if on else '   --')
            print(f'  {lvl:4.0f} dBu, {n:2d} cycle(s): PK {r["pkmax"]:5.2f} V, red {"on" if on else "off"}, lit {hold}')
    print('green hold after a 20 ms burst at 1 kHz:')
    for lvl in (-15.0, 0.0):
        a = vrms(lvl) * math.sqrt(2)
        r = run(deck(f'BS presrc 0 V = {a} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < 21m)', 1.0))
        on = r.get('grnon'); off = r.get('grnoff')
        print(f'  {lvl:5.0f} dBu: green lit {(off - on) * 1e3:4.0f} ms' if on and off else f'  {lvl:5.0f} dBu: green {"stays lit" if on else "off"}')
    r = run(deck(sine(0, 1000), 0.3))
    print(f'0 dBu, 1 kHz: green {r["gend"] * 1e3:.2f} mA, red {r["rend"] * 1e3:.3f} mA; SIG_IN min {r["vin_min"]:.2f} V')
    r = run(deck(sine(22, 1000), 0.3))
    print(f'+22 dBu, 1 kHz (overload): red {r["rend"] * 1e3:.2f} mA, green {r["gend"] * 1e6:.1f} uA (gated off); SIG_IN min {r["vin_min"]:.2f} V')
    r = run(deck('VS presrc 0 DC 0', 0.3))
    print(f'silence: red {r["rend"] * 1e6:.2f} uA, green {r["gend"] * 1e6:.2f} uA')
    r = run(deck(sine(22, 1000), 0.3))
    print(f'P1: discharge current peak, U4A {r["i4max"] * 1e3:.1f} mA (+22 dBu), ', end='')
    r2 = run(deck(sine(0, 1000), 0.3)); print(f'U17A {r2["i17max"] * 1e3:.1f} mA (0 dBu); LM393B output rating 25 mA')
    if r.get('r10') and r.get('r90'): print(f'E6: red LED current 10-90 % rise {(r["r90"] - r["r10"]) * 1e6:.1f} us')
    a0 = vrms(0.0) * math.sqrt(2); hi = VL
    d = deck(f'BS presrc 0 V = {a0} * sin(6.283185307e3 * (time - 1m)) * (time > 1m) * (time < 21m)', 0.5)
    lo = run(d.replace('.endc', 'meas tran bmin min v(sigb)\n.endc'))['bmin']; s_ = hi - lo
    r = run(d.replace('.endc', f'meas tran b90 when v(sigb)={lo + 0.9 * s_} fall=1\nmeas tran b10 when v(sigb)={lo + 0.1 * s_} fall=1\n'
                               f'meas tran c10 when v(sigb)={lo + 0.1 * s_} rise=1\nmeas tran c90 when v(sigb)={lo + 0.9 * s_} rise=1\n.endc'))
    print(f'E6: SIG_B (the 258 mm line to Q4) swings {s_:.2f} V; edges {(r["b10"] - r["b90"]) * 1e6:.1f} us falling, '
          f'{(r["c90"] - r["c10"]) * 1e3:.2f} ms rising (0.8 / 2.0 us without C102)')
