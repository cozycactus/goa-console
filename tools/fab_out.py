"""Fab outputs for one board, after routing: checks first, then the files a fab (JLCPCB) takes. Plain Python 3:
  python3 tools/fab_out.py BOARD [--allow-unrouted] [--force]      (BOARD = channel_strip, jack_board, group, ...)
Writes fab/BOARD/ (gitignored):
  gerber/            copper (F.Cu, In1.Cu, In2.Cu on the 4-layer boards, B.Cu), paste, silk, mask, Edge.Cuts; zones
                     refilled first; Protel extensions
  drill/             Excellon, mm, PTH and NPTH in separate files, with a PDF drill map
  BOARD_gerbers.zip  gerber/ + drill/, the file to upload
  BOARD_pos.csv      KiCad's position file (mm, both sides, DNP left out); BOARD_cpl.csv the same in JLCPCB's CPL
                     columns (Designator, Mid X, Mid Y, Layer, Rotation)
  BOARD_bom.csv      the board's BOM from its schematic (Qty, Value, Footprint, MPN, DNP, References)
  BOARD_drc.json     the DRC report it checked
Refuses (exit 1) when DRC has a violation, a schematic-parity issue or an unrouted connection, or tools/route_check.py
has an ERR. Known footprint-internal DRC items are accepted by name (KNOWN). --allow-unrouted accepts unrouted
connections (to try the outputs on a placed board); --force writes the files anyway and says what it overrode."""
import csv, json, os, re, shutil, subprocess, sys, zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
KC = os.environ.get('KC', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
KPY = os.environ.get('KPY', '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3')
# DRC items that belong to a footprint as designed, not to the layout: (violation type, regex for the footprint refs)
KNOWN = {
    'jack_board': [('hole_clearance', r'^J\d+$'), ('solder_mask_bridge', r'^J\d+$')],       # KiCad's NJ6FD-V footprint
    'group_jack_board': [('hole_clearance', r'^J\d+$'), ('solder_mask_bridge', r'^J\d+$')],
    'master_jack_board': [('hole_clearance', r'^J\d+$'), ('solder_mask_bridge', r'^J\d+$')],
    'psu': [('silk_edge_clearance', r'^(U1|U3|Q2|Q4)$')],  # the TO-220s overhang the edge onto the heatsink (PC1)
}

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode not in (0, 5) and '--exit-code-violations' not in cmd:   # kicad-cli: 5 = DRC found violations
        sys.exit(f'failed: {" ".join(cmd)}\n{r.stdout}\n{r.stderr}')
    return r

def refs_of(item):
    return re.findall(r'\bof ([A-Z]+\d+)\b', item.get('description', ''))

def is_known(name, v):
    """Every item names ONE footprint the board's KNOWN rule covers (an item between two footprints is the layout's,
    whatever they are; the board outline may be the other item of an edge clearance); a track, via or zone in it makes
    it the layout's."""
    rx = [r for t, r in KNOWN.get(name, []) if t == v.get('type')]
    items = v.get('items', [])
    refs = {r for it in items for r in refs_of(it)}
    if not rx or len(refs) != 1: return False
    if any(not refs_of(it) and not it.get('description', '').endswith('on Edge.Cuts') for it in items): return False
    return all(any(re.match(x, r) for x in rx) for r in refs)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    allow_unrouted, force = '--allow-unrouted' in sys.argv, '--force' in sys.argv
    if len(args) != 1: sys.exit(__doc__)
    name = args[0]; pcb, sch = os.path.join(ROOT, 'boards', name, name + '.kicad_pcb'), os.path.join(ROOT, 'boards', name, name + '.kicad_sch')
    out = os.path.join(ROOT, 'fab', name)
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'gerber')); os.makedirs(os.path.join(out, 'drill'))
    problems = []
    # 1. DRC, zones refilled in its own copy (the board file is not saved)
    rpt = os.path.join(out, name + '_drc.json')
    run([KC, 'pcb', 'drc', '--format', 'json', '--schematic-parity', '--severity-all', '--refill-zones', '-o', rpt, pcb])
    d = json.load(open(rpt))
    viol = d.get('violations', [])
    known = [v for v in viol if is_known(name, v)]
    other = [v for v in viol if v not in known]
    unrouted, parity = d.get('unconnected_items', []), d.get('schematic_parity', [])
    print(f'{name}: DRC {len(viol)} violations ({len(known)} known footprint items), {len(parity)} parity issues, '
          f'{len(unrouted)} unrouted connections')
    for v in other[:10]: print(f'  {v.get("type")}: {v.get("description")} — {"; ".join(i.get("description", "") for i in v.get("items", []))}')
    if other: problems.append(f'{len(other)} DRC violations')
    if parity: problems.append(f'{len(parity)} schematic-parity issues')
    if unrouted and not allow_unrouted: problems.append(f'{len(unrouted)} unrouted connections')
    # 2. what DRC can't see
    rc = run([KPY, os.path.join(TOOLS, 'route_check.py'), pcb])
    tail = [l for l in rc.stdout.splitlines() if re.match(r'\s+\d+ ERR, \d+ WARN', l)]
    print('  route_check:', tail[-1].strip() if tail else 'no result')
    if not tail: problems.append('route_check gave no result')
    elif not tail[-1].strip().startswith('0 ERR'): problems.append('route_check ERR')
    if problems and not force:
        sys.exit(f'{name}: not written ({"; ".join(problems)}); fix them, or --force')
    # 3. Gerbers, drill, zip
    import_layers = ['F.Cu', 'B.Cu', 'F.Paste', 'B.Paste', 'F.Silkscreen', 'B.Silkscreen', 'F.Mask', 'B.Mask', 'Edge.Cuts']
    if re.search(r'\(\d+ "In1\.Cu"', open(pcb).read()): import_layers[1:1] = ['In1.Cu', 'In2.Cu']   # any layer numbering
    run([KC, 'pcb', 'export', 'gerbers', '--check-zones', '-l', ','.join(import_layers), '-o', os.path.join(out, 'gerber') + '/', pcb])
    run([KC, 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-units', 'mm', '--excellon-separate-th',
         '--generate-map', '--map-format', 'pdf', '-o', os.path.join(out, 'drill') + '/', pcb])
    zp = os.path.join(out, name + '_gerbers.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for sub in ('gerber', 'drill'):
            for f in sorted(os.listdir(os.path.join(out, sub))): z.write(os.path.join(out, sub, f), f)
    # 4. position file and JLCPCB CPL
    pos = os.path.join(out, name + '_pos.csv')
    run([KC, 'pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp', '-o', pos, pcb])
    rows = list(csv.DictReader(open(pos)))
    with open(os.path.join(out, name + '_cpl.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for r in rows: w.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
    # 5. BOM from the schematic
    if os.path.exists(sch):
        run([KC, 'sch', 'export', 'bom', '-o', os.path.join(out, name + '_bom.csv'),
             '--fields', '${QUANTITY},Value,Footprint,MPN,${DNP},Reference', '--labels', 'Qty,Value,Footprint,MPN,DNP,References',
             '--group-by', 'Value,Footprint,MPN,${DNP}', '--ref-delimiter', ' ', '--ref-range-delimiter', '', sch])
    files = sorted(os.listdir(os.path.join(out, 'gerber'))) + sorted(os.listdir(os.path.join(out, 'drill')))
    print(f'  wrote fab/{name}/: {len(os.listdir(os.path.join(out, "gerber")))} Gerbers, '
          f'{len(os.listdir(os.path.join(out, "drill")))} drill files, {name}_gerbers.zip, pos / cpl ({len(rows)} parts), bom'
          + (f'  (FORCED past: {"; ".join(problems)})' if problems else ''))
    return files

if __name__ == '__main__':
    main()
