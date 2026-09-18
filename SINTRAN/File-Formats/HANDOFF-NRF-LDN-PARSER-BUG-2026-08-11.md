# NRF LDN parser bug - found, fixed, verified

**Date:** 2026-08-11
**Scope:** libnrf (`pcc-nd500`), the NRF/DOM/DESC browser viewer, `NRF-FILE-FORMAT.md`

---

## What was broken

`nrf_read_group()` in `src/lib/nrf/nrf_utils.c` of the `pcc-nd500` repository, and the JS port of it
(`nrfReadGroup()` in `viewer/index.html`), never special-cased **LDN (control number 27)**.
Every other NRF control group's numeric field (NL bytes, 0-7) *is* its entire payload. LDN is
the one exception: its numeric field is a byte **count** N (unsigned), and **N more raw literal
bytes follow the header** that are not a second numeric field and not a symbolic field. Both
parsers treated LDN like a plain group - consumed only the count byte, left N bytes of real
file content sitting in the stream to be misread as the start of the next control group.
Everything after the first LDN in the file desyncs from there: garbage symbol names, spurious
extra BEG/END pairs from noise, and eventually a "malformed group (numeric/symbolic field ran
past end of file)" near EOF once the drift consumes a byte count large enough to run past the
buffer.

`NRF-FILE-FORMAT.md`'s own LDN row said "same as LDI but explicitly no S" - a guess by analogy
to LDI, never checked against real bytes. It was wrong: LDI's numeric field bytes *are* the
immediate data (capped at 7). LDN's numeric field is a count; the data comes after it,
unbounded.

## How it was found

User reported `NC-LIB-A06.NRF` (101,442 bytes, from the ND-500 C library set) failing in the viewer with
"Group stream ended with a malformed group... 6098 control groups decoded, 180 module(s)
found." Traced with a standalone harness linked against the real `nrf_utils.o` (not a
reimplementation) that logs every group's offset/control/NL/symbol:

- Raw iterator hit the malformed condition at group #6098, offset `0x18c1e`, ctrl=25 (MSG),
  NL=5 - a MSG group with a claimed 206-byte symbol that would run 182 bytes past a 101KB
  file. Obviously not real data; the parser was already desynced by then.
- Walking backward through the trace found the actual desync point: group `#005961`, offset
  `0x01818a`, `LDN NL=1 num=52`. The next 52 bytes (offset `0x01818c`..`0x0181c0`) were being
  read as the start of a new group ("LIB sym=67:'JHF IA'" - garbage), when they're actually
  LDN's own immediate-load payload.
- Confirmed by hex dump: skipping exactly 52 bytes after the LDN header lands on `DEF #.646`
  at offset `0x181c0` - a symbol (`#.646`) already seen live and legitimate earlier in the
  same module (module 177, `DDF #.646`).

## The fix

Both `nrf_read_group()` (C) and `nrfReadGroup()` (JS) now do, after the existing
control/numeric/symbolic field handling:

```c
if (cn == NRF_LDN) {
    uint64_t skip = 0;
    for (int j = 0; j < nl; j++) skip = (skip << 8) | group->numeric_raw[j]; /* unsigned! */
    if (p + skip > it->len) return -1;
    p += skip;
}
```

Note it recomputes the count from the raw bytes rather than using the already-computed
`numeric_value` / `numericValue` - that field is sign-extended two's-complement (correct for
every other control number, where the numeric field is a signed value), which is wrong for a
byte count (an LDN with NL=1 and top bit set, e.g. `0x80`, must mean 128, not -128).

## Verification performed (all actually run, not inferred)

- `make -C src/lib/nrf test` - existing unit tests (`nd-500-apf-lib-e.nrf`, 5716 groups, 53
  modules) still pass unchanged.
- Rebuilt `nd500-dump`/`libnrf.a` for real (not the `/tmp` experimental copy) and ran `-N`
  against **four** files: `NC-LIB-A06.NRF` (the reported file, 8354 groups, 103 clean
  BEG/END-paired modules, was 180 with garbage), `CAT-LIB-B06.NRF` (21824 groups),
  `USLIB3.NRF` (74857 groups), and `nd-500-apf-lib-e.nrf` (5716 groups, regression check). All
  four now parse to clean EOF with `Truncated (malformed tail): no`.
- Extracted the **literal** `<script>` contents from `viewer/index.html` (not a port/rewrite),
  ran it under Node against `NC-LIB-A06.NRF`: 8354 groups, all 101,442 bytes consumed,
  `truncated: false` - matches the C reference exactly.
- `node --check` on the extracted script after editing (syntax only, not a browser render -
  no browser-automation tool was available this session; the user opened the real page and
  confirmed the failure, then I re-served the fixed page on port 8888 for them to re-check).

## Files changed

- `pcc-nd500` repository, `src/lib/nrf/nrf_utils.c` - the real fix
- `SINTRAN/File-Formats/viewer/index.html` - same fix, JS
- `SINTRAN/File-Formats/NRF-FILE-FORMAT.md` - corrected LDN row
- `SINTRAN/File-Formats/viewer/run.bat` (new) - double-click launcher, `cd`s to
  `File-Formats/` and serves on **port 8888** (not 8000 - changed at user's request,
  a local conflict)
- `SINTRAN/File-Formats/viewer/README.md` - documents `run.bat`, port 8888

**Commit status:** the `pcc-nd500` fix was committed 2026-08-17 as `c82cbfc`, after an
independent re-verification (control run without the fix: all three libraries end in an
allocation failure with unclosed modules; with it, all three reach clean EOF and libnrf's
own tests still pass at 53 modules). The NDInsight side is committed alongside this
document.

## Also this session: DESC format fields resolved (separate from the above)

A different session/LLM carved `MON-DEBUG:PROG` (the ND-500 Loader/Debug Monitor) and pinned
byte offsets for the Segment Entry fields that `DESCRIPTION-FILE-FORMAT.md` had previously
marked "UNABLE TO DETERMINE" - PLB, PSIZE, DLB, DSIZE, DEBUGINFO, DLINKDATE, ABSFIXAD,
LOWLOGFIX, PLOLOGFIX, PUPLOGFIX (all offset 88-129, see the doc section 4 for the exact
monitor instruction/label evidence per field). I:

- Updated the viewer to decode and display those ten fields for Segment Entries (previously
  intentionally hidden as unverified - see the viewer's own prior disclaimer, now stale and
  removed).
- While verifying the viewer's numbers against the real `description-file.desc`
  (the vendor floppy `210319H02-XX-01D`), found the doc's own section 5 table had a
  transcription error: `LINKAGE-LOAD-H02`'s DSIZE-stored value was listed as 2,109,654, but the
  real bytes at file offset `0x4124` (raw `00 20 2e d6`) are **2,109,142**. This value fed
  directly into section 6, which called it an "open anomaly" (DSIZE not matching the `.dseg`
  file size). With the correct value the anomaly resolves cleanly: `DLB + (DSIZE_stored + 1) =
  75834 + 2,109,143 = 2,184,977`, exactly the `.dseg` file size - the same formula the
  zero-DLB entries already satisfied trivially. Corrected both `.md` and `.json`; moved that
  item from `openQuestions` to a new `resolvedQuestions` array.

At the time, one thing was left open in DESC: the manual-vs-monitor conflict at Segment Entry
bytes 74-84 (manual says `COMSEGSIZE`/`N100SEGNO` arrays; the monitor code seemed to print two
byte strings there using a count at word `37B`). **Settled 2026-08-17: the manual was right** -
the count is `COMSEGNO` and the "strings" were a misread loop. See `DESCRIPTION-FILE-FORMAT.md`
section 4.
