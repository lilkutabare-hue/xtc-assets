"""Kaomoji face kit: eyes + mouth glyphs in one brush weight, and a rig (face root -> eyes, mouth, extras).
Faces have no head outline: the glyphs ARE the face (language of v1 33-42), but big and fat."""
import math

from . import geo
from .geo import U, W, brush, disc, line, ring

# layout on the 512 canvas
EX = 124        # eye offset from centre
EY = 206        # eye centre y
MY = 346        # mouth centre y
ES = 150        # eye glyph box
CX = 256


def eyes_xy(dx=EX, y=EY):
    return (CX - dx, y), (CX + dx, y)


# ---------------------------------------------------------------- eyes


def chevron(x, y, s=ES, d=1, w=W, open_=0.9):
    """'>' (d=1) or '<' (d=-1); open_ = height/width."""
    hw = s * 0.42
    hh = s * 0.5 * open_
    return brush([(x - d * hw, y - hh), (x + d * hw, y), (x - d * hw, y + hh)], w, taper=(0.6, 0.6), smooth=False)


def caret(x, y, s=ES, w=W, h=0.55, round_=True):
    """'^' happy eye."""
    hw, hh = s * 0.46, s * h / 2
    if round_:
        pts = geo.quad((x - hw, y + hh), (x, y - hh * 2.2), (x + hw, y + hh), 16)
        return brush(pts, w, taper=(0.55, 0.55), smooth=False)
    return brush([(x - hw, y + hh), (x, y - hh), (x + hw, y + hh)], w, taper=(0.6, 0.6), smooth=False)


def cup(x, y, s=ES, w=W, h=0.45):
    """'u' / smiling-closed eye (downward arc)."""
    hw, hh = s * 0.46, s * h / 2
    pts = geo.quad((x - hw, y - hh), (x, y + hh * 2.2), (x + hw, y - hh), 16)
    return brush(pts, w, taper=(0.55, 0.55), smooth=False)


def eyelet(x, y, r=ES * 0.46, k=0.46):
    """'O' — the brand grommet as an eye: fat ring."""
    return ring(x, y, r, r * k, 20)


def dot(x, y, r=40):
    return disc(x, y, r, 12)


def dash(x, y, s=ES, w=W, tilt=0):
    hw = s * 0.46
    dy = math.tan(math.radians(tilt)) * hw
    return brush([(x - hw, y - dy), (x + hw, y + dy)], w, taper=(0.7, 0.7), smooth=False)


def xeye(x, y, s=ES * 0.9, w=W):
    h = s / 2
    return U(brush([(x - h, y - h), (x + h, y + h)], w, (0.55, 0.55), False),
             brush([(x - h, y + h), (x + h, y - h)], w, (0.55, 0.55), False))


def teye(x, y, s=ES, w=W):
    """'T' crying eye: bar + stem."""
    hw = s * 0.5
    return U(brush([(x - hw, y - s * 0.28), (x + hw, y - s * 0.28)], w, (0.7, 0.7), False),
             brush([(x, y - s * 0.28), (x, y + s * 0.42)], w, (1, 0.6), False))


def heye(x, y, s=ES * 1.05):
    return geo.heart(x, y, s)


def spiral(x, y, r=ES * 0.5, w=W * 0.78, turns=1.75):
    pts = []
    n = 64
    for i in range(n + 1):
        t = i / n
        a = -math.pi / 2 + t * turns * 2 * math.pi
        rr = r * (0.18 + 0.82 * t)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return brush(pts, w, taper=(0.5, 0.9), smooth=False)


def neg(x, y, s=ES, d=1, w=W):
    """'¬' side-eye lid: bar + short drop on the outer side (d=1 drop right)."""
    hw = s * 0.48
    return brush([(x - d * hw, y - s * 0.12), (x + d * hw, y - s * 0.12), (x + d * hw, y + s * 0.3)], w, (0.7, 0.8), False)


def brow(x, y, s=ES, ang=20, w=W * 0.85):
    """angled brow bar; ang>0 = inner end down (angry) for the left eye; mirror for right."""
    hw = s * 0.5
    dy = math.tan(math.radians(ang)) * hw
    return brush([(x - hw, y - dy), (x + hw, y + dy)], w, (0.6, 0.9), False)


# ---------------------------------------------------------------- mouths


def m_line(x=CX, y=MY, w_=150, w=W):
    return brush([(x - w_ / 2, y), (x + w_ / 2, y)], w, (0.75, 0.75), False)


def m_smile(x=CX, y=MY, w_=170, h=52, w=W):
    return brush(geo.quad((x - w_ / 2, y - h / 2), (x, y + h * 1.1), (x + w_ / 2, y - h / 2), 18), w, (0.55, 0.55), False)


def m_frown(x=CX, y=MY, w_=160, h=46, w=W):
    return brush(geo.quad((x - w_ / 2, y + h / 2), (x, y - h * 1.1), (x + w_ / 2, y + h / 2), 18), w, (0.55, 0.55), False)


def m_tri(x=CX, y=MY, w_=190, h=130, r=22):
    """'▽' open laugh: rounded triangle, flat top."""
    t = geo.poly([(x - w_ / 2, y - h * 0.42), (x + w_ / 2, y - h * 0.42), (x, y + h * 0.58)])
    return t.buffer(-r).buffer(r)


def m_box(x=CX, y=MY, w_=150, h=150, wall=W, r=34):
    """'□' scream: fat rounded-rect ring."""
    return geo.rrect(x - w_ / 2, y - h / 2, x + w_ / 2, y + h / 2, r).difference(
        geo.rrect(x - w_ / 2 + wall, y - h / 2 + wall, x + w_ / 2 - wall, y + h / 2 - wall, max(4, r - wall * 0.6)))


def m_o(x=CX, y=MY, r=46, k=0.42):
    return ring(x, y, r, r * k, 16)


def m_w(x=CX, y=MY, w_=180, h=54, w=W * 0.9):
    """'ω'."""
    q = w_ / 4
    pts = geo.quad((x - 2 * q, y - h / 2), (x - q, y + h * 1.2), (x, y - h / 2 + 4), 12) + \
        geo.quad((x, y - h / 2 + 4), (x + q, y + h * 1.2), (x + 2 * q, y - h / 2), 12)[1:]
    return brush(pts, w, (0.55, 0.55), False)


def m_3(x=CX, y=MY, s=120, w=W * 0.9):
    """'3' kiss (pucker), opening to the right."""
    h = s / 2
    pts = geo.quad((x - h * 0.45, y - h), (x + h * 0.85, y - h * 0.95), (x + h * 0.05, y - h * 0.05), 10) + \
        geo.quad((x + h * 0.05, y - h * 0.05), (x + h * 0.95, y + h * 0.9), (x - h * 0.45, y + h), 10)[1:]
    return brush(pts, w, (0.55, 0.55), False)


def m_wave(x=CX, y=MY, w_=190, amp=18, w=W * 0.9, waves=2):
    pts = [(x - w_ / 2 + w_ * i / 40, y + amp * math.sin(math.pi * 2 * waves * i / 40)) for i in range(41)]
    return brush(pts, w, (0.6, 0.6), False)


def m_grit(x=CX, y=MY, w_=230, h=104, wall=26, cols=4):
    """grimace: rounded rect with a teeth grid of holes."""
    outer = geo.rrect(x - w_ / 2, y - h / 2, x + w_ / 2, y + h / 2, 30)
    holes = []
    iw = (w_ - wall * (cols + 1)) / cols
    ih = (h - wall * 3) / 2
    for c in range(cols):
        for r in range(2):
            x0 = x - w_ / 2 + wall + c * (iw + wall)
            y0 = y - h / 2 + wall + r * (ih + wall)
            holes.append(geo.rrect(x0, y0, x0 + iw, y0 + ih, 6))
    return outer.difference(U(*holes))


def m_smirk(x=CX, y=MY, w_=160, h=40, w=W):
    """'‿' pulled to one side (right corner up)."""
    pts = geo.quad((x - w_ / 2, y + h * 0.1), (x + w_ * 0.15, y + h * 1.1), (x + w_ / 2, y - h * 0.9), 16)
    return brush(pts, w, (0.7, 0.5), False)


# ---------------------------------------------------------------- extras


def tear(x, y, r=26):
    return geo.drop(x, y, r, r * 2.3)


def vein(x, y, s=78, w=24):
    """anger mark '╬' as 4 bent bars (manga)."""
    h = s / 2
    parts = []
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        a = (x + sx * h * 0.25, y + sy * h)
        b = (x + sx * h * 0.25, y + sy * h * 0.25)
        c = (x + sx * h, y + sy * h * 0.25)
        parts.append(line([a, b, c], w, "round", "round"))
    return U(*parts)


def blush(x, y, n=4, s=74, w=18, gap=26):
    """'////' hatch blush."""
    parts = []
    for i in range(n):
        cx = x - (n - 1) * gap / 2 + i * gap
        parts.append(line([(cx - s * 0.18, y + s / 2), (cx + s * 0.18, y - s / 2)], w))
    return U(*parts)


def zzz(x, y, s=60, w=22):
    h = s / 2
    return line([(x - h, y - h), (x + h, y - h), (x - h, y + h), (x + h, y + h)], w, "round", "mitre")


def qmark(x, y, s=120, w=W * 0.8):
    h = s / 2
    pts = geo.arc(x, y - h * 0.35, h * 0.62, 190, 400, 20) + [(x, y + h * 0.3)]
    return U(brush(pts, w, (0.9, 0.9), True, 4), disc(x, y + h * 0.78, w * 0.62))


def emark(x, y, s=130, w=W):
    h = s / 2
    return U(brush([(x, y - h), (x, y + h * 0.35)], w * 1.1, (1, 0.6), False), disc(x, y + h * 0.82, w * 0.6))


def steam(x, y, s=70, w=24, d=1):
    """small puff cloud."""
    return U(disc(x, y, s * 0.32), disc(x + d * s * 0.3, y - s * 0.12, s * 0.26), disc(x - d * s * 0.28, y + s * 0.05, s * 0.22))
