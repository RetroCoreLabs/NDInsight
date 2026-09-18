# RXDIR-CACHE-COMPLETE - the complete block-0 read path through the page cache

Full every-path carve of the SINTRAN III VSX/500 **L07** routines that turn a
filesystem "read directory block 0" request into a device transfer, in segment
`006-S3FS` (load base **26000B**, `sha256(006-S3FS.bin)=b4a563d0...`):

| Symbol | Addr | Role |
|--------|------|------|
| `RXDIR` | 037643B | read page-0 extended-info via the cache; sets block := 0 |
| `RCBLO` | 035766B | reserve/read a cache block (HIT / MISS / alloc / dispatch) |
| `GSIZE` | 037101B | in-core configured disk size (NO device I/O) |
| `COMPP` | 036616B | RCBLO's cache compare/search helper (`[036064]=036616`) |
| `G3NWT` | 034371B | get-new cache entry / wait (`[036066]=034371`) |
| `R3BUF` | 035112B | RELEASE (invalidate) data-cache buffers for a device |
| `R3IBU` | 035102B | RELEASE (invalidate) index-cache buffers for a device |
| `CL1DB` | 035240B | release one cache buffer (used by RXDIR and RCBLO error exit) |

This EXTENDS the sibling folder [`../RCBLO/`](../RCBLO/README.md) (which already
carved RCBLO + GSIZE and answered "why no page-0 read is issued") to add the
full **RXDIR** body, the **R3BUF/R3IBU** release logic, and to name the cache
helpers RCBLO depends on (**COMPP**, **G3NWT**). It also closes the boundary that
[`enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md)
Section 4 left at the `JPL I ,B 10` dispatch.

**Grades.** VERIFIED = re-read from carved `006-S3FS.bin` bytes (offset =
`(addr - 26000B)*2` decimal, big-endian). INFERRED = reasoned from bytes +
architecture. OPEN = crosses an uncarved resident overlay or a runtime binding.
All addresses/values are **octal**. Disassembly:
[`RXDIR-CACHE-COMPLETE.ASM`](RXDIR-CACHE-COMPLETE.ASM); pseudo-code:
[`RXDIR-CACHE-COMPLETE.pseudo.c`](RXDIR-CACHE-COMPLETE.pseudo.c).

---

## 1. The call graph (every edge byte-verified except the runtime `,X 14` hop)

```
CHDSI 037763B --- 040000: JPL I 143 -> [040143]=037643 ---> RXDIR 037643B
RXDIR 037643B
   037647: JPL I 25  -> [037674]=003752   reserve/prologue
   037651: RADD CLD 0 DD                   BLOCK NUMBER := 0        (VERIFIED)
   037652: JPL I 23  -> [037675]=035766 ---> RCBLO 035766B (read cache block 0)
   037661: JPL I 16  -> [037677]=001224    copy 8-word ext-info out of buffer
   037665: JPL I 13  -> [037700]=035240 ---> CL1DB  (release the borrowed buffer)
RCBLO 035766B
   035773: JPL I 63  -> [036056]=037101 ---> GSIZE   (in-core size, NO I/O)
   036011: JPL I 53  -> [036064]=036616 ---> COMPP   (cache compare/search)
   036020: JPL I 46  -> [036066]=034371 ---> G3NWT   (get-new entry / wait)
   036135/036142/036167/036174: JPL I ,B 10 --->  DEVICE TRANSFER (RUNTIME ,X 14)
   036203: JPL I 15  -> [036220]=035240 ---> CL1DB   (release on error)
```

---

## 2. RXDIR (037643B) - every path

RXDIR is small and linear (body 037643-037672; `037673 ROP NOOP` separates it
from its pointer pool; next routine `WXDIR 037702B`).

1. **Prologue** (037643-037647): save link, 7-word frame, call resident
   reserve/prologue `003752`.
2. **Block := 0** (037650-037651): `RADD CLD 0 DA` / `RADD CLD 0 DD` set both A
   and the D (block-number) register to 0. VERIFIED byte `146101`.
3. **Read via cache** (037652): `JPL I 23 -> [037675]=035766` = **RCBLO** with
   block 0. VERIFIED `[037675]=035766`.
   - **RCBLO error** (037653 `JMP 16 -> 037671`): store status in `,B 2`, unwind,
     return error. This is RXDIR's ONLY error path - it forwards whatever RCBLO
     returned (GSIZE-fail, descriptor-fail, COMPP-fail, geometry-error, or a
     driver-transfer error) straight up to CHDSI.
4. **Extract ext-info** (037654-037661): `X = returned buffer`, `A = A+21B`
   (ext-info lives at buffer offset 21B), word count `T := 10B` (8. words),
   `JPL I 16 -> [037677]=001224` = resident block-copy into the caller's area
   (`,B 0`).
5. **Release the buffer** (037662-037665): `JPL I 13 -> [037700]=035240` =
   **CL1DB**. RXDIR does NOT keep the page-0 buffer - it copies the 8 ext-info
   words out and immediately frees it. VERIFIED `[037700]=035240`.
6. **OK exit** (037666-037670): ok-marker `MIN ,B 4`, unwind `-7`, return via
   `[037701]=003776` (resident epilogue).

So RXDIR itself has exactly two exits: OK (037670) and error (037671->037667),
and issues no device I/O of its own - all I/O is inside RCBLO.

---

## 3. RCBLO cache HIT / MISS / alloc decision map

RCBLO is the page cache. Its structure (bytes in [the .ASM](RXDIR-CACHE-COMPLETE.ASM)):

```
prologue (035766-035774)
  |  035773 GSIZE ; 035774 GSIZE-fail --------------------> ERROR STUB 036205
descriptor + classify (035775-036004)
  |  036000 descriptor-fail ------------------------------> ERROR STUB 036205
COMPP cache search (036011)
  |  036012 COMPP-fail -----------------------------------> ERROR STUB 036205
G3NWT get-new + stamp candidate (036020-036030)
block compare (036031-036042):  hi ,X5 / lo ,X6 / device
  |  any mismatch ----------------------------------------> MISS  036072
HIT gate (036043-036046):  clean/valid ?
  |  dirty/invalid ---------------------------------------> MISS  036072
HIT (036047-036053): reserve/wait, NO device read ------->  SUCCESS 036144
MISS (036072-...):
   stamp block/device (036072-036075), reserve/wait (036077)
   load transfer_fn = unit ,X14 -> local 10 (036100-036102)
   geometry math (036103-036117):  out-of-range -> A:=100B -> ERROR EPI 036177
   036122 descriptor2-fail -------------------------------> ERROR EPI 036177
   4 device-transfer dispatches (below)
SUCCESS (036144-036160): link buffer into cache, return X=buffer
ERROR EPILOGUE (036177-036204): CL1DB release + return error
ERROR STUB (036205-036206): store status + return error
```

**Decision summary**

| Situation | Path | Device read? |
|-----------|------|--------------|
| Block 0 already cached, clean | HIT 036047-036053 -> 036144 | NO |
| Block 0 cached but dirty/invalid | falls to MISS 036072 | YES (rewrite/read) |
| Block 0 not cached | MISS 036072 -> dispatch | YES |
| GSIZE / descriptor / COMPP fails | ERROR STUB 036205 | NO |
| Geometry out of range | 036116 A:=100B -> ERROR EPI 036177 | NO |
| Driver transfer returns error | ERROR EPI 036177 (CL1DB) | attempted |

The HIT path returning a stale/clean buffer WITHOUT a device read is exactly the
locus-(2) candidate for "why no page-0 read is issued" identified in
[`../RCBLO/README.md`](../RCBLO/README.md) Section 4d.

---

## 4. The four dispatch sites and what distinguishes them

All four are the SAME instruction `135410 JPL I ,B 10` (VERIFIED) - an indirect
call through frame word B+10, which was loaded at 036100-036102 from the unit
descriptor's **datafield word 14** (`LDA ,X 14`). What differs is the **function
selector "ABFUN"** each site builds from the operation code in `,B 12`:

| # | Addr | ABFUN arithmetic (VERIFIED) | On driver error | On driver OK |
|---|------|-----------------------------|-----------------|--------------|
| 1 | 036135 | `(op & 065B) + 066B` | 036136 -> 036177 error epi | fall to #2 (036137) |
| 2 | 036142 | `(op & 054B) + 063B` | -> 036161 (#3 group) | -> 036144 SUCCESS |
| 3 | 036167 | `(op & 032B) + 066B` | 036170 -> 036177 error epi | fall to #4 |
| 4 | 036174 | `(op & 022B) + 063B` | 036175 -> 036177 error epi | 036176 -> 036144 SUCCESS |

- The AND masks (`065 / 054 / 032 / 022`) and the two base constants (`066B` and
  `063B`) are VERIFIED from the bytes.
- The two bases pair up: `066B` on sites #1/#3, `063B` on sites #2/#4. INFERRED:
  `066B`/`063B` select two adjacent datafield sub-entries of the driver's
  transfer block (an even/odd read-vs-companion selector), i.e. ABFUN is a
  **datafield-relative selector**, NOT a raw SCSI opcode. The mapping ABFUN ->
  SCSDISK function number (0=READ, 1=WRITE, 4=SEEK, 42=READ FORMAT) is **OPEN**
  (that translation lives in the uncarved driver).
- **Which site runs** is driven by the skip-return status of the previous
  dispatch (site #1 ok falls into #2; #2 ok goes to success; #2 error chains to
  #3/#4). This chaining is VERIFIED from the branch bytes; the semantic meaning
  of each site (READ vs a companion/verify op) is INFERRED.

### The exact ABFUN value for a block-0 read

`op` (frame word `,B 12`) is loaded at 036001 from the **device-descriptor
getter `050124`** return, NOT from RXDIR (RXDIR passes A=0, but RCBLO overwrites
A with the descriptor status before it reaches `,B 12`). So the concrete numeric
`op` at mount time is a **RUNTIME input** and cannot be fixed from static
006-S3FS bytes.

- **VERIFIED:** the primary/READ dispatch (#1, 036135) emits
  `ABFUN = (op & 065B) + 066B`.
- **INFERRED:** for a plain read the op-class bits masked by `065B` are clear, in
  which case `ABFUN(#1) = 066B` (the base). `066B` is the datafield READ
  sub-entry selector, not a SCSI opcode.
- **OPEN:** the numeric SCSI function that `066B` resolves to inside the driver.

This is the honest answer the no-assumptions rule demands: the arithmetic is
byte-fixed; the input operand and the driver-side numeric meaning are not in this
segment.

---

## 5. GSIZE (037101B) - in-core, no I/O

Save link, 7-word frame, resident prologue `003752`, then three in-core
parameter getters (`050124`, `050223`, `050220`), a geometry-bit test
(`037124 BSKP ONE 100 DT`) that may call low helper `000215`, a shift
(`037132`), and `037134 RMPY` to compute the 32-bit size, stored in `,B 2`.
**Proof of no device I/O:** there is no `JPL I ,B` (no datafield dispatch)
anywhere in the body. Error path 037141-037142. VERIFIED entry `021042`,
VERIFIED `141216 RMPY`.

---

## 6. R3BUF (035112B) / R3IBU (035102B) - bulk buffer RELEASE

R3BUF/R3IBU are the release counterpart to the cache getters. Two entries share
one body:

- `R3IBU 035102B` sets flavour `2` (index buffers), `R3BUF 035112B` sets
  flavour `1` (data buffers); both converge at 035121.
- The body walks the cache-buffer list (`035121-035123` list head via resident
  iterator `010500`), and for each buffer that matches the requested device
  (`,X 5 == ,B 1`, 035132-035135) and passes the flavour/busy gate
  (035136-035147) it:
  1. **invalidates** the buffer: `,X 4 := -1`, `,X 5 := -1` (035153-035154), and
  2. **unlinks** it from the LRU doubly-linked list via the forward `,X 22` /
     back `,X 23` pointers (head-of-list case 035160-035167, mid-list case
     035170-035177), then pushes it onto the free list (035200-035210).
- Loop continues (035211-035212) until the `T=-1` end sentinel (035124-035126),
  then releases the reserve and returns (035213-035217).

INFERRED role: **dismount / cache-flush** - drop every cached block for a device
so a later mount re-reads from the disk. VERIFIED entries `021116` (R3IBU) /
`021106` (R3BUF); VERIFIED shared-body head `045101`. The exact list-head data
addresses are I-displacement literals into the segment data pool (not carved as
symbols here).

**Relation to the mount bug:** R3BUF is the routine a correct dismount/re-mount
would call to invalidate a stale page-0 buffer. If block 0 is left in the cache
**clean** from a prior probe and R3BUF is NOT called between operations, RCBLO's
HIT path (Section 3) returns it with no device read - consistent with the
"page-0 read never enqueued" symptom. (INFERRED; a live DAP trace settles it, per
[`../RCBLO/README.md`](../RCBLO/README.md) Section 4.)

---

## 7. dd verification (15 load-bearing words)

Re-read from `versions/L-VSX-500/segments/006-S3FS.bin`, byte offset =
`(addr - 26000B)*2` decimal, big-endian. All matched expected:

| Addr | Off (dec) | hex | Octal val | Meaning |
|------|-----------|-----|-----------|---------|
| 037643 | 10054 | 2218 | 021030 | RXDIR entry `STD I 30` |
| 037651 | 10066 | cc41 | 146101 | RXDIR block := 0 (`RADD CLD 0 DD`) |
| 037652 | 10068 | ba13 | 135023 | RXDIR `JPL I 23` -> RCBLO |
| 037675 | 10106 | 3bf6 | 035766 | RXDIR ptr -> RCBLO |
| 037700 | 10112 | 3aa0 | 035240 | RXDIR ptr -> CL1DB |
| 035766 | 8172  | 2236 | 021066 | RCBLO entry `STD I 66` |
| 036135 | 8378  | bb08 | 135410 | RCBLO `JPL I ,B 10` (dispatch) |
| 036056 | 8284  | 3e41 | 037101 | RCBLO ptr -> GSIZE |
| 036064 | 8296  | 3d8e | 036616 | RCBLO ptr -> COMPP |
| 036220 | 8480  | 3aa0 | 035240 | RCBLO ptr -> CL1DB |
| 037101 | 9346  | 2222 | 021042 | GSIZE entry `STD I 42` |
| 037134 | 9400  | c28e | 141216 | GSIZE `RMPY SD DT` (compute size) |
| 035112 | 7316  | 2246 | 021106 | R3BUF entry `STD I 106` |
| 035102 | 7300  | 224e | 021116 | R3IBU entry `STD I 116` |
| 035121 | 7330  | 4a41 | 045101 | R3BUF shared body `LDA I 101` |

Command form (Git Bash):
`off=$(( (8#ADDR - 8#26000) * 2 )); dd if=006-S3FS.bin bs=1 skip=$off count=2 | od -An -tx1`.

---

## 8. VERIFIED / INFERRED / OPEN summary

| # | Claim | Verdict |
|---|-------|---------|
| 1 | RXDIR 037643B sets block := 0 (146101) and calls RCBLO via `[037675]=035766` | VERIFIED (dd) |
| 2 | RXDIR copies 8-word ext-info out (`001224`) then releases the buffer via CL1DB `[037700]=035240` | VERIFIED (dd) |
| 3 | RXDIR has exactly two exits (OK 037670 / error 037671) and issues no I/O itself | VERIFIED |
| 4 | RCBLO HIT path (036047-036053) returns a cached buffer with NO device read | VERIFIED |
| 5 | RCBLO MISS path loads transfer_fn from unit `,X 14` (036100-036102) and dispatches | VERIFIED |
| 6 | 4 dispatch sites = same `135410 JPL I ,B 10`; ABFUN = `(op&065)+066` / `(op&054)+063` / `(op&032)+066` / `(op&022)+063` | VERIFIED (arith) |
| 7 | `op` (`,B 12`) comes from descriptor getter 050124 at runtime, not from RXDIR | VERIFIED |
| 8 | ABFUN(#1) for a read = 066B (op read-class bits clear) | INFERRED |
| 9 | ABFUN is a datafield sub-entry selector, not a raw SCSI opcode; ABFUN->SCSI function map | OPEN (uncarved driver) |
| 10 | GSIZE 037101B is in-core (no datafield dispatch); RMPY 037134 computes size | VERIFIED |
| 11 | COMPP 036616B = RCBLO's cache compare/search; G3NWT 034371B = get-new/wait | VERIFIED (symbol + call ptr) |
| 12 | R3BUF 035112 / R3IBU 035102 = bulk RELEASE (invalidate + LRU unlink) of a device's cache buffers | VERIFIED (structure) / INFERRED (dismount role) |
| 13 | Dispatch target `,X 14` -> SCSDISK -> SCLLD (INITO/SCWAQ) | INFERRED (NPL) / OPEN (runtime pointer, foreign segment) |

**Provenance.** Carved `006-S3FS` SINTRAN L07 bytes, load base 26000B,
`sha256(006-S3FS.bin)=b4a563d0...`; symbols
`SINTRAN/NPL-SOURCE/SYMBOLS/L07/FILSYS-SYMBOLS.SYMB.TXT` (`RXDIR 037643B`,
`RCBLO 035766B`, `GSIZE 037101B`, `COMPP 036616B`, `G3NWT 034371B`,
`R3BUF 035112B`, `R3IBU 035102B`, `G3BUF 034643B`, `G3IBU 034633B`,
`CL1DB 035240B`); driver logic (different revision, INFERRED)
`SINTRAN/NPL-SOURCE/NPL/IP-P2-SCSI-DISK.NPL` / `IP-P2-SCSI-DRIV.NPL`.

## See also
- [`../RCBLO/README.md`](../RCBLO/README.md) - the original RCBLO+GSIZE carve and the "why no page-0 read" analysis this folder extends.
- [`../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md) - the mount trace (Section 4 boundary now closed with the RXDIR body).
- [`../../../../../../SINTRAN/Filesystem/code-logic/scsi-mount-geometry.md`](../../../../../../../SINTRAN/Filesystem/code-logic/scsi-mount-geometry.md) - the last-block = control-record framing.
