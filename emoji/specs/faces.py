"""P0 faces: kaomoji glyphs, big and fat, rigged on a face null."""
import math

from xtc import geo, kao as K, motion as M
from xtc.lot import Split, Track
from xtc.reg import emoji

CX, CY = 256, 270


def rig(c, nm="face", p=(CX, CY), s=None, r=None, parent=None):
    return c.null(nm, parent=parent, p=p, a=p if not isinstance(p, (Track, Split)) else p.v0, s=s or (100, 100), r=r or 0)


def part(c, nm, g, parent, anchor, p=None, s=None, r=None, o=100, ip=0, op=None):
    return c.layer(nm, [geo.shape(g, nm=nm)], parent=parent, p=p if p is not None else anchor, a=anchor,
                   s=s if s is not None else (100, 100), r=r if r is not None else 0, o=o, ip=ip, op=op)


def cyc(tr, t0, t1, a, b, per, ease="swing"):
    """alternate a/b every per/2 frames from t0 to t1 (starts heading to a)."""
    t, k = t0, 0
    while t + per / 2 <= t1 + 1e-6:
        t += per / 2
        tr.to(t, a if k % 2 == 0 else b, ease)
        k += 1
    return tr


@emoji("54-laugh", "😂", "ржу, смешно, лол, ахаха, слёзы", "lol, laugh, lmao, crying laughing, haha",
       ">▽< набирает воздух и ржёт — тело трясёт басом, слёзы бьют фонтаном по дугам с двух сторон, затихает",
       op=120, series="face")
def laugh(c):
    # body: inhale, 8 laugh bounces (10f each, M12), decay, rest
    s = Track([100, 100], 0).hold(6).to(14, [106, 93], "io")
    cyc(s, 14, 84, [95, 106], [105, 95], 10)
    s.to(92, [98, 102], "io").to(100, [101, 99], "io").to(108, [100, 100], "io").loop(120)
    y = Track(CY, 0).hold(6).to(14, CY + 10, "io")
    cyc(y, 14, 84, CY - 12, CY + 6, 10)
    y.to(96, CY + 2, "io").to(108, CY, "io").loop(120)
    rr = Track(0, 0).hold(14)
    cyc(rr, 14, 84, -4, 4, 20, "io")
    rr.to(100, 0, "io").loop(120)
    face = rig(c, p=Split(CX, y), s=s, r=rr)
    # eyes squeeze on every bounce, lagging 2f
    for i, (x, d) in enumerate(((CX - 104, 1), (CX + 104, -1))):
        es = Track([100, 100], 0).hold(8).to(16, [104, 78], "io")
        cyc(es, 16, 86, [100, 92], [104, 74], 10)
        es.to(100, [100, 100], "io").loop(120)
        part(c, f"eye{i}", K.chevron(x, 206, s=136, d=d), face, (x + d * 30, 206), s=es)
    # mouth: "ha-ha-ha" opening 3f after the body
    ms = Track([100, 100], 0).hold(9).to(17, [96, 112], "io")
    cyc(ms, 17, 87, [104, 76], [96, 114], 10)
    ms.to(100, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_tri(CX, 346), face, (CX, 300), s=ms)
    # tear fountains: 5 drops per side shoot up from the outer eye corners (SNAP_OUT), arc over the free
    # corners of the canvas and land beside the mouth; the tip trails the velocity
    for side, d in enumerate((-1, 1)):
        x0 = CX + d * 150
        for k in range(5):
            t0 = 16 + k * 13 + side * 5
            M.particle(c, f"tear{side}{k}", K.tear(x0, 170, 24), t0, 34,
                       (x0, 170), (CX + d * (212 - 8 * (k % 2)), 372 - 18 * (k % 3)), apex=58 + 14 * (k % 2),
                       parent=face, rot=(-d * 163, -d * 8), anchor=(x0, 170), s_peak=100 - 8 * (k % 2))


def jitter(tr, t0, t1, base, amp, step=2, grow=None):
    """M13 shiver: alternate around base every `step` frames; amp may ramp (grow=(a0, a1))."""
    tr.hold(t0)
    t, k = t0, 0
    n = max(1, int((t1 - t0) / step) - 1)
    while t + step < t1:
        t += step
        a = amp if grow is None else grow[0] + (grow[1] - grow[0]) * (k / n)
        sgn = 1 if k % 2 == 0 else -1
        if isinstance(base, (list, tuple)):
            v = [b + sgn * a * (1 if j == 0 else -0.6) for j, b in enumerate(base)]
        else:
            v = base + sgn * a
        tr.to(t, v, "aelin")
        k += 1
    tr.to(t1, base, "io")
    return tr


@emoji("55-rofl", "🤣", "угар, ору, катаюсь, ржака, лмао", "rofl, lmao, rolling, dying, laughing",
       ">▽< откидывается назад и катится колесом на полный оборот, слёзы слетают по касательной, приземляется набок и доржает",
       op=150, series="face")
def rofl(c):
    # roll: lean back (antic) -> 360+ roll with a hop -> land tilted -> ha-ha -> upright
    r = Track(0, 0).hold(10).to(24, 18, "io").to(74, -372, (0.45, 0.0, 0.2, 1.0)).to(86, -352, "io")
    r.to(96, -364, "io").to(104, -360 + -22, "io").hold(128).to(146, -360, "io")
    # keep it one value at loop point: -360 == 0 visually, so wrap with a hold key
    r.k[-1][2] = "hold"
    r.k.append([150, 0, None])
    y = Track(CY, 0).hold(24).to(46, CY - 34, "o").to(70, CY + 4, "i5").to(80, CY - 10, "o").to(88, CY, "i").loop(150)
    s = Track([100, 100], 0).hold(12).to(24, [104, 95], "io").to(34, [96, 104], "o").to(52, [100, 100], "io").hold(68)
    s.to(71, [110, 90], "o").to(80, [97, 103], "io").to(88, [100, 100], "io")
    cyc(s, 104, 128, [104, 95], [97, 103], 8)
    s.to(136, [100, 100], "io").loop(150)
    face = rig(c, p=Split(CX, y), s=s, r=r)
    ds = [(CX - 106, 1), (CX + 106, -1)]
    for i, (x, d) in enumerate(ds):
        es = Track([100, 100], 0).hold(20).to(30, [104, 80], "io").hold(96)
        cyc(es, 104, 128, [100, 70], [104, 86], 8)
        es.to(136, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.chevron(x, 206, s=132, d=d), face, (x + d * 30, 206), s=es)
    ms = Track([100, 100], 0).hold(20).to(30, [104, 112], "io").hold(96)
    cyc(ms, 104, 130, [100, 80], [104, 114], 8)
    ms.to(138, [100, 100], "io").loop(150)
    part(c, "mouth", K.m_tri(CX, 344, 180, 124), face, (CX, 300), s=ms)
    # tears thrown off tangentially during the roll (world space, not parented)
    for k, (t0, x0, y0, x1, y1, rot) in enumerate([(40, 150, 110, 40, 60, -60), (46, 380, 120, 470, 70, 60),
                                                   (54, 400, 330, 480, 430, 140), (60, 120, 360, 36, 440, -140)]):
        M.particle(c, f"fling{k}", K.tear(x0, y0, 22), t0, 22, (x0, y0), (x1, y1), None,
                   rot=(rot + 180, rot + 180), anchor=(x0, y0), fall="os")


@emoji("56-sob", "😭", "рыдаю, плачу, горе, ревёт, тт", "sob, crying, tears, sad, t_t",
       "T_T рыдает: из-под глаз бьют два ручья до самого низа, рот-волна дрожит, всхлипы подбрасывают лицо",
       op=120, series="face")
def sob(c):
    # sobs: 3 hiccups per loop (inhale up, fall back), M12 jelly
    y = Track(CY - 20, 0)
    for t in (0, 40, 80):
        y.hold(t + 4).to(t + 10, CY - 34, "decel").to(t + 22, CY - 16, "slam").to(t + 30, CY - 22, "io")
    y.loop(120)
    s = Track([100, 100], 0)
    for t in (0, 40, 80):
        s.hold(t + 4).to(t + 10, [96, 106], "io").to(t + 22, [106, 94], "o").to(t + 34, [100, 100], "io")
    s.loop(120)
    face = rig(c, p=Split(CX, y), s=s)
    for i, x in enumerate((CX - 118, CX + 118)):
        es = Track([100, 100], 0)
        for t in (0, 40, 80):
            es.hold(t + 6).to(t + 12, [108, 86], "io").to(t + 26, [100, 100], "io")
        es.loop(120)
        part(c, f"eye{i}", K.teye(x, 190, 150), face, (x, 190), s=es)
        # the stream: a drop every 6f from under the stem, falling to the bottom edge (M16), wrapped
        for k in range(20):
            xx = x + (8 if i else -8) * ((k % 3) - 1)
            M.particle(c, f"s{i}{k}", K.tear(xx, 290, 21 + (k % 2) * 3), k * 6, 26, (xx, 272), (xx + (-6 if i else 6), 470),
                       None, parent=face, anchor=(xx, 290), pop=0.12, fade=0.15, fall="i", s_end=60)
    # mouth: wobbling wave, lagging 4f
    mr = Track(0, 0)
    ms = Track([100, 100], 0)
    for t in (0, 40, 80):
        ms.hold(t + 8).to(t + 14, [92, 130], "io").to(t + 28, [100, 100], "io")
        mr.hold(t + 8).to(t + 12, -4, "io").to(t + 16, 4, "io").to(t + 20, -2, "io").to(t + 26, 0, "io")
    ms.loop(120)
    mr.loop(120)
    part(c, "mouth", K.m_wave(CX, 352, 170, 16), face, (CX, 352), s=ms, r=mr)


def pop_in(tr, t, peak, low, base, d1=8, d2=7, d3=8):
    """M9 pop: -> peak (SNAP) -> undershoot -> base."""
    tr.to(t + d1, peak, "snap").to(t + d1 + d2, low, "io").to(t + d1 + d2 + d3, base, "io")
    return tr


@emoji("57-plead", "🥺", "ну пожалуйста, умоляю, щенячьи глаза, милота", "please, pleading, puppy eyes, cute, begging",
       "брови домиком, глаза-люверсы раздуваются огромными, в зрачках дрожит ✦-блик, губа трясётся",
       op=120, series="face")
def plead(c):
    rr = Track(0, 0).hold(16).to(30, -7, "io").hold(88).to(104, 0, "io").loop(120)
    face = rig(c, r=rr)
    for i, (x, d) in enumerate(((CX - 118, -1), (CX + 118, 1))):
        ey = 222
        # eyelet eye: fat ring + big pupil with two glint holes
        g = geo.U(K.eyelet(x, ey, 86, 0.66), geo.disc(x + d * 3, ey + 5, 48))
        g = g.difference(geo.disc(x - 18, ey - 12, 20)).difference(geo.disc(x + 16, ey + 22, 9))
        es = Track([100, 100], 0).hold(18)
        pop_in(es, 18, [132, 132], [118, 118], [124, 124], 9, 7, 8)
        jitter(es, 44, 88, [124, 124], 1.4, 2)
        es.to(96, [100, 100], "io").to(99, [104, 30], "i").to(106, [100, 100], "o").loop(120)
        part(c, f"eye{i}", g, face, (x, ey), s=es)
        # worried brows, inner ends up
        bs = Track([0, 0], 0).hold(16).to(28, [0, -18], "o").hold(92).to(104, [0, 0], "io").loop(120)
        bx = x - d * 10
        part(c, f"brow{i}", K.brow(bx, 96, 120, ang=d * 18, w=34), face, (bx, 96),
             p=Track([bx, 96], 0).hold(16).to(28, [bx, 80], "o").hold(92).to(104, [bx, 96], "io").loop(120))
    # trembling lower lip (small frown), shivering 2f
    mr = Track(0, 0).hold(34)
    jitter(mr, 34, 90, 0, 5, 2)
    mr.loop(120)
    ms = Track([100, 100], 0).hold(24).to(34, [86, 110], "io").hold(90).to(100, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_frown(CX, 392, 104, 34, 38), face, (CX, 392), s=ms, r=mr)


@emoji("58-heart-eyes", "😍", "влюбился, обожаю, красота, вау, love", "love, heart eyes, crush, adore, wow",
       "♥_♥ сердца-глаза делают двойной удар, на втором выпрыгивают вперёд на 150% и тянут за собой лицо",
       op=120, series="face")
def heart_eyes(c):
    s = Track([100, 100], 0).hold(30).to(38, [104, 104], "snap").hold(52).to(64, [100, 100], "io").loop(120)
    face = rig(c, s=s)
    for i, x in enumerate((CX - 116, CX + 116)):
        t0 = i * 3                   # right eye trails 3f (overlap)
        es = Track([100, 100], 0).hold(8 + t0)
        es.to(13 + t0, [114, 114], "snap").to(22 + t0, [100, 100], "io")            # thump 1 (5 up / 10 down)
        es.to(27 + t0, [138, 138], "snap").to(34 + t0, [126, 126], "io")            # thump 2: pops forward
        jitter(es, 34 + t0, 56 + t0, [128, 128], 2.5, 3)
        es.to(66 + t0, [92, 92], "io").to(74 + t0, [103, 103], "io").to(82 + t0, [100, 100], "io")
        es.hold(98).to(103, [110, 110], "snap").to(112, [100, 100], "io").loop(120)
        rr = Track(0, 0).hold(27 + t0).to(40 + t0, (-1) ** i * 8, "io").to(56 + t0, (-1) ** (i + 1) * 6, "io").to(70 + t0, 0, "io").loop(120)
        part(c, f"eye{i}", K.heye(x, 208, 150), face, (x, 216), s=es, r=rr)
    ms = Track([100, 100], 0).hold(26).to(34, [112, 124], "snap").hold(56).to(68, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_w(CX, 372, 170, 50), face, (CX, 360), s=ms)


@emoji("59-kiss", "😘", "чмок, целую, поцелуй, люблю, муа", "kiss, mwah, love, xoxo, smooch",
       "-3- собирает губы, подмигивает и чмокает — сердечко выстреливает по дуге с растяжкой, лицо откидывает отдачей",
       op=120, series="face")
def kiss(c):
    rr = Track(0, 0).hold(10).to(28, 8, "io").to(36, -6, "snap").to(50, 2, "io").to(60, 0, "io").loop(120)
    face = rig(c, r=rr)
    # left eye: calm dash; right eye: winks shut at the smooch
    part(c, "eyeL", K.caret(CX - 118, 214, 140), face, (CX - 118, 214))
    ws = Track([100, 100], 0).hold(24).to(30, [108, 20], "i").hold(52).to(60, [100, 100], "o").loop(120)
    part(c, "eyeR", K.caret(CX + 118, 214, 140), face, (CX + 118, 214), s=ws)
    # mouth: pucker (antic) -> push forward (smooch) -> settle
    ms = Track([100, 100], 0).hold(10).to(28, [78, 84], "io").to(34, [128, 120], "snap").to(42, [94, 96], "io")
    ms.to(52, [100, 100], "io").loop(120)
    mp = Track([CX + 10, 350], 0).hold(10).to(28, [CX + 2, 352], "io").to(34, [CX + 24, 346], "snap").to(52, [CX + 10, 350], "io").loop(120)
    part(c, "mouth", K.m_3(CX + 10, 350, 124), face, (CX + 10, 350), p=mp, s=ms)
    # the heart: shoots out of the lips with a 140% vertical stretch (M25), arcs up-right, beats once, pops
    hx, hy = CX + 70, 330
    g = geo.heart(hx, hy, 120)
    p = Split(Track(hx, 0).hold(34).to(84, 408, "os"), Track(hy, 0).hold(34).to(84, 104, "decel"))
    s = Track([0, 0], 0).hold(34).to(40, [70, 140], "snapo").to(50, [104, 96], "io").to(58, [100, 100], "io")
    s.hold(70).to(75, [116, 116], "snap").to(82, [96, 96], "io").to(88, [0, 0], "i5").loop(120, "lin")
    r = Track(-30, 0).hold(34).to(60, 14, "io").to(88, 4, "io").loop(120, "lin")
    c.layer("heart", [geo.shape(g, nm="heart")], p=p, a=(hx, hy), s=s, r=r, ip=34, op=89)


@emoji("60-rage", "😡", "бесит, злой, ярость, гнев, сука", "angry, rage, mad, furious, pissed",
       "злость копится: лицо дрожит всё сильнее, вена ╬ набухает, на пике из ушей бьёт пар и морду трясёт",
       op=150, series="face")
def rage(c):
    # tremble ramps up 1% -> 5px, peaks at 76, calms down
    px = Track(CX, 0).hold(12)
    jitter(px, 12, 74, CX, 0, 2, grow=(1, 7))
    jitter(px, 74, 100, CX, 9, 2)
    px.to(112, CX, "io").loop(150)
    s = Track([100, 100], 0).hold(12).to(70, [104, 104], "is").to(76, [110, 94], "snap").to(86, [98, 103], "io")
    s.to(96, [102, 99], "io").to(110, [100, 100], "io").loop(150)
    face = rig(c, p=Split(px, CY), s=s)
    for i, (x, d) in enumerate(((CX - 118, 1), (CX + 118, -1))):
        part(c, f"brow{i}", K.brow(x, 170, 150, ang=d * 24, w=44), face, (x, 170))
        es = Track([100, 100], 0).hold(60).to(76, [110, 70], "snap").hold(100).to(112, [100, 100], "io").loop(150)
        part(c, f"eye{i}", geo.disc(x + d * 16, 238, 36), face, (x + d * 16, 238), s=es)
    ms = Track([100, 100], 0).hold(60).to(76, [116, 80], "snap").hold(100).to(112, [100, 100], "io").loop(150)
    part(c, "mouth", K.m_frown(CX, 368, 190, 56), face, (CX, 368), s=ms)
    # vein: beats faster and bigger as it builds (M1 rhythm compressing)
    vx, vy = CX + 142, 104
    vs = Track([0, 0], 0).hold(8).to(18, [90, 90], "snap")
    t = 18
    for k, (dt, a) in enumerate([(18, 100), (14, 104), (11, 108), (9, 112), (7, 116), (6, 120)]):
        vs.to(t + dt * 0.35, [a, a], "snap").to(t + dt, [a - 16, a - 16], "io")
        t += dt
    vs.to(t + 6, [124, 124], "snap").hold(100).to(114, [100, 100], "io").hold(132).to(142, [0, 0], "i").loop(150, "lin")
    part(c, "vein", K.vein(vx, vy, 92, 24), face, (vx, vy), s=vs)
    # steam puffs from the ears at the peak
    for side, d in enumerate((-1, 1)):
        for k in range(3):
            t0 = 76 + k * 5 + side * 2
            x0 = CX + d * 172
            M.particle(c, f"steam{side}{k}", K.steam(x0, 300, 76 - k * 12, d=-d), t0, 30,
                       (x0, 300), (x0 + d * 10, 120 - k * 30), None, parent=face, anchor=(x0, 300),
                       pop=0.15, fade=0.5, fall="decel", s_peak=100 - k * 10)
