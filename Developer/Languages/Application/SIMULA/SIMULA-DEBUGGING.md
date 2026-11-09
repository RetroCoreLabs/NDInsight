# Debugging SIMULA programs

The TPH SIMULA debugger, run-time options and run-time error messages. Back to the index:
[README.md](README.md).

> **Not run on a live machine.** From ND-60.092.03 7.4 (p.37-39) and App. D (p.50-51), and the
> binary analysis of the floppy. The separate `SIMDEBUG` program is not in the manual.

## 1. Turning the debugger on

| what | how | source |
|---|---|---|
| stop after every statement and accept commands | compile with option **O** | ND 7.3.2 p.36; 7.4.1 p.37 |
| let `*VAR` and `*OBJECT` use names | compile with option **D** as well | ND 7.4.1 p.38 |
| get the debugger before the program starts | run-time option **O**: `>RTS O` | ND 7.4.3 p.39 |
| debug only part of a program | `%SETOPT O` before it and `%RESOPT O` after it in the source | ND 2.2 p.16 (options are counters) |

```
@SIM
>SETOPT ODV
>COMPILE PROGRAM
```

With option O, the run-time system gets control at the end of each statement and prints:

```
Line n
*
```

The `*` is the debugger prompt. Any run-time error also enters the debugger, whether or not O was
set (ND 7.4.2 p.39).

## 2. Debugger commands (ND 7.4.1, p.37-39)

| command | what it does |
|---|---|
| `*HELP` | list the commands |
| (just carriage return) | run the next statement |
| `*STEP` | same |
| `*STEP n` | run n statements, unless a breakpoint comes first |
| `*BREAK n` | breakpoint after the first statement of line n |
| `*BREAK` | remove the breakpoint |
| `*GO` | run until the breakpoint (if any) |
| `*GO n` | same as `*BREAK n` then `*GO` |
| `*DYN n` | show the chain of calling or enclosing blocks, up to n (default 20). Shows where you are; the object addresses can be given to `*OBJECT`. |
| `*OBJECT name` | dump an object. `name` is a REF variable visible from here; dots and array elements with a decimal constant subscript are allowed. No name: the current object. |
| `*VAR name` | print a variable's value; dots and array subscripts as for `*OBJECT` |
| `*TRACE n m` | from now on count every statement executed in lines n to m |
| `*HISTO i n m` | stop tracing and print a bar chart on the **printer**, i lines per bar; n, m default to the last `*TRACE` |
| `*SYSIN file` | close SysIn and reopen it on file |
| `*SYSOUT file` | close SysOut and reopen it on file |
| `*RESTART` | close all files, reset, and run the whole program again from `Ready for Simula execution` |
| `*DRIVER a` | dump the "driver" at octal address a (system maintenance) |
| `*EXIT` | end the program |

Anything else gives `ILLEGAL DEBUG COMMAND`. Only one breakpoint is described (`*BREAK` with no
number removes "the breakpoint").

Names are only known if the module was compiled with option D (ND 7.4.1 p.38). `*TRACE` counts only
statements compiled with option O.

### A session (made up from the commands above, not captured)

```
>SETOPT ODV
>COMPILE SUMS
Loading Program
Ready for Simula execution
Line 3
*BREAK 12
*GO
Line 12
*VAR Total
*DYN
*STEP 5
*GO
```

## 3. Profiling with TRACE and HISTO

`*TRACE` and `*HISTO` make a simple execution profile: run with O, give `*TRACE 1 400` at the start,
`*GO`, and when the program stops at a breakpoint near the end give `*HISTO 10` to print counts per
10 lines (ND 7.4.1 p.38). Output goes to the printer.

## 4. Run-time options

The run-time system has options A to O, each TRUE or FALSE (ND App. G p.62). Set them before the
run with `>RTS letters` (ND 7.3.1 p.34), or from the program with the external procedures `RtOn(c)`,
`RtOff(c)` and read them with `RtOpt(c)` (App. G p.62).

| option | meaning (ND 7.4.3 p.39) |
|---|---|
| N | no `Ready for Simula execution` and no end messages - for system programs written in SIMULA |
| O | debugger before the program starts: prints `Pre-program conversation requested.`, then `Line 0` and `*`. Give `*SYSIN` / `*SYSOUT` to redirect, then `*GO`. |

The other letters are not described.

```
@SIM
>RTS O
>SETOPT V
>COMPILE REPORT
Pre-program conversation requested.
Line 0
*SYSOUT REPORT-OUT
*GO
```

## 5. SIMDEBUG:PROG

The floppy has `SIMDEBUG-O:PROG`, installed as `(SYSTEM)SIMDEBUG...:PROG` by `DRC-LOAD:MODE`
(see [SIMULA-INSTALL.md](SIMULA-INSTALL.md)). The binary analysis found it is the **run-time system
together with the interactive debugger** - the part that serves options O and D. The 1980 manual
does not mention it; there the debugger is part of the run-time system (ND 1.2.1 p.13, 7.4).

**Unknown:** the run-time system asks for a file named `SIM-DEBUG:PROG` (with a hyphen), while the
file installed is `SIMDEBUG:PROG` (no hyphen). SINTRAN short-name matching does not obviously
bridge that difference. So it is not known whether the debugger is found on an installed system as
shipped, whether a site is meant to rename or copy the file, or whether some other lookup is used.
Test this first if `*` never appears with option O.

## 6. Run-time error messages

When a run-time error happens, the message is printed and the debugger is entered. Carriage return,
`*STEP` or `*GO` then ends the program; `*RESTART` runs it again (ND 7.4.2 p.39). Use `*DYN` and
`*VAR` first to see where and why.

The full list is in ND App. D p.50-51 (the binary analysis counted 68 texts in `SIMERR:DATA`). Grouped
here with what each means.

### Arithmetic

| message | meaning |
|---|---|
| `Illegal parameter to LN` / `EXP` / `SQRT` / `ARCTAN` / `SIN or COS` / `SINH or COSH` | argument out of range (e.g. `Sqrt(-1)`) |
| `Illegal operands to **` | e.g. negative number to a real power |
| `Arithmetic operation caused overflow` | result outside -32768..32767 or the real range (option N reduces checks) |
| `Result of real to integer conversion was too large` | real does not fit 16 bits |
| `Illegal parameter to isochar` | not 0..127 |

### Objects and references

| message | meaning |
|---|---|
| `Ref before dot or qua was equal to none` | `x.a` or `x QUA C` with x = NONE (check off: option R) |
| `Object in reference assignment or qua was of wrong class` | `:-` or QUA to an unrelated class (check off: option Q) |
| `No match to virtual attribute in this class` | virtual procedure has no body in this object |
| `Attempted assignment to constant or expression` | a name parameter got a constant or expression, then was assigned |
| `Wrong number of parameters to formal or virtual procedure`, `Actual parameter ... is of wrong kind`, `... of wrong type` | procedure parameter mismatch found at run time |

### Arrays and memory

| message | meaning |
|---|---|
| `Array index out of range` | subscript outside the bounds (check off: option A). For several dimensions only the total address is checked. |
| `Too large array declared (max. is 49152 machine words)` | |
| `You have exchanged lower and upper bounds in array declaration` | |
| `Wrong number of actual dimensions in array parameter` | |
| `Sorry, we just ran out of memory space for your data` | the heap is full; drop references to objects you no longer need |

### Coroutines and SIMULATION

| message | meaning |
|---|---|
| `Parameter to CALL or RESUME was terminated` / `was already operating` / `was none` | |
| `Detach called for non-operating class object` | |
| `Illegal goto from detached object or to inspected object` | |
| `Attempt to passivate last process` | the only scheduled process passivated - nothing left to run |
| `Reactivate caused passivation of last process` | |
| `Evtime called for idle process` | |
| `Attempt to activate terminated process` | |

### Text and editing

| message | meaning |
|---|---|
| `Left side of text assignment has too short text object` | `T := value` with T shorter than value |
| `No numeric item found in text`, `Illegal number syntax` | `GetInt` / `InInt` etc. found no number |
| `Illegal parameter to editing or de-editing routine`, `Too small field for editing` | |
| `MORE is false in GETCHAR` / `PUTCHAR` | past the end of the text |
| `SUB parameter(s) out of range` | |
| `Parameter to BLANKS was negative or greater than 8186` | |

### Files

| message | meaning |
|---|---|
| `File not closed at calling OPEN`, `File already closed at calling CLOSE` | |
| `Requested file is busy or non-existent` | the SINTRAN file cannot be opened |
| `File not open at INIMAGE` / `OUTIMAGE` / `LOCATE` / `EJECT` / `SAVE` | |
| `ENDfile is true at INIMAGE` | read past the end - test `EndFile` first |
| `Image of infile is too short` | input line longer than the image |
| `Lastitem is true at ININT` / `INFRAC` / `INREAL` | no more items in the input |
| `Wrong physical directfile image length`, `Too large directfile image` | DirectFile line length differs from the image |
| `Zero parameter to LOCATE` | lines are counted from 1 |
| `Unsuccessful input/output request` | SINTRAN refused the request |

### Library and system

| message | meaning |
|---|---|
| `ERLANG parameter(s) zero or negative`, `HISTO: First array must be longer than second array`, `Wrong parameters to LINEAR` | random/statistics routines |
| `Error in FORTRAN subroutine or function` | a FORTRAN procedure failed |
| `Unimplemented feature used - please report`, `Run time system error detected - please report` | a fault in SIMULA itself |

The OCR of App. D also has a line reading `DRUM Atlas` (p.51) that makes no sense; it is OCR damage
and the real text is unknown.

## 7. Warnings after the run

If a number did not fit an editing field, the field is filled with `*` and a warning is printed
when the program ends (ND 6.4 p.32). The end of a run prints CPU time and the number of garbage
collections, if any (ND ch. 7 p.33).
