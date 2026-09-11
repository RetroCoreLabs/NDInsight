# NC-A06 - Norsk Data C compiler (version A06, 1989-01-10)

## Overview

NC is Norsk Data's C compiler for the ND-500. It is an interactive command
shell (prompt `NC:`) that drives the C build phases: preprocess, syntax check,
code generation, a combined compile, and a link. The real vendor compile flow
does not do everything in one step; it runs CHECK to produce a `:CAT`
intermediate, then GENERATE-CODE to turn that into a relocatable `:NRF` object
via the CAT_COMPILER back end (the CAT-CAT5 domain). The resulting `:NRF` is
then linked into a runnable `.DOM` with LINKER-B01.

Banner printed at start [verified]:
`Norsk Data C - Version: A06 - 1989-01-10`

See the shared conventions in [../README.md](../README.md) for install, the
sintran-root layout, and the requirements model.

## Files (in files/)

| File | Purpose |
|---|---|
| `NC-A06.DOM` | The compiler domain (the program you run). ND-500 root domain, entry `0x08000004`, linker v97.251. |

NC does not ship a `.HELP` or `.INIT` in this folder. It can, at run time,
read/write a per-user init file `NC-A:INIT` (host `NC-A.INIT`) holding the
default option string (see Commands and options). That file is optional; when
absent NC just uses built-in defaults [verified].

## Requirements

- To RUN NC: only `NC-A06.DOM` [verified].
- The CHECK -> GENERATE-CODE flow needs the CAT-CAT5 back end
  (CAT_COMPILER) present in SYSTEM. GENERATE-CODE hands off to it, and the
  console prints `programCAT_COMPILER terminated` on success [verified]. See
  `../CAT-CAT5-B06/`.
- To COMPILE + LINK a C program end to end you also need the C runtime
  libraries and the C linker auto-job (all in
  [../_shared/files/](../_shared/files/)) [verified]:
  - `NC-LIB.NRF`, `CAT-LIB.NRF`, `USLIB3.NRF`
  - `LINKER-AUTO-C.JOB`
- Known media gap: `FORTRAN-LIB` and `EXCEPT-LIB` are missing from all media,
  so the linker's default FORTRAN auto-job cannot resolve its exception
  handlers. The C path works around this with the self-contained
  `LINKER-AUTO-C.JOB`. See [../README.md](../README.md) and the memory note
  `nc-link-fortran-autojob-missing-libs` [verified].

## How to run

Start the SINTRAN shell as described in [../README.md](../README.md), then type
the bare name `NC-A06` at the `@` prompt (the `@` is the prompt, do NOT type
it).

Interaction model [verified]: NC prints its banner, then reads input one
character at a time starting from device 0 (the SINTRAN command buffer, i.e.
the initial argument line). The `NC:` prompt does not appear until the first
carriage return; on that first CR NC switches its input to the terminal
(device 1). So an interactive session needs a leading CR before the first
typed command.

The reliable, run-verified way to compile is a MODE file that runs CHECK then
GENERATE-CODE. Scripted example that produces a real `HELLO.NRF` [verified]:

```sh
# create MODE file COMPILE-HELLO.MODE in the user area with these lines:
#   CREATE-FILE HELLO:CAT
#   CREATE-FILE HELLO:LIST
#   CREATE-FILE HELLO:NRF
#   NC-A06
#   CHECK HELLO,HELLO,HELLO
#   GENERATE-CODE HELLO,HELLO
# then drive the emulator non-interactively:
printf 'LOGIN GUEST\nMODE COMPILE-HELLO\n' | ./build/bin/nd500x --monitor \
    --user GUEST --sintran-root ~/ND500USERS
```

That run writes a real `HELLO.NRF` and prints `programCAT_COMPILER terminated`
cleanly [verified].

Interactive alternative: type `NC-A06`, press Enter once to get `NC:`, then
`CHECK HELLO,HELLO,HELLO`, then `GENERATE-CODE HELLO,HELLO`, then `EXIT`.

## Commands and options

Command set from NC's own built-in `help` [from HELP]. Notation: `<x: >` is a
value NC prompts for, `[...]` optional, `...` repeatable.

| Command | Arguments / prompts |
|---|---|
| `compile` | `<source file>,<list file>,<object file>` |
| `preprocess` | `<source file>,[<list file>],[<output file>]` |
| `check` | `<source file>,[<list file>],[<CAT file>]` |
| `generate-code` | `<CAT file>,<object file>` |
| `link` | `<source file>,<program>` |
| `cross` | `<source file>,<cross reference file>,<lines per page>` |
| `format` | `<source file>,<new source file>` |
| `define` | `[<macro identifier [(identifier,...)]>],[<value>]` |
| `undef` | `[<macro identifier>]` |
| `directory` | `[<include directory/user>]` |
| `options` | `<option>...` (repeatable) |
| `library` | `<library file>...` (repeatable) |
| `value` | `<definitions / options / libraries>` |
| `page-length` | `[<lines>]` |
| `initialize-compile-parameters` | `[<initialization file>]` (reads `NC-A:INIT`) |
| `save-compile-parameters` | `[<initialization file>]` (writes `NC-A:INIT`) |
| `clear` | reset compile parameters |
| `cc` | silent, returns to `NC:` |
| `help` | `<command>` (blank lists all) |
| `exit` | leave NC |
| `@<cmd>` | pass a command to SINTRAN |

File-name trap [verified]: NC treats a dot as part of the name and appends the
default type itself. Type the bare SINTRAN name (`HELLO`), not `HELLO.C`.
Default types NC appends: source `:C`, listing `:LIST`, object `:NRF`,
preprocessed `:PP`, intermediate `:CAT`.

Option string (default, written by `save-compile-parameters` into
`NC-A:INIT`) [verified]:

```
options m2  a4  f-  r4  l+  d+  n+  s-  p-  i-  o-  pr- ic+ lm+ t-  a-  lo+
```

Each token is `<flag><+|-|digit>`. Exact per-flag meanings are not confirmed
against an NC manual - treat individual flag semantics as [UNVERIFIED].

## Verified behaviour in nd500x

- Banner prints; command-buffer -> terminal input switch on first CR
  [verified].
- CHECK writes a `:CAT`, GENERATE-CODE drives the CAT_COMPILER back end and
  writes a real `:NRF`; console prints `programCAT_COMPILER terminated`
  [verified, 2026-07-31].
- The historical "no rewrite / terminated" symptom (the compiler only
  preprocessing and never generating code) was an emulator GETB-heap bug, since
  fixed; it was NOT a compiler-driver problem [verified]. The older analysis
  documents below describe that pre-fix behaviour.

## Known issues / status

- Runs end to end (CHECK + GENERATE-CODE) in nd500x [verified].
- Single-step "all in one" `compile` was the phase that surfaced the old
  GETB-heap bug; the run-verified path of record is the two-step
  CHECK -> GENERATE-CODE MODE flow above.
- Individual option-flag meanings in `NC-A:INIT` are not manual-confirmed
  [UNVERIFIED].

## Input & output files, FAQ, common errors (added 2026-09-11)

### Input

- **NC reads its first line from DEVICE 0, the SINTRAN command buffer (the
  initial argument line), NOT the terminal** [measured/doc, see "How NC talks
  to the terminal" in
  `analysis/nc-a06-usage-and-mon-contract.md` — `MON 503B DVINST` with
  `DevNo=0`, `MaxNo=1`, one character at a time]. This is the "NC-A06
  pattern": a bare monitor `run` with no command-buffer text leaves NC polling
  device 0 forever with nothing to answer it [measured, ND5000UC memory note
  `nc-reads-its-parameter-line-from-the-command-buffer.md` and BUGS.md
  headline table row for NC-A06].
- **The `NC:` prompt does not appear until the first carriage return.** On
  seeing a CR on device 0, NC prints `\r\nNC: ` and **switches its input to
  device 1** (the interactive terminal); every command after that is read
  character-by-character from device 1 [measured,
  `nc-a06-usage-and-mon-contract.md` §2].
- Two correct ways to drive it [doc, same reference §2]:
  1. **One-liner via device 0**: queue `COMPILE name,name,name\r` (or
     `CHECK ...\r` / `GENERATE-CODE ...\r`) **before** the banner even prints.
     NC consumes it as the initial command line.
  2. **Interactive**: send a bare `\r` first (this is what produces the
     `NC: ` prompt), then the command text on device 1.
  Sending an interactive command WITHOUT the leading `\r` is swallowed by the
  device-0 path and the prompt never appears [doc, same reference].
- **Measured failure (corpus701)**: `EXIT` typed as the very first thing sent
  (i.e. as the initial argument line, same mistake as sending a command
  without the leading CR) was consumed on device 0, and NC then parked on the
  next `503B` read at `0x0802E1F4` — banner printed, no `NC:` prompt, no
  further progress [measured, BUGS.md headline table: "NC-A06 | banner |
  no | EXIT went in as the INITIAL ARGUMENT LINE ... parked on the next 503B
  read"].
- **File-name trap**: NC treats a dot as part of the file name and appends
  its own default type — typing `B.C` makes NC look for host file `B.C.C`.
  Always type the bare SINTRAN name (`B`), never `B.C` [measured/doc]. Default
  types NC appends: source `:C`, listing `:LIST`, object `:NRF`, preprocessed
  `:PP`, intermediate `:CAT`.
- The run-verified compile path is **two-step**: `CHECK <src>,<list>,<cat>`
  then `GENERATE-CODE <cat>,<object>` — NOT the single `compile` command,
  which stops after preprocessing without invoking the code generator
  ["Known issues" section above, and §4 of the analysis doc].
- The reliable way to drive a compile non-interactively is a MODE file
  (`CREATE-FILE` the three outputs, then `NC-A06`, then `CHECK ...`, then
  `GENERATE-CODE ...`) — see the worked example in "How to run" above.
- Optional per-user init file `NC-A:INIT` supplies default compile options
  (read by `initialize-compile-parameters`, written by
  `save-compile-parameters`); absent is fine — NC just uses built-in defaults
  [verified].

### Output

- `CHECK` writes the intermediate **`:CAT`** file; `GENERATE-CODE` reads that
  `:CAT` and drives the **CAT-CAT5-B06** back end (`CAT_COMPILER`) to produce
  the relocatable **`:NRF`** object [verified]. The `:LIST` listing file is
  also created by `CHECK` per the command's argument list [doc, command
  table].
- **All three output files (`:CAT`, `:LIST`, `:NRF`) must be `CREATE-FILE`d
  in SINTRAN first** — same convention as PLANC — before `NC-A06`/`CHECK`/
  `GENERATE-CODE` run, per the working MODE-file example in "How to run"
  above [verified pattern; the userguide's own worked example creates all
  three before invoking NC].
- On success the console prints **`programCAT_COMPILER terminated`**
  [verified, 2026-07-31 run] — this string means the back-end sub-program
  finished cleanly, it is NOT an error despite the word "terminated".
- File MON calls used: `50B OPEN`, `117B RFILE`, `120B WFILE`, `76B SETBS`,
  `73B SMAX`, `62B RMAX`, `43B CLOSE`, `221B CRALF` (create), `54B MDLFI`
  (delete) — all byte-denominated, not word-denominated, on the ND-500
  [doc, `nc-a06-usage-and-mon-contract.md` §5-6]. `RFILE`/`WFILE`'s
  `BlockNo = -1` means "continue from the current position", not "seek to
  block -1" [doc, same reference — this was a real emulator bug, fixed
  2026-07-10, unrelated to how you invoke NC].
- **NC is a multi-pass front end, not a single monolithic compiler**: it
  parses to a `SCRATCH-00001:*` scratch area, writes a preliminary object
  image to a scratch segment (`MON 422B GSWSP GetScratchSegment`), and
  re-invokes later passes as **nested SINTRAN commands via `MON 317B UECOM`
  (ExecuteCommand)** — observed nested invocations are named `NC-A'` and
  `CAT-CAT5-B'` [doc/measured, task brief measured facts + `mon_registry`
  entry for `317B`/`UECOM` in the MON contract doc §5].
- **Requires `CAT-CAT5-B06` installed in SYSTEM.** Without it, `GENERATE-CODE`
  still appears to "succeed" in about 14 seconds but writes a **0-byte**
  `:NRF` — a silent failure, not a hang [measured, task brief]. Always check
  the `:NRF`'s byte size after a run, not just the exit code / `terminated`
  string.
- Terminal-input write path (relevant to why input can silently not arrive):
  SINTRAN delivers each line NC reads via `503B` using **`MON 11B DMEMWR`**
  to NC's ND-500 LOGICAL buffer address. On the octobus lane this was
  measured writing to the wrong (physical, not logical) address until fixed
  — **`B24` in `E:\Dev\Ronny\ND5000UC\BUGS.md`, fixed in corpus709**
  [measured, BUGS.md B24: "NC read ':' forever and never printed `NC:`" was
  the exact symptom before the fix]. If a run looks like NC is stuck reading
  forever with no echo, this class of bug (input never actually delivered)
  is the first thing to check on this lane, alongside the input-timing traps
  above.

### Good to know

- Banner is `Norsk Data C - Version: A06 - 1989-01-10` on device 1 via
  `MON 504B DVOUTS` [verified/doc].
- `NC` issues every monitor call through plain `CALL` (never `CALLG`) — 50
  call sites, 34 distinct MON numbers [doc, `nc-a06-usage-and-mon-contract.md`
  §1].
- `321B UEADM` is called once and is EXPECTED to return an error (52, K flag
  set) per the MON registry — it is a deliberately-deprecated call, not a
  bug if it fails [doc, same reference §5 note].
- `MON 32B MSG` is how NC prints its own diagnostic text (e.g. the historical
  `no rewrite` line from the pre-fix GETB-heap bug); `DVOUTS` is only used
  for the banner [doc, same reference §6].
- The historical "no rewrite / terminated" symptom (compiler only
  preprocessing, never generating code) was traced to an emulator GETB-heap
  bug and is now fixed — it was NOT a compiler-driver / command-syntax
  problem [verified, "Verified behaviour" section above].

### FAQ

- **Q: I typed `run` (or just started the DOM with no command line) and
  nothing but the banner ever appears.**
  A: Expected. NC is reading device 0 (the command buffer) one character at
  a time and there is nothing there. Either put your `CHECK .../GENERATE-CODE
  ...` line in the command buffer BEFORE start, or send a leading `\r` first
  to force it to the interactive `NC:` prompt on device 1 [measured/doc].
- **Q: I sent `EXIT` right after starting the program and it just hangs.**
  A: `EXIT` was consumed as the initial device-0 argument line, not as a
  command at the `NC:` prompt (which never appeared). Send a leading `\r`
  first if you want an interactive session [measured, corpus701].
- **Q: I typed `check B.C,B,BCHK` and it can't find my file.**
  A: NC appended its own type on top of the one you typed — it looked for
  `B.C.C`. Use the bare name `B`, not `B.C` [measured].
- **Q: `compile B,B,BOUT` runs, prints `preprocessing`, then `no rewrite` /
  ` terminated` and exits.**
  A: The single-command `compile` path is not the run-verified path on this
  lane (it stops after preprocessing on some builds — see "Known issues").
  Use the two-step `CHECK` then `GENERATE-CODE` MODE-file flow instead
  [verified].
- **Q: `GENERATE-CODE` reports `programCAT_COMPILER terminated` (looks like
  success) but my `.NRF` has 0 bytes.**
  A: `CAT-CAT5-B06` is not installed in SYSTEM. Install it (see
  `../CAT-CAT5-B06/`) and re-run [measured].
- **Q: The program looks stuck reading forever after I typed a line at the
  `NC:` prompt, and nothing echoes back.**
  A: On the octobus lane this was `B24` (BUGS.md) — SINTRAN's terminal-input
  delivery wrote your character to the wrong physical address instead of
  NC's logical buffer, so NC never saw it. Confirmed fixed as of corpus709;
  if you see it again, it has regressed [measured].

### Common errors and how to fix them

| Symptom | Cause | Fix |
|---|---|---|
| Only the banner ever prints, program appears hung | No text was queued in the SINTRAN command buffer (device 0) and no leading `\r` was sent | Either preload `CHECK ...`/`GENERATE-CODE ...` on the command line before start, or send a bare `\r` first to reach the interactive `NC:` prompt [measured/doc] |
| `EXIT` (or any command) sent immediately after start does nothing | Consumed as the device-0 initial argument line before the `NC:` prompt existed | Send a leading `\r` first if the intent was an interactive command [measured, corpus701] |
| "Ambiguous file name" / file not found for a name with a dot in it | NC appended its own default type onto the dotted name (`B.C` -> `B.C.C`) | Use the bare SINTRAN name (`B`), let NC append `:C`/`:LIST`/`:NRF`/etc. itself [measured] |
| `compile` prints `preprocessing` then `no rewrite` / ` terminated`, no object produced | Single-command `compile` stops after preprocessing (known limitation on this build) | Use the two-step `CHECK <src>,<list>,<cat>` then `GENERATE-CODE <cat>,<obj>` MODE-file flow [verified] |
| `GENERATE-CODE` reports "terminated" cleanly but `:NRF` is 0 bytes | `CAT-CAT5-B06` not installed | Install `CAT-CAT5-B06` in SYSTEM before compiling [measured] |
| `SINTRAN ERROR 56B` opening `:CAT`/`:LIST`/`:NRF` | Output file not `CREATE-FILE`d first | `CREATE-FILE` all three output files before running `NC-A06` (see MODE-file example) [pattern from "How to run"] |
| Typed input never echoes / NC reads the same character forever | Octobus-lane terminal-input delivery bug (B24, BUGS.md) writing to the wrong physical address | Confirm the servicer fix (corpus709) is in place; this is a transport bug, not a usage error [measured] |

## References

- [analysis/nc-a06-usage-and-mon-contract.md](analysis/nc-a06-usage-and-mon-contract.md) - command table, terminal model, and the 34-MON-call contract
- [analysis/NC-INTERFACE.md](analysis/NC-INTERFACE.md) - terminal/command interface probe results
- [analysis/nc-a06_analysis.md](analysis/nc-a06_analysis.md) - deep binary/disassembly analysis
- [analysis/nc-a06.asm](analysis/nc-a06.asm) - ND-500 disassembly
- [../README.md](../README.md) - shared install/run conventions and requirements model
- [../CAT-CAT5-B06/](../CAT-CAT5-B06/) - the CAT compiler back end NC hands off to
- [../LINKER-B01/](../LINKER-B01/) - linking the resulting `:NRF` into a `.DOM`
- ND-500 monitor-call analysis: [../../ND500/](../../ND500/) and [../../../Developer/MON/calls/](../../../Developer/MON/calls/)
