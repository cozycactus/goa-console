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
JACK_HOLES = [(23, 27), (23, 37)]
JACK_ZONES = [
 ('input RF caps (bottom, at J1)', (1, 1, 19, 22), ['C8', 'C9'], 'B'),
]
JACK_NOTES = ((12, 'LINE IN | INSERT'), (32, 'DIRECT OUT | link CN5 (bottom)'))

# ================================================================ main board
FIX = {
 'SW15': sw(XR, 50), 'RV9': pot(XL, 54), 'D2': led(XR, 61),                               # Ø, gain, OL
 'RV10': pot(XL, 76), 'SW11': sw(XR, 76),                                                 # HF, HPF
 'RV11': pot(XL, 98), 'RV12': pot(XR, 98, dual=True, right=True),                         # HI-MID gain, freq
 'RV13': pot(XL, 120), 'RV14': pot(XR, 120, dual=True, right=True),                       # LO-MID gain, freq
 'RV15': pot(XL, 142), 'SW12': sw(26, 142), 'D5': led(34.5, 142),                         # LF, EQ + LED
 'RV2': pot(XL, 166), 'RV3': pot(XR, 166, right=True),                                    # aux 1, 2
 'RV4': pot(XL, 188), 'RV5': pot(XR, 188, right=True),                                    # aux 3, 4
 'RV6': pot(XL, 210), 'RV7': pot(XR, 210, right=True),                                    # aux 5, 6
 'SW8': sw(6, 230), 'SW9': sw(17, 230), 'SW10': sw(28, 230),                              # PRE 1-2, 3-4, 5-6
 'RV8': pot(XL, 252, dual=True), 'SW14': sw(XR, 246), 'SW13': sw(XR, 258),                # pan, PAN, DIR
 'SW5': sw(6, 274), 'SW6': sw(17, 274), 'SW7': sw(28, 274),                               # L-R, 1-2, 3-4
 'D6': led(6, 283), 'D7': led(17, 283), 'D8': led(28, 283),                               # routing LEDs
 'SW3': sw(6, 292), 'D3': led(14.2, 292), 'SW4': sw(24, 292), 'D4': led(32.2, 292),       # PFL, ON
 'RV1': FADER,                           # fader, slot centre y = 372
 'CN1': BUS,                             # bus header, bottom side, pins at x = 31.46 / 34, y = 305..346; pin 1 at the
                                         # bottom end so its silk arrow points inboard, not off the edge
 'CN4': SPADE,                           # ground spade, bottom side, left of the fader body
 'NT1': NETTIE,                          # AGND-LGND net tie beside the spade (no courtyard: keep it clear by hand)
}
# M3 standoff holes (11.5 mm), unplated so audio ground never meets the chassis
HOLES = [(XC, 67), (XC, 154), (XC, 221), (5, 330), (5, 425), (34, 425)]

# ---------------------------------------------------------------- zones: (x0, y0, x1, y1), refs, side
# Bottom side: radial electrolytics (too tall for the 11.5 mm panel gap), VCA socket. Placed first.
ZONES = [
 ('jack-board link (bottom)', (12, 44, 37, 120), ['CN3'], 'B'),     # pins between the columns
 ('rail reservoir caps (bottom)', (1, 360, 37, 444), ['C1', 'C3', 'C5', 'C6'], 'B'),
 ('gain-out coupling (bottom)',  (1, 45, 37, 80), ['C38'], 'B'),
 ('insert / EQ coupling (bottom)', (1, 75, 37, 160), ['C51', 'C10', 'C11'], 'B'),
 ('post / pan / direct-out coupling (bottom)', (1, 160, 37, 300), ['C15', 'C16', 'C17', 'C52'], 'B'),
 ('VCA module socket (bottom)', (1, 380, 37, 444), ['J3', 'J4'], 'B'),
 # Top side, roughly in signal order
 ('input receiver + gain', (1, 45, 37, 100), ['U1', 'C20', 'C21', 'R6', 'R7', 'C7', 'R8', 'R9', 'R10',
                                              'R45', 'R46', 'C37', 'R47'], 'F'),
 ('OL detector', (1, 45, 37, 100), ['U4', 'C26', 'R39', 'D1', 'C12', 'R14', 'R40', 'R41', 'R15'], 'F'),
 ('HPF', (1, 60, 37, 100), ['U5', 'C29', 'C30', 'C39', 'C40', 'R48', 'R49'], 'F'),
 ('EQ', (1, 82, 37, 162), ['U6', 'C31', 'C32', 'U7', 'C33', 'C34', 'C48', 'C49', 'R50', 'R51', 'C41', 'C42', 'R52',
                           'C43', 'R53', 'R54', 'R55', 'R58', 'R59',
                           'R62', 'R63', 'R64', 'C50', 'R65', 'R66', 'R67', 'R68', 'R69'], 'F'),
 ('EQ mid tuning (KHN)', (1, 82, 37, 200), ['U12', 'C63', 'C64', 'C44', 'R56', 'U13', 'C65', 'C66', 'C45', 'R57',
                                          'U14', 'C67', 'C68', 'C46', 'R60', 'C47', 'R61',
                                          'R81', 'R82', 'R83', 'R84', 'R85', 'R86', 'R87', 'R88', 'R89',
                                          'R90', 'R91', 'R92', 'R93', 'R94', 'R95', 'R96', 'R97', 'R98'], 'F'),
 ('insert + position jumpers', (1, 120, 37, 175), ['R11', 'R12', 'R13', 'JP5', 'JP6', 'JP7'], 'F'),
 ('aux / PRE jumpers / direct out', (1, 150, 37, 270), ['JP2', 'JP3', 'JP4', 'U8', 'C35', 'C36', 'R70', 'R71',
                                                        'R72', 'R73'], 'F'),
 ('pan buffers + mute', (1, 236, 37, 306), ['U3', 'C24', 'C25', 'R35', 'R36', 'R37', 'R16', 'R17', 'Q1', 'Q2',
                                            'R42', 'C28', 'R43'], 'F'),
 ('PFL', (1, 280, 37, 330), ['R32', 'R33', 'R34'], 'F'),
 ('routing logic + LEDs', (1, 262, 37, 310), ['R74', 'R75', 'R76', 'R77', 'R78', 'R79', 'R80', 'D9', 'C62'], 'F'),
 ('routing switches (DG413, at the header)', (16, 280, 37, 444), ['U9', 'C53', 'C54', 'C55', 'U10', 'C56', 'C57',
                                                                  'C58', 'U11', 'C59', 'C60', 'C61'], 'F'),
 ('bus resistors (at the header)', (22, 296, 37, 362), ['R20', 'R21', 'R22', 'R23', 'R24', 'R25', 'R26', 'R27',
                                                        'R28', 'R29', 'R30', 'R31'], 'F'),
 ('power entry', (1, 340, 37, 380), ['R1', 'R2', 'R3', 'R4', 'R5', 'C2', 'C4'], 'F'),
 ('fader post-amp', (27, 340, 37, 444), ['U2', 'C22', 'C23', 'R19', 'C14', 'R38', 'C13', 'JP1', 'R18', 'R44'], 'F'),
]
NOTES = ((50, 'GAIN | PHASE, OL'), (76, 'HF | HPF'), (98, 'HI-MID gain | freq'), (120, 'LO-MID gain | freq'),
         (142, 'LF | EQ'), (166, 'AUX 1 | 2'), (188, 'AUX 3 | 4'), (210, 'AUX 5 | 6'), (230, 'PRE 1-2  3-4  5-6'),
         (252, 'PAN | PAN, DIR'), (274, 'L-R  1-2  3-4 (LEDs y 283)'), (292, 'PFL | ON'), (305, 'BUS HEADER (bottom, right)'),
         (372, 'FADER 100 mm'), (55, 'LINK CN3 (bottom) to the jack board'))

NEAR = {'C20': 'U1', 'C21': 'U1', 'C22': 'U2', 'C23': 'U2', 'C24': 'U3', 'C25': 'U3', 'C26': 'U4',
        'C29': 'U5', 'C30': 'U5', 'C31': 'U6', 'C32': 'U6', 'C33': 'U7', 'C34': 'U7', 'C35': 'U8', 'C36': 'U8',
        'C53': 'U9', 'C54': 'U9', 'C55': 'U9', 'C56': 'U10', 'C57': 'U10', 'C58': 'U10',
        'C59': 'U11', 'C60': 'U11', 'C61': 'U11',
        'C63': 'U12', 'C64': 'U12', 'C65': 'U13', 'C66': 'U13', 'C67': 'U14', 'C68': 'U14',
        'C44': 'U12', 'R56': 'U12', 'C45': 'U13', 'R57': 'U13', 'C46': 'U14', 'R60': 'U14', 'C47': 'U14', 'R61': 'U14'}

NET, OUT = sys.argv[1], sys.argv[2]
if '(ref "CN5")' in open(NET).read():                           # jack board netlist
    layout = dict(board=(0, 0, W, JACK_Y1), fix=JACK_FIX, holes=JACK_HOLES, zones=JACK_ZONES, notes=JACK_NOTES,
                  hole_value='M3 standoff = jack body height (~24 mm)')
else:
    layout = dict(board=(0, MAIN_Y0, W, MAIN_Y1), fix=FIX, holes=HOLES, zones=ZONES, notes=NOTES, near=NEAR,
                  hole_value='M3 standoff 11.5 mm')
place(NET, OUT, layout)
