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

---

*Case studies are verified end-to-end on SINTRAN III VSX/500 L under nd100x.*
