# NDInsight - Norsk Data Computer Systems Analysis & Documentation

**Comprehensive technical analysis and documentation for Norsk Data computer systems**

---

## 📖 Overview

**NDInsight** is a centralized repository of deep technical analysis, reverse-engineered documentation, OCR'd manuals, and implementation guides for **Norsk Data computer systems** - NORD-1/10/50, ND-100/110/120, ND-500 and ND-5000 - focusing on the **SINTRAN III operating system** and its hardware architecture.

The analysis is made from original SINTRAN III source code, official Norsk Data technical manuals, and with heavy use of AI (Claude AI, Cursor AI, ChatGPT AI). While comprehensive, there might be errors and hallucinations - use with appropriate verification.

### What's Inside

- **SINTRAN III NPL source code** - 45 files of authentic operating system source code, plus symbol tables
- **Kernel-level documentation** extracted from SINTRAN III source code
- **Hardware analysis** of communication protocols (HDLC, X.21, X.25, TAD, XMSG, Octobus)
- **ND-500 / ND-5000 coprocessor** integration and communication, reverse-engineered end to end
- **Device driver** implementation details (SCSI, DOMINO/NUCLEUS, printers) with complete source code
- **Emulator implementation** guides and production C# code
- **Hundreds of official Norsk Data reference manuals and product data sheets**, OCR'd and indexed
- **A hands-on reverse-engineering toolkit** (segment carver + boot-floppy analysis) with real source, disassembly and carved evidence

---

## 🗂️ Repository Structure

```
NDInsight/
├── README.md                    ← You are here
├── CLAUDE.md                    ← AI assistant guidance
├── MERMAID_COLOR_STANDARDS.md   ← Diagram color standards
├── Developer/                   ← Developer guides and language references
│   ├── Case-Studies/            ← Worked examples (an HTTP server over HDLC, written in MAC)
│   └── Reverse-Engineering/     ← Disassembling a :PROG, ND-100 instruction decoding
├── Hardware/                    ← Cabinet sizes and weights from the manuals, FreeCAD 3D models
├── History/                     ← History of the machines, one chapter per generation
├── Installation/                ← Installing SINTRAN III and application software
│   ├── OS/                      ← Installing SINTRAN III from distribution floppies
│   ├── Communication/           ← Installing COSMOS/Ethernet/TCP-IP/X.21/X.25 products
│   ├── Software/                ← Installing application software (later phase)
│   ├── OWS/                     ← Office Work Station: WinLink/WinPrint/WinSMX, PC-NOTIS, SPRINT printing, SIBAS/R
│   ├── Machines/                ← ND-500 / ND-5000 cabinets, cages and board sets, with cutaway diagrams
│   ├── Installation-Description/← OCR'd "Program Description" install/requirements sheets
│   ├── Product-Info/            ← OCR'd product data-sheets/brochures
│   └── Sales-Info/              ← OCR'd internal "Sales Information Document" sheets
├── Operations/                  ← Operator and user guides (COSMOS, SINTRAN)
├── Reference-Manuals/           ← Official Norsk Data reference manuals (incl. NORD-1, NORD-10, ND-500/5000, NOTIS)
├── scripts/                     ← Documentation processing scripts (Python, PowerShell)
├── tools/                       ← Reverse-engineering toolkit
│   ├── sintran-segment-carver/  ← Carved SINTRAN image segments, symbol matching, RE notes
│   └── boot-floppy/             ← Disc boot-sector anatomy, MACM generation, patch analysis
└── SINTRAN/                     ← SINTRAN III Operating System
    ├── Devices/                 ← Hardware device documentation (HDLC, SCSI, DOMINO/NUCLEUS)
    ├── Emulator/                ← C# emulator implementation guides
    ├── File-Formats/            ← Object and executable file formats (BRF, :PROG, :NRF, :DOM/:SEG, :LINK, DESC) + browser viewer
    ├── Filesystem/              ← SINTRAN filesystem structures
    ├── ND500/                   ← ND-500 coprocessor documentation
    ├── ND500-APPS/              ← Real ND-500 vendor programs, runnable in nd500x, with a user guide each
    ├── ND5000/                  ← ND-5000 / Octobus documentation
    ├── NPL-SOURCE/              ← ⭐ SINTRAN III source code & symbols
    ├── OS/                      ← Core OS kernel documentation
    ├── Print/                   ← Printing/spooling subsystem
    ├── Release-Documentation/   ← SINTRAN III release notes (versions J-N)
    ├── SINTRAN Structures/      ← System structures and data analysis
    ├── TAD/                     ← TAD protocol analysis
    ├── TSS/                     ← TSS subsystem documentation
    └── XMSG/                    ← XMSG message system: DOC/ (protocol, API, commands), SRC/ (C# library), constants
```

---

## 🚀 Quick Start

### New to SINTRAN III?

**Start with these documents:**
1. [SINTRAN/OS/00-SINTRAN-ARCHITECTURE-OVERVIEW.md](SINTRAN/OS/00-SINTRAN-ARCHITECTURE-OVERVIEW.md) - System overview
2. [SINTRAN/OS/01-BOOT-SEQUENCE.md](SINTRAN/OS/01-BOOT-SEQUENCE.md) - How the system boots
3. [SINTRAN/README.md](SINTRAN/README.md) - Complete SINTRAN documentation guide

### Installing a System?

**Start here:**
1. [Installation/README.md](Installation/README.md) - Installation guides index
2. [Installation/OS/](Installation/OS/) - Installing SINTRAN III from distribution floppies
3. [Installation/Installation-Description/README.md](Installation/Installation-Description/README.md) - Per-product install/requirements sheets

### Building an Emulator?

**Critical resources:**
1. [SINTRAN/NPL-SOURCE/README.md](SINTRAN/NPL-SOURCE/README.md) - Access to actual source code
2. [SINTRAN/Emulator/README.md](SINTRAN/Emulator/README.md) - C# implementation guides
3. [SINTRAN/OS/19-MEMORY-MAP-REFERENCE.md](SINTRAN/OS/19-MEMORY-MAP-REFERENCE.md) - Memory layout

### Developing Software?

**Language guides:**
1. [Developer/README.md](Developer/README.md) - Developer documentation index
2. [Reference-Manuals/README.md](Reference-Manuals/README.md) - Complete language references

### Reverse-Engineering a SINTRAN Image?

**Toolkit and method:**
1. [tools/sintran-segment-carver/](tools/sintran-segment-carver/) - Carved segments, symbol matching, byte-verified findings
2. [tools/boot-floppy/](tools/boot-floppy/) - Disc boot-sector anatomy, MACM generation dialogue, patch format

---

## 📂 Main Sections

Each top-level folder has its own README with full navigation; this page only summarizes.

| Section | Contents | Index |
|---|---|---|
| **[Developer/](Developer/)** | Language guides (NPL, MAC, PLANC, PASCAL, FORTRAN, COBOL, BASIC, C), editors (QED, PED, LED), build workflow incl. cross-development with nd100x, [case studies](Developer/Case-Studies/README.md) and [reverse-engineering guides](Developer/Reverse-Engineering/README.md) | [README.md](Developer/README.md) |
| **[Hardware/](Hardware/)** | Physical reference for the machines - cabinet dimensions, weights and power quoted from the manuals - and FreeCAD 3D models of the ND-100 Compact, ND-100 Satellite, ND-5900 and the ND 246 terminal | [README.md](Hardware/README.md) |
| **[History/](History/)** | History of the machines: what each one was, how it worked, what changed between generations, with a timeline, verbatim sources and credited images | [README.md](History/README.md) |
| **[Installation/](Installation/)** | How to install SINTRAN III and applications; OCR'd install-description, product-info and sales-info sheets; the [OWS/](Installation/OWS/README.md) office-workstation family; [Machines/](Installation/Machines/README.md) - what is inside the ND-500 and ND-5000 cabinets | [README.md](Installation/README.md) |
| **[Operations/](Operations/)** | Operator/admin guides for COSMOS networking and SINTRAN system operation | [README.md](Operations/README.md) |
| **[Reference-Manuals/](Reference-Manuals/)** | Official Norsk Data reference manuals across the whole product line - CPU architecture, assemblers, languages, editors, NOTIS office suite, NORD-1/NORD-10 | [README.md](Reference-Manuals/README.md) |
| **[SINTRAN/](SINTRAN/)** | The core: kernel docs, source code, device drivers, ND-500/ND-5000 integration, protocols, emulator | [README.md](SINTRAN/README.md) |
| **[tools/](tools/)** | Reverse-engineering toolkit: SINTRAN segment carver and boot-floppy/disc-generation analysis, with real source and carved evidence | [tools/README.md](tools/README.md) |

### [SINTRAN/](SINTRAN/) - Operating System Documentation

The largest and oldest part of the repository.

| Directory | Description |
|-----------|-------------|
| **[NPL-SOURCE/](SINTRAN/NPL-SOURCE/)** ⭐ | **SINTRAN III source code** - 45 NPL files + symbol tables from the s3vs-4 build |
| **[OS/](SINTRAN/OS/)** | Core kernel documentation, chapters 00-19 |
| **[Release-Documentation/](SINTRAN/Release-Documentation/)** | SINTRAN III release notes, versions J-N |
| **[SINTRAN Structures/](SINTRAN/SINTRAN%20Structures/)** | Kernel data structures analysis |
| **[Devices/](SINTRAN/Devices/)** | HDLC, SCSI and DOMINO/NUCLEUS device drivers |
| **[Emulator/](SINTRAN/Emulator/)** | C# emulator implementation guides and production code |
| **[ND500/](SINTRAN/ND500/)** | ND-500 coprocessor. ND-100 <-> ND-500 interface reverse-engineered end to end (byte-verified from L07); status of record: `SINTRAN/ND500/ND500-STATUS-AND-INDEX.md` |
| **[ND5000/](SINTRAN/ND5000/)** | ND-5000 / Octobus fabric analysis |
| **[TAD/](SINTRAN/TAD/)** | Terminal Access Device protocol |
| **[XMSG/](SINTRAN/XMSG/)** | Inter-node messaging: wire protocol, monitor-call API, C# library |
| **[Print/](SINTRAN/Print/)** | Printing/spooling subsystem |
| **[Filesystem/](SINTRAN/Filesystem/)**, **[File-Formats/](SINTRAN/File-Formats/)** | On-disk structures, and the object and executable file formats with a browser viewer |
| **[ND500-APPS/](SINTRAN/ND500-APPS/)** | Real ND-500 vendor programs with every file needed to run them in nd500x, and a user guide per program |
| **[TSS/](SINTRAN/TSS/)** | TSS subsystem |

📖 **[See SINTRAN/README.md for the complete overview](SINTRAN/README.md)**

---

## 📊 Repository Statistics

*Counts are approximate and drift as the repository grows - see each section's own README for exact current numbers.*

| Section | Markdown Files | Size | Highlights |
|---|---|---|---|
| **SINTRAN/** | ~860 | ~92MB | NPL source (45 files), kernel docs (ch. 00-19), ND-500/5000, XMSG, TSS |
| **tools/** | ~410 | ~200MB | Segment carver + boot-floppy RE toolkit; also 250+ carved binaries, 200+ C/ASM/NPL source files |
| **Installation/** | ~900 | ~21MB | 284 OCR'd install-description sheets + 364 OCR'd product-info sheets + sales-info sheets + install guides + machine cabinets |
| **Reference-Manuals/** | ~180 | ~29MB | Official manuals: NORD-1, NORD-10, ND-500/5000, NOTIS suite, languages, editors |
| **History/** | ~80 | - | Machine history, one chapter per generation, with sources |
| **Developer/** | ~60 | ~4MB | Language guides, editors, build workflow, case studies, reverse-engineering guides |
| **Operations/** | ~20 | ~3MB | COSMOS and SINTRAN operator guides |
| **Hardware/** | 5 | - | Physical reference + 3D models |
| **Total** | **~2,500** | **~350MB** | - |

*Markdown file counts were taken again on 2026-09-18 from the tracked files. The Size column was NOT measured again and still holds the 2026-07-20 figures.*

### Source Code Coverage

**What We Have (NPL Source):**
- ✅ Kernel/Monitor core (MON60)
- ✅ SCSI, DOMINO/NUCLEUS and HDLC device drivers
- ✅ ND-500 interface code
- ✅ Disk I/O subsystem
- ✅ Segment administration
- ✅ HASP protocol
- ✅ Terminal handlers (partial)

**What's Missing:**
- ❌ Complete file system implementation (symbols available)
- ❌ Complete XMSG message system source (symbols + wire protocol available)
- ❌ Complete terminal handlers
- ❌ Network subsystems beyond HDLC/XMSG/Octobus
- ❌ Batch processing components

---

## 🛠️ Technologies Documented

### Hardware
- **NORD-1, NORD-10/10-S, NORD-50** - Early Norsk Data minicomputers
- **ND-100/110/120** - 16-bit minicomputer family (1970s-1990s)
- **ND-500 / ND-5000** - 32-bit coprocessor / server family
- **MPM5** - Multiport memory (shared RAM)
- **Octobus** - ND-100 <-> ND-5000 fabric
- **COM5025** - HDLC controller chip
- **NCR 5386** - SCSI protocol controller

### Software
- **SINTRAN III** - Real-time operating system
- **NPL** - NORD Programming Language (system programming)
- **MAC** - Macro assembler
- **PLANC, PASCAL, FORTRAN, COBOL, BASIC, C, SIMULA, Ada** - Application languages
- **NOTIS** - Norsk Data's office automation suite (WP, DS, IR, ID, RG, CALC, BG, DRAW, PM)

### Protocols
- **HDLC / X.21 / X.25 / LAPB** - Link and packet layers
- **XMSG** - Inter-node messaging (SINTRAN's native IPC/networking layer)
- **COSMOS** - Norsk Data's network operating environment
- **TAD** - Terminal Access Device protocol

---

## 🎓 Documentation Methodology

### Sources
1. **SINTRAN III Source Code** - Direct NPL source analysis (s3vs-4 build)
2. **Official Norsk Data Manuals** - OCR'd from scanned originals (see Acknowledgments)
3. **Protocol Specifications** - HDLC, X.21, X.25, TAD standards
4. **Reverse Engineering** - Bit-level / byte-verified analysis when source isn't available

### Quality Standards
- ✅ **No guesswork** - Only verified facts from source/manuals; unverified claims are marked `ASSUMPTION:` or `UNVERIFIED:`
- ✅ **Source citations** - Every claim traced to source
- ✅ **Cross-references** - Extensive linking between documents
- ✅ **Visual aids** - Mermaid diagrams for complex flows
- ✅ **Production code** - Working C# implementations included
- ✅ **WCAG 2.1 AA** - Accessible diagram color standards

---

## 🚀 Use Cases

### For Emulator Developers
→ Start at [SINTRAN/Emulator/README.md](SINTRAN/Emulator/README.md)
- Understand SINTRAN kernel internals
- Implement accurate hardware emulation
- Access production C# code
- Verify against actual NPL source

### For System Archaeologists / Reverse Engineers
→ Start at [tools/sintran-segment-carver/](tools/sintran-segment-carver/) and [SINTRAN/OS/README.md](SINTRAN/OS/README.md)
- Study 1970s-1980s OS design
- Carve and cross-reference SINTRAN image segments
- Analyze interrupt-driven architecture, paging and multi-CPU coordination

### For Software Developers
→ Start at [Developer/README.md](Developer/README.md)
- Learn SINTRAN development
- Choose your language (8+ languages supported)
- Access complete reference manuals

### For System Installers / Operators
→ Start at [Installation/README.md](Installation/README.md)
- Install SINTRAN III from distribution media
- Look up a product's requirements/prerequisites
- Follow operator guides for COSMOS and SINTRAN administration

### For Hardware Analysts
→ Start at [SINTRAN/Devices/README.md](SINTRAN/Devices/README.md)
- Understand device driver architecture
- Analyze communication protocols
- Study HDLC, SCSI and DOMINO/NUCLEUS implementations

---

## 🤝 Contributing

This repository is a work in progress. Areas for contribution:
- Additional SINTRAN subsystem analysis
- Emulator bug fixes and improvements
- Protocol trace analysis
- Hardware documentation
- Historical information and context

---

## 📜 License

**Documentation**: Creative Commons Attribution 4.0 International (CC BY 4.0)
**Code**: MIT License

---

## 🙏 Acknowledgments

- **Norsk Data AS** - Original SINTRAN III development (1970s-1980s)
- **SINTRAN Source Code** - Foundation for this analysis
- **Hardware Manuals** - Official Norsk Data documentation
- **Emulator Community** - Keeping vintage computing alive
- **Jonny Oddene** ([sintran.com](https://sintran.com/) / [norsk-data.com](http://norsk-data.com/)) - A huge thank-you for the enormous personal effort scanning and preserving thousands of Norsk Data documents. A number of the manuals in this repository were OCR'd from material sourced through his sites. Without his work to rescue and archive this documentation, a large part of it would have been lost.
- **[ndwiki.org](https://www.ndwiki.org/)** - The only wiki dedicated to Norsk Data history and technology

---

**Last Updated**: 2026-09-18

---

*Preserving the legacy of Norsk Data computing through comprehensive technical analysis and documentation.*
