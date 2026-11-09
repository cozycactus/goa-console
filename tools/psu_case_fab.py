"""PSU case drilling drawings (docs/proposals/psu_case_proposal.md PC1-PC3, signed off 2026-10-26; heatsink on the FRONT end panel, Ruslan,
2026-10-26, because the 1402K's side walls are split by an extrusion). Hammond 1402KV: end panels 249.81 x 93.14 x 1.63
aluminium (front, rear), base 12 ga with 4 rubber feet. Writes psu_case/:
  front.dxf    window for the regulator board's TO-220 edge, 4 x M4 clearance for the heatsink, power LED
  rear.dxf     Schurter DD11 (screw version A), Neutrik NC7FD-LX (D size), M4 earth stud
  heatsink.dxf Fischer SK 47 75 SA base (200 x 75, base 10 thick): 4 x M3 tapped for the TO-220 tabs, 4 x M4 tapped
               to the panel
  base.dxf     regulator board standoffs (4 x M3 at its H1-H4), the shelf posts for the upper LRS-150, earth lug
  holes.csv    every hole of every part; psu_case.pdf / .svg one A3 sheet of the four views
Panel views are from OUTSIDE, origin at the panel's bottom-left corner. The board's frame (psu.kicad_pcb, x right, y
down, TO-220 edge at y 0) faces the front panel, so seen from the front its x runs right to left.
Assumptions marked CHECK below are the ones to confirm on the parts before cutting (or mark the heatsink holes from
the assembled board, as the rails' holes can be).
usage: python3 tools/psu_case_fab.py [out_dir]   (rsvg-convert for the PDF)"""
import csv, os, subprocess, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# Hammond 1402K drawing (rev 05.05.2020)
PANEL_W, PANEL_H = 249.81, 93.14
INNER_W, INNER_D = 230.0, 234.6                    # between the side extrusions; between the end panels (238.13 - 2 x 1.63 - ~0.3)
FLOOR = 0.2                                        # CHECK: base floor above the end panel's bottom edge ((97.66 - 93.14) / 2 - 2.06)
# regulator board (psu.kicad_pcb, 120 x 60): TO-220 pin-2 x (tab hole x); the tab backs stand 1.68 mm proud of the y = 0
# edge (place_psu.py OVERHANG), the edge sits BOARD_EDGE inside the front panel's inner face; M3 holes
BOARD_W, BOARD_D = 120.0, 60.0
TO220 = {'U1': 14.54, 'Q2': 38.54, 'U3': 74.54, 'Q4': 98.54}
BOARD_HOLES = [(4.0, 4.0), (116.0, 4.0), (4.0, 56.0), (116.0, 56.0)]
STANDOFF = 8.0                                     # board bottom above the floor (M3 x 8 standoffs)
BOARD_EDGE, OVERHANG, PANEL_T = 0.3, 1.68, 1.63
BODY_W = 10.0                                      # TO-220 body width
PCB_T = 1.6
SEAT = 2.0                                         # CHECK: TO-220 body seated 2.0 above the board (a spacer jig when soldering)
TAB_HOLE = 12.9                                    # CHECK: TO-220 tab hole centre above the body's seating plane (JEDEC, ~15.8 tall)
TO220_H = 15.8
PAD = 0.25                                         # silicone pad: the tab backs sit this far inside the panel's outer face
# Fischer SK 47 75 SA: 200 wide (profile), 75 long (vertical, fins vertical), base 10 thick, 40 deep
HS_W, HS_H, HS_BASE = 200.0, 75.0, 10.0
HS_Z0 = 3.0                                        # heatsink bottom above the panel's bottom edge
HS_FIX = 8.0                                       # M4 fixings this far in from the heatsink's corners
# rear-panel parts
DD11_CUT, DD11_HOLES = (47.1, 28.1, 1.0), (56.0, 3.4)     # Schurter DD11 screw version A: cut-out w x h, R1; 2 x 3.4 at 56
D_SIZE = (24.0, [(-9.5, 12.0), (9.5, -12.0)], 3.2)        # CHECK: Neutrik D-size, 24 hole + 2 x 3.2 on a 19 x 24 diagonal
STUD = 4.3                                                # M4 earth stud
LED = 5.0                                                 # 3 mm LED in a panel clip: CHECK the clip's hole (5.0-5.2)
# upper LRS-150 shelf: 2 mm aluminium on four M3 posts, 45 above the floor (15 mm over the lower unit, 30 tall)
LRS = (159.0, 97.0, 30.0); LRS_Y0 = BOARD_D + 6.0         # behind the board (y from the front panel's inner face)
SHELF_Z, SHELF_POSTS_IN = 45.0, 6.0

def board_x0():
    """Board's x = 0 seen from the front: the board is centred on the panel, and its x runs right to left."""
    return PANEL_W / 2 + BOARD_W / 2                     # panel x of board x = 0

def front():
    out = []
    z_board = FLOOR + STANDOFF
    z_hole = z_board + PCB_T + SEAT + TAB_HOLE
    x0 = board_x0()
    xs = sorted(x0 - bx for bx in TO220.values())       # around the four TO-220 bodies (they stand proud into it)
    win = (xs[0] - BODY_W / 2 - 1.0, z_board + PCB_T + SEAT - 1.0, xs[-1] + BODY_W / 2 + 1.0, z_board + PCB_T + SEAT + TO220_H + 1.0)
    assert abs(PANEL_T - PAD - (OVERHANG - BOARD_EDGE)) < 1e-6, 'tab backs must meet the heatsink through the pad'
    out.append(('front', 'window', (win[0] + win[2]) / 2, (win[1] + win[3]) / 2, f'{win[2] - win[0]:.1f} x {win[3] - win[1]:.1f}',
                'the four TO-220s (tab backs 1.68 proud of the board edge, through the panel onto the heatsink)', win))
    hx0 = PANEL_W / 2 - HS_W / 2
    for fx, fz in ((HS_FIX, HS_FIX), (HS_W - HS_FIX, HS_FIX), (HS_FIX, HS_H - HS_FIX), (HS_W - HS_FIX, HS_H - HS_FIX)):
        out.append(('front', 'hole', hx0 + fx, HS_Z0 + fz, 'Ø4.3', 'heatsink fixing M4', None))
    out.append(('front', 'hole', (PANEL_W - HS_W) / 4, PANEL_H / 2, f'Ø{LED}', 'power LED (panel clip)', None))
    hs = [('heatsink', 'tapped', (x0 - bx) - hx0, z_hole - HS_Z0, 'M3 x 6', f'{r} tab (shoulder washer, pad)', None) for r, bx in TO220.items()]
    hs += [('heatsink', 'tapped', fx, fz, 'M4 x 8', 'panel fixing', None) for fx, fz in
           ((HS_FIX, HS_FIX), (HS_W - HS_FIX, HS_FIX), (HS_FIX, HS_H - HS_FIX), (HS_W - HS_FIX, HS_H - HS_FIX))]
    # the fixings must clear the window; the tab holes must sit inside it
    for _, _, x, z, *_ in out[1:5]:
        assert not (win[0] - 4 < x < win[2] + 4 and win[1] - 4 < z < win[3] + 4), 'heatsink fixing in the window'
    for _, _, x, z, *_ in hs[:4]:
        assert win[0] < x + hx0 < win[2] and win[1] < z + HS_Z0 < win[3]
    return out, hs, win

def rear():
    zc = PANEL_H / 2
    out = [('rear', 'cutout', 45.0, zc, f'{DD11_CUT[0]} x {DD11_CUT[1]} R{DD11_CUT[2]:g}', 'Schurter DD11 (inlet, 2-pole switch, fuse)', None)]
    out += [('rear', 'hole', 45.0 + s * DD11_HOLES[0] / 2, zc, f'Ø{DD11_HOLES[1]}', 'DD11 screw', None) for s in (-1, 1)]
    nx = PANEL_W / 2 + 25.0
    out.append(('rear', 'hole', nx, zc, f'Ø{D_SIZE[0]:g}', 'Neutrik NC7FD-LX (console output)', None))
    out += [('rear', 'hole', nx + u, zc + v, f'Ø{D_SIZE[2]}', 'NC7FD-LX screw', None) for u, v in D_SIZE[1]]
    out.append(('rear', 'hole', PANEL_W - 25.0, zc, f'Ø{STUD}', 'M4 earth stud (star washers both sides)', None))
    return out

def base():
    """Base view from inside, origin at the front-left inner corner (x as seen from above, y back from the front panel)."""
    out = []
    # seen from above with the front panel at y 0, the board's x = 0 is on the right (its x runs right to left)
    for hx, hy in BOARD_HOLES:
        out.append(('base', 'hole', INNER_W / 2 + BOARD_W / 2 - hx, BOARD_EDGE + hy, 'Ø3.2', 'board standoff M3 x 8 (H1-H4)', None))
    lx0 = INNER_W / 2 - LRS[0] / 2
    for px in (lx0 + SHELF_POSTS_IN, lx0 + LRS[0] - SHELF_POSTS_IN):
        for py in (LRS_Y0 - 4.0, LRS_Y0 + LRS[1] + 4.0):
            out.append(('base', 'hole', px, py, 'Ø3.2', f'shelf post M3 x {SHELF_Z:g}', None))
    out.append(('base', 'hole', INNER_W - 15.0, INNER_D - 30.0, 'Ø4.3', 'base-to-earth bond (M4, lug to the stud)', None))
    return out, (lx0, LRS_Y0, lx0 + LRS[0], LRS_Y0 + LRS[1])

def write_dxf(path, outline, items, extra=()):
    o = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '4', '0', 'ENDSEC', '0', 'SECTION', '2', 'ENTITIES']
    def line(a, b, c, d, layer='OUTLINE'):
        o.extend(['0', 'LINE', '8', layer, '10', f'{a:.3f}', '20', f'{b:.3f}', '11', f'{c:.3f}', '21', f'{d:.3f}'])
    def rect(x0, y0, x1, y1, layer):
        line(x0, y0, x1, y0, layer); line(x1, y0, x1, y1, layer); line(x1, y1, x0, y1, layer); line(x0, y1, x0, y0, layer)
    rect(0, 0, *outline, 'OUTLINE')
    for part, kind, x, y, size, what, box in items:
        if kind in ('hole', 'tapped'):
            d = float(size.split()[0].lstrip('ØM')) if kind == 'hole' else {'M3': 2.5, 'M4': 3.3}[size.split()[0]]
            o.extend(['0', 'CIRCLE', '8', 'CUT' if kind == 'hole' else 'TAP', '10', f'{x:.3f}', '20', f'{y:.3f}', '40', f'{d / 2:.3f}'])
        elif kind == 'window':
            rect(*box, 'CUT')
        elif kind == 'cutout':
            w, h = DD11_CUT[0], DD11_CUT[1]; rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 'CUT')
    for x0, y0, x1, y1 in extra: rect(x0, y0, x1, y1, 'REF')
    o += ['0', 'ENDSEC', '0', 'EOF']
    open(path, 'w').write('\n'.join(o) + '\n')

def write_svg(path, views):
    """A3 sheet: each view (title, outline w h, items, refs, scale) two per row; its hole list under it, or beside it."""
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" font-family="Arial Narrow, Arial">',
                      '<rect width="420" height="297" fill="white"/>', '<text x="12" y="12" font-size="5" font-weight="bold">goa console PSU: Hammond 1402KV case and Fischer SK 47 75 SA heatsink, drilling</text>']
    pos = [(12, 22), (215, 22), (12, 120), (215, 120)]
    for (title, (w, h), items, refs, k, beside), (ox, oy) in zip(views, pos):
        Y = lambda y: oy + 6 + (h - y) * k                     # y up on the sheet
        o.append(f'<text x="{ox}" y="{oy + 3}" font-size="3.5" font-weight="bold">{title}</text>')
        o.append(f'<rect x="{ox}" y="{Y(h)}" width="{w * k:.2f}" height="{h * k:.2f}" fill="none" stroke="black" stroke-width="0.3"/>')
        for x0, y0, x1, y1 in refs:
            o.append(f'<rect x="{ox + x0 * k:.2f}" y="{Y(y1):.2f}" width="{(x1 - x0) * k:.2f}" height="{(y1 - y0) * k:.2f}" fill="none" stroke="#888" stroke-dasharray="1.5 1" stroke-width="0.2"/>')
        for part, kind, x, y, size, what, box in items:
            if kind == 'window':
                o.append(f'<rect x="{ox + box[0] * k:.2f}" y="{Y(box[3]):.2f}" width="{(box[2] - box[0]) * k:.2f}" height="{(box[3] - box[1]) * k:.2f}" fill="none" stroke="red" stroke-width="0.3"/>')
            elif kind == 'cutout':
                w_, h_ = DD11_CUT[0], DD11_CUT[1]
                o.append(f'<rect x="{ox + (x - w_ / 2) * k:.2f}" y="{Y(y + h_ / 2):.2f}" width="{w_ * k:.2f}" height="{h_ * k:.2f}" rx="0.7" fill="none" stroke="red" stroke-width="0.3"/>')
            else:
                d = float(size.split()[0].lstrip('ØM')) if kind == 'hole' else {'M3': 2.5, 'M4': 3.3}[size.split()[0]]
                o.append(f'<circle cx="{ox + x * k:.2f}" cy="{Y(y):.2f}" r="{max(d / 2 * k, 0.6):.2f}" fill="none" stroke="{"red" if kind == "hole" else "blue"}" stroke-width="0.3"/>')
        tx, ty = (ox + w * k + 4, Y(h) + 3) if beside else (ox, Y(0) + 5)
        for part, kind, x, y, size, what, box in items:
            o.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="2.4">{size}  at ({x:.2f}, {y:.2f})  {what}</text>'); ty += 3.0
    o.append('<text x="12" y="290" font-size="2.6">Panels and heatsink seen from the front / rear outside, origin bottom-left; base from above, origin front-left inner corner. Red: through, blue: tapped. CHECK before cutting: panel-to-floor offset, TO-220 seating height (2.0 spacer), Neutrik D-size pattern; or mark the heatsink holes from the assembled board.</text></svg>')
    open(path, 'w').write('\n'.join(o) + '\n')

def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'psu_case')); os.makedirs(out, exist_ok=True)
    fr, hs, win = front(); re_ = rear(); ba, lrs = base()
    write_dxf(os.path.join(out, 'front.dxf'), (PANEL_W, PANEL_H), fr, [(PANEL_W / 2 - HS_W / 2, HS_Z0, PANEL_W / 2 + HS_W / 2, HS_Z0 + HS_H)])
    write_dxf(os.path.join(out, 'rear.dxf'), (PANEL_W, PANEL_H), re_)
    write_dxf(os.path.join(out, 'heatsink.dxf'), (HS_W, HS_H), hs)
    write_dxf(os.path.join(out, 'base.dxf'), (INNER_W, INNER_D), ba, [lrs, (INNER_W / 2 - BOARD_W / 2, 0, INNER_W / 2 + BOARD_W / 2, BOARD_D)])
    with open(os.path.join(out, 'holes.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['part', 'kind', 'x mm', 'y / z mm', 'size', 'what'])
        for part, kind, x, y, size, what, box in fr + re_ + hs + ba: w.writerow([part, kind, f'{x:.2f}', f'{y:.2f}', size, what])
    write_svg(os.path.join(out, 'psu_case.svg'), [
        ('FRONT end panel (from outside; heatsink outline dashed)', (PANEL_W, PANEL_H), fr, [(PANEL_W / 2 - HS_W / 2, HS_Z0, PANEL_W / 2 + HS_W / 2, HS_Z0 + HS_H)], 1 / 1.5, False),
        ('REAR end panel (from outside)', (PANEL_W, PANEL_H), re_, [], 1 / 1.5, False),
        ('HEATSINK SK 47 75 SA base, seen from the front as the panel (origin its bottom-left)', (HS_W, HS_H), hs, [], 1 / 1.5, False),
        ('BASE (from above, front panel at y 0; board and LRS-150 stack dashed)', (INNER_W, INNER_D), ba, [lrs, (INNER_W / 2 - BOARD_W / 2, 0, INNER_W / 2 + BOARD_W / 2, BOARD_D)], 1 / 2.6, True)])
    rsvg = subprocess.run(['which', 'rsvg-convert'], capture_output=True, text=True).stdout.strip()
    if rsvg: subprocess.run([rsvg, '-f', 'pdf', '-o', os.path.join(out, 'psu_case.pdf'), os.path.join(out, 'psu_case.svg')], check=True)
    # fit: board, LRS stack and rear connectors along the depth; the stack's height
    rear_depth = 33.1                                    # DD11 behind the panel (the deepest rear part)
    assert LRS_Y0 + LRS[1] + 10 < INNER_D - rear_depth, 'LRS stack runs into the rear connectors'
    assert SHELF_Z + 2.0 + LRS[2] < PANEL_H - FLOOR - 10, 'upper LRS-150 too close to the cover'
    print(f'window {win[2] - win[0]:.1f} x {win[3] - win[1]:.1f} at z {win[1]:.1f}-{win[3]:.1f}; TO-220 holes z {hs[0][3] + HS_Z0:.1f} on the panel; '
          f'depth used {LRS_Y0 + LRS[1]:.0f} + rear {rear_depth} of {INNER_D}; upper LRS top {SHELF_Z + 2 + LRS[2]:.0f} of {PANEL_H - FLOOR:.0f}')

if __name__ == '__main__':
    main()
