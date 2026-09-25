"""v1 remakes (02, 03, 04, 10, 13-23): the v1 silhouettes redrawn bold for 24px (pack weight W=46,
min detail 28px) and animated from scratch in XTC MOTION. Techniques M# = moodboard.md."""
import math
import os

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
    """the logo X (1:1 letterform), see specs.drop.brand_x."""
    from specs.drop import brand_x as _bx
    return _bx(x, y, w, h, bold)


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


def _leg(root, knee, tip, w=34):
    return geo.brush([root, knee, tip], w, taper=(1.0, 0.55), smooth=True, n=8)


def spider_parts(cx=256, cy=300):
    """a real spider: round abdomen with the logo X as its back pattern, smaller head, 8 jointed legs."""
    abd = geo.ellipse(cx, cy + 46, 104, 116, 32)
    abd = abd.difference(brand_x(cx, cy + 50, 150, 70, bold=10))
    head = geo.disc(cx, cy - 92, 50, 24)
    neck = geo.rrect(cx - 34, cy - 70, cx + 34, cy - 40, 12)
    body = U(abd, head, neck)
    # legs: (root on the head side, knee, tip), mirrored for the left side
    L = [((cx + 36, cy - 118), (cx + 130, cy - 178), (cx + 210, cy - 112)),
         ((cx + 44, cy - 96), (cx + 156, cy - 130), (cx + 236, cy - 20)),
         ((cx + 44, cy - 74), (cx + 160, cy - 44), (cx + 226, cy + 84)),
         ((cx + 36, cy - 54), (cx + 132, cy + 30), (cx + 188, cy + 168))]
    legs = []
    for root, knee, tip in L:
        legs.append((root, _leg(root, knee, tip)))
        m = lambda p: (2 * cx - p[0], p[1])
        legs.append((m(root), _leg(m(root), m(knee), m(tip))))
    return body, legs


@emoji("03-sigil-x", "🕷️", "паук, x, xtc, жуть, свисаю, готика", "spider, x, xtc, creepy, hanging, goth",
       "паук с логотипным X на спинке висит на нити: подтягивается тремя рывками, поджимает лапы — срывается вниз, пружинит на нити, лапы раскидываются с перелётом, качается маятником, лапы подёргиваются по очереди",
       op=150, series=SERIES)
def sigil(c):
    OP = 150
    top = (256, 22)
    cx, cy = 256, 300
    body, legs = spider_parts(cx, cy)
    pr = seq(-3, [(10, 3, "io"), (20, 0, "io"), (86, None, None), (98, 6, "io"), (110, -4.5, "io"), (122, 3.2, "io"),
                  (134, -1.8, "io"), (144, -3, "io")], op=OP)
    fit_ = rig(c, "fit", (256, 22), s=(84, 84), p=(256, 34))
    pend = rig(c, "pendulum", top, parent=fit_, r=pr)
    dy = [(18, None, None), (24, -28, "o"), (27, None, None), (33, -50, "o"), (36, None, None), (42, -66, "o"),
          (54, None, None), (62, 22, "i5"), (69, -30, "o"), (76, 10, "io"), (82, -8, "io"), (88, 0, "io")]
    y = seq(0.0, dy, f=lambda v: cy + v)
    y.loop(OP)
    ss = seq([100, 100], [(18, None, None), (24, [95, 106], "o"), (27, [100, 100], "io"), (33, [95, 106], "o"),
                          (36, [100, 100], "io"), (42, [95, 106], "o"), (46, [100, 100], "io"),
                          (54, None, None), (60, [90, 112], "i"), (62, [112, 88], "o"), (69, [95, 106], "io"),
                          (76, [102, 98], "io"), (84, [100, 100], "io")], op=OP)
    spider = rig(c, "spider", (cx, cy), parent=pend, p=Split(cx, y), s=ss)
    # legs: tuck up on every pull and on the drop (rotate about the root), splay with overshoot on the bounce,
    # then twitch one after another while it hangs
    for k, (root, g) in enumerate(legs):
        sgn = 1 if root[0] > cx else -1
        up = -sgn * 22
        r = seq(0, [(18, None, None), (24, up * 0.5, "o"), (30, 0, "io"), (33, up * 0.5, "o"), (39, 0, "io"), (42, up * 0.5, "o"), (48, 0, "io"),
                    (54, None, None), (60, up, "i"), (64, -up * 0.6, "o"), (72, up * 0.25, "io"), (80, 0, "io"),
                    (96 + k * 5, None, None), (100 + k * 5, -sgn * 5, "io"), (106 + k * 5, 0, "io")], op=OP)
        part(c, f"leg{k}", g, spider, root, r=r)
    part(c, "body", body, spider, (cx, cy))
    L = cy - 92 - 50 - top[1]
    e = seq(100.0, dy, f=lambda v: 100.0 * (L + v) / L)
    e.loop(OP)
    c.layer("thread", [stroke_line([top, (256, cy - 142)], 24, nm="thread", e=e)], parent=pend, p=top, a=top)


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
                   (58, -34, "io"), (84, 0, "io")], f=lambda v: hc[1] + v)
    hy.loop(OP)
    hs = seq([100, 100], [(10, None, None), (14, [104, 96], "io"), (20, [95, 106], "o"), (28, [103, 97], "io"),
                          (34, [95, 106], "o"), (44, [100, 100], "io"), (84, None, None), (88, [103, 97], "o"),
                          (94, [100, 100], "io")], op=OP)
    body = rig(c, "body", hc, p=Split(hc[0], hy), s=hs)
    # wing stroke (deg, + = down for the right wing): antic up, down, up, down, glide
    flap = [(6, None, None), (13, -22, "io"), (20, 24, "io3"), (27, -20, "io"), (34, 26, "io3"), (44, -4, "io"),
            (58, 0, "io"), (84, None, None), (90, 5, "io"), (98, 0, "io")]
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
    bow = bow_o.difference(geo.heart(cx, top + 84, 118))
    collar = geo.rrect(cx - 44, top + 186, cx + 44, top + 214, 12)
    shaft = geo.rrect(cx - 27, top + 170, cx + 27, bottom, 14)
    teeth = U(geo.rect(cx + 20, bottom - 124, cx + 86, bottom - 88), geo.rect(cx + 20, bottom - 58, cx + 100, bottom - 22),
              geo.rect(cx + 20, bottom - 96, cx + 66, bottom - 58))
    return U(bow, collar, shaft, teeth.buffer(6).buffer(-6))


@emoji("10-club-key", "🔑", "ключ, открыть, доступ, клуб, пропуск", "key, unlock, access, club, pass",
       "клубный ключ-сердце с X в головке входит в скважину и туго проворачивается ребром — щелчок, дрожь — его отпускают, и он докручивается по инерции тяжёлым оборотом: X → люверс на обороте → снова X, на головке ✦",
       op=150, series=SERIES)
def key(c):
    OP = 150
    cx, cy = 256, 256
    # club key: the logo X sits in the heart bow on the face, a grommet (eyelet) on the back -
    # the momentum spin flashes X / eyelet / X
    front = U(_key(cx), brand_x(cx, 108, 40, 32, bold=8))
    back = U(_key(cx), geo.eyelet(cx, 108, 24, 10))
    # insert (push down), turn to edge-on with resistance, click, back out, momentum spin, settle
    T = 52                                   # the story starts after a calm opening (the key face-on)
    y = seq(0.0, [(T + 0, None, None), (T + 8, 14, "io"), (T + 34, None, None), (T + 40, -16, "o"), (T + 78, None, None),
                  (T + 88, 0, "io")], f=lambda v: cy + v)
    y.loop(OP)
    s = seq([100, 100], [(4, [101, 99], "io"), (16, [100, 100], "io")])
    breathe(s, 20, T - 2, [100, 100], 0.7, 14)
    s.hold(T).to(T + 8, [103, 97], "io").to(T + 12, [100, 100], "io").hold(T + 25).to(T + 27, [98, 102], "o")
    s.to(T + 31, [100, 100], "io").hold(T + 82).to(T + 86, [103, 97], "o").to(T + 94, [100, 100], "io")
    s.loop(OP)
    px = seq(float(cx), [(T + 26, None, None)])
    M.shake(px, T + 26, T + 34, 4, float(cx), step=2, decay=0.75)
    px.loop(OP)
    body = rig(c, "body", (cx, cy), p=Split(px, y), s=s)
    segs = [(T + 10, T + 24, 0, 88, "io3"), (T + 24, T + 27, 88, 96, "o"), (T + 27, T + 32, 96, 90, "io"),
            (T + 38, T + 80, 90, 372, (0.3, 0.0, 0.14, 1.0)), (T + 80, T + 90, 372, 360, "io")]
    M.spin3d(c, "key", front, back, cx, cy, segs, thick=42, lip=22, parent=body)
    M.twinkle(c, "tw", cx - 118, 70, 36, T + 82, 16, parent=body)


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
    T = 30                                    # calm opening with the wire on (the sheet frame shows it)
    hc = (256, 262)
    base = _heart_pts(256, 262, 404)
    wy = 282
    pinched = _pinch(base, 262, 0.3, wy, 80)
    hp = Track(poly_path(base), 0).hold(T + 16).to(T + 40, poly_path(pinched), "io").hold(T + 48)
    hp.to(T + 53, poly_path(base), "snap").loop(OP)
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
        # cinch towards the middle, snap off and fly apart spinning on the burst, regrow from the tail and pull tight;
        # position and anchor switch together (hold keys) so the group never jumps
        p = seq(list(mid), [(T + 16, None, None), (T + 40, [mid[0] - sgn * 10, mid[1]], "io"), (T + 49, None, None),
                            (T + 58, [mid[0] + sgn * 60, mid[1] - 30 + j * 50], "o5")])
        p.k[-1][2] = "hold"
        p.k.append([T + 59, list(end), None])
        p.k[-1][2] = "hold"
        p.k.append([T + 108, list(mid), None])
        p.loop(OP, "lin")
        r = seq(0, [(T + 16, None, None), (T + 40, -sgn * 4, "io"), (T + 49, None, None), (T + 58, sgn * 60, "o5")])
        r.k[-1][2] = "hold"
        r.k.append([T + 59, -sgn * 30, None])
        r.hold(T + 78).to(T + 100, sgn * 6, "io").to(T + 108, 0, "io").loop(OP)
        sc = seq([100, 100], [(T + 49, None, None), (T + 58, [0, 0], "o5")])
        sc.hold(T + 78).to(T + 98, [104, 104], "o").to(T + 106, [100, 100], "io").loop(OP)
        a_ = Track(list(mid), 0)
        a_.k[-1][2] = "hold"
        a_.k.append([T + 59, list(end), None])
        a_.k[-1][2] = "hold"
        a_.k.append([T + 108, list(mid), None])
        a_.loop(OP, "lin")
        groups.append(lot.group(geo.paths(hg), nm=f"wire{j}", p=p, a=a_, r=r, s=sc))
    # freed: a ✦ glint flashes through the lacquer (XOR cut)
    gx, gy = 160, 172
    gs = seq([0, 0], [(T + 54, None, None), (T + 59, [120, 120], "ox"), (T + 65, [100, 100], "io"), (T + 74, [0, 0], "i")],
             op=OP, loop_ease="lin")
    gr = seq(-20, [(T + 54, None, None), (T + 74, 20, "os")], op=OP, loop_ease="lin")
    glint = lot.group(geo.paths(geo.spark(gx, gy, 46, 0.34)), nm="glint", p=(gx, gy), a=(gx, gy), s=gs, r=gr)
    grp = lot.group([lot.sh(hp, "heart")] + groups + [glint, lot.fill()], nm="heart")
    s = seq([100, 100], [])
    breathe(s, 0, T + 10, [100, 100], 0.8, 18)
    s.hold(T + 40).to(T + 47, [96, 97], "io").to(T + 51, [109, 108], "snap").to(T + 58, [96, 97], "io")
    s.to(T + 65, [102, 101.5], "io").to(T + 73, [100, 100], "io")
    breathe(s, T + 76, 150, [100, 100], 0.8, 22)
    s.loop(OP)
    px = seq(256.0, [(T + 22, None, None)])
    M.shake(px, T + 22, T + 46, 3, 256.0, step=2, decay=1.0)
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
    heart = heart.difference(geo.rot(geo.ellipse(150, 230, 46, 22).difference(geo.ellipse(158, 244, 46, 22)), -35, (150, 230)))
    dg = _dagger(top=30)
    dg = affinity.scale(dg, 0.86, 0.86, origin=(256, 256))
    dg = geo.rot(dg, 30, (256, 256))
    dg = affinity.translate(dg, 4, 8)
    b = dg.bounds
    dc = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    far = (370, 140)
    # stuck (calm opening) -> pushed out and flung tumbling -> heart alone -> thrown back spinning -> recoil
    p = seq(list(dc), [(56, None, None), (62, [dc[0] + 18, dc[1] - 30], "io"), (72, list(far), "o5"), (84, None, None),
                       (94, list(dc), "lin")], op=OP)
    r = seq(0, [(56, None, None), (62, -6, "io"), (72, 240, "o5"), (84, -500, "hold"), (94, 0, "lin")], op=OP)
    s = seq([100, 100], [(62, None, None), (70, [0, 0], "o"), (84, [26, 26], "hold"), (93, [100, 100], "i")], op=OP)
    dgrp = lot.group(geo.paths(dg), nm="dagger", p=p, a=list(dc), r=r, s=s)
    grp = lot.group([lot.group(geo.paths(heart), nm="heart"), dgrp, lot.fill()], nm="dh")
    hp = seq(list(hc), [(94, None, None), (97, [hc[0] - 20, hc[1] + 12], "o"), (104, [hc[0] + 6, hc[1] - 4], "io"),
                        (110, [hc[0] - 2, hc[1] + 1], "io"), (116, list(hc), "io")], op=OP)
    hr = seq(0, [(94, None, None), (97, -8, "o"), (104, 3, "io"), (110, -1, "io"), (116, 0, "io")], op=OP)
    hs = seq([100, 100], [])
    breathe(hs, 0, 50, [100, 100], 0.8, 16)
    hs.hold(54).to(60, [96, 104], "io").to(64, [104, 96], "o").to(70, [100, 100], "io").to(76, [103, 103], "io")
    hs.to(84, [100, 100], "io").hold(94).to(96, [94, 106], "o").to(102, [103, 98], "io").to(110, [100, 100], "io")
    hs.loop(OP)
    c.layer("dh", [grp], p=hp, a=hc, s=hs, r=hr)
    # drops tear off the wound's lower lip and fall
    for k, (t0, x0) in enumerate(((98, 176), (22, 186))):
        M.particle(c, f"drop{k}", geo.drop(x0, 404, 18, 42), t0, 26, (x0, 404), (x0 - 6, 478), None, anchor=(x0, 404),
                   fall="i5", pop=0.3, fade=0.25, s_end=40)


# ================================================================ 16 💖


@emoji("16-heart-pill", "💖", "сердце xtc, лого, крест, люблю, xtc", "xtc heart, logo, cross, love, xtc",
       "сердце с идеальным крест-лого X·XTC·C насквозь: лаб-даб на бит (быстро вверх, вдвое медленнее вниз), микро-досадка, покой; лого на месте",
       op=120, series=SERIES)
def heart_pill(c):
    OP = 120
    from specs.drop import cross_letters
    heart = geo.heart(256, 262, 420)
    L = cross_letters(256, 262, lh=44, width=250)
    g = heart.difference(geo.U(*[q for q, _ in L.values()]))
    hb = heart.bounds
    s = seq([100, 100], [(8, None, None), (13, [110, 110], "snap"), (23, [100, 100], "io"), (28, [105, 105], "snap"),
                         (38, [99, 99], "io"), (46, [100.4, 100.4], "io"), (54, [100, 100], "io")], op=OP)
    part(c, "heart", g, None, (256, hb[3]), s=s)


# ================================================================ 17 🪽


@emoji("17-winged-x", "🪽", "крылья, лечу, свобода, взлёт, ангел", "wings, flying, free, take off, angel",
       "X с настоящими крыльями: поджимает их (антиципация), мощный взмах — взлетает с растяжкой, перья волной отстают от «руки» крыла, трепещет, планирует; одно перо отрывается и кружит вниз",
       op=150, series=SERIES)
def winged(c):
    OP = 150
    xc = (256, 372)
    xg = brand_x(256, 372, 176, 124, bold=14)
    y = seq(0.0, [(16, None, None), (26, 8, "io"), (36, -60, "o"), (44, -66, "io"), (52, -58, "io"), (60, -64, "io"),
                  (90, 0, "io")], f=lambda v: xc[1] + v)
    y.loop(OP)
    s = seq([100, 100], [(16, None, None), (26, [108, 92], "io"), (32, [93, 108], "o"), (42, [100, 100], "io"),
                         (89, None, None), (93, [104, 96], "o"), (100, [100, 100], "io")])
    breathe(s, 104, 150, [100, 100], 0.8, 15)
    s.loop(OP)
    body = rig(c, "body", xc, p=Split(xc[0], y), s=s)
    # wing stroke (+ = down for the right wing): tuck up (antic), power down, flutter, glide
    stroke = [(16, None, None), (26, -26, "io"), (32, 18, "io3"), (37, -12, "io"), (41, 8, "io"), (45, -8, "io"),
              (49, 6, "io"), (54, -3, "io"), (60, 0, "io"), (96, None, None), (102, 5, "io"), (110, 0, "io")]
    for side in (-1, 1):
        m = lambda p: (256 + side * (p[0] - 256), p[1])
        root = m((300, 318))
        arm_pts = [m(p) for p in ((298, 318), (336, 246), (380, 190), (424, 162))]
        ang = m((0, 0))
        wing = rig(c, f"wing{side}", root, parent=body, r=seq(0, stroke, op=OP, f=lambda v: side * v))
        part(c, f"arm{side}", geo.brush(arm_pts, 58, taper=(1.0, 0.55), smooth=True, n=6), wing, root)
        # primaries hang off the arm; each lags the stroke a little more (a wave runs out along the wing)
        for i, (t, ln, a_) in enumerate(((0.36, 104, 100), (0.56, 114, 90), (0.76, 110, 80), (0.94, 96, 70))):
            L = LineString(arm_pts)
            q = L.interpolate(L.length * t)
            at = (q.x, q.y)
            a = math.radians(a_ if side > 0 else 180 - a_)
            tip = (at[0] + math.cos(a) * ln, at[1] + math.sin(a) * ln)
            mid = (at[0] + math.cos(a) * ln * 0.5, at[1] + math.sin(a) * ln * 0.5)
            fg = geo.brush([at, mid, tip], 50, taper=(1.0, 0.3), smooth=False)
            lag = 2 + 2 * i
            fr = clip_loop(seq(0, stroke, lag, f=lambda v: side * v * 0.35), OP)
            part(c, f"p{side}{i}", fg, wing, at, r=fr)
    part(c, "X", xg, body, xc)
    # one primary comes loose on the power stroke and spirals down
    fx, fy = 404, 250
    fth = geo.brush([(fx, fy - 50), (fx + 5, fy), (fx, fy + 50)], 42, taper=(0.9, 0.18), smooth=True, n=4)
    M.particle(c, "loose", fth, 34, 90, (fx, fy), (432, 420), None, anchor=(fx, fy), rot=(20, 200),
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
    T = 40
    y = seq(0.0, [(T + 14, None, None), (T + 22, 8, "io"), (T + 36, -44, "o"), (T + 46, -48, "io"), (T + 60, 0, "i5"),
                  (T + 66, -10, "o"), (T + 72, 0, "i")], f=lambda v: gy + v)
    y.loop(OP)
    s = seq([100, 100], [])
    breathe(s, 0, T + 10, [100, 100], 0.8, 22)
    s.hold(T + 14).to(T + 22, [107, 92], "io").to(T + 28, [95, 106], "o").to(T + 36, [100, 100], "io")
    s.hold(T + 59).to(T + 61, [110, 90], "o").to(T + 68, [97, 103], "io").to(T + 76, [100, 100], "io")
    s.loop(OP)
    body = rig(c, "body", (cx, gy), p=Split(cx, y), s=s)
    turn = rig(c, "turn", (cx, cy), parent=body, r=90)
    segs = [(T + 20, T + 26, 0, -16, "io"), (T + 26, T + 60, -16, 720, (0.3, 0.0, 0.3, 1.0)),
            (T + 60, T + 68, 720, 726, "o"), (T + 68, T + 76, 726, 720, "io")]
    M.spin3d(c, "star", f_r, b_r, cx, cy, segs, thick=40, lip=26, parent=turn)
    M.twinkle(c, "tw", cx + 118, cy - 150, 38, T + 78, 26, parent=body)


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
    xg = brand_x(cx, cy - 22, 184, 80, bold=13)
    coin = body.difference(groove).difference(xg)
    zig = [(cx + 6, 60), (cx - 14, 150), (cx + 16, 210), (cx - 16, 262), (cx + 14, 320), (cx - 6, 420)]
    left_region = geo.poly(zig + [(0, 420), (0, 60)])
    left, right = coin.intersection(left_region), coin.difference(left_region)
    # separation (px each side): hover apart, creep closer while trembling, snap, hold, pull apart elastically
    T = 20
    gap = [(T + 22, None, None), (T + 40, 32, "io"), (T + 45, -2, "i5"), (T + 47, 0, "o"), (T + 84, None, None),
           (T + 104, 70, "io"), (T + 112, 56, "io"), (T + 120, 60, "io")]
    for j, (g, sgn) in enumerate(((left, -1), (right, 1))):
        px = clip_loop(seq(60.0, gap, 0, f=lambda v: cx + sgn * v), OP)
        bob = seq(0.0, [(10, -8 * sgn, "io"), (22, 0, "io"), (34, 6 * sgn, "io"), (T + 22, 0, "io"), (T + 118, None, None),
                        (T + 124, 6 * sgn, "io"), (150, 0, "io")], f=lambda v: cy + v)
        r = seq(sgn * 12.0, [(T + 22, None, None), (T + 40, sgn * 6.0, "io"), (T + 45, 0.0, "i5"), (T + 84, None, None),
                             (T + 104, sgn * 16.0, "io"), (T + 114, sgn * 10.0, "io"), (T + 122, sgn * 12.0, "io")], op=OP)
        half = rig(c, f"h{j}", (cx, cy), p=Split(px, bob), r=r)
        rr = seq(0.0, [(T + 24, None, None)])
        M.shake(rr, T + 24, T + 44, 2.2, 0.0, step=2, decay=1.0)
        rr.loop(OP)
        part(c, f"half{j}", g, half, (cx, cy), r=rr)
    # the click: sparks out of the seam, the joined pill thumps
    for k, (x1, y1) in enumerate(((cx - 40, 70), (cx + 60, 80), (cx - 20, 440), (cx + 50, 452))):
        y0 = 150 if y1 < 250 else 360
        M.particle(c, f"spk{k}", geo.spark(cx, y0, 34, 0.34), T + 45 + k, 20, (cx, y0), (x1, y1), None, anchor=(cx, y0),
                   rot=(0, 90), fall="o5", xease="o5", pop=0.12, fade=0.5)
    M.twinkle(c, "tw", cx + 150, cy - 110, 34, T + 64, 24)


# ================================================================ 21 🧸


def _bone(p0, p1, w=40, knob=30):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * knob * 0.62, dx / L * knob * 0.62
    ends = []
    for (x, y), s_ in ((p0, 1), (p1, -1)):
        ends += [geo.disc(x + nx, y + ny, knob * 0.78), geo.disc(x - nx, y - ny, knob * 0.78)]
    return U(geo.line([p0, p1], w, "flat"), *ends)


@emoji("21-teddy-skull", "🧸", "мишка, челикс, xtc, кости, наш персонаж", "teddy, mascot, xtc, crossbones, character",
       "мишка XTC (рисунок клиента 1:1): тяжёлый кивок под бас — два кивка и хедбэнг на третьей доле с досадкой, звёзды у уха подрастают по очереди, кости стоят",
       op=120, series=SERIES)
def teddy(c):
    OP = 120
    g = geo.svg(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v1", "rec", "teddy.svg"))
    polys = sorted(geo._polys(g), key=lambda p: -p.area)
    body = polys[0]
    b_ = body.bounds
    stars = [p for p in polys[1:] if p.centroid.x > 330 and p.centroid.y < 260]
    rest = [p for p in polys[1:] if p not in stars]
    ax, ay = (b_[0] + b_[2]) / 2, b_[3]
    r = seq(0, [(2, None, None), (6, 3, "o"), (18, 0, "io"), (32, None, None), (36, -3, "o"), (48, 0, "io"),
                (58, None, None), (61, -5, "io"), (65, 9, "o5"), (74, -3, "io"), (82, 1.5, "io"), (90, 0, "io")], op=OP)
    s = seq([100, 100], [(2, None, None), (6, [103, 97], "o"), (18, [100, 100], "io"), (32, None, None),
                         (36, [103, 97], "o"), (48, [100, 100], "io"), (58, None, None), (61, [97, 103], "io"),
                         (65, [106, 94], "o5"), (74, [99, 101], "io"), (84, [100, 100], "io")])
    breathe(s, 92, 120, [100, 100], 0.6, 14)
    s.loop(OP)
    fit_ = rig(c, "fit", (262, 256), s=(82, 82))
    head = rig(c, "head", (ax, ay), parent=fit_, s=s, r=r)
    part(c, "body", geo.U(body, *rest), head, (ax, ay))
    for k, p in enumerate(stars):
        cx_, cy_ = p.centroid.x, p.centroid.y
        t0 = 8 + k * 30
        ss = seq([100, 100], [(t0, None, None), (t0 + 8, [122, 122], "o"), (t0 + 24, [100, 100], "io"), (t0 + 60, None, None), (t0 + 68, [118, 118], "o"), (t0 + 84, [100, 100], "io")], op=OP)
        part(c, f"star{k}", p, head, (cx_, cy_), s=ss)


# ================================================================ 22 💕


def _glyph_lt():
    return geo.brush([(214, 136), (58, 254), (214, 372)], 60, taper=(0.85, 0.85), smooth=False)


def _glyph_3():
    top = geo.arc(360, 178, 76, 200, 440, 24)
    bot = geo.arc(360, 318, 86, 280, 520, 24)
    pts = top + [(372, 250), (350, 250)] + bot
    return geo.brush(pts, 58, taper=(0.85, 0.85), smooth=True, n=3)


@emoji("22-kiss-less3", "💕", "люблю, <3, чмок, сердечко, обнимаю", "love, <3, kiss, heart, hugs",
       "«<» и «3» подмигивают друг другу, съезжаются — и плавятся в одно сердце: «чмок», ✦, сердце держится, потом снова распадается на <3",
       op=120, series=SERIES)
def less3(c):
    OP = 120
    N = 72
    heart = geo.heart(256, 262, 420)
    hl = heart.intersection(geo.rect(0, 0, 256, 512))
    hr = heart.intersection(geo.rect(256, 0, 512, 512))
    lt, th = _glyph_lt(), _glyph_3()
    A = poly_path(geo.resample(lt, N, start_angle=-40))
    Ah = poly_path(geo.resample(hl, N, start_angle=-40))
    B = poly_path(geo.resample(th, N, start_angle=150))        # 150°: the only alignment without a torn fragment mid-morph
    Bh = poly_path(geo.resample(hr, N, start_angle=150))
    for nm, g0, g1, sgn, cx_ in (("lt", A, Ah, -1, 136), ("three", B, Bh, 1, 376)):
        shp = Track(g0, 0).hold(54).to(67, g1, "io3").hold(96).to(108, g0, (0.3, 0.0, 0.2, 1.0)).loop(OP)
        # slide together (antic away first), meet, the heart thumps once, then spring apart
        dx = seq(0.0, [(40, None, None), (48, sgn * 10, "io"), (59, -sgn * 6, "i"), (67, 0, "o"),
                       (94, None, None), (100, sgn * 4, "io"), (108, -sgn * 14, "o"), (116, 0, "io")],
                 f=lambda v: 256 + v)
        dx.loop(OP)
        wink = seq([100, 100], [(4 + (6 if sgn > 0 else 0), None, None), (8 + (6 if sgn > 0 else 0), [104, 92], "o"),
                                (14 + (6 if sgn > 0 else 0), [100, 100], "io")])
        wink.loop(OP)
        c.layer(nm, [lot.group([lot.sh(shp, nm), lot.fill()], nm=nm)], p=Split(dx, 262), a=(256, 262), s=wink)
    # the kiss: one thump of the whole heart (a null over both halves would re-parent; scale a copy instead)
    thump = seq([0, 0], [(67, None, None), (68, [100, 100], "hold"), (71, [114, 112], "snap"), (77, [96, 97], "io"),
                         (83, [101, 101], "io"), (89, [100, 100], "io"), (95, None, None), (96, [0, 0], "hold")])
    thump.k[1][2] = "hold"
    thump.k[-3][2] = "hold"
    thump.loop(OP, "lin")
    kiss = part(c, "kiss", heart, None, (256, 262), s=thump, ip=67, op=97)
    M.glare_sweep(c, kiss, 256, 262, 70, 22, travel=300)


# ================================================================ 23 🌟


@emoji("23-dot-star", "🌟", "звезда, сияю, огни, топ, праздник", "star, shine, lights, glowing, party",
       "звезда из лампочек: по контуру бежит огонёк — каждая лампа на миг раскрывается люверсом (волна 2f), обегает круг — и звезда вспыхивает сплошной, в сердцевине проступает X-вырез, ✦; потом рассыпается обратно, лампы перемигиваются люверсами",
       op=150, series=SERIES)
def dot_star(c):
    OP = 150
    cx, cy, R, r = 256, 270, 198, 86
    verts = []
    for k in range(10):
        a = math.radians(-90 + 36 * k)
        rr = R if k % 2 == 0 else r
        verts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    dots = []
    for k in range(10):
        p0, p1 = verts[k], verts[(k + 1) % 10]
        dots.append(p0)
        dots.append(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2))
    # the flash: a solid star grows under the lamps, holds, and sinks back
    star = geo.star(cx, cy, R, r, 5, -90).buffer(8, join_style=1).buffer(-8, join_style=1)
    star = star.difference(brand_x(cx, cy + 6, 96, 74, bold=12))      # the lights converge into the logo
    ss = seq([0, 0], [(56, None, None), (62, [108, 108], "snap"), (68, [98, 98], "io"), (74, [100, 100], "io"),
                      (92, None, None), (102, [0, 0], "i")], op=OP, loop_ease="lin")
    part(c, "flash", star, None, (cx, cy), s=ss)
    for k, (x, y) in enumerate(dots):
        t0 = 8 + 2 * k                                   # the running light
        big = k % 2 == 0
        rd = 25 if big else 21
        ds = seq([100, 100], [(t0, None, None), (t0 + 3, [165, 165], "o"), (t0 + 9, [100, 100], "io"),
                              (54 + (k % 4), None, None), (58 + (k % 4), [140, 140], "o"), (66, [118, 118], "io"),
                              (92, None, None), (100 + k % 5, [80, 80], "io"), (110 + k % 5, [100, 100], "io")], op=OP)
        lamp = part(c, f"dot{k}", geo.disc(x, y, rd + 2, 12), None, (x, y), s=ds)
        # a lit lamp opens into an eyelet: its hole flashes as the running light passes (and on the recap)
        hs = seq([0, 0], [(t0, None, None), (t0 + 3, [100, 100], "ox"), (t0 + 12, [0, 0], "i"),
                          (104 + k % 5, None, None), (108 + k % 5, [80, 80], "o"), (116 + k % 5, [0, 0], "i")], op=OP, loop_ease="lin")
        geo.hole(lamp, geo.disc(x, y, rd * 0.5, 10), nm="lit", p=(x, y), a=(x, y), s=hs)
    M.twinkle(c, "tw", cx + 150, cy - 170, 36, 64, 26)
