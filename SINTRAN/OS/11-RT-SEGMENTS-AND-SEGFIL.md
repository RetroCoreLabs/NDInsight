# RT Segments and Segment Files

**Status:** sections 1-3 rewritten 2026-10-29 from what was read off four real packs
(BIGDISK0-K-100, BIGDISK0-L2-100, BIGDISK0-L-SEMICS, nd100x SMD0; SINTRAN K and L), the kernel
listing and the manuals; every claim there is tagged **VERIFIED**, **SOURCE** or **OPEN**.
Sections 4-9 are the 2025 text about RT programs, RTCOMMON and the ND-500, with their dated
correction notes; the C# in section 9 is a sketch written before the measurements.

Related chapters: [29-SEGMENT-MAP-FROM-THE-GENERATION.md](29-SEGMENT-MAP-FROM-THE-GENERATION.md)
(the generation listing: which NPL file is in which segment, the disk layout symbols),
[30-SYSTEM-SEGMENTS-AND-PAGE-TABLES-BY-RELEASE.md](30-SYSTEM-SEGMENTS-AND-PAGE-TABLES-BY-RELEASE.md)
(every system segment by name and purpose, every page table, K to N),
[22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md](22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md)
(the tables in memory, the name records), [01-BOOT-SEQUENCE.md](01-BOOT-SEQUENCE.md) (how the
segments get into memory), [28-CPU-NUMBER-AND-TYPE-ON-DISK.md](28-CPU-NUMBER-AND-TYPE-ON-DISK.md)
(one worked offline edit). The tool that implements this model is `ndtool --segments /
--export-segment / --import-segment / --cpu-identity` in the sibling repository `norskdata-ndfs`.

Units: a **page** is 1024 words = 2048 bytes; a **disk block** is 512 words = 1024 bytes
(`ABLPAGE` = 2 blocks per page on these packs). Numbers are octal unless marked dec.

---

## Table of Contents

1. [What a segment is](#1-what-a-segment-is)
2. [Segment files on disk](#2-segment-files-on-disk)
3. [Save copy, image copy, running segment](#3-save-copy-image-copy-running-segment)
4. [RT Segments vs Segment Files](#4-rt-segments-vs-segment-files)
5. [How RT Programs Reference Segments](#5-how-rt-programs-reference-segments)
6. [RTCOMMON - Shared Memory Area](#6-rtcommon---shared-memory-area)
7. [ND-500 Communication via RT Segments](#7-nd-500-communication-via-rt-segments)
8. [Complete Disk-to-Memory Mapping](#8-complete-disk-to-memory-mapping)
9. [C# Implementation](#9-c-implementation)

---

## 1. What a segment is

A **segment** is a block of up to 64 KW of code or data that SINTRAN swaps as a unit: it has a
number, a logical address range inside one 64 KW bank, a length in pages, a place on disk, and
a page table it is mapped in while it runs. The whole operating system outside the common code is
segments (the file system, the command processor, the drivers for each level, the RT-loader, the
data page), and so is every RT program and background program. One **segment table** describes
them all, by number; there is no per-file numbering. **VERIFIED** (segment table read off the packs,
chapter 22 §3, chapter 28 §4.1).

### 1.1 The segment-table entry (8 words)

| Word | Symbol | Meaning | Unit |
|---|---|---|---|
| 0 | `SEGLI` | forward LRU link | segment-table address |
| 1 | `PRESE` | backward LRU link | segment-table address |
| 2 | `LOGAD` | logical base: low 6 bits = page within the 64 KW bank; the page table in the generation entry (`DPIT@6+2` = page table DPIT, page 2) | pages |
| 3 | `SEGLE` | length, low 10 bits | pages |
| 4 | `MADR` | page of the segment inside its segment file | pages |
| 5 | `FLAG` | bits 13-15 = segment file number (0..4; `SGFI4=100000` is file 4); bit 0 = `5OK` | - |
| 6 | `SGSTA` | protection / ring | - |
| 7 | `BPAGL` | core-map head, 0 = not in memory | core-map address |

**VERIFIED**: `SYMBOL-1-LIST` K03 lines 349-356, identical in L07 and M06; chapter 22 §3.3; read
off the packs in chapter 28 §4.1. There is no "SEGFIL number" word, no "physical page" word and
no "reference count" word.

### 1.2 Where the table is

In memory at `(SEGTB << 16) + SEGST` (chapter 22 §3.2). On disk it is itself a segment inside
`(SYSTEM)SEGFIL0:DATA` (`S3ISGT` image, segment 27; `S3SSGT` save, segment 24), found offline by
the self-validating scan of [26-INITIAL-COMMAND-BUFFER-ON-DISK.md](26-INITIAL-COMMAND-BUFFER-ON-DISK.md)
§3.2: page 461 of `SEGFIL0:DATA` on the K pack, 1275 on the L packs. **VERIFIED.**

### 1.3 Where the names are

Not in the segment table and not in the symbol lists. The RT-loader keeps every segment name as a
"DEFINED SEGMENT NAME" record (type 25B, SIXBIT packed name, segment number) in `(SYSTEM)RTFIL:DATA`
and in the `S3RTFIL` segment; names are given to segments 2-64 "the first time the RT-Loader is
entered" (K release information line 7939). Decoded on the K and L packs: 74 and 98 names, among
them S3IMAGE 2, S3RTFIL 10, S3DPIT 23, S3SSGT 24, S3ISGT 27, S3PATCH 43, S3IDPIT 44, S3SDPIT 53.
**VERIFIED** (chapter 22 §6.5, chapter 28 §4.1, chapter 30 for the whole list).

## 2. Segment files on disk

### 2.1 What a segment file is

A **segment file** is one contiguous NDFS file that holds segments page after page; the kernel
addresses a segment's page as `DBLST(N) + (MADR + P) * ABLPAGE(N)` disk blocks on the disk
`MASSNO(N)`, where `N = FLAG >> 13` is the segment file number (`IP-P2-SEGADM.NPL` RWSEGM lines
1532-1583: "SEGMENT FILE NO. IS IN TOP OF FLAG", "DISK ADDRESS FOR THIS SEGMENT FILE (DOUBLE WORD)",
"NUMBER OF DISK BLOCKS PER PAGE", "LOGICAL UNIT FOR THE DISK OF THIS SEGMENT FILE"). In pages:

```
disk page of segment page P = DBLST(N) / ABLPAGE(N) + MADR + P
```

The three tables are words in the resident data page (`DBLST=004023`; `ABLPA=004461` L07/M06,
`004451` K03; `MASSN=004441` L07/M06, `004431` K03; from the packs' own `SYMBOL-1-LIST`), so an
offline reader takes them from the S3IDPIT copy. **SOURCE + VERIFIED.**

### 2.2 The files on a pack

Measured on every pack (disk pages, dec):

| Disk pages | NDFS file | Segment file | Holds |
|---|---|---|---|
| 0 | the directory's page 0 | - | page-0 bootstrap, directory label, the "entered by system N" stamp |
| 1-63 | `(SYSTEM)SINTRAN:DATA` | 4 | the absolute save copies: S3SAVE (52) at page 1, S3SDPIT (53) at page 28 on K, S3SSYS (54), S3SERRP (55) at 100B, S3SERD (60) |
| 64-127 | `(SYSTEM)MACM-AREA:DATA` | 4 | S3SRTC (56) RT-loader code at 137B, S3SRTD (57), S3MEMTF (63) |
| 128 up | `(SYSTEM)SEGFIL0:DATA` | 0 | everything else: S3IMAGE at its page 0, the segment table, all image and save copies of L and M, the running segments, user segments |

`DBLST(0) = 256` blocks and `ABLPAGE(0) = 2`, so segment file 0 starts at disk page 128, exactly
where `SEGFIL0:DATA` begins; `PH-P2-OPPSTART.NPL` line 746 computes the same
(`A*200+XXSWTYPE=:BLST(1)`, "SET START OF SEGFIL0 IN SECTORS"). Segment file 4 is not a user file:
lines 749-751 copy `MASSNO(0)` to entry 4 and base it at disk page 1, and the K release
information says segments 52-60 and 63 "are placed on the files SINTRAN:DATA and MACM-AREA:DATA"
(line 7941). On the L packs the save copies of the DPIT, system segment and the rest sit in
`SEGFIL0` instead (the generation layout of chapter 29 §3); only S3SAVE, S3SERRP, S3SRTC, S3SRTD
and S3MEMTF stay on file 4 there. **VERIFIED.**

### 2.3 Segment files 1 to 3

A system has at most four segment files, 0 to 3, `SEGFIL0:DATA` to `SEGFIL3:DATA` by convention,
each one contiguous file (`ND-60.133.02A SINTRAN III Real Time Guide.md` 2597, 2605; System
Supervisor 4108). Which file a new segment lands in is the RT-loader's `*SET-SEGMENT-FILE`, fixed
at `*END-LOAD` (Real Time Guide 2599-2601); the advice is "Load onto SEGFIL0 until it becomes
full. Then switch to SEGFIL1" (System Supervisor 4137). No manual assigns a purpose to a file
number, and ND-500 domains (`:PSEG`, `:DSEG`, `:LINK`, `:DESC`, chapter 09) are not SINTRAN
segments at all. On the four packs `DBLST(1..3) = 0`: no second file was ever defined. **VERIFIED.**

## 3. Save copy, image copy, running segment

Most system segments exist three times (chapter 29 §3, chapter 30):

| Copy | Example (data page) | Lives | Used when |
|---|---|---|---|
| **save** (`S3S...`, `MS...` page symbol) | S3SDPIT, segment 53 | on disk; file 4 on K, `SEGFIL0` on L and M | a **cold start** (`HENTFLAG=0`) copies it over the image copy and loads it |
| **image** (`S3I...`, `MI...` page symbol) | S3IDPIT, segment 44 | on disk in `SEGFIL0` | a **warm start** (`HENTFLAG><0`) loads it as it is; the running system swaps against it |
| **running** (the plain name) | S3DPIT, segment 23 | memory only (MADR 0, status 162010) | always, once the system runs |

`PH-P2-OPPSTART.NPL` 262 and 283-284 read the data page from the save copy when `HENTFLAG=0`,
from the image copy otherwise; 771-776 copy save over image only when `HENTFLAG=0`; 772-841 do
the same for 32 segments. There is no separate "SAVE area", no separate "HENT snapshot area" and
no "swap area" as disk regions: the save copies are ordinary segments, the swap space is the
segment files themselves (`MASSNO(0)` is the "LOGICAL DEV.NO. OF MAIN-SWAP-DEVICE", line 741),
and MACM's `)HENT` ("GET SINTRAN FROM SAVE-AREA", System Supervisor 3982, 4920) is the cold start,
not a warm one. **SOURCE + VERIFIED** (the two L packs show every pair of copies; the K pack's
S3IMAGE and S3SAVE are byte-identical).

```mermaid
flowchart LR
    S["save copy<br/>S3S... on disk"] -- "cold start: CRWDISC copy" --> I["image copy<br/>S3I... on disk"]
    I -- "warm start" --> R["running segment<br/>in memory"]
    S -- "cold start" --> R
    R -- "swapped out / in while running" --> I
    style S fill:#2196F3,stroke:#1565C0,color:#fff
    style I fill:#2196F3,stroke:#1565C0,color:#fff
    style R fill:#4CAF50,stroke:#2E7D32,color:#fff
```

The `M...` / `L...` symbols that name each copy's page and length (`MSDPT`, `MIDPT`, `LSDPT`,
`MSSGT`, `MISGT`, `MFILS`, `MICOM`, ...) are the generation's disk layout of `SEGFIL0`; chapter 29 §3
lists them all with the segment-table entries they feed. On the L packs they are also in the pack's
own `SYMBOL-2-LIST:SYMB`.

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
> name field (section 1.1), and the names are in no symbol list either (chapter 22 §6.4).
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
> formula in section 2.1; a working implementation is `ndfs-c/src/sintran_segments.c`
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

1. **SEGFIL** = Container files on disk holding multiple segments (at most four, 0-3; "file 4" is the kernel's absolute-save area - section 2.2)
2. **SAVE area** = Pristine backup of system segments (ordinary segments: in `SEGFIL0:DATA` on L, in `SINTRAN:DATA`/`MACM-AREA:DATA` on K - section 3)
3. **IMAGE area** = Live SEGFIL 0 used during operation
4. **HENT area** = there is none; HENT is the cold start, a warm start loads the image copies (section 3)
5. **Segment Table** = Maps segment numbers → SEGFIL locations (8-word entries, MADR in 1024-word pages - section 1.1)
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


