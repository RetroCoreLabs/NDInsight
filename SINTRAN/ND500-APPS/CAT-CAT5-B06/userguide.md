# CAT-CAT5-B06 - CAT compiler code-generation back-end (used by NC)

## Overview

CAT-CAT5-B06 is the Norsk Data CAT compiler code-generation back-end
(the "CAT_COMPILER"), version B06, 1988. [verified]

It is NOT normally run directly by a user. It is the code generator invoked BY
the NC-A06 C compiler during its GENERATE-CODE step: NC nests it through the
SINTRAN monitor call MON 317B (UECOM). When it finishes it prints
`program CAT_COMPILER terminated`. [verified]

For shared install/run conventions see [../README.md](../README.md).

## Files (in files/)

- `CAT-CAT5-B06.DOM` - the runnable ND-500 domain (the back-end itself).
  [verified]

The `analysis/` folder is empty - no disassembly or RE notes are present for
this program. [verified]

## Requirements

- The `.DOM` file. [verified]
- The CAT run-time library `CAT-LIB` (shared), at
  [../_shared/files/CAT-LIB.NRF](../_shared/files/CAT-LIB.NRF). [from disasm]
- Because it is driven by NC, the full C toolchain requirements apply: NC's
  libraries and the C linker auto-job (`NC-LIB`, `CAT-LIB`, `USLIB3`,
  `LINKER-AUTO-C.JOB`), all in [../_shared/files/](../_shared/files/). See
  [../README.md](../README.md) "Requirements model".
- Install: copy `files/CAT-CAT5-B06.DOM` and the shared libraries into the
  sintran-root. See [../README.md](../README.md).

## How to run

Normally you do NOT run this directly - you run the NC C compiler, which invokes
CAT as its back-end. See the NC-A06 userguide for the C compile chain.

Indirect (normal) use, via NC, scripted from `~/repos/nd500x`:

```
printf 'LOGIN GUEST\nNC-A06\nCOMPILE HELLO\nGENERATE-CODE\nEXIT\n' | \
    ./build/bin/nd500x --monitor --user GUEST --sintran-root ~/ND500USERS
```

(NC's GENERATE-CODE step nests CAT-CAT5-B06 through MON 317B UECOM.) [verified]

Direct invocation by typing the bare name `CAT-CAT5-B06` at the `@` prompt is
possible in principle but is not the intended interface; the program expects to
be driven by NC with the intermediate files NC produces. [UNVERIFIED direct use]

## Commands and options

Not user-facing. CAT-CAT5-B06 has no documented interactive command set of its
own - it takes its input (the intermediate representation) and control
parameters from NC through the nested UECOM invocation. [verified]

No `.HELP` file ships and `analysis/` is empty, so no command/option list could
be extracted. [verified]

## Verified behaviour in nd500x

Verified 2026-07-31 in the `nd500x` C emulator: CAT-CAT5-B06 runs when nested by
NC's GENERATE-CODE step and prints `program CAT_COMPILER terminated` on
completion. [verified]

## Known issues / status

- Runs as the NC back-end (driven indirectly). [verified]
- No standalone command interface is documented; treat it as an internal
  component of the C toolchain, not a user tool. [verified]
- No disassembly/RE notes available in `analysis/`. [verified]

## Input & output files, FAQ, common errors (added 2026-09-11)

### INPUT

- **It is never started from a plain command line.** NC-A06 invokes it
  through **MON 317B ExecuteCommand (short name UECOM)**, passing the
  abbreviated command text `'CAT-CAT5-B'` as a length+pointer descriptor
  (SINTRAN command abbreviation resolves this to CAT-CAT5-B06). [verified,
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\317B_ExecuteCommand.yaml`,
  `observed_calls`]
- Once running, CAT-CAT5 does **not** read from the SINTRAN command buffer
  (device 0) the way a directly-typed program would — its real "input" is
  the intermediate C code NC's front end already wrote to the **always-open
  scratch file** (SINTRAN file number 0100 octal = 64 decimal,
  `SCRATCHnn:DATA`). [verified, same yaml, `observed_calls` note] It reaches
  that scratch segment via **MON 422B GetScratchSegment (GSWSP)** as part of
  its fixed startup sequence. [measured,
  `E:\Dev\Ronny\NDInsight\Developer\MON\calls\422B_GETSCRATCHSEGMENT.yaml`:
  "CAT-500 issues GSWSP as part of its fixed startup sequence"]
- After startup it prints its `Cat-500:` prompt and then reads commands one
  byte at a time via **MON 503B DVINST** (device input). [verified, same
  317B yaml: "prints its banner and 'Cat-500:' prompt, then reads commands
  via 503B DVINST"] Whether that read is device 0 or device 1 in a given run
  is not separately measured here — see the general two-device rule in
  [`E:\Dev\Ronny\ND500UC\docs\DOM-PROGRAM-IO-REFERENCE.md`](../../../../../ND500UC/docs/DOM-PROGRAM-IO-REFERENCE.md)
  section 3. [OPEN]
- Direct invocation by typing the bare name `CAT-CAT5-B06` at the `@` prompt
  is possible in principle but is not the intended interface (unchanged
  from the userguide's existing note above). [UNVERIFIED direct use]

### OUTPUT

- Its fixed startup sequence issues, in order: **11B TIME, 114B TUSED, 143B
  RSIO, 422B GSWSP, 41B ROBJE, 76B SETBS, 62B RMAX, 73B SMAX**, then **504B
  DVOUTS** (its banner line) and **503B DVINST** (the prompt read).
  [verified, `422B_GETSCRATCHSEGMENT.yaml` observed_calls]
- Banner and prompt text go out via **MON 504B DVOUTS**, the same
  whole-buffer, microcode-inline-copy call CPU-STAT uses (see
  `E:\Dev\Ronny\ND500UC\docs\DOM-PROGRAM-IO-REFERENCE.md` section 2).
  [verified]
- **The object-code output ("code generation") does not happen on this
  emulator today.** MON 317B is a **stub** here — it decodes and logs the
  command string but never actually invokes the back end as a nested
  subsystem. Result: `BOUT.NRF` (the intended compiled object) is always
  0 bytes, because CAT-CAT5 never actually runs the write. [verified,
  `317B_ExecuteCommand.yaml`: "THIS STUB IS WHY BOUT.NRF WAS ALWAYS 0
  BYTES... Both emulators stub 317B, so the code generator never runs and
  the scratch file is never turned into an object."]
  **CORRECTION 2026-09-11 — the "stub, always 0 bytes" claim is LANE-SCOPED,
  not universal. Verified by reading
  `E:\Dev\Repos\Ronny\RetroCore\Emulated.HW\ND\CPU\ND500\Sintran\MON_317_UECOM.cs`:**
  (1) that file is gated `#if SINTRAN_EMULATION`, so on the **octobus /
  real-SINTRAN lane 317B is FORWARDED** and real SINTRAN does the nesting —
  the 0-byte NRF there means CAT-CAT5 is not installed / the nested run never
  reached the generator, NOT a handler stub. (2) Even on the C# fake-MON lane
  the handler runs the nested program re-entrantly **when an
  `ExecuteCommandHook` runner is registered** (`r==0` = it produced output);
  it is a benign log-only stub **only when no runner is wired**. (3) On the
  nd500x / classic 3022 lanes the compile produces a **byte-exact** NRF
  (md5 `80455983fe51dce56307e13cc23d33cf`). The `317B_ExecuteCommand.yaml`
  note predates the hook path. See the lane breakdown in
  `E:\Dev\Ronny\ND500UC\docs\DOM-PROGRAM-IO-REFERENCE.md` section 7.
  The strings recovered
  from its own `.DOM` confirm the intended output-file path: `"can't open
  CAT file"`, `"can't map scratch file into memmory"` [sic, in the binary],
  `"can't write to object file"`. [verified, same yaml, `verified` claims
  list]
- **Create convention:** not exercised in any completed run — CAT-CAT5 never
  reaches its own file-open/write for the object file in the measured runs,
  so the OPEN/FOPEN quoted-create rule from the I/O reference doc (section
  4, "File output — the create convention is the gotcha") has not been
  proven for this program specifically. [OPEN]
- On a **completed** run (corpus701, macro round) it prints its banner,
  `Cat-500: EXIT`, and `program CAT_COMPILER terminated`, then reaches
  **MON 0B** cleanly (1.3 s). [measured, `E:\Dev\Ronny\ND5000UC\BUGS.md`
  corpus701 table] This is a DIFFERENT, later run than run319/run326 below
  — see "Common errors."

### GOOD TO KNOW

- CAT-CAT5-B06 is the **code-generation back end of the C compiler**: NC-A06
  writes machine-independent "CAT code" to the scratch file, then nests
  CAT-CAT5-B06 through MON 317B to turn that into an object file. Without
  it installed, a C compile silently produces a 0-byte `.NRF`. [verified,
  `317B_ExecuteCommand.yaml`]
- Being nested rather than typed means CAT-CAT5's success/failure is only
  visible through **NC-A06's** compile output — there is no independent
  "run CAT-CAT5 and see if it worked" outside of the compile chain, other
  than the direct (unsupported) bare-name invocation this userguide already
  notes as unverified.
- **CORRECTION 2026-09-11 — "same build" is not supported.** Two different
  outcomes have been measured for CAT-CAT5: run319 printed its banner and
  reached the `Cat-500:` prompt (then idled an hour); run326 printed
  **nothing at all** and ended in process segment 3 (still in the swapper),
  never reaching the DOM. But `BUGS.md`'s own table (the B23 section) marks
  run319's build as **"earlier"** and run326's as **"same commit"** (i.e.
  same as the reference build used for run324/325) — the two CAT-CAT5 runs
  are explicitly NOT recorded as the same build. [measured,
  `E:\Dev\Ronny\ND5000UC\BUGS.md` B23 table: "run319 | CAT-CAT5 | earlier |
  ... | run326 | CAT-CAT5 | same commit | ..."]
  This means a "no output" result from CAT-CAT5 is not on its own proof of
  a program-level bug — the run may simply not have left the swapper — but
  it cannot be pinned to "same build, different outcome" either, since the
  builds differed.
- The stall at the `Cat-500:` prompt (see B10 below) was seen alongside a
  heap-allocation trap (`GETB: no heap blocks available for size 2^10`) in
  the two programs that get furthest through this toolchain (CAT-CAT5 and
  NC-A06). This is flagged in BUGS.md as a plausible shared cause, not yet
  confirmed. [OPEN, `E:\Dev\Ronny\ND5000UC\BUGS.md` line ~1402-1519]

### FAQ

- **Q: Can I run CAT-CAT5-B06 directly to compile something?**
  A: No — it has no documented command/option set of its own and expects
  its input already prepared by NC's front end. Run **NC-A06** and let it
  invoke CAT-CAT5 automatically at the GENERATE-CODE step. [verified]
- **Q: Why is the compiled `.NRF` file always empty (0 bytes)?**
  A: It depends on the lane (see the CORRECTION near the top of this section
  and section 7 of the central I/O reference). On the C# **fake-MON lane**
  with **no `ExecuteCommandHook` runner wired**, MON 317B logs the nested
  command but does not run it, so no object code is generated — a known
  emulator gap, not a CAT-CAT5 defect. On the **octobus / real-SINTRAN lane**
  317B is FORWARDED and a 0-byte NRF instead means CAT-CAT5 is not installed
  or the nested run never reached the generator. On nd500x/classic the NRF is
  byte-exact. [verified, `MON_317_UECOM.cs`; `317B_ExecuteCommand.yaml`
  emulation.note predates the hook path]
- **Q: CAT-CAT5 printed nothing this run — is it broken?**
  A: Check whether the process ever left the swapper (end process segment
  3 = still in swapper, vs 10 = reached the domain). A silent run that
  ended in segment 3 is a scheduling/paging outcome, not evidence the
  program itself failed — see run326 vs run319 above. [measured]

### COMMON ERRORS AND HOW TO FIX THEM

- **Symptom: reaches `Cat-500:` prompt then stalls for the whole run window
  (up to 3600 s), ending in a WAIT state after 64 page-ins and 208
  restarts** (BUGS.md B10's exact counts — corrected 2026-09-11 from a
  vaguer "dozens", which understated the restart count). This is `BUGS.md`
  **B10**: "CAT-CAT5 reaches its prompt and
  then does nothing for an hour" — the same `MON 1B`-shaped wait pattern as
  other prompt-driven programs that never got a command typed at them.
  **Fix:** the prompt is a real read waiting for a command; supply one (or
  an EXIT) instead of leaving the run to idle. [measured, `BUGS.md` B10]
- **Symptom: run produces a 0-byte object file (`BOUT.NRF`) even though NC
  reports success.** **Cause — lane-dependent (see the CORRECTION above):**
  on the C# fake-MON lane with no `ExecuteCommandHook` runner wired, MON 317B
  logs but does not nest CAT-CAT5's code-generation, so nothing writes the
  object. On the octobus / real-SINTRAN lane 317B is FORWARDED, so a 0-byte
  NRF there means CAT-CAT5 is not installed / the nested run never reached the
  generator. **Fix:** octobus lane — install CAT-CAT5-B06 and confirm the
  nested run reaches the generator; fake-MON lane — wire the
  `ExecuteCommandHook` runner (`MON_317_UECOM.cs`), currently the open gap.
  [verified, `MON_317_UECOM.cs`; `317B_ExecuteCommand.yaml`]
- **Symptom: no console output at all, process ends in segment 3.** Seen in
  run326, against a run that DID print the banner (run319) — but per the
  CORRECTION above, `BUGS.md` records these as **different builds**
  (run319 "earlier", run326 "same commit" as the reference), so this pair
  does NOT show same-build divergence; it only shows that ending in segment
  3 (still in the swapper) is not itself proof CAT-CAT5 regressed. **Fix:**
  re-run on a matched build; check the end process segment before concluding
  CAT-CAT5 itself regressed. [measured, `BUGS.md` B23 table]
- The corpus701 **macro-round** run (the one this project treats as
  authoritative for "does it complete") DID complete cleanly: banner,
  `Cat-500: EXIT`, `program CAT_COMPILER terminated`, MON 0B, 1.3 s.
  [measured, `BUGS.md` corpus701 table] Treat run319/run326's stalls as
  earlier/different conditions, not the current expected behavior.

## References

- Shared conventions: [../README.md](../README.md)
- Shared CAT library: [../_shared/files/CAT-LIB.NRF](../_shared/files/CAT-LIB.NRF)
- NC C compiler (the caller): [../NC-A06/userguide.md](../NC-A06/userguide.md)
- Runnable domain: [files/CAT-CAT5-B06.DOM](files/CAT-CAT5-B06.DOM)
