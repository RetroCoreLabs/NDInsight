# ND-10023K — FORTRAN (48-bit), version K

> Status: STUB — no PD sheet, procedure inferred by pattern, NOT verified   ·   Install source: [INF]

| Field | Value |
|-------|-------|
| Part number | `10023K` (as printed on the floppy volume label) |
| Base product | [`ND-10023`](../README.md) |
| Version | K |
| Release date | files on disk dated 1979-07-12 (libraries) and 1979-07-26 (compiler, print utility) |
| CPU target | NORD-10, 48-bit floating-point |
| OS requirement | unknown |

## Description
FORTRAN compiler for NORD-10 (48-bit float). Single floppy, four files, no installer script and
no PD sheet — everything here is read from the mounted floppy's directory listing only.

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `ND-10023K` | `FTN-2090I:BPUN` (the compiler, 32 pages) · `FTNLIBR-2091F:BRF` (library, 18 pages) · `FTNRTLIBR-2092F:BRF` (runtime library, 14 pages) · `PRINT-FILE-2324B:BPUN` (a print utility, 9 pages), user `FLOPPY-USER` |

Confirmed by downloading the image (MD5 `d5799ff428b0bc95b980bd90167ead26`) and reading it with
`ndtool -t`. Note the four files each carry their own independent revision letter/number
(`2090I`, `2091F`, `2092F`, `2324B`) under the single volume revision `K` — the same
per-file-revision pattern seen in this catalog's Subsystem Package II and PLANC entries.

## Installation procedure — INFERRED, NOT CONFIRMED

No install text exists on this floppy (no `:MODE` script, no PD sheet). By pattern with every
other simple `:BPUN`-shaped product in this catalog (PLANC A/B, Backup-System B):

1. Enter the floppy directory and copy all four files to the user where you keep compiler
   binaries (commonly `SYSTEM`):
   ```
   @ENTER-DIRECTORY ND-10023K,FLOPPY-DISC-1,0,
   @COPY-FILE "FTN-2090I:BPUN",(SYSTEM)FTN:BPUN
   @COPY-FILE "FTNLIBR-2091F:BRF",(SYSTEM)FTNLIBR:BRF
   @COPY-FILE "FTNRTLIBR-2092F:BRF",(SYSTEM)FTNRTLIBR:BRF
   @COPY-FILE "PRINT-FILE-2324B:BPUN",(SYSTEM)PRINT-FILE:BPUN
   ```
2. Dump the compiler reentrant. **Start address 0, restart address 1.** Source: the Program
   Description sheet for `FTN-2090I` ("FTN", NORD 10/100 FORTRAN COMPILER, PART OF ND-NUMBER
   10023K and 10033K), printed in
   [ND-10033K FORTRAN 32 BITS FLOATING FORMAT](../../../Reference-Manuals/ND-10033K%20FORTRAN%2032%20BITS%20FLOATING%20FORMAT.md):
   boundaries `0<76370+tables`, START ADDRESS 0, RESTART ADDRESS 1. That sheet is shared by the
   48-bit (10023K) and 32-bit (10033K) products, and the floppy file name `FTN-2090I` matches the
   sheet's revision log. Its own example is `@DUMP-REENTRANT FTN-20901,0,1,<input file>` (the
   sheet's OCR prints the letter I as a digit 1). [DOC]
   ```
   @DUMP-REENTRANT FTN,0,1,(SYSTEM)FTN-2090I:BPUN
   ```
   **Run on the nd100x emulator (SINTRAN III VSX/500 L): it works.** The command prints nothing on
   success; a second run answers `NAME ALREADY USED ON REENTRANT SUBSYSTEM`; `@LIST-REENTRANT`
   shows `0B 1B 142B FTN`; `@FTN` then prints `NORD-10/ND-100 FORTRAN COMPILER FTN-2090I`.

**Do not treat the above as verified.** Step 1 follows the well-established copy pattern; step 2
is incomplete without a source for the actual addresses.

## Configuration / post-install
Unknown.

## Documentation
- PD-sheet: not located
- PI-sheet: not located
- Manual(s): `ND-60.145` ND FORTRAN Reference Manual (assumed applicable, not confirmed for this
  specific 48-bit product)

## Provenance & open items
- Source: floppy directory listing only, via `ndtool` on the downloaded image.
- Start/restart addresses (0 and 1) found in the `FTN-2090I` Program Description sheet, see
  step 2. They come from the document, not from a run.
- Checked: the downloaded image (MD5 above) holds exactly the four files listed, with the sizes
  in the catalog. The three files `FTN-2090I:BPUN`, `FTNLIBR-2091F:BRF` and
  `FTNRTLIBR-2092F:BRF` were written into `(SYSTEM)` on a SINTRAN SMD pack with `ndtool --put` and
  read back byte for byte identical.
- `@DUMP-REENTRANT` and compiles have now been run live: `ADV-INIT` compiled with no messages.
  The same compiler **rejected 11 lines** of ordinary logical-function code in a 1152-line program
  (`"LOG. EXPR" ILL. ASSIGNMENT`) that the newer F02 compiler accepts. Prefer
  [ND-210191F02](../../ND-210191/ND-210191F02/README.md); see
  [FORTRAN-BUILD-LEARNINGS-FAQ](../../../../Developer/Languages/Application/FORTRAN-BUILD-LEARNINGS-FAQ.md).
- **TODO:** the 32-bit sheet says the libraries are loaded at link time (`FTNLIBR`,
  `FTNRTLIBR` = the reentrant runtime). Which of the two a given program needs is not confirmed.

---
**Parent:** [../README.md](../README.md) (`ND-10023` product overview)
