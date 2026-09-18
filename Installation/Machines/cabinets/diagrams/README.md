# Cutaway diagrams of the ND cabinets

Educational cutaway drawings, one per cabinet, in the style of a period service manual:
a three-quarter view from the front left, the side and top cut away along a red edge,
every named part on a leader line.

| Drawing | Cabinet | Built from |
|---|---|---|
| [nd500-one-cabinet.png](nd500-one-cabinet.png) | ND-500 in one cabinet, model 11 | Book 2 chapter 12 |
| [nd500-two-cabinet.png](nd500-two-cabinet.png) | ND-500 in two cabinets, model 12 | Book 2 chapters 14 and 15 |
| [nd5000-large.png](nd5000-large.png) | ND-5000 large cabinet | Book 2 chapters 16 and 17 |
| [nd5000-compact.png](nd5000-compact.png) | ND-5000 Compact (COMSON) | Book 2 chapter 8, ND-05.017 figure 3 |
| [nd5000-es-model-c.png](nd5000-es-model-c.png) | ND-5000 ES Model C | ND-830102 figures 15 and 16 |
| [nd5000-satellite-technostation.png](nd5000-satellite-technostation.png) | ND-5000 Satellite and Technostation | Book 2 chapter 20 |

Each PNG has an SVG beside it with the same name, which scales without loss.

The facts behind every drawing are in the matching file one folder up, for example
[../ND-5000-LARGE.md](../ND-5000-LARGE.md).

---

## What is drawn from evidence, and what is not

**From the drawings.** The stack order, which unit sits at the front or rear, and the
height of each unit, taken from the nutclip hole numbers on ND's Book 2 sheets. The
number of card positions in each crate. Which boards sit in which positions, from the
maintenance manuals. The part names on the labels.

**From the product sheets.** Outer height, width and depth.

**Schematic, not measured.**

- The depth of each unit front to back, where no drawing gives one.
- The exact spacing of the hole grid, spread evenly over the inside height.
- Which occupied card positions are shown filled in a crate. The patterns are
  illustrative of one configuration.
- The Satellite and Technostation absolute size. Its proportions, 1 : 2.4 : 3.4, are
  measured off drawing 20066, but no dimension exists for that box anywhere.
- **Colour.** No drawing states one, so each drawing takes the colour of its era from
  a photograph, and says which in its caption:

  | Drawing | Colour | Evidence |
  |---|---|---|
  | ND-500 one and two cabinet | dark brown | ND-560 brochure photograph, Norsk Data photo archive on the NAS |
  | ND-5000 large | taupe brown | photograph of an ND-5800 at Telemuseet; ND-SID001 calls it a "brown/beige cabinet" |
  | ND-5000 Compact | red-brown front, greyer brown sides | measured from `Pictures/ronny/compact-wedge.jpg`, see `Hardware/ND-PHYSICAL-MODELS.md` |
  | ES Model C | Compact colours, not confirmed | no photograph of the new ES front cover |
  | Satellite and Technostation | light warm grey | Technostation brochure photograph |

  A later large cabinet, the tpServer in `Pictures/ronny/tp-server-side.png`, is light grey,
  so the grey belongs to the ES era, not to the 1987 ND-5000.
- **Samson CPU edge** in the ND-5000 large drawing follows the photographs of assembly
  320003 in the PCB archive: yellow handles, a column of LEDs, baby modules in layers.

Where one of these matters to a drawing, the drawing's own caption says so.

---

## How to rebuild

The drawings are generated, not hand-drawn, so a correction is a one-line change.

```
python draw_cabinets.py                  (all six)
python draw_cabinets.py nd5000-large     (one)
```

Needs Python 3 and the `cairosvg` package for the PNG output. Without `cairosvg` only the
SVG files are written.

| File | What it is |
|---|---|
| `cutaway.py` | The drawing engine: projection, shaded solids, face decorations such as card slots, fans, louvres and bezels, painter ordering, and callout layout. Knows nothing about Norsk Data |
| `draw_cabinets.py` | One function per cabinet. Positions are written as nutclip hole numbers where the drawings give them, so each line can be checked against its Book 2 sheet |

Rules the layout code follows:

- A callout points only at a part that is visible in that view. A part hidden behind
  another is either left unlabelled or drawn as a dashed line, the usual technical
  drawing convention for hidden detail.
- A label goes on the side of the picture its anchor sits on.
- Callout text uses `|` for a line break, so the layout file never needs a backslash.

---

*Index: [../README.md](../README.md)*
