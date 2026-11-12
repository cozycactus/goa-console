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
MPN.update({'TERM3': 'Phoenix 1715734 MKDS 1,5/3-5,08', 'BNC': 'Amphenol B6252HB-NPP3G-50', 'TP': 'Keystone 5010',
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
    d = json.load(open(os.path.join(ROOT, 'boards', 'master', 'master.kicad_pro')))
    d['meta']['filename'] = name + '.kicad_pro'; d['sheets'] = []
    from schgen import keep_net_settings, own_sheet; keep_net_settings(d, os.path.join(ROOT, 'boards', name, name + '.kicad_pro')); own_sheet(d, name)
    with open(os.path.join(ROOT, 'boards', name, name + '.kicad_pro'), 'w') as f: json.dump(d, f, indent=2); f.write('\n')

# ================================================================ master stub  [jig spec 2]
reset()
b = block('POWER IN  bench +-17 V (screw terminal), reverse Schottkys, PTC per rail to the ribbon; local VA / VL branches')
P(b, ref('J'), 'TERM3', 'Bench supply +V / 0 V / -V', {1: '+VBUS', 2: 'GNDA', 3: '-VBUS'})
P(b, ref('D'), 'DS', 'SS54', {1: '+VBUS', 2: 'GNDA'}); P(b, ref('D'), 'DS', 'SS54', {1: 'GNDA', 2: '-VBUS'})
P(b, ref('F'), 'PTC', 'MF-RX160/72', {1: '+VBUS', 2: '+VBUS_R'}); P(b, ref('F'), 'PTC', 'MF-RX160/72', {1: '-VBUS', 2: '-VBUS_R'})
for rail, rv, cv, g in (('VA', '1R', '470u 25V', 'GNDA'), ('VL', '10R', '47u 25V', 'GNDD')):
    k = dict(mpn='Panasonic ERJ-P06J1R0V') if rv == '1R' else {}       # anti-surge, as the master (MG17)
    R(b, rv, '+VBUS', '+' + rail, **k); CP(b, cv, '+' + rail, g)
    R(b, rv, '-VBUS', '-' + rail, **k); CP(b, cv, g, '-' + rail)
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
drv134(b, 'MIX_L', 'BAL_P', 'BAL_N', rx=False)
P(b, ref('J'), 'XLR3', 'MIX L balanced out', {1: 'CHASSIS', 2: 'BAL_P', 3: 'BAL_N', 'G': 'CHASSIS'})

b = block('PFL DETECT  comparator vs ~0.50 V (one press gives 0.92 V on PFLDET; 2 x 1N4148 clamp, as the master), red LED')
R(b, '10K', 'PFLDET', 'GNDD'); R(b, '330K', '+VL', 'PFL_REF'); R(b, '10K', 'PFL_REF', 'GNDD')
D(b, 'PFLDET', 'PFL_CL'); D(b, 'PFL_CL', 'GNDD'); C(b, '1u', 'PFLDET', 'GNDD')
cmp(b, 'PFL_REF', 'PFLDET', 'PFL_LK')                         # output sinks when PFLDET is above the reference
R(b, '3K3', '+VL', 'PFL_LA', mpn='Panasonic ERJ-P06J332V'); P(b, ref('D'), 'LED', 'PFL ACTIVE red', {2: 'PFL_LA', 1: 'PFL_LK'}, mpn=LED_MPN['red'])

spares(b)

b = block('TEST POINTS')
for n in ('GCANCEL', 'GCREF_BUF') + tuple(x for so in OUTS for x in so) + ('+VA', '-VA', '+VBUS_R', '-VBUS_R', 'GNDA', 'GNDA'):
    P(b, ref('TP'), 'TP', n, {1: n})
project('jig_master_stub'); parts_sidecar(os.path.join(ROOT, 'boards', 'jig_master_stub', 'jig_master_stub.kicad_sch'))

# ---------------------------------------------------------------- the stub's drawing (2026-11-10)
# The sheet is drawn, not laid out in labelled cells: every bus is one wired lane, ribbon -> ferrite -> summer -> re-inverter
# -> 100R -> BNC, with its test points on the nodes they probe and its op-amp's supply pins under it. The parts and their
# order above are untouched and the functional blocks went to jig_master_stub_parts.json first (the placer reads them
# there), so the netlist, every reference and the board stay as they were; only the drawing regroups the parts.
OLD = {t.split('  ')[0]: ps for t, ps in schgen.blocks}
FR = {k: [f[2] for f in schgen.FRAGS.get(id(ps), []) if not f[3]] for k, ps in OLD.items()}        # circuit fragments
PU = {k: [f[2] for f in schgen.FRAGS.get(id(ps), []) if f[3]] for k, ps in OLD.items()}            # power units, spares
by = lambda ps, key, unit=1: [p['ref'] for p in ps if p['key'] == key and p['unit'] == unit]
TPS = {}
for p in OLD['TEST POINTS']: TPS.setdefault(p['pins']['1'], []).append(p)
take = lambda *nets: [TPS[n].pop(0) for n in nets]
tp_of = lambda ps, net: next(p['ref'] for p in ps if p['key'] == 'TP' and p['pins']['1'] == net)


def stub_power(d):
    """Bench terminal, reverse Schottkys, a PTC per rail to the ribbon, the local VA / VL branches; the ground star under it."""
    ps = d.parts; j, (d1, d2), (f1, f2) = by(ps, 'TERM3')[0], by(ps, 'DS'), by(ps, 'PTC')
    r1, r2, r3, r4 = by(ps, 'R'); c1, c2, c3, c4 = by(ps, 'CP'); fl = {d.nets(f)['1']: f for f in by(ps, 'FLAG')}
    T, M, B = 2, 11, 20                                    # +VBUS line, 0 V line, -VBUS line
    d.at(j, 6, M, mirror='y')
    def flag(net, x, y, up=True):                          # a PWR_FLAG on a stub off the line it marks
        d.w((x, y), (x, y - 1 if up else y + 1)); d.at(fl[net], x, y - 1 if up else y + 1, rot=0 if up else 180)
    d.w((j, 1), (13, M - 1), (13, T), (66, T)); d.w((j, 3), (13, M + 1), (13, B), (66, B)); d.w((j, 2), (48, M))
    d.port('+VBUS', (13, T)); d.port('-VBUS', (13, B))
    d.v(d1, 16, 6.5, top='+VBUS'); d.w((16, T), (16, 5)); d.w((16, 8), (16, M))
    d.v(d2, 19, 15.5, top='GNDA'); d.w((19, M), (19, 14)); d.w((19, 17), (19, B))
    flag('+VBUS', 22, T); flag('-VBUS', 22, B, up=False)
    d.w((23, M), (23, M + 1)); d.gnd((23, M + 1))
    d.v(f1, 28, 4.5, top='+VBUS', text='L'); d.w((28, T), (28, 3)); d.w((f1, 2), (28, 7), (37, 7))
    d.at(tp_of(ps, '+VBUS_R'), 31, 7); d.port('+VBUS_R', (37, 7), 'R')
    d.v(f2, 28, 17.5, top='-VBUS_R', text='L'); d.w((28, 19), (28, B)); d.w((f2, 2), (28, 15), (37, 15))
    d.at(tp_of(ps, '-VBUS_R'), 31, 15, rot=180); d.port('-VBUS_R', (37, 15), 'R')
    for x, ra, ca, cb, rb, rail, gnd in ((48, r1, c1, c2, r2, 'VA', 'GNDA'), (66, r3, c3, c4, r4, 'VL', 'GNDD')):
        d.v(ra, x, 4.5, top='+VBUS', text='L'); d.w((x, T), (x, 3)); d.w((x, 6), (x, 7))
        d.v(ca, x, 8.5, top='+' + rail, text='L'); d.w((x, 10), (x, M))
        d.v(cb, x, 13.5, top=gnd, text='L'); d.w((x, M), (x, 12)); d.w((x, 15), (x, 16))
        d.v(rb, x, 17.5, top='-' + rail, text='L'); d.w((x, 19), (x, B))
        e = x + (11 if rail == 'VA' else 7)
        d.w((x, 6), (e, 6)); d.port('+' + rail, (e, 6), 'R'); flag('+' + rail, x + 3, 6)
        d.w((x, 16), (e, 16)); d.port('-' + rail, (e, 16), 'R'); flag('-' + rail, x + 3, 16, up=False)
        if rail == 'VA': d.at(tp_of(ps, '+VA'), x + 7, 6); d.at(tp_of(ps, '-VA'), x + 7, 16, rot=180)
        else: d.w((x, M), (x + 3, M), (x + 3, M + 1)); d.gnd((x + 3, M + 1), 'GNDD')
    # the ground star: the spade to the copper bar, the two net ties, the 0 V test points
    tab, (nt1, nt2) = by(ps, 'TAB')[0], by(ps, 'NT'); ta, tb = [p['ref'] for p in ps if p['key'] == 'TP' and p['pins']['1'] == 'GNDA']
    Y = 27
    d.w((4, Y), (4, Y + 14)); d.gnd((4, Y + 14)); flag('GNDA', 4, Y)
    d.at(tab, 10, Y); d.w((4, Y), (tab, 1))
    d.at(nt1, 10, Y + 4, text='R'); d.w((4, Y + 4), (nt1, 1)); d.w((nt1, 2), (22, Y + 4), (22, Y + 5)); d.gnd((22, Y + 5), 'GNDD')
    flag('GNDD', 18, Y + 4, up=False)
    d.at(nt2, 10, Y + 8, text='R'); d.w((4, Y + 8), (nt2, 1)); d.w((nt2, 2), (22, Y + 8)); d.port('CHASSIS', (22, Y + 8), 'R')
    d.w((4, Y + 12), (9, Y + 12)); d.w((9, Y + 12), (14, Y + 12)); d.at(ta, 9, Y + 12); d.at(tb, 14, Y + 12)


def stub_ribbon(d):
    frags.header(d, by(d.parts, 'HDR')[0], 18, 10)


def stub_gcref(d):
    """GC REF jumper (1-2 = config D, 2-3 = config A), the 22R tie for test 3, the buffer for the re-inverters."""
    ps = d.parts; (jp1,), (jp2,), (r,) = by(ps, 'JMP3'), by(ps, 'JMP2'), by(ps, 'R'); u = by(ps, 'OPA')[0]
    d.port('GCANCEL', (0, 6)); d.w((0, 6), (11, 6)); d.at(tp_of(ps, 'GCANCEL'), 3, 6)
    d.at(jp1, 12, 2, rot=90); d.w((11, 6), (jp1, 1)); d.w((jp1, 3), (13, 5), (15, 5), (15, 6)); d.gnd((15, 6))
    d.v(r, 6, 8.5, top='GCANCEL'); d.w((6, 6), (6, 7))
    d.at(jp2, 6, 14, rot=270); d.w((6, 10), (jp2, 1)); d.w((6, 11), (7, 11)); d.port('GC_TIE', (7, 11), 'R'); d.w((jp2, 2), (3, 12), (3, 13)); d.gnd((3, 13))
    d.at(u, 24, 9, unit=1, text='U')
    d.w((jp1, 2), (12, 8), (u, 3)); d.port('GCREF', (12, 8))
    d.w((u, 1), (28, 9), (28, 12), (20, 12), (20, 10), (u, 2)); d.w((28, 9), (38, 9)); d.port('GCREF_BUF', (38, 9), 'R')
    d.at(tp_of(ps, 'GCREF_BUF'), 31, 9)
    d.shift(12, 13); PU['CONFIG'][0](d); d.shift(-12, -13)
    d.note('JP1 1-2: config D, ground cancel.  2-3: config A, the stub\'s own AGND.', (0, 25))
    d.note('JP2 fitted: 22R from GCANCEL to AGND, the master-end tie of test 3.', (0, 26.5))


ROWS = []                       # (bus, sum net, output net, inv fragment, diff fragment, power unit) per lane
LANE = 23
def stub_amps(d):
    """Six lanes, one per bus: ferrite, summer on GCREF, re-inverter on GCREF_BUF, 100R, BNC."""
    ps = d.parts; routs = [p['ref'] for p in ps if p['key'] == 'R' and p['value'] == '100R']; bncs = by(ps, 'BNC')
    for i, (bus, s, o, inv, dif, pu) in enumerate(ROWS):
        d.shift(0, i * LANE)
        n = len(d.ports); inv(d); d.shift(23, 1); dif(d); d.shift(-23, -1)
        d.ports[n:] = [p for p in d.ports[n:] if p[0] not in (s, o)]          # joined by the wire, named by their test points
        d.at(tp_of(ps, s), 26, 7); d.w((26, 9), (26, 7))
        d.w((52, 10), (56, 10)); d.at(tp_of(ps, o), 53, 8); d.w((53, 10), (53, 8))
        d.h(routs[i], 57.5, 10, left=o, text='D'); d.at(bncs[i], 70, 10); d.w((59, 10), (bncs[i], 1)); d.gnd((bncs[i], 2))
        for net, pt, side in ((bus + '_VE', (5.5, 8), 'R'), (s, (27, 9), 'R'), (o + '_DN', (37.4, 9), 'R'), (o + '_DP', (38, 15), 'U'),
                              (o, (54.5, 10), 'D'), (o + '_BNC', (59.5, 10), 'R')): d.port(net, pt, side)
        d.shift(1, 11); pu(d); d.shift(-1, -11)
        d.note((bus[:3] + ' ' + bus[3:]).strip(), (0, 0.5), 1.8)
        d.shift(0, -i * LANE)


def stub_balanced(d):
    """MIX L through a DRV135 to the XLR (test 11): the fragment's couplers, the decouplers under the IC, the XLR wired."""
    ps = d.parts; cs = by(ps, 'C'); x = by(ps, 'XLR3')[0]
    FR['OUTPUTS'][0](d)
    d.ports[:] = [p for p in d.ports if p[0] == 'MIX_L']
    d.at(cs[2], 24, 15.5); d.at(cs[3], 30, 15.5, rot=180)
    d.at(x, 46, 8, mirror='y')
    d.w((21, 7), (40, 7), (40, 8), (x, 2)); d.w((21, 9), (38, 9), (38, 12), (46, 12), (x, 3))
    d.w((x, 1), (51, 8)); d.w((x, 'G'), (46, 4), (51, 4), (51, 8)); d.w((51, 8), (53, 8)); d.port('CHASSIS', (53, 8), 'R')
    for net, pt, side in (('BAL_P', (24, 7), 'R'), ('BAL_N', (24, 9), 'R'), ('BAL_P_VO', (13, 4), 'U'), ('BAL_N_VO', (13, 12), 'D')):
        d.port(net, pt, side)


def stub_pfl(d):
    """PFL detect as the master: 10K + two 1N4148 + 1u on the line, 0.50 V reference, LM393 sinking the LED; the spares."""
    ps = d.parts; r10, r330, rref, rled = by(ps, 'R'); d3, d4 = by(ps, 'D'); c = by(ps, 'C')[0]; led = by(ps, 'LED')[0]
    u = by(ps, 'CMP')[0]
    d.at(u, 28, 9, unit=1, text='U')
    d.port('PFLDET', (0, 14)); d.w((0, 14), (24, 14), (24, 10), (u, 2))
    d.v(r10, 4, 16.5, top='PFLDET'); d.w((4, 14), (4, 15)); d.gnd((4, 18), 'GNDD')
    d.v(d3, 9, 16.5, top='PFLDET'); d.w((9, 14), (9, 15)); d.v(d4, 9, 20.5, top='PFL_CL'); d.w((9, 18), (9, 19)); d.gnd((9, 22), 'GNDD')
    d.v(c, 15, 16.5, top='PFLDET'); d.w((15, 14), (15, 15)); d.gnd((15, 18), 'GNDD')
    d.v(r330, 20, 5.5, top='+VL', text='L'); d.w((20, 2), (20, 4)); d.port('+VL', (20, 2), 'U')
    d.w((20, 7), (20, 8), (u, 3)); d.v(rref, 20, 9.5, top='PFL_REF', text='L'); d.gnd((20, 11), 'GNDD')
    d.v(rled, 37, 2.5, top='+VL'); d.port('+VL', (37, 1), 'U'); d.v(led, 37, 6.5, top='PFL_LA'); d.w((37, 4), (37, 5))
    d.w((u, 1), (37, 9), (37, 8))
    d.w((9, 18.5), (10, 18.5)); d.w((37, 4.5), (38, 4.5))
    for net, pt, side in (('PFL_REF', (20.5, 8), 'R'), ('PFL_CL', (10, 18.5), 'R'), ('PFL_LA', (38, 4.5), 'R'), ('PFL_LK', (31.5, 9), 'R')):
        d.port(net, pt, side)
    d.shift(42, 11); PU['PFL DETECT'][0](d); d.shift(-42, -11)               # U9's supply pins and decouplers
    d.shift(48, 0); PU['PFL DETECT'][1](d); d.shift(-48, 0)                   # the spare op-amp half (U1B)
    d.port(next(n for n in d.nets(by(ps, 'OPA', 2)[0]).values() if 'SPARE' in n), (52.5, 6), 'R')
    d.at(u, 70, 4, unit=2, text='U')                                         # the spare comparator: + on GNDD, - on +VL
    d.w((u, 5), (65, 3), (65, 4)); d.gnd((65, 4), 'GNDD'); d.w((u, 6), (66, 5), (66, 7)); d.port('+VL', (66, 7), 'D')
    d.note('Spare halves, tied off', (48, -2))


for k, (bus, (s, o)) in enumerate(zip(('MIXL', 'MIXR', 'SUB1', 'AUX1', 'AUX2', 'PFL'), OUTS)):
    ROWS.append((bus, s, o, FR['BUS AMPS'][2 * k], FR['BUS AMPS'][2 * k + 1], PU['BUS AMPS'][k]))
OUTP = OLD['OUTPUTS']; AS_BUILT = list(schgen.blocks)
schgen.blocks[:] = []
for title, draw, parts in (
        ('POWER IN  bench +-17 V, reverse Schottkys, a PTC per rail to the ribbon, local VA / VL', stub_power,
         OLD['POWER IN'] + take('+VA', '-VA', '+VBUS_R', '-VBUS_R', 'GNDA', 'GNDA')),
        ('RIBBON  34-pin header, Delta pinout; SUB 2-4 and AUX 3-6 on AGND', stub_ribbon, OLD['RIBBON']),
        ('GROUND-CANCEL REFERENCE  config jumper, 22R tie, buffer', stub_gcref, OLD['CONFIG'] + take('GCANCEL', 'GCREF_BUF')),
        ('BUS AMPS  bus -> ferrite -> summer (+ on GCREF) -> re-inverter (+ leg on GCREF_BUF) -> 100R -> BNC', stub_amps,
         OLD['BUS AMPS'] + take(*[n for so in OUTS for n in so]) + [p for p in OUTP if p['key'] in ('R', 'BNC')]),
        ('BALANCED OUTPUT  MIX L -> DRV135 -> XLR male (test 11)', stub_balanced, [p for p in OUTP if p['key'] not in ('R', 'BNC')]),
        ('PFL DETECT  one press = 0.92 V on PFLDET against 0.50 V; red LED', stub_pfl, OLD['PFL DETECT'])):
    block(title, draw).extend(parts)
assert not any(TPS.values()), 'test point left undrawn'
build(os.path.join(ROOT, 'boards', 'jig_master_stub', 'jig_master_stub.kicad_sch'), 'jig_master_stub', 'Test jig - master stub (goa console)',
      {1: 'Generated by tools/gen_jig.py from test_jig_spec.md v0.3 (section 2)',
       2: 'Bus amps as master_section_spec.md 2, 3, 12, 13, 18; GC REF jumper selects config D or A'},
      paper='auto', perrow=24, revision='0.3', col_height=300)
schgen.blocks[:] = AS_BUILT                                 # _intended.json in the parts' own order, as before
schgen.write_intended(os.path.join(ROOT, 'boards', 'jig_master_stub', 'jig_master_stub.kicad_sch'))

# ================================================================ load board  [jig spec 3]
reset(); schgen.DRAW.clear(); schgen.FRAGS.clear()        # the stub's drawings must not meet a recycled list id
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
project('jig_load_board'); parts_sidecar(os.path.join(ROOT, 'boards', 'jig_load_board', 'jig_load_board.kicad_sch'))

# ---------------------------------------------------------------- the load board's drawing (2026-11-12)
# One wired drawing of the parts above (their order, references and nets untouched; the functional blocks are in
# jig_load_board_parts.json already): the ribbon header as a pin list at the left with the 10R ground cancel, the ground
# spade and the wing-load terminal wired to it, and one row per bus, the four dummy groups hanging from the bus line.
LB_HEAD = [t for t, _ in schgen.blocks]; LB_PARTS = [p for _, ps in schgen.blocks for p in ps]


def load_board(d):
    ps = d.parts; one = lambda key: next(p['ref'] for p in ps if p['key'] == key)
    by_net = lambda key, pin, net: next(p['ref'] for p in ps if p['key'] == key and p['pins'].get(str(pin)) == net)
    hdr, tab, term = one('HDR'), one('TAB'), one('TERM3')
    XL, YL = 20, 12; L, Rr = XL - 2, XL + 3; row = lambda pin: YL - 8 + (pin - 1) // 2     # the header: rows YL - 8 .. YL + 8
    bottom, tops = frags.pin_list(d, hdr, XL, YL, wired=('26', '30', '31', '32', '33', '34'), short=('R',))
    d.fld(hdr, val_at=(-1.5, -9.5, 'right'))                   # its value beside its reference: the rails run under the header
    # the ground spade and the GNDA flag on top of the header's ground rail
    gx, gy = tops[('GNDA', 'R')]
    d.at(tab, gx + 4, gy - 2); d.w((gx, gy), (gx, gy - 2), (tab, 1)); d.w((gx, gy - 2), (gx, gy - 3.5)); d.at('#FLG01', gx, gy - 3.5)
    # pin 26: the 10R ground cancel, as on a strip
    rgc = by_net('R', 2, 'GCANCEL'); y = row(26)
    d.h(rgc, Rr + 9.5, y, left='GCANCEL'); d.w((hdr, 26), (Rr + 2, y)); d.w((Rr + 2, y), (Rr + 8, y)); d.port('GCANCEL', (Rr + 2, y), 'R')
    d.w((Rr + 11, y), (Rr + 12, y), (Rr + 12, y + 1.5)); d.gnd((Rr + 12, y + 1.5))
    # the rails to the wing-load terminal: +VBUS (32 / 34, and 33 round the bottom), -VBUS outside it (30, and 31 round)
    # (one crossing: +VBUS leaves its loop through -VBUS's); the terminal under the header, +VBUS to its lower pin from below
    yb = YL + 12; XT, YT = Rr + 13, yb + 5
    d.at(term, XT, YT, mirror='x')                             # pin 3 (-VBUS) on top, pin 1 (+VBUS) at the bottom
    d.fld(term, ref_at=(1, -0.6, 'left'), val_at=(1, 0.6, 'left'))
    d.w((hdr, 32), (Rr + 2, row(32)), (Rr + 2, row(34))); d.w((hdr, 34), (Rr + 2, row(34)), (Rr + 2, yb))
    d.w((hdr, 33), (L - 1, row(33)), (L - 1, yb), (Rr + 2, yb))
    d.w((Rr + 2, yb), (Rr + 2, YT + 4), (XT - 3, YT + 4), (XT - 3, YT + 1), (term, 1)); d.port('+VBUS', (Rr + 2, YT + 4), 'L')
    d.w((hdr, 30), (Rr + 4, row(30)), (Rr + 4, yb + 1)); d.w((Rr + 4, yb + 1), (Rr + 4, YT - 1), (term, 3))
    d.w((hdr, 31), (L - 2, row(31)), (L - 2, yb + 1), (Rr + 4, yb + 1)); d.port('-VBUS', (L - 2, yb + 1), 'L')
    d.w((term, 2), (XT - 4.5, YT), (XT - 4.5, YT + 2)); d.gnd((XT - 4.5, YT + 2))
    wl = LB_HEAD[3].index('(')
    d.note(LB_HEAD[3][:wl].rstrip(), (0, YT + 8), 2.0); d.note('  ' + LB_HEAD[3][wl:], (0, YT + 9.6), 2.0)
    # one row per bus: its name where it comes from the header, the dummy groups hanging from the bus line
    X0, Y0, PITCH = 58, 7, 12
    buses = ('MIXL', 'MIXR', 'SUB1', 'AUX1', 'PFL')
    d.note(LB_HEAD[1].split(';')[0] + ';', (X0 - 4, 0.5), 2.0); d.note('  ' + LB_HEAD[1].split(';', 1)[1].strip(), (X0 - 4, 2.1), 2.0)
    cb = LB_HEAD[2]; c1, c2 = cb.index(' per '), cb.index(': ') + 1                 # under the three jumpers, beside the rows without one
    for i, t in enumerate((cb[:c1], '  ' + cb[c1 + 1:c2], '  ' + cb[c2 + 1:])): d.note(t, (X0 + 70, Y0 + 3 * PITCH + 1 + 1.6 * i), 2.0)
    for k, bus in enumerate(buses):
        y = Y0 + k * PITCH; end = X0
        d.port(bus, (X0 - 2, y), 'L')
        for i, n in enumerate((1, 3, 4, 12)):
            gx = X0 + 12 + 18 * i; node = f'{bus}_G{n}'
            r = by_net('R', 2, node); sw = by_net('SLIDE', 2, node)
            d.at(sw, gx, y + 3); d.fld(sw, ref_at=(-6.5, 1.3, 'left'), val_at=(-6.5, 2.2, 'left'))
            d.h(r, gx - 8.5, y + 3, left='GNDA'); d.w((gx - 10, y + 3), (gx - 11, y + 3), (gx - 11, y + 4.5)); d.gnd((gx - 11, y + 4.5))
            d.w((gx - 7, y + 3), (sw, 2)); d.port(node, (gx - 7, y + 3), 'R')
            d.w((sw, 1), (gx + 3, y + 2), (gx + 3, y)); d.w((sw, 3), (gx + 3, y + 4), (gx + 3, y + 5)); d.gnd((gx + 3, y + 5))
            end = gx + 3
        if any(p['key'] == 'JMP2' and p['pins']['1'] == bus for p in ps):      # the bus capacitance on its jumper
            jp = by_net('JMP2', 1, bus); c = by_net('C', 1, bus + '_CB'); jx = X0 + 12 + 18 * 4 - 2
            d.at(jp, jx, y + 3); d.fld(jp, ref_at=(1, 0, 'left'), val_at=(1, 1, 'left'))
            d.w((jx - 4, y), (jx - 4, y + 3), (jp, 1)); end = jx - 4
            d.w((jp, 2), (jx - 3, y + 4), (jx - 3, y + 5)); d.port(bus + '_CB', (jx - 3, y + 4), 'L')
            d.v(c, jx - 3, y + 6.5, top=bus + '_CB'); d.w((jx - 3, y + 8), (jx - 3, y + 8.5)); d.gnd((jx - 3, y + 8.5))
        d.w((X0 - 2, y), (end, y))


schgen.blocks[:] = []
block(LB_HEAD[0], load_board).extend(LB_PARTS)
build(os.path.join(ROOT, 'boards', 'jig_load_board', 'jig_load_board.kicad_sch'), 'jig_load_board', 'Test jig - load board (goa console)',
      {1: 'Generated by tools/gen_jig.py from test_jig_spec.md v0.2 (section 3)',
       2: 'Dummy channels raise the bus noise gain to the 24-channel value'},
      paper='auto', perrow=24, revision='0.2')
