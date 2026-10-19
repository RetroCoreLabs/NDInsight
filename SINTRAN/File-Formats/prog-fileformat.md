# :PROG File Format - Byte-Level Layout

**Full path:** `prog-fileformat.md`

This document describes the on-disk byte-level layout of SINTRAN III `:PROG`
files (as produced by the Nord Relocating Loader and consumed by `@RECOVER`),
based on a combination of:

- The community-circulated 6-word header description.
- Direct reading of NPL sources in this repository.
- Empirical analysis of four real `:PROG` files from the `xmsg` subsystem.
- The companion document
  `PROG-FILE-FORMAT.md`,
  which describes the format operationally and lists what the published
  manuals do and do not document.

Where a fact is verified from source code or matches every test file, it is
marked **VERIFIED**. Where it is inferred from a single sample, it is marked
**INFERRED**. Where it is genuinely unknown, it is marked **UNKNOWN**.

---

## 1. Overall File Layout

A `:PROG` file is a fixed-format memory image of a loaded and linked program.
Three regions can appear in the file, at fixed file offsets:

| Region              | File offset (bytes) | File offset (octal words) | Present when                                    |
|---------------------|---------------------|---------------------------|-------------------------------------------------|
| Header              | `0x00000`           | block 0, words 0..7       | Always                                          |
| Bank 1 image (code) | `0x00200`           | block 1, word 0           | Always                                          |
| Bank 2 image (data) | `0x20000`           | block 0o400, word 0       | Two-bank programs only (header word 4 != 0177777) |
| Debug area (earlier called data-bank-copy) | `0x40000` | block 0o1000, word 0 | header word 7 != 0 (a debug part was saved)  |

Each region is padded with zero words up to the next region's start. The
file is then truncated/padded to a SINTRAN page boundary at the end of the
last region present.

> **VERIFIED** for header, bank 1 and bank 2 from all test files.
> **INFERRED** for the data-bank-copy region from a single sample
> (`xmsg-fido-l03.prog`). The real BRF-LINKER C01 calls this region the **debug** part, see
> section 2.3 (checked 2026-10-12).

---

## 2. Header Layout

The header is **8 16-bit words, big-endian**, at file offset 0 (section 2.3: the real
BRF-LINKER C01 reads eight). The monitor's `RECOVER` reads only the first 7 of them, which is
verified directly from NPL source:

```
RP-P2-MONCALLS.NPL:1903   INTEGER ARRAY RWPAR(5)   % PARAMETER LISTE FOR MON RFILE
RP-P2-MONCALLS.NPL:1904   INTEGER ARRAY BUFFR(7)   % BUFFER FOR MON RFILE; 7 FIRST WORDS ON PROG.FILE
RP-P2-MONCALLS.NPL:2332          ZAREG=:FILNR; 0=:BLCKNO; 7=:NWRD
RP-P2-MONCALLS.NPL:2333          "BUFFR"+B=:RWPAR(2)
RP-P2-MONCALLS.NPL:2334          "RWPAR"+B; *MON 117
RP-P2-MONCALLS.NPL:2340          T:=FILNR; X:="BUFFR"+B; CALL 2BDBRECOVER; GO ERET
```

The routine reads block 0 of the file via `MON 117` (RFILE) with
`NWRD = 7` and passes the 7-word buffer to `2BDBRECOVER`, which performs
the actual page-table population and bank loading.

| Word | Byte offset | Field                                         | Notes                                                       |
|------|-------------|-----------------------------------------------|-------------------------------------------------------------|
| 0    | `0x00`      | Start address                                 | PC after `@RECOVER`                                         |
| 1    | `0x02`      | Restart address                               | PC after `@CONTINUE`                                        |
| 2    | `0x04`      | Bank 1 first address (lower bound)            | Usually 0                                                   |
| 3    | `0x06`      | Bank 1 last address  (upper bound, inclusive) |                                                             |
| 4    | `0x08`      | Bank 2 first address                          | `0177777` if no real bank 2                                 |
| 5    | `0x0A`      | Bank 2 last address                           | `0` if no real bank 2                                       |
| 6    | `0x0C`      | Debug first address                           | `0` in every file looked at but one. Printed by BRF-LINKER as `Debug` first |
| 7    | `0x0E`      | Debug last address (inclusive)                | `0` if there is no debug part. Printed by BRF-LINKER as `Debug` last. Earlier (wrongly placed at word 6) called "data-bank-copy last address" |

All multi-byte fields are big-endian.

The number of words in a region is `(last - first + 1)`. Bank 1 is
**always** loaded starting at address `first` in normal page-table memory.
Bank 2, when present, is loaded starting at address `first` through the
**alternate page table** (the program is expected to call `MON ALTON`
early in its initialisation to make the alternate page table addressable).

### 2.1 The 7th word and `2BDBRECOVER`

(Corrected 2026-10-12, see 2.3: the word described here, `0x346c` in `xmsg-fido-l03.prog`, is the
**eighth** header word, byte offset `0x0E`; the word at `0x0C` is the debug first address.)
The 7th header word (byte offset `0x0C`) is the most interesting. The
loader routine that consumes the header is named `2BDBRECOVER` in source
("two-bank / data-bank recover"). Its body is **not present** in the NPL
sources in this repository - only the call site in
`RP-P2-MONCALLS.NPL:2340` is visible. The routine itself is referenced
through the SINTRAN symbol table as a 5-character truncated symbol:

```
SYMBOLS/L07/SYMBOL-1-LIST.SYMB.TXT:6192   2BDBR=013635
```

(SINTRAN's symbol table truncates symbol names to 5 characters; the full
name `2BDBRECOVER` is used in the source but only `2BDBR` survives in the
symbol list, pointing at octal address 013635.)

So we know the routine exists, where it lives in memory, and that it
takes the 7-word `BUFFR` as its parameter, but we cannot read its body
from the available sources to confirm exactly how it interprets word 6.

The interpretation given in the table above (word 6 = data-bank-copy
last address) is **INFERRED** from a single test file:

- Of four test files, only one (`xmsg-fido-l03.prog`) has a non-zero
  word 6, and that same file is the only one containing a duplicated
  data area at file offset `0x40000`.
- The non-zero value (`0x346c`, octal `032154`) gives a word count of
  `0x346d` words = `0x68DA` bytes, which fits comfortably inside the
  `0x7000`-byte tail region of that file with the remainder being
  zero sector padding.

A second known data-bank-copy file would let us promote this from
INFERRED to VERIFIED.

### 2.3 Header words 6 and 7 as the real BRF-LINKER reads them (checked 2026-10-12)

SINTRAN III on nd100x, BRF-LINKER C01, command `PROGRAM-INFORMATION name`. It prints
`Start, Restart` (words 0, 1), `Program` (words 2, 3), `Data` (words 4, 5, `177777B - 000000B` when
there is no bank 2) and **`Debug` (words 6, 7)**, each as first - last in octal.

- `xmsg-fido-l03.prog` (words `0000 346C` at `0x0C`): `Debug : 000000B - 032154B`. The same file
  with `346C` moved to `0x0C` and `0000` put at `0x0E`: `Debug : 032154B - 000000B`. So the last
  address is the word at byte `0x0E`, not `0x0C`.
- `COPY-PROGFILE FROM,TO,<include debug>,<include link>`: with debug `YES` the copy of
  `xmsg-fido-l03.prog` is the same file byte for byte (290816 bytes, header words kept); with debug `NO`
  it is 79872 bytes, the header words 6 and 7 are `0000 0000` and the part at `0x40000` is gone. The
  tool therefore sees that part as the debug part. Nothing in this run shows it is a copy of
  the data bank; `*DATA-BANK-COPY` (ND-60.066.04) may or may not write the same slot, which was not
  checked (NRL is not on the pack).
- A program made by BRF-LINKER itself: `DEBUG-MODE EXTENDED` while loading `HELLO.BRF` gives
  header words 6, 7 = `0000 0002`, a file of 264192 bytes (`0x40800`: one page at `0x40000`), and
  the first bytes at `0x40000` are `0000 013B 0000 0441 FFFF 0000 0000 0000`. `DEBUG-MODE ON` and
  `OFF` give `0000 0000` and a file of 4096 bytes.
- The monitor does not need the part, or the two words, to start a one-bank program: four copies
  of the `EXTENDED` program (words 6, 7 set to 0; the part at `0x40000` zeroed; the file cut off at
  `0x40000`; word 7 = `077777`) all started and printed `HELLO, WORLD`.

### 2.2 Why no second header at 0x20000

The community-circulated description claims that two-bank PROG files
have a **second 7-word header at file offset 0x20000** followed by the
bank-2 image at `0x20200`. The test file `xmsg-in-l03.prog`, which is
unambiguously a two-bank PROG (bank-2 first/last in the main header are
real values, and the bank-2 image data is present and the right size),
shows that **the bytes at file offset 0x20000 are the start of the
bank-2 image, not a header**:

- Reading those bytes as a header gives nonsensical addresses
  (`0o42516 0o42111 0o43015 ...`).
- The data length from `0x20000` to end of file matches
  `(B2 last - B2 first + 1)` words from the **main** header almost
  exactly (within sector padding).
- Loading bank 2 from `0x20000` with the size from the main header
  produces a self-consistent image.

There is therefore **only one header**, at file offset 0. The
"Header 2 at 0x20000" claim does not match real two-bank files in
this corpus and is most likely a misreading of the format. Bank 2,
when present, starts directly at file offset `0x20000` with no
intervening header words.

> **VERIFIED** from `xmsg-in-l03.prog`.

---

## 3. Region Details

### 3.1 Bank 1 (code bank)

- File offset: `0x00200` (= 1 SINTRAN block of 256 words = 512 bytes).
- Length: `((header[3] - header[2]) + 1)` words.
- Loaded at memory address `header[2]` in the normal page table.
- The end of the image is padded with zero words to the next region's
  start (or to the file's final page boundary if no further region).

### 3.2 Bank 2 (data bank, real two-bank programs)

- Present iff `header[4] != 0177777`.
- File offset: `0x20000` (= 256 SINTRAN blocks = 128 KiB = the maximum
  size of bank 1: 64 Kw header-less + the 256-word header rounded up to
  a 64 Kw boundary for alignment).
- Length: `((header[5] - header[4]) + 1)` words.
- Loaded at memory address `header[4]` in the **alternate** page table.
- The application is expected to call `MON ALTON` early in initialisation
  so that the alternate page table is mapped and addressable.
- There is **no Header 2** between bank 1 and bank 2; the bank-2 image
  starts directly at `0x20000`.

Because bank 2 is sector-aligned at `0x20000`, the bank 1 region in a
two-bank file may have a substantial zero hole between the end of the
bank-1 image and the start of bank 2. This hole is part of the file
and must be preserved when copying the file (in particular, FTP in
ASCII mode will mangle it).

> **VERIFIED** from `xmsg-in-l03.prog`.

### 3.3 Data-bank-copy area (the debug part, see 2.3)

- Present iff `header[7] != 0` (word 7, byte `0x0E`; corrected 2026-10-12).
- File offset: `0x40000` (= 512 SINTRAN blocks = 256 KiB = two full
  bank slots into the file).
- Length: `(header[7] + 1)` words (words 6 and 7 are the debug first and last address, so
  the length is `header[7] - header[6] + 1` when word 6 is not 0). The part is written in whole
  pages: bytes behind the stated length, up to the end of the last page, are **not** zero padding (section 4.4).
- Produced by the Nord Relocating Loader command `*DATA-BANK-COPY`,
  which is documented in
  `Reference-Manuals/ND-60.066.04 ND Relocating Loader.md`
  lines 1013-1027 as: "Duplicates the data area in the PROG segment
  above the code." Functionally it lets `@RECOVER` initialise the
  alternate (data) bank from a copy embedded in the same PROG file
  rather than re-reading a separate data-bank file.
- The header still marks the file as one-bank
  (`header[4] = 0177777`, `header[5] = 0`); the presence of the
  data-bank-copy region is signalled exclusively by `header[7]`.
- Like the bank-2 region, this region is sector-aligned, so a one-bank
  file with `*DATA-BANK-COPY` will have a large zero hole between the
  end of the bank-1 image and `0x40000`.

> **INFERRED** from `xmsg-fido-l03.prog`. Confirmation would require
> either a second data-bank-copy sample or the body of `2BDBRECOVER`.

### 3.4 End-of-file padding

The file is padded with zero words at the end up to a page boundary.
The exact rounding is not constant across the test corpus (some files
round to a 1024-byte boundary, some to a larger one), and it appears
to be whatever the dump operation happened to allocate rather than a
strict format requirement. Readers should rely on the header word
counts for region sizes, not on the file length.

---

## 4. Worked Examples

All four examples below are taken from the `xmsg` subsystem in
`(external test data)`. Header words are shown
big-endian; addresses are shown in octal as well as hex because
ND-100 documentation conventionally uses octal.

### 4.1 `xmsg-command-l03.prog` - simple one-bank PROG

File size: 90112 bytes (`0x16000`).

Header words:

| Word | Hex      | Octal      | Meaning                  |
|------|----------|------------|--------------------------|
| 0    | `0x0000` | 0          | Start address            |
| 1    | `0x0001` | 1          | Restart address          |
| 2    | `0x0000` | 0          | Bank 1 first             |
| 3    | `0xaabd` | 0125275    | Bank 1 last              |
| 4    | `0xffff` | 0177777    | Bank 2 first (none)      |
| 5    | `0x0000` | 0          | Bank 2 last  (none)      |
| 6, 7 | `0x0000` | 0          | No debug / data-bank-copy part |

Bank 1: `(0125275 - 0 + 1) = 0125276` words = 43710 words
= `0x1557c` bytes. Loaded at address 0 from file offset `0x200`.

### 4.2 `xmsg-hdlc-test-l.prog` - small one-bank PROG

File size: 13312 bytes (`0x3400`).

| Word | Hex      | Octal    | Meaning              |
|------|----------|----------|----------------------|
| 0    | `0x0000` | 0        | Start address        |
| 1    | `0x0001` | 1        | Restart address      |
| 2    | `0x0000` | 0        | Bank 1 first         |
| 3    | `0x18ae` | 014256   | Bank 1 last          |
| 4    | `0xffff` | 0177777  | Bank 2 first (none)  |
| 5    | `0x0000` | 0        | Bank 2 last  (none)  |
| 6, 7 | `0x0000` | 0        | No debug / data-bank-copy part |

Bank 1: `014257` words = 6319 words = `0x315e` bytes from file
offset `0x200` into address 0.

### 4.3 `xmsg-in-l03.prog` - real two-bank PROG

File size: 180372 bytes (`0x2c094`).

| Word | Hex      | Octal    | Meaning           |
|------|----------|----------|-------------------|
| 0    | `0x0000` | 0        | Start address     |
| 1    | `0x0001` | 1        | Restart address   |
| 2    | `0x0000` | 0        | Bank 1 first      |
| 3    | `0x7f62` | 0177542  | Bank 1 last       |
| 4    | `0x0000` | 0        | Bank 2 first      |
| 5    | `0x5f49` | 057511   | Bank 2 last       |
| 6, 7 | `0x0000` | 0        | No debug / data-bank-copy part |

Bank 1: `0177543` words = 32611 words from file offset `0x200`
into normal-page-table address 0.

Bank 2: `057512` words = 24394 words from file offset `0x20000`
into alternate-page-table address 0.

This file has a zero hole between the end of bank 1 (around
`0x10800`) and the start of bank 2 at `0x20000`.

### 4.4 `xmsg-fido-l03.prog` - one-bank PROG with `*DATA-BANK-COPY`

File size: 290816 bytes (`0x47000`).

| Word | Hex      | Octal    | Meaning                                   |
|------|----------|----------|-------------------------------------------|
| 0    | `0x8d0d` | 0106415  | Start address                             |
| 1    | `0x8d0d` | 0106415  | Restart address                           |
| 2    | `0x0000` | 0        | Bank 1 first                              |
| 3    | `0x9a52` | 0115122  | Bank 1 last                               |
| 4    | `0xffff` | 0177777  | Bank 2 first (none - one-bank header)     |
| 5    | `0x0000` | 0        | Bank 2 last  (none)                       |
| 6    | `0x0000` | 0        | Debug first address (earlier left out)    |
| 7    | `0x346c` | 032154   | Debug last address (earlier called data-bank-copy last address, at word 6) |

Bank 1: `0115123` words = 39507 words = `0x134a6` bytes from file
offset `0x200` into address 0. Execution begins at address `0106415`.

Data-bank-copy region: `(032154 + 1) = 032155` words = 13421 words
= `0x68da` bytes from file offset `0x40000`. The remainder of the
`0x7000`-byte tail region is **not** zero: in this file every 512-byte block of it holds non-zero bytes
(e.g. at `0x46c00`), and COPY-PROGFILE of BRF-LINKER C01 keeps all of it (section 2.3). The tool writes the
part in whole pages; what the bytes behind the stated length are, is not known.

The header still says one-bank (word 4 = `0177777`); the presence of
the data-bank-copy region is signalled only by the non-zero word 7.

---

## 5. Reading Algorithm

Pseudocode for a correct reader:

```
read 8 big-endian 16-bit words from file offset 0 -> header[0..7]

start    = header[0]
restart  = header[1]
b1_first = header[2]
b1_last  = header[3]
b2_first = header[4]
b2_last  = header[5]
dbc_first = header[6]
dbc_last = header[7]

# Bank 1 - always present
b1_words = (b1_last - b1_first) + 1
read b1_words 16-bit big-endian words from file offset 0x200
load into normal-page memory at address b1_first

# Bank 2 - real two-bank programs
if b2_first != 0o177777:
    b2_words = (b2_last - b2_first) + 1
    read b2_words 16-bit big-endian words from file offset 0x20000
    load into alternate-page memory at address b2_first

# Data-bank-copy - one-bank programs built with *DATA-BANK-COPY
if dbc_last != 0:
    dbc_words = dbc_last + 1
    read dbc_words 16-bit big-endian words from file offset 0x40000
    # destination is "above the code" in the segment, per ND-60.066.04
    # exact load address is not yet pinned down from the available sources

set PC = start
on @CONTINUE: set PC = restart
```

Note: a reader cannot in general derive the file's intended size from
the header alone, because of end-of-file padding. The header's word
counts are authoritative for region sizes; the file length is not.

---

## 6. Known Gaps

Items that this document does **not** establish from primary sources:

1. The exact memory load address of the data-bank-copy region. The
   loader manual says "above the code" but does not give a formula.
   Two plausible candidates are: immediately after `b1_last`, or at
   address 0 in the alternate page table. Distinguishing them requires
   either the body of `2BDBRECOVER` or a known-good runtime trace.
2. Whether the part at `0x40000` is a copy of the data bank at all: the real
   BRF-LINKER C01 names header words 6 and 7 `Debug` (section 2.3). That the last address is
   word 7, not word 6, is verified.
3. Whether two-bank PROG files can also carry the data-bank file name
   that the loader manual mentions for the (historical) "RECOVER reads
   the data bank from a separate file" mode. None of the test files
   show evidence of such a field, but a larger sample set might.
4. The exact end-of-file padding rule. Different test files round up
   to different boundaries.

---

## 7. Sources

- `PROG-FILE-FORMAT.md`
  (operational reference, lists what the manuals do and do not document)
- `../NPL-SOURCE/NPL/RP-P2-MONCALLS.NPL`
  lines 1900-2340 (the `BUFFR(7)` declaration, the `MON 117` call that
  reads 7 words from block 0, and the call to `2BDBRECOVER`)
- `../NPL-SOURCE/SYMBOLS/L07/SYMBOL-1-LIST.SYMB.TXT`
  line 6192 (`2BDBR=013635`, the truncated symbol pointing at the
  routine that consumes the header)
- `../../Reference-Manuals/ND-60.066.04 ND Relocating Loader.md`
  lines 511-523 (header field semantics) and 1009-1027 (two-bank and
  `*DATA-BANK-COPY` behaviour)
- Empirical analysis of the four test files in
  `(external test data)`:
  `xmsg-command-l03.prog`, `xmsg-hdlc-test-l.prog`,
  `xmsg-in-l03.prog`, `xmsg-fido-l03.prog`.

---

**Created:** 2026-04-09
**Status:** byte-level layout established for header, bank 1 and bank 2;
data-bank-copy region inferred from one sample and pending confirmation.
