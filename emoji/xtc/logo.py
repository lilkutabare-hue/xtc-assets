"""The XTC logo, traced 1:1 from the brand file (fonts/xtc-logo.svg = potrace of the cross logo):
X on top, X T C across, C below. Letters are extended (~5:1); the pack condenses them to the
longsleeve-print proportion (~1.6-2.2:1) so they read at 24px."""
import os

from shapely import affinity

from . import geo

HERE = os.path.dirname(os.path.abspath(__file__))
_cache = {}
# ONE typography for the whole pack: the longsleeve print condenses the logo to ~2.8:1 per letter
# (measured on products/night-longsleeve/01: word 9.1:1); 2.2:1 keeps that look and stays readable at
# 24px on a 512 canvas. Every letter in the pack has this aspect and this weight, whatever box it gets.
ASPECT = 2.2
BOLD = 3.0


def glyphs():
    """{'X': poly, 'T': poly, 'C': poly} normalised to bbox origin (0, 0)."""
    if _cache:
        return _cache
    g = geo.svg(os.path.join(HERE, "..", "fonts", "xtc-logo.svg"))
    polys = sorted(geo._polys(g), key=lambda p: (round(p.bounds[1] / 100), p.bounds[0]))
    # row (middle y): X, T, C left to right
    row = sorted([p for p in polys if 900 < p.centroid.y < 1100], key=lambda p: p.bounds[0])
    for ch, p in zip("XTC", row):
        b = p.bounds
        _cache[ch] = affinity.translate(p, -b[0], -b[1])
    return _cache


def letter(ch, x, y, w, h, bold=None):
    """logo letter centred on (x, y), as large as fits a w x h box at the pack's fixed ASPECT and
    weight (the box is a limit, never a stretch: one font everywhere)."""
    g = glyphs()[ch]
    b = g.bounds
    lh = min(h, w / ASPECT)
    lw = lh * ASPECT
    g = affinity.scale(g, lw / (b[2] - b[0]), lh / (b[3] - b[1]), origin=(0, 0))
    g = g.buffer(BOLD if bold is None else bold, join_style=2, mitre_limit=2.5)
    b = g.bounds
    return affinity.translate(g, x - (b[0] + b[2]) / 2, y - (b[1] + b[3]) / 2)


def word(s, cx, cy, lh, total_w, bold=None, gap=0.3):
    """letters of the logo row in one line: gap in units of lh (logo: 0.3). lh and total_w are
    limits; the word takes the largest size that fits both at the fixed ASPECT."""
    n = len(s)
    lh = min(lh, total_w / (n * ASPECT + (n - 1) * gap))
    lw = lh * ASPECT
    total_w = n * lw + (n - 1) * gap * lh
    parts = []
    for i, ch in enumerate(s):
        x = cx - total_w / 2 + lw / 2 + i * (lw + gap * lh)
        if ch != " ":
            parts.append(letter(ch, x, cy, lw, lh, bold))
    return geo.U(*parts)


def cross(cx=256, cy=256, lh=88, lw=None, gap=None, vgap=None, bold=None, width=480):
    """the cross logo with the file's layout (X over the T, C under it) at the fixed ASPECT; the row
    is limited to `width`. Returns {key: (poly, (x, y))}."""
    L = {}
    lh = min(lh, width / (3 * ASPECT + 0.6))
    lw = lh * ASPECT
    gap = 0.3 * lh if gap is None else gap
    vgap = 0.45 * lh if vgap is None else vgap
    dx = lw + gap
    for key, ch, x, y in (("xt", "X", cx, cy - lh - vgap), ("xl", "X", cx - dx, cy), ("t", "T", cx, cy),
                          ("cr", "C", cx + dx, cy), ("cb", "C", cx, cy + lh + vgap)):
        L[key] = (letter(ch, x, y, lw, lh, bold), (x, y))
    return L
