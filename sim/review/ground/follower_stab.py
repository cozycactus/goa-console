"""Phase margin of the strip's input followers U16 (OPA1656, docs/studies/ground_study.md G3): unity follower, 220R in and 100 pF (C94 / C95)
at the + input, driving R6 / R8 (10K into U1A) through SW15 and the panel wiring (5 pF),
with extra load capacitance 0-220 pF behind a build-out of 0 / 47 / 100 ohm (feedback from the op-amp pin).
usage: OPA1656_MACRO=<models_cd.inc> python3 sim/review/ground/follower_stab.py
The macro is the datasheet-fitted OPA1656M of the master review (pins inp inn out cp cn; the test source on cp breaks
the loop at the input stage); it is kept with the review's scratch files, not in the repo."""
import os, re, subprocess, tempfile
LIB = os.environ['OPA1656_MACRO']

def margin(rb, cl):
    d = f"""* U16 follower, build-out {rb}, CL {cl}
.include {LIB}
VT t 0 AC 1
RS in 0 220
CS in 0 100p
X1 in o o t 0 OPA1656M
RB o ob {rb or 1e-3}
R6 ob vn 10k
R7 vn rx 10k
EU rx 0 0 vn 1e5
CL ob 0 {cl or 1e-15}
CW ob 0 5p
.control
set noaskquit
ac dec 200 10k 300meg
let tg = (v(o)-v(in))/v(t)
let mag = db(tg)
let phs = 180 + ph(tg)*180/pi
meas ac fc when mag=0 fall=1
meas ac pm find phs at=fc
.endc
.end"""
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    v = dict(re.findall(r'^(fc|pm)\s+=\s+([-+0-9.eE]+)', out, re.M))
    return float(v['fc']), (float(v['pm']) + 180) % 360 - 180

for rb in (0, 47, 100):
    for cl in (0, 22e-12, 47e-12, 100e-12, 220e-12):
        fc, pm = margin(rb, cl)
        print(f'build-out {rb:3d} ohm, CL {cl * 1e12:5.0f} pF: crossover {fc / 1e6:5.1f} MHz, phase margin {pm:5.1f} deg')
