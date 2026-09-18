# State of play: DESC format resolved, NRF LDN fix committed

**Date:** 2026-08-11, brought up to date 2026-08-17 and 2026-09-18 (finished items removed
from sections 4 and 8; the file name keeps its original date)
**Audience:** whoever picks this thread up next - a WSL session in `nd500x`/`pcc-nd500`, a
Windows session driving Ghidra, or a fresh session with none of this context.
**Supersedes as the entry point:** `HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md` (still the
authoritative record of the LDN bug itself - read it for that; read this for current state).

Paths to files inside this repository are repository-relative. Files in other repositories are
named by repository + relative path, never by drive letter.

---

## 1. Read this first: commit state

**Updated 2026-08-17.** The LDN fix and this documentation set are now committed; only the
nd500x settings question is still open.

| Repository | Uncommitted | Note |
|---|---|---|
| `pcc-nd500` | none - the LDN fix is commit `c82cbfc` (2026-08-17) | untracked `SCRATCH/` and an `nrf_test` binary remain in the working tree and must NOT be committed |
| NDInsight (this repo) | none of the File-Formats set - committed 2026-08-17 on branch `5000x` | **Other sessions are editing XMSG C# sources, Hardware 3D models and `tools/ghidra-planc/` in this repo right now, and their work is still uncommitted. Never `git add -A` here. Add exact paths and check `git status --short` before and after.** |
| `nd500x` | `.claude/settings.json` | the `Bash(kill:*)` deny removal; Ronny's call to commit or revert |

The nd500x DAP work IS committed there as `cf6d83c`, with `docs/HANDOFF-DAP-MONITOR-SHELL-2026-08-11.md`.

## 2. What is settled, and how strongly

### DESCRIPTION-FILE:DESC segment entry - RESOLVED

Ten field offsets confirmed from the ND-500 Monitor's own code (`MON-DEBUG:PROG` J04), which
reads this file and prints each field beside its own label. Full evidence per field, with the
loading instruction address, is in `SINTRAN/ND500/nd-500-mon/CARVE-ANSWER-DESC-FIELD-OFFSETS-2026-08-11.md`;
the layout is written up in `DESCRIPTION-FILE-FORMAT.md` and `desc-format.json`.

**The size rule, verified 4/4 on both axes across two independently produced DESC files:**

```
PLB + PSIZE + 1 = .pseg file size
DLB + DSIZE + 1 = .dseg file size
```

| Segment | PLB | PSIZE | `.pseg` | DLB | DSIZE | `.dseg` |
|---|---|---|---|---|---|---|
| SCRATCH-SEG-01 (both floppies) | 0 | 4 | 5 | 0 | 1028 | 1029 |
| LINKAGE-LOAD-H02 | 0 | 123988 | 123989 | 75834 | 2109142 | 2184977 |
| LED-B03 | 0 | 223694 | 223695 | 0 | 394524 | 394525 |

This is why every historic byte-value search for the literal file sizes failed: the file stores
the last byte index, not a count.

**A correction that matters more than it looks:** an earlier version of section 5 listed
LINKAGE-LOAD-H02's DSIZE as 2,109,654. That was an arithmetic slip reading `00 20 2e d6`; the
value is **2,109,142**. The wrong number created a fictitious "open anomaly" (DSIZE not matching
the `.dseg`) that survived into section 6 and into a task list. With the correct value the entry
obeys the same rule as every other. **If a document you are reading still calls this an open
anomaly, that document is stale.** The offset label in
`HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md` was also wrong and was corrected on 2026-08-17:
these bytes are at `0x4124`, not `0x4120`. Re-read from the real file that day, segment entry
at `0x40C0`: `+88` PLB `00 00 00 00`, `+92` PSIZE `00 01 e4 54`, `+96` DLB `00 01 28 3a`,
`+100` DSIZE `00 20 2e d6`, `+104` DEBUGINFO `00 02 66 8b`.

### File geometry - RESOLVED

2048-byte pages: 256-byte header + 32 domain entries of 56 bytes. Domain entry *index* sits at
`56*index + 256*(index div 32 + 1)`, so entry 0 is at byte 256. This is the monitor's own
arithmetic and it lands exactly on the domain names in both real files. It also explains the old
"fields sum to 54 but entries are 56 apart" puzzle - the entry is 56 because 32 of them plus the
header fill a page.

Segment entries are a **singly linked list**: word 0 of a domain entry is the file byte position
of its first segment entry, word 0 of a segment entry points to the next, 0 ends the chain.
Verified in both files.

### NRF LDN - FIXED, RE-VERIFIED AND COMMITTED

Control number 27's numeric field is a byte **count**, with that many raw payload bytes following
the header; every other control group's numeric field is its whole payload. Both the C parser
(`pcc-nd500`, `src/lib/nrf/nrf_utils.c`) and the viewer's JS port now skip the payload. The count
must be recomputed from the raw bytes - the stored `numeric_value` is sign-extended, so an LDN
with `NL=1` and the top bit set would come out negative. The re-run this section used to ask
for was done on 2026-08-17 before the commit (`pcc-nd500` `c82cbfc`): without the fix all three
libraries end in an allocation failure with unclosed modules, with it all three reach clean EOF
and libnrf's own tests still pass at 53 modules. The record is in
`HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md`, "Commit status".

## 3. Dead ends - do not spend time here again

- **CONVERT-DOMAIN is not a witness for the DESC size fields.** Patching PSIZE from 123988 to
  16384 in a real DESC and re-running `CONVERT-DOM-A03` under nd500x produced a byte-identical
  2,316,049-byte `.DOM`. It queries the filesystem with MON 62B GetBytesInFile instead of reading
  the entry.
- **The DESC read does not go through RFILE.** It is MON 74 SETBT (seek) plus a MON 1 INBT byte
  loop (`013527B` -> `013406B`). An earlier brief guessed the `176740B` RFILE helper; that was
  wrong.
- **Static byte-value scanning of the DESC file** was tried exhaustively by an earlier session and
  could not work, for the size-1 reason above.
- **NLL's `WRITE-DOMAIN-STATUS` / `LIST-DOMAIN` printing nothing** was chased at length without
  resolution. The monitor carve made it unnecessary.

## 4. Genuinely open

The two items that used to lead this list - the domain-entry offsets past DNAME, and the
segment-entry bytes 74-84 conflict - were both settled from the monitor's code on 2026-08-17.
The results are in `DESCRIPTION-FILE-FORMAT.md` sections 3 and 4 and the evidence in
`SINTRAN/ND500/nd-500-mon/CARVE-ANSWER-FOUR-OPEN-QUESTIONS-2026-08-17.md`. PBITMAP and DBITMAP
turned out to sit at bytes 48 and 52, not the manual's 46 and 50; on bytes 74-84 the manual was
right and the "two byte strings" reading was a misread loop.

1. **Write-side proof of the size rule.** The monitor only displays; it never adjusts. The rule is
   proven from files, and the monitor's reader uses the same inclusive-last-index convention twice
   (`277B`=191 for the 192-byte record, `67B`=55 for the 56-byte entry), but the writer is NLL.
   NLL's PSEG is now staged in `SINTRAN/ND500/nll-re/`, which is where this would come from.
2. **`MINPAGES` / `MAXPAGES` offsets** in the segment entry are manual-order only; the monitor
   does not print them. The inner layout of a 12-byte `ADDSGELEM` element is manual-only too.
3. **A DESC with a segment chain longer than one entry**, or a domain with children. All 13
   samples have neither, so that code path is proven in the monitor but never seen in a file.

## 5. Two nd500x defects found while doing this

Neither was chased; both are real and reproducible.

- **A converted `.DOM` was truncated to 0 bytes.** `LINKAGE-LOAD-H02.DOM` was a valid 2,316,049-byte
  file and was later found at 0 bytes. That is the signature of the MON 0B LEAVE segment-mapped-file
  writeback bug recorded as fixed on 2026-07-25 - check whether it regressed. It destroys a
  converted domain silently.
- **Quote-create over an existing file returns the wrong SINTRAN error.** `CONVERT-DOMAIN`'s
  quote-create of an existing (0-byte) destination failed with `056B "No such file name"`; the
  correct code is `076B "File already exists"` (`ndmonlib` already has `MON_ERR_FILE_ALREADY_EXISTS`
  in `mon_221B_CreateFile.c`). The wrong code sent this session down a false trail; moving the stub
  aside made the conversion succeed immediately.

## 6. Traps that cost real time

- The shipped `nd-500-mon-j04.prog.asm` **disassembles pointer words as instructions** (e.g. at
  `016277B` it prints `MIN ,B -44`, which is the pointer to the `DESCRIPTION-FILE` string). Literal
  pools at `014714B`-`014735B`, `013544B`-`013551B`, `016264B`-`016277B`, `016462B`-`016506B`.
- P-relative effective address = **address of the instruction** + displacement, not
  next-instruction-relative.
- `JPL` is opcode `0o134`, not `0o130`. Wrong value silently finds no calls and reads like a finding.
- `LDF`/`STF` in this program move 3-word PLANC descriptors (pointer + length), not floats.
- Bank 1 (code) and bank 2 (data) **both base at word 0**; a bank-1 pointer word holding `040734B`
  refers to the bank-2 string at that address. Import them as two Ghidra programs.
- **WSL cannot drive the Windows Ghidra.** WSL2 cannot reach Windows loopback, and nothing was
  listening on the LAN address either (all of 8000-8200 closed). There is no `ghidra` MCP entry in
  any config on the WSL side. Driving Ghidra needs a Windows-side session, or the GhidraMCP plugin
  bound to `0.0.0.0` with a firewall rule for the WSL subnet.

## 7. Where things are

| What | Where |
|---|---|
| DESC spec + machine-readable schema | `SINTRAN/File-Formats/DESCRIPTION-FILE-FORMAT.md`, `desc-format.json` |
| Monitor carve evidence (per-field addresses) | `SINTRAN/ND500/nd-500-mon/CARVE-ANSWER-DESC-FIELD-OFFSETS-2026-08-11.md` |
| The brief that drove it (import parameters, traps) | `SINTRAN/ND500/nd-500-mon/CARVE-BRIEF-DESC-FIELD-OFFSETS-2026-08-11.md` |
| LDN bug record | `SINTRAN/File-Formats/HANDOFF-NRF-LDN-PARSER-BUG-2026-08-11.md` |
| Viewer | `SINTRAN/File-Formats/viewer/`, launch with `run.bat`, **port 8888** |
| Monitor binary + banks + disassembly | `SINTRAN/ND500/nd-500-mon/` |
| nd500x DAP-under-`--monitor` fix | `nd500x` repo, commit `cf6d83c`, `docs/HANDOFF-DAP-MONITOR-SHELL-2026-08-11.md` |
| Real DESC test files | NLL H02 installer floppy `210319H02-XX-01D`; LED floppy `211160B03-XX-01D` |

## 8. Suggested order

Outstanding only - finished steps have been removed.

1. The two nd500x defects in section 5, in that repo. Not checked since 2026-08-11, so look
   first whether they still reproduce.
2. The three open items in section 4.
3. `:LINK`: the string/module regions of `SL202-FO-L27` and the non-symbol cell types - see
   `LINK-FILE-FORMAT.md` section 6 and `link-format.json` `openQuestions`. Needs the L-series
   NLL binary.
