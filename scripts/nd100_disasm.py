"""ND-100 / ND-110 disassembler — covers the SINTRAN III user-mode ISA
plus most privileged instructions.

Reference: ND-60.096.01 MAC Interactive Assembly and Debugging System §2.3
(NORD-10 Instruction Repertoire). The ND-100 is binary-compatible with
NORD-10/S at the user-mode ISA level used by SINTRAN III programs.

PROG file layout (verified against HSERV1 / HPING / XMSG-HDLC-TEST):
  bytes 0..0xFF       SINTRAN PROG header (256 bytes)
  bytes 0x100..end    program memory image (BE 16-bit words; addr 0 = file offset 0x100)

See `SINTRAN/File-Formats/PROG-FILE-FORMAT.md` for the file layout details,
and `Developer/Reverse-Engineering/` for the decode reference and workflow.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROG_HEADER_BYTES = 0x100


# =========================================================================
# PROG file conventions
# =========================================================================

def parse_prog_header(data: bytes) -> dict:
    if len(data) < PROG_HEADER_BYTES:
        return {}
    def w(idx: int) -> int:
        return (data[idx * 2] << 8) | data[idx * 2 + 1]
    name_bytes = data[24 * 2:28 * 2]
    lib_name = "".join(chr(b) for b in name_bytes if 32 <= b < 127)
    return {
        "end_addr": w(3), "marker": w(4), "build_id": w(14),
        "const21": w(21), "library": lib_name,
    }


# =========================================================================
# Decoding primitives
# =========================================================================

def signed8(v: int) -> int:
    return v - 256 if v & 0x80 else v


def signed7(v: int) -> int:
    return v - 128 if v & 0x40 else v


# Source/destination register name maps
SRC_REG = {0o00: "0", 0o10: "SD", 0o20: "SP", 0o30: "SB",
           0o40: "SL", 0o50: "SA", 0o60: "ST", 0o70: "SX"}
DST_REG = {0o0: "STS", 0o1: "DD", 0o2: "DP", 0o3: "DB", 0o4: "DL",
           0o5: "DA", 0o6: "DT", 0o7: "DX"}


# Memory-reference opcodes (top 4 bits)
MEM_OPS = {
    0o000000: "STZ", 0o004000: "STA", 0o010000: "STT", 0o014000: "STX",
    0o020000: "STD", 0o024000: "LDD", 0o030000: "STF", 0o034000: "LDF",
    0o040000: "MIN", 0o044000: "LDA", 0o050000: "LDT", 0o054000: "LDX",
    0o060000: "ADD", 0o064000: "SUB", 0o070000: "AND", 0o074000: "ORA",
    0o100000: "FAD", 0o104000: "FSB", 0o110000: "FMU", 0o114000: "FDV",
    0o120000: "MPY",
    0o124000: "JMP", 0o134000: "JPL",
}

JCC_OPS = {
    0o130000: "JAP", 0o130400: "JAN", 0o131000: "JAZ", 0o131400: "JAF",
    0o132000: "JPC", 0o132400: "JNC", 0o133000: "JXZ", 0o133400: "JXN",
}

ARG_OPS = {
    0o170000: "SAB", 0o170400: "SAA",
    0o171000: "SAT", 0o171400: "SAX",
    0o172000: "AAB", 0o172400: "AAA",
    0o173000: "AAT", 0o173400: "AAX",
}

# Known MON-call numbers (extracted from ND-860228-2-EN SINTRAN III Monitor Calls).
# Numbers are OCTAL (matching MAC convention). 125 names verified — includes
# 0o0=ExitFromProgram, 0o1=InByte, 0o2=OutByte, 0o122=ReserveResource,
# 0o123=ReleaseResource, 0o201=HDLCfunction. Update via the extraction script
# at scripts/extract_mon_names.py if you want to refresh.
MON_NAMES = {
    0o0: 'ExitFromProgram',
    0o1: 'InByte',
    0o2: 'OutByte',
    0o3: 'SetEcho',
    0o4: 'SetBreak',
    0o6: 'WriteScratchFile',
    0o7: 'ReadBlock',
    0o10: 'WriteBlock',
    0o13: 'ClearInBuffer',
    0o14: 'ClearOutBuffer',
    0o16: 'GetTerminalType',
    0o17: 'SetTerminalType',
    0o23: 'In8Bytes',
    0o24: 'Out8Bytes',
    0o26: 'GetLastByte',
    0o27: 'GetRTDescr',
    0o30: 'GetOwnRTAddress',
    0o31: 'IOInstruction',
    0o32: 'OutMessage',
    0o36: 'NoWaitSwitch',
    0o37: 'ReadADChannel',
    0o40: 'CloseSpoolingFile',
    0o41: 'ReadObjectEntry',
    0o43: 'Closefile',
    0o44: 'GetUserEntry',
    0o50: 'OpenFile',
    0o53: 'GetSegmentEntry',
    0o54: 'DeleteFile',
    0o55: 'GetSpoolingEntry',
    0o57: 'GetUserParam',
    0o62: 'GetBytesInFile',
    0o65: 'ErrorMessage',
    0o66: 'InBufferSpace',
    0o70: 'CallCommand',
    0o71: 'DisableEscape',
    0o73: 'SetMaxBytes',
    0o74: 'SetStartByte',
    0o75: 'GetStartByte',
    0o76: 'SetBlockSize',
    0o77: 'SetStartBlock',
    0o101: 'DelayStart',
    0o103: 'StartupInterval',
    0o105: 'StopRTProgram',
    0o106: 'StartOnInterrupt',
    0o107: 'NoInterruptStart',
    0o110: 'SetRTPriority',
    0o111: 'SetClock',
    0o112: 'AdjustClock',
    0o114: 'GetTimeUsed',
    0o115: 'FixScattered',
    0o117: 'ReadFromFile',
    0o120: 'WriteToFile',
    0o121: 'AwaitFileTransfer',
    0o122: 'ReserveResource',
    0o123: 'ReleaseResource',
    0o124: 'ForceReserve',
    0o126: 'ExactDelayStart',
    0o130: 'ExactInterval',
    0o137: 'DisableRTStart',
    0o140: 'ReservationInfo',
    0o141: 'DeviceControl',
    0o142: 'ToErrorDevice',
    0o144: 'DeviceFunction',
    0o147: 'CAMACfunction',
    0o150: 'CAMACGLRegister',
    0o151: 'GetRTAddress',
    0o152: 'GetRTName',
    0o153: 'CAMACIOInstruction',
    0o154: 'AssignCAMACLAM',
    0o155: 'Graphic',
    0o157: 'SegmentToPageTable',
    0o160: 'FixContiguous',
    0o161: 'InString',
    0o200: 'XMSGFunction',          # Program-to-program comm; from manual cross-ref table (not in MON N %Monitor call form)
    0o201: 'HDLCfunction',
    0o213: 'GetDirUserIndexes',
    0o214: 'GetUserName',
    0o215: 'GetObjectEntry',
    0o216: 'SetObjectEntry',
    0o217: 'GetAllFileIndexes',
    0o220: 'DirectOpen',
    0o221: 'CreateFile',
    0o230: 'GetEscLocalChar',
    0o231: 'ExpandFile',
    0o233: 'SetTemporaryFile',
    0o234: 'SetPeripheralFile',
    0o236: 'SetPermanentOpen',
    0o240: 'AppendSpooling',
    0o241: 'NewUser',
    0o242: 'OldUser',
    0o243: 'GetDirNameIndex',
    0o244: 'GetDirEntry',
    0o245: 'GetNameEntry',
    0o246: 'ReserveDir',
    0o247: 'ReleaseDir',
    0o250: 'GetDefaultDir',
    0o251: 'CopyPage',
    0o252: 'BackupClose',
    0o253: 'NewFileVersion',
    0o254: 'GetErrorDevice',
    0o256: 'FullFileName',
    0o257: 'OpenFileInfo',
    0o262: 'GetSystemInfo',
    0o263: 'GetDeviceType',
    0o267: 'TimeOut',
    0o271: 'WriteDiskPage',
    0o272: 'DeletePage',
    0o273: 'GetFileName',
    0o274: 'GetFileIndexes',
    0o275: 'SetTerminalName',
    0o306: 'GetTerminalMode',
    0o307: 'TerminalNoWait',
    0o310: 'In8AndFlag',
    0o311: 'WriteDirEntry',
    0o312: 'CheckMonCall',
    0o313: 'InBufferState',
    0o322: 'GetSegmentNo',
    0o323: 'SegmentOverlay',
    0o324: 'OctobusFunction',
    0o326: 'LogInStart',
    0o327: 'FileSystemFunction',
    0o330: 'TerminalStatus',
    0o332: 'TerminalStatus',
    0o333: 'DMAFunction',
    0o334: 'GetErrorMessage',
    0o335: 'DataTransfer',
}


# =========================================================================
# Addressing-mode decode (memory-reference family)
# =========================================================================

def decode_ea(w: int, pc: int):
    """For a memory-reference instruction, return (ea_text, target_addr_or_None).
    target_addr is only resolved for P-rel and P-indirect modes (B-rel /
    X-rel depend on runtime register state).
    """
    disp = signed8(w & 0xFF)
    mode = w & 0o3400
    if mode == 0o0000:
        return f"L{(pc + disp) & 0xFFFF:o}", (pc + disp) & 0xFFFF
    if mode == 0o0400:
        return f"{disp},B", None
    if mode == 0o1000:
        return f"I L{(pc + disp) & 0xFFFF:o}", (pc + disp) & 0xFFFF
    if mode == 0o1400:
        return f"I {disp},B", None
    if mode == 0o2000:
        return f"{disp},X", None
    if mode == 0o2400:
        return f"{disp},B,X", None
    if mode == 0o3000:
        return f"I L{(pc + disp) & 0xFFFF:o},X", (pc + disp) & 0xFFFF
    if mode == 0o3400:
        return f"I {disp},B,X", None
    return "?", None


# =========================================================================
# Register-op decode (0o140000..0o147777 family)
# =========================================================================

# Combined register-op codes (§2.3.5 + §2.3 Combined Instructions)
REG_OPS = {
    # The high octet's bits 11-9 select function (RAD=1 family vs RAD=0 family)
    # Plus QC, IC modifiers, plus AD1/CLD/CM1/CM2 modifiers in bits 4-9.
    # We do a coarse classification by the function field bits 9-6.
    # Codes encode: opcode + AD1(bit 8) + ADC(bit 9) + CLD(bit 7) + CM1(bit 8) +CM2(bit 7+8)
    # See full table in ND-60.096.01 §2.3.5.
}


def decode_reg_op(w: int) -> str:
    """Decode a register-operations instruction (top 4 = 1100).
    Format: 1100 | QC | IC | R | source[3] | destin[3]
    Combined ops have bit-7/bit-8 modifiers (AD1, ADC, CLD, CM1, CM2).
    """
    # Common shortcuts (combined instructions per §2.3 Combined)
    if w == 0o146142: return "EXIT"          # COPY SL DP
    if w == 0o146100: return "RCLR"          # COPY 0 0   (clear)
    if w == 0o146400: return "RINC"          # RADD AD1
    if w == 0o146200: return "RCDR"          # RADD CM1

    sr = w & 0o70
    dr = w & 0o7
    sr_n = SRC_REG.get(sr, f"S?{sr:o}")
    dr_n = DST_REG.get(dr, f"D?{dr:o}")

    # Determine base opcode by bits 11-6 (excluding the modifier bits 7-8)
    op_field = w & 0o7700
    BASE_OP = {
        0o6000: "RADD", 0o6100: "COPY", 0o6600: "RSUB",
        0o4000: "SWAP", 0o4400: "RAND", 0o5000: "REXO", 0o5400: "RORA",
        # Extended arithmetic (no separate src/dst encoding in the same way)
        0o1200: "RMPY", 0o1600: "RDIV",
    }
    op = BASE_OP.get(op_field)
    if op:
        # Modifier bits per ND-60.096.01 §2.3.5
        # CLD (bit 7), CM1 (bit 8), AD1 (bit 8 too? — actually different table per RAD)
        # We just print core form.
        return f"{op} {sr_n} {dr_n}".rstrip()
    return f"REG 0o{w:06o}  ; sr={sr_n} dr={dr_n}"


# =========================================================================
# Skip-instructions decode (0o140000..0o140777 — RAD=0, IC=QC=0, sub-class)
# =========================================================================

# SKP format: 1100 0 | condition[2:0] | source[3] | destin[3]
SKP_CONDS = {
    0o0000: "EQL", 0o0400: "GRE", 0o1000: "MGRE",   # signed greater-or-equal / magnitude
    0o2000: "UEQ", 0o2400: "LST", 0o3000: "MLST",
}


def maybe_skp(w: int) -> str | None:
    """Detect and decode SKP instructions.
    Per §2.3.7: SKP base = 0o140000, with condition bits 11-9 distinguishing.
    But this overlaps the reg-op range, so detect by checking common SKP forms.
    """
    if (w & 0o170000) != 0o140000:
        return None
    # The reg-op family also lives here; SKP is distinguished by bit pattern.
    # Easiest heuristic: SKP instruction has form 0o14X000 + cond + sr + dr,
    # where bits 11-10 are 00 (vs reg-op which has 01-10 set).
    # Per the manual table, SKP = 0o140000 exactly with cond/src/dst encoded in low bits.
    if (w & 0o7000) == 0o000:        # the RAD/QC/IC fields are zero
        sr = w & 0o70
        dr = w & 0o7
        cond_bits = w & 0o3400
        cond = SKP_CONDS.get(cond_bits, f"?{cond_bits:o}")
        sr_n = SRC_REG.get(sr, f"S{sr:o}")
        dr_n = DST_REG.get(dr, f"D{dr:o}")
        return f"SKP {cond} {sr_n} {dr_n}"
    return None


# =========================================================================
# Shift-instructions decode (0o154000..0o155777)
# =========================================================================

SHIFT_TARGET = {0o000: "SHT", 0o200: "SHD", 0o400: "SHA", 0o600: "SAD"}
SHIFT_MODE   = {0o000: "ARITH", 0o1000: "ROT", 0o2000: "ZIN", 0o3000: "LIN"}


def decode_shift(w: int) -> str:
    """Per ND-60.096.01 §2.3.8."""
    if (w & 0o174000) != 0o154000:
        return None
    target = w & 0o600
    mode = w & 0o3000
    count = signed7(w & 0o177)         # signed 7-bit shift count; negative = right-shift
    op = SHIFT_TARGET.get(target, "SH?")
    mod = SHIFT_MODE.get(mode, "")
    if count == 0:
        return f"{op}"
    direction = "SHR" if count < 0 else ""
    return f"{op} {direction} {abs(count)}  {mod}".strip()


# =========================================================================
# Bit-instructions decode (0o174000..0o177777)
# =========================================================================

BIT_OPS = {
    0o174000: "BSET", 0o175000: "BSKP",
    0o176000: "BSTC", 0o176200: "BSTA",
    0o176400: "BLDA", 0o176440: "BLDC",   # 176600/176640 in some tables — check
    0o177000: "BANC", 0o177200: "BAND",
    0o177400: "BORC", 0o177600: "BORA",
}
BIT_CONDS = {0o000: "ZRO", 0o200: "ONE", 0o400: "BCM", 0o600: "BAC"}


def decode_bit(w: int) -> str:
    """Bit instructions: 1111 | function(11-9) | cond(8-6 or 7-5) | bit(5-3) | dst(2-0).
    Tables in manual aren't fully consistent; output a best-effort name."""
    if (w & 0o174000) != 0o174000:
        return None
    op_field = w & 0o177400
    op = BIT_OPS.get(op_field)
    if op is None:
        # Fall back to top 9 bits
        op_field = w & 0o177000
        op = BIT_OPS.get(op_field, f"BIT?")
    cond_field = w & 0o600
    cond = BIT_CONDS.get(cond_field, "?")
    bit_no = (w >> 3) & 0o17
    dst = w & 0o7
    dst_n = DST_REG.get(dst, "?")
    return f"{op} {cond} bit{bit_no} {dst_n}"


# =========================================================================
# Privileged / system / interlevel decode
# =========================================================================

PRIV_NAMED = {
    0o150401: "IOF", 0o150402: "ION",
    0o150404: "POF", 0o150410: "PON",
    0o151000: "WAIT 0",
    0o151400: "NLZ",                # integer-to-floating
    0o152000: "DNZ",                # floating-to-integer
    0o152402: "SRB",                # store register block (priv)
    0o152600: "LRB",                # load register block (priv)
    0o143600: "IDENT",              # interrupt identification (priv)
}
SYS_PREFIX = {
    0o150000: "TRA", 0o150100: "TRR",
    0o150200: "MCL", 0o150300: "MST",
    0o150400: "OPCOM",              # (octal range)
    0o153400: "IRR",                # inter-register read (priv)
    0o153600: "IRW",                # inter-register write (priv)
}


def decode_priv(w: int) -> str | None:
    if w in PRIV_NAMED:
        return PRIV_NAMED[w]
    # OPR / panel-info: 150400-150477 (OPCOM family)
    if (w & 0o177400) == 0o150400:
        return f"OPCOM 0o{w & 0o377:o}"
    # IRR/IRW have level encoded in low bits
    op_hi = w & 0o177700
    if op_hi == 0o153400:
        return f"IRR 0o{w & 0o77:o}"
    if op_hi == 0o153600:
        return f"IRW 0o{w & 0o77:o}"
    # TRA/TRR/MCL/MST take a register code in low 6 bits
    op_hi2 = w & 0o177700
    if op_hi2 in SYS_PREFIX:
        return f"{SYS_PREFIX[op_hi2]} 0o{w & 0o77:o}"
    return None


# =========================================================================
# Byte instructions decode (SBYT/LBYT)
# =========================================================================

def decode_byte(w: int) -> str | None:
    if w == 0o142600:
        return "SBYT"
    if w == 0o142200:
        return "LBYT"
    return None


# =========================================================================
# Top-level decoder
# =========================================================================

def decode(w: int, pc: int) -> tuple[str, int | None]:
    """Decode word `w` at memory address `pc`. Returns (mnemonic, jump_target or None)."""
    if w == 0:
        return "ZERO", None

    # MON N — top 8 bits = 0xD6
    if (w & 0xFF00) == 0xD600:
        n = w & 0xFF
        ann = MON_NAMES.get(n)
        if ann:
            return f"MON 0o{n:o}  ({ann})", None
        return f"MON 0o{n:o}", None

    # IOX — 0o164000..0o167777 (top 5 bits = 11101)
    # NB: mask is 0o174000 not 0o170000 — IOX bit-11 is set.
    if (w & 0o174000) == 0o164000:
        return f"IOX 0o{w & 0o3777:o}", None

    # Byte instructions (specific opcodes)
    bm = decode_byte(w)
    if bm:
        return bm, None

    top5 = w & 0o174000

    # Conditional jumps (10110X family)
    if top5 == 0o130000:
        cc = w & 0o3400
        disp = signed8(w & 0xFF)
        op = JCC_OPS.get(top5 | cc, f"JCC?0o{cc:o}")
        target = (pc + disp) & 0xFFFF
        return f"{op} L{target:o}", target

    # Memory-reference (and JMP/JPL)
    if top5 in MEM_OPS:
        op = MEM_OPS[top5]
        eatxt, target = decode_ea(w, pc)
        return f"{op} {eatxt}", target

    # Argument instructions
    top8 = w & 0o177400
    if top8 in ARG_OPS:
        arg = signed8(w & 0o377)
        return f"{ARG_OPS[top8]} 0o{arg & 0o377:o}", None

    # Shift instructions
    sh = decode_shift(w)
    if sh:
        return sh, None

    # Privileged / system control / WAIT
    # WAIT N — 0o151000..0o151377
    if (w & 0o177400) == 0o151000:
        return f"WAIT 0o{w & 0o377:o}", None
    priv = decode_priv(w)
    if priv:
        return priv, None

    # Bit instructions
    bi = decode_bit(w)
    if bi:
        return bi, None

    # Skip family (before reg-op fallback)
    skp = maybe_skp(w)
    if skp:
        return skp, None

    # Register-ops fall-back
    if (w & 0o170000) == 0o140000:
        return decode_reg_op(w), None

    return f".WORD 0o{w:06o}", None


# =========================================================================
# Disassembly infrastructure
# =========================================================================

class Program:
    def __init__(self, data: bytes, base_offset: int = PROG_HEADER_BYTES):
        self.data = data
        self.base = base_offset
        hdr = parse_prog_header(data) if base_offset == PROG_HEADER_BYTES else {}
        self.end_addr = hdr.get("end_addr", (len(data) - base_offset) // 2)
        self.header = hdr

    def word(self, addr: int) -> int | None:
        off = self.base + addr * 2
        if off + 1 >= len(self.data):
            return None
        return (self.data[off] << 8) | self.data[off + 1]

    def words(self):
        for a in range(self.end_addr):
            yield a, self.word(a)


def disassemble(prog: Program, start: int = 0, end: int | None = None,
                symbols: dict[int, str] | None = None,
                code_only: set[int] | None = None) -> list[str]:
    if end is None:
        end = prog.end_addr
    symbols = dict(symbols or {})
    lines: list[str] = []
    target_set: set[int] = set()

    for a in range(start, end):
        w = prog.word(a)
        if w is None:
            continue
        if code_only is not None and a not in code_only:
            continue
        _, tgt = decode(w, a)
        if tgt is not None:
            target_set.add(tgt)

    for a in range(start, end):
        w = prog.word(a)
        if w is None:
            continue
        if code_only is not None and a not in code_only:
            continue
        sym = symbols.get(a, "")
        if a in target_set and not sym:
            sym = f"L{a:o}"
        mnem, tgt = decode(w, a)
        if tgt is not None and tgt in target_set:
            named = symbols.get(tgt, f"L{tgt:o}")
            mnem = mnem.replace(f"L{tgt:o}", named)
        chars = "".join(chr(b) if 32 <= b < 127 else "." for b in (w >> 8, w & 0xFF))
        label = f"{sym + ',':<12s}" if sym else " " * 12
        lines.append(f"0o{a:06o}  0x{w:04x}  {label}{mnem:<36s}  ; {chars}")
    return lines


def trace_reachable(prog: Program, entries: list[int],
                    reloc_targets: set[int] | None = None) -> set[int]:
    """Forward control-flow trace. If `reloc_targets` provided (from BRF parse),
    also seed the worklist with addresses these pointers point to."""
    code: set[int] = set()
    worklist = list(entries)
    if reloc_targets:
        worklist.extend(reloc_targets)
    while worklist:
        pc = worklist.pop()
        if pc < 0 or pc >= prog.end_addr or pc in code:
            continue
        w = prog.word(pc)
        if w is None:
            continue
        if _looks_like_text(prog, pc):
            continue
        code.add(pc)
        _follow(prog, pc, w, worklist)
    return code


def _looks_like_text(prog: Program, pc: int) -> bool:
    text = 0
    total = 0
    for k in range(pc, min(pc + 8, prog.end_addr)):
        w = prog.word(k)
        if w is None:
            break
        for b in (w >> 8, w & 0xFF):
            total += 1
            if 32 <= b < 127 or b in (0, 10, 13, 9):
                text += 1
    return total > 0 and text / total > 0.85


def _follow(prog: Program, pc: int, w: int, worklist: list[int]) -> None:
    if w == 0:
        return
    if (w & 0xFF00) == 0xD600:
        n = w & 0xFF
        if n != 0:
            worklist.append(pc + 1)
            worklist.append(pc + 2)
        return
    if w == 0o146142:  # EXIT
        return
    top5 = w & 0o174000
    mode = w & 0o3400
    disp = signed8(w & 0xFF)
    if top5 == 0o124000:
        if mode == 0o0000:
            worklist.append((pc + disp) & 0xFFFF)
        elif mode == 0o1000:
            ptr = (pc + disp) & 0xFFFF
            v = prog.word(ptr)
            if v is not None:
                worklist.append(v)
        return
    if top5 == 0o134000:
        if mode == 0o0000:
            worklist.append((pc + disp) & 0xFFFF)
        elif mode == 0o1000:
            ptr = (pc + disp) & 0xFFFF
            v = prog.word(ptr)
            if v is not None:
                worklist.append(v)
        worklist.append(pc + 1)
        return
    if top5 == 0o130000:
        worklist.append((pc + disp) & 0xFFFF)
        worklist.append(pc + 1)
        return
    worklist.append(pc + 1)


# =========================================================================
# CLI
# =========================================================================

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", type=Path)
    p.add_argument("--base", type=lambda s: int(s, 0), default=PROG_HEADER_BYTES)
    p.add_argument("--start", type=lambda s: int(s, 0), default=0)
    p.add_argument("--end", type=lambda s: int(s, 0), default=None)
    p.add_argument("--trace", type=lambda s: int(s, 0), action="append", default=None)
    p.add_argument("--header", action="store_true")
    p.add_argument("--sym", type=Path, default=None)
    p.add_argument("--brf", type=Path, default=None,
                   help="matching :BRF file — seeds trace with LR addresses (relocations)")
    args = p.parse_args()

    data = args.file.read_bytes()
    prog = Program(data, args.base)

    if args.header:
        print(f"File: {args.file}")
        print(f"Size: {len(data)} bytes")
        for k, v in prog.header.items():
            print(f"  {k}: {v!r}")
        print(f"  base_offset: 0x{args.base:x}")
        print(f"  memory_size: {prog.end_addr} words")
        return

    symbols: dict[int, str] = {}
    if args.sym:
        for line in args.sym.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                try:
                    symbols[int(parts[0], 0)] = parts[1]
                except ValueError:
                    pass

    reloc_targets = None
    if args.brf:
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            import nd100_brf
            brf = nd100_brf.parse_brf(args.brf.read_bytes())
            reloc_addrs = nd100_brf.relocated_addresses(brf)
            # Seed trace with the VALUES at those addresses (they're function pointers)
            reloc_targets = set()
            for a in reloc_addrs:
                v = prog.word(a)
                if v is not None and 0 <= v < prog.end_addr:
                    reloc_targets.add(v)
                # Also include the slot's address as a candidate code start
                symbols.setdefault(a, f"PTR_{a:o}")
            print(f"; BRF: {len(reloc_addrs)} relocated slots, "
                  f"{len(reloc_targets)} unique pointer values", file=sys.stderr)
        except Exception as e:
            print(f"; BRF load failed: {e}", file=sys.stderr)

    code_only = None
    if args.trace or reloc_targets:
        entries = (args.trace or []) + list(reloc_targets or [])
        code_only = trace_reachable(prog, entries, reloc_targets)
        print(f"; trace-reachable: {len(code_only)} of {prog.end_addr} words "
              f"({len(code_only) * 100 // max(1, prog.end_addr)}%)", file=sys.stderr)

    for line in disassemble(prog, args.start, args.end, symbols, code_only):
        print(line)


if __name__ == "__main__":
    main()
