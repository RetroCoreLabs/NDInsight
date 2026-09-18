# ND Physical Models: Cabinets, Dimensions and Model Ranges

Physical (mechanical) reference for Norsk Data machines: what each cabinet is, how big it
is, what it weighs, what it draws, and which model names sit in which box.

Written to support 3D modelling and hardware reconstruction, so the emphasis is on
measurable, cited facts. Everything below is quoted from a named manual. Where a number is
derived rather than documented, it is marked DERIVED. Where nothing was found, it says so
rather than guessing.

**Status**: third version, 2026-08-01. Machines and Filestore covered from two independent
manuals (1987 in section 1, 1984 in section 7) plus ND's own marketing and photographs
(section 8). Terminals, printers and power distribution are in the appendix. Sections marked
GAP still need a source.

**For 3D modelling**, read section 1 or 7 for the outer box, section 7.1 for footprint and
floor geometry, and section 8 for front-face layout and colour. Outer boxes are solid.
Front-face feature *proportions* are the outstanding gap and are marked as such rather than
guessed.

---

## 1. The master dimensions table

This is the 1987 table. There is a **second, earlier and more detailed table** from 1984 in
the Site Preparation manual, broken down per product number rather than per family - see
section 7. The two disagree slightly; the disagreement is discussed there. Section 7 also
holds the **only dimensioned mechanical drawings found anywhere**: floor cutout diagrams
that give cabinet footprint and cable-hole position in centimetres.

The 1987 table is the site-planning ("computer room planning") manual.

**Source**: ND-13.028.1 NO, *Planlegging av datarom*, Norsk Data, version 1, May 1987,
chapter 18 "Produktspesifikasjoner", page 57.
File: the OCR working folder does not hold this one. It is in the norsk-data.com mirror at
`library/libhw/ND-13028-1-NO.pdf` in the sintran.com mirror (PDF page 65).

The manual states in its foreword that it applies to ND-100, ND-500 and ND-5000 systems.

Column headings in the original are Norwegian: H/B/D = Hoyde/Bredde/Dybde =
height/width/depth, VEKT = weight, FORB. = consumption, SIKRING = fuse.

| Product | Height x Width x Depth (cm) | Weight (kg) | Power (W) | Fuse (A) |
|---|---|---|---|---|
| ND SATELLITE models | 64 x 23 x 77 | 35 | 400 | 16 slow |
| ND COMPACT models | 69 x 54 x 76 | 78 | 800 | 16 slow |
| ND-100 models | 169 x 60 x 95 | 130-200 | 1600 | 16 slow |
| ND-500 models, 1-cabinet | 169 x 60 x 95 | 180-250 | 3200 | 25 slow |
| ND-500 models, 2-cabinet | 169 x 60 x 95 per cabinet | 450 | 2700 / 1600 | 25 slow + 16 slow |
| **ND-5000 COMPACT models** | **69 x 54 x 76** | **100** | **1250** | **16 slow** |
| ND-5000 models, 1-cabinet | 169 x 60 x 95 | 180-250 | 2200 | 25 slow |

Two observations that matter:

- The **ND-5000 Compact and the ND-100 Compact are the same box**, 69 x 54 x 76 cm. They
  differ only in weight (100 kg vs 78 kg) and power (1250 W vs 800 W). This is independently
  confirmed by the ND-5000 ES Model C maintenance manual, which says the Model C "has the
  same cabinet as the previous version, except for the front cover" (ND-830102.1B, page 3).
- The **large ND cabinet is one standard shell**, 169 x 60 x 95 cm, used by ND-100, ND-500
  and ND-5000 alike. Only the contents, weight and power differ.

### Filestore cabinets

Same manual, page 58.

| ND number | Product | H x W x D (cm) | Weight (kg) | Fuse (A) |
|---|---|---|---|---|
| 106240 / 106241 | FILESTORE KABINETT COMPACT | 69 x 54 x 76 | 55-150 | 16 slow |
| 106350 / 110048 / 110025 | FILESTORE KABINETT | 169 x 60 x 96 | 100-215 | 16 slow |
| (unnumbered) | FILESTORE KABINETT with magtape STC 1950 | 169 x 60 x 96 | 234 / 275 | 25 slow |
| 105740 | Free-standing disk, CDC 288 MB | 91 x 58 x 91 | 321 | 25 slow |

The Compact Filestore is the same 69 x 54 x 76 shell as the Compact CPU cabinet. That is
the second box standing beside the machine in most photographs.

Drive power draw inside a Filestore, same page: magtape Cipher 360 W, magtape STC 2922
250 W, fast disk 140 MB 408 W, fast disk 288 MB 140 W, fast disk 450 MB 250 W, cartridge
disk 70 MB 200 W, magtape STC 1950 1650 W plus 880 W for its formatter.

---

## 2. The small cabinet (Compact)

External size 69 x 54 x 76 cm (H x W x D). Used by:

- ND-100 Compact / ND-110 Compact
- ND-5000 Compact
- ND-5000 ES Model C (same shell, new front cover)
- Compact Filestore

### Card rack

The ND-110 Compact houses a **12-position card crate**; the ND-110 Satellite a 7-position
crate; the large cabinet versions hold up to 21 cards.
Source: ND-06.026.1 EN, *ND-110 Functional Description*, section 1.5 "The ND Cabinets",
page 10-11. In repo: [ND-110 Functional Description](../Reference-Manuals/ND-06.026-1-EN%20ND-110%20Functional%20Description.md).

The ND-100 12-position crate carries its power supply inside the crate itself, which the
reference manual notes "leads to a very compact system".
Source: ND-06.014.2A EN, *ND-100 Reference Manual*, figure 2.22 caption.

The **ND-5000 Compact** uses a 20-position double-bus backwiring, split between ND-500 size
cards and ND-110 size cards. Two versions exist.
Source: ND-05.017.01 EN, *ND-5000 Hardware Maintenance*, section 1.2.2 "Small Cabinet",
tables 5 and 6, pages 8-9.

First version (models A0-A4 and model B), table 5:

| Pos | Card | Note |
|---|---|---|
| 1-2 | ND-5000 CPU card | CPU type 1 uses pos. 1-2 |
| 3 | (MFB Dynamic RAM) | CPU type 2 uses pos. 1-3 |
| 4 | MFB Dynamic RAM | 4, 8 or 16 MB |
| 5 | Double Bus Controller | end of ND-500 size cards |
| 6 | ND-110/CX CPU | start of ND-110 size cards |
| 7 | Tracer / Memory | |
| 8-9 | HDLC / Megalink / Memory | |
| 10-12 | 8 term. / PIOC / Memory | |
| 13 | ST506 Disk Controller / Triangel / Memory / Free | |
| 14 | Floppy-SCSI / Free / Memory | |
| 15-17 | Free | |
| 18 | Plugboard 1 | from pos.10 8 term./PIOC; pos.5 and 6 console; pos.6 Telefix/Tfix port |
| 19 | Plugboard 2 | from pos.11 8 term./PIOC; pos.8 HDLC/Megalink |
| 20 | Plugboard 3 | from pos.12 8 term./PIOC; pos.9 HDLC/Megalink |

New type (models A10-A14 and model B), table 6, differs mainly at positions 7-8 (Ethernet
and Token Ring options appear) and position 13 (a combined Floppy and SCSI controller
replaces the ST506 controller, freeing position 14).

Dummy plugs are inserted in all free positions.

### Power supply

One plug-in module, **DC110**, accessible from the front, held by four screws.
Outputs 5 V / 120 A, 12 V / 15 A, 5 V / 7 A standby.

- +5 V / 120 A mainly feeds CPU and memory
- +5 V / 7 A standby holds memory alive through a power failure
- +12 V / 15 A feeds the internally mounted peripherals: 5 1/4" disk and floppy drives

Source: ND-05.017.01 EN section 1.3 "Power supply", page 10, and figure 4 page 11.

The supply family is the ND Multipower System (MPS): DC110 as above, DC200 = 5 V / 200 A,
DC300 = 5 V / 50 A standby for ten minutes, DC400 reserved for future use. Front panel
carries ON/OFF, ADJ trimmers with test points, MARG switches (+/- 5 percent), an OVERTEMP
red LED at 90 degrees C internal, and a TRANSIENT red LED that trips on any voltage more
than 10 percent off nominal. Source: same manual pages 13-14, figure 6.

### Usable drawings

There is **no dimensioned mechanical drawing of the cabinet itself** in any manual found so
far. The nearest thing is the set of floor cutout drawings in section 7.1, which give
footprint and cable-hole geometry but say nothing about the cabinet above floor level, and
which cover the ND-100 and ND-500 cabinets rather than the Compact.

The usable cabinet line-art, all undimensioned, is:

- ND-05.017.01 EN figure 3, page 7: ND-5000 Compact cabinet, cutaway isometric showing card
  rack, power supply, drive bays and plinth. This is the **clearest single view** located.
  File: `5000/ND-05.017.01 EN ND-5000 HARDWARE MAINTENANCE-Gandalf-OCR.pdf` in the OCR working folder, PDF page 21.
- ND-05.017.01 EN figure 4, page 11: same view with the power supply sliding out.
- ND-830102.1B figures 1-5, manual pages 5-12: cabinet, front panel removal, all panels
  exploded (side, top, rear plus bare frame), fan tray and operator panel, backwiring layout
  with the five disk positions.
  File: `5000/ND-830102.1B EN ND-5000 ES Model C Hardware Maint. Manual-Sintran-OCR.pdf` in the OCR working folder,
  PDF pages 13-22.

Note that the repo markdown of both manuals **lost every image** during OCR. Read the PDFs.
Note also that the body text of ND-05.017.01 chapter 1 is missing from the repo markdown
(only the table of contents survived) - the PDF is the only copy.

GAP: no source yet for panel radii, vent slot pitch, plinth height, or castor/foot detail.

---

## 3. The large cabinet

External size 169 x 60 x 95 cm (H x W x D). Used by ND-100, ND-500 and ND-5000 large
systems. ND-500 could be delivered as a two-cabinet system, both cabinets the same size.

Card rack: up to 21 cards (ND-06.026.1 EN section 1.5).

Power supply: the ND Multipower Supply is mounted in the **upper part** of the cabinet and
is accessed from the **rear**, plug-in type held by four screws. Source: ND-05.017.01 EN
section 1.3 "Large cabinet", page 12, figure 5.

GAP: the MF-bus card rack tables for the large cabinet are in ND-05.017.01 (figure 3 in its
figure list, "The MF-bus Card Rack (first version)", page 5) but have not yet been
transcribed here.

---

## 4. ND-5000 model range

### 4.1 System types (the CPU generation)

Source: ND-830102.1B EN, *ND-5000 ES Model C Hardware Maintenance Manual*, table 1 "Model
overview", page 12. In repo:
[ND-5000 ES Model C Hardware Maint.](../Reference-Manuals/500/ND-830102.1B%20EN%20ND-5000%20ES%20Model%20C%20Hardware%20Maint.%20Manual-Sintran.md)

| System | ND-5200 | ND-5400 | ND-5500 | ND-5700 | ND-5800 |
|---|---|---|---|---|---|
| I/O processor | ND-120 | ND-120 | ND-120 | ND-120/CX | ND-120/CX |
| Memory shared + local (MB) | 4 + 2 | 4 + 4 | 8 + 4 | 8 + 4 | 16 + 6 |

ND-05.017.01 additionally documents an upgrade path from ND-5800 to **ND-5900/2/3/4**
(its section 2.1.5), so the range extends past ND-5800.

### 4.2 Model C sizes (the disk complement)

Same table 1. The Model C suffix counts 310 MB disks, not CPU power:

| Model | Disk size |
|---|---|
| Model C1 | 310 MB |
| Model C2 | 2 x 310 MB |
| Model C3 | 3 x 310 MB |
| Model C4 | 4 x 310 MB |
| Model C5 | 5 x 310 MB |

Up to five disk units mount in the cabinet (ND-830102.1B page 40, figure 16). Each drive is
mounted on a board and plugs into the backwiring, so replacement needs no cabling.

Backup media: streamer 155 MB standard; options are the ND Gigatape system and an HP
magtape at 1600/6250 bpi, 125 ips.

The optional Gigatape uses 8 mm cartridges holding up to 2.2 GB, standard SCSI interface,
and the drive is **5 1/4" high**. On models C1-C4 it sits in the upper right corner where
disk B normally goes; on model C5 it is mounted in a separate box.
Source: ND-830102.1B section 2.1.6.4, page 39.

That 5 1/4" drive form factor is currently the only absolute size reference visible inside
the figures. DERIVED: a full-height 5 1/4" bay is 146 mm wide x 82.5 mm high by industry
standard, which can be used to scale the undimensioned figures. This is an industry
standard, not an ND-documented number.

### 4.3 Upgrading

Full upgrade in both axes: between models (C1 up to C5, same system) and between systems
(ND-5200 up to ND-5800, same model). Extra memory boards are not included in upgrade kits
and must be ordered separately. Source: ND-830102.1B section 1.3, table 2, page 13.

### 4.4 Model naming seen in the card-rack tables

ND-05.017.01 tables 5 and 6 refer to Compact models **A0-A4**, **A10-A14** and **model B**.
This is an older naming than the ES "Model C1-C5" scheme, and the Model C manual states the
ES Model C "replaces the current ND-5000 Compacts".

GAP: the relationship between A0-A4, A10-A14, B and C1-C5 is not yet established from a
source. Do not assume A4 equals C4.

### 4.5 CPU types

ND-05.017.01 section 1.4 lists ND-5000 basic CPU type 1, type 2 and type 3, the differences
between them, and microprogram versions. Visible in the card rack: CPU type 1 occupies card
positions 1-2, CPU type 2 occupies positions 1-3.

Related analysis in this repo: see the ND-5000 material under `SINTRAN/ND5000/`.

---

## 5. ND tpServer

A packaged product name, **not a distinct cabinet**. The ND tpServer is a preconfigured
ND-5000/DOMINO database server sold as a turnkey bundle: machine, factory-loaded system
disk, SIBAS database software and a menu-driven administration layer.

*"The ND tpServer series is a range of high-performance/high-functionality database servers
... Based on ND-5000/DOMINO technology"*
Source: ND-830127.1 EN, *ND tpServer System Administrator Guide*, Norsk Data, version 1,
April 1989, chapter 1, page 3.
File: `library/libhw/ND-830127-1-EN.pdf` in the sintran.com mirror

Key physical facts from the 1993 edition (ND-830127.3 EN, February 1993, published by
Comma, chapter 1 page 1):

- Available in **two different models**, each in several types
- Full ND-5000 performance range
- Standard support for up to **130 terminals** simultaneously
- Disk capacity **310 to 67510 MB**, expressed as 48 x 1400 + 310
- Standard backup is the Gigatape System (2.2 GB) plus a streamer; 1600/6250 bpi magtape
  optional
- System disk 310 MB split into two SINTRAN directories, PACK-BASIC and PACK-MAIN-SW

Neither tpServer administrator guide contains a dimensions table, and the product post-dates
the 1987 site-planning manual, so it is absent there too.

**RESOLVED by photograph.** A surviving **ND tpServer A25** is pictured at
`Pictures/ronny/FB_IMG_1754589509271.jpg` in the Norsk Data photo archive on the NAS, and it is a
**Compact-shell machine** - the same stepped front, upper recess, operator-panel ledge and
lower panel as the ND-100/CX Compact. So at least this model sits in the 69 x 54 x 76 cm
box. See section 8.7 for the detail.

The tpServer range still spans two models in several types, so this settles the A25 only.
Whether the larger types use the tall cabinet remains unestablished.

Note also that the badge reads **A25**, which extends the Compact "A" model naming discussed
in section 4.4 beyond the A0-A4 and A10-A14 series seen in the card-rack tables. This is
another reason not to assume the A-numbering maps onto the ES Model C1-C5 scheme.

---

## 6. Sources

Ranked by usefulness for physical reconstruction.

### Primary, with real measurements

1. **ND-13.028.1 NO** *Planlegging av datarom*, May 1987, 76 pp.
   `library/libhw/ND-13028-1-NO.pdf` in the sintran.com mirror
   The only source of exact external dimensions found. Chapter 18, page 57.
   An English twin (ND-13.028.1 EN, June 1987) is indexed in the mirror but **not
   downloaded**.

### Primary, with drawings but no dimensions

2. **ND-05.017.01 EN** *ND-5000 Hardware Maintenance*.
   `5000/ND-05.017.01 EN ND-5000 HARDWARE MAINTENANCE-Gandalf-OCR.pdf` in the OCR working folder
   Chapter 1: model range, both cabinets, card racks, power supplies, CPU types. The repo
   markdown copy is table-of-contents only, so use the PDF.
   In repo (TOC only): [ND-5000 Hardware Maintenance](../Reference-Manuals/500/ND-05.017.01%20EN%20ND-5000%20HARDWARE%20MAINTENANCE.md)

3. **ND-830102.1B EN** *ND-5000 ES Model C Hardware Maintenance Manual*.
   `5000/ND-830102.1B EN ND-5000 ES Model C Hardware Maint. Manual-Sintran-OCR.pdf` in the OCR working folder
   Chapter 2 is an explicit physical description: cabinet, panels, fan tray, operator panel,
   backwiring, card crate, plug-in modules, disk positions. Figures lost in the repo markdown.
   In repo: [ND-5000 ES Model C Hardware Maint.](../Reference-Manuals/500/ND-830102.1B%20EN%20ND-5000%20ES%20Model%20C%20Hardware%20Maint.%20Manual-Sintran.md)

4. **ND-06.026.1 EN** *ND-110 Functional Description*, section 1.5 and figure 2
   "ND-110, ND-110 Compact and ND-110 Satellite cabinets", page 11.
   In repo: [ND-110 Functional Description](../Reference-Manuals/ND-06.026-1-EN%20ND-110%20Functional%20Description.md)

### Secondary

5. **ND-830127.1 EN** and **ND-830127.3 EN**, *ND tpServer System Administrator Guide*,
   1989 and 1993.
   `library/libhw/ND-830127-1-EN.pdf` in the sintran.com mirror
   `library/libhw/ND-830127-3-EN.pdf` in the sintran.com mirror

### Primary, with measurements and dimensioned floor drawings

6. **ND-13.014.04 EN Revision A** *Site Preparation and Installation Manual*, August 1985,
   76 pp. `library/libhw/ND-13014-04A-EN.pdf` in the sintran.com mirror
   Pre-dates the ND-5000, but is the **more detailed of the two dimension sources** for
   everything it does cover, and the only one with dimensioned drawings. Fully transcribed
   in section 7. Appendix F pages 51-52 = floor cutouts; appendix H pages 57-64 = the
   per-product specification table; appendix D page 43 = room size and clearances.

### Checked and found to contain nothing physical

- ND-05.020.01 EN *ND-5000 Hardware Description* - architecture only. Its single physical
  remark is relative: "Physical CPU size is only one sixth of the size of the ND-570."
- ND-895560-2-EN, in `Installation/Installation-Description/` - no dimensions.
- All ND-5000 product-info sheets under `Installation/Product-Info/` - no dimensions.

### Where to look next

- ND-13.028.1 **EN** (indexed in the mirror, not downloaded)
- ND-13.014.01 through .04 (indexed, not available)
- ND-13.015.01 NO *Planlegging og installasjonsmanual* (indexed, not available)
- ND-30.002.01 / .02 *SITE Preparation Manual* (indexed, not available)
- ND mechanical / parts drawings - none located in any archive so far

The mirror indexes to grep are `docs\library\library.md` and `docs\library\libhw\libhw.md`
under the sintran.com mirror.

---

## 7. The 1984/85 Site Preparation manual

**Source**: ND-13.014.04 EN, *Site Preparation and Installation Manual*, Norsk Data,
version 4, revision A, August 1985. Copyright 1985. Specification tables carry their own
revision date, **1 December 1984**.
File: `library/libhw/ND-13014-04A-EN.pdf` in the sintran.com mirror

Its preface states it applies to "the entire family of Norsk Data configurations: the
ND-100, the ND-500 system configurations and the Compact model IV". It pre-dates the
ND-5000, so there is nothing on ND-5000 here. What it has instead is finer granularity: one
row per ND product number, and dimensioned floor drawings.

### 7.1 Floor cutout drawings - the only dimensioned drawings found

Appendix F, figure F.1, PDF page 51. These are the drawings a joiner would have worked from
when cutting the raised computer-room floor, so they carry the cabinet **footprint** and the
**cable hole** position in centimetres. All four are drawn with the cabinet front at the top
of the page and the cable cutout at the rear.

| Drawing | Applies to | Footprint W x D (cm) | Cutout W x D (cm) | Cutout placement |
|---|---|---|---|---|
| C | Equipment in **6-module cabinets**: ND-100 CX and File Store | 54 x 91 | 38 x 20 | centred at rear, 8 cm clear each side |
| D | Equipment in **11-module cabinets**: ND-100/500 and File Store | 60 x 91 | 44 x 20 | centred at rear, 8 cm clear each side |
| A | CDC disk drives 33, 37, 66 and 75 MB | 56 x 92 | 26 x 10 | 15 cm clear each side, 20 cm up from rear |
| B | CDC disk drive 288 MB | 59 x 92 | 15 x 15 | right-hand side, 28 cm up from rear |

The 6-module and 11-module footprints agree with the appendix H table below (54 and 60 cm
wide, 92 cm deep), so drawing C is the **6-module ND-100 cabinet**, not the Compact.

Figure F.2 (PDF page 52) gives the same treatment for printers and printing terminals:
Terminet 340, Omni 825 KSR, a 600/900 lpm line printer (60 x 86 cm footprint, 7 x 5 cm
cutout) and the Fujitsu 1000 lpm.

### 7.2 Room size and service clearance

Appendix D, PDF page 43:

- Minimum computer room size **3 x 4 metres**
- Minimum distance between walls and cabinets **60 cm**
- Cabinets stand in a line against a cable duct running behind them

Figure D.1 is a scaled plan of that minimum room with a Terminet 340, an Omni 825, an
ND-100 cabinet, an ND-500 cabinet and a File Store cabinet lined up side by side.

### 7.3 Equipment specification table, 1 December 1984

Appendix H, PDF pages 57 onward. Column meanings are given on page H-1: H/W/D is total
height/width/depth in cm; CABLE is the standard delivered signal cable length in metres with
the maximum length to the farthest unit in parentheses; SIGNAL is C = current loop,
R = RS-232-C, P = parallel; FUSES is L = quick, G = slow, and the manual says always use
automatic fuses. Figures are for 50 Hz / 230 V.

**ND systems** (page H-2):

| ND no. | Product | H x W x D (cm) | Weight (kg) | Power (W) | Fuse |
|---|---|---|---|---|---|
| 178 | ND-100, 6 module cabinet (empty) | 96 x 54 x 92 | 48 | - | - |
| | ND-100 mini configuration | 96 x 54 x 92 | 90 | 400 | 16 A slow |
| | ND-100 midi configuration | 96 x 54 x 92 | 90 | 600 | 16 A slow |
| | ND-100 maxi configuration | 96 x 54 x 92 | 95 | 700 | 16 A slow |
| | ND-100 expansion system | 96 x **108** x 92 | 170 | 1200 | 16 A slow |
| 131 | ND-100/500 cabinet (empty) | 172 x 60 x 92 | 80 | - | - |
| | ND-100/CX mini configuration | 172 x 60 x 92 | 200 | 600 | 16 A slow |
| | ND-100/CX midi configuration | 172 x 60 x 92 | 230 | 1000 | 16 A slow |
| | ND-100/CX maxi configuration | 172 x 60 x 92 | 250 | 1600 | 16 A slow |
| | ND-520/1 cabinet maxi | 172 x 60 x 92 | 300 | 2400 | 25 A slow |
| | ND-540/1 cabinet maxi | 172 x 60 x 92 | 300 | 2400 | 25 A slow |
| | ND-550/1 and ND-560/1 cabinet | 172 x **120** x 92 | 550 | 4300 | 16/25 A slow |
| | Expansion cabinet maxi | 172 x 60 x 92 | 270 | 2700 | 25 A slow |
| | ND-500/2: ND-530/550/560/570 I | 172 x 60 x 92 | 300 | 2500 | 25 A slow |
| | ND-500/2: ND-530/550/560/570 II | 172 x **120** x 92 | 550 | 4300 | 16/25 A slow |
| | ND-500/2: ND-530/550 III | 172 x 60 x 92 | 350 | 3000 | 25 A slow |
| **092** | **ND-100 COMPACT IV** | **67 x 54 x 74** | **90** | **600** | 16 A slow |
| 624 | Filestore cabinet maxi | 96 x 54 x 74 | 40 | 1000 | 16 A slow |
| 625 | Filestore cabinet maxi | 96 x 54 x 92 | 48 | 1000 | 16 A slow |
| 635 | Filestore cabinet maxi | 172 x 60 x 92 | 80 | 2300 | 25 A slow |

The 120 cm widths are two 60 cm cabinets standing side by side, and the 108 cm width is two
54 cm cabinets - the fuse entry "16/25 A" for the 120 cm rows confirms two separate mains
feeds. That matches the 1987 manual's "ND-500 models, 2-cabinet" row.

**Disk units** (page H-4), the entries that carry a cabinet:

| ND no. | Product | H x W x D (cm) | Weight (kg) | Power (W) | Fuse |
|---|---|---|---|---|---|
| 514 | CDC 66/75 MB | 92 x 56 x 92 | 110 | 700 | 16 A slow |
| 572 | CDC 150 MB in ND-178 | 96 x 54 x 92 | 105 | 600 | 10 A slow |
| 574 | CDC 288 MB | 92 x 59 x 92 | 252 | 1300 | 25 A slow |
| 576 | CDC 37 MB | 92 x 56 x 92 | 110 | 750 | 16 A slow |
| 579 | CDC 150 MB in ND-514 | 92 x 56 x 92 | 167 | 1300 | 16 A slow |
| 585 / 586 / 587 | CDC 30 / 60 / 90 MB in ND-178 | 96 x 54 x 92 | 128 | 950 | 16 A slow |
| 610 / 611 | Winchester 23 / 45 MB, Compact and Satellite | 9 x 15 x 21 | 3.5 | 35 | - |
| 613 | Winchester 150 MB, excluding power supply | 13 x 22 x 38 | 14 | 150 | - |
| 615 / 616 | Winchester 450 / 300 MB, excluding power supply | 26 x 22 x 77 | 35 | 200 | - |
| 617 | Cartridge 75 MB, excluding power supply | 26 x 22 x 77 | 32 | 200 | - |
| 624 | **Filestore cabinet COMPACT** | **67 x 52 x 74** | 140 | - | 16 A slow |
| 625 | Filestore cabinet ND-100 | 96 x 54 x 92 | 175 | - | 16 A slow |
| | Power supply for ND-613 | 10 x 22 x 24 | 6 | 180 | 16 A slow |
| | Power supply for ND-615/616/617 | 25 x 20 x 12 | 5 | 100 | 16 A slow |

Product number 624 appears **twice on the same page** with different figures (67 x 52 x 74
at 140 kg, and 96 x 54 x 74 at 40 kg), and 625 likewise. UNVERIFIED: the second pair looks
like the empty cabinet and the first like the populated one, but the manual does not say so.

Note the Compact Filestore here is 52 cm wide, not 54. That is the only place a 52 turns up.

**Magnetic tape units** (page H-5):

| ND no. | Product | H x W x D (cm) | Weight (kg) | Power (W) | Fuse |
|---|---|---|---|---|---|
| 524 | Pertec 45/800 cpi in ND-178 | 89 x 54 x 100 | 87 | 360 | 16 A slow |
| 528 | Pertec 75/1600 cpi | 89 x 54 x 100 | 118 | 490 | 16 A slow |
| 529 | Pertec 75/800-1600 cpi | 172 x 60 x 100 | 118 | 490 | 16 A slow |
| 543 | STC 125/1600-6250 in ND-131 | 172 x 60 x 100 | 234 | 1850 | 25 A slow |
| 621 | Cipher 1600/3200 bpi | 23 x 44 x 63 | 38 | 270 | 16 A slow |

Note the 100 cm depth: a tape cabinet is **8 cm deeper** than the 92 cm computer cabinet.

**Communication equipment** (page H-8), useful because these boxes appear in photographs:

| ND no. | Product | H x W x D (cm) | Weight (kg) | Power (W) |
|---|---|---|---|---|
| 680 | NCT controller, 110-7680 baud | 13 x 45 x 42 | 15 | 160 |
| 682 | NCT trackerball | 10 x 18 x 17 | 3 | - |
| 677 | NCT keyboard | 9 x 46 x 19 | 2 | - |
| 750 | Limited distance modem KM-1D | 5 x 8 x 15 | 0.5 | 10 |
| 840 | Line driver for line printer | 19 x 22 x 27 | 5 | 50 |
| 845 | Terminal switch panel | 86 x 57 x 38 | 27 | - |
| 846 | Line printer and magtape switch | 10 x 22 x 34 | 3 | - |
| 849 | Terminal cross-coupler | 32 x 25 x 21 | 3 | - |

### 7.4 Where the 1984 and 1987 tables disagree

| Machine | 1984 (ND-13.014.04) | 1987 (ND-13.028.1) | Difference |
|---|---|---|---|
| Compact | 67 x 54 x 74 (ND-100 Compact IV) | 69 x 54 x 76 (ND Compact) | 2 cm taller, 2 cm deeper |
| Large cabinet | 172 x 60 x 92 | 169 x 60 x 95 | 3 cm shorter, 3 cm deeper |
| Compact Filestore | 67 x 52 x 74 | 69 x 54 x 76 | 2 cm each way, 2 cm narrower |

Width is the one dimension both agree on for the large cabinet (60 cm) and the Compact CPU
(54 cm). Height and depth move by 2 to 3 cm.

I do not know which figure is correct. What I can verify is that they are three years apart
and describe partly different product generations - "Compact model IV" in 1984 versus "ND
Compact models" as a family in 1987. UNVERIFIED possibilities, none of them confirmed by any
source: a genuine mechanical revision between generations; one table measuring the bare
cabinet and the other including a plinth or door handles; or simple rounding in one of them.

For 3D modelling: the two sets bracket each other within 3 cm. If the model is of an
**ND-5000 Compact** specifically, use the 1987 figures (69 x 54 x 76), because the 1984
manual pre-dates the ND-5000 entirely and its Compact row is a different machine.

### 7.5 Everything else in this manual

Not transcribed, but present and worth knowing about:

- Chapter 1: computer room size, service access, raised floor construction, holes in the
  data floor, floor covering, air conditioning, mains voltage and permitted fluctuation,
  battery backup, start current, terminal wiring, grounding, electrical disturbance,
  cleaning rules
- Chapter 2: room inspection, visual check on delivery, shipping locks, panel removal,
  cabling, power-up sequence for one and for several systems
- Appendix C: mains installation, the 25 A outlet type (CUI 232-6 + CR 32), and a full
  10 kVA distribution schematic
- Appendix E: grounding, minimum 25 mm squared to the building equipotential connection,
  10 mm squared braided copper lace for each cabinet, with three room-layout figures
- Appendix I: maximum cable lengths per baud rate and interface type, plus complete pin-out
  tables for current loop and V.24 to every supported terminal and printer

---

## 8. Photographic and physical evidence

Sources here are photographs and marketing material rather than manuals. They carry
information the manuals do not: construction breakdown, front-face layout, and colour.

Location: the Norsk Data photo archive on the NAS

### 8.1 A third dimension figure, from ND's own marketing

The NORD-100 sales brochure states plainly:

*"Only 54 cm wide, 96 cm high and 84 cm deep, the NORD-100 cabinet is easily situated as
any copier or filing cabinet."*
Source: `Pictures/Reklame/images/nd-7.jpg` in the Norsk Data photo archive on the NAS, brochure page 7.
The full brochure is at `Pictures/Reklame/nord-100 computer system.pdf` in the Norsk Data photo archive on the NAS.

Height 96 cm and width 54 cm agree **exactly** with the 1984 service table for the 6-module
ND-100 cabinet. Depth is quoted as 84 cm against the service table's 92 cm.

So the depth of the ND-100 6-module cabinet now has two conflicting published values, 84 and
92 cm, both from Norsk Data. I do not know which is right. UNVERIFIED: 84 cm may be the
cabinet body and 92 cm the body plus a rear cable allowance or a projecting rear panel, but
nothing in either document says so. Width and height are corroborated and can be trusted.

The same page also gives a power figure of 450 W for the NORD-100, against the service
table's 400 to 700 W depending on configuration.

### 8.2 The ND-100 cabinet front face

The brochure photograph on that page is a near square-on colour shot of the 6-module ND-100
cabinet. Read off it directly, with no measurement involved:

- The front is a **light grey frame** surrounding **six equal horizontal module bays**. The
  "6 module cabinet" product name is literal - it is six visible bay positions.
- The frame's **top rail carries the "ND NORSK DATA" logo**, right-aligned.
- Bay contents in the photographed machine, top to bottom:
  1. vent panel, fine horizontal slots
  2. the operator panel: two display windows at the left, a wide horizontal display strip,
     two switches, the "ND NORD-100" legend, and a keyswitch at the right
  3. dark panel with a single row of large round holes
  4. dark panel with a single row of large round holes
  5. plain dark panel, no holes
  6. dark panel with a single row of large round holes
- Below the bays is a light grey base rail, and below that a **plinth recessed behind the
  front face**, so the cabinet does not meet the floor flush.

Colour scheme, from this photograph and the peripherals spread
(`Pictures/Reklame/images/building-block-1-2.jpg` in the Norsk Data photo archive on the NAS): frame and plinth
in a light warm grey or off-white, module fronts in a very dark brown-black, and **signal
red** used as the accent on terminals, printers and disk drives.

GAP: the **proportions of those six bays are not recorded here**, and the attempt to recover
them failed. This is worth stating plainly so nobody repeats it.

Careful edge-finding put the cabinet frame at 364 px wide (rails at x=282 and x=646) and
675 px tall (frame top at y=1141, plinth bottom at y=1816) in
`Reklame\images\nd-7.jpg`. That gives an aspect ratio of 0.539, where the published 54 x 96
cm implies 0.5625 - **4 percent out**.

The cause is that this is a **phone photograph of a bound brochure lying on a table**, not a
flat scan, so the page curves and the scale varies across it. A perspective rectification
assumes a flat plane and therefore cannot fix page curvature. On top of that the cabinet is
very dark and low contrast, so automatic detection of the bay separators failed: only the
top rail, the operator panel and the plinth stood out from the background brightness, and
repeated visual readings against an overlaid percentage grid did not agree with each other
to better than a couple of percentage points.

Any bay heights derived this way would be wrong by two to three centimetres at full size, so
none are given. Closing this needs one of:

- a **flat scan** of brochure page 7 rather than a photograph of it, which would remove the
  page curvature and make the rectification valid
- a **square-on photograph of a real cabinet**, ideally with a scale in frame
- a measurement of a real cabinet

Note that the technique which succeeded on the operator panel (section 8.3) does not apply
here: it needs a known physical grid inside the photograph, and a painted cabinet front has
no such grid.

### 8.3 The ND-5000 Compact operator panel

There is **not one panel part but a family of at least two variants**, same size and layout,
differing in the keyswitch legend. Do not treat them as interchangeable when modelling a
specific machine.

| Part | PCB | Keyswitch legend | Seen on |
|---|---|---|---|
| **ND-323163** | ND **1835B** | LOCKED / ON / STANDBY | the photographs measured below; also the ND-100/CX Compact and the tpServer A25 |
| **ND-323165** | ND **1844B-2** | ON LOCK / ON / OFF | `Code/68705/ND-5000C-PANEL.png` in the nd-120 repository |

The 1844 board additionally carries a **TELEFIX** silkscreen legend near its lower edge.

Both are the same size. Measured aspect ratio is **8.62** for the 1835 board and **8.69**
for the 1844 board, agreeing to 0.8 percent, so the 455 x 53 mm below applies to both.

**ND-322691, the older ND-100 "Display Panel N100"**, is a different shape entirely - a
squat block, measured aspect **1.847 : 1**. Its absolute size could not be measured; the
pad-grid method failed on that board because it lacks the long uniform pad rows the Compact
board has. ASSUMPTION, directed by the repository owner: its width is the **same 455 mm** as
the Compact panel, both being fitted to the same 540 mm cabinet family. On that assumption
its height is 455 / 1.847 = **246 mm**, giving **455 x 246 mm**. The aspect is measured; the
width is assumed and the height is derived from the assumption.

Related part numbers, from `Code/68705/readme.md` in the nd-120 repository, which also
records that the panel is driven by an **MC68705P3** microcontroller (the ND-120 CPU board
uses a different one, an MC68705U3):

- 323165, PCB 1844 - Panel Operator including display, ND-5000C
- 324494, PCB 1834 - Panel Control
- 324147, PCB 1844 - Telefix / Driver Comson

#### The measured variant, part ND-323163 / PCB 1835B

Three photographs, all square-on:

- `Pictures/ND-5000-Compact/nd-323163-B1.jpg` in the Norsk Data photo archive on the NAS - component side
- `Pictures/ND-5000-Compact/nd-323163-B2.jpg` in the Norsk Data photo archive on the NAS - solder side, board
  marked **ND 1835B**, legend "S SIDE"
- `Pictures/ND-5000-Compact/nd-323163-B3.jpg` in the Norsk Data photo archive on the NAS - the membrane switch
  layer behind the buttons, made by **Hoffmann & Krippner GmbH, D-6967 Buchen**, marked
  831284 / 1186 / 871088

The panel is a long black anodised fascia strip on a green PCB. Layout, left to right:

1. A wide amber display window. Labels printed above it read **UTILIZATION, CACHE HIT RATE,
   PROTECT RING, INTERRUPT, PAGING**.
2. Immediately below the window, a numeric scale printed **15 14 13 12 11 10 9 8 7 6 5 4 3 2
   1 0**, captioned **ACTIVE LEVEL**. Values 14, 13, 12 and 8, 7, 6 are shown reversed out.
3. Six square pushbuttons, in two groups of three with a gap between the groups.
4. At the far right a keyswitch, with the positions labelled **LOCKED** at the top, **ON**
   at the middle left and **STANDBY** at the bottom.

This is the angled dark strip visible on the front of the cabinet in figure 3 of
ND-05.017.01.

#### Measured dimensions of the operator panel

These are the **first hard millimetre dimensions of any ND cabinet part** obtained in this
work. They are measured, not estimated.

| Part | Width | Height |
|---|---|---|
| Black fascia (the visible front plate) | **455 mm** | **53 mm** |
| PCB behind it (ND 1835B) | **451 mm** | **72 mm** |

Tolerance: **+/- 2 percent**, so 455 +/- 9 mm and 53 +/- 1 mm.

**Method.** The photographs contain their own ruler: the board's through-hole pads sit on
the standard 2.54 mm (0.1 inch) grid. Measuring that grid gives an absolute scale for the
image, with no reliance on any assumed dimension.

1. The pad pitch was recovered by autocorrelating the brightness profile along horizontal
   pad rows, then fitting the position of up to 30 successive autocorrelation harmonics
   through the origin, which averages the error over a long baseline.
2. On the solder side (B2) six independent strips gave 25.812 px per 2.54 mm, standard
   deviation 0.194 px (0.75 percent).
3. On the component side (B1) forty-six independent strips gave 25.858 px, standard
   deviation 0.746 px, standard error 0.11 px.
4. The two photographs are different shots of the same board and their scales agree to
   **0.2 percent**, which is the main reason to trust the result.
5. Panel edges were then found by classifying pixels as neutral-dark (the anodised fascia)
   against green-dominant (bare PCB), which cleanly separates the two.
6. Panel height was measured in three separate plain column bands - the left margin, the
   right margin, and the gap between the display and the buttons - giving 52.7, 53.2 and
   52.2 mm. Agreement to about 1 percent.

**Cross-check**: a 455 mm panel in a 540 mm wide cabinet leaves about 42 mm each side for
the frame. That is consistent with the cabinet proportions and is an independent reason to
believe the number. The panel occupies **84 percent of the cabinet width**.

Scripts used are in the session scratchpad and are not part of the repository.

### 8.4 A surviving ND-100/CX Compact, photographed

`Pictures/ND-100_CX_Compact_front.jpg` in the Norsk Data photo archive on the NAS (square-on front)
`Pictures/ND-100_CX_Compact_front_upper.jpg` in the Norsk Data photo archive on the NAS (upper section, angled)
`Pictures/ronny/*.jpg` in the Norsk Data photo archive on the NAS (the same machine in situ, six shots, one with
the covers off and the operator panel powered up)

This is a **running machine, owned by the repository author**, so it is the authoritative
physical reference for the Compact cabinet and supersedes any measurement taken from print.

#### Colour - correction to section 8.2

The Compact is **brown**. A warm mid-brown or bronze body with a **silver-grey badge strip**
across the top carrying "ND Norsk Data" at the left and the model name at the right in dark
grey lettering. Recesses and the operator panel are black.

This does **not** match the off-white-with-red scheme of the earlier NORD-100 brochure in
section 8.2. Both are correct for their own generation: the late-1970s NORD-100 cabinet was
light with red accents, the mid-1980s Compact is brown. Pick the scheme to match the machine
being modelled, not the family.

#### Front face, top to bottom

1. **Badge strip.** Silver-grey, full width, at the very top. "ND Norsk Data" left,
   "ND-100/CX Compact" right.
2. **Upper recess.** A deep black-lined recess split into two compartments by a vertical
   divider:
   - **left**: the drive module - a black bezel holding a **QIC streamer above** (green LED
     at its lower left) and a **5 1/4 inch floppy below** (lever latch, red LED at its
     right), with a column of vent slots down its left side and a second column of louvres
     down its right side
   - **right**: a large plain dark blanking panel, roughly the same width
3. **Operator panel** on a set-back ledge under the recess - the same part described in
   section 8.3.
4. **A pronounced horizontal step.** The whole upper section overhangs the lower section, so
   the cabinet is not a plain box. This step is the single most distinctive shape feature and
   must be modelled.
5. **Louvred grille panel** filling most of the lower front, inset with a margin all round,
   with roughly thirty horizontal fins.
6. **Plinth**, slightly recessed, with a castor visible at the bottom.

#### Operator panel graphics, read from the powered-up photo

`Pictures/ronny/20230618_193546.jpg` in the Norsk Data photo archive on the NAS

- The display is alphanumeric and was showing **`DAY:02  TIME:12:00:02`**, with bargraph
  segments to its right and the words **OFF** under INTERRUPT and **OFF** under PAGING.
- Button legends are printed **above** each button and are backlit. Lit in that photo:
  **STOP**, **START** and **RUNNING**. Further unlit legends are present but not legible
  enough to transcribe, so they are not recorded here rather than guessed.
- The six buttons are in **two groups of three**, separated by a vertical divider bar.

#### Scale check

Using the 455 mm operator panel from section 8.3 as a ruler inside the square-on photograph,
the panel measures 2455 px across a stable plateau, giving **0.1853 mm per pixel**. On that
scale the whole 2988 x 3688 px frame is 554 x 684 mm - and the cabinet, which nearly fills
the frame, is published at 540 x 690 mm.

That is agreement within a few percent between three independent things: a pad-grid
measurement of a circuit board, a 1987 published dimensions table, and the framing of a
photograph none of them came from. It is good corroboration that the 455 mm figure is right.

It is **not** good enough to publish front-face feature sizes from, because a phone camera
close to a large object has real perspective and lens distortion. Which matters little,
because the machine itself is available to measure - see section 8.5.

### 8.5 MEASURED: the Compact side profile and depth

Taken with a tape from the machine itself by the repository author, 2026-08-02. Photograph
with the measurements marked on it:
`Pictures/ronny/compact-wedge.jpg` in the Norsk Data photo archive on the NAS

**The front of the Compact is a wedge, not a flat face.** The upper front section projects
progressively further forward as it descends, reaching a maximum at the lip where it
overhangs the lower grille section, then steps back. This is the single most important shape
fact about the machine and no manual records it.

Depths, all measured forward from the front face of the main cabinet box:

| Feature | Projection | Total depth |
|---|---|---|
| Main cabinet box | - | **620 mm** |
| Front panel at the **top** | **+50 mm** | 670 mm |
| Wedge at its **maximum**, the overhang lip | **+90 mm** | **710 mm** |
| Lower front section | **+42 mm** | 662 mm |
| Grille, proud of the lower section | **+10 mm** | 672 mm |

So the deepest point of the machine is **710 mm**, at the overhang lip.

#### This does not match either published depth

| Source | Compact depth |
|---|---|
| Measured, this machine | **710 mm** at the deepest point |
| ND-13.028.1 (1987), "ND COMPACT models" | 760 mm |
| ND-13.014.04 (1984), "ND-100 COMPACT IV" | 740 mm |

The measurement is 30 mm short of the 1984 figure and 50 mm short of the 1987 figure.

**Nothing projects rearward.** Confirmed by the owner: the 620 mm was taken from the
rear-most face to the front of the box, so rear-most to front-most is 620 + 90 = **710 mm**
and there is no rear connector panel, duct or foot to account for the difference.

**RESOLVED - see the rear fans section below.** The three fans project 35 mm out of the back
of the cabinet, so the whole-machine depth is 745 mm, not 710. That matches the 1984 table's
740 mm to within 5 mm. The apparent conflict was caused by comparing a cabinet-only
measurement against a published figure that includes the fans.

**Use 710 mm for the cabinet body when modelling**, and add the fans separately.

### 8.4b The ND-100 Satellite front face - GAP CLOSED

Previously recorded here as "no photograph of the front located". Two photographs supplied by
the owner, 2026-08-02, of a surviving **ND-100 Satellite** standing beside the Compact.

NOTE: these two images were pasted into the conversation and are **not on the NAS**, so the
colour sampling done for the Compact could not be repeated numerically for the Satellite.
Everything below is read visually.

Front face, top to bottom:

1. **Badge strip**, cream, reading **"ND Norsk Data"** at one end and **"ND-100 Satellite"**
   at the other.
2. A **recessed bay** in the brown body holding a black drive module:
   - a **tape streamer** on the left
   - a **5 1/4 inch floppy drive mounted rotated 90 degrees**, so its slot and lever run
     **vertically** rather than horizontally. This is a distinctive detail and follows from
     the cabinet being only 230 mm wide - a normally-oriented 146 mm drive plus its
     surrounding structure would not fit as comfortably.
3. A **keyswitch plate**, cream, to the right of the bay, legended **LOCKED** at the top,
   **ON** at the left and **STANDBY** at the bottom, with a **red ring** around the keyhole.
   The same legend set as the Compact's ND-323163 panel.
4. A **button plate**, cream, below, carrying **six square cream buttons in two groups of
   three**, the groups separated by **two vertical scribed lines**. The same 3 + 3 grouping
   as the Compact.
5. A **louvred grille** filling the lower front.

**Colour**: the cabinet brown and the cream of the badge and plates match the Compact, as
reported by the owner.

**But the control surfaces are finished differently.** On the Compact the operator panel is a
**black** fascia with pale legends. On the Satellite the keyswitch plate and the button plate
are **cream** with dark legends - the inverse. The cabinet colours are shared; the panel
treatment is not. The Satellite also has **no display**, only the buttons and keyswitch.

### 8.4b-2 The badge is an applied label, not a full-width band

CORRECTION to earlier drafts of this work, which showed the badge as a full-width strip
running edge to edge and flush with the top of the cabinet. That is wrong.

The badge is a **separate light-coloured label attached to the front panel**, with **rounded
ends**, and it sits with **5 mm of front panel visible above it and 5 mm below**. It does not
touch the top edge and it does not run the full width.

The text is the same layout on every machine - the maker at the left, the model at the right:

| Machine | Badge text |
|---|---|
| ND-100/CX Compact | ND Norsk Data ... ND-100/CX Compact |
| ND-100 Satellite | ND Norsk Data ... ND-100 Satellite |
| ND tpServer A25 | ND Norsk Data ... ND tpServer A25 |
| ND-5830 | ND Norsk Data ... ROBIN ... ND-5830 |

The model part varies with the machine - ND-110/CX and ND-5000/CX badges exist on the same
shell. So for a model, the badge is a **decal on the front panel**, not moulded geometry.

### 8.4c The ND logo - exact dot-matrix construction

The "ND" mark on the badge strip is **not type**. It is a logo built from discrete round
dots on a regular square grid, and it appears this way on every machine seen here - the
ND-100/CX Compact, the ND-100 Satellite, the ND-5830 and the tpServer - varying only in
colour.

Extracted from `Pictures/logo/Logo_Big.png` in the Norsk Data photo archive on the NAS by detecting the dot rows
and columns and sampling each grid intersection. A matching KiCad footprint of the same logo
exists at `Pictures/logo/nd-logo.kicad_mod` in the Norsk Data photo archive on the NAS, generated by
bitmap2component, if exact vector outlines are wanted.

**Grid: 18 columns x 8 rows.** Pitch is square, measured at 54.0 px horizontally and 53.5 px
vertically in that image - equal within measurement error.

```
        N                    D
   1    # # # . . . # # #    # # # # # # # . .
   2    # # # # . . # # #    # # # # # # # # .
   3    # # # # # . # # #    # # # # # # # # #
   4    # # # # # # # # #    # # # . . . # # #
   5    # # # # # # # # #    # # # . . . # # #
   6    # # # . # # # # #    # # # # # # # # #
   7    # # # . . # # # #    # # # # # # # # .
   8    # # # . . . # # #    # # # # # # # . .
```

- The **N** is columns 1-9: a three-column left stem, a three-column right stem, and a
  diagonal descending left to right between them.
- The **D** is columns 10-18: a three-column left stem and a bowl whose right edge steps in
  by one column at rows 1-2 and 7-8, giving the rounded corners, and which is hollow for
  three columns at rows 4-5.
- Total: **120 dots**.

**Dot size**: total ink area divided by 120 dots gives a dot diameter of about **50 px
against a 54 px pitch**, so the dot diameter is close to **0.93 of the grid pitch**. The dots
very nearly touch but do not.

**Letter spacing**: the gap between the last N column and the first D column measures 80 px
centre to centre, against the regular 54 px pitch - so the inter-letter gap is about
**1.5 pitches**, not 1.

To reproduce at any size: lay out an 18 x 8 square grid of pitch p, place a circle of
diameter 0.93p at each marked position, and widen the single gap between column 9 and
column 10 to 1.5p.

#### Panel breakdown - THE MANUAL DESCRIBES THIS

The cabinet is not a single shell. **ND-830102.1B EN**, *ND-5000 ES Model C Hardware
Maintenance Manual*, section 2.1.1 "Panels", states how each one comes off, and that is
effectively a parts list for moulding:

| Panel | How it is fixed | Count |
|---|---|---|
| **Front panel** | *"Remove the screw located at the top of the panel. Lift the panel slightly and pull it away."* | 1, single screw |
| **Side panels** | *"Turn the two screws on the top of the side panels 1/2 turn counterclockwise and lift the panel away."* | 2, one per side |
| **Top panel** | *"Remove the four screws holding the top panel and lift it away."* | 1 |
| **Rear panel** | *"Remove the four screws holding the rear panel and lift it away."* | 1 |

Source: ND-830102.1B section 2.1.1, manual pages 6-7, figures 2 and 3.

So the correct part breakdown for a model is **five mouldings**: front, two sides, top, rear.
The front panel is confirmed as a **separate part** both by the manual and by the visible
vertical seam in `compact-grill-side.jpg`. Note that the manual gives the front panel its own
figure, figure 2, separate from figure 3 which covers the other three.

#### Colour - the front panel is NOT the same colour as the rest

Reported by the owner and confirmed by sampling the photograph
`Pictures/ronny/compact-wedge.jpg` in the Norsk Data photo archive on the NAS. Median colour of each surface:

| Surface | Hue | Saturation |
|---|---|---|
| **Front fascia**, upper | 15.5 deg | 23.7 percent |
| **Front fascia**, lower | 17.8 deg | 20.6 percent |
| **Side panel**, upper | 26.7 deg | 11.8 percent |
| **Side panel**, lower | 31.0 deg | 17.6 percent |
| **Top panel** | 15.7 deg | 9.8 percent |

The front fascia is consistently **redder** (hue about 16 to 18 degrees) and **roughly twice
as saturated** as the side panel (hue about 27 to 31 degrees). In plain terms the front is a
warm red-brown and the rest of the cabinet is a lighter, greyer, more neutral brown.

CAVEAT: the two surfaces face different directions and are differently lit, and lighting
shifts apparent colour. Lightness in particular is not comparable between them. Hue and
saturation are more robust to this than lightness, and the hue gap of 12 to 15 degrees is
larger than lighting alone would usually produce on identical paint. Combined with the
owner's direct observation of the real object, **treat the front panel as a different colour
from the rest of the cabinet.** Exact paint values would need a colour card held against
both surfaces in the same light.

#### The top section is three planes, not one

From `Pictures/ronny/compact-top-1.jpg` in the Norsk Data photo archive on the NAS, `compact-top-2.jpg` and
`compact-top-3.jpg`, plus the owner's description. The upper front is **not** a single
sloping face with things stuck on it:

| Plane | Orientation | Carries |
|---|---|---|
| **A** outer wedge face | angled, part of the main wedge | the badge label |
| **B** recess back wall | **vertical, parallel to the side panels** | the two black modules - drive bay left, blank right |
| **C** operator panel face | angled, projecting **outward** toward the lip | display, buttons, keyswitch |

Between A and B the opening is edged by a **sloping wall** - clearly visible in
compact-top-2.jpg as a chamfer running back and inward from the outer face to the inner
wall. That the black modules hang vertically while the surround is angled is the reason the
recess looks so deep at the bottom and shallow at the top in photographs.

Measurements supplied by the owner, 2026-08-02, pending the clarification requested below:

- outer border at the left and right: **20 mm** on the outer face, **30 mm** where it meets
  the inner wall - a 10 mm horizontal run across the sloping wall
- on the inner wall, margin to the black area: **20 mm** left and right, **8 mm** above,
  **30 mm** below
- brown divider between the two black areas: **12 mm**

Derived, if the border figures apply symmetrically across the full 540 mm width: the opening
is **500 mm** wide at the outer face and **480 mm** at the inner wall, giving **440 mm** of
black across both modules, or **428 mm** once the 12 mm divider is removed.

GAP: the angle of the sloping wall cannot be computed from the 10 mm run alone - it needs
the recess depth. See the open measurement list.

#### The machine stands clear of the floor on castors

The whole cabinet is lifted roughly **10 mm** off the floor by castors it rolls on. This
reinterprets an earlier figure: the note that "the grille section starts about 10 mm from
the bottom" is **not** a feature of the panel. It is the castor clearance under the whole
machine.

The **front panel's bottom edge aligns with the bottom of the metal frame** - they finish at
the same level, 10 mm above the floor. So from the front, the frame does not show below the
panel.

The wheels themselves are **out of scope for the model** and are not drawn.

UNCONFIRMED: whether the published 690 mm height is floor-to-top including the castor lift,
or the cabinet body alone. If it includes the lift, the body is 680 mm. This matters only at
the millimetre level and is noted rather than assumed.

#### The base frame, and the two-tone scheme

Reported by the owner: the ND-100 Compact has a **metal frame, 40 mm**, at the base, which
the side panels **rest on**. The frame is finished in the **same colour as the front panel**.

That completes a coherent **two-tone scheme**, and it explains the colour measurements above:

| Colour | Parts |
|---|---|
| **Darker warm red-brown** | front panel, base frame |
| **Lighter, greyer brown** | side panels, top panel |
| Cream | badge strip |
| Black | operator panel fascia, drive bezels, recess linings |

So the dark colour marks the **structure** - the frame and the front moulding attached to it -
and the light colour marks the **removable covers**. For a model, paint the front and the
40 mm base band in one colour and the sides and top in the other.

POSSIBLE RESOLUTION of the open conflict recorded further down: the earlier figure of
*"4.2 cm"* at the bottom of the machine may have been **this 40 mm frame**, a vertical
height, rather than a forward projection. The two numbers agree to 2 mm. This is a
suggestion, not a confirmation - the owner should say whether the 4.2 cm was the frame
height or a depth.

#### Three ribs along the top of the side panel

Visible in `compact-wedge.jpg`: **three** horizontal rounded ribs, or flutes, running
front-to-back along the top edge of the side panel, with a dark line above them which is
almost certainly the **seam where the top panel meets the side panel**.

UNVERIFIED: in the photograph these read as **solid rounded mouldings, not open vents** - no
openings are visible in the relief. They may be purely decorative, or they may be vents that
simply do not show at this angle. Worth a look at the real machine, since it decides whether
the model needs slots cut or just surface relief.

#### The shape of the lip - CORRECTED, from photographs

The wedge does **not** step straight back from its maximum projection to the grille. Verified
by zooming into `Pictures/ronny/compact-grill-side.jpg` in the Norsk Data photo archive on the NAS, the profile
below the maximum is, in order:

1. a **rounded external corner** at the nose, not a sharp 90 degree edge
2. a straight **diagonal return** running downward and backward toward the cabinet
3. a large, smooth **concave fillet**
4. a narrow **vertical fascia member** continuing down beside the grille, standing proud of
   the main side panel

The same photograph shows a **vertical seam** between the side panel and the fascia, so the
front fascia is a **separate moulding**, not part of the side pressing.

NOT MEASURABLE from the photograph, and therefore not given numbers here: the nose radius,
the angle and length of the diagonal return, the fillet radius, the width of the lower
vertical member, and the exact height of the nose. The photograph is taken close and from
below, so any angle read off it carries perspective error. These are listed as items A to G
in the measurement sheet below.

#### The lower front and grille - MEASURED

Measured by the owner, 2026-08-02. Photographs:
`Pictures/ronny/compact-grill-front.jpg` in the Norsk Data photo archive on the NAS,
`compact-grill-side.jpg`, `compact-grill-side-bottom.jpg`

Heights are from the floor. Projections are forward of the main box front face.

| Feature | Measurement |
|---|---|
| Bottom of the lower front section | **10 mm** above the floor |
| A **45 degree chamfer** at its base, running | **20 mm** |
| Front face of the grille section | **+45 mm** |
| From the top of the chamfer up to the wedge | **350 mm** |
| Height at which the wedge begins to project | **370 mm** |
| Top part of the grille panel that is **flat**, no louvres | **80 mm** |
| Number of louvres | **17** |

**CORRECTION.** Earlier drafts of this document placed the grille face at **+20 mm**. That
was wrong and it made the overhang look far deeper than it is. The 20 mm figure is the
**run of the 45 degree chamfer at the base**, not the position of the grille face.

The front panel projects **45 mm** at the bottom, measured from the side panel to the front
panel below the grille - the point at which the metal part of the cabinet begins. With that
correction the three projections form one coherent profile:

| Height | Projection forward of the side panel |
|---|---|
| Roof, 690 mm | **+50 mm** |
| Lip, about 375 mm | **+90 mm** |
| Grille face, 30 to 370 mm | **+45 mm** |
| Bottom of the chamfer, 10 mm | **+25 mm** |

So the lip stands only **45 mm** proud of the grille face, not 70. The front reads as a
single moulding with a modest lip, which is what the photographs show.

Derived from those: the louvred area is 350 - 80 = **270 mm** tall, so the louvre pitch is
about **16 mm**.

**Cross-check on the louvre count.** Counting ridges automatically in four separate vertical
strips of the close-up photograph gave 16, 16, 16 and 18. That brackets 17, the difference
being whether the topmost and bottom-most ridges are caught at the edge of the band. The
owner's count of 17 stands and the photograph supports it.

#### ONE OPEN CONFLICT in the lower front projection

Two different figures have been given for how far the bottom of the machine projects:

- earlier: *"on the bottom 4.2 cm + 1 cm grill"* - suggesting about **42 mm**, possibly 52
- later: *"the grill section is actually 2 cm out"* - **20 mm**

These cannot both describe the same thing. Two readings are possible and I cannot tell which
is right from the photographs:

- **Reading A**: the chamfer runs from flush with the box at 10 mm height, outward and upward
  to +20 mm at 30 mm height. The lower front then sits at +20 mm all the way up. Under this
  reading the 42 mm figure referred to something else.
- **Reading B**: the grille face is at +20 mm and the chamfer flares *further* outward toward
  the base, reaching roughly +40 mm at the very bottom - which would explain the earlier
  42 mm as the projection at the extreme base.

**Reading A is drawn**, because it follows the most recent and most specific description.
The question that settles it: *at the very bottom of the machine, just above the floor, does
the front stick out further than the flat grille face above it, or less?*

#### Rear fans - MEASURED

**Three fans** are mounted on the **rear face** and project **rearward**. They are *not* on
the top surface; an earlier note in this document said they were and that was wrong.

| Feature | Measurement |
|---|---|
| Number | **3** |
| Size, each | roughly **120 x 120 mm** square |
| Projection **rearward** of the cabinet | **35 mm** |
| Spacing between adjacent fans | **30 mm** |
| Top of the fans, measured **down** from the cabinet top | **40 mm** |

Derived: three fans at 120 mm with two 30 mm gaps span **420 mm** of the 540 mm width,
leaving 120 mm to distribute. Whether the group is centred is **not confirmed**; if it is,
there is 60 mm clear at each side. The fans occupy heights 530 to 650 mm above the floor.

#### This resolves the depth conflict

Because the fans stick out of the back, the true rear-most to front-most span is not the
710 mm of the cabinet alone:

    35 (fans)  +  620 (box)  +  90 (wedge)  =  745 mm

| Source | Depth |
|---|---|
| Measured, **cabinet alone** | 710 mm |
| Measured, **including the rear fans** | **745 mm** |
| ND-13.014.04 (1984), ND-100 Compact IV | **740 mm** |
| ND-13.028.1 (1987), ND Compact models | 760 mm |

745 measured against 740 published is a **5 mm agreement**, which for a hand tape against a
rounded published figure is about as close as this gets. The 1987 figure of 760 sits 15 mm
beyond that, consistent with a site-planning table rounding up or allowing a little air
behind the fans so they are not blocked.

**So the manuals were not wrong - the earlier comparison in this document was measuring the
cabinet against a figure that includes the fans.** The three-way conflict recorded above is
withdrawn.

**For modelling**: use **710 mm** for the cabinet body and add the fans as separate parts.
Use 745 mm only when the question is how much floor the machine needs.

DERIVED, not stated by the owner: a 120 mm square fan standing 35 mm proud is almost
certainly the industry-standard **120 x 120 x 38 mm** fan, a size still manufactured. The
2 mm difference between 35 and 38 is consistent with the frame sitting slightly sunk into
the roof aperture. This is an inference from a standard part size, not a measurement.

NOT measured: where the group of three sits across the width, and how far forward of the
rear edge. Three 120 mm fans occupy 360 mm of the 540 mm width, so there is 180 mm to
distribute, but how it is distributed is unknown.

The fans do **not** affect the height, since their tops sit 40 mm below the cabinet top.

#### The cabinet is a square box - the sections are NOT different widths

Confirmed by the owner. The upper and lower sections are the **same width**; the cabinet is
square in plan. In photographs the lower section often appears inset at the sides, but that
is only the camera angle combined with the lower section sitting 48 mm further back. Do not
model a narrower lower box.

#### Still needed for the side profile

The depths above are complete. The **heights at which they occur are not measured**, so the
wedge can be drawn in section but not yet positioned:

- height from the floor to the **overhang lip** - where the +90 mm maximum occurs
- height from the floor to the **top of the lower grille section**
- whether the wedge face is a straight slope or a series of steps

### 8.6 Measurement sheet for the ND-100/CX Compact

The machine exists and is accessible, so these should be taken with a tape rather than
derived from photographs. Take every measurement in **millimetres**. Where a part is
recessed, note the recess depth as well as the face size.

**Overall**
1. Total height, floor to top surface
2. Total width at the widest point
3. Total depth, front face to rear face
4. Whether the top surface is flat, and any lip or moulding around it

**The step** (the defining feature)
5. Height from floor to the top of the lower section, where the overhang begins
6. How far the upper section projects forward beyond the lower section
7. Whether the upper section is also wider than the lower one, and by how much per side

**Badge strip**
8. Height of the silver strip, and its width
9. Its inset from the cabinet top, left and right ends

**Upper recess**
10. Opening width and height, and recess depth
11. Width of the vertical divider between the two compartments
12. Left compartment opening width; right compartment opening width
13. Drive module bezel width and height (this should be close to a standard 5 1/4 inch
    form factor, so it doubles as a check on everything else)

**Operator panel**
14. Fascia width and height - to confirm or correct the 455 x 53 mm in section 8.3
15. Its inset from the front face, and the height of the ledge it sits on
16. Display window width and height
17. Button size, button pitch, and the gap between the two groups of three
18. Keyswitch centre position from the right-hand end

**Grille**
19. Grille panel width and height
20. Its margin from the left, right, top and bottom of the lower front face
21. Number of fins, and fin pitch (measure across ten fins and divide, for accuracy)

**Base**
22. Plinth height, and how far it is set back from the front face
23. Castor or foot diameter and position

With items 1-3 alone the model shell becomes exact and the 84 / 92 cm depth conflict in
section 7.4 and section 8.1 is settled for the Compact.

### 8.6 Other photographic material not yet examined

In the Norsk Data photo archive on the NAS:

- `ND-100 i Bergen.zip` (22 MB) - not opened
- `ND-100-PANEL\nd-322691-*.jpg` - four photographs of the ND-100 operator panel, part
  ND-322691, same treatment as the ND-5000 panel above
- `Panel Control\nd-324494-*.jpg` - four photographs of panel part ND-324494
- `ND-110_Satellite_back_card_crate_cover.jpg` - 4 MB, the Satellite rear
- `Telemuseum-Oslo-NORD-100-1.jpg`, `NTM TELE 2015 04 A 023 55.jpg` and the DigitaltMuseum
  link - museum photographs of complete machines
- `ND-100 CX.png`, `Nord-100CX.jpg`, `ND10_ND50.png`, `415px-ND-560.jpeg` - product images

---

## Appendix A: Terminals

Source: ND-13.028.1 NO page 59. Signal column: R = RS-232-C, C = current loop.

| ND number | Product | H x W x D (cm) | Weight (kg) | Power (W) | Cable (m) | Signal | Fuse (A) |
|---|---|---|---|---|---|---|---|
| 103190 | TWIST 4440 | 44 x 39 x 35 | 19 | 70 | 6/10 | R/C | 10 fast |
| 103200 | NOTIS models | 31 x 38 x 36 | 14 | 80 | 6/10 | R/C | 10 fast |
| 110002 / 110003 | NORTEXT models | 31 x 38 x 36 | 14 | 80 | 6/10 | R/C | 10 fast |
| 110007 | Colour terminal COLOR-TREND 210 | 38 x 39 x 43 | 17 | 105 | 6/10 | R/C | 10 fast |
| 110140 | TINY | 30 x 34 x 34 | 13 | 45 | 6/10 | R/C | 10 fast |

## Appendix B: Printers

Source: ND-13.028.1 NO page 60. Signal: R = RS-232-C, O = RS-422, C = current loop,
P = parallel.

| ND number | Product | H x W x D (cm) | Weight (kg) | Power (W) | Signal | Fuse (A) |
|---|---|---|---|---|---|---|
| 102180 | Colour plotter | 13 x 57 x 37 | 7 | 35 | R | 10 fast |
| 102380 | Olivetti DY250 | 14 x 55 x 33 | 14 | 50 | R | 10 fast |
| 104480 | Philips GP 300 L | 19 x 62 x 50 | 23 | 180 | R | 10 fast |
| 104520 | Fujitsu M3023 D | 110 x 108 x 68 | 330 | 1300 | P | 25 slow |
| 104750 | Genicom 3024 | 13 x 63 x 30 | 15 | 83 | R | 10 fast |
| 104760 | ELPHO 20 | 117 x 89 x 55 | 150 | 320 | R/P | 16 fast |
| 110020 | Canon LBP-8 | 29 x 48 x 42 | 32 | 850 | R | 16 fast |
| 110021 | Tally MT 660 | 98 x 85 x 57 | 158 | 1200 | R | 16 fast |
| 110079 | Inkjet PT88S | 14 x 41 x 31 | 7.5 | 30 | R | 10 fast |
| 110080 | Inkjet PT88S | 14 x 41 x 31 | 7.5 | 30 | O | 10 fast |
| 110090 | Epson LX-86 | 8 x 42 x 31 | 5 | 60 | R | 10 fast |

## Appendix C: Power distribution units

Source: ND-13.028.1 NO page 61. "STROMFORDELER/PDU" = power distributor.

| ND number | Product | H x W x D (cm) | Weight (kg) | Heat (W) | Fuse |
|---|---|---|---|---|---|
| 108720 | PDU 10 kVA | 97 x 63 x 58 | 200 | 200 | 25 A high-efficiency |
| 108740 | PDU 20 kVA | 97 x 63 x 58 | 235 | 400 | 50 A high-efficiency |
| 108760 | PDU 40 kVA | 115 x 65 x 86 | 330 | 800 | 100 A high-efficiency |
| 108780 | PDU 60 kVA | 190 x 102 x 62 | 485 | 1300 | 250 A high-efficiency |

---

## 9. The NORD machines: NORD-1, NORD-10 and NORD-50

Added 2026-09-13. These pre-date every table above, which starts at the ND-100.

### 9.1 NORD-10/S and NORD-50 cabinet, measured

Both machines use the same cabinet and the Operator's Guide states the figures twice,
once per machine, identically.

| Item | Value |
|---|---|
| Height | 160 cm |
| Width | 59.5 cm |
| Depth | 60.5 cm |
| Volume | 0.576 m3 |
| Weight | 100 kg |
| Mains | 220 V AC, 50 Hz +/- 2 Hz, 2.7 A |
| Cooling | forced |
| Ambient | 0 to 55 degrees C, 10 to 90 percent humidity, non-condensing |

The 2.7 A figure applies to a NORD-10 CPU with memory management, cache, large disk
interface, bus receiver, bus brancher and 128 Kbytes of MOS memory. The NORD-50 cabinet
is rated at 1000 W.

Source: `../Reference-Manuals/10/ND-30001-01A-EN-Nord 10 Operators Guide.md`,
sections 1.2.5 and 4.2.4.

Note how close this is to the later ND-100 6-module cabinet at 96 x 54 x 92 cm and to
the 11-module cabinet at 169 x 60 x 91 cm. The NORD-10 is the same width class and
roughly the height of the later large cabinet, but **30 cm shallower**.

### 9.2 NORD-10/S cage stack, measured by hole number

Figure 1.7 of the same manual, "NORD-10/S layout, front view, max. configuration", is a
dimensioned front elevation that locates each unit by frame hole number, exactly as the
later 11-module cabinet does. Top to bottom:

| Holes | Unit |
|---|---|
| 3-7 | Power panel 2 |
| 17-23 | Operator panel |
| 31-38 | CPU rack A |
| 41-43 | Fan assembly |
| 46-53 | Channel expander rack B |
| 58-65 | Channel expander rack C |
| 68-70 | Fan assembly |
| 89-95 | Power panel 1 |

So the NORD-10 hole grid runs to at least 95, against 66 on the 1985 cabinet.

Figure 1.6, "Cabinet overview", is a pair of section views with 25 numbered items. The
list, read off the scan: top fan right; top fan left; power supply unit no 1; operator's
panel; crate A, the CPU crate; fan for crate A; formatter for floppy disk; floppy
driver 1; floppy driver 2; crate B, an I/O crate; crate C, an I/O crate; fan for crates
B and C; power panel if 115 V AC; power supply unit no 1; terminal no 1; M1 crate, the
multiport memory; terminal no 2; fans for the M1 crate; cross rail no 3; terminal no 3;
frame for plug panel with sub-panels; cabinet front side; cabinet back side; power panel
if 230 V AC.

Figure 1.8 shows the mains distribution bar running down the right side from power
panel 1 at the bottom to power panel 2 at the top. Figure 1.9 shows the 5 V and 24 V
distribution from three supplies A, B and C to the CPU and two channel expanders, all in
4 mm square wire, with 0.4 mm square twisted pair for +24 V to the TTY interface.

### 9.3 NORD-1 cage heights, measured in inches

**No overall cabinet size has been found for the NORD-1.** What exists is better in one
way: a dimensioned side section, ND drawing **2B28 "NORD-1 LAY OUT"**, dated March 1972,
printed as page 4-2 of ND-01.005.01. It gives module heights in inches down two columns.

Front column, top to bottom, as the dimension chain reads:

| Value | Unit the dimension sits beside |
|---|---|
| 5 1/2 in | Power panel 2 |
| 4 3/4 in | gap |
| 4 3/4 in | Operator panel |
| 3/4 in | gap |
| 7 in | CPU crate |
| 7 in | CPU crate |
| 7 in | I/O crate |
| 7 in | I/O crate |
| 6 3/4 in | Plug panel |
| 5 1/4 in | Power panel 1 |

Rear column, top to bottom: power supply 7 in, power supply 7 in, a 3 in gap, memory
13 in on slide rails, then the fan box at the bottom with a cable trench beside it.

So a **NORD-1 CPU or I/O cage is 7 inches high, about 178 mm**, and the machine is two
CPU crates plus two I/O crates, which matches ndwiki's "two racks with 64 cards".

The chain adds to about 55 3/4 inches, roughly 142 cm, for the front column. That is the
stack, not the cabinet, so do not quote it as a cabinet height.

**Caution on the top two dimensions.** The 5 1/2 and the first 4 3/4 sit close together
on the scan and it is not certain which belongs to the panel and which to the gap below
it. The 7 inch crate heights are unambiguous.

Source: the sintran.com mirror, external collection from heim.bitraf.no, file
`ND-01.005.01_NORD-1_Connectors_..._September_1972_ocr.pdf`, PDF page 31. The repo's OCR
of that manual, `../Reference-Manuals/1/ND-01.005.01_NORD-1_...md`, kept the heading
"NORD-1 LAYOUT / Dimensions" but lost the drawing, which is why these figures were not
already here.

---

**Last updated**: 2026-09-13
