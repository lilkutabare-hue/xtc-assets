"""v3.2: crosses (client: «добавил бы разных крестов») in the logo language."""
import math

from xtc import geo, logo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import brand_x
from specs.reactions import seq, breathe, rig, part
from specs.v3 import hit_lines


def latin_cross(cx=256, cy=256, w=400, h=440, bar=118, arm_y=-70, r=10):
    v = geo.rrect(cx - bar / 2, cy - h / 2, cx + bar / 2, cy + h / 2, r)
    hz = geo.rrect(cx - w / 2, cy + arm_y - bar / 2, cx + w / 2, cy + arm_y + bar / 2, r)
    return geo.U(v, hz)


def fleury_cross(cx=256, cy=256, L=176, w=54, arms=(0.72, 0.72, 0.72, 1.0)):
    """gothic latin cross: straight arms (right, down, left, up as fractions of L) that flare into a
    clean trapezoid tip."""
    parts = []
    for ang, f in zip((0, 90, 180, 270), arms):
        a = math.radians(ang)
        L_ = L * f
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        w1 = w * 1.7
        pts = [(cx + px * w / 2, cy + py * w / 2), (cx + ux * (L_ - 40) + px * w / 2, cy + uy * (L_ - 40) + py * w / 2),
               (cx + ux * L_ + px * w1 / 2, cy + uy * L_ + py * w1 / 2), (cx + ux * (L_ - 10), cy + uy * (L_ - 10)),
               (cx + ux * L_ - px * w1 / 2, cy + uy * L_ - py * w1 / 2), (cx + ux * (L_ - 40) - px * w / 2, cy + uy * (L_ - 40) - py * w / 2),
               (cx - px * w / 2, cy - py * w / 2)]
        parts.append(geo.poly(pts))
    return geo.U(*parts).buffer(4, join_style=2).buffer(-4, join_style=2)


def pattee_cross(cx=256, cy=256, L=214, w0=44, w1=150):
    """iron cross: four arms flaring from w0 at the centre to w1 at the tips, tips concave."""
    parts = []
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        pts = [(cx + px * w0 / 2, cy + py * w0 / 2), (cx + ux * L + px * w1 / 2, cy + uy * L + py * w1 / 2),
               (cx + ux * (L - 26), cy + uy * (L - 26)),
               (cx + ux * L - px * w1 / 2, cy + uy * L - py * w1 / 2), (cx - px * w0 / 2, cy - py * w0 / 2)]
        parts.append(geo.poly(pts))
    return geo.U(*parts).buffer(6, join_style=2).buffer(-6, join_style=2)


# ================================================================ 144 ☦️ gothic pendant


# ================================================================ 145 ➕ iron cross


@emoji("145-iron-cross", "➕", "железный крест, штамп, удар, тяжёлый, xtc", "iron cross, stamp, heavy, hit, xtc",
       "железный крест падает штампом с высоты: контакт 1f 108/92, ударное кольцо и линии, всё дрожит; потом тяжёлый переворот — на обороте выгравирован логотип-X",
       op=150, series="cross")
def iron(c):
    OP = 150
    cx, cy = 256, 256
    cross = pattee_cross(cx, cy, 196, 44, 140)
    back = cross.difference(brand_x(cx, cy, 190, 96))
    s = seq([116, 116], [(10, None, None), (22, [100, 100], "slam"), (23, [108, 92], "lin"), (24, [108, 92], "lin"), (32, [96, 104], "o"),
                         (40, [102, 98], "io"), (48, [100, 100], "io"), (126, None, None), (140, [116, 116], "i")], op=OP, loop_ease="lin")
    o = Track(0, 0)
    o.k[-1][2] = "hold"
    o.k.append([10, 100, None])
    o.hold(126)
    o.k[-1][2] = "hold"
    o.k.append([140, 0, None])
    o.loop(OP, "lin")
    px = seq(float(cx), [(23, None, None)])
    M.shake(px, 23, 37, 6, float(cx), step=2, decay=0.75)
    px.loop(OP)
    body = rig(c, "body", (cx, cy), p=Split(px, cy), s=s, o=o)
    segs = [(66, 118, 0, 360, (0.35, 0.0, 0.14, 1.0))]
    root, th, fr, bk = M.spin3d(c, "cross", cross, back, cx, cy, segs, thick=36, lip=26, parent=body)
    from specs.faces import lot_ring
    rs = Track([100, 100], 0).hold(22).to(36, [118, 118], "ring").hold(OP)
    rw = Track(24, 0).hold(22).to(36, 4, "ring").to(40, 0, "i").hold(OP)
    c.layer("ring", [lot_ring(cx, cy, 176, rw)], p=(cx, cy), a=(cx, cy), s=rs, ip=22, op=41)
    hit_lines(c, "hit", [((60, 60), (30, 30)), ((452, 60), (482, 30)), ((60, 452), (30, 482)), ((452, 452), (482, 482))], 23, w=22)
    M.twinkle(c, "tw", cx + 150, cy - 150, 40, 118, 22, parent=root)


# ================================================================ 146 🛐 the logo cut into a cross plate


@emoji("146-cross-xtc", "🛐", "крест xtc, лого, плашка, гравировка, дроп", "xtc cross, logo, plate, engraved, drop",
       "латинский крест-плашка с логотипом-крестом, вырезанным насквозь: висит, делает тяжёлый 360 с торцом — на обороте прорези читаются зеркально, как настоящая гравировка, ✦ на выходе",
       op=150, series="cross")
def cross_plate(c):
    OP = 150
    cx, cy = 256, 262
    plate = latin_cross(cx, cy, 440, 464, 150, -70, 14)
    L = logo.cross(cx, cy - 70, lh=52, width=376)
    holes = geo.U(*[g for g, _ in L.values()])
    front = plate.difference(holes)
    s = seq([100, 100], [(8, None, None), (18, [96, 104], "io"), (26, [100, 100], "o"), (96, None, None), (100, [103, 98], "o"),
                         (108, [99, 101], "io"), (116, [100, 100], "io")])
    breathe(s, 120, 150, [100, 100], 0.6, 30)
    s.loop(OP)
    body = rig(c, "body", (cx, cy + 226), s=s)
    segs = [(18, 96, 0, 360, (0.35, 0.0, 0.14, 1.0))]
    root, th, fr, bk = M.spin3d(c, "plate", front, front, cx, cy, segs, thick=34, lip=22, parent=body, band_h=440)
    M.glare_sweep(c, fr, cx, cy, 100, 28, travel=360, parent=root, length=640, w1=30, w2=12, gap=14,
                  sparks=[(cx + 150, cy - 130, 38, 104, 22)])


# ================================================================ 147 🐦‍⬛ raven


def raven_parts(cx=256, cy=300):
    body = geo.rot(geo.ellipse(cx, cy, 118, 50, 24), -8, (cx, cy))
    head = geo.U(geo.disc(cx + 112, cy - 48, 36, 20), geo.poly([(cx + 136, cy - 66), (cx + 212, cy - 36), (cx + 138, cy - 26)]))
    neck = geo.poly([(cx + 50, cy - 46), (cx + 112, cy - 84), (cx + 136, cy - 30), (cx + 70, cy + 12)])
    tail = geo.poly([(cx - 90, cy - 16), (cx - 214, cy + 10), (cx - 210, cy + 34), (cx - 182, cy + 30), (cx - 192, cy + 52), (cx - 154, cy + 42), (cx - 90, cy + 28)])
    body = geo.U(body, head, neck, tail).buffer(4).buffer(-4)
    body = body.difference(geo.disc(cx + 120, cy - 54, 9))                       # eye
    # wing built pointing LEFT from the shoulder; the layer rotation lifts / drops it
    sh = (cx + 24, cy - 24)
    main = geo.brush([sh, (sh[0] - 96, sh[1] - 8), (sh[0] - 192, sh[1] - 24)], 84, taper=(1.05, 0.5), smooth=False)
    fingers = []
    for k, ang in enumerate((150, 165, 180, 196, 212)):
        a = math.radians(ang)
        r0 = (sh[0] - 160, sh[1] - 22)
        fingers.append(geo.brush([r0, (r0[0] + math.cos(a) * 84, r0[1] + math.sin(a) * 84)], 26, taper=(1.0, 0.45), smooth=False))
    trail = [geo.brush([(sh[0] - 60 - 40 * k, sh[1] + 28 - 4 * k), (sh[0] - 78 - 40 * k, sh[1] + 62 - 4 * k)], 24, taper=(1.0, 0.5), smooth=False) for k in range(3)]
    wing = geo.U(main, *fingers, *trail).buffer(3).buffer(-3)
    return body, wing, sh


@emoji("147-raven", "🐦‍⬛", "ворон, птица, ночь, готика, мрак, xtc", "raven, crow, bird, night, gothic, dark",
       "ворон: четыре тяжёлых взмаха (вниз резко, вверх с торможением), тело качает в противофазе, дальнее крыло отстаёт на 3f, хвост дожимает; потом планирует, ✦ на клюве",
       op=150, series="v1")
def raven(c):
    OP = 150
    cx, cy = 272, 318
    body, wing, sh = raven_parts(cx, cy)
    # body bob: sinks on every downstroke (lag 3f), tilts nose-up when it glides
    by = Track(float(cy), 0)
    br = Track(0, 0)
    for k in range(4):
        t = 8 + k * 24
        by.hold(t + 3).to(t + 11, cy - 14.0, "decel").to(t + 21, cy + 6.0, "io")
        br.hold(t + 3).to(t + 11, 4, "io").to(t + 21, -3, "io")
    by.to(112, cy - 8.0, "io").to(136, float(cy), "io").loop(OP)
    br.to(112, -6, "io").to(140, 0, "io").loop(OP)
    root = rig(c, "bird", (cx, cy), p=Split(cx, by), r=br)
    # wings: near (above the body) and far (behind, smaller, 3f late); downstroke 9f slam, upstroke 15f decel
    def flap(lag, up, down):
        r = Track(up, 0).hold(8 + lag)
        for k in range(4):
            t = 8 + k * 24 + lag
            r.to(t + 9, down, "slam").to(t + 24, up, "decel")
        r.to(116 + lag, up + 14, "io").to(150, up, "io") if 116 + lag < 150 else r.loop(OP)
        return r
    far = geo.scale(wing, 0.86, 0.86, origin=sh)
    part(c, "wingF", far, root, sh, r=flap(3, 74, -26))
    part(c, "body", body, root, (cx, cy))
    part(c, "wingN", wing, root, sh, r=flap(0, 52, -42))
    M.twinkle(c, "tw", cx + 200, cy - 70, 30, 118, 20, parent=root)


# ================================================================ 148 💔 broken heart


@emoji("148-broken-heart", "💔", "разбитое сердце, больно, расстался, эх, xtc", "broken heart, heartbreak, hurt, breakup, xtc",
       "лаковое сердце с логотипным X: два удара, дрожь, трещина щёлкает раз, два — половинки отваливаются на шарнире-кончике и качаются, X рвётся пополам; срастаются обратно",
       op=150, series="react")
def broken_x(c):
    from shapely.geometry import LineString
    from shapely.ops import split as _split
    OP = 150
    hx, hy, hw = 256, 262, 350
    g = geo.heart(hx, hy, hw)
    bx0, by0, bx1, by1 = g.bounds
    tip = (hx, by1 - 2)
    d = (by1 - by0) / 6
    zig = [(hx, by0 - 40), (hx - 4, by0 + d * 0.9), (hx + 30, by0 + d * 1.9), (hx - 30, by0 + d * 2.9), (hx + 22, by0 + d * 3.8), (hx - 8, by1 - 44), (hx, by1 + 40)]
    X = brand_x(hx, hy + 6, 220, 100)
    g = g.difference(X)
    parts = sorted(_split(g, LineString(zig)).geoms, key=lambda p: p.centroid.x)
    left = geo.U(*[p for p in parts if p.centroid.x < hx])
    right = geo.U(*[p for p in parts if p.centroid.x >= hx])
    ws = seq([100, 100], [(8, None, None), (12, [106, 96], "snap"), (20, [100, 100], "io"), (24, None, None), (28, [105, 97], "snap"), (36, [100, 100], "io"),
                          (41, None, None), (42, [103, 98], "o"), (46, [100, 100], "io"), (48, None, None), (49, [104, 97], "o"),
                          (53, [100, 100], "io"), (140, None, None), (144, [104, 96], "o"), (150, [100, 100], "io")])
    wx = seq(float(hx), [(30, None, None)])
    M.shake(wx, 30, 41, 4, float(hx), step=2, decay=1.0)
    wx.loop(OP)
    whole = rig(c, "whole", (hx, hy), p=Split(wx, hy), s=ws)
    io = Track(100, 0)
    for t, v in ((41, 0), (141, 100)):
        io.k[-1][2] = "hold"
        io.k.append([t, v, None])
    io.loop(OP, "lin")
    intact = part(c, "intact", g, whole, tip, o=io)
    M.glare_sweep(c, intact, hx, hy - 20, 6, 24, travel=300, parent=whole, sparks=[(hx + 90, hy - 130, 36, 140, 8)])
    fall = [(40, None, None), (42, 2.5, "snap"), (47, None, None), (49, 5.5, "snap"), (54, None, None),
            (62, 13, "i"), (70, 6.5, "io"), (78, 10, "io"), (86, 8, "io"), (94, 9, "io"), (102, 8.6, "io"),
            (122, None, None), (140, 0, "io3")]
    sag = [(54, None, None), (62, 12, "i"), (70, 5, "io"), (78, 9, "io"), (90, 8, "io"), (122, None, None), (140, 0, "io3")]
    from specs.reactions import _clip_loop
    for j, (nm, geom, sgn) in enumerate((("L", left, -1), ("R", right, 1))):
        amp = 0.85 if j == 0 else 0.75
        r = _clip_loop(seq(0, fall, j, f=lambda v: sgn * v * amp), OP)
        py = _clip_loop(seq(0, sag, j, f=lambda v: tip[1] + v), OP)
        part(c, f"half{nm}", geom, whole, tip, p=Split(tip[0], py), r=r)



# ================================================================ 149 opium face


def blade_eye(x, y, d=1, L=186, w=44):
    """sharp eyeliner wedge: thick at the inner-bottom, tapering to a thin point outward-up (d=-1 left)."""
    pts = [(x, y + 34), (x - d * 34, y - 26), (x - d * L, y - 60), (x - d * 60, y + 10)]
    return geo.poly(pts).buffer(3, join_style=2).buffer(-3, join_style=2)


@emoji("149-opium", "😑", "опиум, взгляд, серьёзно, мрак, xtc, свэг", "opium, stare, serious, dark, xtc, swag",
       "опиумная морда: два острых глаза-лезвия и черта-рот; почти неподвижна — медленный наклон к зрителю, глаза сужаются в щели и резко раскрываются, черта чуть дёргается",
       op=180, series="face")
def opium(c):
    OP = 180
    cx, ey, my = 256, 232, 318
    r = seq(0, [(30, None, None), (90, -3, "io"), (150, 0, "io")], op=OP)
    s = seq([100, 100], [(30, None, None), (90, [104, 104], "io"), (150, [100, 100], "io")], op=OP)
    face = rig(c, "face", (cx, my), r=r, s=s)
    for i, d in enumerate((-1, 1)):
        x = cx + d * 24
        es = seq([100, 100], [(60, None, None), (84, [100, 46], "is"), (96, None, None), (100, [104, 112], "snap"), (110, [100, 100], "io")], op=OP)
        part(c, f"eye{i}", blade_eye(x, ey, d), face, (x - d * 60, ey - 10), s=es)
    ms = seq([100, 100], [(98, None, None), (101, [118, 100], "snap"), (112, [100, 100], "io")], op=OP)
    part(c, "mouth", geo.brush([(cx - 36, my), (cx + 36, my)], 34, taper=(0.9, 0.9), smooth=False), face, (cx, my), s=ms)


# ================================================================ 150 ❌ one letter: X → T → C


@emoji("150-xtc-turn", "❌", "x, xtc, лого, буква, поворот", "x, xtc, logo, letter, turn",
       "логотипная буква на оси: тяжёлый полуоборот с торцом — на ребре подменяется на следующую: X → T → C → X, после каждого поворота покой",
       op=150, series="drop")
def xtc_turn(c):
    from xtc.lot import fit
    OP = 150
    cx, cy = 256, 256
    W, H = 400, 200
    letters = [logo.letter(ch, cx, cy, W, H) for ch in "XTC"]
    # angle: three half-turns with rests; scaleX = |cos|, the design swaps on the edge (M6 hold-swap)
    segs = [(10, 40, 0, 180), (58, 88, 180, 360), (106, 136, 360, 540)]
    ease = (0.4, 0.0, 0.16, 1.0)
    from xtc.motion import spin_angle
    th = spin_angle([(a, b, d0, d1, ease) for a, b, d0, d1 in segs])
    keys = [0, OP]
    for a, b, d0, d1 in segs:
        keys += [a, b]
        # the edge-on crossing (90° into the half turn): find it by bisection
        lo, hi = a, b
        for _ in range(50):
            m = (lo + hi) / 2
            if th(m) < d0 + 90:
                lo = m
            else:
                hi = m
        keys.append(round((lo + hi) / 2, 2))
    keys = sorted(set(keys))
    sx = fit(lambda t: max(4.0, 100 * abs(math.cos(math.radians(th(t))))), keys)     # never 0: rlottie would drop the frame
    st = Track([sx.k[0][1], 100], sx.k[0][0])
    for i in range(1, len(sx.k)):
        st.to(sx.k[i][0], [sx.k[i][1], 100], sx.k[i - 1][2])
    body = rig(c, "body", (cx, cy + H / 2))
    # three designs, each visible for its 180° window (hold keys on opacity)
    edges = [k for k in keys if k not in (0, OP) and all(abs(k - v) > 0.01 for seg in segs for v in seg[:2])]
    for i, g in enumerate(letters):
        o = Track(100 if i == 0 else 0, 0)
        for j, t in enumerate(edges):
            nxt = (j + 1) % 3
            o.k[-1][2] = "hold"
            o.k.append([t, 100 if nxt == i else 0, None])
        o.loop(OP, "lin")
        c.layer(f"L{i}", [geo.shape(g, nm=f"L{i}")], parent=body, p=(cx, cy), a=(cx, cy), s=st, o=o)
    # weight: the axis dips a touch on every rest
    ys = Track(float(cy + H / 2), 0)
    for a, b, *_ in segs:
        ys.hold(b).to(b + 4, cy + H / 2 + 6.0, "o").to(b + 12, float(cy + H / 2), "io")
    ys.loop(OP)
    body.p = Split(cx, ys)


# ================================================================ 151 💀 brand skull


@emoji("151-skull-x", "💀", "череп, x_x, умер, готика, xtc, мрак", "skull, x_x, dead, gothic, xtc, dark",
       "брендовый череп: глазницы — логотипные X, челюсть медленно отвисает и клацает (slam), X-глазницы вспыхивают шире на клацке, голова тяжело кренится и возвращается",
       op=150, series="v1")
def skull_x(c):
    OP = 150
    cx = 256
    cran = geo.U(geo.disc(cx, 196, 168, 32), geo.rrect(cx - 128, 220, cx + 128, 350, 44))
    cran = geo.U(cran, geo.rrect(cx - 92, 330, cx + 92, 372, 20))                   # upper teeth row
    cran = cran.difference(geo.poly([(cx, 262), (cx - 22, 306), (cx + 22, 306)]).buffer(6))   # nose
    for k in range(4):
        tx = cx - 54 + k * 36
        cran = cran.difference(geo.rrect(tx - 9, 342, tx + 9, 372, 6))
    eye = lambda x: brand_x(x, 214, 118, 62)
    head = rig(c, "head", (cx, 300), r=seq(0, [(70, None, None), (96, -7, "io"), (120, 0, "io")], op=OP))
    hl = part(c, "cranium", cran, head, (cx, 300))
    for i, x in enumerate((cx - 70, cx + 70)):
        es = seq([100, 100], [(44, None, None), (46, [116, 116], "snap"), (56, [100, 100], "io")], op=OP)
        geo.hole(hl, eye(x), nm=f"eye{i}", p=(x, 214), a=(x, 214), s=es)
    jaw = geo.rrect(cx - 104, 384, cx + 104, 452, 30)
    for k in range(4):
        tx = cx - 54 + k * 36
        jaw = jaw.difference(geo.rrect(tx - 9, 384, tx + 9, 410, 6))
    jy = seq(384.0, [(16, None, None), (38, 428.0, "decel"), (45, 384.0, "slam"), (46, 384.0, "lin")], op=OP)
    js = seq([100, 100], [(45, None, None), (46, [106, 92], "lin"), (54, [98, 102], "io"), (62, [100, 100], "io")], op=OP)
    part(c, "jaw", jaw, head, (cx, 384), p=Split(cx, jy), s=js)
    hs = seq([100, 100], [(45, None, None), (46, [103, 97], "lin"), (54, [99, 101], "io"), (62, [100, 100], "io")], op=OP)
    head.s = hs


# ================================================================ 152 🧱 LEGO head with the branding


def cyl_track(th, phi, R, cx, keys):
    """a feature printed on a cylinder at angle phi: screen x = cx + R sin(th+phi), width = cos(th+phi),
    visible while it faces the camera (cos > 0). Returns (x track, scaleX track, opacity hold track)."""
    from xtc.lot import fit
    from xtc.motion import crossings
    f = lambda t: math.radians(th(t) + phi)
    x = fit(lambda t: cx + R * math.sin(f(t)), keys)
    # width 0 while it faces away (rlottie ignores animated group opacity); squared so the Hermite fit
    # has a zero slope at the crossing and never dips below 0
    sx = fit(lambda t: 100 * max(0.0, math.cos(f(t))) ** 2 / 1.0, keys)
    st = Track([sx.k[0][1], 100], sx.k[0][0])
    for i in range(1, len(sx.k)):
        st.to(sx.k[i][0], [sx.k[i][1], 100], sx.k[i - 1][2])
    o = Track(100 if math.cos(f(0)) > 0 else 0, 0)
    for t in keys:
        if 0 < t < keys[-1]:
            v = 100 if math.cos(f(t + 0.05)) > 0 else 0
            if v != o.v:
                o.k[-1][2] = "hold"
                o.k.append([t, v, None])
    o.loop(keys[-1], "lin")
    return x, st, o


@emoji("152-lego-head", "🧱", "лего, голова, фигурка, xtc, челик, минифиг", "lego, head, minifig, xtc, figure, toy",
       "LEGO-голова с X_X: настоящий цилиндр — при тяжёлом обороте лицо уезжает по поверхности и прячется за край, на затылке проявляется принт XTC; покой, оборот обратно, кивок",
       op=180, series="drop")
def lego_head(c):
    from xtc.motion import spin_angle
    OP = 180
    cx, cy = 256, 276
    R, H = 150, 300
    head = geo.U(geo.rrect(cx - R, cy - H / 2, cx + R, cy + H / 2, 56), geo.rrect(cx - 54, cy - H / 2 - 40, cx + 54, cy - H / 2 + 10, 12),
                 geo.rrect(cx - 60, cy + H / 2 - 10, cx + 60, cy + H / 2 + 30, 10))
    segs = [(24, 68, 0, 180, (0.4, 0.0, 0.15, 1.0)), (108, 152, 180, 360, (0.4, 0.0, 0.15, 1.0))]
    th = spin_angle(segs)
    # keys: seg ends + every 90° crossing for every printed feature offset (features: -22, 0, 22, 180)
    keys = {0, OP}
    for a, b, d0, d1, _ in segs:
        keys |= {a, b}
        for phi in (-22, 0, 22, 180):
            for target in range(-720, 1080, 90):
                tg = target - phi
                if min(d0, d1) < tg < max(d0, d1):
                    lo, hi = a, b
                    for _ in range(50):
                        m = (lo + hi) / 2
                        if (th(m) < tg) == (d1 > d0):
                            lo = m
                        else:
                            hi = m
                    keys.add(round((lo + hi) / 2, 2))
    keys = sorted(keys)
    # nod on the rests
    hy = seq(float(cy + H / 2), [(70, None, None), (76, cy + H / 2 + 8.0, "o"), (86, float(cy + H / 2), "io"), (154, None, None), (160, cy + H / 2 + 8.0, "o"), (170, float(cy + H / 2), "io")], op=OP)
    body = rig(c, "body", (cx, cy + H / 2), p=Split(cx, hy))
    hl = part(c, "head", head, body, (cx, cy))
    # printed features as holes riding on the cylinder
    feats = [("eyeL", brand_x(cx, cy - 44, 92, 50), -24), ("eyeR", brand_x(cx, cy - 44, 92, 50), 24),
             ("mouth", geo.brush([(cx - 40, cy + 50), (cx + 40, cy + 50)], 28, taper=(0.9, 0.9), smooth=False), 0),
             ("print", logo.word("XTC", cx, cy + 4, 48, 262), 180)]
    for nm, g, phi in feats:
        b = g.bounds
        ax = (b[0] + b[2]) / 2
        x, st, o = cyl_track(th, phi, R * 0.62 if nm != "print" else R * 0.1, cx, keys)
        g = geo.move(g, cx - ax, 0)
        grp_y = (b[1] + b[3]) / 2
        geo.hole(hl, g, nm=nm, p=Split(x, grp_y), a=(cx, grp_y), s=st)


# ================================================================ 43 🦂 scorpion (rebuilt)


def scorpion_parts(cx=250, cy=330):
    """side view: body with the logo X on its back, two claws to the right, tail curling up over the back."""
    body = geo.U(geo.ellipse(cx, cy, 128, 54, 32), geo.ellipse(cx - 100, cy - 6, 56, 40, 24))
    body = body.difference(brand_x(cx + 6, cy - 2, 120, 56, bold=8))
    legs = []
    for k, x in enumerate((cx - 72, cx - 24, cx + 24, cx + 72)):
        legs.append(geo.brush([(x, cy + 30), (x - 18, cy + 72), (x - 4, cy + 110)], 26, taper=(1.0, 0.6), smooth=True, n=6))
    head = geo.ellipse(cx + 128, cy - 4, 46, 34, 24)
    # claws: arm + pincer (two jaws), on the right
    arm = geo.brush([(cx + 150, cy - 10), (cx + 200, cy - 60)], 34, taper=(1.0, 0.9), smooth=False)
    jaw_top = geo.brush([(cx + 196, cy - 64), (cx + 236, cy - 96), (cx + 258, cy - 74)], 30, taper=(1.0, 0.5), smooth=True, n=6)
    jaw_bot = geo.brush([(cx + 196, cy - 64), (cx + 246, cy - 48), (cx + 256, cy - 68)], 30, taper=(1.0, 0.5), smooth=True, n=6)
    # tail: 5 segments arcing up and over the back from the rear, sting at the tip
    pts = [(cx - 150, cy - 20), (cx - 196, cy - 80), (cx - 190, cy - 160), (cx - 130, cy - 220), (cx - 50, cy - 236), (cx + 20, cy - 214)]
    tail = geo.brush(pts, 44, taper=(1.0, 0.7), smooth=True, n=8)
    for k, p in enumerate(pts[1:5]):
        tail = geo.U(tail, geo.disc(p[0], p[1], 30 - k * 2))
    sting = geo.poly([(cx + 8, cy - 232), (cx + 40, cy - 202), (cx + 60, cy - 150), (cx + 18, cy - 196)]).buffer(6).buffer(-6)
    return geo.U(body, *legs, head, arm), (jaw_top, jaw_bot, (cx + 196, cy - 64)), (geo.U(tail, sting), (cx - 150, cy - 20))


@emoji("43-scorpion-sigil", "🦂", "скорпион, x, xtc, жало, удар, готика", "scorpion, x, xtc, sting, strike, goth",
       "скорпион с логотипным X на спине: хвост взводится назад (антиципация), бьёт жалом вперёд с ударом и дрожью, клешня щёлкает дважды, тело подаётся вперёд и садится",
       op=150, series="v1")
def scorpion(c):
    OP = 150
    cx, cy = 250, 330
    body, (jt, jb, jp), (tail, tp) = scorpion_parts(cx, cy)
    fit_ = rig(c, "fit", (256, 256), s=(78, 78), p=(266, 262))
    # body lunge on the strike
    bx = seq(float(cx), [(30, None, None), (40, cx - 10.0, "io"), (46, cx + 18.0, "slam"), (47, cx + 18.0, "lin"), (58, cx - 4.0, "o"), (70, float(cx), "io")], op=OP)
    bs = seq([100, 100], [(45, None, None), (46, [106, 94], "lin"), (54, [98, 102], "io"), (62, [100, 100], "io")], op=OP)
    root = rig(c, "body", (cx, cy + 110), parent=fit_, p=Split(bx, cy + 110), s=bs)
    # tail: winds back 24f, strikes forward 6f (rotation about its root), quivers, returns slowly
    tr = seq(0, [(14, None, None), (38, -34, "io"), (44, 42, "strike"), (46, 36, "io"), (48, 44, "io"), (50, 38, "io"), (52, 42, "io"), (54, 40, "io"),
                 (74, None, None), (100, 0, "io")], op=OP)
    part(c, "tail", tail, root, tp, r=tr)
    part(c, "body", body, root, (cx, cy))
    # claw: the top jaw snaps shut twice after the strike
    jr = seq(0, [(56, None, None), (60, 22, "decel"), (64, 0, "slam"), (68, None, None), (72, 22, "decel"), (76, 0, "slam")], op=OP)
    part(c, "jawT", jt, root, jp, r=jr)
    part(c, "jawB", jb, root, jp)


# ================================================================ gothic crosses (rebuilt): tapered arms, spear tips, the logo X at the crossing


def gothic_cross(cx=256, cy=256, L=200, w=56, arms=(0.62, 1.0, 0.62, 0.56), x_w=0.0):
    """gothic cross: each arm narrows to a waist, flares and ends in a spear point; arms = (right, down,
    left, up) as fractions of L. x_w > 0 cuts the logo X (that wide) through the crossing."""
    parts = []
    for ang, f in zip((0, 90, 180, 270), arms):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        L_ = L * f
        prof = [(0.0, 0.5), (0.5, 0.36), (0.8, 0.5), (0.9, 0.95), (1.0, 0.0)]
        side1 = [(cx + ux * L_ * s + px * w * k, cy + uy * L_ * s + py * w * k) for s, k in prof]
        side2 = [(cx + ux * L_ * s - px * w * k, cy + uy * L_ * s - py * w * k) for s, k in prof[::-1]]
        parts.append(geo.poly(side1 + side2))
    g = geo.U(*parts).buffer(3, join_style=2).buffer(-3, join_style=2)
    g = geo.U(g, geo.disc(cx, cy, w * 0.9, 24))
    if x_w:
        g = g.difference(brand_x(cx, cy, x_w, x_w * 0.46, bold=6))
    return g


@emoji("144-cross-pendant", "☦️", "крест, подвеска, цепь, готика, xtc", "cross, pendant, chain, gothic, xtc",
       "готический крест-подвеска с логотипным X в перекрестии: висит на цепи из люверсов, тяжёлый маятник с затуханием, в крайних точках разворачивается ребром (torso), на обороте — гладкий",
       op=150, series="cross")
def pendant(c):
    OP = 150
    top = (256, 14)
    hang = 56
    ccx, ccy = 256, top[1] + hang + 190
    cross = gothic_cross(ccx, ccy, 196, 50, x_w=112)
    back = gothic_cross(ccx, ccy, 196, 50)
    links = geo.U(*[geo.ring(256, top[1] + 16 + k * 28, 14, 6, 12) for k in range(2)])
    pr = seq(0, [(6, None, None), (18, -12, "io"), (44, 11, "io"), (70, -7, "io"), (94, 4, "io"), (114, -2, "io"), (132, 0.8, "io"), (148, 0, "io")], op=OP)
    pend = rig(c, "pend", top, r=pr)
    part(c, "chain", links, pend, top)
    body = rig(c, "body", (256, top[1] + hang), parent=pend)
    segs = [(12, 44, 0, 180, "io"), (44, 70, 180, 360, "io"), (70, 94, 360, 520, "io"), (94, 114, 520, 720, "io")]
    root, th, fr, bk = M.spin3d(c, "cross", cross, back, ccx, ccy, segs, thick=24, lip=16, parent=body)
    M.glare_sweep(c, fr, ccx, ccy, 116, 22, travel=300, parent=root, length=520, w1=24, w2=10, gap=12)


@emoji("28-tribal-cross", "✝️", "крест, вера, святое, готика, аминь, xtc", "cross, faith, holy, gothic, amen, xtc",
       "большой готический крест с логотипным X: стоит, тяжело поднимается (антиципация) и падает, вбивается в землю — 1f удар, ударные линии, дрожь; по граням бежит блик; покой",
       op=150, series="v1")
def gothic_big(c):
    OP = 150
    cx, cy = 256, 236
    cross = gothic_cross(cx, cy, 236, 60, arms=(0.66, 1.0, 0.66, 0.6), x_w=134)
    y = seq(float(cy), [(20, None, None), (34, cy - 40.0, "io"), (46, cy + 8.0, "slam"), (47, cy + 8.0, "lin"), (56, cy - 4.0, "o"), (66, float(cy), "io")], op=OP)
    s_ = seq([100, 100], [(20, None, None), (34, [96, 104], "io"), (46, [108, 92], "slam"), (47, [108, 92], "lin"), (56, [97, 103], "o"), (66, [100, 100], "io")], op=OP)
    px = seq(256.0, [(47, None, None)])
    M.shake(px, 47, 61, 4, 256.0, step=2, decay=0.7)
    px.loop(OP)
    root = rig(c, "cross", (cx, cy + 236), p=Split(px, _sh2(y, 236)), s=s_)
    lay = part(c, "cross", cross, root, (cx, cy))
    hit_lines(c, "hit", [((80, 470), (40, 484)), ((432, 470), (472, 484)), ((150, 486), (120, 500)), ((362, 486), (392, 500))], 46, w=20)
    M.glare_sweep(c, lay, cx, cy, 90, 28, travel=420, angle=-35, parent=root, length=700, w1=30, w2=12, gap=14)


def _sh2(tr, d):
    out = Track(tr.k[0][1] + d, tr.k[0][0])
    out.k = [[t, v + d, e] for t, v, e in tr.k]
    return out


# ================================================================ 25 🎭 hockey mask (rebuilt clean)


def hockey_mask(cx=256, cy=262):
    face = geo.ellipse(cx, cy, 176, 226, 48)
    face = geo.U(face, geo.rrect(cx - 150, cy - 40, cx + 150, cy + 150, 60)).intersection(geo.ellipse(cx, cy + 10, 180, 236, 48))
    face = face.buffer(-8, join_style=1).buffer(8, join_style=1)
    eyes = geo.U(geo.ellipse(cx - 72, cy - 40, 46, 30, 24), geo.ellipse(cx + 72, cy - 40, 46, 30, 24))
    vents = []
    for (x, y) in ((cx - 100, cy + 30), (cx + 100, cy + 30), (cx - 110, cy + 92), (cx + 110, cy + 92), (cx - 60, cy + 120), (cx + 60, cy + 120),
                   (cx, cy + 150), (cx - 34, cy + 178), (cx + 34, cy + 178), (cx - 70, cy + 60), (cx + 70, cy + 60), (cx, cy + 92)):
        vents.append(geo.disc(x, y, 13, 12))
    holes = geo.U(eyes, *vents)
    x = brand_x(cx, cy - 150, 112, 54, bold=8)
    return face.difference(holes).difference(x), holes, eyes


@emoji("25-mask-glyphs", "🎭", "маска, хоррор, маньяк, пятница, джейсон, xtc", "mask, horror, slasher, creepy, jason, xtc",
       "хоккейная маска с логотипным X на лбу медленно поворачивается к тебе (параллакс прорезей), в глазницах загораются глаза и косятся, по маске бежит блик",
       op=180, series="v1")
def mask(c):
    OP = 180
    shell, holes, eyes = hockey_mask()
    cx, cy = 256, 262
    sx = Track([95, 100], 0).hold(20).to(60, [100, 100], "io").hold(140).to(176, [95, 100], "io").loop(OP)
    base = c.layer("mask", [geo.shape(shell, nm="shell")], p=(cx, cy), a=(cx, cy), s=sx)
    hx = Track([-10, 0], 0).hold(20).to(60, [0, 0], "io").hold(140).to(176, [-10, 0], "io").loop(OP)
    geo.hole(base, holes, nm="holes", p=hx)
    off = c.null("eyes", p=Split(Track(256, 0).hold(20).to(60, 266, "io").hold(140).to(176, 256, "io").loop(OP), 256), a=(256, 256))
    for k, e in enumerate(sorted(geo._polys(eyes), key=lambda e: e.centroid.x)):
        ex, ey = e.centroid.x - 10, e.centroid.y
        es = Track([0, 0], 0).hold(64 + k * 3).to(72 + k * 3, [118, 118], "snap").to(78 + k * 3, [100, 100], "io")
        es.hold(128).to(132, [110, 10], "i").to(136, [0, 0], "lin").loop(OP, "lin")
        ep = Track([ex, ey], 0).hold(86).to(94, [ex + 14, ey], "snap").hold(104).to(112, [ex - 12, ey + 2], "snap").hold(120).to(126, [ex, ey], "io").loop(OP)
        c.layer(f"eye{k}", [geo.shape(geo.disc(ex, ey, 20), nm="eye")], parent=off, p=ep, a=(ex, ey), s=es)
    M.glare_sweep(c, base, cx, cy, 96, 30, travel=420, angle=-35, length=700, w1=30, w2=12, gap=14)
