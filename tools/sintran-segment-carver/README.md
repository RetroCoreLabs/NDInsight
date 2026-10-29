# SINTRAN III System-Segment Carver

Full path: `tools/sintran-segment-carver/`

Carves the individual **system segments** out of a SINTRAN III SMD disk image so
each can be loaded into **Ghidra** (or `nd100-dis`) at its correct load address for
reverse engineering — the file system, command processor, monitor-call handlers,
XMSG, ND-500 monitor, etc. Works for any SINTRAN version; the L/VSX-500 (L07) set
is included as the worked example.

## Start here

| Document | What it covers |
|----------|----------------|
| **[EXTRACTING-SEGMENTS.md](EXTRACTING-SEGMENTS.md)** | The full procedure: page/carve model, fact sources, `reconcile.py` -> `carve.py` pipeline, loading each segment into Ghidra, `nd100-dis` byte order. **Read this first.** |
| **[EXTRACTING-RESIDENT-CODE.md](EXTRACTING-RESIDENT-CODE.md)** | The memory-**resident** code/data the carver skips: resident common code/data, RT-loader area, level-14 MON dispatch, and why the resident data cells are runtime-only. |
| **[versions/L-VSX-500/re/README.md](versions/L-VSX-500/re/README.md)** | The L07 reverse-engineering tree: monitor-call analysis (incl. the full MON 60B / N500M carve) and the byte-verified ND-500 system-monitor carve (the ND-100 <-> ND-500 interface, end to end). |
| [versions/L-VSX-500/re/HANDOFF-fold-live-capture.md](versions/L-VSX-500/re/HANDOFF-fold-live-capture.md) | Open RE task: capture the password fold live via DAP (the fold's runtime values are not in any static carve). |

## The pipeline in one line

```
ndtool -x SEGFIL0:DATA  ->  reconcile.py (facts)  ->  carve.py (big-endian .bin per segment)  ->  Ghidra
```

A SINTRAN page is **1024 words = 2048 bytes**; a segment occupies
`SEGFIL0[MADR*2048 : MADR*2048 + SEGLE*2048]`; load each `.bin` at
`(LOGAD*1024) & 0xFFFF`. Full detail and the verification behind it are in
[EXTRACTING-SEGMENTS.md](EXTRACTING-SEGMENTS.md).

**Corrections 2026-10-29:** the pipeline no longer needs a running system. The segment table
(`S3ISGT`, inside `SEGFIL0:DATA`) and the segment names (type-25 records in
`(SYSTEM)RTFIL:DATA`) are both readable offline, and the kernel's segment-file tables
(`DBLST(0) = 256` blocks, `ABLPAGE(0) = 2` blocks per page, measured on K and L packs) place
`SEGFIL0` at disk page 128. `ndtool --segments / --export-segment / --import-segment` in the
sibling repository `norskdata-ndfs` (`ndfs-c/src/sintran_segments.c`) does it from the image
alone; see [EXTRACTING-SEGMENTS.md](EXTRACTING-SEGMENTS.md) sections 1, 2 and 5 (option C).
Mind that on K packs the save segments 52-60 and 63 are in "segment file 4" =
`SINTRAN:DATA`/`MACM-AREA:DATA`, not in `SEGFIL0:DATA`.

## Carved sets (per version)

| Version | Catalog |
|---------|---------|
| L-VSX-500 (L07) | [versions/L-VSX-500/segments/README.md](versions/L-VSX-500/segments/README.md) |
| K-VSX-500 (K05) | [versions/K-VSX-500/segments/README.md](versions/K-VSX-500/segments/README.md) |
| M-VSX-500 (M06) | [versions/M-VSX-500/segments/README.md](versions/M-VSX-500/segments/README.md) |

## Files

| Path | Purpose |
|------|---------|
| `reconcile.py` | merge live `LIST-SEGMENT` + manual + memory Segment Table into `segment-facts.json` |
| `carve.py` | carve one big-endian `.bin` per segment from the extracted SEGFIL0 (`SECTOR=2048`) |
| `ghidra_scripts/LoadSintranSegments.py` | Ghidra label-import helper |
| `ghidra-tasks/` | self-contained Ghidra RE task handoffs (password/login, MON dispatch, ND-500 monitor, filesystem) |
| `versions/<VER>/inputs/` | per-version inputs (listings + segment-table dump) |
| `versions/<VER>/segment-facts.json` | canonical reconciled facts |
| `versions/<VER>/segments/` | carved `.bin` + `manifest.json` + per-version catalog |
