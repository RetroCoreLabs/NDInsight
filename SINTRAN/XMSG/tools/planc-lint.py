"""Check a PLANC source for the mistakes the ND compiler has actually caught here.

WHY THIS EXISTS. Every rule below cost a real build cycle on D100 - carry the file
across, compile, fetch the listing, read it - and several cost more than one because
the compiler's own message points somewhere else. A round trip is minutes; this is
instant, and it catches them before the file leaves Windows.

It is a LINTER, not a compiler. It reads text and knows nothing about scope or types,
so it will miss things and it can be wrong. Its job is the mistakes that repeat.

    python tools/planc-lint.py SINTRAN-CHAT/CHAT.PLNC SINTRAN-CHAT/CHATSV.PLNC

    --include-dir DIR   also look for $INCLUDE files in DIR (after the source's own
                        folder). "(USER)NAME:TYPE" is tried as DIR/USER/NAME.TYPE, then
                        DIR/NAME.TYPE. For SLIB programs:
                        --include-dir Installation/Communication/TCP/x/D02-gateway-and-clients

Exit code 1 if anything is reported.
"""

import io
import json
import os
import re
import sys
import tempfile


# ---------------------------------------------------------------------------
# THE XMSG API, READ FROM DATA RATHER THAN HARD-CODED HERE.
#
# Developer/Languages/Application/xmp-api.json was transcribed from ND's OWN
# shipped declarations - XMP-B02:IMPT and XMP-B02:DEFS off the ND-10609 media -
# not from the guide, whose parameter tables have several typesetting slips.
# 54 routines and 397 constants. Keeping it as data means the same file serves
# the linter, a future code generator and anybody reading it, and it can be
# corrected in one place when the machine teaches us something.
#
# The linter still works without it: every XMSG rule below is skipped if the
# file is missing, because a linter that dies on a missing side-file is worse
# than one that checks less.
# ---------------------------------------------------------------------------
# Helpers that take a literal AND its length. The number must equal the literal's
# length, and nothing but this check can say so.
#
# EMPTY IS THE GOAL, not an accident: every helper that used to be here now asks
# the string its own length instead. It stays as a list rather than being deleted
# because the next helper written in this shape belongs in it, and a named list is
# where somebody will look.
LITERAL_LENGTH_HELPERS = ()

# Helpers that USED to take a length and no longer do. Passing one is the old
# shape returning.
DERIVES_ITS_OWN_LENGTH = (
    'buildAdmText',
    'putWord',
    'logLine',
    'cmdIs',
    'tryCmd',
    'showIfMatch',
)


def load_xmp_api():
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (os.path.join('..', '..', '..', 'Developer', 'Languages', 'Application',
                             'xmp-api.json'),
                os.path.join('..', 'Developer', 'Languages', 'Application', 'xmp-api.json')):
        p = os.path.normpath(os.path.join(here, rel))
        if os.path.exists(p):
            try:
                with io.open(p, encoding='utf-8', errors='replace') as fh:
                    return json.load(fh)
            except (ValueError, IOError):
                return None
    return None


XMP_API = load_xmp_api()

# The three calls that RECEIVE. Everything in section 1 and 2 of the rules is about these.
RECEIVE_ROUTINES = ('xmpfrcv', 'xmpfrre', 'xmpfrrh')


def mask_strings(line):
    """Blank the inside of every 'quoted' run, keeping the line's length.

    Needed before looking for routine CALLS. A diagnostic string is very likely
    to name the routine it is about - showStatus('xmprout (the join)', st) - and
    a regex looking for "xmprout(" then matches the TEXT and reports a call with
    the wrong number of parameters, on a line that has no call at all. That was
    the first false alarm this rule produced.
    """
    out, in_quote = [], False
    for ch in line:
        if ch == "'":
            in_quote = not in_quote
            out.append(ch)
        else:
            out.append(' ' if in_quote else ch)
    return ''.join(out)


def strip_comment(line):
    """Drop a trailing % comment, leaving quoted text alone.

    Needed because a bare RETURN with a comment after it - "RETURN  % not news" -
    otherwise looks like RETURN with an out-value, which is a different mistake.
    """
    out = []
    in_quote = False
    for ch in line:
        if ch == "'":
            in_quote = not in_quote
        if ch == '%' and not in_quote:
            break
        out.append(ch)
    return ''.join(out)


# Extra folders searched for $INCLUDE files after the source's own folder, set with
# --include-dir. Added 2026-09-27 for the SLIB (TCP/IP socket library) samples, whose
# includes live on the ND as (TCP-IP)SLIB:IMPT and in the repo under the TCP kit.
INCLUDE_DIRS = []


def include_text(source_path, inc_name):
    """The text of a $INCLUDE'd file, parity stripped, or '' when it cannot be found.

    Looked for next to the source first, then in every --include-dir. A leading
    SINTRAN user prefix such as "(TCP-IP)" is tried two ways in an include dir: as a
    subfolder of that name ("TCP-IP/SLIB.IMPT"), then without it. The compiler's
    default file type is SYMB (appendix A section 0.8); an explicit ":TYPE" is
    honoured."""
    spec = inc_name.strip().strip("'\"")
    user = None
    um = re.match(r'^\(([^)]*)\)(.*)$', spec)
    if um:
        user, spec = um.group(1).strip(), um.group(2)
    base = spec.split(':')[0].strip()
    suffix = spec.split(':')[1].strip() if ':' in spec else None
    exts = [suffix] if suffix else ['SYMB', 'INCL', 'PLNC']
    here = os.path.dirname(os.path.abspath(source_path))
    folders = [here]
    for d in INCLUDE_DIRS:
        if user:
            folders.append(os.path.join(d, user))
        folders.append(d)
    for folder in folders:
        for ext in exts:
            for cand in (base + '.' + ext, base.upper() + '.' + ext.upper(),
                         base.lower() + '.' + ext.lower()):
                full = os.path.join(folder, cand)
                if not os.path.exists(full):
                    continue
                try:
                    raw = io.open(full, encoding='utf-8', errors='replace').read()
                except IOError:
                    return ''
                # Strip parity the way the rest of this repo does, so a file copied
                # straight off an ND floppy reads correctly.
                return ''.join(chr(ord(c) & 0x7F) for c in raw)
    return ''


def include_types(source_path, inc_name):
    """The TYPE names a $INCLUDE'd file declares - "TYPE SLin_sockaddr = ..." - so a
    local declared with one ("SLin_sockaddr : myaddr") is seen as a declaration."""
    raw = include_text(source_path, inc_name)
    return re.findall(r'^\s*TYPE\s+([A-Za-z_]\w*)\s*=', raw, re.M | re.I)


def include_names(source_path, inc_name):
    """Every name a $INCLUDE'd file introduces, upper-cased.

    "$INCLUDE screen" brings in the whole PLANC-SCREEN-H interface - frame,
    bytdis, intacc and the rest. Without this, a screen program reports every
    one of them as undeclared: a page of false alarms that trains you to ignore
    the tool.

    Collected: every name in a declaration list after a colon (record fields such
    as "SLu_char : in_b1, in_b2, in_b3, in_b4" declare four, not one); CONSTANT
    names ("CONSTANT SLEok = 0"); TYPE names; and routine names in IMPORT
    statements that continue over lines with "&" - ND's SLIB:IMPT writes
    "(ROUTINE VOID,INTEGER (...) : &" and puts the NAME on the next line, which a
    per-line reading never saw. Checked 2026-09-27 against ND's own TCCOM, which
    reported 55 invented problems before and should report none of this kind after.

    A file that cannot be found returns nothing - the tool goes quiet rather than
    guessing at names it cannot see.
    """
    found = set()
    raw = include_text(source_path, inc_name)
    if not raw:
        return found
    lines = []
    for ln in raw.splitlines():
        ls = ln.split('%', 1)[0].strip()      # a comment runs to end of line
        if ls:
            lines.append(ls)
    joined = re.sub(r'&\s*\n\s*', ' ', '\n'.join(lines))
    for ls in joined.split('\n'):
        cm = re.match(r'^CONSTANT\s+(.+)$', ls, re.I)
        if cm:
            for part in cm.group(1).split(','):
                nm = re.match(r'\s*([A-Za-z][A-Za-z0-9_]*)', part)
                if nm:
                    found.add(nm.group(1).upper())
            continue
        tm = re.match(r'^TYPE\s+([A-Za-z_]\w*)\s*=', ls, re.I)
        if tm:
            found.add(tm.group(1).upper())
        # names after each colon, up to the next closing bracket, "=" or ":="
        for seg in re.findall(r':\s*([^:)=]*)', ls):
            for nm in re.findall(r'[A-Za-z_]\w*', seg):
                if nm.upper() in ('ALIAS', 'MOD', 'ARRAY', 'PACKED', 'RANGE'):
                    continue
                found.add(nm.upper())
    return found


def check(path):
    """Report every problem found in one source. Returns a list of strings."""
    text = io.open(path, encoding='utf-8', errors='replace').read()
    lines = text.split('\n')
    out = []

    def code_lines():
        """Every line with its number, comments and blank lines skipped."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('%'):
                yield i + 1, line, stripped

    # ---- WHAT COUNTS AS A TYPE, INCLUDING THE ONES THIS FILE INVENTS ---------
    #
    # PLANC lets a source name its own type - TYPE xrAddr = INTEGER4 - and
    # XMP-B02:IMPT does exactly that for XMMSGIDENTIFIER and XMUSERADDRESS. A
    # variable declared with such a name is a perfectly ordinary declaration.
    #
    # MEASURED 2026-08-27: the checks below knew only the built-in type names,
    # so the moment a source declared TYPE xrAddr = INTEGER4 and used it, the
    # linter called the type AND every variable declared with it undeclared -
    # six invented problems in a file that was correct. A linter that cries wolf
    # gets switched off, which costs far more than the check ever saves.
    #
    # Built ONCE here and used by every check that recognises a declaration, so
    # a new type is added in one place rather than in four regexes that had
    # already drifted apart from each other.
    own_types = re.findall(r'^\s*TYPE\s+([A-Za-z_]\w*)\s*=', text, re.M)
    # A TYPE declared in a $INCLUDE'd file is just as much a type here - SLIB:DEFS
    # declares SLin_sockaddr, SLmaxima and friends, and a program's locals of those
    # types were reported as undeclared until 2026-09-27.
    for _im in re.finditer(r'^\s*\$INCLUDE\s+(\S+)', text, re.M | re.I):
        own_types += include_types(path, _im.group(1))
    TYPEALT = '|'.join(['INTEGER4', 'INTEGER', 'BYTES', 'BYTE', 'BOOLEAN',
                        'REAL', 'LABEL', 'POINTER']
                       + [re.escape(t) for t in own_types])

    # ---- ADDR FORCED TO A 32-BIT TYPE ---------------------------------------
    #
    # AN ADDRESS ON THIS MACHINE IS SIXTEEN BITS. Forcing ADDR to a 32-bit type
    # draws
    #
    #     *** WARNING - ILLEGAL DATA-ELEMENT TO BE CONVERTED
    #
    # which is a WARNING, so the build carries on and the value that comes out
    # is the 16-bit address with a word of ADJACENT MEMORY on top of it.
    #
    # MEASURED 2026-08-27, and it cost two compile cycles and two published
    # conclusions that both had to be withdrawn. The junk was STABLE - the same
    # two numbers came back across separate builds - which read as a reliable
    # measurement and was nothing of the kind.
    #
    # The product's own working calls force to XMUSERADDRESS, and XMP-B02:IMPT
    # declares it "TYPE XMUSERADDRESS = INTEGER". The line above that one is a
    # COMMENT reading "modify XMUSERADDRESS = INTEGER4" - an instruction to
    # widen it FOR THE MC68000 - and reading that commented instruction as the
    # declaration is exactly how the mistake was made.
    #
    # Only INTEGER4 and REAL8 are flagged: those are the 32-bit and 64-bit
    # built-ins a person actually reaches for when they think "an address is
    # big". A named type cannot be judged from one line, so it is left alone -
    # narrow beats clever.
    for number, line, stripped in code_lines():
        m = re.search(r'ADDR\s*\(.*\)\s*FORCE\s+(INTEGER4|REAL8)', stripped)
        if m:
            out.append('%s:%d  ADDR forced to %s - an address on this machine is a 16-bit '
                       'INTEGER, and PLANC answers *** WARNING - ILLEGAL DATA-ELEMENT TO BE '
                       'CONVERTED. That is a WARNING, so the build continues and the value '
                       'carries a word of adjacent memory above the address. Force to INTEGER, '
                       'or to XMUSERADDRESS which is declared as one.'
                       % (path, number, m.group(1)))

    # ---- AN IMPORT OR EXPORT AFTER AN ORDINARY DECLARATION -------------------
    #
    # Every IMPORT and every EXPORT must sit in the block at the top of the
    # module, before any ordinary declaration. One that comes later draws
    #
    #     *** ERROR   - MISPLACED STATEMENT "IMPORT"
    #     *** ERROR   - MISPLACED STATEMENT "EXPORT"
    #
    # MEASURED 2026-08-27: replacing ten constant declarations with IMPORTs
    # WHERE THEY STOOD - each beside the comment explaining that kind, which
    # read perfectly well - produced ten of these in one compile. Four minutes
    # to be told something this check answers instantly.
    #
    # EXPORT WAS ADDED TO THIS CHECK 2026-08-27, AFTER IT HAPPENED AGAIN - and
    # the second time is the one worth reading. Ten trunk constants were exported
    # from CHATLIB beside their own declarations, well below the main EXPORT
    # block, and every one drew this error. What makes it a linter check rather
    # than a note is what the machine then did with them:
    #
    #   the linker reported NO undefined entries
    #   the test program linked, loaded and RAN
    #   all 139 checks PASSED, including ones reading those very constants back
    #   the last line on the screen was "codec is good"
    #
    # A compile with ten errors produced a program that passed its own test
    # suite. Only the LISTING said anything was wrong. That is the whole reason
    # this project gates on the listing and not on the screen - and the reason a
    # check costing a second belongs in front of a compile costing minutes.
    #
    # The comment can stay where it is; only the IMPORT or EXPORT has to move.
    #
    # Module level only: an IMPORT inside a ROUTINE is a different thing and is
    # not what this is about, so anything indented past the module's own level
    # is left alone.
    first_decl = None
    for number, line, stripped in code_lines():
        if re.match(r'^(?:' + TYPEALT + r')\b'
                    r'(?:\s+ARRAY)?\s*:', stripped) and line.startswith('    ') \
                and not line.startswith('        '):
            if first_decl is None:
                first_decl = number
        word = None
        if stripped.startswith('IMPORT'):
            word = 'IMPORT'
        elif stripped.startswith('EXPORT'):
            word = 'EXPORT'
        if word is not None and line.startswith('    ') \
                and not line.startswith('        '):
            if first_decl is not None:
                out.append('%s:%d  %s comes after the declaration at line %d - PLANC '
                           'answers *** ERROR - MISPLACED STATEMENT "%s". Every %s '
                           'belongs in the block at the top of the module; the comment '
                           'explaining it can stay where it is.'
                           % (path, number, word, first_decl, word, word))

    # ---- A LITERAL AND A HAND-COUNTED LENGTH BESIDE IT ------------------------
    #
    # This project is full of helpers shaped `f('some text', <count>, ...)` -
    # buildAdmText, putWord, bytdis and friends. The count is written by hand, and
    # a wrong one NEVER fails to build: it silently truncates the string, or runs
    # past its end and prints whatever follows.
    #
    # MEASURED 2026-08-27: 'peers locked - no new ones will be learned' was given
    # 41 where the string is 42, and the machine printed "...will be learne". One
    # character, a clean compile, and only a person watching the screen would ever
    # know. The same session miscounted a second one the same way.
    #
    # This is the 'ALn' width rule (R28) wearing different clothes, and it is why
    # MAXINDEX (R115) is the better habit where a routine can ask the string
    # itself. Where the count has to be written, this catches it in a second
    # rather than in a build.
    #
    # ONLY the (literal, number) pair is checked, and only when they are adjacent.
    # A count that is a variable is somebody's deliberate choice and none of this
    # check's business.
    for number, line, stripped in code_lines():
        for m in re.finditer(r"\(\s*'((?:[^']|'')*)'\s*,\s*(\d+)\s*[,)]", stripped):
            # NOT `text` - that name holds the WHOLE FILE in this function, and
            # assigning to it here made every later check read a fragment of a
            # string literal instead of the source. It turned a clean file into
            # 119 invented "undeclared name" reports, and the only reason it was
            # caught is that the file had been linted clean minutes before.
            lit = m.group(1).replace("''", "'")
            said = int(m.group(2))
            # A '$' is CRLF but is still a character in the string, and it counts.
            if said != len(lit):
                out.append('%s:%d  the literal %r is %d character(s) but is given %d '
                           'beside it. A wrong count builds CLEAN and either truncates '
                           'the string on screen or reads past its end. Count the '
                           'trailing $ too, or use MAXINDEX and let the string say.'
                           % (path, number, lit[:44], len(lit), said))

    # ---- A CALL THAT CLAIMS AN ARRAY IS BIGGER THAN IT IS ---------------------
    #
    # Routines that write into a caller's buffer take its size as a parameter and
    # have to believe it. PLANC checks no array bound, so a call that overstates
    # the size writes past the end IN SILENCE - and every assertion about the
    # early bytes still passes, because those bytes are in bounds.
    #
    # MEASURED 2026-08-27, in a TEST SUITE that reported success on every run:
    #
    #     BYTES : buf(0:255)
    #     BYTES : tx(0:63)
    #     cmEnc(buf, kSay, nm, 5, tx, 300, 512)
    #
    # 512 for a 256-byte buffer. It wrote fifty-three bytes past buf and read 236
    # past tx, and printed "codec is good".
    #
    # WHAT IS CHECKED, and deliberately nothing more: a call whose FIRST argument
    # is a BYTES array declared in this file and whose LAST argument is a plain
    # number BIGGER than that array holds. That is the shape a write-into-buffer
    # routine has here - cmEnc(buf, ..., bufMax) - and nothing else is guessed at.
    #
    # THE FIRST VERSION OF THIS CHECK COMPARED THE NUMBER AGAINST ANY ARRAY IN THE
    # CALL, and it fired on `xmpblet(letterBuf, 64, offSet, 123, ...)`, where 123
    # is a SERVICE NUMBER, and on every correct cmEnc call in the test suite,
    # because a 256 meant for a 256-byte buffer was compared against a 16-byte
    # name sitting in the same argument list. Thirteen false alarms against three
    # real faults. This file's own note at the undeclared-name check says it: a
    # page of false alarms trains you to ignore the linter, which costs more than
    # the check ever saves. Narrow beats clever.
    array_size = {}
    for number, line, stripped in code_lines():
        m = re.match(r'^BYTES\s*:\s*(\w+)\s*\(\s*(\d+)\s*:\s*(\d+)\s*\)', stripped)
        if m:
            array_size[m.group(1)] = int(m.group(3)) - int(m.group(2)) + 1

    if array_size:
        for number, line, stripped in code_lines():
            call = re.match(r'^(?:\w+\s*=:\s*)?(\w+)\s*\((.*)\)\s*(?:=:\s*\w+)?\s*$', stripped)
            if not call:
                continue
            if call.group(1).upper() in ('IF', 'FOR', 'WHILE', 'OUTPUT', 'INPUT'):
                continue
            args = [a.strip() for a in call.group(2).split(',')]
            if len(args) < 3:
                continue
            first, last = args[0], args[-1]
            if first not in array_size or not re.match(r'^\d+$', last):
                continue
            if int(last) > array_size[first]:
                out.append('%s:%d  %s is given %s as its last argument while %s holds only '
                           '%d byte(s). If that number is the buffer size the callee '
                           'believes, this call writes past the end - silently, because '
                           'PLANC checks no array bound. A test doing exactly this passed '
                           'while corrupting memory.'
                           % (path, number, call.group(1), last, first, array_size[first]))

    # ---- A BOOLEAN WHERE AN INTEGER IS DECLARED ------------------------------
    #
    # PLANC does not convert at a call. `len <= 256` is a BOOLEAN, so it cannot be
    # handed to a routine whose parameter is INTEGER - and the error names the
    # ROUTINE, not the argument, which sends you to the declaration.
    #
    # Only comparison operators are flagged, because those are unambiguous. A
    # BOOLEAN VARIABLE passed to an INTEGER parameter needs the signature, which
    # is a bigger job than this check is worth.
    int_param_routines = set()
    for number, line, stripped in code_lines():
        m = re.match(r'^ROUTINE\s+\S+\s*,\s*\S+\s*\(([^)]*)\)\s*:\s*(\w+)', stripped)
        if m and 'BOOLEAN' not in m.group(1) and 'INTEGER' in m.group(1):
            int_param_routines.add(m.group(2))

    if int_param_routines:
        for number, line, stripped in code_lines():
            m = re.match(r'^(?:\w+\s*=:\s*)?(\w+)\s*\((.*)\)', stripped)
            if not m or m.group(1) not in int_param_routines:
                continue
            for a in m.group(2).split(','):
                a = a.strip()
                if re.search(r'(?:<=|>=|><|(?<![<>=:])=(?!:))\s*\S', a) and not a.startswith("'"):
                    out.append('%s:%d  passes the comparison "%s" to %s, whose parameters '
                               'are INTEGER. A comparison is a BOOLEAN and PLANC will not '
                               'convert it - and the error names the ROUTINE, not this '
                               'argument. Write a separate BOOLEAN routine.'
                               % (path, number, a[:40], m.group(1)))
                    break

    # ---- TWO EXPORTS THAT ARE THE SAME NAME ACROSS A BRF BOUNDARY -------------
    #
    # Names are unique in TEN characters to the compiler but only SEVEN across an
    # EXPORT/IMPORT, because that is what a BRF entry carries (ND-60.117.5
    # appendix G item 27). Two exports agreeing in their first seven characters
    # are ONE name to the linker.
    #
    # WHAT IT ACTUALLY DOES is the reason this is worth a check: it does NOT
    # report a duplicate. The linker resolves both imports to whichever entry it
    # met first, so calls meant for one routine silently land in the other - and
    # if the signatures differ, it reads arguments that were never passed. The
    # compile is clean, the link is clean, and LIST-ENTRIES-UNDEFINED is empty,
    # because nothing is undefined.
    #
    # This is how kRenamed and kDirected had to be renamed. MEASURED again
    # 2026-08-27: adding cmTxLenN beside cmTxLen made both CMTXLEN, and it was
    # caught by hand rather than by any tool - which is why it is a tool now.
    exports = {}
    for number, line, stripped in code_lines():
        m = re.match(r'^EXPORT\s+(\w+)', stripped)
        if m:
            exports.setdefault(m.group(1)[:7].upper(), []).append((number, m.group(1)))
    for short, found in sorted(exports.items()):
        if len(found) > 1:
            names = ', '.join('%s (line %d)' % (n, ln) for ln, n in found)
            out.append('line %d: EXPORTS COLLIDE at seven characters - %s all read '
                       '"%s" across a BRF boundary. The linker will not complain; it '
                       'will resolve every import to ONE of them. Rename all but one.'
                       % (found[0][0], names, short))

    # ---- BANNED JARGON IN A COMMENT ------------------------------------------
    #
    # Ronny's rule, and it is absolute: plain words a normal person understands.
    # "wedge"/"wedged" is banned by name and so are the other old-Unix ones. Say
    # hung, stuck, crashed, hangs.
    #
    # It is a linter check because writing it down did not stop it. The word had
    # to be swept out of 13 files at once once before, and out of 37 places
    # across this repo on 2026-08-28 - including a comment in CHATSV.PLNC and
    # three commit messages written the same day, by which time it had been a
    # named rule for eighteen days.
    BANNED_WORDS = ('wedge', 'wedged', 'wedges', 'hosed', 'borked', 'clobbered', 'munged')
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped.startswith('%'):
            continue
        low = stripped.lower()
        for bad in BANNED_WORDS:
            if re.search(r'\b' + bad + r'\b', low):
                out.append('%s:%d  "%s" is banned jargon - say hung, stuck or crashed'
                           % (path, number, bad))
                break

    # ---- an IMPORTed ARRAY must carry its BOUNDS ------------------------------
    #
    # MEASURED on D100 2026-08-28, five at once on the first build of a module
    # split out of CHAT.PLNC:
    #
    #     IMPORT (BYTES : inBuf)      ->  *** ERROR - ARRAY BOUNDS MISSING "INBUF"
    #     IMPORT (BYTES : inBuf(0:255))   compiles
    #
    # A scalar needs none - IMPORT (INTEGER : lenMyName) is right - so this only
    # looks at BYTES and at anything declared ARRAY. IMPORT still allocates
    # nothing either way; the bounds only describe the shape, and they must match
    # the declaration in the module that owns the storage.
    #
    # Worth a check rather than a note because the compile that produced these
    # five ALSO printed "1050 LINES COMPILED. 0 DIAGNOSTICS." one line further
    # down, at EXIT, and the MODE file it ran inside went on to report
    # "Built CHAT:PROG".
    for number, line, stripped in code_lines():
        m = re.match(r'^IMPORT\s*\(\s*((?:BYTES|BYTE)\b|[A-Z0-9]+\s+ARRAY\b)'
                     r'[^:]*:\s*([A-Za-z_]\w*)\s*\)', stripped)
        if m:
            out.append('%s:%d  IMPORT of "%s" gives no ARRAY BOUNDS - the compiler answers '
                       'ARRAY BOUNDS MISSING and names it. Write the bounds the owning '
                       'module declared, for example IMPORT (BYTES : %s(0:255))'
                       % (path, number, m.group(2), m.group(2)))

    # ---- assignment written the wrong way round -------------------------------
    # PLANC stores with "expression =: variable". Writing "variable := expression"
    # is the habit of every other language and it compiles as far as the ":=" then
    # answers ILLEGAL SYNTAX ":=" - preceded by a WARNING that the expression does
    # not store a value, which reads like a separate complaint about the line.
    #
    # ":=" IS legal in a DECLARATION as an initialiser, so only lines that are not
    # declarations are flagged. MEASURED: two of these in CHATSV's putNumber cost a
    # push-and-compile round on D100, 2026-08-20, and the linter passed the file.
    declaration = re.compile(
        r'^\s*(INTEGER|BYTE|BYTES|BOOLEAN|REAL|LABEL|POINTER|VOID|ENUMERATION)\b',
        re.IGNORECASE)
    for n, line, stripped in code_lines():
        if ':=' not in line:
            continue
        if declaration.match(line):
            continue
        # A store into a subscripted name, "x(i) := v", is wrong the same way.
        if re.search(r'^\s*[A-Za-z][A-Za-z0-9_]*\s*(\([^)]*\))?\s*:=', line):
            out.append('%s:%d  ":=" assigns the wrong way round - PLANC stores with '
                       '"expression =: variable". ":=" is only an initialiser in a '
                       'declaration.' % (path, n))

    # ---- the operator that does not exist -------------------------------------
    # "=<" gets ILLEGAL SYNTAX, but the compiler blames the line ABOVE first with
    # ILLEGAL DATA TYPE "AND", so the operator is the last thing anyone looks at.
    for n, line, _ in code_lines():
        if '=<' in line:
            out.append('%s:%d  "=<" is not PLANC - the operators are <= and >= '
                       '(ND-60.117.5 section 5.4)' % (path, n))

    # ---- array indexing is ROUND ----------------------------------------------
    # The COSMOS guide prints ADDR(buf[0]) and PLANC F rejects it:
    # EXPECTS ")" ILLEGAL SYNTAX "[", then INVALID PARAMETER LIST for the call.
    for n, line, _ in code_lines():
        if re.search(r'\w\s*\[', line):
            out.append('%s:%d  square brackets index nothing in PLANC - use round ones'
                       % (path, n))

    # ---- the out-value goes BEFORE the keyword --------------------------------
    # "RETURN at" gets ILLEGAL DATA TYPE "RETURN", which reads like RETURN itself
    # is the problem.
    for n, line, stripped in code_lines():
        if re.match(r'RETURN\s+\S', strip_comment(stripped).strip()):
            out.append('%s:%d  the out-value goes BEFORE RETURN - write "x RETURN"'
                       % (path, n))

    # ---- WHILE is a continue-test, not a loop header --------------------------
    for n, line, stripped in code_lines():
        if re.search(r'\bENDWHILE\b', stripped):
            out.append('%s:%d  there is no ENDWHILE - WHILE is a continue-test inside '
                       'DO ... ENDDO' % (path, n))
        if re.search(r'\bWHILE\b.*\bDO\s*$', stripped):
            out.append('%s:%d  "WHILE cond DO" is not a loop header - put WHILE inside '
                       'the DO body' % (path, n))

    # ---- an OUTPUT field is the FIELD, not a maximum ---------------------------
    # Too narrow and it prints the first n characters then a row of asterisks.
    for n, line, _ in code_lines():
        for m in re.finditer(r"OUTPUT\s*\(\s*\d+\s*,\s*'A[LR]?(\d+)'\s*,\s*'((?:[^']|'')*)'", line):
            width = int(m.group(1))
            literal = m.group(2).replace("''", "'")
            if len(literal) > width:
                out.append("%s:%d  'AL%d' is narrower than its %d-character string - "
                           'PLANC prints asterisks' % (path, n, width, len(literal)))

    # ---- a CASE selects on 0..255 ---------------------------------------------
    # Section 6.3: the expression must be an enumeration of at most 256 values or
    # "integers ranging between 0 and 255". A plain INTEGER draws OUT OF RANGE -
    # a WARNING, so the build "succeeds" and the CASE misbehaves at run time.
    ranged = set()
    for _, line, _ in code_lines():
        m = re.search(r'INTEGER\s+RANGE\s*\([^)]*\)\s*:\s*([\w,\s]+)', line, re.I)
        if m:
            for name in m.group(1).split(','):
                ranged.add(name.strip().upper())
    for n, _, stripped in code_lines():
        m = re.match(r'CASE\s+(\w+)\s*$', stripped, re.I)
        if m and m.group(1).upper() not in ranged:
            out.append('%s:%d  CASE selects on 0..255 - declare "%s" as '
                       'INTEGER RANGE (0:255) or it draws OUT OF RANGE'
                       % (path, n, m.group(1)))

    # ---- PLANC is single pass --------------------------------------------------
    # A routine called above its declaration gets ILLEGAL SYNTAX on the CALL,
    # naming a routine that plainly exists - which reads as nonsense.
    declared = {}
    for i, line in enumerate(lines):
        m = re.match(r'\s*(?:ROUTINE|PROGRAM)\b.*?:\s*(\w+)', line)
        if m:
            declared.setdefault(m.group(1).upper(), i + 1)
    for n, line, stripped in code_lines():
        if re.match(r'\s*(?:ROUTINE|PROGRAM)\b', line):
            continue
        # AN EXPORT OR IMPORT LIST IS NOT A USE. It names what crosses a module
        # boundary, and the manual's own example in 8.3 puts EXPORT ABOVE the
        # declaration it names:
        #     EXPORT x
        #     IMPORT REAL : y
        #     INTEGER : x
        # Treating those as forward references made this checker reject a
        # correctly written module, and would have blocked splitting a source
        # into separately compiled parts altogether.
        if re.match(r'\s*(?:EXPORT|IMPORT)\b', line):
            continue
        # BLANK THE QUOTED TEXT FIRST. A routine called UPPER made this rule
        # report the word "Upper" inside the help screen's own sentence as a
        # forward call - a false alarm that sends you rearranging perfectly
        # correct declarations. The call-checking rules below already mask
        # strings; this one did not, and any routine whose name is an ordinary
        # English word walks straight into it.
        scan = mask_strings(stripped)
        for name, at in declared.items():
            if n < at and re.search(r'\b' + re.escape(name) + r'\b', scan, re.I):
                out.append('%s:%d  uses %s but it is declared at line %d - PLANC is '
                           'single pass' % (path, n, name, at))

    # ---- a MODULE-LEVEL VARIABLE is single pass too -----------------------------
    #
    # MEASURED 2026-08-26 and it cost a whole build cycle on D100. buildTellTo
    # sat beside the routine it resembled, near the top of the file, and used
    # two arrays declared with the window state 900 lines further down. PLANC
    # answered
    #
    #     1629 (944)/BUILDTELLT *** ERROR - NOT PREVIOUSLY DECLARED "WINLABLEN"
    #     1629 (944)/BUILDTELLT *** ERROR - EXPECTS ":" ILLEGAL SYNTAX "("
    #
    # and the second line is the trap: it blames a BRACKET, so the eye goes to
    # the argument list rather than to where the array is declared.
    #
    # The rule above catches this for ROUTINES and did not for VARIABLES, which
    # is the whole reason it got through. Only declarations at MODULE level are
    # considered - a local is scoped to its routine and cannot be used above it
    # anyway.
    modvar = {}
    for i, line in enumerate(lines):
        # Module level means one indent step. A local sits deeper than that.
        m = re.match(r'    (?:BYTES|INTEGER|BOOLEAN|REAL)'
                     r'(?:\s+ARRAY)?\s*:\s*(\w+)', line)
        if m:
            modvar.setdefault(m.group(1).upper(), i + 1)

    for n, line, stripped in code_lines():
        if re.match(r'\s*(?:ROUTINE|PROGRAM)\b', line):
            continue
        # AN EXPORT OR IMPORT LIST IS NOT A USE. It names what crosses a module
        # boundary, and the manual's own example in 8.3 puts EXPORT ABOVE the
        # declaration it names:
        #     EXPORT x
        #     IMPORT REAL : y
        #     INTEGER : x
        # Treating those as forward references made this checker reject a
        # correctly written module, and would have blocked splitting a source
        # into separately compiled parts altogether.
        if re.match(r'\s*(?:EXPORT|IMPORT)\b', line):
            continue
        if re.match(r'    (?:BYTES|INTEGER|BOOLEAN|REAL)', line):
            continue
        scan = mask_strings(stripped)
        for name, at in modvar.items():
            if n < at and re.search(r'\b' + re.escape(name) + r'\b', scan, re.I):
                out.append('%s:%d  uses %s but it is declared at line %d - PLANC is '
                           'single pass for VARIABLES too, and the error blames a '
                           'bracket' % (path, n, name, at))

    # ---- a guard that sets a flag NOBODY READS is a silencer, not a guard -------
    #
    # MEASURED 2026-08-21. The chat client's idleSleep did exactly this:
    #
    #     ON ROUTINEERROR DO
    #         TRUE =: sleepFailed
    #     ENDON
    #     FALSE =: sleepFailed
    #     MONITOR_CALL('TimeOut', sleepUnits, sleepKind, sleepWhy)
    #     ENDROUTINE          <- and that was the end of it
    #
    # A refused TimeOut therefore returned instantly and the main loop went round
    # again with NO SLEEP AT ALL - a spin against XMSG, invisible on the screen,
    # in the log and in the kernel tables alike.
    #
    # This is the same shape that hid GetUserName being refused for a whole build
    # cycle: guarded, refused, silent. The guard makes the program SURVIVE, which
    # is right, and then hides that anything happened, which is not. A swallowed
    # failure is a place the machine can be hurt with nothing saying so.
    #
    # The flag must be TESTED somewhere. What you do about it is your business -
    # print it, degrade, give up - but it may not simply vanish.
    handler_flags = {}
    in_handler = False
    for n, line, stripped in code_lines():
        s = mask_strings(stripped)
        if re.search(r'\bON\s+ROUTINEERROR\b', s, re.I):
            in_handler = True
            continue
        if re.search(r'\bENDON\b', s, re.I):
            in_handler = False
            continue
        if in_handler:
            m = re.search(r'\bTRUE\s*=:\s*(\w+)', s, re.I)
            if m:
                handler_flags.setdefault(m.group(1).upper(), n)

    for flag, at in handler_flags.items():
        tested = False
        for n, line, stripped in code_lines():
            s = mask_strings(stripped)
            # A test is any IF/WHILE that mentions it - NOT the assignments that
            # set or clear it, which is why the =: forms are excluded.
            if re.search(r'\b(IF|WHILE)\b.*\b' + re.escape(flag) + r'\b', s, re.I):
                tested = True
                break
        if not tested:
            out.append('%s:%d  %s is set by an ON ROUTINEERROR handler and NEVER TESTED - '
                       'the failure is swallowed in silence. A guard that sets a flag nobody '
                       'reads is a silencer, not a guard.' % (path, at, flag))

    # ---- do not redeclare a name the library already defines -------------------
    # Measured: CHATSV declared its own XFWTF, which XMP-B02:DEFS also defines. The
    # compiler said IDENTIFIER ALREADY SPECIFIED/DECLARED and then FELL OVER with
    # "ASSERT VIOLATION AT 136747B", taking the batch job with it. So this is not a
    # warning you can carry on past - it is a compiler crash waiting to happen.
    defs_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(path)))),
        'Installation', 'Software', 'ND-10609', 'files', 'XMP-B02-DEFS.readable.txt')
    if os.path.exists(defs_path):
        library = set()
        dt = io.open(defs_path, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'CONSTANT\s+(\w+)', dt, re.I):
            library.add(m.group(1).upper())
        if any(s.upper().startswith('$INCLUDE XMP-B02:DEFS') for _, _, s in code_lines()):
            for n, _, stripped in code_lines():
                m = re.match(r'(?:' + TYPEALT + r')'
                             r'(?:\s+RANGE\s*\([^)]*\))?\s*:\s*([A-Za-z_]\w*)', stripped)
                if m and m.group(1).upper() in library:
                    out.append('%s:%d  "%s" is already defined by XMP-B02:DEFS - redeclaring '
                               'it crashes the compiler (ASSERT VIOLATION)'
                               % (path, n, m.group(1)))

    # ---- names are unique in their first TEN characters ------------------------
    # Measured on CHATSV: memberName and memberNameLen both start MEMBERNAME, so
    # the second became a redeclaration of the first - IDENTIFIER ALREADY
    # SPECIFIED/DECLARED - and every memberName(slot, i) then drew MORE SUBSCRIPTS
    # THAN IN THE ARRAY DECLARATION, because the name now meant the 1-D array.
    # Four errors from one cause, and not one of them mentions the length. The
    # listing is the tell: it prints the TRUNCATED names (BUILDRENAM, REASONNICK).
    declared_names = set()
    for _, _, stripped in code_lines():
        m = re.match(r'(?:' + TYPEALT + r')(?:\s+ARRAY)?'
                     r'(?:\s+RANGE\s*\([^)]*\))?\s*:\s*([A-Za-z_]\w*)', stripped)
        if m:
            declared_names.add(m.group(1))
        m = re.match(r'(?:ROUTINE|PROGRAM)\b.*?:\s*(\w+)', stripped)
        if m:
            declared_names.add(m.group(1))
    by_prefix = {}
    for name in sorted(declared_names):
        by_prefix.setdefault(name[:10].upper(), []).append(name)
    for prefix, names in sorted(by_prefix.items()):
        if len(names) > 1:
            out.append('%s  %s all start "%s" - PLANC names are unique in their FIRST TEN '
                       'characters, so these are one identifier'
                       % (path, ' and '.join(names), prefix))

    # ---- an OUTPUT field pads AFTER the newline --------------------------------
    # 'ALnn' wider than its string pads to nn AFTER the $ has emitted the CRLF, so
    # the spaces land at the START of the next line. A /help built from padded
    # fields came out as a staircase. Exact-width fields have no padding at all.
    for n, line, _ in code_lines():
        for m in re.finditer(r"OUTPUT\s*\(\s*\d+\s*,\s*'A[LR]?(\d+)'\s*,\s*'((?:[^']|'')*)'", line):
            width = int(m.group(1))
            literal = m.group(2).replace("''", "'")
            if len(literal) < width:
                out.append("%s:%d  'AL%d' is WIDER than its %d-character string - the padding "
                           'lands after the newline and indents the NEXT line'
                           % (path, n, width, len(literal)))

    # ---- $EOF belongs in an INCLUDE, never in the main source ------------------
    body = [s for _, _, s in code_lines()]
    if any(s.upper().startswith('$EOF') for s in body):
        if any(s.upper().startswith('MODULE') for s in body):
            out.append('%s  $EOF in a MAIN source ends the compiler SESSION - the '
                       'commands after COMPILE then go to SINTRAN' % path)

    # ---- the includes must be INSIDE the module --------------------------------
    module_at = None
    for n, _, stripped in code_lines():
        if re.match(r'MODULE\b', stripped, re.I):
            module_at = n
            break
    if module_at is not None:
        for n, _, stripped in code_lines():
            if stripped.upper().startswith('$INCLUDE') and n < module_at:
                out.append('%s:%d  $INCLUDE above MODULE lands in the outer scope - the '
                           'body cannot see it and the include draws no diagnostic'
                           % (path, n))

    # ---- a name that is STORED TO but never DECLARED ---------------------------
    # PLANC accepted "TRUE =: openFailed" with openFailed declared nowhere in the
    # file, and the compile reported 0 DIAGNOSTICS. The program then ran with the
    # flag permanently reading TRUE, which sent a config-file save down the wrong
    # branch on every single call and cost most of a day.
    #
    # This scans for names on the RECEIVING side of "=:" and checks each one is
    # declared somewhere in the file. It is deliberately loose - any declaration
    # anywhere counts, and subscripted targets are ignored - because the point is
    # to catch a name that exists NOWHERE, not to model PLANC's scoping.
    # NOTE the RANGE clause: "INTEGER RANGE (0:255) : xmxOffset" is a declaration
    # and an earlier version of this rule missed it, reporting a perfectly good
    # variable as undeclared. A lint rule that cries wolf is worse than none.
    declared = set()
    for m in re.finditer(r'^\s*(?:' + TYPEALT + r')'
                         r'(?:\s+ARRAY)*(?:\s+RANGE\s*\([^)]*\))?\s*:\s*([^%\n]+)', text,
                         re.M | re.I):   # PLANC names are case-insensitive: SLiocInt is SLiocINT
        for name in re.findall(r'[A-Za-z_]\w*', m.group(1)):
            declared.add(name.upper())
    # a TYPE this file declares is a name like any other
    for name in own_types:
        declared.add(name.upper())

    # routine names, parameters and IMPORTed routines are declarations too
    # JOIN "&" CONTINUATIONS FIRST, or a routine whose header is split over two lines is
    # invisible here and its name is never recorded as declared.
    #
    # PLANC continues a line with a trailing "&", and a header with several parameters very
    # often uses it:
    #
    #     ROUTINE VOID, VOID (INTEGER, INTEGER, INTEGER, INTEGER) : &
    #             uiSaid(nameAt, nameLen, txtAt, txtLen)
    #
    # The pattern below stops at the newline, so the name never matched. MEASURED in CHAT.PLNC
    # on 2026-08-28: putInWin and uiSaid are both declared this way, and an analysis built on
    # the same per-line assumption reported the file as having 70 routines when it has 75 -
    # then left both of them out of a module split's import list, which would have failed the
    # build twenty minutes later.
    joined_text = re.sub(r'&[ \t]*\r?\n[ \t]*', ' ', text)
    for m in re.finditer(r'^\s*(?:ROUTINE|PROGRAM|MODULE)\b[^:\n]*:\s*(\w+)\s*(\(([^)]*)\))?',
                         joined_text, re.M):
        declared.add(m.group(1).upper())
        if m.group(3):
            for name in re.findall(r'[A-Za-z_]\w*', m.group(3)):
                declared.add(name.upper())
    for m in re.finditer(r'IMPORT\s*\(([^)]*)\)', text):
        for name in re.findall(r'[A-Za-z_]\w*', m.group(1)):
            declared.add(name.upper())
    # A $INCLUDE'd interface file declares names too - without this every
    # parameterless call into an included library (blankscreen, resetscreen)
    # is reported as a typo.
    for m in re.finditer(r'^\s*\$INCLUDE\s+(\S+)', text, re.M | re.I):
        declared |= include_names(path, m.group(1))

    # ---- TWO ROUTINES (OR A ROUTINE AND A PROGRAM) SHARING ONE NAME -----------
    #
    # PLANC's single pass treats a second "ROUTINE ... : sameName" as a
    # redeclaration of the first, and the compiler answers ONE clean error at
    # the header - IDENTIFIER ALREADY SPECIFIED/DECLARED - but then loses its
    # place: everything inside that second routine's own header line reads as
    # top-level statements, MISPLACED STATEMENT and ILLEGAL DATA TYPE, one per
    # line, until the ENDROUTINE closes it. MEASURED on D100 2026-08-31: a
    # second buildMembers (a new admin listing) collided with an existing one
    # (a trunk "who is on you" answer) and the single duplicate declaration
    # cost 215 diagnostics across the whole rest of the compile - once the
    # symbol table lost its footing, unrelated routines two thousand lines
    # away started reporting bogus ILLEGAL SYNTAX on their own, perfectly
    # good, parameter names.
    #
    # Single-line headers only, like the other checks in this file - a header
    # continued with a trailing "&" is rare and narrow beats clever.
    routine_line = {}
    for n, _, stripped in code_lines():
        m = re.match(r'^(?:ROUTINE|PROGRAM)\b[^:]*:\s*([A-Za-z_]\w*)', stripped)
        if not m:
            continue
        name = m.group(1).upper()
        if name in routine_line:
            out.append('%s:%d  "%s" is declared again here - it is ALREADY a ROUTINE or '
                       'PROGRAM at line %d. PLANC answers one clean error at the header and '
                       'then loses its place for the rest of the compile, so this single '
                       'collision can print hundreds of unrelated diagnostics elsewhere in '
                       'the file. Rename one of the two.'
                       % (path, n, m.group(1), routine_line[name]))
        else:
            routine_line[name] = n

    seen_undeclared = set()
    for n, _, stripped in code_lines():
        for m in re.finditer(r'=:\s*([A-Za-z_]\w*)\s*(?![\w(])', stripped):
            name = m.group(1)
            if name.upper() in declared or name.upper() in seen_undeclared:
                continue
            seen_undeclared.add(name.upper())
            out.append('%s:%d  "%s" is stored to but never DECLARED anywhere in this file - '
                       'PLANC compiles that with 0 DIAGNOSTICS and the program then runs on a '
                       'value nothing sets' % (path, n, name))

    # ---- a bare name on a line of its own must BE a routine --------------------
    # THIS IS THE ONE THAT SHIPPED A BROKEN CLIENT FOR DAYS. CHAT.PLNC called
    #
    #     setMyName(at, argLen)
    #     showMyName            <- no such routine, anywhere in the file
    #     sendJoin
    #
    # and PLANC answered, on EVERY build,
    #
    #     2494  (1834)/HANDLECOMM  *** ERROR   - ILLEGAL SYNTAX "SHOWMYNAME"
    #
    # Nobody saw it. The compiler prints diagnostics as it goes and on a source
    # this long they scroll off a 24-line screen; the "0 DIAGNOSTICS" left on
    # screen belongs to the LINKER and sits happily under a compile that failed.
    # The listing is the only place a PLANC error survives, and CHAT:LIST had
    # never once been read. Builds went to the machine broken for days.
    #
    # A call with no parameters is just the name, so it is indistinguishable from
    # a typo by eye - which is exactly why it wants a machine to check it.
    #
    # A line ending in "&" continues onto the next, so the next line is an
    # ARGUMENT and not a statement: skipped, or every continued call is a
    # false alarm.
    STATEMENT_WORDS = {
        'RETURN', 'ENDIF', 'ENDDO', 'ENDFOR', 'ENDON', 'ENDROUTINE', 'ENDMODULE',
        'ENDPROGRAM', 'ENDRECORD', 'ENDCASE', 'ENDMACRO', 'ELSE', 'DO', 'THEN',
        'ENDVAL', 'ENDTYPE', 'GO', 'EXIT',
    }
    prev_continued = False
    for n, _, stripped in code_lines():
        if not stripped.strip():
            continue
        m = re.match(r'^\s*([A-Za-z_]\w*)\s*$', stripped)
        if m and not prev_continued:
            name = m.group(1)
            if name.upper() not in STATEMENT_WORDS and name.upper() not in declared:
                out.append('%s:%d  "%s" is CALLED on a line of its own but is declared '
                           'NOWHERE in this file - PLANC answers *** ERROR ILLEGAL SYNTAX '
                           'and that error only ever reaches the LISTING, which is why a '
                           'build like this can go to the machine looking fine'
                           % (path, n, name))
        prev_continued = stripped.rstrip().endswith('&')

    # =======================================================================
    # XMSG / XMP RULES - see Developer/Languages/Application/PLANC-XMSG-API-RULES.md
    # Skipped entirely when the API data file is not present.
    # =======================================================================
    if XMP_API:
        routines = XMP_API.get('routines', {})

        # ---- wrong ARGUMENT COUNT for a documented XMP routine -------------
        # PLANC will catch this, but only in the listing, and only after a
        # four-minute compile. Here it costs nothing. Continuation lines end
        # with "&", so a call is joined up before its arguments are counted.
        joined = []
        buf, start = '', 0
        for n, _, stripped in code_lines():
            s = mask_strings(stripped).rstrip()
            if not buf:
                start = n
            buf += ' ' + s[:-1] if s.endswith('&') else ' ' + s
            if not s.endswith('&'):
                joined.append((start, buf))
                buf = ''
        if buf:
            joined.append((start, buf))

        for n, text_line in joined:
            for m in re.finditer(r'\b(xmp\w+)\s*\(', text_line, re.I):
                name = m.group(1).lower()
                spec = routines.get(name)
                if not spec or not isinstance(spec.get('params'), list):
                    continue
                # Count arguments by scanning to the matching close paren, so a
                # nested call or a subarray "a(0:n-1)" does not split the count.
                i = m.end()
                depth, args, seen = 1, 1, False
                while i < len(text_line) and depth > 0:
                    ch = text_line[i]
                    if ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                    elif ch == ',' and depth == 1:
                        args += 1
                    if depth == 1 and ch not in ' \t':
                        seen = True
                    i += 1
                if depth != 0:
                    continue                      # unbalanced - do not guess
                if not seen:
                    args = 0
                want = len(spec['params'])
                if args != want:
                    names = ', '.join(p.get('name', '?') for p in spec['params'])
                    out.append('%s:%d  %s takes %d parameter(s) but %d given - (%s)'
                               % (path, n, name, want, args, names))

        # WHICH VARIABLES CARRY A WAIT OR A WAKE-UP.
        #
        # THE REAL BUG PASSED A VARIABLE, WHICH IS WHY A LITERAL-ONLY RULE MISSED
        # IT. CHATSV said "2**XFWAK =: waitFlags" once, near the top of the
        # PROGRAM, and the receive four hundred lines later read
        # "xmpfrcv(waitFlags, myPort, ...)". Nothing on the call line mentions a
        # flag at all. A checker that only looks at the argument text sees
        # nothing wrong with the line that actually parked the server.
        tainted = set()
        for _, text_line in joined:
            for m in re.finditer(r'([^=]*?)=:\s*([A-Za-z_]\w*)\s*$', text_line):
                if re.search(r'\bXFWTF\b', m.group(1), re.I):
                    tainted.add(m.group(2).upper())
        for m in re.finditer(r'INTEGER\s*:\s*(\w+)\s*:=\s*([^%\n]*)', text, re.I):
            if re.search(r'\bXFWTF\b', m.group(2), re.I):
                tainted.add(m.group(1).upper())

        def flags_blocking(arg):
            """Does this flags argument make the receive BLOCK?

            XFWTF ONLY. XFWAK was lumped in here and that was wrong - see the
            note on the multi-port check below. A blocking receive parks the
            task on one port; arming a doorbell does not.
            """
            if re.search(r'\bXFWTF\b', arg, re.I):
                return True
            bare = arg.strip().upper()
            return bare in tainted

        # ---- a receive whose flags argument is a BIT POSITION ---------------
        # XFWTF is 15 and XFWAK is 14 - POSITIONS, not values. Passed raw they
        # are nonsense flags. The value is 2**XFWAK.
        for n, text_line in joined:
            m = re.search(r'\b(%s)\s*\(\s*(XF\w+)\s*,' % '|'.join(RECEIVE_ROUTINES),
                          text_line, re.I)
            if m:
                out.append('%s:%d  %s flags argument is "%s", which is a BIT POSITION, not a '
                           'value - write 2**%s, or 0 for no options'
                           % (path, n, m.group(1).lower(), m.group(2), m.group(2)))

        # ---- TWO PORTS AND A WAIT OR A WAKE-UP ------------------------------
        # THE ONE THAT PARKED THE SERVER FOR HALF A SESSION. XFRCV receives on
        # ONE port; there is no receive-on-any. Armed on two, the task sits on
        # one doorbell while a message waits on the other - measured on D100
        # with LIST-PORTS showing Qlen 1 WAK 0 on the room port and WAK 1 on
        # the admin port. Poll BOTH with flags 0 and sleep between passes.
        recv_ports, flag_lines = {}, []
        for n, text_line in joined:
            for m in re.finditer(r'\b(%s)\s*\(([^,]*),\s*([A-Za-z_]\w*)'
                                 % '|'.join(RECEIVE_ROUTINES), text_line, re.I):
                flags_arg, port_arg = m.group(2).strip(), m.group(3)
                recv_ports.setdefault(port_arg.upper(), n)
                if flags_blocking(flags_arg):
                    flag_lines.append(n)
        # NARROWED 2026-08-28, and the reason is worth keeping.
        #
        # This check used to refuse XFWAK as well as XFWTF, on the strength of a
        # comment in CHATSV.PLNC saying XFWAK "HUNG THE SERVER" on 2026-08-21.
        # Carved from git history that day it does not hold:
        #
        #   - XFWAK appears ZERO times in the version before the outage;
        #   - it first entered CHATSV.PLNC on 2026-08-25, FOUR DAYS AFTER it;
        #   - that build had ONE xmpfrcv, on myPort, with 2**XFWTF - the
        #     blocking flag - and no admin receive at all.
        #
        # So the outage is explained by the BLOCKING receive, which is what the
        # rest of this check is about, and the doorbell was blamed for something
        # it was not present for. A non-blocking XFWAK parks nothing.
        #
        # STILL UNEXPLAINED: the LIST-PORTS capture from that day shows WAK 1 on
        # the admin port, and the committed source has neither an admin receive
        # nor XFWAK. Either the running build was uncommitted or something else
        # sets that bit. Worth re-checking live before trusting the doorbell.
        if len(recv_ports) > 1 and flag_lines:
            where = ', '.join(str(x) for x in sorted(set(flag_lines)))
            ports = ', '.join(sorted(recv_ports))
            out.append('%s:%d  receives on %d DIFFERENT ports (%s) with XFWTF set '
                       '(line(s) %s) - XFRCV waits on ONE port, so the task parks on one while '
                       'a message sits on the other. Poll both with flags 0 and sleep'
                       % (path, min(recv_ports.values()), len(recv_ports), ports, where))

        # ---- the two status tests that are both wrong -----------------------
        # "> 0" accepts XMXENTM (16896, an EMPTY port) and every error.
        # ">< XMOK" alone discards every message, because a receive may answer
        # a MESSAGE TYPE (XMTNO..XMTPS) as success. That one silently ate a
        # welcome and cost a day.
        # SCOPED TO THE LINES JUST AFTER A RECEIVE, and that scoping is the whole
        # difficulty. The same "returnStatus" variable is reused for xmpblet,
        # xmpopcn, xmpfsnd and the rest, where ">< XMOK" is exactly right - so
        # flagging every occurrence of the name reported 21 false alarms on
        # three good files. A lint rule that cries wolf is worse than none.
        recv_lines = []      # (line number, result variable)
        for n, text_line in joined:
            for m in re.finditer(r'\b(?:%s)\s*\([^)]*\)\s*&?\s*=:\s*([A-Za-z_]\w*)'
                                 % '|'.join(RECEIVE_ROUTINES), text_line, re.I):
                recv_lines.append((n, m.group(1).upper()))

        WINDOW = 6           # a receive and its status test are always close together
        by_line = dict((n, s) for n, _, s in code_lines())
        for rn, var in recv_lines:
            for n in range(rn, rn + WINDOW + 1):
                stripped = by_line.get(n)
                if stripped is None:
                    continue
                if re.search(r'\b%s\s*>\s*0' % re.escape(var), stripped, re.I):
                    out.append('%s:%d  "%s > 0" tests the result of the receive on line %d, and '
                               'accepts an EMPTY port - XMXENTM is 16896, and every error is '
                               'positive too. Accept XMOK OR XMTNO..XMTPS' % (path, n, var, rn))
                if re.search(r'\b%s\s*><\s*XMOK' % re.escape(var), stripped, re.I) \
                        and 'XMT' not in stripped.upper():
                    out.append('%s:%d  "%s >< XMOK" tests the result of the receive on line %d '
                               'and nothing else - that DISCARDS every message whose status is '
                               'a message TYPE (XMTNO..XMTPS), which is a successful receive too'
                               % (path, n, var, rn))

        # ---- no way out when XMSG dies underneath a POLLING loop ------------
        # XMXENRU (16933) is "XMSG not running". A poller that never looks for
        # it spins for ever on a dead kernel - which burned the machine once.
        # Only for a program that actually POLLS: the TimeOut sleep is the sign
        # of a loop meant to run for ever. A one-shot command program that
        # receives an answer and exits does not need this.
        if recv_lines and 'TIMEOUT' in text.upper() \
                and 'XMXENRU' not in text.upper() and 'XENRU' not in text.upper():
            out.append('%s  this program polls in a loop but never mentions XMXENRU (16933, '
                       '"XMSG not running") - when XMSG dies the receive stops blocking and the '
                       'loop has no way out' % path)

    # ---- a LOCAL filespec in a SINTRAN command must not be quoted --------------
    # The two routes to "make me a file" take OPPOSITE quoting:
    #
    #   MON50(file, ...)    quoting the name means CREATE IT IF ABSENT
    #   CREATE-FILE <name>  quoting the name is an ILLEGAL CHARACTER IN PARAMETER
    #
    # so a quoted name copied from the first into the second fails every time.
    # Measured on D100 2026-08-19: 'CREATE-FILE "CHAT:CNFG",1' handed to MON70
    # answered ILLEGAL CHARACTER IN PARAMETER, the file was never created, and
    # every nickname save had been failing silently since the day it was written.
    #
    # Quoting IS right for a REMOTE filespec, which goes to another machine's
    # command processor - so this only flags a name with no system prefix.
    for n, _, stripped in code_lines():
        m = re.search(r"'([^']*\b(?:CREATE-FILE|DELETE-FILE|RENAME-FILE)\s+\"[^\"]+\")",
                      stripped, re.I)
        if m and '(' not in m.group(1).split('"')[0][-3:]:
            out.append('%s:%d  a LOCAL filespec in a SINTRAN command must NOT be quoted - '
                       'it answers ILLEGAL CHARACTER IN PARAMETER. Quotes mean "create" to '
                       'MON50 and are illegal to CREATE-FILE, which is exactly how they get '
                       'copied from one to the other' % (path, n))

    # ---- a STRING literal cannot be stored into a BYTES element ----------------
    # "' ' =: outBuf(at)" reads perfectly and does not compile. 'x' is a STRING;
    # an element of a BYTES array is a BYTE. The compiler answers
    #
    #   1082   (422)/BUILDWHO  *** ERROR   - ILLEGAL DATA TYPE "OUTBUF"
    #
    # naming the ARRAY rather than the literal, which sends you looking at the
    # declaration - where nothing is wrong. Hold the character in a one-element
    # BYTES and copy element to element instead.
    for n, _, stripped in code_lines():
        m = re.search(r"'(?:[^']|'')*'\s*=:\s*([A-Za-z_]\w*)\s*\(", stripped)
        if m:
            out.append("%s:%d  a STRING literal cannot be stored into %s(...) - an "
                       "element of a BYTES array is a BYTE. Put the character in a "
                       "one-element BYTES and copy element to element. The compiler "
                       'blames the ARRAY ("ILLEGAL DATA TYPE"), not the literal'
                       % (path, n, m.group(1)))

    # ---- 'ALn' must be the length of the literal it formats --------------------
    # 'ALn' is a FIELD WIDTH, not a hint: too small and the tail of the line is
    # cut off, too large and OUTPUT runs past the end of the literal. The count
    # includes the trailing '$' when there is one, because that is a character in
    # the string like any other.
    #
    # Nothing in the compiler checks this - a wrong width builds clean and shows
    # up only as a truncated line on a terminal nobody may be watching. Five were
    # introduced in one sitting adding /who and the room name to CHAT.PLNC.
    for m in re.finditer(r"'AL(\d+)'\s*,\s*'((?:[^']|'')*)'", text):
        want = int(m.group(1))
        # '' is how a PLANC literal carries one quote, so it counts as one byte.
        got = len(m.group(2).replace("''", "'"))
        if want != got:
            n = text[:m.start()].count('\n') + 1
            out.append("%s:%d  'AL%d' but the literal is %d characters - the width "
                       "includes the trailing '$'" % (path, n, want, got))

    # ---- a MESSAGE KIND that is declared and never handled ---------------------
    # THIS HAS NOW BITTEN THREE TIMES IN THE SAME PROGRAM, and every time it was
    # SILENT - which is what makes it worth a rule rather than a note.
    #
    #  1. kReject was declared and never tested, so a refusal fell through to the
    #     "<name>: <text>" printer and came out as
    #         OLAV: that nickname is taken
    #     - the server's words ABOUT a user, printed as that user speaking.
    #  2. kSaid, kJoined and kLeft appear NOWHERE outside their declarations. All
    #     three land on the same fall-through, and only kSaid is speech, so a join
    #     notice prints as a bare "SYSTEM:" line that reads as screen noise.
    #  3. writeCnfg hangs off kRenamed while the server answers kWelcome, so a
    #     nickname is confirmed on screen and never saved.
    #
    # A kind nobody handles produces NO error at all - not from the compiler, not
    # at run time - so it looks like a save failure, or a display glitch, or
    # nothing. The declaration is the only evidence that the case was intended.
    #
    # The rule: a constant whose name matches k<UpperCamel> and which appears
    # exactly once in the file (its own declaration) is almost certainly a case
    # nobody wrote. Names sent rather than received (kJoin, kSay, kLeave, kRename,
    # kWho) are still worth flagging - a kind this program never mentions again is
    # either dead or forgotten, and both want saying out loud.
    kind_decl = re.compile(r'^\s*(?:INTEGER|CONSTANT)\s*:\s*(k[A-Z][A-Za-z]*)\s*:=\s*(\d+)')
    declared = []
    for n, line, stripped in code_lines():
        m = kind_decl.match(stripped)
        if m:
            declared.append((n, m.group(1), m.group(2)))

    if declared:
        # Count uses across CODE only - a name mentioned in a comment is being
        # discussed, not handled, and that is exactly the state this rule exists
        # to catch.
        body = []
        for n, line, stripped in code_lines():
            body.append(mask_strings(strip_comment(line)))
        body_text = '\n'.join(body)
        for n, name, value in declared:
            uses = len(re.findall(r'\b%s\b' % re.escape(name), body_text))
            if uses <= 1:
                out.append("%s:%d  message kind %s (=%s) is declared and never used "
                           "again - an unhandled kind is SILENT: it falls through to "
                           "whatever the last branch is, or vanishes"
                           % (path, n, name, value))

    # ---- A NAME USED IN A ROUTINE THAT THE ROUTINE CANNOT SEE -----------------
    #
    # MEASURED 2026-08-22: showArrived in CHAT.PLNC used "nameAt", which exists
    # in that file ONLY as a parameter of setMyName. Six minutes into a compile
    # on D100 the answer came back as
    #
    #     2465 (1805)/SHOWARRIVE  *** ERROR   - ILLEGAL SYNTAX "NAMEAT"
    #
    # "ILLEGAL SYNTAX" is a misleading way to say "I have never heard of this
    # name" - the line is perfectly well formed. Worse, a file-wide "is it
    # declared anywhere" check would NOT have caught it, because the name is
    # declared, just not anywhere this routine can see. So the check has to know
    # about SCOPE: a routine sees its own parameters, its own locals, everything
    # declared at module level, the other routines, and the imports. Nothing
    # else.
    #
    # DELIBERATELY CONSERVATIVE. A linter that cries wolf gets ignored, and this
    # one is run before every build, so anything it cannot resolve confidently is
    # left alone rather than reported. It only ever looks at names that appear in
    # a position where a variable is being READ or WRITTEN.
    kw = set("""
        IF THEN ELSE ELSIF ENDIF DO ENDDO OD FOR IN BY ENDFOR WHILE UNTIL
        RETURN ROUTINE ENDROUTINE PROGRAM ENDPROGRAM MODULE ENDMODULE
        IMPORT EXPORT INTEGER INTEGER1 INTEGER2 INTEGER4 BYTE BYTES BOOLEAN
        REAL REAL4 REAL6 REAL8 VOID ARRAY RECORD ENDRECORD POINTER LABEL
        ENUMERATION CONSTANT TRUE FALSE AND OR NOT XOR ABS ADDR SIZE IND
        OUTPUT INPUT GO TO ON OFF ROUTINEERROR ENDON CASE ENDCASE OTHERWISE
        MOD SHIFT NIL PRECISION STANDARD ALIAS INLINE REFERENCE VALUE
        FORCE MONITOR_CALL
        ERRCODE ERRCLASS ERRPARAM
        INCASE RANGE ENDINCASE SELECT ENDSELECT GOTO EXITWHEN GLOBAL LOCAL
        GENERATE FREE NEW DISPOSE GENERALIZED PACKED GO_TO
        MAXINDEX MININDEX BIT_SIZE BLOCKSIZE FILESIZE
        INISTACK
        """.split())

    # INISTACK IS A STATEMENT, NOT A VARIABLE, and it went unnoticed for one
    # reason only: it appears exactly once per program, in the PROGRAM body,
    # and the PROGRAM body was the one region this check never looked at.
    # The moment PROGRAM became a scope, all six sources reported it. Every
    # one of those was the linter being wrong, not the source.

    # MAXINDEX and MININDEX are STANDARD ROUTINES the compiler provides - they
    # need no IMPORT and no declaration, so the undeclared-name check must not
    # report them. Added 2026-08-25 after MAXINDEX(text,1) - which is how a
    # routine asks a BYTES parameter how long it is instead of being handed a
    # hand-counted number - was reported as undeclared.
    #
    # ND-60.117.5 section 3.17 and page 153: MAXINDEX(array-identifier,
    # dimension-number) returns the DECLARED UPPER BOUND. One real restriction
    # is worth knowing and is NOT checked here: page 249 says MININDEX and
    # MAXINDEX for array parameters are NOT available in a STANDARD routine,
    # the FORTRAN/COBOL calling sequence. An ordinary PLANC routine is fine.

    # Every declared name in the file, with where it was declared. A module-level
    # declaration is one that is not inside a ROUTINE ... ENDROUTINE.
    # A DECLARATION IS "<type stuff> : <names>", and "type stuff" is richer than
    # the builtin list. Both of these are declarations and both were missed by a
    # narrower pattern, each producing a page of false alarms:
    #
    #     XMMSGIDENTIFIER : ident            a TYPE from the XMSG library
    #     INTEGER RANGE (0:255) : xmxOffset  a range-limited integer
    #
    # The ":" must not be the store operator "=:", hence the lookbehind.
    builtin_types = set("""
        INTEGER INTEGER1 INTEGER2 INTEGER4 BYTE BYTES BOOLEAN REAL REAL4 REAL6
        REAL8 POINTER LABEL ENUMERATION VOID
        """.split())

    # AND THE TYPES THIS FILE DECLARES FOR ITSELF. "TYPE xrAddr = INTEGER4" is a
    # perfectly ordinary type once written, and "xrAddr : addrA, addrB" is a
    # perfectly ordinary declaration - but a checker that knows only the builtin
    # names and the XMSG XM* family calls the type undeclared AND both variables
    # undeclared with it. Measured 2026-08-27: four invented problems in a file
    # that was correct.
    builtin_types |= set(t.upper() for t in own_types)
    decl_re = re.compile(
        r'^\s*([A-Za-z][A-Za-z0-9_]*)'          # the base type
        r'((?:\s+(?:ARRAY|RANGE|PACKED|POINTER))*'
        r'\s*(?:\([^)]*\))?)'                   # ARRAY / RANGE (0:255) / bounds
        r'\s*(?<![=:]):\s*(.+)$')

    def is_declaration(stripped):
        m = decl_re.match(stripped)
        if not m:
            return None
        base = m.group(1).upper()
        # A builtin, or one of the XMSG library's own types - those are all
        # spelled XM<something> in XMP-B02:DEFS.
        if base in builtin_types or re.match(r'^XM[A-Z0-9_]+$', base):
            return m.group(3)
        return None
    # "ROUTINE VOID, INTEGER (INTEGER, INTEGER) : name(a, b)" - possibly with the
    # ": name(...)" part on the next line after a trailing "&".
    # A PROGRAM IS A SCOPE, EXACTLY LIKE A ROUTINE, and leaving it out cost a
    # build cycle on 2026-08-25.
    #
    # This used to match ROUTINE only. A PROGRAM's own locals therefore fell
    # through to module_names, which does two bad things at once: the main
    # program's body - the biggest single block in a screen program - was never
    # scope-checked at all, and its locals were treated as visible to EVERY
    # routine in the file, hiding undeclared names everywhere else too.
    #
    # What it let through: CHATUI's main loop used "waiting", which is declared
    # in pollKey and nowhere else. PLANC accepts an undeclared name silently, so
    # the only symptom would have been a variable that never held what it was
    # given. The lint said "clean".
    #
    # A PROGRAM closes with ENDROUTINE, the same keyword, so nothing below
    # needs changing.
    routine_re = re.compile(r'^\s*(?:ROUTINE|PROGRAM)\b(.*)$', re.IGNORECASE)

    def names_in(decl_tail):
        """The identifiers a declaration introduces.

        "i, j, at" -> i j at;  "mbrRoom(1:16, 1:16)" -> mbrRoom;
        "spaceByte := ' '" -> spaceByte. Anything inside brackets or after ":="
        is a SIZE or an INITIAL VALUE, not a new name.
        """
        found = []
        depth = 0
        current = ''
        for ch in decl_tail:
            if ch == '(':
                depth += 1
                continue
            if ch == ')':
                depth -= 1
                continue          # NOT appended - "outBuf(0:255)" must not
                                  # become "outBuf)", which matches no
                                  # identifier and silently drops the name.
                                  # That slip made the first run of this rule
                                  # report every module-level buffer in the
                                  # file as undeclared.
            if depth == 0 and ch == ',':
                found.append(current)
                current = ''
                continue
            if depth == 0:
                current += ch
        found.append(current)
        outn = []
        for piece in found:
            piece = piece.split(':=')[0].split('(')[0].strip()
            m = re.match(r'^([A-Za-z][A-Za-z0-9_]*)$', piece)
            if m:
                outn.append(m.group(1))
        return outn

    # Join continuation lines so a "&"-wrapped routine header reads as one line.
    joined = []          # (line_number_of_first_physical_line, text)
    pending_n, pending = None, ''
    for i, line in enumerate(lines):
        code = mask_strings(strip_comment(line)).rstrip()
        if pending_n is None:
            pending_n = i + 1
        if code.endswith('&'):
            pending += code[:-1] + ' '
            continue
        pending += code
        joined.append((pending_n, pending))
        pending_n, pending = None, ''

    module_names = set()
    # Module names declared WITH an initialiser - see the note where this is
    # filled. These are the ones a parameter may not reuse.
    module_consts = set()
    routine_names = set()
    import_names = set()

    # Names that arrive through a local $INCLUDE - see include_names().
    for _n, _code in joined:
        _m = re.match(r'^\$INCLUDE\s+(\S+)', _code.strip(), re.IGNORECASE)
        if _m:
            import_names |= include_names(path, _m.group(1))

    # Names defined by $CONSTANT - PLANC's compile-time constants, the other
    # half of its $IF conditional compilation (appendix A 0.9). A $IF line
    # naming one is a DIRECTIVE, not code, so the name is visible everywhere
    # and the line itself must never be read as a use inside a routine.
    # Added 2026-09-01 when the DBGUI instrument switch drew a false
    # undeclared-name finding.
    for _n, _code in joined:
        _m = re.match(r'^\$CONSTANT\s+(.+)$', _code.strip(), re.IGNORECASE)
        if _m:
            for _item in _m.group(1).split(','):
                _nm = re.match(r'\s*([A-Za-z][A-Za-z0-9_]*)', _item)
                if _nm:
                    import_names.add(_nm.group(1).upper())

    # (name, first_line, last_line, params, locals)
    routines = []
    cur = None
    in_import = False

    for n, code in joined:
        stripped = code.strip()
        if not stripped:
            continue

        if re.match(r'^\s*IMPORT\b', stripped, re.IGNORECASE):
            in_import = True
        if in_import:
            for m in re.finditer(r':\s*([A-Za-z][A-Za-z0-9_]*)', stripped):
                import_names.add(m.group(1).upper())
            if ')' in stripped:
                in_import = False
            continue

        rm = routine_re.match(stripped)
        if rm and not re.match(r'^\s*ENDROUTINE', stripped, re.IGNORECASE):
            # The declared name and its parameter list are after the LAST ":".
            tail = stripped.rsplit(':', 1)[-1].strip()
            nm = re.match(r'^([A-Za-z][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?', tail)
            if nm:
                params = []
                if nm.group(2):
                    for p in nm.group(2).split(','):
                        p = p.strip()
                        if re.match(r'^[A-Za-z][A-Za-z0-9_]*$', p):
                            params.append(p.upper())
                cur = {'name': nm.group(1).upper(), 'start': n, 'end': None,
                       'params': set(params), 'locals': set()}
                routine_names.add(nm.group(1).upper())
                routines.append(cur)
            continue

        if re.match(r'^\s*ENDROUTINE', stripped, re.IGNORECASE):
            if cur is not None:
                cur['end'] = n
                cur = None
            continue

        # CONSTANT IS A DECLARATION WITH NO COLON IN IT.
        #
        # "CONSTANT maxlen=100, pi=3.14" (manual 3.5 p.86) introduces names just
        # as "INTEGER : n" does, but the declaration pattern above looks for a
        # ":" and so never saw it. Every CONSTANT in a file was reported as
        # undeclared at its first use.
        cm = re.match(r'^CONSTANT\s+(.+)$', stripped, re.IGNORECASE)
        if cm is not None:
            for part in cm.group(1).split(','):
                nm4 = re.match(r'\s*([A-Za-z][A-Za-z0-9_]*)', part)
                if nm4:
                    if cur is not None:
                        cur['locals'].add(nm4.group(1).upper())
                    else:
                        module_names.add(nm4.group(1).upper())
                        module_consts.add(nm4.group(1).upper())
            continue

        dm = is_declaration(stripped)
        if dm is not None:
            initialised = ':=' in dm
            for nm2 in names_in(dm):
                if cur is not None:
                    cur['locals'].add(nm2.upper())
                else:
                    module_names.add(nm2.upper())
                # A PLANC LOCAL CANNOT CARRY AN INITIALISER - "INTEGER : x := 1"
                # inside a routine draws INITIAL VALUE ILLEGAL HERE. So anything
                # with a ":=" is certainly module level, whatever this parser
                # thinks the surrounding scope is. That makes it the one set of
                # names we can be SURE about, which is why the parameter rule
                # below tests against it and not against module_names.
                if initialised:
                    module_consts.add(nm2.upper())

    # PROGRAM/MODULE bodies are not routines; anything declared there is visible
    # to the code in them, and that code is not checked here.
    xmp_names = set()
    if XMP_API:
        for section in ('routines', 'constants'):
            entries = XMP_API.get(section) or []
            for e in entries:
                nm3 = e.get('name') if isinstance(e, dict) else e
                if isinstance(nm3, str):
                    xmp_names.add(nm3.upper())

    # A type this file declares is visible everywhere in it, exactly like a
    # builtin type name - it is used as the return type of a routine and as the
    # base of a declaration, and neither is a place a variable could be.
    visible_everywhere = (module_names | routine_names | import_names | xmp_names
                          | kw | set(t.upper() for t in own_types))

    # ---- TWO NAMES THAT ARE THE SAME IN THEIR FIRST TEN CHARACTERS ------------
    #
    # PLANC KEEPS TEN. "buildAdminNum" IS "buildAdmin", so declaring it beside an
    # existing buildAdmin is declaring the same routine twice:
    #
    #     950 (290) *** ERROR - IDENTIFIER ALREADY SPECIFIED/DECLARED "BUILDADMIN"
    #
    # and then TWENTY-FOUR more diagnostics, because the second declaration's
    # body is parsed as though it were loose statements - NOT PREVIOUSLY DECLARED
    # "KIND", MISPLACED STATEMENT, and so on down the routine. Only the FIRST
    # line means anything. Measured on D100, 2026-08-22.
    #
    # Checked across routine names AND module-level names together, since the
    # truncation does not care which kind of thing it is.
    seen_short = {}
    for n, code in joined:
        m = re.match(r'^\s*ROUTINE\b.*?:\s*([A-Za-z][A-Za-z0-9_]*)', code.strip(),
                     re.IGNORECASE)
        if m:
            full = m.group(1)
            short = full.upper()[:10]
            if short in seen_short and seen_short[short][0].upper() != full.upper():
                out.append('%s:%d  "%s" and "%s" (line %d) are THE SAME NAME to '
                           'PLANC - it keeps only the first ten characters. The '
                           'compiler answers IDENTIFIER ALREADY SPECIFIED/DECLARED '
                           'and then mis-parses the whole routine; only that first '
                           'line is real.'
                           % (path, n, full, seen_short[short][0], seen_short[short][1]))
            else:
                seen_short[short] = (full, n)

    # ---- ASSIGNING FROM A ROUTINE THAT RETURNS VOID ---------------------------
    #
    # "ROUTINE VOID, VOID (INTEGER) : addPeer" returns nothing, so
    #
    #     addPeer(taken) =: length
    #
    # is not a value to store. The compiler answers
    #
    #     3005 (2345)/HANDLEMESS *** ERROR - ILLEGAL DATA TYPE "ADDPEER"
    #
    # naming the ROUTINE, which reads like a problem with the argument rather
    # than with the assignment. Measured on D100 2026-08-22, twice in one
    # compile.
    #
    # This one is safe to check because both halves are unambiguous in the text:
    # the declaration says "VOID, VOID" and the call site has "=:" after it.
    void_routines = set()
    for n, code in joined:
        m = re.match(r'^\s*ROUTINE\s+VOID\s*,\s*VOID\b.*?:\s*([A-Za-z][A-Za-z0-9_]*)',
                     code.strip(), re.IGNORECASE)
        if m:
            void_routines.add(m.group(1).upper())
    for n, code in joined:
        stripped = mask_strings(strip_comment(code))
        for m in re.finditer(r'\b([A-Za-z][A-Za-z0-9_]*)\s*\([^()]*\)\s*=:', stripped):
            if m.group(1).upper() in void_routines:
                out.append('%s:%d  "%s" is declared "ROUTINE VOID, VOID" - it returns '
                           'nothing, so there is no value to store. The compiler '
                           'answers ILLEGAL DATA TYPE and names the ROUTINE, which '
                           'looks like an argument problem. Drop the "=:".'
                           % (path, n, m.group(1)))

    # ---- NOT A RULE: THE SUBARRAY-OF-AN-INITIALISED-BYTES TRAP ----------------
    #
    # There IS a real trap here and it has cost two compile cycles, but it is NOT
    # understood well enough to check, and a rule that flags working code is
    # worse than no rule at all.
    #
    # WHAT IS MEASURED:
    #   FAILS  CHATSV sendToName, slicing a BYTES FORMAL PARAMETER bound to
    #          trkName:  xmpblet(..., portName(0:nmLen - 1))
    #          -> 2512 (1852)/SENDTONAME *** ERROR - ILLEGAL DATA TYPE "XMPBLET"
    #   FAILS  CHATMON sendAdmin, per its own comment of 2026-08-20, slicing
    #          admName directly: xmpblet(..., admName(0:lenAdmName - 1))
    #          -> 830 (170)/SENDADMIN *** ERROR - ILLEGAL DATA TYPE "XMPBLET"
    #   WORKS  CHAT sendJoin, slicing servName directly:
    #          xmpblet(..., servName(0:lenServName - 1))          compiles clean
    #   WORKS  every xmpopnm here, slicing admName / trkName directly.
    #
    # The first draft of this rule flagged all four and would have condemned two
    # programs that build. Whatever separates the failing cases from the working
    # ones, it is not "initialised BYTES gets sliced" - so nothing is asserted.
    #
    # THE SAFE HABIT, until somebody carves it properly: pass the WHOLE array to
    # xmpblet when the BYTES was declared with an initialiser. That works in
    # every case above.

    # ---- A PARAMETER THAT REUSES A MODULE-LEVEL NAME --------------------------
    #
    # PARAMETERS ONLY. A routine LOCAL may shadow a module-level name perfectly
    # happily - "INTEGER : i" inside a routine while the module also has an "i"
    # is everywhere in these programs and has built for days. The first version
    # of this rule checked locals too and reported 51 problems across files that
    # compile clean, which would have made it useless: a linter that cries wolf
    # gets switched off, and this one runs before every build.
    #
    # A PARAMETER is different, and that difference is what cost the cycle:
    #
    #     2502 (1842)/SENDTONAME *** ERROR - IDENTIFIER ALREADY SPECIFIED/DECLARED "NAMELEN"
    #
    # and it does not stop there. The parameter list comes apart, so the next
    # three lines of the same routine each drew their own diagnostic - ILLEGAL
    # SYNTAX on a parameter that was perfectly good, then two ILLEGAL DATA TYPEs.
    # Reading the FIRST error is the only way through that; the others are noise.
    #
    # Measured on D100 2026-08-22: "sendToName(portName, nameLen, ...)" against a
    # module-level "INTEGER : nameLen := 16". One full compile cycle.
    for r in routines:
        if r['end'] is None:
            continue
        for nm5 in sorted(r['params']):
            if nm5 in module_consts:
                out.append('%s:%d  %s\'s PARAMETER "%s" reuses a module-level name '
                           'that has an INITIALISER - the compiler answers '
                           'IDENTIFIER ALREADY SPECIFIED/DECLARED and then '
                           'mis-parses the rest of the routine. Rename the '
                           'parameter.' % (path, r['start'], r['name'], nm5))

    # ---- A HAND-COUNTED LENGTH BESIDE A LITERAL -------------------------------
    #
    # These are this project's own helpers, and each one USED to take the length
    # beside the literal - exactly the trap that 'ALnn' has, and for the same
    # reason: nothing checked it, a wrong number built clean, and the only
    # symptom was a sentence cut short or trailing rubbish on somebody's screen.
    # A count too SMALL truncates; too LARGE reads past the end of the literal,
    # and PLANC checks no array bounds, so it prints whatever sits after it.
    #
    # ON 2026-08-31 THE PARAMETER WAS REMOVED FROM ALL OF THEM. Each helper now
    # asks the string itself with MAXINDEX(text, 1) + 1, which deleted 93
    # hand-typed numbers across the chat sources - 18 buildAdmText, 29 putWord,
    # 19 logLine, 14 cmdIs, 15 tryCmd and 12 showIfMatch - none of which could
    # ever be checked by anything but a human counting characters.
    #
    # So this rule now has TWO jobs, and the second is the lasting one:
    #
    #   1. if a helper still takes a length, the number must match the literal;
    #   2. if a helper no longer takes one, passing a number is the OLD shape
    #      coming back - say so by name, because the compiler's own complaint
    #      about the parameter list does not mention MAXINDEX or why the
    #      parameter went away.
    #
    # NAMED, not spelled out at the call site: the point of the whole exercise
    # is that a fact lives in exactly one place.
    for helper in LITERAL_LENGTH_HELPERS:
        for n, line, _ in code_lines():
            for m in re.finditer(helper + r"\s*\(\s*'((?:[^']|'')*)'\s*,\s*(\d+)", line):
                literal = m.group(1).replace("''", "'")
                said = int(m.group(2))
                if len(literal) != said:
                    out.append('%s:%d  %s says %d but the literal is %d character(s) - '
                               '%s. Too small cuts the sentence short; too large reads past '
                               'the end of the literal and prints whatever is stored after it'
                               % (path, n, helper, said, len(literal),
                                  'too small' if said < len(literal) else 'too large'))

    for helper in DERIVES_ITS_OWN_LENGTH:
        for n, line, _ in code_lines():
            for m in re.finditer(helper + r"\s*\(\s*'((?:[^']|'')*)'\s*,\s*(\d+)", line):
                out.append('%s:%d  %s does not take a length any more - it asks the '
                           'string with MAXINDEX(text, 1) + 1. Drop the %s. A number '
                           'beside the literal is the old shape, and it was removed '
                           'because nothing could ever check it'
                           % (path, n, helper, m.group(2)))

    # ---- EVERY IMPORT BELONGS ABOVE THE FIRST ROUTINE -------------------------
    #
    # MEASURED on D100 2026-08-25, merging a screen renderer into the chat
    # client. The renderer's imports were spliced in beside its own code, which
    # sat just above PROGRAM - after every routine the client already had. The
    # compiler answered
    #
    #     MISPLACED STATEMENT "IMPORT"
    #
    # TWENTY-SIX TIMES, once per line, and not one of those messages says where
    # an import is supposed to go. Two full compiles of a 4400-line source to be
    # told a block of declarations is in the wrong half of the file.
    #
    # A DUPLICATE IMPORT IS WORSE THAN MISPLACED, because it is an ERROR and not
    # a warning: importing MON1 a second time answers ILLEGAL PREDECLARATION.
    # That is the one a merge produces without anybody noticing - both halves
    # legitimately needed MON1, and each had said so.
    first_routine = None
    for n, code in joined:
        stripped = code.strip()
        if re.match(r'^\s*(?:ROUTINE|PROGRAM)\b', stripped, re.IGNORECASE):
            first_routine = n
            break

    if first_routine is not None:
        for n, code in joined:
            if n <= first_routine:
                continue
            if re.match(r'^\s*IMPORT\b', code.strip(), re.IGNORECASE):
                out.append('%s:%d  IMPORT after the first routine (line %d). PLANC '
                           'answers MISPLACED STATEMENT "IMPORT" - once per line, and '
                           'the message never says that imports belong above every '
                           'routine. Move it up with the others'
                           % (path, n, first_routine))

    # The same name imported twice.
    seen_import = {}
    for n, code in joined:
        stripped = code.strip()
        if not re.match(r'^\s*IMPORT\b', stripped, re.IGNORECASE):
            continue
        m = re.search(r':\s*([A-Za-z][A-Za-z0-9_]*)\s*\)\s*$', stripped)
        if not m:
            continue
        nm = m.group(1).upper()
        if nm in seen_import:
            out.append('%s:%d  "%s" is IMPORTed here and again on line %d. A second '
                       'IMPORT of one name is ILLEGAL PREDECLARATION, which is an '
                       'ERROR - not the warning a repeated declaration usually gives'
                       % (path, n, m.group(1), seen_import[nm]))
        else:
            seen_import[nm] = n

    # ---- EVERY BLOCK MUST BE CLOSED BY ITS OWN KEYWORD ------------------------
    #
    # PLANC has a separate closer per block - ENDIF, ENDFOR, ENDDO - and closing
    # one with another's keyword is a pure counting mistake that a machine
    # should never have had to find.
    #
    # MEASURED on D100 2026-08-25. resolveTo closed an IF with an ENDFOR:
    #
    #     4503  (3843)/RESOLVETO  *** ERROR - EXPECTS "ENDIF" ILLEGAL SYNTAX "ENDFOR"
    #     4504  (3844)/RESOLVETO  *** ERROR - ILLEGAL SYNTAX "ENDFOR"
    #
    # An 88-second compile to be told a keyword was miscounted. Worse, the
    # BRF-LINKER RAN ANYWAY AND WROTE A PROGRAM FILE, so the build looked
    # finished - CHATSV:BRF had a fresh timestamp and the linker had read it.
    # Only the listing said otherwise, and nothing makes you read it.
    #
    # THE FIRST VERSION OF THIS CHECK REPORTED 405 PROBLEMS ACROSS SIX FILES
    # THAT ALL COMPILE, and every one was this check being wrong. Two reasons,
    # both worth writing down because they are what makes the rule non-obvious:
    #
    #   - "FOR i IN 1:n DO" holds BOTH keywords, and the DO belongs to the FOR.
    #     It is closed by the ENDFOR, not by an ENDDO. Only a DO with no FOR in
    #     front of it on the same line opens a block of its own.
    #   - CASE, ON and RECORD are left out entirely rather than guessed at.
    #     Their closers are ignored too, so the count stays balanced whatever
    #     a file does with them.
    #
    # Only IF, FOR and DO are tracked. That covers every block in this project
    # and cannot be fooled by a construct nobody here writes.
    for r in routines:
        if r['end'] is None:
            continue
        stack = []
        for n, code in joined:
            if n <= r['start'] or n >= r['end']:
                continue
            stripped = code.strip()
            if not stripped:
                continue

            # Comments are already gone and strings are already masked - see
            # where "joined" is built - so every word here is real code.
            words = re.findall(r'[A-Za-z_]+', stripped.upper())

            skip_next_do = False
            for w in words:
                if w == 'ENDIF' or w == 'ENDFOR' or w == 'ENDDO':
                    want = {'ENDIF': 'IF', 'ENDFOR': 'FOR', 'ENDDO': 'DO'}[w]
                    if not stack:
                        out.append('%s:%d  %s in %s closes a block that was never '
                                   'opened. The BRF-LINKER still writes a program '
                                   'file after this, so the build looks finished'
                                   % (path, n, w, r['name']))
                    elif stack[-1][0] != want:
                        opener = stack[-1][0]
                        need = {'IF': 'ENDIF', 'FOR': 'ENDFOR', 'DO': 'ENDDO'}[opener]
                        out.append('%s:%d  %s in %s closes a %s that was opened on '
                                   'line %d - it needs %s. The compiler answers '
                                   'EXPECTS "%s" ILLEGAL SYNTAX "%s", and then the '
                                   'LINKER RUNS ANYWAY and writes a program file, so '
                                   'nothing about the build looks wrong'
                                   % (path, n, w, r['name'], opener, stack[-1][1],
                                      need, need, w))
                        stack.pop()
                    else:
                        stack.pop()
                elif w == 'IF':
                    stack.append(('IF', n))
                elif w == 'FOR':
                    stack.append(('FOR', n))
                    # The DO that follows on this line is the FOR's own.
                    skip_next_do = True
                elif w == 'ON':
                    # ON ROUTINEERROR DO ... ENDON. The DO belongs to the ON and
                    # is closed by the ENDON, which is not tracked - so the DO
                    # must not be pushed either, or it is left open for ever.
                    # This is the same shape as FOR, and it is why logOpen and
                    # readLine were both reported as having an unclosed DO while
                    # compiling perfectly.
                    skip_next_do = True
                elif w == 'DO':
                    if skip_next_do:
                        skip_next_do = False
                    else:
                        stack.append(('DO', n))

        if stack:
            top = stack[-1]
            need = {'IF': 'ENDIF', 'FOR': 'ENDFOR', 'DO': 'ENDDO'}[top[0]]
            out.append('%s:%d  %s in %s is never closed - it wants a %s before '
                       'ENDROUTINE' % (path, top[1], top[0], r['name'], need))

    # A name is only inspected when it is READ or WRITTEN in a way that cannot be
    # anything else: "x =: y", "x(i) =: y", or a bare use as a subscript or in a
    # comparison. Keeping the shapes narrow is what keeps this quiet.
    ident_re = re.compile(r'\b([A-Za-z][A-Za-z0-9_]*)\b')
    for r in routines:
        if r['end'] is None:
            continue
        seen_here = set()
        known = r['params'] | r['locals'] | visible_everywhere
        for n, code in joined:
            if n <= r['start'] or n >= r['end']:
                continue
            stripped = code.strip()
            if not stripped or is_declaration(stripped) is not None:
                continue
            for m in ident_re.finditer(stripped):
                nm4 = m.group(1)
                up = nm4.upper()
                if up in known or up in seen_here:
                    continue
                # An octal literal - 221B, 267B - is a NUMBER, not a name.
                if re.match(r'^[0-7]+B$', up):
                    continue
                # Everything the XMSG library exports is spelled XM<something>
                # in XMP-B02:DEFS - types like XMUSERADDRESS as well as the
                # routines and constants. xmp-api.json carries the routines and
                # constants but not the TYPES, so the shape is trusted rather
                # than the list. Nothing else in these programs is named XM*.
                if re.match(r'^XM[A-Z0-9_]+$', up):
                    continue
                # A field width inside an OUTPUT, 'AL38', is masked already, but
                # a bare ALnn elsewhere is not a variable either.
                if re.match(r'^A[LR]?\d+$', up):
                    continue
                seen_here.add(up)
                out.append('%s:%d  "%s" is used in %s but is not declared there, at '
                           'module level, or as a parameter - the compiler answers '
                           'ILLEGAL SYNTAX "%s", which reads like a punctuation '
                           'problem and is not one'
                           % (path, n, nm4, r['name'], up))

    # ---- A LOCAL MAY NOT CARRY AN INITIAL VALUE --------------------------------
    #
    #     PROGRAM : mainUi
    #         BOOLEAN : smallOpen := FALSE       <- ILLEGAL
    #
    # draws, on the compiler's FIRST pass,
    #
    #     166   (141)/MAINUI  *** ERROR   - INITIAL VALUE ILLEGAL HERE "SMALLOPEN"
    #
    # Only a MODULE-level declaration may be initialised. Inside a ROUTINE or a
    # PROGRAM the declaration must be bare and the value assigned as a statement.
    # The rest of this file already RELIES on that rule - the scope check treats
    # any ":=" as proof of module level - but nothing ever CHECKED it.
    #
    # MEASURED ON D100 2026-08-24, and it cost a build cycle plus a wrong
    # diagnosis. What made it expensive is that the program still LINKED and still
    # RAN: the two flags were simply never set, so two menu keys did nothing and
    # the fault was first blamed on PLANC's NOT operator. The compile errors were
    # on screen the whole time and were missed, because the "0 DIAGNOSTICS" that
    # stays visible belongs to the SECOND pass and sits directly under a COMPILE
    # that had two.
    depth = 0
    unit_name = None
    for n, _, stripped in code_lines():
        opens = re.match(r'^(ROUTINE|PROGRAM)\s', stripped, re.IGNORECASE)
        if opens:
            depth += 1
            nm = re.search(r':\s*([A-Za-z_]\w*)', stripped)
            if nm:
                unit_name = nm.group(1)
            continue

        if re.match(r'^ENDROUTINE', stripped, re.IGNORECASE):
            if depth > 0:
                depth -= 1
            continue

        if depth <= 0:
            continue

        # A LOCAL DECLARED "READ" MAY CARRY ONE. Rule R20 in
        # Developer/Languages/Application/PLANC-LANGUAGE-RULES.md, from RM5 8.6: a
        # local without READ access is allocated on the stack at run time, so it
        # has nowhere to put a compile-time value - but a READ one is constant and
        # does. "INTEGER READ : counter := 0" inside a routine is LEGAL.
        #
        # is_declaration happens not to match that shape today, so this guard is
        # belt and braces - but the rule is the reason, and leaving it implicit
        # would make the next person's tightening of the declaration pattern turn
        # this check into a false alarm.
        if re.search(r'\bREAD\b', stripped, re.IGNORECASE):
            continue

        # Same recogniser the scope check uses, so the two agree on what a
        # declaration is.
        tail = is_declaration(stripped)
        if tail is None or ':=' not in tail:
            continue

        # A ":=" inside brackets is a bound or an index, not an initial value.
        before = tail.split(':=')[0]
        if before.count('(') != before.count(')'):
            continue

        names = names_in(tail)
        if not names:
            continue

        where = (' in ' + unit_name) if unit_name else ''
        out.append(
            '%s:%d  "%s" is declared%s WITH an initial value, and a PLANC LOCAL may '
            'not carry one - the compiler answers *** ERROR INITIAL VALUE ILLEGAL '
            'HERE. Declare it bare and assign the value as a statement after '
            'INISTACK. The build still LINKS and RUNS with the name never set, so '
            'this shows up as behaviour that quietly does nothing'
            % (path, n, names[0], where))

    # ---- a ROUTINE must declare ONE TYPE PER PARAMETER ------------------------
    # MEASURED on D100, 2026-08-25: relayOnward was written with SIX INTEGER types
    # and SEVEN parameter names. The compiler answers
    #
    #     *** ERROR   - EXPECTS ")" ILLEGAL SYNTAX ","
    #
    # at the seventh name, then two more ILLEGAL SYNTAX "," as it stumbles over the
    # rest of the list. Every one of those reads like a BRACKET fault, so the eye
    # goes hunting for a missing parenthesis and never counts the two lists. It
    # cost a fifty-minute compile of a 5000-line source to find out.
    #
    # The header is often split across a continuation, so the logical line has to
    # be rebuilt before the two lists can be compared at all.
    joined = []
    buffer_text = ''
    buffer_line = 0
    for i, raw in enumerate(lines):
        body = strip_comment(raw).rstrip()
        if not body.strip():
            continue
        if not buffer_text:
            buffer_line = i + 1
        if body.endswith('&'):
            buffer_text += body[:-1]
            continue
        buffer_text += body
        joined.append((buffer_line, buffer_text))
        buffer_text = ''
    if buffer_text:
        joined.append((buffer_line, buffer_text))

    routine_header = re.compile(
        r'\bROUTINE\b[^(]*\((?P<types>[^()]*)\)\s*:\s*'
        r'(?P<name>[A-Za-z][A-Za-z0-9_]*)\s*\((?P<names>[^()]*)\)',
        re.IGNORECASE)
    for n, logical in joined:
        found = routine_header.search(mask_strings(logical))
        if found is None:
            continue

        def parts(text):
            """Comma-separated items, with an empty list for an empty bracket."""
            text = text.strip()
            if not text:
                return []
            return [one.strip() for one in text.split(',') if one.strip()]

        types = parts(found.group('types'))
        names = parts(found.group('names'))
        if types and names and len(types) != len(names):
            out.append(
                '%s:%d  routine "%s" declares %d parameter TYPE(S) but names %d '
                'parameter(S) - PLANC wants one type per name. The compiler will '
                'answer EXPECTS ")" ILLEGAL SYNTAX "," at the first name it has no '
                'type for, which looks like a bracket fault and is not'
                % (path, n, found.group('name'), len(types), len(names)))

    # ---- A CALL WITH THE WRONG NUMBER OF ARGUMENTS, OR AN OBVIOUS WRONG TYPE --
    #
    # Written for the CHATXMS split, 2026-08-31: 35 call sites moving onto seven
    # new routines is exactly the shape of mistake that compiles as a confusing
    # error pointing at the wrong token - PLANC's own EXPECTS ")" / ILLEGAL DATA
    # TYPE messages name the SYMPTOM position, not which argument is missing or
    # which type is wrong, the same family of trap as the ONE-TYPE-PER-PARAMETER
    # check above.
    #
    # Signatures come from what THIS FILE can see: its own local ROUTINE/PROGRAM
    # headers, and its own IMPORT blocks - which is exactly where a cross-module
    # routine like xsSendM or xsRecv is declared at the call site. It does NOT
    # know the signature of a routine reached only through a $INCLUDE (XMPFGET
    # and friends live in XMP-B02:IMPT, a file on the machine, not in this repo)
    # - calls to those are not checked here and that is a real limit, not an
    # oversight to silently paper over.
    #
    # THE TYPE CHECK IS DELIBERATELY NARROW. It only judges an argument that IS
    # a literal - a quoted string, a bare integer, TRUE/FALSE - against the
    # parameter's declared type. A variable or an expression (ADDR(...), a
    # subarray, another call) is left alone, because this file does not track
    # variable types well enough to judge those without guessing, and a linter
    # that guesses wrong teaches people to ignore it.
    def arg_parts(text):
        """Comma-separated arguments, respecting nested parens and quotes.

        Empty input is ZERO arguments, not one empty one - name() must count as
        a zero-parameter call, not a one-parameter call with nothing in it.
        """
        text = text.strip()
        if not text:
            return []
        pieces, current, depth, in_str = [], '', 0, False
        for ch in text:
            if in_str:
                current += ch
                if ch == "'":
                    in_str = False
            elif ch == "'":
                in_str = True
                current += ch
            elif ch == '(':
                depth += 1
                current += ch
            elif ch == ')':
                depth -= 1
                current += ch
            elif ch == ',' and depth == 0:
                pieces.append(current)
                current = ''
            else:
                current += ch
        pieces.append(current)
        return [p.strip() for p in pieces]

    def call_args_span(s, open_paren_at):
        """The text between a call's matching parens, or None if unbalanced."""
        depth, in_str, i = 0, False, open_paren_at
        start = open_paren_at + 1
        while i < len(s):
            ch = s[i]
            if in_str:
                if ch == "'":
                    in_str = False
            elif ch == "'":
                in_str = True
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return s[start:i]
            i += 1
        return None

    def base_type_word(spec):
        m = re.match(r'\s*([A-Za-z_]\w*)', spec)
        return m.group(1).upper() if m else spec.strip().upper()

    def type_category(base):
        if base in ('INTEGER', 'INTEGER2', 'INTEGER4'):
            return 'INTEGER'
        if base in ('BYTES', 'BYTE'):
            return 'BYTES'
        if base == 'BOOLEAN':
            return 'BOOLEAN'
        return base

    def literal_category(arg):
        s = arg.strip()
        if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
            return 'BYTES'
        if re.fullmatch(r'-?\d+', s):
            return 'INTEGER'
        if s.upper() in ('TRUE', 'FALSE'):
            return 'BOOLEAN'
        return None

    sigs = {}   # NAME (upper) -> (list of base type words, "where declared" text)

    for n, logical in joined:
        found = routine_header.search(mask_strings(logical))
        if found is None:
            continue
        types_list = arg_parts(found.group('types'))
        names_list = arg_parts(found.group('names'))
        if types_list and names_list and len(types_list) == len(names_list):
            sigs[found.group('name').upper()] = (
                [base_type_word(t) for t in types_list],
                'the ROUTINE declared at line %d' % n)

    import_tuple_re = re.compile(
        r'\(\s*ROUTINE\s+[A-Za-z0-9_]+\s*,\s*[A-Za-z0-9_]+\s*'
        r'\(([^()]*)\)\s*:\s*([A-Za-z_]\w*)\s*\)', re.IGNORECASE)
    for n, logical in joined:
        if not re.match(r'^\s*IMPORT\b', logical, re.IGNORECASE):
            continue
        for m in import_tuple_re.finditer(mask_strings(logical)):
            types_list = arg_parts(m.group(1))
            key = m.group(2).upper()
            if key not in sigs:
                sigs[key] = ([base_type_word(t) for t in types_list],
                             'the IMPORT at line %d' % n)

    call_re = re.compile(r'\b([A-Za-z][A-Za-z0-9_]*)\s*\(')
    for n, logical in joined:
        if re.match(r'^\s*(ROUTINE|PROGRAM|IMPORT|EXPORT)\b', logical,
                    re.IGNORECASE):
            continue
        masked_line = mask_strings(logical)
        for m in call_re.finditer(masked_line):
            key = m.group(1).upper()
            if key not in sigs:
                continue
            expected_types, origin = sigs[key]
            args_text = call_args_span(logical, m.end() - 1)
            if args_text is None:
                continue
            args = arg_parts(args_text)
            if len(args) != len(expected_types):
                out.append(
                    '%s:%d  "%s(...)" is called with %d argument(s) but %s '
                    'declares %d parameter(s) - PLANC answers EXPECTS ")" or '
                    'ILLEGAL DATA TYPE at this call, which names the wrong '
                    'token, not the missing or extra argument'
                    % (path, n, m.group(1), len(args), origin,
                       len(expected_types)))
                continue
            for idx, (arg, base) in enumerate(zip(args, expected_types)):
                cat = type_category(base)
                if cat not in ('INTEGER', 'BYTES', 'BOOLEAN'):
                    continue
                lit = literal_category(arg)
                if lit is None or lit == cat:
                    continue
                out.append(
                    '%s:%d  "%s" argument %d ("%s") is a %s literal but '
                    'parameter %d of %s is declared %s - PLANC checks this '
                    'and answers ILLEGAL DATA TYPE at the call'
                    % (path, n, m.group(1), idx + 1, arg.strip(), lit,
                       idx + 1, origin, base))

    # ---- two names that become ONE after truncation ---------------------------
    # ND-60.117.5 keeps TEN characters of an identifier and PLANC does not warn:
    # it TRUNCATES and carries on. relayOnward compiled quite happily as
    # RELAYONWAR on 2026-08-25.
    #
    # A long name on its own is therefore HARMLESS - this server has nineteen of
    # them and every one works - so flagging length would be nothing but noise.
    # What is NOT harmless is two names sharing those first ten characters,
    # because they silently become the SAME name: one routine ends up calling the
    # other, the build is clean and the program does something nobody wrote.
    # That collision is what is reported here.
    declared_name = re.compile(
        r'ROUTINE[^:]*:\s*(?P<name>[A-Za-z][A-Za-z0-9_]*)', re.IGNORECASE)
    first_ten = {}
    for n, logical in joined:
        found = declared_name.search(mask_strings(logical))
        if found is None:
            continue
        name = found.group('name')
        key = name[:10].upper()
        if key in first_ten and first_ten[key][0] != name:
            other_name, other_line = first_ten[key]
            out.append(
                '%s:%d  routine "%s" and "%s" on line %d share their first TEN '
                'characters, and PLANC keeps only ten - both compile to "%s" and '
                'become ONE name with NO warning. Rename one of them'
                % (path, n, name, other_name, other_line, key))
        else:
            first_ten[key] = (name, n)

    # ---- A SOURCE LINE THAT IS TOO LONG, and the FOURTEEN errors it invents --
    #
    # MEASURED on D100 2026-08-25. A 167-character source line answered
    #
    #     808   (783)/ADDFAKE  *** ERROR   - LINE IS TOO LONG
    #
    # and then FOURTEEN MORE errors that had nothing to do with it. The line
    # held a string literal, so cutting it off left the opening quote unclosed,
    # and the compiler read the NEXT message's words as code:
    #
    #     *** ERROR - EXPECTS "OVERFLOW" ILLEGAL SYNTAX "BATCH"
    #     *** ERROR - ILLEGAL SYNTAX "PROCESSOR"
    #
    # BATCH and PROCESSOR are words inside a perfectly good sentence twenty
    # lines further down. Every one of those fourteen blames an innocent line,
    # and the ONE that matters is the first.
    #
    # WHERE THE LIMIT ACTUALLY IS, HONESTLY: NOT MEASURED. The manual's entry
    # for LINE IS TOO LONG reads "No further explanation." What IS measured is
    # that TESTUI.PLNC, whose longest line is 108 characters, compiles on D100
    # with 0 diagnostics, and that a 167-character line does not. So the check
    # warns above 108 - the widest width this project has PROOF of - rather
    # than at a round number nobody has tested.
    #
    # The threshold started at 102 and was raised the moment TESTUI was run
    # through this check and answered back. That is the right way round: the
    # number is whatever the machine has actually accepted, and it moves when
    # something wider is proved, never because a line is inconvenient.
    #
    # If you need a longer line, break it with the & continuation.
    MAX_PROVED_LINE = 108
    for num, raw_line in enumerate(io.open(path, encoding="latin-1"), 1):
        stripped = raw_line.rstrip(chr(13) + chr(10))
        if len(stripped) > MAX_PROVED_LINE:
            out.append('%s:%d  SOURCE LINE IS %d CHARACTERS. The widest line this project '
                       'has ever compiled is %d; PLANC answers LINE IS TOO LONG above some '
                       'limit it does not document. Worse, if the line holds a string the '
                       'unclosed quote makes the compiler read the following text as code '
                       'and blame lines that are perfectly correct. Break it with &'
                       % (path, num, len(stripped), MAX_PROVED_LINE))

    # ---- MIXED LINE ENDINGS, which the compiler does NOT report ---------------
    #
    # MEASURED 2026-08-25 and it cost a build cycle plus three wrong theories.
    # A source with SOME lines ending CRLF and some ending bare LF compiles with
    # 0 DIAGNOSTICS and produces a program that behaves wrongly - in this case a
    # whole block of routines built and linked, and the array they fill stayed
    # empty. Normalising the file to CRLF, changing nothing else, fixed it.
    #
    # The skill already says sources must be CRLF, and a file that is ENTIRELY
    # bare LF answers LINE IS TOO LONG on every line - loud and obvious. MIXED is
    # the dangerous one, because it is silent, and it is exactly what a scripted
    # edit produces when it writes a bare newline into a CRLF file.
    raw = io.open(path, 'rb').read()
    eol_crlf = raw.count(bytes([13, 10]))
    eol_bare = raw.count(bytes([10])) - eol_crlf
    # ---- A CARRIAGE RETURN THAT IS NOT PART OF A LINE ENDING ------------------
    #
    # A lone CR, or the CR CR LF that a careless splice leaves behind. The
    # mixed-endings check above cannot see this one: the file still has ZERO
    # bare LFs, so by that measure it is perfectly clean CRLF.
    #
    # MEASURED 2026-08-25. ONE CR CR LF in CHAT.PLNC made git report the WHOLE
    # 3467-line file as rewritten - every line deleted and re-added, with the
    # old and new lines looking identical on screen. A real 178-line change was
    # completely buried in it, and reviewing that diff would have been
    # impossible. The compiler has not been asked what it makes of one, and
    # nobody should have to find out.
    stray_cr = raw.count(bytes([13])) - eol_crlf
    if stray_cr > 0:
        out.append('%s  %d CARRIAGE RETURN(S) NOT FOLLOWED BY A LINE FEED. The '
                   'mixed-endings check cannot see these - the file still has zero '
                   'bare line feeds. One of them made git report an entire 3467-line '
                   'file as rewritten, with every old and new line looking identical, '
                   'burying a real change completely' % (path, stray_cr))

    # ---- A SUBARRAY PAINTED WITH A WIDTH OF 0 --------------------------------
    #
    # bytdis takes (row, column, WIDTH, text, attributes). A width of 0 means
    # "use the string's own length", which is right for a LITERAL and WRONG for a
    # SUBARRAY of a bigger buffer.
    #
    # MEASURED on D100 2026-08-25, in TESTUI's paintRun. The text was a subarray
    # of a 700-byte buffer and the width was left at 0; the painted line ran clean
    # off the right-hand side and wiped the scroll window's border at column 76 AND
    # the main window's at 78 - which a write of seventy characters starting at
    # column 5 cannot reach. Note what that also says: bytdis does NOT stop at the
    # viewport edge although VTWRIT does, so viewport clipping must never be
    # assumed for PLANC-SCREEN-H.
    #
    # Passing the exact width removes it. This check is narrow on purpose: only a
    # literal 0 width with a subarray argument, which is the shape that was
    # measured to break. A width held in a variable is somebody's decision.
    for number, line, stripped in code_lines():
        for m in re.finditer(r'\bbytdis\s*\(', stripped, re.IGNORECASE):
            depth = 0
            args = []
            current = ''
            for ch in stripped[m.end() - 1:]:
                if ch == '(':
                    depth += 1
                    if depth == 1:
                        continue
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        args.append(current)
                        break
                if depth == 1 and ch == ',':
                    args.append(current)
                    current = ''
                else:
                    current += ch
            if len(args) < 4:
                continue
            width = args[2].strip()
            text = args[3].strip()
            # A subarray is name(lo : hi) - the colon is what makes it one.
            if width == '0' and '(' in text and ':' in text.split('(', 1)[1]:
                out.append('%s:%d  bytdis is given a SUBARRAY %s with a width of 0. '
                           'Width 0 means the STRING SAYS ITS OWN LENGTH, which is right '
                           'for a literal and wrong for a subarray - MEASURED on D100, the '
                           'line ran off the right-hand side and wiped two window '
                           'borders. bytdis does NOT stop at the viewport edge even '
                           'though VTWRIT does. Pass the exact width.'
                           % (path, number, text[:40]))

    if eol_crlf and eol_bare:
        out.append('%s  MIXED LINE ENDINGS - %d CRLF and %d bare LF. The compiler does '
                   'NOT report this: it answers 0 DIAGNOSTICS and builds a program that '
                   'misbehaves. Normalise the whole file to CRLF' % (path, eol_crlf, eol_bare))

    return out


def _arity_check_proves_itself():
    """End-to-end: does the call-arity/type check actually catch a bad call?

    Every probe in self_test() below tests a REGEX IN ISOLATION - it proves a
    pattern still matches sample text, not that check() end-to-end still
    reports the right thing for it. That gap is real: a pattern can match
    perfectly and still feed a broken comparison, an off-by-one, or a
    mis-wired condition a few lines later, and none of the regex probes would
    notice.

    So this writes a small, real PLANC source with THREE calls to two
    declared routines: one with the WRONG NUMBER of arguments, one with an
    OBVIOUSLY WRONG literal type, and one that matches its signature exactly.
    It runs check() on that source for real and demands the two bad calls are
    reported and the good one draws nothing - a NEGATIVE test, same shape as
    the manual probe used to prove this check when it was written
    (2026-08-31), now kept permanently instead of being thrown away after.
    """
    src = (
        "MODULE aritycheck\n"
        "    IMPORT (ROUTINE VOID, INTEGER (INTEGER, BYTES) : xrClamp)\n"
        "\n"
        "    ROUTINE VOID, INTEGER (INTEGER, INTEGER4, BYTES, INTEGER, INTEGER) : &\n"
        "            xsSendM(port, magic, buf, length, flags)\n"
        "        0 RETURN\n"
        "    ENDROUTINE\n"
        "\n"
        "    PROGRAM : mainUi\n"
        "        INTEGER : st\n"
        "        INTEGER : n\n"
        "        BYTES : buf(0:9)\n"
        "\n"
        "        % BAD - one argument short.\n"
        "        xsSendM(1, 2, buf, 3) =: st\n"
        "        % BAD - a string literal where xrClamp wants an INTEGER.\n"
        "        xrClamp('oops', buf) =: n\n"
        "        % GOOD - matches xsSendM's declared signature exactly.\n"
        "        xsSendM(1, 2, buf, 3, 0) =: st\n"
        "    ENDROUTINE\n"
        "ENDMODULE\n"
    )
    problems = []
    fd, path = tempfile.mkstemp(suffix='.PLNC')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(src)
        findings = check(path)
    finally:
        os.remove(path)

    caught_arity = any('4 argument(s)' in f and 'xsSendM' in f for f in findings)
    caught_type = any('BYTES literal' in f and 'xrClamp' in f for f in findings)

    if not caught_arity:
        problems.append(
            'the end-to-end arity probe did NOT catch xsSendM being called '
            'with 4 arguments where it declares 5 - the call-arity check is '
            'silently broken. findings were: %r' % findings)
    if not caught_type:
        problems.append(
            "the end-to-end arity probe did NOT catch xrClamp('oops', buf) - "
            'a string literal where the routine declares INTEGER - the '
            'literal-type check is silently broken. findings were: %r'
            % findings)
    if caught_arity and caught_type and len(findings) != 2:
        problems.append(
            'the end-to-end arity probe expected EXACTLY 2 findings (the two '
            'bad calls) but got %d - the correctly-shaped third call '
            '(xsSendM with all 5 arguments) is drawing a FALSE POSITIVE. '
            'findings were: %r' % (len(findings), findings))

    return problems


def _arity_check_proves_itself_on_mixed_types():
    """A second end-to-end negative test, on a routine with FOUR parameters of
    THREE different types (BYTES, BOOLEAN, INTEGER, INTEGER) - the first probe
    above only ever gets one type category wrong at a time, in a routine with
    two type categories total. That leaves real gaps this one closes:

     - BOOLEAN was never exercised as an expected type at all.
     - Every earlier bad call had exactly ONE wrong argument. A call with
       SEVERAL wrong arguments at once must report EACH ONE separately, by
       its own argument number - not stop at the first, and not merge them
       into one vague line that only names the call.
     - A correct call sitting in the SAME routine, SAME file, right next to
       three bad ones must still draw nothing, proving position in the file
       is not what the check is keying on.

    Modelled on the real xsOpenC in CHATXMS.PLNC (BYTES, BOOLEAN, INTEGER,
    INTEGER WRITE), declared fresh here so this probe does not depend on that
    file existing or being unchanged.
    """
    src = (
        "MODULE mixedtypes\n"
        "    ROUTINE VOID, INTEGER (BYTES, BOOLEAN, INTEGER, INTEGER) : &\n"
        "            xsOpenC(name, unique, seats, extra)\n"
        "        0 RETURN\n"
        "    ENDROUTINE\n"
        "\n"
        "    PROGRAM : mainUi\n"
        "        INTEGER : st\n"
        "\n"
        "        % BAD - one argument wrong: position 1 (INTEGER, wants BYTES).\n"
        "        xsOpenC(5, TRUE, 10, 1) =: st\n"
        "        % BAD - one argument wrong: position 2 (INTEGER, wants BOOLEAN).\n"
        "        xsOpenC('A', 1, 10, 1) =: st\n"
        "        % BAD - THREE arguments wrong at once: 1, 2 and 3.\n"
        "        xsOpenC(5, 1, 'ten', 1) =: st\n"
        "        % GOOD - matches the declared signature exactly.\n"
        "        xsOpenC('A', TRUE, 10, 1) =: st\n"
        "    ENDROUTINE\n"
        "ENDMODULE\n"
    )
    problems = []
    fd, path = tempfile.mkstemp(suffix='.PLNC')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(src)
        findings = check(path)
    finally:
        os.remove(path)

    def has(text_bits):
        return [f for f in findings if all(bit in f for bit in text_bits)]

    # These two are UNIQUELY shaped - nothing else in this source could
    # produce them - so each is real, independent evidence on its own.
    checks = [
        (['argument 2', 'INTEGER literal', 'declared BOOLEAN'],
         "position 2 of the SECOND call: an INTEGER literal (1) where "
         "xsOpenC declares BOOLEAN"),
        (['argument 3', 'BYTES literal', 'declared INTEGER'],
         "position 3 of the THIRD call: a BYTES literal ('ten') where "
         "xsOpenC declares INTEGER"),
    ]
    for bits, what in checks:
        if not has(bits):
            problems.append(
                'the mixed-type probe did NOT catch %s - findings were: %r'
                % (what, findings))

    # The first call's mismatch (argument 1, INTEGER literal, declared BYTES)
    # and the third call's arguments 1 and 2 are IDENTICAL IN SHAPE to each
    # other - the third call repeats the same two mistakes the first two
    # calls each make once. There is no way to tell from the finding text
    # alone which CALL produced which, so the count below is what actually
    # proves the third call's three violations were each reported and not
    # just the first one found - not another substring check that could not
    # tell the difference either.
    if len(findings) != 5:
        problems.append(
            'the mixed-type probe expected EXACTLY 5 findings (1 from the '
            'first bad call + 1 from the second + 3 from the third, which '
            'gets three arguments wrong at once) but got %d - either a real '
            'violation is going unreported (the third call reporting fewer '
            'than 3 would mean it stops after the first bad argument instead '
            'of checking all of them), or the correctly-shaped fourth call '
            'is drawing a FALSE POSITIVE. findings were: %r'
            % (len(findings), findings))

    return problems


def self_test():
    """Refuse to run if this file's own patterns have been damaged.

    A DEAD REGEX HAS SILENTLY DISABLED THIS LINTER TWICE, and both times the
    tool went on printing "clean" - which is worse than crashing, because a
    clean answer is what you act on.

    Both were the same mistake. In a NON-raw Python string, backslash-b is a
    BACKSPACE CHARACTER, not a word boundary. So a pattern written into this
    file by a script that used an ordinary string ends up containing a literal
    byte 8, and then

        ^\s*(?:ROUTINE|PROGRAM)<backspace>(.*)$

    matches no line ever written. Nothing looks wrong: grep shows the pattern
    apparently intact, because a terminal draws a backspace as nothing at all.

    The first time it took out five checks at once. The second time it took out
    the routine-scope check, and every source in the project answered "clean"
    while one of them used a variable that was declared in another routine.

    So: prove the patterns still match text they are certain to match, and say
    so loudly if they do not. This runs before any file is read.
    """
    problems = []

    if chr(8) in io.open(__file__, encoding="utf-8", errors="replace").read():
        problems.append("this file contains a literal BACKSPACE character - "
                        "almost certainly a backslash-b that was written into a "
                        "non-raw string. Every regex holding one is dead.")

    probes = [
        (re.compile(r'^\s*(?:ROUTINE|PROGRAM)\b(.*)$', re.IGNORECASE),
         'ROUTINE VOID, VOID : helper', 'routine/program header'),
        (re.compile(r'^\s*(?:ROUTINE|PROGRAM)\b(.*)$', re.IGNORECASE),
         'PROGRAM : mainUi', 'program header'),
        (re.compile(r'^\s*ENDROUTINE', re.IGNORECASE),
         'ENDROUTINE', 'routine end'),
        # The cross-file export check is only as good as this one pattern. If it
        # dies, several modules can export the same seven characters and nothing
        # anywhere will say so - see cross_file_exports.
        (re.compile(r'^EXPORT\s+(\w+)\s*$'),
         'EXPORT cmEncAt', 'export statement'),
        # The subarray-width check hangs off this one word. If it dies, a paint
        # that runs off the edge and wipes a window border goes unreported.
        (re.compile(r'\bbytdis\s*\(', re.IGNORECASE),
         "bytdis(row, 3, 0, buf(a : b), '')", 'bytdis call'),
        # The duplicate-routine-name check hangs off this pattern. If it dies,
        # a second ROUTINE reusing a name already used elsewhere in the file
        # goes unreported, and the 215-diagnostic cascade it caused on
        # CHATSV.PLNC 2026-08-31 can happen again with nothing to catch it.
        (re.compile(r'^(?:ROUTINE|PROGRAM)\b[^:]*:\s*([A-Za-z_]\w*)'),
         'ROUTINE VOID, INTEGER : buildMembers', 'routine/program name'),
        # The call-arity/type check hangs off both of these. If either dies, a
        # call to a known routine with the wrong number of arguments, or an
        # obviously wrong literal type, goes unreported.
        (re.compile(r'\(\s*ROUTINE\s+[A-Za-z0-9_]+\s*,\s*[A-Za-z0-9_]+\s*'
                    r'\(([^()]*)\)\s*:\s*([A-Za-z_]\w*)\s*\)', re.IGNORECASE),
         "(ROUTINE VOID, INTEGER (INTEGER, BYTES) : xrClamp)",
         'IMPORT tuple'),
        (re.compile(r'\b([A-Za-z][A-Za-z0-9_]*)\s*\('),
         'xsSendM(port, magic, buf, length, flags)', 'call site'),
    ]
    for pattern, sample, what in probes:
        if not pattern.match(sample):
            problems.append('the %s pattern does not match %r' % (what, sample))

    problems.extend(_arity_check_proves_itself())
    problems.extend(_arity_check_proves_itself_on_mixed_types())
    problems.extend(_cross_check_proves_itself())

    if problems:
        print('planc-lint IS BROKEN AND WOULD REPORT "clean" WRONGLY:',
              file=sys.stderr)
        for p in problems:
            print('  - ' + p, file=sys.stderr)
        return False
    return True


def exports_of(path):
    """Every name this source EXPORTs, as (name, line number).

    Used for the cross-file check below. Kept separate from check() because it
    answers a question about a SET of sources, not about one.
    """
    found = []
    text = io.open(path, encoding='utf-8', errors='replace').read()
    for number, line in enumerate(text.split('\n'), 1):
        stripped = strip_comment(line).strip()
        m = re.match(r'^EXPORT\s+(\w+)\s*$', stripped)
        if m:
            found.append((m.group(1), number))
    return found


def cross_file_exports(paths):
    """Two modules exporting names that agree in seven characters.

    check() already catches this WITHIN one source. It cannot catch it BETWEEN
    two, and between two is where it actually bites: the collision only exists
    once both BRFs are handed to the same linker, so neither file is wrong on
    its own and neither compile says anything.

    This matters much more than it used to. While the client and the server were
    each one big module, the only exports in the link came from CHATLIB. Splitting
    a 6500-line source into separately compiled modules multiplies the exported
    surface, and every new name is a chance to collide with one that already
    exists - silently, because the linker does not report a duplicate. It
    resolves every import to whichever entry it met first.

    Give this the WHOLE set that will be linked together, not one file:

        python tools/planc-lint.py SINTRAN-CHAT/CHAT*.PLNC
    """
    out = []
    if len(paths) < 2:
        return out

    seen = {}
    for path in paths:
        for name, number in exports_of(path):
            seen.setdefault(name[:7].upper(), []).append((path, name, number))

    for short, found in sorted(seen.items()):
        # Only a collision when it spans more than one FILE - the same-file case
        # is check()'s job, and reporting it twice would train people to skim.
        files = set(f for f, _, _ in found)
        if len(found) > 1 and len(files) > 1:
            where = ', '.join('%s (%s line %d)' % (n, os.path.basename(f), ln)
                              for f, n, ln in found)
            out.append('EXPORTS COLLIDE ACROSS FILES at seven characters - %s all read '
                       '"%s" to the linker. It will NOT report a duplicate; it will '
                       'resolve every import to one of them. Rename all but one.'
                       % (where, short))
    return out


def _logical_lines(path):
    """(line number, logical line) pairs with & continuations rebuilt and
    comments stripped - the same joining check() does, standalone so the
    cross-file checks can share it."""
    text = io.open(path, encoding='utf-8', errors='replace').read()
    joined = []
    buffer_text = ''
    buffer_line = 0
    for i, raw in enumerate(text.split('\n')):
        body = strip_comment(raw).rstrip()
        if not body.strip():
            continue
        if not buffer_text:
            buffer_line = i + 1
        if body.endswith('&'):
            buffer_text += body[:-1]
            continue
        buffer_text += body
        joined.append((buffer_line, buffer_text))
        buffer_text = ''
    if buffer_text:
        joined.append((buffer_line, buffer_text))
    return joined


_DATA_TYPE_WORDS = (
    'INTEGER', 'INTEGER1', 'INTEGER2', 'INTEGER4', 'BYTE', 'BYTES',
    'BOOLEAN', 'REAL', 'REAL8', 'LABEL', 'XMMSGIDENTIFIER', 'XMUSERADDRESS')


def _norm_type(spec):
    """One parameter or declaration type, normalised for comparison.

    Collapses whitespace, uppercases, and folds INTEGER2 onto INTEGER -
    on the ND-100 plain INTEGER IS sixteen bits, so the two spellings are
    the same calling convention and must not be reported as a mismatch.
    READ is the default access and is dropped; WRITE is KEPT, because a
    scalar WRITE parameter travels by address and a plain one by value -
    that difference IS a real calling-convention fault.
    """
    words = [w.upper() for w in spec.split()]
    words = [('INTEGER' if w == 'INTEGER2' else w) for w in words]
    words = [w for w in words if w != 'READ']
    return ' '.join(words)


_ROUTINE_SIG_RE = re.compile(
    r'^\s*ROUTINE\s+(?:STANDARD\s+|REFERENCE\s+|SPECIAL\s+|INLINE\s+)?'
    r'(?P<intype>[A-Za-z_]\w*(?:\s+POINTER)?)\s*,\s*'
    r'(?P<outtype>[A-Za-z_]\w*(?:\s+POINTER)?)\s*'
    r'(?:\((?P<types>[^()]*)\))?\s*:\s*'
    r'(?P<name>[A-Za-z_]\w*)\s*[(?]?', re.IGNORECASE)

_IMPORT_ROUTINE_RE = re.compile(
    r'\(\s*ROUTINE\s+(?:STANDARD\s+|REFERENCE\s+|SPECIAL\s+|INLINE\s+)?'
    r'(?P<intype>[A-Za-z_]\w*(?:\s+POINTER)?)\s*,\s*'
    r'(?P<outtype>[A-Za-z_]\w*(?:\s+POINTER)?)\s*'
    r'(?:\((?P<types>[^()]*)\))?\s*:\s*'
    r'(?P<name>[A-Za-z_]\w*)\s*\)', re.IGNORECASE)

_IMPORT_DATA_RE = re.compile(
    r'\(\s*(?P<type>(?:' + '|'.join(_DATA_TYPE_WORDS) + r')'
    r'(?:\s+(?:ARRAY|PACKED|POINTER|READ|WRITE))*)\s*:\s*'
    r'(?P<names>[^()]*(?:\([^()]*\)[^()]*)*)\)', re.IGNORECASE)


def _split_toplevel_commas(text):
    pieces, current, depth = [], '', 0
    for ch in text:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            pieces.append(current)
            current = ''
        else:
            current += ch
    if current.strip():
        pieces.append(current)
    return [p.strip() for p in pieces]


def _routine_sig_tuple(m):
    types = m.group('types')
    params = [] if types is None else [
        _norm_type(t) for t in _split_toplevel_commas(types) if t.strip()]
    return (_norm_type(m.group('intype')), _norm_type(m.group('outtype')),
            tuple(params))


def interface_of(path):
    """What one source EXPORTs, DEFINES and IMPORTs, for the cross-file check.

    defs maps NAME -> list of ('ROUTINE', sig-tuple, line) and
    ('DATA', (normalised type, bounds text or None), line). Every declaration
    of a name is kept, because CHAT.PLNC declares module data BETWEEN routines
    and a local can share a module name - a mismatch is only reported when NO
    declaration in the exporting file agrees, which cannot false-positive.
    """
    exports = dict()
    defs = {}
    imp_routines = []
    imp_data = []
    for n, logical in _logical_lines(path):
        masked = mask_strings(logical)
        stripped = masked.strip()

        em = re.match(r'^EXPORT\s+(\w+)\s*$', stripped)
        if em:
            exports.setdefault(em.group(1).upper(), (em.group(1), n))
            continue

        if re.match(r'^IMPORT\b', stripped, re.IGNORECASE):
            for m in _IMPORT_ROUTINE_RE.finditer(masked):
                imp_routines.append((m.group('name').upper(),
                                     _routine_sig_tuple(m), n))
            for m in _IMPORT_DATA_RE.finditer(masked):
                if re.match(r'\s*ROUTINE\b', m.group(0)[1:], re.IGNORECASE):
                    continue
                base = _norm_type(m.group('type'))
                for item in _split_toplevel_commas(m.group('names')):
                    nm = re.match(r'([A-Za-z_]\w*)\s*(\(([^()]*)\))?', item)
                    if nm:
                        bounds = nm.group(3)
                        bounds = bounds.replace(' ', '') if bounds else None
                        imp_data.append((nm.group(1).upper(),
                                         (base, bounds), n))
            continue

        rm = _ROUTINE_SIG_RE.match(stripped)
        if rm:
            name = rm.group('name').rstrip('?')
            defs.setdefault(name.upper(), []).append(
                ('ROUTINE', _routine_sig_tuple(rm), n))
            continue

        pm = re.match(r'^PROGRAM\s*:\s*([A-Za-z_]\w*)', stripped,
                      re.IGNORECASE)
        if pm:
            defs.setdefault(pm.group(1).upper(), []).append(
                ('ROUTINE', ('VOID', 'VOID', ()), n))
            continue

        dm = re.match(
            r'^(?P<type>(?:' + '|'.join(_DATA_TYPE_WORDS) + r')'
            r'(?:\s+RANGE\s*\([^)]*\))?'
            r'(?:\s+(?:ARRAY|PACKED|POINTER|READ|WRITE))*)\s*:\s*'
            r'(?P<names>.+)$', stripped, re.IGNORECASE)
        if dm:
            base = _norm_type(re.sub(r'\s+RANGE\s*\([^)]*\)', '',
                                     dm.group('type'), flags=re.IGNORECASE))
            for item in _split_toplevel_commas(dm.group('names')):
                item = item.split(':=')[0].strip()
                nm = re.match(r'([A-Za-z_]\w*)\s*(\(([^()]*)\))?\s*$', item)
                if nm:
                    bounds = nm.group(3)
                    bounds = bounds.replace(' ', '') if bounds else None
                    defs.setdefault(nm.group(1).upper(), []).append(
                        ('DATA', (base, bounds), n))
            continue

        cm = re.match(r'^CONSTANT\s+(.+)$', stripped, re.IGNORECASE)
        if cm:
            for item in _split_toplevel_commas(cm.group(1)):
                nm = re.match(r'([A-Za-z_]\w*)', item.strip())
                if nm:
                    defs.setdefault(nm.group(1).upper(), []).append(
                        ('CONSTANT', None, n))

    return exports, defs, imp_routines, imp_data


def _sig_text(sig):
    intype, outtype, params = sig
    inner = ' (' + ', '.join(params) + ')' if params else ''
    return 'ROUTINE %s, %s%s' % (intype, outtype, inner)


def cross_file_interfaces(paths):
    """EXPORT with no definition, and IMPORTs that disagree with the exporter.

    ND-60.117.5 section 8.3: correspondence between an EXPORT and an IMPORT
    'is only checked when both modules are nested in one compilation.
    Separately compiled modules are NOT checked' - so a routine deleted from
    CHAT.PLNC while its EXPORT and CHATARR's IMPORT stay behind, or an IMPORT
    whose signature has drifted from the real header, compiles clean in BOTH
    files, links (an undefined entry does not fail a BRF link), runs, and
    lies. Written 2026-09-01, the night a definitionless-looking uiSaid cost
    an hour of fright during the repeat-first-message hunt - the compiler had
    no opinion and the linker would have had none either.

    Only names exported by a file IN THE GIVEN SET are judged: an import of
    XMPFGET or MON50 resolves against a library this repo does not hold, and
    guessing about those would teach people to ignore the linter.
    """
    out = []
    if len(paths) < 2:
        interfaces = {}
    else:
        interfaces = {p: interface_of(p) for p in paths}

    exporter_of = {}
    for p, (exports, defs, _ir, _id) in interfaces.items():
        for key, (name, line) in exports.items():
            exporter_of.setdefault(key, (p, name, line, defs))

    # 1. An EXPORT whose name is DEFINED NOWHERE in its own module.
    for p, (exports, defs, _ir, _id) in sorted(interfaces.items()):
        for key, (name, line) in sorted(exports.items()):
            if key not in defs:
                out.append(
                    '%s:%d  EXPORT %s but nothing in this file DEFINES it - no '
                    'routine, no declaration, no constant. The compiler accepts '
                    'it, the BRF link leaves the entry undefined WITHOUT failing '
                    'the build, and every caller jumps into rubbish at run time. '
                    'Either the definition was deleted with its export left '
                    'behind, or the name is misspelled.'
                    % (p, line, name))

    # 2. An IMPORT that disagrees with the exporting module's definition.
    for p, (_exports, _defs, imp_routines, imp_data) in sorted(
            interfaces.items()):
        for name, sig, line in imp_routines:
            hit = exporter_of.get(name)
            if hit is None:
                continue
            src, real_name, _eline, src_defs = hit
            if src == p:
                continue
            entries = src_defs.get(name, [])
            routine_sigs = [e for e in entries if e[0] == 'ROUTINE']
            if not entries:
                continue          # dangling export, already reported above
            if not routine_sigs:
                out.append(
                    '%s:%d  IMPORTs %s as a ROUTINE but %s defines it as DATA. '
                    'Separately compiled modules are never checked against each '
                    'other (ND-60.117.5 8.3) - this links clean and every call '
                    'executes the variable as code.'
                    % (p, line, real_name, os.path.basename(src)))
                continue
            if not any(e[1] == sig for e in routine_sigs):
                have = _sig_text(routine_sigs[0][1])
                out.append(
                    '%s:%d  IMPORT of %s declares "%s" but %s line %d defines '
                    '"%s". Separately compiled modules are NEVER checked against '
                    'each other (ND-60.117.5 8.3) - a drifted IMPORT compiles '
                    'clean in both files, links, and the callee reads arguments '
                    'that were never passed.'
                    % (p, line, real_name, _sig_text(sig),
                       os.path.basename(src), routine_sigs[0][2], have))
        for name, (base, bounds), line in imp_data:
            hit = exporter_of.get(name)
            if hit is None:
                continue
            src, real_name, _eline, src_defs = hit
            if src == p:
                continue
            entries = src_defs.get(name, [])
            data_defs = [e for e in entries if e[0] == 'DATA']
            if not entries:
                continue
            if not data_defs:
                if any(e[0] == 'ROUTINE' for e in entries):
                    out.append(
                        '%s:%d  IMPORTs %s as DATA but %s defines it as a '
                        'ROUTINE. This links clean and every read of the '
                        '"variable" reads machine code.'
                        % (p, line, real_name, os.path.basename(src)))
                continue

            def data_matches(d):
                dbase, dbounds = d[1]
                if dbase != base:
                    return False
                if bounds is None or dbounds is None:
                    return True
                literal = re.fullmatch(r'[-0-9:]+', bounds) and \
                    re.fullmatch(r'[-0-9:]+', dbounds)
                if not literal:
                    return True   # constant-named bounds cannot be evaluated
                return bounds == dbounds

            if not any(data_matches(d) for d in data_defs):
                dbase, dbounds = data_defs[0][1]
                have = dbase + ('(%s)' % dbounds if dbounds else '')
                want = base + ('(%s)' % bounds if bounds else '')
                out.append(
                    '%s:%d  IMPORT of %s declares "%s" but %s line %d declares '
                    '"%s". The two are never checked against each other across '
                    'separate compilations - a size or bounds drift here means '
                    'MAXINDEX lies to every user of the import, silently.'
                    % (p, line, real_name, want,
                       os.path.basename(src), data_defs[0][2], have))
    return out


def _cross_check_proves_itself():
    """End-to-end negative test for cross_file_interfaces: two small sources
    with one dangling EXPORT, one drifted routine IMPORT, one drifted data
    IMPORT - and one routine plus one variable imported CORRECTLY, which must
    draw nothing. Same discipline as the arity probes: a check must be shown
    to FAIL on a bad input and PASS on a good one, or it proves nothing.
    """
    src_a = (
        "MODULE parta\n"
        "    EXPORT goodRtn\n"
        "    EXPORT goodVar\n"
        "    EXPORT driftRtn\n"
        "    EXPORT driftVar\n"
        "    EXPORT ghostRtn\n"
        "\n"
        "    INTEGER : goodVar := 0\n"
        "    INTEGER4 : driftVar\n"
        "\n"
        "    ROUTINE VOID, INTEGER (INTEGER, BYTES) : goodRtn(a, b)\n"
        "        0 RETURN\n"
        "    ENDROUTINE\n"
        "\n"
        "    ROUTINE VOID, VOID (INTEGER, INTEGER, INTEGER) : &\n"
        "            driftRtn(a, b, c)\n"
        "    ENDROUTINE\n"
        "ENDMODULE\n"
    )
    src_b = (
        "MODULE partb\n"
        "    IMPORT (ROUTINE VOID, INTEGER (INTEGER, BYTES) : goodRtn)\n"
        "    IMPORT (INTEGER : goodVar)\n"
        "    IMPORT (ROUTINE VOID, VOID (INTEGER, INTEGER) : driftRtn)\n"
        "    IMPORT (INTEGER : driftVar)\n"
        "    IMPORT (ROUTINE VOID, VOID : ghostRtn)\n"
        "ENDMODULE\n"
    )
    problems = []
    fd_a, path_a = tempfile.mkstemp(suffix='.PLNC')
    fd_b, path_b = tempfile.mkstemp(suffix='.PLNC')
    try:
        with os.fdopen(fd_a, 'w', encoding='utf-8') as f:
            f.write(src_a)
        with os.fdopen(fd_b, 'w', encoding='utf-8') as f:
            f.write(src_b)
        findings = cross_file_interfaces([path_a, path_b])
    finally:
        os.remove(path_a)
        os.remove(path_b)

    if not any('ghostRtn' in f and 'DEFINES' in f for f in findings):
        problems.append('the cross-interface probe did NOT catch the EXPORT '
                        'of ghostRtn, which nothing defines. findings: %r'
                        % findings)
    if not any('driftRtn' in f for f in findings):
        problems.append('the cross-interface probe did NOT catch driftRtn '
                        'imported with 2 parameters against a 3-parameter '
                        'definition. findings: %r' % findings)
    if not any('driftVar' in f for f in findings):
        problems.append('the cross-interface probe did NOT catch driftVar '
                        'imported INTEGER against an INTEGER4 declaration. '
                        'findings: %r' % findings)
    for f in findings:
        if 'goodRtn' in f or 'goodVar' in f:
            problems.append('the cross-interface probe FALSE-POSITIVES on a '
                            'correct import: %s' % f)
    return problems


def check_mode_file(path):
    """A .MODE build file: check the ONE thing that has silently cost a listing.

    TWO `COMPILE`s INSIDE ONE PLANC SESSION make the second listing UNPULLABLE.
    The compiler writes it at the file position the first one left, so it comes
    out sparse - the real listing behind a hole the size of the first one - and
    the FA server refuses to read the unwritten blocks with SINTRAN error 18.
    It can then never be gated, which in this project is the whole point of a
    build.

    MEASURED on D100 2026-08-31, twice, and the arithmetic is exact:

        CHAT:LIST 430140  CHATARR:LIST 495270   difference 65130
        CHAT:LIST 405685  CHATARR:LIST 469782   difference 64097

    against a standalone CHATARR listing of 64960 bytes. NOTHING ELSE LOOKS
    WRONG: both compiles say 0 DIAGNOSTICS, the linker resolves everything and
    the first listing gates clean.

    CHATTS:MODE already EXITs and re-enters between its two compiles and has
    never had the fault - which is why CHATLIB:LIST and CHATTST:LIST always
    pulled and CHATARR:LIST never did. That is the control this check is built
    on, so it is a rule with a known-good case as well as a known-bad one.
    """
    out = []
    try:
        text = io.open(path, encoding='utf-8', errors='replace').read()
    except OSError as exc:
        return ['%s  cannot be read: %s' % (path, exc)]

    open_session = False
    compiles_here = 0
    first_line = 0
    for number, raw in enumerate(text.split(chr(10)), 1):
        line = raw.strip()
        upper = line.upper()
        # A comment line in a MODE file starts @cc - never treat one as a command.
        if upper.startswith('@CC'):
            continue
        if upper.startswith('@PLANC-100') or upper.startswith('PLANC-100'):
            open_session = True
            compiles_here = 0
            continue
        if upper.startswith('EXIT'):
            open_session = False
            compiles_here = 0
            continue
        if upper.startswith('COMPILE '):
            if open_session:
                compiles_here += 1
                if compiles_here == 1:
                    first_line = number
                elif compiles_here == 2:
                    out.append('%s:%d  a SECOND COMPILE in the same PLANC session (the first is '
                               'on line %d). The second listing is written at the file position '
                               'the first one left, so it comes out SPARSE and the FA server '
                               'refuses to read it - SINTRAN error 18, and it can NEVER be gated. '
                               'Both compiles still say 0 DIAGNOSTICS, so nothing else shows it. '
                               'Put EXIT and a fresh @PLANC-100-F00 between them, the way '
                               'CHATTS:MODE already does.'
                               % (path, number, first_line))
    return out


def main(argv):
    if not self_test():
        return 3
    if len(argv) < 2:
        print(__doc__)
        return 2

    paths = []
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] == '--include-dir' and i + 1 < len(rest):
            INCLUDE_DIRS.append(rest[i + 1])
            i += 2
            continue
        paths.append(rest[i])
        i += 1

    total = 0
    for path in paths:
        # A MODE file is a BUILD file, not PLANC source - running the language
        # checks over one invents hundreds of undeclared names. It gets its own
        # short check instead.
        if path.upper().endswith('.MODE'):
            problems = check_mode_file(path)
        else:
            problems = check(path)
        total += len(problems)
        if problems:
            for p in problems:
                print(p)
        else:
            print('%s: clean' % path)

    # Only meaningful when several sources were given, and then it is the whole
    # point: these are the faults that no single-file check can see.
    plnc_paths = [a for a in paths if not a.upper().endswith('.MODE')]
    crossed = cross_file_exports(plnc_paths)
    crossed += cross_file_interfaces(plnc_paths)
    total += len(crossed)
    for p in crossed:
        print(p)

    if total:
        print('\n%d problem(s). Every one of these has cost a build cycle on D100.' % total)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
