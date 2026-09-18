# ND cabinets: what they look like inside

One file per cabinet. Each file describes the box, the cages inside it, how the cages are
linked, and ends with ready-to-paste **image briefs** for making educational cutaway
diagrams.

**Cutaway drawings** of every cabinet below are in [diagrams/](diagrams/README.md).

These are companions to [../ND500-HW.md](../ND500-HW.md) and
[../ND5000-HW.md](../ND5000-HW.md), which say which model got which cabinet and which
boards. These files say what the metal looks like.

| File | Cabinet | Main source |
|---|---|---|
| [LARGE-11-MODULE-SHELL.md](LARGE-11-MODULE-SHELL.md) | The shared large shell: frame, hole grid, panels, rear plug frame | Book 2 chapters 10 and 3 |
| [ND-500-ONE-CABINET.md](ND-500-ONE-CABINET.md) | ND-500 single cabinet, model 11 (ND-520, 540, 505/CX, 510/CX, Model 21) | Book 2 chapter 12 |
| [ND-500-TWO-CABINET.md](ND-500-TWO-CABINET.md) | ND-500 two cabinet, model 12 (ND-560, Model 22) | Book 2 chapters 14 and 15 |
| [ND-5000-LARGE.md](ND-5000-LARGE.md) | ND-5000 large cabinet (ND-5200 to ND-5900, ES Model L) | Book 2 chapters 16 and 17 |
| [ND-5000-COMPACT.md](ND-5000-COMPACT.md) | ND-5000 Compact, the COMSON box | Book 2 chapter 8 |
| [ND-5000-ES-MODEL-C.md](ND-5000-ES-MODEL-C.md) | ND-5000 ES Model C, same shell, new inside | ND-830102 maintenance manual |
| [ND-5000-SATELLITE-TECHNOSTATION.md](ND-5000-SATELLITE-TECHNOSTATION.md) | ND-5000 Satellite and Technostation, the narrow deep tower on castors | Book 2 chapter 20 |

---

## Where the drawings are

Norsk Data's production drawing set is bound as **Book 1** (cables), **Book 2** (CPU
cabinets), **Book 4A** (units and panels) and **Book 4B** (drives). Book 2 chapters are
numbered by machine. Scans of the whole set are in the sintran.com mirror, which is kept
outside this repository, under `library/libhw/`.

A Book 2 sheet is A3 landscape, drawn on ND's own "ND-T3000 CAD SYSTEM". The parts list
sits in the top right corner and the title block in the bottom right. Every sheet is an
exploded isometric. Yellow card dividers separate the sub-chapters and carry the drawing
index and revision date.

**These drawings almost never give a millimetre size.** Everything inside a large cabinet
is located by **nutclip hole number** instead. Sizes in these files therefore come from
the product sheets and the site-planning manuals, and each one says where it came from.

### Book 2 in full, so you can find the right scan

Dated November 1988 unless noted. A tick in "read" means it was read sheet by sheet for
these files.

| Chapter | Scan file | Pages | Covers | Read |
|---|---|---|---|---|
| B2 | `ND-B2.pdf` | 4 | Book 2 front matter, CPU cabinets | |
| B2C1 | `ND-B2C1.pdf` | 12 | revision sheet | |
| B2C2 | `ND-B2C2.pdf` | 2 | general information and distribution list | |
| B2C3 | `ND-B2C3.pdf` | 21 | **mounting of panels**: ND-100 Compact, Comson, the 11-module front panel, Satellite and Technostation | yes |
| B2C4 | `ND-B2C4.pdf` | 20 | ND-100 Satellite, assembly drawings (Oct 1988) | |
| B2C5 | `ND-B2C5.pdf` | 12 | ND-100 Satellite, cable info and wiring | |
| B2C6 | `ND-B2C6.pdf` | 24 | ND-100 Compact, assembly drawings | |
| B2C7 | `ND-B2C7.pdf` | 12 | ND-100 Compact, cable info and wiring | |
| B2C8 | `ND-B2C8.pdf` | 38 | **ND-100/5000 Compact (COMSON)**, assembly (Mar 1988) | yes |
| B2C8-1987 | `ND-B2C8-1987.pdf` | 40 | the same set, Dec 1987 edition | yes |
| B2C9 | `ND-B2C9.pdf` | 17 | Clou II, assembly drawings | |
| B2C10 | `ND-B2C10.pdf` | 47 | **ND-100 11-module cabinet '85 and expansion**, assembly | yes |
| B2C11 | `ND-B2C11.pdf` | 25 | the same, cable info and wiring | |
| B2C12 | `ND-B2C12.pdf` | 29 | **ND-500 11-module, ONE CAB**, assembly | yes |
| B2C13 | `ND-B2C13.pdf` | 1 | empty | |
| B2C14 | `ND-B2C14.pdf` | 17 | **ND-500 11-module, TWO CAB**, assembly | yes |
| B2C15 | `ND-B2C15.pdf` | 20 | the same, cable info and wiring | yes |
| B2C16 | `ND-B2C16.pdf` | 40 | **ND-5000 (MAXSON) 11-module**, main assembly. Sub-chapters 2 and 3 missing from the scan | yes |
| B2C17 | `ND-B2C17.pdf` | 11 | the same, cable info and wiring | yes |
| B2C18 | `ND-B2C18.pdf` | 48 | ND-Butterfly, assembly and cable info (Mar 1988) | |
| B2C18-1987 | `ND-B2C18-1987.pdf` | 20 | the same, Dec 1987, index and sub-chapter 1 missing | |
| B2C19 | `ND-B2C19.pdf` | 16 | ND-110 PCT, assembly drawings | |
| B2C20 | `ND-B2C20.pdf` | 24 | **ND-5000 Satellite and Technostation**, assembly | yes |

### The other books, when a Book 2 sheet points out of itself

| Book | Scan file | Covers |
|---|---|---|
| 1A chapter 5 | `ND-B1AC5.pdf` | cabinets and internal cables, overview |
| 1A chapter 6 | `ND-B1AC6.pdf` | internal power cable documentation, 146 pages |
| 1A chapter 7 | `ND-B1AC7.pdf` | internal ground cable documentation |
| 1B and 1C chapter 9 | `ND-B1BC9*.pdf`, `ND-B1CC9.pdf` | internal signal cables, by number range. This is where a cable drawing named on a Book 2 sheet actually lives |
| 4A | listed per chapter | card crates, fan units, operator panels, plug panels, power distribution, ground assemblies |
| 4B | listed per chapter | drive rack assembly, floppy and streamer boxes, disk units |

A Book 2 parts list cites these as "Bk4A Ch11 Sub6" and the like, meaning book, chapter
and sub-chapter.

### Manuals used alongside the drawings

| Manual | In this repo as |
|---|---|
| ND-05.020, ND-5000 Hardware Description | `../../Reference-Manuals/500/ND-05.020.01 EN ND-5000 Hardware Description.md` |
| ND-05.017, ND-5000 Hardware Maintenance | `../../Reference-Manuals/500/ND-05.017.01 EN ND-5000 HARDWARE MAINTENANCE.md` |
| ND-830102, ND-5000 ES Model C Hardware Maintenance | `../../Reference-Manuals/500/ND-830102.1B EN ND-5000 ES Model C Hardware Maint. Manual-Sintran.md` |
| ND-10.003, Technical Introduction to Multiport 4 | `../../Reference-Manuals/500/ND-10.003.01 TECHNICAL INTRODUCTION TO MULTIPORT 4.md` |
| ND-10.004, Multiport Memory 5 Technical Description | `../../Reference-Manuals/500/ND-10.004.01-MPM 5 Technical Description.md` |
| NEC-01, ND-500 course, with the 1982 card assembly sheets | `../../Reference-Manuals/500/NEC-01 - ND-500 course.md` |
| ND-13.028, site planning, for the dimension tables | not in the repo; read through `../../Hardware/ND-PHYSICAL-MODELS.md` |
| ND-830103, ND-5000 ES Model S Hardware Maintenance | **not held.** The gap behind the missing Satellite dimensions |
| ND-05.011, ND-500 Hardware Description | **not held.** The gap behind the missing ND-500/2 board set |

The three OCR'd manuals above **lost every figure** during OCR. For any picture, open the
scan in the mirror, not the markdown.

---

## Reading conventions used in every file

- **Hole numbers.** Each frame post carries a column of paired mounting holes, numbered
  **1 at the top to 66 at the bottom**, on the front frame and the rear frame alike.
  A nutclip is pressed into the holes a given build needs. A smaller hole number is
  higher up. On a 169 cm frame one hole pitch works out at about 25.6 mm, but the
  drawings do not state that, so treat it as derived.
- **Front** is the side the cards plug into and the operator panel faces. **Rear** is the
  side with the connector panels and, on the ND-5000, the power supplies.
- **Cage** and **crate** mean the same thing: a set of boards on one shared backplane.
  ND writes "card crate" or "card frame".
- Anything worked out from a picture rather than read off it is marked **GUESS**.

---

## Card sizes

The only place the two card sizes are written down is the ND-500 course manual, page 9:

| Card | Size |
|---|---|
| ND-500 module | 405 x 277 mm |
| ND-100 module | 367 x 277 mm |

The two do not mix in one crate, which is why every coprocessor machine has at least two
crates. A crate power rail measures about 428 mm end to end (ND-5000 drawing 20524), so
the crates are 19 inch class.

---

## Colour and finish

The assembly drawings are line art and state no colour anywhere. What is documented:

- ND's own sales structure list (ND-SID001) calls the ND-5000 large cabinet a
  **"brown/beige cabinet"**, item 110172 and 110712.
- The ND-100 brochure photograph, read in `../../Hardware/ND-PHYSICAL-MODELS.md`
  section 8.2, shows a **light warm grey or off-white frame and plinth**, **very dark
  brown-black module fronts**, and **signal red** used as an accent on terminals,
  printers and disk drives.

So: warm beige and off-white steel, dark brown-black plastic fronts and bezels, red only
as a small accent. Anything beyond that is invention.

---

## House style for the diagrams

Paste this block ahead of any of the image briefs in these files.

```
Educational cutaway technical illustration of a 1980s Norsk Data minicomputer cabinet.
Clean airbrushed technical-manual style, as in a period service manual: flat even
lighting, no dramatic shadows, no lens effects, slight isometric or straight-on
orthographic view, white background.
Palette: warm beige and off-white painted steel, dark brown-black plastic bezels and
front panels, olive-green circuit boards, cream plastic card ejectors, bare aluminium
chassis, small red accents only on indicator lamps.
Every named part carries a thin black leader line out to a small label in a plain
sans-serif face. Labels sit outside the machine, never on top of it.
No text anywhere except the labels named below. No logos other than "ND Norsk Data"
where the brief says so. No people. Do not invent parts that are not listed.
```

---

*Parent: [../README.md](../README.md)*
