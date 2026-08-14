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
