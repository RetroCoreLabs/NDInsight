# Extracting SINTRAN system segments

Full path: `tools/sintran-segment-carver/EXTRACTING-SEGMENTS.md`

The single authoritative guide for carving the individual **system segments** out
of a SINTRAN III SMD disk image so each can be loaded into **Ghidra** (or
`nd100-dis`) at its correct load address for reverse engineering — file system,
command processor, monitor-call handlers, XMSG, ND-500 monitor, etc. Works for any
SINTRAN version; L/VSX-500 (L07) is the worked example.

For the memory-**resident** code that has no SEGFIL0 disk image (resident common
code/data, the level-14 MON dispatch), see the companion
[EXTRACTING-RESIDENT-CODE.md](EXTRACTING-RESIDENT-CODE.md).

---

## 1. Why this is not just "dd a file out"

SINTRAN keeps every system segment inside one contiguous file,
`(SYSTEM)SEGFIL0:DATA`. Where each segment lives **inside** that file (its `MADR`
page offset) and how long it is (`SEGLE`) are recorded **only in the in-memory
Segment Table** — there is no fixed disk header to parse offline. At runtime the
segments are paged into overlapping virtual-address windows, so you also cannot
just dump memory and get them all. The tool therefore combines four fact sources
(in strict precedence):

> **Corrections 2026-10-29: "only in the in-memory Segment Table" is no longer true.** Both
> fact sources are on the disk and can be read **offline**, measured on BIGDISK0-K-100,
> BIGDISK0-L2-100, BIGDISK0-L-SEMICS and nd100x SMD0:
> - The segment table is itself a segment inside `SEGFIL0:DATA` (`S3ISGT` image, `S3SSGT`
>   save) and is found with the self-validating scan of
>   `SINTRAN/OS/26-INITIAL-COMMAND-BUFFER-ON-DISK.md` §3.2 (entry 0 all zero, one entry whose
>   `MADR` equals the page's own number): page **461** of `SEGFIL0:DATA` on K, **1275** on L.
> - The names are the RT-loader's "DEFINED SEGMENT NAME" records (type 25B, 8 words, SIXBIT
>   name; `SINTRAN/OS/22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md` §6.5) and sit in the
>   plain file `(SYSTEM)RTFIL:DATA` as well as in the S3RTFIL segment: 74 records on K, 98 on L.
> - The kernel's segment-file tables (`DBLST`, `ABLPAGE`, `MASSNO`) are read from the S3IDPIT
>   copy (segment 44) in `SEGFIL0:DATA`; measured `DBLST(0) = 256` blocks, `ABLPAGE(0) = 2`.
>
> `ndtool --segments` / `--export-segment` / `--import-segment` in the sibling repository
> `norskdata-ndfs` (`ndfs-c/src/sintran_segments.c`) does the whole job from the image alone; the
> live DAP path in section 5 remains as option A.

| Fact | Authoritative source |
|------|----------------------|
| Segment number + **name** | live `@RT-LOADER` -> `LIST-SEGMENT`, or the type-25 name records in `(SYSTEM)RTFIL:DATA` / the S3RTFIL segment (offline, 2026-10-29) |
| **MADR** (page offset in SEGFIL0) + **SEGLE** (length in pages) | live in-memory Segment Table (bank 3, offset 0o124000), or the S3ISGT segment-table page inside `SEGFIL0:DATA` (offline, 2026-10-29) |
| **Load address** / range / PIT / description | release manual section 8.3 |
| (cross-checked, not trusted) | `SINTRAN Structures/sintran-system-segments.json` (AI-derived) |

---

## 2. The page / carve model (READ THIS)

- **1 SINTRAN page = 1024 words = 2048 bytes**, big-endian (native ND-100).
  Confirmed via `ndtool --stat`: `(SYSTEM)SINTRAN:DATA` = 63 pages = 129024 bytes
  => 2048 bytes/page.
- **`MADR` and `SEGLE` are both in 2048-byte pages.**
- Inside the extracted `SEGFIL0` a segment occupies exactly:

  ```
  segment bytes = SEGFIL0[ MADR * 2048 : MADR * 2048 + SEGLE * 2048 ]
  ```

- **Load address** for Ghidra = `(LOGAD * 1024) & 0xFFFF` (LOGAD = Segment-Table
  word 2). E.g. S3FS -> 26000B, S3CP -> 30000B, S3SM5 -> 40000B.
- Segments are packed **contiguously**: segment N+1 begins exactly `SEGLE` pages
  after segment N, so a full `SEGLE`-page read never overshoots its neighbour.
- Output `.bin` is big-endian; it drops straight into a big-endian ND-100 Ghidra
  processor. Byte-swap only for `nd100-dis` (section 6), never for Ghidra.

### Why the earlier "half-length" model was wrong (settled)

An earlier version of the carver used `SECTOR = 1024` (1024-byte "sectors", i.e.
half a page) and a raw-SMD base `(CBLST + MADR) * 1024` with `CBLST = 1670`. That
was wrong on two independent counts, both verified against the raw disk:

1. **Half the page size.** Every manual section-8.3 range equals `SEGLE * 1024
   words` exactly (S3FS 54272 = 53 x 1024; S3CP 53248 = 52 x 1024; S3SM5, S3SSM,
   S3TAD likewise). Reading `SEGLE * 512` words produced half of each segment.
2. **A mis-derived base.** `CBLST = 1670` (1024-byte sectors) lands ~60 KB off the
   real NDFS file location; it happened to hit unrelated-but-coherent code.

A tempting "fix" — keep the base and read `SEGLE * 2` sectors — is **also wrong**:
segments are packed at `SEGLE`-page spacing, so the doubled read byte-for-byte
appends the *next* segment (the words after the S3FS carve are identical to S3CP's
start; after S3ISYS, identical to its neighbour at MADR 1067). The correct approach
is to carve from the extracted SEGFIL0 with 2048-byte pages, above.

**How we know the current model is right:** raw `SMD0.IMG` at
`NDFS_block_128 * 2048 + MADR * 2048` is byte-identical to the extracted-SEGFIL0
segment (the extraction is confirmed against the raw disk via the NDFS directory
itself); the full S3FS is coherent ND-100 code across *both* halves (12234 lower /
11946 upper control-flow instructions, near-equal density); and the next segment
begins exactly `SEGLE` pages later, so nothing overshoots.

**Corrections 2026-10-29 - the kernel's own numbers agree, and give the general rule.**
The "NDFS block 128" above is disk **page** 128 (1024 words). The kernel reaches it as
`DBLST(0) = 256` disk **blocks** of 512 words with `ABLPAGE(0) = 2` blocks per page
(`IP-P2-SEGADM.NPL` RWSEGM lines 1532-1540: "DISK ADDRESS FOR THIS SEGMENT FILE (DOUBLE
WORD)", "NUMBER OF DISK BLOCKS PER PAGE"), read from the resident data page (`BLST=004023`,
`ABLPA=004461` L07 / `004451` K03) in the S3IDPIT copy. Measured identical on the K pack and
all three L packs. So in general:

```
disk page of page P of a segment = DBLST(N) / ABLPAGE(N) + MADR + P      N = FLAG >> 13
```

Segment file 4 (`FLAG` bit 15, the absolute-save set) has base `ABLPAGE(0) + XXSWTYPE`
blocks = disk page 1 (`PH-P2-OPPSTART.NPL:751`); on the K pack its segments 52-60 and 63 are
therefore inside `(SYSTEM)SINTRAN:DATA` (disk pages 1-63) and `MACM-AREA:DATA` (64-127), not
in `SEGFIL0:DATA` - e.g. S3SDPIT (53, MADR 27) at disk page 28. `carve.py` with
`--cblst 0` on the extracted `SEGFIL0.DATA` is right for file-0 segments only; a file-4
segment needs the other file. On the L packs every system segment, save copies included, is
in file 0.

---

## 3. Prerequisites

- `ndtool` from `norskdata-ndfs` (reads/extracts the SINTRAN NDFS disk).
- `nd100x` emulator + DAP (only to grab the segment table — step 5 option A).
- Python 3.
- Ghidra with an ND-100 (big-endian, 16-bit) processor module.

Inputs live one folder per version, e.g.
`tools/sintran-segment-carver/versions/L-VSX-500/inputs/`:

| File | How to get it |
|------|---------------|
| the SMD image | your disk image (not copied into the repo) |
| `list-segment.txt` | paste of `@RT-LOADER` -> `LIST-SEGMENT` (name + octal number) |
| `list-rt-programs.txt` | paste of `@LIST-RT-PROGRAMS` (reference/validation) |
| `segment-table-bank3.bin` | the in-memory Segment Table dump (step 5) |

---

## 4. Extract SEGFIL0 (the file the carver reads)

```bash
ndtool -i    SMD0.IMG                                   # volume + user summary
ndtool -t -u SYSTEM SMD0.IMG                            # confirm (SYSTEM)SEGFIL0:DATA present
ndtool -x -F 'SYSTEM/SEGFIL0:DATA' -o extract/ SMD0.IMG # -> extract/SEGFIL0.DATA
```

The extracted `SEGFIL0.DATA` is **big-endian** (native ND-100); `carve.py` reads it
as-is. **Byte-order sanity check** before carving: the first word of a full-window
segment (e.g. S3FS at `MADR * 2048`) should read as its load address `026000` when
interpreted big-endian. If instead you see `000054`, the file is byte-swapped —
swap it back to big-endian first.

---

## 5. Get the Segment Table

**Option A — auto (default), from a running system via nd100x + DAP:**
1. `nd100x --debugger --boot=smd --smd0=SMD0.IMG`, wait for `SINTRAN III RUNNING`.
2. Connect DAP, then read the pointer and the table:
   - `dspace:0x8D0` -> SEGTB (bank, = 3) and SEGST (offset, = 0xA800 = 0o124000).
   - Read `phys:<(SEGTB<<16)+SEGST>` (for L: `phys:0x3A800`) for ~2 KB and save the
     bytes as `segment-table-bank3.bin`. (DAP `phys:` takes a **word** address.)

Segment-Table entry = 8 words: word[2] = LOGAD (page), word[3] = SEGLE (pages),
word[4] = MADR (page offset in SEGFIL0), word[5] = FLAG (top 3 bits = SEGFIL#).

**Option B — manual, from SINTRAN commands only (fallback):**
```
@RT-LOADER
LIST-SEGMENT            (-> list-segment.txt: names + numbers)
EXIT
@LIST-RT-PROGRAMS       (-> list-rt-programs.txt: RT validation)
```
This gives names/numbers but **not** MADR/SEGLE, so Option A (or a supplied
`segment-table-bank3.bin`) is still required to know the file offsets.

**Option C — offline, from the image alone (2026-10-29):** the segment table is the
`S3ISGT` page inside `SEGFIL0:DATA` (found by the self-validating scan of
`SINTRAN/OS/26-INITIAL-COMMAND-BUFFER-ON-DISK.md` §3.2; page 461 on the K pack, 1275 on
the L packs), and the names are the type-25 records in `(SYSTEM)RTFIL:DATA`.
`ndtool --segments <image>` (sibling repository `norskdata-ndfs`,
`ndfs-c/src/sintran_segments.c`) lists number, name, LOGAD, SEGLE, MADR, segment file
and disk page for every segment; `--export-segment` writes one `.bin`. No boot, no DAP.

---

## 6. Reconcile facts and carve

```bash
python3 reconcile.py \
  --list-segment versions/L-VSX-500/inputs/list-segment.txt \
  --manual "../../SINTRAN/Release-Documentation/ND-860230-6-EN Sintran III - Release Information - L-Version.md" \
  --sgt versions/L-VSX-500/inputs/segment-table-bank3.bin \
  --json "../../SINTRAN/SINTRAN Structures/sintran-system-segments.json" \
  --out versions/L-VSX-500
# -> segment-facts.json (canonical) + json-discrepancies.txt

python3 carve.py \
  --smd extract/SEGFIL0.DATA \
  --facts versions/L-VSX-500/segment-facts.json \
  --out versions/L-VSX-500/segments
# -> one big-endian .bin per segment + manifest.json  (SECTOR=2048, --cblst 0)
```

The carver writes **two kinds of metadata**:

- `manifest.json` — all segments in one file: `name`, `load_address_oct`,
  `load_address_hex`, `load_address_dec`, `segle`, `madr`, `flag_oct`,
  `symbol_file`, `confidence`, `file`, `bytes`, `size_words`, `nonzero`,
  `byte_order`.
- `NNN-<NAME>.meta.json` — one **self-contained sidecar per carved segment**, next
  to its `.bin`. It carries the same facts grouped (`load_address` with `oct`/`dec`/
  **`hex`**, `size`, `segfil0`, `symbol_file`, `confidence`, `content`) plus a
  ready-to-use `ghidra` block: `processor`, `format: Raw Binary`, and
  **`base_address_hex`** — the exact base to type into Ghidra.

Segments that carve to all-zero (`nonzero:false`) are un-installed subsystems (e.g.
the ND-500 monitor when not installed) — skip them. `madr == 0` segments are
memory-resident and are correctly skipped (they have no distinct SEGFIL0 image — see
the resident doc).

---

## 7. Load into Ghidra (one program per segment)

Segments overlap in virtual address space (many load at 26000B/30000B because they
share a paged window at runtime), so use **one Ghidra program per segment**:

1. `File > Import File...` -> pick `NNN-<NAME>.bin`.
2. Format **Raw Binary**; Language = your **ND-100 big-endian 16-bit** processor.
3. Options -> **Base Address** = the segment's Ghidra base in **hex**, from its
   `.meta.json` -> `ghidra.base_address_hex` (e.g. S3FS = `26000` octal = **`0x2C00`**;
   S3CP `30000` = `0x3000`; S3SM5 `40000` = `0x4000`). ND-100 is word-addressed — set
   the base in the word address space.
4. Disassemble from the load address (`D`).
5. Apply labels: run `ghidra_scripts/LoadSintranSegments.py` (set `LANG_ID` first)
   with `manifest.json` and `SINTRAN/NPL-SOURCE/SYMBOLS/L07/`. It maps each segment
   to its symbol table (S3FS->FILSYS-SYMBOLS, kernel/command->SYMBOL-1-LIST,
   XMSG->XMSG-SYMBOL-LIST, ND-500->N500-SYMBOLS, RT-loader->RTLO-SYMBOLS) and
   creates labels from `NAME=octaladdr` lines.

Because SINTRAN code calls fixed resident/common addresses via `JPL I`, also import
`SYMBOL-1-LIST` labels into every program so cross-segment/resident calls resolve.

**ND-500 segments are NOT ND-100 code.** S3SM5 (030) and S3SSM5 (062) are ND-500
32-bit byte-addressed code — do not load them with the ND-100 processor. Use
`nd500-dis` (see `versions/L-VSX-500/segments/030-S3SM5-DISASSEMBLY-PROMPT.md`).

**Byte order for `nd100-dis`:** the carved `.bin` is big-endian; `nd100-dis` reads
raw binaries as little-endian only, so byte-swap first (never swap the Ghidra file):
```bash
python3 -c "import sys;d=bytearray(open(sys.argv[1],'rb').read())
d[0::2],d[1::2]=d[1::2],d[0::2];open(sys.argv[2],'wb').write(d)" \
  segments/006-S3FS.bin 006-S3FS.le.bin
nd100-dis -a -S -b 026000 006-S3FS.le.bin      # base = load_address, octal
```

---

## 8. Fact precedence & confidence

`segment-facts.json` records `confidence` per segment:
- **high** — live name and a sane manual range agree.
- **medium** — manual name is an OCR variant of the live name (live is used; e.g.
  manual `S3IP1IT` vs live `S3I5PIT`, OCR 5->1). Load address still trusted.
- **low** — manual range is backwards (OCR, e.g. seg 40 `164000:137777`) or the
  segment is absent from live `LIST-SEGMENT`. Verify the load address before use.

Known OCR issues in the L manual section 8.3:
- Segments 72-77 rows are shifted; live `LIST-SEGMENT` has the correct mapping
  (72 S3SDMWD, 73 S3IDMWD, 74 S3SXMK, 75 S3SXROU, 76 S3XMK, 77 S3XROU).
- Backwards ranges (end < start) on some rows — the JSON's end value is sometimes
  better. Load address (range start) is unaffected.

The `[start,end]` word pair some segments begin with is **not** a reliable length
field (it matches `SEGLE * 1024` for only 13/30 — coincidence for full-window
segments whose data begins with the window bounds). Authoritative length is always
`SEGLE` (Segment-Table word 3).

---

## 9. Per-version carved sets

The carved output for each version, with a human-readable per-segment catalog
(load address, pages, MADR, content type):

- `versions/L-VSX-500/segments/README.md` (canonical template, fullest)
- `versions/K-VSX-500/segments/README.md`
- `versions/M-VSX-500/segments/README.md`

---

## Files

| Path | Purpose |
|------|---------|
| `reconcile.py` | merge live + manual + memory into `segment-facts.json` (+ discrepancy report) |
| `carve.py` | carve `.bin` per segment from the extracted SEGFIL0 using the facts (SECTOR=2048) |
| `ghidra_scripts/LoadSintranSegments.py` | Ghidra label-import helper |
| `versions/<VER>/inputs/` | per-version inputs (listings + segment-table dump) |
| `versions/<VER>/segment-facts.json` | canonical reconciled facts |
| `versions/<VER>/segments/` | carved `.bin` + `manifest.json` + per-version catalog |
