"""Meter L detector transient with TL072 models (old Boyle / TL07xH) vs an ideal single-pole op-amp: steady sine and
tone-burst readings at DET, and the U3 (peak detector) output for ringing. Deck = master deck lines on meter-L nets."""
import sys, re, numpy as np
from masterdeck import deck
from tian import ngspice, load, HERE
KEEP = lambda n: n == '0' or n.startswith(('ML_', 'MTR_L', 'PVM', 'MVM', 'U29', 'U30', 'CLD', 'nc_U29', 'nc_U30')) or n in ('PVM', 'MVM')
def meter_deck(tl, jp, trim, src, tstop, extra=(), step='2u'):
    d = deck(dict(tl='old' if tl == 'ideal' else tl, jp={'JP1': jp}, pos={'RV7': trim}, extra=list(extra)), '')
    out = []; skip = False
    for line in d.splitlines():
        if line.startswith('.subckt LME49600M'): skip = True
        if skip:
            if line.startswith('.ends'): skip = False
            continue
        t = line.split()
        if not t or line.startswith(('*', '.')) or t[0].startswith('+'):
            if line.startswith(('.include', '.model', '.subckt', '.ends')) or not t or line.startswith('*'): out.append(line)
            continue
        if t[0][0] == 'X' and t[-1] in ('TL072', 'TL07XH_TL08XH', 'OPAID'): nodes = t[1:-1]
        elif t[0][0] in 'RCDV' and len(t) >= 3: nodes = t[1:3]
        else: continue
        if all(KEEP(n) for n in nodes): out.append(line)
    # inside-subckt lines of the LME/other subckts were kept whole above only for .subckt blocks; rebuild simply:
    txt = '\n'.join(out)
    if tl == 'ideal':
        txt = txt.replace(' TL072\n', ' OPAID\n')
        txt += '''
.subckt OPAID inp inn vcc vee out
G1 0 n1 inp inn 1e-3
R1 n1 0 1e8
C1 n1 0 53.05p
VCL ch 0 14
VCM cl 0 -14
DH n1 ch DID
DL cl n1 DID
.model DID D(IS=1e-14 N=0.05)
E1 out 0 n1 0 1
.ends'''
    txt += f'\nBSRC MTR_L 0 V = {src}\n'
    txt += f'.options itl1=500 noopiter\n.control\nset wr_singlescale\nset wr_vecnames\ntran {step} {tstop} 0 {step}\nwrdata {HERE}/raw/mtr.txt v(ML_DET) v(ML_U3O) v(ML_X2) v(ML_PK)\n.endc\n.end'
    return txt
if __name__ == '__main__':
    import json
    d = meter_deck('old', 'PK', 0.16, 'sin(2*pi*1k*time)', 0.05)
    open('raw/meter_test.cir', 'w').write(d)
    print(len(d.splitlines()))
