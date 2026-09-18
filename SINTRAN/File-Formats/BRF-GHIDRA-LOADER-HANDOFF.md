# Handoff: Building a Ghidra Loader for ND BRF Files

**Purpose:** everything another LLM/engineer needs to build a Ghidra `Loader`
that ingests a Norsk Data **BRF** (Binary Relocatable Format) object file and
produces a Ghidra program with correct memory layout, symbols, entry points and
relocations for ND-100 code.

**Status, corrected 2026-09-18: THE LOADER HAS BEEN BUILT.** This handoff was written
on 2026-07-07, when no Ghidra loader existed. One was written the next day: the sibling
repository `ghidra-nd100` has `ND-100/src/main/java/nd/bpun/BRFLoader.java` (1171 lines,
commit `c5983bc`, "BRFLoader: add ND-100 BRF (Binary Relocatable Format) import support"),
beside its BPUN and `:PROG` loaders, with its own handoff `HANDOFF-BRF-LOADER.md` dated
2026-07-08 in that repository's root. Read that handoff for the state of the loader.
NOT CHECKED here: whether the loader passes the checklist in section 5 below - the file
and its commit were looked at, the loader was not run.

The rest of this document is kept as the specification the loader was built from, and as
the record of the format rules that cost debugging time.

**Status as written 2026-07-07:** No Ghidra loader exists yet. What DOES exist is a validated
**Python reference implementation** (a BRF linker that emulates the ND Relocating
Loader). Its logic is the authoritative spec for the Ghidra loader - port it.
Both the format doc and the reference code are reproduced below so this file is
self-contained.

---

## 1. Background you need

- **What BRF is:** the relocatable object format emitted by every ND language
  processor (MAC assembler, FORTRAN, COBOL, PLANC, BASIC, PASCAL, NPL, C) and
  consumed by the ND Relocating Loader. It is a byte stream of "BRF groups", each
  led by a one-byte control number. See the full spec:
  `SINTRAN/File-Formats/BRF-FILE-FORMAT.md`
  (primary manual: `Reference-Manuals\ND-60.066.04 ND Relocating Loader.md` ch.2).

- **Target CPU:** ND-100, 16-bit word machine (NOT byte-addressed). Ghidra needs
  an ND-100 SLEIGH processor module - the repo's `nd100-ghidra` skill implies one
  exists in this environment. Word address N in BRF = Ghidra address N in a
  word-addressed language, or N*2 if you model it byte-addressed. Decide this
  first; the reference linker below works in WORD addresses (1 slot = 1 16-bit word).

- **Sample BRF files to test against:**
  `Installation/Communication/Ethernet/x/encos-err-i-b01.brf`
  `Installation/Communication/Ethernet/x/encos-err-ii-b01.brf`
  Each: 174 BRF units, all checksums valid, PLANC compiler output. The ND-100-side
  ENNS0 COSMOS Ethernet supervisor. Symbols include MAIN `ENNS0`, ENTR `POSUERR`,
  `SEGLOAD`, `READPIO`, `START_P`, plus LIBR/ENTR `UEIE*` pairs.

---

## 2. BRF format essentials (what the loader must decode)

Byte stream of groups. Each group = `<control byte>` then optional S-group and/or
P-groups:

- **Control byte** (1 byte): a control number 0-54 octal (loader command).
- **P-group** (2 bytes): one 16-bit word, BIG-ENDIAN (MSB first). VERIFIED - the
  END checksum only validates with big-endian word assembly.
- **S-group** (4 bytes, or 6 after LONGF): a symbol of 1-7 chars in six-bit code,
  right-justified, space(0) padded. Six-bit code = ASCII minus 40 octal
  (0=space, 1-32 octal = A-Z, 60-71 octal = 0-9). Bytes consumed MSB-first.

**Key structural rules (each cost real debugging - honor them):**
1. Big-endian P-groups.
2. Checksum after every END (21 octal) = one's complement of the 16-bit sum of
   everything from the BEG control byte through the END control byte (control
   bytes as 8-bit, P-groups as 16-bit, S-groups as 2/3 16-bit words).
3. `LONGF` (32 octal) = 6-byte S-groups. It is **per-unit**: every `BEG` (17 octal)
   resets S-group size back to 4 bytes; a unit must repeat LONGF for 6-byte symbols.
4. Sixbit = ASCII-40 octal, space padded, MSB-first packing.
5. Zero bytes (FEED, control 0) pad between units; a single EOF (23 octal) byte
   terminates the file.

**REF semantics (NOT documented in ND-60.066.04 - discovered empirically):**
Control number 20 octal (REF) emits its OWN placeholder word at CLC (a link-chain
node); it does NOT patch the previous word. Back-to-back REF groups occur (PLANC
routine headers reference 5ENTR/5ERET/5LEAV consecutively). In the reference
linker this is `ref_mode="self"` - use that mode, not "prev".

### Control-number table (octal ctrl -> mnemonic, P-group count, has-S-group)

The reference linker's `CTRL`, `NW`, `HAS_S` dicts encode this. Semantics of the
ones the linker acts on (CLC=current location counter, PB=program base, all word
addresses):

| Oct | Mnem | Action |
|-----|------|--------|
| 0   | FEED | nothing (padding) |
| 1   | LF   | store W1 at CLC; CLC++ |
| 2   | LR   | store W1+PB at CLC; CLC++ (relocated word) |
| 3   | LC   | store W1+CDB at CLC; CLC++ (COMMON-relative; CDB=0 in samples) |
| 4-7 | AFF/ARF/AFR/ARR | fix-up already-loaded word (add, with/without PB reloc on addr and content) |
| 10  | SFL  | CLC = W1 (set load address) |
| 11  | AFL  | fill W1 zero words from CLC; CLC += W1 |
| 12  | SRL  | CLC = W1+PB |
| 14  | MAIN | S-group symbol = main entry, value = CLC |
| 15  | LIBR | library entry point (conditional load; linker loads everything) |
| 16  | ENTR | S-group symbol = entry point, value = CLC |
| 17  | BEG  | PB = CLC; first byte of a unit; resets LONGF |
| 20  | REF  | external reference; emits a link-chain placeholder word at CLC (see REF semantics) |
| 21  | END  | 1 P-group = checksum |
| 23  | EOF  | end of file |
| 24  | LNF  | "load N fast": W1 = word count, then W1 words stored at CLC.. |
| 26  | ASF  | S-group = COMMON block name, W = length |
| 27  | ADS  | S-group value added to word at CLC-1 |
| 30  | (X30)| UNDOCUMENTED, seen in real files: like LNF (count word + ASCII payload); PLANC id stamp e.g. "PLANC-1BANK-G00 " |
| 32  | LONGF| flags 6-byte S-groups (this unit only) |
| 34-37 | INL/DBL/RLL/CXL | integer/double/real/complex load at W1+PB |
| 44  | BYL  | byte load |
| 46  | NWL  | line number (ignored) |
| 47  | DBG  | debug on/off |
| 50/51 | PMO/DMO | program/data bank mode (two-bank) |
| 52/53 | LRP/LRD | LR against program/data bank base |
| 54  | DIC  | dictionary table (5 words/entry, -1 terminated) |

The samples use only: FEED, LR, REF, LNF, AFR, LF, ENTR, LIBR, BEG, END, LONGF,
AFL, SRL, MAIN, LC, EOF, plus one X30. Other opcodes' word counts rest on the
manual only - implement from the table but they're untested on real data.

---

## 3. What the Ghidra Loader should emit

A Ghidra `Loader` (extend `ghidra.app.util.opinion.AbstractProgramWrapperLoader`
or `AbstractLibrarySupportLoader`) does roughly:

1. **`findSupportedLoadSpecs`**: sniff the file - a valid BRF starts with control
   byte 17 octal (BEG) possibly after FEED padding, and every unit ends END+checksum.
   Offer a LoadSpec bound to the ND-100 language/compilerSpec.

2. **`load`**: run the BRF link algorithm (port `Linker` below):
   - Choose a load base (word address). Real loader uses a system-defined start;
     for RE, base 0 is fine, or make it a loader option.
   - Walk BRF groups, building an in-memory image (`mem[]`), a symbol table
     (ENTR/MAIN/LIBR -> address), and a REF list.
   - Create ONE (or per-unit) initialized memory block from `mem[]`. Because
     ND-100 is word-addressed, either use a word-addressed AddressSpace (preferred
     if the ND-100 SLEIGH defines one) or write each 16-bit word as 2 bytes at
     addr*2 in a byte space, and be consistent everywhere.
   - **Symbols**: for each `(addr, name, kind)` in entries, `createLabel` /
     `createFunction`. MAIN -> set as entry point (`markAsFunction` + add to
     symbol table as the program entry).
   - **Relocations/REFs**: resolve in-file symbols by walking the REF link chains
     against the ENTR definitions (see `resolve()` below); for the 5 unresolved
     PLANC runtime externals (5INIT/5ENTR/5ERET/5LEAV/5QUIT) create external
     symbols or thunks and record a Ghidra relocation entry so they're visible.
   - Record a Ghidra Relocation for each patched site (nice-to-have; lets Ghidra
     show what was relocated).

3. **Entry point**: the MAIN symbol's address (in the samples, `ENNS0`).

**Unresolved externals in the samples (expected, not an error):**
`5INIT`, `5ENTR`, `5ERET`, `5LEAV`, `5QUIT` = PLANC runtime stack routines, in the
external PLANC runtime library. Conventional addresses from
`Reference-Manuals\ND-60.051.8 EN SINTRAN III - Real Time Loader.md`:
5INIT=34012, 5ENTR=34207, 5LEAV=34243 octal. 94 of 99 referenced symbols resolve
within each file; only these 5 are external.

---

## 4. Reference implementation (PORT THIS to Java for Ghidra)

### 4a. BRF linker (emulates the ND Relocating Loader) - the authoritative semantics

```python
# BRF linker: emulates the ND Relocating Loader to produce an absolute image.
# Based on ND-60.066.04 chapter 2 semantics. Works in WORD addresses (1 slot = 16-bit word).
CTRL = {
    0o0:"FEED",0o1:"LF",0o2:"LR",0o3:"LC",0o4:"AFF",0o5:"ARF",0o6:"AFR",0o7:"ARR",
    0o10:"SFL",0o11:"AFL",0o12:"SRL",0o14:"MAIN",0o15:"LIBR",0o16:"ENTR",0o17:"BEG",
    0o20:"REF",0o21:"END",0o22:"INHB",0o23:"EOF",0o24:"LNF",0o25:"RT",0o26:"ASF",
    0o27:"ADS",0o30:"X30",0o32:"LONGF",0o34:"INL",0o35:"DBL",0o36:"RLL",0o37:"CXL",
    0o44:"BYL",0o46:"NWL",0o47:"DBG",0o50:"PMO",0o51:"DMO",0o52:"LRP",0o53:"LRD",
}
NW = {"FEED":0,"LF":1,"LR":1,"LC":1,"AFF":2,"ARF":2,"AFR":2,"ARR":2,"SFL":1,"AFL":1,
      "SRL":1,"MAIN":0,"LIBR":0,"ENTR":0,"BEG":0,"REF":0,"END":1,"INHB":0,"EOF":0,
      "RT":1,"ASF":1,"ADS":0,"LONGF":0,"INL":2,"DBL":3,"RLL":4,"CXL":7,"BYL":2,
      "NWL":1,"DBG":0,"PMO":0,"DMO":0,"LRP":1,"LRD":1}
HAS_S = {"MAIN","LIBR","ENTR","REF","ASF","ADS"}
SIXBIT = " ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"

def sym6(b):
    v=0; n=0; out=[]
    for x in b:
        v=(v<<8)|x; n+=8
        while n>=6:
            n-=6; out.append(SIXBIT[(v>>n)&0x3F])
    return "".join(out).strip()

class Linker:
    def __init__(self, base=0, ref_mode="self"):   # USE ref_mode="self"
        self.mem = [0]*65536
        self.written = [False]*65536
        self.clc = base
        self.pb = base
        self.base = base
        self.syms = {}       # name -> address (ENTR/MAIN)
        self.refs = []       # (site, name, addend)
        self.ref_mode = ref_mode  # "self": REF loads its own placeholder word at CLC
        self.entries = []    # (addr, name, kind)

    def store(self, addr, val):
        self.mem[addr & 0xFFFF] = val & 0xFFFF
        self.written[addr & 0xFFFF] = True

    def load(self, data):
        i = 0; longf = False
        while i < len(data):
            cb = data[i]; name = CTRL[cb]; i += 1
            s = None
            if name in HAS_S:
                sl = 6 if longf else 4
                s = sym6(data[i:i+sl]); i += sl
            if name == "LNF":
                w1 = (data[i]<<8)|data[i+1]; i += 2
                for k in range(w1):
                    self.store(self.clc, (data[i]<<8)|data[i+1]); i += 2; self.clc += 1
                continue
            if name == "X30":                       # undocumented; skip payload
                w1 = (data[i]<<8)|data[i+1]; i += 2 + 2*w1
                continue
            ws = []
            for k in range(NW[name]):
                ws.append((data[i]<<8)|data[i+1]); i += 2
            if name == "FEED": pass
            elif name == "BEG": self.pb = self.clc; longf = False   # LONGF is per-unit
            elif name == "LONGF": longf = True
            elif name == "LF": self.store(self.clc, ws[0]); self.clc += 1
            elif name == "LR": self.store(self.clc, ws[0] + self.pb); self.clc += 1
            elif name == "LC": self.store(self.clc, ws[0]); self.clc += 1  # CDB=0
            elif name == "AFL":
                for k in range(ws[0]): self.store(self.clc + k, 0)
                self.clc += ws[0]
            elif name == "SFL": self.clc = ws[0]
            elif name == "SRL": self.clc = ws[0] + self.pb
            elif name == "AFF": self.store(ws[1], self.mem[ws[1]] + ws[0])
            elif name == "ARF": self.store(ws[1], self.mem[ws[1]] + ws[0] + self.pb)
            elif name == "AFR":
                a = (ws[1] + self.pb) & 0xFFFF; self.store(a, self.mem[a] + ws[0])
            elif name == "ARR":
                a = (ws[1] + self.pb) & 0xFFFF; self.store(a, self.mem[a] + ws[0] + self.pb)
            elif name == "INL": self.store((ws[0] + self.pb) & 0xFFFF, ws[1])
            elif name in ("MAIN","ENTR"):
                self.syms[s] = self.clc; self.entries.append((self.clc, s, name))
            elif name == "LIBR": pass                # always "load"
            elif name == "REF":
                if self.ref_mode == "prev":
                    self.refs.append((self.clc - 1, s, self.mem[self.clc - 1]))
                else:                                # "self" = correct for real files
                    self.refs.append((self.clc, s, 0)); self.store(self.clc, 0); self.clc += 1
            elif name in ("END","INHB","RT","DBG","NWL","PMO","DMO"): pass
            elif name == "EOF": break
            else: raise Exception("unhandled " + name)

    def resolve(self):
        unresolved = {}
        for site, nm, addend in self.refs:
            if nm in self.syms:
                self.store(site, self.syms[nm] + addend)
            else:
                unresolved.setdefault(nm, []).append(site)
        return unresolved   # {symbol: [sites]} - the external references
```

### 4b. Checksum validator (for the sniffer / integrity check)

Sum control bytes (8-bit) + P-groups (16-bit) + S-group words from BEG through
END; stored checksum = one's complement of that 16-bit sum. Verified against 348
units across the two sample files.

### 4c. Minimal ND-100 disassembler (optional - Ghidra's SLEIGH does this properly)

Only needed if you want a sanity disassembly outside Ghidra. Ghidra's ND-100
processor module is the real disassembler. (The Python `nd100_dis.py` from the
session covers memory-ref ops, cond jumps, MON/IOX/WAIT, TRA/TRR family, and marks
reg-op/shift/bit families - adequate for spot-checks, not a full model.)

---

## 5. Validation checklist for the Ghidra loader

Run against `encos-err-i-b01.brf`:
- Parses to the final EOF with no unknown control bytes: **174 units**.
- All **174 checksums** pass.
- Symbol table includes MAIN `ENNS0` and ENTR `POSUERR`, `READPIO`, `SEGLOAD`,
  `START_P`, `STOP_PI`, `RES_SLO`, `REL_SLO`, `SEND_KI`, `REC_KIC`, `INT2GET`.
- Exactly **5 unresolved externals**: 5INIT, 5ENTR, 5ERET, 5LEAV, 5QUIT.
- Entry point = `ENNS0`.
- Strings visible after load (in LNF blocks): "Undefined MON PIOC error.",
  "Check if RTCOMMON is in interface memory.", "COSMOS Ethernet ...".

If those all hold, the loader is faithful to the ND Relocating Loader.

---

## 6. Gotchas that cost real debugging (do not rediscover)

1. **REF emits its own word** (`ref_mode="self"`). Using "prev" (patch previous
   word) desynchronizes on back-to-back REFs and corrupts the image.
2. **LONGF is per-unit**; reset to 4-byte S-groups at every BEG. Files mix LONGF
   and non-LONGF units - parsing only stays in sync (all checksums pass) with the reset.
3. **P-groups big-endian**; checksums fail otherwise.
4. **Control 30 octal** appears in real files though the manual says "not used" -
   treat like LNF (count word + payload) and skip, or surface as a comment.
5. ND-100 is **word-addressed**; keep the whole pipeline in word units or apply a
   consistent *2 everywhere. Mixing the two is the classic ND emulation bug.

---

**Provenance:** created 2026-07-07 during ENCOS Ethernet-II reverse engineering.
Python reference tools live (temporarily) in the session scratchpad
(`brf_link.py`, `brf_parse.py`, `nd100_dis.py`, `analyze_encos.py`); their exact
logic is reproduced above so this handoff is self-contained. (Added 2026-09-18: the
scratchpad is gone. A later BRF linker written to the same format document is kept in this
repository at `SINTRAN/XMSG/DOC/COSMOS-RE/ENNS0-Startup-RE-2026-07-23/tools/brf_link.py`;
it is a different file from the one reproduced above, not a copy of it.) Format spec:
`SINTRAN\File-Formats\BRF-FILE-FORMAT.md`.
