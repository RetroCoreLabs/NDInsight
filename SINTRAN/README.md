# SINTRAN III Documentation

**Complete Documentation for SINTRAN III Operating System**

---

## Overview

This folder contains comprehensive documentation for the SINTRAN III/VS operating system used on NORD-10/ND-100 computer systems, including ND-500 multiprocessor integration.

### Purpose

SINTRAN III was a sophisticated real-time operating system providing:
- Real-time multitasking with priority-based scheduling  
- Demand paging virtual memory  
- Multi-level interrupt handling (16 levels)
- Multi-CPU support (ND-100 + ND-500)
- Device-independent I/O system

---

## Folder Structure

| Folder | Contents | Files |
|--------|----------|-------|
| [Devices/](Devices/README.md) | Hardware device documentation (HDLC, SCSI, SMD, Octobus, FloppyDMA, bus signals) | 177 files |
| [Emulator/](Emulator/README.md) | C# emulator implementation guides | 16 files |
| [File-Formats/](File-Formats/README.md) | ND object and executable file formats: BRF, `:PROG`, `:NRF`, `:DOM`/`:SEG`, `:LINK`, `DESCRIPTION-FILE:DESC` - the four ND-500 formats (`:NRF`, `:DOM`, `:LINK`, DESC) each with a machine-readable `.json`, a drag-and-drop browser viewer for NRF, DOM/SEG and DESC files (start it with `viewer/run.bat`), and `samples/` with the real vendor DESC and `:LINK` files the findings were checked against | 44 files |
| [Filesystem/](Filesystem/README.md) | SINTRAN III directory-device on-disk format: master block, object entry, user entry, page bitmap, boot sector - byte-verified against real disk images | 21 files |
| [ND500/](ND500/README.md) | ND-500 CPU architecture, the 3022/5015 bus interface, SINTRAN integration, and the MON-call hub | 482 files |
| [ND500-APPS/](ND500-APPS/README.md) | **ND-500 vendor programs (FraTor DOMs): runnable files + user guide per program** | **13 programs, 75 files** |
| [ND5000/](ND5000/README.md) | ND-5000 (SAMSON) generation: Octobus protocol, ACCP access module, ND-5800 microcode, and the RetroCore ND-100 <-> ND-5000 emulation | 65 files |
| [NPL-SOURCE/](NPL-SOURCE/README.md) | **SINTRAN III NPL source code & symbols** | **45 NPL + 7 symbol files** |
| [OS/](OS/README.md) | Core operating system architecture (00-19) | 42 files |
| [Print/](Print/README.md) | Printing and output spooling: peripheral files, spooling queues, printer hardware, remote printing, and an emulated PDF printer design | 13 files |
| [Release-Documentation/](Release-Documentation/) | SINTRAN III release information (versions J-N) | 8 files |
| [SINTRAN Structures/](SINTRAN%20Structures/) | System structures and data analysis | 6 files |
| [TAD/](TAD/README.md) | TAD protocol analysis (X.25, HDLC encapsulation) | 8 files |
| [TSS/](TSS/) | Introduction to TSS - slide deck and PDF only, no written notes yet | 2 files |
| [XMSG/](XMSG/README.md) | XMSG message system: wire protocol, MON 200B API, C# library, COSMOS RE | 4287 files (incl. C# sources) |

**ND-500 <-> ND-100 interface reverse-engineering (done, byte-verified from L07):**
- Status of record + master index: `SINTRAN/ND500/ND500-STATUS-AND-INDEX.md`
  ([ND500/ND500-STATUS-AND-INDEX.md](ND500/ND500-STATUS-AND-INDEX.md))
- MON 60B / N500M worker carve (47 subfunction folders + 5IFUNC table):
  `tools/sintran-segment-carver/versions/L-VSX-500/re/mon-analysis/60B-N500M/`
- ND-500 system monitor carve (FUNCS table, 3022 IOX driver, control-store gate, 5MPM message, level-12 return):
  `tools/sintran-segment-carver/versions/L-VSX-500/re/ND500-SYSTEM-MONITOR/`

---

## Quick Start

### Understanding SINTRAN III

**Start here:**
1. [OS/00-SINTRAN-ARCHITECTURE-OVERVIEW.md](OS/00-SINTRAN-ARCHITECTURE-OVERVIEW.md) - System overview
2. [OS/01-BOOT-SEQUENCE.md](OS/01-BOOT-SEQUENCE.md) - How the system boots
3. [OS/02-QUEUE-STRUCTURES-DETAILED.md](OS/02-QUEUE-STRUCTURES-DETAILED.md) - Task scheduling

**For specific topics:**
- **Memory management** → [OS/04-MMU-CONTEXT-SWITCHING.md](OS/04-MMU-CONTEXT-SWITCHING.md), [OS/16-PAGE-FAULT-HANDLER.md](OS/16-PAGE-FAULT-HANDLER.md)
- **Interrupt handling** → [OS/13-INT14-HANDLER-DETAILED.md](OS/13-INT14-HANDLER-DETAILED.md)
- **Device drivers** → [OS/18-DEVICE-DRIVER-FRAMEWORK.md](OS/18-DEVICE-DRIVER-FRAMEWORK.md)
- **ND-500 integration** → [OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md](OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md)

### Building an Emulator

**Emulator developers:**
1. Read [Emulator/KERNEL-ACCESS-EMULATOR.md](Emulator/KERNEL-ACCESS-EMULATOR.md) for C# kernel access
2. Read [Emulator/ND500-INTEGRATION-GUIDE.md](Emulator/ND500-INTEGRATION-GUIDE.md) for ND-500 support
3. Use [Emulator/ND500-QUICK-REFERENCE.md](Emulator/ND500-QUICK-REFERENCE.md) as quick reference

### Hardware Specifics

**HDLC communication:**
- [Devices/HDLC/learning/03-Hardware-Overview.md](Devices/HDLC/learning/03-Hardware-Overview.md)
- [Devices/HDLC/Quick-Reference-Card.md](Devices/HDLC/Quick-Reference-Card.md)

**SCSI disk controllers:**
- [Devices/SCSI/SCSI-Master-Index.md](Devices/SCSI/SCSI-Master-Index.md)
- [Devices/SCSI/SCSI-C#-Implementation-Guide.md](Devices/SCSI/SCSI-C%23-Implementation-Guide.md)

---

## SINTRAN III Source Code

### NPL Source Code and Symbols

**Location:** [NPL-SOURCE/](NPL-SOURCE/)

This folder contains **actual SINTRAN III operating system source code** written in NPL (Norsk Data Programming Language), extracted from the s3vs-4.symb build job output.

#### What's Included

**NPL Source Files (45 files):**
- Kernel/Monitor code (MON60)
- SCSI disk drivers (IP-P2-SCSI-*.NPL)
- HDLC communication drivers (MP-P2-HDLC-DRIV.NPL)
- ND-500 interface code (CC-P2-N500.NPL, MP-P2-N500.NPL)
- Disk I/O subsystem (IP-P2-DISK-*.NPL, MP-P2-DISK-*.NPL)
- Segment administration (IP-P2-SEGADM.NPL)
- HASP protocol implementation (MP-P2-HASP-ETC.NPL)
- Terminal and communication handling (TP-P2-*.NPL)

**Symbol Tables (7 files, SINTRAN L07):**
- **FILSYS-SYMBOLS.SYMB.TXT** (61 KB) - File system symbols
- **N500-SYMBOLS.SYMB.TXT** (122 KB) - ND-500 interface symbols
- **XMSG-SYMBOL-LIST.SYMB.TXT** (30 KB) - XMSG message system symbols
- **SYMBOL-1-LIST.SYMB.TXT** (102 KB) - Primary kernel symbols
- **SYMBOL-2-LIST.SYMB.TXT** (69 KB) - Secondary kernel symbols
- **RTLO-SYMBOLS.SYMB.TXT** (56 KB) - Runtime library symbols
- **LIBRARY-MARKS.SYMB.TXT** (14 KB) - Library entry points

#### Why This is Important

1. **Authentic Implementation** - See how SINTRAN III was actually implemented
2. **Emulator Verification** - Validate emulator behavior against real OS code
3. **Symbol Tables** - Map memory addresses to symbolic names for debugging
4. **File System Insight** - While we lack file system source, symbols provide structure information
5. **Complete Device Drivers** - Full SCSI and HDLC driver implementations

#### Using Source Code with Documentation

The NPL source code should be read alongside the OS documentation:

| Source Files | Corresponding Documentation |
|--------------|---------------------------|
| IP-P2-SCSI-*.NPL | [Devices/SCSI/](Devices/SCSI/) + [OS/15-DISK-IO-SUBSYSTEM.md](OS/15-DISK-IO-SUBSYSTEM.md) |
| MP-P2-HDLC-DRIV.NPL | [Devices/HDLC/](Devices/HDLC/) |
| CC-P2-N500.NPL, MP-P2-N500.NPL | [ND500/](ND500/) + [OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md](OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md) |
| IP-P2-SEGADM.NPL | [OS/16-PAGE-FAULT-HANDLER.md](OS/16-PAGE-FAULT-HANDLER.md) |
| 5P-P2-MON60.NPL | [OS/14-MONITOR-KERNEL-MONCALLS.md](OS/14-MONITOR-KERNEL-MONCALLS.md) |

**Full details:** [NPL-SOURCE/README.md](NPL-SOURCE/README.md)

---

## SINTRAN III Release Information

### Historical Release Documentation

**Location:** [Release-Documentation/](Release-Documentation/)

This folder contains official SINTRAN III release notes documenting system evolution across major versions:

**Release Documents (7 files):**
- **ND-60.230.01** - SINTRAN III J-version (January 1985)
- **ND-60230-5-EN** - SINTRAN III K-version Release Information
- **ND-860230-6-EN** - SINTRAN III L-version Release Information
- **ND-860230-7A-EN** - SINTRAN III M-version Release Information
- **ND-860230-8-EN** - SINTRAN III N-version Release Information
- **SINTRAN-III-Release-History.md** - Comprehensive version timeline
- **ndfs-extensions.md** - NDFS file system extensions

#### Why This is Important

1. **Feature Evolution** - Track when features were added/changed across versions
2. **Bug Fix History** - Understand what issues were resolved in each release
3. **Compatibility** - Determine version-specific behavior for emulation
4. **System Requirements** - Hardware/software requirements per version
5. **Migration Guides** - How to upgrade between versions

---

## SINTRAN System Structures

### Internal Data Structure Analysis

**Location:** [SINTRAN Structures/](SINTRAN%20Structures/)

This folder contains detailed analysis of SINTRAN III internal data structures extracted from symbol tables and source code:

**Structure Files (6 files):**
- **SINTRAN-STRUCTURES.md** (224 KB) - Master reference for all kernel structures
- **LOGICAL-DEVICE-NUMBERS.md** (24 KB) - Device number assignments
- **logical-device-numbers.json** (193 KB) - Machine-readable device mapping
- **sintran-rt-programs.json** (60 KB) - RT program metadata
- **sintran-system-segments.json** (28 KB) - System segment definitions
- **SINTRAN_PCCS_ARRAY_ANALYSIS.md** (21 KB) - PCCS array structure analysis

#### Using Structure Documentation

The structure files provide essential reference for:
- **Emulator Development** - Correctly implement kernel data structures
- **Memory Debugging** - Interpret raw memory dumps
- **Symbol Table Cross-Reference** - Link addresses to data structure fields
- **Device Driver Analysis** - Understand device number assignments

**Cross-Reference Example:**
- Read [SINTRAN Structures/SINTRAN-STRUCTURES.md](SINTRAN%20Structures/SINTRAN-STRUCTURES.md) for structure layouts
- Cross-reference with [NPL-SOURCE/](NPL-SOURCE/) symbol tables for addresses
- Use [OS/19-MEMORY-MAP-REFERENCE.md](OS/19-MEMORY-MAP-REFERENCE.md) for memory locations

---

## XMSG (message system, protocol, API and code)

All XMSG material now lives in one hub: **[XMSG/](XMSG/)** — start at
[XMSG/README.md](XMSG/README.md).

| Area | Location |
|------|----------|
| Wire-format reference (HDLC / SINTRAN header / sub-protocols) | [XMSG/DOC/XMSG-PROTOCOL.md](XMSG/DOC/XMSG-PROTOCOL.md) |
| Programming / API reference (MON 200B, XROUT letter, constants) | [XMSG/DOC/XMSG-API.md](XMSG/DOC/XMSG-API.md) |
| Operator utility (XMSG-COMMAND) | [XMSG/DOC/XMSG-COMMAND-REFERENCE.md](XMSG/DOC/XMSG-COMMAND-REFERENCE.md) |
| Official ND constants + machine-readable JSON | [XMSG/XMSG-PL-VALUES-M.INCL](XMSG/XMSG-PL-VALUES-M.INCL), [XMSG/xmsg-constants.json](XMSG/xmsg-constants.json) |
| C# protocol library + tests | [XMSG/SRC/](XMSG/SRC/) (see [XMSG/SRC/README.md](XMSG/SRC/README.md)) |
| Superseded / historical notes | [XMSG/OLD/](XMSG/OLD/) |

The HDLC hardware/framing layer beneath XMSG is documented separately in
[HDLC-Frame-Format-Reference.md](Devices/HDLC/HDLC-Frame-Format-Reference.md).

**Cross-Reference:** See also [NPL-SOURCE/XMSG-SYMBOL-LIST.SYMB.TXT](NPL-SOURCE/) for XMSG message system symbols.

---

## ND-500 Applications (FraTor vendor DOMs)

**Location:** [ND500-APPS/](ND500-APPS/README.md)

The real Norsk Data ND-500 vendor programs, preserved with **every file needed to
run them** in the `nd500x` emulator, plus a `userguide.md` per program. Each
program has its own folder with `files/` (runtime DOM/PSEG/DSEG/HELP/INIT),
`analysis/` (disassembly + RE notes), and shared runtime libraries live in
`_shared/files/`.

Programs (13): NC-A06 (C compiler), LINKER-B01, PLANC-500-G00, FILE-COMPARE,
CPU-STAT, CONVERT-DOM-A03, CAT-CAT5-B06, LED-FORTRAN-A01, LED-NEW (editor),
AUTOMAKE-500-C00, CODE-COVERAGE, TEST-REAL, BM-FILERE-B02.

- Start at [ND500-APPS/README.md](ND500-APPS/README.md) for the index, install
  steps, run conventions (the `@`-is-the-prompt rule, MODE files, scripted drive),
  the requirements model, and the FORTRAN-LIB/EXCEPT-LIB linking gap.
- The verified C compile -> link -> run chain and per-program commands are in each
  program's `userguide.md`.
- Operational workflow is also captured in the `nd500-apps` skill.

These are the standalone user-mode programs; the ND-500 <-> ND-100 kernel
interface is in [ND500/](ND500/).

---

## Documentation by Topic

### Core OS Architecture

Located in [OS/](OS/) folder:

| Chapter | Document | Topic |
|---------|----------|-------|
| 00 | SINTRAN-ARCHITECTURE-OVERVIEW.md | System components, interrupts, memory |
| 01 | BOOT-SEQUENCE.md | Boot process and initialization |
| 02 | QUEUE-STRUCTURES-DETAILED.md | Execution, time, waiting queues |
| 03 | CPU-DETECTION-AND-INITIALIZATION.md | Hardware detection |
| 04 | MMU-CONTEXT-SWITCHING.md | Memory management unit |
| 05 | ND500-DMA-KERNEL.md | ND-500 DMA operations |
| 05 | ND500-PROGRAMS-SPECIAL.md | Special ND-500 programs |
| 06 | MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md | Shared memory architecture |
| 06 | MULTIPORT-MEMORY-PART2.md | Additional 5MPM details |
| 07 | ND500-IO-AND-USER-INTERACTION.md | ND-500 user interaction |
| 08 | MESSAGE-PASSING-DETAILED.md | Inter-CPU messaging |
| 09 | ND500-CODE-LOADING.md | Loading code into ND-500 |
| 10 | ND500-STANDALONE-EMULATOR.md | Standalone ND-500 emulation |
| 11 | RT-SEGMENTS-AND-SEGFIL.md | Segment management |
| 12 | ND500-DOMAIN-SETUP-AND-MEMORY-MAPPING.md | ND-500 domain configuration |
| 13 | INT14-HANDLER-DETAILED.md | Interrupt handler (Level 14) |
| 14 | MONITOR-KERNEL-MONCALLS.md | Monitor kernel and system calls |
| 15 | DISK-IO-SUBSYSTEM.md | Disk I/O and drivers |
| 16 | PAGE-FAULT-HANDLER.md | Page fault handling |
| 17 | SCHEDULER-AND-PRIORITIES.md | Task scheduler |
| 18 | DEVICE-DRIVER-FRAMEWORK.md | Device driver architecture |
| 19 | MEMORY-MAP-REFERENCE.md | Complete memory layout |
| 20 | MPM-VS-LOCAL-MEMORY-DETECTION.md | Telling multiport memory from local memory |
| 21 | SEMAPHORES-EXPLAINED.md / SEMAPHORES-RECOVERED-CODE.md | Semaphores, with the recovered kernel code |
| 22 | READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md | Locating RT and segment tables in a live dump |
| 23 | MON-CALL-DISPATCH-DEVELOPER-GUIDE.md | How a MON call is dispatched |
| 24 | INITIAL-COMMANDS-AND-STARTUP.md | Startup and the initial command sequence |
| 25 | ND120-MICROCODE-VERSION.md | ND-120 microcode versions |
| 26 | INITIAL-COMMAND-BUFFER-ON-DISK.md | Where the initial command buffer lives on disk |

Unnumbered references in the same folder:

| Document | Topic |
|----------|-------|
| [OS/IOX-REGISTER-COMPLETE-REFERENCE.md](OS/IOX-REGISTER-COMPLETE-REFERENCE.md) | Complete IOX register map |
| [OS/SINTRAN-DEVICE-DRIVER-IOX-EXR-COMPLETE.md](OS/SINTRAN-DEVICE-DRIVER-IOX-EXR-COMPLETE.md) | Driver IOX/EXR reference |
| [OS/N500DF-STRUCTURE-COMPLETE-REFERENCE.md](OS/N500DF-STRUCTURE-COMPLETE-REFERENCE.md) | The N500DF structure |
| [OS/SEGMENTS-INTRO-AND-DEEP-DIVE.md](OS/SEGMENTS-INTRO-AND-DEEP-DIVE.md) | Segments, introduction and deep dive |
| [OS/BUS-EXPANDER-BUSC-REGISTER-REFERENCE.md](OS/BUS-EXPANDER-BUSC-REGISTER-REFERENCE.md) | Bus expander BUSC registers |
| [OS/MEMORY-TYPE-DETECTION.md](OS/MEMORY-TYPE-DETECTION.md), [OS/HOW-TO-DETECT-FIRST-2MB-AS-LOCAL-MEMORY.md](OS/HOW-TO-DETECT-FIRST-2MB-AS-LOCAL-MEMORY.md), [OS/MPM5-MEMORY-DETECTION-AND-IDENTIFICATION.md](OS/MPM5-MEMORY-DETECTION-AND-IDENTIFICATION.md) | Memory detection and identification |
| [OS/KERNEL-DOCUMENTATION-SUMMARY.md](OS/KERNEL-DOCUMENTATION-SUMMARY.md) | Summary of the kernel documentation set |

### Hardware Documentation

**MPM5 Multiport Memory:**
- [OS/MPM5-KEY-FINDINGS.md](OS/MPM5-KEY-FINDINGS.md) - Hardware details from official manual
- [OS/MPM5-DOCUMENTATION-UPDATE-SUMMARY.md](OS/MPM5-DOCUMENTATION-UPDATE-SUMMARY.md) - Documentation updates

**Device Drivers:**
- [Devices/HDLC/](Devices/HDLC/) - HDLC communication controller
- [Devices/SCSI/](Devices/SCSI/) - SCSI disk controllers

**Protocols:**
- [TAD/](TAD/) - TAD protocol analysis (X.25, HDLC encapsulation)

### Emulator Implementation

Located in [Emulator/](Emulator/) folder:

| Document | Purpose |
|----------|---------|
| KERNEL-ACCESS-EMULATOR.md | Read SINTRAN kernel structures from C# |
| ND500-EMULATION-COMPLETE.cs | Complete C# ND-500 emulation code |
| ND500-INTEGRATION-GUIDE.md | Integrate ND-500 into your emulator |
| ND500-QUICK-REFERENCE.md | Quick reference for development |
| ND500-MESSAGE-STRUCTURE-VERIFIED.md | Verified message structure |

---

## Key Concepts

### SINTRAN III Architecture

**Interrupt-Driven Design:**
- 16 interrupt levels with complete register sets
- Level 14: Internal interrupts (monitor calls, page faults)
- Level 13: Real-time clock
- Levels 10-12: Device I/O
- Level 3: Monitor kernel
- Level 1: User programs

**Virtual Memory:**
- 4 Page Index Tables (PITs) mapping 64K address space
- Demand paging (pages loaded on access)
- Ring protection (4 privilege levels)
- POF area accessible without MMU

**Queue-Driven Scheduler:**
- Execution queue: Ready-to-run programs (priority-ordered)
- Time queue: Scheduled programs (time-ordered)
- Waiting queues: Per-resource (priority-ordered)
- Monitor queue: Pending monitor activations (FIFO)

### ND-500 Integration

**Dual-CPU Architecture:**
- ND-100: 16-bit word-addressed CPU (control processor)
- ND-500: Byte-addressed CPU (computation processor)
- 5MPM (Multiport Memory): Shared physical RAM

**Communication:**
- Message passing through 5MPM
- Process descriptors in 5MPM
- TAG-IN/TAG-OUT signaling
- Interrupt-driven protocol

**Key Point:** ND-500 is **byte-oriented**, not 32-bit word! The "32-bit" refers to memory **bus width** for bandwidth optimization.

---

## Document Statistics

Measured 2026-08-17, counting every file in each folder (not only Markdown).

| Folder | Files | Size |
|--------|-------|------|
| XMSG | 4287 | 210 MB |
| ND500 | 482 | 8.6 MB |
| Devices | 177 | 30 MB |
| ND500-APPS | 75 | 40 MB |
| NPL-SOURCE | 73 | 7.7 MB |
| ND5000 | 65 | 1.5 MB |
| File-Formats | 44 | 1.1 MB |
| OS | 42 | 1.6 MB |
| Filesystem | 21 | 372 KB |
| Emulator | 16 | 412 KB |
| Print | 13 | 168 KB |
| Release-Documentation | 8 | 1.3 MB |
| TAD | 8 | 240 KB |
| SINTRAN Structures | 6 | 560 KB |
| TSS | 2 | 8.7 MB |
| **Total** | **5322** | **311 MB** |

The File-Formats row was measured again on 2026-09-18 (it grew from 16 files to 44 when the
sample files were added) and the total was adjusted by that difference. Every other row is
still the 2026-08-17 measurement.

The size columns are dominated by non-text content: XMSG carries a full C# solution,
ND500-APPS carries runnable vendor binaries, Devices carries scanned material, and TSS
is two slide-deck files.

---

## Navigation

### By Experience Level

**Beginner (Understanding SINTRAN):**
1. [OS/00-SINTRAN-ARCHITECTURE-OVERVIEW.md](OS/00-SINTRAN-ARCHITECTURE-OVERVIEW.md)
2. [OS/02-QUEUE-STRUCTURES-DETAILED.md](OS/02-QUEUE-STRUCTURES-DETAILED.md)
3. [OS/17-SCHEDULER-AND-PRIORITIES.md](OS/17-SCHEDULER-AND-PRIORITIES.md)

**Intermediate (System Details):**
1. [OS/13-INT14-HANDLER-DETAILED.md](OS/13-INT14-HANDLER-DETAILED.md)
2. [OS/14-MONITOR-KERNEL-MONCALLS.md](OS/14-MONITOR-KERNEL-MONCALLS.md)
3. [OS/15-DISK-IO-SUBSYSTEM.md](OS/15-DISK-IO-SUBSYSTEM.md)
4. [OS/18-DEVICE-DRIVER-FRAMEWORK.md](OS/18-DEVICE-DRIVER-FRAMEWORK.md)

**Advanced (ND-500 & Emulation):**
1. [OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md](OS/06-MULTIPORT-MEMORY-AND-ND500-COMMUNICATION.md)
2. [OS/12-ND500-DOMAIN-SETUP-AND-MEMORY-MAPPING.md](OS/12-ND500-DOMAIN-SETUP-AND-MEMORY-MAPPING.md)
3. [Emulator/ND500-INTEGRATION-GUIDE.md](Emulator/ND500-INTEGRATION-GUIDE.md)

### By Task

**Reading SINTRAN III Source Code:**
→ Start in [NPL-SOURCE/](NPL-SOURCE/) folder - actual kernel implementation

**Building an Emulator:**
→ Start in [Emulator/](Emulator/) folder, then cross-reference [NPL-SOURCE/](NPL-SOURCE/) and [SINTRAN Structures/](SINTRAN%20Structures/)

**Understanding Devices:**
→ See [Devices/](Devices/) folder, then check corresponding NPL files

**OS Internals:**
→ See [OS/](OS/) folder, chapters 00-19, verified against [NPL-SOURCE/](NPL-SOURCE/)

**Version-Specific Features:**
→ See [Release-Documentation/](Release-Documentation/) for feature evolution across versions J-N

**Data Structure Reference:**
→ See [SINTRAN Structures/](SINTRAN%20Structures/) for kernel structures, device numbers, and memory layouts

**Network Management:**
→ See [XMSG/](XMSG/) for the full XMSG hub (protocol, API, C# library), and
[XMSG/DOC/XMSG-COMMAND-REFERENCE.md](XMSG/DOC/XMSG-COMMAND-REFERENCE.md) for the COSMOS/XMSG operator utility

**Decoding an ND File:**
→ See [File-Formats/](File-Formats/README.md) for BRF, `:PROG`, `:NRF`, `:DOM`/`:SEG`, `:LINK`
and `DESCRIPTION-FILE:DESC` byte layouts,
[File-Formats/viewer/](File-Formats/viewer/README.md) for the drag-and-drop hex + parsed browser
viewer that reads the `.json` layouts directly, and
[File-Formats/samples/](File-Formats/samples/README.md) for the real vendor DESC and `:LINK`
files to check a parser against

**Reading a Raw Disk Image:**
→ See [Filesystem/on-disk-format/](Filesystem/on-disk-format/README.md) for the four
directory-device structures and the boot sector, all verified against real disk bytes

**Protocol Analysis:**
→ See [TAD/](TAD/) folder

---

## Related Documentation

### Developer Guides

Located in `Developer/` folder (parent directory):
- NPL-DEVELOPER-GUIDE.md - NORD PL language
- MAC-DEVELOPER-GUIDE.md - Macro assembler
- C-DEVELOPER-GUIDE.md - C compiler
- PLANC-DEVELOPER-GUIDE.md - PLAN C compiler

### External References

**Official Manuals:**
- SINTRAN III System Manuals
- ND-100 Architecture Manual
- ND-500 Architecture Manual
- MPM5 Technical Description (ND-10.004.01)

**Online Resources:**
- SINTRAN Preservation Project
- NDInsight GitHub Repository

---

## Contributing

When adding documentation:

1. **Follow existing structure** - Use numbered chapters for OS docs
2. **Use Mermaid diagrams** - Follow `../MERMAID_COLOR_STANDARDS.md`
3. **Cross-reference** - Link related documents
4. **Use relative paths** - No absolute paths (E:\, C:\, /)
5. **Add to appropriate README** - Update this file and folder READMEs

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-14 | 1.1 | Added Release-Documentation, SINTRAN Structures, XMSG reference |
| 2025-10-17 | 1.0 | Initial comprehensive SINTRAN documentation structure |

---

**For project overview, see:** [../README.md](../README.md)  
**For developer guides, see:** [../Developer/](../Developer/)

---

*This documentation preserves knowledge of the SINTRAN III operating system for emulation, study, and historical preservation.*

