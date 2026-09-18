# ND-210337 — Backup-System

> Status: IN-PROGRESS

| Field | Value |
|-------|-------|
| ND article number | `ND-210337` |
| Product name | Backup-System |
| Functional category | Backup / Storage / Disk Utilities |
| ND doc-category tag | 80 Utility software [curated] |
| CPU target | ND-100 |
| OS requirement | SINTRAN III |
| Related products | `ND-10337` — older/base article number for the same product (versions B, F; see [ND-10337](../ND-10337/README.md)) |

## Description
The Backup System is Norsk Data's standard file-copy/backup subsystem for SINTRAN III — copying
files between users, disk, diskette, and magnetic tape, interactively, from a mode file, or from
a batch job. It provides `COPY-USERS-FILES`, `MULTIUSER-COPY`, `DEVICE-COPY`, and volume
create/list/delete commands. Full feature description:
[../../Product-Info/ND-210337-A1-EN.md](../../Product-Info/ND-210337-A1-EN.md). [PI]

## Why this matters for installing other products

This is a **hidden prerequisite** for several products already documented in this catalog — their
own install scripts call `@BACKUP-SYSTEM` directly, and the PD sheets never spell that out as a
formal dependency:

- [ND-210400 Subsystem Package II](../ND-210400/ND-210400B/README.md) — "Use the BACKUP-SYSTEM
  to copy all the files to the user where the BPUN-files are kept."
- [ND-210761 C-Compiler for ND-500 (CC-500)](../ND-210761/ND-210761B/README.md) — install steps
  are `@MODE`/`@ENTER-DIRECTORY` based, not BACKUP-SYSTEM, but the ND-500 domain copy path
  (`COPY-DOMAIN`) has the same "must already have a working file-copy subsystem" character.
- [ND-10760 C-Compiler for ND-100 (CC-100)](../ND-10760/ND-10760A/README.md) — `INSTALL-1:MODE`
  and `INSTALL-2:MODE` both open with `@BACKUP-SYSTEM` directly.
- The ND-500 Linkage-Loader install is documented as having this as a **hard, verified**
  prerequisite (the installer fails outright without it) — see
  [../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §2.3 and §3](../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md).

**Install Backup-System before any of the above**, if it is not already resident.

## Versions

| Version | Subfolder | Status | Notes |
|---------|-----------|--------|-------|
| I04 | not a separate subfolder here — see [../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §3](../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md) | **VERIFIED live** (RetroCore session, 2026-07-19) | floppy `210337I04-XX-01D`; the canonical, fully gotcha-documented procedure |
| I05 | [ND-210337I05](ND-210337I05/README.md) | IN-PROGRESS — adapted from the verified I04 session, not independently run | floppy `210337I05-XX-01D` |

## Documentation
- Program Description (PD-sheet) for the modern `21`-prefixed product: not located as a dedicated
  PD sheet — the closest is the general Product Information sheet.
- Product Information (PI-sheet): [../../Product-Info/ND-210337-A1-EN.md](../../Product-Info/ND-210337-A1-EN.md)
  (also documents the real BACKUP User Guide as `ND-60.250 EN` / `ND-60.250 NO`, not in this
  repo)
- Manual(s): `ND-60.250 EN` BACKUP User Guide — [../../../Reference-Manuals/ND-60.250.1_EN_BACKUP_User_Guide.md](../../../Reference-Manuals/ND-60.250.1_EN_BACKUP_User_Guide.md)
  · `ND-60.151.xx` SINTRAN III Utilities Manual (referenced by the older ND-10337B PD sheet)
- NDWIKI: not checked yet

## Provenance
Article number and PI-sheet content: `Product-Info/ND-210337-A1-EN.md`. I04 verified procedure:
live RetroCore session log, `INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md`. I05 floppy contents
confirmed against a local floppy-image reference catalog (temporary working reference, not
committed to this repo) — file set is identical in shape to I04's (`INST-BASY-I05:PROG`,
`RESERVE-SYSTEM:MODE`/`:BATC`, `BACKUP-SERV-I05:PROG`, `BACKUP-SYS-I05:PROG`,
`UE-ERMSG-EN-C05:ERR`), just one version letter later.

---
**Parent:** [../README.md](../README.md) (Software catalog)
