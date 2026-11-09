# The SIMULA compiler: compile, load, run

How to drive the TPH SIMULA compiler on SINTRAN III. Back to the index: [README.md](README.md).

> **Not run on a live machine.** Everything here is from ND-60.092.03 chapter 7 and the product
> sheet ND-10058-D1. The floppy's compiler is newer (level 4, 1983) than the manual (4.017, 1980).

## 1. Fastest path: compile and go

Write the source with QED (or any editor) into a `:SYMB` file, for example `PROGRAM:SYMB`. No line
may start with `%` unless it is meant as a compiler command (ND 7.1 p.33).

```
@SIM
TPH SIMULA 4.017
>SETOPT VS
>LIST L-P
>COMPILE PROGRAM
```

(ND 7.1, p.33.) What happens:

- `@SIM` starts the reentrant subsystem `SIMULA` (short form of the name). The compiler prints its
  version and the `>` prompt.
- `SETOPT VS`: V = run the program after compiling, S = source listing.
- `LIST L-P`: listing to the line printer (`L-P` is SINTRAN's printer name in the manual's
  example).
- `COMPILE PROGRAM`: compile `PROGRAM:SYMB`. If there are no errors the compiler prints
  `LOADING PROGRAM`, then `Ready for Simula execution`, and the program runs. At the end:

```
CPU seconds used:   5.017
Exit Simula
```

(ND 7.1, p.33-34.) Input typed to the program is passed on only after carriage return.

**Only one `>COMPILE` or `>LOAD` per session.** After it the compiler exits by itself unless the
program runs (ND 7.3.1 p.35).

ND's complete worked session, including a compile error and its fix, is Appendix A (p.41-43). The
error looks like this:

```
TPH SIMULA (SINTRAN III) LEVEL 4 ED 011

00001 BEGIN
00002     OUTINT(ININ+ININ+ININ+ININ,10);
00003     END;

*** LINE 00002     ERROR: MISSING DECLARATION OF ININ ***
ERROR MESSAGES GIVEN: 00001
```

## 2. The commands

Every command is typed at the `>` prompt. **Commands cannot be abbreviated** (ND ch. 7 p.33).
Where a file name is asked for, the number of an already open file can be given instead
(ND 7.3.1 p.36).

| command | what it does | default file type | source |
|---|---|---|---|
| `>SETOPT cccc` | add 1 to each compiler option letter in cccc. An option is on when above zero; all start at 0. | - | ND 7.3.1 p.34 |
| `>RESOPT cccc` | subtract 1 from each option in cccc | - | ND 7.3.1 p.34 |
| `>RTS dddd` | set run-time options in dddd to TRUE (section 4 of [SIMULA-DEBUGGING.md](SIMULA-DEBUGGING.md)). The product sheet shows `>RTSO` for "pre-execution conversation". | - | ND 7.3.1 p.34; ND-10058-D1 p.2 |
| `>LIB file` | add a library of separately compiled code to search for EXTERNAL names. Any number; the latest is searched first. | SIM | ND 7.3.1 p.35 |
| `>ASM file` | write the object code as symbolic assembly (mainly for testing; needs option G) | SYMB | ND 7.3.1 p.35 |
| `>BRF file` | write relocatable code - used to build libraries; a main program can also be saved this way and later `>LOAD`ed | SIM | ND 7.3.1 p.35 |
| `>BIN file` | write absolute code in ND-100 hardware format; run it with `@PLACE file:BIN` then `@GO 0` | BIN | ND 7.3.1 p.35 |
| `>PROG file` | write absolute code in SINTRAN `@DUMP` format. **The recommended way to save a program.** | PROG | ND 7.3.1 p.35 |
| `>LIST file` | listing, with error messages | SYMB | ND 7.3.1 p.35 |
| `>RUNOFF file` | documentation output, made instead of code when option M is set | SYMB | ND 7.3.1 p.35 |
| `>COMPILE file` | compile; source from the terminal if no file (in batch: the batch input). Stops at end of file or `%EOF`. With option V and no errors, runs the program. | SYMB | ND 7.3.1 p.35 |
| `>LOAD file` | load relocatable code; with option V run it. The result can also go to a `>BIN` or `>PROG` file. | SIM | ND 7.3.1 p.35 |
| `>EXIT` | back to SINTRAN | - | ND 7.3.1 p.36 |
| `>DATA ...` | **not documented.** The binary analysis found `DATA` among the command names, and one compile error says `SYMBOL TABLE TOO LARGE - TRY SMALLER >DATA PARAMETER` (App. C p.49). What its parameter means is unknown. | - | App. C p.49 |

The binary analysis of the floppy's compiler reported the command names `SETOPT`, `RESOPT`, `LIST`,
`COMPILE`, `RUNOFF`, `EXIT`, `LOAD`, `DATA`. Whether `LIB`, `ASM`, `BRF`, `BIN`, `PROG` and `RTS`
are also in that binary was not part of that report - **not confirmed for the floppy version.**

## 3. Compiler options

Set with `>SETOPT`, cleared with `>RESOPT`, or from inside the source with `%SETOPT` / `%RESOPT`
(section 6). Because options are counters, a source section can do `%SETOPT A` ... `%RESOPT A` and
the outside setting still decides (ND 2.2 p.16).

| option | meaning (ND 7.3.2 p.36-37) |
|---|---|
| A | do not check array bounds at run time |
| D | write a debugging symbol table (needed for `*VAR` and `*OBJECT` names) |
| E | separate compilation of a library. **Not in the option table**; mentioned in ND 4.1 p.24 ("E-option compilation") and App. E p.53 ("When Z option is set, E option is necessary to signal a separate compilation"). |
| F | BEGIN/END flags shortened in the left margin; FF removes them |
| G | write symbolic code to the `>ASM` file |
| I | no line numbers in the code (the debugger and error messages then cannot name lines - my reading) |
| K | stop at the first error |
| L | list every input line, including `%` commands |
| M | make a RUNOFF document instead of compiling |
| N | no overflow check on multiply; `>RESOPT N` checks add and subtract as well |
| O | on-line debugging (see [SIMULA-DEBUGGING.md](SIMULA-DEBUGGING.md)) |
| Q | no qualification checks |
| R | no NONE checks |
| S | source listing, without `%` commands and without lines they skipped |
| T | print time and space used after compiling |
| U | upper and lower case in names are different |
| V | run the program after compiling (compile and go) |
| W | no warning messages |
| X | experimental, for system maintenance only - do not use |
| Y | print the loader map |
| Z | Zimula, the extended language (LITERAL, XOR, QUICK, ENTRYPOINT, INLINE) |

There are also some non-letter options for system maintenance, described only in internal ND
documents (ND 7.3.2 p.37).

## 4. The listing and compile errors

The listing comes from `>LIST` plus option S (or L). It has a banner like
`TPH SIMULA (SINTRAN III) LEVEL 4 ED 011`, the source with five-digit line numbers, and errors
(ND App. A p.42).

- **Syntax errors** appear in the listing under the line.
- **Semantic errors** come at the end, by line number (ND 7.3.3 p.37).
- Format: `*** LINE 00002     ERROR: MISSING DECLARATION OF ININ ***`, and at the end
  `ERROR MESSAGES GIVEN: 00001` (App. A p.42).
- Warnings say `WARNING:` instead of `ERROR:` (App. C p.49). Option W hides them.

The full list of compile messages is in ND App. C p.47-49 (the binary analysis counted 140 texts in
`SIMERC:DATA`). The ones you will meet most, in plain words:

| message | meaning |
|---|---|
| `MISSING DECLARATION OF ...` | a name is used but not declared (or misspelt) |
| `DOUBLE DECLARATION OF ...` | the same name declared twice in one block |
| `WRONG TYPE, I EXPECTED TO SEE ...` | an expression of the wrong type |
| `INCOMPATIBLE TYPES IN EXPRESSION, ASSIGNMENT, OR PARAMETER` | same, in an assignment or call |
| `WRONG NUMBER OF PARAMETERS TO ...` | call does not match the declaration |
| `MISSING SPECIFICATION OF ...` | a parameter has no type line |
| `NO ATTRIBUTE CALLED ...` | `x.name` where the class has no `name` |
| `NOT REFERENCE BEFORE DOT` | a dot after something that is not an object reference |
| `UNKNOWN OR CIRCULAR PREFIX: ...` | prefix class not found, or classes prefix each other |
| `THIS PROGRAM HAS EXTRA BEGIN OR MISSING END` | unbalanced BEGIN/END |
| `SERIOUS SYNTAX ERROR - REST OF STATEMENT IGNORED` | the parser gave up on the statement |
| `NO SPACE IN BLOCK OBJECT FOR THE VARIABLE ...` | the block's data passed 512 words |
| `PROGRAM WAS TOO LARGE FOR COMPILER STORAGE - COMPILATION ABORTED` | split the program (section 5) |
| `NO LIBRARY FILE DEFINES ...` | an EXTERNAL name was not found in any `>LIB` file |
| `EXTERNAL MODULE COMPILED WITH OBSOLETE SIMULA RELEASE` | recompile the library with this compiler |
| `SHORT/LONG HAS NO EFFECT IN THIS IMPLEMENTATION` | warning: `LONG REAL` is the same as `REAL` |
| `LARGE INTEGER CONSTANT CONVERTED TO REAL` | warning: constant does not fit 16 bits |

ND says "some of these messages may be obsolete, thus impossible to evoke" (App. C p.49).

## 5. Separate compilation and libraries

A source file with **only class and procedure declarations, no main program**, compiles to a
**library** instead of a program (ND 4.2 p.24). Write it with `>BRF`; use it with `>LIB`.

Library source, `SHAPES:SYMB`:

```simula
CLASS Shapes;
BEGIN
   CLASS Circle(R); REAL R;
   BEGIN
      REAL PROCEDURE Area; Area := 3.14159 * R * R;
   END;
END;
```

Build it:

```
@SIM
>BRF SHAPES
>COMPILE SHAPES
```

This writes `SHAPES:SIM`. (ND 4.1 p.24 speaks of an "E-option compilation" for libraries; whether
`>SETOPT E` is needed without option Z is not clear from the manual - App. E p.53 only says it is
needed with Z. Try without first.)

Use it from a main program, `MAIN:SYMB`:

```simula
Shapes BEGIN
   REF(Circle) C;
   C :- NEW Circle(2.0);
   OutFix(C.Area, 3, 10);
   OutImage;
END
```

```
@SIM
>LIB SHAPES
>SETOPT V
>COMPILE MAIN
```

A name used as a prefix and not declared is taken as `EXTERNAL CLASS` automatically - that is how
`SIMSET` and `SIMULATION` work (ND 4.1 p.23). Other names need an explicit declaration:

```simula
EXTERNAL CLASS Shapes;
EXTERNAL PROCEDURE Operate, Check;
```

Rules (ND 4.1-4.2, p.23-25):

- The compiler searches the system libraries first, then the `>LIB` files, newest first. It reads
  the parameters and attributes from the library, so everything is checked as if declared in the
  program.
- **When a library changes, recompile everything that uses it,** then everything that uses those,
  up to the main program. ND will not look at a fault report unless all sources were recompiled.
- **A new SIMULA release makes all `>BRF` files invalid.** `>BIN` (and `>PROG`) files are not
  affected.
- Using an external class on a different block level than the one it was compiled for works, but
  runs about 50% slower.
- Library files have type `:SIM` and are **not compatible** with other ND software, because they
  hold SIMULA attribute data (ND 7.3.1 p.36).
- With option Z, every declaration that should be visible outside must start with `ENTRYPOINT`
  (before `QUICK` if both) (App. E p.53).

FORTRAN and assembly procedures are also linked through `>LIB`; see
[SIMULA-LANGUAGE-GUIDE.md](SIMULA-LANGUAGE-GUIDE.md) section 21.

## 6. Precompiler commands in the source

Lines that start with `%` in column one are read by the precompiler before the compiler sees the
text (ND ch. 2, p.16-18). `%` followed by a space is ignored.

| command | effect |
|---|---|
| `%SETOPT cccc` / `%RESOPT cccc` | same as `>SETOPT` / `>RESOPT` |
| `%SET flag` / `%RESET flag` | set a flag TRUE / FALSE. Flags are a separate name space; an unknown flag is FALSE. |
| `%IF flag` ... `%ELSE flag` ... `%FI flag` | conditional compilation |
| `%EOF` | end of the source (the only way to end source typed at the terminal) |
| `%COMPILE file` | include another source file here (can nest) |

```simula
%SET TESTING
BEGIN
%IF TESTING
   OutText("test build");
%ELSE TESTING
   OutText("real build");
%FI TESTING
   OutImage;
END
```

Rules (ND 2.3 p.17-18): `%IF` with a false flag skips to `%ELSE` or `%FI` of the same flag;
`%ELSE` with a true flag skips to `%FI`; a `%FI` on its own is ignored. Nesting is allowed when the
inner one uses a different flag. ND's "A or B" trick:

```
%ELSE A
%IF B
%FI A
   OutText("This is version A or B");
   OutImage;
%FI B
```

The manual's `>COMPILE` text says compilation stops at "the $EOF macro command" (7.3.1 p.35); the
precompiler chapter calls it `%EOF` (2.4 p.18). `%EOF` is the one used here.

## 7. Saving and running a program

**Recommended: `>PROG`** (ND 7.2 p.34):

```
@CREATE-FILE BINSIM:PROG 0
@SIM
>PROG BINSIM
>SETOPT V
>COMPILE PROGRAM
```

The file `BINSIM:PROG` must exist first (ND 7.2 p.34). The `0` in `@CREATE-FILE` makes an empty
indexed file in the usual SINTRAN way - not checked for this case. Later runs:

```
@BINSIM
```

**Big programs.** If the program is too big for one bank, the compiler says so, and it must be
started with the two-bank loader: `@S-LOAD-DUAL BINSIM` (ND 7.3.1 p.35). The floppy ships this
loader as `S-LOAD-O:PROG`; the command name on an installed system may therefore be `@S-LOAD`
(by short name matching) - **not checked**.

**`>BIN`:** `@PLACE file:BIN` then `@GO 0` (ND 7.3.1 p.35).

**From a library file:** `>LOAD file` with option V runs relocatable code saved with `>BRF`.

## 8. Batch jobs

The compiler reads the batch input as its terminal; `>COMPILE` with no file reads the source from
the batch stream (ND 7.3.1 p.35). ND's batch example (App. A p.41, OCR "SETOFT" corrected to
"SETOPT"):

```
@ENTER TPH,,,60
@SIM
SETOPT SV
COMPILE ADD3
5 50 500
```

Note there is no `>` typed in a batch file; the `5 50 500` line is input for the program itself.

## 9. Memory

Each user of SIMULA needs a 128K-word background segment. Without it the compiler cannot run. See
[SIMULA-INSTALL.md](SIMULA-INSTALL.md), "Memory and segment size set-up".
