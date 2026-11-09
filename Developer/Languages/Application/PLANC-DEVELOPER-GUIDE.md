# PLANC Developer Guide

**PLANC Programming Language for SINTRAN III**

**Version:** 2.0  
**Date:** May 26, 2026  
**Status:** Verified on ND-100 hardware

---

## Installing PLANC

PLANC for ND-100 is product `ND-10309`. Three versions are catalogued — pick whichever floppy you
have:

- [ND-10309A](../../../Installation/Software/ND-10309/ND-10309A/README.md) (82.02.19) and
  [ND-10309B](../../../Installation/Software/ND-10309/ND-10309B/README.md) (82.06.15) — verified
  from their PD sheets, ship as `:BPUN` (`@DUMP-REENTRANT PLANC-100,0,1,<file>`).
- [ND-10309F](../../../Installation/Software/ND-10309/ND-10309F/README.md) (floppy
  `10309F00-1S`) — no PD sheet located; ships pre-linked as `:PROG`, procedure adapted from A/B
  and not independently verified.

All versions need a 126K/128K-word terminal background segment
(`@CHANGE-BACKGROUND-SEGMENT-SIZE`) and cannot be restarted with `@CONTINUE`. See
[ND-10309 — PLANC for ND-100](../../../Installation/Software/ND-10309/README.md) for the full
product overview.

---

## Quick Start

**See [QUICK-START-EXAMPLES.md](../../QUICK-START-EXAMPLES.md) Section 4 for complete Hello World example.**

### Minimal Example

**File:** `HELLO:PLNC` (must have CRLF line endings and even parity)

Source files use type `:PLNC` or `:SYMB`. The compiler looks for `:SYMB` first, then `:PLNC`.

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

### Build Process

**Interactive build (verified on ND-100, PLANC Version E):**

```
@PLANC
PROG-FILE "HELLO"
COMPILE HELLO:PLNC,"HELLO:LIST","HELLO"
EXIT
@HELLO
```

**Automated build (MODE file):**

File: `DO-BUILD:MODE`

```mode
@DELETE-FILE HELLO:PROG
@DELETE-FILE HELLO:LIST
@DELETE-FILE HELLO:BRF
@PLANC
PROG-FILE "HELLO"
COMPILE HELLO:PLNC,"HELLO:LIST","HELLO"
EXIT
@HELLO
```

Run with: `@MODE DO-BUILD:MODE,,`

See also [BUILD-PLANC.MODE](../../Workflow/BUILD-PLANC.MODE) and [BUILD-PLANC-2BANK.MODE](../../Workflow/BUILD-PLANC-2BANK.MODE) for parameterized builds.

### Build Output

The compiler produces three files:
- `HELLO:PROG` -- executable program (run with `@HELLO`)
- `HELLO:BRF` -- binary relocatable file
- `HELLO:LIST` -- compiler listing with line numbers

### COMPILE Parameters

`COMPILE source, list, object`

1. `source` -- source file (exists, no quotes needed)
2. `list` -- listing output (created, needs `"quotes"`)
3. `object` -- object file name (created, needs `"quotes"`, produces :BRF)

**SINTRAN quoting rule**: files being CREATED need `"quotes"`. Existing files do not.

### Debug symbols

Put `$DEBUG-MODE ON` before the outermost `MODULE` (or give `DEBUG-MODE` at the compiler prompt),
link as usual, then start `@DEBUGGER name` to set breaks and look at variables by name. Taken from
the manuals, not yet tried on our machines. The full story - the debugger commands, RT programs,
and the runtime messages `NO ON ROUTINEERROR HANDLER` and `STACK OVERFLOW AT` - is in
**[PLANC-DEBUGGING.md](PLANC-DEBUGGING.md)**.

---

## PLANC Syntax Summary

- `MODULE`/`ENDMODULE` structure -- NOT Pascal's PROGRAM/BEGIN/END
- Entry point: `PROGRAM : name` inside the module
- `INISTACK` must be called first to initialize the runtime stack
- `OUTPUT(device, format, variable)` writes to terminal (device 1)
- `'AL17'` = Alphanumeric, Left-justified, 17 characters
- `'$'` in output strings = CR+LF (newline). Literal `$` = `$$`
- **The `'ALn'` count INCLUDES the trailing `$`** -- `'CHAT: bye$'` is TEN characters. The number is
  a FIELD WIDTH, not a maximum: too small silently cuts the line off, too large pads it. Nothing in
  the compiler checks it, so a wrong width builds clean and only shows up on screen. Leaving the
  width off entirely (`'AL'`) sizes the field automatically and is the safer habit for anything
  whose length is not fixed and counted
- **A string literal cannot be stored into an element of a `BYTES` array.** `' ' =: buf(i)` does not
  compile -- `'x'` is a STRING, `buf(i)` is a BYTE. The compiler answers
  `*** ERROR - ILLEGAL DATA TYPE "BUF"`, blaming the ARRAY, which sends you to a declaration where
  nothing is wrong. Hold the character in a one-element `BYTES` and copy element to element. The
  same idiom is needed in the other direction to PRINT one byte, since `'ALn'` formats a string and
  handing it a byte prints the byte's NUMBER
- **Subarrays pass part of a buffer and their bounds may be VARIABLES** -- `name(0:len-1)`. Without
  one, a routine taking `BYTES` receives the array's whole declared length, leftovers included
- **A NAME DECLARED NOWHERE STILL COMPILES.** Measured: a BOOLEAN stored to and tested in two
  routines, declared in neither and not at module level, gave **`0 DIAGNOSTICS`** -- and the program
  ran with it permanently set. The signature is a flag that will not change: printing it
  immediately after `FALSE =: x` showed `1`. When a variable ignores an assignment, check the
  DECLARATION before debugging the logic. `SINTRAN/XMSG/tools/planc-lint.py` flags this
- **Two `EXPORT`s that agree in their first SEVEN characters are ONE name to the linker.** Ten
  characters to the compiler, seven across an `EXPORT`/`IMPORT`. It does NOT report a duplicate --
  it resolves every import to whichever entry it met first, so calls land in the wrong routine and
  read arguments that were never passed. Clean compile, clean link, and `LIST-ENTRIES-UNDEFINED`
  **empty**, because nothing is undefined. There is no message anywhere. See R114
- **`MAXINDEX` works on an array PARAMETER, and on a SUBARRAY** -- measured on D100.
  `MAXINDEX(a, 1) + 1` is the real length of a `BYTES` parameter, so a routine can bound itself
  instead of believing a size its caller passed. Not available inside a `STANDARD` routine. See R115
- **NEVER write a helper that takes `(text, textLen)`.** That signature makes every call site type
  a number nothing can check -- not the compiler, not the linker, not a test. It is right the day
  it is written and wrong the first time somebody edits the wording, and it still builds clean.
  Derive it instead: `MAXINDEX(text, 1) + 1 =: textLen` as the first line of the routine.
  **MEASURED 2026-08-31: 93 hand-typed lengths deleted from the chat product in one sitting** --
  29 `putWord`, 19 `logLine`, 18 `buildAdmText`, 15 `tryCmd`, 14 `cmdIs`, 12 `showIfMatch`. All 93
  happened to be correct, so this removed a hazard rather than a fault; auditing them first is a
  dozen lines of Python and tells you which of the two you are doing. Two preconditions, both easy
  to check: every call site must pass a **literal** (a caller handing a 64-byte buffer that holds a
  10-byte name would get 64, so where the text is a buffer the length is real information and must
  still be passed), and the routine must not be `STANDARD`. `planc-lint.py` keeps two named lists,
  `LITERAL_LENGTH_HELPERS` (deliberately empty -- that is the goal) and `DERIVES_ITS_OWN_LENGTH`,
  and refuses the old shape if it returns. See R121
- **One trap, three costumes.** A `'ALn'` field width, a hand-counted length beside a literal, and
  a start column written as `65 - length` are the same defect: a number a human counted, that
  nothing verifies, that builds clean when wrong. Treat any of the three as a signal to look for
  the other two. See R28 and R121
- **PLANC checks no array bounds, and that reaches the TESTS too.** A clamp that bounds only one of
  several fields is not a clamp (R116), and a test that overflows an array still PASSES, because its
  assertions land on bytes that are in bounds (R117). Assert the TOTAL length against the buffer
  size -- that is the check that catches it
- **A BOOLEAN will not pass where an INTEGER is declared.** `len <= 256` is a BOOLEAN, not a 0 or a
  1; write a second routine rather than trying to convert. See R118
- `BYTES : name := 'string'` declares byte array with implicit length
- `%` starts a comment to end of line
- `&` at end of line continues statement on next line
- `;` separates multiple statements on one line
- Assignment: `expression =: variable` (NOT `:=`)
- Not-equal: `><` (NOT `!=` or `<>`)
- All SINTRAN text files require CRLF line endings and even parity (bit 7)

---

## Getting the program INTO the system

A `:PROG` file that runs when you type its name is the beginning, not the end. SINTRAN has two
places a finished program properly belongs, and which one depends on what the program is for:

| | Started by | Terminal | Copies in memory | Stopped by |
|---|---|---|---|---|
| ordinary `:PROG` | `@NAME` | the caller's | one per run | ESC -- awkward, and impossible while blocked in a monitor call |
| **RT program** | `@RT NAME`, or at boot | **none** | one, resident | **`@ABORT NAME`** |
| **reentrant subsystem** | `@NAME` | the caller's | **one, SHARED by every user** | ends with the invocation |

A **server** wants to be an RT program -- nobody is logged in as it, and it must outlive every
terminal session. A **tool people run** wants to be reentrant -- many users at once, each with
their own data, one copy of the code.

Both routes, with the vendor manuals' mistakes corrected against a real machine, are in
**[PLANC-RT-AND-REENTRANT-PROGRAMS.md](PLANC-RT-AND-REENTRANT-PROGRAMS.md)**.

---

## Reference Manual

**Complete PLANC language documentation:**

**Location:** [Reference-Manuals/ND-60.117.5 EN PLANC Reference Manual.md](../../../Reference-Manuals/ND-60.117.5%20EN%20PLANC%20Reference%20Manual.md)

**Manual:** ND-60.117.5 EN PLANC Reference Manual (5th Ed., March 1986, Version G)

---

## Key Features

1. **MODULE-based:** Programs structured as modules with EXPORT/IMPORT
2. **Strong Typing:** Type-safe development with records, sets, pointers
3. **SINTRAN Integration:** Full monitor call access via `MONITOR_CALL()` or the named `MONn`
   routines - see [PLANC-MONITOR-CALLS.md](PLANC-MONITOR-CALLS.md) for how to find a call's
   name/number and the library load order (`MON-CALL-1BANK` before `PLANC-1BANK`)
4. **Compiler:** `@PLANC` on ND-100, `@PLANC-500` on ND-500
5. **XMSG IPC:** Via COSMOS XMP library routines (MON 200B not directly available) - see
   [COSMOS-XMP-LIBRARY.md](COSMOS-XMP-LIBRARY.md) for the full library documentation
6. **Inline Assembly:** `$*` prefix for MAC assembler statements

---

## See Also

- **[PLANC-RT-AND-REENTRANT-PROGRAMS.md](PLANC-RT-AND-REENTRANT-PROGRAMS.md)** - INSTALLING a
  finished program: as an RT program that holds no terminal and starts at boot, or as a reentrant
  subsystem every user shares one copy of. Where an RT program's name really comes from, the
  RT-LOADER sequence and the three places the manuals get it wrong, `@ABORT`, and
  `DUMP-PROGRAM-REENTRANT`
- **[PLANC-XMSG-PROGRAMMING-GUIDE.md](PLANC-XMSG-PROGRAMMING-GUIDE.md)** - Writing an XMSG client
  or server: hello world, every call, the patterns and the error numbers
- **[PLANC-MONITOR-CALLS.md](PLANC-MONITOR-CALLS.md)** - Doing SINTRAN MON calls from PLANC:
  the three call forms, finding a call's name/number/params, error handling (`ErrCode` /
  `ON ROUTINEERROR`), and the library load ORDER (`MON-CALL-1BANK` then `PLANC-1BANK`)
- **[COSMOS-XMP-LIBRARY.md](COSMOS-XMP-LIBRARY.md)** - The COSMOS XMP library: what it is, why
  MON 200B needs a wrapper, the full routine catalog, working IMPORT declarations, the proven
  D100 build recipe
- **[PLANC-XMSG-COMMUNICATION.md](PLANC-XMSG-COMMUNICATION.md)** - Talking to XMSG from PLANC:
  what is installed on a real machine, why the manual's `$INCLUDE` names do not match it, flags
  being BIT POSITIONS, and the array-bounds traps
- **[QUICK-START-EXAMPLES.md](../../QUICK-START-EXAMPLES.md)** - Complete working example
- **[LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md)** - Linking PLANC programs
- **[SINTRAN-DEVELOPER-GUIDE.md](../../SINTRAN-DEVELOPER-GUIDE.md)** - Master guide
- **[SCRIPT-GUIDE.md](../../Workflow/SCRIPT-GUIDE.md)** - MODE file automation
- **Reference Manual:** [ND-60.117.5 EN PLANC Reference Manual](../../../Reference-Manuals/ND-60.117.5%20EN%20PLANC%20Reference%20Manual.md)
- **Monitor Calls:** [ND-860228-2 SINTRAN III Monitor Calls](../../../Reference-Manuals/ND-860228-2-EN%20SINTRAN%20III%20Monitor%20Calls.md)

---

**Last Updated:** August 17, 2026  
**Version:** 2.0
