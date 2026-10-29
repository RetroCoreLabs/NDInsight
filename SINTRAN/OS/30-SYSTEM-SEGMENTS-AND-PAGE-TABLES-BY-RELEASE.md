# System Segments and Page Tables by Release: Names, Purposes, Layout (J, K, L, M, N)

**Status:** compiled 2026-10-29 from the release information for J, K, L, M and N, the VSX system
documentation, and the segment names decoded from two real packs (K and L). Every row says where
it comes from. **VERIFIED** = read from a pack or a listing; **DOC** = from an ND manual (the OCR
of the manuals garbles some names, noted where seen); **INFERRED** = read off the name only.
Numbers are octal unless marked dec.

Cross-references: [11-RT-SEGMENTS-AND-SEGFIL.md](11-RT-SEGMENTS-AND-SEGFIL.md) (what a segment and a
segment file are), [29-SEGMENT-MAP-FROM-THE-GENERATION.md](29-SEGMENT-MAP-FROM-THE-GENERATION.md)
(the generation listing behind this table), [01-BOOT-SEQUENCE.md](01-BOOT-SEQUENCE.md) (how the
segments are loaded), [../Release-Documentation/SINTRAN-III-Release-History.md](../Release-Documentation/SINTRAN-III-Release-History.md)
§7 (the earlier cross-version sketch this chapter replaces).

Sources, with the place of the segment table in each:

| Release | Document | Segment table at | Layout chapters |
|---|---|---|---|
| J (1985) | `../Release-Documentation/ND-60.230.01_SINTRAN_III_J-version_Release_Information_January_1985.md` | §1.6.1, lines 589-630 (segments 2-43) | §1.6 |
| K (VSX) | `../Release-Documentation/ND-60230-5-EN SINTRAN III - Release Information - K-version.md` | §10.6, lines 7872-7941 | §10.1 memory, §10.2 disk, §10.3 page tables |
| K-era VSX system documentation | `../../Reference-Manuals/ND-820023-1-EN SINTRAN III-VSX System Documentation.md` | §2.5, lines 815-880 | |
| L | `../Release-Documentation/ND-860230-6-EN Sintran III - Release Information - L-Version.md` | §8.3, lines 2497-2598 | |
| M | `../Release-Documentation/ND-860230-7A-EN SINTRAN III - Release Information - M-Version.md` | §17.3, lines 3505-3600 | §17.1 disk, §17.2 page tables |
| N | `../Release-Documentation/ND-860230-8-EN SINTRAN III - Release Information - N-version.md` | §18.3, lines 2124-2228 | §18.1 disk, §18.2 page tables |
| the packs | `(SYSTEM)RTFIL:DATA` name records on BIGDISK0-K-100 (K, 74 names) and BIGDISK0-L2-100 (L, 98 names) | chapter 22 §6.5 | |

---

## 1. The page tables (PITs)

The ND-100 MMS has 16 page index tables of 64 pages each; SINTRAN gives every one a job. The
"Micro-common" (µ©, 2 pages) and the "common code" (©, up to 11 K) are mapped into nearly all of
them, so the kernel's shared routines are reachable whatever table is active. From the K release
information §10.3, the M §17.2 and the N §18.2 (identical in M and N). **DOC.**

| PIT | Name | Mapped in it | Plain purpose |
|---|---|---|---|
| 0 | - | nothing after start-up | used only during start-up (M, N) |
| 1 | UPITN | the user's segments | "users normal PIT": background and RT programs |
| 2 | UPITA | the user's alternate segments | "users alternate PIT": a second table for the same program |
| 3 | FUPIT | µ©, ©, page 13: remote file user segment | remote file access (RFA) users |
| 4 | FPIT | µ©, ©, page 13: the file system segment (S3FS) | the file system runs here |
| 5 | 5PIT | µ©, ©, page 13: MON 60, page 20: the ND-500 system monitor | ND-500 / ND-5000 monitor calls |
| 6 | XPIT | µ©, ©, page 13: XMSG | the XMSG kernel |
| 7 | DPIT | µ©, page 2: resident common data (37 K), 57: the windows (wind.BF background, wind.NS ND-500, wind.10, wind.12, wind.1/4), 62: system segment window, 72: data segment | the **data** table: RT descriptions, datafields, system variables, the segment-file tables; every system code path uses DPIT as its alternative table |
| 10 | RPIT | µ©, ©, 13: extended common, 15: monitor calls, B-level (level 4); from generation 500 also the segment administration | **resident code**: most monitor calls, OUTBT/INBT level code |
| 11 | SPIT | µ©, ©, 13: edit segment, 14: command segment, SSP/Mail, RT-loader, DMAC, error program | the "SINTRAN PIT": one of those segments at a time; page 13 always holds the edit routines |
| 12 | MPIT | µ©, ©, 13: extended common, 15: level 2, 10, 12, 13, 14, MPERF | the **monitor** table: monitor level, internal interrupts, the drivers for levels 10-13 |
| 13 | X5DP1 | ND-500 name tables segment, stack window | ND-500 names |
| 14 | X5DP2 | ND-500 standard domains segment, stack window | ND-500 standard domains |
| 15 | IPIT | µ©, ©, 13: extended common, 15: level 3, level 11 | the **I/O** table (L and later): level 3 and the mass-storage level 11 |
| 16 | - | nothing | unused (M, N) |
| 17 | DTPIT | direct tasks; used for mapping DPIT during start-up | direct tasks |

The K release information adds (§10.3 text): all system code runs in two-bank mode with DPIT as
the alternative page table; the common code must not exceed 11 K (0-25777B); µ© is also in DPIT
"mainly for parameter fetching and other operations on the user's data area"; the data not in any
PIT is the segment table, the memory map, the RT programs' register blocks and bitmaps, the big
terminal (TAD) datafields, the ND-500 mailboxes, the logical device number tables and the ND-500
communication buffers. IPIT (15) does not appear in the K table; it does in L, M and N. **DOC.**

Physical memory at run time (K §10.1): common code from physical 0 (11 K), restart routines, the
start program, resident data (DPIT, logical 4000B) from physical 60000B, then RPIT, MPIT, segment
table and memory map each inside one bank with buffer areas between them. **DOC.**

## 2. System layout on disk, per release

What the release information says sits where, in the three files that hold the kernel. Disk
addresses are pages from the start of the disk for `SINTRAN:DATA` and `MACM-AREA:DATA`, and from
the start of the file for `SEGFIL0:DATA` (where the manuals give the absolute address, 200B is the
file's start). **DOC**, with the measured pack values in the last column.

| Area | K (§10.2) | M (§17.1) / N (§18.1) | On the packs (chapter 11 §2.2, chapter 29 §3) |
|---|---|---|---|
| `SINTRAN:DATA`: common code, start/restart (the `)GJEM` / `)HENT` area) | disk page 1 | 1B, 77B pages, segment address 0 | S3SAVE (52) at disk page 1, 27 pages on K |
| `MACM-AREA:DATA`: error program | 100B | 100B, 20B pages, 30000B | S3SERRP (55) |
| `MACM-AREA:DATA`: RT-loader | 137B, 41 K | 137B, 41B pages, 30000B | S3SRTC (56), S3SRTD (57) |
| `MACM-AREA:DATA` (K only): end of resident data 112B, system segment 114B, Memtof 117B | 112B, 114B, 117B | - | S3SERD (60), S3SSYS (54), S3MEMTF (63) on K |
| `SEGFIL0:DATA`: common code + start/restart | 200B (13 K + 20 K) | 200B, 77B pages | S3IMAGE (2) at file page 0 |
| resident data (DPIT) | 233B, 43 K | 300B, 55B pages | S3SDPIT (53) at `MSDPT` 100B |
| system segment | 301B | 355B, 3B | S3SSYS (54) |
| spooling datafields | 304B | 360B, 1B | S3SSPD (31) |
| extended common | - | 361B, 2B | S3SECOM (60) |
| RPIT, MPIT | 305B, 372B (65 K each) | 363B, 446B (63B each) | S3SRPIT (16), S3SMPIT (17) |
| IPIT | - | 531B, 63B | S3SIPIT (65) |
| 5PIT | 651B | 614B, 5B | S3S5PIT (46) |
| ND-500 monitor | 656B | 621B, 60B | S3SSM5 (62) |
| segment table | 457B | 701B, 20B | S3SSGT (24) |
| ND-110, ND-120 micro program | - | 721B, 761B (40B each) | S3SU110 (110), S3SU120 (112) |
| file system | 477B | 1021B, 65B | S3SFS (12) |
| command segment | 564B | 1106B, 65B | S3SCP (13) |
| SSP/Mail | - | 1173B, 44B | S3SSM (70) |
| XMSG kernel, XROUT, watchdog | - | 1237B, 1276B, 1337B | S3SXMK (74), S3SXROU (75), S3SXMFI (102) |
| device name table | - | 1425B, 6B | S3SDNAM (100) |
| disk mirroring WD | - | 1433B, 4B | S3SDMWD (72) |
| NUCLEUS server, name server | - | 1437B, 1523B | S3SNKSE (104), S3SNKNA (106) |
| ERS watchdog program, data | - | 1623B, 1707B | S3SERWC (114), S3SERWD (116) |
| processor manager, PFTCON, BOPCOM, MT servers | - | 1777B, 2063B, 2147B, 2233B | S3SPRMA (120), S3SEVMS/S3SPWRS (122), S3SBOPC (124), S3SMTSE (126) |

The K table lists the **save** copies' disk pages; the M/N table lists the same areas one
generation later, where the layout grew (IPIT, micro code, the servers). The `s3vs-4` generation
listing (chapter 29 §3) matches the M/N column page for page from 300B (`MSDPT=100B` relative to
the file start 200B) onward. **VERIFIED** for the L packs.

## 3. The system segments, 2 to 127

One row per segment number. "Name on the pack" is the RT-loader record decoded from the K pack and
the L pack (**VERIFIED**; a blank means the pack has no record for that number). "Name in the
documents" gives the release information's spelling where it differs or where the pack has no
record (**DOC**; several are OCR misreads, flagged `?`). The description is the manuals' wording,
the purpose column is plain words. Versions: J K L M N = the segment exists in that release's
table (J from §1.6.1, the rest from §10.6 / §8.3 / §17.3 / §18.3).

### 3.1 The kernel and its copies

| No | Name on pack K / L | Name in documents | PIT | Description (manuals) | Purpose, plainly | J K L M N |
|---|---|---|---|---|---|---|
| 2 | S3IMAGE / S3IMAGE | | 1 | image of common code, start/restart | the resident kernel image the page-0 bootstrap loads | J K L M N |
| 52 | S3SAVE / S3SAVE | | 1 | save of common code & start/restart | untouched copy of 2 on segment file 4; cold start copies it over 2 | K L M N |
| 23 | S3DPIT / S3DPIT | | 7 | DPIT segment (global data) | the live resident data page in memory: RT descriptions, datafields, system tables, SYSNO | K L M N |
| 44 | S3IDPIT / S3IDPIT | L doc "S3DIPIT" (OCR) | 1 | image of DPIT | disk copy of 23 a warm start loads | K L M N |
| 53 | S3SDPIT / S3SDPIT | K doc "S3DSOPT", L doc "S3SOP1T" (OCR) | 1 | save of DPIT | disk copy of 23 a cold start loads and copies over 44; what ND's install run patches | K L M N |
| 60 | S3SERD / S3SECOM | K: save of DPIT last two pages; L-N: save of extended common | 1 | | K: the tail of the data page; L and later: the extended common data | K L M N |
| 61 | S3IERD / S3IECOM | K: image of DPIT last two pages; L-N: image of extended common | 1 | | image copies of the above | K L M N |
| 64 | S3ERD / S3ECOM | K: DPIT last two pages; L-N: extended common segment | 7 (K) / 10 (L-N) | | the running copy | K L M N |
| 24 | S3SSGT / S3SSGT | K doc "S3SGIT", L "S3SSGST", N "S3SGST" (OCR) | 1 | initial (save of) segment table | save copy of the segment table | K L M N |
| 27 | S3ISGT / S3ISGT | | 1 | image of segment table | the segment table SINTRAN reads at a warm start and swaps against | K L M N |
| 16 | S3SRPIT / S3SRPIT | | 1 | initial RPIT (save area) / save of RPIT | save copy of the resident-code segment | K L M N |
| 25 | S3IRPIT / S3IRPIT | L doc "S3RIPIT" (OCR) | 1 | image of RPIT | image copy | K L M N |
| 47 | S3RPIT / S3RPIT | K doc "S3SRPIT", L "S3RP1IT" (OCR) | 10 | RPIT segment | the running resident code: most monitor calls (RP-P2-* sources) | K L M N |
| 17 | S3SMPIT / S3SMPIT | | 1 | initial MPIT (save area) / save of MPIT | save copy of the monitor-code segment | K L M N |
| 26 | S3IMPIT / S3IMPIT | L doc "S3MIPIT" (OCR) | 1 | image of MPIT | image copy | K L M N |
| 35 | S3MPIT / S3MPIT | L doc "S3MP1T"; K doc lists it at 36 (OCR) | 12 | MPIT segment (N: "standard system A", 36 for "B & C") | the running monitor code: monitor level, level 14, drivers for levels 10-13 (MP-P2-* sources) | K L M N |
| 65 | - / S3SIPIT | | 1 | save of IPIT | save copy of the I/O-level code | L M N |
| 66 | - / S3IIPIT | | 1 | image of IPIT | image copy | L M N |
| 67 | - / S3IPIT | | 15 | IPIT segment | the running I/O code: level 3 and level 11 (IP-P2-* sources) | L M N |
| 46 | S3S5PIT / S3S5PIT | K doc "S3SSPIT" | 1 | save of 5PIT segment | save copy of the ND-500 monitor-call code | K L M N |
| 50 | S3I5PIT / S3I5PIT | K doc "S3ISPIT", L "S3IP1IT" (OCR) | 1 (10 in the VSX doc) | image of 5PIT segment | image copy | K L M N |
| 51 | S35PIT / S35PIT | docs "S3SPIT", "S3SP1IT", "S3S5PIT" | 5 | 5PIT segment | the running MON 60 code (5P-P2-MON60) | K L M N |
| 45 | S3ISYS / S3ISYS | K doc "S3SYS" | 1 | memory image of system segment | image of the system segment (the per-background-process system area template) | K L M N |
| 54 | S3SSYS / S3SSYS | K doc "S3SYSX", VSX doc "S3SERSV" (OCR) | 1 | save of system segment | its save copy | K L M N |
| 5 | S3ERRS / S3ERRS | L doc "S3ERS", M "S3ERFS" (OCR) | 7 | system segment for error program | the error program's own system segment | J K L M N |
| 31 | S3SSPD / S3SSPD | | 7 | initial (save of) spooling data fields | spooling datafields / queue | K L M N |
| 40 | S3FUDRT / S3FUDRT | K doc "S3UFDT", L "S3FURDT" | 7 | file user data segment for RT programs | file-system user data for RT programs | J K L M N |
| 110 / 111 | - / S3SU110, S3IU110 | L doc "S3SUI110" | 1 | save / image of ND-110 micro program | the ND-110 control store SINTRAN loads with LOCOSTORE | L M N |
| 112 / 113 | - / S3SU120, S3IU120 | | 1 | save / image of ND-120 micro program | the ND-120 control store | L M N |
| 43 | S3PATCH / S3PATCH | | 2 | reserved for internal use by ND / used for patching purposes | holds the addresses the patch mode file deposits (SYSNO, 33CPN ... at 176000B) | K L M N |
| 63 | S3MEMTF / S3MEMTF | K doc "S3MEMT" | - | Memtof | memory-to-floppy dump program | K L M N |
| 15 | S3BFLY / S3BFLY | | - | reserved for system extension / for Butterfly | placeholder; empty (26000:26000) | K L M N |
| 32 | S3RTACC / S3RTACC | J: RT-accounting segment; K-N: reserved, but not used | 1 | | RT accounting (J); kept as a placeholder later | J K L M N |
| 33, 34 | S3XMSGP, S3XMSGD / S3XMSGP, S3XMSGD | K: XMSG POF segment, XMSG demand segment (XROUT); L-N: reserved, but not used | 2 | | the K-era XMSG segments; on the L pack the records still exist but point at 76 and 77 (§3.4) | J K (L M N reserved) |

### 3.2 The programs SINTRAN runs in SPIT, FPIT and friends

| No | Name on pack K / L | Name in documents | PIT | Description (manuals) | Purpose, plainly | J K L M N |
|---|---|---|---|---|---|---|
| 3 | S3COM / S3CP | VSX doc "S3CG" (OCR) | 11 | command segment | the command processor (`@` commands), holds INIBU and the start program; every background program has it as SEGM1 | J K L M N |
| 13 | S3OPCSV / S3SCP | | 1 | initial / save of command segment | save copy of 3 | J K L M N |
| 6 | S3FS / S3FS | J "S3FSCOM" | 4 | file system segment | the file system: ENTER-DIRECTORY, object entries, bit file, CHDSI | J K L M N |
| 12 | S3FSSV / S3SFS | L doc "S3FSFS", VSX "S3SFSV" | 1 | initial / save of file system segment | save copy of 6 | J K L M N |
| 4 | S3RTL / S3RTL | L doc "S3RTIL" (OCR) | 11 | RT-loader segment | the RT-loader program (`@RT-LOADER`), owner of the segment names | J K L M N |
| 37 | S3RTD / S3RTD | | 1 | RT-loader data segment | the RT-loader's data | J K L M N |
| 56 | S3SRTC / S3SRTC | K doc "S3RTIC" (OCR) | 1 | save of RT-loader code segment | save copy of 4, on segment file 4 (disk page 137B) | K L M N |
| 57 | S3SRTD / S3SRTD | VSX doc "S3SRTO" (OCR) | 1 | save of RT-loader data segment | save copy of 37 | K L M N |
| 10 | S3RTFIL / S3RTFIL | | 2 | RTFIL segment | the RT-loader's file image, including the segment and RT program **name records** (chapter 22 §6.5); its disk file is `RTFIL:DATA` | J K L M N |
| 7 | S3DMAC / S3DMAC | | 11 | DMAC segment | DMAC, the patching assembler (chapter 28 §3) | J K L M N |
| 14 | S3ERRP / S3ERRP | | 11 | error program segment | the error program (ERRFATAL messages, error log output) | J K L M N |
| 55 | S3SERRP / S3SERRP | L doc "S3SSERR" | 1 | save of error program | save copy of 14, segment file 4 at 100B | K L M N |
| 11 | S3ERRL / S3ERRL | VSX "S3ERL", M "S3ERBL" | 1 | error log segment | the error log | J K L M N |
| 41 | S3IMED / S3IMED | | 1 | image of EDIT routines | image copy of the edit routines | K L M N |
| 42 | S3ED / S3ED | | 11 | EDIT routines | the command-line edit routines, always on page 13 of SPIT | K L M N |
| 36 | S3TAD / S3TAD | VSX "S3TA10" (OCR) | 11 | TADADM segment | TAD (terminal access device, COSMOS remote terminals) administration | J K L M N |
| 70 | - / S3SSM | | 1 | save service/mail segment | save copy of 71 | L M N |
| 71 | - / S3SM | | 11 | service/mail segment | SINTRAN-SERVICE-PROGRAM and MAIL (J had them as 15 / 23) | L M N |
| 22 | S3RFAC / S3RFAC | VSX "S3RAF2" (OCR) | 3 | remote file access segment | COSMOS remote file access | J K L M N |
| 72 / 73 | - / S3SDMWD, S3IDMWD | | 1 | save / image of disk mirroring WD segment | disk mirroring watchdog | L M N |
| 100 / 101 | - / S3SDNAM, S3DNAM | M, N "SDNAM" | 1 / 7 | save / running device name table | the device name table (the strings `FLOPPY-DISC` and friends), moved out of the file system in L | L M N |

### 3.3 ND-500 / ND-5000 and the servers

| No | Name on pack K / L | Name in documents | PIT | Description (manuals) | Purpose, plainly | J K L M N |
|---|---|---|---|---|---|---|
| 20 | S3SDT5 / S3SDT5 | VSX "S3MD", J "S3DT5" | 14 | ND-500 standard domains segment | ND-500 standard domain table | J K L M N |
| 21 | S3NMS5 / S3NMS5 | L doc "S3NM5S", M/N "S3NM5" | 13 | ND-500 name tables segment | ND-500 name tables | J K L M N |
| 30 | S3SM5 / S3SM5 | K doc "S3SMS", L "S3SMS5" | 5 | ND-500 system monitor segment | the running ND-500 / ND-5000 monitor | J K L M N |
| 62 | S3SSM5 / S3SSM5 | K doc "S3SMSB" (OCR) | 1 | save of ND-500 monitor | save copy of 30 | K L M N |
| 74 / 76 | - / S3SXMK, S3XMK | | 1 / 2 | save / running XMSG kernel | the XMSG message kernel (XPIT) | L M N |
| 75 / 77 | - / S3SXROU, S3XROU | | 1 / 2 | save / running XMSG XROUT segment | XROUT, the XMSG router (COSMOS) | L M N |
| 102 / 103 | - / S3SXMFI, S3XMFI | K pack: SXMFIDO at 66 | 1 | save / running XMSG watchdog (XMFIDO) | the XMSG watchdog | L M N |
| 104 / 105 | - / S3SNKSE, S3INKSE | | 11 | save / image of NUCLEUS server | NUCLEUS (ND-5000 era) server | L M N |
| 106 / 107 | - / S3SNKNA, S3INKNA | | 1 | save / image of NUCLEUS name server | NUCLEUS name server | L M N |
| 114 / 115 | - / S3SERWC, S3IERWC | L doc "S3SEIWC" | 1 | save / image of ERS watchdog program | ERS (error reporting system) watchdog code | L M N |
| 116 / 117 | - / S3SERWD, S3IERWD | | 1 / 2 | save / image of ERS watchdog data | its data | L M N |
| 120 / 121 | - / S3SPRMA, S3IPRMA | N "S3SPPRMA" | 11 | save / image of processor manager server | PROMAN | L M N |
| 122 / 123 | - / S3SEVMS, S3IEVMS | M, N: S3SPWRS / S3IPWRS "PFTCON server" | 11 | L: event message server; M, N: PFTCON (power supply controller) server | the L pack still names them event message server | L M N |
| 124 / 125 | - / S3SBOPC, S3IBOPC | | 11 | save / image of BOPCOM server | BOPCOM server | L M N |
| 126 / 127 | - / S3SMTSE, S3IMTSE | | 11 | save / image of MT server | MTSERV, magnetic tape server | L M N |

### 3.4 Where the packs and the documents disagree

- Number 36 is `S3TAD` on both packs; the K release information prints `S3MPIT` at 36 as well as
  `S3TAD`, and N lists two MPIT rows (35 "standard system A", 36 "standard systems B & C"). The
  packs have MPIT at 35 only.
- The L pack carries **two names for 76 and 77** (`S3XMK` and `S3XMSGP`, `S3XROU` and `S3XMSGD`):
  the K-era XMSG names were kept as aliases when the segments moved from 33/34. The release
  history noted the duplicate numbers without the reason; the records show it.
- The K pack has `SXMFIDO` at 66 (XMSG watchdog); in L it is `S3XMFI` at 103 and 66 is the image
  of IPIT.
- J's 15, 16, 17, 23, 24, 25, 26, 27, 30, 31, 35, 41, 42, 43 had other jobs (SINTRAN-SERVICE
  initial/running, NORD-net, PT3, reentrant file-system and file-user segments, two ND-500
  monitor segments, spooling program); K renumbered the system set and J's table is kept only for
  reading J packs.

### 3.5 Configuration-dependent segments seen on the packs

Above 127 (and in J above 43) the numbers are the generation's and the RT-loader's: background
programs (two segments each), spooling queues, ND-500 processes, user RT programs and products
loaded afterwards. Names decoded from the two packs, with what is known about them:

| Name | K pack | L pack | What it is |
|---|---|---|---|
| `COSPOOL` | 72 | 137 | COSMOS spooling server (the RT program COSPO "COSMOS-spooling server", K §10.7). **DOC** |
| `ENCOSE0`, `ENCS0B0`-`ENCS0B3` | 101-105 | 142, 144-147 | the Ethernet COSMOS network server ENNS0 and its buffers; "ENNS0" is the server the boot banner starts. **INFERRED** from the name and the banner |
| `XMSGCMD` | 76 | - | XMSG command program. **INFERRED** |
| `XFTRAD` | 71 | 135 | TAD file transfer. **INFERRED** |
| `CCT`, `CFT` | 67, 70 | 132, 130 | COSMOS; which products is **OPEN** |
| `FSASG` | 75 | 136 | **OPEN** |
| `POPWR` | 106 | 150 | **OPEN** |
| `SNA3270` | - | 134 | SNA 3270 terminal emulation. **INFERRED** |
| `208`, `209`, `2518`, `2528`, `2548`, `2549`, `2581`, `2608`, `2618`, `2619` | 115-133 | - | user segments named by number by the RT-loader; what loaded them is **OPEN** |

## 4. Reading the table on a pack

`ndtool --segments <image>` prints every segment of a pack with its name from the RT-loader
records, its page table, logical range, length, disk page and file, so a pack of any generation
can be checked against this chapter; `ndtool --export-segment` copies one out for carving. The
generation listing behind the L layout is decoded in chapter 29.
