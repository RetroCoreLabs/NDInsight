# OWS - the Norsk Data Office Workstation

OWS is Norsk Data's **Office Work Station**: a PC/AT-compatible MS-DOS machine sold by ND
and integrated into a SINTRAN installation, so that the disk space, printers, documents and
databases of an ND-100/ND-500/ND-5000 host are available from the PC.

> "Your office workstation is an integral part of the organization's computer network... Disk
> space, files and printers on the minicomputer are available for the workstation users"
> - [ND-250-3-EN Office Workstation OWS-85](../Product-Info/ND-250-3-EN.md)

Every OWS product therefore has **two halves**, and both must be installed:

| Half | Runs on | Examples |
|---|---|---|
| PC side | MS-DOS on the OWS (later MS-Windows 2.x/3.x) | WinLink, WinPrint, WinSMX, PC-NOTIS, DeskTop Manager, ND Connect Module |
| Host side | SINTRAN III on ND-100/500/5000 | OWS Access Server, OWS Terminal Line Server, TCP/IP, SPRINT, DS, UE, SIBAS backend |

A PC product that "does not work" almost always means the host half is missing - that is the
single most common thread through the Installation Descriptions collected here.

---

**Setting one up?** [GETTING-STARTED.md](GETTING-STARTED.md) walks the whole path - boot from
floppy, partition and format the disk, install MS-DOS, the ND-OWS layer and PC Starter Kit, the
keyboard drivers, the Connect Module for Ethernet, MS-Windows 2.10 with ND's drivers, then WinSMX,
WinLink and WinPrint - quoting the installers and the diskettes at each step.

## 1. The hardware

| Product | ND-no | Notes | Sheet |
|---|---|---|---|
| Office Workstation OWS-85 | ND-250 (PI sheet) | 80386 at 16 MHz, PC/AT compatible, optional 80387; sold with ND DeskTop Manager | [ND-250-3-EN](../Product-Info/ND-250-3-EN.md) |
| OpenLAN OWS Adaptors | ND-110386 (Ethernet), [ND-110394](../Product-Info/ND-110394-A1-EN.md) (Cheapernet) | the OWS network cards | [ND-110394-A1-EN](../Product-Info/ND-110394-A1-EN.md) |
| Ethernet Adapter/PC, /MC | ND-110683, ND-110758 | PC-bus and Micro Channel adapters named in the PC-NOTIS sheets | [ND-895535-1-EN](../Installation-Description/ND-895535-1-EN.md) |
| Ethernet II / III Controller (host) | [ND-110063](../Installation-Description/ND-895070-1A-EN.md), [ND-110513](../Installation-Description/ND-895566-1-EN.md) | the ND-100/500 side of the wire | [ND-895520-1-EN](../Installation-Description/ND-895520-1-EN.md) |
| OpenLAN Terminal Interface Unit, Network Control Server, MAC Bridge | [ND-110577](../Product-Info/ND-110577-A1-EN.md), [ND-110578](../Product-Info/ND-110578-A1-EN.md), [ND-110587](../Product-Info/ND-110587-A1-EN.md) | OpenLAN infrastructure | [ND-110577-A1-EN](../Product-Info/ND-110577-A1-EN.md) |

## 2. How an OWS reaches the ND host

Two transports, and they are not interchangeable.

**Serial / terminal line.** The PC behaves as a terminal. Programs use INT 14h or INT 6Bh, and
the host end is the **OWS Terminal Line Server ([ND-211295](../Installation-Description/ND-895017-S1-EN.md))**, which gives access to SINTRAN
resources such as SPRINT and NOTIS-DS.

> "ND LAN Connect makes it possible for ND applications running on a PC to reach different
> SINTRAN resources via network adapters that supports the interrupt 14 or interrupt 6B
> (hexadecimal) interface" - [ND-895556-1-EN](../Installation-Description/ND-895556-1-EN.md)

**Ethernet / TCP-IP.** The PC runs a TCP/IP stack (packet drivers, NDIS); the host runs ND's
TCP/IP and its **Telnet server**, and the terminal session is Telnet.

> ND prerequisites for the OWS access servers: "TCP/IP, TELNET Server, DS Server, UE Server",
> with "SPRINT Server (Printing facilities)" and "SIBAS backend" optional
> - [ND-211297-1-EN](../Installation-Description/ND-211297-1-EN.md)

The SINTRAN TCP/IP product itself is described as being there "to allow use of TCP/IP protocols
by applications (FTP, TELNET) in a SINTRAN environment on a Ethernet local area network", and
its installer asks for the number of Telnet server connections, up to 124
([ND-895061-2-EN](../Installation-Description/ND-895061-2-EN.md)).

| Host-side communication product | ND-no | Sheet |
|---|---|---|
| OWS Access Server (DS, UE, SSY, SIBAS for up to 16 OWS) | [211297A](../Installation-Description/ND-211297-1-EN.md) | [ND-211297-1-EN](../Installation-Description/ND-211297-1-EN.md) |
| OWS Terminal Line Server | [211295](../Installation-Description/ND-895017-S1-EN.md) | [ND-895017-S1-EN](../Installation-Description/ND-895017-S1-EN.md) |
| TCP/IP Basic Module/III | [211327](../Installation-Description/ND-895061-1A-EN.md) | [ND-895061-2-EN](../Installation-Description/ND-895061-2-EN.md) |
| COSMOS TCP/IP Gateway for Ethernet | [211185](../Installation-Description/ND-895070-1A-EN.md) | [ND-895070-2-EN](../Installation-Description/ND-895070-2-EN.md) |
| OpenLAN TCP/IP Access Module/II, /III | 211488, [211324](../Installation-Description/ND-895087-S1-EN.md) | [ND-895087-S1-EN](../Installation-Description/ND-895087-S1-EN.md) |
| CMS Access Server for ND-500/5000 | [211325](../Installation-Description/ND-895060-2-EN.md) | [ND-895060-2-EN](../Installation-Description/ND-895060-2-EN.md) |
| SINTRAN NFS Support / NFS Server | [211299](../Installation-Description/ND-895520-1-EN.md) | [ND-895520-1-EN](../Installation-Description/ND-895520-1-EN.md) |
| NORTEXT Access Server | [211486](../Installation-Description/ND-895273-S01-EN.md) | [ND-230115-3-EN](../Installation-Description/ND-230115-3-EN.md) |

The host must be SINTRAN III **K or later** for the PC-NOTIS family; [ND-211297](../Installation-Description/ND-211297-1-EN.md) lists ND-100
(all), ND-110 Satellite, S5/S9/T9/T17, ND-500 and ND-5000 (VSX K or later) as supported hosts,
and requires X-MESSAGE (210373 L), TCP/IP ([211185](../Installation-Description/ND-895070-1A-EN.md) B), User Environment ([210518](../Installation-Description/ND-895092-1A-EN.md)), Document
Storage ([210691](../Product-Info/ND-210691-A2-EN.md)) and SPRINT ([211056](../Installation-Description/ND-895191-04-NO.md)).

### What the ND Connect Module actually is

ND's own sheet says only that it "will install CONNECT.EXE and all necessary TCP/IP software on
directory `\ND-OWS\COMMS`" ([ND-895499-1A-EN](../Installation-Description/ND-895499-1A-EN.md)).
The diskette itself (`CONNECTB00`, preserved in the software archive, all files dated March/April
1991) shows what that means: **Connect is not a TCP/IP stack. It is ND's transport layer that sits
on top of whichever stack the PC already has**, so that ND applications need to know only one
interface.

| File on the diskette | Bytes | What its own banner says |
|---|---|---|
| `CONNECT.EXE` | 26 079 | `OWS FC - CONNECT B00 Ethernet version [27/03/91 12:29]` - the resident loaded from `AUTOEXEC.BAT` |
| `FTPSW.EXE` | 8 341 | `SLIB - RESIDENT TRANSPORT MODULE FTP SW PC/TCP A00` |
| `3OPEN.EXE`, `INTERLAN.EXE`, `ILANA.EXE`, `UB.EXE`, `DATACO.EXE` | 6-11 KB each | the same kind of module for 3+Open, Interlan, Ungermann-Bass and Dataco |
| `LANCONN.EXE` | 56 624 | packet assembly - `CONAssemblePacket`, `CONDisAssemblePacket`, `CONNECT-MAXPACKET-SERIAL` |
| `INT14.COM` | 3 271 | `INT 14 interface for Connect, release A00 ... (C) Norsk Data A.S` |
| `NAALIBW.DLL` | 37 892 | the MS-Windows side (`NAACONNECTVERSION`) |
| `NDIS/ELNKII.DOS` | 10 158 | NDIS driver for the 3Com EtherLink II card |
| `SETINT.EXE`, `SETTRACE.EXE` | | set the interrupt vectors, switch tracing on |

So the shape is: **one resident per vendor stack ("SLIB - resident transport module"), a common
Connect resident above it, and two interrupt vectors** - the installer script `INSTALL.DAT` on the
diskette pins them down:

```
@Qstring @SlibInt = "6dh"      the transport module hooks INT 6Dh
@Qstring @ConnInt = "69h"      Connect presents itself on INT 69h
```

with INT 66h taken by the packet driver (`PKTDRVND.SYS` / `DISPKTPM.DOS`) on NDIS adaptors, and
`INT14.COM` offering the INT 14h serial interface for programs that speak to a COM port.

**The TCP/IP stack itself is a separate purchase.** ND's 3Station sheet is explicit: "To be able to
do a complete installation of ND PC Starter Kit, Connect and S-Link, please observe that you need
the PC/TCP kernel - NDIS Ethernet floppy", and its A03 version "is able to use the 2.04 P1 1
version of PC/TCP Kernel NDIS Ethernet"
([ND-895498-1A-EN](../Installation-Description/ND-895498-1A-EN.md)). PC/TCP is FTP Software's
product - which is exactly what `FTPSW.EXE` is the transport module for.

Read that way, the pieces line up: the PC gets a vendor TCP/IP kernel and its NDIS or packet
driver; Connect binds to it through the matching SLIB module; WinLink, WinPrint and the rest call
Connect on INT 69h and never know which network product is underneath.

### The three installation modes, and the six TCP/IP packages

The installer script `INSTALL.DAT` on the `CONNECTB00` diskette asks two questions, and they
decide everything about how the PC reaches the host.

**First question - which kind of Connect:**

```
The Connect Module B00 supports, in addition to the standard TCP/IP packages
as mentioned in the PI-sheet, the standard "Interrupt 6Bh Interface"
(Mini-session or NACS as some vendors call it) and the BIOS INT 14h interface.

  21 = "Normal Connect Module installation"
  22 = "Interrupt 6Bh based Connect"
  23 = "Int 14h based Connect"
```

| Mode | What it means |
|---|---|
| **21 Normal** | The real thing: a TCP/IP stack on the PC, with Connect's own resident transport module (SLIB) bound to it. Only this mode asks the second question. The script sets `@DoSlib = 1`, copies the chosen vendor module to `DRIVERS\SOCKRES.EXE`, and adds `%ND-OWS%\DRIVERS\SOCKRES` to `AUTOEXEC.BAT` after the `SET ND-OWS=` line. |
| **22 INT 6Bh** | No TCP/IP at all. INT 6Bh is Novell's **NASI/NACS** interface - NetWare Asynchronous Services Interface, served by a NetWare Asynchronous Communications Server. A TSR on the workstation gives applications access to a *pool of modems or serial lines* on a server: a specific line can be requested, calls are released quickly, and throughput is better than the INT 14h method. ND's wording "Mini-session or NACS as some vendors call it" is exactly this. |
| **23 INT 14h** | The lowest common denominator. INT 14h is the PC BIOS serial-port service; a network product hooks the vector so a program that believes it is talking to COM1 is in fact carried over the LAN or a terminal server. ND ships its own shim for this on the same diskette - `INT14.COM`, whose banner reads `INT 14 interface for Connect, release A00 ... (C) Norsk Data A.S`. |

So 21 is TCP/IP, while 22 and 23 are ways of reaching the host over somebody else's serial or
async infrastructure without a TCP/IP stack.

**Second question (mode 21 only) - which stack is on the PC:**

```
Please select your TCP/IP package:
  1 = "FTP Software TCP/IP"     4 = "Ungermann-Bass TCP-PC"
  2 = "3+Open TCP/IP"           5 = "Racal InterLan TCP/IP"
  3 = "DataCo TCP/IP"           6 = "Bridge ILANA TCP/IP"
```

Each choice copies a different resident module - `ftpsw.exe`, `3open.exe`, `dataco.exe`, `ub.exe`,
`interlan.exe`, `ilana.exe` - to the same target name, `DRIVERS\SOCKRES.EXE`. They are the six
DOS TCP/IP products a Norwegian or Scandinavian ND customer was likely to already own around
1990-91:

| Option | Product | What it was |
|---|---|---|
| 1 | **FTP Software PC/TCP** | The best known DOS TCP/IP stack of the period. FTP Software wrote the **Packet Driver specification** in 1986 and released it as an open standard in December 1988; PC/TCP itself used an external TCP/IP kernel (`ETHDRV.EXE`) that applications called. ND's own sheets name it as the prerequisite "PC/TCP kernel - NDIS Ethernet floppy" ([ND-895498-1A-EN](../Installation-Description/ND-895498-1A-EN.md)), and the module on the diskette announces itself as `SLIB - RESIDENT TRANSPORT MODULE FTP SW PC/TCP A00`. |
| 2 | **3+Open TCP/IP** | 3Com's networking suite; 3+Open was 3Com's variant of the OS/2 LAN Manager line, NDIS-based. This is also why the Installation Description says "If you are installing on a client running 3+Open client software, choose 4 NDIS from the menu". |
| 3 | **DataCo TCP/IP** | Scandinavian networking supplier. No public description of their DOS TCP/IP product turned up in this research; recorded here as what the diskette says it supports, nothing more. |
| 4 | **Ungermann-Bass TCP-PC** | UB of Santa Clara, whose flagship was Net/One; their products began on XNS and moved to TCP/IP as it became the standard late in the 1980s. |
| 5 | **Racal InterLan TCP/IP** | Interlan, a Massachusetts LAN adapter maker, acquired by Racal - their PC Ethernet cards and stack. |
| 6 | **Bridge ILANA TCP/IP** | Bridge Communications, a direct UB competitor that merged with 3Com in 1987; ILANA was their PC LAN adapter product line. |

Connect binds to the package, and the package owns the card. That is the whole answer to "which
Ethernet cards are supported": whichever the chosen TCP/IP package supports.

### Which Ethernet cards work

**ND's own adaptors** are the ones the sheets name: **ND 110386** OpenLAN OWS adaptor for Ethernet
(thick cable, external transceiver, 15 m transceiver cable supplied) and **ND 110394** for
Cheapernet (built-in transceiver, T-connector). Both are "delivered with TCP/IP software"
([ND-110394-A1-EN](../Product-Info/ND-110394-A1-EN.md)), so they arrive with the stack Connect then
binds to. Also named: Ethernet Adapter/PC ND 110683 and Ethernet Adapter/MC ND 110758.

**The 3Com EtherLink II** is the only card with a driver on the Connect diskette itself -
`NDIS/ELNKII.DOS`. That is the **3C503**: an 8-bit ISA card, 10 Mbit/s, BNC coax and AUI (a
twisted-pair variant exists), jumpered to I/O 0x250-0x2E0 or 0x300-0x350. It has little on-board
memory, which is why NFS implementations of the era advise 4 KB read/write buffers with it. Its
presence on the diskette is convenience, not a requirement.

**An NE2000 works if the chosen TCP/IP package has a driver for it** - Connect never touches the
hardware. The NE2000 was Novell's 16-bit ISA card of 1988 and became the de facto standard that
countless clones copied, so packet drivers (`NE2000.COM`) and, later, NDIS drivers for it were
everywhere; PC/TCP in particular is a packet-driver stack. Nothing in ND's documentation names the
NE2000 either way - the archive holds no ND sheet that lists supported third-party cards - so this
is an inference from how the layering works, not a statement by ND.

## 3. The MS-Windows products - WinLink, WinPrint, WinSMX, WinStart

These are the Windows 2.x/3.x generation of OWS software.

| Product | Product no. quoted in PI | Media/part no. seen on the diskettes | PI sheet |
|---|---|---|---|
| **WinLink** - terminal emulation, file transfer, clipboard, backup to the host | **ND 230210** ([ND-891092EN1](../../Reference-Manuals/ND-891092EN1%20How%20to%20install%20WinLink.md) p2, [ND-860452EN1](../../Reference-Manuals/ND-860452EN1%20WinLink%20User%20Guide.md) p4) | `30210` (`30210NO1A00`..`NO5A00`) | [ND-610-1-EN](../Product-Info/ND-610-1-EN.md) |
| **WinPrint** - print from Windows on a printer attached to the ND server | - | `30211` (`30211NO1A00`) | [ND-611-1-EN](../Product-Info/ND-611-1-EN.md) |
| **WinSMX** - the SMX starter/menu that launches WinLink | ND 230119 | `30212` (`30212NO1A00`) | named in [ND-610-1-EN](../Product-Info/ND-610-1-EN.md) |
| **WinStart** - alternative starter | ND 230118 | not held | named in [ND-610-1-EN](../Product-Info/ND-610-1-EN.md) |

**WinLink** (ND-610-1-EN) does: link to a SINTRAN server and work as a terminal; copy files both
ways; copy text out of SINTRAN into any Windows program through the clipboard; back up PC files
to the server; set screen colours; choose the server (Ethernet only); set communications
parameters (serial only). It is "compatible with Microsoft Windows/286 and Microsoft
Windows/386 version 2" and requires the **PC Starter Kit ([ND 230123](../Installation-Description/ND-895499-1A-EN.md))**, for Ethernet the
**ND Connect Module (ND 230125)**, and either **WinSMX (ND 230119)** or **WinStart (ND 230118)**
to start it with.

The programs on the WinLink diskettes in the archive: `NDTERM.EXE` and `NDTERM-S.EXE` (terminal),
`EASYLINK.EXE` (file transfer), `NDETHSEL.EXE` (choose Ethernet server), `NDSERSET.EXE` (serial
parameters), `INSTMAIN.EXE`/`SETUP.BIN` (installer), and per-language screen fonts
`TD2xx15/25/48/70/84.FON` for NO, SW, DA, EN, US, NL.

ND's own two WinLink manuals are in this repository and add to that picture:

- **The product number is ND 230210** - *"To install WinLink (ND 230210) you need"*
  ([ND-891092EN1 "How to install WinLink"](../../Reference-Manuals/ND-891092EN1%20How%20to%20install%20WinLink.md),
  page 2) and *"WinLink has the product number ND 230210."*
  ([ND-860452EN1 "WinLink User Guide"](../../Reference-Manuals/ND-860452EN1%20WinLink%20User%20Guide.md),
  page 4). The User Guide is dated *"Copyright © 1991 by Norsk Data a.s   Version 1 February 1991"*.
- **Windows version - the sources disagree.** ND-891092EN1 page 2 requires *"An IBM-compatible PC
  running Microsoft Windows 3"*; ND-610-1-EN says WinLink is compatible with Windows/286 and
  Windows/386 version 2. Both are recorded here; nothing in this repository reconciles them.
- **Prerequisites** (ND-891092EN1 page 2): PC Starter Kit [ND 230123](../Installation-Description/ND-895499-1A-EN.md) *"version A04 or newer"*; for
  Ethernet the ND Connect Module ND 230125; on the host, for Ethernet, OWS Access Server [ND 211297](../Installation-Description/ND-211297-1-EN.md)
  on SINTRAN 100 or [ND 211325](../Installation-Description/ND-895060-2-EN.md) on SINTRAN 500/5000, and for serial the OWS Terminal Server [ND 211295](../Installation-Description/ND-895017-S1-EN.md),
  which *"is a part of PC Starter Kit"*. That folder does **not** list WinSMX or WinStart as a
  prerequisite, although ND-610-1-EN does. It also calls [ND 211325](../Installation-Description/ND-895060-2-EN.md) the "OWS Access Server", where
  §2 above tables it as the CMS Access Server for ND-500/5000 after ND-895060-2-EN.
- **Terminal type 93.** *"When asked for terminal type, answer 93!"* (ND-860452EN1 page 5).
- **Neither manual names a protocol.** No mention of TCP/IP, Telnet or FTP appears in either; they
  say only "OpenLAN network (Ethernet)" or "a serial cable". The Telnet statement in §2 above rests
  on ND-211297-1-EN and ND-895061-2-EN, not on these manuals.

The installation procedure, configuration dialogs, EasyLink file transfer and the full error-message
list are written up in [GETTING-STARTED.md](GETTING-STARTED.md) §5.2.1-§5.2.5.

**WinPrint** (ND-611-1-EN) "lets you print out files from MS-Windows programs directly on a
printer attached to a Norsk Data SINTRAN server... Any printer defined in your ND server's
SPRINT system can be used as if it were local." Its diskette holds `SPRINT.SYS`, `LPT2SPR.SYS`
(LPT2 to spooler redirector), `SPRINT.EXE` and `NDSELSPR.EXE` (choose the SPRINT printer).

**WinSMX** diskette: `SMXINIT.EXE`, `SMXLIB.EXE`, `SMXEDIT.EXE`, `WINSMX.HLP`.

Note the number question: the PI sheets quote 2301xx product numbers, while the diskette labels
carry 302xx media numbers (`30210` WinLink, `30211` WinPrint, `30212` WinSMX). Both appear in
ND's own paperwork; which one a catalog should file them under is a decision, not a fact.

## 4. The MS-DOS products

| Product | ND-no | What it is | Sheet |
|---|---|---|---|
| ND PC Starter Kit | [230123](../Installation-Description/ND-895499-1A-EN.md) | the base PC software every other product builds on; contains the OWS Terminal Line server client | [ND-895499-1A-EN](../Installation-Description/ND-895499-1A-EN.md) |
| ND Connect Module | **[380723A](../Installation-Description/ND-895499-1A-EN.md)** (PI of WinLink calls it ND 230125) | installs `CONNECT.EXE` and the TCP/IP software into `\ND-OWS\COMMS`; needs MS-DOS >= 3.2; INT 66 used by `PKTDRVND.SYS`/`DISPKTPM.DOS` on NDIS adaptors | [ND-895499-1A-EN](../Installation-Description/ND-895499-1A-EN.md) |
| ND LAN Connect | [211656A](../Installation-Description/ND-895556-1-EN.md) | reaches SINTRAN resources over INT 14h/6Bh through the OWS Terminal Line Server | [ND-895556-1-EN](../Installation-Description/ND-895556-1-EN.md) |
| ND DeskTop Manager for OWS | 230025 | terminal emulator + file transfer, the shell the OWS was sold with | quoted in [ND-895538-1-EN](../Installation-Description/ND-895538-1-EN.md), [ND-250-3-EN](../Product-Info/ND-250-3-EN.md) |
| PC-ET Communications SW | 230033 | the older Ethernet communications package | [ND-230115-3-EN](../Installation-Description/ND-230115-3-EN.md) |
| Nortext Software Distribution (NSD) | [230115C](../Installation-Description/ND-230115-3-EN.md) | unattended update of PC files from an FTP host; Ethernet only | [ND-230115-3-EN](../Installation-Description/ND-230115-3-EN.md) |
| 3Station Start Volume | 380722A | boot volume for the ND-110948 3Station/2E netstation | [ND-895498-1A-EN](../Installation-Description/ND-895498-1A-EN.md) |
| Keyboard drivers for NOTIS PC Keyboard | [380697A](../Installation-Description/ND-895487-1A-EN.md) | `KEYBOARD.COM`, `NDKEYB.COM`, `NTXKEYB.COM`, keyboard tables per language | [ND-895487-1A-EN](../Installation-Description/ND-895487-1A-EN.md) |
| Keyboard Drivers for NORTEXT Enhanced Keyboard | [230189A](../Installation-Description/ND-895558-1-EN.md) | as above, enhanced keyboard | [ND-895558-1-EN](../Installation-Description/ND-895558-1-EN.md) |
| Butterfly-110 PC system software | [230001A](../Installation-Description/ND-230001-1-EN.md) | the ND Butterfly PC | [ND-230001-1-EN](../Installation-Description/ND-230001-1-EN.md) |

### PC-NOTIS - the office suite on the PC

| Product | ND-no | Sheet |
|---|---|---|
| PC-NOTIS Platform | [230142A](../Installation-Description/ND-895533-1-EN.md) | [ND-895533-1-EN](../Installation-Description/ND-895533-1-EN.md) |
| PC-NOTIS Server for ND-500/5000 (host side) | [230143A](../Installation-Description/ND-895534-1-EN.md) | [ND-895534-1-EN](../Installation-Description/ND-895534-1-EN.md) |
| PC-NOTIS WP | [230144N](../Installation-Description/ND-895535-1-EN.md) | [ND-895535-1-EN](../Installation-Description/ND-895535-1-EN.md) |
| PC-NOTIS CALC | [230145E](../Installation-Description/ND-895536-1-EN.md) | [ND-895536-1-EN](../Installation-Description/ND-895536-1-EN.md) |
| PC-NOTIS ID (electronic mail in a COSMOS network) | [230146B](../Installation-Description/ND-895537-1-EN.md) | [ND-895537-1-EN](../Installation-Description/ND-895537-1-EN.md) |
| PC-NOTIS DS (document storage) | [230147D](../Installation-Description/ND-895538-1-EN.md) | [ND-895538-1-EN](../Installation-Description/ND-895538-1-EN.md) |

Each of these PI sheets names the same host requirements: SINTRAN III >= K, User Environment
[210518](../Installation-Description/ND-895092-1A-EN.md), PC-NOTIS Server [230143](../Installation-Description/ND-895534-1-EN.md), NOTIS-DS [210794](../Installation-Description/ND-210794-S3-EN.md), and **one of** OWS Terminal Line Server [211295](../Installation-Description/ND-895017-S1-EN.md) /
OpenLAN TCP/IP Access Module/II 211488 / OpenLAN TCP/IP Access Module/III 211324.

### Third-party PC software sold for the OWS

| Product | ND-no | Sheet |
|---|---|---|
| EXCEL for OWS | [230026](../Installation-Description/ND-95008-1-EN.md) | [ND-95008-1-EN](../Installation-Description/ND-95008-1-EN.md) |
| Micrografx Designer | [230042A](../Installation-Description/ND-895041-1-EN.md) | [ND-895041-1-EN](../Installation-Description/ND-895041-1-EN.md), [ND-230042-A1-EN](../Product-Info/ND-230042-A1-EN.md) |
| Micrografx Graph Plus | [230044A](../Installation-Description/ND-895040-1-EN.md) | [ND-895040-1-EN](../Installation-Description/ND-895040-1-EN.md), [ND-230044-A1-EN](../Product-Info/ND-230044-A1-EN.md) |
| LED for OWS (Language Editor) | 230050 | see [Product-Info/README.md](../Product-Info/README.md) |

## 5. Printers and printer queues

Printing from an OWS is **SPRINT**, ND's spooling system on the host - not a local queue.

- The OWS-85 sheet: "you can print out on printers connected to the workstation, or centrally
  shared ND minicomputer printers connected to the ND-SPRINT spooling system"
  ([ND-250-3-EN](../Product-Info/ND-250-3-EN.md)).
- **SPRINT** is [ND-211056](../Installation-Description/ND-895191-04-NO.md) (an older number 210506 also appears); version >= A02 is the one the
  other products ask for ([ND-210938-3-EN](../Installation-Description/ND-210938-3-EN.md),
  [ND-211033-3-EN](../Installation-Description/ND-211033-3-EN.md)).
- The **SPRINT Server** is the optional half of the OWS Access Server that gives PCs access to
  those queues ([ND-211297-1-EN](../Installation-Description/ND-211297-1-EN.md)).
- **WinPrint** and its `LPT2SPR.SYS` map a PC printer port onto a SPRINT queue, so any printer
  defined in SPRINT is usable as if local ([ND-611-1-EN](../Product-Info/ND-611-1-EN.md)).
- Behaviour worth knowing: with SPRINT A02 installed, NOTIS-DRAW and NOTIS-BG append drawings to
  the SPRINT queue instead of the SINTRAN spooling queue, and plotters are defined to SPRINT as
  LINE-PRINTER with the header page turned off
  ([ND-211019-2-EN](../Installation-Description/ND-211019-2-EN.md),
  [ND-210793-3-EN](../Installation-Description/ND-210793-3-EN.md)).
- NOTIS-WP prints through SPRINT as well, and its error messages come back from SPRINT
  ([ND-210792-2-EN](../Installation-Description/ND-210792-2-EN.md)).

## 6. SIBAS and SIBAS/R from the OWS

The database half of the OWS story: the PC runs a client, the ND host runs the backend.

| Product | ND-no | Sheet |
|---|---|---|
| SIBAS/R (data management, the family sheet) | [211212A](../Product-Info/ND-211212-A2-EN.md) | [ND-211212-A2-EN](../Product-Info/ND-211212-A2-EN.md) |
| SIBAS/R Backend | [211404B](../Installation-Description/ND-895207-2-EN.md), also quoted as [220004B](../Installation-Description/ND-895628-1-EN.md) | [ND-895207-3-EN](../Installation-Description/ND-895207-3-EN.md), [ND-895628-1-EN](../Installation-Description/ND-895628-1-EN.md) |
| SIBAS/R Client (PC) | [380853B](../Installation-Description/ND-895602-1-EN.md) (package ND-220003B) | [ND-895602-1-EN](../Installation-Description/ND-895602-1-EN.md) |
| SIBAS/R Server | [380855B](../Installation-Description/ND-895604-1-EN.md) | [ND-895604-1-EN](../Installation-Description/ND-895604-1-EN.md) |
| SIBAS/R Softkey / Softkey for Development Access | [380920B](../Installation-Description/ND-895627-1-EN.md) / [220005B](../Installation-Description/ND-895603-1-EN.md) | [ND-895627-1-EN](../Installation-Description/ND-895627-1-EN.md), [ND-895603-1-EN](../Installation-Description/ND-895603-1-EN.md) |

The OWS Access Server lists SIBAS backend as one of its optional services, and the TCP/IP
Installation Description records a fix for "SIBAS Backend over TCP/IP" connections being closed
by `HandleSibdata` when storing wide columns
([ND-895061-1A-EN](../Installation-Description/ND-895061-1A-EN.md)) - i.e. SIBAS/R traffic from
a PC rides the same TCP/IP stack as Telnet and FTP.

## 7. What a working OWS installation actually needs

1. **Host:** SINTRAN III (K or later for the NOTIS-era products) with TCP/IP + Telnet server, or
   the OWS Terminal Line Server for serial/INT 14h.
2. **Host services** as required: DS (Document Storage [210691](../Product-Info/ND-210691-A2-EN.md)), UE (User Environment [210518](../Installation-Description/ND-895092-1A-EN.md)),
   SPRINT ([211056](../Installation-Description/ND-895191-04-NO.md)) for printing, SIBAS backend for the database, X-MESSAGE (210373) underneath
   the OWS Access Server.
3. **PC base:** MS-DOS >= 3.2, ND PC Starter Kit ([230123](../Installation-Description/ND-895499-1A-EN.md) - WinLink asks for **version A04 or
   newer**, [ND-891092EN1](../../Reference-Manuals/ND-891092EN1%20How%20to%20install%20WinLink.md)
   page 2), and for Ethernet the ND Connect Module with its packet/NDIS drivers into
   `\ND-OWS\COMMS`.
4. **PC applications:** DeskTop Manager, PC-NOTIS, or the Windows generation - WinSMX/WinStart
   to start, WinLink (230210) for terminal and file transfer, WinPrint for printing.

## 8. What the software archive holds

MS-DOS floppies in the [norskdata-software-archive](https://github.com/RetroCoreLabs/norskdata-software-archive),
grouped by the ND number carried in the FAT volume label:

| Label group | Disks | Labels | Likely product |
|---|---|---|---|
| 30210 | 5 | `30210NO1A00` .. `30210NO5A00` | WinLink (Norwegian) |
| 30211 | 1 | `30211NO1A00` | WinPrint (Norwegian) |
| 30212 | 1 | `30212NO1A00` | WinSMX (Norwegian) |
| 30025 | 10 | `30025NO1C02`, `30025NO2C02`, `30025SW1C00`, `30025SW2C00` | Desk Top Manager for OWS |
| 30022 | 6 | `30022SW1N06`, `30022XX2N06` | NOTIS-WP for MS-DOS |
| 30021 | 10 | `30021SV1B01` .. `30021SV4B01` | MS-Windows 2.10 with ND drivers |
| 30001, 30002, 30003, 30006, 30008 | 11 | `30001EN1A01`, `30002EN1A00`, `30003EN1A00`, `30006EN1A05`, `30008XX1A01` | ND-OWS system disks: MS-DOS, ND-OWS drivers, EGA/VGA, Windows |
| 38095 | 1 | `380952XXA0` | ND keyboard drivers for DOS and VKM |

Plus unlabelled DOS disks (`CONNECTB00` = ND Connect Module, `PCSTART-NO2` = PC Starter Kit,
`INSTALL1`..`INSTALL4`, `ND-DRIVERE` = MS-Windows 2.10 with ND drivers).

## 9. Sources

Everything above is quoted or tabulated from these files in this repository. Where a statement
could not be traced to one of them it is marked as a question rather than a fact.

- Product Information: [ND-250-3-EN](../Product-Info/ND-250-3-EN.md) (OWS-85),
  [ND-610-1-EN](../Product-Info/ND-610-1-EN.md) (WinLink),
  [ND-611-1-EN](../Product-Info/ND-611-1-EN.md) (WinPrint),
  [ND-110394-A1-EN](../Product-Info/ND-110394-A1-EN.md) (OpenLAN OWS Adaptors),
  [ND-211212-A2-EN](../Product-Info/ND-211212-A2-EN.md) (SIBAS/R),
  [ND-230042-A1-EN](../Product-Info/ND-230042-A1-EN.md), [ND-230044-A1-EN](../Product-Info/ND-230044-A1-EN.md),
  [ND-95008-1-EN](../Installation-Description/ND-95008-1-EN.md) (EXCEL for OWS)
- Installation / Program Descriptions: [ND-211297-1-EN](../Installation-Description/ND-211297-1-EN.md) (OWS Access Server),
  [ND-895017-S1-EN](../Installation-Description/ND-895017-S1-EN.md) (OWS Terminal Line Server),
  [ND-895499-1A-EN](../Installation-Description/ND-895499-1A-EN.md) (ND Connect Module),
  [ND-895556-1-EN](../Installation-Description/ND-895556-1-EN.md) (ND LAN Connect),
  [ND-895533-1-EN](../Installation-Description/ND-895533-1-EN.md) .. [ND-895538-1-EN](../Installation-Description/ND-895538-1-EN.md) (PC-NOTIS),
  [ND-895061-2-EN](../Installation-Description/ND-895061-2-EN.md) (TCP/IP Basic Module/III),
  [ND-895070-2-EN](../Installation-Description/ND-895070-2-EN.md) (COSMOS TCP/IP Gateway),
  [ND-230115-3-EN](../Installation-Description/ND-230115-3-EN.md) (NSD),
  [ND-895487-1A-EN](../Installation-Description/ND-895487-1A-EN.md), [ND-895558-1-EN](../Installation-Description/ND-895558-1-EN.md) (keyboard drivers),
  [ND-895602-1-EN](../Installation-Description/ND-895602-1-EN.md) .. [ND-895628-1-EN](../Installation-Description/ND-895628-1-EN.md) (SIBAS/R),
  [ND-895520-1-EN](../Installation-Description/ND-895520-1-EN.md) (NFS)
- User and installation manuals:
  [ND-891092EN1 How to install WinLink](../../Reference-Manuals/ND-891092EN1%20How%20to%20install%20WinLink.md),
  [ND-860452EN1 WinLink User Guide](../../Reference-Manuals/ND-860452EN1%20WinLink%20User%20Guide.md)
- Diskette contents read directly from the images in the software archive (file lists, `INFO.TXT`,
  `INFOPRIV.TXT`).

## 10. Open questions

1. **Two numbering schemes for the Windows products.** PI sheets say WinSMX = ND 230119,
   WinStart = ND 230118, Connect Module = ND 230125, and the WinLink manuals say WinLink = ND
   230210; the Connect Module's own Installation Description says [380723A](../Installation-Description/ND-895499-1A-EN.md), and the diskettes carry
   30210/30211/30212. No document here reconciles them - not even 230210 against the `30210` on
   WinLink's own diskette labels.
2. ~~**WinLink's own product number**~~ - **answered: ND 230210.**
   [ND-891092EN1 "How to install WinLink"](../../Reference-Manuals/ND-891092EN1%20How%20to%20install%20WinLink.md)
   page 2 and
   [ND-860452EN1 "WinLink User Guide"](../../Reference-Manuals/ND-860452EN1%20WinLink%20User%20Guide.md)
   page 4 both state it. ND-610-1-EN still does not.
3. **ND-100 as an OWS host.** [ND-211297](../Installation-Description/ND-211297-1-EN.md) lists ND-100 (all) as supported for the access servers,
   while the PC-NOTIS sheets name only ND-500/5000. Whether the Windows-era products were ever
   used against an ND-100 is unresolved here.
4. **WinPrint's product number** is missing from the PI sheet; only the media number 30211 is
   known from the diskette.
5. **Which Microsoft Windows version WinLink needs.** ND-891092EN1 page 2 says Windows 3;
   ND-610-1-EN says Windows/286 and Windows/386 version 2. Whether these are two releases of
   WinLink, or one statement is simply wrong, is not answered by any document here. Neither
   manual carries a version number for WinLink itself that would separate them.
6. **What WinLink speaks on the wire.** Neither WinLink manual names a protocol; §2 above derives
   Telnet from the host-side sheets. Nothing here shows a WinLink terminal session being Telnet.
