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
