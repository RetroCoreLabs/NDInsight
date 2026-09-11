# AUTOMAKE-500-C00 - make-like build / dependency driver

## Overview

AUTOMAKE-500 is a Norsk Data ND-500 build automation tool, the ND equivalent of
a "make": it reads an automake file (a rules/dependency file), works out which
targets are out of date relative to their sources, and executes the commands
needed to bring them up to date. [from disasm] The embedded version string is
`April 27, 1987`. [from disasm] This is version C00. [verified] (folder name)

The tool reaches an interactive command prompt and waits for input. [verified]
(load-sweep 2026-07-31 in nd500x)

For shared install/run conventions see [../README.md](../README.md).

## Files (in files/)

- `AUTOMAKE-500-C00.DOM` - the runnable ND-500 domain. One segment, entry point
  0x08001305, linker v97.251. [from disasm] Self-contained (no PSEG/DSEG/HELP/
  INIT ships). [verified]

## Requirements

- Just the `.DOM` file to run. [verified]
- Install: copy `files/AUTOMAKE-500-C00.DOM` into the sintran-root. See
  [../README.md](../README.md) "Installing a program into the emulator".
- To actually build a target, AUTOMAKE runs whatever commands the automake file
  names (typically a compiler + LINKER-B01). Those tools and their runtime
  libraries must be installed too. [from disasm] The FORTRAN library gap
  described in [../README.md](../README.md) applies to any FORTRAN target.

## How to run

Interactive: at the SINTRAN `@` prompt type the bare name (the `@` is the
prompt, do not type it):

```
AUTOMAKE-500-C00
```

Scripted (non-interactive) drive, from `~/repos/nd500x`:

```
printf 'LOGIN GUEST\nAUTOMAKE-500-C00\nHELP\nEXIT\n' | ./build/bin/nd500x \
    --monitor --user GUEST --sintran-root ~/ND500USERS
```

The command set is NOT run-verified in nd500x - only that the program loads and
reaches its prompt. [verified] The commands below are read from the strings and
disassembly of the DOM, not from a live session.

## Commands and options

The following command names and their argument syntax are embedded verbatim in
the DOM. [from disasm]

- `MAKE <Automake file> <Target name> <Output file>` - build a target.
- `GENERATE-AUTOMAKE-FILE <Input file> <Automake file> <Own username> <Expand>`
  - produce an automake file from an input file.
- `COPY-REQUIRED <Automake file> <Target name> <Destination>` - copy the files a
  target needs to a destination.
- `LIST-REQUIRED <Automake file> <Target name> <Output file>` - list the files a
  target needs.
- `EXECUTION-MODE <Execute/Unconditional/Touch/List/Off>` - how MAKE acts
  (actually run / force / just timestamp / just list / disabled).
- `STOP-BATCH-ON-FAULT <Ignore/Error/Warning>` - batch abort policy.
- `SET-VALUE <Name> <Value>` - define a macro/value.
- `CHANGE-VALUE <Name> <Value>` - change a macro/value.
- `LIST-VALUES` - list defined macros/values.
- `SEARCH-ORDER <User name 1> ...` - directory/user search order for files.
- `CROSS-REFERENCE <On/Off>` - cross-reference listing on/off.
- `DEBUG-MODE <On/Off>` - debug output on/off.
- `SEPARATE-DATA <On/Off>` - separate-data option on/off.
- `HELP` - list commands. [from disasm]
- `EXIT` - leave the tool. [from disasm]

Prompts seen in the DOM: `Automake file:`, `Destination:`, `Input file:`,
`Identifier:`, `Add own user name (<On/Off>):`, `Expand file names (<On/Off>):`,
and a target-CPU selector `100/500/68000:`. [from disasm]

The automake (rules) file has its own mini-language: conditional statements
(`if ... then`/`elsif`/`else`/`endif`), `head`/`tail` statements, `include`,
`search-order`, and macro assignment with `in` scoping. Error texts such as
`Dependency statements are not allowed in the rulesfile.` and
`` `Else` must be preceded by `if ... then`. `` are embedded. [from disasm]
The exact rules-file grammar is NOT verified here - see the disassembly.

UNVERIFIED: which command is the default when a bare target name is typed, and
the precise semantics of each `<On/Off>` toggle.

## Verified behaviour in nd500x

- Loads and reaches its command prompt; waits for input. [verified]
  (load-sweep 2026-07-31)
- No end-to-end build has been run through it in nd500x. [verified]

## Known issues / status

- Command set documented from the binary only; not exercised live. [from disasm]
- Building a FORTRAN target is blocked by the missing FORTRAN-LIB / EXCEPT-LIB
  (see [../README.md](../README.md)). C targets can use the working C toolchain.
  [from disasm]

## References

- Shared conventions: [../README.md](../README.md)
- Disassembly: [analysis/automake-500-c00.asm](analysis/automake-500-c00.asm)
- Runnable domain: [files/AUTOMAKE-500-C00.DOM](files/AUTOMAKE-500-C00.DOM)

## Input & output files, FAQ, common errors (added 2026-09-11)

General MON-call background for every ND-500 DOM program: see the central reference
`E:\Dev\Ronny\ND500UC\docs\DOM-PROGRAM-IO-REFERENCE.md`. This section applies that reference to
AUTOMAKE-500-C00 specifically.

**Ships incomplete here.** Our local install is only the single `:DOM` file. The DOM's own
strings show it looks for a default rules file matching the pattern `AUTO-RULES-?-???` (the `?`
are wildcard/blank characters, not a literal name), so it expects at least one external rules
file that this bundle does not carry. **CORRECTION 2026-09-11:** the earlier draft of this
section stated a specific ships-as-"FOUR files" count and a specific rules-file name
(`AUTO-RULES-5:MAKE`) — no source in this repo supports either the file count or the "5"; both
have been removed. [measured via `strings` on `files/AUTOMAKE-500-C00.DOM`, 2026-09-11] So most
of what follows about actually MAKE-ing a target is read from the DOM's own embedded
strings/disassembly, not exercised end to end. [from disasm; see "Requirements" above]
No local copy of the vendor manual (ND-60.232) exists in any corpus we hold, so nothing below
claiming to be the command set can be checked against the manual — only against the binary.
[from disasm]

### Input

- Like every ND-500 DOM, AUTOMAKE reads via `INBT` (MON 1B): device 0 is the command buffer
  (text on the same line as the command name), device 1 is the interactive terminal. [doc,
  `DOM-PROGRAM-IO-REFERENCE.md` section 3]
- **Interactive is the only form actually observed.** Every run so far — the 2026-07-31
  load-sweep and the 2026-09-04/09-09 harness runs — started AUTOMAKE bare and it printed its
  banner (`April 27, 1987`) then reached and PARKED on an interactive prompt, observed in
  corpus701 as `Target name:`. [verified/measured]
- No command-line one-shot form has been exercised for AUTOMAKE in this repo. Given the MON 1B
  device-0/device-1 rule that CONVERT-DOM-A03 confirms, putting the relevant arguments on the
  same line as the start command (for example a `MAKE <file> <target> <output>` line) would be
  expected to skip the interactive prompt for that command, by analogy — but this is
  **[inferred]**, not measured for AUTOMAKE itself.
- **Do not send EXIT too early.** BUGS.md's "THE HEADLINE NUMBER" re-measurement (2026-09-09,
  the `corpus701` macro-round logs — NOT the older, differently-worded `run311` row from the
  2026-09-04 table further down the same file) recorded AUTOMAKE reaching its banner and the
  `Target name:` prompt, but the scripted `EXIT` had already been consumed by an earlier read
  in the harness's input queue, so the process parked on the next read instead of leaving
  cleanly and never reached `MON 0B`. This is the SAME failure shape as CONVERT-DOM-A03's
  entry, and the same fix applies: answer each prompt in order and put `EXIT` after the last
  one, not folded in. [measured, `E:\Dev\Ronny\ND5000UC\BUGS.md` line 48]
- The 2026-09-04 raw run (BUGS.md "kept for the record" table, run311) shows the console output
  as `April 27, 1987` only — a fragment of the version banner — while the trail recorded 14
  `MON 2B OutByte` and 2 `MON 162B OutString` calls, meaning more text was PUSHED than what
  reached the visible console capture at that time. Whether that was lost text or genuinely
  empty calls was left `[UNMEASURED]` in BUGS.md B9 and is superseded by the later corpus701
  run showing the fuller banner and prompt — read `BUGS.md` "THE HEADLINE NUMBER" table before
  trusting the older B9 entry on its own. [measured, BUGS.md B9 and headline table]
- Documented prompts embedded in the DOM, beyond `Target name:`: `Automake file:`,
  `Destination:`, `Input file:`, `Identifier:`, `Add own user name (<On/Off>):`, `Expand file
  names (<On/Off>):`, and a target-CPU selector `100/500/68000:`. [from disasm]

### Output

- AUTOMAKE's own MAKE step does not write files directly for most targets — it EXECUTES other
  commands (typically a compiler, then LINKER-B01) that do the actual compiling/linking and
  file writing. So AUTOMAKE's own file-output footprint is mainly the artifacts named by
  `COPY-REQUIRED`/`LIST-REQUIRED`/`GENERATE-AUTOMAKE-FILE`, plus whatever the driven tools
  produce. [from disasm]
- `GENERATE-AUTOMAKE-FILE <Input file> <Automake file> <Own username> <Expand>` writes a new
  automake (rules) file from an input file — this is the one command that is itself a direct
  file-creation step. [from disasm]
- `LIST-REQUIRED <Automake file> <Target name> <Output file>` and `COPY-REQUIRED <Automake
  file> <Target name> <Destination>` both name an explicit output/destination — expect the same
  SINTRAN create-on-write convention as every other DOM program: **an unquoted open on a name
  that does not exist fails; use the double-quoted create form or pre-create the target with
  `@CREATE-FILE` first.** [doc, `DOM-PROGRAM-IO-REFERENCE.md` section 4 — not independently
  re-verified for AUTOMAKE's own OPEN calls, since no live MAKE has been run through it]
- No live build has gone through AUTOMAKE in this repo, so the exact MON call sequence for its
  own file creation (which of 50B/257B/513B it uses, in what order) is NOT measured here —
  unlike CONVERT-DOM-A03, where the FOPEN→OPEN pair is confirmed by decoding the disassembly at
  specific addresses. [open item]

### Good to know

- AUTOMAKE targets THREE CPU families from one tool — the prompt string `100/500/68000:` shows
  it can drive builds for ND-100, ND-500, and Motorola 68000 targets, not only ND-500. [from
  disasm]
- Building a FORTRAN target through AUTOMAKE is blocked by the same missing FORTRAN-LIB /
  EXCEPT-LIB runtime library gap documented in `../README.md` — this is a toolchain
  installation gap, not an AUTOMAKE defect. C targets have a working toolchain and are
  unaffected. [from disasm, cross-referenced to README.md]
- The rules-file mini-language (`if/elsif/else/endif`, `head`/`tail`, `include`,
  `search-order`, `in`-scoped macro assignment) is real and has real error text embedded
  (`Dependency statements are not allowed in the rulesfile.`), but its exact grammar is not
  verified here — read `analysis/automake-500-c00.asm` directly before writing a rules file by
  hand. [from disasm]
- `EXECUTION-MODE` (Execute/Unconditional/Touch/List/Off) is the make-style "dry run" control —
  `List` should show what would run without doing it, `Touch` should just update timestamps,
  `Off` disables the step — but which is the DEFAULT mode has not been observed live.
  [from disasm; default unverified]

### FAQ

- **Q: AUTOMAKE printed its date banner and then stopped. Is it broken?**
  A: No — it reached its interactive `Target name:` prompt and is waiting for terminal input
  (device 1). This is the SAME "silence looks broken but isn't" trap documented for
  CONVERT-DOM-A03 and CODE-COVERAGE. [measured, BUGS.md headline table]
- **Q: My scripted `EXIT` didn't end the session.**
  A: The same input-queue-consumption bug as CONVERT-DOM-A03: an earlier prompt likely ate it.
  Make sure you have answered every prompt AUTOMAKE actually asks (it may ask more than one
  before it is ready to accept EXIT) and put `EXIT` last. [measured, BUGS.md run311]
- **Q: Where do I get the rules file AUTOMAKE looks for?**
  A: Not shipped in this bundle. The DOM's own strings show it defaults to a name matching
  `AUTO-RULES-?-???` (see the correction under "Ships incomplete here" above — the specific
  file count and exact name once written here were unsupported and have been removed); only the
  `:DOM` is installed here, so a real MAKE run needs a rules file sourced/created separately
  before it can do useful work. [measured via `strings`, 2026-09-11]
- **Q: Can AUTOMAKE build FORTRAN programs?**
  A: The command exists, but the run will fail for FORTRAN specifically because the
  FORTRAN-LIB/EXCEPT-LIB runtime library is not installed in this environment — see
  `../README.md`. C targets are fine. [from disasm/README.md]

### Common errors and how to fix them

| Symptom | Cause | Fix |
|---|---|---|
| Only the date banner (`April 27, 1987`) prints, then silence | Program reached an interactive prompt (`Target name:` or similar) and is waiting on device 1 | Answer the actual prompt text; don't treat silence as a hang [measured] |
| Session parks after `Target name:`, `EXIT` never lands | Scripted `EXIT` was consumed by an earlier prompt in the input queue | Recount how many prompts AUTOMAKE actually issues before your script's answers run out; queue `EXIT` after the last real answer [measured, BUGS.md run311] |
| `MAKE` on a FORTRAN target fails partway through the compile step | Missing FORTRAN-LIB / EXCEPT-LIB runtime library, not an AUTOMAKE bug | Install the FORTRAN runtime library per `../README.md`, or build a C target instead [from disasm] |
| "Dependency statements are not allowed in the rulesfile." or "`Else` must be preceded by `if ... then`." | A hand-written or generated `AUTO-RULES` file violates the rules-file grammar | Fix the rules file syntax; consult `analysis/automake-500-c00.asm` for the exact accepted grammar since no vendor manual is available locally [from disasm] |
| `LIST-REQUIRED`/`COPY-REQUIRED` output/destination file fails to open | Unquoted open-for-write on a name SINTRAN will not auto-create (inferred from the general DOM convention, not yet confirmed for AUTOMAKE's own OPEN calls) | Pre-create the destination with `@CREATE-FILE`, or use the double-quoted create form if AUTOMAKE's own OPEN uses one [doc/inferred] |
