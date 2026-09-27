# ND-500 <-> ND-100 — Status, Evidence Register, and Master Index

**Full path:** `SINTRAN/ND500/ND500-STATUS-AND-INDEX.md`

**THIS IS THE ND-500 STATUS DOCUMENT OF RECORD.** It is the single place that answers
"what do we actually know about ND-500 <-> ND-100 communication, and how well do we know it?"

**Goal driving this work:** recreate the ND-100 <-> ND-500 communication in the RetroCore emulator.
**Version under analysis:** L-VSX-500 (L07).
**Last status refresh:** 2026-08-11.

**Parent status doc:** [`..\CARVING-HANDOFF.md`](../CARVING-HANDOFF.md) — the overall carving/MON effort.
This file is the ND-500-specific view; the parent owns ND-100 dispatch and segment status.

**Maintenance rule:** see section 8. Update this file whenever an ND-500 MON call, segment, symbol,
or NPL routine is analysed. **All output goes under `E:\Dev\Ronny\NDInsight\` — never the D: drive.**

---

## 000. 2026-07-31 — LINKAGE-LOADER install: swap file created, and the blocker moves to RECOVER-DOMAIN

**Full write-up:**
[`..\ND5000\NLL-INSTALL-SWAPFILE-UNBLOCKED-5SWAP-PROTECT-VIOLATION-2026-07-31.md`](../ND5000/NLL-INSTALL-SWAPFILE-UNBLOCKED-5SWAP-PROTECT-VIOLATION-2026-07-31.md)

Three blockers in series on the ND-500 LINKAGE-LOADER install; the first two are FIXED.

1. **`@SET-AVAIL` must run after login and BEFORE `@ND-500`** [V, live]. Adding it changed
   RECOVER-DOMAIN's outcome immediately. **Consequence: every ND-500 result the octobus boot
   harness produced before 2026-07-31 was taken from a machine that had not been made
   available** - including the "ACCP was terminated" banner readings.
2. **This pack has NO ND-500 swap file**, so no domain could ever load ("SWAPPING SPACE NOT
   AVAILABLE" = error 553). Created per ND-30.003.007 section 3.3.9 and verified by
   `LIST-SWAP-FILE-INFO`: `give-user-space system 8000`, `create-file swap-file-0:swap` at
   5000 pages, `define-swap-file`. NOTE the harness refreshes the pack each run, so this must
   be redone in-session.
3. **OPEN — the swapper block-moves from physical page 0 and traps.** With swap space,
   RECOVER-DOMAIN reaches `> Allocating memory - 7110B pages`, then 5SWAP takes a "Protect
   violation".

**What that trap actually is** [V]: the swapper routine at `swapper-k01-pseg.asm:1795`
(`1000012503`) multiplies its parameter by 0o4000 (a PAGE NUMBER), does `dmof` (data paging
OFF), `bmove`, `dmon`. So the report's "DATA POFF read request" is real, and
"Physical address 0 / Physical segment 0" is page_number x 2048 with the page number ZERO.

**Eight hypotheses MEASURED AND DEAD - do not re-open** (each with its measurement in the
write-up): our MMU (all three fault records `(none)`); a stale non-zero SWPSTAT
(`ansSWPSTAT=0B`); us posting the trap (`trapsPosted=0`); SINTRAN never restarting
(`micfu[24B:7]`); us declining restarts (`restarts=7/7`); K/FUNCV carrying an error
(`K=0` throughout); block-copy address resolution (identical on Samson, and the source
buffer genuinely holds zeros); and "the swap page lands outside the 5MPM window" (a DMA core
address is a WORD address, so `core=0x27C800` is byte `0x4F9000`, which IS inside the window).

**Where it really is** [V]: the failing request is `LSWPAGE` (`MP-P2-N500.NPL:136112`,
SINTRAN's own comment "% Disk I/O"), identified by `swpfu[LNEWSWAP:7 LSWPAGE:1]`. Two of its
arguments are confirmed: arg[2] `0x240` = 0o1100 = the swap file's LOGICAL DEVICE NUMBER
(matches `LIST-SWAP-FILE-INFO`), arg[3] `0x30` = 0o60 = `XABSFUNC`. SINTRAN performs the
transfer correctly - `ReadTransfer pos=65159168 words=1024 core=0x27C800`, exactly
SWAP-FILE-0's first page - and it reads ZEROS because **the swap file is virgin**: `xxd` on the
pristine pack at byte 65159168 shows the page blank, and the floppy sees only 22 transfers in
the whole session (format block + directory), with **no bulk read of a domain segment** and
**no write to the swap file at all**.

### CORRECTED 2026-07-31 [V, live MON 60B trace] - RECOVER-DOMAIN DOES ask for everything

An earlier version of this section concluded "RECOVER-DOMAIN never transfers the domain image".
**That was WRONG.** A MON 60B recorder (`SintranLayer.RecordMon60`, deliberately ungated - the
existing `TraceMonitorCall` is gated on Device logging which the harness switches off, and on a
DataCommunication filter that excludes MON 60B) captured all 10 calls of a full run. Every one
comes from `P=0xCCAF` = `146257B`, i.e. the MON at `146256B` - the single MON 60 gateway the
carve names, so the instrument is provably on the right door.

MON 60 passes parameters FORTRAN-style: A points at a parameter list whose first entry is the
function code, BY REFERENCE (`Developer\MON\calls\60B_N500M.yaml`). Measured `[A] = A+0xC` and
`[[A]]` = the code. Decoded against `mon60-callers/SUBFUNCTION-TABLE.md`:

| # | code | subfunction |
|---|---|---|
| 1 | `017` | list open files |
| 2 | `046` | IDEFSWAP - DEFINE SWAP FILE |
| 3 | `050` | (test function) |
| 4 | `055` | **ISPLACE - START-PLACE** |
| 5 | `006` | **ISEGLOAD - LOAD (PLACE), ONE SEGMENT** |
| 6 | `006` | **ISEGLOAD - LOAD (PLACE), ONE SEGMENT** |
| 7 | `056` | **IEPLACE - END-PLACE** |
| 8 | `142` | (redefine default infant file) |
| 9 | `077` | IRMESS - READ MESSAGE |
| 10 | `170` | READ ND-500 CPU-TYPE AND MIC.VERSION |

`START-PLACE` -> two `PLACE SEGMENT` -> `END-PLACE` is a correctly bracketed two-segment
placement, i.e. `:PSEG` + `:DSEG`. Call 2 is the `define-swap-file` command issued in the same
session, confirming the trace spans the whole run. Every code lands in the valid `000`-`177`
range with recognisable members, so the decode is not coincidence.

**THE REQUEST SIDE IS CORRECT.** The defect is that SINTRAN receives two `006 ISEGLOAD`
requests and the floppy is NEVER bulk-read: 22 transfers in the whole session, all format block
and directory. The placement is asked for; the segment content is never fetched.

### ROOT CAUSE [V] - the directory must be entered as `210319H02`, NOT from the volume label

A MON 50B (OpenFile) recorder shows what the ND-100 System Monitor actually opens. Eleven opens
in the whole run (no truncation - the cap was never reached), and two of them disagree:

```
[X]="(210319H02-XX-01D:FLOPPY-USER)LINKAGE-LOAD-H02"    <- description file: FULL name
[X]="(210319H02:FLOPPY-USER)LINKAGE-LOAD-H02:PSEG"      <- segment: SHORT name
[X]="(210319H02:FLOPPY-USER)LINKAGE-LOAD-H02:DSEG"      <- segment: SHORT name
```

**This is NOT a truncation bug in SINTRAN or in the emulator.** The raw distribution floppy
carries the short form itself:

```
@0007E0  210319H02-XX-01D          <- the volume LABEL (exactly 1 occurrence)
@0CD8C5  (210319H02:FLOPPY-USER)LINKAGE-LOAD-H02'
@0CD805  (210319H02:FLOPPY-USER)SCRATCH-SEG-01'
@0CF801  (210319H02:FLOPPY-USER)'
```

ND wrote `210319H02` into the domain's own DESCRIPTION-FILE. SINTRAN follows those references
faithfully. The mismatch is introduced by HOW WE MOUNT IT: `enter-dir,,f-d-1,0` skips the name
as a positional, which takes it FROM THE LABEL, so the directory mounts as `210319H02-XX-01D`
while every internal segment reference names `210319H02`. The `:PSEG`/`:DSEG` opens then resolve
against a directory that does not exist - hence no bulk floppy read, a swap file nothing ever
wrote, and the swapper's block-move from physical page 0.

The description file opened under the FULL name only because the monitor built that spec from
the command line; the segment specs come from INSIDE the description file.

**FIX (operational, no code change):** enter the directory explicitly.

```
@enter-dir 210319H02,f-d-1,0
ND-5000: recover-domain (210319H02:FLOPPY-USER)LINKAGE-LOAD-H02
ND-5000: copy-domain (210319H02:FLOPPY-USER)LINKAGE-LOAD-H02,"LINKAGE-LOAD-H02"
```

**This CONTRADICTS the "skip the name so it is media-independent" note** on
`NllFloppy_EnterDirectory_ListFiles_Capture`. That advice holds only while the volume label and
the description file's internal references agree. On this product floppy they do not, and
following it is what broke the install.

That also means the `RECOVER-DOMAIN` handler carve and **open question 9** (the outer dispatch
table) are NOT on the critical path for this defect - the live trace answered what they would
have. They remain open as carve items.

**Carve note [V]:** `012533` is the RECOVER-DOMAIN command **string in BANK 2** (data) -
`"RECOVER-DOMAIN\F DSCRATCH'Domain name: \"` - NOT a code address. Disassembling bank 1 there
yields plausible nonsense (trap 4/8 wearing a new disguise).

### OPEN QUESTION 9 IS CLOSED (2026-08-02) `[V]` - and RECOVER-DOMAIN's handler is named

The outer dispatch table of `MON-DEBUG:PROG` J04 is located and decoded. Full derivation and the
complete 151-command map:
[`nd-500-mon/COMMAND-DISPATCH-TABLE-CARVED-2026-08-02.md`](nd-500-mon/COMMAND-DISPATCH-TABLE-CARVED-2026-08-02.md).

- **Handler address = `bank2[0o020671 + ordinal]`** - a flat one-word-per-command array of
  bank-1 code addresses, exactly **151** entries.
- Ordinals come from a **3-word-per-command descriptor array at bank 2 `011547`**
  (name pointer, zero, byte length), running `011547`-`012453` and ending precisely where the
  command string region `012454` begins.
- The dispatch is three words at bank 1 `003260`: `RADD CLD SA DX` / `LDX I ,X 50` /
  `JMP ,X 0`. `057050` has I=1 **and** X=1, which on the ND-100 is post-indexing, so the
  effective address is `M[P+disp] + X` = `bank2[020671 + X]`. Decoded field by field, not
  read off the mnemonic.
- **RECOVER-DOMAIN is ordinal 8 -> handler bank 1 `003577` -> worker bank 1 `030302`.**
  The handler is the documented `LDX ,B -176` / `STF ,X 6` marshal-then-`JPL I` shape and
  returns to the command loop at `003527`.

### SOLVED - THE `1 10533B` TRAP IS OUR RPHS OPERAND ENCODING (2026-08-03)

Full proof: [`5SWAP-TRAP-ROOT-CAUSE-RPHS-OPERAND-ENCODING-2026-08-03.md`](5SWAP-TRAP-ROOT-CAUSE-RPHS-OPERAND-ENCODING-2026-08-03.md)

`RPHS` (`0xFFF5`) and `WPHS` (`0xFFF4`) were flagged `O_DIR` in both instruction tables - "operand
0 is four inline literal bytes". Wrong. The operand is an ordinary operand: an address code
followed by whatever that code needs.

```
1000010525:  377 365 | 304 | 010 001 115 054    rphs  <abs 0o1000246454>    7 bytes
1000010534:  300 057                            go    $57
```

`0o304` = "32-bit absolute address follows", proven by `1000010477: 104 304 010 002 075 154
w test $1000436554` in the same routine (`0x08023D6C` in octal IS `0o1000436554`).

Read as a direct operand the instruction is **6** bytes, so decoding resumed at `0o10533` -
**inside the operand** - and executed garbage. `0o10525 + 6 = 0o10533`, exactly the address
SINTRAN reported. The disassembler had the opposite bug (3 bytes, printing the nonsense literal
`$1777777777777777777704`), which is why the two tools never visibly disagreed.

Fixed in RetroCore and nd500x. **This retires the "what reads address `0x00000004`" question
(nothing does - it was decoded garbage) and the `0o10533` instruction-boundary contradiction.**

**THE MACHINE IS NOW PAST THE SWAPPER (2026-08-04).** The swapper reaches its `MON 377B`
(`N5SWAP`) at `0o1000101077`, the call is serviced (`ansMON=377B`, `ansP=0x08008255` = the next
instruction), and SINTRAN starts the loaded domain at **`0xB0000DD1`, which is the CORRECT entry
point** - offset `0xDD1` of `LINKAGE-LOAD-H02:PSEG` begins with `0xDC` = `init`, the domain
entry-point instruction. The remaining fault is `PGF - address not present` on that fetch:
**segment 22's program pages are not mapped.** THAT is the next target - not a wrong PC.

Method note: a `P1` that does not land on an instruction boundary is evidence about the DECODER.
Days were spent treating it as a puzzle about SINTRAN.

The section below is kept because its conclusions still stand - the trap really was
domain-independent, and the place-chain hunt really was the wrong tree - but the "unresolved
address puzzle" it points at is now closed.

### THE 5SWAP TRAP IS DOMAIN-INDEPENDENT, AND THE PLACE-CHAIN HUNT WAS THE WRONG TREE (2026-08-03)

Established from the **existing records**, no new run needed. Two measurements, two different
domains, two different commands, **the same trap at the same address**:

| Date | Command | NLL installed? | Result |
|---|---|---|---|
| 2026-07-31 | `RECOVER-DOMAIN` | no | `> Allocating memory - 7110B pages` -> protect violation, 5SWAP, program address `1 10533B` |
| 2026-08-01 | `ND-5000: LINKAGE-LOADER` | yes | same message, same trap, **same address `1 10533B`** |

`Installation/INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md` section 4a-VERIFIED already
called it "a pre-existing emulator-side defect, independent of the installation".

**Three consequences:**

1. **THE LINKAGE-LOADER INSTALL IS ALREADY COMPLETE.** `DEFINE-STANDARD-DOMAIN LINKAGE-LOADER
   LINKAGE-LOAD-H02` is accepted and `ND-5000: LINKAGE-LOADER` resolves and starts. This trap
   is NOT an install blocker and must not be tracked as one.
2. **The fault does not depend on which domain is placed**, so carving the PLACE chain
   (`042115` -> `ISEGLOAD` -> `5NOPAR` -> `SGLOA` -> the `FUNCS` vocabulary) could never have
   found it. That work below is correct and worth keeping - it closed open question 9, mapped
   all 159 thunk sites, and killed several stale claims - but it was **aimed at the wrong
   target**. Do not resume it in pursuit of this trap.
3. "What writes the domain into the swap file?" is **not** the blocker either, for the same
   reason: the trap fires identically for a domain that was never installed and one that was.

**The real target is the swapper's own paging path**, which fails identically regardless of
workload - i.e. the unresolved `1 10533B` address puzzle, six explanations dead so far.

---

### THE SEGMENT-LOAD DEFECT IS NOT IN THE MONITOR (2026-08-02) `[V]`

Follow-on carve, same session:
[`nd-500-mon/RECOVER-DOMAIN-WORKER-AND-SEGMENT-LOAD-CARVED-2026-08-02.md`](nd-500-mon/RECOVER-DOMAIN-WORKER-AND-SEGMENT-LOAD-CARVED-2026-08-02.md).

The routine that performs a segment placement (bank 1 `042115`, 445 words) contains
**no `MON` instruction and no `IOX` instruction at all**. The monitor program never reads
domain segment content and was never meant to - it issues MON 60 subfunction `006` (ISEGLOAD)
once per segment and SINTRAN does the fetching.

**So "placement requested, segment content never fetched" CANNOT be a monitor-side defect.**
Stop looking at the caller.

Carved call graph, which reproduces the live MON 60B trace exactly:

```
043547 -> subfn 140
043552 -> subfn 055  START-PLACE
043571 -> 042115  segment loader -> 042230 -> subfn 006  ISEGLOAD
044031 -> 042115  segment loader -> 042535 -> subfn 006  ISEGLOAD
044062 -> subfn 056  END-PLACE
```

`006` has exactly **two** call sites in the whole image, both inside `042115`, matching the
two `006` in the trace. All 159 MON 60 thunk call sites in bank 1 are now mapped to their
subfunction codes (`tools/sintran-segment-carver/thunkmap.py`) - and 159 is exactly the count
the original analysis reached independently, which is what makes the map trustworthy.

**`5NOPAR` READ, SAME SESSION - AND IT DOES NO I/O EITHER `[V, NPL SOURCE]`.** Body at
`s3vs-4.symb:78722` (`034337`), verbatim. In full it: computes the process number; saves the
user's `RSEGM`; gets into the ND-500 data segment; `*MOVAA` copies the MON-call info block
(`5DFSIZE` words) there - the source comment is literally "SAVE MONCALL INFO ON ND-500 DATA
SEGM."; then `CALL FPT2ENTRY` - "ENTER ND-500 SYSTEM MONITOR".

**There is no disc access anywhere in it.** And the post-return table settles the other half:
`FUNCS[006] = RET5` (table at `034534`), so on return from the ND-500 system monitor,
subfunction `006` does nothing on the ND-100 side at all.

**So the ND-100 never fetches segment content on ANY leg of this path.** Its entire
contribution to a PLACE is:

1. `ISEGLOAD` copies the segment **name** into the MON 60 buffer (`5P-P2-MON60.NPL:031625`)
2. `5NOPAR` copies the MON-call info block into the ND-500 data segment
3. `FPT2ENTRY` enters the ND-500 SYSTEM MONITOR
4. on return, `RET5` - nothing

**THE PLACE IS PERFORMED ON THE ND-500 SIDE.** That is why the floppy is never bulk-read: the
entity that would read it is the ND-500 system monitor, and the ND-500 side is precisely what is
broken. The fetch is expected to come back to the ND-100 as swapper page traffic (the MON 377B
`LSWPAGE` calls already measured), not as a bulk read driven by the ND-100.

This **answers** the standing "look inside ISEGLOAD's worker" item: the worker does no I/O by
design. Delete that line wherever it survives.

**Corroboration from the same table** (`5IFUNC` at `5P-P2-MON60.NPL:1320`): index `006` =
`ISEGLOAD`, `055` = `ISPLACE`, `056` = `IEPLACE` - independently confirming the
START-PLACE / ISEGLOAD x2 / END-PLACE reading of the carved call graph. Also visible there:
index `007` = `IPLSWAPPER` (PLACE SWAPPER) and index `160` = `IN5SEGLOAD`, a second
segment-load entry point not previously noted.

### `P1` (TRAPPING P) IS NOW IMPLEMENTED IN BOTH EMULATORS (2026-08-03) `[V]`

The ND-500/5000 keeps **two** program registers. `P` is the RESTART address and runs ahead of a
fault; **`P1` is the instruction that actually failed**. ND-05.017.01 ch.6 STEP 2 has the engineer
`ATTACH-PROCESS 0` / `LOOK-AT-REGISTER P` and read **`P1 : ...:<Failing instruction>`** - the whole
procedure exists because the address in a trap report (`P`) does not identify the instruction.

Neither emulator modelled it, which is why identifying `RPHS @1000010525` from the reported
`1 10533B` took days. Both now do:

- **RetroCore** `7169dc30e` - `P1` a real property in `Registers.cs`, latched at the top of
  `RaiseTrap` from `_currentInstructionAddress`. Tests `TestND500_P1TrappingRegister.cs`, 3/3.
- **nd500x** `4584e9b` - `uint32_t P1` in `cpu_protos.h`, latched in `raise_trap`, exposed by name
  in `debug_api.c` so `LOOK-AT-REGISTER P1` reproduces the manual procedure. Baseline unchanged.

**When reading any ND-500 trap from now on: use `P1`.** And if a reported trap address does not
land on an instruction boundary, that is EXPECTED - not a disassembly defect.
Full derivation: [`TRAP-PRINTER-HUNT-2026-08-03.md`](TRAP-PRINTER-HUNT-2026-08-03.md) section 0.45.

---

### CORRECTION, SAME SESSION: "the place is performed on the ND-500 side" IS WRONG

I wrote that above and it is a **name-based error**, corrected within the hour. `FPT2ENTRY`'s
source comment says "ENTER ND-500 SYSTEM MONITOR" and I read that as crossing to the ND-500. It
does not.

**The "ND-500 System Monitor" is segment `030-S3SM5`, and it is ND-100 CODE running on the
ND-100.** It is the system monitor *for* the ND-500, not a monitor *on* it. Verified this pass:

- `030-S3SM5.meta.json`: "ND-500 System Monitor segment", load address `40000B` - which is
  exactly the `FPT2E = 40000+3` definition in `s3vs-4.symb:76989`.
- Runtime word `040003` is `125001 JMP I 1` -> pointer at `040004` = **`0o142231`**, the real
  entry (`5FP2E`).
- Disassembled `142231` onward with **`nd100-dis`** on the byte-swapped image: clean, idiomatic
  ND-100 using the same `STA ,B -nn` / `LDX ,B` / `JPL I` frame conventions as every other
  ND-100 segment. This independently reproduces the 2026-07-21 correction already recorded in
  the carving skill.

**Consequence: the ND-100 CAN do the disc I/O, and the PLACE work is on the ND-100 after all.**
Everything else from the previous entry survives - `5NOPAR` really does no I/O, `ISEGLOAD` really
only copies the name, `FUNCS[006] = RET5` really means no post-return work. What was wrong was
only *where* the work then happens.

**THE ACTUAL TARGET IS NAMED AND ALREADY CARVED:** `FUNCS[006] = SGLOA @ 142637`,
"load (place) one segment", in
`re/ND500-SYSTEM-MONITOR/FUNCS-BODIES/FUNCS-segload-primitives.ASM`. Full chain, every hop named:

```
RECOVER-DOMAIN -> 042115 loader -> subfn 006
  -> [worker]  5IFUNC[006] ISEGLOAD (copies the name) -> 5NOPAR -> FPT2ENTRY
  -> [sysmon]  5FP2E @142231 -> FUNCS[006] = SGLOA @142637 -> the actual segment place
```

### SGLOA READ (2026-08-03) - IT HAS NO `RFILE` EITHER, AND THAT MAY REFRAME THE WHOLE DEFECT

Full carve: [`SGLOA-SEGMENT-PLACE-CARVED-2026-08-03.md`](SGLOA-SEGMENT-PLACE-CARVED-2026-08-03.md).

`SGLOA`'s 457 words contain **exactly one `MON` of any kind**: `MON 43` (CLOSE) at `143517`.
It opens a file at `143352` via the shared helper at `100732` (whose `MON 50` is at `100735`)
and closes it - **with no read of any kind in between**. Every hop of the PLACE chain is now
accounted for, and **not one of them reads segment content**.

The six `RFILE` calls that DO exist in this segment (`154026`, `154255`, `154334`, `155120`,
`155216`, `155375`) belong to **`CSLOA` (`FUNCS[037] @153441`, load control store)** - they read
the microcode file. `FUNCS[040] = DEFMC @155742` bounds that body, and a whole-image scan for
calls resolving into `153700`-`155600` returns 91 sites, **every one internal to that block**.
Nothing outside calls in. Anyone reasoning "S3SM5 reads files, so it reads the domain" lands
here and should stop.

**WORKING HYPOTHESIS, EXPLICITLY NOT ESTABLISHED:** between open and close `SGLOA` writes a
handful of fields through indirect stores on `B-176` (`STA I ,X 71`, `STZ/STA I ,X 57`,
`STA I ,X 47`) with no loop and no block-transfer primitive - the shape of **descriptor setup**.
If the content is paged in later on demand by the swapper (which is what the measured MON 377B
`LSWPAGE` traffic is), then **"the floppy is never bulk-read at PLACE time" is EXPECTED
BEHAVIOUR, not the defect** - and the standing "placement requested, segment content never
fetched" line has been chasing a non-problem.

**Do not act on that until it is proven.** What settles it: identify the structure at `B-176`
and confirm one stored field is the file connect number or a disc/page address the swapper
later consumes. Also unchecked: whether `055 ISPLACE` / `056 IEPLACE` / `007 IPLSWAPPER` do a
bulk transfer instead.

### THE MON 60B "ANSWER RESULT BLOCK 40B-47B" IS DECODED - it is the info-block 5DDn/5Pn array, per-command layouts carved (2026-08-10) `[V]`

Full carve: [`CARVE-ANSWER-RESULT-BLOCKS-2026-08-10.md`](CARVE-ANSWER-RESULT-BLOCKS-2026-08-10.md).

The FUNCS bodies' `,X 40/43/46/47` stores are **NOT message offsets and NOT frame-relative** -
they are the MON 60 info block's parameter records: `5DD1..5DD5` (32-bit values @ 40/43/46/51/54B)
+ `5P1..5P5` (user addresses @ 42/45/50/53/56B), 3-word stride, L07-SYMBOL + byte-verified
(`B-11 = S500DF-ZPREG = 165777B` in 030-S3SM5). The NPL post-return `FUNCS @034534` copies
`5DDn -> [5Pn]` per command. Key per-command results now byte-pinned:

- **RSTAT 041B (STATUS):** 5DD1 = {5015 CSCNT-read half, live RSTA5 half}, 5DD2 = MAR (2x IOXT,
  MS & 377B), 5DD3 low = **the third word = 5015 WA register & 37777B** (-1 on SAMSON). No mailbox.
- **REGRE 000 = MICFU 16B `3EXAR`** (msg[7]=reg#, ANSWER msg[10B-11B]=value); **REGWR 001 =
  17B `3DEPR`** (msg[7]=reg#, msg[10B-11B]=value) - byte-pins the catalog 7c INFERRED layout.
- **Examine 06B/32B answers at msg[11B-12B]** (request addr @ msg[7-10B]); deposits 07B/33B mirror.
- **3RMICV answer: msg[7]=version, msg[10B]=CPU parameter.** CSLOA sends a live 3RMICV after
  micro-start and **VERIFIES msg[7] == the version word extracted from the CS FILE** (word 7 or
  10B of the image, buffer @166056B), then caches msg[10B] -> `CPUDF[20B]`; `CPUDF[-7]` = version.
  GETCP 170B is a pure cache read (`CPUDF[27B]&7` type, `(CPUDF[20B]<<16)|CPUDF[-7]`); **RMVER
  057B's classic branch does a LIVE 3RMICV** (the "RMVER is cached, no HW access" claim is wrong).
- **Classic microcode cross-check (CONT-STORE-10611):** dispatch `007636+fn` (range check 50B,
  illegal -> answer status 4 @007740); fn 1 answers `LARG 24563B` (= 10611, the image's own id) via
  one TAG-code-7 DMA write - version-from-loaded-image proven on BOTH sides; fn 44B writes sampled
  P (32-bit -> msg[7-10B], matching HISTSAMPLE) + process + AM#15.
- **SPRES 043B returns nothing** - the caller's `STD ,X 6` word is the reserve-scope INPUT (5DD1).

**Poisoned priors retired:** "`LDX ,B -11` = the message pointer" (FUNCS-BODIES README - it is the
info block; the message is `B-67`); catalog UNKNOWN #2's "answer block 40B-47B: treat as
NON-EXISTENT". Emulator consequences (servicer answer writes incl. the CSLOA version-verify trap)
are listed in the carve doc section 5.

### DEFMC's "051302/051367 IOX helpers" DO NOT EXIST - no MPM BASE register programming (2026-08-10) `[V]`

Full carve: [`CARVE-ANSWER-DEFMC-MPM-BASE-051302-2026-08-10.md`](CARVE-ANSWER-DEFMC-MPM-BASE-051302-2026-08-10.md).

The RetroCore design doc's TODO 2 ("NEXT CARVE: 051302B-051450B to get the actual
LCON5/limit/BASE IOXT sequence") is answered: **the range holds `RLSWM`/`RELAA`/`RELAL`/`PTOS3`
(N500-SYMBOLS) and contains not one `IOX`/`IOXT`.** DEFMC's two delegation pool words
(`M[156056]=051367` RELAA, `M[156057]=051302` RLSWM, byte-verified) point at memory-release
bookkeeping, not an IOX driver. A whole-segment IOXT scan attributes every site to already
documented routines (3022 driver, CS loader, TSTPO/CHKST/RSTAT). ND-10.004.01 §2 closes it:
the MPM-5 port BASE/limit registers are programmed ONLY from the MPM cabinet's own Test and
Maintenance Program console - never by the ND-100. **Poisoned prior retired:** "DEFMC delegates
the register programming to IOX-driver helpers at 051367B then 051302B". Emulator consequence:
no new register; the MPM window base stays machine configuration; DEFMC is a pure software
answer (ADRZERO value = software allocation: `ALLOC` @171076 -> `SSYSE` store @170705).

### THE TRAP-RECORD FAULT-PARAMETER OFFSETS AND THE MMS STATUS BITS ARE PINNED (2026-08-11) `[V-MC + MANUAL]`

Full carve: [`CARVE-ANSWER-TRAP-RECORD-OFFSETS-AND-MMS-BITS-2026-08-11.md`](CARVE-ANSWER-TRAP-RECORD-OFFSETS-AND-MMS-BITS-2026-08-11.md).
Closes the two OPEN items of `MICROCODE-ANSWER-TRAP-REPORT-FIELDS-2026-07-20.md` and D4-plan
task 3.2's residue (the RetroCore `AnswerTrapStop` blocker).

- **Method:** the B30 trap generators' `ADACT`/`ORCON` fields decode as "address for the NEXT
  microword's memory access; ORCON = byte offset from the message base". Proven on four
  independent anchors (STOPR@11, trapping P@12, restart P@14, TRAPN@16 - all match the SINTRAN
  symbols exactly).
- **Page fault (TRAPN=46B, `TRAP_GEN4` 013560-013605):** fault LA @ **17B-20B** (32-bit),
  physical segment (`DMM,CAP & 017777`) @ **21B** (hw), MMS status @ **22B-23B** (32-bit).
  PHYS collected but NOT written; WR not read.
- **All other stop traps (`TRAP_GEN3`+3B/3C - PV, trace, handler-missing, HWF 51B):** LA @
  **17B-20B**, MMS @ **21B-22B**, phys addr @ 23B-24B, phys seg @ 25B, WR @ 26B, ASTS @ 27B,
  BADAP @ 30B. Identities pinned by the SRF record order {STS,LA,PHYS,CAP,WR} (RFA1=40B,
  `012675-012723`) + the manual's decoded message dump (ND-05.017.01 pp.119-120) matching
  word for word.
- **MMS status word (hardware bit order, ND-05.017.01 A.12):** read-vs-write is NOT one "WR
  bit" - it is **STATE7-5, bits 31-29** (100=read, 101=write, 000/001=POFF r/w, 110/111=PHS
  r/w); **bit 6 = 0 DATA / 1 PROGRAM**; bit 11 = TSB miss; bits 3-0 = trap sub-code (1101 =
  zero in PST entry). The "WR" in trap reports is the WR REGISTER (link.26), a failing
  physical page address. Refines the old "MMS_SIX0 top 2 bits = fault class" note
  (0xC0000000 = STATE7-6). Both manual examples decode consistently (5B -> DATA POFF read +
  memory timeout; 22701016000B -> read request + MISS).
- SINTRAN level-12 reads ONLY TRAPN (TRAPDECODER/DECOERRMESS); the detail decode is the
  ND-500 Monitor's, from the 200B stop block (next entry). The OPEN item "classic
  CONT-STORE-10611 trap writer not yet read - layout expected identical" is now CLOSED by
  `CARVE-ANSWER-CLASSIC-TRAPWRITER-S2-CONTROL-2026-08-11.md`: the "identical" expectation
  held ONLY for the header and the page-fault LA/phys-seg slots - the rest of the
  trap-dependent area is generation-specific (next-next entry).

### CLASSIC (CONT-STORE-10611) TRAP WRITER READ - header matches B30, trap-dependent area DIVERGES; mid-run resume + CONTROL bits 6/8 settled (2026-08-11) `[V-MC classic + V-NPL]`

Full carve: [`CARVE-ANSWER-CLASSIC-TRAPWRITER-S2-CONTROL-2026-08-11.md`](CARVE-ANSWER-CLASSIC-TRAPWRITER-S2-CONTROL-2026-08-11.md).
Closes the B30 trap-record carve's §6 OPEN item and the integration doc's "CONTROL bits 6/8
semantics unknown".

- **Classic trap-stop writer = microwords `011271-011337`** (entry via the micro-trap
  sorter `011022`, exit through `010537 -> 011405` shared answer block). Header AGREES with
  B30 slot for slot (`11B` STOPR:=2, `12-13` trapping P from ctx[224B], `14-15` restart P
  from ctx[240B], `16B` TRAPN). Trap-dependent area: **46B** = LA@17-20 + phys-seg@21
  (mask `7777B`) + ONE composed status halfword @22 (`TRAPINF<<8|subtype`, bit 6 = program
  side) - NOT the B30 32-bit MMS@22-23. **{44B,51B} only** get the big record:
  17-20 REAL addr (24-bit), 21-22 logical addr, 23 DSTS1/2 hw, 24 DSTS0 hw, 25-26 loop
  state, 27-30 DCINHLL, 31 composed status. **{25B,26B,27B}** = LL@17-20 + ctx[124B]@21-22.
  **45B and all others: NO fault parameters.** Do NOT feed B30 GEN3 offsets to a
  classic-generation emulator path.
- **Mid-run S2 poll `011066/011067`** sits in the micro-trap sorter (vector `011022`,
  installed by init word `000627`). A mid-run activate resumes the running program because
  the queue walk accepts **N5STA 1 AND 2** and re-dispatches the program's own status-2
  message; `011473` skips the context reload when the process is already current; re-entry
  is `011370 -> 011377-011401` (`DP:=P; PRF,START; JMPMAP`). Queue-empty -> IDLE happens
  only when nothing should keep running.
- **CONTROL bit 8** = "run the power-fail save on this terminate" (jump into `010750`:
  save the full 35B-register macro context to the process context block, dump
  DWIPGU|IWIPGU written-in-page bytes to memory - mirror loader at `011000-011013` -
  STATUS|=210B, UNLOCK, IDLE). Writer: SINTRAN's ND-100 power-fail path,
  `PH-P2-RESTART.NPL @032246` `LCON5:=400B` + SLOC5 + TERM5. **CONTROL bit 6** only gates
  whether a terminate that aborts an in-progress message sets `AL#10` bit 0 ("no current
  macro process", read only by the MICFU 44B histogram answer). **No SINTRAN writer of
  bit 6 exists in the NPL corpus** (LCON5 values used: 0,1,5,10B,40B,400B) - latent
  test/maintenance feature.

### FPRSTART's 200B "STOP (TRAP) INFO" SOURCE IS CARVED - message hw 12B..41B via the sysmon trap-stop builder (2026-08-11) `[V]`

Full carve: [`CARVE-ANSWER-PRSTART-STOPINFO-SOURCE-2026-08-11.md`](CARVE-ANSWER-PRSTART-STOPINFO-SOURCE-2026-08-11.md).

RUNN's post-return `TOUSMOVE(dest=5P2, len=200B)` copies from the MON60 com-buffer (LOGBADR
window), and the buffer is filled in `030-S3SM5` by `PROGS`' STOPR dispatch
(`146726-146742`: STOPR 1..3 else `N5FAT`; **2 = trap -> `064300`**) whose builder does
**`MOVEW` of 30B (=24) words from message hw 12B into buffer word 0** (`064415-064426`,
source addr = msg + `M[064437]=000012`; dest = ABUFA converted to a window address via
resident `036003`). So the user's stop block = the trap record verbatim, shifted by -12B
(word 0 = trapping P, word 4 = TRAPN, words 5-6 = fault LA, ...). Buffer words 24-63 are NOT
written on this path (stale). **Bonus byte-pin:** the RUNN "stop reason" `5DD1 = (0, TRAPN)`
(`065141-065143`: `STA ,X 41` / `STZ ,X 40`). `FREL5`'s break-state answer reuses the same
copies. All pool words re-read from raw bytes (appendix in the carve doc).

### PSPHS vs THE ND-500 PST: PARALLEL BOOKKEEPING - the PST is swapper-maintained, its base a SINTRAN allocation (2026-08-11) `[V by elimination + MANUAL]`

Full carve: [`CARVE-ANSWER-PST-WRITER-VS-PSPHS-2026-08-11.md`](CARVE-ANSWER-PST-WRITER-VS-PSPHS-2026-08-11.md).
Settles the UNPROVEN flag of `PSPHS-PHYSICAL-SEGMENT-TABLES-CARVED-2026-08-03.md` §0.

SINTRAN does NOT build the ND-500's MMU-walked PST from PSPHS/PSLLI/PSULI/PSMOD. The PST
BASE is a SINTRAN software allocation (`ALLOC @171076` -> `SSYSE`; MEM-CONF lists it) handed
to the CPU as control-store cell `0o21` (patched; `PSTP = cell21 << 11`). The PST ENTRIES
are maintained by the SWAPPER: microcode writes none [V, prior], carved SINTRAN writes none
[V, prior], and ND-05.017.01 says it outright three times (`:4648` "the swapper is also
using physical addressing when accessing the physical segment table"; `:4658`/`:4662`
"wrongly updated by the swapper process"; `:4801` page-fault flow). Swapper-side signature:
25+ `dctsb`/`pctsb` TSB flushes, zero `wphs` (its PST writes are ordinary stores into
mapped data space - why opcode hunts never found "the PST writer"). RESIWR/13B/14B carry
segment content and the swapper LOADER's page lists, never PST entries. **[OPEN]** the
exact swapper store sites; the cell-`0o21` patcher instructions; the ND-100 "first page"
PST seeding the manual's startup chart claims (`:3681`, un-carved).

### THE `B-176` STORES ARE RESOLVED - the PSPHS/PSLLI/PSULI/PSMOD tables (2026-08-03) `[V]` (RPHS relation since settled: see the 2026-08-11 PST entry above)

Full carve:
[`PSPHS-PHYSICAL-SEGMENT-TABLES-CARVED-2026-08-03.md`](PSPHS-PHYSICAL-SEGMENT-TABLES-CARVED-2026-08-03.md).

**First, a correction to the paragraph above.** `B-176` is not a pointer - it is an **array
index**. `I` set together with `X` while `B` is clear is POST-indexed indirect
(`EA = M[P+disp] + X`), so each displacement names a pointer word in the routine's own literal
pool. Bit roles re-derived from the instruction words in the same routine (bit 10 = X, bit 9 = I,
bit 8 = B, bits 7-0 = signed displacement), so this does not rest on the disassembler's mnemonic.

The four stores go to four separate resident tables, indexed by the segment number:

| Store | Table | Address | Value |
|---|---|---|---|
| `STA I ,X 71` | `PSPHS` | `177401B` | physical start (`M[B-174]` OR `M[B-75]`) |
| `STZ I ,X 57` | `PSLLI` | `175341B` | 0 |
| `STA I ,X 57` | `PSULI` | `175441B` | size-1, or -1 when the size word is absent |
| `STA I ,X 47` | `PSMOD` | `175541B` | 0/1 from bit 9 of a descriptor word |

`PSPHS` reads as PHysical Start and `RPHS` is Read from PHysical Segment - the instruction the
5SWAP trap fires on (`RPHS @1000010525`).

**CAUTION, corrected same day:** that is a name correspondence, NOT a proven link. `RPHS` runs
on the ND-500 and resolves through the ND-500's own physical segment table pointer (`PSTP`);
`PSPHS` is an ND-100-side table inside `030-S3SM5`. Whether SINTRAN builds the ND-500 PST from
`PSPHS` is unproven. Do not write "PLACE writes the entry the swapper reads" until it is.

Identification is a 7-for-7 first-try hit in `N500-SYMBOLS.SYMB` that turns out to be one
family: every `PS*` table has a `DS*` twin (`PSLLI`/`DSLLI`, `PSULI`/`DSULI`, `PSMOD`/`DSMOD`,
`PSPHS`/`DSPHS`) on a uniform `40B` = 32-word grid, and all of them are unique symbols with no
overlay aliases. Contents read all-zero on disk, which is what a resident data table does in a
carve.

**Cheap test this now enables:** read `PSPHS[seg]` at the moment of the trap. Zero means PLACE
never wrote it for that segment, and the fault is a missing write rather than a missing page.
Still open: what `M[B-174]` holds (the open/interrogate chain at `143352`-`143414` is uncarved),
what the `ORA M[B-75]` contributes, and whether the swapper reads `PSPHS` directly or a copy.

### WARNING: `FullFlow` IS NOT THE 5SWAP REPRODUCER - a green run proves nothing `[V]`

**Measured 2026-08-03** with `RETROCORE_HARNESS_TIMEOUT_SCALE=5`,
`FullFlow_Octobus_Login_Nd500_Status_StartSwapper_Capture` runs **completely green** in 35
minutes:

```
OUTCOME: ENTER=OK login=OK nd-500=OK status=OK start-swapper=OK list=OK stop-system=OK
trapsPosted=0  lastTRAPN=0B  cpuP1=0x00000000
```

**Do not read that as "the 5SWAP trap is gone."** The trap is produced by `RECOVER-DOMAIN` and by
`ND-5000: LINKAGE-LOADER` (see the dated table earlier in this document) - i.e. by **running a
domain**. `FullFlow` starts the swapper and lists; it parks the swapper at `PC=0x08008255` in its
message loop and never enters the region containing the fault at `0o1000010525` = `0x08001155`.

Two things follow:

1. A green `FullFlow` is the *expected* result and always was - "swapper track GREEN" predates
   any of this work. It is not evidence about the trap in either direction.
2. **Whether the `RPHS` fix changes the trap is still UNMEASURED.** Testing it needs a run that
   actually loads and runs a domain, and each attempt costs ~35 minutes at the 5x timeout the
   harness needs on this machine.

**The reproducer is `Nd500SwapFile_CreateAndDefine_Capture`** (in
`Emulated.Tests\ND100\Nd100SintranNd5000OctobusBootHarnessTests.cs`). It creates and defines the
ND-500 swap file and then issues
`recover-domain (210319H02:FLOPPY-USER)LINKAGE-LOAD-H02` - swap file first, domain second, which
is exactly the order the trap needs. Use that test, not `FullFlow`, for anything about the
5SWAP trap.

Also confirmed by that run, usefully: `PSTP = 0x0003A000` appears between `@nd-500` and `status`,
and the wall-clock "STALL" outcomes at the default timeout are purely wall-clock - every stage
that stalled at 1x passed at 5x with no code change.

### `RPHS` / `WPHS` COULD NEVER EXECUTE IN EITHER EMULATOR (2026-08-03) `[V]`

Handoff to the C port:
[`HANDOFF-RPHS-WPHS-PHYSICAL-SEGMENT-TO-ND500X-LLM-2026-08-03.md`](HANDOFF-RPHS-WPHS-PHYSICAL-SEGMENT-TO-ND500X-LLM-2026-08-03.md).

Chasing `PSPHS` into the emulator turned up the other half. **Both handlers demanded THREE
operands while both decoders correctly emit ONE**, so the guard fired on every execution -
silently a no-op in RetroCore, `trap_illegal_operand` in nd500x. `RPHS` is the instruction the
5SWAP trap fires on, so part of that trap is **our own defect, not SINTRAN's**.

`ND-05.009.4` sections 16.31 / 16.32 give one operand (the domain number) and carry the rest in
the index registers: `I1` = byte count, `I2` = address on the domain, `I3` = address on the
physical segment, `I4` = physical segment number. Five defects were shared by both ports: the
operand-count guard; source taken from operand 0 instead of `[I4,I3)`; `I3`/`I4` never read; no
page-boundary stop (it is a PARTIAL move the caller loops on); `I1=0` and `Z=1` set
unconditionally.

Fixed in RetroCore (commit `f0cf3a436`), with the PSN-rooted half of the MMU walk factored out of
`TranslateVirtualAddress` into `TranslateThroughPst` plus a public
`TranslatePhysicalSegmentAddress` - these instructions are handed the PSN outright and must skip
the capability lookup. The extraction is purely additive, so the virtual path is unchanged.

Tests `TestND500_RphsWphs.cs`, 5/5, **verified to FAIL against the old code**. Full-suite proof
by arithmetic rather than impression: baseline **2056 tests, 2044 passed, exactly those 5
failing**; after the fix **2056 tests, 2049 passed, 0 failing**. 2044 + 5 = 2049, so the only
delta is the five. **`nd500x` is NOT fixed yet** - see the handoff.

**Method note worth keeping:** the usual rule is that the C port leads on MMU work and you read
the C first. That found nothing here, because nd500x is a comment-for-comment port of the C#
stub including its wrong parts. **Two ports agreeing is not corroboration when one was copied
from the other** - the manual settled it in five minutes.

### AND THE WHOLE `FUNCS` VOCABULARY HAS NO FILE-TO-MEMORY OPERATION `[V]`

Read the **complete** 60-entry operation set instead of chasing SGLOA's callees one by one.
The ND-500 system monitor can do registers, memory (logical / physical / examine / deposit /
physical-segment), control store, place, swapper, swap-file define+delete, process and
name-segment management, and memory configuration. **Nothing in it reads a file into ND-500
memory.** Every content-moving operation is a memory primitive fed by the *caller*
(`PMWRI`, `DMWRI`, `AMEMW`, `WPHSG`) or a read back to it (`RPHSG`, `AMEMR`).

Two names checked rather than assumed, both because they read like what I was hoping to find:

- **`076 TOSWP` is "message to swapper", not "copy segment to swap"** - confirmed at the table
  entry (`166733`) and in the NPL handler (`ITOSWP: % FUNCTION=076: MESSAGE TO SWAPPER`,
  `s3vs-4.symb:78328`).
- **`110 WPHSG` has exactly ONE call site** in the whole monitor image (`055736`), and it is
  not in the PLACE bracket.

**So the PLACE subfunctions cannot be delivering segment content - no operation they could
call is capable of it.** Combined with the already-verified fact that the swapper's `LSWPAGE`
names the swap file's logical device number `0o1100` explicitly, the open question sharpens
to one sentence:

> **What is supposed to write the domain into the swap file before the swapper reads it?**

The swapper is asking the right file for a page that was never written. That gap is upstream
of everything carved so far, and it is the next thing to chase.

**ALSO FLAGGED - a stale doc that will mislead the next reader.**
`re/030-S3SM5-routine-map.md` states its disassembler as `nd500-dis` and calls the code region
"ND-500 code". That contradicts both the carving skill's 2026-07-21 correction and the check
above. Its **data**-region work (header, string pools, the MON dispatch vector table at `0x60`)
is unaffected - those are bytes either way - but **every claim it makes about the code region
should be treated as suspect** until re-derived with `nd100-dis`.

**Worth flagging, not yet a claim:** ISEGLOAD is called with five parameters, **three of which
are the ADDRESSES of caller locals** for SINTRAN to write back into. That is the same shape as
the swapper's 7-arg MON 377B (`LSWPAGE`) whose write-back measured EMPTY. Whether the two are
connected or this is just the common calling convention is `[OPEN]`.

**Still open, and do not read this as closing it:** the command -> **MON 60 subfunction**
binding. The thunks at `146310`-`147070` are called from *inside* the handlers, not from this
table, and that hop is untraced. The subfunction column in `nd-500-mon-j04.prog.md` section 14
remains a name-based correspondence.

**Method, worth reusing:** the table was found by searching bank 1 for the single constant
`0o011547` (the descriptor-array base), which occurs **exactly once**, in the command loop's own
pointer pool three words from the dispatch. Two range scans tried first were pure noise - a
151-word window of "plausible code addresses" produced 8 false candidates in bank 1 and 65 in
bank 2 (bank-2 hits were ASCII text whose word values land in the code-address range). Pick the
most distinctive single constant; do not range-scan over values that overlap instruction
encodings.

**Oracle status 2026-07-31 [V]:** mailbox differential oracle 43/43, octobus 5/5, floppy 11/11
green after this session's servicer diagnostics. It CANNOT adjudicate this defect: `23B` start
and `24B` restart are not parity targets, and the fault is above the mailbox layer.

### TOOLING: `nd100-dis` indexed-offset fix + carve regeneration (2026-07-31)

Ronny fixed `nd100-dis` dropping the OFFSET operand on the indexed-through-T family
(`LDATX`/`LDXTX`/`LDDTX`/`LDBTX`/`STATX`/`STZTX`/`STDTX`). Proven on the same address and raw
word `143344`: old tool `STATX`, fixed tool `STATX 4`. The failure was SILENT - the mnemonic
still looked right.

**Why this effort cares:** `*AAX <offset>; LDATX` is exactly how SINTRAN reads swapper/mailbox
message FIELDS (`*AAX SWPFU; LDATX`, `*AAX HSWPI; LDDTX`). Without the offset a listing does not
say WHICH field an instruction touched.

**Bare output is CORRECT for offset 0** [V, from `decode.c`]: the decode masks with `0xFFC7`, so
bits 5-3 are the offset field - `143302 & 0x38 = 0`, `143370 & 0x38 >> 3 = 7`. A remaining bare
line is offset-zero, not a missing operand.

**REGENERATED 2026-07-31** with `make-segment-ref.py` (which byte-swaps for the disassembler only,
hashes the original big-endian bytes, and re-inserts the `>>> NAME(TABLE)` L07 symbols - a raw
`nd100-dis` rerun would have stripped those):

| segment | offsets now shown / family total |
|---|---|
| `017-S3SMPIT` | 255 / 1027 |
| `016-S3SRPIT` | 282 / 606 |
| `004-S3RTL` | 114 / 127 |
| `003-S3CP`, `013-S3SCP` | 64 / 107 each |
| `012-S3SFS`, `006-S3FS` | 12 / 59 each |
| `007-S3DMAC` | 5 / 18 |
| `030-S3SM5.dis` (direct nd100-dis) | 89 / 235 |

`014-S3ERRP`, `010-S3RTFIL`, `020-S3SDT5`, `021-S3NMS5` regenerated with 0 offsets shown - their
handful of family instructions are all genuinely offset-zero.

**STILL STALE:** the three `kernel-carving/SCSI-DRIVER/*.dis` (8 instructions),
`nd-500-mon-j04.prog.asm` (3), and `006-S3FS.annotated.dis` - the last carries HAND ANNOTATIONS
and must be merged, never overwritten.

**Any ND-100 disassembly dated before 2026-07-31 is suspect for this opcode family** - re-check
before trusting an offset read out of one. `030-S3SM5` mattered most here: it is the ND-100
System Monitor that drives the ND-500 swapper and prints "> Loading Swapper".

---

## 00. 2026-07-25 — SWAPPER REACHES ITS MESSAGE-WAIT LOOP; the blocker moves from microcode to transport

**This is the newest status entry. Read it before planning any swapper work.**

Document of record for the detail: [`OCTOBUS-SWAPPER-HANDOFF-2026-07-25.md`](OCTOBUS-SWAPPER-HANDOFF-2026-07-25.md).

**Headline `[V]` (observed in the emulator, reproducible via `SwapperStartDiagnosticTests`):** the ND-500
swapper now executes **420 macro instructions with NO throw at all**. The diagnostic run ends on its
4M-tick budget, not on a fault. It is sitting in its **main message-wait loop** at `P=0x08000677`
(octal `1000003167`):

```
1000003167: call $...377,$2,$1000225040,$1000437234   ; MON 377B, 2-argument form
1000003207: ifkret
1000003210: go $...757                                ; backward branch - this is the loop
```

**The blocker is no longer the microcode — it is the message.** Any plan that still says "the swapper
crashes / the microword lane is incomplete" is stale as of this date.

**Why it stops `[V]`, measured with a mailbox guard added to the diagnostic — NOT what was first
written here.** The swapper makes **exactly two** MON 377B calls (4-arg at `0x0800823F`, 2-arg at
`0x08000677`) and is then never dispatched again: the microcode IDLE poll walks `0o24670..0o24723`
and repeats, never reaching the MICFU-24 slot `0o15250` or `MSG_CONMC` `0o15676`. Cause: at macro
`P=0x08009053` the swapper executes `w4 sfill b.34` (`swapper-k01-pseg.asm:11718`), a bulk fill of
`0x80000000` whose destination is computed **from the fabricated probe message**. It fills over the
harness mailbox, so the re-posted MICFU 24 lands in a wrecked queue. Every message field reads
`0x8000` at the second restart.

**RETRACTED same day:** "it spins because the announce stub returns the same message forever". The
stub was never the problem. Two shortcuts that followed from that wrong reading are also dead, both
tested: a smarter stub does not help (the swapper acts on message CONTENT), and relocating the
harness mailbox does not help (moving `ExtBlock` `0x1000 -> 0x4000` only moved the clobber to
`HeaderBase`; reverted).

**Eight microword gaps closed to get here** (all in the `CpuND5000` microword lane, which runs the real
MICRO-5800-B30 control store one 128-bit word per tick): `D,IDU,CSIT` (write-only 1-bit SIT-arm latch,
ND-05.020.01 chapter 7 section 7.3.3 Table 15 — discarding it is FAITHFUL, the CPU models no trap
machinery); `ST,ACCA` (sticky O, Z/S/C replaced); ADD3/SUB3 dispatch entries; local indirect
post-indexed `0xE4-0xEF`; `ORD,OP1` (latch operand index 0 only); `G,DIR1/2/4` displacement width;
`AB,EA1DIR` (= "use EA1", unscaled — an earlier reading of this as "EA1 + direct operand" was WRONG);
and `ABR,(none)` (**inverted sense** — the branch is taken when the condition is FALSE).

**MULAD carry adjudicated across all three lanes `[V, MANUAL + MICROCODE]`.** The microword lane and the
two C-family lanes disagreed. The ND-500 Reference Manual settles it by comparison: 11.1 ADD lists
"carry from most significant bit -> C (integer)"; **11.7 MUL does NOT list C at all** (Z, S, O, FU, FO
only); 11.19 MULAD lists it with ADD's exact wording. MULAD is MUL followed by ADD, so **C is the ADD's
carry-out, not the multiply's excess** — the multiply's excess is already reported through O, so the old
form double-counted it. Microcode `MULADW` (`002627..002631`) agrees: product to the 32-bit scratch SC7,
`ST,SAVM`, then `ALU,A+B A,SC7 B,SC5` with `ST,ACCA`. **The microword lane was right; the functional
`CpuND500` and the `nd500x` C port were both wrong** and have been corrected to match.

**METHOD LESSON (cost most of a session):** the differential-sweep diff format is
`{name}={expect}!={got}` = **`golden!=microword`**, i.e. GOLDEN FIRST. It was read backwards for an
entire session, which inverted the characterisation of every divergence. Check the polarity of any
diff format before reasoning from it.

`[OPEN]` items, in dependency order:
1. **Give the swapper a structurally valid SWMSG** - carve the field layout (the `sfill` descriptor in
   `b.34` is a precise lever: work backwards from what a sane fill destination must be), and/or wire
   `IMonitorCallSink` to the real octobus transport (`OctobusND5000Station.cs`). Note the transport
   route is NOT small: per `TRACKB-SHARED-ND500-CPU-INTERFACE-DESIGN-2026-07-21.md` the microword CPU
   must not use `Nd500CpuProcessBridge`/the C# servicer, so it needs a `CpuND5000Adapter` behind a
   separate `AttachMicrocodeCpu`, and `Emulated.HW` does not reference the ND5000 package today.
2. Regenerate `ARITHMETIC_mulad.json`. Its 14 remaining divergences are **all** the C flag and are
   **stale goldens generated from the old behaviour, not emulator bugs**. Deliberately not done: the
   generator rewrites all 188 corpus files at once, which would freeze other lanes' in-flight CPU work
   into the oracle.
3. Sub-word WIDTH residuals: `putbf` 6 vectors (register destinations), `loopd` 4 vectors.

---

## 0a. 2026-07-20 — FOUR RETRACTIONS, one carve answer, and the open-questions register

**Read this before citing any pre-2026-07-20 conclusion about the swapper or the octobus mailbox.**

New documents of record:
- [`OPEN-QUESTIONS-REGISTER-2026-07-20.md`](OPEN-QUESTIONS-REGISTER-2026-07-20.md) — **everything both
  tracks do not know**, ~90 deduplicated items with answer routes (`CARVE`/`MICROCODE`/`LIVE`/
  `MANUAL`/`UNANSWERABLE`). §1 = 3022/swapper track, §2 = octobus/ACCP track.
- [`REMEDIATION-PLAN-OCTOBUS-TRACK-2026-07-20.md`](REMEDIATION-PLAN-OCTOBUS-TRACK-2026-07-20.md) —
  what we are doing about them, in dependency order.
- [`NDIX-KERNEL-INTERFACE-EVIDENCE-2026-07-20.md`](NDIX-KERNEL-INTERFACE-EVIDENCE-2026-07-20.md) —
  **independent, non-carve evidence** for the interface from the NDIX Release-3 kernel source
  (`E:\Dev\Ronny\NDIX-C\kernel\`), ND-05.012.01 §13 (vendor message protocol, primary text for
  the N5STA lifecycle and MICFU-era function table), and NEC-01 (the 5015's registers are
  **microcode unit-select codes** — the CPU has no I/O path to the 5015, it is an internal
  module). Key new facts: NDIX's only outbound primitive is `callg 0xF8000180` through a
  `PC_IND|PC_OMC` segment-31 capability = **MON 600B**; the FE_INIT handshake hands SINTRAN the
  interrupt entry points and receives the whole memory map incl. `private` (the ADRZERO window
  constant) and `sharedseg`; inbound is `int_descr` chains + forced entry at `intvec`. Partial
  MANUAL-route answer to register item C7/Q-OTH-05 (classic RIOM path = TAG-OUT 6/7 + 3022 MAR).
  Same session: the fabricated "high-level TAG protocol" was scrubbed from the four remaining
  contaminated docs (list in that document's §8).
- [`CARVE-SWAPPER-CONTEXT-BLOCK-BUILDER-2026-07-20.md`](CARVE-SWAPPER-CONTEXT-BLOCK-BUILDER-2026-07-20.md)
  — **Phase-2 answer: SINTRAN builds NEITHER the swapper's context/register block NOR the PST NOR the
  PCB.** Its swapper-start handler `SWMESS` (`MP-P2-N500.NPL:428-462`) writes ONLY the 5MPM mailbox
  MESSAGE (`SWMSG`: `MICFU=3START`, `SENDE/5RECE=5SWPROC`, `SWPFU=SWACTIVE`, `5PRIO=300`, `5CPUN`,
  `SWPINFO`). The per-process register block IS known to SINTRAN (`CNTXP=57`/`ADRZE=60`/`REGBS=200`/
  `ERREG=152`, `REGBSZ 0o200 words = 0o400-byte microcode stride`) but `CNTXPAGE` is referenced
  EXACTLY ONCE — a READ in `GERRC` after a trap; nothing writes `P/PS/DOM` to seed it. So `P=4/PS=1`
  must come from the microcode: cold-start vector `MACRO_STARTL` (literals) fits a COLD start;
  mailbox-23B/`CNTXTLOAD` is only a WARM restart (needs a prior `CNTXTSAVE`). SINTRAN-vs-ACCP left
  `[OPEN]` with the live discriminator: dump `CNTXPAGE+ADRZERO` before the first swapper instruction.
  Also ties the D4 `r2=0` null-deref at `0x913B` to an unset `SWMSG.SWPINFO` (no posted work message).
- [`CARVE-RUN-TO-WORK-POSTING-CHAIN-2026-07-20.md`](CARVE-RUN-TO-WORK-POSTING-CHAIN-2026-07-20.md)
  — **Phase-4 chain: operator RUN -> swapper gets real work -> domain runs (road to NLL:).** `5ACTSWAPPER`
  (`MP-P2-N500.NPL:2851`, `144762`) posts `SWMSG.SWPINFO` (`HSWPI=104`) ONLY when a RUNNING ND-500 process
  PAGE-FAULTS. Path `[V]`: domain `3START` (=23B) -> executes -> STOP message -> `DECOMESS` (`135161`) reads
  `STOPR`: `MOCALL(1)` -> `MCHANDEL` (`136764`, the `NLL:` output path, swapper NOT involved); `TRAPCODE(2)`
  -> `TRAPDECODER` (`135314`) -> trap `46`=PAGE FAULT -> `CALL 5ACTSWAPPER` -> swapper pages it in via
  `5SWRT` (`RP-P2-N500.NPL:16`, `MON 131` ABSTR) -> restarts domain. RUN posts NO swapper work directly;
  faking `SWPINFO` is not a substitute for the domain running. **Current D4 stop is UPSTREAM**: the SWAPPER's
  own cold-start (process 0) has not parked, so RUN never `3START`s the domain and `5ACTSWAPPER` is not
  reached yet. `[OPEN]`: whether `LINKAGE-LOAD-H02` demand-faults at all — if placed resident it can reach
  `NLL:` via `MCHANDEL` alone with the swapper idle. Symbol values verified vs `SYMBOLS\L07\*`.
- [`SWAPPER-START-CPU-MMU-SETUP-CARVE-2026-07-21.md`](SWAPPER-START-CPU-MMU-SETUP-CARVE-2026-07-21.md)
  — **MICROCODE-SIDE companion to the two docs above: what the B30 microcode sets up (CPU regs, MMU,
  code/data addresses) at process/swapper start.** `[V]` (independently grep-confirmed): the register
  context block = `0o4000 + 0o400*proc` BYTES (256-byte / 64-word stride = the `REGBSZ 0o200`-word stride
  the context-block-builder doc noted); **P (code entry) = ctx offset 0x00** -> `IAC,P` at `014757`,
  EXECUTE `014636` resumes macro fetch there; A1-A4 (data base) = offsets 0x20-0x2C. **The MMU page-table
  root `MM,PSTP`/`MM,PUWP` is written at EXACTLY 4 sites, both CPU-INIT, from CONSTANTS** — INIT_SAM
  `014572`/`014573` (const 2) and macro-start `017731`/`017732` (`PSTP:=0`, `PUWP:=4`) — **never
  per-process, never from the image load address**; there are ZERO `IMM,*`/`DMM,*` page-table WRITES (the
  `017534`-`017557` refs are LOOK_SRF debug READS). Per process only the DOMAIN+SEGMENT switch
  (`MM,PS`/`MM,PHS`/`MM,DOM`/`MM,ADOM` via `CNTXTLOAD`). `[INFERRED]`: PSTP roots a domain-keyed table;
  **SINTRAN/ACCP build those tables — the microcode never builds them at start and ASSUMES they exist =
  the microcode-side confirmation of the D4 RUN blocker** (if SINTRAN's real placement never runs, the MMU
  has nothing to translate through). Also `[INFERRED]`/UNVERIFIED: whether an `MM,PSTP` write fans out to
  both IMM+DMM units or they are read-back aliases (model rec: update both). Resolves the context-block
  doc's `[OPEN]` cold-start P source (= ctx offset 0x00; PSTP/PUWP are init constants).
- [`EMULATOR-SWPINFO-GAP-ANALYSIS-2026-07-20.md`](EMULATOR-SWPINFO-GAP-ANALYSIS-2026-07-20.md)
  — the D4 swapper `0x913B` null-deref, with a **LIVE CORRECTION 2026-07-21** [V, ran
  `Nd500_D4_RunDomain_RealCpu_Capture`]: the SWPINFO **pointer is NOT zero** — SINTRAN's MON 377B
  RESTART write-back delivers `@0x240B4 := 0x210718` (= requester MESSBUFF byte `0x420E30`) + control 5.
  What is empty is the **MESSBUFF BODY** (15 zero words); the swapper derefs it -> `CRASHED @0x0800913B`.
  Disproves the earlier "SWPINFO reads zero" premise and any `SWPINFO==0` gate. Reproduces the Q-MMU-06
  carve exactly. control=5 = fn `MSWIN` (legitimate work), so no valid gate exists.
- [`CARVE-MSWIN-MESSAGE-SENDER-2026-07-21.md`](CARVE-MSWIN-MESSAGE-SENDER-2026-07-21.md)
  — **Who posts the empty MSWIN(fn5) message.** `[V, NEGATIVE]`: NO ND-100 routine fills the message
  body — `5ACTSWAPPER` (`144762B`) is only a relay (writes `SWPST=fn` + `HSWPI=pointer`, copies NONE of
  the 15-word body); a full grep of every NPL file + the `s3vs-4.symb` build shows `SWFUN` is only ever
  LOADED (never STORED) and `MICFU := 3SWMESS` is never written by ND-100 code, so both fields arrive
  pre-set from the ND-500 side. `[I]`: the poster is `030-S3SM5` (ND-500 System Monitor) and/or the
  ND-5800 microcode; `[OPEN]`: the exact S3SM5 routine (S3SM5 carved but not reliably instruction-
  decoded). Ties to the core D4 blocker: the ND-500-side placement/sender that fills the body never
  genuinely runs on the faked 5800 path, so HSWPI addresses a reused, zeroed process-1 MON-200B buffer.
  Trap flagged: `MICFU=3SWMESS=5` and `SWFUN=MSWIN=5` are two DIFFERENT fields both equal to 5; MON 510B
  (SWMC) is a separate path, NOT the sender. **CORRECTED by the S3SM5 decode below - the sender IS
  ND-100 code (in S3SM5); this doc's "ND-500-side / no ND-100 code" bottom line is superseded.**
- [`CARVE-S3SM5-MSWIN-STAMP-AND-FILL-2026-07-21.md`](CARVE-S3SM5-MSWIN-STAMP-AND-FILL-2026-07-21.md)
  — **The MSWIN sender/filler IS ND-100 code in `030-S3SM5`.** `[V]`: `030-S3SM5` is **ND-100 code, NOT
  ND-500 byte-addressed** (reliable decode = byte-swap BIG->LITTLE then `nd100-dis -a -o -b 40000`; base
  word 040000B=0x4000; `nd500-dis` gives garbage; corroborated by sibling `006-S3FS.dis` + the memory
  note; S3SM5 emits the "> Loading Swapper" string). It is the ND-100 System Monitor managing the ND-500
  swapper. `[V]`: S3SM5 stamps `MICFU(off6):=3SWMESS`(literal 5) and writes `SWFUN(off7)` + the ~15-word
  body - MSWIN builder at runtime octal **140771..141001** (SWFUN:=caller `[B-77]`), full body builder at
  **162155..162207** (offsets 2,3,4,10-17,110,112); the message buffer is `X:=[B-67]`. So the fill does
  NOT need ND-5800 microcode; it CORRECTS the prior doc (whose grep only covered the resident nucleus -
  S3SM5 source is not in the repo, so its stores were invisible). Decode saved:
  `tools\sintran-segment-carver\versions\L-VSX-500\re\030-S3SM5.dis`. `[I]` (offsets rest on N500-SYMBOLS
  match), `[OPEN]`: routine has no symbol name (addressed by number); enclosing subroutine entry; and
  WHETHER the MSWIN builder runs in D4 or the `[B-61]` gate diverts to MSWSWAIT / stalls before it.
  **LIVE ANSWER 2026-07-21b [V, gated ND-100 trace]: the builders do NOT run.** During PLACE-DOMAIN
  S3SM5 is confined to `[0xC499, 0xDAD3]` = its CS-load "Loading Swapper" verify loop (1.5M+
  non-terminating iterations, cap hit) and never advances to 0xC1F9 or 0xE46D (cross-checked vs
  `030-S3SM5.dis` = same overlay, no confound). So the empty swapper body is DOWNSTREAM of the CS-load
  verify stall: S3SM5 never reaches its body-fill (162155). Root = task 8 (CS-load verify stall); the
  0x913B crash is a symptom. Next: carve WHAT the verify loop @0xD000..0xDAD3 polls and why it never
  satisfies (that is the task-8 fix).

- [`TRACKB-SHARED-ND500-CPU-INTERFACE-DESIGN-2026-07-21.md`](TRACKB-SHARED-ND500-CPU-INTERFACE-DESIGN-2026-07-21.md)
  — **Track B unblock design: how to wire the real microword `CpuND5000` into the octobus attach path.**
  `[V]`: pure "both CPUs implement one interface" is impossible (`CpuND5000` is a leaf NuGet that cannot
  see `Emulated.HW`), and pure "adapter, zero RetroCore changes" is impossible (`AttachNd5000Cpu`/
  `AttachRealCpu`/bridge ctor are typed to the CONCRETE `CpuND500`). RECOMMEND HYBRID: extract a small
  RetroCore interface `INd500ProcessCpu` (run-thread lifecycle + `ParkOnIdle()`) implemented by
  `CpuND500` (no body changes) + a `CpuND5000Adapter` in `Emulated.HW`; retype the attach path to the
  interface; add `AttachMicrocodeCpu` that skips the functional bridge. **`CpuND5000.cs` needs NO
  changes** (adapter uses public `Cs`/`Regs`/`State`/`Memory`/`Tick()`/`Run()`/`RaiseTrap()`); 2
  OPTIONAL conveniences in `E:\Dev\Ronny\ND5000UC\CARVER-REQUEST-SHARED-CPU-INTERFACE-2026-07-21.md`.
  `[OPEN]` boot-from-CS: CpuND5000 boots from the loaded 128-bit CS and OWNS the mailbox, so the
  station CS-load must land in `CpuND5000.Cs` (DUCS checksum preserved) and the C# servicer/bridge is
  DISABLED for the microcode CPU.

- [`CARVE-S3SM5-CSLOAD-VERIFY-LOOP-2026-07-21.md`](CARVE-S3SM5-CSLOAD-VERIFY-LOOP-2026-07-21.md)
  — **What S3SM5's non-terminating `[0xD000..0xDAD3]` loop really is (task-8 root, re-characterised).**
  `[V]`: it is NOT a 3022 CS-load verify poll - there is ZERO ND-500 3022 IOX in the band (the real
  3022 devices are 0650B-0777B, absent here); the "153011B IOXT/RETG5" the emulator cited is a
  table-bit-set loop, so the CS poll lives in a different MON-60/N500M overlay, and NDBusND500IF's
  CS-load/RETG5/5CLOST + "Loading Control Store" hang are already modeled/fixed. The band is S3SM5
  PLANC swapper-management code (MON 116B UNFIX / 50B+43B OPEN+CLOSE / 61B FIXC5 / 76B SETBS / 217B
  GUIOI + table/chain scans) doing a SOFTWARE WAIT on ND-100 table state that the REAL swapper (proc 0)
  would build by answering the swapper message + building descriptor/segment/process tables
  (5ACTSWAPPER/XACTRDY/LSWPWAIT). `[I]`: the faked functional swapper never runs/answers, so the wait
  never flips and S3SM5 never falls through to the msg builder at 162150B. **FIX IS SERVICER-SIDE
  (functional swapper builds the tables), NOT a 3022 register.** `[OPEN]`: exact polled cell + tight
  loop - the trace PC span covers the whole ~1363-word routine, so a live PC HISTOGRAM over
  `[0xD000..0xDAD3]` is needed to pick the hot non-terminating loop and read the cell its SKP/JMP tests
  (candidates: outer 155225 `JMP ->155122`, chain scans 155765../156020.., back-jumps
  153021/152112/151250).

- [`CORRECTION-HOT-LOOP-IS-IOX-POLL-NOT-S3SM5-2026-07-21.md`](CORRECTION-HOT-LOOP-IS-IOX-POLL-NOT-S3SM5-2026-07-21.md)
  — **The D4 place-domain hot loop IS `030-S3SM5`, a device-poll-with-timeout; the `030-S3SM5.dis` FILE
  is CORRUPT.** `[V byte]`: the `.bin` at the hot PCs matches the live RUNTIME trace byte-for-byte
  (0xDA50=`D64F` MON117B, 0xDAB3=`BA14`, 0xDAC8=`CC7E`, 0xDACA/0xDAAD=`D10D` IOXT), so there is NO
  overlay confound - the running code is S3SM5. BUT the agent-generated `030-S3SM5.dis` shows DIFFERENT
  words than the `.bin` at the same addresses (e.g. 0xDAB3 `.dis` `045027` vs `.bin` `BA14`), so the
  `.dis` is corrupt/misaligned. That corrupt `.dis` caused BOTH the retracted "cell 27B table scan"
  (da22546/e830dda) AND the mistaken "not-S3SM5" claim (85b446b). BYTE-VERIFIED loop: `MON 117B` @0xDA50
  + dynamic `IOXT` @0xDAAD/0xDAB7 (device addr `[[B-2E]-3]+0xB`) + retry counter `[B-7A]` + `RDIV` 100;
  polls device/swapper readiness, times out -> "The Swapper stopped". **CASCADE WARNING: the corrupt
  `.dis` also underlies `CARVE-S3SM5-MSWIN-STAMP-AND-FILL-...` (builders @140771/162155) and
  `CARVE-S3SM5-CSLOAD-VERIFY-LOOP-...` (cell 27B) - their address-level S3SM5 claims are SUSPECT until
  re-derived from a CORRECT disassembly.** Still SOLID (runtime): empty MSWIN body -> 0x913B crash;
  poll times out. `[OPEN]`: regenerate a correct `030-S3SM5` disasm (diagnose the .dis byte-order/
  alignment bug), then decode MON 117B + the IOX readiness register + the emulator fix. METHOD LESSON:
  compare the `.bin`/executed WORD, not just the address, before trusting a `.dis`.
  **UPDATE 2026-07-21f (.dis fixed+committed `3dd5366`; re-analysed on the corrected `.dis`, `.bin`-cross-
  checked):** the loop is a **FILE-TO-DEVICE IMAGE LOADER**, not a poll (supersedes "device-poll" - right
  code, wrong shape). `[V]` `MON 50` OPEN @155012 -> `MON 62` RMAX (file size -> block count `[B-172]`) ->
  `MON 76` SETBS -> setup subr @155233 (`MON 154` ASSIG + `MON 255` PIOCM) -> double loop: outer over
  `[B-172]` blocks (`MON 117` RFILE), inner over `[B-170]` words streaming each via `IOXT` to device reg
  `[[B-56]-3]+0xB`; `MON 74` SETBT @155370 repositions for the next segment. **GATE @155327-155331: reads
  device STATUS at IOX reg base+2, REQUIRES bit 100B (0x40)**, else -> err path 155420. `[B-172]` = a BLOCK
  COUNT (exhaustion = COMPLETION, not timeout). VINDICATES "> Loading Swapper"; kills cell-27B scan AND
  bare-poll. Task-8 gate now crisp; 3 items `[OPEN]` (need live trace): which file `MON 50` opens; which
  device `[B-56]`/`[[B-56]-3]` is (3022/octobus vs PIOC/CAMAC - ASSIG+PIOCM hint CAMAC, do NOT assume
  3022); does it COMPLETE or SPIN. Leading hyp `[I, UNPROVEN]`: emulator iface never raises status bit
  0x40 at IOX base+2. See the doc's `2026-07-21f` section.

### Retracted 2026-07-20 [V] — do not resurrect

| Was believed | Actually |
|---|---|
| The ND-5000 swapper **is control-store microcode** and must be modelled in C# | It is **ordinary ND-500 macrocode** — `SWAPPER-K01.PSEG`, 38,161 B at physical `0x06F800`, byte-identical incl. `REV`/`-K01`. It **executes** on the functional `CpuND500`. See `ND500-D4-RUN-BLOCKER-FINDING-2026-07-19.md` §12c/§12d/§12e, and the retraction banner now on `SWAPPER-START-MECHANISM-CARVE-2026-07-19.md` |
| `LDSWA` contains a **CPU-type branch** (classic → 14B/21B/23B, 5000 → control store) | `LDSWA` (`143551`-`143621`) has **no CPU-type test**; its only descriptor test is bit 3 of `mem[mem[B-57]-22]` = the "swapper already loaded" done-bit |
| `> Loading Control Store` / `> Loading Swapper` are two **branches** of a generation choice | They are **steps 0 and 3 of one state machine**, `500IN` @`075150`, done-mask complete `0o217`. Bit 0 is tested before bit 3 — hence both print, in that order, on one machine |
| A level-12 poll at `033620` reading `-1` is the missing ND-500 signal | **Red herring.** Instruction is `LDX I 114` (*indirect*, P-relative literal pool), not `LDX ,B 114`; `033620` is in segment `017-S3SMPIT` (generic level-12 MPIT entry), not the resident; the cell is `IL12Q`=`0o007265`, the **disk driver's** software queue head, where `-1` is normal |

### The swapper image transport — ANSWERED [V] (closes register §1 B1 / octobus Q4)

`LDSWA`(143551) → `PLSWA`(144212) → `144002` (`MON 50` OPEN, `GFMAD`/`GFDEV`/`GFSEC`) → loop
`143647` → `144117` → **`MON 131` (ABSTR)** = ordinary **disk-controller DMA into ND-100 physical
memory**; destination page allocated by **`MON 61` (FIXC5)**. Path `143600`-`144400` contains only
`BFILL`, `MON 50`, `MON 131`, two 2-word `MOVEW`, `MON 43` — **no IOX, no window store loop, no
mailbox, no ACCP, no SAMSON branch**. (An earlier guess of "ACCP/DMA transport" was wrong.)

### The real `ND-500(0) timeout` gate [V]

`N500TMR` (`RP-P2-N500.NPL:300-341` @127642-127660): `RN5STATUS` ≠ `ANSWER` → check
`MAILINK.X5BRK` → if 0, raise `N5TIMOUT` (`2000B`). Plus `MP-P2-N500.NPL:362/:545`:
`IF CPUAVAILABLE NBIT 5ALIVE GO FAR EN5TIMOUT`. **Three gates:** (a) 5MPM status word becomes
`ANSWER`; (b) `5ALIVE` set in `CPUAVAILABLE`; (c) a level-12 **hardware** interrupt whose
`IDENT PL12` indexes `ITB12` (`0o153563`) to a real datafield.

### Mailbox base — how the ND-5000 legitimately learns it [READ + INFER]

`ND-05.017.01:3961`: SINTRAN **patches system parameters into the first page of
CONTROL-STORE:DATA** before the ACCP burns it. CS words `000020`-`000027` are in that page, and
`START_MESS` (`026`) / `SAMSON_CPU` (`025`) are exactly the two constants that cannot be static.
`START_MESS = 0x2000` is a **5MPM/MFbus window-relative byte address** (offset 0 = ADRZERO) — same
space as the LPARP pointer seen as `0x18000`. **No ACCP command carries a mailbox address.**

> **Emulator rule:** derive `START_MESS` / `SAMSON_CPU` from the **loaded** control store (words
> `000026`/`000025`), never hardcoded and never from the on-disk file (which holds placeholders).

Also corrected: the checksum addend is at **`base + N·8`**, not `region23[0]` — ABSRE's epilogue
(`044642`-`044644`) advances the shared index. `XMSINIT-BUFFER-GEOMETRY-CARVE-2026-07-19.md` patched.

### Method note

All four retractions shared one failure mode: **a plausible mechanism asserted from partial evidence,
then cited by later documents as fact.** Specific traps worth remembering — misreading an
addressing mode (`LDX I` vs `LDX ,B`); assuming a PC below one segment's load base is "the
resident"; treating two console strings printed in sequence as two arms of a branch; and citing
another track's *emulator* behaviour as hardware corroboration.

---

## 0f. 3022 bundle ANSWERED — RFLAG/SFLAG don't cross the bus; poll=watchdog; site-A is a buffer not a ring (added 2026-07-19)

Answer doc: [`CARVE-ANSWER-3022-FLAG-POLL-RING-2026-07-19.md`](CARVE-ANSWER-3022-FLAG-POLL-RING-2026-07-19.md).
Seeds: `CARVE-PROMPT-3022-FLAG-POLL-RING-BUNDLE-2026-07-19.md`,
`ND500-F6-MESSAGE-RING-RAW-CARVE-SEED-2026-07-19.md`, `ND500-BUS-INTERFACE-COMMAND-LADDER-ANALYSIS-2026-07-19.md`.

- **(a) RFLAG(100B)/SFLAG(101B) do NOT cross the 3022.** `FUNCS[100B]=FUNCS[101B]=ERRFP=141574B`
  **[BYTES, 030-S3SM5.bin]** = no ND-500-side op. Handler `RRFLAG/WWFLAG` (5IFUNC[100/101]) maps the
  process **data segment** via `M1MEXY` and reads `FF500=166004B` / writes `FT500=166002B`
  (`DASEGSTART=166000B`) as ordinary ND-100 memory **[NPL 5P-P2-MON60.NPL:1516-1538; SYMBOL:141-146]** —
  no IOXT/ACTIVATE/MSGHDR. Confirms the command-ladder "ND-100-cached, no command-specific 3022 traffic."
  Caller = MON 60 with 2 param ptrs (procno @`,X 6`, flag word @`,X 7`) **[BYTES, nd-500-mon-j04.prog]**.
  OPEN: L07 byte body of RRFLAG/WWFLAG in 050-S3I5PIT (README "pending").
- **(b) The background poll = the WATCHDOG `3RMICV` (MICFU=1, SENDE=-1)**, timer-armed by `LTTMR=23B`,
  re-sent on each ANSWER (RP-P2-N500.NPL:282/384/820-822; N500TMR:305-347) **[NPL+SYMBOL]**. **Site-B
  decode CONFIRMED byte-for-byte:** `N5STA(2)=3 ANSWER`, `SENDE(3)=0xFFFF=-1 watchdog`, `MICFU(6)=1`,
  `word7=0x2E9A=11930=027232B` version. It is the watchdog answer buffer, NOT the ring. "ResidentRead" =
  `3RMED=10B` (command-triggered mem read); its cadence OPEN.
- **(c) Site A (0x420E30) is a reused 200B message buffer (process-1 MESSBUFF), NOT the LAST-N500-MSG
  ring.** The `0x420E35` "03→04" is the N5STA word flipping ANSWER→5ERANSWER on buffer reuse (MICFU
  1→8), not a ring index — architect index-hypothesis **REFUTED**. The actual "last 64 messages" ring is
  NOT in the 5MPM window and NOT found in the carve/NPL/symbols; **[ASSUMPTION]** it lives in
  `ND-500-MON:PROG`'s own memory (carve `LIST-TABLE` there). Record size/capacity/head-tail UNRESOLVED.

## 0e. DOMINO/NUCLEUS/octobus-driver I/O stack BYTE-CARVED (added 2026-07-19)

Three new byte-verified docs in
`tools\sintran-segment-carver\versions\L-VSX-500\re\domino-nucleus-io\`
(+ annotated listings a-*.txt). Plan/context doc:
[`..\ND5000\OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md`](../ND5000/OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md).
Parent handoff carries the summary (its section 1.9). All addresses L07.

UPDATE 2026-07-20: the plan was critically reviewed
([`..\ND5000\OCTOBUS-PLAN-CRITICAL-REVIEW-2026-07-20.md`](../ND5000/OCTOBUS-PLAN-CRITICAL-REVIEW-2026-07-20.md))
and a SCSI-DIOC plan was added
([`..\ND5000\SCSI-DIOC-OCTOBUS-EMULATION-PLAN-2026-07-20.md`](../ND5000/SCSI-DIOC-OCTOBUS-EMULATION-PLAN-2026-07-20.md)).
Scheduled follow-up carves (its phase S0): CONKI @040765 — DONE
2026-07-20 [V]: **incoming octobus KICK 1 dispatches to DKICK @044747**
(NKINI -> CONKI(T=1, A=14B=PIL level 12, X=0, B=125144); receive chain
035555 -> 036047 KICKENT[frame & 17B] -> 036233 fires level 12 with
P := mem[125143] = DKICK; receiver masks with 17B so kicks 20B-37B alias
0-17B; full doc `re\domino-nucleus-io\CONKI-KICKENT-CARVE.md`). Still
DOMDF initializer: CARVED 2026-07-20 [V] - it is the FILSYS DOMINO
pool/port module in 006-S3FS base 026000B (QUINI @134206 writes
DLPRT/DSVER via MON 347 fn 1; GPOOL/RGPOO/RCPOO write PDF.DRPRT via
DOPPR = MON 347 fn 3 open-port-by-NAME; unit binding = named pool port +
DXPOO/OPAIN, the "DSVER+32..67 static header" is DISPROVEN as don't-care
tail; BDTMU/BDTMV live in RPIT not MPIT - poisoned prior killed; doc
`re\domino-nucleus-io\DOMDF-INITIALIZER-CARVE.md`). Segment 105-S3INKSE
interior: CARVED 2026-07-20 [V] - PLANC-compiled server; doNuc
dispatcher @037033 (fns 1..14B, table dd-verified); fn 10B @047432 =
descriptor create/provision writing port +20 KICKDEST / +30 OWNID
(coherence vs kernel layout PASSED); doc
`re\domino-nucleus-io\NKSE-SERVER-INTERIOR-CARVE.md`. Remaining [OPEN]
tail: DRPRT/DLPRT sub-offset pin, freelist head (runtime global), full
NCALL per-word map (live round-trip), fn 11B-14B bodies. PROMAN auto-run: RESOLVED 2026-07-20 [V]
SAFE — PROMAN never runs at boot on this image (live @LIST-RT-PROGRAMS:
PASSIVE P=0; no PMA-* files on the pack; segments 120/121=PROMAN
string-proven); emulated DIOC stations 10B-13B get NO boot-protocol
traffic (`re\domino-nucleus-io\PROMAN-AUTORUN-RECON.md`). Standing
correction: host->remote NUCLEUS kick is byte-verified kick 1 (NUCKI),
NOT kick 5 (that is only the kick-name table); the remote->host kick is
now ALSO proven = 1.

### BDIO / DOMINO nucleus block-I/O (level 12 + monitor level)

Doc: `re\domino-nucleus-io\BDIO-DOMINO-DRIVER-CARVE.md`. BYTE-VERIFIED in
017-S3SMPIT (=026-S3IMPIT), base 032000B.

- The DOMINO disk path does NOT use the 3022/MPM message block: it is
  nucleus messaging (NKWRI/NKSEN/NKREC/NKREA at 043411/042171/043076/
  043375) through the global DOMDF=041064 record (body at DSVER=041104B),
  level-12 wait via WT12=033616 with DOMDF.NFUNC(+6) = REBDI=074246 as the
  continuation. Function codes: read=166B (size 74B), write=167B (70B),
  compare=213B (70B); NKREA read-back max 76B.
- Level-12 start: BDMTR (monitor level) arms level 12 with IRW LV12(140B):
  B=controller DF, X=que DF, P=controller.STDRIV(-2), then MST PID bit 12.
  Byte-verified at 073515-073526.
- DCNVA 073750 converts ND-100 phys word addr -> DOMINO byte addr:
  `((addr - (N500D.ADRZERO << 10dec)) << 1) | bit31`; bias cached by
  self-modifying the entry word to 124012 (JMP). N500D=051767 [SYMBOL-2],
  ADRZERO=+60. Same bit-31 semantics as the ND-500 MPM convention.
- HSTAT (queue DF +10): -1 illegal fn, -2 nucleus reject (SINEC 1661),
  -3 illegal mem addr, -4 device error (SINEC 1662 + BDTMU retry),
  -5 = statuses 104031B/104651B/104622B. Mirror-pool change arms BDTMV.
- Evidence: 13 dd-reproduced anchors + 40 literal-pool symbol hits.
  NPL = MP-P2-DISK-START.NPL (different revision, logic-only, +237B shift).

### Octobus driver routine bodies

Doc: `re\domino-nucleus-io\OCTOBUS-DRIVER-ROUTINES-CARVE.md`. Full
annotated disassembly + pseudo-C: XKICK500/LV12KICK (146526/146555),
XRS5CPU (146642), RS5CPU (146700), 5OMBREAD/I5OMBR/GN5CPUDF
(146756/147240/147252), CON5OMD (147271), MFPREPARE (147300), CON5IDENT
(147334), 5MTRANS (143445), 5MRDTRANS (144740) - all 026-S3IMPIT (load
32000B, = 017-S3SMPIT) - plus SKICK/SIDEN (037254/037256), MBSEND
(037425), OMBREAD (037660).

Key byte-proven facts [V]:
- Overlay proof: 14 siblings at NPL+200B; every literal-pool pointer
  resolves to a named L07 symbol.
- LMFIELD = 011545, LMDF = 011537 (LMDF[0] = 5OMDNO, runtime-allocated by
  CON5OMD); DPITPHYS = 0, DPITBANK = 1 in this build.
- CPU df offsets: 5STATION=17B, MAILINK=22B, CPUAVAILABLE=27B (5ALIVE =
  bit 13 dec, 5CPUTYPE mask 7, SAMSON=3), CPUNO=-14B, stride 5CPUDFSZ=46B;
  list bounds cells S5CPUDF=052222 / E5CPUDF=052404; 5MBBANK cell 004654.
- SKICK builds C|K|station<<8|kick and IOXes control:=4 / frame /
  control:=1 on the OUTPUT base (df[-3]=HDEV+4) when idle, else queues in
  a single-frame ring; SIDEN = same body, no K bit. Errors 13B-20B.
- MBSEND has NO IOXT: validates (station 1..76B, OMD <=17B, length 1..255
  BYTES -> errors 101430/101431/101427), pops a CBPOOL buffer (free head
  007341 / count 007342), copies payload from LMFIELD+4, queues on the TX
  df, and if idle FIRES LEVEL 13 with P:=SOCTW(036342). (Corrects the
  catalog row that placed "IOXT at 037320+" under MBSEND - 037320 is
  SKICK's direct-TX path.)
- OMBREAD receive record: [0]=src station, [1]=src OMD, [2]=broadcast bit,
  [3]=byte count, +4=payload; empty status 101410 (cell 147171).
- 5OMBREAD: SAMSON source range is 70B..77B in L07 (LN5DEST=77, not M06's
  73); MPFATAL @146750 = 1,0,0,1,0,0,0,0,0,1,1,0; ack/nack ->
  CPUAVAILABLE|=5ALIVE; mp hwfault(200B)/trap(201B) with CMICP=1 ->
  shadow-id patch into S4, record LMFIELD+2 len+4; else LMFIELD+3 len+2;
  MF etype -> 9FLER + MFACK reply; SEC codes ORed with N5SECCODE=2000B.
  9FLER record: SEC at LMREC+2, source station at LMREC+3.
- MFPREPARE wire body (station 2..6, OMD 4, 3 bytes): 0E 01 <5OMDNO>;
  CON5IDENT (SAMSON, OMD 3, 7 bytes): 0E 01 <5OMDNO> 00 00 00 00.
- 5MTRANS: 5MPM displacements 5MNWA=100B, 5MREQ=105B, 5MEMA=106B,
  5MLGN=110B, 5MDIS=111B, 5DSEC=112B, 5MNOS=115B, PLINK=147B; disk queue
  element RTRES=1/NLINK=5/ABFUN=14B/MEMAD=15B/ABPA2=17B/ABP31=21B/
  REQID=25B/ADMESS=26B/5MNOWAIT=27B; function codes 60 (read+clear cache),
  61 (write), 66 (read keep cache); M5TRA=000012 = per-controller entry at
  disk-controller df offset 12B (JPL I ,B 12); wait status 5MWAIT=22B;
  success -> 5MRDTRANS (pointer cell 144014 = 144740).
Open: OMBREAD entry[-10..-12] status semantics; helper 036765
level-dispatch details; MBSEND code 101426 site.

### NUCLEUS kernel + the NUCLEUS <-> ND-500 bridge (MON 347)

Docs: `re\domino-nucleus-io\NUCLEUS-PRIMITIVES-CARVE.md` (primitives +
kernel structures + kick path + MON 347B) and NUCLEUS-SEGMENTS-RECON.md
(segments 104-107 recon + follow-up target list). Summary in the parent
handoff section 1.9; ND-500-specific facts:

- MP-P2-N500 L1381 `IF A = 347 GO 5SERVER` [NPL-V] lands in **ENUCL =
  050123** (MPIT): function code from 5MPM message word +102; fn 0..6 ->
  N5FU0 (NKGET), N5FU1 (NKSEN under IOF), N5FU2 (NKREC), N5FU3/5/6; fn 7
  -> driver code 137167. Answers via NURET 047315 (writes message words
  +110/+0/+2; chains resident 023044 + driver cells 145466/135067).
  ND-500 owner ids = CLUST (041574) + process number. MCTAB[347B]=047072
  [V] = SERVE (the MON-CALL-INDEX name "MGDAE" is a flat-table collision;
  overlay = MPIT, not 003-S3CP - index row needs that fix).
- N5FU5 tail (050100) emits SKICK(A=1,X=0,T=station) directly - an
  ND-500-initiated octobus NUCLEUS kick.
- 5NFUN..5NMBU (047541-047555) are the ND-500 NUCLEUS parameter cells in
  MPIT (zero on disk, runtime-populated).
- NUCLEUS delayed abort NKREL -> 5NUREL (MP-P2-N500 L563 area) [NPL-V],
  body not carved this pass.
- [OPEN] ENKIC=047526 (N500-SYMBOLS, ACCP family: NSPIT/GMESS/ACCPE/
  VPARP/OCTOS/NMPIT) resolves in NO carved overlay tried; callers exist in
  007-S3DMAC, 130-CFT, 135-XFTRAD, 134-SNA3270.

---

## 0d. Q7 ANSWERED - ND-500 completion detection is INTERRUPT-DRIVEN (level 12), not RSTA5 poll (added 2026-07-18)

Answer doc: [`CARVE-ANSWER-Q7-COMPLETION-POLL-VS-INTERRUPT.md`](CARVE-ANSWER-Q7-COMPLETION-POLL-VS-INTERRUPT.md).

**Verdict [V-NPL + V symbols]: INTERRUPT-DRIVEN.** Walked `5STDRIV` in
`../NPL-SOURCE/NPL/MP-P2-N500.NPL:659-697`. When level 12 fires (LV12B=000140 octal =
level 12 [V]; re-armed by `WT12` at :693, no busy-poll), `5STDRIV` reads `RSTA5` via
`CLE5STATUS` ONLY to branch on the ERROR group (`IF A/\720><0`, bits 4/6/7/8 =
5PAGF/5DMAER/5PFAIL/5POWOF), then UNCONDITIONALLY drains the `MAILINK` exec-queue and
calls `CHN5STATUS` per message. `CHN5STATUS` (:730) reads the MPM message field `N5STA`
(offset 2 [V]) to discriminate answer / 5ERANSWER / restart - a shared-memory read, not a
hardware poll. **`RSTA5` (offset 2 from HDEV [V]) has NO completion bit** - its full bit
map (`XC-P2-N500.NPL:41-45`) is all error/power/clock/lock, so there is nothing to poll for
"done". The activate path `XACT500` (:3057) reads `RSTA5` once and ends by the source's own
`% Enable for interrupt` block (`LCON5:=10`, then `LSTA5`/`LCON5`/`SLOC5`) and returns - no
wait loop. The only `RSTA5` spin in the file is `XTER500`'s STOP handshake (`WHILE A BIT
5ILOCK`, :2938), not normal completion. No IOX IDENT read inside `5STDRIV` - the level-12
LINE is the detector; the "ident=16" in the request is neither confirmed nor needed.

Decision tests: (1) branch on a finished bit? NO. (2) assume entered=>finished, status only
discriminates type/error? YES. (3) poll loop outside 5STDRIV that level 12 nudges? NO.
(4) status(error) before draining queue; payload from MPM `N5STA` not `RSTA5`; master-clear
only on timeout; ident not read.

**GAP:** byte-level disassembly of L07 `5STDR` (symbol `5STDR = 0xBA08` = octal 135010) not
done - verdict rests on [V-NPL] logic + [V] symbols; NPL is a different revision (listing
address octal 134610 vs L07 135010, ~0x80-word drift). Byte cross-check is the follow-up.

## 0c. ND LINKER B01 "(-677:52)" - V10: jumpg fork is a CHARACTER dispatch, 0x42 = 'B' (correct, not mis-derived); fault re-pinned at B0040C3C (2026-07-18)

**V10 (current):** [`CARVE-ANSWER-LINKER-LOAD-ERROR52-V10.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V10.md).
Answers the "jumpg $0xB004A588+ ... b.0x30=0x42 -> error 52" relay.
- **`b.0x30` holds a CHARACTER, not an arg-type code** [V]: range-checked as a char
  (`comp2 b.0x30,$0x3C '<'` B003C8C7; `,$0xC7` B003C8CD) and the error-52 arm compares it to
  **`0x41 'A'`** (B003D09F). So `0x42` is literally **`'B'`**, the first name char of `B:NRF` -
  **the dispatch selector is CORRECT, not mis-derived.**
- **Fork map** [V]: `B003C8E2 div4 b.0x30,$0x100 -> b.0x48`; `B003C8EB by2 comp $0xB004A584`
  (bound byte = 0x0D); `B003C8F1 if >> go $0xE20` -> out-of-range arm `B003D711`;
  `B003C8F4 jumpg $0xB004A588+`; fall-through calls `B003E0F5`. The error-52 arm is `B003D08F`
  (`call B003DCE2` then `B003D0E2 call B0040C3C`).
- **`B004A570` region is a DATA constant pool** (referenced as data by `B003C850 by scopa
  $0xB004A570`, `B003C876 bmove $0xB004A578`), NOT the "counter code" the linear disassembler shows.
- **[OPEN]** jumpg entry stride/format + div4 result placement - unverifiable from static bytes,
  NOT guessed. Now MOOT for the fix: since 0x42 is correct, the fault is `B0040C3C`'s grammar gate.
- **Action unchanged from V9:** run `LOAD "B:NRF"` (exit A) / `LOAD B.NRF` (exit B). Decoding the
  table is unnecessary.

**V9:** [`CARVE-ANSWER-LINKER-LOAD-ERROR52-V9.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V9.md).
H2 fully disproven by nd500x runtime: `B0040C3C` IS LOAD's intended arg-resolver (reached
`B003C8F4->B003D08F->B003D0E2`), not a misroute; the object-open routines are simply downstream of a
check that aborts first.
- **Under-stated before, now corrected:** `B0040C3C` has **TWO accept exits** - `B0040D3F` (arg
  contains a `"` 0x22, found by the quote-scan `B0040D33-D40`) OR `B0040D84` (`b.0x49==4`, i.e. a `.`
  0x2E). A bare colon `B:NRF` has neither -> error 52. Arg contract = "quoted, or dot-bearing name".
- The `{0xB0048FEC,5,9}`="B:NRF" descriptor is the RAW command-line slice set by `B003C8F4`; the
  recursive parser `B003CFDA` (B0040C3C sites B003D064 & B003D0E2; dispatcher B004D4F4 sel 0x28/0x23)
  never inserts a `"` or `.`.
- **Decisive live test handed back:** type `LOAD "B:NRF"` (exit A) or `LOAD B.NRF` (exit B); whichever
  passes names the contract and tells us what the input path must produce. Recommend pausing static
  drilling until that one-line test picks the exit.

**V8 (LOAD is a real command; data-driven/CPS dispatch):** [`CARVE-ANSWER-LINKER-LOAD-ERROR52-V8.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V8.md).
nd500x proved live that LOAD never enters the object-open subtree (grep of the LOAD-round trace: 0
hits on B004E874/B004CABC/B004AEBC) and dies in the B003Cxxx symbol/spec resolver at B0040C3C.
- **LOAD is a real, first-class command** (DSEG command-name tables at file 0x88a54 full set / 0x88cf4
  restricted set = exactly the session's commands; LOAD at file 0x88b52). So NOT "unrecognized ->
  symbol"; LOAD dispatches as a command and its ARGUMENT `B:NRF` is sent to the wrong parser.
- Dispatch is **data-driven + indirect (jumpg/CPS)**: shared prologue B0031504-152B builds context
  0xB003DFE4-DFF8, jumpg 0xB003DFE8; continuation B0031531 hands a per-command DESCRIPTOR 0xB003EE90
  to executor **B002EF7F**. The file-vs-symbol arg routing lives in that descriptor/executor layer.
- **POISONED PRIORS (mine, deleted):** the `0xB00530BC` keyword-table + `B004ACD9` dispatch model is
  wrong (0xB00530BC is a structured field table; B004ACD9 never reached, live break count 0). Static
  caller-tracing cannot reconstruct this dispatch (all indirect jumpg).
- **Next (split by who's fastest):** nd500x dumps LOAD's vs OPEN-DOMAIN's command descriptor
  (via B002EF7F / the 0xB003EE90-style pointer); carver then decodes B002EF7F + descriptor format to
  find the arg-type selector that routes to the symbol resolver.

**V7 (object-OPEN subtree disjoint) - V6's dot-form model RETRACTED:**
[`CARVE-ANSWER-LINKER-LOAD-ERROR52-V7.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V7.md).
- **POISONED PRIOR (delete V6's NET claim):** "DEABF's dot-form B.NRF becomes B0040C3C's input" is
  FALSE - nd500x set DEABF OUT='B.NRF' live and error 52 was byte-unchanged. Bytes agree: B0040C3C
  parses its window at `B0040C4F` BEFORE its internal DEABF at `B0040D5C`; and the `B003DDCD` resolve
  subroutine is never reached (no-dot branch `B003DD82 -> B003DE13` skips it). The dot-form idea is dead.
- **Verified call graph:** the USER-OBJECT `MON 50B OPEN` is `B004E874` (dynamic `'`-quoted name) in
  routine `B004E80F`, reached `B004AEBC`(post command-dispatch)/`B004DC33` -> `B004E80F`. The other
  OPEN `B004CABC` opens a FIXED-name (`$0xB0054314`, mode 3) work/scratch file, NOT the object.
- The object-open subtree does **not** pass through `B0040C3C`/`B003CFDA`. The error-52 path is a
  SEPARATE mutually-recursive name subsystem (`B003CFDA`/`B003D19E`/`B003D337`/`B003D442` -> `B0040C3C`).
  So nd500x's hypothesis 2 (LOAD mis-routed into the wrong resolver) is the live lead. `B0040C3C`'s
  `;)`/`.` stage grammar looks like a symbol/spec parser, not a file-name parser.
- **OPEN (not yet decoded):** the command keyword table at `0xB00530BC` (matcher `B004ACD9` after the
  MON 511B read at `B004ACBF`) - decoding it names LOAD's intended handler. Offered to carve next.

**V6 (RETRACTED dot-form model) / canonicalizer B003DCE2 contract:**
[`CARVE-ANSWER-LINKER-LOAD-ERROR52-V6.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V6.md). nd500x confirmed
V5 live (break at B0040D85 fires at the B0040C3C gate, I2=0xAE=DEABF; parse window {0xB0048FEC,5,9}=
"B:NRF" ends at stage 1). New byte findings on `B003DCE2` (the name canonicalizer feeding B0040C3C):
- **B003DCE2 SPLITS its input on `.`(0x2E) (B003DD26-DD35); it never ADDS a `.`.** No-dot input is
  carried through unchanged. So a colon `B:NRF` stays dot-less -> stage 1 -> error 52.
- `b.0xBC` is a **scratch descriptor** assembled from input ptr `b.0x14` (B003DD3F/DD52), NOT a
  stored default-type source - corrects the relay's assumption.
- **B003DCE2 is NOT MON-free** (corrects relay point 5): it calls the SAME dispatcher `B004D4F4`
  (DEABF's) at `B003DDCD` (selector 0x28) and `B003DDEE` (0x23). Those are the file-system
  resolution calls the emulator must check. [selector->MON decode is [I], confirm live.]
- **Net root-cause model:** DEABF resolves `B:NRF` -> `B.NRF` (dot-form; nd500x's own observation).
  The real-HW `.` is that RESOLVED name; B0040C3C must parse `B.NRF`. On the emulator the resolution
  op's dot-form is not propagating, so B003DCE2 carries the raw colon window and B0040C3C sees no
  `.`. Fix is in what the B003DCE2 dispatcher call returns - NOT a default-append, NOT b.0x49.
- The prompt buffer `0xB0035CEC` windowed [0,8] = "File name" (a PROMPT pass, not the arg pass);
  multiple B003DCE2 passes exist - the erroring one windows the raw line to `B:NRF`.

**V5 (the parse-STAGE gate itself):**
[`CARVE-ANSWER-LINKER-LOAD-ERROR52-V5.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V5.md). After the V4
line-length issue was moved past (DEABF now RESOLVES B:NRF -> found), the linker still errors 52 at a
NEW gate. Byte-verified in `linker-b01.dom.asm`:
- Success gate `B0040D7D` = `comp2 b.0x49,$0x4` and runs on **both** K paths; K only gates the
  `B0040C44` save-link helper (which RETURNS). So preserving DEABF's K is necessary-but-NOT-sufficient.
- `b.0x49` = parse-stage counter, init 1 (`B0040C59`); `;`->2, `)`->3, `.`(0x2E)->4 (`B0040CC1`);
  **`:`(0x3A) sets flag b.0x4C but does NOT advance the stage**. So `B:NRF` ends at stage 1 -> error 52.
- Real fix is upstream: what `B0040C3C` parses is the OUTPUT of `B003CFDA`/`B003DCE2` (caller
  `B003D0E2`, callee `b.0x18`=caller `b.0x20`), NOT the raw "LOAD B:NRF" line. Probe: dump that
  descriptor; it must reach a `.` (stage 4).
- "error 52" is linker-internal: `B0040D85` jumps into the variadic message FORMATTER at `B004DADC`
  (NOT an error-code table) -> blank message slot. The real object `MON 50B OPEN` is downstream at
  `B004CABC`/`B004E874`, never reached because this gate errors first.
- CAVEAT to reconcile: "(-677:52)" also names V4's scanner error (0x9016). The `(-677:52)` render is
  the generic DIV/MOD-64 formatter; confirm whether the two error sites share one status word or the
  team is now genuinely at the later B0040C3C gate.

**V4 (line-length scanner, prior gate):**
[`CARVE-ANSWER-LINKER-LOAD-ERROR52-V4.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V4.md).
History: [`CARVE-ANSWER-LINKER-LOAD-ERROR52-V3.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-V3.md)
(raise site + 0x90xx family correct; "71 delimiter-free chars" content-explanation retracted),
[`CARVE-ANSWER-LINKER-LOAD-ERROR52-REFINED.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52-REFINED.md)
(display chain correct; event attribution retracted) and
[`CARVE-ANSWER-LINKER-LOAD-ERROR52.md`](CARVE-ANSWER-LINKER-LOAD-ERROR52.md) (retracted).

**V4 mechanism [V]:** for the file-name parameter kind (0x42, bitmap 0xB0048F20), scanner
B0036620's token loop consumes chars <= 0x20 (NUL/space/CR) silently - only %, &, comma, =
terminate; otherwise the token ends at the COUNT limit r.0x94 - 1 (read live from
0xB00491D4 = context 0xB0049140+0x94 at B0036725). Token then copied into B003472C's local
b.0x98 by B00401FC, whose returned desc {ptr, 0, len-1} becomes b.0x44/0x48/0x4C. So the
fixed [0,70] = r.0x94 = 71 at scan time = the LINE LENGTH set at B003519B from line reader
**B003F876**'s returned descriptor (B003F876 = editor/history layer, 0xB004D8xx state,
162-byte history records). **Emulator-side bug: the input path delivers/claims 71-byte
lines.** Decisive probe: write-watch 0xB00491D4, expect 0x47; then read B003F876's return
desc at B0035158. Not stale state - rebuilt every call from the live count.

**ADDRESSING CORRECTION: DSEG file offset = VA - 0xB0000000 + 0x57800, NOT +0x58000**
(proof: command-table record ptr 0xB00314F4 -> "CLOSE" at file 0x88CF4). All prior STATIC
DSEG content reads made with +0x58000 are poisoned; instruction-operand facts survive.

Verified mechanism [V]: "(SSI:NN)" = ONE error word printed as DIV 64 and MOD 64 (octal),
at B003604F/B00360B2 inside reporter **B0035C88** (arg r.0x30). Report hub = **B0015B3F**
(code in H1; 999 = already-reported sentinel); display = code - 0x443 + mem[0xB002C5DC],
and nd500x's trace (H1=0x9016 -> printed 0x906A) proves **mem[0xB002C5DC] = 0x497** at
runtime, so display = code + 0x54. "(-677:52)" = word 0x906A = raw code **0x9016 + 0x54**;
the "-677" pseudo-SSI is a rebase artifact, not a subsystem id.

**The real bug: 0x9016 = "parameter too long", parked at B0035291 inside B003472C - the
universal read-one-parameter routine** (~100 call sites; LOAD calls it at B001648A/B0016689
with prompt "File name", default ":NRF", dest = LOAD's 65-byte name slot {b.0x18,0,0x40}
built at B0016471-B0016481). Token comes from scanner B0036620; delimiter bitmap at DSEG
0xB0048F40 = {NUL, %, &, comma} ONLY (space is NOT a delimiter); line buffer = 0xB0048FEC
(256 bytes). nd500x's run answered a "File name" prompt with a 71-char delimiter-free line:
72 > 65 -> 0x9016 -> deferred retk at B003530B -> LOAD aborts (rethrow B0016446). LOAD's
collection loop ends normally only on an EMPTY answer (parked 0x9011 tolerated at B00164B0).
0xB0048CFC = deferred-error cell; family: 0x9011 no-parameter, 0x9014 copy phase, 0x9015
line-input layer (B0033996), 0x9016 too-long (B0035291, B003541F).
**Not domain state, not segments, not DDBTABLES, not the script logic - the input FEED to
the second File-name prompt is wrong on the emulator side.** Decisive dump: 256 bytes at
VA 0xB0048FEC at the break = the offending line verbatim.

Poisoned priors retracted: (1) 0x106A-as-the-52 (startup DDBTABLES check B004AFBE/B004AFC3);
(2) "-677 is garbage"; (3) **"0x906A = internal 0x46D = error 42 segment-used bit" - WRONG**
(assumed base 0xFFFF9040; real base 0x497). The 0x46D raise sites B001735E/B00185D2 and
their segment-ATT test (desc stride 0x1C, ATT byte +0xA, mask 0x20) remain correctly carved
facts about THOSE routines but never fired in this event.

## 0b. ND LINKER B01 config-prompt carve ANSWERED (added 2026-07-17)

The nd500x session's four questions on the linker's config-prompt "state machine" are
answered in [`CARVE-ANSWER-LINKER-B01-CONFIG-PROMPTS.md`](CARVE-ANSWER-LINKER-B01-CONFIG-PROMPTS.md)
(binary at `D:\ND\500\nd-linker\`, read-only). Three request premises disproven from bytes:
0xB0030DE8 IS written (5 sites, from the item record's +0x3C answer field); B0047162-73 is a
bounded copy loop, not a wait; B004D4F4 is an I/O SERVICE GATEWAY (function code -> jumpg
case ladder; function 1 = read char, masked 0x7F, LF/VT/CR terminators), not the command
loop. The "prompt state machine" = a LINEAR per-parameter prompt sequence (B0014341-B0014626);
B0035319/B003472C = token fetchers on the B0048Cxx tokenizer datafield (B0048CE0 delimiter
byte; refill via B0038FDC when B0048DAC set); B0006FDC announces the two booleans (writers
B0007796/B000719E). Yes/No is a token match via B003C66E, not a byte compare. The 0xB0002000
region = the PLANC CALL STACK (init at B0013B41: base 0x1ABC, limit 0x10000) - nothing to
fill. Escape = feed real answer tokens interactively, not a mode-word poke.

## 0a. ND-5000 activation work flag + head cell ANSWERED (added 2026-07-17)

O1's blocker ("which cell does activation link the message address into; who sets the halfword
work flag the microcode IDLE poll spins on") is answered at NPL grade in
[`../ND5000/CARVE-ANSWER-ND5000-ACTIVATION-WORKFLAG.md`](../ND5000/CARVE-ANSWER-ND5000-ACTIVATION-WORKFLAG.md):
on ND-5000 there is **no MAR/head-cell write** (`XACT500` -> `GO XACTRDY`, NNJ14); the message
address goes only into the ex-queue (`ITO500XQ`) and the **X5FIF ring** (`ITOFIFOQ`; X500DF
header: X5SEM=0, X5HEN=3, X5FYL=4, X5MXF=5, X5FIF=6-7 = 32-bit ring base). The work flag =
**X5ACT, word 5 of the per-CPU MAILINK extension block** (stride 5EXTD=200B): init -1
(XMSINIT), set **0** by `XACTRDY`/ACT51 (145500B) = "work pending"; octobus kick (N100KICK)
is only the preempt path. The flat symbol table collides here (X5FYL=4/X5MXF=5 are X500DF-
relative; X5CPU=4/X5ACT=5/X5PRO=6 are MAILINK-relative) - do not mix bases. Also recorded:
CMSYSPAR=016B, N100IDENT=1, FN5DEST=070B, LN5DEST=073B, SYSPAR=111B (16-word block, MON60
fn 103/104). OPEN there: FIFOB identity.

**Follow-up ANSWERED 2026-07-17** in
[`../ND5000/CARVE-ANSWER-SYSPAR-LSYSPAR-DISAMBIGUATION.md`](../ND5000/CARVE-ANSWER-SYSPAR-LSYSPAR-DISAMBIGUATION.md):
the 3 micro-command-1 words are **NOT** the N500DF+111B block - they are the CON5IDENT
CMSYSPAR payload `S5=5OMDNO<<8, S6=0, S7=0` (5OMDNO = runtime OMD from CONOMD; live 10B
reproduces O1's observed GIVEINT word 100401B exactly). N500DF+SYSPAR(111B) = the ND-500
Monitor SET-SYSTEM-PARAMETERS tunables (ND-60.136 sec 8.10.11; 10 named params, word order
[I]), touched only by MON60 fn 103/104. Name collision, two different structures.

**Follow-up ANSWERED 2026-07-19** in
[`../ND5000/CARVE-ANSWER-OCTOBUS-MAILBOX-ACTIVATION-2026-07-19.md`](../ND5000/CARVE-ANSWER-OCTOBUS-MAILBOX-ACTIVATION-2026-07-19.md):
the octobus-emulation blocker "the 3RMICV that never reaches us / Wrong microprogram". Confirms
the CS-load-stage activation is the **`X5ACT:=0`** write (`ACT51`, MP-P2-N500.NPL:3027 `145500`),
NOT a kick (kick = preempt-only `ACT52`); **`3RMICV` (MICFU=1) is the ND-500 WATCHDOG** carried
on the same ex-queue + `ACTRDY` (RP-P2-N500.NPL:384-390 `130023`), and its miss triggers
`N5TIMOUT/RSTARTALL` (not literally "Wrong microprogram" - that string is [OPEN]). The mailbox is
at a **boot-allocated MPM page** `5MBBANK = 5FPMAILBOX<<10`, header at `+X500DF`, per-CPU block at
`+n*200B` - NEVER at MPM offset 0, which is why `ConfigureMailbox(0x420000)` misses. Emulator fix:
discover the base from SINTRAN's own `X5ACT` `0xFFFF->0x0000` write (address - 0x0A = ext block),
trigger the servicer on that write (keep the OCB kick as the preempt trigger), and answer
`N5STA:=3` (+ version `027232B`@HW7, CPUPAR `001741B`@HW `0o10` for the RMVER path; watchdog reads
neither). OPEN: exact "Wrong microprogram" string source; window-offset attribution; pre-CS-load
vs post-start ordering of the first 3RMICV.

**CS-load "Wrong microprogram" CORRECTED 2026-07-19** — the newest byte-verified carve
[`../ND5000/CARVE-ANSWER-OCTOBUS-WRONG-MICROPROGRAM-2026-07-19.md`](../ND5000/CARVE-ANSWER-OCTOBUS-WRONG-MICROPROGRAM-2026-07-19.md)
**SUPERSEDES** the earlier `CARVE-ANSWER-OCTOBUS-CSLOAD-VERSION-CHECK-2026-07-19.md` (which mis-attributed
the block to VPARP echo / an OCB 202/203 fault). **Both of those framings are refuted by a live
bidirectional ACCP wire trace (2026-07-19):**
- **VPARP is a pure §5.3.16 self-consistency echo and our reply is byte-correct** on the wire
  (`VPARP -> [00 65 96 9B 49]` = SINTRAN's own written word). VPARP is NOT the blocker.
- **"Microprogram error: Wrong microprogram" is SINTRAN status `EWRON = 002203B`** (N500-SYMBOLS
  L07:1525, rendered from `014-S3ERRP.bin`), set **ND-100-side** by the ND-500 **swapper** CS-load path
  when the **CPU type/model it reads != the control-store image word-7 model**. It is **NOT** an OCB
  202/203 decode: `5OMBREAD @146556` takes its silent `5ALIVE` branch for our `ETYPE=0` MFACK (proven).
  J04 (thin MON60 client) just retries `LOAD-CONTROL-STORE` on status `ECSLOAD=002032B`, re-running the
  prologue -> endless `DISKICK/STOPMIC/CPURES/LPARP/VPARP` loop.
- **The model check is NOT an octobus command:** the complete ACCP trace (boot -> loop) has ONLY
  CMSYSPAR/RTEST/CMALI/DISKICK/STOPMIC/CPURES/LPARP/VPARP — no READ-CPU-MODEL (§5.3.57) or any
  model/version read. The swapper reads the compared model from ND-100-internal state (cached / mailbox
  / MPM cell). The prologue sender is the swapper + L07 `MONACCP=157`/`STSELFTST=155` (commented out in
  M06 NPL), living in uncarved `030-S3SM5.bin`/`062-S3SSM5.bin`/`116-S3SERWD.bin`.
- **New lead / fix target:** the monitor `VERSION` cmd shows `Micro program.: 0` + `Module: MB.0 ALU.3
  AAP.0 IDAC.0 ... ACCP.0` (mostly `.0`) — the CPU module/model config the swapper compares, reported
  (mostly) zero by the emulator. FIX = report the ND-5800 module/model config + micro version
  (drive from the loaded CS image word-7 / word-1, not a hardcoded constant) at wherever the swapper
  reads them. OPEN (carve in flight, swapper EWRON setter): the exact compare source + location, and
  which module/version cells the swapper actually reads.

---

## 0i. HANDOFF — 3022/swapper track, session ending 2026-07-20

[`HANDOFF-3022-SWAPPER-TRACK-2026-07-20.md`](HANDOFF-3022-SWAPPER-TRACK-2026-07-20.md) — where D4
stands (swapper executing, PC `0x04` -> `0x913B`), what is established, the seven emulator bugs fixed,
the five retracted claims, the ordered next actions, and the working notes (flaky harness, available
diagnostics, dirty-tree caveats).

## 0h. OPEN QUESTIONS REGISTER — everything this track does not know (added 2026-07-20)

[`OPEN-QUESTIONS-REGISTER-2026-07-20.md`](OPEN-QUESTIONS-REGISTER-2026-07-20.md) lists every open
item with its answer route (CARVE / MICROCODE / LIVE / MANUAL) and priority. Read it before starting
any ND-500 work, and add to it rather than re-deriving. Top five: **A1** who builds the PCB/PST;
**A2** where the program segment number comes from at 3START; **A3** where PSTP comes from; **B1**
what transport delivers the swapper PSEG/DSEG (no RESIWR names them); **C1** whether B30 accepts
MICFU 21B. It also records the four claims this track had to RETRACT, so they are not re-adopted.

## 0g. SWAPPER EXECUTES on the emulated CPU; its LINK SEGMENT is 1 — carve resolves the MMU set-up (added 2026-07-20)

Finding doc: [`ND500-D4-RUN-BLOCKER-FINDING-2026-07-19.md`](ND500-D4-RUN-BLOCKER-FINDING-2026-07-19.md)
sections 12d-12i. Question set for the microcode track:
[`QUESTIONS-FOR-ND5000-MICROCODE-SWAPPER-START-2026-07-20.md`](QUESTIONS-FOR-ND5000-MICROCODE-SWAPPER-START-2026-07-20.md).

The real ND-500 swapper now RUNS on the functional `CpuND500` under live SINTRAN L. Nothing is faked
(swapper injection, the `AnnounceSwapperAlive` announce, and the 3MONCO "parked but alive" intercept
were all deleted).

- **SINTRAN places the swapper's EXECUTABLE itself [BYTES].** MPM physical `0x06F800`, 19 dense pages,
  byte-for-byte identical to `swapper/SWAPPER-K01.PSEG` (38,161 bytes, incl. the `REV`/`-K01` tags).
  It arrives on the "> Loading Swapper" path; **no `14B` RESIWR ever names that address** (those stop
  at `0x6F7FF` and are 40/44 ZERO pages). The old "the swapper is control-store microcode" claim is a
  **POISONED PRIOR — deleted**; ND-500 code is ordinary executable code in an executable segment,
  microcode is only what "> Loading Control Store" puts in the CPU's control storage.
- **SINTRAN names the layout in the two page tables it DMAs [BYTES].** RESIWR page `0x6E800` =
  PROGRAM table (`00DF 00E0 ...`, `0xDF << 11` = `0x06F800`, 19 pages); `0x6E000` = DATA table
  (`0049 004A ...` = `0x00024800`, 107 pages); `0x6F000` = an undecoded descriptor (`02 C0` at +3).
- **The swapper's LINK SEGMENT is 1 [CARVE, decisive].** `swapper/swapper-k01-pseg.asm` disassembles
  at base `0x08000000` and the code's own operands are segment-1 addresses. Entry
  `init $1000441124,$44,$17504` = **`0x08024254`** = the run-time stack bottom per
  `swapper-k01-deep-analysis.md` section 5.1 (DSEG `0x24254..0x26197`, 8004 bytes), and
  `call $1000100645` = **`0x080081A5`**. Both matched live traps EXACTLY (write `0x08024255` at
  program address `0o21`; instruction fetch `0x080081A5`). Code and data therefore share logical
  segment 1 and are separated by the I/D split: program capability -> PSEG, data capability -> DSEG.
- **TOP BLOCKER: the swapper stops at its RIOM intake with zero descriptors [V]; the "DSEG is never
  loaded" explanation is SUSPECTED, NOT VERIFIED.** With the correct segment-1 mapping
  the swapper runs to `PC=0x080082EE` and faults writing `VA 0x00000002`. The carve identifies that
  instruction as its DMA intake — `1000101356: h riom $1000440264,$1000440274,$1000440074+` =
  `0x240B4`/`0x240BC`/`0x2408C`, the RIOM triple documented in `swapper-k01-deep-analysis.md`. It
  writes to ~0 because those descriptor cells read ZERO. A dense-region scan of the whole MPM window
  shows data at `0x000000-0x0007FF` and `0x06F800-0x078FFF` (the PSEG) and **nothing at `0x24800`**,
  although the DATA page table reserves 107 pages there (`0x35800` = 219,136 bytes vs
  `swapper/SWAPPER-K01.DSEG` = 218,117 bytes) and only ONE 256-byte `14B` RESIWR ever touched it.
  **The DSEG IS loaded — a "DSEG never loaded" claim was DISPROVEN and is deleted [V].** A
  content-signature probe (density is useless here: a mostly-zero 218 KB segment never reaches the
  25%-non-zero bar) finds `DSEG+0x2408C @phys 0x04888C` = `00 00 00 08 00 00 00 0B 00 00 00 08` and
  `DSEG+0x26198 @phys 0x04A998` = `08 00 83 D8 08 00 83 F7 08 00 84 74`, byte-identical to
  `swapper/SWAPPER-K01.DSEG`; a window-wide fn-table sweep hits once, implying DSEG base `0x024800` —
  exactly what the DATA page table said. **Placement and mapping are correct for BOTH segments.**
  **Actual cause: the RIOM descriptor cells are RUNTIME variables [V]** — `+0x240B4`/`+0x240BC` are
  zero in the DSEG file itself, filled by the swapper from its SWMSG before RIOM. So the swapper
  reached its intake without a valid message; **the open thread is the MESSAGE path, not the loader.**
  Per `5SWRT` (`RP-P2-N500.NPL:12-58`) SINTRAN computes `A:=SWMSG+"SWPINFO"=:D:=5MBBANK; AD=:DSWMSG`
  (physical address of `SWPINFO` in `SWMSG`) — the pointer the swapper's RIOM needs. NEXT: find what
  writes DSEG `0x240B4`, and whether SINTRAN ever delivers that pointer to us.
- **OPEN [important]: SINTRAN's 21B image sends `P = 0x00000004` — offset only, NO segment bits.**
  Neither halfword order yields `0x08000004`, so the segment number reaches the CPU by some path we
  do not model. The emulator currently takes it from the carve (segment 1).
- **OPEN: who builds the PCB/PST, and when.** A scan of all 8 MB of the MPM window for a PSTE naming
  either page table (`(0xDD << 2)|mode`, `(0xDC << 2)|mode`) found **0 candidates**, so SINTRAN does
  not build them there during PLACE-DOMAIN. The 21B block carries `PS` (`reg[18]`) but **no `PSTP`**.
  Candidates unresolved: the swapper itself, the microcode at process start (context block /
  `LCNTXT`), or CPU-internal state. This is the headline question for the ND-5000/microcode track.
- **OPEN: our trap report to SINTRAN carries wrong fields.** For a fault the CPU records as an
  INSTRUCTION fetch at `0x080081A5`, SINTRAN printed `DATA segment READ access / Logical address
  1 100645B`; a segment-1 data write printed `Logical address 0 0B`.
- Emulator-side defects found and fixed en route (RetroCore, uncommitted): PTE bit 0 is PROTECTION
  (`PG_W`=0/`PG_R`=1) with validity = `PFN != 0` — `MapExistingPhysicalRegion` had written `|0x1` on
  every PTE, marking all pages read-only; and mailbox `17B` = `3DEPR` was unhandled, which had made
  SINTRAN re-send the bring-up cycle forever.

Evidence grade: placement + page tables + link segment = **BYTES/CARVE**; the `P`-segment provenance
and PCB/PST provenance = **OPEN**.

---

## 0. Caller-side carve + swapper deep analysis (added 2026-07-15)

Two folders in this subsystem now hold the ND-100 **caller** side and the ND-500 swapper,
complementing the SINTRAN **worker** carve under
[`tools/sintran-segment-carver/versions/L-VSX-500/re/`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/):

- [`nd-500-mon/`](nd-500-mon/README.md) — the ND-500/5000 MONITOR J04 (`MON-DEBUG:PROG`) caller
  analysis: the single `MON 60` gateway at `146256B`, the 123-thunk table, `mon60-callers/`
  (INDEX + SUBFUNCTION-TABLE + **101 per-subfunction folders**), the RetroCore control-store /
  TAG-OUT-DMA crash handoff, and the bring-up / bus-interface feedback. Front door =
  `MON 60`/N500M -> **FPT2ENTRY ("ENTER ND-500 SYSTEM MONITOR")** -> 5MPM message.
- [`swapper/`](swapper/README.md) — refreshed swapper analysis; start at
  [`swapper/swapper-k01-deep-analysis.md`](swapper/swapper-k01-deep-analysis.md). The swapper is an
  ND-500-side paging/swap worker DOMAIN and a **CLIENT** of SINTRAN (RIOM DMA intake, 29-way
  private dispatch, `MON 377B` = segment-31 monitor call 255 = N5SWAP trapped **outward**).
  The three older swapper docs are retired to [`old/`](old/README.md).

Evidence grade: caller carve = BYTES (resolved from the disassembly); descriptor/purpose naming
cross-checked against the worker source `5P-P2-MON60.NPL` (NPL grade). See each folder's README.

---

## 1. Evidence grades used here

| Grade | Means |
|---|---|
| **BYTES** | Read out of a carved `.bin` by me. Ground truth. |
| **SYMBOL** | Read out of a real symbol-table artifact. Strong, but a value, not a layout. |
| **NPL** | From NPL source. **NPL is a DIFFERENT REVISION than the carved bytes** — logic only, never authority. |
| **MANUAL** | From an ND manual. Weak; often idealised. |
| **INFERRED** | Reasoned. Not evidence. |
| **REPORTED** | A byte-claim from another session/agent that **I have not re-checked**. Treat as a strong lead, NOT as fact. Promote to BYTES only after reading the bytes yourself. |
| **FABRICATED** | Made up by a previous pass. Poison. Delete on sight. |

**Rule: NPL never promotes anything to VERIFIED.** A claim is VERIFIED only when someone read the bytes.

---

## 2. THE HEADLINE — what is and is not known

### 2.1 What is solid

**The 5xx handler BODIES are byte-verified and symbol-pinned** (L07):

| MON | Handler | Address | Folder |
|---|---|---|---|
| 500B | `STAPR` (=`SWITP`) | `140356B` | [500B-StartProcess](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/500B-StartProcess/) |
| 501B | `NSTOP` | `140511B` | [501B-StopProcess](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/501B-StopProcess/) |
| 503B | `NINST` / `XNINS` | `141272B` / `141277B` | [503B-InputString](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/503B-InputString/) |
| 504B | `OSTRS` | `141205B` | [504B-OutputString](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/504B-OutputString/) |
| 505B | `GERRC` | `141633B` | [505B-GetTrapReason](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/505B-GetTrapReason/) |
| 506B | `5SIBM` | `141716B` | (no folder) |
| 510B | `SWMC` | `142153B` | [510B-CallSwapper](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/510B-CallSwapper/) |
| 511B | `DVIO` | `141027B` | [511B-DVIO](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/511B-DVIO/) |
| 512B | `A5XMS` | `142253B` | [512B-XMSGCallA](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/512B-XMSGCallA/) |
| 513B | `B5XMS` | `142253B` — **same body as 512B** | [513B-XMSGCallB](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/513B-XMSGCallB/) |
| 514B | `M5TMO` | `140563B` (in `026-S3IMPIT`, load `32000B`) | [514B-ND500TimeOut](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/514B-ND500TimeOut/) |
| 515B | `5MTRA` | `143445B` | [515B-MultipleDataTransfer](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/515B-MultipleDataTransfer/) |

Other symbol-verified constants: `MOCAL=1`, `TRAPC=2`, `5FMOC=3`; MICFU `3STAR=23B`, `3MONC=24B`,
`3TRAC=25B`, `3WMON=26B`, `3MONO=34B`, `33MON=46B`; STOPREASON = bits 10-14 of `RSTA5`, mask `037000B`.

### 2.2 The gaps that block the emulator

**GAP 0 — MON 60B (`N500M`), the ND-100 -> ND-500 direction. LARGELY CLOSED 2026-07-15.** Essentially
every command from `ND-500-MON` reaches the ND-500 through MON 60B and the 3022 bus interface. The
worker `MCTAB[60B] -> N500M=030416B` is byte-verified; the worker body IS now disassembled (in
`050-S3I5PIT`, 5PIT context) and **all 47 `5IFUNC` subfunction folders are carved**, and the
downstream ND-500 SYSTEM MONITOR (`030-S3SM5`) it hands off to via `5NOPAR`/`FPT2ENTRY` is carved end
to end (FUNCS table + 3022 IOX driver + control-store gate + 5MPM + level-12 return). The prior "lives
outside the carve" conclusion was the wrong-overlay signature and is withdrawn. **See section 3a for
the full resolution and the carve deliverables.** Only remaining sub-item: the bank-2 5IFUNC table for
a per-handler `.ASM`.

**GAP 1 — CLOSED 2026-07-15: the level-12 GOSW dispatch is BYTE-LOCATED.** The compiled `GOSW`
lives in **BOTH `017-S3SMPIT` and `026-S3IMPIT` (identical bytes, load `32000B`)**:

- **Pointer table at `137625B`-`137650B`** (20 slots, 500B-523B; slot 0 file offset `0x1172A`).
- **Range constants at `137623B`/`137624B` = `000500`/`000523`** (L12MIN/L12MAX, read P-relative by
  the range check at `137532B`-`137537B` and the `SUB 60` at `137543B`).
- **Dispatcher = `N5MPA` (SYMBOL-2-LIST `N5MPA=137525`)**: saves MCNO to `137665B`, subtracts 500B,
  `RADD SA DP` computed-goto into a 20-entry `JMP I` ladder at `137545B`-`137570B`, each slot
  indirecting through the pointer table. All offsets reproduced by raw byte reads in both segments.

**Byte-proven slot map** (grade BYTES; names SYMBOL from SYMBOL-2-LIST, which cross-validates —
every named address lands exactly on a byte-verified handler entry):

| MON | Slot value | Symbol | Note |
|---|---|---|---|
| 500B | `140356` | STAPR/SWITP | |
| 501B | `140511` | NSTOP | |
| 502B | `140356` | SWITP | same body as 500B (`STAPR=SWITP`) |
| 503B | `141272` | NINST | (`XNINS=141277` is the inner entry) |
| 504B | `141027` | **NOUTS** | **NPL-only "504B=OSTRS 141205" claim DISPROVEN — bytes say NOUTS, which SHARES its entry with DVIO (both `=141027` in SYMBOL-2-LIST); `OSTRS=141205` is an inner routine** |
| 505B | `141633` | GERRC | |
| 506B | `141716` | 5SIBM | |
| 507B | `142033` | **SPRIO** | previously unknown handler |
| 510B | `142153` | SWMC | |
| 511B | `141027` | DVIO/NOUTS | shared body with 504B |
| 512B/513B | `142253` | A5XMS/B5XMS | |
| 514B | `140563` | M5TMO | |
| 515B | `143445` | 5MTRA | |
| 516B-523B | `137651`-`137663` | M516-M523 | six 2-word stubs, ALL `JMP I` via `[137726B]=137167B` = **NORMM** (common unimplemented/error handler; same target as the range-check failure via `[137620B]`) |

Special case: the dispatcher prologue compares MCNO against `347B` (`137621B`) and routes it via
`[137622B]=050211B` = **`5SERV`** (SYMBOL-1-LIST). The prologue also calls through `[137610B]=023030B`
= **`MONIC` (MONICO)** — the return path is wired right here.

**The four "never located" routines are now SYMBOL-pinned in the same overlay** (bodies still to
be disassembled): `5STDR(IV)=135010`, `CHN5S(TATUS)=135205`, `DECOM(ESS)=135361`, `MCHAN(DEL)=137206`;
plus `NORMM=137167`, `N5MPA=137525`, `N5FUD=137727`, `MONIC=023030`.

### 2.3 Corrected 2026-07-15 — the message fields and status codes are NOT unknown

Previous docs said the 5MPM field offsets and status-code values were "not found in symbol files".
**That was wrong** — they are present in
[`swapper\N500-SYMBOLS.SYMB`](swapper/N500-SYMBOLS.SYMB). Read directly from that artifact:

**Message-block field offsets (grade: SYMBOL for the value; INFERRED that it is a message offset):**

| Symbol | Value (octal) | Cross-check |
|---|---|---|
| `N5STA` | `000002` | |
| `SENDE` | `000003` | |
| `X5CPU` | `000004` | |
| `X5ACT` | `000005` | |
| `MICFU` | `000006` | |
| `STOPR` | `000011` | **matches the independently-known `STOPR` @ `000011B`** |
| `NUMPA` | `000012` | |
| `MCNO` | `000013` | |
| `MSWMC` | `000014` | |
| `TRAPN` | `000016` | **matches the independently-known `TRAPN` @ `000016B`** |
| `SMCNO` | `000037` | |
| `FUNCV` | `000013` | see collision note |
| `KFLIP` | `000011` | see collision note |

**Status-code values (grade: SYMBOL) — the manual hint is now CONFIRMED:**

| Symbol (5-char truncated) | Value | Manual hint said |
|---|---|---|
| `MSGN5` (= `MSGN500`) | `000001` | 1 = to-ND500 |
| `WAITI` (= `WAITING`) | `000002` | 2 = in-process |
| `ANSWE` (= `ANSWER`) | `000003` | 3 = answer |
| `5ERAN` (= `5ERANSWER`) | `000004` | 4 = error |

All four line up with the manual's `0=free, 1=to-ND500, 2=in-process, 3=answer, 4=error` ordering.
Two independent sources agreeing on a 4-value sequence is strong. `0 = free` remains INFERRED
(no symbol for it).

**Two honest caveats — do not skip these:**

1. **`N500-SYMBOLS.SYMB` is a FLAT, alphabetically-sorted, 5-CHAR-TRUNCATED global symbol table.
   It is NOT a struct layout.** It proves *a symbol has a value*. It does NOT prove that value is an
   offset into the 5MPM message block. That step is INFERRED from the NPL usage pattern
   `AAX <sym>; LDATX` (add to X, load indexed), which is a strong but indirect argument.
2. **Value collisions are expected and are NOT contradictions:** `FUNCV=13` = `MCNO=13`,
   `KFLIP=11` = `STOPR=11`, `N5STA=2` = `WAITI=2`. A flat table holding both field offsets AND
   status constants will collide. Do not "resolve" these — they are different namespaces.
   `WAITI=2` is a status VALUE; `N5STA=2` is a field OFFSET.

**Why this table is trustworthy at all** (gotcha 6 — validate before use): `STOPR=000011` and
`TRAPN=000016` both match values known independently. Two known slots match => the table is the
right one.

**Still absent from every source:** the *name* expansions are truncated, so `WAITI` -> `WAITING` is
INFERRED from context; and `0 = free` has no symbol.

### 2.4 POISONED PRIORS — active, must be deleted

1. **The "TAG code" protocol is FABRICATED.** Codes 8/9/16 = MonitorCall / PageFault /
   OperationComplete. It exists **neither in ND hardware nor in SINTRAN**. It lives in:
   - `..\Emulator\ND500-QUICK-REFERENCE.md`
   - `..\Emulator\DETAILED-TAG-MECHANISM-EXPLANATION.md`
   - ~~RetroCore **`NDBusND500IF.cs`** (shipping code!)~~ **PURGED 2026-07-16**: the fabricated
     enums/tests were deleted from `NDBusND500IF.cs` and the test suite, and replaced with the
     carve-verified TAG-IN/TAG-OUT model (Phase 1 of ND500-BUS-INTERFACE-DESIGN.md, live-validated).
   Recorded in [`ND500-L-RELEASE-RE-TASK-HANDOFF.md`](ND500-L-RELEASE-RE-TASK-HANDOFF.md).
   Notably, none of the four real ND-500 MON docs mention TAG codes at all.
   The two Emulator/ docs above are still poisoned - do not cite them.
2. **`..\Emulator\ND500-MESSAGE-STRUCTURE-VERIFIED.md` is MISNAMED.** Its filename says VERIFIED; its
   content explicitly disclaims offsets, struct size, layout, function codes and status codes, and
   contains a section headed *"What I MADE UP (Apologies!)"* admitting the GRAPHICS/DATABASE/COMPUTE
   values 10/20/30 have **no source**. Its "VERIFIED" column means only *"this field name appears in
   NPL"* — name-existence, not layout. The file is internally honest; **only the filename lies.**
   Do not cite it for offsets. Cite `swapper\N500-SYMBOLS.SYMB` (section 2.3) instead.
3. **`ND500-MON-ACTIVATION-AND-MAPPING.md`'s offsets are second-hand** — it cites another doc, not a
   primary source. Same numbers as 2.3, but get them from the symbol file.
4. **Naming disagreement, unresolved:** the routing map calls it `MCHANDEL`; the activation doc calls
   it `MCHANDLE` a.k.a. `5MONICO` (the a.k.a. has **no citation**). Do not treat `5MONICO` as a known alias.

---

## 3. The communication model (current best understanding)

**Grade: NPL-derived. Not byte-proven. This is the thing Phase 1 exists to verify.**

```
ND-500 executes MON
  -> microcode stops the CPU, sets STOPR, writes MCNO + params into the 5MPM message,
     sets status ANSWER (=3, SYMBOL), clears 5ILOCK
  -> hardware raises ND-100 level-12 interrupt
  -> 5STDRIV                (NPL MP-P2-N500.NPL:659)      [NOT located in bytes]
  -> power-fail / comm-error checks
  -> scan exec queue from MAILINK
  -> CHN5STATUS             (NPL MP:730-759)              [NOT located in bytes]
  -> on ANSWER: DECOMESS    (NPL MP:803-818)              [NOT located in bytes]
  -> on STOPR = MOCALL(=1) / 5FMOCALL(=3): MCHANDEL (NPL MP:1251-1406) [NOT located in bytes]
  -> MCHANDEL reads MCNO (offset 013, SYMBOL), saves to SMCNO (offset 037, SYMBOL)
  -> IF A >= L12MIN(500B) AND A <= L12MAX(523B):
         5CMNO-L12MIN GOSW STAPROC, NSTOPROC, SWITPROC, NINSTR, NOUTSTR, GERRC,
                           5SIBMO, SPRIO, SWMC, DVIO, A5XMSG, B5XMSG, M5TMOUT,
                           5MTRANS, M516..M523          (NPL MP:1385-1390)  [THE KEY GAP]
     ELSE -> NORMMC (MP:1277) -> 5RRTWT -> level-1 / background monitor
  -> return path MONICO (NPL CC-P2-N500.NPL:363-372):
         write FUNCV, KFLIP, MICFU=3MONCO(=24B, SYMBOL), status MSGN500(=1, SYMBOL),
         PSTAT=5ACTIVE, then XACTRDY -> LCON5=5
```

Index rule (NPL): **the GOSW index is `MCNO - 500B` (octal).**
Constants (NPL MP:1269-1273): `L12MIN=500`, `L12MAX=523`, `CERN=376`, `N5SWAP=377`.

**MON 60B (`N500M`) is NOT part of this path — it is the OTHER DIRECTION.** See section 3a.

---

## 3a. MON 60B (`N500M`) — THE OTHER DIRECTION. TOP PRIORITY.

**Why it matters:** section 3 is the **ND-500 -> ND-100** path (ND-500 executes MON, ND-100 services
it). **MON 60B is the reverse: ND-100 -> ND-500.** The `ND-500-MONITOR` program (`:PROG`, running on
the ND-100) issues **MON 60B** to make SINTRAN drive the ND-500 across the **3022 bus interface** —
start, stop, load, examine, deposit, trap handling, register access.

**Essentially every command from `ND-500-MON` reaches the ND-500 through MON 60B.** Without it, the
emulator can service ND-500-originated calls but cannot *control* the ND-500 at all. It is the
missing half of the interface, and it is the concrete form of open question **Q3** ("the user side of
the monitor-to-driver interface is not documented").

### What is known

| Fact | Grade |
|---|---|
| `MCTAB[60B] = 005700B -> N500M = 030416B` | **BYTES** — a real, populated worker slot |
| `GOTAB[60B] = 000000` (level-14 fall-through -> `MFELL` -> `CALLP` -> `MCTAB`) | **BYTES** — normal, expected for a non-fast-path call |
| ~67 subfunctions | **MANUAL only** (Loader/Monitor manual + yaml). No byte evidence |
| "servicing lives outside this carve, in the `ND-500-MONITOR` / `MP-P2-N500` back-end" | **INFERRED — and probably WRONG. See below.** |

### The caller side — `ND-500-MON:PROG` (REPORTED 2026-07-15, external decode)

From a parallel disassembly of the `ND-500-MON` program itself. **Grade: REPORTED — not re-checked
against the bytes by this session. Strong lead; do not cite as VERIFIED until confirmed.**
All addresses below are in **`ND-500-MON:PROG`'s own address space**, NOT SINTRAN's.

| Finding | Consequence |
|---|---|
| **Exactly ONE `MON 60` call site** in the whole program: address `146256` (line 52478) | All ~67 subfunctions funnel through **one centralised `N500M` wrapper**. The emulator has a single choke point to implement, not 67 |
| **ZERO `IOXT` instructions in the program** | **ANSWERS Q6.** `ND-500-MON:PROG` never touches the 3022 bus registers directly. **All register access is confined to resident SINTRAN** — exactly as the spec predicted. So the entire ND-100 -> ND-500 control path runs through `MON 60B -> N500M` and nowhere else |
| Wrapper contract: `A` = param-list pointer (`AAA -173`); `JMP 2` = skip return (**success**); `JPL I 23` = direct return (**error**) | Matches the documented MON 60B contract exactly |
| Retry loop: `JMP -21` back to `146254` | The wrapper retries the MON |
| Constant pool at the wrapper's P-relative operands: `146304 = 002032` = **`ECSLOAD` = 2032B** = "CONTROL STORE MUST BE LOADED" | **Exact match to the documented constant** — a strong independent cross-check that this really is the N500M wrapper |
| `146305 = 004017` = `0x080F` = 2063 decimal | Second retry constant; meaning not yet established |

**Why this matters for section 6:** the two directions meet here. `MON 60B` is the *only* ND-100 ->
ND-500 door, and SINTRAN owns the bus registers on both sides. Byte-closing `N500M` therefore closes
the whole control direction.

**To promote from REPORTED to BYTES:** re-derive the `MON 60` site and the constant pool from the
`ND-500-MON:PROG` binary independently, and confirm `002032` = `ECSLOAD` against the L07 symbol table.

### MEMORY-CONFIGURATION — live shared-memory map (OBSERVED 2026-07-15, J04)

`MEMORY-CONFIGURATION` runs safely **without** the control store loaded (pure ND-100-side query).
Live output on Ronny's machine, and the arithmetic closes on every row:

```
   PART       WIDTH        N100   N500P  N500D
     0B      0B-  7777B      Y      Y      Y     (part 0 = pages 0..7777B, all three ports)

                             PAGE          WORD(ND-100)   BYTE(ND-500)
                        ND-100  ND-500
ND-500 address zero:    004100  000000    00010200000    00000000000
ND-500 register block:  004212  000112    00010424000    00000450000
Physical segment table: 004252  000152    00010524000    00000650000
WIP/PGU table:          004211  000111    00010422000    00000444000
```

**Verified facts (arithmetic confirmed from the table):**
- **Base:** ND-500 physical address 0 = **ND-100 page `4100B`** = ND-100 word `010200000B`. This is
  exactly the `DEFINE-MEMORY-CONFIGURATION` parameter ("ND-100 page number for ND-500 phys addr 0").
- **Mapping rule:** **ND-100 page = `4100B` + ND-500 physical page.** (reg block `112B`->`4212B`;
  seg table `152B`->`4252B`; WIP/PGU `111B`->`4211B`.)
- **Unit convention** (matches the memory model): ND-100 addresses are **word** addresses; ND-500
  addresses are **byte** addresses; 1 page = 1024 words = 2048 bytes (`2000B` words = `4000B` bytes).
- **The ND-500 register block is MEMORY-MAPPED into the ND-100 at page `4212B` (word `010424000B`),
  NOT reached by IOX.** This is the mechanism behind the zero-`IOXT` finding: SINTRAN accesses ND-500
  registers through this shared-memory window. **For the emulator: ND-500 register access = ND-100
  word `010424000B`.**
- Physical segment table @ ND-100 word `010524000B` (page `4252B`, ND-500 page `152B`).
- WIP/PGU table @ ND-100 word `010422000B` (page `4211B`, ND-500 page `111B`).

**Grade:** OBSERVED (live J04). The page-base relationship and unit convention are arithmetically
verified. These are J04 values on THIS install; confirm before applying to L07 — the base page
`4100B` is an install/config parameter and may differ.

### LIVE-MACHINE HAZARD — control store must be loaded first (OBSERVED 2026-07-15)

Running `ND-500-MON` (Version **J04**, 88.6.16) on Ronny's machine:
- `LOAD-SWAPPER` -> `> Loading Control Store` -> `Error when loading Control Store` -> `NO SUCH FILE NAME`.
- `VERSION` **looped** on the same control-store error and **required a reboot**.

**Interpretation (OBSERVED behaviour + REPORTED `ECSLOAD` constant):** with the ND-500 control store
(microcode / WCS) NOT loaded, `ND-500-MON` funnels almost every command through a control-store load
attempt, which fails because the microcode image file is absent, and some commands (`VERSION`) loop
until reboot. This is the live counterpart of `ECSLOAD=2032B` "CONTROL STORE MUST BE LOADED" and of
open **Q7** (microcode image NOT FOUND). **No microcode/control-store image exists in the NDInsight
repo** (only the manuals) — so this install genuinely lacks it.

**RULE for the live machine:** until the control store is confirmed loaded, do **NOT** run ND-500-MON
commands — even "read-only" ones like `VERSION` are unsafe (they hang the machine). First resolve
the microcode image. Unknown, do not guess: the exact default microcode filename this J04 monitor
expects, and whether this is real hardware or the emulator.

### CONTROL STORE / microcode — why the emulator hangs, and the way past it (2026-07-15)

**Context:** Ronny's setup is the **RetroCore emulator** with enough of the ND-100 bus interface
working to lure the real `ND-500-MON-J:PROG` (J04) into starting. There is **no ND-500 CPU / no
microcode** behind it.

**Verified from `Reference-Manuals\500\ND-05.012.01 ND-500 Micro Program Guide.md` section 16.4:**
- The ND-500 uses a **WRITABLE control store (WCS)** — microcode is loaded, not in PROM. An ND-500
  with nothing loaded has no working CPU.
- Standard system microcode file = **`(SYSTEM)CONTROL-STORE:DATA`** (line 2852).
- Normal ND-500 bring-up (lines 2861-2872): `MASTER-CLEAR` -> `MICRO-START 0` ->
  `LOAD-SWAPPER SWAPPER` -> `START-SWAPPER` -> `GIVE <pages>`. `LOAD-CONTROL-STORE` is NOT in this
  sequence — normally the control store is already loaded at boot; `LOAD-CONTROL-STORE
  CONTROL-STORE,16010,200` is only for *user* microcode.
- Swapper is loaded as `LOAD-SWAPPER SWAPPER` — a domain/file named **`SWAPPER`**.

**Verified live (LIST-FILES on `PACK-ONE:SYSTEM`):** ND-500 files present are ONLY
`ND-500-MON-J:PROG`, `SWAPPER-K:PSEG`, `SWAPPER-K:DSEG`, `N500-SYMBOLS:SYMB`. **There is NO
`CONTROL-STORE:DATA` and no microcode image.** => Q7 confirmed on the live install. Also: Ronny's
earlier `LOAD-SWAPPER swapper-k01` used the wrong name — the file is `SWAPPER-K` (`:PSEG`/`:DSEG`).

**Why it hangs:** with WCS empty, the monitor's `ECSLOAD` "CONTROL STORE MUST BE LOADED" gate fires;
`LOAD-SWAPPER` (and even `VERSION`) implicitly attempt a control-store load, which fails because
`CONTROL-STORE:DATA` is absent — and `VERSION` loops until reboot.

**What `CONTROL-STORE:DATA` actually is + where it comes from (VERIFIED from manual + package doc):**
- It is the **assembled ND-500 microcode image**: an 8-Kiloword microprogram of **144-bit words**
  (Micro Program Guide line 1596). `(SYSTEM)CONTROL-STORE:DATA` is that image; `LOAD-CONTROL-STORE`
  writes it into the WCS, `LOOK-AT-CONTROL-STORE` saves edits back to it (line 2852).
- Produced by ND's **micro-code assembler** `@N500-8K-ASSEM` (section 14.8) from micro-source `:SYMB`
  files + mnemonic tables (`N500-MNE-SYMBOLS:SYMB`, `N500-MNE-VALUES:DATA`); output is a `:DATA`
  object "input to control store" (lines 1557, 1562), default `N500-MICRO-OBJEC:DATA`. Normally
  shipped pre-built by ND, not site-assembled.
- **Shipped on a SEPARATE microcode diskette, NOT in the ND-211305 L package**
  (`ND500-L-PACKAGE-CONTENTS.md`: "No MIC-5xxx microcode file... ND-5000 microcode as a separate
  diskette"). This is exactly why it is absent = Q7. Getting the genuine image is a separate artifact
  hunt, only needed if you ever want to actually EXECUTE ND-500 code.
- Corroborating: on **real** L hardware `@ND-500` prints `No ND-500(0) CPU found` and stops early
  (`ND500-L-PACKAGE-CONTENTS.md` line 69). The emulator answers the bus enough to march past that to
  "Loading Control Store" — so its further progress is emulator responsiveness, not a new fault.

**WHERE the classic ND-500 CONTROL-STORE:DATA comes from — exact ND product numbers (VERIFIED 2026-07-16):**
The microcode is a SEPARATE per-CPU-model floppy diskette product, not part of SINTRAN or the
ND-500/5000 System Package (ND-211305). Source: L-release info section 1.2 "MICROPROGRAM VERSIONS
FOR ND-500/5000" (`SINTRAN\Release-Documentation\ND-860230-6-EN Sintran III - Release Information - L-Version.md`
lines 353-368):

| ND prod.no. | System type    | Microprogram version | Class       |
|-------------|----------------|----------------------|-------------|
| ND-210786 D | ND-550/560/570 | 15211                | classic 500 |
| ND-210787 D | ND-530         | 15311                | classic 500 |
| ND-210701 F | ND-580         | 15111                | classic 500 |
| ND-211272 C | ND-5200        | 11529                | ND-5000     |
| ND-211273 C | ND-5400        | 11629                | ND-5000     |
| ND-211274 C | ND-5500        | 11729                | ND-5000     |
| ND-211275 C | ND-5700        | 11829                | ND-5000     |
| ND-211276 C | ND-5800        | 11929                | ND-5000     |

("or later versions: ...30, etc." - the M/N release docs list the same products at newer revisions,
e.g. 210701 H = version 15113.)

Microprogram version-number families (first-generation table from
`Reference-Manuals\500\ND-05.012.01 ND-500 Micro Program Guide.md` section 16, lines 2271-2276):

| Version family | Meaning                                      | Generation        |
|----------------|----------------------------------------------|-------------------|
| 103xx          | ND-500 CX micro program                      | ND-500/1 classic  |
| 104xx          | ND-500 AX option                             | ND-500/1 classic  |
| 105xx          | ND-500 standard micro program                | ND-500/1 classic  |
| 106xx          | ND-500 CX, AX option                         | ND-500/1 classic  |
| 15xxx          | ND-500/2 (ND-530/550/560/570/580)            | ND-500/2 classic  |
| 11xxx          | ND-5200..5800                                | ND-5000           |

So e.g. version 10509 = first-gen ND-500 standard microcode rev 09; 10609 = first-gen ND-500 CX
with AX option rev 09 - both are CLASSIC ND-500 (144-bit), NOT ND-5000. The AX option adds the
array-processing instruction set (the guide's section 16 text: some user-instruction codes "are
used in the micro program version containing the ND-500 Area Processing Instruction set" - OCR;
the APF library docs describe it as "a special microprogram ... extension of the standard
microprogram"). The xx suffix is the revision; user-microcode space differs per family
(105xx/103xx: 13000B-17777B free; 104xx/106xx: only 16000B-17777B, rest used by AX).

- On-floppy filename, classic 500: the System Supervisor manual
  (`Operations\SINTRAN\ND-30.003.007 EN SINTRAN III System Supervisor.md` lines 3546-3642) shows
  floppy ND-210701 ("ND-500/2 CX MULTI CPU MICRO-PROGRAM") contains the file `CONT-STORE-151xx`
  (xx = version/revision), installed with `@COPY-FILE CONTROL-STORE:DATA,CONT-STORE-151:DATA`.
  So classic-500 microcode files on disk are named `CONT-STORE-15xxx:DATA`.
- On-floppy filename, ND-5000: `MIC-5xxx-2-500:DATA`, installed with
  `@COPY-FILE CONTROL-STORE:DATA (211:)MIC-5xxx-2-500:DATA` (K/L/M/N release docs; the M-version
  variant also shows `(21):CONT-STORE:DATA` for classic 500).
- Multi-CPU default filenames (K-release info section 17.7.13): from K onward the monitor picks the
  default per CPU: `CONTROL-1-STORE:DATA` / `CONTROL-2-STORE:DATA` on multi-CPU systems;
  `CONTROL-STORE:DATA` on single-CPU (unless `CONTROL-1-STORE:DATA` exists).
- Hunt targets for a genuine classic-500 image: a diskette image of ND-210786 / ND-210787 /
  ND-210701, OR a system-disk image from a classic-500 site containing `(SYSTEM)CONTROL-STORE:DATA`
  or `CONT-STORE-15xxx:DATA`.
- **HUNT STATUS 2026-07-16: a source is FOUND.** Bo Goran (friend of Ronny) has a floppy carrying
  microcode versions 10509 (ND-500/1 standard) and 10609 (ND-500/1 CX+AX option); a digital copy is
  awaited. When it arrives, sanity-check: 144-bit = 18-byte microwords, full 8KW image =
  8192 x 18 = 147456 bytes per version (file/floppy headers aside). Classic word size 144 bits = 18 bytes/word (SINTRAN Ref Manual
  LOAD-CONTROL-STORE note: "Every micro-program word (144 bits, 18 bytes)"), 8KW control store,
  default LOAD size 20000B (octal) = 8192 words -> a full image is 8192 x 18 = 147456 bytes
  (vs the ND-5800 `CONTROL-STORE.DATA` we already have: 128-bit x 16384 = a different format;
  it will NOT run a classic 500).

**CONTROL-STORE GATE SOLVED 2026-07-15 (byte-verified) — the exact emulator fix:**
`tools\...\re\ND500-SYSTEM-MONITOR\ND500-CONTROL-STORE-GATE.md`. The driver reads interface STATUS
(`RSTA5`, IOX `dev+2`) and tests **bit 9 `5CLOST` (`001000`) = "micro clock stopped"**; if set ->
control store not loaded -> `ECSLOAD` (`2032B`). **Emulator fix: return STATUS with bit 9 (`5CLOST`)
CLEAR** (plus bit 5 `5ILOCK` clear for idle-ready; error bits clear) - i.e. STATUS `0` for a ready,
idle, control-store-loaded ND-500. That alone clears the gate and lets `VERSION`/monitor proceed
without a real microcode image. (Unblocks command/message traffic, not real ND-500 execution.)

**The way past it (for the interface-RE goal — do NOT emulate the microcode engine):**
**Satisfy the "control store loaded" gate** in the emulated bus interface so the monitor proceeds to
the real MON-call / 5MPM message traffic. **Strong hypothesis (Ronny, 2026-07-15, to confirm by
capture): ND-500-MON reads the ND-100 bus interface to decide whether the control store needs
loading; the emulator must answer "already loaded / ready."** There is a precedent chain of interface
status reads: (1) "CPU present?" — the emulator already answers yes (real HW prints
`No ND-500(0) CPU found` here); (2) "control store loaded / running?" — currently answered no.

**Capture, do NOT guess (it is the emulator — one run is authoritative):**
1. **Instrument the emulator's ND-500 bus interface to log every read (address + returned value +
   caller PC).** Issue `VERSION` or `LOAD-SWAPPER SWAPPER` and find the **last interface read before
   `> Loading Control Store` prints.** That read IS the gate. Expected location: the memory-mapped
   register block at ND-100 page `4212B` (word `010424000B`), or a dedicated interface/status word;
   candidate HW regs `CSCNT`/`CSWA` (Micro Program Guide register list, `A,XD,CSCNT`).
2. Make the emulated interface return the **"loaded & ready" pattern** for that read.
3. **Confirm against the binary before trusting it:** in `ND-500-MON-J:PROG`, the branch that decides
   to load control store is the `ECSLOAD` path (decoded in the MON 60B wrapper). Verify its compare
   matches the register/value you captured — so the emulator returns the RIGHT status, not just any
   value that dodges the branch. The interface status word likely packs CPU-present + running/stopped
   + stop-reason + control-store-loaded together; a blind value could clear one bit and hang on
   another. `LOOK-AT-HARDWARE INTERFACE` reads this same status word.
4. Then `VERSION` / `START-MONCALL-LOG All` should work -> live capture of the ND-100<->ND-500
   traffic (the whole point).

Unknown / do not guess: whether the ND-5000 (SAMSON) control-store handling differs — needs
`ND-05.020`, which we do not have. The WCS is definitely an ND-500 feature per this manual, so this
is not "5000-only".

### MON 60B / N500M worker — RESOLVED 2026-07-15 via the L release-doc PIT layout

**CONFIRMED: N500M worker = `030416B` in `050-S3I5PIT` (the 5PIT overlay).** Three independent
sources agree:
1. **Bytes:** `MCTAB[60B] = 030416B = N500M` (044-S3IDPIT; anchors `5B`/`144B` match).
2. **Authoritative doc:** the L release doc `ND-860230-6-EN ... L-Version.md` section 8.2 "Page Index
   Table Layout" shows **PIT 5 (5PIT) maps `MON 60` at page 13** = virtual `26000B` (page 13 x
   `2000B`), spanning to page 20 = `40000B` ("ND-500 system monitor"). `N500M=030416B` is inside that
   `26000B-37777B` MON-60 region. Segment 050-S3I5PIT ("Image of 5PIT segment") loads at exactly
   `26000B` (release doc segment table, line 2539).
3. **Code:** `050-S3I5PIT@030416B` is a coherent subfunction dispatcher (range-check `177B`, MPY/ADD
   jump table).

**So the monitor runs MON 60 in the 5PIT (PIT 5) context, and `030416B` in that context IS N500M.**
The reason `N500M` is absent from `N500-SYMBOLS` (050's carver-assigned symbol file): that assignment
is "medium confidence" and **wrong** — the 5PIT MON-60 code is resident code named by
**SYMBOL-2-LIST** (which has `N500M=030416B`). The commoncode overlay's *data* block at `030416B` is a
different PIT context (same virtual address, different content — the normal overlay mechanism).

**Prior retraction (that `050-S3I5PIT` was NOT N500M) is itself withdrawn.** The lesson stands: a
carver `symbol_file` guess is not proof — cross-check against the release-doc PIT layout, which is the
authoritative overlay map. **Cleared to extract N500M's subfunctions from `050-S3I5PIT`.**

**Subfunction structure RESOLVED + ALL SUBFUNCTIONS CARVED 2026-07-15.** The dispatch table is
**`5IFUNC`** (128 entries), sourced from `SINTRAN\NPL-SOURCE\NPL\5P-P2-MON60.NPL` (the MON 60 worker's
own NPL). Full map + 3-way cross-verification: `tools\...\60B-N500M\60B-5IFUNC-dispatch-table.md`.
**All 47 subfunction folders are carved** (README + .pseudo.c + verbatim .npl each) under
`tools\...\re\mon-analysis\60B-N500M\` - every distinct `5IFUNC` handler body, the `5NOPAR` common
path, and the error handlers. Index: `60B-N500M\CARVE-PROGRESS.md`.

**Cross-analysis with the caller side done 2026-07-15.** The other session's `nd-500-mon:prog`
(caller) carve (101 folders, `D:\...\mon60-callers\`) was cross-checked against this worker carve:
`tools\...\60B-N500M\60B-CROSS-ANALYSIS-caller-vs-worker.md`. Both derive the `5IFUNC` map from the
same NPL and **agree exactly** (mutual validation: 117B/122B shared body, 024B/157B duplicate,
MSTOP/MSTCL STOP sequence). The worker carve **closes the caller's open item** (the >142B handler
identities); the caller carve **confirms the control-store gate** (gateway `146244` auto-loads the
control store on `ECSLOAD` error - the byte-level cause of the emulator's `VERSION` hang) and enriches
the `5NOPAR` codes with verbatim purposes. Both converge on the same next target: the ND-500 SYSTEM
MONITOR (`FPT2ENTRY`).

**Follow-up 2 (the ND-500 SYSTEM MONITOR carve) - DONE 2026-07-15. Follow-up 1 remains.**

**ND-500 SYSTEM MONITOR CARVED 2026-07-15 (byte-verified).** The `5NOPAR` hand-off target that builds
the 5MPM message and actually drives the ND-500 - the concrete "more than MON 60" code (SCOPE NOTE) and
the bridge to Phase 1 (5MPM handshake) and Phase 3 (bus interface / bring-up) - is now carved.
Deliverables under
`tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/`
([`README.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/README.md)):
- **Entry chain (byte-verified):** `FPT2ENTRY = FP2ENT = FPT2E = 040003B` (N500-SYMBOLS + SYMBOL-2-LIST),
  in segment **`030-S3SM5` ("ND-500 System Monitor", load base `40000B`)** - the same `40000B` the
  release-doc PIT layout maps at 5PIT page 20. The bytes at `040003B` are `125001 JMP I 1` - a
  **trampoline** to `MEM[040004] = 142231B` = `5FP2E` (the system-monitor entry body), consistent with
  the documented "enter page-table-2 (FPT2)" context switch.
- **FUNCS operation table:** `FUNCS = 142031B` (128 entries) - the server-side twin of the worker's
  `5IFUNC`: `5IFUNC[N]` marshals params, `FUNCS[N]` performs the ND-500 operation. Every entry lands on
  a named N500-SYMBOLS routine (`REGRE`, `PMWRI`, `CSLOA`, `RSTAT`, ...). Maps the whole MON 60B path
  end to end.
  [`FUNCS-dispatch-table.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/FUNCS-dispatch-table.md).
- **3022 IOX bus interface:** the `WADR`/`WRDAT`/`RDATL`/`REDAT`/`WRTAG`/`RSTAT` driver at
  `051023B`+ (via `IOXT`), register-offset map byte-validated both ways (driver bytes AND the hardware
  manual) - matches `ND500-BUS-INTERFACE-REFERENCE.md` section 3.2. Confirms Q6 from bytes (IOX is in
  resident SINTRAN, not the caller).
  [`ND500-3022-IOX-INTERFACE.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/ND500-3022-IOX-INTERFACE.md).
- **5MPM message + `ACT50` activation** and the **level-12 return path** (ISR chain
  `5STDR=135010 -> CHN5S=135205 -> DECOM=135361 -> MCHAN=137206` in the RESIDENT `026-S3IMPIT`,
  dispatch on the MICFU code) are also carved.
  [`ND500-5MPM-MESSAGE-AND-ACTIVATION.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/ND500-5MPM-MESSAGE-AND-ACTIVATION.md),
  [`ND500-LEVEL12-RETURN-PATH.ASM`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/ND500-LEVEL12-RETURN-PATH.ASM).

This clears the prior "cannot enumerate with confidence" (~53% opcode-0) scare: that was whole-segment
linear disassembly; carving from validated symbol entry points (`5FP2E` + the N500-SYMBOLS addresses)
gives coherent code. **What remains is mechanical body-listing of each `FUNCS` routine, not new
mechanism** - the emulator now has the FUNCS/5IFUNC dispatch, the IOX register map, the control-store
gate fix, the 5MPM message + activation, and the level-12 return path.

**Follow-up 1 (still open):** **locate the bank-2 5IFUNC table** in L07 to attach a byte-verified
`.ASM` per handler (the per-subfunction folders are README + `.pseudo.c` + verbatim `.npl` until then).

---
_(historical, superseded by the block above)_ MON 60B / N500M — status (one claim made then retracted)

**Byte-verified and solid:**
- `MCTAB[60B] = 030416B = N500M` (read from `044-S3IDPIT.bin`; MCTAB anchors `5B`/`144B` match).
- Full dispatch chain to that point: `MON 60B -> ENT14 -> GOTAB[60B]=MFELL(072114B) -> CALLP ->
  MCTAB[60B]=N500M=030416B`. Real GOTAB (026-S3IMPIT) verified, not the discredited commoncode one.
- `N500M=030416B` appears in **exactly one** symbol file: **SYMBOL-2-LIST**. In the overlay
  SYMBOL-2-LIST describes, `030416B` is the head of an ND-500 disk/paging **DATA block**
  (`N500M, CMD, NSECT, MNBLK, NOOK, DSKAD, 0PCOU, MPAGS, PGCOP, STOP, PAGTA, SECTA`).

**RETRACTED (was wrong for ~1 iteration):** I briefly claimed the executable N500M body is coherent
code at `030416B` in `050-S3I5PIT`. **That is NOT supported.** `050-S3I5PIT`'s own symbol file is
**N500-SYMBOLS**, which contains **no `N500M` and nothing at `030416B`** — so the coherent-looking
code there is a *different* routine of the I5PIT overlay, not N500M. This was the classic
wrong-overlay trap (gotcha 3): coherent bytes in an overlay whose symbol table does not place the
target there. Do not treat `050-S3I5PIT@030416B` as N500M.

**Honest open question:** where is N500M's *executable* body? Two live possibilities, neither proven:
1. **N500M is genuinely a DATA/descriptor block** (SYMBOL-2 names a data structure), and MON 60B's
   service code is a different symbol reached via `CALLP`'s handling of `MCTAB[N]` — which is NOT a
   plain `JMP ,X` (CALLP @ `032201B` is an elaborate level-switch dispatcher, only partly traced).
2. The monitor-level overlay actually mapped at `030416B` for MON 60B is some segment not yet
   correctly identified (for MON 317B the worker overlay was `003-S3CP`; the per-call worker overlay
   varies).

**Next (rigorous):** fully trace `CALLP` (`032201B`) to learn exactly how it consumes `MCTAB[N]` and
which overlay/level the worker runs on. Only then can N500M's real body be located. Do NOT extract
subfunctions until the worker overlay is proven. Supersedes any "050-S3I5PIT byte-verified" wording.

### The suspect conclusion — a live lead, not a fact

The `60B-N500M` folder (README-only, no body) concluded the worker is **outside the carve** because
the symbol `N500M=030416B` "lands in a data/ASCII region".

**A symbol landing in ASCII is the signature of gotcha 3 (wrong overlay), not of absent code.**
`MCTAB[60B]` is populated with a real worker address; MCTAB slots land on named L07 symbols. The far
more likely reading: **the wrong segment was mapped when that address was decoded.** All the big
segments span to `177777B`, so `030416B` decodes in many of them.

**This is a HYPOTHESIS, not a finding.** It must be tested by the coherence method (gotcha 3): take
sibling symbols near `N500M` and find the segment where they ALL land on parallel entries. Do not
record it as fact until the bytes agree.

### Plan for 60B (Phase 1, item 0 — do this FIRST)

1. Pull the symbols neighbouring `N500M=030416B` from the L07 tables to get a sibling set.
2. Sweep **every** carved L07 segment, not the 4 already disassembled, decoding `030416B` in each.
   Score by sibling coherence. Prime suspects: `030-S3SM5`, `062-S3SSM5`, `046-S3S5PIT`,
   `050-S3I5PIT`, `021-S3NMS5`, `025-S3IRPIT`, `026-S3IMPIT`, `003-S3CP`, `044-S3IDPIT`.
3. If a segment wins, disassemble `N500M` and **byte-recover the subfunction dispatch table**.
   Validate it against known manual subfunction numbers before trusting it (gotcha 6).
4. Trace `N500M` down to the **3022 bus interface** IOX/register writes — this is what the emulator
   must reproduce. Cross-check against `ND500-BUS-INTERFACE-REFERENCE.md` and
   `ND500-BUS-OCTOBUS-HW-INTERFACE.md`.
5. **Carve every dependency `N500M` reaches** (each `JPL`/`JMP` target), recursively, until the path
   from MON 60B to the bus registers is closed and byte-verified.
6. Answer **Q6** on the way: does `ND-500-MON:PROG` ever IOX the 3022 directly, or is all register
   access confined to resident SINTRAN? Tracing `N500M` settles it.
7. Only if the sweep genuinely fails everywhere: revisit "outside the carve", and say which segments
   were checked.

**Deliverable:** a real `60B-N500M/` folder with `.ASM` + `.bin` + `.pseudo.c` on the corrected
model, plus a byte-verified subfunction table. It is currently README-only.

---

## 4. Per-call ND-500 status

**Warning:** the ND-500 table in the full MON index asserts in prose that ND-500 calls were "never
affected by the GOTAB bug ... always byte-verified". **That claim is unsupported** — that table has no
worker column, no segment column, no per-row status. Do not rely on it. This section supersedes it.

### 4.1 Bodies byte-verified, dispatch BYTE-PROVEN (level-12 GOSW located 2026-07-15)
`500B` `501B` `503B` `504B` `505B` `510B` `511B` `512B` `513B` `514B` `515B` — see the table in 2.1
and the byte-proven slot map in section 2.2 (GAP 1, now closed): GOSW pointer table at
`137625B`-`137650B` in `017-S3SMPIT`/`026-S3IMPIT` (load `32000B`), dispatcher `N5MPA=137525B`,
L12MIN/L12MAX constants `500B`/`523B` at `137623B`/`137624B`.
**Corrections from bytes:** `504B` -> `NOUTS=141027B` (shares body with `511B DVIO`; the NPL-only
"OSTRS 141205B" claim is disproven — OSTRS is an inner routine); `502B` -> `SWITP=140356B` (=STAPR);
`507B` -> `SPRIO=142033B` (new); `516B`-`523B` -> stubs `M516`-`M523` all routed to `NORMM=137167B`
(unimplemented). `503B` has an extra `ADDENDUM.md`.
**Folder Dispatch sections still describe the old guess — rewrite pending (Phase 2).**

### 4.2 S3SM5 `0x60` vector routing byte-PROVEN, body decode only PARTIAL

| MON | S3SM5 slot | Vector value | Note |
|---|---|---|---|
| 264B ND500ReadFile | `0x01C8` | `0xA7AD` | not a proven instruction boundary |
| 265B ND500WriteFile | `0x01CA` | `0xA825` | partly coherent decode |
| 266B ND500MagTape | `0x01CC` | `0xA89D` | region only **17 bytes** |
| 416B SaveND500Segment | (ND-500 vector) | body @ `0xbd70` | per-page write-back semantics MANUAL-inferred |
| 420B GetUserRegisters | (vector) | `0xBE0F` | 448-byte window does NOT decode as one clean subroutine; the unrolled descending-immediate pattern is *structurally consistent* with copying 39 registers — INFERRED, flagged |

### 4.3 Byte-PROVEN ABSENT (S3SM5 vector slot = `0000`)

| MON | Slot | Note |
|---|---|---|
| 425B SetProcessName | `0x28a` | |
| 426B GetProcessNo | `0x28c` | |
| 427B GetOwnProcessInfo | `0x28e` | expected ND-100 companion `GPRNA` NOT located |
| 436B SetND500Param | `0x29c` | `GOTAB[436]` hit is a **coincidence** into device table `DT85W` — not a handler. Servicing point NOT LOCATED |
| 437B GetND500Param | `0x29e` | same; coincidental hit on `DT86R`. NOT LOCATED |

### 4.4 ND-100-side, worker byte-verified (from `MCTAB`), dispatch section stale

| MON | Worker | Segment |
|---|---|---|
| 60B N500M | `N500M=030416` | resident / 025-S3IRPIT (but see section 3 — data region) |
| 157B SegmentToPageTable | `ENTSG=067764` | resident / 025-S3IRPIT |
| 262B GetSystemInfo | `CPUST=063022` | 006-S3FS |
| 264B | `500RF=026375` | 006-S3FS |
| 265B | `500WF=026401` | 006-S3FS |
| 266B | `500MT=026351` | 006-S3FS |
| 322B GetSegmentNo | `GSGNO=041424` | resident / 003-S3CP |

### 4.5 No per-row evidence in any index
`410B` `411B` `412B` `413B` `417B` `422B` `423B` — the delivery-mirror snapshot claimed
`410B`/`411B`/`416B`/`417B` map to S3SM5 vectors `0x270`/`0x272`/`0x27c`/`0x27e` as "byte-verified",
but that mirror is a stale snapshot (see parent doc section 1a). **Re-verify from bytes before use.**

---

## 5. Segments to attack (Phase 1)

Carved and **never disassembled** — the GOSW table and the driver chain are almost certainly in here.
**"Uncarved" has almost always meant "nobody looked."**

`tools/sintran-segment-carver/versions/L-VSX-500/segments/`

| Segment | Why it matters |
|---|---|
| `030-S3SM5` | ND-500 monitor. HAS an `.asm` already — verify it. Note: a prior pass found **53% of it decodes as `??? opcode 0x0000`**, and concluded an S3SM5-internal MON dispatch table "cannot be enumerated with confidence". Re-examine that conclusion — it smells like a wrong load base or wrong overlay. |
| `062-S3SSM5` | ND-500 monitor, second copy |
| `046-S3S5PIT` | ND-500 PIT |
| `050-S3I5PIT` | ND-500 PIT |
| `020-S3SDT5` | ND-500 device tables |
| `021-S3NMS5` | ND-500 message system — **prime suspect for the 5MPM message handling** |
| `025-S3IRPIT` / `026-S3IMPIT` | resident PIT; `M5TMO` already located in `026` |

---

## 6. PLAN — Phase 1: close the interface

**The interface has TWO directions. Both must close.**
- **ND-100 -> ND-500** = **MON 60B** across the 3022 bus. **Item 0. Highest priority.** Section 3a.
- **ND-500 -> ND-100** = the level-12 / 5MPM path. Items 1-6. Section 3.

**0. MON 60B (`N500M`) + every dependency, down to the 3022 bus registers — LARGELY DONE 2026-07-15.**
   Essentially all `ND-500-MON` commands reach the ND-500 through this call. The wrong-overlay
   hypothesis on `N500M=030416B` was confirmed (5PIT context), the worker + all 47 subfunctions are
   carved, and the downstream ND-500 SYSTEM MONITOR path to the 3022 bus registers is carved end to
   end. **Deliverables:**
   `tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/60B-N500M/`
   ([README](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/60B-N500M/README.md))
   and
   `tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/`
   ([README](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/README.md)).
   Remaining: bank-2 5IFUNC table for per-handler `.ASM`. See section 3a.

1. Disassemble the section-5 segments; promote each to
   `..\..\tools\sintran-segment-carver\versions\L-VSX-500\re\segments-ref\<seg>\` with `.asm` +
   `.symbols.txt` + `.meta.md`.
2. **DONE 2026-07-15 — level-12 GOSW table BYTE-LOCATED** at `137625B` in `017-S3SMPIT` +
   `026-S3IMPIT` (identical), validated against the required slots (0=STAPR, 1=NSTOP,
   11B=DVIO all land) plus ten more. Full slot map + dispatcher (`N5MPA=137525B`) in section 2.2.
3. Byte-locate `5STDRIV`, `CHN5STATUS`, `DECOMESS`, `MCHANDEL` — **addresses now SYMBOL-pinned in
   the same MPIT overlay** (`135010`/`135205`/`135361`/`137206`, plus `MONIC=023030`); remaining
   work = disassemble the bodies at those addresses (grade BYTES).
4. **Confirm from BYTES** that the section-2.3 symbol values are used as message-block offsets
   (look for the `AAX <off>; LDATX` pattern against the message base).
5. Confirm the status codes from the compare instructions in `CHN5STATUS`. Symbol + manual now agree
   (section 2.3) — close it with bytes and it is done.
6. Byte-locate the return path `MONICO`.
7. **Fix the emulator:** delete the fabricated TAG protocol from `NDBusND500IF.cs`, implement the
   byte-verified handshake, and write the interface spec as the deliverable.
8. Rename or delete `..\Emulator\ND500-MESSAGE-STRUCTURE-VERIFIED.md` — the filename is a lie and
   will re-poison the next reader.

### SCOPE NOTE - complete 500 integration needs MORE than MON 60B (2026-07-15)

MON 60B / N500M is only the **front door**: it validates the subfunction code, copies user params to
the MON60 buffer (`5IFUNC` handler), then `GO FAR 5NOPAR` into the **common system-monitor path**.
The actual ND-500 control (5MPM message build, level-12 driver, register/memory transfer, the reply)
happens AFTER that hand-off, in code MON 60B does not contain. To do complete 500 integration we must
also carve:
- the **`5NOPAR` common path** and the **system-monitor worker** it calls (what builds the 5MPM
  message and issues the operation);
- the **resident ND-500 driver** + level-12 handshake (`5STDRIV`, `CHN5STATUS`, `DECOMESS`,
  `MCHANDEL`, the GOSW table - Phase 1 gaps);
- likely more of `050-S3I5PIT`/`062-S3SSM5`/`021-S3NMS5` and the resident overlay.
Keep an eye out while extracting MON 60B: each handler's `GO FAR 5NOPAR` and any `CALL`/`GOSW` that
leaves the 5IFUNC region is a pointer to code that also needs carving. **Pending external input:** the
other session's decode of the **swapper** and **nd-500-mon:prog** will feed this (caller side + first
real ND-500-side code); integrate when it lands.

### Phase 3 - ND-500 bus interface deep validation + CPU bring-up (AFTER extraction; user-defined 2026-07-15)

Once MON 60B + the other ND-500 MON calls are extracted, do a deep validation pass on the ND-500 bus
interface docs and connect the ND-500 CPU. **The 2026-07-15 ND-500 SYSTEM MONITOR carve already
supplies the byte-grounded inputs for items 2, 3 and 6** (the 3022 IOX register map, the memory-mapped
register window, the control-store gate, the 5MPM message layout + `ACT50` activation, and the
level-12 return path) - see
`tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/`
([README](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/README.md)) and
its [`ND500-3022-IOX-INTERFACE.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/ND500-3022-IOX-INTERFACE.md),
[`ND500-CONTROL-STORE-GATE.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/ND500-CONTROL-STORE-GATE.md),
[`ND500-5MPM-MESSAGE-AND-ACTIVATION.md`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/ND500-5MPM-MESSAGE-AND-ACTIVATION.md).
User's explicit questions to answer:

1. **Validate the bus-interface documentation we have** (`ND500-BUS-INTERFACE-REFERENCE.md`,
   `ND500-BUS-OCTOBUS-HW-INTERFACE.md`, `ND500-ND5000-INTERFACE-COMPREHENSIVE-GUIDE.md`,
   `WHERE-IS-5MPM-LOCATED.md`): analyse deep, validate against bytes, extend where incomplete. Purge
   any remaining fabricated content (the TAG protocol - section 2.4).
2. **Do we actually understand the IOX messages, queues, slots?** Map every IOX command/register on
   the 3022, the 5MPM message-block layout (offsets in section 2.3), the message status/handshake
   state machine (section 3), and the queues (exec queue / MAILINK / time queue). Confirm from bytes,
   not NPL.
3. **Map the bus interface correctly so the emulator can connect the ND-500 CPU.** The ND-100 side is
   memory-mapped register block @ ND-100 word `010424000B` (section MEMORY-CONFIGURATION); ND-500
   register access is confined to resident SINTRAN (zero-IOXT finding). Build the interface spec.
4. **How does the ND-500 CPU logic map to the board on the 500 side of the cabinet?** How the
   hardware interface works physically. (Needs `ND-05.020` ND-5000 Hardware Description, which we may
   not have - flag if missing.)
5. **How does the code running on the ND-500 work - is it the swapper?** The swapper (`SWAPPER-K`) is
   the first real ND-500-side code (Q4; `old\SWAPPER-K01-ANALYSIS.md`). Clarify swapper vs domain
   vs user program on the 500.
6. **Options for loading and setting things in the ND-500 CPU.** Enumerate: `LOAD-CONTROL-STORE`
   (microcode/WCS - see MON 60B `037B ICSLOAD`), `LOAD-SWAPPER` (`007B IPLSWAPPER`), register
   deposit/examine (MON 60B `026B-033B`), memory read/write (`004B/005B/033B`), `MICRO-START`.
7. **How do we get the ND-500 bootstrapped?** The bring-up sequence (Micro Program Guide 16.4):
   `MASTER-CLEAR -> MICRO-START 0 -> LOAD-SWAPPER -> START-SWAPPER -> GIVE <pages>`, plus the
   control-store gate (`ECSLOAD`) the emulator must satisfy. Ties to the missing `CONTROL-STORE:DATA`
   microcode (Q7) and the control-store-loaded check (section 6 item 7). **This is where the whole
   effort converges: MON 60B `037B ICSLOAD` extraction (current work) is the first concrete piece.**

Deliverable: a validated, byte-grounded ND-500 bus-interface + bring-up spec the emulator can
implement to actually run/connect the ND-500 CPU.

### Phase 2 (ND-500-touching cleanup only)
- Rewrite the ND-500 folders' Dispatch sections onto the real GOSW.
- Finish partial bodies: `264B` `265B` `266B` `416B` `420B`.
- Locate the `436B`/`437B` servicing point.
- Reconcile `ND500-MONITOR-CALL-MECHANISM.md` vs `ND500-L-RELEASE-RE-TASK-HANDOFF.md` — they
  disagree on whether the MICFU values are known (the mechanism doc lists `3MONC=24B` from symbols;
  the handoff calls them unverified). Section 2.3 suggests the mechanism doc is right.
- Give the full index's ND-500 table a real worker/segment/status column; delete the unsupported
  "always byte-verified" prose.

---

## 7. Open questions (from ND500-L-RELEASE-RE-TASK-HANDOFF.md)

| Q | Question | Status |
|---|---|---|
| **Q2** | message status code values | **LARGELY CLOSED 2026-07-15** — see 2.3. Confirm with bytes. |
| **Q3** | the USER side of the monitor-to-driver interface: which MON calls the background monitor issues, with which parameter blocks. The `:PROG` side is undocumented | **PARTLY ANSWERED 2026-07-15 (REPORTED)** — it issues exactly ONE: `MON 60B`, from a single wrapper at `146256`, `A` = param-list pointer. The param-block *contents* per subfunction are still open. See 3a |
| **Q6** | does `ND-500-MON:PROG` ever IOX the 3022 directly, or is register access confined to resident SINTRAN? (spec predicts the latter) | **ANSWERED 2026-07-15 (REPORTED)** — **ZERO `IOXT` in the program. Register access IS confined to resident SINTRAN.** The spec's prediction holds. Re-verify from bytes to promote to VERIFIED. See 3a |
| Q1 | 211305 floppy contents | OPEN |
| Q4 | `SWAPPER-K:PSEG/DSEG` — first real ND-500-side code | partially analysed, see `swapper\` |
| Q5 | segment capability word; contradiction C9: 11-bit vs 12-bit segment field | OPEN |
| Q7 | microcode image | **artifact NOT FOUND on `F:\ND`** |

---

## 8. MAINTENANCE RULE

**Update this file IN THE SAME change as the analysis work.** It is the ND-500 status of record.

| Trigger | Update |
|---|---|
| An ND-500 **MON call** analysed / corrected | Section 4 (right subsection), and 2.1 if a body is pinned |
| An ND-500 **segment** disassembled / promoted | Section 5, tick section 6 |
| **NPL** code analysed | Cite it, grade it **NPL**. NPL never promotes to VERIFIED |
| A **symbol** artifact read | Section 2.3; validate against 2 known values first (gotcha 6) |
| A table/address/offset **byte-proven** | Upgrade its grade and say which bytes. Move it out of "the gap" (2.2) |
| A claim **disproven** | Delete it, record it in 2.4 as a poisoned prior. Do not leave it hedged |
| A **Phase-1 item lands** | Tick in section 6, update 2.2 |

- **All paths E: only.** `E:\Dev\Ronny\NDInsight\`. The D: drive was a one-off delivery mirror and is
  NOT a destination — never write there.
- **Never upgrade a grade without reading the bytes yourself.**
- Do not let a "VERIFIED" in a filename or a prose blanket-claim substitute for a per-row status.
  Both have already burned this effort (2.4).

---

## 9. FULL DOCUMENT INDEX (ND-500)

### Status / entry points
| Doc | What |
|---|---|
| **this file** | ND-500 status of record |
| [`OCTOBUS-SWAPPER-HANDOFF-2026-07-25.md`](OCTOBUS-SWAPPER-HANDOFF-2026-07-25.md) | **NEWEST swapper state.** Swapper runs 420 instructions with no throw and sits in its MON 377B message-wait loop at `P=0x08000677`; blocker moved from microcode to the octobus transport (announce sink is a stub). Eight microword gaps closed; MULAD carry adjudicated across all three lanes; sweep-diff polarity is `golden!=microword` |
| [`..\CARVING-HANDOFF.md`](../CARVING-HANDOFF.md) | parent: overall carving + MON status |
| [`README.md`](README.md) | ND-500 folder readme |

### Interface / mechanism
| Doc | Grade / caution |
|---|---|
| [`ND500-MAILBOX-MESSAGE-CATALOG.md`](ND500-MAILBOX-MESSAGE-CATALOG.md) | **The complete 5MPM message spec for the emulator**: all fields + direction overlays (11B/13B), every MICFU, STOPR codes, ISR dispatch tables, MONICO write-back, watchdog/HIMESS/DUMMESS, swapper MSW*/MON 377B family, 11 explicit UNKNOWNS. NOTE: its "40B-47B result block: no symbol evidence" caution is now SUPERSEDED by `CARVE-ANSWER-RESULT-BLOCKS-2026-08-10.md` (the block exists - it is the info-block 5DDn/5Pn array, not a message structure); still correctly flags MP-P2-N500.md sec 7.6 as a conflicting NON-mailbox table |
| [`ND500-WHO-ANSWERS-THE-MAILBOX.md`](ND500-WHO-ANSWERS-THE-MAILBOX.md) | **The mailbox servicer is THE MICROCODE** (hence MICFU) - not the 5015, not the swapper; three-layer model, MICFU handling map, emulator role mapping. MANUAL/DERIVED + trace-consistent |
| [`ND500-CS-LOAD-TRACE-FINDINGS-2026-07-16.md`](ND500-CS-LOAD-TRACE-FINDINGS-2026-07-16.md) | **OBSERVED (live traces of real SINTRAN + nd-500-mon J04).** The complete CS-load protocol incl. the previously UNDOCUMENTED verify pass (words 0-7 read-back; mismatch aborts BEFORE micro-start); SLOC5/UNLC5/MCLR5 strobe on IOX READ; RETG5 bit1-clear = clock restart; bare LCON5 activate = lock only. Where it disagrees with the bus reference, the trace record wins |
| [`CARVE-ANSWER-Q7-COMPLETION-POLL-VS-INTERRUPT.md`](CARVE-ANSWER-Q7-COMPLETION-POLL-VS-INTERRUPT.md) | **Q7: completion detection is INTERRUPT-DRIVEN (level 12), not RSTA5 poll.** [V-NPL] walk of `5STDRIV`/`XACT500`/`CLE5STATUS`/`CHN5STATUS` + [V] L07 symbols. RSTA5 has no finished bit; payload read from MPM `N5STA`. See section 0d. GAP: L07 5STDR byte disassembly |
| [`CARVE-ANSWER-RESULT-BLOCKS-2026-08-10.md`](CARVE-ANSWER-RESULT-BLOCKS-2026-08-10.md) | **The MON 60B "answer result block 40B-47B" decoded: it is the info-block `5DD1..5DD5`/`5P1..5P5` parameter array (3-word stride, 40B-56B), NOT a message structure.** [V bytes+SYMBOL] 5FP2E frame map (B-11=info @165777B, B-67=message, B-65=ABUFA, B-56=CPU-DF); full per-command result table (NPL post-return FUNCS); mailbox answer offsets per command (16B/17B register value @ msg 10B-11B, examine @ msg 11B-12B, 3RMICV version @ msg 7 + CPU param @ msg 10B, CSLOA's version-verify + CPUDF[-7]/[20B] cache); RSTAT's third word = 5015 WA reg & 37777B; classic microcode (CONT-STORE-10611) cross-check incl. fn 1 `LARG 24563B`=10611 answer. Servicer modeling list in sec 5 |
| [`CARVE-ANSWER-DEFMC-MPM-BASE-051302-2026-08-10.md`](CARVE-ANSWER-DEFMC-MPM-BASE-051302-2026-08-10.md) | **051302B-051450B in 030-S3SM5 = RLSWM/RELAA/RELAL/PTOS3, ZERO IOX - the "MPM BASE register programming" DEFMC was said to delegate to does not exist.** [V bytes] full annotated carve + whole-segment IOXT inventory + [V manual] ND-10.004.01 §2 (MPM-5 port registers set only from the MPM cabinet's own maintenance console). Retires design-doc TODO 2's premise; MPM window base = machine config, no new emulator register |
| [`CARVE-ANSWER-TRAP-RECORD-OFFSETS-AND-MMS-BITS-2026-08-11.md`](CARVE-ANSWER-TRAP-RECORD-OFFSETS-AND-MMS-BITS-2026-08-11.md) | **The trap record's per-trap fault-parameter offsets + the MMS status word bit numbers (hardware order).** [V-MC] B30 ADACT/ORCON pipeline decoded (4 anchor matches vs SINTRAN symbols): page fault 46B = LA@17-20, phys-seg@21, MMS@22-23; GEN3-class traps (PV/trace/THM/HWF 51B) = LA@17-20, MMS@21-22, PHYS@23-24, phys-seg@25, WR@26 (+ASTS@27, BADAP@30). [MANUAL] ND-05.017.01 A.12: read/write = STATE7-5 bits 31-29, DATA/PROGRAM = bit 6, TSB-miss = bit 11, trap sub-code = bits 3-0; "WR" in reports = the WR REGISTER word, not a bit. Emulator `AnswerTrapStop` write list in §5. Its [OPEN] classic-10611 item is CLOSED by the next row (layout NOT identical) |
| [`CARVE-ANSWER-CLASSIC-TRAPWRITER-S2-CONTROL-2026-08-11.md`](CARVE-ANSWER-CLASSIC-TRAPWRITER-S2-CONTROL-2026-08-11.md) | **The CLASSIC (CONT-STORE-10611) trap-stop writer read from the real control store: `011271-011337`.** [V-MC classic] Header agrees with B30 (STOPR:=2@11, P@12-13/14-15 from ctx[224B]/[240B], TRAPN@16); trap-dependent area DIVERGES: 46B = LA@17-20 + physseg@21 (7777B mask) + ONE composed status hw@22 (TRAPINF<<8\|subtype, bit6=program); {44B,51B} = real-addr/logical-addr/DSTS-composites/DCINHLL 7-slot record ending @31; {25-27B} = LL + ctx[124B]; 45B and rest = NO params. Also: micro-trap sorter entry `011022` (init `000627`), mid-run activate resume mechanism (queue walk accepts N5STA 1 AND 2, `011473` skips reload for the current process, re-entry `011370->011401` JMPMAP), and CONTROL bit 8 = power-fail save (writer: PH-P2-RESTART 5PF `LCON5:=400B`+SLOC5+TERM5 [V-NPL]) / bit 6 = keep-current-process across terminate (no SINTRAN writer exists - NOT FOUND). AL#10 flag pair fully mapped |
| [`CARVE-ANSWER-PRSTART-STOPINFO-SOURCE-2026-08-11.md`](CARVE-ANSWER-PRSTART-STOPINFO-SOURCE-2026-08-11.md) | **RUNN's 200B "stop (trap) info" source: message hw 12B..41B, MOVEW'd into the MON60 com-buffer by 030-S3SM5's trap-stop builder** (`PROGS` STOPR dispatch 146726-146742, trap builder 064300, copy 064415-064426), then `TOUSMOVE` from LOGBADR to the user's 5P2. [V bytes, pool words re-read] Stop block word N = message hw N+12B; words 24-63 stale. 5DD1 stop reason = (0, TRAPN) @065141-065143. Covers FREL5's break-state answer too |
| [`CARVE-ANSWER-PST-WRITER-VS-PSPHS-2026-08-11.md`](CARVE-ANSWER-PST-WRITER-VS-PSPHS-2026-08-11.md) | **PSPHS/PSLLI/PSULI/PSMOD are parallel ND-100 bookkeeping - the MMU-walked PST is NOT built from them.** PST base = SINTRAN allocation (ALLOC->SSYSE) handed over as patched control-store cell 0o21; PST entries maintained by the SWAPPER [V elimination + ND-05.017.01 :4648/:4658/:4662]; RESIWR/13B/14B never carry PST entries. [OPEN] exact swapper store sites, cell-21 patcher, ND-100 first-page seeding (manual :3681) |
| [`ND500-TO-SINTRAN-MON-MAPPING.md`](ND500-TO-SINTRAN-MON-MAPPING.md) | **Complete MON-call mapping ND-500 -> SINTRAN/ND-100 (2026-07-30).** The `callg $0xF80000NN` seg-31 gate (NN = MON number as integer, VERIFIED vs DEABF/DVOUTS/B5XMSG); MCHANDEL GOSW table 500B-523B vs below-500B forward to native MCTAB; shared vs ND-500-specific numbers; the definitive >255 answer (ND-100 native MON = 8-bit field, 377B=255=0xFF boundary; ND-500 MCNO is a 16-bit SOFTWARE-decoded field, no limit); arg marshalling via 4.2.5.2 + 5AP1..5AP4/NUMPA. Per-claim [VERIFIED]/[INFERRED] |
| [`MICROCODE-ANSWER-MON-CALL-SCREENING-2026-09-26.md`](MICROCODE-ANSWER-MON-CALL-SCREENING-2026-09-26.md) | **Which monitor calls the ND-5000 (B30) microcode treats specially, read from RAW microwords.** [V] `CALL_MON` stop-record layout (address array HW 40B+, value array HW 100B+, P@7, STOPR/NUMPA/MCNO@11B-13B); the `CALL_END` screening table CORRECTED for the one-word condition delay (the D: pseudocode note is off by one row: `500->CALL_STAP`, `501->CALL_STOP`, `502->CALL_SWIP`, `600->CALL_NDIX`; `117/120/144` = cache dump, NOT a wait variant); 504/511/512 inline buffer copy `CALL_5_MATCH` fully decoded (param 2 = count, max `BM13` = 2048 = 4000B, param 3 = buffer, dest = `ABUFA`*2, argc >= 3, error X1=1003B+K); `CLR_DUDC` = 1024 x `CCD` gated on modus bit 6 `EWICO`; 500/501/502 local start/stop assist gated on X500DF word 2 bit 0 - **CLOSED on SINTRAN L07** (XMSINIT zeroes it, nothing writes it), so they are plain monitor calls; the local STOPPR is a 1:1 copy of NSTOPROC (13B = `STOPPED`); 515 answers at once + cache dump [D]. **Section 7 = MEASURED results** (test `MonCallInlineCopyTests`, 8 green): 2048 in / 2049 out, 513 not copied, refusal X1=1003B K=1, and the copy destination `0xFFF00000 + 2*ABUFA` = **the ND-100 memory window is the top MB of ND-5000 physical space** (`ZERO_P` 000027). Classic 10611 store: same 504/511/512 copy + 4000B limit, error code 174, NO cache dump / local start-stop / 515 path. `BMnn` = 1 << nn(OCTAL). Written for Tor's MON-call questions; Tor's copy = `D:\ND\t\re\mon-analysis` addendum |
| [`ND500-MONITOR-CALL-MECHANISM.md`](ND500-MONITOR-CALL-MECHANISM.md) | v1.1. **NPL + symbol only, no carved bytes.** Origin of the section-3 model |
| [`ND500-MONITOR-CALL-PARAMETER-PASSING.md`](ND500-MONITOR-CALL-PARAMETER-PASSING.md) | cited second-hand by the activation doc |
| [`ND500-BUS-INTERFACE-REFERENCE.md`](ND500-BUS-INTERFACE-REFERENCE.md) | section 7.4 = MICFU function codes |
| [`ND500-BUS-OCTOBUS-HW-INTERFACE.md`](ND500-BUS-OCTOBUS-HW-INTERFACE.md) | HW interface |
| [`ND500-ND5000-INTERFACE-COMPREHENSIVE-GUIDE.md`](ND500-ND5000-INTERFACE-COMPREHENSIVE-GUIDE.md) | |
| [`ND500-IF-LOCKING.md`](ND500-IF-LOCKING.md) · [`ND500-IF-USAGE-DEEP-ANALYSIS.md`](ND500-IF-USAGE-DEEP-ANALYSIS.md) | locking / usage |
| [`WHERE-IS-5MPM-LOCATED.md`](WHERE-IS-5MPM-LOCATED.md) | 5MPM location |
| [`ND5000-SAMSON-ARCHITECTURE.md`](ND5000-SAMSON-ARCHITECTURE.md) | |

### DOMINO / NUCLEUS / octobus driver carve (2026-07-19, byte-verified)
| Doc (under `tools\sintran-segment-carver\versions\L-VSX-500\re\domino-nucleus-io\`) | What |
|---|---|
| `BDIO-DOMINO-DRIVER-CARVE.md` | In-kernel DOMINO block-I/O: STRBDIO/REBDIO/MBUILD/DCNVA, fn 166B/167B/213B message layout, NKWRI/NKSEN/NKREC/NKREA gates, HSTAT ladder, pseudo-C. See section 0e |
| `OCTOBUS-DRIVER-ROUTINES-CARVE.md` | SKICK/MBSEND/OMBREAD + XKICK500/5OMBREAD/MFPREPARE/CON5IDENT/5MTRANS bodies, LMFIELD consumption, wire bytes, pseudo-C. See section 0e |
| `NUCLEUS-PRIMITIVES-CARVE.md` | NKSEND/NKGETINFO/NCALL/NKWRI + NUCST, kernel structure byte layout (master block/port/message/kick table), NKSEND->SKICK kick path, MON 347B=SERVE. See section 0e |
| `NUCLEUS-SEGMENTS-RECON.md` | Segments 104-107 (NKSE/NKNA server) recon + follow-up carve target list |
| [`..\ND5000\OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md`](../ND5000/OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md) | The device/controller architecture + RetroCore reusable-objects design + phased plan that drove this carve |

### MON calls
| Doc | Note |
|---|---|
| [`MON\ND500-MON-CALL-ROUTING-MAP.md`](MON/ND500-MON-CALL-ROUTING-MAP.md) | GOSW at NPL MP:1385; concludes S3SM5 table "cannot be enumerated with confidence" (53% undecodable) — **re-examine** |
| [`MON\ND500-MON-ACTIVATION-AND-MAPPING.md`](MON/ND500-MON-ACTIVATION-AND-MAPPING.md) | offsets here are **second-hand** — use `swapper\N500-SYMBOLS.SYMB` |
| [`MON\README.md`](MON/README.md) | |
| [`ND500-MON-RE-FINDINGS.md`](ND500-MON-RE-FINDINGS.md) | |
| [`mon-oracle-for-NC\`](mon-oracle-for-NC/) | NC deliverables: `262B-CPUST`, `312B-MOINF_317B-UECOM`, tier2, tier3. **NB: the shipped 312B/317B GOTAB values were WRONG and corrected** — see parent doc 3a |

### Swapper — contains the primary symbol artifact
| Doc | Note |
|---|---|
| [`swapper\N500-SYMBOLS.SYMB`](swapper/N500-SYMBOLS.SYMB) | **PRIMARY ARTIFACT** — the offsets + status codes in 2.3. Flat, 5-char-truncated, alphabetical |
| [`old\SWAPPER-MON-DISPATCH.md`](old/SWAPPER-MON-DISPATCH.md) | the only doc that correctly cites the symbol file |
| [`old\SWAPPER-K01-ANALYSIS.md`](old/SWAPPER-K01-ANALYSIS.md) · [`SWAPPER-K01.PSEG.asm`](old/SWAPPER-K01.PSEG.asm) | first real ND-500-side code (Q4) |
| [`ND500-SWAPPER-ANALYSIS.md`](ND500-SWAPPER-ANALYSIS.md) · [`ND500-SWAPPER-LOADING-MECHANISM.md`](ND500-SWAPPER-LOADING-MECHANISM.md) | |

### Execution / scheduling / setup
[`ND500-INITIALIZATION-AND-EXECUTION-GUIDE.md`](ND500-INITIALIZATION-AND-EXECUTION-GUIDE.md) ·
[`ND500-SCHEDULING-ANALYSIS.md`](ND500-SCHEDULING-ANALYSIS.md) ·
[`SINTRAN-DOMAIN-SETUP-DEEP-DIVE.md`](SINTRAN-DOMAIN-SETUP-DEEP-DIVE.md) ·
[`ND500-PLACE-LIBRARY-C9-FINDINGS.md`](ND500-PLACE-LIBRARY-C9-FINDINGS.md)

### Audit / contradictions — READ BEFORE TRUSTING ANYTHING
[`ND500-EVIDENCE-AND-CONTRADICTIONS.md`](ND500-EVIDENCE-AND-CONTRADICTIONS.md) ·
[`ND500-EMULATOR-DISCREPANCY-AUDIT.md`](ND500-EMULATOR-DISCREPANCY-AUDIT.md) ·
[`ND500-L-RELEASE-RE-TASK-HANDOFF.md`](ND500-L-RELEASE-RE-TASK-HANDOFF.md) (**records the TAG fabrication**) ·
[`ND500-L-PACKAGE-CONTENTS.md`](ND500-L-PACKAGE-CONTENTS.md)

### Session handoffs (historical)
[`ND500-RE-SESSION-HANDOFF-2026-07-08.md`](ND500-RE-SESSION-HANDOFF-2026-07-08.md) ·
[`ND500-RE-SESSION-2-HANDOFF.md`](ND500-RE-SESSION-2-HANDOFF.md)

### NPL source docs (grade: NPL — logic only)
[`MP-P2-N500.md`](MP-P2-N500.md) (driver; GOSW @ :1385, MCHANDEL @ :1251-1406) ·
[`CC-P2-N500.md`](CC-P2-N500.md) (`MONICO` @ :363-372) ·
[`RP-P2-N500.md`](RP-P2-N500.md) · [`XC-P2-N500.md`](XC-P2-N500.md)

### `old\` — superseded, do not cite without re-verifying
[`old\MP-P2-N500_API_Documentation.md`](old/MP-P2-N500_API_Documentation.md) ·
[`old\ND-500-INTERFACE.md`](old/ND-500-INTERFACE.md) ·
[`old\ND500-BOOT-DETECTION-MECHANISM.md`](old/ND500-BOOT-DETECTION-MECHANISM.md)

### Emulator side — CONTAINS POISON (section 2.4)
| File | Status |
|---|---|
| `..\Emulator\ND500-QUICK-REFERENCE.md` | **FABRICATED TAG codes** |
| `..\Emulator\DETAILED-TAG-MECHANISM-EXPLANATION.md` | **FABRICATED TAG codes** |
| `..\Emulator\ND500-MESSAGE-STRUCTURE-VERIFIED.md` | **MISNAMED** — content disclaims everything the name implies |
| `..\Emulator\ND500-EMULATION-COMPLETE.cs` · `Interface3022-5015.cs` · `ND100-Interrupt-Level-12-Handler.cs` · `ND500-SEGMENT31-TRAP-HANDLER.cs` | emulator code — audit against Phase 1 output |
| `..\Emulator\ND500-MESSAGE-STRUCTURE-VERIFIED.md`, `ND500-INTEGRATION-GUIDE.md`, `ND500-ENTB-IMPLEMENTATION-GUIDE.md`, `INTEGRATION-WITH-EXISTING-3022.md`, `INTEGRATION-GUIDE-SEGMENT31.md`, `ND100Bridge.md`, `KERNEL-ACCESS-EMULATOR.md`, `MONITOR-CALL-DEBUGGING-GUIDE.md` | integration docs — re-verify |
| RetroCore `NDBusND500IF.cs` | fabricated TAG protocol **PURGED 2026-07-16** (Phase 1 de-fabrication); now carries the carve-verified register/TAG/CS/mailbox model, live-validated |

### Carved data
| Path | What |
|---|---|
| `..\..\tools\sintran-segment-carver\versions\L-VSX-500\segments\` | all carved segments (section 5) |
| `..\..\tools\sintran-segment-carver\versions\L-VSX-500\re\mon-analysis\` | 156 call folders |
| [`..\..\tools\...\re\ND500-SYSTEM-MONITOR\`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/README.md) | **ND-500 SYSTEM MONITOR carve (2026-07-15)** - `030-S3SM5`: FUNCS table, 3022 IOX driver + register map, control-store gate, 5MPM + `ACT50`, level-12 return path. See sections 3a, 6 |
| [`..\..\tools\...\re\mon-analysis\60B-N500M\`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/60B-N500M/README.md) | **MON 60B / N500M worker carve (2026-07-15)** - worker `030416B` (5PIT), all 47 `5IFUNC` subfunction folders, `5NOPAR` common path, caller-vs-worker cross-analysis |
| `..\..\tools\sintran-segment-carver\versions\L-VSX-500\re\MON-CALL-INDEX.md` | **authoritative** full MON index |
| `..\NPL-SOURCE\SYMBOLS\{K03,L07,M06}\` | per-version symbol tables |
