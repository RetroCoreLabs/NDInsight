# ENTER-DIRECTORY - the complete carved mount path (device-agnostic side)

Full carve of the `@ENTER-DIRECTORY` command path in SINTRAN III VSX/500 **L07**,
segment `006-S3FS` (load base **26000B**), from the top-level worker `ENDIR`
down to the per-device transfer hand-off. This folder is the comprehensive,
byte-verified companion to
[`enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md)
(the narrative trace) and [`../RCBLO/`](../RCBLO/) (the cache-block dispatcher).

**The user's question:** `@ENTER-DIRECTORY ,,DISC-SCSI-1,0` FAILS on SCSI but
WORKS on SMD, Winchester and floppy. Since the path above the driver is
device-agnostic, the divergence must be at the hand-off to the per-device
driver. This carve makes that hand-off explicit (Section 3).

**Evidence grades.** VERIFIED = re-read from `006-S3FS.bin` / `044-S3IDPIT.bin`
with dd/python (byte offset = `(addr - loadbase)*2` decimal). INFERRED =
reasoned from bytes + architecture. OPEN = crosses into a foreign resident
overlay or depends on runtime state. All addresses/values are **octal**.

Deliverables here:
- [`ENTER-DIRECTORY.ASM`](ENTER-DIRECTORY.ASM) - full commented disassembly
  (GDIRA, ENDIR, CHDSI, RXDIR, WXDIR) + the RCBLO hand-off excerpt.
- [`ENTER-DIRECTORY.pseudo.c`](ENTER-DIRECTORY.pseudo.c) - readable pseudo-C for
  the whole flow; the device hand-off is a clearly-marked block at the bottom.

---

## 1. The call graph (every routine + address)

Every edge is byte-verified except the final `,X 14 -> driver` hop, which is a
runtime pointer binding (see Section 3).

```
@ENTER-DIRECTORY <dir>,<device>,<unit>[,F|R][,subunit]
   |  (command interpreter tokenises + resolves unit -> dir index; upstream
   |   segment, NOT 006-S3FS - OPEN boundary)
   v
ENDIR 0140176   enter-directory worker                       [006-S3FS]
   |  0140244: JPL I 141 -> [0140405]=030225   GDIRA  (get directory datafield)
   |  0140252: MON 124                          PRSRV  (reserve the unit)
   |  0140402: JPL I 33  -> [0140435]=037763   CHDSI  (do the mount)
   v
CHDSI 037763    check / enter directory                      [006-S3FS]
   |  0040000: JPL I 143 -> [0040143]=037643   RXDIR  (read page-0 ext-info)
   |  0040023: JPL I 121 -> [0040144]=037101   GSIZE  (in-core size, no I/O)
   |  0040127: JPL I 30  -> [0040157]=037702   WXDIR  (checksum + write back)
   v
RXDIR 037643    read page-0 ext-info via cache               [006-S3FS]
   |  037651: RADD CLD 0 DD                     block number := 0 (page 0)
   |  037652: JPL I 23  -> [037675]=035766      RCBLO  (reserve/read cache blk 0)
   |  037665: JPL I 13  -> [037700]=035240      CL1DB  (release buffer)
   v
RCBLO 035766    reserve/read cache block                     [006-S3FS]  (../RCBLO/)
   |  036100: LDX ,B 11 ; 036101: LDA ,X 14 ; 036102: STA ,B 10
   |  036135 / 036142 / 036167 / 036174:  JPL I ,B 10   *** DEVICE HAND-OFF ***
   v
(*datafield ,X 14)()   the per-device transfer primitive     [foreign resident seg]
                        SCSI: SCSDISK -> SCLLD (INITO -> SCWAQ)
                        SMD/Winchester/floppy: their own driver entry
```

| Addr (octal) | Symbol | Role | Verdict |
|--------------|--------|------|---------|
| 0140176 | `ENDIR` | Enter-directory worker: datafield, reserve, name guard, CHDSI | VERIFIED (entry `021030`) |
| 030225 | `GDIRA` | Directory index -> datafield base (leaf, `MPY 4`, `EXIT`) | VERIFIED (`146157`) |
| 037763 | `CHDSI` | Check/enter: read page 0, checksum, capacity, owner interlock, stamp | VERIFIED (entry `021154`) |
| 037643 | `RXDIR` | Read page-0 8-word ext-info via the buffer cache | VERIFIED (entry `021030`) |
| 037702 | `WXDIR` | Recompute checksum + write ext-info block back | VERIFIED (entry `021050`) |
| 037101 | `GSIZE` | Configured disk size from in-core tables (NO device I/O) | VERIFIED (see ../RCBLO) |
| 035766 | `RCBLO` | Cache-block manager; issues the device transfer via `,X 14` | VERIFIED (see ../RCBLO) |
| 035240 | `CL1DB` | Release one disk-cache buffer | VERIFIED (ptr) |
| 036357 | `WCBLO` | Write cache block back (used by WXDIR) | VERIFIED (ptr) |

---

## 2. MON calls used by the ENTER-DIRECTORY path

**Result: the carved filesystem path issues exactly ONE MON call - `MON 124`.**
Everything else in the chain (`GDIRA`, `CHDSI`, `RXDIR`, `WXDIR`, `RCBLO`,
`GSIZE`) is reached by ordinary `JPL` calls to routines resident in `006-S3FS`
or in the resident helper pool (`003752`, `003776`, `001224`, `010506`), and the
device transfer is the indirect `JPL I ,B 10`. There is no other `MON` opcode
anywhere in `ENDIR` (0140176-0140477), `CHDSI`, `RXDIR`, `WXDIR`, or `RCBLO`
(grep-verified over the carved listing).

Workers resolved through **`MCTAB` @ `005620B`** (segment `044-S3IDPIT`, load
base `4000B`), byte-read with dd. Table validated against three known slots
before use (skill trap #2): `MON 005 -> MCTAB[005]=102021 (RDISK)`,
`MON 144 -> MCTAB[144]=026354 (MAGTP)` - both match; `MON 200 -> MCTAB[200]=0`
confirms XMSG is a GOTAB level-14 fast handler, not an MCTAB slot.

| MON# | Symbol | MCTAB worker | Role in the mount | Verdict |
|------|--------|--------------|-------------------|---------|
| 124B | `PRSRV` (ForceReserve) | `MCTAB[124] = 037076B` | Reserve the mass-storage unit before any transfer. Fail -> error 147B. Called at 0140252B when `df->,X 4 != 0`. | VERIFIED (opcode `153124`; MCTAB byte-read; symbol `PRSRV=037076` L07) |

**Sibling reserve/release workers** (present in `MCTAB`, byte-verified; NOT
called by ENTER-DIRECTORY itself, but this is the reserve family PRSRV belongs
to - listed so the worker set is unambiguous):

| MON# | Symbol | MCTAB worker | Role |
|------|--------|--------------|------|
| 122B | `RESRV` | `037103B` | Reserve resource (the plain reserve primitive) |
| 123B | `RELES` | `037156B` | Release resource |
| 125B | `PRLS` | `037147B` | ForceRelease (used by the RENAME/release paths, not ENDIR) |

**OVERLAY NOTE (skill trap #4 - important).** `PRSRV=037076`, `RESRV=037103`,
`PRLS=037147`, `RELES=037156` are **resident-monitor virtual addresses**. In the
`006-S3FS` image those same addresses decode as `GSIZE`'s body (`GSIZE=037101`,
`RSSPG=037157` are the real 006-S3FS routines there). So the reserve workers are
a **different overlay** reached through `MCTAB`; their bodies are **not** the
`006-S3FS` bytes at those addresses and are **OPEN** here (resident reservation
module, not carved). This is exactly why one must not "carve RESRV from
006-S3FS" - it would disassemble `GSIZE`. The role for the mount is settled
regardless: `MON 124` reserves the physical unit before the page-0 transfer.

---

## 3. The device-datafield hand-off contract (THE SEAM)

This is where SCSI and the working device types (SMD/Winchester/floppy) diverge.
`RCBLO` (035766, carved in [`../RCBLO/`](../RCBLO/)) on a cache MISS loads the
per-device transfer primitive from the unit datafield and dispatches to it:

```
036100  054411  LDX ,B 11    ; X := unit/device descriptor            (VERIFIED)
036101  046014  LDA ,X 14    ; A := datafield word 14 = TRANSFER FN PTR (VERIFIED)
036102  004410  STA ,B 10    ; local 10 := that pointer (the driver entry)
...
036135  135410  JPL I ,B 10  ; *** DEVICE TRANSFER *** (RUNTIME target = ,X 14) (VERIFIED)
```

The contract the filesystem hands the driver:

| Field | What ENTER-DIRECTORY sets / asks | Basis |
|-------|----------------------------------|-------|
| `,X 14` (transfer ptr) | the per-device transfer primitive. **SCSI = `SCSDISK`**; SMD/Winch/floppy = their own entry. The ONE field that differs per device type. | VERIFIED `LDA ,X 14` at 036101 |
| block / page number | **0** (page 0) - set by RXDIR `RADD CLD 0 DD` at 037651B | VERIFIED |
| `ABFUN` (function code) | built by masking the op-code in `,B 12`: `036135: fn = (op & 065) + 066` -> the driver's READ function (SCSDISK fn 0 for a page-0 read) | VERIFIED (mask bytes 036124-036130); exact numeric fn = INFERRED (op is a runtime input) |
| `MEMA1`/`MEMA2` (DMA target) | the reserved page-cache buffer; the **driver** writes `ABFUN`/`MEMA1`/`MEMA2` into the DEVICE datafield and derives the SCSI LBA + word count from READ CAPACITY. RCBLO does NOT compute the LBA or byte count. | VERIFIED (RCBLO passes buffer+block only) / INFERRED (driver fills MEMA/ABFUN) |
| what `,X 14` dispatches to | for SCSI: `SCSDISK -> SCLLD (INITO -> SCWAQ)`, the sole enqueue into the driver | INFERRED (NPL) / OPEN (runtime pointer, foreign segment) |

**Why the SCSI mount fails (from the RCBLO carve).** On the failing SCSI unit
the wire shows INQUIRY -> READ CAPACITY -> one last-block `READ(6)` (a
**function-42 control-record read**, disk init) and then **silence** - no page-0
READ and no WRITE. `SCWAQ` stays empty, and work enters the driver **only**
through `SCLLD -> INITO -> SCWAQ`; an empty `SCWAQ` therefore proves RCBLO's
`JPL I ,B 10` for block 0 **never executed**. So the page-0 read was never even
enqueued: the abort is **upstream of 036135** (either the resident
connect/init overlay never advanced from the control-record read to
`CHDSI/RXDIR`, or RCBLO took an early exit before the dispatch). On SMD/
Winchester/floppy the same `JPL I ,B 10` reaches a driver that DOES enqueue the
page-0 read, so the mount completes. The exact fault instruction is **OPEN** from
static bytes; a live DAP break at `CHDSI 037763` / `RXDIR 037643` / `RCBLO
035766` settles it (see [`../RCBLO/README.md`](../RCBLO/README.md) section 4).

---

## 4. Self-heal + interlock notes (from CHDSI)

- **Checksum** = plain 16-bit additive sum of ext-info words 1..7 (`ADD ,X 0`
  loop, 040011B). NOT XOR. VERIFIED; identical loop in `WXDIR` (037716B).
- **Bad/zero checksum does NOT reject the mount** - CHDSI zero-fills the 8 words,
  writes the geometry-derived capacity, and falls through to stamp+write-back
  (040063-040077B). Consequence: a garbage page-0 read surfaces as a *write*
  failure or a re-fail, not a checksum error. VERIFIED.
- **Owner interlock**: reject only when flag bit15 set AND owner != 0 AND owner
  != entering system (040110-040117B). VERIFIED (control flow); exact reject code
  INFERRED (032B/034B).
- **Stamp**: owner := entering system (word 5), flag bit15 := 1 (word 4), then
  `WXDIR` recomputes the checksum and writes page 0 back (040121-040127B). VERIFIED.

---

## 5. Error codes surfaced by ENDIR (VERIFIED `SAA` immediates)

| Code | Meaning | Raised at | Evidence |
|------|---------|-----------|----------|
| 147B | Device unit reserved for special use | 0140254B (`SAA 147`) after MON 124 fails | VERIFIED |
| 145B | Illegal on tape device | 0140261B (`SAA 145`) device-type bit | VERIFIED (bit = INFERRED) |
| 42B  | Main directory not last one released | 0140315B (`SAA 42`) | VERIFIED (SAA) / INFERRED (branch) |
| 32B  | Directory entered | 0140370B (`SAA 32`) already-entered guard | VERIFIED |
| 35B  | Master block transfer error | 037747B (`SAA 35`) in WXDIR (page-0 write failure) | VERIFIED |

Driver-layer codes (232B/141B/224B/252B via `SCDTS`) belong to the SCSI driver
and are documented in
[`../../../../../../SINTRAN/Filesystem/DEBUG-scsi-enter-directory.md`](../../../../../../../SINTRAN/Filesystem/DEBUG-scsi-enter-directory.md).

---

## 6. VERIFIED / INFERRED / OPEN summary

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `ENDIR 0140176` entry `021030`; calls GDIRA (0140244), MON 124 (0140252), CHDSI (0140402) | VERIFIED (dd) |
| 2 | `GDIRA 030225` leaf: datafield = base + index*4 (`MPY 4`,`EXIT`) | VERIFIED (dd) |
| 3 | `CHDSI 037763` calls RXDIR `[0040143]=037643`, GSIZE `[0040144]=037101`, WXDIR `[0040157]=037702` | VERIFIED (dd) |
| 4 | `RXDIR 037643` sets block 0 (`RADD CLD 0 DD` 037651) and calls RCBLO `[037675]=035766` | VERIFIED (dd) |
| 5 | Device transfer = `RCBLO` `JPL I ,B 10` via datafield `,X 14` (036101/036135) | VERIFIED (dd, ../RCBLO) |
| 6 | ENTER-DIRECTORY issues exactly one MON call: `MON 124` (PRSRV) | VERIFIED (grep of carved listing) |
| 7 | `MON 124 -> MCTAB[124]=037076 = PRSRV`; MCTAB validated on RDISK/MAGTP slots | VERIFIED (dd MCTAB + L07 symbols) |
| 8 | PRSRV/RESRV/PRLS/RELES bodies are a resident overlay, NOT the 006-S3FS bytes at those addrs (GSIZE overlaps) | VERIFIED (overlay), body OPEN |
| 9 | Hand-off contract: block 0, fn=(op&065)+066, DMA=cache buffer, `,X 14`=driver | VERIFIED (dispatch bytes) / INFERRED (numeric fn, MEMA fill) |
| 10 | `,X 14` -> SCSDISK -> SCLLD for SCSI | INFERRED (NPL) / OPEN (runtime pointer, foreign seg) |
| 11 | SCSI failure = page-0 read never enqueued (SCWAQ empty); abort upstream of 036135 | VERIFIED (ground truth) / OPEN (exact instruction - needs DAP) |

**Provenance.** Carved `006-S3FS` L07 bytes (`ENDIR 0140176`, `GDIRA 030225`,
`CHDSI 037763`, `RXDIR 037643`, `WXDIR 037702`, `RCBLO 035766`, `GSIZE 037101`),
load base 26000B; `MCTAB @ 005620B` from `044-S3IDPIT.bin` (load base 4000B);
symbols `SINTRAN/NPL-SOURCE/SYMBOLS/L07/FILSYS-SYMBOLS.SYMB.TXT`; driver logic
(different revision, INFERRED) `IP-P2-SCSI-DISK.NPL` / `IP-P2-SCSI-DRIV.NPL`.

## See also
- [`../RCBLO/README.md`](../RCBLO/README.md) - the cache-block dispatcher + the "no page-0 read" analysis.
- [`../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md) - the narrative end-to-end trace.
- [`../../segments-ref/006-S3FS/006-S3FS.asm`](../../segments-ref/006-S3FS/006-S3FS.asm) - the whole-segment listing.
