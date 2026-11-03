"""SKiDL description of the WLED 16x16 matrix driver.

Run from this directory to regenerate ``wled_driver.net``:

    KICAD7_SYMBOL_DIR=/usr/share/kicad/symbols python3 generate_schematic.py

Then run ``layout_board.py`` (KiCad's bundled Python) to rebuild the PCB and
``check_board.py`` to run DRC + netlist parity.

ESP32-WROOM-32D 38-pin DevKit header pinout (antenna end = pin 1):

    J1 (left)          J2 (right)
     1 3V3              1 GND
     2 EN               2 GPIO23
     3 GPIO36 (VP)      3 GPIO22
     4 GPIO39 (VN)      4 GPIO1  (TX0)
     5 GPIO34           5 GPIO3  (RX0)
     6 GPIO35           6 GPIO21
     7 GPIO32           7 GND
     8 GPIO33           8 GPIO19
     9 GPIO25           9 GPIO18
    10 GPIO26          10 GPIO5
    11 GPIO27          11 GPIO17
    12 GPIO14          12 GPIO16  <- LED data (WLED default on ESP32)
    13 GPIO12          13 GPIO4
    14 GND             14 GPIO0
    15 GPIO13          15 GPIO2
    16 GPIO9  (SD2)    16 GPIO15
    17 GPIO10 (SD3)    17 GPIO8  (SD1)
    18 GPIO11 (CMD)    18 GPIO7  (SD0)
    19 5V              19 GPIO6  (CLK)
"""

import os

from skidl import ERC, POWER, Net, Part, generate_netlist, set_default_tool

# SKiDL injects NC (the no-connect net) as a builtin; alias it for linters.
import builtins
NC = builtins.NC

HERE = os.path.dirname(os.path.abspath(__file__))

set_default_tool('kicad8')

SOCKET_FP = 'Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical'

header_left = Part('Connector_Generic', 'Conn_01x19', ref='J1', tag='J1',
                   value='ESP32_DevKit_L', footprint=SOCKET_FP)
header_right = Part('Connector_Generic', 'Conn_01x19', ref='J2', tag='J2',
                    value='ESP32_DevKit_R', footprint=SOCKET_FP)

# The KiCad 74xx library has no 74HCT125 symbol; 74LS125 has the identical
# pinout. The part fitted MUST be an HCT (TTL-level input, CMOS rail-to-rail
# output): an LS part only drives ~3.4 V high, which is below the WS2812B's
# 0.7*VDD = 3.5 V input threshold.
level_shifter = Part('74xx', '74LS125', ref='U1', tag='U1', value='74HCT125',
                     footprint='Package_DIP:DIP-14_W7.62mm')

power_in = Part('Connector_Generic', 'Conn_01x02', ref='J3', tag='J3', value='5V_IN',
                footprint='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')
matrix_out = Part('Connector_Generic', 'Conn_01x03', ref='J4', tag='J4', value='MATRIX_OUT',
                  footprint='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal')

bulk_cap = Part('Device', 'C_Polarized', ref='C1', tag='C1', value='1000uF/10V',
                footprint='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm')
bypass_cap = Part('Device', 'C', ref='C2', tag='C2', value='100nF',
                  footprint='Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm')
data_resistor = Part('Device', 'R', ref='R1', tag='R1', value='330R',
                     footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
# Schottky from the 5 V rail to the DevKit's 5V pin. Without it, plugging in
# USB with the PSU off tries to run the whole matrix through the DevKit's USB
# diode / the host's USB port.
esp_diode = Part('Diode', '1N5819', ref='D1', tag='D1', value='1N5819',
                 footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')

v5 = Net('+5V')
esp_5v = Net('ESP_5V')
gnd = Net('GND')
data_3v3 = Net('DATA_3V3')
data_5v = Net('DATA_5V')
data_out = Net('DATA_OUT')

# 5 V and GND are supplied externally through J3.
v5.drive = POWER
gnd.drive = POWER

power_in[1] += v5
power_in[2] += gnd

matrix_out[1] += v5
matrix_out[2] += data_out
matrix_out[3] += gnd

bulk_cap[1] += v5
bulk_cap[2] += gnd

esp_diode['A'] += v5
esp_diode['K'] += esp_5v

header_left[14] += gnd       # GND
header_left[19] += esp_5v    # 5V (VIN)

header_right[1] += gnd       # GND
header_right[7] += gnd       # GND
header_right[12] += data_3v3  # GPIO16

level_shifter['14'] += v5    # VCC
level_shifter['7'] += gnd    # GND

bypass_cap[1] += v5
bypass_cap[2] += gnd

# Buffer 1: always enabled, 3.3 V in -> 5 V out
level_shifter['1'] += gnd       # 1~OE (active low)
level_shifter['2'] += data_3v3  # 1A
level_shifter['3'] += data_5v   # 1Y

# Unused buffers: disabled (~OE high) with inputs tied low
level_shifter['4'] += v5    # 2~OE
level_shifter['5'] += gnd   # 2A
level_shifter['10'] += v5   # 3~OE
level_shifter['9'] += gnd   # 3A
level_shifter['13'] += v5   # 4~OE
level_shifter['12'] += gnd  # 4A

data_resistor[1] += data_5v
data_resistor[2] += data_out

# Mark intentionally unconnected pins so ERC only reports real problems.
for pin in range(1, 20):
    if pin not in (14, 19):
        header_left[pin] += NC
    if pin not in (1, 7, 12):
        header_right[pin] += NC
for pin in ('6', '8', '11'):  # outputs of the disabled buffers
    level_shifter[pin] += NC

if __name__ == '__main__':
    ERC()
    generate_netlist(file_=os.path.join(HERE, 'wled_driver.net'))
