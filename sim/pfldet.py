"""PFL detect as generated (tools/gen_master.py, master spec section 19, master_parts_review.md items 4 and 6).
PFLDET carries T = 38 PFL/AFL keys (24 strips, 12 group keys, 2 on the master). Each key: +VL -> pole B -> ON node ->
100K -> PFLDET, and ON -> 4K7 -> red LED -> GNDD; a released key's ON node floats. Master: 10K to GNDD, 2 x 1N4148 in
series to GNDD (clamp: keeps PFLDET low enough that the released keys' LED paths don't conduct), 1u to GNDD
(debounce), LM393 against 330K / 10K from +VL, output pulled up by 100K to +5VL (DG413 logic), 10M from the output
back to PFLDET (hysteresis).
1. DC: PFLDET, threshold, current in a released and a pressed LED, N = 0..24 keys pressed.
2. Transient: one key pressed at 20 ms and released at 220 ms, both with ~3 ms of contact bounce (C&K PVA: <= 3 ms);
   counts how often the comparator output crosses the DG413 logic threshold (1.6 V) after each event.
Usage: python3 sim/pfldet.py   (ngspice on the PATH)"""
import os, re, subprocess, tempfile
VL, V5 = 16.9, 5.1                    # +VL (+VBUS less ~10 mA through 10R), +5VL (BZX84C5V1)
T = 38
MODELS = """.model LED D(IS=3.2e-19 N=2 RS=10)
.model D4148 D(IS=2.52n N=1.752 RS=0.568 CJO=4p)
.model SWK SW(VT=0.5 VH=0.01 RON=1 ROFF=1e10)
* LM393 (B grade on +-VL): open collector, sinks when - > +, emitter on -VL
.subckt CMP inp inn out vn
B1 out vn I = 0.5*(1+tanh(2e3*(V(inn)-V(inp))))*16m*tanh((V(out)-V(vn))/0.5)
COUT out 0 10p
.ends
"""
def line(pressed_src):
    """Netlist of the PFLDET line; pressed_src(k) gives the switch control for key k or None (released)."""
    L = ['* PFL detect line', MODELS, f'VL vl 0 {VL}', f'VM vm 0 {-VL}', f'V5 v5 0 {V5}',
         'RPD det 0 10K', 'DC1 det cl D4148', 'DC2 cl 0 D4148', 'CDB det 0 1u',
         'RA vl ref 330K', 'RB ref 0 10K', 'XC det ref out vm CMP', 'RPU v5 out 100K', 'RHY out det 10Meg']
    for k in range(T):
        on, ctl = f'on{k}', pressed_src(k)
        if ctl: L += [f'S{k} vl {on} {ctl} 0 SWK']
        L += [f'R{k} {on} det 100K', f'RL{k} {on} la{k} 4.7K', f'DL{k} la{k} 0 LED', f'CO{k} {on} 0 10p']
    return L
def run(lines):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write('\n'.join(lines) + '\n.end\n')
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout; os.unlink(f.name)
    return out
g = lambda out, k: float(re.search(k + r'\s*=\s*([-\d.e+]+)', out).group(1))

print(f'DC, {T} keys:  N   PFLDET V   threshold V   margin   I(released LED) nA   I(pressed LED) mA')
for N in (0, 1, 2, 4, 8, 12, 24):
    L = line(lambda k: 'vc' if k < N else None) + ['VC vc 0 1']
    L += ['.control', 'op', 'print v(det) v(ref)', f'let irel = (v(on{T - 1})-v(la{T - 1}))/4.7k', 'let ipr = (v(on0)-v(la0))/4.7k',
          'print irel ipr', '.endc']
    out = run(L)
    det, ref = g(out, r'v\(det\)'), g(out, r'v\(ref\)')
    print(f'                {N:2d}   {det:7.3f}     {ref:7.3f}    {det / ref if N else 0:5.2f}x   {g(out, "irel") * 1e9:10.2f}'
          f'          {g(out, "ipr") * 1e3 if N else 0:6.3f}')

# bounce: contact state changes (ms after the event), ~3 ms in all: press at 20 ms ends closed, release at 220 ms open
press = [(0, 1), (0.15, 0), (0.45, 1), (0.6, 0), (1.1, 1), (1.3, 0), (1.9, 1), (2.05, 0), (2.6, 1)]
rel = [(0, 0), (0.2, 1), (0.5, 0), (0.7, 1), (1.4, 0), (1.55, 1), (2.3, 0), (2.4, 1), (2.9, 0)]
pwl, state = ['0 0'], 0
for t0, seq in ((20e-3, press), (220e-3, rel)):
    for dt, v in seq:                 # 1 us edges
        t = t0 + dt * 1e-3; pwl += [f'{t:.7f} {state}', f'{t + 1e-6:.7f} {v}']; state = v
L = line(lambda k: 'vk' if k == 0 else None) + ['VK vk 0 PWL(' + ' '.join(pwl) + ')']
L += ['.tran 20u 0.35 0 20u', '.control', 'set noaskquit', 'run',
      'meas tran tp when v(out)=1.6 rise=1', 'meas tran tr when v(out)=1.6 fall=1',
      'meas tran np2 when v(out)=1.6 rise=2', 'meas tran nr2 when v(out)=1.6 fall=2',
      'meas tran vdet find v(det) at=0.2', '.endc']
out = run(L)
tp, tr = g(out, r'\btp'), g(out, r'\btr')
extra = re.findall(r'\b(np2|nr2)\s*=\s*([-\d.e+]+)', out)
print(f'\nBounce test (one key, ~3 ms bounce on press at 20 ms and on release at 220 ms):')
print(f'  PFL_ON_RAW rises at {(tp - 0.020) * 1e3:.1f} ms after the press, falls {(tr - 0.220) * 1e3:.1f} ms after the release;'
      f' PFLDET held {g(out, "vdet"):.3f} V')
print('  further crossings of 1.6 V: ' + ('none (one switch each way)' if not extra else ', '.join(f'{k} at {float(v):.4f} s' for k, v in extra)))
