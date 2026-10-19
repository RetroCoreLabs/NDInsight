# Building and Initializing the Adventure `:PROG` Files

How the English *Adventure* game (FORTRAN source, `ADV-*:SYMB`) was compiled, linked, set up
and saved as a runnable `:PROG` on a SINTRAN III system. Everything here was run on the nd100x
emulator (SINTRAN III VSX/500 L) and the output was read. Things that were not run are marked
**[NOT RUN]**; things taken from a manual or worked out from the sources are marked **[DOC]** or
**[INFERRED]**.

The same method builds the Norwegian original (`SKATT-*`, program `SKATTEJAKT`). That build
itself was not repeated; only its finished program was run for comparison.

---

## 1. The short version

```
Source (13 files, user ADV-ENG)
   | @MODE ADV-BUILD:MODE,,          compile 4 units with FTN-2090I, link with BRF-LINKER
   v
ADVENTURE-RAW:PROG                    a linked program that has NOT read its database yet
   | @ADVENTURE-RAW                   ask for: database, key, magic word, magic number
   |                                  (the program reads the database into its memory)
   | @MEMORY 0,177777
   | @DUMP "ADVENTURE",0,0            save the memory image: the "core image"
   v
ADVENTURE:PROG                        the finished game (131,584 bytes), starts at once
```

Two kinds of `:PROG` are involved. The **raw** program is what the linker makes. The
**initialized** program is the raw one after it has run once, filled its tables from the database
and been saved with `@DUMP`. Only the second one is the game people run. This is why the program
says *"Be sure to save your core image..."* when its setup is done.

---

## 2. The toolchain, and why this one

| Role | File | Where from |
|---|---|---|
| FORTRAN compiler | `FTN-2090I:BPUN`, dumped reentrant as `FTN` | floppy `ND-10023K` (archive id `d5799ff4`) |
| FORTRAN runtime | `FTNLIBR-2091F:BRF` | same floppy |
| Linker | `BRF-LINKER-C01:PROG` | floppy `210721C01-XX-01D` (archive id `68dae73b`) |
| Assembler helpers | `ADV-OPEN`, `ADV-XOR`, `ADV-TR1-TR2`, `ADV-EXIT`, `ADV-8ERR` (`:BRF`) | floppy `NMN-SKATT-NEW (3)` |
| NPL and MAC | `NPL-1896D:BPUN` (dump reentrant), `MAC-1628C:PROG` | on the SMD pack already |

This is the **original** toolchain: the old FORTRAN compiler, the old runtime, one 64K bank. The
known-good Norwegian `SKATTEJAKT:PROG` has exactly this shape: one bank from address 0 to 177777,
start 0, restart 0. **[SEEN]** (header of the file)

### What was tried first, and why it was dropped

| Attempt | Result |
|---|---|
| FTN-2090I on the source as it came | 11 errors in `ADV-SUBR`: `"LOG. EXPR" ILL. ASSIGNMENT` on `LOGICAL FUNCTION` routines. Fixed in the source, see section 4 |
| FTN-2090H (older compiler) | the same errors |
| F02 compiler (ND-210191F02), two banks | compiles with one real error. Links and runs, but the assembler helpers were written for **one** bank (the linker says `Mixed one/two bank routines`), and the game stops with `ILLEGAL PARAMETER` after the first question |
| F02 compiler, one bank | the linker says `Program space exceeded` loading the F02 runtime: it needs about 14,000 words and only about 6,500 are left in a 64K program (the game's COMMON area alone is 41,172 words) |
| F02 objects plus the old `FTNLIBR` | resolves all names and the game starts, but it is the two-bank layout again |

The F02 compiler is the better compiler for new FORTRAN programs (see
[FORTRAN-DEVELOPER-GUIDE.md](FORTRAN-DEVELOPER-GUIDE.md)). For *this* program, the old one-bank
toolchain is the one that works, because the helpers and the memory size were made for it.

---

## 3. Preparing the machine

All steps were done on `SMD0.IMG` with the emulator **stopped**, using `ndtool` and the ndfs
Python library, and each copy was read back and compared. Make a backup of the image first.

1. **User.** `ndtool --useradd ADV-ENG 1000 SMD0.IMG` reserves 1000 pages. About 420 are used
   after a full build. No `@GIVE-USER-SPACE` was needed.
2. **Sources.** Put the 13 `ADV-*:SYMB` files in `ADV-ENG`, under their original names, byte for
   byte (they carry even parity in bit 7; do not convert them).
3. **Helper objects.** Put `ADV-OPEN`, `ADV-XOR`, `ADV-TR1-TR2`, `ADV-EXIT`, `ADV-8ERR` `:BRF`
   in `ADV-ENG`. `ADV-GETIN` is NPL source; build it in step 6.
4. **Tools in SYSTEM.** `FTN-2090I:BPUN`, `FTNLIBR-2091F:BRF`, `BRF-LINKER-C01:PROG`. The linker
   file and the F02 compiler are sparse (they have empty pages): copy them with their holes (see
   the FAQ).
5. **Boot** `nd100x --boot=smd0 --smd0=SMD0.IMG --telnet=9101 --debugger --port=4712`. At the
   console (through the debugger port, hex input) log in as `SYSTEM` with a blank password and
   type `SET-AVAILABLE`. Then telnet to port 9101, press ESC, log in as `ADV-ENG`.
6. **Dump the compiler and NPL reentrant**, once, as `SYSTEM`:

   ```
   DUMP-REENTRANT FTN,0,1,FTN-2090I:BPUN
   DUMP-REENTRANT NPL,0,1,(BPUN-FILES)NPL-1896D:BPUN
   ```

   Start 0 and restart 1 come from the program description sheets. The command prints nothing
   when it works. **[SEEN]**

7. **Build `ADV-GETIN`** once (NPL makes MAC source, MAC makes the object). As `ADV-ENG`:

   ```
   NPL
   @DEV ADV-GETIN,0,"ADV-GETIN:MAC"
   MAC-1628C
   )9ASSM ADV-GETIN:MAC,0,"ADV-GETIN:BRF"
   )9EXIT
   ```

   Expect `0 ERRORS DETECTED` and `**** 000000 DIAGNOSTICS ****`. **[SEEN]**

At the SINTRAN prompt `@` you type commands **without** the `@`. Inside a MODE file each
SINTRAN command **has** its `@`. See the FAQ.

---

## 4. Changes made to the English source

The source was written for a compiler revision that is not in the archive. Section 4a makes it
compile with FTN-2090I (and with F02). Sections 4b and 4c make two things work as the authors
intended on this machine. No game logic was changed.

### 4a. To compile (9 edits)

**`ADV-HOVED:SYMB`, line 551.** An unclosed `IF`:

```
before: 2611  IF((WD1X.EQ.TXLOCK.AND.WD2X.EQ.TXOPP).AND.(AT(GRATE))WD2X=TXOPEN
after:  2611  IF((WD1X.EQ.TXLOCK.AND.WD2X.EQ.TXOPP).AND.(AT(GRATE)))WD2X=TXOPEN
```

**`ADV-SUBR:SYMB`.** `LOGICAL FUNCTION` followed by `IMPLICIT INTEGER (A-Z)`: FTN-2090 lets
`IMPLICIT` retype the function. The fix declares the function name `LOGICAL` *after* `IMPLICIT`,
the same trick the authors used for `NEWHRX` (typed `INTEGER FUNCTION`, retyped `DOUBLE INTEGER`
inside). Line numbers are those of the original file:

| Line | Routine | Added |
|---|---|---|
| 155 | `YES` | `LOGICAL YES,YESX` (was `LOGICAL YESX`) |
| 166 | `YESM` | `LOGICAL YESM,YESX` |
| after 177 | `YESX` | a new line `LOGICAL YESX` |
| 407 | `START` | `LOGICAL START,PTIME,SOON,YESM,WIZARD` |
| 610 | `WIZARD` | `LOGICAL WIZARD,YESM,BLKLIN` |
| 1108 | `PCESS` | `LOGICAL PCESS,YES` |

`NEWHRX` is **left as the authors wrote it**: `INTEGER FUNCTION NEWHRX(DAY1,DAY2)` with
`DOUBLE INTEGER NHR,NEWHRX` inside. The F02 compiler calls that `DOUBLY DEFINED`; FTN-2090 does
not. If you build with F02, change the function line to `DOUBLE INTEGER FUNCTION NEWHRX(...)` and
drop `NEWHRX` from the inner line.

### 4b. Echo of what you type (9 lines added)

The game turns SINTRAN's echo off (`CALL ECHOM(INP,-1)`; `ECHOM` modes: below 0 no echo, 0 echo
all, 1 echo all but control characters) and sets its own flag `ECHOMODE`. Its comments say the
echo is then done "in INBT routine": a patched `INBT` in the authors' library that read the flag.
The stock `INBT` in `FTNLIBR-2091F` does not, so nothing was echoed. The fix keeps the game's
design and lets SINTRAN do the echo whenever the flag says echo:

| File | Change |
|---|---|
| `ADV-HOVED` (start of the game) | `CALL ECHOM(INP,-1)` becomes `CALL ECHOM(INP,0)` |
| `ADV-INIT` (setup) | same change at the start; after the later `ECHOMODE = 1` add `CALL ECHOM(INP,0)` |
| `ADV-SUBR`, routines `MAINT` and `WIZARD` (6 places) | after every `ECHOMODE = 0` add `CALL ECHOM(INP,-1)`, after every `ECHOMODE = 1` add `CALL ECHOM(INP,0)` |

Result **[SEEN]**: what you type is echoed; the magic word and the wizard challenge answer are
not (the game prints a blank line instead).

### 4c. The log file name (1 edit)

`ADV-STAT:SYMB`: `FILE='(N-M)ADV-USED:DATA'` becomes `FILE='ADV-USED:DATA'`, so the usage log is
in the **current user's own directory** (see section 8b). Create the empty file once in every
user that will play: `@CREATE-FILE ADV-USED:DATA,0`.

When you edit a source file by hand outside SINTRAN, write the new bytes with even parity (bit 7
set when the low 7 bits hold an odd number of ones), keep every line within 72 columns, and
verify with `ndtool --fsck`. The lines above all stay within 71.

---

## 5. Build: one MODE file

`ADV-BUILD:MODE`, in user `ADV-ENG`. Each compile starts a fresh compiler session and leaves it
(`EX`), so nothing carries over from the previous unit:

```mode
@DELETE-FILE ADV-HOVED:BRF
@DELETE-FILE ADV-INIT:BRF
@DELETE-FILE ADV-SUBR:BRF
@DELETE-FILE ADV-STAT:BRF
@DELETE-FILE ADVENTURE-RAW:PROG
@FTN
COMP ADV-HOVED,,"ADV-HOVED"
EX
@FTN
COMP ADV-INIT,,"ADV-INIT"
EX
@FTN
COMP ADV-SUBR,,"ADV-SUBR"
EX
@FTN
COMP ADV-STAT,,"ADV-STAT"
EX
@BRF-LINKER-C01
PROG-FILE "ADVENTURE-RAW"
LOAD ADV-HOVED ADV-INIT ADV-SUBR
LOAD ADV-OPEN ADV-XOR ADV-TR1-TR2 ADV-EXIT
LOAD ADV-GETIN ADV-8ERR ADV-STAT
LOAD FTNLIBR-2091F
LIST-ENTRIES-UNDEFINED
EXIT
```

Run it with `@MODE ADV-BUILD:MODE,,`. **[SEEN]** Delete the old objects first: the compiler
stops with `FILE ALREADY EXISTS` otherwise, and a failed compile can leave an empty object that
you would then link by mistake.

What a good build looks like **[SEEN]**:

- every compile ends with `N LINES COMPILED .` and no diagnostics (HOVED 2016 lines, INIT 773,
  SUBR 1152, STAT 27);
- each `LOAD` prints the free program space; the last line is `FREE: P 055770-057450`. The first
  number is where code ends, the second where the COMMON area begins. There are about 800 words
  to spare, so **this program is close to the 64K limit**;
- **no** `Mixed one/two bank routines` and **no** `Undefined entries`. `LIST-ENTRIES-UNDEFINED`
  printing nothing means the link is complete.

Names and sizes (bytes): `ADV-HOVED:BRF` 42,756; `ADV-INIT:BRF` 13,313; `ADV-SUBR:BRF`
18,098; `ADV-STAT:BRF` 917; `ADV-GETIN:BRF` 983; `ADVENTURE-RAW:PROG` 61,440.

---

## 6. Initialize

This step **cannot** be done from a MODE file. The program's `OPEN` helper reads the database
name from the terminal itself, not from the MODE input; a MODE file with the answers was tried
and the batch aborted with `ILLEGAL COMMAND`. Do it by hand:

```
@ADVENTURE-RAW
?                          <- the program asks for the database; no other prompt
ADV-DATA:SYMB              <- name AND type; plain ADV-DATA gives NO SUCH FILE NAME
ABCDEF                     <- key: 6 letters, not echoed, scrambles the stored magic word
LURVEN                     <- the magic word (the wizard password), not echoed
11111                      <- the magic number, not echoed
```

Then it reads the database (about 4 seconds) and prints the table usage and:

```
Table space used:
 11607 of 11700 words of messages
   870 of   900 travel options
   333 of   400 vocabulary words
   184 of   200 locations
    74 of   100 objects
    36 of    40 action verbs
   245 of   250 RTEXT messages
    11 of    13 class messages
    11 of    20 hints
    37 of    50 magic messages

Initialization finished!
Be sure to save your core image...
@
```

Notes:

- **Do not press Enter while it waits.** Empty input to the number question makes the program stop
  with `BAD CHARACTER ON INPUT` and a fatal-error text; a stray ESC aborts the run and your next
  answers are taken as SINTRAN commands.
- **Which values?** `LURVEN` and `11111` are the values of the original (`SKATTEJAKT:PROG`
  carries `11111`). The key only scrambles the stored word, so any 6 letters work; the original
  key is not known.
- **Message usage is 11607 of 11700** (after message 37 was added; it was 11599 before): the English database is almost full. Adding text means
  raising the limits in the source.

The setup is in `ADV-INIT:SYMB`: after `DBNR = OPEN(SEQRD)` it reads `XORKEY`, `MAGIC` (scrambled
with `XOR`) and `MAGNM`, then the database sections. `ADV-HOVED` calls `INIT` only while `SETUP`
is 0.

---

## 7. Save the core image

Still in the same session, with the program stopped in memory:

```
@MEMORY 0,177777
@DUMP "ADVENTURE",0,0
```

`@DUMP <file>,<start>,<restart>` saves the user's memory to a `:PROG` (ND-60.128.5; read it back
later with `@RECOVER`, or run the file by name). The memory range matters: the database lives in
the COMMON area at the **top** of the 64K space, so the range must reach 177777. Start and restart
0 match the known-good program.

Check **[SEEN]**: `ADVENTURE:PROG` is **131,584 bytes**, the same size as `SKATTEJAKT:PROG`;
header words (octal): start 0, restart 0, bank 1 from 0 to 177777, no second bank. The raw
program, for comparison, is 61,440 bytes with bank 1 ending at 072750.

Do not start another program (the linker, a compiler) between the setup and the `@DUMP`: it
would overwrite the memory you want to save.

---

## 8. Verify

```
@ADVENTURE
NO ACCOUNT-FILE!
Welcome to Adventure!!  Would you like instructions?
```

If you see `NO ACCOUNT-FILE!` first, the user has no `ADV-USED:DATA` file: create it with
`@CREATE-FILE ADV-USED:DATA,0` (see [section 8b](#8b-the-account-file-adv-useddata)). It is
harmless otherwise.

Answer `NO` and the first room appears: *"You are standing at the end of a road before a small
brick building..."*.

**Wizard login** (a good test that the saved values are right). At the first move type
`MAGIC MODE`. **[SEEN]** with `MAGIC`=`LURVEN`, `MAGNM`=`11111`:

| The game says | You type |
|---|---|
| `Are you a wizard?` | `YES` |
| `Prove it!  Say the magic word!` | `LURVEN` |
| `That is not what I thought it was.  Do you know what I thought it was?` | `NO` |
| a 5-letter challenge, here `QNGMH` | the decoded answer, here `RMHLI` |
| `Oh dear, you really *ARE* a wizard!  Sorry to have bothered you . . .` | |

**Decoding the challenge** (worked out from `LOGICAL FUNCTION WIZARD` in `ADV-SUBR:SYMB`, lines
601-691, and matching the cheat sheet that came with the task): the answer letters are the
challenge letters shifted by the decimal digits of `MAGNM`, taken from the last letter backwards,
with alternating signs; for `11111` that is `+1 -1 +1 -1 +1` from letter 1 to letter 5.
The game's hour is `MOD(hour,3)` (0, 1 or 2) and is subtracted from the last letter. Z+1 = A and
A-1 = Z. Example: `QNGMH`, hour 09 (value 0): Q+1=R, N-1=M, G+1=H, M-1=L, H+1-0=I, so `RMHLI`.
The hour is the game's clock (SINTRAN's), not your computer's.

---

## 8b. The account file `ADV-USED:DATA`

Read from `ADV-STAT:SYMB` (27 lines). No real log file was found on any of the 349 NDFS disk
images or in the archive, so this is read from the source, not from an example. **[INFERRED]**
where marked.

**Where.** In the original the name is hard-coded:
`OPEN (UNIT=10,FILE='(N-M)ADV-USED:DATA',ACCESS='WA',ERR=99)`. **This build uses
`FILE='ADV-USED:DATA'`** (section 4c), i.e. the file in the current user's directory; the
discussion below explains the difference.
`(N-M)` is a SINTRAN user name; it appears nowhere else in the sources. The game's own error
message names "Nils-Morten Nilssen", so `N-M` is probably his initials **[INFERRED]**. The user
must exist and the file must exist: `ACCESS='WA'` appends to an existing file and does not
create one, which is why a missing file gives `NO ACCOUNT-FILE!`.

**What a line holds.** One line, written by `STAT` with this format:

```
TERM :ttt USER :uuu DATO :yyyy mmmm dddd TID :hhhh mmmm ssss tttt USED :nnnnn MIN.
```

| Field | Value | Where from |
|---|---|---|
| `TERM` | the player's input device (SINTRAN logical device number of the terminal) | `RSIO`, parameter 2 |
| `USER` | the player's user number | `RSIO`, parameter 4 |
| `DATO` | year, month, day | `CLOCK` elements 7, 6, 5 |
| `TID` | hour, minute, second, basic time units | `CLOCK` elements 4, 3, 2, 1 |
| `USED` | minutes: `(minute diff) + (hour diff)*60 + (day diff)*24*60` | `CLOCK` now minus the saved time |

No player name, no score, no answers. `CLOCK` order: basic time units, seconds, minutes, hours,
day, month, year (monitor call 113B, ND-60.228 / `ND MON Calls.md`). The minute count ignores the
month, so a game that crosses a month change gives a wrong number. `DESCF(0)` and `EESCF(0)`
around the write switch the player's ESCAPE key off and on, so the file is not left half
written if someone presses ESC.

**Shared or not.** The log is an **accounting file for the game's manager** (the error text says
to contact "the Adventure system manager"). It is only useful if every game, from every user,
lands in the **same** file. That is what the fixed `(N-M)` is for: one owner, one file, the
manager reads one place. To work, the file needs write and append access for all players and
read access for the manager; nobody should be able to delete it.

If the user part is **removed** from the name (`'ADV-USED:DATA'`), SINTRAN looks in the
*player's own* directory. Then the file must exist in every player's area (the open fails
otherwise, as seen), the entries are scattered, and the manager can read them only with access
to each directory. So a name without a user gives one log per user, not a common log.

Concurrent writers: two players appending in the same moment can in principle lose or mix a line;
the program has no locking. For a log of one short line per game this is a small risk, which the
original accepted. **[INFERRED]**

**When the line is written (a quirk of the saved image).** `STAT` is called at the start and at
the end of a game and keeps `FIRST` to tell which call it is. The setup run calls it once before
`INIT`, so the saved image holds `FIRST` = true. Every later game therefore takes the *end*
branch at its **start**: it opens the file, writes the line (with the date and time of the setup
run and the minutes since then), and the call at the end of the game only stores a new time. This
explains why `NO ACCOUNT-FILE!` appears at the **start** of a game.

**[SEEN]** With the file in place, one game start wrote exactly this one line (terminal 39,
user number 10 = `ADV-ENG`, the date and time of the setup run, 0 minutes since):

```
TERM : 39 USER : 10 DATO :1988  12  16 TID :   9  35  16  40 USED :    0 MIN.
```

So the logged `USED` is "minutes since the setup run" and the real start time is
`DATO`/`TID` plus `USED` minutes. The game end writes nothing. Whether the original behaved the
same is not known. To read the file at the terminal: `@COPY TERM ADV-USED:DATA` (destination
first; with a comma `TERM` is taken as a file name).

---

## 8c. Wizard mode: how to get in, and what it gives

Read from `ADV-HOVED` (line 514), `START` and `MAINT` in `ADV-SUBR`. The login itself was tested;
the maintenance questions were **read from the source**, not all run. **[SEEN]** for the login.

### Two ways in

1. **Maintenance mode.** As the **very first command** of a game (`TURNS = 0`) type `MAGIC MODE`.
   The game asks the login questions in section 8 (`YES`, the magic word, `NO`, the 5-letter
   challenge). A wrong answer gives *"Foo, you are nothing but a charlatan!"* and the game goes on
   as normal. At any later move `MAGIC MODE` does nothing special.
2. **Closed cave.** When the hours say the cave is closed, the game prints the hours and *"Only
   wizards are permitted within the cave right now"* and asks *"Are you a wizard?"* The same
   login lets you play outside the hours. (This is the Norwegian game's opening: the saved
   Norwegian image has weekdays and weekends closed and holidays open, and its text is
   *"Er du en trollmann?"*.) A wizard can also continue a game *"this soon"* after the last
   one, before the restart delay (the latency) has passed.

### What it gives (maintenance mode, in the order asked)

| # | The game asks | Answer YES / a value to |
|---|---|---|
| 1 | Do you wish to read in a new database? *(message 37, added by us, see below)* | **answer NO.** YES re-runs the setup |
| 2 | Do you wish to see the hours? | print the open hours |
| 3 | Do you wish to change the hours? | define "prime time" (the closed hours) as hour numbers, separately for weekdays, weekends and holidays; end with a negative number |
| 4 | Do you wish to (re)schedule the next holiday? | days until it starts, how many days it lasts (0 = none), and its name (up to 24 characters) |
| 5 | Length of short game (null to leave at N) | the number of turns of a short demo game |
| 6 | New magic word (null to leave unchanged) | the wizard password; typed hidden, stored scrambled with the key |
| 7 | New magic number (null to leave unchanged) | the number behind the 5-letter challenge (`11111` now) |
| 8 | Latency for restart (null to leave at N) | minutes before the same user may restart; below 45 is raised to 45 |
| 9 | Do you wish to change the message of the day? | enter a new message of the day. **[INFERRED]** from messages 23 to 25 and 35 to 36: lines of at most 72 characters, ended by an empty line, or read from a file ("Input from file?"). The routine `MOTD` was not read |

Then it prints *"Okay.  You can save this version now."* and stops (`CALL CIAO`).

**The changes live only in the program's memory.** To keep them you must save the core image,
exactly as after the setup: `@MEMORY 0,177777`, delete the old `ADVENTURE:PROG`, then
`@DUMP "ADVENTURE",0,0` (section 7). Leave the game any other way and they are lost.

### A defect in the English database: message 37 was missing (fixed)

`MAINT` starts with `YESM(37,0,0)`. The Norwegian database has message 37 (*"Skal det leses inn ny
database?"*); the English one ended at message 36, so the first question was **silent** and the
game waited for a yes/no. A stray `YES` re-ran the setup (it printed `?` and waited for the
database name). **[SEEN]**

The fix: the line `37,     Do you wish to read in a new database?` is now in `ADV-DATA:SYMB`
(after message 36, before the `-1,` end line). The setup was run again and the game saved; the
table now reads `37 of 50 magic messages` and `11607 of 11700 words of messages`. **[SEEN]**
After the wizard login the game now asks *"Do you wish to read in a new database?"* (answer `NO`),
then *"Do you wish to see the hours?"*. **[SEEN]** The finished `adventure.prog` in the export
folder includes this fix. The rest of the menu (hours, holiday, magic word, message of the day)
was not run through. **[NOT RUN]**

---

## 9. What went wrong on the way (so you can recognize it)

| What you see | Cause |
|---|---|
| `** FTN ERR ... "LOG. EXPR" ILL. ASSIGNMENT` | `LOGICAL FUNCTION` retyped by `IMPLICIT`; fix in section 4 |
| `... 'T(GRATE)) ? WD2X=TXOP', ')' ASSUMED` (F02) | the missing `)` on line 551 |
| `FILE ALREADY EXISTS` from the compiler | delete the old `:BRF` first |
| `Brl message: No program-file specified` | `PROG-FILE` must come before the first `LOAD` |
| `Brl message: Program space exceeded` | the F02 runtime does not fit in one bank with this program |
| `Brl message: Mixed one/two bank routines` | one-bank helpers loaded into a two-bank program |
| nothing you type is shown inside the game | the game switched SINTRAN's echo off and expects a patched `INBT`; apply the echo edits in section 4b |
| `NO ACCOUNT-FILE!` at the start | the user has no `ADV-USED:DATA`: `@CREATE-FILE ADV-USED:DATA,0` |
| `Undefined entries` list | names no loaded library defines; look them up in [LINK-LIBRARY-NAME-INDEX.md](../../Workflow/LINK-LIBRARY-NAME-INDEX.md). The linker writes the `:PROG` anyway |
| `?` and then silence | the program is waiting for the database name, key, magic word and number; it prints no prompt for the last three |
| `NO SUCH FILE NAME` after the database name | give the type: `ADV-DATA:SYMB` |
| `FORTRAN EXCEPTION: (412B) BAD CHARACTER ON INPUT` | an empty or wrong answer to the magic-number question |
| game starts, then `ILLEGAL PARAMETER` | two-bank build with one-bank helpers |
| `ILLEGAL CHARACTER IN PARAMETER` / `ILLEGAL COMMAND` at the answers | the answers were typed to SINTRAN: the program was not waiting (or the batch was feeding them) |
| a long `LOAD` line is cut in the middle of a name | terminal input lines are limited to about 79 characters |
| the dump does not start the game directly (asks `?` again) | the setup was not completed before `@DUMP`, or the linker ran in between |

---

## 10. Re-initialize

To change the key, magic word or magic number, or the database text: edit, rebuild with
`ADV-BUILD:MODE` (it makes a new `ADVENTURE-RAW:PROG`), repeat section 6, then
`@DELETE-FILE ADVENTURE:PROG` and section 7. The old `ADVENTURE:PROG` must be deleted first:
`@DUMP "ADVENTURE",...` creates the file and will not overwrite.

---

## 11. Files

The finished files (patched sources, build file, objects, both programs, the database) were
exported outside this repository, together with a list of every source change. The disk copy is `SMD0.IMG`, user
`ADV-ENG`, in the nd100x repository (backups beside it as `SMD0.IMG.pre-*`).

Not done: the Norwegian game itself was not rebuilt; its sources (`SKATT-*`) show the same
structure and load order (`SKATT-LOAD:SYMB`). `ADV-COMP:SYMB`, the original build file for the
helpers, was not used: the helper objects came ready-made from the floppy, and `ADV-GETIN` was
built by hand (section 3, step 7). The `ADV-XOR` and `ADV-EXIT` objects already carry their final
names (the original comments mention renaming `XXOR` and `EXI` with the BRF editor).

---

**See also:** [FORTRAN-DEVELOPER-GUIDE.md](FORTRAN-DEVELOPER-GUIDE.md) ·
[FORTRAN-BUILD-LEARNINGS-FAQ.md](FORTRAN-BUILD-LEARNINGS-FAQ.md) ·
[LINK-LIBRARY-ENTRY-POINTS.md](../../Workflow/LINK-LIBRARY-ENTRY-POINTS.md) ·
[PROG-FILE-FORMAT.md](../../../SINTRAN/File-Formats/PROG-FILE-FORMAT.md)
