# NRF File Format (ND Relocatable Format)

**NRF** is the relocatable object-code format produced by ND-500(0) compilers
and assemblers (PLANC, FORTRAN, COBOL, PASCAL, ADA, C, MAC/ASSEMBLY) and consumed
by the old ND-500 Linkage-Loader (NLL, ND-210319/ND-10319) and the newer ND Linker
(ND-211224). Default file type is `:NRF`. It is the ND-500(0) sibling of
[BRF-FILE-FORMAT.md](BRF-FILE-FORMAT.md) - same role (compiler output, consumed by
a loader/linker), different byte layout and target machine.

**Primary sources:**

- `ND-60.136.04A ND-500 Loader Monitor.md` (NDInsight `Reference-Manuals/`), chapter 12
  "THE ND RELOCATABLE FORMAT" - the control-byte bit layout and the full control-number
  table (this is the NLL-era manual, the authoritative source for the bit packing)
- `ND-860289-2-EN ND Linker User Guide and Reference Manual.md` (NDInsight
  `Reference-Manuals/`), Appendix D "The ND Relocatable Format" - corroborating,
  slightly newer revision (adds SIMULA/ADA/CORAL/C/BASIC language codes and a target-machine
  byte not present in the NLL-era manual)
- `ND-10319-A1-EN.pdf` (mirror-sintran-com `library/libpdpi/`) - NLL product sheet,
  names the loader/monitor manual above as the detailed reference

**Validation:** the control-byte bit order (control number is the high 5 bits, numeric
length NL is the low 3 bits) was **VERIFIED against a real compiler-produced NRF file**,
`nd-500-apf-lib-e.nrf`, from the ND-500 microcode set outside this repo (an APF/array-processing vector math
library: `VADDXXX`, `VSUBXXX`, `VMULXXX`, `VDOTPR`, `VSQRTXX`, ... - assembly-language
output, not microcode). Three independent exact matches, each too specific to be
coincidental:

| Byte offset | Value | Decoded as | Confirms |
|---|---|---|---|
| 0x00 | `C8` | `MSG` (31 oct = 25 dec), NL=0 | top5=`11001`=25=MSG |
| 0x01 | `11` | Symbol length = 17 | next 17 bytes = `"ND-500-APF-LIB-E$"` exactly (the `$` triggers CR/LF on print, matching the MSG group's documented behavior) |
| 0x13 | `0A` | `BEG` (1 oct/dec), NL=2 | top5=`00001`=1=BEG; numeric bytes = priority 0, language 0=ASSEMBLY |
| 0x16 | `20` | `LIB` (4 oct/dec), NL=0 | top5=`00100`=4=LIB |
| 0x17 | `07` | Symbol length = 7 | next 7 bytes = `"VADDXXX"` exactly - matches LIB's documented "conditional P symbol, DEF must follow" |
| 0x1F | `28` | `DEF` (5 oct/dec), NL=0 | top5=`00101`=5=DEF |
| 0x20 | `0A` | Symbol length = 10 | next 10 bytes = `"#(+PROG0+)"` exactly (leading `#` = hidden symbol, per spec) |

This closes the open "TO-VALIDATE" item in
`../ND500/NRF-MINIMAL-SYNTHETIC-TEST-FILE.md` section 6 (bit packing was previously
only DERIVED from the manual's prose, never checked against a real file).

Related: [DESCRIPTION-FILE-FORMAT.md](DESCRIPTION-FILE-FORMAT.md) - the per-user index
an old-format domain needs to resolve a name to files; `../ND500/NRF-MINIMAL-SYNTHETIC-TEST-FILE.md` -
a hand-built minimal NRF fixture for loader unit tests (test-fixture design note, not a
general spec - this file is the general spec).

---

## 1. Overall structure

An NRF file is a sequence of **NRF groups**. Each group is:

```
<control field><numeric field><symbolic field>
```

- **Control field (1 byte, mandatory)**: high 5 bits = NRF control number (0-37 octal),
  low 3 bits = numeric length NL (0-7). VERIFIED bit order, see above.
- **Numeric field (0-7 bytes, length = NL)**: signed, 2's complement. Always present in
  the sense that NL itself is always in the control byte, but contributes zero trailing
  bytes when NL=0.
- **Symbolic field (present only for control numbers marked (S) below)**: 1 length byte
  (SL, 0-255) followed by SL ASCII bytes (parity bit cleared). Non-printing bytes are
  valid; two symbols are equal only if both length and all bytes match. A symbol whose
  first character is `#` is hidden from the user in symbol-table listings.

## 2. Loading model: PP / DP / XP / BP

The loader (NLL, or the ND Linker in NRF-load mode) tracks byte pointers:

| Pointer | Meaning |
|---|---|
| **PP** | Program byte pointer - current load address in the program segment. Referenced in loader expressions as `#PCLC`. |
| **DP** | Data byte pointer - current load address in the data segment (`#DCLC`; common blocks use `#CCLC` if a FORTRAN-COMMON-SEGMENT is open, else `#DCLC` too). |
| **XP** | Free pointer - used to patch/overwrite already-loaded information without disturbing PP/DP. |
| **BP** | Whichever of PP/DP/XP is active, depending on current mode (PMO/DMO/FMO). |

After a `BEG`, mode is PMO (program) by default. `PMO`/`DMO`/`FMO` control numbers
switch mode; `FMO` (free mode) is reset back to PMO or DMO by loading another `PMO`/`DMO`.

## 3. Control number table

Numbers are **octal** (the manual's own numbering skips 8/9, going 7 -> 10 -> 11 ...).
(S) marks control numbers with a symbolic field.

| Oct | Dec | Name | (S) | Meaning |
|---|---|---|---|---|
| 0 | 0 | NUL | | Ignored. NL must be 0. |
| 1 | 1 | BEG | | Start of module. Numeric bytes: 1=RT priority, 2=language code (see below), 3=address length ADL (default 1; PP/DP rounded up to a multiple of ADL before load), [4=target machine/type, 5=OSID - Linker-manual revision only]. Mode becomes PMO. |
| 2 | 2 | END | | End of module. NL = checksum size in bytes (0 = no test, 2 = default). Checksum = sum of all bytes from BEG to END inclusive, ignoring overflow, 2's complement. |
| 3 | 3 | MSA | | Main start address := current BP (+ numeric value if NL>0). First MSA wins if more than one is loaded; a warning is issued. |
| 4 | 4 | LIB | S | Library conditional-load symbol. If the symbol is referenced but undefined, the rest of the module loads; otherwise it is skipped. NL has no meaning for program LIB. For data LIB with NL>0, treated as a FORTRAN common block of size N. |
| 5 | 5 | DEF | S | Program symbol definition. NL=0: symbol value := PP. NL!=0: symbol value := numeric field (sign-extended to ADL if NL<=ADL). Resolves prior references. |
| 6 | 6 | REF | S | Program symbol reference at current BP. NL=0: value occupies next ADL bytes; NL!=0: next NL bytes. BP += that many bytes. When the symbol resolves, `numeric_value + symbol_value` is stored into those bytes. |
| 7 | 7 | LRF | S | Like REF if the symbol is already defined; if undefined/absent, stores zero instead. |
| 10 | 8 | DDF | S | Data symbol definition. Same as DEF but for DP/data memory; for C/COBOL/FORTRAN/PASCAL with NL>0, defines a common block of size N (no new block if already defined). |
| 11 | 9 | DRF | S | Data symbol reference. Same as REF but for data symbols. Illegal in debug-mode NRF. |
| 12 | 10 | RMV | S | Remove the named symbol from the loader's symbol table (avoids table overflow / name clashes between modules). |
| 13 | 11 | SLA | S | Set load address. BP := numeric value (+ symbol value if SL!=0). Load mode unchanged. |
| 14 | 12 | AJS | | Adjust. BP += signed numeric value (+ symbol value if SL!=0, per Linker-manual revision). Load mode unchanged. |
| 15 | 13 | PMO | | Set program mode. PP := PP + numeric value; BP := PP. |
| 16 | 14 | DMO | | Set data mode. DP := DP + numeric value; BP := DP. |
| 17 | 15 | FMO | S | Set free mode. BP := XP := BP + numeric value, or (if SL!=0) symbol value + numeric value. PP/DP untouched; resume with PMO/DMO. |
| 20 | 16 | REP | | Repeat. The following NRF group (or whole compound group, MIS/CGR0..CGR1) repeats the given number of times. |
| 21 | 17 | LDI | | Load immediately. The NL trailing bytes are stored at BP; BP += NL. Max 7 bytes/group (NL is 3 bits). |
| 22 | 18 | ADI | | Add immediately. Numeric value is added into the NL bytes at BP; BP += NL. |
| 23 | 19 | APA | | Add program address. `PP + numeric value` stored into the next ADL bytes; BP += ADL. |
| 24 | 20 | ADA | | Add data address. `DP + numeric value` stored into the next ADL bytes; BP += ADL. |
| 25 | 21 | IHB | | Execution inhibit - NRF is incomplete due to compile errors. |
| 26 | 22 | EOF | | End of NRF file. |
| 27 | 23 | DBG | | Debug start/stop marker. NLL copies the bytes between two DBGs to the `:LINK` file instead of `:PSEG`/`:DSEG`. |
| 30 | 24 | LBB / LMB | S | Library module byte-pointer (fast-load vector entry). Numeric field = byte offset of a module in the file; loaded unconditionally on first pass if the symbol field is empty, or when the named symbol is referenced-but-undefined. N=0 and S=NUL marks vector start; N=-1 and S=NUL marks vector end. Repeats in passes until all referenced symbols resolve. |
| 31 | 25 | MSG | S | Message. Prints the symbolic field's ASCII string; `$` (36 dec) converts to CR+LF on output. Only printed if the module containing it is actually loaded (or it precedes the fast-load vector in a library). Numeric field ignored. |
| 32 | 26 | MIS | | Miscellaneous; numeric field = subcontrol number (see below). |
| 33 | 27 | LDN | | Load N bytes immediately. **Not** the same shape as LDI: the numeric field is a byte *count* N (unsigned), and N more raw literal bytes follow the header, appended after the numeric field rather than being it - no symbolic field either way. Confirmed 2026-08-11 against NC-LIB-A06.NRF: treating LDN as a plain group (control + NL numeric bytes, nothing more, as if "same as LDI") desyncs the whole rest of the stream after the first LDN - see [HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md](HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md) for the full record; the fix is in `src/lib/nrf/nrf_utils.c` of the `pcc-nd500` repository (commit `c82cbfc`) and in the viewer's `nrfReadGroup`. |
| 34-37 | 28-31 | IL1-IL4 | | Illegal control numbers (reserved). |

### MIS (32) subcontrol numbers

| Sub | Name | Meaning |
|---|---|---|
| 0 | CGR0 | Start of compound group (for REP; nestable). |
| 1 | CGR1 | End of compound group; closes only the innermost nesting level. |
| 2 | ADD | Add the next referenced symbol's value into the location at BP. |
| 3 | SUB | Subtract the next referenced symbol's value from the location at BP. |
| 4 | MUL | Multiply the value at BP by the next referenced symbol. |
| 5 | DIV | Divide the value at BP by the next referenced symbol. |

### BEG language codes

| Code | Language | Code | Language |
|---|---|---|---|
| 0 | ASSEMBLY | 5 | SIMULA |
| 1 | FORTRAN | 6 | ADA |
| 2 | PLANC | 7 | CORAL |
| 3 | COBOL | 8 | C |
| 4 | PASCAL | 9 | BASIC |

(Codes 5-9 appear only in the newer ND Linker manual revision; the NLL-era manual
only documents 0-4.)

## 4. Symbol type bits (CW), as tracked in the loader table

Carried in the loader's in-memory symbol table (and mirrored into the `:DESC` file's
Symbol Entry `CW` byte - see [DESCRIPTION-FILE-FORMAT.md](DESCRIPTION-FILE-FORMAT.md)):

| Bit | Name | Meaning |
|---|---|---|
| 0 | UDEF | false = undefined element |
| 1 | DREF | false = program memory reference, true = data memory reference |
| 2 | DSYM | false = program label, true = data label |
| 3 | CLAB | true = common label |
| 4 | DMPF | true = symbol is written (used in list handling) |
| 5 | GLOB | true = symbol survives a loader-table save |
| 6 | SELECT | true = module must be loaded |
| 7 | OMIT | true = module must not be loaded |

## 5. Open items / not yet verified

- The BEG numeric field's byte count beyond the first 3 (target machine/type byte,
  OSID byte) has not been checked against a real file - `nd-500-apf-lib-e.nrf`'s BEG
  group has NL=2 (only priority + language), so those trailing bytes were never
  exercised.
- The exact reconstruction of a full linear code/data buffer from an NRF file
  (walking LDI/REF/PMO/DMO/AJS to reproduce what NLL would place in `:PSEG`/`:DSEG`)
  has not been implemented or tested against `nd-500-apf-lib-e.nrf` end-to-end.
- LBB/fast-load-vector behavior is transcribed from the manual only; no real library
  file's fast-load vector has been walked yet.
