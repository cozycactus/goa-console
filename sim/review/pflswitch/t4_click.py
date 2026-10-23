from pfl import *
# Zero-signal switching click at CRS_L: toggle at t_sw = 0.2 s, both directions.
# raw = max |V(CRS_L) - V(CRS_L at t_sw)| within 0.3 s; band = max |V(BAND_L)| (20 Hz-20 kHz) within 0.3 s.
def dbu(v): return 20 * math.log10(max(v, 1e-12) / 0.7746)
ib = None
for variant in sys.argv[1].split(','):
  for model in sys.argv[2].split(','):
    for pfl0 in (0, 1):
        extra = ''
        body = f"""tran 2u 0.5 0 20u
meas tran v0 find v(CRS_L) at=0.199
let dv = abs(v(CRS_L) - v0)
meas tran raw max dv from=0.2 to=0.5
let ab = abs(v(BAND_L))
meas tran band max ab from=0.2 to=0.5
meas tran tb when ab=band from=0.2 to=0.5
let ar = abs(v(BAND_R))
meas tran bandr max ar from=0.2 to=0.5
meas tran v1 find v(CRS_L) at=0.5
"""
        out = run(f't4_{variant}_{model}_{pfl0}', make(variant, model, body, pfl0=pfl0, t_sw=0.2), timeout=3000)
        d = 'PFL press  (MON->PFL)' if pfl0 == 0 else 'PFL release(PFL->MON)'
        raw, band, v0, v1 = grab(out, 'raw'), grab(out, 'band'), grab(out, 'v0'), grab(out, 'v1')
        try:
            print(f'{variant:6s} {model:7s} {d}: CRS before {v0*1e3:8.2f} mV, 0.3 s after {v1*1e3:8.2f} mV; raw peak step {raw*1e3:8.2f} mV ({dbu(raw):6.1f} dBu); '
                  f'20 Hz-20 kHz peak {band*1e3:8.3f} mV ({dbu(band):6.1f} dBu)')
        except TypeError:
            print(variant, model, d, 'FAILED', out[-800:])
