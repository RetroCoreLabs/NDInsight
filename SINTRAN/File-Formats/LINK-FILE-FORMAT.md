# `:LINK` - the third file of the old ND-500(0) domain format

**Status: DECODED, 2026-08-17 (same day, third pass). The writer is carved: NLL's own
serializer in `LINKAGE-LOAD-H02.PSEG` (ND-500 code, routine at virtual `B001166C`), and the
record layout is verified against 10 of the 11 sample files - see section 4a. MON-DEBUG:PROG
is ruled out as a reader (section 5). Machine-readable layout: `link-format.json`.
The remaining opening: the L-era `SL202-FO-L27` variant's string/module regions.**

The old ND-500(0) domain format is three files per segment: `:PSEG` (program), `:DSEG` (data)
and `:LINK`. `DESCRIPTION-FILE-FORMAT.md` covers the index that names them, and the `:PSEG` /
`:DSEG` sizes are now fully accounted for by the DESC size rule. `:LINK` had never been looked
at before 2026-08-17.

**How to read this document.** Sections 1 to 4 are the first pass: what eleven real `:LINK`
files look like from the bytes alone, written before any code was carved. They are kept because
the observations are real and a parser has to cope with every one of them. **Section 4a is the
decoded layout** and it explains all of them - where an earlier section offers two readings or
a guess, 4a is the answer. Where something is still a guess it says so.

---

## 1. The corpus

Eleven non-empty `:LINK` files from the thirteen-floppy corpus described in
`DESCRIPTION-FILE-FORMAT.md` section 5a, spanning 1982 to 1989 across twelve unrelated
products. Sizes were taken from each image's own directory entry, and the files extracted with
`ndtool -x`.

## 2. The one strong finding: every `:LINK` is 32k + 1 bytes

| File | Bytes | (size - 1) / 32 |
|---|---|---|
| COBOL-500-H00 | 11361 | 355 |
| FORTRAN-500 (1982) | 12545 | 392 |
| LED-FORTRAN-A01 | 13057 | 408 |
| COBOL-85-K01 | 17089 | 534 |
| FORTRAN-500-K02 | 18561 | 580 |
| RG-SERVICE-D10 | 24353 | 761 |
| HYPHEN-TEST-L03 | 28737 | 898 |
| RG-START-SW-D10 | 30209 | 944 |
| OEM-STATU-A01 | 30337 | 948 |
| NOTIS-RG-SW-D10 | 43937 | 1373 |
| SL202-FO-L27 | 344641 | 10770 |

**Eleven of eleven divide exactly.** Sizes range over a factor of thirty and come from
unrelated release lines seven years apart, so this is not coincidence - by chance it would be
about one in 32^11.

The last byte is `0x00` in all eleven. Trailing zero runs are only 1 to 3 bytes long, so the
file is **not** padded out to a 32-byte boundary - the content genuinely ends there.

Two readings fit, and the evidence here does not separate them:

- **A.** The file is k records of 32 bytes followed by a single terminator byte.
- **B.** The file is a stream whose length the writer rounds to 32k, plus one byte.

**Settled in section 4a: it is reading A, with one correction.** The file is k cells of 32
bytes, and the extra byte is not a terminator - NLL stores a zero end-word and sets the file's
max byte pointer to 32k, and the directory byte count is max byte pointer + 1. The files that
seemed to contradict reading A (shapes b and c in section 4) use the same 32-byte cells - behind
a header page, or with string regions between them.

## 3. `:LINK` is optional and is often absent

Genuinely zero bytes in the image directory - not an extraction artifact:

- `LINKAGE-LOAD-H02:LINK` (0 bytes) - and this is the linker itself
- `LED-B03:LINK` (0 bytes)
- `SCRATCH-SEG-01:LINK` on most floppies (0 bytes)

One oddity: `SCRATCH-SEG-01:LINK` on the COBOL-500-H00 floppy is **1 byte containing `0xE5`**,
and on the 1982 FORTRAN floppy it is 1 byte with 0 pages allocated. `0xE5` is a common
unwritten-media filler byte, so the likeliest reading is an empty file that was never written
rather than a one-byte record. Not proven.

So a domain can ship with no `:LINK` at all. Whatever it holds is not required to run the
domain.

## 4. First pass: three shapes that looked like different formats

From the bytes alone, three clearly different shapes appear. Section 4a shows they are one
format seen in three eras:

**(a) A symbol table with fixed 32-byte records.** `FORTRAN-500.LINK` (1982) is the clean case:
all 392 records begin with `ff ff ff ff`, and each carries a 7-8 character upper-case symbol
name at byte +16 with what looks like a length byte at +4.

```
00000000: ffff ffff 0800 0214 0800 0132 0000 0000  ...........2....
00000010: 4d41 494e 4e41 4d45 0801 5734 0700 0204  MAINNAME..W4....
00000020: ffff ffff 0700 0214 0800 013c 0000 0000  ...........<....
00000030: 454f 4646 4c41 4708 0124 e008 0002 0408  EOFFLAG..$......
```

`MAINNAME` is 8 characters and its record's byte +4 is `08`; `EOFFLAG` is 7 and its byte +4 is
`07`. That correspondence holds for every record checked, which is why the length byte reading
is offered at all. The bytes after a 7-character name look as if the remaining fields sit one
byte earlier than after an 8-character name. They do not: section 4a shows the fields are all
BEFORE the name, at fixed offsets, and what follows the name inside its 16-byte area is
leftover heap content.

**(b) The same `ff ff ff ff` opening, but not at every 32-byte boundary.** Eight of the eleven
start with `ff ff ff ff`, yet only the 1982 file has that marker at every record start.
`COBOL-85-K01.LINK` has it once, at offset 0, followed by a long run of zeros.

**(c) A list of length-prefixed SINTRAN file specifications.** `SL202-FO-L27.LINK` has no
`ff ff ff ff` at all and begins immediately with source-file paths:

```
00000000: 292b 284d 494c 4c49 2d37 2d4e 5458 3a4a  )+(MILLI-7-NTX:J
00000010: 5553 5449 4659 2d4e 5458 294c 4441 542d  USTIFY-NTX)LDAT-
00000020: 4a55 2d4c 3031 3a50 4c4e 433b 3108 0000  JU-L01:PLNC;1...
```

`(MILLI-7-NTX:JUSTIFY-NTX)LDAT-JU-L01:PLNC;1` is exactly 43 characters, and the byte before it
is `0x2b` = 43. So this region is length-prefixed strings naming the **source files** the
domain was built from. It is also by far the most printable file in the set at 49%, against
25-31% for the others.

**Conclusion for this section, as corrected by 4a:** the 32-byte cell is the unit in every
file, but a parser must not assume every cell is a symbol record, that records start at offset
0, or that word 0 means the same thing in every era. Shape (b) is a 2048-byte header page in
front of the records; shape (c) is string/module regions between the cells.

## 4a. DECODED (2026-08-17): the loader-table dump, from NLL's own serializer

The shapes above are all one thing: **the `:LINK` file is NLL's in-memory loader table,
serialized at CLOSE-SEGMENT.** The writer is carved in `LINKAGE-LOAD-H02.PSEG` (ND-500 code,
disassembled with `nd500-dis`; the PSEG is committed at `../ND500/nll-re/`, and the 31,747-line
listing regenerates from it with the command in [../ND500/nll-re/README.md](../ND500/nll-re/README.md)):

- **Serializer `B001166C`** (called from the CLOSE-SEGMENT worker `B00068CC` via the
  per-segment close loop): walks the loader-table hash buckets (chain word at entry +0,
  bucket per segment), and repeatedly picks the not-yet-dumped entry with the **smallest
  value word at +8** - a selection sort, which is the manual's "labels saved in numerically
  sorted order". Each picked entry is marked (set bit 4 of word +4, `B0011763`) and **exactly
  32 bytes are copied to the output cursor** (`by bmove @b.0x44,r2.(0x0),$0x20` at
  `B0011769`); then the record's word +0 is overwritten with the address of the NEXT record
  (`B0011771`-`B0011776`), and after the last record one zero word is stored (`B0011783`).
  The routine returns cursor & 0x7FFFFFF = 32*k.
- **The `32k + 1` law is the SMAX convention.** The caller (`B0006D6D` and twins) passes that
  32*k to the SMAX wrapper (`B001CC5F`, MON 73B). Per the OPENF carve
  (`../ND500/nd-500-mon/CARVE-ANSWER-FOUR-OPEN-QUESTIONS-2026-08-17.md` Q4), SMAX stores its
  argument directly as the max byte pointer and the directory byte count = max byte pointer
  + 1 - hence **every file is exactly 32k+1 bytes**, and the final `0x00` is the first byte
  of the zero end-word, not a counted terminator. Open question 1 is closed.

**Record layout - one 32-byte cell per label** (the manual's loader-table symbol entry;
field names from `desc-format.json` symbolEntry):

| Off | Size | Field | Meaning |
|---|---|---|---|
| +0 | 4 | link | Era-dependent (see below); in K-era+ files it is `0x18000000 + byte position of the NEXT record` - the record's address in NLL's D-space segment 3, so `value & 0x7FFFFFF` = file position. 8 of 11 samples show exactly `0x18000820` in the record at offset 0x800. |
| +4 | 1 | sl | Symbol name length. Matches the name at +16 in every record of every conforming sample. |
| +5 | 1 | nleOper | NLE / operator bits (0 in all sampled label records). |
| +6 | 1 | ident | Language/ident code (2 in all sampled label records). |
| +7 | 1 | cw | Flag byte, SAME bit layout as `desc-format.json` cwBits: bit 0 UDEF, bit 2 DSYM, bit 4 DMPF, bit 5 GLOB. Observed 0x10/0x14/0x16. The serializer's filters test bits 0/4/5 of this byte (`B001170A`-`B0011731`). |
| +8 | 4 | val | Symbol value (ND-500 address). **Strictly ascending across records in 10/10 conforming samples** (e.g. 883/883 pairs) - the sort key. |
| +12 | 4 | size | Common-block size; 0 for plain labels. |
| +16 | 16 | name | Symbol name, `sl` bytes, rest is heap slack. Longer names span cells (manual says 20-char truncation), and non-symbol loader-table node types (trap names etc.) occupy cells too - that is what the "tail" cells hold. |

**File-level layout by era:**

- **1982 (`FORTRAN-500.LINK`, J-era):** records from offset 0, link word = `0xFFFFFFFF`
  constant.
- **~1985 (`COBOL-500-H00`):** records from offset 0, link word = the old in-memory packed
  elink values (26, 53, ... - not file positions).
- **K/D/L product era (8 of 11 samples):** one **2048-byte header page** - all zero except
  word 0 = `0xFFFFFFFF` - then records from offset 2048 with the `0x18000000 | next-pos`
  link law. This is also why COBOL-85-K01 "has the marker once then a long zero run": that
  IS the header page. The 2048 quantum is the serializer's page rounding
  (`(cursor + 0x7FF) & ~0x7FF`, `B00116D7`-`B00116EB`).
- **`SL202-FO-L27` (L-era NLL):** same container, but with large length-prefixed
  string/module regions (auto-load file specifications) interleaved before/around the symbol
  cells; 1332 cells parse as symbol records. Interior NOT yet decoded - needs the L-series
  NLL binary.

Verified 2026-08-17 by parsing all 11 samples under this layout (script preserved in the
carve session): 10/11 fully conform (355/355, 470/470, 516/516, 884/884, 344/344, 834/834,
697/697, 1309/1309, 880/880, 392/392 records with 100% ascending values), SL202 partially.

## 5. What it is for, and who reads it

The old format needs somewhere to keep what NLL requires in order to **relink** a domain, and
what a symbolic debugger requires in order to show names. Global symbol names with addresses
(shape a) and a list of the source files that went into the build (shape c) both fit that
description. `LED-B03` is the symbolic debugger and ships with a **zero-byte** `:LINK`, which
does not contradict it - the debugger reads other domains' link information, it does not need
its own.

**What is and is not proven here.** The WRITER is carved (section 4a). The purpose above rests
on the manual's wording quoted below, not on carved code. **No code has been carved for a
`:LINK` READER** - the readers are only identified (2026-08-17, Ghidra session):

- **`MON-DEBUG:PROG` (nd-500-mon-j04) does NOT read `:LINK` - ruled out, byte-verified.**
  Its file-type table (bank 2 byte 0x996E) holds only `PSEG DSEG DATA PROG`, and the string
  `LINK` appears nowhere in the image as a file type. Every `LINK` string in the binary
  belongs to something else: `$END OF LINK$` / `$ERROR IN LINK$` are the debugger's
  FOLLOW-LINK memory-chain walker (command table with NEXT/EXIT beside them), and
  `LINK KEY INCORRECT` / `LINK SEGMENT:` are the linked-segment machinery. The J04 monitor
  also contains none of the loader commands (no OPEN-SEGMENT/CLOSE-SEGMENT/LOAD-SEGMENT
  strings) - it is the debug monitor only.
- **The reader and writer is NLL itself - ND-500 code.** NLL is the separate ND-500 domain
  `LINKAGE-LOAD-H02` (`:PSEG` 123,989 bytes of ND-500 instructions, `:DSEG` 2,184,977
  bytes). Its DSEG carries the full loader command table (OPEN-SEGMENT, CLOSE-SEGMENT,
  LINK-SEGMENT, LIBRARY-SEGMENT-LINK, FORCE-SEGMENT-LINK, GLOBAL-ENTRIES, ...) and a
  file-type table `NRF'BRF'LINK'SYMB'DATA'RTFIL'` containing the `LINK` type. Both files
  are extracted from the 210319H02 floppy image `ND-disk-00042.img` (one of the downloaded
  ND floppy images, outside this repository) and staged in `SINTRAN/ND500/nll-re/` for the
  carve.
- The symbolic debugger (`(SYSTEM)DEBUGGER`, invoked by name from the monitor) is the other
  known consumer, also an ND-500 domain.

**The carve happened the same day** - there is no ND-500 processor in Ghidra, but the
`nd500-dis` WSL binary handles raw PSEGs and runs fine from Windows. The result is section
4a, read off a 31,747-line listing that regenerates from the committed PSEG - see
[../ND500/nll-re/README.md](../ND500/nll-re/README.md).

**What the Loader Monitor manual (ND-60.136) adds:**
CLOSE-SEGMENT writes "all labels ... on the :LINK file in numerically sorted order"; symbols
are truncated to 20 characters; the file "is not opened when the program is executed but is
used during the loading process and by the symbolic debugger". NLL's command set
(SET-AUTO-LINK-SEGMENT, SET-AUTO-LOAD-FILE with a Language argument, "module index-table")
offers a candidate reading for shape (c): length-prefixed source/auto-load file
specifications recorded alongside the symbol table. UNVERIFIED - noted as a lead, not a
finding.

## 6. Open questions

1. ~~What produces the `32k + 1` length?~~ **CLOSED (section 4a):** NLL writes k 32-byte
   cells, stores a zero end-word, and calls SMAX(32k); the byte count = max byte pointer + 1
   gives 32k+1, and the trailing `0x00` is the first byte of the zero end-word.
2. ~~What is the actual record layout of shape (a)?~~ **CLOSED (section 4a):** the fields do
   NOT shift - the "shifting" bytes past the name are heap slack inside the fixed 16-byte
   name area.
3. Is shape (c) a separate region of the same format, or a different format entirely that
   shares the file type? **PARTLY answered:** same container (the loader-table dump); the
   string regions are loader-table string/module nodes (auto-load file specs). Their node
   layout is still undecoded - needs the L-era NLL binary.
4. Why do `LINKAGE-LOAD-H02` and `LED-B03` ship with no `:LINK` when every compiler on the
   corpus has one?
5. Is `0xE5` in a 1-byte `:LINK` meaningful, or unwritten media?

## 7. The files themselves

All eleven `:LINK` files described here are kept in [samples/](samples/README.md), beside the
DESC file from the same floppy, so nothing above has to be taken on trust. That directory's
README carries the provenance table and the segment sizes.

If you want to re-extract from the images instead: `ndtool -x -F 'FLOPPY-USER/*' -o <outdir>
<image>`, and take file sizes from `ndtool -t <image>` rather than from the extracted copies -
a file with a non-zero byte count but zero allocated pages extracts as empty, which will
otherwise look like a format anomaly.

---

**Related:** [DESCRIPTION-FILE-FORMAT.md](DESCRIPTION-FILE-FORMAT.md) (the index naming these
files), [DOM-FILE-FORMAT.md](DOM-FILE-FORMAT.md) (the newer self-contained format that replaced
the `:PSEG`/`:DSEG`/`:LINK` trio).
