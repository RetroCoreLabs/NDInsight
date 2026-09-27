# SINTRAN III Operations Guide

**A Comprehensive Guide for System Operators**

This guide provides clear operational procedures for SINTRAN III systems, covering terminal management, initial setup, and program execution.

---

## Table of Contents

1. [Terminal Timeout and Disconnection](#terminal-timeout-and-disconnection)
2. [ND-500 Initial System Setup](#nd-500-initial-system-setup)
3. [Loading and Running Programs](#loading-and-running-programs)
4. [Understanding Programs, Users, and RT](#understanding-programs-users-and-rt)

---

## Terminal Timeout and Disconnection

### Overview

SINTRAN III provides mechanisms to automatically disconnect inactive users from terminals. This is critical for:
- **Data security**: Prevents unauthorized access to unattended logged-in terminals
- **Resource management**: Frees up system resources from inactive sessions
- **Network management**: Controls timeout for remote connections via COSMOS

### Terminal Timeout Configuration

#### For Local Terminals (BAS - Background Allocation System)

SINTRAN can automatically log out inactive users after a predefined interval. Before logout occurs, the user receives a warning message and the terminal bell sounds. This repeats every minute until timeout.

**Key Points:**
- Inactive use = no input from or output to the terminal
- System doesn't check what programs are running
- Users who leave terminals without saving risk losing all work since last save

**To enable timeout for all terminals:**

```
*BACKGROUND-ALLOCATION-UTILITIES
FUNCTION: TIMEOUT-ON
```

This enables the TIMEOUT function initially on all terminals.

**To enable/disable for specific terminals:**

```
ENABLE-TIMEOUT <logical unit number>
DISABLE-TIMEOUT <logical unit number>
```

**Example: Enable timeout for all terminals except console:**

```
*BACKGROUND-ALLOCATION-UTILITIES
FUNCTION: TIMEOUT-ON
FUNCTION: DISABLE-TIMEOUT
LOGICAL UNIT NO: 1
FUNCTION: EXIT
```

The console (typically unit 1) should remain in a secure, locked data room.

#### For Remote Network Connections (COSMOS)

For users connecting via COSMOS network, use the Connect-To service program (CT-SERV):

**Setting timeout values:**

```
CT-SERV: SET-TIMEOUT-VALUES
NOT LOGGED IN: <minutes>
NOT ACTIVE: <minutes>
```

- **NOT LOGGED IN**: Time allowed after connecting but before logging in (default: 1 minute)
- **NOT ACTIVE**: Time allowed for inactivity after login (default: 30 minutes)

When timeout occurs, COSMOS automatically disconnects the inactive user from the network.

**Example:**

```
CT-SERV: SET-TIMEOUT-VALUES
NOT LOGGED IN: 2
NOT ACTIVE: 10
```

This sets 2 minutes before login and 10 minutes for inactivity.

**To disable timeout (RT or SYSTEM users only):**

```
CT-SERV: TIMEOUT-OFF
```

Users will not be disconnected regardless of inactivity time.

**To make timeout changes permanent:**

After setting timeout values, use DUMP-PROGRAM to save changes:

```
CT-SERV: SET-TIMEOUT-VALUES
NOT LOGGED IN: 2
NOT ACTIVE: 10

CT-SERV: DUMP-PROGRAM
PROG-FILE: "NEW-CONNECT-TO"
```

**To restore default values:**

```
CT:: LIST-TIMEOUT-VALUES
CT-SERV: SET-TIMEOUT-VALUES
NOT LOGGED IN: 1
NOT ACTIVE: 30
```

### Manual Disconnection

To manually disconnect a user:

```
@TERMINAL-STATUS
```

This shows all logged-in users with their terminal numbers.

```
@STOP-TERMINAL <terminal number>
```

**CAUTION:** This aborts all activity immediately - users have NO chance to save work!

**Terminal number ranges:**
- Direct terminals: 1, 36, 37...63, 544, 545...575
- COSMOS TADs: 768, 769...863
- Batch processors: 670, 672...686 (steps of two)

---

## ND-500 Initial System Setup

### First-Time Boot Procedure

#### Hardware Preparation

**For ND-100 and ND-500 Cabinets:**

1. **Battery switches** (from rear panel):
   - Remove rear panel to access power supply
   - Set battery switches under power control panel to "ON"
   - This enables standby battery for power failures

   **CAUTION:** In some configurations, "STANDBY" light comes on after mains is switched off. In these cases, battery switches MUST be turned OFF when powering off to prevent battery damage!

2. **Power on**:
   - Replace front and rear panels
   - Turn key switch on operator panel to "ON"
   - Computer is now ready for software start

**For Compact Computers:**
- Turn key switch to "ON"

**For Satellite Computers:**
- Turn mains switch on (at rear of terminal)
- Turn key switch to "ON"

#### Console Terminal Setup

**Tandberg TDV 2200/9 (standard from 1985):**
- Turn power switch on (left side)
- Ensure "LINE" indicator light is on (ON-line mode)
- If not, press LOCAL key

**OMNI 825 Hardcopy Terminal:**
- Turn power switch on (rear)
- Set LOCAL/LINE switch to "LINE"

**FACIT 4440 - TWIST Terminal:**
- Turn power switch on (bottom right)
- Strike SET-UP key (top left corner)
- Strike 4 key until "ON LINE" appears
- Strike SET-UP again to exit

#### Initial Loading from Floppy

This procedure loads SINTRAN into a brand new system disk where no files or users exist.

**Step 1: Load SINTRAN from Floppy**

Follow the warm start procedure (section 3.2 of System Supervisor manual) with the floppy diskette.

**Step 2: Create Main Directory**

```
ENTER
PASSWORD:
NO MAIN DIRECTORY        [Expected message]

CREATE-DIRECTORY
DIRECTORY NAME: PACK-ONE
DEVICE-NAME: DISC-70MB-1
DEVICE-UNIT: 0
BIT FILE ADDRESS: [Use default - middle of disk]
```

**Notes:**
- PACK-ONE is conventional name for system disk
- Device name from your SINTRAN order form
- For small disks, may need different bit-file address (see chapter 4 of manual)
- 70MB disk = 512*70 = 35,840 pages (some used by file system)

**Step 3: Create SYSTEM User**

```
@ENTER-DIRECTORY
DIRECTORY-NAME: PACK-ONE
DEVICE-NAME: DISC-70-MB-1 0

@CREATE-USER
USER NAME: SYSTEM

@LOGOUT
-- EXIT --
ESC
```

**Step 4: First Login as SYSTEM**

```
ENTER SYSTEM:
PASSWORD: [Press Enter - no password yet]

@CHANGE-PASSWORD
OLD PASSWORD: [Press Enter]
NEW PASSWORD: [Enter secure password]

@GIVE-USER-SPACE SYSTEM 15000
```

**Space requirements:**
- Slightly more than 29MB total needed
- Small systems (Satellite/Compact): 5000-10000 pages sufficient
- Give extra space initially, return surplus after installation

**Step 5: Set File Access Permissions**

```
@SET-INITIAL-FILE-ACCESS R,RWA,RWAD
@SET-DEFAULT-FILE-ACCESS R,RWA,RWAD
```

Parameters: public, friend, own access
- Adjust based on data-security requirements
- These settings apply to all future users

**Step 6: Create Standard Users**

Required standard users:

| User Name | Purpose |
|-----------|---------|
| RT | Owner of RT-programs |
| SCRATCH | Scratch files for background programs |
| UTILITY | ND software applications |
| PROGRAM-FILES | ND software of type :PROG |
| BPUN-FILES | ND software of type :BPUN |
| FLOPPY-USER | Copying files to/from floppy |

**ND-500 specific users:**
| User Name | Purpose |
|-----------|---------|
| DOMAINS | ND-500 application programs |
| N502-MICRO-TEST | ND-500 test programs (can delete if space limited) |

Create each user:

```
@CREATE-USER
USER NAME: RT

@CHANGE-PASSWORD    [For RT user]
OLD PASSWORD:
NEW PASSWORD: [Enter secure password]

@CREATE-USER
USER NAME: SCRATCH
```

Continue for all standard users. Only RT and SYSTEM require passwords.

**Step 7: Create System Files**

Essential system files must be created on the system disk. See Table 6 in System Supervisor manual for complete list.

Key files include:
- SINTRAN:DATA (63 pages, Allocated)
- SEGFILE:DATA (Configuration-dependent, Allocated)
- SWAP-FILE-x:SWAP (Configuration-dependent, Contiguous)
- LOAD-MODE:BATC (Configuration-dependent, Indexed)
- MAILBOX:DATA (10-20 pages, Indexed)

---

## Loading and Running Programs

### Program Types in SINTRAN III

SINTRAN III is a multiprogramming real-time operating system that allows concurrent execution of:
- **Real-time programs** (RT programs)
- **Time-sharing programs** (interactive/background)
- **Batch programs**
- **Remote batch programs**

### Understanding Program Execution

#### Real-Time (RT) Programs

RT programs run at hardware interrupt levels and have high priority. They:
- Respond to external events with guaranteed timing
- Run independently of time-sharing system
- Can communicate via internal devices (200₈ to 277₈)
- Are started by specific commands or system initialization

**To list RT programs:**

```
@LIST-RT-PROGRAMS
```

Output shows:
- System-included RT programs (DUMMY, STSIN, etc.)
- Application RT programs (XMSG, COSMOS, etc.)
- User-written RT programs

**System RT programs include:**
- **DUMMY**: Idle process in execution queue
- **STSIN**: Initialization, starts system RT programs
- **BAKxxx**: Background process for terminal xx
- **BCHxxx**: Batch processor xx
- **TADxx**: Terminal Access Device xx (COSMOS)
- **RWRTxx**: Block-oriented I/O devices
- **RTERR**: Prints error messages

**Do NOT stop system kernel RT programs!**

**To start an RT program:**

```
@START <RT-program-name>
```

**To abort an RT program:**

```
@ABORT <RT-program-name>
```

**CAUTION:** Only abort user RT programs or application RT programs when following proper shutdown procedures. Never abort kernel RT programs.

#### Background (Time-Sharing) Programs

These are normal user programs running in interactive mode from terminals.

**To execute a program:**

```
@<program-name>
```

For example:
```
@PED               [Text editor]
@FORTRAN           [Fortran compiler]
@NOTIS-WP          [Word processor]
```

**Program execution with parameters:**

```
@<program-name> <parameters>
```

**To load a program into memory:**

```
@LOAD-PROGRAM <program-file>
```

**To run a loaded program:**

```
@RUN
```

Or combine:
```
@EXECUTE <program-file>
```

#### Batch Programs

Batch programs run non-interactively from batch processors.

**To start a batch processor:**

```
@START-BATCH <batch-number>
```

> **Measured 2026-09-28 on SINTRAN III VSX/500 M: `@START-BATCH` does not exist** - it answers
> `"START-BATCH" NO SUCH FILE NAME`. The command that starts a passive batch processor is
> `@BATCH <batch-number>` (it answers `BATCH NUMBER = n`), as in the System Supervisor manual,
> ND-30.003.7. Appending a job to a passive processor answers `BATCH PASSIVE`.


**To list batch processes:**

```
@LIST-BATCH-PROCESS
```

**To submit a batch job:**

```
@SUBMIT-BATCH <batch-file>
```

**To abort batch processor:**

```
@ABORT-BATCH <batch-number>
```

### The LOAD-MODE File

The LOAD-MODE file contains commands executed automatically when SINTRAN starts. This is where:
- System initialization occurs
- RT programs are started
- Default configurations are set
- Application environments are initialized

**Editing LOAD-MODE:**

```
ENTER SYSTEM <password>
@PED (SYSTEM)LOAD-MODE:BATC
```

**Example LOAD-MODE content:**

```
ENTER SYSTEM <password>
@SET-ERROR-DEVICE 2
@START IMPORTANT-RT-PROGRAM
@GIVE-N500-PAGES 2000
@START-SPOOLING LINE-PRINTER
@SET-AVAILABLE
```

**Important notes:**
- First command must be ENTER SYSTEM with password
- Test commands manually before adding to LOAD-MODE
- Comment what each command does
- Terminate with CTRL+ESC twice

---

## Understanding Programs, Users, and RT

### The Three-Level Architecture

SINTRAN III operates on a three-level protection architecture:

#### Ring Levels

1. **Ring 0 & 1**: User programs
2. **Ring 2**: Operating system (SINTRAN kernel)

The ring protection system prevents user programs from accessing or corrupting the operating system.

### Users in SINTRAN

Users are organizational entities that:
- Own files and directories
- Have disk space allocations
- Control access permissions
- Execute programs within their context

**User types:**

**System Users** (predefined):
- **SYSTEM**: Operating system owner, system administration
- **RT**: Owns all real-time programs
- **SCRATCH**: Temporary files for background processes
- **UTILITY**: System utilities

**Application Users**:
- Created for specific applications or individuals
- Have own disk space, passwords, file access rights

### Relationship: Programs, Users, and RT

#### How They Connect

1. **User logs in** → Creates a background process (BAKxx RT program)
2. **User executes program** → Program runs in context of BAKxx
3. **Program needs I/O** → Uses SINTRAN monitor calls
4. **I/O request** → Handled by RT drivers (RWRTxx, etc.)

```
Terminal User → BAKxx (RT program) → User Program → SINTRAN Services → RT Drivers
```

#### Background Processes (BAKxx)

When a user logs in to a terminal:
- SINTRAN creates a Background Allocation RT program (BAKxx)
- This RT program manages that terminal's activity
- User programs execute within this RT program context
- All I/O for the terminal goes through its BAKxx

**Example:**
```
@LIST-RT-PROGRAMS

NAME    STATUS
BAK01   ACTIVE    [Terminal 1 - console]
BAK38   ACTIVE    [Terminal 38 - user logged in]
BAK39   PASSIVE   [Terminal 39 - user idle]
```

#### Batch Processors (BCHxx)

Similar to BAKxx but for batch jobs:
- BCHxx RT programs manage batch execution
- Run jobs from batch queue non-interactively
- Numbered 670, 672, 674, etc.

#### Monitor Calls

User programs interact with SINTRAN through monitor calls:

**Common monitor calls:**
- `INBT` / `OUTBT`: Byte input/output
- `RFILE` / `WFILE`: File read/write
- `PROG`: Program control
- `WAIT`: Wait for event
- `SIGNAL`: Signal event

These calls transition from user level (Ring 0/1) to system level (Ring 2).

### RT Programs vs User Programs

| Aspect | RT Programs | User Programs |
|--------|-------------|---------------|
| Priority | Hardware interrupt levels | Time-sliced scheduling |
| Response | Deterministic, guaranteed | Best-effort |
| Ownership | User RT | Any user |
| Context | Independent | Within BAKxx/BCHxx |
| File Access | RT-OPEN files | Normal OPEN files |
| Starting | @START command or STSIN | @EXECUTE or @ command |
| Stopping | @ABORT command | Normal exit or @STOP-TERMINAL |

### Practical Examples

#### Example 1: User Running a Program

```
User "JOHN" logs in at terminal 38
→ SINTRAN creates BAK38 RT program
→ John executes: @FORTRAN
→ FORTRAN compiler runs within BAK38 context
→ Compiler uses John's file space and permissions
→ I/O operations handled by RT drivers
```

#### Example 2: RT Program Operation

```
System supervisor starts database:
@START SIBAS
→ SIBAS RT program loads from user RT
→ Runs independently at RT level
→ Multiple users can access SIBAS
→ Each user's BAKxx communicates with SIBAS RT
```

#### Example 3: Checking System Activity

```
@TERMINAL-STATUS
LOG.NO  USER    MODE     CPU-MIN  LAST COMMAND
1       SYSTEM  COMMAND  5        TERMINAL-STATUS
38      JOHN    PROGRAM  12       FORTRAN

@LIST-RT-PROGRAMS
NAME    STATUS
DUMMY   READY
STSIN   PASSIVE
BAK01   ACTIVE
BAK38   ACTIVE
SIBAS   RTWAIT
```

This shows:
- Two users logged in (SYSTEM, JOHN)
- Two background RT programs active (BAK01, BAK38)
- SIBAS database RT program waiting for requests

### File Ownership and RT

**RT-OPEN files:**
- Opened by RT programs using special RT-OPEN monitor call
- Remain open across user sessions
- Used by databases, communication programs
- Owned by user RT
- Must be closed with @RTCLOSE-FILE before system stop

**Normal files:**
- Opened by user programs
- Closed when program exits or user logs out
- Owned by the user executing the program

**To list RT-open files:**

```
@LIST-RTOPEN-FILES

FILE NUMBER 00100: (PACK-ONE:KNUTH)ALGORITHMS:DATA::1
```

**To close RT-open file:**

```
@RTCLOSE-FILE 100
```

---

## System Monitoring Commands

Quick reference for operational monitoring:

```
@WHO-IS-ON                    # Users logged in
@TERMINAL-STATUS              # Detailed terminal info
@LIST-RT-PROGRAMS             # All RT programs
@LIST-BATCH-PROCESS           # Batch processors
@LIST-OPEN-FILES              # User's open files
@LIST-RTOPEN-FILES            # RT-open files
@TADADM                       # COSMOS TAD status
@ND-500-MONITOR               # ND-500 specific (if applicable)
```

---

## Best Practices

### Security
- Always set passwords for SYSTEM and RT users
- Configure timeout for all non-console terminals
- Use appropriate file access permissions
- Monitor inactive sessions regularly

### Operations
- Test LOAD-MODE commands manually first
- Document all configuration changes
- Keep console terminal in secure location
- Regular backups before system modifications

### Resource Management
- Monitor RT-open files before system stop
- Check for idle users consuming resources
- Verify proper cleanup of batch jobs
- Ensure adequate disk space allocations

---

## References

This guide is compiled from:
- ND-30.003.007 EN SINTRAN III System Supervisor
- ND-60.062.01D EN SINTRAN III System Documentation
- ND-30.049.1 EN SINTRAN III Tuning Guide

For detailed information, consult these source manuals in the Operations/SINTRAN directory.

---

**Document Version:** 1.0
**Date:** 2025-11-18
**Purpose:** Operations guidance for SINTRAN III system administrators
