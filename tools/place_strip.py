"""Component placement for the channel-strip PCBs, v4.0 (KiCad 10 pcbnew API). Placement only: no copper.
Two boards, each from its own netlist; the layout is picked from the parts (CN5 = jack board):
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_strip.py channel_strip.net channel_strip.kicad_pcb     # main board, 38 x 400 mm
  $KPY tools/place_strip.py jack_board.net jack_board.kicad_pcb              # jack board, 38 x 43 mm
Panel: 8 HP x 12U Eurorack-style (40.3 x 514 mm), two pot columns, jacks on the panel (study:
docs/studies/strip_panel_study.md). y = 0 is 11 mm below the panel's top edge (end rail) and grows towards the fader;
both boards use these coordinates, so the two files overlay on the panel. The jack board (y 0-43) sits
~24 mm under the panel (a 1/4" plug goes ~30 mm deep); the main board (y 44-444) at 11.5 mm. A 10-way
IDC ribbon joins CN5 (jack board, bottom) to CN3 (main board, bottom).
Panel parts sit at fixed coordinates; the rest is packed by zone (engine: placer.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from placer import place, W8 as W, XL, XR, XC, pot, sw, led, led3, jack, FADER, BUS, SPADE, NETTIE

JACK_Y1, MAIN_Y0, MAIN_Y1 = 43.0, 44.0, 444.0   # jack board y 0-43, main board y 44-444 (514 mm 12U panel)

# ================================================================ jack board
JACK_FIX = {'J1': jack(XL, 12), 'J2': jack(XR, 12), 'J5': jack(XL, 32),              # line in, insert / direct out
            # link header, bottom side, pins x 31 / 33.54, y 26.6-36.8 (pin 1 low, so its silk arrow points inboard)
            'CN5': (31.0, 36.8, 180, 'B')}
# M3 standoffs to the panel, length = jack body height (~24 mm); the jack caps hold the board too
# plated, on CHASSIS (H1 / H2 in the jack board schematic, docs/studies/ground_study.md G2): they bond the sleeves to the panel
JACK_HOLES = []
JACK_FIX.update({'H1': (23, 27, 0, 'F'), 'H2': (23, 37, 0, 'F')})
# E5 (docs/studies/emc_placement_study.md): the RF caps between J1's tip / ring pads and its sleeve pad, on the bottom, so the shunt
# to CHASSIS is a few mm long. The standoffs can't come closer to J1: the jack courtyards leave no M3 spot nearer
JACK_FIX.update({'C8': (6.2, 9.0, 270, 'B'), 'C9': (8.8, 12.0, 0, 'B')})
JACK_ZONES = []
JACK_NOTES = ((12, 'LINE IN | INSERT'), (32, 'DIRECT OUT | link CN5 (bottom)'))

# ================================================================ main board
FIX = {
 'SW15': sw(XR, 50), 'RV9': pot(XL, 54), 'SW11': sw(XR, 61), 'D2': led3(20.6, 50),           # Ø, gain, HPF in, OL
 'RV10': pot(XL, 76), 'RV16': pot(XR, 76, dual=True, right=True),                        # HF, HPF freq
 'RV11': pot(XL, 98), 'RV12': pot(XR, 98, dual=True, right=True),                         # HI-MID gain, freq
 'RV13': pot(XL, 120), 'RV14': pot(XR, 120, dual=True, right=True),                       # LO-MID gain, freq
 'RV15': pot(XL, 142), 'SW12': sw(26, 142), 'D5': led(34.5, 142),                         # LF, EQ + LED
 'RV2': pot(XL, 166), 'RV3': pot(XR, 166, right=True),                                    # aux 1, 2
 'RV4': pot(XL, 188), 'RV5': pot(XR, 188, right=True),                                    # aux 3, 4
 'RV6': pot(XL, 210), 'RV7': pot(XR, 210, right=True),                                    # aux 5, 6
 'SW8': sw(XR - 22, 230), 'SW9': sw(XR - 11, 230), 'SW10': sw(XR, 230),                   # PRE 1-2, 3-4, 5-6
 'RV8': pot(XL, 252, dual=True, sx=10), 'SW14': sw(XR, 246), 'SW13': sw(XR, 258),                # pan, PAN, DIR
 'SW5': sw(XR - 22, 274), 'SW6': sw(XR - 11, 274), 'SW7': sw(XR, 274),                    # L-R, 1-2, 3-4 (key rows end
 'D6': led(XR - 22, 283), 'D7': led(XR - 11, 283), 'D8': led(XR, 283),                    # routing LEDs   in the right
 'SW3': sw(XR - 22, 292), 'D3': led(XR - 13.8, 292), 'SW4': sw(XR - 4, 292), 'D4': led(XR + 4.2, 292),  # PFL, ON  (column)
 'RV1': FADER,                           # fader, slot centre y = 372
 'CN1': BUS,                             # bus header, bottom side, pins at x = 31.46 / 34, y = 305..346; pin 1 at the
                                         # bottom end so its silk arrow points inboard, not off the edge
 'CN4': SPADE,                           # ground spade, bottom side, left of the fader body
 'NT1': NETTIE,                          # AGND-LGND net tie beside the spade (no courtyard: keep it clear by hand)
}
# E9 (docs/proposals/stab_caps_proposal.md): the C0G stability caps at the pins they stabilise (the packer had left them 6-22 mm away).
# Moved after packing (placer `moves`), so no other part re-packs into the slots they leave; bottom-side rotations are
# before the flip (board angle = 180 - rot)
MOVES = {'C84': (5.72, 149.9, 180, 'F'), 'C81': (17.72, 243.65, 180, 'F'), 'C37': (4.47, 63.63, 270, 'B'),
         'C71': (28.22, 151.13, 180, 'B'), 'C80': (13.02, 238.38, 90, 'B'), 'C83': (3.77, 240.38, 180, 'B'),
         'C41': (15.47, 89.63, 180, 'B'), 'C78': (2.27, 65.88, 270, 'B'), 'C75': (3.77, 130.38, 180, 'B'),
         'C85': (11.27, 90.13, 180, 'B'), 'C86': (6.27, 84.61, 0, 'F'), 'C70': (26.52, 148.61, 0, 'B')}
# E10 (docs/proposals/input_nets_proposal.md): one SMD part per long high-impedance op-amp input net moved so the net shrinks by
# >= 5 mm without its other net growing more than that (placer `moves`)
MOVES.update({'R50': (15.47, 91.63, 0, 'B'), 'R92': (34.47, 127.13, 270, 'B'), 'R103': (19.77, 84.11, 270, 'F'),
              'R55': (25.77, 147.86, 0, 'F'), 'R85': (7.77, 130.38, 180, 'B'), 'R94': (35.22, 135.15, 180, 'B'),
              'R67': (2.27, 147.86, 90, 'B'), 'R9': (4.52, 67.13, 270, 'B'), 'R57': (32.02, 124.86, 270, 'B')})
# E11 (docs/proposals/decouplers_proposal.md): decouplers more than 5.5 mm from their supply pin moved to it, most on the bottom
# under the pin (placer `moves`)
MOVES.update({'C60': (28.77, 384.61, 180, 'B'), 'C57': (28.77, 367.11, 180, 'B'), 'C61': (35.72, 385.88, 180, 'B'),
              'C58': (35.72, 368.38, 180, 'B'), 'C92': (18.59, 56.77, 270, 'B'), 'C93': (24.15, 58.22, 270, 'B'),
              'C25': (13.27, 243.65, 0, 'F'), 'C59': (34.72, 383.11, 90, 'B'), 'C56': (34.72, 365.61, 90, 'B'),
              'C54': (28.77, 352.61, 180, 'B'), 'C53': (35.72, 352.61, 180, 'B'), 'C98': (2.84, 313.77, 180, 'B'),
              'C55': (34.72, 355.38, 270, 'B')})
# PAN1 (docs/proposals/pan_buffer_proposal.md): U3 and U8 pinned where they were, so pan buffer L (U8B) stays beside the pan pot
FIX.update({'U2': (33.245, 403.245, 90, 'F'), 'U3': (16.745, 239.745, 0, 'F'), 'U8': (4.745, 239.745, 0, 'F'), 'C17': (18.26875, 261.34, 0, 'B'),
            'C16': (16.0, 202.3, 90, 'B'), 'C79': (10.2, 242.35, 270, 'F'),
            'R38': (32.61, 413.72, 0, 'F'), 'JP1': (36.38, 414.22, 90, 'F'), 'R18': (32.88, 416.22, 0, 'F'),
            'R44': (29.225, 418.995, 0, 'F')})
# docs/proposals/untangle_proposal.md: two-pad parts turned in place (degrees) so their ratsnest crosses less, measured with
# tools/ratsnest.py (placer `turns`, after packing and the moves)
TURNS = {'C12': 180, 'C28': 180, 'C97': 180, 'C99': 180, 'R5': 90, 'R6': 180, 'R11': 180, 'R15': 180, 'R16': 180,
         'R17': 180, 'R23': 180, 'R24': 180, 'R25': 180, 'R26': 180, 'R28': 180, 'R29': 180, 'R33': 270, 'R34': 270,
         'R37': 270, 'R46': 180, 'R47': 270, 'R58': 180, 'R60': 90, 'R64': 180, 'R76': 180, 'R79': 180, 'R86': 180,
         'R88': 180, 'R96': 180, 'R99': 180, 'R100': 180, 'R106': 180, 'R107': 180, 'R108': 180, 'R117': 180,
         'R119': 180}
# v4.9 (P1): the hold networks no longer touch the comparator outputs (R126 / R127 between), so the placer would
# re-anchor them; kept where v4.8 had them (angles before their TURNS), with U17, which their fixed spots would
# otherwise push 50 mm down (its ring no longer fits)
FIX.update({'U17': (3.745, 316.245, 90, 'F'), 'C97': (32.77, 67.84, 0, 'F'), 'R115': (35.77, 72.84, 90, 'F'), 'C99': (2.34, 306.72, 0, 'F'), 'R121': (9.34, 322.22, 90, 'F')})
# strip v4.9 (P1 / P2 / E6, 2026-10-27): the five new parts are placed by MOVES alone (placer `moves_only`), so the
# rest of the board keeps its packing: R126 / R127 between each comparator output and its hold cap, C100 under R41,
# C101 / C102 across Q3's / Q4's base and emitter (probed like E9, both sides)
NEW49 = {'R126': (31.27, 75.84, 90, 'B'), 'R127': (6.09, 313.97, 90, 'B'), 'C100': (31.8575, 88.88, 90, 'B'),
         'C101': (28.9125, 49.795, 270, 'B'), 'C102': (32.4125, 55.045, 0, 'B')}
MOVES.update(NEW49)
# CS1 (docs/proposals/cs1_proposal.md, signed off 2026-10-27): the multi-point overload detector's parts by MOVES alone, like
# NEW49: each tap's 1K + BAV99 beside its op-amp (RECV / GOUT at U1, EQOUT at C51, FPOST at U2; D1, now a SOT-23 BAV99,
# where the DO-35 was), U18 and the negative side's divider / hold / discharge beside U4 (probed free spots)
CS1 = {'D1': (35.75, 100.75, 90, 'B'), 'R128': (2.25, 61.5, 90, 'B'), 'D12': (2.5, 58.0, 0, 'B'),
       'R129': (5.5, 58.75, 90, 'B'), 'D13': (12.75, 58.75, 90, 'B'), 'R130': (13.0, 78.75, 0, 'B'),
       'D14': (12.5, 76.0, 0, 'B'), 'R131': (35.5, 405.75, 90, 'B'), 'D15': (35.0, 410.5, 0, 'B'),
       'U18': (34.25, 82.5, 270, 'B'), 'C104': (36.25, 84.5, 90, 'F'), 'R132': (34.25, 77.5, 0, 'B'),
       'R133': (34.25, 75.25, 0, 'B'), 'R134': (33.75, 70.75, 0, 'B'), 'C103': (34.25, 73.0, 0, 'B'),
       'R135': (28.25, 77.5, 0, 'B')}
MOVES.update(CS1)
# CS10 (docs/proposals/cs10_proposal.md, signed off 2026-10-27): the reverse Schottkys beside C1 (+VA) and C3 (-VA), placed by MOVES alone
CS10 = {'D16': (15.5, 300.5, 0, 'F'), 'D17': (3.25, 298.25, 0, 'F')}
MOVES.update(CS10)
# CS4 (docs/proposals/cs4_proposal.md, signed off 2026-10-27): the jack-link clamps (BAV199) beside CN3, bottom side, placed by MOVES alone
CS4 = {'D18': (31.75, 138.25, 0, 'B'), 'D19': (25.0, 124.75, 0, 'B'), 'D20': (20.25, 138.5, 0, 'B'),
       'D21': (25.0, 120.5, 0, 'B'), 'D22': (13.0, 124.75, 0, 'B')}
MOVES.update(CS4)
# CS2 (docs/proposals/cs2_proposal.md): the pan buffers' gain resistors, their 22p and the 3K3s back to the wipers, under U8 / U3 on the bottom,
# placed by MOVES alone
CS2 = {'R137': (7.5, 240.5, 90, 'B'), 'R138': (10.0, 240.5, 90, 'B'), 'R136': (7.25, 243.75, 0, 'B'),
        'R140': (20.5, 235.75, 0, 'B'), 'R141': (10.25, 236.5, 90, 'B'), 'R139': (11.75, 244.5, 90, 'B'),
        'C105': (6.25, 237.25, 0, 'B'), 'C106': (16.5, 235.75, 0, 'B')}
MOVES.update(CS2)
# CS6 (docs/proposals/cs6_proposal.md): R1-R4 are fusible 1206s (Vishay M25SI), too big for the E4 cluster, so they leave the packer:
# placed by MOVES alone at probed spots by the header's power pins (R1 / R2 top, at their old spots; R3 / R4 bottom).
# C2 / C4 stay fixed where they were, and the old 0805 spots are kept out of packing, so every other part packs as before
CS6 = {'R1': (32.75, 297.0, 90, 'F'), 'R2': (28.75, 298.5, 0, 'F'), 'R3': (31.75, 297.75, 0, 'B'), 'R4': (25.0, 305.0, 0, 'B')}
MOVES.update(CS6)
# docs/proposals/clicks_proposal.md RV3 / RV4 (signed off 2026-10-28): the gain stage's 1M keeper on the bottom under U1 (pads 8.6 / 9.9 mm
# from U1 pins 6 / 7: the nearest free spot) and the direct out's cold-leg 33u NP beside R73 (6.8 mm), placed by MOVES alone
# (spots probed clear of courtyards and leads)
CLICKS = {'R142': (7.21, 54.56, 0, 'B'), 'C107': (30.03, 199.0, 0, 'B')}
MOVES.update(CLICKS)
# docs/proposals/clicks_followup_proposal.md RV3b (signed off 2026-10-29): the ring's BAV199 D23 beside D22 at CN3 and its 47K bleed R143
# beside C107, bottom side, placed by MOVES alone (probed spots)
RV3B = {'D23': (13.0, 120.75, 0, 'B'), 'R143': (34.03, 199.0, 90, 'B')}
MOVES.update(RV3B)
FIX.update({'C2': (31.745, 302.025, 0, 'F'), 'C4': (19.745, 302.525, 0, 'F')})
CS6_KEEP = [(31.0, 296.0, 34.45, 297.99, 'F'), (26.0, 297.5, 29.45, 299.49, 'F'), (30.0, 298.5, 33.45, 300.49, 'F'),
            (26.0, 300.0, 29.45, 301.99, 'F')]
# D1 leaves the OL detector zone, so the packer shifts five of its neighbours one slot along (R39 into R15's, R15 into
# R104's, ...): they go back to their v4.9 spots, in this order (pre-turn angles: R15 and R107 are in TURNS)
MOVES.update({'R39': (36.27, 101.3, 90, 'F'), 'R15': (35.995, 58.225, 90, 'F'), 'R104': (35.995, 62.225, 90, 'F'),
              'R107': (35.995, 66.225, 90, 'F'), 'R116': (35.72, 76.61, 90, 'F')})
# The upper board's op-amps where the reviewed placement had them (2026-10-26, before the EMC changes): the packer
# re-shuffles every IC after any change near the top (E1-E3 moved 163 parts and starved the HPF), so they are fixed
# and their own parts pack around them as before
FIX.update({'U1': (4.745, 63.745, 0, 'F'), 'U4': (31.245, 85.745, 0, 'F'), 'U5': (12.245, 88.245, 0, 'F'),
            'U6': (28.245, 151.745, 0, 'F'), 'U7': (4.745, 153.745, 0, 'F'), 'U12': (4.745, 129.745, 0, 'F'),
            'U13': (32.745, 129.745, 0, 'F'), 'U14': (4.745, 176.745, 0, 'F'), 'U15': (25.245, 108.745, 0, 'F'),
            'U16': (20.745, 56.745, 90, 'F')})
# M3 standoff holes (11.5 mm), unplated so audio ground never meets the chassis
HOLES = [(XC, 65.5), (XC, 154), (XC, 221), (5, 330), (5, 425), (34, 425)]   # 65.5: clear of the turned GAIN and HF pots

# ---------------------------------------------------------------- zones: (x0, y0, x1, y1), refs, side
# Bottom side: radial electrolytics (too tall for the 11.5 mm panel gap), VCA socket. Placed first.
ZONES = [
 ('jack-board link (bottom)', (12, 120, 37, 142), ['CN3'], 'B'),    # across the strip, LO-MID row to LF row
 # E4 (docs/studies/emc_placement_study.md): the reservoirs under the supply filters, beside the header's power pins (30-34)
 # E3 (docs/studies/emc_placement_study.md): the soft-mute JFETs under U3B's + input, sources at U3's ground (Self, "offness")
 ('soft mute under U3B (bottom)', (1, 226, 37, 256), ['Q2', 'Q1', 'R17', 'R16', 'R42', 'C28'], 'B'),
 ('rail reservoir caps (bottom)', (1, 285, 30, 345), ['C1', 'C3', 'C5', 'C6'], 'B'),
 ('gain-out coupling (bottom)',  (1, 44, 37, 120), ['C38', 'C91'], 'B'),   # to y 120 since C94 / C95 (v4.4)
 ('insert / EQ coupling (bottom)', (1, 75, 37, 160), ['C51', 'C10', 'C11'], 'B'),
 ('post / pan / direct-out coupling (bottom)', (1, 160, 37, 300), ['C15', 'C16', 'C17', 'C52'], 'B'),
 ('VCA module socket (bottom)', (1, 380, 37, 444), ['J3', 'J4'], 'B'),
 # 2.2 uF MKS2 film is 13 mm tall (WIMA, 63 V): more than the 11.5 mm under the panel
 ('LF film cap (bottom)', (1, 82, 37, 175), ['C49'], 'B'),
 ('fader film coupler (bottom)', (1, 330, 37, 444), ['C13'], 'B'),
 ('PFL send DC block, film (bottom; K1)', (1, 260, 37, 340), ['C96'], 'B'),
 # Top side. E4: the 10R supply filters first, beside the header's power pins, so unfiltered bus power runs a few mm
 # (the E4 supply-filter cluster, R1-R4 with C2 / C4, is placed by CS6 below: MOVES and FIX)
 # Top side, roughly in signal order
 # stability caps right after their op-amp's decouplers: the placer gives list order the closest spots
 # input followers (docs/studies/ground_study.md G3) at the top beside SW15: placed first, the receiver and the KHN keep their spots
 # E2 (docs/studies/emc_placement_study.md): the followers' 220R / 100p on the bottom under U16's + pins. U16 itself stays by SW15:
 # no spot 8 mm from D2's leads is free without moving the input section (pot and key pins fill the area)
 ('input followers', (1, 44, 37, 62), ['U16', 'C92', 'C93', 'R112', 'R113', 'R114'], 'F'),
 ('input followers RF / stability RC, under U16 (bottom)', (8, 52, 30, 76), ['R110', 'R111', 'C94', 'C95'], 'B'),
 ('input receiver + gain', (1, 45, 37, 100), ['U1', 'C20', 'C21', 'C7', 'C78', 'R6', 'R7', 'R8', 'R9', 'R10',
                                              'R45', 'R46', 'C37', 'R47'], 'F'),
 ('OL detector', (1, 45, 37, 100), ['U4', 'C26', 'R39', 'C12', 'R14', 'R40', 'R41', 'R15', 'R115', 'C97', 'R116'], 'F'),
 ('HPF', (1, 44, 37, 135), ['U5', 'C29', 'C30', 'C85', 'C86', 'R100', 'R101', 'R102', 'R103',
                             'U15', 'C89', 'C90', 'C87', 'C88', 'R104', 'R105', 'R106', 'R107', 'R108', 'R109'], 'F'),
 ('EQ', (1, 82, 37, 200), ['U6', 'C31', 'C32', 'C69', 'C70', 'C71', 'C72', 'U7', 'C33', 'C34', 'C73', 'C48',
                           'R50', 'R51', 'C41', 'C42', 'R52', 'C43', 'R53', 'R54', 'R55', 'R58', 'R59',
                           'R62', 'R63', 'R64', 'C50', 'R65', 'R66', 'R67', 'R68', 'R69'], 'F'),
 ('EQ mid tuning (KHN)', (1, 82, 37, 215), ['U12', 'C63', 'C64', 'C74', 'C75', 'C44', 'R56',
                                          'U13', 'C65', 'C66', 'C76', 'C77', 'C45', 'R57',
                                          'U14', 'C67', 'C68', 'C46', 'R60', 'C47', 'R61',
                                          'R81', 'R82', 'R83', 'R84', 'R85', 'R86', 'R87', 'R88', 'R89',
                                          'R90', 'R91', 'R92', 'R93', 'R94', 'R95', 'R96', 'R97', 'R98'], 'F'),
 ('insert + position jumpers', (1, 120, 37, 200), ['R11', 'R12', 'R99', 'C84', 'R13', 'JP5', 'JP6', 'JP7'], 'F'),
 # MET1 (docs/reviews/feature_gaps.md): the signal detector and the LED's switches carry only DC and the op-amp-driven PRESRC, so they
 # sit in the free column left of the fader (the signal path's area is full); R118 at U17, so the long run is low-Z
 ('signal detector + LED switches (MET1)', (1, 300, 10, 440), ['U17', 'C98', 'R118', 'D11', 'R119', 'R120', 'R121', 'C99',
                                                            'R122'], 'F'),
 # E1 (docs/studies/emc_placement_study.md): the LED switches beside D2 on the bottom, so the switched anode lines are a few mm long;
 # the base resistors stay at their comparators (R116 at U4, R122 at U17), so the long control lines are fed through 47K
 ('MET1 LED switches, beside D2 (bottom)', (30, 44, 37.5, 76), ['Q3', 'R117', 'Q4', 'R123', 'R124', 'Q5', 'R125'], 'B'),
 ('aux / PRE jumpers / direct out', (1, 150, 37, 270), ['JP2', 'JP3', 'JP4', 'U8', 'C35', 'C36', 'C83', 'R70', 'R71',
                                                        'R72', 'R73'], 'F'),
 ('pan buffers + mute', (1, 236, 37, 306), ['U3', 'C24', 'C25', 'C80', 'C81', 'C79', 'R35', 'R36', 'R37', 'R43'], 'F'),
 ('PFL', (1, 280, 37, 330), ['R32', 'R33', 'R34'], 'F'),
 ('routing logic + LEDs', (1, 262, 37, 310), ['R74', 'R75', 'R76', 'R77', 'R78', 'R79', 'R80', 'D9', 'D10', 'C62'], 'F'),
 ('routing switches (DG413, at the header)', (16, 280, 37, 444), ['U9', 'C53', 'C54', 'C55', 'U10', 'C56', 'C57',
                                                                  'C58', 'U11', 'C59', 'C60', 'C61'], 'F'),
 ('bus resistors (at the header)', (22, 296, 37, 362), ['R20', 'R21', 'R22', 'R23', 'R24', 'R25', 'R26', 'R27',
                                                        'R28', 'R29', 'R30', 'R31'], 'F'),
 ('power entry', (1, 340, 37, 380), ['R5'], 'F'),
 ('fader post-amp', (27, 340, 37, 444), ['U2', 'C22', 'C23', 'C82', 'R19', 'C14', 'R38', 'JP1', 'R18',
                                         'R44'], 'F'),
]
NOTES = ((50, 'GAIN | PHASE, OL'), (76, 'HF | HPF'), (98, 'HI-MID gain | freq'), (120, 'LO-MID gain | freq'),
         (142, 'LF | EQ'), (166, 'AUX 1 | 2'), (188, 'AUX 3 | 4'), (210, 'AUX 5 | 6'), (230, 'PRE 1-2  3-4  5-6'),
         (252, 'PAN | PAN, DIR'), (274, 'L-R  1-2  3-4 (LEDs y 283)'), (292, 'PFL | ON'), (305, 'BUS HEADER (bottom, right)'),
         (372, 'FADER 100 mm'), (91, 'LINK CN3 (bottom, across) to the jack board'))

NEAR = {'C20': 'U1', 'C21': 'U1', 'C22': 'U2', 'C23': 'U2', 'C24': 'U3', 'C25': 'U3', 'C26': 'U4', 'C98': 'U17',
        'C29': 'U5', 'C30': 'U5', 'C31': 'U6', 'C32': 'U6', 'C33': 'U7', 'C34': 'U7', 'C35': 'U8', 'C36': 'U8',
        'C53': 'U9', 'C54': 'U9', 'C55': 'U9', 'C56': 'U10', 'C57': 'U10', 'C58': 'U10',
        'C59': 'U11', 'C60': 'U11', 'C61': 'U11',
        'C63': 'U12', 'C64': 'U12', 'C92': 'U16', 'C93': 'U16', 'C65': 'U13', 'C66': 'U13', 'C67': 'U14', 'C68': 'U14',
        'C44': 'U12', 'R56': 'U12', 'C45': 'U13', 'R57': 'U13', 'C46': 'U14', 'R60': 'U14', 'C47': 'U14', 'R61': 'U14',
        # stability caps at their op-amp's pins (docs/reviews/strip_parts_review.md T1-T4), RET's series 1K at U7, the BAT54W at +5VL
        'C78': 'U1', 'C69': 'U6', 'C70': 'U6', 'C71': 'U6', 'C72': 'U6', 'C73': 'U7', 'C74': 'U12', 'C75': 'U12',
        'C76': 'U13', 'C77': 'U13', 'C79': 'U8', 'C82': 'U2', 'C80': 'U3', 'C81': 'U3', 'C83': 'U8', 'R99': 'U7', 'C84': 'U7',
        'D10': 'D9',
        # E2 (docs/studies/emc_placement_study.md): the followers' 220R / 100p at U16's + pins (RF filter and G3 stability cap)
        'C94': 'U16', 'C95': 'U16', 'R110': 'U16', 'R111': 'U16',
        # E1: base resistors at their comparators
        'R116': 'U4', 'R122': 'U17',
        # soft mute as one cluster at U3B's + input: Q2 drives M2, Q1 and the gate RC (high-Z MGATE) beside it
        'Q2': 'U3', 'Q1': 'Q2', 'C28': 'Q2', 'R42': 'Q2', 'R17': 'Q2', 'R16': 'Q1'}

NET, OUT = sys.argv[1], sys.argv[2]
if '(ref "CN5")' in open(NET).read():                           # jack board netlist
    layout = dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=JACK_ZONES, notes=JACK_NOTES,
                  hole_value='M3 standoff = jack body height (~24 mm)')
else:
    layout = dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, holes=HOLES, zones=ZONES, notes=NOTES, near=NEAR,
                  hole_value='M3 standoff 11.5 mm', attach=True, silk_text_off=('K',), moves=MOVES, moves_only=tuple(NEW49) + tuple(CS1) + tuple(CS10) + tuple(CS4) + tuple(CS6) + tuple(CS2) + tuple(CLICKS) + tuple(RV3B), keepout=CS6_KEEP, turns=TURNS, layers=4, rails=(0.5, 5.5))  # docs/studies/layer_study.md: 4 layers for the main board
place(NET, OUT, layout)
