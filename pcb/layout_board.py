import pcbnew
import sys
import math

board = pcbnew.LoadBoard("wled_driver.kicad_pcb")

# KiCad 7/8 uses pcbnew.FromMM
def mm(val):
    return pcbnew.FromMM(val)

esp32_x = 100.0
esp32_y = 100.0

j1 = board.FindFootprintByReference("J1")
j2 = board.FindFootprintByReference("J2")

if j1 and j2:
    j1.SetPosition(pcbnew.VECTOR2I(mm(esp32_x - 12.7), mm(esp32_y)))
    j2.SetPosition(pcbnew.VECTOR2I(mm(esp32_x + 12.7), mm(esp32_y)))

u1 = board.FindFootprintByReference("U1")
if u1:
    u1.SetPosition(pcbnew.VECTOR2I(mm(esp32_x), mm(esp32_y + 35.0)))
    u1.SetOrientation(pcbnew.EDA_ANGLE(90.0, pcbnew.DEGREES_T))

j3 = board.FindFootprintByReference("J3")
j4 = board.FindFootprintByReference("J4")

if j3:
    j3.SetPosition(pcbnew.VECTOR2I(mm(esp32_x - 15.0), mm(esp32_y + 45.0)))
    j3.SetOrientation(pcbnew.EDA_ANGLE(180.0, pcbnew.DEGREES_T))

if j4:
    j4.SetPosition(pcbnew.VECTOR2I(mm(esp32_x + 15.0), mm(esp32_y + 45.0)))
    j4.SetOrientation(pcbnew.EDA_ANGLE(0.0, pcbnew.DEGREES_T))

c1 = board.FindFootprintByReference("C1")
if c1:
    c1.SetPosition(pcbnew.VECTOR2I(mm(esp32_x - 20.0), mm(esp32_y + 35.0)))

c2 = board.FindFootprintByReference("C2")
if c2:
    c2.SetPosition(pcbnew.VECTOR2I(mm(esp32_x - 5.0), mm(esp32_y + 30.0)))

r1 = board.FindFootprintByReference("R1")
if r1:
    r1.SetPosition(pcbnew.VECTOR2I(mm(esp32_x + 15.0), mm(esp32_y + 35.0)))

outline_points = [
    (esp32_x - 25, esp32_y - 25),
    (esp32_x + 25, esp32_y - 25),
    (esp32_x + 25, esp32_y + 55),
    (esp32_x - 25, esp32_y + 55),
]

for i in range(len(outline_points)):
    p1 = outline_points[i]
    p2 = outline_points[(i + 1) % len(outline_points)]

    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
    seg.SetEnd(pcbnew.VECTOR2I(mm(p2[0]), mm(p2[1])))
    seg.SetWidth(mm(0.1))
    board.Add(seg)

logo_text = pcbnew.PCB_TEXT(board)
logo_text.SetText("Logo Space (15x15)")
logo_text.SetPosition(pcbnew.VECTOR2I(mm(esp32_x), mm(esp32_y - 15)))
logo_text.SetLayer(pcbnew.F_SilkS)
board.Add(logo_text)

pcbnew.SaveBoard("wled_driver.kicad_pcb", board)
print("Board layout generated.")
