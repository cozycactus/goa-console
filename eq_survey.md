# How other consoles build the swept mid EQ (2026-10-26)

The Delta's mid bands are a Wien band-pass tuned by an "ALPS 16MM 100KC REV.SEMILOG X2", a dual 100K reverse-log
(C-law) pot that no one stocks. This strip replaces it with a KHN state-variable band-pass tuned by a stocked Alpha
A10K dual used as dividers into the two integrators (decision 2026-10-22, spec 6.2). This survey asks how other
consoles solved the same problem.

## Sources and confidence

- **Read from schematics** in Ruslan's iCloud service-manual library: Soundcraft 6000, 200B, Sapphyre, Ghost, Series
  Five; Sony MXP-3000; Yamaha PM-4000 and PM-5000; SSL 4000G. Each was read page by page, and where the parts list was
  readable the values are from it.
- **Mackie:** from the 1642-VLZ Pro service manual's parts list, found on the web.
- **Not found:** Allen & Heath, Midas, Behringer, Tascam, DDA, Amek have no schematic in the library or online.

## The consoles

| Console | Mid band topology | Frequency pot | How the pot is used | Q | Range (printed or calculated) |
|---|---|---|---|---|---|
| Soundcraft 6000, 200B (and the Delta) | Wien band-pass driving the boost/cut stage | dual 100K reverse-log ("100K INV LOG") | two rheostats, one per Wien arm, 6K8 end stops | fixed | 600 Hz–10 kHz, 150 Hz–2.4 kHz (200B printed); the 6000 calculates to the Delta's exact 670 Hz–10.5 kHz / 148 Hz–2.3 kHz |
| Soundcraft Sapphyre | Wien-type band-pass as an inverting stage, positive feedback for Q | dual 100KC | two rheostats, 3K9 end stops | fixed | about 460 Hz–12 kHz, 100 Hz–2.7 kHz (calculated) |
| Soundcraft Ghost | **KHN state-variable**, inside the boost/cut stage | 200KC (dual, possibly a 3-gang part) | rheostats in series with each integrator's input resistor | Q pot, 20KC | about 380 Hz–20 kHz, 26 Hz–1.6 kHz (calculated) |
| Soundcraft Series Five | **KHN state-variable** ("KHN" on the sheet) | 100KC gangs on a concentric gain / frequency pot | rheostats into the integrators, 5K6 / 4K7 end stops | Q pot "10KC REV LOG", 0.5–3 | HMF 500 Hz–8 kHz, LMF 70 Hz–1.5 kHz (printed) |
| Sony MXP-3000 | Wien band-pass fed from a buffered gain-pot wiper | dual **5K** reverse-log | two rheostats, 309R / 499R end stops | fixed; a Vari-Q board adds a Q switch | MID1 150 Hz–2.5 kHz, MID2 800 Hz–8 kHz (printed) |
| Yamaha PM-4000 / PM-5000 | buffered Wien band-pass, gain 3, Q by positive feedback (in a hybrid on the PM-4000, discrete on the PM-5000) | custom dual **C50K** on a concentric gain / frequency pot (V9070400) | two rheostats with 2K7 end stops; f = 1/(2π(2.7K + R)C) | Q pot C50K, 0.5–3, constant peak gain | 80 Hz–1.6 kHz, 400 Hz–8 kHz, ±15 dB (printed) |
| SSL 4000G (611G card, 82E292) | single-op-amp band-pass (series-RC in, parallel-RC feedback), Q by positive feedback with a set-Q trimmer, level make-up stage | dual 47K "A LOG", plus a 100K lin Total Recall gang (12SKHLBX) | two rheostats with 5K1 end stops; frequency rises clockwise, so in effect anti-log | Q pot 10K + 10K log dual, 0.5–3 | HMF 0.6–7 kHz (×3), LMF 0.2–2.5 kHz (÷3) (printed) |
| Mackie 1604 / 1642-VLZ (Perkins EQ) | Wien band-pass | dual **500K C**, 12 mm | two rheostats | fixed, wide | 100 Hz–8 kHz in one band |

## What it shows

- **Every console read tunes with a reverse-log taper, wired as a rheostat.** It makes no difference whether the
  filter is a Wien band-pass (Soundcraft 6000 / 200B / Delta, Sapphyre, Sony, Yamaha, Mackie), a positive-feedback
  band-pass (SSL) or a KHN (Ghost, Series Five).
  - **Why:** with a rheostat in an RC, f ∝ 1/R. An even sweep in octaves with frequency rising clockwise needs the
    resistance to fall exponentially with rotation, which is the C law.
  - **Supply:** Yamaha and SSL had their pots made (custom part numbers with recall gangs), and Soundcraft bought
    100KC / 200KC duals from ALPS. The C-law dual is the whole industry's dependency, which is why it is gone now.
- **Ghost and Series Five are this strip's closest relatives:** the same KHN inside a boost/cut stage. But they still
  tune with C-law rheostats in series with the integrator resistors.
- **No console read tunes by dividers.** This strip's A10K-as-divider tuning appears in none of them.
  - **Why it needs only an A law:** f is proportional to the divider ratio, so a plain log taper gives the even
    sweep in octaves, and a stocked A10K dual does the job.
  - **Noise:** the 10K source impedance is the lowest of all, apart from Sony's 5K.
- **Sony shows the impedance argument from the other side:** a low-value (5K) pot fed from a buffered wiper keeps the
  Wien quiet, but it still needs the C law.
- **Q control is the one feature the big consoles add:** Series Five, Yamaha PM and SSL have a Q pot; the Delta and
  this strip don't.
  - **In this strip's KHN,** Q is set by one resistor ratio at the summer, independent of frequency and gain. A Q pot
    (or a two-position Q switch, as on Sony's Vari-Q board) would be a small circuit change.
  - **The cost:** a panel position per band, and the strip has no free knob positions.
  - **Status:** noted here as an option, not proposed.

## Not settled by the reading

- Ghost's frequency pot may be a 3-gang part, and Series Five's a 3-gang concentric part: inferred from the reference
  lists, not confirmed.
- SSL's "A LOG" marking: the panel calibration implies anti-log, but the manual doesn't say.
- SSL LMF ÷3 capacitors read 47n (a 4.1:1 ratio, not 3:1). Check against another source if it matters.
- Ranges marked "calculated" are from the component values, not printed on the panel.
