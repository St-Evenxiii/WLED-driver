# WLED ESP32-WROOM-32D driver for a 16x16 matrix

KiCad design files and a bring-up sketch for a carrier board that runs
[WLED](https://kno.wled.ge/) on a 16x16 5 V WS2812B matrix. An ESP32-WROOM-32D
38-pin DevKit plugs into the board.

## What's on the board

| Ref | Part | Notes |
|-----|------|-------|
| J1, J2 | 2x 1x19 female header, 2.54 mm | ESP32 38-pin DevKit, rows 25.4 mm (1.0") apart |
| U1 | **SN74HCT125N** (DIP-14) | 3.3 V GPIO16 to 5 V data. Must be **HCT**: 74LS/74HC parts won't reliably drive WS2812B from 3.3 V |
| R1 | 330 Ω axial | Series resistor at the driver output |
| C1 | 1000 µF, ≥10 V electrolytic, 10 mm dia. | Bulk cap across the LED supply |
| C2 | 100 nF ceramic | U1 decoupling |
| D1 | 1N5819 Schottky (DO-41) | +5V rail to DevKit 5V pin. Stops USB from trying to power the matrix |
| J3 | 2-pin 5.08 mm screw terminal | **Power in**: +5V, GND |
| J4 | 3-pin 5.08 mm screw terminal | **To matrix**: +5V, DIN, GND |
| H1–H4 | M3 mounting holes | |

Board size: 50 x 115 mm, 2 layers. All nets are routed. There are GND pours on
both layers, a +5V pour around the terminals, a copper keep-out under the ESP32
antenna, and a 15 x 15 mm logo area on the front silkscreen (above the antenna
end of the DevKit).

## Repository layout

```
pcb/
  generate_schematic.py   SKiDL source of truth -> wled_driver.net
  layout_board.py         netlist -> placed, routed, poured wled_driver.kicad_pcb
  check_board.py          DRC + netlist parity + design sanity checks
  netlist.py              small KiCad netlist reader used by the two scripts above
  wled_driver.kicad_pro / .kicad_pcb / .net
firmware/
  test_matrix/            Arduino sketch (folder name matches the .ino, as the IDE requires)
  tests/                  host-side tests: mock FastLED + unit tests, `make -C firmware/tests`
.github/workflows/ci.yml  runs all of the above on every push
```

## Testing

```sh
# Firmware logic (any machine with g++)
make -C firmware/tests

# PCB: DRC (with zone refill), netlist parity, sanity checks (needs KiCad's Python)
python3 pcb/check_board.py --report drc.rpt

# Regenerate from source (only if you change the design)
KICAD7_SYMBOL_DIR=/usr/share/kicad/symbols python3 pcb/generate_schematic.py   # needs: pip install skidl
python3 pcb/layout_board.py
```

Current results: ERC 0 errors / 0 warnings. DRC 0 errors and 0 unconnected
items. All 29 connected pads match the netlist. The only DRC warnings are
"library not in fp-lib-table", which happens when the check runs headless
without a KiCad library table.

## Using it

1. Open `pcb/wled_driver.kicad_pro` in KiCad 7, 8 or 9 and go to the PCB Editor.
   KiCad 8/9 will offer to upgrade the file format. Accepting is fine.
   There's no `.kicad_sch`, because the circuit is defined in `generate_schematic.py`.
   **Measure your DevKit first:** some 38-pin boards have rows 22.86 mm (0.9")
   apart, not 25.4 mm. If yours does, change `J2`'s x position in
   `layout_board.py` and regenerate.
2. Flash `firmware/test_matrix/test_matrix.ino` (board "ESP32 Dev Module",
   library FastLED). Open the Serial Monitor at 115200. The sketch shows:
   - corner markers (orientation and origin)
   - solid R/G/B (`COLOR_ORDER`)
   - a single pixel walking the chain (dead LEDs / joints)
   - row and column sweeps (`SERPENTINE`)
   - a rainbow
   - a current-limited full-white load test
3. Flash WLED and set: LED output **GPIO16**, WS2812B, 256 LEDs. Under
   *2D Configuration*, set a 16x16 matrix (serpentine for most panels).
   Leave **ABL (current limiter)** on, sized to your supply.

## Power notes

- A 16x16 WS2812B panel can draw ~15 A at full white. The J3→J4 path is a
  3 mm track inside a +5V pour, with GND poured on both layers. Plan on a few
  amps through the board on 1 oz copper (more with 2 oz). For higher current,
  inject power straight from the PSU into the matrix and use J4's +5V only as
  a local feed. Fuse the supply line in either case.
- Keep the WLED/FastLED current limit on (the sketch defaults to 2 A).
- With D1 fitted, the DevKit runs from the 5 V rail (about 4.7 V after the
  diode) or from USB, and USB never feeds the matrix.
- Mechanical: C1 is tall (~20 mm). It sits about 20 mm below the DevKit's USB
  connector. Check that your USB plug clears it, or lay C1 on its side.
