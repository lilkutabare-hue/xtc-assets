"""Geometry for the pack: shapely in, Lottie paths out. All coordinates are canvas px (512x512)."""
import math
import os
import random

from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from . import lot

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")

# pack-wide weights (px on 512): one optical weight for the whole set
W = 46       # main brush stroke
W2 = 34      # secondary stroke
WMIN = 28    # minimum detail


def U(*gs):
    return unary_union([g for g in gs if g is not None and not g.is_empty])


def disc(x, y, r, res=16):
    return Point(x, y).buffer(r, quad_segs=res)


def ellipse(x, y, rx, ry, res=16):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, quad_segs=res), rx, ry, origin=(0, 0)), x, y)


def ring(x, y, ro, ri, res=16):
    return disc(x, y, ro, res).difference(disc(x, y, ri, res))


def rect(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def rrect(x0, y0, x1, y1, r):
    r = min(r, abs(x1 - x0) / 2 - 0.01, abs(y1 - y0) / 2 - 0.01)
    return rect(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=8)


def poly(pts):
    return Polygon(pts).buffer(0)


def line(pts, w=W, cap="round", join="round"):
    caps = {"round": 1, "flat": 2, "square": 3}
    joins = {"round": 1, "mitre": 2, "bevel": 3}
    return LineString(pts).buffer(w / 2, cap_style=caps[cap], join_style=joins[join], quad_segs=8)


def bezier(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def quad(p0, p1, p2, n=20):
    return bezier(p0, (p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1])),
                  (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1])), p2, n)


def spline(pts, n=10, closed=False):
    """Catmull-Rom through pts."""
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    if not closed:
        out.append(tuple(pts[-1]))
    return out


def arc(x, y, r, a0, a1, n=None):
    """points on a circle, angles in degrees, 0 = right, 90 = down (screen)."""
    n = n or max(6, int(abs(a1 - a0) / 6))
    return [(x + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), y + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def brush(pts, w=W, taper=(0.55, 0.7), smooth=True, n=8):
    """Ink stroke: width swells in the middle and tapers to round ends (brush feel)."""
    if smooth and len(pts) > 2:
        pts = spline(pts, n)
    ls = LineString(pts)
    L = ls.length
    if L == 0:
        return disc(pts[0][0], pts[0][1], w / 2)
    k = max(8, int(L / 6))
    left, right, caps = [], [], []
    samples = [ls.interpolate(L * i / k) for i in range(k + 1)]
    for i, p in enumerate(samples):
        s = i / k
        a = samples[max(0, i - 1)]
        b = samples[min(k, i + 1)]
        dx, dy = b.x - a.x, b.y - a.y
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        # profile: taper[0] at start, 1 in the middle, taper[1] at the end
        if s < 0.5:
            prof = taper[0] + (1 - taper[0]) * _smooth(min(1, s / 0.35))
        else:
            prof = taper[1] + (1 - taper[1]) * _smooth(min(1, (1 - s) / 0.35))
        hw = w / 2 * prof
        left.append((p.x + nx * hw, p.y + ny * hw))
        right.append((p.x - nx * hw, p.y - ny * hw))
        if i in (0, k):
            caps.append(disc(p.x, p.y, hw, 8))
    body = Polygon(left + right[::-1]).buffer(0)
    return U(body, *caps)


def _smooth(x):
    return x * x * (3 - 2 * x)


def rough(g, amp=2.2, step=5.0, seed=1):
    """Hand-inked edge: resample the outline and push it along the normal with smooth noise."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.283) for _ in range(3)]

    def ringfix(coords):
        ls = LineString(coords)
        L = ls.length
        n = max(12, int(L / step))
        pts = [ls.interpolate(L * i / n) for i in range(n)]
        out = []
        for i, p in enumerate(pts):
            a, b = pts[i - 1], pts[(i + 1) % n]
            dx, dy = b.x - a.x, b.y - a.y
            d = math.hypot(dx, dy) or 1
            u = L * i / n
            off = amp * (0.55 * math.sin(u / 23 + ph[0]) + 0.3 * math.sin(u / 9.7 + ph[1]) + 0.15 * math.sin(u / 4.1 + ph[2]))
            out.append((p.x - dy / d * off, p.y + dx / d * off))
        return out

    polys = []
    for p in _polys(g):
        polys.append(Polygon(ringfix(p.exterior.coords), [ringfix(r.coords) for r in p.interiors]).buffer(0))
    return U(*polys)


def _polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [x for x in getattr(g, "geoms", []) if isinstance(x, Polygon)]


def move(g, dx=0, dy=0):
    return affinity.translate(g, dx, dy)


def scale(g, sx, sy=None, origin=(256, 256)):
    return affinity.scale(g, sx, sy if sy is not None else sx, origin=origin)


def rot(g, deg, origin=(256, 256)):
    return affinity.rotate(g, deg, origin=origin)


def mirror(g, x=256):
    return affinity.scale(g, -1, 1, origin=(x, 0))


def bounds(g):
    return g.bounds


def fit_box(g, x0, y0, x1, y1, keep=True):
    bx0, by0, bx1, by1 = g.bounds
    sx, sy = (x1 - x0) / (bx1 - bx0), (y1 - y0) / (by1 - by0)
    if keep:
        sx = sy = min(sx, sy)
    g = affinity.scale(g, sx, sy, origin=(bx0, by0))
    bx0, by0, bx1, by1 = g.bounds
    return affinity.translate(g, (x0 + x1) / 2 - (bx0 + bx1) / 2, (y0 + y1) / 2 - (by0 + by1) / 2)


# ---------------------------------------------------------------- motifs


def heart(x, y, s, res=48):
    """classic heart, s = width; (x, y) = centre of its bbox."""
    pts = []
    for i in range(res):
        t = 2 * math.pi * i / res
        px = 16 * math.sin(t) ** 3
        py = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((px, py))
    g = Polygon(pts).buffer(0)
    b = g.bounds
    return fit_box(g, x - s / 2, y - s / 2 * (b[3] - b[1]) / (b[2] - b[0]), x + s / 2, y + s / 2 * (b[3] - b[1]) / (b[2] - b[0]))


def spark(x, y, r, pinch=0.3, rotdeg=0):
    """✦ latex glare: 4 tips joined by concave quadratic sides; pinch = radius at 45° / r."""
    c = (math.sqrt(2) * pinch - 0.5) * r
    tips = [(0, -r), (r, 0), (0, r), (-r, 0)]
    ctl = [(c, -c), (c, c), (-c, c), (-c, -c)]
    ca, sa = math.cos(math.radians(rotdeg)), math.sin(math.radians(rotdeg))
    R = lambda p: (x + p[0] * ca - p[1] * sa, y + p[0] * sa + p[1] * ca)
    tips, ctl = [R(p) for p in tips], [R(p) for p in ctl]
    pts = []
    for j in range(4):
        pts += quad(tips[j], ctl[j], tips[(j + 1) % 4], 12)[:-1]
    return Polygon(pts).buffer(0)


def star(x, y, ro, ri, n=5, rotdeg=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rotdeg + 180 * i / n)
        r = ro if i % 2 == 0 else ri
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return Polygon(pts)


def drop(x, y, r, h=None):
    """teardrop: round bottom centred at (x, y) radius r, tip up at y - h."""
    h = h or r * 2.2
    body = Polygon([(x, y - h)] + arc(x, y, r, -32, 212, 36)).buffer(0)
    return U(body, disc(x, y, r))


def eyelet(x, y, ro, ri=None):
    """grommet: fat ring (the brand's louverse motif)."""
    ri = ri if ri is not None else ro * 0.52
    return ring(x, y, ro, ri)


def glare(cx, cy, length=640, w1=38, w2=16, gap=16, angle=-35):
    """latex glare: two parallel streaks (thick + thin), centred on (cx, cy), rotated."""
    a = rect(cx - length / 2, cy - w1 / 2, cx + length / 2, cy + w1 / 2)
    b = rect(cx - length / 2, cy + w1 / 2 + gap, cx + length / 2, cy + w1 / 2 + gap + w2)
    return rot(U(a, b), angle, (cx, cy))


def xmark(x, y, s, w=W, rotdeg=0):
    g = U(line([(x - s / 2, y - s / 2), (x + s / 2, y + s / 2)], w), line([(x - s / 2, y + s / 2), (x + s / 2, y - s / 2)], w))
    return rot(g, rotdeg, (x, y)) if rotdeg else g


# ---------------------------------------------------------------- fonts


class _FlatPen:
    def __init__(self, glyphset, flat=8):
        from fontTools.pens.basePen import BasePen

        pen = self

        class P(BasePen):
            def _moveTo(self, p):
                pen.cur = [p]
                pen.contours.append(pen.cur)

            def _lineTo(self, p):
                pen.cur.append(p)

            def _curveToOne(self, p1, p2, p3):
                p0 = pen.cur[-1]
                pen.cur.extend(bezier(p0, p1, p2, p3, flat)[1:])

            def _qCurveToOne(self, p1, p2):
                p0 = pen.cur[-1]
                pen.cur.extend(quad(p0, p1, p2, flat)[1:])

            def _closePath(self):
                pass

            def _endPath(self):
                pass

        self.contours = []
        self.cur = None
        self.pen = P(glyphset)


_font_cache = {}


def font(name, **axes):
    key = (name, tuple(sorted(axes.items())))
    if key in _font_cache:
        return _font_cache[key]
    from fontTools.ttLib import TTFont
    f = TTFont(os.path.join(FONTS, name))
    if axes and "fvar" in f:
        from fontTools.varLib.instancer import instantiateVariableFont
        f = instantiateVariableFont(f, axes)
    _font_cache[key] = f
    return f


def glyph(ch, fnt):
    gs = fnt.getGlyphSet()
    cmap = fnt.getBestCmap()
    gname = cmap[ord(ch)]
    fp = _FlatPen(gs)
    gs[gname].draw(fp.pen)
    g = Polygon()
    for c in fp.contours:
        if len(c) < 3:
            continue
        g = g.symmetric_difference(Polygon(c).buffer(0))
    adv = gs[gname].width
    return affinity.scale(g, 1, -1, origin=(0, 0)), adv


def text(s, fnt, x, y, h, tracking=0.06, bold=0.0, width=None, anchor="c"):
    """Outline text. h = cap height px. bold = outline growth in px (Michroma is light).
    width: force total width by horizontal scaling."""
    upm = fnt["head"].unitsPerEm
    cap = getattr(fnt["OS/2"], "sCapHeight", 0) or upm * 0.7
    k = h / cap
    pen_x = 0
    parts = []
    for ch in s:
        if ch == " ":
            pen_x += upm * 0.35
            continue
        g, adv = glyph(ch, fnt)
        parts.append(affinity.translate(g, pen_x, 0))
        pen_x += adv + tracking * upm
    g = U(*parts)
    g = affinity.scale(g, k, k, origin=(0, 0))
    if bold:
        g = g.buffer(bold, join_style=2, mitre_limit=3)
    bx0, by0, bx1, by1 = g.bounds
    if width:
        g = affinity.scale(g, width / (bx1 - bx0), 1, origin=(bx0, 0))
        bx0, by0, bx1, by1 = g.bounds
    # centre on (x, y)
    return affinity.translate(g, x - (bx0 + bx1) / 2, y - (by0 + by1) / 2)


# ---------------------------------------------------------------- svg (v1 geometry)


def _svg_transform(t):
    """parse translate/scale/matrix into an affine (a, b, c, d, e, f): x' = a x + c y + e, y' = b x + d y + f."""
    import re
    m = [1, 0, 0, 1, 0, 0]

    def mul(p, q):
        a1, b1, c1, d1, e1, f1 = p
        a2, b2, c2, d2, e2, f2 = q
        return [a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
                a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1]
    for name, args in re.findall(r"(\w+)\(([^)]*)\)", t or ""):
        v = [float(x) for x in re.split(r"[ ,]+", args.strip()) if x]
        if name == "translate":
            q = [1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0]
        elif name == "scale":
            q = [v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0]
        elif name == "matrix":
            q = v
        else:
            continue
        m = mul(m, q)
    return m


def svg(path):
    """SVG paths -> shapely (evenodd), honouring group transforms (potrace output uses them)."""
    import xml.etree.ElementTree as ET
    from svgpathtools import parse_path
    root = ET.parse(path).getroot()
    g = Polygon()

    def walk(el, m):
        nonlocal g
        t = _svg_transform(el.get("transform"))
        a1, b1, c1, d1, e1, f1 = m
        a2, b2, c2, d2, e2, f2 = t
        m = [a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
             a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1]
        if el.tag.endswith("path"):
            p = parse_path(el.get("d"))
            for sub in p.continuous_subpaths():
                pts = []
                for seg in sub:
                    n = 1 if seg.__class__.__name__ == "Line" else 12
                    for i in range(n):
                        z = seg.point(i / n)
                        x, y = z.real, z.imag
                        pts.append((m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]))
                if len(pts) >= 3:
                    g = g.symmetric_difference(Polygon(pts).buffer(0))
        for ch in el:
            walk(ch, m)
    walk(root, [1, 0, 0, 1, 0, 0])
    return g


def tgs_geometry(path, layer_names=None):
    """Static geometry of a v1 .tgs (layers' shapes at frame 0, anchors resolved)."""
    import gzip
    import json
    d = json.load(gzip.open(path))
    out = {}
    for L in d["layers"]:
        if layer_names and L["nm"] not in layer_names:
            continue
        ks = L["ks"]

        def val(p):
            k = p["k"]
            if p.get("a"):
                k = k[0]["s"]
            return k
        px, py = val(ks["p"])[:2]
        ax, ay = val(ks["a"])[:2]
        g = Polygon()

        def walk(items):
            nonlocal g
            for it in items:
                if it["ty"] == "gr":
                    walk(it["it"])
                elif it["ty"] == "sh":
                    k = it["ks"]["k"]
                    if isinstance(k, list):
                        k = k[0]["s"][0]
                    if len(k["v"]) >= 3:
                        g = g.symmetric_difference(Polygon(k["v"]).buffer(0))
        walk(L.get("shapes", []))
        out[L["nm"]] = affinity.translate(g, px - ax, py - ay)
    return out


# ---------------------------------------------------------------- to lottie


def paths(g, tol=0.45, nm="p"):
    """shapely -> list of Lottie `sh` items (exteriors + holes; use with an evenodd fill)."""
    out = []
    for p in _polys(g):
        p = p.simplify(tol, preserve_topology=True)
        if p.is_empty:
            continue
        p = orient(p)
        for ring_ in [p.exterior] + list(p.interiors):
            pts = list(ring_.coords)[:-1]
            if len(pts) >= 3:
                out.append(lot.sh(lot.pathdata(pts), nm))
    return out


def hole(layer, g, nm="hole", **t):
    """cut an animated hole into a layer's filled group (evenodd): g must lie fully inside the black."""
    layer.shapes[0]["it"].insert(0, lot.group(paths(g), nm=nm, **t))
    return layer


def stroked(pts, w, nm="line", e=100, s=0, cap=2, **t):
    """open polyline drawn with a round-capped stroke; e/s may be Tracks (trim path: draw-on)."""
    items = [lot.sh(lot.pathdata(pts, closed=False), nm), lot.stroke(w, cap=cap, join=2)]
    if not (e == 100 and s == 0):
        items.append(lot.trim(s, e))
    return lot.group(items, nm=nm, **t)


def shape(g, o=100, nm="g", tol=0.45, **t):
    """shapely -> a filled Lottie group."""
    return lot.group(paths(g, tol) + [lot.fill(o)], nm=nm, **t)


def resample(g, n, start_angle=None):
    """Exterior of a polygon as exactly n points (for shape morphs). Starts at the point closest to
    start_angle (deg, from centroid) so morph targets line up."""
    p = max(_polys(g), key=lambda q: q.area)
    p = orient(p)
    ls = LineString(p.exterior.coords)
    L = ls.length
    pts = [ls.interpolate(L * i / n) for i in range(n)]
    pts = [(q.x, q.y) for q in pts]
    if start_angle is not None:
        c = p.centroid
        a = math.radians(start_angle)
        tx, ty = c.x + math.cos(a) * 1000, c.y + math.sin(a) * 1000
        i0 = min(range(n), key=lambda i: (pts[i][0] - tx) ** 2 + (pts[i][1] - ty) ** 2)
        pts = pts[i0:] + pts[:i0]
    return pts
