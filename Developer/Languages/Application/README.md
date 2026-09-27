# Application Programming Languages

High-level programming languages for business, scientific, and general-purpose application development on NORD/SINTRAN systems.

---

## 📝 Application Languages

### [C-DEVELOPER-GUIDE.md](C-DEVELOPER-GUIDE.md)
**C Programming Language**

Modern, portable system and application programming language.

**Key Features:**
- Pointer manipulation
- Structured programming
- Standard library
- Portable code
- System utilities

**Use Cases:**
- Cross-platform applications
- System utilities
- Data structures
- Algorithm implementation
- Modern programming

**Reference Manual:** `../../../Reference-Manuals/ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual.md`

---

### START HERE FOR PLANC: [HOW-TO-PROGRAM-PLANC.md](HOW-TO-PROGRAM-PLANC.md)

**Read this before writing or changing any PLANC.** The working guide: the language traps that
compile clean and go wrong later, how to call a monitor call without killing the program, the
XMSG receive rules, RT programs, and the build loop that tells you whether it actually worked.
Written after a two-thousand-line program took days, with every avoidable cost turned into a rule.

Its companions, extracted from the manuals as DATA so tools can use them too:

| file | what it holds |
|---|---|
| [PLANC-LANGUAGE-RULES.md](PLANC-LANGUAGE-RULES.md) | 113 checkable rules, each with a detection heuristic and its false-positive traps |
| [monitor-calls.json](monitor-calls.json) | 258 monitor calls - number, parameters, types, directions, and which 54 the runtime supplies as `MONn` |
| [PLANC-MONITOR-CALL-RULES.md](PLANC-MONITOR-CALL-RULES.md) | how to call them from PLANC safely |
| [xmp-api.json](xmp-api.json) | 54 XMP routines and 397 constants, from ND's own shipped declarations |
| [PLANC-XMSG-API-RULES.md](PLANC-XMSG-API-RULES.md) | the XMSG rules, each with a linter recipe |

`SINTRAN/XMSG/tools/planc-lint.py` reads `xmp-api.json` and checks sources against it. Run it
before every push - it is free, and it catches on Windows what otherwise costs a ten-minute round
trip to the machine.

---

### [PLANC-DEVELOPER-GUIDE.md](PLANC-DEVELOPER-GUIDE.md)
**PLANC (PLAN-oriented C)**

Structured programming language with strong typing and modularity.

**Key Features:**
- Module system
- Strong type checking
- Structured control flow
- Readable syntax
- Business logic

**Use Cases:**
- Business applications
- Modular systems
- Maintainable codebases
- Team development
- Structured projects

**Companion docs:**
- [PLANC-MONITOR-CALLS.md](PLANC-MONITOR-CALLS.md) - doing SINTRAN MON calls from PLANC (the
  named `MONn` routines, why `MONITOR_CALL` fails on D100, error handling, library load order)
- [COSMOS-XMP-LIBRARY.md](COSMOS-XMP-LIBRARY.md) - XMSG (MON 200B) via the COSMOS XMP library
- **[PLANC-XMSG-PROGRAMMING-GUIDE.md](PLANC-XMSG-PROGRAMMING-GUIDE.md) - how to WRITE an XMSG
  client or server: hello world, every call, the patterns, the traps, the error numbers**
- [PLANC-XMSG-COMMUNICATION.md](PLANC-XMSG-COMMUNICATION.md) - what XMSG the machine has installed,
  and how to find it
- **[PLANC-TCP-UDP-SOCKETS.md](PLANC-TCP-UDP-SOCKETS.md) - TCP and UDP programs with ND's socket
  library SLIB: the program shape, a TCP server, a UDP server, building, testing, the traps**
- [SLIB-API-REFERENCE.md](SLIB-API-REFERENCE.md) - every SLIB call, record, constant and status code
- **[PLANC-RT-AND-REENTRANT-PROGRAMS.md](PLANC-RT-AND-REENTRANT-PROGRAMS.md) - INSTALLING a program
  into SINTRAN: as an RT program that holds no terminal and starts at boot, or as a reentrant
  subsystem every user shares one copy of. Where an RT program's name comes from, the RT-LOADER
  sequence, and `DUMP-PROGRAM-REENTRANT`**

**Reference Manuals:**
- `../../../Reference-Manuals/ND-60.117.5 EN PLANC Reference Manual.md`
- `../../../Reference-Manuals/ND-10309A PLANC FOR ND-100.md`

---

### [PASCAL-DEVELOPER-GUIDE.md](PASCAL-DEVELOPER-GUIDE.md)
**ND-PASCAL**

Educational and structured programming language.

**Key Features:**
- Strong typing
- Structured programming
- Clear syntax
- Educational design
- Algorithm focus

**Use Cases:**
- Educational programs
- Algorithm development
- Structured applications
- Academic computing
- Learning programming

**Reference Manual:** `../../../Reference-Manuals/ND-60.124.05 ND-PASCAL User's Guide.md`

---

### [FORTRAN-DEVELOPER-GUIDE.md](FORTRAN-DEVELOPER-GUIDE.md)
**NORD FORTRAN**

Scientific and numerical computing language.

**Key Features:**
- Array operations
- Mathematical functions
- Floating-point arithmetic
- Scientific notation
- Numerical libraries

**Use Cases:**
- Scientific computing
- Engineering calculations
- Numerical analysis
- Matrix operations
- Statistical analysis

**Reference Manuals:**
- `../../../Reference-Manuals/ND-60.145.7A EN ND FORTRAN Reference Manual.md`
- `../../../Reference-Manuals/ND-60.011.04 NORD Standard FORTRAN Reference Manual.md`
- `../../../Reference-Manuals/ND-10191A Fortran for ND-100-NORD-10.md`
- `../../../Reference-Manuals/ND-10190D FORTRAN FOR ND-500.md`
- `../../../Reference-Manuals/ND-10033K FORTRAN 32 BITS FLOATING FORMAT.md`

---

### [COBOL-DEVELOPER-GUIDE.md](COBOL-DEVELOPER-GUIDE.md)
**NORD COBOL**

Business-oriented programming language.

**Key Features:**
- English-like syntax
- Record processing
- File management
- Business calculations
- Report generation

**Use Cases:**
- Business data processing
- Financial systems
- Inventory management
- Report generation
- Legacy system maintenance

**Reference Manual:** `../../../Reference-Manuals/ND-60.144.3 EN COBOL Reference Manual.md`

---

### [BASIC-DEVELOPER-GUIDE.md](BASIC-DEVELOPER-GUIDE.md)
**NORD BASIC**

Interactive, easy-to-learn programming language.

**Key Features:**
- Interactive development
- Simple syntax
- Line-oriented editing
- Quick prototyping
- Immediate execution

**Use Cases:**
- Quick scripts
- Interactive programs
- Learning programming
- Simple calculations
- Prototyping

**Reference Manuals:**
- `../../../Reference-Manuals/ND-60.071.01D NORD-10 BASIC Compiler Reference Manual.md`
- `../../../Reference-Manuals/ND-60.040.02 NORD BASIC Reference Manual.md`

---

### [SIBAS-DEVELOPER-GUIDE.md](SIBAS-DEVELOPER-GUIDE.md)
**SIBAS (Norsk Data database system)**

CODASYL / DBTG-style (network model) database, accessed from a host language.

**Key Features:**
- Realm / schema data organisation
- DML (Data Manipulation Language)
- Host-language access (COBOL, FORTRAN)
- SIBAS I and SIBAS II generations
- Operator / administration tooling

**Use Cases:**
- Structured business data storage
- Multi-record network databases
- COBOL / FORTRAN applications needing a DBMS
- Legacy SIBAS database maintenance

**Reference Manuals:**
- `../../../Reference-Manuals/ND-60.127.5 EN THE DATABASE SYSTEM SIBAS II ND User Manual.md`
- `../../../Reference-Manuals/ND-30.009.3 EN SIBAS II Operator Manual.md`
- `../../../Reference-Manuals/210166F SIBAS II for ND-100.md`
- `../../../Reference-Manuals/ND-60.057.03 The Data Base System SIBAS I Users Manual Appendix A.md`

---

## 🎯 Choosing the Right Language

### For General-Purpose Programming
**C** - Best for modern, portable applications with system-level access

### For Business Applications
- **COBOL** - Traditional business data processing
- **PLANC** - Modern structured business logic

### For Scientific Computing
**FORTRAN** - Numerical analysis, engineering, mathematics

### For Educational Projects
- **PASCAL** - Learning structured programming
- **BASIC** - Learning programming basics

### For Maintainable Systems
**PLANC** or **PASCAL** - Strong typing and clear structure

---

## 📊 Language Comparison

| Feature | C | PLANC | PASCAL | FORTRAN | COBOL | BASIC |
|---------|---|-------|--------|---------|-------|-------|
| **Typing** | Weak | Strong | Strong | Weak | Weak | Weak |
| **Speed** | Fast | Fast | Medium | Fast | Medium | Slow |
| **Learning Curve** | Medium | Medium | Easy | Medium | Medium | Easy |
| **Portability** | High | Low | Medium | High | High | Low |
| **Modern Features** | Yes | Yes | Yes | No | No | No |
| **Best For** | Systems | Business | Education | Science | Business | Learning |

---

## 🔄 Development Workflow

### 1. Choose Your Language
Select based on project requirements and team expertise.

### 2. Set Up Development Environment
```
@QED myprogram.c        - For C
@QED myprogram.planc    - For PLANC
@QED myprogram.pas      - For PASCAL
@QED myprogram.for      - For FORTRAN
@QED myprogram.cob      - For COBOL
@BASIC                  - For BASIC (interactive)
```

### 3. Write Your Program
Use QED or PED editor ([../../Editors/](../../Editors/))

### 4. Compile
Follow language-specific compilation ([../../Workflow/COMPILER-COMMANDS-REFERENCE.md](../../Workflow/COMPILER-COMMANDS-REFERENCE.md))

### 5. Link and Run
Create executables ([../../Workflow/LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md))

### 6. Automate
Use MODE scripts ([../../Workflow/SCRIPT-GUIDE.md](../../Workflow/SCRIPT-GUIDE.md))

---

## 🚀 Quick Start Examples

### C Hello World
```c
#include <stdio.h>

int main() {
    printf("Hello, NORD!\n");
    return 0;
}
```

### PLANC Hello World
```planc
PROGRAM HelloWorld;
BEGIN
    WRITELN('Hello, NORD!');
END.
```

### PASCAL Hello World
```pascal
program HelloWorld;
begin
    writeln('Hello, NORD!');
end.
```

### FORTRAN Hello World
```fortran
      PROGRAM HELLO
      WRITE(*,*) 'Hello, NORD!'
      STOP
      END
```

### COBOL Hello World
```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. HELLOWORLD.
PROCEDURE DIVISION.
    DISPLAY 'Hello, NORD!'.
    STOP RUN.
```

### BASIC Hello World
```basic
10 PRINT "Hello, NORD!"
20 END
```

---

## 📚 Learning Resources

Each developer guide includes:
- **Quick Start** - First program and basic concepts
- **Language Syntax** - Complete syntax reference
- **Standard Library** - Available functions and procedures
- **File I/O** - Reading and writing files
- **Compilation** - How to build programs
- **Examples** - Practical code samples
- **Best Practices** - Writing maintainable code

---

## 🔗 Related Documentation

### Development Workflow
- **Editors**: [../../Editors/](../../Editors/)
- **Compilation**: [../../Workflow/COMPILER-COMMANDS-REFERENCE.md](../../Workflow/COMPILER-COMMANDS-REFERENCE.md)
- **Linking**: [../../Workflow/LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md)
- **Scripts**: [../../Workflow/SCRIPT-GUIDE.md](../../Workflow/SCRIPT-GUIDE.md)
- **Tools**: [../../Workflow/TOOLS-REFERENCE.md](../../Workflow/TOOLS-REFERENCE.md)

### Reference Manuals
- **All Manuals**: [../../../Reference-Manuals/](../../../Reference-Manuals/)

### System Documentation
- **SINTRAN Commands**: [../../../Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md](../../../Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md)

---

## 💡 Tips for Success

1. **Start Simple** - Begin with Hello World, then gradually add complexity
2. **Use Examples** - Study example code in each guide
3. **Follow Conventions** - Each language has its own style guidelines
4. **Test Frequently** - Compile and test often during development
5. **Read Errors** - Compiler messages are your friend
6. **Document Code** - Add comments explaining your logic
7. **Use Version Control** - Keep backups of working versions

---

**Last Updated**: 2026-07-04  
**Languages**: 6 (C, PLANC, PASCAL, FORTRAN, COBOL, BASIC) + SIBAS database system  
**Documentation Status**: ✅ Complete guides available (SIBAS = reference index)

