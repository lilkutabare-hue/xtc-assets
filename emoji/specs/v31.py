"""v3.1: the acid-smiley face family (the v1 brand face: black disc, logo-X eyes, features as holes),
logo-X reactions. Everything else brand-only (STYLE.md)."""
import math

from xtc import geo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import brand_x
from specs.reactions import seq, breathe, rig, part, stroke_line
from specs.v1a import drip_shape

FC = (256, 232)
R = 184
EY = 196


def head(mouth=None, eyes=True, r=R, fc=FC, eye_sq=1.0):
    """acid smiley: disc with the logo X for eyes and the mouth cut out."""
    g = geo.disc(fc[0], fc[1], r, 40)
    if eyes:
        g = g.difference(geo.U(brand_x(fc[0] - 82, EY, 112, 58 * eye_sq, bold=11), brand_x(fc[0] + 82, EY, 112, 58 * eye_sq, bold=11)))
    if mouth is not None:
        g = g.difference(mouth)
    return g


def smile(cx=256, cy=246, r=100, w=36):
    return geo.U(geo.brush(geo.arc(cx, cy, r, 24, 156, 24), w, taper=(0.8, 0.8), smooth=False),
                 geo.line([(cx - r - 6, cy + 26), (cx - r + 6, cy + 46)], 28), geo.line([(cx + r + 6, cy + 26), (cx + r - 6, cy + 46)], 28))


def flat(cx=256, cy=316, w_=150, w=34):
    return geo.brush([(cx - w_ / 2, cy), (cx + w_ / 2, cy)], w, taper=(0.8, 0.8), smooth=False)


def frown(cx=256, cy=336, r=96, w=34):
    return geo.brush(geo.arc(cx, cy + 40, r, 212, 328, 22), w, taper=(0.8, 0.8), smooth=False)


def tri(cx=256, cy=318, w_=170, h=110, r=18):
    t = geo.poly([(cx - w_ / 2, cy - h * 0.42), (cx + w_ / 2, cy - h * 0.42), (cx, cy + h * 0.58)])
    return t.buffer(-r).buffer(r)


def rim_drips(c, spec, t_slosh=None, parent=None):
    """latex drips hanging under the rim (black, outside the disc): (x, y0, y1, w)."""
    out = []
    for k, (x, y0, y1, w) in enumerate(spec):
        out.append(part(c, f"drip{k}", drip_shape(x, y0 - 30, y1, w), parent, (x, y0 - 30)))
    return out


# ================================================================ 139 😵 X_X


@emoji("139-xx", "😵", "х_х, вырубило, умер, кислота, нокаут, всё", "x_x, dead, knocked out, acid, ko, done",
       "кислотный смайл X_X: сверху прилетает удар — блин 112/86, язык-подтёк вываливается изо рта и болтается, голову мотает с затуханием, подтёки с кромки срываются каплями",
       op=150, series="face")
def xx(c):
    OP = 150
    g = head(flat(256, 322, 150))
    tongue_slot = geo.rrect(222, 304, 290, 342, 16)
    # body: hit at 30 (1f squash), damped wobble, breathing
    s = seq([100, 100], [(22, None, None), (28, [97, 104], "i"), (31, [112, 86], "slam"), (32, [112, 86], "lin"),
                         (40, [96, 105], "o"), (48, [102, 98], "io"), (56, [99, 101], "io"), (64, [100, 100], "io")])
    breathe(s, 70, 140, [100, 100], 0.8, 35)
    s.loop(OP)
    r = seq(0, [(31, None, None), (38, -7, "o"), (50, 5, "io"), (62, -3, "io"), (74, 1.5, "io"), (86, 0, "io")], op=OP)
    body = rig(c, "body", (256, FC[1] + R), s=s, r=r)
    hl = part(c, "head", g, body, FC)
    # the mouth slot opens when the tongue falls out (hole grows from the mouth line)
    ms = seq([100, 0], [(31, None, None), (36, [100, 100], "o"), (120, None, None), (132, [100, 0], "i")], op=OP, loop_ease="lin")
    geo.hole(hl, tongue_slot, nm="slot", p=(256, 306), a=(256, 306), s=ms)
    # tongue: a latex drip that flops out, swings with the head (lag 4f), sucked back at the end
    tg = drip_shape(256, 312, 470, 54)
    ts = seq([100, 0], [(31, None, None), (36, [94, 105], "o"), (40, [103, 97], "io"), (46, [100, 100], "io"),
                        (120, None, None), (126, [104, 96], "io"), (132, [100, 0], "i")], op=OP, loop_ease="lin")
    tr = seq(0, [(35, None, None), (42, 9, "o"), (54, -7, "io"), (66, 4, "io"), (78, -2, "io"), (90, 0, "io")], op=OP)
    part(c, "tongue", tg, body, (256, 312), s=ts, r=tr)
    # impact lines from the top (M8)
    for k, (p0, p1) in enumerate((((150, 70), (124, 36)), ((362, 70), (388, 36)), ((256, 40), (256, 20)))):
        e = Track(0, 0).hold(30).to(37, 100, "o").hold(OP)
        st = Track(0, 0).hold(32).to(39, 100, "i").hold(OP)
        c.layer(f"hit{k}", [geo.stroked([p0, p1], 22, e=e, s=st)], p=(0, 0), a=(0, 0), ip=30, op=40)
    # rim drips slosh on the hit, one snaps off
    for k, (x, y0, y1, w, lag) in enumerate(((150, 386, 442, 40, 0), (352, 372, 420, 36, 4))):
        ds = seq([100, 100], [(31 + lag, None, None), (36 + lag, [94, 108], "o"), (44 + lag, [104, 95], "io"), (52 + lag, [100, 100], "io")], op=OP)
        part(c, f"drip{k}", drip_shape(x, y0 - 30, y1, w), body, (x, y0 - 30), s=ds)
    M.particle(c, "drop", geo.drop(352, 420, 18, 42), 44, 26, (352, 420), (356, 470), None, anchor=(352, 420), fall="i5", pop=0.2, fade=0.3, s_end=50)


# ================================================================ 140 😂 laugh


@emoji("140-laugh", "😂", "ржу, смешно, лол, ахаха, кислота", "lol, laugh, lmao, crying laughing, acid",
       "кислотный смайл ржёт: голова трясётся басом (10f), X-глаза жмурятся, рот-треугольник раскрывается, из уголков глаз выстреливают латексные слёзы по дугам, подтёки на кромке пляшут",
       op=120, series="face")
def laugh(c):
    OP = 120
    mouth = tri(256, 322, 176, 116)
    g = head(mouth, eye_sq=0.62)
    s = seq([100, 100], [(6, None, None), (14, [106, 93], "io")])
    from specs.faces import cyc
    cyc(s, 14, 84, [95, 106], [105, 95], 10)
    s.to(92, [98, 102], "io").to(100, [101, 99], "io").to(108, [100, 100], "io").loop(OP)
    rr = Track(0, 0).hold(14)
    cyc(rr, 14, 84, -4, 4, 20, "io")
    rr.to(100, 0, "io").loop(OP)
    body = rig(c, "body", (256, FC[1] + R), s=s, r=rr)
    hl = part(c, "head", g, body, FC)
    # mouth hole "ha-ha": stretches 3f behind the body
    ms = Track([100, 100], 0).hold(9).to(17, [96, 112], "io")
    cyc(ms, 17, 87, [104, 76], [96, 114], 10)
    ms.to(100, [100, 100], "io").loop(OP)
    geo.hole(hl, mouth, nm="mouth", p=(256, 280), a=(256, 280), s=ms)
    # tears: latex drops shoot from the outer eye corners, arc over the free corners, land beside the head
    for side, d in enumerate((-1, 1)):
        x0 = 256 + d * 150
        for k in range(4):
            t0 = 16 + k * 16 + side * 6
            M.particle(c, f"tear{side}{k}", geo.drop(x0, 190, 28, 64), t0, 34, (x0, 190),
                       (256 + d * (200 - 10 * (k % 2)), 430 - 20 * (k % 3)), apex=84 + 14 * (k % 2),
                       parent=body, rot=(-d * 160, -d * 10), anchor=(x0, 190), s_peak=100 - 8 * (k % 2))
    for k, (x, y0, y1, w) in enumerate(((160, 384, 436, 38), (256, 410, 476, 46), (352, 384, 430, 36))):
        ds = Track([100, 100], 0).hold(12 + k * 3)
        cyc(ds, 12 + k * 3, 82 + k * 3, [96, 106], [104, 95], 10)
        ds.to(96 + k * 3, [100, 100], "io").loop(OP)
        part(c, f"drip{k}", drip_shape(x, y0 - 30, y1, w), body, (x, y0 - 30), s=ds)


# ================================================================ 141 😭 cry


@emoji("141-cry", "😭", "рыдаю, плачу, слёзы, горе, кислота", "sob, crying, tears, sad, acid",
       "кислотный смайл рыдает: из-под X-глаз по лицу бегут слёзы-прорези (негатив), у кромки становятся чёрными подтёками и капают; всхлипы подбрасывают голову, рот-волна дрожит",
       op=120, series="face")
def cry(c):
    OP = 120
    mouth = frown(256, 330, 90)
    g = head(mouth)
    y = Track(0.0, 0)
    s = Track([100, 100], 0)
    for t in (0, 40, 80):
        y.hold(t + 4).to(t + 10, -14.0, "decel").to(t + 22, 4.0, "slam").to(t + 30, 0.0, "io")
        s.hold(t + 4).to(t + 10, [96, 106], "io").to(t + 22, [106, 94], "o").to(t + 34, [100, 100], "io")
    y.loop(OP)
    s.loop(OP)
    base = (256, FC[1] + R)
    body = rig(c, "body", base, p=Split(256, _shift(y, base[1])), s=s)
    hl = part(c, "head", g, body, FC)
    # tear streams as holes: a chain of drops sliding down under each eye, wrapped through the loop
    for i, x in enumerate((256 - 82, 256 + 82)):
        for k in range(5):
            t0 = k * 24 + i * 6
            starts = [t0] + ([t0 - OP] if t0 + 30 > OP else [])
            for j, ts in enumerate(starts):
                hy = Track(EY + 40, ts).to(ts + 30, FC[1] + R - 20, "i")
                hs = Track([0, 0], ts).to(ts + 5, [100, 100], "o").hold(ts + 24).to(ts + 30, [0, 0], "i")
                geo.hole(hl, geo.drop(x, EY + 40, 17, 40), nm=f"t{i}{k}{j}", p=Split(x, _wrap(hy, OP)), a=(x, EY + 40), s=_wrap(hs, OP))
    # mouth wobble
    mr = Track(0, 0)
    for t in (0, 40, 80):
        mr.hold(t + 8).to(t + 12, -4, "io").to(t + 16, 4, "io").to(t + 20, -2, "io").to(t + 26, 0, "io")
    mr.loop(OP)
    geo.hole(hl, mouth, nm="mouth", p=(256, 330), a=(256, 330), r=mr)
    # black drips below the rim under each stream, drops fall from them
    for i, x in enumerate((256 - 76, 256 + 76)):
        ds = Track([100, 100], 0)
        for t in (0, 40, 80):
            ds.hold(t + 12 + i * 4).to(t + 20 + i * 4, [94, 110], "o").to(t + 34 + i * 4, [100, 100], "io")
        ds.loop(OP)
        part(c, f"drip{i}", drip_shape(x, FC[1] + R - 30, FC[1] + R + 62, 40), body, (x, FC[1] + R - 30), s=ds)
        for k in range(3):
            M.particle(c, f"d{i}{k}", geo.drop(x, FC[1] + R + 62, 16, 36), 22 + k * 40 + i * 6, 26, (x, FC[1] + R + 62), (x + (4 if i else -4), 500), None,
                       anchor=(x, FC[1] + R + 62), fall="i5", pop=0.2, fade=0.3, s_end=50, parent=body)


def _shift(tr, base):
    out = Track(base + tr.k[0][1], tr.k[0][0])
    out.k = [[t, base + v, e] for t, v, e in tr.k]
    return out


def _wrap(tr, op):
    """a track that may start after 0 (pad with a hold from 0) or before 0 / end after op (keys stay:
    rlottie interpolates keys outside [0, op]); the hole is scaled to 0 at both ends anyway."""
    k = [list(x) for x in tr.k]
    if k[0][0] > 0:
        k = [[0, k[0][1], "hold"]] + k
    out = Track(k[0][1], k[0][0])
    out.k = k
    if out.t < op:
        out.hold(op)
    out.k[-1][2] = None
    return out


# ================================================================ 142 😎 cool


@emoji("142-cool", "😎", "круто, кайф, чил, визор, стиль, кислота", "cool, sunglasses, chill, visor, swag, acid",
       "кислотный смайл в Y2K-визоре: визор-прорезь съезжает с макушки на глаза, кивок, по линзам бежит латексный блик и ✦ на кромке",
       op=150, series="face")
def cool(c):
    OP = 150
    g = head(smile(256, 250, 96))
    band = geo.rrect(256 - 168, EY - 42, 256 + 168, EY + 42, 42)
    lens = geo.U(geo.rrect(256 - 150, EY - 28, 256 - 20, EY + 28, 22), geo.rrect(256 + 20, EY - 28, 256 + 150, EY + 28, 22))
    s = seq([100, 100], [(36, None, None), (40, [104, 95], "o"), (48, [98, 102], "io"), (56, [100, 100], "io")])
    breathe(s, 60, 150, [100, 100], 0.7, 45)
    s.loop(OP)
    r = seq(0, [(44, None, None), (52, 4, "io"), (64, -2, "io"), (76, 0, "io")], op=OP)
    body = rig(c, "body", (256, FC[1] + R), s=s, r=r)
    hl = part(c, "head", g, body, FC)
    # the visor: a slot in the head (hole) that slides down from the crown, lenses ride in it
    vy = seq(EY - 118, [(14, None, None), (36, EY + 6, "slam"), (37, EY + 6, "lin"), (44, EY - 4, "o"), (50, EY, "io"),
                        (126, None, None), (142, EY - 118, "io")], op=OP)
    geo.hole(hl, band, nm="visor", p=Split(256, vy), a=(256, EY))
    ll = c.layer("lens", [geo.shape(lens, nm="lens")], parent=body, p=Split(256, vy), a=(256, EY))
    M.glare_sweep(c, ll, 256, EY, 60, 26, travel=340, angle=-30, parent=body, length=560, w1=26, w2=12, gap=12,
                  sparks=[(256 + 146, EY - 22, 30, 84, 22)])


# ================================================================ 143 🫠 melt


@emoji("143-melt", "🫠", "таю, плыву, растекаюсь, кислота, всё", "melting, melt, dying, acid, ugh",
       "кислотный смайл тает: голова тянется вниз и оседает в лужу, X-глаза и улыбка съезжают, с кромки растут подтёки и капают — и всё отматывается назад",
       op=180, series="face")
def melt(c):
    OP = 180
    fc = (256, 208)
    r = 168
    g = geo.disc(fc[0], fc[1], r, 40)
    top = (256, fc[1] - r)
    # melt = stretch down from the crown (keeps the top), pool = widen at the bottom; rewind at the end (M21)
    hs = seq([100, 100], [(20, None, None), (70, [104, 116], "is"), (100, [108, 122], "io"), (120, None, None), (150, [100, 100], "io3")], op=OP)
    hl = part(c, "head", g, None, top, s=hs)
    for i, x in enumerate((fc[0] - 78, fc[0] + 78)):
        ey = seq(EY - 24, [(20, None, None), (70, EY + 30 + i * 8, "is"), (100, EY + 60 + i * 12, "io"), (120, None, None), (150, EY - 24, "io3")], op=OP)
        es = seq([100, 100], [(20, None, None), (100, [110, 78], "io"), (120, None, None), (150, [100, 100], "io3")], op=OP)
        geo.hole(hl, brand_x(x, EY - 24, 106, 56, bold=11), nm=f"eye{i}", p=Split(x, ey), a=(x, EY - 24), s=es)
    my = seq(0, [(24, None, None), (74, 40, "is"), (104, 78, "io"), (120, None, None), (150, 0, "io3")], op=OP)
    ms = seq([100, 100], [(24, None, None), (104, [112, 70], "io"), (120, None, None), (150, [100, 100], "io3")], op=OP)
    geo.hole(hl, smile(256, 250, 90, 34), nm="mouth", p=Split(256, _shift(my, 250)), a=(256, 250), s=ms)
    # drips grow from the rim, fall as drops, retract on the rewind
    for k, (x, y0, y1, w, lag) in enumerate(((146, 350, 440, 42, 0), (256, 372, 468, 50, 6), (362, 350, 430, 40, 12))):
        ds = seq([100, 10], [(30 + lag, None, None), (80 + lag, [100, 100], "is"), (120, None, None), (150, [100, 10], "io3")], op=OP)
        part(c, f"drip{k}", drip_shape(x, y0 - 30, y1, w), None, (x, y0 - 30), s=ds)
        M.particle(c, f"drop{k}", geo.drop(x, y1 - 10, w * 0.36, w * 0.9), 84 + lag * 2, 24, (x, y1 - 10), (x, 474), None, anchor=(x, y1 - 10), fall="i5", pop=0.2, fade=0.3, s_end=50)


# ================================================================ 87 ❌ logo X stamp (REDO)


@emoji("87-cross", "❌", "нет, отказ, мимо, неверно, крест, стоп, x", "no, nope, wrong, denied, cross, rejected, x",
       "логотипный X отрывается от бумаги как штамп (под ним бледный оттиск), бьёт с разворота — 1 кадр 107/93, брызги-подтёки в стороны, ✦ по кромке",
       op=120, series="react")
def cross_x(c):
    OP = 120
    X = brand_x(256, 256, 424, 276, bold=10)
    io = Track(0, 0).hold(12).to(22, 34, "io").to(27, 34, "lin")
    io.k[-1][2] = "hold"
    io.k.append([28, 0, None])
    io.loop(OP, "lin")
    part(c, "imprint", X, None, (256, 256), o=io)
    root_s = seq([100, 100], [(10, None, None), (24, [84, 84], "io3"), (28, [107, 93], "slam"), (29, [107, 93], "lin"),
                              (34, [96, 104], "io"), (40, [101.5, 98.5], "io"), (47, [100, 100], "io")])
    breathe(root_s, 70, 120, [100, 100], 0.7, 25)
    root_s.loop(OP)
    root_r = seq(0, [(10, None, None), (24, -16, "io3"), (28, 3, "slam"), (34, -1.5, "io"), (41, 0, "io")], op=OP)
    px = seq(256.0, [(29, None, None)])
    M.shake(px, 29, 43, 6, 256.0, step=2, decay=0.78)
    px.loop(OP)
    root = rig(c, "stamp", (256, 256), p=Split(px, 256), s=root_s, r=root_r)
    xl = part(c, "x", X, root, (256, 256))
    M.glare_sweep(c, xl, 256, 256, 50, 26, travel=340, angle=-35, parent=root, length=560, w1=30, w2=12, gap=14,
                  sparks=[(256 + 170, 256 - 108, 36, 30, 22)])
    for k, (x0, y0, x1, y1) in enumerate([(256, 150, 256, 40), (366, 256, 474, 262), (256, 362, 250, 470),
                                          (146, 256, 38, 248), (330, 176, 400, 88), (182, 336, 112, 420)]):
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90
        rr = 20 if k < 4 else 15
        g = geo.rot(geo.drop(x0, y0, rr, rr * 2.6), ang, (x0, y0))
        M.particle(c, f"ink{k}", g, 28 + (k % 3), 22, (x0, y0), (x1, y1), None, anchor=(x0, y0), rot=(0, 0),
                   fall="o5", xease="o5", pop=0.12, fade=0.4)


# ================================================================ 90 ✨ chrome X (REDO)


@emoji("90-sparkles", "✨", "блеск, искры, хром, x, вау, глянец", "sparkles, shine, chrome, x, wow, gloss",
       "хромовый логотипный X делает тяжёлый оборот ребром (торец), на выходе лицом по кромке пробегают три ✦-блика по очереди и блик-штрих, досадка, короткий второй оборот-подмиг",
       op=150, series="react")
def sparkles_x(c):
    OP = 150
    cx, cy = 256, 256
    X = brand_x(cx, cy, 410, 270, bold=10)
    ss = seq([100, 100], [(8, None, None), (18, [94, 106], "io"), (26, [100, 100], "o"), (74, None, None), (78, [104, 97], "o"),
                          (86, [99, 101], "io"), (94, [100, 100], "io")], op=OP)
    body = rig(c, "body", (cx, cy + 150), s=ss)
    segs = [(18, 74, 0, 360, (0.35, 0.0, 0.14, 1.0)), (110, 136, 360, 720, (0.4, 0.0, 0.2, 1.0))]
    root, th, fr, bk = M.spin3d(c, "x", X, X, cx, cy, segs, thick=40, lip=28, parent=body, band_h=300)
    sp = [(cx - 136, cy - 88, 44, 72, 26), (cx + 136, cy + 88, 38, 80, 26), (cx + 136, cy - 88, 32, 88, 26), (cx - 136, cy + 88, 38, 136, 12)]
    M.glare_sweep(c, fr, cx, cy, 68, 26, travel=330, angle=-35, parent=root, sparks=sp, length=560, w1=34, w2=14, gap=14)
