# C Compiler Guide - CC-100/CC-500

**NORD C Compiler for ND-100 and ND-500**

**Version:** 1.0 (Placeholder)  
**Date:** October 17, 2025  
**Status:** Reference Guide

---

> **Looking for C on the ND-500/5000 with the NC compiler (Norsk Data C, version A06)?** That is a
> different, later compiler than CC-500. See
> [../../ND500/NC-C-COMPILER-GUIDE.md](../../ND500/NC-C-COMPILER-GUIDE.md) and
> [../../ND500/ND-LINKER-PRACTICAL-GUIDE.md](../../ND500/ND-LINKER-PRACTICAL-GUIDE.md).

---

## Installing the C Compiler

CC-100 (ND-100) and CC-500 (ND-500) are **separate products** with separate floppy sets — CC-500
has a full install sheet; CC-100's install steps have not yet been transcribed from its floppies.

- **ND-500 — CC-500**, product `ND-210761`: [ND-210761B — C-Compiler for ND-500, version B](../../../Installation/Software/ND-210761/ND-210761B/README.md)
  (verified from the PD sheet — floppy `210761B00-XX-01D`, or a 3-disk single-density set).
- **ND-100 — CC-100**, product `ND-10760` (article number assumed from the floppy label, no PD
  sheet found): [ND-10760A — C-Compiler for ND-100, version A](../../../Installation/Software/ND-10760/ND-10760A/README.md)
  (install procedure recovered verbatim from the real floppy set `10760A00-1` + `10760A00-2`).

---

## Quick Start

**See [QUICK-START-EXAMPLES.md](../../QUICK-START-EXAMPLES.md) Section 3 for complete Hello World example.**

### Minimal Example

```c
#include <stdio.h>

main()
{
    printf("HELLO FROM C!\n");
    return 0;
}
```

### Build Process

```bash
@CC-100 HELLO:C              # Compile C to BRF
@NRL                         # Start linker
*IMAGE 100                   # ND-100 target
*PROG-FILE "HELLO"
*LOAD CC-2HEADER             # C runtime header
*LOAD HELLO                  # Your program
*LOAD CC-2BANK               # C runtime library
*LOAD CC-2TRAILER            # C runtime trailer
*EXIT
@HELLO                       # Run
```

---

## Reference Manual

**Complete C compiler documentation:**

**Location:** [Reference-Manuals/ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual.md](../../../Reference-Manuals/ND-60.214.01%20CC-100%20and%20CC-500%20C-Compiler%20User%20Manual.md)

**Manual:** ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual

---

## Key Differences from Standard C

1. **Runtime Library Required:** Always link CC-2HEADER, CC-2BANK, CC-2TRAILER
2. **Memory Model:** 16-bit word-addressable on ND-100
3. **I/O Functions:** Standard stdio.h available
4. **Compiler Invocation:** `@CC-100` for ND-100, `@CC-500` for ND-500

---

## See Also

- **[QUICK-START-EXAMPLES.md](../../QUICK-START-EXAMPLES.md)** - Complete working example
- **[LINKING-GUIDE.md](../../Workflow/LINKING-GUIDE.md)** - Linking C programs with runtime
- **[SINTRAN-DEVELOPER-GUIDE.md](../../SINTRAN-DEVELOPER-GUIDE.md)** - Master guide
- **Reference Manual:** [ND-60.214.01 CC-100 and CC-500 C-Compiler User Manual](../../../Reference-Manuals/ND-60.214.01%20CC-100%20and%20CC-500%20C-Compiler%20User%20Manual.md)

---

**For comprehensive C development, refer to the reference manual and QUICK-START-EXAMPLES.md.**

