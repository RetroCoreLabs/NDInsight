# Plan: patch the TCP option parser in TCP-SER-D02

**Next:** step 1, the full validation run.

## Result, 2026-09-29: the patch removes the error lines

The patch was applied on the reference machine with `@LOOK-AT SEGMENT TCPS0B0` after
`TCP-IP-LO-D02:MODE`:

- word `133412` read `022156` before the change - the expected old word, which confirms
  the address (segment word 0 = byte 0 of the bank 0 payload);
- `60050` was written, and TCP was started with `TCP-START-D02:MODE`;
- **with the patch in, the TCPP lines**
  ```
  047301B: TCPP0-TCP      Invalid argument
           Information: 047303B:  Operation not supported on socket
  ```
  **are no longer printed.** Before the patch they came for every connection from Windows.

So applying this patch removes the error log lines. The original `:BPUN` files are
unchanged; running `TCP-IP-LO-D02:MODE` without the patch brings the lines back.

The patch has to be applied again after every run of `TCP-IP-LO-D02:MODE`, because that
file loads bank 0 from the `:BPUN` again (step 2 below makes that automatic).

The option parser at 0x16CBA in `TCP-SER-B0-D02.BIN` reports every option kind above 2 as
an error. That is the TCPP `Invalid argument` / `Operation not supported on socket` line
printed for every connection from Windows. The analysis is in
[TCP-OPTION-PARSER.md](TCP-OPTION-PARSER.md).

**Goal, as decided 2026-09-28:** when the kind is above 2, end the option walk quietly -
no report, no error. Kinds above 2 are NOT to be parsed or skipped. FAULT 1 (index one
byte too far after MSS) and FAULT 2 (NOP does not move the index) are left as they are.

**How, as decided 2026-09-28:** patch the firmware in its SINTRAN segment after it has been
loaded, with a MODE file, instead of changing the `:BPUN` files. The original files on the
pack are never touched, so their checksums stay valid and going back is just not running
the patch.

## Rules for this work

- **Never overwrite an original.** The `:BPUN` files and `TCP-IP-LO-D02:MODE` stay as
  they are.
- **Change as few bytes as possible**, inside the existing routine.
- **A patch is done only when it is measured on the machine**, not when it assembles.

## Steps

1. **Validate in full.** All with the RetroCore console log running, so every TCPP line has
   a host time:
   - the 13 SYN layouts from the analysis: none may print the message now, and the MSS
     must still be taken (capture the SYN-ACK and check the segment size used);
   - a SYN with a broken MSS length (below 4) must still be reported - that path
     (0x16DD6) is not changed;
   - Windows `telnet`, `ftp` and `finger` to the ND, and Linux (WSL) `finger`: each must
     connect and work, with no TCPP line;
   - a long FTP transfer both ways, to check nothing else changed.
2. **Make it automatic and write it up.** Put [TCP-OPTFIX-D02.MODE](TCP-OPTFIX-D02.MODE) on
   the pack as `(TCP-IP)TCP-OPTFIX-D02:MODE` (parity is decided per file - read
   [../COPYING-FILES-TO-SINTRAN.md](../COPYING-FILES-TO-SINTRAN.md) first; wrong parity
   gives `ILL. CHARACTER` and the patch does nothing). In `HENT-MODE:MODE`, add
   `@MODE (TCP-IP)TCP-OPTFIX-D02:MODE,,` on the line straight after
   `@MODE (TCP-IP)TCP-IP-LO-D02:MODE,,`. Its output must show
   `133412/ 022156 60050`; any other old word means the loaded firmware is not the one
   this patch was made for. Then update
   [TCP-OPTION-PARSER.md](TCP-OPTION-PARSER.md),
   [RUNNING-TCPIP-ON-RETROCORE.md](../RUNNING-TCPIP-ON-RETROCORE.md) and the Finger case
   study, and delete the finished steps from this plan.

## The patch

One instruction, 2 bytes, at the start of the unknown-kind report:

```
address  old bytes  old instruction           new bytes  new instruction
016E14   24 6E      movea.l $14(a6),a2 (1st   60 28      bra.b $16E3E
                    half of the instruction)
```

0x16E3E is the code the old path already ran after the report:

```
016E3E  42 6E 00 26   clr.w $26(a6)     bytes left = 0
016E42  60 00 FE 96   bra.w $16CDA      loop test: bytes left <= 0 -> leave at $16E46
016E46  movea.l (sp)+,a6 ; movea.l (sp)+,a2 ; jmp 2(a2)     normal return
```

So a kind above 2 now does exactly what it did before, minus the report: the walk stops and
the routine returns normally. Only the console line goes away.

**Branch distance, checked by hand:** `bra.b` is `60` plus an 8-bit distance counted from
the address after the instruction: 0x16E3E - 0x16E16 = `$28`. Not run through an
assembler or a disassembler, but the patched firmware runs and the lines are gone (see
Result).

**What is left behind:** bytes 0x16E16-0x16E3D (the rest of the old report block) are
never reached any more. They stay in the image unchanged.

## The patch file: TCP-OPTFIX-D02:MODE

Local copy: [TCP-OPTFIX-D02.MODE](TCP-OPTFIX-D02.MODE). The part that does the work:

```
@LOOK-AT SEGMENT TCPS0B0
133412/60050
.
```

### Where the numbers come from

| Value | Meaning | How it was found |
|---|---|---|
| `TCPS0B0` | the segment that holds bank 0 of the firmware | `TCP-IP-LO-D02:MODE`: `NEW-SEGMENT TCPS0B0` then `READ-BI (TCP-IP)TCP-SER-B0-D02:BPUN` |
| bank 0 | 68000 addresses 0x00000-0x1FFFF | the host image `TCP-SER-B0-D02.BIN` is the four bank payloads in order: each `:BPUN` payload (from file offset 0x44, 131072 bytes) was compared with the image, all four equal, 2026-09-28 |
| `133412` | segment word address, octal | 68000 byte address 0x16E14 / 2 = 0xB70A = 46858 = 133412B. The 68000 and the ND-100 are both big-endian, so byte 0x16E14 is the high byte of word 0xB70A |
| `022156` | the old word | bytes `24 6E` = 0x246E = 9326 = 022156B. Read at 0x16E14 of the `:BPUN` payload and of the image |
| `60050` | the new word | bytes `60 28` = 0x6028 = 24616 = 060050B |

That segment word 0 holds payload byte 0 comes from the D02 segment recovery, which found
each bank's 128 KB payload as a page-aligned copy in `SEGFIL0:DATA` and checked it against
the `:BPUN` checksum (see `SINTRAN/XMSG/DOC/COSMOS-RE/TCPIP-D02-SEGMENT-RECOVERY-2026-07-30.md`).
The segment NUMBER differs between runs (145 in one listing, 146 in another), so the patch
uses the segment NAME.

### Why LOOK-AT SEGMENT and not DMAC

ND's own install files patch a loaded firmware bank segment this way. The B05 loader,
`TCP-IP-LO-1-B05.MODE`, does it after its `READ-BI` lines:

```
@LOOK-AT SEGMENT TCPS1B1
150615/0
0
0
.
```

and its listing (`TCP-IP-LO-1-B05.LIST`) shows the reply:

```
@LOOK-AT SEGMENT TCPS1B1
READY:
150615/ 000000 0
 000000 0
 000000 0
 000000 .
-END
```

So `address/value` shows the old word and writes the new one, the next line is the next
word, and `.` ends without changing the word it is at. Addresses and values are octal
(`TCP-IP-LO-D02:MODE` writes -4 as `177774`). The D02 loader carries the same form
commented out, for segment `FTPS0`. ND's note with those settings says the controller must
be restarted before a change has effect, which fits: the patch goes in after the load and
before `TCP-START-D02:MODE`.

In the TCP files, DMAC is used only by `DEFINE-TCPP-D02:MODE` and `DEFINE-FTPRT-D02:MODE`,
to patch resident SINTRAN (`)RESSM`, `)CLOAD S3PATCH`). How DMAC would address a named
segment has not been looked up, so it is not used here.

### What is not verified

- The patch has been applied by hand on the machine (see Result), but
  `TCP-OPTFIX-D02:MODE` itself has not yet been run as a file.
- Which program copies the segments to the controller has not been read. That the copy
  happens at `TCP-START-D02:MODE` (after `PO-STOP-D02 0`) comes from the order of the ND
  files and ND's restart note, not from the code.

## Review of the 2-byte change, 2026-09-28

Read in Ghidra from the image. The bytes on disk at 0x16E06-0x16E45 were compared against
Ghidra and are the same; the image is loaded at address 0, so the file offset equals the
address.

- **Nothing else uses the replaced bytes.** Ghidra shows one way into 0x16E14: the
  `bne.b` at 0x16E0C (kind is not 1, after the kind-2 test at 0x16D0A sent it there).
  Nothing references 0x16E36 or 0x16E3C. 0x16E3E was reached only by falling through from
  the report call, and 0x16E42 from 0x16E04 and 0x16E12; both stay as they are.
- **No pointer into the block.** The whole image was searched for `00 01 6E ??` (a 32-bit
  pointer into 0x16Exx). Three hits, none of them a pointer: 0x3896 is inside
  `cmpi.w #1,d0 ; bgt`, 0x1626F inside `beq.w`, 0x1EF9F inside `bra.w`.
- **Limit of that check:** Ghidra's references cover only code it has followed. A jump
  through a computed address would not show up. Nothing in the routine suggests one, but
  it is not proven.
- **No registers or frame fields change** compared with the old path, other than the ones
  the report call used to set (`$50`-`$5A`, only arguments for 0xA83C). The kind-2 error
  path at 0x16DD6 sets its own.
- **What is not changed:** FAULT 1 and FAULT 2 stay. After MSS the walk still reads one
  byte too far; if that byte is above 2 the walk now stops quietly, exactly where it
  stopped before. The Windows and Linux behaviour in the analysis is the same, apart from
  the missing line.
- **Not read:** the report routine at 0xA83C. Whether anything depends on it being called
  for an unknown kind has not been checked.

## Not known yet

- Whether real ND hardware prints the same line. The same image should behave the same,
  but nobody has measured it.
