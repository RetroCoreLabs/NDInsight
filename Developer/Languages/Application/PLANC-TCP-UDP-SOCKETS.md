# TCP and UDP Programs in PLANC

How to write, build and test a PLANC program that talks TCP or UDP through ND's socket
library, SLIB. Everything here was built and run on SINTRAN III VSX/500 M, with COSMOS
TCP/IP D02, SLIB B01, PLANC-100-F00 and BRF-LINKER-C01. It was tested from a Windows host.

| You want | Read |
|---|---|
| every call, record and status code | [SLIB-API-REFERENCE.md](SLIB-API-REFERENCE.md) |
| complete working programs | [TCP-Echo-Server case study](../../Case-Studies/TCP-Echo-Server.md) |
| the network running first | [RUNNING-TCPIP-ON-RETROCORE.md](../../../Installation/Communication/TCP/RUNNING-TCPIP-ON-RETROCORE.md) |
| sockets from MAC | [MAC-COOKBOOK.md section 11](../System/MAC-COOKBOOK.md#11-tcp-and-udp-from-mac-through-a-planc-shim) |
| PLANC itself | [PLANC-DEVELOPER-GUIDE.md](PLANC-DEVELOPER-GUIDE.md), [PLANC-LANGUAGE-RULES.md](PLANC-LANGUAGE-RULES.md) |
| a server with no terminal: RT program or batch job | [section 10](#10-a-server-with-no-terminal-rt-program-or-batch-job) |

---

## 1. Before you start

- COSMOS TCP/IP must be running, with TCPP holding the Ethernet card.
  `@(TCP-IP)TCPIP-MONITOR` followed by `netstat a` should list the telnet and FTP listeners.
- The PLANC compiler `PLANC-100-F00:PROG`, and the libraries `PLANC-1BANK-F00:BRF` and
  `MON-CALL-1B-A00:BRF`, must be on the pack.
- Copy [`SLIBF00.DEFS`](../../Case-Studies/TCP-Echo-Server/SLIBF00.DEFS) to the pack as
  `SLIBF00:DEFS`. ND's own `SLIB:DEFS` uses the word `UNSIGNED`, which PLANC-100-F00 does not
  know, and this copy has that one word removed.
- To get files onto the pack, use FTP in binary mode once the stack runs. For other routes see
  [COPYING-FILES-TO-SINTRAN.md](../../../Installation/Communication/TCP/COPYING-FILES-TO-SINTRAN.md).
  A PLANC source can be plain 7-bit text with CR LF line ends.

---

## 2. The shape of every SLIB program

```planc
MODULE myprog

% 1. Five sizes, declared BEFORE the include: SLIB:DEFS computes SLSzWorkArea from them.
CONSTANT SLMaxPorts = 1
CONSTANT SLMaxSockets = 10
CONSTANT SLMaxSLFork = 1
CONSTANT SLSubTaskStackSize = 1
CONSTANT SLMainTaskStackSize = 1

% 2. ND's definitions and imports.
$LIST OFF
$INCLUDE SLIBF00:DEFS
$INCLUDE (TCP-IP)SLIB:IMPT
$LIST ON

% 3. Module level: the PLANC stack, SLIB's work area, buffers and records.
INTEGER ARRAY : stack ( 0 : 4095 )
INTEGER ARRAY : SocketHeap ( 0 : SLSzWorkArea - 1 )
BYTES : buf ( 0 : 511 )
SLmaxima : maxval
INTEGER : rstat

PROGRAM : main
   INISTACK stack
   % 4. Start SLIB (section 3), then open sockets (sections 4 and 5).
ENDROUTINE

ENDMODULE
```

**The work area must be module level.** SLIB keeps pointers into it for as long as the
program runs. The stack must also be module level, because `INISTACK` needs a global array with lower bound 0.

---

## 3. Starting SLIB

PLANC-100-F00 does not know `USING ... ENDUSING`, which ND's TCCOM uses here, so write
every field out in full:

```planc
SLMaxPorts =: maxval.max_nports
SLMaxSockets =: maxval.max_nsockets
FALSE =: maxval.max_debug
1 =: maxval.max_debfd
NIL =: maxval.max_AUserDataP
6 =: maxval.max_nsallocmsg
0 =: maxval.max_nballocmsg
0 =: maxval.max_nxballocmsg
SLDominoPioc =: maxval.max_tcpdev
SLinit ( ADDR SocketHeap, maxval, NIL, SLMainTaskStackSize, NIL ) =: rstat
```

**20234 from SLinit** means the reserved messages (`max_nsallocmsg + max_nballocmsg`) are
more than `SLMaxSockets`. Raise `SLMaxSockets`.

---

## 4. A TCP server

Create the socket, bind it to a port on any local address, and listen:

```planc
SLsocket ( af_inet, sock_stream, 0, sock ) =: rstat
af_inet =: myaddr.sa_family
7 =: myaddr.sin_port               % the ND-100 is big-endian: no byte swap needed
0 =: myaddr.sin_addr.in_l1         % 0.0.0.0 = any local address
SLbind ( sock, myaddr ) =: rstat
SLlisten ( sock, 1 ) =: rstat
```

Accept a client. `SLaccept` fills in the peer's address and port:

```planc
SLaccept ( sock, csock, peer ) =: rstat
0 =: ioArg.SliocNumber             % blocking mode, as ND's TCCOM does
SLioctl ( csock, SLiocNBIO, ADDR ioArg, SIZE ( ioArg ) ) =: rstat
```

Read and write. **`SLrecv` returns `SLEok` with a count of 0 when the client closes**, and
**`SLsend` may take fewer bytes than offered**, so keep sending until all of them are gone:

```planc
DO
   SLrecv ( csock, ADDR ( buf ( 0 ) ), 512, 0, got ) =: rstat
   WHILE rstat = SLEok
   WHILE got > 0
   0 =: off
   DO
      WHILE off < got
      SLsend ( csock, ADDR ( buf ( off ) ), got - off, 0, sent ) =: rstat
      WHILE rstat = SLEok
      WHILE sent > 0
      off + sent =: off
   ENDDO
   WHILE rstat = SLEok
ENDDO
SLclose ( csock )
```

The whole program is [`ECHOPL.PLNC`](../../Case-Studies/TCP-Echo-Server/ECHOPL.PLNC).

---

## 5. A UDP server

A datagram socket is never connected. Each message arrives with its sender's address, and
the reply goes to an address you give:

```planc
SLsocket ( af_inet, sock_dgram, 0, sock ) =: rstat
% bind exactly as for TCP; no listen, no accept
DO WHILE 1 < 2
   SLrecvFrom ( sock, ADDR ( buf ( 0 ) ), 512, 0, ADDR peer, got ) =: rstat
   SLsendTo ( sock, ADDR ( buf ( 0 ) ), got, 0, ADDR peer, sent ) =: rstat
ENDDO
```

`peer` is an `SLin_sockaddr`. `SLrecvFrom` and `SLsendTo` take a *pointer* to it, so pass
`ADDR peer`. The whole program is
[`ECHOUD.PLNC`](../../Case-Studies/TCP-Echo-Server/ECHOUD.PLNC).

---

## 6. A TCP client

This has not been run here yet. It follows ND-860372 7.5. Fill in the server's address and
port, then connect:

```planc
SLsocket ( af_inet, sock_stream, 0, sock ) =: rstat
af_inet =: server.sa_family
23 =: server.sin_port
192 =: server.sin_addr.in_b1
168 =: server.sin_addr.in_b2
199 =: server.sin_addr.in_b3
1 =: server.sin_addr.in_b4
SLconnect ( sock, server ) =: rstat
% then SLsend / SLrecv as in section 4
```

`SLinNetAddr('192.168.199.1', server.sin_addr)` should also work, and `SLgHbyName` looks a
name up in `AIP-HOSTS`. Neither has been run here.

---

## 7. Building

Compile and link with a MODE file. Copy [`ECHOPL.MODE`](../../Case-Studies/TCP-Echo-Server/ECHOPL.MODE)
and change the name. The library order is in
[SLIB-API-REFERENCE.md section 7](SLIB-API-REFERENCE.md#7-linking).

**Delete the old outputs first.** A quoted file name, as in `"NAME:LIST"` or
`PROGRAM-FILE "NAME"`, means *create*. Both the compiler and the linker refuse with
`FILE ALREADY EXISTS` when the file is still there. ND's own `COMP-TCCOM:MODE` deletes them the same way.

**Give the MODE file even parity.** It goes through SINTRAN's command reader. Run it with
`@MODE NAME:MODE,,`.

**Check three things after every build:**

1. The compiler's summary says `0 DIAGNOSTICS`. The words `(PARITY ERRORS)` in that line
   appear for 7-bit sources, ND's own included files among them. They cause nothing.
2. The listing file `NAME:LIST` has no `***` lines.
3. `LIST-ENTRIES-UNDEFINED` prints nothing.

**Lint before you build.** A compile takes minutes, and the linter takes a second. It finds
undeclared names, which PLANC accepts silently. It has to be able to read ND's included files:

```
python SINTRAN/XMSG/tools/planc-lint.py --include-dir Installation/Communication/TCP/x/D02-gateway-and-clients NAME.PLNC
```

A `(TCP-IP)` prefix in an `$INCLUDE` is looked up in `DIR/TCP-IP/`.

---

## 8. Testing

- Test from another machine or from the Windows host. The ND cannot connect to its own
  address.
- `@(TCP-IP)TCPIP-MONITOR`, then `netstat a`, shows your listener, for example
  `0.0.0.0 port 7 LISTEN`, and every connection with its queues.
- **A program stopped with ESC leaves its sockets behind.** Running the program again
  replaced the old listener on this machine. To remove one by hand, look up its `Cid` in
  `netstat a` and type `kill <cid>` in the monitor.
- From Windows, `telnet 192.168.199.40 7` works for TCP. For exact byte counts and for UDP,
  use a small script that sends known data and compares what comes back.

---

## 9. Traps, all met on the way

One more rule comes from the manual and was not met here. On the ND-100 a receive buffer
must start on a word boundary (ND-860372 7.15). Receiving into `buf ( 0 )` of a module-level
`BYTES` array keeps to it.


| What happened | Why | Fix |
|---|---|---|
| Compile stops in `SLIB:DEFS` | PLANC-100-F00 has no `UNSIGNED` | include `SLIBF00:DEFS` |
| `USING` is a syntax error | F00 has no `USING ... ENDUSING` | qualify each field |
| `FILE ALREADY EXISTS` | a quoted name means create | `@DELETE-FILE` the outputs first |
| SLinit returns 20234 | reserved messages > `SLMaxSockets` | `SLMaxSockets = 10` with 6 messages |
| linker "Redefinition" lines | `NK-100-1BANK` loaded; SLIB already has NK | do not load it |
| a query sent in two TCP segments is never completed; the read times out | a non-blocking `SLrecv` loop that sleeps with `MN104`: SLIB takes in data only inside its own calls | blocking `SLrecv` plus the no-activity timer `SLiocSNOACT` (see the [Finger server](../../Case-Studies/Finger-Server.md)) |
| port never answers after a restart | an old `CLOSED` socket from an ESC-stopped run can hide the new listener | `kill <cid>` in TCPIP-MONITOR |
| TCPP prints `Invalid argument` / `Operation not supported on socket` on each connection from Windows, never from Linux | not your program: the card firmware's option parser, written for 1980s TCP, trips on the options a modern Windows sends | nothing to fix in your code; see [TCP-OPTION-PARSER.md](../../../Installation/Communication/TCP/RE/TCP-OPTION-PARSER.md#why-nd-never-saw-it-tcp-options-then-and-now) |

---

## 10. A server with no terminal: RT program or batch job

A server should not need somebody logged in. SINTRAN gives two ways to run one with no
terminal, and the monitor calls the program makes decide which one you can use.

| | RT program | batch job |
|---|---|---|
| Started by | `@RT <name>` | `@APPEND-BATCH <n> <file>:BATC <log>` |
| Runs as | an RT program, no user | a background program, logged in by the batch file |
| SLIB | works | works |
| Background-only monitor calls (TerminalStatus 330B, ExecuteCommand 317B, ...) | **the program is aborted** with `ERROR 15B` | work |
| `OUTPUT(1, ...)` goes to | the operator console | the batch log file |
| Holds | an RT description and a segment | a whole batch processor, for as long as it runs |
| Measured with | the Finger server loaded as `FINGERS` | the Finger server, `FINGERB:BATC` |

**Check every monitor call you use before you choose RT.** The page for each call in
ND-860228 has a line "All users | Background programs". A call marked background-only does
not return an error code to an RT program: SINTRAN aborts the program. See
[PLANC-RT-AND-REENTRANT-PROGRAMS.md section 5](PLANC-RT-AND-REENTRANT-PROGRAMS.md#5-traps-collected).

### 10.1 What was verified in RT

The Finger server was loaded as an RT program on the VSX/500 M reference machine on
2026-09-28. As RT it called SLinit, SLsocket, SLbind, SLlisten, SLaccept, SLrecv with the
no-activity timer, SLsend and SLclose, and answered the queries that need no session data.
Its lines came out on the console:

```
FINGER: listening on TCP port 79
FINGER: answered, query kind 2
FINGER: answered, query kind 1
ERROR   * 15B.0B * 1998-09-27 23:41:40 * FINGERS.66025B
```

The error line is the first query that called TerminalStatus. So **SLIB itself works in an
RT program**. A server that needs only SLIB and calls allowed for all users, such as the
[echo servers](../../Case-Studies/TCP-Echo-Server.md), can be RT. The echo servers have not
been run as RT programs; that is expected to work, not measured.

### 10.2 Building and loading one

Build it exactly as in section 7 first, and check the three things there. The `RT-LOADER`
then loads the same BRF files the linker loaded, in the same order: the program first, then
the libraries. This is the session that loaded FINGER, as the machine printed it:

```
@RT-LOADER
*NEW-SEGMENT 2540
RING: 2
SEGMENT TYPE:
PROTECTION BITS:
WP/NP:
*LOAD FINGER
LOAD-SEGMENT: 2540
LINKING-SEGMENT:

NO PRIORITY IN:  FINGERS
*LOAD (TCP-IP)SLIB-NRE-1B-B01
LOAD-SEGMENT: 2540
LINKING-SEGMENT:
*LOAD (TCP-IP)SLIB-REE-1B-B01
LOAD-SEGMENT: 2540
LINKING-SEGMENT:
*LOAD MON-CALL-1B-A00
LOAD-SEGMENT: 2540
LINKING-SEGMENT:
*LOAD PLANC-1BANK-F00
LOAD-SEGMENT: 2540
LINKING-SEGMENT:
*WRITE-REFERENCES
OUTPUT FILE:

*END-LOAD
*CHANGE-RT-DESCRIPTION
RT-PROGRAM: FINGERS
PRIORITY: 75
SEGMENT ONE: 2540
SEGMENT TWO:
START ADDRESS:
RING: 2
INITIAL PAGE TABLE:
ALTERNATIVE PAGE TABLE:
*EXIT-LOADER
@RT FINGERS
```

Notes, all from this session:

- **Pick a free segment on the day** with `LIST-FREE-SEGMENTS`. 2540 was free on this
  machine; it is not a constant.
- **The RT name is the `PROGRAM` unit cut to seven characters**: `PROGRAM : fingersrv`
  became `FINGERS`. `NO PRIORITY IN: FINGERS` after the first `LOAD` is how you learn it.
- **`MON-CALL-1B-A00` is only needed if the program uses `MONITOR_CALL`.** FINGER does. A
  program that uses only SLIB and the PLANC runtime routines leaves it out, as its linker
  MODE file would.
- **Do not load `NK-100-1BANK`**, the same as with the linker: SLIB already holds NK.
- **`WRITE-REFERENCES` must print nothing** before `END-LOAD`. Anything listed is
  unresolved.
- **`END-LOAD` comes before `CHANGE-RT-DESCRIPTION`**, and that command asks seven
  questions. Answer each one on the screen before typing the next command. See
  [PLANC-RT-AND-REENTRANT-PROGRAMS.md section 2.2](PLANC-RT-AND-REENTRANT-PROGRAMS.md#22-installing-it---verified-and-the-manuals-own-example-is-wrong).
- **Priority 75** copies `FSART`, the file server, as the RT guide recommends. It worked;
  no other value was tried.

### 10.3 Stopping, reloading and removing

```
@ABORT FINGERS                  stop it
```

To load a new build, run the same session on the next free segment. The first `LOAD` then
asks `FINGERS REPLACING?`; answer `YES`. Each of the three loads made this way printed
`FINGER: listening on TCP port 79` again after `@RT FINGERS`.

To take it out completely, as was done once RT proved impossible for FINGER:

```
@ABORT FINGERS
@RT-LOADER
*DELETE-PROGRAM FINGERS
*CLEAR-SEGMENT 2540
*CLEAR-SEGMENT 2541
*CLEAR-SEGMENT 2542
*EXIT-LOADER
@LIST-RT-DESCRIPTION FINGERS
ILLEGAL PARAMETER                (it is gone)
```

Clear every segment you loaded it onto, not just the last one.

### 10.4 Two things any server started without a person needs

- **Wait for TCP/IP.** Started early at boot, SLinit returns 20229 (`SLEconstart`, no contact
  with the packet level) because the TCP start has not finished. Retry SLinit instead of
  ending: FINGER tries every 10 seconds for up to 10 minutes with `MN104(10, 2)`.
- **Somewhere to write.** An RT program's `OUTPUT(1, ...)` goes to the console. A batch job's
  goes to its log file, and that file must be created with size 0 so it can grow:
  `@CREATE-FILE NAME-LOG:SYMB,0`. Created with size 1 it fills after one 2048-byte page and
  the batch job ends.

Starting an RT server at boot (`@RT <name>` in `LOAD-MODE:BATC`) has not been tested here.
Starting a batch-job server at boot has; see the
[Finger server case study, section 7](../../Case-Studies/Finger-Server.md#7-why-it-is-not-an-rt-program-and-what-to-use-instead).
