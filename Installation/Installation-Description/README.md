# Installation-Description — Norsk Data Program Description / Installation Documents

**289 OCR'd Norsk Data "Program Description" (PD), "Product Information" (PI), "Installation Description" and internal delivery-list documents** — the ND Software Library's per-product install/requirements sheets, covering nearly every SINTRAN III product ND ever shipped for ND-100/110/120/500/5000, OWS/PC and Uniline/XENIX systems.

Each document is a short, standardised form: product name, ND document number, prerequisites (SINTRAN version, computer type, floating format), and referenced manuals. Some are internal-only "Delivery List" / "Product Structure Sheet" documents listing the diskettes and manuals shipped for a release rather than describing the product itself — these are marked accordingly below.

**One exception worth knowing about:** [210373L X-MESSAGE](./ND-210373L-EN.md) is a full 37-page technical document, not a short form. ND filed it as a Program Description and it carries the usual install procedure, but most of it is register-level specification of the XMSG functions and XROUT services that changed in version L. It is the only place in this repository that documents several of them.

---

## Document Index

### SINTRAN III Core

| Product | Document # | Type | Description |
|---|---|---|---|
| **[SINTRAN Utility Programs (File System Investigator)](./ND-10022-20-EN.md)** | ND-10022-20-EN | PD | FILESYS-INV utility to check and update disc directories, loaded from floppy on SINTRAN alone. |
| **[SINTRAN III version J](./ND-10174-10-EN.md)** | ND-10174-10-EN | PD | SINTRAN III J-version change/addition covering VSE/VSX/VSX-500 modules and full documentation set. |
| **[BACKUP-SYSTEM](./ND-10337-2-EN.md)** | ND-10337-2-EN | PD | File copying and backup sub-system for SINTRAN III, loaded from floppy ND-10337B. |
| **[SINTRAN III Configuration Program](./ND-895031-S1A-EN.md)** | ND-895031-S1A-EN | Delivery List | Delivery list for SINTRAN III Configuration Program E02, with note not to auto-ship over existing E01 customers. |
| **[SINTRAN MS-DOS Service](./ND-895054-S01-EN.md)** | ND-895054-S01-EN | Delivery List | Delivery list for SINTRAN MS-DOS Service rev A, its manual and diskette. |
| **[SINTRAN Socket Library](./ND-895175-S1-EN.md)** | ND-895175-S1-EN | Delivery List | Internal delivery list for SINTRAN Socket Library, manual, PI-sheet and diskette. |
| **[SINTRAN NFS Support](./ND-895520-1-EN.md)** | ND-895520-1-EN | PI | Lets a ND-5000 SINTRAN system act as an NFS server (not client) giving OWS/UNIX workstations transparent file access. |
| **[SINTRAN III Monitor Call Package](./ND-895546-1-EN.md)** | ND-895546-1-EN | PI | ND-100/ND-500/5000 monitor call interface library for COBOL, FORTRAN, PASCAL, and PLANC compilers. |

---

### ND-500 / ND-5000 System Software

| Product | Document # | Type | Description |
|---|---|---|---|
| **[ABM for ND-500](./ND-210718-3-EN.md)** | ND-210718-3-EN | PD | System development/maintenance tool for transaction-oriented apps using SIBAS/COBOL/FORTRAN on ND-500. |
| **[FORTRAN Crosscompiler for ND-100 running on ND-500](./ND-210863-7-EN.md)** | ND-210863-7-EN | PD | ANSI 77 FORTRAN cross-compiler running on ND-500 producing ND-100/NORD-10 code, v.G error correction. |
| **[ND-500 Swapper](./ND-211034-8-EN.md)** | ND-211034-8-EN | PD | Memory management (swapper) program for ND-500, lists compatible control-store microprograms. |
| **[ND-500/5000 Swapper](./ND-211034-9-EN.md)** | ND-211034-9-EN | PD | Swapper memory-management program extended to also support ND-5000 (workmode 406) alongside ND-500. |
| **[ND-500/2 Micro Test Programs II](./ND-211041-2-EN.md)** | ND-211041-2-EN | PD | Improved TPE-based microcode diagnostic/test suite for ND-500/2 CX with TELEFIX support. |
| **[ND-500/5000 System Package for SINTRAN III/VSX version L](./ND-895030-1A-EN.md)** | ND-895030-1A-EN | PD | Control and supervision of ND-500(0) processes for SIN III/VSX L; lists microprogram versions per ND-5xxx model. |
| **[ND-500/5000 System Package for SINTRAN III/VSX version M](./ND-895030-2-EN.md)** | ND-895030-2-EN | PI | Version M package containing ND-500/5000 Monitor, Swapper and Place Library; new hardware support, faster swapper. |
| **[CONVERT DOMAIN](./ND-895218-S1-EN.md)** | ND-895218-S1-EN | Delivery List | Delivery list for CONVERT DOMAIN utility, linked to ND Linker User Guide manual. |
| **[CAT-PROFILE for ND-500/5000](./ND-895462-S1-EN.md)** | ND-895462-S1-EN | Delivery List | Internal product structure sheet for CAT-PROFILE, listing reference manual and two diskettes. |
| **[X Window System for ND-500/5000](./ND-895566-1-EN.md)** | ND-895566-1-EN | PI | Port of MIT X11.R3 clients/utilities (xterm, xclock, etc.) for ND-500/5000 under SINTRAN III; no display server. |

---

### ND-5000 Diagnostics

| Product | Document # | Type | Description |
|---|---|---|---|
| **[ND-5000 Test Microprograms](./ND-211124-2-EN.md)** | ND-211124-2-EN | PD | SEMICS-based microcoded diagnostic test programs for the ND-5000 series CPU. |
| **[Basic System Package for ND-5000 Systems](./ND-895560-1-EN.md)** | ND-895560-1-EN | PI | Prepackaged upgrade kit for basic software on ND EServer/ND-5000 models with menu-driven installation. |
| **[Basic Software Package for ND-5000 ES Systems](./ND-895560-2-EN.md)** | ND-895560-2-EN | PI | Version B basic software/upgrade kit for ND-5000 ES models with prepacked software and platform kits. |

---

### Development Tools

| Product | Document # | Type | Description |
|---|---|---|---|
| **[AUTOMAKE for ND-100](./ND-210886-2-EN.md)** | ND-210886-2-EN | PD | New tool to control development and generation of software systems, v.B for SIN III VSX >=H. |
| **[AUTOMAKE for ND-500](./ND-210887-2-EN.md)** | ND-210887-2-EN | PD | Installation of AUTOMAKE tool controlling development/generation of software systems on ND-500. |
| **[ND LINKER](./ND-895035-S2-EN.md)** | ND-895035-S2-EN | Delivery List | Delivery list for ND LINKER B01, user guide and reference manual plus 6-diskette SS/SD set. |

---

### Patches and Error-Correction Kits

| Product | Document # | Type | Description |
|---|---|---|---|
| **[SINTRAN III/VSX Patch File (L-version, level 003100)](./ND-895230-1A-EN.md)** | ND-895230-1A-EN | Diskette Dir | Diskette directory listing of files (NEW-SYSTEM, PATCH-FILE etc.) for SINTRAN L patch level 003100. |
| **[SINTRAN III/VSX Patch File (L-version, level 007200)](./ND-895230-1G-EN.md)** | ND-895230-1G-EN | PI | Patch file 007200 for SINTRAN L/VSX with changed reports list and ERS/Watchdog descriptor updates. |
| **[SINTRAN III/VSX Patch File (M-version, level 6500)](./ND-895230-2H-EN.md)** | ND-895230-2H-EN | PI | Patch file 6500 for SINTRAN III/VSX Version M with software system reports since patch 5000. |
| **[SINTRAN III/VSX Patch File (L04, level 004300)](./ND-895230-S1C-EN.md)** | ND-895230-S1C-EN | Delivery List | Internal product structure sheet for SINTRAN L04 patch file 004300 with SW module and diskette. |
| **[Upgrade for Basic SYSTEM Software for Small Systems](./ND-895524-1-EN.md)** | ND-895524-1-EN | PI | Correction package (patch) for Basic SYSTEM Software for Small Systems. |
| **[SIBAS Manager for ND-500/5000 (Patch File)](./ND-895617-1-EN.md)** | ND-895617-1-EN | PI | Patch file with error corrections for SIBAS Manager version A05. |
| **[Patch Kit for ND tpServer](./ND-896058-2-EN.md)** | ND-896058-2-EN | Delivery List | Patch kit listing corrected SINTRAN III/VSX M, monitor call package, swapper, SIBAS/R and other components. |
| **[ND tpServer Error Correction Diskette](./ND-896058-3-EN.md)** | ND-896058-3-EN | Delivery List | Installation description plus error-correction diskette with Swapper M03 and SINTRAN III/VSX-N patch 044B. |
| **[ND tpServer Upgrade](./ND-896058-4-EN.md)** | ND-896058-4-EN | Delivery List | Patch kit upgrading tpServer platform C01 to C02, listing updated SINTRAN, swapper, SIBAS/R, and microprograms. |

---

### BASIC

| Product | Document # | Type | Description |
|---|---|---|---|
| **[BASIC for ND-100/NORD-10](./ND-10034-8-EN.md)** | ND-10034-8-EN | PD | BASIC-H00 compiler v.H error-correction release for ND-10/ND-100 under SINTRAN III >=H. |
| **[BASIC for ND-500](./ND-210755-1-EN.md)** | ND-210755-1-EN | PD | BASIC-500-A compiler and runtime, new product for ND-500 under SIN III VSX. |
| **[CBASIC Utilities and Runtime for ND-100/500/5000](./ND-895271-S1-EN.md)** | ND-895271-S1-EN | Delivery List | Product structure sheet for CBASIC utilities/runtime with German CBASIC manuals. |
| **[CBASIC Compiler for ND-500/5000](./ND-895276-S1-EN.md)** | ND-895276-S1-EN | Delivery List | Product structure sheet for CBASIC Compiler for ND-500/5000 with German CBASIC manuals. |
| **[CBASIC Compiler for ND-100](./ND-895277-S1-EN.md)** | ND-895277-S1-EN | Delivery List | Product structure sheet for CBASIC Compiler for ND-100 with German CBASIC manuals. |

---

### COBOL

| Product | Document # | Type | Description |
|---|---|---|---|
| **[COBOL-85 Runtime for ND-500/5000](./ND-895229-S1-EN.md)** | ND-895229-S1-EN | Delivery List | Delivery list for COBOL-85 Runtime K01, referencing ND COBOL-85 Reference Manual. |

---

### PLANC

| Product | Document # | Type | Description |
|---|---|---|---|
| **[PLANC for ND-110 (compiling on ND-500/5000)](./ND-211037-9-EN.md)** | ND-211037-9-EN | PD | PLANC compiler for ND-110, cross-compiled/run on ND-500/ND-5000, SIN III >=I. |
| **[PLANC for MC68000 (compiling on ND-500/5000)](./ND-895259-S1-EN.md)** | ND-895259-S1-EN | Delivery List | Product structure sheet for PLANC MC68000 cross-compiler with PLANC User Guide. |
| **[PLANC for Intel-386](./ND-895315-S1-EN.md)** | ND-895315-S1-EN | Delivery List | Internal product structure sheet for PLANC compiler on Intel-386, listing manual and XENIX-format diskette. |

---

### Pascal

| Product | Document # | Type | Description |
|---|---|---|---|
| **[ND Pascal for ND-110](./ND-895246-S01-EN.md)** | ND-895246-S01-EN | Delivery List | Product structure sheet for Pascal for ND-110 with Reference Manual and 16 diskettes. |
| **[ND Pascal for ND-500/5000](./ND-895247-S01-EN.md)** | ND-895247-S01-EN | Delivery List | Product structure sheet for Pascal for ND-500/5000 with Reference Manual and diskettes. |

---

### SIBAS/R (Relational Database)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[DIALOGUE SIBAS/R Online Tutorial for ND-500/5000](./ND-211418-1-EN.md)** | ND-211418-1-EN | PD | New product: introductory tutorials covering DIALOGUE, SIBAS/R and SIBAS/R DRL, requires SIN III >= J. |
| **[SIBAS/R](./ND-895202-S2-EN.md)** | ND-895202-S2-EN | Delivery List | Internal product structure sheet for SIBAS/R B03, SW/DOC modules and PI-sheet reference. |
| **[SIBAS/R Runtime](./ND-895203-S2-EN.md)** | ND-895203-S2-EN | Delivery List | Internal product structure sheet for SIBAS/R Runtime B03, SW/DOC modules and PI-sheet reference. |
| **[SIBAS/R Process](./ND-895204-S2A-EN.md)** | ND-895204-S2A-EN | Delivery List | Internal product structure sheet for SIBAS/R Process B03 with three delivery diskettes. |
| **[SIBAS/R Libraries for ND-100/500/5000](./ND-895206-S2-EN.md)** | ND-895206-S2-EN | Delivery List | Internal product structure sheet for SIBAS/R DML libraries B03 with manuals and diskettes. |
| **[SIBAS/R Backend](./ND-895207-2-EN.md)** | ND-895207-2-EN | PI | Backend module for SIBAS/R database system over COSMOS/TCP-IP, adds Ethernet TCP/IP support. |
| **[SIBAS/R Backend](./ND-895207-3-EN.md)** | ND-895207-3-EN | PI | Later revision of SIBAS/R Backend product info, same TCP/IP over Ethernet capability, ND-5000 CPU. |
| **[SIBAS/R Softkey](./ND-895208-S2-EN.md)** | ND-895208-S2-EN | Delivery List | Internal product structure sheet for SIBAS/R Softkey B03 module and diskette. |
| **[SIBAS/R Utilities](./ND-895243-S1-EN.md)** | ND-895243-S1-EN | Delivery List | Product structure sheet for SIBAS/R Utilities with DIALOGUE manuals and diskettes. |
| **[SIBAS Manager for ND-500/5000](./ND-895275-1A-EN.md)** | ND-895275-1A-EN | PI | Describes SIBAS Manager's database administration and monitoring features. |
| **[SIBAS Manager for ND-500/5000](./ND-895275-S1-EN.md)** | ND-895275-S1-EN | Delivery List | Product structure sheet for SIBAS Manager with DIALOGUE Operations manual and diskettes. |
| **[SIBAS/R Backend for NOTIS-DS](./ND-895479-1-EN.md)** | ND-895479-1-EN | PI | Describes SIBAS/R backend module for NOTIS-DS adding TCP/IP-over-Ethernet support alongside COSMOS. |
| **[SIBAS/R Client](./ND-895602-1-EN.md)** | ND-895602-1-EN | PI | Access libraries, DBMS control program, and utilities for ND-100/500/5000 SIBAS/R database client. |
| **[SIBAS/R Softkey for Development Access](./ND-895603-1-EN.md)** | ND-895603-1-EN | PI | Software license key enabling SIBAS/R application development under the new B-version key system. |
| **[SIBAS/R Server](./ND-895604-1-EN.md)** | ND-895604-1-EN | PI | Server part and utility programs of SIBAS/R database, excluding client-side SIBR-SERVICE/SIBR-INTER. |
| **[SIBAS/R SQL Interactive for ND-500/5000](./ND-895615-1-EN.md)** | ND-895615-1-EN | PI | Interactive SQL query editor for SIBAS/R with built-in SQL server, replacing the older SQLI-A version. |
| **[SIBAS/R SQL Library for ND-500/5000](./ND-895616-1-EN.md)** | ND-895616-1-EN | PI | SQL-oriented function call library (COBOL/FORTRAN/PLANC/C) for accessing SIBAS/R databases via embedded SQL. |
| **[SIBAS/R](./ND-895623-1-EN.md)** | ND-895623-1-EN | PI | Full SIBAS/R DBMS bundle listing its 6 sub-products (client, server, softkeys, manager, MMOE) and install order. |
| **[SIBAS/R Runtime](./ND-895624-1-EN.md)** | ND-895624-1-EN | PI | Runtime-only bundle of SIBAS/R DBMS listing 5 sub-products and required install order. |
| **[SIBAS/R Client Package](./ND-895625-1-EN.md)** | ND-895625-1-EN | PI | Client-only bundle of SIBAS/R (access libraries, control program, utilities plus manager sub-product). |
| **[SIBAS/R Softkey](./ND-895627-1-EN.md)** | ND-895627-1-EN | PI | Software license key enabling Runtime use of SIBAS/R under the new B-version key system. |
| **[SIBAS/R Backend](./ND-895628-1-EN.md)** | ND-895628-1-EN | PI | License key and setup instructions to activate SIBAS/R Backend module over COSMOS and/or TCP/IP. |

---

### SIBAS / UNIQUE (4GL and ISAM/SIBAS Tools)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[SQL for ND-500](./ND-211049-1-EN.md)** | ND-211049-1-EN | PD | Interactive SQL DML-only query tool for SIBAS databases on ND-500, requires SINTRAN III >=K. |
| **[UNIQUE Start SIBAS for ND-110](./ND-895083-S1-EN.md)** | ND-895083-S1-EN | Delivery List | Delivery list for UNIQUE Start SIBAS for ND-110 C10, bundling Software Keys and UNIQUE Text System. |
| **[UNIQUE Start SIBAS for ND-500/5000](./ND-895084-S1-EN.md)** | ND-895084-S1-EN | Delivery List | Delivery list for UNIQUE Start SIBAS for ND-500/5000 C10, bundling Software Keys and UNIQUE Text System. |
| **[UNIQUE Text System](./ND-895177-1B-EN.md)** | ND-895177-1B-EN | PI | Language-dependent files (EN/GE/NO/SW) for UNIQUE CONCEPT products, compatible with version C10+. |
| **[UNIQUE Text System (German)](./ND-895177-S1A-EN.md)** | ND-895177-S1A-EN | Delivery List | Internal product structure sheet for UNIQUE Text System C10 German diskette delivery. |
| **[UNIQUE Documentation SIBAS for ND-500/5000](./ND-895178-1B-EN.md)** | ND-895178-1B-EN | PI | Documentation system for UNIQUE-II ON-LINE/XTRA reports, revisions C13/C14 error corrections. |
| **[UNIQUE Documentation SIBAS for ND-500/5000](./ND-895178-S1-EN.md)** | ND-895178-S1-EN | Delivery List | Internal delivery list bundling Software Keys, Text System, manuals and diskettes for release C11. |
| **[UNIQUE Documentation SIBAS for ND-110](./ND-895179-1B-EN.md)** | ND-895179-1B-EN | PI | Documentation system for UNIQUE-II ON-LINE/XTRA reports on ND-110, revisions C13/C14. |
| **[UNIQUE XTRA SIBAS for ND-110](./ND-895180-1B-EN.md)** | ND-895180-1B-EN | PI | Report generation and query tool on SIBAS databases for ND-110, revisions C13/C14. |
| **[UNIQUE XTRA SIBAS for ND-500/5000](./ND-895181-1B-EN.md)** | ND-895181-1B-EN | PI | Report generation and query tool on SIBAS databases for ND-500/5000, revisions C13/C14. |
| **[UNIQUE Server for ND-110](./ND-895182-1B-EN.md)** | ND-895182-1B-EN | PI | Background/scheduled XTRA report execution module (RT program + interactive service) for ND-110. |
| **[UNIQUE Server for ND-500/5000](./ND-895183-1B-EN.md)** | ND-895183-1B-EN | PI | Background/scheduled XTRA report execution module (RT program + interactive service) for ND-500/5000. |
| **[UNIQUE UNIQUICK SIBAS for ND-110](./ND-895184-1B-EN.md)** | ND-895184-1B-EN | PI | Interactive application generator for UNIQUE-II SIBAS on ND-110, revisions C13/C14. |
| **[UNIQUE UNIQUICK SIBAS for ND-500/5000](./ND-895185-1B-EN.md)** | ND-895185-1B-EN | PI | Interactive application generator for UNIQUE-II SIBAS on ND-500/5000, revisions C13/C14. |
| **[UNIQUE-II SIBAS for ND-110](./ND-895194-1B-EN.md)** | ND-895194-1B-EN | PI | 4th generation language for storing/modifying/retrieving SIBAS database data on ND-110, C13/C14. |
| **[UNIQUE-II SIBAS for ND-500/5000](./ND-895195-1B-EN.md)** | ND-895195-1B-EN | PI | 4th generation language for storing/modifying/retrieving SIBAS database data on ND-500/5000, C13/C14. |
| **[SQL Library for OWS](./ND-895316-S1-EN.md)** | ND-895316-S1-EN | Delivery List | Internal product structure sheet for SQL Library for OWS, listing manual and DOS-format diskette. |
| **[UNIQUE-II SIBAS Runtime for ND-110](./ND-895467-1B-EN.md)** | ND-895467-1B-EN | PI | Describes revisions C13/C14 of the UNIQUE-II SIBAS runtime (no compiling), a 4GL database access tool. |
| **[UNIQUE-II SIBAS Runtime for ND-500/5000](./ND-895468-1B-EN.md)** | ND-895468-1B-EN | PI | Describes revisions C13/C14 of the UNIQUE-II SIBAS runtime for ND-500/5000, a 4GL database access tool. |
| **[UNIQUE XTRA SIBAS Runtime for ND-110](./ND-895469-1B-EN.md)** | ND-895469-1B-EN | PI | Describes revisions C13/C14 of UNIQUE XTRA, a SIBAS report-generation/query runtime (no new report creation). |
| **[UNIQUE XTRA SIBAS Runtime for ND-500/5000](./ND-895470-1B-EN.md)** | ND-895470-1B-EN | PI | Describes revisions C13/C14 of UNIQUE XTRA report-generation/query runtime for ND-500/5000. |

---

### UNIQUE-II ISAM

| Product | Document # | Type | Description |
|---|---|---|---|
| **[UNIQUE-II ISAM for ND-500](./ND-210895-2-EN.md)** | ND-210895-2-EN | PD | 4th-generation ISAM database loading/updating/retrieval program for ND-500, requires SIN III VSX >=I. |
| **[UNIQUE UNIQUICK ISAM for ND-100](./ND-210896-1-EN.md)** | ND-210896-1-EN | PD | Application generation tool for UNIQUE-II ISAM on ND-100. |
| **[UNIQUE UNIQUICK ISAM for ND-500](./ND-210897-1-EN.md)** | ND-210897-1-EN | PD | Application generation tool for UNIQUE-II ISAM on ND-500, notes known key-collision bug. |
| **[UNIQUE Text System](./ND-211005-3-EN.md)** | ND-211005-3-EN | PD | Language-dependent (dictionary/help) component of the UNIQUE/DIALOGUE product line. |

---

### BIM (4th-Generation ADP Tool)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[BIM for ND-500/5000](./ND-210938-3-EN.md)** | ND-210938-3-EN | PD | 4th-generation ADP tool with batch facility using the SIBAS database on ND-500/ND-5000. |
| **[BIM Runtime for ND-500/5000](./ND-211033-3-EN.md)** | ND-211033-3-EN | PD | Runtime component for the BIM 4th-generation ADP/SIBAS tool on ND-500/ND-5000. |

---

### DIALOGUE / ABM (Application Building)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[ABM Runtime for ND-100](./ND-211081-3-EN.md)** | ND-211081-3-EN | PD | Error-correction release of the ABM runtime system for ND-100. |
| **[ABM Runtime for ND-500/5000](./ND-211082-S4-EN.md)** | ND-211082-S4-EN | Delivery List | Internal delivery list of manual/diskettes for ABM Runtime for ND-500/5000, version D01. |
| **[DIALOGUE Utilities](./ND-895209-S01-EN.md)** | ND-895209-S01-EN | Delivery List | Internal delivery list for DIALOGUE Utilities, program description reference and diskettes. |
| **[ABM/PG Runtime for ND-500/5000](./ND-895471-S1-EN.md)** | ND-895471-S1-EN | Delivery List | Internal product structure sheet for ABM/PG Runtime, listing DIALOGUE-ABM manuals and 5 diskettes. |
| **[ABM/PG for ND-500/5000](./ND-895472-S1-EN.md)** | ND-895472-S1-EN | Delivery List | Internal product structure sheet for ABM/PG, listing constituent SW-modules and related PI-sheets. |
| **[DIALOGUE-3 for ND-500/5000](./ND-895474-S1-EN.md)** | ND-895474-S1-EN | Delivery List | Internal product structure sheet for DIALOGUE-3, listing constituent SW-modules and related PI-sheets. |
| **[APM/PG Kit for Porting to Uniline x0](./ND-895475-S1-EN.md)** | ND-895475-S1-EN | Delivery List | Internal product structure sheet for APM/PG porting kit, listing manual and 3 diskettes. |
| **[ABM Tool for ND-500/5000](./ND-895476-S1-EN.md)** | ND-895476-S1-EN | Delivery List | Internal product structure sheet for ABM Tool, listing DIALOGUE-ABM manuals and 9 diskettes. |

---

### NOTIS Office Automation Suite

| Product | Document # | Type | Description |
|---|---|---|---|
| **[NOTIS-BG for ND-100 (Business Graphics)](./ND-10724-2-EN.md)** | ND-10724-2-EN | PD | 48-bit-float NOTIS-BG line/bar/pie chart program for ND-100 under SIN III VS >=I. |
| **[NOTIS-CALC for ND-100](./ND-210530-04-EN.md)** | ND-210530-04-EN | PD | NOTIS spreadsheet program error-correction/change release, version 210530D for SIN III >I. |
| **[NOTIS-ID for ND-500/5000](./ND-210792-2-EN.md)** | ND-210792-2-EN | PI | Electronic mail system for COSMOS network message/document distribution, first version integrating with PC-NOTIS ID. |
| **[NOTIS-ID for ND-500/5000](./ND-210792-S2-EN.md)** | ND-210792-S2-EN | Delivery List | Internal delivery list of manuals/diskettes for NOTIS-ID B07 in English and Norwegian language versions. |
| **[NOTIS-BG for ND-500/5000](./ND-210793-3-EN.md)** | ND-210793-3-EN | PD | Bar/column/line/pie/text chart production tool for ND-500/5000 under SIN III VS >=J, requires XMSG. |
| **[NOTIS-DS for ND-500/5000](./ND-210794-S3-EN.md)** | ND-210794-S3-EN | Delivery List | Internal delivery list for NOTIS-DS C02 diskettes/manuals in English and Norwegian. |
| **[NOTIS-DS for ND-500/5000 (German Version)](./ND-210794-S4-EN.md)** | ND-210794-S4-EN | Delivery List | Product structure sheet for German NOTIS-DS D04 diskettes and manuals, replacing prior German versions. |
| **[NOTIS-WP Examples](./ND-210960-13-EN.md)** | ND-210960-13-EN | PD | Example/demo files supporting the NOTIS-WP User Guide for ND-100/ND-500. |
| **[NOTIS-DE for ND-100](./ND-211011-1-EN.md)** | ND-211011-1-EN | PD | Data entry system for NOTIS on ND-100, requires SINTRAN III >=J. |
| **[NOTIS-DE for ND-500](./ND-211015-1-EN.md)** | ND-211015-1-EN | PD | Data entry system for NOTIS on ND-500, requires SINTRAN III >=J. |
| **[NOTIS-DRAW for ND-100](./ND-211019-2-EN.md)** | ND-211019-2-EN | PD | General-purpose graphic editor for ND-100 with 32-bit floating format, needs graphics terminal. |
| **[NOTIS-DISOSS BRIDGE for ND-110](./ND-211048-S1-EN.md)** | ND-211048-S1-EN | Delivery List | Internal delivery list of manuals/diskettes for NOTIS-DISOSS BRIDGE, English/Norwegian A04. |
| **[NOTIS-DISOSS BRIDGE for ND-500/5000](./ND-211127-S1-EN.md)** | ND-211127-S1-EN | Delivery List | Internal delivery list of manuals/diskettes for NOTIS-DISOSS BRIDGE on ND-500/5000, English/Norwegian A04. |
| **[NOTIS-WP for ND-WS](./ND-895005-S1-EN.md)** | ND-895005-S1-EN | Delivery List | Delivery list for NOTIS-WP for ND workstations version N06, English and Norwegian manual/diskette sets. |
| **[NOTIS-DM for ND-500/5000](./ND-895037-S01-EN.md)** | ND-895037-S01-EN | Delivery List | Delivery list for NOTIS-DM A02, English and Norwegian manuals (App Manager's/User Guide, SIBAS-CONVERT). |
| **[NOTIS-DM with ABM Definition Tool](./ND-895042-S01-EN.md)** | ND-895042-S01-EN | Delivery List | Delivery list combining NOTIS-DM A02 and ABM Tool D01 for ND-500/5000, English A00. |
| **[NOTIS-DM Upgrade for NOTIS-WP](./ND-895043-S01-EN.md)** | ND-895043-S01-EN | Delivery List | Delivery list for NOTIS-DM upgrade path from NOTIS-WP, version A00, English/Norwegian. |
| **[NOTIS-DS for ND-500/5000](./ND-895045-1A-EN.md)** | ND-895045-1A-EN | PD | NOTIS-DS document storage system, version D, error correction and change/addition release, needs SIN III >= J. |
| **[NOTIS-DS for ND-500/5000](./ND-895045-2A-EN.md)** | ND-895045-2A-EN | PI | NOTIS-DS version E product info: SIBAS/R-based, adds automated restart, security and admin improvements. |
| **[NOTIS-TELETEX for Denmark (X.21)](./ND-895047-S1-EN.md)** | ND-895047-S1-EN | Delivery List | Internal delivery list for NOTIS-TELETEX Denmark C, Danish/multi-format diskettes, Norwegian manuals. |
| **[NOTIS-TELETEX for Denmark Remote User Module](./ND-895048-S1-EN.md)** | ND-895048-S1-EN | Delivery List | Internal delivery list for NOTIS-TELETEX Denmark remote-user module C02, Danish version. |
| **[NOTIS-TELETEX for Norway Remote User Module](./ND-895052-S1-EN.md)** | ND-895052-S1-EN | Delivery List | Internal delivery list for NOTIS-TELETEX Norway remote-user module C02, Norwegian version. |
| **[NOTIS-RP for ND-110](./ND-895066-S1-EN.md)** | ND-895066-S1-EN | Delivery List | Delivery list for RP for ND-110 D10, English and Norwegian, with RP-START and NOTIS-RG User Guide. |
| **[NOTIS-RP for ND-500/5000](./ND-895067-2-EN.md)** | ND-895067-2-EN | PI | NOTIS-RP version E product info: report-production program for NOTIS-RG, requires SINTRAN K or L. |
| **[NOTIS-RP for ND-500/5000](./ND-895067-S1-EN.md)** | ND-895067-S1-EN | Delivery List | Delivery list for RP for ND-500/5000 D10, English and Norwegian, with RP-START and NOTIS-RG User Guide. |
| **[NOTIS-MAIL](./ND-895080-1-EN.md)** | ND-895080-1-EN | PI | NOTIS-MAIL version A product info: X.400 CCITT electronic mail/document interchange system, SPAG-tested. |
| **[NOTIS-PRO for ND-500/5000](./ND-895171-S1-EN.md)** | ND-895171-S1-EN | Delivery List | Product structure sheet for NOTIS-PRO B03, with User Guide, Supervisor Guide, and Quick Reference card. |
| **[NOTIS-DIARY for ND-500/5000](./ND-895186-1-EN.md)** | ND-895186-1-EN | PI | Personal diary and meeting-scheduling system replacing NOTIS-PM. |
| **[NOTIS-WP for ND-500/5000](./ND-895191-04-NO.md)** | ND-895191-04-NO | PI | Norwegian-language product info for text processing program NOTIS-WP; adds Nynorsk/Finnish spell-check. |
| **[NOTIS-DRAW for ND-110](./ND-895224-S1-EN.md)** | ND-895224-S1-EN | Delivery List | Delivery list for NOTIS-DRAW B05 drawing program with user guide and quick reference card. |
| **[NOTIS-BG for ND-110 (32-bit)](./ND-895232-S1-EN.md)** | ND-895232-S1-EN | Delivery List | Delivery list for NOTIS-BG C05 business graphics, English and Norwegian manuals and diskettes. |
| **[NOTIS-BG for ND-110 (48-bit)](./ND-895233-S1-EN.md)** | ND-895233-S1-EN | Delivery List | Delivery list for NOTIS-BG with manuals and diskettes in English and Norwegian. |
| **[NOTIS-DH Document Handler](./ND-895266-S1-EN.md)** | ND-895266-S1-EN | Delivery List | Product structure sheet for NOTIS-DH Document Handler with Document Handler User Guide. |
| **[NOTIS-SPELL for ND-500/5000](./ND-895489-2-EN.md)** | ND-895489-2-EN | PI | New version 8 spelling checker for NOTIS-WP using Proximity Linguistic Technology, with new file formats and Nynorsk/Finnish dictionaries. |
| **[ND SPELL Dictionaries for ND-500/5000](./ND-895490-2-NO.md)** | ND-895490-2-NO | PI | Norwegian-language document describing dictionary files (14 languages) for NTX-SPELL/NOTIS-SPELL, new file format. |
| **[NOTIS-MAIL API for ND-500/5000](./ND-895504-1-EN.md)** | ND-895504-1-EN | PI | Application programmer's interface for sending/receiving mail against NOTIS-MAIL on SINTRAN, ND-500/5000 only. |
| **[XNOTIS TDV2200 Terminal Emulator for X-Windows](./ND-895559-1-EN.md)** | ND-895559-1-EN | PI | X-Window terminal emulator for the Tandberg 2200/9s, letting SINTRAN NOTIS apps run on X terminals. |
| **[NOTIS-WP for ND-WS](./ND-99122-1-EN.md)** | ND-99122-1-EN | Install | Install steps for NOTIS-WP under DTM version C on Norwegian ND workstations (EGA/VGA/Wyse 700). |
| **[NOTIS-WP for ND-100 (rev M05)](./10079M05_NOTIS-WP_for_ND-100.md)** | 10079M05-XX-1D | Diskette listing + PD | NORD Software Library diskette sheet for NOTIS-WP M05 on ND-100, with revision notes and INIT-file upgrade steps. Wiki-sourced (NDwiki), not from the standard oracle series. |
| **[NOTIS-WP for ND-100 (rev M07)](./10079M07_NOTIS-WP_for_ND-100.md)** | 10079M07-XX-1D | Diskette listing + PD | NORD Software Library diskette sheet for NOTIS-WP M07 on ND-100, later revision than M05. Wiki-sourced (NDwiki), not from the standard oracle series. |

---

### PC-NOTIS (PC Client Suite)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[PC-NOTIS Platform](./ND-895533-1-EN.md)** | ND-895533-1-EN | PI | Basic integration platform allowing NOTIS applications to be launched between PC and ND-500/5000. |
| **[PC-NOTIS Server for ND-500/5000](./ND-895534-1-EN.md)** | ND-895534-1-EN | PI | Server floppy with IDSAS (ID/DS request handler) and HOST-AS to start ND-HOST apps from a PC. |
| **[PC-NOTIS WP](./ND-895535-1-EN.md)** | ND-895535-1-EN | PI | General-purpose PC text processor upgraded to match NOTIS-WP N09 functionality, running under PC-NOTIS Platform. |
| **[PC-NOTIS CALC](./ND-895536-1-EN.md)** | ND-895536-1-EN | PI | First PC version of NOTIS-CALC spreadsheet, keeping UI close to the ND-500/5000 version. |
| **[PC-NOTIS ID](./ND-895537-1-EN.md)** | ND-895537-1-EN | PI | Norwegian PC version of NOTIS-ID electronic mail Main User Program for COSMOS networks. |
| **[PC-NOTIS DS](./ND-895538-1-EN.md)** | ND-895538-1-EN | PI | Norwegian PC version of NOTIS-DS Document Manager, part of the document storage system. |

---

### NORTEXT (Typesetting / Publishing)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[NORTEXT-100 Editor for ND-110](./ND-210800-12-EN.md)** | ND-210800-12-EN | PD | NORTEXT-100 article editor v.L providing command interface to Basic RealTime System, requires XCOM/User Environment. |
| **[NORTEXT-100 Auto Justification](./ND-210809-12-EN.md)** | ND-210809-12-EN | PD | Automatic text justification/hyphenation module v.L for NORTEXT-100 Basic RT, no operator interaction. |
| **[NORTEXT-100 Typographic Tables Maintenance](./ND-210814-12-EN.md)** | ND-210814-12-EN | PD | Maintenance program v.L for NORTEXT-100 typographical tables on ND-100/ND-500 SIN III VSX >=J. |
| **[NORTEXT-100 MCS8400 Output Module](./ND-210820-12-EN.md)** | ND-210820-12-EN | PD | Typesetter control module v.L for the MCS8400 device under NORTEXT-100 SIN III VSX >=J. |
| **[NORTEXT-100 CG8600 Output Module](./ND-210821-12-EN.md)** | ND-210821-12-EN | PD | Typesetter control module v.L for the CG8600 device under NORTEXT-100 SIN III VSX >=J. |
| **[NORTEXT-100 LINOTRON Output Module (German)](./ND-210822-12-EN.md)** | ND-210822-12-EN | PD | German-version typesetter control module v.L for the LINOTRON device under NORTEXT-100. |
| **[NORTEXT APS5 Output Module](./ND-210823-13-EN.md)** | ND-210823-13-EN | PD | Typesetter control module v.M for APS 5/APS micro 5/APS-55 rip series, SIN III VSX >=K, WorkMode >=406. |
| **[NORTEXT-100 DIGISET T20 Output Module](./ND-210824-12-EN.md)** | ND-210824-12-EN | PD | Typesetter control module v.L for the DIGISET T20 device under NORTEXT-100 SIN III VSX >=J. |
| **[NORTEXT German Hyphenation Tables](./ND-210831-S12-EN.md)** | ND-210831-S12-EN | Delivery List | Internal delivery list for NORTEXT German hyphenation tables product v.L04. |
| **[NORTEXT-100 VIDEOSETTER V Output Module](./ND-210839-12-EN.md)** | ND-210839-12-EN | PD | New typesetter control module v.L for the VIDEOSETTER V device under NORTEXT-100. |
| **[NORTEXT Mathematic Composition Package](./ND-211298-1-EN.md)** | ND-211298-1-EN | PD | New product providing formats for composing mathematic formulas in NORTEXT on ND-500(0), SIN III VSX K. |
| **[Nortext Software Distribution (NSD)](./ND-230115-3-EN.md)** | ND-230115-3-EN | PI | NSD 230115C, MS-DOS unattended update utility for PC files over Ethernet via FTP or NAS, new version C. |
| **[NORTEXT PC-FT for PDWS (ND-110)](./ND-895250-S01-EN.md)** | ND-895250-S01-EN | Delivery List | Product structure sheet for NORTEXT PC-FT for PDWS on ND-110 with Page Designer guide. |
| **[NORTEXT PC-FT for PDWS (ND-500)](./ND-895251-S01-EN.md)** | ND-895251-S01-EN | Delivery List | Product structure sheet for NORTEXT PC-FT for PDWS on ND-500 with Page Designer guide. |
| **[NORTEXT Support Programs for PDWS](./ND-895252-S01-EN.md)** | ND-895252-S01-EN | Delivery List | Product structure sheet for NORTEXT Support Programs for PDWS with Page Designer guide. |
| **[NORTEXT Page Designer](./ND-895253-S01-EN.md)** | ND-895253-S01-EN | Delivery List | Product structure sheet for NORTEXT Page Designer with user guide and license agreement. |
| **[NORTEXT Ad Designer](./ND-895254-S01-EN.md)** | ND-895254-S01-EN | Delivery List | Product structure sheet for NORTEXT Ad Designer with user guide and quick reference cards. |
| **[NORTEXT Access Server for ND-500/5000](./ND-895273-S01-EN.md)** | ND-895273-S01-EN | Delivery List | Product structure sheet for NORTEXT Access Server with Programmers Guide. |
| **[NORTEXT Spanish Hyphenation](./ND-895287-S01-EN.md)** | ND-895287-S01-EN | Delivery List | Product structure sheet for NORTEXT Spanish Hyphenation module with Hyphenation Reference Manual. |
| **[NORTEXT Portuguese Hyphenation](./ND-895288-S01-EN.md)** | ND-895288-S01-EN | Delivery List | Internal product structure sheet listing SW/DOC modules, manual, PD-sheet and diskette. |
| **[NORTEXT Italian Hyphenation](./ND-895289-S01-EN.md)** | ND-895289-S01-EN | Delivery List | Internal product structure sheet listing SW/DOC modules, manual, PD-sheet and diskette. |
| **[NORTEXT Turkish Hyphenation](./ND-895290-S01-EN.md)** | ND-895290-S01-EN | Delivery List | Internal product structure sheet listing SW/DOC modules, manual, PD-sheet and diskette. |
| **[NORTEXT Editor for Workstation (NEWS)](./ND-NEWS-N02-EN.md)** | ND-NEWS-N02-EN | PI | PC editing environment family (NEWS, NEWS Jr., Dial variants) integrated with a remote NORTEXT text system. |

---

### COSMOS Networking

| Product | Document # | Type | Description |
|---|---|---|---|
| **[X-MESSAGE version L](./ND-210373L-EN.md)** | 210373L | PD | The message system COSMOS is built on. Unusually detailed for this collection: XMFIDO watchdog letter layouts, register specs for the new/changed XMSG functions (XFDUM, XFGST, **XFGSM**, XFCPV) and XROUT services (XSGAT, XSLKI, XSNET, XSNSI, XSLIN, XSDAT, XSLSY, XSGSU, XSGSG), the new error codes, then the install/patch procedure. Dated 1988-02-02, 37 pages. |
| **[COSMOS Ethernet Option](./ND-210580-02-EN.md)** | ND-210580-02-EN | PD | Enables Ethernet (ISO 8802/3 CSMA/CD) transmission under COSMOS for ND-100/ND-500 with X-MESSAGE. |
| **[COSMOS Network Monitor](./ND-211104-1-EN.md)** | ND-211104-1-EN | PD | Monitors connection/server status and long-term statistics in a COSMOS network on ND-100. |
| **[COSMOS X.25 Program Access](./ND-211197-1-EN.md)** | ND-211197-1-EN | PD | PLANC libraries to access COSMOS X.25 Option from programs on ND-100/110/120/500/5000. |
| **[COSMOS Basic Module](./ND-895036-2-EN.md)** | ND-895036-2-EN | PI | COSMOS Basic Module 210374G: CONNECT-TO, spooling, file access/transfer; requires SIN III/VSX L or later. |
| **[COSMOS X.25 Option for PIOC](./ND-895398-01A-EN.md)** | ND-895398-01A-EN | PI | Describes revision A06 of the COSMOS X.25 Option for PIOC, extending COSMOS networks over public data networks. |
| **[ND OSI Session Service](./ND-895549-2-EN.md)** | ND-895549-2-EN | PD | New ISO OSI Session Service (layer 5, ISO 8326/8327) for program-to-program comms in OSI/COSMOS networks. |
| **[COSMOS X.21 Option](./ND-xxxxx1-T1-NO.md)** | ND-xxxxx1-T1-NO | Memo | Norwegian internal memo (OPH, 1987) with installation tips for the COSMOS X.21 option over HDLC-link. |

---

### TCP/IP and Telnet/FTP

| Product | Document # | Type | Description |
|---|---|---|---|
| **[TCP/IP Basic Module/III](./ND-895061-1A-EN.md)** | ND-895061-1A-EN | PI | TCP/IP Basic Module version B05 product info: Telnet/FTP over Ethernet, SIBAS backend, NFS support. |
| **[TCP/IP Basic Module/III](./ND-895061-2-EN.md)** | ND-895061-2-EN | PI | TCP/IP Basic Module version D00 product info: performance/error-reporting improvements, NCS alive-check support. |
| **[COSMOS TCP/IP Gateway for Ethernet](./ND-895070-1A-EN.md)** | ND-895070-1A-EN | PI | COSMOS TCP/IP Gateway version C07 product info: Berkeley 4.3-compatible Telnet server, FTP get/pwd interop. |
| **[COSMOS TCP/IP Gateway for Ethernet](./ND-895070-2-EN.md)** | ND-895070-2-EN | PI | COSMOS TCP/IP Gateway version D02 product info: incoming checksum fix, NCS NetMap response support. |
| **[COSMOS Telnet/FTP Clients](./ND-895071-2-EN.md)** | ND-895071-2-EN | PI | COSMOS Telnet/FTP Clients version D01 product info: DNS resolver support, Berkeley 4.3 Telnet compatibility. |
| **[COSMOS FTP/Telnet Clients](./ND-895071-3-EN.md)** | ND-895071-3-EN | PI | COSMOS FTP/Telnet Clients version E02 product info: FTP client for 100 and 500(0), file-hole transfer, RSH client removed. |
| **[OpenLAN TCP/IP Access Module/III](./ND-895087-S1-EN.md)** | ND-895087-S1-EN | Delivery List | Delivery list bundling OWS Access Server, TCP/IP Basic Module/III, and COSMOS Telnet/FTP Client A00. |
| **[ND Connect Module](./ND-895499-1A-EN.md)** | ND-895499-1A-EN | PI | Floppy installer for CONNECT.EXE and TCP/IP software under \ND-OWS\COMMS as part of ND PC Starter Kit. |

---

### SNA / IBM Mainframe Gateways

| Product | Document # | Type | Description |
|---|---|---|---|
| **[SNA 3270 Emulator II](./ND-211278-S1-EN.md)** | ND-211278-S1-EN | Delivery List | Internal delivery list of manual/diskettes for SNA 3270 Emulator II, English A05. |
| **[SNA 3270 Program Access II](./ND-211279-S1-EN.md)** | ND-211279-S1-EN | Delivery List | Internal delivery list of manual/diskette for SNA 3270 Program Access II, English A00. |
| **[SNA RJE Support II](./ND-211280-S1-EN.md)** | ND-211280-S1-EN | Delivery List | Internal delivery list of manuals/diskettes for SNA RJE Support II, English A03. |
| **[SNA APPC - LU 6.2 Library II](./ND-211281-S1-EN.md)** | ND-211281-S1-EN | Delivery List | Internal delivery list of manual/diskettes for SNA APPC LU 6.2 Library II, English A01. |
| **[SNA Database Access II](./ND-211284-S1-EN.md)** | ND-211284-S1-EN | Delivery List | Internal delivery list of manual/diskette for SNA Database Access II, English A00. |
| **[SNA Database Server II](./ND-211285-S1-EN.md)** | ND-211285-S1-EN | Delivery List | Internal delivery list for SNA Database Server II version A00, magnetic tape distribution, dated 23.09.1988. |
| **[OWS SNA 3270 Emulator II](./ND-895269-S1-EN.md)** | ND-895269-S1-EN | Delivery List | Product structure sheet for OWS SNA 3270 Emulator II with user guide. |
| **[ND SNA NOTIS-MEMO Bridge](./ND-895455-2-EN.md)** | ND-895455-2-EN | PI | Approved post-beta release describing the bridge connecting IBM MEMO mail to ND NOTIS-ID over SNA 3270. |
| **[OpenLAN SNA 3270 Emulator for XENIX](./ND-895492-1-EN.md)** | ND-895492-1-EN | PI | 3270 terminal emulator for Uniline running XENIX, connecting to IBM mainframes via OpenLAN or SINTRAN SNA Gateway II. |
| **[OpenLAN SNA Gateway Software for XENIX](./ND-895493-1-EN.md)** | ND-895493-1-EN | PI | SNA gateway to IBM mainframes running on Uniline x0/XENIX with a PCB SNA SDLC card, successor to ND-100 SNA gateways I/II. |
| **[ND SNA Remote Terminal Server II](./ND-895502-1-EN.md)** | ND-895502-1-EN | PI | Server making an IBM 3270 terminal appear as an ND terminal type 6, for use with SNA-Gateway-II. |

---

### LAN / PC Connectivity

| Product | Document # | Type | Description |
|---|---|---|---|
| **[3Station Start Volume](./ND-895498-1A-EN.md)** | ND-895498-1A-EN | PI | Start-volume floppy enabling a diskless ND-110948 3Station/2E Netstation to access 3+Open LM and SINTRAN/Unix concurrently. |
| **[ND LAN Connect](./ND-895556-1-EN.md)** | ND-895556-1-EN | PI | PC driver letting ND applications reach SINTRAN resources via interrupt 14/6B network adapters. |

---

### OWS / OpenLAN (Office Workstation)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[OWS Access Server](./ND-211297-1-EN.md)** | ND-211297-1-EN | PD | Access to DS/UE/SSY/SIBAS services for up to 16 OWS over Ethernet; prerelease, requires SIN III VSX K. |
| **[Desk Top Manager for OWS](./ND-895002-S2-EN.md)** | ND-895002-S2-EN | Delivery List | Delivery list for Desk Top Manager for OWS C02, English and Norwegian manuals and diskettes. |
| **[OWS Terminal Line Server](./ND-895017-S1-EN.md)** | ND-895017-S1-EN | Other (Product Structure Sheet) | Internal product structure sheet for OWS Terminal Line Server A03, software module only, no manuals. |
| **[Graph Plus](./ND-895040-1-EN.md)** | ND-895040-1-EN | PI | Graph Plus 230044A, business chart/diagram program for OWS under MS Windows 2.03, various plotter/printer output. |
| **[Designer](./ND-895041-1-EN.md)** | ND-895041-1-EN | PI | Designer 230042A, drawing/illustration program for OWS under MS Windows 2.03. |
| **[CMS Access Server for ND-500/5000](./ND-895060-2-EN.md)** | ND-895060-2-EN | PI | CMS Access Server product info: OWS access to DS/UE/SSY/SIBAS over Ethernet, 48-124 connections. |
| **[OWS Access Server for ND-500/5000](./ND-895060-S1-EN.md)** | ND-895060-S1-EN | Delivery List | Delivery list for OWS Access Server A02, referencing OpenLAN Network Supervisor Guide. |
| **[OWS Software Distribution System](./ND-895221-S1-EN.md)** | ND-895221-S1-EN | Delivery List | Internal product structure sheet for OWS Software Distribution System A00, with user guide manual. |
| **[ND SMX for Windows](./ND-895249-S1-EN.md)** | ND-895249-S1-EN | Delivery List | Product structure sheet for System Menu eXpander for Windows with install/user guide. |

---

### Uniline / XENIX

| Product | Document # | Type | Description |
|---|---|---|---|
| **[OS Customization for Uniline x0 (SCO UNIX 386)](./ND-895460-3-EN.md)** | ND-895460-3-EN | PI | Menu-driven OS tailoring package (rev C) unifying customization for the Uniline x0 series running SCO UNIX 386. |
| **[OpenLAN Printing from XENIX](./ND-895506-1A-EN.md)** | ND-895506-1A-EN | PI | Enables XENIX machines with EXCELAN/FUSION network cards to print via a Terminal Interface Unit over the standard lp spooler. |
| **[DNS Domain Name Service for Xenix](./ND-895561-1-EN.md)** | ND-895561-1-EN | PI | New product implementing BIND-based DNS server/resolver (named, libresolv, nslookup) for Xenix with ExceLAN. |

---

### DOMINO / NUCLEUS

| Product | Document # | Type | Description |
|---|---|---|---|
| **[DOMINO Maintenance Kit](./ND-895056-S2-EN.md)** | ND-895056-S2-EN | Delivery List | Delivery/structure list for DOMINO Maintenance Kit C03, referencing DOMINO Maintenance and NUCLEUS guide. |
| **[NUCLEUS Library](./ND-895058-S1-EN.md)** | ND-895058-S1-EN | Delivery List | Product structure sheet for NUCLEUS Library C06 (38 SW-modules, 87 DOC-modules). |
| **[NUCLEUS Maintenance Kit](./ND-895059-S2-EN.md)** | ND-895059-S2-EN | Delivery List | Product structure sheet for NUCLEUS Maintenance Kit C03, DOMINO Maintenance and NUCLEUS Software Guide. |

---

### MS-DOS / Windows Software

| Product | Document # | Type | Description |
|---|---|---|---|
| **[Microsoft Windows 2.10](./ND-895001-S2-EN.md)** | ND-895001-S2-EN | Delivery List | Internal delivery list for Microsoft Windows 2.10 version B02, 5-diskette MS-DOS format set. |
| **[Excel for OWS](./ND-95008-1-EN.md)** | ND-95008-1-EN | PI | Microsoft Excel bundle for Office Workstations, with ND reference card and function-key keyboard templates. |

---

### ND-PILOT (Computer-Based Training)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[ND-PILOT Runtime for ND-500/5000](./ND-211253-1-EN.md)** | ND-211253-1-EN | PD | Runtime system for ND-PILOT tutorials on ND-500/ND-5000. |
| **[ND-PILOT Runtime for ND-110](./ND-211254-S1-EN.md)** | ND-211254-S1-EN | Delivery List | Internal delivery list of manuals/diskettes for ND-PILOT Runtime on ND-110, English/Norwegian A03. |
| **[ND-PILOT for ND-110](./ND-211300-S1-EN.md)** | ND-211300-S1-EN | Delivery List | Delivery list for ND-PILOT A03, English and Norwegian diskette sets with User Guide and addendum manuals. |
| **[ND-PILOT Tutorial in NOTIS-WP for ND-500/5000](./ND-895214-S01-EN.md)** | ND-895214-S01-EN | Delivery List | Delivery list for ND-PILOT tutorial guide in NOTIS-WP, English and Norwegian manual/diskette sets. |
| **[ND-PILOT Tutorial in NOTIS-WP for ND-110](./ND-895215-S01-EN.md)** | ND-895215-S01-EN | Delivery List | Delivery list for ND-PILOT tutorial guide in NOTIS-WP on ND-110, English and Norwegian sets. |

---

### LED Editor and Debugger

| Product | Document # | Type | Description |
|---|---|---|---|
| **[LED-DEBUGGER for ND-500/5000](./ND-211157-2-EN.md)** | ND-211157-2-EN | PD | Source symbolic debugger for ND-500/5000, requires SIN III VS K workmode 312B. |
| **[LED for ND-500/5000](./ND-211160-2-EN.md)** | ND-211160-2-EN | PD | Language Program Editor for ND-500/5000, requires SIN III VS K workmode 312B. |
| **[LED for ND-5100/XI](./ND-895014-S1-EN.md)** | ND-895014-S1-EN | Delivery List | Delivery list for LED editor product for ND-5100/XI version B04, single diskette. |
| **[LED for OWS](./ND-895270-S1-EN.md)** | ND-895270-S1-EN | Delivery List | Product structure sheet for LED editor for OWS with LED User Guide. |

---

### TECHNOVISION (CAD/CAM)

| Product | Document # | Type | Description |
|---|---|---|---|
| **[TECHNOGSU Graphics Service Utilities](./ND-895174-S1-EN.md)** | ND-895174-S1-EN | Delivery List | Product structure sheet for TECHNOGSU Graphics Service Utilities A00, no manuals listed. |
| **[Basic TECHNOVISION Software for TECHNOSTATION](./ND-895496-1-EN.md)** | ND-895496-1-EN | PI | Revision B01 packaging of TECHNOVISION CAD/CAM modules (TECH2D, TECHMILL, etc.) for TECHNOSTATION installs. |
| **[TECHNOVISION Postprocessor Generator (TECHPPG)](./ND-895519-1-EN.md)** | ND-895519-1-EN | PI | New product: FORTRAN-source software tool for generating postprocessors on ND500/5000, delivered as sources/NRF libraries. |

---

### Backup Manager

| Product | Document # | Type | Description |
|---|---|---|---|
| **[Backup Manager for ND-500/5000](./ND-250351-3-EN.md)** | ND-250351-3-EN | Other (Source Description) | Source description for Backup Manager C01 (BM-DEFINITION/OPERATOR/SCHEDULER/FILERESTORE), restore from 155MB streamer tape. |
| **[Backup Manager for ND-500/5000](./ND-895055-1A-EN.md)** | ND-895055-1A-EN | PI | Backup Manager version B02 product info: SCSI/DOMINO backup, SIBAS on-the-fly backup, mirroring support. |
| **[Backup Manager for ND-500/5000](./ND-895055-3A-EN.md)** | ND-895055-3A-EN | PI | Backup Manager version C01 product info: adds Unix TAR sequential-media handling. |

---

### Test Programs and Diagnostics

| Product | Document # | Type | Description |
|---|---|---|---|
| **[Test Programs for ND-100/110/120](./ND-895076-1p-EN.md)** | ND-895076-1p-EN | PI | Lists the full TPE-MON-100 test-program suite (cache, memory, disk, HDLC, SCSI, terminal, etc.) for ND-100/110/120. |
| **[Test Programs for ND-100/110/120](./ND-895076-2A-EN.md)** | ND-895076-2A-EN | PI | Updated test-program suite listing; DISC-TEMA, DISK-MM, SCSI-TV, UNIVERS-DMA modified, DISK-MM/SCSI-TV now run online. Confirmed against a real floppy set (`ND-210523I01-XX-01D`/`-02D`): both disks' `TPE-MON-100-B01:BPUN` plus ~30 individual `:TEST`/`:NEXT` module files (CACHE, DISC-TEMA, DISK-MM, SCSI-TV, MEMORY, PAGING, OCTOBUS, PIOC-ETHER, PRINTERS, and more) match this PI sheet's own listing name-for-name — floppy images and full NDFS file listings in the [Norsk Data Software Archive](https://github.com/RetroCoreLabs/norskdata-software-archive) (product `ND-210523`); wiki page [ndwiki.org/wiki/ND-210523I](https://www.ndwiki.org/wiki/ND-210523I). |
| **[Bridge Test for ND-100](./ND-895446-S1-EN.md)** | ND-895446-S1-EN | Delivery List | Internal product structure sheet for a bridge test program for ND-100. |
| **[Test Programs No. 1 for NORD-10/NORD-12/ND-100 (ND-10324E)](./ND-10324E.md)** | ND-10324E | Diskette listing + PD | NORD Software Library diskette sheet (dated 1982-11-26) for 15 test/utility BPUN programs (BIG-RAND, DISC-TERM, FLOPPY-RAN, MEMORY, MULTI, TAMB-MAG, TERMINAL-ASYNC, etc.) plus a program description section. Wiki-sourced (NDwiki), not from the standard oracle series. |
| **[DISC-TEMA version D — release note](./ND-10324E_Disc-Tema_version_D_info_NO.md)** | ND-10324E (companion) | Release note (NO) | One-page Norwegian caveat for DISC-TEMA version D: disk-unit 0 must always be spinning during use; fixed in the next version. Bundled with the ND-10324E diskette sheet above on NDwiki. |

---

### Operator Environment and System Administration

| Product | Document # | Type | Description |
|---|---|---|---|
| **[Multi-Machine Operator Environment (OEM)](./ND-211078-1-EN.md)** | ND-211078-1-EN | PD | Operator toolset for monitoring terminals/TADs/batches across multiple ND-110/ND-500/5000 machines. |
| **[UE-ERRORS Translation Kit](./ND-250178-S4-EN.md)** | ND-250178-S4-EN | Delivery List | Internal delivery list for UE-ERRORS Translation Kit D07 in English, Norwegian and Swedish diskette sets. |
| **[Performance Monitor](./ND-895028-S1-EN.md)** | ND-895028-S1-EN | Delivery List | Delivery list for Performance Monitor B01, tuning/capacity-planning manual and 8-diskette set. |
| **[Configuration Dictionary](./ND-895090-1-EN.md)** | ND-895090-1-EN | PI | Configuration Dictionary version A product info: displays HW/OS configuration, split out from Operator Environment package. |
| **[File Manager](./ND-895091-S1-EN.md)** | ND-895091-S1-EN | Delivery List | Delivery list for File Manager C03, English and Norwegian, with File Manager Introduction guide. |
| **[File System Verification](./ND-895092-1A-EN.md)** | ND-895092-1A-EN | PI | File System Verification version A product info: checks directory data-structure consistency, now supports discs up to 630 MB. |
| **[Operator Environment Menu System](./ND-895093-S1-EN.md)** | ND-895093-S1-EN | Delivery List | Delivery list for Operator Environment Menu System B01, English and Norwegian versions. |
| **[User Area Manager](./ND-895095-1-EN.md)** | ND-895095-1-EN | PI | User Area Manager version A product info: create/delete/rename SINTRAN user areas, split from Operator Environment package. |
| **[User Environment (version D07)](./ND-895256-3-EN.md)** | ND-895256-3-EN | PI | Describes USER ENVIRONMENT security/personal-environment features and new-version rationale. |

---

### Hardware and Peripherals

| Product | Document # | Type | Description |
|---|---|---|---|
| **[Mass Storage Utilities](./ND-211067-1-EN.md)** | ND-211067-1-EN | PD | Stand-alone TPE disc-utility program (DISC-TEMA) for offline mass-storage handling on ND-100/110. |
| **[Additional fonts for ND-616CN](./ND-211419-1-EN.md)** | ND-211419-1-EN | PD | Downloads soft-fonts to the Philips GP300 printer and Matrix Printer 616CN on ND-110 SIN III >= J. |
| **[VTM terminal tables (Type 128/129) DEC VT200](./ND-211464-1-EN.md)** | ND-211464-1-EN | PD | New VTM terminal-table product enabling DEC VT200 non-standard terminals to communicate with ND software. |
| **[Disk Mirroring](./ND-895039-S2-EN.md)** | ND-895039-S2-EN | Other (Product Structure Sheet) | Internal product structure sheet for Disk Mirroring E, operator guide and single diskette. |
| **[DISK RESTORE](./ND-895081-S1-EN.md)** | ND-895081-S1-EN | Delivery List | Delivery list for DISK RESTORE version B01, diskette-only, no manual. |
| **[ND Network Printing for Windows](./ND-895237-S1-EN.md)** | ND-895237-S1-EN | Delivery List | Product structure sheet listing modules, manual, and diskette for Network Printing for Windows. |
| **[Keyboard Drivers for NOTIS PC Keyboard](./ND-895487-1A-EN.md)** | ND-895487-1A-EN | PI | Rewritten VKM drivers (DOS/Windows) mapping PC keyboard codes to NOTIS keyboard codes, plus Windows keyboard drivers. |
| **[Keyboard Drivers for NORTEXT Enhanced Keyboard](./ND-895558-1-EN.md)** | ND-895558-1-EN | PI | VKM DOS/Windows keyboard drivers converting PC keycodes to NORTEXT keyboard codes. |
| **[Publisher 19" Display Unit with Adapter Card](./ND-899092-1-EN.md)** | ND-899092-1-EN | Install | Hardware install guide for a 19-inch display adapter card on ND-PC and OWS workstations. |
| **[MS-DOS Printer Driver for ND Applications](./ND-899129-2-EN.md)** | ND-899129-2-EN | PI | Printer driver package (EPSON, ND-420/460/715/720/730 etc.) for ND workstations using SSY-LIB printing. |
| **[SCSI Optical Disk Drive LD 1200](./ND-99118-1-EN.md)** | ND-99118-1-EN | Install | Installation procedure for the LD 1200 SCSI optical disk drive in a Norsk Data computer system. |

---

### Other Software

| Product | Document # | Type | Description |
|---|---|---|---|
| **[PC-LINK for APPLE II](./ND-10719-1-EN.md)** | ND-10719-1-EN | PD | ND-host file transfer program pairing with APPLE IIe NU-LINK over async terminal lines up to 9600 baud. |
| **[IBM 3780/2780-II Emulator](./ND-10777-1-EN.md)** | ND-10777-1-EN | PD | BSC 3780/2780/2770 protocol emulator for file transfer between ND and non-ND computers. |
| **[DIALOGUE Example for ND-100](./ND-10869-2-EN.md)** | ND-10869-2-EN | PD | Demonstration and example system for ND-DIALOGUE, requiring SIBAS-II, User Environment, NOTIS-WP, NRL, QED. |
| **[BRF-Linker for ND-100](./ND-210721-3-EN.md)** | ND-210721-3-EN | PD | BRF-Linker v.C error-correction/change release for loading, linking and editing BRF-unit program files. |
| **[UNIQUE-II ISAM for ND-100](./ND-210731-2-EN.md)** | ND-210731-2-EN | PD | 4th-generation ISAM database load/update/retrieve program, new product v.B for SIN III VS/VSX >=I. |
| **[SNA 3270 Terminal Emulator](./ND-210742-3-EN.md)** | ND-210742-3-EN | PD | Emulates IBM SNA 3270 Display System over SNA Gateway, requires SINTRAN III I+ and X-MESSAGE. |
| **[C-COMPILER for ND-500](./ND-210761-2-EN.md)** | ND-210761-2-EN | PD | C language compiler for ND-500, new product requiring SIN III VSX >=J. |
| **[ND Coloured Books, Red/Blue Book Job, File and Mail Transfer](./ND-210770-2-EN.md)** | ND-210770-2-EN | PD | JNT Red/Blue/Grey Book job/file/mail transfer between manufacturers' computers on ND-500 SINTRAN >=J. |
| **[ND Coloured Books, Yellow Book Transport Service (YBTS)](./ND-210771-2-EN.md)** | ND-210771-2-EN | PD | Network-independent transport service (YBTS) enabling other coloured-books protocols, error correction v.B. |
| **[ND Coloured Books, Blue Book File and Mail Transfer](./ND-210866-2-EN.md)** | ND-210866-2-EN | PD | JNT Blue/Grey Book file and mail transfer between manufacturers' computers on ND-500 SINTRAN >=J. |
| **[DIALOGUE Example for ND-100](./ND-210869-3-EN.md)** | ND-210869-3-EN | PD | Demonstration and example system for ND-DIALOGUE v.C, requires SIBAS-II, User Environment, NOTIS-WP. |
| **[ADA for ND-500/5000](./ND-211114-1-EN.md)** | ND-211114-1-EN | PD | Ada compiler for compiling Ada programs under SINTRAN III on ND-500/ND-5000. |
| **[FTX Error Logger](./ND-211128-S1-EN.md)** | ND-211128-S1-EN | Delivery List | Internal delivery list for the FTX Error Logger product, version A03. |
| **[UNKNOWN (ND-110/PC Integration)](./ND-230001-1-EN.md)** | ND-230001-1-EN | Other | Table of contents for an ND-110/PC integration manual covering booting, watchdog, power fail and startup modes. |
| **[Y for ND-100](./ND-300000-1-EN.md)** | ND-300000-1-EN | PI | Small screen utility program that clears the screen and homes the cursor, for ND-100. |
| **[Y for ND-500/5000](./ND-300001-1-EN.md)** | ND-300001-1-EN | PI | New product: screen-clear/cursor-home utility Y ported to ND-500/5000, single-file diskette listing. |
| **[REPRO for ND-500](./ND-895065-S1-EN.md)** | ND-895065-S1-EN | Delivery List | Delivery list for REPRO for ND-500 version D10, diskette-only, no manual. |
| **[SPRINT Spooling System (German)](./ND-895072-S1-EN.md)** | ND-895072-S1-EN | Delivery List | Product structure sheet for SPRINT Spooling System German version A04, replaces revision A03. |
| **[Graphic Server for Leonardo](./ND-895089-S3-EN.md)** | ND-895089-S3-EN | Delivery List | Product structure sheet for Graphic Server for Leonardo D01, no manuals listed. |
| **[ND Dialogue Processor (NDP) and NDP-Compiler](./ND-895099-S01-EN.md)** | ND-895099-S01-EN | Delivery List | Delivery list for NDP and NDP-Compiler version F00 for ND-110/500(0), with NDP Reference Manual. |
| **[Standard XCOM Installation Procedure](./ND-895240-S1-EN.md)** | ND-895240-S1-EN | Delivery List | Delivery list for Standard XCOM installation procedure, no manuals, one diskette. |
| **[XCOM Extended Command Processor](./ND-895241-S1-EN.md)** | ND-895241-S1-EN | Delivery List | Delivery list for XCOM Extended Command Processor with manual and diskette references. |
| **[DSS Basic System](./ND-895242-S01-ENa.md)** | ND-895242-S01-ENa | Delivery List | Product structure sheet for DSS Basic System listing SW modules and diskettes. |
| **[DSS Libraries](./ND-895242-S01-ENb.md)** | ND-895242-S01-ENb | Delivery List | Product structure sheet for DSS Libraries listing SW modules and diskettes. |
| **[DSS Test Program](./ND-895242-S01-ENc.md)** | ND-895242-S01-ENc | Delivery List | Product structure sheet for DSS Test Program listing SW modules and diskettes. |
| **[FTX Automatic Reconfiguration](./ND-895244-S1-EN.md)** | ND-895244-S1-EN | Delivery List | Delivery list for FTX Automatic Reconfiguration with FTX Configuration Management Guide. |
| **[ND C for ND-500/5000](./ND-895245-S01-EN.md)** | ND-895245-S01-EN | Delivery List | Delivery list for ND C compiler for ND-500/5000 with C Reference Manual. |
| **[ND TELEX Remote User Module](./ND-895263-S1-EN.md)** | ND-895263-S1-EN | Delivery List | Product structure sheet for ND TELEX Remote User Module with TELEX guides. |
| **[ND TELEX (German)](./ND-895264-S1-EN.md)** | ND-895264-S1-EN | Delivery List | Product structure sheet for ND TELEX in German with TELEX Benutzerhandbuch. |
| **[ND-SHELL](./ND-895265-S1-EN.md)** | ND-895265-S1-EN | Delivery List | Product structure sheet for ND-SHELL with Reference Card. |
| **[ND-100 Server for WPX/IPS Bridge](./ND-895267-1A-EN.md)** | ND-895267-1A-EN | PD | Program description for COMMTAD server bridging WPX/IPS to ND via shared memory and MTADs. |
| **[SOFTICE for SINTRAN (Software Key Installation Program)](./ND-895530-1-EN.md)** | ND-895530-1-EN | PI | First release (A01) of SOFTICE, which stores software activation keys on SINTRAN to unlock protected software. |
| **[SOFTICE for Xenix (Software Key Installation Program)](./ND-895532-1-EN.md)** | ND-895532-1-EN | PI | First release (A01) of SOFTICE for XENIX, storing software activation keys to unlock protected software. |

---

*285 documents. Part of the [NDInsight](../../README.md) Norsk Data / SINTRAN III documentation and preservation project. All manuals are Norsk Data A.S publications; OCR'd from scanned originals.*
