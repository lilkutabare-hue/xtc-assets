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


@emoji("144-cross-pendant", "☦️", "крест, подвеска, цепь, готика, xtc", "cross, pendant, chain, gothic, xtc",
       "готический крест-подвеска на цепи из люверсов: качается маятником с затуханием, на крайней точке разворачивается ребром и ловит ✦ на лепестке",
       op=150, series="cross")
def pendant(c):
    OP = 150
    top = (256, 14)
    hang = 60
    cross = fleury_cross(256, top[1] + hang + 176, 190, 50, arms=(0.62, 1.0, 0.62, 0.56))
    back = cross.difference(brand_x(256, top[1] + hang + 176, 110, 56))
    links = geo.U(*[geo.ring(256, top[1] + 18 + k * 30, 15, 6, 12) for k in range(2)])
    # pendulum from the bail: big swing, damped 4 half-periods
    pr = seq(0, [(6, None, None), (16, -13, "io"), (40, 12, "io"), (64, -8, "io"), (86, 5, "io"), (106, -2.5, "io"), (124, 1, "io"), (140, 0, "io")], op=OP)
    pend = rig(c, "pend", top, r=pr)
    part(c, "chain", links, pend, top)
    body = rig(c, "body", (256, top[1] + hang), parent=pend)
    # the cross twists edge-on at the extremes of the swing (fake-3D about its own axis)
    segs = [(10, 40, 0, 180, "io"), (40, 64, 180, 360, "io"), (64, 86, 360, 520, "io"), (86, 106, 520, 720, "io")]
    root, th, fr, bk = M.spin3d(c, "cross", cross, back, 256, top[1] + hang + 176, segs, thick=26, lip=18, parent=body)
    M.glare_sweep(c, fr, 256, top[1] + hang + 176, 110, 24, travel=300, parent=root, length=520, w1=26, w2=12, gap=12,
                  sparks=[(256 + 120, top[1] + hang + 70, 36, 112, 22)])


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
       "лаковое сердце с логотипным X: два удара, дрожь, трещина щёлкает раз, два — половинки отваливаются на шарнире-кончике и качаются, X рвётся пополам, из разлома капает латекс; срастаются обратно",
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
    # latex drips off the crack lips: two drops fall from the dip, one stretches from the lower lip
    for k, (t0, x0, y0) in enumerate(((58, hx - 10, by0 + d * 1.2), (66, hx + 14, by0 + d * 2.6), (96, hx - 12, by0 + d * 1.6))):
        M.particle(c, f"drop{k}", geo.drop(x0, y0, 15, 36), t0, 30, (x0, y0), (x0 + (-18 if k % 2 == 0 else 18), by1 + 30), None,
                   anchor=(x0, y0), fall="i5", pop=0.25, fade=0.25, s_end=60)


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
    sx = fit(lambda t: 100 * abs(math.cos(math.radians(th(t)))), keys)
    st = Track([sx.k[0][1], 100], sx.k[0][0])
    for i in range(1, len(sx.k)):
        st.to(sx.k[i][0], [sx.k[i][1], 100], sx.k[i - 1][2])
    body = rig(c, "body", (cx, cy + H / 2))
    # edge band (thickness) near edge-on
    band = geo.rect(cx - 16, cy - H / 2 + 8, cx + 16, cy + H / 2 - 8)
    bs = fit(lambda t: 100 * max(0.0, 1 - abs(math.cos(math.radians(th(t)))) / 0.35), keys)
    bt = Track([bs.k[0][1], 100], bs.k[0][0])
    for i in range(1, len(bs.k)):
        bt.to(bs.k[i][0], [bs.k[i][1], 100], bs.k[i - 1][2])
    c.layer("band", [geo.shape(band, nm="band")], parent=body, p=(cx, cy), a=(cx, cy), s=bt)
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
