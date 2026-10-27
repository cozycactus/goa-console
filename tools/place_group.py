"""Component placement for the group module (M1, master_panel_study.md): main board + jack board, placement only.
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_group.py      # -> group.kicad_pcb (38 x 349.5 mm), group_jack_board.kicad_pcb (38 x 93.5 mm)
8 HP x 12U panel in the strip's frame (placer.py): same y origin, fader, bus header and spade, so the ribbon and
the faders line up with the strips. The switches that carry a bus (sub to MIX, return routing, AFL/PFL) sit in
the strips' pan / routing / PFL rows, a few cm from the bus header. Zones follow gen_group.py's blocks
(group_parts.json). The jack board (7 jacks, 2x8 + 2x5 links) sits ~24 mm under the panel, y 0-93.5.
RET1 (feature_gaps.md, 2026-10-26): return 2's jacks are a fourth row (y 78), so the main board starts at y 94.5;
RETURN 1 / RETURN 2 knobs at y 106 / 128, return 2's routing keys at y 150, AUX at y 172."""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field
import netnames
from placer import place, PROJ, W8 as W, XL, XR, XC, pot, sw, led, jack, FADER, BUS, SPADE, NETTIE, FADER_HOLES

JACK_Y1, MAIN_Y0, MAIN_Y1 = 93.5, 94.5, 444.0

# ================================================================ jack board
JACK_FIX = {'J2': jack(XL, 12), 'J1': jack(XR, 12),          # sub out | sub insert
            'J3': jack(XL, 34),                              # aux out | link headers
            'J4': jack(XL, 56), 'J5': jack(XR, 56),          # return 1 L | R
            'J6': jack(XL, 78), 'J7': jack(XR, 78),          # return 2 L | R (RET1)
            'CN1': (31.0, 42.3, 180, 'B'),                   # 2x8 link, bottom side, pins x 31 / 33.54, y 24.5-42.3 (1 mm up:
                                                             # its body had sat over J5's tip joint, 2026-10-26 review)
            'CN2': (19.9, 39.0, 180, 'B')}                   # 2x5 link (return 2) beside it: pins x 19.9 / 22.44, y 28.8-39.0
JACK_HOLES = []                                              # M3 standoffs to the panel, ~24 mm (jack body height):
JACK_FIX.update({'H1': (XL, 89.8, 0, 'F'), 'H2': (XR, 89.8, 0, 'F')})   # plated, on CHASSIS (ground_study.md G2); below
                                                             # the last row since the links fill the free slot
JACK_NOTES = ((12, 'SUB OUT | SUB INSERT'), (34, 'AUX OUT | links CN2, CN1 (bottom)'), (56, 'RETURN 1 L | R'),
              (78, 'RETURN 2 L | R'))
place(os.path.join(PROJ, 'group_jack_board.net'), os.path.join(PROJ, 'group_jack_board.kicad_pcb'),
      dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=[], notes=JACK_NOTES,
           hole_value='M3 standoff = jack body height (~24 mm)'))

# ================================================================ main board
d = json.load(open(os.path.join(PROJ, 'group_parts.json')))
seen, B = set(), {}
for title, refs in d['blocks']:                 # a package shared by two blocks stays in the first
    B[title.split('  ')[0].split(':')[0]] = [r for r in refs if not (r in seen or seen.add(r))]
# Beside-parts (decouplers, summing-junction parts, DRV134 caps) come from the generator (group_parts.json 'near');
# groups below are derived from the netlist, so a regeneration that renumbers parts needs no edits here
NEAR = dict(d['near'])
net = sexp(open(os.path.join(PROJ, 'group.net')).read())
comps = next(c for c in net[1:] if isinstance(c, list) and c[0] == 'components')
FPN = {field(c, 'ref'): field(c, 'footprint') for c in comps[1:]}
VAL = {field(c, 'ref'): field(c, 'value') for c in comps[1:]}
ON = {field(n, 'name').lstrip('/'): {field(x, 'ref') for x in n[1:] if isinstance(x, list) and x[0] == 'node'}
      for n in next(c for c in net[1:] if isinstance(c, list) and c[0] == 'nets')[1:]}
_rn = netnames.renames(os.path.join(PROJ, 'group.net'))    # a drawn schematic leaves nets inside a drawing unlabelled
ON = {_rn.get(k, k): v for k, v in ON.items()}
num = lambda r: int(re.sub(r'\D', '', r))
byval = lambda v: next(r for r, x in VAL.items() if x == v)
ic_on = lambda n: next(r for r in sorted(ON[n], key=num) if r.startswith('U'))
for out in ('S_MIX', 'A_MIX'):                  # re-inverter networks short, at their op-amp
    u = ic_on(out + '_DN'); NEAR.update({r: u for r in (ON[out + '_DN'] | ON[out + '_DP']) - {u} if r not in NEAR})

FIX = {
 'RV4': pot(XL, 106, dual=True), 'SW7': sw(27, 106), byval('Return PFL red'): led(35, 106),     # RETURN 1 level | PFL
 'RV5': pot(XL, 128, dual=True), 'SW11': sw(27, 128), byval('Return 2 PFL red'): led(35, 128), # RETURN 2 level | PFL
 'SW8': sw(XR - 22, 150), 'SW9': sw(XR - 11, 150), 'SW10': sw(XR, 150),     # return 2 to MIX, 1-2, 3-4
 'RV3': pot(XL, 172), 'SW3': sw(26, 172), byval('Aux AFL red'): led(34.5, 172),                # AUX n master | AFL
 'RV2': pot(XL, 252, dual=True, sx=10), 'SW1': sw(XR, 252),                         # SUB pan | to MIX (strips' pan row)
 'SW4': sw(XR - 22, 274), 'SW5': sw(XR - 11, 274), 'SW6': sw(XR, 274),       # return to MIX, 1-2, 3-4 (routing row)
 'SW2': sw(XR - 22, 292), byval('Sub AFL red'): led(XR - 13.8, 292),         # SUB AFL (strips' PFL row)
 'RV1': FADER, 'CN2': BUS, 'CN1': SPADE, 'NT1': NETTIE,
}
# bus-select solder jumpers, top side, right of the fader under the bus header: SUB 1-4 | AUX 1-4
JP_Y = [358.0 + 3.5 * k for k in range(4)]
for k, y in enumerate(JP_Y):
    FIX[f'JP{k + 1}'] = (30.5, y, 0, 'F'); FIX[f'JP{k + 5}'] = (35.0, y, 0, 'F')
# two boards on one bus rail both summers (master_group_review.md MG19): write the board's group number in GRP __
LABELS = [(32.75, 352.4, 'GRP __', 0.9), (30.5, 355.2, 'SUB', 1.0), (35.0, 355.2, 'AUX', 1.0)] + \
         [(28.3, y, str(k + 1), 0.9) for k, y in enumerate(JP_Y)]
HOLES = [(34.2, 117), (XC, 160), (XC, 215)] + FADER_HOLES   # (34.2, 117): XC is a pot's pins

RADIAL = {r for r, f in FPN.items() if 'CP_Radial' in f or 'C_Rect' in f}   # electrolytics, 2.2u film: too tall for the 11.5 mm panel gap -> bottom
RESERVOIR = sorted(RADIAL & set(B['POWER AND GROUNDS']), key=num)
take = lambda name, *drop: [r for r in B[name] if r not in FIX and r not in RADIAL and r not in drop]
switch_rs = lambda *sws: sorted({r for n, rs in ON.items() for s in sws if n in (f'RT_{s}A', f'RT_{s}B') for r in rs
                                 if r.startswith('R')}, key=num)
RET_ROUTE = switch_rs('SW4', 'SW5', 'SW6')                                  # 4K7s beside SW4-SW6
RET2_ROUTE = switch_rs('SW8', 'SW9', 'SW10')                                # and beside SW8-SW10
SUB_BUS = switch_rs('SW1') + sorted((ON['S_AFLJ'] | ON['SW2_ON']) - {'SW2'}, key=num)   # sub to MIX 4K7s, AFL 22K / 100K / 4K7
SUB_BUS = [r for r in SUB_BUS if r.startswith('R')]
NETS_OF = collections.defaultdict(set)
for n, rs in ON.items():
    for r in rs: NETS_OF[r].add(n)
def caps_first(r):
    """Beside-part order (first = closest to the pins): decouplers, summing-junction parts, other caps, the rest."""
    if r.startswith('C') and VAL[r].split()[0] in ('100n', '1u', '10u'): rank = 0
    elif any(n.endswith('_VE') for n in NETS_OF[r]): rank = 1
    else: rank = 2 if r.startswith('C') else 3
    return rank, num(r)
beside = lambda a: sorted((r for r, x in NEAR.items() if x == a and r not in RADIAL), key=caps_first)
# ICs before their NEAR parts: the aux sum + re-inverter first (the most parts, and the zone narrows at the board
# end), then the GC buffer + sub sum, then the sub re-inverter
SUMMERS = []
for u in dict.fromkeys((ic_on('AUX_SEL_VE'), ic_on('SUB_SEL_VE'), ic_on('S_MIX_DN'))): SUMMERS += [u] + beside(u)
RETURN = []                                     # each IC, then the parts beside it, then the rest
_ret = take('STEREO RETURN', *RET_ROUTE)
for u in (r for r in _ret if r.startswith('U')): RETURN += [u] + [r for r in beside(u) if r in _ret]
RETURN += [r for r in _ret if r not in RETURN]
RETURN2 = []
_ret2 = take('STEREO RETURN 2', *RET2_ROUTE)
for u in (r for r in _ret2 if r.startswith('U')): RETURN2 += [u] + [r for r in beside(u) if r in _ret2]
RETURN2 += [r for r in _ret2 if r not in RETURN2]
SUPPLY_R = [r for r in take('POWER AND GROUNDS') if VAL[r].startswith('10R') and {'+VBUS', '-VBUS'} & NETS_OF[r]]
POWER = [r for r in take('POWER AND GROUNDS') if r not in SUPPLY_R]
ZONES = [
 # bottom side first: links and electrolytics. The return rows' pins fill the bottom at the top of the board (RET1), so
 # the links go below them, where the bottom is empty (ribbons ~150 mm; the strip's is ~136 mm)
 ('jack-board links (bottom)', (1, 185, 37, 260), ['CN3', 'CN4'], 'B', 1.0),
 # E4 (emc_placement_study.md): the reservoirs under the supply filters, beside the header's power pins (30-34)
 ('rail reservoir caps (bottom)', (1, 285, 30, 345), RESERVOIR, 'B'),
 ('coupling caps and DRV134 output caps, beside their ICs (bottom; clear of the CN3 pin-1 mark)', (1, 96, 37, 444),
  sorted(RADIAL - set(RESERVOIR), key=num), 'B'),
 # top side
 # E4: the 10R supply filters first, beside the header's power pins, so unfiltered bus power runs a few mm
 ('supply filters at the bus header (E4)', (14, 294, 27, 318), SUPPLY_R, 'F'),
 ('GC buffer, summers + re-inverters (under the bus header)', (27, 300, 37.7, 444), SUMMERS, 'F'),
 ('power entry', (0.3, 299, 11, 444), POWER, 'F'),
 ('return 2 bus resistors at its switches', (1, 138, 37, 165), RET2_ROUTE, 'F'),
 ('return receivers, level buffers, PFL', (1, MAIN_Y0 + 2, 37, 165), RETURN, 'F'),
 ('return 2 receivers, level buffers, PFL', (1, MAIN_Y0 + 2, 37, 240), RETURN2, 'F'),
 ('sub insert, post-amp, pan buffers, DRV134', (1, 150, 37, 300), take('SUBGROUP', *SUMMERS, *SUB_BUS), 'F'),
 ('aux level buffer + DRV134, AFL', (1, 150, 37, 300), take('AUX MASTER', *SUMMERS), 'F'),
 ('bus resistors at the switches', (1, 240, 37, 300), RET_ROUTE + SUB_BUS, 'F'),
]
NOTES = ((106, 'RETURN 1 | PFL'), (128, 'RETURN 2 | PFL'), (150, 'RETURN 2 to MIX  1-2  3-4'), (172, 'AUX n | AFL'), (252, 'SUB PAN | to MIX'), (274, 'RETURN to MIX  1-2  3-4'),
         (292, 'SUB AFL'), (305, 'BUS HEADER (bottom, right)'), (356, 'bus select: close one SUB and one AUX, unique across the four groups; group number in GRP'),
         (372, 'FADER 100 mm'), (97, 'LINKS CN3, CN4 (bottom) to the jack board'))
# E9 (stab_caps_proposal.md): the C0G stability caps at the op-amp pins they stabilise (the packer had left them
# 6.6-13 mm away). Moved after packing (placer `moves`), so no other part re-packs into the slots they leave;
# bottom-side rotations are before the flip (board angle = 180 - rot)
MOVES = {'C35': (36.65, 377.02, 270, 'B'), 'C34': (33.13, 377.52, 180, 'B'), 'C51': (36.15, 135.77, 270, 'B'),
         'C39': (32.72, 243.65, 270, 'B'), 'C50': (35.88, 139.72, 180, 'B'), 'C76': (28.27, 182.88, 90, 'B'),
         'C44': (20.77, 116.38, 90, 'B'), 'C19': (2.27, 236.36, 270, 'B'), 'C7': (35.72, 398.13, 270, 'B'),
         'C59': (25.77, 158.11, 270, 'B'), 'C60': (28.52, 158.88, 180, 'B')}
# E10 (input_nets_proposal.md): one SMD part per long high-impedance op-amp input net moved so the net shrinks by
# >= 5 mm without its other net growing more than that (placer `moves`)
MOVES.update({'R57': (34.22, 160.38, 0, 'B'), 'R55': (32.47, 166.65, 180, 'B'), 'R53': (32.02, 157.11, 180, 'B'),
              'R32': (35.15, 384.77, 180, 'F'), 'R43': (6.27, 139.88, 180, 'B'), 'R46': (10.22, 140.88, 270, 'B'),
              'R10': (31.88, 438.72, 0, 'B')})
place(os.path.join(PROJ, 'group.net'), os.path.join(PROJ, 'group.kicad_pcb'),
      dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, moves=MOVES, holes=HOLES, zones=ZONES, near=NEAR, labels=LABELS, notes=NOTES,
           keepout=[(22.0, 185.0, 23.5, 215.0, 'B')],          # silk room beside the links' boxes
           hole_value='M3 standoff 11.5 mm', attach=True))
