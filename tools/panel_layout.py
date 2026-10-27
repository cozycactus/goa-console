"""Front-panel layout of each module, without Blender: plate, cut-outs, mounting screws and the Delta-style print, from
the placed boards (render/<module>.json, tools/export_3d.py). tools/console_3d.py builds the 3D panel layer from it and
tools/panel_fab.py the fabrication drawings, so the two can't drift apart.

Coordinates are board mm (x right, y down), the module's frame: main board at x 0..38.1, y 44..444; the panel spans
x X0 .. X0 + width, y Y0 .. Y1 (12U = 4 x 128.5 = 514 mm). Rules for the print: panel_print.md."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models3d import lookup
from models3d.knob import D_KNOB                # Elma Ø14.5 on every pot (knob_proposal.md KN2)

HP = 5.08
WIDTH = {'strip': 8 * HP - 0.34, 'group': 8 * HP - 0.34, 'master': 16 * HP - 0.34}   # 40.30 / 80.94 mm
X0, Y0, Y1 = -1.15, -11.0, 503.0
SCREW_D = 3.2                                  # M3 panel screws on the end rails, 3 mm from each end
CSK_HOLE, CSK_D = 3.4, 6.5                     # P4 without studs: the jack-board standoffs' M3 flat-head screws, 90 deg
LABEL = {'master': 'MASTER'}
# the console: 12 strips | groups 1-2 | master (16 HP) | groups 3-4 | 12 strips, on an 8 HP pitch
ORDER = ['S'] * 12 + ['G1', 'G2', 'M', 'G3', 'G4'] + ['S'] * 12
PITCH = 8 * HP
# frame rails (frame_proposal.md FR1, signed off 2026-10-25): 10 x 50 flat bar on edge under each panel end, centred
# on the panel screw lines, top face against the panel underside, 2 mm into each cheek (the cheeks' inner faces are
# CHEEK_GAP outside the console's 0 / width; console_3d.py)
RAIL_W, RAIL_H, CHEEK_GAP, RAIL_INTO = 10.0, 50.0, 2.0, 2.0
RAIL_LINES = (Y0 + 3.0, Y1 - 3.0)
# the back rail (the y = Y0 + 3 line, the console's high end) is the vent outlet (thermal_study.md TH1, signed off
# 2026-10-26): 30 slots 30 x 25 mm through its 10 mm thickness, centred on its neutral axis, evenly from 40 mm in
VENT_SLOTS, VENT_W, VENT_H, VENT_IN = 30, 30.0, 25.0, 40.0

# the tub (tub_proposal.md TB1-TB4, signed off 2026-10-26), module frame: x along the console, y as the boards (back
# negative), z up from the main-board top (panel underside at PANEL_Z0, top at PANEL_Z1); mm
PANEL_Z0, PANEL_Z1 = 11.5, 13.0
TILT_DEG, MOUNT_Y, MOUNT_Z = 9.0, 250.0, 165.0     # console tilt (front lower); where the module origin sits over the desk
FLOOR_TOP, FLOOR_T, DADO = -45.0, 12.0, 6.0        # 12 mm ply floor in 6 mm dados
FLOOR_Y = (-13.0, 504.0)                           # back rail's outer face .. arm-rest's inner face
INLET_ROWS, INLET_W, INLET_L, INLET_BRIDGE = (455.0, 470.0, 485.0), 10.0, 100.0, 15.0   # floor inlet slots (TB2)
ARM_Y, ARM_TOP = (504.0, 548.0), PANEL_Z1 + 6.0
# plenum: a 12 mm rear wall, a 14 mm cap strip on top of it; between the wall and the back rail a 21 mm channel whose
# whole top is the outlet (21 x 1223 mm = 0.026 m2; a cap with a cut slot would leave a 0.5 mm sliver)
PLENUM_WALL_Y, PLENUM_CAP_Y, PLENUM_CAP_Z, PLENUM_CAP_T = (-48.0, -36.0), (-48.0, -34.0), PANEL_Z1 + 10.0, 10.0
CHEEK_T, CHEEK_TOP = 20.0, (PANEL_Z1 + 24.0, PANEL_Z1 + 8.0)   # cheek top line above the panel at the back / front
NC7_X = 14 * PITCH + X0 + WIDTH['master'] / 2   # the master panel's centre (console x): the NC7MD-LX in the rear wall
CABLE_SLOT = 14                                    # back-rail vent slot the supply cable passes

def to_desk(y, z):
    """Module (y, z) -> side elevation over the desk (Y back, Z up), mm."""
    t = math.radians(TILT_DEG)
    return (y * -math.cos(t) - z * math.sin(t) + MOUNT_Y, -y * math.sin(t) + z * math.cos(t) + MOUNT_Z)

def cheek_outline():
    """The cheek's side profile over the desk [(Y, Z)]: the top line 24 / 8 above the panel, extended back to cover the
    plenum's rear wall; vertical back and front; the bottom on the desk."""
    tb, tf = to_desk(PLENUM_WALL_Y[0], CHEEK_TOP[0]), to_desk(ARM_Y[1], CHEEK_TOP[1])
    yb = to_desk(PLENUM_WALL_Y[0], FLOOR_TOP - FLOOR_T)[0]
    zb = tb[1] + (tf[1] - tb[1]) * (yb - tb[0]) / (tf[0] - tb[0])
    return [(yb, 0.0), (yb, zb), tf, (tf[0], 0.0)]

def inlet_slots():
    """Floor inlet slots [(x0, x1, y)] in console x (the floor spans the console between the cheeks)."""
    w = console_width(); x0 = -CHEEK_GAP; x1 = w + CHEEK_GAP; out = []
    n = int((x1 - x0 - INLET_BRIDGE) // (INLET_L + INLET_BRIDGE))
    start = x0 + (x1 - x0 - (n * INLET_L + (n - 1) * INLET_BRIDGE)) / 2
    for y in INLET_ROWS:
        out += [(start + k * (INLET_L + INLET_BRIDGE), start + k * (INLET_L + INLET_BRIDGE) + INLET_L, y) for k in range(n)]
    return out

def vent_slots():
    """Centres of the back rail's vent slots, x from the rail's left end."""
    r0, r1 = rail_span(); ln = r1 - r0
    return [VENT_IN + k * (ln - 2 * VENT_IN) / (VENT_SLOTS - 1) for k in range(VENT_SLOTS)]

def modules():
    """[(item, key, x)] along the console: item from ORDER, key 'strip' / 'group' / 'master', x of the module's frame."""
    out, x = [], 0.0
    for item in ORDER:
        key = {'S': 'strip', 'M': 'master'}.get(item, 'group')
        out.append((item, key, x)); x += 2 * PITCH if item == 'M' else PITCH
    return out

def console_width():
    return sum(2 * PITCH if item == 'M' else PITCH for item in ORDER)

def rail_holes():
    """x of every panel screw along a rail (console frame); the same on both rails."""
    return [x + sx for item, key, x in modules() for sx in sorted({sx for sx, sy in Panel(key, WIDTH[key]).screws})]

def rail_span():
    """(x0, x1) of a rail in the console frame."""
    return -CHEEK_GAP - RAIL_INTO, console_width() + CHEEK_GAP + RAIL_INTO

# ---------------------------------------------------------------- legends and colours per module
# Switch caps C&K PV: red, grey, black, white only (knob_proposal.md KC1: ON black, DIR grey); knob caps Elma 040-30x5
# (red, grey, blue, yellow, green, black; KN3); fader caps Sifam LK111 01, black with a white line (KC2; white / red /
# yellow only if the coloured-cap trial passes). The group's AUX cap is yellow on groups 1-2 and green on 3-4 (the model shows one group design: yellow).
STRIP = {'RV9': ('GAIN', 'red'), 'RV10': ('HF', 'grey'), 'RV11': ('HI-MID', 'grey'), 'RV12': ('FREQ', 'blue'),
         'RV13': ('LO-MID', 'grey'), 'RV14': ('FREQ', 'blue'), 'RV15': ('LF', 'grey'), 'RV2': ('AUX 1', 'yellow'),
         'RV3': ('AUX 2', 'yellow'), 'RV4': ('AUX 3', 'green'), 'RV5': ('AUX 4', 'green'), 'RV6': ('AUX 5', 'black'),
         'RV7': ('AUX 6', 'black'), 'RV8': ('PAN', 'black'), 'RV16': ('', 'blue'),     # HPF FREQ: the key above names it
         'SW15': ('Ø', 'grey'), 'SW11': ('HPF', 'grey'), 'SW12': ('EQ', 'grey'), 'SW8': ('PRE 1-2', 'grey'),
         'SW9': ('PRE 3-4', 'grey'), 'SW10': ('PRE 5-6', 'grey'), 'SW14': ('PAN', 'grey'), 'SW13': ('DIR', 'grey'),
         'SW5': ('L-R', 'white'), 'SW6': ('1-2', 'white'), 'SW7': ('3-4', 'white'), 'SW3': ('PFL', 'red'), 'SW4': ('ON', 'black'),
         'D2': ('OL', 'red'), 'D3': (None, 'off'), 'D4': (None, 'green'), 'D5': (None, 'green'), 'D6': (None, 'yellow'),
         'D7': (None, 'off'), 'D8': (None, 'off'),
         'J1': ('LINE IN', None), 'J2': ('INSERT', None), 'J5': ('DIRECT', None), 'RV1': ('', 'black')}
GROUP = {'RV4': ('RET 1', 'blue'), 'RV5': ('RET 2', 'blue'), 'RV3': ('AUX', 'yellow'), 'RV2': ('SUB PAN', 'black'),
         'SW7': ('PFL', 'red'), 'SW11': ('PFL', 'red'), 'SW3': ('AFL', 'red'), 'SW1': ('MIX', 'white'), 'SW4': ('R1 MIX', 'white'),
         'SW5': ('R1 1-2', 'white'), 'SW6': ('R1 3-4', 'white'), 'SW8': ('R2 MIX', 'white'), 'SW9': ('R2 1-2', 'white'),
         'SW10': ('R2 3-4', 'white'), 'SW2': ('AFL', 'red'),
         'D1': (None, 'off'), 'D2': (None, 'off'), 'D3': (None, 'off'), 'D4': (None, 'off'),
         'J2': ('SUB OUT', None), 'J1': ('INSERT', None), 'J3': ('AUX OUT', None), 'J4': ('RET 1 L', None),
         'J5': ('RET 1 R', None), 'J6': ('RET 2 L', None), 'J7': ('RET 2 R', None), 'RV1': ('SUB', 'black')}
MASTER = {'RV2': ('AUX 5', 'black'), 'RV3': ('AUX 6', 'black'), 'RV5': ('C/ROOM', 'grey'), 'RV6': ('PHONES', 'grey'),
          'RV4': ('SOLO', 'red'), 'SW1': ('AFL', 'red'), 'SW2': ('AFL', 'red'), 'SW3': ('EXT', 'grey'),
          'D12': (None, 'off'), 'D13': (None, 'off'), 'D3': ('POWER', 'green'), 'D15': ('PFL', 'off'),
          'J1': ('INS L', None), 'J2': ('INS R', None), 'J10': ('C/R L', None), 'J11': ('C/R R', None),
          'J8': ('EXT L', None), 'J9': ('EXT R', None), 'J6': ('AUX 5', None), 'J7': ('AUX 6', None),
          'J12': ('PHONES', None), 'J3': ('MAIN L', None), 'J4': ('MAIN R', None), 'J5': ('MONO', None), 'RV1': ('MIX', 'black')}
NAMES = {'strip': STRIP, 'group': GROUP, 'master': MASTER}
KNOB_ANGLE = {'AUX': -50.0, 'RETURN': 40.0, 'RET': 40.0, 'C/ROOM': 30.0, 'PHONES': 20.0}

def led_state(p, names):
    if p['ref'] in names: return names[p['ref']]
    v = p['value'].split()
    if len(v) == 3 and v[2] == 'dB': return None, (v[0] if int(v[1]) <= 4 else 'off')   # meters: lit up to +4 dB
    return None, 'off'

# ---------------------------------------------------------------- cut-outs
HOLE = {'alpha_pot': 7.2, 'alps_rk09l': 9.5, 'ck_pva2': 8.0, 'neutrik_nj6fd_v': 12.0}      # panel holes, spec 16.1 / 16.2
POTS = ('alpha_pot', 'alps_rk09l')                 # knob-and-legend parts (the pan pot RV8 is the ALPS)
FADER_SLOT = (110.0, 2.4, 60.0)               # PTB: 100 travel + 8.0 blade (BP lever), 1.3 blade; M3 fixings at +-60
XLR_CUT = (22.2, [(-9.9, -9.9), (9.9, 9.9)])  # NC3MAV (A series, rear mount): >= 22 hole, 2 x 3.2 (footprint frame)
LED_HOLE = (3.2, 5.2)                          # 3 mm / 5 mm LED
FIX_D = 3.2                                    # M3 fixing holes (fader, XLR)
LEGEND = {'alpha_pot': (-9.8, 2.0), 'alps_rk09l': (-9.8, 2.0), 'ck_pva2': (-5.8, 1.7), 'neutrik_nj6fd_v': (-10.2, 1.8), 'neutrik_nc3mav': (-16.2, 1.8)}

# ---------------------------------------------------------------- panel print in the Delta's style (ref/delta200_panels)
# Each pot: name above, a ring of 11 dots over the 300-degree rotation and numbers at chosen positions; numbers that
# would hit a neighbouring knob, switch, LED, jack or label are left out (two pot columns 20.32 mm apart, rows 22 mm).
EVEN11 = [k / 10 for k in range(11)]
def gain_theta(db):
    """Strip gain stage (spec 4): G = (2K2 + 10K t) / (2K2 + 10K (1 - t)), symmetric in dB about the detent."""
    r = 10 ** (db / 20); return min(1.0, max(0.0, (12.2 * r - 2.2) / (10 * (1 + r))))
def both(*pairs):
    """Labels in priority order: each (theta, text) and its mirror (1 - theta, text)."""
    return [q for t, a in pairs for q in ((t, a), (1 - t, a))][:None]
KHN = {'RV12': [(0.0, '0.7'), (1.0, '10KHz'), (0.5, '2.2'), (0.25, '1.6'), (0.75, '4.8')],   # sim/mid_tuning.py 10e3:
       'RV14': [(0.0, '0.15'), (1.0, '2.3KHz'), (0.5, '0.48'), (0.25, '0.34'), (0.75, '1.0')],  # KHN f0 at theta 0..1
       'RV16': [(0.0, '20'), (1.0, '400Hz'), (0.5, '85'), (0.2, '50'), (0.7, '170')]}   # HPF -3 dB, khn_hpf.py law
SCALES = {   # (dots, labels in priority order, unit at 6 o'clock); as the real Delta panels (ref/delta200_panels, photos)
    'gain': ([k / 20 for k in range(21)], [(gain_theta(d), f'{d:+d}' if d else '0') for d in (-15, 15, 0, -10, 10, -5, 5)], 'dB'),
    'eq': (EVEN11, both((0.0, '15'), (0.2, '9')) + [(0.5, '-0+')] + both((0.1, '12'), (0.3, '6'), (0.4, '3')), 'dB'),
    'level': (EVEN11, [(0.0, '0'), (1.0, '10'), (0.5, '5'), (0.2, '2'), (0.8, '8'), (0.1, '1'), (0.9, '9'),
                       (0.3, '3'), (0.7, '7'), (0.4, '4'), (0.6, '6')], None),
    'pan': (EVEN11, [(0.0, 'L5'), (1.0, '5R'), (0.5, '0')] + both((0.2, '3'), (0.1, '4'), (0.3, '2'), (0.4, '1')), None),
}
PAIRS = {'strip': {'RV12': ('RV11', 'HI MID'), 'RV14': ('RV13', 'LO MID')}}   # frequency knob: (its gain knob, band)
RULES = {'strip': [152.2, 221.2, 236.6, 264.6], 'group': [156.2, 207.0, 264.6], 'master': [112.0, 196.0]}
METERS = {'master': [(18.0, 327.0, 422.0), (60.6, 327.0, 422.0)]}   # LED columns: outline as the Delta's meter block
def scale_of(ref, name):
    if ref in KHN: return (EVEN11, KHN[ref], None)
    n = name.split()[0] if name else ''
    return SCALES['gain' if n == 'GAIN' else 'eq' if n in ('HF', 'HI-MID', 'LO-MID', 'LF') else
                  'pan' if 'PAN' in name else 'level']

def fader_theta(db, post=1 + 4.7 / 2.2):
    """Fader position (0 = bottom) for db at the post-amp output: A taper as two slopes, 15 % at mid-travel (the law
    sim/mid_tuning.py uses for the Alpha pots; the fader's own curve is still to be measured), then +9.9 dB."""
    a = 10 ** (db / 20) / post
    return 0.0 if a <= 0 else min(1.0, a / 0.3 if a <= 0.15 else 0.5 + (a - 0.15) / 1.7)
FADER_MARKS = [(10, '10'), (5, '5'), (0, '0'), (-5, '5'), (-10, '10'), (-15, '15'), (-20, '20'), (-25, '25'),
               (-30, '30'), (-40, '40'), (-50, '50'), (-60, '60'), (None, '∞')]       # the Delta input's scale

class Panel:
    """One module's panel. holes: [(kind, x, y, size or rotation)] with kind 'round' (diameter), 'slot' (fader slot and
    its two M3 holes, rotation) or 'xlr' (NC3MAV hole and its two M3 holes, rotation); screws: [(x, y)] M3 panel
    screws; texts: [(s, x, y, size, bold)] centred on (x, y), size = em in mm; rects: [(x0, y0, x1, y1)] filled ink
    (dots, ticks, rules, brackets, meter outlines). parts: per panel part (ref, kind, x, y, rot, name, colour, big),
    for the 3D layer. studs: [(x, y, ref, board)] the boards' standoffs, where blind M3 studs go into the panel's back
    (met1_ret1_review.md P4: if the maker offers them); board 'main' or 'jack' (the jack boards' bond CHASSIS)."""
    def __init__(self, key, width):
        self.key, self.width = key, width
        self.x0, self.x1, self.y0, self.y1 = X0, X0 + width, Y0, Y1
        self.holes, self.texts, self.rects, self.parts, self.studs = [], [], [], [], []
        self.screws = [(xx, yy) for yy in (Y0 + 3.0, Y1 - 3.0) for xx in ((X0 + 7.5,) if width < 50 else (X0 + 7.5, X0 + width - 7.5))]

    def line(self, x0, y0, x1, y1, w=0.28):
        self.rects.append((min(x0, x1) - w / 2, min(y0, y1) - w / 2, max(x0, x1) + w / 2, max(y0, y1) + w / 2))

    def cut(self):
        """Every cut-out as circles [(x, y, d)] and slots [(x, y, length, width, rotation)]."""
        circles, slots = [], []
        for kind, x, y, a in self.holes:
            if kind == 'round': circles.append((x, y, a)); continue
            ca, sa = math.cos(math.radians(a)), -math.sin(math.radians(a))      # footprint x axis on the board
            rot = lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)
            if kind == 'slot':
                slots.append((x, y, FADER_SLOT[0], FADER_SLOT[1], a))
                circles += [(*rot(u, 0.0), FIX_D) for u in (-FADER_SLOT[2], FADER_SLOT[2])]
            else:
                circles.append((x, y, XLR_CUT[0]))
                circles += [(*rot(u, v), FIX_D) for u, v in XLR_CUT[1]]
        circles += [(x, y, SCREW_D) for x, y in self.screws]
        return circles, slots

EDGE = 0.5                                     # print (estimated text box) to the plate edge, for the optional numerals

def text_box(s, size):
    """The print's text size estimate (Arial Narrow): width, height in mm."""
    return 0.47 * size * len(s.replace('.', '')) + 0.15 * s.count('.'), 0.75 * size

def panel_print(P, pots, faders, obst):
    """The Delta's panel print, one cream ink: pot names (bold) above the knobs, a frequency/gain pair joined by a
    bracket carrying the band name, 11-dot rings (dense for GAIN) with numerals outside the dots and 'dB' between the
    end numerals, fader ticks both sides with numerals on the right (heavier 0 / top / bottom bars), full-width section
    rules and meter outlines. pots: [(ref, name, x, y, big)], faders: [(name, x, y, dual)], obst: [(x, y, r for the
    print, owner, r of the part itself)]."""
    key, width, placed = P.key, P.width, []
    def free(x, y, w, h, own):
        if x - w / 2 < P.x0 + EDGE or x + w / 2 > P.x1 - EDGE: return False     # a numeral off the plate edge drops
        if any(math.hypot(max(abs(x - ox) - w / 2, 0), max(abs(y - oy) - h / 2, 0)) < r for ox, oy, r, o, _ in obst if o != own):
            return False
        # 0.3 mm between texts of one knob, 1.2 mm to another's, so neighbours' numerals don't read as one ('9 50')
        return not any(abs(x - px) < (w + pw) / 2 + g and abs(y - py) < (h + ph) / 2 + g
                       for px, py, pw, ph, po in placed for g in [0.3 if po == own else 1.2])
    def put_text(s, x, y, size, own, force=False, bold=False):
        w, h = text_box(s, size)
        if force or free(x, y, w, h, own):
            placed.append((x, y, w, h, own)); P.texts.append((s, x, y, size, bold))
            return True
        return False
    pairs = PAIRS.get(key, {}); paired = {gref for gref, _ in pairs.values()} | set(pairs)
    at = {ref: (x, y, big) for ref, name, x, y, big in pots}
    for ref, name, x, y, big in pots:                # names first: ring numbers give way to them
        if ref not in paired and name:
            put_text(name, x, y - D_KNOB / 2 - 4.2, 2.0, ref, force=True, bold=True)
    for fref, (gref, band) in pairs.items():         # bracket over a gain / frequency pair, band name in its middle
        (xg, y, _), (xf, _, _) = at[gref], at[fref]; yb, xm = y - D_KNOB / 2 - 4.2, (xg + xf) / 2
        hw = 0.47 * 2.0 * len(band) / 2 + 0.8
        P.line(xg, yb, xm - hw, yb); P.line(xm + hw, yb, xf, yb); P.line(xg, yb, xg, yb + 0.6); P.line(xf, yb, xf, yb + 0.6)
        put_text(band, xm, yb, 2.0, None, force=True, bold=True)
    for ref, name, x, y, big in pots:
        rk = D_KNOB / 2; rd, rn = rk + 0.85, rk + 2.15
        dots, labels, unit = scale_of(ref, name)
        for t in dots:
            a = math.radians(-150 + 300 * t); px, py = x + rd * math.sin(a), y - rd * math.cos(a)
            P.rects.append((px - 0.27, py - 0.27, px + 0.27, py + 0.27))              # square dots, as the Delta's
        for t, s in labels:
            a = math.radians(-150 + 300 * t)
            put_text(s, x + rn * math.sin(a), y - rn * math.cos(a), 1.6, ref)
        if unit: put_text(unit, x, y + rn * math.cos(math.radians(30)), 1.5, ref)
    for name, x, y, dual in faders:                  # ticks both sides of the slot, dB numbers on the right (Delta)
        last_tick = last = None                      # from the bottom up, so the infinity mark always prints; marks the
        for db, s in reversed(FADER_MARKS):          # (approximate) law crowds there give way: ticks 1.2, numbers 3.0 mm
            yy = y + 50.0 - 100.0 * (0.0 if db is None else fader_theta(db))
            major = db in (10, 0, None)
            if last_tick is not None and abs(yy - last_tick) < 1.2: continue
            last_tick = yy
            for side in (-1, 1):
                x0 = x + side * 11.6; x1 = x0 + side * (2.6 if major else 1.8)
                P.rects.append((min(x0, x1), yy - (0.32 if db == 0 else 0.18), max(x0, x1), yy + (0.32 if db == 0 else 0.18)))
            if last is None or abs(yy - last) >= 3.0:
                put_text(s, x + 16.0, yy, 1.6, None, force=True); last = yy
        put_text(name, x, y + 65.0, 2.4 if dual else 2.0, None, force=True, bold=True)
    for yr in RULES.get(key, ()):                    # section rules, full width, broken where a part sits on them
        xs = [-0.6, width - 1.7]
        cuts = sorted((ox - rp - 0.8, ox + rp + 0.8) for ox, oy, r, o, rp in obst if abs(oy - yr) < rp + 0.3)
        x0 = xs[0]
        for a, b in cuts + [(xs[1], xs[1])]:
            if a > x0 + 0.5: P.line(x0, yr, min(a, xs[1]), yr)
            x0 = max(x0, b)
    for xm, y0, y1 in METERS.get(key, ()):           # meter block outline
        for (ax, ay), (bx, by) in (((xm - 4.0, y0 - 5.0), (xm + 4.0, y0 - 5.0)), ((xm - 4.0, y1 + 5.0), (xm + 4.0, y1 + 5.0)),
                                   ((xm - 4.0, y0 - 5.0), (xm - 4.0, y1 + 5.0)), ((xm + 4.0, y0 - 5.0), (xm + 4.0, y1 + 5.0))):
            P.line(ax, ay, bx, by, 0.25)

def boards(key, render_dir=None):
    d = render_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'render')
    return json.load(open(os.path.join(d, key + '.json')))

def layout(key, data=None, number=None):
    """The Panel of module key ('strip', 'group', 'master') from its boards' JSON (render/<key>.json by default).
    number: the strip number / group number printed at the bottom (the 3D console adds its own per instance)."""
    names = NAMES[key]; P = Panel(key, WIDTH[key])
    pots, faders, obst = [], [], []
    for bd in data if data is not None else boards(key):
        # in reference order: a board's footprint order changes whenever it is re-placed, and where two scales' numerals
        # collide the one placed first stays, so the artwork must not depend on it
        for p in sorted(bd['parts'], key=lambda p: (p['ref'].rstrip('0123456789'), int('0' + p['ref'][len(p['ref'].rstrip('0123456789')):]))):
            fp, ref = p['fp'], p['ref']
            if ref.startswith('H') and fp.startswith('MountingHole'):     # a standoff: a blind stud in the panel's back
                kind_ = 'jack' if 'jack' in bd['file'] else 'main'
                P.studs.append((p['x'], p['y'], ref, kind_))
                if kind_ == 'jack':                       # without studs: a countersunk M3 screw (P4), so the print keeps off it
                    obst.append((p['x'], p['y'], CSK_D / 2 + 0.6, ref, CSK_D / 2))
                continue
            name, colour = names.get(ref, ('', 'grey'))
            f = p.get('feature'); reg = lookup(fp)
            if 'LED_D' in fp:
                big = 'D5.0' in fp
                lg, st = led_state(p, names)
                P.holes.append(('round', f[0], f[1], LED_HOLE[big])); obst.append((f[0], f[1], 3.0, ref, 3.0))
                P.parts.append((ref, 'led', f[0], f[1], 0.0, lg, st, big))
                if lg: P.texts.append((lg, f[0], f[1] - (5.0 if big else 3.8), 1.6, False))
            if p['model'] or not reg: continue
            mod, kw = reg; kind = mod.__name__.rsplit('.', 1)[-1]
            if not (mod.FEATURE and f): continue
            P.parts.append((ref, kind, f[0], f[1], p['rot'], name, colour, False))
            rp = {'alpha_pot': D_KNOB / 2 + 0.3, 'alps_rk09l': D_KNOB / 2 + 0.3, 'ck_pva2': 4.2, 'neutrik_nj6fd_v': 7.3,
                  'neutrik_nc3mav': 12.0}.get(kind, 0.0)
            obst.append((f[0], f[1], rp + 2.5 if kind in POTS else rp, ref, rp))   # pots: keep their ring clear
            if kind == 'ck_pva2': obst.append((f[0], f[1] - 5.8, 0.4 * len(name) + 0.4, ref, 0.0))     # its legend
            if kind in HOLE: P.holes.append(('round', f[0], f[1], HOLE[kind]))
            elif kind == 'neutrik_nc3mav': P.holes.append(('xlr', f[0], f[1], p['rot']))
            elif kind == 'bourns_ptb':
                P.holes.append(('slot', f[0], f[1], p['rot']))
                faders.append((name, f[0], f[1], 'Dual' in fp))
            if kind in POTS: pots.append((ref, name, f[0], f[1], False))
            elif kind in LEGEND and name: P.texts.append((name, f[0], f[1] + LEGEND[kind][0], LEGEND[kind][1], False))
    panel_print(P, pots, faders, obst)
    if key == 'master':                              # meter legends: channel letter, dB scale outboard
        for side, x in (('L', 18.0), ('R', 60.6)):
            P.texts.append((side, x, 318.5, 2.4, False))
            for v in (18, 12, 6, 0, -6, -12, -20):
                P.texts.append((f'{v:+d}' if v else '0', x + (-6.0 if side == 'L' else 6.2), 422.0 - 5.0 * (v + 20) / 2, 1.5, False))
    label = LABEL.get(key) or (number and (str(number) if key == 'strip' else f'GROUP {number}'))
    if label: P.texts.append((label, X0 + P.width / 2, 494.0, 3.0, False))
    return P
