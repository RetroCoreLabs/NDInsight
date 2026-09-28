# The TCP option parser in TCP-SER-D02 (0x16CBA)

The routine at **0x16CBA** in `TCP-SER-B0-D02.BIN` walks the options of an incoming TCP
segment. `TCP_Input` calls it. It is 404 bytes, and the catalog lists it as
`TCP_rep_16CBA`, layer FSMR-tcp-fsm. It is the source of the TCPP console message

```
047301B: TCPP0-TCP      Invalid argument
         Information: 047303B:  Operation not supported on socket
```

that appears for every connection from a Windows client. Found 2026-09-27.

## What the code does

Disassembled with capstone (68000 mode) from the image. Frame offsets are on `a6`:
`$26` is the bytes left, `$24` the index into the options, and `$28` the current kind.

```
016CCC  move.l  $20(a6),d0 ; sub.l #$14,d0      bytes left = TCP header length - 20
016CE0  ble     done
016CF6  move.b  $20(a0,d1.l),d2                  kind = option byte at index
016D04  beq     done                             kind 0 = end of list
016D0A  cmpi.w  #2,$28(a6) ; bne notMss
        ... MSS: length byte must be >= 4 and fit in the bytes left, else ERROR
        ... on a SYN: read the 16-bit value, cap it at 0x400 (1024), store at TCB+$B4
016DC6  move.w  $24(a6),d4
016DCA  add.w   $2a(a6),d4                       index += length
016DCE  addq.w  #1,d4                            index += 1   <-- one byte too far
016E06  notMss: cmpi.w #1,$28(a6) ; bne error
016E0E  subq.w  #1,$26(a6)                       NOP: bytes left - 1, index NOT moved
016E14  error:  move.l #$4EC1,$56(a6)            20161 TcpEinval
016E2E          move.l #$4EC3,$5A(a6)            20163 TcpEopnotsupp
016E36          jsr    $A83C                     report to the host (TCPP prints it)
```

So:

* **End of list (0)** ends the walk.
* **NOP (1)** lowers the count but does not move the index. The same NOP is read again until
  the count reaches zero, so any NOP ends the walk quietly.
* **MSS (2)** is parsed, and then the index moves by length + 1, one byte past the next option.
* **Anything else** is reported as 20161 plus 20163. That covers window scale (3), SACK
  permitted (4) and timestamps (8).

## Why Windows triggers it and Linux does not

After MSS the parser reads byte 5 of the option list, not byte 4.

| Sender | Option bytes | Byte 5 | What happens |
|---|---|---|---|
| Windows 11 | `02 04 05 b4 01 03 03 08 01 01 04 02` | `03` | window-scale kind, so the message |
| Linux | `02 04 05 b4 04 02 08 0a <ts> <ecr> 01 03 03 0a` | `02` | read as MSS with length `08`; the index then lands on a `00` in the echo field, which ends the walk |

## How it was checked

Bare SYNs were injected on the host loopback adapter with scapy and npcap, and the TCPP lines
were counted in RetroCore's console log (`console log FILE`, stamped with host time).
Thirteen option layouts matched the code above. Three of them come out differently only
because of the off-by-one:

| Options | A correct parser | This parser | Seen |
|---|---|---|---|
| `02 04 05 b4 00 03 03 08` | stops at the end-of-list byte | reads byte 5 = `03`, error | message |
| `02 04 05 b4 03 01 01 01` | unknown kind 3, error | reads byte 5 = NOP, stops | quiet |
| `02 04 05 b4 01 01 01 01` | quiet | quiet | quiet |

TTL, window size and source port were varied as well, and none of them change the result.

## Why ND never saw it: TCP options then and now

Every statement in this section is checked against the RFC text, listed under
[References](#references). Quotes are exact.

### What the rules say

**RFC 793 (September 1981), section 3.1 "Header Format"**, the TCP standard of the time, defines three options:

```
  Kind     Length    Meaning
  ----     ------    -------
   0         -       End of option list.
   1         -       No-Operation.
   2         4       Maximum Segment Size.
```

Those are exactly the three kinds the ND parser knows. The same section says how far to
move past an option: *"The option-length counts the two octets of option-kind and
option-length as well as the option-data octets."* So the next option starts `length` bytes
further on. The parser moves `length + 1`, which is the off-by-one. RFC 793 also says of
NOP that *"receivers must be prepared to process options even if they do not begin on a
word boundary"*, and that *"A TCP must implement all options."*

**RFC 1122 (October 1989), section 4.2.2.5** added the rule for options a TCP does not know:
*"A TCP MUST ignore without error any TCP option it does not implement, assuming that the
option has a length field (all TCP options defined in the future will have length
fields)."* RFC 9293 (August 2022), which replaces RFC 793, keeps it as MUST-6. The ND parser
reports an error instead. Whether D02 was written before or after RFC 1122 is not known
here: the build date of the firmware has not been found.

### When the options that trip it arrived

| Option | Kind | First in | Status of that RFC | Now defined in |
|---|---|---|---|---|
| window scale | 3 | RFC 1072, October 1988 | experimental: *"not proposed as an Internet standard at this time"* | RFC 1323 (May 1992), then RFC 7323 (September 2014) |
| SACK permitted | 4 | RFC 1072, October 1988 | experimental, as above | RFC 2018 (October 1996, standards track) |
| timestamps | 8 | RFC 1323, May 1992 (standards track) | - | RFC 7323 |

RFC 1072 had "echo" options, kinds 6 and 7, not timestamps. Kind 8 first appears in
RFC 1323. All three options in the table are sent in the SYN: RFC 1323 says window scale *"is
sent only in a SYN segment"*, and RFC 2018 says SACK permitted *"may be sent in a SYN"* and
*"MUST NOT be sent on non-SYN segments"*.

So until October 1988 MSS was the only option with data that a SYN could carry, and until
1992 the others were experimental. A SYN with only MSS leaves zero bytes after it, the walk
ends, and the overshoot never reads anything. **What hosts actually sent in the late 1980s
is not recorded here**; the RFCs only show what was defined. When Windows and Linux began to
send these options on every connection is not known here either.

### Why Windows prints the line and Linux does not

A modern client sends several options after MSS, so the overshoot now reads a real byte.
Which byte that is depends on the order each operating system uses (see the table under
"Why Windows triggers it and Linux does not" above, taken from captured SYNs):

- **Windows** has window scale (kind 3) at byte 5. The parser does not know kind 3 and
  reports it, so every Windows connection prints the TCPP line.
- **Linux**, WSL included, has the length byte of SACK permitted there. That byte is `02`,
  which the parser takes as a second MSS with length `08`. It then lands in the timestamp
  echo field. RFC 1323 says that field *"is only valid if the ACK bit is set"* and *"When
  TSecr is not valid, its value must be zero"* (RFC 7323 makes it SHOULD), and a first SYN
  has no ACK bit. The parser reads that zero as end of list and stops quietly. So Linux is
  misread too, just without a message. WSL traffic leaves through Windows' address
  translation, which does not change TCP options, so the ND sees the Linux order.

**The lesson for TCP work on SINTRAN:** the D02 stack was written for the TCP of its time.
When a modern client and the ND behave oddly together, first check whether the client sends
something that the ND code predates. Options, window sizes and timers are the usual places.

### References

All from the RFC Editor, `https://www.rfc-editor.org/rfc/rfcNNNN.txt`:

- RFC 793, *Transmission Control Protocol*, September 1981 - section 3.1, "Header Format", the Options field.
- RFC 1072, *TCP Extensions for Long-Delay Paths*, October 1988 - window scale (kind 3),
  SACK permitted (kind 4), echo (kinds 6 and 7).
- RFC 1122, *Requirements for Internet Hosts -- Communication Layers*, October 1989 -
  section 4.2.2.5, "TCP Options".
- RFC 1323, *TCP Extensions for High Performance*, May 1992 - window scale (kind 3),
  timestamps (kind 8). Replaces RFC 1072.
- RFC 2018, *TCP Selective Acknowledgment Options*, October 1996 - section 2, SACK permitted
  (kind 4).
- RFC 7323, *TCP Extensions for High Performance*, September 2014 - replaces RFC 1323.
- RFC 9293, *Transmission Control Protocol (TCP)*, August 2022 - replaces RFC 793;
  MUST-6, MUST-7 and MUST-68 on options.

## Effect

The error path leaves the routine early, and the MSS has already been taken. The connection
is set up normally, so the only effect is the console line. The code is ND's firmware, run
as written. This was not seen on real hardware, but the same image would do the same there.

A fix to the firmware itself is planned in
[PLAN-PATCH-TCP-OPTION-PARSER.md](PLAN-PATCH-TCP-OPTION-PARSER.md).
