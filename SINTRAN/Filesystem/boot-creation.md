# Boot-sector creation - laying the page-0 bootstrap onto a bootable device

**Scope:** how the **raw bootstrap machine code** at the front of **page 0** of a
SINTRAN III directory device is produced, per device class, so an external
"create-directory" tool can emit a *bootable* image for floppy, SMD, Winchester,
or SCSI. This is the **boot half** of making a device. It is **separate from the
filesystem-structure creation** (label / extended info / bit file / object file /
user file), which is documented in [`create-directory.md`](create-directory.md).
The two are independent steps writing to disjoint parts of page 0 - see
[`on-disk-format/boot-sector.md`](on-disk-format/boot-sector.md) for the page-0
map and the boot-format detector.

**Rule of evidence** (same as the rest of the filesystem docs):

- **VERIFIED** - proven from real disk-image bytes, the ND-100 opcode table /
  disassembly, or official ND documentation.
- **INFERRED** - deduced from a driver source or a secondary source, not yet
  byte-proven from a real boot image of that exact device class.
- **OPEN** - not resolvable from the artifacts on hand; needs a specific missing
  image or file.

All ND-100 values are **octal**; on-disk multi-byte values are **big-endian**
(the ND-100 is a big-endian machine). The disassembler `nd100-dis` is
little-endian, so disk words are byte-swapped before decode; the swap is a tool
artifact only and never appears on disk.

---

## 1. Two independent steps: boot vs filesystem

Page 0 (2048 bytes / 1KW) is shared:

| Byte range | Word (octal) | Owned by | This document |
|------------|--------------|----------|---------------|
| 0 .. 1999 | 0B .. 1747B | **boot code** (BPUN / FLOMON / raw binary bootstrap, or zero) | **yes** |
| 2000 .. 2015 | 1750B | extended-info block (checksum, capacity) | no - see `create-directory.md` |
| 2016 .. 2047 | 1760B | master block / directory label | no - see `create-directory.md` |

A device can be:

- **filesystem + bootable** - both halves written (a system disk, e.g.
  `PACK-ONE`);
- **filesystem, not bootable** - boot area zero or space-filled (a data disk);
- **bootable, no filesystem** - e.g. a stand-alone FLOMON floppy that carries a
  bootstrap but no directory.

So the boot area is written by its **own** mechanism, quite apart from
`@CREATE-DIRECTORY`. The rest of this document is only about bytes 0 .. 1999.

---

## 2. The hardware that consumes the bootstrap (why the format is what it is)

The **ND-100 CPU firmware** (the OPCOM / operator's-communication microprogram)
is what actually loads the bootstrap. There are exactly **two** hardware load
formats (ND-06.014.2A, §4.2.5, "Bootstrap Loaders", VERIFIED):

1. **Binary format load** (bit 13 = 0). Reads an **ASCII-preamble + `!` +
   binary load record** stream from a **character/tape-style device** (the floppy
   controller presents itself this way). This is the **BPUN / FLOMON** family.
2. **Mass storage load** (bit 13 = 1). *"1K words will be read from mass storage
   address 0 into main memory starting in address 0. After a successful load, the
   CPU is started in main memory address 0."* (ND-06.014.2A §4.2.5.2, **VERIFIED**).
   This is the **raw binary bootstrap** family (SMD / Winchester / SCSI hard
   disks).

Which one runs is chosen by the **Automatic Load Descriptor (ALD)** thumbwheel
(or the typed `<addr>&` / `<addr>$`): bit 13 = mass-storage vs binary, bits 0-10 =
the controller's lowest device address (ND-06.014.2A §4.2.5.3). **VERIFIED** ALD
presets (ND-06.014.2A p.232, cross-checked against the nd100x emulator
`src/cpu/cpu_types.h` ALD table):

| ALD | Octal value | Load type | Device |
|-----|-------------|-----------|--------|
| 14 | `1560` | Binary load from 1560 | **Floppy** (BPUN/FLOMON) |
| 13 | `20500` | Mass-storage load from 500 | **Winchester** disk |
| 12 | `21540` | Mass-storage load from 1540 | **SMD** disk |
| 6  | `101560` | Binary load from 1560 | Floppy (SCSI systems often boot via a floppy first) |

**The consequence for the format** (VERIFIED):

- A **hard-disk bootstrap** must be a **raw ND-100 program occupying page 0**,
  because the firmware copies **exactly 1KW to address 0 and jumps to address 0**.
  There is no header, no checksum - word 0 is the first instruction executed.
  That is why every hard-disk boot area begins with `PIOF`/`IOF` (disable
  interrupts + paging) before touching the controller.
- Only **1KW** is loaded by firmware. A full system is far larger than 1KW, so the
  page-0 program is a **first-stage loader**: it programs its own controller to
  read the **second-stage** loader/system from later disk blocks into memory and
  jumps to it.
- A **floppy bootstrap** is a **BPUN stream** (preamble + `!` + load record),
  because the firmware runs the *binary-format* loader against the floppy
  controller.

---

## 3. SMD hard disk - **REAL bytes** (`SMD0.IMG` / `PACK-ONE`)

**VERIFIED** from `~/repos/nd100x/SMD0.IMG` (volume `PACK-ONE`). The page-0 boot
program is **byte-identical** in the sibling images `SMD0-org.IMG` and
`SMD0-L.IMG` (all three are `PACK-ONE`).

### 3.1 Extract it

```
# page 0 = first 2048 bytes; boot code = bytes 0..1999 (label starts at 2000)
dd if=SMD0.IMG of=smd_p0.bin bs=2048 count=1
# byte-swap to little-endian for nd100-dis (tool requirement only; NOT on disk)
python3 -c "d=bytearray(open('smd_p0.bin','rb').read());d[0::2],d[1::2]=d[1::2],d[0::2];open('smd_p0.le','wb').write(d)"
nd100-dis -a -o -b 0 smd_p0.le
```

### 3.2 HEX BLOB (big-endian, exactly as stored on disk)

First 512 words (1024 bytes) of the boot region. The live boot program actually
runs on to ~word 1061B; this half-page covers the prologue and the full
controller I/O sequence and is the embeddable "boot sector". (Zero runs are the
in-body parameter/scratch area the loader fills at runtime.)

```
0000: d105 d001 f10a d043 f100 d049 f13f a802
0010: 4813 d04a d048 580f 4e0c 0e0c b5fe 4809
0020: 600c 0807 580b 4e05 0e26 b5fe aa01 fd5e
0030: 00c0 fe00 ff5e 3f00 02f0 fd10 4839 cc6b
0040: 501f f6ff c006 a806 f5c4 cc69 f100 21c8
0050: a818 f6ff c006 a806 f5d2 cc69 f100 21c8
0060: a810 f6ff c006 a80d f222 ba08 a8fe a8fe
0070: a808 007e 8273 0000 0100 7f83 0000 0001
0080: 58f9 51ff d806 48fb cc2e 28f6 baf7 a8f9
0090: a802 a80b 080c d086 d086 d086 d086 eb64
00a0: fa15 a8fa 4804 a8f3 c789 aa03 0000 fde1
00b0: 45a5 0000 0200 0012 005a 0336 0335 0008
...  (mostly zero scratch / parameter words) ...
0180: 31e6 19e9 a801 cc65 09c1 f13f 71e6 b202
0320: cd8d 602b cc6f 49d5 cc41 c1b8 09d5 cc4d
0360: d10f 41d2 0000 49c2 700b 09c2 29e7 59e9
```

(Full blob = the first ~1000 words of page 0 of any `PACK-ONE` image; pull it with
the `dd` above.)

### 3.3 Annotated disassembly - what it does

Prologue and controller detect (addresses/opcodes octal):

```
000000  150405  PIOF                 ; word 0: interrupts + paging OFF - mandatory boot prologue
000001  150001  TRA STS              ; save/settle status
000002  170412  SAA 12               ; \
000003  150103  TRR PCR              ;  > set paging control / clear internal regs
000005  150111  TRR LCIL             ; /
000013  054017  LDX 17               ; \
000014  047014  LDA I ,X 14          ;  > clear a table in low memory (loop, JNC -2)
000016  132776  JNC -2               ; /
...
000113  150206  MCL PID              ; clear the priority-interrupt-detect (x4)
000117  165544  IOX 1544             ; SMD Read Status  - probe the controller
000124  143611  IDENT PL11           ; identify on level 11 (disk interrupt level)
```

The disk-read core (the second-stage loader) - the five SMD register operations:

```
000324  044703  LDA ,B -75           ; control word (unit | opcode Read)
000325  165545  IOX 1545             ; SMD Load Control Word  -> START operation
000326  165544  IOX 1544             ; SMD Read Status        -> poll
000327  175025  BSKP ZRO 20 DA       ; test "ready for transfer"
...
000743  044732  LDA ,B -46
000744  165543  IOX 1543             ; SMD Load Block Address I   (disk sector, low)
000750  044731  LDA ,B -47
000751  165543  IOX 1543             ; SMD Load Block Address II  (disk sector, high)
000753  044425  LDA ,B 25
000754  165541  IOX 1541             ; SMD Load Core Address   (memory dest, low)
000755  044426  LDA ,B 26
000756  165541  IOX 1541             ; SMD Load Core Address   (memory dest, high)
000757  044706  LDA ,B -72
000760  165547  IOX 1547             ; SMD Load Word Count     (transfer length)
000761  044745  LDA ,B -33
000762  165547  IOX 1547             ; SMD Load Word Count II  (ECC control)
000765  165544  IOX 1544             ; SMD Read Status         -> completion poll
```

**Decode (VERIFIED):**

- **Word 0 = `PIOF` (150405)** - the raw-bootstrap signature.
- Every I/O is a **literal `IOX` in the octal device window 1540-1547** - the
  **SMD/ECC** controller register bank (`nd100-dis` labels it "SMD1"). No `IOXT`
  (150415) appears, so this is not a SCSI bootstrap.
- **Register roles** (SMD/ECC controller, VERIFIED against the `nd100-dis`
  register annotations):

  | IOX (octal) | SMD register | Boot use |
  |-------------|--------------|----------|
  | `1541` | Load Core Address | destination memory address for the transfer |
  | `1542` | Read Seek Condition | seek-complete / ECC status |
  | `1543` | Load Block Address I / II | source disk sector (low / high) |
  | `1544` | Read Status | poll active / ready / error |
  | `1545` | Load Control Word | unit select + opcode (0 = Read) + **Active = start** |
  | `1547` | Load Word Count / ECC | transfer length + ECC control |

- **Load address / count / sector** are taken from an **in-page parameter block**
  (the `,B`-relative words the loader initialises - e.g. `,B 25`/`,B 26` hold the
  destination core address). The exact second-stage entry is reached through the
  loader's in-body subroutine-dispatch table (P-relative-indirect `JMP I`), i.e.
  it is **parameter-driven**, not a single fixed constant in the image.

**What it does, in one line (VERIFIED):** firmware (mass-storage load) copies this
1KW to address 0 and jumps to 0 -> `PIOF` prologue -> probe/clear the SMD/ECC
controller -> program Block Address + Core Address + Word Count -> start a **Read**
via the Control Word -> poll status -> jump into the freshly loaded second stage.
**Load device = SMD/ECC base 1540B; the firmware entry and image load base are
both memory address 0.**

> **A second, non-standard SMD image:** `~/repos/nd100x/SMD-BSD.IMG` also starts
> with `PIOF` but then drives the **console** (`IOX 303`/`IOX 305`), not the SMD
> registers - it is a custom BSD-project monitor/loader, **not** a stock SINTRAN
> SMD bootstrap. Treat `SMD0.IMG` as the canonical SMD bootstrap.

---

## 4. Floppy - **REAL bytes** (FLOMON, `250305L07-XX-01D.IMG`)

**VERIFIED** from `~/repos/nd100x/250305L07-XX-01D.IMG` (volume
`250305L07-XX-01D`, 616 pages). The floppy is booted by the **binary-format**
loader (ALD 1560), so page 0 carries a **BPUN stream**, not raw code.

### 4.1 The real preamble + load record bytes

```
0000: 0030 002f 0032 000d 000a 0032 0021 0000
0010: 0000 0000 0040 0003 ...
```

Decoded (each ASCII char is right-justified in a 16-bit big-endian word):

| Bytes | Value | Meaning |
|-------|-------|---------|
| 0x00-0x0B | `'0' '/' '2' CR LF '2'` | ASCII **preamble** (free text / octal digits) |
| 0x0C-0x0D | `00 21` | **`!`** (0x21) - start-of-binary delimiter |
| 0x0E-0x0F | `00 00` | load record **Address** = 0 |
| 0x10-0x11 | `00 00` | load record **Count** = 0 |
| 0x12-0x13 | `00 00` | load record **Checksum** = 0 |

Address = Count = Checksum = 0 after `!` is the **FLOMON** signature: "no program
to load - hand control to the floppy monitor". (A *populated* BPUN record would
carry a real Address, Count, `Count*2` data bytes, a Checksum = 16-bit sum of the
data words, and a 2-byte Action code; see [`boot-sector.md`](on-disk-format/boot-sector.md) §3.)

### 4.2 Binary-format load record layout (the general case)

From ND-06.014.2A §4.2.5.1 (**VERIFIED**) and the NDFS reader:

```
A  Preamble : any bytes except '!' (0x21). Optional octal number B, terminated CR.
B  (opt) octal number -> start address, terminated CR.
C  (opt) octal number -> terminated by '!'.
!  0x21  start-of-binary delimiter.
E  Block start address   : 2 bytes, most-significant byte first (big-endian).
F  Word count            : 2 bytes, big-endian (E, F, H not counted in F).
G  Data                  : F words, each 2 bytes big-endian.
H  Checksum              : 2 bytes = 16-bit arithmetic sum of the G words.
I  Action code           : 0 = start at address B; non-zero = return to OPCOM.
```

A **FLOMON** floppy is exactly this with `E = F = H = 0`. The floppy controller can
also *"load BPUN-files of maximum 64 Kwords directly from the floppy by pressing
LOAD"* (`../Devices/SCSI/ND-11.021.1 EN-Floppy and Streamer Controller 3106 3112.md`).

> `~/repos/nd100x/FLOPPY.IMG` has its boot area **space-filled** (all `0x40`) and is
> therefore **not bootable** - a useful negative control.

---

## 5. Winchester - **DERIVED** (no real Winchester directory image)

**We have no real Winchester boot image**, so there are **no Winchester bytes to
copy**. What *is* known (VERIFIED from the docs / ALD table, INFERRED for the exact
register block):

- Winchester boots via **mass-storage load** exactly like SMD: firmware copies
  page-0 (1KW) to address 0 and jumps to 0. So a Winchester boot area has the
  **same shape** as the SMD one - `PIOF` prologue, then controller I/O, then a
  second-stage read + jump.
- **Controller device window = 500-507B (and 510-517B)** (VERIFIED: ALD preset
  `20500` = "mass-storage load from **500**", ND-06.014.2A + nd100x `cpu_types.h`;
  the boot-format detector uses the same window,
  [`boot-sector.md`](on-disk-format/boot-sector.md) §5.2). So a Winchester
  bootstrap uses **literal `IOX 50x`** where the SMD one uses `IOX 154x`.
- **What differs from SMD is only the controller I/O block** (device window and
  the specific register offsets of the Winchester controller). The prologue,
  the 1KW-at-address-0 contract, and the "read stage 2 + jump" structure are
  identical.

**To get real Winchester bytes you need** one artifact: a **Winchester system disk
image** (page 0 with a `PIOF` + `IOX 50x` bootstrap), *or* the Winchester
bootstrap **MODE/load file** shipped by ND. Until then the Winchester register
sequence stays **INFERRED**.

---

## 6. SCSI - **DERIVED** (no real SCSI directory image)

**We have no real SCSI boot image** either. What is known:

- SCSI hard disks also use **mass-storage load** (1KW -> address 0 -> jump 0), so
  the boot area is again a raw `PIOF`-prologue program.
- The distinguishing feature is the I/O instruction: SCSI/NCR-5386 controllers are
  addressed with the single-word **`IOXT` (150415)**, which takes the device
  address from the **T register at runtime**, instead of a literal `IOX`.
  **VERIFIED** from the SCSI driver `SINTRAN/NPL-SOURCE/NPL/IP-P2-SCSI-DRIV.NPL`:
  every controller access is `T := HDEV + <reg>; *IOXT` (e.g. line 123
  `T:=HDEV+RSTAU; *IOXT`), where `HDEV` is the hardware device base. The NCR-5386
  register offsets (VERIFIED from the same source):

  | Symbol | Offset | Register |
  |--------|--------|----------|
  | `RNDAT` | 40 | Read NCR data register |
  | `WNDAT` | 41 | Write NCR data register |
  | `RNCOM` | 42 | Read NCR command register |
  | `WNCOM` | 43 | Write NCR command register |
  | `RNCNT` | 44 | Read NCR control register |
  | `WNCNT` | 45 | Write NCR control register |

  (`IP-P2-SCSI-DISK.NPL` adds the disk-level read/write logic on top of this
  driver.)

- Consistent with this, the ALD table has no dedicated mass-storage SCSI preset;
  SCSI systems commonly **boot from a floppy first** (ALD 1560, the nd100x
  `cpu_types.h` note "SCSI boot use this setting..?"), which then loads the SCSI
  system - so a pure page-0 SCSI mass-storage bootstrap may not even be the normal
  boot path on those systems. This is **OPEN**.

**To get real SCSI bytes you need** a **SCSI system disk image** whose page 0
begins with `PIOF` + `IOXT` and drives the NCR-5386, *or* the ND SCSI bootstrap
load file. Until then the SCSI boot sequence is **INFERRED** from the driver.

> **Note - driver vs bootstrap I/O style.** The stock SMD *driver*
> (`IP-P2-DISK-START.NPL`) also uses `*IOXT` (T-relative) for its normal I/O, yet
> the SMD *bootstrap* in `SMD0.IMG` uses **literal `IOX 154x`**. The bootstrap
> hard-codes its device because it runs before any datafield/T setup exists; the
> driver is written device-relative. Do not infer the bootstrap I/O style from the
> driver source alone.

---

## 7. How SINTRAN writes the bootstrap (the mechanism)

### 7.1 Floppy - **VERIFIED** operator command

`@DEVICE-FUNCTION ... DUMP-BOOTSTRAP <file>` writes a **BPUN file onto page 0** of
a floppy (ND-60.128.5 p.97, **VERIFIED**):

> *"Dump a bootstrap onto page 0 (the first page) of a floppy. The floppy monitor
> can then be loaded ... by pressing MASTER CLEAR and typing 1560&."*
> Rule: *"Allowed only on floppy disk."*

Operator flow (ND-10022S "SINTRAN UTILITY PROGRAMS", **VERIFIED**):

```
$DEV-FUNCTION,<floppy peripheral name>,DUMP-BOOTSTRAP,FLOPPY-MON
```

**Where the code originates:** a shipped **`:BPUN` file** - `FLOPPY-MONITOR:BPUN`
(program `LDR-2010F`, "FLOPPY-MON") - i.e. a normal absolute-binary load file, not
a ROM copy. `DUMP-BOOTSTRAP` simply copies that BPUN stream into page 0. To make a
FLOMON floppy you emit the empty-record BPUN stream of §4 directly.

### 7.2 Hard disk (SMD / Winchester / SCSI) - the raw bootstrap

There is **no `DUMP-BOOTSTRAP` for hard disks** (it is floppy-only). The 1KW
page-0 program is what the **mass-storage-load firmware** reads and runs (§2). It
gets onto the disk as part of **installing the system image**:

- The hard-disk boot area is a **raw ND-100 program** (the "mass-storage
  bootstrap" / first-stage loader) written at **page 0 of the system disk** when
  the system pack is built - historically by a **stand-alone pack-to-pack /
  mass-storage copy** program (e.g. `COP-VERIFY`, ND-10022S: *"to copy pages
  between mass storage devices"*, booted itself by `MASTER CLEAR, 1560&`), which
  copies page 0 (and the rest) verbatim from a master pack.
- The **origin of the code** is therefore a **prebuilt boot program**, not a live
  SINTRAN routine and not a checksum-wrapped BPUN. For an external tool the
  practical, honest answer is: **copy a known-good real SMD page-0 blob** (§3.2)
  into your image, or assemble a first-stage loader that obeys the §8 contract.
- **OPEN:** the exact ND utility/MODE file that *originally authored* the SMD
  page-0 program (as opposed to copying it pack-to-pack) is not pinned down in the
  manuals on hand. What is fully VERIFIED is the **consumer contract** (§2) and the
  **real bytes** (§3), which is what an emitter needs.

> **Corrections 2026-10-29 - the author is SINTRAN itself.** The question above is answered by
> the kernel source: `PH-P2-OPPSTART.NPL` lines 867-876 ("READ PAGE #0 AND INSERT BOOTS-STRAP
> AND "SWAP-DRIVER", AND THEN WRITE THE PAGE BACK") read page 0 with `CRDISC`, copy the
> bootstrap `RELOA`..`LDEND` (the MAC program at lines 3729-3766, assembled into the kernel) into
> it, append the swap driver (`ZBDIS` for SMD, `ZWDIS` for ST-506, `SCSWD` for SCSI, chosen from
> the `MDISCS` table at lines 22-31; size `SWDSIZE`) and write the page back. This runs after
> label `OVCO` (line 843), i.e. on **both** the cold (`HENTFLAG=0`) and the warm start, so every
> SINTRAN start rewrites the pack's page-0 bootstrap from the running kernel's own copy. Lines
> 845-865 fill the bootstrap's cells first: `NOBLK = CDABLPAGE*77` blocks (63 pages),
> `DYBLS = DBLST(0)` (start of `SEGFIL0`, 256 blocks on the measured K and L packs),
> `LDRAD = SWPDRIVER`, `YSWTY` = disk type. The program ends with `IDENT PL11; JMP I (SINTR`
> (3766). A pack-to-pack copy therefore only has to deliver a page 0 good enough for one boot;
> after that SINTRAN maintains it. **Caveat kept:** the first words of SMD0.IMG page 0 (§3.3,
> lines 147-156: `PIOF; TRA STS; SAA 12; TRR PCR ...`) are not byte-identical to s3vs-4's
> `RELOA` (`PIOF; TRA STS; BSKP ONE 140 DA; JMP *+5 ...`, line 3729), so the L07 `RELOA` may
> differ from this K-source listing - **UNVERIFIED** until an L07 listing or a live L07 page-0
> read-back is compared.

The `@DUMP` / `@DUMP-REENTRANT` commands referenced in ND-10022S (e.g.
`@DUMP "DUMPFL-2327A" ...`) produce **BPUN files with bootstrap + checksum** (the
NRL/loader "octal-coded bootstrap", 44 octal locations - ND-60.066.04 Relocating
Loader) - that is the **BPUN/binary-load** path (character devices), not the
raw hard-disk mass-storage path.

---

## 8. Format spec per device class (to generate, not just copy)

### 8.1 Raw hard-disk bootstrap (SMD / ECC / Winchester / SCSI)

A raw ND-100 program occupying page 0. Firmware loads **1KW to address 0 and jumps
to 0**, so:

1. **Prologue (mandatory):** word 0 = **`PIOF` (150405)** (interrupts + paging off)
   or at minimum **`IOF` (150401)** (interrupts off). Nothing else may legally
   start a raw bootstrap - this is the detector signature.
2. **Controller load block** - the *only* part that differs by controller:
   - **SMD / ECC / Winchester:** literal **`IOX` = 164000B + device number** in the
     low 11 bits.
     - SMD/ECC base **1540B** (`IOX 1541` Load Core Addr, `1543` Load Block Addr,
       `1545` Load Control Word = start, `1544` Read Status, `1547` Load Word
       Count). VERIFIED (§3).
     - Winchester base **500B** (`IOX 50x`). INFERRED (§5).
   - **SCSI / NCR-5386:** single-word **`IOXT` (150415)** with the device address in
     the **T register**; register offsets `RNDAT`=40 ... `WNCNT`=45 (§6). INFERRED.
3. **Second-stage read + jump:** program Block Address (source sector), Core
   Address (destination memory), Word Count (length); start a **Read**; poll
   status; then **jump into the loaded second stage**.

Only the device window / register block changes between SMD, Winchester, and SCSI;
the prologue and the "load 1KW at 0, read stage 2, jump" structure are identical.

### 8.2 Floppy BPUN / FLOMON (punched-tape load format)

Character/tape-style stream consumed by the **binary-format** loader:

```
<preamble bytes, no 0x21>  [octal B <CR>]  [octal C]  '!'(0x21)
Address(2, big-endian)  Count(2)  Data(Count*2)  Checksum(2)  Action(2)
```

- **FLOMON terminator:** `Address = 0, Count = 0, Checksum = 0` immediately after
  `!` - the "hand control to the floppy monitor" convention (three zero words).
- **Populated BPUN:** real Address/Count/Data, Checksum = 16-bit sum of the data
  words, Action = 0 (start at B) or non-zero (return to OPCOM).

---

## 9. "To build a bootable image yourself" - checklist per device

**Common:** write the boot bytes into page 0 **bytes 0..1999**; leave bytes
2000..2047 for the extended-info + label written by your filesystem step
([`create-directory.md`](create-directory.md)). Multi-byte values are
**big-endian**. The two steps do not overlap.

**SMD / ECC (REAL, reproducible now):**
1. Emit the real 1KW page-0 blob from §3.2 (or `dd bs=2048 count=1` from a
   `PACK-ONE` image) into bytes 0..1999.
2. Ensure your second-stage system is at the disk sectors that blob's parameter
   block reads (or author your own first stage per §8.1 using `IOX 154x`).
3. Bootable via ALD **21540** (mass-storage load from 1540).

**Floppy (REAL, reproducible now):**
1. For FLOMON: write the preamble + `!` + three zero words (§4.1); or copy the
   `FLOPPY-MONITOR:BPUN` stream.
2. For a self-loading floppy: emit a populated BPUN record (§8.2) with a valid
   Checksum and Action = 0.
3. Bootable via ALD **1560** (binary load from 1560).

**Winchester (DERIVED - shape only):**
1. Same raw-bootstrap shape as SMD but with `IOX 50x` controller I/O.
2. You **cannot** copy real bytes (none available); you must author the first
   stage or obtain a Winchester boot image.
3. Bootable via ALD **20500**.

**SCSI (DERIVED - shape only):**
1. Same raw-bootstrap shape but with `IOXT` (150415), device base in T, NCR-5386
   register offsets 40..45.
2. No real bytes available; author from the driver or obtain a SCSI boot image.
   Note many SCSI systems boot from a floppy first (ALD 1560).

---

## 10. Status summary - VERIFIED / INFERRED / OPEN

| Claim | Status | Evidence |
|-------|--------|----------|
| Firmware loads 1KW to addr 0 and jumps to 0 (mass storage) | **VERIFIED** | ND-06.014.2A §4.2.5.2 |
| Binary-format load record layout (preamble+`!`+Addr/Count/Data/Cksum/Action) | **VERIFIED** | ND-06.014.2A §4.2.5.1 |
| ALD presets (1560 floppy, 20500 Winchester, 21540 SMD) | **VERIFIED** | ND-06.014.2A p.232 + nd100x `cpu_types.h` |
| SMD bootstrap = `PIOF` + `IOX 1541/1543/1544/1545/1547`, reads stage 2 + jumps | **VERIFIED** | `SMD0.IMG` disassembly (§3) |
| SMD boot blob byte-identical across `SMD0`/`SMD0-org`/`SMD0-L` | **VERIFIED** | md5 of page 0 |
| Floppy FLOMON = preamble `0/2 CR LF 2 !` + 3 zero words | **VERIFIED** | `250305L07-XX-01D.IMG` (§4) |
| `DUMP-BOOTSTRAP` writes a `:BPUN` file to floppy page 0 (floppy only) | **VERIFIED** | ND-60.128.5 p.97 + ND-10022S |
| Floppy bootstrap origin = shipped `FLOPPY-MONITOR:BPUN` (`LDR-2010F`) | **VERIFIED** | ND-10022S |
| SCSI uses `IOXT`, NCR-5386, device in T, regs 40..45 | **VERIFIED (driver)** / **INFERRED (bootstrap)** | `IP-P2-SCSI-DRIV.NPL` |
| Winchester uses `IOX 50x`, otherwise SMD-shaped bootstrap | **INFERRED** | ALD 20500 + detector window; no real image |
| Hard-disk page-0 blob is copied pack-to-pack when the system is installed | **INFERRED** | ND-10022S `COP-VERIFY`; no explicit "author" utility found |
| The utility/MODE file that originally *authored* the SMD page-0 program | **OPEN** | not pinned in manuals on hand |
| SINTRAN rewrites page 0 (bootstrap `RELOA`..`LDEND` + swap driver) at every start, cold and warm (corrected 2026-10-29) | **VERIFIED (source)** | `PH-P2-OPPSTART.NPL` 843, 867-876; §7.2 note |
| The L07 `RELOA` equals the s3vs-4 (K) listing | **UNVERIFIED** | SMD0.IMG page-0 words (§3.3) differ from OPPSTART 3729 |
| SCSI normal boot path (floppy-first vs page-0 mass-storage) | **OPEN** | nd100x note + ALD table |

**What is still missing to close Winchester / SCSI:**

- **Winchester:** a real Winchester **system disk image** (page 0 = `PIOF` +
  `IOX 50x`), *or* the ND Winchester bootstrap MODE/load file. Then §5 becomes
  VERIFIED with real bytes and an annotated disassembly like §3.
- **SCSI:** a real **SCSI system disk image** whose page 0 is `PIOF` + `IOXT`
  driving the NCR-5386, *or* the ND SCSI bootstrap load file. Then §6 becomes
  VERIFIED.

---

## References

- Real images: `~/repos/nd100x/SMD0.IMG`, `SMD0-org.IMG`, `SMD0-L.IMG` (SMD,
  real); `250305L07-XX-01D.IMG` (FLOMON floppy, real); `FLOPPY.IMG` (space-filled,
  not bootable); `SMD-BSD.IMG` (custom BSD monitor, non-standard).
- Firmware / load formats: `../../Reference-Manuals/ND-06.014.2A EN ND-100 Reference Manual.md`
  §4.2.5 (Bootstrap Loaders), p.232 (ALD).
- Operator command: `../../Reference-Manuals/ND-60.128.5 EN SINTRAN III Reference Manual.md`
  p.97 (`DEVICE-FUNCTION DUMP-BOOTSTRAP`);
  `../../Reference-Manuals/ND-10022S SINTRAN UTILITY PROGRAMS.md` (FLOPPY-MON,
  COP-VERIFY).
- Drivers: `../NPL-SOURCE/NPL/IP-P2-DISK-START.NPL` (SMD/disk),
  `../NPL-SOURCE/NPL/IP-P2-SCSI-DRIV.NPL` + `IP-P2-SCSI-DISK.NPL` (SCSI/NCR-5386).
- Emulator boot classification: `~/repos/nd100x/src/cpu/cpu_types.h` (ALD table),
  `src/machine/machine_types.h` (`BOOT_FLOPPY`/`BOOT_SMD`, `DRIVE_SMD`/`DRIVE_FLOPPY`).
- Disassembler: `~/repos/nd100-tools/nd100-dis/nd100-dis` (little-endian).
- Related on-disk docs: [`on-disk-format/boot-sector.md`](on-disk-format/boot-sector.md)
  (page-0 map + boot-format detector), [`create-directory.md`](create-directory.md)
  (the filesystem-structure half), [`README.md`](README.md).
```
