# Case Study: A Finger Server for SINTRAN III

`FINGER` is a Finger server (RFC 1288) written in PLANC. It listens on TCP port 79 and
answers one query per connection with who is logged in, or with one SINTRAN user's
sessions. The user and terminal data come from documented SINTRAN monitor calls, and the
network side uses ND's socket library SLIB.

| File | What it is |
|---|---|
| [`FINGER.PLNC`](Finger-Server/FINGER.PLNC) | the server |
| [`FINGER.MODE`](Finger-Server/FINGER.MODE) | compile and link; needs `MON-CALL-1B-A00` |
| [`FINGER.CONF`](Finger-Server/FINGER.CONF) | example settings: who may be listed |
| [`README.md`](Finger-Server/README.md) | the files and their format on the pack |

It uses `SLIBF00:DEFS` from the [echo server case study](TCP-Echo-Server/SLIBF00.DEFS).

**Ties together:**

- [SLIB API reference](../Languages/Application/SLIB-API-REFERENCE.md) and [TCP and UDP programs in PLANC](../Languages/Application/PLANC-TCP-UDP-SOCKETS.md): the network side.
- [PLANC monitor calls](../Languages/Application/PLANC-MONITOR-CALLS.md): `MONn` routines and `MONITOR_CALL`.
- [Running COSMOS TCP/IP on RetroCore](../../Installation/Communication/TCP/RUNNING-TCPIP-ON-RETROCORE.md): the network underneath.

---

## 1. What it answers

A client connects, sends one line ending in CR LF, reads the answer, and the server closes
the connection. Every line of the answer ends in CR LF.

| Query | Answer |
|---|---|
| empty line | everyone logged in: login, terminal, status (`Logged in`, or `Batch` for an idle batch processor) |
| `/W` | the same list with mode, CPU minutes and minutes logged in |
| `USER` | `Login: USER`, then one line per terminal session, or `Not logged in.` |
| `/W USER` | the same with mode and CPU minutes per session |
| an unknown name | `No such user: NAME` |
| `user@host` | a refusal: this server does not forward |
| anything else | `Not a valid query...` |
| no line in time | `No query received in time.` |
| more than 64 characters | `Query too long...` |

As run on the VSX/500 M reference machine:

```
C:\> finger -l @192.168.199.40
[192.168.199.40:79]
Login             Terminal  Status      Mode                  CPU min  On min
SYSTEM            39        Logged in   suspended             0        27
SYSTEM            48        Logged in   command               2        18
SYSTEM            49        Logged in   command               0        2
RT                1         Logged in   command               0        4
SYSTEM            670       Batch       command               0        28
SYSTEM            768       Logged in   suspended             0        28
```

At the same moment `@WHO` listed exactly these six: 1 RT, 39, 48, 49, 768 and 670 SYSTEM.

"Terminal" is the number `@WHO` and `@TERMINAL-STATUS` print: the SINTRAN logical device
number in decimal, and 1 for the operator console. 670 is batch processor 1, and 768 is a
TAD, where telnet sessions and the FTP server log in.

---

## 2. What was verified

On SINTRAN III VSX/500 M under RetroCore, with COSMOS TCP/IP D02, SLIB B01 and
PLANC-100-F00. The build gives 0 diagnostics, no `***` lines in the listing, and nothing
left undefined.

| Test | Result |
|---|---|
| empty line, `/W`, `SYSTEM`, `/W SYSTEM`, `system`, `  SYSTEM  ` | right answer, every line ends CR LF, server closes |
| `TCP-IP`, a user that exists and is not logged in | `Login: TCP-IP` / `Not logged in.` |
| `RONNY`, `NOSUCHUSER` (no such accounts) | `No such user: ...` |
| `ronny@example.com` | forwarding refused |
| `SYS;TEM` | not a valid query |
| 80 characters | query too long |
| a bare LF instead of CR LF | accepted |
| a client that connects and sends nothing | `No query received in time.` after the idle timeout |
| Windows `finger`, with and without `-l`, list and user | all four right |
| Linux `finger` in WSL, with and without `-l`, list, user, unknown, not logged in | all six right |
| `FINGER:CONF` with `LIST NONE` and `hide system` | list refused; `SYSTEM` gets `No public information for SYSTEM.` |
| the list against `@WHO` at the same moment | the same six sessions, the console and the batch processor included |
| run as a batch job (`FINGERB:BATC`) on batch processor 2, with no terminal | the same answers, from Windows and WSL `finger`; the processor shows as SYSTEM on 672, as in `@WHO` |
| loaded as an RT program | **does not work**: see section 7 |

---

## 3. Where the data comes from

The SINTRAN side is a handful of small routines in layer 1 of the source, and none of them
knows about TCP. Every call is documented in ND-860228-2-EN, *SINTRAN III Monitor Calls*:

| Need | Call | How PLANC reaches it |
|---|---|---|
| who is logged in on a logical device: user, state, mode, CPU minutes, minutes logged in | 330B TerminalStatus, 44-byte answer | `MONITOR_CALL(330B, ldn, buffer)` with `MON-CALL-1B-A00` linked |
| does this user exist? | 44B GetUserEntry; error 46B means no such user | `MON44` (PLANC runtime) |

**There is no call that lists sessions.** `@WHO-IS-ON` reads SINTRAN's internal table
BACKTAB directly, and no documented monitor call exposes it. The server therefore asks
TerminalStatus about every logical device number that appendix B of the manual names as a
place a session can be, about 480 numbers (decimal):

| Numbers | What they are |
|---|---|
| 2-63 | terminals 2-32 |
| 512-575 | terminals 33-64 |
| 646 | "Terminal 1, data field" (1206B): **the operator console** |
| 670-688, even | batch processes 1-10, data field |
| 768-895 | TADs 1-96 |
| 1024-1087 | terminals 65-128 |
| 1472-1599 | terminals 129-256 |
| 1600-1638, even | batch processes 11-30, data field |

It keeps every device whose state is not -1 ("no one logged in"). State 1 is an active
terminal, and state 0 is a batch processor. A user on two terminals shows as two sessions.
A list answer takes about 3.6 seconds on the emulated machine.

**How these numbers were found, because the first version got them wrong.** It scanned only
the plain terminal ranges and kept only state 1. Against `@WHO` it missed two sessions:

- **The console.** To a background program, device 1 means "own terminal". The console
  answers on its data field, 646, and `@TERMINAL-STATUS 646` prints it as log number 1.
  So FINGER prints 646 as terminal 1, as `@WHO` does.
- **Batch processor 1 (670).** TerminalStatus reports it as state 0.

**Not shown, because SINTRAN has no documented source for it:**

- **Full name.** Neither the user entry nor TerminalStatus holds one.
- **Idle time.** Nothing records it. The mode (command, program running, suspended) is shown instead.
- **Login time of day.** TerminalStatus gives "time logged in in minutes", a duration, and that is what the server prints.
- **Last login date.** The user entry holds dates, but the manual gives no format for them.

**Deliberately not shown:**

- **The last command.** TerminalStatus returns it, but it can carry file names and arguments.
- **The password and friend fields** of the user entry are never read.

**Run it as SYSTEM.** GetUserEntry on another user's entry is allowed only for SYSTEM and
RT.

---

## 4. Handling the query

- **Read only up to the first line feed.** A CR just before it is the terminator. A bare LF
  is also accepted.
- **At most 64 characters.** Anything longer gets `Query too long`.
- **A read timeout from SLIB's no-activity timer** (ND-860372 4.5.2). It is set to 10 seconds
  of ND time with the "signal the application" bit, so a blocking `SLrecv` returns 20249
  SLEtimedout. The emulated ND clock runs slower than the PC's, so this took about 20 to 25
  seconds of PC time here.
- **Only spaces around the query are dropped.** A `/W` prefix is recognised. A name must be
  1 to 16 letters, digits or `-`, and it is checked before any lookup, then put in upper case.
- **`user@host` is recognised and refused.** RFC 1288 allows a server to refuse forwarding.
- **Output is made network ASCII on purpose.** The parity bit is dropped, control characters
  become `?`, and one routine, `putNL`, writes every line end as CR LF.

### The polling trap

The first version read the query non-blocking and slept between reads with SINTRAN's
SuspendProgram (`MN104`). Windows `finger.exe` sends the name and the CR LF in **two** TCP
segments. The first read got the name, and the CR LF never came, although the card had
acknowledged it at once. Every Windows query timed out.

SLIB takes in new data only inside its own calls, and a SINTRAN sleep is not one of them.
The fix is the blocking read with the no-activity timer described above.

---

## 5. Configuration: `FINGER:CONF`

Finger tells anyone who asks who is online, so the list is configurable. The file is read
at start-up from the user that runs the server. One setting goes on each line, case does not
matter, and `%` starts a comment.

| Line | Effect |
|---|---|
| `LIST ALL` | the plain query lists everyone logged in (the default) |
| `LIST NONE` | the plain query answers `The list of users on this system is not public.` |
| `HIDE <USER>` | never show this user, in the list or when asked by name (up to 16 users) |

With no file, the server lists everyone and says so on its terminal. It prints a warning for
a line it does not understand.

---

## 6. Build and run

1. Copy the files to the pack, as the folder [README](Finger-Server/README.md) says.
   `SLIBF00:DEFS` must be there too.
2. As SYSTEM: `@MODE FINGER:MODE,,`, then check for `0 DIAGNOSTICS` and an empty
   `LIST-ENTRIES-UNDEFINED`.
3. `@FINGER`. It prints `FINGER: listening on TCP port 79` and then one line per query.
   Stop it with ESC.

To run it with no terminal, give it a batch processor of its own instead (section 7):

```
@BATCH 2
@APPEND-BATCH 2 FINGERB:BATC FINGERB-LOG:SYMB
```

Every connection from a Windows client also prints the TCPP "Invalid argument" line on the
console. That comes from the card firmware and is harmless. See
[RE/TCP-OPTION-PARSER.md](../../Installation/Communication/TCP/RE/TCP-OPTION-PARSER.md).

---

## 7. Why it is not an RT program, and what to use instead

An RT program would need no terminal and could start at boot. FINGER loads as one: the
RT-LOADER names it `FINGERS`, from `PROGRAM : fingersrv` cut to seven characters.
Queries that need no session data, such as a forwarding refusal or an unknown user, were
answered.

**The first TerminalStatus call aborts it:**

```
ERROR   * 15B.0B * 1998-09-27 23:41:40 * FINGERS.66025B
```

ND-860228 says TerminalStatus "can only be used from background programs, not RT
programs", and SINTRAN enforces that by aborting the program. Measured three ways:

| Route to the monitor call | As an RT program |
|---|---|
| `MONITOR_CALL(330B, ...)` (TerminalStatus) | aborted, ERROR 15B |
| `MONITOR_CALL(317B, ...)` (ExecuteCommand, to run `TERMINAL-STATUS` into a file) | aborted, ERROR 15B |
| a MAC routine issuing `MON 330` itself | aborted, ERROR 15B, at the `MON` instruction |

The same MAC routine worked from a terminal. CallCommand (70B) and ExecuteCommand (317B) are
also documented as background-only. No documented monitor call gives an RT program the
session list.

**Use a batch job.** A batch process is a background program with no terminal, and
TerminalStatus is allowed there: the manual says "You may use the monitor call for batch
jobs". [`FINGERB.BATC`](Finger-Server/FINGERB.BATC) logs in as SYSTEM and runs `@FINGER`.
A batch processor running FINGER is busy for as long as FINGER runs, and batch processor 1
runs the boot job (`LOAD-MODE:BATC`), so FINGER gets processor 2 of its own. The machine
has five, and `@LIST-BATCH-PROCESS` shows which are passive:

```
@BATCH 2
BATCH NUMBER =      2
@APPEND-BATCH 2 FINGERB:BATC FINGERB-LOG:SYMB
```

A passive processor must be started with `@BATCH <n>` first; appending to it before that
answers `BATCH PASSIVE`. `@START-BATCH` does not exist on this system ("NO SUCH FILE NAME").
Run this way, FINGER answered every query, and it lists itself as batch processor 2's
session on device 672. Its terminal output goes to the batch output file
`FINGERB-LOG:SYMB`. `@ABORT-BATCH 2` stops it.

**Create the log file with `@CREATE-FILE FINGERB-LOG:SYMB,0`, a file that grows.** Made with
`,1` it is one fixed page, 2048 bytes. Once FINGER's lines filled it, every new job on that
batch processor ended at once, with nothing in the queue and nothing in the log.

**Two things a batch job needs that a terminal does not, both found by running it:**

- **A CPU time limit.** Every batch job printed `MAXIMUM TIME IS 1 MINUTES`, and SINTRAN
  aborts a batch job whose CPU time passes its maximum (System Documentation, routine
  TIMER). FINGER used 8 CPU minutes in 40 minutes at a terminal. The maximum is the fourth
  field of `@ENTER`, so `FINGERB.BATC` starts with `@ENTER SYSTEM,,,32000`. A test job
  confirmed `MAXIMUM TIME IS  32000 MINUTES`.
- **A server that waits for TCP/IP.** Started from the boot batch job, FINGER ran seconds
  before the TCP start had finished, got 20229 from SLinit (SLEconstart, no contact with the
  packet level), and ended. It now retries SLinit every 10 seconds for up to 10 minutes.

### Starting it at boot

The boot batch job `(SYSTEM)LOAD-MODE:BATC` runs on batch processor 1. Two lines just
before its `@SET-AVAILABLE` start FINGER on processor 2:

```
@MODE (TCP-IP)TCP-START-D02:MODE,,
@CC Finger server (TCP port 79) as a batch job on batch processor 2.
@CC It must not be RT: TerminalStatus aborts an RT program (ERROR 15B).
@BATCH 2
@APPEND-BATCH 2 FINGERB:BATC FINGERB-LOG:SYMB
@SET-AVAILABLE
```

Measured on a cold start of the reference machine: port 79 answered 72 seconds after
RetroCore started, with nobody logged in, and Windows and Linux `finger` got the right
answers.
