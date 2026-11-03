"""Build wled_driver.kicad_pcb from wled_driver.net.

Places every footprint, routes all signal/power tracks, adds GND / +5V copper
pours, mounting holes, an antenna keep-out, silkscreen labels and the 15x15 mm
logo area, then fills the zones and saves the board.

Run with the Python that ships with KiCad (it needs the ``pcbnew`` module):

    python3 layout_board.py

Tested with KiCad 7.0; the saved file opens in KiCad 7, 8 and 9.

Coordinates are in mm, KiCad convention (+y points down). The ESP32 DevKit
sits in J1/J2 with its antenna towards the top edge (pin 1) and its USB port
towards the bottom (pin 19).
"""

import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netlist import read_netlist  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NETLIST = os.path.join(HERE, 'wled_driver.net')
BOARD = os.path.join(HERE, 'wled_driver.kicad_pcb')


def footprint_dir():
    for var in ('KICAD9_FOOTPRINT_DIR', 'KICAD8_FOOTPRINT_DIR',
                'KICAD7_FOOTPRINT_DIR', 'KICAD6_FOOTPRINT_DIR'):
        if os.environ.get(var):
            return os.environ[var]
    for cand in ('/usr/share/kicad/footprints',
                 '/usr/local/share/kicad/footprints',
                 '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints',
                 r'C:\Program Files\KiCad\9.0\share\kicad\footprints',
                 r'C:\Program Files\KiCad\8.0\share\kicad\footprints',
                 r'C:\Program Files\KiCad\7.0\share\kicad\footprints'):
        if os.path.isdir(cand):
            return cand
    sys.exit('KiCad footprint library not found; set KICAD7_FOOTPRINT_DIR')


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


board = pcbnew.BOARD()
FP_DIR = footprint_dir()


def load_fp(lib_fp):
    lib, name = lib_fp.split(':', 1)
    fp = pcbnew.FootprintLoad(os.path.join(FP_DIR, lib + '.pretty'), name)
    if fp is None:
        sys.exit(f'Footprint {lib_fp} not found in {FP_DIR}')
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def place(ref, x, y, rot=0.0):
    fp = board.FindFootprintByReference(ref)
    fp.SetPosition(pt(x, y))
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    return fp


def pad_pos(ref, pad):
    p = board.FindFootprintByReference(ref).FindPadByNumber(pad).GetPosition()
    return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)


def track(net, points, width, layer=pcbnew.F_Cu):
    """Add a polyline of track segments. Points may be (x, y) or (ref, pad)."""
    xy = [pad_pos(*p) if isinstance(p[0], str) else p for p in points]
    for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pt(x1, y1))
        t.SetEnd(pt(x2, y2))
        t.SetWidth(mm(width))
        t.SetLayer(layer)
        t.SetNet(board.FindNet(net))
        board.Add(t)


def polygon(points):
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in points:
        chain.Append(mm(x), mm(y))
    chain.SetClosed(True)
    return chain


def zone(net, layer, points, priority=0, name=''):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    if net:
        z.SetNet(board.FindNet(net))
    z.Outline().AddOutline(polygon(points))
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetThermalReliefGap(mm(0.4))
    z.SetThermalReliefSpokeWidth(mm(0.6))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    if name:
        z.SetZoneName(name)
    board.Add(z)
    return z


def keepout(points, name):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(layers)
    z.Outline().AddOutline(polygon(points))
    z.SetZoneName(name)
    board.Add(z)


def line(layer, x1, y1, x2, y2, width=0.12):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetStart(pt(x1, y1))
    s.SetEnd(pt(x2, y2))
    s.SetWidth(mm(width))
    board.Add(s)


def rect(layer, x1, y1, x2, y2, width=0.12):
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
                 ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        line(layer, a[0], a[1], b[0], b[1], width)


def text(msg, x, y, size=1.0, layer=pcbnew.F_SilkS, thickness=0.15):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(msg)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thickness))
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


# --------------------------------------------------------------------------
# Load parts and nets from the netlist
# --------------------------------------------------------------------------
comps, nets = read_netlist(NETLIST)

for name in nets:
    board.Add(pcbnew.NETINFO_ITEM(board, name))

for ref, info in sorted(comps.items()):
    fp = load_fp(info['footprint'])
    fp.SetReference(ref)
    fp.SetValue(info['value'])
    board.Add(fp)

for name, nodes in nets.items():
    net = board.FindNet(name)
    for ref, pad in nodes:
        fp = board.FindFootprintByReference(ref)
        for p in fp.Pads():
            if p.GetNumber() == pad:
                p.SetNet(net)

# Design rules (JLCPCB/PCBWay standard 2-layer capabilities are well above these).
ds = board.GetDesignSettings()
ds.m_MinClearance = mm(0.2)
ds.m_TrackMinWidth = mm(0.2)
ds.m_CopperEdgeClearance = mm(0.5)

# --------------------------------------------------------------------------
# Board outline: 50 x 115 mm
# --------------------------------------------------------------------------
X0, X1, Y0, Y1 = 75.0, 125.0, 75.0, 190.0
rect(pcbnew.Edge_Cuts, X0, Y0, X1, Y1, 0.1)

# --------------------------------------------------------------------------
# Placement
# --------------------------------------------------------------------------
# ESP32 38-pin DevKit, 25.4 mm (1.0") row spacing, pin 1 = antenna end.
place('J1', 87.3, 100.0)
place('J2', 112.7, 100.0)

# Level shifter rotated 270: pins 1..7 run right->left on the upper row
# (y=156), pins 14..8 right->left on the lower row (y=163.62).
place('U1', 105.0, 156.0, 270)
place('C2', 108.2, 163.62, 270)    # decoupling right next to VCC (pin 14)
place('R1', 113.0, 159.81, 270)    # series resistor at the driver output
place('D1', 80.0, 152.0, 270)      # cathode (pad 1) up towards J1 pin 19
place('C1', 88.0, 171.0)           # bulk cap between the terminals

# Screw terminals on the bottom edge, wire entry facing off the board.
place('J3', 86.0, 184.0)           # [ +5V | GND ] power in
place('J4', 100.0, 184.0)          # [ +5V | DATA | GND ] to matrix

# Mounting holes (M3), not in the netlist.
for i, (hx, hy) in enumerate(((79.0, 79.0), (121.0, 79.0),
                              (79.0, 186.0), (121.0, 186.0)), start=1):
    h = load_fp('MountingHole:MountingHole_3.2mm_M3')
    h.SetReference(f'H{i}')
    h.SetValue('M3')
    h.SetPosition(pt(hx, hy))
    h.Reference().SetVisible(False)
    board.Add(h)

# --------------------------------------------------------------------------
# Routing (F.Cu); GND is carried by the pours.
# --------------------------------------------------------------------------
SIG = 0.4

# GPIO16 -> 74HCT125 1A, kept away from the ESP header pins.
track('DATA_3V3', [('J2', '12'), (117.0, 127.94), (117.0, 152.0),
                   (102.46, 152.0), ('U1', '2')], SIG)
# 1Y -> R1: drop between the IC rows and run right.
track('DATA_5V', [('U1', '3'), (99.92, 159.81), ('R1', '1')], SIG)
# R1 -> matrix data terminal.
track('DATA_OUT', [('R1', '2'), (113.0, 174.0), (105.08, 174.0),
                   ('J4', '2')], SIG)

# ESP 5V feed through the Schottky.
track('ESP_5V', [('J1', '19'), (87.3, 149.0), (80.0, 149.0), ('D1', '1')], 1.0)
track('+5V', [('D1', '2'), (80.0, 167.0)], 1.0)

# 74HCT125 supply and disable straps.
track('+5V', [('U1', '14'), ('C2', '1')], 0.8)
track('+5V', [('U1', '14'), (105.0, 167.0), (94.84, 167.0), ('U1', '10')], 0.8)
track('+5V', [('U1', '13'), (102.46, 167.0)], 0.6)
track('+5V', [('U1', '4'), (97.38, 159.81), (94.84, 159.81), ('U1', '10')], 0.5)

# High-current path J3 -> J4 on both copper layers is handled by the +5V
# pour on F.Cu; add a fat track as a backbone as well.
track('+5V', [('J3', '1'), (86.0, 179.5), (100.0, 179.5), ('J4', '1')], 3.0)
track('+5V', [('C1', '1'), (86.0, 171.0), (86.0, 179.5)], 2.0)

# --------------------------------------------------------------------------
# Copper pours
# --------------------------------------------------------------------------
outline = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
zone('GND', pcbnew.B_Cu, outline, priority=0, name='GND_bottom')
zone('GND', pcbnew.F_Cu, outline, priority=0, name='GND_top')
# +5V power island around the terminals, bulk cap and diode.
zone('+5V', pcbnew.F_Cu, [(76.0, 158.0), (87.0, 158.0), (87.0, 165.6),
                          (103.0, 165.6), (103.0, 189.0), (76.0, 189.0)],
     priority=1, name='+5V_top')

# No copper under the ESP32-WROOM antenna (it overhangs pin 1 by ~7 mm).
keepout([(84.0, Y0), (116.0, Y0), (116.0, 98.0), (84.0, 98.0)], 'ANTENNA')

# Solid (non-thermal) connections on the high-current terminal pins.
for ref in ('J3', 'J4'):
    for p in board.FindFootprintByReference(ref).Pads():
        if p.GetNetname() in ('+5V', 'GND'):
            p.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

# --------------------------------------------------------------------------
# Silkscreen
# --------------------------------------------------------------------------
# 15 x 15 mm logo area, centred under the antenna keep-out (bare FR4).
rect(pcbnew.F_SilkS, 92.5, 77.5, 107.5, 92.5, 0.15)
text('LOGO', 100.0, 85.0, 1.5)
text('ANTENNA', 100.0, 95.5, 0.8, thickness=0.12)

text('WLED 16x16 DRIVER', 100.0, 149.0, 1.0)
text('USB', 100.0, 146.5, 0.8, thickness=0.12)
text('GPIO16', 120.6, 127.94, 0.8, thickness=0.12)

# Terminal labels, just above the terminal block bodies.
for label, x in (('+5V', 86.0), ('GND', 91.08), ('+5V', 100.0),
                 ('DIN', 105.08), ('GND', 110.16)):
    text(label, x, 177.6, 0.9)

text('WLED DRIVER', 100.0, 118.0, 1.2, layer=pcbnew.B_SilkS)
text('ESP32-WROOM-32D', 100.0, 121.0, 1.0, layer=pcbnew.B_SilkS)
text('16x16 WS2812B 5V', 100.0, 123.5, 1.0, layer=pcbnew.B_SilkS)

# Keep reference designators readable and off pads.
ref_pos = {'J1': (84.3, 100.0, 90), 'J2': (115.7, 100.0, 90),
           'U1': (97.4, 153.6, 0), 'C2': (110.6, 166.1, 90),
           'R1': (115.4, 164.9, 90), 'D1': (77.6, 157.1, 90),
           'C1': (82.0, 171.0, 90), 'J3': (95.5, 184.0, 90),
           'J4': (117.0, 181.0, 0)}
for ref, (x, y, r) in ref_pos.items():
    t = board.FindFootprintByReference(ref).Reference()
    t.SetPosition(pt(x, y))
    t.SetTextAngle(pcbnew.EDA_ANGLE(r, pcbnew.DEGREES_T))
    t.SetTextSize(pcbnew.VECTOR2I(mm(0.9), mm(0.9)))
    t.SetTextThickness(mm(0.13))

# --------------------------------------------------------------------------
# Fill and save
# --------------------------------------------------------------------------
board.SetFileName(BOARD)
pcbnew.SaveBoard(BOARD, board)

# A BOARD() built in memory has no project attached and the zone filler needs
# one, so reload from disk before filling.
board = pcbnew.LoadBoard(BOARD)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(BOARD, board)
print(f'Board written to {BOARD}')
