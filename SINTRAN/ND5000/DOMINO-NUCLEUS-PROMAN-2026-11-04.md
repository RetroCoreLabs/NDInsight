# DOMINO, NUCLEUS and PROMAN - what they are and how they start

Three names that come up whenever an ND-5000 system boots: **DOMINO** (the I/O controller cards),
**NUCLEUS** (the message system that ties CPUs and controllers together) and **PROMAN** (the
server on the ND-100 that boots the controllers). This document says what each one is, the order
they start in, the files they use, the error codes they print, and one check that stops all
three on the wrong CPU type: the NUCLEUS server reads the CPU type and gives up unless it is 5.
That check was found on 2026-11-04 while getting the ND Backup Manager to install on nd100x.

Evidence marks, as in the rest of this folder: **[V]** = checked in the bytes, on a running
machine or word for word in a manual (the source is named); **[I]** = a conclusion drawn from
[V] facts; **[UNCERTAIN]** = open.

Short names for the sources:

| Short | Source |
|---|---|
| **M** | [ND-820026.1 DOMINO and NUCLEUS Software Guide](../../Reference-Manuals/500/ND-820026.1%20EN%20DOMINO%20and%20NUCLEUS%20Software%20Guide.md) |
| **RL / RM / RN** | SINTRAN III release information, [L](../Release-Documentation/ND-860230-6-EN%20Sintran%20III%20-%20Release%20Information%20-%20L-Version.md), [M](../Release-Documentation/ND-860230-7A-EN%20SINTRAN%20III%20-%20Release%20Information%20-%20M-Version.md) and [N](../Release-Documentation/ND-860230-8-EN%20SINTRAN%20III%20-%20Release%20Information%20-%20N-version.md) versions |
| **SA** | [ND-830147-3 ND-5000 ES System Administrator Guide](../../Reference-Manuals/500/ND-830147-3-EN%20ND-5000%20ES%20System%20Administrator%20Guide.md) |
| **MC** | [ND-860228-2 SINTRAN III Monitor Calls](../../Reference-Manuals/ND-860228-2-EN%20SINTRAN%20III%20Monitor%20Calls.md) |
| **DNI** | the segment carves in [`domino-nucleus-io/`](../../tools/sintran-segment-carver/versions/L-VSX-500/re/domino-nucleus-io/README.md) (SINTRAN L07 image) |
| **nd100x** | measured on 2026-11-04 in the nd100x emulator, on copies of its `ND5000.IMG` pack |

Line numbers below are lines in the markdown files.

Deeper material already exists and is not repeated here:
[NUCLEUS-OCTOBUS-ND5000-COMPLETE-REFERENCE-2026-08-24.md](NUCLEUS-OCTOBUS-ND5000-COMPLETE-REFERENCE-2026-08-24.md)
(the NUCLEUS calls, the microcoded fast path, the octobus) and
[DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md](DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md)
(the DOMINO card hardware).

---

## 1. The three in one paragraph each

**DOMINO** is a family of I/O controller cards for the ND-5000, each built round a Motorola
MC68020 (M:72). Each card runs a small operating system, DOMINOS, and moves its data straight to
and from the shared memory on the MF-bus; the octobus (a serial bus) carries only short messages
and set-up data (M:691-695, M:775-777). The cards have module numbers: 5B VMEI, 20B IPI3,
21B SCSI, 22B ETH3, 23B FPS5, 24B TERM, 25B GRAP, 26B MFCC, 27B VMEC, 30B DMAC (M:1045-1056).
A machine with no DOMINO card still runs NUCLEUS and PROMAN; PROMAN then reports that it found no
controllers (section 5). [V, M]

**NUCLEUS** is "a library for fast message passing" between processes inside ONE computer, where
the computer is the main CPUs plus the DOMINO controllers that share the same memory and octobus
(M:837-843). Its tables live in shared memory (M:847). On the ND-5000, four calls are done in
microcode (nkMove, nkSend, nkReceive, nkGetInfo); all other calls run on the ND-100 (M:6192-6194).
On the ND-100 side it is two RT programs: the NUCLEUS server **NKSERV** and the name server
**NKNAME** (RL:2691-2697), in segments 104/105 (S3SNKSE/S3INKSE) and 106/107 (S3SNKNA/S3INKNA)
(RL:2579-2582). Programs reach it with monitor call 347B, NUCL (RL:1604-1606). [V, M + RL]

**PROMAN** (Processor Manager) is a system server on the ND-100, "started immediately after system
start" (M:917). It boots the DOMINO controllers at start-up or power-up, reboots them, gives them
their configuration, stops them and handles power failure (M:917-927). The release notes call it
"DOMINO boot process" (RL:2694) and later "Process Manager Server" (RM:3694). It is in segments
120/121 (S3SPRMA/S3IPRMA) (DNI/PROMAN-AUTORUN-RECON.md:28-35). [V, M + RL + DNI]

Other servers started the same way: MTSERV (NUCLEUS MTAD server), BOPCOM and EVMESG, which the
L notes list with no description (RL:2691-2697). [V, RL]

---

## 2. Start-up order

### 2.1 What ND says

1. SINTRAN starts. NKSERV, NKNAME and PROMAN are RT programs and stay passive until something
   starts them.
2. **XMSG** is started.
3. `@START-TADADM` (usually in the XMSG start file).
4. **`@START-SERVERS`**, which only user SYSTEM may give (RL:952-960). It starts every passive
   server that comes with SINTRAN.
5. **Then the ND-5000** (`LOAD-CONTROL-STORE`, `START-SWAPPER` in the ND-500 monitor).

Steps 2-5 are from the installation note ND-895061-1A
([line 343](../../Installation/Installation-Description/ND-895061-1A-EN.md)): put `@START-SERVERS`
in LOAD-MODE:MODE or LOAD-SYSTEM:BATC "after starting the XMSG (and after the command
@START-TADADM ...) and before starting the ND-5000". The L notes say the same in short: "If you
are using DOMINO devices, include the command @START-SERVERS ... before starting the ND-500/5000
part of the system" (RL:517). [V, manuals]

`@LIST-SERVERS` shows how each server was started: 0 = by hand (or not to be started),
1 = at SINTRAN start-up, 2 = by START-SERVERS (RL:918-923). The example listing in SA:2742-2753
shows NKSERV 2, NKNAME 0, PROMAN 2, ERS3WD 1, BOPCOM 2, MTSERV 2. [V, manuals]

The manual's own sentence "the servers are started by SINTRAN itself" (M:6429) does not match
those start codes (NKSERV and PROMAN are 2, not 1). [UNCERTAIN] which one describes L07.

The installation note for TCP/IP warns that "the installation will fail if PROMAN is passive" and
says to check it with `@LIST-RT-DESCRIPTION PROMAN`
([ND-895061-2-EN.md:304-318](../../Installation/Installation-Description/ND-895061-2-EN.md)). [V]

### 2.2 What one real pack does - nd100x `ND5000.IMG`

The pack's boot batch file `(SYSTEM)LOAD-MODE:BATC` follows the order above [V, nd100x, read off
the pack]:

```
@ENTER SYSTEM,,,
@SINTRAN-SERVICE-PROGRAM
@START-XMSG
@EXIT
@HOLD 3 2
@START-SERVERS
@HOLD 10 2
@(SYSTEM)ND-500-MON-J
LOAD-CONTROL-STORE,,,,
START-SWAPPER
EXIT
```

Measured while the batch runs [V, nd100x]:

- About 16-20 s after log-in the batch is inside the ND-500 monitor. A terminal that tries to
  enter the monitor at that moment is turned away with
  `ND-500(0) error: ND-500(0) reserved for special use`, and `LOAD-CONTROL-STORE` /
  `START-SWAPPER` answer `Other user(s) already logged on ND-500(0)` (the ND-500 Loader Monitor
  manual lists "OTHER USERS ALREADY LOGGED ON N500"; error 2034 in the SINTRAN K release notes).
- The other way round too: a terminal that sits in the ND-500 monitor blocks the batch's own
  `LOAD-CONTROL-STORE`. So a script must enter the monitor only for its commands and leave it
  straight after.
- The monitor's `VERSION` command shows whether the ND-5000 is running. Not started:
  `Swapper.......: ` (empty) and `Micro program.:     0`. Started:
  `Swapper.......: REV.-K01` and `Micro program.: 11930`.

The nd100x install scripts (`tools/installs/install_common.py`, `start_nd5000()` in the nd100x
repository) start the ND-5000 this way: `VERSION` first, start it only if it is not running, read
every `ND-500(0) error:` line, `VERSION` again, and try again 5 s later while the batch has the
monitor.

### 2.3 Why the order matters

PROMAN's first steps set up memory areas (LAMU buffers, M:1312) and NUCLEUS takes "first available
memory in multiport memory" at start-up (M:6425). A LAMU is a "Logically Addressed Memory Unit",
memory that several CPUs can share (SA:3707-3708). The SCSI document in this repository says that in
the wrong order the ND-5000 takes the shared memory first and the servers stop with
"No LAMU area big enough" (SINTRAN error 277B, MC:26288)
([SCSI-STORAGE-UNDER-SINTRAN.md:1339-1347](../Devices/SCSI/SCSI-STORAGE-UNDER-SINTRAN.md)).
[I] - the manuals give the order but not that error for this case, and it was not measured here.

---

## 3. PROMAN, step by step

The manual's algorithm (M:1310-1327), in plain words [V, M]:

1. Check the configuration is right (an ND-5000). **This check stops on nd100x with the wrong CPU
   type; see section 6.**
2. Set up the ERS log file (ERS is ND's system error report service).
3. Set up the LAMU buffers, the time queue and its own tables.
4. Start octobus and NUCLEUS communication.
5. Start the threads for the ERS gateway and the service port.
6. Find the configuration: find every MF-bus controller (one per card crate), ask each one for the
   crate's contents ("investigate-bank", then "list-configuration" per DOMINO card), then let the
   file `PMA-CONFIG` override what was found.
7. Start one boot thread for each DOMINO controller, then wait for events for ever.

Booting one controller (M:1366-1391): hard reset, open the image file, echo test (EchoTest), read
the card's identity and self-test result (IdentY), stop it (Stop), then for each block of the
image set the mailbox pointer (SetBxP) and download the block (BxDoLd); finally put the start
address in the card's program counter (RegMod), start it (Go-On) and run a watchdog loop. The
error strings for these steps are in the segment (DNI/PROMAN-AUTORUN-RECON.md:49-60). [V, M + DNI]

PROMAN does not try every octobus station; it talks only to controllers it found in step 6
(DNI/PROMAN-AUTORUN-RECON.md:163-177, from the manual's algorithm and the segment's strings, not a
trace). [I]

On the carved L07 image, after a full boot with XMSG started, PROMAN and NKSERV are passive with
P = 0: they never ran
([list-rt-programs.txt:62, 65](../../tools/sintran-segment-carver/versions/L-VSX-500/inputs/list-rt-programs.txt)).
[V, DNI]

---

## 4. Files

| File | What it is | Source |
|---|---|---|
| `(SYSTEM)PMA-CONFIG:SYMB` | Optional. Overrides the configuration PROMAN found; "for testing, debugging and exception cases". | M:1083 |
| `(SYSTEM)PMA-ERS-BUFFER:DATA` | PROMAN's event log, a ring file. 5 pages by default, at least 2, must be contiguous. PROMAN creates it if it is missing. | M:1463 |
| `<PMA>-<hardware id>[-<software id>]:IMAG` | The software image for one controller type, for example `PMA-SCSI-BDIO:IMAG`. Kept under user UTILITY. | M:985-1014, M:1043 |
| `PMA-DUMP-LOG`, `PMA-MONITOR`, `PMA-ERS:NRF` | Tools: print the log (run as SYSTEM), watch PROMAN, ERS reports. | M:1492, M:1553, M:1526 |

PROMAN's service port is called `PMAservicePort` (M:1539); the segment also holds
`PMAersGateWay`, `PMAhomePort` and `PMA-EVENT-LOG` (DNI/PROMAN-AUTORUN-RECON.md:49-51). [V]

### 4.1 PMA-ERS-BUFFER:DATA needs access for user RT [V, nd100x]

No manual names the user PROMAN runs as. On `ND5000.IMG`, once PROMAN ran at all (section 6), it
printed

```
Not read, write and common access          (code 1B:12B)
Unable to log events to ring buffer file   (code 1050B:36B)
```

and could not use `(SYSTEM)PMA-ERS-BUFFER:DATA`. SYSTEM's friend RT had read, write and append
(RWA) but not common (C). With the friend RT given RWAC, and C for friends on the file, both
messages went away. [I] So PROMAN uses the file with user RT's rights, which fits it being an RT
program. Which user NKSERV and NKNAME run as is [UNCERTAIN].

---

## 5. Messages and error codes

ND prints these codes in two forms. The manual tables give one octal number (105016B); the console
splits it into a module part and a number, `1050B:16B`. [I] The split is the number written as
`<first four digits>B:<last two digits>B`; the M notes print ERS codes the same way (RM:3247,
3333), but no source states the rule outright.

Code ranges by module (RM:3296-3335): 101000B-101077B NUCLEUS, 101100B-101177B NUCLEUS operations,
105000B-105077B PROMAN, 006000B DOMINOS, 006200B DOMINO services. [V, RM]

The codes met on nd100x, and others in the same family:

| Code | Console form | Text | Kind | Source |
|---|---|---|---|---|
| 105016B | 1050B:16B | Error in Nucleus initialisation | FATAL | M:9621 |
| 105035B | 1050B:35B | No Domino controllers found in system | WARN | M:9649 |
| 105036B | 1050B:36B | Unable to log events to ring buffer file | WARN | M:9650 |
| 105037B | | This ND-100 is not master in system | | M:9651 |
| 105041B | | Server started | INFO | M:9662 |
| 105046B | | Server stopped | INFO | M:9667 |
| 101025B | 1010B:25B | Nucleus not started (nke_NOTINITIALISED) | | M:9879 |
| 101035B | | Not correct hardware configuration (nke_ILLHARDWARE) | | M:9887 |
| 101105B | | Unable to get Cpu type | FATAL | M:9973 |

Full tables: PROMAN codes 105000B-105051B (M:9597-9672); NUCLEUS library errors 101000B-101045B
(M:9841-9895) and which call can return which (M:9903-9943); NUCLEUS operation codes
101100B-101120B (M:9951-9986). The DOMINO SCSI guide adds 105321B "Operation rejected by PROMAN"
([ND-814009-1-EN:3577](../../Reference-Manuals/500/ND-814009-1-EN%20DOMINO%20SCSI%20Operator%20Guide.md)).
[V]

---

## 6. The CPU type check in the NUCLEUS server

### 6.1 What was seen [V, nd100x]

On `ND5000.IMG` with nd100x's ND-5000 machine set to `cpu = 100`, about 90 s after boot, PROMAN
printed on the console:

```
Nucleus not started                 1010B:25B
Not read, write and common access   1B:12B
Error in Nucleus initialisation     1050B:16B   FATAL
Server stopped
```

It did this whether `@START-SERVERS` was typed by the boot batch, typed by hand, or typed with no
ND-5000 started at all, and on an older pack where Backup Manager backups had worked. So it was not
the batch and not the ND-5000; PROMAN was waiting for a NUCLEUS that never started. Those lines
came in the middle of installer questions and broke the install scripts.

### 6.2 Why: NKSERV gives up unless the CPU type is 5 [V]

The NUCLEUS server NKSERV (segment 105 S3INKSE, load address 030000B) asks SINTRAN for the system
information and goes on only if the CPU type is above 4. Found with the debugger on nd100x, and
the same code is at the same addresses in the carved L07 segment
(`segments/105-S3INKSE.bin` in the carver folder, bytes swapped for `nd100-dis`; the file is
stored big-endian):

```
036346  146547  RADD AD1 CLD SL DX     ; routine entry (PLANC frame)
...
036357  170400  SAA 0                  ; A = 0: the number, must be 0
036360  054612  LDX ,B -166            ; X = address of a 12-word buffer
036361  153262  MON 262                ; GetSystemInfo (CPUST)
036362  124007  JMP 7                  ; error return
036363  171401  SAX 1
036364  047610  LDA I ,B ,X -170       ; buffer word 1 = bytes 2 and 3
036365  156470  SHA ZIN SHR 10         ; keep the high byte: byte 2, the CPU type
036366  004606  STA ,B -172
...
040314  044613  LDA ,B -165            ; the CPU type
040315  171004  SAT 4
040316  141065  SKP IF DA GRE ST       ; type > 4 ?
040317  124042  JMP 42                 ; no -> 040361
040320  170401  SAA 1                  ; yes: result 1, go on
...
040361  170400  SAA 0                  ; no: result 0
```

The one `MON 0` (leave the program) in the segment is at 105474B. On nd100x the server reached
the "no" path and ended without printing anything; PROMAN, waiting for it, later reported
"Nucleus not started". [V, debugger and CPU trace on nd100x]

The manual's table for byte 2 of the GetSystemInfo buffer (MC, GetSystemInfo, page 286) [V]:

| Byte 2 | CPU |
|---|---|
| 2 | ND-100 with 48-bit floating point |
| 3 | ND-100 with 32-bit floating point |
| 4 | ND-110/CX or ND-120/CX with 48-bit floating point |
| 5 | ND-110/CX or ND-120/CX with 32-bit floating point |

So **only type 5 passes**: an ND-110/CX or ND-120/CX with the 32-bit floating point option.
nd100x's `cpu = 100` gave type 2. [I] That a real ND-5000 system was always sold with an ND-110/CX
or ND-120/CX front end with 32-bit floating point is what this check implies; no manual found says
so. The manuals only say NUCLEUS needs an ND-5000, or an ND-500 model II with the octobus line
driver ND-324133 level D or ND-324118 level G (RL:339-341, RN:355-358).

The NUCLEUS code 101105B "Unable to get Cpu type" (M:9973) is not what this check prints; it ends
silently. Which routine prints 101105B is [UNCERTAIN] (not carved).

### 6.3 The fix on nd100x [V, nd100x]

With the ND-5000 machine set to `cpu = ND120CX` and `fpp = 32` (nd100x `config/ND5000.ini`, and
the same lines in the install scripts' machine settings), NKSERV, NKNAME and PROMAN all run. What
is left is true and harmless:

- `No Domino controllers found in system` (1050B:35B), because nd100x has no DOMINO card;
- the access messages of section 4.1, gone once user RT has the C right.

After that, the five ND installers in nd100x `tools/installs/` (BACKUP-SYSTEM I05, the ND-500
monitor as a reentrant subsystem, Linkage-Loader H02, LINKER B01, Backup Manager B02) run one
after another on `ND5000.IMG` with its boot batch in place.

---

## 7. Open questions

1. Which user NKSERV and NKNAME run as.
2. Which routine prints 101105B "Unable to get Cpu type", and whether NKNAME or PROMAN make their
   own CPU check as well.
3. Which code reads the START-SERVERS start-code table (in segment 003 S3CP,
   DNI/PROMAN-AUTORUN-RECON.md:109-118), and how M:6429 "started by SINTRAN itself" fits the start
   codes.
4. How much LAMU / shared memory NUCLEUS and PROMAN need. The defaults (M:6396-6408) are known; the
   minimum is not.
5. What EVMESG is (RL:2695 leaves it blank).
6. What PROMAN's crate questions look like as bytes. The controller software and the
   `PMA-*:IMAG` files are not in this repository (DNI/README.md:66-69).
7. Whether "DOMINO-MODE" (a Backup Manager setting that makes BM search for DOMINO tape drives,
   [SCSI-STORAGE-UNDER-SINTRAN.md:1325-1328](../Devices/SCSI/SCSI-STORAGE-UNDER-SINTRAN.md)) is
   defined in any ND manual. None found.

## Related

- [NUCLEUS-OCTOBUS-ND5000-COMPLETE-REFERENCE-2026-08-24.md](NUCLEUS-OCTOBUS-ND5000-COMPLETE-REFERENCE-2026-08-24.md) - NUCLEUS calls, function codes, status codes, the microcoded fast path.
- [DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md](DOMINO-DIOC-GENERIC-CONTROLLER-ARCHITECTURE-2026-07-28.md) - DOMINO card hardware.
- [SINTRAN-OCTOBUS-MESSAGE-CATALOG.md](SINTRAN-OCTOBUS-MESSAGE-CATALOG.md) - SINTRAN's own octobus messages at start-up.
- DNI: [NUCLEUS-SEGMENTS-RECON.md](../../tools/sintran-segment-carver/versions/L-VSX-500/re/domino-nucleus-io/NUCLEUS-SEGMENTS-RECON.md), [NKSE-SERVER-INTERIOR-CARVE.md](../../tools/sintran-segment-carver/versions/L-VSX-500/re/domino-nucleus-io/NKSE-SERVER-INTERIOR-CARVE.md), [NUCLEUS-PRIMITIVES-CARVE.md](../../tools/sintran-segment-carver/versions/L-VSX-500/re/domino-nucleus-io/NUCLEUS-PRIMITIVES-CARVE.md), [PROMAN-AUTORUN-RECON.md](../../tools/sintran-segment-carver/versions/L-VSX-500/re/domino-nucleus-io/PROMAN-AUTORUN-RECON.md).
- [CARVING-HANDOFF.md](../CARVING-HANDOFF.md) section 1.9 - summary of the NUCLEUS and DOMINO carves.
- [SCSI-STORAGE-UNDER-SINTRAN.md](../Devices/SCSI/SCSI-STORAGE-UNDER-SINTRAN.md) - Backup Manager on the SCSI streamer, DOMINO-MODE, boot order.
