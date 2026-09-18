# Cross-Development: Building SINTRAN Programs from a Modern Host with nd100x

**How to edit, assemble, link, and run ND-100 / SINTRAN III programs from a
modern PC, driving the `nd100x` emulator — no hand-typing source on the
target.**

This is the loop we used to build and iterate on real MAC programs (an HTTP
server) hundreds of times. The existing [Scripting Guide](SCRIPT-GUIDE.md)
covers automation *inside* SINTRAN (MODE files); this document covers the
*host* side: getting your source into the emulated machine, building it, and
capturing output, all from outside.

> **Verified** against `nd100x` + SINTRAN III VSX/500 L on an SMD disk image.
> The mechanics are emulator-/host-agnostic; we automated them in Python, but
> nothing here depends on a particular language.

---

## The loop at a glance

```
edit source on host
   │  (encode correctly + stage into the disk image)
   ▼
boot nd100x with the image
   │
   ▼
drive @MAC / @NRL over the telnet console
   │
   ▼
run the program, capture console + device output
   │
   └─► repeat (re-stage source, re-boot or re-run)
```

Two host-side capabilities make this work: **(1)** writing files into the
SINTRAN disk image with the correct on-disk encoding, and **(2)** driving the
SINTRAN console over TCP (telnet). Everything else is orchestration.

---

## 1. Encode the source the way SINTRAN expects

A source file you stage into the image must match what the target subsystem
reads. For **MAC** (`:SYMB`) the rules are strict — get them wrong and you
get a misleading `ILL. CHARACTER` cascade:

- **CR-only** line endings (`\r`), never LF.
- **Even parity** on every byte.
- **No ETB/`\x17`** end-of-file byte; terminate with `)LINE`.
- File type **`:SYMB`**.

Full detail and the per-language variations are in the
[MAC Cookbook §0–1](../Languages/System/MAC-COOKBOOK.md). Other subsystems
(PLANC, NPL, BASIC) have their own line-ending / EOF conventions — encode to
match the one you are feeding.

## 2. Stage the file into the SMD disk image

You cannot just drop bytes into the image at an arbitrary offset — SINTRAN's
file system needs a real directory entry with correct invariants. The
reliable pattern is **let SINTRAN allocate, then fill from the host**:

1. Boot the image and, on the SINTRAN console, **`@CREATE-FILE name:type,pages`**
   so SINTRAN creates the directory entry and pre-allocates pages.
2. Shut the emulator down.
3. From the host, **write your (correctly-encoded) bytes into the file's
   allocated pages** using a tool that understands the on-disk file system,
   and patch the bytes-used / last-write-date / modified flag so SINTRAN sees
   a valid file.

This "create on target, fill from host" split avoids re-deriving every
directory-entry invariant. (We implemented step 3 in Python against the disk
image; any tool that reads/writes the SINTRAN FS format works.)

## 3. Boot nd100x

```
nd100x --boot=smd --smd0=<image.IMG> --telnet=<port> [--hdlc=1:<tcp-port>] [--max-instr=<N>]
```

- `--boot=smd --smd0=<image>` — boot from the SMD disk image.
- `--telnet=<port>` — expose the SINTRAN console on `127.0.0.1:<port>`; connect
  a TCP/telnet client to drive it.
- `--hdlc=1:<tcp-port>` — (optional) attach HDLC controller 1 and serve its
  wire on a TCP socket; see
  [HDLC Buffer-Pool and Emulator Usage](../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md).
- `--max-instr=<N>` — instruction budget; set high for long-running servers.

## 4. Drive the build over the console

Connect to the telnet port, log in, then send the build sequence as if typing
it. For MAC:

```
@MAC
)9ASSM <name>:SYMB,0,"<name>:BRF"     % list=0 silent; "..:BRF" creates the object
)9EXIT
@NRL
PROG-FILE "<name>"
LOAD <name>
EXIT
@<name>                                % run it
```

Practical tips:
- Drive it as a **send-line / read-until-quiet** exchange: send a command,
  read console output until it goes idle, then send the next. SINTRAN echoes
  and prompts (`@`, `*`) tell you where you are.
- For debugging an assembly error, use `)9ASSM ...,TERM,...` so MAC echoes each
  source line before its diagnostics (error addresses are location-counter
  relative, not line numbers — see the cookbook's debugging section).
- Build the linker step (`@NRL`) only after `)9EXIT` returns to `@`.

## 5. Run and capture output

- **Console output** comes back on the telnet stream. Marker prints
  (`SAT 1; SAA <char>; MON 2`) are the fastest execution trace — see the
  cookbook's debugging methodology.
- **Device output** (HDLC, etc.) comes back on that device's tap (e.g. the
  `--hdlc` TCP socket). Drive and verify it with a host-side client.
- The emulator's own logs (when enabled) show IOX register accesses and DMA
  commands — invaluable for I/O debugging.

---

## A reusable base image saves time

Some target state is expensive to set up every run (e.g. enlarging the HDLC
driver buffers needs `CHANGE-BUFFER-SIZE` + an `@RESTART-SYSTEM` warm start —
see the HDLC buffer doc). Do that **once**, snapshot the resulting image as a
**permanent base**,
and start each build by copying the base. Your per-build script then only
stages source and builds, never re-does the one-time setup.

---

## Why bother (vs editing on the target)

- **Real editor + version control** for your source on the host.
- **Reproducible, scriptable** build/run — essential for iterating quickly or
  for CI-style regression runs.
- **Programmatic verification** — assert on console/device output instead of
  eyeballing a terminal.

---

## See Also

- **[MAC Cookbook](../Languages/System/MAC-COOKBOOK.md)** — source encoding, the `)9ASSM`→NRL build, monitor-call ABI, file I/O.
- **[Scripting and Automation Guide](SCRIPT-GUIDE.md)** — automation *inside* SINTRAN (MODE files).
- **[Linking Guide](LINKING-GUIDE.md)** — NRL details.
- **[HDLC Buffer-Pool and Emulator Usage](../../SINTRAN/Devices/HDLC/implementation/Buffer-Pool-and-Emulator-Usage.md)** — the `--hdlc` tap, buffer setup, running HDLC apps under nd100x.

---

*Workflow verified while cross-developing MAC programs for SINTRAN III
VSX/500 L on nd100x from a Windows host.*
