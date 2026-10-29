# SINTRAN III OS Installation

**Installing the SINTRAN III operating system on a fresh disk from distribution floppies.**

The install is a **shared skeleton + per-version deltas**. The phase documents below
describe the general procedure once; the [version pages](#per-version-guides) record only
what differs for each release; the [golden-disk dumps](floppy-contents/README.md) are the
verification reference.

---

## The procedure at a glance (the phases)

| # | Phase | Doc | Primary source |
|---|-------|-----|----------------|
| 0 | Concepts & terminology (MACM, save-area, phases) | [00-INSTALL-CONCEPTS.md](00-INSTALL-CONCEPTS.md) | install-log.txt |
| 1 | Disk devices & how they map to CREATE-DIRECTORY | [01-DISK-DEVICES.md](01-DISK-DEVICES.md) | System initialisation.txt, K05 FLOPPY/readme |
| 2 | Bootstrap: load OS floppy → disk (MACM) | [02-BOOTSTRAP-MACM.md](02-BOOTSTRAP-MACM.md) | SINTRAN-H/Admin/install-log.txt |
| 3 | File-system initialisation (users, files, segments) | [03-FILESYSTEM-INIT.md](03-FILESYSTEM-INIT.md) | System initialisation.txt |
| 4 | S3 configuration (system generation) | [04-S3-CONFIGURATION.md](04-S3-CONFIGURATION.md) | S3-CONFIGURATION:PROG/CNFG on disk |
| 5 | Applying patches | [05-PATCHES.md](05-PATCHES.md) | ND-PATCH-SIN-*.txt, PATCH-LOG.txt |
| 6 | Startup & runtime/terminal configuration | [06-STARTUP-AND-TERMINAL-CONFIG.md](06-STARTUP-AND-TERMINAL-CONFIG.md) | HENT-MODE.txt, START-SINTRAN-MULTIUSER.TXT |
| 7 | Disk layout & what CREATE-DIRECTORY does | [07-DISK-LAYOUT-AND-CREATE-DIRECTORY.md](07-DISK-LAYOUT-AND-CREATE-DIRECTORY.md) | BIGDISK0-*.txt |
| 8 | Automatic boot: mode files & INITIAL-COMMANDS | [08-AUTOMATIC-BOOT-INITIAL-COMMANDS.md](08-AUTOMATIC-BOOT-INITIAL-COMMANDS.md) | HENT-MODE.txt (`@CC HENT-MODE:MODE`) |

> **Consolidated boot/startup guide + ready-to-use mode files.**
> [SINTRAN-BOOT-AND-MODE-FILES-GUIDE.md](SINTRAN-BOOT-AND-MODE-FILES-GUIDE.md) narrates phases 6 & 8
> end-to-end (cold vs warm start, INITIAL-COMMAND chain, `HENT-MODE`/`LOAD-MODE`, XMSG network
> config incl. include files, and `DUMP-REENTRANT`). Tailored, drop-onto-the-machine files are in
> [mode-files/](mode-files/README.md).

---

## Cross-cutting dimensions

- **CPU type / ID** — asked by NEW-SYSTEM from K on ("Give CPU number (in decimal)", "Give CPU
  type (in decimal)"), written by the patch run into the save copy of the resident data (`S3SDPIT`:
  `SYSNO/ 33CPN`, `FCPUN/ 33CPN`, `HWINF+2/ 33CPU`), then a cold start. Where the words are and how
  to change them on a disk image:
  [`../../SINTRAN/OS/28-CPU-NUMBER-AND-TYPE-ON-DISK.md`](../../SINTRAN/OS/28-CPU-NUMBER-AND-TYPE-ON-DISK.md).
- **Floppy file-system identity** — each distribution floppy is itself a SINTRAN file
  system; its "Directory name" (e.g. `N-220046K03--01D`) is its identity. See
  [floppy-contents/](floppy-contents/README.md).
- **Command alignment** — every command verb links to
  [`../../Operations/SINTRAN/OPCOM-COMMAND-REFERENCE.md`](../../Operations/SINTRAN/OPCOM-COMMAND-REFERENCE.md)
  and the System Supervisor manual.

---

## Subfolders

| Folder | Contents |
|--------|----------|
| [versions/](versions/README.md) | Per-version install notes (H, K, K05, L, M) - see also the table below |
| [floppy-contents/](floppy-contents/README.md) | Golden-disk and distribution-floppy content dumps (the verification reference) |
| [mode-files/](mode-files/README.md) | Ready-to-use, tailored mode files (HENT-MODE, LOAD-MODE, XMSG-START, DUMP-REENTRANT) |
| [SUBSYSTEM/](SUBSYSTEM/README.md) | Subsystem Package II (ND-210400) library-diskette documents |
| [research/](research/README.md) | Temporary working research notes (HDD image findings) |

---

## Per-version guides

Notes below are **verified facts only** (transcribed from the distribution archives). Blank = not yet verified.

| Version | Verified notes | Page |
|---------|----------------|------|
| H   | MACM banner `MACM-1718-K`; 2 floppies (DISKETTE-I/II); initialized for DISC-75MB / DISC-38MB | [versions/SINTRAN-H.md](versions/SINTRAN-H.md) |
| K   | golden disk `BIGDISK0-K` (PACK-ONE, 38400 pages); floppy VSXK1 carries `MACM-1718L:BPUN` | [versions/SINTRAN-K.md](versions/SINTRAN-K.md) |
| K05 | `FLOPPY\readme.txt`: "D version" — no ST-506/Winchester, has SCSI | [versions/SINTRAN-K05.md](versions/SINTRAN-K05.md) |
| L   | 3 VSX floppies (VSXL1/2/3); `START-SINTRAN-MULTIUSER.TXT`; XMSG symbols | [versions/SINTRAN-L.md](versions/SINTRAN-L.md) |
| M   | `System initialisation-WD0.txt` variant; `HENT-MODE.txt`; `PATCH-LOG.txt`; XMSG | [versions/SINTRAN-M.md](versions/SINTRAN-M.md) |

---

**Parent:** [../README.md](../README.md)
