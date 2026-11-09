"""Generate the external PSU regulator board schematic (psu_spec.md v0.2, option B): two identical floating
rails, each Mean Well LRS-150-24 (21.6 V) -> LC 10 uH / 2200 uF -> LM1084-ADJ 17.0 V with 47 uF ADJ soft
start -> TL431 / PNP / SCR crowbar at 19.1 V. +V rail: OUT = +V, RTN = 0V; -V rail: OUT = 0V, RTN = -V.
usage: .venv/bin/python tools/gen_psu.py   ->  psu.kicad_sch (+ psu.kicad_pro, psu_intended.json)
The SMPS modules, mains wiring and the NC7FD-LX output socket are chassis parts wired to the terminals."""
import collections, json, os
from schgen import block, P, build, SYM, FP, MPN

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM.update({'LDO': ('Regulator_Linear', 'LM1084-ADJ'), 'SCR': ('Device', 'Q_SCR_KAG'),
            'TL431': ('Reference_Voltage', 'TL431DBZ'), 'PNP': ('Transistor_BJT', 'MMBT3906'),
            'L': ('Device', 'L'), 'DS': ('Device', 'D_Schottky'), 'DG': ('Device', 'D'),
            'TERM2': ('Connector', 'Screw_Terminal_01x02'), 'TERM7': ('Connector', 'Screw_Terminal_01x07')})
FP.update({'LDO': 'Package_TO_SOT_THT:TO-220-3_Vertical', 'SCR': 'Package_TO_SOT_THT:TO-220-3_Vertical',
           'TL431': 'Package_TO_SOT_SMD:SOT-23', 'PNP': 'Package_TO_SOT_SMD:SOT-23',
           'L': 'Inductor_THT:L_Toroid_Horizontal_D21.8mm_P19.10mm_Bourns_2100',
           'DS': 'Diode_SMD:D_SMC', 'DG': 'Diode_SMD:D_SMA',
           'TERM2': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',
           'TERM7': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-7-5.08_1x07_P5.08mm_Horizontal'})
MPN.update({'LDO': 'TI LM1084IT-ADJ/NOPB', 'SCR': 'onsemi 2N6505G', 'TL431': 'TI TL431AIDBZR', 'PNP': 'onsemi MMBT3906LT1G',
            'L': 'Bourns 2100LL-100-H-RC', 'DS': 'Diodes B540C-13-F (SS54 class, SMC 40 V 5 A)', 'DG': 'Diodes S1G-13-F', 'LED': 'Kingbright WP710A10GD',
            'TERM2': 'Phoenix 1715721 MKDS 1,5/2-5,08', 'TERM7': 'Phoenix 1755897 MKDS 1,5/7-5,08 (to a Neutrik NC7FD-LX)'})
CPFP = {'2200u': 'Capacitor_THT:CP_Radial_D16.0mm_P7.50mm', '220u': 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',
        '47u': 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm'}
CAP_MPN = {'2200u 35V low-ESR': 'Rubycon 35ZLH2200MEFC16X25', '220u 25V': 'Panasonic EEU-FR1E221',
           '47u 25V': 'Rubycon 63ZLH47MEFC6.3X11 (63V)', '100n': 'Samsung CL21B104KBCNNNC (X7R 50V)',
           '2n2': 'KEMET C0805C222J5GACTU (C0G)'}

cnt = collections.Counter()
def ref(p): cnt[p] += 1; return f'{p}{cnt[p]}'
def R(b, v, a, c, **kw): P(b, ref('R'), 'R', v, {1: a, 2: c}, **kw)
def C(b, v, a, c): P(b, ref('C'), 'C', v, {1: a, 2: c}, mpn=CAP_MPN[v])
def CP(b, v, plus, minus): P(b, ref('C'), 'CP', v, {1: plus, 2: minus}, fp=CPFP[v.split()[0]], mpn=CAP_MPN[v])

def rail(name, out, rtn, smps):
    """One floating rail: x = net prefix. OUT and RTN are the rail's own output and return."""
    x = name
    b = block(f'{name} RAIL  {smps} (21.6 V) -> LC -> LM1084-ADJ 17.0 V, soft start;  OUT = {out}, RTN = {rtn}')
    P(b, ref('J'), 'TERM2', f'{smps} DC in', {1: x + '_IN', 2: rtn})
    P(b, ref('L'), 'L', '10u 11A', {1: x + '_IN', 2: x + '_LC'})
    CP(b, '2200u 35V low-ESR', x + '_LC', rtn); C(b, '100n', x + '_LC', rtn)
    P(b, ref('U'), 'LDO', 'LM1084-ADJ', {3: x + '_LC', 2: out, 1: x + '_ADJ'})
    R(b, '120R 1%', out, x + '_ADJ')
    # 15.7 V across the 1K5 = 164 mW: 1206 0.5 W, not the 0805's 125 mW (docs/reviews/project_review.md RV1)
    R(b, '1K5 1%', x + '_ADJ', rtn, fp='Resistor_SMD:R_1206_3216Metric', mpn='Panasonic ERJ-P06F1501V')
    CP(b, '47u 25V', x + '_ADJ', rtn)                                   # soft start (tau ~ 70 ms) + ripple rejection
    P(b, ref('D'), 'DG', 'S1G', {2: x + '_ADJ', 1: out})               # C_ADJ discharge into OUT, not into ADJ
    P(b, ref('D'), 'DG', 'S1G', {2: out, 1: x + '_LC'})                # output caps discharge into VI
    CP(b, '220u 25V', out, rtn); C(b, '100n', out, rtn)
    P(b, ref('D'), 'DS', 'SS54', {1: out, 2: rtn})                     # reverse voltage on the rail
    R(b, '4K7', out, x + '_LA'); P(b, ref('D'), 'LED', f'{name} rail green', {2: x + '_LA', 1: rtn})
    b = block(f'{name} CROWBAR  TL431 at 66K5 / 10K = 19.1 V -> PNP -> SCR gate; SCR 2N6505G across the rail')
    R(b, '66K5 1%', out, x + '_REF'); R(b, '10K 1%', x + '_REF', rtn); C(b, '2n2', x + '_REF', rtn)
    P(b, ref('U'), 'TL431', 'TL431', {1: x + '_K', 2: x + '_REF', 3: rtn})
    R(b, '4K7', out, x + '_PB'); R(b, '1K', x + '_PB', x + '_K')
    P(b, ref('Q'), 'PNP', 'MMBT3906', {1: x + '_PB', 2: out, 3: x + '_GC'})
    R(b, '100R', x + '_GC', x + '_G'); R(b, '1K', x + '_G', rtn)
    P(b, ref('Q'), 'SCR', '2N6505G', {1: rtn, 2: out, 3: x + '_G'})
    return x + '_LC'

lcs = [rail('POS', '+V', '0V', 'LRS-150-24 #1'), rail('NEG', '0V', '-V', 'LRS-150-24 #2')]
b = block('OUTPUT  7-way terminal to the NC7FD-LX on the PSU panel: 1 earth, 2-3 +V, 4-5 0 V, 6-7 -V (0 V not earthed here)')
P(b, ref('J'), 'TERM7', 'Console out (NC7FD-LX)', {1: 'EARTH', 2: '+V', 3: '+V', 4: '0V', 5: '0V', 6: '-V', 7: '-V'})
P(b, ref('J'), 'TERM2', 'Earth stud (case)', {1: 'EARTH', 2: 'EARTH'})
for i, n in enumerate(lcs): P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})

d = json.load(open(os.path.join(ROOT, 'boards', 'master', 'master.kicad_pro')))
d['meta']['filename'] = 'psu.kicad_pro'; d['sheets'] = []
from schgen import keep_net_settings, own_sheet; keep_net_settings(d, os.path.join(ROOT, 'boards', 'psu', 'psu.kicad_pro')); own_sheet(d, 'psu')
with open(os.path.join(ROOT, 'boards', 'psu', 'psu.kicad_pro'), 'w') as f: json.dump(d, f, indent=2); f.write('\n')
build(os.path.join(ROOT, 'boards', 'psu', 'psu.kicad_sch'), 'psu', 'External PSU regulator board - goa console (+-17 V, 4 A per rail)',
      {1: 'Generated by tools/gen_psu.py from psu_spec.md v0.2 (option B)',
       2: 'Two floating rails: LRS-150-24 -> LC -> LM1084-ADJ -> TL431/SCR crowbar'},
      paper='auto', perrow=14, revision='0.2')
