"""Component placement for the channel-strip PCBs, v4.0 (KiCad 10 pcbnew API). Placement only: no copper.
Two boards, each from its own netlist; the layout is picked from the parts (CN5 = jack board):
  KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
  $KPY tools/place_strip.py channel_strip.net channel_strip_v4.kicad_pcb     # main board, 38 x 400 mm
  $KPY tools/place_strip.py jack_board.net jack_board.kicad_pcb              # jack board, 38 x 43 mm
Panel: 8 HP x 12U Eurorack-style (40.3 x 514 mm), two pot columns, jacks on the panel (study:
strip_panel_study.md). y = 0 is 11 mm below the panel's top edge (end rail) and grows towards the fader;
both boards use these coordinates, so the two files overlay on the panel. The jack board (y 0-43) sits
~24 mm under the panel (a 1/4" plug goes ~30 mm deep); the main board (y 44-444) at 11.5 mm. A 10-way
IDC ribbon joins CN5 (jack board, bottom) to CN3 (main board, bottom).
Panel parts sit at fixed coordinates; the rest is packed by zone (engine: placer.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from placer import place, W8 as W, XL, XR, XC, pot, sw, led, jack, FADER, BUS, SPADE, NETTIE

JACK_Y1, MAIN_Y0, MAIN_Y1 = 43.0, 44.0, 444.0   # jack board y 0-43, main board y 44-444 (514 mm 12U panel)

# ================================================================ jack board
JACK_FIX = {'J1': jack(XL, 12), 'J2': jack(XR, 12), 'J5': jack(XL, 32),              # line in, insert / direct out
            # link header, bottom side, pins x 31 / 33.54, y 26.6-36.8 (pin 1 low, so its silk arrow points inboard)
            'CN5': (31.0, 36.8, 180, 'B')}
# M3 standoffs to the panel, length = jack body height (~24 mm); the jack caps hold the board too
# plated, on CHASSIS (H1 / H2 in the jack board schematic, ground_study.md G2): they bond the sleeves to the panel
JACK_HOLES = []
JACK_FIX.update({'H1': (23, 27, 0, 'F'), 'H2': (23, 37, 0, 'F')})
JACK_ZONES = [
 ('input RF caps (bottom, at J1)', (1, 1, 19, 22), ['C8', 'C9'], 'B'),
]
JACK_NOTES = ((12, 'LINE IN | INSERT'), (32, 'DIRECT OUT | link CN5 (bottom)'))

# ================================================================ main board
FIX = {
 'SW15': sw(XR, 50), 'RV9': pot(XL, 54), 'SW11': sw(XR, 61), 'D2': led(20.6, 50),           # Ø, gain, HPF in, OL
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
# M3 standoff holes (11.5 mm), unplated so audio ground never meets the chassis
HOLES = [(XC, 65.5), (XC, 154), (XC, 221), (5, 330), (5, 425), (34, 425)]   # 65.5: clear of the turned GAIN and HF pots

# ---------------------------------------------------------------- zones: (x0, y0, x1, y1), refs, side
# Bottom side: radial electrolytics (too tall for the 11.5 mm panel gap), VCA socket. Placed first.
ZONES = [
 ('jack-board link (bottom)', (12, 120, 37, 142), ['CN3'], 'B'),    # across the strip, LO-MID row to LF row
 ('rail reservoir caps (bottom)', (1, 360, 37, 444), ['C1', 'C3', 'C5', 'C6'], 'B'),
 ('gain-out coupling (bottom)',  (1, 44, 37, 120), ['C38', 'C91'], 'B'),   # to y 120 since C94 / C95 (v4.4)
 ('insert / EQ coupling (bottom)', (1, 75, 37, 160), ['C51', 'C10', 'C11'], 'B'),
 ('post / pan / direct-out coupling (bottom)', (1, 160, 37, 300), ['C15', 'C16', 'C17', 'C52'], 'B'),
 ('VCA module socket (bottom)', (1, 380, 37, 444), ['J3', 'J4'], 'B'),
 # 2.2 uF MKS2 film is 13 mm tall (WIMA, 63 V): more than the 11.5 mm under the panel
 ('LF film cap (bottom)', (1, 82, 37, 175), ['C49'], 'B'),
 ('fader film coupler (bottom)', (1, 330, 37, 444), ['C13'], 'B'),
 ('PFL send DC block, film (bottom; K1)', (1, 260, 37, 340), ['C96'], 'B'),
 # Top side, roughly in signal order
 # stability caps right after their op-amp's decouplers: the placer gives list order the closest spots
 # input followers (ground_study.md G3) at the top beside SW15: placed first, the receiver and the KHN keep their spots
 ('input followers', (1, 44, 37, 62), ['U16', 'C92', 'C93', 'R110', 'R111', 'R112', 'R113', 'R114', 'C94', 'C95'], 'F'),
 ('input receiver + gain', (1, 45, 37, 100), ['U1', 'C20', 'C21', 'C7', 'C78', 'R6', 'R7', 'R8', 'R9', 'R10',
                                              'R45', 'R46', 'C37', 'R47'], 'F'),
 ('OL detector', (1, 45, 37, 100), ['U4', 'C26', 'R39', 'D1', 'C12', 'R14', 'R40', 'R41', 'R15', 'R115', 'C97'], 'F'),
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
 ('aux / PRE jumpers / direct out', (1, 150, 37, 270), ['JP2', 'JP3', 'JP4', 'U8', 'C35', 'C36', 'C83', 'R70', 'R71',
                                                        'R72', 'R73'], 'F'),
 ('pan buffers + mute', (1, 236, 37, 306), ['U3', 'C24', 'C25', 'C80', 'C81', 'R35', 'R36', 'R37', 'R16', 'R17',
                                            'Q1', 'Q2', 'R42', 'C28', 'R43'], 'F'),
 ('PFL', (1, 280, 37, 330), ['R32', 'R33', 'R34'], 'F'),
 ('routing logic + LEDs', (1, 262, 37, 310), ['R74', 'R75', 'R76', 'R77', 'R78', 'R79', 'R80', 'D9', 'D10', 'C62'], 'F'),
 ('routing switches (DG413, at the header)', (16, 280, 37, 444), ['U9', 'C53', 'C54', 'C55', 'U10', 'C56', 'C57',
                                                                  'C58', 'U11', 'C59', 'C60', 'C61'], 'F'),
 ('bus resistors (at the header)', (22, 296, 37, 362), ['R20', 'R21', 'R22', 'R23', 'R24', 'R25', 'R26', 'R27',
                                                        'R28', 'R29', 'R30', 'R31'], 'F'),
 ('power entry', (1, 340, 37, 380), ['R1', 'R2', 'R3', 'R4', 'R5', 'C2', 'C4'], 'F'),
 ('fader post-amp', (27, 340, 37, 444), ['U2', 'C22', 'C23', 'C82', 'C79', 'R19', 'C14', 'R38', 'JP1', 'R18',
                                         'R44'], 'F'),
]
NOTES = ((50, 'GAIN | PHASE, OL'), (76, 'HF | HPF'), (98, 'HI-MID gain | freq'), (120, 'LO-MID gain | freq'),
         (142, 'LF | EQ'), (166, 'AUX 1 | 2'), (188, 'AUX 3 | 4'), (210, 'AUX 5 | 6'), (230, 'PRE 1-2  3-4  5-6'),
         (252, 'PAN | PAN, DIR'), (274, 'L-R  1-2  3-4 (LEDs y 283)'), (292, 'PFL | ON'), (305, 'BUS HEADER (bottom, right)'),
         (372, 'FADER 100 mm'), (91, 'LINK CN3 (bottom, across) to the jack board'))

NEAR = {'C20': 'U1', 'C21': 'U1', 'C22': 'U2', 'C23': 'U2', 'C24': 'U3', 'C25': 'U3', 'C26': 'U4',
        'C29': 'U5', 'C30': 'U5', 'C31': 'U6', 'C32': 'U6', 'C33': 'U7', 'C34': 'U7', 'C35': 'U8', 'C36': 'U8',
        'C53': 'U9', 'C54': 'U9', 'C55': 'U9', 'C56': 'U10', 'C57': 'U10', 'C58': 'U10',
        'C59': 'U11', 'C60': 'U11', 'C61': 'U11',
        'C63': 'U12', 'C64': 'U12', 'C92': 'U16', 'C93': 'U16', 'C65': 'U13', 'C66': 'U13', 'C67': 'U14', 'C68': 'U14',
        'C44': 'U12', 'R56': 'U12', 'C45': 'U13', 'R57': 'U13', 'C46': 'U14', 'R60': 'U14', 'C47': 'U14', 'R61': 'U14',
        # stability caps at their op-amp's pins (strip_parts_review.md T1-T4), RET's series 1K at U7, the BAT54W at +5VL
        'C78': 'U1', 'C69': 'U6', 'C70': 'U6', 'C71': 'U6', 'C72': 'U6', 'C73': 'U7', 'C74': 'U12', 'C75': 'U12',
        'C76': 'U13', 'C77': 'U13', 'C79': 'U2', 'C82': 'U2', 'C80': 'U3', 'C81': 'U3', 'C83': 'U8', 'R99': 'U7', 'C84': 'U7',
        'D10': 'D9',
        # soft mute as one cluster at U3B's + input: Q2 drives M2, Q1 and the gate RC (high-Z MGATE) beside it
        'Q2': 'U3', 'Q1': 'Q2', 'C28': 'Q2', 'R42': 'Q2', 'R17': 'Q2', 'R16': 'Q1'}

NET, OUT = sys.argv[1], sys.argv[2]
if '(ref "CN5")' in open(NET).read():                           # jack board netlist
    layout = dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=JACK_ZONES, notes=JACK_NOTES,
                  hole_value='M3 standoff = jack body height (~24 mm)')
else:
    layout = dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, holes=HOLES, zones=ZONES, notes=NOTES, near=NEAR,
                  hole_value='M3 standoff 11.5 mm', attach=True, silk_text_off=('K',))
place(NET, OUT, layout)
