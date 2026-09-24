"""P1: faces 100-108 (kaomoji kit) and objects 109-114. Every motion scheme checked against specs/*.py
(no repeats); a brand motif (eyelet, ✦ glare, logo X, drips, split-flap) where it fits."""
import math

from shapely import affinity
from shapely.geometry import LineString

from specs.drop import brand_letter, brand_word, brand_x
from specs.faces import CX, CY, cyc, jitter, part, rig
from xtc import geo, kao as K, lot, motion as M
from xtc.geo import U, W
from xtc.lot import Split, Track, bez_y, ease_of
from xtc.reg import emoji

SERIES = "p1"


# ---------------------------------------------------------------- local helpers


def seq(v0, keys, lag=0, op=None, f=None, loop_ease="io"):
    """Track from (t, v, ease) keys; v=None holds until t; lag shifts every key."""
    f = f or (lambda v: v)
    tr = Track(f(v0), 0)
    for t, v, e in keys:
        if v is None:
            tr.hold(t + lag)
        else:
            tr.to(t + lag, f(v), e)
    if op is not None:
        tr.loop(op, loop_ease)
    return tr


def steps(v0, keys, op=None):
    """stepped (hold-key) track for visibility swaps. rlottie also draws a layer on its op frame."""
    tr = Track(v0, 0)
    for t, v in keys:
        tr.k[-1][2] = "hold"
        tr.k.append([t, v, None])
    if op is not None and abs(tr.t - op) > 1e-6:
        tr.k[-1][2] = "hold"                 # close the loop with a step, not a ramp
        tr.k.append([op, v0, None])
    return tr


def clip_loop(tr, op):
    tr.k = [k for k in tr.k if k[0] < op - 0.5]
    tr.k[-1][2] = None
    return tr.loop(op)


def breathe(tr, t0, t1, base, amp=1.0, per=30):
    tr.hold(t0)
    t, k = t0, 0
    while t + per / 2 <= t1 - per / 2 + 1e-6:
        t += per / 2
        sgn = 1 if k % 2 == 0 else -1
        tr.to(t, [b * (1 + sgn * amp / 100) for b in base], "io")
        k += 1
    return tr


def poly_path(pts):
    return lot.pathdata(pts, True)


def smooth(pts, tens=None, closed=True):
    n = len(pts)
    ins, outs = [], []
    for i in range(n):
        a, b = pts[i - 1], pts[(i + 1) % n]
        k = (tens[i] if tens else 1.0) / 6
        tx, ty = (b[0] - a[0]) * k, (b[1] - a[1]) * k
        outs.append((tx, ty))
        ins.append((-tx, -ty))
    return lot.pathdata(pts, closed, ins, outs)


def null(c, nm, anchor, parent=None, p=None, s=None, r=None):
    return c.null(nm, parent=parent, p=p if p is not None else anchor, a=anchor,
                  s=s if s is not None else (100, 100), r=r if r is not None else 0)


def ypos(tr):
    """a 1D y-offset track as a 2D [0, y] position track (group transforms take no split position)."""
    out = Track([0, tr.k[0][1]], 0)
    out.k = [[t, [0, v], e] for t, v, e in tr.k]
    return out


def hole_path(layer, path, nm="hole", **t):
    layer.shapes[0]["it"].insert(0, lot.group([lot.sh(path, nm)], nm=nm, **t))
    return layer


def t_cross(t0, t1, v0, v1, ease, target):
    e = ease_of(ease)
    lo, hi = 0.0, 1.0
    up = v1 > v0
    for _ in range(50):
        m = (lo + hi) / 2
        if (v0 + (v1 - v0) * bez_y(e, m) < target) == up:
            lo = m
        else:
            hi = m
    return t0 + (t1 - t0) * (lo + hi) / 2


# ================================================================ 100 😤


@emoji("100-huff", "😤", "фух, пфф, выдохнул, гордо, злюсь, фыркаю", "huff, triumph, pff, steaming, proud, annoyed",
       ">_< набирает воздух — морда раздувается и поднимается, держит — «пфф!»: из ноздрей-люверсов бьют две струи пара, морду подбрасывает отдачей, второй короткий фырк",
       op=120, series=SERIES)
def huff(c):
    OP = 120
    # inhale (swell up), hold with a tremble, huff = recoil upward like a jet, settle; a small second huff
    y = seq(0.0, [(8, None, None), (28, -16, "io"), (38, None, None), (42, -44, "o5"), (58, 4, "io"), (66, 0, "io"),
                  (74, None, None), (76, -14, "o5"), (86, 0, "io")], f=lambda v: CY + v)
    y.loop(OP)
    s = seq([100, 100], [(8, None, None), (28, [105, 108], "io"), (38, None, None), (41, [110, 90], "o5"), (48, [96, 104], "io"),
                         (56, [101, 99], "io"), (64, [100, 100], "io"), (74, None, None), (76, [104, 96], "o"), (82, [100, 100], "io")])
    breathe(s, 92, 120, [100, 100], 0.8, 14)
    s.loop(OP)
    px = seq(float(CX), [(28, None, None)])
    jitter(px, 28, 38, float(CX), 2.2, 2)
    px.loop(OP)
    face = rig(c, p=Split(px, y), s=s)
    for i, (x, d) in enumerate(((CX - 112, 1), (CX + 112, -1))):
        by = seq(0.0, [(8, None, None), (28, -12, "io"), (38, None, None), (41, 8, "o5"), (56, 0, "io")], op=OP,
                 f=lambda v: 150 + v)
        part(c, f"brow{i}", K.brow(x, 150, 140, ang=d * 22, w=40), face, (x, 150), p=Split(x, by))
        es = seq([100, 100], [(8, None, None), (28, [104, 70], "io"), (38, None, None), (41, [110, 40], "o5"),
                              (56, [100, 100], "io"), (74, None, None), (76, [104, 60], "o"), (84, [100, 100], "io")], op=OP)
        part(c, f"eye{i}", K.chevron(x, 222, 120, d=d, open_=0.72), face, (x + d * 26, 222), s=es)
    ms = seq([100, 100], [(8, None, None), (28, [80, 110], "io"), (38, None, None), (41, [120, 80], "o5"),
                          (56, [100, 100], "io")], op=OP)
    part(c, "mouth", K.m_frown(CX, 386, 120, 40, 40), face, (CX, 386), s=ms)
    # nostrils: two eyelets that flare on each huff
    for i, x in enumerate((CX - 26, CX + 26)):
        ns = seq([100, 100], [(8, None, None), (28, [80, 80], "io"), (38, None, None), (41, [138, 138], "snap"),
                              (52, [100, 100], "io"), (74, None, None), (76, [124, 124], "snap"), (84, [100, 100], "io")], op=OP)
        part(c, f"nostril{i}", K.eyelet(x, 306, 24, 0.4), face, (x, 306), s=ns)
    # steam jets: puffs blast sideways out of the nostrils (above the mouth), growing and thinning out
    for side, sgn in enumerate((-1, 1)):
        x0 = CX + sgn * 46
        for k in range(3):
            t0 = 40 + 3 * k + side
            x1, y1 = CX + sgn * (118 + 26 * k), 332 - 30 * k
            M.particle(c, f"puff{side}{k}", K.steam(x0, 312, 78 - 8 * k, d=sgn), t0, 28, (x0, 312), (x1, y1), None,
                       anchor=(x0, 312), pop=0.1, fade=0.5, fall="o5", xease="o5", s_peak=104 + 14 * k)
        M.particle(c, f"snort{side}", K.steam(x0, 312, 64, d=sgn), 76 + side, 22, (x0, 312), (CX + sgn * 150, 330), None,
                   anchor=(x0, 312), pop=0.15, fade=0.55, fall="o5", xease="o5", s_peak=96)


# ================================================================ 101 🤨


@emoji("101-raised-brow", "🤨", "хм, серьёзно?, подозрительно, ну-ну, сомневаюсь", "raised eyebrow, really?, suspicious, hmm, doubt",
       "¬_O: левый глаз щурится, правая бровь рывками ползёт вверх — тик, тик, ТИК, глаз-люверс под ней раздувается, морда кренится и присматривается вбок, бровь падает",
       op=120, series=SERIES)
def raised_brow(c):
    OP = 120
    lx, rx = CX - 116, CX + 112
    r = seq(0, [(36, None, None), (42, 7, "o5"), (52, 5, "io"), (62, 8, "io"), (76, None, None), (86, 0, "io")], op=OP)
    px = seq(float(CX), [(36, None, None), (42, CX + 20.0, "o5"), (54, CX + 8.0, "io"), (66, CX + 22.0, "io"),
                         (76, None, None), (88, float(CX), "io")], op=OP)
    s = seq([100, 100], [(36, None, None), (40, [104, 97], "o"), (46, [100, 100], "io"), (84, None, None),
                         (87, [104, 96], "o"), (94, [100, 100], "io")])
    breathe(s, 96, 120, [100, 100], 0.7, 12)
    s.loop(OP)
    face = rig(c, p=Split(px, CY), s=s, r=r)
    # the suspicious squint (left) and the flat brow above it
    ls = seq([100, 100], [(36, None, None), (40, [104, 80], "o"), (48, [100, 90], "io"), (76, None, None),
                          (86, [100, 100], "io")], op=OP)
    part(c, "eyeL", K.neg(lx, 214, 136, d=-1), face, (lx, 214), s=ls)
    # the right brow ratchets up in three ticks (fast 3f snaps held between), then drops
    by = seq(150.0, [(12, None, None), (15, 134.0, "snap"), (24, None, None), (27, 116.0, "snap"), (36, None, None),
                     (40, 82.0, "snap"), (44, 90.0, "io"), (76, None, None), (82, 156.0, "i5"), (86, 146.0, "o"), (92, 150.0, "io")],
             op=OP)
    br = seq(-4, [(12, None, None), (15, -8, "snap"), (27, -12, "snap"), (40, -20, "snap"), (44, -16, "io"),
                  (76, None, None), (86, -4, "io")], op=OP)
    part(c, "browR", K.brow(rx, 150, 132, ang=-4, w=40), face, (rx, 150), p=Split(rx, by), r=br)
    es = seq([100, 100], [(12, None, None), (15, [108, 108], "snap"), (19, [104, 104], "io"), (27, [116, 116], "snap"),
                          (31, [112, 112], "io"), (40, [132, 132], "snap"), (46, [122, 122], "io"), (76, None, None),
                          (84, [94, 94], "io"), (92, [100, 100], "io")], op=OP)
    part(c, "eyeR", K.eyelet(rx, 232, 56, 0.44), face, (rx, 232), s=es)
    ms = seq([100, 100], [(36, None, None), (42, [86, 100], "o"), (76, None, None), (86, [100, 100], "io")], op=OP)
    mr = seq(-8, [(36, None, None), (42, -14, "o"), (76, None, None), (86, -8, "io")], op=OP)
    part(c, "mouth", K.m_line(CX + 6, 372, 120, 40), face, (CX + 6, 372), s=ms, r=mr)


# ================================================================ 102 🤐


@emoji("102-zipper-mouth", "🤐", "молчу, рот на замке, секрет, никому, тсс", "zipper mouth, secret, my lips are sealed, shh, quiet",
       "бегунок молнии проезжает по открытому рту — зубцы защёлкиваются по одному, глаза следят за ним; щёлк, язычок с люверсом качается; морда мычит — молния натягивается, но держит; расстёгивается обратно",
       op=150, series=SERIES)
def zipper(c):
    OP = 150
    face = rig(c, s=seq([100, 100], [(88, None, None), (92, [104, 97], "o"), (96, [98, 103], "io"), (100, [104, 97], "o"),
                                       (104, [98, 103], "io"), (108, [104, 97], "o"), (114, [100, 100], "io")], op=OP))
    n, x0, dx = 8, 138, 34
    zy = 356
    t_close = [22 + 3.4 * i for i in range(n)]          # the slider passes tooth i
    t_open = [124 + 2.6 * (n - 1 - i) for i in range(n)]
    for i in range(n):
        xt = x0 + i * dx
        top = geo.rrect(xt - 15, zy - 44, xt + 15, zy - 2, 9)
        bot = geo.rrect(xt + 2, zy + 2, xt + 32, zy + 44, 9)
        # closed = rows pushed 12px into each other (interlocked band); open = 20px apart
        gap = lambda sgn: seq(sgn * 20.0, [(t_close[i], None, None), (t_close[i] + 4, sgn * -15.0, "o5"),
                                           (t_close[i] + 7, sgn * -12.0, "io"), (88, None, None), (92, sgn * -7.0, "o"),
                                           (100, sgn * -13.0, "io"), (108, sgn * -7.0, "o"), (114, sgn * -12.0, "io"),
                                           (t_open[i], None, None), (t_open[i] + 5, sgn * 20.0, "o")], op=OP)
        pt, pb = ypos(gap(-1)), ypos(gap(1))
        c.layer(f"tooth{i}", [lot.group(geo.paths(top), nm="t", p=pt, a=(0, 0)), lot.group(geo.paths(bot), nm="b", p=pb, a=(0, 0)),
                              lot.fill()], parent=face, p=(0, 0), a=(0, 0))
    # the slider rides the teeth; its pull tab (with an eyelet) swings from a hinge
    xs = seq(112.0, [(20, None, None), (22 + 3.4 * n, x0 + n * dx + 6.0, (0.3, 0.0, 0.5, 1.0)), (121, None, None),
                     (124 + 2.6 * n + 2, 112.0, (0.4, 0.0, 0.3, 1.0))], op=OP)
    sl = null(c, "slider", (112, zy), parent=face, p=Split(xs, zy))
    part(c, "body", geo.rrect(82, zy - 36, 142, zy + 36, 18), sl, (112, zy))
    tab = geo.rrect(94, zy + 26, 130, zy + 104, 16).difference(geo.disc(112, zy + 80, 12, 10))
    sw = seq(0, [(20, None, None), (26, 26, "o"), (48, 14, "io"), (52, -32, "o5"), (60, 24, "io"), (68, -15, "io"),
                 (76, 9, "io"), (84, -4, "io"), (92, 0, "io"), (121, None, None), (126, -22, "o"), (140, 8, "io"),
                 (150, 0, "io")])
    part(c, "tab", tab, sl, (112, zy + 26), r=sw)
    # eyes follow the slider, pop on the click, squeeze while mumbling
    for i, x in enumerate((CX - 108, CX + 108)):
        ex = seq(-12.0, [(20, None, None), (50, 14.0, "io"), (121, None, None), (140, -12.0, "io")], op=OP, f=lambda v: x + v)
        es = seq([100, 100], [(50, None, None), (53, [124, 124], "snap"), (60, [100, 100], "io"), (88, None, None),
                              (92, [110, 60], "o"), (100, [104, 80], "io"), (108, [110, 60], "o"), (116, [100, 100], "io")], op=OP)
        part(c, f"eye{i}", K.dot(x, 206, 40), face, (x, 206), p=Split(ex, 206), s=es)
    M.twinkle(c, "tw", 430, 300, 30, 52, 20)


# ================================================================ 103 🥱


def _ell(x, y, rx, ry, n=32):
    return [(x + rx * math.cos(2 * math.pi * i / n), y + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


@emoji("103-yawn", "🥱", "зевок, скучно, спать хочу, устал, ааам", "yawn, bored, sleepy, tired, meh",
       "сонные глаза жмурятся, рот-люверс медленно растягивается в огромное О, голова откидывается, из уголка глаза выжимается слеза — «ам!» — рот схлопывается в волну, веки падают",
       op=150, series=SERIES)
def yawn(c):
    OP = 150
    my = 352
    # head: tilts back and rises through the yawn, snaps forward on the "am", droops
    r = seq(0, [(16, None, None), (54, -12, "io"), (70, -13, "io"), (74, 3, "o5"), (84, -1, "io"), (92, 0, "io")], op=OP)
    y = seq(0.0, [(16, None, None), (54, -18, "io"), (70, -20, "io"), (74, 6, "o5"), (86, 0, "io")], f=lambda v: CY + v)
    y.loop(OP)
    s = seq([100, 100], [(16, None, None), (54, [98, 104], "io"), (70, [98, 105], "io"), (74, [106, 94], "o5"),
                         (84, [99, 101], "io"), (92, [100, 100], "io")])
    breathe(s, 100, 150, [100, 100], 0.8, 24)
    s.loop(OP)
    face = rig(c, p=Split(CX, y), s=s, r=r)
    # eyes: sleepy dashes that squeeze shut (tilted) during the yawn, open droopy, slow blink
    for i, (x, d) in enumerate(((CX - 112, 1), (CX + 112, -1))):
        es = seq([100, 100], [(20, None, None), (48, [108, 40], "io"), (70, None, None), (78, [100, 100], "io"),
                              (120, None, None), (126, [104, 30], "io"), (134, [100, 100], "io")], op=OP)
        er = seq(0, [(20, None, None), (48, -d * 12, "io"), (70, None, None), (78, 0, "io")], op=OP)   # inner ends up
        part(c, f"eye{i}", K.dash(x, 214, 124), face, (x, 214), s=es, r=er)
    # the mouth: a thick eyelet ring whose outer/inner ellipses morph separately (the rim keeps its weight)
    ring_path = lambda rx, ry: [poly_path(_ell(CX, my, rx, ry)), poly_path(_ell(CX, my, max(rx - 40, 6), max(ry - 40, 6)))]
    small, big = ring_path(48, 44), ring_path(96, 132)
    o_tr = Track(small[0], 0).hold(18).to(56, big[0], "io").hold(68).to(74, small[0], "i5")
    i_tr = Track(small[1], 0).hold(18).to(56, big[1], "io").hold(68).to(74, small[1], "i5")
    o_tr.hold(OP)
    i_tr.hold(OP)
    ms = seq([100, 100], [(56, None, None), (58, [103, 97], "io"), (60, [97, 103], "io"), (62, [103, 97], "io"),
                          (64, [98, 102], "io"), (66, [100, 100], "io")], op=OP)
    mo = steps(0, [(16, 100), (74, 0)], OP)
    c.layer("mouthO", [lot.group([lot.sh(o_tr, "o"), lot.sh(i_tr, "i"), lot.fill()], nm="mouthO")], parent=face,
            p=(CX, my), a=(CX, my), s=ms, o=mo)
    # rest mouth: a little wave that chews after the "am"
    wo = steps(100, [(16, 0), (74, 100)], OP)
    ws = seq([100, 100], [(74, None, None), (78, [118, 80], "o"), (84, [88, 110], "io"), (90, [110, 90], "io"),
                          (96, [96, 104], "io"), (102, [100, 100], "io")], op=OP)
    part(c, "mouthW", K.m_wave(CX, my, 120, 12, 36), face, (CX, my), s=ws, o=wo)
    # a tear squeezed out of the eye corner rolls down the cheek
    M.particle(c, "tear", K.tear(CX - 176, 236, 20), 58, 40, (CX - 176, 236), (CX - 190, 420), None, parent=face,
               anchor=(CX - 176, 236), pop=0.2, fade=0.3, fall="i", s_peak=100)


# ================================================================ 104 🤤


def drip_shape(x, y0, y1, w=36, bulb=None):
    bulb = bulb or w * 0.7
    return U(geo.line([(x, y0), (x, y1 - bulb * 0.5)], w, "round"), geo.disc(x, y1 - bulb, bulb, 14))


@emoji("104-drool", "🤤", "слюнки, хочу, вкусняшка, мечтаю, ммм", "drool, want, yummy, craving, dreamy",
       "^ ^ мечтательно покачивается, из уголка рта набухает подтёк-слюна, тянется до низа и качается, истончается почти до обрыва — «шлюрп!» втягивается обратно, глаза распахиваются",
       op=150, series=SERIES)
def drool(c):
    OP = 150
    r = seq(0, [(8, 4, "io"), (40, -4, "io"), (72, 4, "io"), (88, None, None), (92, -3, "o5"), (104, 0, "io")], op=OP)
    y = seq(0.0, [(88, None, None), (92, -14, "o5"), (100, 3, "io"), (108, 0, "io")], f=lambda v: CY + v)
    y.loop(OP)
    s = seq([100, 100], [(88, None, None), (92, [95, 106], "o5"), (100, [102, 98], "io"), (108, [100, 100], "io")])
    breathe(s, 110, 150, [100, 100], 0.8, 20)
    s.loop(OP)
    face = rig(c, p=Split(CX, y), s=s, r=r)
    for i, x in enumerate((CX - 112, CX + 112)):
        eo = steps(100, [(90, 0), (104, 100)], OP)
        part(c, f"eye{i}", K.caret(x, 212, 132, h=0.62), face, (x, 212), o=eo)
        do = steps(0, [(90, 100), (104, 0)], OP)
        ds = seq([60, 60], [(90, None, None), (93, [118, 118], "snap"), (100, [100, 100], "io")], op=OP)
        part(c, f"pop{i}", K.dot(x, 212, 36), face, (x, 212), s=ds, o=do)
    ms = seq([100, 100], [(88, None, None), (91, [70, 60], "i5"), (96, [110, 90], "o"), (104, [100, 100], "io")], op=OP)
    part(c, "mouth", K.m_smile(CX - 10, 344, 176, 58), face, (CX - 10, 344), s=ms)
    # the drool: hangs from the right corner; grows, swings, thins, snaps back up
    cx0, cy0 = CX + 64, 338
    g = drip_shape(cx0, cy0, 480, 42, bulb=30)
    ds = seq([100, 8], [(10, None, None), (70, [100, 100], (0.45, 0.0, 0.3, 1.0)), (78, [92, 102], "io"),
                        (84, [72, 103], "io"), (88, [70, 102], "io"), (93, [120, 6], "i5"), (98, [100, 10], "o"),
                        (150, [100, 8], "io")])
    dr = seq(0, [(40, None, None), (56, 7, "io"), (66, -6, "io"), (76, 4, "io"), (86, -2, "io"), (93, 0, "io")], op=OP)
    part(c, "drool", g, face, (cx0, cy0), s=ds, r=dr)
    M.twinkle(c, "tw", 400, 150, 32, 96, 22)


# ================================================================ 105 🤓


@emoji("105-nerd", "🤓", "ботан, умник, вообще-то, факт, задрот", "nerd, actually, smart, geek, well actually",
       "очки-люверсы сползают по носу — глаза выглядывают поверх оправы, морда морщится и подкидывает очки: щёлк на место, линзы вспыхивают глухим бликом (глаз не видно), ✦ на оправе, зубы-зайчик",
       op=120, series=SERIES)
def nerd(c):
    OP = 120
    ey = 212
    s = seq([100, 100], [(38, None, None), (42, [106, 94], "io"), (46, [97, 104], "o5"), (54, [100, 100], "io")])
    breathe(s, 76, 120, [100, 100], 0.7, 22)
    s.loop(OP)
    face = rig(c, s=s, r=seq(0, [(10, None, None), (36, 4, "io"), (46, -2, "o5"), (56, 0, "io")], op=OP))
    # pupils stay put while the glasses slide: they end up peeking over the rims
    for i, x in enumerate((CX - 104, CX + 104)):
        po = steps(100, [(46, 0), (72, 100)], OP)
        py = seq(0.0, [(10, None, None), (36, -6, "io"), (46, 0, "o5")], op=OP, f=lambda v: ey + v)
        part(c, f"pupil{i}", K.dot(x, ey, 30), face, (x, ey), p=Split(x, py), o=po)
    # glasses: two fat rings + bridge + temples; slide down, pushed back up with a snap
    rings = U(geo.ring(CX - 104, ey, 82, 50, 24), geo.ring(CX + 104, ey, 82, 50, 24),
              geo.brush([(CX - 26, ey - 8), (CX, ey - 20), (CX + 26, ey - 8)], 26, taper=(1, 1), smooth=True, n=4),
              geo.line([(CX - 184, ey - 10), (CX - 214, ey - 24)], 26), geo.line([(CX + 184, ey - 10), (CX + 214, ey - 24)], 26))
    gy = seq(0.0, [(10, None, None), (36, 44, "io"), (40, 48, "io"), (44, -10, "o5"), (50, 3, "io"), (56, 0, "io")],
             op=OP, f=lambda v: ey + v)
    gl = null(c, "glasses", (CX, ey), parent=face, p=Split(CX, gy))
    part(c, "frames", rings, gl, (CX, ey))
    # anime glint: the lenses go blank, two diagonal glare streaks pop in each lens
    for i, x in enumerate((CX - 104, CX + 104)):
        st = U(geo.line([(x - 30, ey + 16), (x + 4, ey - 26)], 16), geo.line([(x + 2, ey + 26), (x + 30, ey - 8)], 12))
        so = seq([0, 0], [(45, None, None), (48, [120, 120], "o5"), (54, [100, 100], "io"), (70, None, None),
                          (74, [0, 0], "i")], op=OP, loop_ease="lin")
        part(c, f"glare{i}", st, gl, (x, ey), s=so)
    M.twinkle(c, "tw", CX + 184, ey - 72, 34, 48, 24, parent=face)
    # buck-tooth grin: a filled grin with two tooth cut-outs, widening on the push
    grin = geo.poly([(CX - 96, 336)] + geo.arc(CX, 332, 96, 0, 180, 20)[::-1] + [(CX + 96, 336)]).buffer(10).buffer(-10)
    grin = geo.U(grin, geo.rect(CX - 96, 322, CX + 96, 346)).buffer(12).buffer(-12)
    teeth = U(geo.rrect(CX - 34, 330, CX - 3, 372, 8), geo.rrect(CX + 3, 330, CX + 34, 372, 8))
    ms = seq([100, 100], [(40, None, None), (46, [114, 104], "o5"), (56, [100, 100], "io")], op=OP)
    part(c, "grin", grin.difference(teeth), face, (CX, 336), s=ms)


# ================================================================ 106 🥴


@emoji("106-woozy", "🥴", "пьяненький, поплыл, окосел, хорошо сидим, ик", "woozy, tipsy, drunk, dizzy, hic",
       "морда плывёт: глаз-люверс и прищур, рот-волна — части раскачиваются с разным запаздыванием, как желе; «ик!» — подскок, глаза меняются местами, изо рта вылетает пузырь-люверс и лопается",
       op=120, series=SERIES)
def woozy(c):
    OP = 120
    hic = [(62, None, None), (65, -34, "o5"), (72, 4, "i"), (78, 0, "io"), (104, None, None), (107, -18, "o5"),
           (112, 2, "i"), (116, 0, "io")]

    def drift(phase, amp_r=7.0, amp_x=16.0):
        r = M.wave(0.0, amp_r, 60, OP, phase)
        x = M.wave(float(CX), amp_x, 60, OP, phase + math.pi / 2)
        y = seq(0.0, hic, op=OP, f=lambda v: CY + v)
        return r, Split(x, y)

    # each feature swings on the same slow wave, but late by its own phase: the face "floats apart"
    r, p = drift(0.0)
    eyes = rig(c, "eyes", p=p, r=r)
    r2, p2 = drift(-0.9, 9.0, 22.0)
    mouth = rig(c, "mouthrig", p=p2, r=r2)
    lx, rx, ey = CX - 112, CX + 112, 214
    # uneven eyes, swapping on the hiccup
    a_o, b_o = steps(100, [(65, 0), (107, 100)], OP), steps(0, [(65, 100), (107, 0)], OP)
    part(c, "eyeL1", K.eyelet(lx, ey, 64, 0.46), eyes, (lx, ey), o=a_o)
    part(c, "eyeR1", K.dash(rx, ey + 6, 118, tilt=-14), eyes, (rx, ey), o=a_o)
    part(c, "eyeL2", K.dash(lx, ey + 6, 118, tilt=14), eyes, (lx, ey), o=b_o)
    part(c, "eyeR2", K.eyelet(rx, ey, 64, 0.46), eyes, (rx, ey), o=b_o)
    ms = seq([100, 100], [(62, None, None), (64, [80, 150], "o5"), (70, [110, 80], "io"), (78, [100, 100], "io"),
                          (104, None, None), (106, [90, 124], "o5"), (112, [100, 100], "io")], op=OP)
    part(c, "mouth", K.m_wave(CX, 356, 170, 18, 40), mouth, (CX, 356), s=ms, r=seq(-8, [], op=None))
    # the hiccup bubble: an eyelet floats up out of the mouth, wobbles, pops into four dots
    bx, by = CX + 40, 330
    bub = K.eyelet(bx, by, 46, 0.62)
    bs = seq([0, 0], [(64, None, None), (70, [104, 104], "ox"), (76, [96, 102], "io"), (84, [102, 96], "io"),
                      (92, [100, 100], "io"), (96, [130, 130], "o"), (98, [0, 0], "i")], op=OP, loop_ease="lin")
    bpx = seq(float(bx), [(64, None, None), (98, bx + 70.0, "os")], op=OP, loop_ease="lin")
    bpy = seq(float(by), [(64, None, None), (98, 120.0, "decel")], op=OP, loop_ease="lin")
    part(c, "bubble", bub, None, (bx, by), p=Split(bpx, bpy), s=bs, ip=64, op=99)
    for k, (dx_, dy_) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        x0, y0 = bx + 70, 120
        M.particle(c, f"pop{k}", geo.disc(x0, y0, 14), 97, 12, (x0, y0), (x0 + dx_ * 50, y0 + dy_ * 44), None,
                   anchor=(x0, y0), fall="o5", xease="o5", pop=0.2, fade=0.5)


# ================================================================ 107 🤗


def _arm(pivot, length, w=58, mitt=46):
    x, y = pivot
    hand = (x, y - length)
    g = U(geo.line([pivot, hand], w, "round"), geo.disc(hand[0], hand[1], mitt, 16))
    thumb = geo.disc(hand[0] + (mitt * 0.8 if x < CX else -mitt * 0.8), hand[1] + mitt * 0.35, mitt * 0.42, 10)
    return U(g, thumb)


@emoji("107-hug", "🤗", "обнимаю, обнимашки, люблю, иди сюда, спасибо", "hug, hugs, love, come here, thanks",
       "^‿^ раскидывает руки-варежки широко (антиципация) — сгребает: руки смыкаются крест-накрест в X, морду сжимает объятием, покачивается, ✦; отпускает",
       op=120, series=SERIES)
def hug(c):
    OP = 120
    rock = seq(0, [(36, None, None), (46, 4, "io"), (56, -4, "io"), (66, 3, "io"), (74, 0, "io")], op=OP)
    s = seq([100, 100], [(10, None, None), (24, [96, 104], "io"), (32, [108, 93], "o5"), (40, [103, 97], "io"),
                         (70, None, None), (78, [98, 102], "io"), (86, [100, 100], "io")])
    breathe(s, 90, 120, [100, 100], 0.8, 15)
    s.loop(OP)
    face = rig(c, p=(CX, 240), s=s, r=rock)
    for i, x in enumerate((CX - 88, CX + 88)):
        es = seq([100, 100], [(28, None, None), (32, [112, 70], "o5"), (70, None, None), (78, [100, 100], "io")], op=OP)
        part(c, f"eye{i}", K.caret(x, 172, 112, h=0.6), face, (x, 172), s=es)
    ms = seq([100, 100], [(10, None, None), (24, [110, 120], "io"), (32, [90, 110], "o5"), (70, None, None),
                          (78, [100, 100], "io")], op=OP)
    part(c, "mouth", K.m_smile(CX, 282, 150, 46, 40), face, (CX, 282), s=ms)
    # arms from shoulder pivots at the bottom corners: up beside the face -> spread -> scoop into an X -> release
    for j, sgn in enumerate((-1, 1)):
        piv = (CX + sgn * 150, 452)
        ang = [(0, -11, "io"), (6, None, None), (12, -5, "io"), (18, -10, "io"), (24, -14, "io"), (32, 60, "io3"),
               (36, 52, "o"), (44, 56, "io"), (70, None, None), (80, -14, "o"), (88, -6, "io"), (96, -11, "io"),
               (104, None, None), (110, -7, "io"), (116, -11, "io")]
        r = seq(-11.0, ang[1:], f=lambda v: -sgn * v)
        r.loop(OP)
        lay = part(c, f"arm{j}", _arm(piv, 218, 54, 42), None, piv, r=r)
    M.twinkle(c, "tw", CX, 250, 44, 34, 24)
    M.twinkle(c, "tw2", CX + 150, 110, 30, 44, 22)


# ================================================================ 108 😋


@emoji("108-yum", "😋", "вкусно, ням, облизываюсь, мм, объедение", "yum, yummy, delicious, tasty, lick",
       "^▽^ облизывается: язык выползает из уголка и обводит губу дугой туда и обратно, «чпок» — прячется, щёки вспыхивают ✦ по очереди, морда жмурится и покачивается",
       op=120, series=SERIES)
def yum(c):
    OP = 120
    r = seq(0, [(56, None, None), (62, 6, "io"), (70, -5, "io"), (78, 4, "io"), (86, -2, "io"), (94, 0, "io")], op=OP)
    s = seq([100, 100], [(54, None, None), (57, [106, 94], "o"), (64, [98, 102], "io"), (72, [100, 100], "io")])
    breathe(s, 96, 120, [100, 100], 0.8, 12)
    s.loop(OP)
    face = rig(c, s=s, r=r)
    for i, x in enumerate((CX - 108, CX + 108)):
        es = seq([100, 100], [(54, None, None), (57, [110, 60], "o"), (66, [104, 80], "io"), (90, None, None),
                              (98, [100, 100], "io")], op=OP)
        part(c, f"eye{i}", K.caret(x, 196, 132, h=0.66), face, (x, 196), s=es)
    part(c, "mouth", K.m_smile(CX, 336, 184, 50, 42), face, (CX, 336))
    # the tongue: hangs out of the right corner (😋), then licks round the mouth like a wiper (pivot = mouth
    # centre): up over the right corner, across the upper lip, down the left corner and back, "pop"
    mc = (CX, 330)
    tongue = U(geo.rect(CX - 32, mc[1] + 34, CX + 32, mc[1] + 96), geo.disc(CX, mc[1] + 96, 32, 14))
    tongue = tongue.difference(geo.line([(CX, mc[1] + 50), (CX, mc[1] + 100)], 10))
    tr = seq(-38, [(12, None, None), (18, -30, "io"), (34, -176, "io"), (44, -300, "io"), (52, -250, "io"),
                   (58, -38, (0.3, 0.0, 0.2, 1.0))], op=OP)
    ts = seq([100, 100], [(12, None, None), (18, [104, 90], "io"), (34, [100, 110], "io"), (44, [100, 104], "io"),
                          (58, [100, 100], "io"), (60, [112, 86], "o"), (66, [100, 100], "io")], op=OP)
    part(c, "tongue", tongue, face, mc, s=ts, r=tr)
    M.twinkle(c, "tw1", CX - 170, 280, 34, 58, 20, parent=face)
    M.twinkle(c, "tw2", CX + 170, 280, 34, 66, 20, parent=face)


# ================================================================ 109 💸

BILL_W, BILL_H = 392, 160


def _bill(cx, cy, w=BILL_W, h=BILL_H):
    b = geo.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 24)
    b = b.difference(geo.ellipse(cx, cy, 78, 56, 20))
    b = b.difference(geo.disc(cx - w / 2 + 52, cy, 20, 10)).difference(geo.disc(cx + w / 2 - 52, cy, 20, 10))
    return b.union(brand_x(cx, cy, 84, 50, bold=10))


@emoji("109-bills", "💸", "деньги улетают, трачу, зарплата всё, дорого, плачу", "money flying, spending, broke, expensive, paying",
       "пачка купюр XTC: верхняя отгибается углом, складывается пополам и улетает, махая половинками как крыльями; за ней вторая и третья — пачка тает, потом «бррр» пересчёт, и она снова толстая с ✦-бликом",
       op=150, series=SERIES)
def bills(c):
    OP = 150
    cx, y0, pitch = 256, 300, 26
    starts = (12, 36, 60)
    # edge stripes of the pack (hidden while the top bill sits on them), bottom first
    st0 = y0 + BILL_H / 2 + 4
    for k in (3, 2, 1, 0):
        y = st0 + pitch * k
        g = geo.rrect(cx - BILL_W / 2 + 6, y, cx + BILL_W / 2 - 6, y + 22, 10)
        part(c, f"edge{k}", g, None, (cx, y + 11), s=None if k == 3 else steps([100, 100], [(starts[k] + 4, [0, 0]), ((104, 110, 116)[2 - k], [100, 100])], op=OP))
    # the pack's top bill: drops a notch as each bill leaves; «brrr» recount climbs back in three snaps
    fy = seq(float(y0), [(starts[0] + 4, None, None), (starts[0] + 10, y0 + pitch * 1.0, "slam"),
                         (starts[1] + 4, None, None), (starts[1] + 10, y0 + pitch * 2.0, "slam"),
                         (starts[2] + 4, None, None), (starts[2] + 10, y0 + pitch * 3.0, "slam"),
                         (104, None, None), (107, y0 + pitch * 2.0, "snap"), (110, None, None), (113, y0 + pitch * 1.0, "snap"),
                         (116, None, None), (119, float(y0), "snap")], op=OP)
    fx = seq(float(cx), [(100, None, None)])
    jitter(fx, 100, 120, float(cx), 5, 2)
    fx.loop(OP)
    fs = seq([100, 100], [(119, None, None), (122, [104, 95], "o"), (128, [100, 100], "io")])
    breathe(fs, 128, 150, [100, 100], 0.8, 22)
    fs.loop(OP)
    part(c, "top", _bill(cx, y0), None, (cx, y0), p=Split(fx, fy), s=fs)
    M.twinkle(c, "tw", cx + BILL_W / 2 - 8, y0 - BILL_H / 2 - 8, 46, 119, 24)
    # three bills take off: right half peels up, then both halves beat like wings, shrinking away
    for k, (t0, x1, y1, bank) in enumerate(zip(starts, (388, 126, 262), (124, 112, 100), (-12, 12, -4))):
        ys = y0 + pitch * k
        g = _bill(cx, ys)
        L = g.intersection(geo.rect(0, 0, cx + 2, 512))
        R = g.intersection(geo.rect(cx - 2, 0, 512, 512))
        thL = seq(0, [(t0 + 6, None, None), (t0 + 12, 26, "o")])
        cyc(thL, t0 + 12, t0 + 40, -16, 28, 10)
        thL.to(t0 + 46, 0, "io")
        thR = seq(0, [(t0, None, None), (t0 + 6, -34, "o"), (t0 + 12, -26, "io")])
        cyc(thR, t0 + 12, t0 + 40, 16, -28, 10)
        thR.to(t0 + 46, 0, "io")
        grp = lambda h, th, nm: lot.group(geo.paths(h) + [lot.fill()], nm=nm, a=(cx, ys), p=(cx, ys), r=th)
        px = seq(float(cx), [(t0 + 6, None, None), (t0 + 34, float(x1), "io"), (t0 + 46, x1 + (x1 - cx) * 0.1, "os")])
        py = seq(float(ys), [(t0 + 6, ys - 16.0, "o"), (t0 + 34, float(y1), "decel"), (t0 + 46, y1 - 8.0, "io")])
        s = seq([100, 100], [(t0 + 6, [98, 100], "o"), (t0 + 30, [56, 56], "io"), (t0 + 40, [50, 50], "io"), (t0 + 46, [0, 0], "i")])
        r = seq(0, [(t0 + 6, -4, "o"), (t0 + 30, float(bank), "io"), (t0 + 46, bank * 1.6, "io")])
        c.layer(f"bill{k}", [grp(R, thR, "R"), grp(L, thL, "L")], p=Split(px, py), a=(cx, ys), s=s, r=r,
                ip=t0, op=t0 + 47)
