# RT programs and reentrant subsystems in PLANC

How to take a PLANC program that works when you type its name, and install it into SINTRAN
properly: as an **RT program** that runs with no terminal and starts at boot, or as a **reentrant
subsystem** that every user shares one copy of.

Everything marked VERIFIED was done on D100 and the machine's own answer is quoted. Everything
else is marked. Nothing here is reasoning from a manual alone - the manuals mislead in at least
three places recorded below, and each one cost a build cycle.

---

## 1. Which one do you want?

| | RT program | Reentrant subsystem |
|---|---|---|
| Started by | `@RT <name>`, or SINTRAN at boot | a user typing `@<name>` |
| Terminal | **none** | the caller's own |
| Copies in memory | one, always resident | one, shared by every caller |
| Data | one set, shared | **per caller** |
| Lives on | an RT segment | a reentrant segment |
| Installed with | `RT-LOADER` | `DUMP-PROGRAM-REENTRANT` or `DUMP-REENTRANT` |
| Suits | servers, daemons, background work | commands and tools people run |

A chat SERVER wants to be an RT program: nobody is logged in as it, and it must survive every
terminal being logged out. A chat CLIENT wants to be reentrant: twenty users run it at once and
each needs their own nickname, their own port and their own screen.

**They are not exclusive.** `FA-SERVER-TAD` appears in `LIST-REENTRANT` and the file access
servers also run as RT programs; a product can ship both.

---

## 2. RT programs

### 2.1 Where the name comes from - VERIFIED

**The RT program's name is the PLANC `PROGRAM` unit, not the file.** A source in `CHATSV:PLNC`
declaring

```planc
PROGRAM : chatServer
```

installs as **`CHATSER`**, and `@RT CHATSV` finds nothing at all.

Two rules combine to give that:

 - PLANC identifiers are unique in their **first ten characters**, but an **ND symbol is exactly
   five characters** on the loader side, so `chatServer` is truncated to `CHATSE`... and then
   `CHATSER` is what the RT description actually carries. **Read the name off the machine rather
   than predicting it** - `LOAD` prints it, see below.
 - Case is not preserved: everything arrives upper case.

**So: load it, read the name the loader prints, and use that.** This is the single most common way
to lose half an hour here.

### 2.2 Installing it - VERIFIED, and the manual's own example is wrong

```
@RT-LOADER
  LIST-FREE-RT-DESCRIPTIONS      -> first free was 63417
  LIST-FREE-SEGMENTS             -> 2512 upwards free
  NEW-SEGMENT   2512 / RING 2 / type, protection, WP-NP all defaulted
  LOAD          CHATSV           onto 2512, no linking segment
  LOAD          XMP-100-1-B02    onto 2512
  LOAD          PLANC-1BANK-F00  onto 2512
  WRITE-REFERENCES               -> EMPTY, so nothing is unresolved
  END-LOAD                       <- BEFORE the next command
  CHANGE-RT-DESCRIPTION  CHATSER / PRIORITY 75 / SEGMENT ONE 2512 / RING 2
  EXIT-LOADER
@RT CHATSER
```

**Read the segment number and the RT description off the machine on the day.** `LIST-FREE-SEGMENTS`
and `LIST-FREE-RT-DESCRIPTIONS` are there for exactly that; the numbers above were free on D100 on
2026-08-18 and are not constants.

**Three ways the manual's worked example misleads.** The SIBAS install in
`Reference-Manuals/210166F SIBAS II for ND-100.md` shows:

```
DECLARE-PROG SIB2A,.........
CHANGE-RT-DES SIB2A,56,SIBPF00,SIB2A;11,1,2,1
END-LOAD
```

 1. **`END-LOAD` comes BEFORE `CHANGE-RT-DESCRIPTION`, not after.** Done the manual's way it
    answers **`THIS COMMAND IS NOT ALLOWED NOW`**. Issue `END-LOAD` first and the identical
    command is accepted without a word.
 2. **`DECLARE-PROGRAM` is not needed - `LOAD` already made the program.** Loading the BRF prints
    `NO PRIORITY IN: CHATSER`, which is not an error: the RT description exists and has no
    priority yet. A following `DECLARE-PROGRAM CHATSER` answers `RT-PROGRAM ALREADY DEFINED`.
    **This print is also how you learn the name** - see 2.1.
 3. The order INSIDE the loader is the other way round from the linker: **the program first, then
    the libraries that satisfy it.**

### 2.2.1 Stopping one, and loading a new build over it - VERIFIED

**`@ABORT <name>` stops an RT program.** That is the whole command - no confirmation, no prompts,
and it is what the COSMOS start mode itself uses (`@ABORT FSART` before `@RT FSART`). So the cycle
while developing is:

```
@ABORT CHATSER          stop it
   ... rebuild ...
@RT CHATSER             start it again
```

**Do not go looking for `STOP-TERMINAL` here.** That is for a program a USER started on a terminal
line, and it is a different and much more awkward thing (see 4). An RT program holds no terminal, so
`ABORT` is both sufficient and the only thing needed - which is one more argument for making a
server an RT program in the first place.

**Loading a new build over an existing one.** The segment already in use does not appear in
`LIST-FREE-SEGMENTS`, so take the next free one and re-point the description at it:

```
@RT-LOADER
  LIST-FREE-SEGMENTS         -> 2512 absent (in use), 2513 free
  NEW-SEGMENT   2513 / RING 2 / rest defaulted
  LOAD          CHATSV       onto 2513
```

and the loader then asks something it does NOT ask on a first install:

```
NO PRIORITY IN:  CHATSER

 CHATSER REPLACING? YES
```

**Answer `YES`** - it is asking permission to point the existing RT description at this new load.
Then the libraries, `WRITE-REFERENCES`, `END-LOAD`, and `CHANGE-RT-DESCRIPTION` with the new
segment.

**`CHANGE-RT-DESCRIPTION` asks SEVEN questions, and the last two are easy to miss:**

```
RT-PROGRAM: CHATSER
PRIORITY: 75
SEGMENT ONE: 2513
SEGMENT TWO:                 (blank)
START ADDRESS:               (blank - keep what was loaded)
RING: 2
INITIAL PAGE TABLE:          (blank)
ALTERNATIVE PAGE TABLE:      (blank)
```

Sending `EXIT-LOADER` while `INITIAL PAGE TABLE:` is still waiting feeds it as the ANSWER, and the
whole command dies with **`ILLEGAL PARAMETER TYPE`** - losing the description change you just typed.
**Read the screen after every answer.** The same trap as batching commands over a terminal line.

Afterwards, check with `@LIST-RT-DESCRIPTION CHATSER`:

```
PASSIVE
       SEGMENTS 1  AND  2    REENT  NPIT APIT RING PRIORITY
ACTUAL   :   2513B      0B            1B   1B   2      75B
START ADDRESS:   6250B   LAST STARTED:    36 SECS
```

**`PASSIVE` with a recent `LAST STARTED` means it ran and EXITED**, not that it never started. For a
server the usual reason is that its name was already claimed by another copy - `LIST-NAMES` in
`X-COMM` tells you who holds it.

### 2.3 Choosing a priority - VERIFIED neighbours

`WRITE-PROGRAMS` lists what is already there. On D100:

```
XROUT 34    XMFIDO 66    XFTRAD 71    FSART 75    ENNS0 101
```

`CHATSER` was given **75**, copying `FSART` - the file server, the closest thing on the machine to
what it does. **Copy the priority of the nearest existing program** rather than picking a number;
these are the machine's own answer to "how urgent is a service like this".

### 2.4 The one code change RT forces - and one fear that was WRONG

**`OUTPUT(1, ...)` writes to device 1, and an RT program has no caller to write to.**

**But it did NOT stop the program.** The plan for this work said the terminal writes had to move to
a log file BEFORE an RT load could work. They did not: `CHATSER` loaded, started and served real
clients with every `OUTPUT` still in place. Moving them to a file is worth doing - those lines are
how a seat leak and a burst failure were found, and they now go nowhere anybody can read - but it
is an improvement, not a prerequisite. **Do not let it block the load.**

To move them, open a log file once at start-up with `MON50`, write with `MON2`, close with `MON43`.
The sequence is written out in
[PLANC-XMSG-PROGRAMMING-GUIDE.md](PLANC-XMSG-PROGRAMMING-GUIDE.md), which uses it for a per-user
config file. **`MON43` is CLOSE; `MON54` is DELETE-FILE** - they are easy to swap and the wrong one
is destructive.

### 2.5 Starting it at boot - NOT VERIFIED

Two files, two different moments:

| File | When | What belongs in it |
|---|---|---|
| `(SYSTEM)HENT-MODE:MODE` | every **COLD** start | rebuild the segment: the RT-LOADER sequence in 2.2 |
| `(SYSTEM)LOAD-MODE:BATC` | every **WARM** start | start it: `@RT CHATSER` |

wired with

```
NEXT-INITIAL-COMMAND APPEND-BATCH 1 (SYSTEM)LOAD-MODE:BATC SYSTEM-OUTPUT-1
```

**Run the batch by hand before wiring it in.** A broken initial command runs on every restart with
no terminal there to stop it.

**And end `LOAD-MODE` with `@SET-AVAILABLE`.** `COS-FA-SERV-E04:MODE` finishes with
`SET-UNAVAILABLE`, which locks every login out - measured, and it cost most of a session.

### 2.6 What an RT program buys you - VERIFIED

`CHATSER` was proved by three C# clients over HDLC saying two lines each: 3 welcomed, **18 `Said`
messages heard** (3 x 2 x 3, exact), 27 frames, and `CHAT-LOBBY` back to **16 free** afterwards.

**And the terminal was in use for `X-COMM` the whole time.** That is the entire point: a background
server that holds a terminal line is also a server that SINTRAN's idle-logout will eventually kill.

---

## 3. Reentrant subsystems

### 3.1 What is already installed - VERIFIED, D100, 2026-08-18

`@LIST-REENTRANT`:

```
           START RESTART SEGMENT   NAME
              0B      0B     65B   BACKUP-SYSTEM-B
           5314B   5314B     67B   CONNECT-TO
              2B      3B     67B   LIST-SYSTEMS
              0B      1B     70B   TRANSFER-FILE
              2B      2B     70B   TRANSFER
              3B      3B     70B   REMOTE-BATCH
              4B      4B     70B   COMPRESS
              5B      5B     70B   COMPRESS-FILE
          21703B  21703B     73B   FA-SERVER-TAD
           4472B   4472B     74B   FS-ADMINISTRATOR
              0B      1B     76B   XMSG-COMMAND
              0B      1B     77B   COS-SPOOL-SERVIC
              0B      1B    100B   QED
         177777B 177776B    107B   MAC
              0B      1B    110B   NPL
            752B    752B    111B   PLANC-100
              0B      0B    112B   PED
             11B     11B    113B   FORTRAN-100
```

**Read that table carefully, because it answers more than it looks like it does.**

**ONE SEGMENT CAN CARRY SEVERAL SUBSYSTEMS.** Segment `70B` holds FIVE - `TRANSFER-FILE`,
`TRANSFER`, `REMOTE-BATCH`, `COMPRESS` and `COMPRESS-FILE` - at START addresses 0, 2, 3, 4 and 5.
Segment `67B` holds two. They are one body of shared code with several front doors, and the name
you type picks which door. If you are building a family of related commands, this is how the
system itself does it: **one segment, one entry point each**, not five copies.

**START and RESTART are usually different, and the difference is the point.** The common pattern is
`0B` / `1B`: entry 0 is a cold start, entry 1 is what a re-entry uses, so the second run can skip
initialisation the first one did. Where the two are equal (`PLANC-100` at `752B`/`752B`,
`FS-ADMINISTRATOR` at `4472B`) the program simply does not distinguish them. `MAC` uses `177777B` /
`177776B`, which are -1 and -2.

**And it tells you what tooling the machine has.** MAC, NPL, PLANC-100, PED, FORTRAN-100 and QED are
all here. **Subsystems live in shared memory: `LIST-FILES` cannot see them and its silence proves
nothing.** `LIST-REENTRANT` is the only honest answer to "is the assembler installed?"

### 3.2 The two install commands - VERIFIED prompts

Both are SYSTEM commands. `@HELP -REE` and `@HELP -PROG` list the family:

```
SYSTEM:   DUMP-REENTRANT              SYSTEM:   DUMP-PROGRAM-REENTRANT
          LIST-REENTRANT
SYSTEM:   DELETE-REENTRANT
SYSTEM:   DEFINE-REENTRANT-PROGRAM
SYSTEM:   LOAD-REENTRANT-SEGMENT
SYSTEM:   CLEAR-REENTRANT-SEGMENT
```

**`HELP` names them and nothing more - it prints no parameter list.** To learn the parameters, type
the command and read the prompts; ESC aborts before it does anything. Asked that way on D100:

```
@DUMP-PROGRAM-REENTRANT
NAME: PROBE-ONLY
FILE NAME:
```

**`DUMP-PROGRAM-REENTRANT` takes TWO parameters: NAME and FILE NAME.** It takes a finished `:PROG`
file and works the rest out itself. That makes it the one to try first.

```
@DUMP-REENTRANT
NAME:
```

`DUMP-REENTRANT` takes more - name, start, restart and the input file - matching the START and
RESTART columns above. The PLANC compiler installs ITSELF this way, and that is the best worked
example on the machine:

```
@DUMP-REENTRANT PLANC-100,0,1,<input-file>
```

which is exactly the `0B` / `1B` cold-and-re-entry pattern, on the row `PLANC-100 752B 752B 111B`.

**NOT VERIFIED: the remaining prompts of `DUMP-REENTRANT` in order.** The probe was stopped at the
first one rather than risk installing something. Type it and read them when you need them.

### 3.2.1 A PLANC program installed end to end - VERIFIED, D100, 2026-08-18

The chat client, built by `CHATCC:MODE` into `CHAT:PROG`, installed as a subsystem:

```
@DUMP-PROGRAM-REENTRANT
NAME: CHAT-CLIENT
FILE NAME:CHAT:PROG

@
```

**It answers nothing at all when it works** - no confirmation, no segment number, no summary. The
blank line and the prompt back ARE the success. Do not read the silence as a refusal; check the
table instead:

```
@LIST-REENTRANT
           START RESTART SEGMENT   NAME
             ...
             11B     11B    113B   FORTRAN-100
          14130B  14130B    114B   CHAT-CLIENT      <- new
```

**`DUMP-PROGRAM-REENTRANT` chose the segment and the start address by itself.** It took the next
free segment after the last one in use (`113B` -> `114B`) and read the start address `14130B` out
of the program file. Nothing had to be worked out by hand, and no segment was created first - which
is the whole difference from `DUMP-REENTRANT`, where those are parameters you supply.

Then, run by name:

```
@CHAT-CLIENT
CHAT: xmpfopn                  status  16933 library error, XMX offset     37
```

The shared copy runs and gets as far as opening its XMSG port. `16933` is `XMXENRU`, "XMSG is not
running" - XMSG was down at the time, and the program reporting it cleanly and stopping is the
behaviour wanted, not a fault in the install.

**STILL TO PROVE: two users at the same time.** That is the only thing a reentrant subsystem does
differently from an ordinary program, so until it has been run by two logged-in users at once, the
install is verified and the REENTRANCY is not. It needs XMSG up.

**And it is reversible** - `@DELETE-REENTRANT` takes it out again.

### 3.2a RELOADING one: DELETE FIRST. A rebuild does NOT reach the subsystem.

**MEASURED on D100, 2026-08-19.** Installing over an existing name is REFUSED:

```
@DUMP-PROGRAM-REENTRANT NDCHAT,CHAT:PROG
NAME ALREADY USED ON REENTRANT SUBSYSTEM
```

The correct cycle is **delete, then load again** - both silent on success:

```
@DELETE-REENTRANT NDCHAT
@DUMP-PROGRAM-REENTRANT NDCHAT,CHAT:PROG
@LIST-REENTRANT                       % 14373B  14373B  114B  NDCHAT
```

**Why this matters more than a one-line error suggests.** A reentrant subsystem is a COPY taken at
install time. Recompiling the source and relinking the `:PROG` changes NOTHING about what the
subsystem runs - it goes on serving the old code until you delete and re-install it. The refusal is
a single line with no `***` and no error number, and in a MODE file it scrolls past without stopping
anything, so the build "succeeds" and the machine keeps running the previous binary.

**While you are still iterating, the other option is simpler: delete the subsystem and run the
`:PROG` file directly.** Install it only when the build is final.

**Both parameters work on one line** - `@DUMP-PROGRAM-REENTRANT <name>,<file>` - as well as through
the `NAME:` / `FILE NAME:` prompts.

### 3.2b The name must not be a prefix-extension of the program file

**This cost hours.** The subsystem was first called `CHAT-CLIENT` while the program file was
`CHAT:PROG`. SINTRAN matches command names by ABBREVIATION, so **`@CHAT` ran the SUBSYSTEM**, not the
program - and every rebuild appeared to change nothing, because the thing being tested was the
frozen install.

The tell: a newly added `OUTPUT` does not print, while a later one in the same routine does.

Reinstalled as **`NDCHAT`** - no shared prefix, so `@CHAT` runs the file and `@NDCHAT` runs the
subsystem, and the two can be compared honestly. Verified end to end 2026-08-19: `@NDCHAT` read the
per-user `CHAT:CNFG`, printed `you are OLAV`, joined `(LOBBY)` and answered `/who`.

### 3.3 Making a PLANC program fit - the part that is on YOU

`DUMP-PROGRAM-REENTRANT` will take almost any program file. Whether the result is CORRECT is a
property of the source, and the compiler will not tell you.

**One copy of the code, one set of data per caller.** Everything a caller needs to keep must live
where a second caller cannot see it. In the chat client that is the nickname, the port, the room
name, the server's magic number, the typed line - all of it.

Three things to check in a PLANC source before dumping it, **NOT VERIFIED as a complete list**:

 1. **`INISTACK` is per-invocation and must run at entry.** The chat client already does this at
    the top of its `PROGRAM` unit.
 2. **Anything declared at MODULE level is shared.** In a program run one at a time that is
    convenient; shared between users it is a defect that shows up as one person's nickname
    appearing on another person's screen.
 3. **A file opened by name resolves against whoever is logged in.** That works FOR you: the chat
    client's `CHAT:CNFG` is per-user with nothing in the source naming a user. Measured with OLAV
    and ANNA, each getting their own.

**Test it before believing it**, and the test is two users at once - a single user cannot fail the
only thing that is different about being reentrant.

### 3.4 The order to do it in

```
1  build the ordinary program first and run it by hand      @CHAT
2  install it under a NON-prefix name                       @DUMP-PROGRAM-REENTRANT NDCHAT,CHAT:PROG
3  check it is there                                        @LIST-REENTRANT
4  run it as TWO different users at the same time           @NDCHAT
5  to RELOAD after a rebuild - delete FIRST, always         @DELETE-REENTRANT NDCHAT
                                                            @DUMP-PROGRAM-REENTRANT NDCHAT,CHAT:PROG
```

**Step 1 is not optional.** A program that does not work standing alone will not work shared, and
the reentrant version is far harder to look at while it runs.

**Step 5 is not optional either** - see 3.2a. Skipping the delete gets you
`NAME ALREADY USED ON REENTRANT SUBSYSTEM` and the OLD code stays installed.

---

## 4. Stopping things, which is not symmetric

| What it is | How to stop it |
|---|---|
| an RT program | **`@ABORT <name>`** - one command, no prompts |
| a reentrant subsystem | it ends when the user's invocation ends; `@DELETE-REENTRANT` removes the install |
| a program a user started on a terminal | `@STOP-TERMINAL <n>` - **awkward, see below** |

**This asymmetry is a reason to choose RT.** A server started with `@CHATSV` on a terminal line and
blocked in a waiting monitor call is close to unkillable:

 - closing the terminal session does not stop it;
 - **ESC does not stop it** - ESC cannot interrupt a monitor-call wait, so the break lands only when
   the call returns, which for a server waiting for a message may be never;
 - a full XMSG `STOP-X`/`START-X` does not stop it.

`@STOP-TERMINAL <n>` does, using `@WHO-IS-ON` to find the number - but it asks

```
TERMINAL IS NOT STOPPED, IT IS IN "ESCOFF" OR IN A WAITING STATE,
DO YOU WANT TO REMOVE IT FROM THIS STATE AND STOP IT?
```

**and you get ONE attempt.** That question is a prompt, so whatever you send next is the answer -
send anything other than `YES` and every later `STOP-TERMINAL` for that line answers
**`ALREADY EXECUTED BY TERMINAL: nn`**, from every terminal, and the line stays held. Measured
2026-08-18: the answer was accidentally a following command, and the line could not be recovered.

**`@ABORT` has none of this.** Nothing to time, nothing to answer, nothing to lose.

## 5. Traps, collected

 - **The RT name is the `PROGRAM` unit, truncated - read it off the loader's own output.**
 - **`@ABORT <name>` stops an RT program** - that is all it takes.
 - **A reload asks `<name> REPLACING?`** - answer `YES`.
 - **`CHANGE-RT-DESCRIPTION` asks SEVEN questions**; the page-table pair at the end will eat your
   next command and answer `ILLEGAL PARAMETER TYPE`.
 - **`PASSIVE` with a recent `LAST STARTED` means it ran and exited**, not that it never ran.
 - **`END-LOAD` before `CHANGE-RT-DESCRIPTION`**, against the manual's example.
 - **`NO PRIORITY IN: <name>` is not an error.** It is the RT description being created.
 - **`OUTPUT(1, ...)` does not stop an RT load** - it just goes nowhere.
   *Seen 2026-09-28 on the VSX/500 M pack under RetroCore:* an RT program's `OUTPUT(1, ...)`
   lines (FINGERS: "listening on TCP port 79", "answered, query kind 2") came out on the
   operator console, captured by `console log`. Where it goes may depend on the system.
 - **`LIST-FILES` cannot see a subsystem.** Only `LIST-REENTRANT` can.
 - **`HELP` prints no parameters** - ask the command itself and ESC out.
 - **`DUMP-PROGRAM-REENTRANT` says NOTHING when it succeeds.** Check `LIST-REENTRANT`, not the
   screen.
 - **`MON43` is CLOSE, `MON54` is DELETE-FILE.**
 - **Put `SET-AVAILABLE` at the end of any boot MODE file** you write.
 - **Some monitor calls are for background programs only, and an RT program that calls one
   is ABORTED, not given an error code.** Measured 2026-09-28 with the Finger server loaded as
   RT program FINGERS: TerminalStatus (330B) and ExecuteCommand (317B) each ended the program
   with `ERROR * 15B.0B * <time> * FINGERS.<address>`. That happened through `MONITOR_CALL`
   and also through a MAC routine issuing `MON 330` directly. Check the caller line on the
   call's page in ND-860228 ("All users | Background programs") before designing an RT
   program around a call. GetUserEntry (44B) and all of SLIB worked in RT.
 - **Need a server with no terminal that uses a background-only call? Make it a batch job.**
   A batch process is a background program: start a free processor with `@BATCH 2`, then
   `@APPEND-BATCH 2 <file>:BATC <log file>`, where the file starts `@ENTER SYSTEM,,,` and then
   runs the program. Processor 1 runs the boot job, so leave it alone. See
   [the Finger server case study](../../Case-Studies/Finger-Server.md), section 7.

---

## See also

 - [PLANC-TCP-UDP-SOCKETS.md section 10](PLANC-TCP-UDP-SOCKETS.md#10-a-server-with-no-terminal-rt-program-or-batch-job) -
   a TCP server as an RT program: the RT-LOADER session with the SLIB libraries, and when
   it must be a batch job instead.
 - [PLANC-XMSG-PROGRAMMING-GUIDE.md](PLANC-XMSG-PROGRAMMING-GUIDE.md) - the XMSG API these
   programs are built on, with the file-I/O monitor calls written out.
 - [PLANC-DEVELOPER-GUIDE.md](PLANC-DEVELOPER-GUIDE.md) - the language itself.
 - [PLANC-MONITOR-CALLS.md](PLANC-MONITOR-CALLS.md) - `MONn` and what is reachable from PLANC.
 - `SINTRAN/XMSG/DOC/PLAN-CHATSV-AS-RT-PROGRAM.md` - the as-built RT install this is drawn from.
 - `Reference-Manuals/210166F SIBAS II for ND-100.md` - a full RT install worked through, with the
   command-order fault noted in 2.2.
