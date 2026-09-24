"""v3.7: the XTCRECORDS pack (client's older emoji set) rebuilt in the adaptive mono language:
lips, 100%% XTC, star ring, star, star snowflake, clef, ¥€$."""
import math

from xtc import geo, logo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import brand_font
from specs.reactions import seq, breathe, rig, part

SER = "records"


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
    g, outer = lips()
    s = seq([100, 100], [(20, None, None), (36, [84, 108], "io"), (44, [110, 94], "snap"), (54, [97, 102], "io"), (64, [100, 100], "io")])
    breathe(s, 80, 150, [100, 100], 0.6, 35)
    s.loop(OP)
    r = seq(0, [(20, None, None), (44, -6, "io"), (90, 0, "io")], op=OP)
    root = rig(c, "lips", (256, 270), s=s, r=r)
    part(c, "lips", g, root, (256, 270))
    st = star_outline(392, 128, 62, 20)
    ss = seq([0, 0], [(42, None, None), (48, [112, 112], "snap"), (56, [100, 100], "io"), (104, None, None), (118, [0, 0], "i")], op=OP, loop_ease="lin")
    sr = seq(-30, [(42, None, None), (118, 40, "os")], op=OP, loop_ease="lin")
    part(c, "star", st, root, (392, 128), s=ss, r=sr)


# ================================================================ 154 💯 100%% XTC


@emoji("154-100xtc", "💯", "100%, сто процентов, xtc, records, чисто", "100%, hundred percent, xtc, records, pure",
       "«100%%» над логотипом XTC: проценты перещёлкиваются ребром по очереди (fake-3D), «100» садится ударом, XTC толкает табло — тяжёлый бейдж",
       op=150, series=SER)
def hundred_xtc(c):
    OP = 150
    top_y, bot_y = 190, 330
    word = logo.word("XTC", 256, bot_y, 96, 440)
    hs = seq([100, 100], [(40, None, None), (43, [103, 97], "o"), (52, [100, 100], "io"), (74, None, None), (77, [102, 98], "o"), (86, [100, 100], "io")], op=OP)
    root = rig(c, "badge", (256, 380), s=hs)
    part(c, "xtc", word, root, (256, bot_y))
    # "100" drops in and lands (slam, 1f squash)
    one = mtext("100", 132, top_y, 104, width=190, bold=6)
    oy = seq(float(top_y), [(8, None, None), (14, top_y - 44.0, "decel"), (24, float(top_y), "slam")], op=OP)
    os_ = seq([100, 100], [(23, None, None), (24, [110, 90], "lin"), (25, [110, 90], "lin"), (32, [97, 103], "io"), (40, [100, 100], "io")], op=OP)
    part(c, "100", one, root, (128, top_y + 52), p=Split(128, _sh(oy, 52)), s=os_)
    # two % signs: each turns edge-on and back (M.spin3d), one after the other
    for k, x in enumerate((300, 416)):
        pc = mtext("%", x, top_y, 96, width=92, bold=3)
        t0 = 40 + k * 34
        segs = [(t0, t0 + 28, 0, 360, (0.4, 0.0, 0.16, 1.0))]
        M.spin3d(c, f"pc{k}", pc, pc, x, top_y, segs, thick=22, lip=14, parent=root)


def _sh(tr, d):
    out = Track(tr.k[0][1] + d, tr.k[0][0])
    out.k = [[t, v + d, e] for t, v, e in tr.k]
    return out


# ================================================================ 155 🌟 star ring with XTC


@emoji("155-star-ring", "🌟", "звёзды, кольцо, xtc records, лого, орбита", "stars, ring, xtc records, logo, orbit",
       "двенадцать звёзд-контуров кольцом вокруг XTC: кольцо тяжело проворачивается на одну звезду и садится, каждая звезда по очереди вспыхивает заливкой по кругу",
       op=150, series=SER)
def star_ring(c):
    OP = 150
    cx, cy, R = 256, 256, 196
    word = logo.word("XTC", cx, cy, 40, 176)
    part(c, "xtc", word, None, (cx, cy))
    rr = seq(0, [(30, None, None), (66, 34, (0.4, 0.0, 0.16, 1.0)), (74, 29, "io"), (82, 30, "io")], op=OP)
    ring = rig(c, "ring", (cx, cy), r=rr)
    for k in range(12):
        a = math.radians(-90 + 30 * k)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        out = star_outline(x, y, 40, 13)
        full = geo.star(x, y, 40, 40 * 0.42, 5, -90)
        t = 90 + k * 4
        so = Track(100, 0)
        fo = Track(0, 0)
        for tr_, on in ((so, 0), (fo, 100)):
            tr_.k[-1][2] = "hold"
            tr_.k.append([t, on, None])
            tr_.k[-1][2] = "hold"
            tr_.k.append([t + 6, 100 - on, None])
            tr_.loop(OP, "lin")
        part(c, f"s{k}", out, ring, (x, y), o=so)
        part(c, f"f{k}", full, ring, (x, y), o=fo)


# ================================================================ 156 ⭐ star


@emoji("156-star", "⭐", "звезда, xtc records, топ, контур", "star, xtc records, top, outline",
       "большая звезда-контур делает тяжёлый оборот с торцом, на обороте — заливка с логотипным X, садится лицом с досадкой",
       op=150, series=SER)
def star_e(c):
    OP = 150
    cx, cy = 256, 262
    front = star_outline(cx, cy, 214, 42)
    back = geo.star(cx, cy, 214, 214 * 0.42, 5, -90).difference(logo.letter("X", cx, cy + 30, 150, 74))
    ss = seq([100, 100], [(10, None, None), (20, [96, 104], "io"), (28, [100, 100], "o"), (88, None, None), (92, [104, 97], "o"), (100, [99, 101], "io"), (108, [100, 100], "io")], op=OP)
    body = rig(c, "body", (cx, cy + 214), s=ss)
    segs = [(20, 88, 0, 360, (0.35, 0.0, 0.14, 1.0))]
    M.spin3d(c, "star", front, back, cx, cy, segs, thick=40, lip=30, parent=body)


# ================================================================ 157 ❄️ star snowflake


@emoji("157-star-flake", "❄️", "снежинка, звёзды, xtc records, сигил, зима", "snowflake, stars, xtc records, sigil, winter",
       "снежинка из звёзд-контуров (6 лучей × 3): медленно проворачивается, заливка бежит волной от центра к краям и обратно",
       op=180, series=SER)
def star_flake(c):
    OP = 180
    cx, cy = 256, 256
    rr = M.wave(0, 0, 180, OP) if False else seq(0, [(0, 60, "lin"), (180, 60, "lin")]) if False else None
    ring = rig(c, "flake", (cx, cy), r=seq(0, [(180, 60, "lin")]))
    rings = [(0, 1, 40), (80, 6, 34), (154, 6, 28), (212, 6, 22)]
    for j, (rad, n, ro) in enumerate(rings):
        for k in range(n):
            a = math.radians(-90 + 360 * k / n)
            x, y = cx + rad * math.cos(a), cy + rad * math.sin(a)
            out = star_outline(x, y, ro, ro * 0.34)
            full = geo.star(x, y, ro, ro * 0.42, 5, -90)
            t = 30 + j * 18
            so = Track(100, 0)
            fo = Track(0, 0)
            for tr_, on in ((so, 0), (fo, 100)):
                tr_.k[-1][2] = "hold"
                tr_.k.append([t, on, None])
                tr_.k[-1][2] = "hold"
                tr_.k.append([t + 60 - j * 4, 100 - on, None])
                tr_.loop(OP, "lin")
            part(c, f"o{j}{k}", out, ring, (x, y), o=so)
            part(c, f"f{j}{k}", full, ring, (x, y), o=fo)
    # 6 spokes joining the rings
    spokes = geo.U(*[geo.line([(cx + 40 * math.cos(math.radians(-90 + 60 * k)), cy + 40 * math.sin(math.radians(-90 + 60 * k))),
                               (cx + 206 * math.cos(math.radians(-90 + 60 * k)), cy + 206 * math.sin(math.radians(-90 + 60 * k)))], 12) for k in range(6)])
    part(c, "spokes", spokes, ring, (cx, cy))


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
