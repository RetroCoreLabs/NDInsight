# Recreating SINTRAN III from its packs: what we have, what is missing, and the phases

**Date:** 2026-10-29. **Status:** analysis and plan. Every fact below is tagged VERIFIED (read
from a pack, a kernel listing, the generation listing or a manual, with the place named),
INFERRED or OPEN. Numbers are octal unless marked dec.

**The question.** Can we understand each SINTRAN segment, follow the boot from the page-0
bootstrap to the background programs, know where the NPL sources we have went, and from there
recreate SINTRAN source (NPL plus symbols) well enough to build new install packs with our own
NPL compiler?

**Short answer.** Yes for the resident kernel, whose source we hold and whose compiler we have
rebuilt byte-exact; it still needs the generation and link steps and a byte-exact comparison
against a pack. No for about half of the system today: the file system, command processor,
RT-loader, error program, DMAC, service program, XMSG, servers, ND-500 monitor, NEW-SYSTEM and
MACM exist only as binaries, and the reverse direction (binary to NPL) is a design note with
nothing built. The disk side is solved: `ndtool` lists, exports and imports any segment of any
pack and changes a pack's identity, so every phase below can be measured on real packs.

Related chapters: [OS/11](OS/11-RT-SEGMENTS-AND-SEGFIL.md) segments and segment files,
[OS/22](OS/22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md) tables and the name records,
[OS/26](OS/26-INITIAL-COMMAND-BUFFER-ON-DISK.md) and [OS/28](OS/28-CPU-NUMBER-AND-TYPE-ON-DISK.md)
offline edits, [NPL-SOURCE/NPL-COVERAGE-AND-GAPS.md](NPL-SOURCE/NPL-COVERAGE-AND-GAPS.md) what
source exists, [CARVING-HANDOFF.md](CARVING-HANDOFF.md) the static carving effort. The compiler
lives in the sibling repository `new-planc` (`src/npl`, `docs/npl`).

---

## 1. What a pack holds (VERIFIED on K and L packs, 2026-10-29)

| Disk pages (dec) | NDFS file | What |
|---|---|---|
| 0 | boot block | page-0 bootstrap plus the directory label; SINTRAN rewrites the bootstrap at every start (PH-P2-OPPSTART.NPL 867-876) |
| 1-63 | `(SYSTEM)SINTRAN:DATA` | the kernel's "segment file 4": SAVE copies with absolute addresses: 52 S3SAVE (common/start code, 27 pages, at page 1), 53 S3SDPIT (at 28), 54 S3SSYS, 55 S3SERRP (error program, at 100), 60 S3SERD |
| 64-127 | `(SYSTEM)MACM-AREA:DATA` | more of segment file 4: 56 S3SRTC (RT-loader code, at 137), 57 S3SRTD, 63 S3MEMTF |
| 128 up | `(SYSTEM)SEGFIL0:DATA` | segment file 0: everything else, starting with 2 S3IMAGE at page 0 (the memory image the bootstrap loads; byte-identical to S3SAVE after a cold start) |

The segment table (segments 27 S3ISGT image, 24 S3SSGT save) describes 1-255 with LOGAD, SEGLE,
MADR (page in its segment file), FLAG (file number in bits 13-15) and status. The names are the
RT-loader's type-25B records in `(SYSTEM)RTFIL:DATA`. The kernel finds a segment file through
DBLST(N)/ABLPAGE(N) (256 blocks / 2 = disk page 128 for file 0; file 4 is set to one page at
start-up, OPPSTART:751). `ndtool --segments` prints all of this from the pack; `--export-segment`
and `--import-segment` move a segment's pages to and from a host file (sibling repository
`norskdata-ndfs`, `ndfs-c/src/sintran_segments.c`).

## 2. How the system boots (VERIFIED from PH-P2-OPPSTART.NPL and the System Supervisor manual)

1. **Firmware load**: STOP, MCL, LOAD; the ND-100 mass-storage load reads 1 KW from disk address 0
   to memory 0 and starts there (ND-06.014.2A, quoted in Filesystem/boot-creation.md:61-63).
2. **Bootstrap** (RELOA, OPPSTART 3712-3766): PIOF, moves itself to 177000, reads NOBLK sectors
   from DYBLS = DBLST(0) = SEGFIL0 page 0, i.e. segment 2 S3IMAGE, 77 pages of "image of common,
   start and restart code" (s3vs-4.symb 79729-79730), then `IDENT PL11; JMP I (SINTR`. Destination
   physical 0 (INFERRED; the manual says common code starts at physical 0, SUP 15437).
3. **SINTR** (OPPSTART 292-325): interrupt system off, PCR, ND-100 check, level 0. DPRE reads the
   DPIT (55 pages) from the SAVE copy S3SDPIT when HENTFLAG = 0 (cold start) or from the IMAGE copy
   S3IDPIT otherwise (262, 283-284). Then page tables, MMS-II test, SYSEVAL (CPU type), memory scan,
   device presence tests, swap device.
4. **Cold start only**: 32 CRWDISC save-to-image copies (OPPSTART 772-841): extended common, DPIT,
   RPIT, MPIT, IPIT, segment table, file system, RT-loader code and data, error program, edit page,
   command segment, SM, system segment, 5PIT, XMSG kernel and XROUT, device names, servers, the
   ND-110/ND-120 microcode segments, ND-500 monitor. Plus the MADR set-up of spool, ND-500, RFA,
   debugger and background system segments. (Where HENTFLAG is set: OPEN.)
5. **Both paths**: read segment table, extended common, RPIT, MPIT, IPIT, segment 42, system
   segment, 5PIT from the image copies; microcode image if UCLOAD; terminal and TAD datafields;
   background programs BAKnn/BCHnn get SEGM1 = 3 (the command segment) and SEGM2 = their own system
   segment (OPPSTART 2534-2540); SGBUILD builds the memory-only segments 23, 47, 35, 67, 51, 64, 42.
6. **SETPTABL** (PH-P2-RESTART.NPL 454-685): LOCOSTORE loads or compares the ND-110/ND-120
   control store from the microcode segment; maps common, RPIT, MPIT, IPIT, DPIT, 42 and 5PIT into
   the page tables; sets PCR on all levels; register blocks for DUMMY, STSIN and 1SWAP; `GO PENT0`.
7. **After start**: STSIN is the start RT program; the initial commands in INIBU (segment 3) run
   (ENTER-DIRECTORY, APPEND-BATCH LOAD-MODE), LOAD-MODE starts batch, spooling, XMSG/COSMOS, UE,
   ND-500, SET-AVAILABLE. Background programs BAK01.. run the command processor in segment 3 S3CP
   (S3COM on K) through SPIT; file-system calls go to segment 6 S3FS through FPIT.
8. **Cold start from the operator side**: `@COLD-START`, or MACM `)HENT` + `22!` without a running
   system; the save area is copied to the image area and HENT-MODE runs (SUP 3787-4041).

## 3. Which segment holds what (VERIFIED: L release information 2497-2598, s3vs-4.symb 79870-80191, the L carve)

| Segment | Name | Holds | Source we have? |
|---|---|---|---|
| 2 / 52 | S3IMAGE / S3SAVE | common code, start and restart program (the memory image) | yes: CC-P2-COMMON, CC-P2-N500, PH-P2-START-BASE, PH-P2-RESTART, PH-P2-CONFG-TAB, PH-P2-OPPSTART |
| 23 / 44 / 53 | S3DPIT / S3IDPIT / S3SDPIT | resident data: variables, datafields, RT descriptions, the system information table, segment-file tables | yes: DP-P2-VARIABLES plus the inline generation text (s3vs-4.symb 79720-80200) |
| 47 / 25 / 16 | S3RPIT and its image/save | resident code, MON call workers | yes: RP-P2-* |
| 35 / 26 / 17 | S3MPIT | monitor level, level 14, drivers, segment administration | yes: MP-P2-* |
| 67 / 66 / 65 | S3IPIT | IPIT code | yes: IP-P2-* |
| 51 / 50 / 46 | 5PIT | ND-500 MON 60 | yes: 5P-P2-MON60 |
| 64 / 61 / 60 | S3ECOM | extended common | yes: XC-P2-1, XC-P2-2, XC-P2-N500 |
| 3 / 13 | S3CP (K: S3COM) | command processor, INIBU, 9ENTO | **no** |
| 6 / 12 | S3FS | file system | **no** |
| 4, 37 / 56, 57 | S3RTL, S3RTD | RT-loader code and data | **no** |
| 14 / 55, 5 | S3ERRP, S3ERRS | error program | **no** |
| 7 | S3DMAC | DMAC, loaded by HENT-MODE | **no** |
| 71 / 70 | S3SM | SINTRAN-SERVICE-PROGRAM, MAIL | **no** |
| 76, 77, 103 | XMSG kernel, XROUT, FIDO | XMSG | **no** |
| 30 / 62, 20, 21 | S3SM5, S3SDT5, S3NMS5 | ND-500 monitor, domains, name tables | **no** |
| 104-127 | NUCLEUS, microcode, ERS, servers | servers; the ND-110/ND-120 microcode segments | microcode: the micro code listings exist (NDMicroCpu); servers: **no** |
| 43 | S3PATCH | addresses for the patch mode file | n/a |
| 63 | S3MEMTF | memory dump to floppies | yes: PH-P2-MEMTOF (INFERRED by name) |

The prefixes CC, XC, DP, RP, MP, IP, 5P match the split markers `%$--:COMMON/RPIT/MPIT/IPIT/5PIT/DPIT`
in the generation listing (INFERRED; P2 = "part 2" is attested; PH is OPEN). Two cautions: the
listing we hold (s3vs-4) is **not the L07 build** (addresses differ, e.g. M1 071455 vs 071633B)
although its disk layout and module grouping match the L carve exactly; and some drivers in the
listing were never split into NPL files (BDISK, SCSWD, BFDIS, STC).

## 4. The tool chain today (VERIFIED, inventory of 2026-10-29)

- **NPL compiler** `npl` (new-planc, C, about 4,350 lines): reproduces NPL-1896D's MAC text byte
  for byte on 1378 probes, 44 of 45 s3vs-4 units and 25 of 25 version-J units. Its `mac -B`
  produces BRF objects identical to the real MAC on 622 of 622. Oracle lane runs the real compiler
  under nd100x. Language server and VS Code extension exist.
- **Not built**: FMAC (the macro assembler the generation runs through), the SIN-GEN prelude (the
  units compile with a stand-in), any link of units into a segment image, and any compile-link-
  compare against a carved pack. "Reverse NPL" (binary plus symbols to NPL) is a design note
  (`new-planc/docs/npl/reverse-npl.md`, "Nothing here is built").
- **Disassembly**: nd100_disasm.py (`--sym`), the carver (79 L07 segments carved, 70 with .asm,
  216 MON calls indexed, 91 workers verified), Ghidra ND-100 processor (loaders for BPUN, PROG,
  BRF; decompiler not reliable), nd100-dis (no symbol lists), RetroCore LOADSYM/LOADKSYM.
- **Symbols**: SYMBOL-1/2-LIST, FILSYS, RTLO, N500, XMSG lists for J, K03, L07, M06; names cut to
  5 characters, octal values, offsets mixed with addresses. Every pack carries its own lists.
- **Disk**: ndtool (segments, identity, initial commands, release, create, fsck) in C with Python,
  TypeScript and C# ports planned (`norskdata-ndfs/docs/CPU-IDENTITY-PLAN.md`).

## 5. Phases

Each phase ends with a measurement on a real pack or in an emulator, never with agreement between
two of our own tools.

**Phase 0 (done 2026-10-29).** Segment table, names, segment files, export, import and CPU
identity readable and writable offline for every generation (`ndtool`). Boot flow and segment map
written down (this document, chapters 11, 22, 28 corrected).

**Phase 1. Ports and proofs of the disk tools.** Python, TypeScript and C# (RetroIO.Storage.Ndfs;
RetroCore's old NDFS layer has the wrong checksum) get the same segment and identity code with the
same tests; import proven by booting a pack with a re-imported S3SDPIT; a pack with a defined
segment file 1 made on a booted copy to prove the DBLST(1) path. (Plan file: norskdata-ndfs
`docs/CPU-IDENTITY-PLAN.md`.)

**Phase 2. Match a listing to a pack.** We need one pack whose build matches a listing we hold.
Candidates: find whether any pack's `SYMBOL-1-LIST` equals s3vs-4's symbol values (the L packs do
not: M1 differs), or the version-J build (NPL-SOURCE-2) against a J pack if one exists. Without a
match, phase 3 can only be measured module by module with address relocation. Deliverable: a table
listing-build versus pack, with the symbol-list diff.

**Phase 3. Rebuild the resident kernel from source, byte-exact.** Compile the units we have with
`npl`, assemble with `mac -B`, then the missing steps: the real SIN-GEN prelude instead of the
stand-in, FMAC, and a linker that lays the units into the S3IMAGE / DPIT / RPIT / MPIT / IPIT / 5PIT
images at the listing's addresses. Measure with `ndtool --export-segment` of the matching pack:
first the small ones (S3ECOM 2 pages, 5PIT 5 pages), then RPIT, MPIT, IPIT, S3IMAGE, DPIT. Byte-
exact means the compiler, the prelude and the link are right; a differing word names a defect in
one of them. Then `--import-segment` the rebuilt save copies into a copy and cold-start it in
RetroCore and nd100x. End state: a kernel we can change in NPL and boot.

**Phase 4. Reverse NPL for the segments without source.** Build `npl-rev` as the design note
describes: the compiler's tables read backwards, symbol lists for names, the carver's code/data
separation and B-register (datafield) context as inputs. Start where it is cheapest to check: the
error program (S3ERRP, 20 pages, with S3SERRP as the save copy), the edit page (S3ED, 1 page), then
S3FS (65 pages; the carver already has 91 verified MON workers and FILSYS-SYMBOLS), then S3CP. The
only acceptance test is recompile and byte-compare with the export. Lost for good: comments, long
names, `)KILL`ed locals; those are written fresh and marked.

**Phase 5. The rest of the system.** RT-loader (S3RTL/S3RTD), DMAC, SINTRAN-SERVICE/MAIL, XMSG
kernel and XROUT (the XMSG wire protocol is already documented in SINTRAN/XMSG), the servers, the
ND-500 monitor; same method, same test. The microcode segments come from the NDMicroCpu listings.

**Phase 6. New install packs.** With phases 3-5 byte-exact, generate a pack: `ndtool --create`
(already byte-identical to `@CREATE-DIRECTORY`), the three files SINTRAN:DATA, MACM-AREA:DATA,
SEGFIL0:DATA at pages 1, 64, 128, every segment imported at its MADR, symbol lists, RTFIL name
records, patch files, mode files, the identity set with `--set-cpu`; boot in both emulators;
NEW-SYSTEM and MACM remain binaries carried over until phase 5 covers them.

## 6. What we do not know yet (OPEN)

- Where HENTFLAG is set, and what MACM `)HENT` / `22!` read.
- PENT0, the STSIN START code and the "SINTRAN III RUNNING" text: not in any source we hold.
- Whether the page-0 RELOA of the L packs equals s3vs-4's (the first words differ).
- The meaning of the PH prefix; segment FLAG 162010 versus 162000; the STSIN SEGM fields.
- What reads FCPUN; what word 107017 is in the L builds (chapter 28).
- Which build the s3vs-4 listing is; whether any pack on hand matches it (phase 2).
