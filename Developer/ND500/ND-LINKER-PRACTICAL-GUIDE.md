# Linking on the ND-500 / ND-5000 with the ND Linker

The ND Linker (`ND LINKER, Version B01, 10. January 1989`, file `LINKER-B01:DOM`) takes relocatable
`:NRF` objects from the NC, PLANC and other compilers and writes a domain file, `:DOM`, that the ND-500
monitor can run. This chapter is the practical side: the session that works, why `CLOSE` loads the
runtime library by itself, how to link several objects, why the domain file looks huge and how to shrink
it.

The reference is the
[ND-860289-2 ND Linker User Guide and Reference Manual](../../Reference-Manuals/ND-860289-2-EN%20ND%20Linker%20User%20Guide%20and%20Reference%20Manual.md);
"Linker manual" below means that document. A longer treatment written from the manual is in
[../Workflow/LINKING-GUIDE-500-DEEP-DIVE.md](../Workflow/LINKING-GUIDE-500-DEEP-DIVE.md). The evidence
tags ([measured], [manual], [unknown]) are explained in [README.md](README.md).

## 1. Before starting the linker

- The files on the pack: `LINKER-B01:DOM`, `:HELP`, `:INIT`, the runtime libraries and the auto job
  files (list in [README.md](README.md)), and a `DDBTABLES-G` terminal table
  (see [../Workflow/VTM-TERMINAL-INTERFACES.md](../Workflow/VTM-TERMINAL-INTERFACES.md)).
- At the SINTRAN prompt, before `@ND-500`: `@SET-TERMINAL-TYPE,,93` [measured]. Without a terminal type
  the linker prints its table of terminal types and waits for an answer.

## 2. The session [measured]

```
@SET-TERMINAL-TYPE,,93
@ND-500
ND-5000: LINKER-B01
- ND LINKER, Version B01            10. January   1989  Time:  0:00 -
NDL: SET-ADVANCED-MODE
NDL(ADV): OPEN-DOMAIN "HELLO"
NDL(ADV): LOAD HELLO
Program:........155B P01   Data:...........214B D01   Debug:.........262B Bytes
NDL(ADV): CLOSE
NDL(ADV): LINKER-AUTO-FORT:JOB
C Auto Job  -  Link/load part.
NDL(ADV): LOAD              (SYSTEM)NC-LIB
Program:......36716B P01   Data:.........23634B D01   Debug:.........262B Bytes
NDL(ADV): LOAD              (SYSTEM)CAT-LIB
Program:......51113B P01   Data:.........30734B D01   Debug:.........262B Bytes
NDL(ADV): DEFINE-ENTRY       stack-space,400000,d
NDL(ADV): DEFINE-ENTRY       heap-space,400000,d
NDL(ADV): REFER              stack-space,rts_stack_size,d,d
NDL(ADV): REFER              heap-space,rts_heap_size,d,d
NDL(ADV): LINKER-AUTO:JOB
NDL(ADV): EXIT
ND-5000: HELLO
HELLO FROM C!
program HELLO terminated
```

Only five lines were typed: `SET-ADVANCED-MODE`, `OPEN-DOMAIN`, `LOAD`, `CLOSE`, `EXIT`. Everything
between `CLOSE` and `EXIT` is the linker running its auto jobs (section 4).

What each command does:

| Command | Effect | Source |
|---|---|---|
| `SET-ADVANCED-MODE` | makes the advanced commands available (`SPECIAL-LOAD`, `LINKER-SERVICE-PROGRAM`, `DEFINE-ENTRY`, ...); the prompt becomes `NDL(ADV):` | Linker manual |
| `OPEN-DOMAIN "HELLO"` | creates `HELLO:DOM`. "Enclosing the domain name in double quotation marks assumes that the domain ... does not already exist. If no double quotation marks are used, the domain ... must already exist, and its contents will be overwritten." | Linker manual, Basic use of the Linker |
| `LOAD HELLO` | loads `HELLO:NRF` into the open domain; `:NRF` is the default type; several files may be named in one command | Linker manual, same section |
| `CLOSE` | writes the symbol table to the file and closes it; runs the auto jobs first if something is undefined | Linker manual, CLOSE |
| `EXIT` | leaves the linker; runs `CLOSE` if that was not done | Linker manual, CLOSE notes |

The numbers after `Program:` and `Data:` are the octal sizes of program and data segment so far; `P01`
and `D01` are segment 1.

Two start-up details [measured]: the line `LINKER:INIT` followed by a "No such file name" warning is the
linker looking for an optional init file of that name, and is harmless; and scripts should wait for the
text `NDL`, because the advanced prompt `NDL(ADV):` does not contain `NDL:`.

Relinking: every measured relink deleted the old file first (`@DELETE-FILE HELLO:DOM`) and used the
quoted name. The manual's alternative is `OPEN-DOMAIN HELLO` without quotes, which overwrites.

## 3. Running the result [measured]

- `ND-5000: HELLO` at the monitor prompt, with arguments after the name if the program takes any.
- `@ND HELLO` or `@ND-500 HELLO` at the SINTRAN prompt.

A C program ends with `program HELLO terminated` and two time lines from its runtime. The PLANC hello
program printed only its own text.

## 4. Why CLOSE loads the runtime: the auto jobs

This is built into `CLOSE` (Linker manual, "automatic actions" and the description of `CLOSE`):

1. `CLOSE` has a second parameter, `<Perform Auto Job/Linker Job (Yes, No)>`. Its default is YES.
2. The linker checks whether there are undefined entries in the symbol table, or whether a trap handler
   is missing.
3. If so, it looks for a job file named `LINKER-AUTO-` plus an abbreviation of the language of the Main
   Start Address: `LINKER-AUTO-FORT:JOB`, `LINKER-AUTO-PLNC:JOB` and so on. "The MSA and its language
   are defined in the NRF modules. If there are several definitions of MSA in the loaded modules, the
   first one loaded applies."
4. "The Linker searches for the file, first in your own user area, and then, if it does not find it
   there, under user SYSTEM."
5. If something is still undefined afterwards, or no language file was found, it runs `LINKER-AUTO:JOB`,
   found the same way.

A job file is a list of ordinary linker commands. The two that matter here:

`LINKER-AUTO-PLNC:JOB`:

```
MESSAGE 'PLANC Auto Job  -  Link/load part.'
SET-ADVANCED-MODE
LIST
SPECIAL-LOAD            (SYSTEM)PLANC-LIB    LIBRARY
```

The C job:

```
MESSAGE 'C Auto Job  -  Link/load part.'
LIST
SET-ADVANCED-MODE
LOAD              (SYSTEM)NC-LIB
LOAD              (SYSTEM)CAT-LIB
DEFINE-ENTRY       stack-space,400000,d
DEFINE-ENTRY       heap-space,400000,d
REFER              stack-space,rts_stack_size,d,d
REFER              heap-space,rts_heap_size,d,d
```

**For an object from the NC compiler the linker runs `LINKER-AUTO-FORT:JOB`, not `LINKER-AUTO-C:JOB`**
[measured]. `LIST-STATUS` on the finished domain shows `Source code language: Fortran*, Planc`. So the
file named `LINKER-AUTO-FORT:JOB` on the pack must contain the C job; the copy in
[../../SINTRAN/ND500-APPS/_shared/files/](../../SINTRAN/ND500-APPS/_shared/files/) does. A site that also
links FORTRAN programs needs a different arrangement, for example a private job file under the user
that links C.

`400000` is octal, 131072 bytes each for stack and heap. They become the values of the data words
`RTS_STACK_SIZE` and `RTS_HEAP_SIZE` that the C runtime reads; they do not take space in the file.

Consequences:

- `EXIT` and `OPEN-DOMAIN` close the current domain implicitly, so the job runs even when `CLOSE` is
  never typed.
- `CLOSE ,NO` closes without running any job.
- A job file with the same name under the linking user is used instead of the one under SYSTEM. The
  vendor's own job files recommend this for private libraries: load them in the local file, then call
  the SYSTEM file from it, for example

  ```
  LOAD MYLIB1
  (SYSTEM)LINKER-AUTO-PLNC:JOB
  ```

- The manual notes that in interactive mode a domain "will not be closed the first time if undefined
  references exist"; give the command a second time to close anyway.

## 5. Several object files, and seeing what is missing [measured]

A C program in two files, `MAIN2:C` calling `add2()` in `ADD2:C`, each compiled to its own `:NRF`:

```
NDL(ADV): OPEN-DOMAIN "MAIN2"
NDL(ADV): LOAD MAIN2
Program:........177B P01   Data:...........210B D01   Debug:.........262B Bytes
NDL(ADV): LIST-ENTRIES UNDEFINED
Undefined entries: 10
NUN!GEHT!S!LOS!..../ffff........5B P01  C!INIT............./ffff.......37B P01
C!EXIT............./ffff......100B P01  RERAISE!EXC!......./ffff......106B P01
C!EXIT............./ffff......114B P01  DAS!WAR!S!........./ffff......122B P01
ADD2.............../ffff......142B P01  PRINTF............./ffff......162B P01
V!ARGV............./ffff.......63B P01  V!ENV............../ffff.......70B P01
NDL(ADV): LOAD ADD2
Program:........221B P01   Data:...........270B D01   Debug:.........501B Bytes
NDL(ADV): CLOSE
```

`ADD2` is the user's own function, defined by the second `LOAD`. The other entries belong to the C
runtime and are defined when the auto job loads `NC-LIB` and `CAT-LIB`. The program then printed
`2 + 3 = 5`.

`LIST-ENTRIES UNDEFINED` is the command to use when a link does not close: it names exactly what is
still missing and where it is referenced.

`SPECIAL-LOAD <file>,LIBRARY` loads from a library file only the modules that define entries currently
referenced; it is an advanced-mode command (Linker manual, SPECIAL-LOAD). Plain `LOAD` of a library, as
the C job does, loaded what was needed from `NC-LIB` in the measured links.

## 6. Looking at a domain: LIST-STATUS [measured]

```
NDL(ADV): LIST-STATUS HELLO
Domain: (PACK-ONE:SYSTEM)HELLO:DOM;1
Main Start Address:   4B           Segment no:   1B
Start of debug info:  20000B       Size:         263B
Start of link info:   10020000B    Size:        4763B
Linker version used:  B01
Trap handler vector:  30734B       Segment no:   1B
Source code language: Fortran*, Planc
Program segment:   1  Address in file:    20020000B      Size:           51113B
Data segment:      1  Address in file:    30020000B      Size:           32734B
```

(Shortened; the real output also lists privileges and segment attributes.)

## 7. Why a ten-line program has a 6.3 MB domain file

`@FILE-STATISTICS HELLO:DOM,,` shows `23 PAGES , 6313436 BYTES IN FILE` [measured]. Both numbers are
true. Only the 23 pages, 47 kilobytes, are on the disk.

The linker lays out a new domain file at fixed default positions and writes only the pages it needs.
The Linker manual, on the structure of domain files:

> "After the domain header comes space for debug information, and link information. By default, 2 MB of
> file space is reserved for each area. ... (Only the pages actually needed are allocated on disk.)"

> "You need not worry about the disk space because of the large default segment sizes. Domain and
> segment files are normally indexed files, and pages not written to are not allocated on disk, even if
> other pages with higher page numbers are. In other words, the files can have holes that do not occupy
> space on disk."

The layout of the measured files, which is also what `LIST-STATUS` prints above:

| Part | Position in the file | Default reservation | In `HELLO:DOM` |
|---|---|---|---|
| header | 0 | 2 pages, and 2 more reserved | 692 bytes |
| debug information | 20000B (0x002000) | 2 MB | 179 bytes |
| link information (the symbol table) | 10020000B (0x202000) | 2 MB | 2547 bytes, 96 entries |
| program segment 1 | 20020000B (0x402000) | 2 MB | 21067 bytes |
| data segment 1 | 30020000B (0x602000) | 32 MB | 13788 bytes |

The byte count that SINTRAN reports is the position of the last byte written: the start of the data
segment plus its size. That holds exactly for all four domains measured
(`HELLO`: 0x602000 + 0x35DC = 6313436; `PHELLO`: 0x602000 + 0x5E4 = 6301156). The stack and heap sizes
in the C auto job have no part in it.

The table in the manual's appendix on the domain file format prints these positions as `00002000`,
`01002000`, `02002000`, `03002000`. Those figures match the measured positions only as octal numbers with
the last digit missing; whether that is a fault in the printed manual or in its transcription has not
been checked.

### Making the file small: COMPRESS [measured]

```
NDL(ADV): LINKER-SERVICE-PROGRAM
- ND LINKER's  SERVICE-PROGRAM -
NDL(SRV): COMPRESS HELLOC,,,,
Copying debug part   -  1 pages.
Copying link part   -  2 pages.
Copying program segment 1  -  11 pages.
Copying data segment 1  -  7 pages.
HELLOC:DOM compressed into 23 pages. All pages allocated.
NDL(SRV): EXIT
```

`@FILE-STATISTICS` afterwards: `23 PAGES , 47104 BYTES IN FILE`, and the program ran as before.

The parameters (Linker manual, COMPRESS):

```
COMPRESS <Name of domain or segment file>
         <Include debug information (Yes,No)>
         <Include link information (Yes,No)>
         <Create contiguous file (No,Yes)>
         <Workfile>
```

The manual's warnings: "COMPRESS does not reduce the number of pages on disk occupied by the file ...
Only the byte count is reduced"; "It is normally impossible to load or reload a segment or domain after
it has been compressed"; "There is no way to reverse the effects of the COMPRESS command." So compress as
the last step, or compress a copy (`@COPY-FILE "HELLOC:DOM",HELLO:DOM` was used for the measurement).

Twelve of the thirteen vendor domain files in
[../../SINTRAN/ND500-APPS/](../../SINTRAN/ND500-APPS/) have this layout without holes; that they were
made with `COMPRESS` is inferred from the layout.

Other controls the manual documents, not measured here:

| Command | Where | What the manual says |
|---|---|---|
| `SET-AREA-SIZE <Debug area size (in pages)> <Link area size (in pages)>` | service program, with no domain open | changes the 2 MB reservations for domains opened afterwards |
| `SET-SEGMENT-SIZE <Segment number> <Program size (in pages)> <Data size (in pages)>` | service program, before the segment is used; `ALL` when no domain is open | changes the reservation per segment |
| `IGNORE-DEBUG-INFORMATION <Ignore (Yes,No)>` | advanced mode, before `LOAD` | leaves the debug information out |

## 8. A fault that is the emulator's, not the linker's

While it links, the linker reads parts of its output file that it has not written yet. The swapper
cannot supply such a page and reports that with a Programmed Trap; the linker has that trap enabled and
its handler writes the page and returns to the read. The documents:

- [ND-60.136.04A ND-500 Loader Monitor](../../Reference-Manuals/ND-60.136.04A%20ND-500%20Loader%20Monitor.md),
  MON 505B GERRCOD: "When the swapper process detects a fatal error (e.g., outside segment), it will
  cause a Programmed Trap (PRT) in the user process. GERRCOD may be used within the trap handler to
  obtain the error code from the swapper."
- [ND-05.009.4 ND-500 Reference Manual](../../Reference-Manuals/ND-05.009.4%20EN%20ND-500%20Reference%20Manual.md),
  status register, PRT: "If the PRT trap is enabled, the trapped process will immediately be
  interrupted and its trap handler invoked. If the process is not in the active state, as soon as it
  becomes active the trap will occur."

An emulated CPU that runs the faulting instruction again before it takes the pending trap ends the link
with `NO SUCH PAGE` after ten attempts, or with a register dump and `ND LINKER abortion` [measured].
On nd100x this was fixed by nd100x commit `70f4854` together with nd500x commit `2d85a44`. A real
machine is not affected: the example sessions in the Linker manual run on the same monitor version,
`J04 88. 6.16 / 88. 8.17`.
