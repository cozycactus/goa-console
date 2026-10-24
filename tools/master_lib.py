"""Shared circuit library for the master-section generators: gen_master.py (the master) and gen_jig.py
(test-jig master stub and load board). Part maps, automatic references, op-amp / comparator unit
allocation with decoupling, and one function per master circuit (spec sections in brackets).
reset() clears the reference counters so one script can build several schematics."""
import collections
import schgen
from schgen import block, P, build, SYM, FP, MPN, CAP_FP, FADER_FP

# ---------------------------------------------------------------- extra parts for the master
SYM.update({
 'OPA1656': ('Amplifier_Operational', 'OPA1656ID'), 'TL072': ('Amplifier_Operational', 'TL072'),
 'LM2901': ('Comparator', 'LM2901'), 'LME49600': ('Amplifier_Audio', 'LME49600'),
 'DRV134': ('goa-console', 'DRV134'), 'RELAY': ('Relay', 'G6K-2'),
 'XLR3': ('Connector_Audio', 'XLR3'), 'PWRIN': ('Connector', 'Screw_Terminal_01x07'),
 'FB': ('Device', 'FerriteBead'), 'PTC': ('Device', 'Polyfuse'), 'DS': ('Device', 'D_Schottky'),
 'DZ': ('Device', 'D_Zener'), 'NPN': ('Transistor_BJT', 'MMBT3904'), 'PNP': ('Transistor_BJT', 'BCP53'),
 'TRIM': ('Device', 'R_Potentiometer_Trim'), 'HDR5': ('Connector_Generic', 'Conn_01x05'),
 'DG': ('Analog_Switch', 'DG413xY'), 'ZEN': ('Diode', 'BZX84Cxx'), 'SCH': ('Diode', 'BAT54W'),
})
FP.update({
 'OPA1656': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'TL072': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
 'LM2901': 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'DRV134': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
 'RELAY': 'Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y', 'XLR3': 'Connector_Audio:Jack_XLR_Neutrik_NC3MAH_Horizontal',
 'PWRIN': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-7-5.08_1x07_P5.08mm_Horizontal',
 'FB': 'Inductor_SMD:L_0805_2012Metric',
 'PTC': 'goa-console:Fuse_Bourns_MF-RX160-72_Radial_P5.08mm', 'DS': 'Diode_SMD:D_SMC',
 'DZ': 'Diode_SMD:D_SOD-123', 'TRIM': 'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',
 'HDR5': 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical', 'JACK': FP['JACKSW'],
 'PNP': 'Package_TO_SOT_SMD:SOT-223',     # pads 1-4 = the BCEC symbol's pins (tab = 4 = C); TabPin2 has no pad 4
})
MPN.update({'DRV134': 'TI DRV134UA', 'RELAY': 'Omron G6K-2F-Y DC12', 'XLR3': 'Neutrik NC3MAH',
            'PWRIN': 'Phoenix MKDS 1,5/7-5,08 (wired to a Neutrik NC7MD-LX inlet)', 'PTC': 'Bourns MF-RX160/72',
            'DS': 'SS54', 'FB': '220R@100MHz 0805',
            'LME49600': 'TI LME49600TS', 'OPA1656': 'TI OPA1656ID', 'JACK': 'Neutrik NRJ6HF',
            # B grades: the comparators run from +-17 V (34 V), over the non-B parts' 30 V recommended maximum
            'CMP': 'TI LM393BIDR', 'LM2901': 'TI LM2901BIDR',
            'DG': 'Vishay DG413DY-E3', 'ZEN': 'Nexperia BZX84-C5V1,215', 'PNP': 'onsemi BCP53-16T1G', 'SCH': 'Nexperia BAT54W',
            # master_group_review.md MG9 / MG16. TL072H: the H suffix fixes the die (SLOS080W Table 9-1) and is rated 42 V
            'OPA': 'TI OPA1612AIDR', 'TL072': 'TI TL072HIDR', 'NPN': 'onsemi MMBT3904LT1G', 'D': 'Vishay 1N4148-TAP',
            'POT': 'Alpha RD901F-40-15R1-A10K', 'HDR': 'Wurth 61203421621 (2x17 box header)',
            # the ferrite is a stability part: the aux summer's margin follows its inductance (MG16)
            'FB': 'Murata BLM21PG221SN1D'})
MPN['DS'] = 'onsemi SS54'
# ceramics >= 25 V (50 V X7R; C0G 50 V) and electrolytics that fit the current footprints, filled by value before
# build() (master_group_review.md MG16; strip_parts_review.md T9). Value strings keep the minimum rating
CAP_MPN = {'100n': 'Samsung CL21B104KBCNNNC (X7R 50V)', '1u': 'Samsung CL31B105KBHNNNE (X7R 50V)',
           '2.2u': 'Murata GRM31CR71H225KA88L (X7R 50V)', '330n': 'Samsung CL21B334KBFNNNE (X7R 50V)',
           '10p C0G': 'KEMET C0805C100J5GACTU', '22p C0G': 'KEMET C0805C220J5GACTU',
           '22p C0G 5%': 'KEMET C0805C220J5GACTU', '33p C0G': 'KEMET C0805C330J5GACTU',
           '100p C0G': 'KEMET C0805C101J5GACTU', '1n C0G': 'KEMET C0805C102J5GACTU',
           '470u 25V': 'Nichicon UPW1E471MPD', '1000u 25V': 'Nichicon UPW1E102MHD',
           '47u 25V': 'Nichicon UPW1J470MPD (63V)', '220u 25V': 'Nichicon UPW1V221MPD (35V)',
           '10u NP 25V': 'Panasonic ECE-A1EN100U', '47u NP 25V': 'Panasonic ECE-A1VN470U (35V)',
           '220u NP 25V': 'Panasonic ECE-A1EN221U'}
RES_2512 = 'Resistor_SMD:R_2512_6332Metric'
# 3 mm diffused LEDs, Vf <= 2.6 V max (GaP / GaAsP): ten in series must fit a meter string's ~31 V, so no InGaN
LED_MPN = {'green': 'Kingbright WP710A10GD', 'amber': 'Kingbright WP710A10ND', 'red': 'Kingbright WP710A10ID'}
FADER2_FP = 'goa-console:Potentiometer_Bourns_PTB0144_Slide_100mm_Dual'
POT2A_MPN = 'Alpha RD902F-40-15R1-A10K (dual, log)'
NPCAP = {'10u': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm', '22u': 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',
         '47u': CAP_FP['47u'], '220u': CAP_FP['220u'], '470u': 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
         '1000u': 'Capacitor_THT:CP_Radial_D12.5mm_P5.00mm', '1u': 'Capacitor_SMD:C_1206_3216Metric',
         '2.2u': CAP_FP['2.2u']}

# ---------------------------------------------------------------- reference and unit allocation
cnt = collections.Counter()
def ref(prefix): cnt[prefix] += 1; return f'{prefix}{cnt[prefix]}'

GND_OF = {'VA': 'GNDA', 'VP': 'GNDA', 'VM': 'GNDM', 'VL': 'GNDD'}
DUAL = {'OPA1612': ('OPA', 2), 'OPA1656': ('OPA1656', 2), 'TL072': ('TL072', 2), 'LM393': ('CMP', 2), 'LM2901': ('LM2901', 4)}
free = {}
decoupling = {}                 # cap ref -> IC ref, for placement beside the IC
def unit_of(part, rail, b):
    """Next free unit of a multi-unit IC on the given rail; a new package brings power and decoupling."""
    key = (part, rail)
    if not free.get(key):
        k, n = DUAL[part]
        r = ref('U'); free[key] = [(r, u) for u in range(1, n + 1)]
        g = GND_OF[rail]
        if part == 'LM2901': P(b, r, k, part, {3: '+' + rail, 12: '-' + rail}, unit=5)
        else: P(b, r, k, part, {8: '+' + rail, 4: '-' + rail}, unit=3)
        for a, c in (('+' + rail, g), (g, '-' + rail)):
            cr = ref('C'); decoupling[cr] = r; P(b, cr, 'C', '100n', {1: a, 2: c})
    return free[key].pop(0)

class new_package:
    """with new_package(): amp() calls inside start a fresh package, so a pair that belongs together on the board
    (the two fader post-amps) shares one; the free units held back meanwhile are used first afterwards."""
    def __init__(self, part='OPA1612', rail='VA'): self.key = (part, rail)
    def __enter__(self): self.held = free.pop(self.key, [])
    def __exit__(self, *exc): free[self.key] = self.held + free.get(self.key, [])

def near(part, anchor):
    """Place part beside anchor (written to <name>_parts.json with the decouplers, read by the placement layouts)."""
    decoupling[part] = anchor

PINS = {1: (3, 2, 1), 2: (5, 6, 7)}                    # op-amp unit: (+, -, out)
CPINS = {1: (5, 4, 2), 2: (7, 6, 1), 3: (11, 10, 13), 4: (9, 8, 14)}   # LM2901 unit: (+, -, out)
def amp(b, inp, inn, out, part='OPA1612', rail='VA'):
    r, u = unit_of(part, rail, b); p, n, o = PINS[u]
    P(b, r, DUAL[part][0], part, {p: inp, n: inn, o: out}, unit=u); return r
def cmp(b, inp, inn, out, part='LM393', rail='VL'):
    r, u = unit_of(part, rail, b); p, n, o = (CPINS if part == 'LM2901' else PINS)[u]
    P(b, r, DUAL[part][0], part, {p: inp, n: inn, o: out}, unit=u); return r

def R(b, v, a, c, **k): r = ref('R'); P(b, r, 'R', v, {1: a, 2: c}, **k); return r
def C(b, v, a, c): r = ref('C'); P(b, r, 'C', v, {1: a, 2: c}, fp=NPCAP.get(v.split()[0])); return r
def CP(b, v, plus, minus): r = ref('C'); P(b, r, 'CP', v, {1: plus, 2: minus}, fp=NPCAP.get(v.split()[0])); return r
def D(b, anode, cathode, v='1N4148'): r = ref('D'); P(b, r, 'D', v, {2: anode, 1: cathode}); return r

# ---------------------------------------------------------------- circuit blocks (spec sections in brackets)
def summer(b, bus, out, rf, cf, part='OPA1612', gref='GCANCEL'):   # [2, 12, 13, 18]
    n = bus + '_VE'; fb = ref('FB')
    P(b, fb, 'FB', 'Ferrite 220R@100MHz', {1: bus, 2: n})
    u = amp(b, gref, n, out, part)
    for x in (fb, R(b, rf + ' 1%', out, n), C(b, cf + ' C0G', out, n)): near(x, u)   # summing junction short
    return u

def reinv(b, src, out, part='OPA1612', gref='GCANCEL_BUF'):  # [3]
    dn, dp = out + '_DN', out + '_DP'
    # the input capacitance against 2K2 leaves ~11 deg phase margin (TI OPA161x model); 22p on both legs, same value
    # and tolerance so the GCANCEL balance holds (master_parts_review.md, item 2). Created first and placed beside
    # the op-amp's pins, ahead of the resistors: they only work at the pins
    cs = C(b, '22p C0G 5%', out, dn), C(b, '22p C0G 5%', dp, 'GNDA')
    k = dict(mpn='Panasonic ERA-6AEB222V')          # 0.1 % 25 ppm: they set the GCANCEL rejection
    R(b, '2K2 0.1%', src, dn, **k); R(b, '2K2 0.1%', dn, out, **k)
    R(b, '2K2 0.1%', gref, dp, **k); R(b, '2K2 0.1%', dp, 'GNDA', **k)
    u = amp(b, dp, dn, out, part)
    for c in cs: near(c, u)
    return u

def insert(b, src, dst, name):                              # [4]
    s, rr, rt, ri, bf = name + '_SEND', name + '_RETRAW', name + '_RET', name + '_RETIN', name + '_RBUF'
    R(b, '75R', src, s, mpn='Panasonic ERJ-P06J750V')       # anti-surge: 258 mW into a shorted send lead
    jack(b, 'JACKSW', name.replace('_', ' ') + ' insert', {'T': s, 'RN': s, 'R': rr, 'TN': 'NC', 'S': 'GNDA'}, split=True)
    C(b, '47u NP 25V', rr, rt); R(b, '47K', rt, 'GNDA')
    # input protection as strip R99/C84, never the 1K alone (it costs the follower 25-45 deg); 75R build-out at the pin:
    # the follower otherwise drives PRE and, at the fader top, the wiper run (master_group_review.md MG7)
    R(b, '1K', rt, ri); ci = C(b, '100p C0G', ri, 'GNDA')
    u = amp(b, ri, bf, bf)
    near(ci, u); near(R(b, '75R', bf, bf + 'O'), u)
    c = C(b, '220u NP 25V', bf + 'O', dst); near(R(b, '47K', dst, 'GNDA'), c)

def post_amp(b, wiper, post, name):                         # [5] fader wiper -> +10 dB -> POST
    fin, fn, fo = name + '_FIN', name + '_FN', name + '_FPOST'
    C(b, '2.2u', wiper, fin); R(b, '100K', fin, 'GNDA')
    u = amp(b, fin, fn, fo)
    # 10p: the wiper's 1-2.5 kohm against Cdiff; 47R build-out at the pin, outside the loop, so POST's run and the
    # DG413 on-capacitance (master) or the pan pot (group) don't load the follower (master_group_review.md MG4)
    near(C(b, '10p C0G', fin, 'GNDA'), u); near(R(b, '47R', fo, fo + 'O'), u)
    R(b, '4K7', fo, fn); C(b, '100p C0G', fo, fn); R(b, '2K2', fn, 'GNDA')
    C(b, '220u NP 25V', fo + 'O', post); R(b, '47K', post, 'GNDA')

def level_buffer(b, wiper, out, name, unity=True):          # [13, 16] pot wiper -> buffer, Rg not fitted
    fin, fn = name + '_LIN', name + '_LN'
    C(b, '2.2u', wiper, fin); R(b, '100K', fin, 'GNDA')
    u = amp(b, fin, fn, out)
    # 100p as post_amp(): without it the follower rings at ~15 MHz (TI OPA161x model). 10p at the + input against
    # the wiper's Cdiff lag; 22p would cost the stage driving the pot top more (master_group_review.md MG5)
    for x in (R(b, '4K7', out, fn), C(b, '100p C0G', out, fn), C(b, '10p C0G', fin, 'GNDA')): near(x, u)
    R(b, 'DNF (2K2 = +10 dB)', fn, 'GNDA', dnp=True)

def drv134(b, inp, op, on):                                 # [7]
    vop, von, u = op + '_VO', on + '_VO', ref('U')
    P(b, u, 'DRV134', 'DRV134', {4: inp, 3: 'GNDA', 6: '+VA', 5: '-VA', 8: vop, 1: von, 7: op, 2: on})
    for c in (C(b, '10u NP 25V', vop, op), C(b, '10u NP 25V', von, on), C(b, '1u', '+VA', 'GNDA'), C(b, '1u', 'GNDA', '-VA')):
        near(c, u)
    return u

def relay(b, a_in, a_out, b_in, b_out, gnd='GNDA', anchor=None):   # [8] G6K-2F-Y: COM 3/6, NC 2/7, NO 4/5
    """Mute relay: COM to the connector side, NO to the driver (Sense node), NC to ground, so a de-energised relay
    shorts the line to ground instead of leaving it floating. anchor: the driver it sits beside."""
    k = ref('K'); coil = k + '_COIL'
    P(b, k, 'RELAY', 'G6K-2F-Y DC12', {1: coil, 8: 'RLY_DRV', 3: a_out, 4: a_in, 2: gnd, 6: b_out, 5: b_in, 7: gnd})
    near(R(b, '560R', '+VBUS', coil), k); near(D(b, 'RLY_DRV', coil), k)
    if anchor: near(k, anchor)
    return k

def routing(b, srcl, srcr, busl, busr, name):               # strip-style routing switch, off grounds the resistor
    sw = ref('SW'); a, c = f'RT_{sw}A', f'RT_{sw}B'
    R(b, '4K7 1%', srcl, a); R(b, '4K7 1%', srcr, c)
    P(b, sw, 'SW', name, {2: a, 1: busl, 3: 'GNDA'}, unit=1)
    P(b, sw, 'SW', name, {5: c, 4: busr, 6: 'GNDA'}, unit=2)

def afl(b, junction, name):                                 # PFL/AFL switch: 22K (or 43K pair) junction -> PFL bus
    sw = ref('SW'); on, la = f'{sw}_ON', f'{sw}_LA'
    P(b, sw, 'SW', name, {2: junction, 1: 'PFL', 3: 'GNDA'}, unit=1)
    P(b, sw, 'SW', name, {5: '+VL', 4: on, 6: 'NC'}, unit=2)
    R(b, '100K', on, 'PFLDET'); R(b, '4K7', on, la)
    P(b, ref('D'), 'LED', name + ' red', {2: la, 1: 'GNDD'}, mpn=LED_MPN['red'])

def receiver(b, tip, ring, out):                            # strip-style ground-compensated receiver
    n, p = out + '_N', out + '_P'
    C(b, '100p C0G', tip, 'GNDA'); C(b, '100p C0G', ring, 'GNDA'); R(b, '1M', tip, 'GNDA')
    k = dict(mpn='Panasonic ERA-6AEB103V')          # 0.1 %: they set the CMRR
    R(b, '10K 0.1%', ring, n, **k); R(b, '10K 0.1%', n, out, **k); cn = C(b, '33p C0G', n, out)
    # 33p on the + leg too: with only the feedback cap the bridge is unbalanced (CMRR 60 / 40 / 34 dB at 1 / 10 / 20 kHz)
    # and the 5 kohm + node lags through Cdiff (45 deg); balanced: 86 dB flat, 85 deg (strip_parts_review.md, T3)
    R(b, '10K 0.1%', tip, p, **k); R(b, '10K 0.1%', p, 'GNDA', **k); cp = C(b, '33p C0G', p, 'GNDA')
    u = amp(b, p, n, out)
    near(cn, u); near(cp, u)
    return u

def stereo_in(b, name, outl, outr):                         # two jacks, R normalled to L
    """The outputs must not be named name + '_LR' / '_RR': those are the jack rings (master_group_review.md MG1)."""
    lt, lr, rt, rr = name + '_LT', name + '_LR', name + '_RT', name + '_RR'
    assert not {outl, outr} & {lt, lr, rt, rr}, 'receiver output named like a jack net'
    jack(b, 'JACKSW', name + ' L in', {'T': lt, 'R': lr, 'S': 'GNDA', 'TN': 'NC', 'RN': 'NC'})
    jack(b, 'JACKSW', name + ' R in', {'T': rt, 'R': rr, 'S': 'GNDA', 'TN': lt, 'RN': lr})
    return receiver(b, lt, lr, outl), receiver(b, rt, rr, outr)

# ---------------------------------------------------------------- jack boards
# A 1/4" jack or an XLR needs ~25 mm behind a panel parallel to the board, so a module's panel connectors sit
# on a jack board under the panel, joined to the main board by an IDC ribbon (as the strip, spec 16.4).
jackboard = None                # None: jacks go on this board; a list: they are collected for the jack board
LINK_SIZES = (5, 8, 10, 13, 20)  # 2 x n IDC headers; never 2 x 17, the bus ribbon's size
JB_FP = {'JACK': 'Connector_Audio:Jack_6.35mm_Neutrik_NJ6FD-V_Vertical',
         'JACKSW': 'Connector_Audio:Jack_6.35mm_Neutrik_NJ6FD-V_Vertical',
         'XLR3': 'Connector_Audio:Jack_XLR_Neutrik_NC3MAV_Vertical'}
JB_MPN = {'JACK': 'Neutrik NJ6FD-V', 'JACKSW': 'Neutrik NJ6FD-V', 'XLR3': 'Neutrik NC3MAV'}

def collect_jacks():
    """From now on, jacks are recorded for a jack board instead of being placed (reset() turns this off)."""
    global jackboard
    jackboard = []

def collected(): return list(jackboard or [])

def project_file(out):
    """A .kicad_pro next to a generated schematic (settings from master.kicad_pro), so ERC uses them."""
    import json, os
    root, name = os.path.dirname(os.path.abspath(out)), os.path.splitext(os.path.basename(out))[0]
    d = json.load(open(os.path.join(root, 'master.kicad_pro')))
    d['meta']['filename'] = name + '.kicad_pro'; d['sheets'] = []
    with open(os.path.join(root, name + '.kicad_pro'), 'w') as f: json.dump(d, f, indent=2); f.write('\n')

def jack(b, key, value, pins, split=False):
    """A panel jack or XLR: placed on this board, or recorded for the module's jack board. split = give every
    signal its own ground-separated place on the link (insert send and return)."""
    if jackboard is None: P(b, ref('J'), key, value, pins)
    else: jackboard.append(dict(key=key, value=value, pins=pins, split=split))

def link_pins(jacks, ground='GNDA', own_ground=('PHONESGND',)):
    """IDC pinout for the jack-board link: each jack's signals adjacent, then a ground; a group that carries its
    own signal return (phones) gets none. Ribbon conductor = pin number. Returns (n, {pin: net})."""
    pins, seen = [], set()
    for j in jacks:
        nets = [n for n in j['pins'].values() if n not in ('NC', ground) and n not in seen and not seen.add(n)]
        for g in ([[n] for n in nets] if j['split'] else [nets]):
            if g:
                pins += g
                if not any(n in own_ground for n in g): pins.append(ground)
    n = next(k for k in LINK_SIZES if 2 * k >= len(pins))
    pins += [ground] * (2 * n - len(pins))
    return n, {i + 1: net for i, net in enumerate(pins)}

def link_header(b, n, link, value):
    SYM[f'LINK{n}'] = ('Connector_Generic', f'Conn_02x{n:02d}_Odd_Even')
    FP[f'LINK{n}'] = f'Connector_IDC:IDC-Header_2x{n:02d}_P2.54mm_Vertical'
    P(b, ref('CN'), f'LINK{n}', value, link, mpn=f'Wurth 6120{2 * n:02d}21621 (2x{n} box header)')

def jack_board(out, project, title, jacks, n, link):
    """Build the jack-board schematic: the collected jacks (NJ6FD-V / NC3MAV, vertical) and the mating link."""
    reset()
    b = block(f'JACK BOARD  panel jacks under the panel (~24 mm deep); 2x{n} IDC ribbon to the main board, pin = conductor')
    for j in jacks:
        P(b, ref('J'), j['key'], j['value'], j['pins'], fp=JB_FP[j['key']], mpn=JB_MPN[j['key']])
    link_header(b, n, link, f'Main board link 2x{n}')
    P(b, '#FLG01', 'FLAG', 'PWR_FLAG', {1: 'GNDA'})
    project_file(out)
    build(out, project, title, {1: 'Generated with its main board (master_lib.jack_board)', 2: 'Link pinout = main board CN'},
          paper='auto', perrow=12, revision='0.1')

def spares(b):
    """Tie off the unused halves of every partly used package: op-amp as a grounded follower, comparator
    with + to its ground and - to its positive rail (output high, open)."""
    for (part, rail), units in free.items():
        for r, u in units:
            g = GND_OF[rail]
            if part in ('LM393', 'LM2901'):
                p, n, o = (CPINS if part == 'LM2901' else PINS)[u]
                P(b, r, DUAL[part][0], part, {p: g, n: '+' + rail, o: 'NC'}, unit=u)
            else:
                p, n, o = PINS[u]
                P(b, r, DUAL[part][0], part, {p: g, n: f'{r}_SPARE{u}', o: f'{r}_SPARE{u}'}, unit=u)
        units.clear()

def fill_mpns():
    """Capacitor MPNs by value for every C / CP still without one (the unit_of() decouplers included)."""
    for _, ps in schgen.blocks:
        for pt in ps:
            if pt['key'] in ('C', 'CP') and not pt['mpn']: pt['mpn'] = CAP_MPN.get(pt['value'], '')

def parts_sidecar(out):
    """Functional blocks (creation order) and decoupling pairs beside a schematic, as <name>_parts.json, for the
    placement layouts (KiCad's Python can't import the generators). Call before build(); fills the capacitor MPNs."""
    import json, os
    fill_mpns()
    blocks = []
    for t, ps in schgen.blocks:
        order = {}
        for i, p in enumerate(ps): order.setdefault(p['ref'], i)
        blocks.append([t, sorted({p['ref'] for p in ps if not p['ref'].startswith('#')}, key=order.get)])
    with open(os.path.splitext(os.path.abspath(out))[0] + '_parts.json', 'w') as f:
        json.dump({'blocks': blocks, 'near': dict(decoupling)}, f, indent=1)

def reset():
    """Start a new schematic: empty block list, references from 1, no half-used packages."""
    global jackboard
    schgen.blocks.clear(); cnt.clear(); free.clear(); decoupling.clear(); jackboard = None
