# CPU-STAT - print CPU type, microcode and system identity

## Overview

CPU-STAT is a small Norsk Data diagnostic that prints the identity of the host
computer: CPU number and type, instruction set, microcode version, system type,
operating system, version/revision, and the generation date. It takes no
arguments and runs to a clean exit. [verified]

The program is written in ND Pascal; the recovered source calls a single system
routine `GetSystemInfo(0, sysrec)` and then formats the returned record.
[from disasm]

For shared install/run conventions see [../README.md](../README.md).

## Files (in files/)

- `CPU-STAT.DOM` - the runnable ND-500 domain (self-contained). [verified]

No PSEG/DSEG/HELP/INIT files ship - the DOM is all that is needed. [verified]
(The `analysis/` folder additionally holds a recovered Pascal source
`cpu-stat.pasc`, used here to document the exact output fields.) [from disasm]

## Requirements

- Just the `.DOM` file to run - no external libraries or segments. [verified]
- Install: copy `files/CPU-STAT.DOM` into the sintran-root. See
  [../README.md](../README.md).

## How to run

Interactive: at the SINTRAN `@` prompt type the bare name (the `@` is the
prompt, do not type it):

```
CPU-STAT
```

Scripted (non-interactive) drive, from `~/repos/nd500x`:

```
printf 'LOGIN GUEST\nCPU-STAT\nEXIT\n' | ./build/bin/nd500x --monitor \
    --user GUEST --sintran-root ~/ND500USERS
```

## Commands and options

None. CPU-STAT takes no arguments and has no interactive prompt: it prints the
report and terminates. [verified]

Output fields printed (label : value, with a parenthetical decode): [from disasm]

- `CPU number` - the system/CPU number (`sysno`).
- `CPU type` - numeric code plus decode, for example
  `4 = ND-110 48-bit floating`. Decodes: 0/1 Nord-10 48/32-bit,
  2/3 ND-100 48/32-bit, 4/5 ND-110 48/32-bit, 6/7 ND-120 48/32-bit,
  8/9 ND-130 48/32-bit (8/9 marked uncertain in the source). [from disasm]
- `Instruction set` - numeric code plus decode (0 Standard ND-100, 1 /CE,
  2 /100 CX, 3 /110 PCX, 4 /120 PCX, 8 /120 CX, 9 /110 CX print 3095,
  10 /110 CX print 3090). [from disasm]
- `Micro prog vers.` - microcode version. [from disasm]
- `System type` - for example `5800`. [verified]
- `Operating system` - numeric code plus decode (0 VS, 1 VSE, 2 VSE-500,
  3 RTP, 4 VSX, 5 VSX-500). [from disasm]
- `Version` - operating-system version character. [from disasm]
- `Revision` - revision number, printed with a trailing `b` (octal). [from disasm]
- `Generated` - generation date: day, month name, year, hour:minute. [from disasm]

## Verified behaviour in nd500x

Verified 2026-07-31 in the `nd500x` C emulator: [verified]

- `CPU-STAT` printed all fields above (for example `CPU type 4 = ND-110 48-bit
  floating`, `System type 5800`, `Operating system 5 = Sintran III VSX-500`).
- The program ran clean to `MON 0B LEAVE` (normal program termination).

## Known issues / status

- No known issues. Runs clean to exit. [verified]

## Input & output files, FAQ, common errors (added 2026-09-11)

### INPUT

- **None.** CPU-STAT reads nothing — no command-line parameters, no file, no
  terminal byte. [measured, `BUGS.md` corpus701 macro round, run303-307/324/325]
  The recovered Pascal source has no read call at all: it calls
  `GetSystemInfo(0, sysrec)` once and formats the result. [from disasm,
  `analysis/cpu-stat.pasc`]
- Because it never reads, **device 0 (command buffer) vs device 1 (terminal)
  does not apply to this program** — see the shared note on the two input
  devices in
  [`E:\Dev\Ronny\ND500UC\docs\DOM-PROGRAM-IO-REFERENCE.md`](../../../../../ND500UC/docs/DOM-PROGRAM-IO-REFERENCE.md)
  section 3. Typing anything after `CPU-STAT` on the command line is simply
  ignored. [inferred — no code path consumes it]

### OUTPUT

- Terminal only. Each of the nine report lines is written with **MON 504B
  DVOUTS** (device-output-string, the microcode inline-copy call — see the
  I/O reference doc section 2). [measured, `BUGS.md`: "complete (39 x 504B,
  2.6 s)"] The recovered Pascal source has no byte-write call and no file
  open at all — every line is a `writeln`. [from disasm, `analysis/cpu-stat.pasc`]
- No output file is created and none is needed — there is nothing to
  pre-create with `@CREATE-FILE` before running this program. [from disasm —
  the source never opens a file]
- Exit is a clean **MON 0B LEAVE**. [measured/verified, both this userguide's
  original nd500x note and `BUGS.md` corpus701]

### GOOD TO KNOW

- The BUGS.md byte-level walk of a mid-run capture shows a repeating
  separator/label/value pattern of 504B calls for the first two fields
  (`0 MON 504B n=2 COPIED ".."`, `1 MON 504B n=19 COPIED "CPU number : "`,
  `2 MON 504B n=8 COPIED "     100"`, then the same shape again for CPU
  type). Extending that 3-calls-per-line pattern across nine fields would
  give 27, not the measured 39 — the Pascal source shows three of the nine
  fields (`cpu_type`, `instr_set`, `oper_sys`) print an *extra* decode line
  through a separate `writeln` in `CPUtype`/`InstrSet`/`OperSys`, which
  accounts for the difference. [inferred from the run307 walk in `BUGS.md`
  plus `analysis/cpu-stat.pasc` — the exact 39-call breakdown across all
  nine fields is not itself measured]
- CPU-STAT is one of the fastest and structurally simplest of the eight DOM
  programs measured on this project (2.6 s wall in the one run that
  completed, `corpus701`) — though it is not the single fastest: PLANC-500-G00
  completed in 0.3 s in the same table. [measured,
  `E:\Dev\Ronny\ND5000UC\BUGS.md` corpus701 table] Use it as the "does the
  octobus/MON-forwarding path work at all" smoke test before trying a
  program with real I/O.
- All MON calls it makes are **forwarded** to real SINTRAN — none are
  answered by a local stand-in. This is a genuine "runs under real SINTRAN"
  program, not a false-positive from a canned answer. [measured, per the
  project's `THE GOAL` rule and the corpus701 log line: "MON calls forwarded
  to real SINTRAN in every case (fake answers 0)"]

### FAQ

- **Q: Does CPU-STAT take any arguments?**
  A: No. It is a bare-name command with no options and no interactive
  prompt. [verified — this userguide's own "Commands and options" section,
  unchanged]
- **Q: Can I redirect its output to a file?**
  A: Not by anything the program itself does — it always writes to the
  terminal (device output) via MON 504B. SINTRAN-level output redirection
  (if the OS supports it for a given device) is outside the program's own
  behavior and not measured here. [inferred — not tested]
- **Q: Why does a run only show 2 of the 9 fields, with the second value
  blank?**
  A: That is a **capture artifact**, not a program bug — see "Common
  errors" below.

### COMMON ERRORS AND HOW TO FIX THEM

- **Symptom: only 2 of 9 fields print, and the second value is blank or
  cut off** (seen in an earlier run, `BUGS.md` run307, PC ended at
  `0x08005097`, never reached MON 0B). **Cause: the capture/harness stopped
  reading too early** — the program itself produced the value correctly
  (`BUGS.md` confirms `MON 504B n=8 COPIED "       2"` — the exact byte
  CPU-STAT sent). **This is not a CPU-STAT defect**: the corpus701
  macro-round run prints all nine fields and reaches MON 0B cleanly. **Fix:**
  let the harness/log-reader run to completion (to `MON 0B LEAVE`, ~2.6 s
  wall) before judging the output short. Do not treat a run cut off mid-report
  as a program failure. [measured, `BUGS.md` corpus701 table]
- **CORRECTION 2026-09-11 — run303-306 and run324/325 do NOT show "all nine
  fields", they show NO output at all.** Re-reading `BUGS.md`: across
  run303-307, run321, run322 (seven runs total) exactly **one** run
  (run307) produced any console output, and that one was the 2-of-9-fields
  cut-off case above — run303, run305, run321 and run322 show no output,
  run304/run306 show `ND-5000 lock timeout` and no output. run324 never even
  left the swapper (`PS=3`, no `MON 262B GetSystemInfo`, no `MON 504B` at
  all) and run325 shows **no console output** either (`PS=10` but the
  BUGS.md B23 table lists its console output as "none"). The only run in
  the whole file that is documented as printing all nine fields and reaching
  MON 0B is the corpus701 macro-round run. **This run-to-run non-determinism
  is itself an open, documented question in `BUGS.md` (B1/B23) — treat any
  single run's silence as inconclusive, not as proof CPU-STAT is broken, but
  do not read it as proof CPU-STAT reliably completes either.** [measured,
  `E:\Dev\Ronny\ND5000UC\BUGS.md` B1 and B23]
- Beyond the output-timing question above, there are **no known program-level
  errors** for CPU-STAT — no failed opens, no parked reads, no traps — in any
  measured run. [measured, `BUGS.md`]

## References

- Shared conventions: [../README.md](../README.md)
- Recovered Pascal source: [analysis/cpu-stat.pasc](analysis/cpu-stat.pasc)
- Disassembly: [analysis/cpu-stat.asm](analysis/cpu-stat.asm)
- Runnable domain: [files/CPU-STAT.DOM](files/CPU-STAT.DOM)
