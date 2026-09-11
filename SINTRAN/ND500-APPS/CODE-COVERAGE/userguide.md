# CODE-COVERAGE - code-coverage analyser / reporter

## Overview

CODE-COVERAGE is a Norsk Data code-coverage reporting tool. It combines a
DEBUGGER dump-log file with a compiler source listing and produces a listing in
which the non-executed statements are highlighted, then prints a coverage
figure. [from disasm] The embedded welcome text is
`Welcome to the code-coverage analyzer, version of ...` and the version date in
the DOM is `DECEMBER 3, 1986`; it credits `OJH, M4`. [from disasm] It works for
both ND-100 and ND-500 programs (`a for ND-100` / `a for ND-500`). [from disasm]

The tool loads and reaches its input prompts. [verified] (load-sweep
2026-07-31 in nd500x)

For shared install/run conventions see [../README.md](../README.md).

## Files (in files/)

- `CODE-COVERAGE.DOM` - the runnable ND-500 domain. One segment, entry point
  0x08001CA9, linker v97.2. [from disasm] Self-contained (no PSEG/DSEG/HELP/
  INIT ships). [verified]

## Requirements

- Just the `.DOM` file to run. [verified]
- To produce useful output it needs, as inputs, an existing DEBUGGER dump-log
  file and the compiler list file for the same program. [from disasm]
- Install: copy `files/CODE-COVERAGE.DOM` into the sintran-root. See
  [../README.md](../README.md).

## How to run

Interactive: at the SINTRAN `@` prompt type the bare name (the `@` is the
prompt, do not type it):

```
CODE-COVERAGE
```

It then asks a fixed series of questions (see below). Scripted drive from
`~/repos/nd500x`, answering the prompts in order:

```
printf 'LOGIN GUEST\nCODE-COVERAGE\nMYPROG:DUMP\nMYPROG:LIST\nN\nOUT:SYMB\nEXIT\n' \
    | ./build/bin/nd500x --monitor --user GUEST --sintran-root ~/ND500USERS
```

WARNING: the exact prompt ORDER and how many answers are needed is NOT
run-verified in nd500x - only that the program loads. [verified] The printf
above is a plausible ordering derived from the embedded prompts, not a proven
transcript. Adjust the answer lines to match what the program actually asks.

## Commands and options

CODE-COVERAGE is question-driven, not command-driven: there is no command
prompt, no `HELP` and no `EXIT` token in the DOM. [from disasm] It asks a set of
questions and then produces the report. The prompt strings embedded in the DOM
are: [from disasm]

- `Compiler List file:` - the source listing produced by the compiler.
- `DUMP-LOG file:` - the DEBUGGER dump-log to analyse.
- `New input file:` - used when the debug file contains include statements and a
  new input file must be built.
- `Print the source (Y/N):` - whether to emit the annotated source listing.
- `Output file:` - where the report is written.
- `Program language:` - source language selector (rejects with `Illegal keyword`
  / `Unknown language` / `Ambiguous language`).

Report text it prints includes:
`Total number of active lines (included declarations) in the program are`,
`Number of lines not executed are`,
`The following routines have non executed source lines:`, and
`The code coverage figure is <n> percent`. [from disasm]

UNVERIFIED: the precise order of the questions, and which are conditional.

## Verified behaviour in nd500x

- Loads and reaches its input prompt. [verified] (load-sweep 2026-07-31)
- A full analysis run has NOT been driven end to end in nd500x. [verified]

## Known issues / status

- Prompt sequence documented from the binary only; not exercised live.
  [from disasm]
- Needs valid DEBUGGER dump-log + compiler list-file inputs to do anything
  useful; producing those is a separate step not covered here. [from disasm]

## Input & output files, FAQ, common errors (added 2026-09-11)

### INPUT

- **Command line / arguments: none needed.** [from disasm] CODE-COVERAGE is
  question-driven (see "Commands and options" above) - it does not read a
  program-name argument off the SINTRAN command line the way `NC TEST` does.
  Start it with the bare name at `@`.
- **CORRECTED 2026-09-11: input is read from device 1 (your own terminal)
  ONE BYTE AT A TIME via MON 1B InByte (INBT), NOT via MON 503B InputString.**
  [from disasm, `analysis/code-coverage.asm`] The monitor-call table in the
  disassembly contains exactly one input call, `MON 1B INBT` at `0x08003DA4`
  (paired with `MON 2B OUTBT` for output at `0x08003DBD`) - there is NO
  occurrence of `503B`/`DVINST` anywhere in the 2623-line file (checked with a
  full-file search). The live run agrees: run308 (`E:\Dev\Ronny\ND5000UC\BUGS.md`
  line 408) records "one `MON 1B`" for this program's only captured input
  attempt, not a 503B call. An earlier draft of this section claimed 503B by
  inference from the prompt list alone, without reading the disassembly's own
  monitor-call table - that inference was wrong.
  Nothing in the prompt list or the monitor-call table shows a device-0
  command-buffer read the way NC-A06 uses one - see the memory note
  `nc-reads-its-parameter-line-from-the-command-buffer.md` for the device-0
  pattern this program does NOT show.
- **MON 1B InByte blocks (suspends) when the input buffer is empty and
  resumes when a byte arrives.** [doc, `1B_InByte.yaml`: "The program waits if
  there is no bytes in the input buffer of the device."] This is consistent
  with why an EXIT typed BEFORE the banner in corpus701 was swallowed by the
  FIRST prompt (`Program language:`) rather than being queued for a later one
  - each prompt only consumes the answer given at the moment it is asked.
  [measured, `E:\Dev\Ronny\ND5000UC\BUGS.md` line 46: "EXIT typed BEFORE the
  banner (`Unknown language`), then parked on the next read"]
- **Input FILES it needs to do useful work** (not command-line args - file
  NAMES you type at the `Compiler List file:` and `DUMP-LOG file:` prompts):
  [from disasm]
  - a **compiler source listing** (the file you'd give at `Compiler List
    file:`) - the `.LIST` output of an ND-500 compiler (NC, PLANC, ...) run
    against the program being measured.
  - a **DEBUGGER dump-log file** (the file you'd give at `DUMP-LOG file:`) -
    a trace/log produced by the ND-500 symbolic DEBUGGER of a run of that
    same program. Neither file ships with CODE-COVERAGE; you must produce
    them yourself with the compiler and the DEBUGGER first. [from disasm]
  - if the dump-log's source has `%INCLUDE`-style statements, it asks `New
    input file:` for a rebuilt single-file version. [from disasm]
- **Terminal type requirement: none known.** [inferred] Unlike LED-FORTRAN,
  nothing in the prompt list or in `analysis/code-coverage.asm` suggests a
  full-screen or DDBTABLES-driven terminal type; CODE-COVERAGE reads and
  writes plain lines, so the default SINTRAN terminal type should work.
  [UNVERIFIED - not run end to end.]

### OUTPUT

- **Report file, written where you name it at the `Output file:` prompt.**
  [from disasm] CODE-COVERAGE does not create the file itself before writing
  - like other ND-500 tools that OPEN their outputs for write (see the shared
  README "Gotchas" section), if the named file does not already exist the
  write can fail with SINTRAN ERROR 56B (`No such file name`, MON 50B
  OpenFile). [inferred from `../README.md` "CREATE-FILE the output files
  before COMPILE" gotcha and `50B_OpenFile.yaml` error table] **CREATE-FILE
  the output file before answering `Output file:`**, e.g.
  `@CREATE-FILE MYPROG:COVR` then answer `MYPROG:COVR` at the prompt.
  [inferred - not run-verified for this program specifically]
- **What gets written:** the annotated source listing (if you answered `Y` to
  `Print the source (Y/N):`) with non-executed statements marked, plus the
  summary lines `Total number of active lines (included declarations) in the
  program are`, `Number of lines not executed are`, `The following routines
  have non executed source lines:`, and `The code coverage figure is <n>
  percent`. [from disasm]
- **CORRECTED 2026-09-11: the disassembly's monitor-call table DOES contain a
  MON 412B FSCNT and a MON 413B FSCDNT call** (`analysis/code-coverage.asm`
  lines with `; MON 412B FSCNT` and `; MON 413B FSCDNT`), alongside plain
  `MON 117B RFILE` / `MON 120B WFILE`. An earlier draft of this section
  claimed "no evidence... of a MON 412B FSCNT call" - that is factually wrong;
  the call is present. What is NOT established is which mechanism CODE-COVERAGE
  actually uses at runtime for its two input files and its output file - the
  table only proves the program is LINKED against both the file-as-segment
  calls and the plain sequential-I/O calls; no live MON-call trace has been
  captured for a full run to say which path executes. [UNVERIFIED - which of
  412B/413B vs 117B/120B fires at runtime]

### GOOD TO KNOW

- It is **question-driven, not command-driven**: there is no `HELP` command
  and no command prompt to type things at - just answer each question as it
  appears. [from disasm]
- The exact question ORDER is not run-verified; the six prompt strings above
  are all that is known from the binary. [from disasm] Treat the order in
  "Commands and options" as a best guess, not a script.
- `Program language:` is the FIRST prompt shown after the banner in the one
  live run captured so far (corpus701, run308). [measured,
  `E:\Dev\Ronny\ND5000UC\BUGS.md` line 46]

### FAQ

- **Q: What do I need before I run CODE-COVERAGE?**
  A: A compiler `.LIST` file and a DEBUGGER dump-log for the SAME program
  run, both already on disk, plus (recommended) a CREATE-FILE'd empty output
  file. [from disasm + inferred]
- **Q: Can I drive it from a script/pipe like NC-A06?**
  A: Only if you answer each prompt in the right order with the right file
  names - it is interactive question-and-answer over MON 503B, which
  suspends waiting for a real line, so a `printf | nd500x` style drive works
  as long as the lines match what it's currently asking. [doc + inferred]
- **Q: Why did my run print nothing after the banner?**
  A: You likely answered `Program language:` (or an earlier prompt) with
  something it didn't expect, or your answer arrived before the prompt was
  actually posted - see B8 in `BUGS.md` line 406 ("CODE-COVERAGE ... produce
  no output at all"). [measured]

### COMMON ERRORS AND HOW TO FIX THEM

| Symptom | Cause | Fix |
|---|---|---|
| `Unknown language` right after the banner, then the program hangs | An answer (e.g. a bare `EXIT`) was typed BEFORE the `Program language:` prompt was posted, so it landed as the language answer instead | Wait for each prompt on the SCREEN before sending the next line; don't pre-queue answers on a timer. [measured, BUGS.md line 46] |
| `Illegal keyword` / `Ambiguous language` at `Program language:` | The language name typed doesn't match one of the languages CODE-COVERAGE recognises | Retype using the exact language keyword the compiler used (see the compiler's own userguide for its language name). [from disasm] |
| No output at all, run just sits there (B8, `nothing printed`, `trapsPosted=3`, one `MON 1B`) | The program is parked waiting on a later prompt that was never answered, or one of the input files it asked for does not exist | Check what it's actually waiting for on the live screen before assuming it's broken; feed the exact file names it asked for. [measured, `BUGS.md` line 406-409] |
| Write to the `Output file:` name fails | The output file was never CREATE-FILE'd first | `@CREATE-FILE <name>:<type>` before running, then answer with that same name. [inferred from the shared README gotcha + `50B_OpenFile.yaml`] |

## References

- Shared conventions: [../README.md](../README.md)
- Disassembly: [analysis/code-coverage.asm](analysis/code-coverage.asm)
- Runnable domain: [files/CODE-COVERAGE.DOM](files/CODE-COVERAGE.DOM)
- MON 1B InByte (terminal reads - the call CODE-COVERAGE actually uses, per
  its own disassembly's monitor-call table):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\1B_InByte.yaml`
- MON 50B OpenFile / MON 221B CreateFile (output-file convention):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\50B_OpenFile.yaml`,
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\221B_CreateFile.yaml`
- Measured run behaviour: `E:\Dev\Ronny\ND5000UC\BUGS.md` (lines 29-51 table,
  B8 at line 406)
