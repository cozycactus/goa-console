import sys, math
import numpy as np
f = sys.argv[1]; side = sys.argv[2] if len(sys.argv) > 2 else 'L'
hdr = open(f).readline().split()
d = np.loadtxt(f, skiprows=1)
col = {h: d[:, i] for i, h in enumerate(hdr)}
x = col['v-sweep']; m = 'M' + side
vmp, vmn = col['v(vmp)'], col['v(vmn)']
I = np.array([col[f'i(VL{m}{k})'] for k in range(1, 21)])
IO = np.array([col[f'i(VO{m}{k})'] for k in range(1, 21)])
nodes = {k: col[f'v({m}{"A" if k <= 10 else "B"}_{(k - 1) % 10})'] for k in range(1, 21)}
ia = I[0] + IO[0]; ib = I[10] + IO[10]           # CCS collector currents = current into node 0 of each string
vce_a = col[f'v({m}A_QE)'] - col[f'v({m}A_0)']; vce_b = col[f'v({m}B_QE)'] - col[f'v({m}B_0)']
vout_max = np.max(np.array([nodes[k] for k in range(1, 21)]), axis=0) - vmn
print(f'VM: +{vmp.min():.3f}..{vmp.max():.3f}  -{-vmn.max():.3f}..{-vmn.min():.3f} V;  T1 {col[f"v({m}_T1)"][0]*1e3:.2f} mV, T11 {col[f"v({m}_T11)"][0]:.4f} V, T20 {col[f"v({m}_T20)"][0]:.4f} V')
print(f'string A current {ia.min()*1e3:.3f}..{ia.max()*1e3:.3f} mA, string B {ib.min()*1e3:.3f}..{ib.max()*1e3:.3f} mA')
print(f'CCS Vce min: A {vce_a.min():.3f} V, B {vce_b.min():.3f} V;  max comparator output above its GND pin (-VM): {vout_max.max():.2f} V')
print(f'max comparator sink current {(-IO).max()*1e3 if (-IO).max()>0 else 0:.3f} / {IO.max()*1e3:.3f} mA; sat V at that: see below')
print('level  DET     lit LEDs (>1 mA)            glow(10uA-1mA)  I_A    I_B    Vce_A  Vce_B  Vout_max  Vol_sinking')
for L in range(-25, 21):
    v = 0.649 * 10 ** (L / 20); i = int(np.argmin(abs(x - v)))
    lit = [k for k in range(1, 21) if I[k - 1, i] > 1e-3]
    glow = [k for k in range(1, 21) if 1e-5 < I[k - 1, i] <= 1e-3]
    sink = [k for k in range(1, 21) if IO[k - 1, i] > 1e-3]
    vol = ','.join(f'{nodes[k][i] - vmn[i]:.2f}' for k in sink)
    s = f'{lit[0]}-{lit[-1]}' if lit and lit == list(range(lit[0], lit[-1] + 1)) else str(lit)
    print(f'{L:+4d} {v:7.4f}  {s:<26} {str(glow):<14} {ia[i]*1e3:5.2f}  {ib[i]*1e3:5.2f}  {vce_a[i]:5.2f}  {vce_b[i]:5.2f}  {vout_max[i]:6.2f}   {vol}')
# switching thresholds: DET where LED k reaches half its string current, in dB re LED 11's
th = []
for k in range(1, 21):
    s = ia if k <= 10 else ib
    j = np.argmax(I[k - 1] > 0.5 * s)
    th.append(x[j] if I[k - 1, j] > 0.5 * s[j] else float('nan'))
ref = th[10]
print('LED k: switch-on DET (V), dB re LED 11, error vs ideal 2 dB grid (dB)')
for k in range(1, 21):
    db = 20 * math.log10(th[k - 1] / ref); print(f'  {k:2d}  {th[k-1]:.4f}  {db:+7.2f}  {db - (2 * (k - 11)):+.2f}')
