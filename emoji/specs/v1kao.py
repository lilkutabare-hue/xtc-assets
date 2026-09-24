"""v1 kaomoji 33-42 reworked in the v2 face kit (bigger, fatter, new stories)."""
import math

from xtc import geo, kao as K, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji
from specs.faces import CX, CY, cyc, jitter, part, rig


@emoji("33-kao-xx", "😵", "нокаут, всё, вырубило, x_x, умер", "knocked out, ko, dead, x_x, dizzy",
       "x_x получает удар сверху: морду сплющивает в блин, X-глаза подскакивают, пружинит обратно и качается",
       op=150, series="v1")
def kao_xx(c):
    # bonk from above at 30: pancake 130/60 for 2f, spring back with 3 swings
    s = Track([100, 100], 0).hold(24).to(30, [104, 96], "io").to(34, [110, 66], "slam").to(36, [110, 66], "lin")
    s.to(44, [88, 116], "snap").to(52, [106, 95], "io").to(60, [97, 103], "io").to(68, [101, 99], "io").to(76, [100, 100], "io").loop(150)
    r = Track(0, 0).hold(60).to(76, -8, "io").to(92, 6, "io").to(108, -3, "io").to(124, 0, "io").loop(150)
    face = rig(c, p=(CX, 440), s=s, r=r)
    face.a = (CX, 440)
    for i, x in enumerate((CX - 118, CX + 118)):
        ey = Track(214, 0).hold(34).to(40, 170, "decel").to(48, 214, "slam").loop(150)
        er = Track(0, 0).hold(34).to(48, (-1) ** i * 180, "o").hold(150)
        er.k[-1][2] = "hold"
        er.k.append([149.99, 0, None])
        part(c, f"eye{i}", K.xeye(x, 214, 118, 46), face, (x, 214), p=Split(x, ey), r=er)
    ms = Track([100, 100], 0).hold(34).to(44, [70, 170], "snap").to(60, [100, 100], "io").loop(150)
    part(c, "mouth", K.m_wave(CX, 360, 150, 14, 40, 1), face, (CX, 360), s=ms)
    # impact lines above the head
    from specs.drop import speed_lines
    for k, (p0, p1) in enumerate((((CX - 90, 110), (CX - 120, 70)), ((CX, 96), (CX, 50)), ((CX + 90, 110), (CX + 120, 70)))):
        e = Track(0, 0).hold(32).to(39, 100, "o").hold(150)
        s0 = Track(0, 0).hold(34).to(42, 100, "i").hold(150)
        c.layer(f"hit{k}", [geo.stroked([p0, p1], 24, e=e, s=s0)], p=(0, 0), a=(0, 0), ip=32, op=43)


@emoji("34-kao-squeeze", "😣", "терплю, держусь, больно, жмурюсь, >_<", "persevere, hang in, ouch, squeeze, >_<",
       ">_< жмурится сильнее и сильнее — морда сжимается рывками с дрожью, потом выдох: распрямляется с перелётом",
       op=150, series="v1")
def kao_squeeze(c):
    s = Track([100, 100], 0).hold(10)
    t = 10
    for k, v in enumerate((94, 88, 82)):
        s.to(t + 6, [v + 1, v - 2], "snap")
        jitter(s, t + 6, t + 22, [v + 1, v - 2], 1.2, 2)
        t += 22
    s.to(t + 8, [112, 110], "snap").to(t + 18, [96, 97], "io").to(t + 28, [102, 102], "io").to(t + 38, [100, 100], "io").loop(150)
    face = rig(c, s=s)
    for i, (x, d) in enumerate(((CX - 112, 1), (CX + 112, -1))):
        es = Track([100, 100], 0).hold(10).to(16, [104, 84], "snap").hold(t).to(t + 8, [96, 118], "snap").to(t + 20, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.chevron(x, 206, 140, d=d), face, (x + d * 30, 206), s=es)
    ms = Track([100, 100], 0).hold(10).to(16, [120, 70], "snap").hold(t).to(t + 8, [80, 140], "snap").to(t + 20, [100, 100], "io").loop(150)
    part(c, "mouth", K.m_line(CX, 350, 150), face, (CX, 350), s=ms)
    # "phew" puff at the release
    M.particle(c, "puff", K.steam(CX + 110, 350, 70), t + 6, 30, (CX + 110, 350), (CX + 180, 330), None,
               pop=0.15, fade=0.5, fall="decel", anchor=(CX + 110, 350))


@emoji("35-kao-happy", "😊", "радуюсь, счастлив, мило, ура, ^^", "happy, glad, yay, cute, ^^",
       "^‿^ танцует два шага на бит: перенос веса влево-вправо с наклоном и приседом, на каждом шаге щёки вспыхивают ✦",
       op=120, series="v1")
def kao_happy(c):
    gy = 440
    x = Track(CX, 0)
    r = Track(0, 0)
    s = Track([100, 100], 0)
    for k, t in enumerate((0, 30, 60, 90)):
        d = -1 if k % 2 == 0 else 1
        x.to(t + 14, CX + d * 22, "io").to(t + 30, CX + d * 22 * 0.2, "io")
        r.to(t + 14, d * 6, "io").to(t + 30, d * 1.5, "io")
        s.to(t + 8, [106, 93], "io").to(t + 16, [96, 104], "o").to(t + 30, [100, 100], "io")
    x.k[-1][1] = CX
    r.k[-1][1] = 0
    face = rig(c, p=Split(x, gy), s=s, r=r)
    face.a = (CX, gy)
    for i, xx in enumerate((CX - 116, CX + 116)):
        part(c, f"eye{i}", K.caret(xx, 214, 140), face, (xx, 214))
    part(c, "mouth", K.m_smile(CX, 344, 190, 58), face, (CX, 344))
    for k, t in enumerate((10, 40, 70, 100)):
        xx = CX + (-1 if k % 2 == 0 else 1) * 158
        M.twinkle(c, f"tw{k}", xx, 300, 30, t, 20, parent=face)


@emoji("36-kao-cry", "😢", "грустно, плачу, обидно, слеза, эх", "sad, crying, tear, upset, hurt",
       "o_o: в уголке глаза набухает одна слеза, дрожит, срывается и катится по щеке, губа дрожит",
       op=150, series="v1")
def kao_cry(c):
    face = rig(c)
    for i, x in enumerate((CX - 128, CX + 128)):
        es = Track([100, 100], 0).hold(30).to(44, [104, 86], "io").hold(100).to(112, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.eyelet(x, 200, 80, 0.46), face, (x, 200), s=es)
    mr = Track(0, 0).hold(40)
    jitter(mr, 40, 96, 0, 4, 2)
    mr.loop(150)
    part(c, "mouth", K.m_frown(CX, 368, 190, 46, 44), face, (CX, 368), r=mr)
    # the tear: swells in the eye corner (tremble), then runs down the cheek and drops
    tx, ty = CX + 170, 272
    ts = Track([0, 0], 0).hold(20).to(56, [100, 100], "is")
    jitter(ts, 56, 76, [100, 100], 3, 2)
    ts.to(80, [90, 116], "io").hold(118).to(126, [60, 60], "i").to(128, [0, 0], "lin").loop(150, "lin")
    ty_ = Track(ty, 0).hold(78).to(118, 430, "i").loop(150, "lin")
    tx_ = Track(tx, 0).hold(78).to(118, tx + 18, "os").loop(150, "lin")
    part(c, "tear", K.tear(tx, ty, 26), face, (tx, ty), p=Split(tx_, ty_), s=ts)


@emoji("37-kao-meh", "😑", "пофиг, ну и, мда, без эмоций, -_-", "meh, whatever, deadpan, bored, -_-",
       "-_- долго ничего, потом над головой по одной печатаются три точки «…» и гаснут разом",
       op=180, series="v1")
def kao_meh(c):
    face = rig(c)
    for i, x in enumerate((CX - 118, CX + 118)):
        es = Track([100, 100], 0).hold(120 + i * 4).to(124 + i * 4, [100, 40], "i").to(132 + i * 4, [100, 100], "o").loop(180)
        part(c, f"eye{i}", K.dash(x, 220, 160, 46), face, (x, 220), s=es)
    part(c, "mouth", K.m_line(CX, 356, 150), face, (CX, 356))
    for k in range(3):
        x = CX - 90 + k * 90
        t0 = 30 + k * 18
        s = Track([0, 0], 0).hold(t0).to(t0 + 6, [120, 120], "snap").to(t0 + 12, [100, 100], "io").hold(110)
        s.to(116, [0, 0], "i").loop(180, "lin")
        y = Track(96, 0).hold(t0).to(t0 + 6, 88, "decel").to(t0 + 12, 96, "io").loop(180)
        c.layer(f"dot{k}", [geo.shape(geo.disc(x, 96, 30), nm="dot")], parent=face, p=Split(x, y), a=(x, 96), s=s)


@emoji("38-kao-tear", "😅", "неловко, хех, упс, пот, фух", "awkward, sweat smile, heh, oops, phew",
       "^_^ неловко хихикает мелкой дрожью, по виску скатывается большая капля пота",
       op=150, series="v1")
def kao_tear(c):
    y = Track(CY, 0).hold(20)
    cyc(y, 20, 60, CY - 6, CY + 2, 8, "io")
    y.to(70, CY, "io").loop(150)
    face = rig(c, p=Split(CX, y))
    for i, x in enumerate((CX - 116, CX + 116)):
        part(c, f"eye{i}", K.caret(x, 220, 136), face, (x, 220))
    part(c, "mouth", K.m_smile(CX, 350, 170, 50), face, (CX, 350))
    # sweat drop at the right temple: appears, slides down with a wobble, falls off
    sx, sy = CX + 210, 124
    ss = Track([0, 0], 0).hold(30).to(40, [110, 110], "snap").to(46, [100, 100], "io").hold(118).to(126, [0, 0], "i").loop(150, "lin")
    py = Track(sy, 0).hold(50).to(116, sy + 150, "is").loop(150, "lin")
    part(c, "sweat", K.tear(sx, sy, 30), face, (sx, sy), p=Split(sx, py), s=ss)


@emoji("39-kao-wink", "😉", "подмигиваю, намёк, хитро, ;), договорились", "wink, ;), hint, deal, flirty",
       "^_- голова наклоняется, глаз подмигивает щелчком — из него выстреливает ✦, уголок рта поднимается",
       op=120, series="v1")
def kao_wink(c):
    r = Track(0, 0).hold(20).to(34, -8, "io").hold(84).to(100, 0, "io").loop(120)
    face = rig(c, r=r)
    part(c, "eyeL", K.caret(CX - 116, 214, 136), face, (CX - 116, 214))
    ws = Track([100, 100], 0).hold(30).to(34, [110, 12], "i").hold(58).to(64, [100, 100], "o").loop(120)
    part(c, "eyeR", K.eyelet(CX + 116, 214, 64, 0.44), face, (CX + 116, 214), s=ws)
    part(c, "eyeR2", K.dash(CX + 116, 214, 140, 44), face, (CX + 116, 214),
         s=Track([0, 100], 0).hold(30).to(34, [100, 100], "o").hold(58).to(62, [0, 100], "i").loop(120))
    ms = Track([100, 100], 0).hold(30).to(38, [108, 120], "back").hold(84).to(96, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_smirk(CX, 356, 190, 44), face, (CX - 90, 360), s=ms)
    M.twinkle(c, "tw", CX + 196, 120, 46, 34, 26, parent=face)


@emoji("40-kao-shock", "😲", "в шоке, ого, что?!, челюсть отвисла, ааа", "shocked, whoa, jaw drop, what, astonished",
       "O_O: глаза-люверсы выпрыгивают вперёд, челюсть падает вниз и вытягивается, со стуком возвращается",
       op=120, series="v1")
def kao_shock(c):
    face = rig(c)
    for i, x in enumerate((CX - 116, CX + 116)):
        es = Track([100, 100], 0).hold(16).to(22, [88, 88], "io").to(28, [138, 138], "snap").to(36, [122, 122], "io").hold(80).to(92, [100, 100], "io").loop(120)
        part(c, f"eye{i}", K.eyelet(x, 190, 74, 0.44), face, (x, 190), s=es)
    my = Track(316, 0).hold(24).to(40, 350, "slam").to(46, 340, "io").to(52, 346, "io").hold(84).to(90, 310, "snap").to(98, 316, "io").loop(120)
    ms = Track([100, 100], 0).hold(24).to(40, [86, 168], "slam").to(46, [90, 152], "io").hold(84).to(90, [100, 90], "snap").to(98, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_o(CX, 316, 50, 0.4), face, (CX, 290), p=Split(CX, my), s=ms)


@emoji("42-kao-tongue", "😛", "бе-бе, дразню, язык, прикол, :P", "tongue, :p, teasing, bleh, silly",
       "-_- показывает язык: он выстреливает вниз и болтается влево-вправо «бе-бе», глаза жмурятся",
       op=120, series="v1")
def kao_tongue(c):
    face = rig(c)
    for i, (x, d) in enumerate(((CX - 128, 1), (CX + 128, -1))):
        es = Track([100, 100], 0).hold(20).to(28, [104, 76], "io").hold(90).to(100, [100, 100], "io").loop(120)
        part(c, f"eye{i}", K.chevron(x, 196, 150, d=d, open_=0.72), face, (x + d * 30, 196), s=es)
    part(c, "mouth", K.m_line(CX, 316, 190), face, (CX, 316))
    tongue = geo.rrect(CX - 58, 316, CX + 58, 450, 56).difference(geo.rrect(CX - 6, 340, CX + 6, 408, 6))
    ts = Track([100, 0], 0).hold(20).to(28, [100, 112], "snap").to(34, [100, 96], "io").to(40, [100, 100], "io").hold(92).to(102, [100, 0], "i").loop(120)
    tr = Track(0, 0).hold(40)
    for k, a in enumerate((12, -12, 10, -8, 5)):
        tr.to(48 + k * 9, a, "io")
    tr.to(96, 0, "io").loop(120)
    part(c, "tongue", tongue, face, (CX, 320), s=ts, r=tr)
