# ND-10191E00 — FORTRAN for ND-100/NORD-10, version E (rev 00)

> Status: IN-PROGRESS — real floppy set decoded, complete matched 3-part set found (resolves the A/D gap question)

| Field | Value |
|-------|-------|
| Part number | `10191E00` |
| Base product | [`ND-10191`](../README.md) |
| Release date | 1985-03 (PART2/PART3) / 1985-05 (PART1) |
| CPU target | ND-100 / NORD-10 |

## Why this version matters

This is a **complete, matched 3-part set** — unlike the `D` revision already documented (PART2/
PART3 only, no PART1 found). Its existence resolves the open question on
[ND-10191's product page](../README.md#the-3-part-floppy-set-and-why-versions-mix-letters): the
compiler (PART1) **was** revised past `A` — `FORTRAN-100-E00:PROG` exists as a real, distinct
compiler binary — so the D-revision's missing PART1 is very likely just an unfound floppy, not
evidence the compiler was frozen. `E00`'s runtime file naming (`FORT48-1BANK-E0`/
`FORT32-1BANK-E0`) already matches D's post-rename convention, confirming the rename happened at
or before E, not at D specifically.

## Distribution media

Four floppies, downloaded via NDwiki (imaged by Torfinn "Tingo" Ingolfsen):

| Floppy volume | Contents |
|---|---|
| `10191E00-1S` | `FORTRAN-100-E00:PROG` (608256 bytes) — the compiler |
| `10191E00-2S` | `FORT48-1BANK-E0:BRF`, `FORT48-2BANK-E0:BRF` — 48-bit floating runtime, both bank splits |
| `10191E00-3S` | `FORT32-1BANK-E0:BRF`, `FORT32-2BANK-E0:BRF` — 32-bit floating runtime, both bank splits |
| `10191E00-1D` | The same 5 files bundled onto a single double-density disk (compiler + all 4 runtime BRFs) |

See [TWO-BANK-PROGRAMS.md](../../../../Developer/Workflow/TWO-BANK-PROGRAMS.md) for the 1-bank/
2-bank distinction.

## Documentation
- No PD sheet, no PI sheet specific to this revision — see [ND-10191's page](../README.md) for
  the shared PI sheet covering the whole product.

## Provenance & open items
- Source: four real floppy images, downloaded via NDwiki and decoded in this session
  (`ndfs -t`).
- **TODO:** no `:MODE`/`:BATC` install script or installer `:PROG` was found — likely a manual
  `NRL`-based install, by analogy to the A/D revisions already documented, not separately
  evidenced here.

---
**Parent:** [../README.md](../README.md) (`ND-10191` product overview)
