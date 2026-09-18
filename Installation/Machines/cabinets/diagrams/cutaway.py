"""
Cutaway engine for the ND cabinet diagrams.

Draws axis-aligned solids in a fixed three-quarter view from the front left and above,
the same view as the reference cutaway illustrations: the front face runs off to the
right, the left side recedes to the left, the top is visible. Each solid can carry
decorations drawn in the local 2D coordinates of any of its three visible faces
(card slots, fans, louvres, bezels, text), which the SVG transform then skews onto
the face.

Units are centimetres throughout. x = width (left to right seen from the front),
y = depth (front to rear), z = height (floor up).

Nothing here knows about Norsk Data. The per-cabinet layouts live in draw_cabinets.py.
"""

import math

# ---------------------------------------------------------------------------------
# Projection
# ---------------------------------------------------------------------------------

# Front axis angle, depth axis angle and depth foreshortening. Chosen by eye to match
# the reference: a broad front face and a steeply receding side.
ALPHA = math.radians(18)
BETA = math.radians(38)
KD = 0.62


class View:
    def __init__(self, scale=6.0):
        self.s = scale

    def p(self, x, y, z):
        """3D point in cm to screen point in px, before the canvas offset."""
        s = self.s
        sx = x * math.cos(ALPHA) * s - y * math.cos(BETA) * KD * s
        sy = -z * s - x * math.sin(ALPHA) * s - y * math.sin(BETA) * KD * s
        return sx, sy

    def vec(self, dx, dy, dz):
        a = self.p(dx, dy, dz)
        b = self.p(0, 0, 0)
        return a[0] - b[0], a[1] - b[1]


# ---------------------------------------------------------------------------------
# Materials: (top, front, side, edge)
# ---------------------------------------------------------------------------------

MAT = {
    "shell":   ("#EDE3CC", "#DCCBA6", "#C8B48E", "#8C7A5A"),
    "shellin": ("#D9C9A6", "#CDB990", "#BCA67C", "#8C7A5A"),
    "brown":   ("#C28A5C", "#AE7449", "#95603B", "#5E3B22"),
    "dark":    ("#4A433D", "#35302B", "#28241F", "#141210"),
    "steel":   ("#E2E5E7", "#CBCFD2", "#B2B7BB", "#6F757A"),
    "galv":    ("#E3E0D0", "#D0CCB8", "#B9B49E", "#77735F"),
    "frame":   ("#D6D0BC", "#BDB59C", "#A69E84", "#6A6450"),
    "pcb":     ("#4E7A45", "#3B6236", "#2F512C", "#1C331A"),
    "copper":  ("#E2A868", "#CD8E50", "#B37840", "#6E4520"),
    "fan":     ("#3A3A3A", "#2C2C2C", "#222222", "#111111"),
    "blue":    ("#A9CBEA", "#8DB6DE", "#779FC6", "#4E7396"),
    "cream":   ("#F4EAD0", "#E9DCB8", "#D8C9A0", "#9C8C66"),
    "black":   ("#3A3A3A", "#262626", "#1C1C1C", "#000000"),
    "filter":  ("#CFCFC6", "#BDBDB2", "#A8A89C", "#6F6F66"),
    "yellow":  ("#EFD46A", "#DDBF4F", "#C6A83E", "#7A6620"),
}

CUT_RED = "#C0392B"

# Cabinet colour schemes by era. Only the outer shell, inner walls and trim change.
# Where each one comes from is written in diagrams/README.md.
PALETTES = {
    # default: neutral beige with brown trim
    "beige": {"shell": ("#EDE3CC", "#DCCBA6", "#C8B48E", "#8C7A5A"),
              "shellin": ("#D9C9A6", "#CDB990", "#BCA67C", "#8C7A5A"),
              "brown": ("#C28A5C", "#AE7449", "#95603B", "#5E3B22")},
    # ND-5000 large cabinet: taupe brown, photo of an ND-5800 at Telemuseet
    "nd5000brown": {"shell": ("#C2A58C", "#AD8F76", "#977A62", "#5E4A38"),
                    "shellin": ("#B19479", "#A0846B", "#8C725C", "#5E4A38"),
                    "brown": ("#9A7A60", "#886A52", "#735945", "#4A392B")},
    # ND-500 era large cabinet: dark brown, ND-560 brochure photograph
    "nd500dark": {"shell": ("#7A5A45", "#664A39", "#553D2F", "#2A1D16"),
                  "shellin": ("#8C6C56", "#7C5E4A", "#6B503F", "#2A1D16"),
                  "brown": ("#4A352A", "#3F2D23", "#34251D", "#1E1510")},
    # Compact: greyer light-brown sides, red-brown front fascia, measured from
    # the compact-wedge photograph (Hardware/ND-PHYSICAL-MODELS.md)
    "compact": {"shell": ("#D2C2AE", "#C2AF98", "#AF9B84", "#6E5E4C"),
                "shellin": ("#C4B29C", "#B5A28B", "#A38F79", "#6E5E4C"),
                "brown": ("#B3775A", "#A06A4F", "#8B5B43", "#55362A")},
    # ES era and Technostation: light warm grey, Technostation brochure photograph
    "grey": {"shell": ("#E9E7E1", "#DAD7D0", "#C9C5BC", "#8A867C"),
             "shellin": ("#D5D2CA", "#C7C3BA", "#B6B2A8", "#8A867C"),
             "brown": ("#BFBBB2", "#B0ACA2", "#A09B91", "#6E6A62")},
}


def set_palette(name):
    """Switch the shell colours for the drawings built after this call."""
    MAT.update(PALETTES[name])


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------------
# Faces
# ---------------------------------------------------------------------------------

class Face:
    """A planar rectangle with a local (u, v) frame. u along its width, v upward."""

    def __init__(self, view, origin, uvec, vvec, w, h):
        self.view = view
        self.o3 = origin
        self.u3 = uvec
        self.v3 = vvec
        self.w = w
        self.h = h

    def pt(self, u, v):
        x = self.o3[0] + u * self.u3[0] + v * self.v3[0]
        y = self.o3[1] + u * self.u3[1] + v * self.v3[1]
        z = self.o3[2] + u * self.u3[2] + v * self.v3[2]
        return self.view.p(x, y, z)

    def matrix(self, ox, oy):
        """SVG matrix mapping local (u, v) with v up to screen, with canvas offset."""
        U = self.view.vec(*self.u3)
        V = self.view.vec(*self.v3)
        O = self.view.p(*self.o3)
        return "matrix(%.4f,%.4f,%.4f,%.4f,%.2f,%.2f)" % (
            U[0], U[1], V[0], V[1], O[0] + ox, O[1] + oy)

    def text_matrix(self, u, v, ox, oy):
        """Matrix for upright text whose baseline starts at local (u, v).
        On a side face the local u axis runs right-to-left on screen, so the text
        axis is flipped there and the caller swaps the text anchor (see label)."""
        U = self.view.vec(*self.u3)
        if getattr(self, "mirror", False):
            U = (-U[0], -U[1])
        V = self.view.vec(*self.v3)
        P = self.pt(u, v)
        return "matrix(%.4f,%.4f,%.4f,%.4f,%.2f,%.2f)" % (
            U[0], U[1], -V[0], -V[1], P[0] + ox, P[1] + oy)

    def poly(self, ox, oy):
        pts = [self.pt(0, 0), self.pt(self.w, 0), self.pt(self.w, self.h), self.pt(0, self.h)]
        return " ".join("%.2f,%.2f" % (a + ox, b + oy) for a, b in pts)


# ---------------------------------------------------------------------------------
# Solids
# ---------------------------------------------------------------------------------

class Box:
    """Axis-aligned solid. Decorations are lists of callables deco(face) -> svg in
    local coordinates. front = the y=y0 face, side = the x=x0 face, top = z=z1."""

    def __init__(self, x0, y0, z0, x1, y1, z1, mat="steel", front=None, side=None,
                 top=None, faces="fst", edge=True, opacity=1.0):
        self.x0, self.y0, self.z0 = min(x0, x1), min(y0, y1), min(z0, z1)
        self.x1, self.y1, self.z1 = max(x0, x1), max(y0, y1), max(z0, z1)
        self.mat = MAT[mat] if isinstance(mat, str) else mat
        self.deco = {"f": front or [], "s": side or [], "t": top or []}
        self.faces = faces
        self.edge = edge
        self.opacity = opacity

    def face(self, view, which):
        if which == "f":
            return Face(view, (self.x0, self.y0, self.z0), (1, 0, 0), (0, 0, 1),
                        self.x1 - self.x0, self.z1 - self.z0)
        if which == "s":
            # Seen from outside (x < x0); u runs rearward along y.
            fc = Face(view, (self.x0, self.y0, self.z0), (0, 1, 0), (0, 0, 1),
                      self.y1 - self.y0, self.z1 - self.z0)
            fc.mirror = True
            return fc
        return Face(view, (self.x0, self.y0, self.z1), (1, 0, 0), (0, 1, 0),
                    self.x1 - self.x0, self.y1 - self.y0)

    def svg(self, view, ox, oy):
        out = []
        fill = {"t": self.mat[0], "f": self.mat[1], "s": self.mat[2]}
        # Side first, then front, then top, so the top edge reads cleanly.
        for which in ("s", "f", "t"):
            if which not in self.faces:
                continue
            fc = self.face(view, which)
            if fc.w <= 0 or fc.h <= 0:
                continue
            stroke = self.mat[3] if self.edge else "none"
            out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.8" '
                       'stroke-linejoin="round"%s/>' % (
                           fc.poly(ox, oy), fill[which], stroke,
                           '' if self.opacity == 1 else ' opacity="%.2f"' % self.opacity))
            if self.deco[which]:
                out.append('<g transform="%s">' % fc.matrix(ox, oy))
                for d in self.deco[which]:
                    s = d(fc)
                    if s:
                        out.append(s)
                out.append("</g>")
                # Text decorations need their own upright matrix.
                for d in self.deco[which]:
                    t = getattr(d, "text", None)
                    if t:
                        out.append(t(fc, ox, oy))
        return "\n".join(out)

    def screen_bbox(self, view):
        xs, ys = [], []
        for x in (self.x0, self.x1):
            for y in (self.y0, self.y1):
                for z in (self.z0, self.z1):
                    a, b = view.p(x, y, z)
                    xs.append(a)
                    ys.append(b)
        return min(xs), min(ys), max(xs), max(ys)


class Raw:
    """Free SVG drawn at a painter position given by an invisible box."""

    def __init__(self, box, fn):
        self.x0, self.y0, self.z0 = box[0], box[1], box[2]
        self.x1, self.y1, self.z1 = box[3], box[4], box[5]
        self.fn = fn

    def svg(self, view, ox, oy):
        return self.fn(view, ox, oy)

    def screen_bbox(self, view):
        return Box.screen_bbox(self, view)


# ---------------------------------------------------------------------------------
# Painter ordering
# ---------------------------------------------------------------------------------

def _behind(a, b, eps=0.01):
    """True when a must be painted before b."""
    if a.x0 >= b.x1 - eps:
        return True
    if a.y0 >= b.y1 - eps:
        return True
    if a.z1 <= b.z0 + eps:
        return True
    return False


def paint_order(items, view):
    n = len(items)
    bb = [it.screen_bbox(view) for it in items]
    after = [set() for _ in range(n)]
    indeg = [0] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if bb[i][2] < bb[j][0] or bb[j][2] < bb[i][0] or bb[i][3] < bb[j][1] or bb[j][3] < bb[i][1]:
                continue
            ij = _behind(items[i], items[j])
            ji = _behind(items[j], items[i])
            if ij and not ji:
                if j not in after[i]:
                    after[i].add(j)
                    indeg[j] += 1

    def key(k):
        it = items[k]
        return -((it.x0 + it.x1) * 0.5 + (it.y0 + it.y1) * 0.5), (it.z0 + it.z1) * 0.5

    ready = sorted([k for k in range(n) if indeg[k] == 0], key=key)
    order = []
    while ready:
        k = ready.pop(0)
        order.append(k)
        for j in after[k]:
            indeg[j] -= 1
            if indeg[j] == 0:
                ready.append(j)
        ready.sort(key=key)
    if len(order) < n:  # cycle: fall back for the rest
        rest = sorted([k for k in range(n) if k not in order], key=key)
        order += rest
    return [items[k] for k in order]


# ---------------------------------------------------------------------------------
# Decorations. Each returns a callable deco(face) -> svg in local coords (v up).
# ---------------------------------------------------------------------------------

def rect(u, v, w, h, fill, stroke="none", sw=0.1, rx=0, opacity=1):
    def d(fc):
        return '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="%.3f" fill="%s" stroke="%s" stroke-width="%.3f" opacity="%.2f"/>' % (
            u, v, w, h, rx, fill, stroke, sw, opacity)
    return d


def card_slots(n, u0, u1, v0, v1, numbered=True, fill_pattern=None, groups=None):
    """Front view of a card crate: n vertical card edges between u0 and u1.
    fill_pattern: function(i) -> 'card' | 'empty' | 'cpu' | 'narrow' | colour tuple."""
    pitch = (u1 - u0) / n

    def d(fc):
        out = ['<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#1d1a17"/>' % (
            u0, v0, u1 - u0, v1 - v0)]
        # guide combs top and bottom
        for vv in (v0, v1 - 0.9):
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="0.9" fill="#8f8a7c"/>' % (u0, vv, u1 - u0))
        for i in range(n):
            kind = fill_pattern(i) if fill_pattern else "card"
            x = u0 + i * pitch
            if kind == "empty":
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#2a2622"/>' % (
                    x + pitch * 0.42, v0 + 0.9, pitch * 0.16, v1 - v0 - 1.8))
                continue
            col = {"card": "#3B6236", "cpu": "#2F5E57", "ram": "#46603A", "blue": "#3C5B7A",
                   "narrow": "#6B6B5F", "gold": "#5C6E35"}.get(kind, kind if isinstance(kind, str) else "#3B6236")
            wfrac = 0.55 if kind != "cpu" else 0.8
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s" stroke="#16230f" stroke-width="0.06"/>' % (
                x + pitch * (1 - wfrac) / 2, v0 + 0.9, pitch * wfrac, v1 - v0 - 1.8, col))
            # small chips on the edge
            for k in range(3):
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#b8a15a" opacity="0.7"/>' % (
                    x + pitch * 0.45, v0 + (v1 - v0) * (0.28 + 0.2 * k), pitch * 0.1, 0.5))
            # cream ejectors top and bottom
            for vv in (v0 + 0.9, v1 - 3.1):
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="2.2" rx="0.25" fill="#EFE3C2" stroke="#9c8c66" stroke-width="0.06"/>' % (
                    x + pitch * 0.22, vv, pitch * 0.56))
        return "\n".join(out)

    def t(fc, ox, oy):
        if not numbered:
            return ""
        out = []
        size = min(1.4, pitch * 0.75)
        for i in range(n):
            u = u0 + (i + 0.5) * pitch - size * 0.28 * len(str(i + 1))
            out.append('<text transform="%s" font-family="Arial" font-size="%.2f" fill="#2b2520">%d</text>' % (
                fc.text_matrix(u, v1 + 0.4, ox, oy), size, i + 1))
        return "\n".join(out)

    d.text = t
    return d


def side_slots(n, u0, u1, v0, v1, fill_pattern=None, numbered=True):
    """Card crate seen from its side face: same drawing, u runs rearward."""
    return card_slots(n, u0, u1, v0, v1, numbered=numbered, fill_pattern=fill_pattern)


def samson_edge(u0, u1, v0, v1):
    """Front edge of a Samson CPU assembly, as in the photographs of 320001-320003:
    the mother board edge with yellow handles and a column of LEDs, and the baby
    modules stacked beside it in layers, their chip rows seen edge on."""
    def d(fc):
        w = u1 - u0
        h = v1 - v0
        out = ['<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#1d1a17"/>' % (u0, v0, w, h)]
        mb = w * 0.18
        # mother board edge with its handles and LEDs
        out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#3B6236"/>' % (u0 + 0.1, v0 + 0.3, mb, h - 0.6))
        for vv in (v0 + 0.3, v1 - 4.3):
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="4.0" rx="0.3" fill="#D9B24A" stroke="#7a5f1c" stroke-width="0.08"/>' % (
                u0, vv, mb + 0.4))
        leds = ["#f2c230", "#4fc36b", "#f2c230", "#e0402f", "#4fc36b", "#e0402f", "#f2c230"]
        for k, c in enumerate(leds):
            out.append('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="%s"/>' % (u0 + mb * 0.55, v0 + h * (0.35 + k * 0.055), mb * 0.22, c))
        # baby module layers, each a board with chip rows and a grey connector strip
        layers = 3
        lw = (w - mb - 0.6) / layers
        for L in range(layers):
            x = u0 + mb + 0.4 + L * lw
            for seg in range(3):
                y0 = v0 + 0.8 + seg * (h - 1.6) / 3
                sh = (h - 1.6) / 3 - 0.5
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#2f5a36" stroke="#16230f" stroke-width="0.06"/>' % (
                    x + lw * 0.55, y0, lw * 0.22, sh))
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#cfcac0"/>' % (
                    x + lw * 0.1, y0, lw * 0.35, sh))
                for c in range(4):
                    out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#141414"/>' % (
                        x + lw * 0.77, y0 + 0.4 + c * (sh - 0.8) / 4, lw * 0.18, (sh - 0.8) / 4 * 0.7))
        return "\n".join(out)
    return d


def fans(rows, cols, u0, u1, v0, v1, rmul=0.42, stagger=False):
    def d(fc):
        out = []
        cw = (u1 - u0) / cols
        ch = (v1 - v0) / rows
        r = min(cw, ch) * rmul
        for rr in range(rows):
            nc = cols if not (stagger and rr % 2) else cols - 1
            offs = 0 if not (stagger and rr % 2) else cw / 2
            for cc in range(nc):
                cx = u0 + offs + (cc + 0.5) * cw
                cy = v0 + (rr + 0.5) * ch
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#5b5750" stroke="#2a2825" stroke-width="0.08"/>' % (
                    cx - r * 1.12, cy - r * 1.12, r * 2.24, r * 2.24))
                out.append('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#1b1b1b"/>' % (cx, cy, r))
                for k in range(5):
                    a = k * 72
                    out.append('<ellipse cx="%.3f" cy="%.3f" rx="%.3f" ry="%.3f" fill="#3d3d3d" transform="rotate(%d %.3f %.3f)"/>' % (
                        cx + r * 0.48, cy, r * 0.46, r * 0.2, a, cx, cy))
                out.append('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#d9d4c4"/>' % (cx, cy, r * 0.22))
        return "\n".join(out)
    return d


def louvres(n, u0, u1, v0, v1, colour="#2a2420"):
    def d(fc):
        out = []
        step = (v1 - v0) / n
        for i in range(n):
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="%.3f" fill="%s"/>' % (
                u0, v0 + i * step + step * 0.25, u1 - u0, step * 0.45, step * 0.2, colour))
        return "\n".join(out)
    return d


def fins(n, u0, u1, v0, v1, colour="#7a7f84"):
    def d(fc):
        step = (u1 - u0) / n
        return "\n".join('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>' % (
            u0 + i * step + step * 0.3, v0, step * 0.4, v1 - v0, colour) for i in range(n))
    return d


def dots(cols, rows, u0, u1, v0, v1, r=0.25, colour="#2a2622"):
    def d(fc):
        out = []
        for i in range(cols):
            for j in range(rows):
                out.append('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="%s"/>' % (
                    u0 + (i + 0.5) * (u1 - u0) / cols, v0 + (j + 0.5) * (v1 - v0) / rows, r, colour))
        return "\n".join(out)
    return d


def dsub_rows(u0, u1, v0, v1, rows, per_row, colour="#2c2c2c"):
    """Rows of long multiway D-connectors, as on a plug panel."""
    def d(fc):
        out = []
        rh = (v1 - v0) / rows
        cw = (u1 - u0) / per_row
        for r in range(rows):
            for c in range(per_row):
                x = u0 + c * cw + cw * 0.12
                y = v0 + r * rh + rh * 0.25
                w = cw * 0.76
                h = rh * 0.5
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="%.3f" fill="#8b8f93" stroke="#44484b" stroke-width="0.08"/>' % (
                    x, y, w, h, h * 0.35))
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="%.3f" fill="%s"/>' % (
                    x + w * 0.08, y + h * 0.22, w * 0.84, h * 0.56, h * 0.25, colour))
        return "\n".join(out)
    return d


def floppy(u, v, w, h):
    def d(fc):
        return "\n".join([
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="0.3" fill="#1f1d1b" stroke="#000" stroke-width="0.08"/>' % (u, v, w, h),
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#050505"/>' % (u + w * 0.12, v + h * 0.45, w * 0.62, h * 0.12),
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#6d6a64"/>' % (u + w * 0.76, v + h * 0.28, w * 0.1, h * 0.46),
            '<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#4fd36b"/>' % (u + w * 0.08, v + h * 0.25, h * 0.07),
        ])
    return d


def streamer(u, v, w, h):
    def d(fc):
        return "\n".join([
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="0.3" fill="#262422" stroke="#000" stroke-width="0.08"/>' % (u, v, w, h),
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="0.2" fill="#0a0a0a"/>' % (u + w * 0.2, v + h * 0.35, w * 0.6, h * 0.3),
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#777"/>' % (u + w * 0.08, v + h * 0.4, w * 0.06, h * 0.2),
        ])
    return d


def disk_front(u, v, w, h):
    def d(fc):
        return "\n".join([
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="0.3" fill="#2d2b28" stroke="#000" stroke-width="0.08"/>' % (u, v, w, h),
            '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#3a3834"/>' % (u + w * 0.1, v + h * 0.4, w * 0.8, h * 0.2),
            '<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#e44b3a"/>' % (u + w * 0.12, v + h * 0.2, min(w, h) * 0.05),
        ])
    return d


def op_panel(u, v, w, h, buttons=8, display=True, key=True):
    def d(fc):
        out = ['<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="0.3" fill="#2e2a26" stroke="#000" stroke-width="0.08"/>' % (u, v, w, h)]
        x = u + w * 0.04
        if display:
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#90a38a" stroke="#1a1a1a" stroke-width="0.06"/>' % (
                x, v + h * 0.2, w * 0.3, h * 0.55))
            x += w * 0.34
        bw = (w * 0.5) / buttons
        for i in range(buttons):
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" rx="0.1" fill="#4a4540" stroke="#1a1a1a" stroke-width="0.05"/>' % (
                x + i * bw + bw * 0.1, v + h * 0.25, bw * 0.8, h * 0.5))
            if i in (0, 2):
                out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#e0402f"/>' % (
                    x + i * bw + bw * 0.25, v + h * 0.8, bw * 0.5, h * 0.08))
        if key:
            kx = u + w * 0.93
            out.append('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#b8b2a4" stroke="#222" stroke-width="0.08"/>' % (kx, v + h / 2, h * 0.28))
            out.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="#222"/>' % (kx - h * 0.04, v + h * 0.32, h * 0.08, h * 0.36))
        return "\n".join(out)
    return d


def label(u, v, text, size=1.2, colour="#1e1b18", weight="normal", anchor="start"):
    def d(fc):
        return ""

    def t(fc, ox, oy):
        a = anchor
        if getattr(fc, "mirror", False):
            # u given is the front end of the text; it reads rearward-to-front on screen
            a = {"start": "end", "end": "start"}.get(anchor, anchor)
        return '<text transform="%s" font-family="Arial" font-size="%.2f" font-weight="%s" fill="%s" text-anchor="%s">%s</text>' % (
            fc.text_matrix(u, v, ox, oy), size, weight, colour, a, esc(text))
    d.text = t
    return d


def holes_column(u, v0, v1, n=66):
    def d(fc):
        step = (v1 - v0) / (n - 1)
        return "\n".join('<circle cx="%.3f" cy="%.3f" r="0.28" fill="#5a5446"/>' % (u, v0 + i * step) for i in range(n))
    return d


def hatch(u0, u1, v0, v1, colour="#8f8a7c", n=12):
    def d(fc):
        step = (u1 - u0) / n
        return "\n".join('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>' % (
            u0 + i * step, v0, step * 0.35, v1 - v0, colour) for i in range(n))
    return d


# ---------------------------------------------------------------------------------
# Drawing: solids, cut edges, labels
# ---------------------------------------------------------------------------------

class Drawing:
    def __init__(self, title, subtitle="", scale=6.0):
        self.view = View(scale)
        self.items = []
        self.overlay = []     # raw svg drawn after the solids, in 3D-point form
        self.labels = []
        self.title = title
        self.subtitle = subtitle
        self.notes = []

    def add(self, item):
        self.items.append(item)
        return item

    def cut_line(self, pts3):
        """A red cut edge along a 3D polyline, drawn above the solids."""
        self.overlay.append(("cut", pts3))

    def line3(self, pts3, colour, width=2.0, dash=None):
        self.overlay.append(("line", pts3, colour, width, dash))

    def callout(self, text, p3, side="auto"):
        self.labels.append((text.replace('|', chr(10)), p3, side))

    def note(self, text):
        self.notes.append(text)

    # -----------------------------------------------------------------------------

    def render(self, path_svg, width=1800):
        v = self.view
        # geometry bbox
        xs, ys = [], []
        for it in self.items:
            b = it.screen_bbox(v)
            xs += [b[0], b[2]]
            ys += [b[1], b[3]]
        gx0, gy0, gx1, gy1 = min(xs), min(ys), max(xs), max(ys)
        gw = gx1 - gx0
        label_col = 360
        top_pad = 120
        bottom_pad = 60 + 26 * len(self.notes)
        W = max(width, int(gw + 2 * label_col + 80))
        H = int(gy1 - gy0 + top_pad + bottom_pad)
        ox = (W - gw) / 2 - gx0
        oy = top_pad - gy0

        out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H),
               '<rect width="100%" height="100%" fill="#ffffff"/>',
               '<defs><filter id="soft" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-opacity="0.18"/></filter></defs>',
               '<text x="%d" y="62" font-family="Arial" font-size="46" font-weight="bold" text-anchor="middle" fill="#1b1714">%s</text>' % (W / 2, esc(self.title))]
        if self.subtitle:
            out.append('<text x="%d" y="98" font-family="Arial" font-size="22" text-anchor="middle" fill="#4b433b">%s</text>' % (W / 2, esc(self.subtitle)))

        out.append('<g filter="url(#soft)">')
        for it in paint_order(self.items, v):
            out.append(it.svg(v, ox, oy))
        out.append("</g>")

        for ov in self.overlay:
            if ov[0] == "cut":
                pts = " ".join("%.1f,%.1f" % (a + ox, b + oy) for a, b in (v.p(*q) for q in ov[1]))
                out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>' % (pts, CUT_RED))
            else:
                _, pts3, col, wd, dash = ov
                pts = " ".join("%.1f,%.1f" % (a + ox, b + oy) for a, b in (v.p(*q) for q in pts3))
                out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round" stroke-linecap="round"%s/>' % (
                    pts, col, wd, ' stroke-dasharray="%s"' % dash if dash else ""))

        out.append(self._labels(W, H, ox, oy, top_pad, bottom_pad))

        y = H - bottom_pad + 34
        for n in self.notes:
            out.append('<text x="40" y="%d" font-family="Arial" font-size="17" fill="#5a524a">%s</text>' % (y, esc(n)))
            y += 26
        out.append("</svg>")
        svg = "\n".join(out)
        with open(path_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        return svg

    def _labels(self, W, H, ox, oy, top_pad, bottom_pad):
        """Callouts in two columns. A label goes on the side its anchor sits on,
        measured against the cabinet's front-left vertical edge, unless forced."""
        v = self.view
        out = []
        fs = 23
        divider = v.p(0, 0, 0)[0] + ox
        cols = {"L": [], "R": []}
        for text, p3, sd in self.labels:
            a, b = v.p(*p3)
            ax, ay = a + ox, b + oy
            side = sd if sd in ("L!", "R!") else ("L" if ax < divider else "R")
            cols[side[0]].append([text, ax, ay])
        for side, group in cols.items():
            group.sort(key=lambda g: g[2])
            heights = [len(g[0].split("\n")) * fs * 1.12 + 16 for g in group]
            lo, hi = top_pad + 10, H - bottom_pad - 10
            ys = [g[2] for g in group]
            for _ in range(400):
                moved = False
                for i in range(1, len(ys)):
                    need = (heights[i - 1] + heights[i]) / 2
                    if ys[i] - ys[i - 1] < need:
                        dlt = (need - (ys[i] - ys[i - 1])) / 2
                        ys[i - 1] -= dlt
                        ys[i] += dlt
                        moved = True
                for i in range(len(ys)):
                    ys[i] = min(max(ys[i], lo + heights[i] / 2), hi - heights[i] / 2)
                if not moved:
                    break
            for g, yy in zip(group, ys):
                text, ax, ay = g
                lines = text.split("\n")
                width_est = max(len(l) for l in lines) * fs * 0.55
                if side == "L":
                    tx, anchor = 32, "start"
                    lx = tx + width_est + 12
                    kx = min(lx + 20, ax - 8)
                    lx = min(lx, kx)
                else:
                    tx, anchor = W - 32, "end"
                    lx = tx - width_est - 12
                    kx = max(lx - 20, ax + 8)
                    lx = max(lx, kx)
                n = len(lines)
                y_first = yy - (n - 1) * fs * 1.12 / 2 + fs * 0.35
                out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="#141210" stroke-width="2"/>' % (
                    lx, yy, kx, yy, ax, ay))
                out.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="#141210" stroke="#fff" stroke-width="1.5"/>' % (ax, ay))
                for k, l in enumerate(lines):
                    yl = y_first + k * fs * 1.12
                    out.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="%d" text-anchor="%s" fill="#ffffff" '
                               'stroke="#ffffff" stroke-width="7" stroke-linejoin="round">%s</text>' % (tx, yl, fs, anchor, esc(l)))
                    out.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="%d" text-anchor="%s" fill="#141210">%s</text>' % (
                        tx, yl, fs, anchor, esc(l)))
        return "\n".join(out)
