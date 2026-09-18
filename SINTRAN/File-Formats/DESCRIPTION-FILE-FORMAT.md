# DESCRIPTION-FILE:DESC Format (Old ND-500(0) Domain Format Index)

**`DESCRIPTION-FILE:DESC`** is a per-SINTRAN-user index file used by the **old** ND-500
domain format. In that format a domain's content is split across `NAME:PSEG` (program
code), `NAME:DSEG` (data), and `NAME:LINK` (symbol/link info), none of which know about
each other. `DESCRIPTION-FILE:DESC` is what lets the old Linkage-Loader (NLL), the
**ND-500 Monitor**, and the `CONVERT-DOMAIN` migration program resolve a bare domain
**name** to its actual files and bookkeeping (sizes, load addresses, segment numbers). See
[DOM-FILE-FORMAT.md](DOM-FILE-FORMAT.md) for the newer, self-contained format this was
replaced by (and [NRF-FILE-FORMAT.md](NRF-FILE-FORMAT.md) for the object format the
Linker/NLL builds domains *from*, which is a separate concern from `:DESC`).

**Primary sources, in order of authority:**

1. **The ND-500 Monitor's own code** - `MON-DEBUG:PROG` (ND-500/5000 Loader/Debug Monitor
   J04), carved 2026-08-11. It reads this file and prints every segment-entry field with
   the field's own name beside it, which pins each offset. Full carve:
   [`../ND500/nd-500-mon/CARVE-ANSWER-DESC-FIELD-OFFSETS-2026-08-11.md`](../ND500/nd-500-mon/CARVE-ANSWER-DESC-FIELD-OFFSETS-2026-08-11.md).
2. Real files on disk - six segment entries from three independently produced product
   installs (NLL H02, LED B03, COBOL-85 K01) worked through in detail in section 5, then the
   whole 13-floppy corpus in [samples/](samples/README.md) (section 5a).
3. `ND-60.136.04A ND-500 Loader Monitor.md` (`Reference-Manuals/`), chapter 11
   "DESCRIPTION FILE LAYOUT" - which states plainly that it "does not pretend to give a
   complete description": it gives field *names, sizes and order*, never byte offsets.

**Status 2026-08-11:** the layout below is **resolved**. The fields this document previously
marked UNABLE TO DETERMINE (`PLB`, `PSIZE`, `DLB`, `DSIZE`, `DEBUGINFO`) are confirmed from
the monitor's code AND match the real files exactly.

**Status 2026-08-17:** the domain entry (section 3) is code-proven as well, the bytes 74-84
conflict is settled in the manual's favour (section 4), and the one anomaly that used to be
open was a transcription error (section 6). What is still open: the `MINPAGES`/`MAXPAGES`
offsets and the inner layout of an `ADDSGELEM` element (both manual only), the meaning of the
five fields that read zero in every sample (section 4 note), a chain of more than one segment
(section 5a), and a write-side proof of the size-minus-one rule (section 5a).

---

## 1. Overall structure

Four areas: **process entries, domain entries, segment entries, symbol entries**.

The file is organised in **2048-byte pages**. Each domain-entry page is a **256-byte
header/bitmap followed by 32 domain entries of 56 bytes** (256 + 32x56 = 2048 exactly).
The ND-500 Monitor computes the position of domain entry *index* as

```
position = 56*index + 256*(index div 32 + 1)
```

so the first domain entry starts at byte **256**. This is the monitor's own arithmetic
(`013454B` READ-DOMAIN-ENTRY), and it is confirmed against both real files: entries land on
`0x100` and `0x138`, exactly where the domain names are. It also explains the old puzzle
that the manual's domain-entry field list sums to 54 while entries are spaced 56 apart -
the entry is 56 bytes because 32 of them plus a 256-byte header fill a 2048-byte page.

**Segment entries are a singly linked list, not an array.** Word 0 of a domain entry holds
the **file byte position** of that domain's first segment entry; word 0 of a segment entry
holds the position of the next one, and **0 ends the chain**. Verified in both real files:
domain `SCRATCH-DOMAIN` -> `0x4000`, domain `LINKAGE-LOAD-H02` (resp. `LED-B03`) ->
`0x40C0`, each segment entry's link then 0.

The monitor walks domain indexes 0..253 (limit `000376B` at `016504B`).

## 2. Process Entry - 1 byte

| Field | Size | Meaning |
|---|---|---|
| (unnamed) | 1 | Domain number of the first domain belonging to this process. |

## 3. Domain Entry - 56 bytes

All offsets are now code-proven from the monitor's own print routine (`014035B`-`014520B` in
`nd-500-mon-j04.prog`), each label print paired with the single field load that follows it,
same method as the segment entry. "Word" gives the ND-100 word offset off the domain-entry
buffer `037651B`. Full evidence:
`../ND500/nd-500-mon/CARVE-ANSWER-FOUR-OPEN-QUESTIONS-2026-08-17.md`.

| Byte | Word | Field | Size | Meaning | Verified |
|---|---|---|---|---|---|
| 0 | `0` | SEGLINK | 4 | **File byte position of the first segment entry** of this domain. | **YES** - code (`014325B LDD ,X 0`, label `$Segptr:`) + files |
| 4 | `2` | DNAME | 16 | Domain name, `0x27` (apostrophe) terminator then zero padding. | **YES** - byte-exact; print loop `014061B`-`014121B` runs exactly 16 iterations off word 2 |
| 20 | `12B` | CHILDDOMAINS | 6 | Byte array of child-domain indexes; element count is byte 27. Max 6 fit before byte 26. | **YES** - `014407B AAT 12` + LBYT loop, label `$Child domains   : ` |
| 26 | `15B` hi | MOTHER | 1 | Domain index of mother domain; `0xFF` = none (all root domains in all 13 samples). | **YES** - `014157B LDA ,X 15` + `SHR 8`, label `$Owner:` |
| 27 | `15B` lo | CHILDINDEX | 1 | Number of child domains - the monitor prints it as `Childindex:` AND uses it as the CHILDDOMAINS element count. | **YES** - `014176B LDA ,X 15` + `SHL 8` + `SHR 8` |
| 28 | `16B` | FLAG + PRIOR | 2 | One 16-bit word, not two bytes: bit 15 `alton`, bit 14 `dinuse` (set on every in-use entry in all samples), bit 13 `occup`; bits 5-12 = priority (`  Prior:`). Bits 0-4 unprinted, zero in all samples. | **YES** - bit tests `014441B`/`014472B`/`014505B`, prior extract `014216B` `(w<<3)>>8` |
| 30 | `17B` | STADR | 4 | Start address (0 for SCRATCH-DOMAIN, segment-1 addresses like `0x8000004` for real programs). | **YES** - `014132B LDD ,X 17`, label `  Start address:` |
| 34 | `21B` | ENABLEINT | 4 | Bitmask of enabled traps. | **YES** - `014261B LDD ,X 21`, label `$Enableint:` |
| 38 | `23B` | THA | 4 | Trap handler address. | **YES** - `014277B LDD ,X 23`, label `  THA:` |
| 42 | `25B` | SYSENABL | 4 | Bitmask of system-enabled traps. | **YES** - `014312B LDD ,X 25`, label `  Sysenable:` |
| 46 | `27B` | (unprinted) | 2 | Not printed by the monitor; zero in all 13 samples. The manual's field order has no room for it, which is where its 54-vs-56-byte sum went. | code (absence) |
| 48 | `30B` | PBITMAP | 4 | Monitor label `  PSEG use:`. Value 2 in all samples = bitmap with bit 1 set, matching STADR in segment 1 - so the bitmap reading fits. **NOTE: manual order put this at byte 46; real offset is 48.** | **YES** - `014340B LDD ,X 30` |
| 52 | `32B` | DBITMAP | 4 | Monitor label `  DSEG use:`. Same bitmap shape. **Manual order put this at 50; real offset is 52.** | **YES** - `014353B LDD ,X 32` |

The `0x27` terminator is not in the manual. It was missed on the first pass because the only
name checked then, `LINKAGE-LOAD-H02`, is exactly 16 characters and leaves no room for it;
`SCRATCH-DOMAIN` (14 chars) stores `...44 4f 4d 41 49 4e 27 00`.

Checked against all 13 real DESC files in `samples/` (2026-08-17): every used entry parses
cleanly under this layout; MOTHER is `0xFF` and CHILDINDEX 0 everywhere (no sample has a
domain tree), `dinuse` is set on every used entry and no unused one. The child machinery is
code-proven but sample-unexercised.

## 4. Segment Entry - 192 bytes

All multi-byte values are **big-endian**. "Word" columns give the ND-100 word offset used by
the monitor's own code (byte offset / 2).

| Byte | Word | Field | Size | Meaning | Verified |
|---|---|---|---|---|---|
| 0 | `0` | SEGLINK | 4 | **File byte position of the next segment entry; 0 = end of chain.** | **YES** - code + both files |
| 4 | `2` | SNAME | 54 | `(directory:user)filename`, `0x27` terminator then zero padding. | **YES** - byte-exact |
| 58 | `35B` | SEGTYPE | 4 | Flags indicating segment type. | manual only |
| 60 | `36B` | (flags) | 2 | A flags word the monitor prints bit by bit (`015743B`-`016052B`). | code |
| 62 | `37B` | COMSEGNO | 2 | Number of shared (common) SINTRAN-III segments; bounds the four arrays below, max 5. Monitor's own label `$Comsegno: ` at `015150B`. | **YES** - adjudicated 2026-08-17, see note |
| 64 | `40B` | COMSEGADDR | 10 | Array of **5 x uint16** (one word per common segment, not 10 loose bytes): logical address of each shared segment. Label `$Comsegaddr: `. | **YES** - `015233B AAX 40`, word loop `015220B`-`015245B` |
| 74 | `45B` | COMSEGSIZE | 5 | Byte array [5]: size of each shared segment. Label `$Comsegsize: `. | **YES** - `015270B AAT 45` + LBYT loop |
| 79 | - | (pad) | 1 | Between the two byte arrays; the monitor never touches it. | code (absence) |
| 80 | `50B` | N100SEGNO | 5 | Byte array [5]: actual SINTRAN-III segment numbers. Label `$N100segno:  `. **Manual order suggested 79; real offset is 80 (word-aligned).** | **YES** - `015324B AAT 50` + LBYT loop |
| 85 | - | (pad) | 1 | Low byte of word `52B`, unprinted. | code (absence) |
| 130 | `101B` | INDPLOG/INDDLOG | 2 | Bitfield word: `  Indplog: ` = bits 10-15 (`015164B` `w>>10`), `  Inddlog:  ` = bits 5-9 (`015200B` `(w<<6)>>11`). | **YES** - code |
| 132 | `102B` | ADDSGELEM | 60 | **5 elements x 12 bytes** (multiply constant 6 words at `015553B`), count = COMSEGNO; the monitor prints the first double of each element, label `$Addsgelem:  `. Fills the entry to exactly 192 bytes. Manual's per-element split (ADDSEGLINK/INDDOMAIN/ADDTYPE.../LINKDATE) not yet paired. | offsets **YES**, inner layout manual only |
| **88** | **`54B`** | **PLB** | 4 | Logical low bound for program segment. | **YES** - `014575B LDD ,X 54`, label `$PLB:` |
| **92** | **`56B`** | **PSIZE** | 4 | Program segment size, stored as **size - 1**. | **YES** - `014610B LDD ,X 56`, label `Psize:` |
| **96** | **`60B`** | **DLB** | 4 | Logical low bound for data segment. | **YES** - `014636B LDD ,X 60`, label `$DLB:` |
| **100** | **`62B`** | **DSIZE** | 4 | Data segment size, stored as **size - 1**. | **YES** - `014651B LDD ,X 62`, label `Dsize:` |
| **104** | **`64B`** | **DEBUGINFO** | 4 | Size of debug info. | **YES** - `014677B LDD ,X 64`, label `$Debuginfo:` |
| **108** | **`66B`** | **DLINKDATE** | 4 | Labelled `Dlinkdate:` by the monitor. **The offset is proven; the meaning is not** - see the note below. | **YES** - `014712B LDD ,X 66` |
| **112** | **`70B`** | **ABSFIXAD** | 2 | Absolute fixed address, if fixed. | **YES** - `014750B LDA ,X 70` |
| **114** | **`71B`** | **LOWLOGFIX** | 2 | Lower page number in fixed area. | **YES** - `014763B LDA ,X 71` |
| **126** | **`77B`** | **PLOLOGFIX** | 2 | (monitor's own label `Plologfix:`) | **YES** - `014623B LDA ,X 77` |
| **128** | **`100B`** | **PUPLOGFIX** | 2 | (monitor's own label `Puplogfix:`) | **YES** - `014664B LDA ,X 100` |
| ? | - | MINPAGES, MAXPAGES | - | Manual's remaining fields (probably in bytes 116-125 between LOWLOGFIX and PLOLOGFIX); the monitor does not print them, so their offsets are still manual-order only. INDIPLOG/INDDLOG and the ADDSEG block are now pinned at 130 and 132 above. | manual only |

**The bytes 74-84 conflict is ADJUDICATED (2026-08-17): the manual was right.** The earlier
"two counted byte strings" reading was a misreading of the loop idiom. Word `37B` is not a
character count - the monitor prints it under its own label `$Comsegno: `, and the same count
bounds a WORD array at byte 64 (`$Comsegaddr: `) and a DOUBLE array at byte 132
(`$Addsgelem:  `), which no string reading can explain. The two `LBYT` loops print array
ELEMENTS as numbers through `013301B`, a wrapper around the resident library number converter
at `172340B` - the same routine that prints the domain child-domain list - not through the
string printer `013177B`. All 13 sample files have COMSEGNO = 0 (floppy installs carry no
common segments), consistent either way; the code is what decides it.

Field values in the six real entries (see section 5) confirm the size fields independently
of the code, so this table is supported from two directions.

**DLINKDATE at +108 is zero in every real entry, including linked ones (2026-08-17).** All
**26** segment entries across the 13-floppy corpus in section 5a read `00 00 00 00` there,
spanning 1982 to 1989 and twelve unrelated products. DEBUGINFO at +104 does vary over the same
entries (0, 4, 157323, 201075, 311129), so this is not a case of the whole region being
unused. If +108 held a link date it should be non-zero for shipped, linked products such as
LINKAGE-LOAD-H02, LED-B03 and COBOL-85-K01. So one of these is true and the evidence does not
separate them: the field is a date but NLL never writes it in a shipped domain; or the field
is something else that the monitor merely labels `Dlinkdate:`. **What is proven is the offset
the monitor loads, not what the value means.** Treat the name as the monitor's label, not as a
decoded meaning. The same caution applies to ABSFIXAD, LOWLOGFIX, PLOLOGFIX and PUPLOGFIX,
which are zero in all 26 entries - their offsets are proven, their behaviour is untested
because no available sample exercises them.

## 5. The real segment entries

Extended 2026-08-17. A sweep of the ND archive turned up four DESC files rather than two,
covering **three independently produced product installs** - the NLL H02 floppy, the LED B03
floppy, and a COBOL-85 K01 floppy that had not been looked at before. In every case the
matching `.pseg` and `.dseg` files sit in the same directory, so the derived size can be
checked against the real file size rather than against another document.

| Segment | Install | `.pseg` | PSIZE stored | `.dseg` | DSIZE stored | DLB | DEBUGINFO |
|---|---|---|---|---|---|---|---|
| SCRATCH-SEG-01 | H02 floppy | 5 | 4 | 1029 | 1028 | 0 | 0 |
| LINKAGE-LOAD-H02 | H02 floppy | 123989 | 123988 | 2184977 | 2109142 | 75834 | 157323 |
| SCRATCH-SEG-01 | LED floppy | 5 | 4 | 1029 | 1028 | 0 | 0 |
| LED-B03 | LED floppy | 223695 | 223694 | 394525 | 394524 | 0 | 201075 |
| SCRATCH-SEG-01 | COBOL K01 floppy | 5 | 4 | 1029 | 1028 | 0 | 0 |
| COBOL-85-K01 | COBOL K01 floppy | 265213 | 265212 | 129253 | 129252 | 0 | 4 |

Eight exact matches of `PLB + PSIZE + 1 = .pseg` and `DLB + DSIZE + 1 = .dseg`, with no
exceptions. The COBOL entry matters most: those offsets were derived from the monitor's code
and checked against the H02 and LED floppies, so COBOL is a file the conclusion was not fitted
to. It agrees anyway.

Produced by `nd500-dump` (pcc-nd500) reading each DESC file through the domain-entry position
formula and the segment chain, with the `.pseg`/`.dseg` sizes taken from the filesystem.

**Correction 2026-08-11:** the LINKAGE-LOAD-H02 DSIZE-stored value above was previously
transcribed as 2,109,654 (an error, off by exactly 512). The real stored value, re-read
byte-for-byte from `description-file.desc` offset `0x4120` (`LINKAGE-LOAD-H02` segment
entry at `0x40C0` + byte 96 = DLB, +100 = DSIZE): raw bytes `00 01 28 3a 00 20 2e d6 00 02
66 8b` = DLB `0x0001283a` (75834), DSIZE-stored `0x00202ed6` (**2,109,142**), DEBUGINFO
`0x0002668b` (157323). This also resolves section 6 below - it was not a format anomaly,
it was this transcription error.

### 5a. Corpus check across 13 vendor floppies (2026-08-17)

The three installs above were extended to a proper corpus: thirteen SINTRAN floppy images, each
holding its own `DESCRIPTION-FILE:DESC` together with the `:PSEG` and `:DSEG` files that DESC
describes. The derived sizes were compared against the sizes in each image's own directory
entry - not against extracted copies, for the reason given below.

**Result: 48 size checks, 48 matches, 0 mismatches, across 24 distinct segment entries.**

| Image | Product | Directory |
|---|---|---|
| ND-disk-00458 | FORTRAN-500 (1982, oldest in the set) | ND-10190D-PART1 |
| 8_nd_f0b_10177h00-1s_fe | COBOL-500-H00 | 10177H00-1S |
| ND-disk-00096 | LED-FORTRAN-A01 | 211159A01-XX-01D |
| ND-disk-00093 | FORTRAN-500-K02 | 210190K02-XX-01D |
| ND-disk-00042 | LINKAGE-LOAD-H02 | 210319H02 |
| ND-disk-00172 | HYPHEN-TEST-L03 | 210814L05-XX-01D |
| ND-disk-00177 | SL202-FO-L27 | 210874L05-XX-02D |
| ND-disk-00022 | OEM-STATU-A01 | 211078A01-EN-02D |
| ND-disk-00092 | COBOL-85-K01 | 210177K01-XX-01D |
| ND-disk-00095 | LED-B03 | 211160B03-XX-01D |
| ND-disk-00215 | RG-SERVICE-D10 | 211066D10-SW-02D |
| ND-disk-00216 | NOTIS-RG-SW-D10 | 210528D10-SW-01D |
| ND-disk-00217 | RG-START-SW-D10 | 210528D10-SW-02D |

Twelve distinct products over seven years, from unrelated release lines - compilers, editors,
a linker, NOTIS applications - all obeying the same rule. The layout is identical in every one:
DESC is 22528 bytes, domain entries land at bytes 256 and 312, and the chains run to `0x4000`
and `0x40C0`.

**A trap worth recording.** The first run of this check reported one mismatch, on the 1982
floppy: DESC said `SCRATCH-SEG-01`'s `.dseg` was 5 bytes, and the extracted file was 0 bytes.
The DESC was right. That file is 5 bytes with **0 pages allocated** in the image's own
directory entry, and `ndtool -x` writes such a file out as empty. Checking against extracted
copies would have manufactured a format anomaly out of an extraction artifact. Read sizes from
the directory entry.

**What this corpus does not test.** Every floppy holds exactly two domains and every segment
chain is one entry long, so the linked-list walk is confirmed to start and terminate correctly
but has never been exercised on a chain of length two or more. A multi-segment domain is still
wanted.

Eight exact `size - 1` matches in the detailed table above, 48 across the corpus.
**This is why every earlier byte-value search failed**: the
file never contains the size, it contains the last byte index.

The monitor itself does not adjust these on the way out - it prints the stored value raw, so
it is not a write-side proof of the `-1`. But its reader uses the same inclusive-last-index
convention twice (`277B` = 191 for the 192-byte segment record, `67B` = 55 for the 56-byte
domain entry), so `stored = last index` is this code's house style. The writer is NLL, which
is where a write-side proof would have to come from.

**CONVERT-DOMAIN is not a witness for these fields.** Patching PSIZE from 123988 to 16384 in
a real DESC and re-running `CONVERT-DOM-A03` under nd500x produced a byte-identical
2,316,049-byte `.DOM`. It queries the filesystem (MON 62B GetBytesInFile) instead of reading
the entry. Any future investigation should not spend time there.

## 6. Resolved: LINKAGE-LOAD-H02's data segment (was marked an open anomaly)

**Status 2026-08-11: closed.** This was reported as an anomaly - DSIZE not matching the
`.dseg` file size - based on a DSIZE-stored value (2,109,654) that turned out to be a
transcription error in section 5's table, not a byte re-read from the file. The real
stored value, verified directly against `description-file.desc` offset `0x4124` (DSIZE; DLB
is the four bytes before it at `0x4120`), is **2,109,142** (raw bytes `00 20 2e d6`).

With the correct value, `DLB + (DSIZE_stored + 1) = .dseg file size` holds exactly:
`75834 + 2,109,143 = 2,184,977`, matching `linkage-load-h02.dseg` byte for byte. The same
formula holds trivially for the three zero-DLB entries (`0 + real_size = file size`). DLB
is simply the logical low bound the data segment is placed at; DSIZE is its length from
there - there is no unexplained gap and nothing left for NLL or the segment placer to
account for.

## 7. How the file is read (ND-500 Monitor, carved)

Not `RFILE`. The monitor opens the file by building `DESCRIPTION-FILE` + `.DESC` as PLANC
descriptors (`016200B`-`016240B`), then:

- **`013454B` READ-DOMAIN-ENTRY(index)** - computes the position with the formula in section
  1 and reads 56 bytes into the buffer at `037651B`.
- **`013527B` READ-SEGMENT-ENTRY(byte position)** - reads 192 bytes into the buffer at
  `037705B`.
- Both call **`013406B`**, which issues **MON 74 SETBT** (seek to the byte position) and then
  a **MON 1 INBT** byte loop, storing with `SBYT`.

The buffer therefore holds the raw file record byte for byte, which is what makes the
word-offset to file-byte-offset mapping exact.

## 8. Symbol Entry - variable size

| Field | Size | Meaning |
|---|---|---|
| ELINK | 4 | Link to next symbol. |
| SL | 1 | Length of symbol name. |
| NLE | 3 bits | Numeric length. |
| OPER | (packed with NLE?) | Operation type (+, -, *, /) upon this symbol. |
| IDENT | 1 | Language code. |
| CW | 1 | Type-of-symbol bitmask, see below. |
| VAL | 4 | Value of symbol. |
| SIZE | 4 | Size of common block. |
| SS | up to 255 | Symbol name. |

### CW bits

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

(Same bit layout as the NRF loader's in-memory symbol table - see
[NRF-FILE-FORMAT.md](NRF-FILE-FORMAT.md) section 4 - these two are almost certainly the
same table, one in memory and one persisted.)

## 9. The real examples used throughout

**NLL H02 installer floppy** (`210319H02-XX-01D`), domains `LINKAGE-LOAD-H02` and
`SCRATCH-DOMAIN`:

| File | Size | Role |
|---|---|---|
| `description-file.desc` | 22528 | worked example |
| `linkage-load-h02.pseg` | 123989 | program segment |
| `linkage-load-h02.dseg` | 2184977 | data segment |
| `linkage-load-h02.link` | 0 | empty. Why the linker ships without one is an open question - see `LINK-FILE-FORMAT.md` section 6, question 4. (This row used to say "no unresolved externals"; that was a guess, and `:LINK` holds the label table, not unresolved externals.) |

**LED floppy** (`211160B03-XX-01D`), domains `LED-B03` and `SCRATCH-DOMAIN`: same
22528-byte DESC geometry, `led-b03.pseg` 223695, `led-b03.dseg` 394525, `led-b03.link` 0,
`scratch-seg-01.pseg` 5, `scratch-seg-01.dseg` 1029. Cross-referenced in
`../../Developer/Workflow/CONVERT-DOMAIN-PSEG-DSEG-TO-DOM.md` section E.

A live data point for PLOG once its offset is pinned: `CONVERT-DOM-A03` reported
`LINKAGE-LOAD-H02`'s logical segment as **22** during a real conversion run.
