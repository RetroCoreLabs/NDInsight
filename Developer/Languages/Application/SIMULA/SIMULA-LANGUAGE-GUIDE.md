# SIMULA language guide (TPH SIMULA, ND-100)

Every language feature, each with a small example. Back to the index: [README.md](README.md).

**How to read the source tags.**

- **[ND]** with a section and page: stated in the ND manual ND-60.092.03 (OCR copy in
  `Reference-Manuals/`).
- **[CB]**: *standard SIMULA, not confirmed in the ND manual.* It comes from the SIMULA Common
  Base Language. The ND manual says TPH SIMULA implements the Common Base and lists only the
  differences (ND-60.092.03 preface p.7 and ch. 1 p.12), so a CB fact should hold, but the ND
  manual does not say it in so many words.

**None of these examples has been compiled.** They are written to the rules in the ND manual and
the Common Base. Keywords are in upper case; the ND compiler treats upper and lower case the same
unless option U is set (ND 3.2, p.20).

---

## 1. The source text

| rule | source |
|---|---|
| Lines are at most 120 characters. Anything past that is ignored. TAB counts as one space. | ND 1.2.2, p.14 |
| A line starting with `%` in column one is a precompiler command (see [SIMULA-COMPILER-AND-RUN.md](SIMULA-COMPILER-AND-RUN.md) section 6). Never start an ordinary line with `%`. A `%` followed by a space is ignored. | ND ch. 2, p.16 |
| Keywords are reserved words; a space is needed between a keyword and a name. | ND ch. 3, p.19 |
| Identifiers: a letter, then letters, digits and `_`. Up to 72 characters, all significant. Underscores count. | ND 3.2, p.20 |
| Lower case in names is turned into upper case, unless option U is set. | ND 3.2, p.20 |
| Comments: `COMMENT any text;` or `! any text;` The `!` form is allowed anywhere a `COMMENT` is, outside character and text constants. | ND ch. 3, p.19 |

### Reserved words (ND 3.2, p.21)

```
ACTIVATE AFTER AND ARRAY AT BEFORE BEGIN BOOLEAN CHARACTER CLASS COMMENT DELAY DO ELSE END
EQ EQV EXTERNAL FALSE FOR GE GO GOTO GT HIDDEN IF IMP IN INNER INSPECT INTEGER IS LABEL LE
LONG LT NAME NE NEW NONE NOT NOTEXT OR OTHERWISE PRIOR PROCEDURE PROTECTED QUA REACTIVATE
REAL REF SHORT STEP SWITCH TEXT THEN THIS TO TRUE UNTIL VALUE VIRTUAL WHEN WHILE
```

With option Z, five more: `ENTRYPOINT INLINE LITERAL QUICK XOR` (ND App. E, p.52).

### Symbols and their word forms (ND 3.1, p.20)

| meaning | write | also accepted |
|---|---|---|
| equal | `=` | `EQ` |
| not equal | `NE` | `=/=`... see note |
| less, greater | `<` `>` | `LT` `GT` |
| less or equal, greater or equal | `<=` `>=` | `LE` `GE` |
| same object, not same object | `==` `=/=` | |
| not, and, or | `NOT` `AND` `OR` | |
| implies, equivalent | `IMP` `EQV` | |
| assign a value | `:=` | |
| assign a reference | `:-` | |
| multiply, divide, integer divide | `*` `/` `//` | |
| power | `**` | `^` |
| array subscript brackets | `(` `)` | see note |

**Note on the OCR.** The delimiter table on p.20 is damaged in the OCR copy. What can be read: the
Common Base square brackets `[` `]` are written with round brackets `(` `)` (another form shown is
`(/` `/)`), and `NE` is the safe spelling of "not equal" (the table also lists `=/=` in that row,
which clashes with the reference comparison - do not rely on it). The examples here use `( )` for
subscripts and `NE` for "not equal".

```simula
BEGIN
   COMMENT this is a comment that runs to the semicolon;
   ! and this is the short form;
   INTEGER Max_Value;
   Max_Value := 2 ** 10;
   IF Max_Value NE 1024 THEN OutText("strange");
   OutInt(Max_Value, 6);
   OutImage;
END
```

---

## 2. Program structure and blocks

A program is one block: `BEGIN` declarations, then statements, `END`. Declarations come before
statements in a block [CB]. A block can appear anywhere a statement can, and opens a new scope
[CB]. Text after the last `END` is ignored with the message `GARBAGE AFTER LAST END IGNORED`
(ND App. C, p.47).

```simula
BEGIN
   INTEGER A;
   A := 1;
   BEGIN
      INTEGER A;          ! a new A, hides the outer one;
      A := 2;
      OutInt(A, 3);       ! prints 2;
   END;
   OutInt(A, 3);          ! prints 1;
   OutImage;
END
```

A program can also be a **prefixed block**: a class name in front of `BEGIN`. The block then has
everything the class declares. This is how SIMSET and SIMULATION are used (section 16, 17):

```simula
SIMSET BEGIN
   REF(Head) Q;
   Q :- NEW Head;
END
```

A source file that holds only class and procedure declarations, no main block, is compiled as a
**library** (separate compilation, ND 4.2 p.24; see
[SIMULA-COMPILER-AND-RUN.md](SIMULA-COMPILER-AND-RUN.md) section 5).

---

## 3. Declarations and types

| type | holds | TPH SIMULA detail | source |
|---|---|---|---|
| `INTEGER` | whole numbers | **16 bits: -32768 to 32767.** | ND 1.2.2 p.14, 3.3.1 p.21 |
| `REAL` | floating point | about 10 significant digits; magnitude from 1&-4920 to 1&4920, or exact zero. 3 words. | ND 1.2.2 p.14; App. F p.56 |
| `LONG REAL` | floating point | accepted, but **the same as REAL**: the compiler warns `SHORT/LONG HAS NO EFFECT IN THIS IMPLEMENTATION` | ND App. C p.49 |
| `SHORT INTEGER` | | accepted with the same warning | ND App. C p.49 |
| `BOOLEAN` | `TRUE`, `FALSE` | 1 word; packed in arrays | ND App. F p.56 |
| `CHARACTER` | one ASCII character, 0-127 | starts as code 0 | ND 3.3.2 p.22 |
| `TEXT` | a reference to a piece of a text object | 4 words; max length 32761 | ND 1.2.2 p.14; App. F p.56 |
| `REF(C)` | a reference to an object of class C or a subclass | 1 word; starts as `NONE` | ND App. F p.56; [CB] start value |

Start values [CB]: numbers 0, Boolean `FALSE`, text `NOTEXT`, references `NONE`. Character
starts as code 0 (ND p.22).

**Watch the integer range.** `30000 + 5000` overflows. Overflow is checked at run time and gives
`Arithmetic operation caused overflow` (ND App. D p.51); option N switches some of the checks off
(ND 7.3.2 p.36). An integer constant too large for 16 bits becomes a real, with the warning
`LARGE INTEGER CONSTANT CONVERTED TO REAL` (ND App. C p.48).

### Constants (ND 3.3, p.21-22)

```simula
BEGIN
   INTEGER I;
   REAL R;
   BOOLEAN B;
   CHARACTER C, Bell;
   TEXT T;
   I := -1000;
   R := 125&-3;                ! & is the exponent sign: 0.125;
   B := TRUE;
   C := 'A';
   Bell := '!7!';              ! !n! = the character with ASCII code n (decimal);
   T :- "Say ""hello""";       ! a double quote inside text is written twice;
   T :- "Part one, " "part two";   ! two text constants side by side are joined;
   OutText(T);
   OutImage;
END
```

- Character constants are in single quotes; only the 95 printable ASCII characters can be typed
  directly (ND 3.3.2 p.21).
- `!n!` with 1-3 decimal digits, value up to 127, puts any code in a character or text constant:
  `"Abc!7!!7!!7!"` is Abc and three bells (ND 3.3.2 p.22).
- A text variable may point at a text constant. **Changing a text constant is caught at run
  time** (ND 1.2.1 p.13).

### Zimula: named constants (option Z only, ND App. E p.52)

```simula
%SETOPT Z
BEGIN
   LITERAL Small = 1, Medium = Small + 1, Large = Medium + 1;
   OutInt(Large, 3);
   OutImage;
END
```

A literal can only be used after the line that defines it. Code with `LITERAL` does not compile on
any other SIMULA (ND App. E p.52).

---

## 4. Arrays

Declared with bounds; lower bounds can be anything, and bounds can be expressions in an inner
block [CB]. Subscripts are written in round brackets (ND 3.1 p.20).

```simula
BEGIN
   INTEGER ARRAY Count(1:10);
   REAL ARRAY Grid(0:3, 0:3);
   TEXT ARRAY Names(1:3);
   INTEGER I, N;
   FOR I := 1 STEP 1 UNTIL 10 DO Count(I) := I * I;
   Grid(2, 3) := 1.5;
   Names(1) :- "Ada";
   N := 5;
   BEGIN
      INTEGER ARRAY Work(1:N);      ! bounds from a variable: allowed in an inner block [CB];
      Work(N) := 99;
   END;
   OutInt(Count(10), 5);
   OutImage;
END
```

TPH limits (ND 1.2.2 p.14):

- An array object is at most **49152 words**: about 49000 integers, 16300 reals, 12000 texts.
  Bigger gives `Too large array declared (max. is 49152 machine words)` (App. D p.50).
- **For a multi-dimension array only the final address is checked, not each subscript.**
  `Grid(0, 7)` in a 4 x 4 array can land inside the array and not be caught.
- Lower bound above upper bound gives
  `You have exchanged lower and upper bounds in array declaration` (App. D p.50).
- Bounds checks can be switched off with option A (ND 7.3.2 p.36).
- Elements are laid out with the last subscript changing fastest (ND App. F p.56).
- `CHARACTER` and `BOOLEAN` arrays are packed two per word (ND App. F p.56).

Library procedures that return bounds must be declared `EXTERNAL` first: `ralb`, `raub` (real
arrays) and `caub` (character arrays) (ND App. G p.61). See section 20.

---

## 5. Expressions and operators

```simula
BEGIN
   INTEGER I, J;
   REAL X;
   BOOLEAN P, Q;
   I := 17 // 5;                  ! integer divide: 3;
   J := Mod(17, 5);               ! remainder: 2;
   X := 17 / 5;                   ! always real: 3.4;
   X := 2.0 ** 0.5;
   P := I > 2 AND NOT (J = 0);
   Q := P IMP (I = 3);            ! implies;
   P := P EQV Q;                  ! equivalent;
   I := IF P THEN 1 ELSE 0;       ! conditional expression;
   J := Entier(-2.5);             ! largest integer not above: -3;
   OutInt(I, 3); OutInt(J, 3);
   OutImage;
END
```

- `/` always gives a real; `//` is integer division [CB].
- `Mod` is listed as a standard procedure (ND App. B p.45).
- `**` with bad operands gives `Illegal operands to **` (App. D p.50).
- Real to integer that does not fit gives `Result of real to integer conversion was too large`
  (App. D p.51).
- Option Z adds `XOR` for Booleans: TRUE when the two sides differ (ND App. E p.52).
- Text values compare with `=` `NE` `<` etc. [CB]. Text **references** compare with `==` `=/=`
  [CB]. A text constant is not allowed in a `==` comparison:
  `TEXT VALUE CONSTANT NOT ALLOWED IN == RELATION` (ND App. C p.48).
- One statement can nest at most 64 levels of expressions and calls (ND 1.2.2 p.14).

Standard functions listed for TPH SIMULA (ND App. B p.44-46): `Abs`, `Sign`, `Entier`, `Mod`,
`Sqrt`, `Sin`, `Cos`, `Arctan`, `Ln`, `Exp`, `Sinh`, `Cosh`, `Rank`, `Char`, `Digit`, `Letter`.
`Isorank` and `Isochar` are described in ND 6.2 p.31.

---

## 6. Statements

### Assignment

`:=` copies a value. `:-` sets a reference (objects and texts). Several at once is allowed
[CB].

```simula
BEGIN
   INTEGER A, B;
   TEXT T, U;
   A := B := 7;          ! both get 7 [CB];
   T :- Copy("abc");     ! T refers to a new text "abc";
   U :- T;               ! U refers to the SAME text;
   U := "xyz";           ! value copy into that text: T is now "xyz" too;
   OutText(T);
   OutImage;
END
```

`Left side of text assignment has too short text object` (ND App. D p.50) comes when the target
text of `:=` is shorter than the value. A longer target is padded with blanks [CB].

### IF

```simula
IF A > B THEN OutText("bigger")
ELSE IF A = B THEN OutText("same")
ELSE OutText("smaller");
```

The statement after `THEN` cannot itself be an `IF` without `BEGIN END` around it [CB]. A stray
`ELSE` gives `USELESS ELSE` (ND App. C p.47).

### WHILE

```simula
WHILE I < 10 DO
BEGIN
   I := I + 1;
END;
```

ND notes the `WHILE` statement "is (of course) implemented" (ND 1.2.1 p.13).

### FOR, all forms [CB]

```simula
BEGIN
   INTEGER I;
   REAL X;
   FOR I := 1 STEP 1 UNTIL 5 DO OutInt(I, 3);       ! 1 2 3 4 5;
   OutImage;
   FOR I := 10 STEP -3 UNTIL 1 DO OutInt(I, 3);     ! 10 7 4 1;
   OutImage;
   FOR I := 2, 3, 5, 7 DO OutInt(I, 3);             ! a list;
   OutImage;
   FOR X := 1.0, X * 2 WHILE X < 100.0 DO OutFix(X, 1, 7);  ! list element with WHILE;
   OutImage;
   FOR I := 1, 2, 10 STEP 10 UNTIL 50 DO OutInt(I, 3);      ! mixed elements;
   OutImage;
END
```

The ND compile errors that go with these: `MISSING FOR ELEMENT`, `MISSING WHILE EXPRESSION`,
`MISSING STEP EXPRESSION`, `MISSING UNTIL`, `MISSING DO`, `MISSING FOR VARIABLE`
(ND App. C p.47-48). A FOR variable can also be a text or reference, using `:-` [CB].

### GOTO, labels and switches

```simula
BEGIN
   SWITCH Choice := One, Two;
   INTEGER K;
   K := 2;
   GOTO Choice(K);
One: OutText("one");
   GOTO Done;
Two: OutText("two");
Done: OutImage;
END
```

`GO TO` (two words) is also reserved (ND 3.2 p.21). Jumping out of a detached object or into an
inspected one at run time gives `Illegal goto from detached object or to inspected object`
(App. D p.50).

### Compound statement and the empty statement

`BEGIN s1; s2 END` groups statements [CB]. A `;` before `END` is allowed (empty statement) [CB].

### INSPECT, WHEN, OTHERWISE

`INSPECT x DO s` runs `s` with the attributes of `x` visible without the `x.` in front; if `x` is
`NONE` the statement is skipped [CB]. With `WHEN`, the branch is picked by the object's class
[CB].

```simula
BEGIN
   CLASS Animal; ;
   Animal CLASS Dog;  BEGIN TEXT Sound; Sound :- "Woof"; END;
   Animal CLASS Cat;  BEGIN TEXT Sound; Sound :- "Miaow"; END;
   REF(Animal) A;
   A :- NEW Cat;
   INSPECT A
      WHEN Dog DO OutText(Sound)
      WHEN Cat DO OutText(Sound)
      OTHERWISE OutText("no animal");
   OutImage;
END
```

Compile errors: `INSPECT EXPRESSION MISSING`, `MISSING DO/WHEN`, `MISSING STATEMENT AFTER OTHERWISE`
(ND App. C p.47).

### ACTIVATE and REACTIVATE

These schedule processes inside a SIMULATION block. All forms are shown in section 17.

---

## 7. Procedures

```simula
BEGIN
   ! a plain procedure, a value parameter;
   PROCEDURE Line(N); INTEGER N;
   BEGIN
      INTEGER I;
      FOR I := 1 STEP 1 UNTIL N DO OutChar('-');
      OutImage;
   END;

   ! a function: a typed procedure returns by assigning to its own name;
   INTEGER PROCEDURE Square(X); INTEGER X;
      Square := X * X;

   ! a name parameter: changes reach the caller;
   PROCEDURE Swap(A, B); NAME A, B; INTEGER A, B;
   BEGIN
      INTEGER T;
      T := A; A := B; B := T;
   END;

   ! VALUE on a text makes a private copy;
   PROCEDURE Shout(T); VALUE T; TEXT T;
   BEGIN
      OutText(T); OutText("!");
      OutImage;
   END;

   INTEGER P, Q;
   P := 3; Q := 4;
   Line(10);
   Swap(P, Q);
   OutInt(Square(P), 5);
   OutImage;
   Shout("hi");
END
```

Parameter modes [CB]: simple values of type INTEGER, REAL, BOOLEAN, CHARACTER go **by value**
unless `NAME` is given. TEXT, REF and arrays go **by reference** unless `VALUE` (for text and
arrays) or `NAME` is given. Procedures and labels as parameters are allowed [CB]. ND App. F p.58
lists the three modes the compiler stores: value, reference, name.

TPH notes:

- A block object (a procedure call's data, a class object) is limited to **512 words**, including
  compiler temporaries; going over gives `NO SPACE IN BLOCK OBJECT FOR THE VARIABLE ...` or
  `... FOR ALL THE TEMPORARIES THAT ARE NEEDED` (ND 1.2.2 p.14; App. C p.48). Put big data in
  arrays, which are separate objects.
- A standard procedure name may not be passed as a parameter:
  `STANDARD PROCEDURE IDENTIFIER IS NOT ALLOWED AS ACTUAL PARAMETER` (App. C p.48).
- Calling a formal procedure with the wrong parameters is a run-time error:
  `Wrong number of parameters to formal or virtual procedure`, `... is of wrong kind`,
  `... is of wrong type` (App. D p.50).
- Recursion is allowed [CB].

### Zimula QUICK procedures (option Z, ND App. E p.52-53)

About 12 times faster to call. Limits: object at most 32 words; parameters at most 3 words (one
real, or three integer/Boolean/character/ref/array); no name parameters; may only use variables of
the surrounding block; no INSPECT; may not call ordinary procedures.

```simula
%SETOPT Z
BEGIN
   INTEGER Total;
   QUICK PROCEDURE Add(N); INTEGER N;
      Total := Total + N;
   Add(5);
   OutInt(Total, 4);
   OutImage;
END
```

---

## 8. Classes and objects

A class declares data, procedures and a body. `NEW C(params)` makes an object and runs its body
[CB].

```simula
BEGIN
   CLASS Point(X, Y); REAL X, Y;
   BEGIN
      REAL PROCEDURE Dist;
         Dist := Sqrt(X * X + Y * Y);
      OutText("point made");        ! the body runs at NEW;
      OutImage;
   END;

   REF(Point) P;
   P :- NEW Point(3.0, 4.0);
   OutFix(P.Dist, 2, 8);            ! remote access with a dot;
   OutImage;
END
```

Class parameters are by value or by reference, **never by name** [CB]; ND gives
`SPECIFICATION ILLEGAL FOR CLASS` for a wrong one (App. C p.48).

### NONE, references, dot access

```simula
REF(Point) P, Q;
IF P == NONE THEN OutText("empty");
P :- NEW Point(1.0, 1.0);
Q :- P;                         ! same object;
IF P == Q THEN OutText("same");
```

A dot on a `NONE` reference gives `Ref before dot or qua was equal to none` (App. D p.50); the
check can be switched off with option R (ND 7.3.2 p.36). Dot access on a class that has local
classes is refused: `ATTEMPTED DOT ACCESS ON CLASS WITH LOCAL CLASSES` (App. C p.48) - use INSPECT
for those.

---

## 9. Subclasses (prefixing) and INNER

Put a class name in front of `CLASS` to extend it. The subclass object has everything the prefix
has [CB].

```simula
BEGIN
   CLASS Shape;
   BEGIN
      OutText("start ");
      INNER;                       ! the subclass body runs here;
      OutText(" end");
      OutImage;
   END;

   Shape CLASS Square(Side); REAL Side;
   BEGIN
      OutText("square");
   END;

   REF(Shape) S;
   S :- NEW Square(2.0);           ! prints: start square end;
END
```

Without `INNER` the subclass body runs after the prefix body [CB]. A missing semicolon gives
`MISSING SEMICOLON BEFORE INNER` (ND App. C p.48). A prefix chain that loops gives
`UNKNOWN OR CIRCULAR PREFIX: ...` (App. C p.47).

**TPH limit:** of the system classes, only SIMSET and SIMULATION may be used as prefixes. The file
classes (InFile, OutFile, ...) **cannot be prefixed** (ND 1.2.2 p.14; ch. 5 p.26).

---

## 10. VIRTUAL procedures

A virtual procedure is declared in the prefix and may be redefined in a subclass. A call through
any reference picks the deepest definition [CB].

```simula
BEGIN
   CLASS Shape;
      VIRTUAL: REAL PROCEDURE Area;
   BEGIN
      REAL PROCEDURE Area; Area := 0.0;
   END;

   Shape CLASS Circle(R); REAL R;
   BEGIN
      REAL PROCEDURE Area; Area := 3.14159 * R * R;
   END;

   Shape CLASS Rect(W, H); REAL W, H;
   BEGIN
      REAL PROCEDURE Area; Area := W * H;
   END;

   REF(Shape) ARRAY All(1:2);
   INTEGER I;
   All(1) :- NEW Circle(1.0);
   All(2) :- NEW Rect(2.0, 3.0);
   FOR I := 1, 2 DO OutFix(All(I).Area, 3, 10);
   OutImage;
END
```

TPH notes (ND 1.2.1 p.13; 4.3 p.25):

- If **every** match of a virtual has the same number, types and modes of parameters, a call is as
  fast as an ordinary call. Different parameter lists are legal but much slower.
- If a virtual in an external module is always called with matching lists inside that module, a
  later compilation may not break that.
- Calling a virtual with no match at run time: `No match to virtual attribute in this class`
  (App. D p.50).
- Compile errors: `MISSING COLON AFTER VIRTUAL`, `ILLEGAL VIRTUAL SPECIFICATION`,
  `GARBAGE IN VIRTUAL LIST`, `INCONSISTENT PARAMETER LISTS TO VIRTUAL PROCEDURE` (App. C p.48).

---

## 11. HIDDEN and PROTECTED

**Accepted, but ignored.** `HIDDEN` and `PROTECTED` are reserved and the compiler takes the
declarations so programs from other systems compile, but it does **not** enforce them: a protected
attribute can still be reached from outside (ND 1.2.1 p.13; 3.2 p.21).

```simula
CLASS Account;
   PROTECTED Balance;          ! accepted, NOT enforced by TPH SIMULA;
BEGIN
   REAL Balance;
END;
```

Do not rely on them for safety on this compiler.

---

## 12. QUA, IS, IN, THIS

```simula
BEGIN
   CLASS Vehicle; BEGIN INTEGER Wheels; END;
   Vehicle CLASS Car; BEGIN TEXT Make; END;
   REF(Vehicle) V;
   REF(Car) C;

   V :- NEW Car;
   IF V IS Car THEN OutText("exactly a Car");      ! IS: exact class;
   IF V IN Vehicle THEN OutText(" and a Vehicle"); ! IN: the class or a subclass;
   OutImage;
   (V QUA Car).Make :- "Volvo";                     ! QUA: look at V as a Car;
   C :- V QUA Car;
   OutText(C.Make);
   OutImage;
END
```

- `QUA` on the wrong class at run time: `Object in reference assignment or qua was of wrong class`
  (App. D p.50). Qualification checks can be switched off with option Q (ND 7.3.2 p.36).
- `ILLEGAL USE OF QUA` at compile time (App. C p.47).
- `THIS C` inside class C (or a subclass) is a reference to the object itself [CB]. Wrong use:
  `ILLEGAL THIS` (App. C p.48).

```simula
CLASS Node;
BEGIN
   REF(Node) Next;
   PROCEDURE LinkTo(N); REF(Node) N;
      N.Next :- THIS Node;
END;
```

---

## 13. Coroutines: DETACH, RESUME, CALL

ND defines these exactly, because "there is presently some confusion as to the operation of
detach" (ND 6.1 p.30-31). In short, for the simple case of a main program and some objects:

- **`Detach`** inside an object: if the object was started by `NEW` or `Call`, control goes back to
  just after that `NEW` or `Call`. If it was started by `Resume`, control goes back to the main
  program after its last `Resume`. In the main program, `Detach` does nothing. The point after
  `Detach` is where the object will carry on next time.
- **`Call(X)`**: X must be detached and not running. It runs from where it stopped, and comes back
  to the caller when it detaches again.
- **`Resume(X)`**: X must be detached and not running. The running object stops (it will carry on
  after the `Resume`) and X runs instead.

Run-time errors: `Parameter to CALL or RESUME was terminated`, `... was already operating`,
`... was none`, `Detach called for non-operating class object` (App. D p.50-51).

### A generator with Detach and Call

```simula
BEGIN
   CLASS Counter;
   BEGIN
      INTEGER N;
      Detach;                   ! NEW returns here;
      WHILE TRUE DO
      BEGIN
         N := N + 1;
         Detach;                ! each Call returns here;
      END;
   END;

   REF(Counter) C;
   INTEGER I;
   C :- NEW Counter;
   FOR I := 1 STEP 1 UNTIL 3 DO
   BEGIN
      Call(C);
      OutInt(C.N, 4);           ! 1 2 3;
   END;
   OutImage;
END
```

### Two coroutines with Resume

```simula
BEGIN
   CLASS Player(Name, Times); TEXT Name; INTEGER Times;
   BEGIN
      REF(Player) Other;
      INTEGER K;
      Detach;
      FOR K := 1 STEP 1 UNTIL Times DO
      BEGIN
         OutText(Name); OutImage;
         Resume(Other);
      END;
      Detach;                   ! back to the main program after its Resume;
   END;

   REF(Player) Ping, Pong;
   Ping :- NEW Player("ping", 3);
   Pong :- NEW Player("pong", 3);
   Ping.Other :- Pong;
   Pong.Other :- Ping;
   Resume(Ping);                ! ping pong ping pong ping pong;
   OutText("done");
   OutImage;
END
```

**Do not use `Call`, `Detach` or `Resume` inside a SIMULATION block** - they break its scheduling
(ND 5.3 p.29).

---

## 14. TEXT handling

A `TEXT` variable is a reference to part of a text object, with a current position [CB]. In TPH
SIMULA it is 4 words: the object and the byte addresses of `Pos`, start and end (ND App. F p.56).

```simula
BEGIN
   TEXT T, U, Part;
   INTEGER N;

   T :- Blanks(20);              ! a new text of 20 blanks;
   T := "Hello world";           ! value copy, padded with blanks;
   U :- Copy(T.Strip);           ! a new copy without trailing blanks;
   OutText(U); OutImage;
   OutInt(U.Length, 4); OutImage;

   Part :- U.Sub(7, 5);          ! "world": start position 7, length 5;
   OutText(Part); OutImage;

   U.SetPos(1);
   WHILE U.More DO               ! walk character by character;
   BEGIN
      IF U.GetChar = 'o' THEN N := N + 1;
   END;
   OutInt(N, 3); OutImage;       ! 2;

   T :- Copy("   left blanks");
   OutText(T.Trim);              ! TPH extra: removes LEADING blanks;
   OutImage;

   T :- Blanks(10);
   T.PutInt(42);                 ! edit a number into the text, right aligned;
   OutText(T); OutImage;
   N := T.GetInt;                ! read it back;
END
```

Text procedures listed in ND App. B (p.44-46): `Blanks`, `Copy`, `Length`, `Main`, `More`, `Pos`,
`SetPos`, `GetChar`, `PutChar`, `Sub`, `Strip`, `Trim` (TPH), and the editing pairs `GetInt`
`PutInt`, `GetReal` `PutReal`, `GetFrac` `PutFrac`, `PutFix`, `GetOct` `PutOct` (TPH), `PutZInt`
(TPH).

TPH details:

- **`Trim`** (TPH extra) is like `Strip` but removes leading blanks (ND 6.5 p.32).
- **`GetOct`** reads in base 8; **`PutOct`** writes in base 8 with leading zeros; **`PutZInt`** is
  `PutInt` with leading zeros (ND 6.4 p.32).
- If a number does not fit the field, the field is filled with `*` and a warning is printed when
  the program ends (ND 6.4 p.32).
- `PutReal` writes the exponent as `&+nnnn`: four digits, because of the wide range (ND 6.4 p.32).
- `GetInt`, `GetFrac` must give a value in -32768..32767 (ND 6.4 p.32).
- `Blanks(n)` with n negative or above 8186: `Parameter to BLANKS was negative or greater than 8186`
  (App. D p.51). Note this is less than the 32761 text limit in ND 1.2.2 p.14; I do not know why
  the two numbers differ.
- `Sub` out of range: `SUB parameter(s) out of range`; `GetChar`/`PutChar` past the end:
  `MORE is false in GETCHAR` / `... PUTCHAR` (App. D p.50).

### Characters

```simula
BEGIN
   CHARACTER C;
   INTEGER K;
   C := 'a';
   K := Rank(C);            ! 97;
   C := Char(K - 32);       ! 'A';
   IF Letter(C) AND NOT Digit(C) THEN OutChar(C);
   OutImage;
END
```

`Rank` and `Isorank` give 0-127. `Char` takes any integer and is faster; `Isochar` takes only 0-127
(`Illegal parameter to isochar` otherwise) (ND 6.2 p.31; App. D p.51). The external procedure
`upper(c)` gives the upper-case letter (ND App. G p.60, section 20).

---

## 15. Input and output

### The terminal: SysIn and SysOut

In the main program, `InInt`, `OutText`, `OutImage` and the rest act on `SysIn` and `SysOut`
without naming them [CB]. A line is built in an **image** and written with `OutImage`; input is
read a line at a time with `InImage` (the `InInt`-style calls do this for you) [CB].

```simula
BEGIN
   INTEGER A, B;
   OutText("Two numbers: ");
   BreakOutImage;               ! TPH: write the line with no newline;
   A := InInt;
   B := InInt;
   OutText("Sum = ");
   OutInt(A + B, 6);
   OutImage;
END
```

- The SysIn and SysOut image is **136** characters. For a shorter line, put
  `SysOut.Image :- Blanks(100);` at the start (ND 5.1 p.27; the manual writes it as
  `image:-blanks(100);`).
- **`BreakOutImage`** (TPH extra, OutFile only) writes the image without carriage return and line
  feed - use it for prompts (ND 5.1 p.28).
- **`InOct`, `OutOct`, `OutZInt`** are added to the file classes (ND 5.1 p.28; 6.4 p.32).
- **`DirectOut(c)`** sends one character at once; **`DirectIn`** reads one character at once when
  the terminal is in character mode (ND 5.1 p.28).

Item reads listed for InFile and DirectFile (ND App. B p.45): `InChar`, `InInt`, `InReal`, `InFrac`,
`InText(n)`, `InImage`, `LastItem`, `EndFile`. Writes for OutFile and DirectFile: `OutChar`,
`OutText`, `OutInt(i, w)`, `OutFix(r, d, w)`, `OutReal(r, d, w)`, `OutFrac(i, n, w)`, `OutImage`.
The App. B OCR also lists `InRest` (TPH extra) and `InCommand`; their meaning is not described in
the manual, so it is unknown here.

### How a file name is opened on SINTRAN (ND 5.1 p.26-27)

The file object gets a **name** at `NEW`, and the image at `Open`:

- If the name is a number, it is a SINTRAN **logical file number in octal** that is already open.
- Otherwise SIMULA opens the SINTRAN file by name. The default file type is `DATA`.
- The text given to `Open` may start with control items, which are blanked after use:
  - `:tttt` in column one: default file type `tttt` (up to four characters) instead of `DATA`.
  - `@a` in column one, or one space after `:tttt`: the access mode.

| `@a` | access |
|---|---|
| `@W` | write sequential |
| `@R` | read sequential |
| `@WX` | write/read random |
| `@RX` | read random |
| `@RW` | read/write sequential |
| `@WA` | write append |
| `@WC` | write/read random common |
| `@RC` | read random common |

With no `@a`: InFile reads sequential, OutFile and PrintFile write sequential, DirectFile is
write/read random. `Close` closes a file SIMULA opened itself. `Id` (TPH extra) returns the file's
name while closed, or an 8-character text with the SINTRAN file number in octal while open.

### OutFile and InFile

```simula
BEGIN
   REF(OutFile) Out;
   REF(InFile) Inp;
   TEXT Img;
   INTEGER I, Sum;

   Out :- NEW OutFile("NUMBERS");
   Img :- Blanks(80);
   Img := ":SYMB";               ! default type SYMB instead of DATA (ND p.26);
   Out.Open(Img);
   FOR I := 1 STEP 1 UNTIL 10 DO
   BEGIN
      Out.OutInt(I, 5);
      Out.OutImage;
   END;
   Out.Close;

   Inp :- NEW InFile("NUMBERS");
   Img :- Blanks(80);
   Img := ":SYMB";
   Inp.Open(Img);
   Inp.InImage;
   WHILE NOT Inp.EndFile DO
   BEGIN
      Sum := Sum + Inp.Image.GetInt;    ! or Inp.InInt;
      Inp.InImage;
   END;
   Inp.Close;
   OutInt(Sum, 6);
   OutImage;
END
```

**Not run.** Whether the file `NUMBERS:SYMB` must exist before `Open` is not stated in the ND
manual. SINTRAN normally needs a file to exist before it is opened for writing, and the manual's
own saving example says a `:PROG` file "must exist in advance" (ND 7.2 p.34), so create it first
with `@CREATE-FILE NUMBERS:SYMB 0` if the open fails - this is my reading, not a tested fact.

Errors: `Requested file is busy or non-existent`, `File not closed at calling OPEN`,
`File already closed at calling CLOSE`, `File not open at INIMAGE`, `ENDfile is true at INIMAGE`,
`Image of infile is too short`, `File not open at OUTIMAGE`, `Unsuccessful input/output request`
(App. D p.50-51).

Rules for lines (ND 5.1 p.28):

- OutFile writes the image **stripped** of trailing blanks, then CR LF.
- InFile: the line on disk may not hold anything but blanks past the image length. CR is not
  counted; a leading LF is ignored.

### DirectFile

Random access by line number. `Locate(n)` picks line n, `Location` tells where you are [CB].

```simula
BEGIN
   REF(DirectFile) D;
   D :- NEW DirectFile("RECORDS");
   D.Open(Blanks(40));           ! every line will be 40 characters;
   D.Locate(5);
   D.OutText("this is line five");
   D.OutImage;
   D.Locate(5);
   D.InImage;
   OutText(D.Image.Strip);
   OutImage;
   D.Close;
END
```

TPH rules (ND 5.1 p.28): the file must be random access; every line is written **unstripped**, so
all lines have the length `Image.Length` had at the first `Open`, plus CR LF; reading needs the
same length (`Wrong physical directfile image length` otherwise, App. D p.50). After `InImage` or
`Locate`, `EndFile` is TRUE only when `Location` points into a disk block that does not exist - a
FALSE `EndFile` does **not** promise there is a valid line there. `Locate(0)` gives
`Zero parameter to LOCATE` (App. D p.51). DirectFile is defined in the library `SIMBASE3:SIM`
(ND 1.3 p.15).

### PrintFile

An OutFile with page control: `Eject(n)` goes to line n (a new page if n is above the current
line), `Spacing(n)` sets line spacing, `LinesPerPage(n)`, `Line` gives the current line [CB].
These are listed for PrintFile in ND App. B p.44-46. `SysOut` is a PrintFile (App. B p.46).

```simula
BEGIN
   REF(PrintFile) P;
   P :- NEW PrintFile("REPORT");
   P.Open(Blanks(132));
   P.LinesPerPage(60);
   P.OutText("Page heading"); P.OutImage;
   P.Spacing(2);
   P.OutText("double spaced"); P.OutImage;
   P.Eject(1);
   P.Close;
END
```

`File not open at EJECT` if the file is closed (App. D p.51).

### The class FILE

`File` itself is visible, so a procedure can take any kind of file as a parameter (ND 5.1 p.26).
Making a plain `File` object is not useful - it has no open or close.

```simula
PROCEDURE Report(F); REF(OutFile) F;
BEGIN
   F.OutText("report line");
   F.OutImage;
END;
```

---

## 16. SIMSET: linked lists

SIMSET gives two-way circular lists [CB]: class `Head` (the list) and class `Link` (an element),
both prefixed by `Linkage`. Prefix the block with `SIMSET` to use them. In TPH SIMULA it is an
external class in `SIMSET3:SIM`, used "according to the Common Base"; "there is nothing special or
restrictive about SIMSET" (ND 5.2 p.29; 1.3 p.15).

Main attributes [CB]:

- `Head`: `First`, `Last`, `Empty`, `Cardinal`, `Clear`.
- `Link`: `Out`, `Into(h)`, `Follow(x)`, `Precede(x)`, and from Linkage `Suc`, `Pred`.

```simula
SIMSET BEGIN
   Link CLASS Item(Value); INTEGER Value; ;

   REF(Head) List;
   REF(Item) X;
   INTEGER I;

   List :- NEW Head;
   FOR I := 5, 3, 9 DO NEW Item(I).Into(List);

   X :- List.First QUA Item;
   WHILE X =/= NONE DO
   BEGIN
      OutInt(X.Value, 4);
      X :- X.Suc QUA Item;          ! Suc is NONE after the last;
   END;
   OutImage;
   OutInt(List.Cardinal, 4);        ! 3;
   OutImage;
END
```

A note from ND 5.2 p.29: if SIMSET is used as a prefix in more than one block, the compiler treats
each copy as a different class, so a `REF(Link)` from one copy cannot be assigned to one from
another.

---

## 17. SIMULATION: discrete-event simulation

`SIMULATION` is a SIMSET with a clock and processes [CB]. Prefix a block with `SIMULATION`; SIMSET
comes with it automatically (ND 5.3 p.29). It lives in `SIMULA3:SIM` (ND 1.3 p.15).

What it gives [CB]:

| name | what it does |
|---|---|
| `Process` | a Link subclass with its own life. Its body is the life of the process. |
| `Time` | the current simulated time (real) |
| `Hold(t)` | wait t time units |
| `Passivate` | stop until somebody activates you |
| `Wait(h)` | go into list h and passivate |
| `Cancel(p)` | take p off the schedule |
| `Current` | the running process |
| `Idle`, `Terminated`, `EvTime`, `NextEv` | process state |

Scheduling statements [CB]:

```simula
ACTIVATE P;                      ! now;
ACTIVATE P DELAY 5.0;            ! 5 units from now;
ACTIVATE P AT 100.0;             ! at time 100;
ACTIVATE P AT 100.0 PRIOR;       ! at 100, before others due at 100;
ACTIVATE P BEFORE Q;             ! just before Q in the schedule;
ACTIVATE P AFTER Q;              ! just after Q;
REACTIVATE P DELAY 2.0;          ! also works on a process already scheduled;
```

`ACTIVATE` does nothing to a process that is already scheduled; `REACTIVATE` moves it [CB].
Run-time errors from ND App. D p.51: `Attempt to passivate last process`,
`Evtime called for idle process`, `Reactivate caused passivation of last process`,
`Attempt to activate terminated process`. Compile error: `MISSING EXPRESSION IN ACTIVATE STATEMENT`
(App. C p.48).

TPH cautions (ND 5.3 p.29):

- **Do not use `Call`, `Detach` or `Resume`** in a SIMULATION program.
- Use SIMULATION as the prefix of the **outermost** block. Used on an inner block it runs about
  50% slower.

### Worked example: one bank clerk

Customers arrive at random, wait in a queue, and are served one at a time. The program reports
how many were served in a 480-minute day and the mean wait.

```simula
SIMULATION BEGIN
   REF(Head) Queue;
   REF(Clerk) TheClerk;
   INTEGER U, Served;
   REAL TotalWait;

   Process CLASS Customer;
   BEGIN
      REAL Arrived;
      Arrived := Time;
      ! the next customer arrives on average 3 minutes later;
      ACTIVATE NEW Customer DELAY Negexp(1.0 / 3.0, U);
      Into(Queue);
      IF TheClerk.Idle THEN ACTIVATE TheClerk;
      Passivate;                       ! wait until served;
   END;

   Process CLASS Clerk;
   BEGIN
      REF(Customer) C;
      WHILE TRUE DO
      BEGIN
         WHILE NOT Queue.Empty DO
         BEGIN
            C :- Queue.First QUA Customer;
            C.Out;
            TotalWait := TotalWait + (Time - C.Arrived);
            Hold(Uniform(1.0, 4.0, U));  ! serve for 1 to 4 minutes;
            Served := Served + 1;
            ACTIVATE C;                  ! the customer leaves;
         END;
         Passivate;                      ! nobody waiting: sleep;
      END;
   END;

   U := 12345;                           ! seed for the random stream;
   Queue :- NEW Head;
   TheClerk :- NEW Clerk;
   ACTIVATE TheClerk;
   ACTIVATE NEW Customer;
   Hold(480.0);                          ! run one working day;

   OutText("Customers served: ");
   OutInt(Served, 5);
   OutImage;
   IF Served > 0 THEN
   BEGIN
      OutText("Mean wait (minutes): ");
      OutFix(TotalWait / Served, 2, 8);
      OutImage;
   END;
END
```

How it works: the main program is itself a process. `Hold(480.0)` lets the simulation run until
time 480, then the main program prints and reaches `END`, which ends everything (customers still
in the queue are left there) [CB]. Every `Negexp` and `Uniform` call updates `U`, so one integer
variable drives the whole random stream (section 18). **Not run** - the numbers it prints are not
known.

---

## 18. Random drawing

All drawing procedures take an `INTEGER` seed `U` as the last parameter, **by name**; each call
changes it [CB]. ND rules (ND 6.3 p.31):

- U is a 16-bit integer, so a stream has 65536 different values.
- **U must be a simple variable of type INTEGER**, because it is passed by name. An expression or
  array element is not allowed.

The routines are in `SIMRAND3:SIM` (ND 1.3 p.15). Listed in ND App. B p.44-46:

| call | gives | [CB] meaning |
|---|---|---|
| `Draw(p, U)` | Boolean | TRUE with probability p |
| `Randint(a, b, U)` | integer | even spread over a..b |
| `Uniform(a, b, U)` | real | even spread over a..b |
| `Normal(m, s, U)` | real | normal, mean m, deviation s |
| `Negexp(r, U)` | real | negative exponential, rate r (mean 1/r) |
| `Poisson(m, U)` | integer | Poisson, mean m |
| `Erlang(m, k, U)` | real | Erlang, mean m, shape k |
| `Discrete(A, U)` | integer | index chosen from a cumulative table A |
| `Linear(A, B, U)` | real | from a piecewise-linear table |
| `Histd(A, U)` | integer | index chosen with weights A |
| `Histo(A, B, c, d)` | (procedure) | adds weight d for value c into histogram A with limits B |

```simula
BEGIN
   INTEGER U, I, Dice;
   U := 4711;
   FOR I := 1 STEP 1 UNTIL 6 DO
   BEGIN
      Dice := Randint(1, 6, U);
      OutInt(Dice, 3);
   END;
   OutImage;
   IF Draw(0.5, U) THEN OutText("heads") ELSE OutText("tails");
   OutImage;
END
```

Errors: `ERLANG parameter(s) zero or negative`, `HISTO: First array must be longer than second
array`, `Wrong parameters to LINEAR` (App. D p.51).

---

## 19. Mathematical library

`SIMMAT:SIM` is listed as "Mathematical library" (ND 1.3 p.15). The manual does not say what is in
it beyond the standard functions in section 5. **Its contents are unknown.**

---

## 20. TPH external procedure library

These are in the run-time system but must be **declared `EXTERNAL PROCEDURE` before use**
(ND App. G p.59). They are not portable.

```simula
BEGIN
   EXTERNAL PROCEDURE Sintran, TimeWait, Date, Clock, TimeUsed;
   Sintran("LIST-FILES ,,");     ! run a SINTRAN command, no leading @;
   OutText(Date);                ! "yy-mm-dd";
   OutImage;
   OutInt(Clock, 5);             ! hhmm as an integer;
   OutImage;
   TimeWait(2.0);                ! wait 2 seconds of wall-clock time;
   OutFix(TimeUsed, 3, 10);      ! CPU seconds so far;
   OutImage;
END
```

The `LIST-FILES ,,` text in this example is an illustration; the parameters SINTRAN needs for it
are not checked here. **Warning from ND App. G p.59:** if the command is wrong there is no error
status, and SINTRAN waits for an extra blank line from the terminal. Give every parameter.

### Operating system interface (ND App. G p.59-60)

| declaration | what it does |
|---|---|
| `PROCEDURE Sintran(t); TEXT t;` | run SINTRAN command t (no `@`) |
| `REAL PROCEDURE TimeUsed;` | CPU seconds used so far |
| `TEXT PROCEDURE Date;` | new 8-character text `yy-mm-dd` |
| `INTEGER PROCEDURE Clock;` | hour and minute as `hhmm` |
| `PROCEDURE TimeWait(r); REAL r;` | wait r seconds of wall-clock time |
| `INTEGER PROCEDURE GetFile(t, a); TEXT t; INTEGER a;` | open file t with access mode a (SINTRAN code), default type DATA; returns the logical unit (positive) or a negative error |
| `INTEGER PROCEDURE GetExFile(t, type, a); TEXT t, type; INTEGER a;` | same, default type given in `type`, which must end with `'` |
| `PROCEDURE RelFile(n); INTEGER n;` | close logical unit n |

ND's own example (App. G p.60): wait until the file `SEMAPHORE:FLAG` can be opened, use it as a
lock, then release it:

```simula
INTEGER I;
FOR I := GetExFile("SEMAPHORE", "FLAG'", 4) WHILE I < 0 DO
   TimeWait(1);
! ... the critical section ... ;
RelFile(I);
```

(`GetExFile`, `TimeWait`, `RelFile` must be declared `EXTERNAL PROCEDURE` first.)

### Bit and number routines (ND App. G p.60-62)

The OCR on p.61 splits the result type away from each declaration; the types below are taken from
the headings above each one.

| declaration | what it does |
|---|---|
| `CHARACTER PROCEDURE Upper(c);` | upper-case version of c |
| `BOOLEAN PROCEDURE CheckSet(i, mask);` | TRUE if i AND mask is not zero |
| `INTEGER PROCEDURE BitSet(i, n);` | i with bit n set (bit 0 is the rightmost; 16 bits) |
| `INTEGER PROCEDURE Shift(i, n);` | i shifted right n places, zero filled |
| `INTEGER PROCEDURE IAnd(a, b);` | bitwise AND |
| `PROCEDURE LongDiv(quot, rem, i, j, div);` | (i*j) // div, with remainder, in 32 bits |
| `INTEGER PROCEDURE Ralb(a); / Raub(a);` | lower / upper bound of a 1-dimension real array |
| `INTEGER PROCEDURE Caub(a);` | upper bound of a 1-dimension character array |
| `REAL PROCEDURE Arctan2(a, b);` | arctan(a/b) in the right quadrant |
| `INTEGER PROCEDURE TabLook(A, n, t);` | find t (may be abbreviated) in text array A(1:n): index, 0 if none, -1 if ambiguous (p.63) |
| `TextTrick`, `TrickReal` | build a text reference or real from raw words - ND says not to use them (p.62) |

```simula
BEGIN
   EXTERNAL PROCEDURE TabLook;
   TEXT ARRAY Cmd(1:3);
   Cmd(1) :- "LIST"; Cmd(2) :- "LOAD"; Cmd(3) :- "EXIT";
   OutInt(TabLook(Cmd, 3, "LI"), 3);   ! 1;
   OutInt(TabLook(Cmd, 3, "L"), 3);    ! -1, LIST or LOAD;
   OutImage;
END
```

### Run-time system interface (ND App. G p.62)

`BOOLEAN PROCEDURE RtOpt(c)`, `PROCEDURE RtOn(c)`, `PROCEDURE RtOff(c)` read and set the run-time
options A to O (see [SIMULA-DEBUGGING.md](SIMULA-DEBUGGING.md) section 4). `PROCEDURE Collect`
forces a garbage collection; ND warns it usually makes things worse.

---

## 21. Procedures in FORTRAN and assembly (ND App. F, p.54-58)

"Such procedures are called at the user's own risk" (ND App. F p.54).

### FORTRAN

1. Compile the FORTRAN module **in reentrant mode** so its data fits SIMULA's.
2. Give the FORTRAN BRF file to the SIMULA compiler with `>LIB`.
3. Declare the routines (typed ones are functions, the others subroutines):

```simula
BEGIN
   EXTERNAL FORTRAN REAL PROCEDURE Dot;
   EXTERNAL FORTRAN PROCEDURE Clear;
   ! ... call Dot(...) and Clear(...) as normal procedures ... ;
END
```

The FORTRAN code **must not use READ, WRITE or FORMAT** (ND App. F p.54). An error inside gives
`Error in FORTRAN subroutine or function` (App. D p.51). How to switch the FORTRAN compiler to
reentrant mode is not in the SIMULA manual; see
[../FORTRAN-DEVELOPER-GUIDE.md](../FORTRAN-DEVELOPER-GUIDE.md). COBOL calls are not supported
(ND 4.1 p.23).

### Assembly

Declared with all parameters and an empty body, language `LIBRARY`:

```simula
EXTERNAL LIBRARY PROCEDURE ExTrick;;
EXTERNAL LIBRARY BOOLEAN PROCEDURE Comp(A, B); CHARACTER A, B;;
```

Rules for the code (ND App. F p.55): label equal to the procedure name; ends with `JPL I (EXIT`;
must not change the B register (it points at the object); return value, parameters and locals start
at `RT*BODY` (=2) from B. ND's own example, the `Rank` function:

```
RANK,    IDA RT*BODY+1,B
         STA RT*BODY,B
         JPL I (EXIT&
)FILL
```

The file must be in the SIMULA BRF format, which ND says "users are strongly discouraged from
attempting to produce" (App. F p.54). The object layout (prototype, data descriptors, text
references, array headers) is in App. F p.55-58.

---

## 22. Limits in one table

| limit | value | source |
|---|---|---|
| line length | 120 characters | ND 1.2.2 p.14 |
| identifier length | 72, all significant | ND 1.2.2 p.14 |
| integer | -32768..32767 | ND 1.2.2 p.14 |
| real | 10 digits, exponent to 4920 | ND 1.2.2 p.14 |
| text length | 32761 (Blanks: 8186) | ND 1.2.2 p.14; App. D p.51 |
| nesting in one statement | 64 | ND 1.2.2 p.14 |
| array object | 49152 words | ND 1.2.2 p.14 |
| block, procedure or class object | 512 words | ND 1.2.2 p.14 |
| program size | about 5000 source lines per compilation, about 8000 with separate compilation | ND 1.2.2 p.14 |
| system prefixes | SIMSET and SIMULATION only | ND 1.2.2 p.14 |
