# SLIB API Reference - the SINTRAN socket library

**SLIB** is ND's socket library for TCP and UDP programs on SINTRAN III. It is product
ND-211566. It ships with the COSMOS TCP/IP gateway, and it is written for PLANC. This page
lists every call, record, constant and status code, taken from the two files ND ships:
`(TCP-IP)SLIB:IMPT` and `(TCP-IP)SLIB:DEFS`. The descriptions come from ND's manual,
[ND-860372 SINTRAN SLIB Programmer's Guide](../../../Reference-Manuals/ND-860372-1-EN.md).

Each call is marked with one of three labels:

- **Run** means it ran on SINTRAN III VSX/500 M with COSMOS TCP/IP D02 and SLIB B01, in one of the
  [echo servers](../../Case-Studies/TCP-Echo-Server.md).
- **Manual** means it comes from ND-860372 and has not yet run here.
- **Declared** means `SLIB:IMPT` declares it, but ND-860372 has no page for it.

How to write and build a program is in
[PLANC-TCP-UDP-SOCKETS.md](PLANC-TCP-UDP-SOCKETS.md). How to run the stack itself is in
[RUNNING-TCPIP-ON-RETROCORE.md](../../../Installation/Communication/TCP/RUNNING-TCPIP-ON-RETROCORE.md).

---

## 1. The files

All of them are under user `TCP-IP` on a pack with the D02 gateway installed. They are
also in this repository, in
[`Installation/Communication/TCP/x/D02-gateway-and-clients/TCP-IP/`](../../../Installation/Communication/TCP/x/).

| File | What it is |
|---|---|
| `SLIB:DEFS` | Types, constants, status codes, and the `SLSzWorkArea` calculation. `$INCLUDE` it. |
| `SLIB:IMPT` | The `IMPORT` declarations of every call. `$INCLUDE` it after `SLIB:DEFS`. |
| `SLIB-NRE-1B-B01:BRF` | Non-reentrant half of the library, 1-bank programs. |
| `SLIB-REE-1B-B01:BRF` | Reentrant half, 1-bank programs. Load both halves. |
| `SLIB-NRE-2B-B01:BRF`, `SLIB-REE-2B-B01:BRF` | The same for 2-bank programs. |

**`SLIB:DEFS` does not compile with PLANC-100-F00.** One line uses the word `UNSIGNED`,
and F00 is the newest ND-100 PLANC compiler in the archive. It stops at that line. The echo-server
folder holds [`SLIBF00.DEFS`](../../Case-Studies/TCP-Echo-Server/SLIBF00.DEFS). It is ND's file
with that one word removed, and its header says exactly what changed. Copy it to the pack as
`SLIBF00:DEFS` and include that instead. `SLIB:IMPT` compiles as ND ships it.

**Do not copy numbers out of the printed manual.** The manual describes SLIB A00, and the
pack has B01. B01 adds status codes 20254-20258 and has larger work areas.
`SLIB:DEFS` works out `SLSzWorkArea` for you.

---

## 2. Starting SLIB

### SLinit - Run

```
ROUTINE VOID, INTEGER (INTEGER ARRAY POINTER, SLmaxima, SLrvvp, INTEGER, INTEGER POINTER) : SLinit
SLinit(ADDR workArea, maxima, NIL, SLMainTaskStackSize, NIL) =: status
```

This must be the first SLIB call. The program supplies SLIB's work area, a module-level
`INTEGER ARRAY` of `SLSzWorkArea` words. SLIB keeps pointers into it for as long as the
program runs.

`SLSzWorkArea` is calculated inside `SLIB:DEFS` from five constants. **The program must
declare these five before it includes the file:**

```planc
CONSTANT SLMaxPorts = 1            % must be 1 (ND-860372 p.38)
CONSTANT SLMaxSockets = 10
CONSTANT SLMaxSLFork = 1
CONSTANT SLSubTaskStackSize = 1
CONSTANT SLMainTaskStackSize = 1
```

The `SLmaxima` record:

| Field | Type | Value used in the samples | Meaning |
|---|---|---|---|
| `max_nports` | INTEGER | `SLMaxPorts` | ports (TCP, UDP ...) |
| `max_nsockets` | INTEGER | `SLMaxSockets` | sockets |
| `max_debug` | BOOLEAN | `FALSE` | debug printing |
| `max_debfd` | INTEGER | `1` | file number for the debug printing |
| `max_AUserDatap` | INTEGER POINTER POINTER | `NIL` | address of a user data pointer |
| `max_nsallocmsg` | INTEGER | `6` | small messages reserved |
| `max_nballocmsg` | INTEGER | `0` | big messages reserved |
| `max_nxballocmsg` | INTEGER | `0` | huge messages reserved |
| `max_tcpdev` | INTEGER | `SLDominoPioc` | which TCP device, see below |

**`max_nsallocmsg + max_nballocmsg` must not be more than `max_nsockets`** (ND-860372 p.39).
Otherwise SLinit returns **20234 `SLEinval`**. This was measured: 4 sockets with 6 small
messages failed exactly that way, and 10 sockets work.

`max_tcpdev` picks the network controller:

| Constant | Value | Meaning |
|---|---|---|
| `SLDominoPioc` | -1 | Ethernet-III (DOMINO) first, then Ethernet II (PIOC). **Run.** |
| `SLPiocDomino` | -2 | Ethernet II first, then Ethernet-III |
| `SLDominoOnly` | -3 | Ethernet-III only |
| `SLPiocOnly` | -4 | Ethernet II only |
| `0`..`3` | | one Ethernet II controller by number (manual) |

### Tasks and sleeping

| Call | Declaration | Status |
|---|---|---|
| `SLfork` | `INTEGER (SLrvvp, INTEGER, INTEGER POINTER)` | Manual 7.7. Starts a subtask; limited by `SLMaxSLFork`. |
| `SLexit` | `VOID` | Manual 7.6. Ends the current task. |
| `SLsleep` | `VOID (INTEGER4 nsec, INTEGER4 eventMask, INTEGER4 WRITE actualEvents)` | Manual 7.23. Sleeps up to `nsec` seconds or until an event in the mask; `-1` = any event. `actualEvents` is 0 on a timeout. |
| `SLsleepShort` | `VOID (INTEGER4)` | Declared only. |
| `SLsetOwnEvent` | `VOID (INTEGER4)` | Manual 7.21. Wakes a task sleeping on its own events. |

---

## 3. Sockets

Every call below returns an INTEGER status: `SLEok` (0) or a code from section 6. Errors
come back as that number, never as a skip return, so compare with `SLEok`.

| Call | Declaration | Status | Notes |
|---|---|---|---|
| `SLsocket` | `INTEGER (INTEGER domain, INTEGER type, INTEGER protocol, SLsockid WRITE)` | **Run** (stream and datagram) | `domain` must be `AF_inet`, and `type` must be `SOCK_stream` (TCP) or `SOCK_dgram` (UDP). `protocol` 0 picks the default. The socket id is never 0. |
| `SLbind` | `INTEGER (SLsockid, SLsockaddr)` | **Run** | Pass an `SLin_sockaddr`. Address 0 (`in_l1 = 0`) means any local address. This was measured: the listener shows as `0.0.0.0 port 7` in `NETSTAT a` and takes connections. |
| `SLlisten` | `INTEGER (SLsockid, INTEGER backlog)` | **Run** with backlog 1 | TCP only. |
| `SLaccept` | `INTEGER (SLsockid, SLsockid WRITE, SLsockaddr)` | **Run** | Waits for a connection. It writes the peer's address and port into the third argument, although that argument is not declared `WRITE`. |
| `SLconnect` | `INTEGER (SLsockid, SLsockaddr)` | Manual 7.5 | TCP client side. |
| `SLsend` | `INTEGER (SLsockid, BYTE POINTER buf, INTEGER len, INTEGER flags, INTEGER WRITE sent)` | **Run** | Connected sockets only. `flags` must be 0. `sent` can be less than `len`, so loop until it is all sent. |
| `SLrecv` | `INTEGER (SLsockid, BYTE POINTER buf, INTEGER len, INTEGER flags, INTEGER WRITE got)` | **Run** | Connected sockets only. `flags` must be 0. **When the peer closes, it returns `SLEok` with `got` = 0** (manual and measured). A second read after that gives `SLEnotconn`. |
| `SLsendTo` | `INTEGER (SLsockid, BYTE POINTER, INTEGER, INTEGER, SLin_sockaddr POINTER to, INTEGER WRITE sent)` | **Run** | UDP. Pass `ADDR peer`. |
| `SLrecvFrom` | `INTEGER (SLsockid, BYTE POINTER, INTEGER, INTEGER, SLin_sockaddr POINTER from, INTEGER WRITE got)` | **Run** | UDP. Writes the sender's address and port into `from`, which may be `NIL`. |
| `SLsendV` | `INTEGER (SLsockid, Sliov POINTER, INTEGER, INTEGER WRITE)` | Declared | Gather-send from a list of buffers (record `sliov`). |
| `SLsense` | `INTEGER (SLsockid, INTEGER WRITE)` | Manual 7.19 | Checks the input queue. |
| `SLshutdown` | `INTEGER (SLsockid, INTEGER how)` | Manual 7.22 | Shuts down one direction. |
| `SLclose` | `INTEGER (SLsockid)` | **Run** | |
| `SLgetsockname` | `INTEGER (SLsockid, SLsockaddr WRITE)` | Manual 7.10 | |
| `SLgetpeername` | `INTEGER (SLsockid, SLsockaddr WRITE)` | Manual 7.9 | |
| `SLgetOption` | `INTEGER (SLsockid, INTEGER level, INTEGER WRITE, BYTE POINTER, INTEGER)` | Manual 7.8 | |
| `SLsetOption` | `INTEGER (SLsockid, INTEGER level, INTEGER opt, BYTE POINTER, INTEGER)` | Manual 7.20 | Level `sol_socket` (-1); options in section 5. |
| `SLioctl` | `INTEGER (SLsockid, INTEGER request, SLiocArg POINTER, INTEGER size)` | **Run** (`SLiocNBIO`) | Requests in section 5. |

**ND-100 rule for receive buffers.** On the ND-100 the buffer given to `SLrecv` must start on
a word boundary (ND-860372 7.15). `ADDR ( buf ( 0 ) )` of a module-level `BYTES` array does.

**Blocking.** ND's own server, TCCOM, sets each accepted socket to blocking mode with
`SLioctl(sock, SLiocNBIO, ADDR arg, SIZE(arg))` and `arg.SLiocNumber = 0`. The samples do the same.
An `SLaccept` on a listener that is not blocking returns 20253 `SLEwouldblock` when no
client is waiting.

**Do not poll with a SINTRAN sleep.** SLIB takes in new data only inside its own calls. A
non-blocking `SLrecv` loop that sleeps with SuspendProgram (`MN104`) between tries got the
first segment of a query and never the second, although the card had acknowledged it.
Measured with Windows `finger.exe`, which sends a name and its CR LF separately. For a
read with a timeout, use a blocking `SLrecv` and the no-activity timer (`SLiocSNOACT`,
section 5); the [Finger server](../../Case-Studies/Finger-Server.md) does this.

---

## 4. Names, addresses and byte order

| Call | Declaration | Status |
|---|---|---|
| `SLhtonl`, `SLntohl` | `INTEGER4 (INTEGER4)` | Declared. The ND-100 is big-endian, so network order is its own order. Port 7 was stored straight into `sin_port` and worked. |
| `SLhtons`, `SLntohs` | `INTEGER2 (INTEGER2)` | Declared; as above. |
| `SLinNetAddr` | `INTEGER (BYTES, SLinaddr WRITE)` | Manual ch. 9. Turns dotted text into an address. It is imported under the name `SLINNETADD`. |
| `SLgHbyName`, `getHbyName` | `SLhostent POINTER (BYTES)` | Manual ch. 8. Looks a host up by name in `AIP-HOSTS`. ND's TCCOM uses this to bind to its own address. |
| `SLgHbyAddr`, `getHbyAddr` | `SLhostent POINTER (SLinaddr)` | Manual ch. 8. |
| `SLgetHent`, `SLsetHent`, `SLendHent` | | Manual ch. 8. Walk the hosts file. |
| `SLgetNent`, `SLsetNent`, `SLendNent`, `SLgNbyName`, `SLgNbyAddr` | | Manual ch. 8. The networks file. |
| `SLgPent`, `SLsetPent`, `SLendPent`, `SLgPbyName`, `SLgPbNumber` | | Manual ch. 8. The protocols file. |
| `SLgetSent`, `SLsetSent`, `SLendSent`, `SLgSbyName`, `SLgSbyPort` | | Manual ch. 8. The services file. |

### The address records (`SLIB:DEFS`)

```planc
TYPE SLinaddr = RECORD PACKED            % an internet address
   SLu_char : in_b1, in_b2, in_b3, in_b4 % the four bytes, in_b1 first: 192.168.199.40
   SLu_short: in_w1 = in_b1
   SLu_short: in_w2 = in_b3
   SLu_long : in_l1 = in_b1              % all four bytes as one number; 0 = any address
ENDRECORD

TYPE SLsockaddr = RECORD                 % the general part
   SLu_short:  sa_family MOD 2           % AF_inet
ENDRECORD

TYPE SLin_sockaddr = SLsockaddr RECORD   % an internet socket address
   SLu_short: sin_port  MOD 2            % port number
   SLinaddr : sin_addr  MOD 2
ENDRECORD
```

`SLsockid` is an `INTEGER`. Declare an `SLin_sockaddr` and pass it wherever a call wants an
`SLsockaddr`, because the record extends it.

---

## 5. Constants

**Address families.** Only `AF_inet` = 2 is implemented (ND-860372 7.24). `SLIB:DEFS` also
defines `AF_unspec` 0 to `AF_max` 15.

**Socket types.** `SOCK_stream` = 1 (TCP) and `SOCK_dgram` = 2 (UDP) are the two the manual
allows. `SOCK_raw` 3, `SOCK_rdm` 4 and `SOCK_seqpacket` 5 are defined but not supported.

**Socket options** (`SLsetOption`, level `sol_socket` = -1):

| Constant | Value | Meaning |
|---|---|---|
| `SO_debug` | 1 | record debug information |
| `SO_reuseaddr` | 4 | allow reuse of a local address |
| `SO_keepalive` | 8 | keep connections alive |
| `SO_linger` | 64 | wait on close while data is queued |
| `SO_dontlinger` | 128 | the opposite of `SO_linger` |

**`SLioctl` requests**, and the record each one takes:

| Constant | Value | What it does | Record |
|---|---|---|---|
| `SLiocNBIO` | 1 | non-blocking on (1) or off (0). **Run.** | `SLiocINT` (`SLiocNumber`, INTEGER4) |
| `SLiocSNOACT`, `SLiocGNOACT` | 2, 3 | set / get the no-activity timer. **SNOACT run**: seconds in bits 31-16, bit 1 = signal the application, bit 0 = signal the peer; with bit 1 a blocking `SLrecv` returns 20249 SLEtimedout after that many idle seconds. ND's default is 600 s with bit 0 | `SLiocINT` |
| `SLiocSOEV` | 4 | set event bits for the socket (used with `SLsleep`) | `SLiocINT` |
| `SLiocSSEV` | 5 | set a routine to call on an event | `SLiocRout` |
| `SLiocGActConn` | 6 | active connections | `SLiocActConn` |
| `SLiocGMbStat` | 7 | buffer statistics | `SLiocMbStat` |
| `SLiocGNetwork` | 8 | network statistics | `SLiocNetwork` |
| `SLiocGArpTable` | 9 | the ARP table | `SLiocArpTable` |
| `SLiocGHwStat` | 10 | hardware statistics | `SLiocLNMAST` |
| `SLiocGGenInfo` | 11 | generation information | `SLiocGenInfo` |
| `SLiocGLoad` | 12 | load information | |
| `SLiocSAipAddr` | 13 | set the IP address | |
| `SLiocKill` | 14 | kill a connection (what the monitor's `KILL` does) | |
| `SLiocGTimers` | 15 | timer information | `SLiocTimers` |
| `SLiocDIEV` | 16 | stop SLIB waiting for these events | |
| `SLiocSndQue` | 17 | send-queue information | `SLiocTSndQue` |
| `SLiocSdelResp` | 18 | delay the send response (DOMINO/PIOC only) | |
| `SLiocAroute`, `SLiocDroute` | 19, 20 | add / delete a route | `SLiocRoute` |
| `SLiocAx25`, `SLiocDx25`, `SLiocGx25` | 21-23 | X.25 address mapping and statistics | `SLiocX25` |

TCPIP-MONITOR is ND's own program built on these requests; its `NETSTAT`, `ARP` and `KILL`
commands show what they return. ND-860372 chapter 4.5 describes the records.

---

## 6. Status codes

`SLEok` = `SLEnoerror` = 0. The error codes are decimal 20225-20258.

| Code | Name | Meaning (ND's comment in `SLIB:DEFS`) |
|---|---|---|
| 20225 | `SLEwksz` | work size error |
| 20226 | `SLEptr` | pointer error |
| 20227 | `SLEilsid` | illegal socket id |
| 20228 | `SLElostPL` | lost contact with the packet level |
| 20229 | `SLEconstart` | error when making contact with the packet level |
| 20230 | `SLEnospace` | no more space |
| 20231 | `SLEnospinmsg` | too little space in message |
| 20232 | `SLEslibfatal` | fatal internal SLIB error |
| 20233 | `SLEtryagain` | used between SLIB and the protocols |
| 20234 | `SLEinval` | argument invalid. **Seen** from SLinit when the reserved messages were more than `max_nsockets`. |
| 20235 | `SLEprototype` | protocol wrong type for socket |
| 20236 | `SLEnoprotoopt` | bad protocol option |
| 20237 | `SLEprotonosupport` | protocol not supported |
| 20238 | `SLEsocktnosupport` | socket type not supported |
| 20239 | `SLEaddrinuse` | address already in use |
| 20240 | `SLEaddrnotavail` | cannot assign requested address |
| 20241 | `SLEnetdown` | network is down |
| 20242 | `SLEnetunreach` | network is unreachable |
| 20243 | `SLEnetreset` | network dropped connection on reset |
| 20244 | `SLEconnaborted` | software caused connection abort |
| 20245 | `SLEconnreset` | connection reset by peer |
| 20246 | `SLEisconn` | socket is already connected |
| 20247 | `SLEnotconn` | socket is not connected |
| 20248 | `SLEshutdown` | cannot send after shutdown |
| 20249 | `SLEtimedout` | connection timed out |
| 20250 | `SLEconnrefused` | connection refused |
| 20251 | `SLEnobufs` | no buffer space available |
| 20252 | `SLEunexpected` | unexpected subsystem error |
| 20253 | `SLEwouldblock` | the call would have blocked |
| 20254 | `SLEhostnotfound` | name lookup: host not found (B01 only) |
| 20255 | `SLErestryagain` | name lookup: try again (B01 only) |
| 20256 | `SLEnodata` | name lookup: no data (B01 only) |
| 20257 | `SLEnorecovery` | name lookup: no recovery (B01 only) |
| 20258 | `SLEnoaddress` | name lookup: no address (B01 only) |

ND-860284 *COSMOS TELNET-FTP Client User Guide*, appendix D, explains 20225-20253 with an
operator action for each.

---

## 7. Linking

Load order for a 1-bank PLANC program, as used by every sample. The order was measured,
and `LIST-ENTRIES-UNDEFINED` prints nothing after it:

```
@BRF-LINKER-C01
PROGRAM-FILE "NAME"
LOAD NAME
LIBRARY-MODE ON
LOAD (TCP-IP)SLIB-NRE-1B-B01
LOAD (TCP-IP)SLIB-REE-1B-B01
LOAD MON-CALL-1B-A00
LOAD PLANC-1BANK-F00
LIST-ENTRIES-UNDEFINED
EXIT
```

ND-860372 section 2 also lists `NK-100-1BANK` and `PLANC-UTILLIB-1B`. Neither is needed:

- `SLIB` already contains the NK routines, so loading `NK-100-1BANK` only prints
  "Redefinition" lines.
- Nothing is left undefined without `PLANC-UTILLIB-1B`, and no copy of it is known to exist.
