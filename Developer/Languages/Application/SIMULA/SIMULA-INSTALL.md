# Installing TPH SIMULA from floppy ND-10058O

How to install and set up the SIMULA compiler on SINTRAN III, fresh or as an upgrade. Back to the
index: [README.md](README.md).

> **Nothing here has been run.** The steps come from the install mode file on the floppy
> (`DRC-LOAD-O:MODE`, quoted in full below), the SIMULA manual ND-60.092.03, the product sheet
> ND-10058-D1 and the SINTRAN III Reference Manual ND-60.128.5. Untested points are marked.

## Short answer: yes, it is a reentrant subsystem

The compiler is installed as a **reentrant subsystem called `SIMULA`**: one shared copy of the code
on a segment, used by every terminal at once. The install file does it with
`@DUMP-REENT SIMULA 0 0 (ND-10058:SYSTEM)N10-SIMULA:BPUN` (start and restart address 0). The manual
says the same: the compiler "executes as a reentrant subsystem under the SINTRAN III/VS operating
system, whereby many active users share common code" (ND-60.092.03 1.1, p.12), and
`N10-SIMULA:BPUN` is "usually made reentrant under the name SIMULA" (1.3, p.15). The product sheet
says a **54-page segment** must be free on a system segment file for it (ND-10058-D1 p.2).

Users then start it by typing `@SIMULA`, or any unique short form such as `@SIM`
(ND-60.092.03 ch. 7, p.33). A reentrant subsystem is found by `@RECOVER` before `:PROG` files are
searched (ND-60.128.5, @DUMP-REENTRANT, p.136).

The product sheet also mentions a non-reentrant form, `SIMULA:PROG` (ND-10058-D1 p.2). The floppy
has no such file, so that form is not covered here.

## The files on the floppy

All in user `SYSTEM` on the floppy directory `ND-10058`. Every name ends in `-O`, which looks like a
release letter. Descriptions from ND-60.092.03 1.3 p.15, ND-10058-D1 p.2 and the binary analysis.

| file on floppy | what it is | installed by DRC-LOAD? |
|---|---|---|
| `N10-SIMULA-O:BPUN` | The compiler with its loader. Banner "TPH SIMULA (SINTRAN III) level 4", build stamp 83-09-12 14:39 (binary analysis). Made into the reentrant subsystem `SIMULA`. | yes, by `@DUMP-REENT` (stays on the floppy as a file) |
| `SIMRT3-O:SIM` | run-time library: the non-standard library routines | yes |
| `SIMBASE3-O:SIM` | definition of DirectFile | yes |
| `SIMSET3-O:SIM` | the SIMSET class | yes |
| `SIMULA3-O:SIM` | the SIMULATION class | yes |
| `SIMRAND3-O:SIM` | random drawing routines | yes |
| `SIMMAT-O:SIM` | mathematical library | yes |
| `SIMERR-O:DATA` | run-time error message texts (68 messages, plain ASCII) | yes |
| `SIMERC-O:DATA` | compiler error message texts (140 messages, plain ASCII) | yes |
| `S-LOAD-O:PROG` | loader for big `:PROG` programs. The manual calls it `S-LOAD-DUAL:PROG` (p.15, p.35); the product sheet calls it the "two bank :PROG file loader" (p.2). That the floppy's `S-LOAD` is the same program is my reading of the names, not checked. | yes |
| `SIMDEBUG-O:PROG` | run-time system with the interactive debugger (binary analysis). Not in the 1980 manual. See [SIMULA-DEBUGGING.md](SIMULA-DEBUGGING.md) section 5. | yes |
| `DRC-LOAD-O:MODE` | the install mode file | - |
| `UTIL-SCREEN:SIM`, `UTIL-SCREEN-ASM:SIM`, `UTIL-SCREEN-DEB:SIM`, `UTIL-OVERLAY:SIM` | compiled SIMULA libraries (binary, no source). No ND document describes them. Their names suggest screen handling and overlays; **what they hold and how to use them is unknown.** | **no** |

The `:SIM` files are **compiled libraries, not source**: name records followed by BRF code in the
SIMULA format. Only the SIMULA loader can read them; the ND relocating loader cannot
(ND-60.092.03 7.3.1 p.36; ND-10058-D1 p.1).

## What DRC-LOAD-O:MODE does

The whole file, as copied from the floppy (parity bit removed). The last line is cut off in the
file itself.

```
@CC
@CC   DRC-LOAD:MODE
@CC   LOG IN UNDER USER SYSTEM,
@CC   ENTER DIRECTORY ND-10058,
@CC   AND RUN THIS MODE FILE TO REPLACE OLD SIMULA RELEASE BY NEW ONE.
@CC

@DE-FI (SYSTEM)SIMRT3:SIM
@DE-FI (SYSTEM)SIMBASE3:SIM
@DE-FI (SYSTEM)SIMSET3:SIM
@DE-FI (SYSTEM)SIMULA3:SIM
@DE-FI (SYSTEM)S-LOAD:PROG
@DE-FI (SYSTEM)SIMERR:DATA
@DE-FI (SYSTEM)SIMRAND3:SIM
@DE-FI (SYSTEM)SIMERC:DATA
@DE-FI (SYSTEM)SIMMAT:SIM
@DE-FI (SYSTEM)SIMDEBUG:PROG

@CR-FI (SYSTEM)SIMRT3-O:SIM 0
@CR-FI (SYSTEM)SIMBASE3-O:SIM 0
@CR-FI (SYSTEM)SIMSET3-O:SIM 0
@CR-FI (SYSTEM)SIMULA3-O:SIM 0
@CR-FI (SYSTEM)S-LOAD-O:PROG 0
@CR-FI (SYSTEM)SIMERR-O:DATA 0
@CR-FI (SYSTEM)SIMRAND3-O:SIM 0
@CR-FI (SYSTEM)SIMERC-O:DATA 0
@CR-FI (SYSTEM)SIMMAT-O:SIM 0
@CR-FI (SYSTEM)SIMDEBUG-O:PROG 0

@COPY-FILE (SYSTEM)SIMRT3:SIM      (ND-10058:SYSTEM)SIMRT3:SIM
@COPY-FILE (SYSTEM)SIMBASE3:SIM    (ND-10058:SYSTEM)SIMBASE3:SIM
@COPY-FILE (SYSTEM)SIMSET3:SIM     (ND-10058:SYSTEM)SIMSET3:SIM
@COPY-FILE (SYSTEM)SIMULA3:SIM     (ND-10058:SYSTEM)SIMULA3:SIM
@COPY-FILE (SYSTEM)S-LOAD:PROG     (ND-10058:SYSTEM)S-LOAD:PROG
@COPY-FILE (SYSTEM)SIMERR:DATA     (ND-10058:SYSTEM)SIMERR:DATA
@COPY-FILE (SYSTEM)SIMRAND3:SIM    (ND-10058:SYSTEM)SIMRAND3:SIM
@COPY-FILE (SYSTEM)SIMERC:DATA     (ND-10058:SYSTEM)SIMERC:DATA
@COPY-FILE (SYSTEM)SIMMAT:SIM      (ND-10058:SYSTEM)SIMMAT:SIM
@COPY-FILE (SYSTEM)SIMDEBUG:PROG   (ND-10058:SYSTEM)SIMDEBUG:PROG

@DELETE-REENT SIMULA
@DUMP-REENT SIMULA 0 0 (ND-10058:SYSTEM)N10-SIMULA:BPUN

@CC   REMEMBER TO REPLACE SAVED SIMULA:BPUN FILE FROM (ND-10058:SYSTEM)N10-SIMUL
```

Step by step:

1. **`@DE-FI`** (DELETE-FILE) removes the ten files of the old release from user SYSTEM. On a fresh
   machine these files do not exist and each line will report an error; I do not know whether a
   mode file stops on that error - **untested**.
2. **`@CR-FI ... 0`** (CREATE-FILE) makes ten new, empty files with the `-O` name. The `0` is the
   size argument; I have not checked what 0 means for this command.
3. **`@COPY-FILE destination source`** copies each file from the floppy. Note the names: the mode
   file writes `SIMRT3:SIM`, not `SIMRT3-O:SIM`. SINTRAN accepts a short form of a file name when
   it is unique, so `SIMRT3:SIM` here should match the `SIMRT3-O:SIM` just created (on the
   destination side) and the floppy's `SIMRT3-O:SIM` (on the source side). **This is my reading of
   why the names differ; it is not tested.** It means the installed files are called
   `SIMRT3-O:SIM` and so on, and the compiler finds them by their short names.
4. **`@DELETE-REENT SIMULA`** removes the old subsystem: "The segment where the reentrant subsystem
   resides is cleared, as well as the corresponding entry in the reentrant subsystem table"
   (ND-60.128.5 @DELETE-REENTRANT, p.86). Only user SYSTEM may do it. On a fresh machine there is
   nothing to delete.
5. **`@DUMP-REENT SIMULA 0 0 (ND-10058:SYSTEM)N10-SIMULA:BPUN`** (DUMP-REENTRANT) reads the
   compiler from the `:BPUN` file, loads it onto a segment with the RT loader and enters the name
   `SIMULA` in the subsystem table. Format: `<name>,<start address>,<restart address>,<binary file>
   [,<segment name>]`; start and restart are octal, default 0 (ND-60.128.5 @DUMP-REENTRANT, p.136).
   Here both are 0. Only user SYSTEM may do it, and it sets a protect flag on the segment.
6. The last line reminds you to replace a saved copy called `SIMULA:BPUN` (if your site keeps one)
   with the new `N10-SIMULA` file. The text is cut off at "N10-SIMUL".

## Fresh install, step by step

Log in as **SYSTEM**. The floppy must be entered as directory `ND-10058` (the name the mode file
uses).

```
@ENTER-DIRECTORY ND-10058,<floppy unit>,...
@MODE (ND-10058:SYSTEM)DRC-LOAD:MODE,,
```

The exact `@ENTER-DIRECTORY` parameters depend on your floppy unit and are not given here. The
`@MODE` line follows the usual SINTRAN form; the second parameter (where the output goes) is left
default - **untested**.

On a fresh machine expect error messages from the ten `@DE-FI` lines and from
`@DELETE-REENT SIMULA` (nothing to delete). If the mode file stops on the first error, do the steps
by hand instead: skip the `@DE-FI` and `@DELETE-REENT` lines and type the `@CR-FI`, `@COPY-FILE`
and `@DUMP-REENT` lines yourself.

Then do the memory set-up below.

## Upgrade from an older release

Same as a fresh install. The mode file is written for exactly this: "run this mode file to replace
old SIMULA release by new one". Make sure nobody is using SIMULA while `@DELETE-REENT SIMULA` runs
(my precaution; the manuals do not say what happens to a user who is in the compiler at that
moment).

**After an upgrade, recompile every separately compiled SIMULA library.** "Each new Simula release
invalidates all >BRF produced files, but will not, of course, affect >BIN files"
(ND-60.092.03 4.1, p.24). The compiler reports old ones as
`EXTERNAL MODULE COMPILED WITH OBSOLETE SIMULA RELEASE` (App. C p.49). `:PROG` and `:BIN` programs
keep working.

## Memory and segment size set-up

SIMULA needs **128K words of virtual memory per user**. The standard SINTRAN set-up gives less, so
`@CHANGE-BACKGROUND-SEGMENT-SIZE` "has to be executed for each terminal that is to be allowed use
of SIMULA compiler or programs" (ND-60.092.03 1.3, p.15). The product sheet: "the compiler uses
the additional page-index-table, and requires a background segment of 128 Kwords. This can be set
for single or all terminals/batch processors" (ND-10058-D1 p.2).

The command (ND-60.128.5 @CHANGE-BACKGROUND-SEGMENT-SIZE, p.40):

```
@CHANGE-BACKGROUND-SEGMENT-SIZE <segment>,<no. of pages>
```

- `<segment>`: the segment number or name of a background segment (one per terminal or batch
  processor).
- `<no. of pages>`: 128 or 64 (decimal); default 128. SIMULA needs 128.
- Only user SYSTEM. It **must be run after `@INITIALIZE-BACKGROUND-PROGRAMS`**. If the segment file
  has no room for 128, SINTRAN quietly falls back to 64.

ND's example sets segment 250 to 64 pages: `@CHANGE-BACKGROUND-SEGMENT-SIZE 250,64`.

Because it must follow `@INITIALIZE-BACKGROUND-PROGRAMS`, the setting belongs in the commands the
machine runs at every start-up, one line per terminal that should use SIMULA. **Which background
segment number belongs to which terminal on your system is not known here**; it depends on the
system generation.

If the segment is too small, the binary analysis found the text `@CH-B-S-S ,128 IS MISSING` in
SIMULA - that is the message you should expect. When exactly it is printed is not known.

Other needs:

| need | value | source |
|---|---|---|
| physical memory | at least 96K words in most set-ups | ND-60.092.03 1.3 p.15; ND-10058-D1 p.2 |
| working set | up to 123K words depending on program size; normal 10-16 pages | ND-60.092.03 p.15; ND-10058-D1 p.1 |
| disk space | about 100 pages | ND-10058-D1 p.2 |
| segment for the subsystem | 54 pages on a system segment file | ND-10058-D1 p.2 |
| file access | the library and message files must be readable by public users | ND-10058-D1 p.2 |
| scratch file | the compiler uses the system scratch file | ND-10058-D1 p.1 |

The file access point: the files are created under SYSTEM. Whether `@CREATE-FILE` gives them public
read access by default on your system is not known; check with `@LIST-FILES` / `@FILE-STATISTICS`
and set it with `@SET-FILE-ACCESS` if needed. **Untested.**

## Checking it worked

None of this has been done; these are the checks I would use.

1. `@LIST-REENTRANT` should show `SIMULA` (the command lists reentrant subsystems,
   ND-60.128.5 command table).
2. `@LIST-FILES (SYSTEM)SIM` should show the nine `SIM...` files, and `(SYSTEM)S-LOAD` the loader.
3. Log in as an ordinary user on a terminal with the 128-page segment and type `@SIM`. The banner
   with the version and the `>` prompt should appear (ND-60.092.03 7.1, p.33).
4. Compile and run the smallest program: put
   `BEGIN OutText("hello"); OutImage; END` in `HELLO:SYMB`, then

   ```
   @SIM
   >SETOPT V
   >COMPILE HELLO
   ```

   Expect `LOADING PROGRAM`, `Ready for Simula execution`, `hello`, then `CPU seconds used:` and
   `Exit Simula` (ND-60.092.03 7.1, p.33-34).
5. Compile a program prefixed with `SIMULATION` - this proves the class libraries are found.
6. Make a run-time error on purpose (for example `OutFix(Sqrt(-1.0), 2, 8)`, which should give `Illegal parameter to SQRT`) and check that a message text
   appears; that proves `SIMERR:DATA` is read.

## Not known

- Whether the mode file stops at the first error on a fresh machine.
- What the `0` in `@CR-FI ... 0` does here.
- Whether the short-name matching in the `@COPY-FILE` lines works as described.
- What the four `UTIL-*:SIM` libraries contain and how to install or use them.
- Why the run-time asks for `SIM-DEBUG:PROG` while the installed file is `SIMDEBUG:PROG`
  (see [SIMULA-DEBUGGING.md](SIMULA-DEBUGGING.md) section 5).
- Which background segment belongs to which terminal on a given system.
