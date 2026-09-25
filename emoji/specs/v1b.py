"""v1 objects 24-32, 41, 43 reworked (bold redraws of the v1 silhouettes, new stories)."""
import math
import os

from xtc import geo, kao as K, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import brand_word, speed_lines

V1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v1", "tg")          # v1 sources (vendored)


def lay(c, nm, g, anchor, parent=None, **kw):
    return c.layer(nm, [geo.shape(g, nm=nm)], parent=parent, p=kw.pop("p", anchor), a=anchor, **kw)


@emoji("24-print-scan", "🫆", "отпечаток, это я, подтверждаю, доступ, скан", "fingerprint, its me, verified, access, scan",
       "отпечаток-гравюра в рамке сканера: линия пробегает сверху вниз, уголки рамки защёлкиваются, гребни вспыхивают волной от центра, ✦",
       op=150, series="v1")
def print_scan(c):
    cx, cy = 256, 280
    ridges = []
    for k in range(4):
        rx = 40 + k * 46
        ry = rx * 1.18
        top = [(cx + rx * math.cos(math.radians(a)), cy - 20 + ry * math.sin(math.radians(a))) for a in range(180, 361, 6)]
        pts = [(cx - rx, cy + 44 + k * 20)] + top + [(cx + rx, cy + 30 + k * 12)]
        ridges.append(geo.brush(pts, 32, taper=(0.6, 0.66), smooth=False))
    core = geo.brush([(cx, cy - 20), (cx, cy + 36)], 32, (0.8, 0.8), False)
    parts = [core] + ridges
    for k, g in enumerate(parts):
        t0 = 64 + k * 4
        sk = Track([100, 100], 0).hold(t0).to(t0 + 5, [106, 106], "snap").to(t0 + 14, [100, 100], "io").loop(150)
        lay(c, f"r{k}", g, (cx, cy), s=sk)
    # viewfinder corners: open wide while scanning, snap onto the print when done
    L = 60
    for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x0, y0 = cx + sx * 212, cy - 8 + sy * 204
        g = geo.line([(x0, y0 - sy * -0 + sy * -L * 0 - sy * L * -0 + sy * -L), (x0, y0), (x0 - sx * L, y0)], 28, "round", "round")
        pp = Track([x0 + sx * 10, y0 + sy * 10], 0).hold(56).to(62, [x0 - sx * 8, y0 - sy * 8], "slam").to(70, [x0, y0], "io").hold(128).to(146, [x0 + sx * 10, y0 + sy * 10], "io").loop(150)
        lay(c, f"corner{k}", g, (x0, y0), p=pp)
    # scan line sweeping down (visible through the gaps between the ridges)
    bar = geo.rrect(cx - 196, cy - 9, cx + 196, cy + 9, 9)
    py = Track(cy - 190, 0).hold(10).to(56, cy + 190, "io").hold(150)
    lay(c, "scan", bar, (cx, cy), p=Split(cx, py), ip=10, op=57)
    M.twinkle(c, "tw", cx + 150, cy - 150, 42, 82, 26)


@emoji("26-tribal-heart", "❤️‍🔥", "горю, страсть, огонь, люблю, трайбл", "on fire, passion, burning love, tribal, heart",
       "трайбл-сердце загорается: рога-завитки лижут вверх как языки пламени вразнобой, из макушки летят угли",
       op=120, series="v1")
def tribal_heart(c):
    g = geo.svg(os.path.join(V1, "26-tribal-heart.svg")).buffer(3)
    cx = 256
    # heavy double beat (lub-dub, M1) from the tip, thorns bend a touch behind the beat, long rest
    s = Track([100, 100], 0).hold(20).to(25, [108, 108], "snap").to(35, [100, 100], "io").to(40, [105, 105], "snap")
    s.to(47, [99, 99], "io").to(55, [100.5, 100.5], "io").to(64, [100, 100], "io").hold(120)
    root = c.null("root", p=(cx, 440), a=(cx, 440), s=s)
    zones = [("L", geo.poly([(0, 0), (256, 0), (256, 512), (0, 512)]), (176, 250), -1),
             ("R", geo.poly([(256, 0), (512, 0), (512, 512), (256, 512)]), (336, 250), 1)]
    core = g.intersection(geo.disc(cx, 250, 150))
    c.layer("core", [geo.shape(core, nm="core")], parent=root, p=(cx, 250), a=(cx, 250))
    for nm, z, anchor, d in zones:
        side = g.intersection(z).difference(geo.disc(cx, 250, 140))
        rr = Track(0, 0).hold(24).to(30, d * 2.5, "o").to(40, -d * 1, "io").to(44, d * 1.5, "o").to(56, 0, "io").loop(120)
        c.layer(f"thorns{nm}", [geo.shape(side, nm=nm)], parent=root, p=anchor, a=anchor, r=rr)


@emoji("27-tribal-eye", "👁️", "вижу, слежу, палю, глаз, око", "i see you, watching, eye, all seeing, stare",
       "трайбл-око закрыто — распахивается, лучи выстреливают по кругу с задержкой, X-зрачок проворачивается, моргает",
       op=150, series="v1")
def tribal_eye(c):
    cx, cy = 256, 256
    upper = geo.brush(geo.quad((cx - 190, cy), (cx, cy - 170), (cx + 190, cy), 24), 40, (0.35, 0.35), False)
    lower = geo.brush(geo.quad((cx - 190, cy), (cx, cy + 170), (cx + 190, cy), 24), 40, (0.35, 0.35), False)
    pupil = geo.disc(cx, cy, 62).difference(geo.text("X", __import__("specs.drop", fromlist=["x"]).brand_font(), cx, cy, 42, bold=6, width=70))
    open_ = Track([100, 100], 0).hold(40).to(44, [104, 8], "i").to(52, [100, 100], "o").hold(96).to(116, [100, 10], "is")
    open_.hold(124).to(132, [100, 112], "snap").to(140, [100, 96], "io").to(148, [100, 100], "io").loop(150)
    lay(c, "upper", upper, (cx, cy), s=open_)
    lay(c, "lower", lower, (cx, cy), s=open_)
    ps = Track([100, 100], 0).hold(40).to(44, [100, 10], "i").to(52, [100, 100], "o").hold(96).to(112, [0, 0], "is")
    ps.hold(126).to(136, [112, 112], "snap").to(144, [100, 100], "io").loop(150)
    pr = Track(0, 0).hold(60).to(78, 90, (0.4, 0.0, 0.1, 1.0)).to(84, 84, "io").to(90, 90, "io").hold(150)
    pr.k[-1][2] = "hold"
    pr.k.append([149.99, 0, None])
    lay(c, "pupil", pupil, (cx, cy), s=ps, r=pr)
    for k in range(8):
        a = math.radians(-90 + k * 45)
        r0, r1 = (176, 222) if k % 2 == 0 else (150, 194)
        if k in (2, 6):
            r0, r1 = 204, 226
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a) * 0.9)
        p1 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a) * 0.9)
        t0 = 128 + (k % 4) * 2
        e = Track(100, 0).hold(100).to(114, 0, "i").hold(t0).to(t0 + 8, 100, "o").loop(150)
        c.layer(f"ray{k}", [geo.stroked([p0, p1], 30, e=e)], p=(0, 0), a=(0, 0))


@emoji("29-drip-xtc", "💦", "капает, течёт, мокро, xtc, сочно", "dripping, wet, drip, xtc, juicy",
       "тяжёлый лаковый XTC: по буквам проходит блик, снизу медленно растут латексные подтёки, средний тянется и срывается каплей, все медленно втягиваются",
       op=150, series="v1")
def drip_xtc(c):
    from specs.drop import brand_word
    from specs.v1a import drip_shape
    from specs.reactions import seq
    OP = 150
    cy = 200
    word = brand_word("XTC", 256, cy, 150, 470)
    x0, y0, x1, y1 = word.bounds
    # the wordmark is heavy lacquer: one glare sweep, no wobble
    wl = lay(c, "word", word, (256, y1))
    M.glare_sweep(c, wl, 256, cy, 18, 30, travel=360, length=640, w1=30, w2=12, gap=14)
    # latex drips: grow slowly from the bottom edge (is), neck, one snaps off into a drop, all retract slowly
    drips = [(x0 + (x1 - x0) * 0.16, 34, 30, 120), (x0 + (x1 - x0) * 0.5, 44, 44, 180), (x0 + (x1 - x0) * 0.84, 30, 58, 100)]
    for k, (x, w, t0, L) in enumerate(drips):
        g = drip_shape(x, y1 - 24, y1 + L, w)
        ts = seq([100, 4], [(t0, None, None), (t0 + 46, [100, 100], "is"), (t0 + 54, [90, 108], "io"), (t0 + 60, [104, 96], "io"),
                            (t0 + 66, [100, 100], "io"), (128, None, None), (148, [100, 4], "io3")], op=OP, loop_ease="lin")
        lay(c, f"drip{k}", g, (x, y1 - 24), s=ts)
        if k == 1:
            M.particle(c, "drop", geo.drop(x, y1 + L, w * 0.42, w), t0 + 56, 30, (x, y1 + L), (x, 500 - w), None,
                       anchor=(x, y1 + L), pop=0.15, fade=0.2, fall="i5", s_end=60)


@emoji("30-club-banner", "🪩", "клуб, туса, вечеринка, club, рейв", "club, party, rave, night out, banner",
       "лента CLUB разворачивается из центра, хвосты выхлёстывают, табличка качается на бит, в конце сворачивается обратно",
       op=150, series="v1")
def club_banner(c):
    from specs.drop import brand_word
    cx, cy = 256, 256
    body = geo.rrect(cx - 170, cy - 70, cx + 170, cy + 70, 16).difference(brand_word("CLUB", cx, cy, 70, 270, bold=9))
    tailL = geo.poly([(cx - 150, cy - 30), (cx - 236, cy - 20), (cx - 204, cy + 26), (cx - 236, cy + 72), (cx - 150, cy + 62)])
    tailR = geo.mirror(tailL, cx)
    y = Track(cy, 0).hold(24)
    r = Track(0, 0).hold(24)
    for t in (24, 54, 84):
        y.to(t + 5, cy - 18, "decel").to(t + 14, cy, "slam").to(t + 20, cy - 3, "o").to(t + 26, cy, "i")
        r.to(t + 8, 3 if t % 60 == 24 else -3, "io").to(t + 22, 0, "io")
    root = c.null("root", p=Split(cx, y.loop(150)), a=(cx, cy), r=r.loop(150))
    # unfurl: the plate opens from a vertical sliver (scaleX), rolls up at the end
    us = Track([8, 100], 0).hold(2).to(18, [104, 100], "o").to(24, [100, 100], "io").hold(126).to(146, [8, 100], "i").loop(150)
    lay(c, "body", body, (cx, cy), parent=root, s=us)
    for k, (g, d) in enumerate(((tailL, -1), (tailR, 1))):
        ax = cx + d * 150
        px = Track(cx, 0).hold(2).to(18, ax + d * 6, "o").to(24, ax, "io").hold(126).to(146, cx, "i").loop(150)
        tr = Track(d * 30, 0).hold(10).to(24, -d * 10, "snap").to(32, 0, "io")
        for t in (24, 54, 84):
            tr.hold(t + 4 + k * 2).to(t + 10 + k * 2, d * 14, "snap").to(t + 20 + k * 2, -d * 6, "io").to(t + 28 + k * 2, 0, "io")
        tr.hold(126).to(146, d * 30, "i")
        lay(c, f"tail{k}", g, (ax, cy + 20), parent=root, p=Split(px, cy + 20), r=tr.loop(150))


@emoji("31-cyber-butterfly", "🦋", "бабочка, лёгкость, влюблена, порхаю, y2k", "butterfly, flutter, crush, light, y2k",
       "кибер-бабочка с люверсами на крыльях складывает их как страницы (fake-3D), два взмаха с подъёмом, парит, крылья обгоняют друг друга на 3 кадра",
       op=120, series="v1")
def butterfly(c):
    cx, cy = 256, 262
    upper = geo.poly([(cx - 18, cy - 20), (cx - 150, cy - 196), (cx - 226, cy - 170), (cx - 214, cy - 60), (cx - 20, cy + 4)]).buffer(24).buffer(-10)
    upper = upper.difference(geo.ring(cx - 146, cy - 106, 38, 18)).difference(geo.disc(cx - 104, cy - 44, 14))
    lower = geo.poly([(cx - 18, cy + 10), (cx - 190, cy + 40), (cx - 196, cy + 150), (cx - 110, cy + 190), (cx - 20, cy + 60)]).buffer(22).buffer(-10)
    lower = lower.difference(geo.ring(cx - 116, cy + 96, 30, 14))
    body = geo.U(geo.rrect(cx - 16, cy - 110, cx + 16, cy + 150, 16), geo.disc(cx, cy - 124, 24))
    antL = geo.brush([(cx - 6, cy - 140), (cx - 40, cy - 200), (cx - 70, cy - 216)], 18, (1, 1), True, 6)
    y = Track(cy, 0)
    for t in (0, 30):
        y.hold(t).to(t + 8, cy + 10, "io").to(t + 20, cy - 26, "decel").to(t + 30, cy - 20, "io")
    y.hold(60).to(100, cy + 4, "io").to(120, cy, "io")
    root = c.null("root", p=Split(cx, y.loop(120)), a=(cx, cy))
    lay(c, "body", geo.U(body, antL, geo.mirror(antL, cx)), (cx, cy), parent=root)
    for side, d in enumerate((1, -1)):
        for k, g in enumerate((upper, lower)):
            g2 = g if d == 1 else geo.mirror(g, cx)
            lag = k * 3
            s = Track([100, 100], 0)
            for t in (0, 30):
                s.hold(t + lag).to(t + 8 + lag, [22, 100], "io").to(t + 20 + lag, [100, 100], "o")
            s.hold(70 + lag).to(84 + lag, [70, 100], "io").to(100 + lag, [100, 100], "io").loop(120)
            lay(c, f"w{side}{k}", g2, (cx, cy), parent=root, s=s)


@emoji("32-swallow", "🐦", "ласточка, лечу, свобода, тату, птичка", "swallow, flying, freedom, tattoo, bird",
       "тату-ласточка делает мёртвую петлю: разгон взмахами, круг с креном по касательной, выход в парение, хвост-ножницы щёлкают",
       op=150, series="v1")
def swallow(c):
    cx, cy = 256, 262
    body = geo.U(geo.ellipse(cx + 20, cy, 112, 50), geo.disc(cx + 118, cy - 26, 44))
    body = geo.U(body, geo.poly([(cx + 150, cy - 44), (cx + 212, cy - 30), (cx + 152, cy - 12)]))
    body = geo.rot(body, -18, (cx, cy)).difference(geo.disc(cx + 126, cy - 64, 10))
    tailU = geo.poly([(cx - 70, cy + 2), (cx - 214, cy - 40), (cx - 196, cy - 18), (cx - 70, cy + 30)]).buffer(10)
    tailD = geo.poly([(cx - 70, cy + 14), (cx - 206, cy + 80), (cx - 188, cy + 96), (cx - 60, cy + 40)]).buffer(10)
    wingU = geo.poly([(cx - 10, cy - 20), (cx - 90, cy - 190), (cx - 60, cy - 206), (cx + 50, cy - 40)]).buffer(18)
    wingD = geo.poly([(cx + 10, cy + 30), (cx - 40, cy + 170), (cx - 10, cy + 186), (cx + 60, cy + 40)]).buffer(16)
    # loop-de-loop: the whole bird travels a circle (radius 40) while rotating a full turn (tangent heading)
    import math as m
    t0, t1 = 40, 100
    th = M.spin_angle([(t0, t1, 0, 360, "io3")])
    ks = [0, t0] + M.crossings(th, [(t0, t1, 0, 360, "io3")], 90, 0) + [t1, 150]
    ks = sorted(set(round(k, 2) for k in ks))
    R = 30
    px = M.fit(lambda t: cx + R * m.sin(m.radians(th(t))), ks)
    py = M.fit(lambda t: cy - R + R * m.cos(m.radians(th(t))) + 0.0, ks)
    rr = M.fit(lambda t: -th(t), ks)
    rr.k[-1][2] = None
    rr.k[-2][2] = "hold" if False else rr.k[-2][2]
    # the rotation ends at -360 == 0: close the loop with a hold jump at the very end
    rr.k[-1][1] = -360
    rr.k[-1][2] = "hold"
    rr.k.append([149.99, 0, None])
    root = c.null("root", p=Split(px, py), a=(cx, cy), r=rr,
                  s=Track([84, 84], 0).hold(150))
    wu = Track(0, 0)
    wd = Track(0, 0)
    for t in (4, 20, 104, 120):
        wu.hold(t).to(t + 7, 58, "io").to(t + 14, -8, "snap").to(t + 16, 0, "io")
        wd.hold(t + 2).to(t + 9, -40, "io").to(t + 16, 8, "snap").to(t + 18, 0, "io")
    lay(c, "wingD", wingD, (cx + 20, cy + 30), parent=root, r=wd.loop(150))
    tu = Track(0, 0)
    td = Track(0, 0)
    for t in (36, 100):
        tu.hold(t).to(t + 5, -10, "snap").to(t + 12, 0, "io")
        td.hold(t).to(t + 5, 10, "snap").to(t + 12, 0, "io")
    lay(c, "tailU", tailU, (cx - 70, cy + 10), parent=root, r=tu.loop(150))
    lay(c, "tailD", tailD, (cx - 70, cy + 20), parent=root, r=td.loop(150))
    lay(c, "body", body, (cx, cy), parent=root)
    lay(c, "wingU", wingU, (cx + 10, cy - 20), parent=root, r=wu.loop(150))


@emoji("41-patch-x", "🩹", "пластырь, заживёт, береги себя, ранен, ой", "bandage, heal, get well, hurt, patch",
       "пластырь-X шлёпается и натягивается, переворачивается через длинную ось как блин (360 с торцом), прилипает — ✦",
       op=150, series="v1")
def patch(c):
    cx, cy = 256, 262
    band = geo.rrect(cx - 220, cy - 84, cx + 220, cy + 84, 84)
    pad = geo.rrect(cx - 78, cy - 56, cx + 78, cy + 56, 16)
    front = band.difference(pad.difference(pad.buffer(-20))).difference(brand_word_x(cx, cy))
    for sx in (-1, 1):
        for dx, dy in ((0, -30), (0, 30), (46, 0)):
            front = front.difference(geo.disc(cx + sx * (140 + dx), cy + dy, 13))
    back = band.difference(geo.rrect(cx - 200, cy - 6, cx + 200, cy + 6, 6))
    # slaps on (squash), then flips over its long axis like a pancake (spin3d on a null turned 90°)
    s = Track([100, 100], 0).hold(10).to(20, [96, 104], "io").to(26, [110, 90], "slam").to(27, [110, 90], "lin").to(34, [97, 103], "io").to(42, [100, 100], "io")
    s.hold(118).to(120, [104, 96], "slam").to(128, [99, 101], "io").to(134, [100, 100], "io").loop(150)
    body = c.null("body", p=(cx, cy), a=(cx, cy), s=s, r=-14)
    turn = c.null("turn", parent=body, p=(cx, cy), a=(cx, cy), r=90)
    fr, bk = geo.rot(front, 90, (cx, cy)), geo.rot(back, 90, (cx, cy))
    segs = [(40, 52, 0, -24, "io"), (52, 112, -24, 380, (0.3, 0.0, 0.14, 1.0)), (112, 124, 380, 360, "io")]
    M.spin3d(c, "patch", fr, bk, cx, cy, segs, thick=30, lip=22, parent=turn)
    M.twinkle(c, "tw", cx + 170, cy - 110, 40, 124, 24)


def brand_word_x(cx, cy):
    from specs.drop import brand_letter
    return brand_letter("X", cx, cy, 46, 90, 11)


