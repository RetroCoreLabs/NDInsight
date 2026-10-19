# Developing for the ND-500 / ND-5000 with NC and PLANC

How to write a program in C or PLANC, compile it on the ND-500/5000 itself, link it with the ND Linker and
run it, under real SINTRAN III VSX/500. Three chapters, one for each tool:

| Chapter | Covers |
|---|---|
| [NC-C-COMPILER-GUIDE.md](NC-C-COMPILER-GUIDE.md) | The NC compiler (Norsk Data C, version A06): commands, options, include files, the C library without header files, arguments, diagnostics |
| [PLANC-500-COMPILER-GUIDE.md](PLANC-500-COMPILER-GUIDE.md) | PLANC-500 version G: compiling a PLANC module to `:NRF` on the ND-500 |
| [ND-LINKER-PRACTICAL-GUIDE.md](ND-LINKER-PRACTICAL-GUIDE.md) | The ND Linker (LINKER-B01): the link session, the auto jobs that `CLOSE` runs, several object files, why a domain file shows 6.3 MB, `COMPRESS`, running the result |

## How to read the evidence tags

Every statement in these chapters says how it is known:

- **[measured]** - run on 5 October 2026 on the nd100x emulator with an ND-5000 CPU on the octobus,
  under real SINTRAN III VSX/500 L (banner `ND-500/5000 MONITOR Version J04 88. 6.16 / 88. 8.17`), with
  `Norsk Data C - Version: A06 - 1989-01-10`, `ND-500 PLANC COMPILER - JUNE 9, 1986 VERSION G` and
  `ND LINKER, Version B01, 10. January 1989`. SINTRAN, the ND-500 monitor, the swapper, the compilers and
  the linker are the vendor binaries; only the hardware is emulated.
- **[NC help]** - text the NC compiler printed for its own `HELP` and `VALUE` commands in that run.
- **[manual ...]** - a vendor manual, named with its document number and linked below.
- **[unknown]** - not measured and not found in a manual. These are left open on purpose.

## The manuals behind these chapters

| Document | What it is used for here |
|---|---|
| [ND-860289-2 ND Linker User Guide and Reference Manual](../../Reference-Manuals/ND-860289-2-EN%20ND%20Linker%20User%20Guide%20and%20Reference%20Manual.md) | Everything about the linker: commands, auto jobs, domain file layout, `COMPRESS` |
| [ND-60.136.04A ND-500 Loader Monitor](../../Reference-Manuals/ND-60.136.04A%20ND-500%20Loader%20Monitor.md) | The ND-500 monitor, standard domains, traps, MON 505B GERRCOD, the older Linkage-Loader |
| [ND-60.117.5 PLANC Reference Manual](../../Reference-Manuals/ND-60.117.5%20EN%20PLANC%20Reference%20Manual.md) | The PLANC language and the compiler commands (version G) |
| [ND-860117-6 PLANC User Guide and Reference Manual](../../Reference-Manuals/ND-860117-6-EN%20PLANC%20-%20User%20Guide%20and%20Reference%20Manual.md) | Later edition of the PLANC manual |
| [ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual](../../Reference-Manuals/ND-60.214.01%20CC-100%20and%20CC-500%20C-Compiler%20User%20Manual.md) | The K&R language level only. **It describes CC-500, an older and different compiler - not NC.** |
| [ND-860228-2 SINTRAN III Monitor Calls](../../Reference-Manuals/ND-860228-2-EN%20SINTRAN%20III%20Monitor%20Calls.md) | Monitor calls a program can make (MON 412B FileAsSegment, MON 505B GetTrapReason, ...) |
| [ND-05.009.4 ND-500 Reference Manual](../../Reference-Manuals/ND-05.009.4%20EN%20ND-500%20Reference%20Manual.md) | The CPU: registers, traps, the Programmed Trap |
| [ND-60.128.5 SINTRAN III Reference Manual](../../Reference-Manuals/ND-60.128.5%20EN%20SINTRAN%20III%20Reference%20Manual.md) | File names, `@CREATE-FILE`, `@FILE-STATISTICS`, `DEFINE-STANDARD-DOMAIN` |

Related material in this repository:

- [../Workflow/LINKING-GUIDE-500-DEEP-DIVE.md](../Workflow/LINKING-GUIDE-500-DEEP-DIVE.md) - the linker and the NRF/DOM formats in depth, written from the manual
- [../../SINTRAN/File-Formats/DOM-FILE-FORMAT.md](../../SINTRAN/File-Formats/DOM-FILE-FORMAT.md) and [NRF-FILE-FORMAT.md](../../SINTRAN/File-Formats/NRF-FILE-FORMAT.md) - file formats
- [../../SINTRAN/ND500-APPS/README.md](../../SINTRAN/ND500-APPS/README.md) - the preserved vendor programs and their runtime files
- [../Languages/Application/PLANC-DEVELOPER-GUIDE.md](../Languages/Application/PLANC-DEVELOPER-GUIDE.md) - the PLANC language guide (mostly ND-100)
- [../Languages/Application/C-DEVELOPER-GUIDE.md](../Languages/Application/C-DEVELOPER-GUIDE.md) - CC-100 / CC-500, the older C compilers

There is no NC manual in this repository. What is known about NC comes from the compiler's own help
and from measurement; see the NC chapter.

## What must be on the pack

All files go under user SYSTEM. The host copies are in this repository:

| File on the pack | Purpose | Host copy |
|---|---|---|
| `NC-A06:DOM` | C compiler front end | [../../SINTRAN/ND500-APPS/NC-A06/files/](../../SINTRAN/ND500-APPS/NC-A06/files/) |
| `CAT-CAT5-B06:DOM` | code generator that NC starts by name | [../../SINTRAN/ND500-APPS/CAT-CAT5-B06/files/](../../SINTRAN/ND500-APPS/CAT-CAT5-B06/files/) |
| `PLANC-500-G00:DOM` | PLANC compiler | [../../SINTRAN/ND500-APPS/PLANC-500-G00/files/](../../SINTRAN/ND500-APPS/PLANC-500-G00/files/) |
| `LINKER-B01:DOM`, `LINKER-B01:HELP`, `LINKER-B01:INIT` | the linker | [../../SINTRAN/ND500-APPS/LINKER-B01/files/](../../SINTRAN/ND500-APPS/LINKER-B01/files/) |
| `NC-LIB:NRF`, `CAT-LIB:NRF` | C runtime libraries | [../../SINTRAN/ND500-APPS/_shared/files/](../../SINTRAN/ND500-APPS/_shared/files/) |
| `PLANC-LIB:NRF` | PLANC runtime library | same folder |
| `LINKER-AUTO:JOB`, `LINKER-AUTO-C:JOB`, `LINKER-AUTO-FORT:JOB`, `LINKER-AUTO-PLNC:JOB` | the linker's auto jobs | same folder |
| `DDBTABLES-G06:VTM` | terminal tables the linker needs | see [../Workflow/VTM-TERMINAL-INTERFACES.md](../Workflow/VTM-TERMINAL-INTERFACES.md) |

On an emulator a host file is put on a pack image with `ndtool --put HOSTFILE SYSTEM/NAME:TYPE image`,
while no emulator has the image open.

## Three things to do in every session

1. **Set the terminal type before entering the monitor** [measured]:
   `@SET-TERMINAL-TYPE,,93`. Without it the linker prints its table of terminal types and waits.
2. **Define the two standard domains NC needs, once per cold start** [measured], at the `ND-5000:` prompt:
   ```
   DEFINE-STANDARD-DOMAIN CAT-CAT5-B,CAT-CAT5-B06
   DEFINE-STANDARD-DOMAIN NC-A,NC-A06
   ```
   NC starts its code generator by giving SINTRAN the command `CAT-CAT5-B`. Without the definition the
   compile stops with `AMBIGUOUS FILE NAME`. PLANC does not need this.
3. **Output files must exist or be named in double quotes.** `"HELLO"` asks SINTRAN to create the file;
   a plain name must already exist (`@CREATE-FILE HELLO:NRF,0`).

## Hello world in both languages [measured]

C source `HELLO:C` (lines end in CR LF):

```c
main()
{
    printf("HELLO FROM C!\n");
}
```

PLANC source `PHELLO:PLNC` (lines end in CR):

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

The whole session:

```
@SET-TERMINAL-TYPE,,93
@CREATE-FILE PHELLO:LIST,0
@CREATE-FILE PHELLO:NRF,0
@ND-500
ND-5000: DEFINE-STANDARD-DOMAIN CAT-CAT5-B,CAT-CAT5-B06
ND-5000: DEFINE-STANDARD-DOMAIN NC-A,NC-A06

ND-5000: PLANC-500-G00
- ND-500 PLANC COMPILER - JUNE 9, 1986   VERSION G
*COMPILE PHELLO:PLNC,PHELLO:LIST,PHELLO:NRF
     11 LINES COMPILED.       0 DIAGNOSTICS.
*EXIT

ND-5000: NC-A06
Norsk Data C - Version: A06 - 1989-01-10
NC: COMPILE HELLO,"HELLO","HELLO"
preprocessing   : ok
syntax check    : ok
semantic check  : ok
code generation : ok
NC: EXIT
@ND-500                               (NC's EXIT returns to the SINTRAN prompt)

ND-5000: LINKER-B01
NDL: SET-ADVANCED-MODE
NDL(ADV): OPEN-DOMAIN "HELLO"
NDL(ADV): LOAD HELLO
NDL(ADV): CLOSE                       (runs the C auto job: loads NC-LIB and CAT-LIB)
NDL(ADV): OPEN-DOMAIN "PHELLO"
NDL(ADV): LOAD PHELLO
NDL(ADV): CLOSE                       (runs the PLANC auto job: loads PLANC-LIB)
NDL(ADV): EXIT

ND-5000: HELLO
HELLO FROM C!
program HELLO terminated
ND-5000: PHELLO
HELLO FROM PLANC!
```

## When it does not work

| Symptom | Cause | How it is known |
|---|---|---|
| `""` then `AMBIGUOUS FILE NAME` after NC's `semantic check : ok`; `protection violation` at NC's `EXIT` | the standard domains `CAT-CAT5-B` and `NC-A` are not defined in this boot | measured |
| NC: `can't find include file` for `#include <x.h>` | no include directory set; see the NC chapter | measured |
| the linker prints a table of terminal types and waits | `@SET-TERMINAL-TYPE` was not given before `@ND-500` | measured |
| the domain file shows 6 MB for a ten-line program | the linker's default file layout with holes; only a few pages are on disk. See the linker chapter | measured, and the Linker manual |
| `NO SUCH PAGE` while linking, or `ND LINKER abortion` with a register dump | **an emulator defect, not a fault in the linker or the pack.** The linker relies on a Programmed Trap that the swapper raises when a page cannot be read; the CPU must take that trap as soon as the process becomes active (ND-500 Reference Manual, status register, PRT; Loader Monitor manual, MON 505B GERRCOD). Fixed in nd100x commit `70f4854` with nd500x commit `2d85a44` | measured |
| a domain started by name prints nothing at all | emulator defect fixed the same day (nd500x `4254ef2`, nd100x `df5d93d`) | measured |
