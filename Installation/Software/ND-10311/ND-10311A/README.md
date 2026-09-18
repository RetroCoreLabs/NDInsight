# ND-10311A — Assembler for ND-500, version A

> Status: IN-PROGRESS — install command sourced from the manual, floppy contents confirmed, not run live   ·   Install source: [manual] + [OBS]

| Field | Value |
|-------|-------|
| Part number | `10311A` |
| Base product | [`ND-10311`](../README.md) |
| Version | A |
| Release date | file dated 1981-10-22 |
| CPU target | ND-500 |
| OS requirement | unknown |

## Description
Single-file floppy: the assembler itself, shipped as a raw `:BPUN`, no runtime banks, no
include/header files, no install script.

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `ND-10311A` | `ASSEMBLER-500:BPUN` (20 pages), user `FLOPPY-USER` |

Confirmed by downloading the image (MD5 `ec1a89cbd51ada86af596609d9bf40e3`) and reading with
`ndtool -t`.

## Installation procedure

No PD sheet or `:MODE` script exists on this floppy, but the exact install command is already
documented elsewhere in this repo — quoted from *ND-30.003.7 EN SINTRAN III System Supervisor* as
the manual's own worked example for `@DUMP-REENTRANT` with omitted (default) addresses:

```
@DUMP-REENTRANT ASSEMBLER,,(BPUN-FILES)ASSEMBLER-500:BPUN
```

See [../../../OS/SINTRAN-BOOT-AND-MODE-FILES-GUIDE.md §12](../../../OS/SINTRAN-BOOT-AND-MODE-FILES-GUIDE.md#12-making-subsystems-reentrant--dump-reentrant-manual-3x--pd-sheets)
— "Empty addresses (`,,`) use the file's own defaults — this is what the manual shows for
ASSEMBLER-500." This is the one FORTRAN/PLANC/Assembler-family product in this catalog whose
reentrant-dump command is **manual-sourced**, not inferred by pattern.

Before this command works, copy the floppy's file to `(BPUN-FILES)`:
```
@ENTER-DIRECTORY ND-10311A,FLOPPY-DISC-1,0,
@COPY-FILE "ASSEMBLER-500:BPUN",(BPUN-FILES)ASSEMBLER-500:BPUN
```

## Configuration / post-install
None known beyond the reentrant dump.

## Documentation
- PD-sheet: not located
- PI-sheet: [../../../Product-Info/ND-10311-A1-EN.md](../../../Product-Info/ND-10311-A1-EN.md)
- Manual(s): `ND-60.113` NORD-500 Assembler Reference Manual — [../../../Reference-Manuals/ND-60.113.02 EN Assembler Reference Manual.md](../../../../Reference-Manuals/ND-60.113.02%20EN%20Assembler%20Reference%20Manual.md)

## Provenance & open items
- Source: floppy directory listing via `ndtool`; install command from the System Supervisor
  manual (already transcribed elsewhere in this repo, not re-verified here).
- **TODO:** confirm the copy-to-`(BPUN-FILES)` step's exact syntax and destination user against a
  real PD sheet if one turns up — inferred from the generic pattern in
  [../../INSTALL-METHODOLOGY.md](../../INSTALL-METHODOLOGY.md), not stated for this product
  specifically.
- **TODO:** this install has not been run live in the emulator.

---
**Parent:** [../README.md](../README.md) (`ND-10311` product overview)
