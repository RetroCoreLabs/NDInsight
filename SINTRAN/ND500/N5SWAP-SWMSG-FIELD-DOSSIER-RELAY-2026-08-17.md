# N5SWAP / SWMSG field dossier (relayed 2026-08-17)

Provenance: compiled by an exploration session from the NPL sources, symbol
tables, and existing carve docs, and relayed to the ND500UC milestone loop on
2026-08-17 for use in the milestone-12 (fn-3) carve work. Grades (PROVEN /
INFERRED / OPEN) are the compiler's own; two reconciliation notes from the
main session are at the end.

Short forms used below: L07 = E:\Dev\Ronny\NDInsight\SINTRAN\NPL-SOURCE\SYMBOLS\L07\N500-SYMBOLS.SYMB.TXT (octal values, 5-char truncated names). MP = ...\NPL-SOURCE\NPL\MP-P2-N500.NPL. RP = ...\NPL\RP-P2-N500.NPL. S3SM5 = ...\SINTRAN\ND500\CARVE-S3SM5-MSWIN-STAMP-AND-FILL-2026-07-21.md. CAT = ...\ND500\ND500-MAILBOX-MESSAGE-CATALOG.md. DEEP = ...\ND500\swapper\swapper-k01-deep-analysis.md. DSEG = ...\swapper\swapper-k01.dseg.md. GATE1 = ...\ND500\GATE1-SWAPPER-COLDSTART-TRACE-ANALYSIS-2026-07-21.md. ANL12 = ...\ND500\ND500-SWAPPER-ANALYSIS.md sec 12 (lines 518-663).

## 0. Structural correction (lead with this)

| Fact | Grade | Cite |
|---|---|---|
| TWO buffers: SWMSG = the swapper's OWN process-0 buffer; MSGTOSW = the REQUESTER's MESSBUFF | PROVEN | MP:2857-2859; RP:776 |
| SWMSG addr 0o53370 (K03) / 0x902C (L07 kallsyms) / 0o110054 (catalog) | PROVEN | K03\SYMBOL-2-LIST.SYMB.TXT:1015; L07\l07-kallsyms.txt:8838; CAT:137 |
| 55MESSIZE = 0o200 = 128 words | PROVEN | L07:277 |
| The 13 halfwords RIOM'd are the head of MSGTOSW, NOT SWMSG | INFERRED (strong) | MP:2861-2866 + GATE1 (RIOM source 0x420E30 is a MESSBUFF: FFFFFFFF link, N5STA +4, MICFU +0xC) |
| RIOM count is NOT constant 13 — from a 29-entry per-function count table (see reconciliation note A on its address) | PROVEN | DSEG:1190,1196-1198 (`h riom $1000440264,$1000440274,$1000440074+`) |

## 1. SWMSG / message field layout (octal word offsets)

### 1a. Header (RIOM window covers 0..0o14)

| Off | Sym | Meaning | Grade | Cite |
|---|---|---|---|---|
| -1 | 5MSFL=177777 | flags: 5IEXQUEUE b15, 5SYSRES, 5CPUBOUND, 5IBRK, S5IBRK, 52ESCSET | PROVEN | L07:1457; MP:380,939-944 |
| -3 | MAGNO=177775 | magic number; WRITER NOT FOUND in NPL | PROVEN val / OPEN writer | CAT:446 |
| -5 | 5PRIO=177773 | priority; swapper=300 | PROVEN | L07:1584; MP:439 |
| -6 | 5CPUN=177772 | CPU number | PROVEN | L07:1543; MP:440 |
| -10 | 500TU=177770 | ND-500 CPU time used | PROVEN | L07:505 |
| 0-1 | LINK/LINK2 | queue link (double), -1 sentinel | PROVEN | RP:794 |
| 2 | N5STA=2 | state word (1d) | PROVEN | L07:5746 |
| 3 | SENDE=3 | sender proc#; -1 = watchdog/HIMESS | PROVEN | L07:4596; RP:802,821 |
| 4 | 5RECE=4 | receiver; =5SWPROC for swapper | PROVEN | L07:1186; MP:437,875 |
| 5 | X5ACT | size/activation | PROVEN | CAT sec1 |
| 6 | MICFU=6 | the ND-500 microcode command (1c) | PROVEN | L07:5266 |
| 7 | SWFUN=7 / N500A=7 | OVERLAY: if MICFU=3SWMESS this is the MSW* code; else ND-500 logical addr | PROVEN | L07:4986 / 5745 |
| 10 | SWRST=10 | swap restart status | PROVEN | L07:3481; MP:500 |
| 11 | N100A/STOPR/KFLIP/SKFLI=11 | OVERLAY: ND-100 phys addr / stop reason / error flag | PROVEN | L07:5743,6995,4836; MP:471 |
| 12 | NUMPA=12 | param count = WRITE-BACK MASK; 5ACTSWAPPER writes 6, MONICO writes 0 | PROVEN | L07:5744; MP:2884 |
| 12 | OLDMI=12 | saved MICFUNC (5MMESSAGE overlay) | PROVEN | L07:6136; MP:491,1176 |
| 13 | NRBYT/MCNO/FUNCV/5DP2=13 | OVERLAY: byte count / MON-call number / return value / param-2 value | PROVEN | L07:6046,5714,2127,3178 |
| 14 | MSWMC=14 | swapper-monitor-call subfield (symbol only, no NPL use) | PROVEN val / OPEN meaning | L07:5462 |
| 14 | 5DITN=14 | data-in-transfer flag | PROVEN | L07:1536; MP:1140 |
| 16 | TRAPN=16 | trap number (fault path) | PROVEN | L07:744; MP:864,2879 |
| 17 | 26NRB=17 | write-back byte count | PROVEN | L07:3185; MP:986 |
| 37 | SMCNO=37 | saved MON-call number | PROVEN | L07:5040; MP:1302 |
| 40 | PDR1=40 (padr2=42) | parameter descriptors | PROVEN | L07:1947; MP:1320,1136 |
| 74 | SM26A=74 | saved write-back logical addr | PROVEN | L07:4131; MP:987-988 |
| 100-120 | PAR1=100..PAR9=120 | MON-call parameter VALUES | PROVEN | L07:1937-2176 |
| 100-112 | RETP1=100,RETP2=102,RETP3=104,RETP4=106,RETP5=110,RETP6=112 | return-value slots (doubles) | PROVEN | L07:858,925,999,1081,1180,1268; MP:473-489 |
| 135 | SM26N=135 | saved write-back count | PROVEN | L07:4988; MP:985 |
| 140 | ABUFA=140 | aux (MON 60) buffer address | PROVEN | L07:2641; MP:1133,1312 |
| 143 | SPFLA=143 | NONZERO = ROUTINE ADDRESS DECOMESS jumps to | PROVEN | L07:4126; MP:1141,1149,1339 |
| 144 | XADPR=144 | process-descriptor address | PROVEN | L07:6717; MP:444,518,2895 |
| 147 | PLINK=147 | backward queue link | PROVEN | L07:2531; MP:1029 |

Requester-side return flags read by SWMESS: PRET1=12, PRET2=13, PRET3=14,
PRET4=15, PRET5=16, PRET6=17 (L07:1946,1987,2024,2060,2103,2126; MP:473-489).

### 1b. SWMSG high "administration" region

| Off | Sym | Meaning | Grade | Cite |
|---|---|---|---|---|
| 0o101 | SWPFU=101 | 5ACTSWAPPER writes SWACTIVE(=0) as STATE MARKER; SWAPPER writes its request code here; SWPDECODER dispatches on it | PROVEN | L07:3594,3479; MP:2867,914 |
| 0o102 | RETP2=102 | return value slot | PROVEN | L07:925 |
| 0o103 | SWPST=103 | BIDIRECTIONAL. ND-100->swapper: activation reason = MSGTOSW.SWFUN (MSW* code) or trap number. swapper->ND-100: ERROR CODE | PROVEN | L07:3480; MP:2883 (write), MP:952-961 (read as error) |
| 0o104 | HSWPI=104 | HIGH word of DOUBLE "SWPINFO" = phys addr of MSGTOSW; 0 = no process served | PROVEN | L07:6463; MP:2866,934-935,1062 |
| 0o105 | SWPIN=105 | LOW word of SWPINFO; also base of the parameter block (`SWMSG+"SWPINFO"`) | PROVEN | L07:4985; MP:1072; RP:22 |
| 0o143 | SPFLA=143 | error/flag word on the LNEWSWAP return path | PROVEN | L07:4126; MP:957 |
| 0o144 | XADPR=144 | proc-descr addr | PROVEN | L07:6717 |
| — | SWFMA(SWFMAX)=6 | SWPDECODER upper bound | PROVEN | L07:4127; MP:915 |

### 1c. MICFU values (all PROVEN, L07)

3RMICV=1 (:4373), 3SWMESS=5 (:4595), 3RMED=0o10 (:4475), 3WMED=0o11 (:4474),
3START=0o23 (:3191), 3MONCO=0o24 (:4372), 3TRACO=0o25 (:4371),
3WMONCO=0o26 (:4987), 3FITRNSF=0o27 (CAT sec2), 3RPREG=0o44 (CAT sec2; RP:803).

TRAP: MICFU=3SWMESS=5 and SWFUN=MSWIN=5 are DIFFERENT FIELDS BOTH HOLDING 5 —
do not collapse (S3SM5 sec 7).

### 1d. N5STA values (PROVEN)

1 MSGN500 (L07:7064), 2 WAITING (:2180), 3 ANSWER (:2798), 4 5ERANSWER,
5 SWPWAIT (:4130), 6 SWPPING (:4837), 7 PSWWAIT (:2297), 0o15 PSW1WAIT (:2839),
0o21 5IALLOPAGE (:1456). High bits 160000B = power-fail, ALWAYS preserved
(`A/\160000\/MSGN500`, MP:992).

### 1e. Who fills the body — segment 030-S3SM5, NOT the NPL nucleus

The nucleus only TESTS SWFUN, never stores it; S3SM5's source is NOT in the
repo, so any grep of NPL-SOURCE for stores is a FALSE NEGATIVE (this already
produced one published wrong conclusion). All PROVEN byte-carved, S3SM5 sec
3C/3D:

- Generic builder, runtime octal 140765..141001: base `X:=[B-67]`; gate at
  140765 (if [B-61]!=0 SWFUN:=0o24 MSWSWAIT, else SWFUN:=[B-77]
  caller-supplied, =MSWIN=5 for swap-in); msg[2]:=1; msg[4]:=[B+72];
  MICFU(6):=5.
- Full-body builder, runtime octal 162155..162207: MICFU(6):=5; SWFUN(7):=0o24;
  fills offsets 2,3,4,0o10,0o11,0o12(:=0o23),0o13,0o14,0o15,0o16(:=1),0o17 +
  DOUBLES at 0o110 and 0o112. ONLY word-by-word body map that exists.
- S3SM5 also reads SWMSG.SWPST(0o103) @164104 and issues MON 377 @164106
  (3 sites).
- OPEN: the SEMANTICS of those body offsets per MSW code.

## 2. MSW* table 0..0o34 — 21 symbols exist, NOT 29

All PROVEN; source L07 (line cited), cross-checked in L07\SYMBOL-1-LIST.SYMB.TXT
and L07\l07-kallsyms.txt:3521-3965.

0=MSWFI (:5612) | 1=MSWUF (:5550) | 2=MSWSO (:5713) | 3=MSWMI (:5611) |
4=MSWMD (:5494) | 5=MSWIN (:5680, "swap-IN" INFERRED) | 6=MSWPO (:5712) |
7=MSWST = **MSWSTART** PROVEN spelled out (:5224; MP:431) | 0o10=MSWFO (:5711) |
0o11=MSWIP (:5081) | 0o12=MSWPF = **MSWPFAULT** PROVEN spelled out (:5549;
MP:877) | 0o13=MSWME (:5531) | 0o14=MSWMC (:5462) | 0o15=MSWSP (:5080) |
0o16=MSWSG (:5571) | 0o17=MSWIS (:5181) | 0o20=MSWRS (:5180) |
0o23=MSWWB (:5430, "WriteBack" INFERRED) | 0o24=MSWSW = **MSWSWAIT** PROVEN
spelled out (:5296; MP:464; S3SM5 `SAA 24` @162200) | 0o33=MSWPR (:5134) |
0o34=MSWDO (:5710, = jump-table max index 0x1C).

NO SYMBOL for: 0o21, 0o22, 0o25, 0o26, 0o27, 0o30, 0o31, 0o32. (0o30/0o32 are
MSCRS/MSCRENEWVERS in a DIFFERENT namespace — L07:5179,5530; MP:974.)

VERSION FACT (PROVEN, callout-worthy): K03\N500-SYMBOLS.SYMB.TXT:3480-3819 has
the same set MINUS MSWPR and MSWDO — codes 0o33/0o34 were ADDED between K03 and
L07. Matters when matching a SWAPPER-K01 (K-gen) domain to an L-gen 29-entry
table.

Nucleus tests only three things on SWFUN (PROVEN): `IF A=MSWSTART` MP:431,
`IF A=MSWSWAIT` MP:464, all else falls to `CALL 5ACTSWAPPER; GO TRACO`
MP:509-511.

## 3. What SINTRAN sends first at boot

ANSWER: on the first round trip, NO function code at all — the first reply is a
STATE TRANSITION, SWMSG.N5STA := PSWWAIT(7) = "swapper free".

1. LOAD-SWAPPER -> MON 60 subfn 0o7 SWLOD -> FUNCS[007] LDSWA @143551 in
   030-S3SM5; prints "> Loading Swapper". PROVEN — CAT:455-462; S3SM5 sec 3B
   (raw string @0x071BF).
2. START-SWAPPER -> MON 60 subfn 0o54 STSWP -> FUNCS[054] RUNSW @163621; posts
   SWFUN=MSWSTART(0o7). PROVEN — CAT:459-461.
3. SWMESS `IF A=MSWSTART`: SWPPING->N5STA; HSWPI:=CNVWADR(5MMESSAGE);
   MICFU:=3START(0o23); SENDE:=5SWPROC; 5RECE:=5SWPROC; SWPFU:=SWACTIVE;
   5PRIO:=300; 5CPUN:=CPUNO; 5SCPU bit->5CPUB; N5STA:=MSGN500; clears SLICE in
   PSTAT ("Swapper is not timesliced"); ITO500XQ; XACTRDY; LOWACT500.
   PROVEN — MP:431-461.
4. ND-500 runs process 0 from P=4 (MACRO_STARTL), build-tag self-check, zeroes
   DSEG 0x240B0/0x240B4, then MON 377B argc=4 selector value 1 = the announce.
   PROVEN — CAT:431-436; GATE1 row 0x0800823F ("argc=4 [V log:4082]").
5. DECOMESS (MICFU=3START + STOPR=MOCALL(1)) -> MCHANDEL -> `IF A=N5SWAP AND
   X=SWMSG` -> SWPDECODER -> SWPFU=1 -> LNEWSWAP -> HSWPI==0 -> `SWPD4:
   PSWWAIT; X:=SWMSG; CALL WN5STATUS % Mark swapper free` -> drains empty
   swap-wait FIFO -> `EMPTY:` zeroes HSWPI+SWPIN+X5SWO -> NXTMSG. PROVEN —
   MP:1286,1346-1348,933,1031,1060-1065.
6. 5ACTSWAPPER hands work ONLY on PSWWAIT (`IF A=PSWWAIT THEN`). PROVEN —
   MP:2864.
7. First REAL work code in a normal boot->RUN flow is MSWPFAULT(0o12):
   TRAPDECODER trap 0o46 -> `MSWPFAULT SHZ 10+D` -> STA into TRAPN -> `CALL
   5ACTSWAPPER`. INFERRED (strong) — MP:868-879.
8. LIVE: SINTRAN's 1164 writes to requester buffer 0x420E30 all occur during
   RUN, AFTER cold-start; at cold-start the buffer is all zeros — the swapper
   is 23B-activated with an EMPTY message. PROVEN — GATE1 "ORDERING PROBE
   RESULT (2026-07-21)".

Also PROVEN: RUN posts NO swapper work directly —
CARVE-RUN-TO-WORK-POSTING-CHAIN-2026-07-20.md.

## 4. MON 377B announce semantics

### 4a. Identity / authorisation (PROVEN)

`SYMBOL N5SWAP = 377 % MON.CALL USED BY THE SWAPPER.` MP:1273 (also
MP-P2-PERF-SAMP.NPL:1100). Ordinary MON-call mailbox path: STOPR=MOCALL(1),
MCNO(13)=0o377, NUMPA(12)=argc, param ADDRESSES at PDR1=0o40+, param VALUES at
PAR1=0o100+ (CAT:437-439). Authorised BY BUFFER IDENTITY — MP:1346-1356:
`IF A=N5SWAP THEN IF X=SWMSG THEN CALL SWPDECODER ELSE (5DBFLAG!=0 ->
E5DEBUG+XRSTARTALL) A:=25; CALL WN5STATUS % YOU ARE NOT AUTHORIZE TO DO THIS;
CALL 5RRTWT`.

DISTINCT FROM SWMC: SWMC = handler for ND-500 MON 510B, GOSW slot 8 of
L12MIN=500..L12MAX=523 (MP:1267,1382-1390); bytes 142153B (CAT:515), 0xC46B
(l07-kallsyms.txt:11254). Explicitly RULED OUT as the MSWIN sender —
CARVE-MSWIN-MESSAGE-SENDER-2026-07-21.md sec G. Do not conflate 510B SWMC with
377B N5SWAP.

### 4b. Sub-function selectors — SWPDECODER (MP:912-919)

Reads SWMSG.SWPFU, bound SWFMAX=6, 7-entry GOSW. All PROVEN:

| SWPFU | Handler | argc | SINTRAN action | Cite |
|---|---|---|---|---|
| 0 | ESWPFATAL | — | `X:=SWMSG; SWPFATAL` -> XRSTARTALL -> CALLID12 | MP:1192 |
| 1 | LNEWSWAP | 4 | start current work / find next requester; escape+error decode; SWPD4 mark PSWWAIT; drain FIFO | MP:933-1065 |
| 2 | LSWPAGE | 7 | DISK I/O, dominant. PSW1WAIT->N5STA; move 11 words from SWMSG+SWPINFO into ND-100 XSDUNIT ABSTR param array; disc-opt (XABSFUNC 60->66, Phoenix subunit bits); enqueue QP100.QP5SW or 5SWACTRT | MP:1070-1103 |
| 3 | LPRSUSPEND | (never used) | `GO FAR ESWPFATAL` — "Suspend proc. not implemented" | MP:1116 |
| 4 | LALLOPAGE | 6 | alloc new page to file; MICFU->OLDMI; copy 0o120 words SWMSG->requester msg; 5IALLOPAGE(0o21)->N5STA; 5RRTWT | MP:1170-1188 |
| 5 | LDATREADY | 3 | copy swapper msg->requester msg, restart ND-100 proc; saves doubles SWDD1/2/3 at N500A/+0o20/+0o40; builds 3RMED read of 0o400 bytes with SPFLA:=INLDATREADY; rebuilds SWMSG | MP:1124-1165 |
| 6 | LCLTSB | 2 | clear TSB multi-CPU; ND-5000 LMPCLR reads SWMSG.5DP2(0o103) as clear mask -> X5CLR -> CLRKICK | MP:1198-1240 |
| 0o2047 | SWPFA (>SWFMAX) | 2 | falls to ESWPFATAL | L07:4128; 5P-P2-MON60.NPL:79 |

Cross-check PROVEN (DEEP:139-180): the 15 carved sites carry 1(x1,argc4),
2(x8,argc7), 4(x1,argc6), 5(x1,argc3), 6(x3,argc2), 0o2047(x1,argc2) — argc
matches exactly; 3 never used because unimplemented.

### 4c. The 4 announced addresses

| Arg | Address | Meaning | Grade | Cite |
|---|---|---|---|---|
| 1 | 0x08012A28 | Address of a CONSTANT WORD whose VALUE IS 1 — the sub-function selector for LNEWSWAP. **NOT a status word.** SINTRAN sees it as SWMSG.SWPFU after write-back | PROVEN | DEEP:153,175 |
| 2 | 0x080240B0 | OUT param: SINTRAN writes the next FUNCTION CODE here. Swapper copies [0x240B0]->[0x240B8] (pseg 10544-10545), bound-checks 0..0o34 (`w comp2 ...,$34`, pseg 10560-10566), jumpg via 29-entry table @0x26198 | PROVEN mechanism / INFERRED-strong content (=SWPST carrying MSW* code) | ANL12 12.4/12.5; DSEG:1097,1099,1197 |
| 3 | 0x080240B4 | OUT param: SINTRAN writes the ND-100 WORD ADDRESS of the requester's MSGTOSW = the SWPINFO double at SWMSG.HSWPI/SWPIN. Swapper `h riom`s from it into [0x240BC] | INFERRED (strong) | MP:2861-2866; GATE1 live RIOM source = MESSBUFF 0x420E30 |
| 4 | b.24 | A STACK LOCAL in the swapper's frame (result slot), NOT a DSEG cell | PROVEN | DEEP:153 |

0x080240BC = destination buffer / record base (`r:= $1000440274` x15) —
DSEG:1100,1198.

### 4d. 0x0802428C

DOES NOT EXIST in the repo (grepped all .md + NPL + all symbol generations).
Two candidates, both PROVEN: 0x0802408C = the 29-entry RIOM HALFWORD-COUNT
table indexed by function code (DSEG:1190,1196-1198) — this is why RIOM length
varies and 13 is one entry; or b.24 = the 4th announce arg. (See reconciliation
note A.)

### 4e. 0x223 / 0o1043 / decimal 547

**OPEN, NOT FOUND ANYWHERE.** Searched E:\Dev\Ronny\NDInsight for `0x223`,
`0o1043`, `1043B`, `001043`, `547`-as-symbol-value across all .md, the whole
NPL tree, and K03/L07/M06/s3vs-4.symb. Ruled out: not an MSW code (max 0o34),
not SWPFA(0o2047), not in the swapper error band 0o2040-0o2051, not a MICFU
code, not a MON number, not NUMPA. The bound check 0..0o34 would REJECT 547 ->
fatal path. Recommend marking emulator-origin (uninitialised/harness) until
proven otherwise. NOTHING in SINTRAN is known to write it. (See reconciliation
note B.)

### 4f. The "MON 24B write-back mask" (PROVEN)

MONICO/MCCO, CC-P2-N500.md sec 359-372 quoted at CAT:120-128:
OKMONICO T:=0 / EMONICO T:=1; MONICO: FUNCV(13):=return value, KFLIP(11):=error
flag, NUMPA(12):=0, MICFU(6):=3MONCO(0o24); MCCO: N5STA(2):=MSGN500(1),
proc-desc:=[XADPR(144)], PSTAT:=5ACTIVE.

NUMPA = how many MON-call params the microcode writes back into the caller's
frame; 5ACTSWAPPER sets 6 with comment `% Par #2 & par #3 will be written into`
(MP:2884); trap-restart variant sets 4 (CAT:128). THIS is how 0x240B0/0x240B4
get filled — they are the swapper's by-reference MON-call args.

NUMPA is genuinely a PER-PARAMETER BITMASK on the MSWSWAIT path (PROVEN,
MP:471-489): read SKFLI(0o11); if no error, for each of PRET2/PRET4/PRET5/PRET6
(requester offsets 0o13/0o15/0o16/0o17) that is nonzero, copy the double into
SWMSG.RETP2/RETP4/RETP5/RETP6 (0o102/0o106/0o110/0o112) and set bit 1/3/4/5 in
L; finally `X:=SWMSG; A:=L; *AAX NUMPA; STATX`.

## 5. What the swapper writes back

### 5a. SWPFU(0o101)

The swapper->ND-100 request code (table 4b). SWPFU REFUTED as the source of the
0x240B8 fn code (ANL12 12.3/12.5).

### 5b. SWPST(0o103) on the return path = ERROR CODE (PROVEN, MP:952-961)

`*AAX SWPST; LDATX; A=:D; IF A><0 THEN` -> zero HSWPI+SWPIN -> read
CSWPM.SPFLA(0o143); nonzero -> EMONICO with SWPST as error code + XACTRDY; else
SWPD2 (restart ND-100 proc with the code in N5STA). **SWPST IS BIDIRECTIONAL —
load-bearing for emulation.**

OK path (MP:968-1002): RN5STATUS(CSWPM); if A/\17777=SWPPING read MICFU;
3SWMESS -> restart ND-100 proc with ANSWER preserving A/\160000; 3START -> set
3TRACO; 3WMONCO -> restore write-back descriptor (SM26N->26NRB, SM26A->26ADD).
MSCRS(0o30)/MSCRENEWVERS(0o32): copy SWMSG.RETP4+1 into CSWPM[0o10]
(MP:974-977).

### 5c. The 0o66 code — PROVEN bytes / OPEN meaning

Dispatch indices 6,7,16,25,26,27 share one shape — set a local to constant
0o66, zero+test an always-zero adjacent local, `call 1000003057`, which issues
MON 377B sub-fn 2 (LSWPAGE). Cite swapper-k01-handlers.md:298-302,305-309,
370-372,439-448,475-496; that doc lists "what 0o66 means" as open at :531.

NEW CANDIDATE ANSWER (INFERRED, testable): LSWPAGE MP:1077 reads `IF
XABSFUNC/\77=60 THEN XABSFUNC+6=:XABSFUNC FI % Use func=66 instead of 60` —
i.e. 0o66 is an ND-100 ABSTR (MON 131) DISC FUNCTION CODE (0o60 plain
transfer, 0o66 disc-optimised), and XABSFUNC is a word of the 11-word block
moved from SWMSG+SWPINFO (MP:1072). TEST: does the 0o66 constant become
parameter #2 of the argc-7 LSWPAGE call?

### 5d. Error codes

| Code | Symbol | Meaning | Grade | Cite |
|---|---|---|---|---|
| 0o2047 | SWPFA = SWPFATAL | FATAL ERROR FROM SWAPPER | PROVEN spelled out | L07:4128; 5P-P2-MON60.NPL:79 |
| 0o2067 | EILPH | UNIQUE symbol at 002067; truncated name | PROVEN val / INFERRED name | L07:1346 |
| 0o2070 | EPFIN = EPFINSWAP | PAGE FAULT IN SWAPPER — fatal, XRSTARTALL | PROVEN | L07:1535; MP:881 |
| 0o1030 | ILADS | UNIQUE resolution for 001030 ("illegal address") | PROVEN val / INFERRED name | L07:6266 |
| 0o1031 | — | **NO SYMBOL with value 001031 in L07 — OPEN** | OPEN | searched N500-SYMBOLS + SYMBOL-1-LIST |
| 0o55 | — | **AMBIGUOUS — 20+ symbols share 000055** (5BRKP:19, 5SERR:218, DALCD:415, UFRIE:1165, PAD7D:2396, FPAR1:2638, RESDB:3137, 5D52:3199, SSIXR:3207, CMSET:3469, 5DPA7:3746, BRKCH:3823, ER29:3863, SUNIH:4789, SEGFI:4816, SWATI:4820, XRRNL:6497, XFSFM:6552, XWAIT:6847, XXVSX:6928). Unresolvable from the symbol table alone | OPEN | L07 as listed |
| 0o1055 | SWDER = SWDERR | disc transfer error: `X:=SWMSG; A:=1055; CALL EMONICO % Error in transfer (swderr=1055)` | PROVEN | L07:3184; MP:1111 |
| 0o25 | — | "YOU ARE NOT AUTHORIZE TO DO THIS" (non-SWMSG MON 377B) | PROVEN | MP:1354 |
| 0o2005 | ILTRA | unknown trap (D>53) | PROVEN | L07:6680; MP:866 |
| 0o2142 | ESCST | escape typed while using swapper | PROVEN | L07:393; MP:947 |
| 0o2054 / 0o2103 | EIMDCONF / EILOCS | memory-pattern-test / CS-verify errors in 030-S3SM5 | PROVEN | CAT:467 |

Swapper error band (PROVEN, swapper\N500-SYMBOLS.SYMB): SWADE=2040 ...
NOMAS=2046, SWPFA=2047, MEMNA=2050, MICFA=2051.

## 6. ND500-STATUS-AND-INDEX.md cross-links

| Line | Pointer |
|---|---|
| 729-798 | sec 00, 2026-07-25 — NEWEST swapper entry. Swapper reaches its MESSAGE-WAIT LOOP at P=0x08000677 (the argc-2 SWPFA site: `call ...377,$2,$1000225040,$1000437234; ifkret; go $...757`). Blocker = message CONTENT, not microcode. RETRACTS "spins because the announce stub returns the same message forever". Its OPEN item #1 is literally "Give the swapper a structurally valid SWMSG — carve the field layout". Doc of record: OCTOBUS-SWAPPER-HANDOFF-2026-07-25.md |
| 801+ | sec 0a, 2026-07-20 — four retractions; OPEN-QUESTIONS-REGISTER-2026-07-20.md (~90 items, sec1 = swapper track) |
| 823 | CARVE-SWAPPER-CONTEXT-BLOCK-BUILDER-2026-07-20.md — SINTRAN builds NEITHER context/register block NOR PST NOR PCB, only the mailbox MESSAGE |
| 835 | CARVE-RUN-TO-WORK-POSTING-CHAIN-2026-07-20.md — RUN posts NO swapper work directly; trap 0o46 -> 5ACTSWAPPER -> 5SWRT (MON 131 ABSTR) |
| 642 | `076 TOSWP` is "MESSAGE TO SWAPPER", not "copy segment to swap" (`ITOSWP: % FUNCTION=076: MESSAGE TO SWAPPER`). NOT YET READ — E:\Dev\Ronny\NDInsight\tools\sintran-segment-carver\versions\L-VSX-500\re\mon-analysis\60B-N500M\60B-076B-ITOSWP\60B-076B-ITOSWP.pseudo.c. MOST LIKELY source of the missing per-code body semantics. Sibling: ...\re\mon-analysis\510B-CallSwapper\510B-CallSwapper.pseudo.c |
| 507 | 2026-08-11 — the PST is SWAPPER-maintained, not SINTRAN-maintained (elimination + ND-05.017.01 x3) |
| CAT:452-454 | POISONED PRIOR: ND500-SWAPPER-LOADING-MECHANISM.md's "the swapper is NOT loaded into ND-500 memory" is DISPROVEN. Do not cite. |

## 7. Open gaps, ranked

1. Per-MSW-code body semantics (offsets 2,3,4,0o10-0o17,0o110,0o112). Next
   move: 60B-076B-ITOSWP.pseudo.c + 510B-CallSwapper.pseudo.c.
2. The single ND-100 instruction copying SWPST into the MON 377B sub-fn-1 OUT
   param at [0x240B0] — open at ANL12:641-647; likely in 030-S3SM5 (reads
   SWPST @164104, issues MON 377 @164106), not the nucleus.
3. 0x223 / 0o1043 — no evidence anywhere.
4. 0o1031 and 0o55 do not resolve uniquely.
5. Full spellings of the 17 truncated MSW names.
6. Whether the swapper's 0o66 is the ABSTR function code (5c) — cheap to test.
7. 030-S3SM5's source is NOT in the repo; grepping NPL-SOURCE for
   swapper-message STORES is a false negative. Everything there can only be
   named by address.

## Reconciliation notes from the ND500UC main session (2026-08-17)

A. **RIOM count table address**: section 0/4d says 0x0802408C, but the cited
   riom operand `$1000440074+` is octal 1000440074 whose low part 0o440074 =
   0x2403C — matching the execution-verified milestone-11 carve (29 x 32-bit
   words at DSEG 0x2403C, ending exactly at the fn cell 0x240B0). The
   0x0802408C figure contradicts its own cite; treat 0x0802403C as correct
   unless the DSEG bytes say otherwise.

B. **fn-cell value 0x223**: the milestone-10 record and the deep-dive mention
   announce fn-cell value 0x223 as observed in the emulator harness. This
   dossier's exhaustive search (4e) found NO SINTRAN source for 547/0o1043 and
   the bound check would reject it. Until re-verified, treat the 0x223
   observation as harness/uninitialised-state origin, not protocol.

---

## ADDENDUM 2026-09-13 — the idx-24 INSTALL message field map (was un-carved)

The idx-24 install command (SWPDECODER install-descriptor) builds a per-PSN segment descriptor
from the relayed SWMSG. The install parameter block was NOT covered by the field table above
(which is fn-3/fn-5). Measured from the CONVERT-DOM output connect (record base 0x240BC = the
riom intake; SWMSG source = ND-100 phys 0x210718; installer routine 1000006134, stores at
1000006253-6306), record offsets (octal, halfwords):

| off (octal) | field | notes |
|---|---|---|
| 0o20 | PSN | idx24.PSN; e.g. psn14 = 0x000E |
| 0o34 | file-first-char | 0x41 'A' / 0x42 'B' — matches FSCNT arg[0] |
| **0o36** | **packed STATE-descriptor word** | written to desc+4; STATE = bits 26-29 (LSB) = `(word>>26)&0xF`. Per-seg measured: 0x8340→0, 0x8180→0, 0xDE00→7, 0xE580→9, **0xEB2C→0xA** |
| 0o40 | (all-zero every install) | NOT the descriptor field — refutes an 0o36-vs-0o40 off-by-one |
| 0o42 | 0x0240 const | |
| 0o0/0o2 | 0xFFFF | constant across installs |
| 0o4 | 0x0006 | constant |
| 0o6 | 0x0001 | constant |
| 0o14 | 0x0005 | constant |
| 0o16 | 0x0018 | constant |

**STATE bit numbering (from ND-05.009.4):** the swapper's `getbf r.4,$32,$4` reads bits 26-29
LSB-numbered; the grow-gate `bi test $1000224744+` treats the permit word as a BYTE-ADDRESSED
BIT ARRAY (a BI operand is byte-addressed, bit 0 = LSB of the addressed byte, `+` post-indexes).
So `0x00E00000` (bytes 00 E0 00 00) permits STATE **{13,14,15}**, not "bits 21-23". The installer's
STATE→attribute tables: `$224744`(grow)→{13,14,15}, `$224754`→{6,7}, `$224760/764`→{0,1,2,3,6,11-15},
`$224770`→{0,1,2,6}.

**Finding:** the fresh CONVERT-DOM output (psn14) carries STATE 0xA verbatim from the ND-100
message; 0xA fails the grow-permit and LALLOPAGE never fires → NO SUCH PAGE. STATE 9 (a source
seg) is also attribute-less yet backs via LNEWSWAP (existing disk page), so STATE alone does not
decide LNEWSWAP-vs-grow — disk backing does. See the ND500UC repo `docs/HANDOFF-2026-09-13.md`.

---

## ADDENDUM 2026-09-13b — CONNECT-FILE (MON 60 fn 13) flow: where STATE is, and is NOT, built

## CONFIRMED 2026-09-14 (measured microcode decode) — the STATE-0xA / {13,14,15} chain in both 2026-09-13 addenda stands

The "fresh output → STATE 0xA → fails grow-permit {13,14,15} → NO SUCH PAGE" chain in the two
addenda below IS measured. (A brief note had called it "unverified" after a census printed rotating
garbage; that census — the functional-lane AppendSwapperFnCells instrument, wrong sample point plus
a mislabeled halfword — was the ONLY broken thing. The STATE-0xA conclusion itself stands.)

1. STATE 0xA for the fresh AccessType-3 output (PSN 14) is decoded from the CORRECT instrument —
   the microcode ALLOCGATE sampling SWMSG@0x080240BC AT the gate (convdom-micro-run.log:10952-10959):
   idx-24 record read big-endian halfword, STATE=(word@0o36>>10)&0xF; PSN 14: 0o20=0x000E,
   0o34=0x0042 ('B'), 0o36=0xEB2C → STATE 0xA. Cross-validated 3 ways (dossier per-seg table
   0x8340→0 / 0xE580→9 / 0xEB2C→0xA; PSN halfword = ALLOCGATE b24; file-char = FSCNT arg[0]).
2. STATE 0xA ∉ grow-permit {13,14,15} (permit word 0x00E00000, byte-addressed bit array) →
   grow-gate declines → allocate 0x0800062F never fires → NO SUCH PAGE. Measured on BOTH ND-500
   lanes (functional + real microcode) = COMMON code, NOT a functional-CPU bug.
3. The PSN-14 output descriptor (DESC@b40=0x08076820) is all-zeros/unbacked — consistent: the SWMSG
   carries STATE 0xA and the page descriptor is unbacked. STATE alone does not decide the outcome;
   disk backing matters too (a source seg with STATE 9 backs via LNEWSWAP because it HAS pages; the
   fresh output has NEITHER backing NOR a growable STATE).
4. NOT terminal: trap 46B, WAIT-parked (no MON 0B exit); SINTRAN re-runs the swapper (104x 3MONCO +
   31x 3TRACO) but never resolves PSN 14.
5. Code caveat (worth checking, not a doubt about the SET): CpuND500.Execute.cs `permitR` uses a
   WORD-SHIFT bit-extraction while 0x00E00000 is byte-addressed = {13,14,15}. The SET {13,14,15} is
   correct; the shift code may pull the wrong bits.
6. ROOT LOCUS (open): why does S3SM5 assign the fresh AccessType-3 output STATE 0xA (non-growable)
   AND leave it unbacked? Fix = pre-backed OR growable STATE {13,14,15}.

Newly mapped from the version-matched NPL source (`SINTRAN/NPL-SOURCE/NPL/5P-P2-MON60.NPL`) plus
the loaded S3FS / S3SM5 Ghidra. This traces WHERE the connect builds the descriptor and STATE,
which the fn-3/fn-5 field table above did not cover.

- **N500M** (MON 60 entry) dispatches via the **5IFUNC** table (pre-monitor param setup), indexed
  by function code.
- **ICONNFI** (func 13, pre-phase): copies the file NAME from user param **5P1** (200 bytes,
  FRUSMOVE) and the file TYPE from user param **5P3** (4 bytes, XFRUSMOVE) into the MON60 buffer.
  For MON 412B FileAsSegment, 5P3 = the AccessType. This is a CROSS-BRIDGE copy of ND-500 user
  memory by ND-100 code.
- **5NOPAR** then does `CALL FPT2ENTRY` = "ENTER ND-500 SYSTEM MONITOR". The actual connect
  (segment descriptor + swapper-message build, carrying STATE) runs in the **ND-500 system monitor
  overlay (S3SM5, address range 0x4000+)** — NOT in the MON60 overlay (0x2C00–0x3B00), and NOT in
  this swapper-message servicer `MP-P2-N500.NPL` (0xB000+, which only RESPONDS to swapper requests
  at runtime: LDATREADY / LALLOPAGE).
- **FCONNFI** (func 13, post-phase): only copies the resulting open-file number back to the user.
  It does **not** build STATE.
- **OFT (open file table), SINTRAN L version:** OPTAB = octal 147515 = 0xCF4D, 2 words/entry;
  per-file pool BPOOL = 0xCFCD. OFT slot+5 = file-type word (Indexed = bit 0o10 = 0x08). An
  env-gated ND-100 OFT-watch instrument now exists in the RetroCore sibling repo
  (`CpuND100.OftWatch.cs`, env `RETROCORE_ND100_OFTWATCH_ADDR`) to watch these OFT / STATE fields.

### Corrected key understanding (we had it wrong)
The STATE VALUE does not by itself decide grow-vs-not. **DISK BACKING decides the page-fault
outcome.** A segment WITH disk pages services the fault via LNEWSWAP regardless of STATE (psn13,
STATE 9, backs fine because it has pages); a FRESH UNBACKED writable segment has nothing to swap in
and MUST take the grow path, which needs STATE {13,14,15}. psn14 (STATE 0xA) fails on both counts:
no backing AND STATE 0xA not grow-permitted. STATE 9 and STATE 0xA are BOTH attribute-less in the
install tables — the tables do NOT separate them. So "STATE 0xA is the bug / just set STATE to
13-15" is too simple; the real question is why the fresh unbacked output is neither pre-backed NOR
given a growable STATE.

### Red herrings / refuted leads (recorded so they are not re-chased)
- **S3FS routine 0x6CA6** is a per-page descriptor loop (its stored value varies across 39 calls),
  NOT the OFT file-type set.
- **The MON60 0x3124 "discriminator"** and the **S3SM5 0xBB6F discriminator**
  (`[struct-0x12] - [[*0x2D]] = 1`) are CONSTANTS inside the STATE-0xA builder, NOT the grow-vs-not
  gate. Verified: the alternate/growable branch never executes; STATE 9 is built by a SEPARATE
  routine at ~0xBCCD. The real gate is the UPSTREAM routing that sends the fresh output to the
  STATE-0xA builder vs the STATE-9 builder — still being traced.

### Tooling caution — carved segments do not byte-align with the live overlays
The carved segment files (`006-S3FS.bin` loaded at 0x2C00, `030-S3SM5.bin` at 0x4000) do NOT
byte-align with the live runtime overlay addresses for all routines. A forced Ghidra disassembly at
the runtime PCs (S3FS 0x3124, S3SM5 0xBB6E) comes out misaligned / garbage, and a byte-search for a
known instruction (e.g. `SAA 0xA` = `f1 0a`) does not land at the traced PC. Verify against a
runtime trace before cross-mapping any static address.

### Grow-permit bit numbering — reaffirmed, and the wrong reading flagged
The permit word `0x00E00000` is a BYTE-ADDRESSED bit array (permitted STATE set = {13,14,15}); the
little-endian word-shift reading ("bits 21-23") is WRONG. The harness `permitR` word-shift model in
the RetroCore file `CpuND500.Execute.cs` reflects that wrong reading and is suspect.

### Status
Root cause is localized (our ND-100/servicer handling of the fresh unbacked output connect;
Ronny's steer is that our forwarding drops the grow-grant) but NOT yet pinned to one line. It is
NOT fixed. Open items: (1) find the upstream STATE-0xA-vs-STATE-9 routing; (2) decide whether the
output should arrive pre-backed or be given a growable STATE (ND-5000 microcode is the ground
truth). See the ND500UC repo `docs/HANDOFF-2026-09-13.md`.

---

## ADDENDUM 2026-09-14 — the CONNECT is the bug (not the program), and the fault-handling phase is faithful

**Root cause, as measured fact.** CONVERT-DOMAIN's `MON 412B` connect of its fresh AccessType-3,
0-page output (logical seg 9 = PSN 14) makes it a NON-GROWABLE segment. The swapper descriptor for
PSN 14 (@0x08038578 = 0x08038000 + 14*0o144) is stamped STATE 0xA, template grow-bit CLEAR
(desc+0o24 = 0x84C0), size 0, no disk backing → non-growable THREE ways (STATE 0xA ∉ {13,14,15};
grow-bit 0x20 clear; unbacked). STATE 0xA is stamped by S3SM5's connect into the connect record
r.36 (SWMSG @0o36); the installer (1000006134) copies it to descriptor+0o4. The swapper TEMPLATE
default STATE = 0 (raw DSEG @0x08023EBC) — so 0xA comes from the CONNECT, not the swapper.
CONVERT-DOMAIN growing a 0-page output by writing through the segment is its INTENDED design
(verified from its disassembly); the output must be growable, so the bug is the CONNECT.

**Fault-handling phase — our emulation is FAITHFUL (these our-side hypotheses are REFUTED, do NOT
record them as bugs).** After the fault the convert WAIT-parks; SINTRAN re-runs the swapper (104×
3MONCO + 31× 3TRACO) but never resolves → parks indefinitely (NOT a terminal MON-exit abort).
Refuted by raw bytes:
- The page-in coupling never holds here (0 hits).
- Our 3MONCO FUNCV/K delivery is faithful — SINTRAN itself sent FUNCV=0 / K=0; our servicer
  delivers other faults' error codes fine (e.g. FUNCV=0x2E where a path DOES error).
- **SWPST=0xA is the MSWPFAULT ACTIVATION reason** (ND-100→swapper direction, per §1d/§2), NOT the
  swapper's error answer. (This reconciles with §5b: SWPST is bidirectional; the 0xA seen here is
  the activation-reason direction, not the error-code direction.)
- SINTRAN's error-restart contract (SWPDECODER / LNEWSWAP, MP-P2-N500 @135443/135470, matching
  §5b): a swapper error answer needs SWPST(0o103) ≠ 0 AND SPFLA(0o143) ≠ 0 → EMONICO restarts with
  the error code (3MONCO delivering FUNCV=code, KFLIP=1); else OK-retry. For PSN 14 SINTRAN takes
  OK-retry (no error answer seen).

**OPEN FORK (NOT settled).** On the declined-non-growable path, does the ND-500 swapper WRITE an
error (SPFLA/SWPST) — in which case, if our emulation does not propagate the SWMSG administration
region (0o101+) to the ND-100 side, that is an our-side unshared-region bug — OR OK-retry without
erroring (→ purely the STATE-0xA-should-be-growable question)? SWPST(0o103)/SPFLA(0o143) live in the
SWMSG administration region (0o101+, §1b), BEYOND the RIOM-copied head (0..0o14). Being measured with
a physical write-watch (ND-100 SWPST at phys 0x420DB6, SPFLA at phys 0x420DC6).

**STATE decode (canonical, tested).** STATE = `(install-record word @0o36 >> 10) & 0xF` (big-endian
halfword); grow-permit byte-addressed array `0x00E00000` = {13,14,15}. Encoded in the RetroCore
sibling repo `SintranSwmsgDecode.cs` with 18 passing tests.
