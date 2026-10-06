# DOM / SEG File Format (New ND-500(0) Domain Format)

**`:DOM`** (domain) and **`:SEG`** (free segment) are the file types produced by the
newer **ND Linker** (ND-211224) and consumed directly by the ND-500(0) Monitor to run a
program. They replace the old `:PSEG`/`:DSEG`/`:LINK` + `DESCRIPTION-FILE:DESC` scheme -
see [DESCRIPTION-FILE-FORMAT.md](DESCRIPTION-FILE-FORMAT.md) for that older format and
why it needed a separate index file. `CONVERT-DOMAIN` (ND-500 vendor program,
`CONVERT-DOM-A03.DOM`) migrates old-format domains into `:DOM`/`:SEG`.

**Primary source - VERIFIED, code-level ground truth, stronger than the manual alone:**

`src/include/nd500/dom.h` in the `pcc-nd500` repository - the exact `#pragma pack(1)`
struct layout used by `dom_utils.c` (`libdom.a`), consumed by both `nd500-dis` and
`nd500-dump` in the pcc-nd500 toolchain to load and run real `.DOM` files (this is the
code path behind the working `HELLO.DOM` compile/link/run chain documented in the
`nd500-apps` skill) - not just a transcription of the manual's prose.

**Secondary source:** `ND-860289-2-EN ND Linker User Guide and Reference Manual.md`
(NDInsight `Reference-Manuals/`), Appendix E "The New Domain Format" - the narrative
description; the header field list there is qualitative only (no byte offsets), which is
why `dom.h`'s concrete offsets are the primary source here.

All multi-byte fields are **big-endian** (ND-500 native byte order).

---

## 1. Overall file layout

```
0x0000  Domain header: 2 pages of 2048 bytes (0x0000-0x0FFF); the next 2 pages are reserved
0x1000  (compressed files only) debug info directly after the header
0x2000  Debug info of a freshly linked domain (default area reserved: 1024 pages = 2 MB)
0x202000  Link info (symbol table), default 2 MB area
0x402000  Program segment 1, default 2 MB area
0x602000  Data segment 1, default 32 MB area
```

Measured 05-OCT-2026 on a freshly linked `HELLO:DOM` (nd100x, real SINTRAN, ND LINKER B01): debug
info at 0x2000, link info at 0x202000, program at 0x402000, data at 0x602000. The byte count of the
file is the start of the data segment plus its size (0x602000 + 0x35DC = 6313436 bytes), while only
23 pages are allocated on disk. `COMPRESS` in the linker's service program removes the holes (the
same domain then has 47104 bytes and the next area directly after the header). Source: ND Linker
manual ND-860289-2, SET-AREA-SIZE and appendix E. The offsets in the manual's appendix E table are
printed one octal digit short; the measured values above are the ones to use.

Only pages actually used are allocated on disk. A `:DOM` file with no external links can
be copied with a plain `@COPY-FILE` (everything needed is inside it); a `:SEG` file holds
exactly one program+data segment pair, referenced by one or more `:DOM` files via a
link key match (see section 5).

## 2. File Header (16 bytes, offset 0x00 - shared by DOM and SEG)

| Offset | Field | Size | Meaning |
|---|---|---|---|
| 0x00 | LINKLOCK | 4 | Random lock value. A domain linked to a `:SEG` file records this value as its LINKKEY; they must match at load time or the segment is considered a different version. |
| 0x04 | VERSION | 1 | ND Linker version that produced this file. |
| 0x05 | REVISION | 1 | ND Linker revision. |
| 0x06 | FLAGS | 1 | Bit 3: trap block valid. Bit 4: **is a `:DOM` file** (vs `:SEG`). Bit 5: root/multidomain. Bit 6: SINTRAN-III domain. Bit 7: is ND-500/5000. |
| 0x07 | MACHINE | 1 | Target machine type. |
| 0x08 | OS_ID | 1 | Operating system ID. |
| 0x09 | reserved | 1 | |
| 0x0A | SUBSYSTEM_KEY | 6 | |

`dom_is_dom_file()`/`dom_is_nd500_file()`/`dom_is_sintran_iii()` test bits 4/7/6 of the
FLAGS byte directly.

## 3. DOM-specific part (offset 0x10 - 0xC6)

| Offset | Field | Size | Meaning |
|---|---|---|---|
| 0x10 | PRIVILEGES | 8 (4x16-bit) | Domain privileges. |
| 0x18-0x25 | (padding) | 14 | |
| 0x26 | MOTHER | 8 | Domain Reference (below) to the mother domain. |
| 0x2E | CHILDREN[16] | 128 (16x8) | Domain References to up to 16 child domains. |
| 0x2E+128=0xAE .. 0xC5 | (padding) | to 0xC6 | |

**Domain Reference** (8 bytes): `MIN_INDEX`(u16) + `MAX_INDEX`(u16) = byte range into the
name pool for this domain's name, + `LINK_KEY`(u32) which should match the referenced
domain's LINKLOCK.

## 4. Common part (offset 0xC6 - 0x108, both DOM and SEG)

| Offset | Field | Size | Meaning |
|---|---|---|---|
| 0xC6 | FREIND | 2 | Free byte pointer into the name pool. |
| 0xC8 | DEB_LB | 4 | Debug info lower bound (file offset). |
| 0xCC | DEB_SZ | 4 | Debug info size. |
| 0xD0 | LINK_LB | 4 | Link info lower bound. |
| 0xD4 | LINK_SZ | 4 | Link info size. |
| 0xD8 | STADDR | 4 | **Start address.** |
| 0xDC | RESTADDR | 4 | Restart address. |
| 0xE0 | THA | 4 | Trap Handler Address. |
| 0xE4 | MTE2 / 0xE8 MTE1 | 4+4 | Memory Trap Enable (64-bit mask, high then low word). |
| 0xEC | OTE2 / 0xF0 OTE1 | 4+4 | Own Trap Enable (64-bit mask). |
| 0xF4 | CTE2 / 0xF8 CTE1 | 4+4 | Child Trap Enable (64-bit mask). |
| 0xFC | TEMM2 / 0x100 TEMM1 | 4+4 | Trap Enable Mod Mask (64-bit mask). |
| 0x104 | PRIORITY | 4 | Process priority. |

(Common part ends at 0x108.)

## 5. Segment part (28 bytes) - the building block for one program OR one data segment

| Field | Size | Meaning when NOT linked | Meaning when `ATT.LINKED_SEGMENT` bit set |
|---|---|---|---|
| LB | 4 | Lower bound = file offset of segment content | Name-pool index of the linked-to segment's name |
| SZ | 4 | Size in bytes | LINKKEY to match against the target `:SEG` file's LINKLOCK |
| ATT | 4 | Attribute bitmask (section 6) | (same) |
| FLA | 4 | Fixed Lower Address = virtual load address | |
| FUA | 4 | Fixed Upper Address | |
| AFA | 4 | Absolute Fix Address | |
| MINP | 2 | Min pages | MIN name-pool index (if linked) |
| MAXP | 2 | Max pages | MAX name-pool index (if linked) |

A **Segment Descriptor** (56 bytes) = one Program Segment Part + one Data Segment Part,
back to back.

## 6. Segment ATT (attribute) bits

| Bit | Name | Meaning |
|---|---|---|
| 10 | FIXED_ABSOLUTE | |
| 11 | FIXED_CONTIGUOUS | |
| 12 | FIXED_SCATTERED | |
| 13 | **SEGMENT_USED** | Slot contains valid data - test this before reading a slot. |
| 14 | **LINKED_SEGMENT** | LB/SZ (and MINP/MAXP) hold name-pool index / link key, not offset/size - see section 5. |
| 15 | ROUTINE_VECTOR | |
| 16 | INSUFF_LOADED | |
| 17 | FORTRAN_COMMON | |
| 18 | OTHER_MACHINE | |
| 19 | START_VECTOR | Start vector on this segment. |
| 20 | INDIRECT | |
| 21 | SHARED_ND100 | |
| 22 | COPY_CAPABILITY | |
| 23 | CLEAR_CAPABILITY | |
| 24 | CACHE | |
| 25 | FILE_AS_SEGMENT | |
| 26 | EMPTY_DATA | |
| 27 | SHARED_DATA | |
| 28 | PROGRAM_SEGMENT | |
| 29 | SWAP_ON_SWAPFILE | |
| 30 | PARAMETER_ACCESS | |
| 31 | WRITE_PERMIT | |

## 7. DOM header - full layout (4096 bytes)

| Offset | Field | Size |
|---|---|---|
| 0x000 | File Header | 16 |
| 0x010 | DOM-specific part | to 0xC6 |
| 0x0C6 | Common part | to 0x108 |
| 0x108 | Indirect segments[32] | 32 x 10 = 320, to 0x248 |
| 0x248 | LANGUAGE_MSAL | 4 |
| 0x24C | IDX_FREE_MIN/MAX | 2+2 |
| 0x250-0x253 | (padding) | 4 |
| **0x254** | **Segment table**: 32 x Segment Descriptor (56 bytes each) | 1792, to 0x954 |
| 0x954 | Name pool | to 0x1000 |

**Indirect Segment** (10 bytes): MIN_INDEX(u16) + MAX_INDEX(u16) + LINK_KEY(u32) +
SLOG(u8, logical segment number) + reserved(u8).

To read segment N's descriptor: `header + 0x254 + N*56` (N = 0..31). Program part first
(28 bytes), then data part (28 bytes). Check `ATT.SEGMENT_USED` before trusting the slot.

## 8. SEG header - full layout (4096 bytes)

A `:SEG` file holds exactly one segment pair (no domain-level bookkeeping - mother/child,
segment table, language mask):

| Offset | Field | Size |
|---|---|---|
| 0x000 | File Header | 16 |
| 0x010-0x013 | (padding) | 4 |
| 0x014 | Program Segment Part | 28, to 0x030 |
| 0x030 | Data Segment Part | 28, to 0x04C |
| 0x04C-0x06F | (padding) | to 0x070 |
| 0x070 | PROG_LOGSEG | 1 |
| 0x071 | DATA_LOGSEG | 1 |
| 0x072 | N100_COUNT | 2 |
| 0x074 | N100 RT segments[10] | 10 x 12 = 120, to 0xEC |
| 0xEC-0xC5 | (pad to Common part) | |
| 0x0C6 | Common part | to 0x108 |
| 0x108 | Indirect segments[32] | 320, to 0x1C8 |
| 0x1C8 | LANGUAGE_MSAL | 4 |
| 0x1CC | IDX_MIN/MAX (ID message) | 2+2 |
| 0x1D0-0x1D3 | reserved | 4 |
| 0x1D4 | Linked segments[32] | 32 x 16 = 512, to 0x3D4 |
| ... | Name pool | to 0x1000 |

**ND-100 RT Segment** (12 bytes): N100SW[6] (name) + N100SNO(u16) + N500LOGPA(u16, map
address in ND-500 logical memory, pages) + N100SIZE(u16, pages).

**Linked Segment** (16 bytes, SEG files only): PROG_MIN/MAX(u16 each) + PROG_KEY(u32) +
DATA_MIN/MAX(u16 each) + DATA_KEY(u32).

## 9. Name pool

A byte pool at the end of the header (`0x954..0x1000` for DOM, `0x454..0x1000` for SEG).
A name is `pool[min_index .. max_index)`. `min_index==0 || max_index==0 || min_index>=max_index`
means "no name."

## 10. Open items

- FLAGS byte (offset 0x06) is now confirmed against a real, freshly-produced `.DOM`:
  `CONVERT-DOM-A03` converting `LINKAGE-LOAD-H02` (2026-08-10, see
  `../ND500-APPS/CONVERT-DOM-A03/userguide.md`) wrote `0xF8` = bits 3/4/5/6/7 set =
  TRAPBLOCK_VALID + IS_DOMAIN_FILE + IS_ROOT_DOMAIN + IS_SINTRAN_III + IS_ND500, exactly
  matching this doc's bit table.
- The rest of the segment table, name pool, and common part have no field-by-field
  validation report against a real `.DOM` beyond what the working `nd500-dis`/
  `nd500-dump`/nd500x runtime already exercises implicitly (they run real DOMs
  successfully, which is strong indirect validation, but no dedicated byte-level
  walkthrough doc exists yet).
- `DOM_COMMON_OFFSET`/`DOM_STADDR_OFFSET` macro names in `dom.h` (0xC6, 0xD8) match this
  doc's Common Part table exactly - kept in sync intentionally; if `dom.h` changes, update
  this doc too.
