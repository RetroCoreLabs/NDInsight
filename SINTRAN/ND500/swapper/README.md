# ND-500 Swapper (SWAPPER-K01) - Binaries and Reverse-Engineering Analysis

The ND-500 swapper domain (SWAPPER-K01): its program and data segment binaries, the
resident ND-500 monitor symbol table, the current disassembly, and the RE write-ups.

> **Path convention.** Every file reference in this folder and its documents is written
> as a path from the repository root `E:\Dev\Ronny\NDInsight`
> (for example `SINTRAN/ND500/swapper/swapper-k01.pseg.md`). No bare filenames, no
> absolute host paths, no `../` links.

---

## Start here

Read `SINTRAN/ND500/swapper/swapper-k01-deep-analysis.md` first. It is the end-to-end
deep dive (role determination, MON 377B descriptor decode, request/response loop,
5MPM / front-door mapping) and it supersedes and partly corrects the older write-ups now
kept under `SINTRAN/ND500/old/`.

## What the swapper is

SWAPPER-K01 is the **ND-500-side paging/swap worker** - a native ND-500 domain
(`{PSEG, DSEG}` based at `0x08000000`) and a **CLIENT of SINTRAN**, NOT the low-level
handler that does ND-500 work for the ND-100. From the byte-level analysis:

**What it does**

- **Receives work as messages** posted into ND-100 private memory and pulls them across by
  **RIOM DMA** (3 sites in the PSEG). It is the ND-500 side of ND-500 **process #0**.
- **Dispatches each request on its own private 29-entry function-code table** (a `jumpg`
  through a table in the DSEG) - a per-request function code keyed into its own handler
  set, not a MON-number dispatcher.
- **Does the page moves itself, in-domain**, with the ND-500 physical-segment page
  primitives: **RPHS** (read physical segment, x2), plus **PCTSB** (x3) and **DCTSB** (x4)
  translation-buffer operations. This is the actual paging/swap work.
- **Traps outward to the ND-100 / SINTRAN only** when it needs a cross-machine service.
  Every **MON 377B** (15 sites) is an outward trap into logical segment 31
  (`0xF80000FF` = monitor call 255 = **N5SWAP**), used for e.g. swap-disk transfer and
  fatal-error reporting. It terminates via **MON 0B** (LEAVE).

**What it is NOT**

- It does **not** touch the bus-interface hardware - the 3022/5015 IOX registers are
  ND-100 I/O space it cannot reach.
- It has **no receive-side MON dispatcher** - every trap direction is outward; it is a
  service *requester*, not the trap target for ND-500 monitor calls.
- The actual swap-disk I/O is done by a **separate ND-100 RT-program (5SWAP)**, not by
  this domain.

**Two corrections the deep analysis established against earlier notes:** WPHS is absent
(only RPHS is present), and the pre-trap "internal call with identical args" is a
trace/log routine gated by a flag, not a try-local-then-forward fast path.

---

## Canonical file set

| File | What it is |
|------|------------|
| `SINTRAN/ND500/swapper/swapper-k01-deep-analysis.md` | THE deep dive - start here. Role determination, MON 377B descriptor decode, request/response loop, 5MPM / front-door mapping. |
| `SINTRAN/ND500/swapper/swapper-k01-handlers.md` | The 29-entry function-code dispatch table decoded: each `MSW*` code -> handler target -> behaviour (27 of 29 PROVEN-shape). The ND-100 side that sets the code (`SWPST`) is in `SINTRAN/ND500/ND500-SWAPPER-ANALYSIS.md` section 12. |
| `SINTRAN/ND500/swapper/swapper-k01.pseg.md` | Pseudo-C analysis of the program segment: routine inventory and the MON 377B gate mechanism. |
| `SINTRAN/ND500/swapper/swapper-k01.dseg.md` | DSEG hex/string dump plus the PSEG -> DSEG cross-reference. |
| `SINTRAN/ND500/swapper/swapper-k01-pseg.asm` | ND-500 disassembly of the PSEG (base 0x08000000, 12046 lines). The current, richer listing. |
| `SINTRAN/ND500/swapper/SWAPPER-K01.PSEG` | ND-500 program segment binary (I-space, 38161 bytes). |
| `SINTRAN/ND500/swapper/SWAPPER-K01.DSEG` | ND-500 data segment binary (D-space, 218117 bytes). |
| `SINTRAN/ND500/swapper/N500-SYMBOLS.SYMB` | Resident ND-500 monitor symbol table (7157 symbols). |
| `SINTRAN/ND500/swapper/README.md` | This index. |

---

## Superseded / history

These three files used to live in this folder and were absorbed and partly corrected by
the canonical set above; they now live under `SINTRAN/ND500/old/`. Notable corrections:
WPHS is absent (only RPHS is present), RIOM DMA does exist, and the pre-trap "internal
call with identical args" is a trace/log routine, not a fast-path.

- `SINTRAN/ND500/old/SWAPPER-K01-ANALYSIS.md` - the earlier reverse-engineering analysis.
- `SINTRAN/ND500/old/SWAPPER-MON-DISPATCH.md` - the earlier MON-dispatch write-up.
- `SINTRAN/ND500/old/SWAPPER-K01.PSEG.asm` - the older, plain disassembly.

---

## Live execution status (2026-07-20)

This swapper now **actually executes** on the RetroCore functional `CpuND500` under live SINTRAN L,
which turned several parts of this analysis into live-verified facts:

- **Link base confirmed:** the disassembly base `0x08000000` is real - the swapper runs in **logical
  segment 1**, with code and data in the SAME segment separated by the I/D split (program capability
  -> PSEG, data capability -> DSEG). SINTRAN itself places the executable at MPM physical `0x06F800`,
  byte-for-byte identical to `SWAPPER-K01.PSEG`.
- **Entry sequence confirmed instruction-for-instruction:** `init $1000441124` = `0x08024254` (the
  stack bottom in section 5.1) and `call $1000100645` = `0x080081A5` both matched live traps exactly.
- **The RIOM intake is where it currently stops:** `1000101356: h riom $1000440264,$1000440274,
  $1000440074+` (= `0x240B4`/`0x240BC`/`0x2408C`) writes to address ~0 because **the DSEG content is
  never loaded** - `0x24800` stays zero although the data page table reserves 107 pages
  (`0x35800` = 219,136 bytes vs `SWAPPER-K01.DSEG` = 218,117). The swapper is running against an
  empty data segment. How DSEG content is meant to be delivered is the open question.
- **Retired prior:** "the swapper is control-store microcode" was wrong. Microcode is only what
  "> Loading Control Store" puts in the CPU's control storage; this swapper is ordinary ND-500
  executable code.

Details: [`../ND500-D4-RUN-BLOCKER-FINDING-2026-07-19.md`](../ND500-D4-RUN-BLOCKER-FINDING-2026-07-19.md)
sections 12d-12j; status of record [`../ND500-STATUS-AND-INDEX.md`](../ND500-STATUS-AND-INDEX.md)
section 0g.

---

## Reading the listing notation (`swapper-k01-pseg.asm`)

Written down 2026-09-21 after two carve attempts produced candidate readings that failed their
own checks, purely because of notation. Every entry here is from **ND-05.009.4** (the ND-500
Reference Manual), not inferred from the listing.

| In the listing | What it is |
|---|---|
| `w1 := b.30` / `by4 := r.24` | LOAD. The prefix names the register (`1`-`4`) and the operand WIDTH: `by`=byte, `h`=halfword, `w`=word. |
| `w1 =: b.104` | STORE, same reading, arrow the other way. |
| `by1 laddr r.36` | `BYn LADDR` = "byte load address", ch.15.4: `addr(<operand>) -> Rn`. Loads the ADDRESS, not the value. The `by`/`h`/`w` prefix here sets only the INDEX SCALING - it is not the width of the address. |
| `@b.134`, opcode byte `305` | `IND(B.(displ):B)` - **local indirect, byte displacement**, §8.6. Its own words: the displacement plus the local base "forms the address of a word which holds the address of the operand". So `w1 =: @b.134` writes THROUGH a pointer; `w1 =: b.104` right after it keeps the address itself. Subroutine arguments normally arrive this way. |
| `r := b.64` | Loads the RECORD register from a local word. Afterwards `r.NN` is that base plus NN. |
| `r.NN` displacements | **BYTE offsets.** Cross-check: this is what makes `by4 := r.24` the descriptor byte whose `0x04`/`0x06` value drives the allocate-on-touch fork. |
| `by shl r1,$72` | Shift counts are **6-bit two's complement**, so `$72` = `-6` = shift RIGHT by 6, not left by 58. |

**The trap this notation sets.** At `1000021533` the two arms each `laddr` a DIFFERENT base -
`by2 laddr r.66` (per-page bitmap) and `by1 laddr r.36` (file index) - and then run COMMON code
that reads `r.14` off whichever base it was given. So an offset quoted from the shared code is
meaningless until you say which arm reached it, and the two structures have the SAME SHAPE,
which makes a wrong rebase look plausible. The discriminator between a working and a failing
segment is not a flag the shared code tests; it is which structure the arm points at and what
is in it.

## Related

- `SINTRAN/ND500/ND500-SWAPPER-LOADING-MECHANISM.md` - **how SINTRAN loads the swapper (INZ500,
  MSINIT, 5SWRT)** - the first place to look for the missing DSEG-delivery step.
- `SINTRAN/ND500/ND500-SWAPPER-ANALYSIS.md` - swapper FIFO/queue mechanics from the ND-100 side.
- `SINTRAN/ND500/ND500-SWAPPER-LOADING-MECHANISM.md` - how SINTRAN loads the swapper (INZ500, MSINIT, 5SWRT).
- `SINTRAN/ND500/nd-500-mon/` - the ND-100-side ND-500/5000 monitor (the other end of the MON 377B gate and the MON 60 front door).
- `SINTRAN/ND500/ND500-BUS-INTERFACE-REFERENCE.md` - the ND-100 <-> ND-500 bus interface reference.

---

**Parent:** `SINTRAN/ND500/README.md`
