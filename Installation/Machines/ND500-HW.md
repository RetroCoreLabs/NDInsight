# ND-500 hardware: cabinets and boards

What box each ND-500 model came in, how big the box is, and which printed circuit
boards (PCBs) were inside. Only what the manuals in this repo say. Where the repo
holds nothing, that is stated.

**Built from:** the ND-500 course manual NEC-01 and its 1982 card assembly sheets, the
Multiport 4 manual ND-10.003, the Multiport 5 manual ND-10.004, the ND-500 and ND-500/CX
product sheets in `../Product-Info/`, the sales document ND-SID001, and the dimension
tables in `../../Hardware/ND-PHYSICAL-MODELS.md`. Full list in section 4.

Sibling document: [ND5000-HW.md](ND5000-HW.md).
What the metal actually looks like, cage by cage, with image briefs:
[cabinets/](cabinets/README.md).

---

## 1. The one cabinet

Every ND-500 system, from the ND-520 of 1981 to the ND-570/CX, ships in the same
floor-standing cabinet. ND calls it the "11 module cabinet" (11 x 5 1/4 inch bays in
front) or the "ND-100/500 cabinet". The ND-5000 later reuses the same shell.

| Measure | Value | Source |
|---|---|---|
| Height x width x depth | 1.69 x 0.60 x 0.91 m | ND-520, ND-540, ND-505/CX product sheets; ND-500 course, page 11 (1690 x 600 x 910 mm) |
| Depth, later sheets | 0.95 m | ND-500/CX Model 21 and 22 sheets; planning manual 1987 |
| 1984 site table | 172 x 60 x 92 cm, empty 80 kg | `Hardware/ND-PHYSICAL-MODELS.md` section 7 |
| Gross weight, one cabinet | 180-250 kg | product sheets |
| Power, one cabinet | 3500 W max, 230 V 50 Hz, 25 A slow fuse | product sheets, planning manual |
| Two-cabinet ND-560 | ND-500 cabinet ca. 150 kg / 2500 W, ND-100 cabinet ca. 200 kg / 1600 W | ND-560 sheet |

The three depth figures (0.91, 0.92, 0.95 m) come from different ND documents and are
not reconciled here. `Hardware/ND-PHYSICAL-MODELS.md` discusses the conflict.

What is inside a NORD-500 system cabinet (ND-500 course, page 7):

- power supply 2 x 150 A at 5 V, plus standby power if the multiport memory is in the
  same cabinet
- AC distribution panel
- one NORD-500 card crate
- one plug panel (reached from the rear)
- room for max 1 MB of NORD-10/S multiport memory in two racks with plug panel

A NORD-500 memory system cabinet holds 1 x 150 A at 5 V, standby supplies, and up to
2 MB of multiport in four racks.

Board size (ND-500 course, page 9): an ND-500 module is **405 x 277 mm**; an ND-100
module is 367 x 277 mm. The two card sizes do not mix in one crate.

---

## 2. One cabinet or two: the configurations

| System | Cabinets | What goes where | Source |
|---|---|---|---|
| ND-520, ND-540 | 1 | ND-500 crate + ND-100 crate in one box. Special MPM4 ND-100 backplane: 15 standard ND-100 positions plus 6 prewired for the most significant part of shared memory; the least significant part (max 1 MB) sits in the ND-500 crate. Shared memory max 2 MB, total 2 1/4 MB. 6 free I/O slots. | ND-520 and ND-540 sheets; MPM4 manual chapter 11 |
| ND-560 | 2 | ND-500 CPU + Multiport IV in one cabinet, ND-100 + I/O in the other. 12 free I/O slots. Memory 3/4 MB standard, 7 1/4 MB in the cabinets, 28 1/4 MB max with expansion. | ND-560 sheet |
| ND-550/1, ND-560/1 | 2 | 1984 site table: 172 x 120 x 92 cm, 550 kg, 4300 W, two mains feeds | site table via `Hardware/ND-PHYSICAL-MODELS.md` |
| ND-500/2: ND-530/550/560/570 "I" | 1 | 300 kg, 2500 W | same 1984 table |
| ND-500/2: ND-530/550/560/570 "II" | 2 | 550 kg, 4300 W | same 1984 table |
| ND-500/2: ND-530/550 "III" | 1 | 350 kg, 3000 W | same 1984 table |
| ND-505/CX | 1 | ND-500/2 CPU, Multiport V, ND-100 front end, I/O. 12 free I/O slots. 2 1/4 MB standard, 8 MB shared max. | ND-505/CX sheet |
| ND-510/CX Model 21 (ND 5171) | 1 | Multiport V, ND-110 front end, 3 MB (8 max), 13 free I/O slots | ND-510/CX sheet |
| ND-500/CX Model 21: 530/550/560/570 (ND 5371/5571/5671/5771) | 1 | Multiport V, ND-110/CX front end (ND-100/CX in the 530), 4-10 MB, 8 MB shared max | ND-500/CX Model 21 sheet |
| ND-500/CX Model 22: 530/550/560/570 (ND 5372/5572/5672/5772) | 2 | Multiport V, ND-110/CX front end, 4-10 MB, 72 MB shared max, expansion rack in the second cabinet adds 18 positions | ND-500/CX Model 22 sheet |
| ND-580/n, ND-590n (2-4 CPUs) | not documented | Only ndwiki names these. No ND document in this repo describes the multiprocessor cabinet. | ndwiki ND-500 |

Expansion products:

| ND number | What | Source |
|---|---|---|
| ND 5001 | Expansion cabinet: an ND-500 cabinet with power supply, holds up to two of 5002/5003 | ND-520/540/560 sheets |
| ND 5002 | Memory expansion, 7 MB: MPM IV rack with 2 banks, ports, controllers, cables | same |
| ND 5003 | I/O expansion, 18 more I/O cards: I/O rack, bus expander cards, cables | same |
| ND 5083 | I/O expansion cabinet, 18 positions | ND-510/CX and Model 21 sheets |
| ND 5084 | Memory and I/O expansion cabinet, 18 positions | same |
| ND 5080 / 5081 | Extra I/O channel, 2.1 MB/s each, up to three channels | Model 22 sheet |
| ND 5085 | Extra I/O DMA channel: an 11-module cabinet, MPM V driver (103880), MPM V 32-bit port (103830), MPM IV bus controller (103900), MPM IV rack with 2 banks (103920) | Sales Information ND-SID001 |

---

## 2b. The crates, and how they link

A crate is a set of PCBs on one shared backplane. An ND-500 system is several crates
cabled together. Everything here is from the MPM4 manual (chapters 4, 8-11), the
course manual and the product sheets.

### The crate types

| Crate / backplane | Positions | Card size | Used for |
|---|---|---|---|
| ND-100 standard | 22 | ND-100 | The ND-100 crate. With MPM 4 modules it can also act as a one-bank multiport memory. |
| MPM4 ND-100 | 15 + 6 | ND-100 | ND-520/540 only: 15 positions are a normal ND-100 bus, 6 prewired positions hold the most significant half of shared memory (or DMA controllers and multiport drivers). |
| ND-500 standard | 27 (positions 1-27 on the assembly sheets) | ND-500 | The ND-500 CPU crate. |
| MPM4-1 BANK | 5 | ND-100 | ND-520/540 only: replaces the first 5 positions of the ND-500 backplane and holds the least significant half of shared memory (max 1 MB). |
| MPM4-2 BANK (ND 392) | 2 x 10 | ND-100 | Memory crate for ND-100 and ND-560 systems. Positions 10 and 13 prewired for the bus controllers, 11-12 hold the bus termination. Two of these fit one 11-module cabinet. |
| MPM4-4 BANK (ND 393) | 4 x 6 | ND-100 | The most compact memory crate, meant for the ND-560. |
| MPM 5 crate | not documented in the repo | | The /CX systems use Multiport Memory V; ND 5085 lists an "MPM IV rack with 2 banks" even for MPM V ports, so the rack is the same. |

### How the crates are linked

| Link | From | To | How |
|---|---|---|---|
| ND-100 to ND-500 control and DMA | PCB 3022 "ND-500 interface" in the ND-100 crate | PCB 5015 "Control II" in the ND-500 crate | Cable. Mailbox registers, DMA into ND-100 memory, and the control-store load path. |
| ND-100 to multiport memory | Bus Master module (BUSM, PCB 3030) in the ND-100 crate | Bus Controller (BUSC, PCB 3021) in every memory bank | Differential "ND-100 master bus". Up to 9 BUSC per BUSM, up to 32 BUSC in a system, several BUSM allowed in one ND-100 bus. The BUSM refreshes the memory behind each BUSC. A bank holding only I/O modules is just an ND-100 bus extension. |
| ND-500 to multiport memory | The CACHE modules in the ND-500 crate (one channel for instructions, one for data) | PORT modules, one in each 16-bit bank | Cables. One 32-bit cache module connects to two 16-bit banks through two ports. ND-520 without cache uses the memory channel on the module directly. |
| Small systems without a separate memory crate | PORT module installed in the ND-100 CPU bus | | "Common memory in smaller configurations." |
| DMA devices (disk, tape) | Their controller in a BUSC bank or via a PORT | shared memory | Same channels; no CPU in the path. |
| MPM 5 (/CX systems) | Multiport driver from the ND-100 (ND 103880) and a 32-bit port (103830) | MPM V rack | From the ND 5085 structure list; the MPM 5 controller module carries its own maintenance processor and console. |

Which crates sit in which cabinet:

| System | Cabinet 1 | Cabinet 2 |
|---|---|---|
| ND-520, ND-540 | ND-500 crate (with MPM4-1 BANK at its front) + MPM4 ND-100 crate | none |
| ND-560 | ND-500 crate + MPM4 2-bank or 4-bank crate(s) | ND-100 crate + I/O |
| ND-500/CX Model 21, ND-505/CX, ND-510/CX | ND-500 crate + MPM V + ND-100/110 crate | none |
| ND-500/CX Model 22 | ND-500 crate + MPM V | ND-110/CX crate + I/O, room for an 18-position expansion rack |
| Expansion (ND 5001/5002/5003, 5083/5084) | | extra MPM IV 2-bank rack and/or an 18-slot I/O rack, linked by bus expander cards |

---

## 3. The boards

### 3.1 ND-500/1 CPU crate (ND-520, 540, 560)

From the card assembly sheets in the ND-500 course manual (dated 21 Dec 1982),
configuration "ND-500/1/4-CACHE". Position numbers are crate slots.

| Pos | Board | PCB | Note |
|---|---|---|---|
| 4 | Cache instruction 0 | 5006 | one per 16 KB |
| 5 | Cache control instruction | 5017 | |
| 9 | Cache data 0 | 5006 | |
| 10 | Cache control data | 5017 | |
| 11 | Memory management instruction | 5022 | |
| 12 | Memory management data | 5022 | |
| 13 | Control II | 5015 | the ND-100 to ND-500 communication card, pairs with 3022 on the ND-100 side |
| 14 | Prefetch | 5018 | |
| 15 | Control I | 5012 | |
| 16 | Trap | 5019 | one OCR reads 5010 |
| 17 | Control store | 5401 | 8K writable, 144-bit microword |
| 18 | Sequencer | 5004 | |
| 19-22 | CPU slice x 4 | 5001 | |
| 23-26 | Arithmetic 1-4 | 5008, 5009, 5011, 5014 | floating point and multiply/divide hardware |
| 27 | Spare | | |

That is 20 boards with quarter cache. The "1/2-CACHE" sheet adds a second cache
instruction and a second cache data board (5006), giving 22. ndwiki's "24 cards" for
the full ND-500 CPU is in the same range, but no sheet in the repo shows a 24-board
configuration exactly.

Cache per model (MPM4 manual, chapters 10 and 11): ND-520 none; ND-540 one 16 KB
instruction and one 16 KB data module; ND-560 one, two or four modules per side.
The ND-500 CPU datasheet (ND-060) gives the total cache as 32, 64 or 128 KB.

In a single-cabinet ND-520/540 the ND-500 crate also carries the memory cards for the
least significant part of shared memory. The "NDSQ-MINI" card assembly sheet
(course manual, page 139) shows positions 1-4 as: ND-100 bus control 3021, MPM4 port
A data 3022, MPM4 port F instruction 3022, dynamic RAM 1/2 MB 3024. The 3022 print
number on the ports is what the OCR gives; the same sheet series also prints the port
as 3029, so treat the port PCB number as unverified.

### 3.2 ND-500/2 CPU crate (ND-510, 530, 550, 560, 570, 505)

**Not held.** The ND-500/2 board set is in ND-05.011 "ND-500 Hardware Description",
which the documentation catalogue describes ("guided through each of the circuit card
assemblies of the ND-500/2 ... main differences between the ND-500/1 and the ND-500/2")
but which is not in this repo. What the repo does say:

- The ND-500/2 has a prefetch processor and the address translation is done by the
  microprogram (ND-5000 Hardware Description, section 6.2, comparing against it).
- The ND-570 has a floating-point unit on separate cards: the first MF-bus rack of the
  ND-5000 keeps positions 1-5 free with the note "earlier used for ND-570
  floating-point unit cards" (ND-5000 Hardware Maintenance, table 3).
- ND-570 with a 64-bit wide cache needs a special interleave PROM on the MPM 5 twin
  port 5152 (MPM 5 Technical Description, section 1.2).
- Cache: ND-560/CX 16 KB, ND-570/CX 32 KB (Model 22 sheet).

### 3.3 ND-100 side

From the "ND-100-MNT" card assembly sheet in the course manual (21 Dec 1982), an
ND-100 crate feeding an ND-500:

| Pos | Board | PCB |
|---|---|---|
| 1 | ND-100 CPU/CX (ND 100) | 3033 |
| 3 | Memory management with cache (ND 032) | 3012 (OCR) |
| 4 | Megalink (ND 724) | 3023 |
| 5 | **ND-500 interface (ND 065)** | **3022** |
| 6 | Pertec magtape controller (ND 557) | 3006 |
| 7-8 | Large disc controller (ND 550) | 3018, 3019 |
| 9 | Floppy controller (ND 367) | 3027 |
| 10 | 8-terminal interface (ND 272) | 3012 (OCR) |
| 14, 20 | Dynamic RAM (ND 116) | 3024 |
| 15 | ND-100 bus master (ND 205) | 3030 |
| 17 | ND-100 bus control (ND 200) | 3021 |
| 18-19 | MPM4 port A data, port E instruction (ND 291) | 3029 |

The OCR gives 3012 for two different boards; one of them is wrong. PCB 3022 is the
ND-100 to ND-500 interface, confirmed by the course manual chapter 3 and the rest of
this repo.

### 3.4 Memory system

| System | Memory | Port board | Source |
|---|---|---|---|
| ND-520, 540, 560 | Multiport Memory IV (MPM 4): 1/2 MB ECC modules 3024, bus master 3030, bus controller 3021, port modules | MPM4 port | MPM4 manual |
| ND-505/CX, 510/CX, 5x0/CX | Multiport Memory V (MPM 5): twin 16-bit port 5152 or 5155, dynamic RAM, line driver | 5152 / 5155 | product sheets; MPM 5 manual |

---

## 4. Sources

- `../../Reference-Manuals/500/NEC-01 - ND-500 course.md` - cabinets (page 7), module size (page 9), cabinet dimensions (page 11), card assembly sheets (pages 139-157), 3022/5015 registers (chapter 3)
- `../../Reference-Manuals/500/ND-10.003.01 TECHNICAL INTRODUCTION TO MULTIPORT 4.md` - chapters 10 and 11, ND-520/540/560 memory and cabinet
- `../../Reference-Manuals/500/ND-10.004.01-MPM 5 Technical Description.md` - twin port 5152/5155, ND-570 interleave PROM
- `../../Reference-Manuals/500/ND-05.017.01 EN ND-5000 HARDWARE MAINTENANCE.md` - table 3, ND-570 floating-point cards
- `../Product-Info/ND-520-C1-EN.md`, `ND-540-C1-EN.md`, `ND-560-C1-EN.md`, `ND-505CX-A1-EN.md`, `ND-5171-A1-EN.md`, `ND-5371-A1-EN.md`, `ND-5372-B1-EN.md`, `ND-060-C1-EN.md`
- `../Sales-Info/ND-SID001-A1-EN.md` - ND 5085 structure list
- `../../Hardware/ND-PHYSICAL-MODELS.md` - the 1984 site-preparation and 1987 planning tables
- `../../History/sources/ndwiki-nd-500.md` - ndwiki "ND-500", Wayback snapshot 27 Aug 2025 (secondary; source of the ND-580/n naming and the "24 cards" figure)
