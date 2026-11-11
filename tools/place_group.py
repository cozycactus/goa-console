"""Component placement for the group module (M1, docs/studies/master_panel_study.md): main board + jack board, placement only.
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_group.py      # -> group.kicad_pcb (38 x 349.5 mm), group_jack_board.kicad_pcb (38 x 93.5 mm)
8 HP x 12U panel in the strip's frame (placer.py): same y origin, fader, bus header and spade, so the ribbon and
the faders line up with the strips. The switches that carry a bus (sub to MIX, return routing, AFL/PFL) sit in
the strips' pan / routing / PFL rows, a few cm from the bus header. Zones follow gen_group.py's blocks
(group_parts.json). The jack board (7 jacks, 2x8 + 2x5 links across, straight ribbons) sits ~24 mm under the panel, y 0-93.5.
RET1 (docs/reviews/feature_gaps.md, 2026-10-26): return 2's jacks are a fourth row (y 78), so the main board starts at y 94.5;
RETURN 1 / RETURN 2 knobs at y 106 / 128, return 2's routing keys at y 150, AUX at y 172."""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from verify import sexp, field
import netnames
from placer import place, PROJ, W8 as W, XL, XR, XC, pot, sw, led, jack, FADER, BUS, SPADE, NETTIE, FADER_HOLES

JACK_Y1, MAIN_Y0, MAIN_Y1 = 93.5, 94.5, 444.0

# ================================================================ jack board
JACK_FIX = {'J2': jack(XL, 12), 'J1': jack(XR, 12),          # sub out | sub insert
            'J3': jack(XL, 31),                              # aux out, 3 mm up from the 22 mm row pitch (2026-11-11): a header
                                                             # across needs a pad-free band of 10.2 mm and the rows leave 7.63
            'J4': jack(XL, 56), 'J5': jack(XR, 56),          # return 1 L | R
            'J6': jack(XL, 78), 'J7': jack(XR, 78),          # return 2 L | R (RET1)
            # Both links across the board, pin 1 on the right end, like the main board's CN3 / CN4 and the strip's CN5
            # (2026-11-11, docs/decisions.md): each ribbon runs straight, no fold. Were along the board (CN1
            # (33.04, 24.52, 0), CN2 (19.9, 39.0, 180)), which took two folds and a strain-relief wrap per cable
            'CN1': (24.89, 44.67, 90, 'B'),                  # 2x8, centre (16.0, 43.4): the short upper cable
            'CN2': (31.68, 26.27, 90, 'B')}                  # 2x5 (return 2), centre (26.6, 25.0), in the slot beside J3; its
                                                             # cable runs under CN1's socket
JACK_HOLES = []                                              # M3 standoffs to the panel, ~24 mm (jack body height):
JACK_FIX.update({'H1': (XL, 89.8, 0, 'F'), 'H2': (XR, 89.8, 0, 'F')})   # plated, on CHASSIS (docs/studies/ground_study.md G2); below
                                                             # the last row since the links fill the free slot
JACK_NOTES = ((12, 'SUB OUT | SUB INSERT'), (31, 'AUX OUT | link CN2 (bottom); CN1 below it'), (56, 'RETURN 1 L | R'),
              (78, 'RETURN 2 L | R'))
place(os.path.join(PROJ, 'boards', 'group_jack_board', 'group_jack_board.net'), os.path.join(PROJ, 'boards', 'group_jack_board', 'group_jack_board.kicad_pcb'),
      dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=[], notes=JACK_NOTES,
           hole_value='M3 standoff = jack body height (~24 mm)'))

# ================================================================ main board
d = json.load(open(os.path.join(PROJ, 'boards', 'group', 'group_parts.json')))
seen, B = set(), {}
for title, refs in d['blocks']:                 # a package shared by two blocks stays in the first
    B[title.split('  ')[0].split(':')[0]] = [r for r in refs if not (r in seen or seen.add(r))]
# Beside-parts (decouplers, summing-junction parts, DRV134 caps) come from the generator (group_parts.json 'near');
# groups below are derived from the netlist, so a regeneration that renumbers parts needs no edits here
NEAR = dict(d['near'])
net = sexp(open(os.path.join(PROJ, 'boards', 'group', 'group.net')).read())
comps = next(c for c in net[1:] if isinstance(c, list) and c[0] == 'components')
FPN = {field(c, 'ref'): field(c, 'footprint') for c in comps[1:]}
VAL = {field(c, 'ref'): field(c, 'value') for c in comps[1:]}
ON = {field(n, 'name').lstrip('/'): {field(x, 'ref') for x in n[1:] if isinstance(x, list) and x[0] == 'node'}
      for n in next(c for c in net[1:] if isinstance(c, list) and c[0] == 'nets')[1:]}
_rn = netnames.renames(os.path.join(PROJ, 'boards', 'group', 'group.net'))    # a drawn schematic leaves nets inside a drawing unlabelled
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
# two boards on one bus rail both summers (docs/reviews/master_group_review.md MG19): write the board's group number in GRP __
LABELS = [(32.75, 352.4, 'GRP __', 1.0), (30.5, 355.2, 'SUB', 1.0), (35.0, 355.2, 'AUX', 1.0)] + \
         [(28.3, y, str(k + 1), 1.0) for k, y in enumerate(JP_Y)]   # JLCPCB: silk text >= 1.0 mm
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
POWER = [r for r in take('POWER AND GROUNDS') if r not in SUPPLY_R and VAL[r] != 'MBR140SFT1G']   # CS10's by MOVES
ZONES = [
 # bottom side first: links and electrolytics. The return rows' pins fill the bottom at the top of the board (RET1), so
 # the links go below them, where the bottom is empty. The two headers are packed along the board, where they stood
 # until 2026-11-11, and LINKS (below) then lays them across: every other part was packed around them, and a change
 # here re-packs the board (tried: 156 parts move with the headers fixed across, 193 with the op-amps held too)
 ('jack-board links (bottom)', (1, 185, 37, 260), ['CN3', 'CN4'], 'B', 1.0),
 # E4 (docs/studies/emc_placement_study.md): the reservoirs under the supply filters, beside the header's power pins (30-34)
 ('rail reservoir caps (bottom)', (1, 285, 30, 345), RESERVOIR, 'B'),
 ('coupling caps and DRV134 output caps, beside their ICs (bottom)', (1, 96, 37, 444),
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
         (372, 'FADER 100 mm'), (184, 'LINKS CN3 (16-way), CN4 (10-way), bottom, across: straight ribbons to the jack board'))
# E9 (docs/proposals/stab_caps_proposal.md): the C0G stability caps at the op-amp pins they stabilise (the packer had left them
# 6.6-13 mm away). Moved after packing (placer `moves`), so no other part re-packs into the slots they leave;
# bottom-side rotations are before the flip (board angle = 180 - rot)
MOVES = {'C35': (36.65, 377.02, 270, 'B'), 'C34': (33.13, 377.52, 180, 'B'), 'C51': (36.15, 135.77, 270, 'B'),
         'C39': (32.72, 243.65, 270, 'B'), 'C50': (35.88, 139.72, 180, 'B'), 'C76': (32.5, 183.75, 180, 'B'),   # C76: CN3 lies under U15's pin 3 now, 3.3 mm
         'C44': (20.77, 116.38, 90, 'B'), 'C19': (2.27, 236.36, 270, 'B'), 'C7': (35.72, 398.13, 270, 'B'),
         'C59': (25.77, 158.11, 270, 'B'), 'C60': (28.52, 158.88, 180, 'B')}
# E10 (docs/proposals/input_nets_proposal.md): one SMD part per long high-impedance op-amp input net moved so the net shrinks by
# >= 5 mm without its other net growing more than that (placer `moves`)
MOVES.update({'R57': (32.25, 159.5, 180, 'B'), 'R55': (27.75, 161.75, 0, 'B'), 'R53': (32.02, 157.11, 180, 'B'),   # R57 / R55 make room for C62 (LINKS)
              'R32': (35.15, 384.77, 180, 'F'), 'R43': (6.27, 139.88, 180, 'B'), 'R46': (10.22, 140.88, 270, 'B'),
              'R10': (31.88, 438.72, 0, 'B')})
# E11 (docs/proposals/decouplers_proposal.md): decouplers more than 5.5 mm from their supply pin moved to it, most on the bottom
# under the pin (placer `moves`)
MOVES.update({'C43': (6.97, 218.9, 90, 'F')})
# CS10 (docs/proposals/cs10_proposal.md, signed off 2026-10-27): the reverse Schottkys beside C1 (+VA) and C2 (-VA), placed by MOVES alone (never packed)
CS10 = {'D5': (28.5, 290.25, 90, 'F'), 'D6': (14.5, 304.0, 0, 'F')}
MOVES.update(CS10)
# CS4b (docs/proposals/cs4b_proposal.md, signed off 2026-10-27): the jack-link clamps (BAV199) beside CN3 / CN4, placed by MOVES alone
CS4B = {'D7': (28.75, 191.0, 90, 'F'), 'D8': (29.5, 190.5, 0, 'B'), 'D9': (25.5, 192.0, 90, 'B'),       # at the pins of the headers
        'D10': (20.0, 176.25, 270, 'B'), 'D11': (19.25, 172.0, 270, 'B'), 'D12': (17.5, 194.5, 90, 'B'),   # across (LINKS): 2.1-9.5 mm
        'D13': (12.5, 176.25, 270, 'B'), 'D14': (12.5, 172.0, 270, 'B'), 'D15': (5.25, 176.25, 270, 'B'),  # from pad to pin, were 8.2-20.2
        'D16': (6.5, 187.75, 90, 'F'), 'D17': (34.5, 208.75, 90, 'F'), 'D18': (26.0, 200.0, 270, 'F'),
        'D19': (25.5, 197.0, 270, 'B'), 'D20': (33.25, 213.25, 90, 'F')}
MOVES.update(CS4B)
# CS4c (docs/proposals/cs4c_proposal.md): the 22R inside each DRV135 loop at its output pin (U4 sub out, U7 aux out), placed by MOVES alone
CS4C = {'R119': (35.25, 197.25, 180, 'B'), 'R120': (29.25, 197.0, 0, 'B'), 'R121': (2.0, 209.0, 90, 'F'),   # R119 / R120 went with U4 (LINKS)
        'R122': (1.75, 205.0, 90, 'F')}
MOVES.update(CS4C)
# CS2b (docs/proposals/cs2b_proposal.md): the sub pan buffers' law network (U3B pan L, U5A pan R), placed by MOVES alone
CS2B = {'C96': (4.25, 240.75, 90, 'B'), 'R124': (2.0, 240.0, 90, 'B'), 'R125': (12.75, 236.75, 90, 'F'),
        'R123': (3.75, 244.25, 0, 'B'), 'C97': (28.75, 243.25, 0, 'B'), 'R127': (25.25, 244.5, 90, 'B'),
        'R128': (22.25, 241.0, 90, 'F'), 'R126': (29.0, 245.75, 0, 'B')}
MOVES.update(CS2B)
# docs/proposals/clicks_proposal.md RV7 (signed off 2026-10-28): the aux AFL film beside its 22K, bottom, placed by MOVES alone
CLICKS = {'C98': (23.72, 263.11, 0, 'B')}
MOVES.update(CLICKS)
# Straight jack-board links (2026-11-11, docs/decisions.md): CN3 / CN4 across the board, pin 1 on the right end, on the jack
# board's CN1 / CN2 lines (x 16.0 / 26.6). The 16-way is the upper cable into CN3; the 10-way passes under CN3's socket
# and comes up into CN4, 14.75 mm of run further on. Only what the two headers, their pin-1 arrows and the cables'
# keepouts (KEEP_TALL) displace is moved (placer `moves`). The small parts went to the free spot nearest to their own
# pins, found by a probe with the placer's rules; the tall capacitors to the few spots that are free on both sides,
# chosen by hand: a local solution, not the best one there is
LINKS = {'CN3': (24.89, 184.77, 90, 'B'), 'CN4': (31.68, 205.52, 90, 'B'),      # centres (16.0, 183.5) / (26.6, 204.25)
         'U12': (16.25, 188.75, 0, 'F'), 'U4': (31.75, 199.0, 0, 'F'),          # off the header pads: 3.0 mm down, 6.75 mm up
         # tall bottom parts: C80 / C82 / C81 in the column CN3 left; C62 at U9 (2.9 mm from pin 5, was 16.5) and C56 on C55's
         # spot (16.3 mm from pin 3, was 3.8); C55 where C61 stood; C61 and C22 by the pan row (54.7 / 65.5 mm from their spots)
         'C80': (7.75, 192.9, 0, 'B'), 'C82': (6.0, 203.7, 90, 'B'), 'C81': (7.75, 209.5, 0, 'B'),
         'C62': (36.0, 164.5, 0, 'B'), 'C56': (4.5, 159.0, 180, 'B'), 'C55': (30.45, 213.85, 0, 'B'),
         'C61': (14.0, 264.0, 0, 'B'), 'C22': (21.0, 246.5, 90, 'B'),
         # U12's, U13's, U15's and U4's parts that stood on the new header pads or under the moved ICs
         'C72': (15.75, 190.5, 270, 'B'), 'C74': (18.75, 190.5, 270, 'B'), 'C75': (12.75, 190.75, 180, 'B'),
         'R80': (14.5, 194.25, 90, 'B'), 'R81': (10.5, 189.5, 180, 'F'), 'R85': (21.75, 192.0, 0, 'B'),
         'R86': (21.75, 189.75, 180, 'B'), 'C89': (21.5, 201.0, 180, 'F'), 'C90': (18.75, 205.25, 0, 'F'),
         'R95': (14.0, 204.25, 0, 'B'), 'R97': (14.0, 202.0, 0, 'B'), 'R115': (24.5, 180.25, 0, 'F'),
         'C23': (34.25, 193.75, 90, 'B'), 'C24': (34.25, 204.25, 90, 'F'), 'R21': (17.25, 234.25, 90, 'F')}
MOVES.update(LINKS)
# The room a cable needs under the board on its way into its socket (ribbon plane 9.4 mm under the board at the socket,
# the jack board's 12.5 mm lower), as (x0, y0, x1, y1, side, tallest part allowed), cable width + 1 mm a side:
#   16-way, before CN3's socket edge: no 100 uF can for 30 mm, nothing over 9 mm for 17.5 mm;
#   10-way where it runs alone (3.7 mm lower at CN3, it passes under that socket): no 100 uF can for 30 mm, nothing over 9 mm for 7 mm;
#   10-way from CN3's socket up into CN4: nothing over 9 mm.
# A model, not yet tried on a cable; the cables must be cut with slack (a taut 16-way bears on C14 / C20, 38-49 mm before CN3)
(_x3, _y3), (_x4, _y4) = (LINKS['CN3'][0] - 8.89, LINKS['CN3'][1] - 1.27), (LINKS['CN4'][0] - 5.08, LINKS['CN4'][1] - 1.27)   # header centres
_l3, _r3, _l4, _r4 = _x3 - 11.16, _x3 + 11.16, _x4 - 7.35, _x4 + 7.35           # 16 / 10 conductors at 1.27 mm, + 1 mm a side
KEEP_TALL = [(_l3, _y3 - 33, _r3, _y3 - 20.5, 'B', 13.5), (_l3, _y3 - 20.5, _r3, _y3 - 3, 'B', 9.0),
             (_r3, _y3 - 33, _r4, _y3 - 10, 'B', 13.5), (_r3, _y3 - 10, _r4, _y3 - 3, 'B', 9.0),
             (_l4, _y3 - 3, _r4, _y4 - 3, 'B', 9.0)]
HEIGHTS = {'CP_Radial_D10': 17.5, 'CP_Radial_D8': 13.0, 'CP_Radial_D5': 12.5, 'C_Rect_L7.2': 13.0}   # seated, max, of the fitted parts
_unlisted = sorted(r for r in RADIAL if not any(k in FPN[r] for k in HEIGHTS))  # (UES 10 x 16 / 8 x 11.5, ECE-A 5 x 11, MMK5 13 mm): a
if _unlisted: raise SystemExit(f'tall capacitors without a height: {_unlisted}')   # new footprint must not count as low; review after a part change
for z in ZONES: z[2][:] = [r for r in z[2] if r not in CS4C and r not in CS2B and r not in CLICKS]   # their drivers' blocks list them too
# docs/proposals/untangle_proposal.md: two-pad parts turned in place (degrees) so their ratsnest crosses less, measured with
# tools/ratsnest.py (placer `turns`, after packing and the moves)
TURNS = {'JP7': 90, 'R5': 90, 'R11': 180, 'R20': 180, 'R22': 180, 'R25': 180, 'R26': 180, 'R30': 180, 'R34': 180,
         'R37': 180, 'R51': 180, 'R54': 90, 'R56': 180, 'R59': 180, 'R61': 180, 'R62': 180, 'R72': 180, 'R73': 180,
         'R74': 180, 'R77': 180, 'R78': 180, 'R89': 180, 'R90': 180, 'R96': 180, 'R107': 180,
         'R109': 180, 'R110': 180, 'R112': 180, 'R117': 270}   # R80, R86, R115: placed by LINKS since 2026-11-11
place(os.path.join(PROJ, 'boards', 'group', 'group.net'), os.path.join(PROJ, 'boards', 'group', 'group.kicad_pcb'),
      dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, moves=MOVES, moves_only=tuple(CS10) + tuple(CS4B) + tuple(CS4C) + tuple(CS2B) + tuple(CLICKS), wire=tuple(CS4C) + tuple(CLICKS), attach_as={'R36': ('output', 'U5', '7')}, turns=TURNS, layers=4, rails=(0.5, 5.5), holes=HOLES, zones=ZONES, near=NEAR, labels=LABELS, notes=NOTES,
           # the first keepout was the silk room beside the links' boxes as packed; it stays only so that the packing stays
           keepout=[(22.0, 185.0, 23.5, 215.0, 'B')] + KEEP_TALL, heights=HEIGHTS,
           hole_value='M3 standoff 11.5 mm', attach=True))
