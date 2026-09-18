# PIOCOS / ENCOS - the ND 68K comms-board RTOS

This is the documentation home for the real-time operating system that runs on Norsk Data MC68000
front-end communications boards, and specifically the **ENCOS** firmware on the **Ethernet II
controller (ND-110063)**.

Tag every claim **[V]** (verified: firmware bytes / Ghidra / an ND manual) or **[U]** (inferred).

## 1. What "PIOCOS" is

**PIOCOS** = "PIOC Operating System", a Norsk Data MC68000 real-time monitor documented for the
**ND 857 PIOC** (Programmable I/O Controller) board. [V-doc: `Installation/Product-Info/ND-857-A1-EN.md`]

Documented capabilities: multiprogramming, process initiation + scheduling, interprocess communication
and synchronization (via messages over ports - a **subset of the SINTRAN III XMSG task-to-task message
system**), timing, exception handling, dynamic process control, and ND-100 communication. A host-side
"PIOC MONITOR" program loads/supervises the card; a "Micro Monitor" executive runs in the 68000. [V-doc]

Host cooperation model (PIOC): a shared 64K-word SINTRAN segment, one mailbox per direction, each with a
one-bit status word. [V-doc]

> The user recollection "PICOS" refers to PIOCOS (no product named "PICOS" exists in the ND docs).

### PIOCOS runs on the Ethernet II controller - confirmed by ND's own error text [V-doc]

The ND-100 TCP/IP client user guide lists an AIP (ARPA Internet Protocol) error whose text names the
controller OS directly:

> `20115 : AIPpiocError : PIOCOS error, error code in information field`
> - `../../../../../Operations/Cosmos/ND-860284-1-EN COSMOS TELNET-FTP Client User Guide.md` line 2212

AIP (the IP layer of the COSMOS TCP/IP Gateway, product 211185) runs **on the ND 110063 Ethernet II
controller** - the same card as our COSMOS/ENCOS firmware - and its error family names its substrate:
`AIPpiocError : PIOCOS error`, `AIPportError : fatal in IOC port message system`, `AIPxmsgError : XMSG
error`, `AIPdeadMA : medium access dead`. So the controller OS **is PIOCOS**, reached over PIOC/IOC
ports + XMSG above the media-access (MA) layer. This is documentary confirmation of what the ENCOS
firmware carve inferred from the "PIOC compatibility" I/O decode. [V-doc]

Nuance kept honest: the `AIPpiocError` proof is in the **TCP/IP (211185) on-card image** context. That
the **COSMOS ENCOS** image's OS is literally the same PIOCOS (vs a close relative) is not separately
stated in a document; the shared PIOC port + XMSG transport is strong evidence it is one OS family
across both card images. [I]

See the full documentary evidence (the two-board TCP/IP product split, TCP-on-host / IP-on-card, the
per-protocol image mechanism):
[../../../../../SINTRAN/XMSG/DOC/COSMOS-RE/HOW-ND-SHIPPED-TCPIP-PRODUCT-EVIDENCE-2026-07-26.md](../../../../../SINTRAN/XMSG/DOC/COSMOS-RE/HOW-ND-SHIPPED-TCPIP-PRODUCT-EVIDENCE-2026-07-26.md).

## 2. ENCOS - the Ethernet II board's firmware/OS

The ND-110063 Ethernet II board runs the **ENCOS** ("Ethernet COSMOS") server firmware. The docs give
its OS **no separate product name**; structurally it is a **PLANC-compiled cooperative-coroutine
kernel**, and it keeps "PIOC compatibility" I/O decoding - i.e. it is a later relative of the PIOC
family. [V-doc: `../../x/stripped/docs/ND_EthernetII_68000_Firmware_COMPLETE.md`]

PLANC modules embedded in the image (dated Apr-Aug 1986): `NCOM`, `HDLC-DR`, `ASYN-DR`, **`LOC-XMSG`**,
`MAIN`, `M-MANAG`, `PHLS-GEN`, `RT-CLOCK`, `SHORTLIB`. [V]

Hardware the firmware drives: MC68000 CPU, **Am7990 LANCE** (Ethernet), **MC68901 MFP** (timers +
GPIP in-doorbell), 512 KB DRAM. No EPROM - loaded by the host. [V]

### Doorbells (host <-> card)
- 68000 -> ND-100: write **SCIP** register `0xEF0080` (mirror `0xEF0180`) -> ND-100 interrupt level 12.
  [V] (`post_and_signal` @ `0x1A48`)
- ND-100 -> 68000: set a channel flag in `nd_channel_flags` @ `0x0B56` + raise MFP GPIP6 ->
  68000 takes MFP vector `0x4E`. [V-doc]

## 3. Subsystem docs (this folder)

- [ARCHITECTURE.md](ARCHITECTURE.md) - the whole-RTOS map: layered software stack (Mermaid), coroutine
  task model, MBOXH host handshake, and the DRAM memory map. Start here for the big picture. **NEW.**

- `SCHEDULER.md` - NOT WRITTEN, planned only: the cooperative-coroutine kernel: signal/enqueue + reaper
  primitives, continuation dispatch, the two work queues (MBOXH `0x4C2`, second queue `0x4C6`), task
  table. Until it exists, the scheduler chapter of the other PIOC-OS document set is
  [04-SCHEDULER.md](../../x/stripped/docs/PIOC-OS/04-SCHEDULER.md).
- [LOC-XMSG-CLIENT.md](LOC-XMSG-CLIENT.md) - the on-card XMSG program-to-program client: MBOXH element
  layout, the 6-word PIOC param block, the virgin XFDBK+XFWDF, **where the kernel writes the reply back
  (param P0/P2, verified in `MP-P2-PIOC-DRIV.NPL` PISAC)**, function/service/error codes, the coroutine
  model, and the two OPEN items (the `*XM-ENNS0` host-vs-card registration tension, and the ungrounded
  XRTRA trace cause). **FILLED 2026-07-26.**
- `MEMORY-MAP.md` - NOT WRITTEN, planned only: DRAM map: low mailbox `0x400-0x500`, control-block pointer
  table @ `0x4CA`, LANCE window, SCIP port `0xEF0080`, code/data banks. Until it exists, see the DRAM
  memory map in [ARCHITECTURE.md](ARCHITECTURE.md) and the memory chapter of the other PIOC-OS document
  set, [08-MEMORY.md](../../x/stripped/docs/PIOC-OS/08-MEMORY.md).

## 4. Verified anchors (seed for the subsystem docs)

| Address | Meaning | Tag |
|---------|---------|-----|
| `0x404` | alive signature / PRKEY = `0x5473`; PISTA host gate polls it | [V] |
| `0x406` / `0x408` | mailbox REQUEST / SUBFUNCTION (OPCOM dispatch) | [V] |
| `0x40A/0x40C/0x40E` | monitor postbox (counter / MON_CODE / MON_PARAM) | [V] |
| `0x414` | LNMAINIT signature `0x5555AAAA` | [V] |
| `0x4C0` | STARTED report cell | [V] |
| `0x4C2` | MBOXH activation queue head (BE 32-bit byte-ptr, LIFO) | [V] |
| `0x4C6` | second work-queue head | [V] |
| `0x4CA` | control-block pointer table (built by `0x1C6A`) | [V] |
| `0x0B56` | `nd_channel_flags` (ND->68K doorbell flags) | [V-doc] |
| `0x1A48` | `post_and_signal_nd100_scip` | [V] |
| `0x1C48` | OPCOM SUB=5 handler (self-test) | [V] |
| `0x1C6A` | control-block init (writes `0x5473`->`0x404`) | [V] |
| `0x21F8-0x2256` | scheduler signal/enqueue (commit @`0x2240`, SCIP @`0x2248`) | [V] |
| `0x226C-0x22F4` | scheduler reaper / list-walker | [V] |
| `0x7BFE / 0x7C74` | LNMAINIT (LANCE config builder; writes `0x414`) | [V] |
| `0x6722C/0x675EC/0x6766C/0x676AC` | PLANC descriptors XMRECEIVER / XMPSEND / XMPFREL / XMPFREA | [V] |

## 5. Open questions

- `*XM-ENNS0` registration: docs say host-side (XROUT `XSNET=85`, seeded by `DEFINE-REMOTE-NAME`);
  empirical card replay suggests the card's own XFWRI/XFSND-to-XROUT is what makes the name resolvable.
  These are in tension - reconcile before asserting either. [U]
- Exact division of labor between `ENCOS-MON-II` (load/monitor) and `ENNS0` (live driver), and whether
  `ENCOS-ERR-II` mediates. [U]
- ~~The OS's own product name for the Ethernet II board.~~ **RESOLVED [V-doc]: PIOCOS** - ND's own AIP
  error text `AIPpiocError : PIOCOS error` names it (see section 1). Remaining nuance [I]: proven for the
  TCP/IP image; that the COSMOS ENCOS image is literally the same PIOCOS vs a relative is not separately
  documented, but the shared PIOC-port + XMSG transport is strong evidence of one OS family.
