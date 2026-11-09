"""Write the project footprints that the KiCad library lacks into goa-console.pretty/.
Dimensions are from the manufacturer drawings quoted below; check a real part against a 1:1 print
before ordering boards."""
import math, os, uuid

OUT = os.path.join(os.path.dirname(__file__), '..', 'goa-console.pretty')
_n = [0]
def U():                          # deterministic, so regenerating changes only what changed
    _n[0] += 1; return str(uuid.uuid5(uuid.NAMESPACE_URL, f'goa-console.pretty/{_n[0]}'))

def rect(layer, x0, y0, x1, y1, w):
    return (f'\t(fp_rect (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f}) (stroke (width {w}) (type solid)) '
            f'(fill none) (layer "{layer}") (uuid "{U()}"))\n')

def line(layer, x0, y0, x1, y1, w):
    return (f'\t(fp_line (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f}) (stroke (width {w}) (type solid)) '
            f'(layer "{layer}") (uuid "{U()}"))\n')

def text(kind, value, x, y, layer, hide=False):
    h = ' (hide yes)' if hide else ''
    return (f'\t(property "{kind}" "{value}" (at {x:.3f} {y:.3f} 0) (layer "{layer}"){h} (uuid "{U()}") '
            f'(effects (font (size 1 1) (thickness 0.15))))\n')

def pad(num, x, y, size, drill, shape='circle'):
    return (f'\t(pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {size} {size}) (drill {drill}) '
            f'(layers "*.Cu" "*.Mask") (uuid "{U()}"))\n')

def footprint(name, descr, tags, body, ref_xy, val_xy, model=True):
    s = (f'(footprint "{name}"\n\t(version 20240108)\n\t(generator "goa_footprints_py")\n\t(layer "F.Cu")\n'
         f'\t(descr "{descr}")\n\t(tags "{tags}")\n')
    s += text('Reference', 'REF**', *ref_xy, 'F.SilkS') + text('Value', name, *val_xy, 'F.Fab')
    s += text('Footprint', '', 0, 0, 'F.Fab', hide=True) + text('Datasheet', '', 0, 0, 'F.Fab', hide=True)
    s += '\t(attr through_hole)\n' + body
    if model:                         # tools/models3d/check.py --wrl writes it
        s += (f'\t(model "${{KIPRJMOD}}/goa-console.3dshapes/{name}.wrl"\n\t\t(offset (xyz 0 0 0))\n\t\t(scale (xyz 1 1 1))\n'
              '\t\t(rotate (xyz 0 0 0))\n\t)\n')
    s += ')\n'
    open(os.path.join(OUT, name + '.kicad_mod'), 'w').write(s)

# ---- Bourns PTB0143-2010BPA103: 100 mm travel, single gang, PC pins down, BP lever (8 mm blade), A10K
# https://www.bourns.com/docs/Product-Datasheets/ptb.pdf (REV. 08/20), PTB100 drawing:
# pin 3 at one end and pins 1, 2 at the other, 127.5 apart; pins 1.9 off the body centreline,
# 3.8 pitch; 1.5 mm holes for pins; 2.0 mm holes for the two body tabs, 38.8 and 43.7 either side
# of the pin-span centre; body 128.0 x 15.0; travel 100.0. Origin = pin 1.
L, CY, BW, BL, TRAVEL = 127.5, -1.9, 15.0, 128.0, 100.0
xc = -L / 2                       # centre of the pin span
bx0, bx1 = xc - BL / 2, xc + BL / 2
by0, by1 = CY - BW / 2, CY + BW / 2
b = pad(1, 0, 0, 2.4, 1.5, 'rect') + pad(2, 0, 3.8, 2.4, 1.5) + pad(3, -L, 0, 2.4, 1.5)
b += pad('', xc - 38.8, CY, 3.0, 2.0) + pad('', xc + 43.7, CY, 3.0, 2.0)   # body tabs, no net (housing floats to the panel via the M3 screws)
b += rect('F.Fab', bx0, by0, bx1, by1, 0.1)
b += rect('F.Fab', xc - TRAVEL / 2 - 0.5, CY - 0.5, xc + TRAVEL / 2 + 0.5, CY + 0.5, 0.1)   # lever slot / travel
b += line('F.Fab', xc, by0, xc, by1, 0.1)
for y in (by0 - 0.12, by1 + 0.12):   # long sides only: the pins sit on the body ends
    b += line('F.SilkS', bx0 - 0.12, y, bx1 + 0.12, y, 0.12)
b += rect('F.CrtYd', bx0 - 1.5, by0 - 0.5, bx1 + 1.5, by1 + 0.5, 0.05)
footprint('Potentiometer_Bourns_PTB0143_Slide_100mm',
          'Bourns PTB series slide potentiometer, 100 mm travel, single gang, PC pins down, https://www.bourns.com/docs/Product-Datasheets/ptb.pdf',
          'fader slide potentiometer 100mm Bourns PTB', b, (xc, by0 - 1.5), (xc, by1 + 1.5))

# ---- Bourns PTB0144-2010BPA103: as PTB0143 but dual gang. Same drawing: pins 1', 2', 3' (here 4, 5, 6)
# mirror 1, 2, 3 about the body centreline (1' and 3' at -1.9, 2' at -5.7 from the centreline).
b = pad(1, 0, 0, 2.4, 1.5, 'rect') + pad(2, 0, 3.8, 2.4, 1.5) + pad(3, -L, 0, 2.4, 1.5)
b += pad(4, 0, 2 * CY, 2.4, 1.5) + pad(5, 0, 2 * CY - 3.8, 2.4, 1.5) + pad(6, -L, 2 * CY, 2.4, 1.5)
b += pad('', xc - 38.8, CY, 3.0, 2.0) + pad('', xc + 43.7, CY, 3.0, 2.0)
b += rect('F.Fab', bx0, by0, bx1, by1, 0.1)
b += rect('F.Fab', xc - TRAVEL / 2 - 0.5, CY - 0.5, xc + TRAVEL / 2 + 0.5, CY + 0.5, 0.1)
b += line('F.Fab', xc, by0, xc, by1, 0.1)
for y in (by0 - 0.12, by1 + 0.12):
    b += line('F.SilkS', bx0 - 0.12, y, bx1 + 0.12, y, 0.12)
b += rect('F.CrtYd', bx0 - 1.5, by0 - 0.5, bx1 + 1.5, by1 + 0.5, 0.05)
footprint('Potentiometer_Bourns_PTB0144_Slide_100mm_Dual',
          'Bourns PTB series slide potentiometer, 100 mm travel, dual gang (pins 4/5/6 = 1\'/2\'/3\'), https://www.bourns.com/docs/Product-Datasheets/ptb.pdf',
          'fader slide potentiometer 100mm dual Bourns PTB', b, (xc, by0 - 1.5), (xc, by1 + 1.5))

# ---- Bourns MF-RX/72 radial PTCs (72 V, 40 A max): MF-RX185/72 (1.85 A hold, 3.7 A trip) master wing fuses
# (2026-10-24, docs/proposals/hpf_proposal.md H4), MF-RX160/72 (1.6 A hold, 3.2 A trip) on the jig's master stub.
# https://www.bourns.com/docs/product-datasheets/mf-rx72.pdf, product dimensions: A 13.94 / 15.18 max (width),
# B 19.94 / 21.18 max (height), C 5.1 +-0.7 lead spacing, E 3.1 max thick, style 2 (straight leads; kinked is -14),
# lead 0.81 dia. 72 V because a +V-to-−V short on a wing puts up to 34 V across one PTC (MF-R160 is 30 V).
def mf_rx(part, a, hold, cy=0.38, p=5.08):
    c = p / 2
    b = pad(1, 0, 0, 2.0, 1.1, 'rect') + pad(2, p, 0, 2.0, 1.1)
    b += rect('F.Fab', c - a / 2, -1.55, c + a / 2, 1.55, 0.1)
    b += rect('F.SilkS', c - a / 2 - 0.12, -1.67, c + a / 2 + 0.12, 1.67, 0.12)
    b += rect('F.CrtYd', c - a / 2 - cy, -1.9, c + a / 2 + cy, 1.9, 0.05)
    footprint(f'Fuse_Bourns_MF-RX{part}-72_Radial_P{p:.2f}mm',
              f'Bourns MF-RX{part}/72 radial PTC resettable fuse, 72 V, {hold} A hold, lead spacing {p:.1f} mm, https://www.bourns.com/docs/product-datasheets/mf-rx72.pdf',
              'PTC polyfuse resettable Bourns MF-RX', b, (c, -3.0), (c, 3.0))
mf_rx('160', 13.94, '1.6')

# ---- Keystone 1287-ST: 0.250" (6.35 mm) quick-fit male PCB tab, Sturdi-Mount
# https://www.keyelco.com/userAssets/file/K75p65.pdf (catalog p.65): two legs 0.200" (5.08) apart,
# 0.052" (1.3) holes, tab 0.250" wide in line with the legs, 0.032" thick, foot 0.120" (3.1) ref.
P = 5.08
b = pad(1, -P / 2, 0, 2.4, 1.3) + pad(1, P / 2, 0, 2.4, 1.3)
b += rect('F.Fab', -3.2, -0.41, 3.2, 0.41, 0.1)                 # tab cross-section
b += rect('F.Fab', -3.2, -1.55, 3.2, 1.55, 0.1)                 # Sturdi-Mount foot
b += rect('F.SilkS', -4.0, -1.8, 4.0, 1.8, 0.12)
b += rect('F.CrtYd', -4.2, -2.0, 4.2, 2.0, 0.05)
footprint('Keystone_1287-ST_FastOn_Tab_6.35mm',
          'Keystone 1287-ST quick-fit male PCB terminal, 0.250 in (6.35 mm) tab, Sturdi-Mount, https://www.keyelco.com/userAssets/file/K75p65.pdf',
          'faston spade tab ground 6.35mm Keystone', b, (0, -3.2), (0, 3.2))
# last: footprints added later keep the UUID sequence of the earlier ones. Courtyard 0.25 mm (KLC): on the master the
# MF-RX185/72 sits between J1 and top-side diode leads where the 160's 0.38 mm doesn't fit (place_master.py)
mf_rx('185', 15.18, '1.85', cy=0.25)
# MF-RX250/72 (+V wing fuses, docs/proposals/wing_power_proposal.md W2): A 17.84 / B 23.84 max, C 10.2 +0.6/-0.2 lead spacing
mf_rx('250', 17.84, '2.5', cy=0.25, p=10.16)
# ---- Kingbright WP3VEGW: T-1 (3 mm) red / green bicolour, white diffused (docs/reviews/feature_gaps.md MET1). Datasheet
# (https://www.kingbrightusa.com/images/catalog/SPEC/WP3VEGW.pdf): 3 leads 0.5 square at 2.0 mm, recommended holes
# Ø0.9; pin 1 anode red, pin 2 common cathode, pin 3 anode green (KiCad's LED_Dual_AKA); dome Ø3.0, flange Ø4.0 at
# the base (fab outline; the square pad 1 marks red), centred on pin 2. No 3D model: the render draws its pins and lens. KiCad's LED_D3.0mm-3 is on 2.54 mm. Origin = pin 1.
P2 = 2.0
b = pad(1, 0, 0, 1.5, 0.9, 'rect') + pad(2, P2, 0, 1.5, 0.9) + pad(3, 2 * P2, 0, 1.5, 0.9)
b += (f'\t(fp_circle (center {P2:.3f} 0) (end {P2 + 2.0:.3f} 0) (stroke (width 0.1) (type solid)) (fill none) '
      f'(layer "F.Fab") (uuid "{U()}"))\n')
for a0 in (32, 212):                                                 # silk: the Ø4.2 rim above and below, clear of the pads
    pt = lambda a: (P2 + 2.1 * math.cos(math.radians(a)), -2.1 * math.sin(math.radians(a)))
    (sx, sy), (mx, my), (ex, ey) = pt(a0), pt(a0 + 58), pt(a0 + 116)
    b += (f'\t(fp_arc (start {sx:.3f} {sy:.3f}) (mid {mx:.3f} {my:.3f}) (end {ex:.3f} {ey:.3f}) (stroke (width 0.12) '
          f'(type solid)) (layer "F.SilkS") (uuid "{U()}"))\n')
b += rect('F.CrtYd', -1.05, -2.4, 2 * P2 + 1.05, 2.4, 0.05)
footprint('LED_D3.0mm-3_P2.00mm',
          'LED, 3 mm round, 3 leads at 2.0 mm (Kingbright WP3VEGW red / green bicolour, common cathode on pin 2), https://www.kingbrightusa.com/images/catalog/SPEC/WP3VEGW.pdf',
          'LED 3mm bicolor bi-color 3 pin', b, (P2, -3.2), (P2, 3.2), model=False)

print('wrote', sorted(os.listdir(OUT)))
