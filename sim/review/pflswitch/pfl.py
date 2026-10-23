"""PFL switcher review decks (generated circuit, Delta-faithful fix, alternatives). Writes decks to ./decks, runs ngspice -b,
parses results. Usage: python3 pfl.py <test> [variant] [model]"""
import subprocess, sys, os, re, math
HERE = os.path.dirname(os.path.abspath(__file__))
DECKS = os.path.join(HERE, 'decks'); os.makedirs(DECKS, exist_ok=True)
NG = '/opt/homebrew/bin/ngspice'
VL = 16.9          # +-VL on the master: +-17 V through 10R + 47u

def sources(am, fm, ap, fp, amr=0, fmr=1300, acm=0, acp=0):
    """MON_L / MON_R = POST_L/R (fader post-amp -> 220u NP -> 47K || DRV134 10K || mono 10K ~ 4.5K, then EXT switch);
    PFL_SIG = OPA1612 follower output (DC coupled)."""
    return f"""
VML ml0 0 DC 0 AC {acm} SIN(0 {am} {fm})
RML ml0 ml1 0.05
CML ml1 MON_L 220u
RMLG MON_L 0 4.5k
VMR mr0 0 DC 0 SIN(0 {amr} {fmr})
RMR mr0 mr1 0.05
CMR mr1 MON_R 220u
RMRG MON_R 0 4.5k
VPF pf0 0 DC 0 AC {acp} SIN(0 {ap} {fp})
RPF pf0 PFL_SIG 0.05
"""

def control(variant, t_sw, pfl0):
    """LM393 open-collector outputs to -VL (Vol ~0.15 V at these currents, ~60 ohm), 10K pull-ups to +VL,
    then the 100K / 100 nF ramp (generated). MON_ON_RAW also feeds the flasher hold diode D14 (FL_P network).
    pfl0 = 1: PFL active at t=0. The state toggles at t_sw."""
    a, b = (1, 0) if pfl0 else (0, 1)
    s = f"""
VLP VLP 0 {VL}
VLN VLN 0 -{VL}
VLO vlo 0 -{VL - 0.12}
* control: VCP high = PFL comparator sinks (PFL inactive); VCM high = MON comparator sinks (PFL active)
VCP cp 0 PWL(0 {b} {t_sw} {b} {t_sw + 1e-6} {a})
VCM cm 0 PWL(0 {a} {t_sw} {a} {t_sw + 1e-6} {b})
* LM393 output transistor: conductance ramps 0 -> 1/60 S over ~1 us (output fall/rise time ~1 us)
BSP PFL_ON_RAW vlo I = V(PFL_ON_RAW, vlo) * (1e-10 + V(cp) / 60)
BSM MON_ON_RAW vlo I = V(MON_ON_RAW, vlo) * (1e-10 + V(cm) / 60)
R97 VLP PFL_ON_RAW 10k
R98 VLP MON_ON_RAW 10k
D14 MON_ON_RAW FL_P D1N4148
RFL1 VLP FL_P 100k
RFL2 FL_P 0 100k
RFL3 VLP FL_P 100k
"""
    if variant in ('gen', 'gen47', 'fixA'):
        s += """
R99 PFL_ON_RAW PFL_ON 100k
C88 PFL_ON 0 100n
R100 MON_ON_RAW MON_ON 100k
C89 MON_ON 0 100n
"""
    elif variant in ('fixB',):
        # ramp 10K / 1 uF (same 10 ms), stiff enough for 470K gate resistors
        s += """
R99 PFL_ON_RAW PFL_ON 10k
C88 PFL_ON 0 1u
R100 MON_ON_RAW MON_ON 10k
C89 MON_ON 0 1u
"""
    elif variant in ('fixD', 'fixD1', 'fixD5'):
        # Delta-style drivers (ED2780 TR13/TR14 with Miller caps C43/C44): NPN, emitter -VL, collector = line,
        # 100K pull-up (Delta R69), 1M base resistor from the comparator output, 47K base-emitter, 2.2 nF collector-base.
        # Cross-connected: the PFL line is pulled down while PFL is idle (MON_ON_RAW high), and vice versa.
        cm = {'fixD': '2.2n', 'fixD1': '2.2n', 'fixD5': '10n'}[variant]
        s += f"""
.model Q3904 NPN(IS=1E-14 VAF=100 Bf=300 IKF=0.4 XTB=1.5 BR=4 CJC=4E-12 CJE=8E-12 RB=20 RC=0.1 RE=0.1 TR=250E-9 TF=350E-12 ITF=1 VTF=2 XTF=3)
QDP PFL_ON QBP VLN Q3904
RBP MON_ON_RAW QBP 1meg
RBEP QBP VLN 47k
CMP PFL_ON QBP {cm}
RPUP VLP PFL_ON 100k
QDM MON_ON QBM VLN Q3904
RBM PFL_ON_RAW QBM 1meg
RBEM QBM VLN 47k
CMM MON_ON QBM {cm}
RPUM VLP MON_ON 100k
"""
    elif variant in ('delta', 'fixC'):
        # line driven straight from the comparator (no RC): stiff, fast (Delta TR13/TR14 are saturated transistors)
        s += """
R99 PFL_ON_RAW PFL_ON 1
R100 MON_ON_RAW MON_ON 1
"""
    return s

def switch(variant, src, dst, ctrl, n, model):
    """One series J112 switch. n = name. Generated: 47u src->S, 1M S->GNDA, 47K G->S, 1N4148 G->ctrl."""
    if variant == 'gen':        # as generated (master.net R107-R115, C91-C96, D16-D19, Q2-Q5)
        return f"""
CSW{n} {src} {n}_S 47u
RSW{n}S {n}_S 0 1meg
J{n} {dst} {n}_G {n}_S {model}
RSW{n}G {n}_G {n}_S 47k
DSW{n} {n}_G {ctrl} D1N4148
"""
    if variant == 'gen47':      # as the spec text: 47K source-to-ground (instead of 1M)
        return f"""
CSW{n} {src} {n}_S 47u
RSW{n}S {n}_S 0 47k
J{n} {dst} {n}_G {n}_S {model}
RSW{n}G {n}_G {n}_S 47k
DSW{n} {n}_G {ctrl} D1N4148
"""
    if variant in ('delta', 'fixA', 'fixB', 'fixC', 'fixD', 'fixD1', 'fixD5'):
        # Delta ED2780 sh.1: gate resistor from the DC-coupled (pre-cap) side; 1M keeps the floating source at 0 V
        rg = {'delta': '47k', 'fixA': '47k', 'fixB': '470k', 'fixC': '470k', 'fixD': '47k', 'fixD1': '47k', 'fixD5': '47k'}[variant]
        return f"""
CSW{n} {src} {n}_S 47u
RSW{n}S {n}_S 0 1meg
J{n} {dst} {n}_G {n}_S {model}
RSW{n}G {n}_G {src} {rg}
DSW{n} {n}_G {ctrl} D1N4148
"""
    raise ValueError(variant)

def crs(side, ibv='60n'):
    """CRS node: 100K to GNDA (R111/R116), OPA1612 follower input (Ib 60 nA typ, ~2 pF), follower = ideal buffer.
    Output view: CRSB, plus 20 Hz-20 kHz band (2nd-order HP 20 Hz and 2nd-order Butterworth LP 20 kHz)."""
    return f"""
R{side}CRS CRS_{side} 0 100k
I{side}B CRS_{side} 0 {ibv}
C{side}IN CRS_{side} 0 2p
E{side}B CRSB_{side} 0 CRS_{side} 0 1
* 20 kHz Butterworth LP (as sim/routing_switch.cir), then 20 Hz Butterworth HP (series R-C, shunt L): BAND = 20 Hz-20 kHz
R{side}L1 CRSB_{side} {side}f1 1125
L{side}L1 {side}f1 {side}f2 6.333m
C{side}L1 {side}f2 0 10n
E{side}L2 {side}f3 0 {side}f2 0 1
R{side}H1 {side}f3 {side}f4 1125
C{side}H1 {side}f4 BAND_{side} 10u
L{side}H1 BAND_{side} 0 6.333
"""

def deck(variant, model, body_ctrl, am=0, fm=1e3, ap=0, fp=1e3, amr=0, fmr=1.3e3, t_sw=1.0, pfl0=0, extra='', acm=0, acp=0):
    lib = os.path.join(HERE, 'models.lib')
    s = f"* PFL switcher, variant={variant}, model={model}\n.include {lib}\n"
    s += sources(am, fm, ap, fp, amr, fmr, acm, acp)
    if variant in ('gen', 'gen47', 'delta', 'fixA', 'fixB', 'fixC', 'fixD', 'fixD1', 'fixD5'):
        s += control(variant, t_sw, pfl0)
        ml, mr = 'MON_L', 'MON_R'
        if variant in ('delta', 'fixA', 'fixB', 'fixC', 'fixD', 'fixD1', 'fixD5'):
            # MON buffered by a new OPA1612 follower per side (DC-coupled op-amp output, as the Delta's IC7 outputs)
            s += "EBML MONB0_L 0 MON_L 0 1\nRBML MONB0_L MONB_L 0.05\nEBMR MONB0_R 0 MON_R 0 1\nRBMR MONB0_R MONB_R 0.05\n"
            ml, mr = 'MONB_L', 'MONB_R'
        s += switch(variant, ml, 'CRS_L', 'MON_ON', 'ML', model)
        s += switch(variant, 'PFL_SIG', 'CRS_L', 'PFL_ON', 'PL', model)
        s += switch(variant, mr, 'CRS_R', 'MON_ON', 'MR', model)
        s += switch(variant, 'PFL_SIG', 'CRS_R', 'PFL_ON', 'PR', model)
    ibv = '10p' if variant in ('fixD', 'fixD5') else '60n'
    s += crs('L', ibv) + crs('R', ibv)
    s += extra
    s += ".options reltol=1e-5 abstol=1e-14 vntol=1e-9 itl1=500 itl4=200 method=" + os.environ.get('METHOD', 'gear') + "\n"
    s += ".control\nset noaskquit\nset wr_singlescale\nset wr_vecnames\n" + body_ctrl + "\n.endc\n.end\n"
    return s

def run(name, text, timeout=1200):
    p = os.path.join(DECKS, name + '.cir')
    open(p, 'w').write(text)
    r = subprocess.run([NG, '-b', p], capture_output=True, text=True, cwd=DECKS, timeout=timeout)
    out = r.stdout + r.stderr
    open(os.path.join(DECKS, name + '.log'), 'w').write(out)
    return out

def grab(out, key):
    m = re.findall(rf'^\s*{re.escape(key)}\s*=\s*([-+0-9.eE]+)', out, re.M)
    return float(m[-1]) if m else None

# ------------------------------------------------------------------ alternatives
def dg_switch(n, s, d, state, ron0=17, ka=-0.15, kb=0.02, qinj=5e-12, t_ev=None, sign=1, ileak=0):
    """DG413 SPST (Vishay doc 70050 rev G): Ron(V) as sim/routing_switch.cir (17 ohm at 0 V, -0.15 ohm/V, +0.02 ohm/V^2;
    25 typ / 35 max at +-8.5 V), CS(off) = CD(off) = 9 pF, CD(on)+CS(on) 35 pF (26 pF added when on, approximated
    by keeping 9 + 9 and adding 17 pF across), CDS(off) 1.3 pF (68 dB off isolation at 1 MHz into 50 ohm).
    state = node with 0..1 (switch conductance scale). Charge injection: qinj (5 pC typ, CL 10 nF, VG 0) into D as a
    50 ns pulse at t_ev. ileak: leakage current drawn out of S (IS(off) 0.1 nA typ / 0.25 nA max at room temperature;
    0 V bias here, so less), which steps CRS by the S node's offset when the switch closes."""
    vm = f'((V({s})+V({d}))/2)'
    t = f"""
B{n} {s} {d} I = V({s},{d}) * (1e-12 + V({state}) / ({ron0} + ({ka})*{vm} + ({kb})*{vm}*{vm}))
C{n}S {s} 0 9p
C{n}D {d} 0 9p
C{n}X {s} {d} 1.3p
"""
    if t_ev is not None and qinj:
        t += f"I{n}Q 0 {d} PULSE(0 {sign*qinj/50e-9} {t_ev} 5n 5n 40n 10)\n"
    if ileak:
        t += f"I{n}L {s} 0 {ileak}\n"
    return t

def dg_deck(body_ctrl, am=0, fm=1e3, ap=0, fp=1e3, amr=0, fmr=1.3e3, t_sw=1.0, pfl0=0, acm=0, acp=0,
            rload='100k', cload=0, ib=60e-9, qinj=5e-12, ka=-0.15, kb=0.02, topo='series', gap=25e-9, ileak=0):
    """(a) series DG413: SW2/SW3 (logic 0 = on) carry MON_L/MON_R, SW1/SW4 (logic 1 = on) carry PFL to CRS_L/CRS_R;
    47u NP + 1M kept at each S node, CRS on the D side; logic = PFL_ON_RAW (LM393, 10K pull-up to +5VL).
    break-before-make: the on-going switch closes `gap` after the off-going one opens (tD 25 ns typ).
    (b) virtual earth: each input through 10K to an S node; SW to the virtual earth (D) and SW to GNDA, as the strip routing;
    inverting summer (OPA1612, Rf 10K || 100 pF) then an ideal re-inverter."""
    lib = os.path.join(HERE, 'models.lib')
    a, b = (1, 0) if pfl0 else (0, 1)          # PFL switch state before / after
    s = f"* PFL switcher alternative: DG413 {topo}\n.include {lib}\n" + sources(am, fm, ap, fp, amr, fmr, acm, acp)
    # switch states: off-going opens over 20 ns at t_sw, on-going closes over 20 ns at t_sw + gap
    def pwl(v0, v1, t0): return f'PWL(0 {v0} {t0} {v0} {t0 + 20e-9} {v1})'
    tp = t_sw + (gap if not pfl0 else 0); tm = t_sw + (gap if pfl0 else 0)
    s += f"VSTP stp 0 {pwl(a, b, tp)}\nVSTM stm 0 {pwl(b, a, tm)}\n"
    if topo == 'series':
        for side, mon in (('L', 'MON_L'), ('R', 'MON_R')):
            s += f"CIM{side} {mon} SM{side} 47u\nRIM{side} SM{side} 0 1meg\nCIP{side} PFL_SIG SP{side} 47u\nRIP{side} SP{side} 0 1meg\n"
            s += dg_switch(f'XM{side}', f'SM{side}', f'CRS_{side}', 'stm', ka=ka, kb=kb, qinj=qinj, t_ev=tm, sign=1, ileak=ileak)
            s += dg_switch(f'XP{side}', f'SP{side}', f'CRS_{side}', 'stp', ka=ka, kb=kb, qinj=qinj, t_ev=tp, sign=1, ileak=ileak)
            s += f"R{side}CRS CRS_{side} 0 {rload}\nI{side}B CRS_{side} 0 {ib}\nC{side}IN CRS_{side} 0 {2e-12 + cload}\nE{side}B CRSB_{side} 0 CRS_{side} 0 1\n"
            s += band(side)
    else:
        s += """.subckt OPA2 inp inn out
* OPA1612 as sim/routing_switch.cir: GBW 40 MHz, A0 120 dB, second pole 70 MHz
G1 0 n1 inp inn 1
R1 n1 0 1e6
C1 n1 0 3.98n
E2 n2 0 n1 0 1
R2 n2 n3 1k
C2 n3 0 2.27p
E1 out 0 n3 0 1
.ends
"""
        for side, mon in (('L', 'MON_L'), ('R', 'MON_R')):
            s += f"RIM{side} {mon} SM{side} 10k\nCIP{side} PFL_SIG PC{side} 47u\nRPC{side} PC{side} 0 1meg\nRIP{side} PC{side} SP{side} 10k\n"
            s += f"VDUMMY{side} sinv{side} 0 0\n"
            s += dg_switch(f'XM{side}', f'SM{side}', f'VE_{side}', 'stm', qinj=qinj, t_ev=tm)
            s += dg_switch(f'YM{side}', f'SM{side}', '0', 'stp', qinj=0)           # grounds the MON resistor when PFL is on
            s += dg_switch(f'XP{side}', f'SP{side}', f'VE_{side}', 'stp', qinj=qinj, t_ev=tp)
            s += dg_switch(f'YP{side}', f'SP{side}', '0', 'stm', qinj=0)
            s += f"XU{side} 0 VE_{side} INV_{side} OPA2\nRF{side} INV_{side} VE_{side} 10k\nCF{side} INV_{side} VE_{side} 100p\nCV{side} VE_{side} 0 30p\n"
            s += f"E{side}RI CRS_{side} 0 INV_{side} 0 -1\nE{side}B CRSB_{side} 0 CRS_{side} 0 1\n"
            s += band(side)
    s += ".options reltol=1e-5 abstol=1e-14 vntol=1e-9 itl1=500 itl4=200 method=" + os.environ.get('METHOD', 'gear') + "\n"
    s += ".control\nset noaskquit\nset wr_singlescale\nset wr_vecnames\n" + body_ctrl + "\n.endc\n.end\n"
    return s

def band(side):
    return f"""R{side}L1 CRSB_{side} {side}f1 1125
L{side}L1 {side}f1 {side}f2 6.333m
C{side}L1 {side}f2 0 10n
E{side}L2 {side}f3 0 {side}f2 0 1
R{side}H1 {side}f3 {side}f4 1125
C{side}H1 {side}f4 BAND_{side} 10u
L{side}H1 BAND_{side} 0 6.333
"""

DG_OPTS = {'dg': dict(), 'dgW': dict(ka=-0.3, kb=0.04), 'dgC': dict(cload=1e-9), 'dgM': dict(rload='1meg', ib=10e-12, cload=1e-9),
           'dgMW': dict(rload='1meg', ib=10e-12, cload=1e-9, ka=-0.3, kb=0.04), 've': dict(topo='ve'), 'dgF': dict(ib=10e-12), 'dgF_L10p': dict(ib=10e-12, ileak=10e-12), 'dgF_L100p': dict(ib=10e-12, ileak=100e-12), 'dgF_L250p': dict(ib=10e-12, ileak=250e-12), 'dgF2': dict(ib=10e-12, cload=220e-12), 'dgF1M': dict(ib=10e-12, rload='1meg')}
def make(variant, model, body, **kw):
    if variant in DG_OPTS:
        kw.pop('extra', None)
        o = dict(DG_OPTS[variant]); o.update(kw)
        return dg_deck(body, **o)
    return deck(variant, model, body, **kw)

def relay_deck(body_ctrl, am=0, fm=1e3, ap=0, fp=1e3, amr=0, fmr=1.3e3, t_sw=1.0, pfl0=0, acm=0, acp=0, ib=10e-12,
               transfer=1.5e-3, bounce=True):
    """(c) DPDT signal relay (G6K-2F-Y class), pole per side: COM = CRS, NC = MON, NO = PFL; 47u NP + 1M kept at
    each input; contact 0.1 ohm closed, 1 pF open. Changeover: the closed contact opens at t_sw, the other closes
    `transfer` later (operate/release 3 ms max), with bounce 50 us open / 50 us closed / 30 us open, then closed."""
    lib = os.path.join(HERE, 'models.lib')
    s = f"* PFL switcher alternative: relay\n.include {lib}\n" + sources(am, fm, ap, fp, amr, fmr, acm, acp)
    tc = t_sw + transfer
    def opening(): return f'PWL(0 1 {t_sw} 1 {t_sw + 10e-6} 0)'
    def closing():
        if not bounce: return f'PWL(0 0 {tc} 0 {tc + 10e-6} 1)'
        seq = [(0, 0), (tc, 0), (tc + 10e-6, 1), (tc + 50e-6, 1), (tc + 60e-6, 0), (tc + 100e-6, 0), (tc + 110e-6, 1),
               (tc + 150e-6, 1), (tc + 160e-6, 0), (tc + 180e-6, 0), (tc + 190e-6, 1)]
        return 'PWL(' + ' '.join(f'{a} {b}' for a, b in seq) + ')'
    sm, sp = (opening(), closing()) if not pfl0 else (closing(), opening())
    s += f"VSTM stm 0 {sm}\nVSTP stp 0 {sp}\n"
    for side, mon in (('L', 'MON_L'), ('R', 'MON_R')):
        s += f"CIM{side} {mon} SM{side} 47u\nRIM{side} SM{side} 0 1meg\nCIP{side} PFL_SIG SP{side} 47u\nRIP{side} SP{side} 0 1meg\n"
        for n, a, st in ((f'KM{side}', f'SM{side}', 'stm'), (f'KP{side}', f'SP{side}', 'stp')):
            s += f"B{n} {a} CRS_{side} I = V({a},CRS_{side}) * (1e-12 + V({st}) / 0.1)\nC{n} {a} CRS_{side} 1p\n"
        s += f"R{side}CRS CRS_{side} 0 100k\nI{side}B CRS_{side} 0 {ib}\nC{side}IN CRS_{side} 0 5p\nE{side}B CRSB_{side} 0 CRS_{side} 0 1\n"
        s += band(side)
    s += ".options reltol=1e-5 abstol=1e-14 vntol=1e-9 itl1=500 itl4=200 method=" + os.environ.get('METHOD', 'gear') + "\n"
    s += ".control\nset noaskquit\nset wr_singlescale\nset wr_vecnames\n" + body_ctrl + "\n.endc\n.end\n"
    return s

_make0 = make
def make(variant, model, body, **kw):
    if variant == 'relay':
        kw.pop('extra', None); return relay_deck(body, **kw)
    return _make0(variant, model, body, **kw)
