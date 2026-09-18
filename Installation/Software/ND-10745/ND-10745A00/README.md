# ND-10745A00 — ND-Ada, version A (rev 00)

> Status: VERIFIED (real floppy images decoded, including two working `:MODE` scripts)   ·   Install source: [PI] + [MODE]

| Field | Value |
|-------|-------|
| Part number | `10745A00` |
| Base product | [`ND-10745`](../README.md) |
| CPU target | ND-500 |
| OS requirement | SINTRAN III version J or later |

## Distribution media

Two 8" floppies, downloaded from NDwiki (imaged by Torfinn "Tingo" Ingolfsen, uploaded 2024-05-26,
mirrored on https://www.ndwiki.org/wiki/ND-10745A):

| Floppy volume | Contents |
|---|---|
| `10745A00-XX-01D` | `DESCRIPTION-FILE:DESC` (binary domain-metadata, not readable text — same format seen on other Linkage-Loader-domain floppies in this catalog) · `INSTALL-ADA-A00:PROG` / `ADA-INST-DD-A00:PROG` (compiled installer, two-part) · `ADA-COMPILER-A00:PSEG`/`:DSEG`/`:LINK` (the compiler domain) · `ADA-BLD-ENV-A00:MODE` (**real, decoded build script — see below**) · `ADA-SYS:ADA`, `ADA-IOX-SPEC:ADA`, `ADA-TIO-SPEC:ADA`, `ADA-TIO-BODY:ADA`, `ADA-CAL-SPEC:ADA` (Ada source for the environment packages `SYSTEM`, `IO_EXCEPTIONS`, `TEXT_IO`, `CALENDAR`) · `ADA-LILO-A00:PSEG`/`:DSEG`/`:LINK` (empty placeholders — link-and-load-Ada domain, populated at build time) |
| `10745A00-XX-02D` | `ADA-DEMO-A00:ADA` (Tower of Hanoi demo source) · `ADA-DEMO-A00:MODE` (**real, decoded compile/link/run script — see below**) · `ADA-LILO-COPY:PSEG`/`:DSEG`/`:LINK` (the pre-built link-and-load-Ada domain) · `ADA-RUN-TIME-A00:NRF`, `ADA-TIO-A00:NRF`, `ADA-CAL-A00:NRF` (compiled runtime library modules — the PLANC-implemented halves of `TEXT_IO`/`CALENDAR`) |

## Installer

`INSTALL-ADA-A00:PROG` + `ADA-INST-DD-A00:PROG` — a two-part compiled installer (same shape as
other ND-500 product installers in this catalog: a driver `:PROG` plus a data/description
`:PROG`). Its internals were not decoded (compiled binary) — use it interactively if the floppy is
mounted on a live system.

## Building the ADA-ENVIRONMENT library — real, decoded `ADA-BLD-ENV-A00:MODE`

Source: byte-for-byte decode (`byte & 0x7F`) of the real `:MODE` file. [MODE]

```
@CC      BUILD-ENVIRON:MODE
@CC
@CC Mode file to prepare everything which will be available to users
@CC  from the ADA-ENVIRONMENT
@CC
@CC Delete existing library partition (including any NRF files), if any
@DELETE-USER-FILE ADA-ADA--0000:NRF N
@DELETE-FILE ADA-ENVIRONMENT:ALIB
@CREATE-FILE ADA-ENVIRONMENT:ALIB 0
@CC
@CC Create a library for ADA-ENVIRONMENT
@CC
@ND
ADA
LIBRARY
CREATE-LIBRARY ADA-ENVIRONMENT

EXIT
EXIT
EXIT
@CC
@CC Compile package SYSTEM
@CC
@ND
ADA
LIBRARY
OPEN-LIBRARY ADA-ENVIRONMENT

EXIT
COMPILE ADA-SYS:ADA 0
CC package SYSTEM defines implementation-dependent characteristics
CLOSE-LIBRARY
EXIT
EXIT
@CC
@CC  Compile the package specification (nb. CALENDAR has no body)
@CC   nb. if any CALENDAR functions/procedures are written in Ada,
@CC        a body will be necessary
@CC
@ND
ADA
LIBRARY
OPEN-LIBRARY ADA-ENVIRONMENT

EXIT
CC
CC The ADA-COMMON version of package CALENDAR
CC
COMPILE ADA-CAL-SPEC:ADA 0
CLOSE-LIBRARY
EXIT
EXIT
@CC
@CC compile a local version package CALENDAR PLANC routines
@CC
@CC @ND PLANC
@CC DEBUG-MODE ON
@CC COMPILE (ADA-COMMON)ADA-CAL:SYMB,0,(ADA-COMMON)ADA-CAL-A00:NRF
@CC
@CC Compile package IO_EXCEPTIONS (specification only, body is not required)
@CC
@ND
ADA
LIBRARY
OPEN-LIBRARY ADA-ENVIRONMENT

EXIT
CC
CC The ADA-COMMON version of package IO_EXCEPTIONS
CC
COMPILE ADA-IOX-SPEC:ADA 0
CC
CC The Text_IO package specification
CC
COMPILE ADA-TIO-SPEC:ADA 0
CC
CC The Text_IO package body
CC
COMPILE ADA-TIO-BODY:ADA 0
CLOSE-LIBRARY
EXIT
EXIT
@CC
@CC Compile the PLANC version of Text_IO routines
@CC
@CC @ND PLANC
@CC DEBUG-MODE ON
@CC COMPILE (ADA-COMMON)ADA-TIO:SYMB,0,(ADA-COMMON)ADA-TIO-A00:NRF
```
(the file ends there — 1744 bytes total, fully captured)

**Reading it**: confirms the `ADA:` top-level command (`@ND` then `ADA`) and the `LIBRARY`
sub-command group described in the PI sheet's command diagram. A "library" (`:ALIB` file) holds
compiled Ada package units; `CREATE-LIBRARY`/`OPEN-LIBRARY`/`CLOSE-LIBRARY`/`COMPILE` are the real
verbs. The commented-out (`@CC`) PLANC compile lines are left in the script as documentation —
the actual `CALENDAR`/`TEXT_IO` runtime bodies for these two packages are implemented in PLANC
(matching the PI sheet's "PLANC routines can be incorporated... by use of the interface pragma"
claim) and were pre-compiled into `ADA-CAL-A00:NRF`/`ADA-TIO-A00:NRF` rather than compiled fresh
by this script.

## Compiling, linking, and running a program — real, decoded `ADA-DEMO-A00:MODE`

Source: byte-for-byte decode of the real `:MODE` file, in full. [MODE]

```
@CC
@CC            This file compiles and runs the HANOI demonstration.
@CC It creates a library partition TEST:ALIB, a domain TEST with segment TEST.
@CC             If any of these already exist they will be deleted.
@CC                It produces an nrf file ADA-TEST-0000001:NRF.
@CC             The display will only work on a Tandberg terminal.
@CC
@DELETE-USER-FILE ADA-TEST-0000:NRF N
@DELETE-FILE TEST:ALIB
@CREATE-FILE TEST:ALIB,,
@ND ADA
LIBRARY
CREATE-LIBRARY-PARTITION TEST

EXIT
COMPILE ADA-DEMO 1
LIBRARY
DOCUMENT-UNIT HANOI
TOWER OF HANOI DEMONSTRATION

EXIT
CLOSE-LIBRARY-PARTITION
EXIT
@ND LINK-LOAD-ADA
ABORT-BATCH-ON-ERROR OFF
RELEASE-DOMAIN TEST
DELETE-DOMAIN TEST
SET-DOMAIN "TEST"
OPEN-SEGMENT "TEST",,
ADA-PROGRAM-LOAD HANOI TEST
EXIT
@ND TEST
4
```

**Reading it**: this is the full real compile-link-run cycle for ND-Ada.
1. `@ND ADA` -> `LIBRARY` -> `CREATE-LIBRARY-PARTITION TEST` makes a private library partition
   (as opposed to the shared `ADA-ENVIRONMENT` library built above).
2. `COMPILE ADA-DEMO 1` compiles the demo unit into that partition (the `1` selects a listing
   option; not decoded further here).
3. A **separate top-level command family, `@ND LINK-LOAD-ADA`**, does the linking — confirmed real
   verbs `RELEASE-DOMAIN`/`DELETE-DOMAIN`/`SET-DOMAIN`/`OPEN-SEGMENT`/`ADA-PROGRAM-LOAD`. This
   matches the `ADA.LINK:` command group named in the PI sheet's command diagram.
4. `@ND TEST` starts the built domain directly by its own name; `4` is a parameter passed to the
   running program (not decoded further — likely a demo menu selection).

## Documentation
- Product Information (PI-sheet): [../../Product-Info/ND-10745-A1-EN.md](../../../Product-Info/ND-10745-A1-EN.md)
- Manual(s): `ND-60.198` ND-Ada User Manual · `ND-60.158` Symbolic Debugger User Manual ·
  `ND-60.136` ND-500 Loader/Monitor — none located in this repo

## Provenance & open items
- Source: two real 8" floppy images, downloaded from NDwiki and decoded in this session
  (`ndfs -t`/`ndtool -x` for the file listing/extraction, `byte & 0x7F` for both `:MODE` files).
- **TODO:** `INSTALL-ADA-A00:PROG`'s exact interactive prompts were not decoded (compiled binary).
  The command-diagram groups `ADA:` (general/compiler) and `ADA.LIB:` (library maintenance) are
  now evidenced by the two scripts above; no separate worked example of the raw `ADA` compiler
  top-level commands (outside the `LIBRARY` sub-menu) was found.

---
**Parent:** [../README.md](../README.md) (`ND-10745` product overview)
