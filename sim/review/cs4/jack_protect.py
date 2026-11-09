"""CS4 (docs/studies/console_survey.md §5): protecting the strip's jack-facing pins. Configurations against the strip as built:
  link clamps (PROPOSED): a BAV199 (low-leakage double diode: common pin 3 to the node, pin 2 to +VA, pin 1 to -VA) at
      the main-board end of the jack link (CN3), on IN_T, IN_R, RET_RAW, SEND and DO_T, ahead of every series part;
  pin clamps: the same BAV199 after the series part instead (IN_TB / IN_RB after the 220R, RET_IN after R99 1K); for
      the outputs (SEND, DO_T) the link end is the only place, so it is the same as above;
  TVS: a PESD24VL1BA (bidirectional, 24 V working, ~11 pF) from each jack-board signal to CHASSIS, beside the jacks.
1. ESD: IEC 61000-4-2 contact discharge, 8 kV (150 pF / 330 ohm gun, 0.15 uH: ~1 ns rise) on a jack's tip. The jack
   board's C8 / C9 (100 pF to CHASSIS on the input legs), the 10-way link (~136 mm: 100 nH, 0.2 ohm per conductor), the
   main board's series parts and the rails (220 uF + 100 nF with their ESL, 10R feed) are modelled. The IC pin is its
   internal protection diodes to the rails (lumped: IS 1e-14, RS 2 ohm); an op-amp output is also its output stage
   (20 ohm to ground at these speeds). Reported: the peak current and the charge into the IC's own diodes, against an
   HBM 2 kV pin rating (1.33 A peak, ~0.2 uC).
2. Phantom: 48 V through 6K8 on SEND and on DO_T, steady state: what C51 (behind the insert send) and C52 (the direct
   out's coupler), both 33 uF 25 V, see, and the current into the rails.
3. Normal operation: THD at U16's input (IN_TB) for a 1 kohm source at +20 dBu, 1 kHz and 20 kHz, with the parts'
   nonlinear capacitance; and DC offset on the 1 Mohm legs from their datasheet leakage.
Device models are approximations from the datasheets; the comparison between configurations is the point.
usage: python3 sim/review/cs4/jack_protect.py"""
import os, re, math, subprocess, tempfile

MODELS = """.model DESD D(IS=1e-14 N=1.0 RS=2 CJO=2p)
.model DBAV199 D(IS=2e-13 N=1.3 RS=0.8 CJO=2p M=0.4 TT=3u)
.model DTVS D(IS=1e-15 N=1.0 RS=4 CJO=22p M=0.33 VJ=0.7 BV=26.7 IBV=1m)"""
CONFIGS = [('as built', None, False), ('link clamps (proposed)', 'link', False), ('pin clamps', 'pin', False),
           ('TVS at the jacks', None, True)]

def rails():
    return """VVP vp 0 DC 16.9
VVN vn 0 DC -16.9
LP1 vp vp1 5n
CP1 vp1 0 220u
LP2 vp vp2 1n
CP2 vp2 0 100n
LN1 vn vn1 5n
CN1 vn1 0 220u
LN2 vn vn2 1n
CN2 vn2 0 100n"""

def gun(node, kv=8.0):
    return f"""CG g 0 150p IC={kv * 1000}
RG g g2 330
LG g2 g3 0.15u
SG g3 {node} ctl 0 SWG
.model SWG SW(VT=0.5 VH=0.01 RON=0.1 ROFF=1e12)
VCTL ctl 0 PWL(0 0 1n 0 1.01n 1)"""

def path(pin, clamp, tvs):
    """The jack-board node J (tip), the link to the main board, and the main-board parts up to the IC pin P."""
    t = [f'DT1 j tx DTVS', f'DT2 ch tx DTVS'] if tvs else []
    common = ['LCH ch 0 10n', 'LL j m 100n', 'RL m m2 0.2'] + t
    if pin in ('IN_T', 'IN_R'):
        p = ['C8 j ch 100p', 'R10 m2 0 1Meg', 'R110 m2 p 220', 'C94 p 0 100p']
        clampnode, kind = ('p' if clamp == 'pin' else 'm2'), 'input'
    elif pin == 'RET_RAW':
        p = ['C10 m2 r 33u', 'R12 r 0 47k', 'R99 r p 1k', 'C84 p 0 100p']
        clampnode, kind = ('p' if clamp == 'pin' else 'm2'), 'input'
    elif pin == 'SEND':
        p = ['R11 m2 p 75']
        clampnode, kind = 'm2', 'output'
    else:                                        # DO_T: C52 then R71 75R to U8A's output
        p = ['R72 m2 0 47k', 'C52 m2 d1 33u', 'R71 d1 p 75']
        clampnode, kind = 'm2', 'output'
    ic = ['VIP p pi 0', 'DI1 pi vp DESD', 'DI2 vn pi DESD']
    if kind == 'output': ic += ['RO pi 0 20']
    cl = [f'VCL {clampnode} cln 0', f'DC1 cln vp DBAV199', f'DC2 vn cln DBAV199'] if clamp else []
    return '\n'.join(common + p + ic + cl)

def run(deck):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(deck)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    return {k.lower(): float(x) for k, x in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', out, re.M)}

def esd(pin, clamp, tvs, kv=8.0):
    d = f"""* ESD {pin}
{MODELS}
{rails()}
{gun('j', kv)}
{path(pin, clamp, tvs)}
.control
set noaskquit
tran 0.05n 400n 0 0.05n uic
let idi = i(VIP)
let iabs = abs(idi)
meas tran ipk max iabs
meas tran q integ iabs from=0 to=400n
meas tran vpk max v(p)
{'let icl = abs(i(VCL))' if clamp else ''}
{'meas tran clpk max icl' if clamp else ''}
{'let icl2 = icl*icl' if clamp else ''}
{'meas tran cli2t integ icl2 from=0 to=400n' if clamp else ''}
.endc
.end"""
    return run(d)

def phantom(pin, clamp):
    if pin == 'SEND':                             # 48 V / 6K8 -> SEND -> R11 -> EQOUT (C51 33u to EQSEL, R68 47K)
        c = 'RPH ph j 6.8k\nVPH ph 0 DC 48\nRJ j m2 0.2\nR11 m2 eqo 75\nR68 eqo 0 47k\nVOP eqo2 0 0\nC51 eqo eqo2 33u'
        clampnode, meas_node = 'm2', 'eqo'
    else:                                          # DO_T (R72 47K), C52 to DO1, R71 75R to U8A's output (0 V)
        c = 'RPH ph j 6.8k\nVPH ph 0 DC 48\nRJ j m2 0.2\nR72 m2 0 47k\nC52 m2 d1 33u\nR71 d1 0 75'
        clampnode, meas_node = 'm2', 'm2'
    cl = f'DC1 {clampnode} vp DBAV199\nDC2 vn {clampnode} DBAV199\nVVP vp 0 DC 16.9\nVVN vn 0 DC -16.9' if clamp else ''
    d = f"""* phantom {pin}
{MODELS}
{c}
{cl}
.control
set noaskquit
op
print v({meas_node})
.endc
.end"""
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    m = re.search(r'v\(\w+\)\s*=\s*([-+0-9.eE]+)', out)
    return float(m.group(1)) if m else None

def thd(f, clamp, tvs, lvl=20.0):
    a = 0.7746 * 10 ** (lvl / 20) * math.sqrt(2)
    t = 'DT1 j tx DTVS\nDT2 0 tx DTVS' if tvs else ''
    n = 'p' if clamp == 'pin' else 'j'
    cl = f'DC1 {n} vp DBAV199\nDC2 vn {n} DBAV199' if clamp else ''
    d = f"""* thd
{MODELS}
VVP vp 0 DC 16.9
VVN vn 0 DC -16.9
VS s 0 SIN(0 {a} {f})
RS s j 1k
C8 j 0 100p
{t}
R10 j 0 1Meg
R110 j p 220
C94 p 0 100p
CIN p 0 9p
{cl}
.options reltol=1e-8 abstol=1e-14 vntol=1e-9 method=gear
.control
set noaskquit
tran {1 / f / 2000} {8 / f} {2 / f} {1 / f / 2000}
fourier {f} v(p)
.endc
.end"""
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as fh: fh.write(d)
    out = subprocess.run(['ngspice', '-b', fh.name], capture_output=True, text=True).stdout
    os.unlink(fh.name)
    m = re.search(r'THD:\s*([0-9.eE+-]+)\s*%', out)
    return float(m.group(1)) if m else None

if __name__ == '__main__':
    print('1. IEC 61000-4-2 contact discharge on the tip: current and charge into the IC pin\'s own diodes (an HBM 2 kV')
    print('   pin rating, as TI rates its OPA165x / OPA166x audio op-amps, is about 1.33 A peak / 0.2 uC). 8 kV: IEC level 4;')
    print('   4 kV: the contact level EN 55103-2 asks of professional audio (on accessible metal, not usually connector pins)')
    for kv in (8.0, 4.0):
        for pin in ('IN_T', 'RET_RAW', 'SEND', 'DO_T'):
            for name, cl, tv in CONFIGS:
                r = esd(pin, cl, tv, kv)
                extra = f'; clamp {r["clpk"]:5.1f} A, I2t {r["cli2t"]:.1e} A2s' if cl else ''
                print(f'   {kv:3.0f} kV {pin:8s} {name:23s} IC {r.get("ipk", 0):6.3f} A, {r.get("q", 0) * 1e6:6.4f} uC, '
                      f'pin {r.get("vpk", 0):5.1f} V{extra}', flush=True)
    print('\n2. phantom 48 V / 6K8 on an output, steady state (C51 / C52 are 33 uF 25 V)')
    for pin in ('SEND', 'DO_T'):
        for cl in (None, 'link'):
            v = phantom(pin, cl)
            what = 'C51 (EQOUT)' if pin == 'SEND' else 'C52 (DO_T)'
            print(f'   {pin:5s} {"rail clamp" if cl else "as built":10s}: {what} at {v:5.1f} V', flush=True)
    print('\n3. THD at U16\'s input, 1 kohm source (C8 100p, 220R, C94 100p, the op-amp\'s 9 pF); the solver\'s floor is about')
    print('   2e-5 % (-134 dB): the as-built rows show it')
    for f in (1000, 20000):
        for lvl in (20.0, 0.0):
            for name, cl, tv in CONFIGS:
                t = thd(f, cl, tv, lvl)
                print(f'   {f:5d} Hz {lvl:+3.0f} dBu {name:22s}: THD {t:.1e} % ({20 * math.log10(t / 100):6.1f} dB)' if t
                      else f'   {f} Hz {lvl} dBu {name}: n/a', flush=True)
    print('\n   DC offset on a 1 Mohm leg from the BAV199\'s leakage: 3 pA typ -> 3 uV; 5 nA max (at 75 V, far above the')
    print('   ~17 V it sees) -> 5 mV. BAV199 surge: 4 A for 1 us, i.e. an I2t of about 1.6e-5 A2s, against the clamp rows above')
