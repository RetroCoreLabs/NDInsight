# Running COSMOS TCP/IP on a RetroCore ND-100

How to run ND's COSMOS TCP/IP gateway on an emulated ND-100 in RetroCore, reach it from the
Windows host with ping, telnet and FTP, and check what the stack is doing. Writing your own
TCP and UDP programs is covered in the developer pages listed in section 12.

**Reference machine.** Everything below was seen on one machine, and the examples use its
numbers. Where something is inferred rather than seen, it says so.

| | |
|---|---|
| System | SINTRAN III VSX/500 M. Boot banner `SINTRAN III - VSX/500 M`, `REVISION (PATCH FILE NO.): 3200B`, CPU type 110, CPU number 210 |
| Pack | one Winchester image attached as `wd0`, volume `PACK-ONE` |
| Terminals | TCP port **9210** (TERM 8, 9, 10). Debugger (DAP) on port **4299** |
| Login | user `SYSTEM`, blank password |
| Network | the ND is **192.168.199.40**, gateway **192.168.199.1**, on a private segment shared with the Windows host through the Microsoft KM-TEST Loopback Adapter (`ND-Loopback`, 192.168.199.1/24) |

**Products on the pack:**

| Product | Version | Prints itself as |
|---|---|---|
| COSMOS TCP/IP Gateway for Ethernet II | ND-211185 D02 | `COSMOS TCP/IP Gateway for Ethernet II ND-211185D02 January 20, 1992` |
| FTP server component | ND-211185 C07 | `FTP-SERVER ND-211185C07 February 7, 1990` |
| Telnet/FTP/RSH clients | ND-211154 D01 | |
| TCPIP-MONITOR | D00 | `TCPIP-MONIT-100 version D00 of October 22, 1991` |
| Socket library SLIB | ND-211566 B01 | |
| TADADM | Version M, Revision 00 | `TADADM  Version - M , Revision: 00.` |

The D02 files themselves are in [`x/D02-gateway-and-clients/`](x/), and
[`COPYING-FILES-TO-SINTRAN.md`](COPYING-FILES-TO-SINTRAN.md) says how to get them onto a pack.

---

## 1. What the reference machine is

A SINTRAN III VSX/500 M system running in RetroCore. It has one emulated ND Ethernet II
controller (ND-110063, PCB 3094) at thumbwheel 0. The card runs the real ENCOS/TCP 68000
firmware on an emulated 68000 with its own 512 KB DRAM bank. The COSMOS TCP/IP Gateway
(TCPP) drives that card and gives the machine:

* a TELNET server on port 23 (TCPP),
* an FTP server on port 21 (FTPRT),
* telnet, FTP and rsh clients you can run from a SINTRAN terminal,
* a socket library (SLIB) for your own TCP and UDP programs,
* a diagnostic shell, TCPIP-MONITOR.

TCP/IP starts by itself at every boot. Nothing has to be typed to bring the network up.

The card's MAC address is `08:00:26:` + the ND system number (byte-reversed) + physical
user; on this machine it is `08:00:26:d2:00:00`. It follows from the CPU number (210), so
two packs with different CPU numbers get different MACs automatically.

---

## 2. Windows prerequisites

Three things must be true on the Windows host: npcap is installed, the loopback adapter
exists with the right address, and `RetroCore.ini` bridges the card to that adapter.

### 2.1 npcap

RetroCore bridges the emulated card onto a host adapter with the **npcap** packet driver,
through the SharpPcap 6.3.1 library, which loads npcap's `wpcap.dll` from the Npcap folder
under the Windows system directory.

* Install from <https://npcap.com/> (free for personal use). No reboot is normally needed,
  but RetroCore must be started after the install.
* The host runs npcap 1.10.4, service `npcap` ("Npcap Packet Driver"). Whether the
  installer's "WinPcap API-compatible mode" option matters to SharpPcap is not verified;
  the install works as it is.
* Wireshark installs npcap too. If Wireshark can capture on an adapter, RetroCore can
  bridge to it.
* Without npcap: `net list` prints `No host network interfaces found (is Npcap installed?)`,
  `net attach` warns `backend failed to start - check npcap installation`, and a
  `--net=pcap:` ini line adds the card with no network. SINTRAN then sees a card that never
  reaches anything.

The other `--net=` forms (udp, tcp, listen; see section 8) need nothing extra.

### 2.2 The loopback adapter

Npcap injects the ND's frames on an adapter's *send* path, and the host's own IP stack never
receives a frame that npcap injected. So on a physical NIC, a Hyper-V vEthernet or a
VirtualBox host-only adapter, the PC that runs RetroCore can never reach the ND. Wi-Fi does
not work with pcap injection at all.

The **Microsoft KM-TEST Loopback Adapter** is a software NIC shipped with Windows that hands
everything sent on it straight back up as received. A frame npcap injects on it arrives in
the host's IP stack, and a frame the host sends on it is captured by npcap and reaches the
card. The adapter gives a direct connection between the host and the ND and nothing else:
there is no DHCP, so both sides get fixed addresses by hand.

The price: the ND sits on a private segment with the host only. Other machines on the LAN do
not see it unless Internet Connection Sharing is added (section 7.3).

**Install the adapter** (as administrator):

1. Run `hdwwiz.exe`. Next, "Install the hardware that I manually select from a list
   (Advanced)", Network adapters, manufacturer Microsoft, "Microsoft KM-TEST Loopback
   Adapter", Next, Finish. The driver (`netloop.inf`) ships with Windows; nothing is
   downloaded. It appears as "Ethernet N" (here "Ethernet 7", interface index 97).
2. Rename it `ND-Loopback`, give it the static address 192.168.199.1/24, no gateway, DHCP
   off, and disable the IPv6 binding (the ND stack is IPv4 only; IPv6 chatter would only
   show up as noise in the card's receive counters). In an elevated PowerShell, with the
   index from `Get-NetAdapter`:

   ```powershell
   Rename-NetAdapter -Name 'Ethernet 7' -NewName 'ND-Loopback'
   Set-NetIPInterface -InterfaceIndex 97 -Dhcp Disabled
   New-NetIPAddress   -InterfaceIndex 97 -IPAddress 192.168.199.1 -PrefixLength 24
   Disable-NetAdapterBinding -Name 'ND-Loopback' -ComponentID ms_tcpip6
   ```

3. Check: `Get-NetIPAddress -InterfaceAlias ND-Loopback` shows 192.168.199.1/24 and the
   adapter status is Up.
4. Get the adapter GUID for the ini file:
   `Get-NetAdapter ND-Loopback | Select InterfaceGuid`.

**Choosing the addresses.** Pick a /24 that nothing else on the PC uses
(`Get-NetIPAddress -AddressFamily IPv4` lists what is taken; 192.168.199.0/24 is free here).
Keep it a 192.168.x.0/24: with "Subnet bits 0" in AIP-CONFIG the ND assumes the class C
mask, and a 10.x or 172.16.x address would make it assume /8 or /16 instead (see
section 6.2). The host address must be inside that /24 and must not be the ND's.

**Windows firewall.** The new adapter comes up as a "Public" network. Outbound ping, telnet
and FTP from the host are allowed by default; only inbound to the host is filtered, and the
ND initiates nothing towards the host in normal use.

### 2.3 RetroCore.ini

The card line is

```
device add ETH 0 --net=pcap:GUID-OF-ND-LOOPBACK
```

The token is the adapter's Windows interface GUID; `GUID-OF-ND-LOOPBACK` stands for
the one Windows gave your loopback adapter (section 2.2 shows how to read it). RetroCore matches the token as a
case-insensitive substring of the npcap device name `\Device\NPF_{GUID}` or of the
description npcap reports, and the GUID is in the name whatever the adapter is called.
`--net=pcap:KM-TEST` also works (`net status` then reports
`Network: ATTACHED - pcap:Microsoft KM-TEST Loopback Adapter`; the description RetroCore
sees is the driver name even though `tshark -D` shows the Windows name `ND-Loopback`).
The GUID is used because it cannot be confused with any other adapter.

**Only one `device add ETH <n>` line per card number may be active.** Two cards at the same
thumbwheel collide at device 140360 and SINTRAN reports *"No answer from interface"*. If a
bare `device add ETH 0` line exists, it must be commented out.

### 2.4 The RetroCore.exe build

RetroCore must be a build that pads short received frames (any build from 2026-09-27 on). The
loopback adapter hands over frames as the host stack built them: an ARP reply is 42 bytes.
A real Ethernet MAC pads every frame to 60 bytes, and the TCP/IP firmware on the card
discards anything shorter, so without the padding the ND never learns the host's MAC and
nothing works. The build you need pads any received frame shorter than 60 bytes with zeros
to 60, and `net status` prints `padded to 60 bytes: N short frames` once it has happened.

---

## 3. Starting the machine and logging in

Start RetroCore with the machine's `RetroCore.ini`. The pack boots SINTRAN and the initial commands start
TCP/IP. Connect a terminal to TCP port 9210 (TERM 8, 9 or 10). On a fresh connection send
ESC first, then log in:

```
ENTER SYSTEM
PASSWORD:            (just press return)
```

### 3.1 What the boot does

`@LIST-INITIAL-COMMANDS` shows:

```
ENTER-DIRECTORY PACK-ONE DISC-74MB-1 0
SET-ERROR-DEVICE 1
BATCH
APPEND-BATCH 1 (SYSTEM)LOAD-MODE:BATC SYSTEM-OUTPUT-1
```

and `(SYSTEM)LOAD-MODE:BATC` is:

```
@ENTER SYSTEM,,,
@CC ***  WARM START  ***
@SET-UNAVAILABLE $'THE COMPUTER IS BEING WARM-STARTED$'
@CC
@CC Loading TCP-IP
@CC
@SINTRAN
@START-XMSG
@EX
@HOLD 0 0
@HOLD 3 2
@START-TADADM
@MODE (TCP-IP)TCP-START-D02:MODE,,
@SET-AVAILABLE
```

A good boot ends on the console with:

```
COSMOS TCP/IP Gateway for Ethernet II ND-211185D02 January 20, 1992
Starting Ethernet II number 0
TELNET and TCP/IP in Ethernet II with Internet address 192.168.199.40 started
<date time> FTPRT started.- FTP-SERVER ND-211185C07 February 7, 1990 -
```

The `Internet address 192.168.199.40` line proves which AIP-CONFIG line the stack read.

### 3.2 Two rules for that batch file

* **Inside `@SINTRAN` (the service program) the commands carry the `@`:** `@START-XMSG`,
  `@EX`. A bare `START-XMSG` in a mode or batch file halts SINTRAN with
  `Sintran halt in ERRFATAL. L-reg: 072013`. Typed by hand at the `*` prompt the same
  command works, which is what makes this hard to spot.
* **The file must be written with even parity** (ndtool `-p`). Every genuine ND text file
  on the pack has bit 7 set on most bytes; a plain 7-bit copy is not the same file to
  SINTRAN. The same applies to AIP-CONFIG and AIP-HOSTS when you edit them off the machine.

### 3.3 Starting TCP/IP by hand

For a restart, or on a pack without the initial commands:

```
@SINTRAN-SERVICE-PROGRAM
START-XMSG
EXIT
@START-TADADM
@MODE (TCP-IP)TCP-START-D02:MODE,,
@SET-AVAILABLE
```

If XMSG is already up, `START-XMSG` answers
`ERROR: XMSG is already running: Use STOP-XMSG to stop it!`. That is fine; carry on with
`START-TADADM`.

### 3.4 Why that order

Each step depends on the one ahead of it:

* **XMSG first.** TADADM talks over XMSG. Out of order, `@START-TADADM` answers:
  ```
  ---- NOT POSSIBLE ---
  Error in accessing X-message, Xmsg error no:  41045
  Operation was: Request privilege.
  ```
* **A HOLD after START-XMSG.** ND-60.134.2 section 4.9.4: XROUT still has to fix its
  segment after `OK:` is printed, so a startup file must wait a moment. The batch file
  holds 3 seconds.
* **TADADM ahead of the servers.** TADADM hands out the TADs that FTP and TELNET sessions
  run in. Start TCPP/FTPRT first and they come up `PASSIVE` holding no device, and every
  login dies with `TADADM has not been started.`
* `TCP-START-D02:MODE` says so itself in its header: *"RUN THIS MODE FILE DURING WARM
  START, ANYTIME AFTER X-MESSAGE AND TADADM ARE RUNNING."*

### 3.5 What TCP-START does

```
@ABORT ftprt
@ABORT tcpp
@(TCP-IP)PO-STOP-D02 0          stop and unload Ethernet controller 0
@RT TCPP                        TELNET + TCP/IP
@RT FTPRT                       FTP server
```

It is safe to run again at any time. It aborts the servers first, so it doubles as a
restart and as the way to pick up a changed AIP-CONFIG.

---

## 4. What runs and how to check it

### 4.1 TCPP holds the Ethernet card

```
@LIST-RT-DESCRIPTION TCPP
```

The line that matters is at the bottom:

```
RESERVED   DATAFIELDS  LOGICAL UNIT        FIRST WAITING
              104262B    2240B  INPUT
```

**`LOGICAL UNIT 2240B`** is Ethernet controller 0. Without it TCPP never got the card and
nothing will answer. CPU time climbs as traffic arrives. A healthy TCPP sits in a timer
wait holding unit 2240B; a healthy FTPRT is passive in its 60-minute timer wait
(`@LIST-RT-DESCRIPTION FTPRT`).

### 4.2 TADADM is handing out TADs

```
@TAD
```

```
       TADADM  Version - M , Revision: 00.
TAD/TYP RESERV ESCAP PORTNO - PORTNO TERMNO USER             SYSTEM
768/255  BAK04 Enab       8 -      6        FTP-Server-C07   <local>
769/  0  No    Enab  Discon -
   ... 770..777 free ...
```

Ten TADs, `768` taken by the FTP server. If `@TAD` says `TADADM has not been started`, do
`@START-TADADM`.

### 4.3 TCPIP-MONITOR quick check

```
@(TCP-IP)TCPIP-MONITOR
TCPIP-MONIT-100 version D00 of October 22, 1991
Slib:netstat a
 TCPIP-MONITOR connected to tcpdev=0
Prot   Rcv-Q-Snd   Cid   Local address  port  Foreign address  port  State
 TCP     0     0     1 192.168.199. 40    23    0.  0.  0.  0     0 LISTEN
 TCP     0     0     2   0.  0.  0.  0    21    0.  0.  0.  0     0 LISTEN
Slib:exit
```

A listener on port 23 (telnet, TCPP) and one on port 21 (FTP, FTPRT) means both servers are
up. `netstat a` is also the quickest way to tell "nobody is listening" from "connected but
the server is not reading". Full reference in section 9.

---

## 5. Connecting from the Windows host

### 5.1 The three tests

From this PC:

```
ping 192.168.199.40
telnet 192.168.199.40
ftp 192.168.199.40        (user SYSTEM, blank password)
```

A good ping answers `Reply from 192.168.199.40: bytes=32 time=91ms TTL=15`. Telnet gives the
SINTRAN login (`ENTER`); log in as `SYSTEM` with a blank password. FTP logs in as `SYSTEM`
with a blank password and gives the FTP prompt; transfer `:PROG`, `:BPUN`, `:ERR` and other
binary files in binary mode.

The ND cannot connect to **its own** address (`connection timed out`): the frame goes out
addressed to the card's own MAC and never comes back. Test from the host or another machine.

### 5.2 What a good session looks like on the wire

At the RetroCore debugger prompt, `net status` shows the backend attached to the loopback
adapter with both TX and RX counters moving, and `net dump 10` shows the host's ARP request
and the ND's reply. From the host side the same exchange is visible with Wireshark on
`ND-Loopback`, or without clicking:

```
tshark -i "\Device\NPF_{GUID-OF-ND-LOOPBACK}" -a duration:12 -w ndloop.pcapng
ping 192.168.199.40            (in another window while it captures)
tshark -r ndloop.pcapng -Y "arp or icmp"
```

The chain to expect: host ARP request (42 bytes, source `02:00:4c:4f:4f:50`, the loopback
adapter's MAC) -> ND ARP reply `192.168.199.40 is at 08:00:26:d2:00:00` (60 bytes) -> echo
requests each answered with TTL 15. For telnet: TCP SYN to port 23, SYN/ACK from the ND
(MSS 1024, window 4096), telnet option negotiation (Will Echo, Binary Transmission), then
the login banner. `arp -a` on the host then shows 192.168.199.40 as `dynamic`.

`arp -d` needs an administrator prompt. Without it Windows keeps an `Incomplete` entry in
back-off for a while and sends no new request, so a capture can miss the ARP even when
everything is right. Wait a minute, or ping from an elevated prompt after `arp -d`.

### 5.3 If it does not answer

* `net status` RX stays at zero: the card sees nothing. Check the adapter is Up, that
  RetroCore logged `ETH 0 network: ...` naming the loopback adapter at start, and that
  npcap lists the adapter (`net list`).
* RX rises, `filtered(wrong MAC)` rises, `accepted` stays zero: frames arrive but not for
  the card's MAC. The host must ARP for 192.168.199.40; if `arp -a` shows a stale entry,
  `arp -d 192.168.199.40` from an elevated prompt.
* RX `accepted` rises, `TX` stays 0, and `net status` shows no `padded to 60 bytes` line:
  the exe is a build without the frame padding (section 2.4). The ND takes the ping in but
  never gets the host's 42-byte ARP reply, so it asks the same ARP question after every ping.
* RX accepted rises, no ping reply: read `net dump` for the ND's ARP reply and ICMP reply.
  If they are transmitted, the loopback path is not delivering them upward on this Windows
  build; report it with the dump.
* Port 21 answers with a TCP reset although the boot said `FTPRT started`: look for a stale
  `CLOSED` socket on port 21 in `netstat a` (section 9.3) and clear it.
* A telnet session that has been idle for about an hour can get a TCP reset from the ND on
  the next keystroke; the session is gone on the ND side. Cause not known. Open a new one.

---

## 6. Network configuration on the pack

Five `AIP-*` files on user `SYSTEM` hold the configuration:

```
(SYSTEM)AIP-CONFIG:SYMB       IP address, gateway and subnet bits  <- the one you edit
(SYSTEM)AIP-HOSTS:SYMB        name -> address
(SYSTEM)AIP-NETWORKS:SYMB
(SYSTEM)AIP-PROTOCOL:SYMB
(SYSTEM)AIP-SERVICES:SYMB     service name -> port number
```

### 6.1 AIP-CONFIG: address, gateway, mask

One line per controller. The live line is:

```
# TCP number    E-II number    IP address    IP gateway    Subnet bits
0              0              192.168.199.40 192.168.199.001  0
                                             ^^^^^^^^^^^^^^^  ^
                                             router           netmask
```

* Column 3 is the ND's address.
* Column 4 is the default gateway. `000.000.000.000` means no default route: the machine
  reaches only hosts on its own segment. Here it is the host's loopback address, so
  anything off 192.168.199.0/24 is sent to the host (which matters only if Internet
  Connection Sharing is added, section 7.3).
* Column 5 is "Subnet bits". There is no separate netmask file.
* The lines mix styles: the address plain (`192.168.199.40`), the gateway zero-padded
  (`192.168.199.001`). Both forms appear in ND's own files.

The file's own header says the address must also be changed in `AIP-HOSTS:SYMB`, and that
the controller must be restarted for a change to take effect.

### 6.2 About "Subnet bits"

No ND document found so far defines the units of this field. The install descriptions do
not mention it, and the only other place it appears is the B05 load procedure, which pokes
subnet bits and gateway straight into the PIOC segment (`@LOOK-AT SEGMENT TCPS1B1` /
`150615/0`) instead of reading `AIP-CONFIG`.

What is known: the value is `0`, the address is class C (192.168.199.x), and the machine
reaches its peers correctly. The reading that fits is *bits added beyond the classful
default*: class C already implies /24, so `0` gives /24. On that reading a /26 would be
`2`. **That is inference, not documented.** `LIST-VERSION` in TCPIP-MONITOR prints the
network mask the stack actually runs (section 9.4); check it there if you ever change the
field.

Both sides must agree or ARP never completes:

| | host (Windows, `ND-Loopback`) | ND (`AIP-CONFIG:SYMB` line) |
|---|---|---|
| address | `192.168.199.1` | `192.168.199.40` (column 3) |
| mask | prefix length 24 = `255.255.255.0` (`New-NetIPAddress -PrefixLength 24`) | Subnet bits `0` (column 5): class C, classful default /24 |
| gateway | none | `192.168.199.001` (column 4) = the host |

If the mask is ever changed on the host (for example to /25), the ND's subnet bits field has
to change with it, and the only reading available is the inference above. Test with `ping`
from the host and `net dump` on the card first.

### 6.3 AIP-HOSTS: names

A flat name table, no mask. Its job here is to name the two ends so `Netstat`, `PING` and
the clients print names:

```
192.168.199.40     c3          C3        <- this machine
192.168.199.1      host        HOST      <- the Windows host on the loopback adapter
192.168.1.11       linux
192.168.1.5        cvs5
192.168.1.1        router
```

`LIST-HOSTS` in TCPIP-MONITOR shows what the stack read from it.

### 6.4 DNS

DNS is a **client-side** feature of the 211154 clients (telnet/FTP/rsh), not part of the
gateway. It is off unless the file `(SYSTEM)AIP-RESOLVER:SYMB` exists, with public read
access, holding a default domain and at least one nameserver:

```
DOMAIN      yourdomain.local
NAMESERVER  192.168.1.1
```

ND-895071-2 section 4:

> If name-to-address resolution is to be performed by a domain name server, copy the
> `AIP-RESOLVER:SYMB` file to user SYSTEM with public read access, and edit it to include
> the local default `DOMAIN` name (to be added to all non-fully-qualified domain names), and
> the IP-address of at least one `NAMESERVER` on the net.

> If the (SYSTEM)AIP-RESOLVER:SYMB file does not exist, or contains no `nameserver`
> entries, the Resolver code will not be used, and the client will then access the
> (SYSTEM)AIP-HOSTS:SYMB file just like previous versions.

`AIP-RESOLVER:SYMB` is **not on this pack** (it shipped on the client floppy). Name lookup
comes from `AIP-HOSTS:SYMB` alone, so hosts must be listed there by hand. To turn DNS on,
create the file with the two keywords above; the clients read it, no reload of the stack is
needed.

### 6.5 Changing the address

1. Stop the emulator if you edit the pack from outside (ndtool, `-p` for even parity), or
   edit the files from inside SINTRAN.
2. Change the controller line in `AIP-CONFIG:SYMB` and the matching name line in
   `AIP-HOSTS:SYMB`.
3. Restart the controller. Either reboot, or run

   ```
   @MODE (TCP-IP)TCP-START-D02:MODE,,
   ```

   which calls `@(TCP-IP)PO-STOP-D02 0` and then `@RT TCPP`, so TCPP reads AIP-CONFIG again.
4. Read the console line `... with Internet address ... started` to confirm which address
   it took.

**Other RetroCore SINTRAN packs on this box use the same addresses. Never run two of them
on the same segment at once** without changing one first. The MAC differs automatically
(it comes from the CPU number) but the IP address does not.

---

## 7. Putting the machine on the real LAN instead

This is the alternative to the loopback setup. On a real adapter every other machine on the
LAN can ping, telnet and FTP to the ND, but **the PC that runs RetroCore cannot** (section
2.2): the host sees `Destination host unreachable` and FTP times out no matter what is right
or wrong on the ND side. Test from a second machine.

### 7.1 The three changes

* `RetroCore.ini`, the Realtek LAN adapter:

  ```
  device add ETH 0 --net=pcap:85D4DF8D-57E8-4863-B14D-17AB639EABE9
  ```

* `(SYSTEM)AIP-CONFIG:SYMB`, no default route:

  ```
  0              0              192.168.1.40   000.000.000.000  0
  ```

  or, to let it out through the LAN router:

  ```
  0              0              192.168.1.40   192.168.001.001  0
  ```

* `(SYSTEM)AIP-HOSTS:SYMB`: the machine's own line becomes `192.168.1.40 c3 C3`; the
  `linux`, `cvs5` and `router` lines already fit this network. The `host HOST` line is not
  needed.

Both AIP files carry the other setup's lines as `#` comments, so switching is a matter of
swapping the comment marks. Restart the controller (section 6.5). The loopback adapter can
stay installed; it does nothing while no card is bridged to it.

### 7.2 What is different on a real adapter

* **The card is promiscuous.** Every frame on the LAN is handed to it; the LANCE address
  filter then decides. Most of what `net status` counts as RX is other people's traffic.
  Expected.
* **Checksums from the capturing host are repaired on the way in.** The host that runs
  RetroCore offloads IPv4/TCP/UDP checksums to its NIC, and npcap captures its frames
  ahead of the NIC filling them in. `NDBusEthernetII` verifies every inbound IPv4 frame
  and rewrites only a checksum that fails (`RepairOffloadedChecksums`, on by default; no
  ini or command switch for it yet; `IpChecksumRepair` in `Emulated.HW\Common\Network`).
  Frames from other machines pass through untouched. The alternative is to disable TX
  IPv4/TCP/UDP checksum offload on the host adapter (Device Manager -> adapter -> Advanced).
* **The ND is reachable from other machines, never from the PC that runs RetroCore.**

### 7.3 Giving the loopback ND the LAN and the internet as well (optional, not done)

Windows Internet Connection Sharing, turned on for the LAN adapter and shared *to*
`ND-Loopback`, makes the host a NAT router and DHCP server for the loopback segment. The
host end of `ND-Loopback` is then forced
to 192.168.137.1, so the ND would move to 192.168.137.x with gateway 192.168.137.1 in
AIP-CONFIG; the ND can then reach the LAN and the internet; other LAN machines reach the ND
only through port forwards set in ICS' Settings dialog. Not done on this machine.

---

## 8. The Ethernet card in RetroCore (reference)

Read out of the emulator source (`EthernetBackendFactory`, `TcpEthernetBackend`,
`UdpEthernetBackend`, `PcapEthernetBackend`, `NDBusEthernetII`, the debugger's
`device add` and `net` commands). Where a value is inferred, it says so.

### 8.1 The ini line

```
device add ETH <card> --net=<spec>
```

`<card>` is the card's 12J thumbwheel, 0 to 3. It fixes the ND bus address, the ident
code and, on the SINTRAN side, the logical device number the TCP/IP mode files talk to.

| `device add ETH` | IOX range | ident | SINTRAN logical unit | used by |
|---|---|---|---|---|
| `0` | 140360-140363 | 140034 | 2240B | `TCP-START-D02` (`PO-STOP-D02 0`), ENNS0 |
| `1` | 140364-140367 | 140035 | 2241B | the B05 kit as shipped (`@PRLS 2241B`) |
| `2` | 140370-140373 | 140036 | 2242B *(inferred from the pattern)* | |
| `3` | 140374-140377 | 140037 | 2243B *(inferred from the pattern)* | |

All four interrupt on level 12. Only 2240B and 2241B have been seen from SINTRAN in a real
run. Without `--net=` the card exists but is connected to nothing: SINTRAN sees it, the
firmware boots, frames go nowhere. Enough for COSMOS on one machine, not for TCP/IP.

### 8.2 The `--net=` specs

| spec | what it does | when to use it |
|---|---|---|
| `pcap:<index>` or `pcap:<name substring>` | Bridges the card onto a host adapter through npcap. The token is an index from `net list`, or a case-insensitive substring of the adapter's name or description. An adapter GUID works because it is part of the npcap device name. | TCP/IP on a real adapter or on the loopback adapter. |
| `select` or `select:<ip prefix>` | At ini time, prints a numbered adapter menu on the RetroCore console and waits for a number. With a prefix such as `192.168.1` the default is the first adapter whose IPv4 starts with it; Enter takes the default. No valid choice: the card is added without a network. Resolved into a `pcap:<index>`, so it needs someone at the console. | An ini that moves between PCs with different NICs. |
| `udp`, `udp:<port>`, `udp:<group>:<port>`, `udp-mcast:...` | One UDP multicast group is one Ethernet segment. Default group 239.3.9.4, default port 3094 (the card's PCB number). No central process; every emulator in the group sees every frame. LAN only (TTL 1); managed switches with IGMP snooping can block it. | Several RetroCore machines on one LAN talking COSMOS to each other. |
| `tcp:<host>:<port>` or `<host>:<port>` | Dials out to a peer or a hub and tunnels frames over one TCP connection (5-byte `RETH` handshake, then `[u16 length][frame]`). Redials for ever with a capped backoff, so the peer may start later or restart. Default port 3094. | Two machines point to point, or many through a hub. Works through NAT because the client dials out. |
| `listen`, `listen:<port>`, `tcp-listen:<port>` | The other end of the point-to-point form: waits for exactly one `tcp:` peer. Port 0 means any free port. | Node A of a two-node pair (node B uses `tcp:127.0.0.1:<port>`). |

Anything else: the frontend logs
`Invalid --net= spec ... (expected pcap:<iface> | tcp:host:port | listen:port)` and adds the
card without a network.

**A hub for many machines over TCP.** `TcpEthernetRelay` in the emulator is the hub class,
but RetroCore.exe has no command that starts one. The hub in use is `xmsghub.exe` from the
NDInsight repository (`SINTRAN/XMSG/SRC/Xmsg.Hub`, run as `xmsghub.exe --port 5010`); every
machine then uses `--net=tcp:127.0.0.1:5010`. Same wire format. Known trap: after a reboot
the ASUS Armoury Crate service can grab port 5010 first.

### 8.3 Commands while the machine runs

Typed at the RetroCore debugger prompt (the same place the ini lines go):

```
net list            list the host adapters, with index, MAC and IPv4
net attach <id>     move the card to that adapter (index or name substring);
                    validated first, so a typo leaves the current bridge alone
net <id>            same as net attach <id>
net detach          disconnect the card (frames go nowhere)
net status          backend, card MAC, TX/RX counters, the LANCE's accepted /
                    filtered (wrong MAC) / missed (no buffer) counts, and the
                    "padded to 60 bytes" count
net dump [n]        the last n TX and RX frames, decoded header plus hex
                    (default 20); the way to see what actually crossed the wire
show config         the device list, including the card's network description
```

`net attach` only builds pcap bridges. For udp/tcp/listen, put the spec in the ini line.

---

## 9. TCPIP-MONITOR reference

ND's own maintenance program for the TCP/IP stack, `(TCP-IP)TCPIP-MONITOR:PROG`, version
**TCPIP-MONIT-100 version D00 of October 22, 1991**. ND's install description calls it
"intended for use by ND technical support" (ND-895061-2). The written reference is chapter
10 of the *SINTRAN SLIB Programmer's Guide*, ND-860372.1 EN, in NDInsight under
`Reference-Manuals`; that manual describes version A0C of 1988, so the D00 binary has more
commands than the manual lists. Below, "manual" means taken from ND-860372, "seen" means
run on this machine.

### 9.1 Starting and leaving it

```
@(TCP-IP)TCPIP-MONITOR
TCPIP-MONIT-100 version D00 of October 22, 1991
Slib:
```

The prompt is `Slib:`. Every command first prints `TCPIP-MONITOR connected to tcpdev=0`: the
monitor talks to TCP device 0, the `device add ETH 0` card. Commands can be abbreviated as
usual in SINTRAN programs (`NET a` is `NETSTAT a`). `EXIT` leaves. Leaving the monitor stops
any trace that is running (manual).

### 9.2 The commands (seen: `HELP` on this machine)

`HELP` (or `?`) lists them one per line, pausing with `Type any character to continue`:

`Help`, `Exit`, `Debug-On`, `Debug-Off`, `List-Hosts`, `Netstat`, `Arp`, `Ping`, `Kill`,
`List-Version`, `List-Domino-Configuration`, `Reboot-Controller`, `Place-Image`,
`Start-Trace`, `Stop-Trace`, `Test-Generate`, `Test-Echo`, `Test-Send`, `Test-Receive`,
`Loop-Open-Log-Files`, `Loop-Close-Log-Files`, `Loop-Send`, `Loop-Receive`,
`Loop-Generate`, `Sleep`, and the raw socket-library calls `Socket`, `Bind`, `Listen`,
`Accept`, `Connect`, `Send`, `Recv`, `Sense`, `Shutdown`, `Close`, `IoCtl`,
`Get-Socket-Name`, `Get-Peer-Name`, `Get-Option`, `Set-Option`, `Fill-And-Send`, `SEC`, `?`.
The same 37 names are in the program's command table on the pack, in this order.

The everyday ones are NETSTAT, ARP, PING, LIST-HOSTS, LIST-VERSION and KILL. The `Loop-*`,
`Test-*` and socket-call commands exercise SLIB by hand; `Test-Generate` (manual) sends N
messages of a given size to a remote echo server and has them returned, for stress and
throughput measurement. `List-Domino-Configuration`, `Reboot-Controller` and `Place-Image`
are for the Ethernet-III "DOMINO" controller on the octobus (manual); this machine has an
Ethernet II card, so expect them to report nothing useful.

### 9.3 NETSTAT

`NETSTAT <letter>`; default letter `a`. Letters (manual):

| letter | shows |
|---|---|
| `a` | active TCP connections: protocol, queue bytes, Cid, local and foreign address and port, state |
| `A` | the same connections with the SLIB access-point address and byte counts sent/received by the application |
| `h` | the hosts table, same as LIST-HOSTS |
| `i` | Ethernet media statistics from the card (transmissions, collisions, frames received, no-buffer drops, bad CRC, ...) |
| `m` | buffer (mbuf) statistics: entries, in use, free, drops per buffer type |
| `s` | protocol statistics: ip, tcp, icmp, udp counters |
| `t` | timing information |
| `n`, `r` | not implemented (manual) |

**`NETSTAT a`, seen on this machine:**

```
Slib:netstat a
 TCPIP-MONITOR connected to tcpdev=0
Prot   Rcv-Q-Snd   Cid   Local address  port  Foreign address  port  State
 TCP     0     0     1 192.168.199. 40    23    0.  0.  0.  0     0 LISTEN
 TCP     0     0     2   0.  0.  0.  0    21    0.  0.  0.  0     0 LISTEN
 TCP     0     0     4   0.  0.  0.  0    21    0.  0.  0.  0     0 CLOSED
 TCP     0     0     5 192.168.199. 40    20    0.  0.  0.  0     0 CLOSED
 TCP     0     0    20 192.168.199. 40    23  192.168.199.  1 19406 ESTABLISHED
```

How to read it:

* **Rcv-Q-Snd**: bytes waiting in the receive queue (for the application) and in the send
  queue (for the network). A receive queue that grows while a session hangs means the
  server has stopped reading.
* **Cid**: the connection identifier inside TCP. It is the argument to `KILL`.
* **LISTEN with zero addresses** = a server waiting for connections; the port says which: 23
  telnet server (TCPP), 21 FTP server (FTPRT). The manual's example also shows 7 echo, 551
  OWS access, 560 and 561 SIBAS. The port 23 listener here is bound to the card's own
  address, the port 21 listener to 0.0.0.0.
* **CLOSED entries are left-overs.** Cid 4 (port 21) and Cid 5 (port 20, the FTP data port)
  above are the remains of an earlier FTP session. **A stale CLOSED socket on a port can
  shadow its listener:** while Cid 4 existed, a SYN to port 21 from the host was answered
  with a TCP reset although Cid 2 was listening. Remove it with `KILL 4` (manual: "to
  remove a connection in TCP without rebooting the controller"), or restart the servers
  with `@MODE (TCP-IP)TCP-START-D02:MODE,,`. Both are verified to clear a leftover on this
  machine.
* **A program stopped with ESC leaves its listener behind.** The TCP connection belongs to
  TCPP, not to the program, so after `@ECHOPL` was stopped with ESC, `NETSTAT a` still
  showed `0.0.0.0 7 ... LISTEN` with nothing behind it. Starting the program again works
  (the new run's listener replaces the old one); `KILL <cid>` on the leftover removes it.
* **State** is the TCP state: LISTEN, SYN-RCVD, ESTABLISHED, FIN-WAIT, CLOSE-WAIT,
  TIME-WAIT, CLOSED, and so on.

**`NETSTAT s`** (manual) prints, per protocol, counters such as `bad tcp checksums`,
`bad tcp segments (to which we sent RST)`, `retransmissions we sent`, `icmp echo requests
responded to`. Only the TCP counters are really implemented; the IP, ICMP and UDP lines are
printed but not maintained. In D00 it prints only non-zero counters. Read it around a test
whenever a TCPP error message appears on the console: if `bad tcp checksums` steps, the TCP
layer rejected a segment; if it does not, the message comes from somewhere else.

**`NETSTAT m`** (manual): mbuf pool. "Be aware of drops! If there are drops on any buffer
type, this means a message has been lost." Drops on `mt_header` (to the net) and
`mt_deliver` (from the net) are recovered by retransmission; drops on `mt_data` (from SLIB)
are data lost for good.

**`NETSTAT i`** (manual): the card's Ethernet statistics "in the same way as the COSMOS
Ethernet Monitor does": transmissions, collisions, `frames received and sent to user`,
`no buffer for receive frame`, `received with bad CRC`, and so on. Compare with RetroCore's
`net status`.

### 9.4 ARP, PING, LIST-HOSTS, LIST-VERSION, KILL

* **ARP** (manual): the ARP table, IP address in decimal, Ethernet address in hex, and IF =
  controller number. Only hosts that have exchanged frames with this machine after the
  last controller restart appear. ND's D02 release note recommends it for chasing a
  "Duplicated IP addresses" report: the table shows which Ethernet address claims the
  disputed IP. On the loopback setup, expect one entry: 192.168.199.1 at
  02:00:4c:4f:4f:50.
* **PING** (manual): `PING <host>`; `<cr>` or `*` pings every host in the hosts table.
  Prints name, address and OK / No contact / Error in answer. The local host itself answers
  "Error in answer" by design.
* **LIST-HOSTS** (manual): the entries of `(SYSTEM)AIP-HOSTS:SYMB`: address, name,
  aliases. It should list `192.168.199.40 c3 C3` and `192.168.199.1 host HOST`.
* **LIST-VERSION** (manual): generation date, version, system type, port name, and, the
  useful part, **IP address, gateway address and network mask (hex)** as the stack actually
  runs them, plus number of connections and buffers, uptime, and the eight event-enable
  masks. This is the way to see what "Subnet bits 0" became as a mask.
* **KILL <Cid>**: removes one connection from TCP. Take the Cid from `NETSTAT a` or `A`.
  Verified here on a leftover port-7 listener: `kill 22`, and the next `NETSTAT a` no
  longer listed it.

### 9.5 START-TRACE / STOP-TRACE (manual, not tried on this machine)

```
Slib:START-TRACE
Trace Mask : <bits, decimal or with B for octal>
Tcp device number (1-15) : 0          (this machine: 0 = the Ethernet II card)
Trace file Name (continuous) : TCP-TRACE:DATA
```

Trace mask bits (octal): 1 user events, 2 AIP events, 4 buffer queues, 10 send/receive
queues, 20 sequence queue state, 40 SuperKernel events, 100 bad
messages/datagrams/inconsistency, 200 line trace on the user interface, 400 line trace on
the IP interface, 1000 data trace; -1 = everything. Output goes to a ring file;
`STOP-TRACE <file>` converts the ring file to readable text into the named file. The trace
stops when the monitor is left. The manual's device range 4 to 15 is for DOMINO controllers;
here the monitor itself reports `tcpdev=0`.

---

## 10. Stopping and restarting TCP/IP

**Restart the servers** (also picks up a changed AIP-CONFIG, and clears stale sockets):

```
@MODE (TCP-IP)TCP-START-D02:MODE,,
```

**Stop TCP/IP:**

```
@MODE (TCP-IP)TCP-STOP-D02:MODE,,
```

Aborts the servers and unloads the controller. Use it for a clean stop of the machine; it is
not required.

**Start everything by hand** after a stop: section 3.3.

---

## 11. Known console messages

All of these are current facts about this machine. None of them stops TCP/IP from working.

**TCPP, once per new connection from a Windows client:**

```
<date time> 047301B: TCPP0-TCP      Invalid argument
         Information: 047303B:  Operation not supported on socket
```

Appears once for every new TCP connection from a Windows client (telnet, FTP, or your own
program's listener) and never for one from Linux. **It is harmless: the connection works, and
nothing on the wire changes.**

**Cause, found 2026-09-27: the TCP option parser in the card's own firmware.** When a SYN
arrives, the D02 PIOC firmware walks the TCP options in the routine at 0x16CBA of
`TCP-SER-B0-D02` (see [RE/TCP-OPTION-PARSER.md](RE/TCP-OPTION-PARSER.md)). It knows three
option kinds, and it handles them like this:

* **End of list (0)** ends the walk.
* **NOP (1)** is counted but the parser never moves past it, so the walk simply ends.
* **MSS (2)** is read correctly, and then the parser moves one byte too far (length + 1).
* **Any other kind** (window scale, SACK, timestamps) is reported to TCPP as 20161
  "Invalid argument" plus 20163 "Operation not supported on socket". That is this message.

Because of the extra byte, the option the parser looks at after MSS is really byte 5 of the
option list:

| Client | Options in its SYN | Byte 5 | Result |
|---|---|---|---|
| Windows | MSS, NOP, window scale, NOP, NOP, SACK | `03`, the window-scale kind | message |
| Linux | MSS, SACK, timestamps, NOP, window scale | `02`, read as a second MSS; the walk then ends on a zero inside the timestamp | quiet |

Hosts from the late 1980s sent MSS alone, which is why this never showed then.

**How it was proved.** Hand-made SYNs were sent onto the loopback adapter with npcap, and the
messages were counted in RetroCore's console log. Thirteen option layouts gave exactly what
the firmware's code predicts. That includes three that only this off-by-one predicts: an
end-of-list byte straight after MSS still gives the message, while an unknown kind straight
after MSS does not. TTL, window size and source port make no difference.

**Nothing to fix on the ND side.** The code is ND's own firmware and runs as written. Windows
always sends window scale, so a Windows client will always print this line.

**The same event without the message file** prints as bare numbers:

```
TCPP0-UE-library routineerror: 46
TCPP0-UE-library routineerror: 90
```

46 is TCPP failing to open its message file (SINTRAN error 46, no such file name); **90 is
the UE library's fallback when it cannot format the real error, not the error itself.** The
message file `(SYSTEM)UE-ERMSG-EN-D06:ERR` (365,568 bytes, 179 pages, public read) is on this
pack, so TCPP prints text. If a pack prints `routineerror: 90`, put that file on it (FTP,
binary mode); TCPP picks it up without a restart. Never read `routineerror: 90` as a
specific fault.

**The SINTRAN watchdog** (`(SYSTEM)ER-S3WD-DESC-D01:EDAT`, `ER-S3WD-MANA-D01:PROG`,
`ER-S3WD-LOG-D01:PROG`, `ER-S3WD-LOG:DATA`) is installed on this pack and prints the
description with each error entry, in this form:

```
ERROR   * 413B.5B * <date time> * XROUT.22141B
          Product unknown
          Error code unknown
          Parameter list is dumped:
             0B 117B  60B  60B
```

**XROUT "Product unknown / Error code unknown", once at boot**, with parameters
`0B 117B 60B 60B`. Cause not established. TCP/IP starts and works after it.

**The watchdog cannot write its log file:**

```
WARNING * 1170B.6B * ERS3WD.40751B
          Log file could not be opened/created
          File name: ER-S3WD-LOG:DATA
          Reason 1B.12B: Not read, write and common access
```

`(SYSTEM)ER-S3WD-LOG:DATA` exists (70 bytes, 11 pages) but its access bits do not give the
watchdog RT program read, write and common access. Candidate fix, untested:
`@SET-FILE-ACCESS ER-S3WD-LOG:DATA,RWACD,RWACD,RWACD` as SYSTEM, then reboot.

**`TCPP0-TCP Error in checksum`**, a steady trickle, only on a real adapter (section 7):
the host that runs RetroCore offloads checksums to its NIC and npcap captures its frames
with the checksum not yet filled in. RetroCore repairs them on the way in, so a current
build should not show this; if it does, check `NETSTAT s` for `bad tcp checksums` and turn
off TX checksum offload on the host adapter.

---

## 12. Developing TCP/UDP programs

The stack ships with a socket library, **SLIB** (ND-211566, B01 on this pack), under user
`TCP-IP`. How to program against it is in the developer section:

| Page | What it holds |
|---|---|
| [SLIB API reference](../../../Developer/Languages/Application/SLIB-API-REFERENCE.md) | Every call, record, constant and status code, from ND's `SLIB:IMPT` and `SLIB:DEFS` |
| [TCP and UDP sockets in PLANC](../../../Developer/Languages/Application/PLANC-TCP-UDP-SOCKETS.md) | How to write, compile and link a socket program, and the traps |
| [MAC Cookbook, section 11](../../../Developer/Languages/System/MAC-COOKBOOK.md#11-tcp-and-udp-from-mac-through-a-planc-shim) | Calling SLIB from a MAC program |
| [TCP echo server case study](../../../Developer/Case-Studies/TCP-Echo-Server.md) | Three working echo servers (PLANC TCP, PLANC UDP, MAC TCP) with their MODE files |

For testing from the host: `NETSTAT a` in TCPIP-MONITOR (section 9.3) lists your
listener and every connection, and `KILL <cid>` removes a socket left behind by a program
stopped with ESC. The ND cannot connect to its own address, so test from the host.

---

## 13. Rebuilding a pack: the one-time install (HENT)

ND split installation in two. The names come from their own mode files:

| | when | what it does | how often |
|---|---|---|---|
| **HENT** ("fetch") | cold start | loads the software into SINTRAN segments and patches the system server table | **once** per pack |
| **LOAD** | warm start | starts the RT programs that HENT loaded | **every boot** (section 3) |

Segments and RT descriptions live on the pack and survive a boot. Once HENT has been done, a
boot only needs LOAD. HENT is needed on a fresh pack, or after the TCP/IP files are replaced.

### 13.1 The files that must be on the pack

Under user `TCP-IP`, plus the five `AIP-*` files on `SYSTEM` (section 6):

```
(TCP-IP)TCPP-D02:PROG              the gateway - TELNET server + TCP/IP stack
(TCP-IP)FTPRT-D02:PROG             the FTP server front end
(TCP-IP)TCP-SER-B0..B3-D02:BPUN    PIOC firmware, four 128 KB banks = 512 KB
(TCP-IP)PO-STOP-D02:PROG           stops/unloads the Ethernet controller
(TCP-IP)PO-PWRFAIL-D02:PROG        powerfail handler
(TCP-IP)TCP-IP-LO-D02:MODE         the HENT mode file  <- this one
(TCP-IP)TCP-START-D02:MODE         the LOAD mode file
(TCP-IP)TCP-STOP-D02:MODE          the shutdown mode file
(TCP-IP)DEFINE-TCPP-D02:MODE       DMAC patch, server table index 7B
(TCP-IP)DEFINE-FTPRT-D02:MODE      DMAC patch, server table index 10B
(TCP-IP)TELNET-CLIEN-D01:PROG      clients
(TCP-IP)FTP-CLIEN-D01:PROG
(TCP-IP)RSH-CLIEN-D01:PROG
(TCP-IP)TCPIP-MONITOR:PROG         diagnostics (section 9)
(SYSTEM)UE-ERMSG-EN-D06:ERR        TCPP's message file (section 11)
```

Documented prerequisites, quoted from ND-895070-2:

```
SINTRAN III L06 PatchFile >= 2000B
BACKUP-SYSTEM version >= H            (ND-210337)
Ethernet II controller                (ND 110063)
```

This pack's banner reads `REVISION (PATCH FILE NO.): 3200B`, which meets the requirement.
An unpatched SINTRAN (patch file `0B`) never completes a telnet login, because its MTAD
connect-request code is the 1988 version. The M patch kit floppy image `ND-PATCH-SIN-M.img`
(`PATCHES:PATC` + `NEW-SYSTEM:PROG`) is kept with the SINTRAN-M machine folder.

### 13.2 Run it

Log in as `SYSTEM` and:

```
@MODE (TCP-IP)TCP-IP-LO-D02:MODE,,
```

That single command does everything, including calling the two DMAC patch files at the end.
It takes a minute or so and prints a lot.

### 13.3 What a good run looks like

```
@OPERATOR *** COSMOS TCP/IP GATEWAY IS BEING DUMPED ***
@ABORT tcpp                     ILLEGAL PARAMETER      <- normal, does not exist yet
@ABORT ftprt                    ILLEGAL PARAMETER      <- normal
@RT-LOADER
REAL TIME LOADER,  SINTRAN III VSX - M
*CLEAR-SEG TCPPS                SEGMENT NAME NOT DEFINED   <- normal on a first install
*NEW-BACK-SEGMENT TCPPS,,DM,,,,,     NEW SEGMENT NO:   144
*READ-PROGFILE (TCP-IP)tcpp-D02,TCPPS,,,,,
*DECLARE-PROGRAM TCPP,,,,
*CHANGE-RT-DESCRIPTION TCPP,30,TCPPS,,20,2,,,,,,,,
*WRITE-SEGMENT TCPPS,,
   144 TCPPS        0 111777  20615   0    0   1  RFW   DEMAND
*NEW-SEGMENT TCPS0B0 ...        NEW SEGMENT NO:   145
*READ-BI (TCP-IP)TCP-SER-B0-D02:BPUN,,,,
*SE-LO-AD,,177777
   ... the same for B1 (146), B2 (147), B3 (150) ...
*NEW-SEGMENT FTPS0,,,,,,        NEW SEGMENT NO:   151
*READ-PROGFILE (TCP-IP)ftprt-D02,,,,,
*DECLARE-PROGRAM ftprt,,,
*CLEAR-SEG popwr                RT-PROGRAMS ON SEGMENT: POPWR
                                DELETING THIS RT-PROGRAM(S)? Y   <- normal, M ships a POPWR
```

then the two server-table patches, each ending in:

```
@MODE (TCP-IP)DEFINE-TCPP-D02:MODE,,
)9ASSM SYMBOL-1-LIST         **** 000000 DIAGNOSTICS ****
SGF3/000000  'TCPP'
@MODE (TCP-IP)DEFINE-FTPRT-D02:MODE,,
SGF3/000000  'FTPRT'
```

**The four `READ-BI ... SE-LO-AD` must not report `NO SUCH PAGE`.** That error means the
`:BPUN` files were copied onto the pack with invented sparse holes, and the PIOC firmware is
incomplete. It is the single most likely thing to go wrong when the files come from a tool
rather than from a real pack.

**`**** 000000 DIAGNOSTICS ****` on both patches.** Anything else means the patch did not
apply, and telnet/FTP will not be reachable as system servers.

### 13.4 Harmless oddity at the end

After the last `)9EXIT` the mode file has trailing blank lines. With `@MODE ...,,` the
terminal becomes the input source again at end of file, and those leftovers get read as
commands, producing the terminal-type list and then:

```
What is your terminal type?  2
Illegal command given!
```

It happens **after** all the real work, so the install is fine. But answering that prompt
sets your terminal type: `2` is Teletype ASR 33. If your session misbehaves afterwards, set
it back (`6` is DEC VT100, 80 columns).

### 13.5 Then, once: make the clients reentrant

So any user can run them by short name (ND-895071-2):

```
@DUMP-PROGRAM-REENTRANT TELNET-CLIEN-D (TCP-IP)TELNET-CLIEN-D01:PROG
@DUMP-PROGRAM-REENTRANT FTP-CLIEN-D    (TCP-IP)FTP-CLIEN-D01:PROG
@DUMP-PROGRAM-REENTRANT RSH-CLIEN-D    (TCP-IP)RSH-CLIEN-D01:PROG
```

No output means it worked. Afterwards `@TELNET-CLIEN-D` starts the client from any user.

### 13.6 Then wire the boot

Put `(SYSTEM)LOAD-MODE:BATC` on the pack (section 3.1, even parity) and set the initial
commands so that `APPEND-BATCH 1 (SYSTEM)LOAD-MODE:BATC SYSTEM-OUTPUT-1` runs at boot.

---

## 14. Quick reference

```
LOGIN            terminal on TCP 9210 (send ESC first)   ENTER SYSTEM, blank password
HOST             ND-Loopback 192.168.199.1/24  <->  ND 192.168.199.40
                 ping / telnet / ftp 192.168.199.40   (ftp: SYSTEM, blank password)

HENT  (once)     @MODE (TCP-IP)TCP-IP-LO-D02:MODE,,
                 @DUMP-PROGRAM-REENTRANT TELNET-CLIEN-D (TCP-IP)TELNET-CLIEN-D01:PROG
                 @DUMP-PROGRAM-REENTRANT FTP-CLIEN-D    (TCP-IP)FTP-CLIEN-D01:PROG
                 @DUMP-PROGRAM-REENTRANT RSH-CLIEN-D    (TCP-IP)RSH-CLIEN-D01:PROG

LOAD  (each boot) AUTOMATIC: initial commands -> APPEND-BATCH 1 (SYSTEM)LOAD-MODE:BATC
                  by hand:  @SINTRAN-SERVICE-PROGRAM / START-XMSG / EXIT
                            @START-TADADM
                            @MODE (TCP-IP)TCP-START-D02:MODE,,
                            @SET-AVAILABLE
                  in a mode/batch file the service-program lines are @START-XMSG / @EX

NET   (RetroCore) needs npcap (https://npcap.com/) for pcap: and select
                  device add ETH 0 --net=pcap:<GUID of ND-Loopback>
                  other forms: pcap:<idx|name> | select[:prefix] | udp | tcp:host:port | listen:port
                  net list / net status / net dump [n] / net attach <id> / net detach

CHECK             @LIST-RT-DESCRIPTION TCPP     -> LOGICAL UNIT 2240B
                  @TAD                          -> TADs 768..777
                  @(TCP-IP)TCPIP-MONITOR   Slib: netstat a | netstat s | arp | ping <host> | list-version | kill <cid> | exit

RESTART           @MODE (TCP-IP)TCP-START-D02:MODE,,
STOP              @MODE (TCP-IP)TCP-STOP-D02:MODE,,
```

---

## 15. References: the original ND documentation

All paths are relative to the root of this repository.

### 15.1 The install descriptions for exactly what is on this machine

| Document | Product | Why it matters here |
|---|---|---|
| `Installation/Installation-Description/ND-895070-2-EN.md` | **COSMOS TCP/IP Gateway for Ethernet, 211185D** | **The one that describes what is installed here.** Prerequisites, storage requirements, the HENT/LOAD/STOP mode-file wiring |
| `Installation/Installation-Description/ND-895070-1A-EN.md` | COSMOS TCP/IP Gateway, 211185**C** (C07) | The earlier version. This is where the Berkeley Unix 4.3 / **not** 4.2 telnet compatibility statement is, and the FTP server on this pack is still the C07 component |
| `Installation/Installation-Description/ND-895071-2-EN.md` | **COSMOS Telnet/FTP Clients, 211154D** | The clients installed here (D01). Has the `DUMP-PROGRAM-REENTRANT` step, the DNS `AIP-RESOLVER:SYMB` option, and the `*TCPGATE` XMSG name for driving the stack from another machine |
| `Installation/Installation-Description/ND-895071-3-EN.md` | COSMOS FTP/TELNET Clients, 211154**E** | The later client release, for comparison |
| `Installation/Product-Info/ND-211154-A1-EN.md` | COSMOS - TCP/IP integration | Overview of how 211185 (gateway) and 211154 (clients) fit together |

### 15.2 The things TCP/IP sits on top of

| Document | Covers |
|---|---|
| `Installation/Installation-Description/ND-895036-2-EN.md` | COSMOS Basic Module (210374G): TADADM, XFTRAD, spooling, file server |
| `Installation/Communication/COSMOS Basic/COSMOS-Basic-Install-Guide.md` | Practical install/start guide for the Basic Module, rev E04 |
| `Reference-Manuals/ND-60.164.3 EN COSMOS Programmer Guide.md` | XMSG and XROUT. Appendix B is the routing/directory record format, needed to decode what the PIOC and SINTRAN say to each other |
| `Installation/Communication/Ethernet/ND-210580-02-EN.md` | The Ethernet option: `ENNS<n>` network-server naming and the install dialogue |
| `Reference-Manuals/ND-60.197.01 EN Ethernet Basic Software Programmer Guide.md` | Ethernet basic software. **Section 2.4 is the authoritative MAC address format** (`08 00 26` + byte-reversed ND system number + physical user) |
| `Reference-Manuals/Devices/ND-12.055.1 EN Ethernet II Controller.md` | The card itself: up to four controllers, thumbwheel 12J, the IOX/ident/bank table |
| `Reference-Manuals/ND-860372.1 EN SINTRAN SLIB Programmer's Guide` | SLIB and, in chapter 10, TCPIP-MONITOR |

### 15.3 SINTRAN itself

| Document | Covers |
|---|---|
| `Reference-Manuals/ND-60.128.5 EN SINTRAN III Reference Manual.md` | The command set: `MODE`, `RT`, `LIST-RT-DESCRIPTION`, `DUMP-PROGRAM-REENTRANT`, `SET-AVAILABLE` |
| `Operations/SINTRAN/ND-30.003.007 EN SINTRAN III System Supervisor.md` | Operator side: `SINTRAN-SERVICE-PROGRAM`, `START-XMSG`, batch, initial commands |
| `Reference-Manuals/ND-60.133.02A SINTRAN III Real Time Guide.md` | RT-LOADER, segments and RT descriptions, which is what `TCP-IP-LO-D02:MODE` drives |
| `Reference-Manuals/ND-820023-1-EN SINTRAN III-VSX System Documentation.md` | VSX system documentation |
| `Installation/OS/05-PATCHES.md` | Notes on applying the SINTRAN patch file (marked SCAFFOLD, incomplete) |
| `Installation/OS/versions/SINTRAN-M.md` | SINTRAN III M install notes, including the `HENT-MODE` warm-boot script and `PATCH-LOG` |

### 15.4 Reverse-engineering notes (this project's own findings, not ND's)

How ND's TCP/IP product is put together and how it drives the Ethernet II card
(folder `SINTRAN/XMSG/DOC/COSMOS-RE`):

| Note | Covers |
|---|---|
| [TCPIP-DRIVER-ON-ND-ETHERNET-II.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/TCPIP-DRIVER-ON-ND-ETHERNET-II.md) | How TCP/IP drives the Ethernet II card; the DIX versus 802.3 mode word at 0x1888A |
| [HOW-ND-SHIPPED-TCPIP-PRODUCT-EVIDENCE-2026-07-26.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/HOW-ND-SHIPPED-TCPIP-PRODUCT-EVIDENCE-2026-07-26.md) | Evidence for how ND packaged the product |
| [TCPIP-211185-B05-MEDIA-RECOVERED-2026-07-30.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/TCPIP-211185-B05-MEDIA-RECOVERED-2026-07-30.md) | Recovery of the B05 media |
| [TCPIP-D02-SEGMENT-RECOVERY-2026-07-30.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/TCPIP-D02-SEGMENT-RECOVERY-2026-07-30.md) | Recovery of the D02 segments; how the files on this pack were obtained |
| [TCPIP-B05-FIRMWARE-RE-2026-07-30.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/TCPIP-B05-FIRMWARE-RE-2026-07-30.md) | The B05 PIOC firmware |
| [WRITING-A-TCPIP-STACK-ON-SINTRAN.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/WRITING-A-TCPIP-STACK-ON-SINTRAN.md) | Background on the stack's structure |
| [HANDOFF-TCPIP-FIRMWARE-AND-D02-2026-08-04.md](../../../SINTRAN/XMSG/DOC/COSMOS-RE/HANDOFF-TCPIP-FIRMWARE-AND-D02-2026-08-04.md) | Handover notes for the firmware and D02 work |

The D02 PIOC firmware (the 68000 image that runs on the card: TCP state machine, IP
demux, telnet server) decoded from the binary (folder `Installation/Communication/TCP/RE`):

| Note | Covers |
|---|---|
| [README.md](RE/README.md) | What the folder holds and how the merged firmware image was verified |
| [TCP-SER-D02-CALL-TREE.md](RE/TCP-SER-D02-CALL-TREE.md) | Call tree of the firmware: IP output, ARP resolve, fragmentation, transmit |
| [TCP-SER-D02-FUNCTION-CATALOG.md](RE/TCP-SER-D02-FUNCTION-CATALOG.md) | Every routine with its address and role |
| [TELNET-XMSG-SIN.md](RE/TELNET-XMSG-SIN.md) | The telnet server, its hand-over to SINTRAN's MTAD, checksum and socket routines, status codes, the TCP state machine |

### 15.5 Online copies

```
https://retrocorelabs.github.io/norskdata-software-archive/docs/ND-895070-2-EN.html    gateway D
https://retrocorelabs.github.io/norskdata-software-archive/docs/ND-895070-1A-EN.html   gateway C / telnet server
https://retrocorelabs.github.io/norskdata-software-archive/docs/ND-895071-2-EN.html    clients D
https://retrocorelabs.github.io/norskdata-software-archive/docs/ND-895071-3-EN.html    clients E
```
