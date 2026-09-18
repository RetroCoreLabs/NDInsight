# ND-210761B — C-Compiler for ND-500, version B

> Status: VERIFIED (transcribed from PD sheet; not yet run live)   ·   Install source: [PD]

| Field | Value |
|-------|-------|
| Part number | `210761B` |
| Base product | [`ND-210761`](../README.md) |
| Version | B |
| Release date | 86.10.16 (16 Oct 1986) — first official version of this product |
| CPU target | ND-500 |
| OS requirement | SINTRAN III VSX, version >= J |

## Description
Compiler for the programming language C, targeting the ND-500. This B-revision is the PD sheet's
own "first official version of this product" — the Error Correction / Changes sections list fixes
against a pre-release build (bad floating-point constant compilation, unreported missing
`#endif`s, large-structure debug-mode failures, `sscanf()` reliability, random-access write bugs
past EOF, invalid debug info) plus two additions: `@filename` command-line-length workaround, and
a new `tused()` library function wrapping the SINTRAN `TUSED` monitor call. [PD]

## Prerequisites
- **Hardware:** ND-500. [PD]
- **Software / OS:** SINTRAN III VSX, version J or later. [PD]
- **Mass storage for install:**

  | User | User space | Number of files |
  |------|-----------|------------------|
  | `<Any>` | 200 pages | 3 files |
  | `<C-Include>` (create if missing) | 50 pages | 13 files |
  | `SYSTEM` | 40 pages | 2 files |
- **Mass storage permanent (after install):**

  | User | User space | Number of files |
  |------|-----------|------------------|
  | `<domain user>` | 200 pages | 3 files |
  | `<C-Include>` | 50 pages | 13 files |
  | `SYSTEM` | 35 pages | 2 files |
- **Dependency products:** none stated on the PD sheet, but two are needed in practice: the
  ND-500 Linkage-Loader (`ND-10319`) for the final `COPY-DOMAIN` step, and
  [ND-210337 Backup-System](../../ND-210337/README.md) — installing the Linkage-Loader itself is
  documented as hard-blocked without Backup-System already present, see
  [../../../Installation/INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md](../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md). `[INF]`

## Release package (ND Software Library — 4 parts)

| Part | What it is | This release |
|------|-----------|--------------|
| **Program Description** (PD-sheet) | 4-page document: metadata, error/changes log, install procedure, floppy directory listing — all in one | [../../../Installation-Description/ND-210761-2-EN.md](../../../Installation-Description/ND-210761-2-EN.md) |
| **Installation** | folded into the PD sheet (page 3) | see below |
| **Diskette** | floppy directory listing (page 4) | see "Distribution media" below |
| **Revision Log** | PD sheet §1–2 ("Error Correction" / "Changes / Addition") | summarized in Description above |

## Distribution media

Two alternative distribution forms — use whichever floppies you have: [PD]

| Floppy volume(s) | Density | Contents |
|-------------------|---------|----------|
| `210761B00-XX-01D` | Double | single disk, all 21 files (`DESCRIPTION-FILE`, `INSTALL-10A-B00:MODE`, `INSTALL-10B-B00:MODE`, `CC-HEADER-A-B00:NRF`, `CC-LIBRARY-A-B00:NRF`, `CC-500-B00:LINK`/`:PSEG`/`:DSEG`, `CAT-B00:C`, and 12 `500-*-B00:H` include files) |
| `210761B<rev>-XX-01S`, `-02S`, `-03S` | Single (3-disk set) | disk 1: `INSTALL-1SA-B<rev>:MODE` (compiler); disk 2: `INSTALL-2S-B<rev>:MODE` (renamed via Linkage-Loader `RENAME-DEFAULT`); disk 3: `INSTALL-3S-B<rev>:MODE` (C-Include headers) |

`<rev>` in the single-density file names is the current revision level (printed literally as
`<rev>` on the PD sheet — substitute the actual revision digits from the floppy label you have).

## Installation procedure

Source: PD sheet page 3 "Installation Procedure", verbatim. Two procedures are given — pick the
one matching the physical media you have. [PD]

### Double-density diskette (`210761B00-XX-01D`)

1. Log in as user `SYSTEM`; create user `<C-Include>` with 50 pages if it does not already exist.
2. ```
   @ENTER-DIRECTORY 210761B<rev>-XX-01D,FLOPPY-DEVICE-<device>,<unit>,
   @MODE (210761B:FLOPPY-USER)INSTALL-1DA-B:MODE,...
   ```
3. Log in / switch to user `<C-Include>`:
   ```
   @MODE (210761B:FLOPPY-USER)INSTALL-1DB-B:MODE,...
   @RELEASE-DIRECTORY 210761B<rev>-XX-01D
   ```

### Single-density diskettes (3-disk set)

1. Log in as user `SYSTEM`; create a new user `<directory:dummy-user>` with 250 pages and user
   `<C-Include>` with 50 pages, if they do not already exist.
2. Disk 1:
   ```
   @ENTER-DIRECTORY 210761B<rev>-XX-01S,FLOPPY-DEVICE-<device>,<unit>,
   @MODE (210761B:FLOPPY-USER)INSTALL-1SA-B:MODE,...
   ```
3. Switch to `<Dummy-user>`, disk 2 (renames the compiler via the Linkage-Loader):
   ```
   @MODE (210761B:FLOPPY-USER)INSTALL-1SB-B:MODE,...
   @RELEASE-DIRECTORY 210761B<rev>-XX-01S
   @ENTER-DIRECTORY 210761B<rev>-XX-02S,FLOPPY-DEVICE-<device>,<unit>,
   @MODE (210761B:FLOPPY-USER)INSTALL-2S-B:MODE,...
   @ND LINK-LOADER
   N1:RENAME-DEFAULT (<directory:dummy-user>)
   N1:EXIT
   @RELEASE-DIRECTORY 210761B<rev>-XX-02S
   ```
4. Switch to `<C-Include>`, disk 3 (headers):
   ```
   @ENTER-DIRECTORY 210761B<rev>-XX-03S,FLOPPY-DEVICE-<device>,<unit>,
   @MODE (210761B:FLOPPY-USER)INSTALL-3S-B:MODE,...
   @RELEASE-DIRECTORY 210761B<rev>-XX-03S
   ```
5. **Result:** the compiler now lives on user `<dummy-user>`. Copy it to a real `<domain-user>`
   with `COPY-DOMAIN` in the ND-500 Linkage-Loader.

> This product installs into an ND-500 **domain** (not a reentrant SINTRAN III subsystem, unlike
> Subsystem Package II) — there is no `@DUMP-REENTRANT` step and nothing to hook into
> `HENT-MODE`/`LOAD-MODE`. It is a per-domain-user install; every user who compiles C needs the
> compiler domain copied/available to them via the Linkage-Loader.

## Configuration / post-install
No start command, no boot-mode hook. Verify by compiling a trivial C program per the CC-100/CC-500
User Manual (`ND-60.214.01`).

## Documentation
- PD-sheet: [../../../Installation-Description/ND-210761-2-EN.md](../../../Installation-Description/ND-210761-2-EN.md)
- PI-sheet: not located
- Manual(s): `ND-60.214.01` CC-100 and CC-500 C-Compiler User Manual
- NDWIKI: not checked yet

## Provenance & open items
- Source: single OCR'd PD-sheet scan (`ND-210761-2-EN.md`), not cross-checked against a second
  independent scan (unlike ND-210400B, only one copy of this document was found in the archive).
- **TODO:** confirm whether the ND-500 Linkage-Loader is a hard prerequisite for `COPY-DOMAIN`, or
  whether some other mechanism exists — not stated on the PD sheet, marked `[INF]` above.
- **TODO:** this install has not yet been run live in the emulator.

---
**Parent:** [../README.md](../README.md) (`ND-210761` product overview)
