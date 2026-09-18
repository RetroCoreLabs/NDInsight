# SINTRAN File Formats

**Byte-level documentation of the Norsk Data object and executable file formats.**

---

## Files

| File | Contents |
|------|----------|
| [BRF-FILE-FORMAT.md](BRF-FILE-FORMAT.md) | **BRF (Binary Relocatable Format)** - the relocatable object-code format produced by all ND language processors (MAC, FORTRAN, COBOL, PLANC, BASIC, PASCAL, NPL, C) and consumed by the Relocating Loader, the Real Time Loader and the BRF Editor |
| [BRF-GHIDRA-LOADER-HANDOFF.md](BRF-GHIDRA-LOADER-HANDOFF.md) | The specification a Ghidra `Loader` for BRF files was built from (memory layout, symbols, entry points, relocations for ND-100 code), with a reference linker in Python. The loader itself now exists: `BRFLoader.java` in the sibling repository `ghidra-nd100`. |
| [PROG-FILE-FORMAT.md](PROG-FILE-FORMAT.md) | **`:PROG` format** - comprehensive description of the SINTRAN III program file format used by the Nord Relocating Loader (NRL), `@DUMP` / `@RECOVER`, and (extended) by the ND-500 Loader Monitor |
| [prog-fileformat.md](prog-fileformat.md) | `:PROG` on-disk byte-level layout (companion to the reference above) |
| [NRF-FILE-FORMAT.md](NRF-FILE-FORMAT.md) / [nrf-format.json](nrf-format.json) | **`:NRF` format (ND Relocatable Format)** - the ND-500(0) sibling of BRF: relocatable object code from ND-500(0) compilers, consumed by the old Linkage-Loader (NLL) and the ND Linker. Control-byte bit order verified against a real compiler-produced file. The LDN (control number 27) row was corrected in 2026-08 - see the handoff below. |
| [DOM-FILE-FORMAT.md](DOM-FILE-FORMAT.md) / [dom-format.json](dom-format.json) | **`:DOM`/`:SEG` format** - the new self-contained ND-500(0) domain format, code-verified against the pcc-nd500 toolchain's working `dom.h`/`dom_utils.c`, and independently confirmed (FLAGS byte) against a real CONVERT-DOM-A03 output file. |
| [LINK-FILE-FORMAT.md](LINK-FILE-FORMAT.md) / [link-format.json](link-format.json) | **`:LINK` format** - the third file of the old domain trio, alongside `:PSEG` and `:DSEG`. **Decoded 2026-08-17:** it is NLL's in-memory loader table, written out at CLOSE-SEGMENT as 32-byte cells, one per label, which is why every real file is exactly 32k+1 bytes (11 of 11). The writer is carved from NLL's own code and the record layout parses 10 of the 11 sample files completely. Still open: the string/module regions of the L-era `SL202-FO-L27` sample, and the non-symbol cell types - read section 4a before writing a parser. |
| [DESCRIPTION-FILE-FORMAT.md](DESCRIPTION-FILE-FORMAT.md) / [desc-format.json](desc-format.json) | **`DESCRIPTION-FILE:DESC` format** - the per-user index the *old* domain format (`:PSEG`/`:DSEG`/`:LINK`) needs to resolve a domain name to its files. The domain entry, the segment entry, the page geometry and the segment-entry linked list are all confirmed from the ND-500 Monitor's own code and checked against the 13 sample files; what is left open is listed below. |

## Sample corpus

[samples/](samples/README.md) holds the **real vendor files** the DESC and `:LINK` findings
were checked against - 13 `DESCRIPTION-FILE:DESC` files and 11 `:LINK` files extracted from
SINTRAN floppy images, covering twelve products from 1982 to 1989, with a provenance table
giving each one's segment sizes. The claims in the two format documents can be re-checked
against these without hunting for the disk images.

## Handoffs and evidence

| File | Contents |
|------|----------|
| [HANDOFF-DESC-AND-NRF-STATE-2026-08-11.md](HANDOFF-DESC-AND-NRF-STATE-2026-08-11.md) | **Start here for current state of the DESC and NRF threads.** What is settled and how strongly, the size rule `PLB+PSIZE+1 = .pseg` / `DLB+DSIZE+1 = .dseg`, dead ends not to re-chase, the work still outstanding, and the traps that cost time. |
| [HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md](HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md) | The authoritative record of the LDN parser bug: LDN's numeric field is a byte **count** with that many raw payload bytes following, unlike every other control group. Found, fixed in the C parser and the viewer, verified against four library files. |
| [../ND500/nd-500-mon/CARVE-ANSWER-DESC-FIELD-OFFSETS-2026-08-11.md](../ND500/nd-500-mon/CARVE-ANSWER-DESC-FIELD-OFFSETS-2026-08-11.md) | Per-field evidence behind the DESC layout - the loading instruction address in `MON-DEBUG:PROG` J04 for each offset, the read path (MON 74 SETBT + MON 1 INBT, not RFILE), and the domain-entry position formula. |
| [../ND500/nd-500-mon/CARVE-BRIEF-DESC-FIELD-OFFSETS-2026-08-11.md](../ND500/nd-500-mon/CARVE-BRIEF-DESC-FIELD-OFFSETS-2026-08-11.md) | The brief that drove that carve: Ghidra import parameters for the two banks and the ND-100 disassembly traps. |

**Still open in DESC** (the two older items - domain-entry offsets past DNAME, and the
bytes 74-84 conflict - were both settled from the monitor's code on 2026-08-17; the manual was
right about 74-84):

- `MINPAGES` / `MAXPAGES` offsets in the segment entry still rest on the manual's field order -
  the monitor does not print them.
- The inner layout of each 12-byte `ADDSGELEM` element is manual-only.
- The meaning of `DLINKDATE`, `ABSFIXAD`, `LOWLOGFIX`, `PLOLOGFIX` and `PUPLOGFIX`: the offsets
  are proven, but all five read zero in every real entry, so the names are only the monitor's labels.
- No sample has a segment chain longer than one entry, or a domain with children.
- A write-side proof of the size-minus-one rule has to come from NLL; the monitor only displays.

The `.json` files alongside each `.md` are machine-readable versions of the same byte
layout (offsets, sizes, bit fields, control-number/flag tables, per-field verification
status) - written so a generic viewer can parse and label any NRF/DOM/DESC file without
re-encoding the format by hand. That viewer now exists: see
[viewer/](viewer/README.md) (plain-JS, drag-and-drop, hex+parsed dual view, fetches these
JSON files live as its single source of truth).

---

## Related

- The **on-disk filesystem** structures that hold these files - directory label, object
  entry, user entry, page bitmap, boot sector, extended-info block - are documented
  separately in [../Filesystem/on-disk-format/](../Filesystem/on-disk-format/README.md).
  That set describes the container; this set describes the contents.
- The BPUN (Bootable Punched Tape) container format is documented in
  [../../Installation/Communication/Ethernet/x/stripped/README.md](../../Installation/Communication/Ethernet/x/stripped/README.md)
  (verified field-by-field against the ENCOS firmware files, including the
  word-count-0 = 65536 quirk).

---

**Parent:** [../README.md](../README.md)
