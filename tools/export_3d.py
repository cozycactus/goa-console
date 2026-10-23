"""Export placed boards to JSON for tools/console_3d.py (Blender), one file per module. Run with KiCad's Python:
  $KPY tools/export_3d.py channel_strip_v4.kicad_pcb jack_board.kicad_pcb > render/strip.json
  $KPY tools/export_3d.py group.kicad_pcb group_jack_board.kicad_pcb > render/group.json
  $KPY tools/export_3d.py master.kicad_pcb master_jack_board.kicad_pcb > render/master.json
Per footprint: ref, footprint, value, position, rotation, side, courtyard box, IDC headers' pin 1, whether KiCad has a 3D model for it
(then render/glb/<board>.glb carries it), the through-hole pad positions of those that don't, and for panel parts
the board position of the panel feature (pot shaft, PVA2 actuator, LED, jack nose, XLR barrel, fader slot centre).
The parts modelled in tools/models3d are built in Blender from there (their own .wrl models are for KiCad's viewer)."""
import json, math, os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models3d import registry
M3D = os.environ.get('KICAD10_3DMODEL_DIR', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels')
PARTS = registry()
FEATURE = {'LED_D3.0mm': (1.27, 0.0), 'LED_D5.0mm': (1.27, 0.0)}
FEATURE.update({fp: mod.FEATURE for fp, (mod, kw) in PARTS.items() if mod.FEATURE})

def has_model(fp):
    """True when KiCad's GLB export will put a 3D model in for the footprint: it takes STEP only (a VRML's STEP twin
    with --subst-models), and a tools/models3d part is built in Blender instead."""
    if fp.GetFPIDAsString().split(':')[-1] in PARTS: return False
    for m in fp.Models():
        f = os.path.splitext(os.path.expandvars(m.m_Filename.replace('${KICAD10_3DMODEL_DIR}', M3D)))[0]
        if m.m_Show and any(os.path.exists(f + e) for e in ('.step', '.stp', '.STEP')): return True
    return False

def to_board(fp, lx, ly):                 # KiCad: y down, orientation counter-clockwise on screen
    a = math.radians(fp.GetOrientationDegrees()); p = fp.GetPosition()
    if fp.IsFlipped(): ly = -ly                   # KiCad flips a footprint top to bottom (mirrors y), then rotates
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
        if 'IDC-Header' in name:                # pin 1, for the socket's key and the cable's red stripe
            part['pin1'] = next([pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)] for p in fp.Pads() if p.GetNumber() == '1')
        part['model'] = has_model(fp)
        if not part['model']:                   # through-hole pins of the parts built in Blender
            part['pads'] = [[pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)] for p in fp.Pads()
                            if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
        board['parts'].append(part)
    out.append(board)
json.dump(out, sys.stdout, indent=0)
