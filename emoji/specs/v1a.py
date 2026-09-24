"""v1 remakes (02, 03, 04, 10, 13-23): the v1 silhouettes redrawn bold for 24px (pack weight W=46,
min detail 28px) and animated from scratch in XTC MOTION. Techniques M# = moodboard.md."""
import math

from shapely import affinity
from shapely.geometry import LineString
from shapely.ops import split as _split

from xtc import geo, lot, motion as M
from xtc.geo import U, W
from xtc.lot import Split, Track, bez_y, ease_of
from xtc.reg import emoji

CX = 256
SERIES = "v1"


# ---------------------------------------------------------------- local helpers


def part(c, nm, g, parent=None, anchor=(CX, CX), p=None, s=None, r=None, o=100, ip=0, op=None, tol=0.45):
    return c.layer(nm, [geo.shape(g, nm=nm, tol=tol)], parent=parent, p=p if p is not None else anchor, a=anchor,
                   s=s if s is not None else (100, 100), r=r if r is not None else 0, o=o, ip=ip, op=op)


def rig(c, nm, anchor, parent=None, p=None, s=None, r=None, o=100):
    return c.null(nm, parent=parent, p=p if p is not None else anchor, a=anchor,
                  s=s if s is not None else (100, 100), r=r if r is not None else 0, o=o)


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
    """hold-key (stepped) track: [(t, v)] - for visibility swaps. rlottie draws a layer on its op frame."""
    tr = Track(v0, 0)
    for t, v in keys:
        tr.k[-1][2] = "hold"
        tr.k.append([t, v, None])
    if op is not None:
        tr.loop(op, "lin")
    return tr


def clip_loop(tr, op):
    tr.k = [k for k in tr.k if k[0] < op - 0.5]
    tr.k[-1][2] = None
    return tr.loop(op)


def stroke_line(pts, w, nm="line", s=0, e=100, **t):
    items = [lot.sh(lot.pathdata(pts, closed=False), nm), lot.trim(s, e), lot.stroke(w)]
    return lot.group(items, nm=nm, **t)


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


def poly_path(pts):
    return lot.pathdata(pts, True)


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


def rot_pt(p, c, deg):
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def breathe(tr, t0, t1, base, amp=1.0, per=30):
    tr.hold(t0)
    t, k = t0, 0
    while t + per / 2 <= t1 - per / 2 + 1e-6:
        t += per / 2
        sgn = 1 if k % 2 == 0 else -1
        tr.to(t, [b * (1 + sgn * amp / 100) for b in base], "io")
        k += 1
    return tr


def hole_path(layer, path, nm="hole", **t):
    layer.shapes[0]["it"].insert(0, lot.group([lot.sh(path, nm)], nm=nm, **t))
    return layer


def brand_x(x, y, w, h, bold=9):
    return geo.text("X", geo.font("Michroma-Regular.ttf"), x, y, h, bold=bold, width=w)


def drip_shape(x, y0, y1, w=44, bulb=None):
    """a latex drip hanging from y0 to y1: a stem with a round bulb at the end."""
    bulb = bulb or w * 0.62
    return U(geo.line([(x, y0), (x, y1 - bulb * 0.4)], w, "round"), geo.disc(x, y1 - bulb, bulb, 12))


# ================================================================ 02 🤪


@emoji("02-acid-xx", "🤪", "кислота, угар, трип, диджей, скретч, безумие", "acid, crazy, trip, dj, scratch, wild",
       "кислотный смайл — пластинка: DJ-скретч туда-сюда, отпускает — полный оборот, подтёки срываются центробежно и заново стекают",
       op=120, series=SERIES)
def acid(c):
    OP = 120
    fc = (256, 202)
    R = 168
    face = geo.disc(*fc, R, 32)
    eyes = U(brand_x(186, 160, 120, 52, bold=11), brand_x(326, 160, 120, 52, bold=11))
    smile = U(geo.brush(geo.arc(256, 204, 104, 22, 158, 24), 38, taper=(0.8, 0.8), smooth=False),
              geo.line([(148, 232), (160, 252)], 30), geo.line([(364, 232), (352, 252)], 30))
    fg = face.difference(eyes).difference(smile)
    # scratch: wind back, 3 jerks (smear-fast), release into a full turn that brakes (decel)
    rot = [(12, None, None), (20, -26, "io"), (25, 34, "io3"), (30, -16, "io3"), (34, 28, "io3"), (38, -8, "io3"),
           (44, 0, "io"), (72, 360, (0.25, 0.0, 0.2, 1.0))]
    r = seq(0, rot)
    s = seq([100, 100], [(24, None, None), (25, [104, 97], "o"), (29, [100, 100], "io"), (33, [104, 97], "o"),
                         (37, [100, 100], "io"), (72, None, None), (75, [103, 98], "o"), (82, [100, 100], "io")])
    breathe(s, 82, 120, [100, 100], 0.8, 19)
    s.loop(OP)
    part(c, "face", fg, None, fc, s=s, r=r)
    # drips hang from the rim: slosh on each jerk, snap off on the release, ooze back one by one
    drips = [(170, 346, 420, 42, 0), (290, 356, 466, 48, 6), (360, 334, 384, 38, 12)]
    for k, (x, y0, y1, w, lag) in enumerate(drips):
        g = drip_shape(x, y0 - 30, y1, w)
        ds = seq([100, 100], [(22, None, None), (26, [96, 106], "o"), (30, [104, 93], "io"), (34, [95, 107], "o"),
                              (38, [104, 94], "io"), (44, [100, 100], "io"), (47, [70, 0], "i"),
                              (76 + lag, None, None), (86 + lag, [92, 107], "o"), (94 + lag, [104, 96], "io"),
                              (102 + lag, [100, 100], "io")])
        ds.k = [kk for kk in ds.k]
        ds.loop(OP)
        part(c, f"drip{k}", g, None, (x, y0 - 30), s=ds)
        # the drop flung off tangentially (the disc turns clockwise: the bottom moves left) and falls
        bx, by = x, y1 - w * 0.62
        M.particle(c, f"fling{k}", geo.drop(bx, by, w * 0.5, w * 1.15), 46 + k * 2, 26, (bx, by),
                   (bx - 150 + k * 30, 470 - k * 20), by - 60 - k * 10, rot=(90, 150), anchor=(bx, by),
                   pop=0.08, fade=0.3, s_peak=100)


# ================================================================ 03 🕷️


def _leg(root, knee, tip, w=40):
    return geo.brush([root, knee, tip], w, taper=(1.0, 0.72), smooth=True, n=6)


@emoji("03-sigil-x", "🕷️", "паук, сигил, жуть, свисаю, готика", "spider, sigil, creepy, hanging, goth",
       "паук-сигил подтягивается по нити, поджимает лапы — и срывается вниз, пружинит на нити, лапы дёргаются, раскачивается маятником",
       op=150, series=SERIES)
def sigil(c):
    OP = 150
    top = (256, 26)
    sc_ = (256, 292)                     # spider centre
    spine = U(geo.line([(256, 150), (256, 404)], 50, "round"), geo.line([(212, 184), (300, 184)], 36, "round"))
    abdomen = geo.ellipse(256, 322, 60, 76, 20)
    body = U(spine, abdomen, geo.disc(256, 238, 36)).difference(brand_x(256, 324, 70, 50, bold=10))
    legs = [((282, 246), (372, 170), (436, 214)), ((282, 288), (392, 264), (446, 322)), ((282, 330), (374, 374), (416, 440))]
    # pendulum from the anchor at the top edge: dangles, damped swing after the drop
    pr = seq(-3, [(10, 3, "io"), (20, 0, "io"), (86, None, None), (98, 6, "io"), (110, -4.5, "io"), (122, 3.2, "io"),
                  (134, -1.8, "io"), (144, -3, "io")], op=OP)
    pend = rig(c, "pendulum", top, r=pr)
    # climb in three pulls, curl at the top, drop (i5), bungee bounce, settle
    dy = [(18, None, None), (24, -40, "o"), (27, None, None), (33, -72, "o"), (36, None, None), (42, -96, "o"),
          (54, None, None), (62, 22, "i5"), (69, -34, "o"), (76, 10, "io"), (82, -8, "io"), (88, 0, "io")]
    y = seq(0.0, dy, f=lambda v: sc_[1] + v)
    y.loop(OP)
    ss = seq([100, 100], [(18, None, None), (24, [95, 106], "o"), (27, [100, 100], "io"), (33, [95, 106], "o"),
                          (36, [100, 100], "io"), (42, [95, 106], "o"), (46, [100, 100], "io"),
                          (54, None, None), (60, [90, 112], "i"), (62, [112, 88], "o"), (69, [95, 106], "io"),
                          (76, [102, 98], "io"), (84, [100, 100], "io")], op=OP)
    spider = rig(c, "spider", sc_, parent=pend, p=Split(sc_[0], y), s=ss)
    # thread: trim end tracks the spider (e is linear in dy, so the same keys/eases stay in sync)
    L = sc_[1] - 142 - top[1]
    e = seq(100.0, dy, f=lambda v: 100.0 * (L + v) / L)
    e.loop(OP)
    c.layer("thread", [stroke_line([top, (256, sc_[1] - 142)], 28, nm="thread", e=e)], parent=pend, p=top, a=top)
    for side in (-1, 1):
        for k, (a, b, t) in enumerate(legs):
            m = lambda p: (256 + side * (p[0] - 256), p[1])
            root = m(a)
            # legs curl in at the top, splay on the drop, twitch in a stagger at the bottom, idle wiggle
            curl = side * 24
            lg = 2 * k + (0 if side < 0 else 1)
            lr = seq(0, [(4 + lg * 2, side * 3, "io"), (12 + lg * 2, 0, "io"), (40, None, None), (46, curl, "io"),
                         (54, None, None), (60, side * 16, "o"), (62 + lg, -side * 10, "io"), (66 + lg, side * 8, "io"),
                         (70 + lg, -side * 4, "io"), (76 + lg, 0, "io"),
                         (104 + lg * 3, side * 4, "io"), (112 + lg * 3, 0, "io")], op=OP)
            part(c, f"leg{side}{k}", _leg(root, m(b), m(t)), spider, root, r=lr)
    part(c, "body", body, spider, sc_)


# ================================================================ 04 💝


def _feather(root, ang, length, w=50):
    a = math.radians(ang)
    tip = (root[0] + math.cos(a) * length, root[1] + math.sin(a) * length)
    mid = (root[0] + math.cos(a) * length * 0.55 - math.sin(a) * 10, root[1] + math.sin(a) * length * 0.55 + math.cos(a) * 10)
    return geo.brush([root, mid, tip], w, taper=(0.75, 0.2), smooth=True, n=6)


@emoji("04-tramp-stamp", "💝", "сердце с крыльями, люблю, подарок, лечу, тату", "winged heart, love, gift, flying, tattoo",
       "сердце-тату с поднятыми крыльями делает два мощных взмаха — перья раскрываются веером с запаздыванием, сердце подлетает, зависает и планирует вниз",
       op=120, series=SERIES)
def tramp(c):
    OP = 120
    hc = (256, 318)
    heart = geo.heart(256, 322, 214).difference(brand_x(256, 304, 112, 48, bold=10))
    hy = seq(0.0, [(10, None, None), (14, 6, "io"), (20, -18, "o"), (28, -10, "io"), (34, -36, "o"), (44, -30, "io"),
                   (58, -34, "io"), (96, 0, "io")], f=lambda v: hc[1] + v)
    hy.loop(OP)
    hs = seq([100, 100], [(10, None, None), (14, [104, 96], "io"), (20, [95, 106], "o"), (28, [103, 97], "io"),
                          (34, [95, 106], "o"), (44, [100, 100], "io"), (96, None, None), (100, [103, 97], "o"),
                          (106, [100, 100], "io")], op=OP)
    body = rig(c, "body", hc, p=Split(hc[0], hy), s=hs)
    # wing stroke (deg, + = down for the right wing): antic up, down, up, down, glide
    flap = [(6, None, None), (13, -22, "io"), (20, 24, "io3"), (27, -20, "io"), (34, 26, "io3"), (44, -4, "io"),
            (58, 0, "io"), (96, None, None), (104, 5, "io"), (112, 0, "io")]
    feathers = [(-72, 176, 44), (-44, 176, 44), (-16, 150, 42)]
    for side in (-1, 1):
        root = (256 + side * 76, 262)
        for i, (ang, ln, w) in enumerate(feathers):
            a = ang if side > 0 else 180 - ang
            g = _feather(root, a, ln, w)
            lag = 2 * i                  # trailing feathers follow 2f later -> the wing fans open on each stroke
            r = clip_loop(seq(0, flap, lag, f=lambda v: side * v * (1 - 0.1 * i)), OP)
            part(c, f"f{side}{i}", g, body, root, r=r)
    part(c, "heart", heart, body, hc)
    M.twinkle(c, "tw", 256, 150, 34, 40, 22, parent=body)


# ================================================================ 10 🔑


def _key(cx, top=30, bottom=482):
    bow_o = geo.heart(cx, top + 88, 204)
    bow = bow_o.difference(geo.heart(cx, top + 84, 96))
    collar = geo.rrect(cx - 44, top + 186, cx + 44, top + 214, 12)
    shaft = geo.rrect(cx - 27, top + 170, cx + 27, bottom, 14)
    teeth = U(geo.rect(cx + 20, bottom - 124, cx + 86, bottom - 88), geo.rect(cx + 20, bottom - 58, cx + 100, bottom - 22),
              geo.rect(cx + 20, bottom - 96, cx + 66, bottom - 58))
    return U(bow, collar, shaft, teeth.buffer(6).buffer(-6))


@emoji("10-club-key", "🔑", "ключ, открыть, доступ, клуб, пропуск", "key, unlock, access, club, pass",
       "ключ-сердце входит в скважину и туго проворачивается ребром — щелчок, дрожь — его отпускают, и он докручивается по инерции тяжёлым оборотом, на головке ✦",
       op=150, series=SERIES)
def key(c):
    OP = 150
    cx, cy = 256, 256
    front = _key(cx)
    back = front.difference(geo.disc(cx, 118, 20))      # the back shows the rivet of the bow
    # insert (push down), turn to edge-on with resistance, click, back out, momentum spin, settle
    y = seq(0.0, [(12, None, None), (22, 14, "io"), (52, None, None), (60, -16, "o"), (100, None, None),
                  (110, 0, "io")], f=lambda v: cy + v)
    y.loop(OP)
    s = seq([100, 100], [(12, None, None), (22, [103, 97], "io"), (26, [100, 100], "io"), (41, None, None),
                         (43, [98, 102], "o"), (47, [100, 100], "io"), (104, None, None), (108, [103, 97], "o"),
                         (116, [100, 100], "io")])
    breathe(s, 116, 150, [100, 100], 0.7, 17)
    s.loop(OP)
    px = seq(float(cx), [(42, None, None)])
    M.shake(px, 42, 52, 4, float(cx), step=2, decay=0.75)
    px.loop(OP)
    body = rig(c, "body", (cx, cy), p=Split(px, y), s=s)
    segs = [(24, 40, 0, 88, "io3"), (40, 43, 88, 96, "o"), (43, 50, 96, 90, "io"),
            (56, 100, 90, 372, (0.3, 0.0, 0.14, 1.0)), (100, 112, 372, 360, "io")]
    M.spin3d(c, "key", front, back, cx, cy, segs, thick=42, lip=22, parent=body)
    M.twinkle(c, "tw", cx - 118, 70, 36, 104, 26, parent=body)


# ================================================================ 13 🗡️


def _dagger(cx=256, top=30, tip=472):
    pommel = geo.spark(cx, top + 30, 34, 0.42)
    grip = geo.rrect(cx - 21, top + 50, cx + 21, top + 138, 12)
    guard = geo.brush([(cx - 108, top + 136), (cx - 60, top + 152), (cx, top + 154), (cx + 60, top + 152), (cx + 108, top + 136)],
                      42, taper=(0.8, 0.8), smooth=True, n=4)
    blade = geo.poly([(cx - 40, top + 160), (cx + 40, top + 160), (cx + 30, tip - 110), (cx, tip), (cx - 30, tip - 110)])
    blade = blade.buffer(4, join_style=2).buffer(-4, join_style=2)
    fuller = geo.rrect(cx - 11, top + 186, cx + 11, tip - 140, 11)
    return U(pommel, grip, guard, blade).difference(fuller)


@emoji("13-dagger-cross", "🗡️", "кинжал, нож, удар, бей, клинок", "dagger, knife, stab, blade, strike",
       "кинжал выдёргивают из земли с усилием, он взмывает — и вонзается обратно: трещина, пыль, клинок дребезжит «твэнг» с затуханием и фантомами",
       op=120, series=SERIES)
def dagger(c):
    OP = 120
    tip = (256, 472)
    g = _dagger(top=62)
    y = seq(0.0, [(12, None, None), (18, -14, "io"), (22, -10, "io"), (30, -36, "o"), (38, -42, "io"),
                  (43, 6, "i5"), (48, 0, "o")], f=lambda v: tip[1] + v)
    y.loop(OP)
    s = seq([100, 100], [(30, None, None), (38, [98, 102], "io"), (42, [97, 103], "i"), (44, [106, 94], "o"),
                         (50, [100, 100], "io")], op=OP)
    root = rig(c, "stuck", tip, p=Split(tip[0], y), s=s)
    # twang: fast damped vibration about the tip (period 6f), with a wiggle while it is yanked
    tw = [(12, None, None), (16, 4, "io"), (20, -4, "io"), (24, 2, "io"), (30, -5, "io"), (38, -7, "io"), (43, 0, "i5")]
    amps = [13, -11, 9, -7.4, 6, -4.8, 3.8, -2.9, 2.1, -1.4, 0.8, 0]
    t = 43
    for a in amps:
        t += 3
        tw.append((t, a, "io"))
    r = seq(0, tw, op=OP)
    part(c, "dagger", g, root, tip, r=r)
    # ghosts of the vibration (paler copies at the swing extremes, fading with the envelope)
    for sgn in (-1, 1):
        gr = seq(sgn * 13.0, [(60, sgn * 4.0, "o"), (70, sgn * 1.5, "io")])
        go = seq(0.0, [(43, None, None), (44, 34.0, "o"), (70, 0.0, "i")])
        part(c, f"ghost{sgn}", g, root, tip, r=gr, o=go, ip=43, op=71)
    # impact: crack under the tip, two dust puffs thrown sideways
    for k, sgn in enumerate((-1, 1)):
        e = seq(0.0, [(43, None, None), (46, 100.0, "o5")])
        st = seq(0.0, [(50, None, None), (60, 100.0, "i")])
        pts = [(256 + sgn * 30, 484), (256 + sgn * 106, 476)]
        c.layer(f"crack{k}", [stroke_line(pts, 28, nm=f"crack{k}", s=st, e=e)], p=(0, 0), a=(0, 0), ip=43, op=61)
        for q in range(2):
            x0 = 256 + sgn * (54 + 26 * q)
            puff = U(geo.disc(x0, 470, 22 - 5 * q), geo.disc(x0 + sgn * 18, 462, 16 - 4 * q), geo.disc(x0 - sgn * 8, 456, 14 - 3 * q))
            M.particle(c, f"dust{k}{q}", puff, 44 + 3 * q, 20, (x0, 470), (x0 + sgn * (110 - 30 * q), 420 - 20 * q), None,
                       anchor=(x0, 470), pop=0.15, fade=0.55, fall="o5", xease="o5", s_peak=100)


# ================================================================ 14 💓


def _heart_pts(cx, cy, w, n=48):
    g = geo.heart(cx, cy, w, res=n * 2)
    return geo.resample(g, n, start_angle=-90)


def _pinch(pts, cy, amount, wy, sig=70):
    out = []
    for x, y in pts:
        k = amount * math.exp(-((y - wy) / sig) ** 2)
        out.append((256 + (x - 256) * (1 - k), y))
    return out


@emoji("14-barbed-heart", "💓", "сердце в проволоке, больно, держусь, тяжело, колючка", "barbed heart, hurts, holding on, pain, wire",
       "колючая проволока затягивается петлёй — сердце перетягивает в талию, оно дрожит, набирает силы и рвёт проволоку: обрывки отлетают, потом проволока снова вползает",
       op=150, series=SERIES)
def barbed(c):
    OP = 150
    hc = (256, 262)
    base = _heart_pts(256, 262, 404)
    wy = 282
    pinched = _pinch(base, 262, 0.3, wy, 80)
    hp = Track(poly_path(base), 0).hold(16).to(40, poly_path(pinched), "io").hold(48).to(53, poly_path(base), "snap").loop(OP)
    # the wire: one band + barbs, XOR-ed with the heart (evenodd): white across the heart, black outside
    wire = [(48, 326), (150, 304), (256, 282), (362, 256), (464, 232)]
    barbs = []
    for x in (100, 176, 250, 330, 406):
        yy = 326 + (x - 48) * (232 - 326) / 416
        barbs.append(U(geo.line([(x - 22, yy - 22), (x + 22, yy + 22)], 18), geo.line([(x - 22, yy + 22), (x + 22, yy - 22)], 18)))
    band = U(geo.line(wire, 32, "round"), *barbs)
    halves = [band.intersection(geo.rect(0, 0, 256, 512)), band.intersection(geo.rect(256, 0, 512, 512))]
    groups = []
    for j, (hg, sgn) in enumerate(zip(halves, (-1, 1))):
        mid = (256 + sgn * 104, 282 - sgn * 24)
        end = (256 + sgn * 208, 282 - sgn * 50)       # the tail end: the wire regrows from here
        # cinch towards the middle, snap off and fly apart spinning on the burst, regrow from the tail and pull tight
        p = seq(list(mid), [(16, None, None), (40, [mid[0] - sgn * 10, mid[1]], "io"), (49, None, None),
                            (58, [mid[0] + sgn * 60, mid[1] - 30 + j * 50], "o5")])
        p.k[-1][2] = "hold"
        p.k.append([59, list(end), None])       # parked at the tail end (scale 0) while the anchor is there too
        p.k[-1][2] = "hold"
        p.k.append([107, list(mid), None])
        p.loop(OP, "lin")
        r = seq(0, [(16, None, None), (40, -sgn * 4, "io"), (49, None, None), (58, sgn * 60, "o5")])
        r.k[-1][2] = "hold"
        r.k.append([59, -sgn * 30, None])
        r.hold(78).to(100, sgn * 6, "io").to(108, 0, "io").loop(OP)
        sc = seq([100, 100], [(49, None, None), (58, [0, 0], "o5")])
        sc.hold(78).to(98, [104, 104], "o").to(106, [100, 100], "io").loop(OP)
        # the group anchor switches from the middle (flying off) to the tail end (regrowing) with the hold key
        a_ = Track(list(mid), 0)
        a_.k[-1][2] = "hold"
        a_.k.append([59, list(end), None])
        a_.k[-1][2] = "hold"
        a_.k.append([107, list(mid), None])
        a_.loop(OP, "lin")
        groups.append(lot.group(geo.paths(hg), nm=f"wire{j}", p=p, a=a_, r=r, s=sc))
    # freed: a ✦ glint flashes through the lacquer (XOR cut)
    gx, gy = 160, 172
    gs = seq([0, 0], [(54, None, None), (59, [120, 120], "ox"), (65, [100, 100], "io"), (74, [0, 0], "i")], op=OP, loop_ease="lin")
    gr = seq(-20, [(54, None, None), (74, 20, "os")], op=OP, loop_ease="lin")
    glint = lot.group(geo.paths(geo.spark(gx, gy, 46, 0.34)), nm="glint", p=(gx, gy), a=(gx, gy), s=gs, r=gr)
    grp = lot.group([lot.sh(hp, "heart")] + groups + [glint, lot.fill()], nm="heart")
    s = seq([100, 100], [(40, None, None), (47, [96, 97], "io"), (51, [109, 108], "snap"), (58, [96, 97], "io"),
                         (65, [102, 101.5], "io"), (73, [100, 100], "io")])
    breathe(s, 76, 150, [100, 100], 0.8, 24)
    s.loop(OP)
    px = seq(256.0, [(22, None, None)])
    M.shake(px, 22, 46, 3, 256.0, step=2, decay=1.0)
    px.loop(OP)
    c.layer("heart", [grp], p=Split(px, hc[1]), a=hc, s=s)


# ================================================================ 15 💘


@emoji("15-dagger-heart", "💘", "кинжал в сердце, ранил, больно, влюбился насмерть, ревность", "dagger heart, stabbed, hurt, lovestruck, jealous",
       "сердце выталкивает кинжал — тот улетает кувырком; сердце успевает выдохнуть, и кинжал возвращается, крутясь, вонзается с отдачей, из раны срывается капля",
       op=120, series=SERIES)
def dagger_heart(c):
    OP = 120
    hc = (256, 286)
    heart = geo.heart(256, 296, 360)
    dg = _dagger(top=30)
    dg = affinity.scale(dg, 0.86, 0.86, origin=(256, 256))
    dg = geo.rot(dg, 30, (256, 256))
    dg = affinity.translate(dg, 4, 8)
    b = dg.bounds
    dc = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    far = (370, 140)
    # dagger (inside the heart's fill group -> XOR: white inside the heart, black outside)
    p = seq(list(dc), [(10, None, None), (16, [dc[0] + 18, dc[1] - 30], "io"), (26, list(far), "o5"), (44, None, None),
                       (54, list(dc), "lin")], op=OP)
    r = seq(0, [(10, None, None), (16, -6, "io"), (26, 240, "o5"), (44, -500, "hold"), (54, 0, "lin")], op=OP)
    r.k[3][2] = "hold"
    s = seq([100, 100], [(16, None, None), (24, [0, 0], "o"), (44, [26, 26], "hold"), (53, [100, 100], "i")], op=OP)
    s.k[2][2] = "hold"
    dgrp = lot.group(geo.paths(dg), nm="dagger", p=p, a=list(dc), r=r, s=s)
    grp = lot.group([lot.group(geo.paths(heart), nm="heart"), dgrp, lot.fill()], nm="dh")
    # the heart: squeezes to push the blade out, exhales (one easy breath), recoils on the hit and settles
    hp = seq(list(hc), [(54, None, None), (57, [hc[0] - 20, hc[1] + 12], "o"), (64, [hc[0] + 6, hc[1] - 4], "io"),
                        (71, [hc[0] - 2, hc[1] + 1], "io"), (78, list(hc), "io")], op=OP)
    hr = seq(0, [(54, None, None), (57, -8, "o"), (64, 3, "io"), (71, -1, "io"), (78, 0, "io")], op=OP)
    hs = seq([100, 100], [(8, None, None), (14, [96, 104], "io"), (18, [104, 96], "o"), (24, [100, 100], "io"),
                          (30, [103, 103], "io"), (40, [100, 100], "io"), (54, None, None), (56, [94, 106], "o"),
                          (62, [103, 98], "io"), (70, [100, 100], "io")])
    breathe(hs, 80, 120, [100, 100], 0.8, 20)
    hs.loop(OP)
    c.layer("dh", [grp], p=hp, a=hc, s=hs, r=hr)
    # a drop tears off the wound's lower lip and falls
    for k, (t0, x0) in enumerate(((58, 176), (92, 186))):
        M.particle(c, f"drop{k}", geo.drop(x0, 404, 18, 42), t0, 26, (x0, 404), (x0 - 6, 478), None, anchor=(x0, 404),
                   fall="i5", pop=0.3, fade=0.25, s_end=40)


# ================================================================ 16 💖


@emoji("16-heart-pill", "💖", "сердечко, мармелад, желе, мило, таблетка", "heart pill, jelly, gummy, cute, candy",
       "сердце-таблетка приседает, подпрыгивает и шлёпается желе: 128/76, мармеладная тряска с затуханием, X на лице отстаёт, ✦ на глянце",
       op=120, series=SERIES)
def heart_pill(c):
    OP = 120
    bot = (256, 466)                          # jelly pivot: the bottom of the tablet
    face = geo.heart(256, 258, 380)
    side = geo.heart(256, 294, 380)
    body = U(face, side)
    groove = face.exterior.buffer(10).intersection(geo.rect(0, 270, 512, 512)).intersection(side.buffer(-2))
    xg = brand_x(256, 252, 160, 70, bold=12)
    bodyg = body.difference(groove)
    ys = [(10, None, None), (18, 6, "io"), (30, -32, "o"), (36, -36, "io"), (46, 0, "i5")]
    y = seq(0.0, ys, f=lambda v: bot[1] + v)
    y.loop(OP)
    wob = [(10, None, None), (18, [112, 88], "io"), (24, [94, 105], "o"), (36, [98, 102], "io"), (45, [95, 105], "i"),
           (47, [128, 76], "o"), (52, [88, 114], "io"), (58, [114, 90], "io"), (64, [92, 107], "io"), (71, [106, 95], "io"),
           (78, [97, 103], "io"), (86, [101.5, 98.5], "io"), (94, [100, 100], "io")]
    s = seq([100, 100], wob)
    breathe(s, 94, 120, [100, 100], 1.0, 13)
    s.loop(OP)
    lay = part(c, "pill", bodyg, None, bot, p=Split(bot[0], y), s=s)
    # the X on the face jiggles 2f late with a bigger swing (overlap)
    xs = clip_loop(seq([100, 100], [(t, None if v is None else [100 + (v[0] - 100) * 1.25, 100 + (v[1] - 100) * 1.25], e)
                                      for t, v, e in wob], 2), OP)
    geo.hole(lay, xg, nm="X", p=(256, 252), a=(256, 252), s=xs)
    gs = seq([0, 0], [(62, None, None), (67, [120, 120], "ox"), (73, [100, 100], "io"), (84, [0, 0], "i")], op=OP, loop_ease="lin")
    gr = seq(-20, [(62, None, None), (84, 25, "os")], op=OP, loop_ease="lin")
    geo.hole(lay, geo.spark(150, 196, 40, 0.34), nm="glint", p=(150, 196), a=(150, 196), s=gs, r=gr)


# ================================================================ 17 🪽


@emoji("17-winged-x", "🪽", "крылья, лечу, свобода, взлёт, ангел", "wings, flying, free, take off, angel",
       "X раскрывает сложенные крылья веером (перья по очереди), мощный взмах — взлетает с растяжкой, трепещет в воздухе, планирует, одно перо медленно падает",
       op=150, series=SERIES)
def winged(c):
    OP = 150
    xc = (256, 356)
    xg = brand_x(256, 356, 176, 132, bold=14)
    y = seq(0.0, [(16, None, None), (26, 8, "io"), (36, -64, "o"), (44, -70, "io"), (52, -62, "io"), (60, -68, "io"),
                  (96, 0, "io")], f=lambda v: xc[1] + v)
    y.loop(OP)
    s = seq([100, 100], [(16, None, None), (26, [108, 92], "io"), (32, [93, 108], "o"), (42, [100, 100], "io"),
                         (95, None, None), (99, [104, 96], "o"), (106, [100, 100], "io")])
    breathe(s, 120, 150, [100, 100], 0.8, 15)
    s.loop(OP)
    body = rig(c, "body", xc, p=Split(xc[0], y), s=s)
    fan = [-88, -64, -40, -16]                 # open fan (right wing, deg from +x, - = up)
    folded = -40
    for side in (-1, 1):
        root = (256 + side * 58, 318)
        for i, ang in enumerate(fan):
            ln = 188 - 12 * abs(i - 1)
            a0 = folded if side > 0 else 180 - folded
            g = _feather(root, a0, ln, 44)
            d = (ang - folded) * side             # rotation that opens this feather from the folded stack
            lag = 2 * i
            # rest = open fan; fold in (reverse stagger) as the anticipation, burst open into the power stroke,
            # flutter while hovering, glide back open
            fl = 2 * (3 - i)
            wing = [(8 + fl, None, None), (18 + fl, 0, "io"), (26, None, None),
                    (30 + i, d + side * 26, "o"), (35 + i, d - side * 10, "io"),
                    (39 + i, d + side * 8, "io"), (43 + i, d - side * 8, "io"), (47 + i, d + side * 6, "io"),
                    (51 + i, d - side * 4, "io"), (58 + i, d, "io"), (96, None, None), (102 + i, d + side * 5, "io"),
                    (110 + i, d, "io")]
            r = seq(d, wing, op=OP)
            part(c, f"f{side}{i}", g, body, root, r=r)
    part(c, "X", xg, body, xc)
    # a loose feather drifts down, rocking
    fx, fy = 420, 150
    fth = _feather((fx, fy - 60), 90, 120, 34)
    M.particle(c, "loose", fth, 34, 90, (fx, fy), (452, 456), None, anchor=(fx, fy), rot=(-40, 30),
               fall="io", xease="io", pop=0.08, fade=0.2, s_peak=100)


# ================================================================ 18 ⛓️


@emoji("18-spike-collar", "⛓️", "чокер, ошейник, цепь, дерзко, шипы", "choker, collar, chain, spiked, edgy",
       "чокер с шипами дёргают как поводок — рывок вверх, сердце-жетон с замочной скважиной раскачивается маятником с досадкой, второй рывок поменьше, ✦ на шипе",
       op=120, series=SERIES)
def collar(c):
    OP = 120
    cc = (256, 210)
    Ro, Ri = 132, 88
    ring = geo.ring(*cc, Ro, Ri, 32)
    spikes = []
    for k in range(8):
        a = math.radians(-90 + 45 * k)
        if k == 4:
            continue                      # the bottom one is where the O-ring hangs
        bx, by = cc[0] + math.cos(a) * (Ro - 6), cc[1] + math.sin(a) * (Ro - 6)
        tx, ty = cc[0] + math.cos(a) * (Ro + 40), cc[1] + math.sin(a) * (Ro + 40)
        nx, ny = -math.sin(a) * 24, math.cos(a) * 24
        spikes.append(geo.poly([(bx + nx, by + ny), (tx, ty), (bx - nx, by - ny)]).buffer(3).buffer(-3))
    collar_g = U(ring, *spikes)
    oring_c = (256, cc[1] + Ro + 18)
    oring = geo.ring(*oring_c, 32, 13, 16)
    pend = geo.heart(256, 432, 140)
    keyhole = U(geo.disc(256, 420, 16), geo.poly([(247, 422), (265, 422), (272, 460), (240, 460)]))
    pend = pend.difference(keyhole)
    # two tugs on the leash: up with a twist, drop back with a bounce
    y = seq(0.0, [(10, None, None), (15, -22, "o5"), (22, 5, "i"), (28, -3, "io"), (34, 0, "io"),
                  (62, None, None), (66, -14, "o5"), (72, 3, "i"), (78, 0, "io")], f=lambda v: cc[1] + v)
    y.loop(OP)
    r = seq(0, [(10, None, None), (15, -5, "o5"), (22, 2, "io"), (30, 0, "io"), (62, None, None), (66, 3, "o5"),
                (74, 0, "io")], op=OP)
    s = seq([100, 100], [(10, None, None), (15, [96, 105], "o5"), (22, [104, 96], "io"), (30, [100, 100], "io")])
    breathe(s, 84, 120, [100, 100], 0.7, 18)
    s.loop(OP)
    col = rig(c, "collar", cc, p=Split(cc[0], y), s=s, r=r)
    part(c, "ring", collar_g, col, cc)
    # the tag swings from the O-ring: pendulum (period 20f), damped; kicked again by the small tug
    sw = [(12, None, None), (18, 28, "o"), (28, -21, "io"), (38, 14.5, "io"), (48, -9.5, "io"), (58, 5, "io"),
          (68, -11, "io"), (78, 8, "io"), (88, -4.5, "io"), (98, 2, "io"), (108, 0, "io")]
    pr = seq(0, sw, op=OP)
    tag = rig(c, "tag", oring_c, parent=col, r=pr)
    part(c, "oring", oring, tag, oring_c)
    part(c, "pendant", pend, tag, oring_c)
    M.twinkle(c, "tw", cc[0] + 118, cc[1] - 118, 34, 88, 22, parent=col)


# ================================================================ 19 ⭐


def _star_thorns(cx, cy, R, r, rot=-90):
    st = geo.star(cx, cy, R, r, 5, rot).buffer(10, join_style=1).buffer(-10, join_style=1)
    thorns = []
    for k in range(5):
        a = math.radians(rot + 36 + 72 * k)            # the inner vertices
        bx, by = cx + math.cos(a) * r, cy + math.sin(a) * r
        tx, ty = cx + math.cos(a) * (r + 60), cy + math.sin(a) * (r + 60)
        nx, ny = -math.sin(a) * 16, math.cos(a) * 16
        thorns.append(geo.poly([(bx + nx, by + ny), (tx, ty), (bx - nx, by - ny)]))
    return U(st, *thorns)


@emoji("19-thorn-star", "⭐", "звезда, топ, лучший, успех, шипы", "star, top, best, winner, thorns",
       "звезда с шипами приседает и подброшена монеткой — два оборота через голову в воздухе (с торцом), приземляется с отдачей, на луче вспыхивает ✦",
       op=150, series=SERIES)
def thorn_star(c):
    OP = 150
    cx, cy = 256, 282
    star = _star_thorns(cx, cy, 204, 92)
    front = star.difference(brand_x(cx, cy + 8, 116, 54, bold=11))
    back = star.difference(geo.spark(cx, cy + 6, 60, 0.36))
    # the flip is about the horizontal axis: spin3d turns about the vertical one, so the art is pre-rotated
    # -90° and the whole rig is turned +90°
    f_r, b_r = geo.rot(front, -90, (cx, cy)), geo.rot(back, -90, (cx, cy))
    gy = cy + 190
    y = seq(0.0, [(14, None, None), (22, 8, "io"), (36, -44, "o"), (46, -48, "io"), (60, 0, "i5"), (66, -10, "o"),
                  (72, 0, "i")], f=lambda v: gy + v)
    y.loop(OP)
    s = seq([100, 100], [(14, None, None), (22, [107, 92], "io"), (28, [95, 106], "o"), (36, [100, 100], "io"),
                         (59, None, None), (61, [110, 90], "o"), (68, [97, 103], "io"), (76, [100, 100], "io")])
    breathe(s, 100, 150, [100, 100], 0.8, 25)
    s.loop(OP)
    body = rig(c, "body", (cx, gy), p=Split(cx, y), s=s)
    turn = rig(c, "turn", (cx, cy), parent=body, r=90)
    segs = [(20, 26, 0, -16, "io"), (26, 60, -16, 720, (0.3, 0.0, 0.3, 1.0)), (60, 68, 720, 726, "o"), (68, 76, 726, 720, "io")]
    M.spin3d(c, "star", f_r, b_r, cx, cy, segs, thick=40, lip=26, parent=turn)
    M.twinkle(c, "tw", cx + 118, cy - 150, 38, 78, 26, parent=body)


# ================================================================ 20 🤝


@emoji("20-split-pill", "🤝", "договорились, сделка, половинки, вместе, мэтч", "deal, handshake, halves, together, match",
       "две половинки таблетки парят порознь, магнит тянет — дрожат и ползут навстречу, щёлк! схлопываются, из шва брызгают ✦, держатся, потом нехотя разлипаются",
       op=150, series=SERIES)
def split_pill(c):
    OP = 150
    cx, cy = 256, 250
    face = geo.ellipse(cx, cy - 20, 164, 108, 32)
    rim = geo.ellipse(cx, cy + 24, 164, 108, 32)
    body = U(face, rim, geo.rect(cx - 164, cy - 20, cx + 164, cy + 24))
    groove = face.exterior.buffer(9).intersection(geo.rect(0, cy - 10, 512, 512)).intersection(rim.buffer(-4))
    xg = affinity.scale(brand_x(cx, cy - 22, 184, 104, bold=13), 1, 0.72, origin=(cx, cy - 22))
    coin = body.difference(groove).difference(xg)
    zig = [(cx + 6, 60), (cx - 14, 150), (cx + 16, 210), (cx - 16, 262), (cx + 14, 320), (cx - 6, 420)]
    left_region = geo.poly(zig + [(0, 420), (0, 60)])
    left, right = coin.intersection(left_region), coin.difference(left_region)
    # separation (px each side): hover apart, creep closer while trembling, snap, hold, pull apart elastically
    gap = [(22, None, None), (40, 32, "io"), (45, -2, "i5"), (47, 0, "o"), (84, None, None), (104, 70, "io"),
           (112, 56, "io"), (120, 60, "io")]
    for j, (g, sgn) in enumerate(((left, -1), (right, 1))):
        px = clip_loop(seq(60.0, gap, 0, f=lambda v: cx + sgn * v), OP)
        bob = seq(0.0, [(10, -8 * sgn, "io"), (22, 0, "io"), (110, None, None), (124, 8 * sgn, "io"), (138, -4 * sgn, "io"),
                        (150, 0, "io")], f=lambda v: cy + v)
        r = seq(sgn * 12.0, [(22, None, None), (40, sgn * 6.0, "io"), (45, 0.0, "i5"), (84, None, None), (104, sgn * 16.0, "io"),
                             (114, sgn * 10.0, "io"), (122, sgn * 12.0, "io")], op=OP)
        half = rig(c, f"h{j}", (cx, cy), p=Split(px, bob), r=r)
        rr = seq(0.0, [(24, None, None)])
        M.shake(rr, 24, 44, 2.2, 0.0, step=2, decay=1.0)
        rr.loop(OP)
        part(c, f"half{j}", g, half, (cx, cy), r=rr)
    # the click: sparks out of the seam, the joined pill thumps
    for k, (x1, y1) in enumerate(((cx - 40, 70), (cx + 60, 80), (cx - 20, 440), (cx + 50, 452))):
        y0 = 150 if y1 < 250 else 360
        M.particle(c, f"spk{k}", geo.spark(cx, y0, 34, 0.34), 45 + k, 20, (cx, y0), (x1, y1), None, anchor=(cx, y0),
                   rot=(0, 90), fall="o5", xease="o5", pop=0.12, fade=0.5)
    M.twinkle(c, "tw", cx + 150, cy - 110, 34, 64, 24)


# ================================================================ 21 🧸


def _bone(p0, p1, w=40, knob=30):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * knob * 0.62, dx / L * knob * 0.62
    ends = []
    for (x, y), s_ in ((p0, 1), (p1, -1)):
        ends += [geo.disc(x + nx, y + ny, knob * 0.78), geo.disc(x - nx, y - ny, knob * 0.78)]
    return U(geo.line([p0, p1], w, "flat"), *ends)


@emoji("21-teddy-skull", "🧸", "мишка, плюшевый, мило, жутко-мило, рейв", "teddy, plush, cute, creepy cute, rave",
       "готик-мишка с глазами-X качает головой под бас: два кивка, на третьей доле хедбэнг — уши-люверсы болтаются с отставанием, глаза жмурятся, кости позади щёлкают ножницами",
       op=120, series=SERIES)
def teddy(c):
    OP = 120
    hc = (256, 262)
    head = geo.disc(256, 256, 146, 32)
    muzzle = geo.ellipse(256, 316, 76, 56, 20)
    nose = geo.heart(256, 300, 58)
    nose = affinity.scale(nose, 1, -1, origin=(256, 300))          # upside-down heart nose
    mouth = U(geo.line([(256, 318), (256, 346)], 14), geo.line([(222, 348), (256, 346), (290, 348)], 14))
    eyes = U(*[U(geo.line([(x - 30, 196), (x + 30, 250)], 28), geo.line([(x - 30, 250), (x + 30, 196)], 28)) for x in (190, 322)])
    face_paths = geo.paths(head.difference(eyes)) + geo.paths(muzzle) + geo.paths(nose) + geo.paths(mouth)
    # rhythm (beat = 30f): nod, nod, headbang (accent), hold
    r = seq(0, [(2, None, None), (6, 3, "o"), (18, 0, "io"), (32, None, None), (36, -3, "o"), (48, 0, "io"),
                (58, None, None), (61, -6, "io"), (65, 11, "o5"), (74, -3, "io"), (82, 1.5, "io"), (90, 0, "io")], op=OP)
    y = seq(0.0, [(2, None, None), (6, 12, "o"), (18, 0, "io"), (32, None, None), (36, 12, "o"), (48, 0, "io"),
                  (58, None, None), (61, -10, "io"), (65, 20, "o5"), (74, -4, "io"), (84, 0, "io")], f=lambda v: 380 + v)
    y.loop(OP)
    s = seq([100, 100], [(2, None, None), (6, [103, 97], "o"), (18, [100, 100], "io"), (32, None, None),
                         (36, [103, 97], "o"), (48, [100, 100], "io"), (58, None, None), (61, [97, 103], "io"),
                         (65, [106, 94], "o5"), (74, [99, 101], "io"), (84, [100, 100], "io")])
    breathe(s, 92, 120, [100, 100], 0.6, 14)
    s.loop(OP)
    head_n = rig(c, "head", (256, 380), p=Split(256, y), s=s, r=r)
    # crossbones behind (scissor-clack on the accent)
    for j, sgn in enumerate((-1, 1)):
        a0 = (256 - sgn * 196, 468)
        a1 = (256 + sgn * 170, 250)
        br = seq(0, [(60, None, None), (65, sgn * 9, "o5"), (70, -sgn * 3, "io"), (78, 0, "io")], op=OP)
        part(c, f"bone{j}", _bone(a0, a1), None, (256, 372), r=br)
    # ears = eyelets, flopping 4f behind the head
    for j, sgn in enumerate((-1, 1)):
        ec = (256 + sgn * 118, 136)
        ear = geo.ring(*ec, 62, 26, 20)
        er = seq(0, [(6, None, None), (10, sgn * 8, "o"), (22, 0, "io"), (36, None, None), (40, sgn * 8, "o"), (52, 0, "io"),
                     (64, None, None), (68, -sgn * 18, "o"), (76, sgn * 10, "io"), (84, -sgn * 5, "io"), (92, 0, "io")], op=OP)
        base = (256 + sgn * 84, 184)
        part(c, f"ear{j}", ear, head_n, base, r=er)
    face = c.layer("face", [lot.group(face_paths + [lot.fill()], nm="face")], parent=head_n, p=hc, a=hc)
    # X eyes squeeze on the accent (a scaled copy of the eye holes closes them: evenodd XOR re-fills)
    es = seq([0, 0], [(62, None, None), (65, [110, 60], "o"), (72, [100, 90], "io"), (76, [0, 0], "i")], op=OP, loop_ease="lin")
    for k, x in enumerate((190, 322)):
        lid = geo.ellipse(x, 223, 44, 40, 12)
        face.shapes[0]["it"].insert(0, lot.group(geo.paths(lid.intersection(eyes)), nm=f"lid{k}", p=(x, 223), a=(x, 223), s=es))
