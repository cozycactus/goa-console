# Front-panel makers (2026-10-26)

29 panels to make from `panels/`. They are fixed by the panel decisions:
- **Sizes:** 24 strip and 4 group panels at 40.30 × 514 mm, one master at 80.94 × 514 mm.
- **Material:** 1.5 mm anodised aluminium. 1.5 is the NJ6FD-V jack's maximum panel, so standard 1.6 mm FR4 "PCB
  panels" are out.
- **Print:** one cream ink.
- **Files:** a DXF (outline, cut-outs, legend outlines), a 1:1 PDF of the artwork and a hole table.

## What the artwork needs from the printer

The finest features, measured from the generated artwork and the fonts' own stems:

| Feature | Width |
|---|---|
| Ring numerals and small legends, Arial Narrow 1.5–1.7 mm | **0.108–0.122 mm** strokes |
| Text at 2.0 mm (regular) | 0.144 mm |
| Names, Arial Narrow Bold 2.0–2.4 mm | 0.23–0.27 mm |
| Section rules / fader ticks / scale dots | 0.28 / 0.36 / 0.54 mm |

A maker whose minimum printed line is 0.15 mm can't hold the regular numerals. In that case print the small text in
Arial Narrow Bold, which gives 0.17 mm at 1.5 mm and keeps the same layout: a one-line change in `panel_layout.py`, then
regenerate. A high-resolution digital UV print usually holds 0.1 mm. Ask for it, or print one test panel.

## Candidates

| Maker | Material and print | Files | Size | Notes |
|---|---|---|---|---|
| **Schaeffer AG** (Berlin) | 1.5 mm anodised in stock; digital UV print on all its anodised stock | Panels are built in its free Front Panel Designer: DXF import for contours, PDF recommended for print (≥ 300 dpi) | "practically any" shape and size | The reference for pro-audio front panels. The price shows live in the designer; historically not cheap (a forum figure from 2010: about €88 for a 3 mm 2U panel). |
| **Front Panel Express** (Seattle) | Schaeffer's US partner: same materials, UV print, same Designer software | as Schaeffer | as Schaeffer | US shipping; same process. |
| **LCSC front panels** (JLCPCB's sister) | anodised aluminium and digital printing; thickness range and the 1.5 mm option to confirm | DXF / PDF uploads; RGB / PANTONE colours accepted "with colour difference" | up to about 594 × 380 mm (the 514 mm panels fit) | Likely the cheapest for 29 panels. Its print minimum isn't published; plan on the bold-numeral variant if it is 0.15 mm. |
| A local CNC + UV-print shop | anything | DXF + PDF | — | Worth a quote for the first article: easier to iterate on the PV-cap and fader-slot fit. |

## Recommendation

1. **One strip panel first** (prototype), from whichever maker quotes lower for it. It settles three open checks at once:
   - the PV caps' 0.30 mm clearance in the Ø8.0 holes;
   - the fader slot and its fixings on a real PTB0143;
   - how the finest numerals print.
2. **Before printing**, measure the fader law: the dB scale is drawn from an assumed law (`panels/README.md`).
3. **Then the batch** of 28 more, with any hole or print adjustment carried back into `panel_layout.py`, so the
   drawings, the 3D model and the rails stay in step.

**Quotes need your accounts:** a Schaeffer price comes from its Designer software (a download) and an LCSC price from
an upload to its site, so I haven't fetched either.
