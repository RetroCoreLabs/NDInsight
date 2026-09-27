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
| empty line | everyone logged in: login, terminal, status |
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
C:\> finger @192.168.199.40
[192.168.199.40:79]
Login             Terminal  Status
SYSTEM            39        Logged in
SYSTEM            48        Logged in
SYSTEM            768       Logged in

C:\> finger -l SYSTEM@192.168.199.40
[192.168.199.40:79]
Login: SYSTEM
On terminal 39, logged in 12 min, suspended, CPU 0 min
On terminal 48, logged in 3 min, command, CPU 1 min
On terminal 768, logged in 13 min, suspended, CPU 0 min
```

"Terminal" is the SINTRAN logical device number in decimal, the same number
`@TERMINAL-STATUS` prints. 768 is a TAD, which is where telnet sessions arrive.

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

---

## 3. Where the data comes from

The SINTRAN side is a handful of small routines in layer 1 of the source, and none of them
knows about TCP. Every call is documented in ND-860228-2-EN, *SINTRAN III Monitor Calls*:

| Need | Call | How PLANC reaches it |
|---|---|---|
| is this logical device a terminal or a TAD? | 263B GetDeviceType, type 1 or 2 | `MN263` (PLANC runtime) |
| who is logged in on it, mode, CPU minutes, minutes logged in | 330B TerminalStatus, 44-byte answer | `MONITOR_CALL(330B, ldn, buffer)` with `MON-CALL-1B-A00` linked |
| does this user exist? | 44B GetUserEntry; error 46B means no such user | `MON44` (PLANC runtime) |

**There is no call that lists sessions.** The server walks every logical device range that
appendix B of the manual gives for terminals and TADs:

- 2-77B
- 1000-1077B
- 1400-1577B, the TADs
- 2000-2077B
- 2700-3077B

It keeps each device where TerminalStatus reports state 1, an active terminal. A user on two
terminals shows as two sessions.

**Not shown, because SINTRAN has no documented source for it:**

- **Full name.** Neither the user entry nor TerminalStatus holds one.
- **Idle time.** Nothing records it. The mode (command, program running, suspended) is shown instead.
- **Login time of day.** TerminalStatus gives "time logged in in minutes", a duration, and that is what the server prints.
- **Last login date.** The user entry holds dates, but the manual gives no format for them.

**Deliberately not shown:**

- **The last command.** TerminalStatus returns it, but it can carry file names and arguments.
- **The password and friend fields** of the user entry are never read.

**The operator console is not listed.** To a background program, logical device 1 means
its own terminal, and the console has no other number.

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

Every connection from a Windows client also prints the TCPP "Invalid argument" line on the
console. That comes from the card firmware and is harmless. See
[RE/TCP-OPTION-PARSER.md](../../Installation/Communication/TCP/RE/TCP-OPTION-PARSER.md).
