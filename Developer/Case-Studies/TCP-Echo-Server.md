# Case Study: TCP and UDP Echo Servers on SINTRAN III

This case study has three small servers that do the same job. Each one sends back every byte
it receives on port 7, the echo service. Together they show how to use ND's socket
library, SLIB, from PLANC and from MAC.

| Program | Language | Protocol | Files |
|---|---|---|---|
| `ECHOPL` | PLANC | TCP | [`ECHOPL.PLNC`](TCP-Echo-Server/ECHOPL.PLNC), [`ECHOPL.MODE`](TCP-Echo-Server/ECHOPL.MODE) |
| `ECHOUD` | PLANC | UDP | [`ECHOUD.PLNC`](TCP-Echo-Server/ECHOUD.PLNC), [`ECHOUD.MODE`](TCP-Echo-Server/ECHOUD.MODE) |
| `ECHOMA` | MAC, with a PLANC shim | TCP | [`ECHOMA.MAC`](TCP-Echo-Server/ECHOMA.MAC), [`ECHOSH.PLNC`](TCP-Echo-Server/ECHOSH.PLNC), [`ECHOMA.MODE`](TCP-Echo-Server/ECHOMA.MODE) |

All three include [`SLIBF00.DEFS`](TCP-Echo-Server/SLIBF00.DEFS), which is ND's `SLIB:DEFS`
with one word removed for the PLANC-100-F00 compiler.

**Ties together:**

- [SLIB API reference](../Languages/Application/SLIB-API-REFERENCE.md): the calls, records and status codes.
- [TCP and UDP programs in PLANC](../Languages/Application/PLANC-TCP-UDP-SOCKETS.md): how to write and build one.
- [MAC Cookbook section 11](../Languages/System/MAC-COOKBOOK.md#11-tcp-and-udp-from-mac-through-a-planc-shim): calling SLIB from MAC.
- [Running COSMOS TCP/IP on RetroCore](../../Installation/Communication/TCP/RUNNING-TCPIP-ON-RETROCORE.md): the network underneath.

---

## 1. What was verified

Built and run on SINTRAN III VSX/500 M under RetroCore, with COSMOS TCP/IP D02, SLIB B01,
PLANC-100-F00 and BRF-LINKER-C01. The ND was at 192.168.199.40, and each test ran from the
Windows host at 192.168.199.1 over the loopback adapter.

| Server | Test | Result |
|---|---|---|
| ECHOPL | 14, 200 and 768 bytes on one connection, then a second connection | every byte came back; both connections logged with the client's address and port |
| ECHOUD | datagrams of 16, 200 and 512 bytes | every datagram came back from 192.168.199.40 port 7; each logged with its sender |
| ECHOMA | 14, 200 and 768 bytes, twice, on two connections | every byte came back; both connections opened and closed cleanly |

The 768-byte message is larger than the 512-byte receive buffer, so it arrives in more
than one `SLrecv`. It also carries every byte value 0-255.

What the terminal shows for the MAC server:

```
@ECHOMA
ECHOMA: STARTING
ECHOMA: LISTENING ON TCP PORT 7
ECHOMA: CONNECTION
ECHOMA: CONNECTION CLOSED
```

And for the UDP server:

```
@ECHOUD
ECHOUD: listening on UDP port 7
ECHOUD: 16 bytes from 192.168.199.1 port 65116
ECHOUD: 200 bytes from 192.168.199.1 port 65116
ECHOUD: 512 bytes from 192.168.199.1 port 65116
```

ESC stops any of them.

---

## 2. Running them yourself

1. Get TCP/IP running and reachable. See
   [RUNNING-TCPIP-ON-RETROCORE.md](../../Installation/Communication/TCP/RUNNING-TCPIP-ON-RETROCORE.md).
2. Copy the files in [`TCP-Echo-Server/`](TCP-Echo-Server/) to the pack in binary mode, for
   example by FTP as user `SYSTEM`. The folder's [README](TCP-Echo-Server/README.md) lists
   the name and format each file needs on the pack.
3. Build the server you want with `@MODE ECHOPL:MODE,,`, `@MODE ECHOUD:MODE,,` or
   `@MODE ECHOMA:MODE,,`. Each MODE file deletes its old outputs first, so it can run
   again. On the very first run those deletes answer `NO SUCH FILE NAME`, which is harmless.
4. Check that the build reports `0 DIAGNOSTICS` and that `LIST-ENTRIES-UNDEFINED` printed
   nothing.
5. Start it with `@ECHOPL`, `@ECHOUD` or `@ECHOMA`, and connect from another machine:
   `telnet 192.168.199.40 7` for TCP, or any small UDP client.

---

## 3. The decisions, and why

**Why port 7 and an echo.** Echo is the smallest server that exercises the whole path:
listen, accept, receive, send, close, and accept again. The client can check every byte.

**Why the PLANC version is modelled on ND's TCCOM.** ND's own SLIB program `TCCOM:SYMB`
(user `TCP-COMM` in the D02 kit) is the only complete SLIB program ND shipped. Following
it settled the questions the manual leaves open:

- how to fill `SLmaxima`;
- that both library halves are loaded;
- that accepted sockets are set to blocking mode.

Two things TCCOM does could not be copied, because PLANC-100-F00 does not know them:

- It uses `USING ... ENDUSING`. The samples write each record field out in full instead.
- ND's `SLIB:DEFS` uses the word `UNSIGNED`. The samples include a local copy without it.

**Why the MAC version needs a PLANC shim.** SLIB is a PLANC library. Its calls take PLANC
records and PLANC `BYTE POINTER`s, and nothing in ND's documentation says how a MAC
program should build those. The FORTRAN calling sequence *is* documented, and a PLANC
`STANDARD` routine uses it. So `ECHOSH.PLNC` has six small STANDARD routines, one per
socket step, and `ECHOMA.MAC` calls them with `JPL`. The shim keeps the data buffer, so
MAC only passes socket numbers and byte counts. The details are in
[MAC Cookbook section 11](../Languages/System/MAC-COOKBOOK.md#11-tcp-and-udp-from-mac-through-a-planc-shim).

**Why the UDP server has no accept loop.** A datagram socket is never connected. Each
`SLrecvFrom` returns the sender's address and port, and `SLsendTo` sends the reply back to that
same address. One socket serves every client.

---

## 4. What went wrong on the way

Each of these stopped a build or a run once. They are in the order they were met.

| Symptom | Cause | Fix |
|---|---|---|
| the compile stops inside `SLIB:DEFS` | PLANC-100-F00 does not know `UNSIGNED` | `SLIBF00.DEFS` |
| `USING` is a syntax error | not in PLANC-100-F00 | write out each field in full |
| `FILE ALREADY EXISTS` from the compiler or the linker | a quoted file name means *create* | the MODE files delete old outputs first |
| `SLinit status 20234` | 6 messages reserved, but `SLMaxSockets` was 4 | `SLMaxSockets = 10` |
| linter reported dozens of undeclared names | the linter could not read `(TCP-IP)` includes | `planc-lint.py --include-dir` |
| `@MAC` printed nothing and ignored every line | the reentrant MAC on this pack was dumped with start address 0 | start MAC from `MAC-1415C:BPUN` at 177777 (the MODE file does) |
| `MODE` command did nothing | typed `@MODE` after the `@` prompt, so SINTRAN saw `@@MODE` | type `MODE ...` at the prompt |

---

## 5. Not covered yet

- **A TCP client.** No program here calls `SLconnect`. The PLANC guide shows the shape
  from ND's manual, and it has not been run.
- **More than one client at a time.** Each TCP server serves one connection, then goes back
  to accept. A server for several clients needs `SLfork` or non-blocking sockets with
  `SLsleep`.
- **A UDP datagram larger than 512 bytes.** It would not fit the receive buffer. What SLIB
  does with the rest has not been tested.
