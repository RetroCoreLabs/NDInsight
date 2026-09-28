# Plan: patch the TCP option parser in TCP-SER-D02

**Next:** step 1, keep copies of the original firmware files and record their checksums.

The option parser at 0x16CBA in `TCP-SER-B0-D02.BIN` moves one byte too far after MSS,
treats NOP wrongly, and reports every option it does not know as an error. That is the
TCPP `Invalid argument` / `Operation not supported on socket` line printed for every
connection from Windows. The analysis is in [TCP-OPTION-PARSER.md](TCP-OPTION-PARSER.md).
The task is to fix the firmware itself and prove the fix, without losing the original.

## Rules for this work

- **Never overwrite an original.** The patched image gets new file names, on the host and
  on the pack. The original files stay loadable, so going back is one MODE file change.
- **Change as few bytes as possible**, inside the existing routine. No new code elsewhere
  in the image unless the routine cannot hold the fix, and then say why in this file.
- **Read every byte of the routine before changing any.** The analysis covers the MSS,
  NOP and error paths. The full 404 bytes, and what the caller does with the result, have
  to be read before the patch is designed.
- **A patch is done only when it is measured on the machine**, not when it assembles.

## Steps

1. **Keep the originals.** Copy the host image and every pack file the loader reads to a
   folder kept outside the repository, and record the MD5 of each here. The host image is
   524288 bytes, MD5 `f7a7ec0d365f27833c8494413681d5d2`. Take the list of pack files from
   `TCP-IP-LO-D02:MODE` itself (the `READ-BI` lines that fill segments `TCPS0B0` to
   `TCPS0B3`) instead of writing it from memory.
2. **Read the whole routine.** Disassemble 0x16CBA to its end and write down every branch:
   how the index and the bytes-left count change for kinds 0, 1, 2 and anything else, what
   the error path returns, and what `TCP_Input` does with it. Check the call to 0xA83C
   (the report to the host) and whether anything else depends on the error being raised.
3. **State the root cause in code terms**, in [TCP-OPTION-PARSER.md](TCP-OPTION-PARSER.md):
   the `addq.w #1,d4` at 0x16DCE, NOP not moving the index, and unknown kinds not being
   skipped by their length byte. RFC 793 and RFC 1122 say an unknown option must be skipped
   using its length, not rejected.
4. **Design the fix** as a list of byte changes, each with the old bytes, the new bytes
   and the instruction before and after:
   - after MSS, move the index by the length only;
   - on NOP, move the index by 1 as well as lowering the count;
   - on an unknown kind, check the length byte (at least 2 and within the bytes left), skip
     that many bytes, and only report an error for a length that is broken.
5. **Build the patched image.** Apply the changes to a copy, disassemble the patched
   routine again and compare it against the design. Rebuild the four `:BPUN` bank files:
   68-byte header (63 NUL bytes, `0x21`, 4 header bytes), 131072 bytes of image, then one
   16-bit big-endian sum-of-words checksum. Before writing any, prove the checksum code
   gives the ORIGINAL files byte for byte.
6. **Load it on the reference machine.** Copy the patched bank files to the pack under new
   names, and make a copy of the loader MODE file that reads them. Keep the original MODE
   file and the boot file unchanged until the patch has passed step 7.
7. **Validate.** All with the RetroCore console log running, so every TCPP line has a host
   time:
   - the 13 SYN layouts from the analysis: none may print the message now, and the MSS
     must still be taken (capture the SYN-ACK and check the segment size used);
   - a SYN with a broken option length must still be refused or reported;
   - Windows `telnet`, `ftp` and `finger` to the ND, and Linux (WSL) `finger`: each must
     connect and work, with no TCPP line;
   - a long FTP transfer both ways, to check nothing else changed.
8. **Switch over and write it up.** Only after step 7 passes: point the boot at the patched
   files, update [TCP-OPTION-PARSER.md](TCP-OPTION-PARSER.md),
   [RUNNING-TCPIP-ON-RETROCORE.md](../RUNNING-TCPIP-ON-RETROCORE.md) and the Finger case
   study, and delete the finished steps from this plan.

## Not known yet

- Whether the routine has room for the unknown-kind skip without moving code. Step 2
  answers it.
- Whether real ND hardware prints the same line. The same image should behave the same,
  but nobody has measured it.
