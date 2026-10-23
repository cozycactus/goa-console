"""Self-heating of the string CCS PNP in the dark state (all comparators sinking: collector at -VM + 0.2 V).
Fixed-point iteration: ngspice operating point with the PNP instance at Tj, Tj = Ta + Rth * Pq. Diodes at Ta.
Usage: ccs_thermal.py  (prints a table for Rth / collector-resistor / emitter-resistor options)"""
import subprocess, re, tempfile, os
NG = '/opt/homebrew/bin/ngspice'
MODEL = ('.model MMBT3906 PNP(IS=1.41f XTI=3 EG=1.11 VAF=18.7 BF=180.7 NE=1.5 ISE=0 IKF=80m XTB=1.5 BR=4.977 NC=2 '
         'ISC=0 IKR=0 RC=2.5 CJC=9.728p MJC=.5776 VJC=.75 FC=.5 CJE=8.063p MJE=.3677 VJE=.75 TR=33.42n TF=179.3p '
         'ITF=.4 VTF=4 XTF=6 RB=10)\n.model D1N4148 D(IS=2.52n RS=0.568 N=1.752 CJO=4p M=0.4 TT=20n BV=100)\n')
def op(tj, ta, re_=75, rc=0, vm=16.43, vbot=0.2):
    deck = f"""* ccs
.options temp={ta} tnom=27
{MODEL}
VP vmp 0 {vm}
VN vmn 0 {-vm}
RE vmp e {re_}
D1 vmp d1 D1N4148
D2 d1 b D1N4148
RB b vmn 27k
Q c b e MMBT3906 temp={tj}
RC c top {rc if rc else 1e-3}
VB top bot 0
VS bot vmn {vbot}
.control
op
print v(e) v(c) v(top) i(VB)
.endc
.end
"""
    fd, p = tempfile.mkstemp(suffix='.cir'); os.write(fd, deck.encode()); os.close(fd)
    r = subprocess.run([NG, '-b', p], capture_output=True, text=True).stdout; os.unlink(p)
    g = lambda n: float(re.search(rf'^{re.escape(n)} = (\S+)', r, re.M).group(1))
    ve, vc, ic = g('v(e)'), g('v(c)'), g('i(vb)')
    return ve, vc, ic
def solve(rth, ta=40, re_=75, rc=0, vbot=0.2):
    tj = ta
    for _ in range(60):
        ve, vc, ic = op(tj, ta, re_, rc, vbot=vbot)
        p = (ve - vc) * ic
        tn = ta + rth * p
        if tn > 400: return float('inf'), ic, p
        if abs(tn - tj) < 0.05: break
        tj = 0.5 * tj + 0.5 * tn
    return tj, ic, p
print('dark state (collector string fully bypassed), Ta = 40 C, +-VM = 16.43 V')
print('case                                   Rth K/W  Re   Rc    Tj C    I mA   Pq mW   P(Rc) mW')
for name, rth, re_, rc in (('MMBT3906 SOT-23, min pad (onsemi)', 556, 75, 0),
                           ('MMBT3906 SOT-23, alumina figure', 417, 75, 0),
                           ('MMBT3906 + 1K2 collector R', 556, 75, 1200),
                           ('MMBT3906 + 1K2, Re 110R (~4 mA)', 556, 110, 1200),
                           ('SOT-89/SOT-223 PNP, ~200 K/W', 200, 75, 0),
                           ('SOT-223 PNP, ~100 K/W (1 cm2+)', 100, 75, 0),
                           ('TO-92 2N3906, 200 K/W', 200, 75, 0)):
    tj, ic, p = solve(rth, re_=re_, rc=rc)
    print(f'{name:<38} {rth:6d}  {re_:4d} {rc:5d}  {tj:6.1f}  {ic*1e3:5.2f}  {p*1e3:6.1f}   {ic*ic*rc*1e3:5.1f}')
print('at Ta = 25 C, MMBT3906 556 K/W:', solve(556, ta=25))
print('isothermal (Tj = Ta = 27 C) current:', op(27, 27)[2])
