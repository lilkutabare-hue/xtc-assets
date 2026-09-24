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
