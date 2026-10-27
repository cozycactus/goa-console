"""Proves every rule in tools/netrules.py's .kicad_dru fires (KiCad skips a rule whose condition it can't evaluate,
without a message). Run with KiCad's Python: $KPY tools/netrules_test.py. Works on a scratch copy of the strip: one
bottom-side track group per rule in an empty spot, then kicad-cli DRC, expecting each rule by name."""
import os, shutil, subprocess, sys, tempfile
import pcbnew
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KC = os.environ.get('KC', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
tmp = tempfile.mkdtemp()
for ext in ('kicad_pcb', 'kicad_pro', 'kicad_dru'): shutil.copy(os.path.join(ROOT, 'channel_strip.' + ext), tmp)
path = os.path.join(tmp, 'channel_strip.kicad_pcb')
b = pcbnew.LoadBoard(path); M = pcbnew.FromMM
pads = [p.GetBoundingBox() for f in b.GetFootprints() for p in f.Pads()]
crt = [f.GetCourtyard(pcbnew.B_CrtYd).BBox() for f in b.GetFootprints() if f.IsFlipped()]
def spots(w, h):
    for y10 in range(500, 4400, 10):
        for x10 in range(80, 380 - int(w * 10), 10):          # right of the rail corridor (x 0.5-5.5)
            r = pcbnew.BOX2I(pcbnew.VECTOR2I(M(x10 / 10), M(y10 / 10)), pcbnew.VECTOR2L(M(w), M(h)))
            if not any(r.Intersects(q) for q in pads + crt): yield x10 / 10, y10 / 10
free = spots(8, 3); used = []
def spot():
    for s in free:
        if all(abs(s[0] - u[0]) > 9 or abs(s[1] - u[1]) > 4 for u in used): used.append(s); return s
def track(net, a, z, w, layer=pcbnew.B_Cu):
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(M(a[0]), M(a[1]))); t.SetEnd(pcbnew.VECTOR2I(M(z[0]), M(z[1])))
    t.SetWidth(M(w)); t.SetLayer(layer); t.SetNet(b.FindNet(net)); b.Add(t)
def pair(n1, w1, n2, w2, gap):                     # two parallel 7 mm tracks, edge to edge gap
    x, y = spot(); track(n1, (x + .5, y + .5), (x + 7.5, y + .5), w1); track(n2, (x + .5, y + .5 + (w1 + w2) / 2 + gap), (x + 7.5, y + .5 + (w1 + w2) / 2 + gap), w2)
HZ = 'Net-(U5B--)'
pair(HZ, 0.2, 'SIG_B', 0.25, 0.6)                   # sensitive 1 mm from switching
pair(HZ, 0.2, '+5VL', 0.4, 0.35)                    # sensitive 0.5 mm from logic supplies
pair('GNDD', 0.6, 'GNDA', 0.6, 0.3)                 # GNDD 0.5 mm from GNDA
pair('MIXL', 0.3, 'POST', 0.25, 0.25)               # bus / entry / high-Z tracks 0.3 mm
x, y = spot(); track('+VA', (x + .5, y + .5), (x + 7.5, y + .5), 0.3)       # power tracks wide
x, y = spot(); track('GNDA', (x + .5, y + .5), (x + 7.5, y + .5), 0.25)     # ground tracks wide
# high-Z longer than 60 mm: a zig-zag in one empty column
x, y = spot()
for i in range(9): track(HZ, (x + .5 + (7 if i % 2 else 0), y + .5 + 0.4 * i), (x + .5 + (0 if i % 2 else 7), y + .5 + 0.4 * (i + 1)), 0.2)
# 4-layer rules (the strip main is 4-layer): a track on the GND plane, a high-Z track on the PWR layer, a signal zone on GND
x, y = spot(); track('POST', (x + .5, y + .5), (x + 7.5, y + .5), 0.25, pcbnew.In1_Cu)
x, y = spot(); track(HZ, (x + .5, y + .5), (x + 7.5, y + .5), 0.2, pcbnew.In2_Cu)
# the rail corridor (rule area RAILS): a rail on GND2 outside it, a high-Z B.Cu track inside it
ra = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName() == 'RAILS'][0].GetBoundingBox()
cx, cy0 = pcbnew.ToMM(ra.GetLeft()) + 1.0, pcbnew.ToMM(ra.GetTop()) + 60
x, y = spot(); track('+VA', (x + .5, y + .5), (x + 7.5, y + .5), 0.8, pcbnew.In2_Cu)
track(HZ, (cx, cy0), (cx, cy0 + 5), 0.2, pcbnew.B_Cu)
x, y = spot(); z = pcbnew.ZONE(b); z.SetLayer(pcbnew.In1_Cu); z.SetNet(b.FindNet('POST'))
ol = z.Outline(); ol.NewOutline()
for px, py in ((x + .5, y + .5), (x + 7.5, y + .5), (x + 7.5, y + 2.5), (x + .5, y + 2.5)): ol.Append(M(px), M(py))
b.Add(z)
pcbnew.SaveBoard(path, b)
# CHASSIS lives on the jack board: a CHASSIS track there, 0.3 mm from a GNDA track
for ext in ('kicad_pcb', 'kicad_pro', 'kicad_dru'): shutil.copy(os.path.join(ROOT, 'jack_board.' + ext), tmp)
jpath = os.path.join(tmp, 'jack_board.kicad_pcb'); jb = pcbnew.LoadBoard(jpath)
def jtrack(net, a, z, w):
    t = pcbnew.PCB_TRACK(jb); t.SetStart(pcbnew.VECTOR2I(M(a[0]), M(a[1]))); t.SetEnd(pcbnew.VECTOR2I(M(z[0]), M(z[1])))
    t.SetWidth(M(w)); t.SetLayer(pcbnew.B_Cu); t.SetNet(jb.FindNet(net)); jb.Add(t)
jtrack('/CHASSIS', (14, 2), (22, 2), 1.5); jtrack('GNDA', (14, 3.35), (22, 3.35), 0.6)
pcbnew.SaveBoard(jpath, jb)
# the wing feeds exist on the master only: a 1.0 mm +VBUS_L track there
for ext in ('kicad_pcb', 'kicad_pro', 'kicad_dru'): shutil.copy(os.path.join(ROOT, 'master.' + ext), tmp)
mpath = os.path.join(tmp, 'master.kicad_pcb'); mb = pcbnew.LoadBoard(mpath)
t_ = pcbnew.PCB_TRACK(mb); t_.SetStart(pcbnew.VECTOR2I(M(70), M(300))); t_.SetEnd(pcbnew.VECTOR2I(M(70), M(305))); t_.SetWidth(M(1.0))
t_.SetLayer(pcbnew.B_Cu); t_.SetNet(mb.FindNet('+VBUS_L')); mb.Add(t_); pcbnew.SaveBoard(mpath, mb)
# the 4 A paths exist on the PSU only: a 2.0 mm +V track there
for ext in ('kicad_pcb', 'kicad_pro', 'kicad_dru'): shutil.copy(os.path.join(ROOT, 'psu.' + ext), tmp)
ppath = os.path.join(tmp, 'psu.kicad_pcb'); pb = pcbnew.LoadBoard(ppath)
t_ = pcbnew.PCB_TRACK(pb); t_.SetStart(pcbnew.VECTOR2I(M(60), M(30))); t_.SetEnd(pcbnew.VECTOR2I(M(66), M(30))); t_.SetWidth(M(2.0))
t_.SetLayer(pcbnew.B_Cu); t_.SetNet(pb.FindNet('/+V')); pb.Add(t_); pcbnew.SaveBoard(ppath, pb)
rules = [l.split('"')[1] for l in open(os.path.join(ROOT, 'channel_strip.kicad_dru')) if l.startswith('(rule')]   # the strip has the 4-layer rules too
hits = {}
for name in ('channel_strip', 'jack_board', 'master', 'psu'):
    subprocess.run([KC, 'pcb', 'drc', '--severity-all', '-o', os.path.join(tmp, name + '.rpt'), os.path.join(tmp, name + '.kicad_pcb')],
                   capture_output=True)
    rpt = open(os.path.join(tmp, name + '.rpt')).read()
    for r in rules: hits[r] = hits.get(r, 0) + rpt.count(f"rule '{r}'")
bad = [r for r in rules if not hits[r]]
for r in rules: print(f'{hits[r]:3d}  {r}')
print("all rules fire" if not bad else f"NOT FIRING: {bad}  (scratch: {tmp})")
if not bad: shutil.rmtree(tmp)
sys.exit(1 if bad else 0)
