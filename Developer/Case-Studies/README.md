# Case Studies

End-to-end, worked examples that combine the language, device, and workflow
guides into a complete, **verified** application on real SINTRAN III under
`nd100x`. Each case study is a map: it shows how the pieces fit and records
the design decisions and lessons, linking to the how-to docs for detail.

---

## Case Studies

### [HTTP-Server-over-HDLC.md](HTTP-Server-over-HDLC.md)
**An HTTP server on SINTRAN III, serving files over HDLC to a browser**

Reads HTML and a binary GIF from the SINTRAN file system in a MAC program,
puts them on the wire via the HDLC controller, and serves them to a browser
through a small host bridge.

**Ties together:**
- [MAC Cookbook](../Languages/System/MAC-COOKBOOK.md) — writing/building the MAC server, SINTRAN file I/O
- [HDLC Raw Programming Guide](../../SINTRAN/Devices/HDLC/HDLC-Raw-Programming-Guide.md) + [Buffer-Pool and Emulator Usage](../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md) — the transport
- [Cross-Development with nd100x](../Workflow/CROSS-DEVELOPMENT-WITH-ND100X.md) — the host build/run loop

**Highlights:** `MON 117` to beat the 456-byte read cap, binary round-trip
via high-byte-first packing, the broadcast-vs-request/response design
decision (and the transmitter-restart-after-receive requirement behind it).

### [TCP-Echo-Server.md](TCP-Echo-Server.md)
**TCP and UDP echo servers on SINTRAN III, in PLANC and in MAC**

Three small servers on port 7, built against ND's socket library SLIB and tested from a
Windows host. They are a PLANC TCP server, a PLANC UDP server, and a MAC TCP server that
calls SLIB through a PLANC shim of `STANDARD` routines.

**Ties together:**
- [SLIB API Reference](../Languages/Application/SLIB-API-REFERENCE.md) and [TCP and UDP Programs in PLANC](../Languages/Application/PLANC-TCP-UDP-SOCKETS.md) - the library and how to use it
- [MAC Cookbook section 11](../Languages/System/MAC-COOKBOOK.md#11-tcp-and-udp-from-mac-through-a-planc-shim) - calling a PLANC library from MAC
- [Running COSMOS TCP/IP on RetroCore](../../Installation/Communication/TCP/RUNNING-TCPIP-ON-RETROCORE.md) - the network underneath

**Highlights:** PLANC-100-F00 cannot compile ND's `SLIB:DEFS` as shipped. SLinit fails with
20234 when the reserved messages are more than the sockets. MAC reaches PLANC through the
FORTRAN calling sequence. The reentrant `@MAC` on the M pack will not start.

Verified on SINTRAN III VSX/500 M under RetroCore.

### [Finger-Server.md](Finger-Server.md)
**A Finger server (RFC 1288, TCP port 79) for SINTRAN III, in PLANC**

Answers who is logged in and one user's terminal sessions. The data comes from documented
monitor calls: GetDeviceType, TerminalStatus through `MONITOR_CALL`, and GetUserEntry. A
configuration file decides who may be listed. Tested with Windows and Linux `finger`.

**Highlights:** there is no call that lists sessions, so the server walks the terminal and
TAD device ranges. SLIB takes in data only inside its own calls, so a SINTRAN sleep in a read
loop loses a query sent in two segments; the fix is SLIB's no-activity timer.

---

*Case studies are verified end-to-end on SINTRAN III VSX/500 L under nd100x.*
