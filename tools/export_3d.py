"""Export placed boards to JSON for tools/console_3d.py (Blender), one file per module. Run with KiCad's Python:
  $KPY tools/export_3d.py channel_strip_v4.kicad_pcb jack_board.kicad_pcb > render/strip.json
  $KPY tools/export_3d.py group.kicad_pcb group_jack_board.kicad_pcb > render/group.json
  $KPY tools/export_3d.py master.kicad_pcb master_jack_board.kicad_pcb > render/master.json
Per footprint: ref, footprint, value, position, rotation, side, courtyard box, whether KiCad has a 3D model for it
(then render/glb/<board>.glb carries it), the through-hole pad positions of those that don't, and for panel parts
the board position of the panel feature (pot shaft, PVA2 actuator, LED, jack nose, XLR barrel, fader slot centre)."""
import json, math, os, sys
import pcbnew
M3D = os.environ.get('KICAD10_3DMODEL_DIR', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels')

FEATURE = {'Potentiometer_Alpha_RD901F': (7.5, 2.5), 'Potentiometer_Alpha_RD902F': (7.5, 2.5),
           'SW_Push_2P2T_Toggle_CK_PVA2': (2.5, 3.0), 'LED_D3.0mm': (1.27, 0.0), 'LED_D5.0mm': (1.27, 0.0),
           'NJ6FD-V': (0.0, 5.72), 'NC3MAV': (3.81, 0.0),
           'Potentiometer_Bourns_PTB014': (-63.75, -1.9)}     # slot centre: 63.75 mm from pin 1 along the travel

def has_model(fp):
    """True when KiCad's GLB export will find a 3D model for the footprint (STEP, or the VRML's STEP twin)."""
    for m in fp.Models():
        f = os.path.expandvars(m.m_Filename.replace('${KICAD10_3DMODEL_DIR}', M3D))
        if m.m_Show and (os.path.exists(f) or os.path.exists(os.path.splitext(f)[0] + '.step')): return True
    return False

def to_board(fp, lx, ly):                 # KiCad: y down, orientation counter-clockwise on screen
    a = math.radians(fp.GetOrientationDegrees()); p = fp.GetPosition()
    if fp.IsFlipped(): lx = -lx
    return (pcbnew.ToMM(p.x) + lx * math.cos(a) + ly * math.sin(a), pcbnew.ToMM(p.y) - lx * math.sin(a) + ly * math.cos(a))

out = []
for path in sys.argv[1:]:
    b = pcbnew.LoadBoard(path)
    e = b.GetBoardEdgesBoundingBox()
    board = dict(file=path, x0=pcbnew.ToMM(e.GetLeft()), y0=pcbnew.ToMM(e.GetTop()), x1=pcbnew.ToMM(e.GetRight()),
                 y1=pcbnew.ToMM(e.GetBottom()), parts=[])
    for fp in b.GetFootprints():
        name = fp.GetFPIDAsString()
        lay = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
        fp.BuildCourtyardCaches(); poly = fp.GetCourtyard(lay)
        bb = poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False)
        part = dict(ref=fp.GetReference(), fp=name, value=fp.GetValue(), x=pcbnew.ToMM(fp.GetPosition().x),
                    y=pcbnew.ToMM(fp.GetPosition().y), rot=fp.GetOrientationDegrees(), side='B' if fp.IsFlipped() else 'F',
                    box=[pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())])
        for key, loc in FEATURE.items():
            if key in name: part['feature'] = to_board(fp, *loc)
        part['model'] = has_model(fp)
        if not part['model']:                   # through-hole pins of the parts built in Blender
            part['pads'] = [[pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)] for p in fp.Pads()
                            if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
        board['parts'].append(part)
    out.append(board)
json.dump(out, sys.stdout, indent=0)
