# C on the ND-500 / ND-5000 with the NC compiler

The NC compiler announces itself as `Norsk Data C - Version: A06 - 1989-01-10`. It is a command shell
(prompt `NC:`) in front of a separate code generator, `CAT-CAT5-B06`. The output is a relocatable `:NRF`
object, which the ND Linker turns into a domain - see
[ND-LINKER-PRACTICAL-GUIDE.md](ND-LINKER-PRACTICAL-GUIDE.md).

The evidence tags ([measured], [NC help], [manual], [unknown]) are explained in [README.md](README.md).

**There is no NC manual in this repository.** The C manual that is here,
[ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual](../../Reference-Manuals/ND-60.214.01%20CC-100%20and%20CC-500%20C-Compiler%20User%20Manual.md),
describes CC-500 from 1984, a different compiler made by the University of Lulea and IAR Systems. Its
command line, its libraries (`CC-HEADER`, `CC-LIBRARY`) and its include directory (`C-INCLUDE`) do not
apply to NC. It is still the reference for the language level: C as in Kernighan and Ritchie, 1978.

## 1. Before the first compile

On the pack, under user SYSTEM: `NC-A06:DOM`, `CAT-CAT5-B06:DOM`, and for linking `NC-LIB:NRF`,
`CAT-LIB:NRF` and the auto job files (list in [README.md](README.md)).

Once per cold start, at the `ND-5000:` prompt [measured]:

```
DEFINE-STANDARD-DOMAIN CAT-CAT5-B,CAT-CAT5-B06
DEFINE-STANDARD-DOMAIN NC-A,NC-A06
```

NC hands the bare command `CAT-CAT5-B` to SINTRAN to start its code generator, and a bare name starts an
ND-500 domain only when it is a standard domain. Without the definitions `CHECK` passes its three phases
and then prints `""` and `AMBIGUOUS FILE NAME`; no object file is written, and `EXIT` ends in
`protection violation` [measured]. `LIST-STANDARD-DOMAINS` shows the definitions:

```
CAT-CAT5-B          (Standard domain is initialized)
    Program segment   1 : (PACK-ONE:SYSTEM)CAT-CAT5-B06:DOM;1
    Data    segment   1 : (PACK-ONE:SYSTEM)CAT-CAT5-B06:DOM;1
```

The command is described in the
[SINTRAN III Reference Manual](../../Reference-Manuals/ND-60.128.5%20EN%20SINTRAN%20III%20Reference%20Manual.md)
and the [ND-500 Loader Monitor manual](../../Reference-Manuals/ND-60.136.04A%20ND-500%20Loader%20Monitor.md).

## 2. Source files

- File type `:C`. Lines end in CR LF. Plain 7-bit ASCII is accepted [measured]. Lines ending in LF
  alone also compile [measured 05-OCT-2026 under real SINTRAN: a source with LF-only line ends gave
  `no errors detected` and an object containing the program's string].
- Give NC the bare SINTRAN name: `HELLO`, not `HELLO.C`. NC adds the type itself: source `:C`, listing
  `:LIST`, object `:NRF`, intermediate `:CAT`, include `:H` [measured].
- NC accepts only the K&R function form. An ANSI prototype definition (`int f(int a, int b) { ... }`)
  gives `*ERROR* error in SUFFIXED_DECLARATOR` and `error in PARAMETER_LIST` in the listing, with
  `2 errors detected` [measured 05-OCT-2026]. Write `f(a, b) int a, b; { ... }`.

```c
main(argc, argv)
int argc;
char *argv[];
{
    printf("argc %d\n", argc);
}
```

### Data sizes [measured with sizeof]

| char | short | int | long | float | double | pointer |
|---|---|---|---|---|---|---|
| 1 | 2 | 4 | 4 | 4 | 8 | 4 |

### Predefined macros [measured with #ifdef]

`ND500` and `SIN3` are defined. The compiler binary also contains `#define nd500 1`; not tested.

## 3. Starting NC

- At the monitor prompt: `ND-5000: NC-A06`.
- At the SINTRAN prompt, once the standard domain is defined: `@NC-A` [measured].

NC prints its banner and `NC:`. After `EXIT` the terminal is at the SINTRAN prompt `@`, not at
`ND-5000:`, even when NC was started from the monitor [measured in three sessions]. Type `ND-500` again
to continue there.

`CROSS MAIN2,XREF2,60` and `FORMAT MAIN2,MAIN2F` were each tried with the output files created first
[measured 05-OCT-2026]: both printed `""` and `AMBIGUOUS FILE NAME`. The cause was not found, so these two
commands are not usable as written here.

## 4. The commands [NC help]

This is the complete list NC printed for `HELP`:

```
cc
help <command: >
exit
preprocess <source file: >,[<list file: >],[<output file: >]
check <source file: >,[<list file: >],[<CAT file: >]
generate-code <CAT file: >,<object file: >
compile <source file: >,<list file: >,<object file: >
link <source file: >,<program: >
cross <source file: >,<cross reference file: >,<lines per page: >
format <source file: >,<new source file: >
value <definitions / options / libraries: >
define [<macro identifier [(identifier,...)]: >],[<value: >]
undef [<macro identifier: >]
directory [<include directory/user: >]
options <option: >...
page-length [<lines: >]
library <library file: >...
initialize-compile-parameters [<initialization file: >]
save-compile-parameters [<initialization file: >]
clear
@<SINTRAN-command>
```

`HELP DEFINE` lists nine more commands that begin with `define-`: `define-nd-500-back-end`,
`define-nd-100-back-end`, `define-68000-back-end`, `define-32000-back-end`, `define-80386-back-end`,
`define-cross`, `define-cat-copy`, `define-optimizer` and `define-user-interface`, each with the
parameter `<program or domain: >...`. What they do is [unknown].

Not run, so their behaviour is [unknown]: `link`, `library`, `cc`, `undef`,
`page-length`, `initialize-compile-parameters`, `save-compile-parameters`.

## 5. Compiling [measured]

One command does everything:

```
NC: COMPILE HELLO,"HELLO","HELLO"
preprocessing   : ok
syntax check    : ok
semantic check  : ok
code generation : ok
```

The same in two steps, keeping the intermediate file:

```
NC: CHECK HELLO,HELLO,HELLO
preprocessing   : ok
syntax check    : ok
semantic check  : ok
NC: GENERATE-CODE HELLO,HELLO
code generation : ok
```

A name in double quotes is created by SINTRAN: `"HELLO"` made `HELLO:LIST` and `HELLO:NRF`. A name
without quotes must already exist; create it at the SINTRAN prompt with `@CREATE-FILE HELLO:NRF,0`.

`PREPROCESS HELLO,,` prints the preprocessed source on the terminal. It is the quick way to check macros
and include files without generating code.

A clean listing file holds the compiler banner, the date and `***  no errors detected  ***`.

### Diagnostics [measured]

A preprocessor error is printed on the terminal in full:

```
pre-processing  : errors detected
nc: messages for "INC3:c"
******   c o m p i l a t i o n   s u m m a r y   ******
*FILE*    (PACK-ONE:SYSTEM)INC3:C;1
    1. #include <mydefs.h>
       ^
*ERROR*   at m.1    Pre-Processor: can't find include file  "mydefs.h"
***   1 error  detected  ***
```

A syntax error under `COMPILE` prints only `syntax check    : errors detected` on the terminal. The
details are in the `:LIST` file, which shows the source line, a caret under the error, the message and
the total. Example for a line `x = ;` [measured 05-OCT-2026]:

```
    4.     x = ;
               ^
*ERROR*   at m.4    error in ASSIGN_EXPR
*MESSAGE*           ;               deleted

***   1 error  detected  ***
```

The terminal does not show this text; read the `:LIST` file on the pack or extract it with `ndtool`.

## 6. Options [NC help]

`VALUE`, answered with `OPTIONS`, printed this before anything had been changed:

| Setting | Code | Setting | Code |
|---|---|---|---|
| target machine is ND-500 | `m2` | without subrange check | `s-` |
| 4 byte record alignment | `a4` | without pointer check | `p-` |
| double arith. for floats | `f-` | without index check | `i-` |
| 64 bit real | `r4` | without overflow check | `o-` |
| with line numbers | `l+` | without profiling | `pr-` |
| with symbolic debug | `d+` | externals as common | `ic+` |
| with procedure names | `n+` | with library mode | `lm+` |
| without trace | `t-` | without complete listing | `a-` |
| with local optimization | `lo+` | page length is 48 lines | |

They are set with `OPTIONS <option>...`. The effect of changing an option has not been measured.

## 7. Macros from the command level [measured]

```
NC: DEFINE DEBUG
value : 1
NC: VALUE
definitions / options / libraries: DEFINITIONS
definitions :
   define DEBUG 1
```

`DEFINE DEBUG,1` typed on one line still asked for `value :`. `CLEAR` resets the compile parameters
[NC help].

## 8. Include files

### There are no vendor header files

No `STDIO:H`, `CTYPE:H` or other NC header file has been found: not in this repository, not on the
media it was built from, not on the pack [searched 5 October 2026]. The header list in the CC-500 manual
(section 1.2) belongs to CC-500. Section 9 shows how to use the C library without headers.

### How NC finds an include file [all measured with PREPROCESS]

| Directive | Result |
|---|---|
| `#include "mydefs.h"` | finds `MYDEFS:H` of the current user; `.h` becomes file type `:H` |
| `#include "MYDEFS:H"` | the same file, written the SINTRAN way |
| `#include "mydefs"` | the same file; `:H` is the default type |
| `#include "(RONNY)MYDEFS2:H"` | a file of another user, named in full |
| `#include <mydefs.h>` | **fails** with `can't find include file` until an include directory is set |

The angle-bracket form looks only in the include directory, and that is empty until it is set:

```
NC: DIRECTORY RONNY
```

After this `#include <mydefs2.h>` finds `(RONNY)MYDEFS2:H`, and `VALUE` -> `DEFINITIONS` shows
`directory RONNY`. The file must be readable for the compiling user: public read access, or the user
must be the owner or a friend.

A practical arrangement: keep a project's shared headers under one user, give them public read access,
give `DIRECTORY <that user>` at the start of each NC session, and use `<name.h>` for the shared headers
and `"name.h"` for headers beside the source.

### Traps

- **SINTRAN abbreviates file names, and NC inherits that.** With `DIRECTORY RONNY`,
  `#include <mydefs.h>` picked up `(RONNY)MYDEFS2:H` without any message, because `MYDEFS` is an
  unambiguous abbreviation of `MYDEFS2` under that user. Do not give one header a name that is the
  beginning of another header's name.
- **Do not answer the `DIRECTORY` prompt with an empty line.** After `DIRECTORY` and an empty answer the
  next `COMPILE` ended NC with `string index exceeds length of string` and `program terminated`
  [measured once; that the empty answer caused it is inferred, not isolated].
- The compiler binary contains the text `#directory`, so a directive for the source file may exist;
  not tested [unknown]. Use the `DIRECTORY` command, which was measured.
- The binary has the message `include nesting too deep`; the limit was not reached and is [unknown].

## 9. The C library without header files

The linker's auto job loads `NC-LIB` (the C library; its records are stamped `NC-LIB-A06.FROM.890116`)
and `CAT-LIB` (runtime and mathematics) into every C program. Functions can be called without a header
[measured]: `printf`, `fprintf`, `fopen`, `fclose`, `fgets`, `strlen`, `exit`. The entry names in the
library file also include `sprintf`, `scanf`, `fscanf`, `sscanf`, `malloc`, `free`, `memcpy`, `fputs`
and `errno`; those were not run.

Without `STDIO:H` there is no `FILE`, `NULL` or `EOF`. This worked [measured]:

```c
main()
{
    char *fp;                       /* in place of FILE * */
    char buf[80];
    extern char *fopen();           /* functions that return a pointer are declared */
    extern char *fgets();

    fp = fopen("CTEST:TEXT", "w");
    if (fp == 0) { printf("open for write failed\n"); exit(1); }
    fprintf(fp, "LINE ONE %d\n", 42);
    fclose(fp);

    fp = fopen("CTEST:TEXT", "r");
    if (fp == 0) { printf("open for read failed\n"); exit(2); }
    if (fgets(buf, 80, fp) != 0) printf("read back: %s", buf);
    fclose(fp);
    printf("strlen %d\n", strlen("hello"));
}
```

Output: `read back: LINE ONE 42` and `strlen 5`. `CTEST:TEXT` did not exist before the run, so `fopen`
with `"w"` created it. The name with SINTRAN's create quotes, `"\"CTEST2:TEXT\""`, worked as well.

A project that needs more can carry its own small header with the `extern` declarations it uses and
include it with the quote form.

## 10. Arguments and program end [measured]

`ND-5000: T1 FOO BAR` gave:

```
argc 3
argv[0] = T1
argv[1] = foo
argv[2] = bar
```

The program name arrives as typed in the domain name; the arguments arrive in lower case. With no
arguments `argc` is 1.

When `main` returns, the runtime prints `program <NAME> terminated` with the execution time and the
elapsed time.

Ways to start a linked C program [measured, with a program `A` whose `main` does nothing]:

| Typed | Result |
|---|---|
| `ND-5000: HELLO` - the domain name as a command | runs at once |
| `ND-5000: RECOVER-DOMAIN A` | runs at once |
| `@ND A` or `@ND-500 A` at the SINTRAN prompt | runs at once |
| `ND-5000: PLACE-DOMAIN A` and then `RUN` | **prints nothing and waits.** The C runtime reads its argument line when it starts (monitor call 1B on device 0), and after `RUN` there is none. One carriage return lets it continue to `program A terminated`. |
| `ND-5000: A:DOM` - the file name with its type; also `@ND A:DOM` | runs at once. The simplest form, and it works for a one-letter name |
| `ND-5000: A` | `AMBIGUOUS COMMAND`: a one-letter name is an abbreviation of several monitor commands. Type `A:DOM`. |

## 11. Several source files [measured]

`MAIN2:C`:

```c
extern int add2();
main()
{
    printf("2 + 3 = %d\n", add2(2, 3));
}
```

`ADD2:C`:

```c
int add2(a, b)
int a, b;
{
    return a + b;
}
```

Compile each to its own `:NRF`, then load both in one link session
(`LOAD MAIN2`, `LOAD ADD2`, `CLOSE`). Result: `2 + 3 = 5`. The session is in
[ND-LINKER-PRACTICAL-GUIDE.md](ND-LINKER-PRACTICAL-GUIDE.md).

## 12. Driving NC from a script

Wait for the prompt text before sending each line: `NC:` for commands, `value :` and
`definitions / options / libraries:` for the prompts of `DEFINE` and `VALUE`. A line sent before its
prompt may be lost, so do not send ahead. In the measured runs NC showed `NC:` by itself when started with `NC-A06` after the
standard domains were defined; no leading carriage return was needed.
