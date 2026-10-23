"""Build an ngspice deck of the GENERATED meter (both sides, as master.net): +-V -> 10R -> +-VM, threshold ladder
16K..91R, 2 x 10-LED strings per side from a PNP current source (2 x 1N4148, 27K; re= emitter R, 75R in the first
draft, 120R as built; pnp=bcp53 as built, pnp=mmbt3906 the first draft), 20 LM2901-like open-collector
comparators per side (GND pin = -VM as in master.net), DET swept by a DC source (= U4 output).
Usage: mkdeck.py out.cir [key=value ...]  keys: vrail, green, amber, red (typ|max|ingan|ingan_max), isink (typ 16m / min 6m),
vos_seed (0 = no offset), vos_max, icc (per package), tl072 (per package), re (emitter R), pnp (bcp53 | mmbt3906), temp"""
import sys, random, math
out = sys.argv[1]
o = dict(vrail=17.0, green='typ', amber='typ', red='typ', isink=16e-3, vos_seed=0, vos_max=3.5e-3, icc=1.0e-3,
         tl072=2.8e-3, re=120.0, temp=27.0, ib=25e-9, step=0.5e-3, pnp='bcp53')
for a in sys.argv[2:]:
    k, v = a.split('='); o[k] = v if k in ('green', 'amber', 'red', 'pnp') else float(v)
LADDER = [1500, 1100, 910, 680, 620, 470, 330, 300, 220, 180, 150, 110, 91, 68, 62, 47, 33, 27, 20]
COLOUR = ['green'] * 11 + ['amber'] * 5 + ['red'] * 4
VT = 0.025852
def led_model(name, vf, iff, n, rs):
    vj = vf - iff * rs
    return f'.model {name} D(IS={iff / math.exp(vj / (n * VT)):.4e} N={n} RS={rs} BV=5 IBV=10u CJO=15p)'
# Kingbright WP710A10GD green GaP 2.0 typ / 2.4 max @10 mA; WP710A10ND orange 1.95 / 2.3; WP710A10ID HE red 1.9 / 2.3;
# InGaN WP710A10ZGCK 3.3 typ / 4.1 max @20 mA
LEDS = {('green', 'typ'): (2.0, 10e-3, 2.0, 12), ('green', 'max'): (2.4, 10e-3, 2.0, 12),
        ('amber', 'typ'): (1.95, 10e-3, 2.0, 10), ('amber', 'max'): (2.3, 10e-3, 2.0, 10),
        ('red', 'typ'): (1.9, 10e-3, 2.0, 10), ('red', 'max'): (2.3, 10e-3, 2.0, 10),
        ('green', 'ingan'): (3.3, 20e-3, 3.0, 12), ('green', 'ingan_max'): (4.1, 20e-3, 3.0, 12)}
L = []
w = L.append
w('* generated meter, both sides; see mkdeck.py header. options: ' + ' '.join(f'{k}={v}' for k, v in o.items()))
w(f'.options temp={o["temp"]} tnom=27 gmin=1e-12 reltol=1e-4 itl1=500 itl2=500')
w('.model D1N4148 D(IS=2.52n RS=0.568 N=1.752 CJO=4p M=0.4 TT=20n BV=100)')
w('.model MMBT3906 PNP(IS=1.41f XTI=3 EG=1.11 VAF=18.7 BF=180.7 NE=1.5 ISE=0 IKF=80m XTB=1.5 BR=4.977 NC=2 ISC=0 '
  'IKR=0 RC=2.5 CJC=9.728p MJC=.5776 VJC=.75 FC=.5 CJE=8.063p MJE=.3677 VJE=.75 TR=33.42n TF=179.3p ITF=.4 VTF=4 XTF=6 RB=10)')
# BCP53-16 (SOT-223, larger die): the MMBT3906 card with IS scaled so Vbe is ~0.63 V at 5 mA (datasheet typical)
w('.model BCP53 PNP(IS=1.3e-13 XTI=3 EG=1.11 VAF=100 BF=150 NE=1.5 ISE=0 IKF=1 XTB=1.5 BR=4.977 NC=2 ISC=0 '
  'IKR=0 RC=0.3 CJC=30p MJC=.5776 VJC=.75 FC=.5 CJE=60p MJE=.3677 VJE=.75 TR=33.42n TF=400p ITF=.4 VTF=4 XTF=6 RB=5)')
w('.model QOC NPN(IS=1e-14 BF=100 BR=1 RC=15 VAF=100)')
for c in ('green', 'amber', 'red'): w(led_model('LED_' + c, *LEDS[(c, o[c])]))
# LM2901-like comparator: PNP-input bias out of the pins, offset, ICC, open-collector NPN with limited base drive
w('.subckt CMP inp inn out vcc vee vos=0')
w(f'IB1 vcc inp {o["ib"]}')
w(f'IB2 vcc inn {o["ib"]}')
w(f'ICC vcc vee {o["icc"] / 4}')
w(f'BB vcc bq I = {o["isink"] / 100} * 0.5 * (1 + tanh((V(inn) - V(inp) - vos) / 0.5m))')
w('RBQ bq vee 100k')
w('QO out bq vee QOC')
w('.ends')
w(f'VP vp 0 {o["vrail"]}')
w(f'VN 0 vn {o["vrail"]}')
w('R5 vp vmp 10'); w('R6 vn vmn 10')
w('C5 vmp 0 47u'); w('C6 0 vmn 47u')
w(f'ITL vmp vmn {4 * o["tl072"]}')          # 4 x TL072 (both detectors), modelled as constant supply current
w('VDET det 0 0.649')
rnd = random.Random(int(o['vos_seed']))
for sd in 'LR':
    m = 'M' + sd
    w(f'R{m}16K vmp {m}_T20 16k')
    for k, rv in zip(range(20, 1, -1), LADDER): w(f'R{m}L{k} {m}_T{k} {m}_T{k - 1} {rv}')
    w(f'R{m}91 {m}_T1 0 91')
    for s0, ks in (('A', range(1, 11)), ('B', range(11, 21))):
        p = f'{m}{s0}'
        w(f'RE{p} vmp {p}_QE {o["re"]}')
        w(f'DR1{p} vmp {p}_D1 D1N4148'); w(f'DR2{p} {p}_D1 {p}_QB D1N4148'); w(f'RB{p} {p}_QB vmn 27k')
        w(f'Q{p} {p}_0 {p}_QB {p}_QE {o["pnp"].upper()}')     # C B E
        for i, k in enumerate(ks):
            node = f'{p}_{i}'; nxt = f'{p}_{i + 1}' if i < 9 else 'vmn'
            w(f'VL{m}{k} {node} {node}x 0')
            w(f'D{m}{k} {node}x {nxt} LED_{COLOUR[k - 1]}')
            vos = (rnd.uniform(-1, 1) * o['vos_max']) if o['vos_seed'] else 0
            w(f'VO{m}{k} {node} {node}o 0')
            w(f'X{m}{k} det {m}_T{k} {node}o vmp vmn CMP vos={vos:.5f}')
w('.control')
w('set noaskquit'); w('set wr_singlescale'); w('set wr_vecnames')
w(f'dc VDET 0.01 6.6 {o["step"]}')
vecs = ['v(vmp)', 'v(vmn)']
for sd in 'LR':
    m = 'M' + sd
    vecs += [f'v({m}_T{k})' for k in (1, 11, 20)]
    for s0 in 'AB':
        p = f'{m}{s0}'; vecs += [f'v({p}_QE)', f'v({p}_0)']
    vecs += [f'i(VL{m}{k})' for k in range(1, 21)]
    vecs += [f'i(VO{m}{k})' for k in range(1, 21)]
    for s0 in 'AB':
        vecs += [f'v(M{sd}{s0}_{i})' for i in range(10)]
w('wrdata ' + out.replace('.cir', '.dat') + ' ' + ' '.join(vecs))
w('quit')
w('.endc')
w('.end')
open(out, 'w').write('\n'.join(L) + '\n')
open(out.replace('.cir', '.cols'), 'w').write('\n'.join(vecs) + '\n')
