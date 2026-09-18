# ND-211224B01 — ND LINKER for ND-500/ND-5000, version B01

> Status: IN-PROGRESS — installer identified by structural analogy to a VERIFIED sibling installer, auto-job files decoded, exact live dialogue NOT captured   ·   Install source: [OBS] (directory listing) + [MODE] (auto-job files) + [INF] (installer flow, by analogy)

| Field | Value |
|-------|-------|
| Part number | `211224B01` |
| Base product | [`ND-211224`](../README.md) |
| Version | B01 |
| Release date | files dated 1989-02-02 |
| CPU target | ND-500 / ND-5000 |
| OS requirement | unknown |

## Description
The ND LINKER program itself (`LINKER-B01:DOM`), its help text, a minimal init file, and nine
per-source-language "auto job" files that the linker invokes automatically on `CLOSE` to set up
runtime trap handling and load the matching runtime library.

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `211224B01-XX-01D` | `IN-LINK-XX-B01:PROG` (67 pages, the installer) / `:XCOM` (14 pages) / `:INIT` (10 pages) — installer program + data · `LINKER-B01:DOM` (354 pages, the linker domain itself) · `LINKER-B01:HELP` (96 pages, online help text) · `LINKER-B01:INIT` (1 page — decoded below) · `LINKER-AUTO:JOB` + 8 per-language variants (`-5ASM`, `-FORT`, `-PLNC`, `-COB`, `-PASC`, `-SIMU`, `-ADA`, `-COR`, `-C`, `-BASC` — decoded below), user `FLOPPY-USER` |

Confirmed by downloading the image (MD5 `1097cc3b230ef5b97582962d842e361d`) and reading with
`ndtool -t`/`-x`.

## What the installer looks like, by analogy (not yet run)

`IN-LINK-XX-B01:PROG`/`:XCOM`/`:INIT` is the **exact same three-file shape** as the ND-500
Linkage-Loader's already-verified installer (`IN-NLL-XX-H02:PROG`/`:XCOM`/`:INIT`, see
[../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §4](../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md)) —
unlike the FORTRAN K02 installer, which uses `:RSRC` in place of `:XCOM`. Given both are Norsk
Data ND-500 domain installers of the same generation and file shape, the safe starting
expectation is the same 5-module flow already observed live for NLL:

```
@(211224B01-XX-01D:FLOPPY-USER)IN-LINK-XX-B01:PROG
```
then a menu of **Get start information → Delete product files → Check environment and resources
→ Copy product files → Exit**, likely asking for a domain-owning user (NLL defaults to
`DOMAIN-USER`) and expecting that user (plus `UTILITY`, with enough free pages) to already exist.
**This is analogy from a structurally similar installer, not a confirmed fact about this
installer** — do not skip the prerequisite user-creation steps NLL needed
([../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §2](../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md))
just because they aren't confirmed here yet, and don't be surprised if the same gotchas apply
(silent domain-copy failure, module-1-must-run-every-session, etc. — see §5 of that document).

## Post-install runtime configuration — the `CLOSE`-time auto-job mechanism (decoded, confirmed)

Unlike NLL, this product's role doesn't end at install — it stays involved every time a program is
linked. `LINKER-B01:INIT` (decoded, `byte & 0x7F`) is a minimal default startup:
```
LIST
SET-ADVANCED-MODE
```

The `LINKER-AUTO*:JOB` files (also decoded) are **optional, user-editable** job files the linker
tries to run automatically during its `CLOSE` command, if the domain being closed has undefined
trap entries and its main-program module was compiled in a recognized language. Per
`LINKER-AUTO:JOB`'s own header comment: the linker first looks for the language-specific file
(e.g. `LINKER-AUTO-FORT:JOB`) under the **current user**, then falls back to user `SYSTEM` (which
must grant public read access); after the language-specific file, it also tries the generic
`LINKER-AUTO:JOB` the same way.

`LINKER-AUTO-FORT:JOB` (FORTRAN) was read in full and shows the concrete shape: it enables 15
named hardware/software trap conditions (`#INVALOP` invalid operation, `#INVALDI` divide-by-zero,
`#FLTOFLW` floating overflow, `#STKOFLW`/`#STKUFLW` stack over/underflow, `#PVIOLAT` protect
violation, and others) via `SET-TRAP-CONDITION OWN,ENAB,<code>,<name>`, then loads the FORTRAN
runtime and exception libraries:
```
SPECIAL-LOAD  (SYSTEM)FORTRAN-LIB  LIBRARY
SPECIAL-LOAD  (SYSTEM)EXCEPT-LIB   LIBRARY
```
This **confirms** `EXCEPT-LIB` — the library referenced by name only (no file) in this catalog's
[ND-210177J02 COBOL install](../../ND-210177/ND-210177J02/README.md) — is a standard, shared
runtime exception-handling library that every language's auto-job loads via `SPECIAL-LOAD`, not
something specific to COBOL. Its source product is `ND-10511` **Exception Handling System** — see
[../../ND-10511/README.md](../../ND-10511/README.md), a bare two-`:NRF`-file floppy
(`EXCEPTION-LIB-A:NRF`/`EXCEPTION-TPS-A:NRF`) decoded from a real image in this catalog.

## Installation procedure

**Not confirmed for the installer itself** (see "by analogy" above). Once installed, the linker's
own per-language auto-job files should be reviewed/edited to match the actual runtime library
users/versions on the target system — the comments inside `LINKER-AUTO-FORT:JOB` explicitly say
so ("The file should, if used, be edited to reflect the wanted environment").

## Configuration / post-install
- Review and, if needed, customize the 9 `LINKER-AUTO-*:JOB` files for the target system's actual
  library locations before relying on automatic `CLOSE`-time linking.
- `LINKER-B01:INIT` is the linker's own startup file (`LIST` + `SET-ADVANCED-MODE`) — copy or
  adapt as needed.

## Documentation
- PD-sheet: not located
- PI-sheet: [../../../Product-Info/ND-211224-A1-EN.md](../../../Product-Info/ND-211224-A1-EN.md)
- Manual(s): `ND-60.289` ND Linker User Guide and Reference Manual — [../../../Reference-Manuals/ND-860289-2-EN ND Linker User Guide and Reference Manual.md](../../../../Reference-Manuals/ND-860289-2-EN%20ND%20Linker%20User%20Guide%20and%20Reference%20Manual.md)

## Provenance & open items
- Source: `ndtool -t`/`-x` on the downloaded image; `LINKER-B01:INIT` and all `LINKER-AUTO*:JOB`
  files decoded with the `byte & 0x7F` technique (clean, grammatical output, no artifacts —
  confirmed correct the same way as the CC-100/COBOL scripts).
- **TODO (blocking):** run `IN-LINK-XX-B01:PROG` live to confirm or refute the NLL-installer
  analogy above.
- **TODO:** read `LINKER-B01:HELP` (96 pages) for the linker's own command reference, and the
  remaining 7 language auto-job files not yet transcribed here (`-5ASM`/ND-500 Assembler,
  `-PLNC`/PLANC, `-COB`/COBOL, `-PASC`/Pascal, `-SIMU`/Simula, `-ADA`/Ada, `-COR`/unknown
  language, `-C`/C, `-BASC`/BASIC).

---
**Parent:** [../README.md](../README.md) (`ND-211224` product overview)
