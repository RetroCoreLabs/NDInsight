# ND-210455G04 — VTM terminal tables (Standard), version G (rev 04)

> Status: IN-PROGRESS — floppy contents confirmed, install command NOT extracted (installer is a compiled :PROG)   ·   Install source: [OBS]

| Field | Value |
|-------|-------|
| Part number | `210455G04` |
| Base product | [`ND-210455`](../README.md) |
| Version | G, revision 04 |
| Release date | files dated 1986-05 through 1988-01 |
| CPU target | ND-100 / ND-500 |
| OS requirement | unknown |

## Description
The full standard terminal-table set: dozens of individual `DDBnnn` descriptors (terminal types
2, 3, 11, 36, 52, 53, 57, 79, 80, 83, 90-93, 99, 100, 103, 105, 106, 110, 113 confirmed present,
each in several format variants), the compounded `DDBTABLES-<rev>:VTM` files for four revisions
(C09, D09, E09, G04) simultaneously, both `VTM-COMPOUND` tool versions (`E09` and `G04`), and
pre-built loadable arrays for every target: `VTM-1B-ARRAY`/`VTM-2B-ARRAY:BRF` (ND-100 1-bank/
2-bank) and `VTM-ARRAYS:NRF` (ND-500), confirming exactly the three-target list
[ND-211464's install doc](../../ND-211464/ND-211464A/README.md) already documented from its own
PD sheet.

**A second installer not seen on any other VTM product in this catalog:** `INSTALL-TABLES:PROG`
(26 pages) — its purpose is inferred from its name only (install the standard `DDBTABLES` set),
not confirmed against any install text.

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `210455G04-XX-01D` | `INSTALL-TABLES:PROG` (26 pages) · `VTM-COMPOUND-G04:PROG` (124 pages), `VTM-COMPOUND-E09:PROG` (107 pages) · `DDBTABLES-E09:VTM`/`-C09:VTM`/`-D09:VTM`/`-G04:VTM` (compounded tables, 4 revisions) · `VTM-ALL-TYPES:VTM` (2 pages) · `VTM-1B-ARRAY-G04:BRF`/`-E09:BRF`, `VTM-2B-ARRAY-G04:BRF`/`-E09:BRF` (ND-100 loadable arrays) · `VTM-ARRAYS-G04:NRF`/`-E09:NRF` (ND-500 loadable arrays) · ~60 individual `DDBnnn-<suffix>:VTM` per-terminal-type descriptor files, user `FLOPPY-USER` |

Confirmed by downloading the image (MD5 `51b54d36e3f11bb834fa213ef3a54a9c`) and reading with
`ndtool -t`. Sibling revisions `210455G02-XX-01D`, `210455G03-XX-01D`, `210455G06-XX-01D` exist
in the floppy library but were not mounted for this entry.

## Installation procedure — NOT established

Neither `INSTALL-TABLES:PROG` nor `VTM-COMPOUND-*:PROG` are `:MODE` text scripts — they're
compiled programs, so their dialogue cannot be extracted the way `:MODE` files elsewhere in this
catalog were decoded. By analogy with [ND-211464's real, PD-sheet-sourced procedure](../../ND-211464/ND-211464A/README.md),
expect: copy the relevant files to `SYSTEM`/your working user, then use `VTM-COMPOUND` to add/
regenerate compounded terminal tables and loadable arrays — **not confirmed for this specific
floppy or for `INSTALL-TABLES:PROG`, which has no analog on the `ND-211464` product to compare
against.**

## Configuration / post-install
See [../../../../Developer/Workflow/VTM-TERMINAL-INTERFACES.md §2](../../../../Developer/Workflow/VTM-TERMINAL-INTERFACES.md)
for setting a terminal's type once the tables are installed (`QSET-TERMINAL-TYPE`).

## Documentation
- PD-sheet: not located
- PI-sheet: not located

## Provenance & open items
- Source: floppy directory listing via `ndtool` on the downloaded image.
- **TODO (blocking):** determine what `INSTALL-TABLES:PROG` actually does — run it live, or find
  a PD sheet.
- **TODO:** this install has not been run live in the emulator.

---
**Parent:** [../README.md](../README.md) (`ND-210455` product overview)
