# XMSG — SINTRAN III message system

Everything about **XMSG** (eXchange MeSsaGe), the SINTRAN III / COSMOS / NORD-NET
inter-process and inter-node message system invoked through monitor call **200B**:
the wire format, the programming API, the official ND constant definitions, a C#
implementation, and the superseded notes it was distilled from.

> **Working with the live machines? Read [LAB.md](LAB.md) FIRST.** It holds the machine folders,
> terminal and HDLC ports, the XMSG bring-up sequence, and the traps that have each cost days —
> notably that **an adjacent system must NOT be given a route**, and that SINTRAN runs its link on
> exactly one HDLC controller. Machine-readable form: [`lab-topology.json`](lab-topology.json).

> **The C# library has moved to [RetroIO](https://github.com/RetroCoreLabs/RetroIO)**
> (`RetroIO.Protocols.Xmsg.*`), where it is built, tested and documented
> (<https://retrocorelabs.github.io/RetroIO/>). The copy in [SRC/](SRC/) is the older one and is no
> longer developed. The recordings that the notes in [DOC/](DOC/README.md) cite by file name were
> renamed on 2026-10-18 to say what they show (date, medium, what, from and to); the
> `pcap/MANIFEST.md` in the X25Emulator repository maps every old name to its new one.

## Folder layout

| Path | Contents |
|------|----------|
| **[LAB.md](LAB.md)** | The live lab: machines, ports, bring-up, capture recipe, and the known traps. Start here before touching D100/D102/D103 |
| **[DOC/](DOC/README.md)** | The documentation set - core specs (below) plus the LAPB/TAD work, the COSMOS application RE, and the dated investigation log; see [DOC/README.md](DOC/README.md) for the full index |
| **[SRC/](SRC/)** | The **working C# implementation** — 1001 tests over 26 projects. Wire formats, the MON 200B kernel model (27 of 48 functions, all 48 accounted for), a COSMOS **FA file server** that reads, writes, creates, deletes and lists files against a real ND-100, a **folder-watch sync daemon** that mirrors a Windows folder onto a SINTRAN user directory unattended, a **chat system**, a TAD terminal server, and the HDLC/LAPB/Ethernet transports. See [SRC/README.md](SRC/README.md) |
| **[OLD/](OLD/)** | Superseded / historical notes, kept for provenance only ([OLD/README.md](OLD/README.md)) |
| `XMSG-PL-VALUES-M.INCL` | The **official ND include file** (PLANC `CONSTANT`s) — XMSG version M, 1988-08-18. The source of truth for all numeric values. |
| `XMSG-VALUES-M.SYMB` | The same value set as assembler `SYMBOL`s (flagged `@DEC` = decimal). |
| `xmsg-constants.json` | Machine-readable constants generated from the `.INCL` (consumed by the docs and the C# enum generator). |


## Proved against a real ND-100

Everything below was done against D100 and confirmed **on the machine**, not from our own logs.

| What | Evidence |
|---|---|
| **Read a file off the ND** | 20400 bytes pulled, SHA256 identical to the original |
| **Create a file by a quoted new name** | 20400 bytes written; D100's own file server reported the file back at that size |
| **The folder-watch sync daemon, unattended** | dropped a file in a watched folder, touched nothing on D100, and `LIST-FILES` showed `FILE 80 : (PACK-ONE:SYSTEM)WATCH3:TXT;1` |
| **APPEND-REMOTE-BATCH** | D100 acknowledged the letter and answered with our serial echoed |

Two rules that cost the most time to learn and are now settled:

 - **The Flags 1 law** - one datagram counter per (sender, peer) pair, zeroed only by a
   reachability exchange, never reset in use. See `DOC/XMSG-PROTOCOL.md` section 4.2.
 - **The envelope seed is a per-link constant**, so it is remembered across runs
   (`xmsg-link-seed.state`). That is what lets us address a machine that has not spoken to us
   since we started - and it is remembered, never invented.

## Documentation (DOC/)

| Document | Scope |
|----------|-------|
| [DOC/XMSG-PROTOCOL.md](DOC/XMSG-PROTOCOL.md) | **Wire format** — HDLC framing, LAPB, the 14-byte SINTRAN header, packet subtypes (incl. the `0x03` ACK), the XMSG sub-header, and the ROUTING/TAD/DC/PAD sub-protocols. What the bytes on the line mean. |
| [DOC/XMSG-API.md](DOC/XMSG-API.md) | **Programming / API** — the MON 200B calling convention, T-register option bits, the XROUT "letter" / standard-message format, magic numbers / ports / names, secure-message semantics, and the **complete constant catalog**. |
| [DOC/XMSG-COMMAND-REFERENCE.md](DOC/XMSG-COMMAND-REFERENCE.md) | **Operator utility** — the `XMSG-COMMAND` program (network management commands, tracing, dumps). |
| [DOC/COSMOS-RE/](DOC/COSMOS-RE/README.md) | **COSMOS application RE** - four COSMOS ND-100 programs (CONNECT-TO, FA server, File Transfer, XFTRA) decoded in Ghidra: how applications actually use MON 200B, with C# reconstructions. |

The full DOC index (LAPB requirements, TAD analyses, capture plans, and the dated
question/answer investigation log) is in [DOC/README.md](DOC/README.md).

The HDLC hardware / COM5025 / DMA layer *beneath* XMSG is documented separately in
[../HDLC-Frame-Format-Reference.md](../Devices/HDLC/HDLC-Frame-Format-Reference.md).

## Where this knowledge came from (provenance)

- **Official ND symbol files** (`XMSG-PL-VALUES-M.INCL` / `.SYMB`, version M) — authoritative for every constant.
- **[X-MESSAGE version L program description, 210373L](../../Installation/Installation-Description/ND-210373L-EN.md)** (1988-02-02, 37 pages) — ND's own account of what changed in version L: register specs for `XFDUM`, `XFGST`, **`XFGSM`**, `XFCPV`, the XROUT services `XSGAT`/`XSLKI`/`XSNET`/`XSNSI`/`XSLIN`/`XSDAT`/`XSLSY`/`XSGSU`/`XSGSG`, the XMFIDO watchdog letter layouts, and the new error codes. **It documents things Appendix A does not** — `XFGSM` was recorded here for months as "no evidence exists" purely because it is absent from the Programmer Guide. Check this before concluding a function is undocumented.
- **[COSMOS Programmer Guide ND-60.164](../../Operations/Cosmos/ND-60164-3-EN%20%20COSMOS%20Programmer%20Guide.md)** (XMSG version J, OCR) — the programming model, the XROUT letter/standard-message byte format, and the service semantics.
- **FCS-validated packet captures** (nodes 100/102/103) in the sibling **X25Emulator** repository (`pcap/`), decoded independently to confirm the wire format and discover the `0x03` ACK.
- **The Wireshark dissector** [../Devices/HDLC/WireShark/hdlc_tcp.lua](../Devices/HDLC/WireShark/hdlc_tcp.lua), which implements `DOC/XMSG-PROTOCOL.md`.

Each documented fact is tagged VERIFIED / SYMBOLS / INFERRED / CAPTURE-SPECIFIC,
with the source-precedence rule (captures > dissector > symbol tables > earlier
prose) recorded in the docs.

## Regenerating the constants / enums

`xmsg-constants.json` is generated from the `.INCL`; the C# enums are generated
from the JSON. See [SRC/README.md](SRC/README.md) for the commands.

## What we do not know

[`DOC/WHAT-WE-DO-NOT-KNOW.md`](DOC/WHAT-WE-DO-NOT-KNOW.md) is the standing register of open
questions - what blocks a task, what we guess at on the wire, and what would settle each.
**Look there before starting a hunt**, and add a row when a new unknown turns up.

## The protocol registry

[`DOC/protocols/README.md`](DOC/protocols/README.md) holds machine-readable definitions of the wire - every field
and every **bit**, with a status (MEASURED / INFERRED / UNKNOWN / SUPERSEDED) and an evidence
pointer. `ProtocolRegistryConformanceTests` fails if the C# and the registry disagree, so
**a protocol change goes in both in the same commit**.
