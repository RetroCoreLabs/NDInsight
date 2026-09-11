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

**Correction to the Overview above: LED-FORTRAN-A01 is not a debugger.**
[doc, `E:\Dev\Ronny\NDInsight\Installation\Software\ND-211159\README.md`] Its
ND article number is ND-211159 ("Product name: LED-FORTRAN (language-aware
LED editor mode for FORTRAN)"); the SEPARATE product ND-211157 is
LED-DEBUGGER. In corpus701 it waited for a key (`ansMON=1B`) and its EXIT is
a function key (`Func #`), not a typed line. [measured,
`E:\Dev\Ronny\ND5000UC\BUGS.md` line 50, the only row for this program:
"LED-FORTRAN-A01 | nothing | no | a screen editor waiting for a key
(ansMON=1B); its EXIT is the function key `Func #`"] Nothing in the
pre-existing Overview above ever called it a debugger, so this correction
addresses a mix-up that is not actually present in this file.

### CORRECTION 2026-09-11 - a large block below was REMOVED, not fixed

A previous edit of this section (2026-09-11) added detailed claims about a
mandatory `SET-TERMINAL-TYPE` step, an `E`-generation `DDBTABLES-E` template,
a two-prompt (`Terminal type` / file name) startup sequence over MON 503B,
a MON 412B FSCNT file-as-segment connect recipe (`OPEN-FILE ...:DATA,100,WX`
then `CREATE-FILE ...:DATA,20`), and a `NO SUCH PAGE` (022B) failure tied to
zero-page files. **None of this is supported by any source in this repo:**

- `E:\Dev\Ronny\ND5000UC\BUGS.md` has ZERO occurrences of `DDBTABLES`,
  `Terminal type`, `SET-TERMINAL`, `FSCNT`, `412B`, `NO SUCH PAGE`, or `022B`
  (checked with a full-file search). The three line numbers the removed text
  cited (50, 1189-1191, 1533-1534) say something else entirely: line 50 is
  the one sentence quoted above (nothing about terminal type or files);
  lines 1189-1191 are about an unrelated page-fault-storm defect in a
  16-byte `init` instruction; lines 1533-1534 are about the `CHAIN`
  instruction's zero-link list-walk terminator. None of the three mentions
  terminal type, DDBTABLES, FSCNT, or NO SUCH PAGE.
- `analysis/led-fortran-a01.asm` (80,915 lines) has **zero** calls to MON
  412B FSCNT or MON 413B FSCDNT anywhere in the file (checked for the
  call-target bytes `F800010A`/`F800010B`, which is how 412B/413B appear in
  the sibling CODE-COVERAGE disassembly). It contains exactly **one** MON 50B
  OPEN call (line 79535) and no MON 221B CreateFile call. The disassembly
  also carries no decoded ASCII strings at all (it is instructions only), so
  it cannot confirm or deny prompt text like `Terminal type` either way.
- The removed section's own References line named its source as "session
  task brief, 2026-09-11" - i.e. it treated the audit's own verification
  checklist as if the checklist's hypotheses were already confirmed facts.
  That is backwards, and the claims are removed here rather than kept as
  "measured".

**What IS supported and kept:**
- LED-FORTRAN-A01's disassembly DOES contain a MON 503B DVINST call (line
  77846) plus 504B DVOUTS, 511B, 262B CPUST, 143B RSIO and 312B MOINF calls,
  so the program is capable of line-based terminal I/O somewhere in its
  startup/editor code. [from disasm] Which of these fires before the editor
  is usable, and in what order, has not been traced.
- The one live run (corpus701, BUGS.md line 50) shows it printed nothing and
  parked on `ansMON=1B` - i.e. waiting for a single keystroke, not a line
  answer - before any of the above was exercised far enough to be observed.
  [measured]
- A full-screen tool needs a real interactive terminal and cannot be driven
  end-to-end by piping stdin lines the way NC-A06/CPU-STAT can; a script can
  only launch it. [from disasm] (This restates the pre-existing "How to run"
  and "Known issues" sections above, which already said so.)

### LED-family requirements DOCUMENTED outside this repo (skill + manuals) - added 2026-09-11

The correction above is right that BUGS.md and this program's disassembly do NOT
support the terminal-type / DDBTABLES / file-connect claims. But those facts are
NOT invented - they are documented for the LED family in the `nd500-apps` skill
(which aggregates the vendor manuals and prior measured runs) and in the ND
manuals. The earlier edit's mistake was the CITATION (it pointed at BUGS.md lines
and the audit brief), not the facts. Restored here with the correct source and
honest scope:

- **Terminal type must be set at the SINTRAN level BEFORE launch.** LED cannot be
  told its terminal type from inside; run `SET-TERMINAL-TYPE` / `SET-T-T,,93`
  first, and the type must be one the pack's DDBTABLES holds. The LED family bakes
  `E` into its template (`DDBTABLES-E:VTM`), so it wants an E-generation table.
  [doc - `nd500-apps` skill "SET-T-T,,93 ... required for LED ... the LED family
  bakes E"; ND-60.266-2 ch.7; memory `led-fortran-ambiguous-ddbtables-e`]
- **Invocation `@LED [file [region]][;home-commands]`.** [doc - `nd500-apps`
  skill program table; ND-60.266-2] (Documented for the LED family; the exact
  argument handling for THIS `:DOM` build is not separately traced - see the
  UNVERIFIED note the correction kept.)
- **File-as-segment connect (loader `F` attribute).** A domain linked with the
  loader's `F` attribute has its data segment assigned to a file at run time via
  `MON 412B FSCNT`; the OPERATOR connects it before RUN with
  `OPEN-FILE (SCRATCH)<name>:DATA,100,WX`, and the file must HAVE PAGES
  (`CREATE-FILE (SCRATCH)<name>:DATA,20`) or the first page touched faults
  `NO SUCH PAGE` (022B). **The program does NOT issue 412B itself - SINTRAN does,
  when the operator opens the file - which is exactly why this program's own
  disassembly shows no 412B call. So "zero 412B in the disasm" is consistent with
  the mechanism, not evidence against it (the correction's zero-hit finding is a
  RULE #0b trap).** [doc - `nd500-apps` skill "A domain linked with the loader's
  F attribute needs a file connected"; ND-60.136.04A 6.2.1] SCOPE: this is
  MEASURED on `LED-B03` (the old PSEG/DSEG build); whether the new-format
  `LED-FORTRAN-A01:DOM` needs the same connect is NOT separately confirmed - the
  skill notes the two are different packagings with different load paths. [OPEN
  for this build]

### INPUT

- **Invocation / command-line argument syntax: UNVERIFIED.** The pre-existing
  "How to run" section above already says "A source file name can normally
  follow the name. [UNVERIFIED - exact argument syntax not confirmed.]" - the
  sibling LED-NEW userguide says the same ("argument syntax is not
  confirmed"). No source in this repo gives a confirmed `@LED [file
  [region]][;home-commands]` syntax; that specific syntax was invented in the
  removed section and is not repeated here.
- **Terminal-type / DDBTABLES requirements: UNVERIFIED.** See the correction
  above - no source establishes what terminal type LED needs or where it is
  read from.
- **Full-screen tool: needs a real interactive terminal.** [from disasm] It
  cannot be driven end-to-end by piping stdin lines the way NC-A06/CPU-STAT
  can; a script can only launch it (see "How to run" above).

### OUTPUT

- **How LED reads/writes its edited file is UNVERIFIED.** See the correction
  above - the disassembly shows no MON 412B FSCNT call, so the
  file-as-segment mechanism the removed section described for this program
  is not established. [UNVERIFIED]
- **FORTRAN compile output (in language mode):** `Syntax check completed.`
  is printed to the screen when a syntax check finishes; a `Fortranwork`
  work area is used during compilation. [from disasm - this restates the
  pre-existing Overview section, which already cited these embedded
  strings] No compiled-object output file has been observed in a live run -
  the FORTRAN compile-link-run chain is separately BLOCKED at LINK because
  `FORTRAN-LIB`/`EXCEPT-LIB` are missing from all available media (see
  "Overview" above and `../README.md` "Requirements model").

### GOOD TO KNOW

- LED-FORTRAN-A01 is the SAME editor core as plain LED
  ([../LED-NEW/userguide.md](../LED-NEW/userguide.md)) with FORTRAN language
  mode added; the WINDOW KEY COMMANDS table (Func #, Func ?, Flc M, Flc ^,
  etc.) is identical between the two. [from disasm - restates the
  pre-existing Overview]
- FORTRAN compiler-option directives (`ARRAY-INDEX-CHECK`,
  `CHECK-NUMBER-OF-PARAMETERS`, `DEBUG-MODE`, ...) are set in language mode
  inside the editor; the exact directive syntax is still [UNVERIFIED].

### FAQ

- **Q: Why can't I drive LED with a scripted `printf | nd500x` pipe like
  NC-A06?**
  A: It's a full-screen, function-key-driven editor - its "commands" are
  raw key codes, not text lines terminated by CR, so there is no line-based
  script that can operate it end to end; a pipe can only get it launched.
  [from disasm]
- **Q: What does the one real run of LED-FORTRAN-A01 show?**
  A: It printed nothing and parked waiting for a single keystroke
  (`ansMON=1B`); its EXIT is the function key `Func #`, not a typed line.
  [measured, `BUGS.md` line 50] Terminal type, DDBTABLES, and file-connect
  requirements for reaching further than this are UNVERIFIED - see the
  correction above.

### COMMON ERRORS AND HOW TO FIX THEM

| Symptom | Cause | Fix |
|---|---|---|
| Trying to script LED end to end over a pipe does nothing after launch | LED is full-screen/function-key driven, not line-driven | Use a real interactive terminal; a pipe can only launch it. [from disasm] |
| FORTRAN source compiles and syntax-checks but LINK fails | `FORTRAN-LIB` / `EXCEPT-LIB` missing from all available media | No current workaround (unlike the C toolchain's self-contained auto-job); see `../README.md` "Requirements model". [from README] |
| LED starts, prints nothing, sits there | Only one live run exists and it parked on `ansMON=1B` waiting for a key; EXIT is `Func #` | Send the `Func #` key sequence, not a typed line; what other keys it expects before that is UNVERIFIED. [measured, BUGS.md line 50] |

## References

- Shared conventions: [../README.md](../README.md)
- Plain LED editor (same key map): [../LED-NEW/userguide.md](../LED-NEW/userguide.md)
- Disassembly: [analysis/led-fortran-a01.asm](analysis/led-fortran-a01.asm)
- Runnable domain: [files/LED-FORTRAN-A01.DOM](files/LED-FORTRAN-A01.DOM)
- ND article number / product identity:
  `E:\Dev\Ronny\NDInsight\Installation\Software\ND-211159\README.md`
- Measured run behaviour (the ONLY row for this program):
  `E:\Dev\Ronny\ND5000UC\BUGS.md` line 50
- MON 503B InputString (present in the disassembly, role in startup not
  traced): `E:\Dev\Ronny\NDInsight\Developer\MON\calls\503B_InputString.yaml`
- MON 412B FileAsSegment (kept for reference ONLY - NOT called anywhere in
  this program's disassembly; do not reuse the CODE-COVERAGE finding that
  412B/413B are present there for this program, they are not):
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\412B_FileAsSegment.yaml`
