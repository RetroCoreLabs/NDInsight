# ENDIR-COMPLETE - exhaustive ENTER-DIRECTORY worker carve

Complete control-flow carve of `ENDIR = 140176B` (the `@ENTER-DIRECTORY` worker)
in SINTRAN III **L07**, segment **006-S3FS**, load base **26000B**. Where the
sibling folder [`../ENTER-DIRECTORY/`](../ENTER-DIRECTORY/README.md) carves the
*downstream call chain* (GDIRA / CHDSI / RXDIR / WXDIR) on the happy path, this
folder carves **every branch and every error exit inside ENDIR itself** - the
five SAA error rungs, the name-mismatch tail, and the four error-exit handlers.

- Full disassembly: [`ENDIR-COMPLETE.ASM`](ENDIR-COMPLETE.ASM)
- Pseudo-C (every branch): [`ENDIR-COMPLETE.pseudo.c`](ENDIR-COMPLETE.pseudo.c)

**Evidence rule:** every claim is graded **VERIFIED** (re-read from
`006-S3FS.bin`, disassembly shown) or **INFERRED** (reasoned from bytes +
architecture) or **OPEN** (crosses into an uncarved routine). Byte offset =
`(addr - 26000B) * 2` (decimal); values are OCTAL; on-disk multi-byte values are
big-endian words.

---

## 1. Correction to the human trace

`SINTRAN/Filesystem/code-logic/enter-directory.md` section 7 lists error **40B**
as raised at **`140140B SAA 40`**. That is a **mis-citation**. Byte-verified:

- `140140B` (`170440` = `SAA 40`) sits **before** ENDIR's entry point
  (`140176B`), in the *preceding* routine's shared error tail. No ENDIR path
  reaches it.
- The `SAA 40` that ENDIR **actually reaches** is **`140777B`**
  (dd off=76798 word=`170440`), in the name-mismatch tail entered from the name
  compare at `140352/140353`.

Both words exist and both equal `170440`; the trace pointed at the wrong one.
This README uses `140777B`. (Byte evidence, per the no-contradiction-without-
bytes rule.)

---

## 2. The five error rungs (code -> condition -> meaning)

All five `SAA` immediates are **VERIFIED** from the bytes. The *branch condition*
that reaches each is VERIFIED where a single decisive test proves it, INFERRED
where a helper's success/failure semantics are assumed.

| Code | SAA @ | Exit | Condition that reaches it | Meaning (ref-manual D.2.1) | Verdict |
|------|-------|------|---------------------------|----------------------------|---------|
| **147B** | 140254 (`170547`) | EXIT_D 141024 | `MON 124` ForceReserve returns `A < 0` at 140252-140253 (`JAP 3` not taken) | Device unit reserved for special use | SAA VERIFIED; condition VERIFIED (MON 124 + JAP) |
| **145B** | 140261 (`170545`) | EXIT_COMMON 141000 | `BSKP ONE 150 DA` on datafield word 0 finds the device-type bit SET at 140257 (`JMP 3` not taken) | Illegal on tape device | SAA VERIFIED; that bit == tape = INFERRED |
| **42B** | 140315 (`170442`) | EXIT_E 141004 | `BSKP ONE 120 DA` on `,B 24` flag scratch finds bit CLEAR at 140307 (`JMP 10` not taken) - a main directory entered out of release order | Main directory not last one released | SAA VERIFIED; branch INFERRED |
| **40B** | 140777 (`170440`) | EXIT_COMMON 141000 | name compare `SKP IF DA EQL ST` at 140352 fails (`JMP I 53 -> 140773`), OR helper at 140360 fails (`JMP I 45 -> 140773`) | Directory not on specified unit (name did not match the on-unit label) | SAA VERIFIED; branch VERIFIED (compare -> tail traced) |
| **32B** | 140370 (`170432`) | EXIT_COMMON 141000 | already-entered probe at 140363 returns nonzero and neither skip (`JMP 6`/`JAZ 5`) is taken at 140364-140365 | Directory entered (a directory of this name is already entered) | SAA VERIFIED; branch INFERRED |
| 35B | (CHDSI/WXDIR 037747) | via CHDSI err -> 141000 | surfaced *through* CHDSI when `WXDIR` write-back fails; not an ENDIR-local SAA | Master block transfer error | VERIFIED in ../ENTER-DIRECTORY |

`35B` is included because the `CHDSI` error return (`140403 -> 141000`) can carry
it; it is raised inside `WXDIR` (`037747 SAA 35`), not by ENDIR. The CHDSI
cross-system owner reject code is INFERRED (see ../ENTER-DIRECTORY sec 5.4).

---

## 3. The four error-exit handlers (what each exit DOES)

Every exit begins `STA ,B 2` = store the A-register error code into local `,B 2`,
the value ENDIR returns to the command interpreter. They differ in (a) whether
they run the **reserve-release unwind** (`RLDIR` + `MON 125` ForceRelease, undoing
the `MON 124` done at 140252) and (b) which error-report pointer they load.

| Handler | Addr | Reached by | Runs reserve-release? | Notes |
|---------|------|-----------|-----------------------|-------|
| EXIT_COMMON | 141000 | 145B, 32B, 40B, CHDSI-err (140403), 140264/140271/140274/140325 | YES - falls through 141003 into the 141005 unwind (RLDIR + conditional `MON 125`) | dd off=76800 word=`004402` |
| EXIT_E | 141004 | 42B (140317), post-mount guards 140747/140760 | YES - `RLDIR` at 141007, then `MON 125` at 141014 if `df[4]!=0` | dd off=76808 word=`004402`; `MON 125` dd off=76824 word=`153125` |
| EXIT_B | 141016 | early parse errors 140212/140214, parse-tail-A 140772 | NO - nothing reserved yet | dd off... word=`004402`; returns via 140726 |
| EXIT_C | 141020 | parse errors 140223/140225, ISETP/ICLEP fail 140300/140305 | NO | returns via 140726 |
| EXIT_D | 141024 | 147B reserve-fail (140255) | NO effective release - the `MON 124` itself FAILED, so `df[4]` release path finds nothing extra | dd off=76302(ptr) word=`141024` |

Key consequence: **any error AFTER a successful `MON 124` reserve (145B, 32B, 40B,
42B, CHDSI failure) unwinds through a path that calls `MON 125 ForceRelease`** so
the unit is not left reserved. The 147B path does not, because its reserve never
succeeded.

---

## 4. Full ENDIR control flow

```
ENDIR 140176 STD I 30 / SAB 27               prologue, 23-word frame
  |  140202-140225  arg fetch + parse (GDIRE 131732 @140222)
  |      err 140204 -> 140770 -> EXIT_B 141016
  |      err 140212/140214       -> EXIT_B 141016
  |      err 140223/140225       -> EXIT_C 141020
  v
STAGE 2  140244 GDIRA 030225 -> df (,B 25)
  |  140250 df[4]!=0 ?  --yes--> 140252 MON 124 ForceReserve
  |                                 A<0 -> SAA 147 @140254 -> EXIT_D 141024
  |  140256 df[0] tape-bit set ? --yes--> SAA 145 @140261 -> EXIT_COMMON 141000
  |  140263/140270/140272 helpers   err -> EXIT_COMMON 141000
  |  140277 ISETP / 140304 ICLEP    err -> EXIT_C 141020
  v
STAGE 3  140306 flag & 0o120 clear ? --yes--> SAA 42 @140315 -> EXIT_E 141004
  |  140320/140324 helpers          err -> EXIT_COMMON 141000
  v
STAGE 4  140326-140352 byte-wise name compare
  |  140352 name != label ?        --yes--> 140773 -> SAA 40 @140777 -> EXIT_COMMON
  |  140360 helper fail            --yes--> 140773 -> SAA 40 @140777 -> EXIT_COMMON
  |  140363 already-entered probe  --yes--> SAA 32 @140370 -> EXIT_COMMON 141000
  v
STAGE 5  140402 JPL I 33 = CHDSI 037763   *** THE MOUNT ***
  |  140403 CHDSI err -> EXIT_COMMON 141000
  v  140404 CHDSI ok -> 140436 post-mount bookkeeping
POST-MOUNT 140436+  in-core directory-table update
       guards 140747/140760 -> EXIT_E 141004   (release on failure)
       success -> return rc=0  (directory MOUNTED)
```

---

## 5. VERIFIED / INFERRED / OPEN

| Item | Verdict |
|------|---------|
| ENDIR entry `140176 = 021030`, `SAB 27` frame | VERIFIED (dd off=76028) |
| `MON 124` ForceReserve @140252 = `153124` | VERIFIED (dd off=76116) |
| All five SAA immediates 147/145/42/40/32 (bytes) | VERIFIED (dd off=76120/76130/76186/76798/76272) |
| 147B trigger = reserve fail (`JAP` not taken) | VERIFIED |
| 40B trigger = name compare fail -> 140773 -> 140777 | VERIFIED |
| 145B trigger = device-type bit; *which* bit = tape | SAA VERIFIED / bit = INFERRED |
| 42B trigger = main-dir ordering guard | SAA VERIFIED / branch INFERRED |
| 32B trigger = already-entered probe | SAA VERIFIED / branch INFERRED |
| Error-exit ptrs 141024/141000/141004 (@140407/140410/140422) | VERIFIED (dd off=76302/76304/76324) |
| `MON 125` ForceRelease in EXIT_E @141014 = `153125` | VERIFIED (dd off=76824) |
| CHDSI ptr @140435 = `037763`, GDIRA ptr @140405/140244 = `030225` | VERIFIED (dd off=76346/76298) |
| Release-on-error semantics (EXIT_COMMON/EXIT_E run MON 125) | VERIFIED (control flow) |
| Intermediate helper roles (010500, 050323, 053047, 037377, 034557, 036511, 035231, 035531, 041552, 047402, 035476) | OPEN - other 006-S3FS routines, not carved here; roles labelled INFERRED from context |
| GDIRE = 131732B (helper @140222) | VERIFIED (ptr) / role INFERRED |
| CHDSI cross-system owner reject exact code | INFERRED (see ../ENTER-DIRECTORY sec 5.4) |
| Post-mount in-core table field semantics (140436+) | OPEN - partially carved |

---

## 6. Cross-links

- [`../ENTER-DIRECTORY/README.md`](../ENTER-DIRECTORY/README.md) - downstream
  chain GDIRA -> CHDSI -> RXDIR -> WXDIR, the page-0 read, checksum/owner
  interlock, and the MON-124 -> MCTAB[124]=037076 PRSRV dispatch.
- [`../RCBLO/README.md`](../RCBLO/README.md) - the device seam
  (`JPL I ,B 10` through datafield word `,X 14`) and the "why the SCSI page-0
  read is never enqueued" analysis.
- [`../PRSRV-124B/`](../PRSRV-124B/) - the MON 124B ForceReserve worker that
  140252 dispatches to (and MON 125B ForceRelease that the error exits use).
- [`../../../re/segments-ref/006-S3FS/006-S3FS.asm`](../../segments-ref/006-S3FS/006-S3FS.asm)
  - the byte-identity-checked whole-segment listing this carve is cut from.
- [`SINTRAN/Filesystem/code-logic/enter-directory.md`](../../../../../../../SINTRAN/Filesystem/code-logic/enter-directory.md)
  - the human end-to-end trace (integrated here; 40B address corrected in sec 1).

---

**Provenance:** carved `006-S3FS` SINTRAN L07 bytes, load base 26000B; ENDIR body
140176-140404, error handlers 140770-141041; every dd offset listed above
reproduced from `versions/L-VSX-500/segments/006-S3FS.bin`. Error meanings from
`Reference-Manuals/ND-60.050.06 SINTRAN III Users Guide.md` table D.2.1.
