# Reference Manuals - Complete NORD/SINTRAN Documentation

**Authoritative reference manuals for all NORD/SINTRAN system components, programming languages, and development tools**

---

## 📖 Overview

This folder contains **96 complete reference manuals** (in the root) spanning system architecture,
ND-100/ND-110 hardware, the SINTRAN III operating system, database systems, programming languages,
assemblers, editors, compilers, linkers, debuggers, diagnostics/test programs, and development
tools. Five further sub-collections (NORD-1, NORD-10, ND-500/ND-5000, Device Controllers, and the
NOTIS office suite) are indexed separately below. Together these manuals serve as the primary source
documentation for all NORD/SINTRAN development work.

### Purpose

- **Comprehensive Reference** - Complete technical documentation for all system components
- **Developer Resource** - Source material for creating developer guides and tutorials
- **Historical Archive** - Preservation of original NORD/SINTRAN documentation (1970s-1990s)
- **Cross-Reference** - Detailed specifications for advanced users and system programmers

---

## 📁 Sub-Collections

In addition to the 91 manuals in this folder, related material is grouped into five sub-folders,
each with its own index:

| Sub-Collection | Index | Manuals | Scope |
|----------------|-------|---------|-------|
| **NORD-1 Manuals** | [1/README.md](1/README.md) | 5 | NORD-1 reference manual, two-volume hardware manual, connectors/I-O/power system, peripheral binder |
| **NORD-10 Manuals** | [10/README.md](10/README.md) | 13 | NORD-10 / NORD-10-S CPU reference & microprogram, NORD-50 communication, operator's guides, verification programs, disc system, drawings/wiring |
| **ND-500 / ND-5000 Manuals** | [500/README.md](500/README.md) | 23 | ND-500/ND-5000 CPU & microprogram (incl. ND-5000 microprogram guide and microcode field/mnemonic references), ND-5000 hardware, DOMINO/NUCLEUS, multiport memory, array processing, course material |
| **Device Controllers** | [Devices/README.md](Devices/README.md) | 7 | Ethernet II Controller manual and its unit-test specification; ECC, 15 MHz SMD, Winchester (ST506/8"), Floppy and NORD-10/HAWK disk-controller manuals |
| **NOTIS Office System** | [Notis/README.md](Notis/README.md) | 31 | NOTIS office-automation suite (WP, TF, DS, IR, ID, RG, CALC, BG, DRAW, PM), reference cards, diskette listings, notes |

---

## 🗂️ Total Collection (Root)

| Category | Manuals |
|----------|---------|
| **System & CPU Architecture** | 5 |
| **Hardware Documentation** | 1 |
| **ND-100 / ND-110 Hardware & Architecture** | 6 |
| **SINTRAN III System & OS** | 29 |
| **Database Systems (SIBAS)** | 6 |
| **Assemblers** | 7 |
| **Intel-8080 Cross-Tools** | 2 |
| **System Programming Language (NPL)** | 1 |
| **Application Languages** | 24 |
| **Compilers & Linkers** | 2 |
| **Debuggers** | 2 |
| **Editors** | 5 |
| **Office Software (NOTIS-1)** | 1 |
| **Diagnostics & Test Programs** | 4 |
| **Documentation & Catalogues** | 1 |
| **Total** | **96** |

---

## 🗂️ Complete Manual Index

### System & CPU Architecture

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **SINTRAN III Monitor Calls** | ND-860228-2 EN | 31,268 | Complete system-call reference - monitor routines, kernel interface, I/O operations |
| **SINTRAN III Monitor Calls (Web)** | ND-860228-2 EN | 30,666 | Web-optimized edition of ND-860228-2 (same document as above) |
| **ND-500 Reference Manual** | ND-05.009.4 EN | 16,323 | Complete ND-500 CPU architecture, instruction set, domains, memory management |
| **SINTRAN Commands Reference** | - | 11,656 | All SINTRAN III commands - batch processing, file management, MODE files |
| **ND-500 Loader Monitor** | ND-60.136.04A | 11,394 | ND-500 program loading and monitor interface |

**Key Topics:** CPU architecture, instruction sets, system calls, command reference, monitor interface

**Note:** ND-860228-2 exists in two forms - the standard OCR edition and a web-optimized edition (`-WEB`); both are the same document.

---

### Hardware Documentation

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **MPM 5 Technical Description** | ND-10.004.01 | 2,991 | Multiport Memory (5MPM) hardware specifications - critical for ND-500 integration |

**Key Topics:** 5MPM architecture, memory mapping, ND-100/ND-500 shared memory, hardware interface

**Related:** See [SINTRAN/OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md](../SINTRAN/OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md) and the [ND-500/ND-5000 sub-collection](500/README.md).

---

### ND-100 / ND-110 Hardware & Architecture

The ND-100 and ND-110 processor hardware manual set - CPU architecture, functional
descriptions, the I/O system, the big multiport memory, and the ND-110 instruction set.
Primary source material for emulator development and low-level hardware work.

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **ND-100 Functional Description** | ND-06.015.02 | 13,839 | Complete ND-100 hardware functional description - CPU, buses, memory, control logic |
| **ND-110 Functional Description** | ND-06.026-1 EN | 9,805 | Complete ND-110 hardware functional description - CPU, buses, memory, control logic |
| **ND-100 Reference Manual** | ND-06.014.2A EN | 9,590 | ND-100 hardware reference - registers, timing, hardware interface |
| **NORD-100 Input/Output System** | ND-06.016.01 | 8,708 | NORD-100 I/O system - device interfaces, IOX, DMA, interrupt system |
| **ND-110 Instruction Set** | ND-06.029.1 EN | 8,436 | Complete ND-110 instruction set - opcodes, addressing, encoding |
| **BIG MULTIPORT MEMORY SYSTEM** | ND-06.007.01 | 4,519 | Big multiport memory hardware - shared memory, port arbitration |

**Key Topics:** ND-100/ND-110 CPU architecture, hardware functional description, instruction set encoding, I/O system, interrupts, DMA, multiport memory

**Related:**
- [SINTRAN/OS/README.md](../SINTRAN/OS/README.md) - Operating system internals
- [SINTRAN/Emulator/](../SINTRAN/Emulator/) - C# emulator implementation

---

### SINTRAN III System & OS Manuals

The core SINTRAN III operating-system manual set. (The **SINTRAN III Monitor Calls** and
**SINTRAN Commands Reference** are listed above under System & CPU Architecture.)

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **SINTRAN III Håndbok for driftsansvarlig** | - | 22,933 | (NO) Norwegian handbook for the system-responsible / operations administrator |
| **SINTRAN III Reference Manual** | ND-60.128.5 EN | 21,694 | Master SINTRAN III reference - commands, subsystems, system behaviour |
| **SINTRAN III Real Time Guide** | ND-60.133.02A | 14,445 | Real-time programming under SINTRAN III |
| **COSMOS Programmer Guide** | ND-60.164.3 EN | 16,900 | Version 3 (05/86), product ND-10609B, based on XMSG version J. The COSMOS programmer library: XMSG task-to-task messaging from PLANC (XMP) and FORTRAN (XMF), RR-LIB remote-routine server/client from PLANC (RRP), and TLIB transport from PLANC (TLP) and FORTRAN (TLF). Per-routine reference sections plus an appendix of the raw XMSG functions - the authoritative source for the XMSG call interface, ports, message buffers and XROUT services. **Its appendix is not complete for later XMSG versions** - see [X-MESSAGE version L, 210373L](../Installation/Installation-Description/ND-210373L-EN.md), which specifies functions and XROUT services this guide predates (`XFGSM` among them) |
| **SINTRAN III-VSX System Documentation** | ND-820023-1 EN | 12,107 | SINTRAN III-VSX system documentation |
| **Performance Monitoring, Tuning and Capacity Planning** | ND-830083-1 EN | 3,042 | Why performance matters, response time vs system capacity, resources/queues/bottlenecks, measurement primitives and log macros, sampling vs event counting, how load depends on program type, and a procedure for resolving performance problems. Part 2 is a guide to the Performance Monitor itself - starting it, its parts, the online HELP and the DIAGNOSE command |
| **SINTRAN III Users Guide** | ND-60.050.06 | 11,589 | General user guide to SINTRAN III |
| **SINTRAN SLIB Programmers Guide** | ND-860372.1 EN | 8,572 | ND Socket Library (SLIB): BSD-socket-style network programming interface for SINTRAN III over ARPANET/TCP-IP - sockets, communication domains, connection setup/accept, datagram sockets, sending/receiving data, shutdown, and multitasking in SLIB |
| **SINTRAN III Timesharing / Batch Guide** | ND-60.132.03 | 6,616 | Timesharing and batch processing guide |
| **SINTRAN III Communication Guide** | ND-60.134.2 EN | 5,740 | Communications / networking under SINTRAN III (dated Nov 1981 - predates ND Ethernet; contains nothing on Ethernet, TCP/IP or ENNS0) |
| **BACKUP User Guide** | ND-60.250.1 EN | 5,489 | The Backup System: file/backup copying between users, disk, diskette and magnetic tape (interactive, mode file, or batch), `COPY-USERS-FILES`/`MULTIUSER-COPY`/`DEVICE-COPY`, volume create/list/delete. Companion to [Installation/Software/ND-210337](../Installation/Software/ND-210337/README.md) (Backup-System product/install docs) |
| **Ethernet Basic Software Programmer Guide** | ND-60.197.01 | 2,404 | *Raw OCR import - read the source PDF for tables and numeric values.* Host-to-controller programming contract: Media Access Process and its three Service Points (Command / Receive / Transmit), the datagram call interface, DIX vs IEEE framing, and the four-physical-address multi-protocol scheme. Describes the two-board Ethernet I Interface, not the one-board ND 110063 |
| **SINTRAN III System Documentation, Appendix A - Data Fields** | ND-60.112.01 | 4,455 | System data-field definitions (system documentation appendix) |
| **SINTRAN III - Real Time Loader** | ND-60.051.8 EN | 3,430 | Real Time Loader (RT loader) manual |
| **SINTRAN III Introduction** | ND-60.125.04 | 3,245 | Introduction / getting started with SINTRAN III |
| **US05 SINTRAN III Workshop** | ND-US05-1 EN | 3,178 | SINTRAN III workshop / course material |
| **SINTRAN II Operator's Guide** | ND-60.044.01 | 2,919 | Operator's guide for the earlier SINTRAN II system |
| **SINTRAN III Utilities Manual** | ND-60.151.3 EN | 2,257 | SINTRAN III utility programs manual |
| **Disk Mirroring Operator Guide** | ND-30.070.1 EN | 2,779 | Operating a mirrored-disk SINTRAN system, 72 pages with preface, chapters and an appendix. Operator-facing software guide - the disk *controller* hardware manuals are in [Devices/](Devices/README.md) |
| **SINTRAN III - How to order it** | ND-30.053.01 | 1,849 | SINTRAN III ordering / product-structure guide |
| **SINTRAN III Real Time Loader - System Documentation** | ND-60.072.02 | 1,620 | RT loader internal / system documentation |
| **SINTRAN Utility Programs** | ND-10022S | 1,158 | SINTRAN utility programs package (version S) |
| **List of special commands for communicating with SINTRAN III** | - | 1,083 | NDIX FE device-call reference (feclos/feopen/etc.) for communicating with SINTRAN III sub-devices |
| **SINTRAN III-VSX Fatal Error Routine Addresses** | ND-820059.1 EN | 953 | Fatal-error routine address list for SINTRAN III-VSX |
| **WinLink User Guide** | ND-860452EN1 | 919 | WinLink (ND 230210), 1991: connect a PC running Microsoft Windows 3 to a SINTRAN host - terminal emulation, EasyLink file transfer PC ↔ host, host selection (Ethernet), screen colours/fonts, communication settings (serial). Companion install folder: ND-891092EN1 below |
| **SINTRAN III Accounting System** | ND-10315B | 584 | Accounting system for SINTRAN III |
| **SINTRAN III Quick Reference Card** | ND-60.174.Q01 | 537 | Quick reference card |
| **SINTRAN III Configuration Program** | 211024C | 205 | System configuration program note |
| **How to install WinLink** | ND-891092EN1 | 89 | One-folder install guide for WinLink: prerequisites (PC Starter Kit ND 230123, ND Connect Module ND 230125, OWS Access/Terminal Server), required install order, multi-user (network server) installation |

**Key Topics:** SINTRAN III commands, real-time programming, RT loader, timesharing/batch, communications, WinLink PC connection, accounting, utilities, system data fields, VSX, operations administration

**Related:**
- [SINTRAN/OS/README.md](../SINTRAN/OS/README.md) - Operating system internals
- [SINTRAN/SINTRAN Structures/SINTRAN-STRUCTURES.md](../SINTRAN/SINTRAN%20Structures/SINTRAN-STRUCTURES.md) - Kernel data structures

---

### Database Systems (SIBAS)

SIBAS - the Norsk Data CODASYL / DBTG-style (network model) database system, accessed
from a host language (COBOL, FORTRAN).

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **THE DATABASE SYSTEM SIBAS II - ND User Manual** | ND-60.127.5 EN | 13,080 | Primary SIBAS II user manual - schema, realms, DML, host-language access (replaces ND-60.057) |
| **SIBAS II Operator Manual** | ND-30.009.3 EN | 3,548 | SIBAS II database administration / operator procedures |
| **The Data Base System SIBAS - An Introduction (December 1974)** | ND-60.057.01 | 2,392 | Early introduction to the SIBAS database system |
| **SIBAS II for ND-100** | 210166F | 1,196 | SIBAS II product documentation for the ND-100 |
| **The Data Base System SIBAS I - Users Manual, Appendix A** | ND-60.057.03 | 1,063 | SIBAS I users manual (Appendix A) - earlier generation |
| **Parametere i SIBAS-kall** | ND-SIBAS-01 NO | 406 | (NO) Norwegian note on the parameters of SIBAS run-unit calls |

**Key Topics:** CODASYL/DBTG network database, realms, schema, DML, host-language (COBOL/FORTRAN) access, operator administration

**Related:** [Developer/Languages/Application/SIBAS-DEVELOPER-GUIDE.md](../Developer/Languages/Application/SIBAS-DEVELOPER-GUIDE.md)

---

### Assemblers

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **MAC Interactive Assembly and Debugging** | ND-60.096.01 | 6,019 | MAC assembler and debugger - interactive assembly, BRF format, debugging |
| **NORD-500 Assembler Reference** | ND-60.113.02 EN | 4,139 | Complete ND-500 assembly - NRF format, structured programming, domains |
| **NORD-50 Assembler** | ND-60.075.01A | 1,952 | NORD-50 assembler reference |
| **Assembler for NORD-5 (April 1972)** | - | 1,384 | Early NORD-5 assembler manual |
| **COURSE MANUAL CF20 - Introduction to Assembly Programming (February 1975)** | - | 1,198 | Introductory assembly-programming course manual (CF20) |
| **MACM Mac Mass Storage Assembler** | ND-60.009.02 | 627 | MACM macro assembler - assembly, macros, mass storage linking |
| **ASSEMBLER FOR ND-500** | ND-10311A | 78 | ND-500 assembler product note (software-library) |

**Key Topics:** Assembly language, macro programming, debugging, object file formats (BRF, NRF), NORD-5/NORD-50/ND-500 targets

**Related:** See [Developer/Languages/System/MAC-DEVELOPER-GUIDE.md](../Developer/Languages/System/MAC-DEVELOPER-GUIDE.md)

---

### Intel-8080 Cross-Tools

Cross-development tools for the Intel-8080 microprocessor, hosted on NORD hardware.

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **Cross-Assembler for Intel-8080 (January 1977)** | - | 374 | Intel-8080 cross-assembler hosted on NORD |
| **Simulator and Debugger for Intel-8080 (January 1977)** | - | 668 | Intel-8080 simulator/debugger hosted on NORD |

**Key Topics:** Intel-8080 cross-assembly, simulation, debugging, cross-development

---

### System Programming Language

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **NORD PL User's Guide** | ND-60.047.03 | 4,239 | NPL (NORD Programming Language) complete reference - system programming, NPL syntax, OS development |

**Key Topics:** NPL language, system programming, kernel development, MAC code generation

**Related:**
- [Developer/Languages/System/NPL-DEVELOPER-GUIDE.md](../Developer/Languages/System/NPL-DEVELOPER-GUIDE.md)
- [SINTRAN/NPL-SOURCE/](../SINTRAN/NPL-SOURCE/) - Actual SINTRAN III NPL source code

---

### Application Languages

#### C Language

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **CC-100 and CC-500 C-Compiler User Manual** | ND-60.214.01 | 4,768 | Complete C compiler reference for ND-100 and ND-500 systems |

**Key Topics:** C language, compiler usage, ND-100/ND-500 differences, optimization

**Related:** [Developer/Languages/Application/C-DEVELOPER-GUIDE.md](../Developer/Languages/Application/C-DEVELOPER-GUIDE.md)

#### PLANC

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **PLANC Reference Manual** | ND-60.117.5 EN | 14,995 | Complete PLANC language reference - structured programming, modules |
| **PLANC - User Guide and Reference Manual** | ND-860117-6 EN | 12,731 | PLANC user guide and reference manual (later edition) |
| **ND-Specific Programming & Advanced PLANC** | ND-20034-1 EN | 4,923 | ND-specific programming techniques and advanced PLANC topics |
| **PLANC FOR ND-100** | ND-10309B | 220 | PLANC compiler for ND-100 (B-release) - setup, restrictions, runtime |
| **PLANC FOR ND-100** | ND-10309A | 162 | PLANC compiler for ND-100 (A-release) - earlier version of ND-10309B |

**Key Topics:** PLANC syntax, structured programming, modular design, ND-specific extensions

**Note:** ND-60.117.5 has one missing page (documented in source). ND-10309A and ND-10309B are the A- and B-releases of the same product note.

#### PASCAL

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **ND-PASCAL User's Guide** | ND-60.124.05 | 3,671 | ND-PASCAL language reference - PASCAL syntax, compiler, runtime |
| **NORD-10 PASCAL (June 1979)** | ND-60.086.02 | 1,721 | PASCAL for the NORD-10 |
| **PASCAL for ND-100 - NORD Software Library Revision Log** | - | 136 | Revision log for the PASCAL NORD Software Library product (10076J/10133J/10187J) |
| **ND-100 Pascal version J - Installation** | - | 77 | Installation notes for PASCAL version J on the ND-100 |
| **PASCAL for ND-100 - NORD Software Library Program Description** | ND-10076J | 38 | Program description for PASCAL (ND-10076J) NORD Software Library |
| **PASCAL for ND-100 - NORD Software Library Diskette** | ND-10076J | 27 | Diskette listing for PASCAL (ND-10076J) NORD Software Library |

**Key Topics:** PASCAL language, structured programming, data types, NORD-10/ND-100 targets, software-library distribution

#### COBOL

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **COBOL Reference Manual** | ND-60.144.3 EN | 20,168 | COBOL language reference - business programming, file handling |
| **NORD-10 COBOL Reference Manual (May 1979)** | ND-60.089.03 | 4,790 | COBOL for the NORD-10 |
| **COBOL - NORD Software Library Diskette (22 November 1979)** | ND-10020G | 407 | Diskette listing for the COBOL NORD Software Library product |

**Key Topics:** COBOL syntax, business data processing, file I/O, NORD-10 target, software-library distribution

#### FORTRAN

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **ND FORTRAN Reference Manual** | ND-60.145.7A EN | 16,676 | ND FORTRAN (ANSI 77, Version 7A 1986) - Extended FORTRAN, optimization |
| **NORD-10 FORTRAN System Reference Manual** | ND-60.074.01 | 8,020 | Complete NORD-10 FORTRAN system reference |
| **NORD Standard FORTRAN Reference** | ND-60.011.04 | 5,195 | NORD Standard FORTRAN (1974) - FORTRAN IV, scientific computing |
| **FORTRAN 32 Bits Floating Format** | ND-10033K | 377 | 32-bit floating-point format used by FORTRAN |
| **FORTRAN for ND-500** | ND-10190D | 280 | FORTRAN targeting the ND-500 processor |
| **Fortran for ND-100 / NORD-10** | ND-10191A | 135 | ND-100 / NORD-10 FORTRAN compiler product note |

**Key Topics:** FORTRAN language, scientific computing, numerical analysis, floating-point format, ND-100/NORD-10/ND-500 targets

#### BASIC

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **NORD-10 BASIC Compiler Reference** | ND-60.071.01D | 8,512 | NORD-10 BASIC Compiler - Compiled BASIC, optimization |
| **NORD BASIC Reference Manual** | ND-60.040.02 | 4,908 | NORD BASIC (1975) - Interactive BASIC programming |

**Key Topics:** BASIC language, interactive programming, compilation

#### SIMULA

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **NORD-100 SINTRAN III SIMULA - Reference Manual** | ND-60.092.03 | 2,449 | SIMULA language reference for the NORD-100 under SINTRAN III |

**Key Topics:** SIMULA language, simulation, object-oriented / class programming

---

### Compilers & Linkers

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **ND Linker User Guide and Reference** | ND-860289-2 EN | 11,721 | Complete linker reference - object file linking, library management, symbol resolution |
| **ND Relocating Loader** | ND-60.066.04 | 2,343 | Loader documentation - program loading, relocation, memory allocation |

**Key Topics:** Linking, loading, relocation, symbol resolution, library management

**Related:**
- [Developer/Workflow/LINKING-GUIDE.md](../Developer/Workflow/LINKING-GUIDE.md) - NRL, BRF, BPUN, PROG and NRF (the ND-100 side; a separate `LINKING-GUIDE-100-DEEP-DIVE.md` was listed here but was never written)
- [Developer/Workflow/LINKING-GUIDE-500-DEEP-DIVE.md](../Developer/Workflow/LINKING-GUIDE-500-DEEP-DIVE.md)

---

### Debuggers

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **Symbolic Debugger - User Guide** | ND-60158-5 EN | 6,749 | Symbolic Debugger user guide - source-level debugging |
| **ND-500 Symbolic Debugger** | ND-10335B | 160 | ND-500 Symbolic Debugger product note |

**Key Topics:** symbolic/source-level debugging, breakpoints, program inspection

---

### Editors

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **LED User Guide** | ND-60.266.2 EN | 2,091 | LED program editor for ND-500 (ND 211160B), version 2 (April 1988) - windows/regions, home and function-key commands, navigation, editing, user-written key-bound extensions, plus chapter 7 on the LED Debugger for ND-500 (ND 211157B, enhanced Symbolic Debugger). Appendix D compares LED with PED |
| **PED User's Guide** | ND-60.121.4 | 4,890 | PED editor reference (English) - screen-oriented text editing |
| **PED Bruker-Veiledning** | ND-60.148.01 | 1,787 | PED editor guide (Norwegian) - Norwegian language version |
| **QED User Manual** | ND-60.031.04 EN | 1,537 | QED editor reference - line-oriented text editing |
| **BRF EDITOR** | ND-60.085.01 | 289 | BRF file editor - binary relocatable format editing |

**Key Topics:** Text editing, file editing, screen editors, line editors

**Related:** [Developer/Editors/](../Developer/Editors/)

---

### Office Software (NOTIS-1)

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **NOTIS-1 Users Guide (February 1981)** | ND-60.120.03 | 5,354 | Users guide for NOTIS-1, the early Norsk Data office/word-processing system |

**Key Topics:** NOTIS-1, early office automation, word processing

**Related:** the full NOTIS office suite is indexed in the [NOTIS Office System sub-collection](Notis/README.md).

---

### Diagnostics & Test Programs

Test-program and diagnostic documentation for the ND-100/ND-110/ND-120 processor family.

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **Test Program Description for ND-100/110** | ND-830005.3 EN | 10,075 | Test-program description for ND-100/ND-110 |
| **Test Programs for ND-100/110/120 - Software Library** | ND-210523G | 1,932 | Library diskette listing of test programs for ND-100/110/120 |
| **Test Program Description for ND-100/ND-110 - Addendum (December 1998)** | ND-899159.1 EN | 1,423 | Addendum to the ND-100/ND-110 test-program description (merged from two OCR passes) |
| **ND-500 Micro Test Programs** | ND-10321D | 257 | Software-library diskette listing for the ND-500 micro test programs (two diskette parts, March 1982) |

**Key Topics:** hardware diagnostics, test programs, ND-100/110/120, acceptance/verification testing

**Note:** ND-899159.1 was merged from two OCR captures, taking the best version of each page. Pages 2, 32 and 43 were unreadable in both scans and are marked as not captured.

---

### Documentation & Catalogues

| Manual | Document # | Lines | Description |
|--------|-----------|-------|-------------|
| **Documentation Catalogue** | ND-40.004.7 EN | 5,469 | Catalogue of Norsk Data documentation - document numbers, titles, product structure |

**Key Topics:** documentation index, document numbering, product structure

---

## 🔗 Cross-Reference to Developer Guides

### System Languages → [Developer/Languages/System/](../Developer/Languages/System/)

| Language | Reference Manuals | Developer Guide | Status |
|----------|-------------------|-----------------|--------|
| **NPL** | ND-60.047.03 | NPL-DEVELOPER-GUIDE.md | ✅ Complete |
| **MAC** | ND-60.096.01, ND-60.009.02 | MAC-DEVELOPER-GUIDE.md | ✅ Complete |
| **NORD-500 Asm** | ND-60.113.02, ND-05.009.4 | NORD-500-ASSEMBLER-DEVELOPER-GUIDE.md | ✅ Complete |

### Application Languages → [Developer/Languages/Application/](../Developer/Languages/Application/)

| Language | Reference Manuals | Developer Guide | Status |
|----------|-------------------|-----------------|--------|
| **C** | ND-60.214.01 | C-DEVELOPER-GUIDE.md | ✅ Complete |
| **PLANC** | ND-60.117.5, ND-860117-6, ND-20034-1, ND-10309A/B | PLANC-DEVELOPER-GUIDE.md | 🚧 Placeholder |
| **PASCAL** | ND-60.124.05, ND-60.086.02 | PASCAL-DEVELOPER-GUIDE.md | 🚧 Placeholder |
| **COBOL** | ND-60.144.3, ND-60.089.03 | COBOL-DEVELOPER-GUIDE.md | 🚧 Placeholder |
| **FORTRAN** | ND-60.145.7A, ND-60.074.01, ND-60.011.04, ND-10191A, ND-10190D, ND-10033K | FORTRAN-DEVELOPER-GUIDE.md | 🚧 Placeholder |
| **BASIC** | ND-60.040.02, ND-60.071.01D | BASIC-DEVELOPER-GUIDE.md | 🚧 Placeholder |
| **SIMULA** | ND-60.092.03 | (none yet) | 🚧 Reference only |
| **SIBAS** (database) | ND-60.127.5, ND-30.009.3, 210166F, ND-60.057.01, ND-60.057.03 | SIBAS-DEVELOPER-GUIDE.md | 🚧 Reference index |

### Development Tools → [Developer/Workflow/](../Developer/Workflow/)

| Tool | Reference Manuals | Workflow Guide | Status |
|------|-------------------|----------------|--------|
| **Linker** | ND-860289-2 EN | LINKING-GUIDE.md, LINKING-GUIDE-500-DEEP-DIVE.md | ✅ Complete |
| **Loader** | ND-60.066.04 | (Covered in linking guides) | ✅ Complete |
| **Debuggers** | ND-60158-5, ND-10335B | (Covered in language/tool guides) | 🚧 Reference only |
| **Editors** | ND-60.031.04, ND-60.121.4 | [Developer/Editors/](../Developer/Editors/) | ✅ Complete |

---

## 🚀 How to Use These Manuals

### For Learning SINTRAN Development

**Step 1: Choose Your Language**
- System programming → Start with NPL (ND-60.047.03)
- Application development → Choose PLANC, PASCAL, C, FORTRAN, COBOL, SIMULA, or BASIC
- Low-level programming → Start with MAC (ND-60.096.01) or ND-500 Assembler (ND-60.113.02)

**Step 2: Understand the System**
- Read SINTRAN Commands Reference for system interaction
- Read SINTRAN III Monitor Calls for system call interface
- Read ND-500 Reference Manual for CPU architecture (if using ND-500)

**Step 3: Set Up Development Environment**
- QED or PED User Manual for text editing
- Linker User Guide for linking programs
- Workflow guides in [Developer/Workflow/](../Developer/Workflow/)

### For Building an Emulator

**Critical Manuals:**
1. **ND-05.009.4** - ND-500 CPU instruction set and architecture
2. **ND-10.004.01** - MPM5 hardware (5MPM shared memory)
3. **ND-860228-2 EN** - SINTRAN III Monitor Calls (system call interface)
4. **ND-60.047.03** - NPL language (to read SINTRAN source code)

**Workflow:**
1. Read hardware manuals for CPU and memory architecture
2. Cross-reference with [SINTRAN/NPL-SOURCE/](../SINTRAN/NPL-SOURCE/) actual source code
3. Use [SINTRAN/Emulator/](../SINTRAN/Emulator/) C# implementation guides
4. Validate against [SINTRAN/OS/](../SINTRAN/OS/) kernel documentation

### For System Programming

**Essential Manuals:**
- **NPL User's Guide** (ND-60.047.03) - Language reference
- **Monitor Calls** (ND-860228-2 EN) - System call interface
- **MAC Assembler** (ND-60.096.01) - Understanding NPL output
- **Linker Guide** (ND-860289-2 EN) - Linking and libraries

**Workflow:**
1. Write code in NPL
2. Compile to MAC assembly
3. Assemble to object files
4. Link with system libraries
5. Test and debug

### For Application Development

**Essential Manuals:**
- **Your chosen language manual** (PLANC, PASCAL, C, FORTRAN, COBOL, SIMULA, BASIC)
- **SINTRAN Commands Reference** - File I/O and system interaction
- **QED or PED User Manual** - Text editing
- **Linker Guide** - Linking applications

**Workflow:**
1. Read language manual for syntax
2. Check [Developer/Languages/Application/](../Developer/Languages/Application/) for quick start
3. Follow [Developer/Workflow/](../Developer/Workflow/) for compilation
4. Use SINTRAN Commands Reference for system operations

---

## 📋 Manual Quality & Versions

### OCR Sources

All manuals are high-quality OCR-scanned versions from original NORD/SINTRAN documentation:

- **Gandalf-OCR** - Primary OCR processing (high quality)
- **Tingo-OCR** - Alternative OCR processing
- **Web versions** - Some manuals have web-optimized versions (e.g., SINTRAN III Monitor Calls-WEB.md)

### Known Issues

| Issue | Affected Manuals | Notes |
|-------|------------------|-------|
| **Missing page** | ND-60.117.5 (PLANC) | One page missing, documented in source |
| **OCR artifacts** | Various | Minor formatting issues, generally readable |
| **Blank / unreadable scan pages** | NEC-01 course, ND-80.001.2 (500/) | Some scanned pages could not be OCR'd |
| **Page numbers** | All | Original page numbers preserved |
| **Cross-references** | All | References use original document numbers |
| **Formatting variance** | All | Each manual has unique formatting from original |

### Version / Duplicate Notes

- **SINTRAN III Monitor Calls** - ND-860228-2 exists as a standard edition (31,268 lines) and a web-optimized `-WEB` edition (30,666 lines); same document.
- **PLANC ND-10309** - A-release (ND-10309A) and B-release (ND-10309B) product notes; same product.
- **Test Program Addendum ND-899159.1** - merged from two OCR captures (best page of each); pages 2, 32 and 43 were unreadable in both scans.
- **Six FORTRAN manuals** - ND-60.011.04 (1974 standard), ND-60.145.7A (ANSI 77 extended), ND-60.074.01 (NORD-10 system), plus product/format notes ND-10191A (ND-100/NORD-10), ND-10190D (ND-500), ND-10033K (32-bit floating format).
- **Two BASIC manuals** - ND-60.040.02 (interactive) and ND-60.071.01D (compiled).
- **Two PED manuals** - English (ND-60.121.4) and Norwegian (ND-60.148.01).
- **SIBAS generations** - SIBAS I (ND-60.057.01, ND-60.057.03) superseded by SIBAS II (ND-60.127.5, which replaces ND-60.057).

---

## 📊 Statistics

### By Category (Root)

| Category | Manuals |
|----------|---------|
| System & CPU Architecture | 5 |
| Hardware Documentation | 1 |
| ND-100 / ND-110 Hardware | 6 |
| SINTRAN III System & OS | 28 |
| Database (SIBAS) | 6 |
| Assemblers | 7 |
| Intel-8080 Cross-Tools | 2 |
| System Programming Language (NPL) | 1 |
| Application Languages | 24 |
| Compilers & Linkers | 2 |
| Debuggers | 2 |
| Editors | 5 |
| Office Software (NOTIS-1) | 1 |
| Diagnostics & Test Programs | 4 |
| Documentation & Catalogues | 1 |
| **Total (Root)** | **95** |

### Whole Collection

| Location | Manuals |
|----------|---------|
| Root | 95 |
| [1/](1/README.md) - NORD-1 | 5 |
| [10/](10/README.md) - NORD-10 | 13 |
| [500/](500/README.md) - ND-500 / ND-5000 | 23 |
| [Devices/](Devices/README.md) - Device Controllers | 7 |
| [Notis/](Notis/README.md) - NOTIS Office System | 31 |
| **Grand Total** | **171** |

### By Era

| Era | Key Documents |
|-----|---------------|
| **Early (1972-1975)** | Assembler for NORD-5 (1972), NORD Standard FORTRAN (1974), SIBAS Introduction (1974), NORD BASIC (1975), CF20 Assembly course (1975) |
| **Mid (1976-1980)** | Intel-8080 cross-tools, NORD-10 FORTRAN/PASCAL/COBOL, PASCAL software library |
| **Late (1981-1987)** | SINTRAN III manuals, C compiler, PLANC, VSX documentation, NOTIS-1 |
| **1990s** | WinLink User Guide + install folder (1991), Test Program Description addendum (1998) |

---

## 🔍 Quick Document Number Reference

| Doc Number | Title | Category | Lines |
|------------|-------|----------|-------|
| ND-05.009.4 | ND-500 Reference Manual | System/CPU | 16,323 |
| ND-06.007.01 | BIG MULTIPORT MEMORY SYSTEM | ND-100/110 HW | 4,519 |
| ND-06.014.2A | ND-100 Reference Manual | ND-100/110 HW | 9,590 |
| ND-06.015.02 | ND-100 Functional Description | ND-100/110 HW | 13,839 |
| ND-06.016.01 | NORD-100 Input/Output System | ND-100/110 HW | 8,708 |
| ND-06.026-1 | ND-110 Functional Description | ND-100/110 HW | 9,805 |
| ND-06.029.1 | ND-110 Instruction Set | ND-100/110 HW | 8,436 |
| ND-10.004.01 | MPM 5 Technical Description | Hardware | 2,991 |
| ND-10020G | COBOL Software Library Diskette | Language (COBOL) | 407 |
| ND-10022S | SINTRAN Utility Programs | SINTRAN III | 1,158 |
| ND-10033K | FORTRAN 32 Bits Floating Format | Language (FORTRAN) | 377 |
| ND-10076J | PASCAL Software Library (program desc / diskette) | Language (PASCAL) | 38 / 27 |
| ND-10190D | FORTRAN for ND-500 | Language (FORTRAN) | 280 |
| ND-10191A | Fortran for ND-100 / NORD-10 | Language (FORTRAN) | 135 |
| ND-10309A | PLANC FOR ND-100 (A-release) | Language (PLANC) | 162 |
| ND-10309B | PLANC FOR ND-100 (B-release) | Language (PLANC) | 220 |
| ND-10311A | ASSEMBLER FOR ND-500 | Assembler | 78 |
| ND-10315B | SINTRAN III Accounting System | SINTRAN III | 584 |
| ND-10321D | ND-500 MICRO TEST PROGRAMS | Diagnostics | 257 |
| ND-10335B | ND-500 Symbolic Debugger | Debugger | 160 |
| ND-20034-1 | ND-Specific Programming & Advanced PLANC | Language (PLANC) | 4,923 |
| ND-210523G | Test Programs for ND-100/110/120 | Diagnostics | 1,932 |
| ND-30.009.3 | SIBAS II Operator Manual | Database | 3,548 |
| ND-30.053.01 | SINTRAN III - How to order it | SINTRAN III | 1,849 |
| ND-40.004.7 | Documentation Catalogue | Documentation | 5,469 |
| ND-60.009.02 | MACM Assembler | Assembler | 627 |
| ND-60.011.04 | NORD Standard FORTRAN | Language (FORTRAN) | 5,195 |
| ND-60.031.04 | QED User Manual | Editor | 1,537 |
| ND-60.040.02 | NORD BASIC | Language (BASIC) | 4,908 |
| ND-60.044.01 | SINTRAN II Operator's Guide | SINTRAN | 2,919 |
| ND-60.047.03 | NORD PL User's Guide | System Language | 4,239 |
| ND-60.050.06 | SINTRAN III Users Guide | SINTRAN III | 11,589 |
| ND-60.051.8 | SINTRAN III - Real Time Loader | SINTRAN III | 3,430 |
| ND-60.057.01 | SIBAS - An Introduction | Database | 2,392 |
| ND-60.057.03 | SIBAS I Users Manual, Appendix A | Database | 1,063 |
| ND-60.066.04 | ND Relocating Loader | Tools | 2,343 |
| ND-60.071.01D | NORD-10 BASIC Compiler | Language (BASIC) | 8,512 |
| ND-60.072.02 | SINTRAN III RT Loader - System Doc | SINTRAN III | 1,620 |
| ND-60.074.01 | NORD-10 FORTRAN System | Language (FORTRAN) | 8,020 |
| ND-60.075.01A | NORD-50 Assembler | Assembler | 1,952 |
| ND-60.085.01 | BRF EDITOR | Editor | 289 |
| ND-60.086.02 | NORD-10 PASCAL | Language (PASCAL) | 1,721 |
| ND-60.089.03 | NORD-10 COBOL | Language (COBOL) | 4,790 |
| ND-60.092.03 | NORD-100 SINTRAN III SIMULA | Language (SIMULA) | 2,449 |
| ND-60.096.01 | MAC Interactive Assembly | Assembler | 6,019 |
| ND-60.112.01 | SINTRAN III System Doc, Appendix A - Data Fields | SINTRAN III | 4,455 |
| ND-60.113.02 | NORD-500 Assembler | Assembler | 4,139 |
| ND-60.117.5 | PLANC Reference Manual | Language (PLANC) | 14,995 |
| ND-60.120.03 | NOTIS-1 Users Guide | Office | 5,354 |
| ND-60.121.4 | PED User's Guide (EN) | Editor | 4,890 |
| ND-60.124.05 | ND-PASCAL User's Guide | Language (PASCAL) | 3,671 |
| ND-60.125.04 | SINTRAN III Introduction | SINTRAN III | 3,245 |
| ND-60.127.5 | SIBAS II - ND User Manual | Database | 13,080 |
| ND-60.128.5 | SINTRAN III Reference Manual | SINTRAN III | 21,694 |
| ND-60.132.03 | SINTRAN III Timesharing / Batch Guide | SINTRAN III | 6,616 |
| ND-60.133.02A | SINTRAN III Real Time Guide | SINTRAN III | 14,445 |
| ND-60.134.2 | SINTRAN III Communication Guide | SINTRAN III | 5,740 |
| ND-60.136.04A | ND-500 Loader Monitor | System/ND-500 | 11,394 |
| ND-60.144.3 | COBOL Reference | Language (COBOL) | 20,168 |
| ND-60.145.7A | ND FORTRAN Reference | Language (FORTRAN) | 16,676 |
| ND-60.148.01 | PED Bruker-Veiledning (NO) | Editor | 1,787 |
| ND-60.151.3 | SINTRAN III Utilities Manual | SINTRAN III | 2,257 |
| ND-60.164.3 | COSMOS Programmer Guide | SINTRAN III | 16,900 |
| ND-60.174.Q01 | SINTRAN III Quick Reference Card | SINTRAN III | 537 |
| ND-60.197.01 | Ethernet Basic Software Programmer Guide | Networking | 2,404 |
| ND-60.214.01 | CC-100/500 C-Compiler | Language (C) | 4,768 |
| ND-60.250.1 | BACKUP User Guide | SINTRAN III | 5,489 |
| ND-60.266.2 | LED User Guide | Editor | 2,091 |
| ND-60158-5 | Symbolic Debugger - User Guide | Debugger | 6,749 |
| ND-820023-1 | SINTRAN III-VSX System Documentation | SINTRAN III | 12,107 |
| ND-820059.1 | SINTRAN III-VSX Fatal Error Routine Addresses | SINTRAN III | 953 |
| ND-830005.3 | Test Program Description for ND-100/110 | Diagnostics | 10,075 |
| ND-860117-6 | PLANC - User Guide and Reference | Language (PLANC) | 12,731 |
| ND-860228-2 | SINTRAN III Monitor Calls (std / web) | System | 31,268 / 30,666 |
| ND-860289-2 | ND Linker User Guide | Tools | 11,721 |
| ND-860372.1 | SINTRAN SLIB Programmers Guide | Networking | 8,572 |
| ND-860452EN1 | WinLink User Guide | SINTRAN III | 919 |
| ND-891092EN1 | How to install WinLink | SINTRAN III | 89 |
| ND-899159.1 | Test Program Description Addendum (1998) | Diagnostics | 1,423 |
| ND-SIBAS-01 | Parametere i SIBAS-kall (NO) | Database | 406 |
| ND-US05-1 | US05 SINTRAN III Workshop | SINTRAN III | 3,178 |
| 210166F | SIBAS II for ND-100 | Database | 1,196 |
| 211024C | SINTRAN III Configuration Program | SINTRAN III | 205 |
| - | SINTRAN III Håndbok for driftsansvarlig (NO) | SINTRAN III | 22,933 |
| - | SINTRAN Commands Reference | System | 11,656 |
| - | List of special commands (NDIX FE) | SINTRAN III | 1,083 |
| - | Assembler for NORD-5 (1972) | Assembler | 1,384 |
| - | COURSE MANUAL CF20 Assembly Programming (1975) | Assembler | 1,198 |
| - | Cross-Assembler for Intel-8080 (1977) | Intel-8080 | 374 |
| - | Simulator and Debugger for Intel-8080 (1977) | Intel-8080 | 668 |
| - | PASCAL NORD Software Library Revision Log | Language (PASCAL) | 136 |
| - | ND-100 Pascal version J Installation | Language (PASCAL) | 77 |

---

## 🔗 Related Documentation

### Developer Resources
- **[Developer/README.md](../Developer/README.md)** - Main developer documentation entry point
- **[Developer/Languages/README.md](../Developer/Languages/README.md)** - Language-specific guides
- **[Developer/Workflow/README.md](../Developer/Workflow/README.md)** - Compilation and linking workflows
- **[Developer/Editors/README.md](../Developer/Editors/README.md)** - Editor documentation

### SINTRAN System
- **[SINTRAN/README.md](../SINTRAN/README.md)** - SINTRAN III system documentation
- **[SINTRAN/OS/README.md](../SINTRAN/OS/README.md)** - Operating system internals
- **[SINTRAN/NPL-SOURCE/README.md](../SINTRAN/NPL-SOURCE/README.md)** - Actual SINTRAN source code

### Sub-Collections
- **[500/README.md](500/README.md)** - ND-500 / ND-5000 manuals
- **[Devices/README.md](Devices/README.md)** - Device controllers
- **[Notis/README.md](Notis/README.md)** - NOTIS office system

### Quick Start
- **[Developer/SINTRAN-DEVELOPER-GUIDE.md](../Developer/SINTRAN-DEVELOPER-GUIDE.md)** - Comprehensive developer guide
- **[Developer/QUICK-START-EXAMPLES.md](../Developer/QUICK-START-EXAMPLES.md)** - Hello World examples

---

## 🤝 Contributing

When adding new reference manuals:

1. **Naming Convention**: `ND-XX.XXX.XX [Title].md`
2. **Remove OCR Suffixes**: Clean up `-Gandalf-OCR_combined` from filenames
3. **Check Duplicates**: Compare line counts and content quality before adding
4. **Update This README**: Add manual to appropriate category with description
5. **Cross-Reference**: Link to relevant developer guides
6. **Document Quality**: Note any missing pages or OCR issues

---

**Last Updated**: 2026-08-17
**Total Manuals (Root)**: 94
**Total Manuals (All Collections)**: 170
**Status**: ✅ Complete Collection

---

*These manuals represent the complete technical documentation for the NORD/SINTRAN computing platform from the 1970s-1990s era.*
