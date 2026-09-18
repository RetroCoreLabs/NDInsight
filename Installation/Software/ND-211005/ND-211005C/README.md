# ND-211005C — UNIQUE Text System, version C (rev 04)

> Status: VERIFIED (transcribed from PD sheet; not yet run live)   ·   Install source: [PD]

| Field | Value |
|-------|-------|
| Part number | `211005C04` |
| Base product | [`ND-211005`](../README.md) |
| Version | C, revision 04 |
| Release date | 88.02.05 |
| CPU target | ND-100 / ND-500 |
| OS requirement | SIN VS/VSX > I (ND-100), SIN VSX/500 > I (ND-500) |

## Description
Per-language text/message base plus example UNIQUE-II applications (a customer register, several
"ZOOM" drill-down examples, a sales example) and the example SIBAS-II database schema
(`DIA-DRL-F-<lang>`) those examples run against.

## Prerequisites
- **Mass storage (permanent):** `SYSTEM` 121 pages / 2 files; `DIALOG-SYS` 100 pages / 5 files;
  `ND-OPERATIONS` 1 page / 1 file. [PD]

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `211005C04-<lang>-01D` (double density) + 3 single-density disks per language | `TEXT-SYS-IN:PROG` (installer) · `DDBTABLES-E07:VTM` (terminal tables — see [VTM chapter](../../../../Developer/Workflow/VTM-TERMINAL-INTERFACES.md)) · `UNIQUE-<lang>-C04:UTXT`/`XTRA-<lang>-C00:UTXT`/`QUICK-<lang>-C03:UTXT` (message text bases) · `UNIQUE-<lang>-C00:HELP` (help text) · `UE-ERMSG-<lang>-C:ERR` (error messages) · `SW-CONFIG-<lang>:SYMB` (system-dependent config) · `DIALOGUE-DDC:SYMB` (example data dictionary) · `DIA-DRL-F/R-<lang>:SYMB` (example SIBAS-II schema) · ~20 `:UNIQ` example applications (customer register, sales, zoom drill-downs, department lists — English and Norwegian variants) each paired with an empty `:UCOM` file of the same name |

Confirmed languages/media: English (`-EN-`) and Norwegian (`-NO-`) fully available; Swedish
(`-SW-`) and German (`-GE-`) listed but "not yet available" per this PD sheet's own text.

## Installation procedure

Source: PD sheet §2 "Installation Procedure", verbatim. [PD]

```
@ENTER-DIRECTORY 211005C04-<lang>-01,FLOPPY-DISC-<n>,0
@(211005C:FLOPPY-USER)TEXT-SYS-IN
```
The installer copies all floppy files to `DIALOG-SYS`, `ND-OPERATIONS`, and `SYSTEM`, creating or
expanding those user areas as needed; if using single-density diskettes it prompts for each
subsequent disk. To install the bundled example applications, run the UNIQUE or XTRA installation
program and choose **INSTALL EXAMPLES** (not part of this product's own installer).

## Configuration / post-install
All system-dependent parameters live in `(ND-OPERATIONS)SW-CONFIG:SYMB` — the older
`UNIQUE-DEF-A:DEF`/`:UTXT`/`UNIQ-DEFCOMP:PROG` files this used to require are no longer needed as
of this revision. Language selection is read from `USER ENVIRONMENT` if active; otherwise decided
at load time.

**Troubleshooting** — `'Can not open message file (DIALOG-SYS)UNIQUE-<lang>-C:UTXT'` means either
missing read+common (`RC`) access on that file, the file doesn't exist, or the running UNIQUE
product needs a newer Text System version than what's installed. [PD]

## Documentation
- PD-sheet: [../../../Installation-Description/ND-211005-3-EN.md](../../../Installation-Description/ND-211005-3-EN.md)
- Manual(s): `ND-60.206.3`, `ND-60.210.3`, `ND-60.281.1` (none located in this repo)

## Provenance & open items
- Source: single, complete OCR'd PD-sheet scan.
- **TODO:** this install has not been run live in the emulator.

---
**Parent:** [../README.md](../README.md) (`ND-211005` product overview)
