"""Component placement for the group module (M1, master_panel_study.md): main board + jack board, placement only.
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_group.py      # -> group.kicad_pcb (38 x 378 mm), group_jack_board.kicad_pcb (38 x 65 mm)
8 HP x 12U panel in the strip's frame (placer.py): same y origin, fader, bus header and spade, so the ribbon and
the faders line up with the strips. The switches that carry a bus (sub to MIX, return routing, AFL/PFL) sit in
the strips' pan / routing / PFL rows, a few cm from the bus header. Zones follow gen_group.py's blocks
(group_parts.json). The jack board (5 jacks, 2x8 link) sits ~24 mm under the panel, y 0-65."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from placer import place, PROJ, W8 as W, XL, XR, XC, pot, sw, led, jack, FADER, BUS, SPADE, NETTIE, FADER_HOLES

JACK_Y1, MAIN_Y0, MAIN_Y1 = 65.0, 66.0, 444.0

# ================================================================ jack board
JACK_FIX = {'J2': jack(XL, 12), 'J1': jack(XR, 12),          # sub out | sub insert
            'J3': jack(XL, 34),                              # aux out | link header
            'J4': jack(XL, 56), 'J5': jack(XR, 56),          # return L | R
            'CN1': (31.0, 43.3, 180, 'B')}                   # 2x8 link, bottom side, pins x 31 / 33.54, y 25.5-43.3
JACK_HOLES = [(23, 26), (23, 42)]                            # M3 standoffs to the panel, ~24 mm (jack body height)
JACK_NOTES = ((12, 'SUB OUT | SUB INSERT'), (34, 'AUX OUT | link CN1 (bottom)'), (56, 'RETURN L | RETURN R'))
place(os.path.join(PROJ, 'group_jack_board.net'), os.path.join(PROJ, 'group_jack_board.kicad_pcb'),
      dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=[], notes=JACK_NOTES,
           hole_value='M3 standoff = jack body height (~24 mm)'))

# ================================================================ main board
d = json.load(open(os.path.join(PROJ, 'group_parts.json')))
seen, B = set(), {}
for title, refs in d['blocks']:                 # a package shared by two blocks stays in the first
    B[title.split('  ')[0].split(':')[0]] = [r for r in refs if not (r in seen or seen.add(r))]
NEAR = dict(d['near'])
NEAR.update({'C19': 'U4', 'C20': 'U4', 'C17': 'U4', 'C18': 'U4',           # DRV134 supply and output caps
             'C32': 'U7', 'C33': 'U7', 'C30': 'U7', 'C31': 'U7',
             'FB1': 'U1', 'R6': 'U1', 'C7': 'U1', 'FB2': 'U6', 'R25': 'U6', 'C27': 'U6',      # summing junctions short
             'R7': 'U2', 'R8': 'U2', 'R9': 'U2', 'R10': 'U2', 'R26': 'U6', 'R27': 'U6', 'R28': 'U6', 'R29': 'U6'})

FIX = {
 'RV4': pot(XL, 84, dual=True), 'SW7': sw(27, 84), 'D3': led(35, 84),        # RETURN level | PFL
 'RV3': pot(XL, 166), 'SW3': sw(26, 166), 'D2': led(34.5, 166),             # AUX n master | AFL (strips' aux 1|2 row)
 'RV2': pot(XL, 252, dual=True), 'SW1': sw(XR, 252),                         # SUB pan | to MIX (strips' pan row)
 'SW4': sw(6, 274), 'SW5': sw(17, 274), 'SW6': sw(28, 274),                  # return to MIX, 1-2, 3-4 (routing row)
 'SW2': sw(6, 292), 'D1': led(14.2, 292),                                    # SUB AFL (strips' PFL row)
 'RV1': FADER, 'CN2': BUS, 'CN1': SPADE, 'NT1': NETTIE,
}
# bus-select solder jumpers, top side, right of the fader under the bus header: SUB 1-4 | AUX 1-4
JP_Y = [358.0 + 3.5 * k for k in range(4)]
for k, y in enumerate(JP_Y):
    FIX[f'JP{k + 1}'] = (30.5, y, 0, 'F'); FIX[f'JP{k + 5}'] = (35.0, y, 0, 'F')
LABELS = [(30.5, 355.2, 'SUB', 1.0), (35.0, 355.2, 'AUX', 1.0)] + [(28.3, y, str(k + 1), 0.9) for k, y in enumerate(JP_Y)]
HOLES = [(XC, 72), (XC, 140), (XC, 215)] + FADER_HOLES

RADIAL = {'C1', 'C2', 'C3', 'C4', 'C10', 'C11', 'C16', 'C17', 'C18', 'C23', 'C24', 'C28', 'C30', 'C31',
          'C42', 'C43', 'C47', 'C49'}                # electrolytics: too tall for the 11.5 mm panel gap -> bottom
take = lambda name, *drop: [r for r in B[name] if r not in FIX and r not in RADIAL and r not in drop]
RET_ROUTE = ['R56', 'R57', 'R58', 'R59', 'R60', 'R61']                     # 4K7s beside SW4-SW6
SUB_BUS = ['R20', 'R21', 'R22', 'R23', 'R24']                              # sub to MIX 4K7s, AFL 22K / 100K / 4K7
SUMMERS = ['U1', 'C5', 'C6', 'FB1', 'R6', 'C7', 'U2', 'C8', 'C9', 'R7', 'R8', 'R9', 'R10',    # ICs before their NEAR parts
           'U6', 'C25', 'C26', 'FB2', 'R25', 'C27', 'R26', 'R27', 'R28', 'R29']
POWER = take('POWER AND GROUNDS')
ZONES = [
 # bottom side first: links and electrolytics
 ('jack-board link (bottom)', (12, MAIN_Y0, 37, 140), ['CN3'], 'B'),
 ('rail reservoir caps (bottom)', (1, 360, 37, 444), ['C1', 'C2', 'C3', 'C4'], 'B'),
 ('return coupling (bottom; clear of the CN3 pin-1 mark)', (1, 96, 37, 165), ['C42', 'C43', 'C47', 'C49'], 'B'),
 ('aux / sub coupling and DRV134 outputs (bottom)', (1, 140, 37, 300),
  ['C17', 'C18', 'C30', 'C31', 'C28', 'C10', 'C11', 'C16', 'C23', 'C24'], 'B'),
 # top side
 ('GC buffer, summers + re-inverters (under the bus header)', (27, 300, 37.7, 444), SUMMERS, 'F'),
 ('power entry', (0.3, 299, 11, 444), POWER, 'F'),
 ('return receivers, level buffers, PFL', (1, MAIN_Y0 + 2, 37, 165), take('STEREO RETURN', *RET_ROUTE), 'F'),
 ('aux level buffer + DRV134, AFL', (1, 150, 37, 245), take('AUX MASTER', *SUMMERS), 'F'),
 ('sub insert, post-amp, pan buffers, DRV134', (1, 170, 37, 300), take('SUBGROUP', *SUMMERS, *SUB_BUS), 'F'),
 ('bus resistors at the switches', (1, 240, 37, 300), RET_ROUTE + SUB_BUS, 'F'),
]
NOTES = ((84, 'RETURN | PFL'), (166, 'AUX n | AFL'), (252, 'SUB PAN | to MIX'), (274, 'RETURN to MIX  1-2  3-4'),
         (292, 'SUB AFL'), (305, 'BUS HEADER (bottom, right)'), (356, 'bus select: close one SUB, one AUX'),
         (372, 'FADER 100 mm'), (75, 'LINK CN3 (bottom) to the jack board'))
place(os.path.join(PROJ, 'group.net'), os.path.join(PROJ, 'group.kicad_pcb'),
      dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, holes=HOLES, zones=ZONES, near=NEAR, labels=LABELS, notes=NOTES,
           hole_value='M3 standoff 11.5 mm'))
