# SIMULA on ND-100 / SINTRAN III

The developer manual for **TPH SIMULA**, the SIMULA compiler Norsk Data sold for the ND-100 under
SINTRAN III. Start here, then read the page you need.

> **Nothing in these pages has been run on a live machine.** Every command, option and example
> was written from the ND manual, the ND product sheet and the files on the distribution floppy.
> Where a fact comes from general SIMULA knowledge instead of an ND document, it is marked
> *"standard SIMULA, not confirmed in the ND manual"*. Where something is not known, the page
> says so.

## The pages

| page | what it holds |
|---|---|
| [SIMULA-LANGUAGE-GUIDE.md](SIMULA-LANGUAGE-GUIDE.md) | The whole language with a small example for every feature: blocks, types, arrays, statements, procedures, classes, VIRTUAL, INNER, references, coroutines, TEXT, files, SIMSET, SIMULATION (with a worked bank simulation), random drawing, the TPH extensions and limits, FORTRAN and assembly procedures |
| [SIMULA-COMPILER-AND-RUN.md](SIMULA-COMPILER-AND-RUN.md) | Starting the compiler, every `>` command, every option, the listing, compile errors, saving a program, separate compilation, running |
| [SIMULA-DEBUGGING.md](SIMULA-DEBUGGING.md) | The built-in debugger (option O), its `*` commands, tracing, run-time options, every run-time error message, and what is known about `SIMDEBUG` |
| [SIMULA-INSTALL.md](SIMULA-INSTALL.md) | The distribution floppy ND-10058O, what each file is, what `DRC-LOAD:MODE` does line by line, and the system set-up SIMULA needs |

## What SIMULA is

SIMULA is a general-purpose language defined in 1967 by the Norwegian Computing Center (NCC) in
Oslo, in the document *"SIMULA Common Base Language"* (Dahl, Myrhaug, Nygaard, NCC S-22). It is
ALGOL 60 plus **classes** (records that carry their own procedures), **subclasses** (built by
"prefixing" one class with another), **references** to objects, **virtual procedures** and
**coroutines** (objects that can pause and be resumed). Two standard classes come with it:
**SIMSET** (two-way linked lists) and **SIMULATION** (processes and a simulated clock for
discrete-event simulation). It is the first object-oriented language.
(Manual ND-60.092.03 ch. 1, p.12; product sheet ND-10058-D1, p.1.)

The ND manual does **not** teach the language. It says a "thorough knowledge of the SIMULA
language is assumed" and only lists where TPH SIMULA differs from the Common Base
(ND-60.092.03 preface, p.7). The language guide in this folder fills that gap, and marks every
part that comes from the Common Base and not from ND.

## Which SIMULA this is

| item | value | source |
|---|---|---|
| Name | TPH SIMULA | ND-60.092.03 preface p.7 |
| Written by | G. P. Philippot, TPH Data A.S., Oslo | ND-60.092.03 p.6-7 |
| Sold by | Norsk Data A.S., product number ND 10058 | product sheet ND-10058-D1 |
| Version on the floppy | "TPH SIMULA (SINTRAN III) level 4", (c) 1982 TPH Data A.S. | strings in the compiler binary, as reported by the binary analysis; not checked by me |
| Distribution floppy | ND-10058O, 1983 | floppy label as given in the task |
| Version in the manual | 4.017, October 1980 release; the example shows `LEVEL 4 ED 011` | ND-60.092.03 p.7, p.42 |
| Version in the product sheet | 4.036, March 1981 | ND-10058-D1 p.2 |
| Runs on | ND-100 or NORD-10/S, SINTRAN III/VS, about 96K words of memory or more | ND-10058-D1 p.2; ND-60.092.03 p.15 |
| Character set | ASCII, codes 0 to 127 | ND-60.092.03 1.1, p.12 |

**The floppy is newer than both documents.** The manual describes 4.017 (1980) and the product
sheet 4.036 (1981); the floppy is level 4 from 1982-83. Things that differ between them are
pointed out where they are known (for example the separate `SIMDEBUG` program, which neither
document mentions). Anything added after 1981 is unknown.

## History

From the NDwiki page on SIMULA (<https://www.ndwiki.org/wiki/Simula>), quoted as found there:

> This implementation of the SIMULA language for the NORD-10 minicomputer has been performed by
> mr. G. P. Philippot of TPH Data A.S. All marketing rights for the NORD-10 have been
> transferred to Norsk Data A.S. in agreement with TPH Data A.S.
>
> The SIMULA language, developed by the Norwegian Computing Center (NCC), has achieved great
> acceptance in universities and computer teaching institutes for the exceptionally good program
> and data structuring capabilities, making it especially suitable in teaching programming
> techniques. The list-processing and simulation capabilities offered by the SIMSET and
> SIMULATION system classes make SIMULA a programming language with capabilities far beyond
> those normally found with FORTRAN, COBOL, BASIC, etc.
>
> This implementation of the SIMULA languag makes, for the first time, these programming
> capabilities available within low cost minicomputer environments.

("languag" is spelled that way in the text as found.) This matches the compiler itself, which
carries "TPH SIMULA (SINTRAN III) level 4", "Copyright (c) 1982 TPH Data A.S." and
G. P. Philippot's name as the contact for internal errors.

## Sources used

| source | in this repository |
|---|---|
| ND-60.092.03 NORD-100 SINTRAN III SIMULA Reference Manual (version 03, 12/80) | [ND-60.092.03 NORD-100 SINTRAN III SIMULA Reference Manual](../../../../Reference-Manuals/ND-60.092.03%20NORD-100%20SINTRAN%20III%20SIMULA%20-%20Reference%20Manual.md) |
| ND-60208-1-EN ND-500 SIMULA Reference Manual (ND-500 version; not yet used as a source for these pages) | [`Reference-Manuals/ND-60208-1-EN ND-500 SIMULA reference manual.md`](../../../../Reference-Manuals/ND-60208-1-EN%20ND-500%20SIMULA%20reference%20manual.md) |
| ND 10058 SIMULA product sheet | [ND-10058-D1-EN SIMULA product sheet](../../../../Installation/Product-Info/ND-10058-D1-EN.md) |
| The install mode file `DRC-LOAD-O:MODE` from the floppy | not in the repository; quoted in full in [SIMULA-INSTALL.md](SIMULA-INSTALL.md) |

Citations in these pages use the manual's printed page numbers as the OCR copy shows them
(`## Page n` headings), for example "ND-60.092.03 7.3.1, p.34".

The OCR copy of the manual has damage in places (for example "SETOFT" for "SETOPT" and "@STM" for
"@SIM" in Appendix A, and garbled symbols in the delimiter table on p.20). Where the damage
matters it is pointed out.

## Related pages

- Other languages: [../README.md](../README.md)
- Developer overview: [../../../README.md](../../../README.md)
- FORTRAN (for FORTRAN procedures called from SIMULA): [../FORTRAN-DEVELOPER-GUIDE.md](../FORTRAN-DEVELOPER-GUIDE.md)
