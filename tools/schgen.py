"""Shared schematic builder for the goa-console generators (gen.py = strip, gen_master.py = master).
A design is a list of blocks of parts; each part lists its pins and the net on each pin.
Each pin gets a net label (or a GNDA/GNDD power symbol, or a no-connect flag); blocks are laid out
in rows. Writes the .kicad_sch (KiCad 7 file format) and <name>_intended.json for tools/verify.py."""
import copy, uuid, os, json, collections, math, re
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from kiutils.items.common import Position, Property, Effects, Font, PageSettings, TitleBlock, Justify
from kiutils.items.schitems import (SchematicSymbol, LocalLabel, NoConnect, Text, Connection, Junction,
                                    SymbolProjectInstance, SymbolProjectPath, HierarchicalSheetInstance,
                                    GlobalLabel, HierarchicalSheet, HierarchicalSheetProjectInstance,
                                    HierarchicalSheetProjectPath)
from kiutils.items.common import Stroke
import schdraw

LIBDIR = next((d for d in (os.environ.get('KICAD_SYMBOL_DIR', ''), '/usr/share/kicad/symbols/',
                            '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/')
               if d and os.path.isdir(d)), None)
if LIBDIR is None: raise SystemExit('KiCad symbol library not found; set KICAD_SYMBOL_DIR')
LIBDIR = os.path.join(LIBDIR, '')
PROJDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PROJLIB = 'goa-console'          # project symbol library: goa-console.kicad_sym
U = lambda: str(uuid.uuid4())
NS = uuid.UUID('6a1f3c52-9d0e-4b7a-8f21-5c3e0d9b7a44')   # stable UUIDs: same design -> same file, PCB link survives regeneration

SYM = {  # key: (lib, symbol)
 'R': ('Device', 'R'), 'C': ('Device', 'C'), 'CP': ('Device', 'C_Polarized'),
 'POT': ('Device', 'R_Potentiometer'), 'POT2': ('Device', 'R_Potentiometer_Dual'),
 'LED': ('Device', 'LED'), 'NT': ('Device', 'NetTie_2'),
 'OPA': ('Amplifier_Operational', 'OPA1612AxD'), 'CMP': ('Comparator', 'LM393'),
 'JFET': ('Transistor_FET', 'MMBFJ112'), 'D': ('Diode', '1N4148'),
 'JACK': ('Connector_Audio', 'AudioJack3'), 'JACKSW': ('Connector_Audio', 'AudioJack3_SwitchTR'),
 'SW': ('Switch', 'SW_DPDT_x2'), 'SJ2': ('Jumper', 'SolderJumper_2_Bridged'),
 'SJ3': ('Jumper', 'SolderJumper_3_Bridged12'),
 'HDR': ('Connector_Generic', 'Conn_02x17_Odd_Even'), 'TAB': ('Connector_Generic', 'Conn_01x01'),
 'OPA1656': ('Amplifier_Operational', 'OPA1656ID'), 'MHPAD': ('Mechanical', 'MountingHole_Pad'),
 'GNDA': ('power', 'GNDA'), 'GNDD': ('power', 'GNDD'), 'GNDM': ('goa-console', 'GNDM'), 'PHONESGND': ('goa-console', 'PHONESGND'), 'FLAG': ('power', 'PWR_FLAG'),
}
FP = {
 'R': 'Resistor_SMD:R_0805_2012Metric', 'C': 'Capacitor_SMD:C_0805_2012Metric',
 'OPA': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'CMP': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
 'LED': 'LED_THT:LED_D3.0mm', 'HDR': 'Connector_IDC:IDC-Header_2x17_P2.54mm_Vertical',
 'NT': 'NetTie:NetTie-2_SMD_Pad0.5mm', 'CP': 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',
 'SJ2': 'Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm',
 'SJ3': 'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm',
 # panel parts (see channel_strip_schematic_spec.md, panel parts)
 'JACKSW': 'Connector_Audio:Jack_6.35mm_Neutrik_NRJ6HF_Horizontal',
 'POT': 'Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical',
 'POT2': 'Potentiometer_THT:Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical',
 'SW': 'Button_Switch_THT:SW_Push_2P2T_Toggle_CK_PVA2xxH1xxxxxxV2',
 'TAB': 'goa-console:Keystone_1287-ST_FastOn_Tab_6.35mm',
 'OPA1656': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
 'MHPAD': 'MountingHole:MountingHole_3.2mm_M3_Pad',     # plated: bonds a jack board's CHASSIS to its standoff and the panel
}
FADER_FP = 'goa-console:Potentiometer_Bourns_PTB0143_Slide_100mm'
MPN = {'JACKSW': 'Neutrik NRJ6HF', 'POT': 'Alpha RD901F-40-15R1-A10K', 'POT2': 'Alpha RD902F-40-15R1-A10K (dual, log)',
       'SW': 'C&K PVA2 EE H1 1.7N V2', 'TAB': 'Keystone 1287-ST',
       'OPA1656': 'TI OPA1656IDR'}
CAP_FP = {'220u': 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', '47u': 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',
          '2.2u': 'Capacitor_SMD:C_1206_3216Metric'}
AMPS = {'OPA': 3, 'CMP': 3, 'OPA1656': 3, 'TL072': 3, 'LM2901': 5}     # op-amp / comparator keys: power unit
DGPWR = {'DG': 5}
POWER_SYMBOL_NETS = ('GNDA', 'GNDD', 'GNDM', 'PHONESGND')
HIDE_PIN_NUMBERS = {'R', 'C', 'CP', 'POT', 'POT2', 'D', 'LED', 'ZEN', 'SCH', 'NT', 'DS', 'DZ', 'TAB', 'MHPAD', 'GNDA', 'GNDD', 'FLAG', 'TRIM', 'SJO'}
HIDE_PIN_NAMES_ONLY = {'SJ3', 'SJ2', 'LME49600', 'JFET'}
HIDE_PIN_NAMES = HIDE_PIN_NUMBERS | {'SW', 'LINK', 'HDR', 'CONN6', 'CONN2', 'TAB', 'JACK', 'JACKSW', 'HDR5', 'NPN', 'PNP', 'PWRIN'}

# ---------------------------------------------------------------- netlist
blocks = []          # (title, [parts])
DRAW = {}            # id(parts list) -> draw function (schdraw.Drawing): the block is drawn, not laid out in rows
FRAGS = {}           # id(parts list) -> [(w, h, fn)]: drawn fragments of a block, laid out by flow() (tools/frags.py)
def frag(b, w, h, fn, last=False): FRAGS.setdefault(id(b), []).append((w, h, fn, last))   # last: after the others (power units)

def frag_box(parts, pins_of, w, h, fn, tight=False):
    """(ox, oy, w, h) in grid units: where to put a fragment's origin so labels sticking out left / up stay inside its
    box, and the box's size; measured from what fn draws, label texts included (~0.45 grid per character).
    tight: the box starts at what is drawn, not at the origin (a piece of a larger drawing)."""
    s = schdraw.Drawing(parts, pins_of, (0, 0)); fn(s)
    xs, ys = ([], []) if tight else ([0.0], [0.0])
    for a, b in s.wires: xs += [a[0], b[0]]; ys += [a[1], b[1]]
    for (cx, cy, *_) in s.place.values(): xs += [cx - 5.08, cx + 5.08]; ys += [cy - 5.08, cy + 5.08]
    for net, (px, py), side in s.ports:
        n = (len(net) * 0.45 + 0.6) * schdraw.G
        xs.append(px - n if side == 'L' else px + n if side == 'R' else px)
        ys.append(py - n if side == 'U' else py + n if side == 'D' else py)
    for text, (px, py), size in s.notes:                  # notes: left-justified text above their point
        xs += [px, px + len(text) * size * 0.85]; ys += [py - size * 1.2, py]
    g = schdraw.G; x0, x1, y0, y1 = min(xs) / g, max(xs) / g, min(ys) / g, max(ys) / g
    if tight: ox, oy = -math.floor(x0), -math.floor(y0)
    else: ox, oy = math.ceil(max(0, -x0)), math.ceil(max(0, -y0))
    return ox, oy, math.ceil(max(w, x1) + ox), math.ceil(max(h, y1) + oy)

def flow(frags, maxw=110, cell=(13, 11)):
    """A block's draw function from its fragments: rows of fragments (left to right, wrapping at maxw grid units),
    then every part no fragment placed, labelled, in rows of cells under them."""
    def draw(d):
        x = y = rowh = 0
        for w, h, fn, _ in [f for f in frags if not f[3]] + [f for f in frags if f[3]]:
            ox, oy, w, h = frag_box(d.parts, d.pins_of, w, h, fn)
            if x and x + w > maxw: x, y, rowh = 0, y + rowh + 4, 0
            d.shift(x + ox, y + oy); fn(d); d.shift(-x - ox, -y - oy)
            x += w + 4; rowh = max(rowh, h)
        rest = [pt for pt in d.parts if (pt['ref'], pt['unit']) not in d.place]
        if rest:
            y0 = y + rowh + (6 if frags else 3); per = max(1, maxw // cell[0])
            for i, pt in enumerate(rest):
                d.at(pt['ref'], 2 + (i % per) * cell[0], y0 + (i // per) * cell[1], unit=pt['unit'])
    return draw
PIECES = {}          # id(parts list) -> a drawn block's pieces (each drawn from the block's origin; packed apart on pages)
def block(title, draw=None):
    blocks.append((title, []))
    if isinstance(draw, list):
        def keep(f):                     # a piece leaves the drawing's origin where it found it
            def run(d): o = (d.ox, d.oy); f(d); d.ox, d.oy = o
            return run
        PIECES[id(blocks[-1][1])] = ps = [keep(f) for f in draw]
        draw = lambda d: [f(d) for f in ps]
    if draw: DRAW[id(blocks[-1][1])] = draw
    return blocks[-1][1]
def P(lst, ref, key, value, pins, unit=1, fp=None, mpn=None, dnp=False):
    lst.append(dict(ref=ref, key=key, value=value, pins={str(k): v for k, v in pins.items()}, unit=unit, fp=fp,
                    mpn=MPN.get(key, '') if mpn is None else mpn, dnp=dnp))

# ---------------------------------------------------------------- library symbols
libs = {}
def libsym(key):
    lib, name = SYM[key]
    if lib not in libs:
        path = os.path.join(PROJDIR, PROJLIB + '.kicad_sym') if lib == PROJLIB else LIBDIR + lib + '.kicad_sym'
        libs[lib] = {s.entryName: s for s in SymbolLib.from_file(path).symbols}
    s = libs[lib][name]
    if s.extends:
        base = libs[lib][s.extends]; f = copy.deepcopy(base)
        f.entryName = name; f.extends = None
        # merge like KiCad's Flatten(): derived fields override, base-only fields (ki_locked, Sim.*) stay
        for p in s.properties:
            i = next((k for k, q in enumerate(f.properties) if q.key == p.key), None)
            if i is None: f.properties.append(copy.deepcopy(p))
            else: f.properties[i] = copy.deepcopy(p)
        for u in f.units: u.entryName = name
    else:
        f = copy.deepcopy(s)
    f.libraryNickname = lib
    # KiCad 10's (pin_numbers / pin_names (hide yes)) isn't read by kiutils: restore what the library hides
    if key in HIDE_PIN_NUMBERS: f.hidePinNumbers = True
    if key in HIDE_PIN_NAMES or key in HIDE_PIN_NAMES_ONLY or key.startswith('LINK'): f.pinNamesHide = True
    return f

def pins_of(sym, unit):
    out = {}
    for u in sym.units:
        if u.unitId in (0, unit):
            for p in u.pins: out[p.number] = (p.position.X, p.position.Y)
    return out

def pin_out(sym, unit, pn):
    """Unit vector (library coordinates) pointing away from the body at pin pn: opposite the pin's own direction."""
    for u in sym.units:
        if u.unitId in (0, unit):
            for p in u.pins:
                if p.number == pn:
                    a = math.radians(p.position.angle or 0); return -round(math.cos(a)), -round(math.sin(a))
    return None

def pin_type(sym, unit, pn):
    return next((p.electricalType for u in sym.units if u.unitId in (0, unit) for p in u.pins if p.number == pn), None)

def outward(px, py):
    if abs(px) >= abs(py): return 'R' if px > 0 else 'L'
    return 'T' if py > 0 else 'B'
PWR_ANG = {'B': 0, 'T': 180, 'R': 90, 'L': 270}
LBL = {'R': (0, 'left'), 'L': (180, 'right'), 'T': (90, 'left'), 'B': (270, 'right')}

# ---------------------------------------------------------------- build
def build(out, project, title, comments, paper='A1', perrow=22, revision='3.0', date='2026-10-19', only=None, drawn=True, col_height=None, last=(), flowed=False, pages=None):
    """Write the schematic. paper='auto' sizes a User page to fit. only: a predicate on block titles (pilot sheets).
    pages: dict(paper, folder) writes a hierarchy instead: the blocks' fragments packed onto pages of that size (a block
    runs on to the next page when it doesn't fit), one sub-sheet file per page in folder, global labels between them,
    and a root sheet (out) holding the sheet symbols."""
    sch = Schematic.create_new()
    K = lambda *a: str(uuid.uuid5(NS, project + '/' + '/'.join(map(str, a))))
    seq = collections.Counter()
    def S(kind): seq[kind] += 1; return K(kind, seq[kind])
    sch.version = 20230121; sch.generator = 'eeschema'; sch.uuid = K('root')
    sch.titleBlock = TitleBlock(title=title, date=date, revision=revision, company='', comments=comments)
    sch.sheetInstances = [HierarchicalSheetInstance(instancePath='/', page='1')]
    root = '/' + sch.uuid
    used = {}
    font = lambda s=1.27: Effects(font=Font(height=s, width=s))
    grid = lambda v: round(v / 2.54) * 2.54

    X0, Y0, CELLW, CELLH = 30.48, 40.64, 33.02, 27.94
    y = Y0
    pwr_n = [0]
    allpins = collections.defaultdict(set)          # net -> {(ref, pin)} over the whole design
    for _, parts in blocks:
        for pt in parts:
            for pn, net in pt['pins'].items(): allpins[net].add((pt['ref'], pn))
    wide = [0.0]; hmax = [0.0]

    def field_layout(key, ang, cx, cy, side=None):
        """Reference and value positions for a drawn part: (x, y, angle, justify) each, None = keep the default.
        Text angles: KiCad turns a field with its symbol, so a 90 / 270 symbol gets 90 to read horizontally."""
        horiz = (ang % 180) == 90; fa = 90 if horiz else 0
        if key in ('FB', 'PTC') and horiz:                         # clear of the slanted body
            if side == 'U': return (cx, cy - 6.6, fa, None), (cx, cy - 4.7, fa, None)
            return (cx, cy - 4.7, fa, None), (cx, cy + 4.7, fa, None)
        if key in ('C', 'CP') and horiz:                           # clear of the plates
            if side == 'U': return (cx, cy - 5.2, fa, None), (cx, cy - 3.3, fa, None)
            if side == 'D': return (cx, cy + 3.3, fa, None), (cx, cy + 5.2, fa, None)
            return (cx, cy - 3.3, fa, None), (cx, cy + 3.3, fa, None)
        if key in ('R', 'C', 'CP', 'FB'):
            if horiz and side == 'U': return (cx, cy - 4.45, fa, None), (cx, cy - 2.54, fa, None)
            if horiz and side == 'D': return (cx, cy + 2.54, fa, None), (cx, cy + 4.45, fa, None)
            if horiz: return (cx, cy - 2.54, fa, None), (cx, cy + 2.54, fa, None)
            if side == 'L': return (cx - 2.54, cy - 1.27, fa, 'right'), (cx - 2.54, cy + 1.27, fa, 'right')
            return (cx + 2.54, cy - 1.27, fa, 'left'), (cx + 2.54, cy + 1.27, fa, 'left')
        if key in AMPS:
            if side == 'U': return (cx, cy - 8.89, fa, None), (cx, cy - 6.35, fa, None)
            return (cx, cy + 6.35, fa, None), (cx, cy + 8.89, fa, None)
        if key in ('LED', 'D', 'ZEN', 'SCH', 'DZ', 'DS'):
            if horiz and side == 'L': return (cx - 2.54, cy - 1.27, fa, 'right'), (cx - 2.54, cy + 1.27, fa, 'right')
            if horiz: return (cx + 2.54, cy - 1.27, fa, 'left'), (cx + 2.54, cy + 1.27, fa, 'left')
            if side == 'U': return (cx, cy - 4.45, fa, None), (cx, cy - 2.8, fa, None)
            return (cx, cy - 3.18, fa, None), (cx, cy + 3.18, fa, None)
        if key in ('NPN', 'PNP'): return (cx + 5.08, cy - 1.27, fa, 'left'), (cx + 5.08, cy + 1.27, fa, 'left')
        if key == 'LED2': return (cx, cy - 6.35, fa, None), (cx, cy + 6.35, fa, None)   # round dual LED: K left, A1 / A2 right
        if key == 'HDR' or (key.startswith('LINK') and key[4:].isdigit()):
            h = ((17 if key == 'HDR' else int(key[4:])) + 2) * 1.27
            return (cx, cy - h, fa, None), (cx, cy + h, fa, None)
        if key == 'CONN6': return (cx, cy - 10.16, fa, None), (cx, cy + 10.16, fa, None)
        if key == 'LME49600': return (cx + 2.54, cy - 6.35, fa, 'left'), (cx + 2.54, cy - 4.83, fa, 'left')
        if key == 'PWRIN': return (cx, cy - 11.43, fa, None), (cx, cy + 11.43, fa, None)
        if key == 'TAB': return (cx + 2.54, cy - 1.27, fa, 'left'), (cx + 2.54, cy + 1.27, fa, 'left')
        if key == 'NT' and side == 'R': return (cx - 2.54, cy - 1.9, fa, 'left'), (cx - 2.54, cy + 1.9, fa, 'left')
        if key == 'NT': return (cx, cy - 2.54, fa, None), (cx, cy + 2.54, fa, None)
        if key == 'SJ3' and side == 'R': return (cx + 2.54, cy - 4.45, fa, 'left'), (cx + 2.54, cy - 2.67, fa, 'left')
        if key in ('SJ2', 'SJO'): return (cx, cy - 4.45, fa, None), (cx, cy - 2.54, fa, None)
        if key == 'SJ3': return (cx, cy - 6.35, fa, None), (cx, cy - 4.45, fa, None)
        if key == 'SW' and side == 'D': return (cx, cy + 5.08, fa, None), (cx, cy + 6.85, fa, None)
        if key == 'SW' and side == 'U': return (cx, cy - 6.85, fa, None), (cx, cy - 5.08, fa, None)
        if key == 'SW': return (cx, cy - 5.08, fa, None), (cx, cy + 5.08, fa, None)
        if key == 'DRV134': return (cx - 2.54, cy - 11.43, fa, 'right'), (cx - 2.54, cy - 9.53, fa, 'right')
        if key == 'TRIM' and horiz: return (cx, cy - 4.6, fa, None), (cx, cy - 2.9, fa, None)
        if key == 'TRIM': return (cx - 2.54, cy - 1.27, fa, 'right'), (cx - 2.54, cy + 1.27, fa, 'right')
        if key == 'RELAY': return (cx + 16.51, cy - 1.27, fa, 'left'), (cx + 16.51, cy + 1.27, fa, 'left')
        if key == 'POT' and horiz and side == 'R': return (cx - 2.54, cy - 3.81, fa, 'left'), (cx - 2.54, cy - 6.35, fa, 'left')
        if key == 'POT' and horiz: return (cx, cy - 3.81, fa, None), (cx, cy - 6.35, fa, None)
        if key == 'POT' and side == 'L': return (cx - 2.54, cy - 1.27, fa, 'right'), (cx - 2.54, cy + 1.27, fa, 'right')
        if key == 'POT': return (cx + 4.45, cy - 1.9, fa, 'left'), (cx + 4.45, cy + 1.9, fa, 'left')
        if key == 'POT2' and side == 'W': return (cx - 24.13, cy - 1.27, fa, 'right'), (cx - 24.13, cy + 1.27, fa, 'right')
        if key == 'POT2': return (cx - 13.97, cy - 1.27, fa, 'right'), (cx - 13.97, cy + 1.27, fa, 'right')
        return None, None

    def add_symbol(pt, cx, cy, ang=0, mirror=None, drawn=False, side=None):
        lib, name = SYM[pt['key']]
        if (lib, name) not in used: used[(lib, name)] = libsym(pt['key']); sch.libSymbols.append(used[(lib, name)])
        ls = used[(lib, name)]
        fp = pt['fp'] or FP.get(pt['key'], next((p.value for p in ls.properties if p.key == 'Footprint'), ''))
        is_pwr = pt['key'] in ('FLAG',)
        horiz = (ang % 180) == 90
        rx, ry = (cx + 2.54, cy - 8.89) if not horiz else (cx, cy - 3.81)
        vx, vy = (cx + 2.54, cy + 8.89) if not horiz else (cx, cy + 3.81)
        if pt['key'] in ('R', 'C', 'CP') and not horiz: rx, ry, vx, vy = cx + 2.54, cy - 1.27, cx + 2.54, cy + 1.27
        jl = Justify(horizontally='left') if (pt['key'] in ('R', 'C', 'CP') and not horiz) else Justify()
        ra = va = 0; rj = vj = jl
        vhide = is_pwr
        if drawn:
            fr, fv = field_layout(pt['key'], ang, cx, cy, side)
            if pt['unit'] == AMPS.get(pt['key'], DGPWR.get(pt['key'])):           # power units: reference only
                fr, fv, vhide = (cx - 3.81, cy, 0, 'right'), None, True
            if is_pwr: fv = (cx, cy - 4.45, 0, None)
            if pt['key'] == 'DG' and pt['unit'] in (1, 2, 3, 4):              # switch sections: reference above
                fr, fv, vhide = (cx - 3.81, cy - 3.8, 0, 'right'), None, True    # above the S pin and its number
            if (ang % 360 == 180 or (ang % 360 == 90 and pt['key'] in ('LED', 'D', 'ZEN', 'SCH', 'DZ', 'DS', 'TRIM'))) != (mirror == 'y'):
                # KiCad flips a field's justification with the symbol (a 90-degree diode's 90-degree text reads at 180)
                sw = {'left': 'right', 'right': 'left'}
                fr = fr and fr[:3] + (sw.get(fr[3], fr[3]),); fv = fv and fv[:3] + (sw.get(fv[3], fv[3]),)
            if fr: rx, ry, ra, j = fr; rj = Justify(horizontally=j) if j else Justify()
            if fv: vx, vy, va, j = fv; vj = Justify(horizontally=j) if j else Justify()
        props = [Property(key='Reference', value=pt['ref'], id=0, position=Position(rx, ry, ra), effects=Effects(font=Font(height=1.27, width=1.27), justify=rj, hide=is_pwr)),
                 Property(key='Value', value=pt['value'], id=1, position=Position(vx, vy, va), effects=Effects(font=Font(height=1.27, width=1.27), justify=vj, hide=vhide and not is_pwr)),
                 Property(key='Footprint', value=fp, id=2, position=Position(cx, cy, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                 Property(key='Datasheet', value='', id=3, position=Position(cx, cy, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True))]
        if pt['mpn']: props.append(Property(key='MPN', value=pt['mpn'], id=4, position=Position(cx, cy, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)))
        pp = pins_of(ls, pt['unit'])
        ss = SchematicSymbol(libraryNickname=lib, entryName=name, position=Position(cx, cy, ang), unit=pt['unit'],
                             inBom=(not is_pwr) and ls.inBom is not False, onBoard=not is_pwr, uuid=K('sym', pt['ref'], pt['unit']), properties=props,
                             pins={n: K('pin', pt['ref'], pt['unit'], n) for n in pp},
                             instances=[SymbolProjectInstance(name=project, paths=[SymbolProjectPath(sheetInstancePath=root, reference=pt['ref'], unit=pt['unit'])])])
        if mirror: ss.mirror = mirror
        if pt.get('dnp'): ss.dnp = True
        sch.schematicSymbols.append(ss)
        for pn in pt['pins']:
            if pn not in pp: raise SystemExit(f"{pt['ref']} unit {pt['unit']} has no pin {pn}")
        return pp

    def power(net, ax, ay, ang, key):
        pwr_n[0] += 1; gs = used.setdefault(('power', net), None)
        if gs is None: used[('power', net)] = gs = libsym(net); sch.libSymbols.append(gs)
        ref = f'#PWR{pwr_n[0]:03d}'
        # KiCad turns and flips a field with its symbol: these read upright, beside the symbol
        vx, vy, va, vj = {0: (ax + 1.9, ay + 2.0, 0, 'left'), 180: (ax + 1.9, ay - 2.0, 0, 'right'),
                          90: (ax + 3.8, ay, 90, 'right'), 270: (ax - 3.8, ay, 90, 'right')}[ang % 360]
        sch.schematicSymbols.append(SchematicSymbol(libraryNickname=SYM[net][0], entryName=net, position=Position(ax, ay, ang), unit=1,
            inBom=True, onBoard=True, uuid=K(*key),
            properties=[Property(key='Reference', value=ref, id=0, position=Position(ax, ay + 5, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                        Property(key='Value', value=net, id=1, position=Position(vx, vy, va), effects=Effects(font=Font(height=1.0, width=1.0), justify=Justify(horizontally=vj), hide=net in ('GNDA', 'GNDD') and ang % 360 != 180)),
                        Property(key='Footprint', value='', id=2, position=Position(ax, ay, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                        Property(key='Datasheet', value='', id=3, position=Position(ax, ay, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True))],
            pins={'1': K(*key, 'pin')},
            instances=[SymbolProjectInstance(name=project, paths=[SymbolProjectPath(sheetInstancePath=root, reference=ref, unit=1)])]))

    def attach(pt, pn, net, ax, ay, side):
        """An unwired pin: no-connect flag, power symbol or net label, pointing away from the symbol."""
        if net == 'NC':
            if pin_type(used[SYM[pt['key']]], pt['unit'], pn) == 'no_connect': return   # an NC pin by type: no flag
            sch.noConnects.append(NoConnect(position=Position(ax, ay), uuid=K('nc', pt['ref'], pt['unit'], pn)))
        elif net in POWER_SYMBOL_NETS:
            power(net, ax, ay, PWR_ANG[side], ('pwr', pt['ref'], pt['unit'], pn))
        else:
            ang, just = LBL[side]
            eff = Effects(font=Font(height=1.0, width=1.0), justify=Justify(horizontally=just, vertically='bottom'))
            add_label(net, ax, ay, ang, eff, K('lbl', pt['ref'], pt['unit'], pn))

    def add_label(net, x, y, ang, eff, uid):
        if pages:             # a global label's text sits centred in its box: 'bottom' put it on the outline (unreadable)
            eff = Effects(font=eff.font, justify=Justify(horizontally=eff.justify.horizontally))
            sch.globalLabels.append(GlobalLabel(text=net, shape='passive', position=Position(x, y, ang), effects=eff, uuid=uid))
        else: sch.labels.append(LocalLabel(text=net, position=Position(x, y, ang), effects=eff, uuid=uid))

    def emit(d, parts):
        """Write what the drawing d placed: symbols, wires, junctions, labels, power symbols, notes; label or flag every
        pin the drawing left bare. Returns the x and y coordinates used (mm)."""
        placed = [pt for pt in parts if (pt['ref'], pt['unit']) in d.place]
        pin_nets, side_of = [], {}
        for pt in placed:
            cx, cy, ang, mir = d.place[(pt['ref'], pt['unit'])]
            pp = add_symbol(pt, cx, cy, ang, mir, drawn=True, side=d.textside.get((pt['ref'], pt['unit']), d.textside.get(pt['ref'])))
            for pn, net in pt['pins'].items():
                px, py = pp[pn]; dx, dy = schdraw.xform(px, py, ang, mir)
                ax, ay = schdraw.snap(cx + dx), schdraw.snap(cy + dy)
                o = pin_out(used[SYM[pt['key']]], pt['unit'], pn)       # the way the pin points, not where it sits
                if o: ox_, oy_ = schdraw.xform(o[0], o[1], ang, mir); o = outward(ox_, -oy_)
                pin_nets.append((pt['ref'], pn, net, (ax, ay))); side_of[(pt['ref'], pn)] = o or outward(dx, -dy)
        groups, junctions = schdraw.check(d, pin_nets)
        byref = {(pt['ref'], pn): pt for pt in placed for pn in pt['pins']}
        for net, its in groups:
            pins = [it for it in its if it[0] == 'pin']
            wired = any(it[0] != 'pin' for it in its) or len(pins) > 1
            labelled = any(it[0] in ('port', 'gnd') for it in its)
            for k, it in enumerate(pins):
                (ref, pn), p = it[3], it[2]
                if not wired:
                    attach(byref[(ref, pn)], pn, net, p[0], p[1], side_of[(ref, pn)])
                elif not labelled and k == 0 and net != 'NC':
                    # a wired group with no label of its own: label it where it is local to this block only
                    # if the net also reaches pins outside the group
                    if net in POWER_SYMBOL_NETS or allpins[net] - {i[3] for i in pins}:
                        attach(byref[(ref, pn)], pn, net, p[0], p[1], side_of[(ref, pn)])
        for a, b in d.wires:
            sch.graphicalItems.append(Connection(type='wire', points=[Position(*a), Position(*b)],
                                                 stroke=Stroke(width=0, type='default'), uuid=S('wire')))
        for p in sorted(junctions):
            sch.junctions.append(Junction(position=Position(*p), diameter=0, uuid=S('junc')))
        for net, p, side in d.ports:
            ang, just = LBL[{'L': 'L', 'R': 'R', 'U': 'T', 'D': 'B'}[side]]
            add_label(net, p[0], p[1], ang, Effects(font=Font(height=1.27, width=1.27), justify=Justify(horizontally=just, vertically='bottom')), S('port'))
        for net, p, dirn in d.gnds:
            power(net, p[0], p[1], {'D': 0, 'U': 180, 'L': 270, 'R': 90}[dirn], ('gnd', S('g')))
        for text, p, size in d.notes:
            sch.texts.append(Text(text=text, position=Position(p[0], p[1], 0), uuid=S('note'),
                                  effects=Effects(font=Font(height=size, width=size), justify=Justify(horizontally='left'))))
        ys = [p_[1] for *_, p_ in pin_nets] + [q[1] for w_ in d.wires for q in w_] + [g[1][1] for g in d.gnds]
        xs = [p_[0] for *_, p_ in pin_nets] + [q[0] for w_ in d.wires for q in w_]
        return xs, ys

    order = [b_ for b_ in blocks if not b_[0].startswith(last or ('\0',))] + [b_ for b_ in blocks if last and b_[0].startswith(last)]
    if pages:
        G = schdraw.G; pinsf = lambda k, un: pins_of(libsym(k), un)
        W, H = pages.get('width', 104), pages.get('height', 57)            # usable area, grid units (A4: 264 x 145 mm, above the title block)
        PX0, PY0 = pages.get('x0', 7), pages.get('y0', 8)
        pagelist, segs, py = [], [], 0
        for btitle, parts in order:
            drawn = id(parts) in DRAW and id(parts) not in FRAGS                  # a drawn block: its pieces, or itself
            fr = FRAGS.get(id(parts)) or [(0, 0, f, False) for f in PIECES.get(id(parts), [DRAW.get(id(parts))]) if f]
            items = [f for f in fr if not f[3]] + [f for f in fr if f[3]]
            s = schdraw.Drawing(parts, pinsf, (0, 0))
            for f in items: f[2](s)
            for pt in [pt for pt in parts if (pt['ref'], pt['unit']) not in s.place]:      # undrawn: a labelled cell each
                items.append((13, 11, lambda d, pt=pt: d.at(pt['ref'], 3, 5, unit=pt['unit']), True))
            seg, x, rowh, cont = None, 0, 0, False
            queue = [frag_box(parts, pinsf, w, h, fn, tight=drawn) + (fn,) for w, h, fn, _ in items]
            def fits(w, h):                      # where the next box goes on this page: same row, next row, or None
                top = py + (0 if seg else 4)
                if seg is None or not x: return 'row' if top + h <= H or not (segs or seg) else None
                if x + w <= W and top + h <= H: return 'row'
                return 'next' if py + rowh + 3 + h <= H else None
            while queue:
                # in order, but when the next box doesn't fit, a later (smaller) one of the same block may fill the page
                k = next((i for i, (_, _, w, h, _) in enumerate(queue) if fits(w, h)), None)
                if k is None:                                              # page full: the block runs on overleaf
                    cont = seg is not None
                    pagelist.append(segs); segs, py, seg, x, rowh = [], 0, None, 0, 0
                    continue
                ox, oy, w, h, fn = queue.pop(k)
                if w > W or h > H: print(f'PAGE OVERFLOW {btitle[:40]!r}: {w} x {h} grid on a {W} x {H} page')
                if fits(w, h) == 'next': py += rowh + 3; x = rowh = 0
                if seg is None:
                    seg = [btitle.split('  ')[0] + ' (cont.)' if cont else btitle, parts, [], py]; segs.append(seg); py += 4
                seg[2].append((fn, x + ox, py + oy)); x += w + 4; rowh = max(rowh, h)
            py += rowh + 5
        if segs: pagelist.append(segs)
        base = os.path.dirname(os.path.abspath(out)); folder = pages['folder']
        os.makedirs(os.path.join(base, folder), exist_ok=True)
        for f in os.listdir(os.path.join(base, folder)):                 # stale pages of an earlier layout
            if f.endswith('.kicad_sch'): os.remove(os.path.join(base, folder, f))
        root_uuid = K('root'); files = []
        short = lambda s: re.split(r'  |:|\(|,| - ', s)[0].strip().replace(' / ', '-').replace('/', '-')   # '/' separates sheet paths
        for i, segs_ in enumerate(pagelist):
            names = list(dict.fromkeys(short(s_[0]) for s_ in segs_))      # every block on the page, in order
            uid = K('sheetsym', i); pname = f'{i + 2:02d} ' + ', '.join(names)
            sch = Schematic.create_new(); sch.version = 20230121; sch.generator = 'eeschema'; sch.uuid = K('page', i)
            sch.titleBlock = TitleBlock(title=', '.join(names), date=date, revision=revision, company=title, comments=comments)
            sch.paper = PageSettings(paperSize=pages.get('paper', 'A4'))
            used = {}; root = f'/{root_uuid}/{uid}'
            for stitle, parts, places, sy in segs_:
                sch.texts.append(Text(text=stitle, position=Position(PX0 * G, (PY0 + sy + 1.5) * G, 0), uuid=S('txt'),
                                      effects=Effects(font=Font(height=2.0, width=2.0), justify=Justify(horizontally='left'))))
                d = schdraw.Drawing(parts, pinsf, (PX0 * G, PY0 * G))
                for fn, fx, fy in places: d.shift(fx, fy); fn(d); d.shift(-fx, -fy)
                emit(d, parts)
            fname = f"{folder}/{i + 2:02d}_{re.sub(r'[^a-z0-9]+', '_', short(segs_[0][0]).lower()).strip('_')}.kicad_sch"
            sch.filePath = os.path.join(base, fname); sch.to_file(); files.append((uid, pname, fname))
        sch = Schematic.create_new(); sch.version = 20230121; sch.generator = 'eeschema'; sch.uuid = root_uuid
        sch.titleBlock = TitleBlock(title=title, date=date, revision=revision, company='', comments=comments)
        sch.paper = PageSettings(paperSize=pages.get('paper', 'A4'))
        sch.sheetInstances = [HierarchicalSheetInstance(instancePath='/', page='1')]
        for i, (uid, pname, fname) in enumerate(files):
            x, y_ = 17.78 + (i % 5) * 53.34, 30.48 + (i // 5) * 22.86
            sch.sheets.append(HierarchicalSheet(position=Position(x, y_), width=45.72, height=12.7, uuid=uid,
                stroke=Stroke(width=0.1524, type='solid'),
                sheetName=Property(key='Sheetname', value=pname, id=0, position=Position(x, y_ - 0.71, 0),
                                   effects=Effects(font=Font(height=1.27, width=1.27), justify=Justify(horizontally='left', vertically='bottom'))),
                fileName=Property(key='Sheetfile', value=fname, id=1, position=Position(x, y_ + 13.3, 0),
                                  effects=Effects(font=Font(height=1.0, width=1.0), justify=Justify(horizontally='left', vertically='top'))),
                instances=[HierarchicalSheetProjectInstance(name=project, paths=[HierarchicalSheetProjectPath(sheetInstancePath='/' + root_uuid, page=str(i + 2))])]))
        sch.filePath = out; sch.to_file()
        print('parts:', sum(len(p) for _, p in blocks), 'pages:', len(files) + 1)
        write_intended(out)
        return
    col_x, col_w = [X0], [0.0]
    for btitle, parts in order:
        if only and not only(btitle): continue
        if col_height and y > Y0 and y > col_height:               # next column (drawn sheets)
            col_x[0] = math.ceil((col_x[0] + col_w[0] + 40) / 2.54) * 2.54; col_w[0] = 0.0; y = Y0
        X0 = col_x[0]
        sch.texts.append(Text(text=btitle, position=Position(X0, y - 8.89, 0), effects=Effects(font=Font(height=2.0, width=2.0), justify=Justify(horizontally='left')), uuid=S('txt')))
        draw = (DRAW.get(id(parts)) or (flow(FRAGS.get(id(parts), [])) if flowed else None)) if drawn else None
        if draw:
            d = schdraw.Drawing(parts, lambda k, un: pins_of(libsym(k), un), (X0, y))
            draw(d)
            missing = [(pt['ref'], pt['unit']) for pt in parts if (pt['ref'], pt['unit']) not in d.place]
            if missing: raise SystemExit(f'{btitle}: not placed {missing}')
            xs, ys = emit(d, parts)
            col_w[0] = max(col_w[0], max(xs) - X0 + 10)
            wide[0] = max(wide[0], col_x[0] + col_w[0] - 30.48)
            y = math.ceil((max(ys) + 30) / 2.54) * 2.54                # block origins on the 2.54 grid
            hmax[0] = max(hmax[0], y)
            continue
        for i, pt in enumerate(parts):
            if pt['key'] == 'HDR':
                cx = grid(X0 + 20 + (i % perrow) * 60); cy = grid(y + 20)
            else:
                cx = grid(X0 + (i % perrow) * CELLW + 5.08); cy = grid(y + (i // perrow) * CELLH + 10.16)
            pp = add_symbol(pt, cx, cy)
            for pn, net in pt['pins'].items():
                px, py = pp[pn]; ax, ay = round(cx + px, 2), round(cy - py, 2)
                attach(pt, pn, net, ax, ay, outward(px, py))
        rows = max(1, (len(parts) + perrow - 1) // perrow)
        y += rows * CELLH + (30 if any(p['key'] == 'HDR' for p in parts) else 0) + 16
        wide[0] = max(wide[0], perrow * CELLW)

    if paper == 'auto':
        w = max(420, round(30.48 + wide[0] + 40)); h = max(297, round(max(y, hmax[0]) + 60))
        sch.paper = PageSettings(paperSize='User', width=w, height=h)
    else:
        sch.paper = PageSettings(paperSize=paper)
    sch.filePath = out
    sch.to_file()
    n = sum(len(p) for b_, p in blocks if not only or only(b_))
    print('parts:', n, 'labels:', len(sch.labels), 'sheet height used (mm):', round(y))
    write_intended(out, only)


def write_intended(out, only=None):
    intended = {}
    for b_, parts in blocks:
        if only and not only(b_): continue
        for pt in parts:
            for pn, net in pt['pins'].items():
                k = f"{pt['ref']}.{pn}"
                if k in intended and intended[k] != net: raise SystemExit(f'{k} assigned to {intended[k]} and {net}')
                intended[k] = net
    json.dump(intended, open(out.replace('.kicad_sch', '_intended.json'), 'w'), indent=0)


def keep_net_settings(d, path):
    """Net classes and patterns are each project's own (tools/netrules.py writes them): a generator that writes a
    .kicad_pro from master.kicad_pro keeps the existing project's net settings, and a project without any starts with
    the Default class only (never another board's classes and patterns)."""
    import json, os
    old = json.load(open(path)) if os.path.exists(path) else {}
    if 'net_settings' in old: d['net_settings'] = old['net_settings']; return d
    ns = d.get('net_settings', {})
    ns['classes'] = [c for c in ns.get('classes', []) if c['name'] == 'Default']
    ns['netclass_patterns'] = []; ns['netclass_assignments'] = {}
    return d
