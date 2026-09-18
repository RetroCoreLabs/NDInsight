"""
Educational cutaway diagrams of the Norsk Data cabinets.

Each function builds one cabinet from the facts in the matching file in ../ :
positions come from the nutclip hole numbers and parts lists in ND's Book 2 assembly
drawings, outer sizes from the product sheets. Where a drawing gives no position, the
layout follows the drawing's isometric and the caption says so.

Run:  python draw_cabinets.py            (all)
      python draw_cabinets.py nd5000     (one, by key)
Writes <key>.svg and <key>.png next to this file.
"""

import os
import sys

from cutaway import (Drawing, Box, card_slots, fans, louvres, fins, dots, dsub_rows,
                     floppy, streamer, disk_front, op_panel, label, hatch, rect,
                     holes_column, samson_edge, set_palette)

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------------
# Large 11-module cabinet helpers
# ---------------------------------------------------------------------------------

LARGE_H = 169.0
PLINTH = 8.0
ROOF = 164.0


def hole(n):
    """Height in cm of nutclip hole n on the 1 (top) to 66 (bottom) grid. The grid is
    spread over the inside height; the drawings give hole numbers, not lengths."""
    return 162.0 - (n - 1) * (150.0 / 65.0)


def large_shell(d, W, D, roof_cut_x=30.0, roof_cut_y=62.0, front_trim=True):
    """Frame, base, far walls and a partly removed roof of the 11-module cabinet."""
    # plinth, recessed
    d.add(Box(1.5, 2.5, 0, W - 1.5, D - 1.0, PLINTH, "brown"))
    # floor plate
    d.add(Box(0, 0, PLINTH, W, D, PLINTH + 1.0, "shellin", faces="t"))
    # right wall, seen from inside
    d.add(Box(W - 2.5, 0, PLINTH, W, D, ROOF, "shell",
              side=[holes_column(3.0, 4.0, ROOF - PLINTH - 4.0), holes_column(D - 3.0, 4.0, ROOF - PLINTH - 4.0)]))
    # back wall
    d.add(Box(0, D - 2.5, PLINTH, W - 2.5, D, ROOF, "shellin", faces="f"))
    # rear left post; the front left post is left out so it does not hide the crates
    d.add(Box(0, D - 2.5, PLINTH, 2.5, D, ROOF, "frame",
              side=[holes_column(1.25, 4.0, ROOF - PLINTH - 4.0)]))
    # roof, cut away over the front left
    d.add(Box(roof_cut_x, 0, ROOF, W, D, ROOF + 4.5, "shell"))
    d.add(Box(0, roof_cut_y, ROOF, roof_cut_x, D, ROOF + 4.5, "shell"))
    d.cut_line([(roof_cut_x, 0, ROOF + 4.5), (roof_cut_x, roof_cut_y, ROOF + 4.5),
                (0, roof_cut_y, ROOF + 4.5)])
    # chamfered moulding edge down the right of the front
    if front_trim:
        d.add(Box(W - 2.5, -1.2, PLINTH, W, 0, ROOF, "brown", faces="fs"))


# ---------------------------------------------------------------------------------
# ND-5000 large cabinet, Book 2 chapters 16 and 17
# ---------------------------------------------------------------------------------

def nd5000_large():
    set_palette("nd5000brown")
    W, D = 60.0, 95.0
    d = Drawing("Norsk Data ND-5000 large cabinet",
                "ND-5200 to ND-5900 and ES Model L   |   internal name MAXSON   |   169 x 60 x 95 cm")
    large_shell(d, W, D)

    x0, x1 = 3.5, W - 3.0

    # --- top rear: power crate, supplies slide in from the rear -------------------
    pz0, pz1 = hole(12), hole(1) + 1.0
    d.add(Box(6, 55, pz0, 54, 90, pz1, "galv",
              side=[fins(22, 1.5, 16, 2.0, pz1 - pz0 - 2.0, "#8a8d90"),
                    rect(17.5, 2.0, 8, pz1 - pz0 - 4.0, "#bfc3c6", "#6f757a", 0.1),
                    rect(27, 2.0, 7, pz1 - pz0 - 4.0, "#bfc3c6", "#6f757a", 0.1),
                    label(2.0, pz1 - pz0 - 2.4, "DC110", 1.3, "#1b1b1b", "bold"),
                    label(17.8, pz1 - pz0 - 2.4, "DC200", 1.1, "#1b1b1b", "bold"),
                    label(27.3, pz1 - pz0 - 2.4, "DC300", 1.1, "#1b1b1b", "bold")]))

    # --- top front: drive rack ----------------------------------------------------
    rz0, rz1 = hole(13), hole(2)
    d.add(Box(x0, 0.5, rz0, x1, 40, rz1, "dark",
              front=[op_panel(2.5, 1.2, 34, 4.2, buttons=8),
                     floppy(2.5, 7.5, 16, 6),
                     disk_front(21, 7.5, 16, 6),
                     label(40.0, 12.0, "ND", 2.2, "#e9dfc7", "bold"),
                     label(40.0, 9.4, "Norsk Data", 1.2, "#e9dfc7")],
              top=[dots(8, 4, 4, 50, 6, 36, r=0.9, colour="#1d1a17")]))

    # blind strip above the upper crate
    d.add(Box(x0, 0.5, hole(16) + 1.2, x1, 3, hole(16) + 3.2, "brown"))

    # --- upper crate: ND-5000 MF-bus, holes 16-31 ---------------------------------
    uz0, uz1 = hole(31) + 2.0, hole(16) + 1.0

    def mf_pattern(i):
        p = i + 1
        if p in (1, 2):
            return "blue"
        if p in (3, 4):
            return "ram"
        if 20 <= p <= 23:
            return "cpu"
        if p in (9, 14, 19):
            return "ram"
        return "empty"

    d.add(Box(x0, 1.0, uz0, x1, 50, uz1, "steel",
              front=[card_slots(24, 1.5, x1 - x0 - 1.5, 1.0, uz1 - uz0 - 3.0, fill_pattern=mf_pattern),
                     samson_edge(1.5 + 19 * (x1 - x0 - 3.0) / 24, 1.5 + 23 * (x1 - x0 - 3.0) / 24, 1.9, uz1 - uz0 - 3.9)]))
    # MF-bus backplane PCB 5337, five connector rows
    d.add(Box(x0, 50, uz0, x1, 52, uz1, "pcb", side=[rect(0.3, 2, 1.4, uz1 - uz0 - 4, "#c9b458", opacity=0.6)]))
    # eight-fan tray and air filter under it
    d.add(Box(x0, 1.0, uz0 - 7.0, x1, 48, uz0, "dark",
              front=[louvres(4, 2, x1 - x0 - 2, 1, 6, "#141210")]))
    d.add(Box(x0, 1.0, uz0 - 9.5, x1, 48, uz0 - 7.0, "filter",
              front=[hatch(1, x1 - x0 - 1, 0.4, 2.1, "#9a9a8e", 40)]))
    # --- lower crate: ND-100, holes 38-60 -----------------------------------------
    lz0, lz1 = hole(52), hole(38)

    def n100_pattern(i):
        p = i + 1
        if p == 1:
            return "gold"
        if p in (4, 5, 8, 9, 10, 11, 12, 13, 14):
            return "card"
        if p in (15, 16):
            return "blue"
        return "empty"

    d.add(Box(x0, 1.0, lz0, x1, 44, lz1, "steel",
              front=[card_slots(22, 1.5, x1 - x0 - 1.5, 1.0, lz1 - lz0 - 3.0, fill_pattern=n100_pattern)]))
    d.add(Box(x0, 44, lz0, x1, 46, lz1, "pcb"))
    d.add(Box(x0, 1.0, lz0 - 7.0, x1, 42, lz0, "dark",
              front=[louvres(4, 2, x1 - x0 - 2, 1, 6, "#141210")]))
    d.add(Box(x0, 1.0, lz0 - 9.5, x1, 42, lz0 - 7.0, "filter",
              front=[hatch(1, x1 - x0 - 1, 0.4, 2.1, "#9a9a8e", 40)]))

    # rear of the lower crate: plug panels left and right
    for a, b in ((4.5, 29.5), (30.0, 55.0)):
        d.add(Box(a, 89.5, hole(53), b, 91.0, hole(39), "galv",
                  front=[dsub_rows(1.5, b - a - 1.5, 2.0, hole(39) - hole(53) - 2.0, 7, 2),
                         rect(b - a - 3.2, 12.0, 2.2, 5.0, "#6f6a5e", rx=1.0)]))

    # bus bar I down the rear centre, bus bar L at the top
    d.add(Box(28, 86.5, lz0, 32, 88.5, pz0, "copper"))
    d.add(Box(28, 86.5, pz0, 32, 90, pz0 + 2.5, "copper"))

    # ribbon bundle up the rear left post to the drive rack
    d.add(Box(4.0, 84.0, lz0 + 4, 6.5, 85.8, rz1 - 1, "blue"))
    d.add(Box(4.0, 38.0, rz1 - 3, 6.5, 85.8, rz1 - 1, "blue", faces="t"))

    # --- floor: AC distribution box, ground rail ----------------------------------
    az0, az1 = PLINTH + 1.0, hole(65) + 1.0
    d.add(Box(x0, 0.5, az0, x1, 58, az1, "galv",
              front=[label(2.0, 1.4, "230V AC LINE", 1.6, "#b3261e", "bold"),
                     rect(34, 2.0, 14, 1.2, "#6f6a5e", rx=0.6)]))
    d.add(Box(x0, 86, az0, x1, 89, az0 + 3.0, "copper"))

    # --- roof fans ----------------------------------------------------------------
    d.add(Box(33, 6, ROOF + 4.5, W - 2, 42, ROOF + 10, "shell",
              top=[fans(1, 2, 2, 23, 3, 33, rmul=0.44)]))
    d.add(Box(6, 66, ROOF + 4.5, W - 2, 92, ROOF + 10, "shell",
              top=[fans(1, 3, 2, 50, 2, 24, rmul=0.44)]))

    # --- callouts: anchors only on parts visible in this view --------------------
    d.callout("Top fan units, front and rear", (45, 24, ROOF + 10), "R")
    d.callout("Power crate: DC110 5V/120A,|DC200 5V/200A, DC300 standby 50A", (6, 72, pz1 - 8))
    d.callout("Drive rack: 5.25\" floppy|and SCSI disk bay", (12, 0.5, rz0 + 10))
    d.callout("Operator panel", (30, 0.5, rz0 + 3))
    d.callout("Ribbon cables up to the drive rack", (4.0, 84, lz1 + 40))
    d.callout("ND-5000 MF-bus crate,|24 positions, holes 16-31", (26, 1.0, uz1 - 5))
    d.callout("MF-bus controller PCB 5465|and ND-100 port PCB 5155", (x0 + 2.5, 1.0, uz0 + 10))
    d.callout("ND-5000 CPU, type 3,|positions 20-23", (x0 + 45, 1.0, uz0 + 14))
    d.callout("MF-bus backplane PCB 5337", (x0, 51, uz0 + 18))
    d.callout("Eight-fan tray, blows up", (40, 1.0, uz0 - 3.5))
    d.callout("Air filter", (15, 1.0, uz0 - 8.3))
    d.callout("Rear plug panels, left and right", (6, 89.5, hole(47)))
    d.callout("ND-100 crate,|22 positions, holes 38-52", (26, 1.0, lz1 - 5))
    d.callout("ND-100 CPU in position 1", (x0 + 2.0, 1.0, lz0 + 10))
    d.callout("Six-fan tray, blows up", (40, 1.0, lz0 - 3.5))
    d.callout("Ground rail", (8, 86, az0 + 3))
    d.callout("AC distribution box,|230 V AC line", (30, 0.5, az1 - 3))
    d.callout("Chamfered front moulding", (W - 1.2, -1.2, 40))

    d.note("Cutaway: left side panel, front cover plates and the front of the roof removed. "
           "Heights from the nutclip hole numbers in ND Book 2 chapter 16; outer size from the ND-5700/5800/5900 product sheet.")
    d.note("Drawn schematic, not to exact scale. Sources: Book 2 ch. 16 and 17 (ND-B2C16.pdf, ND-B2C17.pdf); "
           "ND-05.020 Hardware Description; ND-SID001 sales document.")
    d.note("Colour: taupe brown, from a photograph of an ND-5800 at Telemuseet and ND-SID001's \"brown/beige cabinet\". Samson CPU edge drawn from photographs of assembly 320003.")
    return d


# ---------------------------------------------------------------------------------
# Shared small helpers
# ---------------------------------------------------------------------------------

def card_block_side(n_chips=6):
    """Side face of a block of vertical cards: the outermost card face."""
    def d(fc):
        out = ['<rect x="0.6" y="0.8" width="%.3f" height="%.3f" fill="#3B6236" stroke="#1c331a" stroke-width="0.08"/>' % (
            fc.w - 1.2, fc.h - 1.6)]
        for i in range(n_chips):
            for j in range(3):
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#1f1f1f"/>' % (
                    2 + i * (fc.w - 4) / n_chips, 3 + j * (fc.h - 6) / 3, (fc.w - 4) / n_chips * 0.55, (fc.h - 6) / 3 * 0.4))
        out.append('<rect x="0.6" y="%.3f" width="%.3f" height="1.2" fill="#b8a15a"/>' % (fc.h * 0.02, fc.w - 1.2))
        return "\n".join(out)
    return d


def top_card_edges(n, colour="#2f512c", gap="#1d1a17"):
    """Top face of a block of vertical cards whose planes run along y: n stripes in u."""
    def d(fc):
        out = ['<rect x="0" y="0" width="%.3f" height="%.3f" fill="%s"/>' % (fc.w, fc.h, gap)]
        step = fc.w / n
        for i in range(n):
            out.append('<rect x="%.3f" y="0.4" width="%.3f" height="%.3f" fill="%s"/>' % (
                i * step + step * 0.3, step * 0.4, fc.h - 0.8, colour))
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="1.4" fill="#EFE3C2"/>' % (
                i * step + step * 0.2, fc.h - 2.0, step * 0.6))
        return "\n".join(out)
    return d


def top_card_edges_v(n, colour="#2f512c", gap="#1d1a17"):
    """Top face of cards whose planes run along x: n stripes in v."""
    def d(fc):
        out = ['<rect x="0" y="0" width="%.3f" height="%.3f" fill="%s"/>' % (fc.w, fc.h, gap)]
        step = fc.h / n
        for i in range(n):
            out.append('<rect x="0.4" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>' % (
                i * step + step * 0.3, fc.w - 0.8, step * 0.4, colour))
        return "\n".join(out)
    return d


def backwiring_bands(rows, cols, colour="#c9b458"):
    def d(fc):
        out = []
        for r in range(rows):
            for c in range(cols):
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s" opacity="0.75"/>' % (
                    1 + c * (fc.w - 2) / cols + 0.2, 1 + r * (fc.h - 2) / rows + 0.4,
                    (fc.w - 2) / cols * 0.5, (fc.h - 2) / rows * 0.7, colour))
        return "\n".join(out)
    return d


def cabinet_closed_front(W):
    """Front face of a closed 11-module cabinet: floppy, operator panel, blind panels."""
    decos = [floppy(6, 128, 20, 8), op_panel(4, 116, W - 12, 6, buttons=8),
             label(6, 150, "ND", 3.0, "#e9dfc7", "bold"), label(15, 150, "Norsk Data", 2.0, "#e9dfc7")]
    for k in range(4):
        decos.append(rect(5, 92 - k * 22, W - 13, 18, "#6d4a31", "#3a2618", 0.15, rx=0.6))
    decos.append(louvres(10, 6, W - 10, 8, 20, "#3a2618"))
    return decos


# ---------------------------------------------------------------------------------
# ND-500 in one cabinet, Book 2 chapter 12
# ---------------------------------------------------------------------------------

def nd500_one():
    set_palette("nd500dark")
    W, D = 60.0, 91.0
    d = Drawing("Norsk Data ND-500 in one cabinet, model 11",
                "ND-520, ND-540, ND-505/CX, ND-510/CX and ND-500/CX Model 21   |   169 x 60 x 91 cm")
    large_shell(d, W, D, roof_cut_x=30, roof_cut_y=58)
    x0, x1 = 3.5, W - 3.0

    # floppy box at hole 3
    d.add(Box(x0, 0.5, hole(5), x1, 36, hole(2), "dark",
              front=[floppy(3, 1.5, 18, 5.5), label(36, 3.2, "ND", 2.0, "#e9dfc7", "bold"),
                     label(42, 3.2, "Norsk Data", 1.2, "#e9dfc7")]))
    # drive rack slides at holes 5-7
    for xx in (x0, x1 - 1.2):
        d.add(Box(xx, 1, hole(7), xx + 1.2, 86, hole(7) + 1.2, "steel"))
    # operator panel strip at holes 13-15
    d.add(Box(x0, 0, hole(15), x1, 5, hole(13), "dark",
              front=[op_panel(1, 0.6, x1 - x0 - 2, hole(13) - hole(15) - 1.2, buttons=10)]))
    # power supply tray on slides at holes 16-18, full depth
    pz0, pz1 = hole(24), hole(17)
    d.add(Box(5, 8, pz0, 55, 86, pz1, "galv",
              front=[fins(18, 1, 22, 1.5, pz1 - pz0 - 1.5), fins(12, 24, 38, 1.5, pz1 - pz0 - 1.5),
                     rect(40, 1.5, 9, pz1 - pz0 - 3, "#bfc3c6", "#6f757a", 0.1),
                     label(40.5, pz1 - pz0 - 3.0, "EMP 325", 1.0, "#1b1b1b", "bold")],
              top=[fans(1, 2, 30, 50, 30, 60, rmul=0.4)]))
    # strain relief angle about 108 cm up
    d.add(Box(3.5, 10, 106.5, 5.0, 84, 108, "steel"))

    # ND-100 crate, 24 positions, front, hinged at holes 46-48
    cz0, cz1 = hole(46), hole(25)

    def n100(i):
        p = i + 1
        return {1: "gold", 3: "card", 4: "card", 5: "#9c3d2e", 6: "card", 7: "card", 8: "card",
                9: "card", 10: "card", 14: "ram", 15: "blue", 17: "blue", 18: "card", 19: "card",
                20: "ram"}.get(p, "empty")

    d.add(Box(x0, 1, cz0, x1, 40, cz1, "steel",
              front=[card_slots(24, 1.5, x1 - x0 - 1.5, 1.0, cz1 - cz0 - 3.0, fill_pattern=n100)]))
    d.add(Box(x0, 40, cz0, x1, 42, cz1, "pcb"))
    d.add(Box(x0, 1, cz0 - 7, x1, 38, cz0, "dark", front=[louvres(4, 2, x1 - x0 - 2, 1, 6, "#141210")]))

    # ND-500 crate, 27 positions, lower rear. Position and orientation from the isometric.
    nz0, nz1 = hole(62) + 3, hole(47) - 1
    d.add(Box(x0, 44, nz0, x1, 84, nz1, "steel",
              front=[backwiring_bands(4, 9), label(1.0, nz1 - nz0 - 2.0, "A", 1.4, "#fff", "bold"),
                     label(1.0, (nz1 - nz0) * 0.55, "B", 1.4, "#fff", "bold"),
                     label(1.0, (nz1 - nz0) * 0.32, "C", 1.4, "#fff", "bold"),
                     label(1.0, (nz1 - nz0) * 0.08, "D", 1.4, "#fff", "bold")],
              side=[card_block_side(8)]))
    d.add(Box(x0, 44, nz0 - 6, x1, 84, nz0, "dark"))

    # plug panel frame, bottom rear; 230 V power panel, bottom front; ground rail
    d.add(Box(x0, 86, PLINTH + 4, x1, 88, hole(56), "galv",
              front=[dsub_rows(2, x1 - x0 - 2, 1, hole(56) - PLINTH - 5, 3, 3)]))
    d.add(Box(x0, 0.5, PLINTH + 1, x1, 40, hole(63), "galv",
              front=[label(2.0, 1.2, "230 V", 1.6, "#b3261e", "bold"), rect(30, 1.6, 16, 1.2, "#6f6a5e", rx=0.6)]))
    d.add(Box(x0, 84.5, PLINTH + 1, x1, 86, PLINTH + 3.5, "copper"))

    d.add(Box(33, 6, ROOF + 4.5, W - 2, 40, ROOF + 10, "shell", top=[fans(1, 2, 2, 23, 3, 31, rmul=0.44)]))
    d.add(Box(6, 62, ROOF + 4.5, W - 2, 88, ROOF + 10, "shell", top=[fans(1, 3, 2, 50, 2, 24, rmul=0.44)]))

    d.callout("Top fan assemblies", (45, 22, ROOF + 10))
    d.callout("5.25\" floppy box, hole 3", (14, 0.5, hole(3) - 1))
    d.callout("Drive rack slides, holes 5-7", (x0, 60, hole(7) + 1.2))
    d.callout("Operator panel, holes 13-15", (40, 0, hole(14)))
    d.callout("Power supply tray on slides:|EMP 325 control, SMP modules", (5, 60, pz1 - 3))
    d.callout("Strain relief angle,|about 108 cm up", (3.5, 70, 107))
    d.callout("ND-100 crate, 24 positions,|hinged at holes 46-48", (26, 1, cz1 - 5))
    d.callout("ND-100 CPU, position 1", (x0 + 2.0, 1, cz0 + 12))
    d.callout("ND-500 interface PCB 3022,|position 5", (x0 + 10.5, 1, cz0 + 18))
    d.callout("Six-fan tray", (40, 1, cz0 - 3.5))
    d.callout("ND-500 crate, 27 positions:|7-13 ND-500 CPU, 1-6 MPM 5", (x0, 64, (nz0 + nz1) / 2))
    d.callout("ND-500 backwiring A, B, C, D", (12, 44, nz0 + 3))
    d.callout("Plug panel frame, rear", (x0, 86, hole(60)))
    d.callout("230 V power panel, holes 63-65", (30, 0.5, hole(64)))
    d.callout("Ground rail, hole 66", (x0, 85, PLINTH + 2.5))

    d.note("Cutaway: left side panel, front cover plates and the front of the roof removed. Heights from the nutclip hole "
           "numbers in ND Book 2 chapter 12; outer size from the ND-520/540 product sheets.")
    d.note("The ND-500 crate's position and which face its cards use are read from one isometric (drawing 20489) "
           "and are not certain. Sources: ND-B2C12.pdf; NEC-01 ND-500 course card sheets.")
    d.note("Colour: dark brown, from the ND-560 brochure photograph; the exact paint is not documented.")
    return d


# ---------------------------------------------------------------------------------
# ND-500 in two cabinets, Book 2 chapters 14 and 15
# ---------------------------------------------------------------------------------

def nd500_two():
    set_palette("nd500dark")
    W, D = 60.0, 91.0
    d = Drawing("Norsk Data ND-500 in two cabinets, model 12",
                "ND-560 and ND-500/CX Model 22   |   two cabinets of 169 x 60 x 91 cm")
    large_shell(d, W, D, roof_cut_x=30, roof_cut_y=58)
    x0, x1 = 3.5, W - 3.0

    # power supply unit on slides at holes 11-13
    pz0, pz1 = hole(17), hole(10)
    d.add(Box(5, 3, pz0, 55, 86, pz1, "galv",
              front=[fins(16, 1, 20, 1.5, pz1 - pz0 - 1.5), fins(16, 21, 40, 1.5, pz1 - pz0 - 1.5),
                     rect(41, 1.5, 8, pz1 - pz0 - 3, "#bfc3c6", "#6f757a", 0.1),
                     label(41.3, pz1 - pz0 - 3.0, "MPS 325", 1.0, "#1b1b1b", "bold")],
              top=[fans(1, 2, 8, 44, 20, 60, rmul=0.4)]))
    d.add(Box(3.5, 10, 120, 5.0, 84, 121.5, "steel"))

    def n500(i):
        p = i + 1
        return "cpu" if 7 <= p <= 13 else ("card" if p in (4, 5, 11, 12, 14, 15, 16, 17, 18, 19) else "empty")

    def mpm(i):
        p = i + 1
        return "ram" if p in (1, 2, 3, 4, 5, 6, 9, 10, 11, 13, 14, 16, 17, 18) else "empty"

    uz0, uz1 = hole(44), hole(21)
    d.add(Box(x0, 1, uz0, x1, 45, uz1, "steel",
              front=[card_slots(26, 1.5, x1 - x0 - 1.5, 1.0, uz1 - uz0 - 3.0, fill_pattern=n500)]))
    d.add(Box(x0, 45, uz0, x1, 47, uz1, "pcb"))
    d.add(Box(x0, 1, uz0 - 7, x1, 43, uz0, "dark", front=[louvres(4, 2, x1 - x0 - 2, 1, 6, "#141210")]))

    lz0, lz1 = hole(61) + 2, hole(47) - 1
    d.add(Box(x0, 1, lz0, x1, 45, lz1, "steel",
              front=[card_slots(26, 1.5, x1 - x0 - 1.5, 1.0, lz1 - lz0 - 3.0, fill_pattern=mpm)]))
    d.add(Box(x0, 45, lz0, x1, 47, lz1, "pcb"))
    d.add(Box(x0, 1, lz0 - 6, x1, 43, lz0, "dark", front=[louvres(3, 2, x1 - x0 - 2, 1, 5, "#141210")]))

    # instruction and data channel cables between the crates, at the rear
    d.add(Box(3.8, 47.5, lz1 - 2, 9.0, 50.5, uz0 + 4, "blue"))
    # plug panel strip and cable channel on a rear post
    d.add(Box(3.5, 82, hole(18), 5.5, 88, hole(6), "galv", side=[dsub_rows(0.5, 5.5, 2, hole(6) - hole(18) - 2, 5, 1)]))
    d.add(Box(3.5, 88.5, PLINTH + 6, 6.0, 90.5, hole(18), "galv"))
    # power panel and ground rail
    d.add(Box(x0, 0.5, PLINTH + 1, x1, 40, hole(63), "galv",
              front=[label(2.0, 1.2, "230 V", 1.6, "#b3261e", "bold"), rect(30, 1.6, 16, 1.2, "#6f6a5e", rx=0.6)]))
    d.add(Box(x0, 84.5, hole(62), x1, 86, hole(60), "copper"))
    d.add(Box(33, 6, ROOF + 4.5, W - 2, 40, ROOF + 10, "shell", top=[fans(1, 2, 2, 23, 3, 31, rmul=0.44)]))
    d.add(Box(6, 62, ROOF + 4.5, W - 2, 88, ROOF + 10, "shell", top=[fans(1, 3, 2, 50, 2, 24, rmul=0.44)]))

    # the second cabinet, ND-100, closed, standing to the right
    gx = W + 4.0
    d.add(Box(gx + 1.5, 2.5, 0, gx + W - 1.5, D - 1, PLINTH, "brown"))
    d.add(Box(gx, 0, PLINTH, gx + W, D, ROOF + 4.5, "shell", faces="st",
              top=[rect(10, 20, 40, 6, "#cdbf9f", rx=0.5), rect(10, 60, 40, 6, "#cdbf9f", rx=0.5)]))
    d.add(Box(gx, -1.5, PLINTH, gx + W, 0, ROOF + 4.5, "brown", faces="f", front=cabinet_closed_front(W)))
    # the loom between the cabinets, running behind them; only the stretch in the gap shows
    d.line3([(4.5, 84, hole(12)), (4.5, D + 3, hole(12)), (gx + 25, D + 3, hole(12)), (gx + 25, D, hole(12))],
            "#2E5E8C", 5, "14,9")

    d.callout("Top fan assembly", (45, 22, ROOF + 10))
    d.callout("Power supply unit on slides,|holes 11-13: MPS 325 and|SMP1 5V/220A, SMP2 standby,|SMP3 5V/150A", (5, 50, pz1 - 4))
    d.callout("Strain relief angle,|about 121 cm up", (3.5, 70, 121))
    d.callout("ND-500 CPU crate, 26 positions,|rows A-D (upper, from the isometric)", (30, 1, uz1 - 5))
    d.callout("ND-500 CPU boards", (x0 + 18, 1, uz0 + 15))
    d.callout("MPM 5 memory crate,|26 positions", (30, 1, lz1 - 5))
    d.callout("Six-fan trays under each crate", (40, 1, lz0 - 3))
    d.callout("Instruction and data|channel cables, 327705-327711", (3.8, 49, (lz1 + uz0) / 2))
    d.callout("Plug panel on the rear post:|D13, D14, B16, C16", (3.5, 84, hole(12)))
    d.callout("Cable channel", (3.5, 89, hole(40)))
    d.callout("230 V power panel, holes 63-65", (30, 0.5, hole(64)))
    d.callout("Ground rail, holes 60-62", (x0, 85, hole(61)))
    d.callout("ND-100 cabinet: floppy,|operator panel, ND-100 crate, I/O", (gx + 30, -1.5, 120))
    d.callout("Cross-cabinet loom, dashed = hidden behind:|322907 power and control, 327714 I/O,|327713 and 327716 memory address and data", (gx - 12.0, D + 3, hole(12)), "R!")

    d.note("Cutaway of the ND-500 cabinet; the ND-100 cabinet stands closed beside it. Heights from the nutclip hole numbers "
           "in ND Book 2 chapter 14. Book 2 never draws the ND-100 cabinet itself.")
    d.note("Which crate is upper is read from one isometric (drawing 20497). Sources: ND-B2C14.pdf, ND-B2C15.pdf.")
    d.note("Colour: dark brown, from the ND-560 brochure photograph; the exact paint is not documented.")
    return d


# ---------------------------------------------------------------------------------
# ND-5000 Compact (COMSON), Book 2 chapter 8 and ND-05.017 figure 3
# ---------------------------------------------------------------------------------

def compact_shell(d, W, D, H, roof):
    """Feet, floor, far walls and the parts of the roof that stay on.
    roof = list of (x0, y0, x1, y1) pieces; a red cut edge runs along each piece's
    edges that face into the cabinet."""
    for (a, b) in ((2, 3), (W - 6, 3), (2, D - 7), (W - 6, D - 7)):
        d.add(Box(a, b, 0, a + 4, b + 4, 3, "black"))
    d.add(Box(0, 0, 3, W, D, 4, "shellin", faces="t"))
    d.add(Box(W - 2, 0, 4, W, D, H - 3, "shell"))
    d.add(Box(0, D - 2, 4, W - 2, D, H - 3, "shellin", faces="f"))
    for (a, b, c, e) in roof:
        d.add(Box(a, b, H - 3, c, e, H, "shell"))
        if a > 0:
            d.cut_line([(a, b, H), (a, e, H)])
        if b > 0:
            d.cut_line([(a, b, H), (c, b, H)])


def nd5000_compact():
    set_palette("compact")
    W, D, H = 54.0, 76.0, 69.0
    d = Drawing("Norsk Data ND-5000 Compact (COMSON)",
                "ND-5200, 5400, 5500 and 5700 Compact   |   69 x 54 x 76 cm, 100 kg", scale=11.0)
    compact_shell(d, W, D, H, roof=[(0, 68, W, D)])

    # card side: crate at the right, cards plug in from the right-hand side cover
    cz0, cz1 = 20.0, 58.0

    def pos(i):
        p = i + 1
        if p <= 2:
            return "#2F5E57"
        if p in (3, 4):
            return "#46603A"
        if p == 5:
            return "#3C5B7A"
        if p == 6:
            return "#5C6E35"
        if 18 <= p <= 20:
            return "#7a7a6c"
        if p in (7, 8, 10, 13):
            return "#2f512c"
        return "#1d1a17"

    def crate_top(fc):
        out = ['<rect x="0" y="0" width="%.3f" height="%.3f" fill="#1d1a17"/>' % (fc.w, fc.h)]
        step = fc.h / 20
        for i in range(20):
            out.append('<rect x="0.5" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>' % (
                i * step + step * 0.28, fc.w - 1.0, step * 0.44, pos(i)))
        return "\n".join(out)

    d.add(Box(24, 6, cz0, 51, 72, cz1, "steel", top=[crate_top]))
    # backwiring on the crate's left face: 5805 for 1-5, 5807 for 6-17, 5809 at the end
    d.add(Box(22.6, 6, cz0, 24, 72, cz1, "pcb",
              side=[backwiring_bands(4, 5, "#c9b458"), rect(0.4, 0.6, 16.5, cz1 - cz0 - 1.2, "none", "#e9dfc7", 0.25)]))
    d.add(Box(21, 6, cz0, 22.6, 72, cz0 + 2.5, "copper"))
    # plug panel strips standing on top of the crate at the backwiring side
    d.add(Box(23.0, 42, cz1, 24.5, 66, cz1 + 7.5, "galv", side=[dsub_rows(0.5, 23.5, 0.5, 7.0, 2, 4)]))
    # ten-fan plate under the crate
    d.add(Box(24, 6, 12, 51, 72, cz0, "dark", side=[louvres(4, 2, 64, 1, 7, "#141210")]))

    # drive and power side, front left
    d.add(Box(2, 1, 36, 21, 24, 50, "dark",
              side=[disk_front(3, 3, 12, 6), label(17, 10.5, "PCB 5911", 1.0, "#e9dfc7")],
              top=[rect(3, 4, 13, 24, "#555", rx=0.3)]))
    d.add(Box(4, 26, 32, 19, 30, 52, "steel", front=[rect(2, 4, 11, 12, "#444", rx=0.3)]))
    d.add(Box(2, 1, 4, 20, 24, 30, "dark",
              side=[fins(14, 1.5, 15, 2, 24, "#57524c"), label(20.0, 20.0, "ND", 2.8, "#e9dfc7", "bold"),
                    label(20.0, 14.0, "DC110", 1.6, "#e9dfc7", "bold")]))
    d.add(Box(4, 26, 4, 16, 34, 12, "black"))
    d.add(Box(4, 36, 4, 20, 52, 11, "steel", side=[rect(2, 2, 12, 3, "#555", rx=0.3)]))
    d.add(Box(4, 54, 4, 20, 64, 11, "steel", side=[rect(2, 2, 7, 3, "#555", rx=0.3)]))
    d.add(Box(2, 66, 4, 8, 72, 9, "galv"))

    # front panel: sloped fascia band, drive openings, operator panel, louvre grille
    d.add(Box(0, -1.2, 4, W, 0, H - 3, "brown", faces="f",
              front=[rect(0, 44, W, 18, "#6e4a31"),
                     floppy(3, 50, 13, 6), streamer(17, 50, 13, 6),
                     op_panel(31, 50.5, 20, 5, buttons=6, display=True),
                     label(3, 59, "ND Norsk Data", 2.0, "#f2e6cc", "bold"),
                     label(33, 59, "ND-5000 Compact", 1.9, "#f2e6cc"),
                     louvres(14, 3, W - 3, 4, 40, "#4a3120")]))
    d.add(Box(W - 1, -1.5, 4, W, -1.2, 8, "black", faces="f"))

    d.callout("5.25\" floppy and streamer", (9, -1.2, 53))
    d.callout("Operator panel", (41, -1.2, 53))
    d.callout("Louvre grille", (40, -1.2, 20))
    d.callout("Drive rack with disk 1|and COMSON diskboard PCB 5911", (2, 12, 43))
    d.callout("Disk 2, standing vertically|behind the drive rack", (4, 28, 50))
    d.callout("Power crate: DC110|5V/120A, 12V/15A, 5V/7A standby", (2, 12, 16))
    d.callout("1 Ah backup battery", (4, 30, 8))
    d.callout("Disks 3 and 4 beside|the power system", (4, 44, 9))
    d.callout("Card crate, 20 positions: 1-5 ND-500|size, 6-17 ND-110 size, 18-20 plugboards", (38, 45, cz1))
    d.callout("Backwiring: PCB 5805 (1-5),|PCB 5807 (6-17), PCB 5809", (22.6, 62, 45))
    d.callout("Double Bus Controller PCB 5464|at position 5 joins the two buses", (40, 6 + 66 * 4.5 / 20, cz1))
    d.callout("Busbar and copper rails", (21, 70, cz0 + 1.2))
    d.callout("Plug panel strips, positions 14-17", (23, 55, cz1 + 5))
    d.callout("Ten-fan plate, two rows of five", (24, 70, 15))

    d.note("Cutaway: left side, top and roof removed; the crate's cards plug in from the right-hand side cover, not seen here. "
           "Layout from ND Book 2 chapter 8 and ND-05.017 figure 3; size from the 1987 planning manual.")
    d.note("The depth of the drive rack and power crate is not given in the drawings; they are drawn shallow so the parts behind them show.")
    d.note("Drawn schematic, not to exact scale. Sources: ND-B2C8.pdf, ND-B2C8-1987.pdf, ND-B2C3.pdf; ND-05.017 tables 5 and 6.")
    d.note("Colour: red-brown front fascia and greyer brown sides, measured from a photograph of a real Compact.")
    return d


# ---------------------------------------------------------------------------------
# ND-5000 ES Model C, ND-830102 chapter 2
# ---------------------------------------------------------------------------------

def es_model_c():
    set_palette("compact")
    W, D, H = 54.0, 76.0, 69.0
    d = Drawing("Norsk Data ND-5000 ES Model C",
                "same shell as the ND-5000 Compact, one crate, backwiring in the middle   |   69 x 54 x 76 cm", scale=11.0)
    compact_shell(d, W, D, H, roof=[(30, 0, W, 38.0)])
    yb = 38.0

    # backwiring across the width in the middle
    d.add(Box(1, yb, 5, W - 2, yb + 1.6, H - 5, "pcb",
              side=[rect(0.2, 1, 1.2, H - 12, "#c9b458", opacity=0.6)],
              top=[rect(1, 0.2, W - 5, 1.2, "#c9b458", opacity=0.6)]))
    # front half: fan tray, ND-100 cards, MF bus cards
    d.add(Box(1, 0, 5, W - 2, yb, 11, "dark", front=[fans(1, 5, 1, W - 4, 0.5, 5.5, rmul=0.45)]))

    def front_cards(i):
        p = i + 1
        if p <= 9:
            return {9: "gold", 2: "blue", 1: "card"}.get(p, "card" if p in (3, 4) else "empty")
        return {10: "ram", 14: "#3C5B7A"}.get(p, "empty")

    d.add(Box(1, 1.5, 13, 30, yb, 54, "steel",
              front=[card_slots(14, 1, 28, 1, 40, numbered=False, fill_pattern=front_cards)],
              side=[card_block_side(6)],
              top=[top_card_edges(14)]))
    # operator panel strip across the top front
    d.add(Box(1, 0, 56, 30, 4, 61, "dark", front=[op_panel(1, 0.6, 27, 3.8, buttons=7, display=False)]))
    # device bays, right front, with the front cover still on
    d.add(Box(30.5, 0, 13, W - 2, yb, 61, "dark",
              front=[floppy(1, 36, 7, 10), streamer(8.5, 36, 7, 10), disk_front(16, 36, 5.5, 10),
                     disk_front(1, 22, 10, 12), disk_front(11.5, 22, 10, 12),
                     disk_front(1, 8, 10, 12), disk_front(11.5, 8, 10, 12),
                     label(17, 46.5, "B", 1.4, "#e9dfc7", "bold"), label(5, 33, "A", 1.4, "#e9dfc7", "bold"),
                     label(15.5, 33, "C", 1.4, "#e9dfc7", "bold"), label(5, 19, "E", 1.4, "#e9dfc7", "bold"),
                     label(15.5, 19, "D", 1.4, "#e9dfc7", "bold")]))
    # rear half, top to bottom as in figure 15: power supply, ND-5000 CPU, plugboards
    d.add(Box(2, yb + 2, 48, 42, 73, 64, "galv",
              side=[fins(18, 1.5, 19, 2, 14, "#8a8d90"), label(21.5, 7, "DC 500", 2.0, "#1b1b1b", "bold")]))
    d.add(Box(2, yb + 2, 29, 14, 73, 46, "steel",
              side=[rect(0.8, 0.8, 31.4, 15.4, "#2F5E57", "#16302b", 0.1), rect(1.6, 11.5, 29.8, 2.2, "#3f7a70"),
                    label(2.0, 5.5, "ND-5000 CPU, positions 1-4", 1.7, "#e9f2ef", "bold")],
              top=[top_card_edges(4, "#2F5E57")]))
    d.add(Box(2, yb + 2, 6, W - 3, 73, 27, "steel",
              side=[dsub_rows(1.5, 31, 1.5, 19, 3, 6)],
              top=[top_card_edges(16, "#6b6b5f")]))

    d.callout("Operator panel and key switch,|no display", (12, 0, 59))
    d.callout("ND-100 cards, positions 1-9,|ND-120 CPU in 9", (8, 1.5, 30))
    d.callout("MF bus cards, positions 5-9,|Double bus controller in 9", (24, 1.5, 36))
    d.callout("Floppy, streamer and disk B", (38, 0, 52))
    d.callout("Disks A, C, E, D, up to|five 310 MB SCSI disks", (42, 0, 30))
    d.callout("Fan tray, plugs in from|the bottom of the front", (30, 0, 8))
    d.callout("Backwiring PCB 5812 or 5816, in the|middle: cards plug in from both sides", (8, yb + 0.8, H - 5))
    d.callout("Power supply DC 500, plugs in from the rear", (2, 55, 60))
    d.callout("ND-5000 CPU, four positions,|plugged in from the rear", (2, 64, 40))
    d.callout("Plugboards from the rear: system 5259,|MFB controller 5234, 8-terminal 5261", (2, 64, 16))

    d.note("Cutaway: left side, roof and the front cover over the card area removed. Layout from ND-830102 figures 15 and 16; "
           "which cards sit where across the width is schematic.")
    d.note("Sources: ND-830102 ES Model C Hardware Maintenance Manual (ND-830102-1-EN.pdf), chapter 2; shell size from the 1987 planning manual.")
    d.note("Colour: the Compact colours are used; the new ES front cover and its colour are not documented or photographed.")
    return d


# ---------------------------------------------------------------------------------
# ND-5000 Satellite and Technostation, Book 2 chapter 20
# ---------------------------------------------------------------------------------

def satellite():
    set_palette("grey")
    # Width : height : depth about 1 : 2.4 : 3.4, measured off the "complete" sheet 20066
    # (Book 2 chapter 3 sub-chapter 4) and matching the Technostation brochure photograph.
    # No document gives an absolute size; the height is set to stand just under a desk.
    W, H, L = 28.0, 66.0, 92.0
    d = Drawing("Norsk Data ND-5000 Satellite and Technostation",
                "later sold as ES Model S   |   narrow deep tower on four castors   |   proportions measured from the drawing, size estimated",
                scale=10.0)
    # castors
    for (a, b) in ((2, 3), (W - 7, 3), (2, L - 9), (W - 7, L - 9)):
        d.add(Box(a, b, 0, a + 5, b + 5, 5, "black"))
    # tray: floor, low lip on the open side, tall wall on the far side
    d.add(Box(0, 0, 8, W, L, 10, "galv"))
    d.add(Box(0, 0, 10, 1.2, L, 14, "galv"))
    d.add(Box(W - 1.5, 0, 10, W, L, H - 3, "shell"))
    # hood, cut away except a strip along the far side
    d.add(Box(24, 0, H - 3, W, L, H, "shell", top=[hatch(0.3, 3.7, 2, L - 2, "#c9c5bc", 3)]))
    d.cut_line([(24, 0, H), (24, L, H)])
    d.cut_line([(0, 0, 14), (0, L, 14)])

    # fan trays under the floor: front one home, rear one pulled out of the open side
    d.add(Box(1, 14, 5.2, 26, 40, 7.8, "dark"))
    d.add(Box(-20, 50, 5.2, 8, 76, 7.8, "dark", top=[fans(1, 2, 1, 19, 1, 25, rmul=0.42)]))

    # backwiring across the width, mid depth
    yb = 44.0
    d.add(Box(1.5, yb, 10, W - 1.5, yb + 1.6, 58, "pcb", side=[rect(0.2, 1, 1.2, 46, "#c9b458", opacity=0.6)]))
    # card blocks either side of it
    d.add(Box(2, 16, 11, W - 2, yb, 52, "steel", side=[card_block_side(4)], top=[top_card_edges(11)]))
    d.add(Box(2, yb + 1.6, 11, W - 2, 78, 52, "steel", side=[card_block_side(4)], top=[top_card_edges(11)]))
    d.add(Box(2, yb + 16, 52, 9, 78, 53, "galv", top=[hatch(0.5, 6.5, 1, 16, "#6b6b5f", 6)]))

    # front end: operator panel strip along the top, storage device below it
    d.add(Box(1, 0, H - 9, W - 1.5, 5, H - 3, "dark",
              front=[op_panel(0.6, 0.8, W - 3.4, 4.2, buttons=6, display=False)]))
    d.add(Box(2.5, 1, 30, W - 2, 14, H - 11, "galv",
              front=[disk_front(1, 3, 10.5, 18), disk_front(12.5, 3, 10.5, 18)]))

    # rear end: power supply, plug board 1, plug carriers, circuit breaker
    d.add(Box(2, 82, 10, 19, 90, H - 5, "galv",
              side=[fins(8, 0.6, 7.4, 2, H - 20, "#8a8d90"), label(0.6, H - 19, "DC 500", 1.4, "#1b1b1b", "bold")]))
    d.add(Box(2, 79, 12, W - 2, 81, 56, "pcb", side=[dsub_rows(0.2, 1.8, 4, 40, 3, 1)]))
    d.add(Box(20, 82, 12, 22.5, 90, 56, "pcb", front=[dsub_rows(0.2, 2.3, 2, 42, 4, 1)]))
    d.add(Box(23.0, 82, 12, 25.5, 90, 56, "pcb", front=[dsub_rows(0.2, 2.3, 2, 42, 5, 1)]))
    d.add(Box(0, 83, 15, 1.2, 89, 20, "black", side=[label(0.5, 1.5, "230 V", 1.2, "#e9e7e1", "bold")]))

    d.callout("Operator panel: membrane keypad|and keyswitch along the top front", (8, 0, H - 6))
    d.callout("Storage device: two drive bays|behind the front doors", (8, 1, 42))
    d.callout("Card block, front half:|cards plug rearwards", (2, 30, 40))
    d.callout("Backwiring PCB 5810 or 5811, standing|across the width in the middle", (1.5, yb + 0.8, 55))
    d.callout("Card block, rear half:|cards plug forwards", (2, 62, 40))
    d.callout("6-slot rail, Satellite", (5, yb + 25, 53))
    d.callout("Plug board 1 PCB 1888", (2, 80, 50))
    d.callout("Power supply DC 500 Wiener,|full height at the rear end", (2, 86, 30))
    d.callout("Plug carriers PCB 1889 (4) and|PCB 1891 (5, Satellite only)", (21.2, 86, 56))
    d.callout("Circuit breaker, 230 V 50 Hz", (0, 86, 18))
    d.callout("Fan trays: four fans in the floor,|one tray pulled out from the open side", (-10, 63, 7.8))
    d.callout("Castors", (2, 5, 2))
    d.callout("Hood (cut away), lifts off|after six draw latches", (26, 30, H))

    d.note("Cutaway: hood and front and rear covers removed. No ND document gives this box's size. Width, height and depth "
           "are in the proportion 1 : 2.4 : 3.4 measured off drawing 20066; the absolute size is estimated.")
    d.note("Card counts per half are not in the drawings. Sources: ND-B2C20.pdf; ND-B2C3.pdf sub-chapter 4. "
           "Colour: light grey, from the Technostation brochure photograph.")
    return d


# ---------------------------------------------------------------------------------

DRAWINGS = {
    "nd5000-large": nd5000_large,
    "nd500-one-cabinet": nd500_one,
    "nd500-two-cabinet": nd500_two,
    "nd5000-compact": nd5000_compact,
    "nd5000-es-model-c": es_model_c,
    "nd5000-satellite-technostation": satellite,
}


def render(key):
    d = DRAWINGS[key]()
    svg_path = os.path.join(HERE, key + ".svg")
    d.render(svg_path)
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=os.path.join(HERE, key + ".png"))
    except ImportError:
        pass
    print("wrote", key)


if __name__ == "__main__":
    keys = sys.argv[1:] or list(DRAWINGS)
    for k in keys:
        render(k)
