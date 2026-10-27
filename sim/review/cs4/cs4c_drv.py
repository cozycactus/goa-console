"""CS4c: a resistor RX inside each DRV135 Sense loop, between the output pin (VO) and its 10 uF NP; the Sense pin stays
on the jack side of the 10 uF, where the BAV199 link clamp (CS4b) sits. What it buys and what it costs, on TI's DRV134
model (SBOM004A; the DRV135 is the same die in SO-8), for RX = 0 (as built), 10, 22, 33 ohm:
  stability  the only loop through an output pin is the cross-coupled one (VO+ -> 10u -> Sense+ -> the other side's
             amp -> VO- -> 10u -> Sense- -> back), a positive-feedback loop just below unity in the audio band (|T|
             ~0.96: that is how the DRV floats its outputs). A Tian probe breaks it at VO+. |1 + T| (the distance to
             the critical point) is small in the audio band by design and grows with frequency; a resonance would be
             a dip in it above 20 kHz: reported the deepest dip (or none), |T| at 1 kHz and |1 + T| at 20 kHz;
  response   differential gain at 1 kHz, peaking, -3 dB, 1 V step overshoot;
  impedance  differential output impedance at 1 kHz / 20 kHz (TI's own 50 ohm per leg shows as ~53 ohm: the loop
             floats the outputs, it does not null their resistance);
  headroom   the largest 1 kHz sine at the jack before 0.1 % THD into 600 ohm per leg, and with one leg shorted (TS plug);
  ESD        an 8 kV IEC 61000-4-2 contact on a leg with the BAV199 at the link: current into the output pin.
Loads per leg after the relay contact and the link: 10K // 1 nF (default), 600R, 600R + 47 nF, 10K + 47 nF, and the
TS case (one leg shorted at the jack). usage: TI_MODELS=<folder> python3 sim/review/cs4/cs4c_drv.py [quick]"""
import os, sys, re, subprocess, tempfile, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.environ.get('TI_MODELS', '')
sys.path.insert(0, HERE)
from jack_protect import MODELS, rails, gun, run

RXS = (0, 10, 22, 33)
LOADS = [('10K // 1n', 10e3, 1e-9, False), ('600R', 600, 1e-12, False), ('600R + 47n', 600, 47e-9, False),
         ('10K + 47n', 10e3, 47e-9, False), ('TS: N leg shorted', 10e3, 1e-9, True)]

def ng(deck):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False, dir=HERE, prefix='cs4c_') as f: f.write(deck)
    p = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True, cwd=HERE, timeout=900)
    os.unlink(f.name)
    return p.stdout + p.stderr

def circuit(rx, rl, cl, ts, probe=True, src='DC 0 AC 0', lt=0.0):
    """DRV134 driven from a 47R build-out; per leg: VO -> RX -> 10u -> Sense node S -> relay (50 mR, 10 nH) -> link
    (100 nH, 0.2R) -> jack J -> load. The Tian probe (VTI in series, ITI into the op side) sits at VO+. lt: the board
    trace inside the loop where the 10u sits away from the DRV135 (H): lt in the VO run and lt in the Sense run back."""
    r = max(rx, 1e-3)
    L = [f'.include {M}/DRV134.LIB', 'VP vp 0 16.9', 'VM vm 0 -16.9', f'VIN in 0 {src}', 'RS in vin 47',
         'X1 von snk 0 vin vm vp spk vopx DRV134']
    L += ([ 'VTI vopx vop DC 0 AC 0', 'ITI 0 vopx DC 0 AC 0'] if probe else ['VTI vopx vop DC 0'])
    for leg, vo, s in (('p', 'vop', 'sp'), ('n', 'von', 'sn')):
        L += [f'LV{leg} {vo} {vo}t {max(lt, 1e-12)}', f'LS{leg} {s} {s[0]}{s[1]}k {max(lt, 1e-12)}',
              f'RX{leg} {vo}t {vo}r {r}', f'C{leg} {vo}r {s} 10u', f'RK{leg} {s} k{leg} 0.05', f'LK{leg} k{leg} m{leg} 10n',
              f'LL{leg} m{leg} l{leg} 100n', f'RL{leg} l{leg} j{leg} 0.2']
        if ts and leg == 'n': L.append(f'RSH{leg} j{leg} 0 0.05')
        else: L += [f'RLD{leg} j{leg} 0 {rl}', f'CLD{leg} j{leg} 0 {cl}']
    return '\n'.join(L)

def num(out, key):
    m = re.search(rf'^{key}\s*=\s*([-+0-9.eE]+)', out, re.M)
    return float(m.group(1)) if m else float('nan')

def stability(rx, rl, cl, ts, lt=0.0):
    raw = os.path.join(HERE, 'raw'); os.makedirs(raw, exist_ok=True); fv, fi = f'{raw}/cs4c_v.txt', f'{raw}/cs4c_i.txt'
    d = f"""* cs4c loop
{circuit(rx, rl, cl, ts, lt=lt)}
.control
set wr_singlescale
alter @VTI[acmag] = 1
ac dec 50 100 300meg
wrdata {fv} v(vopx) v(vop)
alter @VTI[acmag] = 0
destroy all
alter @ITI[acmag] = 1
ac dec 50 100 300meg
wrdata {fi} i(VTI)
.endc
.end"""
    ng(d)
    dv = np.loadtxt(fv); di = np.loadtxt(fi)
    f = dv[:, 0]; vx = dv[:, 1] + 1j * dv[:, 2]; vy = dv[:, 3] + 1j * dv[:, 4]; ii = di[:, 1] + 1j * di[:, 2]
    Tv, Ti = -vx / vy, (1 - ii) / ii
    T = (Tv * Ti - 1) / (Tv + Ti + 2)
    # in and above the audio band |1 + T| is small by design (|T| ~0.96, positive feedback just under unity) and rises
    # with frequency; a resonance would show as a dip in it: the deepest one above 20 kHz, else 'none'
    hf = np.where(f >= 20e3)[0]; a = abs(1 + T)
    dips = [k for k in hf[1:-1] if a[k] < a[k - 1] and a[k] <= a[k + 1]]
    k = min(dips, key=lambda k: a[k]) if dips else None
    return (float(a[k]) if k else None), (float(f[k]) if k else None), float(abs(T[np.argmin(abs(f - 1e3))])), \
        float(a[np.argmin(abs(f - 20e3))])

def response(rx, rl, cl, ts, lt=0.0):
    d = f"""* cs4c response
{circuit(rx, rl, cl, ts, probe=False, src='DC 0 AC 1 PULSE(0 1 2u 10n 10n 40u 80u)', lt=lt)}
.control
ac dec 50 10 100meg
let hd = {'v(jp)' if ts else 'v(jp)-v(jn)'}
let g = db(hd)
meas ac g1k find g at=1k
meas ac gpk max g from=20k to=100meg
meas ac g20k find g at=20k
tran 2n 30u 0 2n
let vd = {'v(jp)' if ts else 'v(jp)-v(jn)'}
meas tran vfin avg vd from=20u to=30u
meas tran vmax max vd from=2u to=20u
.endc
.end"""
    o = ng(d)
    g1k, gpk, g20k, vfin, vmax = (num(o, k) for k in ('g1k', 'gpk', 'g20k', 'vfin', 'vmax'))
    return g1k, gpk - g1k, g20k - g1k, (vmax - vfin) / vfin * 100 if vfin else float('nan')

def zout(rx):
    """Differential output impedance at the Sense nodes: input grounded, 1 A AC across S+ / S-."""
    d = f"""* cs4c zout
{circuit(rx, 1e9, 1e-15, False, probe=False)}
IZ sn sp DC 0 AC 1
.control
ac dec 20 100 100k
let z = mag(v(sp)-v(sn))
meas ac z1k find z at=1k
meas ac z20k find z at=20k
.endc
.end"""
    o = ng(d)
    return num(o, 'z1k'), num(o, 'z20k')

def thd(rx, rl, ts, vpk):
    d = f"""* cs4c thd
{circuit(rx, rl, 1e-12, ts, probe=False, src=f'SIN(0 {vpk} 1k)')}
.options reltol=1e-5
.control
tran 2u 6m 2m 2u
fourier 1k {'v(jp)' if ts else 'v(jp)-v(jn)'}
.endc
.end"""
    o = ng(d)
    m = re.search(r'THD:\s*([0-9.eE+-]+)\s*%', o)
    a = re.search(r'^\s*1\s+1000\s+([0-9.eE+-]+)', o, re.M)
    return (float(m.group(1)) if m else float('nan')), (float(a.group(1)) if a else float('nan'))

def clip(rx, rl, ts):
    """Largest input (peak) that keeps THD under 0.1 %; returns the jack-side output in dBu (differential, or the
    remaining leg for TS)."""
    lo, hi, best = 1.0, 14.0, None
    for _ in range(9):
        mid = (lo + hi) / 2; t, a = thd(rx, rl, ts, mid)
        if t < 0.1: lo, best = mid, a
        else: hi = mid
    return 20 * np.log10(best / np.sqrt(2) / 0.7746) if best else float('nan')

def esd(rx, kv=8.0):
    t = ['LCH ch 0 10n', 'LL j m 100n', 'RL m m2 0.2', 'LT m2 s 20n', 'VIS s s1 0', 'RS s1 sx 10k', 'DS1 sx vp DESD',
         'DS2 vn sx DESD', 'RSX sx 0 1Meg', 'C10U s o 10u', f'RXX o o0 {max(rx, 1e-3)}', 'VIO o0 o1 0', 'RO o1 0 20',
         'DO1 o1 vp DESD', 'DO2 vn o1 DESD', 'VCL m2 cln 0', 'DC1 cln vp DBAV199', 'DC2 vn cln DBAV199']
    d = f"""* cs4c esd
{MODELS}
{rails()}
{gun('j', kv)}
{chr(10).join(t)}
.control
set noaskquit
tran 0.05n 400n 0 0.05n uic
let io = abs(i(VIO))
meas tran iopk max io
meas tran qo integ io from=0 to=400n
.endc
.end"""
    r = run(d)
    return r['iopk'], r['qo']

if __name__ == '__main__':
    if not M or not os.path.exists(f'{M}/DRV134.LIB'): sys.exit('set TI_MODELS to the folder with DRV134.LIB')
    quick = 'quick' in sys.argv
    print('1. the cross-coupled loop (Tian probe at VO+): |T| at 1 kHz, |1 + T| at 20 kHz, and the deepest dip of '
          '|1 + T| above 20 kHz (a resonance; 0 = oscillating)')
    for name, rl, cl, ts in LOADS:
        for rx in RXS:
            m, fm, t1, a20 = stability(rx, rl, cl, ts)
            dip = f'dip {m:5.3f} at {fm / 1e6:7.3f} MHz' if m is not None else 'no dip up to 300 MHz'
            print(f'   {name:18s} RX {rx:2d}R: |T| 1 kHz {t1:5.3f}, |1+T| 20 kHz {a20:5.3f}, {dip}', flush=True)
    print('\n2. response at the jack: gain at 1 kHz, peaking above 20 kHz, 20 kHz, 1 V step overshoot')
    for name, rl, cl, ts in LOADS:
        for rx in RXS:
            g, pk, g20, os_ = response(rx, rl, cl, ts)
            print(f'   {name:18s} RX {rx:2d}R: {g:+6.2f} dB, peak {pk:+5.2f} dB, 20 kHz {g20:+6.3f} dB, '
                  f'overshoot {os_:5.1f} %', flush=True)
    print('\n3. differential output impedance at the Sense nodes')
    for rx in RXS:
        z1, z20 = zout(rx)
        print(f'   RX {rx:2d}R: {z1:6.2f} ohm at 1 kHz, {z20:6.2f} ohm at 20 kHz', flush=True)
    if not quick:
        print('\n4. headroom: largest 1 kHz output at the jack under 0.1 % THD')
        for name, rl, ts in (('600R per leg', 600, False), ('10K per leg', 10e3, False), ('TS, 10K on the tip', 10e3, True)):
            for rx in RXS:
                print(f'   {name:18s} RX {rx:2d}R: {clip(rx, rl, ts):+5.1f} dBu', flush=True)
    print('\n5. 8 kV contact on a leg, BAV199 at the link: current and charge into the output pin')
    for rx in RXS:
        i, q = esd(rx)
        print(f'   RX {rx:2d}R: {i:5.2f} A, {q * 1e6:6.3f} uC', flush=True)
    print('   (an HBM 2 kV pin rating is about 1.33 A / 0.2 uC)')
    print('\n6. the 10u away from the DRV135 (group U7 as placed: ~115 mm each way, ~120 nH in the VO run and in the Sense'
          ' run; U4 / master U9: 15-30 mm, ~30 nH)')
    for lt in (30e-9, 120e-9, 240e-9):
        for name, rl, cl, ts in (LOADS[0], LOADS[2]):
            for rx in (0, 22):
                m, fm, t1, a20 = stability(rx, rl, cl, ts, lt)
                g, pk, g20, os_ = response(rx, rl, cl, ts, lt)
                dip = f'dip {m:5.3f} at {fm / 1e6:6.2f} MHz' if m is not None else 'no dip'
                print(f'   {lt * 1e9:3.0f} nH {name:12s} RX {rx:2d}R: {dip}, peak {pk:+5.2f} dB, overshoot {os_:5.1f} %', flush=True)
