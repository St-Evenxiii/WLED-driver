from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

generate_schematic = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'Conn_01x19', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x19'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical', 'keywords':'connector', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='10',name='Pin_10',func=pin_types.PASSIVE,unit=1),
            Pin(num='11',name='Pin_11',func=pin_types.PASSIVE,unit=1),
            Pin(num='12',name='Pin_12',func=pin_types.PASSIVE,unit=1),
            Pin(num='13',name='Pin_13',func=pin_types.PASSIVE,unit=1),
            Pin(num='14',name='Pin_14',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='Pin_15',func=pin_types.PASSIVE,unit=1),
            Pin(num='16',name='Pin_16',func=pin_types.PASSIVE,unit=1),
            Pin(num='17',name='Pin_17',func=pin_types.PASSIVE,unit=1),
            Pin(num='18',name='Pin_18',func=pin_types.PASSIVE,unit=1),
            Pin(num='19',name='Pin_19',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Pin_4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='Pin_5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='Pin_6',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='Pin_7',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='Pin_8',func=pin_types.PASSIVE,unit=1),
            Pin(num='9',name='Pin_9',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'74LS125', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'74LS125'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':'TTL buffer 3State', 'description':'', 'datasheet':'http://www.ti.com/lit/gpn/sn74LS125', 'pins':[
            Pin(num='1',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='~',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='~',func=pin_types.TRISTATE,unit=1),
            Pin(num='4',name='~',func=pin_types.INPUT,unit=2),
            Pin(num='5',name='~',func=pin_types.INPUT,unit=2),
            Pin(num='6',name='~',func=pin_types.TRISTATE,unit=2),
            Pin(num='10',name='~',func=pin_types.INPUT,unit=3),
            Pin(num='8',name='~',func=pin_types.TRISTATE,unit=3),
            Pin(num='9',name='~',func=pin_types.INPUT,unit=3),
            Pin(num='11',name='~',func=pin_types.TRISTATE,unit=4),
            Pin(num='12',name='~',func=pin_types.INPUT,unit=4),
            Pin(num='13',name='~',func=pin_types.INPUT,unit=4),
            Pin(num='14',name='VCC',func=pin_types.PWRIN,unit=5),
            Pin(num='7',name='GND',func=pin_types.PWRIN,unit=5)], 'unit_defs':[{'label': 'uA', 'num': 1, 'pin_nums': ['3', '2', '1']},{'label': 'uB', 'num': 2, 'pin_nums': ['6', '5', '4']},{'label': 'uC', 'num': 3, 'pin_nums': ['9', '8', '10']},{'label': 'uD', 'num': 4, 'pin_nums': ['12', '11', '13']},{'label': 'uE', 'num': 5, 'pin_nums': ['7', '14']}] }),
        Part(**{ 'name':'Conn_01x02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x02'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', 'keywords':'connector', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_01x03', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_01x03'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal', 'keywords':'connector', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C_Polarized', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C_Polarized'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', 'keywords':'cap capacitor', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm', 'keywords':'cap capacitor', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'keywords':'R res resistor', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'1N5819', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'1N5819'}), 'ref_prefix':'D', 'fplist':['Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal'], 'footprint':'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', 'keywords':'diode Schottky', 'description':'', 'datasheet':'http://www.vishay.com/docs/88525/1n5817.pdf', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])