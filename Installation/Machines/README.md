# Machines: the hardware itself

What box each ND-500 and ND-5000 model came in, how big it is, which cages are inside,
how the cages are linked, and which printed circuit boards go in them.

| File | What it covers |
|---|---|
| [ND500-HW.md](ND500-HW.md) | ND-500 family: cabinets, crates, board sets, ND-520 through ND-570/CX and ND-505 |
| [ND5000-HW.md](ND5000-HW.md) | ND-5000 family: three cabinet generations, Samson and Rallar CPU modules, the octobus |
| [cabinets/](cabinets/README.md) | What the metal actually looks like, cage by cage, with image briefs for making cutaway diagrams |

---

## The three questions these files answer

**Which box?** The ND-500 and the ND-5000 share one large floor-standing shell, the
11-module cabinet '85, 169 x 60 x 91 cm. Smaller machines use the Compact shell at
69 x 54 x 76 cm, or, for the ND-5000 Satellite and Technostation, a long low box on
castors. Sizes come from the product sheets and the site-planning manuals, never from
the assembly drawings, which carry almost no dimensions.

**Which cages?** A cage is a set of boards on one shared backplane. Every coprocessor
machine has at least two, because ND-500 cards are 405 x 277 mm and ND-100 cards are
367 x 277 mm and the two do not mix in one crate.

**How are they linked?** That is the real difference between the families. The ND-500
joins its two halves with a cable between PCB 3022 in the ND-100 crate and PCB 5015 in
the ND-500 crate. The ND-5000 has no such pair: it uses the **octobus**, a serial message
bus, plus mailboxes in shared multifunction-bus memory. The Compact and the ES Model C
do it with neither, bridging both buses on one backwiring through a Double Bus Controller.

---

## Source material

- **Reference manuals** in `../../Reference-Manuals/500/`: the ND-5000 Hardware
  Description ND-05.020, the ND-5000 Hardware Maintenance ND-05.017, the ES Model C
  maintenance manual ND-830102, the Multiport 4 and Multiport 5 manuals, and the ND-500
  course manual with its 1982 card assembly sheets.
- **Product sheets and sales documents** in `../Product-Info/` and `../Sales-Info/`, which
  are where the outer dimensions and the configuration tables live.
- **Norsk Data's production drawing set**, Books 1, 2, 4A and 4B, scanned in the
  sintran.com mirror kept outside this repository. Book 2 is the cabinets. The
  [cabinets/](cabinets/README.md) files are built from those sheets read one by one.
- **`../../Hardware/ND-PHYSICAL-MODELS.md`** for the dimension tables, the conflicts
  between them, and the NORD-1, NORD-10 and NORD-50 figures.

---

**Parent:** [../README.md](../README.md)
