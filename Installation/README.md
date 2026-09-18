# Installation

**Task-oriented procedures for installing SINTRAN III and application software on Norsk Data ND-100 / ND-500 systems.**

This branch is for *how to install*, as opposed to:
- `../Operations/` — operator/admin reference manuals and analysis
- `../SINTRAN/OS/` — how the kernel works internally
- `../Reference-Manuals/` — verbatim OCR'd ND manuals

---

## Structure

| Area | Contents |
|------|----------|
| [OS/](OS/README.md) | Installing the SINTRAN III operating system on a fresh disk from distribution floppies |
| [Communication/](Communication/README.md) | Installing the communication products (COSMOS Basic, Ethernet II, TCP/IP, X.21, X.25, Network Monitor): product sheets, floppy images, extracted files, verified install guides |
| [Software/](Software/README.md) | Installing application software / subsystems on a running SINTRAN III system *(later phase)* |
| [Installation-Description/](Installation-Description/README.md) | 284 OCR'd Norsk Data "Program Description" / "Product Information" / "Installation Description" documents - the ND Software Library's per-product install/requirements sheets, covering nearly every SINTRAN III product ND shipped for ND-100/110/120/500/5000, OWS/PC and Uniline/XENIX, grouped by product family (SINTRAN III, ND-500/5000, NOTIS, NORTEXT, SIBAS/R, COSMOS, TCP/IP, SNA, hardware, patches, and more) |
| [Product-Info/](Product-Info/README.md) | 364 OCR'd Norsk Data product data-sheets (document series `ND-nnn(nn)-<rev>-<lang>`) - short marketing/technical brochures covering CPU hardware, storage, terminals, printers, communications, networking, and the software catalogue from the NORD-10 through ND-5000 era, grouped by product family |
| [Sales-Info/](Sales-Info/README.md) | OCR'd Norsk Data "Sales Information Document" sheets (document series `ND-SIDnnn-<rev>-<lang>`) - the internal, company-confidential sales sheets: positioning, configuration and upgrade paths, and the structure lists of article numbers a salesman had to quote |
| [OWS/](OWS/README.md) | The Office Work Station, incl. [getting started](OWS/GETTING-STARTED.md) from bare metal to WinLink: what OWS is, the PC half and the SINTRAN half of every product, how a workstation reaches the host (serial/INT 14h vs Ethernet/TCP-IP + Telnet), the MS-Windows products (WinLink, WinPrint, WinSMX, WinStart), the MS-DOS products (PC Starter Kit, ND Connect Module, LAN Connect, DeskTop Manager, PC-NOTIS, keyboard drivers), printing through SPRINT, SIBAS/R from the PC, and which OWS floppies the software archive holds - every claim linked to its PI/PD sheet |
| [Machines/](Machines/README.md) | The hardware itself: what box each ND-500 and ND-5000 model came in, how big it is, which cages are inside and how they are linked, and which printed circuit boards go in them - one document per cabinet under [Machines/cabinets/](Machines/cabinets/README.md), with cutaway diagrams |
| [ND-NUMBERING-REFERENCE.md](ND-NUMBERING-REFERENCE.md) | How ND article and document numbers work (used throughout this branch) |
| [INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md](INSTALL-ND-LINKAGE-LOADER-AND-BACKUP-SYSTEM.md) | Installing the ND-500 Linkage-Loader (210319H02-XX-01D) + prerequisite Backup System (210337I04-XX-01D) - verified live session walkthrough with all observed gotchas |

---

## Source material

Primary source is the version-specific SINTRAN distribution archives
(`SINTRAN-H`, `SINTRAN-K`, `SINTRAN-K05`, `SINTRAN-L`, `SINTRAN-M`), each containing:

- `Admin/` — install/init/startup command flows (`System initialisation.txt`, `install-log.txt`, `HENT-MODE.txt`, `START-SINTRAN-MULTIUSER.TXT`)
- `FILE-INFO/` — directory dumps of the golden disk (`BIGDISK0-*.txt`) and the distribution floppies (`VSX*.txt`)
- `FLOPPY/` — floppy images and notes

> **Honesty note:** Every command and file fact in this branch must be traceable to a
> source file in the distribution archive or an official ND manual. Anything inferred is marked `ASSUMPTION:`
> or `UNVERIFIED:`. Unknowns are left as explicit `TODO`.

---

**Parent:** [../README.md](../README.md)
