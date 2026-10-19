# SINTRAN III Development - Quick Start Examples

**Purpose:** Immediate validation examples for each supported language  
**Date:** October 17, 2025  
**Status:** Complete

---

## Overview

This document provides minimal "Hello World" examples for each programming language supported on SINTRAN III. These examples are designed for immediate testing and validation.

**Languages covered:**
- NPL (NORD Programming Language)
- MAC (Assembler)
- C (CC-100/CC-500)
- PLANC
- FORTRAN
- PASCAL
- COBOL
- BASIC

---

## 1. NPL - NORD Programming Language

### 1.1 Hello World (NPL)

**File:** `HELLO-NPL:NPL`

```npl
% Simple Hello World in NPL

SUBR HELLO, START

INTEGER ARRAY MSG:='HELLO FROM NPL!', 15, 12

START:
    A:=43                    % WRTSW monitor call
    T:="MSG"
    *MONITOR 43
    A:=3                     % EXIT monitor call
    *MONITOR 3

RBUS
```

### 1.2 Build and Run

```bash
@NPL HELLO-NPL:NPL           # Compile to MAC
@MAC HELLO-NPL:MAC           # Assemble to BRF
@NRL                         # Start linker
*PROG-FILE "HELLO-NPL"
*LOAD HELLO-NPL
*EXIT
@HELLO-NPL                   # Run program
```

**Expected output:**
```
HELLO FROM NPL!
```

---

## 2. MAC - Assembler

### 2.1 Hello World (MAC)

**File:** `HELLO-MAC:MAC`

```mac
        % Simple Hello World in MAC Assembler
        
START,  LDA     =43          % WRTSW monitor call
        LDT     I (MSG)      % Message address
        MONITOR 43           % Write string
        LDA     =3           % EXIT monitor call
        MONITOR 3            % Exit program
        
MSG,    'HELLO FROM MAC!'
        15, 12               % CR, LF
        
        )ENTR START
```

### 2.2 Build and Run

```bash
@MAC HELLO-MAC:MAC           # Assemble to BRF
@NRL                         # Start linker
*PROG-FILE "HELLO-MAC"
*LOAD HELLO-MAC
*EXIT
@HELLO-MAC                   # Run program
```

**Expected output:**
```
HELLO FROM MAC!
```

---

## 3. C - CC-100/CC-500

> For the ND-500 C compiler used today (NC), see section 4b below. The material here is for the older CC-100/CC-500 compiler.

### 3.1 Hello World (C)

**File:** `HELLO-C:C`

```c
/* Simple Hello World in C */

#include <stdio.h>

main()
{
    printf("HELLO FROM C!\n");
    return 0;
}
```

### 3.2 Build and Run

```bash
@CC-100 HELLO-C:C            # Compile C to BRF
@NRL                         # Start linker
*IMAGE 100                   # ND-100 image
*PROG-FILE "HELLO-C"
*LOAD CC-2HEADER             # C runtime header
*LOAD HELLO-C                # Your program
*LOAD CC-2BANK               # C runtime library
*LOAD CC-2TRAILER            # C runtime trailer
*EXIT
@HELLO-C                     # Run program
```

**Expected output:**
```
HELLO FROM C!
```

---

## 4. PLANC

### 4.1 Hello World (PLANC)

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

**PLANC syntax notes:**
- `MODULE`/`ENDMODULE` structure -- NOT Pascal's PROGRAM/BEGIN/END
- Entry point: `PROGRAM : name` inside the module
- `INISTACK` must be called first to initialize the runtime stack
- `OUTPUT(device, format, variable)` writes to terminal (device 1)
- `'AL17'` = Alphanumeric, Left-justified, 17 characters
- `'$'` outputs a CR+LF (newline)
- `BYTES : name := 'string'` declares byte array with implicit length from initializer

### 4.2 Build and Run

**Method 1: Interactive build (verified on ND-100, PLANC Version E)**

```bash
@PLANC
PROG-FILE "HELLO"
COMPILE HELLO:PLNC,"HELLO:LIST","HELLO"
EXIT
@HELLO
```

The `COMPILE` command takes three parameters:
1. `HELLO:PLNC` -- source file (exists, no quotes needed)
2. `"HELLO:LIST"` -- listing output (created, needs quotes)
3. `"HELLO"` -- object file (created, needs quotes, produces :BRF)

`PROG-FILE "HELLO"` tells the compiler to also create `HELLO:PROG` directly.
On `EXIT`, the PLANC runtime is linked automatically.

This produces three files:
- `HELLO:PROG` -- executable (run with `@HELLO`)
- `HELLO:BRF` -- binary relocatable file
- `HELLO:LIST` -- compiler listing with line numbers

**Method 2: Automated build (MODE file)**

**File:** `DO-BUILD:MODE`

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

**Method 3: Separate compile and link**

```bash
@PLANC
COMPILE HELLO:PLNC,"HELLO:LIST","HELLO"
EXIT
@NRL
PROG-FILE "HELLO"
LOAD HELLO
LOAD PLANC-1BANK
EXIT
@HELLO
```

**Expected output:**
```
HELLO FROM PLANC!
```

---

## 4b. ND-500 / ND-5000: NC (C) and PLANC-500 [measured 05-OCT-2026]

Under real SINTRAN III VSX/500 L on the nd100x emulator with an ND-5000. Section 3 is the older
CC-100/CC-500 compiler; the ND-500 C compiler today is NC (Norsk Data C, version A06). Full
chapters: [ND500/README.md](ND500/README.md), [ND500/NC-C-COMPILER-GUIDE.md](ND500/NC-C-COMPILER-GUIDE.md),
[ND500/PLANC-500-COMPILER-GUIDE.md](ND500/PLANC-500-COMPILER-GUIDE.md),
[ND500/ND-LINKER-PRACTICAL-GUIDE.md](ND500/ND-LINKER-PRACTICAL-GUIDE.md).

Source files (CR LF line ends), `HELLO:C`:

```c
main()
{
    printf("HELLO FROM C!\n");
}
```

`PHELLO:PLNC`:

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

Session (type each line at its prompt):

```
@SET-TERMINAL-TYPE,,93
@CREATE-FILE PHELLO:LIST,0
@CREATE-FILE PHELLO:NRF,0
@ND-500
ND-5000: DEFINE-STANDARD-DOMAIN CAT-CAT5-B,CAT-CAT5-B06     (after every cold start)
ND-5000: DEFINE-STANDARD-DOMAIN NC-A,NC-A06                 (after every cold start)
ND-5000: PLANC-500-G00
*COMPILE PHELLO:PLNC,PHELLO:LIST,PHELLO:NRF
     11 LINES COMPILED.       0 DIAGNOSTICS.
*EXIT
ND-5000: NC-A06
NC: COMPILE HELLO,"HELLO","HELLO"
NC: EXIT
@ND-500
ND-5000: LINKER-B01
NDL: SET-ADVANCED-MODE
NDL(ADV): OPEN-DOMAIN "HELLO"
NDL(ADV): LOAD HELLO
NDL(ADV): CLOSE
NDL(ADV): OPEN-DOMAIN "PHELLO"
NDL(ADV): LOAD PHELLO
NDL(ADV): CLOSE
NDL(ADV): EXIT
ND-5000: HELLO:DOM
HELLO FROM C!
ND-5000: PHELLO:DOM
HELLO FROM PLANC!
```

`CLOSE` runs the runtime auto job by itself (for the C object it is `LINKER-AUTO-FORT:JOB`, which
loads `NC-LIB` and `CAT-LIB`). The file `HELLO:DOM` is about 6.3 MB but has 23 pages on disk; see the
linker chapter for why and for `COMPRESS`.

## 5. FORTRAN

### 5.1 Hello World (FORTRAN)

**File:** `HELLO:SYMB` (must have CRLF line endings and even parity)

Source files use `:SYMB` extension (default) or `:FORT`.

```fortran
      PROGRAM HELLO
      WRITE(1, 10)
   10 FORMAT(1X, 'HELLO FROM FORTRAN!')
      END
```

**FORTRAN syntax notes:**
- Fixed-form: column 1 = `C` for comment, columns 1-5 = label, column 6 = continuation, 7-72 = code
- Unit 1 = user's terminal on ND-100 (NOT unit 6)
- `1X` = one blank for carriage control (advance one line)
- `END` terminates the program unit

### 5.2 Build and Run

**Verified on ND-100, compiler 203053F02.**

```bash
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

- `@FORT` -- ANSI 77 FORTRAN compiler (203053F02)
- `SEP OFF` -- 1-bank mode (SEPARATE-DATA OFF)
- `COMP source,,"object"` -- source unquoted (exists), object quoted (created)
- `@BRF-LINKER` -- the ND BRF linker (not NRL)
- `LOAD FORT-1B` -- FORTRAN 1-bank runtime (must be loaded last)

**Automated build (MODE file):**

File: `DO-BUILD:MODE`

```mode
@DELETE-FILE HELLO:PROG
@DELETE-FILE HELLO:BRF
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

Run with: `@MODE DO-BUILD:MODE,,`

**Expected output:**
```
 HELLO FROM FORTRAN!
```

---

## 6. PASCAL

### 6.1 Hello World (PASCAL)

**File:** `HELLO-PAS:PAS`

```pascal
PROGRAM HELLO(OUTPUT);

BEGIN
    WRITELN('HELLO FROM PASCAL!')
END.
```

### 6.2 Build and Run

```bash
@PASCAL                      # Start Pascal compiler
COMPILE HELLO-PAS:PAS
EXIT
@NRL                         # Start linker
*PROG-FILE "HELLO-PAS"
*LOAD HELLO-PAS
*LOAD PASCALLIB              # Pascal runtime library
*EXIT
@HELLO-PAS                   # Run program
```

**Expected output:**
```
HELLO FROM PASCAL!
```

---

## 7. COBOL

### 7.1 Hello World (COBOL)

**File:** `HELLO-COB:COB`

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       
       PROCEDURE DIVISION.
       MAIN-PARAGRAPH.
           DISPLAY "HELLO FROM COBOL!".
           STOP RUN.
```

### 7.2 Build and Run

```bash
@COBOL                       # Start COBOL compiler
HELLO-COB:COB
EXIT
@NRL                         # Start linker
*PROG-FILE "HELLO-COB"
*LOAD HELLO-COB
*LOAD COBOLLIB               # COBOL runtime library
*EXIT
@HELLO-COB                   # Run program
```

**Expected output:**
```
HELLO FROM COBOL!
```

---

## 8. BASIC

### 8.1 Hello World (BASIC)

**File:** `HELLO-BAS:BAS`

```basic
10 PRINT "HELLO FROM BASIC!"
20 END
```

### 8.2 Build and Run

```bash
@BASIC                       # Start BASIC
RUN HELLO-BAS:BAS
EXIT
```

**Expected output:**
```
HELLO FROM BASIC!
```

**Note:** BASIC is typically interpreted, not compiled.

---

## Quick Reference Table

| Language | Source Ext | Compiler | Output | Linker Needed | Runtime Lib |
|----------|-----------|----------|--------|---------------|-------------|
| **NPL** | `:NPL` | `@NPL` | `:MAC` → `:BRF` | Yes | No |
| **MAC** | `:MAC` | `@MAC` | `:BRF` | Yes | No |
| **C** | `:C` | `@CC-100` | `:BRF` | Yes | Yes (CC-2BANK) |
| **PLANC** | `:SYMB` or `:PLNC` | `@PLANC-100` | `:BRF` | Yes (or use `$PROG-FILE`) | Yes (PLANC-1BANK or PLANC-2BANK) |
| **FORTRAN** | `:SYMB` or `:FORT` | `@FORT` | `:BRF` | Yes (BRF-LINKER) | Yes (FORT-1B or FORT-2B) |
| **PASCAL** | `:PAS` | `@PASCAL` | `:BRF` | Yes | Yes (PASCALLIB) |
| **COBOL** | `:COB` | `@COBOL` | `:BRF` | Yes | Yes (COBOLLIB) |
| **BASIC** | `:BAS` | `@BASIC` | Interpreted | No | Built-in |

---

## Common Build Patterns

### Pattern 1: Simple Single-File (NPL, MAC)

```bash
# Compile
@<COMPILER> SOURCE:EXT

# Assemble (if NPL)
@MAC SOURCE:MAC

# Link
@NRL
*PROG-FILE "PROGRAM"
*LOAD SOURCE
*EXIT

# Run
@PROGRAM
```

### Pattern 2: With Runtime Library (C, FORTRAN, PASCAL, COBOL)

```bash
# Compile
@<COMPILER> SOURCE:EXT

# Link with runtime
@NRL
*IMAGE 100
*PROG-FILE "PROGRAM"
*LOAD <RUNTIME-HEADER>    # If needed
*LOAD SOURCE
*LOAD <RUNTIME-LIB>
*LOAD <RUNTIME-TRAILER>   # If needed
*EXIT

# Run
@PROGRAM
```

### Pattern 3: Using MODE Files (Automation)

**File:** `BUILD:MODE`

```mode
@NPL SOURCE:NPL
@MAC SOURCE:MAC
@NRL
PROG-FILE "PROGRAM"
LOAD SOURCE
EXIT
```

**Run:**
```bash
@MODE BUILD:MODE
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| **FILE NOT FOUND** | Source file missing | Check filename and extension |
| **SYNTAX ERROR** | Code syntax wrong | Check language syntax |
| **UNDEFINED SYMBOL** | External reference | Add library or define symbol |
| **OUT OF MEMORY** | Program too large | Reduce size or use segments |
| **RUNTIME ERROR** | Program logic error | Use debugger to trace |

### Verification Steps

1. **Compile successful?** - No errors reported
2. **Link successful?** - PROG file created
3. **File exists?** - Check with `@LI` (list files)
4. **Executable?** - Check with `@TY PROGRAM:PROG` (type file)
5. **Runs?** - Execute with `@PROGRAM`

---

## Next Steps

After validating these examples:

1. **NPL:** See [NPL-DEVELOPER-GUIDE.md](Languages/System/NPL-DEVELOPER-GUIDE.md) for complete language guide
2. **MAC:** See [MAC-DEVELOPER-GUIDE.md](Languages/System/MAC-DEVELOPER-GUIDE.md) for assembler details
3. **C:** See [C-DEVELOPER-GUIDE.md](Languages/Application/C-DEVELOPER-GUIDE.md) for C compiler guide
4. **PLANC:** See [PLANC-DEVELOPER-GUIDE.md](Languages/Application/PLANC-DEVELOPER-GUIDE.md) for PLANC guide
5. **Linking:** See [LINKING-GUIDE.md](Workflow/LINKING-GUIDE.md) for advanced linking
6. **Automation:** See [SCRIPT-GUIDE.md](Workflow/SCRIPT-GUIDE.md) for MODE files

---

## File Locations

**Quick Start Examples:** Current directory  
**Kernel Documentation:** `SINTRAN\OS\`  
**Developer Guides:** Will be created in Phase 2

---

**Last Updated:** October 17, 2025  
**Version:** 1.0  
**Status:** Complete

