# :PROG File Format Reference

**Full path:** `PROG-FILE-FORMAT.md`

A comprehensive description of the SINTRAN III `:PROG` (program) file format used
by the Nord Relocating Loader (NRL), the SINTRAN `@DUMP` / `@RECOVER` commands,
and (in extended form) by the ND-500 Loader Monitor (NLL) when running in
COMPUTER-MODE 100.

> **Authoritative sources used to compile this document**
> - `Reference-Manuals/ND-60.066.04 ND Relocating Loader.md` - sections 1.1.4,
>   1.1.6, 1.1.7, 1.4.2 and Appendix A
> - `Reference-Manuals/ND-60.136.04A ND-500 Loader Monitor.md` - section on
>   COMPUTER-MODE 100 (`:PROG` produced by NLL)
> - `Reference-Manuals/ND-60.096.01 MAC ... User's Guide.md` - section 5.5
>   (the related `:BPUN` absolute-binary format that `:PROG` is contrasted with)
> - `Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md` - `@DUMP`, `@RECOVER`,
>   `@PLACE-BINARY`, `@DUMP-PROGRAM-REENTRANT`
> - `SINTRAN/OS/SEGMENTS-INTRO-AND-DEEP-DIVE.md` - how `@RECOVER` maps a PROG
>   file into a background segment
>
> Anything not directly attested in those sources is marked **UNVERIFIED** or
> **ASSUMPTION**.

---

## 1. What a :PROG File Is

A `:PROG` file is a **memory image** of a loaded and linked program, stored on
a SINTRAN III mass-storage file with default file type `:PROG`. Unlike `:BRF`
(Binary Relocatable Format) it is **not relocatable** - all symbols have already
been resolved by the NRL and the program occupies fixed virtual addresses inside
a 64KW (one bank) or 2x64KW (two bank) ND-100/NORD-10 address space.

A `:PROG` file is "ready for execution": SINTRAN can bring it back into the
caller's address space with a single `@RECOVER` command, set the program counter
to the recorded start address, and the program runs.

| Aspect | `:BRF` | `:BPUN` | `:PROG` |
|---|---|---|---|
| Relocatable? | Yes | No | No |
| Contains symbol info? | Yes | No | No |
| How produced | Compiler / assembler | NRL `*BPUN` or MAC `)BPUN` | NRL `*DUMP` / `*PROG-FILE`, or SINTRAN `@DUMP` |
| How loaded | NRL `*LOAD` | `@PLACE-BINARY`, hardware loader, MAC `)9READ` | `@RECOVER` (or NLL `$RECOVER` for NLL-built ND-100 PROG files) |
| Bootstrap embedded? | No | Yes (44 octal locations) | No |
| Direct execution | No (must be linked) | Yes after `@PLACE-BINARY` | Yes |
| Default file type | `:BRF` | `:BPUN` | `:PROG` |

> Source: `ND-60.066.04` sections 1.1.4 and 1.1.7;
> `SINTRAN/OS/SEGMENTS-INTRO-AND-DEEP-DIVE.md` table at line 1185-1187.

---

## 2. How a :PROG File Is Produced

There are four documented production paths:

### 2.1 NRL `*DUMP` (basic / image-file mode)

```
*DUMP <destination file name>[<start address><restart address>]
```

- The currently loaded program (whatever the loader has linked into its work
  area or into an `IMAGE-FILE`) is written to `<destination file name>`.
- Default file type if none is supplied: `:PROG`.
- The recorded **start address** is where execution begins under `@RECOVER`.
- The recorded **restart address** is where execution resumes under
  `@CONTINUE`. If the user does not specify them, the program's **main entry**
  is used for both.
- The dumped extent defaults to *the lowest through the highest address
  touched by the loader since the last RECOVER*. The user can override this
  with `*BOUNDARIES <lower> <upper>`.

> Source: `ND-60.066.04` lines 505-523 and Appendix A line 1657.

### 2.2 NRL `*PROG-FILE` (prog-file loading mode)

```
*PROG-FILE <file name>
... loading commands ...
*EXIT
```

- Must be the **first** loader command after entering NRL.
- All subsequent `*LOAD` commands write directly to the named file in absolute
  binary form rather than into the loader's in-memory work area.
- The **last** command must be `*EXIT`. (`*DUMP` and `*BPUN` are *not* allowed
  in this mode.)
- Default file type: `:PROG`.
- Resulting file is only executable via SINTRAN `@RECOVER`.

> Source: `ND-60.066.04` section 1.1.7, lines 571-577.

### 2.3 NRL `*IMAGE-FILE` followed by `*DUMP`

```
*IMAGE-FILE <file name>      ! file type defaults to :IMAG
... *LOAD ... *LOAD ...
*DUMP <prog file>
*EXIT
```

- Used for very large programs whose linked image will not fit in the loader's
  memory work area.
- The `:IMAG` file is a transient memory-image work file; the user then
  produces the deliverable `:PROG` from it with `*DUMP`.
- `*SET-LOAD-ADDRESS` may now address from 0 upwards.

> Source: `ND-60.066.04` section 1.1.6, lines 557-569.

### 2.4 SINTRAN `@DUMP` from a running address space

```
@DUMP <file name>, <start>, <restart>
```

- Captures the caller's current memory contents between the limits previously
  set by `@MEMORY` (or default boundaries) into a `:PROG` file.
- Used, for example, to save a hand-modified MON image: change a default with
  the operator commands, leave the monitor with `EXIT`, then `@DUMP` the
  result. The new `:PROG` file is functionally equivalent to the original
  monitor but with the modified defaults baked in.
- Permitted only for user SYSTEM in modern SINTRAN versions.

> Source: `Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md` line 8801 and
> entry `### DUMP` at line 2387; `ND-60.047.03 NORD PL User's Guide` line 3615.

### 2.5 NLL (ND-500 Loader Monitor) producing an ND-100 :PROG

When NLL is set with `COMPUTER-MODE 100`:

- Default object file type changes to `:BRF`.
- Code, data and debug information are placed on the `:PSEG` file but **in
  the same on-disk format as an ordinary ND-100 :PROG file**.
- The `:DSEG` file is not used.
- The resulting file is executed via NLL's `$RECOVER`.

> Source: `Reference-Manuals/ND-60.136.04A ND-500 Loader Monitor.md` line 3140.

---

## 3. Logical Structure of a :PROG File

The published Norsk Data manuals describe the `:PROG` file *operationally* -
they tell you what it must contain and how `@RECOVER` consumes it - rather than
giving a byte-by-byte field layout the way the BRF chapter (chapter 2 of
`ND-60.066.04`) does for `:BRF`. The fields below are the ones that the manuals
explicitly require to be present. Field offsets that are *not* documented in the
sources are marked **UNVERIFIED**.

### 3.1 Required logical fields (all variants)

| Field | Width | Purpose | Source |
|---|---|---|---|
| **Start address** | 1 word (16 bits) | Address loaded into the program counter on `@RECOVER`. Defaults to the program's main entry if `*DUMP` was issued without an explicit value. | `ND-60.066.04` line 511 |
| **Restart address** | 1 word | Address used when the program is resumed with `@CONTINUE`. Defaults to the same value as the start address. | `ND-60.066.04` line 511 |
| **Lower bound** | 1 word | Lowest virtual address covered by the dump. Set by `*BOUNDARIES` or by the lowest address the loader touched since the last `RECOVER`. | `ND-60.066.04` lines 511, 523 |
| **Upper bound** | 1 word | Highest virtual address covered by the dump. | as above |
| **Memory image** | (upper - lower + 1) words | The actual contents of the program's address space, in word order, from `lower` through `upper` inclusive. | implicit from `@RECOVER` behaviour described in `SEGMENTS-INTRO-AND-DEEP-DIVE.md` lines 1389-1392 |

> **ASSUMPTION:** the four control words above appear in a small fixed-format
> *header* at the start of the file, followed by the raw image. The manuals do
> not publish the order of the header words, only that all four pieces of
> information are stored in the file.

### 3.2 Additional fields for two-bank :PROG files

When the program was built in two-bank mode (separate code/program bank and
data bank), `*PROG-FILE` or `*DUMP` records additional information needed by
`@RECOVER` to populate the alternate page table:

| Field | Purpose | Source |
|---|---|---|
| **Data-bank file name** | Until the two-bank `RECOVER` is fully implemented in SINTRAN, the *data bank contents* are read back from the PROG file itself; the file therefore stores the file name (and optionally the user name) as supplied to the original `*PROG-FILE` or `*DUMP` command, so that `@RECOVER` can locate the right file when the user environment differs. | `ND-60.066.04` line 1011 |
| **Data-bank image** | The full 64KW (or `BOUNDARIES`-restricted) image of the alternate (data) bank. Loaded into the alternate memory bank by `@RECOVER`. | `ND-60.066.04` lines 1009-1015 |
| **Code-bank image** | The image of the program (code) bank. | as above |
| **(Optional) duplicated data area** | If the combined code+data fit inside one 64KW bank, the user may issue `*DATA-BANK-COPY` before the dump. The data area is then duplicated into the PROG segment *above the code* so that `@RECOVER` can initialise the data bank from the in-memory copy instead of re-reading the PROG file. | `ND-60.066.04` lines 1013-1015 and Appendix A line 1639 |

> **Note from the Loader manual:** "One-bank and two-bank programs may not be
> mixed. The `BPUN` command does not apply to two-bank systems." (line 1007)

### 3.3 Optional fields produced by NLL in COMPUTER-MODE 100

When the file is produced by NLL with `COMPUTER-MODE 100`, the `:PROG` file may
additionally contain **debug information** (sufficient for the ND-500 Symbolic
Debugger's source-level facilities), in the same on-disk format as the
`:PROG` produced by NRL but with the debug section appended on the `:PSEG`
file. Sources do not document the layout of this debug section in field form.

> Source: `ND-60.136.04A` line 3140. Layout details **UNVERIFIED**.

### 3.4 Reentrant program variant (`@DUMP-PROGRAM-REENTRANT`)

`@DUMP-PROGRAM-REENTRANT <program_name>` writes a reentrant program image to
a `:PROG` file usable for rebuilding reentrant subsystems after a cold restart
(typically driven from the `HENT-MODE` mode file together with `DUMP-REENTRANT`
and `DUMP-PROGRAM-REENTRANT` commands).

| Aspect | Value |
|---|---|
| Permitted for | User SYSTEM only |
| File type | `:PROG` |
| Header fields | Same as section 3.1 |
| Additional payload | Reentrant subsystem image (image-area + run segments). The image is consumed by `@RECOVER` style restoration during cold-start sequencing. |

> Source: `Reference-Manuals/SINTRAN-COMMANDS-REFERENCE.md` lines 1354 and
> 2538-2563.

---

## 4. How a :PROG File Is Consumed (`@RECOVER`)

`@RECOVER <file>` performs the following sequence (paraphrased from
`SINTRAN/OS/SEGMENTS-INTRO-AND-DEEP-DIVE.md` lines 1389-1392 and
`ND-60.066.04` section 1.4.2):

1. The PROG file's logical header is read; SINTRAN extracts the lower/upper
   bounds, start address and restart address.
2. A background segment is allocated (or reused) for the calling RT
   description.
3. The pages spanning `[lower .. upper]` of the segment are mapped into the
   user's PIT (Page Index Table).
4. The memory image portion of the file is read directly into the mapped
   pages (the code bank).
5. **Two-bank only:** the data-bank image is read either from the same PROG
   file, or from the file recorded inside the PROG header (see 3.2), into
   the alternate page table. If `*DATA-BANK-COPY` was used at dump time,
   `@RECOVER` instead initialises the data bank by copying from the
   duplicated area above the code in the PROG segment.
6. The program counter is set to the **start address** and execution begins.
7. A subsequent `@CONTINUE` will (re)start execution at the **restart
   address** instead.

`@CONTINUE` and `@ABORT` operate on the same in-memory image; the PROG file
itself is not modified by execution.

---

## 5. Format Variants Summary

| Variant | Producer | Banks | Extra fields | Consumer |
|---|---|---|---|---|
| **Standard one-bank** | NRL `*DUMP` / `*PROG-FILE`, SINTRAN `@DUMP` | 1 x 64KW | none | `@RECOVER` |
| **Two-bank (split code/data)** | NRL two-bank mode + `*PROG-FILE` or `*DUMP` | 2 x 64KW | data-bank file name, alternate-bank image | `@RECOVER` (with two-bank support) |
| **Two-bank with `DATA-BANK-COPY`** | NRL two-bank mode + `*DATA-BANK-COPY` then `*DUMP` | 2 x 64KW logically, single image physically | data area duplicated above code | `@RECOVER` (initialises data bank from in-segment copy) |
| **Image-file derived** | `*IMAGE-FILE` then `*DUMP` | 1 or 2 | identical to the corresponding above variant | `@RECOVER` |
| **Reentrant program** | `@DUMP-PROGRAM-REENTRANT` | 1 | reentrant subsystem image payload | Cold-start restore via `HENT-MODE`, then `@RECOVER` for use |
| **NLL ND-100 mode** | NLL `COMPUTER-MODE 100` | 1 | optional ND-100 source-level debug section | NLL `$RECOVER` |
| **Hand-modified monitor** | Operator changes default, `EXIT`s monitor, `@DUMP` | 1 | none | `@RECOVER` |

---

## 6. Relationship to `:BPUN` (for contrast)

`:BPUN` is the related but distinct *absolute binary* format produced by
`*BPUN` (NRL) and `)BPUN` (MAC). It is **not** the same as `:PROG`:

- A `:BPUN` file carries a **44 (octal) word bootstrap loader** prefixed to
  the program image, so it can be loaded by the ND-100 hardware loader on a
  stand-alone machine, by the operating system, or by MAC's `)9READ`.
- It carries an explicit **start address** (the program's main entry, in
  symbolic or octal form) and a **bootstrap address** (where the 44-word
  bootstrap will reside when loaded into a stand-alone NORD-10/ND-100).
- A **checksum** is generated by `)BPUN` and verified by the loader.
- It is loaded into a SINTRAN address space with `@PLACE-BINARY`, not
  `@RECOVER`.
- `:BPUN` does **not** apply to two-bank systems.

> Source: `ND-60.066.04` lines 515-519 and Appendix A line 1637;
> `ND-60.096.01 MAC ... User's Guide.md` lines 2212-2216.

---

## 7. Known Gaps in the Public Documentation

**Gaps 1 and 2 below are answered in the companion document
[prog-fileformat.md](prog-fileformat.md)**, from the NPL source of `@RECOVER`
(`RP-P2-MONCALLS.NPL`, which reads exactly 7 words from block 0) and four real `:PROG`
files: the header is 7 big-endian 16-bit words at file offset 0 - start, restart, bank 1
first/last, bank 2 first/last, data-bank-copy last - and there is no magic number or version
word. The list is kept as written because it is still true of the MANUALS; gaps 3, 4 and 5
are still open, and the companion's own section 6 lists what it could not settle.

The following details are **not** published in the manuals in the repository
and would require disassembly of NRL or of the SINTRAN `@RECOVER` /
`@DUMP` command processors to verify:

1. The exact byte/word offsets of the start, restart, lower-bound and
   upper-bound fields in the file header.
2. Whether the header carries any magic number or version word (the manuals
   never refer to one).
3. The on-disk encoding of the data-bank file name field used by two-bank
   PROG files (presumed packed in standard SINTRAN file-name form, but
   **UNVERIFIED**).
4. The exact layout of the optional debug section appended by NLL in
   `COMPUTER-MODE 100`.
5. Whether reentrant-program PROG files have additional descriptor words
   compared to ordinary one-bank PROG files.

If a definitive layout is required, the candidate sources to inspect inside
this repository are:

- `SINTRAN/NPL-SOURCE/NPL/RP-P2-MONCALLS.NPL` (RECOVER monitor call paths)
- `SINTRAN/NPL-SOURCE/NPL/PH-P2-OPPSTART.NPL` (cold-start, image loading)
- `SINTRAN/NPL-SOURCE/NPL/5P-P2-MON60.NPL` (MON 60 image handling)

These are listed in the file index `SINTRAN/NPL-SOURCE/README.md`.

---

## 8. Quick Reference Card

```
Produce
-------
NRL  *DUMP <file>[ <start> <restart>]            -> :PROG  (one or two bank)
NRL  *PROG-FILE <file> ; *LOAD ... ; *EXIT        -> :PROG  (direct, must be first cmd)
NRL  *IMAGE-FILE <file> ; ... ; *DUMP <prog>      -> :PROG  (large programs)
NRL  *DATA-BANK-COPY (two-bank, before *DUMP)     -> :PROG  (data area duplicated above code)
SIN  @DUMP <file>,<start>,<restart>               -> :PROG  (from current address space)
SIN  @DUMP-PROGRAM-REENTRANT <name>               -> :PROG  (reentrant variant, SYSTEM only)
NLL  COMPUTER-MODE 100 ; ... ; (writes :PSEG)     -> :PROG-format on :PSEG

Consume
-------
SIN  @RECOVER <file>          ! load and start at start address
SIN  @CONTINUE                ! resume at restart address
NLL  $RECOVER <file>          ! ND-100 mode, NLL-built PROG file

Boundaries / addresses
----------------------
NRL  *BOUNDARIES <lower> <upper>          ! override default dump extent
NRL  *SET-LOAD-ADDRESS <addr>             ! where subsequent code is placed
NRL  *SET-DATA-LOAD-ADDRESS <addr>        ! one-bank build of two-bank prog
NRL  *SET-MODE PROG | DATA                ! select bank for subsequent commands
SIN  @MEMORY <lower> <upper>              ! defines @DUMP extent
```

---

**Last updated:** 2026-04-09
**Status:** Phase 1 - operational reference complete. The byte-level header layout
is NOT in this document; it was established from the NPL source and real files in
[prog-fileformat.md](prog-fileformat.md). (Status line corrected 2026-09-18; the body above
is unchanged since 2026-04-09.)
