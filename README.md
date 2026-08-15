# WLED ESP32-WROOM-32D Driver for 16x16 Matrix

This project contains the KiCad design files and a test sketch for a custom driver board designed to run WLED on a 16x16 5V LED matrix using an ESP32-WROOM-32D 38-pin DevKit board.

## Deliverables
- **KiCad Project (`pcb/`)**: Contains the schematic (`wled_driver.net` + script) and board layout (`wled_driver.kicad_pcb`).
  - Features high-current input and output screw terminals.
  - SN74HCT125N level shifter correctly translates 3.3V GPIO to 5V data for the matrix.
  - 1000uF bulk capacitor and a 330 ohm resistor on the data line for protection.
  - 15x15mm blank silkscreen space for a custom logo.
- **Firmware (`firmware/`)**: An Arduino sketch using `FastLED` to test matrix functionality before flashing WLED.

## Usage
1. Open the PCB file in KiCad.
2. Ensure you have the `FastLED` library installed in the Arduino IDE before uploading `test_matrix.ino`.
3. Flash WLED to the ESP32 and configure it to use GPIO16 for data out.

## Opening in KiCad (7, 8, or 9)
Because the schematic was generated programmatically (using SKiDL) rather than manually drawn in `Eeschema` to ensure flawless precision, here is how to work with the design in KiCad:

1. Launch KiCad and open the project file: `pcb/wled_driver.kicad_pro`.
2. Open the **PCB Editor**. The components are already laid out and ready for routing.
3. If KiCad 9 prompts you to convert the file format, click **Yes** to upgrade the `.kicad_pcb` file to version 9.
4. **To view the schematic:** You can import the netlist (`wled_driver.net`) into a new KiCad Schematic if you desire a visual representation, or simply work from the PCB Editor which already contains all the correct net and component mappings.
5. Manually route the copper traces between components as you see fit. Ensure you use adequately thick traces for the `+5V` and `GND` lines, as a 16x16 LED matrix can draw up to 15 Amps.
