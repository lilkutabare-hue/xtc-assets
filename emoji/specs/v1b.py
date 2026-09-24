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


@emoji("25-mask-glyphs", "🎭", "маска, хоррор, маньяк, пятница, джейсон", "mask, horror, slasher, creepy, jason",
       "хоккейная маска медленно поворачивается к тебе (параллакс прорезей), в прорезях вспыхивают глаза и косятся, по кромке — блик ножа ✦",
       op=180, series="v1")
def mask(c):
    g = geo.svg(os.path.join(V1, "25-mask-glyphs.svg"))
    shell = geo.U(*[geo.Polygon(p.exterior) for p in geo._polys(g)])
    holes = shell.difference(g)
    cx, cy = 256, 255
    # yaw: the shell narrows a little while the holes slide the other way (parallax = fake 3D); the
    # holes never leave the shell (shift 10px inside a 20px rim)
    sx = Track([95, 100], 0).hold(20).to(60, [100, 100], "io").hold(140).to(176, [95, 100], "io").loop(180)
    base = c.layer("mask", [geo.shape(shell, nm="shell")], p=(cx, cy), a=(cx, cy), s=sx)
    hx = Track([-10, 0], 0).hold(20).to(60, [0, 0], "io").hold(140).to(176, [-10, 0], "io").loop(180)
    geo.hole(base, holes, nm="holes", p=hx)
    # eyes light up inside the two eye slots: pop in, glance right, glance left, blink out
    eyes = sorted([e for e in geo._polys(holes) if e.area > 4000 and e.centroid.y > 150], key=lambda e: e.centroid.x)[:2]
    off = c.null("eyes", p=Split(Track(256, 0).hold(20).to(60, 266, "io").hold(140).to(176, 256, "io").loop(180), 256), a=(256, 256))
    for k, e in enumerate(eyes):
        ex, ey = e.centroid.x - 10, e.centroid.y
        es = Track([0, 0], 0).hold(64 + k * 3).to(72 + k * 3, [118, 118], "snap").to(78 + k * 3, [100, 100], "io")
        es.hold(128).to(132, [110, 10], "i").to(136, [0, 0], "lin").loop(180, "lin")
        ep = Track([ex, ey], 0).hold(86).to(94, [ex + 14, ey], "snap").hold(104).to(112, [ex - 12, ey + 2], "snap").hold(120).to(126, [ex, ey], "io").loop(180)
        c.layer(f"eye{k}", [geo.shape(geo.disc(ex, ey, 21), nm="eye")], parent=off, p=ep, a=(ex, ey), s=es)
    M.twinkle(c, "tw", 392, 96, 40, 104, 26)


@emoji("26-tribal-heart", "❤️‍🔥", "горю, страсть, огонь, люблю, трайбл", "on fire, passion, burning love, tribal, heart",
       "трайбл-сердце загорается: рога-завитки лижут вверх как языки пламени вразнобой, из макушки летят угли",
       op=120, series="v1")
def tribal_heart(c):
    g = geo.svg(os.path.join(V1, "26-tribal-heart.svg")).buffer(3)
    cx = 256
    # cut the curls (top corners) and thorns (sides) off the heart body, each flickers from its root
    zones = [("curlL", geo.poly([(20, 20), (230, 20), (230, 170), (20, 170)]), (190, 150)),
             ("curlR", geo.poly([(282, 20), (492, 20), (492, 170), (282, 170)]), (322, 150)),
             ("thornL", geo.poly([(20, 170), (120, 170), (120, 330), (20, 330)]), (120, 240)),
             ("thornR", geo.poly([(392, 170), (492, 170), (492, 330), (392, 330)]), (392, 240))]
    rest = g
    s = Track([100, 100], 0).hold(10).to(30, [104, 104], "is").to(36, [100, 100], "o").hold(100).to(112, [100, 100], "lin").loop(120)
    root = c.null("root", p=(cx, 420), a=(cx, 420), s=s)
    for k, (nm, z, anchor) in enumerate(zones):
        part = g.intersection(z)
        rest = rest.difference(z)
        ph = k * 5
        sc = Track([100, 100], 0)
        rr = Track(0, 0)
        d = -1 if nm.endswith("L") else 1
        for j, (t, a, v) in enumerate(((12, 128, 9), (26, 88, -6), (38, 122, 8), (52, 92, -5), (66, 118, 6), (80, 90, -4), (96, 108, 3))):
            sc.to(t + ph, [100, a], "io")
            rr.to(t + ph, d * v, "io")
        sc.loop(120)
        rr.loop(120)
        lay(c, nm, part, anchor, parent=root, s=sc, r=rr)
    lay(c, "body", rest, (cx, 300), parent=root)
    # embers: small drops rising and fading (M17)
    import random
    rnd = random.Random(5)
    for k in range(7):
        x0 = rnd.choice([150, 190, 320, 360])
        t0 = k * 16
        M.particle(c, f"ember{k}", geo.spark(x0, 110, 20, 0.34), t0, 36, (x0, 120), (x0 + rnd.uniform(-30, 30), 30), None,
                   pop=0.2, fade=0.4, fall="decel", rot=(0, rnd.choice([-90, 90])), anchor=(x0, 110))


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


@emoji("28-tribal-cross", "✝️", "крест, вера, святое, gothic, аминь", "cross, faith, holy, gothic, amen",
       "готический крест тяжело покачивается, собирается в центр и выстреливает лучами по очереди, вспыхивает ✦",
       op=150, series="v1")
def tribal_cross(c):
    cx, cy = 256, 200
    def arm(ang, L, W):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        pts = [(cx + nx * W / 2, cy + ny * W / 2), (cx + ux * (L - W * 0.9) + nx * W / 2, cy + uy * (L - W * 0.9) + ny * W / 2),
               (cx + ux * (L - W * 0.55) + nx * W * 0.78, cy + uy * (L - W * 0.55) + ny * W * 0.78),
               (cx + ux * L, cy + uy * L),
               (cx + ux * (L - W * 0.55) - nx * W * 0.78, cy + uy * (L - W * 0.55) - ny * W * 0.78),
               (cx + ux * (L - W * 0.9) - nx * W / 2, cy + uy * (L - W * 0.9) - ny * W / 2), (cx - nx * W / 2, cy - ny * W / 2)]
        return geo.poly(pts)
    arms = [(-90, 162, 76), (0, 176, 70), (90, 276, 80), (180, 176, 70)]
    core = geo.disc(cx, cy, 58).difference(geo.disc(cx, cy, 24))
    r = Track(0, 0).to(20, 3, "io").to(44, -2.5, "io").to(62, 0, "io").hold(128).to(140, 2, "io").to(150, 0, "io")
    root = c.null("root", p=(cx, 20), a=(cx, 20), r=r)
    for k, (ang, L, W) in enumerate(arms):
        t0 = 96 + k * 5
        s = Track([100, 100], 0).hold(78).to(92, [40, 40], "is").hold(t0).to(t0 + 8, [106, 106], "snap").to(t0 + 16, [97, 97], "io").to(t0 + 24, [100, 100], "io").loop(150)
        c.layer(f"arm{k}", [geo.shape(arm(ang, L, W), nm="arm")], parent=root, p=(cx, cy), a=(cx, cy), s=s)
    cs = Track([100, 100], 0).hold(78).to(92, [120, 120], "is").to(98, [90, 90], "snap").to(106, [100, 100], "io").loop(150)
    lay(c, "core", core, (cx, cy), parent=root, s=cs)
    M.twinkle(c, "tw", cx + 110, cy - 100, 46, 112, 28)
    M.twinkle(c, "tw2", cx - 104, cy + 126, 30, 122, 22)


@emoji("29-drip-xtc", "💦", "капает, течёт, мокро, xtc, сочно", "dripping, wet, drip, xtc, juicy",
       "XTC трясётся желе волной по буквам, с нижних кромок набухают подтёки, тянутся и срываются каплями",
       op=150, series="v1")
def drip_xtc(c):
    from specs.drop import brand_letter
    cy = 196
    letters = [("X", 110), ("T", 256), ("C", 402)]
    for k, (ch, x) in enumerate(letters):
        g = brand_letter(ch, x, cy, 118, 150, 16)
        t0 = 10 + k * 8                                  # M16 jelly, letters offset 7-8f
        s = Track([100, 100], 0).hold(t0).to(t0 + 10, [95, 105], "io").to(t0 + 20, [105, 95], "io").to(t0 + 30, [97, 103], "io").to(t0 + 40, [100, 100], "io").loop(150)
        lay(c, f"L{k}", g, (x, cy + 59), s=s)
    # drips: hang from letter bottoms, stretch down, detach and fall (stagger 2-4f per M16)
    drips = [(78, 250, 22), (140, 252, 18), (256, 252, 24), (370, 252, 20), (440, 250, 18)]
    for k, (x, y0, r) in enumerate(drips):
        t0 = 40 + k * 7
        # the hanging tongue: grows from the letter bottom
        tongue = geo.U(geo.rect(x - r * 0.7, y0 - 10, x + r * 0.7, y0 + 40), geo.disc(x, y0 + 40, r))
        ts = Track([100, 0], 0).hold(t0 - 20).to(t0, [100, 100], "is").to(t0 + 4, [90, 120], "io").to(t0 + 8, [100, 20], "snap").to(t0 + 30, [100, 0], "io").loop(150)
        lay(c, f"tongue{k}", tongue, (x, y0 - 10), s=ts)
        M.particle(c, f"drop{k}", K.tear(x, y0 + 40, r), t0 + 6, 30, (x, y0 + 40), (x, 470), None, anchor=(x, y0 + 40),
                   pop=0.1, fade=0.15, fall="i", s_end=60)


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


@emoji("43-scorpion-sigil", "🦂", "скорпион, ужалю, опасно, тату, яд", "scorpion, sting, danger, tattoo, venom",
       "скорпион взводит хвост назад (антиципация) и бьёт жалом вперёд с ударом, клешни щёлкают дважды, на жале ✦",
       op=150, series="v1")
def scorpion(c):
    parts = geo.tgs_geometry(os.path.join(V1, "..", "tg-anim", "43-scorpion-sigil.tgs"))
    fat = {k: v.buffer(13).buffer(-5) for k, v in parts.items()}
    root = c.null("root", p=(256, 322), a=(256, 300),
                  s=Track([88, 88], 0).hold(60).to(64, [92, 84], "slam").to(72, [87, 89], "io").to(78, [88, 88], "io").loop(150))
    lay(c, "body", fat["body"], (256, 360), parent=root)
    tb = (384, 350)
    tr = Track(0, 0).hold(24).to(52, 14, "io").to(60, -30, "strike").to(64, -24, "io").to(72, -28, "io").hold(96).to(120, 0, "io").loop(150)
    tail = lay(c, "tail", fat["tail"], tb, parent=root, r=tr)
    cr = Track(0, 0)
    for t in (84, 96):
        cr.hold(t).to(t + 4, -16, "snap").to(t + 9, 0, "slam")
    cr.loop(150)
    lay(c, "claw_up", fat["claw_up"], (150, 280), parent=root, r=cr)
    lay(c, "claw_low", fat["claw_low"], (120, 330), parent=root,
        r=Track(0, 0).hold(86).to(90, 12, "snap").to(95, 0, "slam").hold(98).to(102, 12, "snap").to(107, 0, "slam").loop(150))
    M.twinkle(c, "tw", 336, 96, 36, 62, 24, parent=tail)
    from specs.drop import speed_lines
    for k, (p0, p1) in enumerate((((236, 110), (200, 92)), ((236, 150), (192, 146)), ((250, 72), (224, 48)))):
        e = Track(0, 0).hold(60).to(66, 100, "o").hold(150)
        s0 = Track(0, 0).hold(62).to(69, 100, "i").hold(150)
        c.layer(f"hit{k}", [geo.stroked([p0, p1], 20, e=e, s=s0)], p=(0, 0), a=(0, 0), ip=60, op=70)
