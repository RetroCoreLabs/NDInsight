"""ND BRF (Binary Relocatable Format) parser.

Reads :BRF files emitted by MAC / FORTRAN / PLANC / etc., and produces:
  - A relocation map: {memory_addr: "LF" | "LR" | "AFF" | "ARF" | "AFR" | "ARR"}
  - The symbol table (MAIN, ENTR, LIBR, REF — start address, named entries, refs)
  - The list of program units (each BEG...END pair, with its program base)
  - Real-time priority and other metadata

This unlocks BRF-aware disassembly: words tagged as `LR` are POINTERS that
the loader patches with the program base at load time. They look like data
in the PROG but are actually function/jump-table entries.

Reference: ND-60.066.04 ND Relocating Loader §2.1–2.9.

BRF byte stream syntax (sequence of "groups"):

  <control_byte>                       — 0 args (FEED, BEG, INHB, EOF)
  <control_byte><P-group>              — 1 P-group (LF, LR, LC, SFL, AFL, SRL, END, LNF, RT)
  <control_byte><P-group><P-group>     — 2 P-groups (AFF, ARF, AFR, ARR)
  <control_byte><S-group>              — 1 S-group (4 or 6 bytes)
  <control_byte><S-group><P-group>     — S+P (MAIN, LIBR, ENTR, REF, ASF, ADS)

A P-group is one 16-bit word, big-endian, 2 bytes.
An S-group is a packed symbol — 4 bytes default, 6 bytes if LONGF flag set.

Usage:
  python nd100_brf.py PROG.bin --brf PROG.brf       # cross-reference
  python nd100_brf.py PROG.brf                       # parse only
  python nd100_brf.py LIB.brf --names                # every name the file DEFINES, sorted
  python nd100_brf.py LIB.brf --names --refs         # every name it only REFERS to
  python nd100_brf.py LIB.brf --find INBT            # which unit defines / refers to INBT
  python nd100_brf.py LIB.brf --json                 # units and symbols as JSON

Output: prints the relocation map and symbol table to stdout.

Every unit's checksum is verified (ND-60.066.04 section 2.7: sum of control bytes, P-groups
and S-group words from BEG up to and including END, stored word = two's complement). A unit
whose checksum fails is reported; that is the sign of a damaged file or a group this parser
reads wrongly. Checked against the BRF linker's own LIST-BRF-ENTRIES on FORT48-2BANK-F02:BRF
(415 units, 462 names, all identical). Symbol names use the six-bit code described at
decode_symbol_packed(). LONGF (6-byte S-groups) is per unit and is reset at every BEG.
"""
from __future__ import annotations
import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path


# --- Control-byte constants (octal, per ND-60.066.04 §2.9) ---
CB_FEED = 0o0    # skip / padding
CB_LF   = 0o1    # load value (1 word, no reloc)
CB_LR   = 0o2    # load relocated (W + PB) — addresses
CB_LC   = 0o3    # load common-relative (W + CDB)
CB_AFF  = 0o4    # fix-up: W1 + (W2) -> (W2)
CB_ARF  = 0o5    # fix-up: W1 + PB + (W2) -> (W2)
CB_AFR  = 0o6    # fix-up: W1 + (W2+PB) -> (W2+PB)
CB_ARR  = 0o7    # fix-up: W1 + PB + (W2+PB) -> (W2+PB)
CB_SFL  = 0o10   # set CLC := W1
CB_AFL  = 0o11   # CLC += W1, fill zeros
CB_SRL  = 0o12   # CLC := W1 + PB
# 0o13 not used
CB_MAIN = 0o14   # S-group + P: main entry
CB_LIBR = 0o15   # S-group + P: library subprogram
CB_ENTR = 0o16   # S-group + P: entry point
CB_BEG  = 0o17   # start of program unit, CLC -> PB
CB_REF  = 0o20   # S-group + P: external reference
CB_END  = 0o21   # end of unit + checksum
CB_INHB = 0o22   # compilation errors flag (no args)
CB_EOF  = 0o23   # end of loading (no args)
CB_LNF  = 0o24   # 1+W1: load W1 words
CB_RT   = 0o25   # RT priority (1 word)
CB_ASF  = 0o26   # COMMON block (S+P)
CB_ADS  = 0o27   # add common (S only)
CB_LONGF = 0o32  # set 6-byte S-group mode for the rest of the unit
CB_DBG  = 0o47   # debug mode on/off (no args)
CB_DIC  = 0o54   # dictionary table follows, ends with a 177777 word (made by MAKE-LIBRARY-FILE)

# Groups with a fixed shape that this tool reads past but does not interpret:
# control number -> (has S-group, number of P-groups).  INL DBL RLL CXL / INC DBC RLC CXC / BYL BYC / NWL
EXTRA_GROUPS = {
    0o34: (False, 2), 0o35: (False, 3), 0o36: (False, 4), 0o37: (False, 7),
    0o40: (True, 2), 0o41: (True, 3), 0o42: (True, 4), 0o43: (True, 7),
    0o44: (False, 2), 0o45: (True, 3), 0o46: (False, 1),
}

# --- CC-100 (ND-100 C compiler) BRF extensions ---
# Reverse-engineered 2026-05-25 from CAT.C → CAT.BRF correlation, then extended
# by inspecting the C runtime libraries (CC-{1,2}BANK/HEADER/TRAILER-A.BRF).
# Standard BRF only defines control bytes 0o0-0o27 + 0o32. CC-100 adds:
CB_CC_STRSEG_BEG = 0o51   # marker: begin string-data segment (no args)
CB_CC_STRSEG_END = 0o50   # marker: end string-data segment (no args)
CB_CC_REFFIX_A   = 0o52   # REF fix-up sub-marker, 1 P-group arg
CB_CC_REFFIX_B   = 0o53   # REF fix-up sub-marker (different flavor), 1 P-group arg
# C runtime BRFs (CC-{1,2}{HEADER,TRAILER,BANK}-A.BRF) use additional bytes:
CB_CC_RT54       = 0o54   # observed in CC-{1,2}HEADER preamble; 1 P-group?
CB_CC_RT60       = 0o60   # also HEADER preamble
# Plus various high-byte ones (0o113-0o324 range) that appear preceding REF
# symbols within the runtime. Likely fix-up records with multi-byte arg
# encoding we haven't fully decoded; the parser falls through to "skip
# unknown" for these and the parse still produces useful output.

CONTROL_NAMES = {
    CB_FEED: "FEED", CB_LF: "LF", CB_LR: "LR", CB_LC: "LC",
    CB_AFF: "AFF", CB_ARF: "ARF", CB_AFR: "AFR", CB_ARR: "ARR",
    CB_SFL: "SFL", CB_AFL: "AFL", CB_SRL: "SRL",
    CB_MAIN: "MAIN", CB_LIBR: "LIBR", CB_ENTR: "ENTR",
    CB_BEG: "BEG", CB_REF: "REF", CB_END: "END",
    CB_INHB: "INHB", CB_EOF: "EOF", CB_LNF: "LNF",
    CB_RT: "RT", CB_ASF: "ASF", CB_ADS: "ADS",
    CB_LONGF: "LONGF",
    CB_CC_STRSEG_BEG: "CC.STRBEG", CB_CC_STRSEG_END: "CC.STREND",
    CB_CC_REFFIX_A:   "CC.REFA",   CB_CC_REFFIX_B:   "CC.REFB",
}


# --- Symbol decoding (six-bit characters, ND-60.066.04 section 2) ---
# An S-group is 4 bytes (32 bits) or, after LONGF, 6 bytes (48 bits). The bits are packed
# six to a character, MOST significant first, right-justified. The six-bit code is the LOW SIX
# BITS OF ASCII: 1-32 octal = A-Z, 33-37 = [ \ ] ^ _, 40-77 = space ! " # $ ... 0-9 ... ?.
# So a letter is code + 0100, anything from 040 up is the ASCII value itself, and 0 is a space
# (padding). Checked against the BRF linker's own LIST-BRF-ENTRIES on FORT48-2BANK-F02:BRF:
# 462 of 462 names identical.
def decode_symbol_packed(buf: bytes) -> str:
    """Decode an S-group into its symbol name (trailing and leading spaces removed)."""
    v = int.from_bytes(buf, "big")
    n = (len(buf) * 8) // 6
    chars = []
    for i in range(n - 1, -1, -1):
        c = (v >> (6 * i)) & 0x3F
        if c == 0:
            chars.append(" ")
        elif c < 0x20:
            chars.append(chr(c + 0x40))
        else:
            chars.append(chr(c))
    return "".join(chars).strip()


# --- Data classes ---

@dataclass
class Reloc:
    """One memory-location reloc/load entry."""
    addr: int           # memory address (in words) where loaded
    kind: str           # "LF", "LR", "LC", "ARF", etc.
    value: int          # raw P-group word value (pre-relocation)
    unit: int = 0       # which program unit it's in


@dataclass
class Symbol:
    name: str
    kind: str           # MAIN | ENTR | LIBR | REF
    addr: int           # address of the entry (or referencing location for REF)


@dataclass
class ProgramUnit:
    base: int                       # PB at BEG time
    end: int                        # CLC at END time
    checksum: int = 0
    checksum_ok: bool | None = None  # None until the unit's END group has been read
    offset: int = 0                  # byte offset of the unit's BEG in the file
    symbols: list[Symbol] = field(default_factory=list)
    rt_priority: int | None = None
    longf: bool = False
    comment: str = ""                # identification text of a control-30 group, if any


# --- Strip parity helper (some BRF streams have even-parity bit 7 set) ---

def maybe_strip_parity(data: bytes) -> bytes:
    """If majority of bytes have bit 7 set, strip it."""
    high = sum(1 for b in data if b & 0x80)
    if high > len(data) * 0.4:   # >40% high-bit set → likely parity
        return bytes(b & 0x7F for b in data)
    return data


# --- Parser ---

class BRFParser:
    def __init__(self, data: bytes, base_address: int = 0):
        self.data = data
        self.pos = 0
        self.clc = base_address      # current location counter (= load address)
        self.pb = 0                  # program base
        self.unit_idx = 0
        self.units: list[ProgramUnit] = []
        self.relocs: list[Reloc] = []
        self.longf: bool = False     # 6-byte S-groups when set (reset at every BEG)
        self.csum: int = 0           # running unit checksum: control bytes + P-groups + S-group words
        self.problems: list[str] = []

    def _read_byte(self) -> int | None:
        if self.pos >= len(self.data):
            return None
        b = self.data[self.pos]
        self.pos += 1
        return b

    def _read_word(self) -> int:
        hi = self._read_byte() or 0
        lo = self._read_byte() or 0
        w = (hi << 8) | lo
        self.csum += w
        return w

    def _read_sgroup(self) -> bytes:
        n = 6 if self.longf else 4
        out = self.data[self.pos:self.pos + n]
        self.pos += n
        for k in range(0, len(out) - 1, 2):
            self.csum += (out[k] << 8) | out[k + 1]
        return out

    def parse(self) -> list[ProgramUnit]:
        cur_unit: ProgramUnit | None = None
        while self.pos < len(self.data):
            cb = self._read_byte()
            if cb is None:
                break

            if cb == CB_FEED:
                continue

            if cb == CB_BEG:
                # Start a new unit. LONGF applies to ONE unit only: every BEG goes back to
                # 4-byte S-groups (BRF-FILE-FORMAT.md section 2; a file can mix both forms).
                cur_unit = ProgramUnit(base=self.clc, end=self.clc, offset=self.pos - 1)
                self.pb = self.clc
                self.units.append(cur_unit)
                self.unit_idx += 1
                self.longf = False
                self.csum = CB_BEG
                continue

            if cur_unit is not None:
                self.csum += cb        # the control byte itself is part of the checksum

            if cb == CB_END:
                if cur_unit is not None:
                    cur_unit.end = self.clc - 1
                    # the stored word is NOT part of the sum; sum + stored = 0 (mod 65536)
                    stored = ((self.data[self.pos] << 8) | self.data[self.pos + 1]
                              if self.pos + 1 < len(self.data) else 0)
                    self.pos += 2
                    cur_unit.checksum = stored
                    cur_unit.checksum_ok = ((self.csum + stored) & 0xFFFF) == 0
                    cur_unit = None
                continue

            if cb == CB_LONGF:
                self.longf = True
                if cur_unit:
                    cur_unit.longf = True
                continue

            # Groups the manual lists (ND-60.066.04 2.9) that carry data but no code address,
            # plus the control-30 identification text seen in PLANC and FORTRAN output.
            if cb == 0o30:                       # count word, then count words of ASCII text
                cnt = self._read_word()
                text = bytearray()
                for _ in range(cnt):
                    w = self._read_word()
                    text += bytes((w >> 8, w & 0xFF))
                if cur_unit:
                    cur_unit.comment = text.decode("latin-1").strip()
                continue
            if cb in EXTRA_GROUPS:               # INL DBL RLL CXL INC DBC RLC CXC BYL BYC NWL
                has_s, nwords = EXTRA_GROUPS[cb]
                if has_s:
                    self._read_sgroup()
                for _ in range(nwords):
                    self._read_word()
                continue
            if cb == CB_DBG:
                continue
            if cb == CB_DIC:                     # dictionary: 5-word elements, ends with 177777
                while self.pos + 1 < len(self.data):
                    if self._read_word() == 0xFFFF:
                        break
                continue

            if cb == CB_INHB or cb == CB_EOF:
                # No args
                continue

            if cb in (CB_LF, CB_LR, CB_LC):
                w = self._read_word()
                self.relocs.append(Reloc(self.clc, CONTROL_NAMES[cb], w,
                                          self.unit_idx))
                self.clc += 1
                continue

            if cb in (CB_AFF, CB_ARF, CB_AFR, CB_ARR):
                w1 = self._read_word()
                w2 = self._read_word()
                # w2 is the address being fixed up; w1 is the value to add
                # Record at the FIXUP TARGET ADDRESS, not at CLC
                self.relocs.append(Reloc(w2, CONTROL_NAMES[cb] + ".val", w1,
                                          self.unit_idx))
                # NOTE: fix-up doesn't advance CLC
                continue

            if cb == CB_SFL:
                w = self._read_word()
                self.clc = w
                continue

            if cb == CB_AFL:
                w = self._read_word()
                # Fill (W1) zeros, advance CLC by W1
                self.clc += w
                continue

            if cb == CB_SRL:
                w = self._read_word()
                self.clc = w + self.pb
                continue

            if cb == CB_LNF:
                w = self._read_word()
                for _ in range(w):
                    word = self._read_word()
                    self.relocs.append(Reloc(self.clc, "LF", word, self.unit_idx))
                    self.clc += 1
                continue

            if cb == CB_RT:
                prio = self._read_word()
                if cur_unit:
                    cur_unit.rt_priority = prio
                continue

            if cb in (CB_MAIN, CB_ENTR, CB_LIBR, CB_REF):
                # Per ND-60.066.04 §2.9 "MAIN 2(3)" means the S-group is 2 words
                # (3 if LONGF). There is NO trailing P-group; the symbol's value
                # is set by the loader (= current CLC for MAIN/ENTR, or a
                # back-link for REF, or conditional for LIBR).
                sym = decode_symbol_packed(self._read_sgroup())
                if cur_unit:
                    cur_unit.symbols.append(
                        Symbol(name=sym, kind=CONTROL_NAMES[cb], addr=self.clc)
                    )
                continue

            if cb == CB_ASF:
                sym = decode_symbol_packed(self._read_sgroup())
                length = self._read_word()
                if cur_unit:
                    cur_unit.symbols.append(
                        Symbol(name=f"COMMON:{sym}({length})", kind="ASF",
                               addr=length)
                    )
                continue

            if cb == CB_ADS:
                sym = decode_symbol_packed(self._read_sgroup())
                if cur_unit:
                    cur_unit.symbols.append(
                        Symbol(name=sym, kind="ADS", addr=0)
                    )
                continue

            # CC-100 dialect: string-segment markers (no args)
            if cb in (CB_CC_STRSEG_BEG, CB_CC_STRSEG_END):
                continue

            # CC-100 dialect: REF fix-up sub-markers (1 P-group arg)
            if cb in (CB_CC_REFFIX_A, CB_CC_REFFIX_B):
                w = self._read_word()
                if cur_unit:
                    cur_unit.symbols.append(
                        Symbol(name=f"CC{cb:o}.subref", kind=CONTROL_NAMES[cb], addr=w)
                    )
                continue

            # Unknown control byte — print and continue (defensive)
            print(f"; warning: unknown BRF control byte 0o{cb:o} at offset {self.pos-1}",
                  file=sys.stderr)

        return self.units


# --- High-level helpers ---

def parse_brf(data: bytes, base_address: int = 0) -> BRFParser:
    """Parse a BRF byte stream and return the populated parser."""
    p = BRFParser(maybe_strip_parity(data), base_address)
    p.parse()
    return p


def reloc_kinds(parser: BRFParser) -> dict[int, str]:
    """Return {addr: kind} for every relocation entry."""
    return {r.addr: r.kind for r in parser.relocs}


def relocated_addresses(parser: BRFParser) -> set[int]:
    """Set of memory addresses that hold RELOCATED ADDRESSES (LR or ARF/ARR)."""
    return {r.addr for r in parser.relocs
            if r.kind in ("LR", "LC", "ARF.val", "ARR.val")}


def materialize_memory(parser: BRFParser) -> dict[int, int]:
    """Apply all BRF records to produce a {addr: word} memory image.

    Per ND-60.066.04 §2.9 + empirical refinements from HSERV1 validation:

      LF  loads W1 unmodified at CLC                          [VERIFIED]
      LR  W1 is a 1-indexed word ordinal; loaded value at CLC is (W1-1) + PB
          when W1 != 0; LR with W1=0 is a placeholder waiting for an AFR/ARR
          fix-up to supply the symbol value.                   [empirical]
      LC  loads W1 + CDB at CLC (CDB=0 assumed; we don't model COMMON)
      AFR fix-up: W2 is a 1-indexed word ordinal selecting the target word
                  within the unit (target = PB + W2 - 1).
                  For LF-targeted (= jump/displacement fix-up): add = W1 raw.
                  For LR-targeted (= pointer fix-up): add = W1 - 1.
                  Same applies to ARR (raises the conditional add by PB).
      AFF/ARF: W2 is interpreted as the absolute target address (no -1).
               W1 for AFF is raw; for ARF, add = W1 + PB.

    The LF-vs-LR-target distinction is determined from the FIRST-PASS state:
    if memory[target] was set by an LR record, the fix-up applies the
    ordinal-to-offset shift; otherwise it adds the raw W1.

    This rule has been empirically validated against HSERV1:BRF vs
    HSERV1:PROG (201 / 281 LF-only match → 281 / 281 with the rule above).
    """
    mem: dict[int, int] = {}
    target_was_lr: dict[int, bool] = {}  # tracks LR-target identity

    # Pre-pass: establish initial values from LF/LR/LC.
    for r in parser.relocs:
        if r.kind in ("LF", "LR", "LC"):
            unit = parser.units[r.unit - 1] if r.unit > 0 else None
            pb = unit.base if unit else 0
            if r.kind == "LF":
                mem[r.addr] = r.value & 0xFFFF
                target_was_lr[r.addr] = False
            elif r.kind == "LR":
                # When W1=0 the slot is a placeholder for an upcoming AFR
                # fix-up that supplies the full address. Leaving the initial
                # value at 0 makes the fix-up math work out (AFR's W1 will
                # be the 1-indexed ordinal whose -1 is the actual target).
                if r.value == 0:
                    mem[r.addr] = 0
                else:
                    mem[r.addr] = ((r.value - 1) + pb) & 0xFFFF
                target_was_lr[r.addr] = True
            elif r.kind == "LC":
                mem[r.addr] = r.value & 0xFFFF
                target_was_lr[r.addr] = False

    # Second pass: apply fix-ups.
    for r in parser.relocs:
        if not r.kind.endswith(".val"):
            continue
        unit = parser.units[r.unit - 1] if r.unit > 0 else None
        pb = unit.base if unit else 0
        kind = r.kind[:-4]
        if kind == "AFF":
            target = r.addr
            add = r.value
        elif kind == "ARF":
            target = r.addr
            add = (r.value + pb) & 0xFFFF
        elif kind == "AFR":
            target = (pb + r.addr - 1) & 0xFFFF
            is_lr = target_was_lr.get(target, False)
            add = (r.value - 1) if is_lr else r.value
        elif kind == "ARR":
            target = (pb + r.addr - 1) & 0xFFFF
            is_lr = target_was_lr.get(target, False)
            add = ((r.value - 1) if is_lr else r.value) + pb
            add &= 0xFFFF
        else:
            continue
        old = mem.get(target, 0)
        mem[target] = (old + add) & 0xFFFF

    return mem


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("brf", type=Path, help=":BRF file to parse")
    p.add_argument("--base", type=lambda s: int(s, 0), default=0,
                   help="initial CLC (load address)")
    p.add_argument("--show-reloc", action="store_true",
                   help="print every relocation entry")
    p.add_argument("--out", type=Path, default=None,
                   help="write reloc map to file (one line per address)")
    p.add_argument("--names", action="store_true",
                   help="list every symbol the file DEFINES (MAIN and ENTR), sorted, one per "
                        "line, and nothing else")
    p.add_argument("--refs", action="store_true",
                   help="with --names: list the symbols the file only REFERS to (REF) instead")
    p.add_argument("--find", metavar="NAME", default=None,
                   help="show which unit defines (ENTR/MAIN/LIBR) or refers to (REF) NAME")
    p.add_argument("--json", action="store_true",
                   help="print the units and symbols as JSON and nothing else")
    args = p.parse_args()

    data = args.brf.read_bytes()
    parser = parse_brf(data, args.base)
    units = parser.units

    if args.names:
        want = ("REF",) if args.refs else ("MAIN", "ENTR")
        for name in sorted({s.name for u in units for s in u.symbols if s.kind in want}):
            print(name)
        return

    if args.find:
        for i, u in enumerate(units, 1):
            for s in u.symbols:
                if s.name == args.find:
                    defs = " ".join(t.name for t in u.symbols if t.kind in ("MAIN", "ENTR"))
                    print(f"unit {i}: {s.kind} {s.name}   (unit defines: {defs})")
        return

    if args.json:
        import json
        print(json.dumps({"file": args.brf.name, "units": [
            {"unit": i, "offset": u.offset, "checksum_ok": u.checksum_ok, "longf": u.longf,
             "comment": u.comment,
             "symbols": [{"kind": s.kind, "name": s.name} for s in u.symbols
                         if s.kind in ("MAIN", "ENTR", "LIBR", "REF")]}
            for i, u in enumerate(units, 1)]}, indent=1))
        return

    bad = [i for i, u in enumerate(units, 1) if u.checksum_ok is not True]
    print(f"# BRF parse of {args.brf.name} ({len(data)} bytes)")
    print(f"# {len(units)} program unit(s), {len(parser.relocs)} reloc entries")
    print(f"# LONGF: {parser.longf}")
    print(f"# checksums: {len(units) - len(bad)} of {len(units)} units ok"
          + (f"; NOT ok: units {bad[:10]}" if bad else ""))
    print()

    for i, u in enumerate(units):
        print(f"## Unit {i}: base=0o{u.base:o}, end=0o{u.end:o}, "
              f"checksum=0o{u.checksum:o}" + ("" if u.checksum_ok else "  CHECKSUM WRONG"))
        if u.comment:
            print(f"   comment: {u.comment}")
        if u.rt_priority is not None:
            print(f"   RT priority: {u.rt_priority}")
        for s in u.symbols:
            print(f"   {s.kind:5s} {s.name:8s} = 0o{s.addr:o}")

    if args.show_reloc:
        print()
        print("# Relocation entries:")
        for r in parser.relocs:
            print(f"  0o{r.addr:06o}  {r.kind:5s}  0o{r.value:06o}  (unit {r.unit})")

    if args.out:
        # Write {addr -> kind} map
        lines = [f"0o{r.addr:o}\t{r.kind}\t0o{r.value:o}" for r in parser.relocs]
        args.out.write_text("\n".join(lines))
        print(f"\nWrote reloc map to {args.out}")

    # Summary stats
    kinds: dict[str, int] = {}
    for r in parser.relocs:
        kinds[r.kind] = kinds.get(r.kind, 0) + 1
    print("\n# Relocation kind histogram:")
    for k, c in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"  {k:8s} {c:6d}")


if __name__ == "__main__":
    main()
