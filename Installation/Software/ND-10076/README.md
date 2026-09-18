# ND-10076 — Pascal for ND-100

> Status: IN-PROGRESS

| Field | Value |
|-------|-------|
| ND article number | `ND-10076` |
| Product name | PASCAL for ND-100 |
| Functional category | Programming Languages & Compilers |
| ND doc-category tag | 60 General [curated] |
| CPU target | NORD-10 and ND-100 (PD sheet checks both "10" and "100"; catalog previously listed this as NORD-10-only — corrected here) |
| OS requirement | SINTRAN III VS |
| Related products | `ND-10133` Pascal (32-bit, sibling for 32-bit float machines) · `ND-10187` Pascal for ND-500 · `ND-211003` ND Pascal for ND-500/5000 (ISO-standard successor) · `ND-211001` "ND PASCAL" — a later, consolidated compiler explicitly replacing three earlier Pascal compilers (this one likely among them), see [Product-Info/ND-211001-A1-EN.md](../../Product-Info/ND-211001-A1-EN.md), not yet catalogued here |

## Description
Compile and execute Pascal programs. Two-bank compiler, needs a 128K-word terminal segment. Full
PD sheet: [../../../Reference-Manuals/19831207_ND-10076J_PASCAL_for_ND-100_NORD_Software_Library_Program_Description.md](../../../Reference-Manuals/19831207_ND-10076J_PASCAL_for_ND-100_NORD_Software_Library_Program_Description.md). [PD]

This product's install procedure is already this repo's **canonical worked example** for the
generic install methodology — see
[../../INSTALL-METHODOLOGY.md](../INSTALL-METHODOLOGY.md) §5, which quotes it verbatim. This
product folder gives it a proper catalog entry.

## Versions

| Version | Subfolder | Status | Notes |
|---------|-----------|--------|-------|
| J | [ND-10076J](ND-10076J/README.md) | verified (PD sheet transcribed; also the methodology doc's worked example) | dated 83.12.07; floppy `ND-10076J` |

## Documentation
- Program Description (PD-sheet): [../../../Reference-Manuals/19831207_ND-10076J_PASCAL_for_ND-100_NORD_Software_Library_Program_Description.md](../../../Reference-Manuals/19831207_ND-10076J_PASCAL_for_ND-100_NORD_Software_Library_Program_Description.md)
  · Installation guide (separate attached document): [../../../Reference-Manuals/19840118_ND-100_Pascal_version_J_Installation.md](../../../Reference-Manuals/19840118_ND-100_Pascal_version_J_Installation.md)
  · Diskette listing: [../../../Reference-Manuals/19840207_ND-10076J_PASCAL_for_ND-100_NORD_Software_Library_Diskette.md](../../../Reference-Manuals/19840207_ND-10076J_PASCAL_for_ND-100_NORD_Software_Library_Diskette.md)
  · Revision log: [../../../Reference-Manuals/19831207_Pascal_NORD_Software_Library_Revision_Log.md](../../../Reference-Manuals/19831207_Pascal_NORD_Software_Library_Revision_Log.md)
- Product Information (PI-sheet): not located for this article specifically
- Manual(s): `ND-60.124.5`/`ND-60.124.05` ND-Pascal Reference Manual — [../../../Reference-Manuals/ND-60.124.05 ND-PASCAL User's Guide.md](../../../Reference-Manuals/ND-60.124.05%20ND-PASCAL%20User's%20Guide.md)
  · earlier `ND-60.086.02` NORD-10 PASCAL (1979) — [../../../Reference-Manuals/ND-60.086.02_NORD-10_PASCAL_June_1979.md](../../../Reference-Manuals/ND-60.086.02_NORD-10_PASCAL_June_1979.md)
- NDWIKI: not checked yet

## Provenance
Four OCR'd source documents (PD sheet, separate installation guide, diskette listing, revision
log), all filed under `Reference-Manuals/` (the same filing pattern already seen for PLANC's A/B
sheets and ND-10335B) rather than `Installation-Description/`.

---
**Parent:** [../README.md](../README.md) (Software catalog)
