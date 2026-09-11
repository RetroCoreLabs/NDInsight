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

- **Command line / arguments: none needed.** [doc] CODE-COVERAGE is
  question-driven (see "Commands and options" above) - it does not read a
  program-name argument off the SINTRAN command line the way `NC TEST` does.
  Start it with the bare name at `@`.
- **All input is read from device 1 (your own terminal), one prompt at a
  time, via MON 503B InputString (DVINST).** [inferred from
  `../../Developer/MON/calls/503B_InputString.yaml`] 503B is the standard
  ND-500 terminal line-read call; nothing in the disassembled prompt list
  (`Compiler List file:`, `DUMP-LOG file:`, `New input file:`, `Print the
  source (Y/N):`, `Output file:`, `Program language:`) suggests device-0
  command-buffer reads the way NC-A06 or NC-A06-style programs use them - see
  the memory note `nc-reads-its-parameter-line-from-the-command-buffer.md` for
  the device-0 pattern this program does NOT show.
- **503B blocks (suspends) on an empty line and re-reads the whole line on
  resume.** [doc, 503B yaml `verified` block] This is exactly why an EXIT
  typed BEFORE the banner in corpus701 was swallowed by the FIRST prompt
  (`Program language:`) rather than being queued for a later one - each
  prompt only consumes the answer you give it at the moment it is asked.
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
- **No file-as-segment mechanism.** [inferred] CODE-COVERAGE reads its two
  input files and writes its one output file as ordinary text; there is no
  evidence in the disassembly of a MON 412B FSCNT (FileAsSegment) call the
  way LED-FORTRAN uses one - it looks like plain sequential MON 117B/120B-style
  file I/O. [UNVERIFIED - the MON-call trace for this program has not been
  captured live.]

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
- MON 503B InputString (terminal reads):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\503B_InputString.yaml`
- MON 50B OpenFile / MON 221B CreateFile (output-file convention):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\50B_OpenFile.yaml`,
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\221B_CreateFile.yaml`
- Measured run behaviour: `E:\Dev\Ronny\ND5000UC\BUGS.md` (lines 29-51 table,
  B8 at line 406)
