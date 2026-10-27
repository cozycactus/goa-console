"""CS10 (console_survey.md §7): what a strip's audio rails do when one supply rail goes away, with and without a reverse
Schottky across each reservoir (PMEG4010CEH: cathode +VA / anode GNDA, cathode GNDA / anode -VA).

Model (one strip or group board; values from the strip netlist where they exist):
- +VBUS -> R1 10R -> +VA (C1 220u // C2 100n + the op-amps' 100n decouplers); -VBUS -> R2 10R -> -VA (C3 220u, ...);
- the op-amps' quiescent current flows rail to rail: 87 mA (the strip's -V current, test_jig_spec.md 4.1), constant
  down to a 4.5 V span (OPA1612 / OPA1656 datasheets: specified from +-2.25 V) and falling to 0 at 1.5 V;
- 13 mA more from +VA to ground (the +5VL zener feed, output loads);
- the ICs' own way back to ground when a rail crosses it: their pin-protection diodes into inputs and outputs that sit
  near ground through the circuit's resistors. Lumped as one silicon diode in series with R_PIN; R_PIN = 20 ohm (low
  impedance paths, e.g. outputs into coupling caps) and 200 ohm (through resistors) bracket it;
- the lost rail: its bus source disconnects at 20 ms (a wing PTC trips, a ribbon conductor opens). The power-down case
  ramps both buses to 0 at 280 / 240 V/s (+V faster: 2.8 / 2.4 A into ~10 mF), as sim/review/cs1/ol_multi.py.
Measured: the dead rail's voltage (its polar 220 uF reverse-biased when it crosses ground) and the current through the
ICs' protection paths, 100 ms after the loss.
usage: python3 sim/review/cs10/rail_loss.py"""
import os, re, subprocess, tempfile

VB = 17.0
PMEG = '.model DPMEG D(IS=1.75e-7 N=1.05 RS=0.045 CJO=70p BV=40 IBV=50u)'     # fit: 340 mV at 0.1 A, 490 mV at 1 A
PIN = '.model DPIN D(IS=1e-14 N=1.0 RS=0)'

def deck(case, schottky, r_pin, tstop=0.15):
    if case == 'lose -V':
        vp, vn = f'DC {VB}', f'PWL(0 -{VB} 20m -{VB} 20.001m 0)'
        sw = 'RSWN vnb_s vnb 1m\nSN vnb_s vnb2 ctl 0 SWO\nRN2 vnb2 vnb 1e9'
    elif case == 'lose +V':
        vp, vn = f'PWL(0 {VB} 20m {VB} 20.001m 0)', f'DC -{VB}'
        sw = ''
    else:                                                                # power-down, +V falls faster
        vp, vn = f'PWL(0 {VB} 20m {VB} {0.02 + VB / 280} 0)', f'PWL(0 -{VB} 20m -{VB} {0.02 + VB / 240} 0)'
        sw = ''
    # a lost rail is open (not driven to 0 V): model the bus source behind a switch that opens at 20 ms
    lose_p, lose_n = case == 'lose +V', case == 'lose -V'
    return f"""* CS10 rail loss: {case}, schottky={schottky}, R_PIN={r_pin}
{PMEG}
{PIN}
.model SWO SW(VT=0.5 VH=0.01 RON=1m ROFF=1e9)
VCTL ctl 0 PWL(0 1 20m 1 20.001m 0)
VP vpb_s 0 {f'DC {VB}' if lose_p else vp}
VN vnb_s 0 {f'DC -{VB}' if lose_n else vn}
{'SP vpb_s vpb ctl 0 SWO' if lose_p else 'RP0 vpb_s vpb 1m'}
{'SN vnb_s vnb ctl 0 SWO' if lose_n else 'RN0 vnb_s vnb 1m'}
R1 vpb va_p 10
R2 vnb va_n 10
C1 va_p 0 220u
C3 0 va_n 220u
CDP va_p 0 2.6u
CDN 0 va_n 2.6u
* rail-to-rail quiescent current, constant above a 4.5 V span
BIQ va_p va_n I = 87m * min(1, max(0, (v(va_p) - v(va_n) - 1.5) / 3))
BIG va_p 0 I = 13m * min(1, max(0, v(va_p) / 2))
* the ICs' protection paths back to ground (one per rail), current measured in VPN / VPP
DPN va_n pn DPIN
RPN pn pn2 {r_pin}
VPN pn2 0 0
DPP pp va_p DPIN
RPP pp2 pp {r_pin}
VPP 0 pp2 0
{'DSN va_n 0 DPMEG' if schottky else ''}
{'DSP 0 va_p DPMEG' if schottky else ''}
.ic v(va_p)={VB - 1.0} v(va_n)={-VB + 0.87}
.control
set noaskquit
tran 20u {tstop} 0 20u
meas tran vn_max max v(va_n) from=20m
meas tran vp_min min v(va_p) from=20m
meas tran ipn_max max i(VPN) from=20m
meas tran ipp_max max i(VPP) from=20m
meas tran vn_end find v(va_n) at={tstop}
meas tran vp_end find v(va_p) at={tstop}
meas tran t_rev when v(va_n)=0.3 rise=1
.endc
.end"""

def run(d):
    with tempfile.NamedTemporaryFile('w', suffix='.cir', delete=False) as f: f.write(d)
    out = subprocess.run(['ngspice', '-b', f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    return {k.lower(): float(x) for k, x in re.findall(r'^(\w+)\s+=\s+([-+0-9.eE]+)', out, re.M)}

if __name__ == '__main__':
    print('strip / group audio rails, 100 ms after the event (R_PIN: the ICs\' own protection paths to ground)')
    print(f'{"event":30s} {"R_PIN":>6s} {"diodes":>7s} | {"-VA max":>8s} {"+VA min":>8s} | {"IC paths peak":>14s}')
    for case in ('lose -V', 'lose +V', 'power-down, +V faster'):
        for r_pin in (20, 200):
            for sch in (False, True):
                r = run(deck(case, sch, r_pin))
                ip = max(r.get('ipn_max', 0), r.get('ipp_max', 0))
                print(f'{case:30s} {r_pin:6d} {"PMEG" if sch else "none":>7s} | {r["vn_max"]:+8.2f} {r["vp_min"]:+8.2f} | '
                      f'{ip * 1e3:11.2f} mA', flush=True)
    r = run(deck('lose -V', False, 200))
    if r.get('t_rev'): print(f'without the diodes, -VA crosses +0.3 V {(r["t_rev"] - 0.02) * 1e3:.1f} ms after -V is lost')
