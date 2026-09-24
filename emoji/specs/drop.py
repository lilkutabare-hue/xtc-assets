"""DROP series: brand objects doing their signature move."""
from xtc import geo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji

F_BRAND = ("Michroma-Regular.ttf", {})


def brand_font():
    return geo.font(F_BRAND[0], **F_BRAND[1])


def brand_x(x, y, w, h, bold=9):
    """the logo X (Michroma bold, stretched like the longsleeve print)."""
    return geo.text("X", brand_font(), x, y, h, bold=bold, width=w)


def pill_faces(cx, cy, R):
    lip, groove = 34, 20
    shell = geo.disc(cx, cy, R, 24)
    field_r = R - lip - groove
    ring_hole = geo.ring(cx, cy, R - lip, field_r)
    x = brand_x(cx, cy, field_r * 1.66, field_r * 0.8, bold=13)
    front = shell.difference(ring_hole).difference(x)
    score = geo.rrect(cx - field_r * 0.86, cy - 15, cx + field_r * 0.86, cy + 15, 15)
    back = shell.difference(ring_hole).difference(score)
    back = back.difference(geo.disc(cx - field_r * 0.45, cy - field_r * 0.45, 17)).difference(
        geo.disc(cx + field_r * 0.45, cy + field_r * 0.45, 17))
    return front, back


@emoji("01-pill-x", "💊", "таблетка, колёса, xtc, дроп, монета", "pill, xtc, drop, coin, spin",
       "таблетка-монета приседает, взлетает и делает тяжёлый двойной оборот с торцом, приземляется с отскоком и ловит ✦-блик",
       op=150, series="drop")
def pill(c):
    cx, cy, R = 256, 278, 184
    front, back = pill_faces(cx, cy, R)
    # hop: body null (pivot at the bottom of the coin) carries height + squash/stretch
    gy = cy + R
    y = Track(gy, 0).hold(32).to(54, gy - 58, "o").to(66, gy - 62, "io").to(86, gy, "i5")
    y.to(94, gy - 14, "o").to(102, gy, "i").loop(150)
    s = Track([100, 100], 0).hold(20)
    s.to(32, [108, 91], "io")                    # anticipation squash
    s.to(40, [95, 105], "o")                     # launch stretch
    s.to(56, [100, 100], "io").hold(80)
    s.to(86, [99, 101], "i").to(89, [109, 90], "o")   # land
    M.settle(s, 97, [100, 100], [-4, 4], n=2, per=10)
    s.loop(150)
    body = c.null("body", p=Split(cx, y), a=(cx, gy), s=s)
    segs = [(20, 32, 0, -28, "io"), (34, 100, -28, 732, (0.25, 0.0, 0.12, 1.0)), (100, 116, 732, 720, "io")]
    root, th, fr, bk = M.spin3d(c, "pill", front, back, cx, cy, segs, thick=44, lip=34, parent=body)
    # latex glare sweeps the face once it lands face-on, ✦ pops off the rim on the same beat
    M.glare_sweep(c, fr, cx, cy, 100, 34, parent=root,
                  sparks=[(cx + 56, cy - 90, 44, 114, 30)])


def tile_glyph(ch, x, y, w, h, fw=0.78, fh=0.6, bold=10):
    """a character as a hole shape filling the tile (stretched taller than the extended face: at 24px
    height is what reads)."""
    if ch in (None, " "):
        return None
    g = geo.text(ch, brand_font(), x, y, h * 0.5, bold=bold)
    bx0, by0, bx1, by1 = g.bounds
    aspect = (bx1 - bx0) / (by1 - by0)
    ww = min(w * fw, h * fh * aspect * 1.25) if aspect < 0.6 else w * fw     # narrow glyphs (1, !) keep shape
    g = geo.fit_box(g, x - ww / 2, y - h * fh / 2, x + ww / 2, y + h * fh / 2, keep=False)
    if ch == "C":   # Michroma's C nearly closes when bolded: re-open the aperture
        g = geo.U(g, geo.rect(x + ww * 0.05, y - h * fh * 0.13, x + ww / 2, y + h * fh * 0.13))
    return g


def board_push(tr, t, base=(100, 100)):
    """M7: the board answers every flip with a 102/97 push ~6f later."""
    tr.hold(t + 4).to(t + 8, [base[0] * 1.02, base[1] * 0.97], "io").to(t + 14, list(base), "io")
    return tr


def speed_lines(c, nm, cx, cy, r0, r1, t0, n=8, w=22, parent=None, skip=()):
    """M8 impact lines: radial strokes drawn by trim (end leads, start follows 2f later)."""
    import math as m
    for k in range(n):
        if k in skip:
            continue
        a = m.radians(-90 + 360 * k / n + 22.5)
        p0 = (cx + r0 * m.cos(a), cy + r0 * m.sin(a))
        p1 = (cx + r1 * m.cos(a), cy + r1 * m.sin(a))
        e = Track(0, 0).hold(t0).to(t0 + 7, 100, "o").hold(c.op)
        s = Track(0, 0).hold(t0 + 2).to(t0 + 9, 100, "i").hold(c.op)
        c.layer(f"{nm}{k}", [geo.stroked([p0, p1], w, e=e, s=s)], parent=parent, p=(0, 0), a=(0, 0), ip=t0, op=t0 + 10)


@emoji("47-flipclock", "⏳", "ждём, скоро, таймер, дроп, отсчёт", "waiting, soon, countdown, timer, drop",
       "таймер дропа щёлкает 03 → 02 → 01 → 00, на нулях табло бьёт вспышкой и дрожит, потом взводится обратно",
       op=180, series="drop")
def flipclock(c):
    w, h, gap = 200, 292, 26
    xs = (256 - w / 2 - gap / 2, 256 + w / 2 + gap / 2)
    y = 262
    flips = [20, 50, 80, 150]
    bs = Track([100, 100], 0)
    for t in flips[:2]:
        board_push(bs, t)
    bs.hold(88).to(92, [108, 93], "snap").to(93, [108, 93], "lin").to(100, [97, 104], "io").to(108, [102, 98], "io").to(116, [100, 100], "io")
    board_push(bs, 150)
    board = c.null("board", p=(256, y + h / 2), a=(256, y + h / 2), s=bs.loop(180))
    M.flip_tile(c, "d1", board, xs[0], y, w, h, [tile_glyph("0", xs[0], y, w, h)], [])
    M.flip_tile(c, "d2", board, xs[1], y, w, h, [tile_glyph(ch, xs[1], y, w, h) for ch in "3210"], flips, dur=12)
    for k, (x0, y0, x1, y1) in enumerate([(52, 100, 30, 76), (460, 100, 482, 76), (52, 430, 30, 454), (460, 430, 482, 454)]):
        e = Track(0, 0).hold(92).to(99, 100, "o").hold(180)
        s = Track(0, 0).hold(94).to(102, 100, "i").hold(180)
        c.layer(f"hit{k}", [geo.stroked([(x0, y0), (x1, y1)], 24, e=e, s=s)], p=(0, 0), a=(0, 0), ip=92, op=103)
    for k, (x, yy, t0) in enumerate(((66, 96, 96), (452, 120, 102), (70, 440, 108))):
        M.twinkle(c, f"tw{k}", x, yy, 34, t0, 20)


def board_row(c, nm, parent, words, times, cy, w, h, gap=16, dur=12, stagger=5, x0=None):
    """a row of split-flap tiles flipping through `words` (equal length strings; ' ' = blank, '*' = ✦).
    The flip runs as a wave left -> right (stagger frames per tile)."""
    n = len(words[0])
    total = n * w + (n - 1) * gap
    x0 = x0 if x0 is not None else 256 - total / 2 + w / 2
    for j in range(n):
        x = x0 + j * (w + gap)
        gl = []
        for word in words:
            ch = word[j]
            if ch == "*":
                gl.append(geo.spark(x, cy, min(w, h) * 0.4, 0.44))
            else:
                gl.append(tile_glyph(ch, x, cy, w, h))
        M.flip_tile(c, f"{nm}{j}", parent, x, cy, w, h, gl, [t + j * stagger for t in times], dur=dur)


@emoji("48-board-payme", "💸", "плати, оплата, скинь денег, pay me, xtc", "pay me, pay, money, xtc, send money",
       "закреп-табло XTC перещёлкивается волной в PAY, потом в ME ✦ — каждая буква толкает табло",
       op=180, series="drop")
def payme(c):
    w, h, cy = 142, 214, 262
    times = [24, 84, 144]
    bs = Track([100, 100], 0)
    for t in times:
        board_push(bs, t + 10)
    board = c.null("board", p=(256, cy + h / 2), a=(256, cy + h / 2), s=bs.loop(180))
    board_row(c, "t", board, ["XTC", "PAY", "ME "], times, cy, w, h, gap=16)


@emoji("49-board-dropnow", "🚀", "дроп, сейчас, старт, погнали, drop now", "drop now, launch, go, live, drop",
       "табло DROP перещёлкивается в NOW!, дрожит от нагрузки и рвётся вверх с растяжкой, приземляется с отскоком",
       op=180, series="drop")
def dropnow(c):
    w, h, gap = 188, 176, 18
    rows = [(160, ["DR", "NO"]), (160 + h + gap, ["OP", "W!"])]
    times = [30, 138]
    ys = Track(456, 0).hold(66)
    # strain (M13 jitter) -> launch with stretch (M25) -> land, squash, settle
    jit = Track(256, 0).hold(62)
    for k in range(10):
        jit.to(64 + k * 2, 256 + (4 if k % 2 == 0 else -4), "aelin")
    jit.to(86, 256, "io").loop(180)
    ys.hold(84).to(96, 432, "decel").to(106, 456, "slam").to(114, 446, "o").to(122, 456, "i").loop(180)
    ss = Track([100, 100], 0)
    board_push(ss, 36)
    ss.hold(78).to(84, [105, 93], "io").to(92, [94, 108], "snap").to(104, [100, 100], "io")
    ss.to(106, [110, 90], "slam").to(107, [110, 90], "lin").to(114, [97, 104], "io").to(122, [100, 100], "io")
    board_push(ss, 146)
    board = c.null("board", p=Split(jit, ys), a=(256, 456), s=ss.loop(180))
    for r, (cy, words) in enumerate(rows):
        board_row(c, f"r{r}", board, words, [t + r * 8 for t in times], cy, w, h, gap=gap)


def brand_letter(ch, x, y, lh, lw, bold):
    """a logo letter; C gets its aperture re-opened after bolding (Michroma closes it)."""
    g = geo.text(ch, brand_font(), x, y, lh, bold=bold, width=lw)
    if ch == "C":
        g = g.difference(geo.rect(x + lw * 0.06, y - lh * 0.17, x + lw * 0.6, y + lh * 0.17))
    return g


def brand_word(word, cx, cy, lh, total_w, bold=10, gap=0.2):
    """a word in the logo letters (per-letter so every C keeps its aperture)."""
    n = len(word)
    lw = total_w / (n + (n - 1) * gap)
    parts = []
    for i, ch in enumerate(word):
        x = cx - total_w / 2 + lw / 2 + i * lw * (1 + gap)
        if ch != " ":
            parts.append(brand_letter(ch, x, cy, lh, lw, bold))
    return geo.U(*parts)


def cross_letters(cx=256, cy=256, lh=84, lw=136, dx=158, dy=124, bold=14):
    """the XTC cross logo: X on top, X T C across, C below (T shared)."""
    L = {}
    for key, ch, x, y in (("xt", "X", cx, cy - dy), ("xl", "X", cx - dx, cy), ("t", "T", cx, cy),
                          ("cr", "C", cx + dx, cy), ("cb", "C", cx, cy + dy)):
        L[key] = (brand_letter(ch, x, y, lh, lw, bold), (x, y))
    return L


@emoji("44-cross-amen", "🙏", "аминь, благословляю, молюсь, спасибо, крест", "amen, bless, pray, thank you, cross",
       "буквы слетаются в крест-лого X·XTC·C, щелчок сборки, крест делает тяжёлый 360 с торцом и вспыхивает ✦ на концах",
       op=180, series="drop")
def cross(c):
    L = cross_letters()
    cx, cy = 256, 256
    # scattered start (and end) poses: pushed out along their arm, small, rotated
    off = {"xt": (0, -30, -40), "xl": (-26, 0, 35), "t": (0, 0, 0), "cr": (26, 0, -30), "cb": (0, 30, 45)}
    vis = Track(100, 0)
    vis.k[-1][2] = "hold"
    vis.k.append([30, 0, None])
    vis.k[-1][2] = "hold"
    vis.k.append([150, 100, None])
    vis.to(180, 100, "lin")
    for k, (key, (g, (x, y))) in enumerate(L.items()):
        dx_, dy_, rr = off[key]
        lag = k * 3
        p = Track([x + dx_, y + dy_], 0).hold(2 + lag).to(20 + lag, [x, y], "back").hold(150 + (4 - k) * 3).to(172, [x + dx_, y + dy_], "i")
        s0 = [52, 52] if key != "t" else [100, 100]
        s = Track(s0, 0).hold(2 + lag).to(20 + lag, [100, 100], "back").hold(150 + (4 - k) * 3).to(172, s0, "i")
        r = Track(rr, 0).hold(2 + lag).to(20 + lag, 0, "back").hold(150 + (4 - k) * 3).to(172, rr, "i")
        c.layer(f"L{key}", [geo.shape(g, nm=key)], p=p.loop(180), a=(x, y), s=s.loop(180), r=r.loop(180), o=vis)
    # click of assembly: squash of the whole logo drawn by a body null (applies to the spin layers)
    bs = Track([100, 100], 0).hold(30).to(33, [106, 95], "snap").to(40, [98, 102], "io").to(46, [100, 100], "io").loop(180)
    body = c.null("body", p=(cx, cy), a=(cx, cy), s=bs)
    front = geo.U(*[g for g, _ in L.values()])
    segs = [(40, 52, 0, -24, "io"), (52, 120, -24, 378, (0.3, 0.0, 0.14, 1.0)), (120, 134, 378, 360, "io")]
    n0 = len(c.layers)
    root, th, fr, bk = M.spin3d(c, "cross", front, front, cx, cy, segs, thick=26, lip=14, parent=body, band_h=300)
    for l in c.layers[n0:]:
        l.ip, l.op = 30, 150
    for k, (x, y) in enumerate(((cx + 112, cy - 104), (cx - 112, cy + 104), (cx - 116, cy - 100), (cx + 116, cy + 100))):
        M.twinkle(c, f"tw{k}", x, y, 40, 124 + k * 5, 24)


@emoji("46-eyelets-wow", "😮", "вау, ого, офигеть, люверсы, о", "wow, whoa, oh, eyelets, surprised",
       "три люверса по очереди защёлкиваются прессом (удар, волна-кольцо, ✦) и складываются в o o / O — рот-люверс ахает",
       op=150, series="drop")
def eyelets(c):
    items = [("eL", 150, 166, 76, 12), ("eR", 362, 166, 76, 22), ("m", 256, 340, 102, 36)]
    for nm, x, y, r, t in items:
        g = geo.ring(x, y, r, r * 0.5, 24)
        s = Track([100, 100], 0).hold(t).to(t + 3, [118, 80], "slam").to(t + 4, [118, 80], "lin").to(t + 11, [92, 108], "o")
        s.to(t + 18, [103, 97], "io").to(t + 25, [100, 100], "io")
        if nm == "m":
            s.hold(56).to(86, [124, 124], "is").to(92, [132, 118], "io").to(104, [96, 104], "io").to(114, [102, 98], "io").to(122, [100, 100], "io")
        else:
            tb = 76 if nm == "eL" else 80
            s.hold(tb).to(tb + 4, [110, 10], "i").to(tb + 11, [100, 100], "o")
        c.layer(nm, [geo.shape(g, nm=nm)], p=(x, y), a=(x, y), s=s.loop(150))
        # shock ring of the press (M20: stroke width thins while it expands)
        rs = Track([100, 100], 0).hold(t).to(t + 12, [138 if nm != "m" else 128] * 2, "ring").hold(150)
        rw = Track(22, 0).hold(t).to(t + 12, 4, "ring").to(t + 16, 0, "i").hold(150)
        from specs.faces import lot_ring
        c.layer(f"{nm}-ring", [lot_ring(x, y, r + 8, rw)], p=(x, y), a=(x, y), s=rs, ip=t, op=t + 17)
    M.twinkle(c, "tw1", 150 + 54, 166 - 54, 30, 18, 18)
    M.twinkle(c, "tw2", 362 + 54, 166 - 54, 30, 28, 18)
    M.twinkle(c, "tw3", 256 + 74, 340 - 74, 38, 42, 22)


def longsleeve(cx=256, top=128):
    """XTC longsleeve silhouette on a hanger (logo as holes)."""
    y = top
    pts = [(cx - 50, y), (cx - 116, y + 18), (cx - 170, y + 70), (cx - 198, y + 276), (cx - 156, y + 288),
           (cx - 130, y + 116), (cx - 122, y + 330), (cx + 122, y + 330), (cx + 130, y + 116), (cx + 156, y + 288),
           (cx + 198, y + 276), (cx + 170, y + 70), (cx + 116, y + 18), (cx + 50, y), (cx, y + 26)]
    tee = geo.poly(pts).buffer(12).buffer(-6)
    logo = brand_word("XTC", cx, y + 112, 42, 180, bold=9)
    tee = tee.difference(logo)
    hook = geo.brush(geo.arc(cx + 16, y - 52, 28, 180, 450, 20)[::-1] + [(cx, y - 6)], 22, taper=(0.9, 1.0), smooth=False)
    return geo.U(tee, hook), (cx, y - 70)


@emoji("50-soldout-tee", "🔥", "sold out, раскупили, нет в наличии, дроп, горит", "sold out, gone, hot drop, xtc, fire",
       "лонгслив XTC покачивается на вешалке — сверху бьёт штамп SOLD OUT, вещь дёргается, из-под штампа пыхает дым",
       op=180, series="drop")
def soldout(c):
    tee, hook = longsleeve(256, 132)
    import math as m
    r = Track(0, 0).to(20, 2, "io").to(44, -1.5, "io").to(52, 0, "io").to(56, 4.5, "snap")
    M.settle(r, 60, 0, -3, n=3, per=16, decay=0.5, hit="io")
    r.to(150, 1.5, "io").to(180, 0, "io")
    tl = c.layer("tee", [geo.shape(tee, nm="tee")], p=hook, a=hook, r=r)
    # the stamp: plate with letter + border-line holes; the same holes cut the tee through the matte
    sx, sy = 256, 300
    f = brand_font()
    letters = geo.U(geo.text("SOLD", f, sx, sy - 38, 54, bold=9, width=236), geo.text("OUT", f, sx, sy + 40, 54, bold=9, width=180))
    plate = geo.rrect(sx - 162, sy - 102, sx + 162, sy + 102, 30)
    border = plate.buffer(-16).difference(plate.buffer(-30))
    cut = geo.U(letters, border)
    stamp_s = Track([118, 118], 0).hold(44).to(52, [100, 100], "slam").to(53, [96, 104], "lin").to(60, [102, 98], "io").to(66, [100, 100], "io")
    stamp_s.hold(152).to(166, [114, 114], "i").to(180, [118, 118], "lin")
    stamp_r = Track(-24, 0).hold(44).to(52, -12, "slam").hold(152).to(166, -20, "i").to(180, -24, "lin")
    so = Track(0, 0).hold(44).to(46, 100, "lin").hold(156).to(164, 0, "lin").loop(180, "lin")
    stamp = c.null("stamp", parent=tl, p=(sx, sy), a=(sx, sy), s=stamp_s, r=stamp_r)
    mt = c.matte(tl, "stampcut", [geo.shape(cut, nm="cut")], parent=stamp, p=(sx, sy), a=(sx, sy))
    # the matte cuts only once the stamp has landed
    mt.o = Track(0, 0).hold(44).to(46, 100, "lin").hold(160).to(162, 0, "lin").loop(180, "lin")
    c.layer("plate", [geo.shape(plate.difference(cut), nm="plate")], parent=stamp, p=(sx, sy), a=(sx, sy), o=so)
    # smoke puffs from under the plate corners on impact
    for k, (x0, y0, d) in enumerate(((sx - 150, sy + 90, -1), (sx + 150, sy + 60, 1), (sx - 140, sy - 80, -1))):
        M.particle(c, f"smoke{k}", K_steam(x0, y0, 70, -d), 53 + k * 2, 30, (x0, y0), (x0 + d * 26, y0 - 50), None,
                   anchor=(x0, y0), pop=0.15, fade=0.5, fall="decel")
    for k, (p0, p1) in enumerate((((60, 150), (34, 124)), ((452, 150), (478, 124)), ((60, 440), (34, 466)), ((452, 440), (478, 466)))):
        ee = Track(0, 0).hold(52).to(59, 100, "o").hold(180)
        s0 = Track(0, 0).hold(54).to(62, 100, "i").hold(180)
        c.layer(f"hit{k}", [geo.stroked([p0, p1], 22, e=ee, s=s0)], p=(0, 0), a=(0, 0), ip=52, op=63)


def K_steam(x, y, s, d):
    from xtc import kao
    return kao.steam(x, y, s, d=d)


@emoji("51-latex-heart", "🖤", "латекс, чёрное сердце, люблю, глянец, xtc", "latex, black heart, love, gloss, xtc",
       "глянцевое сердце медленно вдыхает, на пике по латексу бегут два блика, резиновый отскок, ✦ на кромке",
       op=150, series="drop")
def latex_heart(c):
    cx, cy = 256, 262
    g = geo.heart(cx, cy, 440)
    # static gloss: crescent highlight in the upper-left lobe (a hole)
    hi = geo.ellipse(cx - 104, cy - 96, 58, 30).difference(geo.ellipse(cx - 94, cy - 80, 58, 30))
    hi = geo.rot(hi, -35, (cx - 104, cy - 96))
    g = g.difference(hi)
    s = Track([100, 100], 0).hold(10).to(56, [106, 106], "is").to(62, [103, 109], "io").to(70, [108, 101], "io")
    s.to(78, [100, 104], "io").to(88, [102, 100], "io").to(98, [99.5, 100.5], "io").to(108, [100, 100], "io").loop(150)
    heart = c.layer("heart", [geo.shape(g, nm="heart")], p=(cx, cy + 180), a=(cx, cy + 180), s=s)
    M.glare_sweep(c, heart, cx, cy - 10, 50, 30, travel=300, sparks=[(cx + 120, cy - 118, 42, 70, 30)])


@emoji("53-bag-xtc", "👜", "сумка, шоппинг, xtc, покупка, мерч", "bag, shopping, xtc, merch, purchase",
       "сумка XTC висит на пальце за ручку: раскачивается маятником, закручивается на 410° и раскручивается обратно с затуханием, ✦",
       op=150, series="drop")
def bag(c):
    cx, cy = 256, 296
    body = geo.poly([(cx - 140, cy - 110), (cx + 140, cy - 110), (cx + 168, cy + 140), (cx - 168, cy + 140)]).buffer(28).buffer(-8)
    handle = geo.brush(geo.arc(cx, cy - 132, 90, 180, 360, 24), 36, taper=(1, 1), smooth=False)
    zipper = geo.rrect(cx - 132, cy - 104, cx + 132, cy - 90, 7)
    tab = geo.rrect(cx + 108, cy - 94, cx + 136, cy - 40, 10).difference(geo.rrect(cx + 116, cy - 70, cx + 128, cy - 50, 5))
    logo = brand_word("XTC", cx, cy + 34, 64, 230, bold=10)
    front = geo.U(body.difference(zipper).difference(logo), handle).difference(tab.buffer(6)).union(tab)
    back = geo.U(body.difference(zipper), handle)
    # hangs from a finger at the top of the handle: swings like a pendulum while it twists and unwinds
    top = (cx, cy - 132 - 90 - 10)
    r = Track(0, 0).hold(12).to(22, -4.5, "io").to(40, 4, "io").to(58, -2.5, "io").to(74, 1.5, "io").to(90, -0.6, "io").to(104, 0, "io").loop(150)
    s = Track([100, 100], 0).hold(8).to(14, [102, 98], "io").to(22, [98, 103], "io").to(30, [100, 100], "io").hold(118).to(122, [101, 99], "io").to(130, [100, 100], "io").loop(150)
    root = c.null("root", p=top, a=top, r=r, s=s)
    segs = [(14, 62, 0, 410, (0.4, 0.0, 0.2, 1.0)), (62, 80, 410, 330, "io"), (80, 96, 330, 385, "io"),
            (96, 110, 385, 350, "io"), (110, 122, 350, 360, "io")]
    M.spin3d(c, "bag", front, back, cx, cy, segs, thick=64, lip=26, parent=root)
    M.twinkle(c, "tw", cx - 120, cy - 100, 40, 118, 26, parent=root)
