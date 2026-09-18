# ND-211464A — VTM terminal tables (Type 128/129) DEC VT200, version A (rev 00)

> Status: VERIFIED (transcribed from PD sheet; not yet run live)   ·   Install source: [PD]

| Field | Value |
|-------|-------|
| Part number | `211464A00` |
| Base product | [`ND-211464`](../README.md) |
| Version | A, revision 00 |
| Release date | 88.09.08 |
| CPU target | ND-100 / ND-500 |
| OS requirement | SINTRAN III >= H |

## Description
Terminal type descriptor files for the DEC VT200 in Multinational mode (type 128) and National
mode (type 129), plus the `VTM-COMPOUND` tool to compound/regenerate loadable terminal tables.

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `211464A00-XX-01D` (double density) | `DDB128-0-A00:VTM` (1 page, C/D/E format table for VT200 Multinational) · `DDB128-7S-A00:VTM` (2 pages, G format table for VT200 Multinational) · `DDB129-0-A00:VTM` (1 page, C/D/E/G format table for VT200 National) · `VTM-ALL-TYPES:VTM` (3 pages, descriptors needed when compounding) · `VTM-COMPOUND-E09:PROG` (107 pages) · `VTM-COMPOUND-G04:PROG` (124 pages) |
| `211464A00-XX-01S` + `-02S` (single-density, 2-disk set) | same files split across two disks: disk 1 has everything except `VTM-COMPOUND-G04`, which is alone on disk 2 |

## Installation procedure

Source: PD sheet §2 "Installations Procedure", verbatim. [PD]

**Loading:** copy the files to `SYSTEM` or your logged-in user — no special command sequence
given beyond a plain file copy. [PD]

**Which composite file you get depends on the VTM version already on the target system:**
- Version A: one file per terminal type, `DDBnnn-A:VTM`; standard types live in `DDB999-A:VTM`.
- Version B: one composite file, `DDBARRAYS-B:VTM`.
- Version C onward: one composite file, `DDBTABLES-n:VTM`. Since B and C-onward hold equivalent
  data, you can rename between them: `@RENAME-FILE DDBTABLES-C:VTM DDBARRAYS-B:VTM`.

**If you want the compounded tables loaded together with the application itself** (rather than
relying on the system-wide `DDBTABLES:VTM`), load `VTM-ARRAY-D:NRF` (ND-500) or
`VTM-(128/129)-ARRAY-D:BRF` (ND-100) with the program system — see
[LINKING-GUIDE.md](../../../../Developer/Workflow/LINKING-GUIDE.md).

**Adding this VT200 terminal type to the system's terminal-table file (version B onward):**
```
@VTM-COMPOUND-E09
2    (ADD TERMINAL TYPES)
2    (DDBTABLES-n:VTM)
E    (E-Version)
47   (the new terminal type number)
777  (no more DDB-files to add)
9    (EXIT)
```
(run once per `DDBTABLES-?` file that needs the new type). [PD]

**Version A instead edits `DDB999:VTM` directly:**
```
@VTM-COMPOUND-E09
8    (EDIT THE CONTENT IN DDB999:VTM)
2    (ADD TERMINAL TYPE DESCRIPTIONS)
47   (new terminal type)
777  (no more terminal types)
9    (EXIT)
```

The standard terminal types the `VTM-COMPOUND` programs already ship with (types 2 and 11 are
line-oriented; the rest are the standard ND screen-oriented set) are listed verbatim on the PD
sheet — see [../../../Developer/Workflow/VTM-TERMINAL-INTERFACES.md](../../../../Developer/Workflow/VTM-TERMINAL-INTERFACES.md) §3
for the full list.

## Configuration / post-install
Set each terminal's type with `@QSET-TERMINAL-TYPE (<terminal number>) (<terminal type>)` — see
the [VTM chapter](../../../../Developer/Workflow/VTM-TERMINAL-INTERFACES.md) §2 for the full command
reference (not part of this product's own PD sheet, sourced from the System Supervisor manual).

## Documentation
- PD-sheet: [../../../Installation-Description/ND-211464-1-EN.md](../../../Installation-Description/ND-211464-1-EN.md)
- Manual(s): `ND-60.151.02` SINTRAN III Utilities Manual

## Provenance & open items
- Source: single, complete 6-page OCR'd PD-sheet scan.
- **TODO:** this install has not been run live in the emulator.

---
**Parent:** [../README.md](../README.md) (`ND-211464` product overview)
