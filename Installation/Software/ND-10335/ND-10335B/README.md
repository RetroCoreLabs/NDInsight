# ND-10335B — ND-500 Symbolic Debugger, version B

> Status: VERIFIED (transcribed from PD sheet; not yet run live)   ·   Install source: [PD]

| Field | Value |
|-------|-------|
| Part number | `10335B` (source article: `10348B`) |
| Base product | [`ND-10335`](../README.md) |
| Version | B |
| Release date | 82.02.10 (10 Feb 1982) |
| CPU target | ND-500 |
| OS requirement | SINTRAN III VS. **Requires ND-500-MONITOR Version B or later** (this version's own requirement, stated on the PD sheet) |

## Description
Symbolic Debugger for FORTRAN, PLANC and COBOL. This revision: implements real (floating-point)
constants in debugger expressions, hexadecimal/binary constant literals (`0F9EH`, `100110X`),
improved array printing (paginated, FORTRAN 2-D arrays no longer transposed), an improved
`INVOKE` command (normal PLANC routines, more parameter types), stack-relative addressing in
`LOOK-AT-STACK`, `segment'address` notation (e.g. `16'1233B`), and several minor error
corrections. [PD]

## Prerequisites
- **Hardware/OS:** ND-500, SINTRAN III VS, **ND-500-MONITOR Version B or later** (a hard
  requirement stated on this version's own PD sheet — earlier monitor versions are not
  supported). [PD]
- **Dependency:** the debugger calls routines in the **FORTRAN library**, which must therefore
  always be present — see "Installation procedure" below. [PD]

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `ND-10335B` (per the actual mounted floppy and the PD sheet's own loading-procedure text) | `DEBUGGER-B:NRF` (66 pages, program number `203318B`), user `FLOPPY-USER` |

Confirmed by downloading the image (MD5 `138f37dfa978bee02fd9077576133f33`) and reading with
`ndtool -t` — matches the PD sheet's file list exactly.

> **Directory-name discrepancy, as printed on the PD sheet:** page 1 (the Diskette Directory
> listing) prints the directory name as `ND-10335E` and the file as `DEBUGGER-E:NRF`. Every other
> mention on the same document — the Program Description header, the Loading/Operating Procedure
> text, and the Revision Log — consistently says `10335B`/`DEBUGGER-B:NRF`, and the actual
> downloaded floppy is volume `ND-10335B` containing `DEBUGGER-B:NRF`. The page-1 `E` is almost
> certainly an OCR misread of `B`, not a real second revision.

## Installation procedure

Source: PD sheet "Loading/Operating Procedure, Use", verbatim. [PD]

1. Copy the debugger off the floppy:
   ```
   @ENTER-DIRECTORY ND-10335 <Floppy disk name and unit>
   @COPY-FILE "DEBUGGER-B:NRF" (ND-10335:FLOPPY-USER)DEBUGGER:NRF
   @RELEASE-DIRECTORY ND-10335
   ```
2. **This is not a reentrant-dump install.** Unlike every other product in this catalog, the
   debugger is `:NRF` (a linkable object module) and gets loaded fresh into **each** debugged
   program's own domain, via the ND-500 **Linkage-Loader**'s `TOTAL-SEGMENT-LOAD` command — not
   `DUMP-REENTRANT`/`DUMP-PROGRAM-REENTRANT`. It may be loaded onto any of the user program's
   segments, or a dedicated separate segment.
3. **The FORTRAN library must always be loaded (not linked), and loaded before the debugger** —
   the debugger calls FORTRAN library routines internally regardless of what language the target
   program is written in.
4. Per-language conditions on the program **being debugged** (not the debugger itself):
   - **FORTRAN:** no special restrictions.
   - **PLANC:** the debugger must be explicitly invoked — `IMPORT (ROUTINE VOID, VOID: DEBUG)`.
     The calling module itself does not need `DEBUG-MODE`.
   - **COBOL:** the main program must be compiled in `DEBUG-MODE`.
   - Modules in different languages may be mixed as long as each satisfies its own condition
     above.

## Usage (from the PD sheet, not part of "installation" but needed to verify a working install)

Use `DEBUG-PLACE` instead of the normal `PLACE` monitor command, or debugger commands fail with
`ATTEMPT TO MODIFY READ-ONLY SEGMENT`:
```
@ND-500-MONITOR
N500: DEBUG-PLACE MY-DOMAIN
N500: RUN
SEGMENT NUMBER(S) OF SEGMENT(S) WITH DEBUG-INFORMATION: 8
NAME OF SEGMENT 8D: MY-DOMAIN
ND-500 SYMBOLIC DEBUGGER - 203318B. FEBRUARY 10, 1982.
PLANC PROGRAM. Starting scope
*
```
The debugger asks for every segment used by the program, whether or not each one was compiled
with `DEBUG-MODE`. With multiple debug-info segments, `SCOPE .<segment> <routine>` moves the
current scope (e.g. `SCOPE .19 XROUT`).

## Configuration / post-install
None beyond the per-program load described above — there is no resident subsystem to persist
across a cold start; the debugger is loaded fresh with each debugged program.

## Documentation
- PD-sheet: [../../../Reference-Manuals/ND-10335B ND-500 SYMBOLIC DEBUGGER.md](../../../../Reference-Manuals/ND-10335B%20ND-500%20SYMBOLIC%20DEBUGGER.md)
- PI-sheet: [../../../Product-Info/ND-10335-C1-EN.md](../../../Product-Info/ND-10335-C1-EN.md) (covers ND-10335/ND-10336 together)
- Manual(s): `ND-60.158.01` Symbolic Debugger Reference Manual

## Provenance & open items
- Source: single OCR'd PD-sheet scan, cross-checked against the actual downloaded floppy image.
- **TODO:** this install has not been run live in the emulator.

---
**Parent:** [../README.md](../README.md) (`ND-10335` product overview)
