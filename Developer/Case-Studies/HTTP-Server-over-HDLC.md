# Case Study: An HTTP Server on SINTRAN III, over HDLC

**A worked example tying together MAC programming, SINTRAN file I/O, and the
HDLC device — serving a web page and an image from an ND-100 to a browser.**

This case study is a map, not a code dump: it shows how the pieces
documented elsewhere in this repo combine into a real, running application,
and records the design decisions and lessons. Follow the links for the
how-to detail.

> **Verified** on SINTRAN III VSX/500 L under `nd100x`. Pages and a binary
> GIF were served to a normal browser, byte-for-byte intact.

---

## Goal

From a browser on a modern laptop, open `http://nd-server/` and get an
HTML 3.2 page **plus an image**, where the content lives on the ND-100's
SINTRAN file system and is served by a program running on the ND-100.

## Architecture

```
 browser ──HTTP──► host bridge ──HDLC frames (TCP tap)──► nd100x ──► MAC server (HSERVI)
                                                                         │
                                                          reads files from NDFS (MON 50/117/43)
```

Three layers:

1. **MAC server on the ND-100** — at startup it opens each file on the
   SINTRAN disk, reads it into memory, and then drives the HDLC controller to
   put the bytes on the wire.
2. **HDLC transport** — the ND's HDLC controller, exposed by the emulator as a
   TCP "tap."
3. **Host bridge** — a small program that speaks HTTP to the browser and
   HDLC frames to the tap, routing each URL to the right bytes.

## How each layer was built

### 1. The MAC server (read files, push frames)

- **Read files from NDFS.** Open with `MON 50` (access = 3, random), pull the
  whole file in one shot with `MON 117` (block read), close with `MON 43`.
  `MON 117` is essential here: the simpler sequential `MON 1` is capped at
  ~456 bytes, too small for a real page. Word counts, access codes, and the
  high-byte-first packing that lets a **binary GIF round-trip intact** are in
  the [MAC Cookbook — File system access from MAC](../Languages/System/MAC-COOKBOOK.md#7-file-system-access-from-mac-reading-files-to-serve-them).
- **Drive HDLC.** Reserve the device, DEVCL + DEVINI, then transmit the cached
  bytes as frames via `MON 201B`. The API is in the
  [HDLC Raw Programming Guide](../../SINTRAN/Devices/HDLC/HDLC-Raw-Programming-Guide.md);
  buffer-pool setup and the receive-arm trap are in
  [HDLC Buffer-Pool and Emulator Usage](../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md).
- The whole program is written and built with the
  [MAC Cookbook](../Languages/System/MAC-COOKBOOK.md) conventions and the
  [host cross-development loop](../Workflow/CROSS-DEVELOPMENT-WITH-ND100X.md).

### 2 & 3. Transport and host bridge

- The emulator's `--hdlc=1:<port>` exposes the controller's wire as TCP. The
  bridge connects there, de-stuffs/decodes HDLC frames the ND sends, and
  frames/encodes anything it sends back.
- The bridge serves HTTP to the browser and maps each request path to a slice
  of the bytes the ND produced (one HTML page, another page, the GIF), setting
  the right content type.

## Two working designs: broadcast and request/response

Both designs are implemented and verified on `nd100x`.

**Broadcast** (the first to ship): the ND continuously transmits all of its
cached files; the host bridge captures one full cycle and serves URLs from
that capture. The transmitter never goes idle, so it sidesteps the
restart-after-receive problem entirely — at the cost of caching every file in
RAM and keeping the wire always busy.

**Request/response** (now working, and the design that scales past RAM): the
ND receives an HTTP request, reads the requested data **from disk on demand**,
and replies. Our first attempt stalled — after the receive, a plain send
transmitted nothing — because the transmitter had gone idle and a bare `FSND`
did not restart it. The working recipe, verified end-to-end (a browser fetches
the full page, byte-exact), is:

1. **Transmit the buffer that just received.** After a real DMA receive the
   only DCB the driver will transmit is the one whose receive just completed.
   Overwrite its payload with your response bytes but **keep the RX-set
   `USize`** (the receive wrote the byte count into the shared size cell) — the
   driver validates the transmit length against that count, so the response
   frame can be at most as large as the request frame.
2. **Drain the transmit with an `FRCV` on the *output* LDN** before re-arming
   the buffer for receive. The DMA writes completion status back into the DCB;
   without the drain the transmitter dies after ~3 frames (a TX/RX write-back
   clash on a shared DCB — keep TX and RX DCB memory separate where you can).
3. **Pace the requests (or double-buffer RX).** A request frame sent
   *immediately* after a response is dropped (the ND is mid drain-and-re-arm,
   RX not yet armed). The pacing floor is only ~2 ms; ~10 ms is a safe margin.
   To drop pacing entirely, keep two or more RX DCBs armed so a fresh buffer
   always catches the next frame.
4. **Read on demand.** Open the file once (`MON 50`), set the block size to one
   chunk (`MON 76`, register form: `T`=file, `A`=size in words), and per
   request `MON 117`-read the next chunk into a single ~60-word buffer — no
   full-file cache. The host sizes each request to the chunk and reassembles.

The full recipe, the transmit DCB format it relies on, and the gotchas are in
[HDLC Buffer-Pool and Emulator Usage](../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md#restarting-transmit-after-the-tx-list-drains-incl-after-a-receive).

| Model | Status | RAM footprint | Notes |
|-------|--------|---------------|-------|
| Broadcast (cache all, stream) | ✅ verified | all files resident | simplest; transmitter never stops, wire always busy |
| Request/response (read on demand) | ✅ verified | **one ~118 B chunk at a time** | scales past RAM; ND program ~6× smaller (no cache); needs the TX-drain + light request pacing above |

On a 2 MB ND-110 the request/response model matters for *scale* — you can't
cache an unbounded site. The on-demand server holds only one disk chunk
regardless of total site size, and its ND-side program is roughly a
sixth the size of the cache-everything build.

## Lessons worth carrying forward

- **`MON 117`, not `MON 1`, for whole files** — the ~456-byte sequential cap
  is a wall you will hit immediately on real content.
- **Binary survives if you don't byte-swap** — `MON 117` packs high-byte-first;
  emit words high-then-low and a GIF arrives intact. No special binary path.
- **Size the HDLC receive arm above `FRSIZE`+header** — too small and the
  driver insta-completes the arm, turning a blocking receive into a busy
  flood. (Buffer doc §3.)
- **Enlarge the HDLC buffer pool once, into a base image** — `CHANGE-BUFFER-SIZE`
  + `@RESTART-SYSTEM` (warm start), then reuse the snapshot. (Buffer doc §1;
  cross-dev workflow.)
- **A host bridge is a legitimate architecture** — pushing the HTTP/routing
  complexity to the host keeps the ND-side MAC program small and within the
  device's real constraints.
- **After a receive, transmit the buffer that received** — a fresh standalone
  TX DCB won't start the transmitter post-receive; the just-completed RX DCB
  will. Refill its payload, keep the RX-set size. (Buffer doc, RX→TX section.)
- **Drain each send with an `FRCV` on the output LDN** — lets the DMA finish
  writing status back into the DCB before you reuse it; without it the
  transmitter stalls after a few frames.
- **Pace request/response lightly, or double-buffer RX** — the ND needs a beat
  (~2 ms floor, ~10 ms safe) between requests to drain TX and re-arm RX; a
  too-fast follow-up is dropped. Keeping 2+ RX DCBs armed removes the need.
- **`MON 76 SetBlockSize` is register-based** (`T`=file, `A`=size in *words*),
  not a parameter list — passing a list address returns error `133₈`. Set the
  block size to one chunk and each `MON 117` reads exactly one chunk.

---

## See Also

- **[MAC Cookbook](../Languages/System/MAC-COOKBOOK.md)** — writing/building the MAC server; file I/O.
- **[HDLC Raw Programming Guide](../../SINTRAN/Devices/HDLC/HDLC-Raw-Programming-Guide.md)** — the MON 201B transmit/receive API.
- **[HDLC Buffer-Pool and Emulator Usage](../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md)** — pool setup, receive tuning, the RX→TX caveat.
- **[Cross-Development with nd100x](../Workflow/CROSS-DEVELOPMENT-WITH-ND100X.md)** — the host build/run loop.

---

*Built and verified on SINTRAN III VSX/500 L under nd100x. Both the broadcast
and the on-demand request/response servers were run end-to-end: a browser
fetched the page byte-exact. Transmit-after-receive is a transmitter-restart
requirement, not an emulator limitation — first confirmed via SINTRAN's own
XMSG-HDLC-TEST echo mode between two relay-connected instances, then
implemented in our server by transmitting the just-received DCB and draining
each send with an output-side `FRCV`.*
