"""Generate the external PSU regulator board schematic (psu_spec.md v0.2, option B): two identical floating
rails, each Mean Well LRS-150-24 (21.6 V) -> LC 10 uH / 2200 uF -> LM1084-ADJ 17.0 V with 47 uF ADJ soft
start -> TL431 / PNP / SCR crowbar at 19.1 V. +V rail: OUT = +V, RTN = 0V; -V rail: OUT = 0V, RTN = -V.
usage: .venv/bin/python tools/gen_psu.py   ->  psu.kicad_sch (+ psu.kicad_pro, psu_intended.json)
The SMPS modules, mains wiring and the NC7FD-LX output socket are chassis parts wired to the terminals."""
import collections, json, os
import schgen
from schgen import block, P, build, SYM, FP, MPN

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM.update({'LDO': ('Regulator_Linear', 'LM1084-ADJ'), 'SCR': ('Device', 'Q_SCR_KAG'),
            'TL431': ('Reference_Voltage', 'TL431DBZ'), 'PNP': ('Transistor_BJT', 'MMBT3906'),
            'L': ('Device', 'L'), 'DS': ('Device', 'D_Schottky'), 'S1G': ('Device', 'D'),
            'TERM2': ('Connector', 'Screw_Terminal_01x02'), 'TERM7': ('Connector', 'Screw_Terminal_01x07'),
            # the three rails as power symbols local to the sheet (goa-console.kicad_sym): the nets stay /+V, /0V, /-V
            '+V': ('goa-console', '+V'), '0V': ('goa-console', '0V'), '-V': ('goa-console', '-V')})
schgen.POWER_SYMBOL_NETS += ('+V', '0V', '-V')
FP.update({'LDO': 'Package_TO_SOT_THT:TO-220-3_Vertical', 'SCR': 'Package_TO_SOT_THT:TO-220-3_Vertical',
           'TL431': 'Package_TO_SOT_SMD:SOT-23', 'PNP': 'Package_TO_SOT_SMD:SOT-23',
           'L': 'Inductor_THT:L_Toroid_Horizontal_D21.8mm_P19.10mm_Bourns_2100',
           'DS': 'Diode_SMD:D_SMC', 'S1G': 'Diode_SMD:D_SMA',
           'TERM2': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',
           'TERM7': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-7-5.08_1x07_P5.08mm_Horizontal'})
MPN.update({'LDO': 'TI LM1084IT-ADJ/NOPB', 'SCR': 'onsemi 2N6505G', 'TL431': 'TI TL431AIDBZR', 'PNP': 'onsemi MMBT3906LT1G',
            'L': 'Bourns 2100LL-100-H-RC', 'DS': 'Diodes B540C-13-F (SS54 class, SMC 40 V 5 A)', 'S1G': 'Diodes S1G-13-F', 'LED': 'Kingbright WP710A10GD',
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
    P(b, ref('D'), 'S1G', 'S1G', {2: x + '_ADJ', 1: out})              # C_ADJ discharge into OUT, not into ADJ
    P(b, ref('D'), 'S1G', 'S1G', {2: out, 1: x + '_LC'})               # output caps discharge into VI
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

# ---------------------------------------------------------------- the drawing
# One wired drawing of all the parts above (their order, references and nets are untouched): the sheet is drawn, not
# laid out in labelled cells. HEAD holds the five block headings as they were: build() writes HEAD[0] over the drawing's
# origin, the drawing places the other four.
HEAD = [t for t, _ in schgen.blocks]
PARTS = [pt for _, ps in schgen.blocks for pt in ps]


# Layout (grid units of 2.54 mm, y down). The two rails are identical rows, the NEG row ROW units under the POS row. A
# row's power path is its line at y = 0: SMPS terminal -> L -> LDO -> output -> riser at XR, which feeds the crowbar bus
# (y = B) and goes on to J3. Tier 1 hangs from the line: upper parts centred at y = 2.5, the nodes between at y = 5, lower
# parts at 8.5, every return symbol at 11. Tier 2 is the crowbar on its bus, its returns at B + 13. J3 / J4 sit between
# the rows at the right: +V comes down to them from the POS row, 0V up from the NEG row.
ROLES = ('J', 'L', 'CIN', 'CINF', 'U', 'RA', 'RB', 'CADJ', 'DADJ', 'DREV', 'COUT', 'COUTF', 'DRV', 'RLED', 'LED',
         'RT', 'RBOT', 'CF', 'TL', 'RBE', 'RK', 'Q', 'RG', 'RGK', 'SCR')      # one rail's parts, in their order above
RAILS = (('POS', '+V', '0V'), ('NEG', '0V', '-V'))                            # name, OUT, RTN: rail() above
Y1, ROW, B = 5, 53, 23          # the POS line under the drawing's origin; NEG line under the POS line; crowbar bus
XR, XN = 69, 71                 # the riser to the crowbar bus (and, in the POS row, down to J3); the NEG row's turn to J3
JX, JY = 79, 28                 # J3, from the POS line
T1 = dict(lin=3, l=8.5, llc=11, flg=15.5, cin=17, cinf=20, adjl=23, u=28, adjr=33, dadj=35, rdiv=39,     # tier-1 columns
          cout=45.5, coutf=52, drv=56.5, led=61)
CB = dict(dv=8, cf=11.5, tl=19, rk=22.5, pb=29, q=37, rg=41.5, g=46.5, scr=56)                   # crowbar columns


def note(d, lines, x, top, size=1.27):
    """A note of one text per line, its first line's top at grid y = top, one grid unit per line."""
    for i, line in enumerate(lines): d.note(line, (x, top + 0.42 + i), size)


# What the wires cannot show, per block (columns under tier 1: entry and LC, LDO, output; under the crowbar: sense,
# SCR). Every figure is from psu_spec.md; answer.md lists the section of each.
NOTES = {
    'POS': (["J1: LRS-150-24 #1 (+ pin 1, - pin 2), set to",
             "21.6 V; 150 mV pk-pk ripple at about 65 kHz;",
             "5.1 A peak at start-up (its limit: >= 6.8 A).",
             "L1 / C1: -47 dB, 0.7 mV pk-pk at the LDO input."],
            ["VO = 1.25 V x (1 + 1K5 / 120R) + 55 uA x 1K5",
             "   = 17.0 V; 120R is also U1's 10 mA minimum load.",
             "C3: soft start: 10 % at 5 ms, 90 % at 165 ms.",
             "D1 / D2 let C3 and C4 discharge around U1.",
             "R2: 1206 0.5 W: 15.7 V across it is 164 mW."],
            ["D3: clamps a reversed rail.",
             "D4 lit: rail up. Flashing: the crowbar has",
             "fired and the SMPS hiccups into the fault."],
            ["Trips at 2.495 V x (1 + 66K5 / 10K) = 19.1 V (18.6-19.9 V worst",
             "case): 2.1 V over the output, 0.9 V under the OPA1612's 20 V abs max.",
             "Running: POS_REF at 2.21 V, the gate never moves. A TL431, not a",
             "zener: the gate's up to 30 mA would move a zener's trip by over 1 V."],
            ["Q2 2N6505G (25 A, 250 A surge) fires 17 us after a shorted",
             "pass element (20.7 V peak at the terminals) and holds the",
             "rail near 1 V; the SMPS hiccups and D4 flashes: switch off",
             "and repair."]),
    'NEG': (["J2: LRS-150-24 #2 (+ pin 1, - pin 2), isolated",
             "from #1: its - output is -V, so this copy of the",
             "POS rail makes 0V, 17.0 V above -V."],
            ["U3 holds 0V at 17.0 V above -V, as U1",
             "holds +V above 0V; U3's tab is at 0V.",
             "R11: 1206 0.5 W, as R2."],
            ["D7: clamps a reversed rail.",
             "D8: as D4."],
            ["Trips when 0V rises 19.1 V above -V: the",
             "POS crowbar's figures, between 0V and -V."],
            ["Q4 fires as Q2 does and holds 0V near 1 V above -V."]),
}


def rail_row(d, k):
    """One rail as a row (k = 0 POS, 1 NEG), drawn from its line at y = 0."""
    name, out, rtn = RAILS[k]
    r = {role: pt['ref'] for role, pt in zip(ROLES, PARTS[25 * k: 25 * k + 25])}
    n = lambda s: f'{name}_{s}'
    on = lambda role, net: (r[role], next(p for p, v in d.nets(r[role]).items() if v == net))     # a pin by its net
    ret = lambda x, y: d.gnd((x, y), rtn)                      # a return symbol, pointing down
    c = T1
    # entry: the SMPS terminal (pins to the right), its return straight down to the row's return level
    d.at(r['J'], 0, 0, mirror='y')
    d.fld(r['J'], ref_at=(-1, 1.5, 'right'), val_at=(-0.6, -1.6, 'left'))
    d.w(on('J', n('IN')), (c['lin'], 0)); d.port(n('IN'), (c['lin'], 0), 'R')
    d.w(on('J', rtn), (4, 1), (4, 11)); ret(4, 11)
    if rtn == '-V':                                            # -V has no driver: its PWR_FLAG where it enters
        d.w((4, 6), (7, 6)); d.flag((7, 6))
    # LC filter; the regulator input's PWR_FLAG where X_LC begins
    d.h(r['L'], c['l'], 0, left=n('IN'), text='D'); d.w((c['lin'], 0), on('L', n('IN')))
    d.w(on('L', n('LC')), (c['llc'], 0)); d.port(n('LC'), (c['llc'], 0), 'R')
    d.w((c['flg'], 0), (c['flg'], -1)); d.at('#FLG%02d' % (k + 1), c['flg'], -1)
    for role, text in (('CIN', 'L'), ('CINF', None)):
        x = c[role.lower()]
        d.v(r[role], x, 8.5, top=n('LC'), text=text); d.w((x, 0), (x, 7)); d.w((x, 10), (x, 11)); ret(x, 11)
    # LDO: the reverse diode over it, C_ADJ under it, D_ADJ and the divider on the output side
    u = c['u']
    d.at(r['U'], u, 0)
    d.w((c['llc'], 0), (c['flg'], 0), (c['cin'], 0), (c['cinf'], 0), (c['adjl'], 0), (r['U'], 3))
    d.h(r['DREV'], u, -4, left=n('LC'), text='U')
    d.w((c['adjl'], 0), (c['adjl'], -4), on('DREV', n('LC'))); d.w(on('DREV', out), (c['adjr'], -4), (c['adjr'], 0))
    d.w((r['U'], 1), (u, 5)); d.v(r['CADJ'], u, 8.5, top=n('ADJ')); d.w((u, 5), (u, 7)); d.w((u, 10), (u, 11)); ret(u, 11)
    d.w((u, 5), (u + 1, 5)); d.port(n('ADJ'), (u + 1, 5), 'R'); d.w((u + 1, 5), (c['dadj'], 5), (c['rdiv'], 5))
    d.v(r['DADJ'], c['dadj'], 2.5, top=out); d.w((c['dadj'], 0), (c['dadj'], 1)); d.w((c['dadj'], 4), (c['dadj'], 5))
    d.v(r['RA'], c['rdiv'], 2.5, top=out); d.w((c['rdiv'], 0), (c['rdiv'], 1)); d.w((c['rdiv'], 4), (c['rdiv'], 5))
    d.v(r['RB'], c['rdiv'], 8.5, top=n('ADJ')); d.w((c['rdiv'], 5), (c['rdiv'], 7)); d.w((c['rdiv'], 10), (c['rdiv'], 11)); ret(c['rdiv'], 11)
    # output: the caps, the reverse Schottky, the rail LED and its resistor
    for role in ('COUT', 'COUTF', 'DRV'):
        x = c[role.lower()]
        d.v(r[role], x, 8.5, top=out); d.w((x, 0), (x, 7)); d.w((x, 10), (x, 11)); ret(x, 11)
    x = c['led']
    d.v(r['RLED'], x, 2.5, top=out); d.w((x, 0), (x, 1)); d.w((x, 4), (x, 5)); d.port(n('LA'), (x, 5), 'R')
    d.v(r['LED'], x, 8.5, top=n('LA')); d.w((x, 5), (x, 7)); d.w((x, 10), (x, 11)); ret(x, 11)
    d.w((r['U'], 2), (c['adjr'], 0), (c['dadj'], 0), (c['rdiv'], 0), (c['cout'], 0), (c['coutf'], 0), (c['drv'], 0), (x, 0), (XR, 0))
    # crowbar on its bus: divider (tap to the left), TL431, PNP, gate drive, SCR across the rail
    d.w((XR, 0), (XR, B))
    dv, cf, tl, rk, pb, q, rg, g, scr = (CB[k_] for k_ in ('dv', 'cf', 'tl', 'rk', 'pb', 'q', 'rg', 'g', 'scr'))
    d.v(r['RT'], dv, B + 2.5, top=out, text='L'); d.w((dv, B), (dv, B + 1)); d.w((dv, B + 4), (dv, B + 7))
    d.v(r['RBOT'], dv, B + 10.5, top=n('REF'), text='L'); d.w((dv, B + 7), (dv, B + 9)); d.w((dv, B + 12), (dv, B + 13)); ret(dv, B + 13)
    d.port(n('REF'), (dv, B + 7), 'L')
    d.v(r['CF'], cf, B + 10.5, top=n('REF')); d.w((cf, B + 7), (cf, B + 9)); d.w((cf, B + 12), (cf, B + 13)); ret(cf, B + 13)
    d.at(r['TL'], tl, B + 7, rot=90)
    d.w((dv, B + 7), (cf, B + 7), (r['TL'], 2))
    d.w((r['TL'], 3), (tl, B + 13)); ret(tl, B + 13)
    d.w((r['TL'], 1), (tl, B + 5)); d.port(n('K'), (tl, B + 5), 'L')
    d.h(r['RK'], rk, B + 5, left=n('K'), text='U'); d.w((tl, B + 5), on('RK', n('K')))
    d.v(r['RBE'], pb, B + 2.5, top=out); d.w((pb, B), (pb, B + 1)); d.w((pb, B + 4), (pb, B + 5))
    d.w(on('RK', n('PB')), (pb, B + 5)); d.port(n('PB'), (pb, B + 5), 'R')
    d.at(r['Q'], q, B + 5, mirror='x'); d.w((pb, B + 5), (r['Q'], 1))
    d.w((r['Q'], 2), (q + 1, B)); d.w((r['Q'], 3), (q + 1, B + 8)); d.port(n('GC'), (q + 1, B + 8), 'L')
    d.h(r['RG'], rg, B + 8, left=n('GC'), text='D'); d.w((q + 1, B + 8), on('RG', n('GC')))
    d.w(on('RG', n('G')), (g, B + 8))
    d.v(r['RGK'], g, B + 10.5, top=n('G')); d.w((g, B + 8), (g, B + 9)); d.w((g, B + 12), (g, B + 13)); ret(g, B + 13)
    d.port(n('G'), (g, B + 8), 'R')
    d.at(r['SCR'], scr, B + 7); d.w((g, B + 8), (r['SCR'], 3))
    d.w((r['SCR'], 1), (scr, B + 13)); ret(scr, B + 13)
    d.w((r['SCR'], 2), (scr, B))
    d.w((dv, B), (pb, B), (q + 1, B), (scr, B), (XR, B))
    d.note(HEAD[2 * k + 1], (0, B - 3), 2.0)
    if k: d.note(HEAD[2], (0, -8.5), 2.0)                     # HEAD[0] is the builder's, over the POS row
    na, nb, nc, nd, ne = NOTES[name]
    note(d, na, -0.5, 12.8); note(d, nb, 23, 12.8); note(d, nc, 45, 12.8)
    note(d, nd, -0.5, B + 14.8); note(d, ne, 33, B + 14.8)


def output(d):
    """J3 between the rows at the right with J4 over it, drawn from the POS line: +V comes down the POS riser past the
    crowbar bus, 0V up from the NEG line, -V by its symbol; EARTH is the labelled wire from J3 pin 1 to J4."""
    px = JX - 2                                                # J3's and J4's pin column
    d.at('J3', JX, JY); d.at('J4', JX, JY - 7)
    d.fld('J3', ref_at=(1.6, -3, 'left'), val_at=(1.6, -2, 'left'))
    d.fld('J4', ref_at=(1.6, 0, 'left'), val_at=(1.6, 1, 'left'))
    d.w((XR, 0), (XR, -1)); d.gnd((XR, -1), '+V', 'U')
    d.w((XR, B), (XR, JY - 2), (px, JY - 2)); d.w((px - 1, JY - 2), (px - 1, JY - 1), (px, JY - 1))
    d.w((XR, ROW), (XN, ROW), (XN, ROW + 1)); d.gnd((XN, ROW + 1), '0V')
    d.w((XN, ROW), (XN, JY + 1), (px, JY + 1)); d.w((px - 1, JY + 1), (px - 1, JY), (px, JY))
    d.w((px, JY + 2), (px - 1, JY + 2), (px - 1, JY + 3)); d.w((px, JY + 3), (px - 1, JY + 3), (px - 1, JY + 5)); d.gnd((px - 1, JY + 5), '-V')
    d.w((px, JY - 3), (px - 2, JY - 3), (px - 2, JY - 7), (px, JY - 7)); d.w((px, JY - 6), (px - 2, JY - 6))
    d.port('EARTH', (px - 2, JY - 7), 'L')
    d.note(HEAD[4], (XN + 1, JY - 10), 2.0)
    d.note('+V = 17.0 V @ (, 3.31, 4.54) A (min, typ, max); 4.54 A is the accepted worst corner; design 4 A per rail.',
           (XR + 3, -1.6), 1.27)
    d.note('0V: the NEG regulator\'s output, 17.0 V above -V.   -V = -17.0 V @ (, 2.79, ) A (min, typ, max); design 4 A.',
           (XN + 3, ROW + 2.2), 1.27)
    note(d, ["J3: to the NC7FD-LX (female) on the PSU panel, each rail on two contacts; cable NC7MX - NC7FX,",
             "   7 x 1.0 mm2, <= 2 m.",
             "0V is not earthed in the PSU: it meets mains earth only at the console's star point.",
             "J4: to the earth stud on the case, where the LRS-150 FG terminals go too; J3 pin 1 takes earth to the console."],
         XN + 1, JY + 7)
    note(d, ["Layout: the 4 A paths (J1 / J2 -> L -> LDO -> J3) want >= 3 mm tracks or pours on both layers.",
             "Heatsink: U1, Q2, U3, Q4 (TO-220) share one, each on a silicone pad and a shoulder washer:",
             "   the tabs sit at +17 V (U1), 0 V (U3) and the rails (SCR anodes). U1 and U3: 19 W each at 4 A,",
             "   12 W typical.",
             "Stacking: the two SMPS outputs are isolated, so both rails are the same positive regulator and",
             "   crowbar: POS OUT = +V over RTN = 0V, NEG OUT = 0V over RTN = -V.",
             "The SMPS modules, the mains wiring, the NC7 socket and the earth stud are chassis parts."],
         XN + 1, ROW + 41)


def draw_sheet(d):
    d.shift(0, Y1)
    rail_row(d, 0)
    output(d)
    d.shift(0, ROW); rail_row(d, 1); d.shift(0, -ROW)
    d.shift(0, -Y1)


schgen.blocks[:] = []
block(HEAD[0], draw_sheet).extend(PARTS)

d = json.load(open(os.path.join(ROOT, 'boards', 'master', 'master.kicad_pro')))
d['meta']['filename'] = 'psu.kicad_pro'; d['sheets'] = []
from schgen import keep_net_settings, own_sheet; keep_net_settings(d, os.path.join(ROOT, 'boards', 'psu', 'psu.kicad_pro')); own_sheet(d, 'psu')
with open(os.path.join(ROOT, 'boards', 'psu', 'psu.kicad_pro'), 'w') as f: json.dump(d, f, indent=2); f.write('\n')
build(os.path.join(ROOT, 'boards', 'psu', 'psu.kicad_sch'), 'psu', 'External PSU regulator board - goa console (+-17 V, 4 A per rail)',
      {1: 'Generated by tools/gen_psu.py from psu_spec.md v0.2 (option B)',
       2: 'Two floating rails: LRS-150-24 -> LC -> LM1084-ADJ -> TL431/SCR crowbar'},
      paper='auto', perrow=14, revision='0.2')
