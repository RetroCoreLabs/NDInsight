# ND-10373 — IS XMSG (X-Message, Inter System)

> Status: IN-PROGRESS — real J-version floppy decoded; same load/start pattern as ND-10130, plus inter-system extras

| Field | Value |
|-------|-------|
| ND article number | `ND-10373` |
| Product name | X-Message (Inter System) |
| Functional category | Networking & Communications (inter-task messaging, networked) |
| CPU target | ND-100 |
| Related products | `ND-10130` X-Message for SINTRAN III/VS — see [../ND-10130/README.md](../ND-10130/README.md), the base single-system product this one extends. **Historical note:** XMSG version **J** (1985), unrelated to this repo's live XMSG reverse-engineering project (`SINTRAN/XMSG/`, revision L03). |

## What is known — real floppy, decoded

Floppy `10373J00` (downloaded via NDwiki, imaged by Torfinn "Tingo" Ingolfsen) mounts cleanly. Its
file set is nearly identical to [ND-10130's](../ND-10130/README.md) J-version floppy — same
`XMSG-LOAD-J00:MODE` load script (decoded there, byte-for-byte identical in structure), same
`XMSG-SYSTABS`/`XMSG-POFTABS`/`XMSG-VALUES`/`XMSG-LIBRARY` support files, same CX/NX kernel
variants (here named `XMSG-KERN-*`/`XMSG-XROU-*`/`XMSG-SYMB-*` rather than the abbreviated
`XMSG-KE-*`/`XMSG-XR-*`/`XMSG-SY-*` seen on ND-10130 — cosmetic naming difference only, contents
not diffed byte-for-byte).

**What this floppy adds over the base product:**
- `XMSG-HDLC-TEST-J:PROG` — a compiled HDLC link test program, confirming this "Inter System"
  variant is specifically about the wire-level link between systems (HDLC being the physical/link
  layer XMSG rides on for inter-system traffic — see [LAPB-REQUIREMENTS.md](../../../SINTRAN/XMSG/DOC/LAPB-REQUIREMENTS.md), the compact LAPB note kept in this repository; the full ND LAPB spec it is a companion to, `lapb-nd-spec.md`, lives in the separate X25Emulator repository and not here).
- The load script's comment explicitly lists a third foreground program beyond `XROUT`/`XTRACE`:
  **`XFTRA`** (XMSG File Transfer) — "Create foreground programs XROUT, XTRACE and XFTRA" — real
  evidence that inter-system file transfer support is what distinguishes this product from
  ND-10130.
- `XMSG-STARTEX-J00:MODE`/`:BATC` in place of ND-10130's `XMSG-START-S-J00:MODE`/`:BATC` — same
  role (example startup script + batch wrapper), not individually re-decoded here since the
  pattern is already fully documented on ND-10130's page.

## Documentation
- No PD sheet or PI sheet located specifically for `ND-10373` (the base `ND-10130` PI sheet
  describes the shared XMSG concepts — ports, XROUT directory service, etc.).

## Provenance & open items
- Source: one real floppy image, downloaded via NDwiki and decoded in this session
  (`ndfs -t`/`ndtool -x`); the load script's structure was confirmed but not re-transcribed
  verbatim here (see [ND-10130](../ND-10130/README.md) for the full decode).
- **TODO:** `XMSG-STARTEX-J00:MODE`/`:BATC` and `XMSG-HDLC-TEST-J:PROG` were not individually
  decoded/read.

---
**Parent:** [../README.md](../README.md) (Software catalog)
