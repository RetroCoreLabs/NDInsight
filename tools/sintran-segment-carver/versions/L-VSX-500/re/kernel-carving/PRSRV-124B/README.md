# MON 124B PRSRV (ForceReserve) - byte-verified carve + the block-0 reserve flow

Carve of **MON 124B `PRSRV`** (ForceReserve) in SINTRAN III VSX/500 **L07**
(running system L-VSX-500, symbols L07), and of the **read-modify-write of block
0** that `@ENTER-DIRECTORY` uses to stamp a directory as "entered", with the
exact point where the SCSI path diverges from SMD/Winchester/floppy.

**Evidence grades.** VERIFIED = re-read from the carved `.bin` with `dd` /
`nd100-dis` (byte offset in the `.bin` = `(addr_oct - loadbase) * 2`, decimal).
INFERRED = reasoned from bytes + manual/NPL. OPEN = crosses into an uncarved
low-resident overlay or depends on runtime state. All addresses/values **octal**.

Deliverables:
- [`PRSRV-124B.ASM`](PRSRV-124B.ASM) - commented disassembly of the PRSRV/RESRV/
  EXECC/PRLS/RELES family (from `071-S3SM`) + the block-0 WXDIR write-back excerpt.
- [`PRSRV-124B.pseudo.c`](PRSRV-124B.pseudo.c) - readable pseudo-C for PRSRV and
  the block-0 read -> stamp -> write-back reserve flow.

Cross-linked carves:
[`../ENTER-DIRECTORY/`](../ENTER-DIRECTORY/) (device-agnostic mount path),
[`../RCBLO/`](../RCBLO/) (cache-block dispatcher + "no page-0 read" analysis),
[`../SCSI-DRIVER/`](../SCSI-DRIVER/) (SCSDISK / SCLLD), and narrative
[`../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md).

---

## (a) Which overlay holds PRSRV - and the sibling-coherence proof

**Dispatch is byte-verified.** `MON N` goes `ENT14 -> GOTAB[N]=MFELL -> CALLP ->
MCTAB[N] -> worker` (the skill's MON model). The monitor-call table is
**`MCTAB @ 005620B`** in `044-S3IDPIT` (load base `4000B`). I re-`dd`'d the four
reserve/release slots:

| Slot | byteoff | bytes | = addr | Symbol (L07 SYMBOL-1-LIST) |
|------|---------|-------|--------|-----------------------------|
| MCTAB[122B] | 1988 | `3e 43` | `037103B` | `RESRV` (ReserveResource) |
| MCTAB[123B] | 1990 | `3e 6e` | `037156B` | `RELES` (ReleaseResource) |
| MCTAB[124B] | 1992 | `3e 3e` | `037076B` | **`PRSRV` (ForceReserve)** |
| MCTAB[125B] | 1994 | `3e 67` | `037147B` | `PRLS` (ForceRelease) |

All four land **exactly** on the L07 SYMBOL-1-LIST addresses
(`PRSRV=037076`, `RESRV=037103`, `PRLS=037147`, `RELES=037156`). **VERIFIED.**

**Which overlay's bytes are these?** SYMBOL-1-LIST is the resident-monitor
symbol world. I scanned all 60 carved segments at the four sibling addresses
(`re/segments-ref/`); the only segments with byte-identical, non-zero code there
are, all with load base `30000B` and symbol file SYMBOL-1-LIST:

- **`071-S3SM`** (System Monitor)      <- authoritative resident home
- `070-S3SSM` (System Monitor, save)   identical bytes
- `003-S3CP`  (Command segment)        identical bytes

At `037076..037170` these three are word-for-word equal:
`PRSRV=044322 RESRV=036776 EXECC=045053 PRLS=142200 RELES=146147` (VERIFIED
cross-segment scan). Since the monitor level runs with the System Monitor
mapped, **`071-S3SM` is the overlay**; `003-S3CP` carries the same bytes, so a
carve read out of `003-S3CP` is reading the *correct* bytes. No other overlay
(`006-S3FS`, commoncode, the ERWD/NKSE/U110 segments, ...) produces a coherent
reserve family at these addresses - they land mid-loop or on zeros.

**Sibling coherence:** `PRSRV/RESRV/PRLS/RELES` sit as a contiguous family
(`037076, 037103, 037147, 037156`) with the shared executor `EXECC=037110`
between them - a parallel entry cluster, exactly the discriminator the skill
requires. VERIFIED.

**Did the existing `122B-ReserveResource` folder use the wrong overlay?**
**No - it used `003-S3CP`, whose bytes are identical to the resident System
Monitor `071-S3SM`, so the BYTES are correct.** Two corrections to its
*interpretation*, though:

1. It described the whole `037103..037155` block as "the RESRV worker = a
   command-builder that calls MON 70 twice." That block is really **`EXECC`
   (037110B)**, a *shared* executor; `RESRV` is the 5-word entry stub in front
   of it. Minor mislabel, not a wrong overlay.
2. **PRSRV (124B) is NOT the same shape as RESRV.** PRSRV@037076 is a **2-word
   trampoline** that does not enter EXECC at all (see (c) below). So the
   command-builder story does not describe MON 124 PRSRV.

---

## (b) Full dependency tree of MON 124B (routines + addresses + further MONs)

```
MON 124B  ForceReserve
  -> ENT14 072167B  -> GOTAB[124]=MFELL 072114B -> CALLP 032201B     (MON model)
  -> MCTAB[124B] = 037076B = PRSRV                                    VERIFIED (dd)
       PRSRV @037076B  [071-S3SM, resident System Monitor]
         037076 LDA -56    ; A := MEM[037020] = 000003  (selector const) VERIFIED
         037077 JMP I 10   ; PC := MEM[037107] = 027417B = LEAV2         VERIFIED
       -> LEAV2 027417B    monitor "leave/return" routine  (SYMBOL-1-LIST)
                           BELOW the 30000B monitor window -> body OPEN

  Sibling reserve/release family (co-located; NOT on PRSRV's path, listed so the
  worker set is unambiguous):
    RESRV @037103B (MON 122B)  \
    PRLS  @037147B (MON 125B)   >  fall into the shared executor EXECC @037110B
    RELES @037156B (MON 123B)  /
       EXECC @037110B (== OTRAN)  builds a command line, scans it, and issues:
         037124 MON 70B  --.
         037154 MON 70B  --+->  MCTAB[070B] = 050673B = COMSB            VERIFIED (dd)
                                COMSB = the @-command interpreter worker
                                (family: UECOM 050701, UELOG 050726) [003-S3CP]
       EXECC helpers (low-resident, OPEN):
         037120 JPL I 45 -> [037165] = 004177B  (UCACH/DALTO)
         037157 JPL I 10 -> [037167] = 004116B  (ALTOF/SINAL)
```

**MON calls issued by the reserve family:** only **MON 70B (COMMND/CallCommand
-> COMSB)**, from the shared executor used by RESRV/PRLS/RELES. **PRSRV itself
issues no MON call** - it loads `3` and leaves via `LEAV2`. VERIFIED.

**Consequence that matters for the mount:** in this L07 build **MON 124 PRSRV is
effectively a pass-through** (constant-load + monitor leave); it does not run the
command executor and does not raise error `147B`. What the `3` encodes and any
work inside `LEAV2` is OPEN, but the practical result - *PRSRV returns cleanly on
every device type, SCSI included* - is what the failing-mount console confirms
(no `147B` printed; the mount proceeds past `MON 124`).

---

## (c) The block-0 read -> stamp -> write-back reserve flow (exact addresses)

**Important:** this "directory reserve" is a **different** reservation from
MON 124. MON 124 reserves the **device unit**; the block-0 stamp marks the
**directory** as entered/owned. Bodies are in `006-S3FS` (base `26000B`); fully
carved in [`../ENTER-DIRECTORY/`](../ENTER-DIRECTORY/) and
[`../RCBLO/`](../RCBLO/). The flow (all VERIFIED there; WXDIR re-checked here):

```
ENDIR 0140176   0140252: MON 124 PRSRV (device reserve; passes)
                0140402: JPL I 33 -> [0140435]=037763  CHDSI
CHDSI 037763    0040000: JPL I 143-> [040143]=037643   RXDIR   (READ block 0)
                0040023: JPL I 121-> [040144]=037101   GSIZE   (in-core size)
                stamp + 0040127: JPL I 30 -> [040157]=037702  WXDIR (WRITE block 0)
RXDIR 037643    037651: RADD CLD 0 DD          block number := 0
                037652: JPL I 23 -> [037675]=035766  RCBLO
RCBLO 035766    036101: LDA ,X 14              transfer fn ptr (SCSI=SCSDISK)
                036135: JPL I ,B 10            *** device READ of block 0 ***
```

Step by step:

1. **READ block 0.** `RXDIR` sets the block number to **0** (`037651 RADD CLD 0
   DD`, VERIFIED) and calls `RCBLO`, which on a cache miss dispatches the
   per-device transfer via datafield word `,X 14` (`036101 LDA ,X 14 ; 036135
   JPL I ,B 10`, VERIFIED). This is the read of the directory master block.
2. **Checksum + self-heal** (CHDSI, VERIFIED in ENTER-DIRECTORY sec 4): additive
   sum of ext-info words 1..7 (`ADD ,X 0` loop). A bad/zero checksum does **not**
   reject - CHDSI zero-fills the 8 words and writes the geometry-derived
   capacity, then falls through to the stamp.
3. **Owner interlock** (`040110-040117`, VERIFIED): reject only when flag bit15
   set AND owner != 0 AND owner != entering system (error 32B/34B, code INFERRED).
4. **STAMP** (`040121-040127`, VERIFIED): owner word := entering system, flag
   word bit15 := 1. This is the actual "reserve/enter" mark on the directory.
5. **WRITE block 0 back.** `WXDIR 037702B` recomputes the checksum (`037714-
   037721 ADD ,X 0` loop, `037722-037723` store, VERIFIED here by dd) and writes
   block 0 via `WCBLO` (`037727 JPL I 25 -> [037754]`). Failure raises
   **error 35B "Master block transfer error"** (`037747 SAA 35`, VERIFIED).

---

## (d) THE DIVERGENCE: where SCSI fails vs SMD/Winchester/floppy

**MON 124 PRSRV is NOT the divergence.** It is a pass-through in this build
(section (b)); it raises no `147B` and the failing SCSI console never shows
`147B`. The mount reaches `CHDSI`.

**The divergence is in the block-0 READ (step 1), the same seam the RCBLO carve
pinned:** on the failing SCSI run the per-device transfer for block 0 is **never
enqueued** - `SCLLD` (the sole entry that puts work on `SCWAQ`) is never called
for block 0, and `SCWAQ` stays empty. So `RCBLO`'s `036135 JPL I ,B 10` for
block 0 **never executed**: no page-0 READ and no page-0 WRITE ever hit the wire
(the write-back in step 5 is therefore never reached either). On SMD/Winchester/
floppy the same `JPL I ,B 10` reaches a driver that DOES enqueue the page-0 read,
so the read-modify-write completes and the directory is stamped. VERIFIED
(ground-truth SCWAQ-empty) / the exact fault **instruction** is OPEN from static
bytes.

**The one runtime check that settles the exact instruction** (from
[`../RCBLO/README.md`](../RCBLO/README.md) sec 4): live nd100x/DAP breakpoints at
`CHDSI 037763B`, `RXDIR 037643B`, `RCBLO 035766B`.
- **CHDSI never hit** -> the resident mass-storage connect/init overlay (which
  did INQUIRY + READ CAPACITY + the function-42 control-record READ) never
  advances to the directory read. Carve that overlay next, not `006-S3FS`.
- **RCBLO hit with block 0** -> single-step from `035766` and see which branch
  (GSIZE prologue at `035773`, geometry check `036103-036117`, or a spurious
  cache HIT `036043-036053`) returns **before** `036135 JPL I ,B 10`. That
  instruction is THE answer.

The factor-2 page(2048B)/block(1024B) shift is **REFUTED** as the cause here: it
would corrupt a read that *is* issued, not remove it; no read is issued
(RCBLO README sec 5).

---

## (e) The "APPROACHING END OF ACCOUNTING FILE" message

**Not on the ENTER-DIRECTORY error path.** VERIFIED: it is SINTRAN error
**243B (163 decimal)**, set in exactly one place -
`SINTRAN/NPL-SOURCE/NPL/RP-P2-ACCRT.NPL` (`243=:ERFL` when accounting records
pass the warning threshold), inside the **RT-accounting collector that runs at
logout**. `ENTER-DIRECTORY` never enters the accounting collector, never opens
`ACCOUNTS:DATA`, and never touches `ERFL`; there is no call edge from the mount
path to `RP-P2-ACCRT`. So the message is either a coincidental logout event or
(more likely) the genuine mass-storage read-error code (e.g. 141B transfer error
via `SCDTS`) **mis-rendered** by the emulator's error-to-string table. Full
analysis:
[`../../../../../../SINTRAN/Filesystem/DEBUG-scsi-enter-directory.md`](../../../../../../../SINTRAN/Filesystem/DEBUG-scsi-enter-directory.md).
**Verdict: red herring - not raised by the mount itself.**

---

## (f) VERIFIED / INFERRED / OPEN

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `MCTAB[124B]=037076=PRSRV`, `[122B]=037103=RESRV`, `[123B]=037156=RELES`, `[125B]=037147=PRLS` | VERIFIED (dd) |
| 2 | Worker bodies resident in System Monitor `071-S3SM` (== `070-S3SSM` == `003-S3CP` bytes), base 30000B | VERIFIED (cross-seg scan) |
| 3 | `PRSRV@037076` = 2-word trampoline: `A:=MEM[037020]=3`; `JMP I 10 -> [037107]=027417B` | VERIFIED (dd of all 3 words) |
| 4 | `027417B = LEAV2`, a monitor leave/return routine; body below the 30000B window | VERIFIED (symbol) / body OPEN |
| 5 | PRSRV issues no MON call; is a pass-through (no `147B`) on every device incl. SCSI | VERIFIED (bytes + no-147B console) / meaning of `3` INFERRED |
| 6 | Siblings RESRV/PRLS/RELES fall into shared executor `EXECC 037110` which issues `MON 70B` x2 | VERIFIED (dd) |
| 7 | `MON 70B -> MCTAB[070]=050673=COMSB` (@-command interpreter) | VERIFIED (dd) |
| 8 | EXECC helpers `[037165]=004177B (UCACH)`, `[037167]=004116B (ALTOF)` | VERIFIED (ptrs) / bodies OPEN |
| 9 | Block-0 RMW: RXDIR reads blk0 (blk:=0 @037651), stamp @040121-040127, WXDIR writes back @037702 (err 35B @037747) | VERIFIED (dd; ../ENTER-DIRECTORY) |
| 10 | Directory reserve (block-0 stamp) is SEPARATE from device reserve (MON 124) | VERIFIED (distinct code paths) |
| 11 | SCSI divergence = block-0 device READ never enqueued (SCWAQ empty); MON 124 is not the fault | VERIFIED (ground truth) / exact instr OPEN (DAP settles) |
| 12 | Accounting message 243B is not on the mount path (RT-accounting, logout only) | VERIFIED |

**Provenance.** `071-S3SM.bin` (PRSRV family, base 30000B), `044-S3IDPIT.bin`
(MCTAB, base 4000B), `006-S3FS.bin` (CHDSI/RXDIR/WXDIR, base 26000B), all under
`tools/sintran-segment-carver/versions/L-VSX-500/segments/`; symbols
`SINTRAN/NPL-SOURCE/SYMBOLS/L07/SYMBOL-1-LIST.SYMB.TXT`; manual
`Reference-Manuals/ND-860228-2-EN SINTRAN III Monitor Calls.md` (ForceReserve
124B / ReserveResource 122B); accounting `SINTRAN/NPL-SOURCE/NPL/RP-P2-ACCRT.NPL`.
Disassembly via `nd100-dis` (WSL, little-endian input).

## See also
- [`../ENTER-DIRECTORY/README.md`](../ENTER-DIRECTORY/README.md) - device-agnostic mount path, error codes.
- [`../RCBLO/README.md`](../RCBLO/README.md) - the block-0 dispatch seam + the settling DAP check.
- [`../SCSI-DRIVER/README.md`](../SCSI-DRIVER/README.md) - SCSDISK / SCLLD enqueue.
