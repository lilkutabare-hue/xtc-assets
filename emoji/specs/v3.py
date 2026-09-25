"""v3: brand objects and innovations (STYLE.md). Replaces 45 and 52 from drop.py."""
import math

from xtc import geo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import board_push, brand_font, brand_word, cross_letters, longsleeve, tile_glyph


def shape_layer(c, nm, g, parent=None, anchor=(256, 256), p=None, s=None, r=None, o=100, ip=0, op=None):
    return c.layer(nm, [geo.shape(g, nm=nm)], parent=parent, p=p if p is not None else anchor, a=anchor,
                   s=s if s is not None else (100, 100), r=r if r is not None else 0, o=o, ip=ip, op=op)


def hit_lines(c, nm, pts, t0, w=22, life=10):
    """M8 impact lines: short strokes drawn by trim, end leads and start follows 2f later."""
    for k, (p0, p1) in enumerate(pts):
        e = Track(0, 0).hold(t0).to(t0 + 7, 100, "o").hold(c.op)
        s = Track(0, 0).hold(t0 + 2).to(t0 + 9, 100, "i").hold(c.op)
        c.layer(f"{nm}{k}", [geo.stroked([p0, p1], w, e=e, s=s)], p=(0, 0), a=(0, 0), ip=t0, op=t0 + life)


def click(tr, t, base=(100, 100), amp=(7, -7), per=8):
    """1-frame contact squash then a damped settle (chrome click)."""
    tr.hold(t).to(t + 1, [base[0] + amp[0], base[1] + amp[1]], "slam").to(t + 2, [base[0] + amp[0], base[1] + amp[1]], "lin")
    M.settle(tr, t + 2 + per, list(base), [-amp[0] * 0.45, -amp[1] * 0.45], n=2, per=per, hit="io")
    return tr


# ================================================================ 45 🔒 belt buckle (REDO)


@emoji("45-buckle-lock", "🔒", "застегнись, договорились, замок, закрыто, ремень, пряжка", "lock, deal, locked, belt, buckle, fasten",
       "ремень с двумя рядами люверсов въезжает в хромовую пряжку, язычок падает в люверс — щелчок, отдача рамки, ✦ по хрому; подтяжка, и ремень выезжает обратно",
       op=150, series="drop")
def buckle(c):
    # chrome frame on the right; the strap comes from the left and threads through the opening
    fx0, fy0, fx1, fy1, wall = 250, 128, 496, 384, 44
    frame = geo.rrect(fx0, fy0, fx1, fy1, 44).difference(geo.rrect(fx0 + wall, fy0 + wall, fx1 - wall, fy1 - wall, 14))
    sy, sh = 256, 124
    end0, travel = 300, 120                       # strap tip rests at the opening, slides `travel` in
    strap = geo.rrect(16, sy - sh / 2, end0, sy + sh / 2, 40)
    holes = [geo.disc(end0 - 52 - 66 * k, sy + d, 19) for k in range(4) for d in (-30, 30)]
    strap = strap.difference(geo.U(*holes))
    hit_x = end0 - 52 + travel                    # first eyelet lands under the tongue tip
    pivot = (fx0 + wall - 4, sy - 30)
    tongue = geo.U(geo.rrect(pivot[0] - 18, pivot[1] - 15, hit_x, pivot[1] + 15, 15), geo.disc(hit_x, pivot[1], 14))
    root = c.null("root", p=(256, 256), a=(256, 256))
    sx = Track(256, 0).hold(14).to(46, 256 + travel + 6, (0.5, 0.0, 0.18, 1.0)).to(52, 256 + travel, "io").hold(70)
    sx.to(80, 256 + travel - 12, "i5").to(92, 256 + travel, "o").hold(120).to(146, 256, "io").loop(150)
    c.layer("strap", [geo.shape(strap, nm="strap")], parent=root, p=Split(sx, 256), a=(256, 256))
    fs = Track([100, 100], 0)
    click(fs, 50, amp=(4, -5))
    fs.hold(80).to(84, [101.5, 99], "io").to(92, [100, 100], "io").loop(150)
    fcx = (fx0 + fx1) / 2
    fr = c.layer("frame", [geo.shape(frame, nm="frame")], parent=root, p=(fcx, sy), a=(fcx, sy), s=fs)
    tr = Track(0, 0).hold(8).to(20, -34, "io").hold(44).to(50, 3, "slam").to(51, 3, "lin").to(56, -2, "io").to(62, 0, "io")
    tr.hold(116).to(126, -34, "io").hold(136).to(148, 0, "io").loop(150)
    c.layer("tongue", [geo.shape(tongue, nm="tongue")], parent=root, p=pivot, a=pivot, r=tr)
    hit_lines(c, "hit", [((fx1 - 44, fy0 - 14), (fx1 - 30, fy0 - 46)), ((fx0 + 44, fy0 - 14), (fx0 + 30, fy0 - 46)),
                         ((fx1 - 44, fy1 + 14), (fx1 - 30, fy1 + 46)), ((fx0 + 44, fy1 + 14), (fx0 + 30, fy1 + 46))], 50, w=20)
    M.glare_sweep(c, fr, fx1 - 70, fy0 + 40, 54, 22, travel=140, angle=-35, length=260, w1=26, w2=12, gap=12,
                  sparks=[(fx0 + 24, fy1 - 22, 34, 56, 22)])


# ================================================================ 131-133 the XTC tiles (puzzle)


def tile(c, ch):
    """one split-flap tile of the pinned board; all three share timing so a row X T C flips as one board."""
    w, h, cy = 424, 424, 258
    bs = Track([100, 100], 0)
    board_push(bs, 40)
    board_push(bs, 76)
    board = c.null("board", p=(256, cy + h / 2), a=(256, cy + h / 2), s=bs.loop(150))
    M.flip_tile(c, "t", board, 256, cy, w, h, [tile_glyph(ch, 256, cy, w, h, fw=0.74, fh=0.66, bold=12), None],
                [40, 76], dur=12, gap=14, r=30, bounce=9)


@emoji("131-tile-x", "🇽", "x, икс, xtc, плитка, табло", "x, xtc, tile, board, letter",
       "плитка X закрепа: перещёлкивается в пустую и обратно на тех же кадрах, что T и C — подряд в тексте три плитки читаются как табло XTC",
       op=150, series="drop")
def tile_x(c):
    tile(c, "X")


@emoji("132-tile-t", "🇹", "t, тэ, xtc, плитка, табло", "t, xtc, tile, board, letter",
       "плитка T закрепа: перещёлкивается синхронно с X и C", op=150, series="drop")
def tile_t(c):
    tile(c, "T")


@emoji("133-tile-c", "🇨", "c, си, xtc, плитка, табло", "c, xtc, tile, board, letter",
       "плитка C закрепа: перещёлкивается синхронно с X и T", op=150, series="drop")
def tile_c(c):
    tile(c, "C")


# ================================================================ 134 🎽 louverse tank


def tank_shape(cx=256, top=70, bottom=486):
    """tank top: narrow straps, deep round armholes, U neckline, hem slightly wider than the chest."""
    hw_chest, hw_hem, strap_w = 136, 158, 34
    body = geo.poly([(cx - hw_chest, top + 150), (cx - hw_hem, bottom), (cx + hw_hem, bottom), (cx + hw_chest, top + 150)])
    straps = geo.U(geo.rrect(cx - 96 - strap_w / 2, top, cx - 96 + strap_w / 2, top + 180, 14), geo.rrect(cx + 96 - strap_w / 2, top, cx + 96 + strap_w / 2, top + 180, 14))
    yoke = geo.rect(cx - 96, top + 100, cx + 96, top + 190)
    body = geo.U(body, straps, yoke)
    body = body.difference(geo.ellipse(cx, top + 22, 84, 110, 24))                     # U neckline
    body = body.difference(geo.ellipse(cx - hw_chest - 40, top + 78, 90, 100, 24))       # armholes
    body = body.difference(geo.ellipse(cx + hw_chest + 40, top + 78, 90, 100, 24))
    return body.buffer(10, join_style=1).buffer(-10, join_style=1)


DOTS = {"X": ["X.X", "X.X", ".X.", "X.X", "X.X"], "T": ["XXX", ".X.", ".X.", ".X.", ".X."], "C": [".XX", "X..", "X..", "X..", ".XX"]}


@emoji("134-louverse-tank", "🎽", "louverse, майка, люверсы, xtc, вещь, дроп", "louverse, tank top, eyelets, xtc, merch, drop",
       "louverse tank: XTC выложено люверсами на ткани; ткань дышит, люверсы моргают волной слева направо (кольцо сжимается в щель), на выдохе хром ловит ✦",
       op=150, series="drop")
def tank(c):
    """the louverse tank from the client's render (silhouette traced 1:1), the XTC eyelet print at the
    print's real size and place (print width ~31% of the tank)."""
    OP = 150
    import os
    body = geo.svg(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v1", "rec", "tank.svg"))
    b_ = body.bounds
    tw = b_[2] - b_[0]
    pitch = tw * 0.40 / 10.5
    r = pitch * 0.36
    x0 = 256 - 5 * pitch
    y0 = b_[1] + (b_[3] - b_[1]) * 0.40
    cols = {}
    col = 0
    for ch in "XTC":
        for j in range(3):
            for i, row in enumerate(DOTS[ch]):
                if row[j] == "X":
                    cols.setdefault(col, []).append(geo.disc(x0 + col * pitch, y0 + i * pitch, r))
            col += 1
        col += 1
    # the tank hangs and sways heavily from its straps; a tug at 90 with a damped settle
    rr = Track(0, 0).to(24, 2.5, "io").to(54, -2, "io").to(82, 1.3, "io").hold(90).to(96, -3.5, "snap")
    M.settle(rr, 104, 0, 2.2, n=3, per=16, decay=0.5, hit="io")
    rr.loop(OP)
    root = c.null("root", p=(256, b_[1]), a=(256, b_[1]), r=rr)
    lay = c.layer("tank", [geo.shape(body, nm="tank")], parent=root, p=(256, b_[1]), a=(256, b_[1]))
    # the eyelets blink in a wave, twice per loop (ring -> slit -> ring)
    for k, g in cols.items():
        cx = x0 + k * pitch
        s = Track([100, 100], 0)
        for t0 in (24, 100):
            t = t0 + k * 3
            s.hold(t).to(t + 5, [112, 10], "i").to(t + 11, [100, 100], "o")
        s.loop(OP)
        geo.hole(lay, geo.U(*g), nm=f"col{k}", p=(cx, y0 + 2 * pitch), a=(cx, y0 + 2 * pitch), s=s)


# ================================================================ 135 👖 LATEXX pants


def pants_shape(cx=256, top=42, bottom=488):
    waist_w, hip_w, hem_w, crotch = 132, 150, 96, 250
    left = [(cx - waist_w, top), (cx - hip_w, top + 90), (cx - hip_w - 4, bottom - 140), (cx - hem_w - 22, bottom), (cx - 30, bottom), (cx - 8, crotch)]
    right = [(cx + 8, crotch), (cx + 30, bottom), (cx + hem_w + 22, bottom), (cx + hip_w + 4, bottom - 140), (cx + hip_w, top + 90), (cx + waist_w, top)]
    return geo.poly(left + right).buffer(14).buffer(-10)


@emoji("135-latexx-pants", "👖", "latexx, латекс, штаны, лак, xtc, вещь", "latexx, latex pants, gloss, xtc, merch, drop",
       "100% LATEXX: штаны приседают и тянутся как латекс (объём сохраняется), отпружинивают желе, по глянцу бежит блик-вырез, молния едет вниз и ловит ✦ на бегунке",
       op=150, series="drop")
def pants(c):
    g = pants_shape()
    cx = 256
    # waistband slot + fly: zip teeth as a column of holes, the slider is a black tab riding in a slot
    band = geo.rrect(cx - 118, 62, cx + 118, 80, 8)
    g = g.difference(band)
    slot = geo.rrect(cx - 16, 88, cx + 16, 262, 12)
    # latex stretch: squat (wide) -> pull (tall) -> jelly settle; anchor at the hem
    s = Track([100, 100], 0).hold(16).to(30, [109, 92], "io").to(40, [94, 106], "o").to(41, [94, 106], "lin")
    M.settle(s, 50, [100, 100], [4, -3], n=3, per=9, decay=0.5, hit="io")
    s.hold(120).to(150, [100, 100], "io")
    lay = c.layer("pants", [geo.shape(g, nm="pants")], p=(cx, 488), a=(cx, 488), s=s)
    # the fly slot opens behind the slider as it rides down (trim-like: hole grows from the top)
    zs = Track([100, 6], 0).hold(64).to(96, [100, 100], (0.5, 0.0, 0.2, 1.0)).hold(126).to(142, [100, 6], "io").loop(150)
    geo.hole(lay, slot, nm="slot", p=(cx, 88), a=(cx, 88), s=zs)
    # slider: a chrome tab riding down the open slot (drawn above the hole)
    tab = geo.rrect(cx - 14, 56, cx + 14, 98, 9).difference(geo.disc(cx, 86, 7))
    ty = Track(88, 0).hold(64).to(96, 88 + 150, (0.5, 0.0, 0.2, 1.0)).hold(126).to(142, 88, "io").loop(150)
    c.layer("slider", [geo.shape(tab, nm="tab")], p=Split(cx, ty), a=(cx, 88))
    M.glare_sweep(c, lay, cx, 300, 60, 34, travel=360, angle=-30, length=620, w1=34, w2=14, gap=16,
                  sparks=[(cx + 4, 246, 26, 98, 22), (cx - 96, 150, 34, 84, 26)])


# ================================================================ 136 📸 flash on the parking lot


@emoji("136-flash", "📸", "вспышка, фото, паркинг, ночь, кадр, xtc", "flash, photo, camera, night, parking, xtc",
       "ночная карточка с крест-лого дрожит в руках — вспышка: на 3 кадра всё уходит в негатив (карточка белая, лого чёрное), потом чёрное проявляется обратно с пережогом; второй кадр короче",
       op=150, series="drop")
def flash(c):
    card = geo.rrect(30, 30, 482, 482, 44)
    L = cross_letters(256, 262, lh=74, width=410)
    logo = geo.U(*[g for g, _ in L.values()])
    pos = card.difference(logo)
    neg = geo.U(card.difference(card.buffer(-30)), logo)
    # handheld micro-shake of the whole card
    jx = M.wave(256, 3, 50, 150, 0.0)
    jy = M.wave(256, 2, 75, 150, 1.2)
    rr = M.wave(0, 0.8, 30, 150, 0.4)
    root = c.null("hand", p=Split(jx, jy), a=(256, 256), r=rr)
    # flash windows: negative on [36, 39) and [96, 98)
    po = Track(100, 0)
    no = Track(0, 0)
    for a, b in ((36, 39), (96, 98)):
        for tr, v_in in ((po, 0), (no, 100)):
            tr.k[-1][2] = "hold"
            tr.k.append([a, v_in, None])
            tr.k[-1][2] = "hold"
            tr.k.append([b, 100 - v_in, None])
    po.hold(150)
    no.hold(150)
    # burn-in: after the flash the logo hole blooms 112% and shrinks back (the black "develops")
    ps = Track([100, 100], 0)
    for t in (39, 98):
        ps.hold(t).to(t + 1, [106, 106], "lin").to(t + 9, [100, 100], "o")
    ps.loop(150)
    c.layer("pos", [geo.shape(pos, nm="pos")], parent=root, p=(256, 256), a=(256, 256), o=po, s=ps)
    c.layer("neg", [geo.shape(neg, nm="neg")], parent=root, p=(256, 256), a=(256, 256), o=no)
    # the camera ✦ pops in the corner one frame before each flash
    M.twinkle(c, "tw1", 452, 60, 40, 34, 8, spin=0)
    M.twinkle(c, "tw2", 452, 60, 32, 94, 7, spin=0)


# ================================================================ 137 🌗 longsleeve day / night


@emoji("137-tee-daynight", "🌗", "day night, лонгслив, белый чёрный, xtc, вещь, дроп", "day night, longsleeve, white black, xtc, merch, drop",
       "лонгслив XTC на вешалке: тяжёлый переворот на 180° — с ночного (чёрный) на дневной (белый = контур-дырка с чёрным лого), пауза, переворот обратно; торец даёт объём",
       op=180, series="drop")
def tee_daynight(c):
    tee, hook = longsleeve(256, 138)
    hook_g = geo.brush(geo.arc(256 + 16, 138 - 52, 28, 180, 450, 20)[::-1] + [(256, 138 - 6)], 22, taper=(0.9, 1.0), smooth=False)
    body = tee.difference(hook_g.buffer(4))
    night = body
    outline = body.difference(body.buffer(-30))
    day = geo.U(outline, brand_word("XTC", 256, 138 + 112, 42, 180, bold=9))
    # hanger swing: the flip is a hand spinning the hanger, the tee follows with a lag
    r = Track(0, 0).hold(20).to(34, -3, "io").to(74, 3, "io").to(100, -1.5, "io").to(120, 0, "io").hold(130).to(150, 2, "io").to(180, 0, "io")
    root = c.null("root", p=hook, a=hook, r=r)
    c.layer("hook", [geo.shape(hook_g, nm="hook")], parent=root, p=hook, a=hook)
    segs = [(30, 42, 0, -20, "io"), (42, 78, -20, 180, (0.35, 0.0, 0.15, 1.0)), (78, 90, 180, 172, "io"), (90, 100, 172, 180, "io"),
            (120, 132, 180, 160, "io"), (132, 168, 160, 360, (0.35, 0.0, 0.15, 1.0))]
    M.spin3d(c, "tee", night, geo.mirror(day, 256), 256, 300, segs, thick=30, lip=30, parent=root, band_h=300)
    M.twinkle(c, "tw", 256 + 150, 138 + 60, 34, 82, 20, parent=root)


# ================================================================ 138 🪙 wax seal with the cross logo


@emoji("138-seal", "🪙", "печать, сургуч, клише, лого, крест, xtc", "seal, wax, stamp, logo, cross, xtc",
       "клише опускается на сургуч, давит (блин расплющивается), поднимается — в воске остаётся оттиск крест-лого X·XTC·C дыркой, ✦ по кромке; к концу лупа воск заплывает",
       op=150, series="drop")
def seal(c):
    cx, cy, R = 256, 340, 150
    blob = geo.rough(geo.ellipse(cx, cy, 196, R, 32), amp=6, step=8, seed=3)
    L = cross_letters(cx, cy, lh=54, lw=88, dx=102, dy=82, bold=11)
    logo = geo.U(*[g for g, _ in L.values()])
    # wax: squashes under the press (anchor at the bottom), settles
    ws = Track([100, 100], 0).hold(44).to(48, [112, 86], "slam").to(49, [112, 86], "lin").hold(58).to(66, [97, 103], "o").to(74, [102, 99], "io").to(82, [100, 100], "io").loop(150)
    wax = c.layer("wax", [geo.shape(blob, nm="wax")], p=(cx, cy + R), a=(cx, cy + R), s=ws)
    # the imprint appears the moment the press lifts, melts shut at the end of the loop
    hs = Track([0, 0], 0).hold(58).to(59, [100, 100], "lin").hold(120).to(146, [100, 8], "io").loop(150, "i")
    geo.hole(wax, logo, nm="imprint", p=(cx, cy), a=(cx, cy), s=hs)
    # the press: handle from the top, descends, holds, lifts with anticipation
    handle = geo.U(geo.rrect(cx - 44, 22, cx + 44, 124, 26), geo.rrect(cx - 130, 118, cx + 130, 156, 16))
    hy = Track(156, 0).hold(24).to(30, 146, "io").to(44, cy - R + 6, "slam").to(48, cy - R + 6 + 2 * R * 0.14, "slam")
    hy.hold(58).to(74, 156, "o").loop(150)
    c.layer("press", [geo.shape(handle, nm="press")], p=Split(cx, hy), a=(cx, 156))
    hit_lines(c, "hit", [((cx - R - 10, cy - 60), (cx - R - 40, cy - 80)), ((cx + R + 10, cy - 60), (cx + R + 40, cy - 80)),
                         ((cx - R - 20, cy + 50), (cx - R - 48, cy + 60)), ((cx + R + 20, cy + 50), (cx + R + 48, cy + 60))], 48, w=20)
    M.twinkle(c, "tw", cx + R - 30, cy - R + 44, 36, 62, 22)


# ================================================================ 52 🎮 PSP with a game in the screen (REDO)


@emoji("52-psp", "🎮", "играю, залипаю, геймер, psp, мини-апп, понг", "gaming, playing, psp, gamer, mini app, pong",
       "PSP: в экране-дырке идёт понг — шарик отскакивает от ракеток, крестовина и кнопки жмутся в такт ударам, корпус кренится; пропуск — экран вспыхивает XTC и раунд заново",
       op=150, series="drop")
def psp(c):
    cx, cy = 256, 262
    scr = (150, cy - 82, 362, cy + 70)
    body = geo.rrect(22, cy - 112, 490, cy + 112, 104)
    body = body.difference(geo.rrect(*scr, 12))
    body = body.difference(geo.rrect(208, cy + 84, 304, cy + 96, 6))
    # rally: the ball bounces between the paddles, 5 hits, then a miss
    hits = [(0, "L"), (22, "R"), (44, "L"), (66, "R"), (88, "L"), (110, "miss")]
    lx, rx = scr[0] + 30, scr[2] - 30
    ys = [cy - 40, cy + 30, cy - 20, cy + 40, cy - 46, cy + 20]
    lay_rot = Track(0, 0)
    for t, side in hits[1:]:
        lay_rot.hold(t - 2).to(t + 1, -3 if side == "L" else 3, "snap").to(t + 7, 0, "io")
    lay_rot.loop(150)
    root = c.null("root", p=(cx, cy + 112), a=(cx, cy + 112), r=lay_rot)
    lay = c.layer("body", [geo.shape(body, nm="body")], parent=root, p=(cx, cy), a=(cx, cy))
    dp = geo.U(geo.rrect(58, cy - 44, 124, cy - 20, 8), geo.rrect(79, cy - 66, 103, cy + 2, 8))
    dpp = Track([0, 0], 0)
    for k, (t, side) in enumerate(hits[1:]):
        if side == "L":
            dpp.hold(t - 6).to(t - 3, [0, -8 if ys[k + 1] < ys[k] else 8], "snap").to(t + 3, [0, 0], "io")
    geo.hole(lay, dp, nm="dpad", p=dpp.loop(150))
    geo.hole(lay, geo.disc(91, cy + 50, 20), nm="nub")
    bts = [(418, cy - 58), (380, cy - 24), (456, cy - 24), (418, cy + 10)]
    for j, (bx, by) in enumerate(bts):
        s = Track([100, 100], 0)
        for k, (t, side) in enumerate(hits[1:]):
            if side == "R" and j == (0 if ys[k + 1] < ys[k] else 3):
                s.hold(t - 6).to(t - 3, [45, 45], "snap").to(t + 3, [100, 100], "o")
        geo.hole(lay, geo.disc(bx, by, 19), nm=f"btn{j}", p=(bx, by), a=(bx, by), s=s.loop(150))
    # --- the game, drawn inside the screen hole (black on the chat background)
    ball = geo.disc(0, 0, 13)
    bx = Track(lx + 16, 0)
    by = Track(ys[0], 0)
    for k, (t, side) in enumerate(hits[1:], 1):
        x = (lx + 16) if side == "L" else (rx - 16) if side == "R" else scr[2] + 30
        bx.to(t, x, "lin")
        by.to(t, ys[k] if side != "miss" else ys[k], "lin")
    bx.hold(130).to(131, lx + 16, "hold")
    by.hold(130).to(131, ys[0], "hold")
    bx.loop(150, "lin")
    by.loop(150, "lin")
    bo = Track(100, 0).hold(109)
    bo.k[-1][2] = "hold"
    bo.k.append([110, 0, None])
    bo.k[-1][2] = "hold"
    bo.k.append([131, 100, None])
    bo.hold(150)
    c.layer("ball", [geo.shape(ball, nm="ball")], parent=root, p=Split(bx, by), a=(0, 0), o=bo)
    # paddles: follow the ball with a lag, the left one snaps on every hit
    for nm, px, side in (("padL", lx, "L"), ("padR", rx, "R")):
        py = Track(ys[0] if side == "L" else ys[1], 0)
        for k, (t, sd) in enumerate(hits):
            if sd == side and t > 0:
                py.to(t - 4, ys[k], "o")
            elif sd == side:
                pass
        if side == "R":
            py.hold(120).to(134, ys[1], "io")
        py.loop(150)
        c.layer(nm, [geo.shape(geo.rrect(px - 10, -32, px + 10, 32, 8), nm=nm)], parent=root, p=Split(px, py), a=(px, 0))
    # miss: the screen fills with the logo for 14f (game over), then the rally restarts
    logo = brand_word("XTC", cx, cy - 6, 46, 200, bold=9)
    lo = Track(0, 0).hold(111)
    lo.k[-1][2] = "hold"
    lo.k.append([112, 100, None])
    lo.k[-1][2] = "hold"
    lo.k.append([128, 0, None])
    lo.hold(150)
    ls = Track([100, 100], 0).hold(112).to(116, [108, 108], "snap").to(124, [100, 100], "io").loop(150)
    c.layer("over", [geo.shape(logo, nm="logo")], parent=root, p=(cx, cy - 6), a=(cx, cy - 6), s=ls, o=lo)
    jx = Track(cx, 0).hold(112)
    for k in range(6):
        jx.to(114 + k * 2, cx + (4 if k % 2 == 0 else -4), "aelin")
    jx.to(128, cx, "io").loop(150)
    root.p = Split(jx, cy + 112)
    M.twinkle(c, "tw", 340, cy - 70, 26, 116, 18, parent=root)
