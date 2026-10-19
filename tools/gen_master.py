"""Generate the master-section schematic from master_section_spec.md v0.5.
Same builder as the strip (schgen.py). References are assigned automatically; dual op-amps and
comparators are allocated unit by unit, and each new package gets its power unit and decoupling."""
import sys, collections
import schgen
from schgen import block, P, build, SYM, FP, MPN, CAP_FP, FADER_FP

OUT = sys.argv[1] if len(sys.argv) > 1 else 'master.kicad_sch'

# ---------------------------------------------------------------- extra parts for the master
SYM.update({
 'OPA1656': ('Amplifier_Operational', 'OPA1656ID'), 'TL072': ('Amplifier_Operational', 'TL072'),
 'LM2901': ('Comparator', 'LM2901'), 'LME49600': ('Amplifier_Audio', 'LME49600'),
 'DRV134': ('goa-console', 'DRV134'), 'RELAY': ('Relay', 'G6K-2'),
 'XLR3': ('Connector_Audio', 'XLR3'), 'XLR5': ('Connector_Audio', 'XLR5'),
 'FB': ('Device', 'FerriteBead'), 'PTC': ('Device', 'Polyfuse'), 'DS': ('Device', 'D_Schottky'),
 'DZ': ('Device', 'D_Zener'), 'NPN': ('Transistor_BJT', 'MMBT3904'), 'PNP': ('Transistor_BJT', 'MMBT3906'),
 'TRIM': ('Device', 'R_Potentiometer_Trim'), 'HDR5': ('Connector_Generic', 'Conn_01x05'),
})
FP.update({
 'OPA1656': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'TL072': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
 'LM2901': 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'DRV134': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
 'RELAY': 'Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y', 'XLR3': 'Connector_Audio:Jack_XLR_Neutrik_NC3MAH_Horizontal',
 'XLR5': 'Connector_Audio:Jack_XLR_Neutrik_NC5MAH_Horizontal', 'FB': 'Inductor_SMD:L_0805_2012Metric',
 'PTC': 'goa-console:Fuse_Bourns_MF-R075_Radial_P5.08mm', 'DS': 'Diode_SMD:D_SMC',
 'DZ': 'Diode_SMD:D_SOD-123', 'TRIM': 'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',
 'HDR5': 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical', 'JACK': FP['JACKSW'],
})
MPN.update({'DRV134': 'TI DRV134UA', 'RELAY': 'Omron G6K-2F-Y DC12', 'XLR3': 'Neutrik NC3MAH',
            'XLR5': 'Neutrik NC5MAH', 'PTC': 'Bourns MF-R075', 'DS': 'SS54', 'FB': '220R@100MHz 0805',
            'LME49600': 'TI LME49600TS', 'OPA1656': 'TI OPA1656ID', 'JACK': 'Neutrik NRJ6HF'})
FADER2_FP = 'goa-console:Potentiometer_Bourns_PTB0144_Slide_100mm_Dual'
POT2A_MPN = 'Alpha RD902F-40 A10K'
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
def unit_of(part, rail, b):
    """Next free unit of a multi-unit IC on the given rail; a new package brings power and decoupling."""
    key = (part, rail)
    if not free.get(key):
        k, n = DUAL[part]
        r = ref('U'); free[key] = [(r, u) for u in range(1, n + 1)]
        g = GND_OF[rail]
        if part == 'LM2901': P(b, r, k, part, {3: '+' + rail, 12: '-' + rail}, unit=5)
        else: P(b, r, k, part, {8: '+' + rail, 4: '-' + rail}, unit=3)
        P(b, ref('C'), 'C', '100n', {1: '+' + rail, 2: g}); P(b, ref('C'), 'C', '100n', {1: g, 2: '-' + rail})
    return free[key].pop(0)

PINS = {1: (3, 2, 1), 2: (5, 6, 7)}                    # op-amp unit: (+, -, out)
CPINS = {1: (5, 4, 2), 2: (7, 6, 1), 3: (11, 10, 13), 4: (9, 8, 14)}   # LM2901 unit: (+, -, out)
def amp(b, inp, inn, out, part='OPA1612', rail='VA'):
    r, u = unit_of(part, rail, b); p, n, o = PINS[u]
    P(b, r, DUAL[part][0], part, {p: inp, n: inn, o: out}, unit=u)
def cmp(b, inp, inn, out, part='LM393', rail='VL'):
    r, u = unit_of(part, rail, b); p, n, o = (CPINS if part == 'LM2901' else PINS)[u]
    P(b, r, DUAL[part][0], part, {p: inp, n: inn, o: out}, unit=u)

def R(b, v, a, c, **k): P(b, ref('R'), 'R', v, {1: a, 2: c}, **k)
def C(b, v, a, c): P(b, ref('C'), 'C', v, {1: a, 2: c}, fp=NPCAP.get(v.split()[0]))
def CP(b, v, plus, minus): P(b, ref('C'), 'CP', v, {1: plus, 2: minus}, fp=NPCAP.get(v.split()[0]))
def D(b, anode, cathode, v='1N4148'): P(b, ref('D'), 'D', v, {2: anode, 1: cathode})

# ---------------------------------------------------------------- circuit blocks (spec sections in brackets)
def summer(b, bus, out, rf, cf, part='OPA1612'):            # [2, 12, 13, 18]
    n = bus + '_VE'
    P(b, ref('FB'), 'FB', 'Ferrite 220R@100MHz', {1: bus, 2: n})
    amp(b, 'GCANCEL', n, out, part)
    R(b, rf + ' 1%', out, n); C(b, cf + ' C0G', out, n)

def reinv(b, src, out, part='OPA1612'):                    # [3]
    dn, dp = out + '_DN', out + '_DP'
    R(b, '2K2 0.1%', src, dn); R(b, '2K2 0.1%', dn, out)
    R(b, '2K2 0.1%', 'GCANCEL_BUF', dp); R(b, '2K2 0.1%', dp, 'GNDA')
    amp(b, dp, dn, out, part)

def insert(b, src, dst, name):                              # [4]
    s, rr, rt, bf = name + '_SEND', name + '_RETRAW', name + '_RET', name + '_RBUF'
    R(b, '75R', src, s)
    P(b, ref('J'), 'JACKSW', name.replace('_', ' ') + ' insert', {'T': s, 'RN': s, 'R': rr, 'TN': 'NC', 'S': 'GNDA'})
    C(b, '47u NP 25V', rr, rt); R(b, '47K', rt, 'GNDA')
    amp(b, rt, bf, bf)
    C(b, '220u NP 25V', bf, dst); R(b, '47K', dst, 'GNDA')

def post_amp(b, wiper, post, name):                         # [5] fader wiper -> +10 dB -> POST
    fin, fn, fo = name + '_FIN', name + '_FN', name + '_FPOST'
    C(b, '2.2u', wiper, fin); R(b, '100K', fin, 'GNDA')
    amp(b, fin, fn, fo)
    R(b, '4K7', fo, fn); C(b, '100p C0G', fo, fn); R(b, '2K2', fn, 'GNDA')
    C(b, '220u NP 25V', fo, post); R(b, '47K', post, 'GNDA')

def level_buffer(b, wiper, out, name, unity=True):          # [13, 16] pot wiper -> buffer, Rg not fitted
    fin, fn = name + '_LIN', name + '_LN'
    C(b, '2.2u', wiper, fin); R(b, '100K', fin, 'GNDA')
    amp(b, fin, fn, out)
    R(b, '4K7', out, fn); R(b, 'DNF (2K2 = +10 dB)', fn, 'GNDA', dnp=True)

def drv134(b, inp, op, on):                                 # [7]
    vop, von = op + '_VO', on + '_VO'
    P(b, ref('U'), 'DRV134', 'DRV134', {4: inp, 3: 'GNDA', 6: '+VA', 5: '-VA', 8: vop, 1: von, 7: op, 2: on})
    C(b, '10u NP 25V', vop, op); C(b, '10u NP 25V', von, on)
    C(b, '1u', '+VA', 'GNDA'); C(b, '1u', 'GNDA', '-VA')

def relay(b, a_in, a_out, b_in, b_out):                    # [8] G6K-2F-Y, NO contacts 3-4 and 6-5
    k = ref('K'); coil = k + '_COIL'
    P(b, k, 'RELAY', 'G6K-2F-Y DC12', {1: coil, 8: 'RLY_DRV', 3: a_in, 4: a_out, 2: 'NC', 6: b_in, 5: b_out, 7: 'NC'})
    R(b, '560R', '+VBUS', coil); D(b, 'RLY_DRV', coil)

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
    P(b, ref('D'), 'LED', name + ' red', {2: la, 1: 'GNDD'})

def receiver(b, tip, ring, out):                            # strip-style ground-compensated receiver
    n, p = out + '_N', out + '_P'
    C(b, '100p C0G', tip, 'GNDA'); C(b, '100p C0G', ring, 'GNDA'); R(b, '1M', tip, 'GNDA')
    R(b, '10K 0.1%', ring, n); R(b, '10K 0.1%', n, out); C(b, '33p C0G', n, out)
    R(b, '10K 0.1%', tip, p); R(b, '10K 0.1%', p, 'GNDA')
    amp(b, p, n, out)

def stereo_in(b, name, outl, outr):                         # two NRJ6HF, R normalled to L
    lt, lr, rt, rr = name + '_LT', name + '_LR', name + '_RT', name + '_RR'
    P(b, ref('J'), 'JACKSW', name + ' L in', {'T': lt, 'R': lr, 'S': 'GNDA', 'TN': 'NC', 'RN': 'NC'})
    P(b, ref('J'), 'JACKSW', name + ' R in', {'T': rt, 'R': rr, 'S': 'GNDA', 'TN': lt, 'RN': lr})
    receiver(b, lt, lr, outl); receiver(b, rt, rr, outr)

def jfet_switch(b, src, dst, ctrl, name):                   # [19] series J112, Delta ED2780 sh.1
    s, g = name + '_S', name + '_G'
    C(b, '47u NP 25V', src, s); R(b, '1M', s, 'GNDA')
    P(b, ref('Q'), 'JFET', 'J112', {2: s, 1: dst, 3: g})
    R(b, '47K', g, s); D(b, g, ctrl)

# ================================================================ PART 5: power entry, grounding  [24-26]
b = block('POWER ENTRY  (5-pin XLR from external +-17 V PSU; reverse-polarity Schottkys; star point)')
P(b, ref('J'), 'XLR5', 'PSU in', {1: 'GNDA', 2: '+VBUS', 3: '-VBUS', 4: 'GNDA', 5: 'CHASSIS'})
P(b, ref('D'), 'DS', 'SS54', {1: '+VBUS', 2: 'GNDA'}); P(b, ref('D'), 'DS', 'SS54', {1: 'GNDA', 2: '-VBUS'})
P(b, ref('CN'), 'TAB', 'Ground bar M4 (star point)', {1: 'GNDA'}, fp='MountingHole:MountingHole_4.3mm_M4_Pad', mpn='')
for n in ('GNDD', 'GNDM', 'PHONESGND', 'CHASSIS'):
    P(b, ref('NT'), 'NT', f'Star GNDA-{n}', {1: 'GNDA', 2: n})
b = block('DISTRIBUTION  (PTC per wing per rail; local branches VA audio, VP phones, VM meters, VL logic)')
for w in 'LR':
    P(b, ref('F'), 'PTC', 'MF-R075', {1: '+VBUS', 2: f'+VBUS_{w}'}); P(b, ref('F'), 'PTC', 'MF-R075', {1: '-VBUS', 2: f'-VBUS_{w}'})
for rail, rv, cv, g in (('VA', '1R', '470u 25V', 'GNDA'), ('VP', '2R2', '1000u 25V', 'GNDA'),
                        ('VM', '10R', '47u 25V', 'GNDM'), ('VL', '10R', '47u 25V', 'GNDD')):
    R(b, rv, '+VBUS', '+' + rail); CP(b, cv, '+' + rail, g)
    R(b, rv, '-VBUS', '-' + rail); CP(b, cv, g, '-' + rail)
R(b, '4K7', '+VL', 'PWR_LA'); P(b, ref('D'), 'LED', 'Power green', {2: 'PWR_LA', 1: 'GNDD'})
for i, n in enumerate(['+VBUS', '-VBUS', '+VA', '-VA', '+VP', '-VP', '+VM', '-VM', '+VL', '-VL', 'GNDA', 'GNDD', 'GNDM', 'PHONESGND']):
    P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})

b = block('MOTHERLOOM  (master in the centre: CN1 = left wing, CN2 = right wing; Delta pinout)')
for w in 'LR':
    hdr = {1: 'SPARE1', 3: 'SPARE3', 5: 'SPARE5', 7: 'SPARE7', 19: 'SPARE19', 9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1',
           17: 'MIXR', 18: 'MIXL', 20: 'AUX6', 21: 'AUX5', 22: 'AUX4', 23: 'AUX3', 24: 'AUX1', 25: 'AUX2', 26: 'GCANCEL',
           27: 'PFL', 28: 'PFLN', 29: 'PFLDET', 30: f'-VBUS_{w}', 31: f'-VBUS_{w}', 32: f'+VBUS_{w}', 33: f'+VBUS_{w}', 34: 'P48V_NC'}
    hdr.update({k: 'GNDA' for k in range(2, 17, 2)})
    P(b, ref('CN'), 'HDR', f'Bus {w} wing 2x17', hdr)

b = block('GROUND CANCEL BUFFER  (feeds every re-inverter; summing amps use the raw GCANCEL line)')
amp(b, 'GCANCEL', 'GCANCEL_BUF', 'GCANCEL_BUF')

# ================================================================ PART 1: stereo mix  [1-8]
for side, bus in (('L', 'MIXL'), ('R', 'MIXR')):
    b = block(f'MIX {side}: summing amp (GCANCEL-referenced), re-inverter, master insert')
    summer(b, bus, f'SUM_{side}', '4K7', '100p')
    reinv(b, f'SUM_{side}', f'MIX_{side}')
    insert(b, f'MIX_{side}', f'PRE_{side}', f'MIX_{side}')
b = block('MASTER FADER (dual 100 mm A10K, pin 1 = GNDA) + post-amps +10 dB')
P(b, ref('RV'), 'POT2', 'Master fader 10K log 100mm dual', {1: 'GNDA', 3: 'PRE_L', 2: 'MW_L', 4: 'GNDA', 6: 'PRE_R', 5: 'MW_R'},
  fp=FADER2_FP, mpn='Bourns PTB0144-2010BPA103')
post_amp(b, 'MW_L', 'POST_L', 'MST_L'); post_amp(b, 'MW_R', 'POST_R', 'MST_R')
b = block('MONO: inverting sum of POST L+R, re-inverter')
R(b, '10K', 'POST_L', 'MONO_N'); R(b, '10K', 'POST_R', 'MONO_N')
amp(b, 'GNDA', 'MONO_N', 'MONO_INV'); R(b, '10K', 'MONO_INV', 'MONO_N'); C(b, '100p C0G', 'MONO_INV', 'MONO_N')
R(b, '10K', 'MONO_INV', 'MONO_N2'); R(b, '10K', 'MONO_N2', 'MONO')
amp(b, 'GNDA', 'MONO_N2', 'MONO')
b = block('MAIN OUTPUTS: DRV134 -> 10u NP in the Sense loop -> mute relay (NO) -> XLR male, pin 2 hot')
for src, nm in (('POST_L', 'MAIN_L'), ('POST_R', 'MAIN_R'), ('MONO', 'MAIN_M')):
    drv134(b, src, nm + '_P', nm + '_N')
    relay(b, nm + '_P', nm + '_XP', nm + '_N', nm + '_XN')
    P(b, ref('J'), 'XLR3', nm.replace('_', ' ') + ' out', {1: 'CHASSIS', 2: nm + '_XP', 3: nm + '_XN'})

b = block('POWER-ON MUTE: rails > ~14 V for ~2 s closes all five relays; either rail low opens them at once')
P(b, ref('D'), 'DZ', 'BZX84C6V2', {2: 'GNDD', 1: 'VREF6'}, mpn='BZX84C6V2'); R(b, '4K7', '+VBUS', 'VREF6')
R(b, '56K', '+VBUS', 'SENSE_P'); R(b, '47K', 'SENSE_P', 'GNDD')       # +V < 13.6 V -> fault
R(b, '22K', 'VREF6', 'SENSE_N'); R(b, '51K', 'SENSE_N', '-VBUS')     # -V above -14.4 V -> fault
cmp(b, 'SENSE_P', 'VREF6', 'RAIL_OK'); cmp(b, 'GNDD', 'SENSE_N', 'RAIL_OK')
R(b, '10K', '+VL', 'RAIL_OK')
# timer and Schmitt: values from sim/mute.cir (closes 2.8 s after both rails pass threshold; opens ~2 ms after
# either rail drops; any fault longer than ~10 ms re-arms the full delay)
R(b, '2M2', 'RAIL_OK', 'MUTE_T')
P(b, ref('C'), 'C', '2.2u film 63V', {1: 'MUTE_T', 2: 'GNDD'}, fp='Capacitor_THT:C_Rect_L7.2mm_W8.5mm_P5.00mm_FKP2_FKP2_MKS2_MKP2', mpn='WIMA MKS2 2.2uF 63V')
D(b, 'MUTE_T', 'MUTE_TX'); R(b, '2K2', 'MUTE_TX', 'RAIL_OK'); D(b, 'GNDD', 'MUTE_T')   # reset path, clamp at -0.7 V
cmp(b, 'MUTE_T', 'VREF6', 'MUTE_GO'); R(b, '22M', 'MUTE_GO', 'MUTE_T')
R(b, '4K7', '+VL', 'MUTE_GO'); R(b, '4K7', 'MUTE_GO', 'RLY_B')
D(b, 'RLY_B', 'RLY_BX'); R(b, '2K2', 'RLY_BX', 'RAIL_OK'); D(b, 'GNDD', 'RLY_B')      # fast release, base clamp
P(b, ref('Q'), 'NPN', 'MMBT3904', {1: 'RLY_B', 2: 'GNDD', 3: 'RLY_DRV'})

# ================================================================ PART 2: subgroups, aux masters  [12-13]
SUBPIN = {1: 'SUB1', 2: 'SUB2', 3: 'SUB3', 4: 'SUB4'}
for n in range(1, 5):
    s = f'S{n}'
    b = block(f'SUBGROUP {n}: sum, re-invert, insert, fader + post-amp, DRV134 out, pan to MIX, AFL')
    summer(b, SUBPIN[n], s + '_SUM', '4K7', '100p')
    reinv(b, s + '_SUM', s + '_MIX')
    insert(b, s + '_MIX', s + '_PRE', s)
    P(b, ref('RV'), 'POT', f'Sub {n} fader 10K log 100mm', {1: 'GNDA', 3: s + '_PRE', 2: s + '_W'}, fp=FADER_FP, mpn='Bourns PTB0143-2010BPA103')
    post_amp(b, s + '_W', s + '_POST', s)
    drv134(b, s + '_POST', s + '_OP', s + '_ON')
    P(b, ref('J'), 'JACK', f'Sub {n} out TRS', {'T': s + '_OP', 'R': s + '_ON', 'S': 'GNDA'})
    P(b, ref('RV'), 'POT2', f'Sub {n} pan 10K dual', {1: s + '_POST', 3: 'GNDA', 2: s + '_PWL', 4: 'GNDA', 6: s + '_POST', 5: s + '_PWR'})
    amp(b, s + '_PWL', s + '_PBL', s + '_PBL'); amp(b, s + '_PWR', s + '_PBR', s + '_PBR')
    C(b, '220u NP 25V', s + '_PBL', s + '_PANL'); R(b, '47K', s + '_PANL', 'GNDA')
    C(b, '220u NP 25V', s + '_PBR', s + '_PANR'); R(b, '47K', s + '_PANR', 'GNDA')
    routing(b, s + '_PANL', s + '_PANR', 'MIXL', 'MIXR', f'Sub {n} to MIX')
    R(b, '22K', s + '_POST', s + '_AFLJ'); afl(b, s + '_AFLJ', f'Sub {n} AFL')

for n in range(1, 7):
    a = f'A{n}'
    b = block(f'AUX MASTER {n}: OPA1656 sum (22K || 100p) + re-invert, level, buffer, DRV134 out, AFL')
    summer(b, f'AUX{n}', a + '_SUM', '22K', '100p', 'OPA1656')
    reinv(b, a + '_SUM', a + '_MIX', 'OPA1656')
    C(b, '47u NP 25V', a + '_MIX', a + '_PT')
    P(b, ref('RV'), 'POT', f'Aux {n} master 10K log', {1: 'GNDA', 3: a + '_PT', 2: a + '_W'})
    level_buffer(b, a + '_W', a + '_OUT', a)
    drv134(b, a + '_OUT', a + '_OP', a + '_ON')
    P(b, ref('J'), 'JACK', f'Aux {n} out TRS', {'T': a + '_OP', 'R': a + '_ON', 'S': 'GNDA'})
    R(b, '22K', a + '_OUT', a + '_AFLJ'); afl(b, a + '_AFLJ', f'Aux {n} AFL')

# ================================================================ PART 3: stereo returns  [16]
for n in range(1, 5):
    r = f'RT{n}'
    b = block(f'STEREO RETURN {n}: receivers (R normalled to L), level, buffers, MIX / 1-2 / 3-4, PFL')
    stereo_in(b, f'Return {n}', r + '_L', r + '_R')
    for sd in 'LR':
        C(b, '47u NP 25V', f'{r}_{sd}', f'{r}_PRE{sd}'); R(b, '47K', f'{r}_PRE{sd}', 'GNDA')
    P(b, ref('RV'), 'POT2', f'Return {n} level 10K log dual', {1: 'GNDA', 3: r + '_PREL', 2: r + '_WL', 4: 'GNDA', 6: r + '_PRER', 5: r + '_WR'}, mpn=POT2A_MPN)
    for sd in 'LR':
        level_buffer(b, f'{r}_W{sd}', f'{r}_B{sd}', f'{r}{sd}')
        C(b, '220u NP 25V', f'{r}_B{sd}', f'{r}_RTN{sd}'); R(b, '47K', f'{r}_RTN{sd}', 'GNDA')
    for busl, busr, nm in (('MIXL', 'MIXR', 'MIX'), ('SUB1', 'SUB2', '1-2'), ('SUB3', 'SUB4', '3-4')):
        routing(b, r + '_RTNL', r + '_RTNR', busl, busr, f'Return {n} {nm}')
    R(b, '43K', r + '_PREL', r + '_PFLJ'); R(b, '43K', r + '_PRER', r + '_PFLJ')
    afl(b, r + '_PFLJ', f'Return {n} PFL')

# ================================================================ PART 4: monitoring  [17-22]
b = block('EXT INPUT (2-track / DAW) and MIX / EXT monitor select  (SW latched = EXT)')
stereo_in(b, 'EXT', 'EXT_RL', 'EXT_RR')
for sd in 'LR':
    C(b, '47u NP 25V', f'EXT_R{sd}', f'EXT_{sd}'); R(b, '47K', f'EXT_{sd}', 'GNDA')
sw = ref('SW')
P(b, sw, 'SW', 'EXT select', {2: 'MON_L', 1: 'EXT_L', 3: 'POST_L'}, unit=1)
P(b, sw, 'SW', 'EXT select', {5: 'MON_R', 4: 'EXT_R', 6: 'POST_R'}, unit=2)

b = block('PFL / AFL: OPA1656 sum (22K || 100p) + re-invert, SOLO LEVEL, follower')
summer(b, 'PFL', 'PFL_SUM', '22K', '100p', 'OPA1656')
reinv(b, 'PFL_SUM', 'PFL_MIX', 'OPA1656')
C(b, '47u NP 25V', 'PFL_MIX', 'PFL_PT')
P(b, ref('RV'), 'POT', 'Solo level 10K log', {1: 'GNDA', 3: 'PFL_PT', 2: 'PFL_W'})
C(b, '2.2u', 'PFL_W', 'PFL_FIN'); R(b, '100K', 'PFL_FIN', 'GNDA')
amp(b, 'PFL_FIN', 'PFL_SIG', 'PFL_SIG')

b = block('PFL DETECT (1.5 V per press vs 0.74 V), complementary ramps, rude-solo flasher')
R(b, '10K', 'PFLDET', 'GNDD'); R(b, '220K', '+VL', 'PFL_REF'); R(b, '10K', 'PFL_REF', 'GNDD')
cmp(b, 'PFLDET', 'PFL_REF', 'PFL_ON_RAW'); cmp(b, 'PFL_REF', 'PFLDET', 'MON_ON_RAW')
R(b, '10K', '+VL', 'PFL_ON_RAW'); R(b, '10K', '+VL', 'MON_ON_RAW')
R(b, '100K', 'PFL_ON_RAW', 'PFL_ON'); C(b, '100n', 'PFL_ON', 'GNDD')
R(b, '100K', 'MON_ON_RAW', 'MON_ON'); C(b, '100n', 'MON_ON', 'GNDD')
R(b, '100K', '+VL', 'FL_P'); R(b, '100K', 'FL_P', 'GNDD'); R(b, '100K', 'FL_OUT', 'FL_P')
D(b, 'MON_ON_RAW', 'FL_P')                                   # PFL inactive: holds the flasher off
R(b, '1M', 'FL_OUT', 'FL_N'); C(b, '330n', 'FL_N', 'GNDD')
cmp(b, 'FL_P', 'FL_N', 'FL_OUT')
R(b, '10K', '+VL', 'FL_OUT'); R(b, '3K3', '+VL', 'FL_LA')
P(b, ref('D'), 'LED', 'PFL ACTIVE red 5mm', {2: 'FL_LA', 1: 'FL_OUT'}, fp='LED_THT:LED_D5.0mm')

b = block('PFL SWITCHER: series J112 (Delta ED2780 sh.1) -> CRS L/R followers')
for sd in 'LR':
    jfet_switch(b, f'MON_{sd}', f'CRS_{sd}', 'MON_ON', f'SWM{sd}')
    jfet_switch(b, 'PFL_SIG', f'CRS_{sd}', 'PFL_ON', f'SWP{sd}')
    R(b, '100K', f'CRS_{sd}', 'GNDA')
    amp(b, f'CRS_{sd}', f'CRSB_{sd}', f'CRSB_{sd}')

b = block('CONTROL ROOM: C/ROOM dual A10K, followers, DRV134, mute relays, TRS outs')
P(b, ref('RV'), 'POT2', 'C/Room level 10K log dual', {1: 'GNDA', 3: 'CRSB_L', 2: 'CRW_L', 4: 'GNDA', 6: 'CRSB_R', 5: 'CRW_R'}, mpn=POT2A_MPN)
for sd in 'LR':
    C(b, '2.2u', f'CRW_{sd}', f'CR_FIN{sd}'); R(b, '100K', f'CR_FIN{sd}', 'GNDA')
    amp(b, f'CR_FIN{sd}', f'CRO_{sd}', f'CRO_{sd}')
    drv134(b, f'CRO_{sd}', f'CR{sd}_P', f'CR{sd}_N')
    relay(b, f'CR{sd}_P', f'CR{sd}_XP', f'CR{sd}_N', f'CR{sd}_XN')
    P(b, ref('J'), 'JACK', f'C/Room {sd} out TRS', {'T': f'CR{sd}_XP', 'R': f'CR{sd}_XN', 'S': 'GNDA'})

b = block('HEADPHONES: PHONES dual A10K, OPA1612 + LME49600 composite (+9.9 dB), 2R2 out, PHONESGND')
P(b, ref('RV'), 'POT2', 'Phones level 10K log dual', {1: 'GNDA', 3: 'CRSB_L', 2: 'PHW_L', 4: 'GNDA', 6: 'CRSB_R', 5: 'PHW_R'}, mpn=POT2A_MPN)
for sd in 'LR':
    pin, pn, drv, buf, out = f'PH_IN{sd}', f'PH_N{sd}', f'PH_DRV{sd}', f'PH_BUF{sd}', f'PHO_{sd}'
    C(b, '2.2u', f'PHW_{sd}', pin); R(b, '100K', pin, 'GNDA')
    amp(b, pin, pn, drv, rail='VP')
    P(b, ref('U'), 'LME49600', 'LME49600', {2: drv, 4: buf, 5: '+VP', 3: '-VP', 1: 'NC'})
    C(b, '100n', '+VP', 'GNDA'); C(b, '100n', 'GNDA', '-VP'); C(b, '10u NP 25V', '+VP', 'GNDA'); C(b, '10u NP 25V', 'GNDA', '-VP')
    R(b, '2R2', buf, out); R(b, '4K7', out, pn); C(b, '100p C0G', out, pn); R(b, '2K2', pn, 'GNDA')
P(b, ref('J'), 'JACK', 'Phones TRS', {'T': 'PHO_L', 'R': 'PHO_R', 'S': 'PHONESGND'})

b = block('REMOTE METER HEADER (for a meter bridge)')
P(b, ref('CN'), 'HDR5', 'Remote meter', {1: 'MTR_L', 2: 'MTR_R', 3: '+VM', 4: 'GNDM', 5: '-VM'})

LADDER = [1500, 1100, 910, 680, 620, 470, 330, 300, 220, 180, 150, 110, 91, 68, 62, 47, 33, 27, 20]   # Delta R310-R328
COLOUR = ['green'] * 11 + ['amber'] * 5 + ['red'] * 4                                                  # LED 1 (-20 dB) .. 20 (+18 dB)
def fmt_r(v): return f'{v}R' if v < 1000 else (f'{v // 1000}K{v % 1000 // 100}' if v % 1000 else f'{v // 1000}K')
for sd in 'LR':
    m = f'M{sd}'
    b = block(f'METER {sd}: full-wave rectifier, precision peak / average, follower (TL072), 2 dB ladder, 2 x 10-LED strings')
    R(b, '100R', f'CRSB_{sd}', f'MTR_{sd}')
    R(b, '10K', f'MTR_{sd}', m + '_N1'); R(b, '10K', m + '_N1', m + '_HW')
    amp(b, 'GNDM', m + '_N1', m + '_U1O', 'TL072', 'VM')
    D(b, m + '_HW', m + '_U1O'); D(b, m + '_U1O', m + '_N1')
    R(b, '20K', f'MTR_{sd}', m + '_N2'); R(b, '10K', m + '_HW', m + '_N2')
    R(b, '10K', m + '_X2', m + '_RG')
    P(b, ref('RV'), 'TRIM', 'Cal 10K', {1: m + '_RG', 2: m + '_N2', 3: m + '_N2'}, mpn='Bourns 3296W-1-103')
    amp(b, 'GNDM', m + '_N2', m + '_X2', 'TL072', 'VM')
    R(b, '33K', m + '_X2', m + '_AV'); C(b, '2.2u', m + '_AV', 'GNDM')
    amp(b, m + '_X2', m + '_N4', m + '_U3O', 'TL072', 'VM')
    D(b, m + '_U3O', m + '_PK1'); R(b, '1K', m + '_PK1', m + '_PK'); C(b, '1u', m + '_PK', 'GNDM')
    R(b, '330K', m + '_PK', m + '_PKR'); R(b, '220K', m + '_PKR', 'GNDM')
    R(b, '10K', m + '_DET', m + '_N4'); D(b, m + '_N4', m + '_U3O')
    P(b, ref('JP'), 'SJ3', 'PEAK(1-2) / AVG', {1: m + '_PK', 3: m + '_AV', 2: m + '_JSEL'})
    amp(b, m + '_JSEL', m + '_DET', m + '_DET', 'TL072', 'VM')
    # threshold ladder: +VM - 16K - T20 ... T1 - 91R - GNDM
    R(b, '16K', '+VM', f'{m}_T20')
    for k, rv in zip(range(20, 1, -1), LADDER): R(b, fmt_r(rv), f'{m}_T{k}', f'{m}_T{k - 1}')
    R(b, '91R', f'{m}_T1', 'GNDM')
    # two series LED strings, each from a PNP current source; comparator k shorts the string at the node before LED k
    for s0, ks in (('A', range(1, 11)), ('B', range(11, 21))):
        src = f'{m}{s0}_0'; base, emit = f'{m}{s0}_QB', f'{m}{s0}_QE'
        R(b, '75R', '+VM', emit); D(b, '+VM', f'{m}{s0}_D1'); D(b, f'{m}{s0}_D1', base); R(b, '27K', base, '-VM')
        P(b, ref('Q'), 'PNP', 'MMBT3906', {1: base, 2: emit, 3: src})
        for i, k in enumerate(ks):
            node = f'{m}{s0}_{i}'; nxt = f'{m}{s0}_{i + 1}' if i < 9 else '-VM'
            P(b, ref('D'), 'LED', f'{COLOUR[k - 1]} {-20 + 2 * (k - 1):+d} dB', {2: node, 1: nxt})
            cmp(b, f'{m}_DET', f'{m}_T{k}', node, 'LM2901', 'VM')

build(OUT, 'master', 'Master section - goa console',
      {1: 'Generated by tools/gen_master.py from master_section_spec.md v0.5',
       2: 'Nets joined by labels; refs auto-assigned'}, paper='auto', perrow=30, revision='0.5')
