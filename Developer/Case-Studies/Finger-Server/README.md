# Finger-Server - sources

The files for the [Finger server case study](../Finger-Server.md). Built and run on
SINTRAN III VSX/500 M with COSMOS TCP/IP D02.

| File here | Name on the pack | Format on the pack | What it is |
|---|---|---|---|
| `FINGER.PLNC` | `FINGER:PLNC` | as it is (7-bit, CR LF) | the server |
| `FINGER.MODE` | `FINGER:MODE` | even parity on every byte | builds `FINGER:PROG` |
| `FINGER.CONF` | `FINGER:CONF` | as it is | settings, read at start-up |
| `FINGERB.BATC` | `FINGERB:BATC` | even parity on every byte | runs FINGER as a batch job, with no terminal |
| `../TCP-Echo-Server/SLIBF00.DEFS` | `SLIBF00:DEFS` | as it is | ND's `SLIB:DEFS` made acceptable to PLANC-100-F00 |

Put them under user SYSTEM and run the server as SYSTEM, from a terminal or as a batch job. It cannot run as an RT program (see the case study, section 7). The parity conversion is shown in
the [echo server README](../TCP-Echo-Server/README.md).

```
@MODE FINGER:MODE,,
@FINGER                                          from a terminal, or with no terminal:
@BATCH 2
@APPEND-BATCH 2 FINGERB:BATC FINGERB-LOG:SYMB    (first: @CREATE-FILE FINGERB-LOG:SYMB,0)
```

To start it at every boot, put those two lines just before `@SET-AVAILABLE` in
`(SYSTEM)LOAD-MODE:BATC`; the case study, section 7, shows the result.

Lint first. The second `--include-dir` lets the linter find `SLIBF00:DEFS`:

```
python SINTRAN/XMSG/tools/planc-lint.py --include-dir Installation/Communication/TCP/x/D02-gateway-and-clients --include-dir Developer/Case-Studies/TCP-Echo-Server Developer/Case-Studies/Finger-Server/FINGER.PLNC
```
