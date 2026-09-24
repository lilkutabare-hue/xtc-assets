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
    em = [(55, 262, 92, 292, 58, 30, 16), (57, 136, 170, 84, 110, 32, 15), (59, 400, 196, 452, 136, 30, 15),
          (62, 214, 140, 176, 76, 28, 13), (65, 322, 150, 372, 92, 28, 13),
          (8, 300, 118, 330, 66, 34, 12), (28, 142, 180, 104, 116, 34, 12), (94, 392, 200, 438, 140, 34, 12),
          (108, 236, 110, 214, 58, 32, 12)]
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
       "подчёркивания втягиваются, по «100» прокатывается волна прыжков 1-0-0, каждая черта хлёстко дописывается кистью на приземлении, нули-люверсы подмигивают",
       op=120, series=SERIES)
def hundred(c):
    OP = 120
    one = geo.line([(92, 122), (150, 58), (150, 312)], 60, "round", "round")
    z1c, z2c = (252, 186), (404, 186)
    z1 = geo.ellipse(*z1c, 74, 128, 24).difference(geo.ellipse(*z1c, 24, 80, 24))
    z2 = geo.ellipse(*z2c, 74, 128, 24).difference(geo.ellipse(*z2c, 24, 80, 24))
    u1 = [(78, 380), (250, 370), (474, 354)]
    u2 = [(120, 446), (300, 438), (430, 428)]
    raw = U(one, z1, z2, geo.line(u1, W), geo.line(u2, W))
    gm, pt = _affine(1, 0, 0, 12)
    b = gm(raw).bounds
    sc = min((478 - 34) / (b[2] - b[0]), (470 - 50) / (b[3] - b[1]))
    tx = 256 - (b[0] + b[2]) / 2 * sc
    ty = 260 - (b[1] + b[3]) / 2 * sc
    gm, pt = _affine(sc, tx, ty, 12)
    one, z1, z2 = gm(one), gm(z1), gm(z2)
    u1, u2 = [pt(p) for p in u1], [pt(p) for p in u2]
    z1c, z2c = pt(z1c), pt(z2c)
    base = pt((256, 400))
    # the mark leans with the wave and gets a kick from each finished underline
    s = seq([100, 100], [(36, None, None), (38, [101.5, 98.5], "o"), (43, [100, 100], "io"), (46, None, None),
                         (48, [102, 98], "o"), (54, [99.5, 100.5], "io"), (60, [100, 100], "io")])
    breathe(s, 60, 120, [100, 100], 0.8, 30)
    s.loop(OP)
    r = seq(0, [(14, None, None), (24, -3, "io"), (36, 2.5, "io"), (46, -1, "io"), (56, 0, "io")], op=OP)
    root = rig(c, "mark", base, s=s, r=r)
    # a hop wave rolls through the digits (antic squash -> stretch up -> land squash), 5f apart
    for i, (nm, g, anc) in enumerate((("one", one, pt((150, 312))), ("zero1", z1, z1c), ("zero2", z2, z2c))):
        t0 = 16 + 5 * i
        ds = seq([100, 100], [(t0, None, None), (t0 + 4, [106, 94], "io"), (t0 + 9, [93, 107], "decel"),
                              (t0 + 15, [98, 102], "i"), (t0 + 17, [110, 91], "o"), (t0 + 22, [97, 103], "io"),
                              (t0 + 28, [100, 100], "io")])
        if i:
            M.blink(ds, 82 + 7 * (i - 1), dur=8, closed=10)
        ds.loop(OP)
        y = seq(anc[1], [(t0 + 4, None, None), (t0 + 10, anc[1] - 24, "decel"), (t0 + 16, anc[1], "i"),
                         (t0 + 21, anc[1] - 5, "o"), (t0 + 25, anc[1], "i")], op=OP)
        part(c, nm, g, root, anc, p=Split(anc[0], y), s=ds)
    # underlines: sucked back into their start, then whipped out as the first / last digit lands
    for j, (u, t_in) in enumerate(((u1, 28), (u2, 38))):
        e = seq(100, [(8 + 2 * j, None, None), (18 + 2 * j, 0, "i"), (t_in, None, None),
                      (t_in + 9, 100, (0.2, 0.0, 0.1, 1.0))], op=OP, loop_ease="lin")
        c.layer(f"under{j}", [stroke_line(u, W, nm=f"under{j}", e=e)], parent=root, p=(0, 0), a=(0, 0))


# ================================================================ 86 ✅


@emoji("86-check", "✅", "готово, да, сделано, принято, ок, чек", "done, check, yes, approved, ok, complete",
       "плашка-бирка на люверсе: кисть одним росчерком закрашивает галочку, бирка крутнувшись схлопывается в свой люверс, жирная галочка остаётся одна и раздувается — бирка выстреливает из люверса обратно 108→92→100, покачивается на нём, галочка выворачивается в вырез, с кромки люверса ✦",
       op=120, series=SERIES)
def check(c):
    OP = 120
    box = geo.rrect(30, 30, 482, 482, 116)
    ck = [(140, 262), (222, 344), (378, 166)]
    cw = 72
    ex, ey = 126, 126                                   # the hang-tag grommet: the plate hangs and spins on it
    box = box.difference(geo.ring(ex, ey, 34, 15, 20))
    holed = box.difference(geo.line(ck, cw, "round", "round"))
    s = seq([100, 100], [(20, None, None), (26, [106, 94], "io"), (33, [0, 0], "i"), (44, None, None),
                         (49, [105, 105], "snap"), (55, [95, 95], "io"), (62, [102, 101.5], "io"), (69, [99.5, 100], "io"),
                         (76, [100, 100], "io")])
    breathe(s, 76, 120, [100, 100], 0.7, 22)
    s.loop(OP)
    r = seq(0, [(20, None, None), (26, 3, "io"), (33, -35, "i"), (44, None, None), (49, 0, "snap"), (55, 2, "io"),
                (62, -1, "io"), (69, 0, "io")], op=OP)
    t_swap = t_cross(44, 49, 0, 105, "snap", 100)
    ts = int(math.ceil(t_swap))
    plate = rig(c, "plate", (ex, ey), s=s, r=r)
    # the plate is holed at rest; solid while the black tick covers the check (no slivers), holed again at the swap
    oh, osd = Track(100, 0), Track(0, 0)
    # rlottie still draws a layer on its op frame, so the plate flips one frame after the tick's op
    for tr_, seq_ in ((oh, ((20, 0), (ts + 1, 100))), (osd, ((20, 100), (ts + 1, 0)))):
        for t, v in seq_:
            tr_.k[-1][2] = "hold"
            tr_.k.append([t, v, None])
        tr_.loop(OP, "lin")
    boxl = part(c, "box", holed, plate, (256, 256), o=oh)
    part(c, "solid", box, plate, (256, 256), o=osd)
    gx, gy = 186, 88                                    # the glint pops off the grommet's rim
    gs = seq([0, 0], [(58, None, None), (63, [120, 120], "ox"), (69, [100, 100], "io"), (78, [0, 0], "i"),
                      (98, None, None), (103, [84, 84], "ox"), (108, [70, 70], "io"), (115, [0, 0], "i")], op=OP, loop_ease="lin")
    gr = seq(-14, [(58, None, None), (78, 14, "os"), (98, None, None), (115, 40, "os")], op=OP, loop_ease="lin")
    geo.hole(boxl, spark_g(gx, gy, 42, 0.3), nm="glare", p=(gx, gy), a=(gx, gy), s=gs, r=gr)
    # the brush inks the white check (slightly wider than the hole), stays alone, swells, sinks back at the swap
    e = seq(0, [(8, None, None), (19, 100, (0.3, 0.0, 0.2, 1.0))])
    cs = Track([100, 100], 0).hold(33).to(37, [132, 112], "o").to(41, [118, 128], "io").to(t_swap, [100, 100], "i")
    cy = seq(256, [(34, None, None), (39, 240, "decel"), (45, 256, "i")])
    c.layer("tick", [stroke_line(ck, cw + 6, nm="tick", e=e)], p=Split(256, cy), a=(256, 256), s=cs,
            ip=8, op=ts)


# ================================================================ 87 ❌


@emoji("87-cross", "❌", "нет, отказ, мимо, неверно, крест, стоп", "no, nope, wrong, denied, cross, rejected",
       "X из двух ремней с люверсами отрывается как штамп (под ним бледный оттиск), бьёт с разворота — 1 кадр 107/93, брызги-подтёки в стороны, по люверсам бежит эхо",
       op=120, series=SERIES)
def cross(c):
    OP = 120
    sw, half = 100, 170
    holes_d = (118, 196)

    def strap(sgn):
        return geo.line([(256 - half, 256 - sgn * half), (256 + half, 256 + sgn * half)], sw, "round")

    def holes(sgn):
        out = []
        for d in holes_d:
            for side in (-1, 1):
                out.append((256 + side * d / math.sqrt(2), 256 + side * sgn * d / math.sqrt(2)))
        return out
    # the paler imprint left on the "paper" while the stamp is lifted
    imp = U(strap(1), strap(-1)).difference(U(*[geo.disc(x, y, 19, 10) for sg in (1, -1) for x, y in holes(sg)]))
    io = Track(0, 0).hold(12).to(22, 34, "io").to(27, 34, "lin")
    io.k[-1][2] = "hold"
    io.k.append([28, 0, None])
    io.loop(OP, "lin")
    part(c, "imprint", imp, None, (256, 256), o=io)
    root_s = seq([100, 100], [(10, None, None), (24, [84, 84], "io3"), (28, [107, 93], "slam"), (29, [107, 93], "lin"),
                              (34, [96, 104], "io"), (40, [101.5, 98.5], "io"), (47, [100, 100], "io")])
    breathe(root_s, 70, 120, [100, 100], 0.7, 25)
    root_s.loop(OP)
    root_r = seq(0, [(10, None, None), (24, -16, "io3"), (28, 3, "slam"), (34, -1.5, "io"), (41, 0, "io")], op=OP)
    px = seq(256.0, [(29, None, None)])
    M.shake(px, 29, 43, 6, 256.0, step=2, decay=0.78)
    px.loop(OP)
    root = rig(c, "stamp", (256, 256), p=Split(px, 256), s=root_s, r=root_r)
    for j, sgn in enumerate((1, -1)):      # j=0 '\' below, j=1 '/' on top
        lay = part(c, f"strap{j}", strap(sgn), root, (256, 256))
        for q, (hx, hy) in enumerate(holes(sgn)):
            t0 = 60 + (q // 2) * 6 + j * 2
            hs = seq([100, 100], [(t0, None, None), (t0 + 5, [150, 150], "o"), (t0 + 12, [90, 90], "io"),
                                  (t0 + 18, [100, 100], "io")], op=OP)
            geo.hole(lay, geo.disc(hx, hy, 19, 10), nm=f"e{q}", p=(hx, hy), a=(hx, hy), s=hs)
    for k, (x0, y0, x1, y1) in enumerate([(256, 150, 256, 40), (366, 256, 474, 262), (256, 362, 250, 470),
                                          (146, 256, 38, 248), (330, 176, 400, 88), (182, 336, 112, 420)]):
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
        r = 20 if k < 4 else 15
        g = geo.rot(geo.drop(x0, y0, r, r * 2.6), ang, (x0, y0))
        M.particle(c, f"ink{k}", g, 28 + (k % 3), 22, (x0, y0), (x1, y1), None, anchor=(x0, y0), rot=(0, 0),
                   fall="o5", xease="o5", pop=0.12, fade=0.4)


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
    for j, (x0, y0, x1, y1) in enumerate([(118, 322, 62, 428), (394, 322, 450, 428)]):
        sp = spark_g(x0, y0, 46, 0.36)
        M.particle(c, f"spark{j}", sp, 47 + 2 * j, 34, (x0, y0), (x1, y1), None, anchor=(x0, y0),
                   rot=(0, 40 if j else -40), pop=0.2, fade=0.4, fall="o5", xease="o5", s_peak=100)


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
    part(c, "intact", g, whole, tip, o=io)
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


# ================================================================ 90 ✨


@emoji("90-sparkles", "✨", "блеск, искры, красота, вау, магия, глянец", "sparkles, shine, magic, glam, wow",
       "большая ✦ заряжается, вспыхивает острее и поворачивается на 90°, выбрасывает микро-искры — малые ✦ отвечают по очереди 140/124, потом волна мерцания",
       op=120, series=SERIES)
def sparkles(c):
    OP = 120
    B, Md, Sm = (212, 298, 150), (382, 146, 80), (410, 402, 54)
    x, y, R = B
    shp = Track(spark4(x, y, R, 0.38), 0).hold(24)
    shp.to(30, spark4(x, y, R, 0.22), "snap").to(44, spark4(x, y, R, 0.38), "io").loop(OP)
    s = seq([100, 100], [(14, None, None), (24, [86, 86], "io"), (30, [123, 123], "snap"), (37, [93, 93], "io"),
                         (45, [104, 104], "io"), (53, [100, 100], "io"), (76, None, None), (81, [111, 111], "o"),
                         (90, [100, 100], "io")], op=OP)
    r = Track(0, 0).hold(14).to(24, -14, "io").to(31, 62, "snap").to(40, 96, "io").to(48, 88, "io").to(56, 90, "io")
    c.layer("big", [lot.group([lot.sh(shp, "big"), lot.fill()], nm="big")], p=(x, y), a=(x, y), s=s, r=r)
    for nm, (x, y, R), t0, peak, spin, tw in (("mid", Md, 32, 140, -90, 86), ("small", Sm, 40, 124, 90, 92)):
        s = seq([100, 100], [(t0, None, None), (t0 + 4, [72, 72], "io"), (t0 + 10, [peak, peak], "snap"),
                             (t0 + 17, [90, 90], "io"), (t0 + 24, [104, 104], "io"), (t0 + 31, [100, 100], "io"),
                             (tw, None, None), (tw + 5, [114, 114], "o"), (tw + 14, [100, 100], "io")], op=OP)
        r = Track(0, 0).hold(t0 + 4).to(t0 + 12, spin * 0.8, "snap").to(t0 + 24, spin * 1.04, "io").to(t0 + 31, spin, "io")
        part(c, nm, spark_g(x, y, R, 0.38), None, (x, y), s=s, r=r)
    x, y, R = B
    ring = lot.group([lot.sh(smooth([(x + 120 * math.cos(a), y + 120 * math.sin(a)) for a in
                                     [2 * math.pi * i / 8 for i in range(8)]]), "ring"),
                      lot.stroke(seq(24, [(31, None, None), (48, 0, "ring")]))],
                     nm="ring", p=(x, y), a=(x, y), s=seq([92, 92], [(31, None, None), (48, [146, 146], "ring")]))
    c.layer("shine", [ring], ip=31, op=48)
    for k, (dx, dy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
        x0, y0 = x + dx * R * 0.7, y + dy * R * 0.7
        x1 = min(max(x + dx * R * 1.16 - dy * 20, 40), 472)
        y1 = min(max(y + dy * R * 1.16 + dx * 20, 40), 472)
        M.particle(c, f"micro{k}", spark_g(x0, y0, 24, 0.38), 30 + k, 20, (x0, y0), (x1, y1), None,
                   anchor=(x0, y0), rot=(0, 45), fall="o5", xease="o5", pop=0.15, fade=0.5)
    twinkle(c, "late", 92, 96, 30, 96, dur=18, spin=50)


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
