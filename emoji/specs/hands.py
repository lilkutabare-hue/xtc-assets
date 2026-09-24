"""P2 hands, drawn as bold capsule silhouettes (only the ones that read at 24px stay in the pack)."""
import math

from xtc import geo, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji

GAP = 12      # finger separation cut (hole line)


def cap(p0, p1, w):
    return geo.line([p0, p1], w, "round", "round")


def seps(g, lines, w=GAP):
    for a, b in lines:
        g = g.difference(geo.line([a, b], w, "round", "round"))
    return g


def fist(x, y, w=250, h=224):
    """fist from the thumb side: palm block + 4 rolled fingers bulging on the right, split by gap lines."""
    g = geo.rrect(x - w / 2, y - h / 2, x + w * 0.3, y + h / 2, 64)
    rolls = []
    for k in range(4):
        yy = y - h / 2 + h * (k + 0.5) / 4
        rolls.append(cap((x + w * 0.05, yy), (x + w / 2 - 26, yy), h / 4 + 6))
    g = geo.U(g, *rolls)
    for k in range(1, 4):
        yy = y - h / 2 + h * k / 4
        g = g.difference(geo.line([(x + w * 0.02, yy), (x + w / 2 + 20, yy)], GAP, "round", "round"))
    return g


def thumbs(x=256, y=300, up=True):
    f = fist(x + 30, y + 50)
    th = geo.rot(cap((x - 70, y - 20), (x - 70, y - 200), 104), -6, (x - 70, y - 20))
    g = geo.U(f, th)
    g = seps(g, [((x - 12, y - 50), (x - 12, y + 40))])
    if not up:
        g = geo.scale(g, 1, -1, (256, 256))
    return g


@emoji("126-thumbs-up", "👍", "лайк, класс, ок, одобряю, палец вверх", "like, thumbs up, nice, approve, ok",
       "кулак замахивается вниз и выщёлкивает большой палец вверх с перелётом, на кончике ✦, кулак пружинит",
       op=120, series="p2")
def thumbs_up(c):
    g = thumbs(256, 300)
    body = c.null("body", p=(290, 460), a=(290, 460),
                  s=Track([100, 100], 0).hold(10).to(20, [106, 92], "io").to(28, [94, 108], "snap").to(38, [102, 98], "io").to(46, [100, 100], "io").loop(120),
                  r=Track(0, 0).hold(10).to(20, 10, "io").to(28, -8, "snap").to(36, 3, "io").to(44, 0, "io").loop(120))
    c.layer("hand", [geo.shape(g, nm="hand")], parent=body, p=(256, 256), a=(256, 256))
    M.twinkle(c, "tw", 196, 70, 44, 30, 24)


@emoji("127-thumbs-down", "👎", "дизлайк, фу, плохо, не одобряю, палец вниз", "dislike, thumbs down, bad, nope, boo",
       "кулак тяжело опускает палец вниз: медленный наклон, удар вниз со сплющиванием, дрожь разочарования",
       op=120, series="p2")
def thumbs_down(c):
    g = thumbs(256, 290, up=False)
    body = c.null("body", p=(290, 70), a=(290, 70),
                  s=Track([100, 100], 0).hold(20).to(40, [104, 96], "is").to(46, [92, 110], "slam").to(56, [103, 98], "io").to(66, [100, 100], "io").loop(120),
                  r=Track(0, 0).hold(20).to(40, -8, "is").to(46, 6, "slam").to(56, -2, "io").to(66, 0, "io").loop(120))
    c.layer("hand", [geo.shape(g, nm="hand")], parent=body, p=(256, 256), a=(256, 256))


@emoji("128-victory", "✌️", "мир, пис, победа, два, peace", "peace, victory, v sign, two, chill",
       "ладонь выстреливает двумя пальцами в V, пальцы расходятся ножницами дважды, ✦ между ними",
       op=120, series="p2")
def victory(c):
    x, y = 256, 340
    palm = geo.rrect(x - 110, y - 70, x + 110, y + 130, 60)
    folded = [cap((x + 30, y - 60), (x + 30, y + 10), 64), cap((x + 86, y - 50), (x + 86, y + 10), 56)]
    thumb = cap((x - 100, y + 40), (x + 40, y - 10), 70)
    base = geo.U(palm, *folded)
    base = seps(base, [((x + 58, y - 70), (x + 58, y + 20))])
    base = geo.U(base, thumb)
    base = seps(base, [((x - 86, y + 6), (x + 54, y - 40))], 12)
    lay = c.layer("palm", [geo.shape(base, nm="palm")], p=(x, y), a=(x, y),
                  s=Track([100, 100], 0).hold(6).to(14, [104, 94], "io").to(22, [98, 104], "snap").to(30, [100, 100], "io").loop(120))
    for k, (dx, ang) in enumerate(((-60, -12), (-4, 12))):
        base_pt = (x + dx, y - 50)
        f = cap(base_pt, (x + dx, y - 260), 68)
        s = Track([100, 30], 0).hold(8).to(20, [100, 108], "snap").to(28, [100, 100], "io").loop(120)
        r = Track(0, 0).hold(14).to(24, ang, "snap")
        for t in (50, 70):
            r.to(t + 5, ang * 0.2, "io").to(t + 12, ang * 1.3, "snap").to(t + 18, ang, "io")
        r.to(110, 0, "io").loop(120)
        c.layer(f"f{k}", [geo.shape(f, nm="f")], parent=lay, p=base_pt, a=base_pt, s=s, r=r)
    M.twinkle(c, "tw", x - 32, y - 250, 36, 34, 24)


@emoji("129-rock", "🤘", "рок, металл, жара, круто, коза", "rock, metal, rock on, horns, hell yeah",
       "коза: кулак с рогами качает головой на бас — два жёстких удара вперёд, рога вибрируют",
       op=120, series="p2")
def rock(c):
    x, y = 256, 322
    fistg = geo.rrect(x - 120, y - 80, x + 120, y + 120, 60)
    fistg = seps(fistg, [((x - 30, y - 90), (x - 30, y + 10)), ((x + 30, y - 90), (x + 30, y + 10))])
    thumb = cap((x - 110, y + 60), (x + 50, y + 30), 64)
    g = geo.U(fistg, thumb)
    g = seps(g, [((x - 96, y + 24), (x + 64, y - 6))], 12)
    horns = geo.U(cap((x - 90, y - 60), (x - 132, y - 250), 66), cap((x + 90, y - 60), (x + 132, y - 250), 66))
    s = Track([100, 100], 0)
    r = Track(0, 0)
    y_ = Track(y, 0)
    for t in (10, 40):
        s.hold(t).to(t + 6, [96, 104], "io").to(t + 10, [110, 90], "slam").to(t + 16, [98, 102], "io").to(t + 24, [100, 100], "io")
        y_.hold(t).to(t + 6, y - 10, "io").to(t + 10, y + 16, "slam").to(t + 18, y, "io")
    body = c.null("body", p=Split(x, y_.loop(120)), a=(x, y), s=s.loop(120))
    c.layer("fist", [geo.shape(g, nm="fist")], parent=body, p=(x, y), a=(x, y))
    hr = Track(0, 0)
    for t in (10, 40):
        hr.hold(t + 10).to(t + 13, 4, "aelin").to(t + 16, -3, "aelin").to(t + 19, 2, "aelin").to(t + 22, 0, "io")
    c.layer("horns", [geo.shape(horns, nm="horns")], parent=body, p=(x, y - 60), a=(x, y - 60), r=hr.loop(120))


@emoji("130-wave", "👋", "привет, пока, хай, машу, здравствуй", "hi, hello, bye, wave, hey",
       "раскрытая ладонь машет от запястья: три взмаха с запаздыванием пальцев, дуги движения по бокам",
       op=120, series="p2")
def wave(c):
    x, y = 256, 330
    palm = geo.rrect(x - 110, y - 80, x + 110, y + 110, 60)
    fingers = [cap((x - 84, y - 60), (x - 110, y - 230), 60), cap((x - 28, y - 70), (x - 30, y - 262), 62),
               cap((x + 30, y - 70), (x + 40, y - 256), 62), cap((x + 84, y - 60), (x + 110, y - 214), 58)]
    thumb = cap((x - 100, y + 40), (x - 180, y - 44), 62)
    g = geo.U(palm, *fingers, thumb)
    g = seps(g, [((x - 56, y - 100), (x - 56, y - 30)), ((x, y - 110), (x, y - 40)), ((x + 57, y - 100), (x + 57, y - 30))])
    wr = (x, y + 110)
    r = Track(0, 0).hold(10)
    for k, t in enumerate((10, 30, 50)):
        r.to(t + 10, -14, "io").to(t + 20, 12, "io")
    r.to(84, 0, "io").loop(120)
    c.layer("hand", [geo.shape(g, nm="hand")], p=wr, a=wr, r=r)
    for k, (d, t0) in enumerate(((-1, 22), (1, 32), (-1, 42), (1, 52))):
        cx0 = x + d * 180
        pts = geo.arc(x, y + 110, 330, -90 + d * 32, -90 + d * 42, 8)
        e = Track(0, 0).hold(t0).to(t0 + 8, 100, "o").hold(120)
        s0 = Track(0, 0).hold(t0 + 4).to(t0 + 14, 100, "i").hold(120)
        c.layer(f"arc{k}", [geo.stroked(pts, 22, e=e, s=s0)], p=(0, 0), a=(0, 0), ip=t0, op=t0 + 15)
