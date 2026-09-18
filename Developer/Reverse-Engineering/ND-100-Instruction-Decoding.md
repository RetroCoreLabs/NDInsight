# ND-100 Instruction Decoding (Disassembly Reference)

**How to decode a 16-bit ND-100 / ND-110 instruction word back to a
mnemonic — the inverse of MAC assembly.**

This is the decode table behind a working disassembler we built and ran
against real SINTRAN `:PROG` files (an HTTP server, ping, XMSG test). The
authoritative instruction repertoire is
**[ND-60.096 §2.3](<../../Reference-Manuals/ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide.md>)
(NORD-10 Instruction Repertoire)** — the ND-100 is binary-compatible with
NORD-10/S at the user-mode ISA level SINTRAN programs use; see also
**[ND-60.113 Assembler Reference Manual](<../../Reference-Manuals/ND-60.113.02 EN Assembler Reference Manual.md>)**.
For the *file container* (header, memory image), see the repo's
**[:PROG File Format Reference](../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)**.

> **Confidence tags:** **[V]** verified by disassembling real `:PROG` files
> and matching the source; **[B]** best-effort (the manual's tables for this
> family are inconsistent — cross-check against ND-60.096 before relying on
> it). Numbers are **octal** (MAC convention) unless prefixed `0x`.

---

## Words and addresses

- An instruction is **one 16-bit word**, stored **big-endian** in the file.
- In a `:PROG`, the 256-byte header is followed by the memory image; **memory
  address 0 = file offset `0x100`**. Word at address *a* is at byte
  `0x100 + a*2`. (Header fields: see the file-format reference.)
- Memory-reference and jump displacements are **signed 8-bit** (−128..+127),
  added to the current address (P-relative). Argument immediates are signed
  8-bit. Shift counts are signed 7-bit.

---

## Decode order (disambiguation)

Families overlap in the opcode space, so decode in this order (this is the
order the disassembler uses, and it resolves the overlaps):

1. `0` → data word `ZERO`.
2. **MON**: `(w & 0xFF00) == 0xD600` → `MON n`, `n = w & 0xFF`. **[V]**
3. **IOX**: `(w & 0o174000) == 0o164000` → `IOX <w & 0o3777>`. **[V]**
4. **Byte ops**: `SBYT = 0o142600`, `LBYT = 0o142200`. **[V]**
5. **Conditional jumps**: `(w & 0o174000) == 0o130000` (see table). **[V]**
6. **Memory-reference** (incl. `JMP`/`JPL`): top 5 bits in the MEM table. **[V]**
7. **Argument instructions**: `(w & 0o177400)` in the ARG table. **[V]**
8. **Shift**: `(w & 0o174000) == 0o154000`. **[B]**
9. **Privileged / system** (IOF/ION/WAIT/TRA/…). **[B]**
10. **Bit instructions**: `(w & 0o174000) == 0o174000`. **[B]**
11. **Skip** (`SKP`) then **register-ops**: `(w & 0o170000) == 0o140000`. **[B]**
12. Else `.WORD <w>` (data).

---

## Memory-reference instructions  **[V]**

Format: `op(bits 15-11) | mode(bits 10-8) | disp(bits 7-0, signed)`.

| Opcode (octal) | Mnem | | Opcode | Mnem | | Opcode | Mnem |
|---|---|---|---|---|---|---|---|
| `004000` | STA | | `044000` | LDA | | `064000` | SUB |
| `000000` | STZ | | `050000` | LDT | | `070000` | AND |
| `010000` | STT | | `054000` | LDX | | `074000` | ORA |
| `014000` | STX | | `060000` | ADD | | `120000` | MPY |
| `020000` | STD | | `024000` | LDD | | `124000` | JMP |
| `030000` | STF | | `034000` | LDF | | `134000` | JPL |
| `040000` | MIN | | | | | | |
| `100000` | FAD | | `104000` | FSB | | `110000` | FMU |
| `114000` | FDV | | | | | | |

### Addressing modes (bits 10-8 = `w & 0o3400`)  **[V]**

| `w & 0o3400` | Syntax | Effective address |
|---|---|---|
| `0o0000` | `<disp>` (P-rel) | `PC + disp` |
| `0o0400` | `<disp>,B` | `B + disp` |
| `0o1000` | `I <disp>` | `*(PC + disp)` (indirect P-rel) |
| `0o1400` | `I <disp>,B` | `*(B + disp)` |
| `0o2000` | `<disp>,X` | `X + disp` |
| `0o2400` | `<disp>,B,X` | `B + X + disp` |
| `0o3000` | `I <disp>,X` | `*(PC + disp) + X` |
| `0o3400` | `I <disp>,B,X` | `*(B + disp) + X` |

Only P-rel and indirect-P-rel resolve to a static target when disassembling;
B/X modes depend on runtime register values. (This is exactly the
"deref ladder" from the [MAC Cookbook](../Languages/System/MAC-COOKBOOK.md#5-addressing--the-deref-ladder),
seen from the decode side.)

## Conditional jumps  **[V]**

Base `0o130000`, condition in bits 10-8, signed-8 displacement (P-rel).

| Code | Mnem | meaning |
|---|---|---|
| `130000` | JAP | jump if A ≥ 0 |
| `130400` | JAN | jump if A < 0 |
| `131000` | JAZ | jump if A = 0 |
| `131400` | JAF | jump if A ≠ 0 |
| `132000` | JPC | jump if X-count positive (and increment) |
| `132400` | JNC | jump if X-count negative (and increment) |
| `133000` | JXZ | jump if X = 0 |
| `133400` | JXN | jump if X < 0 |

## Argument instructions  **[V]**

Base in bits 15-8, signed-8 immediate in bits 7-0.

| Code | Mnem | | Code | Mnem |
|---|---|---|---|---|
| `170000` | SAB | | `172000` | AAB |
| `170400` | SAA | | `172400` | AAA |
| `171000` | SAT | | `173000` | AAT |
| `171400` | SAX | | `173400` | AAX |

`SAx` = set register to immediate; `AAx` = add immediate to register
(B/A/T/X). Immediate range ±127 — the cookbook's "immediates are small and
signed" rule, confirmed from the encoding.

## MON and IOX  **[V]**

- **`MON n`**: `0xD600 | n` (i.e. `0o153000 + n`); `n` is the octal monitor
  number. Full name table in the disassembler and in
  [ND MON Calls](../MON/ND MON Calls.md) — e.g. `0o0` ExitFromProgram,
  `0o2` OutByte, `0o35` OutNumber, `0o43` CloseFile, `0o50` OpenFile,
  `0o117` ReadFromFile, `0o122` ReserveResource, `0o201` HDLCfunction.
- **`IOX <dev>`**: `(w & 0o174000) == 0o164000`, device/function in
  `w & 0o3777`. (Raw I/O — e.g. direct HDLC register pokes.)

## Register operations  **[B]**

`(w & 0o170000) == 0o140000`. Format `1100 | QC | IC | R | source(5-3) | dest(2-0)`
with AD1/ADC/CLD/CM1/CM2 modifier bits. Source/destination register maps:

| `src (bits 5-3)` | name | | `dst (bits 2-0)` | name |
|---|---|---|---|---|
| `0o00` | 0 | | `0o0` | STS |
| `0o10` | SD | | `0o1` | DD |
| `0o20` | SP | | `0o2` | DP |
| `0o30` | SB | | `0o3` | DB |
| `0o40` | SL | | `0o4` | DL |
| `0o50` | SA | | `0o5` | DA |
| `0o60` | ST | | `0o6` | DT |
| `0o70` | SX | | `0o7` | DX |

Base ops by `w & 0o7700`: `RADD 0o6000`, `COPY 0o6100`, `RSUB 0o6600`,
`SWAP 0o4000`, `RAND 0o4400`, `REXO 0o5000`, `RORA 0o5400`. Common combined
forms: `EXIT = 0o146142` (COPY SL DP), `RCLR = 0o146100`, `RINC = 0o146400`,
`RDCR = 0o146200`. Modifier-bit decoding is the inconsistent part — verify
against ND-60.096 §2.3.5 before trusting a modified form.

## Other families (summarised)  **[B]**

- **Skip** `SKP <cond> <sr> <dr>`: `0o140000` with cond in bits 10-8
  (`EQL/GRE/MGRE/UEQ/LST/MLST`) and the RAD/QC/IC fields zero.
- **Shift** `0o154000` family: target `SHT/SHD/SHA/SAD` (bits 8-7), mode
  `ARITH/ROT/ZIN/LIN` (bits 10-9), signed-7 count (negative = right).
- **Bit** `0o174000` family: `BSET/BSKP/BSTC/BSTA/BLDA/BANC/BAND/BORC/BORA`
  with condition `ZRO/ONE/BCM/BAC`. *(Manual tables inconsistent — [B].)*
- **Privileged/system**: `IOF 0o150401`, `ION 0o150402`, `POF 0o150404`,
  `PON 0o150410`, `WAIT 0o151000+n`, `IDENT 0o143600`, and register-coded
  `TRA/TRR/MCL/MST 0o1501xx/0o1502xx/0o1503xx`, `IRR 0o153400+`, `IRW
  0o153600+`. Many are RT/privileged and won't appear in user-mode programs.

---

## Worth knowing when reading disassembly

- **Literal pool**: blocks of `.WORD` after a routine are usually the literal
  pool (addresses for `(LABEL` operands) — not code. A run of high-entropy
  words right after a `)FILL`-terminated routine is the giveaway.
- **MON-call skip slots**: after a `MON n` the next word is the error path and
  the one after is the success path (skip-on-success) — so a `JMP`
  immediately after a `MON` is normal control flow, not dead code.
- **Text/data vs code**: a window where most bytes are printable ASCII is a
  string/data region; don't disassemble it. (The disassembler's reachability
  trace and an ">85% printable" heuristic separate the two.)

---

## See Also

- **[Disassembling a :PROG](Disassembling-a-PROG.md)** — the practical RE workflow that uses this table.
- **[:PROG File Format Reference](../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)** — the container around the memory image.
- **[ND-60.096 §2.3](<../../Reference-Manuals/ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide.md>)** — authoritative NORD-10 instruction repertoire.
- **[MAC Cookbook](../Languages/System/MAC-COOKBOOK.md)** — the assembly side (addressing deref ladder, MON ABI).

---

*Decode tables come from a disassembler verified against real SINTRAN
`:PROG` files; [B]-tagged families need a cross-check against ND-60.096 §2.3.*
