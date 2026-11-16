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
  <control_byte><S-group>              — 1 S-group (MAIN, LIBR, ENTR, REF, ADS)
  <control_byte><S-group><P-group>     — S+P (ASF)
  (two-bank files also use PMO/DMO with no args and LRP/LRD with one P-group)

A P-group is one 16-bit word, big-endian, 2 bytes.
An S-group is a packed symbol — 4 bytes default, 6 bytes if LONGF flag set.

Loading rules this file follows (measured; see BRF-FILE-FORMAT.md, sections 3 and 4):
  - PB = CLC at BEG minus 1, so LR W loads W + PB and AFR W1,W2 changes word W2 + PB.
  - REF takes one word at CLC (the reference chain of ND-60.066.04 section 2.5).
  - Two-bank files: one CLC and one PB per bank; DMO selects the data bank, PMO and every
    BEG the program bank. The data bank starts at 0 here (its real start is set at load time).
  - Everything after EOF is ignored. materialize_memory() loads the file and lists what it
    could not load cleanly in parser.problems (broken reference chains, symbols defined
    twice, units past 0177777).
An earlier version used PB = CLC with "W - 1" corrections in LR and AFR, did not give REF a
word, and read the two-bank groups as C-compiler markers; names and checksums were right,
loaded addresses were not.

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
CB_BEG  = 0o17   # start of program unit, PB := CLC - 1 (measured, see BRFParser)
CB_REF  = 0o20   # S-group: reference to a symbol; TAKES ONE WORD at CLC (see BRFParser)
CB_END  = 0o21   # end of unit + checksum
CB_INHB = 0o22   # compilation errors flag (no args)
CB_EOF  = 0o23   # end of loading (no args)
CB_LNF  = 0o24   # 1+W1: load W1 words
CB_RT   = 0o25   # RT priority (1 word)
CB_ASF  = 0o26   # COMMON block (S+P)
CB_ADS  = 0o27   # add common (S only)
CB_LONGF = 0o32  # set 6-byte S-group mode for the rest of the unit
CB_DBG  = 0o47   # debug mode on/off (no args)
CB_PMO  = 0o50   # two-bank: load into the program bank (no args)
CB_DMO  = 0o51   # two-bank: load into the data bank (no args)
CB_LRP  = 0o52   # two-bank: load W + program-bank PB at CLC of the CURRENT bank
CB_LRD  = 0o53   # two-bank: load W + data-bank PB at CLC of the CURRENT bank
CB_DIC  = 0o54   # dictionary table follows, ends with a 177777 word (made by MAKE-LIBRARY-FILE)

# Groups with a fixed shape that this tool reads past but does not interpret:
# control number -> (has S-group, number of P-groups).  INL DBL RLL CXL / INC DBC RLC CXC / BYL BYC / NWL
EXTRA_GROUPS = {
    0o34: (False, 2), 0o35: (False, 3), 0o36: (False, 4), 0o37: (False, 7),
    0o40: (True, 2), 0o41: (True, 3), 0o42: (True, 4), 0o43: (True, 7),
    0o44: (False, 2), 0o45: (True, 3), 0o46: (False, 1),
}

# 0o50-0o53 are the two-bank groups PMO, DMO, LRP, LRD (ND-60.066.04 section 2.9). An earlier
# version of this file read them as "CC-100 string-segment markers" (0o50/0o51) and "REF fix-up
# sub-markers" (0o52/0o53), guessed from the C runtime. The byte widths are the same, so names
# and checksums came out right, but addresses in two-bank files did not. Census of the 48 BRF
# files in this repository (2026-11-16): PMO 1838, DMO 1813, LRP 2452, LRD 387, all in the 13
# two-bank (-2 / 2BANK) files.

CONTROL_NAMES = {
    CB_FEED: "FEED", CB_LF: "LF", CB_LR: "LR", CB_LC: "LC",
    CB_AFF: "AFF", CB_ARF: "ARF", CB_AFR: "AFR", CB_ARR: "ARR",
    CB_SFL: "SFL", CB_AFL: "AFL", CB_SRL: "SRL",
    CB_MAIN: "MAIN", CB_LIBR: "LIBR", CB_ENTR: "ENTR",
    CB_BEG: "BEG", CB_REF: "REF", CB_END: "END",
    CB_INHB: "INHB", CB_EOF: "EOF", CB_LNF: "LNF",
    CB_RT: "RT", CB_ASF: "ASF", CB_ADS: "ADS",
    CB_LONGF: "LONGF", CB_PMO: "PMO", CB_DMO: "DMO", CB_LRP: "LRP", CB_LRD: "LRD",
}


# --- Symbol decoding (six-bit characters, ND-60.066.04 section 2) ---
# An S-group is 4 bytes (32 bits) or, after LONGF, 6 bytes (48 bits). The bits are packed
# six to a character, MOST significant first, right-justified. The six-bit code is the LOW SIX
# BITS OF ASCII: 1-32 octal = A-Z, 33-37 = [ \ ] ^ _, 40-77 = space ! " # $ ... 0-9 ... ?.
# So a letter is code + 0100, anything from 040 up is the ASCII value itself, and 0 is a space
# (padding). Checked against the BRF linker's own LIST-BRF-ENTRIES on FORT48-2BANK-F02:BRF:
# 462 of 462 names identical.
def decode_symbol_packed(buf: bytes) -> str:
    """Decode an S-group into its symbol name (trailing and leading spaces removed).

    FORTRAN/BASIC statement-number labels are not names: in a 6-byte S-group the first two
    and last two bytes are zero and bytes 3-4 hold the label number (ND-60.066.04 section
    2.3). They are returned as "STMT_" + the decimal number, as the ghidra-nd100 BRF loader
    does. Read as six-bit text they give junk such as "Y", "[" or "#J" (X25-LTST-C00).
    """
    if len(buf) == 6 and buf[0] == 0 and buf[1] == 0 and buf[4] == 0 and buf[5] == 0 \
            and (buf[2] or buf[3]):
        return f"STMT_{(buf[2] << 8) | buf[3]}"
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
    bank: int = 0       # 0 = program bank, 1 = data bank (two-bank files, after DMO)
    name: str = ""      # symbol name for REF and DEF entries


@dataclass
class Symbol:
    name: str
    kind: str           # MAIN | ENTR | LIBR | REF
    addr: int           # address of the entry (or referencing location for REF)
    bank: int = 0       # 0 = program bank, 1 = data bank


@dataclass
class ProgramUnit:
    base: int                       # program-bank PB: CLC at BEG minus 1
    end: int                        # last program-bank word loaded
    checksum: int = 0
    checksum_ok: bool | None = None  # None until the unit's END group has been read
    offset: int = 0                  # byte offset of the unit's BEG in the file
    symbols: list[Symbol] = field(default_factory=list)
    rt_priority: int | None = None
    longf: bool = False
    data_base: int = 0               # data-bank PB (two-bank files): data CLC at BEG minus 1
    data_end: int = -1               # last data-bank word loaded, -1 if none
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
        # One load counter and one base per bank. Bank 0 = program (the only bank of a
        # one-bank file), bank 1 = data (two-bank files, selected by DMO). Measured over the
        # 13 two-bank files in this repository: with separate counters 1720 of 1724 fix-ups
        # land on words already loaded in the current bank; with one shared counter 48 land
        # on words never loaded. The data bank's start address is set at load time and is
        # not in the file; it starts at 0 here.
        self.clcs = [base_address, 0]
        self.pbs = [0, 0]
        self.bank = 0
        self.twobank = False
        self.unit_idx = 0
        self.units: list[ProgramUnit] = []
        self.relocs: list[Reloc] = []
        self.longf: bool = False     # 6-byte S-groups when set (reset at every BEG)
        self.csum: int = 0           # running unit checksum: control bytes + P-groups + S-group words
        self.problems: list[str] = []

    @property
    def clc(self) -> int:
        return self.clcs[self.bank]

    @clc.setter
    def clc(self, v: int) -> None:
        # NOT masked to 16 bits: a file whose units together pass 0177777 (a library loaded
        # whole: X25-UTILITY-C00, TCP-ERROR-1-B05) keeps counting upward instead of wrapping
        # onto its own start. The real loader would load only the library units something
        # references. Addresses above 0177777 are reported in problems.
        if v > 0xFFFF and self.clcs[self.bank] <= 0xFFFF:
            self.problems.append(f"unit {self.unit_idx} runs past 0177777; addresses from here"
                                 f" on are counted past 64K words (no real load would hold all"
                                 f" of these units)")
        self.clcs[self.bank] = v

    @property
    def pb(self) -> int:
        return self.pbs[self.bank]

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
                # Every BEG starts in the program bank. PB = CLC - 1: measured on the real
                # BRF-LINKER (an LR 1 in the first word loads the unit's own first address)
                # and over 4701 fix-ups in five files (BRF-FILE-FORMAT.md section 3).
                self.bank = 0
                self.pbs = [self.clcs[0] - 1, self.clcs[1] - 1]
                cur_unit = ProgramUnit(base=self.pbs[0], end=self.pbs[0],
                                       offset=self.pos - 1, data_base=self.pbs[1])
                self.units.append(cur_unit)
                self.unit_idx += 1
                self.longf = False
                self.csum = CB_BEG
                continue

            if cur_unit is not None:
                self.csum += cb        # the control byte itself is part of the checksum

            if cb == CB_END:
                if cur_unit is not None:
                    cur_unit.end = self.clcs[0] - 1
                    if self.clcs[1] - 1 != cur_unit.data_base:
                        cur_unit.data_end = self.clcs[1] - 1
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

            if cb == CB_EOF:
                # End of the loading. What follows is padding or junk, not BRF groups (the
                # 48-file census found zero bytes and "00 00 00 00 00 00 00 65 01" there).
                break
            if cb == CB_INHB:
                continue
            if cb in (CB_PMO, CB_DMO):
                self.bank = 0 if cb == CB_PMO else 1
                self.twobank = True
                continue
            if cb in (CB_LRP, CB_LRD):
                # Relocated by the base of the bank the group names, stored in the CURRENT
                # bank: the data bank holds tables of program addresses (LRP in DMO mode).
                w = self._read_word()
                self.relocs.append(Reloc(self.clc, CONTROL_NAMES[cb], w, self.unit_idx,
                                         self.bank))
                self.clc += 1
                continue

            if cb in (CB_LF, CB_LR, CB_LC):
                w = self._read_word()
                self.relocs.append(Reloc(self.clc, CONTROL_NAMES[cb], w,
                                          self.unit_idx, self.bank))
                self.clc += 1
                continue

            if cb in (CB_AFF, CB_ARF, CB_AFR, CB_ARR):
                w1 = self._read_word()
                w2 = self._read_word()
                # W1 is the value to add, W2 the word to change (relative to PB for AFR/ARR,
                # absolute for AFF/ARF). Stored with the raw W2; materialize_memory() works out
                # the target. AFF and ARF occur in none of the 48 files in this repository.
                self.relocs.append(Reloc(w2, CONTROL_NAMES[cb] + ".val", w1,
                                          self.unit_idx, self.bank))
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
                    self.relocs.append(Reloc(self.clc, "LF", word, self.unit_idx, self.bank))
                    self.clc += 1
                continue

            if cb == CB_RT:
                prio = self._read_word()
                if cur_unit:
                    cur_unit.rt_priority = prio
                continue

            if cb in (CB_MAIN, CB_ENTR, CB_LIBR, CB_REF):
                # MAIN, ENTR, LIBR, REF: an S-group of 2 words (3 after LONGF), no P-group.
                sym = decode_symbol_packed(self._read_sgroup())
                if cur_unit:
                    cur_unit.symbols.append(
                        Symbol(name=sym, kind=CONTROL_NAMES[cb], addr=self.clc, bank=self.bank)
                    )
                if cb == CB_REF:
                    # REF TAKES ONE WORD: the loader stores the symbol's value there or, while
                    # the symbol is undefined, a link to the previous reference of it (177777
                    # for the first) - ND-60.066.04 section 2.5. Measured: with REF taking a
                    # word every fix-up target is a loaded word; without it 985 of 4701 are not.
                    self.relocs.append(Reloc(self.clc, "REF", 0, self.unit_idx, self.bank, sym))
                    self.clc += 1
                elif cb == CB_ENTR:
                    # Defines the symbol as CLC. LIBR only names the unit for library search.
                    # MAIN marks the start address but is NOT entered as a symbol here: in an
                    # RT load the MAIN name becomes an RT program, and a REF to it gets the RT
                    # DESCRIPTION address (ND-60.051.8, DEFINE-PROGRAM / IGNORE-MAIN), which is
                    # not in the file. X25-LINK-C00 references X25TM, its own MAIN name.
                    self.relocs.append(Reloc(self.clc, "DEF", 0, self.unit_idx, self.bank, sym))
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
    return {r.addr: r.kind for r in parser.relocs if r.bank == 0 and r.kind != "DEF"}


def relocated_addresses(parser: BRFParser) -> set[int]:
    """Set of memory addresses that hold RELOCATED ADDRESSES (LR or ARF/ARR)."""
    out = set()
    for r in parser.relocs:
        if r.bank != 0:
            continue
        if r.kind in ("LR", "LC", "LRP", "LRD", "ARF.val"):
            out.add(r.addr)
        elif r.kind == "ARR.val":
            unit = parser.units[r.unit - 1] if r.unit > 0 else None
            out.add(((unit.base if unit else 0) + r.addr) & 0xFFFF)
    return out


def materialize_memory(parser: BRFParser, bank: int = 0) -> dict[int, int]:
    """Load the file the way BRF-LINKER does and return {addr: word} for one bank.

    Rules (ND-60.066.04 section 2.9; measured where marked):
      PB  = CLC at BEG minus 1, one per bank                             [measured]
      LF  W1 at CLC;  LR  W1 + PB;  LC  W1 + CDB (COMMON not modelled, CDB = 0)
      LRP / LRD  W1 + program-bank / data-bank PB, at CLC of the current bank
      AFF W1 + (W2) -> (W2);       ARF W1 + PB + (W2) -> (W2)
      AFR W1 + (W2+PB) -> (W2+PB); ARR W1 + PB + (W2+PB) -> (W2+PB)
      REF takes one word. A defined symbol's value is stored at once; an undefined
          symbol's word holds a link to its previous reference (177777 for the first)
          and the chain is walked and patched when MAIN/ENTR defines it (section 2.5).
          Checked on BRF-LINKER C01 (2026-11-16): REF to a defined symbol + AFR 5 gives
          symbol + 5. A fix-up onto the word of a still-undefined symbol changes a link;
          the real linker then follows it without a message and writes the address into
          wrong places. Here the walk stops at that word and the problem is added to
          parser.problems.
    Only symbols defined in this file are known; a reference to anything else keeps its
    chain link (or 177777). Library units are all loaded, unlike the real loader.
    """
    mems: list[dict[int, int]] = [{}, {}]
    refs: dict[str, list[tuple[int, int]]] = {}    # name -> [(bank, addr)] of open references
    defs: dict[str, int] = {}
    pbs = [0, 0]
    cur_unit = 0
    for r in parser.relocs:
        if r.unit != cur_unit:
            cur_unit = r.unit
            u = parser.units[r.unit - 1]
            pbs = [u.base, u.data_base]
        m = mems[r.bank]
        pb = pbs[r.bank]
        k = r.kind
        if k == "LF":
            m[r.addr] = r.value & 0xFFFF
        elif k == "LR":
            m[r.addr] = (r.value + pb) & 0xFFFF
        elif k == "LC":
            m[r.addr] = r.value & 0xFFFF
        elif k in ("LRP", "LRD"):
            m[r.addr] = (r.value + pbs[0 if k == "LRP" else 1]) & 0xFFFF
        elif k == "REF":
            if r.name in defs:
                m[r.addr] = defs[r.name] & 0xFFFF
            else:
                chain = refs.setdefault(r.name, [])
                m[r.addr] = (chain[-1][1] & 0xFFFF) if chain else 0xFFFF
                chain.append((r.bank, r.addr))
        elif k == "DEF":
            if r.name in defs:
                parser.problems.append(f"{r.name} defined again in unit {r.unit}")
            defs[r.name] = r.addr
            chain = refs.pop(r.name, [])
            # Walk from the newest reference back, as the loader does, checking each link.
            for i in range(len(chain) - 1, -1, -1):
                b_, a_ = chain[i]
                want = (chain[i - 1][1] & 0xFFFF) if i > 0 else 0xFFFF
                word = mems[b_].get(a_, 0)
                mems[b_][a_] = r.addr & 0xFFFF
                if word != want:
                    parser.problems.append(
                        f"reference chain of {r.name} broken at 0o{a_:06o} (a fix-up changed it)")
                    break
        elif k.endswith(".val"):
            k = k[:-4]
            target = r.addr if k in ("AFF", "ARF") else r.addr + pb
            add = r.value + (pb if k in ("ARF", "ARR") else 0)
            m[target] = (m.get(target, 0) + add) & 0xFFFF
    return mems[bank]


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

    materialize_memory(parser)      # loads the file; fills parser.problems
    if parser.problems:
        print(f"\n# {len(parser.problems)} problem(s) found while loading:")
        for x in parser.problems:
            print(f"  {x}")

    # Summary stats
    kinds: dict[str, int] = {}
    for r in parser.relocs:
        kinds[r.kind] = kinds.get(r.kind, 0) + 1
    print("\n# Relocation kind histogram:")
    for k, c in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"  {k:8s} {c:6d}")


if __name__ == "__main__":
    main()
