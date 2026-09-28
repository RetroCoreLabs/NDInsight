# Reverse engineering — TCP-SER-D02 PIOC firmware

The 68000 firmware that runs the COSMOS TCP/IP Gateway D02 on the ND Ethernet II
controller. **All 906 functions carry a name, zero `FUN_` left** — of which **227 are
actually identified** and the rest are placeholders or stubs (see the breakdown below).
The TCP state machine is fully decoded.

| File | What |
|---|---|
| [`TCP-SER-D02-CALL-TREE.md`](TCP-SER-D02-CALL-TREE.md) | **Start here.** Module map, dependency graph, `protosw`, the 14×10 transition matrix and state diagram, the trace bitmaps, the server-name scheme, call trees, corrections, open items |
| [`TCP-SER-D02-CALL-TREE-FULL.txt`](TCP-SER-D02-CALL-TREE-FULL.txt) | depth-4 call trees from 15 entry points (1227 lines) |
| [`TCP-SER-D02-FUNCTION-CATALOG.md`](TCP-SER-D02-FUNCTION-CATALOG.md) / [`.csv`](TCP-SER-D02-FUNCTION-CATALOG.csv) | every entry point, one row each. **Pre-naming snapshot** — structural columns are current, the names are historical |
| [`TELNET-XMSG-SIN.md`](TELNET-XMSG-SIN.md) | how the telnet server reaches SINTRAN over XMSG |
| [`TCP-OPTION-PARSER.md`](TCP-OPTION-PARSER.md) | the TCP option parser at 0x16CBA, and why every Windows connection prints TCPP "Invalid argument" (an off-by-one after MSS) |
| [`PLAN-PATCH-TCP-OPTION-PARSER.md`](PLAN-PATCH-TCP-OPTION-PARSER.md) | open task: patch that parser in the firmware, keep the original, validate on the machine |
| [`TCP-SER-D02-GHIDRA-NAMES.csv`](TCP-SER-D02-GHIDRA-NAMES.csv) | **the applied names, exported** — `address,name,kind` for all 906 functions, so the naming survives independently of the local Ghidra database |
| `TCP-SER-B0-D02.BIN` | the four `:BPUN` banks merged into one flat 512 KB image — the Ghidra input |

## What "906 functions named" actually means

The headline number is true but flattering, and the `kind` column in the CSV exists to take
it apart. Counted from the export:

| kind | count | what it is |
|---|---:|---|
| `identified` | **227** | the name says what the routine does |
| `placeholder` | 429 | `MODULE_role_ADDR` — placed in a subsystem and given a role, nothing more |
| `stub-fault` | 221 | two-byte `trap #1` vectors |
| `stub-rte` | 20 | one-instruction `rte` "ignore this interrupt" stubs |
| `stub-empty` | 5 | prologue and epilogue, no body |
| `label` | 4 | stray duplicate labels, not real functions |

So **227 routines are actually understood**; 246 of the 906 are stubs that carry no
information at all. `kind` is computed from the name shape, not hand-assigned, so it can be
regenerated and cannot drift from the names beside it.

To re-apply the names to a fresh import, drive a Ghidra script from the `address` and `name`
columns — everything with `kind` starting `stub-` can be skipped.

## The merged image

`TCP-SER-B0-D02.BIN` — 524,288 bytes, md5 `f7a7ec0d365f27833c8494413681d5d2`. Built from
the four bank files in [`../x/D02-gateway-and-clients/TCP-IP/`](../x/) with no modification
to them: each `:BPUN` is a 63-byte NUL leader, a `0x21` mark, 4 bytes, then a 131,072-byte
image, so the four images concatenate to banks at 0x00000 / 0x20000 / 0x40000 / 0x60000.

Verified three ways: all four bank checksums match; the 68000 vector table at offset 0 is
coherent (SSP `0x05C8`, reset PC `0x1CFE`); and an instruction decodes cleanly across the
bank seam at 0x20000.

## What it turned out to be

A **PLANC-MC re-implementation of 4.2/4.3BSD networking** — real `struct protosw` entries
for raw/UDP/TCP, `pr_usrreq` dispatch, `m_get`/`m_freem`-shaped buffer handling, and a
14-state TCP machine driven by a transition matrix.

Findings that matter outside the disassembler:

- **No IP forwarding path.** A packet not addressed to this card (or broadcast) is counted
  and dropped. It is a host, not a router.
- **EtherType 0x9002** (configuration test) is answered roughly **one time in eight**, with
  a `"ND/EII-TCP-"` station banner.
- **The XMSG server name is self-modifying** — the code patches the string literal at
  0x07BDDC with the interface number. `*TCP` for interface 0, `*TCPn` otherwise. An
  emulator or HLE that maps that page read-only works on interface 0 and fails silently on
  every other one.
- **Fragment reassembly ages off the receive path**, not a timer — no packets arriving means
  no ageing.

## Reading it

Both `ghidra-planc` and `nd-ethernet-ii` skills carry the conventions this firmware uses —
the PLANC-MC skip return, the `jmp (A5)` error unwind, and the epilogue Ghidra always
misreads as an unrecoverable jump table. Read those before opening the image.

**Parent:** [../README.md](../README.md) ·
**Related:** [../../Ethernet/RE/](../../Ethernet/RE/README.md) — the ENCOS firmware for the
same card
