# ND-5000 Family / Models — Reference & Emulation Cross-Check

> **Read PART 2 (section 5 onward) too — added 2026-08-24.** Part 1 below is graded
> [DOC-wiki] throughout because it came from a community wiki. Part 2 checks all of it
> against the actual ND manuals in this repo and **corrects or extends Part 1 in several
> places**: the CPU-type definition, a CPU MODEL 9 the wiki does not have, the real
> microprogram version scheme, the full list of the 25 '87 extension instructions, the
> ND-5950 (multi-CPU Rallar), and two spots where ND's own manuals contradict each other.
> Where Part 1 and Part 2 disagree, **Part 2 wins** — it cites a printed manual.
>
> **PART 3 (section 15 onward)** covers performance and dating: the fact that the famous
> **28 MIPS is a four-CPU aggregate, not a processor rating**, the **only measured benchmark**
> in any ND document (6553 dhrystones/second, about 3.7 DMIPS per CPU), the relative
> performance ladders, and what dates the ND-5900 can actually be pinned to.
>
> **PART 4 (section 21 onward)** answers "which microcode do we actually run": **`MICRO-5800-B30`
> is a SAMSON image** (ND-5800, type 3 / model 8), there is **no Rallar microcode in the
> corpus at all**, and the **version constant in microword 1 is the manual's version number
> read as DECIMAL** — which closes the open item in section 2.1 and **corrects section 1.6's
> claim that the version is the same across models.**
>
> **PART 5 (section 25 onward)** defines **work mode / generation** (WM406 = A, WM500 = B):
> it is a **generation of a SINTRAN III version**, not a version of its own, and the reason
> two microprograms exist per model is that **an ND-5000 could run under either generation
> 406 or 500**. It also brings a **third independent confirmation** of the version scheme,
> and a terminology trap where "500" means three different things.
>
> **PART 6 (section 30 onward)** sweeps SINTRAN J..N: work mode does not exist in J, the
> three-digit numbering is K-only, and **generation 406 died with the K-version**. Also:
> **what A actually differs from B** — the B microcode carries the multiprocessor NUCLEUS and
> the A microcode traps those instructions as illegal.
>
> **PARTS 7-9 (section 35 onward)** are from the norsk-data.com archive mirror:
> **Rallar is "N-5000 Basic CPU IV"** with its own PCB series; **KUSK, GAMP and a third chip
> DSB are CONFIRMED**; ND's **"MIPS" means WHETSTONE MIPS** (this **corrects Part 3**); the
> ND-5000 was **announced 27 January 1987**; and we already hold an unread **1983 SAMSON design
> spec** that confirms the 16K x 128-bit control store and describes the octobus control path.

**Date compiled:** 2026-07-18 (Part 1), 2026-08-24 (Parts 2-9)
**Primary source:** community wiki summary of the ND-5000 family (grade **[DOC-wiki]** —
secondary/community, NOT byte-verified), itself citing:
- ND-05.009.3 NORD-500 REFERENCE MANUAL
- ND-05.020.1 ND-5000 Hardware Description
- ND-05.017.01 ND-5000 Hardware Maintenance
- PRODUCT NEWS November 1987

**Purpose:** capture the family/model structure and — importantly — flag where it
CROSS-CONFIRMS or reconciles with our independently CARVED findings ([V]/[NPL-V]) in the
octobus/microcode/servicer work. Grades: **[V]** carve-verified by us; **[DOC-wiki]** from
this secondary source; **[D]** our inference; **[?]** open/unreconciled.

---

## 1. What matters for the emulation (the high-value cross-confirmations)

### 1.1 "Samson" = the ND-5000 CPU; "Delilah" = the ND-120 I/O side  [DOC-wiki, matches our usage]
The ND-5000 uses an ND-100/110/120 CPU as its I/O processor. The ND-5000 CPU line is named
**Samson** (sold as ND-5200/5400/5500/5700/5800); the ND-120 I/O-side line is named
**Delilah**. A separate later processor, **Rallar** (ND-5830/5850), is two VLSI gate arrays
**KUSK** ("jockey") + **GAMP** ("horse").
- CONNECTION: we have been calling the 5000 CPU path "SAMSON" throughout the servicer work
  (OnStartProcessSamson, Samson5800 generation, `MICRO-5800-B30`). This pins that name to
  the official hardware name. Rallar (5830/5850) is a DIFFERENT processor from Samson — our
  microcode/servicer work targets Samson (ND-5800/B30), NOT Rallar. [D: Rallar likely needs
  its own microcode; out of current scope.] **CONFIRMED 2026-08-24 — Rallar does have its own
  microcode, product 211847, files `MICRO-5830-12010:DATA` / `MICRO-5850-12010:DATA`, a
  separate 120xx version series. There is also an ND-5950 (multi-CPU Rallar) the wiki misses.
  See PART 2 section 9. KUSK and GAMP remain unconfirmed — they appear in NO manual here.**

### 1.2 The four ND-5000 CPUs are octobus stations 70B–73B  [DOC-wiki CONFIRMS carve [NPL-V]]
The ND-5900 (multi-CPU) assigns:
- ND-5000 CPU 1 -> octobus station "708"  = octal **70B**
- ND-5000 CPU 2 -> "718" = **71B**
- ND-5000 CPU 3 -> "728" = **72B**
- ND-5000 CPU 4 -> "738" = **73B**

The trailing "8" is a rendering artifact of the octal subscript (70₈ = 70B) [D — but the
increment-by-10-octal pattern and the range make this unambiguous]. This EXACTLY matches
our carved **`FN5DEST=070B` / `LN5DEST=073B`** (stations 070–073, `CARVE-ANSWER-ND5000-
ACTIVATION-WORKFLAG.md` [NPL-V]) and the "up to 4 CPUs" multi-CPU threading requirement.
- CONNECTION: independent official-doc confirmation that (a) the max is 4 CPUs and (b) the
  station range is exactly 70B–73B. Our GIVEINT-needs-5OMDNO>=8-to-reach-station-1 finding
  and the fabric station addressing are consistent with this range.
- ORIGINAL MANUAL CITATIONS (added; read directly from the manual text):
  - `../../Reference-Manuals/ND-830083-1-EN Performance Monitoring, Tuning and Capacity Planning.md`,
    section "Multi-CPU", line 1297: "Norsk Data also delivers computer systems with up to four
    ND-500(0) CPUs. These systems always have a single ND-100 CPU controlling the ND-500(0) CPUs."
  - `../../Reference-Manuals/500/ND-05.017.01 EN ND-5000 HARDWARE MAINTENANCE.md`, section 2.1.5
    "Upgrading from ND-5800 to ND-5900/2/3/4 System", line 2170: insert 1, 2 or 3 extra ND-5000
    CPUs (type 3); CPU 1 to 4 are octobus stations 70B, 71B, 72B, 73B. The system table at line 2049
    lists ND-5900 Model 2, 3 and 4.
  - Neither manual states in so many words that a fifth CPU is impossible; four is the most they
    say Norsk Data delivers.

### 1.3 CPU MODEL (2/4/5/7/8) is DISTINCT from the SINTRAN 5CPUTYPE  [DOC-wiki + our carve]
Two different identifiers — do not conflate:
- **`5CPUTYPE`** (SINTRAN, 3-bit field, our skill/carve): OLD500=1, **SAMSON=3**. This is the
  GENERATION the driver detects (CH5CPUPRESENT / READ-CPU-TYPE 170B GETCP / CPUAVAILABLE).
- **CPU MODEL** (MF-backplane EEPROM, this doc): **2/4/5/7/8** = ND-5200/5400/5500/5700/5800.
  A FINER designation WITHIN Samson, set by the MF-bus updating tool (`SET-CPU-MODEL`), read
  via the MF-bus maintenance `LIST-CONFIGURATION` (NOT a SINTRAN 5CPUTYPE read). All five
  models report `5CPUTYPE=3` (Samson) to SINTRAN. [D: the model number is an MF-bus/ACCP
  concern, invisible to the 5MPM mailbox path — so it does NOT affect the servicer.]

### 1.4 Model / CPU-type / microprogram / clock table  [DOC-wiki]
| Model | CPU MODEL # | CPU type | Master clock | Microprogram ver | Caches enabled |
|---|---|---|---|---|---|
| ND-5200 | 2 | 1 | 70 ns | (base) | none |
| ND-5400 | 4 | 2 | 156 ns | 144xx | I-cache, Smart-IfGo |
| ND-5500 | 5 | 2 | 156 ns | 145xx | + D-cache |
| ND-5700 | 7 | 2 | 70 ns  | 147xx | + Address-cache |
| ND-5800 | 8 | 3 | 70 ns  | 148xx | + WICO (write-in-cache-only) |

- **CPU types 1/2/3** = 2/3/4 card layers. Type 1 lacks the instruction/data-cache layer
  AND the **AAP** (Additional Arithmetic Processor) -> on type 1 **floating point is done by
  the microprogram** [DOC-wiki]. RELEVANCE: if FP is ever emulated on a type-1 (ND-5200)
  Samson, it runs through microcode, not an AAP.
- Master clock jumpered Slow (156 ns) / Normal (70 ns); performance = CPU type × clock ×
  cache-feature enables. No mailbox/servicer relevance — timing is not modeled (protocol is
  flag-driven, not delay-driven), but noted for the live-oracle timing discussions.

### 1.5 '87 extensions — 25 new instructions  [DOC-wiki]
The ND-5000 CPU runs the same instruction set as the ND-500 CPU PLUS **25 new instructions**
("'87 extensions"), also present in the ND-500/1 and ND-500/2 CPUs.
- RELEVANCE to `CpuND500`: a full fetch/execute Samson bring-up (octobus Phase-3 next tier)
  may encounter these 25 opcodes; they are NOT in the base ND-500 instruction set.
  **[?] CLOSED 2026-08-24 — the full list of all 25 is in PART 2 section 10 below**, from
  Appendix D of `Reference-Manuals\ND-05.009.4 EN ND-500 Reference Manual.md`.

---

## 1.6 HOW the CPU type/model is encoded and read — [V] microcode-image evidence (2026-07-18)

Source corpus: `E:\Dev\Ronny\ND5000UC\docs\MC\` (per-model microcode images + `.LABE`
symbol files + PROGRAM DESCRIPTION `.TEXT` files — the FULL set; the `microcode\*.md`
markdown are only exports of the 5800 image). manifest: 4 models (5200/5500/5700/5800) x
work modes (A=WM406, B=WM500, M) x revisions (27/29/30).

**FINDING [V by direct 4-image comparison]:** the CPU **type+model is baked into the
microcode image at control-store word `000007` (symbol `CPUMODEL`)**. Comparing word 7
(bytes 0x70-0x7F) across `MIC-52/55/57/58 00-90-500.DATA`, all bytes are IDENTICAL except
the last, which decodes as a packed byte **`(CPU_type << 4) | model_digit`**:

| Image | word7 last byte | CPU type (hi nibble) | model digit (lo nibble) |
|---|---|---|---|
| 5200 | 0x12 | 1 | 2 |
| 5500 | 0x25 | 2 | 5 |
| 5700 | 0x27 | 2 | 7 |
| 5800 | 0x38 | 3 | 8 |

Exact match to the wiki type column (1/2/2/3) AND model numbers (2/5/7/8). The
`MICRO-5800-B30.DATA` we exported carries 0x38 (type 3, model 8) = confirmed genuine 5800.

**The read chain [V symbol addresses, `MICRO-5800-B30.LABE`]:**
- `CPUMODEL` = word `000007` (the packed type/model byte in the LARG field).
- `CPU_READ` @`017130` reads `CPUMODEL` and indexes the `CPU_MODEL00-17` table
  (`017143-017162`, 16 entries; values `000101/001240/001041/001001/001000/000001...` per
  the INIT-SAMSON decode) to compose **CPUPAR** -> SRF `0o2015` (exact mask/index [D]).
- CPUPAR is returned to the ND-100 in the `3RMICV` mailbox reply (msg HW `0o10`) and
  surfaced through the cached CPU-DF that MON60 `170B READ-CPU-TYPE` reports.
- Version is a SEPARATE baked field: word 1 LARG = `0x2E9A` = `027232B` (same across
  models — tracks REVISION, not model).
  **WRONG — CORRECTED 2026-08-24, see PART 4 section 22.** Word 1 differs per model AND per
  work mode; it was only ever read from one image. Read `0x2E9A` as **DECIMAL 11930** = the
  manual's own version number (5800, WM500, rev 30), not as octal `027232B`.

**CORRECTION to §1.3's earlier phrasing:** the model number the MICROCODE reports to
SINTRAN comes from **word 7 of the loaded image**, NOT the MF-backplane EEPROM. The EEPROM
(`SET-CPU-MODEL`) is the MF-bus hardware's separate copy; an upgrade sets BOTH (new
microprogram floppy carries word 7 + the updating tool writes the EEPROM) — which is why
every wiki upgrade step pairs "exchange microprogram" with "set CPU model". EMULATION
consequence: the reported model follows whichever microcode image is loaded into the
control store (the emulator's `csStore`); to emulate a 5700 vs 5800, load that image (or
patch word 7). [?] whether the real loader ALSO patches word 7 from the EEPROM — not proven.

## 1.7 Directly-useful content in the PROGRAM DESCRIPTION texts  [DOC — 211276D]

`5800-30.TEXT` = the real ND-5800 Microprogram PROGRAM DESCRIPTION (Reg.no `211276D`,
rev 30, source `250291D`; A=WM406 / B=WM500, both SINGLE-CPU configs). Its changelog
documents fields we had flagged as unmodeled in the context-block work:
- **CED register:** changing it (when included in the register-block mask) could cause a
  PV-trap OR load wrong data to the rest of the register block — fixed rev 30. Relevant to
  `CED@0x5C` (R2-4 byte-mask) semantics.
- **PS register:** changing it "was not done in hardware" — fixed rev 30. Relevant to the
  `PS/PHS@0x48` context field we listed as NOT modeled.
- Built-in **RTC** (`ND-500-RTC-LIB`): `CLINT` (gen external interrupt), `CLRCLK` (reset
  RTC, must be privileged else Illegal Instruction Code), `RDCLK` (read 32-bit). Relevant
  to the octobus RTC-determinism work; "INIT-5000 routine to reset the clock counter"
  changelog.
- ALT-prefix string instructions, `Lregbl` fix, `Nksend`/`Nkmove` nucleus changes, kicklock
  timeout error code — microcode-behavior notes for the CPU/nucleus layers.

## 2. Open reconciliations / [?]

1. **Microprogram version numbering vs our extracted constant.** *(PART 2 section 8 adds the
   manual's actual scheme — `11`+model-index+revision, with a SEPARATE series per SINTRAN
   work mode, WM406 vs WM500. "144xx" still matches nothing.)* This doc gives ND-5800
   microprogram = **"148xx" (decimal)**. We extracted **`027232B` (octal)** = 0x2E9A =
   11930 decimal from microword 1 LARG of `MICRO-5800-B30.DATA`, and separately noted work
   modes A=406 / B=500. `027232B` does NOT obviously equal 148xx. UNRECONCILED [?] but now better bounded:
   the image-internal version (`027232B` @word1 LARG) tracks the REVISION (same across the
   5200/5500/5700/5800 word-7-differing images) and is DISTINCT from the model (word 7). The
   ND-5800 microprogram product/floppy is Reg.no `211276D` rev 30 (source `250291D`) per
   `5800-30.TEXT` — none of these equal "148xx" either. So "148xx" is likely a THIRD
   identifier (an earlier/marketing microprogram version or LOAD version), NOT the word-1
   constant and NOT the product number. Do NOT assume equality. (Classic-500 microprograms
   were 15211/15311/15111 per model — a different scheme again.)
2. **`LIST-CONFIGURATION` fields** (MF-bus maintenance): `STATION NO=0000708`, `POWER FAIL
   DESTINATION=1B`, `BROADCAST TYPE=0`, `SPEED=1B`, `CPU MODEL=7B`, `MASTER CONTROL
   REG=201B`. These are MF-bus/EEPROM slot-config fields, NOT 5MPM mailbox fields — no direct
   servicer mapping. `MASTER CONTROL REG=201B` and `SPEED=1B` recorded verbatim; meaning not
   independently verified [?].
3. **Updating tool destroys CPU model** if `INITIATE-EEPROM`/`CONFIGURATE-SLOT` used on the
   MF-controller/CPU slot — pure hardware-maintenance hazard, no emulation relevance beyond
   noting the model lives in nonvolatile MF-backplane memory (an emulator would seed it, not
   compute it).

---

## 3. What this does NOT change

- **The 5MPM mailbox / servicer model is unaffected.** CPU model (5200–5800), clock speed,
  cache enables, and the MF-backplane EEPROM are all BELOW / BESIDE the mailbox protocol.
  The servicer sees `5CPUTYPE=3` (Samson) and the message fields, not the model number.
- **Rallar (5830/5850) is out of scope** — different processor (KUSK/GAMP), likely different
  microcode; our Samson (5800/B30) work does not cover it.
- **NDIX (UNIX) coexistence** confirmed (5000 runs SINTRAN III AND NDIX) — consistent with
  the microcode's NDIX MON-call case that answers WITHOUT stopping (async MON). No new action.

---

## 4. Compact vs Large cabinet (background)  [DOC-wiki]
- **Compact series** (ND-5200/5700 Compact): ND-110/CX (ND-5200 Compact uses ND-110) or
  ND-120 I/O processor; internal disks; updating tool = **350156 "Double Bus Contr."**.
- **Large cabinet**: updating tool = **350157 "MF Bus Controller"**.
- Both hold the CPU model in MF-backplane nonvolatile memory. Emulation: seed the model per
  the configured machine; there is no runtime computation of it.

---

# PART 2 - MANUAL-VERIFIED MODEL DIFFERENCES (added 2026-08-24)

Everything above was graded **[DOC-wiki]** because it came from a community wiki summary.
This part reads the actual ND manuals in `E:\Dev\Ronny\NDInsight\Reference-Manuals\500` and
`E:\Dev\Ronny\NDInsight\Reference-Manuals` and says what they confirm, what they add, and
where **ND's own manuals contradict each other**. Grade here is **[DOC-manual]** - printed in
an ND manual in this repo, with the file cited - which outranks [DOC-wiki] but is still not
byte-verified against hardware.

Sources for this part:
- `E:\Dev\Ronny\NDInsight\Reference-Manuals\500\ND-05.017.01 EN ND-5000 HARDWARE MAINTENANCE.md`
  (section 1.4 CPU Types with Figures 9/10/11 and part lists; Table 1 Compact config;
  Table 2 Large config; Table 8 model differences; the microprogram version tables)
- `E:\Dev\Ronny\NDInsight\Reference-Manuals\500\ND-05.020.01 EN ND-5000 Hardware Description.md`
  (Table 4 model differences; section 5.3.57 READ CPU MODEL)
- `E:\Dev\Ronny\NDInsight\Reference-Manuals\ND-05.009.4 EN ND-500 Reference Manual.md`
  (Appendix D, the 1987 extension instruction list)
- `E:\Dev\Ronny\NDInsight\Installation\Installation-Description\ND-895560-2-EN.md` (ES model list)
- `E:\Dev\Ronny\NDInsight\Installation\Installation-Description\ND-896058-2-EN.md` and
  `ND-896058-4-EN.md` (Rallar microprogram release notes)
- `E:\Dev\Ronny\NDInsight\Reference-Manuals\500\ND-830102.1B EN ND-5000 ES Model C Hardware Maint. Manual-Sintran.md`

---

## 5. CPU type is defined by CONTENT, not by layer count  [DOC-manual]

ND-05.020.01 section 5.3.57 states it directly:

| Type | Manual's definition | Layers | CPU part no. |
|---|---|---|---|
| 1 | **No cache, no AAP, no IDAC (booster)** | 2 | 320001 |
| 2 | **With cache and AAP** | 3 | 320002 |
| 3 | **With cache, AAP and IDAC (booster)** | 4 | 320003 |

The wiki's "layers of cards" count is right but says nothing about what the fourth layer is.
It is the **IDAC** - I-level Data Address Controller, the "data address booster", part
**324714**. ND-05.020.01 calls it "provided as **an option** for the ND-5800 and ND-5900
models", so a type-3 CPU does not automatically carry one.

### 5.1 Type 3 is NOT just type 2 plus a layer  [DOC-manual, corrects a natural wrong reading]

ND-05.017.01 section 1.4 baby-module part lists, compared:

| Module | Type 1 | Type 2 | Type 3 |
|---|---|---|---|
| MB mother board | 324602 | 324602 | **324603** (unique) |
| CACHE instruction/data cache | - | 324710 | **324717** (unique) |
| IDA instruction/data address controller | 324708 | 324708 | **324718** (unique) |
| IDAC "booster" | - | - | **324714** (only type 3) |
| AAP additional arithmetic processor | - | 324715 | 324715 |
| MMS / M5 memory management | 324701 | 324701 | 324701 |
| ALU arithmetic logical unit | 324704 | 324704 | 324704 |
| CS control store 16K | 324707 | 324707 | 324707 |
| MIC microinstruction controller | 324709 | 324709 | 324709 |
| **ACCP access processor** | **324702** | **324702** | **324702** |

Verbatim (ND-05.020.01, "DIFFERENCE BETWEEN THE CPU TYPES"): "CPU types 1 and 2 use the same
mother board and baby modules. On CPU type 1, the cache and AAP baby modules are removed. On
the ND-5200 CPU, floating-point operations are performed by the microprogram. On CPU type 3,
the mother board and the cache and IDA baby module are unique to this CPU type."

**Note for the ACCP work in this folder:** all three CPU types list the ACCP as part
**324702**. The card we have dumped
(`E:\Dev\Ronny\NDInsight\Installation\Communication\OctobusAccp\`) is **ND-324716**, which
supersedes 324702 - so a real type-1/2/3 board may carry either part. Do not assume the
dumped firmware is what a type-1 5200 shipped with. [?]

---

## 6. The ACCP returns type and model as ONE PACKED BYTE - and our microcode finding matches  [DOC-manual CONFIRMS carve [V]]

ND-05.020.01 section 5.3.57 **READ CPU MODEL**:

- Direct parameters: none. Memory parameters: none.
- **Messack parameters: CPU type (bits 7-4), CPU model (bits 3-0), one byte.**
- Messnak error codes: **11** = "MFbus controller has incorrect CPU setting",
  **12** = "Illegal CPU configuration".

This is EXACTLY the packed byte we measured independently in section 1.6 above at control
store word `000007` (`CPUMODEL`): 5200=`0x12`, 5500=`0x25`, 5700=`0x27`, 5800=`0x38`, i.e.
`(type << 4) | model`. Two derivations from different artifacts (a printed manual and four
real microcode images) agreeing on the same encoding.

**Emulation consequence:** an emulated ACCP answering READ CPU MODEL should return the same
byte the loaded control store carries at word 7, and should have error codes 11 and 12
available for the "wrong / illegal configuration" paths.

---

## 7. CPU MODEL 9 EXISTS - and the two manuals disagree about the ND-5900  [OPEN]

ND-05.020.01 section 5.3.57, verbatim: "CPU models are **2, 4, 5, 7, 8 or 9** for the CPUs
from the ND-5200, the ND-5400, and so on, up to the ND-5900."

ND-05.017.01 **Table 2** lists the ND-5900 as **CPU model 8**, the same as the ND-5800. The
wiki's upgrade procedure agrees with the maintenance manual ("set the CPU model to 8 for the
extra ND-5000 CPUs").

**Unresolved [OPEN].** Either the ND-5900 reports model 9 and the maintenance table is
simplifying, or model 9 was allocated and never used. Section 1.6 above gives a cheap way to
settle it: if an ND-5900 microcode image ever turns up, read word 7 and look at the low
nibble. **Do not hardcode either answer in the emulator until this is closed.**

---

## 8. Microprogram version numbering - the wiki's 144xx/145xx/147xx/148xx is NOT in any manual  [DOC-manual, CORRECTS wiki]

This closes part of the open item in section 2.1 above. ND-05.017.01's own tables give a
different scheme entirely, and add a dimension the wiki does not mention at all: **there is a
separate microprogram series per SINTRAN work mode.**

Released versions, ND-05.017.01 "Released microprogram versions":

| Model | ND no. | SINTRAN K **WM406** (A series) | SINTRAN K **WM500** (B series) |
|---|---|---|---|
| ND-5200 | 211272 | `MICRO-5200-A27:DATA` v **11027** | `MICRO-5200-B27:DATA` v **11527** |
| ND-5400 | 211273 | v **11127** | v **11627** |
| ND-5500 | 211274 | v **11227** | v **11727** |
| ND-5700 | 211275 | v **11327** | v **11827** |
| ND-5800 | 211276 | v **11427** | v **11927** |

Pattern: `11` + model index (0/1/2/3/4) + revision for WM406; `11` + (5/6/7/8/9) + revision
for WM500. Each product also ships three libraries: `ND-5000-AF-SIM-A:NRF` (SAX),
`ND-5000-DF-SIM-A:NRF` (DAX), `ND-500-RTC-LIB-A:NRF` (RTC).

Prereleased versions (same manual, "Prereleased versions for Sintran K WM406"):
`MIC-5200-23-400:DATA` v11023, `MIC-5400-23-400` v11123, `MIC-5500-23-400` v11223,
`MIC-5700-23-400` v11323, `MIC-5800-23-400` v11423. Note the header
"ND5000 W/AAP4 with FMUL/DMUL" over the 5400-5800 group - the AAP revision is tied to which
microprogram you may run (the wiki's own upgrade note "check what kind of AAP module
(Checkpoint 3) is installed and use the correct microprogram" is the same fact).

**So the "144xx / 145xx / 147xx / 148xx" numbers in the wiki upgrade steps match NEITHER the
released version numbers NOR the product numbers.** They remain a third, unexplained
identifier. Do not treat them as equal to anything. [OPEN, unchanged from section 2.1]

Later revisions are tracked in the release notes: `211273E01`/`211274E01`/`211275E01`/
`211276E01` (ND-896058-2-EN), then `211273E03`/`211274E03`/`211275F01`/`211276F01`
(ND-896058-4-EN).

---

## 9. RALLAR - what the repo actually holds  [DOC-manual + [OPEN]]

**KUSK and GAMP appear NOWHERE in this repository** except in our own transcription of the
wiki text in Part 1 above. A full sweep (all file types, not just markdown) found "Rallar" in
exactly two files: this document, and one contemporary aside. There is **no Rallar hardware
manual in the repo**. Treat the gate-array names as [DOC-wiki] and unconfirmed.

What IS documented:

### 9.1 Rallar has per-model microcode, in its own version series  [DOC-manual]

- Product **211847** "ND-5830/5850 Microprogram", revisions A01 and B01.
- Files: **`MICRO-5830-12010:DATA`** and **`MICRO-5850-12010:DATA`** (ND-896058-2-EN).
- Versions seen: **12000** (ND-895030-2-EN), **12009** (ND-895061-2-EN and the SINTRAN M
  release information), **12010**, **12011** (SINTRAN N release information, 211847 B).
- So Rallar continues the same `1xxxx` scheme as Samson with a **120xx** series, and like
  Samson ships a **separate image per model** rather than one shared image.

### 9.2 The ND-5950 is the multi-CPU Rallar - the wiki does not mention it  [DOC-manual + [D]]

`ND-895560-2-EN.md` lists the ES basic models. Read together the naming decodes:

| ES model code | Meaning | Machines listed |
|---|---|---|
| **S11** | Satellite, 1 CPU | ND-5400, ND-5500, ND-5700, ND-5700-II, **ND-5830** |
| **C11** | Compact, 1 CPU | ND-5400, ND-5500, ND-5700, ND-5700-II, ND-5800, **ND-5830**, **ND-5850** |
| **L11** | Large, 1 CPU | ND-5700, ND-5700-II, ND-5800, **ND-5830**, **ND-5850** |
| **L12 / L13 / L14** | Large, 2 / 3 / 4 CPUs | ND-5900, **ND-5950** |

**ND-5950 (ND 111286/111287/111288) stands to ND-5830/5850 exactly as ND-5900 stands to
ND-5800**: same L12/L13/L14 codes, same 2/3/4-CPU ladder. The letter = cabinet (S/C/L) and
the last digit = CPU count is **[D] our inference** from the pairings; the manual does not
spell the code out.

### 9.3 Rallar behaviour facts from the release notes  [DOC-manual]

From `ND-896058-2-EN.md` (211847A01) and `ND-896058-4-EN.md` (211847B01), plus SINTRAN
release information:

- Rallar has **CPU-local memory of its own**: "Change of strategy for selecting memory if
  **own CPU memory** on the ND-5830/5850 is exhausted", and "Error if ND-5830 or ND-5850 CPU
  and extra MF-memory".
- **Multi-CPU Rallar was timing-marginal**: "Clear TSB inserted for multi ND-5830/5850,
  because expected trouble at marginal timing."
- Semaphore and lock behaviour was retuned: TSET was polled every 2 microseconds while
  waiting for a semaphore, "now changed to 50-microsecond intervals to avoid hang situations
  on the MF bus"; a **13-second semaphore timeout** was introduced; the octobus driver now
  releases the execution queue if the microprogram must wait more than 10 microseconds, "to
  avoid Lock timeout `20.32B`".
- "Corrections in the **WEXT** instruction adding a new Octobus driver" - i.e. on Rallar the
  octobus is driven through the WEXT ('87 extension) instruction.
- Swapping behaviour: "There might be trashing (100% swapping) if ND-5830/5850 and large FIX
  areas."
- The ND-5850 has a **Tracer** ("Errors in ND-5850 Tracer operations", ND-895230-2H-EN).

### 9.4 Rallar was still unfinished when the PLANC manual was written  [DOC-manual]

`E:\Dev\Ronny\NDInsight\Reference-Manuals\ND-20034-1-EN ND-Specific Programming & Advanced PLANC.md`
line 874, on the ZOOM sort: "A bottleneck in today's ZOOM is the ND-5000's slow access of raw
memory when there are no cache hits. ... Here, a multi-CPU version is possible ... **or wait
for Rallar to be finished.**"

**Scope reminder, unchanged:** our Samson (5800/B30) microcode and servicer work does NOT
cover Rallar. Rallar has its own microcode series (120xx) and its own memory model.

---

## 10. THE 25 '87 EXTENSION INSTRUCTIONS - the list, in full  [DOC-manual, CLOSES the [?] in section 1.5]

Section 1.5 above flagged "[?] which 25 - needs the ND-05.009.3 / ND-05.020.1 opcode
appendix". **Found.** They are Appendix D of
`E:\Dev\Ronny\NDInsight\Reference-Manuals\ND-05.009.4 EN ND-500 Reference Manual.md`
("New instructions - 1987 extension"). The list has exactly **25** entries, which confirms
the wiki's count.

Chapter 1 of that manual, verbatim: "A number of new instructions are introduced with the
ND-5000. These instructions also run on computer systems with the ND-500/1 and the ND-500/2
CPUs. The instructions are labelled: ('87 extension)."

| # | Instruction | Description | Page in ND-05.009.4 |
|---|---|---|---|
| 1 | `AMODB` | integer modulo | 158 |
| 2 | `CAD :=` | load current alternative domain | 316 |
| 3 | `CLINIT` | initialize local clock | 270 |
| 4 | `CLREAD` | read local clock | 271 |
| 5 | `DDIRT` | dump dirty | 285 |
| 6 | `ENTIER` | SIMULA entier function | 159 |
| 7 | `JUMPS` | call supervisor | 317 |
| 8 | `LCNTXT` | load context block | 310 |
| 9 | `LREGBL` | load register block | 308 |
| 10 | `NCPLC` | convert ND-500 descriptor to PLANC descriptor | 269 |
| 11 | `PHYLADR` | get physical address | 320 |
| 12 | `PLCCN` | convert PLANC descriptor to ND-500 descriptor | 268 |
| 13 | `RECVE` | receive from port | 304 |
| 14 | `REXT` | read from device external to CPU | 311 |
| 15 | `RHOLE` | read from NUCLEUS hole | 301 |
| 16 | `RPHS` | read from physical address | 314 |
| 17 | `SCNTXT` | save context block | 309 |
| 18 | `SCPUNO` | store CPU number | 319 |
| 19 | `SEND` | send to port | 303 |
| 20 | `SREGBL` | save register block | 307 |
| 21 | `SVERS` | store microprogram version | 318 |
| 22 | `TOSSP :=` | special load of TOS | 313 |
| 23 | `WEXT` | write to device external to CPU | 312 |
| 24 | `WHOLE` | write to NUCLEUS hole | 302 |
| 25 | `WPHS` | write to physical address | 315 |

**Naming caution [DOC-manual]:** the manual's own table of contents uses slightly different
mnemonics for four of these - `LNCTX`/`SNCTX` (TOC) versus `LCNTXT`/`SCNTXT` (Appendix D),
and `RECV` (TOC) versus `RECVE` (Appendix D). Read the body pages before fixing a mnemonic in
code. The changelog in `5800-30.TEXT` (section 1.7 above) uses `Lregbl` and `Nksend`, a third
spelling style again.

**Why this list matters to the emulation:**

- `RHOLE` / `WHOLE` / `SEND` / `RECVE` are the **NUCLEUS hole and port primitives** - the
  microcoded path the DOMINO work in
  `DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md` describes as letting an
  unprivileged ND-500 user program move data to a controller with no system call.
- `REXT` / `WEXT` are the **"device external to CPU"** pair, and the Rallar release notes
  (section 9.3) show `WEXT` is how the octobus driver is reached from the microprogram.
- `SREGBL` / `LREGBL` / `SCNTXT` / `LCNTXT` are the register-block and context-block
  instructions - the same objects as the `CED` and `PS` context-field defects listed in
  section 1.7 above.
- `SVERS` "store microprogram version" and `SCPUNO` "store CPU number" are the macro-level
  reads of the identity fields discussed in sections 1.6 and 7.
- `CLINIT` / `CLREAD` are the built-in RTC (`ND-500-RTC-LIB`), relevant to the octobus
  determinism work.

---

## 11. Two places where ND's OWN MANUALS CONTRADICT EACH OTHER  [OPEN]

### 11.1 WICO on the ND-5800

The two manuals print the same table and disagree on one cell.

| Source | ND-5800 row |
|---|---|
| `ND-05.020.01` **Table 4** "Differences Between CPU models" | Enabled: Data cache, **WICO**, Instr.cache, Addr.cache, SIFGOC. Disabled: (blank) |
| `ND-05.017.01` **Table 8** "Difference between the CPU Models" | Enabled: Data cache, Instr.cache, Addr.cache, SIFOC. **Disabled: WICO** |

The wiki follows the hardware description (WICO enabled on ND-5800). Both manuals agree that
WICO is **disabled** on the ND-5700, so WICO-enabled is the one thing that distinguishes the
5800 from the 5700 in the feature column - which makes the hardware description's version the
more likely one, but that is reasoning, **not evidence**. **[OPEN]**

Glossary from ND-05.017.01 Table 8, verbatim:

- **SIFOC / SIFGOC** : "Smart IFGO Control (Smart ifgo strategy enabled)" - a control
  strategy, **not a cache**. The wiki's column header "Smart IfGo cache" is misleading.
- **WICO** : "Write In Cache Only (Write ones strategy ('dirty'))"

### 11.2 Which I/O processor each model uses

The wiki says the Compact series uses "ND-110/CX I/O Processor (ND-110 in ND-5200 Compact
system)". The manuals say otherwise:

| Model | ND-05.017.01 Table 1 (Compact) | ND-05.017.01 Table 2 (Large) | wiki |
|---|---|---|---|
| ND-5200 | ND110 | ND110 | ND-110 |
| ND-5400 | **ND120** | ND120 | ND-110/CX |
| ND-5500 | **ND120** | ND120 | ND-110/CX |
| ND-5700 | ND120/CX w/memory | ND120/CX w/2Mb | ND-110/CX |
| ND-5800 | - | ND120/CX w/4Mb | - |
| ND-5900 | - | ND120/CX w/4Mb | - |

**"ND-110/CX for the 5400 and 5500" is not in these manuals.** The wiki's own upgrade steps
are self-consistent with the manual though ("Exchange the ND-110 CPU with ND-120 CPU with 4MB
memory" when going 5200 -> 5400), so the Compact-series bullet list looks like the error.
**[OPEN]** - worth checking against a Compact parts list before correcting the wiki.

---

## 12. Full manual configuration tables  [DOC-manual]

### 12.1 Large cabinet - ND-05.017.01 Table 2

| Parameter | 5200 | 5400 | 5500 | 5700 | 5800 | 5900* |
|---|---|---|---|---|---|---|
| CPU type | 1 | 2 | 2 | 2 | 3 | 3 |
| CPU model | 2 | 4 | 5 | 7 | 8 | 8 |
| CPU ND-number | 110249 | 110248 | 110247 | 110218 | 110171 | 110171 |
| Microprogram vers.** | 110xx | 111xx | 112xx | 113xx | 114xx | 114xx |
| I/O processor | ND110 | ND120 | ND120 | ND120/CX w/2Mb | ND120/CX w/4Mb | ND120/CX w/4Mb |
| Memory shared/local (MB) | 4/2 | 4/4 | 8/4 | 12/6 | 16/10 | **24/6** |
| Data cache (KB) | - | - | 64 | 64 | 64 | 64* |
| Instruction cache | - | - | 8K x 320 bit | 8K x 320 bit | - | - |
| Disk size (external) | up to 29 Gb across all models | | | | | |

`*` = model 5900 contains 2, 3 or 4 CPUs. `**` = valid for SINTRAN K, WM 406.

Notes:

- **`8K x 320 bit` = 320 KB**, which reconciles the wiki's bare "320" instruction-cache
  column. Same for the 64 KB data cache.
- The memory figures here are the **delivered configuration**, not the wiki's "8-512 MB"
  ranges. Both can be true (standard config versus maximum expansion) - they are different
  measurements, so do not overwrite one with the other.
- **Oddity [OPEN]:** this table shows a dash for the ND-5400's instruction cache and for the
  ND-5800/5900's instruction cache, yet Table 8 and Table 4 both say the instruction cache is
  ENABLED on the 5400, 5800 and 5900. The dashes are probably an OCR or typesetting loss, not
  a fact. Do not read "no instruction cache on the ND-5800" out of this.

### 12.2 Compact - ND-05.017.01 Table 1

| Parameter | 5200 | 5400 | 5500 | 5700 |
|---|---|---|---|---|
| CPU type | 1 | 2 | 2 | 2 |
| CPU model | 2 | 4 | 5 | 7 |
| CPU ND number | 110249 | 110248 | 110247 | 110218 |
| CPU part number | 320001 | 320002 | 320002 | 320002 |
| Microprogram vers.* | 110xxx | 111xxx | 112xxx | 113xxx |
| I/O processor | ND110 | ND120 | ND120 | ND120/CX w/memory |
| Disk, A models (internal) | 60 to 4x125 Mb | 125 to 4x125 Mb | 125 to 4x125 Mb | 125 to 4x125 Mb |
| Disk, model B (external) | up to 3.6 Gb | up to 3.6 Gb | up to 3.6 Gb | up to 3.6 Gb |
| Streamer | A-models | A-models | A-models | A-models |

Disk model codes (same table): A0/A10 = 60 MB (**ND-5200 only**), A1/A11 = 125 MB,
A2/A12 = 2x125, A3/A13 = 3x125, A4/A14 = 4x125, B = external.

Compact memory, ND-05.017.01 chapter 2: shared/local **4/2 MB on the ND-5200 Compact model A**
and **4/4 MB** on the other Compact models.

### 12.3 Peak performance  [DOC-manual]

ND-05.020.01, chapter 1: "System performance rates up to **28 MIPS** (ND-5900 model 4 with
four CPUs) depending on the model."

---

## 13. A manual the wiki's reference list is missing  [DOC-manual]

`E:\Dev\Ronny\NDInsight\Reference-Manuals\500\ND-830102.1B EN ND-5000 ES Model C Hardware Maint. Manual-Sintran.md`
(ND-830102) documents the **ND-5000 ES Model C**, and names a sibling **ND-830103** for the
**ES Model S**. Verbatim: "The new ND-5000 ES Model C replaces the current ND-5000 Compacts",
and "The new ND-5000 ES Model C is available with all ND-5000 CPU versions, including
ND-5800." Its parts list carries the same three CPU part numbers (320001 / 320002 / 320003).

So the family has **three cabinet generations**, not two: the original Large cabinet, the
Compact series, then the **ES** line (Model S satellite / Model C compact / Model L large)
which replaced the Compacts and is where the Rallar machines appear.

---

## 14. What is still open after this pass

1. **ND-5900: CPU model 8 or 9?** Section 7. Settle by reading word 7 of an ND-5900 microcode
   image if one is ever found.
2. **WICO on the ND-5800: enabled or disabled?** Section 11.1. Two ND manuals disagree.
3. **I/O processor on the 5400/5500 Compact.** Section 11.2. Needs a Compact parts list.
4. **KUSK and GAMP.** Section 9. No Rallar hardware documentation exists in this repo at all.
   Anything about the two gate arrays stays [DOC-wiki].
5. **The "144xx/145xx/147xx/148xx" microprogram numbers.** Section 8. Still match nothing.
6. **ACCP part 324702 versus the dumped 324716.** Section 5.1. Which models shipped which.
7. **The `LCNTXT`/`LNCTX`, `SCNTXT`/`SNCTX`, `RECVE`/`RECV` mnemonic split.** Section 10.
   Read the body pages of ND-05.009.4 before committing a spelling to code.

## Cross-references for Part 2

- `E:\Dev\Ronny\NDInsight\SINTRAN\ND5000\DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md`
  - the DOMINO/DIOC controller architecture the NUCLEUS hole instructions feed
- `E:\Dev\Ronny\NDInsight\SINTRAN\ND5000\ACCP-COMPLETE-REFERENCE.md` - the ACCP firmware and
  register map (the card listed as part 324702 in section 5.1)
- `E:\Dev\Ronny\NDInsight\SINTRAN\ND5000\OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md`
  - octobus station map, including the 70B-73B ND-5000 CPU range confirmed in section 1.2 above

---

# PART 3 - PERFORMANCE, DATES AND THE ONE MEASURED BENCHMARK (added 2026-08-24)

## 15. ND's own performance figures - and the number that is routinely misread  [DOC-manual]

`ND-05.020.01`, chapter 1, "Performance", verbatim and complete:

> - Maximum performance for one CPU is 6-7 MIPS.
> - System performance rates up to 28 MIPS (ND-5900 model 4 with four CPUs) depending on the model.

**The 28 MIPS figure is the FOUR-CPU AGGREGATE, not a processor rating.** It is quoted on its
own in secondary sources (and was quoted that way in an earlier draft of the ndwiki article),
which makes the machine look about four times faster than it was per processor. The
comparable single-processor number is **6-7 MIPS**, and even that is a NATIVE instruction
rate, not a VAX-equivalent one - see section 17.

## 16. THE ONLY MEASURED BENCHMARK IN ND'S OWN DOCUMENTATION  [DOC-manual]

`ND-05.017.01` section 8.3.4 "INVERSE-MATRIX, WHEATSTONE, DHRYSTONE and LACOURT Tests"
prints sample output from the benchmark programs shipped with the machine, run as user
`ND5000-USER-TEST` under the ND-500/5000 Monitor:

| Benchmark | Result as printed |
|---|---|
| **Whetstone** | `3125.0 WHETSTONE KIPS` |
| **Dhrystone** | `Dhrystone time for 100000 passes = 15` / `This computer benchmarks at 6553 dhrystones/second` |
| **Lacourt** | `8.68 SECONDS` / `16.08 SECONDS` / `12.92 SECONDS` / `13.90 SECONDS` |
| Inverse Matrix | precision table only, no timing |

**This is the only measured performance data for the ND-5000 anywhere in this repository.**
Everything else (6-7 MIPS, 28 MIPS, the relative ladders) is a vendor rating.

### 16.1 What is NOT known about it  [OPEN]

- **Which CPU model ran it.** The manual never says. The transcript shows
  `ND-500/5000 MONITOR Version 100 (preliminary) 87. 6.16 / 87. 9. 1`, so it is a 1987
  machine, but that does not pin the model. This matters a lot: against the relative ladder
  in section 18, an ND-5200 and an ND-5800 differ by about 11x.
- **Which Dhrystone version.** The output line
  "This computer benchmarks at N dhrystones/second" is the standard **Dhrystone 1.1** C
  program's format. [D - inferred from the output format, not stated.] Version matters:
  Dhrystone 2.x results are not comparable to 1.1 results.
- **Which compiler.** Dhrystone is heavily compiler-sensitive, and the manual groups these
  tests as "FORTRAN number crunchers" even though Dhrystone is a C program - so the grouping
  text cannot be trusted to identify the language or toolchain used.

### 16.2 The conversion, and why it is worth doing  [D, from a standard definition]

**DMIPS** is defined as dhrystones-per-second divided by **1757**, the VAX-11/780's Dhrystone
1.1 result. Applying that definition:

- `6553 / 1757` = **about 3.7 DMIPS** for a single ND-5000 CPU.

So one ND-5000 CPU measured at roughly **3.7 VAX-11/780 equivalents**. That is a very
different picture from the 28 MIPS headline, and it is the number to use in any comparison
with machines of the period. By the same conversion a four-CPU ND-5900 model 4 lands near
**15 DMIPS**, not 28.

The 1757 constant is a standard industry definition, not something found in an ND manual -
grade the conversion **[D]**, the 6553 measurement **[DOC-manual]**.

## 17. Why raw MIPS across architectures is not a comparison  [reference note]

ND's "6-7 MIPS" is a native instruction rate. A VAX CISC instruction frequently did the work
of several instructions on a simpler machine, so instructions-per-second was not comparable
between vendors even in period. The industry's workarounds were the **VUP** (VAX Unit of
Performance, VAX-11/780 = 1) and **DMIPS** as above.

Commonly cited period figures, **NOT from any ND source and NOT verified in this repo** -
included only so that the 3.7 DMIPS number in section 16.2 has a scale to sit on:

| Machine | Approximate performance |
|---|---|
| PDP-11/70 | about 0.6 VUP |
| MicroVAX II | about 0.9 VUP |
| VAX-11/780 | 1 VUP (definitional) |
| VAX 8600 | about 4 VUP |
| VAX 8800 | about 6 VUP |

Reading: a single ND-5000 CPU was roughly VAX 8600 class, comfortably obsoleted the PDP-11
family for compute-bound work, and did not reach the top single-processor VAX machines of
1988. **Do not put these competitor numbers into an NDInsight document as evidence** - they
are background, and this table is the only place they should appear.

## 18. Relative performance ladders - two ND sheets, one of them damaged  [DOC-manual]

`E:\Dev\Ronny\NDInsight\Installation\Product-Info\ND-5230-A1-EN.md` ("ND-5000 ES Model L",
Configuration Overview) gives a clean ladder normalised to the ND-5200:

| ND-5200 | ND-5400 | ND-5500 | ND-5700 | ND-5800 | 5900 L2 | 5900 L3 | 5900 L4 |
|---|---|---|---|---|---|---|---|
| 1 | 2.2 | 4.3 | 6.3 | 11.3 | 22.6 | 33.9 | 45.2 |

The three ND-5900 values are exactly 2x, 3x and 4x the ND-5800 - ND claimed **linear scaling
with CPU count**. Same sheet: memory 6-544 MB, disk 35.2 GB, multifunction bus capacity
**18 MB/sec**, up to 512 MB main memory, front-end local memory up to 32 MB.

`E:\Dev\Ronny\NDInsight\Installation\Product-Info\ND-5700-B1-EN.md` gives, for the same
machines, relative CPU performance **1 / 2 / 3 / 4 / 4** (ND-5700, ND-5800, 5900 M2, M3, M4).
**M3 and M4 cannot both be 4** under linear scaling, so that row is damaged in the scan.
Prefer the ND-5230 ladder. [D]

Note also that the two sheets use **different baselines** (ND-5200 = 1 versus ND-5700 = 1), so
their numbers must never be mixed in one table.

## 19. Dating the ND-5900  [DOC-manual]

No announcement date survives in this repo. The product was documented and SINTRAN-supported
by the first half of 1988:

| Evidence | Date |
|---|---|
| `ND-05.020.01 ND-5000 Hardware Description` v1 - describes the ND-5900, gives 28 MIPS | **April 1988** |
| `ND-60230.5 SINTRAN III Release Information, K version` v5 - multi-CPU ND-5900 supported in ND-500/5000 Monitor version J | **May 1988** |
| `ND-05.017.01 ND-5000 Hardware Maintenance` v1 - carries the ND-5800 to ND-5900 upgrade procedure | **June 1988** |
| MF bus test and maintenance PROMs used by `SET-CPU-MODEL` | **November 1987** |
| `PRODUCT NEWS` (the wiki's source for the Compact models) | **November 1987** |

`ND-5700-B1-EN.md` covers the ND-5700, ND-5800 and ND-5900 as one product family in a single
sheet, which suggests they were launched together rather than the ND-5900 arriving later -
but that sheet carries no date, so this is **[D]**, a reading, not a fact.

Related dates already in hand: `ND-05.017.01` internal transcripts carry
`November 11, 1987` (MF bus test program), `DECEMBER 2, 1987` (trace module),
`1987-12-20` (page-fault exerciser A03), and the ND-500/5000 Monitor at
`Version 101 87. 9. 1 / 87. 9.17`.

## 20. Additions to the open list

8. **Which CPU model produced the 6553 dhrystones/second figure.** Section 16.1. Without it
   the DMIPS number cannot be attached to a specific system.
9. **Which Dhrystone version and compiler.** Section 16.1.

---

# PART 4 - WHICH MICROCODE WE RUN, AND THE VERSION CONSTANT DECODED (added 2026-08-24)

## 21. The microcode CpuND5000 executes is SAMSON, not Rallar  [V - re-verified by byte dump]

`CpuND5000` runs **`MICRO-5800-B30`**. Decoded from its own bytes:

| Field | Location | Value | Meaning |
|---|---|---|---|
| Model/type | word 7, last byte | `0x38` | CPU **type 3**, CPU **model 8** = **ND-5800** |
| Version | word 1, last 2 bytes | `0x2E9A` = **11930** decimal | series 119xx = ND-5800 **WM500**, revision **30** |

**ND-5800 is a Samson machine** (Samson = ND-5200/5400/5500/5700/5800/5900). So every
microword-level fact in this folder, and every `// real B30 microcode does X` comment in
RetroCore's `Emulated.HW/ND/CPU/ND500/`, is a statement about **Samson**.

**There is no Rallar microcode in the corpus at all.** `E:\Dev\Ronny\ND5000UC\docs\MC\`
holds images for models 5200, 5500, 5700 and 5800 only. Rallar images would be named
`MICRO-5830-12010:DATA` / `MICRO-5850-12010:DATA` (product 211847, the 120xx series - see
PART 2 section 9.1). We do not have them, and nothing in this repo describes Rallar's
microword format. **Do not assume the 128-bit Samson microword layout carries over to
Rallar** - Rallar is a different processor built from different gate arrays (KUSK/GAMP).

## 22. THE VERSION CONSTANT IS THE MANUAL'S VERSION NUMBER, IN DECIMAL  [V - CLOSES section 2.1]

Section 2.1 above recorded an unreconciled item: we had extracted `027232B` (octal) from
microword 1 of `MICRO-5800-B30` and could not match it to any documented version number.

**The mistake was reading it as octal.** Read as **decimal**, `0x2E9A` = **11930**, which is
exactly the manual's scheme from PART 2 section 8: `11` + series digit + two-digit revision.

Word 1 dumped from every image in the corpus (offset 16, last two bytes):

| Image | word 1 hex | decimal | Decodes as |
|---|---|---|---|
| `MICRO-5800-B30` | `0x2E9A` | **11930** | 5800 WM500, rev 30 |
| `MICRO-5800-B29` | `0x2E99` | **11929** | 5800 WM500, rev 29 |
| `MICRO-5800-A30` | `0x2CA6` | **11430** | 5800 WM406, rev 30 |
| `MICRO-5800-A29` | `0x2CA5` | **11429** | 5800 WM406, rev 29 |
| `MIC-5800-90-500` | `0x2ED6` | **11990** | 5800 WM500, rev 90 |
| `MIC-5700-90-500` | `0x2E72` | **11890** | 5700 WM500, rev 90 |
| `MIC-5500-90-500` | `0x2E0E` | **11790** | 5500 WM500, rev 90 |
| `MIC-5200-90-500` | `0x2D46` | **11590** | 5200 WM500, rev 90 |
| `MICRO-5200-M27` | `0x2B13` | **11027** | 5200 WM406, rev 27 |
| `CONTROL-STORE` | `0x2B16` | **11030** | 5200 WM406, rev 30 |

Cross-check against the manual's released-version table (PART 2 section 8): it lists
`MICRO-5200-A27` = **11027** and `MICRO-5800-B27` = **11927**. Our `MICRO-5200-M27` image
carries exactly **11027**, and our 5800 WM500 images carry 11929/11930 - the same 119xx
series, three revisions later. **The manual and the binaries agree exactly.**

Consequences:

1. **The series digit encodes model AND work mode together**, per PART 2 section 8:
   110xx/111xx/112xx/113xx/114xx = 5200/5400/5500/5700/5800 on WM406;
   115xx/116xx/117xx/118xx/119xx = the same five models on WM500.
2. **The last two digits are the revision** (27, 29, 30, 90 all appear).
3. **CORRECTION to section 1.6 above.** It stated the version constant was "the same across
   models - tracks REVISION, not model". That is **wrong**: word 1 differs per model *and*
   per work mode. Only word 7 was compared across models at the time; word 1 was read from a
   single image and assumed constant.
4. **`M` work-mode images are the A (WM406) series** - byte-proof: `MICRO-5200-M27` carries
   11027, which is the A27 number. This confirms what `docs\MC\README.md` inferred from the
   fact that M-images pair with A-label symbol files.
5. **`CONTROL-STORE.DATA` is a 5200, and the manifest is wrong about the model.** Its word 7
   is `0x12` (type 1 / model 2) and its version is 11030 (5200, WM406, rev 30). The manifest
   calls it "5800 CONTROL-STORE:DATA (~A30 rev)". The **A30 part is right** (WM406, rev 30);
   the **5800 part is wrong**. Two independent fields agree it is a 5200 image. This upgrades
   the `[?]` in `docs\MC\README.md` to a settled **[V]** finding.

**Still open:** this does NOT explain the wiki's "144xx/145xx/147xx/148xx" upgrade numbers
(PART 2 section 8). Those put the *model digit* in the third position (`14` + 4/5/7/8),
whereas ND's real scheme uses a series index that folds in work mode. They remain
unexplained.

## 23. What else the corpus tells us about the microcode  [V/DOC]

- **Geometry**: every image is exactly **262144 bytes = 16384 words x 128 bits**. That is a
  **16K-word control store**, matching the CS baby module part 324707 "Control store - 16K"
  in PART 2 section 5.1. Byte-verified across all images.
- **Word 7 is identical across models except its last byte** - the model/type byte is the
  only per-model difference in that word (`50 00 00 01 dd 70 b0 00 00 00 00 00 00 07 00 XX`).
- **Word 1 is likewise identical except its last two bytes** - the version constant
  (`40 00 00 01 de 01 60 10 00 00 00 00 00 00 XX XX`).
- **Revisions present**: 27, 29, 30 and 90. Revision 30's product description
  (`5800-30.TEXT`, Reg.no 211276D, source 250291D) documents the CED and PS register fixes
  already noted in section 1.7 above.
- **Work mode** is a SINTRAN III VSX generation, selected by `LIST-TITLE`
  "GENERATION (WORK MODE NO)": 406 -> A image, 500 -> B image. Both are single-CPU configs
  per `5800-30.TEXT`.
- **We run the newest 5800 WM500 image we have** (rev 30). The manual's released table stops
  at rev 27, so revisions 29, 30 and 90 in the corpus are all later than anything documented
  in `ND-05.017.01`.

## 24. Additions to the open list

10. **Rallar microcode is absent.** Sections 21. `MICRO-5830-*` / `MICRO-5850-*` (product
    211847, 120xx series) are not in the corpus and their microword format is undocumented
    here.
11. **The 144xx family of version numbers.** Section 22. Still matches nothing, even now that
    the real encoding is understood.

---

# PART 5 - WHAT "WORK MODE" (WM406 / WM500) ACTUALLY MEANS (added 2026-08-24)

Parts 2 and 4 kept saying "work mode A=WM406 / B=WM500" without ever defining the term. This
part defines it from primary sources, and in doing so produces a **third independent
confirmation** of the microprogram version scheme.

**Primary source:** `E:\Dev\Ronny\NDInsight\SINTRAN\Release-Documentation\ND-60230-5-EN SINTRAN III - Release Information - K-version.md`
(version 5, May 1988) - cited below as **[K5]**.

## 25. Work mode = GENERATION of a SINTRAN III version  [DOC-manual]

A **work mode** and a **generation** are the same thing, and it is **not** a version number of
its own. A machine runs, for example, *SINTRAN III/VSX **version K**, **generation 406***.
The SINTRAN command `@LIST-TITLE` prints it under the heading
**`GENERATION (WORK MODE NO.)`** - confirmed by a sample transcript in
`Installation\Installation-Description\ND-211297-1-EN.md` which shows
`BETA TEST (WORK MODE NO.):    312B`.

Version K of SINTRAN III/VSX existed in these generations [K5]:

**101, 200, 301, 312, 406, 500**

They are broadly but not strictly cumulative. [K5] verbatim: "Features introduced in
generation 406 are generally also available in generation 500 even if they were unavailable
in generation 312."

**Later SINTRAN versions abandoned the three-digit scheme** and used small integers instead -
`SINTRAN-III/VSX L Work-Mode 7` and `M Work-Mode 6`
(`Installation\Installation-Description\ND-895061-2-EN.md`), also
`SINTRAN-III >= L Workmode 7` in ND-895275/895602/895603/895604/895617/895627/895628. The
three-digit generations are a **K-version** phenomenon. [DOC-manual; why L=7 and M=6 rather
than ascending is NOT explained anywhere I have found - **[?]**, and possibly an OCR
artifact, do not build on it.]

## 26. Why the ND-5000 has TWO microprograms per model  [DOC-manual - this is the answer]

[K5] section 17.1, verbatim:

> "ND-500 series CPUs require generation 500 of SINTRAN III/VSX, whereas **ND-5000 series
> CPUs require either of the generations 406 or 500**."

**That is the whole reason the A/B split exists.** An ND-5000 could be run under either
generation, so ND shipped a microprogram image for each, and the machine must be given the
one matching the SINTRAN generation it will run under. The A series is generation 406, the B
series is generation 500.

Also [K5] section 17: "The ND-500/5000 Monitor version J and ND-500/5000 Swapper are intended
to be used under generation 500 of SINTRAN III/VSX, but the ND-500/5000 Monitor may also run
under generation 406." And: "Both ND-500 series and ND-5000 series CPUs may run version J.
Furthermore, the multi-CPU systems (ND-580 and ND-5900) are supported."

### 26.1 The two generations are NOT feature-equivalent  [DOC-manual]

- **`CHANGE-CPU`** - the command that moves a process to another CPU on a multi-CPU ND-5900 -
  "runs only from SINTRAN work mode 500"
  (`Installation\Installation-Description\ND-211124-2-EN.md`). **So a multi-CPU ND-5900 is
  effectively a generation-500 machine**, even though the ND-5000 family as a whole accepts
  406.
- **`MON PERFO` is not supported in generation 406 at all** [K5].
- `DISC-ACCESS-LOG` does not support SCSI disks in generations 312, 406 or 500 [K5].
- Some segment-sharing restrictions apply only to "generations 406 and earlier" [K5].
- **Standard system builds differed by generation** [K5]: standard system **A** for
  generations 101 and 200; **C** for 301, 312 and 406; **D** for 312 and 406 only. "Standard
  systems for generation 500 were not available at the time of printing" (May 1988).
- The ND-500/5000 Swapper product description
  (`Installation\Installation-Description\ND-211034-9-EN.md`) states:
  "**ND-5000**: must use SIII/VSX K Workmode 406" and
  "**ND-500**: must use SIII/VSX K Workmode less than or equal to 312", and separately
  "The ND-5000 requires SINTRAN III/VSX 500 K workmode 406." These do not read consistently
  with [K5]'s rule above, and the phrasing "VSX 500 K workmode 406" is ambiguous about which
  number is the product and which is the generation. **[?]** Prefer [K5].

## 27. THIRD CONFIRMATION of the version scheme  [DOC-manual]

[K5] section 1.2 "MICROPROGRAM VERSIONS FOR ND-5000" prints the whole grid:

> "The following table shows the microprogram versions required to run ND-5000 systems on
> generations 406 and 500 of SINTRAN III:"

| System type | generation 406 | generation 500 |
|---|---|---|
| ND-5200 | **11026** | **11526** |
| ND-5400 | **11126** | **11626** (or later versions: ...27, etc.) |
| ND-5500 | **11226** | **11726** |
| ND-5700 | **11326** | **11826** |
| ND-5800 | **11426** | **11926** |

**All three sources now agree**, at three different revision levels:

| Source | Revision level | Evidence type |
|---|---|---|
| [K5], May 1988 | **26** | printed minimum-version table |
| `ND-05.017.01`, June 1988 | **27** | printed released-version table (PART 2 section 8) |
| The microcode binaries | **27, 29, 30, 90** | word 1 of the image, decimal (PART 4 section 22) |

The series digits are identical in all three: `110/111/112/113/114` for generation 406 and
`115/116/117/118/119` for generation 500, across ND-5200/5400/5500/5700/5800. The scheme
described in PART 2 section 8 and decoded from the binaries in PART 4 section 22 is now
**settled** - it is not an inference from one table any more.

[K5]'s parenthetical "(or later versions: ...27, etc.)" also confirms directly that the last
two digits are a **revision counter**, exactly as PART 4 section 22 concluded from the
binaries.

## 28. Terminology trap - "500" means three different things  [reference note]

This bit us while reading the sources and will bite the next reader:

| "500" as | Means |
|---|---|
| **ND-500** | the 32-bit CPU architecture (ND-520, ND-570, ND-580 ...) |
| **SINTRAN III/VSX 500** | the product variant supporting an ND-500-family CPU |
| **generation 500 / work mode 500 / WM500** | a SINTRAN III **version-K generation**, the B microprogram series |

A sentence like "the ND-5000 requires SINTRAN III/VSX 500 K workmode 406" contains two of
these at once. Read every occurrence in context; do not pattern-match on the number.

## 29. Additions to the open list

12. **Why later SINTRAN versions use L=Work-Mode 7 and M=Work-Mode 6.** Section 25. The
    descending numbers are unexplained and may be an OCR error in ND-895061.
13. **The ND-211034 Swapper generation requirements** contradict [K5]. Section 26.1.

---

# PART 6 - WORK MODE ACROSS SINTRAN J..N, AND WHAT A ACTUALLY DIFFERS FROM B (added 2026-08-24)

Part 5 defined work mode from the K-version release information alone. This part sweeps
**every** SINTRAN III release-information manual in the repo (J, K, L, M, N) and answers two
questions: does the concept survive past K, and what is the real difference between the
A (406) and B (500) microprograms.

Sources, all in `E:\Dev\Ronny\NDInsight\SINTRAN\Release-Documentation\`:

| Version | File | Date |
|---|---|---|
| J | `ND-60.230.01_SINTRAN_III_J-version_Release_Information_January_1985.md` | January 1985 |
| K | `ND-60230-5-EN SINTRAN III - Release Information - K-version.md` | May 1988 |
| L | `ND-860230-6-EN Sintran III - Release Information - L-Version.md` | September 1988 |
| M | `ND-860230-7A-EN SINTRAN III - Release Information - M-Version.md` | Jan 1990 (v7) / Dec 1990 (v7A) |
| N | `ND-860230-8-EN SINTRAN III - Release Information - N-version.md` | February 1993 |

## 30. The concept starts at K and survives to N  [DOC-manual]

**J (1985): no.** "Generation" appears three times in the J manual and every one of them means
*system generation* - building a system - as in "an option that must be ordered at the time of
system generation". There is no generation-as-variant number and no work mode. **The work-mode
concept is not present in J.**

**K, L, M, N: yes**, all four use it. What changes is the numbering.

| Version | Generations documented | Where stated |
|---|---|---|
| **K** | **101, 200, 301, 312, 406, 500** | throughout [K5]; also "405 or later" appears once, see section 33 |
| **L** | **5** (config screen), and **7** required by several products | L manual config program; ND-895275/895602/895603/895604/895617/895627/895628 |
| **M** | **5** (original) and **6** (updated) | "The current revision of the manual is updated to reflect **generation 6** of the M-version of SINTRAN III/VSX. Changes from the original version (**generation 5**) are marked with a change bar." |
| **N** | **1** | "SINTRAN III/VSX version N, **generation 1** requires revision level (patch file level) 1000 or higher." |

**The three-digit numbering is a K-only phenomenon.** From L onward the numbers are small
integers.

### 30.1 The numbering across versions is NOT coherent, and I cannot explain it  [OPEN]

L's release manual (September 1988) shows generation **5**. M's manual says M began at
generation **5** and moved to **6**. N restarts at **1**. Several product descriptions require
"SINTRAN-III >= L Workmode **7**" - a higher number than any M generation.

`ND-895061-2-EN.md` lists both alternatives side by side, which at least reads consistently as
"either L at work mode 7, or M at work mode 6":

```
| SINTRAN-III/VSX  | L Work-Mode 7   |
| SINTRAN-III/VSX  | .M Work-Mode 6  |
```

So the number is **scoped to its version letter** and must always be quoted with it -
"work mode 7" alone is meaningless. Beyond that, why L reaches 7 while M runs 5-6 and N
restarts at 1 is **not explained in any document I have found**. Do not build a rule on it.
**[OPEN - item 12 in the running list, now better evidenced but still unexplained.]**

### 30.2 What the work mode IS, from L onward  [DOC-manual]

The L-version configuration program displays it as a system parameter:

```
| Work mode version (generation)         | 000005B |
```

with the definition, verbatim: "**Work mode version** - Version of work mode used when
generating this system (**for internal use by ND**)."

Two things follow. First, it is a **build-time property of a generated SINTRAN image**, shown
in octal by the configuration program. Second, ND itself called it internal - yet product
descriptions kept quoting it as an installation requirement right through the L and M eras, so
in practice it stayed externally load-bearing.

L's `NEW-SYSTEM` installation program also gained a **`CHECK-WORKMODE`** step, described as
"check if requirements to SINTRAN III" - i.e. the installer verifies the running system's work
mode before applying a patch file.

## 31. GENERATION 406 DIED WITH THE K-VERSION  [DOC-manual - clean finding]

Every release manual from K on carries a "microprogram versions for ND-500/5000" table.
Putting them side by side settles what happened to the A series:

| Model | K (gen 406) | K (gen 500) | M | N |
|---|---|---|---|---|
| ND-5200 | 11026 | 11526 | **11531** | **11533** |
| ND-5400 | 11126 | 11626 | **11631** | **11633** |
| ND-5500 | 11226 | 11726 | **11731** | **11733** |
| ND-5700 | 11326 | 11826 | **11831** | **11833** |
| ND-5800 | 11426 | 11926 | **11931** | **11933** |
| ND-5830/5850 | - | - | **12009** | **12011** |

**M and N list ONLY the 115-119 series.** The 110-114 (generation 406 / A) series is gone
entirely. Generation 406 was a **K-version generation**, and once the K-version was superseded
the A microprograms had no host to run under.

Consequence for the emulation: **the B images are the ones that matter.** `MICRO-5800-B30` -
the image `CpuND5000` runs - is on the line that survived. The A images are a K-era artifact.

Revision levels also climb across the manuals, which independently confirms the last two
digits are a revision counter (PART 4 section 22): **26** (K release info) -> **27**
(ND-05.017.01) -> **29/30** (our binaries) -> **31** (M) -> **33** (N). **We do not hold
revisions 31 or 33.**

### 31.1 The classic ND-500 microprogram series, for completeness  [DOC-manual]

The same M and N tables list the pre-ND-5000 machines, on a different numbering scheme:

| Prod. no. | System | M | N |
|---|---|---|---|
| 210332 | ND-500 series I, standard | 10512 | 10512 |
| 210338 | ND-500 series I, AX-CPU | 10412 | 10412 |
| 210411 | ND-500 series I, CX-CPU | 10312 | 10312 |
| 210412 | ND-500 series I, CXA-CPU | 10612 | 10612 |
| 210787 | ND-530 | 15313 | 15313 |
| 210786 | ND-550/560/570 | 15213 | 15213 |
| 210788 | ND-550/560/570, > 32 Mb | 15413 | 15413 |
| 210701 | ND-580 | 15113 | 15113 |

This confirms the "classic-500 microprograms were 15211/15311/15111 per model" remark in
section 2.1 of Part 1 - the 151xx/152xx/153xx/154xx series are the ND-580/570/530/570-large
machines. Note these are **frozen** between M and N while the ND-5000 ones advanced 31 -> 33.

## 32. WHAT ACTUALLY DIFFERS BETWEEN A AND B  [V - byte-verified from our own images]

This is the substantive answer, and it comes from our own comparison of the two revision-30
images, recorded in
`E:\Dev\Ronny\NDInsight\SINTRAN\ND5000\OCTOBUS-ND100-ND5000-REFERENCE.md` section 7, verbatim:

> **A30 vs B30 [V]**: identical ACCP primitive layer; B30 (work mode 500) adds the whole NK
> multiprocessor nucleus (SEND/RECVE/GETINF/MHOLE macro-instructions, LOCK_DH spin-locks,
> NK_TRACE, SENKICK) and real handlers for kicks 3-6; A30 stubs kicks 3-6 to "not recognised"
> and vectors SEND/RECVE/GETINF/WHOLE to ILLEG.

So the difference is **not** cosmetic and not a mere recompile:

| | A series (generation 406) | B series (generation 500) |
|---|---|---|
| ACCP primitive layer | identical | identical |
| NUCLEUS message instructions `SEND` / `RECVE` / `GETINF` / `WHOLE` | **vector to ILLEG** (illegal instruction) | fully implemented |
| `MHOLE`, `LOCK_DH` spin-locks, `NK_TRACE`, `SENKICK` | absent | present |
| Octobus kicks 3-6 | stubbed, "not recognised" | real handlers |

### 32.1 This joins up three separate findings  [D - but a strong join]

- **The NUCLEUS instructions are '87 extensions.** `SEND`, `RECVE`, `RHOLE`, `WHOLE` are four
  of the 25 instructions listed in PART 2 section 10. So **a subset of the '87 extension
  instruction set exists only under work mode 500** - on a generation-406 machine those
  opcodes trap. Anyone documenting the ND-5000 instruction set needs to say which work mode
  they mean.
- **It explains `CHANGE-CPU`.** PART 5 section 26.1 noted that moving a process between CPUs
  on a multi-CPU ND-5900 "runs only from SINTRAN work mode 500". Now the reason is visible:
  the multiprocessor nucleus is only in the B microcode. A 406 machine physically cannot do
  it.
- **It explains why the ND-5900 needs generation 500** and, by extension, why generation 406
  had no future once multi-CPU systems became the top of the range.

**Emulation consequence:** `CpuND5000` runs B30, so it has the full NK nucleus. Any test that
exercises `SEND`/`RECVE`/`GETINF`/`WHOLE` or kicks 3-6 is testing **work-mode-500 behaviour**
and would legitimately fail against an A image. Do not treat an A/B difference as a bug.

## 33. Smaller findings from this sweep  [DOC-manual]

- **Rallar is dated by the M-version.** M's section 1.4 "New hardware supported": "All
  ND-500/5000 systems, **including the new ND-5830 and ND-5850 systems**, are supported by the
  M-version of SINTRAN III." M is January 1990. So the Rallar machines were **new around
  1989-1990** - the first dating evidence for Rallar anywhere in this repo. (PART 3 section 19
  dates the ND-5900 to 1988; Rallar is roughly two years later.)
- **N shipped new microcode for exactly four machines**: "One diskette containing new
  microprograms for ND-5850, ND-5830, ND-5800 and ND-5700." The 5200/5400/5500 kept revision
  33 numbers in the table but were not on the new-microcode diskette.
- **The ND-5000 memory ceiling moved in L**: "The previous limitation of memory size to 32
  megabytes was changed to 128 megabytes on ND-5000 systems in the L-version of SINTRAN III.
  This new limit (128 megabytes) now applies to all ND-500/5000 systems." (M manual,
  section 1.5.)
- **Patch-file levels are tied to generations**: M generation 6 requires patch level >= 4000;
  N generation 1 requires patch level >= 1000. Product descriptions that say
  "SINTRAN-III >= L Workmode 7 / >= 4000" are quoting a work mode and a patch level together.
- **A "workmode 405" appears once**, in `Installation\Product-Info\ND-211154-A1-EN.md`
  ("For ND-500/5000 - SINTRAN III VSX version K, workmode 405 or later", twice). 405 is in no
  other document and is not in [K5]'s generation list. **Most likely an OCR error for 406**
  [D] - but flagged rather than silently corrected. **[?]**
- **N dropped standalone XMSG**: "remove any commands used to load and initialise XMSG to your
  system" when moving from K to N - XMSG became built in.

## 34. Additions to the open list

14. **Why the generation numbers run L=5..7, M=5..6, N=1.** Section 30.1. Scoped per version
    letter, but the sequence is not explained anywhere.
15. **"Workmode 405"** in ND-211154. Section 33. Probably OCR for 406, unconfirmed.
16. **We do not hold microcode revisions 31 (M-era) or 33 (N-era)** for any model, nor any
    Rallar image (12009 / 12011). Section 31.

---

# PART 7 - RALLAR IS "CPU TYPE IV", AND ND'S OWN PCB INDEX NAMES EVERY MODULE (added 2026-08-24)

**Source:** `E:\Dev\Ronny\mirror-sintran-com\mirror\hardware\hardware.js` lines **1060-1091**,
the PCB database index of norsk-data.com (Jonny Oddene / Sintran Data). Read directly and
quoted verbatim below - **not** taken on a subagent's word.

Grade: **[DOC-index]** - a maintained hardware index derived from ND part data, one step below
a printed ND manual but far above the community wiki. The per-PCB detail pages it links to are
**NOT in the mirror** (see section 38).

## 35. RALLAR IS THE FOURTH CPU TYPE  [DOC-index - big finding]

Part 1 and Part 2 treated Rallar as "a different processor, out of scope". The PCB index puts
it squarely in the same numbering as Samson:

```
320001 - PCB 5502 - N-5000 Basic CPU Type I   (Samson)
320002 - PCB 5502 - N-5000 Basic CPU Type II  (Samson)
320003 - PCB 5503 - N-5000 Basic CPU Type III (Samson)
320026 - PCB 6201 - N-5000 Basic CPU IV (Rallar) 25MHz 16MB
320027 - PCB 6201 - N-5000 Basic CPU IV (Rallar) 45MHz 16MB
320028 - PCB 6201 - N-5000 Basic CPU IV (Rallar) 45MHz 8MB
320034 - PCB 6201 - N-5000 Basic CPU IV (Rallar) 45MHz 32MB
320035 - PCB 6201 - N-5000 Basic CPU IV (Rallar) 45MHz 64MB
```

**Rallar = "N-5000 Basic CPU IV".** It is not a separate product line beside the ND-5000, it is
the fourth CPU type *within* it - which is why ND-895560 lists ND-5830/5850 in the same ES
model codes (S11/C11/L11) as the Samson machines, and why the M-version of SINTRAN supports
"all ND-500/5000 systems, including the new ND-5830 and ND-5850".

### 35.1 Rallar variants are distinguished by CLOCK and LOCAL MEMORY  [DOC-index]

| Part | PCB | Clock | Local memory |
|---|---|---|---|
| 320026 | 6201 | **25 MHz** | 16 MB |
| 320027 | 6201 | **45 MHz** | 16 MB |
| 320028 | 6201 | **45 MHz** | 8 MB |
| 320034 | 6201 | **45 MHz** | 32 MB |
| 320035 | 6201 | **45 MHz** | 64 MB |

Two clock speeds, 25 and 45 MHz, and four local-memory sizes. This is the **first hard
performance data on Rallar** anywhere in our material.

For scale, Samson's master clock is quoted in the manuals as 70 ns "normal" or 156 ns "slow"
(PART 2 section 11.1). **Do not naively convert** 70 ns to 14.3 MHz and compare it with
Rallar's 45 MHz as though they were the same measurement - the manuals call 70 ns a *master
clock period* and never state a Samson CPU clock frequency. The two numbers are stated in
different units by different sources. **[?]** What is safe to say is that Rallar is specified
by CPU frequency in MHz while Samson was specified by master-clock period in ns, and that this
is a generational change in how ND described the part.

Note also that Rallar carries **local memory on the CPU assembly itself** (8/16/32/64 MB in
the part description). This matches the SINTRAN M/N release notes quoted in PART 2 section 9.3
about "own CPU memory on the ND-5830/5850" being exhausted, and "Error if ND-5830 or ND-5850
CPU and extra MF-memory".

### 35.2 The Rallar module set  [DOC-index]

```
350401 - PCB 6201 - Rallar motherboard
350402 - PCB 6202 - Rallar 8 MB local memory
350403 - PCB 6203 - Rallar CPU
350404 - PCB 6204 - Rallar ICA
350405 - PCB 6205 - Rallar DCA
350406 - PCB 6206 - Rallar RAAP
350412 - PCB 6212 - Rallar CPU
```

A PCB 62xx series, entirely separate from Samson's 55xx/56xx. **Seven modules against
Samson's ten.**

**ICA and DCA are not expanded anywhere in the index.** Plausibly instruction- and data-cache
modules by position against the Samson set, but **that is a guess from naming symmetry and
nothing more. [?]**

**`RAAP` IS expanded elsewhere in the archive: "Rallar Additional Arithmetic Processor"** -
see PART 8 section 41.

KUSK and GAMP do not appear in *this* index - it names modules, not the chips on them.
**They are confirmed elsewhere in the same archive: see PART 8 section 41, which also settles
what RAAP stands for and names a third gate array.**

## 36. ND'S OWN NAMES FOR EVERY SAMSON MODULE  [DOC-index - confirms PART 2 section 5.1]

```
324602 - PCB 5502 - Samson motherboard
324603 - PCB 5503 - Samson motherboard, 58xx
324701 - PCB 5601 - Samson instruction/data Memory Management System controller (MMS) module
324702 - PCB 5602 - Samson ACCess Processor (ACCP) module
324704 - PCB 5604 - Samson Arithmetic and Logical Unit (ALU) module
324707 - PCB 5607 - Samson Control Store - 16K (CS) module
324708 - PCB 5608 - Samson Instruction/Data Address controller (IDA) module
324709 - PCB 5609 - Samson Micro Instruction Controller (MIC) module
324710 - PCB 5610 - Samson Instruction/Data cache (CACHE) module
324714 - PCB 5614 - Samson I-level Data Address Controller (IDAC) booster module
324715 - PCB 5615 - Samson Additional Arithmetic Processor (AAP) module
324716 - PCB 5616 - Samson ACCess Processor (ACCP) module
324717 - PCB 5617 - Samson Instruction/Data cache (CACHE) module
324718 - PCB 5618 - Samson Instruction/Data Address controller (IDA) module
324913 - PCB 5913 - Samson dummy module
324914 - PCB 5914 - Samson dummy module
350162 - PCB 5604 - Samson Arithmetic and Logical Unit (ALU) module
```

Every part number and expansion matches the ND-05.017.01 tables transcribed in PART 2
section 5.1 exactly. New information beyond those tables:

1. **PCB numbers**, which the maintenance manual does not give: part `3247nn` maps to
   `PCB 56nn`, and the CPU assemblies to PCB 5502 (types I and II) and 5503 (type III). Note
   type I and type II share PCB 5502 - consistent with the manual's "CPU types 1 and 2 use the
   same mother board".
2. **`324716` is confirmed as a second ACCP part on PCB 5616**, alongside `324702` on PCB 5602.
   This is the card we hold an EPROM dump of
   (`Installation\Communication\OctobusAccp\`) - **the index independently confirms it is a
   Samson ACCP module**, closing the `[?]` raised in PART 4 section 21 about whether 324716
   belongs to this family. Which models shipped which part is still open.
3. **`350162` is a second ALU part sharing PCB 5604** with `324704` - a later build of the same
   board [D].
4. **`324913` / `324914` "Samson dummy module"** - filler cards for unused baby-module
   positions. Not mentioned in any manual we have.

## 37. "SAMSON CONSOLE PRINT" IDENTIFIED, plus two cabinet code names  [DOC-index]

The wiki upgrade procedure for ND-5800 -> ND-5900 says "Insert **'Samson console print'**
behind each extra ND-5000 CPU" without saying what it is. The index has it (lines 1218-1226,
1136-1138, and the MFB section):

```
324195 - PCB 5235 - Samson Console
324196 - PCB 5236 - Samson Console Comson
324194 - PCB 5234 - Maxson MFB Console/Octobus plug board
324904 - PCB 5904 - Plug board 1, Samson-C
324905 - PCB 5905 - Plug board 2, Samson-C
324908 - PCB 5908 - Plug board 3, Samson-C, Ethernet/Ethernet
350150 - PCB 5908 - Plug board 3, Samson-C, Token ring/Ethernet
350151 - PCB 5908 - Plug board 3, Samson-C, Token ring/Token ring
```

So the "console print" is a real plug board, part **324195** (PCB 5235), with a Comson variant
**324196**. `324194` is the combined **MFB Console/Octobus plug board**.

**Two cabinet/system code names appear that are NOT the CPU name:**

- **MAXSON** - the large-cabinet ND-5000. From the assembly-drawing titles in
  `data\libhw.js`: "Book 2: **ND-5000 (MAXSON)** 11-Mod.Cab. '85, Main Assy" (ND-B2C16) and
  "Book 2: ND-5000 (MAXSON) 11-Mod.Cab. '85, Cable Info. Block & Wiring Diagrams" (ND-B2C17).
- **COMSON** - the compact. "Book 2: **ND-100/5000 COMPACT (COMSON)**, Assembly Drawings"
  (ND-B2C8).

**Do not confuse these with Samson.** Samson is the CPU; Maxson and Comson are the machine
builds it goes into. "Samson-C" on the plug boards is a further variant marker whose expansion
is **not stated** anywhere in the index. **[?]**

## 38. THE MODULE DETAIL PAGES ARE MISSING FROM THE MIRROR  [action item]

Every row above links to a page `nd-5000/nd-3247xx.html`, and
**`mirror\hardware\nd-5000\` does not exist**. `mirror\hardware\hw-pcb.html` describes these
per-PCB pages as carrying "Configuration info and switch settings together with some tips and
tricks".

**This is live content on norsk-data.com that our mirror never fetched.** The highest-value
targets, given the ACCP and octobus work in this folder:

- `http://norsk-data.com/hardware/nd-5000/nd-324702.html` (ACCP)
- `http://norsk-data.com/hardware/nd-5000/nd-324716.html` (ACCP, the card we have dumped)
- `http://norsk-data.com/hardware/nd-5000/nd-350403.html` and `nd-350412.html` (Rallar CPU)
- `http://norsk-data.com/hardware/nd-5000/nd-320027.html` (Rallar CPU IV assembly)

Rows prefixed `@` in the index (320026, 320028, 320034, 320035) are marked as having no page at
all, so only 320027 of the five Rallar assemblies is documented.

## 39. `ND-820060.1 RALLAR Design Information` EXISTS AND IS NOT AVAILABLE  [DOC-index]

`E:\Dev\Ronny\mirror-sintran-com\data\libhw.js` line **380**, verbatim:

```
libHW.push(['I', '820060.1', 'EN', '1990', 0, 0, 'No', 'HW', '@ND-820060-1-EN.pdf', 'RALLAR Design Information']);
```

Section `(20) Internal System Documentation`. Dated **1990**, **0 pages, 0 bytes, availability
`No`**, filename prefixed `@` meaning no file exists.

**This is the Rallar design document.** It is catalogued but was never scanned. If it ever
surfaces it would answer KUSK/GAMP and the ICA/DCA/RAAP expansions in one go. Also
catalogued-but-absent and relevant: **`830103.01 ND-5000 ES Model S Hardware Maintenance`**
(`libhw.js` line 525) and `30.073.01 NORD-5000 Macrotest Description`.

## 40. Additions to the open list

17. **What ICA, DCA and RAAP stand for.** Section 35.2. Naming symmetry suggests answers; no
    source states them.
18. **Whether Rallar's 45 MHz is comparable to Samson's 70 ns master clock.** Section 35.1.
    Different units from different sources.
19. **What "Samson-C" means** on the plug boards. Section 37.
20. **Which models shipped ACCP 324702 versus 324716.** Still open from PART 4 section 21,
    though 324716 is now confirmed to be a Samson ACCP.
21. **`mirror\hardware\nd-5000\*.html` was never fetched.** Section 38 - a re-crawl target, not
    a research question.

---

# PART 8 - KUSK/GAMP CONFIRMED, AND "MIPS" MEANT WHETSTONE ALL ALONG (added 2026-08-24)

Everything in this part was **read and verified directly** by me in the source file or the
rendered PDF page - not accepted on a subagent's report.

## 41. KUSK, GAMP AND A THIRD CHIP - CONFIRMED  [DOC-index]

**Source:** `E:\Dev\Ronny\mirror-sintran-com\mirror\history\giveaway\giveaway.js`, lines
**460-472**. This is the collectibles catalogue of the sintran.com archive maintainer
(Jonny Oddene, ex-ND), describing physical chips he holds. Verbatim:

```
giveaway.push(['N', ['ng0074.jpg'], '1989', 'JOO', '47 x 47 mm', 1, 'ND chip',
   ['Dolphin chip used on the Rallar CPU, GAMP',
    'Found on Rallar CPU module ND-350403 or ND-350412',
    'This is the work "horse" chip in the Rallar CPU']]);
giveaway.push(['N', ['ng0073.jpg'], '1989', 'JOO', '47 x 47 mm', 1, 'ND chip',
   ['Dolphin chip used on the Rallar CPU, KUSK',
    'Found on Rallar CPU module ND-350403 or ND-350412',
    'This is the controlling "kusk" chip in the Rallar CPU']]);
giveaway.push(['N', ['ng0072.jpg'], '1995', 'JOO', '42 x 42 mm', 4, 'ND chip',
   ['Dolphin chip used on the Rallar CPU, DSB',
    'Found on RAAP module (Rallar Additional Arithmetic Processor) ND-350406',
    'This chip takes care of division, square root and BCD arithmetic']]);
```

**This closes open item 4 (KUSK/GAMP) and open item 17 (RAAP).** New facts:

| Chip | Size | Dated | Module | Role, verbatim |
|---|---|---|---|---|
| **GAMP** | 47 x 47 mm | 1989 | 350403 / 350412 (Rallar CPU) | "the work **horse** chip" |
| **KUSK** | 47 x 47 mm | 1989 | 350403 / 350412 (Rallar CPU) | "the controlling **kusk** chip" |
| **DSB** | 42 x 42 mm | 1995 | 350406 (RAAP) | "division, square root and BCD arithmetic" |

1. **A THIRD Rallar gate array exists: `DSB`**, on the RAAP module - not in the wiki, not in
   any manual. Its listed role (division, square root, BCD) reads as an initialism of those
   functions, but the source does not expand it. **[?]**
2. **`RAAP` = "Rallar Additional Arithmetic Processor"**, stated outright. The Samson analogue
   is AAP, part 324715.
3. **They are "Dolphin chips"** - i.e. Dolphin Server Technology, the company formed from ND's
   assets. Consistent with the 1989/1995 dates and with Rallar being the last generation.
4. The "jockey / horse" gloss in the community wiki is **corroborated in substance** but the
   source does not translate the words: it says GAMP is the work "horse" and KUSK the
   controlling "kusk". (In Norwegian *kusk* = driver/coachman and *gamp* = a workhorse/nag.)

**Caveats, stated plainly:**
- This is a **collector's catalogue entry, not an ND document.** Grade **[DOC-index]**. It is
  written by someone who worked at ND and holds the parts, which is strong - but it is not a
  printed ND specification.
- **The photographs ng0072/ng0073/ng0074.jpg were never downloaded** - `mirror\history\
  giveaway\` holds only the HTML and the .js. Re-crawl target.
- **KUSK and GAMP appear in ZERO PDF text anywhere in the 7.3 GB archive.** A raw byte-level
  grep hit ~30 PDFs but every one was compressed-stream noise; the one near-miss in extracted
  OCR text was "An e**gamp**le" in `ND-30.024.02`. So: confirmed, but from exactly one source.

### 41.1 Samson's gate arrays, for symmetry  [DOC-index]

`E:\Dev\Ronny\mirror-sintran-com\mirror\hardware\hw-utility\hw-components\components.js`
lines 56-59 - an ND component stock list. Verbatim descriptions:

```
516117  Gate Array ND-IMU    Samson Gate Array ND-IMU-L5A0560
516118  Gate Array ND-1364   Samson Gate Array ND-1364A
516119  Gate Array ND-1365   Samson Gate Array ND-1365B
516119B Gate Array ND-1365   Samson Gate Array ND-1365B, marked Weitek
```

**Samson's gate arrays are ND-IMU, ND-1364 and ND-1365** - and one ND-1365B variant is
**"marked Weitek"**, i.e. ND was sourcing (or second-sourcing) from Weitek, the floating-point
coprocessor house. Separately, `giveaway.js` records a 1987 chip photo captioned "One of the
chips on the ND-5800 CPU / Found on ND-324715 Samson Additional Arithmetic Processor (AAP)
module / **The Floating Point Unit (FPU) chip**". Consistent: the AAP carries a bought-in FPU.
All prices are in the stock list (ND-1364/1365 at 3787.50 each, ND-IMU at 991.95).

## 42. CORRECTION - ND's "MIPS" IS WHETSTONE MIPS  [V - verified on the page]

**This corrects PART 3 section 15 and everything downstream of it, including what was written
into the ndwiki article.**

`ND-05.020.01` says "Maximum performance for one CPU is 6-7 MIPS" and "up to 28 MIPS
(ND-5900 model 4 with four CPUs)". Part 3 read those as *native instruction rates*. **They are
not.**

`E:\Dev\Ronny\mirror-sintran-com\mirror\library\libsales\ND-SID001-A1-EN.pdf`
("ND-5000 series", Sales Information Document, COMPANY CONFIDENTIAL, Corporate Marketing,
December 1986), **printed page 12, section 3.3 "Whetstone ratings"** - I read the rendered
page myself. Header text verbatim: *"These are the expected Whetstone ratings without
optimized Fortran."* Bar chart, axis labelled **WMIPS**:

| Model | WMIPS |
|---|---|
| ND-5700 | 3-3.5 |
| ND-5800 | **6-7** |
| ND-5900 Mod.2 | 12-14 |
| ND-5900 Mod.3 | 18-21 |
| ND-5900 Mod.4 | **24-28** |

**6-7 and 24-28 are exactly the Hardware Description's "6-7 MIPS" and "up to 28 MIPS".** The
Hardware Description is quoting the Whetstone figures with the "W" dropped. ND's unqualified
"MIPS" for the ND-5000 means **Whetstone MIPS**, a floating-point measure - not an instruction
rate.

This is corroborated by ND's own methodology document,
`E:\Dev\Ronny\mirror-sintran-com\mirror\library\libsw\ND-HW-02-EN.pdf` - "ND COMPETITION
NEWSLETTER / CPU SPEED COMPARISONS-MINI AND UPWARDS / DECEMBER 1983 / CORPORATE MARKETING",
which defines MIPS, Whetstone MIPS, KOPS and FLOPS separately and states that *"globally
optimized Whetstone-figures have not been used, as they tell more about the FORTRAN-compiler
than the hardware speed"* - the same caveat SID001 repeats.

### 42.1 Consequence for the Dhrystone number  [D]

PART 3 section 16 derived **~3.7 DMIPS** for one CPU from the measured 6553 dhrystones/second
in ND-05.017.01. That stands - but it is now clear the two figures measure **different
things**:

- **6-7 WMIPS** = Whetstone, floating point (and the ND-5000 has a dedicated AAP for FP).
- **~3.7 DMIPS** = Dhrystone, integer and string, no floating point at all.

A machine with a hardware FP coprocessor scoring roughly twice as well on Whetstone as on
Dhrystone is entirely coherent. **Both numbers are right; neither is "the" performance.** Do
not average them, and never quote one as if it were the other.

## 43. ND'S OWN COMPETITOR TABLE - on a consistent Whetstone basis  [V - verified on the page]

SID001 **printed page 16, section 5 "COMPETETIVE POSITIONING"** (ND's spelling), verbatim
lead: *"Here we have listed some of our major competitors."* Four tables; the first row of
each is **"Whetstone MIPS"** - so ND compared every vendor on the same basis. I read the page
myself. The DEC columns:

| Machine | Whetstone MIPS |
|---|---|
| VAX-8200 | 1.1 |
| VAX-8300 | 1.9 |
| VAX-8500 | 3 |
| VAX-8550 | 6.8 |
| VAX-8600 | 4.4 |
| VAX-8650 | 6.8 |
| VAX-8700 | 6.8 |
| VAX-8800 | **11** |

Against ND's own row: **ND-5700 3-3.5, ND-5800 6-7, ND-5900 Mod.2 12-14, Mod.3 18-21,
Mod.4 24-28.**

Other vendors on the same page: HP-3000 70 = 1.8, 930 = 4.5, 950 = 6.7; PRIME 9750 = 1.7,
9950 = 2.5, 9955 = 4; IBM-4381-12 = 2.7, -13 = 3.5, -14 = 6, IBM 9373-20/40/60 = 0.5/0.5/1.3,
9373-90 = 2.6; WANG VS 100 = 1.3, VS 200 = 3.3. Footnotes flag the HP SPECTRUM 930/950 and the
IBM 9370 series as not yet shipping, and mark several VAX models "@ Not upgradeable".

**Reading, on ND's own consistent basis:**
- A single **ND-5800 (6-7)** sits level with a **VAX-8550 / 8650 / 8700 (6.8)** and above a
  **VAX-8600 (4.4)**.
- A single **ND-5800 does NOT reach a VAX-8800 (11)**.
- The four-CPU **ND-5900 Mod.4 (24-28)** is about **2.3x a VAX-8800** - the only ND
  configuration that beats DEC's top machine in this table.
- **ND-5700 (3-3.5)** is about a **VAX-8500 (3)**.

This supersedes the borrowed VUP figures written into PART 3 section 17. **Use this table
instead** - it is a primary ND document, internally consistent, and every machine on it is
measured the same way. The earlier PDP-11/MicroVAX/VUP table was general knowledge with no
source in this archive and should be treated as background only.

### 43.1 The ADP/OA ladder and the ND-570/CX crossover  [V - verified on the page]

SID001 **printed page 13, section 3.4**, verbatim table (a red pen has struck through the
ND-5700 row on the scan):

| System | ADP/OA | WMIPS | No. of users |
|---|---|---|---|
| 510/CX | 1.0 | 0.4 | 12-14 |
| 530/CX | 1.6 | 0.6 | 19-22 |
| 550/CX | 2.1 | 1.2 | 28-32 |
| 560/CX | 3.8 | 2.1 | 46-53 |
| 570/CX | 5.9 | 3.2 | 71-83 |
| 5700 | *5.9, struck through* | | *71-83, struck through* |
| 5800 | 7.4 | | 89-104 (25% more than 570/CX) |

Section 3.2 gives the ADP ladder against ND-100/CX = 1: **100/CX 1.0, 560/CX 3.8, ND-5700 5.9,
ND-5800 7.4**. And page 2 states: *"ND-5700 has approximately the same CPU performance as the
ND-570/CX and the ND-5800 has approximately twice the performance of the ND-570/CX. Hence the
ND-570/CX will be replaced by the ND-5700. ND-5900 Model 2, 3 and 4 have respectively two,
three and four times the performance of the ND-5800."*

That confirms the wiki's claim "the single processor ND-5700 system has the same computational
power as an ND-570 system" **from a primary ND source**.

Note there are now **three different relative-performance baselines** in circulation - ND-100/CX
= 1 (SID001 3.2), ND-570/CX-relative prose, and ND-5200 = 1 (the 1988 ES sheet, PART 3
section 18). **Never mix them.**

## 44. THE ND-5000 ANNOUNCEMENT DATE - SETTLED  [V - verified on the page]

SID001 **printed page 20, section 7.1 "Release/Delivery times"**, verbatim:

> "**Corporate External release is set for the 27. January 1987.**
> First delivery is expected in 2. quarter of 1987 ~~and then the ND-570/CX will be phased
> out.~~"  *(the strike-through is red pen on the scan)*

The document itself is **December 1986** and covers **ND-5700, ND-5800 and ND-5900 Models
2/3/4 by name**, with performance figures and part numbers.

**This moves the ND-5900 bound from "documented by April-June 1988" (PART 3 section 19) back
to announced 27 January 1987, documented December 1986** - about fifteen months earlier. The
ND-5900 was announced *with* the ND-5700 and ND-5800, as one family, which settles the
[D] reading in PART 3 section 19.

Section 7.3 "Material available" also lists a **Press Release, "New High-End Series from Norsk
Data"** - which is **not in the archive**, and is now the single most wanted ND-5000 document.

## 45. Corrections and closures this part makes

| Item | Was | Now |
|---|---|---|
| PART 3 section 15 | "6-7 MIPS is a native instruction rate" | **WRONG** - it is Whetstone MIPS (section 42) |
| PART 3 section 17 | borrowed VUP figures, no source | **superseded** by ND's own Whetstone table (section 43) |
| PART 3 section 19 | ND-5900 documented by April-June 1988 | **announced 27 January 1987** (section 44) |
| Open item 4 (KUSK/GAMP) | unconfirmed, community wiki only | **CONFIRMED** + a third chip, DSB (section 41) |
| Open item 17 (RAAP) | guess | **"Rallar Additional Arithmetic Processor"**, stated (section 41) |
| PART 7 section 35.1 | Rallar clock vs Samson clock incomparable | still true, but section 43 gives a **benchmark** basis instead |

## 46. Additions to the open list

22. **Which CPU model produced the 6553 dhrystones/second.** Still open - the archive has
    **zero** occurrences of "Dhrystone", "Linpack", "MFLOPS" or "VUP" in any searchable text.
    ND-05.017.01 remains the only source and it does not say.
23. **Press Release "New High-End Series from Norsk Data"** - proven to exist (SID001 7.3),
    absent from the archive.
24. **`ND-05.021 SAMSON Design Information`** - cited in the Related Manuals list of
    `ND-05.022.1 ND-5000 Microprogram Guide`, **not in the sintran.com index at all**, so not
    even on its wishlist. The Samson counterpart of `ND-820060.1 RALLAR Design Information`.
25. **`ND-SAMSON-1-EN.pdf` "Expected Samson Behaviour"** (June **1983**, 95 pages) IS
    downloaded at `mirror\library\libsw\ND-SAMSON-1-EN.pdf` but is **image-only with no text
    layer**. A 1983 Samson design-era document - by date the earliest Samson material known.
    **OCR candidate #1.**
26. **The four `06.DEL.*` Delilah manuals** (Circuit Diagrams, Hardware Introduction, Design
    Documents, Schematics - **639 pages total**, Jan 1987 to Jan 1988) are downloaded at
    `mirror\library\libhw\ND-06DEL-*.pdf` and are **all image-only**. The largest body of
    unsearchable primary material touching this work.
27. **Archive-wide coverage limit:** of 4,014 PDFs in the mirror, only ~212 have a real text
    layer - about **5%**. Every "zero hits" result in Parts 7 and 8 is therefore "not found in
    the 5% that is searchable plus all titles and indexes", **not** "not present".

---

# PART 9 - "EXPECTED SAMSON BEHAVIOUR" (1983): THE DESIGN SPEC WE DID NOT KNOW WE HAD (added 2026-08-24)

**All of this was read by me directly from the rendered PDF pages.** The file has no text
layer, so a keyword search will never find any of it.

**File:** `E:\Dev\Ronny\mirror-sintran-com\mirror\library\libsw\ND-SAMSON-1-EN.pdf`
(3,174,340 bytes, 95 pages). Catalogue no. `SAMSON.1`, **June 1983**, flagged `Incomplete` in
the index. **It is already on disk.**

## 47. What the document is  [V - read from page 1]

Verbatim, page 1:

> "The **SAMSON project** aims at developing a new CPU in the family of ND computer systems.
> The instruction set is the same as implemented in **ND-500/GEPETTO**, with a few minor
> extensions. A main design goal is to increase the computation speed for the top model of the
> line. It is also considered important to decrease the complexity, the component cost and the
> production cost of the ND-500 concept. These goals should be obtained by utilizing new
> technology where possible, and by shrinking the physical dimensions of the CPU to diminish
> signal propagation delays. Extensive pipelining techniques, as used in ND-500/GEPETTO, will
> be employed."
>
> "This document ... is primarily intended to be a guide for the designers involved within the
> SAMSON project."
>
> "This document will be far from finished when it is released for the first time."

**This is Norsk Data's internal SAMSON design specification, dated four years before the
product shipped.** It is a draft, by its own admission.

### 47.1 A new ND code name: GEPETTO  [V]

**`GEPETTO` is the code name of the classic ND-500**, stated twice on page 1 as
"ND-500/GEPETTO". Not in the community wiki, not in any manual we hold. Add it to the code-name
set alongside Samson (ND-5000 CPU), Rallar (CPU IV), Delilah (ND-120), Maxson (ND-5000 large
cabinet) and Comson (ND-100/5000 Compact).

### 47.2 Chapter list  [V - read from page 2]

```
1. General Description              8. External Control
2. Macro Instruction Pipelining     9. Memory Management
3. ALU and Registers               10. Physical Caches
4. Logical Data Cache              11. Multiport Memory Interface
5. Logical Instruction Caches      12. Timing
6. Micro Instruction               13. Additional Arithmetical Processors
7. Trap System
```

## 48. THE CONTROL STORE GEOMETRY, CONFIRMED FROM A DESIGN DOCUMENT  [V]

Page 4, verbatim:

> "The operations of the ALU, the selections of WRF registers and several other functions, are
> controlled by a microprogram that resides in a **control store (CS). CS consists of RAM, and
> is organized as 16K words with a word width of 128 bits.** The address of the CS is generated
> by a microprogram sequencer, **MIC**. The MIC has ability to sequence and branch through the
> microprogram in CS, and it is controlled by the trap system (TRP)."

**This independently confirms, from a 1983 ND design document, the geometry PART 4 section 23
derived from the binaries** (16384 words x 128 bits = 262144 bytes per image). Two derivations,
four years and one medium apart, agreeing exactly. The control store is **RAM**, not ROM -
consistent with it being loaded from a `CONTROL-STORE:DATA` file at boot.

## 49. THE ARCHITECTURE BLOCK NAMES - directly useful to the emulator  [V - read from page 4]

Page 4 names the whole datapath. Every one of these is an object we either model or have
wondered about:

| Block | Page-4 description, verbatim or close |
|---|---|
| **WRF** | "working register file ... holds a small number of 32-bit registers" |
| **SRF** | "scratch register file", used "when more extensive storage is needed" |
| **ALU** | operates on A and B operands; results go "on the F BUS, which spreads to several destinations, most notably back to the WRF" |
| **AAP** | "additional arithmetical processors ... results from AAP are routed through the ALU" |
| **CS / MIC / TRP** | control store, microprogram sequencer, trap system (section 48) |
| **IAC / DAC** | "instruction memory controller (IAC) and the data memory controller (DAC) ... generate addresses used to address the instruction and data memory respectively" |
| **DLC** | "data logical cache" |
| **ILC** | "instruction logical caches", "further divided into the **instruction cache (ICA)** and the **operand cache (OCA)**" |
| **IMDB / DMDB** | "memory data bus" - instruction and data |
| **IMM / DMM** | "memory management units ... connected to the memory data buses" |
| **IPC / DPC** | "optional **physical** cache systems" |
| **MPC / MPM** | "multiport memory controllers (MPC)", "the multiport memory (MPM) must then provide the needed data" |
| **CON** | control processors - see section 50 |
| **OCT** | octobus interfaces - see section 50 |
| **ACC** | the access module - see section 50 |

Verbatim on the DAC: "In order to calculate operand addresses in a fast and easy manner, the
DAC contains the B and R registers, and copies of the 4 index registers."

**Note `ICA` = instruction cache and `OCA` = operand cache in SAMSON.** Rallar's module set
(PART 7 section 35.2) has boards named **ICA** and **DCA**. That makes "ICA = instruction
cache" very likely on Rallar too, with DCA the data counterpart - but Samson also has an `IAC`
and a `DAC` (address controllers), so the letters are genuinely ambiguous. **Still [?], but
much better grounded than before.**

## 50. THE OCTOBUS CONTROL ARCHITECTURE, DESCRIBED IN 1983  [V - read from page 4]

This is the passage that matters most for the octobus and ACCP work in this folder. Verbatim:

> "There are **two control processors (CON)** interfaced with the SAMSON CPU. One is needed to
> perform cold-start bootstrapping, test functions and to control tracing functions inside
> SAMSON. The other will be involved in I/O-functions and other run-time communication tasks.
> The **CON-processors (which in the first systems will be 1 or 2 ND-100 computers)** perform
> their control through **octobus interfaces (OCT)**. Special hardwired functions in the first
> system and in the **access module (ACC)** makes it possible to bootstrap or test different
> circuits in the SAMSON CPU **before the microprogram starts running**. The main hardware
> feature responsible for this is the possibility to read and write a long shift register that
> consists of ..." *(continues past the page break)*

Four things this settles or sharpens:

1. **The access module (ACC) is in the design from 1983** and its stated purpose is to
   bootstrap and test the CPU *before the microprogram runs*. That is exactly the role our ACCP
   work has reconstructed from the firmware.
2. **The control path was designed as one or two ND-100s over octobus** - matching the
   ND-100-as-I/O-processor model throughout the family.
3. **Two CON processors were intended**, split bootstrap/test/trace versus I/O and run-time
   communication. Whether shipped systems used two is **not stated here** and we have not seen
   it elsewhere. **[?]**
4. **A "long shift register" is the bootstrap/test mechanism.** A scan chain, in modern terms.
   This is a concrete lead for anyone working on ACCP bring-up. The description continues past
   page 4 - **unread**.

**91 of the 95 pages are unread.** Chapters 6 (Micro Instruction), 8 (External Control),
11 (Multiport Memory Interface) and 13 (Additional Arithmetical Processors) are all directly on
top of open questions in this folder.

## 51. THE TEST MICROPROGRAMS PRODUCT - we already hold it  [V]

`E:\Dev\Ronny\mirror-sintran-com\mirror\library\libswpdpi\ND-211124-2-EN.pdf` is the PROGRAM
DESCRIPTION for **"ND-5000 Test Microprograms", Reg. no. 211124B, dated 88.04.12**. Its file
manifest lists fifteen microtests as `TEST` / `LABE` / `DATA` triplets.

**Every one of them is already on disk in `E:\Dev\Ronny\ND5000UC\` at revision B00** - I
checked: `ALU-VERIFY`, `MIC-REGISTER`, `MIC-SEQUENCE`, `ALU-CARD`, `CACHE-TEST`, `IAC-TEST`,
`DAC-TEST`, `BOOSTER-TEST`, `IDU-REGISTER`, `IDA-VERIFY`, `DMM-REGISTER`, `IMM-REGISTER`,
`MM-VERIFY`, `AAP1-2-TEST`, `AAP2-VERIFY`, all `.DATA`.

**So the ND5000UC corpus contains the complete ND-5000 Test Microprograms product, and we now
have its product sheet.** Note the block names map straight onto section 49: IAC, DAC, IDU,
IMM, DMM, AAP, CACHE, BOOSTER (= IDAC).

Other facts from that sheet, verbatim where quoted:

- Source register number is **`250245B`** - *not* 250291 as recorded in Part 1 section 1.7.
  250291D was read from `5800-30.TEXT` for the **microprogram** product 211276D; 250245B is
  the **test microprogram** product's source. Two different products. **No contradiction, but
  do not conflate them.**
- Prerequisite: `ND-5000 All All SIN III VSX/500 K **Work mode 406**`, and
  "This version needs work mode 406, or newer, of SINTRAN for ND-5000."
- **"The ACCP PROMS should be dated 06.07.87 or later."** A dated ACCP firmware requirement -
  relevant to the EPROM dump in `Installation\Communication\OctobusAccp\`. **[?]** whether our
  dump satisfies it is unknown.
- `CHANGE-CPU` for multi-CPU ND-5900 "runs only from SINTRAN work mode 500" - the third
  independent source for the fact in PART 5 section 26.1.
- `LOOK-AT-CONTROL-STORE` has a **disassembler**, and rev B "is now able to disassemble the
  mnemonic `NEXT*`".
- Documentation cross-references: **`SEMICS User Guide` ND-20.024.2** and **`TPE Monitor User
  Guide` ND-30.105.1**. Neither is in the sintran.com archive at all - not held, not even
  wishlisted. These are the manuals that document the control-store disassembler.

## 52. Media that exists at DDHF and is NOT in the mirror  [DOC-index]

`E:\Dev\Ronny\mirror-sintran-com\mirror\software\software.js` lines ~700-737 hold a
**commented-out** block of Datamuseum "Bits" IDs, invisible to the mirror's inventory builder:

```
Bits:30001652   BINARY   1,310,720   211274A - ND-5500 MICRO-PROGRAM
Bits:30001653   PNG      1,842,165   211274A - ND-5500 MICRO-PROGRAM   (diskette label photo)
Bits:30001684   BINARY   1,310,720   250247A - ND-5000 Test Microprograms (1/2)
Bits:30001681   BINARY   1,310,720   250247A - ND-5000 Test Microprograms (2/2)
Bits:30001666            211034I  - ND-500/5000 SWAPPER
Bits:30001649            211305A  - ND-500/5000 System Package for SINTRAN III/VSX ver k, gen 500
```

**`211274A - ND-5500 MICRO-PROGRAM` is a 1.25 MB ND floppy image of a PRODUCT microprogram**
(211274 = the ND-5500 register number from PART 2 section 8), at
`http://datamuseum.dk/bits/30001652`. We hold `MIC-5500-90-500.DATA` already, but this is the
original distribution medium and may carry the `.LABE`/`.TEXT` companions and the label photo.

**The archive holds ZERO microcode binaries of its own** - no `.img`, `.IMD`, `.zip` or `.bin`
anywhere in the 7.3 GB tree. The `software.js` catalogue links to `.zip` media that was never
downloaded.

## 53. Coverage limit - read this before trusting any negative

Of **4,014 PDFs** in the mirror, only about **212 (5%)** have a real text layer - essentially
only the externally-OCR'd copies under `mirror\external\`. The entire `mirror\library\**` set
(~3,800 files) returns nothing but the scan watermark.

**Every "zero hits" statement in Parts 7, 8 and 9 means "not found in the 5% that is searchable,
plus all titles, filenames and index files" - never "not present".** Two of the most valuable
finds in this whole sweep (`Expected Samson Behaviour`, `ND-211124-2`) were invisible to text
search and were found by title, then read page by page as images.

Also beware: a raw byte-grep of scanned PDFs produces **false positives** inside compressed
image streams - part numbers like `211274` and `320001` "match" files that have no text at all.

## 54. OCR priority list, in order

1. **`mirror\library\libsw\ND-SAMSON-1-EN.pdf`** - Expected Samson Behaviour, 95 pp, 1983.
   The design spec. 91 pages unread.
2. **`mirror\library\libhw\ND-06DEL-*.pdf`** - the four Delilah manuals (Circuit Diagrams,
   Hardware Introduction, Design Documents, Schematics), **639 pages**, Jan 1987 - Jan 1988.
3. **`mirror\library\libhw\ND-05017-01B-EN.pdf`** - ND-5000 Hardware Maintenance **revision B**,
   294 pages, June 1988 - a later, larger revision than the 272-page copy we transcribed.
4. `mirror\library\libhw\ND-B2C17.pdf` (11 pp, cable/block/wiring) and `ND-B2C16.pdf`
   sub-chapter 6.
5. The nine `ND-NDSH0*.pdf` ND Service Handbooks.

## 55. Additions to the open list

28. **`GEPETTO`** - the ND-500 code name. Section 47.1. Seen once; look for corroboration.
29. **Whether shipped SAMSON systems used one or two CON processors.** Section 50.
30. **The "long shift register" scan-chain bootstrap mechanism.** Section 50 - description
    continues past page 4, unread.
31. **Whether our ACCP EPROM dump is dated 06.07.87 or later.** Section 51.
32. **`ND-20.024.2 SEMICS User Guide`** and **`ND-30.105.1 TPE Monitor User Guide`** - cited by
    ND-211124B, absent from the archive entirely.
33. **`ND-05.021 SAMSON Design Information`** - cited in the Related Manuals list of
    ND-05.022.1, absent from the archive index. Distinct from `SAMSON.1 Expected Samson
    Behaviour`, which we DO have.
