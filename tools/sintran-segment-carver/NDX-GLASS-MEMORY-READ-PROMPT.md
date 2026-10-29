# Prompt for the nd100x LLM — read RT + segment listings from memory (glass web)

Copy everything below the line to the Claude working on the nd100x emulator
(the sibling repository `nd100x`). Goal: the glass WASM web UI should show the SINTRAN
RT-program list and segment table by reading them **live from emulated memory**,
version-aware, instead of relying on hardcoded/AI-derived JSON name data.

> **Corrections 2026-10-29.** Three things in this prompt were superseded by measurements on
> real K and L packs (chapter 22 §3.6, §6.4, §6.5; chapter 28 §4): the name records are
> **8 words**, not 6, and their packing is decoded (SIXBIT, base 64, chapter 22 §6.5); the same
> records are on disk in `(SYSTEM)RTFIL:DATA`, so names can be read offline too; and a
> segment's disk location is `DBLST(N)/ABLPAGE(N) + MADR + P` with `MADR` in 1024-word pages
> (`DBLST(0) = 256` blocks, `ABLPAGE(0) = 2` measured, so `SEGFIL0` starts at disk page 128) -
> the older `CBLST + MADR` / `×512` model in the glass tests is wrong. Notes at the places below.

---

You are working in the `nd100x` repository (ND-100/CX emulator, C→WASM, with a
browser "glass" frontend under `template-glass/`). Make the SINTRAN inspectors
source their data from **emulated memory**, not from static JSON/JS name tables.

## Read these first (full paths)
- `SINTRAN/OS/22-READING-RT-AND-SEGMENT-TABLES-FROM-MEMORY.md`
  — the complete, verified memory-read recipe (version detection, root pointers,
  entry layouts, DPIT translation). This is the authority; follow it.
- `SINTRAN/OS/23-MON-CALL-DISPATCH-DEVELOPER-GUIDE.md`
  — context on how kernel structures are reached (levels, DPIT vs physical).
- Per-version SINTRAN symbol tables (the ONLY source of human-readable names):
  `SINTRAN/NPL-SOURCE/SYMBOLS/K03/`
  `SINTRAN/NPL-SOURCE/SYMBOLS/L07/`
  `SINTRAN/NPL-SOURCE/SYMBOLS/M06/`
  (`SYMBOL-1-LIST.SYMB.TXT`, `SYMBOL-2-LIST.SYMB.TXT` — lines `NAME=octaladdr`.)

## Core principle
Everything **structural/numeric** is in memory and must be read from there:
segment table (numbers, LOGAD, SEGLE, MADR, FLAG, SGSTA, BPAGL), RT descriptions
(priority, status, assigned/active segment), and the running version. The **only**
thing not in memory is human-readable **names** — SINTRAN RT descriptions carry no
name field, and segment names are not in the segment table. Names come from the
matching version's symbol table, keyed by the version detected in memory.

## Facts to implement (all VERIFIED in doc 22 — cite it, don't re-derive)

1. **Version detection from memory.** `SINVER0` at logical `004055₈` (`0x82D`):
   low byte `& 0x7F` = version letter (K/L/M...), bits 8-10 = OS type. Generation
   date in `GENDAT0..4` (`004060₈`-`004064₈`). Use the letter to pick K03/L07/M06.
   The boot banner is just the printed form of these cells — read the cells.

2. **Root pointers are byte-identical across K03/L07/M06** (verified by grep of all
   three `SYMBOL-1-LIST`), so hardcode ONE set (no per-version pointer lookup):
   `RTSTA=004020`, `RTEND=004323`, `SGMAX=004015`, `SEGTB=004320`, `SEGST=004321`,
   `CORMB=004322`, `SINVER=004055`, `5RTSI=000026` (RT stride).

3. **Segment table read.** `SGMAX` is a direct max-segment-number value.
   `physBase = (SEGTB<<16) + SEGST` is a physical **word** address (L07: bank 3,
   `0o124000` → `0x3A800`). Walk `SGMAX+1` entries of **8 words**; field offsets:
   `SEGLI=0, PRESE=1, LOGAD=2, SEGLE=3, MADR=4, FLAG=5, SGSTA=6, BPAGL=7`.
   **Load address (words) = `LOGAD × 1024`** (LOGAD is a page/VPN, not a word addr).
   SEGFIL number = `(FLAG >> 13) & 7`.

4. **RT-program list read.** `RTSTA`/`RTEND` are pointer cells; entry count =
   `(RTEND - RTSTA) / 22`, stride `5RTSI = 26₈ = 22` words. Field offsets in each
   RT description: `STATU=1` (bit `USED=1` selects live entries), `PRITY=3`
   (priority), `SEGM1=011/SEGM2=012` (assigned segment numbers), `ACT1S=014/
   ACT2S=015` (active segment numbers), `STADR=010`, P-register via `RTDLG=025`.
   There is **no name field** — get the name from the symbol table (below).

5. **DPIT access (portable).** The root cells are logical addresses mapped through
   DPIT = PIT #7. Translate live: `vpn = logical>>10; ppn = getPageTableMap(7)[vpn];
   phys = ppn*1024 + (logical & 1777₈)`. Do NOT hardcode a physical page — derive
   it from the live page table so it works on any image/version.

## What every 8-word segment entry gives you (all live from memory, no name)
Per segment (join to the UI row by segment number = entry index):
| word | field | meaning for the UI |
|------|-------|--------------------|
| 0 | `SEGLI` | segment-link (chain), rarely shown |
| 1 | `PRESE` | present/reserve flag |
| 2 | `LOGAD` | load **page**; **load word address = `LOGAD × 1024`** |
| 3 | `SEGLE` | length in **pages** (1 page = 1024 words = 2048 bytes; size = `SEGLE × 1024` words) |
| 4 | `MADR`  | page offset inside its segment file `N = FLAG >> 13` (for file 0: byte offset `MADR × 2048` in `SEGFIL0:DATA`; disk page `DBLST(N)/ABLPAGE(N) + MADR`); `0` = memory-resident, no disk image |
| 5 | `FLAG`  | SEGFIL number = `(FLAG>>13)&7`; low bits = attribute flags (`5OK/5INHB/5SREE/5FIXC` per `SYMBOL-2-LIST`) |
| 6 | `SGSTA` | status word (in-core / on-disk / in-transfer …) |
| 7 | `BPAGL` | base physical page when resident |

So the inspector can show number, load address, size, disk location, SEGFIL,
attribute flags, status, and residency **entirely from memory**. Only the *name*
is absent from this table.

## Names — the two kinds have DIFFERENT sources (VERIFIED, important)
- **RT-program names ARE in the symbol table.** The symbol's value equals the
  RT-description address: `DUMMY=012071`, `STSIN=012117`, `RWRT1=012501`,
  `ACCRT=012377` … So for each RT slot at `RTSTA + n*26₈`, look up the symbol whose
  value equals that address. Parse the detected version's `SYMBOL-1-LIST` +
  `SYMBOL-2-LIST` into `{octalAddr → NAME}` and resolve. This is a live
  memory-address → name join; keep it, drop the hardcoded RT name array.
- **System-segment names are NOT in the symbol table.** `S3FS`/`S3CP`/`S3IMAGE`
  do **not** appear in any `SYMBOL-*-LIST`. At runtime they exist only in the
  RT-loader's packed `PSGNA` table (6-word records keyed by segment number,
  mapped only while the RT-loader runs). So do **not** try to get segment names
  from the symbol table. Instead ship a small **per-version segment
  number→name map** captured from `@RT-LOADER LIST-SEGMENT` (names are fixed per
  SINTRAN version); an example L07 map is
  `tools/sintran-segment-carver/versions/L-VSX-500/inputs/list-segment.txt`.
  (Optional advanced path: decode the live `PSGNA` packed-name table for
  fully-dynamic names — needs RE of the ND name packing.)
  **Corrections 2026-10-29:** the records are **8 words** (words 0-2 packed name, 3 = segment
  number, 4 = 0, 5 = 25B "DEFINED SEGMENT NAME", 6 = segment number, 7 = 0), the packing is
  SIXBIT = ASCII & 0x3F right-justified base 64 (decoded, chapter 22 §6.5), and the records are
  also in the plain file `(SYSTEM)RTFIL:DATA` on disk - 74 on the K pack, 98 on the L packs, so
  the set is per pack, not only per version. The "advanced path" is therefore the normal path.
- Select the right symbol set / segment-name map by the memory-detected version
  letter (§ version detection). This replaces the AI-derived JSON.

## Files to change (glass frontend)
- `template-glass/js/sintran-symbols.js` — already defines the FIXED root pointers
  (`SGMAX 0x80D`, `SEGTB 0x8D0`, `SEGST 0x8D1`, `RTSTA`, `RTEND`) and DPIT read
  helpers. Extend it with `SINVER` and the symbol-table name maps per version.
- `template-glass/js/sintran-segments.js` — already walks the segment table from
  memory; make sure it uses `LOGAD×1024` for load address and takes names from the
  symbol map, not from `sintran-seg-names.js`.
- `template-glass/js/sintran-rt-names.js` — **replace the hardcoded RT name/desc
  arrays** with symbol-map lookups keyed by RT-description address.
- `template-glass/js/sintran-seg-names.js` — **replace the hardcoded segment-name
  array** with the symbol map (or LIST-SEGMENT parse), version-keyed.
- version detection (`template-glass/js/sintran.js` or wherever `versionLetter`
  lives) — read `SINVER0` from memory instead of inferring from the banner.

## Acceptance
- With no JSON/hardcoded name arrays, the RT and segment inspectors still show
  correct names + all structural fields, driven by live memory + the version's
  symbol table.
- Switching the booted image between SINTRAN versions (K/L/M) auto-selects the
  right symbol set from the memory-detected version letter.
- `logical-device-numbers.json` may remain (it is a genuine LDN label lookup, not
  structural SINTRAN data) — leave it.
