# PLANC on the ND-500 / ND-5000 with PLANC-500

PLANC-500 announces itself as `ND-500 PLANC COMPILER - JUNE 9, 1986   VERSION G` (file
`PLANC-500-G00:DOM`). It compiles a PLANC module to a relocatable `:NRF` object; the ND Linker makes the
runnable domain - see [ND-LINKER-PRACTICAL-GUIDE.md](ND-LINKER-PRACTICAL-GUIDE.md). There is no
`PROG-FILE` short cut on the ND-500 as there is on the ND-100.

This chapter is only about building on the ND-500. The language itself is covered by:

- [ND-60.117.5 PLANC Reference Manual](../../Reference-Manuals/ND-60.117.5%20EN%20PLANC%20Reference%20Manual.md)
  (5th edition, March 1986, compiler version G - the matching manual)
- [ND-860117-6 PLANC User Guide and Reference Manual](../../Reference-Manuals/ND-860117-6-EN%20PLANC%20-%20User%20Guide%20and%20Reference%20Manual.md)
- [../Languages/Application/PLANC-DEVELOPER-GUIDE.md](../Languages/Application/PLANC-DEVELOPER-GUIDE.md)
  and [../Languages/Application/PLANC-LANGUAGE-RULES.md](../Languages/Application/PLANC-LANGUAGE-RULES.md)

The evidence tags ([measured], [manual], [unknown]) are explained in [README.md](README.md).

## 1. What is needed

On the pack under user SYSTEM: `PLANC-500-G00:DOM`, and for linking `PLANC-LIB:NRF`,
`LINKER-AUTO-PLNC:JOB` and the linker files (list in [README.md](README.md)).

PLANC-500 needs no standard domain: it compiled in a session where none had been defined [measured].
That is a difference from the NC compiler.

## 2. The source file

```planc
MODULE hello
    INTEGER ARRAY : stack(0:100)
    BYTES : msg := 'HELLO FROM PLANC!'

    PROGRAM : main
        INISTACK stack
        OUTPUT (1,'AL17',msg)
        OUTPUT (1,'AL1','$')
    ENDROUTINE
ENDMODULE
```

- The file used was `PHELLO:PLNC`, with lines ending in CR and plain 7-bit characters [measured]. The
  PLANC manual gives `:SYMB` as the first default source type and `:PLNC` as the second (section 0.3).
- A program needs exactly one `PROGRAM` routine, and `INISTACK` must come before any routine call
  (PLANC manual, sections 8.2 and 8.6).
- `OUTPUT (1,'AL17',msg)` writes 17 characters left-justified to file number 1, the terminal; a `$` in
  an output string is a new line (PLANC manual, section 9.3).

## 3. Compiling [measured]

```
@CREATE-FILE PHELLO:LIST,0
@CREATE-FILE PHELLO:NRF,0
@ND-500
ND-5000: PLANC-500-G00
- ND-500 PLANC COMPILER - JUNE 9, 1986   VERSION G
*COMPILE PHELLO:PLNC,PHELLO:LIST,PHELLO:NRF
     11 LINES COMPILED.       0 DIAGNOSTICS.

*EXIT
ND-5000:
```

- The compiler's prompt is `*`.
- `COMPILE <source> <list> <object>`: three file names (PLANC manual, section 0.3). A list name of `0`
  suppresses the listing according to the manual; not measured here.
- The two output files were created beforehand with `@CREATE-FILE ...,0`. The manual's alternative is
  to give a new file's name in double quotes; that form was not measured with PLANC-500 in this run (it
  was measured with the NC compiler).
- `EXIT` returns to the `ND-5000:` prompt [measured]. (The NC compiler returns to the SINTRAN prompt
  instead.)
- Results: `PHELLO:NRF` of 270 bytes and a listing with numbered source lines.

The other compiler commands (`INCLUDE`, `OPTION`, `DEBUG-MODE`, `SEPARATE-DATA`, `LIBRARY-MODE`, ...) are
described in the PLANC manual, chapter 0. None of them was exercised on the ND-500 in these
measurements.

## 4. Linking [measured]

```
ND-5000: LINKER-B01
NDL: SET-ADVANCED-MODE
NDL(ADV): OPEN-DOMAIN "PHELLO"
NDL(ADV): LOAD PHELLO
Program:........121B P01   Data:...........744B D01
NDL(ADV): CLOSE
NDL(ADV): LINKER-AUTO-PLNC:JOB
PLANC Auto Job  -  Link/load part.
NDL(ADV): SPECIAL-LOAD            (SYSTEM)PLANC-LIB    LIBRARY
PLANC-LIB-F00
Program:.......1363B P01   Data:...........744B D01
NDL(ADV): LINKER-AUTO:JOB
NDL(ADV): EXIT
ND-5000: PHELLO
HELLO FROM PLANC!
```

Only `SET-ADVANCED-MODE`, `OPEN-DOMAIN`, `LOAD`, `CLOSE` and `EXIT` were typed. `CLOSE` found the
runtime entries undefined, saw that the main program is PLANC, and ran `LINKER-AUTO-PLNC:JOB`, which
loads from `PLANC-LIB` the routines the program refers to. How that works, and how to add libraries of
your own, is in [ND-LINKER-PRACTICAL-GUIDE.md](ND-LINKER-PRACTICAL-GUIDE.md), section 4.

The library that was loaded names itself `PLANC-LIB-F00`. It holds the runtime routines a PLANC program
calls for input and output, whose entry names begin with `#` (`#UTBY`, `#INBY`, `#OPFI`, ...). Without
it the link stays open with those entries undefined.

The finished `PHELLO:DOM` occupies 5 pages on disk although SINTRAN reports 6301156 bytes; the linker
chapter explains why and how `COMPRESS` removes the difference.

## 5. Mixing PLANC and C

Not measured. The linker decides which auto job to run from the language of the Main Start Address in
the first loaded module, so in a mixed program only one language's job runs by itself; the other
library has to be loaded by hand or from a private job file (Linker manual, "automatic actions").

## 6. Driving the compiler from a script

Wait for the banner and the `*` prompt before sending `COMPILE`, wait for the text `DIAGNOSTICS` before
sending `EXIT`, and wait for `ND-5000:` after it. Do not send a line before its prompt; every measured run paced its input this way.
