"""Text badges on the split-flap board (the channel pin's mechanics), logo letters (Michroma bold)."""
from xtc import geo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.drop import board_push, board_row

W3, H3 = 146, 214
W2, H2 = 204, 270


def hop(tr, t, h=34, base=None):
    """a tile jump: up (decel), down (slam), land squash."""
    b = base if base is not None else tr.v
    tr.hold(t).to(t + 8, b - h, "decel").to(t + 16, b, "slam").to(t + 22, b - h * 0.18, "o").to(t + 28, b, "i")
    return tr


@emoji("94-lol", "😆", "лол, ахах, ржу, смешно, lol", "lol, haha, lmao, funny, laughing",
       "табло LOL: буква O подпрыгивает от смеха, плитки перещёлкиваются в HA! и обратно",
       op=180, series="badge")
def lol(c):
    cy = 262
    y = Track(cy + H3 / 2, 0)
    for t in (12, 36):
        hop(y, t, 20)
    y.loop(180)
    board = c.null("board", p=Split(256, y), a=(256, cy + H3 / 2),
                   s=board_push(board_push(Track([100, 100], 0), 72), 150).loop(180))
    board_row(c, "t", board, ["LOL", "HA!"], [70, 142], cy, W3, H3, gap=14)
    # the O jumps on its own (laugh), twice, on top of the board hop
    # (implemented as a second board null for the middle tile would double layers; instead the whole board hops)


@emoji("95-omg", "😲", "омг, боже, офигеть, omg, капец", "omg, oh my god, wow, shocked, no way",
       "OMG бьёт по табло: плитки откидываются назад от шока (растяжка), перещёлкиваются в !!! и возвращаются",
       op=180, series="badge")
def omg(c):
    cy = 262
    s = Track([100, 100], 0).hold(14).to(24, [106, 92], "io").to(30, [92, 112], "snap")
    for k in range(8):
        s.to(32 + k * 2, [92 + (1 if k % 2 == 0 else -1), 112 - (1 if k % 2 == 0 else -1)], "aelin")
    s.to(58, [102, 98], "io").to(66, [100, 100], "io")
    board_push(s, 150)
    board = c.null("board", p=(256, cy + H3 / 2), a=(256, cy + H3 / 2), s=s.loop(180))
    board_row(c, "t", board, ["OMG", "!!!"], [84, 146], cy, W3, H3, gap=14, stagger=3)


@emoji("96-wtf", "🤨", "втф, чё, что за, wtf, прикол", "wtf, what, huh, what the, seriously",
       "табло сбоит: плитки глитчем перещёлкиваются через мусорные символы и встают WTF криво, потом выравниваются",
       op=180, series="badge")
def wtf(c):
    cy = 262
    r = Track(0, 0).hold(68).to(72, -5, "snap").to(80, -3.5, "io").hold(128).to(138, 1, "io").to(146, 0, "io").loop(180)
    board = c.null("board", p=(256, cy + 204 / 2), a=(256, cy + 204 / 2), r=r)
    words = ["WTF", "#?%", "W!$", "?T@", "WTF"]
    # glitch burst: flips every 8f, tiles out of sync (stagger 2), last one lands at 68
    times = [30, 40, 50, 60]
    n = 3
    total = n * 136 + (n - 1) * 14
    x0 = 256 - total / 2 + 136 / 2
    from specs.drop import tile_glyph
    for j in range(n):
        x = x0 + j * (136 + 14)
        gl = [tile_glyph(w[j], x, cy, 136, 204) for w in words[:-1]]
        M.flip_tile(c, f"t{j}", board, x, cy, 136, 204, gl, [t + j * 2 for t in times], dur=8, bounce=14)


@emoji("97-ok", "👌", "ок, окей, понял, принято, ok", "ok, okay, got it, fine, roger",
       "две плитки OK кивают всем табло, перещёлкиваются в +1 и обратно, ✦",
       op=150, series="badge")
def ok(c):
    cy = 262
    # nod: board tips forward (squash down from the top edge) twice
    s = Track([100, 100], 0).hold(50)
    for t in (50, 66):
        s.to(t + 5, [102, 88], "io").to(t + 12, [99, 103], "io").to(t + 16, [100, 100], "io")
    s.loop(150)
    board = c.null("board", p=(256, cy - H2 / 2), a=(256, cy - H2 / 2), s=s)
    board_row(c, "t", board, ["OK", "+1"], [92, 124], cy, W2, H2, gap=18)
    M.twinkle(c, "tw", 256 + W2 - 16, cy - H2 / 2 + 6, 34, 84, 22)


@emoji("98-no", "🙅", "нет, не, неа, отказ, no", "no, nope, nah, no way, denied",
       "плитки NO мотают «нет» всем табло — влево-вправо с затуханием, на последнем мотке O подскакивает",
       op=150, series="badge")
def no(c):
    cy = 262
    r = Track(0, 0).hold(20).to(26, -5, "io")
    for k, a in enumerate((5, -4, 3, -2)):
        r.to(32 + k * 8, a, "io")
    r.to(70, 0, "io").loop(150)
    x = Track(256, 0).hold(20).to(26, 246, "io")
    for k, a in enumerate((266, 248, 262, 252)):
        x.to(32 + k * 8, a, "io")
    x.to(70, 256, "io").loop(150)
    board = c.null("board", p=Split(x, cy + H2 / 2), a=(256, cy + H2 / 2), r=r)
    board_row(c, "t", board, ["NO", "NO"], [96, 124], cy, W2, H2, gap=18)


@emoji("99-yes", "✅", "да, ага, конечно, yes, согласен", "yes, yep, sure, agreed, yeah",
       "YES: плитки подпрыгивают волной по очереди, S приземляется последней с ударом",
       op=150, series="badge")
def yes(c):
    cy = 268
    n, gap = 3, 14
    total = n * W3 + (n - 1) * gap
    x0 = 256 - total / 2 + W3 / 2
    from specs.drop import tile_glyph
    for j in range(n):
        x = x0 + j * (W3 + gap)
        y = Track(cy + H3 / 2, 0)
        hop(y, 20 + j * 7, 44 if j < 2 else 60)
        y.loop(150)
        s = Track([100, 100], 0).hold(20 + j * 7).to(26 + j * 7, [94, 108], "o").to(36 + j * 7, [100, 100], "io")
        s.to(38 + j * 7, [108, 92], "slam").to(44 + j * 7, [98, 102], "io").to(50 + j * 7, [100, 100], "io").loop(150)
        tn = c.null(f"tile{j}", p=Split(x, y), a=(x, cy + H3 / 2), s=s)
        M.flip_tile(c, f"t{j}", tn, x, cy, W3, H3, [tile_glyph(ch, x, cy, W3, H3) for ch in ("YES"[j], "YEP"[j])],
                    [96 + j * 4, 124 + j * 4], dur=10)


# ---------------------------------------------------------------- P1 badges


@emoji("115-gm", "☀️", "доброе утро, гм, проснулся, утро, gm", "gm, good morning, morning, wake up, rise",
       "табло «просыпается»: плитки открываются по одной из пустых в GM, табло потягивается вверх, за ним восходит ✦-солнце",
       op=150, series="p1")
def gm(c):
    cy = 300
    s = Track([100, 100], 0).hold(40).to(52, [96, 110], "io").to(60, [103, 97], "io").to(70, [100, 100], "io").loop(150)
    board = c.null("board", p=(256, cy + H2 / 2), a=(256, cy + H2 / 2), s=s)
    board_row(c, "t", board, ["  ", "GM"], [10, 112], cy, W2, H2, gap=18, stagger=8)
    # the sun: a big ✦ rising from behind the board top edge, spinning slowly
    sy = Track(cy - 40, 0).hold(34).to(66, 92, "o").hold(120).to(140, cy - 40, "i").loop(150)
    ss = Track([40, 40], 0).hold(34).to(66, [100, 100], "o").hold(120).to(140, [40, 40], "i").loop(150)
    sr = Track(0, 0).hold(34).to(140, 90, "io")
    sr.k[-1][2] = "hold"
    sr.k.append([149.9, 0, None])
    c.layer("sun", [geo.shape(geo.spark(256, cy - 40, 74, 0.34), nm="sun")], p=Split(256, sy), a=(256, cy - 40), s=ss, r=sr)


@emoji("116-gn", "🌙", "спокойной ночи, гн, сплю, ночь, gn", "gn, good night, night, sleep, bye",
       "табло GN сонно кренится, плитки по одной гаснут (перещёлкиваются в пустые), над ним поднимаются Z и плитки снова загораются",
       op=180, series="p1")
def gn(c):
    cy = 300
    r = Track(0, 0).hold(20).to(60, -5, "io").to(96, 4, "io").to(132, -3, "io").to(160, 0, "io").loop(180)
    board = c.null("board", p=(256, cy + H2 / 2), a=(256, cy + H2 / 2), r=r)
    board_row(c, "t", board, ["GN", "  "], [60, 140], cy, W2, H2, gap=18, stagger=10)
    from specs.drop import brand_font
    for k in range(3):
        t0 = 72 + k * 14
        z = geo.text("Z", brand_font(), 380, 120, 50 + k * 8, bold=7, width=62 + k * 10)
        M.particle(c, f"z{k}", z, t0, 48, (360, 150), (420, 84 - k * 4), None, anchor=(380, 120), rot=(-10, 12),
                   pop=0.2, fade=0.35, fall="decel", xease=(0.4, 0.0, 0.2, 1.0))


@emoji("117-xoxo", "💋", "обнимаю целую, xoxo, чмоки, люблю, крестики-нолики", "xoxo, hugs and kisses, love, kisses, tic tac toe",
       "поле 2×2 заполняется как крестики-нолики: X, O, X, O щёлкают по очереди — и вся доска делает «чмок» (сжатие + ✦)",
       op=180, series="p1")
def xoxo(c):
    w, h, gap = 188, 176, 18
    rows = [(160, ["  ", "XO"]), (160 + h + gap, ["  ", "XO"])]
    # tic-tac-toe order: X (0,0) -> O (1,1) -> X (1,0) -> O (0,1)
    s = Track([100, 100], 0).hold(90).to(96, [90, 90], "io").to(102, [108, 108], "snap").to(112, [98, 98], "io").to(120, [100, 100], "io").loop(180)
    board = c.null("board", p=(256, 262), a=(256, 262), s=s)
    from specs.drop import tile_glyph
    order = {(0, 0): 12, (1, 1): 30, (1, 0): 48, (0, 1): 66}
    for r_, (cy, words) in enumerate(rows):
        x0 = 256 - (2 * w + gap) / 2 + w / 2
        for j in range(2):
            x = x0 + j * (w + gap)
            ch = "X" if (r_ + j) % 2 == 0 else "O"
            t_on = order[(j, r_)]
            M.flip_tile(c, f"t{r_}{j}", board, x, cy, w, h, [None, tile_glyph(ch, x, cy, w, h)], [t_on, 150 + (r_ * 2 + j) * 4], dur=10)
    M.twinkle(c, "tw", 452, 70, 36, 100, 24)
    M.twinkle(c, "tw2", 64, 450, 28, 106, 20)


@emoji("118-soon", "🔜", "скоро, ждите, soon, анонс, на подходе", "soon, coming soon, stay tuned, teaser, wait",
       "SO/ON: по плиткам бежит «загрузка» — каждая по очереди перещёлкивается в ✦ и обратно, круг за кругом",
       op=180, series="p1")
def soon(c):
    w, h, gap = 206, 192, 16
    board = c.null("board", p=(256, 262), a=(256, 262))
    from specs.drop import tile_glyph
    letters = [["S", "O"], ["O", "N"]]
    ring = [(0, 0), (0, 1), (1, 1), (1, 0)]      # clockwise
    for k, (r_, j) in enumerate(ring):
        cy = 150 + r_ * (h + gap)
        x = 256 - (2 * w + gap) / 2 + w / 2 + j * (w + gap)
        t1 = 16 + k * 14
        g = [tile_glyph(letters[r_][j], x, cy, w, h), geo.spark(x, cy, min(w, h) * 0.36, 0.42)]
        M.flip_tile(c, f"t{k}", board, x, cy, w, h, g + [g[0].buffer(0), g[1].buffer(0)],
                    [t1, t1 + 14, t1 + 70, t1 + 84], dur=8, bounce=8)


@emoji("119-sold-out", "🚫", "sold out, раскуплено, всё, нет в наличии, распродано", "sold out, gone, out of stock, no more, drop",
       "табло DROP с грохотом перещёлкивается в SOLD / OUT, проседает от удара, из-под плиток пыль, в конце взводится обратно",
       op=180, series="p1")
def sold_out(c):
    W, H, gap = 112, 176, 10
    y = Track(256, 0).hold(52).to(58, 270, "slam").to(66, 250, "o").to(74, 256, "io").loop(180)
    s = Track([100, 100], 0).hold(52).to(58, [103, 92], "slam").to(59, [103, 92], "lin").to(66, [99, 102], "io").to(74, [100, 100], "io").loop(180)
    board = c.null("board", p=Split(256, y), a=(256, 256), s=s)
    board_row(c, "a", board, ["DROP", "SOLD"], [40, 138], 256 - H / 2 - gap / 2, W, H, gap=gap, stagger=3)
    board_row(c, "b", board, [" XTC", " OUT"], [46, 144], 256 + H / 2 + gap / 2, W, H, gap=gap, stagger=3)
    for k, (x0, d) in enumerate(((60, -1), (452, 1), (130, -1), (382, 1))):
        M.particle(c, f"dust{k}", geo.disc(x0, 460, 20 + (k % 2) * 6), 58 + k, 24, (x0, 460), (x0 + d * 26, 480 - (k % 2) * 30), None,
                   pop=0.15, fade=0.5, fall="decel", anchor=(x0, 460))


@emoji("120-new", "🆕", "новинка, new, новое, свежак, дроп", "new, fresh, just dropped, latest, drop",
       "табло OLD перещёлкивается в NEW волной, плитки подпрыгивают с перелётом и ✦ «новенькое»",
       op=150, series="p1")
def new(c):
    cy = 262
    board = c.null("board", p=(256, cy), a=(256, cy))
    from specs.drop import tile_glyph
    n, gap = 3, 14
    total = n * 136 + (n - 1) * gap
    x0 = 256 - total / 2 + 136 / 2
    plates = []
    for j in range(n):
        x = x0 + j * (136 + gap)
        t0 = 100 + j * 4
        s = Track([100, 100], 0).hold(t0 - 6).to(t0, [94, 94], "io").hold(t0 + 20).to(t0 + 26, [108, 108], "snap").to(t0 + 32, [97, 97], "io").to(t0 + 38, [100, 100], "io").loop(150)
        tn = c.null(f"tn{j}", parent=board, p=(x, cy), a=(x, cy), s=s)
        M.flip_tile(c, f"t{j}", tn, x, cy, 136, 204, [tile_glyph("NEW"[j], x, cy, 136, 204), tile_glyph("OLD"[j], x, cy, 136, 204)],
                    [80 + j * 4, 100 + j * 4], dur=10)
    # one glare across the whole board: needs a single target -> a flat plate behind the tiles
    M.twinkle(c, "tw", 256 + total / 2 - 44, cy - 204 / 2 - 4, 40, 124, 22)
    M.twinkle(c, "tw2", 256 - total / 2 + 40, cy + 204 / 2 + 2, 28, 130, 18)


@emoji("121-xtc", "✖️", "xtc, икстиси, бренд, xtcpay, лого", "xtc, brand, logo, xtcpay, drop",
       "три плитки XTC по очереди делают полный оборот ребром (fake-3D волна), логотип встаёт на место с толчком табло",
       op=150, series="p1")
def xtc_badge(c):
    cy = 262
    board = c.null("board", p=(256, cy + H3 / 2), a=(256, cy + H3 / 2),
                   s=board_push(Track([100, 100], 0), 88).loop(150))
    from specs.drop import tile_glyph
    n, gap = 3, 14
    total = n * W3 + (n - 1) * gap
    x0 = 256 - total / 2 + W3 / 2
    for j in range(n):
        x = x0 + j * (W3 + gap)
        tile = geo.rrect(x - W3 / 2, cy - H3 / 2, x + W3 / 2, cy + H3 / 2, 22).difference(tile_glyph("XTC"[j], x, cy, W3, H3))
        t0 = 20 + j * 10
        segs = [(t0, t0 + 50, 0, 360, (0.4, 0.0, 0.15, 1.0))]
        M.spin3d(c, f"s{j}", tile, tile, x, cy, segs, thick=26, lip=16, parent=board)
