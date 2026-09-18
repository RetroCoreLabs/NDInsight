# MAC Assembler Developer Guide

**NORD-10 Macro Assembler - Complete Reference**

**Version:** 1.0  
**Date:** October 17, 2025  
**Status:** Complete

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [MAC Assembler Overview](#2-mac-assembler-overview)
3. [Assembly Language Syntax](#3-assembly-language-syntax)
4. [Addressing Modes](#4-addressing-modes)
5. [Assembler Directives](#5-assembler-directives)
6. [Symbol Management](#6-symbol-management)
7. [Expressions](#7-expressions)
8. [Macro Processor](#8-macro-processor)
9. [Practical Examples](#9-practical-examples)
10. [Common Patterns](#10-common-patterns)
11. [Error Messages](#11-error-messages)
12. [Integration with NPL](#12-integration-with-npl)

---

## Installing MAC

MAC (both 48-bit and 32-bit floating-point builds) ships as part of **Subsystem Package II**
(`ND-210400`), Norsk Data's standard developer-tools bundle for SINTRAN III. Install that
product first if MAC is not already on the system — full procedure (floppy, prerequisites, the
`@DUMP-REENTRANT` addresses for every module, and how to keep it loaded across a cold start) is
in [ND-210400B — Subsystem Package II, version B](../../../Installation/Software/ND-210400/ND-210400B/README.md).

---

## 1. Introduction

### 1.1 What is MAC?

**MAC** is the macro assembler for the NORD-10/100 computer systems. It translates assembly language programs into relocatable binary format (BRF) files that can be linked by NRL (NORD Relocating Loader).

**Key features:**
- **Two-pass assembler** - First pass builds symbol table, second pass generates code
- **Macro processing** - Supports macro definition and expansion
- **Relocation support** - Generates relocatable code for flexible loading
- **External references** - Supports multi-module programs
- **Comprehensive** - Full access to all NORD-10 instructions

### 1.2 When to Use MAC

**Use MAC directly for:**
- Hand-optimized assembly code
- Device drivers and interrupt handlers
- Boot loaders and low-level code
- Learning NORD-10 architecture

**Use NPL instead for:**
- Application programs
- Maintainable system code
- Team development projects
- Complex logic

### 1.3 Build Process

```
Source.MAC → MAC Assembler → Object.BRF → NRL Linker → Executable.PROG
```

---

## 2. MAC Assembler Overview

### 2.1 Command Format

**Basic invocation:**
```
@MAC SOURCE:MAC
```

**With options:**
```
@MAC SOURCE:MAC, LISTING:LST
@MAC SOURCE:MAC, , (XREF)           # Cross-reference
@MAC SOURCE:MAC, , (MAP)            # Memory map
@MAC SOURCE:MAC, LISTING:LST, (XREF,MAP)  # Multiple options
```

### 2.2 Assembly Process

**Pass 1:**
- Scans source code
- Builds symbol table
- Calculates addresses
- Detects undefined symbols

**Pass 2:**
- Generates object code
- Resolves relocatable references
- Creates BRF file
- Produces listing (if requested)

### 2.3 Output Files

| Extension | Description | Format |
|-----------|-------------|--------|
| **`.BRF`** | Binary Relocatable Format | Binary object code |
| **`.LST`** | Listing file | Human-readable assembly listing |
| **`.MAP`** | Memory map | Symbol addresses and usage |
| **`.XRF`** | Cross-reference | Symbol usage report |

---

## 3. Assembly Language Syntax

### 3.1 Line Format

```
[LABEL,] [OPERATION] [OPERAND] [% COMMENT]
```

**Components:**
- **Label:** Optional identifier followed by comma
- **Operation:** Instruction mnemonic or directive
- **Operand:** Instruction operand(s) or directive parameters
- **Comment:** Text starting with `%`

### 3.2 Labels

```mac
START,   LDA  =100       % Label 'START' at this instruction
LOOP,    ADD  COUNT      % Label 'LOOP' at this instruction
DATA,    0, 1, 2, 3      % Label 'DATA' marks data area
```

**Rules:**
- Must start with letter or digit
- Can contain letters, digits, spaces
- First 5 characters significant
- Followed by comma
- Case insensitive

### 3.3 Instructions

```mac
% Format: MNEMONIC OPERAND

LDA    VALUE          % Load A register
ADD    =10            % Add immediate value 10
STA    RESULT         % Store A register
JMP    LOOP           % Jump to LOOP
```

### 3.4 Comments

```mac
% Full line comment

LDA =100     % Inline comment after instruction
```

### 3.5 Literals

**Octal (default):**
```mac
LDA =177777      % Octal value
```

**Decimal:**
```mac
LDA =D100        % Decimal value 100
```

**Binary:**
```mac
LDA =B1010       % Binary value
```

**Character:**
```mac
LDA ='A'         % ASCII value of 'A'
```

**String:**
```mac
MSG, 'HELLO'     % String data
```

---

## 4. Addressing Modes

### 4.1 Addressing Mode Summary

| Mode | Syntax | Description | Example |
|------|--------|-------------|---------|
| **Immediate** | `=VALUE` | Literal value | `LDA =100` |
| **Direct** | `LABEL` | Direct address | `LDA COUNT` |
| **Indirect** | `I (LABEL)` | Indirect via address | `LDA I (PTR)` |
| **Indexed** | `LABEL,X` | X-indexed | `LDA TABLE,X` |
| **B-relative** | `LABEL,B` | B-relative | `LDA FIELD,B` |
| **P-relative** | `LABEL` | PC-relative (auto) | `JMP LOOP` |

### 4.2 Immediate Addressing

```mac
LDA =100         % Load literal 100 (octal)
LDA =D100        % Load literal 100 (decimal)
LDA =B11110000   % Load binary value
LDA ='A'         % Load ASCII 'A'
```

### 4.3 Direct Addressing

```mac
COUNT, 0         % Define variable COUNT

START, LDA COUNT      % Load from COUNT
       ADD =1         % Add 1
       STA COUNT      % Store to COUNT
```

### 4.4 Indirect Addressing

```mac
PTR,   ADDRESS   % Pointer contains address

FETCH, LDA I (PTR)    % Load from address in PTR
       STA VALUE      % Store result
```

### 4.5 Indexed Addressing

```mac
TABLE, 100, 200, 300, 400     % Array of values

ACCESS, LDX =2                % X = index 2
        LDA TABLE,X           % Load TABLE[2] = 300
```

### 4.6 B-Relative Addressing

```mac
% Used with NPL BASE/ESAB structures

STRUCT, % B points here
        INTEGER FIELD1        % Offset 0
        INTEGER FIELD2        % Offset 1
        INTEGER FIELD3        % Offset 2

ACCESS, LDA FIELD2,B          % Access FIELD2 via B register
```

---

## 5. Assembler Directives

### 5.1 `)FILL` - Fill to Boundary

**Purpose:** Fill unused memory with zeros up to a page boundary (2048 words).

```mac
SUBR1,  LDA =100
        EXIT
        )FILL              % Fill to page boundary
        
SUBR2,  LDA =200          % Starts on next page
        EXIT
        )FILL
```

**Usage in NPL:**
```npl
SUBR ROUTINE
    % Code here
    EXIT
RBUS                      % Generates )FILL
```

### 5.2 `)KILL` - Remove Symbols

**Purpose:** Remove symbols from symbol table (local symbols in NPL subroutines).

```mac
LOCAL1, 0
LOCAL2, 0

ROUTINE, LDA LOCAL1
         ADD LOCAL2
         EXIT
         )FILL
         )KILL LOCAL1 LOCAL2    % Remove from table
```

**Usage in NPL:**
```npl
SUBR ROUTINE
INTEGER LOCAL1, LOCAL2    % Local variables
ROUTINE: % code
    EXIT
RBUS                      % Generates )KILL LOCAL1 LOCAL2
```

### 5.3 `)ZERO` - Zero Memory

**Purpose:** Reserve and initialize memory to zero.

```mac
BUFFER, )ZERO 100         % Reserve 100 words, initialized to 0
```

### 5.4 `)PCL` - Print Control Line

**Purpose:** Control listing output (seen in SINTRAN source).

```mac
)PCL LIST                 % Enable listing
CODE,   LDA =100
)PCL NOLIST              % Disable listing
```

### 5.5 `)LINE` - Line Number Control

**Purpose:** Set line number for error reporting (used in batch compilation).

```mac
)LINE 1000                % Set line number to 1000
```

### 5.6 `)9SLPL` - Special Control

**Purpose:** SINTRAN-specific control directive for batch assembly.

```mac
)9SLPL                    % Special processing control
```

### 5.7 `)9ASSM` - Assembly Mode

**Purpose:** Set assembly mode parameters.

```mac
)9ASSM 100,LIST-FILE,(OTS-CRS-BRF-1)FILE
```

### 5.8 `)9TSS` - TSS Mode

**Purpose:** Timesharing System mode control.

```mac
?)9TSS                    % Enter TSS mode
```

### 5.9 `)ENTR` - Entry Point

**Purpose:** Define program entry point.

```mac
START,  LDA =100
        EXIT
        
        )ENTR START       % START is entry point
```

### 5.10 `)EXTR` - External Reference

**Purpose:** Declare external symbols.

```mac
        )EXTR ROUTINE     % ROUTINE defined in another file
        
CALL,   JMP ROUTINE       % Can now reference ROUTINE
```

### 5.11 Data Definition

```mac
% Single word
COUNT,  0

% Multiple words
TABLE,  100, 200, 300

% String
MSG,    'HELLO'

% Reserve space
BUFFER, 0, 0, 0, 0        % 4 words
```

### 5.12 Location Counter

```mac
        =*+100            % Reserve 100 words
        
BUFFER, =*                % BUFFER = current address
        =*+1000           % Reserve 1000 words
```

---

## 6. Symbol Management

### 6.1 Symbol Types

| Type | Scope | Example | Usage |
|------|-------|---------|-------|
| **Local** | Single module | `LOOP, COUNT` | Internal labels/data |
| **Entry** | Exported | `)ENTR START` | Entry points for linker |
| **External** | Imported | `)EXTR ROUTINE` | References to other modules |
| **Global** | System | `MONITOR` | System symbols |

### 6.2 Symbol Table

**Maximum symbols:** Typically 1000-2000 symbols per module

**Symbol format:**
- Name: First 5 characters significant
- Value: 16-bit address or constant
- Type: Relocatable or absolute
- Attributes: Entry, External, Local

### 6.3 Forward References

```mac
% Forward reference - allowed
START,  JMP FORWARD       % FORWARD not yet defined

% Later in code
FORWARD, LDA =100         % Now defined
```

**Phase errors:** Occur when symbol value changes between Pass 1 and Pass 2.

---

## 7. Expressions

### 7.1 Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| **+** | Addition | `ADDR+10` |
| **-** | Subtraction | `END-START` |
| ***** | Multiplication | `SIZE*3` |
| **/** | Division | `TOTAL/COUNT` |
| **&** | Logical AND | `VALUE&177` |
| **!** | Logical OR | `FLAG!BIT` |
| **^** | Logical XOR | `A^B` |

### 7.2 Expression Evaluation

```mac
% Simple arithmetic
LDA =100+50              % Load 150

% Symbol arithmetic
SIZE, END-START          % Calculate size

% Complex expression
LDA =((VALUE+10)*2)/4
```

### 7.3 Relocation

**Absolute:**
```mac
LDA =100                 % Absolute value, not relocated
```

**Relocatable:**
```mac
LDA LABEL                % LABEL address relocated by linker
```

**Mixing:**
```mac
LDA LABEL+10             % Relocatable + absolute = relocatable
SIZE, END-START          % Relocatable - relocatable = absolute
```

---

## 8. Macro Processor

### 8.1 Macro Definition

```mac
% Define macro
        )MACRO SAVE       % Macro name SAVE
        STA TEMP          % Macro body
        )ENDM             % End macro
        
% Use macro
        SAVE              % Expands to: STA TEMP
```

### 8.2 Macros with Parameters

```mac
% Define macro with parameter
        )MACRO LOAD #ARG
        LDA #ARG
        )ENDM
        
% Use with parameter
        LOAD COUNT        % Expands to: LDA COUNT
        LOAD =100         % Expands to: LDA =100
```

### 8.3 Multi-Parameter Macros

```mac
        )MACRO SWAP #A,#B
        LDA #A
        LDT #B
        STA #B
        STT #A
        )ENDM
        
        SWAP VAR1,VAR2    % Swap two variables
```

### 8.4 Conditional Assembly

```mac
        )IF DEBUG
        LDA ERROR_CODE
        STA LOG
        )ENDIF
```

---

## 9. Practical Examples

### 9.1 Simple Program

```mac
% Hello World in pure MAC

START,  LDT I (MSG)           % Message address
        MONITOR 162           % OutString - write the message (MON 162B)
        MONITOR 0             % ExitFromProgram

MSG,    'HELLO FROM MAC!'
        15, 12                % CR, LF

        )ENTR START
```

> **Monitor numbers corrected.** Earlier drafts of this example used
> `MONITOR 43` for "write string" and `MONITOR 3` for "exit"; per the
> repo's own monitor-call reference those are **CloseFile** (43) and the
> **No-Wait switch** (3). String output is **OutString = MON 162B** and
> program exit is **ExitFromProgram = MON 0**. (For the `@MAC` *reentrant*
> subsystem the mnemonic is `MON n`, not `MONITOR n` — see the
> [MAC Cookbook](MAC-COOKBOOK.md).)

### 9.2 Subroutine

```mac
% Subroutine to multiply A by 10

MUL10,  LDT A                % T = A
        LDA =9               % A = 9
        MPY T                % A = A * T = A * 9
        ADD T                % A = A + T = A * 10
        JMP I 0              % Return (JMP I 0)

% Call subroutine
MAIN,   LDA VALUE
        JSR MUL10            % Call subroutine
        STA RESULT
```

### 9.3 Loop Example

```mac
% Sum array elements

SUM,    0                    % Result

LOOP,   LDX =0               % X = 0 (index)
        LDA =0               % A = 0 (sum)
        
NEXT,   ADD TABLE,X          % Add TABLE[X]
        ADX =1               % X++
        LDT =100             % T = array size
        SAX                  % Compare X with A
        JPL NEXT             % If X < 100, continue
        
        STA SUM              % Store result
        EXIT

TABLE,  1, 2, 3, 4, 5        % Array data
        % ... 95 more elements
```

### 9.4 Data Structures

```mac
% Linked list element

ELEMENT, 0                   % NEXT pointer (offset 0)
         0                   % DATA1 (offset 1)
         0                   % DATA2 (offset 2)

% Access
START,  LDA I (ELEMENT)      % Get NEXT pointer
        LDX ELEMENT          % X = address of element
        LDA 1,X              % Get DATA1 (offset 1)
        LDA 2,X              % Get DATA2 (offset 2)
```

---

## 10. Common Patterns

### 10.1 Register Save/Restore

```mac
SUBR,   STA SAVE_A          % Save A
        LDT SAVE_T          % Save T
        
        % ... code ...
        
        LDA SAVE_A          % Restore A
        LDT SAVE_T          % Restore T
        JMP I 0             % Return

SAVE_A, 0
SAVE_T, 0
```

### 10.2 Parameter Passing

```mac
% Parameters passed via memory locations

FUNC,   LDA PARAM1          % Get parameter 1
        ADD PARAM2          % Add parameter 2
        STA RESULT          % Store result
        JMP I 0             % Return

% Call
MAIN,   LDA =10
        STA PARAM1
        LDA =20
        STA PARAM2
        JSR FUNC
        LDA RESULT          % Get result

PARAM1, 0
PARAM2, 0
RESULT, 0
```

### 10.3 Table Lookup

```mac
LOOKUP, LDX INDEX           % X = table index
        LDA TABLE,X         % Load TABLE[INDEX]
        STA VALUE
        EXIT

INDEX,  5
TABLE,  10, 20, 30, 40, 50, 60, 70, 80
VALUE,  0
```

### 10.4 Bit Manipulation

```mac
% Set bit 5
        LDA FLAGS
        BSET ONE DA 40      % Set bit 5 (octal 40 = bit 5)
        STA FLAGS

% Clear bit 5
        LDA FLAGS
        BSET ZRO DA 40      % Clear bit 5
        STA FLAGS

% Test bit 5
        LDA FLAGS
        BSKP ONE DA 40      % Skip if bit 5 is 1
        JMP BIT_CLEAR

FLAGS,  0
```

---

## 11. Error Messages

### 11.1 Common Assembly Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| **UNDEFINED SYMBOL** | Symbol not defined | Define symbol or add )EXTR |
| **MULTIPLY DEFINED** | Symbol defined twice | Remove duplicate definition |
| **PHASE ERROR** | Symbol value changed | Check forward references |
| **VALUE ERROR** | Invalid expression value | Check arithmetic |
| **RELOCATION ERROR** | Illegal relocation mix | Check address calculation |
| **SYNTAX ERROR** | Invalid syntax | Check instruction format |
| **OPERAND ERROR** | Wrong operand | Check instruction requirements |

### 11.2 Warning Messages

| Warning | Meaning | Action |
|---------|---------|--------|
| **TRUNCATED VALUE** | Value too large | Check if intentional |
| **FORWARD REFERENCE** | Symbol not yet defined | Usually OK |
| **UNUSED SYMBOL** | Symbol defined but not used | Remove if unneeded |

---

## 12. Integration with NPL

### 12.1 NPL to MAC Translation

**NPL Code:**
```npl
INTEGER VAR1, VAR2
SUBR ROUTINE
    ROUTINE: A:=VAR1 + VAR2
    EXIT
RBUS
```

**Generated MAC Code:**
```mac
VAR1, 0
VAR2, 0

ROUTINE, LDA I (VAR1)
         ADD I (VAR2)
         EXIT
         )FILL
```

### 12.2 NPL Assembly Directives

**From NPL:**
```npl
*)FILL                  % Passed to MAC as )FILL
*)KILL VAR1 VAR2        % Passed to MAC as )KILL VAR1 VAR2
*=*+100                 % Passed to MAC as =*+100
```

### 12.3 Mixed NPL and MAC

**NPL with inline MAC:**
```npl
SUBR ROUTINE
INTEGER LOCAL
ROUTINE:
    A:=LOCAL
    *IOF                % MAC instruction
    *STZTX              % MAC instruction
    *ION                % MAC instruction
    EXIT
RBUS
```

**Generated MAC:**
```mac
LOCAL, 0

ROUTINE, LDA LOCAL
         IOF
         STZTX
         ION
         EXIT
         )FILL
         )KILL LOCAL
```

---

## Quick Reference

### Essential Instructions

| Instruction | Description | Example |
|-------------|-------------|---------|
| **LDA** | Load A | `LDA VALUE` |
| **STA** | Store A | `STA RESULT` |
| **ADD** | Add to A | `ADD COUNT` |
| **SUB** | Subtract from A | `SUB TEMP` |
| **AND** | Logical AND | `AND MASK` |
| **OR** | Logical OR | `OR FLAGS` |
| **JMP** | Jump | `JMP LOOP` |
| **JSR** | Jump subroutine | `JSR FUNC` |
| **EXIT** | Return | `EXIT` |

### Essential Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| **)FILL** | Fill to page | `)FILL` |
| **)KILL** | Remove symbols | `)KILL VAR` |
| **)ENTR** | Entry point | `)ENTR START` |
| **)EXTR** | External ref | `)EXTR FUNC` |
| **)MACRO** | Define macro | `)MACRO NAME` |

---

## See Also

- **[MAC-COOKBOOK.md](MAC-COOKBOOK.md)** - Practitioner's companion: what actually assembles and runs through `@MAC` on SINTRAN III (verified source encoding, addressing deref ladder, monitor-call ABI, gotcha catalogue)
- **[NPL-DEVELOPER-GUIDE.md](NPL-DEVELOPER-GUIDE.md)** - NPL language guide
- **[LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md)** - NRL linker guide
- **[QUICK-START-EXAMPLES.md](../../QUICK-START-EXAMPLES.md)** - Hello World examples
- **Kernel Documentation:** `SINTRAN\OS\`

---

**Last Updated:** October 17, 2025  
**Version:** 1.0  
**Status:** Complete

