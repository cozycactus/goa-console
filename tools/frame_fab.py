"""Frame rail drawing (frame_proposal.md FR1-FR3): one part, two off, from the module order and the panel screw pattern in
tools/panel_layout.py (the panels and the 3D model use the same numbers).
  frame/rail.dxf        R12 DXF, mm: top view (the panel face, M3 holes), front view (side face, bonding hole), both end
                        views (M4 holes); layers OUTLINE, HOLES (tap-drill circles), CENTER, TEXT
  frame/rail_holes.csv  every hole: face, x from the left end, y / z, thread, tap drill, depth
  frame/rail.pdf / .svg the drawing on A3, scaled, with the hole table
Rail frame: x from the left end along the rail, y across the 10 mm top face (0 at the back edge), z down from the top face.
usage: python3 tools/frame_fab.py [out_dir]   (rsvg-convert for the PDF)"""
import csv, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel_layout as L

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
M3 = ('M3', 2.5, 6.0, 8.0)            # thread, tap drill, thread depth, drill depth
M4_SIDE = ('M4', 3.3, 'through', 'through')   # across the 10 mm thickness
M4_END = ('M4', 3.3, 10.0, 12.0)
MATERIAL = '6060-T6 or 6082 aluminium flat bar 50 x 10, mill finish (or clear anodised, holes tapped after)'

def holes():
    """[(face, x, a, (thread, drill, depth, drill depth), what)]: a = y on the top face, z (down) on the side / ends."""
    r0, r1 = L.rail_span(); ln = r1 - r0; w, h = L.RAIL_W, L.RAIL_H
    out = [('top', x - r0, w / 2, M3, 'panel screw') for x in L.rail_holes()]
    out += [(end, 0.0 if end == 'left end' else ln, z, M4_END, 'cheek fixing') for end in ('left end', 'right end') for z in (h / 4, 3 * h / 4)]
    out.append(('outer side', ln / 2, h / 2, M4_SIDE, 'bond to the M4 star (2.5 mm2, ring lug)'))
    return ln, out

def dxf(path, ln, hl):
    w, h = L.RAIL_W, L.RAIL_H
    views = {'top': (0.0, 0.0), 'side': (0.0, -30.0 - h), 'left end': (-40.0, -30.0 - h), 'right end': (ln + 30.0, -30.0 - h)}
    o = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '4', '0', 'ENDSEC', '0', 'SECTION', '2', 'TABLES',
         '0', 'TABLE', '2', 'LAYER', '70', '4']
    for n, col in (('OUTLINE', 7), ('HOLES', 1), ('CENTER', 3), ('TEXT', 2)):
        o += ['0', 'LAYER', '2', n, '70', '0', '62', str(col), '6', 'CONTINUOUS']
    o += ['0', 'ENDTAB', '0', 'ENDSEC', '0', 'SECTION', '2', 'ENTITIES']
    def rect(layer, x0, y0, x1, y1):
        for (a, b), (c, d) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            o.extend(['0', 'LINE', '8', layer, '10', f'{a:.3f}', '20', f'{b:.3f}', '11', f'{c:.3f}', '21', f'{d:.3f}'])
    def text(s, x, y, size=3.0):
        o.extend(['0', 'TEXT', '8', 'TEXT', '10', f'{x:.3f}', '20', f'{y:.3f}', '40', f'{size}', '1', s])
    def circle(x, y, r):
        o.extend(['0', 'CIRCLE', '8', 'HOLES', '10', f'{x:.3f}', '20', f'{y:.3f}', '40', f'{r:.3f}'])
    tx, ty = views['top']; rect('OUTLINE', tx, ty, tx + ln, ty + w); text('TOP (panel face), M3 x 6 deep', tx, ty + w + 4)
    sx, sy = views['side']; rect('OUTLINE', sx, sy, sx + ln, sy + h); text('SIDE (outer face): bonding M4 through', sx, sy + h + 4)
    for end in ('left end', 'right end'):
        ex, ey = views[end]; rect('OUTLINE', ex, ey, ex + w, ey + h); text(end.upper() + ': 2 x M4 x 10', ex - 5, ey + h + 4, 2.5)
    for face, x, a, (th, dr, dp, dd), what in hl:
        if face == 'top': circle(tx + x, ty + w - a, dr / 2)
        elif face == 'outer side': circle(sx + x, sy + h - a, dr / 2)
        else:
            ex, ey = views[face]; circle(ex + w / 2, ey + h - a, dr / 2)
    text(f'RAIL, 2 OFF. {MATERIAL}. Length {ln:.1f}. Hole positions +-0.15. goa-console frame_proposal.md', 0, -h - 70, 3.5)
    o += ['0', 'ENDSEC', '0', 'EOF']
    open(path, 'w').write('\n'.join(o) + '\n')

def svg(path, ln, hl):
    """A3 landscape (420 x 297), rail views at 1:3.5, hole table below."""
    k = 1 / 3.5; w, h = L.RAIL_W, L.RAIL_H; X0 = 20.0
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" '
         'font-family="Arial Narrow, Arial, sans-serif">', '<rect width="420" height="297" fill="white"/>',
         '<g fill="none" stroke="black" stroke-width="0.25">']
    ty, sy = 30.0, 60.0
    o.append(f'<rect x="{X0}" y="{ty}" width="{ln * k:.2f}" height="{w * k:.2f}"/>')
    o.append(f'<rect x="{X0}" y="{sy}" width="{ln * k:.2f}" height="{h * k:.2f}"/>')
    o.append('</g><g fill="none" stroke="red" stroke-width="0.2">')
    for face, x, a, (th, dr, dp, dd), what in hl:
        if face == 'top': o.append(f'<circle cx="{X0 + x * k:.2f}" cy="{ty + a * k:.2f}" r="{max(dr / 2 * k, 0.4):.2f}"/>')
        elif face == 'outer side': o.append(f'<circle cx="{X0 + x * k:.2f}" cy="{sy + a * k:.2f}" r="{max(dr / 2 * k, 0.5):.2f}"/>')
        else: o.append(f'<circle cx="{X0 + x * k:.2f}" cy="{sy + a * k:.2f}" r="0.6"/>')
    o.append('</g><g font-size="3.2">')
    o.append(f'<text x="{X0}" y="18" font-size="5" font-weight="bold">goa console: frame rail, 2 off</text>')
    o.append(f'<text x="{X0}" y="{ty - 3}">Top face (panel screws): {sum(1 for f in hl if f[0] == "top")} x M3, tap drill 2.5 x 8, thread 6 deep, on the centre line</text>')
    o.append(f'<text x="{X0}" y="{sy - 3}">Side face: M4 tapped through at mid-length, mid-height (bond). Ends: 2 x M4 x 10 at z {h / 4:g} / {3 * h / 4:g} (cheek fixing)</text>')
    o.append(f'<text x="{X0}" y="{sy + h * k + 8}">{MATERIAL}. Length {ln:.1f} mm. Section 10 x 50 on edge. Hole positions +-0.15 mm. Scale 1:3.5.</text>')
    o.append(f'<text x="{X0}" y="{sy + h * k + 14}">Panel screw holes, x from the left end (mm):</text>')
    xs = [x for f, x, *_ in hl if f == 'top']
    for i in range(0, len(xs), 10):
        o.append(f'<text x="{X0}" y="{sy + h * k + 20 + 5 * (i // 10)}">' + '   '.join(f'{x:.2f}' for x in xs[i:i + 10]) + '</text>')
    o.append('</g></svg>')
    open(path, 'w').write('\n'.join(o) + '\n')

def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'frame')); os.makedirs(out, exist_ok=True)
    ln, hl = holes()
    dxf(os.path.join(out, 'rail.dxf'), ln, hl)
    with open(os.path.join(out, 'rail_holes.csv'), 'w', newline='') as f:
        wr = csv.writer(f); wr.writerow(['face', 'x mm from left end', 'y / z mm', 'thread', 'tap drill', 'thread depth', 'drill depth', 'what'])
        for face, x, a, (th, dr, dp, dd), what in hl: wr.writerow([face, f'{x:.2f}', f'{a:.2f}', th, dr, dp, dd, what])
    svg(os.path.join(out, 'rail.svg'), ln, hl)
    rsvg = subprocess.run(['which', 'rsvg-convert'], capture_output=True, text=True).stdout.strip()
    if rsvg: subprocess.run([rsvg, '-f', 'pdf', '-o', os.path.join(out, 'rail.pdf'), os.path.join(out, 'rail.svg')], check=True)
    xs = [x for f, x, *_ in hl if f == 'top']
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    print(f'rail {ln:.1f} mm, {len(xs)} M3 panel holes ({xs[0]:.2f} .. {xs[-1]:.2f}, pitch {min(gaps):.2f}-{max(gaps):.2f}), '
          f'{sum(1 for f in hl if "end" in f[0])} M4 end holes, 1 bonding hole')
    # every panel's screws land on a rail: on a rail line and inside its length, clear of the cheek rebates
    for item, key, x in L.modules():
        for sx, sy in L.Panel(key, L.WIDTH[key]).screws:
            assert sy in L.RAIL_LINES and L.rail_span()[0] + L.RAIL_INTO + 3 < x + sx < L.rail_span()[1] - L.RAIL_INTO - 3, (item, sx, sy)

if __name__ == '__main__':
    main()
