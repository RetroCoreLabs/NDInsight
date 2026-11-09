# Programming Languages Documentation

This folder contains developer guides for all NORD/SINTRAN programming languages, organized by purpose.

---

## 📂 Organization

### [System/](System/) - System Programming Languages
Low-level languages for operating system development, device drivers, and system utilities.

| Language | Purpose | Guide |
|----------|---------|-------|
| **NPL** | NORD Programming Language - OS development | [NPL-DEVELOPER-GUIDE.md](System/NPL-DEVELOPER-GUIDE.md) |
| **MAC** | Macro Assembler - Low-level programming | [MAC-DEVELOPER-GUIDE.md](System/MAC-DEVELOPER-GUIDE.md), then [MAC-COOKBOOK.md](System/MAC-COOKBOOK.md) (what actually assembles and runs through @MAC) |
| **NORD-500 Assembler** | ND-500 assembly language | [NORD-500-ASSEMBLER-DEVELOPER-GUIDE.md](System/NORD-500-ASSEMBLER-DEVELOPER-GUIDE.md), [NORD-500-ASSEMBLER-EXPERT-GUIDE.md](System/NORD-500-ASSEMBLER-EXPERT-GUIDE.md) |

### [Application/](Application/) - Application Programming Languages
High-level languages for business, scientific, and general-purpose application development.

| Language | Purpose | Guide |
|----------|---------|-------|
| **C** | General-purpose programming | [C-DEVELOPER-GUIDE.md](Application/C-DEVELOPER-GUIDE.md) |
| **PLANC** | Structured programming (PLAN-oriented) | [HOW-TO-PROGRAM-PLANC.md](Application/HOW-TO-PROGRAM-PLANC.md) (start here), [PLANC-DEVELOPER-GUIDE.md](Application/PLANC-DEVELOPER-GUIDE.md); all other PLANC, XMSG, SLIB and VTM pages are listed in [Application/README.md](Application/README.md) |
| **PASCAL** | Structured programming, education | [PASCAL-DEVELOPER-GUIDE.md](Application/PASCAL-DEVELOPER-GUIDE.md) |
| **FORTRAN** | Scientific and numerical computing | [FORTRAN-DEVELOPER-GUIDE.md](Application/FORTRAN-DEVELOPER-GUIDE.md), [FORTRAN-BUILD-LEARNINGS-FAQ.md](Application/FORTRAN-BUILD-LEARNINGS-FAQ.md), [ADVENTURE-BUILD-AND-INITIALIZE.md](Application/ADVENTURE-BUILD-AND-INITIALIZE.md) |
| **COBOL** | Business applications | [COBOL-DEVELOPER-GUIDE.md](Application/COBOL-DEVELOPER-GUIDE.md) |
| **BASIC** | Interactive programming, learning | [BASIC-DEVELOPER-GUIDE.md](Application/BASIC-DEVELOPER-GUIDE.md) |
| **SIMULA** | Classes, coroutines, discrete-event simulation | [SIMULA/README.md](Application/SIMULA/README.md) |
| **SIBAS** (database, not a language) | The ND database system, called from COBOL, FORTRAN and others | [SIBAS-DEVELOPER-GUIDE.md](Application/SIBAS-DEVELOPER-GUIDE.md), and [../Workflow/SIBAS-DATABASE-PROGRAMMING.md](../Workflow/SIBAS-DATABASE-PROGRAMMING.md) |

Indexes: [System/README.md](System/README.md), [Application/README.md](Application/README.md).

---

## 🎯 Choosing a Language

### System Programming
**Choose NPL or MAC when:**
- Writing device drivers
- Developing OS components
- Need direct hardware access
- Require maximum performance
- Working with SINTRAN internals

**Choose NORD-500 Assembler when:**
- Programming the ND-500 coprocessor
- Need 32-bit operations
- Implementing specialized algorithms
- Working with ND-500 domains

### Application Development

**Choose C when:**
- Need portability
- Writing system utilities
- Require pointer manipulation
- Want modern programming constructs

**Choose PLANC when:**
- Structured business logic
- Need strong typing
- Want readable, maintainable code
- Working with modules

**Choose PASCAL when:**
- Educational projects
- Structured algorithms
- Type-safe development
- Academic computing

**Choose FORTRAN when:**
- Scientific computing
- Numerical analysis
- Matrix operations
- Engineering applications

**Choose COBOL when:**
- Business data processing
- File management systems
- Record-oriented applications
- Legacy system maintenance

**Choose BASIC when:**
- Quick prototyping
- Interactive applications
- Learning programming
- Simple calculations

---

## 📚 Reference Manuals

All developer guides are based on complete reference manuals located in `../../Reference-Manuals/`:

### System Languages
- **NPL**: [ND-60.047.03 NORD PL User's Guide](../../Reference-Manuals/ND-60.047.03%20NORD%20PL%20User's%20Guide.md)
- **MAC**: [ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide](../../Reference-Manuals/ND-60.096.01%20MAC%20Interactive%20Assembly%20and%20Debugging%20System%20User's%20Guide.md)
- **NORD-500 Asm**: [ND-60.113.02 EN Assembler Reference Manual](../../Reference-Manuals/ND-60.113.02%20EN%20Assembler%20Reference%20Manual.md)

### Application Languages
- **C**: [ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual](../../Reference-Manuals/ND-60.214.01%20CC-100%20and%20CC-500%20C-Compiler%20User%20Manual.md)
- **PLANC**: [ND-60.117.5 EN PLANC Reference Manual](../../Reference-Manuals/ND-60.117.5%20EN%20PLANC%20Reference%20Manual.md)
- **PASCAL**: [ND-60.124.05 ND-PASCAL User's Guide](../../Reference-Manuals/ND-60.124.05%20ND-PASCAL%20User's%20Guide.md)
- **FORTRAN**: [ND-60.145.7A EN ND FORTRAN Reference Manual](../../Reference-Manuals/ND-60.145.7A%20EN%20ND%20FORTRAN%20Reference%20Manual.md)
- **COBOL**: [ND-60.144.3 EN COBOL Reference Manual](../../Reference-Manuals/ND-60.144.3%20EN%20COBOL%20Reference%20Manual.md)
- **BASIC**: [ND-60.071.01D NORD-10 BASIC Compiler Reference Manual](../../Reference-Manuals/ND-60.071.01D%20NORD-10%20BASIC%20Compiler%20Reference%20Manual.md)
- **SIMULA**: [ND-60.092.03 NORD-100 SINTRAN III SIMULA - Reference Manual](../../Reference-Manuals/ND-60.092.03%20NORD-100%20SINTRAN%20III%20SIMULA%20-%20Reference%20Manual.md), [ND-60208-1-EN ND-500 SIMULA reference manual](../../Reference-Manuals/ND-60208-1-EN%20ND-500%20SIMULA%20reference%20manual.md) (ND-500)

---

## 🔄 Development Workflow

After choosing your language, follow the complete development workflow:

1. **Write** - Use QED or PED editor ([../Editors/](../Editors/))
2. **Compile** - Follow language-specific compilation ([../Workflow/COMPILER-COMMANDS-REFERENCE.md](../Workflow/COMPILER-COMMANDS-REFERENCE.md))
3. **Link** - Create executable programs ([../Workflow/LINKING-GUIDE.md](../Workflow/LINKING-GUIDE.md))
4. **Run** - Execute and debug your program
5. **Automate** - Use MODE scripts ([../Workflow/SCRIPT-GUIDE.md](../Workflow/SCRIPT-GUIDE.md))

---

## 📖 Documentation Structure

Each language guide follows a consistent structure:

- **Overview** - Language purpose and characteristics
- **Quick Start** - First program and basic concepts
- **Core Concepts** - Language-specific features
- **Compilation** - How to compile and run
- **Advanced Topics** - Expert-level features
- **Examples** - Practical code samples
- **Reference** - Links to complete manuals

---

## 🔗 Related Documentation

- **Main Developer Guide**: [../README.md](../README.md)
- **Editor Documentation**: [../Editors/](../Editors/)
- **Workflow Guides**: [../Workflow/](../Workflow/)
- **Reference Manuals**: [../../Reference-Manuals/](../../Reference-Manuals/)
- **SINTRAN OS**: [../../SINTRAN/OS/](../../SINTRAN/OS/)

---

**Last Updated**: October 18, 2025  
**Total Languages**: 9 (3 system + 6 application)  
**Documentation Status**: ✅ Complete structure, guides in progress

