"""Write the project footprints that the KiCad library lacks into goa-console.pretty/.
Dimensions are from the manufacturer drawings quoted below; check a real part against a 1:1 print
before ordering boards."""
import os, uuid

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

def footprint(name, descr, tags, body, ref_xy, val_xy):
    s = (f'(footprint "{name}"\n\t(version 20240108)\n\t(generator "goa_footprints_py")\n\t(layer "F.Cu")\n'
         f'\t(descr "{descr}")\n\t(tags "{tags}")\n')
    s += text('Reference', 'REF**', *ref_xy, 'F.SilkS') + text('Value', name, *val_xy, 'F.Fab')
    s += text('Footprint', '', 0, 0, 'F.Fab', hide=True) + text('Datasheet', '', 0, 0, 'F.Fab', hide=True)
    s += '\t(attr through_hole)\n' + body
    s += (f'\t(model "${{KIPRJMOD}}/goa-console.3dshapes/{name}.wrl"\n\t\t(offset (xyz 0 0 0))\n\t\t(scale (xyz 1 1 1))\n'
          '\t\t(rotate (xyz 0 0 0))\n\t)\n)\n')       # tools/models3d/check.py --wrl writes it
    open(os.path.join(OUT, name + '.kicad_mod'), 'w').write(s)

# ---- Bourns PTB0143-2010APA103: 100 mm travel, single gang, PC pins down, AP lever (4 mm fork), A10K
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

# ---- Bourns PTB0144-2010APA103: as PTB0143 but dual gang. Same drawing: pins 1', 2', 3' (here 4, 5, 6)
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

# ---- Bourns MF-RX160/72 radial PTC (72 V, 1.6 A hold, 3.2 A trip, 40 A max): master wing fuses.
# https://www.bourns.com/docs/product-datasheets/mf-rx72.pdf, product dimensions: A 13.94 max (width),
# B 19.94 max (height), C 5.1 +-0.7 lead spacing, E 3.1 max thick, style 2 (straight leads; kinked is -14), lead 0.81 dia.
# 72 V because a +V-to-−V short on a wing puts up to 34 V across one PTC (MF-R160 is 30 V).
b = pad(1, 0, 0, 2.0, 1.1, 'rect') + pad(2, 5.08, 0, 2.0, 1.1)
b += rect('F.Fab', 2.54 - 6.97, -1.55, 2.54 + 6.97, 1.55, 0.1)
b += rect('F.SilkS', 2.54 - 7.09, -1.67, 2.54 + 7.09, 1.67, 0.12)
b += rect('F.CrtYd', 2.54 - 7.35, -1.9, 2.54 + 7.35, 1.9, 0.05)
footprint('Fuse_Bourns_MF-RX160-72_Radial_P5.08mm',
          'Bourns MF-RX160/72 radial PTC resettable fuse, 72 V, 1.6 A hold, lead spacing 5.1 mm, https://www.bourns.com/docs/product-datasheets/mf-rx72.pdf',
          'PTC polyfuse resettable Bourns MF-RX', b, (2.54, -3.0), (2.54, 3.0))

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
print('wrote', sorted(os.listdir(OUT)))
