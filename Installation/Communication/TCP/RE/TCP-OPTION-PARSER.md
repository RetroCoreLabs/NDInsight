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

## Effect

The error path leaves the routine early, and the MSS has already been taken. The connection
is set up normally, so the only effect is the console line. The code is ND's firmware, run
as written. This was not seen on real hardware, but the same image would do the same there.

A fix to the firmware itself is planned in
[PLAN-PATCH-TCP-OPTION-PARSER.md](PLAN-PATCH-TCP-OPTION-PARSER.md).
