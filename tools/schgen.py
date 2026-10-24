"""Shared schematic builder for the goa-console generators (gen.py = strip, gen_master.py = master).
A design is a list of blocks of parts; each part lists its pins and the net on each pin.
Each pin gets a net label (or a GNDA/GNDD power symbol, or a no-connect flag); blocks are laid out
in rows. Writes the .kicad_sch (KiCad 7 file format) and <name>_intended.json for tools/verify.py."""
import copy, uuid, os, json, collections, math
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from kiutils.items.common import Position, Property, Effects, Font, PageSettings, TitleBlock, Justify
from kiutils.items.schitems import (SchematicSymbol, LocalLabel, NoConnect, Text, Connection, Junction,
                                    SymbolProjectInstance, SymbolProjectPath, HierarchicalSheetInstance)
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
 'GNDA': ('power', 'GNDA'), 'GNDD': ('power', 'GNDD'), 'FLAG': ('power', 'PWR_FLAG'),
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
}
FADER_FP = 'goa-console:Potentiometer_Bourns_PTB0143_Slide_100mm'
MPN = {'JACKSW': 'Neutrik NRJ6HF', 'POT': 'Alpha RD901F-40 A10K', 'POT2': 'Alpha RD902F-40 B10K centre detent',
       'SW': 'C&K PVA2 EE H1 1.7N V2', 'TAB': 'Keystone 1287-ST'}
CAP_FP = {'220u': 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', '47u': 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',
          '2.2u': 'Capacitor_SMD:C_1206_3216Metric'}
POWER_SYMBOL_NETS = ('GNDA', 'GNDD')
HIDE_PIN_NUMBERS = {'R', 'C', 'CP', 'POT', 'POT2', 'D', 'LED', 'ZEN', 'SCH', 'NT'}
HIDE_PIN_NAMES = HIDE_PIN_NUMBERS | {'SW', 'LINK', 'HDR', 'CONN6', 'CONN2', 'TAB', 'JACK', 'JACKSW'}

# ---------------------------------------------------------------- netlist
blocks = []          # (title, [parts])
DRAW = {}            # id(parts list) -> draw function (schdraw.Drawing): the block is drawn, not laid out in rows
def block(title, draw=None):
    blocks.append((title, []))
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
    if key in HIDE_PIN_NAMES: f.pinNamesHide = True
    return f

def pins_of(sym, unit):
    out = {}
    for u in sym.units:
        if u.unitId in (0, unit):
            for p in u.pins: out[p.number] = (p.position.X, p.position.Y)
    return out

def outward(px, py):
    if abs(px) >= abs(py): return 'R' if px > 0 else 'L'
    return 'T' if py > 0 else 'B'
PWR_ANG = {'B': 0, 'T': 180, 'R': 90, 'L': 270}
LBL = {'R': (0, 'left'), 'L': (180, 'right'), 'T': (90, 'left'), 'B': (270, 'right')}

# ---------------------------------------------------------------- build
def build(out, project, title, comments, paper='A1', perrow=22, revision='3.0', date='2026-10-19', only=None, drawn=True, col_height=None, last=()):
    """Write the schematic. paper='auto' sizes a User page to fit. only: a predicate on block titles (pilot sheets)."""
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
        if key in ('R', 'C', 'CP'):
            if horiz and side == 'U': return (cx, cy - 4.45, fa, None), (cx, cy - 2.54, fa, None)
            if horiz and side == 'D': return (cx, cy + 2.54, fa, None), (cx, cy + 4.45, fa, None)
            if horiz: return (cx, cy - 2.54, fa, None), (cx, cy + 2.54, fa, None)
            if side == 'L': return (cx - 2.54, cy - 1.27, fa, 'right'), (cx - 2.54, cy + 1.27, fa, 'right')
            return (cx + 2.54, cy - 1.27, fa, 'left'), (cx + 2.54, cy + 1.27, fa, 'left')
        if key in ('OPA', 'CMP'): return (cx, cy + 6.35, fa, None), (cx, cy + 8.89, fa, None)
        if key in ('LED', 'D', 'ZEN', 'SCH'):
            if horiz: return (cx + 2.54, cy - 1.27, fa, 'left'), (cx + 2.54, cy + 1.27, fa, 'left')
            return (cx, cy - 3.18, fa, None), (cx, cy + 3.18, fa, None)
        if key == 'SJ2': return (cx, cy - 4.45, fa, None), (cx, cy - 2.54, fa, None)
        if key == 'SJ3': return (cx, cy - 6.35, fa, None), (cx, cy - 4.45, fa, None)
        if key == 'SW': return (cx, cy - 5.08, fa, None), (cx, cy + 5.08, fa, None)
        if key == 'POT' and horiz: return (cx, cy - 3.81, fa, None), (cx, cy - 6.35, fa, None)
        if key == 'POT': return (cx, cy + 7.62, fa, None), (cx, cy + 8.89, fa, None)
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
            if pt['key'] in ('OPA', 'CMP', 'DG') and pt['unit'] in (3, 5):    # power units: reference only
                fr, fv, vhide = (cx - 3.81, cy, 0, 'right'), None, True
            if is_pwr: fv = (cx, cy - 4.45, 0, None)
            if pt['key'] == 'DG' and pt['unit'] in (1, 2, 3, 4):              # switch sections: reference above
                fr, fv, vhide = (cx, cy - 3.18, 0, None), None, True
            if ang % 360 == 180:                                  # KiCad flips a field's justification with the symbol
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
        sch.schematicSymbols.append(SchematicSymbol(libraryNickname='power', entryName=net, position=Position(ax, ay, ang), unit=1,
            inBom=True, onBoard=True, uuid=K(*key),
            properties=[Property(key='Reference', value=ref, id=0, position=Position(ax, ay + 5, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                        Property(key='Value', value=net, id=1, position=Position(ax, ay + 4.5, 0), effects=Effects(font=Font(height=1.0, width=1.0), hide=True)),
                        Property(key='Footprint', value='', id=2, position=Position(ax, ay, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                        Property(key='Datasheet', value='', id=3, position=Position(ax, ay, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True))],
            pins={'1': K(*key, 'pin')},
            instances=[SymbolProjectInstance(name=project, paths=[SymbolProjectPath(sheetInstancePath=root, reference=ref, unit=1)])]))

    def attach(pt, pn, net, ax, ay, side):
        """An unwired pin: no-connect flag, power symbol or net label, pointing away from the symbol."""
        if net == 'NC':
            sch.noConnects.append(NoConnect(position=Position(ax, ay), uuid=K('nc', pt['ref'], pt['unit'], pn)))
        elif net in POWER_SYMBOL_NETS:
            power(net, ax, ay, PWR_ANG[side], ('pwr', pt['ref'], pt['unit'], pn))
        else:
            ang, just = LBL[side]
            eff = Effects(font=Font(height=1.0, width=1.0), justify=Justify(horizontally=just, vertically='bottom'))
            sch.labels.append(LocalLabel(text=net, position=Position(ax, ay, ang), effects=eff, uuid=K('lbl', pt['ref'], pt['unit'], pn)))

    order = [b_ for b_ in blocks if not b_[0].startswith(last or ('\0',))] + [b_ for b_ in blocks if last and b_[0].startswith(last)]
    col_x, col_w = [X0], [0.0]
    for btitle, parts in order:
        if only and not only(btitle): continue
        if col_height and y > Y0 and y > col_height:               # next column (drawn sheets)
            col_x[0] = math.ceil((col_x[0] + col_w[0] + 40) / 2.54) * 2.54; col_w[0] = 0.0; y = Y0
        X0 = col_x[0]
        sch.texts.append(Text(text=btitle, position=Position(X0, y - 8.89, 0), effects=Effects(font=Font(height=2.0, width=2.0), justify=Justify(horizontally='left')), uuid=S('txt')))
        draw = DRAW.get(id(parts)) if drawn else None
        if draw:
            d = schdraw.Drawing(parts, lambda k, un: pins_of(libsym(k), un), (X0, y))
            draw(d)
            missing = [(pt['ref'], pt['unit']) for pt in parts if (pt['ref'], pt['unit']) not in d.place]
            if missing: raise SystemExit(f'{btitle}: not placed {missing}')
            pin_nets, side_of = [], {}
            for pt in parts:
                cx, cy, ang, mir = d.place[(pt['ref'], pt['unit'])]
                pp = add_symbol(pt, cx, cy, ang, mir, drawn=True, side=d.textside.get(pt['ref']))
                for pn, net in pt['pins'].items():
                    px, py = pp[pn]; dx, dy = schdraw.xform(px, py, ang, mir)
                    ax, ay = schdraw.snap(cx + dx), schdraw.snap(cy + dy)
                    pin_nets.append((pt['ref'], pn, net, (ax, ay))); side_of[(pt['ref'], pn)] = outward(dx, -dy)
            groups, junctions = schdraw.check(d, pin_nets)
            byref = {(pt['ref'], pn): pt for pt in parts for pn in pt['pins']}
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
                ang, just = LBL[{'L': 'L', 'R': 'R', 'U': 'B', 'D': 'T'}[side]]
                sch.labels.append(LocalLabel(text=net, position=Position(p[0], p[1], ang), uuid=S('port'),
                    effects=Effects(font=Font(height=1.27, width=1.27), justify=Justify(horizontally=just, vertically='bottom'))))
            for net, p, dirn in d.gnds:
                power(net, p[0], p[1], {'D': 0, 'U': 180, 'L': 270, 'R': 90}[dirn], ('gnd', S('g')))
            for text, p, size in d.notes:
                sch.texts.append(Text(text=text, position=Position(p[0], p[1], 0), uuid=S('note'),
                                      effects=Effects(font=Font(height=size, width=size), justify=Justify(horizontally='left'))))
            ys = [p_[1] for *_, p_ in pin_nets] + [q[1] for w_ in d.wires for q in w_] + [g[1][1] for g in d.gnds]
            xs = [p_[0] for *_, p_ in pin_nets] + [q[0] for w_ in d.wires for q in w_]
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

    intended = {}
    for b_, parts in blocks:
        if only and not only(b_): continue
        for pt in parts:
            for pn, net in pt['pins'].items():
                k = f"{pt['ref']}.{pn}"
                if k in intended and intended[k] != net: raise SystemExit(f'{k} assigned to {intended[k]} and {net}')
                intended[k] = net
    json.dump(intended, open(out.replace('.kicad_sch', '_intended.json'), 'w'), indent=0)
