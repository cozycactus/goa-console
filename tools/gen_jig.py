"""Generate the test-jig schematics (test_jig_spec.md v0.3): the master stub and the load board.
usage: .venv/bin/python tools/gen_jig.py   ->  jig_master_stub.kicad_sch, jig_load_board.kicad_sch
Both sit on the same 34-way ribbon as the four real strips. The circuits are the master's own
(master_lib.py, shared with gen_master.py)."""
import os
from master_lib import *

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM.update({'TERM3': ('Connector', 'Screw_Terminal_01x03'), 'JMP2': ('Connector_Generic', 'Conn_01x02'),
            'JMP3': ('Connector_Generic', 'Conn_01x03'), 'BNC': ('Connector', 'Conn_Coaxial'),
            'TP': ('Connector', 'TestPoint'), 'SLIDE': ('Switch', 'SW_SPDT')})
FP.update({'TERM3': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal',
           'JMP2': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
           'JMP3': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
           'BNC': 'Connector_Coaxial:BNC_Amphenol_B6252HB-NPP3G-50_Horizontal',
           'TP': 'TestPoint:TestPoint_Keystone_5010-5014_Multipurpose',
           'SLIDE': 'Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q'})
MPN.update({'TERM3': 'Phoenix MKDS 1,5/3-5,08', 'BNC': 'Amphenol B6252HB-NPP3G-50', 'TP': 'Keystone 5010',
            'SLIDE': 'C&K OS102011MS2QN1', 'JMP2': '2.54 mm header + shunt', 'JMP3': '2.54 mm header + shunt'})

def bus_header(b, plus, minus, used, unused='GNDA', pfldet='PFLDET'):
    """34-pin header with the Delta pinout. Buses not in `used` go to `unused`: AGND at the stub, standing in for
    their summing amps' virtual earths; no-connect on the load board."""
    names = {9: 'SUB4', 11: 'SUB3', 13: 'SUB2', 15: 'SUB1', 17: 'MIXR', 18: 'MIXL', 20: 'AUX6', 21: 'AUX5',
             22: 'AUX4', 23: 'AUX3', 24: 'AUX1', 25: 'AUX2'}
    hdr = {1: 'NC', 3: 'NC', 5: 'NC', 7: 'NC', 19: 'NC', 26: 'GCANCEL', 27: 'PFL', 28: 'NC', 29: pfldet,
           30: minus, 31: minus, 32: plus, 33: plus, 34: plus}   # 34: third +V (W1)
    hdr.update({k: (n if n in used else unused) for k, n in names.items()})
    hdr.update({k: 'GNDA' for k in range(2, 17, 2)})
    P(b, ref('CN'), 'HDR', 'Bus 2x17 (ribbon)', hdr)

def flags(b, nets):
    for i, n in enumerate(nets): P(b, f'#FLG{i + 1:02d}', 'FLAG', 'PWR_FLAG', {1: n})


def project(name):          # a .kicad_pro next to each schematic, so ERC uses the project's settings
    import json
    d = json.load(open(os.path.join(ROOT, 'master.kicad_pro')))
    d['meta']['filename'] = name + '.kicad_pro'; d['sheets'] = []
    with open(os.path.join(ROOT, name + '.kicad_pro'), 'w') as f: json.dump(d, f, indent=2); f.write('\n')

# ================================================================ master stub  [jig spec 2]
reset()
b = block('POWER IN  bench +-17 V (screw terminal), reverse Schottkys, PTC per rail to the ribbon; local VA / VL branches')
P(b, ref('J'), 'TERM3', 'Bench supply +V / 0 V / -V', {1: '+VBUS', 2: 'GNDA', 3: '-VBUS'})
P(b, ref('D'), 'DS', 'SS54', {1: '+VBUS', 2: 'GNDA'}); P(b, ref('D'), 'DS', 'SS54', {1: 'GNDA', 2: '-VBUS'})
P(b, ref('F'), 'PTC', 'MF-RX160/72', {1: '+VBUS', 2: '+VBUS_R'}); P(b, ref('F'), 'PTC', 'MF-RX160/72', {1: '-VBUS', 2: '-VBUS_R'})
for rail, rv, cv, g in (('VA', '1R', '470u 25V', 'GNDA'), ('VL', '10R', '47u 25V', 'GNDD')):
    R(b, rv, '+VBUS', '+' + rail); CP(b, cv, '+' + rail, g)
    R(b, rv, '-VBUS', '-' + rail); CP(b, cv, g, '-' + rail)
P(b, ref('CN'), 'TAB', 'Ground spade 6.3mm (to the ground bar)', {1: 'GNDA'})
P(b, ref('NT'), 'NT', 'Star GNDA-GNDD', {1: 'GNDA', 2: 'GNDD'})
P(b, ref('NT'), 'NT', 'Star GNDA-CHASSIS', {1: 'GNDA', 2: 'CHASSIS'})
flags(b, ['+VBUS', '-VBUS', '+VA', '-VA', '+VL', '-VL', 'GNDA', 'GNDD'])

b = block('RIBBON  one 34-pin header, Delta pinout; unused buses (SUB 2-4, AUX 3-6) tied to AGND')
bus_header(b, '+VBUS_R', '-VBUS_R', used={'MIXL', 'MIXR', 'SUB1', 'AUX1', 'AUX2'})

b = block('CONFIG  JP: GC REF 1-2 = D (ground cancel), 2-3 = A (plain, AGND);  TIE: 22R from GCANCEL to AGND (test 3)')
P(b, ref('JP'), 'JMP3', 'GC REF (1-2 D, 2-3 A)', {1: 'GCANCEL', 2: 'GCREF', 3: 'GNDA'})
R(b, '22R', 'GCANCEL', 'GC_TIE'); P(b, ref('JP'), 'JMP2', 'GC TIE (fit = 22R tie)', {1: 'GC_TIE', 2: 'GNDA'})
amp(b, 'GCREF', 'GCREF_BUF', 'GCREF_BUF')                     # buffer for the re-inverters, as the master's

b = block('BUS AMPS  MIX L/R, SUB 1, AUX 1/2: OPA1612 (4K7 or 22K) || 100p + re-inverter;  PFL: OPA1656 22K || 100p + re-inverter')
OUTS = []
for bus, s, o, rf, part in (('MIXL', 'SUM_ML', 'MIX_L', '4K7', 'OPA1612'), ('MIXR', 'SUM_MR', 'MIX_R', '4K7', 'OPA1612'),
                            ('SUB1', 'SUM_S1', 'SUB_1', '4K7', 'OPA1612'), ('AUX1', 'SUM_A1', 'AUX_1', '22K', 'OPA1612'),
                            ('AUX2', 'SUM_A2', 'AUX_2', '22K', 'OPA1612'), ('PFL', 'SUM_P', 'PFL_MIX', '22K', 'OPA1656')):
    with new_package(part):             # each summer and its re-inverter in one dual, as on the master
        summer(b, bus, s, rf, '100p', part, gref='GCREF')
        reinv(b, s, o, part, gref='GCREF_BUF')
    OUTS.append((s, o))

b = block('OUTPUTS  each re-inverter -> 100R -> BNC;  MIX L also -> DRV134 -> XLR male (balanced checks, test 11)')
for s, o in OUTS:
    R(b, '100R', o, o + '_BNC'); P(b, ref('J'), 'BNC', o.replace('_', ' ') + ' out', {1: o + '_BNC', 2: 'GNDA'})
drv134(b, 'MIX_L', 'BAL_P', 'BAL_N')
P(b, ref('J'), 'XLR3', 'MIX L balanced out', {1: 'CHASSIS', 2: 'BAL_P', 3: 'BAL_N'})

b = block('PFL DETECT  comparator vs ~0.50 V (one press gives 0.92 V on PFLDET; 2 x 1N4148 clamp, as the master), red LED')
R(b, '10K', 'PFLDET', 'GNDD'); R(b, '330K', '+VL', 'PFL_REF'); R(b, '10K', 'PFL_REF', 'GNDD')
D(b, 'PFLDET', 'PFL_CL'); D(b, 'PFL_CL', 'GNDD'); C(b, '1u', 'PFLDET', 'GNDD')
cmp(b, 'PFL_REF', 'PFLDET', 'PFL_LK')                         # output sinks when PFLDET is above the reference
R(b, '3K3', '+VL', 'PFL_LA'); P(b, ref('D'), 'LED', 'PFL ACTIVE red', {2: 'PFL_LA', 1: 'PFL_LK'}, mpn=LED_MPN['red'])

spares(b)

b = block('TEST POINTS')
for n in ('GCANCEL', 'GCREF_BUF') + tuple(x for so in OUTS for x in so) + ('+VA', '-VA', '+VBUS_R', '-VBUS_R', 'GNDA', 'GNDA'):
    P(b, ref('TP'), 'TP', n, {1: n})
project('jig_master_stub'); parts_sidecar(os.path.join(ROOT, 'jig_master_stub.kicad_sch'))
build(os.path.join(ROOT, 'jig_master_stub.kicad_sch'), 'jig_master_stub', 'Test jig - master stub (goa console)',
      {1: 'Generated by tools/gen_jig.py from test_jig_spec.md v0.3 (section 2)',
       2: 'Bus amps as master_section_spec.md 2, 3, 12, 13, 18; GC REF jumper selects config D or A'},
      paper='auto', perrow=24, revision='0.3')

# ================================================================ load board  [jig spec 3]
reset()
b = block('RIBBON  34-pin header like a strip; own ground spade; 10R ground cancel to pin 26 (strip-like ground)')
bus_header(b, '+VBUS', '-VBUS', used={'MIXL', 'MIXR', 'SUB1', 'AUX1'}, unused='NC', pfldet='NC')
P(b, ref('CN'), 'TAB', 'Ground spade 6.3mm (to the ground bar)', {1: 'GNDA'})
R(b, '10R', 'GNDA', 'GCANCEL')
flags(b, ['GNDA'])

b = block('DUMMY CHANNELS  per bus, groups of 1 / 3 / 4 / 12 channels as one equivalent resistor (same noise and noise '
          'gain); slide switch at the bus end: on = bus, off = AGND (as the routing switches)')
EQUIV = {('4K7', 1): '4K7', ('4K7', 3): '1K58', ('4K7', 4): '1K18', ('4K7', 12): '392R',
         ('22K', 1): '22K', ('22K', 3): '7K32', ('22K', 4): '5K49', ('22K', 12): '1K82'}
for bus, rch in (('MIXL', '4K7'), ('MIXR', '4K7'), ('SUB1', '4K7'), ('AUX1', '22K'), ('PFL', '22K')):
    for n in (1, 3, 4, 12):
        node = f'{bus}_G{n}'
        R(b, EQUIV[(rch, n)] + ' 1%', 'GNDA', node)
        P(b, ref('SW'), 'SLIDE', f'{bus} +{n} ch', {2: node, 1: bus, 3: 'GNDA'})

b = block('BUS CAPACITANCE  1 nF C0G per MIX / SUB 1 bus on a jumper: the 24 strips\' DG413 switches + ribbon (~1.1 nF)')
for bus in ('MIXL', 'MIXR', 'SUB1'):
    P(b, ref('JP'), 'JMP2', f'{bus} +1 nF', {1: bus, 2: bus + '_CB'}); C(b, '1n C0G', bus + '_CB', 'GNDA')

b = block('DUMMY WING LOAD  terminal for external power resistors (about 17 R / 20 W per rail = one 12-strip wing, 1 A)')
P(b, ref('J'), 'TERM3', 'Dummy load +V / 0 V / -V', {1: '+VBUS', 2: 'GNDA', 3: '-VBUS'})
project('jig_load_board'); parts_sidecar(os.path.join(ROOT, 'jig_load_board.kicad_sch'))
build(os.path.join(ROOT, 'jig_load_board.kicad_sch'), 'jig_load_board', 'Test jig - load board (goa console)',
      {1: 'Generated by tools/gen_jig.py from test_jig_spec.md v0.2 (section 3)',
       2: 'Dummy channels raise the bus noise gain to the 24-channel value'},
      paper='auto', perrow=24, revision='0.2')
