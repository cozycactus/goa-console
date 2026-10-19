"""Shared schematic builder for the goa-console generators (gen.py = strip, gen_master.py = master).
A design is a list of blocks of parts; each part lists its pins and the net on each pin.
Each pin gets a net label (or a GNDA/GNDD power symbol, or a no-connect flag); blocks are laid out
in rows. Writes the .kicad_sch (KiCad 7 file format) and <name>_intended.json for tools/verify.py."""
import copy, uuid, os, json, collections
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from kiutils.items.common import Position, Property, Effects, Font, PageSettings, TitleBlock, Justify
from kiutils.items.schitems import (SchematicSymbol, LocalLabel, NoConnect, Text,
                                    SymbolProjectInstance, SymbolProjectPath, HierarchicalSheetInstance)

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

# ---------------------------------------------------------------- netlist
blocks = []          # (title, [parts])
def block(title): blocks.append((title, [])); return blocks[-1][1]
def P(lst, ref, key, value, pins, unit=1, fp=None, mpn=None, dnp=False):
    lst.append(dict(ref=ref, key=key, value=value, pins={str(k): v for k, v in pins.items()}, unit=unit, fp=fp,
                    mpn=mpn or MPN.get(key, ''), dnp=dnp))

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
def build(out, project, title, comments, paper='A1', perrow=22, revision='3.0', date='2026-10-19'):
    """Write the schematic. paper='auto' sizes a User page to fit."""
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
    pwr_n = 0
    for btitle, parts in blocks:
        sch.texts.append(Text(text=btitle, position=Position(X0, y - 8.89, 0), effects=Effects(font=Font(height=2.0, width=2.0), justify=Justify(horizontally='left')), uuid=S('txt')))
        for i, pt in enumerate(parts):
            if pt['key'] == 'HDR':
                cx = grid(X0 + 20 + (i % perrow) * 60); cy = grid(y + 20)
            else:
                cx = grid(X0 + (i % perrow) * CELLW + 5.08); cy = grid(y + (i // perrow) * CELLH + 10.16)
            lib, name = SYM[pt['key']]
            if (lib, name) not in used: used[(lib, name)] = libsym(pt['key']); sch.libSymbols.append(used[(lib, name)])
            ls = used[(lib, name)]
            fp = pt['fp'] or FP.get(pt['key'], next((p.value for p in ls.properties if p.key == 'Footprint'), ''))
            is_pwr = pt['key'] in ('FLAG',)
            props = [Property(key='Reference', value=pt['ref'], id=0, position=Position(cx + 2.54, cy - 8.89, 0), effects=font()),
                     Property(key='Value', value=pt['value'], id=1, position=Position(cx + 2.54, cy + 8.89, 0), effects=font()),
                     Property(key='Footprint', value=fp, id=2, position=Position(cx, cy, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                     Property(key='Datasheet', value='', id=3, position=Position(cx, cy, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True))]
            if pt['mpn']: props.append(Property(key='MPN', value=pt['mpn'], id=4, position=Position(cx, cy, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)))
            pp = pins_of(ls, pt['unit'])
            ss = SchematicSymbol(libraryNickname=lib, entryName=name, position=Position(cx, cy, 0), unit=pt['unit'],
                                 inBom=(not is_pwr) and ls.inBom is not False, onBoard=not is_pwr, uuid=K('sym', pt['ref'], pt['unit']), properties=props,
                                 pins={n: K('pin', pt['ref'], pt['unit'], n) for n in pp},
                                 instances=[SymbolProjectInstance(name=project, paths=[SymbolProjectPath(sheetInstancePath=root, reference=pt['ref'], unit=pt['unit'])])])
            if pt.get('dnp'): ss.dnp = True
            sch.schematicSymbols.append(ss)
            for pn, net in pt['pins'].items():
                if pn not in pp: raise SystemExit(f"{pt['ref']} unit {pt['unit']} has no pin {pn}")
                px, py = pp[pn]; ax, ay = round(cx + px, 2), round(cy - py, 2)
                if net == 'NC':
                    sch.noConnects.append(NoConnect(position=Position(ax, ay), uuid=K('nc', pt['ref'], pt['unit'], pn)))
                elif net in POWER_SYMBOL_NETS:
                    pwr_n += 1; gs = used.setdefault(('power', net), None)
                    if gs is None: used[('power', net)] = gs = libsym(net); sch.libSymbols.append(gs)
                    sch.schematicSymbols.append(SchematicSymbol(libraryNickname='power', entryName=net, position=Position(ax, ay, PWR_ANG[outward(px, py)]), unit=1,
                        inBom=True, onBoard=True, uuid=K('pwr', pt['ref'], pt['unit'], pn),
                        properties=[Property(key='Reference', value=f'#PWR{pwr_n:03d}', id=0, position=Position(ax, ay + 5, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                                    Property(key='Value', value=net, id=1, position=Position(ax, ay + 4.5, 0), effects=Effects(font=Font(height=1.0, width=1.0), hide=True)),
                                    Property(key='Footprint', value='', id=2, position=Position(ax, ay, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True)),
                                    Property(key='Datasheet', value='', id=3, position=Position(ax, ay, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=True))],
                        pins={'1': K('pwrpin', pt['ref'], pt['unit'], pn)},
                        instances=[SymbolProjectInstance(name=project, paths=[SymbolProjectPath(sheetInstancePath=root, reference=f'#PWR{pwr_n:03d}', unit=1)])]))
                else:
                    ang, just = LBL[outward(px, py)]
                    eff = Effects(font=Font(height=1.0, width=1.0), justify=Justify(horizontally=just, vertically='bottom'))
                    sch.labels.append(LocalLabel(text=net, position=Position(ax, ay, ang), effects=eff, uuid=K('lbl', pt['ref'], pt['unit'], pn)))
        rows = max(1, (len(parts) + perrow - 1) // perrow)
        y += rows * CELLH + (30 if any(p['key'] == 'HDR' for p in parts) else 0) + 16

    if paper == 'auto':
        w = max(420, round(X0 + perrow * CELLW + 40)); h = max(297, round(y + 60))
        sch.paper = PageSettings(paperSize='User', width=w, height=h)
    else:
        sch.paper = PageSettings(paperSize=paper)
    sch.filePath = out
    sch.to_file()
    n = sum(len(p) for _, p in blocks)
    print('parts:', n, 'labels:', len(sch.labels), 'sheet height used (mm):', round(y))

    intended = {}
    for _, parts in blocks:
        for pt in parts:
            for pn, net in pt['pins'].items():
                k = f"{pt['ref']}.{pn}"
                if k in intended and intended[k] != net: raise SystemExit(f'{k} assigned to {intended[k]} and {net}')
                intended[k] = net
    json.dump(intended, open(out.replace('.kicad_sch', '_intended.json'), 'w'), indent=0)
