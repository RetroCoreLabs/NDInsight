# COSMOS TCP/IP for SINTRAN III

**Product sheets, the extracted distribution files for two generations of the gateway, a
verified install and start-up procedure, and the reverse engineering of the PIOC firmware.**

Two complete kits are here, recovered from real packs. Neither is a pristine distribution
floppy — they are what was installed and running on two machines — but every file has been
checked and **nothing in either kit is damaged**.

---

## Contents

| Path | What |
|------|------|
| [`COPYING-FILES-TO-SINTRAN.md`](COPYING-FILES-TO-SINTRAN.md) | **How to get the files onto a pack** — four routes, the parity rules, and the traps. Read this first. |
| [`RUNNING-TCPIP-ON-RETROCORE.md`](RUNNING-TCPIP-ON-RETROCORE.md) | **Running the D02 stack on an emulated ND-100 in RetroCore**: npcap, the host loopback adapter, addresses, start-up, TCPIP-MONITOR, known console messages, and telnet/FTP from the Windows host |
| [`x/D02-gateway-and-clients/`](x/) | Gateway **D02** + Telnet/FTP/RSH clients **D01**, from the c3 pack |
| [`x/B05-gateway-and-telnet-server/`](x/) | Gateway **B05**, which is the one with an **ND-100 telnet server**, from the Tingo pack |
| [`RE/`](RE/) | Reverse engineering of the 68000 PIOC firmware — every routine named, the TCP state machine fully decoded |
| `ND-8950*.pdf`, `ND0106.PDF` | The product sheets (below) |

### Product sheets

| File | Product | Product no. |
|------|---------|-------------|
| `ND-895061-1A-EN.pdf` | PI: TCP/IP Basic Module/III (rev B05) | 211327B |
| `ND-895061-2-EN.pdf` | PI: TCP/IP Basic Module/III (version D00) | 211327D |
| `ND-895070-1A-EN.pdf` | PI: COSMOS TCP/IP Gateway for Ethernet (version C07) | 211185C |
| `ND-895070-2-EN.pdf` | PI: COSMOS TCP/IP Gateway for Ethernet (version D02) | 211185D |
| `ND-895071-2-EN.pdf` | PI: COSMOS Telnet/FTP Clients (version D01) | 211154D |
| `ND-895071-3-EN.pdf` | PI: COSMOS FTP/Telnet Clients (version E02) | 211154E |
| `ND0106.PDF` | Software Library Diskette listing, directory `211154B05-XX-01D` | 211154B05 |

---

## 1. Which product is this, exactly

Read out of the binaries, not assumed:

| Kit | Product | ND number | Version | Proof string |
|---|---|---|---|---|
| D02 | COSMOS TCP/IP Gateway for Ethernet | 211185 | **D02** | `COSMOS TCP/IP Gateway for Ethernet II ND-211185D02` in `TCPP-D02:PROG` |
| D02 | COSMOS Telnet/FTP Clients | 211154 | **D01** | `TELNET CLIENT ND-211154D01`, `FTP CLIENT ND-211154D01`, `RSH CLIENT ND-211154D01` |
| D02 | FTP server component | 211185 | **C07** | `FTP-SERVER ND-211185C07` |
| B05 | COSMOS TCP/IP Gateway for Ethernet | 211185 | **B05** | `TCP/IP server ETH II,version:B05` |
| B05 | COSMOS Telnet/FTP Clients | 211154 | **B05** | `TELNET client ND-211154B05` |

**Neither kit is TCP/IP Basic Module/III (211327).** Both are the 211185 gateway, two
revisions apart. The gateway sheet lists `211327 >= B05` as an *alternative* prerequisite
and the shared letters make that easy to misread.

**Do not mix generations.** The mode files, bank images and segment names differ (`TCPS0*`
in D02, `TCPS1*` in B05).

### Which one do you want?

| You want | Use |
|---|---|
| telnet **client**, FTP client, RSH client, FTP server | **D02** |
| an incoming **telnet server** on the ND-100 side | **B05** — D02 has no `TNSERV` |

---

## 2. Prerequisites

- An **ND Ethernet II controller** (ND-110063) installed and working, with its ENCOS
  firmware loaded. See [`../Ethernet/`](../Ethernet/README.md).
- **XMSG running**, and **TADADM running**. TCP/IP registers as a system server and talks
  to SINTRAN through XMSG. See [`../../../SINTRAN/XMSG/`](../../../SINTRAN/XMSG/README.md).
- `SYMBOL-1-LIST` present — the two `DEFINE-*` mode files run `@DMAC` and patch live
  SINTRAN.

---

## 3. Where the files go

From the original installation log `(SYSTEM)IN-TCP-IP-XX-D02:LOGG`:

```
Source directory 211185D-XX-01D   ->  user 'TCP-IP'
Source directory 211185D-XX-02D   ->  user 'TCP-IP'
```

| Kit folder | SINTRAN user | Notes |
|---|---|---|
| `TCP-IP/` | **`TCP-IP`** | create it first; ~1000-page quota (37 files on the c3 pack) |
| `SYSTEM/AIP-*.SYMB` | **`SYSTEM`** | hosts/networks/services tables, read at run time **by name** |
| `TCP-COMM/` (D02 only) | `TCP-COMM` | **source** of the comms module — not needed to run |
| `SYSTEM/IN-TCP-IP-XX-D02.INST` / `.LOGG` | — | the original answer file and log. **Reference only, do not run.** |

**How to copy them in: [`COPYING-FILES-TO-SINTRAN.md`](COPYING-FILES-TO-SINTRAN.md).**
That document exists because the parity handling is per-file and getting it wrong fails
silently.

---

## 4. Load order — D02

Three mode files, three different moments.

### 4a. Cold start — `TCP-IP-LO-D02:MODE`

Its own header:

```
@CC = TO BE RUN DURING COLD-START IN THE FILE HENT-MODE:MODE, ANYWHERE
@CC = AFTER THE 'INITIALIZE-BACKGROUND-PROGRAMS' COMMAND IS EXECUTED.
```

Add `@MODE (TCP-IP)TCP-IP-LO-D02:MODE,,` to `HENT-MODE:MODE`. What it does, in order:

| # | File | Into segment | Becomes RT program |
|---|---|---|---|
| 1 | `PO-STOP-D02:PROG` | run directly (`@(TCP-IP)PO-STOP-D02 0`) | — |
| 2 | `TCPP-D02:PROG` | `TCPPS` (background, DM) | `TCPP`, priority 30 |
| 3–6 | `TCP-SER-B0..B3-D02:BPUN` | `TCPS0B0`..`TCPS0B3` | — |
| 7 | `FTPRT-D02:PROG` | `FTPS0` | `FTPRT`, priority 30 |
| 8 | `PO-PWRFAIL-D02:PROG` | `POPWR` | `POPWR`, priority 50 |
| 9 | `@MODE DEFINE-TCPP-D02:MODE` | — | patches `TCPP` into the system-server table, index **7B** |
| 10 | `@MODE DEFINE-FTPRT-D02:MODE` | — | patches `FTPRT` into the system-server table, index **10B** |

Banks load with `READ-BI` then `SE-LO-AD,,177777` — the whole 64K-word bank.

**Choosing the Ethernet controller.** `TCP-IP-LO-D02:MODE` carries this commented out:

```
@cc set tcpdevice to n:  0= 0B, 1= 1B, 2= 2B, 3= 3B.
@cc -4=177774B sets tcpdevice to the lowest numbered ACTIVE eth-II !!
@cc @LOOK-AT SEGMENT FTPS0
@cc 24/177774
@cc .
```

Uncomment and adjust if the default is wrong.

### 4b. Warm start — `TCP-START-D02:MODE`

> "RUN THIS MODE FILE DURING WARM START, ANYTIME AFTER X-MESSAGE AND TADADM ARE RUNNING."

```
@ABORT ftprt / @ABORT tcpp / @(TCP-IP)PO-STOP-D02 0
@RT TCPP      <- telnet + TCP/IP
@RT FTPRT     <- FTP server
```

Running this before XMSG and TADADM are up is the classic failure.

### 4c. Shutdown — `TCP-STOP-D02:MODE`

> "RUN THIS MODE FILE WHEN STOPPING MACHINE, ANYTIME BEFORE X-MESSAGE AND TADADM ARE STOPPED."

Call it from `STOP-MACHINE:MODE`.

### 4d. The clients are dumped reentrant

Not loaded to segments — ordinary user programs:

```
@DUMP-PROGRAM-REENTRANT TELNET-CLIEN-D (TCP-IP)TELNET-CLIEN-D01:PROG
@DUMP-PROGRAM-REENTRANT FTP-CLIEN-D    (TCP-IP)FTP-CLIEN-D01:PROG
@DUMP-PROGRAM-REENTRANT RSH-CLIEN-D    (TCP-IP)RSH-CLIEN-D01:PROG
```

`HENT-MODE-C3:MODE` names them abbreviated (`(TCP-IP)TELNET-CLIEN-D`); SINTRAN resolves by
prefix, so those *are* the `-D01` files.

---

## 5. Load order — B05 (the one with the telnet server)

`TCP-IP-LO-1-B05:MODE`. Same shape, segment names `TCPS1*`, plus two things D02 lacks:

| File | Into segment | Becomes RT program |
|---|---|---|
| `TCP-ERROR-1-B05:BRF` | `TCPE1` (page table 2) — relocating `LOAD` then `WRITE-REFERENCES` | — |
| `TCP-SER-B0..B3-B05:BPUN` | `TCPS1B0`..`TCPS1B3` | RT descr `TCPS1`, priority 40 |
| **`TELNET-SERV-B05:PROG`** | **`TNSEG`, a 2-bank background segment** | **`TNSERV`, priority 16** |
| `FTPRT-B05:PROG` | `FTPS0` | `FTPRT`, priority 30 |

`TELNET-SERV` **must** be 2-bank — `NEW-BACKGROUND-SEGMENT TNSEG,2,dm` and
`CHANGE-RT-DESCRIPTION TNSERV,16,TNSEG,,0,2,1,2`, then `WRITE-SEGMENT TNSEG`. The file's
own header is a 2-bank header (§7).

Two `@LOOK-AT` patches follow, and **you must set these for your network**:

```
@LOOK-AT SEGMENT TCPS1B1     <- subnet bits and gateway address
150615/0
0
0
.
@LOOK-AT SEGMENT TCPE1       <- server number
0/1
0
0
.
```

Word `150615B` in bank 1 is byte `0x1A35A` of the bank image — verified to be inside the
image in a zero region, which is what an unwritten config slot looks like.

---

## 6. Configuration — user `SYSTEM`

| File | Holds |
|---|---|
| `AIP-CONFIG:SYMB` | **the controller table — the IP address lives here** |
| `AIP-HOSTS:SYMB` | host table, `address name ALIAS` per line |
| `AIP-NETWORKS:SYMB` | network numbers (`loopback 127`, `arpanet 10`, …) |
| `AIP-SERVICES:SYMB` | port/service table |
| `AIP-PROTOCOL:SYMB` | protocol numbers — `ip 0`, `icmp 1`, `ggp 3`, `tcp 6`, `pup 12`, `udp 17` |

### `AIP-CONFIG:SYMB` — edit this first

```
# TCP number    E-II number    IP address    IP gateway       Subnet bits
0               0              192.168.1.40  000.000.000.000  0
```

> NOTE: The Internet address must be updated in the AIP-HOSTS:SYMB too.
> The controller must be restarted before any changes have effect.

The **IP gateway** and **Subnet bits** columns are the same two values the
`@LOOK-AT SEGMENT TCPS1B1 / 150615/` patch writes into bank 1 on B05. Keep them
consistent.

The firmware reads its own address, gateway, mask and broadcast MAC from fixed globals —
see [`RE/TCP-SER-D02-CALL-TREE.md`](RE/TCP-SER-D02-CALL-TREE.md) §6 if you need to find
them in a memory dump.

**`AIP-RESOLVER:SYMB` does not exist anywhere.** ND-895071-3 names it and
`RSH-CLIEN-D01:PROG` references `(SYSTEM)aip-resolver:symb` internally, but a sweep of all
354 NDFS volumes on hand finds no copy. Name resolution falls back to `AIP-HOSTS`.

---

## 7. What the pieces actually are

- **`TCP-SER-B0..B3:BPUN` are not ND-100 code.** They are flat 128 KB memory-bank dumps for
  ND's **68000-based PIOC** controller. `:BPUN` here means "binary dump", not BPUN block
  format — there are no `Address/Count/Data/Checksum` blocks.
- **A mostly-empty bank is normal.** `TCP-SER-B2-D02` is 100% zero and *correct* — that bank
  is unused. The checksum is what separates "empty" from "damaged".
- **Each bank carries its own checksum**, which makes these the one ND file type where
  "is this damaged?" has a real answer. Bytes `0x40..0x20043` are the image; a 16-bit
  big-endian sum of every word sits at `0x20044`. All eight banks here verify.
- **`:PROG` headers** are `startaddr startaddr 0000 length FFFF` for a 1-bank program.
  `TELNET-SERV-B05` reads `14A8 14A8 0000 71A5 0000 E1C5 …` with no `FFFF` — a 2-bank
  header, matching `NEW-BACKGROUND-SEGMENT TNSEG,2`.
- **`TCP-ERROR-1-B05:BRF`** is the error-message module (`UE-ERMSG-EN-C` / `TCP/IP server`),
  relocatable BRF linked with `WRITE-REFERENCES`.

### Where the telnet server actually lives

**D02 has no telnet-server RT program** — the install log shows `@ABORT TNSERV` →
`NO SUCH RT-PROGRAM NAME`. The server is inside the PIOC firmware, and the reverse
engineering pins it down: it is the `TELNET_*` routines in **bank 0** (`TELNET_Main`
@0x1C10E, `TELNET_ServerInit`, `TELNET_AcceptLoop`), which reach SINTRAN over XMSG.

> **Correction to an earlier note.** Bank 3 was described as containing "the routine
> `ConnectToSintranConMTAD`". It does not. Bank 3 is 2.3% content and holds **strings and
> tables only** — `ConnectToSintran` and `ConMTAD` are entries in a 27-name table at
> 0x75FE4 that **no code in the image references**. See
> [`RE/TCP-SER-D02-CALL-TREE.md`](RE/TCP-SER-D02-CALL-TREE.md) §3b: the names describe the
> intended mailbox/TAD path, but they are not proof of the wire format.

B05 is different — it ships a real ND-100-side `TELNET-SERV-B05:PROG`.

---

## 8. Condition of the files

**Nothing in either kit is damaged.** Per-page evidence in each folder's `TRUST.md`.

| | D02 | B05 |
|---|---|---|
| pages confirmed by another image of the pack | 717 | 739 |
| uncorroborated / contradicted / lost to imaging | 0 / 0 / **0** | 0 / 0 / **0** |
| blank (real zeros on disk) | 217 | 250 |
| sparse holes (block pointer 0, by design) | 611 | 377 |
| PIOC bank checksums | 4/4 OK | 4/4 OK |

Large blank and sparse counts are normal — these are memory-image files with unused address
ranges. Cross-checked three ways: against other packs, against the `mfm_read` bad-sector log
(no TCP file sits on a bad track), and against the bank checksums.

### Named somewhere but not present

| Missing | Named in | Matters? |
|---|---|---|
| `AIP-RESOLVER:SYMB` | ND-895071-3; inside `RSH-CLIEN-D01:PROG` | no — hosts table works without it |
| `TCPPCONT:PROG` | installer delete-list, `TCP-IP-LO-C07:LIST` | C07 only; D02 replaced it with `TCPP` |
| `IN-TCP-IP` (the installer) | both manuals | lived on floppy `211185D-XX-01D`, not among the images |
| `TCP-SER-B*-C07`, `FTPRT-C07`, `PO-STOP-C07`, `PO-PWRFAIL-C07` | `TCP-IP-LO-C07:LIST` | the whole **C07 generation is gone**; only listings survive |
| `TELNET-SERV` in D02 | — | never on c3 — use B05 |
| `RSH-CLIEN` in B05 | — | never on Tingo — use D01 from the D02 kit |

None of these blocks a D02 or B05 load. The real gap is the distribution floppy
`211185D-XX-01D` — worth watching for, since it would give pristine copies.

---

## 9. Order for a manual install

1. Create user `TCP-IP`, ~1000-page quota.
2. Copy `x/<kit>/TCP-IP/*` in — **see
   [`COPYING-FILES-TO-SINTRAN.md`](COPYING-FILES-TO-SINTRAN.md)**; parity is per file.
3. Copy `SYSTEM/AIP-*.SYMB` to user `SYSTEM`. Edit `AIP-CONFIG` and `AIP-HOSTS`.
4. **Verify the four bank checksums after the copy.** This catches a parity mistake
   instantly and is the most common way to ruin a `:BPUN`:
   ```powershell
   python verify_pioc_bank.py mypack.img
   ```
5. Confirm XMSG and TADADM are running.
6. `@MODE (TCP-IP)TCP-IP-LO-D02:MODE,,` — read the output; it should reach `EXIT` with no
   `NO SUCH SEGMENT` or `SPACE NOT AVAILABLE`.
7. Set the Ethernet device with the `@LOOK-AT SEGMENT FTPS0` / `24/` patch if needed.
8. Dump the clients reentrant (§4d).
9. `@MODE (TCP-IP)TCP-START-D02:MODE,,`.
10. Once it works, add the cold-start call to `HENT-MODE:MODE` and the shutdown call to
    `STOP-MACHINE:MODE`.

---

## 10. Reverse engineering — [`RE/`](RE/)

The D02 PIOC firmware has been fully mapped: all 906 functions named, the TCP state machine
decoded, and the BSD ancestry established.

| File | What |
|---|---|
| `TCP-SER-D02-CALL-TREE.md` | the main document — module map, call trees, `protosw`, the 14×10 transition matrix, the trace bitmaps, the server-name scheme |
| `TCP-SER-D02-CALL-TREE-FULL.txt` | depth-4 call trees from 15 entry points |
| `TCP-SER-D02-FUNCTION-CATALOG.md` / `.csv` | every entry point, one row each |
| `TELNET-XMSG-SIN.md` | how the telnet server reaches SINTRAN over XMSG |
| `TCP-SER-B0-D02.BIN` | the four banks merged into one flat 512 KB image (the Ghidra input) |

Points that matter operationally:

- The stack is a **PLANC-MC re-implementation of 4.2/4.3BSD** — real `protosw` entries for
  raw/UDP/TCP at 0x07536A, and a 14-state TCP machine driven by a transition matrix.
- **There is no IP forwarding path.** A packet whose destination is not this card's address
  (or a broadcast) is counted and dropped. It is a host, not a router.
- The card answers **EtherType 0x9002** (configuration test) roughly **one time in eight**,
  replying with a `"ND/EII-TCP-"` banner.
- The XMSG server name is built by **patching the string literal in place** with the
  interface number — `*TCP` for interface 0, `*TCPn` otherwise. An emulator that maps that
  page read-only breaks every interface except 0, and breaks it silently.

---

## 11. Sources

| | |
|---|---|
| D02 gateway + D01 clients | `c3_2024_1.img` — May 2024 read of the **c3** Micropolis 1325 |
| B05 gateway + telnet server | `tingo_micropolis_1325.img` — the **Tingo** Micropolis 1325 |
| corroborating images | `c3-k-bd.img`, `BD.IMG`, `WD0-M.IMG`, `c3-recovered.img`, and an earlier read of the Tingo drive |
| install manifest | `(SYSTEM)IN-TCP-IP-XX-D02:LOGG` on the c3 pack |
| manuals | ND-895070-2-EN (gateway D), ND-895070-1A-EN (gateway C), ND-895071-3-EN (clients E) |

**Do not use the 2023 read of the c3 drive (`1325.img`) or its copies** — it lost
heads 4–7 and all four of its bank files fail checksum.

---

**Parent:** [../README.md](../README.md) ·
**Related:** [../Ethernet/](../Ethernet/README.md) ·
[../../../SINTRAN/XMSG/](../../../SINTRAN/XMSG/README.md)
