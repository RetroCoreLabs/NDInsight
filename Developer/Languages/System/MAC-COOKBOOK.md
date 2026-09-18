# MAC Cookbook — what actually assembles and runs

**A practitioner's companion to the [MAC Assembler Developer Guide](MAC-DEVELOPER-GUIDE.md).**

Where the developer guide describes the NORD-10/100 MAC *language*, this
cookbook records what we **empirically verified** while writing and
running real MAC programs through the **`@MAC` interactive/reentrant
subsystem** ([ND-60.096](<../../../Reference-Manuals/ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide.md>))
on **SINTRAN III VSX/500 L**, assembled with `)9ASSM` and linked with NRL,
running under the `nd100x` emulator. It is the "what bit us / what works"
layer: the exact source encoding, the addressing-mode deref ladder, the
monitor-call calling convention, and a catalogue of the specific errors we
hit and how we fixed them.

> **Scope note.** Everything here is verified against the *reentrant* `@MAC`
> subsystem driven from a running SINTRAN III. Some forms shown in the
> sibling developer guide (e.g. `=N` immediates, `)ENTR`, `MONITOR n`) did
> **not** assemble in this path; see [§9 Differences we observed](#9-differences-we-observed-from-the-general-reference).
> Treat the two docs as complementary: language reference vs. verified
> SINTRAN workflow.

---

## 0. TL;DR — the five things that must be right

A MAC source file fed to `@MAC` will only assemble if **all five** of these
hold. Get one wrong and you get a misleading cascade of `ILL. CHARACTER` →
`I/O-ERROR` → `NO SUCH PAGE`, all reported at the location counter, not the
offending source line.

| # | Property | Value | Why |
|---|----------|-------|-----|
| 1 | File type | `:SYMB` | MAC's documented source extension; matches its defaults. |
| 2 | Line ending | **CR only** (`\r`), no LF | A bare LF (`0x0A`) trips `ILL. CHARACTER`. |
| 3 | Parity | **even parity on every byte** | `)9PARI` defaults ON; 7-bit-clean fails. |
| 4 | EOF | **no `\x17`/ETB byte** | ETB (`027`) is rejected as `ILL. CHARACTER` despite the manual. |
| 5 | Terminator | `)LINE` on its own last line | Switches MAC back to terminal input — the proper end. |

Plus three language facts that cause the most lost time:

- **Numbers are OCTAL by default.** `1361` means `1361₈` (= 753 decimal).
- **Labels are significant to 5 characters.** Longer labels collide silently.
- **Monitor calls skip-on-success** (return to PC+2 on success, PC+1 on
  error) — your control flow must be built around that. See [§6](#6-monitor-calls-mon-n).

---

## 1. The build pipeline (host → SINTRAN → run)

```
your .SYMB source
   │  (even parity, CR-only, no ETB)
   ▼
@MAC  )9ASSM name:SYMB,0,"name:BRF"   →  name:BRF   (relocatable object)
   │
   ▼
@NRL  PROG-FILE "name" / LOAD name / EXIT   →  name:PROG  (executable)
   │
   ▼
@name      ← run it
```

Interactive transcript that works:

```
@MAC
)9ASSM HELLO:SYMB,0,"HELLO:BRF"     % list=0 → no listing; "..:BRF" creates the file
)9EXIT
@NRL
PROG-FILE "HELLO"
LOAD HELLO
EXIT
@HELLO                               % run
```

Notes:
- `list` arg: `0` = null device (silent). Use `TERM` while debugging — MAC
  then echoes each source line *before* its error, which is the only
  reliable way to localise a source-level mistake.
- A **double-quoted** `"name:BRF"` opens-with-create; an unquoted name only
  opens an existing file.
- After `)9EXIT`, link with NRL ([ND Relocating Loader](<../../../Reference-Manuals/ND-60.066.04 ND Relocating Loader.md>)).
- This whole sequence automates cleanly over a telnet connection to
  SINTRAN; we drive it from Python (boot `nd100x`, log in, stage the
  even-parity source into the disk image, then send the lines above).

---

## 2. Your first program

```mac
        )9BEG START      % declare START as the entry point
START,  MON 0            % MON 0 = ExitFromProgram
        )9END            % close the BRF program unit
        )LINE            % terminate source / back to terminal
```

That assembles to a one-word `:BRF` that NRL turns into a `:PROG` which
exits cleanly. Four facts already in play:

- `)9BEG <label>` declares the entry point. **Not** `)ENTR` (which errors
  `WHAT? ENTR` in this subsystem).
- `)9END` closes the program unit; required before `)LINE`.
- `MON 0` is the clean exit.
- Labels end with a comma: `START,`.

## 3. Printing a value (and the marker trick)

`MON 35` (OutNumber) prints the **A** register as a number; **T** selects
the base: `SAT 10` → octal output, `SAT 12` → decimal output (10₈ and 12₈
= 8 and 10 decimal — even the *format codes* are octal).

```mac
        )9BEG START
START,  SAT  10          % T = 8 → octal output format
        SAA  5           % A = 5
        MON  35          % prints "5" — MON 35 does NOT skip-on-success
        SAT  10
        SAA  6
        MON  35          % prints "6"
        MON  0
        )9END
        )LINE
```

`MON 35` is the workhorse for **debugging by marker**: drop
`SAT 1; SAA <char>; MON 2` (or `MON 35`) at known points so the terminal
tells you exactly which code paths executed and in what order. This single
technique found most of the bugs in [§8](#8-gotcha-catalogue). (`MON 2`
prints one character — the low byte of A — and *is* privileged; in a
non-RT user program output still appears but a deferred
`PRIVILEGED INSTRUCTION` error is logged. For pure diagnostics either is
fine; for real text output `MON 35`/`MON 162` are safer.)

---

## 4. Numbers, labels, and reserved words

### Numbers are octal
`SAA 62` loads `62₈` = 50 decimal (ASCII `'2'`). To emit an ASCII marker
you must convert: ASCII `'2'`..`'9'` = `62₈`..`71₈`, then `':'` = `72₈`,
`';'` = `73₈`. Decimal `68` is **not** a valid octal literal — digits `8`
and `9` in an "octal" context silently misassemble. When generating MAC
from a script, always `format(n, 'o')`.

### Labels: 5 significant characters
`RDEVNO`, `HDEVNO`, `LDEVNO` all collapse to `DEVNO` and trigger
`ALREADY DEFINED`. Keep labels unique within their first 5 characters.

### Reserved mnemonics collide with labels
Instruction and monitor names are reserved; using one as a label fails:

| Wanted label | Collides with | Symptom | Use instead |
|--------------|---------------|---------|-------------|
| `COPY` | the `COPY` register-transfer instruction | label silently shadows / `ILL` | `CPYIT` |
| `WRITE` | reserved mnemonic | `ILL.MNEMONIC` | `WRT` |
| `CLOSE` | `CLOSE` monitor name | `ALREADY DEFINED CLOSE` | `CLOSEF` |

This bites hardest with **dead code**: an unreferenced label like `ECLOSE`
still gets defined and still collides. Delete dead labels, don't just stop
jumping to them.

### Immediates are small and signed
`SAA n` / `SAT n` take an **8-bit signed** immediate (±127). For anything
larger, put it in a data word and load it:

```mac
        LDA  LDNUM        % load a constant > 127 from memory
        ...
LDNUM,  1361              % 1361 octal lives here
```

`=N` and `(N` prefixes on `LDA` (as the general guide shows) **error** in
this subsystem (`ILL. USE OF COMMAND` / `ILL. CHARACTER`); use a labelled
data word or the literal-pool form in [§5](#5-addressing--the-deref-ladder).

---

## 5. Addressing & the deref ladder

This is the single biggest source of subtle bugs. The `(LABEL` literal-pool
form and the `I` indirect flag compose into a "ladder" of dereferences:

| Form | Meaning | A ends up holding |
|------|---------|-------------------|
| `LDA (LABEL` | load the **address** of LABEL (from the literal pool) | `&LABEL` |
| `LDA I (LABEL` | load the **contents** of LABEL | `*(&LABEL)` = `LABEL`'s value |
| `LDA LABEL` | P-relative direct load | `LABEL`'s value (if in ±range) |
| `STA I (LABEL` | store A **into** LABEL (via the pool address) | `LABEL := A` |
| `LDA ,X` | load via the **X register** as an absolute pointer | `*X` |
| `STA ,B` | store via the **B register** as an absolute pointer | `*B := A` |

**The classic mistake:** `LDA (PARR` where you meant `LDA I (PARR`. The
first loads the *address* of the parameter list; the second loads the
*value*. One missing `I` and every dereference is off by one level.
Likewise, **by-reference parameter-list slots hold ADDRESSES, not values** —
a slot you "set" must be the address of the cell, and the monitor reads
through it.

### P-relative range is ±128 words — and the literal pool must be flushed
P-relative operands (including `JMP LABEL` and `(LABEL` literal refs) reach
only ±128 words. Two consequences:

1. **Jumps that escape range** silently wrap or mis-target. If a `JMP` to a
   far label misbehaves at runtime (but assembled fine), suspect range.
   Restructure so the target is near, or bounce through a nearby trampoline.
2. **The literal pool needs periodic flushing.** Every `(LABEL` you use is
   stored in a literal pool that must be emitted within reach. After the
   last instruction you must add `)FILL`, or you get `)FILL MISSING`. For
   long routines with many forward `(LABEL` references (more than ~8), you
   must flush **mid-program** too, or MAC emits range errors
   (`ERROR 5/14/17/26/31`) — and crucially the `:BRF` may still *build* but
   then **fault at runtime**. The pattern:

```mac
        ... code using many (LABEL refs ...
        JMP  MID          % skip over the pool we are about to dump
        )FILL             % flush the literal pool here
MID,    ... more code ...
```

### Walking memory with X/B
The register-pointer forms (`LDA ,X` / `STA ,B`) are **absolute** — no
±128 limit — which is how you copy buffers larger than P-relative reach.
Increment a pointer register with `COPY`:

```mac
        LDA  (SRC         % X = &SRC
        COPY SA DX        %   (A → X)
        LDA  (DST
        COPY SA DB        % B = &DST
        LDA  (71          % counter = 57 decimal (71 octal)
        STA  I (CNT
LOOP,   LDA  ,X           % A = *X
        STA  ,B           % *B = A
        COPY AD1 SX DX    % X++  (add-1, source X, dest X)
        COPY AD1 SB DB    % B++
        LDA  I (CNT
        SUB  (1
        STA  I (CNT
        JAZ  DONE         % JAZ = jump if A zero
        JMP  LOOP
DONE,   ...
```

`COPY AD1 S<reg> D<reg>` is the idiomatic register increment; `COPY SA DX`
moves A→X, `COPY SX DA` moves X→A, etc.

---

## 6. Monitor calls (`MON n`)

The SINTRAN monitor-call ABI, as we exercised it (see also
[ND MON Calls](<../../MON/ND MON Calls.md>) and
[ND-860228 SINTRAN III Monitor Calls](<../../../Reference-Manuals/ND-860228-2-EN SINTRAN III Monitor Calls.md>)):

- **Most calls take a parameter list by reference.** Load the *address* of
  the param list into A (`LDA (PARM`), then `MON n`. Each slot in the list
  is itself usually an **address** of the actual argument cell.
- **Skip-on-success.** On success the monitor returns to **PC+2** (it skips
  the next word); on error it returns to **PC+1**. So the instruction
  immediately after `MON n` is the **error path**, and the one after that
  is the **success path**. The idiom is a single jump as the "skip slot":

```mac
        LDA  (PARM
        MON  50           % OpenFile
        JMP  EOPEN        % ← executed ONLY on error (PC+1)
        STA  FILNO        % ← success continues here (PC+2)
```

  For an unconditional continue after success, use the **convergent jump**:
  put `JMP TARGET` twice, so both the success-skip and the explicit jump
  land on `TARGET`.

  **Exception:** some simple-return monitors do **not** skip — notably
  `MON 35`, which just falls through. Don't leave a skip slot after those.

- **Error codes print in octal.** A returned `-10B` is `-8` decimal
  ("Illegal function"). Read monitor errors as octal.
- **`MON 35` is special:** it uses the **T and A registers directly** (T =
  format, A = number), *not* a parameter list.
- Test A with `JAZ` (jump if A = 0), `JAF` (jump if A **non-zero**), `JAP`
  (A ≥ 0), `JAN` (A < 0). *(JAF = "jump if A Filled" = non-zero — per
  ND-60.096 §2.3; a common error-check idiom since a 0/negative return makes
  JAF branch exactly on the non-zero error.)*

### Monitors we used (verified)

| MON | Name | Args | Notes |
|-----|------|------|-------|
| `0` | ExitFromProgram | — | clean exit; last instruction |
| `1` | InByte (sequential read) | param list | capped ~456 bytes by an internal buffer — see below |
| `2` | OutByte | A = byte | privileged; works for diagnostics, logs deferred error in user mode |
| `35` | OutNumber | T=format, A=number | no skip; T=`10`→octal, `12`→decimal |
| `43` | CloseFile | T = file number | |
| `50` | OpenFile | X=&name, A=&type, T=access | access 1=seq read, 2=random R/W, 3=random read-only |
| `74` | SetStartByte | param list | position within an open file |
| `117` | ReadFromFile (random/block) | param list | **bypasses the MON 1 ~456-byte cap**; reads whole blocks; count is in **words** |
| `122` | Reserve device | param list | reserve a logical device (e.g. an HDLC LDN) before use |
| `201` | HDLCfunction | param list | full HDLC send/receive/init; heavily used — see the HDLC docs |

The **MON 1 vs MON 117** distinction matters: sequential `MON 1` is limited
by an internal ~456-byte buffer (tied to `CHANGE-BUFFER-SIZE`), so to read a
larger file in one shot, open with access=3 and use `MON 117` with a word
count. (`RFCNT` is a *word* count: `1000₈` = 512 words = 1024 bytes.)

---

## 7. File system access from MAC (reading files to serve them)

This is the file-I/O surface we used to read HTML/GIF files off the SINTRAN
disk and serve them — the recipe for any MAC program that reads stored
files. All of it is plain SINTRAN monitor calls; nothing HDLC-specific.

### The calls and their registers

| MON | Name | Inputs | Returns |
|-----|------|--------|---------|
| `50` | OpenFile | `X = &name`, `A = &type`, `T = access code` | `A = file number` (save it) |
| `1` | InByte (sequential) | param list / open file | next byte; **capped ~456 bytes per buffer** |
| `117` | ReadFromFile (random/block) | param list (see below) | reads N **words** into a buffer; **no 456-byte cap** |
| `74` | SetStartByte | param list | repositions the file pointer for sequential I/O |
| `43` | CloseFile | `T = file number` | — |

### Access codes (the `T` value passed to MON 50)

| Access | Meaning | Notes |
|--------|---------|-------|
| `1` | sequential read | works with `MON 1`; subject to the ~456-byte buffer |
| `2` | random read/write | |
| `3` | random read-only | **required for `MON 117`** block reads |

A filename/type is a packed character literal: `FILNA, 'INDEX'` and
`FILTY, 'HTML'`. Names are significant to the usual SINTRAN limits — keep
them short (we hit failures with 6-char names where 5 worked).

### Why MON 117, not MON 1 — the 456-byte wall

**[VERIFIED]** Sequential `MON 1` reads through an internal buffer that caps
a single read at roughly **456 bytes** (tied to `CHANGE-BUFFER-SIZE`). For
anything larger — a full HTML page, a GIF — that wall forces awkward
chunking. **`MON 117` reads whole blocks directly and has no such cap**, so
it is the right call for "load a file into memory in one shot." Two details:

- Open with **access = 3** (random read-only); `MON 117` requires it.
- `RFCNT` is a **word** count, not bytes: `1000₈` = 512 words = 1024 bytes.

### The recipe: open → block-read → close

```mac
LOAD,   SAT  3                  % access = 3 (random, read-only) — required for MON 117
        LDX  (FILNA             % X = &filename
        LDA  (FILTY             % A = &filetype
        MON  50                 % OpenFile
        JMP  EOPEN              % error path (PC+1)
        STA  FILNO              % success: save returned file number
        LDA  (RFPAR             % A = &MON-117 parameter list
        MON  117                % ReadFromFile (block)
        JAF  EREAD              % JAF = jump if A non-zero (MON 117 left a non-zero error) → read error
        LDT  FILNO
        MON  43                 % CloseFile (T = file number)
        JMP  ECLOSE             % error path
        ...                     % success: file now in FILEBUF

% MON 117 parameter list — each slot is an ADDRESS (by reference),
% except the buffer slot which IS the buffer's address.
RFPAR,  FILNO; RFWAIT; FILEBUF; RFBLK; RFCNT
RFWAIT, 0                       % 0 = wait until complete
RFBLK,  0                       % start block (0 = beginning)
RFCNT,  1000                    % 1000 octal = 512 words = 1024 bytes
FILNA,  'INDEX'
FILTY,  'HTML'
FILNO,  0
FILEBUF, 0; 0; 0 ...            % buffer, sized to the read (in words)
```

### Bytes inside words (matters for binary files)

`MON 117` packs file bytes into 16-bit words **high byte first**: file byte
0 is the high byte of word 0, byte 1 the low byte, and so on. When you later
emit those words (e.g. over HDLC) high-byte-then-low-byte, the on-wire byte
stream matches the original file order — so **binary files (GIF, etc.)
round-trip intact** with no special handling. Just don't byte-swap.

### Serving several files

To serve more than one file, repeat **open → MON 117 → close** per file into
**separate buffer regions** (one slot per file), then keep the buffers
resident. Each `MON 117` reuses the same parameter-list shape with a
different name/type and a different buffer address. Memory is the limit:
on a 2 MB ND-110 you cannot cache an unbounded set, so a large site wants a
rotation that reads one file at a time from disk rather than caching all of
them at once.

> Complete, runnable versions live in the project's `mac-programs/` set
> (`hfile-mon117.mac` for the block read; the HDLC server programs combine
> this with transmit). For the file-serving-over-HDLC application — buffer
> pool setup, the receive-arm trap, running under nd100x — see
> **[HDLC Buffer-Pool and Emulator Usage](../../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md)**.

---

## 8. Gotcha catalogue

Every entry here cost real debugging time. Symptom → cause → fix.

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ILL. CHARACTER` cascade, points at location counter not source | LF in line endings, or an ETB (`\x17`) EOF byte, or odd parity | CR-only, even parity, no ETB; end with `)LINE` |
| `)FILL MISSING` | used `(LABEL` literals but never flushed the pool | add `)FILL` after the last instruction |
| `ERROR 5/14/17/26/31`, or builds but **faults at runtime** | literal pool / P-relative reference out of ±128 range | flush the pool mid-program (`JMP MID; )FILL; MID,`); keep jumps near |
| `ALREADY DEFINED <X>` | two labels share their first 5 chars, **or** a label equals a reserved mnemonic/monitor name (incl. dead code) | rename to a unique ≤5-char non-reserved label; delete dead labels |
| `WHAT? ENTR` | used `)ENTR` for the entry point | use `)9BEG <label>` |
| `ILL. USE OF COMMAND` / `ILL. CHARACTER` on a load | used `=N` or `(N` immediate forms | use `SAA`/`SAT` (±127) or a labelled data word |
| value wrong by a factor / nonsense address | forgot the `I` — `LDA (X)` (address) vs `LDA I (X)` (value) | add the `I` for the value; one deref level per `I` |
| marker bytes print as wrong glyphs (`8`, `9`, `!`) | decimal literal where MAC expects octal | emit octal (`format(n,'o')`); remember default base is octal |
| program runs the error path even though the call worked | mis-applied skip-on-success (or left a skip slot after `MON 35`) | error path is PC+1, success PC+2; `MON 35` does not skip |
| reading a file truncates near ~456 bytes | `MON 1` sequential read hits the internal buffer cap | open access=3 and use `MON 117` (word count) |
| `STA I (CELL)` seems to corrupt a nearby variable | wrote past a buffer because the counter/loop ran one extra iteration | re-check the `JAZ`/decrement order; the test is *before* the next write |

---

## 9. Differences we observed from the general reference

The sibling [MAC-DEVELOPER-GUIDE.md](MAC-DEVELOPER-GUIDE.md) documents the
broad NORD-10/100 MAC language. In the **reentrant `@MAC` subsystem on
SINTRAN III VSX/500 L** we drive, these specific forms behaved differently —
recorded here so the two docs don't quietly contradict each other:

| General guide shows | In `@MAC` (verified) | Use |
|---------------------|----------------------|-----|
| `=100` immediate (`LDA =100`) | errors `ILL. USE OF COMMAND` | `SAA`/`SAT` (±127), or a labelled data word |
| `)ENTR START` | errors `WHAT? ENTR` | `)9BEG START` |
| `MONITOR 43` / `MONITOR 3` | not the form used | `MON n`; exit is `MON 0` |
| `JSR` / `JMP I 0` subroutine return | not exercised here | we used straight-line + `JMP` flow; verify before relying on `JSR` |

These may reflect a different MAC variant/version than the one resident at
segment 134B on our SINTRAN. The point isn't that either doc is "wrong" —
it's that **if you're building through `@MAC` + `)9ASSM` on SINTRAN III,
the right-hand column is what assembles.**

---

## 10. Debugging methodology

When a MAC program assembles but misbehaves at runtime, in order of payoff:

1. **Marker prints.** Insert `SAT 1; SAA <ascii>; MON 2` (or `MON 35`) at
   each milestone. The terminal output becomes an execution trace —
   e.g. `ABCDEFG` tells you which phases ran and where it stopped. This is
   the fastest, most reliable tool; reach for it first.
2. **Assemble with `list = TERM`.** MAC echoes each source line before its
   diagnostics, which is the only dependable way to map an error back to a
   source line (error addresses are location-counter-relative, not line
   numbers).
3. **Disassemble the `:PROG`/`:BRF`.** Cross-check the generated code and
   addressing against intent (the project ships disassembly tooling; the
   PROG/BRF format is documented under Reference-Manuals).
4. **Read the device/emulator logs.** For I/O (HDLC, disk), the `nd100x`
   logs show every IOX register access and DMA command, which pins down
   whether the chip saw what you intended.

---

## See Also

- **[MAC-DEVELOPER-GUIDE.md](MAC-DEVELOPER-GUIDE.md)** — the MAC language reference (syntax, addressing, directives, macros).
- **[ND-60.096 MAC Interactive Assembly and Debugging System User's Guide](<../../../Reference-Manuals/ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide.md>)** — the authoritative `@MAC` subsystem manual.
- **[ND-60.113 Assembler Reference Manual](<../../../Reference-Manuals/ND-60.113.02 EN Assembler Reference Manual.md>)** — instruction set reference.
- **[ND-860228 SINTRAN III Monitor Calls](<../../../Reference-Manuals/ND-860228-2-EN SINTRAN III Monitor Calls.md>)** and **[ND MON Calls](<../../MON/ND MON Calls.md>)** — the monitor-call catalogue.
- **[ND-60.066 ND Relocating Loader](<../../../Reference-Manuals/ND-60.066.04 ND Relocating Loader.md>)** — NRL linking.
- **[LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md)** — build/link workflow.
- **[HDLC Raw Programming Guide](../../../SINTRAN/Devices/HDLC/HDLC-Raw-Programming-Guide.md)** — programming the HDLC device (MON 201B, DCBs) — the natural next step once you can write MAC.
- **[HDLC Buffer-Pool and Emulator Usage](../../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md)** — buffer setup, receive tuning, and running HDLC under nd100x.

---

*This cookbook is empirical: every claim was observed while building and
running MAC programs through `@MAC` on SINTRAN III VSX/500 L under nd100x.
Where it disagrees with a manual, it is reporting what the live system did —
please verify on your own configuration before treating any single item as
universal.*
