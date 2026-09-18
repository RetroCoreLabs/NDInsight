# ND-210337I05 — Backup-System, version I05

> Status: IN-PROGRESS — procedure adapted from a VERIFIED I04 live session; I05 itself not yet run   ·   Install source: [OBS] (file listing) + adapted [VERIFIED, different version]

| Field | Value |
|-------|-------|
| Part number | `210337I05` |
| Base product | [`ND-210337`](../README.md) |
| Version | I05 |
| Release date | unknown |
| CPU target | ND-100 |
| OS requirement | SINTRAN III (ND-500/5000 MONITOR environment confirmed working in the I04 session) |

## Description
Same product, one version letter newer than the fully verified I04 install documented in
[../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §3](../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md).
The floppy's file set is identical in shape — only the version-letter suffix on each file name
changed (`I04` → `I05`). No install text specific to I05 has been read (the installer is a
compiled `:PROG` executable, not a `:MODE`/`:BATC` script, so its dialogue cannot be extracted
with `ndtool` the way the CC-100 `:MODE` files were — it would need to be run live or
disassembled). This entry **transposes** the verified I04 procedure onto I05's file names; treat
it as high-confidence but not independently confirmed.

## Distribution media

| Floppy volume | Contents |
|----------------|----------|
| `210337I05-XX-01D` | `INST-BASY-I05:PROG` (installer, 75 pages) · `RESERVE-SYSTEM:MODE` · `RESERVE-SYSTEM:BATC` · `BACKUP-SERV-I05:PROG` (72 pages) · `BACKUP-SYS-I05:PROG` (170 pages) · `UE-ERMSG-EN-C05:ERR` (156 pages, error-message file) |

Confirmed via directory listing only (not mounted with `ndtool` — unlike the CC-100 floppies,
there is no plain-text `:MODE` install script here worth extracting; the installer itself is a
`:PROG` binary).

## Installation procedure (transposed from the verified I04 session)

Run the installer:
```
@(210337I05-XX-01D:FLOPPY-USER)INST-BASY-I05:PROG
```

Question-and-answer flow (as observed for I04 — expected identical for I05):

1. `Delete previous version ... (Y/N)` — Y/N answer.
2. `Please specify which user you want the files ... copied to (default: UTILITY)` — **this
   wants a USER NAME. Press plain CR to accept UTILITY.** Do not type `Y` here — the installer
   will take it as a literal user name and fail.
3. `Should the BACKUP-SYSTEM be dumped reentrant (Y/N) ?` — answer Y. The installer itself warns
   the following `NO SUCH FILE NAME` (from its own `@DELETE-REENTRANT BACKUP`) is expected on a
   first-time install, not a failure.

The installer copies `RESERVE-SYSTEM` files to `SYSTEM`, `BACKUP-SERV-I05`/`BACKUP-SYS-I05` to
`UTILITY`, the error-message file to `SYSTEM`, dumps `BACKUP-SYSTEM-I` reentrant from
`(UTILITY)BACKUP-SYS-I05:PROG`, and runs a `BACKUP-LOAD-I:MODE` job that loads the DMA-Server.

**Post-install — persist across a cold start (do not skip):**
```
Append to the DUMP-REENTRANT file on user SYSTEM:
  @DUMP-PROGRAM-REENTRANT BACKUP-SYSTEM-I, (UTILITY)BACKUP-SYS-I05:PROG

Append (SYSTEM)BACKUP-LOAD-I:MODE to the HENT-MODE file on user SYSTEM
```

**Verify:**
```
@LIST-REENTRANT
   START RESTART SEGMENT   NAME
      0B      1B    130B   BACKUP-SYSTEM-I

@BACKUP-SYSTEM
BACKUP-SYSTEM / I05  <date>
Ba-sy:
```

## Prerequisites
Same as observed for I04:
- User `UTILITY` must exist with >= 177 free pages, or the installer terminates immediately.
- Answer "default:" prompts with a plain CR to accept the default — typing free text is taken
  literally as the field's value, not as a yes.

## Configuration / post-install
See "Post-install" above — two file-append steps (`DUMP-REENTRANT`, `HENT-MODE`) are required or
the install does not survive a cold start.

## Documentation
- PD-sheet: not located for I05 specifically
- PI-sheet: [../../../Product-Info/ND-210337-A1-EN.md](../../../Product-Info/ND-210337-A1-EN.md) (general product sheet, not version-specific)
- Manual(s): `ND-60.250 EN` BACKUP User Guide — [../../../../Reference-Manuals/ND-60.250.1_EN_BACKUP_User_Guide.md](../../../../Reference-Manuals/ND-60.250.1_EN_BACKUP_User_Guide.md)
- Full gotcha list (G1–G12, all from the I04 session but largely version-independent): [../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §5](../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md)

## Provenance & open items
- Source: floppy directory listing (temporary working reference, not committed to this repo) for
  I05's file set; installation dialogue text transposed from the **I04** verified live session in
  [../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md §3](../../../INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md).
- **TODO:** run I05's installer live to confirm the dialogue is unchanged from I04 — not yet
  done. Flag any prompt-wording difference if found.

---
**Parent:** [../README.md](../README.md) (`ND-210337` product overview)
