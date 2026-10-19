# BRF File Format (Binary Relocatable Format)

**BRF** is the relocatable object-code format produced by all ND language processors
(MAC assembler, FORTRAN, COBOL, PLANC, BASIC, PASCAL, NPL, C) and consumed by the
ND Relocating Loader, the Real Time Loader and the BRF Editor. Default file type is `:BRF`.

**Primary sources:**

- [ND-60.066.04 ND Relocating Loader](../../Reference-Manuals/ND-60.066.04%20ND%20Relocating%20Loader.md) - chapter 2 (format), chapter 3 (BRF Editor)
- [ND-60.085.01 BRF EDITOR](../../Reference-Manuals/ND-60.085.01%20BRF%20EDITOR.md) - standalone editor manual (later merged into ND-60.066)

**Validation:** every structural claim below marked VERIFIED was checked byte-by-byte
against two real BRF files (PLANC compiler output, ENCOS error modules,
`Installation/Communication/Ethernet/x/encos-err-i-b01.brf` and `encos-err-ii-b01.brf`).
See [Validation Against Real Files](#validation-against-real-files) at the end.

Related: [PROG-FILE-FORMAT.md](PROG-FILE-FORMAT.md) - the executable format the loader
produces from BRF input.

---

## Tools

- **[nd100_brf.py](../../scripts/nd100_brf.py)**: parser. Lists every unit and symbol, checks every
  unit's checksum, builds the relocation map for the disassembler. `--names` prints every name a
  file defines, `--find NAME` shows where a name is defined or used, `--json` for other tools.
- **[brf_library_catalog.py](../../scripts/brf_library_catalog.py)**: runs the parser over every
  `:BRF` on the archive floppies and writes
  [LINK-LIBRARY-ENTRY-POINTS.md](../../Developer/Workflow/LINK-LIBRARY-ENTRY-POINTS.md) (every
  library and every name it defines) and
  [LINK-LIBRARY-NAME-INDEX.md](../../Developer/Workflow/LINK-LIBRARY-NAME-INDEX.md) (which library
  defines a name).

---

## 1. Overall Structure

BRF is a **byte stream** of 8-bit bytes, not bound to any particular medium
(paper tape, magnetic tape, disc file). It is a sequence of **BRF groups**, each
starting with a one-byte **control byte** interpreted as a loader command:

```
<control byte>
<control byte><P-group>
<control byte><P-group><P-group>
<control byte><S-group>
<control byte><S-group><P-group>
```

Three kinds of information:

| Element      | Size                          | Content |
|--------------|-------------------------------|---------|
| Control byte | 1 byte                        | Control number (loader command), values 0-54 octal |
| P-group      | 2 bytes                       | One 16-bit word, **most significant byte first** (VERIFIED - checksums only match with big-endian word assembly) |
| S-group      | 4 bytes (6 bytes after LONGF) | A symbol of 1-7 six-bit characters, right-justified, space (0) padded |

A BRF **file** contains one or more BRF **units** (see section 2), optionally
separated/padded by zero bytes (control number 0 = FEED, "neglect" - VERIFIED:
the sample files contain long runs of 0x00 padding between units, and the last
unit is followed by control number 23 octal = EOF as the final byte).

---

## 2. Program Units

Each compiled program unit (main program or subprogram) is one BRF unit:

```
BEG (17)                          first control byte of the unit; loader sets program base PB = CLC
[LONGF (32)]                      optional; flags that all S-groups in this unit are 6 bytes
[LIBR <sym>]                      zero or more; library entry points (conditional loading)
... code, data, fixups, ENTR/REF/MAIN groups ...
END (21) <checksum P-group>       last group of the unit
```

- A unit contains at least one of MAIN (14) or ENTR (16).
- A **library subprogram** has LIBR group(s) at the beginning of the unit. The loader
  only loads the unit if the LIBR symbol has been REFerenced and is not yet defined;
  otherwise the unit is check-read (syntax and checksum still verified) up to END and skipped.
- Load order of main/subprogram units is arbitrary; library units are loaded last.
  If library unit A references library unit B, A must appear first in the file.
- EOF (23) ends loading for the whole file.

VERIFIED: both sample files contain 174 units each; every unit starts with BEG and
ends with END + checksum. 167 of the 174 units carry LONGF (6-byte S-groups,
PLANC output); 7 units do not (4-byte S-groups).

**LONGF scope (observed behavior, not stated explicitly in the manual):** LONGF
applies only to the unit it appears in. Each BEG resets the S-group size to the
default 4 bytes; a unit must repeat LONGF to get 6-byte S-groups. VERIFIED: the
sample files mix LONGF and non-LONGF units, and parsing only stays in sync (all
checksums pass) when the flag is reset at every BEG.

---

## 3. Control Numbers

Terminology (from ND-60.066.04 section 2.9):

- **CLC** - current location counter: address where the next word is placed
- **PB** - program base of the current unit. Relative addresses count the first word of the unit
  as 1, so the value the loader adds is the CLC value when BEG was read **minus 1**: `LR W1`
  stores `L + W1 - 1`, `AFR W1,W2` patches the word at `L + W2 - 1`, `ARF W1,W2` adds `W1 + L - 1`,
  `SRL W1` sets CLC to `L + W1 - 1` (L = address of the unit's first word). The table below writes
  `W1+PB` with this PB. Checked with the real BRF-LINKER C01 (nd100x, 2026-10-12) on hand-made
  units loaded behind another unit (L = 8): `LR 1` gave 0008, `LR 0` gave 0007, `AFR 100,2`
  changed the second word, `ARF 3,8` added 3 + 7, `SRL 6` placed the next word at 13. The same
  with and without a LONGF group in the unit. Not run through the tool: ARR, INL, LC, LRP, LRD
  and the other groups of the table (they are written with the same PB; whether the loader
  uses PB - 1 for them too is not checked).
- **CDB** - COMMON data base (COMMON block address)
- **W1..Wn** - contents of the 1st..n'th P-group of the group
- **ADR** - value of the COMMON block symbol named by the S-group (control numbers 40-43, 45)
- `X -> (Y)` means the value X replaces the contents of address Y

All control numbers are given in **octal**. "Words" = number of P-groups following
the control byte (S-group not counted; it adds 2 words, or 3 with LONGF).

| Ctrl (oct) | Mnemonic | Words   | S-group | Interpretation |
|-----------|----------|---------|---------|----------------|
| 0         | FEED     | 0       | -       | Neglect (padding, blank tape) |
| 1         | LF       | 1       | -       | Load word: W1 -> ((CLC)), CLC+1 -> (CLC) |
| 2         | LR       | 1       | -       | Load relocated: W1+PB -> ((CLC)), CLC+1 -> (CLC) |
| 3         | LC       | 1       | -       | Load COMMON-relative: W1+CDB -> ((CLC)), CLC+1 -> (CLC) |
| 4         | AFF      | 2       | -       | Fixup: W1+(W2) -> (W2) |
| 5         | ARF      | 2       | -       | Fixup: W1+PB+(W2) -> (W2) |
| 6         | AFR      | 2       | -       | Fixup: W1+(W2+PB) -> (W2+PB) |
| 7         | ARR      | 2       | -       | Fixup: W1+PB+(W2+PB) -> (W2+PB) |
| 10        | SFL      | 1       | -       | Set load address: W1 -> (CLC) |
| 11        | AFL      | 1       | -       | Advance load address: W1+CLC -> (CLC), fill zeros |
| 12        | SRL      | 1       | -       | Set relative load address: W1+PB -> (CLC) |
| 13        | -        | -       | -       | Not used |
| 14        | MAIN     | 0       | yes     | Symbol becomes the main entry (start address) |
| 15        | LIBR     | 0       | yes     | Library entry point; conditional loading |
| 16        | ENTR     | 0       | yes     | Symbol is assigned the value of CLC (entry point) |
| 17        | BEG      | 0       | -       | Begin unit: CLC -> PB |
| 20        | REF      | 0       | yes     | Symbol is referenced at CLC (external reference) |
| 21        | END      | 1       | -       | End unit; W1 is the BRF checksum (section 5) |
| 22        | INHB     | 0       | -       | Inhibit: compilation errors occurred |
| 23        | EOF      | 0       | -       | End of loading (end of file) |
| 24        | LNF      | 1+W1    | -       | Load N words fast: W1 = word count, then W1 words -> (CLC)..(CLC+W1-1) |
| 25        | RT       | 1       | -       | W1 contains real-time priority |
| 26        | ASF      | 1       | yes     | Allocate COMMON: S-group = block name, W = block length; symbol value = block start address |
| 27        | ADS      | 0       | yes     | Add COMMON address: value of symbol + (CLC-1) -> (CLC-1) |
| 30        | -        | -       | -       | Not used per manual - but see section 7 (observed in real files) |
| 31        | -        | -       | -       | Not used |
| 32        | LONGF    | 0       | -       | Flags 6-byte S-groups (this unit - see section 2) |
| 33        | -        | -       | -       | Not used |
| 34        | INL      | 2       | -       | Integer load: W2 -> (W1+PB) |
| 35        | DBL      | 3       | -       | Double load: Wi -> (W1+PB+i-2), i = 2..3 |
| 36        | RLL      | 4       | -       | Real load: Wi -> (W1+PB+i-2), i = 2..4 |
| 37        | CXL      | 7       | -       | Complex load: Wi -> (W1+PB+i-2), i = 2..7 |
| 40        | INC      | 2       | yes     | Integer to COMMON: W5 -> (W4+ADR); W1-W3 = COMMON block name (the S-group) |
| 41        | DBC      | 3       | yes     | Double to COMMON: Wi -> (W4+ADR+i-5), i = 5..6 |
| 42        | RLC      | 4       | yes     | Real to COMMON: Wi -> (W4+ADR+i-5), i = 5..7 |
| 43        | CXC      | 7       | yes     | Complex to COMMON: Wi -> (W4+ADR+i-5), i = 5..10 |
| 44        | BYL      | 2       | -       | Byte load: W2(bits 0-7) -> (W1+PB) bits 0-7 if W2 bit 15 = 0, bits 8-15 if bit 15 = 1 |
| 45        | BYC      | 3       | yes     | Byte to COMMON: W5(bits 0-7) -> (W4+ADR) bits 0-7 if W5 bit 15 = 0, bits 8-15 if bit 15 = 1 |
| 46        | NWL      | 1       | -       | W1 contains line number (not in use) |
| 47        | DBG      | 0       | -       | Debug mode on/off |
| 50        | PMO      | 0       | -       | Program bank mode (two-bank loading) |
| 51        | DMO      | 0       | -       | Data bank mode (two-bank loading) |
| 52        | LRP      | 1       | -       | Same as LR but with PB of the program bank |
| 53        | LRD      | 1       | -       | Same as LR but with PB of the data bank |
| 54        | DIC      | var     | -       | Dictionary table follows: elements of name (3 words) + byte pointer (2 words); table ends with a -1 (177777) word |

Notes on the manual's word counts for 14-16, 20, 26, 27 and 40-43, 45: the manual
counts the S-group as 2 words (3 with LONGF) and writes e.g. "2(3)" for MAIN. The
table above separates the S-group into its own column; the Words column counts only
the plain P-groups. For 40-43 and 45 the manual numbers the P-groups W4, W5, ...
because W1-W3 are the (LONGF) S-group words holding the COMMON block name.

The manual's group grammar in section 2.1 lists at most 2 P-groups per group, but
control numbers 24 (LNF), 35-37, 41-43, 45 and 54 exceed that; the grammar is
illustrative, not exhaustive. (LNF with large counts is by far the dominant code
carrier in compiler output - VERIFIED.)

### Two-bank loading (PMO/DMO)

PMO (50) and DMO (51) switch the loader between program-bank and data-bank load
addressing for two-bank program systems; LRP (52) and LRD (53) relocate against the
respective bank's program base. Used with IMAGE-FILE/PROG-FILE loading
(ND-60.066.04 section 1).

---

## 4. S-groups (Symbols)

An S-group holds a symbol of 1-7 characters in **six-bit code**, right-justified,
padded on the left with 0 (space):

- Default: 4 bytes = 32 bits = 5 six-bit characters + 2 pad bits (MAC assembler symbols)
- After LONGF: 6 bytes = 48 bits = 8 six-bit character positions, of which up to 7
  are used (FORTRAN, COBOL, PLANC, etc.)

Six-bit character code (VERIFIED by decoding real symbols): value 0 = space,
1-32 octal = `A`-`Z`, 33-37 = `[ \ ] ^ _`, 40-77 = ` ! " # $ % & ' ( ) * + , - . / 0-9 : ; < = > ?`.
That is **the low six bits of the ASCII value**: a letter is the code plus 100 octal, anything
from 40 octal up is the ASCII value itself (so the digits are 60-71 octal and `#` is 43 octal).
Bytes are consumed MSB-first. Earlier text here said "ASCII minus 40 octal"; that is only right
for the upper half of the table and gives garbage for letters. Checked against the BRF linker's
own `LIST-BRF-ENTRIES` on `FORT48-2BANK-F02:BRF`: 462 of 462 names identical (2026-10-15).

Examples decoded from the sample files (VERIFIED): `ENNS0` (MAIN), `POSUERR`,
`READPIO`, `SEGLOAD`, `UNLOAD`, `UEIEDIN` (LIBR+ENTR pairs).

Statement numbers (labels) in FORTRAN and BASIC are S-groups where the first two
and last two bytes are zero; bytes 3-4 hold the numeric label value.

### Symbol table and reference linking

The loader's symbol table entry is 3 words for the symbol + 1 word ADR:

- Symbol defined (ENTR read): ADR = memory address of the entry point.
- Symbol only REFerenced so far: ADR points to the **last** location that referenced
  the symbol; that location holds a pointer to the previous reference, forming a
  linked list through the loaded code. The first (oldest) reference location holds
  177777 (octal) as end-of-list marker. When the ENTR arrives, the loader walks the
  chain and patches every reference. One bit in the table entry distinguishes the
  two meanings of ADR.

---

## 5. Checksum

A checksum P-group follows every END (21) control byte. Algorithm
(ND-60.066.04 section 2.7, the 348 units named here were not re-counted; see the real-tool check below):

- Sum everything from the BEG control byte up to and including the END control byte:
  control bytes as 8-bit values, P-groups as 16-bit values, S-groups as two
  (three with LONGF) 16-bit values.
- Sum is taken modulo 2^16; the stored checksum is the two's complement of the sum, so that
  `(sum + checksum) AND 177777 = 0` (not the one's complement: the sum plus the stored word is 0,
  not 177777).
- Checked with the real BRF-LINKER C01 (SINTRAN III on nd100x, 2026-10-12): the object
  `HELLO.BRF` with the stored word `134775` (sum `043003`) is loaded without a message; the same
  object with the one's complement `134774`, or with `134777`, gives
  `Brl message: Chechsum error  MAIN.......473` (sic) at LOAD.

---

## 6. COMMON Blocks

- One-bank programs: COMMON is allocated downward from the upper bound of the load
  area; programs grow upward. Two-bank programs: COMMON is allocated upward from the
  current data load address, like other data.
- The **first** unit declaring a COMMON block fixes its address and (maximum) length
  via ASF (26): `<ASF><S-group = block name><P-group = length>`. Succeeding units
  cannot expand the block.
- COMMON data is referenced by indirect addressing; the loaded address word is
  followed by ADS (27): `<ADS><S-group>`, meaning the block address (symbol value)
  is added to the previously loaded word at CLC-1.
- Control numbers 40-43 (INC/DBC/RLC/CXC) and 45 (BYC) store constants directly into
  a COMMON block: the S-group names the block (must already be defined; its value is
  ADR), W4 is the offset, W5.. are the data.

---

## 7. Observed Extension: Control Number 30 (octal)

ND-60.066.04 lists 30 octal as "not used", but both sample files (PLANC compiler
output, ca. 1986-88 ENCOS sources) contain exactly one group with control byte
30 octal, structured like LNF:

```
30 <count P-group> <count x 16-bit words of ASCII text>
```

Observed payload: count = 8 words = 16 bytes of plain ASCII: `PLANC-1BANK-G00 `.

ASSUMPTION (UNVERIFIED interpretation): this is a compiler/runtime identification
stamp inserted by the PLANC compiler ("PLANC 1-bank runtime, version G00"),
presumably checked or listed by later loaders. The framing (count word + payload)
is verified; the meaning is not documented in any manual in this repository.

---

## 8. BRF Files and the BRF Editor

BRF units in a file are numbered from 1 (decimal). The BRF Editor
(chapter 3 of ND-60.066.04; SINTRAN subsystem) manipulates units:

- `LIST-ENTRIES` - list all ENTR/MAIN/LIBR symbols per unit
- `LIST-BRF` - disassembling dump of the BRF groups (control number, mnemonic, symbols; LF/LR words also shown as MAC assembly)
- `APPEND-FILE`, `APPEND-UNIT`, `FETCH-UNITS`, `DELETE-UNITS`, `EXCHANGE-UNITS` - unit-level editing; an EOF (23) byte is written at the end of the destination file
- `WRITE-EOF-AFTER-UNIT` - insert EOF after a given unit
- `MAKE-LIBRARY-UNITS` - insert a LIBR byte+symbol at the start of each unit (first ENTR symbol becomes the LIBR symbol)
- `MAKE-LIBRARY-FILE` - copy the file and prepend a dictionary unit (DIC, control number 54): five words per unit (3-word name + 2-word byte pointer), terminator -1; speeds up selective library loading
- `RENAME-SYMBOL` / `CHANGE-FILE` / `CLEAR-TABLES` - symbol renaming
- The editor checks all units for syntax and checksum errors

---

## 9. Validation Against Real Files

Validated 2026-07-07 with a Python parser implementing exactly the rules above,
against the two files in `Installation/Communication/Ethernet/x/`:

| File | Size (bytes) | Units | Checksums OK | Parse coverage |
|------|-------------|-------|--------------|----------------|
| encos-err-i-b01.brf  | 60909 | 174 | 174/174 | 100% (to last byte) |
| encos-err-ii-b01.brf | 61005 | 174 | 174/174 | 100% (to last byte) |

Control-number usage (encos-err-i-b01.brf): FEED 1651 (inter-unit zero padding),
LR 868, REF 834, LNF 715, AFR 567, LF 482, ENTR 214, LIBR 201, BEG 174, END 174,
LONGF 167, AFL 18, SRL 2, MAIN 1, LC 1, EOF 1, plus one undocumented 30-octal
group (section 7). No SFL, no fix-up 4/5/7, no COMMON (ASF/ADS), no two-bank
(PMO/DMO/LRP/LRD), no DIC groups occur in these files, so those word counts rest
on the manual only.

Facts established by the validation:

1. P-group byte order is big-endian (MSB first) - checksums fail otherwise.
2. Checksum = two's complement of the 16-bit sum from BEG through the END byte (sum + checksum = 0;
   BRF-LINKER C01 rejects the one's complement with "Checksum error", see section 5).
3. LONGF is per-unit; BEG resets S-group size to 4 bytes.
4. Six-bit symbol code is the low six bits of ASCII (see section 4), space-padded, MSB-first packing.
5. Zero bytes (FEED) pad between units; a single EOF (23) byte terminates the file.
6. Compiler output is dominated by LNF blocks with LR-relocated words interleaved.
