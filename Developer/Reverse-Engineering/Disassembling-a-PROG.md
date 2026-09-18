# Disassembling and Reverse-Engineering a SINTRAN `:PROG`

**A practical workflow for taking a built `:PROG` (or `:BRF`) apart and
understanding it — when you have the binary but not the source.**

This is the approach we used to verify our own programs and to understand
others. It pairs with two references: the
**[ND-100 Instruction Decoding](ND-100-Instruction-Decoding.md)** table
(word → mnemonic) and the
**[:PROG File Format Reference](../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)**
(the container). Where the decode table is the *what*, this is the *how*.

> Verified against real SINTRAN `:PROG` files (HTTP server, ping, XMSG
> test) under nd100x / SINTRAN III VSX/500 L.

---

## 1. Get the bytes and find the memory image

A `:PROG` is a 256-byte header followed by the program's memory image as
big-endian 16-bit words: **memory address 0 lives at file offset `0x100`**.
So the first thing to read is the header (end address, entry/marker fields —
see the format reference), then treat everything from `0x100` on as words at
ascending addresses.

For a `:BRF` (relocatable object, pre-link) the layout differs — it carries
relocation/definition records. The most useful thing a `:BRF` gives you for
RE is the **set of relocated slots**: those are pointer cells whose values
are addresses, which seed control-flow discovery (below).

## 2. Find the entry point(s)

- The header's entry/start field is the primary entry.
- In MAC source the entry is declared with `)9BEG <label>`; in the binary
  it's just the address execution begins at.
- Additional entry points show up as the **targets of relocated pointer
  slots** (from the `:BRF`) and as jump/call targets you discover while
  tracing.

## 3. Separate code from data (don't disassemble strings)

Blindly disassembling every word produces garbage over data regions. Two
reliable separators:

- **Reachability trace.** Start from the entry point(s), follow straight-line
  flow, jumps, and conditional branches, and mark every reachable word as
  code. Everything unreached is data (or unreachable code). This alone
  cleans up most output.
- **Printable-ASCII heuristic.** A window where >~85% of bytes are printable
  (or CR/LF/TAB/NUL) is almost certainly a string/message region — skip it.

Our disassembler does both: a forward trace from the entries (seeded with
`:BRF` relocation targets when available) plus the ASCII heuristic, then only
disassembles the reachable, non-text words.

## 4. Decode the words

Apply the [instruction decoding table](ND-100-Instruction-Decoding.md) in its
disambiguation order. Things that make the output readable:

- **Resolve P-relative targets** to labels: a memory-ref/jump in P-rel or
  indirect-P-rel mode points to `PC + signed8(disp)`; name those addresses
  `Lnnnnnn` and back-substitute so jumps read as `JMP LOOP` not `JMP 0o…`.
- **Annotate `MON n`** with the monitor name (see
  [ND MON Calls](../MON/ND MON Calls.md)) — `MON 0o50 (OpenFile)` tells you
  far more than the number.
- **Recognise the patterns** from the cookbook: a `MON` followed by a `JMP`
  is the skip-on-success error path, not a bug; a block of `.WORD` after a
  `)FILL`-terminated routine is the **literal pool** (addresses for `(LABEL`
  operands), not code.

## 5. Reconstruct intent

With code separated and decoded, the structure usually falls out:

- **MON-call sites** tell you what the program *does* (file I/O via
  50/117/43, device I/O via 122/201, output via 2/35/162, exit via 0).
- **The literal pool + addressing modes** reveal the data the routine touches
  (each `(LABEL` is a pool entry pointing at a variable/buffer/param-list).
- **Param lists** for monitor calls are contiguous data words holding
  addresses — find the `LDA (PARM; MON n` and read `PARM`'s words as the
  call's arguments (each a by-reference address). This is how you recover,
  e.g., an `OpenFile` filename/type or a `ReadFromFile` block/count.

## 6. Improve the disassembler as you go

Reverse-engineering and tooling co-evolve: every time a real program reveals
a mnemonic, addressing form, or MON number the decoder got wrong, fold the
correction back into the decode table. The well-verified families
(memory-reference, jumps, arguments, MON, IOX, addressing modes) got that way
by being checked against real `:PROG` output; the **[B]**-tagged families in
the decode reference are the ones still worth hardening against ND-60.096
§2.3 the next time you meet them in the wild.

---

## Tooling

This workflow is implemented as a Python disassembler shipped in this repo:
**[`scripts/nd100_disasm.py`](../../scripts/nd100_disasm.py)** (with
**[`scripts/nd100_brf.py`](../../scripts/nd100_brf.py)** for the optional
`--brf` relocation seeding). It parses the `:PROG` header, runs the
reachability trace, applies the decode table, resolves P-relative labels, and
annotates MON calls. The decode logic in
[ND-100 Instruction Decoding](ND-100-Instruction-Decoding.md) is exactly that
tool's table — keep them in sync.

```bash
# Inspect the header
python scripts/nd100_disasm.py MYPROG.PROG --header

# Disassemble, following control flow from the entry point (cleaner output)
python scripts/nd100_disasm.py MYPROG.PROG --trace 0

# Seed the trace from a matching :BRF's relocations (finds more code)
python scripts/nd100_disasm.py MYPROG.PROG --brf MYPROG.BRF

# Annotate addresses with your own symbol file (addr name per line)
python scripts/nd100_disasm.py MYPROG.PROG --sym MYPROG.sym
```

Stdlib-only (Python 3.10+); `--brf` is the sole inter-module dependency.

---

## See Also

- **[ND-100 Instruction Decoding](ND-100-Instruction-Decoding.md)** — the word → mnemonic table.
- **[:PROG File Format Reference](../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)** — header + memory image container.
- **[MAC Cookbook](../Languages/System/MAC-COOKBOOK.md)** — the assembly side; addressing deref ladder, MON ABI, literal pool.
- **[ND-60.096 §2.3](<../../Reference-Manuals/ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide.md>)** — authoritative instruction repertoire.

---

*Workflow verified reverse-engineering real SINTRAN `:PROG` files; the decode
table it relies on was hardened against that same set of programs.*
