"""Proves tools/route_check.py: on a scratch copy of the (4-layer) strip, routes one known fault per check and the
matching known-good case, runs the checker and expects exactly the faults. Run with KiCad's Python:
  $KPY tools/route_check_test.py"""
import os, shutil, sys, tempfile
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_check
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
tmp = tempfile.mkdtemp()
for ext in ('kicad_pcb', 'kicad_pro'): shutil.copy(os.path.join(ROOT, 'boards', 'channel_strip', 'channel_strip.' + ext), tmp)
path = os.path.join(tmp, 'channel_strip.kicad_pcb')
b = pcbnew.LoadBoard(path); M, mm = pcbnew.FromMM, pcbnew.ToMM
def P(v): return (mm(v.x), mm(v.y))
def pad(ref, num): return [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0]
def track(net, a, z, layer=pcbnew.F_Cu, w=0.2):
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(M(a[0]), M(a[1]))); t.SetEnd(pcbnew.VECTOR2I(M(z[0]), M(z[1])))
    t.SetWidth(M(w)); t.SetLayer(layer); t.SetNet(b.FindNet(net)); b.Add(t)
def via(net, p):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(M(p[0]), M(p[1]))); v.SetWidth(M(0.6)); v.SetDrill(M(0.3))
    v.SetNet(b.FindNet(net)); b.Add(v)
def zone(net, layer, x0, y0, x1, y1):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet(net)); o = z.Outline(); o.NewOutline()
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): o.Append(M(px), M(py))
    b.Add(z)
HZ = 'Net-(U5B--)'
# planes: In1 GNDA with a 5 mm gap across the board at y 200-205; In2 GNDA everywhere
zone('GNDA', pcbnew.In1_Cu, 0.2, 44.2, 37.8, 200); zone('GNDA', pcbnew.In1_Cu, 0.2, 205, 37.8, 443.8)
zone('GNDA', pcbnew.In2_Cu, 0.2, 44.2, 37.8, 443.8)
# 1 return vias: one high-Z via alone (ERR), one with a GNDA via 0.8 mm away (fine)
via(HZ, (20.0, 250.0)); via(HZ, (30.0, 250.0)); via('GNDA', (30.8, 250.0))
# 2 reference: a high-Z F.Cu track across the In1 gap (ERR)
track(HZ, (25.0, 190.0), (25.0, 215.0))
# 3 high-Z: a 70 mm high-Z track on top of the rest (WARN: well past 1.5x its pads' spread + 5 mm)
track(HZ, (35.0, 260.0), (35.0, 330.0))
# 4 decoupler: C20 to U1 pin 8 by an 8 mm detour, its ground pad with no via (two WARN)
p8, c = P(pad('U1', '8').GetPosition()), P(pad('C20', [q.GetNumber() for q in b.FindFootprintByReference('C20').Pads() if q.GetNetname() == '+VA'][0]).GetPosition())
track('+VA', p8, (p8[0], p8[1] - 8)); track('+VA', (p8[0], p8[1] - 8), c)
# 5 stability: C78 (bottom, under U1 pin 3) reached through three vias (ERR); C75 (under U12 pin 3) through one, with a
# GNDA via 1-2 mm away, the nearest a SOIC pin allows (fine for checks 2 and 5, WARN only for check 1)
p3 = P(pad('U1', '3').GetPosition()); c78 = [q for q in b.FindFootprintByReference('C78').Pads() if q.GetNetname() == pad('U1', '3').GetNetname()][0]
n3 = pad('U1', '3').GetNetname().lstrip('/'); x, y = p3
track(n3, p3, (x - 1, y)); via(n3, (x - 1, y)); track(n3, (x - 1, y), (x - 1, y + 1.5), pcbnew.B_Cu)
via(n3, (x - 1, y + 1.5)); track(n3, (x - 1, y + 1.5), (x + 1.5, y + 1.5)); via(n3, (x + 1.5, y + 1.5))
track(n3, (x + 1.5, y + 1.5), P(c78.GetPosition()), pcbnew.B_Cu)
q3 = P(pad('U12', '3').GetPosition()); c75 = [q for q in b.FindFootprintByReference('C75').Pads() if q.GetNetname() == pad('U12', '3').GetNetname()][0]
m3 = pad('U12', '3').GetNetname().lstrip('/'); via(m3, q3); track(m3, q3, P(c75.GetPosition()), pcbnew.B_Cu)
def clear_spot(c, r=1.9):                         # a via on any pad takes that pad's net when KiCad loads the board
    allpads = [q.GetBoundingBox() for f in b.GetFootprints() for q in f.Pads()]
    for i in range(1, 20):
        for k in range(16):
            import math
            x, y = c[0] + r * i / 19 * math.cos(k * math.pi / 8), c[1] + r * i / 19 * math.sin(k * math.pi / 8)
            box = pcbnew.BOX2I(pcbnew.VECTOR2I(M(x - 0.35), M(y - 0.35)), pcbnew.VECTOR2L(M(0.7), M(0.7)))
            if not any(box.Intersects(q) for q in allpads): return (x, y)
    raise SystemExit('no clear spot for the GNDA via')
via('GNDA', clear_spot(q3))
# 6 GNDD: a GNDD fill on F.Cu (ERR)
zone('GNDD', pcbnew.F_Cu, 1.0, 300.0, 3.0, 302.0)
pcbnew.SaveBoard(path, b)
lines = []; route_check.check(path, out=lines.append)
text = '\n'.join(lines); print(text)
want = [('ERR', '1 return via', HZ, '(20.0, 250.0)'), ('WARN', '1 return via', 'Net-(U12A-+)', ''), ('ERR', '2 reference', HZ, 'over a gap'), ('WARN', '3 high-Z', HZ, ''),
        ('WARN', '4 decoupler: C20 is', '', ''), ('WARN', '4 decoupler: C20 ground', '', ''), ('ERR', '5 stability: C78', '3 vias', ''),
        ('ERR', '6 GNDD', '', '')]
nowant = ['(30.0, 250.0)', '5 stability: C75', 'ERR  1 return via: Net-(U12A-+)', 'ERR  2 reference: Net-(U12A-+)']
miss = [w for w in want if not any(all(x in l for x in w if x) for l in lines)]
extra = [w for w in nowant if any(w in l for l in lines)]
print('\nexpected faults found:', len(want) - len(miss), 'of', len(want), '; known-good cases flagged:', len(extra))
if miss: print('MISSING', miss)
if extra: print('FALSE ALARMS', extra)
shutil.rmtree(tmp); sys.exit(1 if miss or extra else 0)
