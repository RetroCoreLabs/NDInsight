# Reading and Changing the CPU Number and CPU Type of a SINTRAN Pack From a Disk Image

**Status:** measured on five real packs (SINTRAN K and L) on 2026-10-29; the write path is specified
but not yet run end to end (see §9).
**Scope:** SINTRAN III VSX / VSX-500, versions K and L measured, M from the symbol lists and the
carved M-VSX-500 image.
**Purpose:** a complete, implementable specification for finding the words that hold a pack's
**CPU number** (SYSNO, FCPUN) and **CPU type** (HWINFO(2)) inside an NDFS disk image, changing
them **offline, without booting**, and clearing the directory's "entered by system N" stamp so the
pack is not refused by the new machine.

Written for implementers extending:
- `norskdata-ndfs` (`ndfs-c` and `ndtool`, `ndfs-py`, `ndfs-ts`) - the segment-table locator
  already there (`sintran.c`) is the mechanism this chapter reuses
- RetroCore (`Emulated.Utilities\ND\FileSystem`, RetroCommander) and nd100x (web front end,
  `sintran-initial-commands.js`)

Cross-references:
- [26-INITIAL-COMMAND-BUFFER-ON-DISK.md](26-INITIAL-COMMAND-BUFFER-ON-DISK.md) - how a kernel
  symbol becomes a byte offset in `SEGFIL0:DATA` (segment table, entry layout). Everything here
  builds on §3 of that chapter.
- [27-CPU-TYPE-THE-THREE-MEANINGS.md](27-CPU-TYPE-THE-THREE-MEANINGS.md) - what "CPU type" means
  and why the order-form code is never read by the kernel.
- [03-CPU-DETECTION-AND-INITIALIZATION.md](03-CPU-DETECTION-AND-INITIALIZATION.md) - SYSEVAL and
  GCPUNR, the back-wiring PROM layout.
- [../Filesystem/on-disk-format/extended-info-block.md](../Filesystem/on-disk-format/extended-info-block.md)
  and [../Filesystem/code-logic/enter-directory.md](../Filesystem/code-logic/enter-directory.md) -
  the page-0 field that CHDSI checks at ENTER-DIRECTORY.
- [ndwiki-CPU-type.wiki](ndwiki-CPU-type.wiki) - the ndwiki article "CPU type" (the code table,
  the order form, NEW-SYSTEM).
- `tools/boot-floppy/patches/README.md` §6 and `tools/boot-floppy/patches/tools/read_revle.py` -
  the first offline read of SYSNO and REVLE out of carved DPIT segments.

Notation: words are 16-bit, big-endian. 1 page = **1024 words = 2048 bytes**. Octal is written
`NNNNNB` or `NNNNN₈`. Every claim is tagged **VERIFIED** (read from a pack, a kernel listing, a
manual or the NPL source, with the place named), **INFERRED** or **OPEN**.

---

## 0. Executive summary

| Question | Answer | Confidence |
|---|---|---|
| Where does the CPU number live on a pack? | In three copies of the resident data page (the "DPIT" segments 23, 44 and 53), at kernel symbol **SYSNO = 004051B** and again at **FCPUN**. The CPU type is at **HWINF+2 = 004054B**. The patch level is at **REVLE = 004057B**. | VERIFIED (K and L packs, §5, §6) |
| Are those addresses the same in every version? | SYSNO, HWINF and REVLE: yes, 004051/004052/004057 in J (different page), K03, L07, M06 and in every pack measured. **FCPUN moves with every generation** (110166 J, 103771 K03, 105034 the K pack here, 004414 L07/M06 and both L packs here, 107017 another L build). | VERIFIED (§5) |
| How does a tool get the right FCPUN? | From the pack's own `(SYSTEM)SYMBOL-1-LIST:SYMB` / `SYMBOL-2-LIST:SYMB`, which every system pack carries. Never from a fixed table. | VERIFIED (§5.2) |
| Which copies have to be changed? | Every copy that is on disk: the image copy S3IDPIT (segment 44, in `SEGFIL0:DATA`) and the save copy S3SDPIT (segment 53: in `SEGFIL0:DATA` on L and M, in **`SINTRAN:DATA`** on K). The live copy S3DPIT (segment 23) has no disk address; it exists only in memory. | VERIFIED (§4) |
| What did ND's own procedure change? | Only S3SDPIT, followed by a mandatory cold start, which copies save → image → memory. | VERIFIED (§3.2) |
| Does the disk value survive on an ND-110 / ND-120? | Only if the back-wiring PROM has no valid signature. With the signature, GCPUNR overwrites SYSNO, FCPUN, HWINFO(2) and NLEGU in memory at every start (SINTRAN L and later). SINTRAN K stops dead on the signature. | VERIFIED (§2.3) |
| Why can a renamed pack refuse to mount? | Page 0 holds the system number of the machine that last entered the directory (extended-info word 5) and an "entered" flag (word 4 bit 15). CHDSI compares the stored number with **SYSNO** and refuses with error 3203 "DIRECTORY ENTERED BY ANOTHER SYSTEM". | VERIFIED (§7) |
| Is there a tool for that part already? | `ndtool --release <image>` (ndfs-c 0.0.8) clears the flag and the number and fixes the checksum. | VERIFIED (§7.3) |
| Does the kernel care about the CPU type? | No. HWINFO(2) has one write and no read in the J, L and M sources. It is banner and MON 262 output. The CPU number is what matters (COSMOS, directory ownership). | VERIFIED (§1) |

---

## 1. The values and who uses them

The resident data page at logical 004000B-005777B holds a 12-word system information table. The
words this chapter is about (all **VERIFIED** from `SINTRAN/NPL-SOURCE/SYMBOLS/*/SYMBOL-1-LIST.SYMB.TXT`
and the packs' own lists, §5):

| Symbol | Address | Meaning | Written by | Read by |
|---|---|---|---|---|
| `SYSNO` | 004051B | the CPU number ("SYSTEM NUMBER (NORMALLY CPU NUMBER)", `PH-P2-OPPSTART.NPL:3412`) | generation (J), NEW-SYSTEM + patch run (K and later), GCPUNR from the PROM (L and later) | COSMOS/TAD login `MP-P2-1.NPL:232` ("LOCAL CONNECTIONS ALWAYS OK"), PIOC datafield `RP-P2-PIOC.NPL:372`, CHDSI at ENTER-DIRECTORY (§7), `@LIST-TITLE`, MON 262 |
| `FCPUN` | per build (§5) | a second copy of the CPU number, kept among the file-system tables | the same writers as SYSNO (`A=:SYSNO=:FCPUN`, `PH-P2-OPPSTART.NPL:3564`; `FCPUN/ 33CPN` in the patch run) | **no reader found** in the NPL subset; the file-system code is not in the source. OPEN |
| `HWINF+2` = HWINFO(2) | 004054B | the CPU type, the order-form code (100, 102, 9883 ...) | NEW-SYSTEM + patch run (`HWINF+2/ 33CPU`), GCPUNR from the PROM | **nothing in the kernel.** One write, no read in J, L, M (`23-WINCHESTER-POF.NPL:692` says "HWINFO(2) NOT USED"). Printed by `@LIST-TITLE`, copied out by MON 262 |
| `REVLE` | 004057B | the patch level ("REVISION (PATCH FILE NO.)" on the banner) | patch run (`REVLE/ 33CPV`) | banner |
| `PRFLAG` | 006634B (L07), 006620B (M06), absent in K03 and J | 1 when GCPUNR has read a valid PROM; "USED BY NEW-SYSTEM" (`PH-P2-OPPSTART.NPL:3564`) | GCPUNR | NEW-SYSTEM (comment only; its code is not available). OPEN how |
| `NLEGU` | 006633B (L07); absent in K03 and J | number of legal users, from PROM byte 4 | GCPUNR | `MP-P2-1.NPL:238` (login limit) |

The generation symbols **`33CPN`** (CPU number) and **`33CPU`** (CPU type) are what the operator's
answers become; they live in the pack's `SYMBOL-2-LIST:SYMB` and are what the patch run deposits
(`SYSNO/ 33CPN`, `FCPUN/ 33CPN`, `HWINF+2/ 33CPU`). **VERIFIED**: the K pack measured here has
`33CPN=000144` (100) and `33CPU=000156` (110) in its list; both L packs have 0 and 0
(generation zeroes them, `NPL-SOURCE-2/NPL/0.SIN-GEN.NPL:74-75` "FORCE NEW-SYSTEM TO ASK FOR
CPU-NUMBER"). The ndwiki article notes the real-world convention `type.number`, for example
`9883.21005` on a Satellite label.

---

## 2. How the number gets onto a pack, and what can override it

### 2.1 Per version

| Version | Mechanism | Source |
|---|---|---|
| H | separate program `CPU-TYPE:PROG` on the install floppies | `tools/boot-floppy/patches/inventory.md:70,82` |
| J | fixed at generation: `FCPUN,33CPN` in `NPL-SOURCE-2/NPL/04-SIN4-GEN.NPL:1477`, 33CPN set in the symbol list | VERIFIED |
| K | NEW-SYSTEM asks "Give CPU number (in decimal):" and "Give CPU type (in decimal):" (K release information, `../Release-Documentation/ND-60230-5-EN SINTRAN III - Release Information - K-version.md` lines 1102-1109); the patch run writes them (§3.2) | VERIFIED |
| L | the same questions; NEW-SYSTEM has a `CPU-UPDATE` sub-command "update CPU number and CPU type" (L release information lines 521-554, 641) | VERIFIED |
| M | "answer the questions for CPU number and CPU type" (M release information line 712) | VERIFIED |
| N | "**If** you get the question 'Give CPU number (in decimal):' ..." (N release information lines 685-686) | VERIFIED; why it became conditional is OPEN (fits "skipped when the PROM was read", INFERRED) |

The documented dialogue (`../../Operations/SINTRAN/ND-30.003.007 EN SINTRAN III System Supervisor.md`
lines 5076-5090), where pressing RETURN at the type prompt means "no CPU type assigned":

```
Checking CPU number ... Wait ...
> Give CPU number (in decimal): 6586
--- OK
Checking CPU type ... Wait ...
> Give CPU type (in decimal):
--- OK
> Do you want to run the patch-file (def=Y)? Y
> Defining SEGFILE and loading DMAC (def=Y)? Y
```

How NEW-SYSTEM turns the typed answers into the `33CPN` / `33CPU` values the patch run reads is
**OPEN**: the program exists only as a binary. The result is visible, though: the K pack's
`SYMBOL-2-LIST:SYMB` carries the answers (§1).

### 2.2 The three copies and the two kinds of start

`PH-P2-OPPSTART.NPL` (**VERIFIED**): line 262 `DPSA:=MSDPT, DPIM:=MIDPT` (disk addresses of the save
and image copies); lines 283-284 read the DPIT into memory from the **save** copy when `HENTFLAG=0`
and from the **image** copy otherwise; lines 771-776 "COPY FROM SAVE TO IMAGE ... COPY DPIT" when
`HENTFLAG=0`. The System Supervisor manual says the same: a cold start copies the save area to the
image area and the image to memory; a warm start copies the image to memory and does not use the
save area (lines 2912, 2961-2967, 3803-3816).

So a value in **S3SDPIT** survives everything; a value only in **S3IDPIT** survives a warm start and
is overwritten by the next cold start; a value only in **S3DPIT** (memory) survives nothing. The
`*CHANGE-VARIABLE` command has the same three targets, `(<memory?>) (<image?>) (<save-area?>)`
(System Supervisor line 14852).

### 2.3 The back-wiring PROM on ND-110 and ND-120 (SINTRAN L and later)

At every start `PH-P2-OPPSTART.NPL:313` runs `IF HWINFO(0)/\377 >= 3 THEN CALL GCPUNR FI`, that is
on an ND-110 or ND-120 only. GCPUNR (lines 3542-3569) executes VERSN on levels 1-7 to read PROM
bytes 0-7, and **if bytes 6-7 equal 52652B (0x55AA)** it stores PROM word 0 into `SYSNO` and `FCPUN`
(unless -1), PROM word 1 into `HWINFO(2)` (unless -1), PROM byte 4 into `NLEGU` (unless 377B), and
sets `PRFLAG=1`. **VERIFIED.** Both the ND-110 and the ND-120 carry the PROM: the ND-110 functional
description documents it directly (`../../Reference-Manuals/ND-06.026-1-EN ND-110 Functional Description.md`
lines 766, 7256-7258), the joint microprogrammer's guide lists IDBS 35 "RINR - read installation
number" without an "ND-110 only" mark (`ND-06.031.1 EN ND-110 and ND-120 Microprogrammer's Guide.md:1136`),
and the kernel comment says "CALLED ONLY IF 110/120 CPU". No ND-120 hardware manual is on hand (OPEN).

Consequences for a disk patch:

- On an **ND-100 / ND-100/CX** the disk value is the value. GCPUNR never runs.
- On an **ND-110 / ND-120 with a programmed PROM**, SINTRAN L and later take the CPU number and type
  from the PROM at every start, so the disk words are overwritten in memory before the banner.
  The disk words still matter for the directory stamp (§7) and for anything that reads the pack
  offline.
- On an **ND-110 / ND-120 with SINTRAN K**, the K start-up code reads PROM bytes 6-7 on levels 6 and
  7 and, when they equal 52652B, jumps to `IOF; WAIT` at address 2 before printing anything.
  **VERIFIED** by CPU trace on the K pack `BIGDISK0-K-100` in the RetroCore emulator on 2026-10-29
  (RetroCore `DOCS/ND_CPU_SYSTEM_TYPE_CODES_REFERENCE.md` §10.4 and `CpuND100.cs`,
  `VersnPromSignatureNone`). GCPUNR, PRFLAG and NLEGU are absent from the K03 symbol lists and the
  J source, so the PROM reader is an L addition. Why K treats a programmed PROM as fatal is OPEN;
  no K source is available.
- The emulators: RetroCore's default PROM for ND110CX/ND120CX has **no signature** since
  2026-10-29, so K and L packs boot unchanged and keep their disk values; setting `cpu_number` /
  `system_type` / `legal_users` arms the signature and the PROM then wins, exactly as on the real
  machine. nd100x's default PROM (`src/cpu/cpu_instr.c`, `versn_load_default_prom`) still carries
  the signature with SYSNO 102, so on nd100x an ND-110/ND-120 K pack stops and an L pack reports
  CPU NUMBER 102 whatever the disk says. **VERIFIED by reading the code; the nd100x boot itself was
  not run.**

---

## 3. The DMAC patch, decoded

### 3.1 The operator's session

```
@DMAC
* DMAC-1915F *   MAY 22, 1984
)CLEAR                      clear the symbol table
)OCT                        numbers are octal from here
SYSNO=4051                  define the three addresses (octal)
FCPUN=107017
TYPE=4054                   = HWINF+2
)CLOAD S3DPIT               open segment 23, the live DPIT (memory)
)DEC                        numbers are decimal from here
TYPE/9883  9883             open word TYPE: it holds 9883; deposit 9883 (unchanged)
SYSNO/21056  21238          open word SYSNO: 21056; deposit 21238
FCPUN/21056  21238          open word FCPUN: 21056; deposit 21238
)CLOAD S3IDPIT              segment 44, the image copy - same three deposits
)CLOAD S3SDPIT              segment 53, the save copy - same three deposits
)9EXIT                      close all files
```

DMAC is "a special version of the MAC assembler used for patching or debugging RT-programs. Also
used for patching of SINTRAN segments" (`../../Reference-Manuals/ND-60.128.5 EN SINTRAN III Reference Manual.md`
lines 4158-4179); it "can be used for patching any segment on a segment file" (System Supervisor
lines 14866-14890). The commands are MAC's (`ND-60.096.01 MAC ... User's Guide.md`): `)CLEAR`
(2218), `)OCT`/`)DEC` (3161-3202, affect what is read **and** printed), `SYM=expr` (2061), `expr/`
opens a word and prints it (1997-2017), a value then RETURN deposits it (4126-4132), `)9EXIT` closes
all files (2544). `)CLOAD` takes a segment number (System Supervisor 14890) and, in DMAC-1915F, a
segment **name**: ND's own patch log uses `)CLOAD S3SDPIT`, `)CLOAD 52`, `)CLOAD S3PATCH`
(`../XMSG/PATCH-FILE.OUT`, parity-encoded). How the name is resolved is OPEN (INFERRED: the
RT-loader's segment name table). Whether DMAC writes at each deposit or at `)9EXIT` is OPEN; MACF
documents a buffer pool flushed by `)LINE` and `)9EXIT`, so always end with `)9EXIT` (INFERRED).

The session renames the CPU from **21056 to 21238** and rewrites the type **9883** (ND-110 Satellite
model T9) with its existing value. The address `FCPUN=107017` is the FCPUN of the build the operator
was patching, not of every L build (§5).

### 3.2 ND's own run (the install and patch procedure)

From the K pack's `(SYSTEM)PATCH-FILE:OUT` (**VERIFIED**, read off `BIGDISK0-K-100` on 2026-10-29;
the same text is in `../XMSG/PATCH-FILE.OUT` and quoted in `tools/boot-floppy/patches/README.md`
§6):

```
)CLOAD S3PATCH
176000/000000   SYSNO; 33CPU; 33CPN; HWINF; FCPUN; REVLE; 33CPV
)SYSDF
)9ASSM SYMB-2-LIST
)SYSDF
)9ASSM SYMB-1-LIST
)SYSDF
)9ASSM SYMBOLS:FADM
)CLOAD S3SDPIT
SYSNO/000000   33CPN
FCPUN/000144   33CPN
HWINF+2/000000   33CPU
REVLE/177777     33CPV; 33CPV:010200
)9EXIT
Please do a cold start (@COLD-START) of your SYSTEM to get the patches into effect.
```

Three things to take from it: the addresses come from the pack's **own symbol lists**
(`)9ASSM SYMB-2-LIST`, `SYMB-1-LIST`), the values are the generation symbols `33CPN` / `33CPU` /
`33CPV`, and ND patches **only the save copy** and relies on the cold start to propagate it.

---

## 4. Where the words are on disk

### 4.1 The three DPIT segments

From the system-included segment tables (`../../Reference-Manuals/ND-820023-1-EN SINTRAN III-VSX System Documentation.md`
lines 837, 854, 861; the L, M, N release information) and the L07 generation source
(`../NPL-SOURCE/s3vs-4.symb` lines 79991, 80070, 80089) - **VERIFIED**:

| Segment | Name | What it is | Disk address |
|---|---|---|---|
| 23B | S3DPIT | the live resident data (memory) | none: `SG23, 0;0;DPIT@6+2;0;0;111;...` has MADR 0 |
| 44B | S3IDPIT | image copy, used by a warm start | `MIDPT` in `SEGFIL0:DATA` |
| 53B | S3SDPIT | save copy, used by a cold start | `MSDPT`: in `SEGFIL0:DATA` on L and M; on **segment file 4** on K |

All three have logical page 2 (`DPIT@6+2`, `UPITN@6+2`), so they load at **004000B** and an address
`A` in the DMAC session is word `A - 004000B` of the segment.

Segment-table facts read off the packs (**VERIFIED**, 2026-10-29; the segment table was found with
the self-validating scan of chapter 26 §3.2, pages 461 on K and 1275 on L):

| Pack | Seg | LOGAD | SEGLE (pages) | MADR | FLAG | Segment file |
|---|---|---|---|---|---|---|
| K (BIGDISK0-K-100, K-5000) | 44 | 000102 | 35 | 27 | 000111 | 0 = `SEGFIL0:DATA` |
| K | 53 | 000102 | 35 | 27 | **100111** | **4 = `SINTRAN:DATA`** |
| L (BIGDISK0-L2-100, L-SEMICS, nd100x SMD0) | 44 | 000102 | 45 | 1019 | 000111 | 0 |
| L | 53 | 000102 | 45 | 64 | 000111 | 0 |
| M (carved M-VSX-500, `tools/sintran-segment-carver/versions/M-VSX-500/segment-facts.json`) | 44 | | 45 | 1055 | 000111 | 0 |
| M | 53 | | 45 | 64 | 000111 | 0 |

`LOGAD & 77B = 2` is the logical page; the segment-file number is `(FLAG >> 13) & 7`. The K manual
says it: "All system included segments are placed on segment file number 0 ... except segments
52-60 and 63 which are placed on the files SINTRAN:DATA and MACM-AREA:DATA" (K release information
line 7941). On the K pack, `SINTRAN:DATA` is 60 pages long and page 27 of it holds the save copy:
word 004051 = 000144, 004054 = 000156, 004057 = 010200, 105034 = 000144, identical to S3IDPIT
(**VERIFIED** by reading the file).

### 4.2 The formula

```
pageIndex  = MADR                              (pages of 2048 bytes, counted from the start of the
                                                segment's file: SEGFIL0:DATA, or SINTRAN:DATA on K seg 53)
wordIndex  = A - (LOGAD & 77B) * 2000B          (= A - 004000B for the DPIT segments)
byteOffset = pageIndex * 2048 + wordIndex * 2    big-endian 16-bit word
```

Worked, L pack: SYSNO in S3SDPIT = `64 * 2048 + 41 * 2` = 131154; in S3IDPIT = `1019 * 2048 + 82`.
A new CPU number 21238 = 051366B = bytes `52 F6`.

---

## 5. Symbol addresses per build

### 5.1 The fixed ones

`SYSNO=004051`, `HWINF=004052` (so `HWINF+2=004054`), `REVLE=004057` in K03, L07 and M06
(`../NPL-SOURCE/SYMBOLS/*/SYMBOL-1-LIST.SYMB.TXT`) and in the symbol lists of every pack measured
here. In J the table sat in page 0 (`SYSNO=000046`, `HWINF=000047`). **VERIFIED.**

### 5.2 FCPUN moves

| Build | FCPUN | Where the value came from |
|---|---|---|
| J | 110166 | `SYMBOLS/J/SYMBOL-2-LIST.SYMB.TXT:974` |
| VSX J (NPL-SOURCE-2) | 110240 | `NPL-SOURCE-2/BOUT-6.SYMB:1917` |
| K03 | 103771 | `SYMBOLS/K03/SYMBOL-2-LIST.SYMB.TXT:1612` (FFTAB+3) |
| the K pack here (BIGDISK0-K-100, patch 10200B) | **105034** | its own `(SYSTEM)SYMBOL-2-LIST:SYMB` |
| L07 and both L packs here | **004414** | `SYMBOLS/L07/SYMBOL-1-LIST.SYMB.TXT:1372` and the packs' own `SYMBOL-1-LIST:SYMB` |
| M06 | 004414 | `SYMBOLS/M06/SYMBOL-1-LIST.SYMB.TXT:1440` |
| the build the operator patched in §3.1 | 107017 | the operator's symbol definition; the carved L-VSX-500 image holds the CPU number at that word too |

Why it moves: in J and K FCPUN is a word among the file-system tables (`ENDBF=*` / `FCPUN,33CPN` /
`MCCLC=*` after the name, directory and bit-file tables, `04-SIN4-GEN.NPL:1474-1478`), whose size
depends on the generation; in L and M the device name table moved to its own segments
(`S3DNAM`/`S3SDNAM`) and FCPUN sits in the system data page. **VERIFIED for the placement, INFERRED
for the reason the L/M address is stable.**

**Rule for a tool:** read `FCPUN=` (and `SYSNO=`, `HWINF=`, `REVLE=`, `33CPN=`, `33CPU=`) from the
pack's own `(SYSTEM)SYMBOL-1-LIST:SYMB` and `SYMBOL-2-LIST:SYMB`. Both files are present on every
system pack measured (K-100, L2-100, L-SEMICS). They are 7-bit text with even parity set on every
byte; strip bit 7 before parsing. A symbol line is `NAME=OOOOOO` (name up to 5 characters, value
octal). A tool must refuse to write when either list is missing or does not define FCPUN.

### 5.3 The measured packs

Read on 2026-10-29 (segment 44, S3IDPIT; segment 53 agrees on every pack):

| Pack | SYSNO 4051 | HWINFO(2) 4054 | REVLE 4057 | FCPUN (own symbol) | banner |
|---|---|---|---|---|---|
| BIGDISK0-K-100 (K) | 000144 = 100 | 000156 = 110 | 010200 | 105034 → 000144 = 100 | CPU TYPE 110, CPU NUMBER 100 |
| BIGDISK0-K-5000 (K) | 100 | 110 | 010200 | 100 | |
| BIGDISK0-L2-100 (L) | 000144 = 100 | 023233 = **9883** | 0 | 004414 → **051366 = 21238** | CPU TYPE 9883, CPU NUMBER 100 |
| BIGDISK0-L-SEMICS (L) | 100 | 000156 = 110 | 0 | 004414 → 000144 = 100 | |
| nd100x SMD0.IMG (L, PACK-ONE) | 000146 = 102 | 9883 | 0 | 004414 → 21238 | |

Two observations. On BIGDISK0-L2-100 and SMD0 the FCPUN word holds **21238** while SYSNO holds 100
or 102, so on those two packs the two copies of the CPU number disagree; nothing in the available
code reads FCPUN, so no symptom is known (OPEN). On the same two packs word 107017 holds the SYSNO
value (100 / 102) and on L-SEMICS it holds 034065, so 107017 is not FCPUN in these L builds; what
it is, is OPEN.

---

## 6. The CPU type codes

The order-form code written into HWINFO(2). The full table with product names is in
[ndwiki-CPU-type.wiki](ndwiki-CPU-type.wiki) (ndwiki "CPU type", local copy of 2026-09-02; the live
article of 2026-10-29 has the same codes and only says "census" where the copy says "machine
list"); the values
seen on the packs here are 100 and 110 (the K packs, L-SEMICS) and 9883 = ND-110 Satellite model T9
(L2-100, SMD0). The kernel never reads the value (§1), so any number boots; it is identification,
not configuration. The order manual ND-830053.3 lists 100, 102, 500, 502, 5561 as "some common
values" and the SINTRAN source writes the list as open-ended (`PH-P2-OPPSTART.NPL:3440`).

---

## 7. The directory's "entered by system N" stamp

### 7.1 The field

Page 0 of every directory device holds an 8-word extended-info block at byte 2000 (word 1750B),
just before the 32-byte master block (`../Filesystem/on-disk-format/extended-info-block.md`, lines
36-45). **VERIFIED:**

| Word | Byte | Field |
|---|---|---|
| 0 | 2000 | checksum: 16-bit additive sum of words 1-7 |
| 1-3 | 2002-2007 | reserved, 0 |
| 4 | 2008 | flag word; **bit 15 = "entered"** |
| 5 | 2010 | **system number of the machine that entered the directory** |
| 6-7 | 2012-2015 | page capacity, 32 bits |

All five packs here read `flag 0x8000, system 100` (`ndtool -i`).

### 7.2 The check

CHDSI (SINTRAN L, segment 006-S3FS at 37763B;
`tools/sintran-segment-carver/versions/L-VSX-500/re/kernel-carving/CHDSI-COMPLETE/CHDSI-COMPLETE.ASM`
lines 180-230) refuses the enter when **all** of: option bit 3 is clear, the entering `SYSNO` is
not 0, the stored flag bit 15 is set, the stored number is not 0, and the stored number differs
from `SYSNO`. The compare is against **SYSNO** (the indirect operands at 040105 and 040121 both
resolve through word 040155 = 004051), not FCPUN. The reject code is **3203 = DIRECTORY ENTERED
BY ANOTHER SYSTEM** (K release information lines 13357-13358). Otherwise CHDSI stamps `SYSNO` into
word 5 and sets bit 15. `@RELEASE-DIRECTORY` (REENB, 40162B) clears bit 15 only and keeps the
number. A bad or zero checksum makes CHDSI zero the whole block first, so the enter then succeeds.
**VERIFIED.** The effect of a refusal is that the directory is not entered at all; there is no
read-only mode on this path.

Since **CHDSI compares the stored number with the pack's SYSNO**, a pack whose directory was
entered by system 21056 and whose SYSNO is then changed to 21238 refuses itself at the next boot
unless the stamp is cleared or the number matches. That is the "disk locked to the old CPU number"
effect.

### 7.3 Clearing it

`ndtool --release <image>` (ndfs-c 0.0.8, `tools/ndtool/cmd_user.c:210-246`; library call
`ndfs_release_directory`) clears bit 15, zeroes word 5 and rewrites the checksum; `-n` previews.
SINTRAN itself keeps the number on release; either is accepted by CHDSI. The Python and TypeScript
libraries read the field (`MasterBlock.is_entered`, `ext_last_system_number`) but have no release
call; RetroCore's `Emulated.Utilities\ND\FileSystem\FSObject\MasterBlock.cs` reads it, has no
release, and still uses the disproved XOR checksum (OPEN, to fix before it ever writes page 0).

---

## 8. Specification for a tool

### 8.1 Read ("show cpu identity")

1. Open the image; read `(SYSTEM)SYMBOL-1-LIST:SYMB` and `SYMBOL-2-LIST:SYMB`; strip parity; parse
   `SYSNO`, `HWINF`, `REVLE`, `FCPUN`, `33CPN`, `33CPU`, `33CPV`, `INIBU`. Refuse if SYSNO or FCPUN
   is missing. Determine the version letter from `INIBU` (067172 K, 074123 L, 102327 M; chapter 26)
   and cross-check SYSNO = 004051.
2. Read `(SYSTEM)SEGFIL0:DATA`; find the segment table page (chapter 26 §3.2); take entries 44B and
   53B; require `LOGAD & 77B = 2` and `SEGLE` of 35 or 45 pages (report, do not refuse, other values).
3. For each: segment file = `(FLAG >> 13) & 7`; 0 means `SEGFIL0:DATA`, 4 means `SINTRAN:DATA`
   (the K save copy), anything else is OPEN and must be reported. Read the words at SYSNO, FCPUN,
   HWINF+2, REVLE with the §4.2 formula.
4. Read the page-0 extended-info block: flag bit 15, stored system number, checksum validity.
5. Print: version, the two DPIT copies with their file and page, SYSNO / FCPUN / type / REVLE for
   each, the generation symbols 33CPN / 33CPU, and the directory stamp. Flag a mismatch between the
   two copies, between SYSNO and FCPUN, and between the stamp and SYSNO.

### 8.2 Write ("set cpu number N [type T]")

1. Everything in 8.1 first; refuse on any missing piece.
2. In **both** on-disk DPIT copies (44 and 53, each in its own file) write `N` at SYSNO and at
   FCPUN, and `T` at HWINF+2 when given. The live copy 23 has no disk form and needs nothing.
3. Update `33CPN` (and `33CPU`) in `SYMBOL-2-LIST:SYMB` to the same values, so a later ND patch run
   (`SYSNO/ 33CPN`) does not put the old number back. The line format is `NAME=OOOOOO` with parity;
   rewrite the value in place with the same width. INFERRED to be sufficient; the only consumer seen
   is the patch mode file.
4. Clear the directory stamp (`ndfs_release_directory`) unless told not to, so the pack does not
   refuse itself with 3203 at the next enter.
5. Leave REVLE alone.
6. Verify by re-running 8.1 and comparing every word written.

### 8.3 What the tool cannot do

- Change the value a real or emulated ND-110/ND-120 reports when its PROM carries the signature:
  the PROM wins at every start (§2.3). The tool should say so when the image is going to be used on
  such a machine, but it cannot know that.
- Patch K's save copy when `SINTRAN:DATA` is missing or shorter than `MADR + SEGLE` pages: refuse.
- Do anything about pages SINTRAN keeps elsewhere that nobody has found yet (§10).

---

## 9. Verification done and not done

Done on 2026-10-29:

- Read path: §5.3 values read with a script built on `ndfs-py` (`NdfsFileSystem`,
  `sintran.find_segment_table_page`, `sintran._seg_entry`) from the five packs. Where the carved
  images and `read_revle.py` had values (K: SYSNO 100, REVLE 10200; L PACK-ONE: SYSNO 102, type 9883)
  they agree.
- K save copy inside `SINTRAN:DATA` at page 27 read and found identical to the image copy.
- Symbol lists extracted from the three packs with `ndtool -x -p`; FCPUN per build as in §5.2.
- Kernel side: the CHDSI compare and the 3203 code from the carved listing; the K halt on the PROM
  signature by CPU trace in RetroCore.

Not done:

- No pack has yet been patched with the §8.2 procedure and then booted to show the new CPU NUMBER on
  the banner and a clean ENTER-DIRECTORY. That is the acceptance test for the implementation.
- The DMAC write timing (deposit vs `)9EXIT`) and the name-to-number resolution of `)CLOAD` were not
  observed.

---

## 10. Open questions

1. What reads FCPUN. No reader in the NPL subset; the file-system segment is only carved. The two
   L packs where FCPUN and SYSNO disagree booted and ran COSMOS, so whatever reads it did not stop
   them.
2. What word 107017 is in the L builds here (holds the CPU number on two packs, 034065 on the third).
3. How NEW-SYSTEM uses PRFLAG and how its answers reach `33CPN` / `33CPU`.
4. Why SINTRAN K stops on a programmed PROM, and what a pre-L PROM held.
5. Whether anything else on a pack holds the CPU number: not found in the boot sector, the object
   entries or `S3-CONFIGURATION`; S3PATCH (segment 43, 176000B) holds the *addresses* of the symbols,
   not the values.
6. Whether DMAC's name lookup for `)CLOAD` is the RT-loader name table.
