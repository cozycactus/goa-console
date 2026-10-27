"""CS4b: the group and master boards' jack-link signals. Their receivers (master_lib.receiver: 1M, 220R, 100 pF into an
OPA1656 follower) and inserts (master_lib.insert: 75R send; 47 uF NP, 47K, 1K, 100 pF return) are the strip's circuits,
so sim/review/cs4/jack_protect.py covers them. New here: a DRV135 balanced output leg (master_lib.drv134). Its output
pin drives the jack through a 10 uF NP (25 V), and the jack-side node is also its Sense pin, inside its feedback
network. Modelled: the output pin as 20 ohm with its protection diodes to the rails; the Sense pin as 10 kohm into the
DRV135's internal network (an estimate: TI gives no value), with protection diodes; 20 nH of board track between the
link and the part. Same IEC 61000-4-2 gun, link and rails as jack_protect.py. A clamp is a BAV199 at the link end.
The master's main outputs add a G6K relay contact (a few nH) and the phones a 2R2 to the LME49600; neither changes the
picture. usage: python3 sim/review/cs4/jack_protect_mg.py"""
import os, sys, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jack_protect import MODELS, rails, gun, run

def drv_path(clamp):
    t = ['LCH ch 0 10n', 'LL j m 100n', 'RL m m2 0.2']
    t += ['LT m2 s 20n',                                    # track to the DRV135: Sense pin and the 10u coupler
          'VIS s s1 0', 'RS s1 sx 10k', 'DS1 sx vp DESD', 'DS2 vn sx DESD', 'RSX sx 0 1Meg',
          'C10U s o 10u', 'VIO o o1 0', 'RO o1 0 20', 'DO1 o1 vp DESD', 'DO2 vn o1 DESD']
    if clamp: t += ['VCL m2 cln 0', 'DC1 cln vp DBAV199', 'DC2 vn cln DBAV199']
    return '\n'.join(t)

def esd(clamp, kv):
    d = f"""* DRV135 leg ESD
{MODELS}
{rails()}
{gun('j', kv)}
{drv_path(clamp)}
.control
set noaskquit
tran 0.05n 400n 0 0.05n uic
let io = abs(i(VIO))
let isn = abs(i(VIS))
meas tran iopk max io
meas tran isnpk max isn
meas tran qo integ io from=0 to=400n
meas tran vs max v(s)
{'let icl = abs(i(VCL))' if clamp else ''}
{'meas tran clpk max icl' if clamp else ''}
{'let icl2 = icl*icl' if clamp else ''}
{'meas tran cli2t integ icl2 from=0 to=400n' if clamp else ''}
.endc
.end"""
    return run(d)

def phantom(clamp):
    c = f"""* phantom on a DRV135 leg
{MODELS}
VVP vp 0 DC 16.9
VVN vn 0 DC -16.9
VPH ph 0 DC 48
RPH ph s 6.8k
RS s sx 10k
RSX sx 0 1Meg
C10U s o 10u
RO o 0 20
{'DC1 s vp DBAV199' if clamp else ''}
{'DC2 vn s DBAV199' if clamp else ''}
.control
set noaskquit
op
print v(s) v(sx)
.endc
.end"""
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(c)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    v = dict(re.findall(r'(v\(\w+\))\s*=\s*([-+0-9.eE]+)', out))
    return float(v.get('v(s)', 'nan')), float(v.get('v(sx)', 'nan'))

if __name__ == '__main__':
    print('DRV135 output leg (group sub / aux out; master main, aux 5 / 6, C/Room), IEC 61000-4-2 contact on the tip:')
    for kv in (8.0, 4.0):
        for clamp in (False, True):
            r = esd(clamp, kv)
            extra = f'; clamp {r["clpk"]:5.1f} A, I2t {r["cli2t"]:.1e} A2s' if clamp else ''
            print(f'  {kv:3.0f} kV {"BAV199 at the link" if clamp else "as built":18s}: output pin {r["iopk"]:6.2f} A '
                  f'({r["qo"] * 1e6:5.3f} uC), Sense pin {r["isnpk"] * 1e3:6.1f} mA, node {r["vs"]:6.1f} V{extra}', flush=True)
    print('\nphantom 48 V / 6K8 on a leg (steady state): the 10 uF NP 25 V coupler sees the jack-side node')
    for clamp in (False, True):
        s, sx = phantom(clamp)
        print(f'  {"BAV199 at the link" if clamp else "as built":18s}: coupler {s:5.1f} V, Sense pin\'s internal node {sx:5.1f} V')
