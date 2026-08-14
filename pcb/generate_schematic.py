import os
import sys
from skidl import *

set_default_tool('kicad8')

header_left = Part('Connector_Generic', 'Conn_01x19', footprint='Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical')
header_right = Part('Connector_Generic', 'Conn_01x19', footprint='Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical')

level_shifter = Part('74xx', '74LS125', footprint='Package_DIP:DIP-14_W7.62mm')

power_in = Part('Connector_Generic', 'Conn_01x02', footprint='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')
matrix_out = Part('Connector_Generic', 'Conn_01x03', footprint='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal')

bulk_cap = Part('Device', 'C_Polarized', footprint='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', value='1000uF')
bypass_cap = Part('Device', 'C', footprint='Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm', value='0.1uF')
data_resistor = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', value='330R')

v5 = Net('+5V')
v33 = Net('+3V3')
gnd = Net('GND')
data_3v3 = Net('DATA_3V3')
data_5v = Net('DATA_5V')
data_out = Net('DATA_OUT')

power_in[1] += v5
power_in[2] += gnd

matrix_out[1] += v5
matrix_out[2] += data_out
matrix_out[3] += gnd

bulk_cap[1] += v5
bulk_cap[2] += gnd

header_left[1] += v33 # 3V3
header_left[14] += gnd # GND
header_left[19] += v5  # 5V

header_right[1] += gnd # GND
header_right[7] += gnd # GND
header_right[12] += data_3v3 # GPIO16

# Level Shifter 74HCT125 (using 74LS125 footprint)
level_shifter['14'] += v5 # VCC
level_shifter['7'] += gnd # GND

bypass_cap[1] += v5
bypass_cap[2] += gnd

# Buffer 1
level_shifter['1'] += gnd # 1~OE (Active low enable)
level_shifter['2'] += data_3v3 # 1A (Input)
level_shifter['3'] += data_5v # 1Y (Output)

# Disable unused buffers by tying OE to 5V and A to GND
level_shifter['4'] += v5 # 2~OE
level_shifter['5'] += gnd # 2A
level_shifter['10'] += v5 # 3~OE
level_shifter['9'] += gnd # 3A
level_shifter['13'] += v5 # 4~OE
level_shifter['12'] += gnd # 4A

data_resistor[1] += data_5v
data_resistor[2] += data_out

ERC()
generate_netlist(file_='wled_driver.net')
