# PLANC-500-G00 - PLANC compiler for the ND-500 (version G00)

## Overview

PLANC is Norsk Data's systems-programming language; SINTRAN III itself and most
ND system tools are written in it. PLANC-500-G00 is the ND-500 PLANC compiler.
It runs as an interactive command shell that reads compiler directives
(COMPILE, INCLUDE, OPTION, LIST, DEBUG-MODE, ...), compiles a PLANC source into
a relocatable `:NRF` object, and can produce a listing and cross-reference. The
`:NRF` is then linked into a runnable `.DOM` with LINKER-B01.

Banner (embedded in the DOM) [from disasm]: `PLANC COMPILER - VERSION G`.

See [../README.md](../README.md) for install, sintran-root layout, and the
requirements model.

## Files (in files/)

| File | Purpose |
|---|---|
| `PLANC-500-G00.DOM` | The PLANC compiler domain (the program you run). ND-500 root domain, linker v97.2, entry `0x0800065C`. |

No `.HELP` or `.INIT` ships in this folder; the command help is built into the
DOM (a `HELP` command lists it).

## Requirements

- To RUN the compiler: only `PLANC-500-G00.DOM` [verified: the DOM loads and
  reaches its prompt].
- To COMPILE + LINK a PLANC program end to end you also need, in SYSTEM
  ([../_shared/files/](../_shared/files/)):
  - `PLANC-LIB.NRF` (the PLANC runtime library)
  - `LINKER-AUTO-PLNC.JOB` (the PLANC linker auto-job)
- Known media gap: the FORTRAN/exception libraries (`FORTRAN-LIB`,
  `EXCEPT-LIB`) are absent from all media; this affects the linker's default
  FORTRAN trap auto-job, not PLANC's own library. See
  [../README.md](../README.md) [verified].

## How to run

Start the SINTRAN shell as described in [../README.md](../README.md), then type
`PLANC-500-G00` at the `@` prompt (the `@` is the prompt, do NOT type it). The
compiler starts and waits for directives at its prompt [verified].

Scripted (non-interactive) invocation feeding stdin. This drives the compiler
to its prompt and issues a COMPILE; a full compile has NOT been run to a
finished `:NRF` here, so treat the compile result as not yet verified:

```sh
printf 'LOGIN GUEST\nPLANC-500-G00\nCOMPILE MYPROG MYPROG MYPROG\nEXIT\n' \
  | ./build/bin/nd500x --monitor --user GUEST --sintran-root ~/ND500USERS
```

COMPILE takes three file arguments: `<source file> <list file> <object file>`
[from disasm].

## Commands and options

Command set read from the compiler's built-in HELP table embedded in the DOM
[from disasm]. Angle-bracket tokens are the argument the compiler expects.
These are extracted from the binary, not yet each run-verified.

| Command | Arguments |
|---|---|
| `COMPILE` | `<source file> <list file> <object file>` |
| `INCLUDE` | `<source file>` |
| `LIST` | `<ON/OFF>` |
| `NOLIST` | (list off) |
| `OBLIST` | `<ON/OFF>` (object/generated-code listing) |
| `OPTION` | `<options>` |
| `CONSTANT` | `<identifier>=<constant value>,...` |
| `KILL` | `<constant identifier>,...` |
| `CROSS-REFERENCE` | `<work file-name>` |
| `XREF` | `<auxiliary file>` |
| `LINKAGE-REFERENCE` | `<work file name>` |
| `DEBUG-MODE` | `<ON/OFF>` |
| `LIBRARY-MODE` | `<ON/OFF>` |
| `MODULE-LIBRARY-MODE` | `<ON/OFF>` |
| `SEPARATE-DATA` | `<ON/OFF>` |
| `CALL-HIERARCHY` | `<ON/OFF>` |
| `SQUEEZE` | `<ON/OFF>` (code-size optimisation; see Known issues) |
| `ARRAY-INDEX-CHECK` | `<ON/OFF>` |
| `BOOLEAN2-ENUMERATION2` | `<ON/OFF>` |
| `REAL-PRECISION` | `<no-of-digits>` |
| `LINE-BIAS` | `<line-number>` |
| `CPU-EXTENSION` | `<number>` |
| `TARGET-MACHINE` | (target selection) |
| `MESSAGE-TO-TERMINAL` | `<message>` |
| `MACRO` / `ENDMACRO` | Define a macro block. |
| `IF` / `THEN` / `ELSIF` / `ELSE` / `ENDIF` | Conditional compilation. |
| `EJECT` | Page eject in the listing. |
| `DATE` | Emit/print the date. |
| `EOF` | End of input. |
| `HELP` | List commands. |
| `EXIT` | Leave the compiler. |

Compiler diagnostics are also embedded (e.g. `SYNTAX ERROR IN GENERAL
OPERAND`, `RANGE EXCEEDED`, `ILLEGAL DATA TYPE`, `CODE BUFFER FULL`) [from
disasm].

## Verified behaviour in nd500x

- The DOM loads and prints its banner ("ND-500 PLANC COMPILER - JUNE 9, 1986
  VERSION G") and reaches the `**` prompt [verified].
- **End-to-end compile VERIFIED (2026-07-31).** Driving:
  `CREATE-FILE X:LIST` / `CREATE-FILE X:NRF`, then `PLANC-500-G00`, then
  `COMPILE X:PLNC,X:LIST,X:NRF` produced a real object file (an 11-line PLANC
  `hello` module -> "11 LINES COMPILED. 0 DIAGNOSTICS." and a 270-byte `X.NRF`).
  Two requirements matter (see ../README.md "Gotchas when driving the compilers"):
  the source must use CR (`0x0D`) line terminators (LF is read as one line, giving
  "1 LINES COMPILED" and an empty NRF), and the `:LIST`/`:NRF` outputs must be
  `CREATE-FILE`d first (else `SINTRAN ERROR 56B`).

## Known issues / status

- Status: **compile end-to-end works** [verified]; command/option details beyond
  `COMPILE` are still [from disasm].
- The DOM embeds the warning `SQUEEZE OPTION GENERATES INCORRECT CODE FOR THIS
  ROUTINE`, so the `SQUEEZE` optimisation can be unsafe on some routines [from
  disasm].
- Linking a compiled PLANC program needs `PLANC-LIB` + `LINKER-AUTO-PLNC.JOB`
  (present in `_shared/files/`); this link has not been verified here.

## Input & output files, FAQ, common errors (added 2026-09-11)

### Input

- **Command source**: the SINTRAN `@` prompt starts `PLANC-500-G00` like any
  other program, and every measured run shows it coming up straight to its own
  `*` prompt with no separate device-0 argument-line step
  [measured, corpus701/corpus709 — banner then `*`, no leading-CR needed].
  **Which device (0 or 1) it reads from once at the prompt is NOT established
  here** — the disassembly in `analysis/planc-500-g00.asm` has no MON 503B
  (DVINST) or 504B (DVOUTS) call at all, for input or output, so this repo has
  no positive evidence either way; absence of a device-0 pattern is not proof
  of device 1, only proof that no such pattern was found in the swept code
  `[OPEN]`. What IS supported is the practical difference from NC-A06 (below):
  a measured run never needed a leading CR or a device-switch step, and never
  showed NC's "type the answer as the very first argument line" trap.
- The prompt is `*` [measured, corpus701/corpus709 — banner
  `ND-500 PLANC COMPILER - JUNE 9, 1986 VERSION G` then `*`].
- **`COMPILE <source>,<list>,<object>`** — three file arguments
  [doc, `analysis/planc-500-g00.asm`]. **Any omitted argument is PROMPTED
  for interactively** [inferred from PLANC's `? ` style directive prompts
  and the HELP table's per-argument shape; not yet isolated by a run that
  deliberately omits one — mark this sub-claim [inferred], not [measured]].
  Practical effect: always pass all three names on the `COMPILE` line in a
  scripted run, or the run will park waiting for a prompt the harness never
  answers.
- Source file type convention: PLANC does not force a specific input type the
  way NC does; corpus709's working run used `PHELLO:PLNC` as the source name
  [measured]. The default **object** type on the ND-500 is `:NRF`
  [doc/measured — corpus709 `PHELLO:NRF`].
- Source line terminators: **must be CR (`0x0D`)** — LF-only source is read as
  a single line ("1 LINES COMPILED", empty NRF) [measured, see "Verified
  behaviour" above].
- `EXIT` leaves the compiler and returns to SINTRAN [doc, HELP table].
- **Common corpus701 failure mode**: typing `EXIT` too early, before the
  banner/prompt has actually printed, is swallowed and PLANC parks waiting on
  its next terminal read — this is a harness timing bug (answer-before-prompt),
  not a PLANC defect [measured, corpus701 headline table: "banner, `*EXIT`" —
  note this run DID complete, so the trap is specifically about the earlier
  2026-09-04 table's mistimed EXIT injections against the OTHER seven
  programs, not PLANC on the corpus701 round].

### Output

- **`:LIST`** — the compile listing, and **`:NRF`** — the relocatable object,
  both named explicitly on the `COMPILE` line [doc]. Both must be
  `CREATE-FILE`d in SINTRAN **before** the `COMPILE` command runs, or SINTRAN
  answers **error 56B** when PLANC tries to open them [measured, "Verified
  behaviour" section above].
- PLANC opens/writes these through ordinary ND-500 file MON calls (the same
  family NC uses — `OPEN`/`CLOSE`/`WFILE`/`RFILE`/`SETBS`/`SMAX`/`RMAX`); the
  corpus701/corpus709 runs report PLANC issuing far more **`MON 2B OutByte`**
  calls than any other DOM program tested (68 in one run) [measured, BUGS.md
  "PLANC also made 68 `MON 2B OutByte` calls"] — consistent with it emitting
  its listing/diagnostics character-by-character rather than in blocks.
- **corpus709 measured product**: `COMPILE PHELLO:PLNC,PHELLO:LIST,PHELLO:NRF`
  -> `10 LINES COMPILED. 0 DIAGNOSTICS.`, `MON 0B`, 2.4 s — the first DOM
  program on the octobus lane to do real, verified work [measured, BUGS.md
  headline table].
- **MEMFS extraction caveat — read this before trusting "the file is on the
  pack"**: the mounted SINTRAN pack is an in-memory MEMFS handle that
  **copies on first write**. A normal run's SINTRAN writes (the new `:LIST`
  and `:NRF`) land only in that in-memory copy-on-write layer — **the working
  disk image on disk is NOT updated** unless the run explicitly saves the
  mounted pack at the end (`RETROCORE_ND5000_SAVE_IMAGE`, exercised in
  corpus710) [measured, BUGS.md]. If you go looking for `PHELLO.NRF` in the
  image file afterward and don't find it, this is why — it is not evidence
  the compile failed.
- Scratch usage beyond `:LIST`/`:NRF` is not characterized here; PLANC's own
  cross-reference/linkage-reference commands (`CROSS-REFERENCE`,
  `XREF`, `LINKAGE-REFERENCE`) take their own explicit work-file names [doc,
  HELP table above] rather than using an implicit SINTRAN scratch segment —
  unlike NC-A06's `GENERATE-CODE`, which hands off through `CAT-CAT5-B06` via
  scratch segments (see NC-A06 userguide).

### Good to know

- PLANC is the compiler SINTRAN itself is written in — it is NOT a C-like
  toolchain and shares no back end with NC/CAT-CAT5 [doc, Overview].
- The `SQUEEZE` optimisation is documented, IN THE DOM ITSELF, as unsafe:
  `SQUEEZE OPTION GENERATES INCORRECT CODE FOR THIS ROUTINE` [from disasm].
  Leave it off unless you are deliberately testing it.
- Compiling end to end does **not** require the linker or `PLANC-LIB.NRF` —
  those are only needed for the later LINK step, not for `COMPILE` itself
  [doc].
- Unlike NC-A06, PLANC issues no MON 317B `UECOM` nested-command call — the
  whole compile happens inside one DOM invocation with no hand-off to a
  second program [inferred from the absence of any `CAT-CAT5`-style back end
  in the Overview/Files section; not independently re-verified against the
  disassembly for this note].

### FAQ

- **Q: I typed `PLANC-500-G00 COMPILE X,X,X` on the SINTRAN command line and
  nothing happened past the banner.**
  A: PLANC does not read the SINTRAN command buffer the way NC-A06 does.
  Start the program bare, wait for the `*` prompt, THEN type the `COMPILE`
  line [doc/measured].
- **Q: My compile produced `SINTRAN ERROR 56B`.**
  A: You did not `CREATE-FILE` the `:LIST` and/or `:NRF` output files first.
  `CREATE-FILE X:LIST` and `CREATE-FILE X:NRF` before running `COMPILE`
  [measured, "Verified behaviour" section].
- **Q: My compile reports "1 LINES COMPILED" and an empty `.NRF` for a
  multi-line source.**
  A: The source file uses LF-only line endings. PLANC wants CR (`0x0D`)
  terminators; re-save/transfer the source with CR endings [measured].
- **Q: The run said `MON 0B` (clean exit) and printed the right compile
  counts, but I can't find the `.NRF` file in the disk image afterward.**
  A: Expected under the default run mode — see the MEMFS extraction caveat
  above. Re-run with `RETROCORE_ND5000_SAVE_IMAGE` set if you need the
  written pack persisted [measured].
- **Q: Can I feed `COMPILE` with some arguments left off and answer the
  prompts afterward?**
  A: The HELP table's argument shape implies PLANC will prompt for a missing
  file name, but this repo has not run that case — treat it as
  [inferred/UNVERIFIED] and always supply all three names in a scripted run.

### Common errors and how to fix them

| Symptom | Cause | Fix |
|---|---|---|
| `SINTRAN ERROR 56B` right after `COMPILE ...` | `:LIST`/`:NRF` output file not created first | `CREATE-FILE X:LIST` and `CREATE-FILE X:NRF` before `COMPILE` [measured] |
| `1 LINES COMPILED` and an empty/near-empty `.NRF` | Source uses LF, not CR, line endings | Convert source to CR (`0x0D`) line terminators [measured] |
| Run parks after the banner, before any `*` prompt shows in the log | Harness sent its next line (e.g. `EXIT`) before the prompt actually rendered | Wait for the literal `*` on screen before sending the next line, not a fixed timer [inferred from the general corpus701 pattern documented for the other seven DOM programs; not PLANC-specific in the measured record] |
| Compiled `.NRF` seems to vanish from the disk image after a "successful" run | MEMFS copy-on-write: writes never left the in-memory layer | Set `RETROCORE_ND5000_SAVE_IMAGE` for the run if you need the pack persisted [measured] |
| `SQUEEZE OPTION GENERATES INCORRECT CODE FOR THIS ROUTINE` | You turned on `SQUEEZE` and PLANC's own runtime check flagged a routine it applies to unsafely | Turn `SQUEEZE` off (`SQUEEZE OFF`) [from disasm] |

## References

- [analysis/planc-500-g00.asm](analysis/planc-500-g00.asm) - ND-500 disassembly (command strings extracted from the DOM)
- [../README.md](../README.md) - shared install/run conventions and requirements model
- [../LINKER-B01/](../LINKER-B01/) - linking the resulting `:NRF` into a `.DOM`
- [../_shared/files/PLANC-LIB.NRF](../_shared/files/PLANC-LIB.NRF) and [../_shared/files/LINKER-AUTO-PLNC.JOB](../_shared/files/LINKER-AUTO-PLNC.JOB) - PLANC runtime + linker auto-job
- ND-500 monitor-call analysis: [../../ND500/](../../ND500/) and [../../../Developer/MON/calls/](../../../Developer/MON/calls/)
