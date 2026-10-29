# Recreating SINTRAN III from its packs: the plan

**Date:** 2026-10-29. **Status:** plan. Facts live in the chapters; this file holds the open work
and the phases only.

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

**Where the facts are** (moved out of this file on 2026-10-29):
- what a pack holds, segment files, save/image/running copies: [OS/11](OS/11-RT-SEGMENTS-AND-SEGFIL.md)
- how the system boots, stage by stage: [OS/01](OS/01-BOOT-SEQUENCE.md) Part A
- which NPL file is in which segment, the generation listing's disk layout and segment table:
  [OS/29](OS/29-SEGMENT-MAP-FROM-THE-GENERATION.md)
- every system segment by name and purpose, every page table, K to N:
  [OS/30](OS/30-SYSTEM-SEGMENTS-AND-PAGE-TABLES-BY-RELEASE.md)
- the tables in memory and the name records: [OS/22](OS/22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md)
- offline edits: [OS/26](OS/26-INITIAL-COMMAND-BUFFER-ON-DISK.md), [OS/28](OS/28-CPU-NUMBER-AND-TYPE-ON-DISK.md)
- what source exists: [NPL-SOURCE/NPL-COVERAGE-AND-GAPS.md](NPL-SOURCE/NPL-COVERAGE-AND-GAPS.md);
  the static carving effort: [CARVING-HANDOFF.md](CARVING-HANDOFF.md). The compiler lives in the
  sibling repository `new-planc` (`src/npl`, `docs/npl`).

---

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
