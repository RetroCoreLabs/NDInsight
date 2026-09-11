# CONVERT-DOM-A03 - convert old-format domains to the new :DOM format

## Overview

CONVERT-DOM-A03 (Convert-Domain, version A03) converts Norsk Data ND-500 domains
from the OLD domain format (a description file plus per-segment `:PSEG`, `:DSEG`
and `:LINK` files) to the NEW domain format (a single `:DOM` file with the
bookkeeping information stored in a header, plus `:SEG` files for shared/free
segments). [from HELP]

The main difference between the two formats: the old format has a separate
description file; the new format does not - each domain is one `:DOM` file that
can be copied with a plain `@COPY-FILE`. [from HELP]

It uses the ND-SHELL as its command processor, so the interface is very similar
to ND's LINKER. [from HELP]

For shared install/run conventions see [../README.md](../README.md).

## Files (in files/)

- `CONVERT-DOM-A03.DOM` - the runnable ND-500 domain. [verified]
- `CONVERT-DOM-A03.HELP` - the vendor help text (topics and command syntax).
  [from HELP]
- `CONVERT-DOM-A03.INIT` - the startup command script run on entry. It contains
  a `LIST` command and two comment (`%`) lines describing the tool. [from HELP]

## Requirements

- The `.DOM` file to run. [verified]
- Install: copy `files/*` into the sintran-root. See
  [../README.md](../README.md).
- To convert a domain you need the source domain in the OLD format (its
  description file plus its `:PSEG`/`:DSEG`/`:LINK` files) available under a
  user directory. [from HELP]

## How to run

Interactive: at the SINTRAN `@` prompt type the bare name (the `@` is the
prompt, do not type it):

```
CONVERT-DOM-A03
```

With no command-line parameters the ND-SHELL is used and you get an interactive
command prompt (press the HELP key for help). If you instead write the
parameters on the command line, the shell is NOT used, for example
`ND CONVERT-DOM DEST-DOM SOURCE-DOM`. [from HELP]

Scripted (non-interactive) drive, from `~/repos/nd500x`:

```
printf 'LOGIN GUEST\nCONVERT-DOM-A03\nCONVERT-DOMAIN NEW-DOM OLD-DOM\nEXIT\n' | \
    ./build/bin/nd500x --monitor --user GUEST --sintran-root ~/ND500USERS
```

**Note (corrected 2026-09-11):** the HELP's destination-first order is CORRECT. The scripted line
above types the `CONVERT-DOMAIN` verb because it drives the INTERACTIVE ND-SHELL. When you instead
run the DOM with parameters on its OWN command line, do NOT type the verb — the first token is the
destination directly (see "Parameter order" under "Input & output files" below). An earlier note
here claimed a "source-first" order; that was an artifact of counting the verb as the first token,
and is withdrawn.

## Commands and options

Commands (from the shipped HELP): [from HELP]

- `CONVERT-DOMAIN <Destination domain> <Source domain> <Include linked
  segments (Yes/No)> <Display progress information (Yes/No)> <Force free segment
  number(s)>...`
  - `<Destination>` (mandatory) - name of the new-format `:DOM` file to create.
    Accepts an empty string (just CR), which is equivalent to a single `$`.
    A `$` in the name is substituted with the source domain name. Enclose the
    name in double quotes to prevent overwriting an existing `:DOM` file.
  - `<Source>` (mandatory) - name of the source domain, which must be in the old
    format. No default.
  - `<Include linked segments>` (optional, default NO) - YES copies all `:SEG`
    files needed by the destination to the destination's user (useful for
    putting everything on one floppy); NO links to `:SEG` files that may live in
    other user areas.
  - `<Display progress information>` (optional, default YES) - YES prints
    progress messages such as `>> Converting debug part for segment 3 <<`.
  - `<Force free segment numbers>...` (optional, repeated) - force listed
    segment numbers onto `:SEG` files even when the tool would otherwise put
    them on the `:DOM`. Ranges accepted, for example `0:31`, `0-31` or `0..31`.
    Example: `CONVERT-DOMAIN $ NOTIS-WP,,,0:31`.
- `EXIT` - leave the Convert-Domain command processor. [from HELP]
- `HELP` - built-in help; accepts SINTRAN matching and the wildcards `-`, `+`
  (any single character) and `*` (any string). SHIFT+HELP lists all matching
  commands. [from HELP]
- `%` - shell comment line. [from HELP]
- `@<command>` - run a SINTRAN III command from inside the tool
  (for example `@DELETE-FILE destination:DOM`). [from HELP]

Help topics defined: COMMENT, CONVERT-DOMAIN, EXIT, HELP, LIMITATIONS,
NEW-DOMAIN-FORMAT, OLD-DOMAIN-FORMAT, SHELL, SIBAS. [from HELP]

Limitations (do NOT convert): Sibas version F or older; Notis-DS version D or
older; Notis-ID version B or older; ND-500 Basic version B or older; and the
ND-500/5000 Swapper and Symbolic Debugger (they have no description file).
[from HELP]

## Verified behaviour in nd500x

Verified 2026-07-31 in the `nd500x` C emulator: the program loads and runs.
[verified]

**Full end-to-end conversion VERIFIED 2026-08-10** - the first real conversion run
recorded for this tool. Source: `LINKAGE-LOAD-H02` (the NLL H02 installer floppy's own
domain, old format: `DESCRIPTION-FILE:DESC` + `:PSEG`/`:DSEG`/`:LINK`, staged as SINTRAN
user `FLOPPY-USER` under `~/ND500USERS/FLOPPY-USER/`). Driven non-interactively:

```
printf 'LOGIN FLOPPY-USER\nCONVERT-DOM-A03\nCONVERT-DOMAIN "LINKAGE-LOAD-H02" LINKAGE-LOAD-H02\nEXIT\n' | \
    ./build/bin/nd500x --monitor --user FLOPPY-USER --sintran-root ~/ND500USERS
```

Output (verbatim, ANSI codes stripped):

```
- Convert Domain, Version A03            January 24,  1989
- CONV entered:
CONVERT-DOM:INIT
% This program converts domains and segments from :PSEG/:DSEG/:LINK
% format to :DOM/:SEG format. If you need help, press the help key.
CONV: CONVERTDOMAIN "LINKAGE-LOAD-H02" LINKAGE-LOAD-H02
 >> Converting debug part for segment 22
 >> Converting link part for segment 22
 >> Converting program segment 22
 >> Converting data segment 22
 >> Finished
CONV: EXIT
-- program exited (316156 instructions) --
```

Produced `LINKAGE-LOAD-H02.DOM` (2,316,049 bytes - roughly
4096-byte header + 123,989-byte PSEG + 2,184,977-byte DSEG + debug/link overhead,
consistent with the source sizes). Header bytes independently confirm
`../../File-Formats/DOM-FILE-FORMAT.md`'s FLAGS byte layout: offset 0x06 = `0xF8` =
bits 3/4/5/6/7 all set = TRAPBLOCK_VALID + IS_DOMAIN_FILE + IS_ROOT_DOMAIN +
IS_SINTRAN_III + IS_ND500, exactly as that spec's bit table predicts.

Notes: the tool reported the domain's logical segment as **22**, not 0 or 1 - a real
data point toward pinning `DESCRIPTION-FILE:DESC`'s still-unverified PLOG/DLOG bitfield
(see `../../File-Formats/DESCRIPTION-FILE-FORMAT.md` section 5).

**The converted `.DOM` DOES run, confirmed 2026-08-10.** Ran directly (no floppy, no old
`:PSEG`/`:DSEG`/`RECOVER-DOMAIN` path - just `@LINKAGE-LOAD-H02` against the file
CONVERT-DOM-A03 produced):

```
printf 'LOGIN FLOPPY-USER\nLINKAGE-LOAD-H02\nEXIT\n' | \
    ./build/bin/nd500x --monitor --user FLOPPY-USER --sintran-root ~/ND500USERS
```

```
@LINKAGE-LOAD-H02
-- LINKAGE-LOAD-H02 placed (domain 1, start 0xB0000DD1) --
  [SINTRAN ERROR 132B]
Nll: EXIT
[STOP] Unimplemented MON 405B (USTRK) with 2 args
-- program exited (15066 instructions) --
```

The domain **placed at the correct start address and reached its own live `Nll:` command
prompt** - strong evidence the conversion is structurally and functionally correct (entry
point, segment placement, and enough of the loaded code to run its own startup and print
its prompt). `SINTRAN ERROR 132B`'s meaning is not yet decoded here - it appeared but did
not stop execution, so treat it as non-fatal until checked against the SINTRAN error-code
list. The eventual stop is an **`nd500x` emulator gap** (MON call `405B`/USTRK not
implemented), not a defect in the converted domain - a materially different, and better,
result than the OLD-format run path in
`../../../Installation/INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md` (which hits a
5SWAP protect-violation before ever reaching a prompt).

## Known issues / status

- Loads and runs; ships both HELP and INIT files. [verified]
- End-to-end conversion output VERIFIED 2026-08-10 - see above. [verified]
- The converted `.DOM` runs and reaches its own `Nll:` prompt, VERIFIED 2026-08-10 - see
  above. **MON 405B (USTRK) is now implemented in `nd500x`** (fixed same day - the
  handler existed but was registered with `MON_STATUS_NOT_IMPLEMENTED` instead of
  `MON_STATUS_IN_PROGRESS` in `external/ndmonlib/src/core/mon_registry.c`, which forced a
  STOP regardless of the real handler code; one-line fix). Re-tested after rebuild: the
  call now returns SUCCESS (confirmed via `ND500X_MONLOG=1` trace) and `Nll:` commands run
  to completion without stopping - `WRITE-DOMAIN-STATUS LINKAGE-LOAD-H02` and `EXIT` both
  now finish cleanly at `MON 0B LEAVE` instead of halting.
- `WRITE-DOMAIN-STATUS` produces no visible console text - traced to `MON 120B WFILE`
  writing 2048 bytes back into `DESCRIPTION-FILE:DESC` itself (file 101, block 0, the same
  block holding the Domain Entries) rather than printing to the terminal.

  **UPDATE, same session, further tracing:** the manual (ND-60.136.04A section 6.1.6)
  explicitly says WRITE-DOMAIN-STATUS "Prints all the available information about the
  domain" and 6.1.5 says LIST-DOMAIN "Writes ... on the output device" - so both SHOULD
  print, contradicting the "persist-only" read above. Re-traced with `ND500X_MONLOG=1`
  and found a real secondary bug: mid-command, NLL tries (twice, access codes 2 and 3)
  to open `(SYSTEM)DESCRIPTION-FILE:DESC`, which didn't exist (`error -46`,
  `Cannot open host file '.../SYSTEM/DESCRIPTION-FILE.DESC'`) - a genuine emulator-adjacent
  finding: NLL appears to unconditionally consult SYSTEM's own description file as part of
  status reporting, not just the current user's. Creating a `SYSTEM/DESCRIPTION-FILE.DESC`
  (copied from FLOPPY-USER's) cleared that specific error - **but status text still never
  printed**, so it was a real bug, just not THE blocker. `OUTST` call count stayed at the
  same 5 calls (all short prompt/banner writes, never a real status listing) before and
  after the fix.

  **Not yet resolved**: the actual status-print short-circuit is somewhere past this
  point in NLL's own code, not identified from MON-call tracing alone - narrowing it
  further needs single-instruction tracing (`--trace-file`, or the DAP debugger) from the
  last confirmed-good `OUTST` call forward to find exactly where the status-formatting
  routine diverges or returns early. Command variants tried without success: bare
  `WRITE-DOMAIN-STATUS`, with domain name space-separated, with domain name comma-separated
  (`WRITE-DOMAIN-STATUS,LINKAGE-LOAD-H02`). `LIST-DOMAIN` inside the `Nll:` shell also
  produced no visible text with either no argument (bare CR to accept the documented "all
  domains" default) or the domain name on the following line (its actual `Domain-name:`
  prompt syntax, confirmed from ND-60.136.04A section 6.1.5) - unlike the system-wide
  `LIST-DOMAIN` at the top-level `ND-5000:`/monitor prompt seen working in
  `../../../Installation/INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md`, which is a
  different prompt context (`nd500x` has no separate `ND-500`/monitor shell - only
  whatever the placed domain itself, here NLL, provides).

## References

- Shared conventions: [../README.md](../README.md)
- Vendor help text: [files/CONVERT-DOM-A03.HELP](files/CONVERT-DOM-A03.HELP)
- Startup script: [files/CONVERT-DOM-A03.INIT](files/CONVERT-DOM-A03.INIT)
- Disassembly: [analysis/convert-dom-a03.asm](analysis/convert-dom-a03.asm)
- Runnable domain: [files/CONVERT-DOM-A03.DOM](files/CONVERT-DOM-A03.DOM)

## Input & output files, FAQ, common errors (added 2026-09-11)

General MON-call background for every ND-500 DOM program: see the central reference
`E:\Dev\Ronny\ND500UC\docs\DOM-PROGRAM-IO-REFERENCE.md`. This section applies that reference
to CONVERT-DOM-A03 specifically.

### Input

- CONVERT-DOM-A03 reads its whole command line with `INBT` (MON 1B), one byte at a time,
  from **SINTRAN device 0, the command buffer** — the text that followed the command name on
  the line that started the program. [measured, `DOM-PROGRAM-IO-REFERENCE.md` section 3]
- **One-shot (non-interactive) form** — put every parameter on the SAME line as the command
  name. When parameters are on the command line, the ND-SHELL is **not** invoked at all — it
  reads the line straight from device 0 and acts. [from HELP, section "SHELL"]
- **Interactive form** — the bare name only. The ND-SHELL takes over and prompts step by step
  (`Source domain:`, etc). [from HELP]
- **Parameter order — DESTINATION FIRST, and NO `CONVERT-DOMAIN` verb on the command line.**
  When you run the DOM with parameters on its OWN command line, it reads them DIRECTLY: the
  FIRST token is the `<destination>`, the SECOND is the `<source>`. The word `CONVERT-DOMAIN`
  is a verb ONLY inside the interactive ND-SHELL — do NOT type it on the command line, or the
  DOM takes the literal word `CONVERT-DOMAIN` as your destination name. So the one-shot form is:
  `<dest> <source> [linked Y/N] [progress Y/N] [force-free-seg...]` — e.g. `LED-CONV LED-B03`.
  This matches the HELP/manual's documented destination-first order.
  MEASURED 2026-09-11 on the real-SINTRAN lane: `LED-CONV LED-B03` (no verb) resolved the
  destination correctly — the DOM issued MON 221B CREATE for `LED-CONV:DOM`, then MON 50B OPEN
  (write) K=0. The two earlier attempts that PREPENDED the verb gave a misleading "source-first"
  appearance and are the whole reason an earlier version of this note (now withdrawn) claimed
  source-first: `CONVERT-DOMAIN LED-B03 "LED-CONV"` was parsed dest=`CONVERT-DOMAIN`,
  source=`LED-B03` (third token ignored); `CONVERT-DOMAIN "LED-CONV" LED-B03` put the quoted
  `"LED-CONV"` in the source slot and failed `Conv-Dom Error: ChkNames: Sourcename has '"'`.
  Counting the verb as the first (destination) token is what produced the false source-first
  reading. [measured 2026-09-11; reconciles with the HELP dest-first order]
  `<dest>` and `<source>` are mandatory; the rest are optional with documented defaults
  (NO / YES). A `$` in `<dest>` is replaced with the source domain name; an empty `<dest>`
  (bare CR) is treated as a single `$`. Quoting `<dest>` means "refuse to overwrite an existing
  `:DOM`", NOT "create" — the quote is optional when the destination does not yet exist. [from HELP]
- **SILENCE = WAITING, NOT BROKEN — but the banner DOES print first.** The verified 2026-08-10
  run (see "Verified behaviour in nd500x" above) and the 2026-09-09 corpus701 re-measurement
  both show the banner and `CONV entered:` print immediately on start; CONVERT-DOM-A03 then
  waits, silently, at whatever prompt comes next (`CONV:` or `Source domain:`). Waiting there is
  normal, not a hang — but the claim that it "reads before printing any banner at all" is NOT
  supported by either measured run and has been removed. [checked against the verified
  transcript above and BUGS.md line 47, 2026-09-11]
- **Do not send EXIT too early.** BUGS.md's "THE HEADLINE NUMBER" re-measurement (2026-09-09,
  the `corpus701` macro-round logs — this supersedes the older, differently-worded `run314` row
  from the 2026-09-04 table further down the same file) recorded CONVERT-DOM-A03 reaching its
  banner, `CONV entered:`, and the `Source domain:` prompt, but the harness's scripted `EXIT`
  had already been consumed by an earlier read, so the program parked instead of leaving
  cleanly and never reached `MON 0B`. [measured, `E:\Dev\Ronny\ND5000UC\BUGS.md` line 47]
- Terminal type: CONVERT-DOM-A03's own DOM binary contains the bare string `DDBTABLES-      :VTM`
  (name padded with blanks, no generation letter baked in — unlike LED-FORTRAN's DOM, which
  contains the literal `DDBTABLES-E     :VTM FILE DOES NOT EXIST`), plus a separate string
  `VTM ver. G03` elsewhere in the same binary. [measured via a `strings` dump of
  `files/CONVERT-DOM-A03.DOM`, 2026-09-11] Whether that `G03` is the generation letter this
  lookup actually needs is an **inference by analogy with LED-FORTRAN's own E-generation match**
  (see `led-fortran-ambiguous-ddbtables-e` memory) — it has NOT been confirmed by a live run of
  CONVERT-DOM-A03 hitting this code path, and LED's own root cause was a DUPLICATE
  `DDBTABLES-E*` on the pack, not a missing/wrong letter. [inferred, unconfirmed]

### Output

- The converted domain is written as a new `:DOM` file. The disassembly confirms the exact
  MON sequence: **MON 257B FOPEN** then **MON 50B OPEN** with access mode 3 (write, "WX") —
  `analysis/convert-dom-a03.asm` lines 43129 and 43149 — plus 14 sites of the ND-500-native
  **MON 513B** file-write call and one **MON 512B** message call further down (lines
  ~51552–54955). A second, independent `MON 50B OPEN` call site exists at line 53099. [from
  disasm]
- **CORRECTION 2026-09-11 (previous text here was unsupported and has been removed):** there is
  NO evidence CONVERT-DOM-A03 calls `MON 50B` three times for the destination open. The
  disassembly has exactly two static `MON 50B` call sites (line 43149 and a second, independent
  one at line 53099), and the one measured real run that reached the file layer shows a SINGLE
  `MON 50B` call succeeding immediately (K=0, file 101B) — no retry pattern was observed.
  [checked against `analysis/convert-dom-a03.asm` and `DOM-PROGRAM-IO-REFERENCE.md` section 3,
  2026-09-11] The HELP text DOES describe a three-step fallback search (destination user, then
  a library user, then the current user) — but that is for creating a **free `:SEG` file** for a
  linked segment when `<Include linked segments>` is NO, not for opening the main destination
  `:DOM` file. Do not conflate the two.
- **SINTRAN does NOT auto-create a file on an unquoted open-for-write.** Per the central IO
  reference, an output `:DOM`/`:SEG` name that does not already exist needs either the
  double-quoted create form (`"name:type"`, which is also how CONVERT-DOM-A03's own
  `<Destination>` quoting works to PREVENT overwrite — quoting has a dual meaning here, so read
  the HELP text's `<Destination>` paragraph carefully) or a prior `@CREATE-FILE` on the console.
  [doc, `DOM-PROGRAM-IO-REFERENCE.md` section 4]
- Verified 2026-08-10 end-to-end: `CONVERT-DOMAIN "LINKAGE-LOAD-H02" LINKAGE-LOAD-H02` produced
  a working `LINKAGE-LOAD-H02.DOM` (2,316,049 bytes) whose header FLAGS byte matches the
  documented DOM-FILE-FORMAT bit layout, and the resulting domain PLACEd and ran to its own
  `Nll:` prompt. [verified, see "Verified behaviour in nd500x" above]

### Good to know

- CONVERT-DOM-A03 shares its command processor (the ND-SHELL) with ND's LINKER, so LINKER
  habits (HELP key, SHIFT+HELP, `@`-prefixed SINTRAN commands mid-session, `%` comments)
  transfer directly. [from HELP]
- The DOM's own logical segment number is not guaranteed to be 0 or 1 — the verified real run
  reported segment **22** for its source domain, a live data point for the still-open
  PLOG/DLOG bitfield question in `DESCRIPTION-FILE-FORMAT.md`. [measured, 2026-08-10 run above]
- Do NOT convert: Sibas version F or older, Notis-DS version D or older, Notis-ID version B or
  older, ND-500 Basic version B or older, or the ND-500/5000 Swapper and Symbolic Debugger
  (the last two have no description file to convert from). [from HELP, "LIMITATIONS"]
- `WRITE-DOMAIN-STATUS`/`LIST-DOMAIN` style status text does not appear on the octobus/nd500x
  runs even after the underlying MON 405B gap was fixed — a separate, still-open formatting
  short-circuit inside NLL's own code, not a CONVERT-DOM-A03 defect and not yet localized past
  the last confirmed-good `OUTST` call. [verified/open, see "Known issues / status" above]

### FAQ

- **Q: I ran the bare command name (`CONVERT-DOM-A03`) and nothing prints. Is it hung?**
  A: No — the verified 2026-08-10 run shows the banner and `CONV entered:` DO print for a bare
  start; it then waits at the `CONV:` shell prompt for a command. [verified, see "Verified
  behaviour in nd500x" above] A DIFFERENT, real trap is typing the bare command **`CONVERT-
  DOMAIN`** (no arguments) at that `CONV:` prompt: measured 2026-09-11, this makes the program
  read back leftover bytes from its own command line ("-DOMAIN", the tail of the command name
  it just read) and loop on `Source domain:` forever — always supply the parameters, or expect
  to answer `Source domain:` yourself. [measured, `DOM-PROGRAM-IO-REFERENCE.md` section 3]
- **Q: Why did my scripted `EXIT` not end the session?**
  A: An earlier prompt in the script likely consumed it as its own answer. Count prompts and
  make sure `EXIT` is queued as its own separate line AFTER the last real prompt, not folded
  into the same input burst. [measured, BUGS.md "THE HEADLINE NUMBER" table, line 47 — see the
  correction above the older `run314` label is superseded by this]
- **Q: My destination file open fails on the first two tries and only succeeds on the third
  `MON 50B` — is that a bug?**
  A: This has not actually been observed for the destination `:DOM` open — see the correction
  above. If you see a `MON 50B` retried, it is more likely the HELP text's free-`:SEG`-file
  search order (destination user, then a library user, then the current user), which applies
  when copying a LINKED segment, not the destination file itself. [from HELP]
- **Q: Can I convert Sibas or Notis-DS?**
  A: Only specific versions — see LIMITATIONS in the HELP text; older Sibas F / Notis-DS D /
  Notis-ID B / ND-500 Basic B must NOT be converted. [from HELP]

### Common errors and how to fix them

| Symptom | Cause | Fix |
|---|---|---|
| A bare `CONVERT-DOMAIN` (no args) typed at the `CONV:` prompt loops on `Source domain:` forever | It read back leftover bytes ("-DOMAIN") from its own command line instead of your answer | Always type `CONVERT-DOMAIN` with its parameters, or be ready to answer `Source domain:` on the next line [measured, `DOM-PROGRAM-IO-REFERENCE.md` section 3] |
| Session parks after `Source domain:`, never reaches `EXIT`/`MON 0B` | Scripted `EXIT` was consumed by an earlier prompt read | Re-count the prompts your script answers; put `EXIT` on its own trailing line after every expected prompt has been answered [measured, BUGS.md "THE HEADLINE NUMBER" table, line 47] |
| "File already exists" style error creating `<Destination>` | `<Destination>` was quoted (quoting here means "refuse to overwrite"), or the file legitimately already exists | Drop the quotes if overwrite is intended, or pick a different destination name; quoting on `<Destination>` is NOT the SINTRAN create-file convention, it means the opposite (protect) [from HELP] |
| Output `:DOM`/`:SEG` open fails outright | Unquoted open-for-write on a name SINTRAN will not auto-create (general SINTRAN rule; not yet seen fail this way for CONVERT-DOM-A03's own destination open, which succeeded first-try in the one measured run) | Pre-create the target with `@CREATE-FILE`, matching name/type/user exactly, before running CONVERT-DOMAIN [doc, central IO reference] |
| "Ambiguous file name" style terminal/database errors | Possibly more than one generation of the terminal database file (DDBTABLES) present on the pack, or the wrong generation letter installed — CONVERT-DOM-A03's binary looks up a bare `DDBTABLES-` prefix, and separately contains the string `VTM ver. G03`, but which generation it actually needs has not been confirmed by a live run [inferred, unconfirmed — see "Terminal type" note above] | Ensure exactly one matching-prefix DDBTABLES entry is on the pack; verify the required generation with a live run before trusting the `G03` guess |
| Converting a domain listed under LIMITATIONS produces a broken/unusable result | Program is one of the excluded old-domain-format families (Sibas F-, Notis-DS D-, Notis-ID B-, ND-500 Basic B-, or the Swapper/Symbolic Debugger) | Do not convert; use the vendor-documented alternate procedures in the HELP text's SIBAS topic instead [from HELP] |
