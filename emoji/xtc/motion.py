"""XTC MOTION: 120 BPM (beat = 30 frames @60fps). Helpers append pose keys to Tracks;
lot.Track writes them in the rlottie-safe key format."""
import math

from . import geo, lot
from .lot import Split, Track, bez_y, ease_of, fit

BEAT = 30


def vadd(a, b):
    if isinstance(a, (list, tuple)):
        return [x + y for x, y in zip(a, b)]
    return a + b


def vmul(a, k):
    if isinstance(a, (list, tuple)):
        return [x * k for x in a]
    return a * k


def sq(k, base=100):
    """squash/stretch scale that keeps area: k>1 wide+short, k<1 narrow+tall."""
    return [base * k, base / k]


def T(v, t=0):
    return Track(v, t)


# ---------------------------------------------------------------- pose helpers


def settle(tr, t_hit, target, over, n=2, per=10, decay=0.42, hit="o"):
    """Arrive at t_hit on target+over (overshoot), then damped oscillation (n swings) into target.
    `over` is the first overshoot offset (scalar or vector)."""
    tr.to(t_hit, vadd(target, over), hit)
    sign = -1
    amp = over
    for i in range(n):
        amp = vmul(amp, decay)
        tr.by(per / 2, vadd(target, vmul(amp, sign)), "io")
        sign = -sign
    tr.by(per / 2, target, "io")
    return tr


def blink(tr, t, dur=7, closed=8, base=(100, 100)):
    """eye scaleY 100 -> closed -> 100; anchor must be the eye centre."""
    tr.hold(t)
    tr.to(t + dur * 0.4, [base[0] * 1.06, closed], "i")
    tr.to(t + dur, list(base), "o")
    return tr


def shake(tr, t0, t1, amp, base, step=2, decay=1.0):
    """bass shake: alternate +amp/-amp every `step` frames, optional decay; ends on base."""
    tr.hold(t0)
    t = t0
    sign = 1
    a = amp
    while t + step < t1:
        t += step
        tr.to(t, vadd(base, vmul(a, sign)), "io")
        sign = -sign
        a = vmul(a, decay)
    tr.to(t1, base, "io")
    return tr


def breathe(tr, t0, t1, base, amp=1.2, per=60):
    """micro-life during holds: 99-101% scale (amp in %)."""
    tr.hold(t0)
    t = t0
    sign = 1
    while t + per / 2 <= t1 + 1e-6:
        t += per / 2
        tr.to(t, [b * (1 + sign * amp / 100) for b in base] if isinstance(base, (list, tuple)) else base * (1 + sign * amp / 100), "io")
        sign = -sign
    tr.to(max(t1, tr.t + 1), base, "io") if tr.t < t1 else None
    return tr


# ---------------------------------------------------------------- particles


def particle(comp, nm, g, t0, life, p0, p1, apex=None, parent=None, s_peak=100, rot=(0, 0),
             pop=0.18, fade=0.3, anchor=None, fall="i", s_end=0, xease=None):
    """One particle living [t0, t0+life): pops in, travels p0 -> p1 along a parabola (apex = y of the
    top of the arc, or None for a straight eased fall), shrinks out. g = shapely geometry drawn around
    `anchor` (defaults to its centroid). A particle crossing the loop point is split in two layers
    (the tail replays at the start with negative key times) so the loop stays seamless."""
    if anchor is None:
        c = g.centroid
        anchor = (c.x, c.y)
    shapes = [geo.shape(g, nm=nm)]

    def tracks(t0):
        t1 = t0 + life
        if apex is None:
            x = Track(p0[0], t0).to(t1, p1[0], xease or "os")
            y = Track(p0[1], t0).to(t1, p1[1], fall)
        else:
            up = abs(p0[1] - apex)
            down = abs(p1[1] - apex)
            ta = t0 + life * (math.sqrt(up) / (math.sqrt(up) + math.sqrt(down) + 1e-9))
            y = Track(p0[1], t0).to(ta, apex, "os").to(t1, p1[1], "is")
            x = Track(p0[0], t0).to(t1, p1[0], xease or "lin")
        tp = t0 + max(2, life * pop)
        tf = t1 - max(3, life * fade)
        s = Track([0, 0], t0).to(tp, [s_peak * 1.15] * 2, "ox")
        mid = tp + 4 if tp + 4 < tf else (tp + tf) / 2
        if mid < t1 - 0.5:
            s.to(mid, [s_peak] * 2, "io")
        if tf > s.t + 0.5:
            s.to(tf, [s_peak] * 2, "lin")
        s.to(t1, [s_end] * 2, "i")
        r = Track(rot[0], t0).to(t1, rot[1], "os") if rot[0] != rot[1] else rot[0]
        return Split(x, y), s, r

    t1 = t0 + life
    p, s, r = tracks(t0)
    lay = comp.layer(nm, shapes, parent=parent, p=p, a=anchor, s=s, r=r,
                     ip=int(math.floor(t0)), op=min(comp.op, int(math.ceil(t1))))
    if t1 > comp.op:
        p, s, r = tracks(t0 - comp.op)
        comp.layer(nm + "w", shapes, parent=parent, p=p, a=anchor, s=s, r=r, ip=0,
                   op=int(math.ceil(t1 - comp.op)))
    return lay


SPARKS = False   # client (v3.4): «меньше звёздочек» — ✦ glints are off pack-wide; glare sweeps stay


def twinkle(comp, nm, x, y, r, t0, dur=16, parent=None, spin=45, pinch=0.36):
    """✦ latex glint: pops to 120%, settles, spins a bit, pinches out. No-op while SPARKS is off."""
    if not SPARKS:
        return None
    g = geo.spark(x, y, r, pinch)
    s = Track([0, 0], t0).to(t0 + dur * 0.3, [118, 118], "ox").to(t0 + dur * 0.55, [100, 100], "io").to(t0 + dur, [0, 0], "i")
    rr = Track(-spin / 2, t0).to(t0 + dur, spin / 2, "os")
    return comp.layer(nm, [geo.shape(g, nm=nm)], parent=parent, p=(x, y), a=(x, y), s=s, r=rr,
                      ip=int(t0), op=int(math.ceil(t0 + dur)))


# ---------------------------------------------------------------- 3D fakes


def spin_angle(segs):
    """piecewise angle: segs = [(t0, t1, deg0, deg1, ease), ...] in time order; holds between."""
    segs = [(a, b, c, d, ease_of(e)) for a, b, c, d, e in segs]

    def th(t):
        prev = segs[0][2]
        for t0, t1, d0, d1, e in segs:
            if t < t0:
                return prev
            if t <= t1:
                return d0 + (d1 - d0) * bez_y(e, (t - t0) / (t1 - t0))
            prev = d1
        return prev
    return th


def crossings(th, segs, step=90, offset=0):
    """times where the piecewise angle passes offset + k*step."""
    out = []
    for t0, t1, deg0, deg1, _ in segs:
        lo, hi = min(deg0, deg1), max(deg0, deg1)
        inc = deg1 > deg0
        for k in range(math.ceil((lo - offset) / step), math.floor((hi - offset) / step) + 1):
            target = offset + k * step
            a, b = t0, t1
            for _ in range(60):
                m = (a + b) / 2
                if (th(m) < target) == inc:
                    a = m
                else:
                    b = m
            out.append(round((a + b) / 2, 2))
    return sorted(set(out))


def windows(th, segs, visible):
    """opacity track (hold keys) that is 100 while visible(angle) holds."""
    ts = crossings(th, segs, 180, 90)
    state = visible(th(0))
    tr = Track(100 if state else 0, 0)
    for t in ts:
        new = visible(th(t + 0.05))
        if new != state and t > tr.t + 0.01:
            tr.k[-1][2] = "hold"
            tr.k.append([t, 100 if new else 0, None])
            state = new
    return tr


def spin3d(comp, nm, front, back, cx, cy, segs, thick=40, lip=30, parent=None, band_h=None, face_parent=None):
    """Flat object turning around the vertical axis through (cx, cy).
    front/back: shapely designs (holes allowed) drawn around (cx, cy); back is shown un-mirrored.
    segs: [(t0, t1, deg0, deg1, ease)] piecewise angle (end on a multiple of 360 to rest face-on).
    Layers: hidden-side rim (gives the edge thickness), edge band near edge-on, both faces.
    Returns (root null, angle fn)."""
    th = spin_angle(segs)
    ks = [0, comp.op]
    for t0, t1, *_ in segs:
        ks += [t0, t1]
    ks += crossings(th, segs, 90, 0) + crossings(th, segs, 180, 66.4) + crossings(th, segs, 180, 113.6)
    ks = sorted(set(round(t, 2) for t in ks))
    ks = [t for i, t in enumerate(ks) if i == 0 or t - ks[i - 1] > 0.2]
    c = lambda t: math.cos(math.radians(th(t)))
    sn = lambda t: math.sin(math.radians(th(t)))
    root = comp.null(nm, parent=parent, p=(cx, cy))

    def trk(fn):
        return fit(fn, ks)

    sil = geo.U(*[geo.Polygon(p.exterior) for p in geo._polys(geo.U(front, back))])
    rim = sil.difference(sil.buffer(-lip))
    x0, y0, x1, y1 = sil.bounds
    bh = band_h or (y1 - y0)
    band = geo.rect(cx - thick / 2, cy - bh / 2 + lip * 0.4, cx + thick / 2, cy + bh / 2 - lip * 0.4)
    sx = lambda t: 100 * c(t)
    front_vis = lambda a: math.cos(math.radians(a)) >= 0
    back_vis = lambda a: math.cos(math.radians(a)) < 0
    for side, sgn, vis in (("rimB", -1, front_vis), ("rimF", 1, back_vis)):
        comp.layer(f"{nm}-{side}", [geo.shape(rim, nm=side)], parent=root,
                   p=Split(trk(lambda t, s=sgn: cx + s * thick / 2 * sn(t)), cy), a=(cx, cy),
                   s=_scale(trk(sx)), o=windows(th, segs, vis))
    band_fn = lambda t: 100 * max(0.0, 1 - abs(c(t)) / 0.4)
    comp.layer(f"{nm}-band", [geo.shape(band, nm="band")], parent=root, p=(cx, cy), a=(cx, cy),
               s=_scale(trk(band_fn)))
    f = comp.layer(f"{nm}-front", [geo.shape(front, nm="front")], parent=root,
                   p=Split(trk(lambda t: cx + thick / 2 * sn(t)), cy), a=(cx, cy), s=_scale(trk(sx)),
                   o=windows(th, segs, front_vis))
    b = comp.layer(f"{nm}-back", [geo.shape(geo.mirror(back, cx), nm="back")], parent=root,
                   p=Split(trk(lambda t: cx - thick / 2 * sn(t)), cy), a=(cx, cy), s=_scale(trk(sx)),
                   o=windows(th, segs, back_vis))
    return root, th, f, b


def _scale(tr):
    out = Track([tr.k[0][1], 100], tr.k[0][0])
    for i in range(1, len(tr.k)):
        out.to(tr.k[i][0], [tr.k[i][1], 100], tr.k[i - 1][2])
    return out


def _prepend(tr, t):
    if tr.k[0][0] <= t:
        return tr
    out = Track(tr.v0, t)
    out.to(tr.k[0][0], tr.v0, "lin")
    out.k[-1][2] = tr.k[0][2]
    out.k.extend([list(k) for k in tr.k[1:]])
    return out


def _append(tr, t):
    if tr.t >= t:
        return tr
    return tr.to(t, tr.v, "lin")


def glare_sweep(comp, target, cx, cy, t0, dur=24, travel=280, angle=-35, parent=None, sparks=(), **kw):
    """the brand's latex glare: a double streak sweeps across `target` through the pack's one matte
    (inverted: it cuts light through the black). Parked off-art outside [t0, t0+dur].
    sparks: [(x, y, r, t_pop, life)] ✦ glints cut through the same matte."""
    import math as _m
    a = _m.radians(angle + 90)
    dx, dy = _m.cos(a) * travel, _m.sin(a) * travel
    p = Track([-dx, -dy], 0).hold(t0).to(t0 + dur, [dx, dy], "io")
    p.k[-1][2] = "hold"          # jump back while parked off-art
    p.k.append([comp.op, [-dx, -dy], None])
    shapes = [geo.shape(geo.glare(cx, cy, angle=angle, **kw), nm="glare", p=p)]
    for i, (x, y, r, tp, life) in enumerate(sparks if SPARKS else ()):
        s = Track([0, 0], 0).hold(tp).to(tp + life * 0.3, [120, 120], "ox").to(tp + life * 0.55, [100, 100], "io")
        s.to(tp + life, [0, 0], "i").loop(comp.op, "lin")
        rr = Track(-25, 0).hold(tp).to(tp + life, 20, "os").loop(comp.op, "lin")
        shapes.append(geo.shape(geo.spark(x, y, r), nm=f"spark{i}", p=(x, y), a=(x, y), s=s, r=rr))
    return comp.matte(target, "glare", shapes, parent=parent, p=(0, 0), a=(0, 0))


def wave(base, amp, per, op, phase=0.0):
    """smooth periodic base + amp*sin(2pi t/per + phase) over [0, op] (op a multiple of per):
    keys at the extrema, Hermite-fitted curves."""
    ts = {0.0, float(op)}
    k = -2
    while True:
        t = ((math.pi / 2 + k * math.pi - phase) / (2 * math.pi)) * per
        if t > op:
            break
        if 0.3 < t < op - 0.3:
            ts.add(round(t, 3))
        k += 1
    fn = lambda t: base + amp * math.sin(2 * math.pi * t / per + phase)
    return fit(fn, sorted(ts))


def flip_tile(comp, nm, parent, x, y, w, h, glyphs, times, dur=12, gap=10, r=22, bounce=10):
    """Split-flap tile without overlapping layers (black-on-black would eat the glyph holes).
    glyphs: shapely glyph shapes (holes) centred on the tile, or None for blank; state k shows glyphs[k].
    times[k] = start of the flip from state k to state k+1 (len(times) == len(glyphs) - 1), or one
    more time to flip from the last state back to glyphs[0] (cyclic loop).
    Physics faked by scale: old top half falls to the hinge while the new top grows from the top edge
    (squashed, reads as foreshortening), then the flap's back (new bottom) drops from the hinge while
    the old bottom shrinks to the bottom edge; the flap bounces `bounce`% off the stop."""
    hh = h / 2 - gap / 2
    top = geo.rrect(x - w / 2, y - h / 2, x + w / 2, y - gap / 2, r)
    bot = geo.rrect(x - w / 2, y + gap / 2, x + w / 2, y + h / 2, r)
    n = len(glyphs)
    cyclic = len(times) == n
    half = dur / 2
    states = list(range(n)) + ([0] if cyclic else [])
    layers = []
    for k in range(n):
        g = glyphs[k]
        T_ = top if g is None else top.difference(g)
        B_ = bot if g is None else bot.difference(g)
        t_in = times[k - 1] if k > 0 else (times[-1] if cyclic else None)
        t_out = times[k] if k < len(times) else None
        visible0 = (k == 0)
        # --- top half: grows from the top edge on flip-in, falls to the hinge on flip-out
        ts = Track([100, 100 if visible0 else 0], 0)
        ty = Track(y, 0) if visible0 else Track(y - hh, 0)
        events = []
        if t_out is not None:
            events.append(("out", t_out))
        if t_in is not None and not (k == 0 and not cyclic):
            events.append(("in", t_in))
        for kind, t in sorted(events, key=lambda e: e[1]):
            if kind == "out":
                ts.hold(t).to(t + half, [100, 0], "i")
                ty.hold(t)
                if abs(ty.v - y) > 0.01:
                    ty.to(t + 0.01, y, "hold")
            else:
                ts.hold(t).to(t + half, [100, 100], "i")
                ty.hold(t)
                if abs(ty.v - (y - hh)) > 0.01:
                    ty.k[-1][2] = "hold"
                    ty.k.append([t + 0.01, y - hh, None])
                ty.to(t + half, y, "i")
        ts.hold(comp.op)
        ty.hold(comp.op)
        lt = comp.layer(f"{nm}-t{k}", [geo.shape(T_, nm="t")], parent=parent, p=Split(x, ty), a=(x, y), s=ts)
        # --- bottom half: drops from the hinge on flip-in (with bounce), shrinks to the bottom edge on flip-out
        bs = Track([100, 100 if visible0 else 0], 0)
        by = Track(y, 0)
        for kind, t in sorted(events, key=lambda e: e[1]):
            t2 = t + half
            if kind == "in":
                bs.hold(t2)
                by.hold(t2)
                if abs(by.v - y) > 0.01:
                    by.k[-1][2] = "hold"
                    by.k.append([t2 + 0.01, y, None])
                bs.to(t2 + half, [100, 100], "o").to(t2 + half + 3, [100, 100 - bounce], "io").to(t2 + half + 7, [100, 100], "io")
            else:
                bs.hold(t2).to(t2 + half, [100, 0], "o").to(t2 + half + 3, [100, bounce], "io").to(t2 + half + 7, [100, 0], "io")
                by.hold(t2).to(t2 + half, y + hh, "o").to(t2 + half + 3, y + hh * (1 - bounce / 100), "io").to(t2 + half + 7, y + hh, "io")
        bs.hold(comp.op)
        by.hold(comp.op)
        lb = comp.layer(f"{nm}-b{k}", [geo.shape(B_, nm="b")], parent=parent, p=Split(x, by), a=(x, y), s=bs)
        layers += [lt, lb]
    return layers
