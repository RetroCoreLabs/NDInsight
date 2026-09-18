# Reverse Engineering ND-100 Programs

Taking a built SINTRAN program apart — decoding `:PROG`/`:BRF` binaries back
to instructions and reconstructing intent — when you have the binary but not
the source. The inverse of the [MAC](../Languages/System/MAC-DEVELOPER-GUIDE.md)
assembly workflow.

---

## Documents

### [Disassembling-a-PROG.md](Disassembling-a-PROG.md)
**The practical RE workflow**

Get the memory image, find entry points, separate code from data (reachability
trace + ASCII heuristic), decode, resolve P-relative labels, annotate MON
calls, and reconstruct intent from MON-call sites + literal pool + param lists.

### [ND-100-Instruction-Decoding.md](ND-100-Instruction-Decoding.md)
**The decode reference: 16-bit word → mnemonic**

Opcode families (memory-reference, conditional jumps, argument, register-ops,
shift, bit, privileged), the 8 addressing modes, source/destination register
maps, and MON/IOX detection. Derived from a disassembler verified against real
`:PROG` files; confidence-tagged **[V]**/**[B]**. Complements
[ND-60.096 §2.3](<../../Reference-Manuals/ND-60.096.01 MAC Interactive Assembly and Debugging System User's Guide.md>)
(authoritative repertoire).

---

## Related

- **[:PROG File Format Reference](../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)** — the binary container (header + memory image).
- **[MAC Cookbook](../Languages/System/MAC-COOKBOOK.md)** — the assembly side (addressing, MON ABI, literal pool).
- **[ND MON Calls](../MON/ND MON Calls.md)** — monitor-call numbers to annotate `MON n` sites.

---

*Verified against real SINTRAN `:PROG` files under nd100x.*
