"""Strip ON / soft mute (spec 9) in time: PRE -> R16 4K7 -> M1 (Q1 J112 to AGND) -> R17 4K7 -> M2 (Q2, C81 10p) ->
U3B follower; the gates MGATE = SW4's MSW (-VL when ON, LGND when muted) through R42 220K, C28 100n to AGND.
Values from channel_strip.net. J112 corners from the datasheet: VGS(off) -1 / -2.5 / -5 V, rds(on) <= 50 ohm,
Cgs = Cgd 5 pF (typical) or 14 pF. usage: python3 sim/review/gaps/mute.py
Reports: the mute and unmute ramps (time from the key to -3 dB / -60 dB / full and back), the attenuation, and the
click with no programme (gate charge through Cgd into the 4K7 nodes), at MUTEOUT."""
import os, re, sys, math, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ol import v, VL, run, dbu

def jfet(vto, cgs):
    beta = 1 / (2 * 50 * abs(vto))                       # rds(on) = 1 / (2 beta |VTO|) = 50 ohm, the datasheet maximum
    return f'.model J112 NJF(VTO={vto} BETA={beta} LAMBDA=0.01 CGS={cgs} CGD={cgs} IS=1e-14)'

def deck(model, src, gate, tstop):
    return f"""* strip soft mute
{model}
{src}
R16 pre m1 {v('R16')}
J1 m1 mg 0 J112
R17 m1 m2 {v('R17')}
J2 m2 mg 0 J112
C81 m2 0 {v('C81')}
EU3 out 0 m2 0 1
{gate}
R42 msw mg {v('R42')}
C28 mg 0 {v('C28')}
.control
set noaskquit
tran 10u {tstop} 0 10u
meas tran vout_max max v(out)
meas tran vout_min min v(out)
.endc
.end"""

def ramp(vto, cgs, f=1000):
    """0 dBu at PRE; SW4 opens (mute) at 50 ms, closes (unmute) at 300 ms. Envelope in 1 ms windows."""
    a = 0.7746 * math.sqrt(2)
    d = deck(jfet(vto, cgs), f'VS pre 0 SIN(0 {a} {f})', f'VG msw 0 PWL(0 {-VL} 50m {-VL} 50.01m 0 300m 0 300.01m {-VL})', 0.6)
    d = d.replace('meas tran vout_max max v(out)', 'wrdata /tmp/mute_env.txt v(out)')
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as fh: fh.write(d)
    subprocess.run(['ngspice', '-b', fh.name], capture_output=True, text=True); os.unlink(fh.name)
    rows = [tuple(map(float, l.split()[:2])) for l in open('/tmp/mute_env.txt') if l.strip() and l.split()[0][0] in '0123456789']
    win = {}
    for t, y in rows: win.setdefault(int(t * 1000), []).append(abs(y))
    env = {k: 20 * math.log10(max(max(w), 1e-9) / a) for k, w in sorted(win.items())}
    def when(start, cond):
        return next((k - start for k in sorted(env) if k >= start and cond(env[k])), None)
    return dict(mute_3=when(50, lambda e: e < -3), mute_60=when(50, lambda e: e < -60),
                floor=min(env[k] for k in env if 200 <= k < 300), unmute_3=when(300, lambda e: e > -3),
                unmute_0=when(300, lambda e: e > -0.2))

def click(vto, cgs):
    """No programme: the step at MUTEOUT when SW4 opens and closes (gate charge through Cgd into M1 / M2)."""
    d = deck(jfet(vto, cgs), 'VS pre 0 DC 0', f'VG msw 0 PWL(0 {-VL} 50m {-VL} 50.01m 0 300m 0 300.01m {-VL})', 0.6)
    r = run(d)
    return max(abs(r.get('vout_max', 0)), abs(r.get('vout_min', 0)))

print(f'values: R16 / R17 {VAL_R if (VAL_R := v("R16")) else 0:.0f} ohm, R42 {v("R42") / 1e3:.0f}K, C28 {v("C28") * 1e9:.0f}n (tau {v("R42") * v("C28") * 1e3:.0f} ms)')
print('VGS(off)  Cgs/Cgd | mute: -3 dB  -60 dB  floor | unmute: -3 dB  full | click, no programme')
for vto in (-1.0, -2.5, -5.0):
    for cgs in (5e-12, 14e-12):
        r = ramp(vto, cgs); c = click(vto, cgs)
        print(f'  {vto:5.1f} V  {cgs * 1e12:4.0f} pF | {r["mute_3"]!s:>5} ms {r["mute_60"]!s:>5} ms {r["floor"]:6.1f} dB | '
              f'{r["unmute_3"]!s:>5} ms {r["unmute_0"]!s:>5} ms | {c * 1e6:6.1f} uV ({dbu(max(c, 1e-12) / math.sqrt(2)):6.1f} dBu peak-equiv)')
