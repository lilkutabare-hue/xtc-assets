"""The XTC logo, traced 1:1 from the brand file (fonts/xtc-logo.svg = potrace of the cross logo):
X on top, X T C across, C below. Letters are extended (~5:1); the pack condenses them to the
longsleeve-print proportion (~1.6-2.2:1) so they read at 24px."""
import os

from shapely import affinity

from . import geo

HERE = os.path.dirname(os.path.abspath(__file__))
_cache = {}


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


def letter(ch, x, y, w, h, bold=0.0):
    """logo letter stretched into a w x h box centred on (x, y); bold = outline growth px."""
    g = glyphs()[ch]
    b = g.bounds
    g = affinity.scale(g, w / (b[2] - b[0]), h / (b[3] - b[1]), origin=(0, 0))
    if bold:
        g = g.buffer(bold, join_style=2, mitre_limit=3)
    b = g.bounds
    return affinity.translate(g, x - (b[0] + b[2]) / 2, y - (b[1] + b[3]) / 2)


def word(s, cx, cy, lh, total_w, bold=0.0, gap=0.3):
    """letters of the logo row in one line: gap in units of lh (logo: 0.3)."""
    n = len(s)
    lw = (total_w - (n - 1) * gap * lh) / n
    parts = []
    for i, ch in enumerate(s):
        x = cx - total_w / 2 + lw / 2 + i * (lw + gap * lh)
        if ch != " ":
            parts.append(letter(ch, x, cy, lw, lh, bold))
    return geo.U(*parts)


def cross(cx=256, cy=256, lh=88, lw=144, gap=27, vgap=40, bold=0.0):
    """the cross logo with the file's layout: X over the T, C under it. Returns {key: (poly, (x, y))}."""
    L = {}
    dx = lw + gap
    for key, ch, x, y in (("xt", "X", cx, cy - lh - vgap), ("xl", "X", cx - dx, cy), ("t", "T", cx, cy),
                          ("cr", "C", cx + dx, cy), ("cb", "C", cx, cy + lh + vgap)):
        L[key] = (letter(ch, x, y, lw, lh, bold), (x, y))
    return L
