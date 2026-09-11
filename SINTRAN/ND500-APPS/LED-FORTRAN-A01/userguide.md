# LED-FORTRAN-A01 - LED editor with integrated FORTRAN compiler

## Overview

LED-FORTRAN is the Norsk Data LED full-screen editor bound to the ND FORTRAN
compiler: the same LED screen editor as [../LED-NEW/userguide.md](../LED-NEW/userguide.md),
plus a FORTRAN "language mode" that syntax-checks and compiles the edited source
in place. [from disasm] Embedded strings confirm both halves: the full LED
`WINDOW KEY COMMANDS` table (windows, marked areas, `Func # EXIT`, `Func ? HELP`,
`Flc M Syntax check area. LANGUAGE MODE`), and FORTRAN-specific text such as
`Syntax check completed.`, `Fortranwork`, and a large list of FORTRAN compiler
options (see below). [from disasm] This is version A01. [verified] (folder name)

The compiler domain loads. [verified] (load-sweep 2026-07-31 in nd500x)

IMPORTANT BLOCKER: taking FORTRAN source through the full compile -> link -> run
chain is currently BLOCKED AT LINK, because `FORTRAN-LIB` and `EXCEPT-LIB` are
missing from all available media, so the linker cannot resolve the FORTRAN
runtime and exception handlers. See [../README.md](../README.md) "Requirements
model" (the C toolchain works around this with a self-contained auto-job; there
is no such workaround for FORTRAN here). [from README]

For shared install/run conventions see [../README.md](../README.md).

## Files (in files/)

- `LED-FORTRAN-A01.DOM` - the runnable ND-500 domain (editor engine + FORTRAN
  compiler in one, ~1.3 MB). One segment, entry point 0x08000004, linker v97.2.
  [from disasm] Self-contained (no separate PSEG/DSEG/HELP/INIT ships alongside).
  [verified]

## Requirements

- To RUN the editor/compiler: just the `.DOM` file. [verified]
- To LINK and RUN compiled FORTRAN output: `FORTRAN-LIB` + `EXCEPT-LIB` - which
  are NOT present on any available media. FORTRAN link is therefore blocked.
  [from README]
- A full-screen terminal to use the editor interactively. [from disasm]
- Install: copy `files/LED-FORTRAN-A01.DOM` into the sintran-root. See
  [../README.md](../README.md).

## How to run

Interactive: at the SINTRAN `@` prompt type the bare name (the `@` is the
prompt, do not type it):

```
LED-FORTRAN-A01
```

A source file name can normally follow the name. [UNVERIFIED - exact argument
syntax not confirmed.]

Scripted drive can only launch it (it is full-screen; you cannot edit over a
pipe):

```
printf 'LOGIN GUEST\nLED-FORTRAN-A01\n' | ./build/bin/nd500x --monitor \
    --user GUEST --sintran-root ~/ND500USERS
```

Real use needs an interactive terminal. [from disasm]

## Commands and options

Two layers, both read from the DOM strings and NOT run-verified. [from disasm]

Editor keys (the LED `WINDOW KEY COMMANDS` table, embedded verbatim): [from disasm]

- `Func #` (EXIT) - exit from editor.
- `Func ?` (HELP) - give help.
- `Flc M` (Execute key) - syntax check area, LANGUAGE MODE.
- `Flc ^` (Shift Execute) - continue syntax check, LANGUAGE MODE.
- `Func C` copy, `Func D` delete, `Func M` move, `Func F` mark field,
  `Func Z` mark contiguous area, `Func ]` window mode, plus many cursor/scroll
  and `Ctrl`-key line-editing commands. See the disassembly for the full table.

FORTRAN compiler options (option names embedded in the DOM; set in language mode
/ compiler directives): [from disasm]

`ARRAY-INDEX-CHECK`, `CHECK-NUMBER-OF-PARAMETERS`, `COBOL-INTERFACE`,
`CONDITIONAL-COMPILING`, `CROSS-REFERENCE`, `DEBUG-MODE`, `HEADING-TEXT`,
`INLINE-EXPANSION`, `LINK-SEGMENT`, `LOCAL-STACK-SIZE`, `MAIN-STACK-SIZE`,
`MON-CALL-NAMES`, `MOVE-COMMON-VARIABLES`, and several non-standard-language
flags. [from disasm]

UNVERIFIED: the exact directive syntax for setting these options, and how the
compile is invoked from inside the editor versus as a batch compile.

## Verified behaviour in nd500x

- The domain loads. [verified] (load-sweep 2026-07-31)
- No compile/edit session has been driven in nd500x; the FORTRAN link step is
  blocked (missing libraries), so a compiled program cannot currently be linked
  or run. [verified] / [from README]

## Known issues / status

- BLOCKER: FORTRAN compile -> link -> run is blocked at link (`FORTRAN-LIB` and
  `EXCEPT-LIB` missing from all media). [from README]
- Full-screen interactive tool: needs a real terminal; not drivable by pipe.
  [from disasm]
- Command/key map and compiler-option syntax are [UNVERIFIED] for this binary.

## Input & output files, FAQ, common errors (added 2026-09-11)

**Correction to the Overview above: LED-FORTRAN-A01 is NOT a debugger.**
[measured] It is the ND Language EDitor (ND 211159), the FORTRAN-mode build
of LED - the same full-screen screen editor as LED-NEW/LED-B03, plus
FORTRAN-mode syntax check/compile. In corpus701 it waited for a key
(`ansMON=1B`) and its EXIT is a function key (`Func #`), not a typed line.
[measured, `E:\Dev\Ronny\ND5000UC\BUGS.md` line 50]

### INPUT

- **Invocation: `@LED [file [region]][;home-commands]`.** [doc] A file name
  and an optional region can follow the program name on the command line;
  optional home-commands (editor commands run at startup) can follow a `;`.
- **Terminal type MUST be set BEFORE the program starts, at the SINTRAN
  level - it cannot be set from inside LED.** [measured] Use
  `SET-TERMINAL-TYPE` (or `SET-T-T,,93` short form) at the `@` prompt, and
  the type must be one the installed pack's DDBTABLES actually holds. LED's
  own template bakes in `E` generation (`DDBTABLES-E:VTM`), so the pack needs
  an E-generation DDBTABLES table for LED's default terminal type to resolve.
  [measured] (Compare `../README.md`'s abbreviated-name note on
  `DDBTABLES-G` for the linker - each program's DDBTABLES generation
  requirement is program-specific, not a shared default.)
- **LED asks TWO questions in order at startup, both over the terminal
  (device 1), and both are BLOCKING MON 503B InputString reads:** [measured
  + inferred from `503B_InputString.yaml`]
  1. **Terminal type**, first. If a usable type was NOT preset with
     `SET-TERMINAL-TYPE`, LED PRINTS THE WHOLE TERMINAL-TYPE TABLE and stops
     at the prompt `Terminal type `. A bare CR at that prompt gives `THIS
     TERMINAL TYPE IS UNKNOWN`. [measured]
  2. **File name**, second, silently (no visible prompt text recorded).
     [measured] This is the file LED will edit/create - see OUTPUT below for
     what it needs to already exist.
- **A domain linked with the loader's `F` attribute (which LED-FORTRAN is)
  needs its target file CONNECTED AS A SEGMENT before the program can use
  it** - MON 412B FSCNT (FileAsSegment). [measured + doc,
  `412B_FileAsSegment.yaml`] Do this from SINTRAN BEFORE running LED:
  ```
  N500: OPEN-FILE (SCRATCH)<name>:DATA,100,WX
  ```
  The `:DATA` file type is REQUIRED - 412B connects an OPEN file (per MON
  50B/OpenFile's "the file must be open" rule) and LED's `F`-attribute load
  expects a `:DATA`-typed connection specifically. [measured]
- **The connected file must actually HAVE PAGES - `AccessType`/page count
  matters.** [measured] Create it with pages, not empty:
  ```
  @CREATE-FILE (SCRATCH)<name>:DATA,20
  ```
  `20` here is `NoOfPages` (MON 221B CreateFile, "Use 0 if you want to create
  an indexed file" - LED needs the opposite: a real pre-allocated,
  non-zero-page file). [measured + doc, `221B_CreateFile.yaml` parameter
  notes on `NoOfPages`] A zero-page (indexed, no-prealloc) file is what
  produces the `NO SUCH PAGE` failure below.
- **Full-screen tool: needs a real interactive terminal.** [from disasm] It
  cannot be driven end-to-end by piping stdin lines the way NC-A06/CPU-STAT
  can; a script can only launch it (see "How to run" above).

### OUTPUT

- **The file connected as a segment via 412B FSCNT is where LED reads/writes
  its edited text - not a separately-named "output file".** [measured +
  doc] Once connected, the file's bytes are mapped into LED's domain as a
  logical segment (MON 412B `return_contract`: "the file's bytes mapped into
  an MMU/PST-backed logical segment in the caller's domain") and LED
  edits/compiles against that mapped memory rather than doing line-by-line
  MON 117B/120B file I/O. [doc,
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\412B_FileAsSegment.yaml`]
- **No write-back is modelled end to end yet in the harness.** [inferred]
  The 412B yaml's own `unverified` list notes "there is no WRITE-BACK from
  the segment to the file at any point in 412B's lifetime" in the reference
  emulator (nd500x) - whether the SAME is true of the real octobus/SINTRAN
  path this project targets has not been separately confirmed. Treat
  "does LED's saved edit actually reach disk" as open until measured.
  [UNVERIFIED]
- **FORTRAN compile output (in language mode):** `Syntax check completed.`
  is printed to the screen when a syntax check finishes; a `Fortranwork`
  work area is used during compilation. [from disasm] No compiled-object
  output file has been observed in a live run - the FORTRAN
  compile-link-run chain is separately BLOCKED at LINK because
  `FORTRAN-LIB`/`EXCEPT-LIB` are missing from all available media (see
  "Overview" above and `../README.md` "Requirements model").

### GOOD TO KNOW

- **Terminal type cannot be fixed from inside the program** - if you forgot
  `SET-TERMINAL-TYPE` and see the terminal-type table dump, you cannot type
  your way out of it into a working editor session; you must exit and reset
  the type at SINTRAN level first. [measured]
- **The `NO SUCH PAGE` (022B) failure LOOKS like a deep MMU/paging fault but
  usually ISN'T** - it is what you get when LED draws its whole screen and
  then dies because the connected file has zero pages. [measured] Don't
  chase this as a CPU/MMU defect before checking the file was CREATE-FILE'd
  with a non-zero page count.
- LED-FORTRAN-A01 is the SAME editor core as plain LED
  ([../LED-NEW/userguide.md](../LED-NEW/userguide.md)) with FORTRAN language
  mode added; the WINDOW KEY COMMANDS table (Func #, Func ?, Flc M, Flc ^,
  etc.) is identical between the two. [from disasm]
- FORTRAN compiler-option directives (`ARRAY-INDEX-CHECK`,
  `CHECK-NUMBER-OF-PARAMETERS`, `DEBUG-MODE`, ...) are set in language mode
  inside the editor; the exact directive syntax is still [UNVERIFIED].

### FAQ

- **Q: Why does LED print a giant table of terminal types and then just sit
  there at `Terminal type `?**
  A: No terminal type was set before starting LED, or the one that was set
  isn't in this pack's DDBTABLES. Exit, run `SET-TERMINAL-TYPE` (or
  `SET-T-T,,93`) for a type the pack's DDBTABLES actually has (LED wants an
  `E`-generation table by default), then restart LED. [measured]
- **Q: I set a terminal type but LED still says `THIS TERMINAL TYPE IS
  UNKNOWN`.**
  A: You answered the `Terminal type ` prompt with CR/blank, or with a type
  name the DDBTABLES doesn't define. Re-answer with an exact type name from
  the table LED just printed. [measured]
- **Q: LED draws the whole screen then dies with `NO SUCH PAGE`. Is this a
  CPU bug?**
  A: Usually not - it means the file connected as LED's segment (via MON
  412B FSCNT) has zero pages. CREATE-FILE it with a real page count first
  (e.g. `@CREATE-FILE (SCRATCH)<name>:DATA,20`), then OPEN-FILE it
  `,WX` before starting LED. [measured]
- **Q: Can I give LED a file name on the command line instead of typing it
  at the second prompt?**
  A: Yes - `@LED <file> [region]` is the documented invocation - but the
  file still has to be a `:DATA` file already connected/openable the way
  described above; naming it on the command line does not skip the
  CREATE-FILE/OPEN-FILE step. [doc + measured]
- **Q: Why can't I drive LED with a scripted `printf | nd500x` pipe like
  NC-A06?**
  A: It's a full-screen, function-key-driven editor - its "commands" are
  raw key codes, not text lines terminated by CR, so there is no line-based
  script that can operate it end to end; a pipe can only get it launched.
  [from disasm]

### COMMON ERRORS AND HOW TO FIX THEM

| Symptom | Cause | Fix |
|---|---|---|
| Whole terminal-type table dumped, stuck at `Terminal type ` | Terminal type not set before LED started, or not in this pack's DDBTABLES | `SET-TERMINAL-TYPE` / `SET-T-T,,93` at `@` BEFORE starting LED, using a type the pack's DDBTABLES holds (LED wants `E`-generation, `DDBTABLES-E:VTM`). [measured] |
| `THIS TERMINAL TYPE IS UNKNOWN` | Bare CR or an undefined type name answered at `Terminal type ` | Retype an exact name from the table LED just printed. [measured] |
| LED draws its screen then fails with `NO SUCH PAGE` (022B) | The file connected via MON 412B FSCNT has zero pages (created with `NoOfPages=0`, i.e. indexed/no-prealloc) | `@CREATE-FILE (SCRATCH)<name>:DATA,20` (pages > 0) before `OPEN-FILE ... ,WX` and starting LED. [measured] |
| LED never gets a file to edit / silently hangs at the (invisible) file-name prompt | The target file was never OPENed, or was opened without the `:DATA` type | `N500: OPEN-FILE (SCRATCH)<name>:DATA,100,WX` before running LED - `:DATA` is required. [measured] |
| Trying to script LED end to end over a pipe does nothing after launch | LED is full-screen/function-key driven, not line-driven | Use a real interactive terminal; a pipe can only launch it. [from disasm] |
| FORTRAN source compiles and syntax-checks but LINK fails | `FORTRAN-LIB` / `EXCEPT-LIB` missing from all available media | No current workaround (unlike the C toolchain's self-contained auto-job); see `../README.md` "Requirements model". [from README] |

## References

- Shared conventions: [../README.md](../README.md)
- Plain LED editor (same key map): [../LED-NEW/userguide.md](../LED-NEW/userguide.md)
- Disassembly: [analysis/led-fortran-a01.asm](analysis/led-fortran-a01.asm)
- Runnable domain: [files/LED-FORTRAN-A01.DOM](files/LED-FORTRAN-A01.DOM)
- MON 412B FileAsSegment (FSCNT, the file-connected-as-segment mechanism):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\412B_FileAsSegment.yaml`
- MON 50B OpenFile / MON 221B CreateFile (open-before-connect, page-count
  requirement): `E:\Dev\Ronny\NDInsight\Developer\MON\calls\50B_OpenFile.yaml`,
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\221B_CreateFile.yaml`
- MON 503B InputString (terminal reads, blocking-read semantics):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\503B_InputString.yaml`
- Measured run behaviour: `E:\Dev\Ronny\ND5000UC\BUGS.md` (line 50 run table,
  lines 1189-1191, 1533-1534)
- Memory note on terminal type / DDBTABLES / file-as-segment for LED (source
  of the "MEASURED / DOCUMENTED FACTS" used above): session task brief,
  2026-09-11.
