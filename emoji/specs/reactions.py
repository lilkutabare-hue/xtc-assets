"""P0 reactions 83-93: symbols with a 2-second story, in the XTC language
(eyelet = eye/dot, ✦ latex glare, drips, logo X, bass shake). Techniques M# = moodboard.md."""
import math

from shapely import affinity
from shapely.geometry import LineString
from shapely.ops import split as _split

from xtc import geo, lot, motion as M
from xtc.geo import U, W
from xtc.lot import Split, Track, bez_y, ease_of
from xtc.reg import emoji

CX = 256
SERIES = "react"


# ---------------------------------------------------------------- local helpers


def part(c, nm, g, parent=None, anchor=(CX, CX), p=None, s=None, r=None, o=100, ip=0, op=None, tol=0.45):
    return c.layer(nm, [geo.shape(g, nm=nm, tol=tol)], parent=parent, p=p if p is not None else anchor, a=anchor,
                   s=s if s is not None else (100, 100), r=r if r is not None else 0, o=o, ip=ip, op=op)


def rig(c, nm, anchor, parent=None, p=None, s=None, r=None, o=100):
    return c.null(nm, parent=parent, p=p if p is not None else anchor, a=anchor,
                  s=s if s is not None else (100, 100), r=r if r is not None else 0, o=o)


def seq(v0, keys, lag=0, op=None, f=None, loop_ease="io"):
    """Track from a list of (t, v, ease); v=None means hold until t. lag shifts every key."""
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


def stroke_line(pts, w, nm="line", s=0, e=100, **t):
    """open polyline, round caps, trim-path draw-on (s/e may be Tracks)."""
    items = [lot.sh(lot.pathdata(pts, closed=False), nm), lot.trim(s, e), lot.stroke(w)]
    return lot.group(items, nm=nm, **t)


def smooth(pts, tens=None):
    """closed Catmull-Rom as a Lottie bezier path with few vertices (morph-friendly: fixed count).
    tens[i] < 1 sharpens vertex i (flame tips)."""
    n = len(pts)
    ins, outs = [], []
    for i in range(n):
        a, b = pts[i - 1], pts[(i + 1) % n]
        k = (tens[i] if tens else 1.0) / 6
        tx, ty = (b[0] - a[0]) * k, (b[1] - a[1]) * k
        outs.append((tx, ty))
        ins.append((-tx, -ty))
    return lot.pathdata(pts, True, ins, outs)


def poly_path(pts):
    return lot.pathdata(pts, True)


def t_cross(t0, t1, v0, v1, ease, target):
    """time at which an eased segment v0->v1 passes target."""
    e = ease_of(ease)
    lo, hi = 0.0, 1.0
    up = v1 > v0
    for _ in range(50):
        m = (lo + hi) / 2
        v = v0 + (v1 - v0) * bez_y(e, m)
        if (v < target) == up:
            lo = m
        else:
            hi = m
    return t0 + (t1 - t0) * (lo + hi) / 2


def rot_pt(p, c, deg):
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def breathe(tr, t0, t1, base, amp=1.0, per=30):
    """micro-life in the rest part of the loop (99-101%)."""
    tr.hold(t0)
    t, k = t0, 0
    while t + per / 2 <= t1 - per / 2 + 1e-6:
        t += per / 2
        sgn = 1 if k % 2 == 0 else -1
        tr.to(t, [b * (1 + sgn * amp / 100) for b in base], "io")
        k += 1
    return tr


def brand_x(x, y, w, h, bold=9):
    """the logo X: Michroma, stretched like the longsleeve print."""
    return geo.text("X", geo.font("Michroma-Regular.ttf"), x, y, h, bold=bold, width=w)


def eyelet(x, y, ro, ri):
    return geo.ring(x, y, ro, ri, 20)


def _spark_ctrl(x, y, r, pinch, rot):
    c = (math.sqrt(2) * pinch - 0.5) * r
    tips = [(0, -r), (r, 0), (0, r), (-r, 0)]
    ctl = [(c, -c), (c, c), (-c, c), (-c, -c)]
    R = lambda p: (x + p[0] * math.cos(math.radians(rot)) - p[1] * math.sin(math.radians(rot)),
                   y + p[0] * math.sin(math.radians(rot)) + p[1] * math.cos(math.radians(rot)))
    return [R(p) for p in tips], [R(p) for p in ctl]


def spark4(x, y, r, pinch=0.3, rot=0):
    """✦ latex glare as 4 bezier vertices (tips) with concave quad sides; pinch = radius at 45° / r.
    Fixed vertex count -> morph-friendly."""
    tips, ctl = _spark_ctrl(x, y, r, pinch, rot)
    ins, outs = [], []
    for j in range(4):
        cin, cout = ctl[j - 1], ctl[j]
        outs.append(((cout[0] - tips[j][0]) * 2 / 3, (cout[1] - tips[j][1]) * 2 / 3))
        ins.append(((cin[0] - tips[j][0]) * 2 / 3, (cin[1] - tips[j][1]) * 2 / 3))
    return lot.pathdata(tips, True, ins, outs)


def spark_g(x, y, r, pinch=0.3, rot=0):
    """✦ as shapely (for particles / holes)."""
    tips, ctl = _spark_ctrl(x, y, r, pinch, rot)
    pts = []
    for j in range(4):
        pts += geo.quad(tips[j], ctl[j], tips[(j + 1) % 4], 12)[:-1]
    return geo.poly(pts)


def hole_path(layer, path, nm="hole", **t):
    """animated hole from a raw path (or a Track of paths = morph) inside the layer's filled group."""
    layer.shapes[0]["it"].insert(0, lot.group([lot.sh(path, nm)], nm=nm, **t))
    return layer


def twinkle(c, nm, x, y, r, t0, dur=18, parent=None, spin=40, pinch=0.38):
    """✦ glint (bezier sparkle): pops to 120%, settles, turns a little, pinches out."""
    s = Track([0, 0], 0).hold(t0).to(t0 + dur * 0.3, [120, 120], "ox").to(t0 + dur * 0.55, [100, 100], "io")
    s.to(t0 + dur, [0, 0], "i")
    rr = Track(-spin / 2, 0).hold(t0).to(t0 + dur, spin / 2, "os")
    return c.layer(nm, [geo.shape(spark_g(x, y, r, pinch), nm=nm)], parent=parent, p=(x, y), a=(x, y), s=s, r=rr,
                   ip=int(t0), op=int(math.ceil(t0 + dur)))


def _clip_loop(tr, op):
    """drop keys past op (lagged tracks), then close the loop."""
    tr.k = [k for k in tr.k if k[0] < op - 0.5]
    tr.k[-1][2] = None
    return tr.loop(op)


# ================================================================ 83 👀


@emoji("83-eyes", "👀", "глаза, смотрю, палю, интересно, слежу, чё там", "eyes, looking, watching, drama, sus, tea",
       "глаза-люверсы косятся влево, зрачки стреляют вправо со смазом и бьются о край, двойной взгляд — выпучиваются на тебя, в зрачках вспыхивает ✦, моргают вразнобой",
       op=120, series=SERIES)
def eyes(c):
    OP = 120
    RX, RY = 112, 150
    E = [(140, 258), (372, 258)]
    dart = (0.55, 0.0, 0.15, 1.0)
    for i, (ex, ey) in enumerate(E):
        lag = 2 * i                       # right eye trails 2f (overlap)
        look = [(16, None, None), (22, -48, "decel"), (30, 46, dart), (35, 36, "io"), (40, 42, "io"), (45, 40, "io"),
                (58, None, None), (63, -46, dart), (67, -40, "io"), (73, 0, dart), (100, None, None), (118, -40, "io")]
        px = seq(-40, look, lag, op=OP, f=lambda v: ex + v)
        py = seq(14, [(66, None, None), (73, 2, dart), (100, None, None), (118, 14, "io")], lag, op=OP, f=lambda v: ey + v)
        ps = seq([100, 100], [(16, None, None), (22, [90, 110], "decel"), (26, [148, 80], "lin"), (30, [84, 114], "o"),
                              (35, [104, 97], "io"), (41, [100, 100], "io"),
                              (58, None, None), (60.5, [138, 84], "i"), (63, [86, 112], "o"), (68, [100, 100], "io"),
                              (70, [126, 88], "i"), (73, [110, 110], "o"), (80, [97, 97], "io"), (87, [102, 102], "io"),
                              (95, [100, 100], "io")], lag, op=OP)
        es = seq([100, 100], [(66, None, None), (70, [97, 104], "io"), (75, [113, 113], "snap"), (82, [95, 96], "io"),
                              (89, [103, 102], "io"), (97, [100, 100], "io")], lag)
        M.blink(es, 102 + 6 * i, dur=8, closed=8)
        es.loop(OP)
        ex_t = _clip_loop(seq(-8, [(19, None, None), (33, 9, "io"), (40, 7, "io"), (61, None, None), (66, -8, "io"),
                                   (76, 0, "io"), (103, None, None), (120, -8, "io")], lag, f=lambda v: ex + v), OP)
        er = _clip_loop(seq(-3, [(19, None, None), (33, 4, "io"), (61, None, None), (66, -4, "io"), (76, 0, "io"),
                                 (103, None, None), (120, -3, "io")], lag), OP)
        eye = rig(c, f"eye{i}", (ex, ey), p=Split(ex_t, ey), s=es, r=er)
        ring = geo.ellipse(ex, ey, RX, RY, 24).difference(geo.ellipse(ex, ey, RX - W, RY - W, 24))
        part(c, f"white{i}", ring, eye, (ex, ey))
        pl = part(c, f"pupil{i}", geo.disc(ex, ey, 52, 16), eye, (ex, ey), p=Split(px, py), s=ps)
        # glint cut into the pupil: a round catch-light that turns into a ✦ on the stare (morph), then back
        gx, gy = ex + 4, ey - 22
        rnd, star = spark4(gx, gy, 17, 0.98), spark4(gx, gy, 30, 0.3)
        gp = Track(rnd, 0).hold(72 + lag).to(77 + lag, star, "ox").hold(90 + lag).to(98 + lag, rnd, "io").loop(OP)
        hole_path(pl, gp, nm="glint")


# ================================================================ 84 🔥

FLAME = [  # x, y, tension (clockwise from the bottom): one tall leaning tongue, a medium left, a small right
    (256, 494, 1), (160, 484, 1), (100, 430, 1), (82, 350, 1), (96, 270, 1),
    (124, 212, 1),                          # 5 L outer flank
    (126, 146, 0.2),                        # 6 L tip (medium)
    (172, 206, 1),                          # 7 L inner flank
    (192, 258, 0.5),                        # 8 notch L
    (198, 180, 1), (214, 110, 1),           # 9, 10 C left flank
    (246, 50, 0.2),                         # 11 C tip (tall, leaning left)
    (304, 98, 1), (336, 182, 1),            # 12, 13 C right flank (bulges right)
    (350, 264, 0.5),                        # 14 notch R
    (374, 222, 1),                          # 15 R inner flank
    (400, 172, 0.2),                        # 16 R tip (small)
    (424, 238, 1),                          # 17 R outer flank
    (440, 322, 1), (430, 404, 1), (386, 470, 1),
]
# tip index: (period, phase, amp x, amp y, flanks near -> far)
TONGUES = {6: (40, 0.0, 16, 18, (5, 7)), 11: (60, 1.9, 18, 16, (10, 12, 9, 13)), 16: (30, 3.7, 14, 16, (15, 17))}


def flame_at(t, flare=0.0):
    """tongues lick on their own loop-friendly rhythms; flanks lag the tip (a wave runs up the tongue)."""
    pts = [list(p[:2]) for p in FLAME]
    for i, (per, ph, ax, ay, fl) in TONGUES.items():
        w = 2 * math.pi * t / per + ph
        dx = ax * math.sin(w) + 4 * math.sin(2 * math.pi * t / 24 + 2 * ph)
        dy = ay * (0.5 + 0.5 * math.cos(w + 0.8)) - flare * (24 if i == 11 else 20)
        pts[i][0] += dx
        pts[i][1] += dy
        for n, j in enumerate(fl):
            wt = 0.55 if n < 2 else 0.25
            pts[j][0] += wt * ax * math.sin(w - 0.9 - 0.5 * (n >= 2))
            pts[j][1] += wt * 0.6 * dy
    return pts


@emoji("84-fire", "🔥", "огонь, жара, пушка, горит, топ", "fire, lit, hot, flames, banger",
       "X-пламя лижет языками вразнобой, приседает и вспыхивает — угли-язычки рвутся вверх по дугам, логотип-X в сердцевине раздувается",
       op=120, series=SERIES)
def fire(c):
    OP = 120
    tens = [p[2] for p in FLAME]
    env = seq(0.0, [(38, None, None), (48, -0.6, "io"), (56, 1.0, "snap"), (66, 0.3, "io"), (74, 0.55, "io"),
                    (88, 0.0, "io")], op=OP)
    key = Track(smooth(flame_at(0, env.at(0)), tens), 0)
    for t in range(4, OP + 1, 4):
        tt = t % OP
        key.to(t, smooth(flame_at(tt, env.at(tt)), tens), "aelin")
    xg = brand_x(256, 386, 150, 104, bold=12)
    xs = seq([100, 100], [(46, None, None), (52, [86, 86], "io"), (58, [118, 118], "snap"), (66, [95, 95], "io"),
                          (74, [102, 102], "io"), (82, [100, 100], "io")], op=OP)
    grp = lot.group([lot.sh(key, "flame"), lot.group(geo.paths(xg), nm="X", p=(256, 386), a=(256, 386), s=xs),
                     lot.fill()], nm="flame")
    s = seq([100, 100], [(38, None, None), (48, [105, 94], "io"), (56, [97, 103], "snap"), (64, [101, 99], "io"),
                         (72, [99.5, 100.5], "io"), (80, [100, 100], "io")])
    breathe(s, 80, 120, [100, 100], 0.8, 20)
    s.loop(OP)
    c.layer("flame", [grp], p=(256, 494), a=(256, 494), s=s)
    # embers = little flames tearing off the tips: burst on the flare (stagger 2-3f) + stragglers
    em = [(55, 262, 92, 292, 84, 30, 22), (57, 136, 170, 84, 136, 32, 20), (59, 400, 196, 452, 162, 30, 20),
          (63, 214, 140, 172, 104, 28, 18), (66, 322, 150, 376, 120, 28, 18),
          (14, 300, 118, 330, 94, 34, 18), (100, 142, 180, 104, 142, 34, 18)]
    for k, (t0, x0, y0, x1, y1, life, r) in enumerate(em):
        g = geo.drop(x0, y0, r, r * 2.8)
        M.particle(c, f"ember{k}", g, t0, life, (x0, y0), (x1, y1), None, anchor=(x0, y0),
                   rot=(0, (x1 - x0) * 0.35), fall="decel", xease="os", pop=0.2, fade=0.45)


# ================================================================ 85 💯


def _affine(sx, tx, ty, sk):
    """skew (italic) around (256,184) then uniform scale + translate: (geom_fn, point_fn)."""
    k = math.tan(math.radians(sk))

    def pt(p):
        x = p[0] - k * (p[1] - 184)
        return (x * sx + tx, p[1] * sx + ty)

    def gm(g):
        g = affinity.skew(g, xs=-sk, origin=(256, 184))
        return affinity.affine_transform(g, [sx, 0, 0, sx, tx, ty])
    return gm, pt


@emoji("85-hundred", "💯", "сто, 100, точно, в точку, топ, база", "100, hundred, perfect, facts, exactly",
       "«100» шрифтом лого: нули — люверсы, которые пресс пробивает по очереди (удар, кольцо-волна), единица падает бруском последней, две черты подчёркивания выхлёстываются кистью, ✦ на хроме нуля",
       op=120, series=SERIES)
def hundred(c):
    OP = 120
    from specs.drop import brand_font
    one = geo.text("1", brand_font(), 96, 186, 150, bold=18)
    one = geo.fit_box(one, 34, 96, 122, 276, keep=False)
    zc = [(224, 186), (396, 186)]
    root = rig(c, "mark", (256, 300))
    # the 1: drops in as a bar from above and slams, 1f squash
    oy = seq(276.0, [(4, None, None), (6, 240.0, "io"), (14, 276.0, "slam")], op=OP)
    os_ = seq([100, 100], [(13, None, None), (14, [112, 88], "slam"), (15, [112, 88], "lin"), (21, [97, 103], "io"), (27, [100, 100], "io")], op=OP)
    part(c, "one", one, root, (84, 276), p=Split(84, oy), s=os_)
    # the zeros: eyelets punched by a press, 12f apart (click + shock ring), ✦ on the chrome of the second
    for k, (x, y) in enumerate(zc):
        t = 12 + k * 14
        ring = geo.ring(x, y, 84, 42, 24)
        zs = seq([0, 0], [(t, None, None), (t + 3, [118, 82], "slam"), (t + 4, [118, 82], "lin"), (t + 11, [94, 106], "o"),
                          (t + 18, [102, 98], "io"), (t + 25, [100, 100], "io"), (108, None, None), (113, [0, 0], "i")], op=OP, loop_ease="lin")
        part(c, f"zero{k}", ring, root, (x, y), s=zs)
        from specs.faces import lot_ring
        rs = Track([100, 100], 0).hold(t + 2).to(t + 14, [112, 112], "ring").hold(OP)
        rw = Track(22, 0).hold(t + 2).to(t + 14, 4, "ring").to(t + 18, 0, "i").hold(OP)
        c.layer(f"z{k}-ring", [lot_ring(x, y, 84, rw)], parent=root, p=(x, y), a=(x, y), s=rs, ip=t + 2, op=t + 19)
    # whole mark answers the punches
    root.s = seq([100, 100], [(15, None, None), (18, [102, 98], "o"), (24, [100, 100], "io"), (29, None, None),
                              (32, [102, 98], "o"), (38, [100, 100], "io")], op=OP)
    # underlines whip out after the second punch, retract at the end of the loop
    for j, (u, t_in) in enumerate((([(52, 340), (256, 332), (470, 322)], 36), ([(96, 412), (300, 404), (440, 396)], 44))):
        e = seq(0, [(t_in, None, None), (t_in + 9, 100, (0.2, 0.0, 0.1, 1.0)), (100 + 2 * j, None, None), (110 + 2 * j, 0, "i")], op=OP, loop_ease="lin")
        c.layer(f"under{j}", [stroke_line(u, W, nm=f"under{j}", e=e)], parent=root, p=(0, 0), a=(0, 0))
    M.twinkle(c, "tw", 396 + 60, 186 - 60, 34, 54, 22, parent=root)


# ================================================================ 86 ✅


@emoji("86-check", "✅", "готово, да, сделано, принято, ок, чек", "done, check, yes, approved, ok, complete",
       "бирка на люверсе: галочка прорезается одним росчерком насквозь (матт-вырез), бирка дёргается от прореза и качается на люверсе, ✦ с кромки; к концу лупа прорез затягивается",
       op=120, series=SERIES)
def check(c):
    OP = 120
    ex, ey = 126, 126
    box = geo.rrect(30, 30, 482, 482, 116).difference(geo.ring(ex, ey, 34, 15, 20))
    ck = [(140, 262), (222, 344), (378, 166)]
    s = seq([100, 100], [(30, None, None), (33, [103, 97], "o"), (40, [99, 101], "io"), (47, [100.3, 99.8], "io"), (54, [100, 100], "io")])
    breathe(s, 60, 120, [100, 100], 0.5, 30)
    s.loop(OP)
    r = seq(0, [(30, None, None), (34, 2.5, "o"), (46, -1.5, "io"), (58, 0.8, "io"), (70, 0, "io")], op=OP)
    plate = rig(c, "plate", (ex, ey), s=s, r=r)
    lay = part(c, "box", box, plate, (256, 256))
    # the one matte: a stroke drawn by trim cuts the check through the plate (draw-on of a hole)
    e = seq(0, [(12, None, None), (30, 100, (0.3, 0.0, 0.2, 1.0)), (100, None, None), (112, 0, "i")], op=OP, loop_ease="lin")
    st = seq(0, [])
    c.matte(lay, "cut", [stroke_line(ck, 72, nm="cut", e=e, s=st)], parent=plate, p=(0, 0), a=(0, 0))
    gx, gy = 186, 88
    gs = seq([0, 0], [(36, None, None), (41, [120, 120], "ox"), (47, [100, 100], "io"), (58, [0, 0], "i")], op=OP, loop_ease="lin")
    gr = seq(-14, [(36, None, None), (58, 14, "os")], op=OP, loop_ease="lin")
    geo.hole(lay, spark_g(gx, gy, 42, 0.3), nm="glare", p=(gx, gy), a=(gx, gy), s=gs, r=gr)


# ================================================================ 88 ❤️


@emoji("88-heart", "❤️", "сердце, люблю, love, лайк, обожаю", "heart, love, like, adore, <3",
       "лаковое сердце набирает воздух и тянется вверх — лаб-даб, на втором ударе блик вспыхивает ✦ и с боков отлетают две ✦-искры, досадка затухает",
       op=120, series=SERIES)
def heart(c):
    OP = 120
    hx, hy, hw = 256, 262, 436
    g = geo.heart(hx, hy, hw)
    bx0, by0, bx1, by1 = g.bounds
    tip = (hx, by1)
    k = hw / 404
    gl = lambda p: (hx + (p[0] - hx) * k, hy + (p[1] - hy) * k)
    streak = geo.brush([gl(p) for p in geo.arc(178, 196, 66, 196, 258, 14)], 36, taper=(0.7, 0.9), smooth=False)
    heart_g = g.difference(streak)
    bs = seq([100, 100], [(8, None, None), (32, [94, 109], "io"), (37, [100, 100], "i")])
    breathe(bs, 92, 120, [100, 100], 1.0, 28)
    bs.loop(OP)
    by = seq(tip[1], [(8, None, None), (32, tip[1] - 14, "io"), (37, tip[1], "i")], op=OP)
    base = rig(c, "breath", tip, p=Split(hx, by), s=bs)
    s = seq([100, 100], [(37, [106, 95], "snap"), (43, [98, 102], "io"), (47, [111, 91], "snap"),
                         (54, [95, 104], "io"), (61, [103, 98], "io"), (69, [99, 100.8], "io"), (78, [100.4, 99.7], "io"),
                         (87, [100, 100], "io")], op=OP)
    rr = seq(0, [(47, None, None), (51, -3, "o"), (58, 2, "io"), (66, 0, "io")], op=OP)
    beat = rig(c, "beat", (hx, hy + 20), parent=base, s=s, r=rr)
    hl = part(c, "heart", heart_g, beat, (hx, hy + 20))
    # the lacquer catch-light flashes into a ✦ on the dub, then melts back into a dot
    dx_, dy_ = gl((206, 150))
    rnd, star = spark4(dx_, dy_, 17, 0.98), spark4(dx_, dy_, 40, 0.3)
    hole_path(hl, Track(rnd, 0).hold(47).to(52, star, "ox").hold(60).to(70, rnd, "io").loop(OP), nm="catch")
    M.glare_sweep(c, hl, hx, hy + 10, 50, 30, travel=300, parent=beat)


# ================================================================ 89 💔


@emoji("89-broken-heart", "💔", "разбитое сердце, больно, грусть, расстался, эх", "broken heart, heartbreak, sad, hurt, breakup",
       "сердце бьётся, дрожит — трещина щёлкает раз, два, и половинки отваливаются на шарнире-кончике, качаются, с разлома капает, потом срастаются",
       op=150, series=SERIES)
def broken(c):
    OP = 150
    hx, hy, hw = 256, 262, 380
    g = geo.heart(hx, hy, hw)
    bx0, by0, bx1, by1 = g.bounds
    tip = (hx, by1 - 2)
    d = (by1 - by0) / 6
    zig = [(hx, by0 - 40), (hx - 4, by0 + d * 0.9), (hx + 30, by0 + d * 1.9), (hx - 30, by0 + d * 2.9),
           (hx + 22, by0 + d * 3.8), (hx - 8, by1 - 44), (hx, by1 + 40)]
    parts = sorted(_split(g, LineString(zig)).geoms, key=lambda p: p.centroid.x)
    assert len(parts) == 2, len(parts)
    left, right = parts
    kk = hw / 404
    gl = lambda p: (hx + (p[0] - 256) * kk, hy + (p[1] - 262) * kk)
    gloss = U(geo.brush([gl(p) for p in geo.arc(178, 196, 66, 196, 258, 14)], 34, taper=(0.7, 0.9), smooth=False),
              geo.disc(*gl((206, 150)), 16))
    left = left.difference(gloss)
    g = g.difference(gloss)
    ws = seq([100, 100], [(8, None, None), (12, [106, 96], "snap"), (20, [100, 100], "io"), (41, None, None),
                          (42, [103, 98], "o"), (46, [100, 100], "io"), (48, None, None), (49, [104, 97], "o"),
                          (53, [100, 100], "io"), (140, None, None), (144, [104, 96], "o"), (150, [100, 100], "io")])
    wx = seq(float(hx), [(26, None, None)])
    M.shake(wx, 26, 41, 4, float(hx), step=2, decay=1.0)
    wx.loop(OP)
    whole = rig(c, "whole", (hx, hy), p=Split(wx, hy), s=ws)
    # the intact heart under the halves while closed (hides the anti-aliased seam between two layers)
    io = Track(100, 0)
    for t, v in ((41, 0), (141, 100)):
        io.k[-1][2] = "hold"
        io.k.append([t, v, None])
    io.loop(OP, "lin")
    intact = part(c, "intact", g, whole, tip, o=io)
    M.glare_sweep(c, intact, hx, hy, 8, 26, travel=280, parent=whole)
    fall = [(40, None, None), (42, 2.5, "snap"), (47, None, None), (49, 5.5, "snap"), (54, None, None),
            (62, 13, "i"), (70, 6.5, "io"), (78, 10, "io"), (86, 8, "io"), (94, 9, "io"), (102, 8.6, "io"),
            (122, None, None), (140, 0, "io3")]
    sag = [(54, None, None), (62, 12, "i"), (70, 5, "io"), (78, 9, "io"), (90, 8, "io"), (122, None, None), (140, 0, "io3")]
    rots, sags = [], []
    for j, (nm, geom, sgn) in enumerate((("L", left, -1), ("R", right, 1))):
        amp = 1.0 if j == 0 else 0.9
        r = _clip_loop(seq(0, fall, j, f=lambda v: sgn * v * amp), OP)
        py = _clip_loop(seq(0, sag, j, f=lambda v: tip[1] + v), OP)
        rots.append(r)
        sags.append(py)
        part(c, f"half{nm}", geom, whole, tip, p=Split(tip[0], py), r=r)
    # the crack spits shards out of the dip on the final split (they arc over the lobes and pinch out)
    for k, (t0, x1, y1, ap, sz, rt) in enumerate(((54, 124, 96, 52, 26, -160), (55, 390, 90, 48, 24, 170),
                                                   (57, 306, 70, 44, 18, 120))):
        x0, y0 = hx + (6 if k == 1 else -6), by0 + d * 0.9
        tri = geo.poly([(x0 - sz, y0 + sz * 0.7), (x0 + sz * 0.9, y0 + sz * 0.4), (x0 - sz * 0.1, y0 - sz)])
        M.particle(c, f"shard{k}", tri, t0, 26, (x0, y0), (x1, y1), ap, anchor=(x0, y0), rot=(0, rt),
                   pop=0.15, fade=0.35)


# ================================================================ 91 ⚡

BOLT = [(214, 22), (362, 22), (300, 186), (406, 186), (184, 474), (234, 280), (110, 280)]


@emoji("91-zap", "⚡", "молния, разряд, энергия, быстро, мощь, заряд", "zap, lightning, energy, fast, power, electric",
       "молния втягивается в ✦-заряд наверху, заряд сжимается и — разряд: молния прошивает вниз с растяжкой, удар кольцом и искрами, трещит и мигает",
       op=120, series=SERIES)
def zap(c):
    OP = 120
    top = (288, 22)
    g = geo.poly(BOLT).buffer(10, join_style=1).buffer(-10, join_style=1)
    s = seq([100, 100], [(4, [101, 99.4], "io"), (9, [100, 100], "io"), (12, None, None), (23, [92, 3], "i"),
                         (31, None, None), (35, [94, 105], "snap"),
                         (38, [110, 93], "slam"), (44, [97, 103], "io"), (50, [101, 99], "io"), (56, [100, 100], "io")])
    breathe(s, 60, 84, [100, 100], 0.9, 12)
    s.hold(86).to(88, [103, 98], "o").to(94, [100, 100], "io")
    breathe(s, 94, 120, [100, 100], 0.9, 12)
    s.loop(OP)
    px = seq(float(top[0]), [(38, None, None)])
    M.shake(px, 38, 60, 8, float(top[0]), step=2, decay=0.86)
    M.shake(px, 86, 96, 4, float(top[0]), step=2, decay=0.8)
    px.loop(OP)
    o = Track(100, 0)
    for t, v in ((23, 0), (31, 100), (41, 30), (43, 100), (47, 45), (49, 100), (88, 55), (90, 100)):
        o.k[-1][2] = "hold"
        o.k.append([t, v, None])
    o.loop(OP)
    part(c, "bolt", g, None, top, p=Split(px, top[1]), s=s, o=o)
    cx_, cy_ = 290, 120
    cs = seq([0, 0], [(12, None, None), (21, [104, 104], "snap"), (24, [84, 84], "io"), (27, [100, 100], "io"),
                      (29, [76, 76], "io"), (32, [116, 116], "snap"), (37, [0, 0], "i")])
    cr = seq(-20, [(12, None, None), (28, 10, "io"), (37, 70, "i")])
    c.layer("charge", [geo.shape(spark_g(cx_, cy_, 88, 0.4), nm="charge")], p=(cx_, cy_), a=(cx_, cy_), s=cs, r=cr,
            ip=12, op=38)
    tx, ty = 190, 450
    ring = lot.group([lot.sh(smooth([(tx + 150 * math.cos(a), ty + 30 * math.sin(a)) for a in
                                     [2 * math.pi * i / 12 for i in range(12)]]), "ring"),
                      lot.stroke(seq(30, [(38, None, None), (56, 0, "ring")]))],
                     nm="ring", p=(tx, ty), a=(tx, ty), s=seq([18, 18], [(38, None, None), (56, [100, 100], "ring")]))
    c.layer("shock", [ring], ip=38, op=56)
    # mini bolts flicker around the discharge (3-4 frames each), one more on the aftershock
    mini = geo.poly(BOLT)
    for k, (x, y, sc, rt, t0) in enumerate(((104, 176, 0.24, -24, 39), (420, 132, 0.22, 28, 43),
                                             (124, 380, 0.2, 200, 48), (374, 300, 0.22, 160, 52), (110, 150, 0.2, -30, 86))):
        mg = affinity.translate(affinity.rotate(affinity.scale(mini, sc, sc, origin=(288, 250)), rt, origin=(288, 250)),
                                x - 288, y - 250)
        ms = Track([0, 0], 0).hold(t0).to(t0 + 1.5, [115, 115], "ox").to(t0 + 3, [100, 100], "io").to(t0 + 5, [0, 0], "i")
        c.layer(f"mini{k}", [geo.shape(mg, nm=f"mini{k}")], p=(x, y), a=(x, y), s=ms, ip=t0, op=t0 + 5)
    for k, (x1, y1) in enumerate(((70, 360), (330, 350), (96, 440), (312, 440))):
        M.particle(c, f"spark{k}", spark_g(tx, ty - 10, 30, 0.4), 38 + k, 18, (tx, ty - 10), (x1, y1), None,
                   anchor=(tx, ty - 10), rot=(0, 45), fall="o5", xease="o5", pop=0.12, fade=0.5)


# ================================================================ 92 ❓


@emoji("92-question", "❓", "вопрос, что, чего, а, не понял, хм", "question, what, huh, confused, hmm",
       "«?» медленно склоняет голову-крючок «хм…», потом вертит ей «а?! а?» — рядом выскакивает мини-«!», точка-люверс семенит следом с отставанием и сплющивается на разворотах",
       op=120, series=SERIES)
def question(c):
    OP = 120
    hc = (256, 164)
    hook_pts = geo.arc(hc[0], hc[1], 104, 198, 392, 26) + [(270, 282), (262, 326)]
    hook = geo.brush(hook_pts, 70, taper=(0.72, 0.85), smooth=True, n=4)
    dcx, dcy, dro, dri = 262, 436, 56, 22
    dot = eyelet(dcx, dcy, dro, dri)
    turns = [(16, None, None), (32, -24, "io"), (44, None, None), (50, 22, "io3"), (56, -12, "io"), (62, 6, "io"),
             (69, 0, "io"), (90, None, None), (97, -8, "io"), (105, 2.5, "io"), (112, 0, "io")]
    hr = seq(0, turns, op=OP)
    hs = seq([100, 100], [(44, None, None), (48, [96, 105], "o"), (54, [102, 98], "io"), (60, [100, 100], "io")])
    breathe(hs, 76, 120, [100, 100], 0.8, 22)
    hs.loop(OP)
    hk = rig(c, "hook", hc, s=hs, r=hr)
    part(c, "hookg", hook, hk, hc)
    # the stem end swings with the head; the dot follows it 5f late (follow-through), squashing on turns
    stem = (262, 326)
    L = math.hypot(stem[0] - hc[0], stem[1] - hc[1])

    def sx(deg):
        return hc[0] - L * math.sin(math.radians(deg)) * 0.9

    lag = 5
    dx = seq(float(dcx), [(t, None if v is None else sx(v) + (dcx - hc[0]), e) for t, v, e in turns], lag)
    dx = _clip_loop(dx, OP)
    db = (dcx, dcy + dro)
    ds = seq([100, 100], [(16 + lag, None, None), (24 + lag, [112, 90], "io"), (32 + lag, [100, 100], "io"),
                          (44 + lag, None, None), (47 + lag, [124, 84], "o"), (50 + lag, [88, 112], "io"),
                          (53 + lag, [118, 86], "o"), (56 + lag, [92, 108], "io"), (60 + lag, [108, 94], "io"),
                          (65 + lag, [100, 100], "io"), (95, None, None), (99, [112, 88], "io"), (103, [95, 104], "o"),
                          (109, [100, 100], "io"), (111, [110, 90], "o"), (116, [100, 100], "io")], op=OP)
    dy = seq(float(db[1]), [(49 + lag, None, None), (52 + lag, db[1] - 10.0, "o"), (55 + lag, float(db[1]), "i"),
                            (58 + lag, db[1] - 6.0, "o"), (61 + lag, float(db[1]), "i"), (99, None, None),
                            (105, db[1] - 12.0, "decel"), (111, float(db[1]), "i5")], op=OP)
    part(c, "dot", dot, None, db, p=Split(dx, dy), s=ds)
    # "а?!" — a mini "!" pops out beside the head on the snap and floats off, turning
    mx, my = 432, 132
    mq = U(U(geo.disc(mx, my - 50, 20), geo.disc(mx, my + 8, 13)).convex_hull, geo.disc(mx, my + 44, 16))
    M.particle(c, "minix", mq, 49, 34, (mx, my), (452, 96), None, anchor=(mx, my), rot=(-28, 16),
               fall="o5", xease="os", pop=0.2, fade=0.35, s_peak=100)


# ================================================================ 93 ❗


@emoji("93-exclaim", "❗", "важно, внимание, восклицание, ого, срочно", "important, attention, exclamation, alert, urgent",
       "«!» приседает, вздёргивается вверх и молотом бьёт по точке-люверсу: точка сплющивается и звенит дыркой, удар расходится веером линий, ✦-блик, позже эхо-тап",
       op=120, series=SERIES)
def exclaim(c):
    OP = 120
    bar = U(geo.disc(256, 112, 58), geo.disc(256, 300, 34)).convex_hull
    dcx, dcy, dro, dri = 256, 424, 56, 22
    dot = eyelet(dcx, dcy, dro, dri)
    bb = (256, 334)
    s = seq([100, 100], [(12, None, None), (22, [112, 88], "io"), (29, [92, 105], "o"), (35, [95, 104], "io"),
                         (39, [118, 86], "slam"), (40, [118, 86], "lin"), (45, [94, 106], "io"), (51, [103, 97], "io"),
                         (58, [100, 100], "io")])
    s.hold(84).to(90, [96, 104], "io").to(93, [108, 93], "slam").to(99, [98, 102], "io").to(105, [100, 100], "io")
    s.loop(OP)
    y = seq(bb[1], [(22, None, None), (30, bb[1] - 16, "o"), (35, bb[1] - 18, "io"), (39, bb[1] + 36, "slam"),
                    (40, bb[1] + 36, "lin"), (47, bb[1] - 8, "o"), (54, bb[1] + 3, "io"), (60, bb[1], "io"),
                    (84, None, None), (90, bb[1] - 8, "io"), (93, bb[1] + 14, "slam"), (100, bb[1] - 2, "o"),
                    (106, bb[1], "io")], op=OP)
    r = seq(0, [(22, None, None), (33, -5, "io"), (39, 1.5, "slam"), (47, -1, "io"), (55, 0, "io")], op=OP)
    root = rig(c, "all", (256, 256))
    bl = rig(c, "bar", bb, parent=root, p=Split(bb[0], y), s=s, r=r)
    part(c, "barg", bar, bl, bb)
    db = (dcx, dcy + dro)
    ds = seq([100, 100], [(22, None, None), (30, [104, 97], "io"), (39, None, None), (41, [138, 66], "slam"),
                          (42, [138, 66], "lin"), (48, [88, 114], "o"), (55, [106, 95], "io"), (62, [98, 102], "io"),
                          (69, [100, 100], "io"), (93, None, None), (95, [112, 90], "o"), (101, [96, 104], "io"),
                          (107, [100, 100], "io")], op=OP)
    dl = part(c, "dot", geo.disc(dcx, dcy, dro, 20), root, db, s=ds)
    hs = seq([100, 100], [(40, None, None), (42, [60, 60], "o"), (48, [132, 132], "o"), (54, [88, 88], "io"),
                          (60, [106, 106], "io"), (66, [100, 100], "io")], op=OP)
    geo.hole(dl, geo.disc(dcx, dcy, dri, 12), nm="eyelet", p=(dcx, dcy), a=(dcx, dcy), s=hs)
    for k, (sgn, ang) in enumerate([(sg, a) for sg in (-1, 1) for a in (-36, -8, 20)]):
        a = math.radians(ang)
        x0 = dcx + sgn * 104 * math.cos(a)
        y0 = dcy - 6 + 104 * math.sin(a) * 0.8
        Ln = 70 if ang == 0 else 58
        x1, y1 = x0 + sgn * Ln * math.cos(a), y0 + Ln * math.sin(a)
        e = seq(0, [(41, None, None), (47, 100, "o5")])
        st = seq(0, [(44, None, None), (53, 100, "o5")])
        c.layer(f"hit{k}", [stroke_line([(x0, y0), (x1, y1)], 30, nm=f"hit{k}", s=st, e=e)], parent=root,
                p=(0, 0), a=(0, 0), ip=41, op=54)
    gx, gy = dcx + 70, dcy - 64
    twinkle(c, "glint", gx, gy, 36, 56, dur=22, parent=root, spin=40)
