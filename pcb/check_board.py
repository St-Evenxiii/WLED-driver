"""Automated checks for wled_driver.kicad_pcb.

1. Netlist parity: every pad's net on the board matches wled_driver.net, and
   every footprint in the netlist is on the board.
2. Full KiCad DRC (with zone refill): fails on any error-severity violation
   or any unconnected item. Warnings are printed but do not fail.
3. Design sanity checks specific to this board (GPIO16 routing, level shifter
   part, high-current track width, logo area size).

Run with KiCad's Python:  python3 check_board.py [--report drc.rpt]
Exit status is non-zero if anything fails.
"""

import argparse
import collections
import os
import re
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from netlist import read_netlist  # noqa: E402

BOARD = os.path.join(HERE, 'wled_driver.kicad_pcb')
NETLIST = os.path.join(HERE, 'wled_driver.net')

failures = []


def check(cond, msg):
    print(('PASS  ' if cond else 'FAIL  ') + msg)
    if not cond:
        failures.append(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', help='where to write the DRC report')
    args = ap.parse_args()

    board = pcbnew.LoadBoard(BOARD)
    comps, nets = read_netlist(NETLIST)

    # ---- 1. netlist parity ------------------------------------------------
    expected = {}
    for name, nodes in nets.items():
        for ref, pad in nodes:
            expected[(ref, pad)] = name
    mismatches = []
    for ref, info in comps.items():
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            mismatches.append(f'{ref} missing from board')
            continue
        if fp.GetValue() != info['value']:
            mismatches.append(f'{ref} value {fp.GetValue()} != {info["value"]}')
        if fp.GetFPIDAsString() != info['footprint']:
            mismatches.append(f'{ref} footprint {fp.GetFPIDAsString()} != {info["footprint"]}')
        for p in fp.Pads():
            want = expected.get((ref, p.GetNumber()), '')
            if p.GetNetname() != want:
                mismatches.append(f'{ref}.{p.GetNumber()} net "{p.GetNetname()}" != "{want}"')
    for m in mismatches:
        print('      ' + m)
    check(not mismatches, f'netlist parity ({len(expected)} connected pads)')

    # ---- 2. DRC -----------------------------------------------------------
    report = args.report or os.path.join(tempfile.mkdtemp(), 'drc.rpt')
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.WriteDRCReport(board, report, pcbnew.EDA_UNITS_MILLIMETRES, True)
    text = open(report, encoding='utf-8').read()
    entries = re.findall(r'^\[(\w+)\]:.*?\n.*?Severity: (\w+)', text, re.M)
    by_sev = collections.defaultdict(collections.Counter)
    for kind, sev in entries:
        by_sev[sev][kind] += 1
    for sev in sorted(by_sev):
        for kind, n in sorted(by_sev[sev].items()):
            print(f'      DRC {sev:8s} {kind}: {n}')
    unconnected = int(re.search(r'Found (\d+) unconnected', text).group(1))
    errors = sum(by_sev['error'].values())
    check(errors == 0, f'DRC errors: {errors}  (report: {report})')
    check(unconnected == 0, f'unconnected items: {unconnected}')

    # ---- 3. design sanity -------------------------------------------------
    check(comps['U1']['value'].upper().startswith('74HCT'),
          'level shifter is an HCT part (LS cannot drive 5 V WS2812B input)')
    gpio16 = board.FindFootprintByReference('J2').FindPadByNumber('12')
    check(gpio16.GetNetname() == 'DATA_3V3', 'ESP32 GPIO16 (J2 pin 12) drives DATA_3V3')
    widest = max((pcbnew.ToMM(t.GetWidth()) for t in board.GetTracks()
                  if t.GetNetname() == '+5V'), default=0)
    check(widest >= 2.5, f'+5V backbone track width {widest:.1f} mm >= 2.5 mm')
    edge = board.GetBoardEdgesBoundingBox()
    w, h = pcbnew.ToMM(edge.GetWidth()), pcbnew.ToMM(edge.GetHeight())
    print(f'      board size {w:.1f} x {h:.1f} mm')
    logo = [d for d in board.GetDrawings()
            if d.GetLayer() == pcbnew.F_SilkS and isinstance(d, pcbnew.PCB_SHAPE)]
    xs = [pcbnew.ToMM(v) for d in logo for v in (d.GetStart().x, d.GetEnd().x)]
    ys = [pcbnew.ToMM(v) for d in logo for v in (d.GetStart().y, d.GetEnd().y)]
    check(logo and round(max(xs) - min(xs), 2) >= 15 and round(max(ys) - min(ys), 2) >= 15,
          '15x15 mm logo area outlined on F.SilkS')

    print()
    if failures:
        print(f'{len(failures)} check(s) failed')
        return 1
    print('All checks passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
