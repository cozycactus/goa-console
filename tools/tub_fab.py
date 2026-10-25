"""Tub drawings (tub_proposal.md TB1-TB4, signed off 2026-10-26) from the shared geometry in tools/panel_layout.py (the
panels, the rails and the 3D model use the same numbers). Writes tub/:
  cheek.dxf     the LEFT cheek's outside face (the right one is its mirror): profile over the desk, rail rebates
                10 x 50 x 2 deep and the floor dado 6 deep (on the inside face), screw holes (counterbored outside)
  floor.dxf     12 mm ply floor with its inlet slots
  armrest.dxf, rear_wall.dxf, cap.dxf   the arm-rest section, the plenum's rear wall (NC7MD-LX cut-out), its cap strip
  cutlist.csv   every part; tub.pdf / .svg an A3 sheet of the parts
Cheek coordinates: X from the cheek's back edge forwards, Y up from the desk. Other parts: x along the console from the
part's left end, y across it.
usage: python3 tools/tub_fab.py [out_dir]   (rsvg-convert for the PDF)"""
import csv, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel_layout as L

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SCREW, CBORE = 4.5, (8.0, 4.0)                 # M4 / 4 mm wood screw clearance; counterbore on the outside face
NC7 = (24.0, [(-9.5, 12.0), (9.5, -12.0)], 3.2)   # Neutrik D size (as the PSU case's NC7FD-LX)

def geometry():
    w = L.console_width(); inner = w + 2 * L.CHEEK_GAP
    out = L.cheek_outline(); yb = out[0][0]
    X = lambda p: (yb - p[0], p[1])                       # desk elevation -> cheek drawing (back edge at X = 0)
    rect = lambda y0, y1, z0, z1: [X(L.to_desk(y, z)) for y, z in ((y0, z0), (y1, z0), (y1, z1), (y0, z1))]
    pt = lambda y, z: X(L.to_desk(y, z))
    ch = dict(outline=[X(p) for p in out], rebates=[], holes=[], dado=None)
    for yc in L.RAIL_LINES:
        ch['rebates'].append(rect(yc - L.RAIL_W / 2, yc + L.RAIL_W / 2, L.PANEL_Z0 - L.RAIL_H, L.PANEL_Z0))
        ch['holes'] += [(pt(yc, L.PANEL_Z0 - z), 'rail end M4 (2 x per rail)') for z in (L.RAIL_H / 4, 3 * L.RAIL_H / 4)]
    ch['dado'] = rect(L.FLOOR_Y[0], L.FLOOR_Y[1], L.FLOOR_TOP - L.FLOOR_T, L.FLOOR_TOP)
    za, zt = L.FLOOR_TOP - L.FLOOR_T, L.ARM_TOP
    ch['holes'] += [(pt(sum(L.ARM_Y) / 2, za + f * (zt - za)), 'arm-rest screw') for f in (0.3, 0.7)]
    ch['holes'] += [(pt(sum(L.PLENUM_WALL_Y) / 2, za + f * (L.PLENUM_CAP_Z - za)), 'rear-wall screw') for f in (0.3, 0.7)]
    ch['holes'].append((pt(sum(L.PLENUM_CAP_Y) / 2, L.PLENUM_CAP_Z + L.PLENUM_CAP_T / 2), 'cap screw'))
    parts = dict(
        floor=dict(size=(inner + 2 * L.DADO, L.FLOOR_Y[1] - L.FLOOR_Y[0]), t=L.FLOOR_T, qty=1, mat='birch ply 12',
                   slots=[(a + L.CHEEK_GAP + L.DADO, b + L.CHEEK_GAP + L.DADO, y - L.FLOOR_Y[0]) for a, b, y in L.inlet_slots()]),
        armrest=dict(size=(inner, L.ARM_Y[1] - L.ARM_Y[0]), h=zt - za, qty=1, mat='walnut'),
        rear_wall=dict(size=(inner, L.PLENUM_CAP_Z - za), t=L.PLENUM_WALL_Y[1] - L.PLENUM_WALL_Y[0], qty=1, mat='walnut 12',
                       nc7=(L.NC7_X + L.CHEEK_GAP, (L.PLENUM_CAP_Z - za) / 2)),
        cap=dict(size=(inner, L.PLENUM_CAP_Y[1] - L.PLENUM_CAP_Y[0]), t=L.PLENUM_CAP_T, qty=1, mat='walnut 10'))
    return ch, parts

def inside(poly, p):
    x, y = p; n = len(poly); c = False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def check(ch, parts):
    bad = []
    for poly in ch['rebates'] + [ch['dado']]:
        bad += [f'feature corner {c} outside the cheek' for c in poly if not inside(ch['outline'], (c[0] + 0.01 * (1 if c[0] < 300 else -1), c[1] + 0.01))]
    for (x, y), what in ch['holes']:
        if not inside(ch['outline'], (x, y)): bad.append(f'{what} hole at ({x:.1f}, {y:.1f}) outside the cheek')
    nx, nz = parts['rear_wall']['nc7']
    if not (NC7[0] / 2 + 3 < nz < parts['rear_wall']['size'][1] - NC7[0] / 2 - 3): bad.append('NC7 cut-out off the rear wall')
    # the floor clears the rails and the parts below the boards; the cable slot is a real vent slot
    if L.PANEL_Z0 - L.RAIL_H - L.FLOOR_TOP < 5: bad.append('rail bottom too close to the floor')
    channel = L.RAIL_LINES[0] - L.RAIL_W / 2 - L.PLENUM_CAP_Y[1]
    if channel * (L.console_width() + 2 * L.CHEEK_GAP) / 1e6 < 0.024: bad.append(f'plenum outlet {channel:.1f} mm too narrow')
    return bad

def write_dxf(path, polys, circles, texts=()):
    o = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '4', '0', 'ENDSEC', '0', 'SECTION', '2', 'ENTITIES']
    for layer, pts in polys:
        o += ['0', 'POLYLINE', '8', layer, '66', '1', '70', '1']
        for x, y in pts: o += ['0', 'VERTEX', '8', layer, '10', f'{x:.3f}', '20', f'{y:.3f}']
        o += ['0', 'SEQEND', '8', layer]
    for layer, (x, y), d in circles: o += ['0', 'CIRCLE', '8', layer, '10', f'{x:.3f}', '20', f'{y:.3f}', '40', f'{d / 2:.3f}']
    for (x, y), s, h in texts: o += ['0', 'TEXT', '8', 'TEXT', '10', f'{x:.3f}', '20', f'{y:.3f}', '40', f'{h}', '1', s]
    o += ['0', 'ENDSEC', '0', 'EOF']
    open(path, 'w').write('\n'.join(o) + '\n')

def box(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'tub')); os.makedirs(out, exist_ok=True)
    ch, parts = geometry()
    bad = check(ch, parts)
    write_dxf(os.path.join(out, 'cheek.dxf'), [('OUTLINE', ch['outline'])] + [('REBATE_2DEEP_INSIDE', r) for r in ch['rebates']]
              + [('DADO_6DEEP_INSIDE', ch['dado'])], [('HOLES', p, SCREW) for p, _ in ch['holes']] + [('CBORE_OUTSIDE', p, CBORE[0]) for p, _ in ch['holes']],
              [((5, -12), 'LEFT CHEEK, outside face (right cheek: mirror). Walnut 20. Rebates and dado on the inside face.', 4)])
    f = parts['floor']; fx, fy = f['size']
    write_dxf(os.path.join(out, 'floor.dxf'), [('OUTLINE', box(0, 0, fx, fy))] + [('SLOTS', box(a, y - L.INLET_W / 2, b, y + L.INLET_W / 2)) for a, b, y in f['slots']],
              [], [((0, -10), f'FLOOR, birch ply 12, {fx:.1f} x {fy:.1f}; y from its back edge; {len(f["slots"])} inlet slots {L.INLET_L:g} x {L.INLET_W:g} (mesh underneath)', 4)])
    a = parts['armrest']; write_dxf(os.path.join(out, 'armrest.dxf'), [('OUTLINE', box(0, 0, a['size'][1], a['h']))], [],
                                    [((0, -8), f'ARM-REST section {a["size"][1]:g} x {a["h"]:g}, length {a["size"][0]:.1f}, walnut; front top edge rounded R10', 3)])
    r = parts['rear_wall']; rx, ry = r['size']; nx, nz = r['nc7']
    write_dxf(os.path.join(out, 'rear_wall.dxf'), [('OUTLINE', box(0, 0, rx, ry))],
              [('HOLES', (nx, nz), NC7[0])] + [('HOLES', (nx + u, nz + v), NC7[2]) for u, v in NC7[1]],
              [((0, -8), f'PLENUM REAR WALL (the console\'s rear panel), walnut 12, {rx:.1f} x {ry:.1f}, seen from the back; NC7MD-LX at x {nx:.1f}', 3)])
    c = parts['cap']; write_dxf(os.path.join(out, 'cap.dxf'), [('OUTLINE', box(0, 0, c['size'][0], c['size'][1]))], [],
                                [((0, -8), f'PLENUM CAP STRIP, walnut 10, {c["size"][0]:.1f} x {c["size"][1]:g}; the channel in front of it is the open outlet', 3)])
    with open(os.path.join(out, 'cutlist.csv'), 'w', newline='') as fh:
        wr = csv.writer(fh); wr.writerow(['part', 'qty', 'material', 'length mm', 'width mm', 'thickness mm', 'notes'])
        ox = [p[0] for p in ch['outline']]; oy = [p[1] for p in ch['outline']]
        wr.writerow(['cheek', 2, 'walnut', f'{max(ox) - min(ox):.0f}', f'{max(oy):.0f}', 20, 'left and right (mirror); cheek.dxf'])
        wr.writerow(['floor', 1, 'birch ply', f'{fx:.1f}', f'{fy:.1f}', 12, 'in 6 mm dados; inlet slots + mesh'])
        wr.writerow(['arm-rest', 1, 'walnut', f'{a["size"][0]:.1f}', f'{a["size"][1]:g}', f'{a["h"]:g}', 'between the cheeks'])
        wr.writerow(['plenum rear wall', 1, 'walnut', f'{rx:.1f}', f'{ry:.1f}', 12, 'NC7MD-LX cut-out'])
        wr.writerow(['plenum cap strip', 1, 'walnut', f'{c["size"][0]:.1f}', f'{c["size"][1]:g}', 10, 'on the rear wall'])
        wr.writerow(['frame rails', 2, 'aluminium', '1227.2', 10, 50, 'frame/ (front plain, back slotted)'])
        wr.writerow(['felt pads', 6, '', '', '', '', 'under the cheek bottoms'])
    # A3 sheet: the cheek at 1:2.5, the other parts as labelled boxes with their features
    k = 1 / 2.5; ox, oy = 20, 150
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" font-family="Arial Narrow, Arial">',
         '<rect width="420" height="297" fill="white"/><text x="20" y="14" font-size="5" font-weight="bold">goa console: tub (tub_proposal.md TB1-TB4)</text>']
    P = lambda pts, st: '<polygon points="' + ' '.join(f'{ox + x * k:.2f},{oy - y * k:.2f}' for x, y in pts) + f'" style="{st}"/>'
    s.append(P(ch['outline'], 'fill:#f3e7d6;stroke:#000;stroke-width:.3'))
    for rb in ch['rebates']: s.append(P(rb, 'fill:#ccd;stroke:#225;stroke-width:.25'))
    s.append(P(ch['dado'], 'fill:#e8d39a;stroke:#875;stroke-width:.25'))
    for (x, y), _ in ch['holes']: s.append(f'<circle cx="{ox + x * k:.2f}" cy="{oy - y * k:.2f}" r="{SCREW / 2 * k + .3:.2f}" fill="none" stroke="red" stroke-width=".25"/>')
    s.append(f'<text x="{ox}" y="{oy + 8}" font-size="3.2">Left cheek, outside face, 1:2.5 (right: mirror). Blue: rail rebates 10 x 50 x 2 deep, inside face. Tan: floor dado 6 deep, inside. Red: Ø{SCREW:g} through, Ø{CBORE[0]:g} x {CBORE[1]:g} counterbore outside.</text>')
    y = 176
    for name, desc in (('Floor', f'birch ply 12, {fx:.1f} x {fy:.1f}: {len(f["slots"])} inlet slots {L.INLET_L:g} x {L.INLET_W:g} in 3 rows at {", ".join(f"{r - L.FLOOR_Y[0]:g}" for r in L.INLET_ROWS)} from its back edge, mesh underneath'),
                       ('Arm-rest', f'walnut {a["size"][1]:g} x {a["h"]:g}, length {a["size"][0]:.1f}, between the cheeks, front top edge R10'),
                       ('Plenum rear wall', f'walnut 12, {rx:.1f} x {ry:.1f}: NC7MD-LX (Ø24 + 2 x Ø3.2) at x {nx:.1f}, mid-height; the console\'s rear panel'),
                       ('Plenum cap strip', f'walnut 10 x {c["size"][1]:g}, length {c["size"][0]:.1f}, on the rear wall; the 21 mm channel in front of it is the open outlet (0.026 m2)'),
                       ('Under the floor', 'open front and back between the cheeks (no base panel): the inlet air comes in there; felt pads under the cheeks'),
                       ('Supply cable', f'from the NC7MD-LX through back-rail vent slot {L.CABLE_SLOT} (30 x 25) and along the floor to the master\'s J1')):
        s.append(f'<text x="20" y="{y}" font-size="3.4"><tspan font-weight="bold">{name}: </tspan>{desc}</text>'); y += 7
    s.append('<text x="20" y="288" font-size="2.8">Dimensions in mm, from the 3D model\'s geometry (tools/panel_layout.py). Joints: dowels / screws and glue, from outside through the cheeks.</text></svg>')
    open(os.path.join(out, 'tub.svg'), 'w').write('\n'.join(s) + '\n')
    rsvg = subprocess.run(['which', 'rsvg-convert'], capture_output=True, text=True).stdout.strip()
    if rsvg: subprocess.run([rsvg, '-f', 'pdf', '-o', os.path.join(out, 'tub.pdf'), os.path.join(out, 'tub.svg')], check=True)
    print(f'cheek {max(p[0] for p in ch["outline"]):.0f} x {max(p[1] for p in ch["outline"]):.0f} mm, {len(ch["holes"])} holes; floor {fx:.1f} x {fy:.1f}, '
          f'{len(f["slots"])} slots; {len(bad)} problems')
    for b in bad: print('   ', b)
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
