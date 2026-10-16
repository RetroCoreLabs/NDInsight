# FORTRAN Developer Guide

**ND FORTRAN for SINTRAN III (ND-100 / NORD-10)**

**Version:** 3.0
**Date:** October 15, 2026
**Status:** Compile and link steps in "Building with the F02 compiler" were run on the nd100x
emulator (SINTRAN III VSX/500 L, compiler `203053F02`). Things not run are marked **[NOT RUN]**.

> There is more than one FORTRAN compiler for this machine, and they do not accept the same
> programs. **For new programs use the newest one (F02).** A program written for the old
> toolchain, with one-bank assembler helpers, builds best with that toolchain (FTN-2090I and the
> old runtime): see [ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md). See
> [Which compiler](#which-compiler). Questions and traps found while building a real program
> are in [FORTRAN-BUILD-LEARNINGS-FAQ.md](FORTRAN-BUILD-LEARNINGS-FAQ.md).

---

## Which compiler

The archive holds five FORTRAN compilers for the ND-100. They are different programs, with
different commands, different runtime libraries and different strictness.

| Compiler | Product | File on the floppy | Banner | How you start it | Compile command |
|---|---|---|---|---|---|
| NORD FORTRAN, 48-bit float | [ND-10023K](../../../Installation/Software/ND-10023/ND-10023K/README.md) | `FTN-2090I:BPUN` (also `FTN-2090H`) | `NORD-10/ND-100 FORTRAN COMPILER FTN-2090I` | dump it reentrant, then `@FTN` | `COMP src,,"obj"` then `EX` |
| ND FORTRAN 77, older article | [ND-10191](../../../Installation/Software/ND-10191/README.md) (A, D, E00) | `FORTRAN-100-E00:PROG` and others | | run the `:PROG` by name | `COMPILE src,,"obj"` |
| **ND FORTRAN 77, newest** | [ND-210191F02](../../../Installation/Software/ND-210191/ND-210191F02/README.md) | `FORTRAN-100-F02:PROG` | `ND-100/NORD-10 ANSI 77 FORTRAN COMPILER - 203053F02` | run the `:PROG` by name | `COMPILE src,,"obj"` then `EXIT` |
| FORTRAN for ND-500 | [ND-210190](../../../Installation/Software/ND-210190/README.md) | | | ND-500 monitor | not covered here |

**Why the newest one.** The same program text, `ADV-SUBR:SYMB` (1152 lines of ordinary
FORTRAN with `LOGICAL FUNCTION` and `IMPLICIT INTEGER (A-Z)`), gave:

| Compiler | Result |
|---|---|
| FTN-2090I | **11 errors**: `"LOG. EXPR" ILL. ASSIGNMENT`, `"LOG. CONST" ILL. ASSIGNMENT`, `"GOTO22" SYNTAX ERROR` |
| FORTRAN-100-F02 | **1 error**: `NEWHRX DOUBLY DEFINED`, a real mistake in the source (see the FAQ) |

The manual (ND-60.074.01, section 4.10) says an explicit type in a `FUNCTION` statement overrides
`IMPLICIT`. FTN-2090I does not do that. F02 does.

**F02 is stricter about real mistakes.** It reports a missing closing parenthesis and a function
typed twice. FTN-2090I let one of those through. A program that "always compiled" on the old
compiler may need small source fixes for F02.

**The runtime library is part of the compiler.** Objects from one compiler need that compiler's
runtime. F02 objects need `FORT48-1BANK-F02:BRF` or `FORT48-2BANK-F02:BRF`. Old FTN-2090 objects
need `FTNLIBR` / `FTNRTLIBR`. The two families call the runtime by different entry names
(`8ENTR` in the old one, `5ENTR` in F02), so you cannot mix them freely. See the FAQ.

---

## Installing

Every step here was done on a SINTRAN image and read back. All file copies came from the
[Norsk Data Software Archive](https://github.com/RetroCoreLabs/norskdata-software-archive).

### The newest compiler (F02)

Floppy `210191F02-XX-01D` (archive id `nd-210191-f02-d1-5b6a3ad3`, MD5
`5b6a3ad3e72571540755b93d1607ff09`). Its files:

| File | Use |
|---|---|
| `FORTRAN-100-F02:PROG` | the compiler. Already a `:PROG`, **no dump needed** |
| `FORT48-1BANK-F02:BRF`, `FORT48-2BANK-F02:BRF` | runtime for 48-bit floating point |
| `FORT32-1BANK-F02:BRF`, `FORT32-2BANK-F02:BRF` | runtime for 32-bit floating point |

Copy the compiler and the runtime you need into `(SYSTEM)`. The compiler file is **sparse** (655,360
bytes but only 137 pages on disk). Copy it with its holes kept, or the copy is a different file on
disk (same bytes, different layout). With the ndfs Python library:

```python
src_blocks = src.get_file_blocks(path)
holes = [i for i, b in enumerate(src_blocks) if b == 0]
dst.write_file(path, data, "none", holes if holes else None)   # "none" = no parity change
```

Then it runs by name:

```
@FORTRAN-100-F02
ND-100/NORD-10 ANSI 77 FORTRAN COMPILER - 203053F02
FTN:
```

Note the prompt: `FTN:`. It is the F02 compiler's prompt, not the old compiler.

### The old compiler (FTN-2090I) and the dump addresses

`FTN-2090I:BPUN` is a binary, so it must be dumped reentrant before `@FTN` works. The addresses
come from the Program Description sheet for FTN-2090I: **start 0, restart 1**. Source: the sheet
printed in [ND-10033K FORTRAN 32 BITS FLOATING FORMAT](../../../Reference-Manuals/ND-10033K%20FORTRAN%2032%20BITS%20FLOATING%20FORMAT.md).

```
@DUMP-REENTRANT FTN,0,1,FTN-2090I:BPUN
```

It prints **nothing** when it works. If you run it a second time, it answers
`NAME ALREADY USED ON REENTRANT SUBSYSTEM`, which means the first run worked. Check with
`@LIST-REENTRANT`: the line `0B 1B 142B FTN` is the dump. It survives a restart.

Start it with `@FTN`. The banner is `NORD-10/ND-100 FORTRAN COMPILER FTN-2090I` and the prompt is `$`.

### The linker

FORTRAN needs a linker to make a `:PROG`. Two exist: `BRF-LINKER` (product
[ND-210721](../../../Installation/Software/ND-210721/README.md), one file
`BRF-LINKER-C01:PROG`) and the older `NRL`. A plain SINTRAN pack may have **neither** installed:
`@BRF-LINKER` and `@NRL` both answered `NO SUCH FILE NAME` on the SMD0 pack. Copy
`BRF-LINKER-C01:PROG` into `(SYSTEM)` (it is sparse too). It starts as `@BRF-LINKER-C01` with the
banner `- BRF Linker -  210721C01` and the prompt `Brl:`.

### NPL and MAC (only if the program has assembler parts)

Some programs, like the English Adventure, have helper routines written in NPL. Then you also
need `NPL` and `MAC`:

```
@DUMP-REENTRANT NPL,0,1,(BPUN-FILES)NPL-1896D:BPUN     % NPL: start 0, restart 1
@MAC-1628C                                              % MAC runs as a plain :PROG
```

---

## Building with the F02 compiler

### Step by step (run on the emulator)

```
@FORTRAN-100-F02
COMPILE ADV-INIT,,"ADV-INIT"
EXIT
```

Real output from that machine:

```
FTN: COMPILE ADV-INIT,,"ADV-INIT"
- CPU TIME USED: 2.5 SECONDS.  773 LINES COMPILED.
- NO MESSAGES
- PROGRAM SIZE=1641 DATA SIZE=1144 COMMON SIZE=41172
```

`COMPILE source,list,object`:

1. `source`: the file to compile. It exists, so **no quotes**. Default type `:SYMB`.
2. `list`: a listing. Leave it empty (`,,`) for none.
3. `object`: the `:BRF` that is made. It is created, so it needs **"quotes"**.

**If the object file already exists the compiler stops** and prints
`FILE ALREADY EXISTS "NAME"`. Delete the old `:BRF` first.

### Link to a :PROG

```
@BRF-LINKER-C01
PROG-FILE "ADVENTURE"
LOAD ADV-HOVED
LOAD ADV-INIT
LOAD ADV-SUBR
LOAD FORT48-2BANK-F02
EXIT
```

`PROG-FILE "NAME"` sets the output file. It is created, so it needs quotes. `LOAD` takes a `:BRF`
by name, with no quotes. **Load the runtime library last.** Each `LOAD` prints the free space; the
runtime prints `FORTRAN-2BANK-F02 48-BIT FLOATING`.

`EXIT` writes the program. **Read the lines before the next `@` prompt.** If something is not
resolved, the linker prints an `Undefined entries` list and *still writes the `:PROG`*, which will
not run. The file existing is not proof the link worked.

**Programs with assembler helpers.** Helpers written for the old toolchain (they call `8ENTR`,
`8LEAV`, `8RLDN`, `INBT`, `OUTBT`) do not link against the F02 runtime alone: those names are
undefined, and they are one-bank code. The English Adventure is such a program. Two things to know:

1. **Where is a name defined?** Look it up in
   [LINK-LIBRARY-NAME-INDEX.md](../../Workflow/LINK-LIBRARY-NAME-INDEX.md) (every name in every
   `:BRF` library on the archive floppies). `FTNLIBR-2091F` defines all five names. See
   [the FAQ](FORTRAN-BUILD-LEARNINGS-FAQ.md#q-what-are-inbt-and-outbt).
2. **Build such a program with the toolchain it was written for:** FTN-2090I, the old runtime
   `FTNLIBR-2091F` and one bank. Worked example, with every command and message:
   [ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md). With F02 the one-bank
   link does not fit (`Program space exceeded`) and the two-bank layout does not suit one-bank
   helpers.

Pure FORTRAN programs (no assembler helpers) build with F02 as shown above.

### Programs that set up their own data

Some programs read their data once and then expect their memory to be saved as the program (the
Adventure says *"Be sure to save your core image..."*). That is a separate step after the link:
run the program, answer its setup questions, then `@MEMORY 0,177777` and `@DUMP "NAME",0,0`.
See [the Adventure document](ADVENTURE-BUILD-AND-INITIALIZE.md#7-save-the-core-image) and the FAQ.

### Calling MAC, NPL or PLANC routines from F02 FORTRAN (ASSEMBLY)

**[DOC]** ND-60.145.7A section 3.10 and appendix F. This was **not needed** for the Adventure and
was **not tested**. An external routine written in assembler is called with the compiler's
*standard* sequence (parameter list address in A, a stack frame built by `5ENTR`) unless you
declare it:

```fortran
      ASSEMBLY OPEN, GETIN
```

With `ASSEMBLY`, the compiler passes up to **four** arguments, each an `INTEGER*2` value or an
array name, **in registers T, A, D, X** (an array name is the address of its first word). The
return address is `L` + 1. Arguments cannot be changed by the routine unless they are arrays. A
function result comes back as usual for its type. The names must not also appear in an `EXTERNAL`
statement. For compatibility with the 2090 compilers there is also the compiler command
`RESERVE-WORK-SPACE ON` (section 14.27), which keeps 20 octal words free below the frame for
assembler routines.

### Which runtime, 1-bank or 2-bank

The F02 compiler makes separate code and data banks unless you tell it otherwise (the linker's
`FREE:` line shows both `P` and `D` ranges). Use `FORT48-2BANK-F02` for that. A 1-bank program is
made by compiling with `SEP OFF` and linking `FORT48-1BANK-F02`. **[NOT RUN]** on this pack.
See [TWO-BANK-PROGRAMS.md](../../Workflow/TWO-BANK-PROGRAMS.md).

### 48-bit or 32-bit

Pick the runtime that matches the number of bits in a `REAL`. A program that keeps six characters
in a `REAL` (a 3-word `REAL`) is a 48-bit program. A 32-bit `REAL` holds four characters.
Compiled objects do not carry the choice: you decide at link time with `FORT48` or `FORT32`.

### Build in a MODE file

Inside a MODE file each SINTRAN command carries its `@`. Lines for a program (the compiler or
the linker) do not. **Leave the compiler between builds** so that nothing carries over from the
previous run, and delete the old outputs first:

```mode
@DELETE-FILE ADV-HOVED:BRF
@DELETE-FILE ADV-INIT:BRF
@DELETE-FILE ADV-SUBR:BRF
@DELETE-FILE ADVENTURE:PROG
@FORTRAN-100-F02
COMPILE ADV-HOVED,,"ADV-HOVED"
EXIT
@FORTRAN-100-F02
COMPILE ADV-INIT,,"ADV-INIT"
EXIT
@FORTRAN-100-F02
COMPILE ADV-SUBR,,"ADV-SUBR"
EXIT
@BRF-LINKER-C01
PROG-FILE "ADVENTURE"
LOAD ADV-HOVED
LOAD ADV-INIT
LOAD ADV-SUBR
LOAD FORT48-2BANK-F02
EXIT
```

Run with `@MODE ADV-BUILD:MODE,,`. This F02 two-bank example was run line by line; the **MODE
file that was run as one file** is the FTN-2090I one-bank build in
[ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md#5-build-one-mode-file).
For the full Adventure, the F02 version above reports undefined entries for the reason in the
paragraph below.

---

## The older hello-world recipe

The earlier version of this guide gave this build for a machine where the compiler was installed
as `FORT` and the runtime as `FORT-1B`. Those are names someone gave the files at install time; the
floppy calls them `FORTRAN-100-F02:PROG` and `FORT48-1BANK-F02:BRF`. If your machine has both
names, it works; otherwise use the file names above.

```
@FORT
SEP OFF
COMP HELLO,,"HELLO"
EXIT
@BRF-LINKER
PROG-FILE "HELLO"
LOAD HELLO
LOAD FORT-1B
EXIT
@HELLO
```

```fortran
      PROGRAM HELLO
      WRITE(1, 10)
   10 FORMAT(1X, 'HELLO FROM FORTRAN!')
      END
```

Notes that apply to either compiler:

- Fixed form: column 1 `C` = comment, columns 1 to 5 = label, column 6 = continuation, columns
  7 to 72 = code. **A line past column 72 is cut off silently.**
- Unit 1 is the user's terminal on the ND-100.
- `1X` in a `FORMAT` is one blank for carriage control.
- SINTRAN text files have even parity in bit 7. Copy source files between disks byte for byte
  (see the FAQ). Do not convert.

---

## Reference manuals

All under [Reference-Manuals/](../../../Reference-Manuals/):

| Manual | Document # | Covers |
|--------|-----------|--------|
| [ND FORTRAN Reference Manual](../../../Reference-Manuals/ND-60.145.7A%20EN%20ND%20FORTRAN%20Reference%20Manual.md) | ND-60.145.7A EN | ANSI 77 language reference (Sept 1986). Primary manual for F02 |
| [NORD-10 FORTRAN System Reference Manual](../../../Reference-Manuals/ND-60.074.01%20NORD-10%20FORTRAN%20SYSTEM%20Reference%20Manual.md) | ND-60.074.01 | The NORD-10 compiler, `IMPLICIT`, `PARAMETER`, `OPEN` |
| [NORD Standard FORTRAN](../../../Reference-Manuals/ND-60.011.04%20NORD%20Standard%20FORTRAN%20Reference%20Manual.md) | ND-60.011.04 | Original NORD FORTRAN (1974) |
| [Fortran for ND-100 / NORD-10](../../../Reference-Manuals/ND-10191A%20Fortran%20for%20ND-100-NORD-10.md) | ND-10191A | Product note for the F77 compiler |
| [FORTRAN for ND-500](../../../Reference-Manuals/ND-10190D%20FORTRAN%20FOR%20ND-500.md) | ND-10190D | ND-500 |
| [FORTRAN 32 Bits Floating Format](../../../Reference-Manuals/ND-10033K%20FORTRAN%2032%20BITS%20FLOATING%20FORMAT.md) | ND-10033K | The FTN-2090 program description sheets |

---

## Key features

1. **ANSI 77** with ND extensions (`DO WHILE`, long names, bit intrinsics, `ERRCODE`).
2. **Monitor calls** from FORTRAN through `ERRCODE` and the `MONITOR CALL` statement.
3. **Assembler and NPL helpers** can be linked in as `:BRF`, for what FORTRAN cannot do (reading
   a terminal character at a time, for example).
4. **Separate banks** for code and data, so a program can be larger than 64K words.

---

## See also

- **[ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md)**: a complete worked
  build of a real FORTRAN program with assembler helpers, from source to a saved, working `:PROG`
- **[FORTRAN-BUILD-LEARNINGS-FAQ.md](FORTRAN-BUILD-LEARNINGS-FAQ.md)**: what went wrong while
  building a real program, and what each message means
- **[LINK-LIBRARY-ENTRY-POINTS.md](../../Workflow/LINK-LIBRARY-ENTRY-POINTS.md)** and
  **[LINK-LIBRARY-NAME-INDEX.md](../../Workflow/LINK-LIBRARY-NAME-INDEX.md)**: every entry point
  in every `:BRF` link library on the archive floppies (FORTRAN, PLANC, COBOL, Pascal, C, BASIC,
  monitor calls ...), and which library defines a given name
- [BRF-FILE-FORMAT.md](../../../SINTRAN/File-Formats/BRF-FILE-FORMAT.md) and the parser
  `scripts/nd100_brf.py` (`--names`, `--find`)
- [QUICK-START-EXAMPLES.md](../../QUICK-START-EXAMPLES.md): working examples
- [LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md): linking
- [COMPILER-COMMANDS-REFERENCE.md](../../Workflow/COMPILER-COMMANDS-REFERENCE.md): compiler and linker commands
- [SINTRAN-DEVELOPER-GUIDE.md](../../SINTRAN-DEVELOPER-GUIDE.md): master guide
- [SCRIPT-GUIDE.md](../../Workflow/SCRIPT-GUIDE.md): MODE file automation
- [NPL-DEVELOPER-GUIDE.md](../System/NPL-DEVELOPER-GUIDE.md) and
  [MAC-DEVELOPER-GUIDE.md](../System/MAC-DEVELOPER-GUIDE.md): the assembler side

---

**Last Updated:** October 15, 2026
**Version:** 3.0
