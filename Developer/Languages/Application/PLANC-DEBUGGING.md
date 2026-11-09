# Debugging PLANC programs on SINTRAN III

How to turn debug symbols on, and how to use them once they are on - plus what else SINTRAN
gives you when a PLANC program goes wrong.

**Status of this page:** everything below is taken from the manuals, with the manual and the line
(in the Markdown copy under `Reference-Manuals/`) or page given for each claim. **None of it has
been tried on our live machines yet.** Where something is not known, the page says so.

The two manuals:

- **PLANC** = [ND-60.117.5 EN PLANC Reference Manual](../../../Reference-Manuals/ND-60.117.5%20EN%20PLANC%20Reference%20Manual.md)
- **DBG** = [ND-60.158.5 EN Symbolic Debugger - User Guide](../../../Reference-Manuals/ND-60158-5-EN%20Symbolic%20Debugger%20-%20User%20Guide.md)

---

## 1. Turn debug information on

There are two ways the manuals show it. Both switch the same thing.

**In the source** (PLANC section 0.18, line ~11095):

```
$DEBUG-MODE ON
MODULE hello
...
ENDMODULE
```

`$DEBUG-MODE OFF` switches it off again; the default is OFF. The command must stand **outside the
outermost module** (PLANC restrictions list, item 13, line ~14639).

**At the compiler prompt** (DBG section 5.3 "Another Example in PLANC", page 112, line ~4735):

```
@PLANC-100
*DEBUG-MODE
*COMPILE SORTER SORTER:LIST SORTER
```

Our own build recipe (see [PLANC-DEVELOPER-GUIDE.md](PLANC-DEVELOPER-GUIDE.md#build-process))
starts the compiler with `@PLANC`, not `@PLANC-100`. Whether `DEBUG-MODE` is accepted the same way
at that prompt has **not been tried**.

Debug mode does not change the code that runs; it adds information the debugger reads. That is
stated in the debugger description in ND-80.001.2 (ND-500 folder, line ~7690). For the ND-100 no
manual found says it in so many words.

### What changes in the link step

Nothing new to type. You link as usual; the BRF-Linker shows an extra `DEBUG` counter in its
`FREE:` lines (DBG section 5.3, line ~4743):

```
@BRF-LINKER
Brl: PROG-FILE "SORT-EXAMPLE"
Brl: LOAD SORTER
FREE: P 000156-177777 DEBUG 000300
Brl: LOAD TESTSORT
FREE: P 002404-177777 DEBUG 000515
Brl: LOAD PLANC-1BANK
FREE: P 005460-177777 DEBUG 000515
Brl: EXIT
```

The FORTRAN example in DBG section 2.2 (line ~805) shows the same: `FREE: P ... | D ... | DEBUG 000130`.

### Where the debug information ends up

The debugger reads it from the `:PROG` file. Evidence: the debugger command
`PROGRAM-INFORMATION` (DBG 3.38, line ~3515) lists, from the program file, "lower and upper bounds
for debug information", with the example output `DEBUG-INFORMATION: 000000B - 000063B`. The error
text "No Debug Information Available" (DBG chapter 6, line ~5538) says you either did not compile in
debug mode or forgot to `PLACE` the `:PROG` file.

**Not known:** the byte layout of that area inside the `:PROG` file. Measured 2026-11-09: the
ND-100 PLANC programs we have (CHAT.PROG built on D100, TPE-MON) carry no symbol or debug table.
They were, as far as we know, built without debug mode, so this does not contradict the manual - but
we have not yet looked at a `:PROG` file that was built with it.

A second hint that the debug area sits inside the `:PROG` file: when the ND-500 Loader Monitor
loads ND-100 code (`COMPUTER-MODE 100`), "program, data and debug information will all be loaded to
the :PSEG file, but in the same format as an ordinary ND-100 :PROG file" (ND-60.136.04A ND-500
Loader Monitor, line ~3140).

---

## 2. Start the debugger (ND-100)

### Ordinary (background) program

```
@DEBUGGER SORT-EXAMPLE
```

or start `@DEBUGGER` and then give `PLACE SORT-EXAMPLE` (DBG 2.2 line ~752; 3.37 line ~3492;
example on page 115, line ~4870). `PLACE` reads the `:PROG` file into your memory and sets the
program counter to the start address. `PLACE name W` also writes any memory change you make back
into the `:PROG` file - "use W with care".

### RT program

Needs user SYSTEM or RT, and only one terminal can use it at a time (DBG chapter 2, RT-program section, page 29, line ~1083). The
manual's sequence: load the `:PROG` onto a segment with the RT-Loader (`READ-PROGFILE`,
`DECLARE-PROGRAM`, `CHANGE-RT-DESCRIPTION`), then:

```
@SET-ERROR-DEVICE 39          (optional: break messages come to your terminal)
@RT-DEBUGGER
*ATTACH-SEGMENT 200B (DEBUGGER)FORTRAN-BUBBLE
*RT-PLACE BUBBLE
*BREAK 12
...  SINTRAN prints: BREAKPOINT IN BUBBLE AT ADDRESS 54B
*GET-BREAK-STATUS
```

`STEP` is not available in the RT-Debugger (DBG 3.51, line ~3802). For how we load RT programs, see
[PLANC-RT-AND-REENTRANT-PROGRAMS.md](PLANC-RT-AND-REENTRANT-PROGRAMS.md).

### Multi-segment / reentrant program

`ATTACH-REENTRANT-SEGMENT file,segment` then `REENTRANT-PLACE name`; needs user SYSTEM
(DBG 2.2.1, line ~884).

---

## 3. The commands you will use most

Commands can be cut short; the ones marked "+" in the manual win a tie, so `D` means `DISPLAY` and
`B` means `BREAK` (DBG 1.1, line ~464). Names use dot notation, `MODULE.ROUTINE.VARIABLE`, and a
place in the code is `ROUTINE.LINE`, with the line numbers from the `:LIST` file (DBG line ~4196).

| Command | What it does | Where |
|---|---|---|
| `BREAK quicksort` / `BREAK 12` | Stop at a routine, label or line. Optional count and condition | DBG 3.6 |
| `BREAK-ADDRESS addr` | Stop at a program address (for INLINE routines, which get no line numbers) | DBG 3.7, line ~1545 |
| `BREAK-RETURN` | Stop when the current routine returns. For a PLANC `ERRETURN` it shows the error code | DBG 3.8, line ~1654 |
| `RUN` / `CONTINUE` | Start / go on | DBG 3.44, 3.12 |
| `STEP n` | Go to the next step point; `LOG-LINES` makes every line one. `STEP -1` = one machine instruction | DBG 3.51, line ~3802 |
| `DISPLAY arr, i` | Show variables by name. `DISPLAY` alone shows the locals | DBG 3.13 |
| `SET seed = 1` | Change a variable | DBG 3.49 |
| `ACTIVE-ROUTINES` | The call chain: `QUICKSORT.3 CALLED FROM MAIN.23` | DBG 3.1, example line ~4893 |
| `LOOK-AT-DATA` / `LOOK-AT-PROGRAM` / `LOOK-AT-REGISTER` / `LOOK-AT-STACK` | Raw memory, registers, a stack frame | DBG 3.29-3.34 |
| `LOOK-AT-LIST start:link` | Walk a linked list of PLANC records | DBG 3.31 |
| `USING-PREFIX` | Name record fields inside a PLANC `USING` block | DBG 3.53 |
| `GUARD item low:high` | Stop when a variable leaves a range | DBG 3.21 |
| `PROGRAM-INFORMATION` | Start address, program/data bounds, debug-info bounds of the `:PROG` | DBG 3.38 |
| `@ command` | Run a SINTRAN command from inside the debugger | DBG 1.1 table |
| `EXIT` | Leave | DBG 3.16 |

A worked PLANC session (DBG 5.3, page 115, line ~4870):

```
*PLACE SORT-EXAMPLE
*SET SEED = 1
*BREAK QUICKSORT
*RUN
Break at QUICKSORT.6
*DISPLAY ARR
*ACTIVE-ROUTINES
QUICKSORT.3 CALLED FROM QUICKSORT.44
QUICKSORT.3 CALLED FROM MAIN.23
MAIN.9
*BREAK-RETURN
Break at QUICKSORT.46
*EXIT
```

### PLANC limits the debugger has (PLANC restrictions, item 15, line ~14643)

- After `BREAK-RETURN` the routine's out-value may not show yet; it is only stored once the calling
  statement finishes.
- If `ELSE`, `INCASE`, `EXITFOR` or `EXITWHILE` has code after it **on the same line**, a break on
  that line stops before the construct, not at the code after it. Put that code on its own line.
- WRITE parameters are not updated at `BREAK-RETURN` (DBG 3.8, line ~1702).
- `ILLEGAL COMMAND IN DEBUG-MODE` is a compiler error with "no further explanation" (PLANC line
  ~11351). Which commands it means is **not known**.

---

## 4. What SINTRAN and the PLANC runtime tell you without the debugger

Runtime messages, PLANC chapter "Runtime Messages", page 272 (line ~11565):

| Message | Meaning |
|---|---|
| `NO ON ROUTINEERROR HANDLER, ERRETURN=` | A routine took an `ERRETURN` exit and nobody catches it. The number may be your own or a SINTRAN error code |
| `ASSERT VIOLATION AT address` | An `ASSERT` was false and there is no `ON ASSERTFALSE` handler |
| `STACK OVERFLOW AT address` | Out of stack (the `INISTACK` array is too small, or runaway recursion). `ON STACKERROR` is not implemented, and stack overflow never runs exception blocks (PLANC line ~7583) |

The address in these messages is a program address. To turn it into a routine and line, start the
debugger on the same `:PROG` and use `FIND-SCOPE address` (DBG 3.17, line ~2162; example output
"line 49, belonging to the routine WRITE_TREE").

**Not documented here yet:** SINTRAN's own monitor-level tools (for example `@LOOK-AT` on a
program's memory) have not been checked against a manual for this page, so they are left out
rather than guessed.

---

## 5. ND-500

Same idea, different tools (DBG 2.3, line ~956): compile with `DEBUG-MODE`, load with the
Linkage-Loader, then `@ND-500` and `N500: DEBUGGER name`. Version G of the ND-500/5000 debugger has its own trap
handler (DBG line ~440). Full manual:
[ND-10335B ND-500 Symbolic Debugger](../../../Reference-Manuals/ND-10335B%20ND-500%20SYMBOLIC%20DEBUGGER.md).
Symbolic names only exist for modules compiled in debug mode (ND-80.001.2, line ~7690).

---

## What is still unknown

- Whether all of this works with the PLANC compiler and debugger versions on our machines.
- Whether `@PLANC` (as opposed to `@PLANC-100`) takes `DEBUG-MODE` at its prompt.
- The layout of the debug area inside an ND-100 `:PROG` file.
- Which commands trigger `ILLEGAL COMMAND IN DEBUG-MODE`.
- SINTRAN-level aids beyond the runtime messages above.
