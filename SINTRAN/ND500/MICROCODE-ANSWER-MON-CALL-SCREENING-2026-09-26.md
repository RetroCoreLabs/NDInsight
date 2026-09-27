# What the ND-5000 microcode does with a monitor call before SINTRAN sees it

Date: 2026-09-26. Source: the real ND-5000 control store `MICRO-5800-B30` (16384 x 128-bit words),
read as RAW WORDS, not from the rendered listing. Written to answer a question from Tor about the
ND-500 monitor calls 410-515, 45, 5, 6, 67, 74, 75, 120, 144, 313, 327: **which of those does the
CPU microcode treat specially, and what exactly does it do?**

Short answer: **six of Tor's calls are special in the microcode: 511B, 512B, 500B, 501B, 120B and
144B.** All the others on his list go to SINTRAN unchanged.

Evidence grades used here:

| Grade | Meaning |
|---|---|
| **[V]** | read from the raw 128-bit microwords, field by field, and consistent with a known second source |
| **[D]** | derived from the words by reasoning; the words are real, the meaning is my reading |
| **[M]** | from a Norsk Data manual |
| **[OPEN]** | not known; says what would settle it |

---

## 0. The corrected screening table

The table that started this (pasted from an earlier note) was **shifted by one row** in the second
half, because the microcode tests a condition ONE WORD LATE and the earlier reader did not apply that
rule to the `CALL_END` chain. Corrected, from raw words `013614`-`013631` [V]:

| MON (octal) | Name | Microcode routine | What the microcode does |
|---|---|---|---|
| 504 DVOUTS, **511 DVIO**, **512** (A5XMS / XMSG for ND-500) | | `CALL_5XX` -> `CALL_5_MATCH` (`004013`, `013667`) | copies the user's byte buffer (parameter 3, length = parameter 2, max 2048 bytes) into the ND-100 com-buffer named by message word `ABUFA` BEFORE the stop message is sent |
| 117 RFILE, **120 WFILE**, **144 MAGTP** | | `CALL_RF` / `CALL_WF` / `CALL_MT` (all `025017`) | dumps the dirty data cache to memory (`CLR_DUDC`), then the normal stop message |
| 201 (HDLC function), 270 RDPAG, 271 WDPAG, 333 UDMA, 335 | | `CALL_DUDC` (`013633`) | identical: dump dirty data cache, then normal stop message |
| **500 STARTPR** | | `CALL_STAP` (`025027`) | local start assist: may restart the target process WITHOUT the ND-100, if a gate flag is set; else normal stop message |
| **501 STOPPR** | | `CALL_STOP` (`025246`) | local stop assist: same gate; may passivate the process locally |
| 502 SWITCHP | | `CALL_SWIP` (`025264`) | local start of the target plus local stop of the caller, same gate |
| 515 (5MTRANS) | | `CALL_515` (`013641`) | answers the message at once, dumps the data cache for sub-functions 0-5 of parameter 5, does NOT restart the process |
| 600 (NDIX `fecall`) | | `CALL_NDIX` (`025401`) | asynchronous: answers the ND-100 and KEEPS EXECUTING the ND-500 program |
| everything else | | `CALL_END9` (`013635`) | the plain path: stop message, status ANSWER, interrupt, idle |

**Of Tor's list**: 511, 512 are in row 1; 120, 144 in row 2; 500, 501 in rows 4 and 5. **410, 411,
416, 417, 425, 426, 427, 505, 510, 513, 45, 5, 6, 67, 74, 75, 313, 327 are NOT screened** - they
take the plain path and everything about them is in the SINTRAN handler, not in the CPU.

Not on Tor's list but worth knowing: 504 DVOUTS shares row 1 with DVIO, and **513 is NOT in row 1**,
even though SINTRAN services 512 and 513 with the same handler body (`A5XMS`/`B5XMS` at the same
address). So 513's buffer, if it has one, is NOT pre-copied by the microcode.

---

## 1. How to read the words yourself (so the tables below can be checked)

**The file.** `MICRO-5800-B30.DATA`, 16 bytes per word, big-endian, word `N` at byte offset
`N*16`. Copies live in the RetroCore repository under the ND-5000 CPU package's `tests/MC/` folder
and in the ND5000UC repository. Bits are numbered 127 (first byte, top bit) down to 0.

**Field positions used here** (from the CPU's generated `MicroFields`, which is derived from the
microprogram guide ND-05.022.1):

| Field | Bits | Meaning |
|---|---|---|
| `ALU_TRUE` | 127-122 | ALU op + carry mode |
| `EXUC` | 115 | run the sneak cycle (second body) |
| `DATATYPE` | 100-98 | 0 = word (32), 2 = halfword (`TYP,HW`), 3 = byte (`TYP,BY`) |
| `A_OP` / `B_OP` / `DEST` | 96-89 / 88-84 / 83-76 | operand selects |
| `LC_DECR` | 70 | decrement loop counter |
| `COND_SEQ` | 69 | sequencing is conditional |
| `SEQ_TRUE` / `SEQ_FALSE` | 68-65 / 64-61 | 00 next, 03 call (jump+push), 10/11 return(+pop), 14 jump |
| `INVSEQ` | 60 | swap the true/false sequences |
| `TESTOBJ` | 58-53 | the condition: 00 `MSEXO` (always), 03 `MCNZ`, 11 `MZRO`, 13 `MSGN`, 34 `LCZ` |
| `MEMORY` | 41 + 34-32 | 0/1 `LADDR`, 0/2 `WR,POF`, 0/3 `CCD`, 1/1 `RD,POF`, 1/7 `READ` |
| `AD_ARTI` / `EA_SAVE` / `ADACT` | 40 / 39-38 / 35 | address arithmetic on, which EA register to save into (1..3 = EA1..EA3), address action |
| `ABS_ADDR` | 31-16 | jump target |
| `AA` / `AB` | 15-13 / 12-9 | address base (2 = DPA, 5 = EA1, 6 = EA2, 7 = EA3) and index (1 = MARG) |
| `SARG` | 15-0 | 16-bit constant (the MON numbers compared) |
| `MARG` | 7-0 | 8-bit signed constant used as the address displacement |

**Three rules without which every reading here comes out wrong:**

1. **A condition tests the ALU result of the PREVIOUS word.** `013615` is `XOR SC3, 117B` with a
   `MZRO` jump to `CALL_515`; that jump fires when `013614`'s `XOR SC3, 515B` was zero, i.e. when the
   MON number is 515, not 117. This is the rule the earlier table missed. It is [V]: the RetroCore
   microword CPU implements it and its trap-dispatch tests depend on it, and here every label name
   only makes sense with it (`CALL_RF` for 117 RFILE, `CALL_WF` for 120 WFILE, `CALL_MT` for 144
   MAGTP, `CALL_STAP` for 500 STARTPR, `CALL_STOP` for 501 STOPPR, `CALL_NDIX` for 600 which is
   exactly NDIX's `fecall` number).
2. **An address displacement set on word N is used by the memory access on word N+1.** So a `READ`
   on word N+1 reads at the address word N computed.
3. **`BMnn` is a bit mask with the bit number in OCTAL: `BMnn = 1 << nn(octal)`.** `BM13` = bit 11
   = 2048, `BM12` = bit 10 = 1024, `BM04` = 16, `BM06` = 64, `BM01` = 2, `BM00` = 1. Read in
   decimal these give wrong limits (8192 instead of 2048).

**The rendered listing `MICRO-5800-B30.md` mis-prints the `ORCON`/`MARG` displacement** (it
splits the overlapping immediate into separate tokens). Example: `013670` prints `ORCON=0x08`, the
raw word has `MARG = 0110B = 0x48`. Every displacement below is from the raw word.

---

## 2. The common path every monitor call takes

### 2.1 Recognition - it is a trap, not an instruction [V]

An ND-500 monitor call is compiled as `CALLG $0xF80000NN` (see
`ND500-TO-SINTRAN-MON-MAPPING.md`): segment 31, low bits = the MON number. Segment 31 is not a real
code segment, so the instruction fetch faults; the MMU status carries trap sub-code 6 and the trap
sorter `TRAP_MONC` (`012740`-`012742`) sends code 6 to `CALL_MON` (`003744`) and code 7 (a real
cross-domain call) to `CALL_DOM`.

### 2.2 `CALL_MON` builds the stop record inside the process's OWN message [V]

The microcode does not build a new message. It writes into the activation message the process was
started with (address held in `ADR_MESS`, loaded to `DPA` at `003762`-`003763`). Byte offsets are
relative to the message start; `HW n` is the SINTRAN halfword index (byte `2n`), which is how the
mailbox catalogue names the fields.

| Word | Does | Field |
|---|---|---|
| `003754` | `SC4 := LC` | argument count (the CALLG count register) |
| `003755`-`003756` | `SC3 := IAC,NPC` (low 16 bits) | the MON number |
| `003757`-`003761` | if `SC3 == 600B` call `CALL_600` first | NDIX lock path, then continue normally |
| `003764` | `16 - argc` | more than 16 arguments is an error (`BM04` = 16) |
| `003765` | if `L >= 0` -> `INS_SEQ_ERR` | L must be a valid return link |
| `003770` | `EA3 := EA1 + 0x3C` | one word BEFORE the address array |
| `003773`-`004000` loop, `LC` times | fetch operand k; `SC1 := its address`, `SC2 := its value`; `EA3 += 4`; **write `SC1` at `EA3`** (= `0x40 + 4k`, HW `40B + 2k`); **write `SC2` at `EA3 + 0x40`** (= `0x80 + 4k`, HW `100B + 2k`) | parameter ADDRESS array `5PPA1..` at HW 40B-77B, parameter VALUE array `5AP1..` at HW 100B-137B |
| `004001` | call `CALL_5XX` | the inline-copy screening, section 3 |
| `004003` | `SC13 := L` | the return address |
| `004005`-`004006` | `write P` at `+0x0E` | HW 7 = `N500A`, the saved P |
| `004007` | `write HW 1` at `+0x12` | HW 11B = `STOPR` := 1 = `MOCALL` |
| `004010` | `write HW SC4` at `+0x14` | HW 12B = `NUMPA` := argument count |
| `004011` | `write HW SC3` at `+0x16` | HW 13B = `MCNO` := MON number |
| `004012` | `P := SC13` -> `CALL_END` | so the restart resumes AFTER the CALLG |

Both arrays are written with `WR,POF` = physical write with paging off, i.e. straight into the ND-100
side message block. **The parameter VALUE is always a 32-bit word** (`003775` is a word `READ` of
the operand). A halfword parameter therefore lands in the low half of its slot.

### 2.3 `CALL_END` screens on the MON number, then `CALL_END9` answers [V]

`013613` first moves `EA1` forward by `0x40` (so inside the screened routines `EA1` points at the
address array, not the message start - matters for `CALL_NDIX`). Then `013614`-`013631` compare
`SC3` against 515, 117, 120, 144, 201, 270, 271, 333, 335, 500, 501, 502, 600 in that order (rule 1
applies: the jump on each line belongs to the compare on the line above). No match -> `CALL_END9`:

| Word | Does |
|---|---|
| `013635`-`013636` | clear `MIC,STS` bit 2 |
| `013637` | `SET_IDLE` |
| `013640` | `SC10 := 3` (`BM01 + 1`) = `N5STA` **ANSWER** |
| -> `MSG_END0` | write `N5STA := 3`, raise the ND-100 interrupt (`GIVEINT`), go idle or take the next queued message |

### 2.4 The restart, for completeness [V, from the same store]

When SINTRAN has serviced the call it sends `3MONCO` (MICFU 24B). `MSG_CONMC` (`015676`) delivers
message HW 13B (`FUNCV`) into **X1** (`015721`) and HW 11B (`KFLIP`) into the **K flag**
(`015727`/`015731`), then continues the process at the saved P. That is the mechanical basis of the
manual's "on error K is set and the error code is in W1".

---

## 3. Group 1 - 504B DVOUTS, 511B DVIO, 512B: the buffer is copied by the CPU

### 3.1 Selection [V]

```
004001  CALL_MON9   XOR HW SC3, 504B          ; call CALL_5XX (unconditional)
004013  CALL_5XX    XOR HW SC3, 504B          ; recompute (needed because of rule 1)
004014              XOR HW SC3, 511B   MZRO -> CALL_5_MATCH   ; fires when 504 matched
004015              XOR HW SC3, 512B   MZRO -> CALL_5_MATCH   ; fires when 511 matched
004016              (zero)             MZRO -> CALL_5_MATCH, else RETURN+POP   ; fires when 512 matched
```

So exactly 504, 511 and 512. Any other number returns to `004002` and nothing is copied.

### 3.2 What `CALL_5_MATCH` reads [V words, D meaning]

At this point `EA1` = message start (the `+0x40` shift of section 2.3 has not happened yet).

| Word | Access | Where | What that slot is |
|---|---|---|---|
| `013667` | `2 - argc` | | argument-count check, see 3.3 |
| `013670` | `EA2 := EA1 + 0x48` | | HW 44B = **address of parameter 3** (k = 2) |
| `013672` | word `RD,POF` at `EA2` -> `SC10`; `EA2 += 0x3C` | msg + 0x48 | `SC10` = the ADDRESS of parameter 3 = **the user's buffer address** (parameter 3 is passed by reference, so its address IS the buffer) |
| `013673` | word `RD,POF` at `EA2` -> `SC11`, also `Q := SC11` | msg + 0x84 | HW 102B = **value of parameter 2** = **the byte count** |
| `013674` | word `RD,POF` at `EA2 + 0x3C` -> `SC13` | msg + 0xC0 | HW 140B = **`ABUFA`**, the ND-100 word address of the com-buffer that SINTRAN put in the message |

Cross-check against the manual [M]: `504B DVOUTS <dev.no> <no. of bytes> <buffer>`. Parameter 2 is
the count and parameter 3 the buffer - exactly the two slots the microcode reads. **The microcode
uses the same two slots for 511 and 512**, so for DVIO and for the ND-500 XMSG call, parameter 2
must be a byte count and parameter 3 the buffer, whatever the rest of their parameter lists are.
That is a hard constraint on Tor's open question about DVIO's parameters: the first three are
`<dev.no> <no. of bytes> <buffer>` in the DVOUTS order, because the CPU itself assumes it.

### 3.3 The two checks [V words, D direction]

| Word | Test | Meaning | On failure |
|---|---|---|---|
| `013667` + `013670` (`MSGN`) | `2 - argc < 0` | **at least 3 arguments** | `MISEQERR` |
| `013675` + `013676` (`MCNZ`, inverted) | `count - BM13` where `BM13` = 2048 | **count must not exceed 2048 bytes (4000B)** | `MISEQERR` |

`MISEQERR` (`004017`) loads **X1 := 1003B**, sets **K**, and RETURNS - to `004002`, so **the stop
message is still built and sent** with the header fields of section 2.2. What SINTRAN then does with
a call whose buffer was not copied is not traced here [OPEN]; note that SINTRAN's own DVIO handler
independently rejects `DNOBY > 4000B` with error 174 (see the SINTRAN carve of 511B), so the two
limits agree.

### 3.4 The copy [V words]

```
013702  DPA := SC13 + SC13            ; ABUFA is an ND-100 WORD address -> byte address
013703  DPA := SC10 ; Q := Q >> 1     ; source = user buffer
        EA2 := (ABUFA*2) - 4          ; destination pointer, pre-decremented
013704  Q := Q >> 1                   ; Q = count / 4 = number of whole words
013705  LC := Q
013706  EA3 := SC10 - 4               ; source pointer, pre-decremented
CALL_5_W  (013707)  while LC != 0:  EA3 += 4 ; SC12 := READ word [EA3] ; EA2 += 4 ; WR,POF word [EA2] := SC12
013710  LC := count & 3               ; the odd bytes
013711  EA3 += 3 ; 013712  EA2 += 3   ; step both pointers to the last full word's end - 1
CALL_5_B  (013713)  while LC != 0:  EA3 += 1 ; SC12 := READ byte [EA3] ; EA2 += 1 ; WR,POF byte [EA2] := SC12
        RETURN+POP when LC == 0
```

- Source reads are **`READ`** = virtual, through the MMS, in the user's data space. Page faults can
  happen here like in any instruction.
- Destination writes are **`WR,POF`** = physical, paging off: the ND-100 com-buffer at `ABUFA*2`.
- Word copy first, then 0-3 bytes. Byte count exact; no padding, no terminator.

### 3.5 What the SINTRAN side does with it (from the L07 carve, for context)

Message word `MIFLAG` has a bit `WSMC` = "data buffer is in com-buffer (by mic.prog)". SINTRAN sets
that bit when it knows the CPU generation pre-copies; the DVIO/NOUTSTR handler at `141056`-`141105`
(segment `026-S3IMPIT`) tests it, and only when it is CLEAR does it build a `read-data-memory`
micro-function to fetch the bytes itself. The microcode does **not** write `MIFLAG`; SINTRAN decides
from the CPU type. So on an ND-5000 the ND-100 never fetches these buffers a second time - that is
the whole point of the screening.

### 3.6 Practical consequences for 511B and 512B

- **Parameter 2 = byte count (max 4000B), parameter 3 = buffer, at least 3 parameters.** True for all
  three calls, enforced by the CPU.
- **The buffer contents SINTRAN sees are a COPY taken at call time.** Anything the handler reads
  comes from the com-buffer at `ABUFA`, never from ND-500 memory. For DVIO's INPUT phase (the bytes
  coming back) this copy path is one-way; the return data must come by another route (SINTRAN's
  terminal driver writing into ND-500 memory, or the restart's write-back). That is consistent with
  the SINTRAN 511B carve, which shows a separate input phase.
- **512B and 513B differ here.** Same SINTRAN handler, but only 512B is pre-copied. 513B (called
  with 1 to 6 parameters, per Tor) gets no copy, so its parameters must be values or addresses the
  ND-100 reads itself.

---

## 4. Group 2 - 117, 120, 144, 201, 270, 271, 333, 335: dump the data cache first

### 4.1 The routine [V]

`CALL_RF`, `CALL_WF`, `CALL_MT` are three names for ONE address, `025017`; `CALL_DUDC` at `013633`
is the same two words. Both are: **call `CLR_DUDC`, then go to `CALL_END9`**. So there is no "wait
variant"; the earlier table's label was a guess from the letters `WF`. The letters are RFILE / WFILE
/ MagTape.

`CLR_DUDC` (`015130`):

```
015130  LC := BM12 - 1  = 1023          ; 1024 iterations
015131  SC14 := BM06    = 64            ; modus register bit 6
015132  AND SPEC,MOD, SC14
015133  if zero -> return                ; cache mode does not need it: do nothing
CLR_DUDC1 (015134)  loop 1024 times:  EA0 += 4 ; memory op CCD
```

`CCD` is memory op 3 = **"CLEAR CACHE AND DUMP DIRTY"** [M, ND-05.022.1 mnemonic 517]. Modus bit 6
is **`EWICO` = "enable write cache once mechanism"** [M, ND-05.020.01 modus register table]. The
hardware description says the used/dirty map is "1K by 16 bits ... it is sufficient to count to 1024
once in order to clear the cache" - exactly the loop count.

### 4.2 Why [D]

In write-once mode the ND-5000 data cache holds written data that memory does not yet have. Every
call in this group moves data between the user's buffer and a device by the ND-100 or DMA, which
reads and writes MEMORY, not the cache. So before the ND-100 is told to act, the microcode writes
every dirty line back and invalidates the cache. That protects both directions: an output call would
otherwise send stale memory; an input call would otherwise have its fresh data overwritten later by
a dirty line write-back.

### 4.3 Consequences for Tor's 120B WFILE and 144B MAGTP

Nothing about the CALL's semantics changes. Parameters, the seek-by-zero-length trick with WFILE,
and every MAGTP sub-function are entirely SINTRAN's business. The only thing the microcode adds is
the cache flush, which is invisible to the program. If an emulator has no data cache, the correct
model of this group is "do nothing special".

Members not on Tor's list, named from the L07 monitor table: 117 RFILE, 201 `XTLX` (HDLC function),
270 `RDPAG`, 271 `WDPAG`, 333 `UDMA` (DMA function), 335 (`DOPEN` in `030-S3SM5` per the table; its
role as a data-moving call is [OPEN]).

---

## 5. Group 3 - 500 STARTPR, 501 STOPPR, 502 SWITCHP: local process assists

This group is the least finished. What is [V] is the structure; the exact field meanings are [D].

### 5.1 The gate: `X5SIBCALL` (`025021`) [V words]

```
025021  SC13 := START_MESS (= 20000B, the patched system-block base)
025022  DPA := SC13
025023  SC13 := 1
025024  AND HW [DPA + 4], SC13
025025  if zero -> CALL_END9            ; assist NOT enabled: plain monitor call to SINTRAN
025026  DPA := EA3                       ; else continue into the assist
```

So all three calls first look at **bit 0 of the halfword at system block + 4**. If it is clear, the
call is an ordinary monitor call and SINTRAN does the work. If it is set, the microcode tries to do
it locally. Who sets that bit and when is [OPEN] (it is in the `START_MESS` area, which the ND-100
patches into the control store at boot; a SINTRAN generation for the 5800 presumably sets it).

### 5.2 STARTPR locally (`CALL_STAP` -> `START_P_0` -> `CALL_STA_*`) [D]

`START_P_0` (`025321`) takes parameter 1 (`SC2` = `<proc.no>`, "process index in the upper half,
cycle number in the lower half" [M]), masks the index (`AND 0x00FF0000`, shifts right 8) and adds
`index * 256` to the execution-queue base from `ADR_EXQUE`: **each ND-500 process has a 256-byte
block**, and the microcode addresses the TARGET's block directly. `START_P_1`/`_2` read the target's
message flag word (`5MSFL`, at block - 4) and status halfwords and decide between:

- **`CALL_STA_OWN`** (`025041`): `UNLOCK_QUE`, `SET_RUNNING`, **X1 := 0, K := 0**, `GET_NEXT`.
  The caller continues with its next instruction. The ND-100 is never involved.
- **`BOK_MCALL`** (`025351`): writes into the target's message: `N5STA := 1`, `MICFU := 24B`
  (`3MONCO`, restart after monitor call), `N500A := 0`, `STOPR := 0`, `NUMPA := 0`,
  `FUNCV := SC3` (0 or 4). That is a **synthesised restart message for a process that is sitting
  in STOPPR**, queued for the microcode itself to pick up. This is how "start a stopped process"
  is done without SINTRAN.
- **`CALL_STA_REP`** (`025036`): ORs bit 15 (`BM17`) into the target's flag word = **set the
  repeat flag** ("if the process is already active, its repeat flag will be set" [M]).
- **`CALL_STA_CPU`** / `SENKICK` (`025131`, `025142`): the target belongs to another CPU:
  compute its per-CPU area and send an octobus kick (`ACCP_WRITE` with `100102B`).

### 5.3 STOPPR locally (`CALL_STOP` -> `STOP_P_0` -> `CALL_STO_*`) [D]

`STOP_P_0` reads the caller's own flag word (message - 4). `CALL_STO_0` tests bit 15 (the repeat
flag):

- set -> `CALL_STO_1`: clear it, `UNLOCK_QUE`, `SET_RUNNING`, **X1 := 0, K := 0**, `GET_NEXT`: the
  process does NOT stop ("if the repeat flag is set when STOPPR is executed, the process is
  immediately reactivated" [M]) - and SINTRAN never hears about it.
- clear -> `CALL_STO_2`: write halfword `13B` at message + 4 (`N5STA`), `SET_IDLE`, `MSG_CCMOVE`,
  `MSG_END_1`: the process is parked and the microcode moves on to the next queued message. No stop
  record is written (no `STOPR := MOCALL`). The value `13B` in the status slot is not one of the
  documented 0-4 codes [OPEN].

### 5.4 SWITCHP (`CALL_SWIP`) [D]

Same gate, then `START_P_0` on the target followed by the stop logic on the caller
(`CALL_SWI_0..5` mirror `CALL_STA_*` and `CALL_STO_*`), as the manual describes ("a combination
of STARTPR and STOPPR").

### 5.5 Consequences for Tor's 500B and 501B

- With the gate CLEAR (or on a classic ND-500, whose microcode has no such assist), these are plain
  monitor calls; the SINTRAN handlers `STAPR` (`140356B`) and `NSTOP` (`140511B`) in the L07 carve
  are the whole story.
- With the gate SET, **SINTRAN may never see a STARTPR or STOPPR at all.** An emulator that only
  models the SINTRAN side will still be correct in behaviour (the process starts/stops), but any
  trace-comparison against a real ND-5000 will show fewer MON stops than expected.
- **Return convention holds either way:** success is X1 = 0 and K clear; the local paths set exactly
  that.

---

## 6. The two remaining special numbers

### 6.1 515B (Tor: 5MTRANS, "async disk transfer, check event, start process") [D]

`CALL_515` (`013641`): `SET_IDLE`; `MSG_CCMOVE`; then in the caller's own message **write `N5STA :=
3` (ANSWER) immediately** (`013645`-`013646`); read **parameter 1's value** (HW 100B) and test its
bit 0; read **parameter 5's value** (HW 110B), mask its low 3 bits into `MIC,VECT` and jump through
an 8-entry table (`013655`-`013664`): sub-functions **0-5 -> `CALL_515D` = dump the data cache**,
then `MSG_QUEUE_END`; **6, 7 -> `MSG_QUEUE_END`** directly. If parameter 1's bit 0 is clear, straight
to `MSG_QUEUE_END`.

So: the message is answered at once and the microcode goes to the next queued message. The process
is NOT restarted here; it stays stopped until the ND-100 sends the restart. The cache dump exists for
the same reason as group 2 (a transfer is about to touch the buffer). Which sub-function numbers mean
what is SINTRAN's business (L07 handler `515B-MultipleDataTransfer` in the carve tree).

### 6.2 600B (NDIX `fecall`, not a SINTRAN call) [V flow]

Handled twice: `CALL_600` at entry (lock), and `CALL_NDIX` at the end: if the value of parameter 2
is non-zero and the system-block halfword at `20000B + 4` is non-zero, write halfword 3 at message
+ 0x104, `GIVEINT`, `UNLOCK_QUE`, **and `EXECUTE`: the ND-500 program keeps running** while the ND-100
services the request. This is the only asynchronous monitor call in the store. Irrelevant to SINTRAN
programs; listed so nobody mistakes 502 or 600 for each other again.

---

## 7. Open items - SETTLED later the same day (2026-09-26)

| Item | Result | How |
|---|---|---|
| `CALL_5_MATCH` count boundary | **2048 accepted, 2049 refused** (X1 := `1003B`, K := 1, nothing copied). 2047 and 2048 copy byte-exact and contiguous. 504/511/512 copy; **513 does not**. argc = 2 refused. | **measured**: RetroCore `Nuget/HackerCorpLabs.Emulation.CPU.ND5000/tests/MonCallInlineCopyTests.cs`, 8 cases green, real B30 store executed from `CALL_5XX` (`004013`) to the RETURN |
| Destination address of the copy | **`0xFFF00000 + 2 * ABUFA`**. `ZERO_P` (`000027`) is `SC13 := SC13 - 0o2000000` (= 0x80000) before the doubling at `013702`, so the ND-100 word address lands in the **top megabyte of the ND-5000 physical space = the ND-100 memory window** (512K ND-100 words). The first test run threw out-of-bounds exactly there; the test now models the window. [V raw word + measured] | raw word `000027`: `ALU,B-A CRY,ONE A,LARG LARG=00002000000 B,SC13 D,SC13` |
| The start/stop assist gate (`X5SIBCALL`, `START_MESS + 4` bit 0) | `START_MESS` = the `X500DF` CPU datafield; `+4` = **X500DF word 2** (L07 symbol at offset 2: `X5LOG`, unreferenced in the NPL revision we have; `X5NAC` is the exec-queue "number active", a different struct). `XMSINIT` (`RP-P2-N500.NPL:131140-131152`) zeroes the whole `5NPMAILBOX` area and nothing in `RP-P2-N500`/`MP-P2-N500` writes offset 2 afterwards -> **the gate is CLOSED on SINTRAN L07; 500/501/502 are plain monitor calls**. The routine names (`X5SIBCALL`) say ND built the path for SIBAS servers (506B `5SIBMO` = SIBSURV); dormant here. [V-NPL, different revision] | NPL grep + symbol tables |
| `N5STA := 13B` from the local STOPPR | **`13B` = `STOPPED`** (`STOPP=000013` in `N500-SYMBOLS`). SINTRAN's own `NSTOPROC` (`MP-P2-N500.NPL:140316-140333`) does exactly the microcode's two branches: "REP bit set? clear it and `OKMONICO` restart, else `STOPPED; CALL WN5STATUS`". The local path is a 1:1 copy of the SINTRAN handler. [V symbol + NPL] | symbol table + NPL |
| 335B | **EXABS "TransferData - data to and from mass storage"** (ND-860228-2). The MON index's `DOPEN=110066` is a 5-char symbol collision, not the call's identity. A data-moving call, so the cache-dump group is the right place for it. [M] | manual |
| Classic ND-500 (CONT-STORE-10611) | Has the **same 504/511/512 selection** (`010511` XOR 504 -> JSR `010657`; `010657`/`010660` XOR 511/512) and the **same `4000B` limit** (`010717`: `A-B-1 CRY,ONE A,SARG 004000 B,AM#34 COND,MSGN`). Refusal loads **X1 := `174`** with K (`010741`: `SARG=000174 D,X#0 K,ONE`) - the classic uses SINTRAN's own error code, the 5000 uses `1003B`. **No** compares against 117/120/144/201/270/271/333/335/500/501/502/515/600 as post-call screens (the few `SARG=000120`/`000270`/`000201` hits are constants inside other routines, e.g. `012005`, `011712`, `007541`); no cache dump (the classic cache is write-through per ND-05.020.01 3.2.5); no local start/stop; no 515 fast answer. [V static read; the classic compare direction was not executed] | classic listing `CONT-STORE-10611.md` |

Still [D]: the field tests inside the ND-5000 local STARTPR (`START_P_1`/`START_P_2`); irrelevant
while the gate is closed. Still not executed: the classic store's boundary direction.

---

## 8. Files this supersedes or corrects

- The screening table in the earlier note `MAILBOX-MICROCODE-PSEUDOCODE.md` (section "CALL_END",
  a D: drive snapshot) is **off by one row from 117 onward** and says `500 -> CALL_DUDC`,
  `501 -> CALL_STAP`, `502 -> CALL_STOP`, `600 -> CALL_SWIP`. Correct: `500 -> CALL_STAP`,
  `501 -> CALL_STOP`, `502 -> CALL_SWIP`, `600 -> CALL_NDIX`, and `117/120/144 -> 025017`
  (cache dump, not a wait variant). Its `CALL_MON` decode (parameter arrays, header offsets) is
  confirmed here.
- The "max 0o4000 bytes" for the inline buffer, marked [X] there, is now [V]: `BM13` = 2048.
- The reading "`013670` `ORCON=0x08`" from the rendered listing is wrong; the raw displacement is
  `0x48` (HW 44B, address of parameter 3).

Related: `ND500-MAILBOX-MESSAGE-CATALOG.md` (field names and offsets used above),
`ND500-TO-SINTRAN-MON-MAPPING.md` (the seg-31 gate), the per-call SINTRAN carves under
`tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/` (`504B-OutputString`,
`511B-DVIO`, `512B-XMSGCallA`, `500B-StartProcess`, `501B-StopProcess`, `515B-MultipleDataTransfer`,
`120B-WriteToFile`, `144B-DeviceFunction`).
