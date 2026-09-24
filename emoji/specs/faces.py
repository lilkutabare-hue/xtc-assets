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


def glyph_outline(ch, x, y, h, bold=10):
    from specs.drop import brand_font
    return geo.text(ch, brand_font(), x, y, h, bold=bold)


@emoji("61-swear", "🤬", "мат, сука, бля, ругаюсь, #$%!", "swearing, cursing, #$%!, wtf, furious",
       "рот-табло: глифы #$%@! перещёлкиваются как на flip-табло, злые глаза, голову трясёт на каждом ругательстве",
       op=120, series="face")
def swear(c):
    # head nods hard on every swap (every 12f), M13 tremble in between
    y = Track(CY, 0).hold(16)
    for t in range(22, 94, 12):
        y.to(t + 3, CY + 10, "slam").to(t + 10, CY - 2, "io")
    y.to(104, CY, "io").loop(120)
    face = rig(c, p=Split(CX, y))
    for i, (x, d) in enumerate(((CX - 128, 1), (CX + 128, -1))):
        # angry eye: disc cut by a slanted lid
        e = geo.disc(x, 196, 70).difference(geo.rot(geo.rect(x - 110, 60, x + 110, 178), d * 22, (x, 178)))
        es = Track([100, 100], 0).hold(14).to(22, [106, 84], "snap").hold(96).to(106, [100, 100], "io").loop(120)
        part(c, f"eye{i}", e, face, (x, 210), s=es)
    # the board: a black bar with glyph holes; each slot flips through glyphs with hold keys on scale
    bx, by, bw, bh = CX, 358, 420, 150
    bar = geo.rrect(bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2, 30)
    bs = Track([100, 24], 0).hold(12).to(20, [100, 112], "snap").to(26, [100, 96], "io").to(30, [100, 100], "io")
    for t in range(34, 94, 12):
        bs.to(t + 2, [102, 92], "io").to(t + 6, [100, 100], "io")
    bs.hold(98).to(106, [100, 24], "i5").loop(120)
    lay = c.layer("board", [geo.shape(bar, nm="bar")], parent=face, p=(bx, by), a=(bx, by), s=bs)
    seqs = ["#$%!", "$!#@", "%@!#", "!#@$", "@%$!"]
    slots = [bx - 150, bx - 50, bx + 50, bx + 150]
    for j, sx in enumerate(slots):
        chars = [seq[j] for seq in seqs]
        for k, ch in enumerate(chars):
            ton, toff = 22 + k * 12 + j * 1, 22 + (k + 1) * 12 + j * 1
            if k == len(chars) - 1:
                toff = 100
            g = geo.fit_box(glyph_outline(ch, sx, by, 90, bold=8), sx - 38, by - 46, sx + 38, by + 46)
            sc = Track([0, 0], 0)
            sc.k[-1][2] = "hold"
            sc.k.append([ton, [100, 100], None])
            sc.k[-1][2] = "hold"
            sc.k.append([toff, [0, 0], None])
            sc.to(120, [0, 0], "lin")
            geo.hole(lay, g, nm=f"g{j}{k}", p=(sx, by), a=(sx, by), s=sc)


@emoji("62-scream", "😱", "ужас, аааа, шок, кошмар, страшно", "scream, horror, shock, omg, terrified",
       "O□O: лицо приседает и вытягивается вверх на 140%, глаза-люверсы выстреливают, рот-коробка орёт, всё дрожит",
       op=120, series="face")
def scream(c):
    s = Track([100, 100], 0).hold(12).to(24, [110, 88], "io").to(31, [86, 128], "snap")
    jitter(s, 31, 78, [88, 124], 1.6, 2)
    s.to(90, [104, 96], "io").to(100, [98, 102], "io").to(108, [100, 100], "io").loop(120)
    face = rig(c, p=(CX, 420), s=s)
    face.a = (CX, 420)
    for i, x in enumerate((CX - 118, CX + 118)):
        es = Track([100, 100], 0).hold(20).to(24, [90, 90], "io").to(31, [122, 122], "snap").to(40, [114, 114], "io").hold(80)
        es.to(92, [100, 100], "io").loop(120)
        ey = Track([x, 206], 0).hold(24).to(31, [x, 198], "snap").hold(80).to(92, [x, 206], "io").loop(120)
        part(c, f"eye{i}", K.eyelet(x, 206, 78, 0.44), face, (x, 206), p=ey, s=es)
    ms = Track([100, 100], 0).hold(24).to(32, [92, 136], "snap").hold(80).to(92, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_box(CX, 342, 136, 124, 42), face, (CX, 300), s=ms)


@emoji("63-flushed", "😳", "стыдно, смущён, покраснел, ой, неловко", "flushed, embarrassed, blush, oops, awkward",
       "O_O: по щекам прорастает штриховка румянца ////, лицо съёживается и отводит глаза",
       op=120, series="face")
def flushed(c):
    s = Track([100, 100], 0).hold(20).to(34, [94, 94], "io").hold(92).to(106, [100, 100], "io").loop(120)
    y = Track(CY, 0).hold(20).to(34, CY + 12, "io").hold(92).to(106, CY, "io").loop(120)
    face = rig(c, p=Split(CX, y), s=s)
    for i, x in enumerate((CX - 116, CX + 116)):
        es = Track([100, 100], 0).hold(8).to(16, [114, 114], "snap").to(24, [106, 106], "io")
        for tb in (58, 70):
            es.hold(tb + i * 2).to(tb + 3 + i * 2, [110, 12], "i").to(tb + 8 + i * 2, [106, 106], "o")
        es.hold(98).to(108, [100, 100], "io").loop(120)
        part(c, f"eye{i}", K.eyelet(x, 200, 78, 0.5), face, (x, 200), s=es)
        # blush: 4 hatch strokes drawn on with trim, staggered 3f
        for k in range(4):
            hx = x - 45 + k * 30
            t0 = 26 + k * 3 + i * 2
            e = Track(0, 0).hold(t0).to(t0 + 8, 100, "o").hold(96).to(104, 0, "i").loop(120)
            c.layer(f"blush{i}{k}", [geo.stroked([(hx - 14, 336), (hx + 14, 282)], 26, e=e)], parent=face, p=(0, 0), a=(0, 0))
    ms = Track([100, 100], 0).hold(20).to(30, [70, 100], "io").hold(94).to(106, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_wave(CX, 382, 110, 10, 30, 1.5), face, (CX, 382), s=ms)


@emoji("64-think", "🤔", "хм, думаю, сомнительно, вопрос, ну такое", "hmm, thinking, doubt, sus, wondering",
       "o_O: один глаз щурится, другой лезет на лоб, над головой пишется «?» и покачивается",
       op=150, series="face")
def think(c):
    rr = Track(0, 0).hold(14).to(30, -8, "io").hold(118).to(134, 0, "io").loop(150)
    face = rig(c, p=(CX, CY + 30), r=rr)
    face.a = (CX, CY + 30)
    # left: squint dash; right: ring eye grows, brow lifts
    ls = Track([100, 100], 0).hold(18).to(30, [100, 55], "io").hold(118).to(132, [100, 100], "io").loop(150)
    part(c, "eyeL", geo.disc(CX - 150, 236, 32), face, (CX - 150, 236), s=ls)
    rs = Track([100, 100], 0).hold(18).to(28, [126, 126], "snap").to(36, [118, 118], "io").hold(118).to(132, [100, 100], "io").loop(150)
    part(c, "eyeR", K.eyelet(CX + 70, 236, 64, 0.42), face, (CX + 70, 236), s=rs)
    bp = Track([CX + 70, 140], 0).hold(18).to(28, [CX + 70, 110], "snap").to(36, [CX + 70, 118], "io").hold(118).to(132, [CX + 70, 140], "io").loop(150)
    part(c, "brow", K.brow(CX + 70, 140, 120, ang=-10, w=34), face, (CX + 70, 140), p=bp)
    part(c, "browL", K.brow(CX - 150, 176, 110, ang=6, w=34), face, (CX - 150, 176))
    mr = Track(0, 0).hold(18).to(30, -10, "io").hold(118).to(132, 0, "io").loop(150)
    part(c, "mouth", K.m_line(CX - 30, 368, 130, 40), face, (CX - 30, 368), r=mr)
    # "?" drawn on with trim, then its dot pops, bobbing; top right corner
    qx, qy = 404, 120
    pts = geo.arc(qx, qy - 28, 40, 185, 395, 24) + [(qx, qy + 22)]
    e = Track(0, 0).hold(40).to(60, 100, "o").hold(124).to(136, 0, "i").loop(150)
    qr = Track(0, 0).hold(60).to(76, 14, "io").to(92, -10, "io").to(108, 8, "io").to(124, 0, "io").loop(150)
    q = c.layer("q", [geo.stroked(pts, 32, e=e)], p=(qx, qy + 60), a=(qx, qy + 60), r=qr)
    ds = Track([0, 0], 0).hold(58).to(66, [120, 120], "snap").to(72, [100, 100], "io").hold(124).to(134, [0, 0], "i").loop(150)
    c.layer("qdot", [geo.shape(geo.disc(qx, qy + 58, 19), nm="dot")], parent=q, p=(qx, qy + 58), a=(qx, qy + 58), s=ds)


@emoji("65-eyeroll", "🙄", "закатываю глаза, ой всё, бесит, скучно, ну да", "eye roll, whatever, ugh, bored, sure",
       "зрачки уезжают по дуге под самый верх люверсов со смазом, веки падают, долгий вздох и медленный возврат",
       op=150, series="face")
def eyeroll(c):
    s = Track([100, 100], 0).hold(20).to(40, [98, 104], "io").to(70, [103, 97], "io").hold(100).to(120, [100, 100], "io").loop(150)
    face = rig(c, s=s)
    R, r_in, pr = 92, 60, 36
    for i, x in enumerate((CX - 120, CX + 120)):
        ey = 214
        part(c, f"ring{i}", geo.ring(x, ey, R, r_in, 24), face, (x, ey))
        # pupil path: centre -> right -> top (arc) with smear, long hold, slow return
        lag = i * 3
        px = Track(x, 0).hold(22 + lag).to(32 + lag, x + 24, "io").to(44 + lag, x, "io").hold(96 + lag).to(118 + lag, x, "io").loop(150)
        py = Track(ey + 6, 0).hold(22 + lag).to(32 + lag, ey - 6, "io").to(44 + lag, ey - r_in + pr - 4, "o").hold(96 + lag)
        py.to(118 + lag, ey + 10, "io").to(128 + lag, ey + 6, "io").loop(150)
        ps = Track([100, 100], 0).hold(22 + lag).to(30 + lag, [96, 116], "io").to(40 + lag, [118, 92], "io").to(48 + lag, [100, 100], "io").loop(150)
        part(c, f"pupil{i}", geo.disc(x, ey + 6, pr), face, (x, ey + 6), p=Split(px, py), s=ps)
        # heavy lid (flat bar) drops over the top of the ring: half-lidded boredom
        ly = Track(ey - R - 30, 0).hold(46 + lag).to(62 + lag, ey - R + 22, "io").hold(96 + lag).to(118 + lag, ey - R - 30, "io").loop(150)
        part(c, f"lid{i}", K.dash(x, ey - R - 30, 200, 42), face, (x, ey - R - 30), p=Split(x, ly))
    # sigh: mouth line slides sideways and sags
    mp = Track([CX, 372], 0).hold(50).to(70, [CX + 24, 380], "io").hold(100).to(120, [CX, 372], "io").loop(150)
    mr = Track(0, 0).hold(50).to(70, -6, "io").hold(100).to(120, 0, "io").loop(150)
    part(c, "mouth", K.m_line(CX, 372, 140), face, (CX, 372), p=mp, r=mr)


@emoji("66-smirk", "😏", "ухмылка, ну-ну, хитрый, флирт, я знаю", "smirk, sly, flirt, i know, heh",
       "¬‿¬ веки полуопущены, ухмылка ползёт в один угол, «ну-ну» бровями дважды и ✦ на уголке рта",
       op=120, series="face")
def smirk(c):
    rr = Track(0, 0).hold(12).to(28, 5, "io").hold(96).to(110, 0, "io").loop(120)
    face = rig(c, r=rr)
    for i, x in enumerate((CX - 118, CX + 118)):
        # eyebrow-wiggle: lids bob up twice quickly (M5 settle)
        ly = Track(0, 0).hold(46 + i * 2)
        for t in (46, 58):
            ly.to(t + 4 + i * 2, -26, "snap").to(t + 10 + i * 2, 0, "slam")
        ly.to(76 + i * 2, -4, "io").to(84 + i * 2, 0, "io").loop(120)
        lid = c.null(f"lidn{i}", parent=face, p=Split(x, Track(208, 0).hold(46 + i * 2).to(50 + i * 2, 182, "snap").to(56 + i * 2, 208, "slam")
                                                         .to(62 + i * 2, 182, "snap").to(68 + i * 2, 208, "slam").to(76 + i * 2, 204, "io").to(84 + i * 2, 208, "io").loop(120)),
                     a=(x, 208))
        part(c, f"lid{i}", K.neg(x, 200, 150, d=1), lid, (x, 208))
        # half-lidded pupils sitting under the lid, looking right
        part(c, f"pupil{i}", geo.disc(x + 34, 246, 30), face, (x + 34, 246),
             s=Track([100, 100], 0).hold(100).to(103, [110, 15], "i").to(109, [100, 100], "o").loop(120))
    # smirk grows one-sided (scale anchored at the left corner)
    ms = Track([70, 60], 0).hold(14).to(34, [112, 118], "back").hold(96).to(110, [70, 60], "io").loop(120)
    part(c, "mouth", K.m_smirk(CX + 10, 360, 190, 46), face, (CX - 85, 364), s=ms)
    M.twinkle(c, "glint", CX + 150, 318, 40, 36, 22, parent=face)


@emoji("67-unamused", "😒", "фу, недоволен, ну и?, скептик, пфф", "unamused, meh, side eye, skeptical, pfft",
       "¬_¬ медленно косит в сторону, вся морда отворачивается (параллакс), держит паузу и цыкает",
       op=150, series="face")
def unamused(c):
    # fake head turn (M22): features on deeper nulls travel more
    turn = Track(0, 0).hold(24).to(52, 1, "io").hold(108).to(132, 0, "io").loop(150)
    face = rig(c)

    def shifted(dx, dy=0):
        return Split(Track(CX, 0).hold(24).to(52, CX + dx, "io").hold(108).to(132, CX, "io").loop(150),
                     Track(CY, 0).hold(24).to(52, CY + dy, "io").hold(108).to(132, CY, "io").loop(150))
    near = c.null("near", parent=face, p=shifted(40, 4), a=(CX, CY))
    far = c.null("far", parent=face, p=shifted(28, 2), a=(CX, CY),
                 s=Track([100, 100], 0).hold(24).to(52, [92, 100], "io").hold(108).to(132, [100, 100], "io").loop(150))
    for i, x in enumerate((CX - 118, CX + 118)):
        part(c, f"lid{i}", K.dash(x, 196, 150, 44, tilt=-4 if i == 0 else 4), far, (x, 196))
        pxs = Track(x, 0).hold(20).to(40, x + 38, "io").hold(108).to(132, x, "io").loop(150)
        part(c, f"pupil{i}", geo.disc(x, 244, 34), near, (x, 244), p=Split(pxs, 244),
             s=Track([100, 100], 0).hold(8 + i * 5).to(11 + i * 5, [110, 12], "i").to(17 + i * 5, [100, 100], "o").loop(150))
    # "tsk": mouth pulls to the side twice at 84/92
    mx = Track(CX, 0).hold(80).to(84, CX + 30, "snap").to(88, CX + 6, "io").to(92, CX + 28, "snap").to(100, CX, "io").loop(150)
    ms = Track([100, 100], 0).hold(80).to(84, [70, 120], "snap").to(88, [100, 100], "io").to(92, [74, 116], "snap").to(100, [100, 100], "io").loop(150)
    part(c, "mouth", K.m_line(CX, 372, 130), near, (CX, 372), p=Split(mx, 372), s=ms)


@emoji("68-cool", "😎", "круто, кайф, чил, в очках, стиль", "cool, sunglasses, chill, swag, boss",
       "Y2K-очки-щиток съезжают с макушки на глаза, кивок, по линзам проходит латексный блик и ✦",
       op=150, series="face")
def cool(c):
    y = Track(CY, 0).hold(40).to(48, CY + 14, "slam").to(58, CY - 4, "io").to(66, CY, "io").loop(150)
    face = rig(c, p=Split(CX, y))
    # visor: one wraparound lens shape, tinted solid
    v = geo.U(geo.rrect(34, 150, 478, 270, 56), geo.rect(120, 150, 392, 180))
    v = v.difference(geo.poly([(226, 272), (256, 236), (286, 272)]).buffer(10))
    # rest: visor pushed up on the forehead; slams down on the beat, lifts back before the loop
    vp = Track([CX, 92], 0).hold(12).to(22, [CX, 80], "io").to(40, [CX, 210], "slam").to(46, [CX, 198], "io")
    vp.to(52, [CX, 210], "io").hold(118).to(138, [CX, 92], "io")
    vs = Track([90, 90], 0).hold(22).to(40, [104, 94], "slam").to(46, [98, 103], "io").to(54, [100, 100], "io").hold(118).to(138, [90, 90], "io")
    vis = c.layer("visor", [geo.shape(v, nm="visor")], parent=face, p=vp.loop(150), a=(CX, 210), s=vs.loop(150))
    # before the visor lands: plain dot eyes under it (covered after 40)
    for i, x in enumerate((CX - 118, CX + 118)):
        part(c, f"eye{i}", geo.disc(x, 222, 40), face, (x, 222))
    ms = Track([100, 100], 0).hold(44).to(56, [112, 116], "back").hold(130).to(146, [100, 100], "io").loop(150)
    part(c, "mouth", K.m_smirk(CX + 10, 370, 180, 40), face, (CX - 80, 372), s=ms)
    M.glare_sweep(c, vis, CX, 210, 66, 36, travel=440, parent=face, w1=36, w2=16, gap=18,
                  sparks=[(418, 176, 40, 94, 26)])


@emoji("69-peek", "🫣", "подглядываю, стесняюсь, ой, не смотрю, палево", "peek, peeking, shy, lurking, oops",
       "|ω・) морда подглядывает из-за стены: высовывается, моргает люверсом, замечает тебя — прячется и снова медленно выглядывает",
       op=150, series="face")
def peek(c):
    wx = 212                                    # wall edge
    # face peeks from behind the wall (black over black hides it); ducks back = slides + shrinks behind
    fx = Track(292, 0).hold(12).to(36, 336, "o").hold(70).to(76, 342, "io").to(86, 118, "slam")
    fx.hold(104).to(140, 292, "o").loop(150)
    fs = Track([100, 100], 0).hold(76).to(86, [54, 54], "slam").hold(104).to(140, [100, 100], "o").loop(150)
    face = rig(c, p=Split(fx, CY), s=fs,
               r=Track(-8, 0).hold(12).to(36, 0, "o").hold(76).to(86, -14, "io").hold(104).to(140, -8, "o").loop(150))
    face.a = (292, CY)
    for i, x in enumerate((292 - 80, 292 + 80)):
        es = Track([100, 100], 0).hold(46 + i * 4).to(50 + i * 4, [106, 10], "i").to(56 + i * 4, [100, 100], "o")
        es.hold(66).to(70, [120, 120], "snap").to(76, [110, 110], "io").hold(104).to(114, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.eyelet(x, 212, 62, 0.42), face, (x, 212), s=es)
    part(c, "mouth", K.m_w(302, 336, 110, 36, 36), face, (302, 336))
    c.layer("wall", [geo.shape(geo.rrect(28, 24, wx, 488, 22), nm="wall")], p=(wx, 256), a=(wx, 256))
    # fingers gripping the edge, let go when it hides, grab again when it comes back
    for k in range(3):
        gy = 282 + k * 46
        gs = Track([100, 100], 0).hold(76 + k).to(84 + k, [0, 0], "i").hold(112 + k * 3).to(124 + k * 3, [112, 112], "snap").to(130 + k * 3, [100, 100], "io").loop(150)
        c.layer(f"finger{k}", [geo.shape(geo.rrect(wx - 30, gy - 19, wx + 40, gy + 19, 19), nm="f")], p=(wx - 20, gy), a=(wx - 20, gy), s=gs)


@emoji("70-party", "🥳", "праздник, ура, др, туса, вечеринка", "party, celebrate, birthday, yay, hooray",
       "колпак прыгает на голову, морда ^▽^ дует в дудку — дудка разворачивается, хлопок конфетти веером с дугами и вращением",
       op=150, series="face")
def party(c):
    y = Track(CY + 30, 0).hold(8).to(20, CY + 42, "io").to(30, CY + 22, "o").to(40, CY + 30, "io")
    y.hold(44).to(48, CY + 38, "slam").to(56, CY + 26, "o").to(64, CY + 30, "io").loop(150)
    face = rig(c, p=Split(CX, y))
    face.a = (CX, CY + 30)
    for i, x in enumerate((CX - 120, CX + 120)):
        es = Track([100, 100], 0).hold(44).to(50, [106, 64], "io").hold(92).to(100, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.caret(x, 262, 124), face, (x, 262), s=es)
    part(c, "mouth", K.m_tri(CX - 20, 380, 120, 84, 16), face, (CX - 20, 370))
    # party horn: blows out from the mouth corner (scaleX from the lips)
    horn = geo.poly([(CX + 20, 364), (CX + 128, 346), (CX + 176, 318), (CX + 176, 432), (CX + 128, 404), (CX + 20, 388)]).buffer(4)
    horn = horn.difference(geo.rect(CX + 70, 330, CX + 84, 420)).difference(geo.rect(CX + 112, 330, CX + 126, 420))
    hs = Track([0, 100], 0).hold(38).to(48, [112, 110], "snap").to(56, [94, 100], "io").to(64, [100, 100], "io").hold(100).to(114, [0, 100], "i").loop(150)
    part(c, "horn", horn, face, (CX + 20, 375), s=hs)
    # hat: tilted cone with a band cut + eyelet pompom
    hx, hy = CX - 96, 200
    hat = geo.poly([(hx - 70, hy), (hx + 70, hy), (hx + 6, hy - 128)]).buffer(10)
    hat = hat.difference(geo.rect(hx - 120, hy - 62, hx + 120, hy - 44))
    hat = geo.U(hat, geo.disc(hx + 6, hy - 136, 24)).difference(geo.disc(hx + 6, hy - 136, 9))
    hp = Track([hx, hy], 0).hold(10).to(16, [hx, hy + 8], "slam").to(22, [hx, hy - 14], "io").to(28, [hx, hy], "io")
    ho = Track([0, 0], 0).to(8, [100, 100], "ox").hold(130).to(146, [0, 0], "i").loop(150, "lin")
    hr = Track(-40, 0).to(16, -18, "slam").to(24, -24, "io").to(32, -20, "io").hold(46).to(52, -28, "snap").to(62, -16, "io").to(72, -20, "io")
    hr.hold(128).to(144, -40, "io")
    part(c, "hat", hat, face, (hx, hy), p=hp.loop(150), r=hr.loop(150), s=ho)
    # confetti fan out of the horn bell: bars, rings, sparks, dots; arcs + spin, 1.5f stagger
    kinds = [lambda x, y: geo.rrect(x - 20, y - 9, x + 20, y + 9, 5), lambda x, y: geo.ring(x, y, 17, 7),
             lambda x, y: geo.spark(x, y, 22, 0.3), lambda x, y: geo.disc(x, y, 14)]
    import random
    rnd = random.Random(7)
    x0, y0 = CX + 170, 360
    for k in range(12):
        x1 = rnd.uniform(250, 480)
        y1 = rnd.uniform(400, 470)
        apex = rnd.uniform(40, 200)
        M.particle(c, f"conf{k}", kinds[k % 4](x0, y0), 48 + k * 1.5, rnd.uniform(40, 56), (x0, y0), (x1, y1), apex=apex,
                   rot=(0, rnd.choice([-1, 1]) * rnd.uniform(200, 420)), anchor=(x0, y0), s_peak=100, pop=0.08, fade=0.25)


@emoji("71-devil", "😈", "хитрый, дьявол, злодей, задумал, хехе", "devil, evil, naughty, scheme, hehe",
       "из макушки прорастают рожки, глаза щурятся, ухмылка расползается до ушей, хвост-стрелка щёлкает кнутом, «хе-хе» трясёт плечами",
       op=150, series="face")
def devil(c):
    y = Track(CY + 16, 0).hold(60)
    for t in (60, 70, 80):
        y.to(t + 3, CY + 8, "snap").to(t + 10, CY + 16, "io")
    y.loop(150)
    face = rig(c, p=Split(CX, y))
    face.a = (CX, CY + 16)
    for i, (x, d) in enumerate(((CX - 112, 1), (CX + 112, -1))):
        # evil eye: slanted leaf (disc minus a tilted cut from above)
        e = geo.ellipse(x, 226, 70, 44).difference(geo.rot(geo.rect(x - 110, 140, x + 110, 214), d * 20, (x, 214)))
        es = Track([100, 100], 0).hold(30).to(42, [104, 70], "io").hold(120).to(134, [100, 100], "io").loop(150)
        part(c, f"eye{i}", e, face, (x, 226), s=es)
        # horn: tapered brush curving outward, grows from its base
        hb = (x - d * 6, 132)
        horn = geo.brush([hb, (x - d * 22, 84), (x - d * 58, 44)], 64, taper=(1.0, 0.12))
        hs = Track([100, 0], 0).hold(12 + i * 4).to(24 + i * 4, [100, 118], "snap").to(32 + i * 4, [100, 94], "io").to(40 + i * 4, [100, 100], "io")
        hs.hold(126).to(140, [100, 0], "i").loop(150)
        part(c, f"horn{i}", horn, face, hb, s=hs)
    # grin: wide smile whose scale spreads from the centre
    ms = Track([60, 70], 0).hold(30).to(44, [112, 112], "back").to(54, [100, 100], "io").hold(120).to(136, [60, 70], "io").loop(150)
    g = K.m_smile(CX, 350, 290, 64, 44)
    g = geo.U(g, geo.poly([(CX + 60, 382), (CX + 90, 378), (CX + 74, 418)]).buffer(6))   # a fang
    part(c, "mouth", g, face, (CX, 350), s=ms)
    # arrow tail: whips from the bottom right corner, cracks at 64
    tb = (452, 474)
    tail = geo.U(geo.brush([tb, (420, 444), (440, 396), (414, 356)], 30, taper=(1, 0.8)),
                 geo.poly([(414, 322), (388, 368), (440, 366)]).buffer(4))
    tr_ = Track(10, 0).hold(46).to(58, -26, "antic").to(64, 18, "slam").to(72, -8, "io").to(80, 4, "io").to(88, 0, "io")
    ts = Track([0, 0], 0).hold(40).to(50, [100, 100], "back").hold(126).to(140, [0, 0], "i").loop(150)
    c.layer("tail", [geo.shape(tail, nm="tail")], p=tb, a=tb, r=tr_.loop(150), s=ts)


@emoji("72-skull", "💀", "умер, я всё, смешно до смерти, череп, кринж", "dead, skull, im dead, lmao, cringe",
       "жирный череп клацает челюстью в ритм 120 BPM (три клака), на каждом ударе из углов челюсти летят искры, потом замирает и медленно наклоняется",
       op=150, series="face")
def skull(c):
    cx = CX
    s = Track([100, 100], 0)
    for t in (10, 24, 38):
        s.hold(t).to(t + 7, [97, 102], "decel").to(t + 14, [103, 96], "slam")
    s.to(62, [100, 100], "io").loop(150)
    rr = Track(0, 0).hold(70).to(96, -8, "io").hold(118).to(138, 0, "io").loop(150)
    face = rig(c, p=(cx, 300), s=s, r=rr)
    face.a = (cx, 300)
    cran = geo.U(geo.disc(cx, 200, 166, 24), geo.rrect(cx - 116, 220, cx + 116, 356, 40))
    cran = cran.difference(geo.ellipse(cx - 70, 222, 50, 58)).difference(geo.ellipse(cx + 70, 222, 50, 58))
    cran = cran.difference(geo.poly([(cx, 276), (cx - 24, 318), (cx + 24, 318)]).buffer(6))
    for k in range(3):
        tx = cx - 56 + k * 56
        cran = cran.difference(geo.rrect(tx - 8, 332, tx + 8, 356, 6))
    part(c, "cranium", cran, face, (cx, 300))
    jaw = geo.rrect(cx - 100, 368, cx + 100, 440, 30)
    for k in range(3):
        tx = cx - 50 + k * 50
        jaw = jaw.difference(geo.rrect(tx - 8, 368, tx + 8, 394, 6))
    jy = Track(368, 0)
    for t in (10, 24, 38):
        jy.hold(t).to(t + 7, 404, "decel").to(t + 14, 368, "slam")
    jy.loop(150)
    part(c, "jaw", jaw, face, (cx, 368), p=Split(cx, jy),
         r=Track(0, 0).hold(10).to(17, -4, "decel").to(24, 0, "slam").to(31, 4, "decel").to(38, 0, "slam").to(45, -3, "decel").to(52, 0, "slam").loop(150))
    # clack sparks: a pair per hit, 13f life (M11)
    for k, t in enumerate((24, 38, 52)):
        for side, d in enumerate((-1, 1)):
            x0 = cx + d * 120
            M.particle(c, f"cl{k}{side}", geo.spark(x0, 380, 26, 0.3), t, 14, (x0, 380), (x0 + d * 50, 350), None,
                       rot=(0, d * 45), anchor=(x0, 380), pop=0.2, fade=0.4, fall="decel")


@emoji("73-melt", "🫠", "таю, плыву, всё, растекаюсь, неловко", "melting, melt, dying, awkward, ugh",
       "улыбка держится, но глифы тянутся вниз подтёками, капли срываются в растущую лужу — и всё отматывается назад",
       op=180, series="face")
def melt(c):
    face = rig(c)
    glyphs = [("eyeL", geo.disc(CX - 124, 190, 48), (CX - 124, 142)), ("eyeR", geo.disc(CX + 124, 190, 48), (CX + 124, 142)),
              ("mouth", K.m_smile(CX, 320, 280, 70, 48), (CX, 288))]
    for k, (nm, g, top) in enumerate(glyphs):
        lag = k * 6
        # melt: stretch down from the top anchor and sag; rewind (M21) back up
        sy = Track([100, 100], 0).hold(24 + lag).to(80 + lag, [90, 185], "is").hold(112).to(146, [100, 100], "o").to(154, [102, 97], "io").to(162, [100, 100], "io").loop(180)
        py = Track(top[1], 0).hold(24 + lag).to(80 + lag, top[1] + 60, "is").hold(112).to(146, top[1], "o").loop(180)
        part(c, nm, g, face, top, p=Split(top[0], py), s=sy)
    # drips detach from the glyph bottoms (stagger 2-4f, life 16-24f, M16) into the puddle
    import random
    rnd = random.Random(3)
    starts = [(CX - 112, 330), (CX + 112, 330), (CX - 80, 430), (CX, 440), (CX + 84, 430)]
    for k in range(9):
        x0, y0 = starts[k % 5]
        x0 += rnd.uniform(-10, 10)
        M.particle(c, f"drip{k}", K.tear(x0, y0, 20), 50 + k * 4, 20, (x0, y0), (x0, 456), None, parent=face,
                   anchor=(x0, y0), pop=0.3, fade=0.1, fall="i", s_end=80)
    pud = geo.ellipse(CX, 462, 226, 28)
    ps = Track([0, 0], 0).hold(50).to(90, [100, 100], "o").hold(112).to(140, [0, 0], "i").loop(180, "lin")
    part(c, "puddle", pud, face, (CX, 462), s=ps)


@emoji("74-dizzy", "😵‍💫", "голова кругом, плыву, штормит, уф, кружится", "dizzy, woozy, spinning, confused, dazed",
       "@_@ спирали крутятся в разные стороны, голова ходит восьмёркой, вокруг орбитой летают три ✦ (ближние крупнее)",
       op=120, series="face")
def dizzy(c):
    import math as m
    fx = M.wave(CX, 22, 120, 120)
    fy = M.wave(CY, 14, 60, 120)
    fr = M.wave(0, 6, 120, 120, 1.2)
    face = rig(c, p=Split(fx, fy), r=fr)
    for i, (x, d) in enumerate(((CX - 116, 1), (CX + 116, -1))):
        rot = Track(0, 0).to(120, d * 720, "lin")
        part(c, f"eye{i}", K.spiral(x, 216, 76, 34, 1.9), face, (x, 216), r=rot)
    mr = M.wave(0, 8, 60, 120)
    part(c, "mouth", K.m_wave(CX, 356, 170, 18, 38, 1.5), face, (CX, 356), r=mr)
    # orbiting sparks on an ellipse above the head; nearer (lower) half = bigger
    ocx, ocy, rx, ry = CX, 92, 190, 44
    for k in range(3):
        ph = 2 * m.pi * k / 3
        x = M.wave(ocx, rx, 120, 120, ph + m.pi / 2)
        y = M.wave(ocy, ry, 120, 120, ph)
        sc = M.wave(80, 30, 120, 120, ph)
        s2 = M.Track([sc.k[0][1]] * 2, 0)
        for j in range(1, len(sc.k)):
            s2.to(sc.k[j][0], [sc.k[j][1]] * 2, sc.k[j - 1][2])
        c.layer(f"star{k}", [geo.shape(geo.spark(ocx, ocy, 44, 0.36), nm="star")], p=Split(x, y), a=(ocx, ocy), s=s2,
                r=Track(0, 0).to(120, 180, "lin"))


@emoji("75-mind-blown", "🤯", "мозг взорван, офигеть, шок, вау, не может быть", "mind blown, shocked, wow, no way, boom",
       "O_O: череп-дуга над глазами трескается и разлетается осколками с ударным кольцом, облако — и всё отматывается назад",
       op=150, series="face")
def mind_blown(c):
    s = Track([100, 100], 0).hold(20).to(34, [106, 92], "io").to(40, [96, 105], "snap").to(52, [100, 100], "io").hold(118).to(126, [103, 97], "slam").to(136, [100, 100], "io").loop(150)
    face = rig(c, p=(CX, 420), s=s)
    face.a = (CX, 420)
    for i, x in enumerate((CX - 108, CX + 108)):
        es = Track([100, 100], 0).hold(26).to(40, [124, 124], "snap").to(50, [112, 112], "io").hold(118).to(132, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.eyelet(x, 272, 66, 0.44), face, (x, 272), s=es)
    ms = Track([60, 60], 0).hold(26).to(40, [120, 120], "snap").hold(118).to(132, [60, 60], "io").loop(150)
    part(c, "mouth", K.m_o(CX, 404, 44, 0.4), face, (CX, 404), s=ms)
    # skull arc: 5 segments; they blow off radially spinning at 40, rewind back at 104-126 (M21)
    ox, oy, R = CX, 262, 186
    angs = [(-172, -140), (-136, -104), (-100, -80), (-76, -44), (-40, -8)]
    for k, (a0, a1) in enumerate(angs):
        g = geo.brush(geo.arc(ox, oy, R, a0, a1, 10), 44, taper=(0.8, 0.8), smooth=False)
        am = math.radians((a0 + a1) / 2)
        cxk, cyk = ox + R * math.cos(am), oy + R * math.sin(am)
        dist = 120 + 30 * (k % 2)
        tx, ty = cxk + dist * math.cos(am), cyk + dist * math.sin(am) * 0.55
        tx = min(max(tx, 112), 400)
        ty = max(ty, 96)
        p = Track([cxk, cyk], 0).hold(40).to(58, [tx, ty], "ox").to(96, [tx + (tx - cxk) * 0.1, ty + 14], "io").to(122, [cxk, cyk], "i5")
        p.to(126, [cxk, cyk + 4], "io").to(130, [cxk, cyk], "io").loop(150)
        rr = Track(0, 0).hold(40).to(58, (-1) ** k * 200, "ox").to(96, (-1) ** k * 230, "io").to(122, 0, "i5").loop(150)
        part(c, f"shard{k}", g, face, (cxk, cyk), p=p, r=rr)
    # shock ring (stroke width thins, M20) + puff cloud
    rs = Track([20, 20], 0).hold(40).to(56, [100, 100], "ring").hold(150)
    rw = Track(44, 0).hold(40).to(56, 10, "ring").to(62, 0, "i").hold(150)
    c.layer("ring", [lot_ring(ox, 176, 124, rw)], parent=face, p=(ox, 176), a=(ox, 176), s=rs, ip=40, op=63)
    for k, (dx, dy, r) in enumerate([(-60, 110, 50), (0, 90, 64), (60, 112, 48), (-24, 60, 40), (34, 64, 42)]):
        g = geo.disc(CX + dx, dy, r)
        sc = Track([0, 0], 0).hold(42 + k).to(56 + k, [110, 110], "ox").to(70 + k, [100, 100], "io").hold(92).to(110, [0, 0], "i").loop(150, "lin")
        part(c, f"puff{k}", g, face, (CX + dx, dy + r), s=sc)


def lot_ring(x, y, r, w):
    from xtc import lot
    import math as m
    n = 4
    k = 0.5523 * r
    pts = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
    ins = [(-k, 0), (0, -k), (k, 0), (0, k)]
    outs = [(k, 0), (0, k), (-k, 0), (0, -k)]
    return lot.group([lot.sh(lot.pathdata(pts, True, ins, outs)), lot.stroke(w)], nm="ring")


@emoji("76-sleep", "😴", "сплю, спать, устал, zzz, скучно", "sleep, sleepy, tired, zzz, bored",
       "-_- клюёт носом: медленно оседает и дёргается вверх, zZz поднимаются по волне и растворяются, из носа надувается пузырь и лопается",
       op=180, series="face")
def sleep(c):
    # nod: slow sink (60f) then a jerk up (SNAP), twice per loop
    y = Track(CY, 0)
    r = Track(0, 0)
    for t in (0, 90):
        y.to(t + 70, CY + 26, "is").to(t + 76, CY - 12, "snap").to(t + 90, CY, "io")
        r.to(t + 70, -7, "is").to(t + 76, 2, "snap").to(t + 90, 0, "io")
    face = rig(c, p=Split(CX, y), r=r)
    for i, x in enumerate((CX - 118, CX + 118)):
        es = Track([100, 100], 0)
        for t in (0, 90):
            es.to(t + 70, [100, 100], "lin").to(t + 74, [100, 150], "snap").to(t + 84, [100, 100], "io")
        part(c, f"eye{i}", K.dash(x, 238, 150, 46, tilt=-6 if i == 0 else 6), face, (x, 238), s=es)
    part(c, "mouth", K.m_o(CX - 10, 372, 42, 0.36), face, (CX - 10, 372))
    # snot bubble from the right: inflates while sinking, pops on the jerk
    bs = Track([0, 0], 0)
    for t in (0, 90):
        bs.hold(t + 20).to(t + 70, [100, 100], "is").to(t + 74, [140, 140], "snap").to(t + 76, [0, 0], "lin")
    part(c, "bubble", geo.ring(CX + 74, 380, 52, 36), face, (CX + 30, 380), s=bs)
    # zZz: brand Z glyphs rising on a wave, growing, fading (stagger 30f, life 70f)
    from specs.drop import brand_font
    for k in range(6):
        t0 = k * 30
        z = geo.text("Z", brand_font(), 330, 150, 60 + (k % 2) * 10, bold=7, width=76 + (k % 2) * 12)
        M.particle(c, f"z{k}", z, t0, 70, (340, 170), (420, 72), None, s_peak=100, rot=(-10, 14),
                   anchor=(330, 150), pop=0.2, fade=0.35, fall="decel", xease=(0.4, 0.0, 0.2, 1.0))


@emoji("77-grimace", "😬", "неловко, упс, кринж, ой-ой, зубы", "grimace, awkward, yikes, cringe, eek",
       "оскал-решётка: морда отшатывается назад и сжимается, зубы стучат дрожью по 2 кадра, по виску катится капля",
       op=120, series="face")
def grimace(c):
    s = Track([100, 100], 0).hold(14).to(24, [92, 90], "snap").to(30, [95, 93], "io").hold(92).to(104, [100, 100], "io").loop(120)
    y = Track(CY, 0).hold(14).to(24, CY - 16, "snap").to(30, CY - 10, "io").hold(92).to(104, CY, "io").loop(120)
    face = rig(c, p=Split(CX, y), s=s)
    for i, (x, d) in enumerate(((CX - 120, -1), (CX + 120, 1))):
        es = Track([100, 100], 0).hold(16).to(24, [116, 116], "snap").to(32, [106, 106], "io").hold(92).to(104, [100, 100], "io").loop(120)
        part(c, f"eye{i}", geo.disc(x, 214, 42), face, (x, 214), s=es)
        bp = Track([x, 128], 0).hold(14).to(24, [x, 110], "snap").hold(92).to(104, [x, 128], "io").loop(120)
        part(c, f"brow{i}", K.brow(x - d * 8, 128, 130, ang=d * 16, w=38), face, (x, 128), p=bp)
    mx = Track(CX, 0).hold(26)
    jitter(mx, 26, 92, CX, 4, 2)
    mx.loop(120)
    ms = Track([100, 100], 0).hold(14).to(24, [110, 92], "snap").hold(92).to(104, [100, 100], "io").loop(120)
    part(c, "mouth", K.m_grit(CX, 360, 380, 136, 30, 5), face, (CX, 360), p=Split(mx, 360), s=ms)
    M.particle(c, "sweat", K.tear(CX + 200, 110, 24), 36, 50, (CX + 200, 110), (CX + 214, 230), None, parent=face,
               anchor=(CX + 200, 110), pop=0.15, fade=0.2, fall="io", s_end=40)


@emoji("78-clown", "🤡", "клоун, цирк, кринж, пранк, шут", "clown, circus, joke, prank, cringe",
       "нос-шар надувается, «хонк» — нос сплющивается и отпружинивает, кудри по бокам подпрыгивают с запаздыванием",
       op=120, series="face")
def clown(c):
    face = rig(c)
    for i, (x, d) in enumerate(((CX - 112, -1), (CX + 112, 1))):
        es = Track([100, 100], 0).hold(44).to(50, [118, 118], "snap").to(60, [100, 100], "io").loop(120)
        part(c, f"eye{i}", K.eyelet(x, 196, 62, 0.44), face, (x, 196), s=es)
        # curly hair: two fat curls per side, bounce with follow-through
        for k in range(2):
            hx, hy = CX + d * (172 + k * 12), 96 + k * 80
            hs = Track([100, 100], 0).hold(46 + k * 4).to(52 + k * 4, [118, 86], "snap").to(60 + k * 4, [92, 108], "io").to(70 + k * 4, [100, 100], "io").loop(120)
            part(c, f"hair{i}{k}", geo.disc(hx, hy, 44), face, (hx, hy), s=hs)
    part(c, "mouth", K.m_smile(CX, 392, 260, 64, 46), face, (CX, 392),
         s=Track([100, 100], 0).hold(44).to(52, [110, 120], "snap").to(64, [100, 100], "io").loop(120))
    # nose: inflates over 30f, honk squash (contact held 1f), springs back
    ns = Track([100, 100], 0).hold(10).to(42, [124, 124], "is").to(46, [142, 74], "slam").to(47, [142, 74], "lin")
    ns.to(54, [88, 116], "snap").to(62, [106, 95], "io").to(70, [98, 102], "io").to(78, [100, 100], "io").loop(120)
    part(c, "nose", geo.disc(CX, 292, 56), face, (CX, 292), s=ns)


@emoji("79-moai", "🗿", "моаи, ну да, бро, серьёзно, каменное лицо", "moai, stone face, bruh, deadpan, sure",
       "каменная морда стоит, бровь-глазница медленно ползёт вверх — и резкий «бум»-зум",
       op=150, series="face")
def moai(c):
    s = Track([100, 100], 0).hold(92).to(94, [110, 110], "snap").to(100, [107, 107], "io").hold(130).to(146, [100, 100], "io").loop(150)
    face = rig(c, p=(CX, 300), s=s)
    face.a = (CX, 300)
    head = geo.U(geo.rrect(142, 40, 370, 470, 40), geo.rect(120, 150, 392, 200))
    head = head.difference(geo.rect(190, 214, 238, 238)).difference(geo.rect(274, 214, 322, 238))   # eye slits
    head = head.difference(geo.poly([(248, 214), (264, 214), (286, 340), (226, 340)]).buffer(-1).difference(
        geo.poly([(252, 218), (260, 218), (272, 324), (240, 324)])))                              # nose outline
    head = head.difference(geo.rect(206, 372, 306, 386))                                          # lips
    head = head.difference(geo.rect(150, 440, 362, 452))
    lay = part(c, "head", head, face, (CX, 300))
    # right brow: a hole bar over the eye rises (brow ridge lifts)
    by = Track([0, 0], 0).hold(30).to(88, [0, -34], "is").hold(130).to(146, [0, 0], "io").loop(150)
    geo.hole(lay, geo.rect(272, 176, 330, 190), nm="brow", p=by)
    geo.hole(lay, geo.rect(182, 176, 240, 190), nm="browL")


@emoji("80-salute", "🫡", "есть, так точно, уважение, принял, служу", "salute, yes sir, respect, roger, o7",
       "ладонь взлетает к брови и щёлкает, рука дрожит от напряжения, взгляд твёрдый, кивок",
       op=120, series="face")
def salute(c):
    y = Track(CY, 0).hold(26).to(30, CY + 8, "slam").to(38, CY, "io").loop(120)
    face = rig(c, p=Split(CX, y))
    for i, x in enumerate((CX - 124, CX + 124)):
        part(c, f"eye{i}", K.dash(x, 228, 130, 46, tilt=-8 if i == 0 else 8), face, (x, 228))
    part(c, "mouth", K.m_line(CX, 360, 130), face, (CX, 360))
    # hand: mitten palm (fingers together) at the right brow, forearm diagonal to the elbow (pivot)
    pv = (424, 462)
    palm = geo.U(geo.rrect(286, 96, 452, 174, 38), geo.rrect(404, 150, 452, 214, 22))
    palm = geo.rot(palm, -18, (370, 134))
    palm = palm.difference(geo.rot(geo.rect(296, 132, 364, 142), -18, (370, 134)))
    arm = geo.brush([pv, (424, 320), (420, 200)], 64, taper=(1, 1), smooth=False)
    hr = Track(-30, 0).hold(10).to(24, 4, "slam").to(30, -2, "io").to(36, 0, "io")
    jitter(hr, 40, 94, 0, 1.0, 2)
    hr.to(110, -30, "io").loop(120)
    hs = Track([0, 0], 0).hold(8).to(20, [104, 104], "snap").to(28, [100, 100], "io").hold(100).to(112, [0, 0], "i").loop(120)
    c.layer("arm", [geo.shape(geo.U(palm, arm), nm="arm")], parent=face, p=pv, a=pv, r=hr, s=hs)


@emoji("81-angel", "😇", "ангел, невинный, я не я, святой, мило", "angel, innocent, halo, saint, not me",
       "^‿^ над головой опускается нимб-люверс, качается в 3D (наклоняется эллипсом), вокруг ✦ по очереди",
       op=150, series="face")
def angel(c):
    face = rig(c, p=(CX, CY + 30))
    face.a = (CX, CY + 30)
    for i, x in enumerate((CX - 116, CX + 116)):
        part(c, f"eye{i}", K.cup(x, 272, 136, 44, 0.42), face, (x, 272))
    part(c, "mouth", K.m_smile(CX, 392, 150, 40, 42), face, (CX, 392))
    # halo: flat fat ellipse ring; descends, then wobbles like a spun coin (scaleY breathing + tilt)
    halo = geo.ellipse(CX, 96, 170, 52).difference(geo.ellipse(CX, 96, 124, 22))
    hy = Track(-60, 0).to(20, 12, "o").to(28, -4, "io").to(36, 0, "io").hold(130).to(150, -60, "i")
    hs = Track([100, 100], 0).hold(36)
    for t, v in ((50, [96, 76]), (64, [100, 108]), (78, [98, 84]), (92, [100, 104]), (106, [100, 94]), (120, [100, 100])):
        hs.to(t, v, "io")
    hs.loop(150)
    hr = Track(0, 0).hold(36).to(50, 8, "io").to(64, -6, "io").to(78, 4, "io").to(92, -2, "io").to(106, 0, "io").loop(150)
    ho = Track(0, 0).to(8, 100, "lin").hold(138).to(150, 0, "lin")
    c.layer("halo", [geo.shape(halo, nm="halo")], parent=face, p=Split(CX, Track(96, 0).to(20, 96, "lin")), a=(CX, 96),
            s=hs, r=hr)
    c.layers[-1].p = Split(CX, Track(46, 0).to(20, 96, "o").to(28, 88, "io").to(36, 96, "io").hold(132).to(150, 46, "i"))
    c.layers[-1].s = Track([60, 60], 0).to(20, [100, 100], "o").hold(36)
    s2 = c.layers[-1].s
    for t, v in ((50, [96, 76]), (64, [100, 108]), (78, [98, 84]), (92, [100, 104]), (106, [100, 94]), (120, [100, 100])):
        s2.to(t, v, "io")
    s2.hold(132).to(150, [60, 60], "i")
    for k, (x, y, t0) in enumerate(((CX - 190, 120, 44), (CX + 188, 160, 70), (CX - 176, 196, 96))):
        M.twinkle(c, f"tw{k}", x, y, 40, t0, 22, parent=face)


@emoji("82-nausea", "🤢", "тошнит, фу, мерзко, укачало, бе", "nauseated, sick, gross, ew, queasy",
       "щёки раздуваются шарами, лицо позеленело — зажмуривается, глотает (всё сжимается вниз) и снова пухнет",
       op=150, series="face")
def nausea(c):
    s = Track([100, 100], 0).hold(20).to(50, [104, 98], "is").to(58, [96, 108], "snap").to(66, [102, 96], "io").to(76, [100, 100], "io")
    s.hold(90).to(110, [104, 98], "is").to(116, [96, 108], "snap").to(126, [100, 100], "io").loop(150)
    face = rig(c, p=(CX, 440), s=s)
    face.a = (CX, 440)
    for i, (x, d) in enumerate(((CX - 116, 1), (CX + 116, -1))):
        es = Track([100, 100], 0).hold(40).to(52, [104, 70], "io").hold(70).to(80, [100, 100], "io").loop(150)
        part(c, f"eye{i}", K.chevron(x, 196, 118, d=d, open_=0.55), face, (x + d * 24, 196), s=es)
        # cheeks puff
        cs = Track([30, 30], 0).hold(10).to(48, [104, 104], "is").to(56, [30, 30], "slam").hold(86).to(108, [96, 96], "is").to(116, [30, 30], "slam").loop(150)
        cx = CX + (-1 if i == 0 else 1) * 110
        part(c, f"cheek{i}", geo.disc(cx, 356, 64), face, (cx, 356), s=cs)
    ms = Track([100, 100], 0).hold(10).to(48, [60, 180], "is").to(56, [100, 100], "slam").hold(86).to(108, [64, 170], "is").to(116, [100, 100], "slam").loop(150)
    part(c, "mouth", K.m_wave(CX, 356, 120, 12, 40, 1), face, (CX, 356), s=ms)
    # queasy wavy lines rising above the head (stagger)
    for k in range(3):
        x = CX - 90 + k * 90
        pts = [(x + 14 * math.sin(i / 3), 150 - i * 7) for i in range(12)]
        M.particle(c, f"wave{k}", geo.brush(pts, 26, (0.8, 0.8), False), 20 + k * 10, 50, (x, 150), (x, 116), None,
                   anchor=(x, 150), pop=0.3, fade=0.4, fall="decel")
