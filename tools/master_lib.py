"""Shared circuit library for the master-section generators: gen_master.py (the master) and gen_jig.py
(test-jig master stub and load board). Part maps, automatic references, op-amp / comparator unit
allocation with decoupling, and one function per master circuit (spec sections in brackets).
reset() clears the reference counters so one script can build several schematics."""
import collections
import schgen, frags
from schgen import frag
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
MPN.update({'DRV134': 'TI DRV135UA',   # SO-8: the DRV134 is DIP-8 / SOL-16 only (design_review.md R1)
            'RELAY': 'Omron G6K-2F-Y DC12', 'XLR3': 'Neutrik NC3MAH',
            'PWRIN': 'Phoenix 1755897 MKDS 1,5/7-5,08 (wired to a Neutrik NC7MD-LX inlet)', 'PTC': 'Bourns MF-RX160/72-0',
            'DS': 'SS54', 'FB': '220R@100MHz 0805',
            'LME49600': 'TI LME49600TS/NOPB', 'OPA1656': 'TI OPA1656IDR', 'JACK': 'Neutrik NRJ6HF',
            # B grades: the comparators run from +-17 V (34 V), over the non-B parts' 30 V recommended maximum
            'CMP': 'TI LM393BIDR', 'LM2901': 'TI LM2901BIDR',
            'DG': 'Vishay DG413DY-E3', 'ZEN': 'Nexperia BZX84-C5V1,215', 'PNP': 'onsemi BCP53-16T1G', 'SCH': 'Nexperia BAT54W,115',
            # master_group_review.md MG9 / MG16. TL072H: the H suffix fixes the die (SLOS080W Table 9-1) and is rated 42 V
            'OPA': 'TI OPA1612AIDR', 'TL072': 'TI TL072HIDR', 'NPN': 'onsemi MMBT3904LT1G', 'D': 'Vishay 1N4148-TAP',
            'POT': 'Alpha RD901F-40-15R1-A10K', 'HDR': 'Wurth 61203421621 (2x17 box header)',
            # the ferrite is a stability part: the aux summer's margin follows its inductance (MG16)
            'FB': 'Murata BLM21PG221SN1D'})
MPN['DS'] = 'Diodes B540C-13-F (SS54 class, SMC 40 V 5 A)'
# CS10: a reverse Schottky across each audio rail of a ribbon board (group), as the strip's D16 / D17
SYM['DSK'] = ('Device', 'D_Schottky'); FP['DSK'] = 'Diode_SMD:D_SOD-123F'; MPN['DSK'] = 'Nexperia PMEG4010CEH,115'
# CS4b: a BAV199 per jack-link signal at the link header, as the strip's D18-D22 (pin 3 the signal, 2 +VA, 1 -VA)
SYM['DD'] = ('Diode', 'BAV99'); FP['DD'] = 'Package_TO_SOT_SMD:SOT-23'; MPN['DD'] = 'Nexperia BAV199,215'
# wing PTCs MF-RX185/72 (hpf_proposal.md H4, 2026-10-24): same pads as the MF-RX160/72 (kept on the jig stub), a
# 1.24 mm wider body; hold 1.50 / 1.33 A at 40 / 50 C against a 1.25 A wing
PTC185 = dict(fp='goa-console:Fuse_Bourns_MF-RX185-72_Radial_P5.08mm', mpn='Bourns MF-RX185/72-0')
# +V wing PTCs MF-RX250/72 (wing_power_proposal.md W2, 2026-10-25): +V has three ribbon conductors (pin 34, W1), so its
# 2.5 A hold is 0.83 A per IDC contact (1 A rated); 10.2 mm lead spacing, its own footprint. -V keeps the MF-RX185/72.
PTC250 = dict(fp='goa-console:Fuse_Bourns_MF-RX250-72_Radial_P10.16mm', mpn='Bourns MF-RX250/72-0')
# ceramics >= 25 V (50 V X7R; C0G 50 V) and electrolytics that fit the current footprints, filled by value before
# build() (master_group_review.md MG16; strip_parts_review.md T9). Value strings keep the minimum rating
CAP_MPN = {'100n': 'Samsung CL21B104KBCNNNC (X7R 50V)', '1u': 'Samsung CL31B105KBHNNNE (X7R 50V)',
           '2.2u': 'Murata GRM31CR71H225KA88L (X7R 50V)', '330n': 'Samsung CL21B334KBFNNNE (X7R 50V)',
           '10p C0G': 'KEMET C0805C100J5GACTU', '22p C0G': 'KEMET C0805C220J5GACTU',
           '22p C0G 5%': 'KEMET C0805C220J5GACTU', '33p C0G': 'KEMET C0805C330J5GACTU',
           '100p C0G': 'KEMET C0805C101J5GACTU', '1n C0G': 'KEMET C0805C102J5GACTU',
           '470u 25V': 'Nichicon UPW1E471MPD', '1000u 25V': 'Nichicon UPW1E102MHD',
           '47u 25V': 'Nichicon UPW1J470MPD (63V)', '220u 25V': 'Nichicon UHE1V221MPD6 (35V)',
           # 10u NP: DRV135 sense legs (inside its loop) and the LME49600 +-VP bypasses; UES1E100MDM is discontinued
           # (sourcing.md S1, 2026-10-25), so a general-purpose bipolar in the same 5 x 11 / P2.0 can
           '10u NP 25V': 'Panasonic ECE-A1EN100U', '47u NP 25V': 'Panasonic ECE-A1VN470U (35V)',
           '220u NP 25V': 'Panasonic ECE-A1EN221U',
           # film couplers and audio bipolars (film_np_proposal.md): MUSE ES 25 V in the existing footprints
           '2.2u film': 'WIMA MKS2C042201K00KSSD (PET 63V)',
           '33u NP 25V': 'Nichicon UES1E330MPM (MUSE ES)', '100u NP 25V': 'Nichicon UES1E101MPM (MUSE ES)'}
FILM_2U2 = 'Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'          # MKS2 2.2u 63V: 7.2 x 13 x 7.2
NP_VALUE = {'47u NP 25V': '33u NP 25V', '220u NP 25V': '100u NP 25V'}             # MUSE ES 8x11.5 / 10x16 cans
RES_2512 = 'Resistor_SMD:R_2512_6332Metric'
# 3 mm diffused LEDs, Vf <= 2.6 V max (GaP / GaAsP): ten in series must fit a meter string's ~31 V, so no InGaN
LED_MPN = {'green': 'Kingbright WP710A10GD', 'amber': 'Kingbright WP710A10ND', 'red': 'Kingbright WP710A10ID'}
FADER2_FP = 'goa-console:Potentiometer_Bourns_PTB0144_Slide_100mm_Dual'
POT2A_MPN = 'Alpha RD902F-40-15R1-A10K (dual, log)'
NPCAP = {'10u': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm', '22u': 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',
         '47u': CAP_FP['47u'], '220u': CAP_FP['220u'], '470u': 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
         '1000u': 'Capacitor_THT:CP_Radial_D12.5mm_P5.00mm', '1u': 'Capacitor_SMD:C_1206_3216Metric',
         '2.2u': CAP_FP['2.2u']}
NP_FP = {'10u': NPCAP['10u'], '33u': NPCAP['47u'], '100u': NPCAP['220u']}   # MUSE ES in the 47u / 220u footprints

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
        cs = []
        for a, c in (('+' + rail, g), (g, '-' + rail)):
            cr = ref('C'); decoupling[cr] = r; P(b, cr, 'C', '100n', {1: a, 2: c}); cs.append(cr)
        pu = (r, 5 if part == 'LM2901' else 3)
        frag(b, 16, 10, lambda d: frags.power_unit(d, pu, *cs), last=True)
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
LAST = [None]                                           # (ref, unit) of the last amp() / cmp(), for the drawings
def amp(b, inp, inn, out, part='OPA1612', rail='VA'):
    r, u = unit_of(part, rail, b); p, n, o = PINS[u]
    P(b, r, DUAL[part][0], part, {p: inp, n: inn, o: out}, unit=u); LAST[0] = (r, u); return r
def cmp(b, inp, inn, out, part='LM393', rail='VL'):
    r, u = unit_of(part, rail, b); p, n, o = (CPINS if part == 'LM2901' else PINS)[u]
    P(b, r, DUAL[part][0], part, {p: inp, n: inn, o: out}, unit=u); LAST[0] = (r, u); return r

def R(b, v, a, c, **k): r = ref('R'); P(b, r, 'R', v, {1: a, 2: c}, **k); return r
def chain(b, start, elems, end=None, flag=None):
    """Draw a series / shunt line (frags.chain) of parts already created: elems [('s' | 'g', ref)]; flag: a PWR_FLAG
    on the end node."""
    frag(b, frags.chain_w(elems, end is not None), 6, lambda d: frags.chain(d, start, elems, end, flag))
def C(b, v, a, c):
    """A capacitor: '2.2u' is a film coupler, an 'NP' value an audio bipolar (MUSE ES), the rest by value."""
    v = '2.2u film' if v == '2.2u' else NP_VALUE.get(v, v)
    fp = FILM_2U2 if v == '2.2u film' else NP_FP.get(v.split()[0]) if ' NP' in v else NPCAP.get(v.split()[0])
    r = ref('C'); P(b, r, 'C', v, {1: a, 2: c}, fp=fp); return r
def CP(b, v, plus, minus): r = ref('C'); P(b, r, 'CP', v, {1: plus, 2: minus}, fp=NPCAP.get(v.split()[0])); return r
def D(b, anode, cathode, v='1N4148'): r = ref('D'); P(b, r, 'D', v, {2: anode, 1: cathode}); return r

# ---------------------------------------------------------------- circuit blocks (spec sections in brackets)
def summer(b, bus, out, rf, cf, part='OPA1612', gref='GCANCEL'):   # [2, 12, 13, 18]
    n = bus + '_VE'; fb = ref('FB')
    P(b, fb, 'FB', 'Ferrite 220R@100MHz', {1: bus, 2: n})
    u = amp(b, gref, n, out, part); uu = LAST[0]
    rr, cc = R(b, rf + ' 1%', out, n), C(b, cf + ' C0G', out, n)
    for x in (fb, rr, cc): near(x, u)   # summing junction short
    frag(b, 24, 15, lambda d: frags.inv(d, bus, out, uu, fb, rr, cc, gref))
    return u

def reinv(b, src, out, part='OPA1612', gref='GCANCEL_BUF'):  # [3]
    dn, dp = out + '_DN', out + '_DP'
    # the input capacitance against 2K2 leaves ~11 deg phase margin (TI OPA161x model); 22p on both legs, same value
    # and tolerance so the GCANCEL balance holds (master_parts_review.md, item 2). Created first and placed beside
    # the op-amp's pins, ahead of the resistors: they only work at the pins
    cs = C(b, '22p C0G 5%', out, dn), C(b, '22p C0G 5%', dp, 'GNDA')
    k = dict(mpn='Panasonic ERA-6AEB222V')          # 0.1 % 25 ppm: they set the GCANCEL rejection
    rs = (R(b, '2K2 0.1%', src, dn, **k), R(b, '2K2 0.1%', dn, out, **k),
          R(b, '2K2 0.1%', gref, dp, **k), R(b, '2K2 0.1%', dp, 'GNDA', **k))
    u = amp(b, dp, dn, out, part); uu = LAST[0]
    for c in cs: near(c, u)
    frag(b, 30, 18, lambda d: frags.diff(d, src, gref, out, uu, *rs, cs[0], cs[1]))
    return u

def insert(b, src, dst, name):                              # [4]
    s, rr, rt, ri, bf = name + '_SEND', name + '_RETRAW', name + '_RET', name + '_RETIN', name + '_RBUF'
    rs_ = R(b, '75R', src, s, mpn='Panasonic ERJ-P06J750V')       # anti-surge: 258 mW into a shorted send lead
    jack(b, 'JACKSW', name.replace('_', ' ') + ' insert', {'T': s, 'RN': s, 'R': rr, 'TN': 'NC', 'S': 'GNDA'}, split=True)
    cin, rin = C(b, '47u NP 25V', rr, rt), R(b, '47K', rt, 'GNDA')
    # input protection as strip R99/C84, never the 1K alone (it costs the follower 25-45 deg); 75R build-out at the pin:
    # the follower otherwise drives PRE and, at the fader top, the wiper run (master_group_review.md MG7)
    rp = R(b, '1K', rt, ri); ci = C(b, '100p C0G', ri, 'GNDA')
    u = amp(b, ri, bf, bf); uu = LAST[0]
    rbo = R(b, '75R', bf, bf + 'O'); near(ci, u); near(rbo, u)
    c = C(b, '220u NP 25V', bf + 'O', dst); ro = R(b, '47K', dst, 'GNDA'); near(ro, c)
    frag(b, 39, 12, lambda d: frags.insert(d, src, s, rr, dst, rs_, cin, rin, rp, ci, uu, rbo, c, ro))

def post_amp(b, wiper, post, name):                         # [5] fader wiper -> +10 dB -> POST
    fin, fn, fo = name + '_FIN', name + '_FN', name + '_FPOST'
    cin, rsh = C(b, '2.2u', wiper, fin), R(b, '100K', fin, 'GNDA')
    u = amp(b, fin, fn, fo); uu = LAST[0]
    # 10p: the wiper's 1-2.5 kohm against Cdiff; 47R build-out at the pin, outside the loop, so POST's run and the
    # DG413 on-capacitance (master) or the pan pot (group) don't load the follower (master_group_review.md MG4)
    csh, rb = C(b, '10p C0G', fin, 'GNDA'), R(b, '47R', fo, fo + 'O'); near(csh, u); near(rb, u)
    rf, cf, rg = R(b, '4K7', fo, fn), C(b, '100p C0G', fo, fn), R(b, '2K2', fn, 'GNDA')
    cout, rout = C(b, '220u NP 25V', fo + 'O', post), R(b, '47K', post, 'GNDA')
    frag(b, 38, 17, lambda d: frags.noninv(d, wiper, fo, uu, cin, rsh, csh, rf, cf, rg, rb, cout, rout, post))

def level_buffer(b, wiper, out, name, unity=True):          # [13, 16] pot wiper -> buffer, Rg not fitted
    fin, fn = name + '_LIN', name + '_LN'
    cin, rsh = C(b, '2.2u', wiper, fin), R(b, '100K', fin, 'GNDA')
    u = amp(b, fin, fn, out); uu = LAST[0]
    # 100p as post_amp(): without it the follower rings at ~15 MHz (TI OPA161x model). 10p at the + input against
    # the wiper's Cdiff lag; 22p would cost the stage driving the pot top more (master_group_review.md MG5)
    rf, cf, csh = R(b, '4K7', out, fn), C(b, '100p C0G', out, fn), C(b, '10p C0G', fin, 'GNDA')
    for x in (rf, cf, csh): near(x, u)
    rg = R(b, 'DNF (2K2 = +10 dB)', fn, 'GNDA', dnp=True)
    frag(b, 26, 17, lambda d: frags.noninv(d, wiper, out, uu, cin, rsh, csh, rf, cf, rg))

DRV_RX = []                     # CS4c: the resistors inside the DRV135 loops, created last by drv_loop_rs()

def drv134(b, inp, op, on, rx=True):                        # [7]
    """rx (CS4c): a 22R between each output pin and its 10u, inside the Sense loop; created last (drv_loop_rs), so
    every other ref stays. The jig stub passes rx=False."""
    vop, von, u = op + '_VO', on + '_VO', ref('U')
    pp, pn = (op + '_DRV', on + '_DRV') if rx else (vop, von)
    P(b, u, 'DRV134', 'DRV135', {4: inp, 3: 'GNDA', 6: '+VA', 5: '-VA', 8: pp, 1: pn, 7: op, 2: on})
    cs = (C(b, '10u NP 25V', vop, op), C(b, '10u NP 25V', von, on), C(b, '1u', '+VA', 'GNDA'), C(b, '1u', 'GNDA', '-VA'))
    for c in cs: near(c, u)
    rs = []
    if rx: DRV_RX.append((b, u, ((pp, vop), (pn, von)), rs))
    frag(b, 35 if rx else 30, 15, lambda d: frags.drv134(d, inp, op, on, u, *cs, rs=rs))
    return u

def drv_loop_rs():
    """CS4c: create the resistors inside the DRV135 loops (output pin -> 22R -> 10u), anti-surge 0805, each in its
    DRV135's block: an 8 kV discharge on a leg leaves the output pin 0.84 A with the CS4b clamp (5.9 A without). Call
    it last: they take the next free R refs, so every other part keeps its ref."""
    out = []
    while DRV_RX:
        b, u, legs, rs = DRV_RX.pop(0)
        for a, c in legs:
            r = R(b, '22R', a, c, mpn='Panasonic ERJ-P06J220V'); rs.append(r); out.append(r)   # placed by moves alone
    return out

def relay(b, a_in, a_out, b_in, b_out, gnd='GNDA', anchor=None):   # [8] G6K-2F-Y: COM 3/6, NC 2/7, NO 4/5
    """Mute relay: COM to the connector side, NO to the driver (Sense node), NC to ground, so a de-energised relay
    shorts the line to ground instead of leaving it floating. anchor: the driver it sits beside."""
    k = ref('K'); coil = k + '_COIL'
    P(b, k, 'RELAY', 'G6K-2F-Y DC12', {1: coil, 8: 'RLY_DRV', 3: a_out, 4: a_in, 2: gnd, 6: b_out, 5: b_in, 7: gnd})
    rc, df = R(b, '560R', '+VBUS', coil), D(b, 'RLY_DRV', coil); near(rc, k); near(df, k)
    if anchor: near(k, anchor)
    frag(b, 24, 15, lambda d: frags.relay(d, k, rc, df, gnd))
    return k

def routing(b, srcl, srcr, busl, busr, name):               # strip-style routing switch, off grounds the resistor
    sw = ref('SW'); a, c = f'RT_{sw}A', f'RT_{sw}B'
    rl, rr = R(b, '4K7 1%', srcl, a), R(b, '4K7 1%', srcr, c)
    P(b, sw, 'SW', name, {2: a, 1: busl, 3: 'GNDA'}, unit=1)
    P(b, sw, 'SW', name, {5: c, 4: busr, 6: 'GNDA'}, unit=2)
    frag(b, 16, 11, lambda d: frags.routing(d, srcl, srcr, busl, busr, rl, rr, sw))

def afl(b, junction, name):                                 # PFL/AFL switch: 22K (or 43K pair) junction -> PFL bus
    sw = ref('SW'); on, la = f'{sw}_ON', f'{sw}_LA'
    P(b, sw, 'SW', name, {2: junction, 1: 'PFL', 3: 'GNDA'}, unit=1)
    P(b, sw, 'SW', name, {5: '+VL', 4: on, 6: 'NC'}, unit=2)
    rd, rl = R(b, '100K', on, 'PFLDET'), R(b, '4K7', on, la); led = ref('D')
    P(b, led, 'LED', name + ' red', {2: la, 1: 'GNDD'}, mpn=LED_MPN['red'])
    frag(b, 20, 15, lambda d: frags.afl(d, junction, sw, rd, rl, led))

DEFER = []                      # parts created at the end (before the spares): new circuits keep every other ref

def receiver(b, tip, ring, out):                            # strip-style ground-compensated receiver
    """Buffered since 2026-10-25 (ground_study.md G3b, as the strip's U16): each leg 100p and 1M to GNDA, 220R, an
    OPA1656 follower and a 100R build-out (>= 48.5 deg for any load), then the 10K 0.1 % bridge. The followers are
    created last (DEFER), so the refs of everything else on the board stay as they were."""
    n, p = out + '_N', out + '_P'
    ti, ri, to, ro, tb, rb = (out + s for s in ('_TI', '_RI', '_TO', '_RO', '_TB', '_RB'))
    # the 100p sit at the followers' + inputs, after the 220R: there they stop the OPA1656's input capacitance and the
    # 220R from costing the follower ~10 deg (3.3 dB peaking on the fitted model); a 7 MHz RF low-pass as well
    ct, cr, rt = C(b, '100p C0G', ti, 'GNDA'), C(b, '100p C0G', ri, 'GNDA'), R(b, '1M', tip, 'GNDA')
    k = dict(mpn='Panasonic ERA-6AEB103V')          # 0.1 %: they set the CMRR
    r1, r2, cn = R(b, '10K 0.1%', rb, n, **k), R(b, '10K 0.1%', n, out, **k), C(b, '33p C0G', n, out)
    # 33p on the + leg too: with only the feedback cap the bridge is unbalanced (CMRR 60 / 40 / 34 dB at 1 / 10 / 20 kHz)
    # and the 5 kohm + node lags through Cdiff (45 deg); balanced: 86 dB flat, 85 deg (strip_parts_review.md, T3)
    r3, r4, cp = R(b, '10K 0.1%', tb, p, **k), R(b, '10K 0.1%', p, 'GNDA', **k), C(b, '33p C0G', p, 'GNDA')
    u = amp(b, p, n, out); uu = LAST[0]
    near(cn, u); near(cp, u)
    buf = {}
    frag(b, 32, 17, lambda d: frags.rx_buffers(d, tip, ring, tb, rb, buf['ut'], buf['ur'], buf['st'], buf['sr'], rt,
                                               buf['rr'], buf['ot'], buf['or'], ct, cr))
    frag(b, 30, 18, lambda d: frags.diff(d, rb, tb, out, uu, r1, r2, r3, r4, cn, cp, (), c0n=1))
    def late():
        buf['rr'] = R(b, '1M', ring, 'GNDA')
        buf['st'], buf['sr'] = R(b, '220R', tip, ti), R(b, '220R', ring, ri)
        with new_package('OPA1656'):
            amp(b, ti, to, to, 'OPA1656'); buf['ut'] = LAST[0]
            amp(b, ri, ro, ro, 'OPA1656'); buf['ur'] = LAST[0]
        buf['ot'], buf['or'] = R(b, '100R', to, tb), R(b, '100R', ro, rb)
        for x in ('rr', 'st', 'sr', 'ot', 'or'): near(buf[x], buf['ut'][0])
    DEFER.append(late)
    return u

def stereo_in(b, name, outl, outr, label=None):            # two jacks, R normalled to L
    """The outputs must not be named name + '_LR' / '_RR': those are the jack rings (master_group_review.md MG1).
    label: the jacks' value text (default name)."""
    lt, lr, rt, rr = name + '_LT', name + '_LR', name + '_RT', name + '_RR'
    assert not {outl, outr} & {lt, lr, rt, rr}, 'receiver output named like a jack net'
    # sleeves on CHASSIS (ground_study.md G2): cable-shield currents go to the panel, not through GNDA
    # L's own normals short an empty L input (and, through R's normals, an empty R): the 1M bias would hiss (G3b)
    jack(b, 'JACKSW', (label or name) + ' L in', {'T': lt, 'R': lr, 'S': 'CHASSIS', 'TN': 'GNDA', 'RN': 'GNDA'})
    jack(b, 'JACKSW', (label or name) + ' R in', {'T': rt, 'R': rr, 'S': 'CHASSIS', 'TN': lt, 'RN': lr})
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
    from schgen import keep_net_settings; keep_net_settings(d, os.path.join(root, name + '.kicad_pro'))
    with open(os.path.join(root, name + '.kicad_pro'), 'w') as f: json.dump(d, f, indent=2); f.write('\n')

def jack(b, key, value, pins, split=False):
    """A panel jack or XLR: placed on this board, or recorded for the module's jack board. split = give every
    signal its own ground-separated place on the link (insert send and return)."""
    if jackboard is None: P(b, ref('J'), key, value, pins)
    else: jackboard.append(dict(key=key, value=value, pins=pins, split=split))

def link_pins(jacks, ground='GNDA', own_ground=('PHONESGND',), skip=()):
    """IDC pinout for the jack-board link: each jack's signals adjacent, then a ground; a group that carries its
    own signal return (phones) gets none. Ribbon conductor = pin number. skip: nets that stay on the jack board
    (CHASSIS where the standoffs bond it to the panel). Returns (n, {pin: net})."""
    pins, seen = [], set(skip)
    for j in jacks:
        nets = [n for n in j['pins'].values() if n not in ('NC', ground) and n not in seen and not seen.add(n)]
        for g in ([[n] for n in nets] if j['split'] else [nets]):
            if g:
                pins += g
                if not any(n in own_ground for n in g): pins.append(ground)
    n = next(k for k in LINK_SIZES if 2 * k >= len(pins))
    pins += [ground] * (2 * n - len(pins))
    return n, {i + 1: net for i, net in enumerate(pins)}

LINK_GROUNDS = ('GNDA', 'CHASSIS', 'PHONESGND', 'NC')
def link_clamps(b, nets):
    """CS4b: one BAV199 per jack-link signal (pin 3 the signal, pin 2 +VA, pin 1 -VA), each its own fragment. Call it
    last: the clamps take the next free D refs, so every other part keeps its ref."""
    refs = []
    for net in [n for n in nets if n not in LINK_GROUNDS]:
        d_ = ref('D'); P(b, d_, 'DD', 'BAV199', {1: '-VA', 3: net, 2: '+VA'}); refs.append(d_)
        def draw(d, dd=d_, n=net):
            d.at(dd, 4, 3)
            d.w((dd, 1), (1, 1)); d.port('-VA', (1, 1), 'U'); d.w((dd, 2), (7, 1)); d.port('+VA', (7, 1), 'U')
            d.w((dd, 3), (4, 7)); d.port(n, (4, 7), 'D')
        frag(b, 10, 10, draw)
    return refs

def link_header(b, n, link, value):
    SYM[f'LINK{n}'] = ('Connector_Generic', f'Conn_02x{n:02d}_Odd_Even')
    FP[f'LINK{n}'] = f'Connector_IDC:IDC-Header_2x{n:02d}_P2.54mm_Vertical'
    cn = ref('CN'); P(b, cn, f'LINK{n}', value, link, mpn=f'Wurth 6120{2 * n:02d}21621 (2x{n} box header)')
    frag(b, 44, n + 6, lambda d: frags.header(d, cn, 20, n // 2 + 2))

def jack_board(out, project, title, jacks, n, link, holes=0, more=()):
    """Build the jack-board schematic: the collected jacks (NJ6FD-V / NC3MAV, vertical) and the mating link.
    holes: plated M3 standoff holes H1..Hn on CHASSIS (they bond the sleeves' CHASSIS to the panel).
    more: further links, [(n, link, value)], after the first."""
    reset()
    b = block(f'JACK BOARD  panel jacks under the panel (~24 mm deep); 2x{n} IDC ribbon to the main board, pin = conductor')
    for j in jacks:
        P(b, ref('J'), j['key'], j['value'], j['pins'], fp=JB_FP[j['key']], mpn=JB_MPN[j['key']])
    link_header(b, n, link, f'Main board link 2x{n}')
    for n2, link2, value in more: link_header(b, n2, link2, value)
    for i in range(1, holes + 1): P(b, f'H{i}', 'MHPAD', 'M3 standoff to panel', {1: 'CHASSIS'})
    P(b, '#FLG01', 'FLAG', 'PWR_FLAG', {1: 'GNDA'})
    if any('PHONESGND' in j['pins'].values() for j in jacks):         # a power symbol too: driven here as well
        P(b, '#FLG02', 'FLAG', 'PWR_FLAG', {1: 'PHONESGND'})
    project_file(out)
    build(out, project, title, {1: 'Generated with its main board (master_lib.jack_board)', 2: 'Link pinout = main board CN'},
          paper='auto', perrow=12, revision='0.1')

def spares(b):
    """Tie off the unused halves of every partly used package: op-amp as a grounded follower, comparator
    with + to its ground and - to its positive rail (output high, open)."""
    while DEFER: DEFER.pop(0)()                       # the deferred circuits first (receiver followers)
    for (part, rail), units in free.items():
        for r, u in units:
            g = GND_OF[rail]
            if part in ('LM393', 'LM2901'):
                p, n, o = (CPINS if part == 'LM2901' else PINS)[u]
                P(b, r, DUAL[part][0], part, {p: g, n: '+' + rail, o: 'NC'}, unit=u)
            else:
                p, n, o = PINS[u]
                P(b, r, DUAL[part][0], part, {p: g, n: f'{r}_SPARE{u}', o: f'{r}_SPARE{u}'}, unit=u)
                frag(b, 14, 8, lambda d, ru=(r, u): frags.spare(d, ru), last=True)
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
    schgen.blocks.clear(); cnt.clear(); free.clear(); decoupling.clear(); DEFER.clear(); DRV_RX.clear(); jackboard = None
