# G6K-2F-Y DC12 coil drive with 560R from the rail, MMBT3904 low side (VCE 0.16 V typ sim, 1.0 V worst).
# Must operate <= 80 % of 12 V at 23 C (spec table) = 9.6 V on the relay's own 23 C resistance; operate is an
# ampere-turn threshold, so it is a constant current that does not change with coil temperature.
R0, RS, TC = 1315.0, 560.0, 0.00393
print(f"{'Vrail':>6} {'R23':>6} {'Tcoil':>6} {'VCE':>4} | {'Icoil mA':>8} {'Vcoil V':>8} {'%rated I':>8} {'need mA':>8} {'margin':>7}")
for vr in (17.0, 16.5, 13.6):
    for tol in (-0.10, 0.0, 0.10):
        for tc in (23, 50, 70):
            for vce in (0.16, 1.0):
                r23 = R0 * (1 + tol); r = r23 * (1 + TC * (tc - 23))
                i = (vr - vce) / (RS + r); need = 9.6 / r23
                if vce == 1.0 and vr != 17.0: continue
                print(f"{vr:6.1f} {r23:6.0f} {tc:6d} {vce:4.2f} | {i*1e3:8.2f} {i*r:8.2f} {i/0.0091*100:7.0f}% {need*1e3:8.2f} {i/need*100-100:+6.0f}%")
# maximum coil voltage at the PSU fault peak (19.7 V), coldest / highest-R coil
for r23 in (R0*0.9, R0*1.1):
    print(f"fault 19.7 V, R23 {r23:.0f}: coil {19.7*r23/(RS+r23):.2f} V = {19.7*r23/(RS+r23)/12*100:.0f} % of rated (max 150 %)")
print(f"560R dissipation at 17 V: {(17/(RS+R0))**2*RS*1e3:.0f} mW; at 19.7 V: {(19.7/(RS+R0*0.9))**2*RS*1e3:.0f} mW")
for n in (5, 6):
    print(f"Q1 with {n} coils, cold, R -10 %: {n*16.84/(RS+R0*0.9)*1e3:.1f} mA; Ib = (16.8-0.75)/9.4k = {(16.8-0.75)/9.4:.2f} mA, forced beta {n*16.84/(RS+R0*0.9)/((16.8-0.75)/9400):.0f}")
