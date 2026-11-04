# ND-5000 (SAMSON) Documentation Index

Documentation for the ND-5000 generation (SAMSON CPUs, Octobus, ACCP access
module, ND-5800 microcode) and the RetroCore emulation of the
ND-100 <-> ND-5000 communication path.

Evidence marking used throughout: [V] = byte/live-verified, [I] =
interpretation/inference, [C] = contradiction, [UNCERTAIN] = explicitly open.

## Reading order

1. **[OCTOBUS-ND100-ND5000-REFERENCE.md](OCTOBUS-ND100-ND5000-REFERENCE.md)** -
   START HERE. The master protocol reference: one true frame format
   (C=15, B=14, station=13:8, E/K/M/S=7/6/5/4), CM* command codes,
   emergencies, kick numbers 1-6, ident resolution (40B/41B level 13),
   debunks + corrections-to-prior-analyses section.
2. **[HANDOFF-OCTOBUS-EMULATION.md](HANDOFF-OCTOBUS-EMULATION.md)** -
   State of the RetroCore emulation and the agreed remaining plan
   (phase 1 shared-memory mailbox, phase 2 mailbox-to-kick wiring,
   phase 3 MON 60B bring-up validation, phase 4 ND-5000-originated
   messages). Includes the lessons/rules that cost real time.
3. **[OCTOBUS-TEST-PROTOCOL-RE.md](OCTOBUS-TEST-PROTOCOL-RE.md)** -
   The OMD-0 "Octobus Test Protocol" (TPE OCTOBUS B00) fully reverse
   engineered: request + reply wire formats, per-command payload layouts,
   status codes, and the emulator reply recipe (section 3.6). The generic
   responder in RetroCore is built from this document.
4. **[CARVE-ANSWER-OCTOBUS-STATION-NUMBER-2026-07-18.md](CARVE-ANSWER-OCTOBUS-STATION-NUMBER-2026-07-18.md)** -
   How the own station number is obtained [V]: TPE reads INPUT STATUS (+2)
   bits 13:8 (a STATIC thumbwheel readback, valid right after master-clear
   with an empty FIFO) BEFORE any transmit; the dest-0 self-send (frame word
   0x0000) is only the cross-check (+2-pre-transmit vs +0 frame source).
   Reply detection = poll of +2 bit 3, interrupts cross-checked as
   diagnostics. SINTRAN never reads a station number (ND-5000 stations =
   constant ASTAT 070B + cpu index). Full +2/+6 bit maps from TPE's
   DECODE-STATUS-REGISTER text; new function map for octobus-b00.
5. **[ND5800-MICROCODE-ACCP-OCTOBUS-CATALOG.md](ND5800-MICROCODE-ACCP-OCTOBUS-CATALOG.md)** -
   Microcode side: every ACCP-touching routine in the ND-5800 control store
   (ACCP_READ/ACCP_WRITE/TRAP_OMESS, OCB_DEC_K kick dispatch), AFLAG
   handshake bits, TRAP_OCBM report formats.
5b. **THE ACCP FIRMWARE ITSELF - reverse engineered 2026-07-27/31, now TWO documents.**
   The ACCP's own 68000 ROM (`octo.bin`, ND-324716, December 5 1988) is the octobus
   controller's operating software. It is now **fully disassembled and fully named**:
   279 functions, zero `FUN_`, 26 hardware registers and 32 RAM globals labelled.

   - **[ANSWERS-ACCP-CPU-SEAM-CONTRACT-2026-08-04.md](ANSWERS-ACCP-CPU-SEAM-CONTRACT-2026-08-04.md)**
     - the AFLAG seam settled from the real B30 microwords: `AflagAtrapBit = 5`, FATAL is a
     trap-WORD payload (no AFLAG bit), `AobReadClearsWide = false`, and the **one-word
     condition delay** rule needed to decode any B30 bit test correctly. Answers
     [HANDOFF-ACCP-CPU-SEAM-CONTRACT-2026-08-03.md](HANDOFF-ACCP-CPU-SEAM-CONTRACT-2026-08-03.md).

   *Consolidated 2026-07-31: twelve ACCP documents were merged VERBATIM into the two
   below - nothing was summarised or dropped, and the merge was verified line by line
   (4573 source lines, 0 missing). The originals are in git history.*
   - **[ACCP-COMPLETE-REFERENCE.md](ACCP-COMPLETE-REFERENCE.md)** - everything factual
     about the card, in 6 parts:
     - *part 1* - the write-up of record. Memory map, vector table, PLANC conventions,
       every carve, and the embedded selftest microcode.
     - *part 2* - full-image sweep of every peripheral address, with the false positives
       called out.
     - *part 3* - all 43 console commands with codes, full parameter syntax and handler
       addresses. The dispatch is a linear compare chain, not a jump table.
     - *part 4* - **implementation spec for the ACCP <-> ND-5000 CPU interface**, carved
       from BOTH sides and cross-checked. The four registers (AOB/AIB/AFLAG/AOBASR)
       mapped onto the ACCP's own addresses: data pair `0x440000`/`0x550000`, gates
       `0x660001` bits 0/1, and the AOB strobe `0x330000` bit 6 (which resolves a
       previously unidentified address). Both handshakes as pseudocode, the AIB command
       channel (1/2/3), kick and trap classes, and the full CPU-model chain MFbus
       controller -> ACCP -> microcode -> `5ALIVE`. Includes the AFLAG off-by-one warning
       and a minimum viable implementation order.
     - *part 5* - **the CPU model class derivation, SOLVED 2026-07-31.** The matrix
       builder has **four** phases, not three: a second pass at `0x7DD0` rewrites every
       word (including a 7-bit Gray decode at `0x7CA2`) before the class chain reads it.
       Also the `0x220000` armed read port, and why two earlier port designs failed.
       Read this before touching any CPU-model logic.
     - *part 6* - the ACCP is **not** running PIOC-OS. Same PLANC-MC compiler, no kernel,
       no `trap #2`. Do not carry ENCOS frame offsets or descriptor widths across.
   - **[ACCP-EMULATION-STATUS-AND-HANDOFF.md](ACCP-EMULATION-STATUS-AND-HANDOFF.md)** -
     everything about the work, in 6 parts: the disassembly plan (complete, including the
     headless-Ghidra recipe that got past a GUI that would not list the ND.PLANC scripts),
     the RetroCore machine implementation handoff, the defect report, two raw command-log
     captures, and the open questions put to the ACCP team.
   - **[OCTOBUS-OBCON-PROTOCOL-AND-ACCP-DRIVER-2026-07-27.md](OCTOBUS-OBCON-PROTOCOL-AND-ACCP-DRIVER-2026-07-27.md)** -
     ND-14001 chapter 4 transcribed (16-bit software frame, acknowledge codes, octal
     station ranges, the 7 hardware-decoded messages) PLUS the carved driver:
     TX `0x770004`, RX `0x880000`, and `ObconRequestDispatch` @0xF686 with 17 function
     codes. **The dispatcher touches no hardware** - it is a software message layer.
     **Updated 2026-07-28: the information byte is DECODED** (section 1a) from
     ND-05.017.01 chapter 3 - `E K M S` flags plus a 4-bit code give emergency / kick /
     ident / multibyte-start / multibyte-end, and CMD numbers 0-15. Section 1b decodes the
     captured MFbus scan completely and specifies the expected reply as frames. One byte
     (`0x03`) remains unknown.
   - **[DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md](DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md)** -
     can we build a generic 68k octobus controller? **Yes.** ND-14001 Figure 22 draws the
     standard/device-dependent seam itself: OBA, MFA, console+trace, and the 68020 CPU part
     are all standard; only the device logic + request arbiter and the device differ.
     Includes the MFA register file (RMT/RMS/WOI/MASTA), station-number assignment, the
     two-phase node initialization, per-controller doc status (Ethernet III has almost
     nothing), and **why the ACCP is NOT a DIOC** - do not derive one from the other.

6. **[OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md](OCTOBUS-DEVICE-CONTROLLERS-ANALYSIS-AND-EMULATION-PLAN-2026-07-19.md)** -
   ALL octobus device types (station map, DOMINO DIOC module table, MFbus
   controllers), how each CPU (ND-100 / ND-5000 / DIOC) talks to devices
   (two-bus model: octobus signals, MFbus/MPM carries data; NUCLEUS
   kick-table model; PROMAN boot), the RetroCore coupling analysis, the
   reusable-octobus-objects design (OctobusFrame / OmdDispatcher /
   MultibyteAssembler / OctobusDeviceStation / ISharedMemoryWindow) and
   the phased controller-emulation implementation plan. Critically
   reviewed 2026-07-20: all phases carry ordered TODO task lists with
   verification gates.
7. **[OCTOBUS-PLAN-CRITICAL-REVIEW-2026-07-20.md](OCTOBUS-PLAN-CRITICAL-REVIEW-2026-07-20.md)** -
   The 2026-07-20 three-angle critical review of item 6 (RetroCore code /
   SINTRAN carves / hardware manuals): full findings with evidence
   (DEV-n / SIN-Fn / HW-An IDs referenced from the plan), incl. the
   kick-1-vs-kick-5 correction, the MF error-record wire direction, the
   361B=0xF1 emergency-code analysis, and the multi-CPU hardwiring list.
8. **[SCSI-DIOC-OCTOBUS-EMULATION-PLAN-2026-07-20.md](SCSI-DIOC-OCTOBUS-EMULATION-PLAN-2026-07-20.md)** -
   The SCSI controller (DOMINO SCSI DIOC, module 21B, station 13B) plan:
   carve-first sequencing (CONKI kick number, DOMDF initializer, segment
   105 interior), NucleusClient/BdioEngine architecture reusing the
   byte-verified BDIO/NUCLEUS carves, and phases S0-S5 to full SINTRAN
   disk I/O against RetroCore SCSIHDD.
8a. **[SCSI-DIOC-RETROCORE-IMPLEMENTATION-HANDOFF-2026-07-23.md](SCSI-DIOC-RETROCORE-IMPLEMENTATION-HANDOFF-2026-07-23.md)** -
   State of the RetroCore SCSI DIOC / BDIO code (2026-07-23): the components
   built + verified (MpmWindow, OctobusScsiDiocStation, BdioRecord/BdioEngine,
   BdioRecordScanner, NucleusStructures/NucleusClient, AttachScsiDioc), what is
   [V] vs [OPEN], and how to close the live tail (S2/S4) in one boot. Read
   before resuming DIOC work.
9. **[SINTRAN-OCTOBUS-MESSAGE-CATALOG.md](SINTRAN-OCTOBUS-MESSAGE-CATALOG.md)** -
   The OS side: every octobus message SINTRAN sends/expects (kick call
   sites, CMSYSPAR/CMCPURES multibyte builders, 5OMBREAD receive dispatch,
   CH5CPUPRESENT/OCSTART/XX5CONOMD startup ladders, MF-controller error
   records), with the LMFIELD record layout and M06 constant values.
10. **[DOMINO-NUCLEUS-PROMAN-2026-11-04.md](DOMINO-NUCLEUS-PROMAN-2026-11-04.md)** -
   What DOMINO, NUCLEUS and PROMAN are, the start-up order (XMSG, START-SERVERS, then the
   ND-5000), PROMAN's steps and files, the error codes, and the CPU type check in the
   NUCLEUS server (MON 262B at 036361B, goes on only for type 5 = ND-110/CX or ND-120/CX
   with 32-bit floating point) that stopped all three on nd100x.

## Related documentation elsewhere

| Topic | Where |
|---|---|
| Octobus card register layout + protocol intro | [..\Devices\Octobus\](../Devices/Octobus/README.md) |
| ND-500 side of octobus HW + MON 60 subfunction table | [..\ND500\ND500-BUS-OCTOBUS-HW-INTERFACE.md](../ND500/ND500-BUS-OCTOBUS-HW-INTERFACE.md) |
| Shared-memory mailbox / X500DF / X5FIF spec (phase 1) | [..\ND500\ND500-BUS-INTERFACE-REFERENCE.md](../ND500/ND500-BUS-INTERFACE-REFERENCE.md) sections 6.5 + 7.5 |
| ND-500 mailbox message catalog (MON call stop records) | [..\ND500\ND500-MAILBOX-MESSAGE-CATALOG.md](../ND500/ND500-MAILBOX-MESSAGE-CATALOG.md) |
| Carved SINTRAN driver bodies (SOCTO/SKICK/MBSEND/...) | ..\..\tools\sintran-segment-carver\versions\L-VSX-500\re\segments-ref\026-S3IMPIT\026-S3IMPIT.asm |
| NPL sources (PH-P2-OPPSTART, MP-P2-N500, 5P-P2-MON60) | [..\NPL-SOURCE\NPL\](../NPL-SOURCE/README.md) |

External (outside this repo):
- Hardware manual: E:\Dev\Ronny\ND5000UC\manual\ND-05.020.01 EN ND-5000 Hardware Description.md (ch. 5 The Access Module + Appendix 2 Octobus Protocol v5)
- Microcode disassemblies: E:\Dev\Ronny\ND5000UC\microcode\MICRO-5800-B30.md / -A30.md + MAILBOX-MICROCODE-PSEUDOCODE.md
- Emulator + tests: E:\Dev\Repos\Ronny\RetroCore\Emulated.HW\ND\CPU\NDBUS\ (NDBusOctobus.cs, OctobusFabric.cs, OctobusND5000Station.cs) + Emulated.Tests.ND100\ControllerOctobus\

## Status snapshot (2026-07-16)

- Octobus frame/card/ACCP layer: DONE and live-verified (TPE tests 1-3 pass,
  CONFIGURATION D05 NO ERRORS, idents 40B/41B level 13).
- OMD-0 Test Protocol responder: implemented from the byte-verified spec;
  unit tests green; awaiting live TPE tests 4-6 rerun.
- Shared-memory mailbox layer (X5SEMA/X5FIF): NOT implemented - phase 1 of
  the handoff plan.

---

*Last Updated: 2026-07-16*
