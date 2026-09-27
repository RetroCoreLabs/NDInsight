# TCP-Echo-Server - sources

The files for the [TCP and UDP echo server case study](../TCP-Echo-Server.md). Every
program here was built and run on SINTRAN III VSX/500 M with COSMOS TCP/IP D02.

## The files, and what each must be on the pack

The repository copies are plain 7-bit text with CR LF line ends. Some need changing before
they go to the pack:

| File here | Name on the pack | Format on the pack | What it is |
|---|---|---|---|
| `SLIBF00.DEFS` | `SLIBF00:DEFS` | as it is | ND's `SLIB:DEFS` with `UNSIGNED` removed so that PLANC-100-F00 accepts it |
| `ECHOPL.PLNC` | `ECHOPL:PLNC` | as it is | TCP echo server in PLANC |
| `ECHOPL.MODE` | `ECHOPL:MODE` | even parity on every byte | builds `ECHOPL:PROG` |
| `ECHOUD.PLNC` | `ECHOUD:PLNC` | as it is | UDP echo server in PLANC |
| `ECHOUD.MODE` | `ECHOUD:MODE` | even parity on every byte | builds `ECHOUD:PROG` |
| `ECHOSH.PLNC` | `ECHOSH:PLNC` | as it is | the PLANC shim: six STANDARD routines around SLIB, for the MAC server |
| `ECHOMA.MAC` | `ECHOMA:SYMB` | **CR only** (no LF), even parity, no ETB at the end | TCP echo server in MAC |
| `ECHOMA.MODE` | `ECHOMA:MODE` | even parity on every byte | builds `ECHOSH:BRF`, `ECHOMA:BRF` and `ECHOMA:PROG` |

**Parity.** A byte has even parity when it has an even number of 1-bits. Where the count
is odd, set the top bit (add 128). A MODE file goes through SINTRAN's command reader, and a
MAC source through MAC's reader, and both want it. PLANC reads 7-bit text and prints
`(PARITY ERRORS)` in its summary, which is harmless.

**MAC line ends.** MAC rejects a line feed with `ILL. CHARACTER`. Change each CR LF to a
lone CR. See [MAC-COOKBOOK.md section 0](../../Languages/System/MAC-COOKBOOK.md#0-tldr--the-five-things-that-must-be-right).

A few lines of Python do both conversions:

```python
def even_parity(data):
    return bytes(b | 0x80 if bin(b).count('1') % 2 else b for b in data)

mac = open('ECHOMA.MAC', 'rb').read().replace(b'\r\n', b'\r')
open('ECHOMA.SYMB', 'wb').write(even_parity(mac))
open('ECHOMA-parity.MODE', 'wb').write(even_parity(open('ECHOMA.MODE', 'rb').read()))
```

Then send the files in binary mode, for example with Windows `ftp` to the ND as user
`SYSTEM`: `binary`, `put ECHOMA.SYMB ECHOMA:SYMB`. `FILE-STATISTICS` on the ND shows the byte count, so
you can check that it arrived whole.

## Build and run

```
@MODE ECHOPL:MODE,,        then  @ECHOPL
@MODE ECHOUD:MODE,,        then  @ECHOUD
@MODE ECHOMA:MODE,,        then  @ECHOMA
```

Type `MODE` at the `@` prompt. Typing `@MODE` gives `@@MODE`, which does nothing.

`ECHOMA.MODE` starts MAC with `@PLACE-BINARY MAC-1415C` and `@GOTO-USER 177777` rather
than `@MAC`. The reentrant MAC on the pack this was built on does not start (see
[MAC-COOKBOOK.md section 11](../../Languages/System/MAC-COOKBOOK.md#when-mac-does-nothing-at-all)).
On a pack where `@MAC` prints its `- MAC -` banner, either way works.

## Lint first

Every PLANC file here lints clean with:

```
python SINTRAN/XMSG/tools/planc-lint.py --include-dir Installation/Communication/TCP/x/D02-gateway-and-clients Developer/Case-Studies/TCP-Echo-Server/*.PLNC
```
