# The large 11-module cabinet, 1985 shell

The floor-standing cabinet shared by every large ND machine from the ND-100 through the
ND-500 to the ND-5000. ND calls it the **11-module cabinet '85**, or in the older books
the **ND-100/500 cabinet**. "11 module" is literal: eleven 5 1/4 inch bay positions down
the front.

This file is the shell only. What goes inside it is in the per-machine files listed in
[README.md](README.md).

**Source:** **Book 2 chapter 10**, "ND-100 11-Mod.Cab.'85 and EXPANSION, Assembly
Drawings", scan `ND-B2C10.pdf`, 47 pages, and **Book 2 chapter 3**, "Mounting of
Panels", scan `ND-B2C3.pdf`, 21 pages. Both read sheet by sheet. The scans are in the
sintran.com mirror under `library/libhw/`; see the source map in
[README.md](README.md). Sizes come from the product sheets and planning manuals, not
from the drawings.


The shell with its contents is drawn in the cutaways [nd500-one-cabinet](diagrams/nd500-one-cabinet.png), [nd500-two-cabinet](diagrams/nd500-two-cabinet.png) and [nd5000-large](diagrams/nd5000-large.png).

---

## 1. Outer size

Not one of the 68 drawing sheets gives an overall height, width or depth. These figures
come from elsewhere and they do not fully agree.

| Source | H x W x D | Weight |
|---|---|---|
| ND-520, ND-540, ND-505/CX product sheets | 1.69 x 0.60 x 0.91 m | 180-250 kg |
| ND-500/CX Model 21 and 22 sheets | 1.69 x 0.60 x 0.95 m | 180-250 kg |
| ND-5700/5800/5900 sheet | 1.60 x 0.60 x 0.95 m | max 250 kg |
| 1987 planning manual ND-13.028 | 169 x 60 x 95 cm | 130-250 kg by family |
| 1984 site table, empty cabinet | 172 x 60 x 92 cm | 80 kg |

Width is the one dimension every source agrees on: **60 cm**. Use 169 x 60 x 91 cm and
say where it came from. The conflict is discussed in
`../../Hardware/ND-PHYSICAL-MODELS.md`.

A two-cabinet system is two of these standing side by side, so 172 x 120 x 92 cm in the
1984 table, with two separate mains feeds.

---

## 2. The frame

- **Four vertical channel-section uprights**, two front and two rear, standing on a
  **closed rectangular base slab** which forms a shallow plinth. A matching slab closes
  the top. The base plate has a large rectangular cutout in the middle of the floor for
  cable entry from below, which suits a raised computer-room floor.
- No castors and no adjustable feet are drawn or listed. The 11-module cabinet sits on
  its slab.
- Down the inner face of every upright runs a column of paired mounting holes,
  **numbered 1 at the top to 66 at the bottom**, on the front frame and the rear frame
  alike. Nutclips are pressed into the holes a given build needs, and every shelf, slide,
  bracket and crate is located by hole number.
- Nothing heavy bolts straight to a post. **Horizontal slides span front upright to rear
  upright** and the drive rack and the power supply ride on those slides, pushed in from
  the front.
- Three small tabs or slots run along the top edge of both the front and rear frame.
  These carry the top fan assembly.
- An **angle iron** sits inside the front-left corner post over the full height and is
  taken out before the modules go in.

The only cabinet-scale lengths printed anywhere in the set:

| Printed on | Value | What it locates |
|---|---|---|
| Drawing 20464 | 48.5 cm | ground-rail bracket up to the card-crate hinge line |
| Drawing 20471 | ca. 100 cm from socket | the perforated strain-relief angle, ND-100 build |
| Drawing 20471, ND-500 one-cabinet | ca. 108 cm from socket | same angle in that build |
| Drawing 20493, ND-500 two-cabinet | ca. 121 cm from socket | same angle in that build |
| Drawing 20490 | ca. 63 cm from socket | terminal strip 1 on a front post |

"Socket" here means the plinth the cabinet stands on.

---

## 3. The front face

The front of the large cabinet is **not a door**. It is two moulded panels bolted into
one tall face:

| Part | Number | Notes |
|---|---|---|
| Front panel, upper | 509 059 | ND-100, ND-500 and ND-5000 all share it |
| Front panel, upper, expansion cabinet | 509 056 | blank version, backed by one Plexiglas sheet 509 057 |
| Front panel, lower | 509 061 | the tall one |
| Mounting angle | 519 807 | bar across the back of the upper panel |
| Rail | 519 820 | two vertical stiffeners behind the lower panel |
| Panel blind | 519 577 and 519 656 | close an opening a given machine does not use |

Shape, read off drawing 20559 page 4: the assembled front is a tall narrow rectangle,
roughly three times as high as it is wide. The upper panel is short, about a fifth of the
total height, and carries two windows in its top row. The lower panel is one big frame
with a grid of recessed rectangular openings in its upper part and a plain area below.
**Both mouldings have a chamfered right-hand end**, so the finished front face carries one
bevelled vertical edge running its full height. That is the cabinet's most distinctive
outside feature. Two small feet or tabs project at the very bottom of the lower panel.

Where things show through: the **floppy drive near the top** (its box hangs at hole 3),
the **operator panel just below it** (holes 13 to 15). Every other opening is filled with
a blind panel unless that machine uses it.

**The expansion cabinet is the same shell with a blank, glazed upper front.** No floppy,
no operator panel, no drive-rack slides. From the outside you tell it apart only by the
Plexiglas sheet behind the upper openings.

---

## 4. The rear face

The rear is a large **hinged plug-panel frame** that swings open. It holds a stack of
narrow connector strips, each a flat plate with one or two long rows of multiway
connectors on its outer face and a notch cut in each end where it drops into the frame.
At the left end of each strip sits a **white letter box over a black number box**.

Labels seen on those strips across the set:

| Kind | Labels |
|---|---|
| Strip identity | A, B, C, D over 12, 13, 14, 16, 22 |
| Console and service | CONS, TFIX/MOD, TFIX/PRINT |
| Disk | SMD, SMC 0 to SMC 4, SMR, SMT |
| Communications | MEG-L, LINE DRIVER, OCTO 1, OCTO 2 |
| Terminals | 8 TERM, and numbered groups 36-39 and 48-51 |
| Plain | 1, 2, 3 |

Below the strips, a horizontal **ground rail** is bolted across the rear at hole 66 with
M10 hardware. Every green ground strap from every crate, fan tray, power supply and the
floppy box ends there under a star washer.

---

## 5. How it is fastened

Everything a service engineer touches is tool-free or quarter-turn:

- **Crate front covers**: DZUS quarter-turn fasteners with captive Vistop washers, sealed
  along the edge with an 8 x 15 mm neoprene strip.
- **Fan trays**: M4 and M6 wing nuts, guided onto locating pins.
- **Power supply and drive rack**: slide in from the front on their rails.
- **Outer panels on the smaller ND machines** in the same book: hung on brackets, held by
  DZUS fasteners, each panel bonded to the chassis with a Faston spade and a ground lead,
  with a keyed DZUS lock on the front and a CAUTION label on the rear.
- **A wrist strap** for the engineer is clipped to the frame at hole 8, high up.

---

## 6. Air and mains

Air moves bottom to top. Each crate has its own fan tray sitting directly under it,
blowing up through the cards, with a flat mesh air filter under the fans. One or two
**top fan assemblies** lie flat on the cabinet roof over the top vent slots, chained
together by a 45 cm mains cable.

Mains enters at the **bottom**, at the 230 V power panel, and fans out upward from there
to the top fans, the crate fans, the floppy and the power supplies. A long perforated
angle running front to rear is the cable tie-down bar for the heavy DC cables; the DC bus
cables themselves are 16 mm square and 135 to 225 cm long, so they run essentially the
full height of the cabinet.

---

## 7. Not known, so do not draw it

- Any overall dimension from the drawings themselves.
- Plinth height, panel radii, vent slot pitch, grille pattern on the large cabinet.
- Castors or feet; none are drawn.
- Colour and finish. See the colour note in [README.md](README.md).
- A rear door as such. The rear is the hinged plug-panel frame, not a skinned door.

---

## 8. Image brief: the bare shell

Paste the house style block from [README.md](README.md) first.

### Panel A, the frame alone

```
Subject: the empty steel frame of a 1980s floor-standing minicomputer cabinet, three
quarter view from the front left, no skin panels.
Draw: four vertical channel-section corner uprights standing on a closed rectangular
base slab that forms a shallow plinth; a matching flat slab closing the top with two
long rectangular vent slots in it; a large rectangular cable cutout in the middle of the
base floor.
Down the inner face of each upright runs a column of small paired mounting holes from
top to bottom, evenly spaced, about 66 of them. Show a few small spring nutclips pressed
into some of the holes.
Across the middle, between one front upright and one rear upright, a perforated angle
bar runs front to back.
Proportions: about 169 cm high, 60 cm wide, 91 cm deep, so noticeably taller than a
person's chest and deeper than it is wide.
Labels with leader lines: "Front upright", "Rear upright", "Base slab and plinth",
"Top slab with vent slots", "Nutclip hole column, 1 at top to 66 at bottom",
"Cable cutout in floor", "Strain relief angle", "Ground rail".
```

### Panel B, the front face

```
Subject: straight-on front elevation of the closed cabinet.
Draw: a tall narrow face about three times as high as it is wide, made of two bolted
mouldings. The short upper moulding carries two rectangular windows side by side in its
top row. The taller lower moulding is one frame holding a grid of recessed rectangular
openings in its upper part over a plain area below. The right-hand vertical edge of both
mouldings is chamfered, so one bevelled edge runs the full height of the face. A shallow
plinth is recessed behind the face at the bottom, so the cabinet does not meet the floor
flush. Two small tabs project at the very bottom.
In the top row of openings: a 5.25 inch floppy drive bezel with a horizontal slot on the
left. Below it, a slim horizontal operator panel strip with a small display window, a row
of square buttons and a round keyswitch. All other openings are closed with plain blind
panels.
Small "ND Norsk Data" wordmark near the top of the face.
Colours: warm off-white painted steel frame, dark brown-black panel fronts.
Labels: "Upper front panel", "Lower front panel", "Chamfered edge", "Floppy drive bay",
"Operator panel", "Blind panel", "Plinth".
```

### Panel C, the rear

```
Subject: straight-on rear elevation with the hinged plug-panel frame closed.
Draw: a tall rectangular frame filled by a stack of narrow horizontal connector strips.
Each strip is a flat plate carrying one or two long rows of multiway D-shaped connectors,
with a small white letter label over a small black number label at its left end. Show
about eight strips, some fully populated with connectors and some blank.
Letter and number labels on the strips: A over 22, B over 22, C over 12, D over 13,
D over 14.
Text labels printed beside individual connector rows: CONS, TFIX/MOD, TFIX/PRINT, SMD,
SMC 0, SMC 1, SMR, SMT, MEG-L, LINE DRIVER, OCTO 1, OCTO 2, 8 TERM, and the number
groups 36 37 38 39 and 48 49 50 51.
At the bottom, a horizontal copper ground rail bolted across with large hex nuts, with
several green and yellow earth straps ending on it under star washers.
Labels with leader lines: "Hinged plug panel frame", "Connector strip", "Strip identity
label", "Ground rail", "Earth straps".
```

---

## 9. Sources

- Book 2 chapter 10, "ND-100 11-Mod.Cab.'85 and EXPANSION, Assembly Drawings", 47 sheets.
  Key sheets: 20645 main assembly, 20468 position of nutclips, 20470 drive rack slides,
  20469 power supply slides, 20471 strain relief angle, 20464 hinge bracket and ground
  rail, 20466 power panel and plug frame, 20472 floppy box, 20478 power supply unit,
  20462 card crate assembly, 20467 card crate and cover mounting, 20481 operator panel,
  20482 cabling mains and ground, 20657 expansion cabinet main assembly.
- Book 2 chapter 3, "Mounting of Panels", sub-chapter 3, drawing 20559 pages 1 to 4,
  front panel assembly for ND-5000, ND-500, ND-100, I/O expansion and memory cabinets.
- `../../Hardware/ND-PHYSICAL-MODELS.md` for the dimension tables and the colour reading.
- `../Product-Info/ND-520-C1-EN.md`, `ND-540-C1-EN.md`, `ND-505CX-A1-EN.md`,
  `ND-5371-A1-EN.md`, `ND-5372-B1-EN.md`, `ND-5700-B1-EN.md` for the outer sizes.

---

*Index: [README.md](README.md)*
