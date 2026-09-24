"""v3.7: the XTCRECORDS pack (client's older emoji set) rebuilt in the adaptive mono language:
lips, 100%% XTC, star ring, star, star snowflake, clef, ¥€$."""
import math
import os

from xtc import geo, logo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import brand_font
from specs.reactions import seq, breathe, rig, part

SER = "records"
REC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v1", "rec")


def rec(name):
    """the client's original XTCRECORDS artwork, traced 1:1 from the 512px sources (v1/rec/*.svg)."""
    return geo.svg(os.path.join(REC, name + ".svg"))


def star_outline(x, y, ro, w=None, n=5, rot=-90, ri=None):
    ri = ri if ri is not None else ro * 0.42
    s = geo.star(x, y, ro, ri, n, rot)
    if w is None:
        return s
    return s.difference(s.buffer(-w, join_style=2, mitre_limit=4))


def mtext(s, x, y, h, width=None, bold=8):
    return geo.text(s, brand_font(), x, y, h, bold=bold, width=width)


# ================================================================ 153 💋 lips


def lips(cx=256, cy=270, w=380, h=210, stroke=34):
    """outline lips: cupid's-bow upper lip + full lower lip, mouth line."""
    L, R = (cx - w / 2, cy), (cx + w / 2, cy)
    top = geo.quad(L, (cx - w * 0.28, cy - h * 0.62), (cx - w * 0.06, cy - h * 0.24), 14)[:-1] + \
        geo.quad((cx - w * 0.06, cy - h * 0.24), (cx, cy - h * 0.16), (cx + w * 0.06, cy - h * 0.24), 8)[:-1] + \
        geo.quad((cx + w * 0.06, cy - h * 0.24), (cx + w * 0.28, cy - h * 0.62), R, 14)
    bot = geo.quad(R, (cx, cy + h * 0.78), L, 22)
    outer = geo.Polygon(top + bot[1:]).buffer(0)
    body = outer.difference(outer.buffer(-stroke, join_style=1))
    mouth = geo.brush(geo.quad(L, (cx, cy + h * 0.12), R, 20), stroke * 0.8, taper=(0.5, 0.5), smooth=False)
    return geo.U(body, mouth), outer


@emoji("153-lips", "💋", "губы, поцелуй, чмок, xtc records, звезда", "lips, kiss, mwah, xtc records, star",
       "губы-контур: собираются в поцелуй (сжатие к центру, верхняя губа вниз), «чмок» — отдача, у уголка вспыхивает звезда контуром и гаснет; медленный наклон",
       op=150, series=SER)
def lips_e(c):
    OP = 150
    g = rec("lips")
    b_ = g.bounds
    cx, cy = (b_[0] + b_[2]) / 2, (b_[1] + b_[3]) / 2
    # the mouth line: split the artwork into the upper and the lower lip along the mouth's centre line
    holes = [geo.Polygon(r) for p in geo._polys(g) for r in p.interiors]
    mouth = max(holes, key=lambda h: h.area)
    my = mouth.centroid.y
    upper = g.intersection(geo.rect(0, 0, 512, my))
    lower = g.intersection(geo.rect(0, my, 512, 512))
    # KISS: lips pucker (narrow, taller, lips press together), push to the camera, hold, "mwah" - lips
    # part with a 1f smack and the whole mouth recoils, settles; twice per loop with a rest between
    root_s = Track([100, 100], 0)
    root_r = Track(0, 0)
    up_y = Track(0.0, 0)
    lo_y = Track(0.0, 0)
    for t, d in ((10, -4), (76, 3)):
        root_s.hold(t).to(t + 14, [84, 110], "io").to(t + 20, [92, 118], "io").to(t + 24, [90, 116], "io")   # pucker, push
        root_s.to(t + 26, [108, 96], "slam").to(t + 27, [108, 96], "lin").to(t + 35, [97, 103], "o").to(t + 43, [101, 99.5], "io").to(t + 52, [100, 100], "io")
        root_r.hold(t).to(t + 20, d, "io").to(t + 52, 0, "io")
        up_y.hold(t).to(t + 14, 9.0, "io").hold(t + 24).to(t + 26, -6.0, "slam").to(t + 36, 0.0, "o")        # lips press, then part
        lo_y.hold(t).to(t + 14, -9.0, "io").hold(t + 24).to(t + 26, 6.0, "slam").to(t + 36, 0.0, "o")
    root_s.loop(OP)
    root_r.loop(OP)
    up_y.loop(OP)
    lo_y.loop(OP)
    root = rig(c, "lips", (cx, cy), s=root_s, r=root_r)
    part(c, "upper", upper, root, (cx, my), p=Split(cx, _sh(up_y, my)))
    part(c, "lower", lower, root, (cx, my), p=Split(cx, _sh(lo_y, my)))


# ================================================================ 154 💯 100%% XTC


@emoji("154-100xtc", "💯", "100%, сто процентов, xtc, records, чисто", "100%, hundred percent, xtc, records, pure",
       "«100%%» над логотипом XTC: проценты перещёлкиваются ребром по очереди (fake-3D), «100» садится ударом, XTC толкает табло — тяжёлый бейдж",
       op=150, series=SER)
def hundred_xtc(c):
    OP = 150
    g = rec("100xtc")
    b_ = g.bounds
    ymid = (b_[1] + b_[3]) / 2
    top = g.intersection(geo.rect(0, 0, 512, ymid))
    word = g.intersection(geo.rect(0, ymid, 512, 512))
    tb = top.bounds
    xsplit = tb[0] + (tb[2] - tb[0]) * 0.47
    one = top.intersection(geo.rect(0, 0, xsplit, 512))
    pcs = top.intersection(geo.rect(xsplit, 0, 512, 512))
    hs = seq([94, 94], [(40, None, None), (43, [97, 91], "o"), (52, [94, 94], "io"), (74, None, None), (77, [96, 92], "o"), (86, [94, 94], "io")], op=OP)
    root = rig(c, "badge", (256, b_[3]), s=hs)
    part(c, "xtc", word, root, (256, ymid))
    ob = one.bounds
    ox, oy = (ob[0] + ob[2]) / 2, ob[3]
    oyt = seq(float(oy), [(8, None, None), (14, oy - 44.0, "decel"), (24, float(oy), "slam")], op=OP)
    os_ = seq([100, 100], [(23, None, None), (24, [110, 90], "lin"), (25, [110, 90], "lin"), (32, [97, 103], "io"), (40, [100, 100], "io")], op=OP)
    part(c, "100", one, root, (ox, oy), p=Split(ox, oyt), s=os_)
    # the two % turn edge-on one after the other (fake-3D), the pair stays one piece
    pb = pcs.bounds
    for k, (x0, x1) in enumerate(((pb[0], (pb[0] + pb[2]) / 2), ((pb[0] + pb[2]) / 2, pb[2]))):
        pc = pcs.intersection(geo.rect(x0, 0, x1, 512))
        cb = pc.bounds
        px, py = (cb[0] + cb[2]) / 2, (cb[1] + cb[3]) / 2
        t0 = 40 + k * 34
        segs = [(t0, t0 + 28, 0, 360, (0.4, 0.0, 0.16, 1.0))]
        M.spin3d(c, f"pc{k}", pc, pc, px, py, segs, thick=22, lip=12, parent=root)


def _sh(tr, d):
    out = Track(tr.k[0][1] + d, tr.k[0][0])
    out.k = [[t, v + d, e] for t, v, e in tr.k]
    return out


# ================================================================ 155 🌟 star ring with XTC


@emoji("155-star-ring", "🌟", "звёзды, кольцо, xtc records, лого, орбита", "stars, ring, xtc records, logo, orbit",
       "двенадцать звёзд-контуров кольцом вокруг XTC: кольцо тяжело проворачивается на одну звезду и садится, каждая звезда по очереди вспыхивает заливкой по кругу",
       op=180, series=SER)
def star_ring(c):
    OP = 180
    g = rec("starring")
    polys = sorted(geo._polys(g), key=lambda p: -p.area)
    cx, cy = 256, 256
    stars = [p for p in polys if math.hypot(p.centroid.x - cx, p.centroid.y - cy) > 150]
    mark = geo.U(*[p for p in polys if math.hypot(p.centroid.x - cx, p.centroid.y - cy) <= 150])
    mb = mark.bounds
    part(c, "xtc", mark, None, ((mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2))          # static, untouched
    # the stars stay where the artwork put them; a spin runs around the circle clockwise from the mark,
    # each star turning 360 on itself with a heavy ease, slight grow at the peak; twice per loop
    stars.sort(key=lambda p: (math.atan2(p.centroid.y - cy, p.centroid.x - cx) + 0.3) % (2 * math.pi))
    n = len(stars)
    for k, p in enumerate(stars):
        c_ = p.centroid
        spin = Track(0, 0)
        sc = Track([100, 100], 0)
        for t0 in (4, 90):
            t = t0 + k * 5
            spin.hold(t).to(t + 30, 360, (0.4, 0.0, 0.16, 1.0))
            spin.k[-1][2] = "hold"
            spin.k.append([t + 30.01, 0, None])
            sc.hold(t).to(t + 12, [118, 118], "io").to(t + 30, [100, 100], "io")
        spin.hold(OP)
        spin.k[-1][2] = None
        sc.loop(OP)
        part(c, f"s{k}", p, None, (c_.x, c_.y), r=spin, s=sc)


# ================================================================ 156 ⭐ star


@emoji("156-star", "⭐", "звезда, xtc records, топ, контур", "star, xtc records, top, outline",
       "большая звезда-контур делает тяжёлый оборот с торцом, на обороте — заливка с логотипным X, садится лицом с досадкой",
       op=180, series=SER)
def star_e(c):
    OP = 180
    front = rec("star")
    fb = front.bounds
    cx, cy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2
    # slow and heavy: pull back 14°, one full turn in 96f, overshoot, settle, long rest
    r = seq(0, [(12, None, None), (26, -14, "io"), (122, 368, (0.45, 0.0, 0.2, 1.0)), (136, 357, "io"), (150, 361, "io"), (164, 360, "io")], op=OP, loop_ease="lin")
    r.k[-1][2] = "hold"
    s_ = seq([88, 88], [(12, None, None), (26, [84, 84], "io"), (70, [92, 92], "io"), (122, [88, 88], "io")], op=OP)
    body = rig(c, "body", (cx, cy), r=r, s=s_)
    part(c, "star", front, body, (cx, cy))


# ================================================================ 157 ❄️ star snowflake


@emoji("157-star-flake", "❄️", "снежинка, звёзды, xtc records, сигил, зима", "snowflake, stars, xtc records, sigil, winter",
       "снежинка из звёзд-контуров (6 лучей × 3): медленно проворачивается, заливка бежит волной от центра к краям и обратно",
       op=180, series=SER)
def star_flake(c):
    OP = 180
    g = rec("flake")
    cx, cy = 256, 256
    # the whole flake makes one slow heavy turn (360 = seamless), breathing; while it turns, every star
    # spins on itself in a wave from the centre outwards, growing a touch at the peak
    fr = seq(0, [(8, None, None), (160, 360, (0.4, 0.0, 0.2, 1.0))], op=OP, loop_ease="lin")
    fr.k[-1][2] = "hold"
    fs = seq([92, 92], [(8, None, None), (84, [96, 96], "io"), (160, [92, 92], "io")], op=OP)
    ring = rig(c, "flake", (cx, cy), r=fr, s=fs)
    polys = geo._polys(g)
    polys.sort(key=lambda p: math.hypot(p.centroid.x - cx, p.centroid.y - cy))
    for k, p in enumerate(polys):
        c_ = p.centroid
        d = math.hypot(c_.x - cx, c_.y - cy)
        t = 20 + int(d / 240 * 70)
        spin = Track(0, 0).hold(t).to(t + 44, 360, (0.4, 0.0, 0.16, 1.0))
        spin.k[-1][2] = "hold"
        spin.k.append([OP, 0, None])
        sc = seq([100, 100], [(t, None, None), (t + 18, [116, 116], "io"), (t + 44, [100, 100], "io")], op=OP)
        part(c, f"s{k}", p, ring, (c_.x, c_.y), r=spin, s=sc)


# ================================================================ 158 🎼 clef


def clef(cx=256, cy=256, h=440, w=40):
    """stylised treble clef: bottom curl, curved stem, top loop, big middle loop (spiral)."""
    k = h / 440
    P = lambda x, y: (cx + x * k, cy + y * k)
    tail = geo.brush([P(-46, 196), P(-64, 172), P(-40, 152), P(-6, 168), P(-4, 130)], w * 0.9, taper=(0.55, 1.0), smooth=True, n=8)
    stem = geo.brush([P(-4, 130), P(4, 0), P(22, -150), P(30, -214)], w, taper=(1.0, 0.9), smooth=True, n=6)
    top = geo.brush([P(30, -214), P(54, -196), P(58, -150), P(30, -110), P(-10, -70)], w * 0.95, taper=(0.9, 0.7), smooth=True, n=8)
    loop = []
    for i in range(37):
        t = i / 36
        ang = math.radians(-100 + 330 * t)
        r = 110 - 44 * t
        loop.append(P(-8 + r * math.cos(ang), 56 + r * math.sin(ang) * 0.92))
    spiral = geo.brush(loop, w * 1.05, taper=(0.8, 0.5), smooth=True, n=4)
    return geo.U(tail, stem, top, spiral)


@emoji("158-clef", "🎼", "скрипичный ключ, музыка, records, xtc, трек", "treble clef, music, records, xtc, track",
       "скрипичный ключ XTC Records: качается метрономом на бит (120 BPM) с тяжёлой досадкой, на четвёртой доле удар — приседает и подпрыгивает",
       op=120, series=SER)
def clef_e(c):
    OP = 120
    g = clef(256, 262, 430, 42)
    r = Track(0, 0)
    for t in (0, 30, 60):
        r.to(t + 12, 7 if t % 60 == 0 else -7, "io").to(t + 30, 0 if t < 60 else -2, "io")
    r.to(96, 3, "io").to(120, 0, "io")
    s = seq([100, 100], [(88, None, None), (92, [108, 92], "slam"), (93, [108, 92], "lin"), (100, [96, 104], "o"), (108, [101, 99], "io"), (116, [100, 100], "io")], op=OP)
    root = rig(c, "clef", (256, 470), r=r, s=s)
    part(c, "clef", g, root, (256, 262))


# ================================================================ 159 💸 ¥€$


@emoji("159-yes-money", "💸", "деньги, yes, ¥€$, xtc records, бабки", "money, yes, ¥€$, xtc records, cash",
       "¥€$ — три знака валют как слот-машина: каждый перещёлкивается по вертикали (flip по X) с отскоком, последним встаёт $ — табло толкает",
       op=150, series=SER)
def yes_money(c):
    OP = 150
    cy = 256
    xs = (112, 256, 400)
    bs = seq([100, 100], [(84, None, None), (88, [103, 97], "o"), (98, [100, 100], "io")], op=OP)
    root = rig(c, "board", (256, 420), s=bs)
    for k, (ch, x) in enumerate(zip("¥€$", xs)):
        if ch == "€":       # Michroma's € closes up when bolded: C + two bars
            g = mtext("C", x + 8, cy, 230, width=132, bold=4)
            g = geo.U(g, geo.rrect(x - 84, cy - 46, x + 20, cy - 20, 6), geo.rrect(x - 84, cy + 10, x + 20, cy + 36, 6))
        else:
            g = mtext(ch, x, cy, 250, bold=4)
            b = g.bounds
            if b[2] - b[0] > 140:
                g = mtext(ch, x, cy, 250, width=140, bold=4)
        t0 = 20 + k * 22
        # vertical flip: scaleY = cos, hold-swap unnecessary (same glyph both sides), bounce at the end
        sy = Track([100, 100], 0).hold(t0).to(t0 + 8, [100, 0], "i").to(t0 + 9, [100, 0], "lin").to(t0 + 17, [100, 100], "o")
        sy.to(t0 + 20, [100, 90], "io").to(t0 + 25, [100, 100], "io").loop(OP)
        part(c, f"g{k}", g, root, (x, cy), s=sy)
