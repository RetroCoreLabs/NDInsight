# FORTRAN Build, Link and Debug: Learnings and FAQ

What we learned building a real FORTRAN program (the English *Adventure* game, about 4,000 lines
of FORTRAN plus assembler helpers) on SINTRAN III, from a bare SMD disk image. Short questions,
short answers. Everything here was seen on a running machine unless marked.

How to read the marks:

- **[SEEN]** happened on the emulator and the output was read.
- **[DOC]** comes from a manual or a product sheet, not from a run.
- **[NOT RUN]** written down but not tested.

The main guide is [FORTRAN-DEVELOPER-GUIDE.md](FORTRAN-DEVELOPER-GUIDE.md).

---

## 1. Choosing and installing a compiler

### Q. There are several FORTRAN compilers. Which one do I use?

For **new** programs, the newest one: `FORTRAN-100-F02` (ND-210191F02, banner `203053F02`).
**[SEEN]** The old `FTN-2090I` (ND-10023K) refused 11 lines in a program that F02 compiled with
one real error. The F02 compiler is also the one the main manual (ND-60.145.7A) describes.

**But a program that was written for the old toolchain is easiest to build with it.** The English
Adventure uses assembler helpers for one bank and the old runtime, and it nearly fills a 64K
bank. With F02, the one-bank link fails (`Program space exceeded`: the F02 runtime is much
larger) and the two-bank layout does not suit the one-bank helpers. The working build is FTN-2090I
plus `FTNLIBR`, after a few small source edits. See
[ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md).

### Q. What did the old compiler refuse?

In `ADV-SUBR` (1152 lines), routines such as:

```fortran
      LOGICAL FUNCTION YES(X,Y,Z)
      IMPLICIT INTEGER (A-Z)
      LOGICAL YESX
      YES     = YESX(X,Y,Z,RSPEAK)
```

FTN-2090I answered `"LOG. EXPR" ILL. ASSIGNMENT` on the assignment, as if `IMPLICIT INTEGER`
had turned `YES` into an integer. The manual says the type in a `FUNCTION` statement wins over
`IMPLICIT` (ND-60.074.01, section 4.10). F02 follows the manual. **[SEEN]** I did not find out
whether a *different revision* of FTN-2090 (the one the original authors used) accepted it. The
archive has only revisions H and I.

### Q. How do I install the F02 compiler?

Copy `FORTRAN-100-F02:PROG` and the runtime `FORT48-1BANK-F02:BRF` / `FORT48-2BANK-F02:BRF` (or
the `FORT32` pair) into `(SYSTEM)`. The floppy is `210191F02-XX-01D`. It is a plain `:PROG`, so you
do **not** dump it reentrant. **[SEEN]**

The older ND-10191 product sheet (A revision) tells you to dump it reentrant with
`DUMP-REENTRANT FORTRAN-100-A[,11,11],FORTRAN-100-A:BPUN` and to keep the `:PROG` file in
SYSTEM. That is for the `BPUN` form. **[DOC]** F02 ships as a `:PROG` and ran by name. **[SEEN]**

### Q. The compiler file is 655,360 bytes but only 137 pages. Is the copy broken?

No, the file is **sparse**: 183 of its 320 pages are holes (reading them gives zeros). Copy it
byte for byte *with its holes*, or you write 320 real pages. Use the ndfs library's `write_file`
with the hole list. `ndtool --put` writes the zero pages as real pages. The bytes are the same
(MD5 `4004c2ba5d0c22964a0072cf503885c3`) either way. **[SEEN]**

The same compiler is on two floppies: `210191F02-XX-01D` (with the runtime) and
`210191F02-XX-01S` (compiler only). They are byte-identical. **[SEEN]**

### Q. `@DUMP-REENTRANT FTN,0,1,FTN-2090I:BPUN` printed nothing. Did it work?

Yes. It prints nothing when it works. Run it a second time and you get
`NAME ALREADY USED ON REENTRANT SUBSYSTEM`. `@LIST-REENTRANT` shows `0B 1B 142B FTN`. The
dump survives a restart. **[SEEN]** Start addresses 0 and 1 are from the program description sheet. **[DOC]**

If you run `DUMP-REENTRANT` with no arguments it asks, in order: `NAME:`, `START ADDRESS (OCT):`,
`RESTART ADDRESS (OCT):`, `FILE NAME:`. **[SEEN]**

---

## 2. Compiling

### Q. What is the compile command?

| Compiler | Start | Command | Leave |
|---|---|---|---|
| FTN-2090I | `@FTN` (prompt `$`) | `COMP src,,"obj"` | `EX` or `EXIT` |
| F02 | `@FORTRAN-100-F02` (prompt `FTN:`) | `COMPILE src,,"obj"` | `EXIT` |

Source has **no quotes** (it exists). The object name **has quotes** (it is created). **[SEEN]**

### Q. The compiler says `FILE ALREADY EXISTS "ADV-HOVED"`.

It will not overwrite the old `:BRF`. Delete it first with `@DELETE-FILE ADV-HOVED:BRF`. In a MODE
file, put the deletes at the top. **[SEEN]**

**Watch for stale objects.** A compile that *failed* may still leave a `:BRF`. Mine did. If you
delete only some outputs, you may link an object from an older compiler. Delete every output
before a build.

### Q. Should I leave the compiler between builds?

Yes. Start the compiler, compile one unit, `EXIT`, and start it again for the next unit, so one
unit cannot inherit symbols from the previous one. This is the working rule from Ronny's
experience on these machines. **[DOC]** In my runs I compiled three units in one compiler session
and saw no carry-over, but I did not test for it. So I would still follow the rule.

### Q. What do the compiler's numbers mean?

```
- CPU TIME USED: 3.4 SECONDS.  1152 LINES COMPILED.
- NO MESSAGES
- PROGRAM SIZE=2638 DATA SIZE=2345 COMMON SIZE=37921
```

`PROG SIZE` is code, `DATA SIZE` is local data, `COMMON SIZE` is the largest total of the COMMON
blocks. With `SEPARATE-DATA OFF` the data is counted in the code figure. **[DOC]** ND-60.145.7A,
appendix. All three units of this program share one COMMON area, and the COMMON size differs
(41172 and 37921) because each unit uses a different set of blocks, which is normal.

### Q. What do the message formats look like?

| Compiler | Example |
|---|---|
| FTN-2090I | `** FTN ERR IN LINE 551 OF ADVENTU: "WD2X" SYNTAX ERROR` |
| F02 | `*** ERROR *** ADVENTUR  551: 'T(GRATE)) ? WD2X=TXOP', ')' ASSUMED` |

Both give the line number *within the program unit*, not within the file. F02 also shows the text
around the problem, with `?` where it gave up. **[SEEN]**

### Q. F02 said `')' ASSUMED` and reported 1 error. Why did it not compile the unit?

An assumed character is still an error, and with an error the object is empty:
`PROGRAM SIZE=0`. **[SEEN]** Fix the source. Do not count on the "assumed" repair.

### Q. What were the real mistakes in the English Adventure source?

Both mistakes are also in the Norwegian original. **[SEEN]**

1. `ADV-HOVED` line 551:
   `IF((WD1X.EQ.TXLOCK.AND.WD2X.EQ.TXOPP).AND.(AT(GRATE))WD2X=TXOPEN` is missing the final `)`
   of the `IF`. Fixed by adding it.
2. `ADV-SUBR` line 787 and 792: `INTEGER FUNCTION NEWHRX(DAY1,DAY2)` and later
   `DOUBLE INTEGER NHR,NEWHRX`. The function is typed twice, and F02 says
   `'NEWHRX', DOUBLY DEFINED`. The caller declares it `DOUBLE INTEGER`, so the double type is
   what was meant. **For F02** fix it by writing `DOUBLE INTEGER FUNCTION NEWHRX(DAY1,DAY2)` and
   dropping `NEWHRX` from the later line. **For FTN-2090 leave it as the authors wrote it**: the old
   compilers take the later declaration (that is how the original compiled), and they reject the
   `DOUBLE INTEGER FUNCTION` form (`"DAY1" NOT INTEGER TYPE`, `MISPLACED STATEMENT`). **[SEEN]**

After the first edit and the `NEWHRX` fix, F02 gives: HOVED 2 warnings and no errors, SUBR no
messages, INIT no messages. The two warnings are `BRANCH INTO DO/IF NEST` at lines 1746 and 1753,
meaning a jump into a `DO` or `IF` block. They are in the original program. I left them alone.

**For FTN-2090H and I** there are six more edits: in each of `YES`, `YESM`, `YESX`, `START`,
`WIZARD` and `PCESS` declare the function name `LOGICAL` *after* `IMPLICIT INTEGER (A-Z)`. The
full list with line numbers is in [ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md#4-changes-made-to-the-english-source).

### Q. Are lines longer than 72 columns a problem?

Yes, the compiler ignores everything past column 72, without a message. After editing a line,
check its length. **[DOC]** (Fixed form.)

---

## 3. Linking

### Q. `@BRF-LINKER` says `NO SUCH FILE NAME`.

A bare SINTRAN pack may have no linker. `@NRL` was not there either. Install ND-210721C, one
file `BRF-LINKER-C01:PROG`, then run it as `@BRF-LINKER-C01` (banner
`- BRF Linker -  210721C01`, prompt `Brl:`). **[SEEN]**

### Q. How do I link, step by step?

```
@BRF-LINKER-C01
Brl: PROG-FILE "ADVENTURE"
Brl: LOAD ADV-HOVED
Brl: LOAD ADV-INIT
Brl: LOAD ADV-SUBR
Brl: LOAD FORT48-2BANK-F02
Brl: EXIT
```

Each `LOAD` prints the free program (`P`) and data (`D`) address ranges. **[SEEN]**

### Q. I get `Brl message: Mixed one/two bank routines`.

It is a notice, not an error. It appears when you load a one-bank object (here, the assembler
helpers copied from an older build) into a two-bank program. Check that the helper really works
in a two-bank program. **[SEEN]**

### Q. The link ended with `Undefined entries`. Is there a `:PROG`?

Yes, and that is the trap. **The linker writes the `:PROG` file even when entries are undefined.**
`@LIST-FILES ADVENTURE:PROG` shows it, and it will not run. Always read the lines between `EXIT`
and the next `@`:

```
Brl: EXIT
OUTBT....30171 U  INBT.....30172 U  8RLDN....30571 U  8ENTR....30512 U
Brl message: Undefined entries
```

The number is the address in the program that refers to the name. **[SEEN]** Use it to find which
`LOAD`ed unit made the reference: the program's units are laid out in load order, so the address
falls inside one unit's range (the `FREE: P` lines show where each one ended).

### Q. How do I see what a library defines?

```
Brl: LIST-BRF-ENTRIES FTNLIBR-2091F,TERMINAL
```

It prints every unit with its entry names. **[SEEN]** Long lists scroll off a terminal fast and
mix up when the screen is slow. **Write the list to a file instead**: the second argument, in
quotes to create it, works:

```
Brl: LIST-BRF-ENTRIES FORT48-2BANK-F02,"E-F48-2B"
```

That made `E-F48-2B:SYMB` (33 KB). Pull it off the disk image and search it on the host. **[SEEN]**
This is how to answer "does this library define name X": look at the list, do not guess.

### Q. What are `INBT` and `OUTBT`?

SINTRAN monitor calls: `INBT` is call **1B** (read a byte from a device) and `OUTBT` is call
**2B** (write a byte to a device). **[DOC]** ND-860228-2, the monitor call reference. FORTRAN's
`INCH` and `OUTCH` use them (ND-60.145.7A appendix C, note 2). The assembler routine `GETIN`
calls them as subroutines by those names.

Where the *names* come from, checked against the entry list of each library: **[SEEN]**

| Library | `INBT` / `OUTBT` | What it does have |
|---|---|---|
| old runtime `FTNLIBR-2091F` | **defined** (in the unit with `8CNCT`, `8BINI`, `8CONV`) | the `8…` names |
| F02 runtime `FORT48-2BANK-F02` (462 entries) | **not defined** | `INCH`, `OUTCH`, `MON1`, `MON2`, `MON3`, … (a routine per monitor call), `5ENTR`, `5ERET`, `5LEAV` |
| monitor-call package ND-210913 (`MON-CALL-2B-A00`) | not defined. Loading it changed nothing | |

So F02 programs reach the same calls under other names: `INCH` / `OUTCH` for characters, or
`MON1` / `MON2` for the raw monitor calls. **Or you add the old runtime last:** linking
`FTNLIBR-2091F` after the F02 runtime made every one of the five undefined names resolve, and the
linker ended with no `Undefined entries` message. **[SEEN]** See "Does the old library fix it?"
below for what happened when the program then ran.

**To find out who defines a name, do not guess: look it up.** The catalog
[LINK-LIBRARY-NAME-INDEX.md](../../Workflow/LINK-LIBRARY-NAME-INDEX.md) lists, for every name in
every `:BRF` library on the archive floppies, the libraries that define it. For example `8ENTR`:
`FTNLIBR-2091F`, `FTNLIBR-2093F`, `FTNRTLIBR-2092F`, `FTNRTLIBR-2094F`, `EXTRA-PAS-LIB`,
`EXTRA-PASLIB-PBL`. `STAT` is in no library (it is a routine in the program itself,
`ADV-STAT:SYMB`). The full per-library lists are in
[LINK-LIBRARY-ENTRY-POINTS.md](../../Workflow/LINK-LIBRARY-ENTRY-POINTS.md).

### Q. Does the old library fix it? What happens when the program runs?

Linking the F02 objects with `FORT48-2BANK-F02` and then `FTNLIBR-2091F` gave a clean link and a
`:PROG` of 233,472 bytes. **[SEEN]** Running it, **[SEEN]**:

1. It prints `?` and waits. That is the `OPEN` helper asking for the database name.
2. `ADV-DATA` gave `NO SUCH FILE NAME`. The helper wants the **type** too: `ADV-DATA:SYMB` was accepted.
3. Then it went quiet. **That was not a fault: the program was waiting for three more answers**
   (a key, the magic word and the magic number, none of them echoed and none with a prompt).
   Pressing Enter gave the number question an empty answer and the game's own fatal-error text
   appeared: `FORTRAN EXCEPTION: (412B) BAD CHARACTER ON INPUT "j" IN LINE 331`, followed by
   "Fatal error, contact Adventure system manager ... Please report this number: 5".

**Correction.** An earlier version of this page said the program had read the terminal instead of
the database because the assembler helpers use the old calling convention, and suggested the
`ASSEMBLY` statement as the fix. **That reading was wrong.** Line 331 is `READ(INP,*) MAGNM`, a
terminal read that belongs to the setup. The full story is in
[ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md).

What the F02 two-bank build really ran into was different and is also recorded there: the helpers
are one-bank code (`Mixed one/two bank routines`), the saved game then stopped with
`ILLEGAL PARAMETER`, and a one-bank F02 build does not fit in 64K (`Program space exceeded`).
The build that works is the original one: FTN-2090I, `FTNLIBR`, one bank.

The `ASSEMBLY` statement and `RESERVE-WORK-SPACE` are real F02 features for calling MAC, NPL and
PLANC routines (ND-60.145.7A section 3.10, 14.27 and appendix F). They were not needed here, and
`RESERVE-WORK-SPACE ON` did not change the result when tried.

### Q. What are the `8…` and `5…` names?

The two runtimes have different internal entry names.

| | Old runtime (FTN-2090) | F02 runtime |
|---|---|---|
| Enter/leave a routine | `8ENTR`, `8LEAV` | `5ENTR`, `5ERET`, `5LEAV` |
| Start up | | `5INIT`, `1BANK`, `5PGTB` |
| Fatal error, quit | `8ERR` | `5FATA`, `5QUIT`, `5MSG` |
| Terminal characters | `INBT`, `OUTBT` (in `8CNCT`) | `INCH`, `OUTCH`, `MON1`, `MON2` |

**[SEEN]** from `LIST-BRF-ENTRIES` on both. A routine compiled by one compiler refers to its own
runtime's names, so **objects from the two compilers do not mix freely.** Recompile everything
you can with F02. I recompiled `ADV-STAT` this way and its `8LEAV` reference disappeared.

### Q. What are the helper files `ADV-8ERR`, `ADV-OPEN`, `ADV-XOR`, `ADV-EXIT`?

Assembler (MAC) helpers that came with the Norwegian game. `ADV-8ERR` is the important one: it
**replaces the old runtime's own error routine** (it exports the name `8ERR`) and uses the old
runtime's private cell `8RLDN` and routine `8LEAV`. It only makes sense with the old runtime.
**[SEEN]** (source read)

They go with the old runtime and one bank, which is what the working build uses. With F02 they
would have to be rewritten for the F02 runtime and for two banks; that was not done.

### Q. A program line given to the linker is cut off.

Terminal input lines are limited to about 79 characters. A long `LOAD a b c d ...` line was cut
in the middle of a name, and the next command was glued onto it (`AEXIT`: `NO SUCH FILE NAME`).
Send shorter lines. **[SEEN]**

### Q. Does `LOAD` take several names on one line?

Yes: `LOAD ADV-8ERR ADV-STAT FORT48-2BANK-F02` worked. **[SEEN]** Mind the line length above.

### Q. Can the compiler link too?

The F77 manual says yes: `PROG-FILE name`, then `COMPILE`, then `LOAD` more files, and `EXIT`
completes the program by loading the FORTRAN library (1-bank or 2-bank depending on
`SEPARATE-DATA`). **[DOC]** ND-60.145.7A section 14.5.4. **[NOT RUN]**

---

## 4. Assembler and NPL helpers

### Q. How do I get a `:BRF` from NPL source?

Two steps: NPL makes MAC source, MAC makes the `:BRF`. **[SEEN]**

```
@NPL
@DEV ADV-GETIN,0,"ADV-GETIN:MAC"
- END OF COMPILATION
0 ERRORS DETECTED
@MAC-1628C
)9ASSM ADV-GETIN:MAC,0,"ADV-GETIN:BRF"
 **** 000000 DIAGNOSTICS ****
)9EXIT
```

Notes: `@DEV` is typed to NPL (NPL's own prompt shows nothing, it just waits), and NPL leaves by
itself when it has compiled. `MAC` is not a registered name on a bare pack, but `MAC-1628C` is a
plain `:PROG` in `(SYSTEM)` and runs by that name. NPL must be dumped first:
`DUMP-REENTRANT NPL,0,1,(BPUN-FILES)NPL-1896D:BPUN`. **[SEEN]**

---

## 5. Working on the machine

### Q. At the `@` prompt, do I type the `@`?

No. `@` is the prompt. Typing a second `@` gives a silent empty answer, and every command seems
to do nothing. **Inside a MODE file the `@` is part of each line.** Lines meant for a program
(compiler, linker) have none. **[SEEN]**

### Q. I log in on a terminal and get `SYSTEM UNAVAILABLE`.

After a boot only the console may log in. Log in at the console as `SYSTEM` with a blank password
and type `SET-AVAILABLE`. Then the other terminals work. **[SEEN]**

### Q. `LIST-FILES` printed nothing, or asks `OUTPUT FILE:`.

Press Enter at `OUTPUT FILE:` to list on the terminal. If a list shows nothing at all, check you
did not type the extra `@`. **[SEEN]**

### Q. Do I need `GIVE-USER-SPACE` for a new user?

If you create the user offline with `ndtool --useradd NAME 1000`, the 1000 pages are reserved
already; the listing shows `Reserved: 1000`. From SINTRAN use `@GIVE-USER-SPACE name,pages`
as SYSTEM. **[SEEN]** (offline) **[DOC]** (SINTRAN).

### Q. How do I put files on the disk image?

With the machine **stopped**:

1. Copy the image first (`cp SMD0.IMG SMD0.IMG.before-x`).
2. `ndtool --useradd ADV-ENG 1000 SMD0.IMG` for a new user.
3. `ndtool --put host-file "ADV-ENG/ADV-HOVED:SYMB" SMD0.IMG`. Use the original `NAME:TYPE`.
4. For files with holes, or to change bytes, use the ndfs Python library.
5. Read it back and compare. Run `ndtool --fsck`.

Source text on the pack has **even parity** in bit 7. When you edit a line on the host, write it
back with parity (bit 7 set only when the low 7 bits hold an odd number of ones). Copy untouched
files byte for byte. **[SEEN]**

### Q. `ndtool --fsck` shows warnings. Is the image damaged?

The warnings here are `pages_used=N but actual file pages=M`, a few pages off, for most users. They
were there before any change of mine (7), and one more user appears once a program has written
files (8). 0 errors. **[SEEN]**

### Q. How do I drive the emulator with no screen?

`nd100x` needs `--debugger` to give you the console. Steps that worked **[SEEN]**:

1. Start `nd100x --boot=smd0 --smd0=SMD0.IMG --telnet=9101 --debugger --port=4712`.
2. Connect a DAP client to port 4712, enable console capture, then `attach` **without pausing**.
3. Wait about 50 seconds for SINTRAN. Output only arrives when you call `continue` or read.
4. Type at the console with **hex** (`1B` for ESC, `0D` for Enter). The text form with `\r` did not work for the console.
5. Log in as `SYSTEM`, blank password, then `SET-AVAILABLE`.
6. Telnet to 9101, pick a terminal in the menu, press ESC, log in.

The menu numbers did not always match: choosing `2` landed on `Terminal 39`. Wait for the menu to
draw before sending your choice. Stop your own emulator by its process id when you are done.

---

## 5b. Programs that set up their own data (save the "core image")

### Q. The program says "Be sure to save your core image..." What is that?

The program has read its data into its own tables and has stopped with the memory filled in. It
expects you to save that memory as a new `:PROG`, so the next run starts with the data already in
place. In SINTRAN that is:

```
@MEMORY 0,177777
@DUMP "NAME",0,0
```

`@DUMP <file>,<start>,<restart>` saves the user's virtual memory on a `:PROG` file (ND-60.128.5).
The range must cover everything, including the COMMON area at the **top** of a one-bank program.
Start and restart 0 match a known-good program. **[SEEN]**

### Q. Can the linker's `RUN` do it?

No. `RUN` inside `BRF-LINKER-C01` starts the program, and the program's setup ends the whole
session, so the memory is gone before you can save it. Run the linked `:PROG` from SINTRAN and
`@DUMP` afterwards. **[SEEN]**

### Q. Can I put the setup answers in a MODE file?

Not for this program: the helper that reads the database name reads the terminal itself. A MODE
file that started the program and supplied the answers aborted with `ILLEGAL COMMAND`. **[SEEN]**

### Q. How do I know the dump worked?

Run it by name: it must go straight to the game and not ask for the database. Its size is the
size of the memory range (64K words plus a header page, 131,584 bytes). The header words, read as
7 big-endian 16-bit words, give start, restart and the bank limits (see
[PROG-FILE-FORMAT.md](../../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)). **[SEEN]**

### Q. `ndtool --rm` seems to hang.

It asks `Delete ...? [y/N]` and waits. Pipe an answer: `echo y | ndtool --rm "USER/FILE:TYPE" image`.
A background command waiting on that prompt looks like a hang. **[SEEN]**

---

## 6. Open items

- **The English Adventure is built and works** (compile, link, setup, saved as `ADVENTURE:PROG`,
  wizard login tested). See [ADVENTURE-BUILD-AND-INITIALIZE.md](ADVENTURE-BUILD-AND-INITIALIZE.md).
  The build uses FTN-2090I and the old runtime; the source needed nine small edits.
- Not known: which compiler revision built the original game. Both archive revisions (H and I)
  reject `LOGICAL FUNCTION` followed by `IMPLICIT INTEGER (A-Z)`; the fix is a later `LOGICAL name`
  declaration in each routine.
- The setup step cannot be run from a MODE file (the `OPEN` helper reads the terminal), so the
  build is a MODE file plus a short interactive session.
- Not tested: the F02 two-bank build with rewritten two-bank helpers; the built-in loader
  (`PROG-FILE` inside the F02 compiler).
- 30 of the 378 distinct `:BRF` files on the floppies have units with a failing checksum (see the
  catalog). Some are damaged copies (a good copy of the same file exists), some may hold a group the
  parser reads wrongly, for example C and COBOL runtimes. Not sorted out.

---

**Last Updated:** October 15, 2026
