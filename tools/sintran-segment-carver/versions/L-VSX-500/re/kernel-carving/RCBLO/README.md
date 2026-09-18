# RCBLO - the disk-cache block manager, and why `@ENTER-DIRECTORY` never reads page 0

Carved analysis of **`RCBLO = 035766B`** (SINTRAN III VSX/500 **L07**, segment
`006-S3FS`, load base **26000B**), the disk-buffer-cache routine that turns a
filesystem "read page 0" request into a device transfer. This folder closes the
OPEN boundary that [`enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md)
Section 4.2 left at the `JPL I ,B 10` device dispatch, and explains why the mount
`@ENTER-DIRECTORY ,,DISC-SCSI-1,0` issued INQUIRY -> READ CAPACITY -> one READ(6)
of the last block and then went silent, never reading page 0.

**RESOLVED (2026-07-14, VERIFIED LIVE):** the root cause was a RetroCore ND-100
CPU-emulation bug in the `RDIV` (141600) opcode - on overflow it early-returned
without writing the A/D result registers, so the mount's geometry-check division
read a zero quotient and aborted with error 243B **before** block 0 was read. It
was NOT a SINTRAN bug. Full detail and the fix are in Section 4. The static carve
below correctly narrowed the fault to "an early exit before RCBLO's `JPL I ,B 10`
dispatch, before any page-0 device transfer"; the decisive step was running the
`RDIV` opcode on a reference microcode emulator. (Which routine holds the faulting
`(UHLIM/2)/divisor` division - RCBLO's geometry check, CHDSI, or the connect/init
overlay - was NOT pinned to a carved address; the fix did not require it.)

**Evidence grades.** VERIFIED = re-read from the carved `006-S3FS.bin` bytes
(offsets reproduced with dd/python; byte offset = `(addr - 26000B)*2` decimal).
INFERRED = reasoned from bytes + architecture, not one decisive instruction.
OPEN = crosses into an uncarved resident overlay or depends on runtime state.

All addresses/values are **octal**. Disassembly:
[`RCBLO.ASM`](RCBLO.ASM); pseudo-code: [`RCBLO.pseudo.c`](RCBLO.pseudo.c).

---

## 0. First result: RCBLO is NOT a foreign overlay - it is resident in 006-S3FS

The task framed `RCBLO` as a "resident overlay" whose real body had to be
resolved among the many segments that have non-zero bytes at `035766B`
(116/117-S3ERWD, 104/105-S3NKSE, 070/071-S3SM, 065/066-SIPIT, ...). It is not.
**RCBLO's true body is in `006-S3FS`**, proven by sibling coherence:

- `035766B` opens with `021066 STD I 66` - a real link-saving routine prologue,
  immediately followed by a frame `SAB 17`. VERIFIED byte `021066`.
- Its **siblings are parallel cache routines** at consecutive entries:
  `WBLOC 036221B` (`021116 STD I`), `WCBLO 036357B` (`021114 STD I`),
  `WTAPE 036511B` (`021067 STD I`) - all the same prologue idiom, all
  cache-block writers next to the cache-block reader. VERIFIED (labels +
  bytes from FILSYS-SYMBOLS L07).
- The **cross-references resolve inside 006-S3FS**: RXDIR's literal pointer
  `[037675] = 035766` (RCBLO), CHDSI's `[040143] = 037643` (RXDIR),
  `[040144] = 037101` (GSIZE), RCBLO's own `[036220] = 035240` (CL1DB),
  `[036056] = 037101` (GSIZE). All VERIFIED by dd.

That is the discriminator the skill demands (2-3 siblings landing on parallel
entries). In `006-S3FS` they all do. The overlay concern was a false lead: the
address that IS runtime-bound to a foreign resident segment is the **dispatch
target** `datafield word ,X 14`, not RCBLO itself (Section 3).

---

## 1. The call chain, closed end to end

Every edge below is byte-verified except the final `,X 14 -> SCSDISK -> SCLLD`
hop, which is a runtime pointer binding (INFERRED from NPL, see Section 3).

```
@ENTER-DIRECTORY ,,DISC-SCSI-1,0
   |  (command interpreter, upstream segment - OPEN)
   v
ENDIR 140176B                                         [006-S3FS]
   |  140402: JPL I 33 -> [140435]=037763
   v
CHDSI 37763B  check/enter directory                   [006-S3FS]
   |  040000: JPL I 143 -> [040143]=037643            (read page-0 ext-info)
   |  040023: JPL I 121 -> [040144]=037101  GSIZE      (in-core size, no I/O)
   v
RXDIR 37643B  read page-0 ext-info via cache          [006-S3FS]
   |  037651: RADD CLD 0 DD           (block number := 0)
   |  037652: JPL I 23 -> [037675]=035766
   v
RCBLO 35766B  reserve/read cache block 0              [006-S3FS]
   |  035773: JPL I 63 -> [036056]=037101  GSIZE       (in-core size, no I/O)
   |  cache search 036031-036042  (HIT -> success, no read)
   |  036100: LDX ,B 11 ; 036101: LDA ,X 14 ; 036102: STA ,B 10
   |  036135 / 036142 / 036167 / 036174:  JPL I ,B 10  (RUNTIME target = ,X 14)
   v
SCSDISK  "level-11 SCSI disk transfer"   fn 0=READ ... 42=READ FORMAT
   |     (resident driver segment - NOT carved in 006-S3FS)
   v
SCLLD 67160B   enqueue work: INITO -> SCWAQ           (only entry to the driver)
   v
SCINT / SELEC  NCR 5386 command sequence on the IOX bus
```

This meets the two existing analyses: `enter-directory.md` (down to `RCBLO`'s
`JPL I ,B 10`) and the SCSI-driver notes (`SCLLD` upward). The junction is the
datafield transfer pointer `,X 14`.

---

## 2. What RCBLO does (fields, function code, block arithmetic)

VERIFIED from the bytes (see [`RCBLO.ASM`](RCBLO.ASM) for the annotated listing):

1. **Prologue** (035766-035774): save link, build frame, call the resident
   reserve/prologue `003752B`, then call **GSIZE 037101B**. `[036056]=037101`
   is VERIFIED - RCBLO's prologue really does invoke GSIZE. GSIZE reads the
   **in-core disk-parameter tables** (helpers `050124/050220/050223B`, bounds
   check to error `174B`) and computes a size with `RMPY` (037134); it issues
   **no device transfer** (no `JPL I ,B` dispatch anywhere in GSIZE). VERIFIED.

2. **Cache search** (036005-036042): the requested 32-bit block number (from
   `,B 6`, set by RXDIR to **0**) is compared against a candidate buffer's
   stored `block-hi ,X 5` / `block-lo ,X 6` / `device ,X 12`. On a full match
   it is a **HIT** (036043-036053) and RCBLO returns the cached buffer with
   **no device read**.

3. **Transfer dispatch** (036100-036174) on a miss:
   - `LDX ,B 11` (unit descriptor), `LDA ,X 14` (**transfer function pointer**),
     `STA ,B 10`. VERIFIED - this is the datafield word 14 the driver hangs off.
   - Four dispatch sites `135410 JPL I ,B 10` each build a device **function
     code** from the operation code in `,B 12`:
     - 036135: `fn = (op & 065) + 066`  (primary transfer / READ)
     - 036142: `fn = (op & 054) + 063`  (alternate)
     - 036167: `fn = (op & 032) + 066`
     - 036174: `fn = (op & 022) + 063`
     The exact op-code value in `,B 12` at mount time is a **runtime input**, so
     which numeric SCSI function each site emits is INFERRED, not byte-fixed.
   - `036177` is the error epilogue: it releases the buffer via **CL1DB
     (`[036220]=035240`, VERIFIED)** and returns the error up to RXDIR.

4. **DMA count / memory address / page->LBA:** RCBLO passes the **block number**
   and buffer to the driver; it does **not** compute the SCSI LBA or the byte
   count itself. Those are derived inside the driver from READ CAPACITY via the
   `SUSI1/2/3` shift instructions. So the page(2048B)->block(1024B) conversion
   is a **driver** concern, not an RCBLO concern (bears on Section 4d).

---

## 3. The dispatch target `,X 14` is the OPEN boundary (correctly)

`036101 LDA ,X 14` loads a **runtime pointer** that device configuration binds
to the driver serving `DISC-SCSI-1`. For a SCSI disk that is **SCSDISK**, the
"LEVEL 11 ROUTINE TO PERFORM TRANSFERS ON SCSI DISKS"
(`SINTRAN/NPL-SOURCE/NPL/IP-P2-SCSI-DISK.NPL`, function table: 0=READ, 1=WRITE,
4=SEEK, 42=READ FORMAT/read control record, 75=INQUIRY). SCSDISK enqueues work
through **SCLLD** (`INITO -> SCWAQ`). The pointer VALUE is not in the static
`006-S3FS` bytes, and SCSDISK/SCLLD are in a resident driver segment not carved
here - so this hop is INFERRED (NPL logic) / OPEN (L bytes). This is the same
boundary `enter-directory.md` 4.2 named; it is genuinely a runtime binding, not
a carving gap that more disassembly of 006-S3FS would close.

---

## 4. THE ANSWER: why no page-0 read is issued - RESOLVED (RDIV emulator bug)

**Verdict: SOLVED and FIXED, VERIFIED LIVE 2026-07-14. The fault is NOT in
SINTRAN and NOT a static-carve question - it was a RetroCore ND-100 CPU
emulation bug in the `RDIV` (141600) instruction.** The static carve below was
correct in every structural conclusion (4a-4c): the abort happened before any
page-0 device transfer was issued. What it could not see - because it depended on
runtime register state, exactly as 4d/THE ONE CHECK said - was that a
geometry-check division produced a wrong quotient due to a defective opcode. (The
static carve listed two candidate loci in 4d; the fix evidence does not, by
itself, pin the faulting division to either one - see the note in 4d below.)

### THE ROOT CAUSE (VERIFIED LIVE)
The SCSI mount runs a geometry check of the form `(UHLIM/2)/divisor` using the
ND-100 `RDIV` (141600) instruction, then tests the quotient with
`SKP IF DD EQL 0`. With `divisor = 1` (T=1) and `UHLIM/2 = 61036`, the quotient
**61036 overflows** the signed 16-bit result (|quotient| >= 32768).

- **ND-100 hardware behaviour (VERIFIED on a microcode emulator by Ronny):**
  `RDIV` on overflow STILL writes `A = low 16 bits of the quotient` and
  `D = remainder`, THEN sets `STS.Z`. The ND-100 Reference Manual
  (ND-06.014.2A, RDIV p.52) says only "if the division causes overflow, the
  error indicator Z is set to one" and lists "Affected: (A),(D)" - it does NOT
  say the result registers are left untouched.
- **The RetroCore bug:** `RDIV()` in
  `E:\Dev\Repos\Ronny\RetroCore\Emulated.HW\ND\CPU\ND100\Instructions.RegisterOperations.cs`
  did `if (Math.Abs(result) >= 32768) { STS.Z = true; return; }` - it
  early-returned WITHOUT writing A/D, leaving `A = 0` (stale). SINTRAN then read
  a **zero quotient** at `SKP IF DD EQL 0` and aborted the mount with error
  **243B before block 0 was ever read**. That abort is the "silence" this whole
  document was tracking - an early error exit before any page-0 transfer was
  dispatched (VERIFIED: no read, no write, SCWAQ empty). Whether the faulting
  division lives in RCBLO's geometry check (4d locus 2), in CHDSI, or in the
  connect/init overlay (4d locus 1) was NOT pinned to a carved address; the
  live fix did not require distinguishing them.

### THE FIX (VERIFIED LIVE)
Set `STS.Z` on overflow but ALWAYS fall through and write `A = low-16 quotient`
and `D = remainder`. After the fix, `@ENTER-DIRECTORY,,DISC-SCSI-1,0` **mounts**;
`@DIR` shows `DISC-SCSI-1 UNIT 0 ** 125 Mb ** : PACK-ONE ... OUT OF 61036 PAGES`
- and **61036 = UHLIM/2**, exactly the quotient `RDIV` now writes. The page-0
read is issued, block 0 is read, the directory mounts. SCSI ENTER-DIRECTORY
saga CLOSED.

### PROCESS NOTE (why the static carve stopped at UNDETERMINED)
The divisor (T=1), `UHLIM` (122072), and the disk were all correct - the fault
was one opcode. The static 006-S3FS bytes genuinely could not see it: the bug
lived in the emulated CPU, not in any SINTRAN instruction, and only surfaced
with the specific runtime register values. THE ONE CHECK THAT SETTLES IT (below)
named the right experiment - "run it and observe which branch is taken" - and
the decisive form of that experiment turned out to be *running the `RDIV` opcode
itself on a reference microcode emulator*, which took two minutes and proved it.

Sections 4a-4d and THE ONE CHECK below are retained as the correct structural
narrowing that led here; read them as the (validated) reasoning, not as an open
question.

Here is what the bytes + the verified ground truth established (all still true):

### 4a. The wire's last-block read is function 42 (control record), not page 0
The observed INQUIRY -> READ CAPACITY -> READ(6) of the last LBA (129311) is a
**function-42 "READ FORMAT" operation**: `IP-P2-SCSI-DISK.NPL` 057170
`*LDDTX 10 % ADDRESS OF CONTROLL RECORD`, then FINEX (057261+) validates it
(XOR loop, `NPART`, `L<=2 OR L>NCOPA` guard) and sets `UHLIM`. This is disk
**initialization / geometry discovery**, a **separate operation** that runs
**before** `CHDSI` ever reads block 0. VERIFIED (NPL logic) + consistent with
the ground-truth disk-layer trace (control record NPART=8, XOR=0, UHLIM set,
T:=0 success). So the last-block read is NOT the page-0 read and NOT a failure.

### 4b. The page-0 read was never *enqueued*
Ground truth (driver exoneration): after the control-record read completes, the
driver returns success and **SELEC finds SCWAQ empty**. Work enters the driver
**only** through `SCLLD -> INITO -> SCWAQ`. An empty SCWAQ therefore proves that
**RCBLO's `JPL I ,B 10` transfer dispatch for block 0 never executed** - had it
run, SCLLD would have enqueued the read and SCWAQ would be non-empty. So the
abort is **upstream of RCBLO's dispatch (036135)**.

### 4c. It was an *error* return, not the rebuild-writeback
The wire shows **silence** after the control record - no page-0 READ and no
WRITE. CHDSI's bad/zero-checksum path would issue a **write-back** via WXDIR
(enter-directory.md 5.3). No write means CHDSI never reached that path: the
mount took an **error return** with no I/O. Combined with 4b, the page-0 read
(`CHDSI -> RXDIR -> RCBLO`) aborted **before** any device transfer.

### 4d. Where the abort is - two static-indistinguishable loci
1. **Upstream of CHDSI (most likely):** the resident mass-storage connect/init
   layer that issued function 42 succeeds at reading the control record but does
   **not** then hand control to `CHDSI/RXDIR` (or returns an error from the init
   completion). `CHDSI` is then never entered, so `RCBLO` is never called with
   block 0. This overlay is not carved in `006-S3FS`.
2. **Inside RCBLO before 036135:** RCBLO is reached with block 0 but returns
   early - via the GSIZE prologue call (035773, e.g. a geometry mismatch using
   the just-set `UHLIM`), the geometry check at 036103-036117 (`SAA 100B`
   error), or a spurious cache HIT (036043-036053) that returns a stale buffer.
   All of these return **without** a `JPL I ,B 10`, matching 4b/4c.

Static 006-S3FS bytes cannot choose between (1) and (2): both are byte-present
paths, and which executes depends on runtime state (`UHLIM`, cache contents,
the `,X 14` binding) that is not in this segment.

### THE ONE CHECK THAT SETTLES IT
Run a live nd100x/DAP trace of the failing `@ENTER-DIRECTORY` and set three
breakpoints at their mapped absolute addresses: **CHDSI 37763B**, **RXDIR
37643B**, **RCBLO 35766B**.
- **If CHDSI is never hit** -> the abort is locus (1): the mass-storage
  connect/init overlay does not advance from the function-42 control-record read
  to the page-0 directory read. Carve that overlay next (the driver segment that
  owns `,X 14` / SCSDISK / disk-start), not 006-S3FS.
- **If RCBLO is hit with block 0** -> the abort is locus (2): single-step from
  035766 and observe which branch (GSIZE fail at 035774, geometry error at
  036117, cache HIT at 036053, or CL1DB error at 036203) is taken **before**
  reaching `036135 JPL I ,B 10`. That instruction address is THE ANSWER.

---

## 5. Factor-2 hypothesis (page 2048B vs SCSI block 1024B): REFUTED as the cause

The leading hypothesis was a unit mismatch: filesystem page = 1024 words =
2048 bytes, SCSI block = 1024 bytes, so page 0 = two SCSI blocks; and with
`blockSize=1024` the driver's `SUSI1/2/3` shifts come out as `SAD 0` (no shift).

**Refuted as the cause of THIS bug (the absence of a page-0 read):** a wrong
shift factor would make the driver issue a read of the **wrong size or wrong
LBA** - i.e. a page-0 read that transfers garbage. The observed symptom is the
**complete absence** of any page-0 read (SCWAQ empty, Section 4b). A factor-2
error cannot explain "no read issued"; it can only corrupt a read that *is*
issued. Since no read is issued, the shift math is never even reached.
(Factor-2 may still be a **latent, separate** defect that would bite *after*
locus (1)/(2) is fixed and the page-0 read finally reaches the driver;
`SUSI1/2/3` = `SAD 0` at blockSize=1024 is real - it is just not this bug.)
**Verdict: REFUTED for the no-read abort; UNDETERMINED as a latent read-content
defect.**

---

## 6. VERIFIED / INFERRED / OPEN summary

| # | Claim | Verdict |
|---|-------|---------|
| 1 | RCBLO body is resident in `006-S3FS` (siblings WBLOC/WCBLO/WTAPE, cross-refs resolve) | VERIFIED |
| 2 | `RCBLO 035766B` entry `021066 STD I 66`; dispatches `135410 JPL I ,B 10` at 036135/036142/036167/036174 | VERIFIED (dd) |
| 3 | RXDIR->RCBLO `[037675]=035766`; CHDSI->RXDIR `[040143]=037643`; RCBLO prologue->GSIZE `[036056]=037101`; error->CL1DB `[036220]=035240` | VERIFIED (dd) |
| 4 | `,X 14` = datafield transfer pointer; `036101 LDA ,X 14 ; 036102 STA ,B 10` feeds the four dispatches | VERIFIED |
| 5 | GSIZE 037101B reads in-core parameter tables + `RMPY`; no device transfer | VERIFIED |
| 6 | Dispatch target `,X 14` -> SCSDISK -> SCLLD (INITO/SCWAQ) | INFERRED (NPL) / OPEN (L bytes: runtime pointer, foreign segment) |
| 7 | The wire's last-block READ(6) is function 42 (READ FORMAT / control record), a separate op before CHDSI | VERIFIED (NPL logic + ground-truth disk-layer trace) |
| 8 | Page-0 read never enqueued (SCWAQ empty) => RCBLO's `JPL I ,B 10` for block 0 never executed | VERIFIED (ground truth) + INFERRED (SCLLD is sole enqueue) |
| 9 | Mount took an error return (no read, no write) before any page-0 transfer | VERIFIED (silence) / INFERRED (which return) |
| 10 | Exact fault: a geometry-check division `(UHLIM/2)/divisor` read a zero quotient and aborted (243B) before any page-0 transfer, because RetroCore `RDIV` early-returned on overflow without writing A/D | RESOLVED + FIXED, VERIFIED LIVE 2026-07-14 (Section 4). NOT a SINTRAN bug - a CPU-emulation bug. Which routine holds that division = not pinned (INFERRED) |
| 11 | Factor-2 (page/block shift) causes the no-read abort | REFUTED (would corrupt a read, not remove it) |

**Provenance.** Carved `006-S3FS` SINTRAN L07 bytes (`RCBLO 035766B`,
`WBLOC 036221B`, `WCBLO 036357B`, `WTAPE 036511B`, `GSIZE 037101B`,
`RXDIR 037643B`, `CHDSI 37763B`, `CL1DB 035240B`), load base 26000B,
`sha256(006-S3FS.bin)=b4a563d0...`; symbols `SINTRAN/NPL-SOURCE/SYMBOLS/L07/
FILSYS-SYMBOLS.SYMB.TXT`; driver logic (different revision, INFERRED)
`SINTRAN/NPL-SOURCE/NPL/IP-P2-SCSI-DISK.NPL` (function 42 / control record,
SCSDISK) and `IP-P2-SCSI-DRIV.NPL` (SCLLD); ground-truth driver/disk-layer
exoneration per the mount-debug session.

## See also
- **Root-cause fix (RetroCore ND-100 CPU):** `RDIV` (141600) overflow now always
  writes A/D before setting Z, in
  `E:\Dev\Repos\Ronny\RetroCore\Emulated.HW\ND\CPU\ND100\Instructions.RegisterOperations.cs`.
  This is the actual fix that closed the SCSI ENTER-DIRECTORY mount failure (Section 4).
- [`../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md) - the mount trace this folder extends (Section 4.2 boundary now closed/narrowed).
- [`../../../../../../SINTRAN/Filesystem/code-logic/scsi-mount-geometry.md`](../../../../../../../SINTRAN/Filesystem/code-logic/scsi-mount-geometry.md) - the last-block = control-record framing (corrected).
- [`../../../../../../SINTRAN/Filesystem/DEBUG-scsi-enter-directory.md`](../../../../../../../SINTRAN/Filesystem/DEBUG-scsi-enter-directory.md) - the 243B "accounting file" red herring.
