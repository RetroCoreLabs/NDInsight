# RT Segments and SEGFIL - Complete Guide

**Deep Understanding of SINTRAN Segment Files and RT Program Memory**

**Version:** 1.0  
**Last Updated:** October 17, 2025  
**Purpose:** Explain how RT segments on disk map to RT processes in memory, including SEGFIL structure, memory/save/hent areas, and ND-500 communication

---

## Table of Contents

1. [Overview - The Confusion](#1-overview---the-confusion)
2. [SEGFIL - Segment Files on Disk](#2-segfil---segment-files-on-disk)
3. [The Three Areas: MEMORY, SAVE, HENT](#3-the-three-areas-memory-save-hent)
4. [RT Segments vs Segment Files](#4-rt-segments-vs-segment-files)
5. [How RT Programs Reference Segments](#5-how-rt-programs-reference-segments)
6. [RTCOMMON - Shared Memory Area](#6-rtcommon---shared-memory-area)
7. [ND-500 Communication via RT Segments](#7-nd-500-communication-via-rt-segments)
8. [Complete Disk-to-Memory Mapping](#8-complete-disk-to-memory-mapping)
9. [C# Implementation](#9-c-implementation)

---

## 1. Overview - The Confusion

### 1.1 The Problem

The manual mentions "segments" in many contexts:
- **Segment files on disk** (SEGFIL 0, 1, 2, etc.)
- **RT program segments** (referenced by RT programs)
- **Memory areas** (MEMORY, SAVE, HENT)
- **RTCOMMON** area
- **ND-500 segments** (:PSEG, :DSEG, :LINK)

**How do these relate?** Let's untangle this!

### 1.2 The Key Distinction

```mermaid
flowchart TB
    subgraph DISK [On Disk]
        SF0[SEGFIL 0 System segments]
        SF1[SEGFIL 1 User segments]
        SF2[SEGFIL 2 More segments]
        SAVE[SAVE area Boot images]
    end

    subgraph MEM [In Memory]
        SEG0[Segment 0]
        SEG1[Segment 1]
        SEG2[Segment 2]
        RTCOM[RTCOMMON Shared area]
        POF[POF area Paging off]
    end

    subgraph RT [RT Programs]
        RTP1[RT Program 1 Uses Seg 5]
        RTP2[RT Program 2 Uses Seg 6 7]
    end

    SF0 -.->|"Load on boot"| SEG0
    SF1 -.->|"Load on demand"| SEG1
    SF2 -.->|"Load on demand"| SEG2
    SAVE -.->|"HENT restart"| MEM

    SEG1 --> RTP1
    SEG2 --> RTP2
    RTCOM --> RTP1
    RTCOM --> RTP2

    style SF0 fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
    style SAVE fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
    style RTCOM fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
```

**CRITICAL INSIGHT:**
- **SEGFIL** = Files on disk containing segments (like a "segment library")
- **Segments** = blocks of code/data of up to 64KW (128KB) loaded into memory
- **RT Programs** = Reference segments by number (one global number space, see the correction in 2.3)
- **Areas** = Different regions on disk for different purposes

> **Corrections 2026-10-29.** Measured on four real packs (BIGDISK0-K-100, BIGDISK0-L2-100,
> BIGDISK0-L-SEMICS, nd100x SMD0; SINTRAN K and L), written up in
> [28-CPU-NUMBER-AND-TYPE-ON-DISK.md](28-CPU-NUMBER-AND-TYPE-ON-DISK.md) §4. Sections 2.2, 2.3,
> 2.4, 3, 4.3 and 9 of this chapter were written before those measurements and each carries a
> dated note where the measurement showed something else. The units in those notes: a **page** is
> 1024 words = 2048 bytes; a **disk block** is 512 words = 1024 bytes (`ABLPAGE` = 2 blocks per
> page on these packs). The tool that implements the corrected model is `ndtool --segments /
> --export-segment / --import-segment` in the sibling repository `norskdata-ndfs`
> (`ndfs-c/src/sintran_segments.c`).

---

## 2. SEGFIL - Segment Files on Disk

### 2.1 What is SEGFIL?

From `PH-P2-OPPSTART.NPL` line 769:
```npl
SEGFSTART=:CBLST    % START OF SEGFILE 0
```

**SEGFIL is a container file on the system disk that holds multiple segments.**

Think of it like a library or archive:

```text
 ┌────────────────────────────────────────┐
 │ SEGFIL 0 (System Segments)             │
 ├────────────────────────────────────────┤
 │ Segment 0:  Offset 0, Size 20 pages    │
 │ Segment 1:  Offset 20, Size 16 pages   │
 │ Segment 2:  Offset 36, Size 10 pages   │
 │ Segment 3:  Offset 46, Size 5 pages    │
 │ ...                                    │
 │ Segment N:  Offset X, Size Y pages     │
 └────────────────────────────────────────┘
 
 ┌────────────────────────────────────────┐
 │ SEGFIL 1 (User Segments)               │
 ├────────────────────────────────────────┤
 │ Segment 0:  User A's program           │
 │ Segment 1:  User B's program           │
 │ ...                                    │
 └────────────────────────────────────────┘
```

### 2.2 Multiple SEGFILs

SINTRAN supports **multiple SEGFIL files** (typically 0-4):

| SEGFIL | Purpose | Typical Contents |
|--------|---------|------------------|
| **0** | **System** | RT-Loader, Error handler, System monitor, Kernel segments |
| **1** | **Users** | User RT programs, Application segments |
| **2** | **Libraries** | Shared library segments |
| **3** | **ND-500** | ND-500 domains (:PSEG/:DSEG files) |
| **4** | **Special** | Additional system or user segments |

**From code (line 749):**
```npl
MASSNO(0)=:MASSNO(4)      % INITIALIZE "SEGMENT FILE" #4
```

> **Corrections 2026-10-29 (the purpose table above is UNVERIFIED and partly wrong).** No manual
> assigns a purpose to a segment file number. What the manuals say:
> - A system has **at most four** segment files, numbers **0 to 3**, named `SEGFIL0:DATA` to
>   `SEGFIL3:DATA` by convention; each is one contiguous file (`ND-60.133.02A SINTRAN III Real
>   Time Guide.md` lines 2597, 2605; `ND-30.003.007 EN SINTRAN III System Supervisor.md` line 4108).
> - Which file a new segment lands in is chosen by the RT-loader command `*SET-SEGMENT-FILE`
>   and is only fixed at `*END-LOAD` (Real Time Guide lines 2599-2601). The advice is simply
>   "Load onto SEGFIL0 until it becomes full. Then switch to SEGFIL1" (System Supervisor line
>   4137). So "1 = users, 2 = libraries" is an invention, not a rule.
> - **"3 = ND-500 domains" is wrong.** ND-500 domains are the files `:PSEG`, `:DSEG`, `:LINK`,
>   `:DESC` made by the ND-500 linkage loader ([09-ND500-CODE-LOADING.md](09-ND500-CODE-LOADING.md)
>   lines 183-186); they are not SINTRAN segments and are not in any segment file.
> - **Segment file 4 is not a user file.** It is the kernel's name for the "absolute save" area
>   (`SGFI4=100000`, FLAG bit 15, `SYMBOL-2-LIST`): `PH-P2-OPPSTART.NPL` lines 749-751 copy
>   `MASSNO(0)`/`MASSUNIT(0)` to entry 4 and set its start `BLST(11)` to
>   `ABLPAGE(0) + XXSWTYPE` blocks = **disk page 1** when `XXSWTYPE` (the Phoenix fixed-disk
>   flag, `PH-P2-START-BASE.NPL:226`) is 0. On the K pack the save copy S3SDPIT (segment 53,
>   FLAG `100111`, MADR 27) is at disk page 28 = page 27 of `(SYSTEM)SINTRAN:DATA`, which
>   occupies disk pages 1-63; `MACM-AREA:DATA` is disk pages 64-127. The K release information
>   says it: segments 52-60 and 63 are "placed on the files SINTRAN:DATA and MACM-AREA:DATA"
>   (`ND-60230-5-EN ... K-version.md` line 7941).
> - Measured on all four packs: `DBLST(1..3) = 0`, so no second, third or fourth segment file was
>   defined on any of them.

### 2.3 Segment Numbering

**Segments are numbered 0-255 within a SEGFIL.**

**Global segment reference:**
```
Segment Number = (SEGFIL_number * 256) + Local_segment_number

Examples:
  Segment 5 in SEGFIL 0  = Global segment 5
  Segment 10 in SEGFIL 1 = Global segment 266 (256 + 10)
  Segment 0 in SEGFIL 2  = Global segment 512 (256*2 + 0)
```

> **Corrections 2026-10-29 (the formula above is wrong; no source was found for it).** A
> segment number is an index into **one** segment table; there is no per-file numbering. The
> segment file a segment lives in is stored **per segment** in bits 13-15 of its FLAG word
> (`IP-P2-SEGADM.NPL` RWSEGM line 1532 "SEGMENT FILE NO. IS IN TOP OF FLAG", line 1533
> `A SHZ -15`). The manual gives the number range as 0-376B (`Real Time Guide` line 2327, an
> older limit); the live L07 system has `SGMAX = 3261B` = 1713 slots
> ([22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md](22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md)
> §3.1), and the system-included segments 2-127B are all in segment file 0 except the K save
> set in file 4 (section 2.2 note). None of that fits "256 per file". The same formula is
> repeated in `SINTRAN/OS/README.md` line 704 and in
> [SEGMENTS-INTRO-AND-DEEP-DIVE.md](SEGMENTS-INTRO-AND-DEEP-DIVE.md) §8.1 (corrected there too).

### 2.4 Segment Table

SINTRAN maintains a **Segment Table** (SGT) in memory:

```
┌──────────────────────────────────────┐
│ Segment Table Entry (per segment)    │
├──────────────────────────────────────┤
│ SEGFIL number (which file?)          │ 16 bits
│ Offset in SEGFIL (pages)             │ 16 bits
│ Length (pages)                       │ 16 bits
│ Status flags                         │ 16 bits
│ Physical page (if loaded)            │ 16 bits
│ Reference count                      │ 16 bits
└──────────────────────────────────────┘
```

**From code (line 784):**
```npl
X:=CBLST; T:="MSSGT"+X; A:="MISGT"+X
X:="LSSGT"; CALL FAR CRWDISC    % COPY SEGMENT TABLE
```

> **Corrections 2026-10-29 (the entry drawing above is wrong).** The real entry is **8 words**,
> with these symbols and units (`SYMBOL-1-LIST` K03 lines 349-356, identical in L07 and M06;
> chapter 22 §3.3; read off the packs in chapter 28 §4.1):
>
> | Word | Symbol | Meaning | Unit |
> |---|---|---|---|
> | 0 | `SEGLI` | forward LRU link | segment-table address |
> | 1 | `PRESE` | backward LRU link | segment-table address |
> | 2 | `LOGAD` | logical base page; low 6 bits = page within the 64KW bank | 1024-word pages |
> | 3 | `SEGLE` | length, low 10 bits | 1024-word pages |
> | 4 | `MADR` | offset of the segment inside its segment file | 1024-word pages |
> | 5 | `FLAG` | bits 13-15 = segment file number; bit 0 = `5OK`; bit 15 alone = `SGFI4` | - |
> | 6 | `SGSTA` | protection / ring | - |
> | 7 | `BPAGL` | core-map head (0 = not in memory) | core-map address |
>
> There is no "SEGFIL number" word, no "physical page" word and no "reference count" word.
>
> **Where the table is.** In memory at `(SEGTB << 16) + SEGST` (chapter 22 §3.2). On disk it is
> itself a segment inside `(SYSTEM)SEGFIL0:DATA` (`S3ISGT` image, `S3SSGT` save), found offline
> with the self-validating scan of [26-INITIAL-COMMAND-BUFFER-ON-DISK.md](26-INITIAL-COMMAND-BUFFER-ON-DISK.md)
> §3.2: page **461** of `SEGFIL0:DATA` on the K pack, **1275** on the L packs (measured).
>
> **Where a segment's page is on disk.** From `IP-P2-SEGADM.NPL` RWSEGM lines 1532-1540 and
> 1576-1583: segment file `N = FLAG >> 13`; `DBLST(N)` is the file's start address in **disk
> blocks** (a double word, "DISK ADDRESS FOR THIS SEGMENT FILE"); `ABLPAGE(N)` is "NUMBER OF
> DISK BLOCKS PER PAGE"; `MASSNO(N)` is the logical device of the disk holding the file (line
> 1555). The block address of page `P` of the segment is `DBLST(N) + (MADR + P) * ABLPAGE(N)`, so
> in pages:
>
> ```
> disk page = DBLST(N) / ABLPAGE(N) + MADR + P
> ```
>
> The three tables live in the resident data page (`BLST=004023`, `ABLPA=004461` L07/M06 and
> `004451` K03, `MASSN=004441` L07/M06 and `004431` K03, from the `SYMBOL-1-LIST` files) and are
> read offline from the S3IDPIT copy (segment 44) in `SEGFIL0:DATA`. **Measured on the K and L
> packs:** `DBLST(0) = 256` blocks, `ABLPAGE(0) = 2` blocks per page, so `SEGFIL0` starts at
> **disk page 128**, which is exactly the first page of the contiguous file
> `(SYSTEM)SEGFIL0:DATA` on every pack. `PH-P2-OPPSTART.NPL` line 746 computes the same:
> `A*200+XXSWTYPE=:BLST(1)` with `A = ABLPAGE(0)`, "SET START OF SEGFIL0 IN SECTORS".
> Cross-check: S3IDPIT on the L packs has MADR 1019 and its words `SYSNO` etc. are found at byte
> `1019 * 2048` of `SEGFIL0:DATA`, so MADR counts 1024-word pages, not 512-word blocks.

---

## 3. The Three Areas: MEMORY, SAVE, HENT

### 3.1 Overview

The boot code copies segments from **SAVE area** to different locations:

```
Disk Layout:
┌─────────────────────────────────────────┐
│ System Disk                             │
├─────────────────────────────────────────┤
│ Page 0:     Boot sector                 │
│ Pages 1-N:  SEGFIL 0 (IMAGE area)       │
│ Pages M-P:  SAVE area                   │
│ Pages Q-R:  HENT restart image          │
│ Pages S-T:  Swap area                   │
└─────────────────────────────────────────┘
```

> **Corrections 2026-10-29 (the layout above is a sketch, not a measurement).** The measured
> layout of the K and L packs (disk pages of 1024 words): page 0 = directory page 0 / boot;
> pages **1-63** `(SYSTEM)SINTRAN:DATA`; pages **64-127** `(SYSTEM)MACM-AREA:DATA`; page **128**
> onwards `(SYSTEM)SEGFIL0:DATA` (`DBLST(0) = 256` blocks / 2 blocks per page). There is no
> separate "SAVE area" and no separate "HENT area" as disk regions: the save copies are ordinary
> segments (S3SDPIT 53, S3SSGT 24, ...) that sit in `SEGFIL0:DATA` on the L packs and, for
> segments 52-60 and 63 on K, in `SINTRAN:DATA` / `MACM-AREA:DATA` as "segment file 4" (section
> 2.2 note). The "swap area" is the segment files themselves (`MASSNO(0)` is "LOGICAL DEV.NO.
> OF MAIN-SWAP-DEVICE", `PH-P2-OPPSTART.NPL:741`).

### 3.2 IMAGE Area (MEMORY)

**Purpose:** The "live" segments used during normal operation.

**Location:** Part of SEGFIL 0, starts at `SEGFSTART`

**Contents:**
- All currently active segments
- Modified by system and RT programs
- Survives normal shutdown (but not power loss)

**From code (line 772):**
```npl
% COPY FROM SAVE TO IMAGE
X:=CBLST; T:="MSECO"+X; A:="MIECO"+X
X:="LSECO"; CALL FAR CRWDISC    % COPY EXT. COMMON
```

### 3.3 SAVE Area

**Purpose:** **Clean backup copy** of system segments.

**Location:** Separate area on disk (disk pages defined at system generation)

**Contents:**
- Pristine copy of all system segments
- **NEVER modified during operation**
- Used to restore IMAGE area during boot

**Symbol definitions (from code lines 773-841):**
- `MSECO` = Memory Save Extended COmmon
- `MSDPT` = Memory Save DPIT
- `MSRPT` = Memory Save RPIT
- `MSMPT` = Memory Save MPIT
- `MSIPT` = Memory Save IPIT
- `MSSGT` = Memory Save SeGment Table
- `MFILS` = Memory Save FILe System
- `MRTLO` = Memory RT-LOader
- `MERRP` = Memory ERRor Program
- `MSCOM` = Memory Save COMmand segment
- (many more...)

### 3.4 HENT Restart Area

**Purpose:** **Complete memory snapshot** for fast restart after HENT (halt/restart).

**Location:** Another area on disk

**How it works:**
1. **@HENT command** (halt system):
   - Saves ENTIRE memory contents to HENT area
   - Includes all PITs, segment tables, datafields, RT program states
   - Essentially a "memory dump"

2. **On restart:**
   - Check `HENTFLAG` (line 766, 771)
   - If HENT restart: Copy HENT area back to memory
   - If cold start: Copy SAVE area to IMAGE area

**From code (line 771):**
```npl
IF HENTFLAG><0 GO FAR OVCO    % HENT restart - skip SAVE copy
```

> **Corrections 2026-10-29 (the "HENT area = complete memory snapshot" claim is UNVERIFIED;
> the code read shows something simpler).** `PH-P2-OPPSTART.NPL` line 262 defines
> `DPSA:=MSDPT, DPIM:=MIDPT` (disk addresses of the **save** and **image** copies of the resident
> data page) and lines 283-284 read the data page from the **save** copy when `HENTFLAG=0` and
> from the **image** copy otherwise; lines 771-776 copy save → image only when `HENTFLAG=0`. So
> a warm start (`HENTFLAG><0`) reads the **image** segments, which are the normal running
> copies in `SEGFIL0:DATA`; no third "HENT area" appears in this code. The three copies of the
> resident data page are the segments **23 S3DPIT** (live, memory only: MADR 0), **44 S3IDPIT**
> (image, warm start) and **53 S3SDPIT** (save, cold start) - listed in
> `ND-820023-1-EN SINTRAN III-VSX System Documentation.md` lines 837, 854 (misprinted
> "S3DIPIT") and 861; measured on every pack in chapter 28 §4.1. **Also the naming:** the MACM
> command `)HENT` is "GET SINTRAN FROM SAVE-AREA" (`ND-30.003.007 EN SINTRAN III System
> Supervisor.md` lines 3982, 4920), so HENT is the **cold** start (`HENTFLAG=0`), not a warm
> "HENT restart" as this section says. Where `HENTFLAG` is set was not found; the available NPL
> only reads it.

### 3.5 The Complete Picture

```mermaid
flowchart LR
    subgraph COLD [Cold Start Power On]
        S1[SAVE area Clean backup]
        I1[IMAGE area SEGFIL 0]
        M1[Memory Segments loaded]
    end

    subgraph HENT [HENT Restart Warm]
        H1[HENT area Memory snapshot]
        M2[Memory Exact restore]
    end

    S1 -->|Copy| I1
    I1 -->|"Load on demand"| M1
    H1 -->|"Bulk copy"| M2

    style S1 fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
    style H1 fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
```

**Why three areas?**
- **IMAGE**: Fast access, modified during operation
- **SAVE**: Pristine backup, never modified
- **HENT**: Fast restart, complete state

---

## 4. RT Segments vs Segment Files

### 4.1 The Relationship

**An RT Program references segments by number.**

**Example RT program structure:**
```
RT Program "TERMINAL-HANDLER":
  Program Segment:  Uses segment 5 (code)
  Data Segment:     Uses segment 6 (data)
  Stack:            In data segment or separate
```

**That segment number points into the Segment Table:**
```
Segment 5:
  SEGFIL: 0
  Offset: 100 pages into SEGFIL 0
  Length: 20 pages
  Status: Loaded
  Physical: Pages 150-169 in RAM
```

### 4.2 Segment Loading Process

```mermaid
sequenceDiagram
    participant RTP as RT Program
    participant SINT as SINTRAN
    participant SGT as Segment Table
    participant SEGF as SEGFIL on Disk
    participant MEM as Physical Memory

    RTP->>SINT: Access segment 5
    SINT->>SGT: Lookup segment 5
    SGT-->>SINT: SEGFIL 0 offset 100 len 20

    alt Segment not loaded
        SINT->>MEM: Allocate 20 pages
        SINT->>SEGF: Read pages 100 to 119
        SEGF-->>MEM: Copy data
        SINT->>SGT: Update loaded at pages 150 to 169
    else Segment already loaded
        SINT->>SGT: Increment ref count
    end

    SINT-->>RTP: Physical address 150 times 4096
```

### 4.3 Segment Naming

**Segments can have names:**
- Name stored in Segment Table
- Maps name → segment number
- Example: "RT-LOADER" = segment 4

> **Corrections 2026-10-29 (names are NOT in the segment table).** The 8-word entry has no
> name field (section 2.4 note), and the names are in no symbol list either (chapter 22 §6.4).
> A segment name is a **"DEFINED SEGMENT NAME" record of the RT-loader** (symbol type 25B),
> 8 words: words 0-2 the packed name (SIXBIT = ASCII & 0x3F, right-justified base 64, up to 8
> characters), word 3 = segment number, word 4 = 0, word 5 = 25B, word 6 = segment number,
> word 7 = 0 (decoded in chapter 22 §6.5). The records are on disk in the plain file
> `(SYSTEM)RTFIL:DATA` and again inside `SEGFIL0:DATA` (the S3RTFIL segment, 10B), so they can
> be read offline without booting. **Measured 2026-10-29:** 74 names on the K pack, 98 on the L
> packs; on every pack they decode to S3IMAGE 2, S3RTFIL 10, S3DPIT 23, S3SSGT 24, S3ISGT 27,
> S3PATCH 43, S3IDPIT 44, S3SDPIT 53 (octal). The real names are of the form `S3xxxx`; "RT-LOADER
> = segment 4" is the manual's description of segment 4 (`S3RTL`), not its name, and the table
> below pairs MACM disk-address symbols (`S04MA`, `MICOM`, ...) with invented names - treat its
> name column as UNVERIFIED.

**From code (lines 787-841), system segments:**
```
Segment Name         Code     Purpose
────────────────────────────────────────────────
RT-LOADER (prog)     S04MA    RT program loader
RT-LOADER (data)     S37MA    RT loader data
ERROR-PROGRAM        S14MA    Error handler
EDIT-ROUTINE         S41MA    Command editor
COMMAND              MICOM    Command processor
SM-SEGMENT           MISMS    System Monitor
SYSTEM-SEGMENT-5     S05MA    System utilities
5PIT-SEGMENT         MI5PT    ND-500 PIT area
XMSG-KERNEL          MIXMK    ND-500 message kernel
NK-SERV              MINKS    Network service
NK-NAME              MINKN    Network naming
ERSWD-CODE           MIERC    Error code
ND-500-MONITOR       MI5MO    ND-500 system monitor
```

---

## 5. How RT Programs Reference Segments

### 5.1 RT Program Structure

An RT program consists of:

```
┌─────────────────────────────────────┐
│ RT-Description (26 words)           │
├─────────────────────────────────────┤
│ TLINK, STATE, PRIORITY, DTIME, ...  │
│ STADR ← Start address               │
│ SEGM  ← Program segment number      │ 16 bits
│ SEGM2 ← Data segment number         │ 16 bits
│ Saved registers (P, X, T, A, D, L...) │
│ ACTPRI ← PCR value (MMU config)     │
│ RSEGM ← Reentrant segment bitmap    │
└─────────────────────────────────────┘
```

**Key fields:**
- **SEGM** (offset 10): Program segment number (0-255)
- **SEGM2** (offset 11): Data segment number (0-255)
- **RSEGM** (offset 23): Bitmap of additional segments (up to 16 more)

### 5.2 Multi-Segment RT Programs

An RT program can use **multiple segments:**

```
RT Program "DATABASE-SERVER":
  Segment 10: Main program code
  Segment 11: Data area
  Segment 12: Shared library (reentrant)
  Segment 13: Communication buffer
  Segment 14: Index tables
```

**RSEGM bitmap** (offset 23-25):
```
Bits 0-15  (RSEGM):   Segments 0-15  used/not used
Bits 16-31 (BITM1):   Segments 16-31 used/not used
Bits 32-47 (BITM2):   Segments 32-47 used/not used
```

### 5.3 Segment Loading on RT Activation

**When RT program is activated:**

1. **SINTRAN reads RT-Description**
2. **Loads program segment** (SEGM field)
   - Lookup in Segment Table
   - Load from SEGFIL if not in memory
   - Set up MMU to map segment
3. **Loads data segment** (SEGM2 field)
4. **Loads additional segments** (RSEGM bitmap)
5. **Sets ACTPRI** (PCR value for MMU)
6. **Starts execution** at STADR

---

## 6. RTCOMMON - Shared Memory Area

### 6.1 What is RTCOMMON?

**RTCOMMON** = **RT COMMON area** = Shared memory accessible by ALL RT programs and ND-500 processes.

**Purpose:**
- Fast inter-process communication
- Shared data structures
- ND-500 ↔ ND-100 communication
- Always resident in physical memory (never swapped)

**From code (lines 625-645):**
```npl
% SET UP RT-COMMON TABLE
IF CCNOX><0 THEN    % Number of pages in RT-COMMON
   ...
   200-CCNOX+161000; T:=CCNOX; X:=0  % First logical page of RT-COMMON
   DO WHILE T><0
      AD=:DCCTAB(X); A+1; D+1; X+2; T-1  % Fill log.page and phys.page
   OD; -1=:ACCTAB(X)    % -1 is end of table
FI
```

### 6.2 RTCOMMON Layout

```text
Logical Address Space:
┌─────────────────────────────────────┐
│ Pages 0-127:  Normal memory         │
├─────────────────────────────────────┤
│ Pages 128-159: RTCOMMON             │ ← 32 pages typical
│                Fixed physical addr  │
│                Contiguous           │
│                Shared by all RT     │
├─────────────────────────────────────┤
│ Pages 160-199: Other memory         │
│ Page  200:     Start of RT segments │
└─────────────────────────────────────┘

Physical Memory:
┌─────────────────────────────────────┐
│ Pages 0-63:   POF area              │
├─────────────────────────────────────┤
│ Pages 64-95:  RTCOMMON              │ ← Fixed location
│               CCSTART = 64          │
├─────────────────────────────────────┤
│ Pages 96-...: Other memory          │
└─────────────────────────────────────┘
```

### 6.3 RTCOMMON for ND-500

**From documentation:**
> The RTCOMMON area is accessed from the ND-500 as a part of the regular memory space. The mapping onto the RTCOMMON is done at load time through the **MATCH-RTCOMMON** command.

**How it works:**

1. **ND-500 domain created** with loader command:
   ```
   NLL: SET-DOMAIN "MY-500-PROG"
   NLL: MATCH-RTCOMMON    ← Maps ND-500 segment to RTCOMMON
   NLL: LOAD-SEGMENT MY-CODE
   ```

2. **At load time:**
   - ND-500 segment (e.g., segment 0) is mapped to RTCOMMON physical pages
   - ND-500 can read/write directly to RTCOMMON
   - ND-100 RT programs also access same physical pages

3. **Result:**
   - Shared memory between ND-100 and ND-500
   - No message passing overhead
   - Direct read/write access
   - **Must be contiguous** (for ND-500 DMA)

**Critical constraint:**
> If the RTCOMMON area is used from ND-500, it must be contiguous. In other words, if the system supervisor through the SINTRAN-SERVICE-PROGRAM command DEFINE-RTCOMMON-SIZE expands RTCOMMON beyond what was specified at system generation, this area must be adjacent to the initially allocated area.

---

## 7. ND-500 Communication via RT Segments

### 7.1 MATCH-COMMON-RT-SEGMENT

**From documentation:**
> An ND-100 RT-program may share data with an ND-500 process through a segment in one of the ND-100 SEGFILs. The segment must be **fixed in a continuous area in memory** before the ND-500 process referring to it is started.

**How it works:**

```mermaid
flowchart TB
    subgraph ND100 [ND100 Side]
        RTP[RT Program Segment 10]
        SEG10[Segment 10 in SEGFIL 1]
        PHYS[Physical Pages 200 to 219]
    end

    subgraph ND500 [ND500 Side]
        DOMAIN[ND500 Domain]
        SEG1[Segment 1]
        FIX[Fixed Pages 200 to 219]
    end

    SEG10 -->|Loaded| PHYS
    SEG1 -->|Mapped| FIX
    PHYS -.->|"Same physical memory"| FIX
    RTP -->|Uses| SEG10
    DOMAIN -->|Uses| SEG1

    style PHYS fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
    style FIX fill:#009688,stroke:#00695C,stroke-width:2px,color:#fff
```

### 7.2 Setup Process

**Step 1: ND-100 RT Program loads segment:**
```
@RT-LOADER
RT: LOAD MY-RT-PROG
(Loads segment 10 from SEGFIL 1)
```

**Step 2: Fix segment in memory:**
```
@FIX-SEGMENT 10, START-ADDRESS=0x32000
(Segment 10 fixed at physical address 0x32000-0x37FFF)
```

**Step 3: ND-500 domain setup:**
```
@ND-500 LINKAGE-LOADER
NLL: SET-DOMAIN "SHARED-DOMAIN"
NLL: MATCH-COMMON-RT-SEGMENT 10    ← Links to ND-100 segment 10
NLL: OPEN-SEGMENT "MY-CODE", P
NLL: LOAD-SEGMENT MY-CODE-FILE
NLL: EXIT
```

**Step 4: ND-500 execution:**
- ND-500 segment 1 maps to same physical pages as ND-100 segment 10
- Both CPUs see same memory
- **Synchronization required** (semaphores, flags)

### 7.3 Communication Methods Compared

| Method | Speed | Size Limit | Setup Complexity | Use Case |
|--------|-------|------------|------------------|----------|
| **Process Flags** | Fastest | 16 bits | Very simple | Simple signaling |
| **RTCOMMON** | Very fast | ~128KB | Simple | Moderate data, many processes |
| **RT Segment** | Fast | Up to 64KB per segment | Moderate | Large data transfers |
| **Files** | Slowest | Unlimited | Simple | Very large data, not time-critical |
| **Messages (5MPM)** | Moderate | Variable | Complex | Structured I/O requests |

---

## 8. Complete Disk-to-Memory Mapping

### 8.1 Boot Sequence Segment Loading

**From `PH-P2-OPPSTART.NPL` lines 772-841:**

```
Cold Start (HENTFLAG=0):
┌────────────────────────────────────────┐
│ 1. Copy from SAVE to IMAGE on disk     │
├────────────────────────────────────────┤
│ Extended Common    (MSECO → MIECO)     │
│ DPIT               (MSDPT → MIDPT)     │
│ RPIT               (MSRPT → MIRPT)     │
│ MPIT               (MSMPT → MIMPT)     │
│ IPIT               (MSIPT → MIIPT)     │
│ Segment Table      (MSSGT → MISGT)     │
│ File System        (MFILS → MIFIL)     │
│ RT-Loader Program  (MRTLO → S04MA)     │
│ RT-Loader Data     (MRTLO+20 → S37MA)  │
│ Error Program      (MERRP → S14MA)     │
│ Command Segment    (MSCOM → MICOM)     │
│ System Monitor     (MSSMS → MISMS)     │
│ System Segment 5   (MSSYS → S05MA)     │
│ 5PIT Segment       (MS5PT → MI5PT)     │
│ XMSG Kernel        (MSXMK → MIXMK)     │
│ ND-500 Monitor     (MN5MO → MI5MO)     │
│ (many more...)                         │
└────────────────────────────────────────┘

Warm Start (HENTFLAG<>0):
┌────────────────────────────────────────┐
│ Copy HENT area → Memory (bulk copy)    │
│ Much faster than cold start            │
│ Exact memory state restored            │
└────────────────────────────────────────┘
```

### 8.2 Complete Memory Map

```
Logical Address Space (16-bit addressing):
┌────────────────────────────────────────┐ 0x0000
│ Page 0-63:    POF area                 │
│               (Paging Off - no MMU)    │
│               System datafields        │
│               RT-Description table     │
│               Critical kernel code     │
├────────────────────────────────────────┤ 0x10000 (page 64)
│ Page 64-95:   RTCOMMON                 │
│               (Fixed, contiguous)      │
│               Shared by all RT progs   │
├────────────────────────────────────────┤ 0x18000 (page 96)
│ Page 96-127:  Extended Common          │
│               Additional shared area   │
├────────────────────────────────────────┤ 0x20000 (page 128)
│ Page 128-199: System segments          │
│               Segment 0-15 mapped here │
├────────────────────────────────────────┤ 0x32000 (page 200)
│ Page 200-255: User segments            │
│               RT program segments      │
│               Dynamically loaded       │
└────────────────────────────────────────┘ 0x40000 (page 256)

Physical Memory (24-bit addressing):
┌────────────────────────────────────────┐ 0x000000
│ Pages 0-63:    POF area                │
│                Direct mapping          │
├────────────────────────────────────────┤ 0x040000
│ Pages 64-95:   RTCOMMON                │
│                Fixed location          │
├────────────────────────────────────────┤ 0x060000
│ Pages 96-...:  Dynamic segments        │
│                Loaded on demand        │
│                May be anywhere in RAM  │
├────────────────────────────────────────┤
│ ...                                    │
├────────────────────────────────────────┤
│ Top of memory: ND-500 multiport (5MPM) │
│                (if ND-500 present)     │
└────────────────────────────────────────┘ 0xFFFFFF
```

### 8.3 Segment Reference Example

**Example: RT Program needs segment 10**

```
Step 1: RT Program starts
  - RT-Description says SEGM = 10

Step 2: SINTRAN looks up segment 10
  - Segment Table Entry 10:
    SEGFIL:  1
    Offset:  50 pages into SEGFIL 1
    Length:  8 pages
    Status:  Not loaded
    
Step 3: SINTRAN loads segment
  - Allocate 8 physical pages (say, pages 150-157)
  - Read from disk:
    SEGFIL 1 offset 50 → Read 8 pages
  - Copy to physical pages 150-157
  - Update Segment Table Entry 10:
    Status: Loaded
    Physical: 150
    
Step 4: SINTRAN sets up MMU
  - RT program's PIT (Page Index Table):
    Logical page 200 → Physical page 150
    Logical page 201 → Physical page 151
    ...
    Logical page 207 → Physical page 157
    
Step 5: RT Program executes
  - Accesses logical address 0x32000 (page 200)
  - MMU translates: page 200 → physical page 150
  - Physical address: 0x96000
  - Data read/written from physical pages 150-157
```

---

## 9. C# Implementation

> **Corrections 2026-10-29.** The classes below are a design sketch written before the
> on-disk layout was measured, and they disagree with it in four places: the entry is 8 words
> (not "12 bytes, estimated"), there is no reference count or physical-page word, blocks per
> page come from the kernel table `ABLPAGE(N)` (2 on the measured packs, not 8), and the file
> base comes from `DBLST(N)` in blocks (256 for `SEGFIL0` on the measured packs). Use the
> formula in the section 2.4 note; a working implementation is `ndfs-c/src/sintran_segments.c`
> in the sibling repository `norskdata-ndfs`. The code is kept as the author wrote it.

### 9.1 Segment Table Entry

```csharp
/// <summary>
/// Entry in SINTRAN Segment Table.
/// One entry per segment (0-255 per SEGFIL).
/// </summary>
public class SegmentTableEntry
{
    public byte SegmentNumber { get; set; }        // 0-255
    public byte SegfilNumber { get; set; }         // Which SEGFIL (0-4)
    public ushort OffsetInSegfil { get; set; }     // Offset in pages
    public ushort LengthPages { get; set; }        // Size in pages (1 page = 1024 words = 2048 bytes)
    public SegmentStatus Status { get; set; }
    public ushort PhysicalPage { get; set; }       // If loaded, first physical page
    public ushort ReferenceCount { get; set; }     // How many RT programs using it
    public string SegmentName { get; set; }        // Optional name
    public SegmentFlags Flags { get; set; }
    
    public uint DiskAddress => (uint)(OffsetInSegfil * 8);  // Convert pages to sectors (8 sectors/page)
    public uint SizeBytes => (uint)(LengthPages * 2048);
    public bool IsLoaded => Status == SegmentStatus.Loaded;
}

public enum SegmentStatus : byte
{
    NotLoaded = 0,
    Loading = 1,
    Loaded = 2,
    Error = 3
}

[Flags]
public enum SegmentFlags : ushort
{
    None = 0,
    Reentrant = 0x0001,      // Multiple progs can share
    System = 0x0002,         // System segment
    User = 0x0004,           // User segment
    FixedInMemory = 0x0008,  // Never swapped
    ReadOnly = 0x0010,       // Code segment
    ReadWrite = 0x0020       // Data segment
}
```

### 9.2 SEGFIL Manager

```csharp
/// <summary>
/// Manages SEGFIL files on disk and segment loading.
/// </summary>
public class SegfilManager
{
    private readonly DiskAccess _disk;
    private readonly MemoryAccess _memory;
    private readonly SegmentTableEntry[] _segmentTable;  // Up to 256 * 5 = 1280 segments
    private readonly Dictionary<byte, uint> _segfilStartSectors;  // SEGFIL start addresses
    
    public SegfilManager(DiskAccess disk, MemoryAccess memory)
    {
        _disk = disk;
        _memory = memory;
        _segmentTable = new SegmentTableEntry[1280];
        _segfilStartSectors = new Dictionary<byte, uint>();
    }
    
    /// <summary>
    /// Initialize SEGFIL start addresses from boot data.
    /// </summary>
    public void InitializeSegfils(uint segfil0Start, uint segfil1Start, uint segfil2Start)
    {
        _segfilStartSectors[0] = segfil0Start;  // CBLST from NPL code
        _segfilStartSectors[1] = segfil1Start;
        _segfilStartSectors[2] = segfil2Start;
        // SEGFIL 3, 4 if present
    }
    
    /// <summary>
    /// Load segment table from disk.
    /// </summary>
    public void LoadSegmentTable()
    {
        // Segment table is stored in SEGFIL 0 at known location
        // (MSSGT/MISGT in code)
        
        uint segTableSector = _segfilStartSectors[0] + /* offset to SGT */;
        byte[] segTableData = _disk.ReadSectors(segTableSector, 32);  // Read segment table
        
        // Parse segment table
        for (int i = 0; i < 256; i++)
        {
            int offset = i * 12;  // 12 bytes per entry (estimated)
            
            var entry = new SegmentTableEntry
            {
                SegmentNumber = (byte)i,
                SegfilNumber = segTableData[offset],
                OffsetInSegfil = BitConverter.ToUInt16(segTableData, offset + 1),
                LengthPages = BitConverter.ToUInt16(segTableData, offset + 3),
                Status = (SegmentStatus)segTableData[offset + 5],
                PhysicalPage = BitConverter.ToUInt16(segTableData, offset + 6),
                ReferenceCount = BitConverter.ToUInt16(segTableData, offset + 8),
                Flags = (SegmentFlags)BitConverter.ToUInt16(segTableData, offset + 10)
            };
            
            _segmentTable[i] = entry;
        }
    }
    
    /// <summary>
    /// Load a segment from SEGFIL into memory.
    /// </summary>
    public void LoadSegment(byte segmentNumber)
    {
        var entry = _segmentTable[segmentNumber];
        
        if (entry == null)
            throw new Exception($"Segment {segmentNumber} not defined");
        
        if (entry.IsLoaded)
        {
            entry.ReferenceCount++;
            return;  // Already loaded
        }
        
        // Calculate disk address
        uint segfilStart = _segfilStartSectors[entry.SegfilNumber];
        uint segmentSector = segfilStart + (uint)(entry.OffsetInSegfil * 8);
        uint sectorsToRead = (uint)(entry.LengthPages * 8);
        
        // Allocate physical pages
        ushort physPage = AllocatePhysicalPages(entry.LengthPages);
        
        // Read from disk
        byte[] segmentData = _disk.ReadSectors(segmentSector, sectorsToRead);
        
        // Write to memory
        uint physAddr = (uint)(physPage * 2048);  // Page size = 2048 bytes
        _memory.WriteBytes(physAddr, segmentData);
        
        // Update segment table
        entry.Status = SegmentStatus.Loaded;
        entry.PhysicalPage = physPage;
        entry.ReferenceCount = 1;
        
        Console.WriteLine($"Loaded segment {segmentNumber} from SEGFIL {entry.SegfilNumber} " +
                          $"at physical page {physPage}");
    }
    
    /// <summary>
    /// Unload a segment (decrement ref count, free if zero).
    /// </summary>
    public void UnloadSegment(byte segmentNumber)
    {
        var entry = _segmentTable[segmentNumber];
        
        if (entry == null || !entry.IsLoaded)
            return;
        
        entry.ReferenceCount--;
        
        if (entry.ReferenceCount == 0 && !entry.Flags.HasFlag(SegmentFlags.FixedInMemory))
        {
            // Free physical pages
            FreePhysicalPages(entry.PhysicalPage, entry.LengthPages);
            entry.Status = SegmentStatus.NotLoaded;
            entry.PhysicalPage = 0;
            
            Console.WriteLine($"Unloaded segment {segmentNumber}");
        }
    }
    
    /// <summary>
    /// Get physical address of segment.
    /// </summary>
    public uint GetSegmentPhysicalAddress(byte segmentNumber)
    {
        var entry = _segmentTable[segmentNumber];
        
        if (entry == null || !entry.IsLoaded)
            throw new Exception($"Segment {segmentNumber} not loaded");
        
        return (uint)(entry.PhysicalPage * 2048);
    }
    
    private ushort _nextPhysPage = 96;  // Start after RTCOMMON
    private readonly Dictionary<ushort, bool> _freePages = new Dictionary<ushort, bool>();
    
    private ushort AllocatePhysicalPages(ushort count)
    {
        // Try to find free pages first
        ushort consecutive = 0;
        ushort startPage = 0;
        
        for (ushort page = 96; page < 256; page++)
        {
            if (_freePages.TryGetValue(page, out bool isFree) && isFree)
            {
                if (consecutive == 0) startPage = page;
                consecutive++;
                if (consecutive == count)
                {
                    // Mark pages as allocated
                    for (ushort p = startPage; p < startPage + count; p++)
                        _freePages[p] = false;
                    return startPage;
                }
            }
            else
            {
                consecutive = 0;
            }
        }
        
        // No free pages found, allocate new ones
        ushort result = _nextPhysPage;
        _nextPhysPage += count;
        
        // Mark as allocated
        for (ushort p = result; p < result + count; p++)
            _freePages[p] = false;
            
        return result;
    }
    
    private void FreePhysicalPages(ushort start, ushort count)
    {
        // Mark pages as free for reuse
        for (ushort page = start; page < start + count; page++)
        {
            _freePages[page] = true;
        }
        
        Log($"Freed {count} pages starting at physical page {start}");
    }
}
```

### 9.3 RT Program Segment Loader

```csharp
/// <summary>
/// Loads segments for an RT program and sets up MMU.
/// </summary>
public class RtProgramSegmentLoader
{
    private readonly SegfilManager _segfilManager;
    private readonly MmuManager _mmuManager;
    
    public void LoadRtProgramSegments(RtDescription rtDesc)
    {
        // Load program segment
        byte progSeg = (byte)(rtDesc.SEGM & 0xFF);
        _segfilManager.LoadSegment(progSeg);
        
        // Load data segment
        byte dataSeg = (byte)(rtDesc.SEGM2 & 0xFF);
        _segfilManager.LoadSegment(dataSeg);
        
        // Load additional segments from RSEGM bitmap
        ushort rsegm = rtDesc.RSEGM;
        for (int bit = 0; bit < 16; bit++)
        {
            if ((rsegm & (1 << bit)) != 0)
            {
                byte additionalSeg = (byte)bit;
                _segfilManager.LoadSegment(additionalSeg);
            }
        }
        
        // Set up MMU for this RT program
        SetupMmuForRtProgram(rtDesc);
    }
    
    private void SetupMmuForRtProgram(RtDescription rtDesc)
    {
        byte progSeg = (byte)(rtDesc.SEGM & 0xFF);
        byte dataSeg = (byte)(rtDesc.SEGM2 & 0xFF);
        
        // Get physical addresses
        uint progPhysAddr = _segfilManager.GetSegmentPhysicalAddress(progSeg);
        uint dataPhysAddr = _segfilManager.GetSegmentPhysicalAddress(dataSeg);
        
        // Map logical pages 200-207 (typical RT program area) to physical
        // This is simplified - real mapping depends on segment sizes
        ushort progPhysPage = (ushort)(progPhysAddr / 2048);
        ushort dataPhysPage = (ushort)(dataPhysAddr / 2048);
        
        _mmuManager.MapPages(200, progPhysPage, 8);  // Map 8 pages for program
        _mmuManager.MapPages(208, dataPhysPage, 8);  // Map 8 pages for data
    }
}
```

---

## Summary

**The complete picture:**

1. **SEGFIL** = Container files on disk holding multiple segments (at most four, 0-3; "file 4" is the kernel's absolute-save area - section 2.2 note)
2. **SAVE area** = Pristine backup of system segments (ordinary segments: in `SEGFIL0:DATA` on L, in `SINTRAN:DATA`/`MACM-AREA:DATA` on K - section 3 notes)
3. **IMAGE area** = Live SEGFIL 0 used during operation
4. **HENT area** = Complete memory snapshot for fast restart (UNVERIFIED; the code reads the image copies on a warm start - section 3.4 note)
5. **Segment Table** = Maps segment numbers → SEGFIL locations (8-word entries, MADR in 1024-word pages - section 2.4 note)
6. **RT Programs** = Reference segments by number (SEGM, SEGM2, RSEGM)
7. **RTCOMMON** = Shared memory area for all RT programs and ND-500
8. **ND-500 segments** = Can be mapped to RT segments or RTCOMMON for communication

**Key insights:**
- Segments live in SEGFIL files on disk
- Loaded on demand into physical memory
- RT programs reference by number, not by file name
- Multiple areas (MEMORY/SAVE/HENT) for redundancy and fast restart
- RTCOMMON provides fast shared memory for ND-100 ↔ ND-500 communication

**For emulator:** Track segment table, implement on-demand loading, manage physical page allocation.

---

*For ND-500 communication details, see `05-ND500-DMA-KERNEL.md` and `08-MESSAGE-PASSING-DETAILED.md`.*


